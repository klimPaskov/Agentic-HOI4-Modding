"""Fixture tests for the finding levels of `.tools/audits/validate_scripts_mcp.py`.

The fixtures are real `hoi4.script_validate` responses, so the tests need no MCP server.
Run from the mod root: `python -B .tools/tests/test_validate_scripts_mcp.py`.
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS / "audits"))

import validate_scripts_mcp as validator

RESPONSES = json.loads((TOOLS / "tests" / "fixtures" / "script_validate" / "responses.json").read_text(encoding="utf-8"))


def rules(name):
	return [(f.rule, f.level, f.line) for f in validator.findings_for("events/x.txt", RESPONSES[name])]


class FindingLevels(unittest.TestCase):
	def test_syntax_error_is_an_error(self):
		self.assertEqual(rules("syntax_error"), [("MCP-SCRIPT-ERROR", "error", 3)])

	def test_unresolved_and_unchecked_never_fail(self):
		self.assertEqual(rules("unresolved_and_unchecked"), [
			("MCP-SCRIPT-UNRESOLVED", "warning", 1),
			("MCP-SCRIPT-UNCHECKED-ARGUMENTS", "review", 3),
		])
		self.assertIn("did you mean add_political_power", validator.findings_for("events/x.txt", RESPONSES["unresolved_and_unchecked"])[0].message)

	def test_known_mistakes_are_warnings_and_omissions_are_reported(self):
		self.assertEqual(rules("known_mistake_false_positive"), [
			("MCP-SCRIPT-KNOWN-MISTAKE", "warning", 1466),
			("MCP-SCRIPT-INCOMPLETE", "warning", 0),
		])

	def test_only_script_files_are_sent(self):
		with tempfile.TemporaryDirectory() as folder:
			root = Path(folder)
			(root / "events").mkdir()
			(root / "events" / "present.txt").write_text("namespace = test", encoding="utf-8")
			with patch.object(validator, "REPO_ROOT", root):
				self.assertEqual(validator.script_paths(["events/present.txt", "localisation/english/x.yml",
					"gfx/x.dds", "common/missing_file.txt"]), ["events/present.txt"])


if __name__ == "__main__":
	unittest.main()
