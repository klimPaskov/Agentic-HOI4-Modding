"""The Tripo checks' maths on synthetic data: no unit files, no Blender."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))
sys.path.insert(0, str(PIPELINE / "tripo"))

import tripo_checks as TC  # noqa: E402
from lib import tripo_checks as T  # noqa: E402

RADIUS = 0.019
AXIS = np.array([0.0, 0.0, 1.0])
ORIGIN = np.zeros(3)


def wrap(degrees: float, spacing: float = 0.01) -> np.ndarray:
    """Skin points on a cylinder just outside the haft (3 mm), covering `degrees` of its circumference over 6 cm."""

    points = []
    for z in np.arange(-0.03, 0.0301, spacing):
        for a in np.arange(0.0, degrees, np.degrees(spacing / (RADIUS + 0.003))):
            r = np.radians(a)
            points.append([(RADIUS + 0.003) * np.cos(r), (RADIUS + 0.003) * np.sin(r), z])
    return np.array(points)


class Enclosure(unittest.TestCase):
    def coverage(self, skin):
        return T.enclosure_share(ORIGIN, AXIS, RADIUS, skin, TC.ENCLOSURE_TOLERANCE_SHARE, TC.ENCLOSURE_HALF_LENGTH_SHARE)

    def test_a_hand_that_wraps_the_haft_passes_and_an_open_one_lying_against_it_fails(self) -> None:
        good = self.coverage(wrap(280.0))
        flat = self.coverage(wrap(60.0))
        self.assertGreater(good, 0.8)
        self.assertLess(flat, 0.4)
        self.assertGreater(good, TC.MIN_ENCLOSURE_SHARE)
        self.assertLess(flat, TC.MIN_ENCLOSURE_SHARE)

    def test_skin_far_from_the_haft_covers_nothing(self) -> None:
        self.assertEqual(self.coverage(wrap(360.0) + np.array([0.2, 0.0, 0.0])), 0.0)

    def test_an_empty_hand_covers_nothing(self) -> None:
        self.assertEqual(self.coverage(np.zeros((0, 3))), 0.0)


def plate(normal_axis: int, count: int = 400, seed: int = 1) -> np.ndarray:
    """A haft along x (2 m) with a flat head at its far end: 0.4 m by 0.3 m in the plane perpendicular to `normal_axis`."""

    rng = np.random.default_rng(seed)
    haft = np.stack([rng.uniform(0.0, 1.6, count), rng.normal(0, 0.01, count), rng.normal(0, 0.01, count)], axis=1)
    head = np.zeros((count, 3))
    head[:, 0] = rng.uniform(1.6, 2.0, count)
    other = 1 if normal_axis == 2 else 2
    head[:, other] = rng.uniform(-0.15, 0.15, count)
    head[:, normal_axis] = rng.normal(0, 0.005, count)
    return np.concatenate([haft, head])


class BladeFacing(unittest.TestCase):
    front = np.array([0.0, 0.0, 1.0])

    def test_a_blade_face_toward_the_camera_reads_near_zero_and_edge_on_near_ninety(self) -> None:
        facing, _n = T.blade_facing_degrees(plate(2), np.zeros(3), self.front)
        edge_on, _n = T.blade_facing_degrees(plate(1), np.zeros(3), self.front)
        self.assertLess(facing, 10.0)
        self.assertGreater(edge_on, 80.0)
        self.assertLess(facing, T.MAX_BLADE_FACING_DEGREES)
        self.assertGreater(edge_on, T.MAX_BLADE_FACING_DEGREES)

    def test_the_head_is_the_end_away_from_the_hand(self) -> None:
        points = plate(2)
        near, _n = T.blade_facing_degrees(points, np.array([0.0, 0.0, 0.0]), self.front)
        far, _n = T.blade_facing_degrees(points[::-1] * np.array([-1.0, 1.0, 1.0]) + np.array([2.0, 0.0, 0.0]), np.array([2.0, 0.0, 0.0]), self.front)
        self.assertLess(abs(near - far), 10.0)


class Cloak(unittest.TestCase):
    def setUp(self) -> None:
        # Two rows of vertices: the body's front (kept out) and a cloak behind it, hanging from 0.8 to 0.3 of a 1.0 body.
        self.front = np.array([0.0, 0.0, 1.0])
        self.hips = np.array([0.0, 0.5, 0.0])
        rows = np.linspace(0.3, 0.8, 6)
        self.cloak = np.array([[x, y, -0.15] for y in rows for x in (-0.1, 0.0, 0.1)])
        self.body = np.array([[x, y, 0.05] for y in rows for x in (-0.1, 0.0, 0.1)])
        self.positions = np.concatenate([self.cloak, self.body, [[0.0, 0.0, 0.0], [0.0, 1.0, 0.0]]])
        self.dominant = ["Spine"] * len(self.positions)

    def test_the_region_is_what_hangs_behind_the_body_between_the_bones_and_heights(self) -> None:
        mask = T.cloak_region(self.positions, self.dominant, self.hips, self.front, 1.0, ["Spine"])
        self.assertEqual(int(mask[: len(self.cloak)].sum()), len(self.cloak))
        self.assertFalse(mask[len(self.cloak):].any())
        other = T.cloak_region(self.positions, ["Head"] * len(self.positions), self.hips, self.front, 1.0, ["Spine"])
        self.assertFalse(other.any())

    def test_stretch_counts_the_region_edges_a_clip_pulls_apart(self) -> None:
        mask = np.zeros(len(self.positions), dtype=bool)
        mask[: len(self.cloak)] = True
        edges = np.array([[i, i + 1] for i in range(0, len(self.cloak) - 1, 3)] + [[i, i + 1] for i in range(1, len(self.cloak) - 1, 3)])
        still = self.positions.copy()
        pulled = self.positions.copy()
        pulled[0] = pulled[0] + np.array([-0.5, 0.0, 0.0])  # drag one corner far away
        share, frame = T.region_stretch_share(self.positions, [still, pulled], edges, mask, 1.0)
        self.assertEqual(frame, 1)
        self.assertGreater(share, 0.0)
        calm, _ = T.region_stretch_share(self.positions, [still], edges, mask, 1.0)
        self.assertEqual(calm, 0.0)
        # an edge outside the region is not counted
        outside = np.zeros(len(self.positions), dtype=bool)
        self.assertEqual(T.region_stretch_share(self.positions, [pulled], edges, outside, 1.0)[0], 0.0)

    def test_the_vanilla_limit_is_the_worst_vanilla_share_with_a_margin(self) -> None:
        self.assertGreaterEqual(TC.CLOAK_MAX_STRETCH_SHARE, TC.VANILLA_CLOAK_WORST)
        self.assertLessEqual(TC.CLOAK_MAX_STRETCH_SHARE, 3.0 * TC.VANILLA_CLOAK_WORST)


class LimbInTorso(unittest.TestCase):
    def setUp(self) -> None:
        # A unit cube of torso vertices (8 corners, 12 triangles) and a row of limb vertices.
        corners = np.array([[x, y, z] for x in (0.0, 1.0) for y in (0.0, 1.0) for z in (0.0, 1.0)])
        quads = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
        triangles = [[a, b, c] for a, b, c, d in quads] + [[a, c, d] for a, b, c, d in quads]
        self.limb_points = np.array([[0.5, 0.5, z] for z in np.linspace(-1.0, 0.5, 20)])
        self.positions = np.concatenate([corners, self.limb_points])
        self.triangles = np.array(triangles)
        self.torso = np.zeros(len(self.positions), bool)
        self.torso[:8] = True
        self.limb = ~self.torso

    def test_a_limb_poking_deep_into_the_torso_is_counted_and_one_outside_is_not(self) -> None:
        inside = TC.limb_torso_core([self.positions], self.triangles, self.torso, self.limb, 10.0, margin_share=0.01)[0]
        self.assertGreater(inside, 0.05)
        outside = self.positions.copy()
        outside[8:, 2] -= 5.0
        self.assertEqual(TC.limb_torso_core([outside], self.triangles, self.torso, self.limb, 10.0)[0], 0.0)

    def test_the_death_limits_are_named_constants(self) -> None:
        self.assertGreater(TC.MAX_FINAL_EXTENT_SHARE, 0.3)
        self.assertGreaterEqual(TC.MAX_LIMB_IN_TORSO_SHARE, 0.055)  # the worst frame of a vanilla death clip
        self.assertEqual(TC.MAX_TORSO_VERTICAL_SHARE, 0.5)


class Thresholds(unittest.TestCase):
    def test_the_weapon_in_body_thresholds_are_the_strict_ones(self) -> None:
        import clip_check

        self.assertLess(TC.PENETRATION_MARGIN_SHARE, clip_check.PENETRATION_MARGIN_SHARE)
        self.assertLess(TC.MAX_IN_BODY_SHARE, clip_check.MAX_IN_BODY_SHARE)

    def test_a_clip_is_judged_per_frame_not_on_samples(self) -> None:
        # one bad frame in the series is enough: the finding lists the frames over the limit
        series = [0.0] * 30 + [3.0] + [0.0] * 30
        limit = 100 * TC.MAX_IN_BODY_SHARE
        self.assertEqual([i for i, value in enumerate(series) if value > limit], [30])


if __name__ == "__main__":
    unittest.main()
