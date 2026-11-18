"""The Tripo route's pose rules on a synthetic biped: the loop seam, the feet on the ground, the boots at the end of a death, the grounding of the
exported clips and the readable captions of the game-size sheet. No Blender."""

from __future__ import annotations

import math
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))
sys.path.insert(0, str(PIPELINE / "tests"))
sys.path.insert(0, str(PIPELINE / "tripo"))

import run_pilot
import test_deformation_checks as TD
from lib import pdx_deform, tripo_pose as P, tripo_trim

BONES = [
    ("Hips", -1, (0.0, 0.55, 0.0)),
    ("LeftUpLeg", 0, (-0.1, 0.5, 0.0)), ("LeftLeg", 1, (-0.1, 0.28, 0.0)), ("LeftFoot", 2, (-0.1, 0.06, 0.0)), ("LeftToeBase", 3, (-0.1, 0.0, 0.1)),
    ("RightUpLeg", 0, (0.1, 0.5, 0.0)), ("RightLeg", 5, (0.1, 0.28, 0.0)), ("RightFoot", 6, (0.1, 0.06, 0.0)), ("RightToeBase", 7, (0.1, 0.0, 0.1)),
    ("Spine", 0, (0.0, 0.7, 0.0)), ("Head", 9, (0.0, 0.95, 0.0)),
]
IDENTITY = (0.0, 0.0, 0.0, 1.0)


def about_x(degrees: float):
    half = math.radians(degrees) / 2.0
    return (math.sin(half), 0.0, 0.0, math.cos(half))


def biped_mesh(path: Path) -> None:
    positions, triangles, owner = [], [], []
    for index, (_name, _parent, (x, y, z)) in enumerate(BONES):
        base = len(positions)
        points, tris = TD.tetrahedron((x, y, z), 0.05)
        positions += points
        triangles += [tuple(base + i for i in tri) for tri in tris]
        owner += [index] * 4
    TD.write_mesh(path, positions, triangles, owner)


def rest_translation(name: str):
    index = [b[0] for b in BONES].index(name)
    parent = BONES[index][1]
    base = BONES[parent][2] if parent >= 0 else (0.0, 0.0, 0.0)
    return tuple(BONES[index][2][i] - base[i] for i in range(3))


class Unit(unittest.TestCase):
    """Writes the biped and its clips into a temporary folder; `clip(role, frames, pose)` makes `<unit>_<role>.anim`."""

    def setUp(self) -> None:
        self.saved = list(TD.BONES)
        TD.BONES[:] = BONES
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.addCleanup(lambda: TD.BONES.__setitem__(slice(None), self.saved))
        self.folder = Path(temp.name)
        self.mesh_path = self.folder / "unit.mesh"
        biped_mesh(self.mesh_path)
        self.mesh = pdx_deform.load_mesh(self.mesh_path)

    def clip(self, role: str, frames: int, pose) -> Path:
        path = self.folder / f"unit_{role}.anim"
        TD.write_anim(path, frames, pose)
        return path

    def load(self, path: Path):
        return pdx_deform.load_anim(path)


class LoopSeam(Unit):
    def test_a_clip_that_ends_where_it_started_has_no_seam(self) -> None:
        anim = self.load(self.clip("attack", 20, lambda f: {"RightUpLeg": ((0.1 - 0.0, -0.05, 0.0), about_x(60 * math.sin(math.pi * f / 19)))}))
        self.assertLess(P.loop_seam(self.mesh, anim)[0], 1.0)

    def test_a_clip_that_ends_turned_away_has_the_seam_of_its_turn_and_names_the_joint(self) -> None:
        anim = self.load(self.clip("attack", 20, lambda f: {"RightUpLeg": (rest_translation("RightUpLeg"), about_x(100.0 * f / 19))}))
        turn, joint = P.loop_seam(self.mesh, anim)
        self.assertAlmostEqual(turn, 100.0, delta=0.5)
        self.assertEqual(joint, "RightUpLeg")

    def test_the_limit_comes_from_vanilla_and_the_roles_are_the_looping_ones(self) -> None:
        self.assertGreater(P.LOOP_POSE_LIMIT_DEGREES, P.VANILLA_LOOP_WORST_DEGREES)
        self.assertLessEqual(P.LOOP_POSE_LIMIT_DEGREES, 1.5 * P.VANILLA_LOOP_WORST_DEGREES)
        self.assertEqual(set(P.LOOP_ROLES), {"idle", "move", "attack", "defend", "retreat"})

    def test_the_check_fails_a_looping_role_but_not_a_death(self) -> None:
        turn = lambda f: {"RightUpLeg": (rest_translation("RightUpLeg"), about_x(100.0 * f / 19))}
        anims = {"unit_attack": self.load(self.clip("attack", 20, turn)), "unit_death": self.load(self.clip("death", 20, turn))}
        found, numbers = P.pose_findings(self.mesh, anims)
        self.assertEqual([(item["rule"], item["subject"]) for item in found if item["rule"] == "TRIPO-LOOP-POP"], [("TRIPO-LOOP-POP", "unit_attack")])
        self.assertNotIn("loop_seam_degrees", numbers["unit_death"])


