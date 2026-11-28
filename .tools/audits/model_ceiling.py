#!/usr/bin/env python3
"""Model ceiling: a helper an agent starts never runs on a higher model than the one the user's chat started on.

	python -B .tools/check.py model-ceiling --hook session-start|pre-tool   # Claude Code hook adapters (stdin: the hook's JSON)
	python -B .tools/check.py model-ceiling                                  # check the shipped agents and hooks, exit 1 on a problem

The rule (D-170): subagents run on the model their task needs, new sessions, orchestrators and other helpers never start
on a higher model than the user's chat did, and a run the user started on Sonnet never escalates to Opus by itself.

- The `SessionStart` hook records the model the chat started on, once per session, in `.tmp/model-ceiling/state.json`.
- The `PreToolUse` hook (matcher `Agent|Task|Bash`) looks at what an agent is about to start. A subagent call is judged by its
  `model` argument, or by the `model` its definition in `.claude/agents/` pins; `inherit` or none is always fine. A shell
  command that starts `claude` or `codex` with `--model` or `-m` is judged by that model. A model above the recorded ceiling
  is refused with the reason and the model to use instead.
- When the chat's model is unknown (no recorded start, or a model name outside the known families) nothing is refused.
- `HOI4_MODEL_CEILING=off` in the environment turns the hook off.

Families rank haiku < sonnet < opus < fable. The check (no `--hook`) verifies that no shipped agent pins a family above
sonnet and that `.claude/settings.json` registers both hooks.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

REPO_ROOT = Path(__file__).resolve().parents[2]
STATE = Path(".tmp/model-ceiling/state.json")
AGENTS = Path(".claude/agents")
SETTINGS = Path(".claude/settings.json")
FAMILIES = ("haiku", "sonnet", "opus", "fable")
MAX_PINNED = "sonnet"
SESSION_LIMIT = 200
COMMAND = re.compile(r"(?:^|[;&|(`])\s*(?:[A-Za-z_]+=\S*\s+)*(?:\S*[\\/])?(?:claude|codex)(?:\.exe|\.cmd)?\s")
MODEL_ARGUMENT = re.compile(r"(?:--model(?:\s+|=)|\s-m\s+)[\"']?([A-Za-z0-9._:\[\]-]+)")


def rank(model: object) -> Optional[int]:
	"""The family rank of an alias or full model id (1 haiku .. 4 fable), or None for inherit and unknown names."""
	text = str(model or "").strip().lower()
	for index, family in enumerate(FAMILIES, start=1):
		if family in text:
			return index
	return None


def family(model: object) -> str:
	number = rank(model)
	return FAMILIES[number - 1] if number else str(model)


def off() -> bool:
	return os.environ.get("HOI4_MODEL_CEILING", "").strip().lower() in ("off", "0", "false", "no")


def read_payload() -> Dict[str, Any]:
	try:
		payload = json.loads(sys.stdin.read() or "{}")
	except ValueError:
		return {}
	return payload if isinstance(payload, dict) else {}


def load_state(root: Path) -> Dict[str, Any]:
	try:
		data = json.loads((root / STATE).read_text(encoding="utf-8"))
	except (OSError, ValueError):
		return {}
	return data if isinstance(data, dict) else {}


def save_state(root: Path, state: Dict[str, Any]) -> None:
	path = root / STATE
	path.parent.mkdir(parents=True, exist_ok=True)
	sessions = state.get("sessions", {})
	if len(sessions) > SESSION_LIMIT:
		state["sessions"] = dict(list(sessions.items())[-SESSION_LIMIT:])
	path.write_text(json.dumps(state, indent=2), encoding="utf-8")


def transcript_model(payload: Dict[str, Any]) -> Optional[str]:
	"""The model of the first assistant message in the session's transcript, when the payload names no model."""
	path = payload.get("transcript_path")
	if not path:
		return None
	try:
		with open(str(path), encoding="utf-8") as handle:
			for line in handle:
				try:
					entry = json.loads(line)
				except ValueError:
					continue
				message = entry.get("message") if isinstance(entry, dict) else None
				if isinstance(message, dict) and message.get("role") == "assistant" and message.get("model"):
					return str(message["model"])
	except OSError:
		return None
	return None


def hook_session_start(root: Path, payload: Dict[str, Any]) -> int:
	"""Record the model the chat started on, the first time a session is seen (a resume keeps the first record)."""
	if off():
		return 0
	session = str(payload.get("session_id") or "")
	model = str(payload.get("model") or "") or transcript_model(payload) or ""
	if not session or rank(model) is None:
		return 0
	state = load_state(root)
	sessions = state.setdefault("sessions", {})
	if session not in sessions:
		sessions[session] = {"model": model}
		save_state(root, state)
	return 0


