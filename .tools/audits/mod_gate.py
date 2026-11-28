#!/usr/bin/env python3
"""Mod ledger and completion gate: decide from files, not from the agent's word, whether a mod build may stop.

	python -B .tools/check.py gate                    # report; exit 0 may stop, 1 work is open, 2 the ledger is unreadable
	python -B .tools/check.py gate --next             # the session-start routine: progress, the next feature, the baseline check
	python -B .tools/check.py gate --wait "question"  # the agent asked the user something; the next stop is allowed
	python -B .tools/check.py gate --pause "reason"   # the user said stop; the gate stays open until --resume
	python -B .tools/check.py gate --resume
	python -B .tools/check.py gate --hook stop|session-start|prompt   # Claude Code hook adapters (stdin: the hook's JSON)

The ledger is `docs/mod/ledger.json` (schema `hoi4-mod-ledger/1`, documented in the `hoi4-new-mod` skill). Without it
every command exits 0 and the hooks print nothing, so a mod that never planned a whole-mod build is untouched.
While the ledger's `state` is `building`, the gate fails when:

- the ledger breaks its schema: a bad or duplicate id, a dependency that does not exist or forms a cycle;
- a surface the build plan names (`scope.surfaces`) has no feature whose `surfaces` include it;
- a feature names no phase of `scope.phases`, or passes while a feature of an earlier phase is still open;
- a feature is open: `passes` is false and it has no recorded `blocker`;
- a feature passes without evidence: no `evidence` path, a path that does not exist, a dependency that has not passed,
  or one of its machine `checks` (`exists`, `contains`, `count`) failing;
- a mod text file still carries a placeholder marker (TODO, FIXME, TBD or PLACEHOLDER in a script comment or a
  localisation value, lorem ipsum, or a localisation value that only repeats its key), outside the paths the ledger
  lists under `placeholders_allowed` with a reason;
- `check.py quick` finds an error in the changed files;
- every feature has passed but `check.py full --only localisation asset-wiring script-rules gui-rules` finds an error.

A check that cannot run on this machine (exit 2, for example no game folder) limits what was verified and is reported,
but never fails the gate by itself. The Stop hook is capped: after `gate.max_idle_blocks` blocks in a row with no change
to the ledger or the working tree (default 3), or `gate.max_blocks` blocks in one session (default 30), it lets the stop
through and says why. `HOI4_MOD_GATE=off` in the environment turns the hooks off.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, NamedTuple, Optional, Sequence, Set, Tuple

REPO_ROOT = Path(__file__).resolve().parents[2]
LEDGER = Path("docs/mod/ledger.json")
PROGRESS = Path("docs/mod/progress.md")
STATE = Path(".tmp/mod-gate/state.json")
SCHEMA = "hoi4-mod-ledger/1"
STATES = ("planning", "building", "paused", "complete")
BLOCKER_NEEDS = ("user", "credential", "money", "access", "in_game", "tool")
CHECK_KINDS = ("exists", "contains", "count")
DEFAULT_MAX_BLOCKS = 30
DEFAULT_MAX_IDLE = 3
QUICK_TIMEOUT = 900
FULL_TIMEOUT = 1800
FINAL_CHECKS = ("localisation", "asset-wiring", "script-rules", "gui-rules")
MOD_TEXT_DIRS = ("common", "events", "history", "localisation", "interface", "map")
MOD_TEXT_SUFFIXES = (".txt", ".yml", ".gui", ".gfx", ".asset")
SCRIPT_MARKER = re.compile(r"#.*\b(TODO|FIXME|TBD|PLACEHOLDER)\b")
LOC_LINE = re.compile(r'^\s*([A-Za-z0-9_.\-]+):\d*\s*"(.*)"\s*(#.*)?$')
LOC_MARKER = re.compile(r"\b(TODO|FIXME|TBD|PLACEHOLDER)\b|lorem ipsum", re.IGNORECASE)
ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_-]*$")
GLOB_CHARS = "*?["

Ledger = Dict[str, Any]


class Gate(NamedTuple):
	"""One evaluation: `problems` fail the gate, `notes` limit or explain it."""

	active: bool
	problems: List[str]
	notes: List[str]
	ledger: Optional[Ledger]


def now() -> str:
	return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_ledger(root: Path) -> Tuple[Optional[Ledger], Optional[str]]:
	"""Return the ledger, or None when there is none; the second value is a read or parse error."""
	path = root / LEDGER
	if not path.is_file():
		return None, None
	try:
		data = json.loads(path.read_text(encoding="utf-8-sig"))
	except (OSError, ValueError) as error:
		return None, f"{LEDGER.as_posix()} cannot be read: {error}"
	if not isinstance(data, dict):
		return None, f"{LEDGER.as_posix()} must hold one JSON object"
	return data, None


def save_ledger(root: Path, ledger: Ledger) -> None:
	(root / LEDGER).write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def features_of(ledger: Ledger) -> List[Dict[str, Any]]:
	rows = ledger.get("features")
	return [row for row in rows if isinstance(row, dict)] if isinstance(rows, list) else []


def dependencies(row: Dict[str, Any]) -> List[str]:
	value = row.get("depends_on", [])
	return [str(item) for item in value] if isinstance(value, list) else []


def inside(root: Path, value: Any) -> Optional[Path]:
	"""A repository-relative path inside the mod, or None for an absolute or escaping one."""
	if not isinstance(value, str) or not value.strip() or value.startswith(("/", "\\")) or Path(value).is_absolute():
		return None
	resolved = (root / value).resolve()
	try:
		resolved.relative_to(root.resolve())
	except ValueError:
		return None
	return resolved


def schema_problems(ledger: Ledger) -> List[str]:
	"""Structural rules: schema id, state, unique ids, known dependencies and no dependency cycle."""
	problems: List[str] = []
	if ledger.get("schema") != SCHEMA:
		problems.append(f"ledger: `schema` must be \"{SCHEMA}\"")
	if ledger.get("state") not in STATES:
		problems.append(f"ledger: `state` must be one of {', '.join(STATES)}")
	rows = ledger.get("features")
	if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
		return problems + ["ledger: `features` must be a list of objects"]
	ids = [str(row.get("id", "")) for row in rows]
	problems += [f"ledger: feature id `{i}` must be lower-case letters, digits, `-` or `_`" for i in ids if not ID_PATTERN.match(i)]
	problems += [f"ledger: feature id `{i}` is used more than once" for i in sorted({i for i in ids if ids.count(i) > 1})]
	for row in rows:
		if not isinstance(row.get("depends_on", []), list):
			problems.append(f"{row.get('id')}: `depends_on` must be a list of feature ids")
		problems += [f"{row.get('id')}: depends on `{d}`, which is not a feature" for d in dependencies(row) if d not in ids]
	return problems + cycle_problems(rows) + coverage_problems(ledger, rows) + phase_problems(ledger, rows)


def phase_ids(ledger: Ledger) -> List[str]:
	scope = ledger.get("scope")
	phases = scope.get("phases") if isinstance(scope, dict) else None
	return [str(row.get("id")) for row in phases if isinstance(row, dict)] if isinstance(phases, list) else []


def phase_problems(ledger: Ledger, rows: Sequence[Dict[str, Any]]) -> List[str]:
	"""Every feature names a declared phase; the core phase comes first, as the build plan's order."""
	phases = phase_ids(ledger)
	if not phases:
		return ["ledger: `scope.phases` must list the build plan's phases in order, the playable core first"]
	return [f"{row.get('id')}: `phase` must be one of {', '.join(phases)}" for row in rows if row.get("phase") not in phases]


