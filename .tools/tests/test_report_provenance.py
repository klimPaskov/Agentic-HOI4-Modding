"""End-to-end test of report-image provenance (plan check B7) in a temporary mod tree.

The report processor records a card, the canonical writer converts it to DDS, and `gfx.py reports`
must accept it, then catch changed runtime pixels and a changed recorded recipe.
Run from the mod root: `python -B .tools/tests/test_report_provenance.py`.
"""

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from PIL import Image

TOOLS = Path(__file__).resolve().parents[1]
ROOT = TOOLS.parent


def load(name, path):
	spec = importlib.util.spec_from_file_location(name, path)
	module = importlib.util.module_from_spec(spec)
	spec.loader.exec_module(module)
	return module


gfx = load("gfx_reports_under_test", TOOLS / "gfx" / "gfx.py")
PROCESSOR = gfx.REPORT_PROCESSOR
RUNTIME = "gfx/event_pictures/test_report.dds"


class ReportProvenance(unittest.TestCase):
	def setUp(self):
		folder = tempfile.TemporaryDirectory()
		self.addCleanup(folder.cleanup)
		self.root = Path(folder.name)
		self.registry = self.root / "provenance.json"
		self.source = self.root / "source.png"
		image = Image.new("RGB", (300, 220))
		for x in range(300):
			for y in range(0, 220, 10):
				image.putpixel((x, y), (x % 256, y, 90))
		image.save(self.source)
		processed = self.root / "processed.png"
		processor = load("report_processor_cli", PROCESSOR)
		with mock.patch.object(sys, "argv", ["process", str(self.source), str(processed), "--runtime", RUNTIME,
				"--provenance", str(self.registry)]):
			processor.main()
		self.runtime = self.root / RUNTIME
		self.runtime.parent.mkdir(parents=True)
		with Image.open(processed) as card:
			gfx.write_dds(card.convert("RGBA"), self.runtime)

	def rules(self):
		with mock.patch.object(gfx, "REPORT_PROVENANCE", self.registry):
			return sorted(f.rule for f in gfx.check_reports(self.root, None))

	def test_recorded_card_passes_and_reruns_identically(self):
		record = json.loads(self.registry.read_text(encoding="utf-8"))["records"][RUNTIME]
		self.assertEqual(record["arguments"]["canvas_size"], [210, 176])
		self.assertEqual(self.rules(), [])

	def test_changed_runtime_pixels_are_an_error(self):
		with Image.open(self.runtime) as card:
			changed = card.convert("RGBA")
		changed.putpixel((105, 88), (255, 0, 0, 255))
		self.runtime.unlink()
		gfx.write_dds(changed, self.runtime)
		self.assertEqual(self.rules(), ["GFX-REPORT-PROVENANCE-MISMATCH"])

	def test_changed_recipe_is_an_error(self):
		data = json.loads(self.registry.read_text(encoding="utf-8"))
		data["records"][RUNTIME]["arguments"]["seed"] += 1
		self.registry.write_text(json.dumps(data), encoding="utf-8")
		self.assertEqual(self.rules(), ["GFX-REPORT-RECIPE-MISMATCH"])

	def test_unrecorded_card_is_a_warning_and_stale_record_too(self):
		data = json.loads(self.registry.read_text(encoding="utf-8"))
		data["records"]["gfx/event_pictures/missing.dds"] = data["records"].pop(RUNTIME)
		self.registry.write_text(json.dumps(data), encoding="utf-8")
		self.assertEqual(self.rules(), ["GFX-REPORT-NO-PROVENANCE", "GFX-REPORT-STALE-PROVENANCE"])


if __name__ == "__main__":
	unittest.main()