class Feet(Unit):
    def test_the_lowest_foot_vertex_is_read_per_frame_toes_included(self) -> None:
        down = lambda f: {"Hips": ((0.0, 0.55 - 0.004 * f, 0.0), IDENTITY)}  # the whole body sinks 0.4% of its height a frame
        heights = P.foot_heights(self.mesh, self.load(self.clip("move", 5, down)))
        self.assertAlmostEqual(float(heights[0]), 0.0, places=3)
        self.assertAlmostEqual(float(heights[4]), -0.016, places=3)

    def test_a_foot_under_the_ground_fails_at_a_tenth_of_a_percent_and_a_grounded_clip_passes(self) -> None:
        sunk = self.load(self.clip("move", 5, lambda f: {"Hips": ((0.0, 0.55 - 0.0015 * f, 0.0), IDENTITY)}))
        found, _ = P.pose_findings(self.mesh, {"unit_move": sunk})
        self.assertEqual([item["rule"] for item in found], ["TRIPO-FOOT-BELOW-GROUND"])
        steady = self.load(self.clip("idle", 5, lambda f: {"Hips": ((0.0, 0.55, 0.0), IDENTITY)}))
        self.assertEqual(P.pose_findings(self.mesh, {"unit_idle": steady})[0], [])

    def test_the_ground_tolerance_is_under_the_check_limit(self) -> None:
        self.assertLess(P.GROUND_TOLERANCE, P.FOOT_SINK_LIMIT)

    def test_grounding_the_exported_clip_leaves_no_foot_under_the_limit_in_any_frame(self) -> None:
        anim_path = self.clip("move", 12, lambda f: {"Hips": ((0.0, 0.55 - 0.003 * (f % 4), 0.0), IDENTITY)})
        before = P.foot_heights(self.mesh, self.load(anim_path))
        self.assertLess(float(before.min()), -P.FOOT_SINK_LIMIT)
        record = run_pilot.ground_exported_clip(self.mesh_path, anim_path, "move", {})
        self.assertTrue(record["ground"]["shifted"])
        after = P.foot_heights(self.mesh, self.load(anim_path))
        self.assertGreaterEqual(float(after.min()), -P.FOOT_SINK_LIMIT)
        self.assertEqual(P.pose_findings(self.mesh, {"unit_move": self.load(anim_path)})[0], [])


def lying_death(knee_degrees: float, thigh_degrees: float = 0.0, sink: float = 0.0):
    """Stand 20 frames, fall onto the front over 20 more, bend both knees (or lift both thighs) over 10 and lie so to frame 70.
    `sink` lowers the lying body by that share of the height, so part of it ends under the ground."""

    def pose(frame: int):
        fall = min(max((frame - 20) / 20.0, 0.0), 1.0)
        bend = min(max((frame - 45) / 10.0, 0.0), 1.0)
        moved = {"Hips": ((0.0, 0.55 - (0.45 + sink) * fall, 0.0), about_x(90.0 * fall))}
        for side in ("Left", "Right"):
            moved[f"{side}Leg"] = (rest_translation(f"{side}Leg"), about_x(knee_degrees * bend))
            if thigh_degrees:
                moved[f"{side}UpLeg"] = (rest_translation(f"{side}UpLeg"), about_x(thigh_degrees * bend))
        return moved

    return pose


