"""The complete Tripo job entry in docs/3d-units.md (step 2) against the code that reads it, so the page cannot drift from the route.

The page carries a `3d_jobs.json` with an unarmed and an armed entry, and the answers file of the picture review. Each is run through the
real functions: the job's initialization, the review, the size check, the intake's command, the vanilla reference. A field the code
needs and the page lacks fails here. The unit type the page names for an unarmed soldier is checked too."""

from __future__ import annotations

import contextlib
import copy
import io
import json
import os
import re
import struct
import sys
import tempfile
import unittest
import zlib
from pathlib import Path
from unittest import mock

PIPELINE = Path(__file__).resolve().parents[1]
REPO = PIPELINE.parents[1]
sys.path.insert(0, str(PIPELINE))

import init_pilot_jobs
import measure_body
import run_pilot
import tripo_intake
from lib import paths

DOC = (REPO / "docs" / "3d-units.md").read_text(encoding="utf-8")
SIX_ROLES = {"idle", "move", "attack", "defend", "retreat", "death"}


def step_two() -> str:
    start = DOC.index("### 2. Job entry")
    return DOC[start:DOC.index("### 3. Model")]


def json_blocks(text: str) -> list:
    return [json.loads(block) for block in re.findall(r"```json\n(.*?)\n```", text, flags=re.S)]


def tiny_png() -> bytes:
    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    row = b"\x00" + b"\x80\x40\x40" * 2
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", 2, 1, 8, 2, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(row)) + chunk(b"IEND", b"")


