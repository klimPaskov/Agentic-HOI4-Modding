"""The still-tail trim rule: a role clip that ends standing still is cut after a short settle, by rule, and the job's own trim wins."""

from __future__ import annotations

import json
import struct
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))

import run_pilot
import tripo_intake
from lib import tripo_trim as T
from tests.test_tripo_route import tripo_spec


def motion_profile(moving: int, still: int, speed: float = 40.0, rest: float = 1.0) -> np.ndarray:
    """`moving` frames of a swinging motion (about `speed` degrees a frame) and then `still` frames of breathing (`rest` degrees)."""

    wave = speed * (0.6 + 0.4 * np.sin(np.arange(moving) * 0.7))
    return np.concatenate([wave, np.full(still, rest)])


def glb_with_clips(clips: dict, fps: float = 24.0) -> bytes:
    """A GLB with one joint per clip channel and, per clip, a rotation track made from per-frame angles about z (degrees)."""

    blob = bytearray()
    views, accessors, nodes, animations = [], [], [], []

    def add(values: np.ndarray, kind: str) -> int:
        data = np.asarray(values, dtype="<f4").tobytes()
        views.append({"buffer": 0, "byteOffset": len(blob), "byteLength": len(data)})
        blob.extend(data)
        count = len(values)
        accessors.append({"bufferView": len(views) - 1, "componentType": 5126, "count": count, "type": kind})
        return len(accessors) - 1

    for name, angles in clips.items():
        samplers, channels = [], []
        for joint in range(2):
            nodes.append({"name": f"J{len(nodes)}"})
            degrees = np.concatenate([[0.0], np.cumsum(angles)]) * (1 if joint == 0 else -0.5)
            half = np.radians(degrees) / 2.0
            quats = np.stack([np.zeros_like(half), np.zeros_like(half), np.sin(half), np.cos(half)], axis=1)
            times = np.arange(len(degrees)) / fps
            samplers.append({"input": add(times, "SCALAR"), "output": add(quats, "VEC4"), "interpolation": "LINEAR"})
            channels.append({"sampler": len(samplers) - 1, "target": {"node": len(nodes) - 1, "path": "rotation"}})
        animations.append({"name": name, "samplers": samplers, "channels": channels})
    document = {"asset": {"version": "2.0"}, "buffers": [{"byteLength": len(blob)}], "bufferViews": views, "accessors": accessors, "nodes": nodes, "animations": animations}
    text = json.dumps(document).encode()
    text += b" " * (-len(text) % 4)
    blob.extend(b"\0" * (-len(blob) % 4))
    body = struct.pack("<II", len(text), 0x4E4F534A) + text + struct.pack("<II", len(blob), 0x004E4942) + bytes(blob)
    return struct.pack("<III", 0x46546C67, 2, 12 + len(body)) + body


class Rule(unittest.TestCase):
    def test_a_clip_that_goes_still_keeps_a_short_settle_and_drops_the_rest(self) -> None:
        result = T.still_tail(motion_profile(60, 60))
        self.assertIsNotNone(result)
        self.assertEqual(result["from_frames"], 120)
        self.assertTrue(60 <= result["still_from_frame"] <= 64, result)
        self.assertEqual(result["keep_frames"], result["still_from_frame"] + 12)  # half a second at 24 frames a second
        self.assertLess(result["keep_frames"], 120 * 0.8)

    def test_the_floor_and_the_settle_follow_the_clips_own_peak_and_the_frame_rate(self) -> None:
        slow = T.still_tail(motion_profile(60, 60, speed=10.0, rest=0.2))
        fast = T.still_tail(motion_profile(60, 60, speed=100.0, rest=2.0))
        self.assertAlmostEqual(fast["floor_degrees"] / slow["floor_degrees"], 10.0, delta=1.5)
        self.assertEqual(fast["keep_frames"], slow["keep_frames"])  # both go still at the same frame
        at_30 = T.still_tail(motion_profile(75, 75), fps=30.0)
        self.assertEqual(at_30["keep_frames"] - at_30["still_from_frame"], 15)

    def test_one_snapping_frame_does_not_set_the_peak(self) -> None:
        profile = motion_profile(60, 60, speed=20.0, rest=0.5)
        profile[10] = 600.0
        result = T.still_tail(profile)
        self.assertLess(result["peak_degrees"], 60.0)
        self.assertTrue(60 <= result["still_from_frame"] <= 64, result)

    def test_a_clip_that_never_goes_still_or_barely_ends_still_is_left_alone(self) -> None:
        self.assertIsNone(T.still_tail(motion_profile(120, 0)))
        self.assertIsNone(T.still_tail(motion_profile(100, 20)))  # would save less than a fifth
        self.assertIsNone(T.still_tail(np.zeros(100)))
        self.assertIsNone(T.still_tail(motion_profile(8, 40)))  # would leave less than a second

    def test_a_pause_in_the_middle_is_not_the_still_tail(self) -> None:
        profile = np.concatenate([motion_profile(30, 0), np.full(20, 0.5), motion_profile(40, 50)])
        result = T.still_tail(profile)
        self.assertGreaterEqual(result["still_from_frame"], 90)