class DeathFeet(Unit):
    def hanging(self) -> Path:
        # A knee bent +90 degrees about x lifts the lower leg of the lying body away from the ground (the other sense pushes it into it).
        return self.clip("death", 70, lying_death(90.0))

    def test_boots_hanging_above_the_ground_at_the_end_fail_the_check(self) -> None:
        path = self.hanging()
        found, numbers = P.pose_findings(self.mesh, {"unit_death": self.load(path)})
        self.assertIn("TRIPO-DEATH-FEET", [item["rule"] for item in found], numbers)

    def test_the_vanilla_limit_is_a_percent_and_the_target_is_under_it(self) -> None:
        self.assertEqual(P.DEATH_FEET_LIMIT, 0.01)
        self.assertLess(P.DEATH_FEET_TARGET, P.DEATH_FEET_LIMIT)

    def test_the_knees_are_straightened_toward_the_rest_pose_and_the_boots_come_down(self) -> None:
        path = self.hanging()
        out = self.folder / "settled.anim"
        result = P.settle_death_legs(self.mesh_path, path, out)
        self.assertTrue(result.changed, result)
        self.assertLess(result.height_after, result.height_before)
        after = self.load(out)
        self.assertAlmostEqual(P.lifted_death_feet_height(self.mesh, after), result.height_after, places=4)
        self.assertLessEqual(P.death_feet_height(self.mesh, after), P.DEATH_FEET_LIMIT)

    def test_only_the_knees_change_and_no_joint_turns_faster_than_before_or_than_the_settle_rate(self) -> None:
        path = self.hanging()
        out = self.folder / "settled.anim"
        P.settle_death_legs(self.mesh_path, path, out)
        before, after = self.load(path), self.load(out)
        for joint in before.channels:
            same = np.allclose(before.channels[joint]["q"], after.channels[joint]["q"], atol=1e-5)
            if joint in ("LeftLeg", "RightLeg"):
                self.assertFalse(same, joint)
            else:
                self.assertTrue(same, joint)
            self.assertTrue(np.allclose(before.channels[joint]["t"], after.channels[joint]["t"], atol=1e-6))
        steps = [P.quaternion_turn(after.channels["LeftLeg"]["q"][i], after.channels["LeftLeg"]["q"][i + 1]) for i in range(after.frames - 1)]
        original = [P.quaternion_turn(before.channels["LeftLeg"]["q"][i], before.channels["LeftLeg"]["q"][i + 1]) for i in range(before.frames - 1)]
        self.assertLessEqual(max(steps), max(max(original), tripo_trim.SETTLE_MAX_RATE) + 1e-3)

    def test_thighs_lifted_at_the_hip_are_turned_back_and_the_straight_knees_are_left_alone(self) -> None:
        # The zombie's death: straight knees, both thighs lifted, so straightening the knees cannot lower the boots.
        path = self.clip("death", 70, lying_death(0.0, 30.0))
        self.assertGreater(P.death_feet_height(self.mesh, self.load(path)), P.DEATH_FEET_LIMIT)
        out = self.folder / "settled.anim"
        result = P.settle_death_legs(self.mesh_path, path, out)
        self.assertTrue(result.changed, result)
        self.assertEqual(set(result.joints), {"LeftUpLeg", "RightUpLeg"})
        self.assertLessEqual(P.death_feet_height(self.mesh, self.load(out)), P.DEATH_FEET_LIMIT)
        before, after = self.load(path), self.load(out)
        for joint in before.channels:
            if joint not in ("LeftUpLeg", "RightUpLeg"):
                self.assertTrue(np.allclose(before.channels[joint]["q"], after.channels[joint]["q"], atol=1e-5), joint)

    def test_the_knees_are_tried_before_the_thighs(self) -> None:
        self.assertEqual(P.LEG_SETTLE_GROUPS[0], ("knees",))
        result = P.settle_death_legs(self.mesh_path, self.hanging(), self.folder / "settled.anim")
        self.assertEqual(set(result.joints), {"LeftLeg", "RightLeg"})

    def test_a_death_with_its_boots_on_the_ground_is_left_alone(self) -> None:
        path = self.clip("death", 70, lying_death(0.0))
        out = self.folder / "settled.anim"
        result = P.settle_death_legs(self.mesh_path, path, out)
        self.assertFalse(result.changed)
        self.assertEqual(path.read_bytes(), out.read_bytes())

    def test_the_lifted_boot_height_adds_how_far_the_body_sinks_under_the_ground(self) -> None:
        # The ogre (2026-11-16): settling the thighs put the boots on the ground but pushed the legs under it, the ground pass then lifted the
        # body 2.5% and the boots ended 1.5% up. The settle now judges the boots as the lift will leave them.
        level = self.load(self.clip("death", 70, lying_death(0.0)))
        sunk = self.load(self.clip("death", 70, lying_death(0.0, sink=0.06)))
        self.assertLess(P.death_feet_height(self.mesh, sunk), P.death_feet_height(self.mesh, level) - 0.05)
        self.assertAlmostEqual(P.lifted_death_feet_height(self.mesh, sunk), P.lifted_death_feet_height(self.mesh, level), places=3)
        self.assertGreaterEqual(P.lifted_death_feet_height(self.mesh, level), P.death_feet_height(self.mesh, level))

    def test_the_legs_are_settled_on_the_grounded_body_so_a_lift_does_not_raise_the_boots_again(self) -> None:
        # The ogre (2026-11-16): its face went under the ground in the death, so the ground pass lifted the body 5.3% after the legs were
        # settled against the rest ground, and the boots ended 4.5% up. Grounding first, then settling, then grounding again keeps them down.
        path = self.clip("death", 70, lying_death(90.0, sink=0.06))
        record = run_pilot.ground_exported_clip(self.mesh_path, path, "death", {})
        self.assertTrue(record["legs"]["changed"], record)
        self.assertLessEqual(P.death_feet_height(self.mesh, self.load(path)), P.DEATH_FEET_LIMIT, record)

    def test_the_run_pilot_grounding_straightens_the_legs_of_a_death_only(self) -> None:
        path = self.hanging()
        record = run_pilot.ground_exported_clip(self.mesh_path, path, "death", {})
        self.assertTrue(record["legs"]["changed"])
        self.assertLessEqual(P.death_feet_height(self.mesh, self.load(path)), P.DEATH_FEET_LIMIT)
        other = self.clip("attack", 10, lambda f: {"Hips": ((0.0, 0.55, 0.0), IDENTITY)})
        self.assertNotIn("legs", run_pilot.ground_exported_clip(self.mesh_path, other, "attack", {}))


