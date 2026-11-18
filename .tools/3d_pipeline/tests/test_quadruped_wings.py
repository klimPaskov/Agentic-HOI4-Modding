"""The winged quadruped (adapter/quadruped_wings.py and the winged styles of adapter/quadruped_layout.py), without Blender: a tail lying on
the ground is not a foot, the feet set the long axis, the wings are found by rule and fanned into chains, their poses are reached from the
rest frame, the clips the game loops start where they end, the dead body comes to rest by rule, and the checks find the wings by their
bones."""

from __future__ import annotations

import math
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
        self.assertEqual(len(ql.build_layout(landmarks).bones), 26 + 2 * qw.WING_CHAINS * qw.WING_BONES)
        self.assertLessEqual(len(ql.build_layout(landmarks).bones), 50)

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
            self.assertGreater(frame[1, 0], 0.85, "the span points to the tail")
            self.assertGreater(frame[2, 0], 0.05, "the span rises over the back instead of hanging on the flank")
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

    def test_the_two_wings_take_mirrored_poses(self) -> None:
        _points, _triangles, landmarks, plans, _masks = _found()
        layout = ql.build_layout(landmarks)
        for style in ("winged_walk", "winged_flee", "winged_guard"):
            for t in (0.2, 0.5):
                rows = qw.role_rows(style, t, layout, -30.0)
                left, right = (qw.target_frame(0, 0, 0, sign) for sign in (1.0, -1.0))
                turns = {side: rows[qw.wing_name(side, 1, 0)][1] for side in ("Left", "Right")}
                mirror = np.diag([-1.0, 1.0, 1.0])
                a = qw.rotation(*turns["Left"]) @ qw.rest_frame(plans["Left"])[0]
                b = mirror @ qw.rotation(*turns["Right"]) @ qw.rest_frame(plans["Right"])[0]
                self.assertTrue(np.allclose(a[:, :2], b[:, :2], atol=1e-6), f"{style} {t}")
                del left, right

    def test_the_retreat_turns_away_and_back(self) -> None:
        _points, _triangles, landmarks, _plans, _masks = _found()
        layout = ql.build_layout(landmarks)
        total = ql.frame_count("winged_flee")
        turns = [sum(d for _a, d in ql.pose_at("winged_flee", frame, layout).get("__root_turn__", [])) for frame in range(total + 1)]
        self.assertAlmostEqual(turns[0], 0.0)
        self.assertAlmostEqual(turns[-1], 0.0)
        self.assertAlmostEqual(abs(max(turns, key=abs)), abs(ql.FLEE_TURN), places=3)

    def test_a_turn_does_not_change_one_wing(self) -> None:
        _points, _triangles, landmarks, plans, _masks = _found()
        layout = ql.build_layout(landmarks)
        self.assertEqual(qw.role_rows("winged_flee", 0.5, layout, 0.0), qw.role_rows("winged_flee", 0.5, layout, -30.0))

    def test_the_dead_wings_lie_level_with_the_rolled_body(self) -> None:
        _points, _triangles, landmarks, plans, _masks = _found()
        landmarks["death"] = {"roll": -80.0}
        for side, plan in plans.items():
            upper = not qw.lies_under(plan, landmarks)
            frame = qw.lying_pose(plan, landmarks, upper)
            world = qw.rotation((0.0, 1.0, 0.0), -80.0) @ frame
            self.assertLess(world[2, 0], 0.05, f"{side}: the span does not rise from its root")
            self.assertLess(abs(world[2, 1]), 0.05, f"{side}: the membrane lies level")
            self.assertGreater(world[1, 0], 0.5, f"{side}: the wing lies toward the tail, behind the shoulders")


