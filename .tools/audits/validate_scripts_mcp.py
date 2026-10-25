#!/usr/bin/env python3
"""Validate changed script files with HOI4 Agent Tools' `hoi4.script_validate` (plan check A12).

The tool checks syntax, command kinds and declared scopes against the installed game
documentation, plus its known-mistake rules. One server session serves every file, so only the
first call pays the mod indexing cost. Findings follow `.tools/lib/report.py`:

- `MCP-SCRIPT-ERROR` (error): a finding with status `error` (syntax, command kind or declared scope).
- `MCP-SCRIPT-KNOWN-MISTAKE` (warning): a `KNOWN_MISTAKE_*` pattern match. `CLAUDE.md` says a listed
  rule does not establish a defect, and on 25 October 2026 `KNOWN_MISTAKE_TEMP_VARIABLE_SCOPE_PREFIX`
  misread script constants such as `constant:x_event_log.event_id` as scoped temporary variables.
- `MCP-SCRIPT-UNRESOLVED` (warning): a command the tool could not classify, such as a helper it
  does not resolve; `CLAUDE.md` requires inspecting these rather than treating them as passed.
- `MCP-SCRIPT-UNCHECKED-ARGUMENTS` (review): a native argument block the tool does not validate.
- `MCP-SCRIPT-INCOMPLETE` (warning): the tool omitted findings, so the file needs a narrower check.

A passing file is evidence only for the tool's `checksPerformed`; parameter semantics and engine
behaviour stay unverified. The server is the `hoi4_agent_tools` entry of `.mcp.json`.

Usage (the tool needs explicit files; it never scans the whole repository):
	python -B .tools/audits/validate_scripts_mcp.py --paths events/x.txt common/scripted_effects/y.txt
	python -B .tools/audits/validate_scripts_mcp.py --paths-from changed.txt --json .tmp/script_validate.json

Exit status: 0 no errors, 1 errors, 2 when the server cannot run or no path was given.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Dict, List

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # .tools, for the shared lib package
from lib.mcp_session import McpError, McpSession, server_command
from lib.report import Finding, add_arguments, exit_code, merge_json, print_findings, relative, requested_paths

REPO_ROOT = Path(__file__).resolve().parents[2]
CHECK = "script-validate"
SERVER = "hoi4_agent_tools"
TOOL = "hoi4.script_validate"
SCRIPT_FOLDERS = ("common/", "events/", "history/")
FINDING_LIMIT = 32  # the tool's maximum per call
CALL_TIMEOUT_SECONDS = 300
LEVELS = {
	"MCP-SCRIPT-ERROR": "error",
	"MCP-SCRIPT-KNOWN-MISTAKE": "warning",
	"MCP-SCRIPT-UNRESOLVED": "warning",
	"MCP-SCRIPT-INCOMPLETE": "warning",
	"MCP-SCRIPT-UNCHECKED-ARGUMENTS": "review",
}


def script_paths(paths: List[str]) -> List[str]:
	"""Keep existing `.txt` script files under the folders the tool validates."""
	chosen = []
	for path in paths:
		rel = relative(path)
		if rel.endswith(".txt") and rel.startswith(SCRIPT_FOLDERS) and (REPO_ROOT / rel).is_file():
			chosen.append(rel)
	return sorted(set(chosen))


def findings_for(path: str, result: Dict[str, Any]) -> List[Finding]:
	data = result.get("data", {})
	rows = []
	for item in data.get("findings", []):
		status, code = item.get("status"), item.get("code", "")
		if status == "supported":
			continue
		if code.startswith("KNOWN_MISTAKE"):
			rule = "MCP-SCRIPT-KNOWN-MISTAKE"
		elif status == "error":
			rule = "MCP-SCRIPT-ERROR"
		elif code == "SCRIPT_ARGUMENT_BLOCK_UNCHECKED":
			rule = "MCP-SCRIPT-UNCHECKED-ARGUMENTS"
		else:
			rule = "MCP-SCRIPT-UNRESOLVED"
		subject = f"{item['command']}: " if item.get("command") else ""
		hint = f" (did you mean {', '.join(item['suggestions'][:2])}?)" if item.get("suggestions") else ""
		rows.append(Finding(CHECK, rule, LEVELS[rule], path, int(item.get("line") or 0),
			f"{code} {subject}{item.get('message', '')}{hint}"))
	if data.get("omittedFindings"):
		rows.append(Finding(CHECK, "MCP-SCRIPT-INCOMPLETE", "warning", path, 0,
			f"{data['omittedFindings']} findings omitted after the first {FINDING_LIMIT}; validate this file in narrower parts"))
	return rows


# What to do when the server cannot validate; matched against the error text, first match wins.
MCP_HINTS = {
	"WORKSPACE_CONTEXT_REQUIRED": "the HOI4 Agent Tools server does not know this mod folder as a workspace: add the mod "
		"(or the folder that holds your mods) to `modRoots` in the server configuration named by HOI4_AGENT_CONFIG, "
		"as HOI4 Mod Setup does when it registers the server",
	"TRANSACTION_MANIFEST_INVALID": "the HOI4 Agent Tools command in .mcp.json is an older install that cannot read the "
		"current server state: point .mcp.json at the pinned runtime (HOI4 Mod Setup, or .tools/mcp/bootstrap_hoi4_agent_tools.py)",
	"default": "run `python -B .tools/check.py doctor` to check the HOI4 Agent Tools registration in .mcp.json",
}

def main() -> int:
	parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
	parser.add_argument("--json", type=Path, help="also write the findings as JSON")
	add_arguments(parser)
	arguments = parser.parse_args()
	requested = requested_paths(arguments)
	if not requested:
		parser.error("give the changed files with --paths or --paths-from; the tool never scans the whole repository")
	paths = script_paths(requested)
	findings: List[Finding] = []
	if paths:
		try:
			command, cwd, env = server_command(SERVER)
			with McpSession(command, cwd, env, CALL_TIMEOUT_SECONDS) as session:
				for path in paths:
					findings += findings_for(path, session.call(TOOL, {"path": path, "limit": FINDING_LIMIT}))
		except McpError as error:
			print(f"{CHECK}: could not run: {error}", file=sys.stderr)
			hint = next((text for code, text in MCP_HINTS.items() if code in str(error)), MCP_HINTS["default"])
			print(f"{CHECK}: {hint}", file=sys.stderr)
			return 2
	findings.sort(key=lambda f: (f.path, f.line, f.rule, f.message))
	print_findings(CHECK, findings)
	print(f"{CHECK}: validated {len(paths)} script file(s)")
	if arguments.json:
		merge_json(arguments.json, findings, LEVELS)
	return exit_code(findings, arguments.fail_on)


if __name__ == "__main__":
	raise SystemExit(main())
