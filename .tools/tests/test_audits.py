"""Fixture tests for the localisation and asset-wiring audits in `.tools/audits/`.

`fixtures/audits/mod/` is a tiny mod that both audits accept without an error, and
`fixtures/audits/game/` stands in for the installed game through `HOI4_GAME_DIR`. Each case copies
the mod into a temporary folder, adds one defect, runs the audit with `--root` and checks that the
expected error rule appears; the untouched copy is the valid case for every rule. The 3D model
registration rules of the asset-wiring audit start from a correct registration written below (a
mesh built in memory, since a `.mesh` is binary) and break it one link at a time. Nothing is
written outside temporary folders. Run from the package root:

	python -m unittest discover -s .tools/tests -p "test_*.py"
"""

from __future__ import annotations

import importlib.util
import json
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

TOOLS = Path(__file__).resolve().parents[1]
FIXTURES = Path(__file__).resolve().parent / "fixtures" / "audits"
LOCALISATION_AUDIT = TOOLS / "audits" / "audit_localisation_static.py"
ASSET_AUDIT = TOOLS / "audits" / "audit_asset_wiring_static.py"
BOM = "﻿"


def run_audit(script: Path, root: Path, game: Path) -> subprocess.CompletedProcess:
	"""Run one audit against `root` with `game` as the installation; the JSON report goes beside `root`."""
	environment = dict(os.environ, HOI4_GAME_DIR=str(game))
	report = root.parent / "report.json"
	return subprocess.run(
		[sys.executable, "-B", str(script), "--root", str(root), "--json", str(report), "--fail-on", "error"],
		capture_output=True, text=True, encoding="utf-8", errors="replace", env=environment, check=False,
	)


def report_rows(root: Path) -> List[Dict[str, object]]:
	return json.loads((root.parent / "report.json").read_text(encoding="utf-8"))["findings"]


def error_rules(root: Path) -> List[str]:
	return sorted({row["rule"] for row in report_rows(root) if row["level"] == "error"})


class AuditCase(unittest.TestCase):
	script: Path = LOCALISATION_AUDIT

	def report(self, files: Optional[Dict[str, Union[str, bytes]]] = None) -> List[Dict[str, object]]:
		"""Copy the valid mod, write `files` into it, run the audit and return every finding it reports."""
		with tempfile.TemporaryDirectory() as folder:
			root = Path(folder) / "mod"
			shutil.copytree(FIXTURES / "mod", root)
			for name, content in (files or {}).items():
				path = root / name
				path.parent.mkdir(parents=True, exist_ok=True)
				path.write_bytes(content if isinstance(content, bytes) else content.encode("utf-8"))
			completed = run_audit(self.script, root, FIXTURES / "game")
			self.assertIn(completed.returncode, (0, 1), completed.stderr)
			self.assertEqual(completed.returncode, 1 if error_rules(root) else 0)
			return report_rows(root)

	def audit(self, files: Optional[Dict[str, Union[str, bytes]]] = None) -> List[str]:
		"""Return the error rules the audit reports for the valid mod plus `files`."""
		return sorted({row["rule"] for row in self.report(files) if row["level"] == "error"})

	def assert_rule(self, rule: str, files: Dict[str, str]) -> None:
		self.assertNotIn(rule, self.audit())
		self.assertIn(rule, self.audit(files))


DECISIONS = "common/decisions/fixture_decisions.txt"
EVENTS = "events/fixture_events.txt"
EXTRA_LOCALISATION = "localisation/english/extra_l_english.yml"


