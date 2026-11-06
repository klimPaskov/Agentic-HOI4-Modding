"""Quadruped landmarks and skin weights on a procedural horse, without Blender."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "adapter"))

import quadruped_layout


def _line(start, end, count, radius, rng):
    t = rng.random(count)[:, None]
    return np.asarray(start) + t * (np.asarray(end) - np.asarray(start)) + rng.normal(0.0, radius, (count, 3))


def horse_with_hanging_tail() -> np.ndarray:
    """A horse facing -Y whose tail hangs from the rump to below the belly."""

    rng = np.random.default_rng(7)
    parts = [
        _line((x, y, 0.0), (x, y, 1.0), 300, 0.04, rng) for x in (-0.25, 0.25) for y in (0.0, 1.6)
    ]
    parts.append(np.column_stack([rng.uniform(-0.35, 0.35, 3000), rng.uniform(-0.2, 1.8, 3000), rng.uniform(1.0, 1.6, 3000)]))
    parts.append(_line((0.0, -0.2, 1.5), (0.0, -0.6, 2.0), 400, 0.06, rng))
    parts.append(_line((0.0, 1.85, 1.5), (0.0, 2.0, 0.5), 400, 0.03, rng))
    return np.vstack(parts)


class HangingTail(unittest.TestCase):
    def test_a_tail_below_the_belly_follows_only_the_tail(self) -> None:
        points = horse_with_hanging_tail()
        landmarks = quadruped_layout.detect_landmarks(points)
        self.assertIsNotNone(landmarks["tail"])
        layout = quadruped_layout.build_layout(landmarks)
        names = layout.names()
        order, weights = quadruped_layout.skin_weights(points, layout)
        tail_tip = (points[:, 1] > 1.9) & (points[:, 2] < 0.9)
        self.assertGreater(int(tail_tip.sum()), 20)
        for row in np.flatnonzero(tail_tip):
            used = [names[order[row, column]] for column in range(order.shape[1]) if weights[row, column] > 0]
            self.assertTrue(used and all(name.startswith("Tail_") for name in used), used)

    def test_the_rear_legs_keep_their_own_weights(self) -> None:
        points = horse_with_hanging_tail()
        layout = quadruped_layout.build_layout(quadruped_layout.detect_landmarks(points))
        names = layout.names()
        order, weights = quadruped_layout.skin_weights(points, layout)
        rear_hoof = (np.abs(points[:, 1] - 1.6) < 0.1) & (points[:, 2] < 0.3)
        for row in np.flatnonzero(rear_hoof):
            self.assertTrue(names[order[row, 0]].startswith("Rear_"), names[order[row, 0]])


if __name__ == "__main__":
    unittest.main()
