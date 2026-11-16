"""The quadruped clips' rules and the checks a war elephant's round 9 failed by review: the death's side, neck and legs, the loaded neck,
the rear and the defend, the map-camera reading and the load seam, without Blender."""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

import numpy as np

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE / "adapter"))
sys.path.insert(0, str(PIPELINE))

import quadruped_layout as ql
from lib import map_read, quadruped_checks
from lib import pdx_deform as P


def _landmarks(heavy: bool, load: bool = False) -> dict:
    rng = np.random.default_rng(3)
    parts = [rng.normal((x, y, z), 0.03, (300, 3)) for x in (-0.25, 0.25) for y in (0.0, 1.6) for z in np.linspace(0.05, 0.95, 4)]
    parts.append(np.column_stack([rng.uniform(-0.35, 0.35, 3000), rng.uniform(-0.2, 1.8, 3000), rng.uniform(1.0, 1.6, 3000)]))
    parts.append(rng.normal((0.0, -0.5, 1.8), 0.05, (300, 3)))
    landmarks = ql.detect_landmarks(np.vstack(parts))
    if heavy:
        landmarks["legs"] = {key: {**joints, "radius": np.asarray(0.25 * float(landmarks["belly_z"]))} for key, joints in landmarks["legs"].items()}
    if load:
        landmarks["load"] = {"roll_limit": 70.0, "roll_limit_other_side": -64.0, "bone": ql.LOAD_BONE}
    return landmarks


def _degrees(pose: dict, name: str, axis=ql.X_AXIS) -> float:
    return sum(degrees for row_axis, degrees in pose.get(name, []) if tuple(row_axis) == tuple(axis))


class ChooseCollapse(unittest.TestCase):
    def test_the_body_falls_onto_the_side_where_its_torso_reaches_out(self) -> None:
        # A wide left ear holds the body up when it falls to the left (positive roll); on its right side the torso lies lowest.
        calls = []

        def evaluate(roll, lift):
            calls.append((roll, lift))
            return (0.06, "Head") if roll > 0 else (0.0, "Spine")

        chosen = ql.choose_collapse(evaluate, (82.0, -82.0))
        self.assertEqual((chosen["roll"], chosen["neck_lift"]), (-82.0, 0.0))

    def test_the_neck_never_turns_when_the_load_holds_the_body_up(self) -> None:
        lifts = []

        def evaluate(roll, lift):
            lifts.append(lift)
            return 0.013 + 0.0001 * abs(lift) * -1, "Load"  # a neck turn would gain a hair, the load still holds the body up

        chosen = ql.choose_collapse(evaluate, (82.0,))
        self.assertEqual(chosen["neck_lift"], 0.0)
        self.assertEqual(set(lifts), {0.0}, "no neck lift is even tried while the head is not what holds the body up")
        self.assertIn("note", chosen)

    def test_the_smallest_neck_lift_that_lays_a_dropped_head_down(self) -> None:
        def evaluate(roll, lift):
            return (0.0, "Spine") if abs(lift) >= 20 else (0.05, "Head")

        chosen = ql.choose_collapse(evaluate, (82.0,))
        self.assertEqual((chosen["roll"], abs(chosen["neck_lift"])), (82.0, 20.0))
        self.assertLessEqual(max(abs(lift) for lift in ql.NECK_LIFTS), 30.0)

    def test_both_sides_are_capped_by_the_load(self) -> None:
        self.assertEqual(ql.roll_limits(_landmarks(True, load=True)), (70.0, -64.0))
        self.assertEqual(ql.roll_limits(_landmarks(True)), (ql.COLLAPSE_ROLL, -ql.COLLAPSE_ROLL))


