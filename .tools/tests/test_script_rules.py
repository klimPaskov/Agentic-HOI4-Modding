"""Fixture tests for `.tools/audits/audit_script_rules.py`.

Run from the mod root: `python -B .tools/tests/test_script_rules.py`.
"""

import sys
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS / "audits"))

import audit_script_rules as rules

FIXTURES = TOOLS / "tests" / "fixtures" / "script_rules"


def scan(name, path):
	return rules.scan_text(path, (FIXTURES / name).read_text(encoding="utf-8"))


class ScriptRules(unittest.TestCase):
	def test_valid_fixture_has_no_findings(self):
		self.assertEqual(scan("valid.txt", "common/scripted_effects/valid.txt"), [])

	def test_comparison_and_unary_minus_are_errors(self):
		found = [(f.rule, f.line) for f in scan("invalid.txt", "common/scripted_effects/invalid.txt")]
		self.assertEqual(found, [
			("RULE-COMPARISON-OPERATOR", 5),
			("RULE-COMPARISON-OPERATOR", 6),
			("RULE-UNARY-MINUS", 8),
		])

	def test_format_characters_only_matter_in_scripted_localisation(self):
		found = scan("invalid_scripted_localisation.txt", "common/scripted_localisation/x.txt")
		self.assertEqual([(f.rule, f.line) for f in found], [("RULE-SCRIPTED-LOC-FORMAT", 5), ("RULE-SCRIPTED-LOC-FORMAT", 5)])
		self.assertEqual(scan("invalid_scripted_localisation.txt", "common/scripted_effects/x.txt"), [])

	def test_every_finding_is_an_error(self):
		self.assertTrue(all(f.level == "error" for f in scan("invalid.txt", "events/x.txt")))


if __name__ == "__main__":
	unittest.main()
