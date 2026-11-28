#!/usr/bin/env python3
"""End-to-end benchmark of the new-mod flow: one-line prompts, each built in a fresh copy of a Setup-made mod.

	python scripts/benchmark_new_mod.py --template <fresh mod folder> --prompts prompts.json --out <run folder>
	python scripts/benchmark_new_mod.py ... --model sonnet --turns 40 --game-check "<command with {mod}>"
	python scripts/benchmark_new_mod.py --report <run folder>        # summarise an earlier run again

`--template` is a mod folder exactly as HOI4 Mod Setup's "Create new mod" leaves it (a Git repository with the kit
installed). The template is never changed: each prompt gets its own copy under `--out`, so every run starts from the
same state.

`prompts.json` lists the prompts and the user's scripted replies:

	{"prompts": [{"id": "atlantis", "prompt": "Create an Atlantis mod."},
	             {"id": "hansa", "prompt": "Make a mod where the Hanseatic League comes back as a Baltic power."}],
	 "replies": ["Use your suggestions."],
	 "continue": "Continue building."}

For each prompt the runner sends the prompt, then each reply in turn, then `continue` until the gate passes, the
ledger is paused, or `--sessions` sessions have run. Every turn starts a new headless session that resumes the last
one (`--resume`), the way a user returns, so the ledger's session routine is exercised. The client is Claude Code
(`claude -p`) by default; `--client` takes another command template with `{prompt}`, `{model}`, `{turns}` and
`{resume}` placeholders, which is also how the tests run it without a model. The default client skips permission prompts, so run it only on these disposable copies, never on a real mod.

After the last session the runner reads only files, never the transcript's claims: the brief, decisions, canon and
ledger in `docs/mod/`, `check.py gate` (exit code and problems), `check.py quick` (an exit of 2, a check that cannot run here, is a limit and not a failure), the Git log, and, when
`--game-check` is given, that command's exit code and output (for example an in-game smoke test on a test copy of the
game). It writes `report.json` and `report.md` under `--out`. A gate that passes with a smoke test record, a clean
`check.py`, and a passing game check is a pass for that prompt; everything else is reported with its reason.

Exit codes: 0 every prompt passed, 1 at least one did not, 2 the run could not start.
"""

from __future__ import annotations

import argparse
import json
import shlex
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

DEFAULT_CLIENT = "claude -p {prompt} --model {model} --max-turns {turns} --output-format json --permission-mode bypassPermissions {resume}"
MOD_FILES = ("brief.md", "decisions.md", "canon.md", "ledger.json", "progress.md")
SESSION_TIMEOUT = 4 * 3600


def run(command: Sequence[str], cwd: Path, timeout: int = 1800, stdin: str = "") -> subprocess.CompletedProcess:
	return subprocess.run(list(command), cwd=cwd, input=stdin, capture_output=True, text=True, encoding="utf-8",
		errors="replace", timeout=timeout)


def client_command(template: str, prompt: str, model: str, turns: int, session: Optional[str]) -> List[str]:
	parts = []
	for token in shlex.split(template, posix=True):
		if token == "{resume}":
			parts += ["--resume", session] if session else []
		else:
			parts.append(token.replace("{prompt}", prompt).replace("{model}", model).replace("{turns}", str(turns)))
	return parts


def session_id(stdout: str) -> Optional[str]:
	"""Read the session id from the client's JSON result (the last JSON object it printed)."""
	for line in reversed(stdout.strip().splitlines()):
		try:
			data = json.loads(line)
		except ValueError:
			continue
		if isinstance(data, dict) and data.get("session_id"):
			return str(data["session_id"])
	return None


def gate(mod: Path) -> Dict[str, Any]:
	completed = run([sys.executable, "-B", ".tools/check.py", "gate"], mod, timeout=3600)
	return {"exit": completed.returncode, "output": (completed.stdout + completed.stderr).strip().splitlines()[-40:]}


def ledger_state(mod: Path) -> Dict[str, Any]:
	path = mod / "docs" / "mod" / "ledger.json"
	try:
		data = json.loads(path.read_text(encoding="utf-8-sig"))
	except (OSError, ValueError):
		return {"exists": path.is_file(), "readable": False}
	rows = [row for row in data.get("features", []) if isinstance(row, dict)]
	live = data.get("live_testing") if isinstance(data.get("live_testing"), dict) else {}
	return {
		"exists": True, "readable": True, "state": data.get("state"),
		"features": len(rows), "passed": sum(1 for row in rows if row.get("passes") is True),
		"blocked": [{"id": row.get("id"), **row["blocker"]} for row in rows if row.get("passes") is not True and isinstance(row.get("blocker"), dict)],
		"phases": [str(row.get("id")) for row in (data.get("scope") or {}).get("phases", []) if isinstance(row, dict)],
		"surfaces": (data.get("scope") or {}).get("surfaces", []),
		"live_testing": {key: live.get(key) for key in ("run", "how", "when")},
		"smoke_passed": isinstance(live.get("smoke"), dict) and live["smoke"].get("passes") is True,
	}


def measure(mod: Path, game_check: Optional[str]) -> Dict[str, Any]:
	"""Everything the verdict uses, read from the mod's files and the checks."""
	result: Dict[str, Any] = {
		"files": {name: (mod / "docs" / "mod" / name).is_file() for name in MOD_FILES},
		"ledger": ledger_state(mod),
		"gate": gate(mod),
		"quick": run([sys.executable, "-B", ".tools/check.py", "quick"], mod, timeout=3600).returncode,
		"commits": len(run(["git", "log", "--oneline"], mod).stdout.splitlines()),
	}
	if game_check:
		completed = run(shlex.split(game_check.replace("{mod}", str(mod))), mod, timeout=3 * 3600)
		result["game_check"] = {"exit": completed.returncode, "output": (completed.stdout + completed.stderr).strip().splitlines()[-30:]}
	return result


