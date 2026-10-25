"""Unit tests for the bounded sprite QA helpers."""
from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("gfx_under_test", Path(__file__).with_name("gfx.py"))
gfx = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(gfx)

# Same lookup as `.tools/lib/game.py`, which this directory cannot import.
VANILLA = Path(os.environ.get("HOI4_GAME_DIR") or r"C:\Program Files (x86)\Steam\steamapps\common\Hearts of Iron IV") / "gfx" / "interface" / "counters"


class GfxHelpersTests(unittest.TestCase):
    def test_canonical_dds_round_trip_keeps_bgra_pixels_and_header(self):
        pixels = np.array([
            [[240, 10, 20, 255], [7, 80, 190, 37]],
            [[5, 6, 7, 0], [255, 255, 255, 128]],
        ], dtype=np.uint8)
        image = Image.fromarray(pixels, "RGBA")
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "roundtrip.dds"
            gfx.write_dds(image, output)
            raw = output.read_bytes()
            self.assertEqual(raw[:4], b"DDS ")
            self.assertEqual(struct.unpack_from("<I", raw, 4)[0], 124)
            self.assertEqual(struct.unpack_from("<II", raw, 12), (2, 2))
            self.assertEqual(len(raw), 128 + 2 * 2 * 4)
            self.assertEqual(np.asarray(gfx.strict_dds(output)).tobytes(), pixels.tobytes())
            self.assertEqual(np.asarray(gfx.load(output)).tobytes(), pixels.tobytes())

    def test_strict_dds_rejects_truncated_payload_and_moved_pixel_format(self):
        image = Image.new("RGBA", (2, 2), (11, 22, 33, 255))
        with tempfile.TemporaryDirectory() as directory:
            valid = Path(directory) / "valid.dds"
            gfx.write_dds(image, valid)
            truncated = Path(directory) / "truncated.dds"
            truncated.write_bytes(valid.read_bytes()[:-1])
            moved = Path(directory) / "moved.dds"
            raw = bytearray(valid.read_bytes())
            raw[76:80], raw[80:84] = raw[80:84], raw[76:80]
            moved.write_bytes(raw)
            for bad in (truncated, moved):
                with self.subTest(path=bad.name), self.assertRaises(ValueError):
                    gfx.strict_dds(bad)

    def test_defringe_removes_one_alpha_pixel_and_replaces_chroma_from_core(self):
        image = Image.new("RGBA", (9, 9), (0, 255, 0, 0))
        # Large uncontaminated region makes the intended nearest interior unambiguous.
        for y in range(2, 7):
            for x in range(2, 7):
                image.putpixel((x, y), (30, 80, 120, 255))
        image.putpixel((1, 4), (0, 255, 0, 255))
        image.putpixel((3, 4), (0, 255, 0, 180))
        repaired = gfx.defringe(image, erosion=1)
        self.assertEqual(repaired.getpixel((1, 4))[3], 0)
        self.assertEqual(repaired.getpixel((3, 4))[:3], (30, 80, 120))
        self.assertEqual(repaired.getpixel((3, 4))[3], 180)
        self.assertEqual(repaired.getpixel((5, 4))[3], 255)
        self.assertEqual(repaired.getpixel((0, 0))[3], 0)

    def test_vivid_green_opaque_interior_is_preserved_while_boundary_green_is_repaired(self):
        image = Image.new("RGBA", (15, 15), (0, 255, 0, 0))
        for y in range(2, 13):
            for x in range(2, 13):
                image.putpixel((x, y), (40, 90, 130, 255))
        for y in range(5, 10):
            for x in range(5, 10):
                image.putpixel((x, y), (15, 230, 20, 255))
        image.putpixel((2, 7), (15, 230, 20, 255))

        repaired = gfx.defringe(image, erosion=1)
        self.assertEqual(repaired.getpixel((7, 7)), (15, 230, 20, 255))
        self.assertEqual(repaired.getpixel((2, 7))[:3], (40, 90, 130))
        self.assertEqual(repaired.getpixel((2, 7))[3], 0)

    def test_explicit_spill_mask_recolours_only_selected_internal_green(self):
        image = Image.new("RGBA", (15, 15), (0, 255, 0, 0))
        for y in range(2, 13):
            for x in range(2, 13):
                image.putpixel((x, y), (40, 90, 130, 255))
        image.putpixel((6, 7), (15, 230, 20, 255))  # reviewed opaque spill
        image.putpixel((8, 7), (15, 230, 20, 255))  # adjacent legitimate green detail
        mask = np.zeros((15, 15), dtype=bool)
        mask[7, 6] = True

        repaired = gfx.defringe(image, erosion=1, spill_mask=mask)
        self.assertEqual(repaired.getpixel((6, 7)), (40, 90, 130, 255))
        self.assertEqual(repaired.getpixel((8, 7)), (15, 230, 20, 255))
        self.assertEqual(repaired.getchannel("A").tobytes(),
                         gfx.defringe(image, erosion=1).getchannel("A").tobytes())

    def test_explicit_spill_mask_rejects_wrong_canvas_shape(self):
        image = Image.new("RGBA", (9, 9), (0, 0, 0, 0))
        for y in range(2, 7):
            for x in range(2, 7):
                image.putpixel((x, y), (40, 40, 40, 255))
        with self.assertRaisesRegex(ValueError, "exact frame canvas"):
            gfx.defringe(image, spill_mask=np.zeros((8, 9), dtype=bool))

    def test_partial_alpha_core_keeps_its_rgb_but_one_pixel_erosion_can_lower_alpha(self):
        image = Image.new("RGBA", (9, 9), (0, 0, 0, 0))
        for y in range(2, 7):
            for x in range(2, 7):
                image.putpixel((x, y), (40, 40, 40, 245))
        image.putpixel((3, 3), (90, 90, 90, 240))
        image.putpixel((4, 4), (140, 140, 140, 250))

        repaired = gfx.defringe(image, erosion=1)
        # This point survives the alpha>=240 seed mask's one-pixel erosion.
        self.assertEqual(repaired.getpixel((4, 4))[:3], (140, 140, 140))
        # Alpha erosion is independent of the RGB-core preservation rule.
        self.assertEqual(repaired.getpixel((4, 4))[3], 240)

    def test_defringe_fails_closed_for_empty_or_fully_opaque_canvases(self):
        with self.assertRaisesRegex(ValueError, "Empty subject"):
            gfx.defringe(Image.new("RGBA", (7, 7), (1, 2, 3, 0)))
        with self.assertRaisesRegex(ValueError, "No transparent canvas"):
            gfx.defringe(Image.new("RGBA", (7, 7), (1, 2, 3, 255)))

    def test_frames_are_repaired_independently_without_cross_frame_rgb_bleed(self):
        sheet = Image.new("RGBA", (16, 8), (0, 0, 0, 0))
        for y in range(2, 6):
            for x in range(2, 6):
                sheet.putpixel((x, y), (220, 20, 20, 255))
            for x in range(10, 14):
                sheet.putpixel((x, y), (20, 20, 220, 255))
        left, right = gfx.frames(sheet, 2)
        repaired = [gfx.defringe(frame) for frame in (left, right)]
        self.assertTrue(all(repaired[0].getpixel((x, y))[2] < 100
                            for y in range(8) for x in range(8)
                            if repaired[0].getpixel((x, y))[3] > 0))
        self.assertTrue(all(repaired[1].getpixel((x, y))[0] < 100
                            for y in range(8) for x in range(8)
                            if repaired[1].getpixel((x, y))[3] > 0))

    def test_alpha_ghost_threshold_and_opaque_normal_image_are_explicit(self):
        ghost = Image.new("RGBA", (5, 5), (0, 0, 0, 0))
        ghost.putpixel((2, 2), (20, 30, 40, 100))
        normal = Image.new("RGBA", (5, 5), (20, 30, 40, 255))
        self.assertTrue(gfx.alpha_stats(ghost)["ghosted"])
        self.assertFalse(gfx.alpha_stats(normal)["ghosted"])
        self.assertEqual(gfx.alpha_stats(normal)["subject_alpha_mean"], 255)

    def test_size_profiles_report_wrong_canvas_and_three_pixel_margin(self):
        wrong = Image.new("RGBA", (209, 176), (0, 0, 0, 0))
        self.assertTrue(any("canvas" in finding for finding in gfx.size_check(wrong, "report")))
        tight = Image.new("RGBA", (52, 40), (0, 0, 0, 0))
        for y in range(2, 38):
            for x in range(2, 50):
                tight.putpixel((x, y), (120, 120, 120, 255))
        findings = gfx.size_check(tight, "category", margin=3)
        self.assertTrue(any("minimum 3" in finding for finding in findings))
        self.assertEqual(gfx.PROFILES["report"][:2], (210, 176))
        self.assertEqual(gfx.PROFILES["news"][:2], (397, 153))

    def test_output_refusal_does_not_modify_input_even_with_force(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source.png"
            original = Image.new("RGBA", (5, 5), (40, 80, 120, 255))
            original.save(source)
            before = source.read_bytes()
            result = subprocess.run(
                [sys.executable, str(Path(__file__).with_name("gfx.py")), "defringe",
                 str(source), "--root", str(root), "--out", str(root), "--force"],
                capture_output=True, text=True, check=False)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Input overwrite forbidden", result.stdout)
            self.assertEqual(source.read_bytes(), before)

    def test_non_force_output_install_preserves_competing_writer(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "review.png"
            competitor_bytes = b"created by competing worker"
            install = gfx.install_output

            def competitor_wins(scratch, path, overwrite):
                path.write_bytes(competitor_bytes)
                return install(scratch, path, overwrite)

            image = Image.new("RGBA", (4, 4), (20, 40, 60, 255))
            with patch.object(gfx, "install_output", side_effect=competitor_wins):
                with self.assertRaises(FileExistsError):
                    gfx.write_png(image, target, overwrite=False)
            self.assertEqual(target.read_bytes(), competitor_bytes)
            self.assertEqual(list(Path(directory).iterdir()), [target])

    def test_json_report_refuses_to_replace_a_selected_input(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source.png"
            Image.new("RGBA", (5, 5), (40, 80, 120, 255)).save(source)
            before = source.read_bytes()
            result = subprocess.run(
                [sys.executable, str(Path(__file__).with_name("gfx.py")), "alpha",
                 str(source), "--json", str(source)],
                capture_output=True, text=True, check=False)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(source.read_bytes(), before)

    def test_json_report_refuses_input_list_and_planned_output_collisions(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source.png"
            Image.new("RGBA", (9, 9), (40, 80, 120, 255)).save(source)
            manifest = root / "inputs.json"
            manifest.write_text('[{"path":"source.png","frames":1}]', encoding="utf-8")
            list_before = manifest.read_bytes()
            list_result = subprocess.run(
                [sys.executable, str(Path(__file__).with_name("gfx.py")), "alpha",
                 "--list", str(manifest), "--json", str(manifest)],
                capture_output=True, text=True, check=False)
            self.assertNotEqual(list_result.returncode, 0)
            self.assertEqual(manifest.read_bytes(), list_before)

            planned_png = root / "output" / "source.png"
            output_result = subprocess.run(
                [sys.executable, str(Path(__file__).with_name("gfx.py")), "defringe",
                 str(source), "--root", str(root), "--out", str(root / "output"),
                 "--json", str(planned_png)],
                capture_output=True, text=True, check=False)
            self.assertNotEqual(output_result.returncode, 0)
            self.assertFalse(planned_png.exists())

    def test_json_report_refuses_to_replace_explicit_spill_mask(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source.png"
            mask = root / "mask.png"
            Image.new("RGBA", (9, 9), (40, 40, 40, 255)).save(source)
            Image.new("L", (9, 9), 0).save(mask)
            before = mask.read_bytes()
            result = subprocess.run(
                [sys.executable, str(Path(__file__).with_name("gfx.py")), "defringe",
                 str(source), "--root", str(root), "--out", str(root / "output"),
                 "--spill-mask", str(mask), "--json", str(mask)],
                capture_output=True, text=True, check=False)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(mask.read_bytes(), before)

    def test_manifest_can_declare_mixed_frame_counts(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            single = root / "single.png"
            strip = root / "strip.png"
            Image.new("RGBA", (8, 8), (10, 20, 30, 255)).save(single)
            Image.new("RGBA", (16, 8), (10, 20, 30, 255)).save(strip)
            manifest = root / "inputs.json"
            manifest.write_text(json.dumps([
                {"path": str(single), "frames": 1},
                {"texture": str(strip), "frames": 2},
            ]), encoding="utf-8")
            report = root / "report.json"
            result = subprocess.run(
                [sys.executable, str(Path(__file__).with_name("gfx.py")), "alpha",
                 "--list", str(manifest), "--json", str(report)],
                capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            rows = json.loads(report.read_text(encoding="utf-8"))
            self.assertEqual([len(row["frames"]) for row in rows], [1, 2])


class InstalledVanillaCounterTests(unittest.TestCase):
    @unittest.skipUnless((VANILLA / "divisions_large" / "unit_infantry_icon.dds").is_file(),
                         "Installed vanilla counter DDS unavailable")
    def test_counter_cli_reports_both_frames_without_extra_frame_argument(self):
        source = VANILLA / "divisions_large" / "unit_infantry_icon.dds"
        with tempfile.TemporaryDirectory() as directory:
            report = Path(directory) / "counter.json"
            result = subprocess.run([sys.executable, "-B", str(Path(__file__).with_name("gfx.py")),
                                     "counter", str(source), "--surface", "large", "--reference", str(source),
                                     "--json", str(report)], capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(len(json.loads(report.read_text(encoding="utf-8"))[0]["frames"]), 2)

    @unittest.skipUnless((VANILLA / "divisions_large" / "unit_infantry_icon.dds").is_file()
                         and (VANILLA / "divisions_small" / "onmap_unit_infantry_icon.dds").is_file(),
                         "Installed vanilla counter DDS files unavailable")
    def test_exact_vanilla_reference_surfaces_are_valid_inputs_and_expose_threshold_baseline(self):
        large = gfx.load(VANILLA / "divisions_large" / "unit_infantry_icon.dds")
        small = gfx.load(VANILLA / "divisions_small" / "onmap_unit_infantry_icon.dds")
        self.assertEqual(large.size, (152, 42))
        self.assertEqual(small.size, (60, 12))
        # These are precise baselines: legacy normal frames have translucent pixels,
        # so a universal <200 subject-alpha rule would reject the vanilla templates.
        self.assertLess(gfx.alpha_stats(gfx.frames(large, 2)[0])["subject_alpha_mean"], 200)
        self.assertLess(gfx.alpha_stats(gfx.frames(small, 2)[0])["subject_alpha_mean"], 200)
        large_findings = gfx.counter_check(large, "large", large)
        small_findings = gfx.counter_check(small, "small", small)
        # The reference itself must not be presented as a defective candidate.
        self.assertEqual(large_findings, [])
        self.assertEqual(small_findings, [])
        self.assertEqual(gfx.size_check(large, "counter-large", 2), [])
        self.assertEqual(gfx.size_check(small, "counter-small", 2), [])

    @unittest.skipUnless((VANILLA / "divisions_large" / "unit_infantry_icon.dds").is_file(),
                         "Installed vanilla counter DDS unavailable")
    def test_counter_rejects_white_and_black_speckles_without_a_nato_field(self):
        reference = gfx.load(VANILLA / "divisions_large" / "unit_infantry_icon.dds")
        candidate = reference.copy()
        candidate.paste(Image.new("RGBA", (76, 42)), (76, 0))
        for y in range(4, 38, 4):
            for x in range(4, 72, 4):
                candidate.putpixel((76 + x, y), (255, 255, 255, 255) if (x + y) % 8 else (0, 0, 0, 255))
        findings = gfx.counter_check(candidate, "large", reference)
        self.assertTrue(any("coherent rectangular NATO field" in finding for finding in findings))


if __name__ == "__main__":
    unittest.main()
