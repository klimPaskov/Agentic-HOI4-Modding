"""The prop-fitting stage (fit_prop.py): its verdict, its texture packing, and the Blender fit on a small unit."""

from __future__ import annotations

import argparse
import io
import json
import math
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


def cylinder(radius, low, high, rings, sides):
    """A closed cylinder along Y (glTF up), wound outward: rings of vertices and two capped ends."""

    positions = [(radius * math.cos(2 * math.pi * s / sides), low + (high - low) * r / (rings - 1), radius * math.sin(2 * math.pi * s / sides)) for r in range(rings) for s in range(sides)]
    triangles = []
    for r in range(rings - 1):
        for s in range(sides):
            a, b = r * sides + s, r * sides + (s + 1) % sides
            c, d = a + sides, b + sides
            triangles += [(a, c, b), (b, c, d)]
    bottom, top = len(positions), len(positions) + 1
    positions += [(0.0, low, 0.0), (0.0, high, 0.0)]
    for s in range(sides):
        a, b = s, (s + 1) % sides
        triangles.append((bottom, a, b))
        triangles.append((top, (rings - 1) * sides + b, (rings - 1) * sides + a))
    return np.asarray(positions, dtype=np.float32), np.asarray(triangles, dtype=np.uint32)


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

    def test_a_blade_of_small_plates_is_kept_and_a_lone_fragment_dropped(self) -> None:
        # A smart-topology polearm: a shaft of many vertices, a blade of six small plates each far
        # smaller than the shaft, stacked 1 cm apart, and a neighbour's sliver half a metre away.
        import test_deformation_checks as arms
        import test_measure_body as glb

        positions, triangles = cylinder(0.03, 0.0, 1.0, rings=8, sides=8)
        plates = glb.body(*[(-0.05, 0.05, 1.01 + 0.04 * k, 1.04 + 0.04 * k, -0.01, 0.01) for k in range(6)], (-0.05, 0.05, -0.55, -0.5, -0.05, 0.05))
        offset = len(positions)
        positions = np.vstack([positions, plates[0]])
        triangles = np.vstack([triangles, plates[1] + offset])
        with tempfile.TemporaryDirectory() as folder:
            unit = Path(folder) / "unit"
            unit.mkdir()
            body, body_triangles, bones = arms.two_arm_strip()
            arms.write_mesh(unit / "u.mesh", body, body_triangles, bones)
            arms.write_anim(unit / "u_idle.anim", 4, lambda frame: {})
            prop = Path(folder) / "prop" / "geometry.glb"
            maps(prop.parent / "geometry_textures")
            glb.write_glb(prop, positions.astype(np.float32), triangles.astype(np.uint32))
            out = Path(folder) / "props"
            with redirect_stdout(io.StringIO()):
                fit_prop.main([str(unit), "--prop", str(prop), "--bone", "HandR", "--length", "0.6", "--size", "16", "--step", "1", "--out", str(out)])
            log = (out / "blender.log").read_text(encoding="utf-8", errors="replace")
        self.assertIn("FIT_PIECES 8 kept 7", log)

    def test_fitting_again_replaces_the_prop(self) -> None:
        import test_deformation_checks as arms
        import test_measure_body as glb

        with tempfile.TemporaryDirectory() as folder:
            unit = Path(folder) / "unit"
            unit.mkdir()
            positions, triangles, bones = arms.two_arm_strip()
            arms.write_mesh(unit / "u.mesh", positions, triangles, bones)
            arms.write_anim(unit / "u_idle.anim", 4, lambda frame: {})
            prop = Path(folder) / "prop" / "geometry.glb"
            maps(prop.parent / "geometry_textures")
            glb.write_glb(prop, *glb.body((-0.03, 0.03, 0.0, 1.0, -0.03, 0.03)))
            common = ["--prop", str(prop), "--bone", "HandR", "--size", "16", "--step", "2"]
            with redirect_stdout(io.StringIO()):
                fit_prop.main([str(unit), *common, "--out", str(Path(folder) / "first")])
                fit_prop.main([str(Path(folder) / "first" / "files"), *common, "--length", "0.4", "--out", str(Path(folder) / "second")])
            once = pdx_binary.summarize_mesh(pdx_binary.read(Path(folder) / "first" / "files" / "u.mesh"))
            twice = pdx_binary.summarize_mesh(pdx_binary.read(Path(folder) / "second" / "files" / "u.mesh"))
            report = json.loads((Path(folder) / "second" / "fit_report.json").read_text(encoding="utf-8"))
        self.assertEqual(len(twice.streams), len(once.streams))
        self.assertEqual(report["replaced_prop"], ["u_prop"])


if __name__ == "__main__":
    unittest.main()
