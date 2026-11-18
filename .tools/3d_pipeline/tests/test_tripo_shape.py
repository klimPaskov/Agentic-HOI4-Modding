"""The shape check for reduced parts: shells, silhouettes and the refusals built on them."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))

import numpy as np

from lib import tripo_shape as shape


def plate(x0, x1, z0, z1, offset=0, split=False):
    """A flat quad in the x-z plane as two triangles; with split=True a duplicated corner pair, like a UV seam."""

    points = np.array([[x0, 0, z0], [x1, 0, z0], [x1, 0, z1], [x0, 0, z1]], dtype=float)
    triangles = np.array([[0, 1, 2], [0, 2, 3]]) + offset
    if split:
        points = np.vstack([points, points[[0, 2]]])
        triangles = np.array([[0, 1, 2], [4, 5, 3]]) + offset
    return points, triangles




class Shells(unittest.TestCase):
    def test_vertices_split_along_a_seam_are_one_shell_and_a_gap_makes_two(self) -> None:
        one = plate(0, 1, 0, 1, split=True)
        self.assertEqual(shape.shell_summary(*one, 1e-6)["shells"], 1)
        far = plate(3, 4, 0, 1, offset=6)
        positions = np.vstack([one[0], far[0]])
        triangles = np.vstack([one[1], far[1]])
        summary = shape.shell_summary(positions, triangles, 1e-6)
        self.assertEqual(summary["shells"], 2)
        self.assertAlmostEqual(summary["max_gap"], 2.0, places=6)
        self.assertAlmostEqual(summary["max_gap_share"], 0.5, places=6)


class Silhouettes(unittest.TestCase):
    def test_a_filled_plate_gives_a_full_front_mask_and_identical_parts_agree(self) -> None:
        part = plate(0, 1, 0, 1)
        low, high = part[0].min(axis=0), part[0].max(axis=0)
        masks = shape.silhouettes(*part, low, high, size=64)
        self.assertGreater(masks["front"].mean(), 0.85)
        self.assertEqual(shape.iou(masks["front"], masks["front"]), 1.0)
        self.assertEqual(shape.iou(np.zeros((4, 4), bool), np.zeros((4, 4), bool)), 1.0)

    def test_half_the_part_has_half_the_agreement(self) -> None:
        whole, half = plate(0, 1, 0, 1), plate(0, 0.5, 0, 1)
        report = shape.shape_report(whole, half, size=96)
        self.assertLess(report["iou"]["front"], 0.6)
        self.assertGreater(report["iou"]["front"], 0.4)


class Refusals(unittest.TestCase):
    def report(self, **changes):
        base = {
            "shells_before": {"shells": 1, "max_gap_share": 0.0},
            "shells_after": {"shells": 1, "max_gap_share": 0.0},
            "iou": {"front": 0.99, "side": 0.98, "top": 0.99},
        }
        base.update(changes)
        return base

    def test_an_intact_part_passes(self) -> None:
        self.assertEqual(shape.shape_problems(self.report()), [])

    def test_more_shells_a_far_shell_or_a_poor_silhouette_each_fail(self) -> None:
        self.assertIn("split the part into 4 shells", shape.shape_problems(self.report(shells_after={"shells": 4, "max_gap_share": 0.0}))[0])
        far = shape.shape_problems(self.report(shells_after={"shells": 1, "max_gap_share": 0.2}))
        self.assertIn("from the main body", far[0])
        poor = shape.shape_problems(self.report(iou={"front": 0.99, "side": 0.90, "top": 0.99}))
        self.assertIn("side silhouette", poor[0])
        self.assertEqual(shape.shape_problems(self.report(iou={"front": 0.99, "side": 0.90, "top": 0.99}), min_iou=0.85), [])


if __name__ == "__main__":
    unittest.main()