def phase_order_problems(ledger: Ledger) -> List[str]:
	"""A later phase's feature may not pass while an earlier phase still has open, unblocked work."""
	order = {name: index for index, name in enumerate(phase_ids(ledger))}
	rows = features_of(ledger)
	open_rows = [row for row in rows if row.get("passes") is not True and not row.get("blocker")]
	problems: List[str] = []
	for row in rows:
		if row.get("passes") is not True:
			continue
		earlier = [str(other.get("id")) for other in open_rows if order.get(str(other.get("phase")), 0) < order.get(str(row.get("phase")), 0)]
		if earlier:
			problems.append(f"{row.get('id')}: passes in phase `{row.get('phase')}` while an earlier phase is open ({', '.join(earlier[:5])})")
	return problems


def coverage_problems(ledger: Ledger, rows: Sequence[Dict[str, Any]]) -> List[str]:
	"""Every surface of the scope contract belongs to at least one feature, so no promised part is left out of the plan."""
	scope = ledger.get("scope")
	wanted = scope.get("surfaces") if isinstance(scope, dict) else None
	if not isinstance(wanted, list) or not wanted:
		return ["ledger: `scope.surfaces` must list the surfaces the scope contract names (for example map, country, "
			"focus_tree, events, decisions, characters, ai, art, localisation)"]
	covered = {str(item) for row in rows if isinstance(row.get("surfaces"), list) for item in row["surfaces"]}
	return [f"ledger: scope surface `{item}` has no feature; add one whose `surfaces` include it" for item in wanted if str(item) not in covered]


