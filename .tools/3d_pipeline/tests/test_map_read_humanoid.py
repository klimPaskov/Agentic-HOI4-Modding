"""TRIPO-MAP-READ for a humanoid (pixels of the idle's silhouette changed at game size), the raised-hands rule for an unarmed gait, and the
refusal of a diffuse map recoloured by a global colour transform, without Blender."""

from __future__ import annotations

import math
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
from PIL import Image

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))
sys.path.insert(0, str(PIPELINE / "tests"))
sys.path.insert(0, str(PIPELINE / "tripo"))

import run_pilot
import tripo_intake
from lib import map_read, texture_look, tripo_arms
from lib import pdx_deform as P
from test_quadruped_clips import towered_animal, turning
from test_tripo_route import tripo_spec


def spike(frames: int, at: int, yaw: float) -> P.Animation:
    """The root holds still except one frame, turned by `yaw` degrees."""

    angle = np.zeros(frames)
    angle[at] = math.radians(yaw) / 2
    q = np.stack([np.zeros(frames), np.sin(angle), np.zeros(frames), np.cos(angle)], axis=1)
    still = {"t": np.tile([0.0, 1.5, -3.0], (frames, 1)), "q": np.tile([0.0, 0.0, 0.0, 1.0], (frames, 1)), "s": np.ones(frames)}
    return P.Animation(fps=30.0, frames=frames, channels={"Root": {"t": np.zeros((frames, 3)), "q": q, "s": np.ones(frames)}, "Head": still})


class HumanoidMapRead(unittest.TestCase):
    def test_an_attack_that_reads_as_the_idle_fails_and_a_turned_defend_passes(self) -> None:
        mesh = towered_animal()
        anims = {"u_idle": turning(12), "u_attack": turning(12, yaw=2.0), "u_defend": turning(12, yaw=30.0)}
        found, numbers = map_read.humanoid_findings(mesh, anims)
        self.assertEqual([(item["rule"], item["subject"]) for item in found], [("TRIPO-MAP-READ", "u_attack")])
        self.assertLess(numbers["u_attack"]["pixels"], map_read.MIN_HUMANOID_READ_PIXELS["attack"])
        self.assertGreater(numbers["u_defend"]["pixels"], map_read.MIN_HUMANOID_READ_PIXELS["defend"])

    def test_a_pose_held_for_one_frame_in_thirty_does_not_read(self) -> None:
        mesh = towered_animal()
        found, numbers = map_read.humanoid_findings(mesh, {"u_idle": turning(30), "u_defend": spike(30, 15, 40.0)})
        self.assertGreater(numbers["u_defend"]["peak_pixels"], map_read.MIN_HUMANOID_READ_PIXELS["defend"], "the one frame changes the outline")
        self.assertEqual([item["subject"] for item in found], ["u_defend"], "but the clip reads as the idle")

    def test_no_idle_no_reading(self) -> None:
        self.assertEqual(map_read.humanoid_findings(towered_animal(), {"u_attack": turning(12)}), ([], {}))

    def test_the_limits_sit_under_every_passed_humanoid_and_over_the_failed_zombie(self) -> None:
        # the readings of lib/map_read.py's calibration (exported files, 2026-11-18)
        passed = {"attack": (441, 320, 530), "defend": (453, 166, 493)}
        failed = {"attack": 192, "defend": 104}
        for role, limit in map_read.MIN_HUMANOID_READ_PIXELS.items():
            self.assertLessEqual(limit, min(passed[role]))
            self.assertGreater(limit, failed[role])


