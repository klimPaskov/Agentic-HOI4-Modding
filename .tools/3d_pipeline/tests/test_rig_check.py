"""TRIPO-RIG-ARMS (tripo/rig_check.py): Tripo's auto-rig must put the arm chain into the arms. A synthetic layout, and a real export when one
is on this machine. No Blender."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))
sys.path.insert(0, str(PIPELINE / "tests"))
sys.path.insert(0, str(PIPELINE / "tripo"))

import rig_check as R
from rig_glb import REAL_EXPORT


def layout(hand_points_out: float, forearm_points: int = 20) -> dict:
    """Both arms hang from the shoulder along x: upper arm 0.15, forearm 0.15 (arm length 0.3), and hand skin out to `hand_points_out`."""

    heads, positions, dominant = {}, [], []
    for side, sign in (("Left", -1.0), ("Right", 1.0)):
        heads[f"{side}Arm"] = np.array([sign * 0.10, 1.4, 0.0])
        heads[f"{side}ForeArm"] = np.array([sign * 0.25, 1.4, 0.0])
        heads[f"{side}Hand"] = np.array([sign * 0.40, 1.4, 0.0])
        for t in np.linspace(0.26, 0.39, forearm_points):
            positions.append([sign * t, 1.4, 0.0])
            dominant.append(f"{side}ForeArm")
        for t in np.linspace(0.40, 0.40 + hand_points_out, 20):
            positions.append([sign * t, 1.4, 0.0])
            dominant.append(f"{side}HandIndex1" if t > 0.45 else f"{side}Hand")
    return {"heads": heads, "positions": np.array(positions), "dominant": np.array(dominant)}


class RigCheck(unittest.TestCase):
    def test_a_hand_that_holds_a_hand_passes(self) -> None:
        found, numbers = R.rig_findings(layout(0.12))
        self.assertEqual(found, [], numbers)
        self.assertLess(numbers["Left"]["hand_reach"], 0.6)

    def test_a_hand_that_holds_a_wing_or_an_arm_with_no_forearm_skin_fails(self) -> None:
        found, _numbers = R.rig_findings(layout(0.9))
        self.assertEqual({item["subject"] for item in found}, {"Left", "Right"})
        found, _numbers = R.rig_findings(layout(0.12, forearm_points=0))
        self.assertEqual([item["rule"] for item in found], ["TRIPO-RIG-ARMS", "TRIPO-RIG-ARMS"])

    @unittest.skipUnless(REAL_EXPORT.is_file(), "no real Tripo export on this machine")
    def test_a_real_humanoid_rig_passes(self) -> None:
        found, numbers = R.rig_findings(R.skin_layout(REAL_EXPORT))
        self.assertEqual(found, [], numbers)


if __name__ == "__main__":
    unittest.main()
