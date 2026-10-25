#!/usr/bin/env python3
"""Lexical checks for the Clausewitz syntax rules in `CLAUDE.md` that break the game silently.

Rules, all reported at `error` level under the `.tools/lib/report.py` contract:

- `RULE-COMPARISON-OPERATOR` (CLAUDE.md section 1, rule 2): `<=` and `>=` are not supported in
  script; use `check_variable` with `compare = greater_than_or_equals` or `less_than_or_equals`.
- `RULE-UNARY-MINUS` (section 1, rule 11): `= -token` negates a variable token, which does
  nothing; negate with `multiply_variable` first. Negative numbers are not affected, and
  `constant:` and `@` values are not variable tokens, so this rule does not cover them.
- `RULE-SCRIPTED-LOC-FORMAT` (section 2, rule 3): `§` and `£` must not be written directly in
  scripted localisation (`common/scripted_localisation/`).

Localisation keys with an ordinal (`key:0 "..."`, section 2, rule 5) are reported by
`audit_localisation_static.py` as `LOC-ENCODING`.

The scan is comment- and string-aware: `#` comments are ignored everywhere, and the two script
rules ignore quoted text. It reads `.txt` files under `common/`, `events/` and `history/`. It is
lexical only: it cannot judge scopes, semantics or whether a construct runs.

Usage:
	python -B .tools/audits/audit_script_rules.py
	python -B .tools/audits/audit_script_rules.py --paths events/x.txt common/scripted_effects/
	python -B .tools/audits/audit_script_rules.py --json .tmp/script_rules.json

With `--paths`, only those files or folders are scanned. Exit status: 0 no errors, 1 errors.
"""

from __future__ import annotations

import sys
import argparse
import re
from pathlib import Path
from typing import Iterable, List

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # .tools, for the shared lib package
from lib.clausewitz import strip_comment
from lib.report import Finding, PathFilter, add_arguments, exit_code, merge_json, print_findings, relative, requested_paths

REPO_ROOT = Path(__file__).resolve().parents[2]
SCAN_DIRS = ("common", "events", "history")
CHECK = "script-rules"
LEVELS = {
	"RULE-COMPARISON-OPERATOR": "error",
	"RULE-UNARY-MINUS": "error",
	"RULE-SCRIPTED-LOC-FORMAT": "error",
}

COMPARISON = re.compile(r"<=|>=")
# `= -name`, where name starts like a variable token. `constant:` and `@macro` values are injected
# literals, not variable tokens, and are not covered by the rule.
UNARY_MINUS = re.compile(r"=\s*-(?!constant:)([A-Za-z_][A-Za-z0-9_.:@^]*)")
FORMAT_CHARACTER = re.compile("[§£]")
QUOTED = re.compile(r'"[^"\n]*"')


def scan_text(path: str, text: str) -> List[Finding]:
	"""Return the rule findings for one script file's text."""
	findings = []
	scripted_loc = path.startswith("common/scripted_localisation/")
	for number, raw in enumerate(text.splitlines(), 1):
		code = strip_comment(raw)
		bare = QUOTED.sub('""', code)
		for match in COMPARISON.finditer(bare):
			findings.append(Finding(CHECK, "RULE-COMPARISON-OPERATOR", "error", path, number,
				f"`{match.group(0)}` is not supported; use check_variable with a compare mode"))
		for match in UNARY_MINUS.finditer(bare):
			findings.append(Finding(CHECK, "RULE-UNARY-MINUS", "error", path, number,
				f"`-{match.group(1)}` negates a variable token, which does nothing; multiply by -1 first"))
		if scripted_loc:
			for match in FORMAT_CHARACTER.finditer(code):
				findings.append(Finding(CHECK, "RULE-SCRIPTED-LOC-FORMAT", "error", path, number,
					f"format character U+{ord(match.group(0)):04X} written directly in scripted localisation"))
	return findings


def script_files(paths: Iterable[str] = ()) -> List[Path]:
	selector = PathFilter(list(paths))
	found = []
	for folder in SCAN_DIRS:
		base = REPO_ROOT / folder
		if base.is_dir():
			found += [p for p in base.rglob("*.txt") if selector.matches(relative(p.resolve()))]
	return sorted(found)


def main() -> int:
	parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
	parser.add_argument("--json", type=Path, help="also write the findings as JSON")
	add_arguments(parser)
	arguments = parser.parse_args()
	paths = requested_paths(arguments)
	findings: List[Finding] = []
	for path in script_files(paths or ()):
		text = path.read_bytes().decode("utf-8-sig", errors="replace")
		findings += scan_text(relative(path.resolve()), text)
	findings.sort(key=lambda f: (f.path, f.line, f.rule, f.message))
	print_findings(CHECK, findings)
	if arguments.json:
		merge_json(arguments.json, findings, LEVELS)
	return exit_code(findings, arguments.fail_on)


if __name__ == "__main__":
	raise SystemExit(main())