class Settle(unittest.TestCase):
    """An action clip is looped by the game, so it ends in its first pose over a length its own motion sets."""

    def test_a_clip_that_already_ends_in_its_first_pose_gets_no_frames(self) -> None:
        self.assertEqual(T.settle_frames(0.0), 0)
        self.assertEqual(T.settle_frames(T.SETTLE_TOLERANCE_DEGREES), 0)

    def test_no_bone_turns_faster_than_the_rate_in_the_settle(self) -> None:
        for turn in (5.0, 40.0, 118.7, 180.0):
            for rate in (4.0, 10.5):
                frames = T.settle_frames(turn, rate)
                steps = np.diff(np.concatenate([[0.0], T.settle_weights(frames)])) * turn
                if frames < T.SETTLE_MAX_FRAMES:
                    self.assertLessEqual(float(steps.max()), rate + 1e-6, (turn, rate, frames))
                self.assertGreaterEqual(frames, T.SETTLE_MIN_FRAMES)

    def test_a_bigger_turn_takes_more_frames_and_the_length_is_capped(self) -> None:
        self.assertLess(T.settle_frames(20.0), T.settle_frames(100.0))
        self.assertEqual(T.settle_frames(10000.0), T.SETTLE_MAX_FRAMES)

    def test_the_weights_end_exactly_on_the_first_pose_and_never_go_back(self) -> None:
        weights = T.settle_weights(12)
        self.assertEqual(len(weights), 12)
        self.assertAlmostEqual(float(weights[-1]), 1.0)
        self.assertTrue(np.all(np.diff(weights) >= 0))

    def test_the_rate_is_the_clips_own_fast_motion_but_never_above_the_cap(self) -> None:
        self.assertAlmostEqual(T.settle_rate(np.full(60, 3.0)), 3.0, places=1)
        self.assertEqual(T.settle_rate(np.full(60, 40.0)), T.SETTLE_MAX_RATE)
        self.assertEqual(T.settle_rate(np.zeros(60)), 1.0)


class FromAGlb(unittest.TestCase):
    def setUp(self) -> None:
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.folder = Path(temp.name)
        self.clips = {
            "idle": motion_profile(120, 0, speed=2.0),
            "A heavy warrior stands holding a long poleaxe upright in his right hand": motion_profile(60, 60),
            "hit_to_body_01": motion_profile(30, 0),
            "flee_01": motion_profile(64, 0),
            "defeat_03": motion_profile(60, 70),
        }
        self.glb = self.folder / "unit__rigged.glb"
        self.glb.write_bytes(glb_with_clips(self.clips))
        self.roles = {"idle": "idle", "move": "walk", "attack": "A heavy warrior stands", "defend": "hit_to_body_01", "retreat": "flee_01", "death": "defeat_03"}

    def test_the_motion_is_read_from_the_rotation_tracks(self) -> None:
        doc, binary = T._clip_check().load_glb(self.glb)
        motion = T.clip_motion(doc, binary, doc["animations"][1])
        self.assertEqual(len(motion), 120)
        self.assertAlmostEqual(float(motion[70]), 1.5, delta=0.1)  # two joints turn 1 and 0.5 degrees a frame

    def test_only_attack_defend_and_retreat_are_trimmed_and_only_when_they_end_still(self) -> None:
        found = T.auto_trims(self.glb, self.roles)
        self.assertEqual(list(found), ["attack"])
        self.assertEqual(found["attack"]["clip"], "A heavy warrior stands holding a long poleaxe upright in his right hand")
        # a death that ends lying still, an idle and a walk are never touched, whatever the roles asked
        self.assertNotIn("death", found)
        self.assertEqual(T.auto_trims(self.glb, self.roles, apply_to=("idle", "move", "death")), {"death": T.auto_trims(self.glb, self.roles, apply_to=("death",))["death"]})
        self.assertNotIn("death", T.DEFAULT_ROLES)
        self.assertNotIn("idle", T.DEFAULT_ROLES)
        self.assertNotIn("move", T.DEFAULT_ROLES)

    def test_an_explicit_trim_wins_and_an_unreadable_file_gives_nothing(self) -> None:
        self.assertEqual(T.auto_trims(self.glb, self.roles, explicit={"attack"}), {})
        self.assertEqual(T.auto_trims(self.folder / "missing.glb", self.roles), {})