class LocalisationAudit(AuditCase):
	script = LOCALISATION_AUDIT

	def test_valid_mod_has_no_errors(self) -> None:
		self.assertEqual(self.audit(), [])

	def test_parse_error(self) -> None:
		self.assert_rule("LOC-PARSE", {EXTRA_LOCALISATION: BOM + "l_english:\n this line has no colon\n"})

	def test_missing_bom(self) -> None:
		self.assert_rule("LOC-BOM", {EXTRA_LOCALISATION: "l_english:\n fixture_extra: \"Extra\"\n"})

	def test_missing_header(self) -> None:
		self.assert_rule("LOC-HEADER", {EXTRA_LOCALISATION: BOM + " fixture_extra: \"Extra\"\n"})

	def test_ordinal_suffix(self) -> None:
		self.assert_rule("LOC-ENCODING", {EXTRA_LOCALISATION: BOM + "l_english:\n fixture_extra:0 \"Extra\"\n"})

	def test_duplicate_key(self) -> None:
		self.assert_rule("LOC-DUPLICATE", {EXTRA_LOCALISATION: BOM + "l_english:\n fixture_flag: \"Again\"\n"})

	def test_undefined_event_root(self) -> None:
		# `fixture.99` names an event of the declared `fixture` namespace that has no keys at all.
		events = (FIXTURES / "mod" / EVENTS).read_text(encoding="utf-8").replace("name = fixture.1.a", "name = fixture.99")
		self.assert_rule("LOC-EVENT-ROOT", {EVENTS: events})

	def test_undefined_key_binding(self) -> None:
		decisions = (FIXTURES / "mod" / DECISIONS).read_text(encoding="utf-8").replace(
			"\t\ticon = fixture_icon\n", "\t\ticon = fixture_icon\n\t\tdesc = fixture_unwritten_desc\n")
		self.assert_rule("LOC-KEY-BINDING", {DECISIONS: decisions})

	def test_missing_event_text(self) -> None:
		event = "\ncountry_event = {\n\tid = fixture.2\n\tis_triggered_only = yes\n\toption = {\n\t\tname = fixture.1.a\n\t}\n}\n"
		events = (FIXTURES / "mod" / EVENTS).read_text(encoding="utf-8") + event
		self.assert_rule("LOC-EVENT-CONTENT", {EVENTS: events})

	def test_unlocalised_requirement_flag(self) -> None:
		decisions = (FIXTURES / "mod" / DECISIONS).read_text(encoding="utf-8").replace("fixture_flag", "fixture_raw_flag")
		self.assert_rule("LOC-REQUIREMENT-FLAG", {DECISIONS: decisions})

	def test_unlocalised_requirement_variable(self) -> None:
		decisions = (FIXTURES / "mod" / DECISIONS).read_text(encoding="utf-8").replace(
			"has_country_flag = fixture_flag", "has_variable = fixture_raw_variable")
		self.assert_rule("LOC-REQUIREMENT-VARIABLE", {DECISIONS: decisions})

	def test_unlocalised_check_variable_forms(self) -> None:
		original = (FIXTURES / "mod" / DECISIONS).read_text(encoding="utf-8")
		for check in ("check_variable = { fixture_raw_variable > 5 }",
				"check_variable = { var = fixture_raw_variable value = 5 compare = greater_than }"):
			with self.subTest(check=check):
				self.assert_rule("LOC-REQUIREMENT-VARIABLE", {DECISIONS: original.replace("has_country_flag = fixture_flag", check)})

	def test_unlocalised_multiline_check_variable_forms(self) -> None:
		original = (FIXTURES / "mod" / DECISIONS).read_text(encoding="utf-8")
		for block in ("check_variable = {\n\t\t\t\tvar = fixture_raw_variable\n\t\t\t\tvalue = 5\n\t\t\t\tcompare = greater_than\n\t\t\t}",
				"check_variable = {\n\t\t\t\tfixture_raw_variable > 5\n\t\t\t}"):
			with self.subTest(block=block):
				self.assert_rule("LOC-REQUIREMENT-VARIABLE", {DECISIONS: original.replace("has_country_flag = fixture_flag", block)})

	def test_hidden_check_variable_is_not_displayed(self) -> None:
		decisions = (FIXTURES / "mod" / DECISIONS).read_text(encoding="utf-8").replace(
			"has_country_flag = fixture_flag", "hidden_trigger = { check_variable = { fixture_raw_variable > 5 } }\n\t\t\thas_country_flag = fixture_flag")
		self.assertNotIn("LOC-REQUIREMENT-VARIABLE", self.audit({DECISIONS: decisions}))

	def test_missing_implicit_key(self) -> None:
		decisions = (FIXTURES / "mod" / DECISIONS).read_text(encoding="utf-8").replace(
			"\tfixture_decision = {", "\tfixture_unnamed_decision = {\n\t}\n\tfixture_decision = {")
		self.assert_rule("LOC-IMPLICIT", {DECISIONS: decisions})


