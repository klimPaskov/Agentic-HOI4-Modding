"""Fixture tests for the localisation and asset-wiring audits in `.tools/audits/`.

`fixtures/audits/mod/` is a tiny mod that both audits accept without an error, and
`fixtures/audits/game/` stands in for the installed game through `HOI4_GAME_DIR`. Each case copies
the mod into a temporary folder, adds one defect, runs the audit with `--root` and checks that the
expected error rule appears; the untouched copy is the valid case for every rule. Nothing is written
outside temporary folders. Run from the package root:

	python -m unittest discover -s .tools/tests -p "test_*.py"
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Dict, List, Optional

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


def error_rules(root: Path) -> List[str]:
	payload = json.loads((root.parent / "report.json").read_text(encoding="utf-8"))
	return sorted({row["rule"] for row in payload["findings"] if row["level"] == "error"})


class AuditCase(unittest.TestCase):
	script: Path = LOCALISATION_AUDIT

	def audit(self, files: Optional[Dict[str, str]] = None) -> List[str]:
		"""Copy the valid mod, write `files` into it, run the audit and return the error rules it reports."""
		with tempfile.TemporaryDirectory() as folder:
			root = Path(folder) / "mod"
			shutil.copytree(FIXTURES / "mod", root)
			for name, text in (files or {}).items():
				path = root / name
				path.parent.mkdir(parents=True, exist_ok=True)
				path.write_bytes(text.encode("utf-8"))
			completed = run_audit(self.script, root, FIXTURES / "game")
			self.assertIn(completed.returncode, (0, 1), completed.stderr)
			rules = error_rules(root)
			self.assertEqual(completed.returncode, 1 if rules else 0)
			return rules

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
