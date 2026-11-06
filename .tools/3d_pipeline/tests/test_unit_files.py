"""The unit-file checker, the PDX reader, the DXT5 writer and the unit-type catalog."""

from __future__ import annotations

import io
import json
import struct
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))

import numpy as np  # noqa: E402
from PIL import Image  # noqa: E402

import check_unit_files  # noqa: E402
from lib import model_dds, pdx_binary  # noqa: E402

LAND_ROLES = {"idle", "move", "attack", "defend", "retreat", "death"}


def _prop(name: str, kind: str, values: list) -> bytes:
    data = b"!" + struct.pack("<B", len(name)) + name.encode("latin-1") + kind.encode() + struct.pack("<i", len(values))
    if kind == "i":
        return data + struct.pack(f"<{len(values)}i", *values)
    if kind == "f":
        return data + struct.pack(f"<{len(values)}f", *values)
    for value in values:
        encoded = value.encode("latin-1") + b"\0"
        data += struct.pack("<i", len(encoded)) + encoded
    return data


def _obj(name: str, depth: int) -> bytes:
    return b"[" * depth + name.encode("latin-1") + b"\0"


def write_mesh(path: Path, bones: list[str], influences: int = 4, triangles: int = 2, tx: dict | None = None) -> None:
    data = b"@@b@" + _obj("object", 1) + _obj("unit_shape", 2) + _obj("mesh", 3)
    vertices = triangles + 2
    data += _prop("p", "f", [0.0] * (3 * vertices))
    data += _prop("tri", "i", [index for t in range(triangles) for index in (0, t + 1, t + 2)])
    data += _obj("material", 4) + _prop("shader", "s", ["PdxMeshAdvanced"]) + _prop("diff", "s", ["unit_diffuse.dds"])
    if bones:
        data += _obj("skin", 4) + _prop("bones", "i", [influences])
        data += _obj("skeleton", 3)
        for index, bone in enumerate(bones):
            data += _obj(bone, 4) + _prop("ix", "i", [index])
            if tx and bone in tx:
                data += _prop("tx", "f", tx[bone])
    path.write_bytes(data)


def write_anim(path: Path, joints: list[str], animated: bool = True, fps: float = 30.0, samples: int = 24) -> None:
    data = b"@@b@" + _obj("info", 1) + _prop("fps", "f", [fps]) + _prop("sa", "i", [samples]) + _prop("j", "i", [len(joints)])
    for joint in joints:
        data += _obj(joint, 2) + _prop("sa", "s", ["q" if animated else ""])
    path.write_bytes(data)


def write_bgra_dds(path: Path, image: Image.Image) -> None:
    rgba = image.convert("RGBA")
    width, height = rgba.size
    bgra = np.asarray(rgba)[..., [2, 1, 0, 3]].tobytes()
    header = struct.pack(
        "<4sIIIIIII44sIIIIIIIIIIIII", b"DDS ", 124, 0x100F, height, width, width * 4, 0, 1, b"\0" * 44,
        32, 0x41, 0, 32, 0x00FF0000, 0x0000FF00, 0x000000FF, 0xFF000000, 0x1000, 0, 0, 0, 0,
    )
    path.write_bytes(header + bgra)