class DocumentedEntry(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        blocks = json_blocks(step_two())
        cls.registry, cls.answers = blocks[0], blocks[1]
        cls.jobs = cls.registry["jobs"]

    def setUp(self) -> None:
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name).resolve()
        self.job = self.root / "job"
        for target in (init_pilot_jobs, run_pilot):
            for name, replacement in (("resolve_job_root", lambda slug: self.job), ("ensure_job_layout", self.layout)):
                patcher = mock.patch.object(target, name, side_effect=replacement)
                patcher.start()
                self.addCleanup(patcher.stop)

    def layout(self, _root: Path) -> Path:
        for relative in paths.JOB_DIRS:
            (self.job / relative).mkdir(parents=True, exist_ok=True)
        return self.job

    def spec(self, name: str) -> dict:
        return copy.deepcopy(self.jobs[name])

    def test_the_page_shows_an_unarmed_and_an_armed_entry_and_the_review_answers(self) -> None:
        self.assertEqual(sorted(self.jobs), ["axe_soldier", "undead_soldier"])
        self.assertEqual(set(self.answers) - {"notes"}, set(init_pilot_jobs.VISUAL_PREFLIGHT_CHECKS))
        self.assertTrue(all(value is True for key, value in self.answers.items() if key != "notes"))
        self.assertNotIn("weapon", self.jobs["undead_soldier"]["tripo"])
        self.assertEqual(self.jobs["axe_soldier"]["tripo"]["weapon"]["source"], "rigged")

    def test_each_entry_has_every_field_the_scripts_read(self) -> None:
        for name, spec in self.jobs.items():
            with self.subTest(job=name):
                self.assertEqual(init_pilot_jobs.missing_entry_fields(spec), [])
                self.assertEqual(spec["asset_id"], f"hoi4_3d_model_jobs.{name}")
                self.assertEqual(spec["provider"], "tripo")
                self.assertEqual(spec["runtime_stem"], name)
                for field in ("runtime_entity_scale", "credit_budget", "anatomy", "vanilla_scale_reference", "tripo"):
                    self.assertIn(field, spec)
                self.assertEqual(set(spec["tripo"]["roles"]), SIX_ROLES)
                reference = spec["vanilla_scale_reference"]
                for field in ("mesh", "entity", "mesh_object_names", "exclude_name_patterns", "forward_axis", "up_axis", "mesh_height", "entity_scale", "runtime_height"):
                    self.assertIn(field, reference)

    def test_the_unit_type_and_the_anatomy_fit_a_body_preset(self) -> None:
        types = json.loads((PIPELINE / "config" / "unit_types.json").read_text(encoding="utf-8"))["types"]
        presets = json.loads((PIPELINE / "config" / "body_presets.json").read_text(encoding="utf-8"))
        for name, spec in self.jobs.items():
            with self.subTest(job=name):
                self.assertIn(spec["unit_type"], types)
                self.assertEqual(set(spec["anatomy"]), set(presets["anatomy_questions"]), "the page answers every question, and no other key")
                wanted = presets["presets"][types[spec["unit_type"]]["body"]]["anatomy"]
                for key, value in wanted.items():
                    self.assertEqual(spec["anatomy"][key], value, key)

    def test_the_size_check_and_the_budget_accept_the_entries(self) -> None:
        for name in self.jobs:
            with self.subTest(job=name):
                spec = run_pilot.prepare_spec(self.spec(name), require_budget=False)
                self.assertEqual(spec["asset_kind"], "humanoid")
                self.assertEqual({action["role"] for action in spec["required_actions"]}, SIX_ROLES)

    def test_the_documented_sequence_initializes_reviews_and_passes_the_runner(self) -> None:
        """init_pilot_jobs.py, then the recorded review, then the job initialization that run_pilot.py makes (step 9)."""

        for name in self.jobs:
            with self.subTest(job=name):
                spec = self.spec(name)
                (self.job / "refs" / "original").mkdir(parents=True, exist_ok=True)
                (self.job / "refs" / "original" / Path(spec["reference_path"]).name).write_bytes(tiny_png())
                run_pilot.prepare_spec(spec, require_budget=False)
                first = init_pilot_jobs.initialize_one(spec, require_review=False)
                self.assertEqual(first["visual_preflight"], "pending_review")
                with self.assertRaisesRegex(RuntimeError, "pending_review"):
                    run_pilot.initialize_job(self.spec(name))
                answers = dict(self.answers)
                notes = answers.pop("notes")
                outcome = init_pilot_jobs.record_visual_preflight_review(self.job, answers, reviewer="a reviewer", notes=notes)
                self.assertEqual(outcome["status"], "passed")
                run_pilot.initialize_job(self.spec(name))  # no refusal
                saved = json.loads((self.job / "job.yaml").read_text(encoding="utf-8"))
                self.assertEqual(saved["unit_type"], spec["unit_type"], "measure_body.py reads the unit type from the job")
                self.assertEqual(saved["anatomy"], spec["anatomy"], "and the anatomy answers")
                self.assertEqual(saved["provider"], "tripo")
                self.layout_cleanup()

    def layout_cleanup(self) -> None:
        import shutil

        shutil.rmtree(self.job, ignore_errors=True)

    def test_the_intake_command_names_every_role_and_only_an_armed_unit_has_a_weapon(self) -> None:
        for name, weapon in (("undead_soldier", False), ("axe_soldier", True)):
            with self.subTest(job=name):
                spec = run_pilot.prepare_spec(self.spec(name), require_budget=False)
                with contextlib.redirect_stderr(io.StringIO()):
                    command = tripo_intake.prepare_command(Path("blender.exe"), spec, {"rigged": Path("missing.glb")}, Path("out"), Path("report.json"))
                roles = command[command.index("--roles") + 1:]
                for role, clip in spec["tripo"]["roles"].items():
                    self.assertIn(f"{role}={clip}", roles)
                self.assertEqual("--rigid-part" in command, weapon)
                if weapon:
                    self.assertEqual(command[command.index("--rigid-part") + 1], "tripo_part_1=Weapon")

    def test_the_vanilla_reference_of_the_entry_is_found_in_the_game_folder(self) -> None:
        game = self.root / "game"
        mesh = game / "gfx" / "models" / "units" / "western_european_infantry.mesh"
        mesh.parent.mkdir(parents=True)
        mesh.write_bytes(b"vanilla")
        spec = run_pilot.prepare_spec(self.spec("undead_soldier"), require_budget=False)
        self.layout(self.job)
        with mock.patch.object(run_pilot, "installed_game_dir", return_value=game):
            staged = run_pilot.stage_vanilla_reference(self.job, spec)
        self.assertEqual(staged["mesh_height"], 7.3518242835)
        self.assertTrue((self.job / "blender" / "reference" / "western_european_infantry.mesh").is_file())
        spec["vanilla_scale_reference"]["mesh"] = "gfx/models/units/missing.mesh"
        with mock.patch.object(run_pilot, "installed_game_dir", return_value=game), self.assertRaisesRegex(FileNotFoundError, "missing.mesh"):
            run_pilot.stage_vanilla_reference(self.job, spec)


