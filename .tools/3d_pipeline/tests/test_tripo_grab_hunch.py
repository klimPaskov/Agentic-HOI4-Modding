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


class WideGrab(Biped):
    def test_the_arms_swing_out_wide_on_the_approach_and_close_at_the_peak(self) -> None:
        travel = np.concatenate([np.zeros(5), np.linspace(0.0, 1.0, 15), np.ones(5), np.linspace(1.0, 0.0, 10)])
        plan = G.wide_plan(travel)
        peak = int(np.argmax(travel))
        self.assertEqual(plan[0], G.READY)
        self.assertEqual(plan[-1], G.READY)  # the loop holds
        np.testing.assert_allclose(plan[peak], (G.UPPER_ARM, G.FOREARM), atol=1e-9)
        outs = [step[0][2] for step in plan[:peak]]
        self.assertGreater(max(outs), 0.7, "the upper arms swing out wide before the peak")

    def test_the_wide_grab_opens_the_hands_then_brings_them_together(self) -> None:
        path = self.clip("attack", 30, lunge())
        result = G.grab_attack(self.mesh_path, path, FRONT, wide=True)
        self.assertTrue(result["wide"], result)
        after = pdx_motion.posed_joints(self.mesh, self.load(path))
        names = self.mesh.bones
        gap = np.linalg.norm(after[:, names.index("LeftHand")] - after[:, names.index("RightHand")], axis=1)
        peak = 10
        self.assertGreater(float(gap[:peak].max()), 1.5 * float(gap[peak]))


class Recoil(Biped):
    def test_the_recoil_throws_the_torso_back_and_the_arms_out(self) -> None:
        from lib import tripo_guard

        defend, idle = self.clip("defend", 21, lambda frame: {}), self.clip("idle", 21, lambda frame: {})
        before = pdx_motion.posed_joints(self.mesh, self.load(defend))
        tripo_guard.guard_defend(self.mesh_path, defend, idle, FRONT, **tripo_guard.RECOIL)
        after = pdx_motion.posed_joints(self.mesh, self.load(defend))
        names = self.mesh.bones
        head, hips = names.index("Head"), names.index("Hips")
        self.assertLess(float(after[10, head, 2] - after[10, hips, 2]), -0.05, "the head goes back behind the hips")
        for hand, arm in (("LeftHand", "LeftArm"), ("RightHand", "RightArm")):
            self.assertLess(float(after[10, names.index(hand), 1]), float(after[10, names.index(arm), 1]), f"{hand} flung down")
        np.testing.assert_allclose(after[0], before[0], atol=1e-5)


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