def verdict(measured: Dict[str, Any], game_check: bool) -> List[str]:
	"""Why a prompt did not pass; an empty list is a pass."""
	reasons = [f"docs/mod/{name} missing" for name, present in measured["files"].items() if not present]
	ledger = measured["ledger"]
	if not ledger.get("readable"):
		reasons.append("no readable ledger")
	elif ledger.get("state") not in ("building", "complete"):
		reasons.append(f"ledger state is {ledger.get('state')}")
	if measured["gate"]["exit"] != 0:
		reasons.append(f"gate exit {measured['gate']['exit']}")
	if measured["quick"] == 1:
		reasons.append("check.py quick found errors")
	if ledger.get("live_testing", {}).get("run") not in ("no", None) and not ledger.get("smoke_passed"):
		reasons.append("in-game smoke test not recorded")
	if game_check and measured.get("game_check", {}).get("exit") != 0:
		reasons.append("game check failed")
	return reasons


def run_prompt(entry: Dict[str, str], config: Dict[str, Any], arguments: argparse.Namespace) -> Dict[str, Any]:
	mod = arguments.out / entry["id"] / "mod"
	if mod.exists():
		shutil.rmtree(mod)
	shutil.copytree(arguments.template, mod, symlinks=True)
	messages = [entry["prompt"], *config.get("replies", [])]
	session: Optional[str] = None
	log: List[Dict[str, Any]] = []
	for number in range(arguments.sessions):
		message = messages[number] if number < len(messages) else config.get("continue", "Continue building.")
		started = time.time()
		command = client_command(arguments.client, message, arguments.model, arguments.turns, session)
		try:
			completed = run(command, mod, timeout=SESSION_TIMEOUT)
			code, stdout, stderr = completed.returncode, completed.stdout, completed.stderr
		except subprocess.TimeoutExpired:
			code, stdout, stderr = -1, "", "session timed out"
		session = session_id(stdout) or session
		(arguments.out / entry["id"] / f"session-{number + 1}.out").write_text(stdout + "\n--- stderr\n" + stderr, encoding="utf-8")
		log.append({"session": number + 1, "message": message, "exit": code, "seconds": round(time.time() - started)})
		state = ledger_state(mod)
		if number + 1 >= len(messages) and (state.get("state") in ("paused", "complete") or gate(mod)["exit"] == 0):
			break
	measured = measure(mod, arguments.game_check)
	reasons = verdict(measured, bool(arguments.game_check))
	return {"id": entry["id"], "prompt": entry["prompt"], "model": arguments.model, "sessions": log,
		"measured": measured, "passed": not reasons, "reasons": reasons}


def write_report(out: Path, results: List[Dict[str, Any]]) -> int:
	(out / "report.json").write_text(json.dumps({"results": results}, indent=2), encoding="utf-8")
	lines = ["# New-mod benchmark", "", "| Prompt | Model | Sessions | Features passed | Gate | Result |", "| --- | --- | --- | --- | --- | --- |"]
	for row in results:
		ledger = row["measured"]["ledger"]
		lines.append(f"| {row['id']} | {row['model']} | {len(row['sessions'])} | {ledger.get('passed', 0)} of {ledger.get('features', 0)} | "
			f"exit {row['measured']['gate']['exit']} | {'pass' if row['passed'] else 'fail: ' + '; '.join(row['reasons'])} |")
	(out / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
	print("\n".join(lines))
	return 0 if results and all(row["passed"] for row in results) else 1


def main(argv: Optional[Sequence[str]] = None) -> int:
	parser = argparse.ArgumentParser(description=(__doc__ or "").split("\n\n")[0])
	parser.add_argument("--template", type=Path, help="a fresh mod folder made by HOI4 Mod Setup (never changed)")
	parser.add_argument("--prompts", type=Path, help="JSON file with prompts, replies and the continue message")
	parser.add_argument("--out", type=Path, help="run folder; each prompt gets <out>/<id>/mod")
	parser.add_argument("--model", default="sonnet", help="model alias passed to the client (default sonnet)")
	parser.add_argument("--turns", type=int, default=60, help="agent turns per session (default 60)")
	parser.add_argument("--sessions", type=int, default=8, help="sessions per prompt at most (default 8)")
	parser.add_argument("--client", default=DEFAULT_CLIENT, help="client command template")
	parser.add_argument("--game-check", help="command run after the build, {mod} is the mod folder; exit 0 is a pass")
	parser.add_argument("--only", nargs="+", help="run only these prompt ids")
	parser.add_argument("--report", type=Path, metavar="RUN", help="summarise an earlier run folder again")
	arguments = parser.parse_args(argv)
	if arguments.report:
		data = json.loads((arguments.report / "report.json").read_text(encoding="utf-8"))
		return write_report(arguments.report, data["results"])
	if not (arguments.template and arguments.prompts and arguments.out):
		parser.error("--template, --prompts and --out are required")
	if not (arguments.template / ".tools" / "check.py").is_file():
		print(f"{arguments.template} is not a mod with the kit installed (.tools/check.py is missing)", file=sys.stderr)
		return 2
	config = json.loads(arguments.prompts.read_text(encoding="utf-8"))
	prompts = [entry for entry in config.get("prompts", []) if not arguments.only or entry["id"] in arguments.only]
	if not prompts:
		print("no prompts to run", file=sys.stderr)
		return 2
	arguments.out.mkdir(parents=True, exist_ok=True)
	results = [run_prompt(entry, config, arguments) for entry in prompts]
	return write_report(arguments.out, results)


if __name__ == "__main__":
	raise SystemExit(main())
