"""The grip stage's maths: curl to contact, finger gaps, and the arm-hold solve."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))

import numpy as np  # noqa: E402

from lib import tripo_grip as G  # noqa: E402

Z = np.array([0.0, 0.0, 1.0])
Y = np.array([0.0, 1.0, 0.0])


class Rotations(unittest.TestCase):
    def test_a_quarter_turn_about_z_takes_x_to_y(self) -> None:
        turned = G.rodrigues(Z, np.pi / 2) @ np.array([1.0, 0.0, 0.0])
        self.assertTrue(np.allclose(turned, [0, 1, 0], atol=1e-9))

    def test_line_distance_is_perpendicular_distance(self) -> None:
        d = G.line_distance(np.array([[3.0, 4.0, 9.0]]), np.zeros(3), Z)
        self.assertAlmostEqual(float(d[0]), 5.0)


class Contact(unittest.TestCase):
    chain = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]])

    def test_the_finger_turns_until_it_touches_and_stops_there(self) -> None:
        # A haft along z through (0.6, 0.5): the finger, turning about z toward +y, reaches it.
        point, radius = np.array([0.6, 0.5, 0.0]), 0.1
        angle, why = G.contact_angle(self.chain, Z, point, Z, radius, 90.0)
        self.assertEqual(why, "contact")
        self.assertGreater(angle, 0.0)

        def nearest(a: float) -> float:
            moved = G.rotate_about(G.segment_points(self.chain), np.zeros(3), Z, a)
            return float(G.line_distance(moved, point, Z).min())

        self.assertGreaterEqual(nearest(angle), radius - 1e-9)
        self.assertLess(nearest(angle + np.radians(0.5)), radius)

    def test_no_haft_in_reach_leaves_the_joint_at_its_limit(self) -> None:
        angle, why = G.contact_angle(self.chain, Z, np.array([0.0, 9.0, 0.0]), Z, 0.1, 40.0)
        self.assertEqual(why, "open")
        self.assertAlmostEqual(np.degrees(angle), 40.0, places=1)

    def test_a_chain_already_inside_the_clearance_does_not_turn(self) -> None:
        angle, why = G.contact_angle(self.chain, Z, np.array([0.5, 0.0, 0.0]), Z, 0.1, 90.0)
        self.assertEqual((angle, why), (0.0, "inside"))


class Curl(unittest.TestCase):
    def test_a_three_joint_finger_wraps_a_haft_without_entering_it(self) -> None:
        joints = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [2.0, 0.0, 0.0], [3.0, 0.0, 0.0]])
        # A haft along y, 0.8 below the finger and 1.6 along it: fingers curl in the x-z plane toward -z.
        point, radius, finger = np.array([1.6, 0.0, -0.8]), 0.3, [0.05, 0.05, 0.05]
        result = G.curl_chain(joints, point, Y, radius, finger, limits_degrees=(80.0, 100.0, 90.0))
        self.assertGreater(result["angles"][0], 0.0)
        self.assertIn("contact", result["why"])
        clearance = radius + 0.05
        reach = G.line_distance(G.segment_points(result["joints"]), point, Y).min()
        self.assertGreaterEqual(float(reach), clearance - 2e-3)
        # The tip came round toward the haft's side of the finger line.
        self.assertLess(float(result["joints"][-1][2]), -0.5)

    def test_finger_gaps_report_penetration_negative_and_the_tip_gap(self) -> None:
        ring = np.array([[0.31, 0.0, 0.0], [0.0, 0.31, 0.0], [-0.29, 0.0, 0.0]])
        report = G.finger_gaps({"index": ring}, {"index": np.array([0.31, 0.0, 0.0])}, np.zeros(3), Z, 0.3, 1.0)
        self.assertAlmostEqual(report["index"]["deepest"], -0.01, places=6)
        self.assertAlmostEqual(report["index"]["tip_gap"], 0.01, places=6)
        self.assertEqual(G.finger_gaps({"x": ring + [0, 0, 5]}, {"x": ring[0]}, np.zeros(3), Z, 0.3, 1.0)["x"]["vertices"], 0)

    def test_the_haft_radius_is_read_from_the_vertices_near_the_grip(self) -> None:
        angles = np.linspace(0, 2 * np.pi, 40, endpoint=False)
        shaft = np.stack([0.02 * np.cos(angles), 0.02 * np.sin(angles), np.zeros(40)], axis=1)
        column = np.vstack([shaft + [0, 0, z] for z in np.linspace(0.0, 1.0, 20)] + [np.array([[0.2, 0.0, 0.1]] * 3)])
        self.assertAlmostEqual(G.haft_radius(column, np.zeros(3), Z, 0.5, 0.1), 0.02, places=6)


class Hold(unittest.TestCase):
    @staticmethod
    def arm(params: np.ndarray):
        """Two links of length 1 in the x-y plane; the haft points along the hand's x axis."""

        a, b = params
        elbow = np.array([np.cos(a), np.sin(a), 0.0])
        hand = elbow + np.array([np.cos(a + b), np.sin(a + b), 0.0])
        return hand, np.array([np.cos(a + b), np.sin(a + b), 0.0])

    def test_the_solve_finds_the_joint_angles_that_reach_the_target(self) -> None:
        target, direction = self.arm(np.array([0.5, 0.7]))
        found = G.solve_hold(self.arm, [np.zeros(2)], target, direction, scale=1.0, ridge=1e-8)
        self.assertLess(found["position_error"], 1e-3)
        self.assertLess(found["direction_error_degrees"], 0.2)
        self.assertTrue(np.allclose(found["params"], [0.5, 0.7], atol=2e-3))

    def test_the_cheapest_of_several_starts_wins_and_ridge_prefers_small_turns(self) -> None:
        target, direction = self.arm(np.array([0.2, 0.3]))
        found = G.solve_hold(self.arm, [np.array([3.0, -3.0]), np.zeros(2)], target, direction, scale=1.0, ridge=1e-3)
        self.assertLess(float(np.abs(found["params"]).max()), 1.0)