class TurnedToward(unittest.TestCase):
    """A turn toward a target keeps its way from frame to frame (`turned_toward`). The zombie's knee passed half a turn from rest during the
    legs' settle (zombie_n, 2026-11-18) and the short-way slerp turned it 120 degrees in one frame."""

    @staticmethod
    def steps(track) -> list:
        return [P.quaternion_turn(track[i], track[i + 1]) for i in range(len(track) - 1)]

    def crossing(self):
        # a knee turning 8 degrees a frame from 100 to 260 degrees off rest: it passes the far side of rest at frame 10
        track = np.array([about_x(100.0 + 8.0 * f) for f in range(21)])
        amounts = 0.4 * tripo_trim.settle_weights(21)
        return track, amounts

    def test_a_track_that_passes_half_a_turn_from_the_target_turns_no_faster_than_the_clip_and_the_ramp(self) -> None:
        track, amounts = self.crossing()
        short = np.array([P.slerp(q, np.array(IDENTITY), a) for q, a in zip(track, amounts)])
        self.assertGreater(max(self.steps(short)), 60.0)  # the old rule's jump
        turned = P.turned_toward(track, np.array(IDENTITY), amounts)
        self.assertLess(max(self.steps(turned)), 8.0 + 0.4 * 360.0 / 21 * 2)

    def test_the_frame_with_the_largest_amount_and_the_frames_on_its_side_turn_the_short_way(self) -> None:
        track, amounts = self.crossing()
        turned = P.turned_toward(track, np.array(IDENTITY), amounts)
        for f in range(11, 21):
            self.assertLess(P.quaternion_turn(turned[f], P.slerp(track[f], np.array(IDENTITY), amounts[f])), 1e-4, f)

    def test_a_track_with_no_crossing_turns_exactly_as_a_slerp(self) -> None:
        track = np.array([about_x(10.0 + 5.0 * f) for f in range(20)])
        track[7] = -track[7]  # a key on the other hemisphere keeps its sign
        amounts = np.linspace(0.0, 0.5, 20)
        turned = P.turned_toward(track, np.array(about_x(-30.0)), amounts)
        for f in range(20):
            expected = P.slerp(track[f], np.array(about_x(-30.0)), amounts[f])
            self.assertLess(P.quaternion_turn(turned[f], expected), 1e-4, f)
            self.assertGreaterEqual(float(turned[f] @ track[f]), 0.0)

    def test_frames_with_no_amount_are_left_as_they_are(self) -> None:
        track, amounts = self.crossing()
        amounts[:5] = 0.0
        turned = P.turned_toward(track, np.array(IDENTITY), amounts)
        self.assertTrue(np.allclose(turned[:5], track[:5]))


