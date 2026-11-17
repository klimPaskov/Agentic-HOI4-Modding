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
    def test_pillar_legs_give_way_in_a_death_and_relax_once_lying(self) -> None:
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
        fallen, final = ql.pose_at("quadruped_collapse", 30, layout), ql.pose_at("quadruped_collapse", last, layout)
        for name in ("Front_Right_Upper", "Front_Left_Lower", "Rear_Left_Upper"):
            self.assertAlmostEqual(_degrees(final, name), _degrees(fallen, name) * (1 - ql.COLLAPSE_RELAX), places=6, msg=name)
            self.assertEqual(_degrees(final, name, ql.Y_AXIS), 0.0, "no leg turns down at the shoulder or hip")
        self.assertAlmostEqual(_degrees(fallen, "Rear_Left_Lower"), _degrees(fallen, "Front_Left_Lower") * ql.COLLAPSE_HIND_FOLD, places=6)
        loaded = ql.build_layout({**_landmarks(True, load=True), "death": {"roll": 60.0, "neck_lift": 0.0}})
        for name in ("Neck_02", "Head"):
            self.assertFalse(any(abs(degrees) > 1e-9 for _axis, degrees in ql.pose_at("quadruped_collapse", last, loaded).get(name, [])), name)


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

    def test_a_heavy_retreat_turns_away_and_back_to_its_heading(self) -> None:
        heavy = ql.build_layout(_landmarks(True, load=True))
        self.assertEqual(ql.stance_style("quadruped_gallop", heavy.landmarks), "quadruped_flee")
        total = ql.frame_count("quadruped_flee")
        self.assertEqual(total, 2 * ql.frame_count("quadruped_trot"))
        yaws = [_degrees(ql.pose_at("quadruped_flee", frame, heavy), "__root_yaw__", ql.Z_AXIS) for frame in range(total + 1)]
        self.assertAlmostEqual(yaws[0], 0.0, places=6)
        self.assertAlmostEqual(yaws[-1], 0.0, places=6)
        self.assertAlmostEqual(yaws[total // 2], ql.RETREAT_TURN, places=6, msg="turned away in the middle")
        self.assertGreaterEqual(min(yaws), -1e-9, "it never swings to the other side")

    def test_a_heavy_walk_sways_once_a_stride_and_ends_at_its_heading(self) -> None:
        heavy, light = ql.build_layout(_landmarks(True)), ql.build_layout(_landmarks(False))
        total = ql.frame_count("quadruped_walk")
        yaws = [_degrees(ql.pose_at("quadruped_walk", frame, heavy), "__root_yaw__", ql.Z_AXIS) for frame in range(total + 1)]
        self.assertAlmostEqual(max(yaws), ql.WALK_SWAY, delta=0.2)
        self.assertAlmostEqual(min(yaws), -ql.WALK_SWAY, delta=0.2)
        self.assertAlmostEqual(yaws[0], 0.0, places=6)
        self.assertNotIn("__root_yaw__", ql.pose_at("quadruped_walk", total // 4, light), "a runner's walk does not sway")

    def test_a_heavy_retreat_loops_on_two_trot_strides(self) -> None:
        heavy = ql.build_layout(_landmarks(True, load=True))
        total = ql.frame_count("quadruped_flee")
        self.assertEqual(ql.pose_at("quadruped_flee", 0, heavy), ql.pose_at("quadruped_flee", total, heavy), "it loops")
        trot = ql.pose_at("quadruped_trot", 5, heavy)
        flee = ql.pose_at("quadruped_flee", 5, heavy)
        second = ql.pose_at("quadruped_flee", 5 + ql.frame_count("quadruped_trot"), heavy)
        self.assertAlmostEqual(_degrees(second, "Front_Left_Upper"), _degrees(trot, "Front_Left_Upper"), places=6, msg="two strides")
        self.assertAlmostEqual(_degrees(flee, "Front_Left_Upper"), _degrees(trot, "Front_Left_Upper"), places=6)
        self.assertLessEqual(_degrees(flee, "Neck_01"), abs(_degrees(trot, "Neck_01")) + 1e-9, "the head is not raised into a load")

    def test_the_defend_is_a_braced_guard_turned_one_way_with_planted_feet(self) -> None:
        layout = ql.build_layout(_landmarks(True, load=True))
        total = ql.frame_count("quadruped_brace")
        poses = [ql.pose_at("quadruped_brace", frame, layout) for frame in range(total)]
        yaws = [_degrees(pose, "__root_yaw__", ql.Z_AXIS) for pose in poses]
        self.assertAlmostEqual(yaws[0], 0.0, places=6)
        self.assertAlmostEqual(yaws[-1], 0.0, places=6)
        self.assertLessEqual(max(yaws), 1e-9, "it turns to one side only, away from the retreat's turn")
        self.assertGreater(-min(yaws), ql.GUARD_TURN)
        self.assertLess(-min(yaws), ql.GUARD_TURN + ql.GUARD_SWEEP + 1e-6)
        for pose in poses:
            for side in ("Left", "Right"):
                self.assertFalse(pose.get(f"Front_{side}_Cannon"), "no forefoot steps")
        held = poses[total // 2]
        self.assertGreater(_degrees(held, "Neck_01"), 0.0, "the head is lowered")
        self.assertLess(_degrees(held, "Front_Left_Upper"), 0.0, "the forefeet are set forward")
        self.assertNotEqual(_degrees(held, "Front_Left_Upper", ql.Y_AXIS), 0.0, "and spread")
        self.assertEqual(_degrees(held, "Front_Left_Upper", ql.Y_AXIS), -_degrees(held, "Front_Right_Upper", ql.Y_AXIS))

    def test_a_pillar_hip_and_shoulder_turn_no_farther_than_a_walk(self) -> None:
        heavy, light = ql.build_layout(_landmarks(True)), ql.build_layout(_landmarks(False))
        for style in ("quadruped_walk", "quadruped_trot", "quadruped_flee", "quadruped_brace"):
            for frame in range(ql.frame_count(style)):
                pose = ql.pose_at(style, frame, heavy)
                for end, side in ql.LEGS:
                    self.assertLessEqual(abs(_degrees(pose, ql.leg_name(end, side, "Upper"))), ql.PILLAR_SWING + 1e-6, (style, frame, end, side))
        swings = [abs(_degrees(ql.pose_at("quadruped_trot", frame, light), "Rear_Left_Upper")) for frame in range(ql.frame_count("quadruped_trot"))]
        self.assertGreater(max(swings), ql.PILLAR_SWING, "a runner's trot keeps its own swing")


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
        self.assertGreater(numbers["unit_defend"]["map_read"]["idle"], map_read.MIN_READ)

    def test_the_check_fails_a_retreat_that_reads_as_the_move_or_the_defend(self) -> None:
        mesh = towered_animal()
        for retreat, failing in ((turning(12, yaw=2.0), ["move", "defend"]), (turning(12, yaw=30.0), []), (turning(12, yaw=-30.0), ["defend"])):
            numbers: dict = {}
            anims = {"unit_idle": turning(12), "unit_move": turning(12), "unit_defend": turning(12, yaw=-30.0), "unit_retreat": retreat}
            found = quadruped_checks._map_findings(mesh, anims, numbers)
            self.assertEqual([item["against"] for item in found if item["subject"] == "unit_retreat"], failing)
            self.assertEqual(sorted(numbers["unit_retreat"]["map_read"]), ["defend", "move"])


def seamed_mount():
    """A load row (weight 1 on `Load`, at the top) joined edge by edge to a row of head skin, and a long ring of skin half on the load and
    half on the tail, its neighbours joined in a chain; a floor vertex sets the height."""

    count, ring = 40, 200
    load = np.array([[float(i), 10.0, 0.0] for i in range(count)])
    head = np.array([[float(i), 4.0, 0.0] for i in range(count)])
    tail = np.array([[0.1 * i, 3.0, 5.0] for i in range(ring)])
    positions = np.concatenate([load, head, tail, [[0.0, 0.0, 0.0]]])
    joints = np.zeros((len(positions), 4), int)
    weights = np.zeros((len(positions), 4))
    joints[:count, 0], weights[:count, 0] = 1, 1.0
    joints[count:2 * count, 0], weights[count:2 * count, 0] = 2, 1.0
    joints[2 * count:-1, :2], weights[2 * count:-1, :2] = [1, 3], 0.5
    weights[-1, 0] = 1.0
    edges = np.concatenate([np.stack([np.arange(count), np.arange(count) + count], axis=1),
                            np.stack([np.arange(ring - 1), np.arange(1, ring)], axis=1) + 2 * count])
    mesh = P.SkinnedMesh(positions=positions, triangles=np.zeros((0, 3), int), joints=joints, weights=weights,
                         bones=["Root", "Load", "Head", "Tail_01"], parents=[-1, 0, 0, 0], inverse_bind=np.tile(np.eye(4), (4, 1, 1)))
    return mesh, edges, count


class LoopHeading(unittest.TestCase):
    def test_a_clip_turned_at_its_ends_fails_and_one_turned_in_the_middle_passes(self) -> None:
        mesh = towered_animal()
        rest = mesh.positions
        turn = lambda degrees: rest @ np.array([[np.cos(np.radians(degrees)), 0, -np.sin(np.radians(degrees))], [0, 1, 0], [np.sin(np.radians(degrees)), 0, np.cos(np.radians(degrees))]])
        self.assertAlmostEqual(abs(quadruped_checks.heading(rest, turn(25.0))), 25.0, places=4)
        row: dict = {}
        self.assertTrue(quadruped_checks._heading_findings(mesh, "unit_retreat", np.stack([turn(25.0), turn(25.0), turn(25.0)]), row))
        self.assertFalse(quadruped_checks._heading_findings(mesh, "unit_retreat", np.stack([rest, turn(30.0), turn(2.0)]), row))
        self.assertEqual(set(quadruped_checks.HEADING_ROLES), {"move", "attack", "defend", "retreat"})

    def test_the_check_fails_a_move_that_reads_as_the_idle(self) -> None:
        mesh = towered_animal()
        for move, failing in ((turning(12, yaw=2.0), True), (turning(12, yaw=30.0), False)):
            found = quadruped_checks._map_findings(mesh, {"unit_idle": turning(12), "unit_move": move}, {})
            self.assertEqual(bool(found), failing)


class LegRoot(unittest.TestCase):
    def test_the_root_is_the_skin_shared_by_the_torso_and_the_upper_leg(self) -> None:
        # a row of skin half on the Pelvis and half on the hind leg's Upper bone, joined in a chain, and a leg below it on the Upper alone
        count = 60
        root = np.array([[0.1 * i, 5.0, 0.0] for i in range(count)])
        leg = np.array([[0.1 * i, 2.0, 0.0] for i in range(count)])
        positions = np.concatenate([root, leg, [[0.0, 0.0, 0.0], [0.0, 10.0, 0.0]]])
        joints = np.zeros((len(positions), 4), int)
        weights = np.zeros((len(positions), 4))
        joints[:count, :2], weights[:count, :2] = [1, 2], 0.5
        joints[count:2 * count, 0], weights[count:2 * count, 0] = 2, 1.0
        weights[-2:, 0] = 1.0
        edges = np.concatenate([np.stack([np.arange(count - 1), np.arange(1, count)], axis=1),
                                np.stack([np.arange(count - 1), np.arange(1, count)], axis=1) + count])
        mesh = P.SkinnedMesh(positions=positions, triangles=np.zeros((0, 3), int), joints=joints, weights=weights,
                             bones=["Root", "Pelvis", "Rear_Left_Upper"], parents=[-1, 0, 1], inverse_bind=np.tile(np.eye(4), (3, 1, 1)))
        roots = quadruped_checks.leg_roots(mesh, edges)
        self.assertEqual(list(roots), ["Rear_Left"])
        self.assertEqual(len(roots["Rear_Left"]), count - 1, "the leg below the root is not judged")
        torn = positions.copy()
        torn[1:3, 0] += 1.0  # two edges of the root stretch about eleven times, one squashes
        share, frame, part = quadruped_checks.leg_root_share(mesh, np.stack([positions, torn]), roots)
        self.assertEqual((frame, part), (1, "Rear_Left"))
        self.assertAlmostEqual(share, 2 / (count - 1), places=6)
        self.assertGreater(share, quadruped_checks.LEG_ROOT_LIMIT)


class LoadSeam(unittest.TestCase):
    def test_a_crease_beside_one_part_fails_though_the_whole_seam_barely_moves(self) -> None:
        mesh, edges, count = seamed_mount()
        load = quadruped_checks.load_mask(mesh)
        self.assertEqual(int(load.sum()), count)
        picked, parts = quadruped_checks.seam_edges(mesh, edges, load, quadruped_checks.seam_mask(mesh))
        self.assertEqual(sorted(set(parts.tolist())), ["Head", "Tail_01"])
        creased = mesh.positions.copy()
        creased[count:count + 4, 1] = 9.6  # four head vertices pushed up against the load: those edges squash to a tenth
        share, frame, part = quadruped_checks.seam_share(mesh, np.stack([mesh.positions, creased]), picked, parts)
        self.assertEqual((round(share, 3), frame, part), (0.1, 1, "Head"))
        self.assertLess(4 / len(picked), quadruped_checks.LOAD_SEAM_LIMIT, "a share of the whole seam would pass it")
        self.assertGreater(share, quadruped_checks.LOAD_SEAM_LIMIT)


if __name__ == "__main__":
    unittest.main()