class Intake(unittest.TestCase):
    def setUp(self) -> None:
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        folder = Path(temp.name)
        clips = {"idle": motion_profile(60, 0, speed=2.0), "walk": motion_profile(40, 0), "chop": motion_profile(60, 60), "hit_to_body_01": motion_profile(30, 0),
                 "flee_01": motion_profile(60, 0), "defeat_03": motion_profile(60, 70)}
        glb = folder / "orc_test__rigged.glb"
        glb.write_bytes(glb_with_clips(clips))
        self.files = {"rigged": glb}
        self.spec = run_pilot.prepare_spec(tripo_spec())
        self.spec["tripo"]["roles"]["attack"] = "chop"

    def command(self) -> list:
        return tripo_intake.prepare_command(Path("blender.exe"), self.spec, self.files, Path("out"), Path("report.json"))

    def test_the_attack_that_ends_still_gets_an_exact_trim_and_nothing_else_does(self) -> None:
        command = self.command()
        ends = [command[i + 1] for i, item in enumerate(command) if item == "--trim-end"]
        self.assertEqual(len(ends), 1)
        self.assertTrue(ends[0].startswith("attack="), ends)
        self.assertLess(int(ends[0].split("=")[1]), 120)
        self.assertNotIn("--trim", command)

    def test_the_action_roles_settle_back_to_their_first_pose_and_the_job_can_limit_it(self) -> None:
        command = self.command()
        self.assertEqual(command[command.index("--settle") + 1:command.index("--settle") + 4], ["attack", "defend", "retreat"])
        self.spec["tripo"]["settle"] = ["attack"]
        command = self.command()
        self.assertEqual(command[command.index("--settle") + 1], "attack")
        self.assertNotIn("defend", command[command.index("--settle"):command.index("--settle") + 3])
        self.spec["tripo"]["settle"] = False
        self.assertNotIn("--settle", self.command())

    def test_every_role_is_untwisted_by_default_and_the_job_can_switch_it_off(self) -> None:
        command = self.command()
        self.assertIn("--untwist", command)
        self.assertIn("retreat", command[command.index("--untwist"):])
        self.spec["tripo"]["untwist"] = False
        self.assertNotIn("--untwist", self.command())

    def test_the_jobs_own_trim_wins_and_the_rule_can_be_switched_off(self) -> None:
        self.spec["tripo"]["trim"] = {"attack": 100, "idle": 120}
        command = self.command()
        self.assertNotIn("--trim-end", command)
        self.assertEqual([command[i + 1] for i, item in enumerate(command) if item == "--trim"], ["attack=100", "idle=120"])
        del self.spec["tripo"]["trim"]
        self.spec["tripo"]["auto_trim"] = False
        self.assertNotIn("--trim-end", self.command())
        self.spec["tripo"]["auto_trim"] = ["defend"]
        self.assertNotIn("--trim-end", self.command())
        self.spec["tripo"]["auto_trim"] = ["attack"]
        self.assertIn("--trim-end", self.command())


if __name__ == "__main__":
    unittest.main()
