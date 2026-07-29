from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image


TOOL_PATH = Path(__file__).resolve().parents[1] / "extract_portrait_source_crop.py"
SPEC = importlib.util.spec_from_file_location("extract_portrait_source_crop", TOOL_PATH)
if SPEC is None or SPEC.loader is None:
	raise RuntimeError(f"Unable to load source-crop module: {TOOL_PATH}")
SOURCE_CROP = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SOURCE_CROP)


class SourceCropTests(unittest.TestCase):
	def test_grayscale_jpeg_crop_is_exact_after_png_decode(self) -> None:
		with tempfile.TemporaryDirectory(dir=SOURCE_CROP.REPO_ROOT) as temporary:
			root = Path(temporary)
			master_path = root / "archival_master.jpg"
			output_path = root / "archival_crop.png"
			metadata_path = root / "archival_crop.json"
			master_pixels = [
				((x * 29) + (y * 17)) % 256
				for y in range(12)
				for x in range(16)
			]
			master = Image.new("L", (16, 12))
			master.putdata(master_pixels)
			master.save(master_path, format="JPEG", quality=100, subsampling=0)

			metadata = SOURCE_CROP.crop_source(
				master_path,
				output_path,
				metadata_path,
				(3, 2, 13, 10),
			)

			with Image.open(master_path) as decoded_master, Image.open(output_path) as output:
				expected = decoded_master.crop((3, 2, 13, 10)).convert("RGBA")
				actual = output.convert("RGBA")
				self.assertEqual(actual.size, expected.size)
				self.assertEqual(actual.tobytes(), expected.tobytes())
			self.assertEqual(metadata["decode"]["backend"], "Pillow")
			self.assertEqual(metadata["equality"]["decoded_pixels_equal"], True)
			self.assertEqual(metadata["crop"]["dimensions"], [10, 8])
			self.assertEqual(metadata["output"]["dimensions"], [10, 8])
			self.assertEqual(metadata["master"]["decode_mode"], "L")
			self.assertEqual(metadata["output"]["decode_mode"], "L")
			self.assertEqual(
				metadata["equality"]["master_crop_rgba_sha256"],
				metadata["equality"]["output_rgba_sha256"],
			)
			with metadata_path.open(encoding="utf-8") as handle:
				recorded = json.load(handle)
			self.assertEqual(recorded["normalized_command"]["schema"], SOURCE_CROP.COMMAND_SCHEMA)
			self.assertEqual(
				recorded["output"]["file_sha256"],
				SOURCE_CROP.sha256_file(output_path),
			)

	def test_invalid_bounds_reject_negative_outside_and_empty_rectangles(self) -> None:
		invalid_crops = ((-1, 0, 4, 4), (0, 0, 11, 4), (4, 4, 4, 5))
		for crop in invalid_crops:
			with self.subTest(crop=crop):
				with self.assertRaises(ValueError):
					SOURCE_CROP.validate_crop_box((10, 10), crop)

	def test_existing_artifacts_require_explicit_force(self) -> None:
		with tempfile.TemporaryDirectory(dir=SOURCE_CROP.REPO_ROOT) as temporary:
			root = Path(temporary)
			master_path = root / "master.jpg"
			output_path = root / "crop.png"
			metadata_path = root / "crop.json"
			Image.new("RGB", (4, 4), (10, 20, 30)).save(master_path, format="JPEG")
			output_path.write_bytes(b"existing")
			with self.assertRaises(FileExistsError):
				SOURCE_CROP.crop_source(
					master_path,
					output_path,
					metadata_path,
					(0, 0, 2, 2),
				)


if __name__ == "__main__":
	unittest.main()
