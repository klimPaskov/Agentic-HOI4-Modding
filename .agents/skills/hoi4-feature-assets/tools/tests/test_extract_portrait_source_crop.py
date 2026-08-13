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
	def test_bundled_yunet_model_is_present_and_hash_pinned(self) -> None:
		self.assertTrue(SOURCE_CROP.DEFAULT_MODEL_PATH.is_file())
		self.assertEqual(
			SOURCE_CROP.sha256_file(SOURCE_CROP.DEFAULT_MODEL_PATH),
			"ebafce4e3c118d6554634be5c27ab333b4c047a9a8c3faf1d7cf93101c22f0f0",
		)

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

	def test_automatic_package_preserves_source_and_writes_crop_resize_and_contract(self) -> None:
		with tempfile.TemporaryDirectory(dir=SOURCE_CROP.REPO_ROOT) as temporary:
			root = Path(temporary)
			master_path = root / "archival_master.png"
			output_path = root / "portrait_source_crop.png"
			master = Image.new("RGB", (400, 500), (40, 50, 60))
			master.save(master_path, format="PNG", optimize=False)
			master_bytes = master_path.read_bytes()

			metadata = SOURCE_CROP.process_portrait_source(
				master_path,
				output_path,
				detector=lambda _image: [(150, 80, 100, 110)],
			)

			source_copy = root / "portrait_original.png"
			processed = root / "portrait_156x210.png"
			provenance = root / "portrait.txt"
			self.assertEqual(source_copy.read_bytes(), master_bytes)
			with Image.open(output_path) as crop, Image.open(processed) as resized:
				self.assertEqual(crop.size, tuple(metadata["source_crop"]["dimensions"]))
				self.assertEqual(resized.size, (156, 210))
			self.assertEqual(metadata["source_copy"]["byte_identical_to_master"], True)
			self.assertTrue(metadata["equality"]["decoded_pixels_equal"])
			self.assertIn("subject_identity: [REQUIRED", provenance.read_text(encoding="utf-8"))
			self.assertIn("source_mode: source_placeholder", provenance.read_text(encoding="utf-8"))
			self.assertEqual(metadata["provenance"]["path"], SOURCE_CROP.normalized_path(provenance))

	def test_automatic_package_rejects_ambiguous_subjects_without_artifacts(self) -> None:
		with tempfile.TemporaryDirectory(dir=SOURCE_CROP.REPO_ROOT) as temporary:
			root = Path(temporary)
			master_path = root / "group.png"
			output_path = root / "group_crop.png"
			Image.new("RGB", (500, 500), (20, 30, 40)).save(master_path, format="PNG")
			with self.assertRaisesRegex(ValueError, "refusing to guess"):
				SOURCE_CROP.process_portrait_source(
					master_path,
					output_path,
					detector=lambda _image: [(50, 80, 90, 100), (320, 85, 90, 100)],
				)
			self.assertFalse(output_path.exists())
			self.assertFalse((root / "group.txt").exists())

	def test_automatic_package_requires_co_located_artifacts(self) -> None:
		with tempfile.TemporaryDirectory(dir=SOURCE_CROP.REPO_ROOT) as temporary:
			root = Path(temporary)
			master_path = root / "master.png"
			Image.new("RGB", (400, 500), (10, 20, 30)).save(master_path, format="PNG")
			with self.assertRaisesRegex(ValueError, "co-located"):
				SOURCE_CROP.process_portrait_source(
					master_path,
					root / "crop.png",
					processed_path=root / "nested" / "processed.png",
					detector=lambda _image: [(150, 80, 100, 110)],
				)

	def test_manual_crop_override_writes_the_same_complete_package_without_detector_claim(self) -> None:
		with tempfile.TemporaryDirectory(dir=SOURCE_CROP.REPO_ROOT) as temporary:
			root = Path(temporary)
			master_path = root / "master.jpg"
			output_path = root / "portrait_subject_source_crop.png"
			Image.new("RGB", (400, 500), (10, 20, 30)).save(master_path, format="JPEG", quality=100)
			metadata = SOURCE_CROP.process_portrait_source(
				master_path,
				output_path,
				crop_override=(40, 20, 360, 460),
			)
			self.assertEqual(metadata["mode"], "manual_crop_override")
			self.assertIsNone(metadata["detector"]["face_box_xywh"])
			self.assertIsNone(metadata["detector"]["subject_count"])
			self.assertTrue((root / "portrait_subject_original.jpg").is_file())
			self.assertTrue((root / "portrait_subject_156x210.png").is_file())
			self.assertTrue((root / "portrait_subject.txt").is_file())


if __name__ == "__main__":
	unittest.main()
