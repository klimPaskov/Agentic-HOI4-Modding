"""The Tripo route's neck rule on a synthetic biped with a chest, a neck, a head and two clavicles: the visible neck, TRIPO-NECK-SUNK and the lift
that fixes it (lib/tripo_neck.py). No Blender."""

from __future__ import annotations

import math
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))
sys.path.insert(0, str(PIPELINE / "tests"))
sys.path.insert(0, str(PIPELINE / "tripo"))

import run_pilot
import test_deformation_checks as TD
import tripo_checks as TC
from lib import pdx_deform, tripo_neck as N, tripo_pose as P

BONES = [
    ("Hips", -1, (0.0, 1.0, 0.0)),
    ("LeftUpLeg", 0, (0.1, 0.95, 0.0)), ("LeftLeg", 1, (0.1, 0.5, 0.0)), ("LeftFoot", 2, (0.1, 0.06, 0.0)), ("LeftToeBase", 3, (0.1, 0.0, -0.1)),
    ("RightUpLeg", 0, (-0.1, 0.95, 0.0)), ("RightLeg", 5, (-0.1, 0.5, 0.0)), ("RightFoot", 6, (-0.1, 0.06, 0.0)), ("RightToeBase", 7, (-0.1, 0.0, -0.1)),
    ("Spine", 0, (0.0, 1.3, 0.0)), ("Spine02", 9, (0.0, 1.5, 0.0)),
    ("neck", 10, (0.0, 1.62, 0.0)), ("Head", 11, (0.0, 1.72, 0.0)),
    ("LeftShoulder", 10, (0.08, 1.58, 0.0)), ("LeftArm", 13, (0.2, 1.56, 0.0)), ("LeftForeArm", 14, (0.2, 1.3, 0.0)),
    ("RightShoulder", 10, (-0.08, 1.58, 0.0)), ("RightArm", 16, (-0.2, 1.56, 0.0)), ("RightForeArm", 17, (-0.2, 1.3, 0.0)),
]
IDENTITY = np.array([0.0, 0.0, 0.0, 1.0])


def about(axis: int, degrees: float):
    half = math.radians(degrees) / 2.0
    q = [0.0, 0.0, 0.0, math.cos(half)]
    q[axis] = math.sin(half)
    return tuple(q)


def local(name: str):
    index = [b[0] for b in BONES].index(name)
    parent = BONES[index][1]
    base = BONES[parent][2] if parent >= 0 else (0.0, 0.0, 0.0)
    return tuple(BONES[index][2][i] - base[i] for i in range(3))


def pitched(degrees: float) -> dict:
    """The neck turned forward and down by `degrees`."""

    return {"neck": (local("neck"), about(0, degrees))}


def shrugged(degrees: float) -> dict:
    """Both clavicles turned up by `degrees`, so the upper-arm joints rise."""

    return {"LeftShoulder": (local("LeftShoulder"), about(2, degrees)), "RightShoulder": (local("RightShoulder"), about(2, -degrees))}


class Unit(unittest.TestCase):
    def setUp(self) -> None:
        self.saved = list(TD.BONES)
        TD.BONES[:] = BONES
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.addCleanup(lambda: TD.BONES.__setitem__(slice(None), self.saved))
        self.folder = Path(temp.name)
        self.mesh_path = self.folder / "unit.mesh"
        positions, triangles, owner = [], [], []
        for index, (_name, _parent, (x, y, z)) in enumerate(BONES):
            base = len(positions)
            points, tris = TD.tetrahedron((x, y, z), 0.03)
            positions += points
            triangles += [tuple(base + i for i in tri) for tri in tris]
            owner += [index] * 4
        TD.write_mesh(self.mesh_path, positions, triangles, owner)
        self.mesh = pdx_deform.load_mesh(self.mesh_path)

    def clip(self, role: str, frames: int, pose) -> Path:
        path = self.folder / f"unit_{role}.anim"
        TD.write_anim(path, frames, pose)
        return path

    def neck(self, path: Path) -> np.ndarray:
        return N.visible_neck(self.mesh, pdx_deform.load_anim(path))


