"""The winged quadruped (adapter/quadruped_wings.py and the winged styles of adapter/quadruped_layout.py), without Blender: a tail lying on
the ground is not a foot, the feet set the long axis, the wings are found by rule and fanned into chains, their poses are reached from the
rest frame, the clips the game loops start where they end, the dead body comes to rest by rule, and the checks find the wings by their
bones."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

import numpy as np

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE / "adapter"))
sys.path.insert(0, str(PIPELINE))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import quadruped_layout as ql
import quadruped_wings as qw
from test_quadruped_ears import _box


def _dragon(wing_reach: float = 1.6):
    """A blocky dragon facing -Y: four legs, a torso 0.35 wide each side, a neck and head, a tail lying on the ground behind it and a wing
    plate each side of the shoulders reaching `wing_reach` from the mid-plane (0.02 thick, overlapping the torso so it is one skin there)."""

    parts = [((x - 0.08, y - 0.08, 0.0), (x + 0.08, y + 0.08, 1.0), 8) for x in (-0.22, 0.22) for y in (0.0, 1.6)]
    parts.append(((-0.35, -0.2, 1.0), (0.35, 1.8, 1.6), 8))
    parts.append(((-0.15, -0.7, 1.3), (0.15, -0.2, 1.8), 8))
    parts.append(((-0.04, 2.25, 0.0), (0.04, 3.6, 0.05), (2, 16, 1)))  # the tail, lying on the ground
    parts.append(((-0.04, 1.8, 0.3), (0.04, 2.25, 1.2), (2, 4, 8)))  # the tail's root, down from the rump
    parts.append(((-0.04, 2.2, 0.05), (0.04, 2.25, 0.3), (2, 1, 4)))
    parts.append(((0.25, 0.0, 1.3), (wing_reach, 0.02, 2.2), (16, 1, 10)))
    parts.append(((-wing_reach, 0.0, 1.3), (-0.25, 0.02, 2.2), (16, 1, 10)))
    points, triangles = [], []
    for lo, hi, steps in parts:
        p, t = _box(lo, hi, steps)
        triangles.append(t + sum(len(x) for x in points))
        points.append(p)
    return np.vstack(points), np.vstack(triangles)


def _found():
    points, triangles = _dragon()
    first = ql.detect_landmarks(points)
    feet, _dragged = ql.ground_contacts(points)
    plans, masks = qw.detect_wings(points, triangles, first, feet)
    wing = masks["Left"] | masks["Right"]
    landmarks = ql.detect_landmarks(points[~wing])
    landmarks["wings"] = plans
    return points, triangles, landmarks, plans, masks


class Ground(unittest.TestCase):
    def test_a_tail_lying_on_the_ground_is_not_a_foot(self) -> None:
        points, _triangles = _dragon()
        feet, dragged = ql.ground_contacts(points)
        self.assertEqual(len(feet), 4)
        self.assertEqual(len(dragged), 1)
        self.assertGreater(float(dragged[0][:, 1].min()), 2.0, "the dragged piece is the tail")
        landmarks = ql.detect_landmarks(points)
        self.assertLess(abs(landmarks["rear_y"] - 1.6), 0.1, "the tail does not pull the rear feet back")
        self.assertIsNotNone(landmarks["tail_ground_y"])

    def test_four_pieces_on_the_ground_are_four_feet(self) -> None:
        points, _triangles = _box((0, 0, 0), (1, 1, 1))
        feet, dragged = ql.ground_contacts(points)
        self.assertEqual(dragged, [])

    def test_the_feet_set_the_long_axis(self) -> None:
        points, _triangles = _dragon()
        self.assertFalse(ql.feet_axis_along_x(points))
        turned = np.c_[points[:, 1], -points[:, 0], points[:, 2]]
        self.assertTrue(ql.feet_axis_along_x(turned), "spread wings wider than the body do not decide it")


class Legs(unittest.TestCase):
    def test_a_curled_tail_does_not_move_the_mid_plane(self) -> None:
        points, _triangles = _dragon()
        curl = _box((0.0, 3.55, 0.0), (0.9, 3.6, 0.05), (8, 1, 1))[0]  # the tail tip curls aside on the ground
        landmarks = ql.detect_landmarks(np.vstack([points, curl]))
        self.assertLess(abs(landmarks["centre_x"]), 0.02, "the feet set the mid-plane")

    def test_no_leg_is_thinner_than_half_the_median(self) -> None:
        points, _triangles = _dragon()
        landmarks = ql.detect_landmarks(points)
        radii = [float(joints["radius"]) for joints in landmarks["legs"].values()]
        self.assertGreaterEqual(min(radii), 0.5 * float(np.median(radii)) - 1e-12)

    def test_the_neck_never_takes_leg_skin(self) -> None:
        _points, _triangles, landmarks, _plans, _masks = _found()
        points, _triangles = _dragon()
        layout = ql.build_layout(landmarks)
        indices, weights = ql.skin_weights(points, layout)
        names = np.array(layout.names())
        neck = np.where(np.isin(names[indices], ["Neck_01", "Neck_02", "Head"]), weights, 0.0).sum(axis=1)
        legs = points[:, 2] < 0.9
        self.assertTrue((neck[legs] < 1e-9).all())


class FindWings(unittest.TestCase):
    def test_the_far_plates_are_the_wings(self) -> None:
        points, triangles, landmarks, plans, masks = _found()
        self.assertEqual(set(plans), {"Left", "Right"})
        for side, sign in (("Left", 1.0), ("Right", -1.0)):
            mask = masks[side]
            plate = (points[:, 0] * sign > 0.5) & (points[:, 1] < 0.03) & (points[:, 1] > -0.01) & (points[:, 2] > 1.29)
            self.assertTrue((mask >= plate).all(), "the far plate is wing")
            self.assertFalse((mask & (points[:, 2] < 1.0)).any(), "no leg, tail or foot")
            plan = plans[side]
            self.assertLess(abs(plan["root"][0] * sign - 0.345), 0.1, "the root is where the wing leaves the body's side")
            self.assertEqual(np.asarray(plan["joints"]).shape, (qw.WING_CHAINS, qw.WING_BONES + 1, 3))
            self.assertGreater(plan["length"], 1.0)
        self.assertEqual(len(ql.build_layout(landmarks).bones), 27 + 2 * qw.WING_CHAINS * qw.WING_BONES)

    def test_no_wing_on_a_plain_quadruped(self) -> None:
        points, triangles = _dragon(0.3)
        first = ql.detect_landmarks(points)
        feet, _dragged = ql.ground_contacts(points)
        plans, masks = qw.detect_wings(points, triangles, first, feet)
        self.assertEqual(plans, {})

    def test_weights_bind_the_wing_to_its_chains(self) -> None:
        points, triangles, landmarks, plans, masks = _found()
        layout = ql.build_layout(landmarks)
        indices, weights = ql.skin_weights(points, layout)
        indices, weights = qw.wing_weights(points, triangles, layout.names(), plans, masks, indices, weights,
                                           float(landmarks["centre_x"]), float(landmarks["belly_z"]))
        names = np.array(layout.names())
        self.assertTrue(np.allclose(weights.sum(axis=1), 1.0))
        self.assertLessEqual(indices.shape[1], 4)
        on_wing = np.where(np.char.startswith(names[indices], "Wing"), weights, 0.0).sum(axis=1)
        tip = masks["Left"] & (points[:, 0] > 1.0)
        self.assertTrue((on_wing[tip] > 0.999).all(), "the far wing moves with its chains alone")
        self.assertTrue((on_wing[points[:, 2] < 1.0] < 1e-6).all(), "the legs carry no wing weight")


class Poses(unittest.TestCase):
    def test_the_rest_frame_round_trips(self) -> None:
        _points, _triangles, _landmarks, plans, _masks = _found()
        for plan in plans.values():
            rest, _middle, _axis = qw.rest_frame(plan)
            angles = qw.frame_angles(rest, plan["side_sign"])
            again = qw.target_frame(*angles, plan["side_sign"])
            self.assertTrue(np.allclose(again, rest, atol=1e-6))
            rows = qw.wing_rows(plan, dict(zip(("sweep", "rise", "roll"), angles)), "Left" if plan["side_sign"] > 0 else "Right")
            self.assertTrue(all(abs(degrees) < 1e-4 for row in rows.values() for _axis, degrees in row), "the rest pose turns nothing")

    def test_a_folded_wing_points_back(self) -> None:
        for sign in (1.0, -1.0):
            frame = qw.target_frame(qw.FOLDED["sweep"], qw.FOLDED["rise"], qw.FOLDED["roll"], sign)
            self.assertGreater(frame[1, 0], 0.9, "the span points to the tail")
            self.assertGreater(frame[2, 1], 0.0, "the chord rises")

    def test_mirrored_poses_are_mirrored(self) -> None:
        left = qw.target_frame(30.0, 20.0, -10.0, 1.0)
        right = qw.target_frame(30.0, 20.0, -10.0, -1.0)
        mirror = np.diag([-1.0, 1.0, 1.0])
        self.assertTrue(np.allclose(mirror @ left[:, :2], right[:, :2], atol=1e-9))

    def test_clips_the_game_loops_end_where_they_start(self) -> None:
        _points, _triangles, landmarks, _plans, _masks = _found()
        layout = ql.build_layout(landmarks)
        for style in ("winged_idle", "winged_walk", "winged_flee", "winged_rear", "winged_guard"):
            total = ql.frame_count(style)
            last = total if style in ql.LOOPING else total - 1
            first, end = ql.pose_at(style, 0, layout), ql.pose_at(style, last, layout)
            for name in set(first) | set(end):
                a = qw.rotation((1.0, 0.0, 0.0), 0.0)
                for axis, degrees in first.get(name, []):
                    a = qw.rotation(axis, degrees) @ a
                b = qw.rotation((1.0, 0.0, 0.0), 0.0)
                for axis, degrees in end.get(name, []):
                    b = qw.rotation(axis, degrees) @ b
                self.assertLess(qw.axis_angle(a @ b.T)[1], 1.0, f"{style} {name}")
            self.assertTrue(any(name.startswith("Wing") for name in first), style)

    def test_the_retreat_turns_away_and_back(self) -> None:
        _points, _triangles, landmarks, _plans, _masks = _found()
        layout = ql.build_layout(landmarks)
        total = ql.frame_count("winged_flee")
        turns = [sum(d for _a, d in ql.pose_at("winged_flee", frame, layout).get("__root_turn__", [])) for frame in range(total + 1)]
        self.assertAlmostEqual(turns[0], 0.0)
        self.assertAlmostEqual(turns[-1], 0.0)
        self.assertAlmostEqual(abs(max(turns, key=abs)), abs(ql.FLEE_TURN), places=3)

    def test_the_wing_carried_forward_by_a_turn_sweeps_back(self) -> None:
        _points, _triangles, landmarks, plans, _masks = _found()
        layout = ql.build_layout(landmarks)
        still = qw.role_rows("winged_flee", 0.5, layout, 0.0)
        turned = qw.role_rows("winged_flee", 0.5, layout, -30.0)
        # a turn toward the right (negative) carries the left wing forward: only its rows change
        self.assertNotEqual(still[qw.wing_name("Left", 0, 0)], turned[qw.wing_name("Left", 0, 0)])
        self.assertEqual(still[qw.wing_name("Right", 0, 0)], turned[qw.wing_name("Right", 0, 0)])

    def test_the_dead_wings_lie_level_with_the_rolled_body(self) -> None:
        _points, _triangles, landmarks, plans, _masks = _found()
        landmarks["death"] = {"roll": -80.0}
        for side, plan in plans.items():
            frame = qw.lying_pose(plan, landmarks)
            world = qw.rotation((0.0, 1.0, 0.0), -80.0) @ frame
            self.assertLess(world[2, 0], 0.05, f"{side}: the span does not rise from the ground")
            self.assertLess(abs(world[2, 1]), 0.05, f"{side}: the membrane lies flat")


class Rest(unittest.TestCase):
    def test_each_part_takes_its_least_change(self) -> None:
        def evaluate(leg_drop, wing_lift, tail_lift, neck_drop):
            return {"legs": 0.03 - 0.1 * leg_drop, "wings": -0.05 + 0.01 * wing_lift, "tail": 0.002 * tail_lift + 0.045,
                    "head": 0.2 - 0.005 * neck_drop}

        chosen = ql.choose_winged_rest(evaluate)
        self.assertEqual(chosen["leg_drop"], 0.25)  # 0.03 - 0.025 >= -0.01, while 0.5 gives -0.02
        self.assertEqual(chosen["wing_lift"], 5.0)
        self.assertEqual(chosen["tail_lift"], -25.0)
        self.assertEqual(chosen["neck_drop"], 40.0)


class Checks(unittest.TestCase):
    def test_the_checks_find_the_wings_by_their_bones(self) -> None:
        from tripo import tripo_checks as TC

        bones = ["Root", "Pelvis", "WingLeft_1_1", "WingRight_1_1"] + [f"{end}_{side}_Hoof" for end in ("Front", "Rear") for side in ("Left", "Right")]
        joints = np.array([[2, 1, -1, -1], [2, 1, -1, -1], [3, -1, -1, -1], [1, -1, -1, -1]])
        weights = np.array([[0.7, 0.3, 0, 0], [0.4, 0.6, 0, 0], [1.0, 0, 0, 0], [1.0, 0, 0, 0]])
        mesh = SimpleNamespace(bones=bones, joints=joints, weights=weights)
        left, right = TC.quadruped_wing_sides(mesh)
        self.assertEqual(left.tolist(), [True, False, False, False])
        self.assertEqual(right.tolist(), [False, False, True, False])
        self.assertIsNone(TC.quadruped_wing_sides(SimpleNamespace(bones=["Root"], joints=joints, weights=weights)))


class QuadrupedViews(unittest.TestCase):
    def test_the_views_run_from_the_hind_hooves_to_the_fore_hooves(self) -> None:
        from lib import pdx_motion
        from tripo import tripo_checks as TC

        bones = [f"{end}_{side}_Hoof" for end in ("Front", "Rear") for side in ("Left", "Right")] + ["Head", "TailCurl"]
        joints = np.array([[0.5, 0.0, -1.0], [-0.5, 0.0, -1.0], [0.5, 0.0, 1.0], [-0.5, 0.0, 1.0], [0.0, 2.0, -2.0], [5.0, 0.0, 3.0]])
        mesh = SimpleNamespace(bones=bones)
        original = pdx_motion.rest_joints
        pdx_motion.rest_joints = lambda _mesh: joints
        try:
            front = TC.front_direction(mesh)
        finally:
            pdx_motion.rest_joints = original
        self.assertTrue(np.allclose(front, [0.0, 0.0, -1.0]))


class Size(unittest.TestCase):
    def test_the_body_without_its_wings_is_measured(self) -> None:
        from lib import mount_size

        points, triangles = _dragon()
        turned = np.c_[points[:, 1], -points[:, 0], points[:, 2]]
        back, found = mount_size.winged_body(turned, triangles)
        body = back[found["body"]]
        self.assertGreater(found["wing_vertices"], 0)
        self.assertLess(float(np.ptp(body[:, 0])), 1.0, "the wings are left out of the width")
        self.assertGreater(float(np.ptp(body[:, 1])), 3.5, "the length runs from the head to the tail along Y")


if __name__ == "__main__":
    unittest.main()
