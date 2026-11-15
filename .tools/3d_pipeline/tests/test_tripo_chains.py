"""Secondary chains: the budget and shape rules, the sheet layout and weights, the border blend and the cloak sheet motion."""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

import numpy as np

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))
sys.path.insert(0, str(PIPELINE / "tripo"))

from lib import tripo_chains as C

UP = np.array([0.0, 0.0, 1.0])
DOWN = -UP
FRONT = np.array([0.0, -1.0, 0.0])


def chain_rest(lengths, start=(0.0, 0.0, 1.0), direction=DOWN):
    """Rest matrices relative to the parent for a straight chain hanging from `start` along `direction` (bones point along local +Y)."""

    direction = C.unit(direction)
    basis = np.eye(4)
    basis[:3, :3] = C.shortest_arc(np.array([0.0, 1.0, 0.0]), direction)
    out, offset = [], np.array(start, float)
    for k in range(len(lengths)):
        relative = np.eye(4)
        if k == 0:
            relative[:3, :3] = basis[:3, :3]
            relative[:3, 3] = offset
        else:
            relative[:3, 3] = [0.0, lengths[k - 1], 0.0]
        out.append(relative)
    return np.stack(out)


class BudgetAndShape(unittest.TestCase):
    def test_free_bones_are_shared_by_sides(self) -> None:
        self.assertEqual(C.bone_budget(23, ["wings"]), 13)
        self.assertEqual(C.bone_budget(24, ["cloak"]), 26)
        self.assertEqual(C.bone_budget(23, ["cloak", "wings"]), 9)

    def test_a_rig_with_no_room_is_refused(self) -> None:
        with self.assertRaises(ValueError):
            C.bone_budget(48, ["wings"])

    def test_shape_follows_length_and_width_over_the_segment(self) -> None:
        self.assertEqual(C.chain_shape(0.30, 0.20, 0.1, 50), (2, 3))
        self.assertEqual(C.chain_shape(0.52, 0.43, 0.096, 26), (5, 4))

    def test_over_budget_drops_to_three_bones_then_fewer_chains(self) -> None:
        self.assertEqual(C.chain_shape(0.5, 0.8, 0.05, 13), (4, 3))
        self.assertEqual(C.chain_shape(0.5, 0.8, 0.05, 6), (2, 3))
        self.assertEqual(C.chain_shape(0.5, 0.8, 0.05, 4), (2, 2))


class SheetLayout(unittest.TestCase):
    def sheet(self):
        rng = np.random.default_rng(3)
        u = rng.uniform(-1.0, 1.0, 4000)
        s = rng.uniform(0.0, 1.0, 4000)
        points = np.stack([u, np.zeros_like(u), -s], axis=1)
        return points, u, s

    def test_joints_lie_on_the_sheet_and_run_down_each_column(self) -> None:
        points, u, s = self.sheet()
        chain_u = C.even_angles(u, 3)
        joints, stations = C.sheet_layout(points, u, s, chain_u, 4)
        self.assertEqual(joints.shape, (3, 5, 3))
        self.assertTrue(np.all(np.diff(stations, axis=1) > 0))
        self.assertTrue(np.all(np.diff(joints[:, :, 2], axis=1) < 0))
        np.testing.assert_allclose(joints[:, 0, 0], chain_u, atol=0.1)

    def test_weights_have_at_most_four_influences_summing_to_one(self) -> None:
        points, u, s = self.sheet()
        chain_u = C.even_angles(u, 3)
        _joints, stations = C.sheet_layout(points, u, s, chain_u, 4)
        rows = C.sheet_weights(u, s, chain_u, stations)
        self.assertLessEqual(max(len(row) for row in rows), 4)
        np.testing.assert_allclose([sum(row.values()) for row in rows], 1.0, atol=1e-9)

    def test_a_vertex_on_a_chain_at_a_bone_middle_belongs_to_that_bone(self) -> None:
        chain_u = np.array([-0.5, 0.5])
        stations = np.array([[0.0, 0.25, 0.5, 0.75, 1.0]] * 2)
        rows = C.sheet_weights(np.array([0.5]), np.array([0.375]), chain_u, stations)
        self.assertEqual(rows[0], {1 * 4 + 1: 1.0})

    def test_ridges_are_where_the_region_reaches_farthest(self) -> None:
        rng = np.random.default_rng(5)
        u = rng.uniform(0.5, 2.5, 20000)
        reach = 0.6 + 0.4 * np.cos(math.pi * u) ** 8  # peaks at 1 and 2, low at the ends
        s = rng.uniform(0.0, 1.0, 20000) * reach
        angles, mode = C.ridge_angles(u, s, 2)
        self.assertEqual(mode, "ridges")
        self.assertTrue(all(min(abs(a - p) for p in (1.0, 2.0)) < 0.15 for a in angles), angles)

    def test_no_ridges_gives_an_even_fan(self) -> None:
        u = np.linspace(0.0, 1.0, 1000)
        s = np.ones_like(u)
        angles, mode = C.ridge_angles(u, s, 3)
        self.assertEqual(mode, "fan")
        np.testing.assert_allclose(np.diff(angles), np.diff(angles)[0])