class Measure(Unit):
    def test_the_rig_is_found_by_its_names_and_its_parents(self) -> None:
        rig = N.neck_rig(self.mesh)
        bones = self.mesh.bones
        self.assertEqual(bones[rig.chest], "Spine02")
        self.assertEqual(bones[rig.head], "Head")
        self.assertEqual([bones[j] for j in rig.neck], ["neck"])
        self.assertEqual(sorted(bones[j] for j in rig.clavicles), ["LeftShoulder", "RightShoulder"])

    def test_the_rest_pose_keeps_its_whole_neck_and_a_leaning_torso_does_not_shorten_it(self) -> None:
        still = self.neck(self.clip("idle", 4, lambda f: {}))
        self.assertTrue(np.allclose(still, 1.0, atol=1e-6))
        leaning = self.neck(self.clip("move", 4, lambda f: {"Spine": (local("Spine"), about(0, 50.0))}))
        self.assertTrue(np.allclose(leaning, 1.0, atol=1e-6))

    def test_a_pitched_neck_and_a_shrug_each_shorten_it(self) -> None:
        # head joint 0.1 above the neck joint, 0.16 above the shoulder line at rest
        neck = self.neck(self.clip("attack", 3, lambda f: pitched(60.0)))
        self.assertAlmostEqual(float(neck[0]), (0.16 - 0.1 * (1 - math.cos(math.radians(60)))) / 0.16, places=3)
        shrug = self.neck(self.clip("defend", 3, lambda f: shrugged(30.0)))
        rise = 0.12 * math.sin(math.radians(30)) - 0.02 * math.cos(math.radians(30)) + 0.02
        self.assertAlmostEqual(float(shrug[0]), (0.16 - rise) / 0.16, places=3)

    def test_the_parts_name_the_head_drop_and_the_shoulder_rise(self) -> None:
        parts = N.neck_parts(self.mesh, pdx_deform.load_anim(self.clip("attack", 2, lambda f: pitched(60.0))))
        self.assertGreater(parts.head_drop[0], 0.02)
        self.assertAlmostEqual(float(parts.shoulder_rise[0]), 0.0, places=6)
        parts = N.neck_parts(self.mesh, pdx_deform.load_anim(self.clip("defend", 2, lambda f: shrugged(30.0))))
        self.assertGreater(parts.shoulder_rise[0], 0.02)
        self.assertAlmostEqual(float(parts.head_drop[0]), 0.0, places=6)

    def test_a_body_without_a_head_has_no_measure(self) -> None:
        self.mesh.bones[self.mesh.bones.index("Head")] = "Skull"
        self.assertIsNone(N.neck_rig(self.mesh))
        self.assertEqual(N.neck_findings(self.mesh, {})[0], [])


class Check(Unit):
    def test_the_limit_comes_from_vanilla_with_a_quarter_added_to_its_shrink(self) -> None:
        self.assertAlmostEqual(N.NECK_LIMIT, 1.0 - 1.25 * (1.0 - N.VANILLA_NECK_WORST), places=2)
        self.assertLess(N.NECK_LIMIT, N.VANILLA_NECK_WORST)
        self.assertEqual(N.NECK_TARGET, N.VANILLA_NECK_WORST)
        self.assertEqual(min(N.VANILLA_NECK_WORST_BY_ROLE.values()), N.VANILLA_NECK_WORST)

    def test_a_sunk_head_fails_and_names_its_worst_frame_and_a_nod_passes(self) -> None:
        sunk = pdx_deform.load_anim(self.clip("attack", 10, lambda f: pitched(40.0 + 5.0 * f)))
        nod = pdx_deform.load_anim(self.clip("idle", 10, lambda f: pitched(30.0)))
        found, numbers = N.neck_findings(self.mesh, {"unit_attack": sunk, "unit_idle": nod})
        self.assertEqual([(item["rule"], item["subject"], item["frame"]) for item in found], [("TRIPO-NECK-SUNK", "unit_attack", 9)])
        self.assertGreaterEqual(numbers["unit_idle"]["lowest_neck_share"], N.NECK_LIMIT)
        self.assertGreater(numbers["unit_attack"]["frames_under_limit"], 0)

    def test_the_unit_checks_run_it_for_a_humanoid(self) -> None:
        anims = {"unit_death": pdx_deform.load_anim(self.clip("death", 6, lambda f: pitched(80.0)))}
        numbers: dict = {}
        found = TC.body_findings(self.mesh, anims, numbers)
        self.assertIn("TRIPO-NECK-SUNK", [item["rule"] for item in found])
        self.assertIn("unit_death", numbers["neck"])