class SkinCurl(unittest.TestCase):
    def test_a_finger_skin_closes_on_a_haft_and_never_enters_it(self) -> None:
        # A finger along +x with its skin (a thick line of points), over a haft along y at (1.3, 0, -0.9).
        joints = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [2.0, 0.0, 0.0], [3.0, 0.0, 0.0]])
        xs = np.linspace(0.0, 3.4, 60)
        skin = np.array([[x, y, z] for x in xs for y, z in ((0.0, 0.1), (0.0, -0.1), (0.1, 0.0), (-0.1, 0.0))])
        level = np.minimum((skin[:, 0] // 1.0).astype(int), 3)
        result = G.curl_skin(joints, skin, level, np.array([1.3, 0.0, -0.9]), Y, 0.4, limits_degrees=(70.0, 100.0, 90.0))
        reach = float(G.line_distance(result["skin"], np.array([1.3, 0.0, -0.9]), Y).min())
        self.assertGreaterEqual(reach, 0.4 - 1e-6)
        self.assertGreater(result["angles"][0], 0.0)
        self.assertIn("contact", result["why"])
        # The distal skin has come round toward the haft (it started on z = 0).
        self.assertLess(float(result["skin"][-1][2]), -0.3)

    def test_a_joint_with_no_skin_beyond_it_stays_put(self) -> None:
        joints = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [2.0, 0.0, 0.0], [3.0, 0.0, 0.0]])
        skin = np.array([[0.5, 0.0, 0.0], [0.8, 0.0, 0.0]])
        result = G.curl_skin(joints, skin, np.array([0, 0]), np.array([0.5, 0.0, -0.9]), Y, 0.3)
        self.assertEqual(result["why"][1:], ["no skin", "no skin"])
        self.assertEqual(result["angles"][1:], [0.0, 0.0])


def finger_chain(base, direction, lengths, radius=0.009, ring=8, along=4):
    """Joints (4, 3), skin ring points and their bone levels for a straight finger."""

    d = G.unit(direction)
    side = G.unit(np.cross(d, Z))
    up = np.cross(side, d)
    joints = [np.array(base, float)]
    for length in lengths:
        joints.append(joints[-1] + d * length)
    joints = np.array(joints)
    points, levels = [], []
    for i in range(3):
        for t in np.linspace(0, 1, along):
            centre = joints[i] + (joints[i + 1] - joints[i]) * t
            for a in np.linspace(0, 2 * np.pi, ring, endpoint=False):
                points.append(centre + radius * (np.cos(a) * side + np.sin(a) * up))
                levels.append(i)
    for a in np.linspace(0, 2 * np.pi, ring, endpoint=False):
        points.append(joints[3] + 0.7 * radius * (np.cos(a) * side + np.sin(a) * up))
        levels.append(3)
    points.append(joints[3] + d * radius)
    levels.append(3)
    return joints, np.array(points), np.array(levels)


