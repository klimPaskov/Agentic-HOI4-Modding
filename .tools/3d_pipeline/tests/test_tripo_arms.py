"""The arm-level maths: where the hands are, and the one constant rotation that brings them to chest height."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))

from lib import tripo_arms as A  # noqa: E402


def frames(count, hand_y, shoulder_y=1.4, head_y=1.6, hips_y=1.0, forward=0.3):
    """Joint tracks for `count` frames; y is up and z is forward. `hand_y` is a number or an array per frame."""

    hand_y = np.broadcast_to(np.asarray(hand_y, float), (count,))
    hand = np.stack([np.full(count, 0.2), hand_y, np.full(count, forward)], axis=1)
    other = hand.copy()
    other[:, 0] = -0.2
    shoulder = np.stack([np.full(count, 0.2), np.full(count, shoulder_y), np.zeros(count)], axis=1)
    other_shoulder = shoulder.copy()
    other_shoulder[:, 0] = -0.2
    head = np.stack([np.zeros(count), np.full(count, head_y), np.zeros(count)], axis=1)
    hips = np.stack([np.zeros(count), np.full(count, hips_y), np.zeros(count)], axis=1)
    return hand, other, shoulder, other_shoulder, head, hips


class HandsHigh(unittest.TestCase):
    def test_hands_over_the_head_fail(self) -> None:
        hand, other, s1, s2, head, _ = frames(40, 1.9)
        levels = A.hand_levels(hand, other, s1, s2, head)
        self.assertEqual(levels["above_head_share"], 1.0)
        self.assertIn("above the head", A.hands_high(levels))

    def test_hands_above_the_shoulders_but_below_the_head_fail_on_the_shoulder_rule(self) -> None:
        hand, other, s1, s2, head, _ = frames(40, 1.5)
        levels = A.hand_levels(hand, other, s1, s2, head)
        self.assertEqual(levels["above_head_share"], 0.0)
        self.assertIn("above the shoulders", A.hands_high(levels))

    def test_hands_at_chest_height_pass_and_a_short_raise_is_allowed(self) -> None:
        hand, other, s1, s2, head, _ = frames(40, 1.2)
        self.assertIsNone(A.hands_high(A.hand_levels(hand, other, s1, s2, head)))
        raised = np.full(40, 1.2)
        raised[:6] = 1.9  # 15% of the frames over the head
        hand, other, s1, s2, head, _ = frames(40, raised)
        self.assertIsNone(A.hands_high(A.hand_levels(hand, other, s1, s2, head)))
        raised[:10] = 1.9  # 25%
        hand, other, s1, s2, head, _ = frames(40, raised)
        self.assertIsNotNone(A.hands_high(A.hand_levels(hand, other, s1, s2, head)))


class Target(unittest.TestCase):
    def test_the_target_runs_from_chest_to_shoulder_height(self) -> None:
        shoulder = np.array([[0.0, 1.4, 0.0]])
        hips = np.array([[0.0, 1.0, 0.0]])
        self.assertAlmostEqual(float(A.chest_height(shoulder, hips, 1)[0]), 1.2)
        self.assertAlmostEqual(float(A.chest_height(shoulder, hips, 1, 0.5)[0]), 1.3)
        self.assertAlmostEqual(float(A.chest_height(shoulder, hips, 1, 1.0)[0]), 1.4)


class Solve(unittest.TestCase):
    def test_the_rotation_that_brings_the_mean_error_to_zero_is_found(self) -> None:
        # a straight arm of length 0.6 at the shoulder (y = 1.4): the hand height is 1.4 + 0.6 sin(pitch), pitch = 1.2 + angle
        chest = 1.2

        def error(angle):
            return 1.4 + 0.6 * np.sin(1.2 + angle) - chest

        angle, left = A.solve_arm_offset(error)
        self.assertLess(abs(left), 2e-3)
        self.assertAlmostEqual(1.4 + 0.6 * np.sin(1.2 + angle), chest, places=2)

    def test_it_returns_the_best_end_when_the_height_cannot_be_reached(self) -> None:
        angle, left = A.solve_arm_offset(lambda a: 1.0 + 0.1 * a)  # never zero on the interval
        self.assertAlmostEqual(angle, -2.4)
        self.assertAlmostEqual(left, 1.0 - 0.24)

    def test_the_turn_nearest_zero_is_chosen_when_there_are_several(self) -> None:
        angle, _ = A.solve_arm_offset(lambda a: np.sin(3.0 * a) + 0.1)
        self.assertLess(abs(angle), 0.2)

    def test_the_axis_with_the_steepest_slope_is_picked_with_its_sign(self) -> None:
        self.assertEqual(A.pick_axis([0.05, -0.9, 0.2]), (1, -1.0))
        self.assertEqual(A.pick_axis([0.7, 0.1, 0.2]), (0, 1.0))


class ReachPhase(unittest.TestCase):
    def test_the_reach_phase_is_where_the_hands_are_farthest_forward(self) -> None:
        forward = np.concatenate([np.linspace(0.0, 0.5, 20), np.linspace(0.5, 0.0, 20)])
        hand = np.stack([np.zeros(40), np.full(40, 1.2), forward], axis=1)
        hips = np.zeros((40, 3))
        chosen = A.reach_frames(hand, hips, np.array([0.0, 0.0, 1.0]), share=0.5)
        self.assertTrue(all(forward[i] >= 0.25 for i in chosen))
        self.assertIn(19, chosen)
        self.assertNotIn(0, chosen)

    def test_a_minimum_number_of_frames_is_kept(self) -> None:
        hand = np.stack([np.zeros(12), np.full(12, 1.2), np.linspace(0, 1, 12)], axis=1)
        chosen = A.reach_frames(hand, np.zeros((12, 3)), np.array([0.0, 0.0, 1.0]), share=0.99, minimum=6)
        self.assertEqual(len(chosen), 6)


if __name__ == "__main__":
    unittest.main()