class PdxReader(unittest.TestCase):
    def test_mesh_and_anim_summaries(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            mesh = Path(folder) / "u.mesh"
            write_mesh(mesh, ["Hips", "Spine"], triangles=3)
            summary = pdx_binary.summarize_mesh(pdx_binary.read(mesh))
            self.assertEqual(summary.bones, ["Hips", "Spine"])
            self.assertEqual(summary.triangles, 3)
            self.assertEqual(summary.streams[0].influences_per_vertex, 4)
            self.assertEqual(summary.streams[0].textures, {"diff": "unit_diffuse.dds"})
            anim = Path(folder) / "u_idle.anim"
            write_anim(anim, ["Hips", "Spine"], fps=24.0, samples=48)
            parsed = pdx_binary.summarize_anim(pdx_binary.read(anim))
            self.assertEqual((parsed.fps, parsed.samples, parsed.joints), (24.0, 48, ["Hips", "Spine"]))
            self.assertAlmostEqual(parsed.seconds, 2.0)

    def test_rejects_other_files(self) -> None:
        with self.assertRaises(pdx_binary.PdxFormatError):
            pdx_binary.parse(b"DDS \0\0\0\0")
        with self.assertRaises(pdx_binary.PdxFormatError):
            pdx_binary.parse(b"@@b@!\x01p" + b"q")


class ModelDds(unittest.TestCase):
    def test_dxt5_has_a_full_chain_and_decodes_like_pillow(self) -> None:
        gradient = np.zeros((64, 32, 4), dtype=np.uint8)
        gradient[..., 0] = np.linspace(0, 255, 32, dtype=np.uint8)[None, :]
        gradient[..., 1] = np.linspace(255, 0, 64, dtype=np.uint8)[:, None]
        gradient[..., 3] = 200
        data = model_dds.dxt5_bytes(Image.fromarray(gradient, "RGBA"))
        header = model_dds.read_header(data)
        self.assertEqual((header["width"], header["height"], header["mips"], header["format"]), (32, 64, 7, "DXT5"))
        mine = model_dds.decode_top_level(data).astype(int)
        self.assertLess(np.abs(mine - gradient.astype(int)).max(), 24)
        theirs = np.asarray(Image.open(io.BytesIO(data)).convert("RGBA"), dtype=int)
        self.assertLessEqual(np.abs(mine - theirs).max(), 1)

    def test_refuses_sizes_that_are_not_powers_of_two(self) -> None:
        with self.assertRaises(model_dds.DdsError):
            model_dds.dxt5_bytes(Image.new("RGBA", (24, 16)))


class CheckUnitFiles(unittest.TestCase):
    def run_check(self, folder: Path, unit_type: str) -> list:
        types = check_unit_files.load_unit_types()
        profile = check_unit_files.load_profile(types[unit_type]["profile"])
        findings, _facts = check_unit_files.check_files(folder, types[unit_type], profile)
        return findings

    def test_a_complete_unit_passes(self) -> None:
        bones = ["Hips", "Spine", "Head"]
        with tempfile.TemporaryDirectory() as name:
            folder = Path(name)
            write_mesh(folder / "unit.mesh", bones)
            for role in LAND_ROLES:
                write_anim(folder / f"unit_{role}.anim", bones)
            self.assertEqual([item.rule for item in self.run_check(folder, "infantry_melee") if item.severity == "error"], [])

    def test_a_soldiers_clip_must_play_at_30_a_vehicles_need_not(self) -> None:
        # A Blender scene from factory settings runs at 24, and io_pdx_mesh writes the scene's rate.
        bones = ["Hips", "Spine", "Head"]
        with tempfile.TemporaryDirectory() as name:
            folder = Path(name)
            write_mesh(folder / "unit.mesh", bones)
            for role in LAND_ROLES:
                write_anim(folder / f"unit_{role}.anim", bones, fps=24.0 if role == "attack" else 30.0)
            errors = [item for item in self.run_check(folder, "infantry_melee") if item.severity == "error"]
            self.assertEqual([(item.rule, Path(item.file).name) for item in errors], [("UNIT-ANIM-FPS", "unit_attack.anim")])
            self.assertIn("plays at 24", errors[0].message)
            found = []
            vehicle = {"calibration_group": "vehicle", "roles": {}}
            check_unit_files._check_animations(folder, "unit", vehicle, bones, lambda *item: found.append(item), {"animations": {}})
            self.assertEqual(found, [])

    def test_engine_limits_and_missing_roles(self) -> None:
        bones = [f"Bone_{index}" for index in range(51)]
        with tempfile.TemporaryDirectory() as name:
            folder = Path(name)
            write_mesh(folder / "unit.mesh", bones, influences=5)
            write_anim(folder / "unit_idle.anim", bones + ["Tail"])
            write_anim(folder / "unit_move.anim", bones, animated=False)
            rules = {item.rule for item in self.run_check(folder, "mount")}
        self.assertTrue({"UNIT-BONES", "UNIT-INFLUENCES", "UNIT-ANIM-JOINTS", "UNIT-ANIM-STATIC", "UNIT-ROLE-MISSING", "UNIT-NODE-MISSING"} <= rules)

    def test_a_rotated_attach_node_is_refused(self) -> None:
        identity = [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, -5.0, 0.0]
        turned = [1.0, 0.0, 0.0, 0.0, 0.0, -1.0, 0.0, 1.0, 0.0, 0.0, -5.0, 0.0]
        for matrix, expected in ((identity, False), (turned, True)):
            with tempfile.TemporaryDirectory() as name:
                folder = Path(name)
                write_mesh(folder / "unit.mesh", ["Root", "Saddle_Node"], tx={"Saddle_Node": matrix})
                rules = {item.rule for item in self.run_check(folder, "mount")}
                self.assertEqual("UNIT-NODE-ORIENTATION" in rules, expected)

    def test_a_mount_and_its_rider_share_a_folder(self) -> None:
        identity = [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, -5.0, 0.0]
        horse, rider = ["Root", "Spine", "Saddle_Node"], ["Hips", "Spine01", "Head"]
        types = check_unit_files.load_unit_types()
        with tempfile.TemporaryDirectory() as name:
            folder = Path(name)
            write_mesh(folder / "knights.mesh", horse, tx={"Saddle_Node": identity})
            write_mesh(folder / "knights_rider.mesh", rider)
            for role in LAND_ROLES:
                write_anim(folder / f"knights_{role}.anim", horse)
                write_anim(folder / f"knights_rider_{role}.anim", rider)
            for stem, unit_type in (("knights", "mount"), ("knights_rider", "rider")):
                findings, facts = check_unit_files.check_files(folder, types[unit_type], None, stem)
                self.assertEqual([item.rule for item in findings if item.severity == "error"], [], stem)
                self.assertEqual(list(facts["meshes"]), [f"{stem}.mesh"])
                self.assertEqual(len(facts["animations"]), len(LAND_ROLES))
            unscoped = {item.rule for item in check_unit_files.check_files(folder, types["mount"], None)[0]}
            self.assertIn("UNIT-NODE-MISSING", unscoped)

    def test_texture_warnings_and_repair(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            folder = Path(name)
            write_mesh(folder / "unit.mesh", [])
            normal = Image.new("RGBA", (16, 16), (0, 128, 40, 128))
            write_bgra_dds(folder / "unit_normal.dds", normal)
            rules = {item.rule for item in check_unit_files.check_files(folder, None, None)[0]}
            self.assertTrue({"UNIT-DDS-MIPS", "UNIT-DDS-FORMAT", "UNIT-DDS-EMISSIVE"} <= rules)
            self.assertEqual(check_unit_files.repair_textures(folder), ["unit_normal.dds"])
            rules = {item.rule for item in check_unit_files.check_files(folder, None, None)[0]}
            self.assertFalse({"UNIT-DDS-MIPS", "UNIT-DDS-FORMAT", "UNIT-DDS-EMISSIVE"} & rules)
            self.assertEqual(check_unit_files.repair_textures(folder), [])

    def test_command_line_exit_code(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            with redirect_stdout(io.StringIO()):
                self.assertEqual(check_unit_files.main([name]), 1)


class RegistrationAuditFallback(unittest.TestCase):
    def test_a_mod_with_an_older_audit_gets_a_warning_not_a_crash(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            mod = Path(folder)
            unit = mod / "gfx" / "models" / "units" / "u"
            unit.mkdir(parents=True)
            write_mesh(unit / "u.mesh", ["Hips"])
            (mod / ".tools" / "audits").mkdir(parents=True)
            older_audit = "def _files(root, folder):\n    return []\n"
            (mod / ".tools" / "audits" / "audit_asset_wiring_static.py").write_text(older_audit, encoding="utf-8")
            original = check_unit_files.REPO_ROOT
            check_unit_files.REPO_ROOT = mod
            try:
                findings = check_unit_files.check_unit_registration(unit, mod, None)
            finally:
                check_unit_files.REPO_ROOT = original
                sys.modules.pop("audit_asset_wiring_static", None)
        self.assertEqual([(item.rule, item.severity) for item in findings], [("UNIT-REG-UNAVAILABLE", "warning")])
        self.assertIn("ModelLookup", findings[0].message)


class UnitTypeCatalog(unittest.TestCase):
    def test_every_type_is_complete(self) -> None:
        types = check_unit_files.load_unit_types()
        profiles = json.loads((PIPELINE / "config" / "asset_profiles.json").read_text(encoding="utf-8"))["profiles"]
        for name, unit_type in types.items():
            with self.subTest(unit_type=name):
                self.assertIn(unit_type["profile"], profiles)
                self.assertEqual(set(unit_type["roles"]), LAND_ROLES)
                for role in unit_type["roles"].values():
                    self.assertTrue(role.get("meshy") or role.get("blender"))
                    for clip in role.get("meshy", []):
                        self.assertIsInstance(clip[0], int)
                        self.assertIsInstance(clip[1], str)
                    if unit_type["rig"] != "meshy_humanoid":
                        self.assertNotIn("meshy", role)
        self.assertIn("Saddle_Node", types["mount"]["required_nodes"])
        self.assertEqual(types["vehicle"]["calibration_group"], "vehicle")


class UnitTypeValidation(unittest.TestCase):
    def test_overrides_are_measured_and_stay_with_their_type(self) -> None:
        import run_pilot

        types = check_unit_files.load_unit_types()
        for name, unit_type in types.items():
            if unit_type.get("validation_overrides"):
                with self.subTest(unit_type=name):
                    self.assertIn("measured", unit_type.get("validation_calibration", ""))
        tree = run_pilot.apply_unit_type({"unit_type": "tree_creature"})
        self.assertEqual(tree["profile_validation_overrides"], {"max_boundary_edges": 1250})
        self.assertNotIn("profile_validation_overrides", run_pilot.apply_unit_type({"unit_type": "archer"}))


class UnitTypeActions(unittest.TestCase):
    def test_rider_pays_once_per_clip_and_seats_its_death(self) -> None:
        import run_pilot

        spec = run_pilot.apply_unit_type({"unit_type": "rider"})
        by_role = {row["role"]: row for row in spec["required_actions"]}
        self.assertEqual(spec["asset_kind"], "humanoid")
        self.assertEqual(run_pilot.provider_animated_roles(spec), ["idle", "attack", "defend"])
        self.assertEqual((by_role["move"]["task_type"], by_role["move"]["reuse_role"]), ("reused_clip", "idle"))
        self.assertTrue(by_role["death"]["slump"])

    def test_mount_is_a_blender_quadruped(self) -> None:
        import run_pilot

        spec = run_pilot.apply_unit_type({"unit_type": "mount"})
        self.assertEqual((spec["asset_kind"], spec["creature_rig_family"]), ("creature", "quadruped"))
        self.assertEqual(run_pilot.provider_animated_roles(spec), [])
        self.assertEqual({row["action_style"] for row in spec["required_actions"]} - {None}, {
            "quadruped_idle", "quadruped_trot", "quadruped_charge", "quadruped_rear", "quadruped_gallop", "quadruped_collapse"})

    def test_mounts_plan_a_paid_remesh_and_humanoids_defer_raw_topology(self) -> None:
        import run_pilot

        mount = run_pilot.prepare_spec({"unit_type": "mount", "asset_id": "x.mount", "runtime_stem": "mount"}, require_budget=False)
        self.assertEqual([row["operation"] for row in run_pilot.planned_stages(mount)], ["image_to_3d", "remesh"])
        self.assertTrue(run_pilot.route_remeshes(mount))
        rider = run_pilot.prepare_spec({"unit_type": "rider", "asset_id": "x.rider", "runtime_stem": "rider"}, require_budget=False)
        self.assertTrue(run_pilot.route_remeshes(rider))
        self.assertEqual([row["role"] for row in run_pilot.planned_stages(rider) if row["operation"] == "animation"], ["idle", "attack", "defend"])

    def test_job_actions_win_and_unknown_types_fail(self) -> None:
        import run_pilot

        own = [{"role": "idle", "provider_action_id": 0}]
        self.assertEqual(run_pilot.apply_unit_type({"unit_type": "archer", "required_actions": own})["required_actions"], own)
        with self.assertRaises(ValueError):
            run_pilot.apply_unit_type({"unit_type": "dragon_knight"})


class JobStatus(unittest.TestCase):
    def test_status_names_the_next_command(self) -> None:
        import run_pilot

        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            original = run_pilot.resolve_job_root
            run_pilot.resolve_job_root = lambda slug: root / slug
            try:
                fresh = run_pilot.job_status("unit_a", {"unit_type": "archer"}, Path("docs/plans/x/3d_jobs.json"))
                self.assertEqual(fresh["state"], "not_initialized")
                self.assertIn("init_pilot_jobs.py", fresh["next"])
                job = root / "unit_b"
                (job / "provider" / "submissions").mkdir(parents=True)
                (job / "validation").mkdir()
                (job / "job.yaml").write_text(json.dumps({"status": "provider_running"}), encoding="utf-8")
                (job / "validation" / "reference_preflight.json").write_text(json.dumps({"status": "passed"}), encoding="utf-8")
                (job / "provider" / "submissions" / "rig.json").write_text(json.dumps({"state": "uncertain"}), encoding="utf-8")
                stuck = run_pilot.job_status("unit_b", {}, Path("jobs.json"))
                self.assertIn("Reconcile", stuck["next"])
            finally:
                run_pilot.resolve_job_root = original


class RetiredClip(unittest.TestCase):
    def test_a_refused_clip_falls_back_and_stays_skipped(self) -> None:
        import run_pilot
        from lib.mcp_stdio import MCPRouteError

        submitted, reconciled = [], []

        def provider_task(client, job, stage, *, request, **_kwargs):
            submitted.append(request.action_id)
            if request.action_id == 674:
                raise MCPRouteError("Meshy refused the request: Error: Invalid request. This animation is no longer available.")
            return f"task-{request.action_id}"

        class Request:
            def __init__(self, action_id: int) -> None:
                self.action_id, self.fingerprint = action_id, f"fp-{action_id}"

        patches = {
            "provider_task": provider_task,
            "paid_request": lambda spec, kind, tool, arguments, role: Request(arguments["action_id"]),
            "unreconciled_submissions": lambda jobs, fingerprint: [{"file": fingerprint}],
            "reconcile_submission": lambda file, note: reconciled.append(file),
        }
        originals = {name: getattr(run_pilot, name) for name in patches}
        try:
            for name, value in patches.items():
                setattr(run_pilot, name, value)
            with tempfile.TemporaryDirectory() as name:
                job = Path(name)
                spec = {"animation_estimate_credits": 3}
                action = {"role": "retreat", "provider_action_id": 674, "library_key": "Stumble_Walk_inplace",
                          "library_candidates": [[674, "Stumble_Walk_inplace"], [637, "Injured_Walk_inplace"]]}
                task = run_pilot.animate_library_clip(None, job, spec, action, "animation_retreat", "rig", "rig-1")
                self.assertEqual((task, action["provider_action_id"], action["library_key"]), ("task-637", 637, "Injured_Walk_inplace"))
                self.assertEqual((submitted, reconciled), ([674, 637], ["fp-674"]))
                resumed = dict(action, provider_action_id=674)
                run_pilot.animate_library_clip(None, job, spec, resumed, "animation_retreat", "rig", "rig-1")
                self.assertEqual(submitted[2:], [637])
                with self.assertRaises(MCPRouteError):
                    run_pilot.animate_library_clip(None, job, spec, dict(action, library_candidates=[[674, "x"]], provider_action_id=674), "other", "rig", "rig-1")
        finally:
            for name, value in originals.items():
                setattr(run_pilot, name, value)


if __name__ == "__main__":
    unittest.main()
