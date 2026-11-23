"""tripo/proportion_check.py: a quadruped model's neck and legs against its reference picture, before the rig."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))
sys.path.insert(0, str(PIPELINE / "adapter"))
sys.path.insert(0, str(PIPELINE / "tripo"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import proportion_check as pc
from test_quadruped_ears import _box


def _dragon(neck_top: float):
    """A blocky winged dragon facing -Y with a thin neck column from the torso's top (1.6) to `neck_top`, under a head 0.35 tall."""

    parts = [((x - 0.08, y - 0.08, 0.0), (x + 0.08, y + 0.08, 1.0), 8) for x in (-0.22, 0.22) for y in (0.0, 1.6)]
    parts.append(((-0.35, -0.2, 1.0), (0.35, 1.8, 1.6), 8))
    parts.append(((-0.06, -0.3, 1.55), (0.06, -0.1, neck_top), (2, 3, 8)))
    parts.append(((-0.2, -0.85, neck_top), (0.2, -0.1, neck_top + 0.35), 8))
    parts.append(((-0.04, 2.25, 0.0), (0.04, 3.6, 0.05), (2, 16, 1)))
    parts.append(((-0.04, 1.8, 0.3), (0.04, 2.25, 1.2), (2, 4, 8)))
    parts.append(((-0.04, 2.2, 0.05), (0.04, 2.25, 0.3), (2, 1, 4)))
    parts.append(((0.25, 0.4, 1.3), (1.6, 0.42, 2.2), (16, 1, 10)))
    parts.append(((-1.6, 0.4, 1.3), (-0.25, 0.42, 2.2), (16, 1, 10)))
    points, triangles = [], []
    for lo, hi, steps in parts:
        p, t = _box(lo, hi, steps)
        triangles.append(t + sum(len(x) for x in points))
        points.append(p)
    return np.vstack(points), np.vstack(triangles)


class Proportions(unittest.TestCase):
    def test_the_neck_and_legs_are_measured_as_shares_of_the_height(self) -> None:
        found = pc.model_proportions(*_dragon(2.0))
        height = 2.35
        self.assertAlmostEqual(found["neck"], 0.4 / height, delta=0.06)
        self.assertAlmostEqual(found["legs"], 1.0 / height, delta=0.06)

    def test_a_neck_much_shorter_than_drawn_fails_and_one_as_drawn_passes(self) -> None:
        short = pc.model_proportions(*_dragon(2.0))
        drawn = {"neck": short["neck"], "legs": short["legs"]}
        self.assertEqual(pc.proportion_verdict(short, drawn)["verdict"], "pass")
        long_picture = {"neck": 2.0 * short["neck"], "legs": short["legs"]}
        verdict = pc.proportion_verdict(short, long_picture)
        self.assertEqual(verdict["verdict"], "fail")
        self.assertEqual([item["part"] for item in verdict["findings"]], ["neck"])

    def test_a_model_without_a_neck_column_fails_a_picture_with_one(self) -> None:
        self.assertEqual(pc.proportion_verdict({"neck": 0.0, "legs": 0.4}, {"neck": 0.2, "legs": None})["verdict"], "fail")

    def test_shares_read_off_a_picture_are_judged_before_any_model(self) -> None:
        self.assertEqual(pc.main(["--shares", "neck=0.12,legs=0.36", "--neck", "0.22", "--legs", "0.36"]), 1, "a multi-view that lost the neck")
        self.assertEqual(pc.main(["--shares", "neck=0.21,legs=0.35", "--neck", "0.22", "--legs", "0.36"]), 0, "a redraw that kept it")


if __name__ == "__main__":
    unittest.main()