def cycle_problems(rows: Sequence[Dict[str, Any]]) -> List[str]:
	graph: Dict[str, List[str]] = {}
	for row in rows:
		graph.setdefault(str(row.get("id")), []).extend(dependencies(row))
	done: Set[str] = set()
	found: List[str] = []

	def visit(node: str, trail: List[str]) -> None:
		if node in trail:
			found.append("ledger: dependency cycle " + " -> ".join(trail[trail.index(node):] + [node]))
			return
		if node in done or node not in graph:
			return
		for child in graph[node]:
			visit(child, trail + [node])
		done.add(node)

	for node in sorted(graph):
		visit(node, [])
	return found[:1]


def check_files(root: Path, pattern: str) -> List[Path]:
	if any(char in pattern for char in GLOB_CHARS):
		return sorted(path for path in root.glob(pattern) if path.is_file())
	return [root / pattern] if (root / pattern).is_file() else []


def run_machine_check(root: Path, check: Any) -> Optional[str]:
	"""Evaluate one machine check; return why it fails, or None when it holds."""
	if not isinstance(check, dict) or check.get("kind") not in CHECK_KINDS:
		return f"check {check!r} needs a `kind` of {', '.join(CHECK_KINDS)}"
	kind, pattern, need = str(check["kind"]), check.get("path"), check.get("min", 1)
	if not isinstance(pattern, str) or inside(root, pattern.split("*", 1)[0].rstrip("/") or ".") is None:
		return f"{kind} check needs a repository-relative `path`"
	if not isinstance(need, int) or need < 1:
		return f"{kind} check on `{pattern}`: `min` must be a whole number of at least 1"
	files = check_files(root, pattern)
	if kind == "exists":
		return None if len(files) >= need else f"`{pattern}` matches {len(files)} file(s), needs {need}"
	regex = check.get("regex") if isinstance(check.get("regex"), str) else re.escape(str(check.get("text", "")))
	if not regex:
		return f"{kind} check on `{pattern}` needs `text` or `regex`"
	try:
		compiled = re.compile(regex, re.MULTILINE)
	except re.error as error:
		return f"{kind} check on `{pattern}`: bad regex: {error}"
	count = sum(len(compiled.findall(path.read_text(encoding="utf-8-sig", errors="replace"))) for path in files)
	if count >= need:
		return None
	return f"`{check.get('text') or check.get('regex')}` occurs {count} time(s) in `{pattern}`, needs {need}"


def pass_problems(root: Path, row: Dict[str, Any], passed: Set[str]) -> List[str]:
	"""Why a feature marked as passed has not earned it."""
	issues: List[str] = []
	evidence = row.get("evidence")
	if not isinstance(evidence, list) or not evidence:
		issues.append("passes with no `evidence` paths; record the files that prove it, or set `passes` back to false")
	else:
		for item in evidence:
			path = inside(root, item)
			if path is None or not path.exists():
				issues.append(f"evidence `{item}` does not exist in the mod")
	issues += [f"passes before its dependency `{d}`" for d in dependencies(row) if d not in passed]
	checks = row.get("checks", [])
	for check in checks if isinstance(checks, list) else [checks]:
		failure = run_machine_check(root, check)
		if failure:
			issues.append(f"passes but its check fails: {failure}")
	return issues


def blocker_problem(blocker: Any) -> Optional[str]:
	if not isinstance(blocker, dict) or not str(blocker.get("reason", "")).strip():
		return "`blocker` needs a `reason`"
	if blocker.get("needs") not in BLOCKER_NEEDS:
		return f"`blocker.needs` must be one of {', '.join(BLOCKER_NEEDS)}"
	return None


