"""The Tripo checks' maths on synthetic data: no unit files, no Blender."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))
sys.path.insert(0, str(PIPELINE / "tripo"))

import tripo_checks as TC
from lib import tripo_checks as T

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


def club(count: int = 1500, seed: int = 3) -> np.ndarray:
    """A haft along x with a thick, near-round head at the far end (spreads 0.72 thinnest to middle, as the round 4 ogre's club)."""

    rng = np.random.default_rng(seed)
    haft = np.stack([rng.uniform(0.0, 1.6, count), rng.normal(0, 0.01, count), rng.normal(0, 0.01, count)], axis=1)
    head = np.stack([rng.uniform(1.6, 2.0, count // 4), rng.normal(0, 0.12, count // 4), rng.normal(0, 0.088, count // 4)], axis=1)
    return np.concatenate([haft, head])


class FlatHead(unittest.TestCase):
    front = np.array([0.0, 0.0, 1.0])

    def test_a_blade_is_flat_and_a_club_is_round(self) -> None:
        _h, _n, blade = T.blade_head(plate(2), np.zeros(3))
        _h, _n, round_head = T.blade_head(club(), np.zeros(3))
        self.assertLess(blade, T.MAX_FACE_FLATNESS)
        self.assertGreater(round_head, T.MAX_FACE_FLATNESS)
        self.assertLess(blade, 0.41)
        self.assertGreater(round_head, 0.65)

    def test_the_head_is_the_end_with_the_broad_cross_section_whichever_end_the_hand_holds(self) -> None:
        points = plate(2)
        near_hand = T.blade_facing_degrees(points, np.array([1.8, 0.0, 0.0]), self.front)[0]
        far_hand = T.blade_facing_degrees(points, np.array([0.0, 0.0, 0.0]), self.front)[0]
        self.assertAlmostEqual(near_hand, far_hand, places=3)
        self.assertLess(near_hand, 10.0)

    def judged(self, points: np.ndarray):
        """TRIPO-BLADE-FACING on a unit whose only weapon-bone vertices are `points` (the pose functions stubbed)."""

        from types import SimpleNamespace
        from unittest import mock

        count = len(points)
        mesh = SimpleNamespace(bones=["RightHand", "Weapon"], parents=[-1, 0], weights=np.ones((count, 1)), joints=np.ones((count, 1), int), height=1.0)
        idle = SimpleNamespace(frames=1)
        with mock.patch.object(TC.pdx_deform, "dominant_bones", lambda _m: np.ones(count, int)),                 mock.patch.object(TC, "posed_frames", lambda _m, _a, step=1: [points]),                 mock.patch.object(TC.pdx_motion, "posed_joints", lambda _m, _a: np.zeros((1, 2, 3))),                 mock.patch.object(TC, "front_direction", lambda _m: self.front):
            return TC.blade_findings(mesh, {"unit_idle": idle}, "Weapon")

    def test_a_round_head_is_not_judged_and_a_flat_edge_on_blade_still_fails(self) -> None:
        findings, numbers = self.judged(club())
        self.assertEqual(findings, [])
        self.assertFalse(numbers["judged"])
        self.assertGreater(numbers["head_flatness"], TC.MAX_FACE_FLATNESS)
        findings, numbers = self.judged(plate(1))
        self.assertEqual([f["rule"] for f in findings], ["TRIPO-BLADE-FACING"])
        self.assertLess(numbers["head_flatness"], TC.MAX_FACE_FLATNESS)
        self.assertEqual(self.judged(plate(2))[0], [])


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

    def _block_body(self, depth: float):
        """A 1-unit-tall body: a torso block (Spine) `depth` deep and 0.5 wide, on two legs (LeftLeg)."""

        from types import SimpleNamespace
        corners = np.array([[x, y, z] for x in (-0.25, 0.25) for y in (0.5, 1.0) for z in (-depth / 2, depth / 2)])
        legs = np.array([[x, y, 0.0] for x in (-0.1, 0.1) for y in (0.0, 0.5)])
        positions = np.vstack([corners, legs])
        joints = np.array([[0, 0, 0, 0]] * len(corners) + [[1, 0, 0, 0]] * len(legs))
        weights = np.array([[1.0, 0, 0, 0]] * len(positions))
        return SimpleNamespace(bones=["Spine", "LeftLeg"], positions=positions, joints=joints, weights=weights, collision=np.zeros(len(positions), bool))

    def test_a_thick_body_gets_its_extra_torso_thickness_on_top_of_the_lying_limit(self) -> None:
        human, ogre = self._block_body(0.2), self._block_body(0.4)
        self.assertAlmostEqual(TC.torso_thickness_share(human), 0.2, places=3)
        self.assertAlmostEqual(TC.final_extent_limit(human), TC.MAX_FINAL_EXTENT_SHARE, places=3)
        self.assertAlmostEqual(TC.final_extent_limit(ogre), TC.MAX_FINAL_EXTENT_SHARE + 0.4 - TC.HUMAN_TORSO_THICKNESS_SHARE, places=3)
        self.assertGreater(TC.final_extent_limit(ogre), 0.51)  # the ogre lay flat at 51% of its standing height

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
