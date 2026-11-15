"""wire_unit.py: writing a finished unit's registration into a mod, rerunning it and reporting what is missing."""

from __future__ import annotations

import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))

import wire_unit
from lib import unit_wiring as wiring
from lib.unit_registration import registration_text

STEM = "ab_ghoul"
FOLDER = f"gfx/models/units/{STEM}"
SUBUNIT = """sub_units = {
	ghoul_infantry = {
		abbreviation = "GHL"
		sprite = ab_ghoul
		map_icon_category = infantry
	}
}
"""
CLEAN_CHECKS = {"exit": 0, "errors": [], "warnings": []}


def write(path: Path, text: str | bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text if isinstance(text, bytes) else text.encode("utf-8"))


def make_job(root: Path, sound_plan=None, roles=("idle", "move", "attack", "defend", "retreat", "death")) -> Path:
    job = root / "job"
    text = registration_text(unit_entity=f"{STEM}_entity", model_folder=FOLDER, stem=STEM, shapes=["shape_0"], roles=list(roles), scale=0.8, template="infantry")
    write(job / "runtime" / "registration.md", text)
    names = [f"{STEM}.mesh", f"{STEM}_diffuse.dds", f"{STEM}_normal.dds", f"{STEM}_specular.dds"] + [f"{STEM}_{role}.anim" for role in roles]
    for name in names:
        write(job / "runtime" / "files" / name, f"bytes of {name}".encode())
    spec = {"blender_plan": {"runtime_stem": STEM}, "unit_type": "infantry_melee"}
    if sound_plan is not None:
        spec["sound_plan"] = sound_plan
    write(job / "job.yaml", json.dumps(spec))
    write(job / "runtime" / "files.json", json.dumps({"facts": {"animations": {f"{STEM}_move.anim": {"samples": 70}, f"{STEM}_attack.anim": {"samples": 150}}}}))
    return job


def make_mod(root: Path, subunit: bool = True, localisation: bool = True, counters: bool = False) -> Path:
    mod = root / "mod"
    write(mod / "descriptor.mod", 'name = "fixture"\n')
    if subunit:
        write(mod / "common" / "units" / "ghoul.txt", SUBUNIT)
    if localisation:
        write(mod / "localisation" / "english" / "ghoul_l_english.yml", 'l_english:\n ghoul_infantry:0 "Ghoul"\n ghoul_infantry_desc:0 "Hungry."\n')
    if counters:
        write(mod / "interface" / "subuniticons.gfx", f'spriteTypes = {{\n\tspriteType = {{ name = "GFX_unit_{STEM}_icon_medium" textureFile = "gfx/interface/counters/a.dds" }}\n}}\n')
        write(mod / "gfx" / "interface" / "counters" / "a.dds", b"dds")
    return mod


def run(job: Path, mod: Path, *extra: str, checks=CLEAN_CHECKS, audit=None):
    """Run the tool with its two subprocess checks replaced; return (exit code, parsed --json result)."""

    audit = audit or {"exit": 0, "findings": []}
    out = io.StringIO()
    with mock.patch.object(wire_unit, "run_check_unit_files", return_value=checks), mock.patch.object(wire_unit, "run_audit", return_value=audit), mock.patch.object(wire_unit, "game_dir", return_value=None), redirect_stdout(out):
        code = wire_unit.main([str(job), "--mod-root", str(mod), "--json", *extra])
    return code, json.loads(out.getvalue())


def snapshot(mod: Path) -> dict:
    return {path.relative_to(mod).as_posix(): path.read_bytes() for path in sorted(mod.rglob("*")) if path.is_file()}