def feature_problems(root: Path, ledger: Ledger) -> Tuple[List[str], List[str]]:
	"""Open features and passes without evidence; the second list names the recorded blockers."""
	problems: List[str] = []
	notes: List[str] = []
	rows = features_of(ledger)
	passed = {str(row.get("id")) for row in rows if row.get("passes") is True}
	for row in rows:
		name, blocker = str(row.get("id")), row.get("blocker")
		if row.get("passes") is True:
			problems += [f"{name}: {issue}" for issue in pass_problems(root, row, passed)]
		elif row.get("passes") is not False:
			problems.append(f"{name}: `passes` must be true or false")
		elif blocker:
			issue = blocker_problem(blocker)
			if issue:
				problems.append(f"{name}: {issue}")
			else:
				notes.append(f"{name}: blocked ({blocker['needs']}): {blocker['reason']}")
		else:
			problems.append(f"{name}: open ({row.get('title', 'no title')})")
	return problems, notes


def mod_text_files(root: Path) -> Iterable[Path]:
	for folder in MOD_TEXT_DIRS:
		base = root / folder
		if base.is_dir():
			yield from (path for path in sorted(base.rglob("*")) if path.is_file() and path.suffix.lower() in MOD_TEXT_SUFFIXES)


def loc_placeholder(line: str) -> bool:
	match = LOC_LINE.match(line)
	if not match:
		return False
	key, value = match.group(1), match.group(2).strip()
	return LOC_MARKER.search(value) is not None or value == key


def allowed_placeholders(ledger: Ledger) -> List[str]:
	rows = ledger.get("placeholders_allowed", [])
	return [str(row.get("path", "")) for row in rows if isinstance(row, dict) and str(row.get("reason", "")).strip()] \
		if isinstance(rows, list) else []


def placeholder_problems(root: Path, ledger: Ledger) -> List[str]:
	"""Placeholder markers left in mod text, outside the paths the ledger allows with a reason."""
	allowed = [entry for entry in allowed_placeholders(ledger) if entry]
	found: List[str] = []
	for path in mod_text_files(root):
		relative = path.relative_to(root).as_posix()
		if any(relative == entry or (entry.endswith("/") and relative.startswith(entry)) for entry in allowed):
			continue
		is_loc = path.suffix.lower() == ".yml"
		for number, line in enumerate(path.read_text(encoding="utf-8-sig", errors="replace").splitlines(), 1):
			if loc_placeholder(line) if is_loc else SCRIPT_MARKER.search(line) is not None:
				found.append(f"{relative}:{number}: placeholder left in mod text: {line.strip()[:90]}")
				if len(found) >= 25:
					return found + ["(more placeholders are not listed)"]
	return found


def git_lines(root: Path, *arguments: str) -> List[str]:
	try:
		completed = subprocess.run(["git", *arguments], cwd=root, capture_output=True, text=True, encoding="utf-8",
			errors="replace", timeout=60)
	except (OSError, subprocess.TimeoutExpired):
		return []
	return completed.stdout.splitlines() if completed.returncode == 0 else []


def fingerprint(root: Path) -> str:
	"""Changes with the ledger, the commit and the working tree, but not with the gate's own state under `.tmp/`."""
	digest = hashlib.sha256()
	ledger = root / LEDGER
	digest.update(ledger.read_bytes() if ledger.is_file() else b"")
	outside_tmp = ("--", ".", ":(exclude).tmp")
	for line in git_lines(root, "rev-parse", "HEAD") + git_lines(root, "status", "--porcelain", "--untracked-files=all", *outside_tmp) \
			+ git_lines(root, "diff", "--stat", *outside_tmp):
		digest.update(line.encode("utf-8"))
	return digest.hexdigest()


def run_check_py(root: Path, arguments: Sequence[str], timeout: int) -> Tuple[int, List[str]]:
	"""Run `check.py` and return its exit code and its last error lines (2 also when it times out)."""
	command = [sys.executable, "-B", str(root / ".tools" / "check.py"), *arguments]
	try:
		completed = subprocess.run(command, cwd=root, capture_output=True, text=True, encoding="utf-8",
			errors="replace", timeout=timeout)
	except subprocess.TimeoutExpired:
		return 2, [f"timed out after {timeout} s"]
	lines = [line for line in (completed.stdout + completed.stderr).splitlines() if line.strip()]
	if completed.returncode == 1:
		lines = [line for line in lines if ": error " in line] or lines
	return completed.returncode, lines[-20:]


