"""The prop-fitting stage (fit_prop.py): its verdict, its texture packing, and the Blender fit on a small unit."""

from __future__ import annotations

import argparse
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))
sys.path.insert(0, str(PIPELINE / "tests"))

import numpy as np
from PIL import Image

import fit_prop
from lib import pdx_binary, pdx_deform
from test_winding_regression import BLENDER


def maps(folder: Path) -> Path:
    folder.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (16, 16), (120, 80, 40)).save(folder / "base_color.png")
    Image.new("L", (16, 16), 40).save(folder / "metallic.png")
    Image.new("L", (16, 16), 180).save(folder / "roughness.png")
    Image.new("RGB", (16, 16), (128, 128, 255)).save(folder / "normal.png")
    return folder


def args_for(out: Path, unit_type=None, stem=None) -> argparse.Namespace:
    return argparse.Namespace(out=out, unit_type=unit_type, stem=stem)


class Verdict(unittest.TestCase):
    def report(self, inside, under):
        return {"best": {"inside": inside, "under": under, "per_clip": {}}, "frames_checked": 10, "samples_per_frame": 100,
                "textures": {}, "unit": "u", "prop_stem": "u_prop"}

    def test_a_clean_grip_passes_and_names_the_check(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            out = Path(folder) / "props"
            out.mkdir()
            payload = fit_prop.verdict_for(self.report(inside=15, under=0), args_for(out, unit_type="spearman"))
            registration = (out / "registration_prop.md").read_text(encoding="utf-8")
        self.assertEqual(payload["verdict"], "pass")
        self.assertIn("check_unit_files.py", payload["next"][0])
        self.assertIn("--unit-type spearman", payload["next"][0])
        self.assertIn('name = "u_prop"', payload["outputs"]["meshsettings"])
        self.assertIn('texture_specular = "u_prop_specular.dds"', registration)

    def test_a_prop_in_the_ground_escalates(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            (Path(folder) / "props").mkdir()
            payload = fit_prop.verdict_for(self.report(inside=0, under=1), args_for(Path(folder) / "props"))
        self.assertEqual((payload["verdict"], payload["findings"][0]["rule"]), ("escalate", "PROP-CLIPS"))

    def test_a_prop_through_the_body_escalates(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            (Path(folder) / "props").mkdir()
            payload = fit_prop.verdict_for(self.report(inside=30, under=0), args_for(Path(folder) / "props"))
        self.assertEqual(payload["verdict"], "escalate")
        self.assertIn("live-authoring.md", payload["escalate"]["how"])


class Textures(unittest.TestCase):
    def test_maps_are_packed_into_three_dds_and_the_source_is_left_alone(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            source = maps(Path(folder) / "downloads" / "geometry_textures")
            before = sorted(path.name for path in source.iterdir())
            files = Path(folder) / "out" / "files"
            files.mkdir(parents=True)
            written = fit_prop.pack_textures(source, Path(folder) / "out", files, "u_prop", 16, 1.0)
            self.assertEqual(sorted(written), ["diffuse", "normal", "specular"])
            for role in written:
                self.assertTrue((files / f"u_prop_{role}.dds").is_file())
            self.assertEqual(sorted(path.name for path in source.iterdir()), before)

    def test_the_maps_next_to_the_glb_are_found(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            maps(Path(folder) / "geometry_textures")
            self.assertEqual(fit_prop.find_textures(Path(folder) / "geometry.glb", None).name, "geometry_textures")
            with self.assertRaises(SystemExit):
                fit_prop.find_textures(Path(folder) / "missing" / "geometry.glb", None)


@unittest.skipUnless(BLENDER and BLENDER.exists(), "no supported Blender installed")
class FitInBlender(unittest.TestCase):
    def test_a_club_is_fitted_to_the_right_hand_and_bound_to_it(self) -> None:
        import test_deformation_checks as arms
        import test_measure_body as glb

        with tempfile.TemporaryDirectory() as folder:
            unit = Path(folder) / "unit"
            unit.mkdir()
            positions, triangles, bones = arms.two_arm_strip()
            arms.write_mesh(unit / "u.mesh", positions, triangles, bones)
            arms.write_anim(unit / "u_idle.anim", 6, lambda frame: {})
            prop = Path(folder) / "prop" / "geometry.glb"
            maps(prop.parent / "geometry_textures")
            # A club standing upright: a long thin box, as a provider prop sheet delivers it.
            glb.write_glb(prop, *glb.body((-0.03, 0.03, 0.0, 1.0, -0.03, 0.03), (-0.06, 0.06, 0.8, 1.0, -0.06, 0.06)))
            out = Path(folder) / "props"
            with redirect_stdout(io.StringIO()) as output:
                code = fit_prop.main([str(unit), "--prop", str(prop), "--bone", "HandR", "--length", "0.6", "--size", "16", "--step", "1", "--out", str(out)])
            payload = json.loads(output.getvalue().strip().splitlines()[-1])
            fitted = pdx_deform.load_mesh(out / "files" / "u.mesh")
            summary = pdx_binary.summarize_mesh(pdx_binary.read(out / "files" / "u.mesh"))
            report = json.loads((out / "fit_report.json").read_text(encoding="utf-8"))
        self.assertIn(code, (0, 1))
        self.assertEqual(payload["stage"], "props")
        self.assertGreater(len(fitted.positions), len(positions))
        self.assertEqual(summary.bones, [name for name, _parent, _position in arms.BONES])
        # Every new vertex follows the hand bone only.
        added = np.arange(len(positions), len(fitted.positions))
        hand = fitted.bones.index("HandR")
        self.assertTrue(np.all(fitted.joints[added, 0] == hand))
        self.assertEqual(report["frames_checked"], 6)


if __name__ == "__main__":
    unittest.main()
