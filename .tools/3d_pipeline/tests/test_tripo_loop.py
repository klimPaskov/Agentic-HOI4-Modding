"""The looped gait of a Tripo humanoid (lib/tripo_loop.py): the stride speed, TRIPO-LOOP-STANDS, the loop window and its close, the intake's
arguments and pose_check's gait verdict, on plain joint tracks, on the synthetic biped of test_tripo_pose_upper and on a small skinned GLB,
and the calibration on vanilla's locomotion clips when the game is installed. No Blender."""

from __future__ import annotations

import json
import math
import struct
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))
sys.path.insert(0, str(PIPELINE / "tests"))
sys.path.insert(0, str(PIPELINE / "tripo"))
sys.path.insert(0, str(PIPELINE.parents[1]))

import pose_check
import run_pilot
import tripo_checks as TC
import tripo_intake
from lib import pdx_deform, tripo_loop as L, tripo_trim
from test_tripo_pose_upper import UNITS, Biped, local, turn
from tests.test_tripo_route import tripo_spec

PERIOD = 20  # frames of one stride (both feet lead once)
EASE = 10  # frames a run takes to start and to stop
FEET, PELVIS = (1, 2), 0


def phases(stand_before: int, strides: float, stand_after: int, period: int = PERIOD) -> np.ndarray:
    """The stride's phase per frame (radians): a stand, then `strides` strides, then a stand in the pose the run ended in. Between two
    stands the run takes `EASE` frames to reach its speed and as many to lose it, as a body does (the strides counted are at full speed)."""

    full = int(round(strides * period))
    if not stand_before and not stand_after:
        speed = np.ones(full)
    else:
        ramp = (np.arange(1, EASE + 1) / (EASE + 1.0)) ** 2
        speed = np.concatenate([ramp, np.ones(full), ramp[::-1]])
    run = 2.0 * math.pi * np.cumsum(speed) / period
    return np.concatenate([np.zeros(stand_before + 1), run, np.full(stand_after, run[-1] if len(run) else 0.0)])


def joints_of(phase: np.ndarray, reach: float = 0.2, grow: float = 0.0) -> np.ndarray:
    """(F, 3, 3) joints of a body striding in place: the pelvis and two ankles that swing past each other, `reach` of the height each way.
    With `grow` the swing widens by that share a frame, so no two strides are the same."""

    frames = len(phase)
    reach = reach * (1.0 + grow * np.arange(frames))
    out = np.zeros((frames, 3, 3))
    out[:, 0, 1] = 0.5 + 0.01 * np.cos(2.0 * phase)
    out[:, 1] = np.stack([np.full(frames, -0.1), 0.05 + 0.03 * np.maximum(np.cos(phase), 0.0), reach * np.sin(phase)], axis=1)
    out[:, 2] = np.stack([np.full(frames, 0.1), 0.05 + 0.03 * np.maximum(-np.cos(phase), 0.0), -reach * np.sin(phase)], axis=1)
    return out


def numbers(phase: np.ndarray, **kwargs) -> dict:
    return L.gait_numbers(joints_of(phase, **kwargs), FEET, PELVIS, 1.0, 30.0)


