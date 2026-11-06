"""Ground-contact correction of exported `.anim` files, on synthetic units (no Blender)."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))
sys.path.insert(0, str(PIPELINE / "tests"))

from lib import pdx_deform, pdx_ground
from test_deformation_checks import BONES, _obj, _prop, two_arm_strip, write_anim, write_mesh

IDENTITY = (0.0, 0.0, 0.0, 1.0)


def root_moves(heights):
    """A clip that moves the root up or down by `heights[frame]`."""

    return lambda frame: {"Root": ((0.0, heights[frame], 0.0), IDENTITY)}


class Grounding(unittest.TestCase):
    def run_clip(self, heights, death=False):
        positions, triangles, bones = two_arm_strip()
        with tempfile.TemporaryDirectory() as folder:
            mesh, anim, out = Path(folder) / "u.mesh", Path(folder) / "u_idle.anim", Path(folder) / "fixed.anim"
            write_mesh(mesh, positions, triangles, bones)
            write_anim(anim, len(heights), root_moves(heights))
            # The strip's rest root sits at y = 1 with the strip's lowest point at y = 1 as well.
            correction = pdx_ground.ground(mesh, anim, out, death=death)
            skinned = pdx_deform.load_mesh(mesh)
            report = pdx_deform.deformation_report(skinned, pdx_deform.load_anim(out))
            size = (anim.stat().st_size, out.stat().st_size)
        return correction, report, size

    def test_a_sinking_clip_is_lifted_onto_the_ground(self) -> None:
        correction, report, (before, after) = self.run_clip([0.7, 0.5, 0.3, 0.7])
        self.assertTrue(correction.corrected)
        self.assertEqual(correction.root, "Root")
        self.assertAlmostEqual(report.lowest, 0.0, places=4)
        self.assertAlmostEqual(report.highest_lowest, 0.0, places=4)
        self.assertEqual(before, after, "only existing keys change")

    def test_a_hovering_clip_is_brought_down(self) -> None:
        correction, report, _size = self.run_clip([1.0, 1.4, 1.8, 1.0])
        self.assertTrue(correction.corrected)
        self.assertAlmostEqual(correction.largest_shift, 0.8 / 0.2, places=3)  # 0.8 units on a strip 0.2 tall
        self.assertAlmostEqual(report.highest_lowest, 0.0, places=4)

    def test_a_death_is_lifted_out_of_the_ground_but_never_lowered(self) -> None:
        correction, report, _size = self.run_clip([1.0, 1.5, 0.6, 0.6], death=True)
        self.assertTrue(correction.corrected)
        self.assertAlmostEqual(report.lowest, 0.0, places=4)
        self.assertGreater(report.highest_lowest, 2.0, "the raised frame keeps its height")

    def test_a_grounded_clip_is_left_alone(self) -> None:
        correction, _report, _size = self.run_clip([1.0, 1.0, 1.0])
        self.assertFalse(correction.corrected)
        self.assertEqual(correction.reason, "already on the ground")

    def test_a_root_without_translation_keys_is_reported(self) -> None:
        positions, triangles, bones = two_arm_strip()
        with tempfile.TemporaryDirectory() as folder:
            mesh, anim = Path(folder) / "u.mesh", Path(folder) / "u_idle.anim"
            write_mesh(mesh, positions, triangles, bones)
            data = b"@@b@" + _obj("info", 1) + _prop("fps", "f", [15.0]) + _prop("sa", "i", [2]) + _prop("j", "i", [len(BONES)])
            for name, _parent, _position in BONES:
                data += _obj(name, 2) + _prop("sa", "s", ["q"]) + _prop("t", "f", [0.0, 0.0, 0.0]) + _prop("q", "f", list(IDENTITY)) + _prop("s", "f", [1.0])
            data += _obj("samples", 1) + _prop("q", "f", list(IDENTITY) * len(BONES) * 2)
            anim.write_bytes(data)
            correction = pdx_ground.ground(mesh, anim, Path(folder) / "fixed.anim")
        self.assertFalse(correction.corrected)
        self.assertIn("no translation keys", correction.reason)


if __name__ == "__main__":
    unittest.main()
