"""Every exported `.anim` holds one sample per frame of its action (io_pdx_mesh's operator exports the scene range)."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE / "adapter"))
sys.path.insert(0, str(PIPELINE / "tests"))

from anim_frame_range import AnimFrameRangeError, verify_frame_range
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


@unittest.skipUnless(BLENDER and BLENDER.exists(), "no supported Blender installed")
class ExportClipInBlender(unittest.TestCase):
    def test_export_clip_writes_the_actions_frames_whatever_the_scene_range(self) -> None:
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