class AssetWiringAudit(AuditCase):
	script = ASSET_AUDIT
	GUI = "interface/fixture.gui"
	GFX = "interface/fixture.gfx"

	def test_valid_mod_has_no_errors(self) -> None:
		self.assertEqual(self.audit(), [])

	def test_unresolved_reference(self) -> None:
		gui = (FIXTURES / "mod" / self.GUI).read_text(encoding="utf-8").replace("GFX_vanilla_ok", "GFX_registered_nowhere")
		self.assert_rule("GFX-UNRESOLVED", {self.GUI: gui})

	def test_missing_texture_file(self) -> None:
		gfx = (FIXTURES / "mod" / self.GFX).read_text(encoding="utf-8").replace("fixture_icon.dds", "absent_icon.dds")
		self.assert_rule("GFX-MISSING-FILE", {self.GFX: gfx})

	def test_missing_vanilla_backing_file(self) -> None:
		gui = (FIXTURES / "mod" / self.GUI).read_text(encoding="utf-8").replace("GFX_vanilla_ok", "GFX_vanilla_broken")
		self.assert_rule("GFX-MISSING-VANILLA-FILE", {self.GUI: gui})

	def test_missing_implicit_sprite(self) -> None:
		decisions = (FIXTURES / "mod" / DECISIONS).read_text(encoding="utf-8").replace("icon = fixture_icon", "icon = unregistered_icon")
		self.assert_rule("GFX-IMPLICIT", {DECISIONS: decisions})


def pdx_property(name: str, kind: str, values: Tuple[object, ...]) -> bytes:
	"""One PDX binary property: `!`, a length byte, the name, a type letter and a counted array."""
	head = b"!" + bytes([len(name)]) + name.encode("ascii") + kind.encode("ascii") + struct.pack("<I", len(values))
	if kind == "i":
		return head + struct.pack(f"<{len(values)}i", *values)
	if kind == "f":
		return head + struct.pack(f"<{len(values)}f", *values)
	return head + b"".join(struct.pack("<I", len(text) + 1) + str(text).encode("ascii") + b"\0" for text in values)


def pdx_mesh(*objects: str) -> bytes:
	"""A small PDX binary mesh in the layout of the exported zin meshes: one `object` block of shapes, then a `locator` block.

	Float and string payloads carry bytes that look like markers (`[` and `!`), so a reader that
	scans for markers instead of skipping each property by its size loses its place.
	"""
	data = b"@@b@" + pdx_property("pdxasset", "i", (1, 0)) + b"[object\0"
	for name in objects:
		data += b"[[" + name.encode("ascii") + b"\0[[[mesh\0"
		data += pdx_property("p", "f", (1.0, 2.0, 3.0)) + pdx_property("ix", "i", (0x215B5B21,))
		data += b"[[[[material\0" + pdx_property("shader", "s", ("PdxMeshAdvanced",)) + pdx_property("diff", "s", ("![[a.dds",))
	return data + b"[locator\0"


MODEL_GFX = "gfx/entities/fixture_units.gfx"
MODEL_ENTITIES = "gfx/entities/fixture_units.asset"
MODEL_ANIMATIONS = "gfx/models/units/fixture/fixture_unit.asset"
MODEL_UNITS = "common/units/fixture_units.txt"
MODEL_MESH = "gfx/models/units/fixture/fixture_unit.mesh"