class Round4(unittest.TestCase):
    def test_a_fold_turns_every_chain_about_one_line(self) -> None:
        _points, _triangles, _landmarks, plans, _masks = _found()
        plan = plans["Left"]
        rows = qw.wing_rows(plan, {**qw.FOLDED, "sweep": 0.0, "rise": 0.0, "roll": 0.0}, "Left")
        axes = {tuple(np.round(rows[qw.wing_name("Left", c, 1)][0][0], 6)) for c in range(qw.WING_CHAINS)}
        self.assertEqual(len(axes), 1, "one fold line for all chains")

    def test_the_trailing_chain_follows_part_of_the_turn(self) -> None:
        _points, _triangles, _landmarks, plans, _masks = _found()
        rows = qw.wing_rows(plans["Left"], dict(qw.FOLDED), "Left")
        trailing = rows[qw.wing_name("Left", 0, 0)][1][1]
        lead = rows[qw.wing_name("Left", qw.WING_CHAINS - 1, 0)][1][1]
        self.assertAlmostEqual(trailing, qw.TRAIL_SHARE * lead, places=6)

    def test_the_attack_cocks_then_strikes_then_recovers(self) -> None:
        cock, strike, snap = qw.attack_phases(0.15)
        self.assertGreater(cock, 0.5)
        self.assertLess(strike, 0.01)
        cock, strike, snap = qw.attack_phases(0.435)
        self.assertLess(cock, 0.01)
        self.assertGreater(strike, 0.9)
        self.assertGreater(snap, 0.9)
        self.assertEqual(qw.attack_phases(1.0), (0.0, 0.0, 0.0))

    def test_the_wing_on_top_of_a_dead_body_stays_folded(self) -> None:
        _points, _triangles, landmarks, plans, _masks = _found()
        landmarks["death"] = {"roll": 82.0}
        self.assertTrue(qw.lies_under(plans["Left"], landmarks))
        self.assertFalse(qw.lies_under(plans["Right"], landmarks))
        pose = qw.role_pose("winged_collapse", 1.0, qw.WING_BONES, None, upper=True)
        self.assertEqual(pose["curl"], qw.FOLDED["curl"])
        self.assertNotIn("frame", pose)


