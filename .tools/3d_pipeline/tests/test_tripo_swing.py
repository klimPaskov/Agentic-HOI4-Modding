"""The weapon's head leads the blow (lib/tripo_swing.py): the strike frame, the lead cosine, the grip side and the head end. No Blender."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))

sys.path.insert(0, str(PIPELINE / "tests"))
sys.path.insert(0, str(PIPELINE / "tripo"))

import tempfile

import test_deformation_checks as TD
import tripo_checks
from lib import pdx_deform, tripo_swing as S

ARM = [("Root", -1, (0.0, 1.0, 0.0)), ("RightArm", 0, (0.0, 1.5, 0.0)), ("RightHand", 1, (0.0, 1.5, 0.5)), ("Weapon", 2, (0.0, 1.5, 0.55))]


def chop(frames: int = 30, strike: int = 20):
    """A hand that rises slowly, then chops down fast around `strike` and slows again."""

    t = np.arange(frames, dtype=float)
    speed = 0.02 + np.exp(-0.5 * ((t - strike) / 2.0) ** 2)
    rise = t < strike - 6
    step = np.where(rise[:, None], np.array([0.0, 0.05, 0.0]), np.array([0.0, -1.0, 0.3]) / np.linalg.norm([0.0, -1.0, 0.3]))
    hand = np.cumsum(step * speed[:, None], axis=0)
    return hand


class Strike(unittest.TestCase):
    def test_the_strike_is_the_hands_fastest_frame(self) -> None:
        self.assertLessEqual(abs(S.strike_frame(chop(strike=20)) - 20), 1)
        self.assertLessEqual(abs(S.strike_frame(chop(strike=12)) - 12), 1)

    def test_a_head_along_the_blow_leads_and_one_behind_trails(self) -> None:
        hand = chop()
        down = np.tile([0.0, -1.0, 0.3], (len(hand), 1))
        frame, cosine = S.head_lead(hand, down)
        self.assertLessEqual(abs(frame - 20), 1)
        self.assertGreater(cosine, 0.9)
        _frame, behind = S.head_lead(hand, -down)
        self.assertLess(behind, -0.9)
        _frame, across = S.head_lead(hand, np.tile([1.0, 0.0, 0.0], (len(hand), 1)))
        self.assertAlmostEqual(across, 0.0, places=6)

    def test_the_side_is_the_one_whose_head_leads(self) -> None:
        hand = chop()
        # the haft carried by the hand points up while the hand chops down: the head belongs on the other side
        up = np.tile([0.0, 1.0, 0.0], (len(hand), 1))
        side, cosine = S.lead_side(hand, up)
        self.assertEqual(side, -1)
        self.assertGreater(cosine, 0.9)
        self.assertEqual(S.lead_side(hand, -up)[0], 1)

    def test_the_head_end_is_the_wide_end(self) -> None:
        rng = np.random.default_rng(3)
        haft = np.column_stack([np.linspace(0.0, 10.0, 400), rng.normal(0, 0.05, 400), rng.normal(0, 0.05, 400)])
        blade = np.column_stack([rng.uniform(9.0, 10.0, 200), rng.uniform(-1.5, 1.5, 200), rng.normal(0, 0.05, 200)])
        points = np.vstack([haft, blade])
        mask, axis = S.head_end_mask(points)
        self.assertGreater(points[mask, 0].mean(), 8.0)
        self.assertGreater(axis[0], 0.9, "the axis points from the butt toward the head")
        mask, axis = S.head_end_mask(points * np.array([-1.0, 1.0, 1.0]))
        self.assertLess(points[mask, 0].mean() * -1.0, -8.0)
        self.assertLess(axis[0], -0.9)

    def test_the_limit_asks_the_head_not_to_trail(self) -> None:
        self.assertEqual(S.HEAD_LEAD_MIN, 0.0)


class Check(unittest.TestCase):
    """TRIPO-WEAPON-HEAD-LEAD on a synthetic arm that chops down with a weapon whose wide head points up or down from the fist."""

    def run_check(self, head_up: bool):
        saved = list(TD.BONES)
        TD.BONES[:] = ARM
        self.addCleanup(lambda: TD.BONES.__setitem__(slice(None), saved))
        sign = 1.0 if head_up else -1.0
        positions, triangles, owner = [], [], []
        for index, (_name, _parent, (x, y, z)) in enumerate(ARM[:3]):
            points, tris = TD.tetrahedron((x, y, z), 0.05)
            triangles += [tuple(len(positions) + i for i in tri) for tri in tris]
            positions += points
            owner += [index] * 4
        for k in range(20):  # the haft: thin, from the butt below the fist to the head above (or the other way round)
            along = sign * (-0.4 + 0.06 * k)
            points, tris = TD.tetrahedron((0.0, 1.5 + along, 0.55), 0.01)
            triangles += [tuple(len(positions) + i for i in tri) for tri in tris]
            positions += points
            owner += [3] * 4
        for k in range(12):  # the head: wide, at the far end
            points, tris = TD.tetrahedron((-0.2 + 0.04 * k, 1.5 + sign * 0.8, 0.55), 0.03)
            triangles += [tuple(len(positions) + i for i in tri) for tri in tris]
            positions += points
            owner += [3] * 4
        with tempfile.TemporaryDirectory() as folder:
            mesh_path, anim_path = Path(folder) / "u.mesh", Path(folder) / "u_attack.anim"
            TD.write_mesh(mesh_path, positions, triangles, owner)
            hand = chop(30, 20)
            TD.write_anim(anim_path, 30, lambda frame: {"Root": (tuple(np.array([0.0, 1.0, 0.0]) + hand[frame]), (0.0, 0.0, 0.0, 1.0))})
            mesh = pdx_deform.load_mesh(mesh_path)
            return tripo_checks.head_lead_findings(mesh, {"u_attack": pdx_deform.load_anim(anim_path)}, "Weapon")

    def test_a_head_held_up_while_the_arm_chops_down_fails(self) -> None:
        found, numbers = self.run_check(head_up=True)
        self.assertEqual([item["rule"] for item in found], ["TRIPO-WEAPON-HEAD-LEAD"], numbers)
        self.assertLess(numbers["u_attack"]["head_lead_cosine"], -0.5)

    def test_a_head_that_comes_down_first_passes(self) -> None:
        found, numbers = self.run_check(head_up=False)
        self.assertEqual(found, [])
        self.assertGreater(numbers["u_attack"]["head_lead_cosine"], 0.5)


if __name__ == "__main__":
    unittest.main()