class GameSizeSheet(unittest.TestCase):
    """The captions under the tiles of `game_size.png` were drawn over each other because the tiles are only about 70 px wide."""

    def test_every_caption_is_readable_and_stays_in_its_own_cell(self) -> None:
        from PIL import Image

        import weapon_sheets

        with tempfile.TemporaryDirectory() as folder:
            tiles = Path(folder)
            size = 69
            clips, count = [], 0
            for name in ("orc_int3_idle", "orc_int3_move"):
                rows = []
                for frame in (1, 24, 48, 100):
                    entry = {"frame": frame, "tiles": {}}
                    for view in ("hoi4", "front"):
                        file = f"{name}_{frame}_{view}.png"
                        Image.new("RGB", (size, size), (200, 0, 200)).save(tiles / file)
                        entry["tiles"][view] = file
                        count += 1
                    rows.append(entry)
                clips.append({"name": name, "rows": rows})
            title = lambda n, f, v: f"f{f}{weapon_sheets.CAPTION_BREAK}{v}"
            image = weapon_sheets.sheet({"clips": clips}, tiles, ["hoi4", "front"], [c["name"] for c in clips], title)
        pixels = np.asarray(image.convert("RGB")).astype(int)
        white = (pixels > 235).all(axis=2)
        per_row = 8
        cell = image.width // per_row
        self.assertGreaterEqual(image.width, per_row * (size + 6))
        row_height = image.height // 2
        for row in range(2):
            band = white[row * row_height + weapon_sheets.LABEL + size: (row + 1) * row_height]
            spans = []
            for c in range(per_row):
                columns = np.nonzero(band[:, c * cell:(c + 1) * cell].any(axis=0))[0]
                self.assertGreater(len(columns), 3, f"row {row} cell {c} has no readable caption")
                spans.append((c * cell + columns.min(), c * cell + columns.max()))
            for (_a0, a1), (b0, _b1) in zip(spans, spans[1:]):
                self.assertLess(a1, b0 - 1, f"captions run together in row {row}: {spans}")
            self.assertGreater(band.shape[0], 14, "the second caption line is cut off")


class WaistTwist(unittest.TestCase):
    def test_the_twist_is_the_shoulder_lines_turn_against_the_hip_lines_about_the_up_axis(self) -> None:
        angle = math.radians(30.0)
        shoulders_left = np.array([[-1.0, 1.0, 0.0], [-math.cos(angle), 1.0, -math.sin(angle)]])
        shoulders_right = -shoulders_left * np.array([1.0, -1.0, 1.0])
        hips_left, hips_right = np.array([[-1.0, 0.0, 0.0]] * 2), np.array([[1.0, 0.0, 0.0]] * 2)
        twist = P.line_twist(shoulders_left, shoulders_right, hips_left, hips_right, 1)
        self.assertAlmostEqual(float(twist[0]), 0.0)
        self.assertAlmostEqual(abs(float(twist[1])), 30.0, places=4)

    def test_the_hip_line_runs_between_the_legs_top_joints_even_when_the_finder_took_the_knees(self) -> None:
        # 0 Hips, 1 LeftUpLeg, 2 LeftLeg, 3 RightUpLeg, 4 RightLeg
        parents = [-1, 0, 1, 0, 3]
        self.assertEqual(P.leg_roots(parents, 2, 4), (1, 3))
        self.assertEqual(P.leg_roots(parents, 1, 3), (1, 3))

    def test_only_the_part_past_the_target_is_turned_back(self) -> None:
        np.testing.assert_allclose(P.twist_excess(np.array([10.0, -40.0, 30.0]), 25.0), [0.0, -15.0, 5.0])

    def test_each_role_has_a_limit_a_quarter_over_vanillas_worst(self) -> None:
        self.assertEqual(set(P.WAIST_TWIST_LIMITS), {"idle", "move", "attack", "defend", "retreat", "death"})
        self.assertAlmostEqual(P.WAIST_TWIST_LIMITS["retreat"], 24.5)


if __name__ == "__main__":
    unittest.main()