class StrideSpeed(unittest.TestCase):
    def test_a_walk_strides_in_every_step_and_a_stand_in_none(self) -> None:
        walk = numbers(phases(0, 3, 0))
        self.assertEqual(walk["still_steps"], 0)
        self.assertGreater(walk["slowest"], L.VANILLA_MIN_STRIDE_SPEED)
        self.assertIsNone(L.stands_reason(walk, "move"))
        stand = numbers(np.zeros(40))
        self.assertEqual(stand["still_share"], 1.0)
        self.assertIn("stops and stands", L.stands_reason(stand, "move"))

    def test_the_turn_of_a_swing_is_not_a_stand(self) -> None:
        """Where the feet turn round one ankle is still against the other for an instant: the smoothing around the loop carries it."""

        joints = joints_of(phases(0, 3, 0, period=60), reach=0.15)
        raw = L.step_speed(joints[:, 1], joints[:, 2], 1.0, 30.0)
        self.assertLess(raw.min(), L.MIN_STRIDE_SPEED)
        self.assertGreater(L.stride_speed(joints[:, 1], joints[:, 2], 1.0, 30.0).min(), L.MIN_STRIDE_SPEED)

    def test_the_smoothing_runs_round_the_loop(self) -> None:
        values = np.array([10.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        self.assertAlmostEqual(float(L.smooth_cyclic(values, 3)[-1]), 10.0 / 3.0)
        self.assertAlmostEqual(float(L.smooth_cyclic(values, 3)[3]), 0.0)
        self.assertEqual(L.smooth_width(30.0), 5)
        self.assertEqual(L.smooth_width(24.0) % 2, 1)

    def test_a_run_between_two_stands_fails_with_the_share_and_the_first_frame(self) -> None:
        """`flee_01`: a cower, a run in the middle and a stand at the end."""

        row = numbers(phases(15, 2, 12))
        self.assertGreater(row["still_share"], 0.25)
        self.assertEqual(row["first_still_frame"], 0)
        reason = L.stands_reason(row, "retreat")
        self.assertIn("looped retreat stops and stands once per cycle", reason)

    def test_a_short_stop_inside_a_walk_fails_too(self) -> None:
        """The settle's eased frames at the end of a walk (the dwarf's and the orc's move): a third of a second without stride."""

        row = numbers(np.concatenate([phases(0, 2, 0), np.full(10, phases(0, 2, 0)[-1])]))
        self.assertGreater(row["still_steps"], 0)
        self.assertLess(row["still_share"], 0.2)
        self.assertIsNotNone(L.stands_reason(row, "move"))

    def test_a_seam_that_jerks_fails_and_a_seam_that_flows_passes(self) -> None:
        flowing = numbers(phases(0, 2, 0))
        self.assertLess(flowing["seam_share"], L.MAX_SEAM_SHARE)
        # cut a quarter of a stride early: the last step still swings forward, the first step starts from the middle of the other swing
        cut = numbers(phases(0, 2, 0)[: 2 * PERIOD - PERIOD // 4], reach=0.3)
        self.assertEqual(cut["still_steps"], 0)
        self.assertGreater(cut["seam_share"], L.MAX_SEAM_SHARE)
        self.assertAlmostEqual(cut["seam_share"], cut["seam_speed_change"] / cut["inner_speed_change"], delta=0.01)
        self.assertIn("jerks once per cycle", L.stands_reason(cut, "retreat"))

    def test_the_limits_are_vanillas_worst_less_or_plus_a_quarter(self) -> None:
        self.assertAlmostEqual(L.MIN_STRIDE_SPEED, L.VANILLA_MIN_STRIDE_SPEED / 1.25, delta=0.005)
        self.assertAlmostEqual(L.MAX_SEAM_SHARE, L.VANILLA_SEAM_SHARE * 1.25, delta=0.005)


class Window(unittest.TestCase):
    def window(self, phase: np.ndarray, **kwargs):
        return L.loop_window(joints_of(phase, **kwargs), FEET, PELVIS, 1.0, 24.0)

    def test_the_window_is_whole_strides_inside_the_run(self) -> None:
        found = self.window(phases(15, 2.6, 12), grow=0.004)
        self.assertIsNotNone(found)
        self.assertFalse(found["whole"])
        self.assertGreaterEqual(found["first"], 15 + EASE)
        self.assertLessEqual(found["last"], 15 + EASE + int(2.6 * PERIOD))
        self.assertEqual(found["frames"] % PERIOD, 0, found)
        self.assertEqual(found["from_frames"], 15 + 2 * EASE + int(2.6 * PERIOD) + 12)

    def test_the_cut_clip_passes_the_check_the_whole_clip_fails(self) -> None:
        joints = joints_of(phases(15, 2.6, 12), grow=0.004)
        self.assertIsNotNone(L.stands_reason(L.gait_numbers(joints, FEET, PELVIS, 1.0, 24.0), "retreat"))
        found = L.loop_window(joints, FEET, PELVIS, 1.0, 24.0)
        cut = L.gait_numbers(joints[found["first"] : found["last"] + 1], FEET, PELVIS, 1.0, 24.0)
        self.assertIsNone(L.stands_reason(cut, "retreat"), cut)

    def test_a_walk_that_already_loops_keeps_every_frame(self) -> None:
        found = self.window(phases(0, 2, 0))
        self.assertTrue(found["whole"])
        self.assertEqual((found["first"], found["last"]), (0, 2 * PERIOD))
        self.assertLess(found["cost"], 1e-6)

    def test_more_strides_win_when_they_close_as_well(self) -> None:
        """Three equal strides between two stands: every whole number of strides closes, and the window keeps all three."""

        found = self.window(phases(12, 3.5, 12))
        self.assertEqual(found["frames"], 3 * PERIOD)

    def test_one_stride_wins_when_the_run_changes_as_it_goes(self) -> None:
        found = self.window(phases(12, 3.5, 12), grow=0.02)
        self.assertEqual(found["frames"], PERIOD)

    def test_a_stand_or_half_a_stride_has_no_window(self) -> None:
        self.assertIsNone(self.window(np.zeros(40)))
        half = 2.0 * math.pi * np.concatenate([np.zeros(11), np.arange(1, 9), np.full(10, 8.0)]) / PERIOD  # 0.4 of a stride, then a stand
        self.assertIsNone(self.window(half), "each foot must lead once inside the window")
        self.assertIsNone(L.loop_window(joints_of(phases(0, 1, 0))[:3], FEET, PELVIS, 1.0, 24.0))

    def test_the_striding_phase_is_vanillas_slowest_and_over(self) -> None:
        speed = np.array([0.0, L.MIN_STRIDE_SPEED, L.VANILLA_MIN_STRIDE_SPEED, 2.0])
        self.assertEqual(list(L.striding_phase(speed)), [False, False, True, True])


class Close(unittest.TestCase):
    def test_the_weights_end_on_the_first_pose_and_start_and_end_with_no_speed(self) -> None:
        weights = L.close_weights(8)
        self.assertEqual(float(weights[-1]), 1.0)
        self.assertTrue(np.all(np.diff(weights) > 0))
        self.assertLess(weights[0], 0.06)
        self.assertLess(1.0 - weights[-2], 0.06)

    def test_a_gaits_stride_is_eased_only_past_the_kits_spin_limit(self) -> None:
        self.assertAlmostEqual(L.GAIT_SNAP_DEGREES, 0.75 * 37.0 * 30.0 / 24.0, delta=0.05)
        self.assertGreater(L.GAIT_SNAP_DEGREES, 31.9 * 30.0 / 24.0 * 0.75, "vanilla's charge knee would not be eased")
        self.assertLess(L.GAIT_SNAP_DEGREES * 24.0 / 30.0, L.SPIN_LIMIT_DEGREES)

    def test_the_close_takes_the_settles_count_but_never_over_half_the_window(self) -> None:
        self.assertEqual(L.close_frames(0.5, 10.0, 17), 0)
        self.assertEqual(L.close_frames(20.0, 10.0, 40), tripo_trim.settle_frames(20.0, 10.0))
        self.assertEqual(L.close_frames(120.0, 2.0, 17), 8)

    def test_a_closed_run_keeps_striding_through_the_seam(self) -> None:
        """The close adds a share of the last-to-first offset on top of the motion: the feet never stop, unlike a blend to the first pose."""

        joints = joints_of(phases(15, 2.6, 12), grow=0.004)
        found = L.loop_window(joints, FEET, PELVIS, 1.0, 24.0)
        cut = joints[found["first"] : found["last"] + 1].copy()
        count = 6
        weights = L.close_weights(count)
        closed = cut.copy()
        closed[-count:] += weights[:, None, None] * (cut[0] - cut[-1])[None]
        row = L.gait_numbers(closed, FEET, PELVIS, 1.0, 24.0)
        self.assertEqual(row["still_steps"], 0)
        self.assertTrue(np.allclose(closed[-1], closed[0]))
        settled = np.concatenate([cut, cut[-1][None] + weights[:, None, None] * (cut[0] - cut[-1])[None], np.repeat(cut[:1], 4, axis=0)])
        self.assertGreater(L.gait_numbers(settled, FEET, PELVIS, 1.0, 24.0)["still_steps"], 0)


def walking(period: int = 30, stand_from: int = 10 ** 6, degrees: float = 25.0):
    """The biped's thighs swinging past each other, standing still from frame `stand_from`."""

    def pose(frame: int):
        angle = degrees * math.sin(2.0 * math.pi * min(frame, stand_from) / period)
        return {"LeftUpLeg": (local("LeftUpLeg"), turn("x", angle)), "RightUpLeg": (local("RightUpLeg"), turn("x", -angle))}

    return pose


class OnTheExportedFiles(Biped):
    def test_a_walking_move_passes_and_a_retreat_that_stands_fails(self) -> None:
        anims = {"unit_move": self.load(self.clip("move", 61, walking())), "unit_retreat": self.load(self.clip("retreat", 76, walking(stand_from=60)))}
        findings, rows = L.loop_findings(self.mesh, anims)
        self.assertEqual([item["subject"] for item in findings], ["unit_retreat"])
        self.assertEqual(findings[0]["rule"], "TRIPO-LOOP-STANDS")
        self.assertEqual(rows["unit_move"]["still_steps"], 0)
        self.assertGreater(rows["unit_retreat"]["still_share"], 0.1)
        self.assertGreaterEqual(findings[0]["frame"], 55)

    def test_only_the_move_and_the_retreat_are_judged(self) -> None:
        anims = {f"unit_{role}": self.load(self.clip(role, 40, lambda frame: {})) for role in ("idle", "attack", "defend", "death")}
        self.assertEqual(L.loop_findings(self.mesh, anims), ([], {}))

    def test_the_unit_checks_run_it_for_a_humanoid(self) -> None:
        anims = {"unit_retreat": self.load(self.clip("retreat", 40, lambda frame: {}))}
        report: dict = {}
        findings = TC.body_findings(self.mesh, anims, report)
        self.assertIn("TRIPO-LOOP-STANDS", [item["rule"] for item in findings])
        self.assertEqual(report["gait"]["unit_retreat"]["still_share"], 1.0)

    def test_pose_check_judges_a_gait_candidate(self) -> None:
        run = pose_check.gait(self.mesh, self.load(self.clip("retreat", 121, walking(stand_from=90))))
        self.assertGreater(run["whole_still_share"], 0.1)
        self.assertEqual(run["reasons"], [])
        self.assertEqual((run["window"][1] - run["window"][0]) % 30, 0)
        self.assertLessEqual(run["window"][1], 90)
        stand = pose_check.gait(self.mesh, self.load(self.clip("move", 40, lambda frame: {})))
        self.assertIsNone(stand["window"])
        self.assertIn("never strides", stand["reasons"][0])


JOINTS = [("Hips", -1, (0.0, 0.55, 0.0)), ("LeftUpLeg", 0, (-0.1, 0.5, 0.0)), ("LeftFoot", 1, (-0.1, 0.05, 0.0)),
          ("RightUpLeg", 0, (0.1, 0.5, 0.0)), ("RightFoot", 3, (0.1, 0.05, 0.0)), ("Head", 0, (0.0, 1.0, 0.0))]


def humanoid_glb(clips: dict, fps: float = 24.0) -> bytes:
    """A skinned GLB with Tripo's joint names and, per clip, the thighs swung by the clip's per-frame angles (degrees), one against the other."""

    blob = bytearray()
    views, accessors = [], []

    def add(values, kind: str, component: int = 5126) -> int:
        data = np.asarray(values, dtype="<f4" if component == 5126 else "<u2").tobytes()
        views.append({"buffer": 0, "byteOffset": len(blob), "byteLength": len(data)})
        blob.extend(data)
        blob.extend(b"\0" * (-len(blob) % 4))
        accessors.append({"bufferView": len(views) - 1, "componentType": component, "count": len(values), "type": kind})
        return len(accessors) - 1

    nodes = []
    for index, (name, parent, position) in enumerate(JOINTS):
        base = JOINTS[parent][2] if parent >= 0 else (0.0, 0.0, 0.0)
        nodes.append({"name": "mixamorig:" + name, "translation": [position[i] - base[i] for i in range(3)],
                      "children": [child for child, joint in enumerate(JOINTS) if joint[1] == index]})
    inverse = [[1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, -x, -y, -z, 1] for _name, _parent, (x, y, z) in JOINTS]
    nodes.append({"name": "body", "mesh": 0, "skin": 0})
    primitive = {"attributes": {"POSITION": add([[0, 0, 0], [0.1, 0, 0], [0, 1, 0]], "VEC3"), "JOINTS_0": add([[0, 0, 0, 0]] * 3, "VEC4", 5123),
                                "WEIGHTS_0": add([[1, 0, 0, 0]] * 3, "VEC4")}}
    animations = []
    for name, angles in clips.items():
        samplers, channels = [], []
        for node, sign in ((1, 1.0), (3, -1.0)):
            half = np.radians(sign * np.asarray(angles, float)) / 2.0
            quats = np.stack([np.sin(half), np.zeros_like(half), np.zeros_like(half), np.cos(half)], axis=1)
            samplers.append({"input": add(np.arange(len(half)) / fps, "SCALAR"), "output": add(quats, "VEC4"), "interpolation": "LINEAR"})
            channels.append({"sampler": len(samplers) - 1, "target": {"node": node, "path": "rotation"}})
        animations.append({"name": name, "samplers": samplers, "channels": channels})
    document = {"asset": {"version": "2.0"}, "buffers": [{"byteLength": len(blob)}], "bufferViews": views, "accessors": accessors, "nodes": nodes,
                "meshes": [{"primitives": [primitive]}], "skins": [{"joints": list(range(len(JOINTS))), "inverseBindMatrices": add(inverse, "MAT4")}],
                "animations": animations}
    document["buffers"][0]["byteLength"] = len(blob)
    text = json.dumps(document).encode()
    text += b" " * (-len(text) % 4)
    body = struct.pack("<II", len(text), 0x4E4F534A) + text + struct.pack("<II", len(blob), 0x004E4942) + bytes(blob)
    return struct.pack("<III", 0x46546C67, 2, 12 + len(body)) + body


def swing(phase: np.ndarray, degrees: float = 25.0, grow: float = 0.0) -> np.ndarray:
    return degrees * (1.0 + grow * np.arange(len(phase))) * np.sin(phase)


class FromAGlb(unittest.TestCase):
    def setUp(self) -> None:
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.glb = Path(temp.name) / "unit__rigged.glb"
        self.clips = {"idle": np.zeros(60), "walk": swing(phases(0, 2, 0)), "flee_01": swing(phases(15, 2.6, 12), grow=0.004), "chop": np.zeros(50),
                      "hit_to_body_01": np.zeros(30), "defeat_03": np.zeros(60)}
        self.glb.write_bytes(humanoid_glb(self.clips))
        self.roles = {"idle": "idle", "move": "walk", "attack": "chop", "defend": "hit_to_body_01", "retreat": "flee_01", "death": "defeat_03"}
        self.spec = run_pilot.prepare_spec(tripo_spec())
        self.spec["tripo"]["roles"] = dict(self.roles)
        self.spec["tripo"].pop("trim", None)

    def command(self) -> list:
        return tripo_intake.prepare_command(Path("blender.exe"), self.spec, {"rigged": self.glb}, Path("out"), Path("report.json"))

    @staticmethod
    def after(command: list, flag: str) -> list:
        if flag not in command:
            return []
        rest = command[command.index(flag) + 1:]
        return rest[:next((i for i, item in enumerate(rest) if item.startswith("--")), len(rest))]

    def test_the_walk_keeps_every_frame_and_the_flee_is_cut_to_its_run(self) -> None:
        found = L.auto_windows(self.glb, self.roles)
        self.assertEqual(sorted(found), ["move", "retreat"])
        self.assertTrue(found["move"]["whole"])
        self.assertEqual(found["retreat"]["clip"], "flee_01")
        self.assertGreaterEqual(found["retreat"]["first"], 15 + EASE)
        self.assertEqual(found["retreat"]["frames"] % PERIOD, 0)

    def test_only_the_move_and_the_retreat_get_a_window_and_an_explicit_trim_wins(self) -> None:
        self.assertEqual(L.STRIDE_ROLES, ("move", "retreat"))
        self.assertEqual(L.auto_windows(self.glb, self.roles, explicit={"retreat", "move"}), {})
        self.assertEqual(L.auto_windows(self.glb.with_name("missing.glb"), self.roles), {})
        self.assertNotIn("move", L.auto_windows(self.glb, dict(self.roles, move="idle")), "a clip that never strides has no window")

    def test_the_intake_passes_the_window_and_closes_both_gaits(self) -> None:
        command = self.command()
        windows = [command[i + 1] for i, item in enumerate(command) if item == "--loop-window"]
        self.assertEqual(len(windows), 1, "the walk loops as it is and is not cut")
        role, _, span = windows[0].partition("=")
        first, last = (int(value) for value in span.split(":"))
        self.assertEqual(role, "retreat")
        self.assertEqual((last - first) % PERIOD, 0)
        self.assertEqual(self.after(command, "--loop-close"), ["move", "retreat"])
        self.assertFalse([item for i, item in enumerate(command) if command[i - 1] == "--trim-end" and item.startswith("retreat=")],
                         "a windowed retreat is not trimmed by the still-tail rule as well")

    def test_the_jobs_trim_wins_and_the_rule_can_be_switched_off_or_limited(self) -> None:
        self.spec["tripo"]["trim"] = {"retreat": 40}
        command = self.command()
        self.assertNotIn("--loop-window", command)
        self.assertEqual(self.after(command, "--loop-close"), ["move"])
        self.assertIn("retreat=40", command)
        del self.spec["tripo"]["trim"]
        self.spec["tripo"]["loop_window"] = False
        command = self.command()
        self.assertNotIn("--loop-window", command)
        self.assertNotIn("--loop-close", command)
        self.spec["tripo"]["loop_window"] = ["retreat"]
        self.assertEqual(self.after(self.command(), "--loop-close"), ["retreat"])

    def test_a_gait_that_never_strides_keeps_the_settle(self) -> None:
        self.spec["tripo"]["roles"]["retreat"] = "hit_to_body_01"
        command = self.command()
        self.assertEqual(self.after(command, "--loop-close"), ["move"])
        self.assertIn("retreat", self.after(command, "--settle"))


VANILLA_LOCOMOTION = ("moving_rifle", "moving_mg", "march_rifle", "march_mg", "retreat_rifle", "retreat_mg", "charge_rifle", "charge_mg")


@unittest.skipUnless((UNITS / "GER_infantry.mesh").is_file(), "the game is not installed here")
class VanillaCalibration(unittest.TestCase):
    """The limits come from vanilla's GER infantry, whose clips every western infantry mesh plays."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.mesh = pdx_deform.load_mesh(UNITS / "GER_infantry.mesh")
        cls.rows = {clip: L.clip_gait(cls.mesh, pdx_deform.load_anim(UNITS / f"GER_infantry_{clip}.anim")) for clip in VANILLA_LOCOMOTION}

    def test_vanillas_slowest_stride_and_worst_seam_are_the_recorded_ones(self) -> None:
        self.assertAlmostEqual(min(row["slowest"] for row in self.rows.values()), L.VANILLA_MIN_STRIDE_SPEED, delta=0.002)
        self.assertAlmostEqual(max(row["seam_share"] for row in self.rows.values()), L.VANILLA_SEAM_SHARE, delta=0.01)

    def test_every_vanilla_locomotion_clip_passes(self) -> None:
        for clip, row in self.rows.items():
            with self.subTest(clip=clip):
                self.assertIsNone(L.stands_reason(row, "move"))
                self.assertEqual(row["still_steps"], 0)

    def test_vanillas_idle_and_standing_attack_stand(self) -> None:
        for clip in ("idle_rifle", "attack_stand_rifle"):
            row = L.clip_gait(self.mesh, pdx_deform.load_anim(UNITS / f"GER_infantry_{clip}.anim"))
            with self.subTest(clip=clip):
                self.assertGreater(row["still_share"], 0.9)

    def test_a_vanilla_walk_is_its_own_whole_window(self) -> None:
        from lib import pdx_motion

        legs = pdx_motion.find_legs(self.mesh)
        anim = pdx_deform.load_anim(UNITS / "GER_infantry_march_rifle.anim")
        found = L.loop_window(pdx_motion.posed_joints(self.mesh, anim), (legs.legs[0].ankle, legs.legs[1].ankle), legs.pelvis, self.mesh.height, anim.fps)
        self.assertTrue(found["whole"], found)


if __name__ == "__main__":
    unittest.main()
