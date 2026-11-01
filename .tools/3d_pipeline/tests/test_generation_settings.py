"""The generation model is a per-profile setting that is validated before any paid call."""

from __future__ import annotations

import copy
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import bootstrap_3d_workflow as bootstrap
import run_pilot
import verify_environment
from lib.generation import (
    GenerationError,
    generation_credits,
    generation_problems,
    operation_credits,
    validate_generation,
)
from meshy_client import MeshyClient, image_to_3d_arguments

LEGACY = {
    "ai_model": "meshy-7",
    "model_type": "standard",
    "target_polycount": 21000,
    "target_polycount_applies": False,
    "should_remesh": False,
    "texture_resolution": "2k",
    "enable_pbr": True,
}


def generation(**changes) -> dict:
    return {**LEGACY, **changes}


def profiles() -> dict:
    return json.loads((ROOT / "config/asset_profiles.json").read_text(encoding="utf-8"))["profiles"]


class ShippedProfileTests(unittest.TestCase):
    def test_every_profile_has_valid_generation_settings(self) -> None:
        for name, profile in profiles().items():
            with self.subTest(profile=name):
                self.assertEqual(generation_problems(profile["generation"]), [])

    def test_shipped_defaults_keep_todays_request_values(self) -> None:
        for name, profile in profiles().items():
            settings = profile["generation"]
            with self.subTest(profile=name):
                self.assertEqual(settings["ai_model"], "meshy-7")
                self.assertEqual(settings["model_type"], "standard")
                self.assertIs(settings["should_remesh"], False)
                self.assertIs(settings["enable_pbr"], True)
                self.assertEqual(settings["target_polycount"], profile["triangle_range"]["working_triangle_target"])


class ValidationTests(unittest.TestCase):
    def problems(self, **changes) -> str:
        return "; ".join(generation_problems(generation(**changes)))

    def test_retired_models_and_model_types_are_refused(self) -> None:
        for model in ("meshy-t1", "meshy-5", "meshy-4"):
            with self.subTest(model=model):
                self.assertIn("retired", self.problems(ai_model=model))
        self.assertIn("retired", self.problems(model_type="lowpoly"))

    def test_unknown_models_and_unpinned_aliases_are_refused(self) -> None:
        self.assertIn("not accepted by the locked", self.problems(ai_model="meshy-9"))
        self.assertIn("alias", self.problems(ai_model="latest"))
        self.assertIn("not accepted by the locked", self.problems(model_type="quad-remesh"))

    def test_accepted_models_pass(self) -> None:
        for model in ("meshy-7", "meshy-7.1", "meshy-6", "meshy-6-lite"):
            with self.subTest(model=model):
                self.assertEqual(generation_problems(generation(ai_model=model)), [])
        self.assertEqual(validate_generation(generation(ai_model=" Meshy-7 "))["ai_model"], "meshy-7")

    def test_smart_topology_face_caps(self) -> None:
        smart = {"model_type": "smart-topology", "should_remesh": False}
        self.assertEqual(generation_problems(generation(ai_model="meshy-t2", target_polycount=15000, **smart)), [])
        self.assertEqual(generation_problems(generation(ai_model="meshy-t2.5", target_polycount=30000, **smart)), [])
        self.assertIn("15000", self.problems(ai_model="meshy-t2", target_polycount=15001, **smart))
        self.assertIn("30000", self.problems(ai_model="meshy-t2.5", target_polycount=30001, **smart))
        self.assertIn("between 100", self.problems(ai_model="meshy-t2.5", target_polycount=99, **smart))
        self.assertIn("between 100", self.problems(ai_model="meshy-t2.5", target_polycount=None, **smart))

    def test_smart_topology_and_its_models_go_together(self) -> None:
        self.assertIn("requires exactly", self.problems(ai_model="meshy-7", model_type="smart-topology"))
        self.assertIn("requires exactly", self.problems(ai_model="meshy-t2.5", model_type="standard"))
        self.assertIn("ignored", self.problems(ai_model="meshy-t2.5", model_type="smart-topology", should_remesh=True))

    def test_a_standard_target_that_is_meant_to_apply_needs_should_remesh(self) -> None:
        self.assertIn("should_remesh", self.problems(target_polycount_applies=True, should_remesh=False))
        self.assertEqual(generation_problems(generation(target_polycount_applies=True, should_remesh=True)), [])
        self.assertIn("needs a target_polycount", self.problems(should_remesh=True, target_polycount=None))
        self.assertIn("between 100", self.problems(should_remesh=True, target_polycount=300001))

    def test_texture_resolution_must_be_priced(self) -> None:
        self.assertIn("does not offer 4k", self.problems(ai_model="meshy-6-lite", texture_resolution="4k"))
        self.assertIn("does not offer 1k", self.problems(texture_resolution="1k"))

    def test_missing_and_mistyped_settings_are_refused(self) -> None:
        incomplete = dict(LEGACY)
        del incomplete["should_remesh"]
        self.assertIn("missing", "; ".join(generation_problems(incomplete)))
        self.assertIn("true or false", self.problems(enable_pbr="yes"))
        self.assertIn("whole number", self.problems(target_polycount=True))
        self.assertEqual(generation_problems(None), ["the profile has no generation settings"])
        with self.assertRaises(GenerationError):
            validate_generation(generation(ai_model="meshy-t1"))


