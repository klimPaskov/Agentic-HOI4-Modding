"""An unarmed lunge posed as a two-handed grab (lib/tripo_grab.py) and an idle posed hunched with the head forward (lib/tripo_hunch.py), on
the synthetic biped of test_tripo_pose_upper (it faces +Z). No Blender."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))
sys.path.insert(0, str(PIPELINE / "tests"))
sys.path.insert(0, str(PIPELINE / "tripo"))

from lib import pdx_motion, tripo_grab as G, tripo_hunch as H
from test_tripo_pose_upper import Biped, local

FRONT = np.array([0.0, 0.0, 1.0])


def lunge(frames: int = 30, step: float = 0.3):
    """Standing in a T-pose, the hips step `step` forward and back: up over the first third, held, back over the last third."""

    def pose(frame: int):
        t = frame / (frames - 1)
        share = min(t * 3.0, 1.0, (1.0 - t) * 3.0)
        hips = local("Hips")
        return {"Hips": ((hips[0], hips[1], hips[2] + step * share), (0.0, 0.0, 0.0, 1.0))}

    return pose


class Grab(Biped):
    def test_the_hands_reach_out_together_in_front_while_the_body_lunges(self) -> None:
        path = self.clip("attack", 30, lunge())
        before = pdx_motion.posed_joints(self.mesh, self.load(path))
        result = G.grab_attack(self.mesh_path, path, FRONT)
        self.assertTrue(result["changed"], result)
        after = pdx_motion.posed_joints(self.mesh, self.load(path))
        names = self.mesh.bones
        left, right, chest = (names.index(n) for n in ("LeftHand", "RightHand", "Spine02"))
        mid = 15
        gap_before = float(np.linalg.norm(before[mid, left] - before[mid, right]))
        gap_after = float(np.linalg.norm(after[mid, left] - after[mid, right]))
        self.assertLess(gap_after, 0.4 * gap_before)
        for hand in (left, right):
            self.assertGreater(float(after[mid, hand, 2] - after[mid, chest, 2]), 0.2, "the hand is out in front of the chest")
            self.assertAlmostEqual(float(after[mid, hand, 1]), float(after[mid, names.index("LeftArm"), 1]), delta=0.06)
        np.testing.assert_allclose(after[0], before[0], atol=1e-5)  # the clip starts and ends on its own pose
        np.testing.assert_allclose(after[-1], before[-1], atol=1e-5)
        legs = [names.index(n) for n in ("Hips", "LeftFoot", "RightFoot", "Head")]
        np.testing.assert_allclose(after[:, legs], before[:, legs], atol=1e-5)  # the body keeps the clip's own motion

    def test_the_weight_follows_the_lunge_and_a_clip_with_no_step_gets_the_ramp(self) -> None:
        weight = G.lunge_weight(self.mesh, self.load(self.clip("attack", 30, lunge())), FRONT)
        self.assertEqual(float(weight[0]), 0.0)
        self.assertAlmostEqual(float(weight[15]), 1.0)
        still = G.lunge_weight(self.mesh, self.load(self.clip("still", 21, lambda frame: {})), FRONT)
        np.testing.assert_allclose(still, G.tripo_guard.ramp(21))


class Hunch(Biped):
    def test_the_idle_leans_forward_to_the_target_with_the_head_ahead(self) -> None:
        path = self.clip("idle", 12, lambda frame: {})
        before = pdx_motion.posed_joints(self.mesh, self.load(path))
        result = H.hunch_idle(self.mesh_path, path, FRONT)
        self.assertTrue(result["changed"], result)
        self.assertGreaterEqual(result["lean_after"], 12.0)
        self.assertEqual(result["reached"], result["lean_after"] >= H.TARGET)
        reached = H.hunch_idle(self.mesh_path, self.clip("idle2", 12, lambda frame: {}), FRONT, target=12.0)
        self.assertTrue(reached["reached"], reached)
        self.assertLess(reached["lean_after"], 12.0 + 4.0)
        after = pdx_motion.posed_joints(self.mesh, self.load(path))
        names = self.mesh.bones
        head, chest = names.index("Head"), names.index("Spine02")
        self.assertGreater(float(after[0, head, 2] - after[0, chest, 2]), 0.0, "the head juts out ahead of the chest")
        self.assertLess(float(after[0, head, 1]), float(before[0, head, 1]))
        legs = [names.index(n) for n in ("Hips", "LeftFoot", "RightFoot")]
        np.testing.assert_allclose(after[:, legs], before[:, legs], atol=1e-5)
        np.testing.assert_allclose(after[0], after[-1], atol=1e-5)  # every frame takes the same turn: the loop holds

    def test_an_idle_that_already_leans_is_left_as_it_was(self) -> None:
        path = self.clip("idle", 6, lambda frame: {})
        H.hunch_idle(self.mesh_path, path, FRONT, target=12.0)
        data = path.read_bytes()
        result = H.hunch_idle(self.mesh_path, path, FRONT, target=12.0)
        self.assertFalse(result["changed"], result)
        self.assertEqual(path.read_bytes(), data)


if __name__ == "__main__":
    unittest.main()