def static_checks(root: Path, final: bool, state: Dict[str, Any], mark: str) -> Tuple[List[str], List[str]]:
	"""`check.py quick` on the changed files and, once every feature passed, the final full scan; cached per fingerprint."""
	problems: List[str] = []
	notes: List[str] = []
	runs: List[Tuple[str, List[str], int]] = [("quick", ["quick"], QUICK_TIMEOUT)]
	if final:
		runs.append(("final", ["full", "--only", *FINAL_CHECKS], FULL_TIMEOUT))
	cache = state.setdefault("checks", {})
	for name, arguments, timeout in runs:
		cached = cache.get(name)
		if isinstance(cached, dict) and cached.get("mark") == mark:
			code, lines = int(cached.get("code", 2)), [str(line) for line in cached.get("lines", [])]
		else:
			code, lines = run_check_py(root, arguments, timeout)
			cache[name] = {"mark": mark, "code": code, "lines": lines}
		label = "check.py " + " ".join(arguments)
		if code == 1:
			problems.append(f"{label} found errors:\n  " + "\n  ".join(lines))
		elif code != 0:
			notes.append(f"{label} could not run here, which limits what was verified: {' | '.join(lines[-3:])}")
	return problems, notes


def evaluate(root: Path, state: Optional[Dict[str, Any]] = None, run_static: bool = True) -> Gate:
	"""Evaluate the gate. It is active only while the ledger's state is `building`."""
	ledger, error = load_ledger(root)
	if error:
		return Gate(True, [error], [], None)
	if ledger is None:
		return Gate(False, [], [], None)
	if ledger.get("state") != "building":
		note = f"ledger state is `{ledger.get('state')}`"
		if ledger.get("state") == "paused":
			note += f" ({ledger.get('pause_reason') or 'no reason given'}); resume with `check.py gate --resume`"
		return Gate(False, [], [note], ledger)
	problems = schema_problems(ledger)
	if problems:
		return Gate(True, problems, [], ledger)
	if not features_of(ledger):
		return Gate(True, ["ledger: no features yet; write the feature ledger before building (hoi4-new-mod)"], [], ledger)
	open_problems, notes = feature_problems(root, ledger)
	open_problems += phase_order_problems(ledger)
	problems = open_problems + placeholder_problems(root, ledger)
	if run_static:
		static_problems, static_notes = static_checks(root, not open_problems, state if state is not None else {}, fingerprint(root))
		problems += static_problems
		notes += static_notes
	return Gate(True, problems, notes, ledger)


def next_feature(ledger: Ledger) -> Optional[Dict[str, Any]]:
	"""The first open, unblocked feature whose dependencies have all passed."""
	rows = features_of(ledger)
	passed = {str(row.get("id")) for row in rows if row.get("passes") is True}
	order = {name: index for index, name in enumerate(phase_ids(ledger))}
	for row in sorted(rows, key=lambda item: order.get(str(item.get("phase")), len(order))):
		if row.get("passes") is not True and not row.get("blocker") and all(d in passed for d in dependencies(row)):
			return row
	return None


def summary(ledger: Ledger) -> str:
	"""The session-start routine as text: where the build stands and what to do next."""
	rows = features_of(ledger)
	passed = sum(1 for row in rows if row.get("passes") is True)
	blocked = sum(1 for row in rows if row.get("passes") is not True and row.get("blocker"))
	lines = [f"Mod ledger ({LEDGER.as_posix()}): {ledger.get('mod', 'this mod')}, state `{ledger.get('state')}`, "
		f"{passed} of {len(rows)} features passed, {blocked} blocked."]
	waiting = ledger.get("awaiting_user")
	if isinstance(waiting, dict):
		lines.append(f"Waiting for the user's answer: {waiting.get('question', '')}")
	chosen = next_feature(ledger)
	if chosen:
		raw = chosen.get("acceptance")
		acceptance: List[Any] = raw if isinstance(raw, list) else []
		lines.append(f"Next feature: `{chosen.get('id')}` ({chosen.get('title', '')}). Acceptance: "
			+ ("; ".join(str(item) for item in acceptance) or "see the ledger"))
	elif ledger.get("state") == "building" and passed < len(rows):
		lines.append("No feature is ready: every open feature waits for a dependency or a blocker.")
	lines.append(f"Session routine: read {PROGRESS.as_posix()} and the ledger, run `python -B .tools/check.py quick` as the "
		"baseline, build one feature, record its evidence and progress, then run `python -B .tools/check.py gate`.")
	return "\n".join(lines)


