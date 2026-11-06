"""Every exported `.anim` holds one sample per frame of its action, at 30 fps.

io_pdx_mesh's operator exports the scene range, and its exporter writes the scene's rate (24 in a factory scene).
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE / "adapter"))
sys.path.insert(0, str(PIPELINE / "tests"))

from anim_frame_range import AnimFpsError, AnimFrameRangeError, retime_action, verify_fps, verify_frame_range
from test_deformation_checks import write_anim
from test_winding_regression import BLENDER

SCRIPT = PIPELINE / "tests" / "blender_export_clip_integration.py"


class FrameRange(unittest.TestCase):
    def test_a_clip_with_one_sample_per_frame_passes(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "u_idle.anim"
            write_anim(path, 10, lambda frame: {})
            self.assertEqual(verify_frame_range(path, 1, 10), 10)

    def test_a_padded_clip_fails(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "u_idle.anim"
            write_anim(path, 85, lambda frame: {})
            with self.assertRaisesRegex(AnimFrameRangeError, "padded"):
                verify_frame_range(path, 1, 10)

    def test_a_cut_clip_fails(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "u_attack.anim"
            write_anim(path, 80, lambda frame: {})
            with self.assertRaisesRegex(AnimFrameRangeError, "cut short"):
                verify_frame_range(path, 1, 120)


class FrameRate(unittest.TestCase):
    def test_a_clip_at_30_passes(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "u_idle.anim"
            write_anim(path, 10, lambda frame: {}, fps=30.0)
            self.assertEqual(verify_fps(path), 30.0)

    def test_a_clip_at_the_factory_24_fails(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "u_idle.anim"
            write_anim(path, 10, lambda frame: {}, fps=24.0)
            with self.assertRaisesRegex(AnimFpsError, "24 frames a second, not 30"):
                verify_fps(path)


class Point(list):
    """A Blender key coordinate: indexable, x first."""


class Key:
    def __init__(self, frame: float, value: float) -> None:
        self.co = Point([frame, value])
        self.handle_left = Point([frame - 1.0, value])
        self.handle_right = Point([frame + 1.0, value])


class Curve:
    def __init__(self, frames) -> None:
        self.keyframe_points = [Key(frame, 0.0) for frame in frames]
        self.updated = False

    def update(self) -> None:
        self.updated = True


class Layered:
    """A Blender 4.4+ action: layers, strips, channel bags."""

    def __init__(self, curves) -> None:
        bag = type("Bag", (), {"fcurves": curves})()
        strip = type("Strip", (), {"channelbags": [bag]})()
        self.layers = [type("Layer", (), {"strips": [strip]})()]
        self.use_frame_range = True
        self.frame_start, self.frame_end = 1, 25


class Retime(unittest.TestCase):
    def test_24_to_30_keeps_the_clip_length_in_seconds(self) -> None:
        curve = Curve([1, 13, 25])
        action = Layered([curve])
        self.assertEqual(retime_action(action, 1, 25, 24.0, 30.0), (1, 31))
        self.assertEqual([key.co[0] for key in curve.keyframe_points], [1.0, 16.0, 31.0])
        self.assertEqual(curve.keyframe_points[1].handle_left[0], 1 + 11 * 1.25)
        self.assertTrue(curve.updated)
        self.assertEqual((action.frame_start, action.frame_end), (1, 31))
        # 24 frames at 24 fps and 30 frames at 30 fps are both one second.
        self.assertEqual((25 - 1) / 24.0, (31 - 1) / 30.0)

    def test_a_clip_already_at_30_is_left_alone(self) -> None:
        curve = Curve([1, 10])
        self.assertEqual(retime_action(Layered([curve]), 1, 10, 30.0, 30.0), (1, 10))
        self.assertEqual([key.co[0] for key in curve.keyframe_points], [1.0, 10.0])

    def test_a_legacy_action_is_retimed_through_its_own_curves(self) -> None:
        curve = Curve([0, 48])
        legacy = type("Legacy", (), {"fcurves": [curve]})()
        self.assertEqual(retime_action(legacy, 0, 48, 24.0), (0, 60))
        self.assertEqual(curve.keyframe_points[1].co[0], 60.0)


@unittest.skipUnless(BLENDER and BLENDER.exists(), "no supported Blender installed")
class ExportClipInBlender(unittest.TestCase):
    def test_export_clip_writes_the_actions_frames_at_30_whatever_the_scene(self) -> None:
        # Not --factory-startup: the test needs the installed io_pdx_mesh.
        completed = subprocess.run(
            [str(BLENDER), "--background", "--python-exit-code", "1", "--python", str(SCRIPT)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=600,
        )
        if "io_pdx_mesh is not installed" in completed.stdout + completed.stderr:
            self.skipTest("io_pdx_mesh is not installed for this Blender")
        self.assertEqual(completed.returncode, 0, completed.stdout[-3000:] + completed.stderr[-3000:])
        self.assertIn("EXPORT_CLIP_INTEGRATION_OK", completed.stdout)


if __name__ == "__main__":
    unittest.main()
