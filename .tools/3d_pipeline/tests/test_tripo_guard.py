"""The defend posed as a guard (lib/tripo_guard.py) and the defend against the attack on the map camera (lib/map_read.alike_findings).
A synthetic biped. No Blender."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))
sys.path.insert(0, str(PIPELINE / "tests"))

import test_deformation_checks as TD
from lib import map_read, pdx_deform, pdx_motion, tripo_guard as G
from test_tripo_chain_lift import WingedBiped, local
from test_tripo_pose_upper import turn


class Guard(WingedBiped):
    def clip(self, name: str, frames: int = 20, twist: float = 0.0) -> Path:
        path = self.folder / f"unit_{name}.anim"
        TD.write_anim(path, frames, lambda frame: {"Spine": (local("Spine"), turn("y", twist))} if twist else {})
        return path

    def test_the_ramp_starts_and_ends_on_the_clips_own_pose(self) -> None:
        weight = G.ramp(21)
        self.assertEqual(float(weight[0]), 0.0)
        self.assertEqual(float(weight[-1]), 0.0)
        self.assertAlmostEqual(float(weight[10]), 1.0)

    def test_both_hands_come_up_before_the_face_and_the_twist_goes(self) -> None:
        defend, idle = self.clip("defend", twist=40.0), self.clip("idle")
        before = pdx_motion.posed_joints(self.mesh, pdx_deform.load_anim(defend))
        G.guard_defend(self.mesh_path, defend, idle, np.array([0.0, 0.0, 1.0]))
        after = pdx_motion.posed_joints(self.mesh, pdx_deform.load_anim(defend))
        names = self.mesh.bones
        chest = after[10, names.index("Spine02"), 1]
        for hand in ("LeftHand", "RightHand"):
            self.assertGreater(float(after[10, names.index(hand), 1]), chest, hand)
            self.assertGreater(float(after[10, names.index(hand), 2]), float(after[10, names.index("Spine02"), 2]), f"{hand} ahead of the chest")
        np.testing.assert_allclose(after[0], before[0], atol=1e-5)  # the first frame is the clip's own


class Alike(WingedBiped):
    def test_a_defend_posed_as_the_attack_fails_and_a_different_one_passes(self) -> None:
        still = lambda frame: {}
        raised = lambda frame: {"LeftArm": (local("LeftArm"), turn("z", -80.0)), "RightArm": (local("RightArm"), turn("z", 80.0))}
        paths = {}
        for name, pose in (("attack", still), ("defend", still), ("other", raised)):
            paths[name] = self.folder / f"unit_{name}.anim"
            TD.write_anim(paths[name], 6, pose)
        load = pdx_deform.load_anim
        found, _numbers = map_read.alike_findings(self.mesh, {"unit_attack": load(paths["attack"]), "unit_defend": load(paths["defend"])})
        self.assertEqual([item["rule"] for item in found], ["TRIPO-MAP-ALIKE"])
        self.assertEqual(map_read.MIN_DEFEND_ATTACK_PIXELS, 125.0)


if __name__ == "__main__":
    unittest.main()