class Blending(unittest.TestCase):
    def strip(self, count=40):
        positions = np.stack([np.arange(count) * 0.01, np.zeros(count), np.zeros(count)], axis=1)
        edges = np.stack([np.arange(count - 1), np.arange(1, count)], axis=1)
        return positions, edges

    def test_the_region_is_whole_and_the_blend_runs_outward(self) -> None:
        positions, edges = self.strip()
        region = np.arange(40) >= 20
        alpha = C.blend_alpha(positions, edges, region, 0.1)
        self.assertTrue(np.all(alpha[20:] == 1.0))
        self.assertTrue(np.all(np.diff(alpha[9:21]) >= 0))
        self.assertTrue(np.all(alpha[:10] == 0.0))
        self.assertTrue(0.0 < float(alpha[15]) < 1.0)

    def test_a_limb_end_gets_no_chain_weight_and_the_share_fades_to_it(self) -> None:
        positions, edges = self.strip()
        region = np.arange(40) >= 20
        hand = np.arange(40) == 25
        alpha = C.blend_alpha(positions, edges, region, 0.05, hand)
        self.assertEqual(float(alpha[25]), 0.0)
        self.assertTrue(0.0 < float(alpha[23]) < 1.0)
        self.assertEqual(float(alpha[35]), 1.0)
        self.assertTrue(C.is_limb_end("LeftHand") and C.is_limb_end("RightLeg") and not C.is_limb_end("LeftUpLeg"))

    def test_mix_keeps_the_four_largest_weights_normalised(self) -> None:
        mixed = C.mix_weights({"A": 0.5, "B": 0.3, "C": 0.2}, {"X": 0.6, "Y": 0.4}, 0.5)
        self.assertEqual(len(mixed), 4)
        self.assertAlmostEqual(sum(mixed.values()), 1.0)
        self.assertNotIn("C", mixed)

    def test_growth_stops_at_vertices_that_are_not_allowed(self) -> None:
        _positions, edges = self.strip(10)
        allowed = np.ones(10, bool)
        allowed[6] = False
        grown = C.grow_region(np.arange(10) == 3, edges, allowed)
        np.testing.assert_array_equal(np.where(grown)[0], [0, 1, 2, 3, 4, 5])


class Rotations(unittest.TestCase):
    def test_shortest_arc_turns_a_onto_b(self) -> None:
        for a, b in (((1, 0, 0), (0, 1, 0)), ((0, 0, 1), (0, 0, -1)), ((1, 2, 3), (-2, 0.5, 1))):
            a, b = C.unit(np.array(a, float)), C.unit(np.array(b, float))
            np.testing.assert_allclose(C.shortest_arc(a, b) @ a, b, atol=1e-9)

    def test_quaternion_round_trip(self) -> None:
        m = C.axis_angle_matrix(np.array([1.0, 2.0, -1.0]), 1.1)
        np.testing.assert_allclose(C.matrix_from_quaternion(C.quaternion_from_matrix(m)), m, atol=1e-9)

    def test_forward_kinematics_points_bones_where_asked(self) -> None:
        rest = chain_rest([0.2, 0.2, 0.2])
        wanted = C.unit(np.array([[0.0, 0.3, -1.0], [0.0, 0.6, -1.0], [0.2, 0.8, -1.0]]))
        _q, heads, matrices = C.chain_forward(np.eye(4), rest, wanted)
        for k in range(3):
            np.testing.assert_allclose(C.unit(matrices[k][:3, 1]), wanted[k], atol=1e-9)
        np.testing.assert_allclose(heads[1], heads[0] + 0.2 * wanted[0], atol=1e-9)


LENGTHS = np.array([0.15, 0.15, 0.15])
SLANT = np.array([0.0, 0.2, -1.0])


def carried(_frame, _bone, _head, rigid):
    """The simplest target: where the parent carries the bone."""

    return rigid


class SpringChain(unittest.TestCase):
    def run_chain(self, parents, target=carried, capsule_axes=None, radii=None, passes=1, ground=-np.inf):
        rest = chain_rest(LENGTHS, start=(0.0, 0.1, 1.0), direction=SLANT)
        return C.simulate_chain(parents, rest, LENGTHS, C.pendulum_omegas(LENGTHS, 1.8), 1.0 / 24, target, capsule_axes, radii, ground, UP,
                                None, passes)

    def test_a_still_body_leaves_the_chain_at_rest(self) -> None:
        quaternions, _joints = self.run_chain(np.stack([np.eye(4)] * 30))
        np.testing.assert_allclose(np.abs(quaternions[..., 0]), 1.0, atol=1e-6)

    def test_the_chain_lags_a_sudden_target_then_settles(self) -> None:
        hang = C.unit(np.array([0.0, -0.6, -1.0]))

        def target(frame, _bone, _head, rigid):
            return rigid if frame < 10 else hang

        _q, joints = self.run_chain(np.stack([np.eye(4)] * 90), target)
        first = C.unit(joints[:, 1] - joints[:, 0])
        self.assertLess(float(first[11] @ hang), 0.99)  # it does not jump in one frame
        self.assertGreater(float(first[-1] @ hang), 0.999)  # and it gets there

    def test_a_capsule_pushes_the_chain_out(self) -> None:
        frames = 40
        parents = np.stack([np.eye(4)] * frames)
        axes = np.zeros((frames, 1, 2, 3))
        for f in range(frames):
            y = 0.5 - 0.5 * min(f / 20, 1.0)  # a leg swings back into the cloth
            axes[f, 0] = [[-0.2, y, 0.75], [0.2, y, 0.75]]
        radii = np.full((3, 1), 0.08)
        _q, joints = self.run_chain(parents, capsule_axes=axes, radii=radii)
        for f in range(frames):
            for k in range(1, 4):
                nearest = C.closest_on_segment(joints[f, k], axes[f, 0, 0], axes[f, 0, 1])
                self.assertGreater(float(np.linalg.norm(joints[f, k] - nearest)), 0.08 - 0.02)

    def test_the_ground_holds_the_chain_up(self) -> None:
        parents = []
        for f in range(40):
            m = np.eye(4)
            m[2, 3] = -0.8 * min(f / 10, 1.0)  # the body falls
            parents.append(m)
        _q, joints = self.run_chain(np.stack(parents), ground=0.0)
        self.assertGreaterEqual(float(joints[:, 1:, 2].min()), -1e-6)

    def test_a_looping_clip_ends_where_it_starts(self) -> None:
        hang = C.unit(np.array([0.0, 0.0, -1.0]))

        def target(_frame, _bone, _head, rigid):
            return C.unit(rigid + hang)  # half way between where the body carries it and straight down

        parents = []
        for f in range(48):
            m = np.eye(4)
            m[:3, :3] = C.axis_angle_matrix(np.array([0.0, 1.0, 0.0]), math.radians(15.0) * math.sin(2 * math.pi * f / 47))
            parents.append(m)
        quaternions, _joints = self.run_chain(np.stack(parents), target, passes=C.LOOP_PASSES)
        closed = C.close_loop(quaternions)
        self.assertLess(C.quaternion_step_degrees(closed[-1, 2], closed[0, 2]), 1e-6)
        self.assertLess(C.fastest_step(closed), 15.0)

    def test_omegas_do_not_depend_on_the_model_scale(self) -> None:
        np.testing.assert_allclose(C.pendulum_omegas([0.1, 0.1], 1.0), C.pendulum_omegas([0.73518, 0.73518], 7.3518))
        self.assertGreater(C.pendulum_omegas([0.1, 0.05], 1.0)[1], C.pendulum_omegas([0.1, 0.05], 1.0)[0])  # a shorter link swings faster