class DeathLegs(unittest.TestCase):
    def test_pillar_legs_give_way_in_a_death_and_the_top_legs_sag(self) -> None:
        heavy = ql.build_layout(_landmarks(True))
        light = ql.build_layout(_landmarks(False))
        last = ql.frame_count("quadruped_collapse") - 1
        for frame in (10, last):
            a, b = ql.pose_at("quadruped_collapse", frame, light), ql.pose_at("quadruped_collapse", frame, heavy)
            self.assertAlmostEqual(_degrees(a, "Front_Left_Lower"), _degrees(b, "Front_Left_Lower"), places=6)
            self.assertAlmostEqual(_degrees(a, "Front_Left_Cannon"), _degrees(b, "Front_Left_Cannon"), places=6)
        trot = ql.pose_at("quadruped_walk", 5, heavy)
        self.assertLess(abs(_degrees(trot, "Front_Left_Cannon")), abs(_degrees(ql.pose_at("quadruped_walk", 5, light), "Front_Left_Cannon")) + 1e-9)
        layout = ql.build_layout({**_landmarks(True), "death": {"roll": 60.0, "neck_lift": 0.0}})
        final = ql.pose_at("quadruped_collapse", last, layout)
        self.assertAlmostEqual(_degrees(final, "Front_Right_Upper", ql.Y_AXIS), -ql.COLLAPSE_SAG, places=6)
        self.assertEqual(_degrees(final, "Front_Left_Upper", ql.Y_AXIS), 0.0, "the legs underneath stay")


class LoadedPoses(unittest.TestCase):
    def test_a_loaded_neck_and_head_turn_less(self) -> None:
        free = ql.build_layout(_landmarks(True))
        loaded = ql.build_layout(_landmarks(True, load=True))
        for style, frame in (("quadruped_brace", 20), ("quadruped_rear", 20)):
            a, b = ql.pose_at(style, frame, free), ql.pose_at(style, frame, loaded)
            self.assertAlmostEqual(_degrees(b, "Neck_01"), _degrees(a, "Neck_01") * ql.LOADED_NECK, places=6)
            neck = ql.leg_stance(free.landmarks)["neck"]
            self.assertAlmostEqual(_degrees(b, "Head"), _degrees(a, "Head") * neck * ql.LOADED_NECK, places=6)

    def test_a_heavy_rear_raises_the_head_and_folds_the_lifted_forelegs(self) -> None:
        heavy, light = ql.build_layout(_landmarks(True)), ql.build_layout(_landmarks(False))
        pose = ql.pose_at("quadruped_rear", 20, heavy)
        self.assertLess(_degrees(pose, "Head"), 0.0, "the head rises with the forequarters")
        self.assertLess(_degrees(pose, "__root_pitch__"), 0.0, "the body pitches up")
        runner = ql.pose_at("quadruped_rear", 20, light)
        self.assertAlmostEqual(_degrees(pose, "Front_Left_Cannon"), _degrees(runner, "Front_Left_Cannon") * ql.HEAVY_PITCH, places=6)

    def test_a_heavy_retreat_flees_with_its_head_up(self) -> None:
        heavy, light = ql.build_layout(_landmarks(True)), ql.build_layout(_landmarks(False))
        self.assertEqual(ql.stance_style("quadruped_gallop", heavy.landmarks), "quadruped_trot")
        for frame in range(0, ql.frame_count("quadruped_trot"), 5):
            self.assertLess(_degrees(ql.pose_at("quadruped_trot", frame, heavy), "Neck_01"), _degrees(ql.pose_at("quadruped_trot", frame, light), "Neck_01"))

    def test_the_defend_sweeps_both_ways_steps_and_ends_where_it_began(self) -> None:
        layout = ql.build_layout(_landmarks(True))
        total = ql.frame_count("quadruped_brace")
        yaws = [_degrees(ql.pose_at("quadruped_brace", frame, layout), "__root_yaw__", ql.Z_AXIS) for frame in range(total)]
        self.assertAlmostEqual(max(yaws), ql.BRACE_SWEEP, delta=0.5)
        self.assertAlmostEqual(min(yaws), -ql.BRACE_SWEEP, delta=0.5)
        self.assertEqual(ql.pose_at("quadruped_brace", 0, layout), ql.pose_at("quadruped_brace", total - 1, layout))
        swinging = max(range(total), key=lambda frame: abs(yaws[min(frame + 1, total - 1)] - yaws[frame]))
        self.assertGreater(_degrees(ql.pose_at("quadruped_brace", swinging, layout), "Front_Left_Cannon"), 20.0, "the forefeet step across")


def _box(low, high):
    (x0, y0, z0), (x1, y1, z1) = low, high
    points = np.array([[x, y, z] for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)], float)
    faces = np.array([[0, 1, 3], [0, 3, 2], [4, 6, 7], [4, 7, 5], [0, 4, 5], [0, 5, 1], [2, 3, 7], [2, 7, 6], [0, 2, 6], [0, 6, 4], [1, 5, 7], [1, 7, 3]])
    return points, faces


