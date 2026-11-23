"""The weapon-clearance rule on synthetic data: a stick through a box, turned about a pivot until it leaves."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))

from lib import tripo_clearance as C


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

    def test_a_held_weapon_under_the_bodys_lowest_point_counts_when_the_up_axis_is_given(self) -> None:
        vertices, triangles = box()
        under = np.array([[2.0, 0.0, float(vertices[:, 2].min()) - 0.1]])
        self.assertEqual(C.deep_share(under, vertices, triangles, 1.0), 0.0, "without an up axis only the body counts")
        self.assertEqual(C.deep_share(under, vertices, triangles, 1.0, ground_axis=2), 1.0)
        self.assertEqual(C.GROUND_AXIS, 2, "the grip stage's poses are Z-up")


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

    def test_the_blend_between_two_clear_poses_is_cleared_again_after_the_loop_settle(self) -> None:
        # The settle (`prepare_tripo_unit.settle_to_first`) blends the weapon arm from the clip's last pose to its first. The straight blend of two
        # poses that both clear the body (a stick up and a stick down at the pivot's side) swings the stick through the box in the middle
        # (round 4 ogre: 9 frames of the attack, up to 9.1% of the club). The clearance on the blended frames takes it out again.
        vertices, triangles = box()
        pivot = np.array([0.8, 0.0, 0.0])
        weapons, pivots, bodies = [], [], []
        for frame in range(13):
            angle = np.pi / 2 + np.pi * frame / 12  # from +y through -x to -y
            direction = np.array([np.cos(angle), np.sin(angle), 0.0])
            weapons.append(np.array([pivot + direction * 0.6 * k / 59 for k in range(60)]))
            pivots.append(pivot)
            bodies.append(vertices)
        before = [C.deep_share(w, vertices, triangles, 1.0, C.CLEAR_MARGIN_SHARE, ground_axis=C.GROUND_AXIS) for w in weapons]
        self.assertEqual(before[0], 0.0)
        self.assertEqual(before[-1], 0.0)
        self.assertGreater(max(before), 0.4)
        result = C.clear_clip(weapons, pivots, bodies, triangles, 1.0)
        self.assertEqual(result["failed"], [])
        self.assertLessEqual(max(result["after"]), C.LIMIT)
        self.assertGreater(result["frames_changed"], 0)
        size = np.linalg.norm(result["rotvecs"], axis=1)
        self.assertLess(size[0], size[6])  # the turn is largest where the blend is deepest in the body

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




def plate(grip, reach=0.5, half=0.2, count=15):
    """A flat part held at `grip` by a bar along z, reaching `reach` toward -x (a shield's crescent beside its bar)."""

    return np.array([grip + np.array([-reach * i / (count - 1), 0.0, half * (2.0 * j / (count - 1) - 1.0)]) for i in range(count) for j in range(count)])


class Staged(unittest.TestCase):
    """The order of the turns: the wrist, then the part about its own haft, then the upper arm, which never lowers a raised hand."""

    def setUp(self) -> None:
        self.vertices, self.triangles = box()

    def test_a_part_the_wrist_cannot_clear_is_rolled_about_its_bar(self) -> None:
        grip, wrist = np.array([0.8, 0.0, 0.0]), np.array([0.95, 0.0, 0.0])
        frames = [plate(grip)] * 3
        result = C.clear_clip_staged(frames, [wrist] * 3, [self.vertices] * 3, self.triangles, 1.0, grips=[grip] * 3,
                                     haft_axes=[np.array([0.0, 0.0, 1.0])] * 3, max_angle=4.0)
        self.assertGreater(max(result["before"]), 0.3)
        self.assertEqual(result["failed"], [])
        self.assertEqual(result["rolled_frames"], [0, 1, 2])
        self.assertGreater(result["max_roll_degrees"], 45.0)
        self.assertEqual(result["armed_frames"], [])
        # the roll turns about the bar: its direction is the bar's
        roll = result["rolls"][1] / np.linalg.norm(result["rolls"][1])
        self.assertAlmostEqual(abs(float(roll[2])), 1.0, places=6)

    def test_the_arm_turns_last_and_only_where_the_hand_and_the_roll_could_not(self) -> None:
        shoulder, elbow, wrist = np.array([1.0, 0.0, 0.9]), np.array([1.0, 0.0, 0.65]), np.array([0.9, 0.0, 0.42])
        frames = [stick(wrist, length=0.6, count=60)] * 3
        result = C.clear_clip_staged(frames, [wrist] * 3, [self.vertices] * 3, self.triangles, 1.0, shoulders=[shoulder] * 3,
                                     arm_joints=[np.array([elbow, wrist])] * 3, max_angle=4.0)
        self.assertGreater(max(result["before"]), 0.3)
        self.assertEqual(result["failed"], [])
        self.assertEqual(result["armed_frames"], [0, 1, 2])
        self.assertLessEqual(result["max_arm_degrees"], C.ARM_MAX_DEGREES + 1e-6)

    def test_a_clear_clip_turns_nothing_but_the_wrist(self) -> None:
        wrist = np.array([1.5, 0.0, 0.0])
        result = C.clear_clip_staged([stick(wrist)] * 2, [wrist] * 2, [self.vertices] * 2, self.triangles, 1.0, grips=[wrist] * 2,
                                     haft_axes=[np.array([1.0, 0.0, 0.0])] * 2, shoulders=[wrist + [0, 0, 0.4]] * 2,
                                     arm_joints=[np.array([wrist + [0, 0, 0.2], wrist])] * 2)
        self.assertEqual(float(np.abs(result["rolls"]).max()), 0.0)
        self.assertEqual(float(np.abs(result["arm_rotvecs"]).max()), 0.0)

    def test_the_arm_never_lowers_a_raised_hand(self) -> None:
        shoulder, elbow, wrist = np.array([1.0, 0.0, 0.2]), np.array([1.0, 0.0, 0.32]), np.array([0.9, 0.0, 0.42])
        points = stick(wrist, length=0.6, count=60)
        free = points[np.linalg.norm(points - wrist, axis=1) > C.GRIP_RADIUS_SHARE]
        for raised in (True, False):
            vector, _share = C.arm_frame(free, shoulder, np.array([elbow, wrist]), self.vertices, self.triangles, 1.0, 2, raised)
            moved = C.rotvec_matrix(vector) @ (wrist - shoulder) + shoulder
            if raised:
                self.assertGreaterEqual(moved[2], wrist[2] - C.RAISE_KEEP_SHARE - 1e-9)

    def test_a_stage_turn_grows_in_and_fades_out_and_keeps_every_solved_frame(self) -> None:
        turns = np.zeros((20, 3))
        turns[9, 2] = np.radians(60.0)
        turns[10, 2] = np.radians(15.0)
        out = C.ramp_turns(turns)
        sizes = np.degrees(np.linalg.norm(out, axis=1))
        self.assertTrue(np.all(np.abs(np.diff(sizes)) <= C.STAGE_RAMP_DEGREES + 1e-6))
        self.assertGreaterEqual(sizes[9], 60.0 - 1e-6)
        self.assertGreater(sizes[10], 15.0, "a solved frame is raised toward its neighbour, never lowered")
        self.assertEqual(C.ramp_turns(turns, last=9)[12:].tolist(), np.zeros((8, 3)).tolist())
        refused = C.ramp_turns(turns, clear=lambda frame, vector: False)
        np.testing.assert_array_equal(refused, turns)

    def test_the_roll_keeps_the_side_the_frame_before_took(self) -> None:
        grip, wrist = np.array([0.8, 0.0, 0.0]), np.array([0.95, 0.0, 0.0])
        points = plate(grip)
        free = points[np.linalg.norm(points - wrist, axis=1) > C.GRIP_RADIUS_SHARE]
        up, down = (C.roll_frame(free, grip, np.array([0.0, 0.0, 1.0]), self.vertices, self.triangles, 1.0, prefer=sign)[0] for sign in (1.0, -1.0))
        self.assertGreater(up, 0.0)
        self.assertLess(down, 0.0)

    def test_rotation_vectors_come_back_from_their_matrices(self) -> None:
        for vector in (np.zeros(3), np.array([0.3, -0.2, 0.9]), np.array([0.0, np.pi - 1e-3, 0.0])):
            np.testing.assert_allclose(C.rotvec_matrix(C.matrix_rotvec(C.rotvec_matrix(vector))), C.rotvec_matrix(vector), atol=1e-6)
        self.assertAlmostEqual(C.turn_between(np.zeros(3), np.array([0.0, 0.0, np.radians(40.0)])), 40.0, places=6)

    def test_a_jump_is_bridged_round_the_way_that_stays_clear(self) -> None:
        # frame 0 needs a turn of 60 degrees about z, frame 1 none; the straight way between them is blocked (any turn about z between 10 and
        # 50 degrees is "in the body"), so the bridge takes frame 1 round another axis, within the step of frame 0
        turns = np.array([[0.0, 0.0, np.radians(60.0)], [0.0, 0.0, 0.0]])

        def clear(frame, vector):
            about_z = abs(float(vector[2])) / max(float(np.linalg.norm(vector)), 1e-12) > 0.99
            return not (about_z and np.radians(10.0) < np.linalg.norm(vector) < np.radians(50.0))

        out = C.bridge_turns(turns, clear, [35.0])
        self.assertLessEqual(C.turn_between(out[0], out[1]), 35.0 + 1e-6)
        self.assertTrue(clear(1, out[1]))
        np.testing.assert_allclose(out[0], turns[0])
        untouched = C.bridge_turns(turns, lambda frame, vector: False, [35.0])
        np.testing.assert_array_equal(untouched, turns)

    def test_the_wrist_room_bridges_the_hands_jumps_before_the_easing_sees_them(self) -> None:
        pivot = np.array([0.8, 0.0, 0.0])
        frames = [stick(pivot, length=0.5, count=60)] * 4 + [stick(pivot + [0.9, 0, 0], length=0.5, count=60)] * 4
        pivots = [pivot] * 4 + [pivot + [0.9, 0, 0]] * 4
        loose = C.clear_clip_staged(frames, pivots, [self.vertices] * 8, self.triangles, 1.0)
        bridged = C.clear_clip_staged(frames, pivots, [self.vertices] * 8, self.triangles, 1.0, wrist_room=[10.0] * 7)
        steps = lambda r: max(C.turn_between(r["rotvecs"][i], r["rotvecs"][i + 1]) for i in range(7))
        self.assertGreater(steps(loose), 10.0)
        self.assertLessEqual(steps(bridged), 10.0 + 1e-6)
        self.assertEqual(bridged["failed"], [])

    def test_the_bridge_stops_at_its_bound_and_keeps_what_it_found(self) -> None:
        turns = np.zeros((40, 3))
        turns[::2, 2] = np.radians(60.0)  # a jump at every step
        tests = {"n": 0}

        def never(frame, vector):
            tests["n"] += 1
            return False

        budget = C.Budget(100)
        out = C.bridge_turns(turns, never, [10.0] * 39, budget=budget)
        self.assertTrue(budget.spent_out)
        self.assertLessEqual(tests["n"], 100)
        np.testing.assert_array_equal(out, turns)

    def test_no_arm_turn_puts_the_wrist_in_the_body(self) -> None:
        shoulder, elbow, wrist = np.array([0.8, 0.0, 0.9]), np.array([0.7, 0.0, 0.7]), np.array([0.6, 0.0, 0.52])
        points = stick(wrist, length=0.6, count=60)
        free = points[np.linalg.norm(points - wrist, axis=1) > C.GRIP_RADIUS_SHARE]
        vector, _share = C.arm_frame(free, shoulder, np.array([elbow, wrist]), self.vertices, self.triangles, 1.0, 2, False)
        moved = C.rotvec_matrix(vector) @ (wrist - shoulder) + shoulder
        self.assertFalse(bool(np.all(np.abs(moved) < 0.5)))


def pelvis_series() -> list:
    """Standing at 0.5, a crouch that comes back up (frames 8 to 14), a steady fall from frame 30 to a stagger and a rest at 0.05."""

    out = [0.5] * 8 + [0.5 - 0.04 * np.sin(np.pi * k / 6.0) for k in range(7)] + [0.5] * 16
    out += [0.5 - 0.45 * (k / 20.0) for k in range(21)]
    out[45] = out[44] + 0.01  # a stagger on the way down
    return out + [0.05] * 15


class SoftCloth(unittest.TestCase):
    """Cloth that a later stage swings: the weapon is kept clear of it by its swing, not only by the rigid pose's margin."""

    def setUp(self) -> None:
        self.vertices, self.triangles = box(subdivide=20)
        self.soft = self.vertices[:, 0] > 0.4  # the cloth is the +x face
        # a stick along y that lies outside the box, 2% of the height off the cloth
        self.points = np.array([[0.52, -0.3 + 0.6 * k / 39.0, 0.0] for k in range(40)])

    def test_a_weapon_outside_the_body_but_within_the_swing_of_the_cloth_counts(self) -> None:
        hard = C.deep_share(self.points, self.vertices, self.triangles, 1.0, C.CLEAR_MARGIN_SHARE)
        soft = C.deep_share(self.points, self.vertices, self.triangles, 1.0, C.CLEAR_MARGIN_SHARE, self.soft, C.SOFT_SHARE)
        self.assertEqual(hard, 0.0)
        self.assertGreater(soft, 0.9)
        self.assertEqual(C.deep_share(self.points, self.vertices, self.triangles, 1.0, C.CLEAR_MARGIN_SHARE, self.soft, 0.0), 0.0)

    def test_the_solve_turns_the_weapon_away_from_the_cloth_and_not_only_out_of_the_body(self) -> None:
        pivot = np.array([0.52, -0.3, 0.0])
        free = self.points[8:]  # outside the grip zone round the pivot
        rotation, left = C.solve_frame(free, pivot, self.vertices, self.triangles, 1.0, soft=self.soft, soft_share=C.SOFT_SHARE)
        self.assertGreater(float(np.linalg.norm(rotation)), 0.0)
        self.assertLessEqual(left, C.TARGET)
        none, _ = C.solve_frame(free, pivot, self.vertices, self.triangles, 1.0)
        self.assertEqual(float(np.linalg.norm(none)), 0.0)

    def test_a_clip_is_cleared_of_the_cloth_while_failure_is_still_the_checks_own_test(self) -> None:
        pivot = np.array([0.52, -0.3, 0.0])
        result = C.clear_clip([self.points] * 4, [pivot] * 4, [self.vertices] * 4, self.triangles, 1.0, soft=self.soft, soft_share=C.SOFT_SHARE)
        self.assertGreater(result["frames_changed"], 0)
        self.assertEqual(result["failed"], [])
        self.assertLessEqual(max(result["soft_after"]), C.LIMIT)
        plain = C.clear_clip([self.points] * 4, [pivot] * 4, [self.vertices] * 4, self.triangles, 1.0)
        self.assertEqual(plain["frames_changed"], 0)
        # a weapon buried in cloth the swing cannot clear fails by the hard test only when it is truly inside the body
        outside = C.clear_clip([self.points] * 2, [pivot] * 2, [self.vertices] * 2, self.triangles, 1.0, soft=self.soft, soft_share=0.9)
        self.assertEqual(outside["failed"], [])


class DropRules(unittest.TestCase):
    def row(self, inside=0.0, low=0.0005, moved=0.119) -> dict:
        return {"planned_weapon_inside_body_share": inside, "planned_weapon_inside_body_frame": 40, "measured": {"lowest_point_over_ground_share": low, "moved_after_landing_share": moved}}

    def test_a_weapon_that_moves_on_the_glb_is_a_diagnostic_and_does_not_fail_the_stage(self) -> None:
        problems, diagnostics = C.drop_problems(self.row())
        self.assertEqual(problems, [])
        self.assertEqual(len(diagnostics), 1)
        self.assertIn("11.9%", diagnostics[0])

    def test_a_weapon_in_the_body_or_under_the_ground_fails(self) -> None:
        self.assertEqual(len(C.drop_problems(self.row(inside=0.05))[0]), 1)
        self.assertEqual(len(C.drop_problems(self.row(low=-0.01))[0]), 1)
        self.assertEqual(C.drop_problems(self.row(moved=0.0)), ([], []))


class Fall(unittest.TestCase):
    def test_the_fall_starts_where_the_pelvis_starts_its_last_descent_not_at_a_crouch_or_a_stagger(self) -> None:
        pelvis = pelvis_series()
        still_hand = [0.8] * len(pelvis)
        start = C.fall_start_frame(pelvis, still_hand, 1.0)
        self.assertTrue(29 <= start <= 31, start)

    def test_a_hand_that_drops_before_the_pelvis_starts_the_fall_earlier(self) -> None:
        pelvis = pelvis_series()
        hand = [0.8] * 25 + [0.8 - 0.03 * k for k in range(len(pelvis) - 25)]
        start = C.fall_start_frame(pelvis, hand, 1.0)
        self.assertEqual(start, 25 + 2)  # 4% of the height is lost at the second step

    def test_a_clip_without_a_descent_has_only_the_hand_and_none_means_the_last_frame(self) -> None:
        level = [0.5] * 30
        self.assertEqual(C.fall_start_frame(level, [0.8] * 30, 1.0), 29)
        self.assertEqual(C.fall_start_frame(level, [0.8] * 10 + [0.7] * 20, 1.0), 10)


class Tumble(unittest.TestCase):
    relative = stick(np.zeros(3), length=1.0, count=30) - np.array([0.4, 0.0, 0.0])

    def test_lying_orientations_put_the_head_level_and_the_thin_axis_up(self) -> None:
        axes = np.eye(3)
        for rotation in C.lying_orientations(axes):
            self.assertAlmostEqual(float((rotation @ axes[:, 0])[2]), 0.0, places=9)
            self.assertAlmostEqual(abs(float((rotation @ axes[:, 2])[2])), 1.0, places=9)
            self.assertAlmostEqual(float(np.linalg.det(rotation)), 1.0, places=9)

    def test_the_path_starts_in_the_hand_falls_under_gravity_lands_and_stays_still(self) -> None:
        start_turn, start_point = np.eye(3), np.array([0.0, 0.0, 0.8])
        land_turn = np.eye(3)
        land_point = np.array([0.6, 0.0, 0.1])
        turns, points = C.tumble_path(start_turn, start_point, land_turn, land_point, self.relative, 0.0, 30, 10)
        self.assertTrue(np.allclose(turns[0], start_turn) and np.allclose(points[0], start_point))
        self.assertTrue(np.allclose(turns[10:], land_turn) and np.allclose(points[10:], land_point))
        drop = points[:11, 2]
        self.assertTrue(all(drop[k + 1] <= drop[k] + 1e-9 for k in range(10)))
        self.assertLess(drop[0] - drop[5], 0.5 * (drop[0] - drop[10]))  # slow at first, quick at the end

    def test_the_weapon_never_dips_under_the_ground_on_the_way(self) -> None:
        start_turn, start_point = C.rotation_matrix(np.array([0.0, 1.0, 0.0]), -np.pi / 2), np.array([0.0, 0.0, 0.6])  # standing upright
        land_turn = np.eye(3)
        land_point = np.array([0.6, 0.0, 0.01])
        turns, points = C.tumble_path(start_turn, start_point, land_turn, land_point, self.relative, 0.0, 30, 10)
        for turn, point in zip(turns, points):
            self.assertGreaterEqual(float((self.relative @ turn.T)[:, 2].min() + point[2]), -1e-9)

    def test_the_bone_pose_holds_the_weapon_on_its_world_path_whatever_the_hand_does(self) -> None:
        rng = np.random.default_rng(3)
        centre = np.array([0.3, -0.1, 0.9])
        for _ in range(5):
            attached = np.eye(4)
            attached[:3, :3] = C.rotvec_matrix(rng.normal(size=3) * 0.7)
            attached[:3, 3] = rng.normal(size=3)
            bone_rest = np.eye(4)
            bone_rest[:3, :3] = C.rotvec_matrix(rng.normal(size=3))
            bone_rest[:3, 3] = rng.normal(size=3)
            turn = C.rotvec_matrix(rng.normal(size=3))
            point = rng.normal(size=3)
            basis = C.local_pose(attached, turn, point, centre, bone_rest)
            skinned = attached @ bone_rest @ basis @ np.linalg.inv(bone_rest)  # what the skin matrix does to a rest point
            rest = rng.normal(size=(6, 3)) + centre
            moved = rest @ skinned[:3, :3].T + skinned[:3, 3]
            self.assertTrue(np.allclose(moved, (rest - centre) @ turn.T + point, atol=1e-9))


def falling_body(frames: int = 40, height: float = 1.0):
    """A box that stands for 10 frames, falls about the y axis over 20 and lies. Returns its posed vertices per frame and its triangles."""

    vertices, triangles = box()
    vertices = vertices * np.array([0.3, 0.3, height])
    poses = []
    for frame in range(frames):
        s = min(max((frame - 10) / 20.0, 0.0), 1.0)
        turned = (vertices + [0.0, 0.0, 0.5 * height]) @ C.rotation_matrix(np.array([0.0, 1.0, 0.0]), -s * np.pi / 2).T
        turned[:, 2] -= turned[:, 2].min()
        poses.append(turned)
    return poses, triangles


class Drop(unittest.TestCase):
    def plan(self, release: int = 10):
        poses, triangles = falling_body()
        centre = np.array([0.35, 0.0, 0.7])
        rest = np.array([centre + [0.0, 0.0, -0.5 + 1.06 * k / 59] for k in range(60)])
        attached = np.tile(np.eye(4), (len(poses), 1, 1))
        for frame in range(len(poses)):  # the hand falls with the body
            attached[frame, :3, 3] = [0.0, 0.0, poses[frame][:, 2].max() - 1.0]
        axes = np.eye(3)[:, [2, 0, 1]]  # head up (z), blade along x, thin axis y
        return C.plan_drop(rest, centre, axes, attached, poses, triangles, 1.0, 0.0, release, 24.0, candidates=4), poses, rest, centre

    def test_the_weapon_lands_flat_on_the_ground_clear_of_the_body_and_never_goes_under_it(self) -> None:
        plan, poses, rest, centre = self.plan()
        relative = rest - centre
        lying = relative @ plan["land_turn"].T + plan["land_point"]
        self.assertAlmostEqual(float(lying[:, 2].min()), C.GROUND_LIFT_SHARE, places=6)
        self.assertLess(float(np.ptp(lying[:, 2])), 0.2)  # level, not leaning
        self.assertGreaterEqual(plan["clearance_share"], C.LANDING_CLEAR_SHARE - 1e-9)
        for frame in range(len(plan["turns"])):
            low = float((relative @ plan["turns"][frame].T)[:, 2].min() + plan["points"][frame][2])
            self.assertGreaterEqual(low, -1e-9)
        gap = np.linalg.norm(lying[:, None, :2] - poses[-1][None, ::4, :2], axis=2).min()
        self.assertGreaterEqual(float(gap), C.LANDING_CLEAR_SHARE - 1e-6)  # clear of the final footprint, seen from above
        self.assertEqual(plan["in_body_share"], 0.0)

    def test_the_search_widens_when_the_nearest_places_all_swing_through_the_body(self) -> None:
        # Every plan for the 4 nearest places is a swing through the body (a fall onto the back); a later place is clear. The planner goes on to it
        # instead of giving up with the best of the first few.
        real = C._drop_row
        seen = []

        def faked(place, *args, **kwargs):
            row = real(place, *args, **kwargs)
            seen.append(place["orientation"])
            row = dict(row)
            row["in_body_share"] = 0.05 if len(seen) <= 4 else 0.0
            return row

        C._drop_row = faked
        try:
            plan, *_ = self.plan()
        finally:
            C._drop_row = real
        self.assertGreater(len(seen), 4)
        self.assertEqual(plan["in_body_share"], 0.0)

    def test_after_the_tumble_the_planned_weapon_does_not_move(self) -> None:
        plan, *_ = self.plan()
        tail = plan["points"][plan["tumble_frames"] :]
        self.assertTrue(np.allclose(tail, tail[0]))
        self.assertTrue(np.allclose(plan["turns"][plan["tumble_frames"] :], plan["turns"][-1]))

    def test_the_weapon_is_let_go_where_the_hand_holds_it_at_the_release_frame(self) -> None:
        plan, _poses, _rest, centre = self.plan(release=12)
        self.assertEqual(plan["release"], 12)
        self.assertEqual(len(plan["points"]), 40 - 12)
        self.assertAlmostEqual(float(plan["points"][0][0]), float(centre[0]), places=9)

    def test_every_resting_place_keeps_the_clearance_from_the_body_seen_from_above(self) -> None:
        ring = np.array([[np.cos(a), np.sin(a)] for a in np.linspace(0.0, 2 * np.pi, 80, endpoint=False)]) * 0.5
        relative = stick(np.zeros(3), length=1.0, count=20)
        orientations = C.lying_orientations(np.eye(3), steps=8)
        places = C.landing_places(relative, orientations, ring, np.array([2.0, 0.0]), 1.0)
        self.assertGreater(len(places), 0)
        self.assertEqual(places, sorted(places, key=lambda row: row["cost"]))
        for place in places:
            lying = (relative @ orientations[place["orientation"]].T)[:, :2] + place["xy"]
            gap = np.linalg.norm(lying[:, None, :] - ring[None, :, :], axis=2).min()
            self.assertGreaterEqual(float(gap), C.LANDING_CLEAR_SHARE - 0.03)  # one grid cell of rounding


if __name__ == "__main__":
    unittest.main()
