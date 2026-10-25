#!/usr/bin/env python3
"""Single read-only entry point for the repository checks.

	python -B .tools/check.py quick                      # changed and untracked paths from git
	python -B .tools/check.py quick --paths events/x.txt localisation/english/x.yml
	python -B .tools/check.py full                       # whole repository
	python -B .tools/check.py full --json .tmp/checks/full.json
	python -B .tools/check.py doctor                     # what the checks need on this machine, and how to fix it
	python -B .tools/check.py setup                      # install what is missing, run the synchronizers, then doctor

`quick` runs only the checks whose inputs the changed paths can affect and reports only
findings located in those paths. `full` runs every check over the whole repository. Both print
errors one per line (`path:line: level RULE message`), then one summary line per check;
`quick` and `--verbose` also print warnings. Review candidates are counted on the console and
listed only in the `--json` report.

Exit codes: 0 no errors, 1 errors found, 2 a check could not run or the arguments were invalid.
The command never edits tracked files; the checks it starts write only to temporary folders and
to the `--json` destination.

Checks (rule ids and levels are defined by each tool; see `.tools/lib/report.py`):

- localisation     `audits/audit_localisation_static.py`   localisation integrity and key wiring
- asset-wiring     `audits/audit_asset_wiring_static.py`   sprite, texture and implicit GFX lookups
- script-rules     `audits/audit_script_rules.py`          `<=`/`>=`, unary minus, scripted-localisation format codes
- gfx              `gfx/gfx.py audit`                      frame strips, flag ladder, achievement size, runtime binaries,
                   profiled icon families and report-image provenance
- guidance         `sync/check_guidance_size.py`           single-read ceiling for instructions, skills and agents
- generators       `--check` modes of the synchronizers    AGENTS.md, agent definitions and skill copies
- tests            maintained tests in `.tools/` and in skill `tools/tests/` folders (full, or quick when they change)
- quality          `quality.py`                            ruff defects, complexity ratchet and mypy --strict for the
                   tooling (skipped with a notice when uv is not installed)
- script-validate  `audits/validate_scripts_mcp.py`        HOI4 Agent Tools script validation of changed files (quick
                   only; skipped with a notice when the MCP server cannot start)

The localisation, asset-wiring and gfx checks read the installed game, found through `HOI4_GAME_DIR`,
`.tools/local_settings.json` or the Steam libraries (`.tools/lib/game.py`); without it they exit 2.
`doctor` reports the game folder with every other requirement.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Callable, List, NamedTuple, Optional, Sequence, Set, Tuple

from lib import doctor, setup
from lib.report import LEVELS, Finding, format_finding, relative, to_json

REPO_ROOT = Path(__file__).resolve().parents[1]
TOOLS = REPO_ROOT / ".tools"
TEST_TIMEOUT_SECONDS = 600
AUDIT_TIMEOUT_SECONDS = 900

# Maintained unittest files; each runs through `unittest discover` in its own folder.
TEST_PATTERNS = (
	".tools/tests/test_*.py",
	".tools/gfx/test_*.py",
	".claude/skills/*/tools/tests/test_*.py",
	".claude/skills/*/tests/test_*.py",
)


class Check(NamedTuple):
	name: str
	inputs: Tuple[str, ...]  # path prefixes (folders end in `/`) whose change makes `quick` run the check
	quick: bool
	run: Callable[[Optional[List[str]]], Tuple[List[Finding], Optional[str]]]


Runner = Callable[[Optional[List[str]]], Tuple[List[Finding], Optional[str]]]


def run_report_tool(name: str, script: str, extra: Sequence[str] = (), optional: bool = False) -> Runner:
	"""Run a tool that writes the shared `findings` JSON and return its findings.

	`extra` arguments come first, so a subcommand such as `gfx.py audit` works. An `optional`
	tool that exits 2 (its service is unavailable) is reported as skipped instead of failing.
	"""

	def runner(paths: Optional[List[str]]) -> Tuple[List[Finding], Optional[str]]:
		with tempfile.TemporaryDirectory(prefix="hoi4_check_") as folder:
			destination = Path(folder) / "report.json"
			command = [sys.executable, "-B", str(TOOLS / script), *extra, "--json", str(destination), "--fail-on", "none"]
			if paths:
				# A path list can exceed the Windows command-line limit, so it travels in a file.
				listing = Path(folder) / "paths.txt"
				listing.write_text("\n".join(paths), encoding="utf-8")
				command += ["--paths-from", str(listing)]
			try:
				completed = subprocess.run(command, cwd=REPO_ROOT, capture_output=True, text=True,
					encoding="utf-8", errors="replace", timeout=AUDIT_TIMEOUT_SECONDS)
			except subprocess.TimeoutExpired:
				return [], f"{script} timed out after {AUDIT_TIMEOUT_SECONDS} s"
			if completed.returncode != 0 or not destination.exists():
				tail = (completed.stderr or completed.stdout).strip().splitlines()[-3:]
				if optional and completed.returncode == 2:
					print(f"{name}: skipped: {' | '.join(tail)}")
					return [], None
				return [], f"{script} exited {completed.returncode}: {' | '.join(tail)}"
			payload = json.loads(destination.read_text(encoding="utf-8"))
		return [Finding(**row) for row in payload.get("findings", [])], None

	return runner


def run_guidance(paths: Optional[List[str]]) -> Tuple[List[Finding], Optional[str]]:
	"""Map `check_guidance_size.py` output onto findings."""
	completed = subprocess.run([sys.executable, "-B", str(TOOLS / "sync" / "check_guidance_size.py")],
		cwd=REPO_ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
	findings = []
	for line in completed.stdout.splitlines():
		over = re.match(r"OVER: (.+?) is ([\d,]+) bytes .*the limit is ([\d,]+) bytes", line)
		if over:
			findings.append(Finding("guidance", "GUIDE-SIZE", "error", relative(over.group(1)), 0,
				f"{over.group(2)} bytes exceeds the {over.group(3)}-byte ceiling in .tools/sync/read_limits.json"))
	if completed.returncode not in (0, 1) or (completed.returncode == 1 and not findings):
		tail = (completed.stderr or completed.stdout).strip().splitlines()[-3:]
		return findings, f"check_guidance_size.py exited {completed.returncode}: {' | '.join(tail)}"
	return findings, None


class Generator(NamedTuple):
	name: str
	command: Tuple[str, ...]
	inputs: Tuple[str, ...]  # sources and generated outputs; the first is the finding location when the check fails
	sources: Tuple[str, ...]  # canonical sources; a mod that has none of them has nothing to project


# Generated files must equal what their generator writes from the current sources.
GENERATORS = (
	Generator("AGENTS.md instruction", (".tools/sync/sync_instructions.py", "--check"),
		("CLAUDE.md", "AGENTS.md", "CLAUDE_template.md", "AGENTS_template.md", ".tools/sync/"), ("CLAUDE.md", "CLAUDE_template.md")),
	Generator("agent definitions", (".tools/sync/sync_agents.py", "--check"),
		(".claude/agents/", ".tools/sync/", ".codex/", ".cursor/", ".qoder/", ".opencode/"), (".claude/agents",)),
	Generator("skill copies", (".tools/sync/sync_skills.py", "--check"),
		(".claude/skills/", ".tools/sync/", ".agents/", ".qoder/"), (".claude/skills",)),
)


def run_one_generator(generator: Generator) -> List[Finding]:
	completed = subprocess.run([sys.executable, "-B", *generator.command], cwd=REPO_ROOT, capture_output=True, text=True,
		encoding="utf-8", errors="replace", timeout=AUDIT_TIMEOUT_SECONDS)
	if completed.returncode == 0:
		return []
	lines = [line.strip() for line in (completed.stdout + completed.stderr).splitlines() if line.strip()]
	drift = [line for line in lines if line.startswith(("DRIFT", "Would update", "STALE"))] or lines[-1:] or ["no output"]
	return [Finding("generators", "GEN-STALE", "error", generator.inputs[0], 0,
		f"the {generator.name} projection is out of date ({detail}); rerun `python {generator.command[0]}`") for detail in drift]


def run_generators(paths: Optional[List[str]]) -> Tuple[List[Finding], Optional[str]]:
	# A changed tool can change any generator's output, so `.tools/` changes rerun them all.
	everything = not paths or any(p.startswith(".tools/") for p in paths)
	chosen = [g for g in GENERATORS if (TOOLS / Path(g.command[0]).relative_to(".tools")).is_file()
		and any((REPO_ROOT / source).exists() for source in g.sources)
		and (everything or any(p.startswith(i) for p in paths or () for i in g.inputs))]
	with ThreadPoolExecutor(max_workers=max(1, len(chosen))) as pool:
		results = list(pool.map(run_one_generator, chosen))
	return [finding for found in results for finding in found], None


def discover_tests() -> List[str]:
	found: Set[str] = set()
	for pattern in TEST_PATTERNS:
		found.update(path.relative_to(REPO_ROOT).as_posix() for path in REPO_ROOT.glob(pattern) if path.is_file())
	return sorted(found)


def run_one_test(test: str) -> Optional[Finding]:
	folder, name = test.rsplit("/", 1)
	command = [sys.executable, "-B", "-m", "unittest", "discover", "-s", folder, "-p", name]
	try:
		completed = subprocess.run(command, cwd=REPO_ROOT, capture_output=True, text=True,
			encoding="utf-8", errors="replace", timeout=TEST_TIMEOUT_SECONDS)
	except subprocess.TimeoutExpired:
		return Finding("tests", "TEST-TIMEOUT", "error", test, 0, f"did not finish within {TEST_TIMEOUT_SECONDS} s")
	if completed.returncode == 0:
		return None
	lines = [line for line in (completed.stderr + completed.stdout).strip().splitlines() if line.strip()]
	return Finding("tests", "TEST-FAILED", "error", test, 0, f"exit {completed.returncode}: {lines[-1].strip() if lines else 'no output'}")


def run_tests(paths: Optional[List[str]]) -> Tuple[List[Finding], Optional[str]]:
	tests = discover_tests()
	with ThreadPoolExecutor(max_workers=min(8, os.cpu_count() or 2)) as pool:
		results = list(pool.map(run_one_test, tests))
	return [finding for finding in results if finding], None


CHECKS = (
	Check("localisation", ("localisation/", "events/", "common/", "interface/", "history/", "map/"), True,
		run_report_tool("localisation", "audits/audit_localisation_static.py")),
	Check("asset-wiring", ("gfx/", "interface/", "common/", "events/", "history/", "localisation/"), True,
		run_report_tool("asset-wiring", "audits/audit_asset_wiring_static.py")),
	Check("script-rules", ("common/", "events/", "history/"), True,
		run_report_tool("script-rules", "audits/audit_script_rules.py")),
	Check("gfx", ("gfx/", "interface/", "sound/", "music/"), True,
		run_report_tool("gfx", "gfx/gfx.py", ("audit",))),
	Check("guidance", ("CLAUDE.md", "AGENTS.md", "CLAUDE_template.md", "AGENTS_template.md", ".claude/", ".tools/sync/"), True,
		run_guidance),
	Check("generators", tuple(sorted({i for g in GENERATORS for i in g.inputs} | {".tools/"})), True, run_generators),
	Check("tests", (".tools/", ".claude/skills/"), True, run_tests),
	# Ruff and mypy through uvx; skipped with a notice when uv is not installed.
	Check("quality", (".tools/", ".claude/skills/"), True,
		run_report_tool("quality", "quality.py", optional=True)),
	# Changed-file validation through the HOI4 Agent Tools MCP server; quick only, because a
	# whole-repository pass would validate thousands of files one call at a time.
	Check("script-validate", ("common/", "events/", "history/"), True,
		run_report_tool("script-validate", "audits/validate_scripts_mcp.py", optional=True)),
)
QUICK_ONLY = {"script-validate"}


def changed_paths() -> List[str]:
	"""Return changed, staged and untracked paths reported by git."""
	completed = subprocess.run(["git", "status", "--porcelain", "--untracked-files=all", "-z"], cwd=REPO_ROOT,
		capture_output=True, check=True)
	paths = []
	entries = completed.stdout.decode("utf-8", errors="replace").split("\0")
	index = 0
	while index < len(entries):
		entry = entries[index]
		index += 1
		if len(entry) < 4:
			continue
		paths.append(entry[3:])
		if entry[0] in "RC":
			index += 1  # the rename source follows as its own entry
	return sorted(set(paths))


def selected_checks(mode: str, paths: Sequence[str], only: Optional[Sequence[str]]) -> List[Check]:
	chosen = []
	for check in CHECKS:
		if only and check.name not in only:
			continue
		if mode == "full":
			if check.name not in QUICK_ONLY:
				chosen.append(check)
		elif check.quick and any(path.startswith(prefix) for path in paths for prefix in check.inputs):
			chosen.append(check)
	return chosen


def requested(arguments: argparse.Namespace) -> List[str]:
	"""Return the paths a quick run checks (given or changed in git); a full run checks everything."""
	if arguments.mode != "quick":
		return []
	return [relative(path) for path in arguments.paths] if arguments.paths else changed_paths()


def print_report(checks: Sequence[Check], outcomes: Sequence[Tuple[List[Finding], Optional[str]]],
		all_findings: List[Finding], failures: List[str], shown: Tuple[str, ...]) -> None:
	"""Print the shown findings, one summary line per check, and every check that could not run."""
	for finding in sorted(all_findings, key=lambda f: (f.path, f.line, f.rule, f.message)):
		if finding.level in shown:
			print(format_finding(finding))
	for check, (findings, _) in zip(checks, outcomes):
		counts = {level: sum(1 for f in findings if f.level == level) for level in LEVELS}
		print(f"{check.name}: " + ", ".join(f"{counts[level]} {level}" for level in LEVELS))
	for failure in failures:
		print(failure)
	if failures:
		print("Run `python -B .tools/check.py setup` to install and configure what this machine is missing (`doctor` only reports it).")


def main() -> int:
	relaunched = setup.relaunch_in_project_venv(REPO_ROOT, sys.argv)
	if relaunched is not None:
		return relaunched
	parser = argparse.ArgumentParser(description=(__doc__ or "").split("\n\n")[0])
	parser.add_argument("mode", choices=("quick", "full", "doctor", "setup"))
	parser.add_argument("--paths", nargs="+", metavar="PATH", help="quick: check these paths instead of the git changes")
	parser.add_argument("--only", nargs="+", choices=[check.name for check in CHECKS], help="run only these checks")
	parser.add_argument("--json", type=Path, help="write every finding, including review candidates, to this file")
	parser.add_argument("--verbose", action="store_true", help="also print warnings in full mode")
	parser.add_argument("--save-game-dir", type=Path, metavar="FOLDER", help="doctor, setup: record this machine's game folder")
	parser.add_argument("--no-install", action="store_true", help="setup: report missing Python packages instead of installing them")
	arguments = parser.parse_args()

	if arguments.mode == "doctor":
		return doctor.run(REPO_ROOT, (), arguments.save_game_dir)
	if arguments.mode == "setup":
		return setup.run(REPO_ROOT, arguments.save_game_dir, not arguments.no_install)

	if arguments.mode == "full" and arguments.paths:
		parser.error("--paths applies to quick mode only")
	paths = requested(arguments)
	if arguments.mode == "quick" and not paths:
		print("quick: no changed paths")
		return 0
	checks = selected_checks(arguments.mode, paths, arguments.only)
	if not checks:
		print(f"quick: no check reads the {len(paths)} changed path(s)")
		return 0

	report_paths = paths or None

	def run_check(check: Check) -> Tuple[List[Finding], Optional[str]]:
		try:
			return check.run(None if check.name == "tests" else report_paths)
		except Exception as error:  # noqa: BLE001 - a crashing check is reported as "could not run" (exit 2)
			return [], f"{type(error).__name__}: {error}"

	with ThreadPoolExecutor(max_workers=len(checks)) as pool:
		outcomes = list(pool.map(run_check, checks))

	all_findings: List[Finding] = []
	failures: List[str] = []
	# Tests, guidance limits and projections are repository-wide contracts, so their findings are never path-filtered.
	for check, (findings, failure) in zip(checks, outcomes):
		all_findings.extend(findings)
		if failure:
			failures.append(f"{check.name}: could not run: {failure}")

	shown = ("error", "warning") if arguments.mode == "quick" or arguments.verbose else ("error",)
	print_report(checks, outcomes, all_findings, failures, shown)

	if arguments.json:
		arguments.json.parent.mkdir(parents=True, exist_ok=True)
		arguments.json.write_text(json.dumps({
			"mode": arguments.mode,
			"paths": paths,
			"checks": [check.name for check in checks],
			"failures": failures,
			"findings": to_json(sorted(all_findings, key=lambda f: (f.check, f.path, f.line, f.rule, f.message))),
		}, indent=2, sort_keys=True), encoding="utf-8")
	if failures:
		return 2
	return 1 if any(finding.level == "error" for finding in all_findings) else 0


if __name__ == "__main__":
	raise SystemExit(main())
