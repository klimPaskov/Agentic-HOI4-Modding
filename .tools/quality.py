#!/usr/bin/env python3
"""Lint and type checks for the maintained Python tooling, with a ratchet for older code.

Ruff (rules in `.tools/ruff.toml`) and mypy run through `uvx` at the versions pinned in
`.tools/requirements-dev.txt`, so nothing is installed globally. Findings follow
`.tools/lib/report.py`:

- `QUALITY-RUFF` (error): a ruff defect finding (unused import, undefined name, swallowed
  exception, bugbear pattern and so on) in a strict file, or one that the baseline does not hold.
- `QUALITY-COMPLEXITY` (error): a function whose McCabe complexity or statement count exceeds the
  limit and is new, or has grown past its recorded value.
- `QUALITY-TYPE` (error): a `mypy --strict` error in a strict file.
- `QUALITY-BASELINE` (review): an older finding recorded in `.tools/quality_baseline.json`.

Strict files (`STRICT_FILES`) must stay free of defect and type findings; everything else in
`.tools/` and the skill helpers is held at or below its baseline. `--write-baseline` records
the current findings, and refuses while any error is reported, so it can only record
improvements or the first baseline. A suppression needs a `noqa` comment with its reason.

Usage:
	python -B .tools/quality.py                       # whole tooling tree
	python -B .tools/quality.py --paths .tools/check.py .tools/gfx/gfx.py
	python -B .tools/quality.py --write-baseline      # after reducing findings

Exit status: 0 no errors, 1 errors, 2 when uv, ruff or mypy cannot run.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from lib.report import Finding, PathFilter, add_arguments, exit_code, merge_json, print_findings, relative, requested_paths

REPO_ROOT = Path(__file__).resolve().parents[1]
BASELINE = REPO_ROOT / ".tools" / "quality_baseline.json"
CHECK = "quality"
RUFF = "ruff@0.8.4"
MYPY = "mypy==1.14.1"
RATCHET_CODES = {"C901", "PLR0915"}
STRICT_FILES = (
	".tools/lib/", ".tools/check.py", ".tools/quality.py", ".tools/audits/audit_script_rules.py", ".tools/audits/validate_scripts_mcp.py",
	".tools/gfx/gfx.py", ".claude/skills/hoi4-feature-assets/tools/", ".claude/skills/hoi4-save-inspection/scripts/",
)
# mypy runs from each folder so that local imports (such as `.tools/lib`) resolve.
MYPY_GROUPS: Tuple[Tuple[str, Tuple[str, ...]], ...] = (
	(".tools", ("lib", "check.py", "quality.py", "audits/audit_script_rules.py", "audits/validate_scripts_mcp.py", "gfx/gfx.py")),
	(".claude/skills/hoi4-feature-assets/tools", ("convert_to_dds.py", "create_advisor_icon.py",
		"extract_portrait_source_crop.py", "process_achievement_icons.py", "process_report_event_image.py")),
	(".claude/skills/hoi4-save-inspection/scripts", ("save_inspect.py",)),
)
MYPY_FLAGS = ("--strict", "--python-version", "3.9", "--ignore-missing-imports", "--no-error-summary", "--no-color-output")
LEVELS = {"QUALITY-RUFF": "error", "QUALITY-COMPLEXITY": "error", "QUALITY-TYPE": "error", "QUALITY-BASELINE": "review"}
MEASURE = re.compile(r"\((\d+) > \d+\)")
# Ruff messages can name a line ("from line 61"); keys drop those numbers so moving code keeps its entry.
LINE_NUMBER = re.compile(r"\bline \d+")
DEF_NAME = re.compile(r"^\s*(?:async\s+)?def\s+([A-Za-z_][A-Za-z0-9_]*)")


class ToolUnavailable(RuntimeError):
	pass


def is_strict(path: str) -> bool:
	return path.startswith(STRICT_FILES)


def run_uvx(package: str, arguments: Sequence[str], cwd: Path) -> subprocess.CompletedProcess[str]:
	if shutil.which("uvx") is None:
		raise ToolUnavailable("uvx is not on PATH; install uv (https://docs.astral.sh/uv/) to run the quality checks")
	command = ["uvx", "--from", package, package.split("@")[0].split("==")[0], *arguments]
	return subprocess.run(command, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")


def ruff_findings(paths: Optional[List[str]]) -> List[Dict[str, Any]]:
	targets = [p for p in paths if p.endswith(".py")] if paths else []
	if paths and not targets:
		return []
	completed = run_uvx(RUFF, ["check", "--config", ".tools/ruff.toml", "--output-format", "json", "--no-cache", "--exit-zero", *targets], REPO_ROOT)
	if completed.returncode != 0:
		raise ToolUnavailable(f"ruff failed: {completed.stderr.strip()[-300:]}")
	rows: List[Dict[str, Any]] = json.loads(completed.stdout or "[]")
	return rows


def normalise_key(key: str) -> str:
	return LINE_NUMBER.sub("line N", key)


def ruff_key(row: Dict[str, Any], path: str) -> Tuple[str, int]:
	"""Return (baseline key, measured value) for one ruff finding."""
	code = str(row["code"])
	if code not in RATCHET_CODES:
		return normalise_key(f"{code} {row['message']}"), 1
	match = MEASURE.search(str(row["message"]))
	value = int(match.group(1)) if match else 0
	lines = (REPO_ROOT / path).read_text(encoding="utf-8", errors="replace").splitlines()
	line = lines[int(row["location"]["row"]) - 1] if lines else ""
	name = DEF_NAME.match(line)
	return f"{code} {name.group(1) if name else 'line ' + str(row['location']['row'])}", value


def mypy_findings(paths: Optional[List[str]]) -> List[Finding]:
	findings = []
	selector = PathFilter(paths)
	for folder, targets in MYPY_GROUPS:
		chosen = [t for t in targets if not paths or selector.matches(f"{folder}/{t}".rstrip("/"))
			or any(p.startswith(f"{folder}/{t}") for p in paths)]
		if not chosen:
			continue
		completed = run_uvx(MYPY, [*MYPY_FLAGS, *chosen], REPO_ROOT / folder)
		if completed.returncode not in (0, 1):
			raise ToolUnavailable(f"mypy failed: {(completed.stderr or completed.stdout).strip()[-300:]}")
		for line in completed.stdout.splitlines():
			match = re.match(r"^(.+?):(\d+): error: (.+)$", line)
			if match:
				path = relative(f"{folder}/{match.group(1)}")
				findings.append(Finding(CHECK, "QUALITY-TYPE", "error", path, int(match.group(2)), f"mypy --strict: {match.group(3)}"))
	return findings


def evaluate(rows: List[Dict[str, Any]], baseline: Dict[str, Dict[str, int]]) -> Tuple[List[Finding], Dict[str, Dict[str, int]]]:
	findings: List[Finding] = []
	measured: Dict[str, Dict[str, int]] = {}
	remaining = {path: dict(entries) for path, entries in baseline.items()}
	for row in sorted(rows, key=lambda r: (str(r["filename"]), int(r["location"]["row"]), str(r["code"]))):
		path = relative(Path(str(row["filename"])))
		line, code = int(row["location"]["row"]), str(row["code"])
		key, value = ruff_key(row, path)
		entries = measured.setdefault(path, {})
		entries[key] = max(entries.get(key, 0), value) if code in RATCHET_CODES else entries.get(key, 0) + 1
		known = remaining.get(path, {})
		message = f"{code} {row['message']}"
		if code in RATCHET_CODES:
			if key in known and value <= known[key]:
				findings.append(Finding(CHECK, "QUALITY-BASELINE", "review", path, line, f"{message} (recorded limit {known[key]})"))
			else:
				grown = f"; recorded {known[key]}" if key in known else "; new"
				findings.append(Finding(CHECK, "QUALITY-COMPLEXITY", "error", path, line, f"{message}{grown}"))
		elif not is_strict(path) and known.get(key, 0) > 0:
			known[key] -= 1
			findings.append(Finding(CHECK, "QUALITY-BASELINE", "review", path, line, message))
		else:
			findings.append(Finding(CHECK, "QUALITY-RUFF", "error", path, line, message))
	return findings, measured


def main() -> int:
	parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
	parser.add_argument("--json", type=Path, help="also write the findings as JSON")
	parser.add_argument("--write-baseline", action="store_true", help="record the current findings; refused while errors remain")
	add_arguments(parser)
	arguments = parser.parse_args()
	paths = requested_paths(arguments)
	if arguments.write_baseline and paths:
		parser.error("--write-baseline needs the whole tree; omit --paths")
	baseline: Dict[str, Dict[str, int]] = json.loads(BASELINE.read_text(encoding="utf-8"))["entries"] if BASELINE.is_file() else {}
	baseline = {path: {normalise_key(key): value for key, value in entries.items()} for path, entries in baseline.items()}
	try:
		rows = ruff_findings(paths)
		findings, measured = evaluate(rows, baseline)
		findings += mypy_findings(paths)
	except ToolUnavailable as error:
		print(f"{CHECK}: could not run: {error}", file=sys.stderr)
		return 2
	if paths:
		findings = [f for f in findings if PathFilter(paths).matches(f.path)]
	findings.sort(key=lambda f: (f.path, f.line, f.rule, f.message))
	if arguments.write_baseline:
		# The first baseline records every older finding, including strict files' complex functions;
		# after that, and always for strict defects and type errors, an error blocks the write.
		blocking = [f for f in findings if f.level == "error" and (BASELINE.is_file() or f.rule == "QUALITY-TYPE"
			or (is_strict(f.path) and f.rule != "QUALITY-COMPLEXITY"))]
		if blocking:
			print_findings(CHECK, blocking)
			print(f"{CHECK}: baseline not written; fix the errors above first")
			return 1
		recorded = {path: entries for path, entries in sorted(measured.items()) if not is_strict(path) or
			any(key.split(" ", 1)[0] in RATCHET_CODES for key in entries)}
		recorded = {path: {k: v for k, v in sorted(entries.items()) if not is_strict(path) or k.split(" ", 1)[0] in RATCHET_CODES}
			for path, entries in recorded.items()}
		BASELINE.write_text(json.dumps({"ruff": RUFF, "entries": recorded}, indent=1, sort_keys=True) + "\n", encoding="utf-8")
		print(f"{CHECK}: wrote {relative(BASELINE)} with {sum(len(v) for v in recorded.values())} entries")
		return 0
	print_findings(CHECK, findings)
	if arguments.json:
		merge_json(arguments.json, findings, LEVELS)
	return exit_code(findings, arguments.fail_on)


if __name__ == "__main__":
	raise SystemExit(main())
