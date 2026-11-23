"""lib/static_yard.py: a map building's wide raised yard becomes a thin skirt close to its footprint."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))

from lib import static_yard


def box(low, high):
    (x0, y0, z0), (x1, y1, z1) = low, high
    points = np.array([[x, y, z] for z in (z0, z1) for y in (y0, y1) for x in (x0, x1)], dtype=float)
    faces = [(0, 2, 1), (1, 2, 3), (4, 5, 6), (5, 7, 6), (0, 1, 4), (1, 5, 4), (2, 6, 3), (3, 6, 7), (0, 4, 2), (2, 4, 6), (1, 3, 5), (3, 7, 5)]
    return points, np.array(faces)


def yard_disc(radius, height, rings=6, spokes=36):
    """A raised earth disc: a grid of rings, its rim at `height` and its centre a little higher."""

    points = [[0.0, 0.0, height * 1.2]]
    for r in range(1, rings + 1):
        for s in range(spokes):
            a = 2 * np.pi * s / spokes
            points.append([radius * r / rings * np.cos(a), radius * r / rings * np.sin(a), height])
    triangles = []
    for s in range(spokes):
        triangles.append((0, 1 + s, 1 + (s + 1) % spokes))
    for r in range(1, rings):
        for s in range(spokes):
            a, b = 1 + (r - 1) * spokes + s, 1 + (r - 1) * spokes + (s + 1) % spokes
            c, d = a + spokes, b + spokes
            triangles += [(a, c, b), (b, c, d)]
    return np.array(points), np.array(triangles)


def scene(with_yard=True):
    parts = [box((-2, -2, 0.0), (2, 2, 5.0))]  # the building
    if with_yard:
        parts.append(yard_disc(8.0, 0.3))  # a yard reaching far past it
    parts.append(box((5.0, -0.3, 0.3), (5.6, 0.3, 0.9)))  # a barrel out on the yard
    points, triangles, base = [], [], 0
    for p, t in parts:
        points.append(p)
        triangles.append(t + base)
        base += len(p)
    return np.vstack(points), np.vstack(triangles)


class YardSkirt(unittest.TestCase):
    def test_wide_yard_is_pulled_in_and_lowered(self):
        points, triangles = scene()
        new, report = static_yard.yard_skirt(points, triangles)
        self.assertTrue(report["yard"])
        self.assertGreater(report["reach_before"], 0.3)
        self.assertLessEqual(report["reach_after"], static_yard.REACH + 1e-6)
        self.assertLess(report["rim_height_after"], report["rim_height_before"])
        # the building itself does not move
        np.testing.assert_allclose(new[:8], points[:8])
        # the outermost ring stays outermost along each ray (no fold)
        disc = slice(8, 8 + 1 + 6 * 36)
        radius = np.linalg.norm(new[disc][1:, :2], axis=1).reshape(6, 36)
        self.assertTrue((np.diff(radius, axis=0) >= -1e-9).all())
        # the barrel moved in with the yard and kept its shape
        barrel_before, barrel_after = points[-8:], new[-8:]
        self.assertEqual(report["loose_pieces_moved"], 1)
        self.assertLess(barrel_after[:, 0].mean(), barrel_before[:, 0].mean())
        np.testing.assert_allclose(np.ptp(barrel_after, axis=0), np.ptp(barrel_before, axis=0), atol=1e-9)

    def test_findings_flag_a_wide_yard_only(self):
        points, triangles = scene()
        self.assertEqual(static_yard.yard_findings(points, triangles)[0][0], "STATIC-YARD")
        new, _report = static_yard.yard_skirt(points, triangles)
        self.assertEqual(static_yard.yard_findings(new, triangles), [])

    def test_model_without_yard_is_left_alone(self):
        points, triangles = scene(with_yard=False)
        new, report = static_yard.yard_skirt(points, triangles)
        self.assertFalse(report["yard"])
        np.testing.assert_array_equal(new, points)


if __name__ == "__main__":
    unittest.main()
