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

    def test_a_spread_still_wing_keeps_its_rest_directions(self) -> None:
        rest, _lateral = self.wing_chain()
        posed = C.wing_pose_directions(rest, 0.5, 0.0, np.array([0.0, -1.0, 0.0]), UP, FRONT, 0.0, 0.0, np.zeros(3), 80.0)
        np.testing.assert_allclose(posed, rest, atol=1e-9)

    def test_a_folded_wing_lies_behind_the_body(self) -> None:
        rest, lateral = self.wing_chain()
        posed = C.wing_pose_directions(rest, 0.5, 0.0, np.array([0.0, -1.0, 0.0]), UP, FRONT, 1.0, 0.0, np.zeros(3), 80.0)
        self.assertTrue(np.all(posed @ -FRONT > 0.5))
        self.assertTrue(np.all(posed @ lateral < 0.5))

    def test_a_wrapped_wing_comes_forward_and_a_flap_raises_it(self) -> None:
        rest, _lateral = self.wing_chain()
        wrapped = C.wing_pose_directions(rest, 0.5, 0.0, np.array([0.0, -1.0, 0.0]), UP, FRONT, 0.0, 1.0, np.zeros(3), 80.0)
        self.assertTrue(np.all(wrapped @ FRONT > 0.5))
        raised = C.wing_pose_directions(rest, 0.5, 0.0, np.array([0.0, -1.0, 0.0]), UP, FRONT, 0.0, 0.0, np.array([20.0, 0.0, 0.0]), 80.0)
        self.assertTrue(np.all(raised @ UP > rest @ UP))

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
        self.assertAlmostEqual(C.wing_sweep_degrees(1.0, 0.0), 90.0)
        self.assertLess(C.wing_sweep_degrees(0.4, 0.05), 90.0)

    def test_flap_is_delayed_down_the_chain(self) -> None:
        phase = np.linspace(0.0, 2.0 * math.pi, 101)
        angles = C.flap_angles(phase, np.full(101, 10.0), 3)
        self.assertAlmostEqual(float(angles[:, 0].max()), 10.0, places=1)
        peaks = [int(np.argmax(angles[:, k])) for k in range(3)]
        self.assertTrue(peaks[0] < peaks[1] < peaks[2])


if __name__ == "__main__":
    unittest.main()