class Round5(unittest.TestCase):
    def test_the_inner_web_runs_from_the_flank_to_the_trailing_chain(self) -> None:
        line_s, line_u = np.array([0.1, 0.2, 0.3]), np.array([-1.0, -0.9, -0.8])
        u = np.array([-1.0, -0.6, -0.2, 0.3, -0.9])
        s = np.array([0.1, 0.1, 0.1, 0.1, 0.5])
        share = qw.web_share(u, s, line_s, line_u, -0.2)
        self.assertAlmostEqual(share[0], 0.0, places=6, msg="none on the flank line")
        self.assertAlmostEqual(share[1], 0.5, places=6, msg="linear between the line and the chain")
        self.assertAlmostEqual(share[2], 1.0, places=6, msg="all on the trailing chain")
        self.assertEqual(share[3], 1.0, "ahead of the trailing chain the web plays no part")
        self.assertAlmostEqual(share[4], (-0.9 + 1.0) / (-0.2 + 1.0), places=6, msg="beyond the line its far end anchors (running least angle)")
        self.assertTrue(np.all(qw.web_share(u, s, np.zeros(0), np.zeros(0), -0.2) == 1.0), "no flank line: no web")

    def test_the_flank_line_is_the_border_behind_the_trailing_chain(self) -> None:
        points, triangles, _landmarks, plans, masks = _found()
        plan = plans["Left"]
        first, second, _normal = (np.asarray(row, float) for row in plan["plane"])
        rel = points - np.asarray(plan["root"], float)
        u, s = np.arctan2(rel @ second, rel @ first), np.hypot(rel @ first, rel @ second)
        trailing = float(np.asarray(plan["angles"], float)[0])
        line_s, line_u = qw.flank_line(points, triangles, masks["Left"], u, s, trailing)
        self.assertTrue(np.all(np.diff(line_s) >= 0), "sorted by radius")
        self.assertTrue(np.all(line_u < trailing))

    def test_folded_wings_ride_over_the_back(self) -> None:
        for pose in (qw.FOLDED, qw.HALF, qw.FLEE):
            frame = qw.target_frame(pose["sweep"], pose["rise"], pose["roll"], 1.0)
            self.assertGreater(frame[2, 0], 0.05, "the span rises over the back")

    def test_the_dead_wings_lie_behind_the_shoulders(self) -> None:
        for sweep, _tip in (qw.LYING_UPPER, qw.LYING_LOWER):
            self.assertGreaterEqual(sweep, 60.0, "toward the tail, clear of the head and neck laid forward")

    def test_the_falling_body_tucks_its_lower_legs_and_lays_its_neck_forward(self) -> None:
        _points, _triangles, landmarks, _plans, _masks = _found()
        landmarks["death"] = {"roll": -82.0, "leg_drop": 0.0}
        layout = ql.build_layout(landmarks)
        total = ql.frame_count("winged_collapse")

        def drop(frame: int) -> float:
            pose = ql.pose_at("winged_collapse", frame, layout)
            return sum(d for a, d in pose.get(ql.leg_name("Front", "Right", "Lower"), []) if tuple(a) == ql.Y_AXIS)
        middle = max(range(total), key=lambda frame: abs(drop(frame)))
        self.assertGreater(abs(drop(middle)), 1.0, "the leg underneath swings in mid-fall")
        self.assertLess(abs(drop(total - 1)), 1e-6, "and back to leg_drop once the body lies")
        neck = ql.pose_at("winged_collapse", total - 1, layout)["Neck_01"]
        self.assertIn((ql.X_AXIS, ql.WINGED_DEAD_NECK["Neck_01"]), [(tuple(a), round(d, 6)) for a, d in neck])

    def test_the_retreat_turns_away_at_mid_clip_and_runs(self) -> None:
        _points, _triangles, landmarks, _plans, _masks = _found()
        layout = ql.build_layout(landmarks)
        total = ql.frame_count("winged_flee")
        turns = [sum(d for _a, d in ql.pose_at("winged_flee", frame, layout).get("__root_turn__", [])) for frame in range(total)]
        self.assertEqual(int(np.argmax(np.abs(turns))), total // 2)
        self.assertGreater(ql.WINGED_CYCLES["winged_flee"] / ql.frame_count("winged_flee"), ql.WINGED_CYCLES["winged_walk"] / ql.frame_count("winged_walk"))


class Round6(unittest.TestCase):
    def test_a_thin_spike_has_a_small_aspect(self) -> None:
        sys.path.insert(0, str(PIPELINE / "tripo"))
        import tripo_checks as tc
        line = np.c_[np.linspace(0, 1, 50), 0.02 * np.sin(np.arange(50))]
        square = np.random.default_rng(0).uniform(0, 1, (200, 2))
        self.assertLess(tc._aspect(line), 0.1)
        self.assertGreater(tc._aspect(square), 0.8)

    def test_folded_wings_turn_their_membrane_down_and_open_wings_toward_the_sky(self) -> None:
        self.assertLess(qw.FOLDED["roll"], -30.0, "folded wings lie along the back and flanks, below the head from the front")
        for pose in (qw.HALF, qw.FLEE):
            self.assertLess(pose["roll"], -30.0, "the membrane faces the game camera")

    def test_the_defend_crouches_and_the_attack_lunges(self) -> None:
        _points, _triangles, landmarks, _plans, _masks = _found()
        layout = ql.build_layout(landmarks)
        middle = ql.pose_at("winged_guard", ql.frame_count("winged_guard") // 2, layout)
        self.assertNotEqual(middle.get(ql.leg_name("Front", "Left", "Lower"), []), [], "the legs bend in the crouch")
        reach = max(sum(d for _a, d in ql.pose_at("winged_rear", frame, layout).get("Neck_01", [])) for frame in range(ql.frame_count("winged_rear")))
        self.assertGreaterEqual(reach, 0.9 * ql.STRIKE_NECK["Neck_01"][1], "the neck drives forward at the strike")


class Round7(unittest.TestCase):
    def test_no_neck_joint_bends_past_the_cap_in_the_strike(self) -> None:
        _points, _triangles, landmarks, _plans, _masks = _found()
        layout = ql.build_layout(landmarks)
        for frame in range(ql.frame_count("winged_rear")):
            pose = ql.pose_at("winged_rear", frame, layout)
            for name in ("Neck_01", "Neck_02"):  # the head turns to face where it is aimed (`aim_head`), most often back into the neck's line
                for _axis, degrees in pose.get(name, []):
                    self.assertLessEqual(abs(degrees), ql.STRIKE_JOINT_MAX + 1e-6, f"{name} frame {frame}")

    def test_the_gait_strides_farther_than_the_shared_walk(self) -> None:
        _points, _triangles, landmarks, _plans, _masks = _found()
        layout = ql.build_layout(landmarks)
        name = ql.leg_name("Front", "Left", "Upper")
        walk = max(abs(d) for f in range(ql.frame_count("quadruped_walk")) for a, d in ql.pose_at("quadruped_walk", f, layout).get(name, []) if tuple(a) == ql.X_AXIS)
        self.assertGreater(ql.WINGED_STRIDE, 1.0)
        self.assertGreater(walk, 0.0)

    def test_the_crush_limit_lies_between_passed_and_failed_poses(self) -> None:
        sys.path.insert(0, str(PIPELINE / "tripo"))
        import tripo_checks as tc
        self.assertTrue(0.045 < tc.MAX_WING_CRUSH < 0.096, "between the attack flare reviewers passed and the crushed defend")
        self.assertTrue(0.24 < tc.MIN_STEP_READ, "run 12's move, which read as legs standing still")


class Round8(unittest.TestCase):
    """Round 7 of the Tripo dragon: both dead wings folded, a braced recoil for the defend, a retreat with the wings swept back."""

    def test_both_dead_wings_keep_the_idle_fold(self) -> None:
        for upper in (True, False):
            for t in (0.0, 0.3, 0.6, 1.0):
                pose = qw.role_pose("winged_collapse", t, qw.WING_BONES, None, upper=upper)
                self.assertEqual(pose["curl"], qw.FOLDED["curl"], "folded at the joints as in the idle")
                self.assertEqual(pose["spread"], qw.FOLDED["spread"])
                self.assertEqual(pose.get("flap", 0.0), 0.0, "no beat and no lift on the way down")

    def test_the_dead_wings_turn_only_while_the_body_rolls(self) -> None:
        _points, _triangles, landmarks, plans, _masks = _found()
        landmarks["death"] = {"roll": -82.0}
        frame = qw.lying_pose(plans["Left"], landmarks, True)
        self.assertEqual(qw.role_pose("winged_collapse", qw.DEAD_WINGS_START, qw.WING_BONES, frame, upper=True)["frame_share"], 0.0)
        self.assertEqual(qw.role_pose("winged_collapse", qw.DEAD_WINGS_END, qw.WING_BONES, frame, upper=True)["frame_share"], 1.0)

    def test_the_wing_underneath_lifts_by_what_the_rest_chose(self) -> None:
        _points, _triangles, landmarks, plans, _masks = _found()
        landmarks["death"] = {"roll": -82.0}
        lower = next(plan for plan in plans.values() if qw.lies_under(plan, landmarks))
        turn = qw.rotation((0.0, 1.0, 0.0), -82.0)
        flat = (turn @ qw.lying_pose(lower, landmarks, False))[2, 0]
        landmarks["death"]["wing_lift"] = 10.0
        self.assertGreater((turn @ qw.lying_pose(lower, landmarks, False))[2, 0], flat)

    def test_a_planted_crouch_moves_the_feet_of_both_ends_alike_within_its_limits(self) -> None:
        _points, _triangles, landmarks, _plans, _masks = _found()
        crouch = ql.planted_crouch(landmarks, 8.0, 40.0)
        back, sink = crouch["travel"]
        self.assertGreater(back, 0.0, "the body shifts back")
        self.assertGreater(sink, 0.0, "and sinks")
        for name, joints in landmarks["legs"].items():
            upper, lower = crouch[name.split("_")[0]]
            self.assertLessEqual(abs(upper), 9.0, "the hip or shoulder turns no farther than its skin allows")
            self.assertLessEqual(abs(lower), 42.0)
            travel = ql._foot_travel(joints, upper, lower)
            self.assertAlmostEqual(float(travel[0]), -back, delta=0.02 * float(landmarks["height"]), msg=f"{name}: the foot stays under the shift back")
            self.assertAlmostEqual(float(travel[1]), sink, delta=0.02 * float(landmarks["height"]), msg=f"{name}: and under the sink")
        self.assertEqual(ql.planted_crouch(landmarks, 0.0, 0.0), {}, "no turn allowed: no crouch")

    def test_the_tail_lifts_by_the_sink(self) -> None:
        landmarks = {"tail": [np.array([0.0, 2.0, 1.0]), np.array([0.0, 3.0, 0.2]), np.array([0.0, 4.0, 0.0]), np.array([0.0, 5.0, 0.0])]}
        lift = ql.tail_lift(landmarks, 0.3)
        angle = math.radians(lift)
        self.assertAlmostEqual(1.0 * math.sin(angle) - 0.8 * math.cos(angle) + 0.8, 0.3, places=4, msg="its first joint rises by the sink")
        self.assertEqual(ql.tail_lift(landmarks, 0.0), 0.0)
        self.assertEqual(ql.tail_lift({}, 0.3), 0.0)

    def test_the_defend_is_a_braced_recoil(self) -> None:
        _points, _triangles, landmarks, _plans, _masks = _found()
        layout = ql.build_layout(landmarks)
        total = ql.frame_count("winged_guard")
        middle = ql.pose_at("winged_guard", total // 2, layout)
        self.assertGreater(sum(d for _a, d in middle["__root_shift__"]), 0.0, "the body shifts back (+Y, away from the enemy)")
        self.assertNotIn("__root_pitch__", middle, "the forefeet stay on the ground")
        for end, side in ql.LEGS:
            upper = sum(d for _a, d in middle[ql.leg_name(end, side, "Upper")])
            self.assertLessEqual(abs(upper), ql.GUARD_HIP + 1.0, "the hips and shoulders turn within the skin's limit")
            turns = [sum(d for _a, d in middle[ql.leg_name(end, side, segment)]) for segment in ("Upper", "Lower", "Cannon")]
            self.assertAlmostEqual(sum(turns), 0.0, places=6, msg="the foot stays flat")
            self.assertNotIn(ql.leg_name(end, side, "Hoof"), middle)
        self.assertGreater(sum(d for _a, d in middle["Tail_01"]), 0.0, "the tail lifts as the body sinks")
        self.assertAlmostEqual(sum(d for _a, d in middle["Tail_01"]) + sum(d for _a, d in middle["Tail_02"]), 0.0, places=6)
        neck = {name: sum(d for _a, d in middle[name] if tuple(_a) == ql.X_AXIS) for name in ("Neck_01", "Neck_02", "Head")}
        self.assertGreater(neck["Neck_01"], 0.0, "the neck arcs forward and down from the shoulders, carrying the head low")
        self.assertLess(neck["Head"], 0.0, "and the head turns up at its end")
        self.assertAlmostEqual(sum(neck.values()), ql.GUARD_NECK_S["Head"], places=6, msg="so it faces the enemy as GUARD_NECK_S says")
        for frame in (0, total - 1):
            self.assertAlmostEqual(sum(d for _a, d in ql.pose_at("winged_guard", frame, layout)["__root_shift__"]), 0.0, places=6)

    def test_the_wings_held_back_keep_the_fold(self) -> None:
        for pose in (qw.MANTLE, qw.FLEE):
            self.assertEqual((pose["curl"], pose["spread"], pose["roll"]), (qw.FOLDED["curl"], qw.FOLDED["spread"], qw.FOLDED["roll"]),
                             "the fold's own bend: unbent, the trailing half of the fan stood out to the side (run 15)")
            self.assertGreaterEqual(pose["sweep"], qw.FOLDED["sweep"], "behind the shoulders, never further out than the fold")
        self.assertGreater(qw.MANTLE["rise"], qw.FOLDED["rise"], "the mantle raises the fold over the back, so it does not read as the idle")

    def test_the_retreat_holds_its_wings_folded_further_than_the_move(self) -> None:
        self.assertGreater(qw.FLEE["sweep"], qw.HALF["sweep"] + 10.0, "swept back")
        self.assertGreater(qw.FLEE["curl"], 0.0, "half folded")
        self.assertLess(qw.FLEE_BEAT[0], qw.WALK_BEAT[0], "and beating less than the wings of the move")

    def test_the_down_stroke_of_the_attack_ends_before_the_wings_fold(self) -> None:
        for t in (qw.ATTACK_DOWN_END, 0.85, 1.0):
            self.assertAlmostEqual(qw.role_pose("winged_rear", t, qw.WING_BONES)["flap"], 0.0, places=6)
        self.assertGreater(qw.role_pose("winged_rear", 0.45, qw.WING_BONES)["flap"], 0.5 * qw.ATTACK_DOWNSTROKE)

    def test_a_winged_death_starts_to_roll_early(self) -> None:
        _points, _triangles, landmarks, _plans, _masks = _found()
        landmarks["death"] = {"roll": -82.0, "leg_drop": 0.0}
        layout = ql.build_layout(landmarks)
        total = ql.frame_count("winged_collapse")
        roll = [abs(sum(d for _a, d in ql.pose_at("winged_collapse", frame, layout).get("__root_roll__", []))) for frame in range(total)]
        self.assertLess(roll[0], 1e-9)
        self.assertGreater(roll[int(0.2 * total)], 3.0, "no opening hold")
        self.assertAlmostEqual(roll[int(0.6 * total)], 82.0, places=3, msg="it lies by 0.6 of the clip")


def _lying(head_at: float, wing: str):
    """A dead body as points on one bone (file frame: Y up, facing +Z): a torso slab 1 high, a head and neck block starting `head_at`
    along the facing, and a wing joined to the torso: "flat" on the ground beside it (0.6 thick, its join on the ground) or a "sail"
    standing 1.2 over its join on top of the torso. Returns (mesh, one frame of matrices, wing mask, head and neck mask, torso mask)."""

    from lib import pdx_deform as P

    def grid(xs, ys, zs):
        return np.array([[x, y, z] for x in xs for y in ys for z in zs], float)

    step = 0.1
    torso = grid(np.arange(-1.0, 1.01, step), (0.0, 0.5, 1.0), np.arange(-2.0, 2.01, step))
    head = grid(np.arange(-0.3, 0.31, step), (0.2,), np.arange(head_at, head_at + 0.81, step))
    if wing == "flat":
        membrane = grid(np.arange(1.0, 3.01, step), (0.0, 0.6), np.arange(-1.0, 1.01, step))
        joined = np.flatnonzero((membrane[:, 0] == 1.0) & (membrane[:, 1] == 0.0))
    else:
        membrane = grid((0.0,), np.arange(1.0, 2.21, step), np.arange(-1.0, 1.01, step))
        joined = np.flatnonzero(membrane[:, 1] == 1.0)
    positions = np.concatenate([torso, head, membrane])
    first = len(torso) + len(head)
    # the wing's border with the body: a triangle from each joined wing point to the torso
    triangles = np.array([[first + index, first + index, 0] for index in joined])
    count = len(positions)
    joints = np.full((count, 4), -1)
    joints[:, 0] = 0
    weights = np.zeros((count, 4))
    weights[:, 0] = 1.0
    mesh = P.SkinnedMesh(positions=positions, triangles=triangles, joints=joints, weights=weights, bones=["Root"], parents=[-1], inverse_bind=np.eye(4)[None])
    index = np.arange(count)
    return mesh, np.eye(4)[None, None], index >= first, (index >= len(torso)) & (index < first), index < len(torso)


class AimedHead(unittest.TestCase):
    def test_the_head_faces_where_its_style_says_whatever_the_neck_does(self) -> None:
        names = {"Neck_01", "Neck_02", "Head", "Chest"}
        pose = {"__root_pitch__": [(ql.X_AXIS, -10.0)], "Chest": [(ql.X_AXIS, 5.0)], "Neck_01": [(ql.X_AXIS, 50.0)],
                "Neck_02": [(ql.X_AXIS, 50.0)], "Head": [(ql.Z_AXIS, 7.0), (ql.X_AXIS, 30.0)]}
        ql.aim_head(pose, names, 20.0)
        carried = -10.0 + 5.0 + 50.0 + 50.0
        head = [degrees for axis, degrees in pose["Head"] if tuple(axis) == ql.X_AXIS]
        self.assertEqual(len(head), 1)
        self.assertAlmostEqual(carried + head[0], 20.0, places=6, msg="the carried pitches and the head's own add to the facing asked")
        self.assertIn((ql.Z_AXIS, 7.0), pose["Head"], "the head's other turns are kept")

    def test_the_strike_ends_facing_forward_and_down_not_back_at_the_chest(self) -> None:
        _points, _triangles, landmarks, _plans, _masks = _found()
        layout = ql.build_layout(landmarks)
        for frame in range(ql.frame_count("winged_rear")):
            pose = ql.pose_at("winged_rear", frame, layout)
            facing = sum(d for name in ("__root_pitch__",) + ql.HEAD_CARRIERS + ("Head",) for a, d in pose.get(name, []) if tuple(a) == ql.X_AXIS)
            self.assertLessEqual(abs(facing), 40.0, f"frame {frame}: run 15 turned the snout 108 degrees, back at the chest")


class DeathEnd(unittest.TestCase):
    def setUp(self) -> None:
        sys.path.insert(0, str(PIPELINE / "tripo"))
        import tripo_checks as tc
        self.tc = tc

    def test_a_head_laid_forward_shows_and_one_on_the_body_is_lost(self) -> None:
        tc = self.tc
        mesh, matrices, wing, head, torso = _lying(2.6, "flat")
        _above, clear = tc.death_end_numbers(mesh, matrices, [wing], head, head, torso)
        self.assertGreater(clear, tc.DEATH_HEAD_CLEAR, "forward of the body: seen from the game camera on either side")
        mesh, matrices, wing, head, torso = _lying(-0.4, "flat")
        _above, clear = tc.death_end_numbers(mesh, matrices, [wing], head, head, torso)
        self.assertLess(clear, 0.3, "over the torso: lost in its outline")

    def test_a_head_beside_a_wing_is_judged_from_both_sides_of_the_heading(self) -> None:
        tc = self.tc
        # the head lies forward and to the wing's side: one of the two cameras sees it against the wing
        mesh, matrices, wing, head, torso = _lying(1.2, "flat")
        mesh.positions[head, 0] += 1.6
        one_side = []
        for axes in tc.game_cameras(mesh):
            cell = 2.0 * tc.SILHOUETTE_CELL_SHARE * mesh.height
            seen = tc._cells(mesh.positions[head], axes, cell)
            one_side.append(len(seen - tc._cells(mesh.positions[~head], axes, cell)) / len(seen))
        _above, clear = tc.death_end_numbers(mesh, matrices, [wing], head, head, torso)
        self.assertAlmostEqual(clear, min(one_side), places=6)

    def test_a_folded_wing_on_the_ground_is_not_a_sail(self) -> None:
        tc = self.tc
        mesh, matrices, wing, head, torso = _lying(2.6, "flat")
        above, _clear = tc.death_end_numbers(mesh, matrices, [wing], head, head, torso)
        self.assertLess(above, tc.DEATH_WING_ABOVE, "0.6 thick on the ground beside a torso 1 high: under the middle of the lying torso")
        plain, _clear = tc.death_end_numbers(mesh, matrices, [wing], head, head)
        self.assertGreater(plain, above, "measured from its join on the ground it would count as standing")
        mesh, matrices, wing, head, torso = _lying(2.6, "sail")
        above, _clear = tc.death_end_numbers(mesh, matrices, [wing], head, head, torso)
        self.assertGreater(above, tc.DEATH_WING_ABOVE, "standing over the body it is one")


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


class HeldPoseChecks(unittest.TestCase):
    """TRIPO-HEAD-FACING, TRIPO-DEATH-SIDE and TRIPO-WING-SIDE-REACH on a few points (file frame: y up, facing -z)."""

    @staticmethod
    def _turn(axis, degrees: float) -> np.ndarray:
        matrix = np.eye(4)
        matrix[:3, :3] = qw.rotation(axis, degrees)
        return matrix

    def test_the_head_facing_counts_a_hook_and_not_a_nod(self) -> None:
        from tripo import tripo_checks as TC

        # bones Root, Chest, Head (joint at the origin); the snout 1 ahead and 1 below: 45 degrees down
        mesh = SimpleNamespace(positions=np.array([[0.0, -1.0, -1.0]]), inverse_bind=np.stack([np.eye(4)] * 3))
        front = np.array([0.0, 0.0, -1.0])
        nod = np.stack([np.stack([np.eye(4), np.eye(4), self._turn((1, 0, 0), 20.0 * f)]) for f in range(3)])
        turn, frame = TC.head_facing_turn(mesh, nod, 2, 0, 1, front)
        self.assertAlmostEqual(turn, 40.0, places=4)
        self.assertEqual(frame, 2)
        hook = np.stack([np.stack([np.eye(4), np.eye(4), self._turn((1, 0, 0), sign * 110.0)]) for sign in (0.0, 1.0)])
        turn, _frame = TC.head_facing_turn(mesh, hook, 2, 0, 1, front)
        self.assertGreater(turn, TC.MAX_HEAD_FACING_TURN, "the snout turned back at the chest")

    def test_the_dead_torso_lies_on_its_side(self) -> None:
        from tripo import tripo_checks as TC

        frame = np.stack([np.eye(4), self._turn((0, 0, 1), 82.0)])
        self.assertAlmostEqual(TC.torso_roll(frame, 1), 82.0, places=4)
        low, high = TC.DEATH_ROLL_RANGE
        self.assertTrue(low <= 82.0 <= high)
        self.assertFalse(low <= TC.torso_roll(np.stack([np.eye(4), self._turn((0, 0, 1), 170.0)]), 1) <= high, "on its back")

    def test_the_side_reach_is_read_in_the_chest_frame(self) -> None:
        from tripo import tripo_checks as TC

        # a torso point on the midline, a left wing point 2 out and a right one 1 out; the chest (all one bone) yaws 40 degrees
        positions = np.array([[0.0, 1.0, 0.0], [2.0, 1.0, 0.0], [-1.0, 1.0, 0.0]])
        mesh = SimpleNamespace(positions=positions, joints=np.zeros((3, 1), int), weights=np.ones((3, 1)))
        sides = [np.array([False, True, False]), np.array([False, False, True])]
        torso = np.array([True, False, False])
        matrices = np.stack([np.stack([self._turn((0, 1, 0), 40.0 * f)]) for f in range(2)])
        reach = TC.side_reach(mesh, matrices, sides, torso, 0, np.array([0.0, 0.0, -1.0]))
        self.assertAlmostEqual(reach[0], 2.0, places=6, msg="a turned body keeps its own sides")
        self.assertAlmostEqual(reach[1], 1.0, places=6)


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


class Mirror(unittest.TestCase):
    def test_the_best_turn_recovers_a_rotation(self) -> None:
        from tripo import tripo_checks as TC

        rng = np.random.default_rng(3)
        points = rng.normal(size=(50, 3)) * np.array([3.0, 1.0, 0.1])
        turn = qw.rotation((0.3, 0.2, 0.9), 40.0)
        found = TC._best_turn(points, points @ turn.T + 5.0)
        self.assertLess(TC._turn_degrees(found.T @ turn), 1e-6)


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
