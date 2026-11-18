"""A death's wings never hold the body up (lib/tripo_chain_lift.py): the ground pass and the fall leave the wing chains out, and a wing
under the ground is turned up about its root. A synthetic winged biped. No Blender."""

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

import run_pilot
import test_deformation_checks as TD
from lib import pdx_deform, pdx_motion, tripo_chain_lift as L, tripo_trim
from test_tripo_pose_upper import BONES as BIPED, turn

# The biped of test_tripo_pose_upper without its weapon, and a wing on each side: two chains that grow from one point on the upper spine.
WINGS = []
for side, sign in (("L", -1.0), ("R", 1.0)):
    spine = [name for name, _p, _x in BIPED].index("Spine02")
    for chain, drop in ((1, 0.0), (2, 0.1)):
        first = len(BIPED) - 1 + len(WINGS)  # the weapon is left out
        WINGS += [(f"Wing{side}{chain}_1", spine, (sign * 0.13, 0.85, -0.05)),
                  (f"Wing{side}{chain}_2", first, (sign * 0.6, 0.85 - drop, -0.05))]
BONES = [bone for bone in BIPED if bone[0] != "Weapon"] + WINGS
NAMES = [name for name, _parent, _position in BONES]
TIP = 1.1  # the wing tips' distance out from the mid-plane


def local(name: str):
    index = NAMES.index(name)
    parent = BONES[index][1]
    base = BONES[parent][2] if parent >= 0 else (0.0, 0.0, 0.0)
    return tuple(BONES[index][2][i] - base[i] for i in range(3))


class WingedBiped(unittest.TestCase):
    def setUp(self) -> None:
        saved = list(TD.BONES)
        TD.BONES[:] = BONES
        self.addCleanup(lambda: TD.BONES.__setitem__(slice(None), saved))
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.folder = Path(temp.name)
        self.mesh_path = self.folder / "unit.mesh"
        positions, triangles, owner = [], [], []
        points = [(index, position) for index, (_n, _p, position) in enumerate(BONES)]
        points += [(NAMES.index(f"Wing{s}{c}_2"), ((-1.0 if s == "L" else 1.0) * TIP, 0.85 - 0.1 * (c - 1), -0.05)) for s in "LR" for c in (1, 2)]
        for index, position in points:
            corners, tris = TD.tetrahedron(position, 0.05)
            triangles += [tuple(len(positions) + i for i in tri) for tri in tris]
            positions += corners
            owner += [index] * 4
        TD.write_mesh(self.mesh_path, positions, triangles, owner)
        self.mesh = pdx_deform.load_mesh(self.mesh_path)

    def death(self, droop: float, frames: int = 30) -> Path:
        """Standing still, each wing turned down `droop` degrees about the front axis at its root from frame 10 on (ramped over 5 frames)."""

        def pose(frame: int):
            share = min(1.0, max(0.0, (frame - 10) / 5.0))
            out = {}
            for side, sign in (("L", 1.0), ("R", -1.0)):
                for chain in (1, 2):
                    name = f"Wing{side}{chain}_1"
                    out[name] = (local(name), turn("z", sign * droop * share))
            return out

        path = self.folder / "unit_death.anim"
        TD.write_anim(path, frames, pose)
        return path

    def wing_low(self, path: Path) -> np.ndarray:
        anim = pdx_deform.load_anim(path)
        mask = np.isin(pdx_deform.dominant_bones(self.mesh), [NAMES.index(n) for n in L.chain_bones(self.mesh)])
        matrices = pdx_deform.skinning_matrices(self.mesh, anim)
        ground = float(self.mesh.positions[:, 1].min())
        return np.array([float(pdx_deform.skin(self.mesh, matrices[f])[mask, 1].min()) - ground for f in range(anim.frames)])

    def hips(self, path: Path) -> np.ndarray:
        anim = pdx_deform.load_anim(path)
        return pdx_motion.posed_joints(self.mesh, anim)[:, NAMES.index("Hips"), 1]


class RootGroups(WingedBiped):
    def test_the_chains_that_grow_from_one_point_are_one_wing(self) -> None:
        groups = L.root_groups(self.mesh, L.chain_bones(self.mesh))
        self.assertEqual(sorted(sorted(self.mesh.bones[j] for j in g) for g in groups), [["WingL1_1", "WingL2_1"], ["WingR1_1", "WingR2_1"]])

    def test_a_cloak_is_not_lifted(self) -> None:
        self.assertTrue(all(name.startswith("Wing") for name in L.chain_bones(self.mesh)))


class RampedNeed(unittest.TestCase):
    def test_the_lift_never_falls_short_and_changes_at_the_settle_rate(self) -> None:
        need = np.array([0.0, 0.0, 0.0, 30.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        ramped = L.ramped_need(need)
        self.assertTrue(np.all(ramped >= need))
        self.assertLessEqual(float(np.abs(np.diff(ramped)).max()), tripo_trim.SETTLE_MAX_RATE + 1e-9)
        self.assertEqual(float(ramped[0]), 0.0)

    def test_the_smallest_lift_brings_every_point_to_the_floor(self) -> None:
        points = np.array([[-1.0, -0.2, 0.0], [-0.5, 0.1, 0.0]])
        degrees = L.smallest_lift(points, np.zeros(3), np.array([0.0, 0.0, -1.0]), 0.0)
        self.assertGreater(degrees, 0.0)
        self.assertAlmostEqual(degrees, math.ceil(math.degrees(math.atan2(0.2, 1.0))), delta=1.0)


class DeathLift(WingedBiped):
    def test_a_wing_under_the_ground_is_turned_up_and_the_body_stays_down(self) -> None:
        path = self.death(droop=75.0)
        self.assertLess(float(self.wing_low(path).min()), -0.1 * self.mesh.height)  # the drooped wing reaches under the ground
        hips_before = self.hips(path)
        record = run_pilot.ground_exported_clip(self.mesh_path, path, "death", None)
        self.assertTrue(record["chain_lift"]["changed"], record)
        np.testing.assert_allclose(self.hips(path), hips_before, atol=1e-4)  # the wing did not lift the body
        self.assertGreaterEqual(float(self.wing_low(path).min()), -0.003 * self.mesh.height)

    def test_without_the_rule_the_ground_pass_would_have_lifted_the_body(self) -> None:
        from lib import pdx_ground

        path = self.death(droop=75.0)
        hips_before = self.hips(path)
        pdx_ground.ground(self.mesh_path, path, path, death=True)
        self.assertGreater(float((self.hips(path) - hips_before).max()), 0.1 * self.mesh.height)

    def test_the_lift_turns_no_faster_than_the_settle_rate(self) -> None:
        path = self.death(droop=75.0)
        before = pdx_deform.load_anim(path)
        L.lift_death_chains(self.mesh_path, path, path)
        after = pdx_deform.load_anim(path)
        q0, q1 = before.channels["WingL1_1"]["q"], after.channels["WingL1_1"]["q"]
        extra = np.degrees(2.0 * np.arccos(np.clip(np.abs(np.sum(q0 * q1, axis=1)), 0.0, 1.0)))
        self.assertGreater(float(extra.max()), 0.0)
        self.assertLessEqual(float(np.abs(np.diff(extra)).max()), tripo_trim.SETTLE_MAX_RATE + 1.0)

    def test_a_wing_above_the_ground_is_left_alone(self) -> None:
        path = self.death(droop=10.0)
        data = path.read_bytes()
        result = L.lift_death_chains(self.mesh_path, path, path)
        self.assertFalse(result.changed)
        self.assertEqual(path.read_bytes(), data)


if __name__ == "__main__":
    unittest.main()
