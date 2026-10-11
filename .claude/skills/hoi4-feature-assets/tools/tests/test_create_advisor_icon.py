from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw


TOOL_PATH = Path(__file__).resolve().parents[1] / "create_advisor_icon.py"
SPEC = importlib.util.spec_from_file_location("create_advisor_icon", TOOL_PATH)
if SPEC is None or SPEC.loader is None:
	raise RuntimeError(f"Unable to load advisor compositor: {TOOL_PATH}")
ADVISOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ADVISOR)


class AdvisorIconTests(unittest.TestCase):
	def setUp(self) -> None:
		self.source = Image.new("RGBA", (156, 210), (0, 0, 0, 255))
		draw = ImageDraw.Draw(self.source)
		draw.rectangle((0, 0, 77, 104), fill=(255, 0, 0, 255))
		draw.rectangle((78, 0, 155, 104), fill=(0, 255, 0, 255))
		draw.rectangle((0, 105, 77, 209), fill=(0, 0, 255, 255))
		draw.rectangle((78, 105, 155, 209), fill=(255, 255, 0, 255))

	def make_template(self) -> Image.Image:
		template = Image.new("RGBA", ADVISOR.CARD_SIZE, (0, 0, 0, 0))
		draw = ImageDraw.Draw(template)
		draw.rectangle((5, 5, 45, 61), fill=(17, 23, 31, 255))
		draw.rectangle((10, 10, 38, 53), fill=(0, 0, 0, 0))
		draw.rectangle((30, 24, 64, 66), fill=(211, 187, 139, 255))
		return template

	def test_complete_source_is_preserved_before_uniform_fit(self) -> None:
		prepared = ADVISOR.prepare_portrait(self.source, 0.0)
		self.assertEqual(prepared.size, self.source.size)
		self.assertEqual(prepared.tobytes(), self.source.tobytes())

	def test_cover_resize_preserves_aspect_without_stretch_or_padding(self) -> None:
		opening_size = (30.477406, 45.094508)
		geometry = ADVISOR.calculate_covering_portrait_geometry(
			self.source.size,
			opening_size,
		)
		self.assertAlmostEqual(
			geometry["content_size"][0] / geometry["content_size"][1],
			self.source.width / self.source.height,
			places=6,
		)
		self.assertAlmostEqual(geometry["content_size"][1], opening_size[1], places=6)
		self.assertGreater(geometry["content_size"][0], opening_size[0])
		self.assertGreater(geometry["frame_clip"][0], 0.0)
		self.assertGreater(geometry["frame_clip"][2], 0.0)
		self.assertEqual(geometry["frame_clip"][1], 0.0)
		self.assertEqual(geometry["frame_clip"][3], 0.0)
		self.assertNotIn("padding", geometry)

	def test_template_is_the_final_top_layer(self) -> None:
		template = self.make_template()
		card = ADVISOR.compose(
			self.source,
			template,
			ADVISOR.TEMPLATE_OPENING_CENTER,
			(33.0, 46.0),
			(-1.0, -1.0),
			-6.0,
			0.0,
		)
		self.assertEqual(card.size, ADVISOR.CARD_SIZE)
		card_pixels = list(card.get_flattened_data() if hasattr(card, "get_flattened_data") else card.getdata())
		template_pixels = list(template.get_flattened_data() if hasattr(template, "get_flattened_data") else template.getdata())
		for index, pixel in enumerate(template_pixels):
			if pixel[3] == 255:
				self.assertEqual(card_pixels[index], pixel)

	def test_portrait_is_clipped_to_the_safe_under_frame_region(self) -> None:
		template = self.make_template()
		card = ADVISOR.compose(
			self.source,
			template,
			ADVISOR.TEMPLATE_OPENING_CENTER,
			(65.0, 67.0),
			(0.0, 0.0),
			-5.0,
			0.0,
		)
		self.assertEqual(card.getpixel((0, 0))[3], 0)
		self.assertGreater(card.getpixel((20, 20))[3], 0)

	def test_canonical_bleed_mask_stays_beneath_nontransparent_frame_pixels(self) -> None:
		template = ADVISOR.load_template(ADVISOR.DEFAULT_TEMPLATE)
		opening_mask = ADVISOR.create_opening_mask(template)
		bleed_mask = ADVISOR.create_portrait_bleed_mask(template)
		template_alpha = template.getchannel("A")
		self.assertGreater(
			sum(1 for value in bleed_mask.getdata() if value),
			sum(1 for value in opening_mask.getdata() if value),
		)
		for opening, bleed, alpha in zip(
			opening_mask.getdata(),
			bleed_mask.getdata(),
			template_alpha.getdata(),
		):
			if bleed and not opening:
				self.assertGreater(alpha, 0)

	def test_canonical_template_opening_mask_is_enclosed(self) -> None:
		template = ADVISOR.load_template(ADVISOR.DEFAULT_TEMPLATE)
		mask = ADVISOR.create_opening_mask(template)
		self.assertEqual(mask.getbbox(), (8, 8, 40, 55))
		for x in range(mask.width):
			self.assertEqual(mask.getpixel((x, 0)), 0)
			self.assertEqual(mask.getpixel((x, mask.height - 1)), 0)
		for y in range(mask.height):
			self.assertEqual(mask.getpixel((0, y)), 0)
			self.assertEqual(mask.getpixel((mask.width - 1, y)), 0)

	def test_cover_fills_every_canonical_opening_pixel(self) -> None:
		template = ADVISOR.load_template(ADVISOR.DEFAULT_TEMPLATE)
		geometry = ADVISOR.measure_opening_geometry(template)
		card = ADVISOR.compose(
			self.source,
			template,
			geometry["center"],
			geometry["size"],
			(0.0, 0.0),
			geometry["rotation"],
			0.0,
		)
		mask = ADVISOR.create_opening_mask(template)
		for y in range(mask.height):
			for x in range(mask.width):
				if mask.getpixel((x, y)):
					self.assertGreater(card.getpixel((x, y))[3], 0)

	def test_canonical_composite_has_no_opening_seam_or_exterior_spill(self) -> None:
		template = ADVISOR.load_template(ADVISOR.DEFAULT_TEMPLATE)
		geometry = ADVISOR.measure_opening_geometry(template)
		card = ADVISOR.compose(
			self.source,
			template,
			geometry["center"],
			geometry["size"],
			(0.0, 0.0),
			geometry["rotation"],
			0.0,
		)
		self.assertEqual(
			ADVISOR.audit_portrait_alpha_coverage(card, template),
			{
				"opening_alpha_gap_pixels": 0,
				"inner_edge_alpha_gap_pixels": 0,
				"exterior_alpha_leak_pixels": 0,
			},
		)

	def test_canonical_opening_geometry_is_measured_from_the_frame(self) -> None:
		template = ADVISOR.load_template(ADVISOR.DEFAULT_TEMPLATE)
		geometry = ADVISOR.measure_opening_geometry(template)
		self.assertAlmostEqual(geometry["center"][0], 24.7615, places=2)
		self.assertAlmostEqual(geometry["center"][1], 30.6451, places=2)
		self.assertAlmostEqual(geometry["size"][0], 30.4774, places=2)
		self.assertAlmostEqual(geometry["size"][1], 45.0945, places=2)
		self.assertAlmostEqual(geometry["rotation"], -4.76, places=2)

	def test_opening_fill_plane_gate_rejects_oversizing(self) -> None:
		template = ADVISOR.load_template(ADVISOR.DEFAULT_TEMPLATE)
		geometry = ADVISOR.measure_opening_geometry(template)
		center = geometry["center"]
		rotation = geometry["rotation"]
		with self.assertRaisesRegex(ValueError, "opening-fill plane must remain inside"):
			ADVISOR.validate_fit_to_opening(
				(43.0, 56.0),
				center,
				rotation,
				geometry,
			)
		bounds = ADVISOR.validate_fit_to_opening(
			(29.0, 39.0),
			center,
			rotation,
			geometry,
		)
		self.assertAlmostEqual(bounds[0], -14.5)
		self.assertAlmostEqual(bounds[2], 14.5)

	def test_size_rotation_and_center_must_align_with_measured_opening(self) -> None:
		template = ADVISOR.load_template(ADVISOR.DEFAULT_TEMPLATE)
		geometry = ADVISOR.measure_opening_geometry(template)
		ADVISOR.validate_opening_alignment(
			geometry["size"],
			(0.0, 0.0),
			geometry["rotation"],
			geometry,
		)
		with self.assertRaisesRegex(ValueError, "must align with the measured dossier opening"):
			ADVISOR.validate_opening_alignment(geometry["size"], (0.0, 0.0), -6.0, geometry)
		with self.assertRaisesRegex(ValueError, "center must remain aligned"):
			ADVISOR.validate_opening_alignment(
				geometry["size"],
				(0.01, 0.0),
				geometry["rotation"],
				geometry,
			)
		with self.assertRaisesRegex(ValueError, "must resize the complete image plane"):
			ADVISOR.validate_opening_alignment(
				(29.0, 39.0),
				(0.0, 0.0),
				geometry["rotation"],
				geometry,
			)

	def test_neutral_rotation_requires_explicit_review_exception(self) -> None:
		with self.assertRaisesRegex(ValueError, "explicit visible rotation"):
			ADVISOR.validate_transform((44.0, 57.0), (-2.0, 3.0), 0.0)
		ADVISOR.validate_transform(
			(44.0, 57.0),
			(-2.0, 3.0),
			0.0,
			allow_zero_rotation=True,
		)

	def test_rotation_and_offset_change_the_portrait_pixels(self) -> None:
		portrait = ADVISOR.prepare_portrait(self.source, 0.0)
		first = ADVISOR.render_portrait_layer(
			portrait,
			(42.0, 42.0 * 210.0 / 156.0),
			(23.0, 34.5),
			-7.0,
		)
		second = ADVISOR.render_portrait_layer(
			portrait,
			(48.0, 48.0 * 210.0 / 156.0),
			(27.0, 31.0),
			5.0,
		)
		self.assertNotEqual(first.tobytes(), second.tobytes())

	def test_portrait_renderer_rejects_anisotropic_stretch(self) -> None:
		portrait = ADVISOR.prepare_portrait(self.source, 0.0)
		with self.assertRaisesRegex(ValueError, "one uniform scale factor"):
			ADVISOR.render_portrait_layer(
				portrait,
				(42.0, 55.0),
				(23.0, 34.5),
				-7.0,
			)

	def test_selected_transform_must_appear_in_placement_study(self) -> None:
		self.assertTrue(
			ADVISOR.transform_matches_candidate(
				(42.0, 55.0),
				(-2.0, 3.0),
				-7.0,
				(42.0, 55.0, -2.0, 3.0, -7.0),
			)
		)

	def test_placement_study_and_metadata_record_the_selected_transform(self) -> None:
		with tempfile.TemporaryDirectory() as temporary:
			root = Path(temporary)
			source_path = root / "source.png"
			template_path = ADVISOR.DEFAULT_TEMPLATE
			preview_path = root / "preview.png"
			runtime_path = root / "runtime.dds"
			study_path = root / "study.png"
			alignment_path = root / "alignment.png"
			metadata_path = root / "metadata.json"
			self.source.save(source_path)
			template = ADVISOR.load_template(template_path)
			geometry = ADVISOR.measure_opening_geometry(template)
			rotation = geometry["rotation"]
			candidates = [
				(*geometry["size"], 0.0, 0.0, rotation),
			]
			card = ADVISOR.compose(
				self.source,
				template,
				geometry["center"],
				geometry["size"],
				(0.0, 0.0),
				rotation,
				0.18,
			)
			card.save(preview_path)
			ADVISOR.write_bgra_dds(card, runtime_path)
			portrait_center = geometry["center"]
			ADVISOR.write_alignment_preview(
				card,
				geometry,
				geometry["size"],
				portrait_center,
				rotation,
				alignment_path,
			)
			ADVISOR.write_placement_study(
				self.source,
				template,
				geometry["center"],
				candidates,
				0.18,
				study_path,
			)
			ADVISOR.write_metadata(
				metadata_path,
				source_path,
				self.source.size,
				template_path,
				preview_path,
				runtime_path,
				alignment_path,
				geometry["center"],
				geometry["size"],
				(0.0, 0.0),
				rotation,
				0.18,
				study_path,
				candidates,
				False,
			)
			payload = json.loads(metadata_path.read_text(encoding="utf-8"))
			self.assertEqual(payload["source"]["native_output_canvas"], [65, 67])
			self.assertEqual(payload["selected_transform"]["rotation_degrees"], rotation)
			self.assertEqual(payload["selected_transform"]["portrait_size"], list(geometry["size"]))
			self.assertEqual(payload["selected_transform"]["rotation_alignment_error_degrees"], 0.0)
			self.assertIn("fit_to_opening", payload["selected_transform"])
			self.assertEqual(
				payload["selected_transform"]["complete_image_resize"]["mode"],
				"aspect_preserving_cover_with_under_frame_bleed",
			)
			self.assertEqual(
				payload["selected_transform"]["fit_to_opening"]["under_frame_bleed_pixels"],
				ADVISOR.UNDER_FRAME_BLEED_PIXELS,
			)
			self.assertEqual(
				payload["selected_transform"]["fit_to_opening"]["alpha_coverage"],
				{
					"opening_alpha_gap_pixels": 0,
					"inner_edge_alpha_gap_pixels": 0,
					"exterior_alpha_leak_pixels": 0,
				},
			)
			self.assertFalse(payload["selected_transform"]["complete_image_resize"]["source_pre_crop"])
			self.assertTrue(payload["selected_transform"]["complete_image_resize"]["frame_clip"])
			self.assertFalse(payload["selected_transform"]["complete_image_resize"]["stretch"])
			self.assertNotIn(
				"source_derived_padding",
				payload["selected_transform"]["complete_image_resize"],
			)
			self.assertEqual(len(payload["placement_candidates"]), 1)
			self.assertTrue(study_path.exists())
			self.assertTrue(alignment_path.exists())
		self.assertFalse(
			ADVISOR.transform_matches_candidate(
				(42.0, 55.0),
				(-2.0, 3.0),
				-7.0,
				(42.0, 55.0, -2.0, 3.0, 0.0),
			)
		)

	def test_dds_round_trip_matches_composite(self) -> None:
		image = Image.new("RGBA", ADVISOR.CARD_SIZE, (41, 83, 127, 191))
		with tempfile.TemporaryDirectory() as temporary:
			output = Path(temporary) / "advisor.dds"
			ADVISOR.write_bgra_dds(image, output)
			reopened = Image.open(output).convert("RGBA")
			self.assertEqual(reopened.tobytes(), image.tobytes())
			self.assertEqual(
				output.stat().st_size,
				128 + ADVISOR.CARD_SIZE[0] * ADVISOR.CARD_SIZE[1] * 4,
			)


if __name__ == "__main__":
	unittest.main()