def ceiling_for(root: Path, payload: Dict[str, Any]) -> Optional[str]:
	record = load_state(root).get("sessions", {}).get(str(payload.get("session_id") or ""))
	if isinstance(record, dict) and rank(record.get("model")) is not None:
		return str(record["model"])
	return transcript_model(payload)


def definition_model(path: Path) -> str:
	"""The `model` in an agent definition's front matter; empty when it sets none."""
	text = path.read_text(encoding="utf-8", errors="replace")
	front = text.split("---")[1] if text.startswith("---") and text.count("---") >= 2 else ""
	match = re.search(r"(?m)^model:\s*(\S+)", front)
	return match.group(1) if match else ""


def pinned_model(root: Path, agent_type: str) -> str:
	"""The `model` an agent definition pins; empty when the definition is missing or inherits."""
	for name in (agent_type, agent_type.replace("_", "-")):
		path = root / AGENTS / f"{name}.md"
		if name and path.is_file():
			return definition_model(path)
	return ""


def started_models(root: Path, payload: Dict[str, Any]) -> List[str]:
	"""Every model the tool call is about to start something on, as written in the call."""
	tool = str(payload.get("tool_name") or "")
	data = payload.get("tool_input")
	data = data if isinstance(data, dict) else {}
	if tool in ("Agent", "Task"):
		requested = str(data.get("model") or "") or pinned_model(root, str(data.get("subagent_type") or ""))
		return [requested] if requested else []
	if tool == "Bash":
		command = str(data.get("command") or "")
		if COMMAND.search(command):
			return MODEL_ARGUMENT.findall(command)
	return []


def hook_pre_tool(root: Path, payload: Dict[str, Any]) -> int:
	"""Refuse a start above the session's ceiling."""
	if off():
		return 0
	started = [model for model in started_models(root, payload) if rank(model) is not None]
	if not started:
		return 0
	ceiling = ceiling_for(root, payload)
	if ceiling is None:
		return 0
	too_high = [model for model in started if (rank(model) or 0) > (rank(ceiling) or 0)]
	if not too_high:
		return 0
	reason = (f"Model ceiling: this chat started on {family(ceiling)}, so a helper never starts on {family(too_high[0])}. "
		f"Start it on {family(ceiling)} or lower (for a subagent pass `model: \"{family(ceiling)}\"`). "
		"A higher model needs the user to start a new chat on it.")
	print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": reason}}))
	return 0


def check(root: Path) -> List[str]:
	"""Problems with the shipped agents and hook registration."""
	problems: List[str] = []
	for path in sorted((root / AGENTS).glob("*.md")):
		model = definition_model(path)
		number = rank(model)
		if model != "inherit" and number is None:
			problems.append(f"{path.name}: model '{model}' is not inherit, haiku or sonnet")
		elif number is not None and number > FAMILIES.index(MAX_PINNED) + 1:
			problems.append(f"{path.name}: pins {family(model)}; no agent pins a model above {MAX_PINNED} (the chat's model is the ceiling)")
	try:
		hooks = json.loads((root / SETTINGS).read_text(encoding="utf-8")).get("hooks", {})
	except (OSError, ValueError):
		return problems + [f"{SETTINGS.as_posix()} is missing or unreadable"]
	for event, mode in (("SessionStart", "session-start"), ("PreToolUse", "pre-tool")):
		commands = [hook.get("command", "") for group in hooks.get(event, []) for hook in group.get("hooks", [])]
		if not any(f"model-ceiling --hook {mode}" in command for command in commands):
			problems.append(f"{SETTINGS.as_posix()}: no {event} hook runs `check.py model-ceiling --hook {mode}`")
	return problems


def main(argv: Optional[Sequence[str]] = None, root: Path = REPO_ROOT) -> int:
	parser = argparse.ArgumentParser(prog="check.py model-ceiling", description=(__doc__ or "").split("\n\n")[0])
	parser.add_argument("--hook", choices=("session-start", "pre-tool"), help="Claude Code hook adapter (reads the hook JSON)")
	arguments = parser.parse_args(argv)
	if arguments.hook == "session-start":
		return hook_session_start(root, read_payload())
	if arguments.hook == "pre-tool":
		return hook_pre_tool(root, read_payload())
	problems = check(root)
	for problem in problems:
		print(f"model-ceiling: {problem}")
	if not problems:
		print("model-ceiling: no agent pins a model above sonnet and both hooks are registered")
	return 1 if problems else 0


if __name__ == "__main__":
	raise SystemExit(main())