# A correct registration: a mesh with two objects, a pdxmesh that settings one of them, two animations,
# an entity per sprite, and sprites that the mod, the game and a DLC package of the game all supply.
MODEL_FILES: Dict[str, Union[str, bytes]] = {
	MODEL_GFX: """objectTypes = {
	pdxmesh = {
		name = "fixture_unit_mesh"
		file = "gfx/models/units/fixture/fixture_unit.mesh"
		meshsettings = {
			name = "fixture_shape"
			index = 0
			texture_diffuse = "fixture_unit_diffuse.dds"
			texture_normal = "fixture_unit_normal.dds"
			texture_specular = "fixture_unit_specular.dds"
			shader = "PdxMeshAdvanced"
		}
		animation = { id = "idle" type = "fixture_unit_idle_animation" }
		animation = { id = "move" type = "fixture_unit_move_animation" }
	}
}
""",
	MODEL_ENTITIES: """entity = {
	name = "fixture_unit_entity"
	pdxmesh = "fixture_unit_mesh"
	default_state = "idle"
	state = { name = "idle" animation = "idle" animation_blend_time = 0.3 animation_speed = 1.0 }
	state = { name = "move" animation = "move" animation_blend_time = 0.5 animation_speed = 1.0 }
	attach = { name = "weapon" Right_Hand_node = "vanilla_weapon_entity" }
	scale = 0.8
}

entity = {
	name = "fixture_game_mesh_entity"
	pdxmesh = "vanilla_fixture_mesh"
	default_state = "idle"
	state = { name = "idle" animation = "idle" animation_blend_time = 0.3 animation_speed = 1.0 }
}
""",
	MODEL_ANIMATIONS: """animation = {
	name = "fixture_unit_idle_animation"
	file = "fixture_unit_idle.anim"
}
animation = {
	name = "fixture_unit_move_animation"
	file = "fixture_unit_move.anim"
}
""",
	MODEL_UNITS: """sub_units = {
	fixture_unit = {
		sprite = fixture_unit
	}
	fixture_game_mesh_unit = {
		sprite = "fixture_game_mesh"
	}
	fixture_vanilla_unit = {
		sprite = vanilla_unit
	}
	fixture_dlc_unit = {
		sprite = dlc_unit
	}
}
""",
	"interface/fixture_units.gfx": "spriteTypes = {\n" + "".join(
		f'\tspriteType = {{\n\t\tname = "GFX_unit_{sprite}_icon_medium"\n\t\ttexturefile = "gfx/interface/decisions/fixture_icon.dds"\n\t}}\n'
		for sprite in ("fixture_unit", "fixture_game_mesh", "vanilla_unit", "dlc_unit")) + "}\n",
	MODEL_MESH: pdx_mesh("fixture_shape", "collision_shape"),
	"gfx/models/units/fixture/fixture_unit_idle.anim": b"anim",
	"gfx/models/units/fixture/fixture_unit_move.anim": b"anim",
	"gfx/models/units/fixture/fixture_unit_diffuse.dds": b"DDS ",
	"gfx/models/units/fixture/fixture_unit_normal.dds": b"DDS ",
	"gfx/models/units/fixture/fixture_unit_specular.dds": b"DDS ",
}


def load_audit_module():
	"""Import the asset-wiring audit to call its PDX reader directly.

	The module is not registered in `sys.modules`, which is how `gfx/gfx.py` imports it, so a module-level
	dataclass would fail here as it does there.
	"""
	spec = importlib.util.spec_from_file_location("audit_asset_wiring_static", ASSET_AUDIT)
	module = importlib.util.module_from_spec(spec)
	spec.loader.exec_module(module)
	return module