class MissingFields(unittest.TestCase):
    """The entry a small model wrote on 2026-11-19 (no reference fields) stopped with a bare KeyError."""

    ENTRY = {
        "asset_id": "hoi4_3d_model_jobs.undead_soldier", "unit_type": "infantry_unarmed", "runtime_stem": "undead_soldier", "provider": "tripo",
        "credit_budget": 70, "anatomy": {"limbs": 2, "wings": False, "weapon_in_hand": False}, "target_height_m": 7.35, "runtime_entity_scale": 0.8,
        "tripo": {"roles": {"idle": "idle", "move": "walk", "attack": "box_01", "defend": "hit_to_body_01", "retreat": "flee_01", "death": "fall"}},
    }

    def test_the_missing_fields_are_listed(self) -> None:
        self.assertEqual(
            init_pilot_jobs.missing_entry_fields(self.ENTRY),
            ["reference_path", "reference_source_mode", "reference_generator_output", "asset_brief", "required_components", "forbidden_additions", "proposed_runtime_identifiers"],
        )

    def test_the_command_names_them_and_does_not_ask_for_a_meshy_key(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            registry = Path(folder) / "3d_jobs.json"
            registry.write_text(json.dumps({"jobs": {"undead_soldier": self.ENTRY}}), encoding="utf-8")
            environment = {key: value for key, value in os.environ.items() if key != "MESHY_API_KEY"}
            with mock.patch.dict(os.environ, environment, clear=True), mock.patch.object(init_pilot_jobs, "REPO_ROOT", Path(folder).resolve()), \
                    mock.patch.object(sys, "argv", ["init_pilot_jobs.py", "--jobs-config", str(registry), "undead_soldier"]):
                with self.assertRaises(SystemExit) as stop, contextlib.redirect_stdout(io.StringIO()) as printed:
                    init_pilot_jobs.main()
        self.assertIn("reference_path", str(stop.exception))
        self.assertIn("step 2", str(stop.exception))
        self.assertNotIn("MESHY_API_KEY", printed.getvalue())


class UnarmedSoldierType(unittest.TestCase):
    def test_an_unarmed_soldier_sized_humanoid_has_its_own_type(self) -> None:
        types = json.loads((PIPELINE / "config" / "unit_types.json").read_text(encoding="utf-8"))["types"]
        unit = types["infantry_unarmed"]
        self.assertEqual((unit["body"], unit["profile"], unit["entity_template"]), ("humanoid", "humanoid_unit", "infantry"))
        self.assertEqual(set(unit["roles"]), SIX_ROLES)
        for role, config in unit["roles"].items():
            with self.subTest(role=role):
                self.assertEqual(len(config["meshy"]), 2)
        self.assertEqual(measure_body.body_types()["infantry_unarmed"], "humanoid")
        # the other types are untouched
        self.assertEqual(types["infantry_melee"]["roles"]["attack"]["meshy"][0], [219, "Right_Hand_Sword_Slash"])
        self.assertEqual(types["beast_biped"]["body"], "large_biped")

    def test_the_six_roles_are_distinct_clips_so_the_runner_plans_six_actions(self) -> None:
        spec = run_pilot.apply_unit_type({"unit_type": "infantry_unarmed", "provider": "tripo"})
        self.assertEqual([action["role"] for action in spec["required_actions"]], ["idle", "move", "attack", "defend", "retreat", "death"])
        self.assertFalse(any(action.get("reuse_role") for action in spec["required_actions"]))


class PageStaysTrue(unittest.TestCase):
    """What the page says about paths, the gate and the setup output matches the code."""

    def test_the_tripo_pages_are_named(self) -> None:
        self.assertIn("studio.tripo3d.ai/workspace/generate-image", DOC)
        self.assertIn("studio.tripo3d.ai/workspace/animate/<asset id>", DOC)
        self.assertIn("studio.tripo3d.ai/workspace/generate/<asset id>", DOC)
        self.assertIn("A look change is also a redraw.", DOC)
        self.assertIn("A promotion dialog is closed, never used.", DOC)

    def test_the_page_lists_every_command_that_starts_blender(self) -> None:
        listing = DOC[DOC.index("The commands that start Blender, and so wait:"):DOC.index("### 9. Blender stage and export")]
        callers = set()
        for path in PIPELINE.rglob("*.py"):
            if "tests" in path.parts or path.name == "heavy_job.py":
                continue
            text = path.read_text(encoding="utf-8")
            if "heavy_job.run(" in text or "heavy_job.hold(" in text:
                callers.add("run_pilot.py" if path.name == "blender_client.py" else path.name)
        self.assertGreaterEqual(len(callers), 10)
        for name in callers:
            with self.subTest(command=name):
                self.assertIn(name, listing)

    def test_the_page_explains_the_two_codes_of_the_setup_record(self) -> None:
        self.assertIn('"claude_registration": "claude_cli_not_found"', DOC)
        self.assertIn('"template_removed": true', DOC)
        self.assertIn("neutral_bone", DOC)
        self.assertIn("extra joints dropped:", DOC)
        for text in (
            "Claude Code registration skipped",
            "Config template removed",
        ):
            self.assertTrue(any(text in line for line in __import__("bootstrap_3d_workflow").explain_outcomes("claude_cli_not_found", True)))


if __name__ == "__main__":
    unittest.main()
