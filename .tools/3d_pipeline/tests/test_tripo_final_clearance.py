"""The final clearance step's maths on synthetic data: a hand turned about its own joint in the world, the held part's split from the body."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

import numpy as np

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))

from lib import pdx_deform, tripo_clearance as CL, tripo_final_clearance as F


def rotation_z(degrees: float) -> np.ndarray:
    a = np.radians(degrees)
    return np.array([[np.cos(a), -np.sin(a), 0.0], [np.sin(a), np.cos(a), 0.0], [0.0, 0.0, 1.0]])


def quaternion(matrix: np.ndarray) -> np.ndarray:
    from lib import tripo_pose

    return tripo_pose._quaternion_from_matrix(matrix)


class HandTurn(unittest.TestCase):
    def new_world(self, parent_degrees: float, local_degrees: float, vector: np.ndarray) -> np.ndarray:
        world = np.tile(np.eye(4), (1, 2, 1, 1))
        world[0, 0, :3, :3] = rotation_z(parent_degrees)
        q = np.array([quaternion(rotation_z(local_degrees))])
        out = F._rotation_vectors_to_quaternions(world, 0, 1, q, np.array([vector]))
        return world[0, 0, :3, :3] @ pdx_deform._quaternion_matrices(out)[0]

    def test_the_turn_is_a_world_turn_about_the_hand_whatever_the_parent_does(self) -> None:
        vector = np.array([0.0, 0.0, np.radians(30.0)])
        for parent in (0.0, 70.0, -120.0):
            before = rotation_z(parent) @ rotation_z(25.0)
            after = self.new_world(parent, 25.0, vector)
            np.testing.assert_allclose(after, CL.rotvec_matrix(vector) @ before, atol=1e-5)

    def test_a_frame_without_a_turn_keeps_its_rotation_exactly(self) -> None:
        q = np.array([quaternion(rotation_z(40.0))])
        world = np.tile(np.eye(4), (1, 2, 1, 1))
        out = F._rotation_vectors_to_quaternions(world, 0, 1, q, np.zeros((1, 3)))
        np.testing.assert_array_equal(out, q)

    def test_the_new_rotation_stays_in_the_hemisphere_of_the_old_one(self) -> None:
        q = np.array([quaternion(rotation_z(170.0))])
        world = np.tile(np.eye(4), (1, 2, 1, 1))
        out = F._rotation_vectors_to_quaternions(world, 0, 1, q, np.array([[0.0, 0.0, np.radians(20.0)]]))
        self.assertGreater(float(out[0] @ q[0]), 0.0)


class LocalSmoothing(unittest.TestCase):
    def test_only_the_frames_round_a_fast_step_are_smoothed(self) -> None:
        turns = np.zeros((30, 3))
        turns[5:9, 2] = np.radians(60.0)  # a turn far from the fast step keeps its full size
        turns[20, 2] = np.radians(80.0)
        out = F._smoothed_near(turns, [20], 2)
        np.testing.assert_array_equal(out[:15], turns[:15])
        self.assertLess(out[20, 2], turns[20, 2])
        self.assertGreater(out[19, 2], 0.0)
        np.testing.assert_array_equal(F._smoothed_near(turns, [], 3), turns)


class Ramp(unittest.TestCase):
    def test_a_turn_that_starts_and_ends_in_one_frame_fades_in_and_out_by_the_step(self) -> None:
        turns = np.zeros((20, 3))
        turns[8:12, 2] = np.radians(40.0)
        needed = turns[:, 2] > 0
        out = F.ramped(turns, needed)
        sizes = np.degrees(np.linalg.norm(out, axis=1))
        self.assertTrue(np.all(np.abs(np.diff(sizes)) <= F.RAMP_DEGREES + 1e-6))
        self.assertTrue(np.all(sizes[8:12] >= 40.0 - 1e-6), "the frames that needed the turn keep at least it")
        self.assertGreater(sizes[7], 0.0)
        self.assertGreater(sizes[12], 0.0)
        self.assertEqual(sizes[0], 0.0)

    def test_a_fade_that_puts_the_prop_in_the_body_is_cut_to_the_share_that_clears_it(self) -> None:
        turns = np.zeros((10, 3))
        turns[5, 2] = np.radians(40.0)
        needed = turns[:, 2] > 0
        refused = F.ramped(turns, needed, clear=lambda frame, vector: False)
        np.testing.assert_array_equal(refused, turns)
        half = F.ramped(turns, needed, clear=lambda frame, vector: float(np.linalg.norm(vector)) <= np.radians(16.0))
        self.assertGreater(np.linalg.norm(half[4]), 0.0)
        self.assertLessEqual(np.degrees(np.linalg.norm(half[4])), 16.0 + 1e-6)

    def test_no_turn_stays_no_turn_and_small_steps_are_not_touched(self) -> None:
        self.assertTrue(np.all(F.ramped(np.zeros((5, 3)), np.zeros(5, bool)) == 0.0))
        small = np.zeros((6, 3))
        small[:, 0] = np.radians([0.0, 3.0, 6.0, 9.0, 6.0, 3.0])
        np.testing.assert_allclose(F.ramped(small, np.ones(6, bool)), small)


class Split(unittest.TestCase):
    def mesh(self):
        # vertices 0..5: body (Spine), 6..8: the weapon (own bone), 9..11: the shield (own bone), all weighted wholly to their bone
        bones = ["Spine", "RightHand", "Weapon", "LeftHand", "Shield"]
        dominant = [0] * 6 + [2] * 3 + [4] * 3
        joints = np.array([[d, 0, 0, 0] for d in dominant])
        weights = np.zeros((12, 4))
        weights[:, 0] = 1.0
        triangles = np.array([[0, 1, 2], [3, 4, 5], [0, 6, 7], [9, 10, 11], [1, 2, 3]])
        return SimpleNamespace(bones=bones, parents=[-1, 0, 1, 0, 3], joints=joints, weights=weights, triangles=triangles)

    def test_the_held_part_and_the_other_part_are_not_the_body(self) -> None:
        held, triangles, body = F.part_split(self.mesh(), "Weapon", ["Shield"])
        self.assertEqual(np.nonzero(held)[0].tolist(), [6, 7, 8])
        self.assertEqual(np.nonzero(body)[0].tolist(), [0, 1, 2, 3, 4, 5])
        self.assertEqual(triangles.tolist(), [[0, 1, 2], [3, 4, 5], [1, 2, 3]], "only triangles of body vertices, renumbered over the body")

    def test_a_part_is_held_by_the_hand_its_bone_hangs_from(self) -> None:
        mesh = self.mesh()
        self.assertEqual(F.holding_hand(mesh, "Weapon"), "RightHand")
        self.assertEqual(F.holding_hand(mesh, "Shield"), "LeftHand")
        self.assertIsNone(F.holding_hand(mesh, "RightHand"), "a part bound to the hand itself has no bone of its own")
        self.assertIsNone(F.holding_hand(mesh, "Spine"))


class Stage(unittest.TestCase):
    def run_stage(self, spec, weapon):
        import tempfile
        from unittest import mock

        import run_pilot

        with tempfile.TemporaryDirectory() as folder:
            staged = Path(folder)
            for role in ("idle", "attack"):
                (staged / f"u_{role}.anim").write_bytes(b"x")
            records = {"u_idle.anim": {}, "u_attack.anim": {}}
            with mock.patch.object(run_pilot, "clear_held_props", lambda mesh, anim, role, held: {"role": role}):
                run_pilot.clear_staged_props(staged, staged, spec, ["idle", "attack"], weapon, records)
        return records

    def test_every_clip_of_an_armed_unit_is_cleared_and_recorded(self) -> None:
        records = self.run_stage({"runtime_stem": "u"}, [{"bone": "Weapon"}])
        self.assertEqual(records["u_attack.anim"]["clear_props"], {"role": "attack"})
        self.assertIn("staged", records["u_idle.anim"])

    def test_an_unarmed_unit_and_the_switch_leave_the_clips_alone(self) -> None:
        self.assertNotIn("clear_props", self.run_stage({"runtime_stem": "u"}, [])["u_idle.anim"])
        off = self.run_stage({"runtime_stem": "u", "tripo": {"clear_props": False}}, [{"bone": "Weapon"}])
        self.assertNotIn("clear_props", off["u_idle.anim"])


class Drop(unittest.TestCase):
    def test_a_weapon_has_landed_where_its_centre_stops_moving(self) -> None:
        centres = np.zeros((40, 3))
        centres[:12, 0] = np.linspace(1.0, 0.1, 12)  # in the air until frame 12
        centres[12:, 0] = 0.0
        self.assertEqual(F.landing_frame(centres, 1.0), 12)

    def test_a_weapon_that_never_moves_has_landed_at_the_start(self) -> None:
        self.assertEqual(F.landing_frame(np.ones((10, 3)), 1.0), 0)

    def test_the_shift_is_eased_in_and_then_held(self) -> None:
        ramp = F._smoothstep(20, 5, 13)
        self.assertEqual(float(ramp[5]), 0.0)
        self.assertEqual(float(ramp[13]), 1.0)
        self.assertTrue(np.all(np.diff(ramp) >= 0.0))
        self.assertTrue(np.all(ramp[13:] == 1.0))

    def test_the_final_solve_may_turn_past_the_grip_stages_sixty_degrees_by_the_smallest_angle_first(self) -> None:
        angles = list(CL.ANGLES_DEGREES)
        self.assertEqual(angles, sorted(angles))
        self.assertGreaterEqual(angles[-1], F.MAX_TURN_DEGREES)
        self.assertEqual(CL.MAX_ANGLE_DEGREES, 60.0, "the grip stage keeps its own cap")

    def test_a_part_without_location_keys_is_left_alone(self) -> None:
        mesh = SimpleNamespace(bones=["Hand", "Weapon"], parents=[-1, 0])
        anim = object()
        out, record, weights = F.clear_dropped_part(mesh, anim, "Weapon", [], [])
        self.assertIs(out, anim)
        self.assertFalse(record.changed)
        self.assertIsNone(weights)


if __name__ == "__main__":
    unittest.main()