class PowerGrip(unittest.TestCase):
    forward = np.array([1.0, 0.0, 0.0])
    closing = Y
    palm = Z
    radius = 0.019
    centre = np.array([0.012, 0.0, 0.035])

    def haft(self):
        phi = np.radians(35.0)
        return G.unit(-self.closing * np.cos(phi) + self.forward * np.sin(phi))

    def finger(self, y):
        joints, skin, level = finger_chain([0.0, y, 0.0], self.forward, (0.04, 0.028, 0.022))
        result = G.solve_finger(joints, skin, level, self.centre, self.haft(), self.radius, self.closing, self.palm, 0.0015)
        return result, level

    def test_a_finger_wraps_with_all_three_joints_bent_and_nothing_inside_the_haft(self) -> None:
        result, level = self.finger(0.04)
        degrees = np.degrees(result["angles"])
        for angle, (low, high) in zip(degrees, G.FINGER_RANGE_DEGREES):
            self.assertGreaterEqual(angle, low - 1e-6)
            self.assertLessEqual(angle, high + 1e-6)
        self.assertTrue((degrees >= 40.0).all(), degrees)
        gap = G.signed_gaps(result["skin"], self.centre, self.haft(), self.radius)
        self.assertGreaterEqual(float(gap.min()), -0.0016)
        self.assertLess(float(gap[level == 3].min()), 0.004)

    def test_the_thumb_closes_from_the_side_opposite_the_fingers_and_stays_out_of_the_haft(self) -> None:
        d = self.haft()
        middle, middle_level = self.finger(0.04)
        index, index_level = self.finger(0.03)
        obstacles = np.concatenate([middle["skin"], index["skin"]])
        joints, skin, level = finger_chain([0.0, -0.03, 0.01], [0.6, 0.6, 0.4], (0.03, 0.025, 0.02), radius=0.011)
        finger_tip = middle["skin"][middle_level == 3].mean(axis=0)
        away = G.radial_unit(finger_tip, self.centre, d)
        middle_segments = np.concatenate([middle["skin"][middle_level == 1], index["skin"][index_level == 1]])
        thumb = G.solve_thumb(joints, skin, level, self.centre, d, self.radius, obstacles, target_skin=middle_segments, away_from=away)
        gap = G.signed_gaps(thumb["skin"], self.centre, d, self.radius)
        self.assertGreaterEqual(float(gap.min()), -0.0006)  # no part of the thumb inside the haft
        self.assertLess(float(gap[level >= 2].min()), 0.004)  # the pad is on it
        tip = thumb["skin"][level == 3].mean(axis=0)
        self.assertGreater(G.opposite_sides([finger_tip], tip, self.centre, d), 100.0)

    def test_the_sides_of_a_haft_are_measured_around_its_axis(self) -> None:
        d = np.array([0.0, 0.0, 1.0])
        origin = np.zeros(3)
        self.assertAlmostEqual(G.opposite_sides([np.array([1.0, 0.0, 5.0])], np.array([-1.0, 0.0, -3.0]), origin, d), 180.0, places=6)
        self.assertAlmostEqual(G.opposite_sides([np.array([1.0, 0.0, 5.0])], np.array([1.0, 0.2, -3.0]), origin, d), np.degrees(np.arctan(0.2)), places=4)
        self.assertAlmostEqual(G.radial_angle(np.array([0.0, 1.0, 2.0]), origin, d, np.array([1.0, 0.0, 0.0])), 90.0, places=6)


class PivotTurn(unittest.TestCase):
    def test_the_axis_and_angle_of_a_rotation_are_recovered(self) -> None:
        axis = G.unit(np.array([1.0, 2.0, -0.5]))
        for angle in (0.3, 1.5, 3.0, 3.14159):
            found_axis, found_angle = G.rotation_axis_angle(G.rodrigues(axis, angle))
            self.assertAlmostEqual(found_angle, angle, places=4)
            self.assertAlmostEqual(abs(float(found_axis @ axis)), 1.0, places=4)
        self.assertEqual(G.rotation_axis_angle(np.eye(3))[1], 0.0)

    def test_a_turn_about_a_pivot_is_found_and_reproduces_the_motion(self) -> None:
        pivot = np.array([0.4, -0.2, 0.7])
        rotation = G.rodrigues(G.unit(np.array([0.2, 1.0, 0.3])), 1.9)
        translation = (np.eye(3) - rotation) @ pivot
        found = G.pivot_for_motion(rotation, translation, near=np.array([0.0, 0.0, 0.0]))
        points = np.random.default_rng(3).normal(size=(20, 3))
        moved_by_pivot = (points - found) @ rotation.T + found
        self.assertTrue(np.allclose(moved_by_pivot, points @ rotation.T + translation, atol=1e-9))

    def test_a_motion_along_the_axis_has_no_pivot_and_the_pivot_nearest_a_point_is_chosen(self) -> None:
        axis = np.array([0.0, 0.0, 1.0])
        rotation = G.rodrigues(axis, 1.0)
        self.assertIsNone(G.pivot_for_motion(rotation, np.array([0.0, 0.0, 0.5]), np.zeros(3)))
        translation = (np.eye(3) - rotation) @ np.array([1.0, 2.0, 0.0])
        found = G.pivot_for_motion(rotation, translation, near=np.array([5.0, 5.0, 3.0]))
        self.assertAlmostEqual(float(found[2]), 3.0, places=9)  # slid along the axis to the nearest point


if __name__ == "__main__":
    unittest.main()
