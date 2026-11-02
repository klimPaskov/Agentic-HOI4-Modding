"""Tests for the vanilla reference shelf check, the family list and the 40 profile rows.

The shelf check (`.tools/audits/audit_shelf.py`) must pass on this repository and must catch each kind of drift on
a small fixture shelf. The profile tests prove that `gfx.py` still loads the 40 rows and that its focus, decision and
idea checks fire for a mod that uses the package's `profiles.json`.
Run from the mod root: `python -B .tools/tests/test_shelf.py`.
"""

import hashlib
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image

TOOLS = Path(__file__).resolve().parents[1]
ROOT = TOOLS.parent


def load(name, path):
	spec = importlib.util.spec_from_file_location(name, path)
	module = importlib.util.module_from_spec(spec)
	spec.loader.exec_module(module)
	return module


audit = load("audit_shelf_under_test", TOOLS / "audits" / "audit_shelf.py")
gfx = load("gfx_shelf_under_test", TOOLS / "gfx" / "gfx.py")
IDS = json.loads((TOOLS / "gfx" / "family_ids.json").read_text(encoding="utf-8"))
EXPECTED_IDS = (
	"focus idea_spirit idea_concern officer_corps_spirit decision decision_category_icon state_modifier special_project_icon raid "
	"mio_department mio_trait mio_policy bop_side medal agency_upgrade operation_icon commander_trait personal_trait doctrine "
	"report_event news_event decision_category_picture operation_picture technology achievement "
	"leader_portrait commander_portrait operative_portrait scientist_portrait advisor_card flag "
	"counter_large counter_small division_emblem building faction_logo agency_logo modifier_stat_icon gui_texture super_event").split()