class FirstWrite(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.job = make_job(self.root)
        self.mod = make_mod(self.root)
        self.addCleanup(self.tmp.cleanup)

    def test_writes_each_block_between_markers_and_copies_the_runtime_files(self) -> None:
        code, result = run(self.job, self.mod)
        self.assertEqual(code, 0, result["errors"])
        self.assertEqual(result["verdict"], "PASS")
        gfx = (self.mod / "gfx/entities/ab_units.gfx").read_text(encoding="utf-8")
        self.assertTrue(gfx.startswith("objectTypes = {"))
        self.assertIn(f"# wire_unit begin {STEM} pdxmesh", gfx)
        self.assertIn(f'name = "{STEM}_mesh"', gfx)
        self.assertTrue(gfx.rstrip().endswith("}"))
        asset = (self.mod / FOLDER / f"{STEM}.asset").read_text(encoding="utf-8")
        self.assertIn(f"# wire_unit begin {STEM} animations", asset)
        self.assertIn(f'name = "{STEM}_idle_animation"', asset)
        entity = (self.mod / "gfx/entities/ab_units.asset").read_text(encoding="utf-8")
        self.assertIn(f'name = "{STEM}_entity"', entity)
        self.assertEqual((self.mod / FOLDER / f"{STEM}.mesh").read_bytes(), f"bytes of {STEM}.mesh".encode())
        self.assertTrue((self.mod / FOLDER / f"{STEM}_normal.dds").is_file())

    def test_a_missing_sound_plan_is_a_visible_warning(self) -> None:
        _code, result = run(self.job, self.mod)
        self.assertTrue(any(line.startswith("no sound plan") for line in result["warnings"]))
        text = io.StringIO()
        with mock.patch.object(wire_unit, "run_check_unit_files", return_value=CLEAN_CHECKS), mock.patch.object(wire_unit, "run_audit", return_value={"exit": 0, "findings": []}), redirect_stdout(text):
            wire_unit.main([str(self.job), "--mod-root", str(self.mod)])
        self.assertIn("WARNING: no sound plan", text.getvalue())

    def test_the_target_follows_the_mods_one_units_gfx(self) -> None:
        write(self.mod / "gfx/entities/zed_units.gfx", "objectTypes = {\n}\n")
        _code, result = run(self.job, self.mod)
        paths = [item["path"] for item in result["plan"]]
        self.assertIn("gfx/entities/zed_units.gfx", paths)
        self.assertIn("gfx/entities/zed_units.asset", paths)

    def test_explicit_targets_win(self) -> None:
        _code, result = run(self.job, self.mod, "--gfx-file", "gfx/mine.gfx", "--entity-file", "gfx/entities/mine.asset")
        paths = [item["path"] for item in result["plan"]]
        self.assertIn("gfx/mine.gfx", paths)
        self.assertIn("gfx/entities/mine.asset", paths)

    def test_a_job_id_resolves_through_the_kits_job_root(self) -> None:
        with mock.patch.object(wire_unit, "resolve_job_root", return_value=self.job) as resolver:
            _code, result = run(wire_unit.JOB_ID_PREFIX + STEM, self.mod)
        resolver.assert_called_once_with(STEM)
        self.assertEqual(result["stem"], STEM)


class Rerun(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.job = make_job(self.root)
        self.mod = make_mod(self.root)
        self.addCleanup(self.tmp.cleanup)

    def test_a_second_run_changes_no_byte(self) -> None:
        run(self.job, self.mod)
        first = snapshot(self.mod)
        _code, result = run(self.job, self.mod)
        self.assertEqual(snapshot(self.mod), first)
        self.assertEqual({item["status"] for item in result["plan"]}, {"unchanged"})

    def test_a_changed_block_is_replaced_only_between_its_markers(self) -> None:
        gfx_path = self.mod / "gfx/entities/ab_units.gfx"
        write(gfx_path, "# my header\nobjectTypes = {\n\tspriteType = { name = \"GFX_mine\" }\n}\n# my footer\n")
        run(self.job, self.mod)
        before = gfx_path.read_text(encoding="utf-8")
        self.assertIn("GFX_mine", before)
        # the registration changes: a different scale in the entity, a new texture name in the pdxmesh
        registration = self.job / "runtime" / "registration.md"
        registration.write_text(registration.read_text(encoding="utf-8").replace('"ab_ghoul_diffuse.dds"', '"ab_ghoul_diffuse.dds" # edited').replace("scale = 0.8", "scale = 0.9"), encoding="utf-8")
        run(self.job, self.mod)
        after = gfx_path.read_text(encoding="utf-8")
        self.assertIn("# edited", after)
        self.assertEqual(after.count(f"# wire_unit begin {STEM} pdxmesh"), 1)
        head, tail = before.split(f"# wire_unit begin {STEM} pdxmesh")[0], before.split(f"# wire_unit end {STEM} pdxmesh")[1]
        self.assertTrue(after.startswith(head))
        self.assertTrue(after.endswith(tail))
        self.assertIn("scale = 0.9", (self.mod / "gfx/entities/ab_units.asset").read_text(encoding="utf-8"))

    def test_foreign_content_keeps_its_bytes_bom_and_newlines(self) -> None:
        entity_path = self.mod / "gfx/entities/ab_units.asset"
        foreign = b"\xef\xbb\xbfentity = {\r\n\tname = \"other_entity\"\r\n\tscale = 1\r\n}\r\n"
        write(entity_path, foreign)
        run(self.job, self.mod)
        first = entity_path.read_bytes()
        self.assertTrue(first.startswith(foreign.rstrip(b"\r\n")))
        self.assertTrue(first.startswith(b"\xef\xbb\xbf"))
        self.assertNotIn(b"\n\t", first.replace(b"\r\n", b""))  # every newline is CRLF
        run(self.job, self.mod)
        self.assertEqual(entity_path.read_bytes(), first)

    def test_a_broken_marker_pair_is_an_error_and_writes_nothing(self) -> None:
        write(self.mod / "gfx/entities/ab_units.gfx", f"objectTypes = {{\n# wire_unit begin {STEM} pdxmesh\n}}\n")
        before = snapshot(self.mod)
        code, result = run(self.job, self.mod)
        self.assertEqual(code, 1)
        self.assertTrue(any("broken" in line for line in result["errors"]))
        self.assertEqual(snapshot(self.mod), before)

    def test_a_hand_pasted_copy_outside_the_markers_is_a_conflict(self) -> None:
        write(self.mod / "gfx/entities/mine.asset", f'entity = {{\n\tname = "{STEM}_entity"\n}}\n')
        before = snapshot(self.mod)
        code, result = run(self.job, self.mod)
        self.assertEqual(code, 1)
        self.assertTrue(any("already defines" in line for line in result["errors"]))
        self.assertEqual(snapshot(self.mod), before)

    def test_a_changed_runtime_file_is_copied_again_and_a_same_one_is_skipped(self) -> None:
        run(self.job, self.mod)
        write(self.job / "runtime" / "files" / f"{STEM}_idle.anim", b"new idle")
        _code, result = run(self.job, self.mod)
        by_path = {item["path"]: item["status"] for item in result["plan"]}
        self.assertEqual(by_path[f"{FOLDER}/{STEM}_idle.anim"], "update")
        self.assertEqual(by_path[f"{FOLDER}/{STEM}_move.anim"], "unchanged")
        self.assertEqual((self.mod / FOLDER / f"{STEM}_idle.anim").read_bytes(), b"new idle")


class Reports(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.job = make_job(self.root)
        self.addCleanup(self.tmp.cleanup)

    def test_a_missing_sub_unit_sprite_fails(self) -> None:
        mod = make_mod(self.root, subunit=False)
        code, result = run(self.job, mod)
        self.assertEqual((code, result["verdict"]), (1, "FAIL"))
        self.assertTrue(any(f"sprite = {STEM}" in line for line in result["errors"]))

    def test_a_sprite_that_points_elsewhere_is_missing(self) -> None:
        mod = make_mod(self.root, subunit=False)
        write(mod / "common/units/x.txt", SUBUNIT.replace("sprite = ab_ghoul", "sprite = infantry"))
        _code, result = run(self.job, mod)
        self.assertEqual(result["subunit"]["subunits"], [])

    def test_missing_localisation_keys_are_listed_and_fail(self) -> None:
        mod = make_mod(self.root, localisation=False)
        write(mod / "localisation/english/x_l_english.yml", 'l_english:\n ghoul_infantry:0 "Ghoul"\n')
        code, result = run(self.job, mod)
        self.assertEqual(result["subunit"]["missing_localisation"], ["ghoul_infantry_desc"])
        self.assertEqual(code, 1)

    def test_counter_tokens_report_mod_art_and_gaps_without_failing(self) -> None:
        mod = make_mod(self.root, counters=True)
        code, result = run(self.job, mod)
        status = {row["token"]: row["status"] for row in result["counters"]}
        self.assertEqual(status[f"GFX_unit_{STEM}_icon_medium"], "mod")
        self.assertEqual(status[f"GFX_unit_{STEM}_icon_medium_white"], "missing")
        self.assertEqual(code, 0)
        self.assertTrue(any("icon_medium_white" in line for line in result["warnings"]))

    def test_check_errors_make_the_verdict_fail_with_exit_1(self) -> None:
        mod = make_mod(self.root)
        checks = {"exit": 1, "errors": ["UNIT-MESH-UNREADABLE x.mesh: broken"], "warnings": []}
        code, result = run(self.job, mod, checks=checks)
        self.assertEqual((code, result["verdict"]), (1, "FAIL"))
        self.assertIn("check_unit_files: UNIT-MESH-UNREADABLE x.mesh: broken", result["errors"])

    def test_audit_errors_about_the_unit_fail_and_others_only_warn(self) -> None:
        mod = make_mod(self.root)
        findings = [
            {"level": "error", "rule": "GFX-3D-ENTITY", "path": "gfx/entities/ab_units.asset", "line": 1, "message": "bad"},
            {"level": "error", "rule": "GFX-MISSING-FILE", "path": "interface/old.gfx", "line": 1, "message": "gfx/old.dds does not exist"},
        ]
        code, result = run(self.job, mod, audit={"exit": 1, "findings": findings})
        self.assertEqual(code, 1)
        self.assertEqual(len([line for line in result["errors"] if line.startswith("audit ")]), 1)
        self.assertTrue(any("not about this unit" in line for line in result["warnings"]))
        code, result = run(self.job, mod, "--strict-audit", audit={"exit": 1, "findings": findings})
        self.assertEqual(len([line for line in result["errors"] if line.startswith("audit ")]), 2)

    def test_an_audit_that_cannot_run_fails_instead_of_passing(self) -> None:
        mod = make_mod(self.root)
        code, result = run(self.job, mod, audit={"exit": 2, "unavailable": "no game folder", "findings": []})
        self.assertEqual((code, result["verdict"]), (1, "FAIL"))

    def test_a_job_without_registration_is_a_usage_error(self) -> None:
        mod = make_mod(self.root)
        (self.job / "runtime" / "registration.md").unlink()
        err = io.StringIO()
        with redirect_stderr(err):
            code = wire_unit.main([str(self.job), "--mod-root", str(mod)])
        self.assertEqual(code, 2)
        self.assertIn("registration.md", err.getvalue())

    def test_a_runtime_file_the_registration_names_but_the_job_lacks_fails_and_writes_nothing(self) -> None:
        mod = make_mod(self.root)
        (self.job / "runtime" / "files" / f"{STEM}_normal.dds").unlink()
        before = snapshot(mod)
        code, result = run(self.job, mod)
        self.assertEqual(code, 1)
        self.assertTrue(any("_normal.dds" in line for line in result["errors"]))
        self.assertEqual(snapshot(mod), before)


class DryRun(unittest.TestCase):
    def test_changes_nothing_and_runs_no_checks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            job, mod = make_job(root), make_mod(root)
            before = snapshot(mod)
            check, audit = mock.Mock(), mock.Mock()
            out = io.StringIO()
            with mock.patch.object(wire_unit, "run_check_unit_files", check), mock.patch.object(wire_unit, "run_audit", audit), redirect_stdout(out):
                code = wire_unit.main([str(job), "--mod-root", str(mod), "--dry-run"])
            self.assertEqual(code, 0)
            self.assertEqual(snapshot(mod), before)
            check.assert_not_called()
            audit.assert_not_called()
            self.assertIn("create", out.getvalue())
            self.assertIn("VERDICT: DRY-RUN", out.getvalue())

    def test_a_conflict_in_a_dry_run_still_exits_1(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            job, mod = make_job(root), make_mod(root)
            write(mod / "gfx/entities/mine.asset", f'entity = {{\n\tname = "{STEM}_entity"\n}}\n')
            code, _result = run(job, mod, "--dry-run")
            self.assertEqual(code, 1)


class SoundPlan(unittest.TestCase):
    def test_events_are_written_into_the_named_states(self) -> None:
        plan = [{"role": "move", "soundeffect": "ghoul_step", "frame": 12}, {"role": "attack", "soundeffect": "ghoul_snarl", "frame": 40}]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            job, mod = make_job(root, sound_plan=plan), make_mod(root)
            _code, result = run(job, mod)
            entity = (mod / "gfx/entities/ab_units.asset").read_text(encoding="utf-8")
            self.assertIn('event = { time = 12 sound = { soundeffect = "ghoul_step" } }', entity)
            self.assertIn('event = { time = 40 sound = { soundeffect = "ghoul_snarl" } }', entity)
            self.assertFalse(any(line.startswith("no sound plan") for line in result["warnings"]))
            self.assertTrue(any("ghoul_step" in line and "defined in no sound" in line for line in result["warnings"]))
            first = snapshot(mod)
            run(job, mod)
            self.assertEqual(snapshot(mod), first)

    def test_a_frame_past_the_clip_is_an_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            job, mod = make_job(root, sound_plan=[{"role": "move", "soundeffect": "s", "frame": 70}]), make_mod(root)
            before = snapshot(mod)
            code, result = run(job, mod)
            self.assertEqual(code, 1)
            self.assertTrue(any("frame 70" in line for line in result["errors"]))
            self.assertEqual(snapshot(mod), before)

    def test_a_sound_file_name_is_refused_as_a_soundeffect(self) -> None:
        with self.assertRaises(wiring.WiringError):
            wiring.parse_sound_plan([{"role": "move", "soundeffect": "step.wav", "frame": 1}])

    def test_a_role_the_entity_lacks_is_an_error(self) -> None:
        block = registration_text(unit_entity="x_entity", model_folder="gfx/models/units/x", stem="x", shapes=["s"], roles=["idle"], scale=1.0, template="infantry")
        entity = wiring.parse_registration(block).entity_block
        with self.assertRaises(wiring.WiringError):
            wiring.apply_sound_events(entity, [wiring.SoundEvent("move", "s", 1)])

    def test_a_state_that_already_has_an_event_gets_another_before_its_brace(self) -> None:
        entity = 'entity = {\n\tstate = { name = "move" animation = "move"\n\t\tevent = { sound = { soundeffect = "a" } }\n\t}\n}'
        result = wiring.apply_sound_events(entity, [wiring.SoundEvent("move", "b", 3)])
        self.assertEqual(result.split("\n")[-3:], ['\t\tevent = { time = 3 sound = { soundeffect = "b" } }', "\t}", "}"])


class Fixture(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.job = make_job(self.root)
        self.mod = make_mod(self.root)
        self.addCleanup(self.tmp.cleanup)


class NoDuplicateBlocks(Fixture):
    def test_a_rerun_with_another_gfx_file_is_refused_and_writes_nothing(self) -> None:
        run(self.job, self.mod)
        before = snapshot(self.mod)
        code, result = run(self.job, self.mod, "--gfx-file", "gfx/other.gfx")
        self.assertEqual(code, 1)
        self.assertTrue(any("already in gfx/entities/ab_units.gfx" in line for line in result["errors"]), result["errors"])
        self.assertEqual(snapshot(self.mod), before)
        self.assertFalse((self.mod / "gfx/other.gfx").exists())

    def test_a_rerun_with_another_entity_file_is_refused_and_writes_nothing(self) -> None:
        run(self.job, self.mod)
        before = snapshot(self.mod)
        code, result = run(self.job, self.mod, "--entity-file", "gfx/entities/other.asset")
        self.assertEqual(code, 1)
        self.assertTrue(any("already in gfx/entities/ab_units.asset" in line for line in result["errors"]), result["errors"])
        self.assertEqual(snapshot(self.mod), before)

    def test_naming_the_file_that_already_holds_the_block_is_fine(self) -> None:
        run(self.job, self.mod)
        before = snapshot(self.mod)
        code, result = run(self.job, self.mod, "--gfx-file", "gfx\\entities\\ab_units.gfx", "--entity-file", "gfx/entities/ab_units.asset")
        self.assertEqual(code, 0, result["errors"])
        self.assertEqual(snapshot(self.mod), before)

    def test_an_animations_block_marked_in_a_file_the_registration_does_not_name_is_refused(self) -> None:
        write(self.mod / "gfx/entities/stray.asset", f"# wire_unit begin {STEM} animations\n# wire_unit end {STEM} animations\n")
        before = snapshot(self.mod)
        code, result = run(self.job, self.mod)
        self.assertEqual(code, 1)
        self.assertTrue(any("animations block" in line and "stray.asset" in line for line in result["errors"]), result["errors"])
        self.assertEqual(snapshot(self.mod), before)

    def test_the_animations_marker_carries_the_job_stem_not_the_asset_file_stem(self) -> None:
        registration = self.job / "runtime" / "registration.md"
        registration.write_text(registration.read_text(encoding="utf-8").replace(f"{FOLDER}/{STEM}.asset", f"{FOLDER}/other_name.asset"), encoding="utf-8")
        code, result = run(self.job, self.mod)
        self.assertEqual(code, 0, result["errors"])
        asset = (self.mod / FOLDER / "other_name.asset").read_text(encoding="utf-8")
        self.assertIn(f"# wire_unit begin {STEM} animations", asset)
        self.assertNotIn("# wire_unit begin other_name animations", asset)
        first = snapshot(self.mod)
        run(self.job, self.mod)
        self.assertEqual(snapshot(self.mod), first)


class StaysInsideTheMod(Fixture):
    def assert_refused(self, *extra: str) -> None:
        before = snapshot(self.mod)
        outside = {path.name for path in self.root.iterdir()}
        code, result = run(self.job, self.mod, *extra)
        self.assertEqual(code, 1)
        self.assertTrue(any("inside the mod" in line or "leaves the mod" in line for line in result["errors"]), result["errors"])
        self.assertEqual(snapshot(self.mod), before)
        self.assertEqual({path.name for path in self.root.iterdir()}, outside)

    def test_a_backslash_traversal_in_gfx_file_is_refused(self) -> None:
        self.assert_refused("--gfx-file", "..\\evil.gfx")

    def test_a_backslash_traversal_in_entity_file_is_refused(self) -> None:
        self.assert_refused("--entity-file", "gfx\\..\\..\\evil.asset")

    def test_an_absolute_or_drive_path_is_refused(self) -> None:
        self.assert_refused("--gfx-file", "C:\\evil.gfx")
        self.assert_refused("--entity-file", "/evil.asset")

    def test_a_model_folder_that_climbs_out_of_the_mod_is_refused(self) -> None:
        registration = self.job / "runtime" / "registration.md"
        registration.write_text(registration.read_text(encoding="utf-8").replace(FOLDER, "..\\evil"), encoding="utf-8")
        self.assert_refused()
        self.assertFalse((self.root / "evil").exists())

    def test_a_symlinked_folder_that_leaves_the_mod_is_refused(self) -> None:
        elsewhere = self.root / "elsewhere"
        elsewhere.mkdir()
        link = self.mod / "gfx" / "linked"
        link.parent.mkdir(parents=True)
        try:
            link.symlink_to(elsewhere, target_is_directory=True)
        except OSError as error:
            self.skipTest(f"no symlinks here: {error}")
        self.assert_refused("--gfx-file", "gfx/linked/evil.gfx")
        self.assertEqual(list(elsewhere.iterdir()), [])

    def test_safe_destination_accepts_a_normal_path_and_normalises_backslashes(self) -> None:
        self.assertEqual(wiring.safe_destination(self.mod, "gfx\\entities\\x.gfx"), "gfx/entities/x.gfx")


class LineEndings(Fixture):
    MIXED = b"\xef\xbb\xbf# top\r\nobjectTypes = {\r\n\tspriteType = { name = \"GFX_a\" }\n\tspriteType = { name = \"GFX_b\" }\r\n\r# lone\r}\r\n# tail\n"

    def test_every_untouched_byte_survives_a_mixed_file(self) -> None:
        path = self.mod / "gfx/entities/ab_units.gfx"
        write(path, self.MIXED)
        code, result = run(self.job, self.mod)
        self.assertEqual(code, 0, result["errors"])
        data = path.read_bytes()
        suffix = b"}\r\n# tail\n"
        prefix = self.MIXED[: -len(suffix)]
        self.assertTrue(data.startswith(prefix))
        self.assertTrue(data.endswith(suffix))
        added = data[len(prefix) : -len(suffix)]
        self.assertIn(b"# wire_unit begin ab_ghoul pdxmesh", added)
        # the file is mostly CRLF, so the new lines are CRLF
        self.assertEqual(added.count(b"\n"), added.count(b"\r\n"))
        first = snapshot(self.mod)
        run(self.job, self.mod)
        self.assertEqual(snapshot(self.mod), first)

    def test_a_block_replaced_in_a_mixed_file_keeps_the_lines_around_it(self) -> None:
        path = self.mod / "gfx/entities/ab_units.asset"
        write(path, b"a = 1\n# b\r\nc = 3\r\n")
        run(self.job, self.mod)
        first = path.read_bytes()
        self.assertTrue(first.startswith(b"a = 1\n# b\r\nc = 3\r\n"))
        registration = self.job / "runtime" / "registration.md"
        registration.write_text(registration.read_text(encoding="utf-8").replace("scale = 0.8", "scale = 0.9"), encoding="utf-8")
        run(self.job, self.mod)
        second = path.read_bytes()
        self.assertTrue(second.startswith(b"a = 1\n# b\r\nc = 3\r\n"))
        self.assertIn(b"scale = 0.9", second)

    def test_a_file_without_a_final_newline_gets_one_before_the_block(self) -> None:
        file = wiring.TextFile.read(self.write_temp(b"a = 1\n# b\n c = 3"))
        out = wiring.upsert_block(file, stem="s", kind="entity", block="x = 1", wrapper="", where="f")
        self.assertEqual(out.encode(), b"a = 1\n# b\n c = 3\n\n# wire_unit begin s entity\nx = 1\n# wire_unit end s entity\n")

    def test_a_lone_cr_is_kept_as_a_line_end(self) -> None:
        file = wiring.TextFile.read(self.write_temp(b"a = 1\rb = 2\r\n"))
        self.assertEqual(file.encode(), b"a = 1\rb = 2\r\n")
        out = wiring.upsert_block(file, stem="s", kind="entity", block="x = 1", wrapper="", where="f")
        self.assertTrue(out.encode().startswith(b"a = 1\rb = 2\r\n"))

    def write_temp(self, data: bytes) -> Path:
        path = self.root / "scratch.txt"
        write(path, data)
        return path


class PdxmeshPlacement(Fixture):
    def test_the_block_goes_inside_objecttypes_not_before_a_later_top_level_brace(self) -> None:
        path = self.mod / "gfx/entities/ab_units.gfx"
        write(path, 'objectTypes = {\n\t# } in a comment\n\tspriteType = { name = "GFX_a" text = "}" }\n}\nother = {\n\tx = 1\n}\n')
        code, result = run(self.job, self.mod)
        self.assertEqual(code, 0, result["errors"])
        text = path.read_text(encoding="utf-8")
        self.assertTrue(text.endswith(f"# wire_unit end {STEM} pdxmesh\n}}\nother = {{\n\tx = 1\n}}\n"), text)
        self.assertLess(text.index("# wire_unit begin"), text.index("}\nother"))

    def test_a_gfx_file_without_objecttypes_is_an_error(self) -> None:
        write(self.mod / "gfx/entities/ab_units.gfx", "other = {\n}\n")
        code, result = run(self.job, self.mod)
        self.assertEqual(code, 1)
        self.assertTrue(any("objectTypes" in line for line in result["errors"]), result["errors"])


class DryRunErrors(Fixture):
    def test_a_dry_run_with_a_missing_sub_unit_fails_with_exit_1(self) -> None:
        mod = make_mod(self.root / "second", subunit=False)
        code, result = run(self.job, mod, "--dry-run")
        self.assertEqual((code, result["verdict"]), (1, "DRY-RUN-FAIL"))

    def test_a_dry_run_with_missing_localisation_fails_with_exit_1(self) -> None:
        mod = make_mod(self.root / "second", localisation=False)
        code, result = run(self.job, mod, "--dry-run")
        self.assertEqual((code, result["verdict"]), (1, "DRY-RUN-FAIL"))

    def test_a_clean_dry_run_still_exits_0(self) -> None:
        code, result = run(self.job, self.mod, "--dry-run")
        self.assertEqual((code, result["verdict"]), (0, "DRY-RUN"))


class BadInputIsNotAFailVerdict(Fixture):
    def exit_code(self) -> tuple:
        err = io.StringIO()
        with redirect_stderr(err), redirect_stdout(io.StringIO()):
            code = wire_unit.main([str(self.job), "--mod-root", str(self.mod)])
        return code, err.getvalue()

    def test_an_invalid_job_yaml_exits_2(self) -> None:
        write(self.job / "job.yaml", "{ this is: [not valid")
        code, message = self.exit_code()
        self.assertEqual(code, 2, message)
        self.assertIn("job.yaml", message)

    def test_a_job_yaml_that_is_not_a_mapping_exits_2(self) -> None:
        write(self.job / "job.yaml", "[1, 2]")
        self.assertEqual(self.exit_code()[0], 2)

    def test_invalid_files_json_exits_2(self) -> None:
        write(self.job / "runtime" / "files.json", "{nope")
        code, message = self.exit_code()
        self.assertEqual(code, 2, message)
        self.assertIn("files.json", message)

    def test_a_registration_that_is_not_utf8_exits_2(self) -> None:
        write(self.job / "runtime" / "registration.md", b"# Registration for x_entity\n\xff\xfe\n")
        code, message = self.exit_code()
        self.assertEqual(code, 2, message)
        self.assertIn("registration.md", message)

    def test_a_failed_import_of_the_kits_checks_exits_2(self) -> None:
        with mock.patch.object(wire_unit, "load_audit_module", side_effect=wiring.WiringError("cannot load the kit's checks")):
            err = io.StringIO()
            with redirect_stderr(err), redirect_stdout(io.StringIO()):
                code = wire_unit.main([str(self.job), "--mod-root", str(self.mod)])
        self.assertEqual(code, 2)

    def test_the_real_loader_turns_an_import_error_into_a_wiring_error(self) -> None:
        import check_unit_files

        with mock.patch.object(check_unit_files, "_registration_audit", side_effect=ImportError("gone")):
            with self.assertRaises(wiring.WiringError):
                wire_unit.load_audit_module()

    def test_nothing_is_written_when_the_input_is_bad(self) -> None:
        write(self.job / "runtime" / "files.json", "{nope")
        before = snapshot(self.mod)
        self.exit_code()
        self.assertEqual(snapshot(self.mod), before)


class AtomicOrderedWrites(Fixture):
    def test_runtime_files_are_copied_before_any_block_is_written(self) -> None:
        order = []
        real = wiring._write_atomically

        def spy(dest: Path, data: bytes) -> None:
            order.append(dest.suffix)
            real(dest, data)

        with mock.patch.object(wiring, "_write_atomically", spy):
            code, _result = run(self.job, self.mod)
        self.assertEqual(code, 0)
        blocks = [index for index, suffix in enumerate(order) if suffix in (".gfx", ".asset")]
        files = [index for index, suffix in enumerate(order) if suffix not in (".gfx", ".asset")]
        self.assertTrue(files and blocks)
        self.assertLess(max(files), min(blocks))
        self.assertEqual(order[-1], ".asset")  # the entity is the last write

    def test_a_failure_while_writing_blocks_leaves_files_but_no_registration(self) -> None:
        real = wiring._write_atomically

        def failing(dest: Path, data: bytes) -> None:
            if dest.suffix == ".gfx":
                raise OSError("disk full")
            real(dest, data)

        err = io.StringIO()
        with mock.patch.object(wiring, "_write_atomically", failing), redirect_stderr(err), redirect_stdout(io.StringIO()):
            code = wire_unit.main([str(self.job), "--mod-root", str(self.mod)])
        self.assertEqual(code, 2)
        self.assertIn("disk full", err.getvalue())
        self.assertTrue((self.mod / FOLDER / f"{STEM}.mesh").is_file())
        self.assertFalse((self.mod / "gfx/entities/ab_units.asset").exists())

    def test_a_failed_replace_keeps_the_old_file_and_leaves_no_temporary_file(self) -> None:
        target = self.mod / "gfx" / "x.gfx"
        write(target, b"old")
        with mock.patch.object(wiring.os, "replace", side_effect=OSError("locked")):
            with self.assertRaises(OSError):
                wiring._write_atomically(target, b"new")
        self.assertEqual(target.read_bytes(), b"old")
        self.assertEqual([path.name for path in target.parent.iterdir()], ["x.gfx"])

    def test_a_write_replaces_the_file_in_one_step(self) -> None:
        target = self.mod / "gfx" / "y.gfx"
        wiring._write_atomically(target, b"first")
        wiring._write_atomically(target, b"second")
        self.assertEqual(target.read_bytes(), b"second")
        self.assertEqual([path.name for path in target.parent.iterdir()], ["y.gfx"])


class ModelFolder(unittest.TestCase):
    def test_a_mesh_path_without_a_folder_gives_an_empty_folder(self) -> None:
        registration = wiring.Registration("x_entity", "x", 'pdxmesh = {\n\tname = "x_mesh"\n\tfile = "x.mesh"\n}', (("x.asset", "animation = {}"),), "entity = {}")
        self.assertEqual(wiring.model_folder(registration), "")

    def test_a_mesh_path_with_a_folder_gives_that_folder(self) -> None:
        registration = wiring.Registration("x_entity", "x", 'pdxmesh = {\n\tfile = "a\\b/x.mesh"\n}', (("a/b/x.asset", "animation = {}"),), "entity = {}")
        self.assertEqual(wiring.model_folder(registration), "a/b")


class SoundEventText(unittest.TestCase):
    def test_quotes_in_a_soundeffect_name_are_escaped(self) -> None:
        entity = 'entity = {\n\tstate = { name = "move" animation = "move" }\n}'
        out = wiring.apply_sound_events(entity, [wiring.SoundEvent("move", 'say "hi"', 3)])
        self.assertIn('soundeffect = "say \\"hi\\""', out)

    def test_a_sound_plan_warns_that_the_time_unit_is_unverified(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            job, mod = make_job(root, sound_plan=[{"role": "move", "soundeffect": "ghoul_step", "frame": 12}]), make_mod(root)
            _code, result = run(job, mod)
            self.assertTrue(any("unverified" in line and "time" in line for line in result["warnings"]), result["warnings"])
            self.assertIn('event = { time = 12 sound = { soundeffect = "ghoul_step" } }', (mod / "gfx/entities/ab_units.asset").read_text(encoding="utf-8"))


class RealChecks(unittest.TestCase):
    """The two real subprocess checks, on a fixture whose mesh is not a mesh: the verdict must be FAIL and the exit code 1."""

    @unittest.skipUnless(wire_unit.game_dir() and wire_unit.game_dir().is_dir(), "the installed game is needed by the static audit")
    def test_the_real_checks_run_and_a_broken_mesh_fails_the_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            job, mod = make_job(root), make_mod(root)
            out = io.StringIO()
            with redirect_stdout(out):
                code = wire_unit.main([str(job), "--mod-root", str(mod), "--json"])
            result = json.loads(out.getvalue())
            self.assertEqual(code, 1)
            self.assertEqual(result["verdict"], "FAIL")
            self.assertIn("check_unit_files", result["checks"])
            self.assertIn("audit", result["checks"])
            self.assertNotIn("unavailable", result["checks"]["audit"])
            self.assertTrue(any(line.startswith("check_unit_files: UNIT-MESH") for line in result["errors"]))


if __name__ == "__main__":
    unittest.main()