class RaisedHandsGait(unittest.TestCase):
    def command(self, **tripo):
        spec = run_pilot.prepare_spec(tripo_spec())
        spec["tripo"].update(tripo)
        return tripo_intake.prepare_command(Path("blender.exe"), spec, {"rigged": Path("r.glb")}, Path("out"), Path("report.json"))

    def test_an_unarmed_unit_levels_a_gait_only_when_its_hands_are_high(self) -> None:
        self.assertNotIn("--arm-level-high", self.command(), "an armed unit keeps its gait's arms")
        unarmed = self.command(weapon=None)
        at = unarmed.index("--arm-level-high")
        self.assertEqual(unarmed[at + 1 : at + 3], ["move", "retreat"])
        self.assertNotIn("--arm-level-high", self.command(weapon=None, arm_level_high=False))
        named = self.command(weapon=None, arm_level=["attack", "move"])
        self.assertEqual(named[named.index("--arm-level-high") + 1], "retreat", "a role levelled always is not levelled twice")

    def test_the_trigger_is_the_hands_high_rule(self) -> None:
        frames = 20
        up = np.tile([0.0, 2.2, 0.3], (frames, 1))
        down = np.tile([0.0, 1.0, 0.1], (frames, 1))
        shoulder, head = np.tile([0.0, 1.5, 0.0], (frames, 1)), np.tile([0.0, 1.8, 0.0], (frames, 1))
        self.assertIsNotNone(tripo_arms.hands_high(tripo_arms.hand_levels(up, up, shoulder, shoulder, head)), "a reaching walk over the head")
        self.assertIsNone(tripo_arms.hands_high(tripo_arms.hand_levels(down, down, shoulder, shoulder, head)), "a walk with the arms down")


class DiffuseLook(unittest.TestCase):
    def setUp(self) -> None:
        rng = np.random.default_rng(5)
        base = np.clip(rng.normal(110, 35, (128, 128, 3)) + np.linspace(0, 60, 128)[None, :, None], 0, 255)
        self.base = base.astype(np.uint8)

    def save(self, folder: Path, name: str, pixels: np.ndarray) -> Path:
        path = folder / name
        Image.fromarray(np.clip(pixels, 0, 255).astype(np.uint8), "RGB").save(path)
        return path

    def test_a_tinted_map_is_refused_and_the_untouched_one_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            source = self.save(folder, "export.png", self.base)
            untouched = texture_look.global_transform(source, self.save(folder, "same.png", self.base))
            self.assertFalse(untouched["recoloured"])
            self.assertIsNone(texture_look.refusal(untouched))
            tint = self.base.astype(float) @ np.array([[0.7, 0.1, 0.0], [0.1, 0.8, 0.1], [0.0, 0.1, 0.75]]).T + np.array([10.0, 18.0, 6.0])
            tinted = texture_look.global_transform(source, self.save(folder, "tinted.png", tint))
            self.assertTrue(tinted["recoloured"])
            self.assertIn("Regenerate the model", texture_look.refusal(tinted))

    def test_a_local_change_is_not_a_global_transform(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            source = self.save(folder, "export.png", self.base)
            edited = self.base.astype(float).copy()
            edited[20:60, 30:90] = (200.0, 40.0, 40.0)
            numbers = texture_look.global_transform(source, self.save(folder, "painted.png", edited))
            self.assertGreater(numbers["change"], texture_look.MIN_CHANGE)
            self.assertFalse(numbers["recoloured"])

    def test_the_route_refuses_the_export_when_the_map_was_tinted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            job = Path(tmp)
            (job / "src").mkdir()
            (job / "out").mkdir()
            self.save(job / "src", "base_color.png", self.base)
            textures = {"conversions": [{"image": "texture_0", "png": "out/texture_0.png"}]}
            self.save(job / "out", "texture_0.png", self.base)
            report = run_pilot.check_diffuse_look(job, {"diffuse": "src/base_color.png"}, textures)
            self.assertFalse(report["diffuse_look"]["recoloured"])
            self.save(job / "out", "texture_0.png", self.base.astype(float) * 0.6 + 20.0)
            with self.assertRaises(RuntimeError):
                run_pilot.check_diffuse_look(job, {"diffuse": "src/base_color.png"}, textures)


if __name__ == "__main__":
    unittest.main()