class CloakSheet(unittest.TestCase):
    def test_the_torso_follow_shares_by_height(self) -> None:
        tails = np.array([[0.0, 0.0, 1.4], [0.0, 0.0, 1.2], [0.0, 0.0, 0.9]])
        rows = C.torso_follow_weights(tails, np.array([0.0, 0.0, 1.4]), np.array([0.0, 0.0, 1.0]), UP)
        self.assertEqual(rows[0], {C.CHAIN_PARENT: 1.0})
        self.assertAlmostEqual(rows[1][C.CHAIN_PARENT], 0.5)
        self.assertEqual(rows[2], {"Hips": 1.0})

    def test_follow_targets_skin_the_rest_point(self) -> None:
        moved = np.eye(4)
        moved[:3, 3] = [0.0, 0.0, -0.5]
        skinning = {"Hips": np.stack([np.eye(4), moved]), C.CHAIN_PARENT: np.stack([np.eye(4), np.eye(4)])}
        points = C.follow_targets(np.array([[0.0, 0.0, 1.0]]), [{"Hips": 0.5, C.CHAIN_PARENT: 0.5}], skinning)
        np.testing.assert_allclose(points[:, 0, 2], [1.0, 0.75])

    def test_cloth_never_points_above_the_horizon(self) -> None:
        np.testing.assert_allclose(C.hang_below_horizon(C.unit(np.array([0.0, 1.0, 1.0])), UP), [0.0, 1.0, 0.0], atol=1e-12)
        down = C.unit(np.array([0.0, 1.0, -1.0]))
        np.testing.assert_allclose(C.hang_below_horizon(down, UP), down)

    def test_a_push_spreads_to_the_neighbours(self) -> None:
        np.testing.assert_allclose(C.spread_pushes(np.array([0.0, 0.2, 0.0, 0.0])), [0.1, 0.2, 0.1, 0.05])

    def test_exit_along_leaves_the_capsule_on_that_line(self) -> None:
        moved = C.exit_along(np.zeros(3), np.array([-1.0, 0.0, 0.0]), np.array([1.0, 0.0, 0.0]), 0.1, np.array([0.0, 1.0, 0.0]))
        np.testing.assert_allclose(moved, [0.0, 0.1, 0.0], atol=1e-5)

    def sheet(self, frames, axes=None, radius=0.0):
        chains = []
        for x in (-0.1, 0.0, 0.1):
            rest = chain_rest(LENGTHS, start=(x, 0.1, 1.0), direction=SLANT)
            tails = np.array([[x, 0.1 + 0.2 * 0.15 * k / np.linalg.norm(SLANT), 1.0 - 0.15 * k / np.linalg.norm(SLANT)] for k in (1, 2, 3)])
            follow = np.repeat(tails[None], frames, axis=0)
            chains.append({"rest_relative": rest, "lengths": LENGTHS, "omegas": C.pendulum_omegas(LENGTHS, 1.8),
                           "radii": np.full((3, 1), radius), "follow_points": follow})
        return C.simulate_sheet(np.stack([np.eye(4)] * frames), chains, 1.0 / 24, axes, -np.inf, UP, np.array([0.0, 1.0, 0.0]))

    def test_a_still_sheet_stays_at_rest(self) -> None:
        for quaternions in self.sheet(20):
            np.testing.assert_allclose(np.abs(quaternions[..., 0]), 1.0, atol=1e-6)

    def test_a_heel_under_one_chain_moves_the_sheet_together(self) -> None:
        frames = 30
        axes = np.zeros((frames, 1, 2, 3))
        for f in range(frames):  # a short capsule (a heel) comes up under the middle chain's hem only
            axes[f, 0] = [[-0.02, 0.15, 0.6], [0.02, 0.15, 0.6]]
        turns = [C.quaternion_step_degrees(q[-1, 2], np.array([1.0, 0, 0, 0])) for q in self.sheet(frames, axes, 0.08)]
        self.assertGreater(turns[1], 1.0)
        self.assertGreater(turns[0], 0.1 * turns[1])  # without the spread they would not move at all
        self.assertGreater(turns[2], 0.1 * turns[1])