class ModelRegistrationAudit(AuditCase):
	script = ASSET_AUDIT

	def broken(self, name: str, old: str, new: str) -> Dict[str, Union[str, bytes]]:
		"""The correct registration with `old` replaced by `new` in the text file `name`."""
		text = MODEL_FILES[name]
		assert isinstance(text, str) and text.count(old) == 1, (name, old)
		return {**MODEL_FILES, name: text.replace(old, new)}

	def model_rows(self, files: Dict[str, Union[str, bytes]]) -> List[Tuple[str, str, str, int]]:
		"""The (rule, level, file, line) of every 3D registration finding, plus a check that the line is the one that holds `old`."""
		rows = self.report(files)
		return sorted((str(row["rule"]), str(row["level"]), str(row["path"]), int(row["line"])) for row in rows if str(row["rule"]).startswith("GFX-3D-"))

	def line_of(self, name: str, needle: str, files: Dict[str, Union[str, bytes]]) -> int:
		text = files[name]
		assert isinstance(text, str)
		return next(number for number, line in enumerate(text.splitlines(), 1) if needle in line)

	def assert_finding(self, name: str, old: str, new: str, rule: str, level: str, where: str, needle: str) -> None:
		"""Break one link and expect exactly one 3D finding, at the line of `needle` in file `where`."""
		files = self.broken(name, old, new)
		self.assertEqual(self.model_rows(files), [(rule, level, where, self.line_of(where, needle, files))])
		errors = self.audit(files)
		self.assertEqual(errors, [rule] if level == "error" else [])

	def test_correct_registration_has_no_findings(self) -> None:
		self.assertEqual(self.model_rows(MODEL_FILES), [])
		self.assertEqual(self.audit(MODEL_FILES), [])

	def test_missing_mesh_file(self) -> None:
		self.assert_finding(MODEL_GFX, "fixture_unit.mesh", "fixture_unit_absent.mesh", "GFX-3D-MESH-MISSING", "error", MODEL_GFX, "fixture_unit_absent.mesh")

	def test_mesh_path_wrong_but_file_exists(self) -> None:
		self.assert_finding(MODEL_GFX, "units/fixture/fixture_unit.mesh", "units/elsewhere/fixture_unit.mesh", "GFX-3D-FILE-PATH", "warning", MODEL_GFX, "units/elsewhere")

	def test_missing_animation_file(self) -> None:
		self.assert_finding(MODEL_ANIMATIONS, "fixture_unit_move.anim", "fixture_unit_gone.anim", "GFX-3D-ANIM-MISSING", "error", MODEL_ANIMATIONS, "fixture_unit_gone.anim")

	def test_undefined_animation_type(self) -> None:
		self.assert_finding(MODEL_GFX, "fixture_unit_move_animation", "fixture_unit_run_animation", "GFX-3D-ANIM-UNDEFINED", "error", MODEL_GFX, "fixture_unit_run_animation")

	def test_dangling_entity_pdxmesh(self) -> None:
		self.assert_finding(MODEL_ENTITIES, 'pdxmesh = "fixture_unit_mesh"', 'pdxmesh = "fixture_absent_mesh"', "GFX-3D-ENTITY-PDXMESH", "error", MODEL_ENTITIES, "fixture_absent_mesh")

	def test_entity_may_use_a_pdxmesh_of_the_game(self) -> None:
		self.assertNotIn("GFX-3D-ENTITY-PDXMESH", [row[0] for row in self.model_rows(MODEL_FILES)])

	def test_unit_sprite_without_entity(self) -> None:
		files = self.broken(MODEL_UNITS, "sprite = fixture_unit\n", "sprite = fixture_orphan\n")
		self.assertEqual(self.model_rows(files), [("GFX-3D-UNIT-ENTITY", "error", MODEL_UNITS, self.line_of(MODEL_UNITS, "fixture_orphan", files))])
		self.assertIn("GFX-3D-UNIT-ENTITY", self.audit(files))

	def test_unit_sprite_entity_comes_from_the_game_or_a_dlc_package(self) -> None:
		# `vanilla_unit_entity` is defined by the game and `dlc_unit_entity` by a DLC package; the correct registration uses both.
		self.assertEqual([row for row in self.model_rows(MODEL_FILES) if row[0] == "GFX-3D-UNIT-ENTITY"], [])

	def test_meshsettings_name_not_in_mesh(self) -> None:
		self.assert_finding(MODEL_GFX, 'name = "fixture_shape"', 'name = "other_shape"', "GFX-3D-MESHSETTINGS", "error", MODEL_GFX, "meshsettings = {")

	def test_meshsettings_name_differing_only_in_case(self) -> None:
		self.assert_finding(MODEL_GFX, 'name = "fixture_shape"', 'name = "Fixture_Shape"', "GFX-3D-MESHSETTINGS-CASE", "warning", MODEL_GFX, "meshsettings = {")

	def test_meshsettings_may_name_any_object_of_the_mesh(self) -> None:
		files = self.broken(MODEL_GFX, 'name = "fixture_shape"', 'name = "collision_shape"')
		self.assertEqual(self.model_rows(files), [])

	def test_missing_texture(self) -> None:
		for key, name in (("texture_diffuse", "fixture_unit_diffuse.dds"), ("texture_normal", "fixture_unit_normal.dds"), ("texture_specular", "fixture_unit_specular.dds")):
			with self.subTest(key=key):
				# The error is the 3D rule alone: the diffuse map is not also reported as a missing file.
				self.assert_finding(MODEL_GFX, f'"{name}"', '"fixture_unit_absent.dds"', "GFX-3D-TEXTURE-MISSING", "error", MODEL_GFX, key)

	def test_unreadable_mesh(self) -> None:
		pointer = b"version https://git-lfs.github.com/spec/v1\noid sha256:0\nsize 1\n"
		for label, content in (("a Git LFS pointer", pointer), ("a truncated mesh", pdx_mesh("fixture_shape")[:-3])):
			with self.subTest(label):
				files = {**MODEL_FILES, MODEL_MESH: content}
				self.assertEqual(self.model_rows(files), [("GFX-3D-MESH-UNREADABLE", "warning", MODEL_GFX, self.line_of(MODEL_GFX, "file = ", files))])

	def test_entity_state_without_animation(self) -> None:
		self.assert_finding(MODEL_ENTITIES, 'name = "move" animation = "move"', 'name = "move" animation = "walk"', "GFX-3D-STATE-ANIMATION", "warning", MODEL_ENTITIES, "animation = \"walk\"")

	def test_attach_without_entity(self) -> None:
		self.assert_finding(MODEL_ENTITIES, '"vanilla_weapon_entity"', '"fixture_absent_entity"', "GFX-3D-ATTACH-ENTITY", "warning", MODEL_ENTITIES, "fixture_absent_entity")


