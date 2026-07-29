from __future__ import annotations

import importlib.util
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

	def test_complete_source_is_resized_before_transform(self) -> None:
		prepared = ADVISOR.prepare_portrait(self.source, 0.0)
		expected = self.source.resize(ADVISOR.CARD_SIZE, Image.Resampling.LANCZOS)
		self.assertEqual(prepared.size, ADVISOR.CARD_SIZE)
		self.assertEqual(prepared.tobytes(), expected.tobytes())

	def test_template_is_the_final_top_layer(self) -> None:
		template = Image.new("RGBA", ADVISOR.CARD_SIZE, (0, 0, 0, 0))
		draw = ImageDraw.Draw(template)
		draw.rectangle((0, 0, 64, 6), fill=(17, 23, 31, 255))
		draw.rectangle((30, 24, 64, 66), fill=(211, 187, 139, 255))
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
		card_pixels = list(card.getdata())
		template_pixels = list(template.getdata())
		for index, pixel in enumerate(template_pixels):
			if pixel[3] == 255:
				self.assertEqual(card_pixels[index], pixel)

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