def load_state(root: Path) -> Dict[str, Any]:
	try:
		data = json.loads((root / STATE).read_text(encoding="utf-8"))
	except (OSError, ValueError):
		return {}
	return data if isinstance(data, dict) else {}


def save_state(root: Path, state: Dict[str, Any]) -> None:
	path = root / STATE
	path.parent.mkdir(parents=True, exist_ok=True)
	path.write_text(json.dumps(state, indent=1), encoding="utf-8")


def gate_limits(ledger: Optional[Ledger]) -> Tuple[int, int]:
	settings = ledger.get("gate", {}) if ledger else {}
	settings = settings if isinstance(settings, dict) else {}
	total, idle = settings.get("max_blocks", DEFAULT_MAX_BLOCKS), settings.get("max_idle_blocks", DEFAULT_MAX_IDLE)
	return (total if isinstance(total, int) and total > 0 else DEFAULT_MAX_BLOCKS,
		idle if isinstance(idle, int) and idle > 0 else DEFAULT_MAX_IDLE)


def block_reason(gate: Gate, blocks: int, total: int) -> str:
	shown = gate.problems[:12]
	lines = [f"The mod ledger is not finished (stop blocked {blocks} of at most {total} times this session). Keep building:"]
	lines += [f"- {problem}" for problem in shown]
	if len(gate.problems) > len(shown):
		lines.append(f"- and {len(gate.problems) - len(shown)} more; run `python -B .tools/check.py gate` for the full list")
	lines += [f"- note: {note}" for note in gate.notes[:5]]
	lines.append("Build or fix the next feature and record its evidence in docs/mod/ledger.json. A true blocker (the user's "
		"decision or asset, a credential, money, access, an in-game check, a missing tool) goes into that feature's `blocker`. "
		"If you need the user's answer, run `python -B .tools/check.py gate --wait \"<question>\"`, then ask and end your turn. "
		"If the user asked you to stop, run `python -B .tools/check.py gate --pause \"<their words>\"`.")
	return "\n".join(lines)


def gate_off() -> bool:
	return os.environ.get("HOI4_MOD_GATE", "").strip().lower() in ("off", "0", "false", "no")


def hook_stop(root: Path, payload: Dict[str, Any]) -> int:
	"""Claude Code `Stop` hook: block with a reason while the gate fails, within the caps."""
	if gate_off() or not (root / LEDGER).is_file():
		return 0
	ledger, _ = load_ledger(root)
	if ledger is not None and ledger.get("awaiting_user"):
		return 0
	state = load_state(root)
	sessions = state.setdefault("sessions", {})
	record = sessions.setdefault(str(payload.get("session_id") or "unknown"), {"blocks": 0, "idle": 0, "mark": ""})
	gate = evaluate(root, state)
	if not gate.active or not gate.problems:
		record.update(blocks=0, idle=0)
		save_state(root, state)
		return 0
	total, idle_limit = gate_limits(gate.ledger)
	mark = fingerprint(root)
	record["idle"] = int(record.get("idle", 0)) + 1 if mark == record.get("mark") else 0
	record["mark"] = mark
	blocks = int(record.get("blocks", 0))
	if blocks >= total or record["idle"] >= idle_limit:
		why = f"{blocks} blocks this session" if blocks >= total else f"{record['idle']} blocks in a row with no change to the ledger or the files"
		save_state(root, state)
		print(json.dumps({"systemMessage": f"Mod completion gate: let the stop through after {why}; {len(gate.problems)} "
			"problem(s) remain. Run `python -B .tools/check.py gate` for the list and report them."}))
		return 0
	record["blocks"] = blocks + 1
	save_state(root, state)
	print(json.dumps({"decision": "block", "reason": block_reason(gate, blocks + 1, total)}))
	return 0