class PdxMeshReader(unittest.TestCase):
	def setUp(self) -> None:
		self.names = load_audit_module().pdx_object_names

	def test_reads_the_objects_under_object(self) -> None:
		self.assertEqual(self.names(pdx_mesh("a", "b.002", "c")), ["a", "b.002", "c"])

	def test_a_mesh_without_objects_has_none(self) -> None:
		self.assertEqual(self.names(pdx_mesh()), [])

	def test_a_text_mesh_is_not_decoded(self) -> None:
		self.assertIsNone(self.names(b"@@t@pdxasset int 2 1 0\n[object]\n"))

	def test_malformed_meshes_raise(self) -> None:
		good = pdx_mesh("a")
		for label, data in (("no header", b"mesh"), ("empty", b""), ("truncated", good[:-3]), ("cut in a property", good[:20]), ("unknown byte", good + b"?"), ("unknown type", b"@@b@!\x01xq\x01\0\0\0")):
			with self.subTest(label), self.assertRaises((ValueError, IndexError, struct.error)):
				self.names(data)


class MissingGame(unittest.TestCase):
	def test_each_audit_exits_2_without_a_game(self) -> None:
		with tempfile.TemporaryDirectory() as folder:
			empty = Path(folder) / "empty_game"
			empty.mkdir()
			root = Path(folder) / "mod"
			shutil.copytree(FIXTURES / "mod", root)
			for script in (LOCALISATION_AUDIT, ASSET_AUDIT):
				completed = run_audit(script, root, empty)
				self.assertEqual(completed.returncode, 2, script.name)
				self.assertIn("HOI4_GAME_DIR", completed.stderr)


if __name__ == "__main__":
	unittest.main()