def towered_animal() -> P.SkinnedMesh:
    """A long body (file frame: Y up, facing -Z) with a tall tower, all on `Root`, and a `Head` joint in front."""

    parts = [_box((-1.0, 1.0, -3.0), (1.0, 2.0, 3.0)), _box((-0.8, 2.0, -1.0), (0.8, 4.0, 1.0)), _box((-0.2, 0.0, -2.5), (0.2, 1.0, 2.5))]
    points, faces, offset = [], [], 0
    for p, f in parts:
        points.append(p)
        faces.append(f + offset)
        offset += len(p)
    positions = np.concatenate(points)
    joints = np.full((len(positions), 4), -1)
    joints[:, 0] = 0
    weights = np.zeros((len(positions), 4))
    weights[:, 0] = 1.0
    inverse = np.stack([np.eye(4), np.eye(4)])
    inverse[1, :3, 3] = -np.array([0.0, 1.5, -3.0])
    return P.SkinnedMesh(positions=positions, triangles=np.concatenate(faces), joints=joints, weights=weights, bones=["Root", "Head"], parents=[-1, 0], inverse_bind=inverse)


def turning(frames: int, yaw: float = 0.0, slide: float = 0.0) -> P.Animation:
    """The root yaws up to `yaw` degrees and back, or slides `slide` units sideways and back."""

    share = np.sin(np.linspace(0.0, math.pi, frames))
    angle = np.radians(yaw) * share / 2
    q = np.stack([np.zeros(frames), np.sin(angle), np.zeros(frames), np.cos(angle)], axis=1)
    t = np.stack([slide * share, np.zeros(frames), np.zeros(frames)], axis=1)
    still = {"t": np.tile([0.0, 1.5, -3.0], (frames, 1)), "q": np.tile([0.0, 0.0, 0.0, 1.0], (frames, 1)), "s": np.ones(frames)}
    return P.Animation(fps=30.0, frames=frames, channels={"Root": {"t": t, "q": q, "s": np.ones(frames)}, "Head": still})


class MapReading(unittest.TestCase):
    def test_only_a_change_of_shape_reads_on_the_map(self) -> None:
        mesh = towered_animal()
        idle = turning(12)
        self.assertLess(map_read.clip_reading(mesh, turning(12, slide=0.3), idle), 0.02, "sliding the same shape does not count")
        self.assertGreater(map_read.clip_reading(mesh, turning(12, yaw=30.0), idle), map_read.MIN_READ, "a turn changes the silhouette")
        self.assertLess(map_read.clip_reading(mesh, turning(12, yaw=2.0), idle), map_read.MIN_READ)

    def test_the_check_fails_an_attack_that_reads_as_the_idle(self) -> None:
        mesh = towered_animal()
        anims = {"unit_idle": turning(12), "unit_attack": turning(12, yaw=2.0), "unit_defend": turning(12, yaw=30.0)}
        numbers: dict = {}
        found = quadruped_checks._map_findings(mesh, anims, numbers)
        self.assertEqual([item["subject"] for item in found], ["unit_attack"])
        self.assertGreater(numbers["unit_defend"]["map_read"], map_read.MIN_READ)


class LoadSeam(unittest.TestCase):
    def test_the_seam_share_counts_only_the_skin_the_load_blends_into(self) -> None:
        positions = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [2.0, 0.0, 0.0], [0.0, 10.0, 0.0], [1.0, 10.0, 0.0]])
        edges = np.array([[0, 1], [1, 2], [3, 4]])
        mesh = P.SkinnedMesh(positions=positions, triangles=np.array([[0, 1, 2], [2, 3, 4]]), joints=np.zeros((5, 4), int), weights=np.ones((5, 4)) / 4,
                             bones=["Root"], parents=[-1], inverse_bind=np.eye(4)[None])
        seam = np.array([False, True, False, False, False])
        torn = positions.copy()
        torn[2, 0] = 4.0  # the edge 1-2 stretches three times; the far edge 3-4 is not seam
        torn[4, 0] = 5.0
        share, frame = quadruped_checks.seam_share(mesh, np.stack([positions, torn]), edges, seam)
        self.assertEqual((share, frame), (0.5, 1))
        self.assertGreater(0.03, quadruped_checks.LOAD_SEAM_LIMIT)


if __name__ == "__main__":
    unittest.main()