class Regions(unittest.TestCase):
    def test_wing_masks_split_sides_and_leave_the_arms_out(self) -> None:
        positions = np.array([[0.4, 0, 1], [-0.4, 0, 1], [0.0, 0, 1], [0.3, 0, 0.5], [-0.5, 0, 1.2]])
        dominant = ["Spine02", "Spine02", "Spine02", "LeftHand", "RightShoulder"]
        left, right = C.wing_masks(positions, dominant, np.zeros(3), FRONT, UP)
        lateral = np.cross(UP, FRONT)
        self.assertTrue(np.all((positions[left] @ lateral) > 0))
        self.assertTrue(np.all((positions[right] @ lateral) < 0))
        self.assertFalse(left[3] or right[3])
        self.assertEqual(int(left.sum() + right.sum()), 3)

    def test_cloak_mask_matches_the_cloak_check_region(self) -> None:
        from lib import tripo_checks

        rng = np.random.default_rng(7)
        positions = rng.uniform([-0.3, -0.3, 0.0], [0.3, 0.3, 1.0], (2000, 3))
        dominant = rng.choice(["Hips", "LeftUpLeg", "LeftArm", "Head"], 2000)
        hips = np.array([0.0, 0.0, 0.5])
        mask = C.cloak_mask(positions, dominant, hips, FRONT, UP, 1.0)
        yup = positions[:, [0, 2, 1]] * np.array([1.0, 1.0, -1.0])  # the same points with y up and +z in front
        expected = tripo_checks.cloak_region(yup, dominant, hips[[0, 2, 1]] * np.array([1.0, 1.0, -1.0]), np.array([0.0, 0.0, 1.0]), 1.0, C.CLOAK_BONES)
        np.testing.assert_array_equal(mask, expected)

    def test_the_cloak_grows_into_loose_torso_cloth_only(self) -> None:
        # a strip of vertices behind the hips at mid height, the first one in the check's region
        positions = np.array([[x, 0.2, 0.5] for x in np.linspace(0.0, 0.5, 6)] + [[0.0, 0.0, 0.0]])  # the last: a foot on the ground
        edges = np.stack([np.arange(5), np.arange(1, 6)], axis=1)
        check = np.arange(7) == 0
        dominant = ["Hips", "LeftUpLeg", "Spine01", "LeftArm", "Hips", "Hips", "LeftFoot"]
        grown = C.cloak_rebind_mask(check, positions, edges, dominant, np.array([0.0, 0.0, 0.5]), FRONT, UP, 1.0, [])
        np.testing.assert_array_equal(np.where(grown)[0], [0, 1, 2])  # the arm's vertex stops the growth
        far_leg = [(np.array([0.1, 0.2, 0.4]), np.array([0.1, 0.2, 0.6]), 0.05)]  # a limb whose skin lies on vertex 1
        grown = C.cloak_rebind_mask(check, positions, edges, dominant, np.array([0.0, 0.0, 0.5]), FRONT, UP, 1.0, far_leg)
        np.testing.assert_array_equal(np.where(grown)[0], [0])

    def wing_chain(self):
        lateral = np.cross(UP, FRONT)  # the unit's left
        return np.array([C.unit(lateral + 0.3 * UP), C.unit(lateral), C.unit(lateral - 0.5 * UP)]), lateral

    WING = {"u_min": 0.0, "normal": np.array([0.0, -1.0, 0.0]), "sweep": 80.0, "wrap": 70.0, "down": 60.0, "droop": 20.0}

    def pose(self, fold=0.0, wrap=0.0, sweep=1.0, droop=0.0):
        return {"fold": fold, "wrap": wrap, "sweep": sweep, "droop": droop}

    def test_a_spread_still_wing_keeps_its_rest_directions(self) -> None:
        rest, _lateral = self.wing_chain()
        posed = C.wing_pose_directions(rest, 0.5, self.WING, UP, FRONT, self.pose(), np.zeros(3))
        np.testing.assert_allclose(posed, rest, atol=1e-9)

    def test_a_folded_wing_lies_behind_the_body(self) -> None:
        rest, lateral = self.wing_chain()
        posed = C.wing_pose_directions(rest, 0.5, self.WING, UP, FRONT, self.pose(fold=1.0), np.zeros(3))
        self.assertTrue(np.all(posed @ -FRONT > 0.5))
        self.assertTrue(np.all(posed @ lateral < 0.5))

    def test_a_flap_or_a_raise_lifts_the_wing(self) -> None:
        rest, _lateral = self.wing_chain()
        raised = C.wing_pose_directions(rest, 0.5, self.WING, UP, FRONT, self.pose(), np.array([20.0, 0.0, 0.0]))
        self.assertTrue(np.all(raised @ UP > rest @ UP))
        lifted = C.wing_pose_directions(rest, 0.5, self.WING, UP, FRONT, dict(self.pose(), **{"raise": 20.0}), np.zeros(3))
        self.assertTrue(np.all(lifted @ UP > rest @ UP))

    def test_every_pose_keeps_the_side_floor_and_a_turned_torso_adds_to_it(self) -> None:
        rest, lateral = self.wing_chain()
        wing = dict(self.WING, side=30.0)
        spread = C.wing_pose_directions(rest, 0.5, wing, UP, FRONT, self.pose(), np.zeros(3))
        swung = rest @ C.axis_angle_matrix(UP, math.radians(30.0)).T
        np.testing.assert_allclose(spread, swung, atol=1e-9)  # an unfolded wing still swings back by the floor
        twisted = C.wing_pose_directions(rest, 0.5, wing, UP, FRONT, dict(self.pose(), twist=30.0), np.zeros(3))
        self.assertLess(float(twisted[1] @ FRONT), float(spread[1] @ FRONT))  # further back
        capped = C.wing_pose_directions(rest, 0.5, wing, UP, FRONT, dict(self.pose(), twist=500.0), np.zeros(3))
        full = C.wing_pose_directions(rest, 0.5, dict(wing, side=self.WING["sweep"]), UP, FRONT, self.pose(), np.zeros(3))
        np.testing.assert_allclose(capped, full, atol=1e-9)  # never past the full swing
        # the torso turning its front toward the unit's left brings the right wing forward, not the left one
        carry = C.axis_angle_matrix(UP, math.radians(25.0))
        self.assertAlmostEqual(C.side_twist(carry, UP, FRONT, "R"), 25.0, places=6)
        self.assertEqual(C.side_twist(carry, UP, FRONT, "L"), 0.0)
        del lateral

    def test_the_side_floor_is_where_swinging_back_stops_paying(self) -> None:
        # a flat body facing -y, and a wing sheet beside its back that hides it from the left side until it swings back
        body = np.array([[x, y, z] for x in np.linspace(-0.15, 0.15, 7) for y in np.linspace(-0.1, 0.1, 9) for z in np.linspace(0.5, 1.5, 26)])
        root = np.array([0.15, 0.05, 1.3])  # inside the body's depth seen from the side, outside it seen from behind
        wing = np.array([[0.15 + r, 0.05, 1.3 + h] for r in np.linspace(0.0, 0.6, 25) for h in np.linspace(-0.6, 0.3, 19)])
        most = 80.0
        floor, ceiling = C.wing_side_floor(wing, body, root, FRONT, UP, 2.0, most)
        self.assertGreater(floor, 0.0)
        self.assertLess(floor, most)
        self.assertLessEqual(C.wing_side_cover(wing, body, root, FRONT, UP, 2.0, floor), ceiling)
        self.assertGreater(C.wing_side_cover(wing, body, root, FRONT, UP, 2.0, 0.0), ceiling)

    def test_the_face_turn_shows_the_face_to_the_side_and_the_map(self) -> None:
        normal = FRONT  # a wing spread in the frontal plane: edge-on from the side
        self.assertAlmostEqual(C.face_shares(normal, FRONT, UP)["side"], 0.0)
        sweep, tilt = C.face_turn(normal, FRONT, UP, 0.0, 80.0)
        shares = C.face_shares(C.turned_normal(normal, FRONT, UP, sweep, tilt), FRONT, UP)
        self.assertGreater(min(shares.values()), 0.5)
        self.assertGreater(tilt, 0.0)
        # a turn the side-view rule refuses is never taken; with none left it falls back to the floor
        self.assertEqual(C.face_turn(normal, FRONT, UP, 20.0, 80.0, fits=lambda s, t: False), (20.0, 0.0))
        sweep, tilt = C.face_turn(normal, FRONT, UP, 0.0, 80.0, fits=lambda s, t: t == 0.0)
        self.assertEqual(tilt, 0.0)

    def test_the_death_folds_before_the_fall_and_sags_after_it(self) -> None:
        hips = np.r_[np.full(40, 1.0), np.linspace(1.0, 0.4, 30), np.full(30, 0.4)]
        fall = C.fall_frame(hips, 2.0)
        self.assertEqual(fall, 40 + int(np.ceil(C.FALL_DROP_SHARE * 2.0 / (0.6 / 29))))
        self.assertIsNone(C.fall_frame(np.full(50, 1.0), 2.0))
        pose = C.wing_role_pose("death", 100, {"fall": fall})
        end = int(C.FOLD_SHARE * 99) + 1
        self.assertAlmostEqual(float(pose["fold"][end]), 1.0, places=6)  # folded before the knees bend
        self.assertEqual(float(pose["droop"][fall - 1]), 0.0)  # and it sags only once the body falls
        self.assertAlmostEqual(float(pose["droop"][-1]), 1.0)

    def test_the_move_beats_in_step_with_the_walk(self) -> None:
        frames = 61
        t = np.linspace(0.0, 1.0, frames)
        stride = 0.3 * np.cos(2.0 * math.pi * 2 * t + 0.4)  # two strides: four steps
        left = np.outer(stride, FRONT) / 2.0
        right = -left
        beats, phase = C.walk_beats(left, right, FRONT)
        self.assertEqual(beats, 4)
        pose = C.wing_role_pose("move", frames, {"beats": beats, "beat_phase": phase})
        flap = np.sin(pose["phase"])
        strikes = [int(i) for i in range(1, frames - 1) if abs(stride[i]) >= abs(stride[i - 1]) and abs(stride[i]) >= abs(stride[i + 1])]
        for i in strikes:
            self.assertLess(flap[i], -0.9)  # a down-stroke as a foot strikes
        self.assertAlmostEqual(float(flap[0]), float(flap[-1]), places=9)  # it still loops
        self.assertIsNone(C.walk_beats(np.zeros((frames, 3)), np.zeros((frames, 3)), FRONT))

    def test_idle_is_folded_and_still_and_move_is_half_spread_and_beating(self) -> None:
        idle, move = C.WING_ROLES["idle"], C.WING_ROLES["move"]
        self.assertGreater(idle["fold"], move["fold"])
        self.assertGreater(move["flap"], 3 * idle["flap"])
        self.assertTrue(move.get("steps"))

    def test_a_dying_wing_is_lifted_above_the_knees(self) -> None:
        rest, lateral = self.wing_chain()
        low = np.array([C.unit(lateral - 1.5 * UP)] * 3)  # a lowest chain that hangs steeply down
        wing = dict(self.WING, low_rest=low, low_lengths=np.array([0.3, 0.3, 0.3]), low_u=0.0)
        stage = {"up": UP, "front": FRONT}
        root = np.array([0.1, 0.0, 1.4])
        pose = self.pose()
        lift = C.knee_raise(wing, pose, np.zeros(3), np.eye(3), root, "L", stage, 0.9)
        self.assertGreater(lift, 0.0)
        directions = C.wing_pose_directions(low, 0.0, wing, UP, FRONT, dict(pose, **{"raise": lift}), np.zeros(3))
        joints = root + np.cumsum(directions * 0.3, axis=0)
        self.assertGreaterEqual(float((joints @ UP).min()), 0.9 - 1e-9)
        self.assertEqual(C.knee_raise(wing, pose, np.zeros(3), np.eye(3), root, "L", stage, 0.0), 0.0)
        del rest

    def test_a_down_stroke_stops_at_the_wings_down_room(self) -> None:
        rest, _lateral = self.wing_chain()
        deep = C.wing_pose_directions(rest, 0.5, self.WING, UP, FRONT, self.pose(), np.array([-200.0, 0.0, 0.0]))
        capped = C.wing_pose_directions(rest, 0.5, self.WING, UP, FRONT, self.pose(), np.array([-60.0, 0.0, 0.0]))
        np.testing.assert_allclose(deep, capped, atol=1e-9)

    def test_the_wing_limits_follow_the_body(self) -> None:
        self.assertAlmostEqual(C.wing_down_degrees(np.array([1.0, 0.0, 0.0]), -UP), 90.0)
        self.assertAlmostEqual(C.wing_droop_degrees(C.unit(np.array([1.0, 0.0, 1.0])), UP), 45.0)
        self.assertEqual(C.wing_droop_degrees(np.array([1.0, 0.0, -1.0]), UP), 0.0)

    def test_a_dying_wing_sags_level_in_its_own_plane(self) -> None:
        rest, _lateral = self.wing_chain()
        sagged = C.wing_pose_directions(rest, 0.5, dict(self.WING, droop=C.wing_droop_degrees(rest[0], UP)), UP, FRONT, self.pose(sweep=0.0, droop=1.0), np.zeros(3))
        self.assertAlmostEqual(float(sagged[0] @ UP), 0.0, places=9)
        np.testing.assert_allclose(sagged @ FRONT, 0.0, atol=1e-9)  # it stays in the wing's own plane

    def test_a_dying_wing_folds_back_while_the_torso_stands(self) -> None:
        rest, lateral = self.wing_chain()
        lengths = np.array([0.1, 0.1, 0.1])
        relative = chain_rest(lengths, start=(0.1, 0.0, 1.4), direction=rest[0])
        plan = {"lengths": lengths, "wing": dict(self.WING, droop=0.0), "side": "L", "rest_directions": np.array([rest[0]] * 3),
                "parent_rest": np.eye(4), "chain_u": 0.5, "rest_relative": relative}
        stage = {"up": UP, "front": FRONT, "ground": -10.0}
        frames = 60
        standing = C.wing_quaternions(plan, np.stack([np.eye(4)] * frames), "death", stage)
        lying = np.eye(4)
        lying[:3, :3] = C.axis_angle_matrix(lateral, math.radians(90.0))  # the torso pitched flat
        fallen = C.wing_quaternions(plan, np.stack([lying] * frames), "death", stage)
        swung = C.quaternion_step_degrees(standing[-1, 0], np.array([1.0, 0, 0, 0]))
        flat = C.quaternion_step_degrees(fallen[-1, 0], np.array([1.0, 0, 0, 0]))
        self.assertGreater(swung, 45.0)  # standing: folded back along the back
        self.assertLess(flat, swung)  # lying: it stays in the body's back plane, flat

    def test_looping_wing_roles_end_as_they_start(self) -> None:
        for role in C.LOOPING_ROLES:
            pose = C.wing_role_pose(role, 57)
            flaps = C.flap_angles(pose["phase"], pose["amplitude"], 3)
            np.testing.assert_allclose(flaps[0], flaps[-1], atol=1e-9)
            self.assertAlmostEqual(float(pose["fold"][0]), float(pose["fold"][-1]))

    def test_a_dying_wing_folds_by_the_end_and_the_sweep_clears_the_back(self) -> None:
        pose = C.wing_role_pose("death", 100)
        self.assertEqual(float(pose["fold"][0]), 0.0)
        self.assertAlmostEqual(float(pose["fold"][-1]), 1.0)
        self.assertAlmostEqual(float(pose["droop"][-1]), 1.0)
        self.assertAlmostEqual(C.wing_sweep_degrees(1.0, 0.0), 90.0)
        self.assertLess(C.wing_sweep_degrees(0.4, 0.05), 90.0)

    def test_the_front_cover_counts_torso_cells_a_wing_hides(self) -> None:
        grid = np.array([[x, y, 0.0] for x in np.linspace(-0.1, 0.1, 11) for y in np.linspace(0.5, 0.9, 21)])  # a flat torso facing +z
        wing_behind = grid[:50] + np.array([0.0, 0.0, -0.2])
        wing_front = grid[:50] + np.array([0.0, 0.0, 0.2])
        torso = np.r_[np.ones(len(grid), bool), np.zeros(50, bool)]
        wings = ~torso
        front = np.array([0.0, 0.0, 1.0])
        up = np.array([0.0, 1.0, 0.0])
        self.assertEqual(C.front_cover_share(np.vstack([grid, wing_behind]), torso, wings, front, up, 1.0), 0.0)
        hidden = C.front_cover_share(np.vstack([grid, wing_front]), torso, wings, front, up, 1.0)
        self.assertGreater(hidden, 0.1)
        self.assertLess(hidden, 0.5)

    def test_the_side_views_count_only_the_parts_a_viewer_sees(self) -> None:
        # seen from +z: a torso plate in front, an arm plate behind it, and a wing nearer the camera than both over half of them
        torso = np.array([[x, y, 0.0] for x in np.linspace(-0.1, 0.1, 11) for y in np.linspace(0.5, 0.9, 21)])
        arm = torso + np.array([0.0, 0.0, -0.1])
        wing = torso[:110] + np.array([0.0, 0.0, 0.2])
        posed = np.vstack([torso, arm, wing])
        body = np.r_[np.ones(len(torso) + len(arm), bool), np.zeros(len(wing), bool)]
        limbs = np.r_[np.zeros(len(torso), bool), np.ones(len(arm), bool), np.zeros(len(wing), bool)]
        front, up = np.array([0.0, 0.0, 1.0]), np.array([0.0, 1.0, 0.0])
        self.assertGreater(C.front_cover_share(posed, body, ~body, front, up, 1.0), 0.3)
        self.assertEqual(C.front_cover_share(posed, body, ~body, front, up, 1.0, judged=limbs), 0.0)  # the torso already hides the arm

    def test_points_inside_at_rest_are_not_counted(self) -> None:
        # a closed box body and two cloth points: one modelled inside it, one that moves in
        corners = np.array([[x, y, z] for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)], float)
        faces = np.array([[0, 1, 3], [0, 3, 2], [4, 6, 7], [4, 7, 5], [0, 4, 5], [0, 5, 1], [2, 3, 7], [2, 7, 6], [0, 2, 6], [0, 6, 4], [1, 5, 7], [1, 7, 3]])
        rest = np.vstack([corners, [[0.0, 0.0, 0.0], [0.0, 0.0, 3.0]]])
        moved = rest.copy()
        moved[9] = [0.0, 0.2, 0.1]
        body = np.r_[np.ones(8, bool), False, False]
        cloth = ~body
        self.assertEqual(C.inside_share_series([moved], faces, body, cloth, 2.0, 0.01)[0], 1.0)
        self.assertEqual(C.inside_share_series([moved], faces, body, cloth, 2.0, 0.01, rest=rest)[0], 1.0)
        self.assertEqual(C.inside_share_series([rest], faces, body, cloth, 2.0, 0.01, rest=rest)[0], 0.0)

    def test_turning_an_open_body_does_not_put_cloth_inside_it(self) -> None:
        # a box with its back face cut out (where a region was cut from a single skin), and cloth points on that opening; the ray
        # votes run along fixed world directions, the winding number does not care how the body is turned
        corners = np.array([[x, y, z] for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)], float)
        faces = np.array([[0, 1, 3], [0, 3, 2], [4, 6, 7], [4, 7, 5], [0, 4, 5], [0, 5, 1], [2, 3, 7], [2, 7, 6], [1, 5, 7], [1, 7, 3]])
        cloth = np.array([[x, y, -1.05] for x in (-0.5, 0.0, 0.5) for y in (-0.5, 0.0, 0.5)])  # just outside the open face z = -1
        rest = np.vstack([corners, cloth])
        body = np.r_[np.ones(8, bool), np.zeros(len(cloth), bool)]
        winding = C.winding_numbers(cloth, corners[faces])
        self.assertTrue(np.all(winding < C.WINDING_INSIDE))
        for axis in (np.array([1.0, 0.0, 0.0]), np.array([0.0, 1.0, 0.0]), C.unit(np.array([1.0, 1.0, 0.3]))):
            for degrees in (30.0, 60.0, 90.0, 135.0):
                turned = rest @ C.axis_angle_matrix(axis, math.radians(degrees)).T
                self.assertEqual(C.inside_share_series([turned], faces, body, ~body, 2.0, 0.01, rest=rest)[0], 0.0)
        self.assertGreater(float(C.winding_numbers(np.zeros((1, 3)), corners[faces])[0]), C.WINDING_INSIDE)  # deep in, it is inside

    def test_plates_ride_the_bone_nearest_the_root_and_go_rigid(self) -> None:
        depth = C.bone_depths({"Hips": None, "Spine02": "Hips", "LeftShoulder": "Spine02", "LeftArm": "LeftShoulder"})
        rows = [{"LeftArm": 0.6, "LeftShoulder": 0.4}, {"LeftArm": 0.7, "LeftShoulder": 0.3}, {"LeftArm": 1.0}]
        mask = np.array([True, True, False])
        self.assertEqual(C.plate_bone(rows, mask, depth), "LeftShoulder")
        positions = np.array([[0.0, 0.0, 0.0], [0.01, 0.0, 0.0], [1.0, 0.0, 0.0]])
        edges = np.array([[0, 1], [1, 2]])
        new, report = C.rigid_plates(rows, positions, edges, {"left_pauldron": mask}, depth)
        self.assertEqual(new[0], {"LeftShoulder": 1.0})
        self.assertEqual(new[1], {"LeftShoulder": 1.0})
        self.assertEqual(new[2], {"LeftArm": 1.0})  # beyond the ring
        self.assertEqual(report["left_pauldron"]["bone"], "LeftShoulder")

    def test_a_plates_ring_stops_before_another_plate(self) -> None:
        depth = C.bone_depths({"Hips": None, "Spine02": "Hips", "LeftShoulder": "Spine02", "LeftArm": "LeftShoulder"})
        positions = np.stack([np.arange(12) * 0.01, np.zeros(12), np.zeros(12)], axis=1)
        edges = np.stack([np.arange(11), np.arange(1, 12)], axis=1)
        rows = [{"Spine02": 0.6, "LeftShoulder": 0.4}] * 4 + [{"LeftShoulder": 0.5, "LeftArm": 0.5}] * 8
        chest = np.arange(12) < 4
        pauldron = (np.arange(12) >= 5) & (np.arange(12) < 9)
        new, _report = C.rigid_plates(rows, positions, edges, {"chest_plate": chest, "left_pauldron": pauldron}, depth)
        for index in np.where(pauldron)[0]:
            self.assertEqual(new[index], {"LeftShoulder": 1.0})  # the chest plate's ring does not bend the pauldron
        for index in np.where(chest)[0]:
            self.assertEqual(new[index], {"Spine02": 1.0})

    def test_touching_plates_ride_one_bone(self) -> None:
        depth = C.bone_depths({"Hips": None, "Spine02": "Hips", "LeftShoulder": "Spine02", "LeftArm": "LeftShoulder"})
        positions = np.stack([np.arange(8) * 0.01, np.zeros(8), np.zeros(8)], axis=1)
        edges = np.stack([np.arange(7), np.arange(1, 8)], axis=1)
        rows = [{"Spine02": 0.6, "LeftShoulder": 0.4}] * 4 + [{"LeftShoulder": 0.5, "LeftArm": 0.5}] * 4
        masks = {"chest_plate": np.arange(8) < 4, "left_pauldron": np.arange(8) >= 4}
        self.assertEqual(C.plate_assemblies(masks, edges), [["chest_plate", "left_pauldron"]])
        new, report = C.rigid_plates(rows, positions, edges, masks, depth)
        self.assertEqual({row_name for row in new for row_name in row}, {"Spine02"})  # no seam between them to tear
        self.assertEqual(report["left_pauldron"]["bone"], "Spine02")

    def test_plate_masks_find_the_shoulders_and_the_chest(self) -> None:
        heads = {"Hips": np.array([0.0, 1.0, 0.0]), "Spine01": np.array([0.0, 1.2, 0.0]), "Spine02": np.array([0.0, 1.3, 0.0]),
                 "neck": np.array([0.0, 1.5, 0.0]), "LeftShoulder": np.array([0.05, 1.45, 0.0]), "LeftArm": np.array([0.2, 1.45, 0.0]),
                 "LeftForeArm": np.array([0.2, 1.15, 0.0]), "RightShoulder": np.array([-0.05, 1.45, 0.0]), "RightArm": np.array([-0.2, 1.45, 0.0]),
                 "RightForeArm": np.array([-0.2, 1.15, 0.0])}
        up, front = np.array([0.0, 1.0, 0.0]), np.array([0.0, 0.0, 1.0])  # these joints stand with y up and face +z; +x is their left
        points = np.array([[0.25, 1.5, 0.0], [-0.25, 1.5, 0.0], [0.0, 1.35, -0.15], [0.0, 1.35, 0.15], [0.2, 1.0, 0.0]])
        masks = C.plate_masks(points, heads, front, up, 0.15)
        np.testing.assert_array_equal(masks["left_pauldron"], [True, False, False, False, False])
        np.testing.assert_array_equal(masks["right_pauldron"], [False, True, False, False, False])
        np.testing.assert_array_equal(masks["chest_plate"], [False, False, False, True, False])
        self.assertFalse(any(m[4] for m in masks.values()))

    def test_flap_is_delayed_down_the_chain(self) -> None:
        phase = np.linspace(0.0, 2.0 * math.pi, 101)
        angles = C.flap_angles(phase, np.full(101, 10.0), 3)
        self.assertAlmostEqual(float(angles[:, 0].max()), 10.0, places=1)
        peaks = [int(np.argmax(angles[:, k])) for k in range(3)]
        self.assertTrue(peaks[0] < peaks[1] < peaks[2])