def png(width, height, background=(0, 0, 0, 0), empty=False):
	image = Image.new("RGBA", (width, height), background)
	if not empty:
		for x in range(width // 4, width * 3 // 4):
			for y in range(height // 4, height * 3 // 4):
				image.putpixel((x, y), (200, 160, 90, 255))
	buffer = io.BytesIO()
	image.save(buffer, format="PNG")
	return buffer.getvalue()


class RepositoryState(unittest.TestCase):
	def test_the_shelf_and_the_family_ids_have_no_findings(self):
		self.assertEqual([f"{f.path}: {f.rule} {f.message}" for f in audit.run_checks(ROOT)], [])

	def test_the_family_list_is_the_forty_ids(self):
		self.assertEqual(IDS["families"], EXPECTED_IDS)

	def test_profiles_have_one_row_per_family_and_gfx_loads_them(self):
		rows = list(gfx.PROFILE_DATA)
		mapped = [IDS["profile_row_aliases"].get(name, name) for name in rows]
		self.assertEqual(sorted(mapped), sorted(EXPECTED_IDS))
		for name, profile in gfx.PROFILE_DATA.items():
			self.assertTrue(profile["source"], name)
			self.assertIn(name, gfx.PROFILES)
		# The five rows gfx.py always had keep their keys and geometry.
		self.assertEqual(gfx.PROFILES["report"][:2], (210, 176))
		self.assertEqual(gfx.PROFILES["counter-large"][:2], (76, 42))
		for name in ("focus", "decision", "idea"):
			self.assertIn(gfx.PROFILE_DATA[name]["off_size_level"], ("error", "warning"), name)

	def test_vanilla_values(self):
		data = gfx.PROFILE_DATA
		self.assertEqual(data["focus"]["canvas"], [100, 88])
		self.assertEqual(data["idea"]["canvas"], [60, 68])
		self.assertEqual(data["idea_concern"]["canvas"], [64, 64])
		self.assertEqual(data["advisor_card"]["canvas"], [65, 67])
		self.assertEqual(data["decision"]["canvas"], [33, 32])
		self.assertEqual(data["agency_logo"]["frames"], 2)
		self.assertEqual(data["gui_texture"]["canvas"], [0, 0])


class KitModFamilyChecks(unittest.TestCase):
	"""The focus, decision and idea checks of gfx.py fire on a mod that has only the package's rows."""

	def test_checks_fire_with_the_package_rows(self):
		focus, decision, idea = (tuple(gfx.PROFILE_DATA[name]["canvas"]) for name in ("focus", "decision", "idea"))
		folder = tempfile.TemporaryDirectory()
		self.addCleanup(folder.cleanup)
		root = Path(folder.name)

		def add(relative, data):
			path = root / relative
			path.parent.mkdir(parents=True, exist_ok=True)
			path.write_bytes(data if isinstance(data, bytes) else data.encode("utf-8"))

		add("common/national_focus/tree.txt", "focus_tree = {\n\tfocus = { id = good icon = GFX_focus_good }\n\tfocus = { id = odd icon = GFX_focus_odd }\n}\n")
		add("common/decisions/test.txt", "category = {\n\tbig_decision = { icon = big }\n}\n")
		add("common/ideas/test.txt", "ideas = {\n\tcountry = {\n\t\tspirit = { picture = spirit }\n\t\tconcern = { picture = concern }\n\t}\n}\n")
		sprites = {"GFX_focus_good": "goals/good", "GFX_focus_odd": "goals/odd", "GFX_decision_big": "decisions/big",
			"GFX_idea_spirit": "ideas/spirit", "GFX_idea_concern": "ideas/concern"}
		add("interface/test.gfx", "spriteTypes = {\n" + "".join(
			f'\tspriteType = {{ name = "{name}" texturefile = "gfx/interface/{path}.png" }}\n' for name, path in sprites.items()) + "}\n")
		add("gfx/interface/goals/good.png", png(*focus))
		add("gfx/interface/goals/odd.png", png(94, 86))
		add("gfx/interface/decisions/big.png", png(60, 60))
		add("gfx/interface/ideas/spirit.png", png(*idea))
		add("gfx/interface/ideas/concern.png", png(64, 64))
		found = gfx.check_families(root, None, root / "no_vanilla")
		self.assertEqual(sorted((f.rule, f.level, f.path.split("/")[-1]) for f in found), [
			("GFX-DECISION-SIZE", "warning", "big.png"),
			("GFX-FOCUS-SIZE", "error", "odd.png"),
		])
		self.assertEqual(decision, (33, 32))


class ShelfDrift(unittest.TestCase):
	"""A fixture shelf with two families; every kind of drift is reported once."""

	def setUp(self):
		folder = tempfile.TemporaryDirectory()
		self.addCleanup(folder.cleanup)
		self.root = Path(folder.name)
		shelf = self.root / audit.SHELF_DIR
		self.files = {}
		families = []
		for fid, shelf_folder, count in (("focus", "icons/national_focus", 2), ("flag", "flags", 1)):
			selected = []
			for index in range(count):
				name = f"a{index}.png"
				relative = name if fid != "flag" else f"normal/{name}"
				data = png(8 + index, 8)
				path = shelf / shelf_folder / relative
				path.parent.mkdir(parents=True, exist_ok=True)
				path.write_bytes(data)
				(path.parent / "contact_sheet.png").write_bytes(png(4, 4))
				selected.append({"file": relative, "png_sha256": hashlib.sha256(data).hexdigest(), "source_sha256": "0" * 64, "source_path": "gfx/x.dds",
					"source_root": "base", "width": 8, "height": 8, "frames": ["1"], "sprites": ["GFX_x"]})
			families.append({"id": fid, "shelf_folder": shelf_folder, "dominant_canvas": "8x8", "frames": {"1": count}, "selected_count": count,
				"candidate_count": 9, "selected": selected, "source_dirs": ["gfx"], "skipped": {}, "notes": None})
		self.catalog = {"game_version": "test", "game_raw_version": "1", "hoi4_exe_mtime": "x", "roots": ["base"], "generated": "x", "seed": 0,
			"tool_versions": {"python": "3", "pillow": "1", "numpy": "1"}, "method": "m", "families": families}
		self.kept = {"groups": []}
		self.write_json(audit.CATALOG_FILE, self.catalog)
		self.write_json(audit.KEPT_FILE, self.kept)
		self.write_json(audit.BUILDER_INPUT, {"families": [{"id": "focus"}, {"id": "flag"}]})
		self.write_json(audit.FAMILY_IDS_FILE, {"expected_count": 2, "families": ["focus", "flag"], "profile_row_aliases": {}, "shelf_family_aliases": {}, "families_without_shelf": {}})
		self.write_json(audit.PROFILES_FILE, {"profiles": {"focus": {}, "flag": {}}})
		for named in ("flags/medium", "flags/small", "interface/vanilla"):  # folders the generated CATALOG.md names
			(shelf / named).mkdir(parents=True, exist_ok=True)
		(shelf / "flags" / "contact_sheet.png").write_bytes(png(4, 4))
		(shelf / "README.md").write_text("The `icons/national_focus/` folder.\n", encoding="utf-8")
		audit.write_docs(self.root)

	def write_json(self, relative, data):
		path = self.root / relative
		path.parent.mkdir(parents=True, exist_ok=True)
		path.write_text(json.dumps(data), encoding="utf-8")

	def rules(self):
		return sorted({f.rule for f in audit.run_checks(self.root)})

	def test_clean_fixture_passes(self):
		self.assertEqual(audit.run_checks(self.root), [])

	def test_changed_png_is_a_hash_error(self):
		(self.root / audit.SHELF_DIR / "icons/national_focus/a0.png").write_bytes(png(8, 8, background=(1, 1, 1, 255)))
		self.assertEqual(self.rules(), ["SHELF-HASH"])

	def test_missing_png_is_reported(self):
		(self.root / audit.SHELF_DIR / "icons/national_focus/a1.png").unlink()
		self.assertIn("SHELF-MISSING", self.rules())
		self.assertIn("SHELF-COUNT", self.rules())

	def test_extra_png_is_reported(self):
		(self.root / audit.SHELF_DIR / "icons/national_focus/stray.png").write_bytes(png(8, 8))
		self.assertEqual(self.rules(), ["SHELF-COUNT", "SHELF-EXTRA"])

	def test_missing_contact_sheet_is_reported(self):
		(self.root / audit.SHELF_DIR / "flags/normal/contact_sheet.png").unlink()
		self.assertEqual(self.rules(), ["SHELF-CONTACT-SHEET"])

	def test_stale_document_is_reported(self):
		path = self.root / audit.SHELF_DIR / "CATALOG.md"
		path.write_text(path.read_text(encoding="utf-8") + "extra\n", encoding="utf-8")
		self.assertEqual(self.rules(), ["SHELF-DOC-STALE"])

	def test_readme_naming_a_missing_folder_is_reported(self):
		(self.root / audit.SHELF_DIR / "README.md").write_text("The `event_art/super_event/` folder.\n", encoding="utf-8")
		self.assertEqual(self.rules(), ["SHELF-DOC-FOLDER"])

	def test_family_list_drift_is_reported(self):
		self.write_json(audit.PROFILES_FILE, {"profiles": {"focus": {}, "flag": {}, "texticon": {}}})
		self.assertEqual(self.rules(), ["FAMILY-IDS"])
		self.write_json(audit.PROFILES_FILE, {"profiles": {"focus": {}}})
		self.assertEqual(self.rules(), ["FAMILY-IDS"])
		self.write_json(audit.PROFILES_FILE, {"profiles": {"focus": {}, "flag": {}}})
		self.write_json(audit.BUILDER_INPUT, {"families": [{"id": "flag"}, {"id": "focus"}]})
		self.assertEqual(self.rules(), ["FAMILY-IDS"])

	def test_a_mod_without_the_catalog_has_nothing_to_check(self):
		with tempfile.TemporaryDirectory() as empty:
			self.assertEqual(audit.run_checks(Path(empty)), [])


if __name__ == "__main__":
	unittest.main()
