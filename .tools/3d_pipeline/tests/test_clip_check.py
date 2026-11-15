"""The Tripo clip check's maths on tiny synthetic meshes: no orc files, no Blender."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE / "tripo"))

import clip_check


def box(lo=(-1.0, -1.0, -1.0), hi=(1.0, 1.0, 1.0)) -> np.ndarray:
    """A closed box as 12 triangles, shape (12, 3, 3)."""

    x0, y0, z0 = lo
    x1, y1, z1 = hi
    v = np.array([[x, y, z] for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)], dtype=float)
    quads = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    tris = []
    for a, b, c, d in quads:
        tris.append([v[a], v[b], v[c]])
        tris.append([v[a], v[c], v[d]])
    return np.array(tris)


def stick(start, end, count=21) -> np.ndarray:
    return np.linspace(np.asarray(start, float), np.asarray(end, float), count)


class InsideTest(unittest.TestCase):
    def test_points_in_and_out_of_a_box(self) -> None:
        inside = clip_check.points_inside_mesh(np.array([[0, 0, 0], [0.5, -0.5, 0.3], [2, 0, 0], [0, 3, 0], [0, 0, -1.5]]), box())
        self.assertEqual(inside.tolist(), [True, True, False, False, False])

    def test_reversed_faces_do_not_change_the_answer(self) -> None:
        tris = box()
        tris[::2] = tris[::2][:, ::-1]
        inside = clip_check.points_inside_mesh(np.array([[0, 0, 0], [3, 0, 0]]), tris)
        self.assertEqual(inside.tolist(), [True, False])

    def test_a_box_with_a_missing_face_still_holds_its_centre(self) -> None:
        tris = box()
        holed = np.concatenate([tris[:10], tris[11:]])  # drop one triangle of the last face
        inside = clip_check.points_inside_mesh(np.array([[-0.3, -0.2, -0.1], [3.0, 0, 0]]), holed)
        self.assertEqual(inside.tolist(), [True, False])

    def test_empty_input(self) -> None:
        self.assertEqual(clip_check.points_inside_mesh(np.zeros((0, 3)), box()).shape, (0,))
        self.assertFalse(clip_check.points_inside_mesh(np.zeros((2, 3)), np.zeros((0, 3, 3))).any())


class GripAndVerdict(unittest.TestCase):
    def test_grip_zone_is_a_sphere_around_the_hand(self) -> None:
        pts = stick((0, 0, 0), (0, 2, 0), 5)
        mask = clip_check.grip_zone_mask(pts, np.array([0, 0, 0]), 0.6)
        self.assertEqual(mask.tolist(), [True, True, False, False, False])

    def weapon_share(self, points, hand, radius=0.5) -> float:
        body = box()
        free = ~clip_check.grip_zone_mask(points, hand, radius)
        if not free.any():
            return 0.0
        return float(clip_check.points_inside_mesh(points[free], body).mean())

    def test_stick_outside_passes(self) -> None:
        share = self.weapon_share(stick((2, -1, 0), (2, 1, 0)), np.array([2, 0, 0]))
        self.assertEqual(share, 0.0)
        self.assertEqual(clip_check.clip_verdict(share, 0.0, 0.0)["verdict"], "pass")

    def test_stick_through_the_box_fails(self) -> None:
        points = stick((0, 0, 0), (4, 0, 0), 41)  # starts in the middle of the box, hand at the far end
        share = self.weapon_share(points, np.array([4, 0, 0]))
        self.assertGreater(share, clip_check.MAX_IN_BODY_SHARE)
        verdict = clip_check.clip_verdict(share, 0.0, 0.0)
        self.assertEqual(verdict["verdict"], "fail")
        self.assertTrue(verdict["reasons"])

    def test_stick_only_inside_the_grip_radius_passes(self) -> None:
        points = stick((0, 0, 0), (0.4, 0, 0), 9)  # all inside the box and within 0.5 of the hand
        self.assertTrue(clip_check.points_inside_mesh(points, box()).all())
        self.assertEqual(self.weapon_share(points, np.array([0.2, 0, 0])), 0.0)

    def test_depth_is_distance_to_the_nearest_vertex(self) -> None:
        depth = clip_check.nearest_vertex_distance(np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.5]]), box().reshape(-1, 3))
        self.assertAlmostEqual(float(depth[0]), 3 ** 0.5, places=6)
        self.assertAlmostEqual(float(depth[1]), 0.5, places=6)

    def test_verdict_reasons_and_thresholds(self) -> None:
        self.assertEqual(clip_check.clip_verdict(0.02, 0.0, 0.0)["verdict"], "pass")
        self.assertEqual(clip_check.clip_verdict(0.0, 0.5, 0.0)["verdict"], "fail")
        self.assertEqual(clip_check.clip_verdict(0.0, 0.0, 50.0)["verdict"], "fail")
        both = clip_check.clip_verdict(0.1, 0.1, 0.0)
        self.assertEqual(len(both["reasons"]), 2)

    def test_hand_joint_names(self) -> None:
        names = ["mixamorig:Hips", "mixamorig:RightHand", "mixamorig:RightHandIndex1", "mixamorig:LeftHand"]
        self.assertEqual(clip_check.hand_joint_indices(names), [1, 3])
        rest = np.array([[0, 0, 0], [1, 0, 0], [1.1, 0, 0], [-1, 0, 0]], float)
        weapon = np.array([[0.8, 0, 0], [0.9, 0, 0]])
        self.assertEqual(clip_check.resolve_weapon_joint(names, weapon, rest), 1)
        self.assertEqual(clip_check.resolve_weapon_joint(names, weapon, rest, "LeftHand"), 3)


if __name__ == "__main__":
    unittest.main()