class WingChecks(unittest.TestCase):
    """The wing parts of tripo/tripo_checks.py: per-view limits, the edge-on rule and the idle and move rule."""

    @staticmethod
    def row(cover=None, face=None, motion=0.1):
        return {"in_body_worst_share": 0.0, "in_body_frame": 0, "below_ground_worst_share": 0.0, "below_ground_frame": 0,
                "stretch_worst_share": 0.0, "stretch_frame": 0, "cover": cover or {}, "face": face or {}, "map_motion": motion}

    def rules(self, clip, row):
        import tripo_checks as TC

        return [(item["rule"], item.get("view")) for item in TC.chain_row_findings(clip, "wings", row)]

    def test_side_views_judge_the_limbs_against_their_own_limit(self) -> None:
        import tripo_checks as TC

        self.assertEqual(self.rules("u_attack", self.row({"left": TC.MAX_WING_SIDE_COVER - 0.01, "front": 0.0})), [])
        self.assertEqual(self.rules("u_attack", self.row({"right": TC.MAX_WING_SIDE_COVER + 0.01})), [("TRIPO-WING-FRONT", "right")])
        self.assertEqual(self.rules("u_idle", self.row({"map": TC.MAX_WING_COVER_SHARE + 0.01})), [("TRIPO-WING-FRONT", "map")])
        self.assertGreater(TC.MAX_WING_SIDE_COVER, 0.053)  # the side views a fresh review accepted (round 2 retreat)
        self.assertLess(TC.MAX_WING_SIDE_COVER, 0.175)  # and the least it failed (round 2 defend)

    def test_only_a_beating_wing_is_failed_for_showing_its_edge(self) -> None:
        import tripo_checks as TC

        edge = {"left": TC.MIN_WING_FACE_SHARE - 0.1, "right": 0.6, "map": 0.6}
        self.assertEqual(self.rules("u_retreat", self.row(face=edge)), [("TRIPO-WING-EDGE-ON", "left")])
        self.assertEqual(self.rules("u_idle", self.row(face=edge)), [])  # folded and still: an edge is fine
        self.assertEqual(self.rules("u_death", self.row(face=edge)), [])

    def test_idle_and_move_must_differ_at_map_size(self) -> None:
        import tripo_checks as TC

        alike = {"u_idle": {"wings": self.row(motion=0.13)}, "u_move": {"wings": self.row(motion=0.21)}}  # the round 2 demon
        self.assertEqual([item["rule"] for item in TC.idle_move_findings(alike)], ["TRIPO-WING-IDLE-MOVE"])
        apart = {"u_idle": {"wings": self.row(motion=0.06)}, "u_move": {"wings": self.row(motion=0.42)}}
        self.assertEqual(TC.idle_move_findings(apart), [])
        self.assertEqual(TC.idle_move_findings({"u_idle": {"wings": self.row()}}), [])


if __name__ == "__main__":
    unittest.main()