class PriceTableTests(unittest.TestCase):
    def test_prices_match_the_recorded_pricing_page(self) -> None:
        self.assertEqual(generation_credits("meshy-7", "2k"), 30)
        self.assertEqual(generation_credits("meshy-7.1", "8k"), 35)
        self.assertEqual(generation_credits("meshy-t2.5", "2k"), 15)
        self.assertEqual(generation_credits("meshy-6-lite", None), 5)
        self.assertEqual(operation_credits("remesh"), 5)
        self.assertEqual(operation_credits("rig"), 5)
        self.assertEqual(operation_credits("animation", actions=3), 9)
        self.assertEqual(operation_credits("text_to_motion", mode="prime"), 10)
        self.assertEqual(operation_credits("text_to_motion", mode="swift"), 3)

    def test_unknown_prices_fail_instead_of_guessing(self) -> None:
        with self.assertRaises(GenerationError):
            generation_credits("meshy-9")
        with self.assertRaises(GenerationError):
            operation_credits("teleport")

    def test_the_table_names_its_source_and_date(self) -> None:
        table = json.loads((ROOT / "config/meshy_pricing.json").read_text(encoding="utf-8"))
        self.assertEqual(table["source_url"], "https://docs.meshy.ai/en/api/pricing")
        self.assertEqual(table["retrieved"], "2026-10-31")


class RequestTests(unittest.TestCase):
    image = Path("job/refs/original/meshy_input.png")

    def test_shipped_settings_reproduce_the_previous_request(self) -> None:
        previous = {
            "file_path": str(self.image),
            "ai_model": "meshy-7",
            "model_type": "standard",
            "enable_pbr": True,
            "topology": "triangle",
            "target_polycount": 21000,
            "should_remesh": False,
            "should_texture": True,
            "image_enhancement": True,
            "target_formats": ["glb", "fbx"],
            "multi_view_thumbnails": False,
            "response_format": "json",
            "pose_mode": "a-pose",
        }
        built = image_to_3d_arguments(self.image, validate_generation(LEGACY), "a-pose")
        built.pop("texture_resolution")  # the one explicit value: it is Meshy's own 2k default
        self.assertEqual(built, previous)

    def test_each_setting_changes_the_request(self) -> None:
        base = image_to_3d_arguments(self.image, validate_generation(LEGACY), None)
        changed = {
            "ai_model": "meshy-7.1",
            "target_polycount": 12000,
            "should_remesh": True,
            "texture_resolution": "4k",
            "enable_pbr": False,
        }
        for key, value in changed.items():
            with self.subTest(key=key):
                built = image_to_3d_arguments(self.image, validate_generation(generation(**{key: value})), None)
                self.assertEqual(built[key], value)
                self.assertNotEqual(built, base)

    def test_smart_topology_request_leaves_out_what_meshy_rejects(self) -> None:
        settings = validate_generation(generation(ai_model="meshy-t2.5", model_type="smart-topology", target_polycount=21000))
        built = image_to_3d_arguments(self.image, settings, None)
        self.assertEqual((built["ai_model"], built["model_type"], built["target_polycount"]), ("meshy-t2.5", "smart-topology", 21000))
        self.assertNotIn("should_remesh", built)
        self.assertNotIn("image_enhancement", built)

    def test_lite_model_request_leaves_out_image_enhancement(self) -> None:
        built = image_to_3d_arguments(self.image, validate_generation(generation(ai_model="meshy-6-lite")), None)
        self.assertNotIn("image_enhancement", built)


