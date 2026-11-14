"""The Tripo route: the inbox naming rule, the intake's receipt and manifests, the provider switch."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))

import run_pilot  # noqa: E402
import tripo_intake  # noqa: E402
from lib import credits  # noqa: E402
from lib.tripo import animation_source_kind, inbox_file, provider_name, uses_tripo  # noqa: E402

ROLES = {"idle": "idle", "move": "walk", "attack": "chop", "defend": "hit_to_body_01", "retreat": "flee_01", "death": "fall"}


def tripo_spec(**extra) -> dict:
    spec = {
        "asset_id": "hoi4_3d_model_jobs.orc_test",
        "unit_type": "infantry_melee",
        "runtime_stem": "orc_test",
        "provider": "tripo",
        "tripo": {"roles": dict(ROLES), "weapon": {"part": "tripo_part_1", "bone": "RightHand", "source": "rigged"}},
    }
    spec.update(extra)
    return spec


def fake_prepare_output(out_dir: Path, command: list) -> subprocess.CompletedProcess:
    """What prepare_tripo_unit.py would leave behind, without Blender."""

    base = command[command.index("--base-name") + 1]
    pattern = command[command.index("--role-name") + 1]
    roles = command[command.index("--roles") + 1 : command.index("--roles") + 7]
    (out_dir / f"{base}.glb").write_bytes(b"base")
    (out_dir / f"{base}_textures").mkdir()
    clips = {}
    for item in roles:
        role, clip = item.split("=")
        name = pattern.format(role=role) + ".glb"
        (out_dir / name).write_bytes(b"role " + role.encode())
        clips[role] = {"clip": clip, "file": name, "animation_name": clip, "frames": 10, "joints": 22}
    report = {"tool": "prepare_tripo_unit", "blender": "5.2.2", "bones_before": 65, "bones_after": 22, "weapon": [], "clips": clips, "triangles": 100}
    return subprocess.CompletedProcess(command, 0, "Blender noise\n" + json.dumps(report, sort_keys=True) + "\n", "")


class InboxRule(unittest.TestCase):
    def test_a_file_is_found_by_asset_slug_and_kind(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            inbox = Path(name)
            (inbox / "orc_test__rigged.glb").write_bytes(b"x")
            (inbox / "orc_test__model.glb.txt").write_bytes(b"x")
            self.assertEqual(inbox_file(inbox, "orc_test", "rigged"), inbox / "orc_test__rigged.glb")
            self.assertIsNone(inbox_file(inbox, "orc_test", "model"))
            self.assertIsNone(inbox_file(inbox, "other", "rigged"))
            with self.assertRaises(ValueError):
                inbox_file(inbox, "orc_test", "baked")

    def test_a_unit_needs_rigged_and_a_twin_only_when_the_weapon_comes_from_it(self) -> None:
        spec = run_pilot.prepare_spec(tripo_spec())
        with tempfile.TemporaryDirectory() as name:
            inbox = Path(name)
            with self.assertRaisesRegex(FileNotFoundError, "orc_test__rigged.glb"):
                tripo_intake.intake_files(spec, "orc_test", inbox)
            (inbox / "orc_test__rigged.glb").write_bytes(b"x")
            self.assertEqual(list(tripo_intake.intake_files(spec, "orc_test", inbox)), ["rigged"])
            spec["tripo"]["weapon"]["source"] = "twin"
            with self.assertRaisesRegex(FileNotFoundError, "orc_test__segmented.glb"):
                tripo_intake.intake_files(spec, "orc_test", inbox)

    def test_the_prepare_command_names_every_role_and_the_weapon(self) -> None:
        spec = run_pilot.prepare_spec(tripo_spec())
        files = {"rigged": Path("r.glb")}
        command = tripo_intake.prepare_command(Path("blender.exe"), spec, files, Path("out"), Path("report.json"))
        self.assertIn("idle=idle", command)
        self.assertIn("defend=hit_to_body_01", command)
        self.assertEqual(command[command.index("--rigid-part") + 1], "tripo_part_1=RightHand")
        self.assertEqual(command[command.index("--role-name") + 1], "animation_{role}_provider")
        self.assertEqual(command[command.index("--python-exit-code") + 1], "1")
        self.assertNotIn("--trim", command)
        spec["tripo"]["trim"] = {"idle": 120}
        trimmed = tripo_intake.prepare_command(Path("blender.exe"), spec, files, Path("out"), Path("report.json"))
        self.assertEqual(trimmed[trimmed.index("--trim") + 1], "idle=120")
        spec["tripo"]["roles"].pop("death")
        with self.assertRaisesRegex(ValueError, "death"):
            tripo_intake.prepare_command(Path("blender.exe"), spec, files, Path("out"), Path("report.json"))


class IntakeRecords(unittest.TestCase):
    def setUp(self) -> None:
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name).resolve()
        self.job = self.root / "orc_test"
        self.inbox = self.root / "inbox"
        self.inbox.mkdir()
        (self.inbox / "orc_test__rigged.glb").write_bytes(b"tripo rigged export")
        for name, replacement in (("resolve_job_root", lambda slug: self.job), ("ensure_job_layout", self._layout)):
            patcher = mock.patch.object(tripo_intake, name, side_effect=replacement)
            patcher.start()
            self.addCleanup(patcher.stop)
        for name in ("resolve_job_root", "ensure_job_layout"):
            patcher = mock.patch.object(run_pilot, name, side_effect=getattr(tripo_intake, name))
            patcher.start()
            self.addCleanup(patcher.stop)
        patcher = mock.patch.object(tripo_intake, "find_blender", return_value=Path("blender.exe"))
        patcher.start()
        self.addCleanup(patcher.stop)

    def _layout(self, root: Path) -> Path:
        for relative in ("provider/downloads", "provider/tasks", "provider/credits"):
            (self.job / relative).mkdir(parents=True, exist_ok=True)
        return self.job

    def intake(self, **kwargs) -> dict:
        def run(command, **_options):
            return fake_prepare_output(Path(command[command.index("--out-dir") + 1]), command)

        with mock.patch.object(tripo_intake.subprocess, "run", side_effect=run):
            return tripo_intake.run_intake(tripo_spec(), self.inbox, **kwargs)

    def test_the_receipt_records_name_size_and_hash_of_each_file(self) -> None:
        result = self.intake(credits=30, credits_note="rig and animate")
        self.assertEqual(result["state"], "ingested")
        receipt = json.loads((self.job / "provider" / "tripo_intake.json").read_text(encoding="utf-8"))
        (source,) = receipt["sources"]
        self.assertEqual(source["name"], "orc_test__rigged.glb")
        self.assertEqual(source["bytes"], len(b"tripo rigged export"))
        self.assertRegex(source["sha256"], "^[0-9A-F]{64}$")
        self.assertEqual(receipt["task_id"], f"tripo-{source['sha256'].lower()[:12]}")

    def test_manifests_and_tasks_are_what_the_download_step_recognises(self) -> None:
        self.intake()
        downloads = self.job / "provider" / "downloads"
        manifest = json.loads((downloads / "generation_model.glb.manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["file"]["relative_path"], "provider/downloads/generation_model.glb")
        self.assertEqual(manifest["provider"], "tripo")
        self.assertTrue((downloads / "animation_attack_provider.glb.manifest.json").is_file())
        generation = json.loads((self.job / "provider" / "tasks" / "generation.json").read_text(encoding="utf-8"))
        attack = json.loads((self.job / "provider" / "tasks" / "animation_attack.json").read_text(encoding="utf-8"))
        self.assertEqual(generation["status"], "SUCCEEDED")
        self.assertEqual(attack["provider"]["name"], "tripo")
        self.assertEqual(attack["library_clip"], "chop")
        self.assertEqual(attack["task_id"], generation["task_id"])
        # download_once finds the file and its manifest and calls no provider client.
        record = run_pilot.download_once(
            None, self.job, stage="generation_glb", task_id=generation["task_id"], task_type="image-to-3d",
            format_name="glb", filename="generation_model.glb",
        )
        self.assertEqual(record["task_id"], generation["task_id"])

    def test_the_same_files_are_not_ingested_twice_and_other_files_are_refused(self) -> None:
        self.intake()
        self.assertEqual(self.intake()["state"], "already_ingested")
        (self.inbox / "orc_test__rigged.glb").write_bytes(b"a different export")
        with self.assertRaisesRegex(RuntimeError, "generation_stage"):
            self.intake()

    def test_credits_go_to_the_ledger_once_without_a_meshy_balance(self) -> None:
        self.intake(credits=40, credits_note="segment, rig, animate")
        rows = credits.read_ledger(self.job)
        (row,) = rows
        self.assertEqual((row["model"], row["consumed_credits"], row["outcome"]), ("tripo", 40, "success"))
        self.assertEqual(row["consumed_source"], "manual_entry")
        report = credits.credits_report([self.job])
        self.assertEqual(report["totals"]["consumed"], 40)
        self.assertEqual(report["by_model"]["tripo"], 40)
        self.assertEqual(report["totals"]["unknown_consumption"], 0)


class ProviderSwitch(unittest.TestCase):
    def test_a_tripo_job_needs_no_credit_budget_and_plans_no_paid_stage(self) -> None:
        spec = run_pilot.prepare_spec(tripo_spec())
        self.assertEqual(spec["planned_total_credits"], 0)
        self.assertEqual(spec["credit_budget"], 0)
        self.assertEqual({spec[f"{key}_estimate_credits"] for key in ("image_to_3d", "remesh", "rig", "animation")}, {0})
        with mock.patch.object(run_pilot, "MeshyClient", side_effect=AssertionError("Meshy was constructed")):
            run_pilot.preflight_selected_credits([spec], "full")

    def test_a_tripo_main_run_never_constructs_the_meshy_client_or_asks_for_the_key(self) -> None:
        spec = tripo_spec()
        environment = {key: value for key, value in os.environ.items() if key != "MESHY_API_KEY"}
        calls = []
        patches = [
            mock.patch.dict(os.environ, environment, clear=True),
            mock.patch.object(sys, "argv", ["run_pilot.py", "--jobs-config", "jobs.json", "orc_test"]),
            mock.patch.object(run_pilot, "load_job_configs", return_value={"orc_test": spec}),
            mock.patch.object(run_pilot, "MeshyClient", side_effect=AssertionError("Meshy was constructed")),
            mock.patch.object(run_pilot, "initialize_job", side_effect=lambda s: calls.append("init")),
            mock.patch.object(run_pilot, "run_candidate", side_effect=lambda s: calls.append("candidate") or {}),
            mock.patch.object(run_pilot, "continue_unit_humanoid", side_effect=lambda s: calls.append("unit") or {}),
        ]
        for patcher in patches:
            patcher.start()
            self.addCleanup(patcher.stop)
        with mock.patch("builtins.print"):
            self.assertEqual(run_pilot.main(), 0)
        self.assertEqual(calls, ["init", "candidate", "unit"])

    def test_the_unit_stages_read_the_intake_and_make_no_provider_call(self) -> None:
        spec = run_pilot.prepare_spec(tripo_spec())
        with tempfile.TemporaryDirectory() as name:
            job = Path(name) / "orc_test"
            for relative in ("provider/downloads", "provider/tasks"):
                (job / relative).mkdir(parents=True)
            with mock.patch.object(run_pilot, "resolve_job_root", return_value=job), mock.patch.object(
                run_pilot, "ensure_job_layout", side_effect=lambda root: root
            ), mock.patch.object(run_pilot, "MeshyClient", side_effect=AssertionError("Meshy was constructed")):
                with self.assertRaisesRegex(RuntimeError, "tripo_intake.py"):
                    run_pilot.tripo_unit_stages(spec)

    def test_status_names_the_intake_for_a_tripo_job_with_nothing_downloaded(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            job = Path(name) / "orc_test"
            (job / "provider" / "submissions").mkdir(parents=True)
            (job / "provider" / "tasks").mkdir()
            (job / "validation").mkdir()
            (job / "job.yaml").write_text(json.dumps({"status": "preflight"}), encoding="utf-8")
            (job / "validation" / "reference_preflight.json").write_text(json.dumps({"status": "passed"}), encoding="utf-8")
            with mock.patch.object(run_pilot, "resolve_job_root", return_value=job):
                status = run_pilot.job_status("orc_test", run_pilot.prepare_spec(tripo_spec()), Path("jobs.json"))
        self.assertIn("tripo_intake.py", status["next"])
        self.assertIn("orc_test__rigged.glb", status["next"])

    def test_the_bone_shape_icosphere_is_excluded_from_a_tripo_unit_and_its_job_has_no_meshy_plan(self) -> None:
        import init_pilot_jobs as init
        from PIL import Image

        spec = run_pilot.prepare_spec(tripo_spec())
        self.assertEqual(spec["excluded_provider_objects"], ["Icosphere"])
        with tempfile.TemporaryDirectory() as name:
            job = Path(name) / "orc_test"
            (job / "refs/original").mkdir(parents=True)
            for directory in ("refs/derived", "refs/briefs", "validation"):
                (job / directory).mkdir(parents=True)
            Image.new("RGB", (4, 4)).save(job / "refs/original/ref.png")
            full = dict(spec, reference_path="refs/original/ref.png", asset_brief="x", required_components=[], forbidden_additions=[],
                        reference_source_mode="agent", reference_generator_output="x", target_height_m=1.8, proposed_runtime_identifiers={})
            with mock.patch.object(init, "resolve_job_root", return_value=job), mock.patch.object(init, "ensure_job_layout", side_effect=lambda r: r):
                init.initialize_one(full, require_review=False)
            document = json.loads((job / "job.yaml").read_text(encoding="utf-8"))
        self.assertEqual(document["provider"], "tripo")
        self.assertEqual(document["provider_plan"]["mode"], "manual_export")
        self.assertNotIn("meshy_input_gate", document)

    def test_an_unknown_provider_and_unsupported_asset_kinds_are_refused(self) -> None:
        with self.assertRaises(ValueError):
            provider_name({"provider": "blender"})
        with self.assertRaisesRegex(RuntimeError, "Tripo jobs cover"):
            run_pilot.vet_spec(tripo_spec(unit_type="mount"))


class AnimationReceipt(unittest.TestCase):
    def receipt(self, **kwargs) -> dict:
        with tempfile.TemporaryDirectory() as name:
            job = Path(name)
            rel = run_pilot.write_animation_receipt(
                job, "attack", {"task_id": "tripo-abc"}, "chop", "chop", "provider/downloads/a.glb", "AB" * 32, "chop", **kwargs
            )
            return json.loads((job / rel).read_text(encoding="utf-8"))

    def test_a_tripo_clip_is_a_professional_source_with_its_preset_name(self) -> None:
        receipt = self.receipt(source_kind=animation_source_kind(tripo_spec()))
        self.assertEqual(receipt["source_kind"], "professional_source")
        self.assertEqual(receipt["library_clip"], "chop")
        self.assertEqual(receipt["verification_status"], "verified")
        self.assertEqual(receipt["source_reference_id"], "tripo-abc")

    def test_a_meshy_job_still_writes_meshy_animate(self) -> None:
        self.assertEqual(self.receipt()["source_kind"], "meshy_animate")
        self.assertEqual(animation_source_kind({"unit_type": "infantry_melee"}), "meshy_animate")


class MeshyBootstrapGate(unittest.TestCase):
    def lock(self, directory: str, routes: dict) -> Path:
        path = Path(directory) / "dependencies.lock.json"
        path.write_text(json.dumps({"routes": routes}), encoding="utf-8")
        return path

    def test_a_blender_only_bootstrap_blocks_meshy_jobs_until_a_full_bootstrap(self) -> None:
        with tempfile.TemporaryDirectory() as name, mock.patch("builtins.print") as printed:
            lock = self.lock(name, {"meshy_mcp": {"verified": False, "reason": "no key"}})
            with self.assertRaises(SystemExit) as stop:
                run_pilot.require_meshy_bootstrap(lock)
            self.assertEqual(stop.exception.code, 2)
            self.assertIn("bootstrap_3d_workflow.py", printed.call_args.args[0])

    def test_a_full_bootstrap_an_old_lock_or_no_lock_do_not_block(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            run_pilot.require_meshy_bootstrap(self.lock(name, {"meshy_mcp": {"version": "0.6.9"}}))
            run_pilot.require_meshy_bootstrap(self.lock(name, {}))
            run_pilot.require_meshy_bootstrap(Path(name) / "missing.json")


class MeshyJobsUnchanged(unittest.TestCase):
    def test_a_job_without_provider_is_a_meshy_job_that_needs_its_budget_and_key(self) -> None:
        spec = {"asset_id": "x.orc", "unit_type": "infantry_melee", "runtime_stem": "orc"}
        self.assertEqual(provider_name(spec), "meshy")
        self.assertFalse(uses_tripo(spec))
        with self.assertRaisesRegex(RuntimeError, "credit_budget"):
            run_pilot.prepare_spec(dict(spec))
        prepared = run_pilot.prepare_spec(dict(spec), require_budget=False)
        self.assertGreater(prepared["planned_total_credits"], 0)
        environment = {key: value for key, value in os.environ.items() if key != "MESHY_API_KEY"}
        with mock.patch.dict(os.environ, environment, clear=True), mock.patch.object(
            sys, "argv", ["run_pilot.py", "--jobs-config", "jobs.json", "orc"]
        ), mock.patch.object(run_pilot, "load_job_configs", return_value={"orc": spec}), mock.patch("builtins.print"):
            with self.assertRaises(SystemExit) as stop:
                run_pilot.main()
        self.assertEqual(stop.exception.code, 2)


class AtlasLayout(unittest.TestCase):
    def test_the_body_keeps_seven_eighths_and_the_weapon_gets_an_edge_cell(self) -> None:
        from lib.tripo import atlas_layout

        layout = atlas_layout([(2048, 2048), (512, 512)])
        self.assertEqual(layout["size"], 2048)
        self.assertEqual(layout["main"], 0)
        self.assertEqual(layout["rects"], [(0, 0, 1792, 1792), (1792, 0, 256, 256)])

    def test_the_largest_texture_is_the_body_whatever_its_position(self) -> None:
        from lib.tripo import atlas_layout

        layout = atlas_layout([(512, 512), (2048, 2048), (512, 512)])
        self.assertEqual(layout["main"], 1)
        self.assertEqual(layout["rects"], [(1792, 0, 256, 256), (0, 0, 1792, 1792), (1792, 256, 256, 256)])

    def test_cells_never_overlap_and_stay_inside_the_atlas(self) -> None:
        from lib.tripo import atlas_layout

        layout = atlas_layout([(2048, 2048)] + [(512, 512)] * 15)
        side, covered = layout["size"], set()
        for x, y, width, height in layout["rects"]:
            self.assertTrue(0 <= x and x + width <= side and 0 <= y and y + height <= side)
            cells = {(cx, cy) for cx in range(x // 256, (x + width) // 256) for cy in range(y // 256, (y + height) // 256)}
            self.assertFalse(cells & covered)
            covered |= cells

    def test_too_many_parts_are_refused(self) -> None:
        from lib.tripo import atlas_layout

        with self.assertRaises(ValueError):
            atlas_layout([(2048, 2048)] + [(512, 512)] * 16)


if __name__ == "__main__":
    unittest.main()