class Lift(Unit):
    def test_a_clip_above_the_limit_is_copied_byte_for_byte(self) -> None:
        path = self.clip("attack", 8, lambda f: pitched(30.0))
        before = path.read_bytes()
        out = self.folder / "out.anim"
        lift = N.lift_neck(self.mesh_path, path, out, "attack")
        self.assertFalse(lift.changed)
        self.assertEqual(out.read_bytes(), before)

    def test_a_looping_attack_gets_its_neck_lifted_by_one_share_and_keeps_its_seam(self) -> None:
        path = self.clip("attack", 21, lambda f: pitched(70.0 + 10.0 * math.sin(math.pi * f / 20)))
        anim = pdx_deform.load_anim(path)
        seam = P.loop_seam(self.mesh, anim)[0]
        lift = N.lift_neck(self.mesh_path, path, path, "attack")
        self.assertTrue(lift.changed)
        self.assertEqual(lift.group, "neck")
        self.assertLess(lift.neck_before, N.NECK_LIMIT)
        self.assertGreaterEqual(lift.neck_after, N.NECK_TARGET - 1e-6)
        after = pdx_deform.load_anim(path)
        self.assertGreaterEqual(float(N.visible_neck(self.mesh, after).min()), N.NECK_TARGET - 1e-6)
        self.assertLessEqual(P.loop_seam(self.mesh, after)[0], seam + 1e-3)
        self.assertEqual(lift.frames_changed, 21)
        # only the neck's rotations change, and by the same share in every frame
        for joint in self.mesh.bones:
            if joint != "neck":
                self.assertTrue(np.allclose(anim.channels[joint]["q"], after.channels[joint]["q"]))
        turns = [P.quaternion_turn(q, IDENTITY) / P.quaternion_turn(p, IDENTITY) for p, q in zip(anim.channels["neck"]["q"], after.channels["neck"]["q"])]
        self.assertTrue(np.allclose(turns, 1.0 - lift.share, atol=1e-3))

    def test_a_shrug_lowers_the_clavicles_not_the_neck(self) -> None:
        path = self.clip("defend", 8, lambda f: shrugged(35.0))
        lift = N.lift_neck(self.mesh_path, path, path, "defend")
        self.assertTrue(lift.changed)
        self.assertEqual(lift.group, "clavicles")
        self.assertEqual(sorted(lift.joints), ["LeftShoulder", "RightShoulder"])
        self.assertGreaterEqual(lift.neck_after, N.NECK_TARGET - 1e-6)
        self.assertFalse(lift.tried["neck"]["reaches_target"])

    def test_a_death_gets_each_frames_own_share_ramped_in_and_out(self) -> None:
        def pose(f):
            return pitched(85.0 * math.exp(-((f - 20) / 4.0) ** 2))

        path = self.clip("death", 41, pose)
        anim = pdx_deform.load_anim(path)
        lift = N.lift_neck(self.mesh_path, path, path, "death")
        after = pdx_deform.load_anim(path)
        self.assertTrue(lift.changed)
        self.assertGreaterEqual(float(N.visible_neck(self.mesh, after).min()), N.NECK_TARGET - 1e-6)
        self.assertGreaterEqual(lift.ramp_frames, N.LIFT_MIN_RAMP_FRAMES)
        self.assertLess(lift.frames_changed, 41)
        # the start and the lying end are as they were
        for frame in (0, 1, 39, 40):
            self.assertTrue(np.allclose(anim.channels["neck"]["q"][frame], after.channels["neck"]["q"][frame]))

    def test_spread_shares_holds_a_loop_and_ramps_a_death(self) -> None:
        needed = np.array([0.0, 0.0, 0.0, 0.0, 0.6, 0.0, 0.0, 0.0, 0.0, 0.0])
        self.assertTrue(np.allclose(N.spread_shares(needed, 4, loop=True), 0.6))
        spread = N.spread_shares(needed, 4, loop=False)
        self.assertTrue(np.all(spread >= needed))
        self.assertEqual(spread[0], 0.0)
        self.assertLessEqual(float(np.abs(np.diff(spread)).max()), 0.6 * 1.5 / 4 + 1e-9)
        self.assertEqual(float(N.spread_shares(np.array([0.2, np.inf]), 1, loop=True)[0]), 1.0)

    def test_run_pilot_records_the_lift(self) -> None:
        path = self.clip("attack", 6, lambda f: pitched(80.0))
        record = run_pilot.lift_sunk_neck(self.mesh_path, path, "attack")
        self.assertTrue(record["changed"])
        self.assertEqual(record["joints"], ["neck"])
        self.assertGreaterEqual(record["neck_after"], round(N.NECK_TARGET, 3) - 1e-3)
        self.assertEqual(N.neck_findings(self.mesh, {"unit_attack": pdx_deform.load_anim(path)})[0], [])


if __name__ == "__main__":
    unittest.main()