def hook_session_start(root: Path) -> int:
	"""Claude Code `SessionStart` hook: put the session-start routine into the context."""
	if gate_off():
		return 0
	ledger, error = load_ledger(root)
	if error:
		print(f"Mod ledger: {error}. Fix it before building.")
	elif ledger is not None:
		print(summary(ledger))
	return 0


def hook_prompt(root: Path) -> int:
	"""Claude Code `UserPromptSubmit` hook: a user message answers a waiting question and resets the Stop hook's counters."""
	ledger, _ = load_ledger(root)
	if ledger is None:
		return 0
	if ledger.pop("awaiting_user", None) is not None:
		save_ledger(root, ledger)
	state = load_state(root)
	sessions = state.get("sessions")
	if isinstance(sessions, dict) and sessions:
		for record in sessions.values():
			if isinstance(record, dict):
				record.update(blocks=0, idle=0)
		save_state(root, state)
	return 0


def set_state(root: Path, action: str, value: Optional[str]) -> int:
	"""`--wait`, `--pause` and `--resume`: change only the ledger's control fields."""
	ledger, error = load_ledger(root)
	if error or ledger is None:
		print(error or f"{LEDGER.as_posix()} does not exist; nothing to change")
		return 2
	if action == "wait":
		ledger["awaiting_user"] = {"question": value or "", "since": now()}
		message = "the next stop is allowed; the user's next message clears the wait"
	elif action == "pause":
		ledger.update(state="paused", pause_reason=value or "the user asked to stop", paused_at=now())
		message = "paused; the gate stays open until `python -B .tools/check.py gate --resume`"
	else:
		ledger["state"] = "building"
		for stale in ("pause_reason", "paused_at", "awaiting_user"):
			ledger.pop(stale, None)
		message = "building; the gate is active"
	save_ledger(root, ledger)
	print(f"{LEDGER.as_posix()}: {message}")
	return 0


def report(root: Path) -> int:
	state = load_state(root)
	gate = evaluate(root, state)
	if gate.ledger is None and not gate.problems:
		print(f"gate: no {LEDGER.as_posix()}, so there is no whole-mod build to check")
		return 0
	if gate.active:
		save_state(root, state)
	for problem in gate.problems:
		print(f"gate: {problem}")
	for note in gate.notes:
		print(f"gate: note: {note}")
	if gate.ledger is not None:
		print(summary(gate.ledger))
	if gate.ledger is None:
		return 2
	if not gate.active:
		return 0
	print(f"gate: {len(gate.problems)} problem(s)" if gate.problems else "gate: every feature passed with evidence and the checks are clean")
	return 1 if gate.problems else 0


def read_payload() -> Dict[str, Any]:
	try:
		payload = json.loads(sys.stdin.read() or "{}")
	except ValueError:
		return {}
	return payload if isinstance(payload, dict) else {}


def main(argv: Optional[Sequence[str]] = None, root: Path = REPO_ROOT) -> int:
	parser = argparse.ArgumentParser(prog="check.py gate", description=(__doc__ or "").split("\n\n")[0])
	group = parser.add_mutually_exclusive_group()
	group.add_argument("--next", action="store_true", help="print the session-start routine and the next feature")
	group.add_argument("--wait", metavar="QUESTION", help="record that the agent is waiting for the user's answer")
	group.add_argument("--pause", metavar="REASON", help="record the user's stop; the gate stays open until --resume")
	group.add_argument("--resume", action="store_true", help="make the gate active again after --pause")
	group.add_argument("--hook", choices=("stop", "session-start", "prompt"), help="Claude Code hook adapter (reads the hook JSON)")
	arguments = parser.parse_args(argv)
	if arguments.hook == "stop":
		return hook_stop(root, read_payload())
	if arguments.hook == "session-start":
		return hook_session_start(root)
	if arguments.hook == "prompt":
		read_payload()
		return hook_prompt(root)
	if arguments.next:
		ledger, error = load_ledger(root)
		print(error or (summary(ledger) if ledger is not None else f"gate: no {LEDGER.as_posix()}"))
		return 2 if error else 0
	if arguments.wait is not None:
		return set_state(root, "wait", arguments.wait)
	if arguments.pause is not None:
		return set_state(root, "pause", arguments.pause)
	if arguments.resume:
		return set_state(root, "resume", None)
	return report(root)


if __name__ == "__main__":
	raise SystemExit(main())
