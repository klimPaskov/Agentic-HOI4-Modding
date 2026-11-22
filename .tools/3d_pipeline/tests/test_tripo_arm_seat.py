"""The arm re-seat for a winged rig whose arm chain Tripo put outside the arms (lib/tripo_arm_seat.py). A synthetic side: a flat wing behind the
shoulder and a hanging arm in front of it, all bound to the hand as on the ZIN devil. No Blender."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))

from lib import tripo_arm_seat as S


def strip(points: np.ndarray, start: int) -> list:
    """Triangles joining consecutive pairs of a two-row strip of points (row-major: point 2i and 2i+1 are a pair)."""

    tris = []
    for i in range(0, len(points) - 2, 2):
        a = start + i
        tris += [(a, a + 1, a + 2), (a + 1, a + 3, a + 2)]
    return tris


def side_model():
    """The left side (x < 0): an arm from (-0.06, 1.4) down to (-0.12, 0.8) at z = 0.06, and a wing sheet at z = 0 out to x = -1.0."""

    arm = []
    for t in np.linspace(0.0, 1.0, 30):
        centre = np.array([-0.06 - 0.06 * t, 1.4 - 0.6 * t, 0.06])
        arm += [centre + [-0.01, 0, 0], centre + [0.01, 0, 0]]
    wing = []
    for x in np.linspace(-0.25, -1.0, 40):
        wing += [[x, 1.2, 0.0], [x, 1.8, 0.0]]
    hips = [[0.0, 1.0, 0.0], [0.0, 1.0, 0.0]]  # a small body piece on the mid-line, so the width is the wing's
    right = [[0.6, 1.2, 0.0], [0.6, 1.8, 0.0]]
    positions = np.array(arm + wing + hips + right, float)
    triangles = np.array(strip(np.array(arm), 0) + strip(np.array(wing), len(arm)), int)
    dominant = np.array(["LeftHand"] * (len(arm) + len(wing)) + ["Hips"] * 2 + ["RightHand"] * 2)
    heads = {"Hips": np.array([0.0, 1.0, 0.0]), "LeftArm": np.array([-0.03, 1.45, 0.0]), "Head": np.array([0.0, 1.7, 0.0])}
    return positions, triangles, dominant, heads, len(arm)


class ArmSeat(unittest.TestCase):
    def test_the_arm_in_front_of_the_wing_gets_the_chain_and_the_wing_goes_to_the_shoulder(self) -> None:
        positions, triangles, dominant, heads, arm_count = side_model()
        seat = S.seat_side("Left", positions, triangles, dominant, heads, body_height=1.7)
        self.assertTrue(seat["arm"][:arm_count].all(), seat["numbers"])
        self.assertFalse(seat["arm"][arm_count:].any())
        self.assertEqual(int(seat["wing"].sum()), 80)
        elbow, wrist = seat["joints"]["ForeArm"], seat["joints"]["Hand"]
        self.assertAlmostEqual(elbow[1], 1.4 - 0.6 * S.ELBOW_SHARE, delta=0.05)
        self.assertAlmostEqual(wrist[1], 1.4 - 0.6 * S.WRIST_SHARE, delta=0.05)

    def test_a_side_without_a_wing_is_refused(self) -> None:
        positions, triangles, dominant, heads, arm_count = side_model()
        dominant[arm_count:arm_count + 80] = "Spine02"
        with self.assertRaises(S.SeatError):
            S.seat_side("Left", positions, triangles, dominant, heads, body_height=1.7)

    def test_the_arm_weights_run_from_upper_arm_to_hand_and_sum_to_one(self) -> None:
        for share in np.linspace(0.0, 1.0, 21):
            row = S.arm_weights(float(share))
            self.assertAlmostEqual(sum(row.values()), 1.0, places=6)
        self.assertEqual(S.arm_weights(0.1), {"Arm": 1.0})
        self.assertEqual(S.arm_weights(0.6), {"ForeArm": 1.0})
        self.assertEqual(S.arm_weights(0.95), {"Hand": 1.0})


if __name__ == "__main__":
    unittest.main()