class ClientRefusalTests(unittest.TestCase):
    def client(self, job_root: Path) -> MeshyClient:
        client = object.__new__(MeshyClient)
        client.job_root = job_root
        client.call = Mock(return_value={})
        return client

    def test_invalid_settings_never_reach_the_provider(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            job = Path(temporary).resolve()
            image = job / "refs" / "meshy_input.png"
            image.parent.mkdir(parents=True)
            image.write_bytes(b"png")
            client = self.client(job)
            for bad in (generation(ai_model="meshy-t1"), generation(ai_model="meshy-5"), generation(ai_model="meshy-9")):
                with self.subTest(model=bad["ai_model"]), self.assertRaises(GenerationError):
                    client.image_to_3d(image_path=image, generation=bad, pose_mode=None, estimate_credits=30)
            client.call.assert_not_called()
            client.image_to_3d(image_path=image, generation=LEGACY, pose_mode="a-pose", estimate_credits=30)
            client.call.assert_called_once()
            self.assertEqual(client.call.call_args.args[1]["ai_model"], "meshy-7")


def humanoid_spec(**changes) -> dict:
    spec = {
        "asset_id": "hoi4.model.job.test_unit",
        "asset_kind": "humanoid",
        "profile": "humanoid_unit",
        "credit_budget": 60,
        "target_polycount": 21000,
        "required_actions": [
            {"role": "idle", "provider_action_id": 0},
            {"role": "move", "provider_action_id": None, "task_type": "blender_authored_skeletal"},
            {"role": "attack", "provider_action_id": 4},
            {"role": "death", "provider_action_id": 8},
        ],
    }
    spec.update(changes)
    return spec


class RunnerSpecTests(unittest.TestCase):
    def test_the_job_may_restate_the_profile_model_but_never_change_it(self) -> None:
        run_pilot.prepare_spec(humanoid_spec(meshy_ai_model="meshy-7", resolved_meshy_ai_model="MESHY-7"))
        with self.assertRaisesRegex(RuntimeError, "never changes silently"):
            run_pilot.prepare_spec(humanoid_spec(meshy_ai_model="meshy-7.1"))
        with self.assertRaisesRegex(RuntimeError, "never changes silently"):
            run_pilot.prepare_spec(humanoid_spec(resolved_meshy_ai_model="latest"))

    def test_estimates_come_from_the_price_table_not_from_the_job(self) -> None:
        spec = run_pilot.prepare_spec(humanoid_spec(image_to_3d_estimate_credits=20, planned_total_credits=44))
        self.assertEqual(
            (
                spec["image_to_3d_estimate_credits"],
                spec["remesh_estimate_credits"],
                spec["rig_estimate_credits"],
                spec["animation_estimate_credits"],
            ),
            (30, 5, 5, 3),
        )
        self.assertEqual(spec["planned_total_credits"], 49)
        self.assertEqual(spec["pricing_source"]["retrieved"], "2026-10-31")
        self.assertEqual(spec["generation"]["ai_model"], "meshy-7")

    def test_planned_stages_follow_the_route(self) -> None:
        spec = run_pilot.prepare_spec(humanoid_spec(generation_stage="generation_2"))
        self.assertEqual(
            [item["stage"] for item in run_pilot.planned_stages(spec)],
            [
                "generation_2",
                "generation_2_rig_remesh",
                "generation_2_rig",
                "generation_2_animation_idle",
                "generation_2_animation_attack",
                "generation_2_animation_death",
            ],
        )
        local = run_pilot.prepare_spec(humanoid_spec(humanoid_rig_route="blender_failure_recovery_humanoid_v1"))
        self.assertEqual(local["planned_total_credits"], 30)
        creature = run_pilot.prepare_spec(humanoid_spec(asset_kind="creature", profile="nonhumanoid_creature"))
        self.assertEqual(creature["planned_total_credits"], 30)

    def test_a_profile_change_changes_the_plan(self) -> None:
        smart = dict(profiles()["humanoid_unit"])
        smart["generation"] = generation(ai_model="meshy-t2.5", model_type="smart-topology")
        with patch.object(run_pilot, "load_profile", return_value=smart):
            spec = run_pilot.prepare_spec(humanoid_spec())
        self.assertEqual(spec["generation"]["ai_model"], "meshy-t2.5")
        self.assertEqual(spec["image_to_3d_estimate_credits"], 15)
        self.assertEqual(spec["planned_total_credits"], 15 + 5 + 9)

    def test_retired_profile_model_stops_before_any_provider_call(self) -> None:
        broken = dict(profiles()["humanoid_unit"])
        broken["generation"] = generation(ai_model="meshy-t1", model_type="smart-topology")
        with patch.object(run_pilot, "load_profile", return_value=broken):
            with self.assertRaisesRegex(GenerationError, "retired"):
                run_pilot.prepare_spec(humanoid_spec())

    def test_paid_work_needs_a_credit_budget(self) -> None:
        for budget in (None, 0, -5, True, "60", 49.5):
            spec = humanoid_spec()
            spec["credit_budget"] = budget
            with self.subTest(budget=budget), self.assertRaisesRegex(RuntimeError, "no credit_budget.*49 credits"):
                run_pilot.prepare_spec(spec)

    def test_initialize_job_records_budget_and_settings_in_job_yaml(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            job = Path(temporary) / "job"
            job.mkdir()
            (job / "job.yaml").write_text("{}\n", encoding="utf-8")
            initialize = Mock(return_value={"status": "preflight"})
            with patch.dict(sys.modules, {"init_pilot_jobs": Mock(initialize_one=initialize)}), patch.object(
                run_pilot, "ensure_job_layout", return_value=job
            ), patch.object(run_pilot, "resolve_job_root", return_value=job):
                run_pilot.initialize_job(humanoid_spec())
            recorded = json.loads((job / "job.yaml").read_text(encoding="utf-8"))
        self.assertEqual(recorded["credit_budget"], 60)
        self.assertEqual(recorded["generation"]["ai_model"], "meshy-7")
        self.assertEqual(recorded["estimated_credits"], 49)
        self.assertEqual(initialize.call_args.args[0]["credit_budget"], 60)


class SetupAndVerificationTests(unittest.TestCase):
    def test_bootstrap_accepts_the_shipped_profiles(self) -> None:
        bootstrap.verify_generation_profiles(ROOT)

    def test_bootstrap_refuses_a_profile_with_a_retired_model(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            pipeline = Path(temporary)
            (pipeline / "lib").mkdir()
            shutil.copy2(ROOT / "lib" / "generation.py", pipeline / "lib" / "generation.py")
            shutil.copytree(ROOT / "config", pipeline / "config")
            path = pipeline / "config" / "asset_profiles.json"
            document = json.loads(path.read_text(encoding="utf-8"))
            document["profiles"]["humanoid_unit"]["generation"]["ai_model"] = "meshy-5"
            path.write_text(json.dumps(document), encoding="utf-8")
            with self.assertRaisesRegex(bootstrap.SetupError, "humanoid_unit.*retired"):
                bootstrap.verify_generation_profiles(pipeline)

    def test_verification_reports_a_contract_tool_the_lock_does_not_have(self) -> None:
        contract = json.loads((ROOT / "config/meshy_tool_contract.json").read_text(encoding="utf-8"))
        schema = json.loads((ROOT / "config/meshy_tool_schema.lock.json").read_text(encoding="utf-8"))
        document = {"profiles": profiles()}
        self.assertEqual(verify_environment.contract_findings(contract, schema, document), [])
        stale = copy.deepcopy(contract)
        stale["optional_capabilities"]["text_to_motion"]["tool_names"].append("meshy_get_motion_status")
        findings = verify_environment.contract_findings(stale, schema, document)
        self.assertTrue(any("meshy_get_motion_status" in finding for finding in findings))
        bad_profiles = copy.deepcopy(document)
        bad_profiles["profiles"]["building"]["generation"]["ai_model"] = "meshy-t1"
        self.assertTrue(any("profile building" in finding for finding in verify_environment.contract_findings(contract, schema, bad_profiles)))


if __name__ == "__main__":
    unittest.main()
