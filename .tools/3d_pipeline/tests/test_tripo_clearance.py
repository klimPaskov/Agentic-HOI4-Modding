"""The weapon-clearance rule on synthetic data: a stick through a box, turned about a pivot until it leaves."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))

from lib import tripo_clearance as C  # noqa: E402


def box(lo=-0.5, hi=0.5, subdivide=6):
    """A closed box as vertices and triangles; its faces are subdivided so the nearest-vertex depth is meaningful."""

    ticks = np.linspace(lo, hi, subdivide + 1)
    vertices, triangles, index = [], [], {}

    def vertex(p):
        key = tuple(np.round(p, 6))
        if key not in index:
            index[key] = len(vertices)
            vertices.append(p)
        return index[key]

    for axis in range(3):
        for value in (lo, hi):
            for i in range(subdivide):
                for j in range(subdivide):
                    corners = []
                    for di, dj in ((0, 0), (1, 0), (1, 1), (0, 1)):
                        p = np.zeros(3)
                        p[axis] = value
                        p[(axis + 1) % 3] = ticks[i + di]
                        p[(axis + 2) % 3] = ticks[j + dj]
                        corners.append(vertex(p))
                    triangles += [[corners[0], corners[1], corners[2]], [corners[0], corners[2], corners[3]]]
    return np.array(vertices), np.array(triangles)


def stick(pivot, length=0.4, count=40):
    """Points from the pivot straight toward -x."""

    return np.array([pivot - np.array([length * k / (count - 1), 0.0, 0.0]) for k in range(count)])


class Maths(unittest.TestCase):
    def test_rotation_matrices_are_rotations(self) -> None:
        matrix = C.rotation_matrix(np.array([0.0, 0.0, 1.0]), np.pi / 2)
        self.assertTrue(np.allclose(matrix @ [1.0, 0.0, 0.0], [0.0, 1.0, 0.0], atol=1e-9))
        self.assertTrue(np.allclose(C.rotvec_matrix(np.zeros(3)), np.eye(3)))
        for axis in C.fibonacci_axes(20):
            self.assertAlmostEqual(float(np.linalg.norm(axis)), 1.0, places=9)

    def test_smoothing_keeps_a_constant_and_spreads_a_spike(self) -> None:
        constant = np.tile([0.1, 0.0, 0.0], (10, 1))
        self.assertTrue(np.allclose(C.smooth_rotations(constant), constant))
        spike = np.zeros((11, 3))
        spike[5] = [1.0, 0.0, 0.0]
        smooth = C.smooth_rotations(spike)
        self.assertLess(smooth[5, 0], 1.0)
        self.assertGreater(smooth[4, 0], 0.0)
        self.assertAlmostEqual(float(smooth[:, 0].sum()), 1.0, places=9)

    def test_the_check_and_the_rule_agree_on_what_deep_means(self) -> None:
        vertices, triangles = box()
        inside = np.array([[0.0, 0.0, 0.0]])
        outside = np.array([[2.0, 0.0, 0.0]])
        self.assertEqual(C.deep_share(inside, vertices, triangles, 1.0), 1.0)
        self.assertEqual(C.deep_share(outside, vertices, triangles, 1.0), 0.0)
        centre = np.array([[0.0, 0.0, 0.0]])
        self.assertGreater(C.deep_share(centre, vertices, triangles, 1.0, margin=0.05), 0.0)
        self.assertEqual(C.deep_share(centre, vertices, triangles, 1.0, margin=0.9), 0.0)  # deeper than the margin only when it is that deep


class Solve(unittest.TestCase):
    def setUp(self) -> None:
        self.vertices, self.triangles = box()
        self.pivot = np.array([0.8, 0.0, 0.0])

    def test_a_clear_weapon_is_left_alone(self) -> None:
        points = stick(np.array([1.5, 0.0, 0.0]))
        vector, share = C.solve_frame(points, np.array([1.5, 0.0, 0.0]), self.vertices, self.triangles, 1.0)
        self.assertEqual(float(np.linalg.norm(vector)), 0.0)
        self.assertEqual(share, 0.0)

    def test_a_weapon_in_the_body_is_turned_out_by_the_smallest_angle_that_clears_it(self) -> None:
        points = stick(self.pivot, length=0.4)
        before = C.deep_share(points, self.vertices, self.triangles, 1.0)
        self.assertGreater(before, 0.2)
        vector, share = C.solve_frame(points, self.pivot, self.vertices, self.triangles, 1.0)
        angle = np.degrees(np.linalg.norm(vector))
        self.assertLessEqual(share, C.TARGET)
        self.assertGreater(angle, 0.0)
        self.assertLessEqual(angle, C.MAX_ANGLE_DEGREES + 1e-6)
        moved = (points - self.pivot) @ C.rotvec_matrix(vector).T + self.pivot
        self.assertLessEqual(C.deep_share(moved, self.vertices, self.triangles, 1.0), C.TARGET)

    def test_a_weapon_that_cannot_be_cleared_inside_the_cap_keeps_the_best_rotation_and_reports_the_share_left(self) -> None:
        buried = stick(np.array([0.0, 0.0, 0.0]), length=0.4)  # the pivot itself is in the middle of the body
        vector, share = C.solve_frame(buried, np.zeros(3), self.vertices, self.triangles, 1.0)
        self.assertGreater(share, C.TARGET)
        self.assertLessEqual(np.degrees(np.linalg.norm(vector)), C.MAX_ANGLE_DEGREES + 1e-6)


class Clip(unittest.TestCase):
    def test_a_clip_with_a_bad_stretch_is_cleared_frame_by_frame_and_the_report_says_what_failed(self) -> None:
        vertices, triangles = box()
        pivot = np.array([0.8, 0.0, 0.0])
        weapons, pivots, bodies = [], [], []
        for frame in range(9):
            reach = 0.4 if 3 <= frame <= 5 else 0.0  # in the middle frames the stick pokes into the box
            weapons.append(stick(pivot, length=0.1 + reach))
            pivots.append(pivot)
            bodies.append(vertices)
        # the grip zone (0.12 of the height from the pivot) is ignored, so the stick must reach past it to be judged: make it long
        weapons = [stick(pivot, length=0.1 + (0.3 if 3 <= f <= 5 else 0.0), count=60) for f in range(9)]
        result = C.clear_clip(weapons, pivots, bodies, triangles, 1.0)
        self.assertGreater(max(result["before"]), C.LIMIT)
        self.assertEqual(result["failed"], [])
        self.assertLessEqual(max(result["after"]), C.LIMIT)
        self.assertLessEqual(result["max_degrees"], C.MAX_ANGLE_DEGREES + 1e-6)
        self.assertGreater(result["frames_changed"], 0)

    def test_frames_from_the_release_on_are_left_to_the_fall(self) -> None:
        vertices, triangles = box()
        pivot = np.array([0.8, 0.0, 0.0])
        weapons = [stick(pivot, length=0.5, count=60) for _ in range(8)]
        result = C.clear_clip(weapons, [pivot] * 8, [vertices] * 8, triangles, 1.0, skip_from=5)
        sizes = np.linalg.norm(result["rotvecs"], axis=1)
        self.assertGreater(sizes[4], 0.0)
        self.assertTrue(all(sizes[k + 1] <= sizes[k] + 1e-9 for k in range(4, 7)))  # from the release the hand's rotation only fades out
        self.assertLess(sizes[7], sizes[4])
        self.assertTrue(all(i < 5 for i in result["failed"]))

    def test_the_grip_zone_can_be_fixed_at_the_rest_pose_as_the_check_does(self) -> None:
        vertices, triangles = box()
        pivot = np.array([0.8, 0.0, 0.0])
        weapons = [stick(pivot, length=0.4, count=60) for _ in range(3)]
        result = C.clear_clip(weapons, [pivot] * 3, [vertices] * 3, triangles, 1.0, rest_weapon=weapons[0], rest_grip=pivot)
        self.assertEqual(result["failed"], [])
        self.assertGreater(result["frames_changed"], 0)

    def test_a_clip_that_cannot_be_cleared_is_reported_failed(self) -> None:
        vertices, triangles = box()
        buried = [stick(np.zeros(3), length=0.5, count=60) for _ in range(4)]
        result = C.clear_clip(buried, [np.zeros(3)] * 4, [vertices] * 4, triangles, 1.0)
        self.assertEqual(result["failed"], [0, 1, 2, 3])


if __name__ == "__main__":
    unittest.main()
