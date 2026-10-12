#!/usr/bin/env python3
"""Project canonical Claude Code subagents into the other agent runtimes.

Canonical source: `.claude/agents/*.md` (Claude Code subagent files).
Generated outputs, all one-way and overwritten on every run:

- Codex: `.codex/agents/<snake_name>.toml` plus the `[agents.<snake_name>]`
  registry tables in `.codex/config.toml`
- Cursor: `.cursor/agents/*.md` and `.cursor/agent-map.md`
- Qoder: `.qoder/agents/*.md` and `.qoder/agent-map.md`
- OpenCode: `.opencode/agent/*.md` and `.opencode/agent-map.md`
- Claude Code: `.claude/agent-map.md` (the agent files themselves are the source)

Runtime tuning that is not part of a prompt, such as the Codex reasoning effort
for each Claude model tier, lives in `agent_profiles.json` next to this file.
The synchronizer discovers agents from the canonical folder, so adding or
removing an agent never requires editing this script.

Standard library only; runs on Python 3.9 or newer.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple


TOOLS_DIR = Path(__file__).resolve().parent
MOD_ROOT = TOOLS_DIR.parents[1]
CANONICAL_DIR = MOD_ROOT / ".claude" / "agents"
PROFILES_PATH = TOOLS_DIR / "agent_profiles.json"
CODEX_CONFIG = MOD_ROOT / ".codex" / "config.toml"

READ_ONLY = "read-only"
CAN_EDIT = "can edit"
MODEL_TIERS = ("opus", "sonnet", "haiku")
NAME_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]*$")

# Canonical wording that each runtime expresses with its own mechanism.
# Claude Code reads the canonical text unchanged.
RUNTIME_PHRASES = {
    "codex": (
        ("spawned without inherited conversation context", 'spawned with fork_turns="none" (fork_context=false, no inherited conversation context)'),
        ("spawn this agent without inherited conversation context", 'spawn this agent with fork_turns="none" (fork_context=false, no inherited conversation context)'),
        ("CLAUDE.md", "AGENTS.md"),
    ),
    "other": (
        ("CLAUDE.md", "AGENTS.md"),
    ),
}


@dataclass(frozen=True)
class Agent:
    name: str
    description: str
    model: str
    effort: str
    read_only: bool
    body: str
    source_name: str

    @property
    def snake_name(self) -> str:
        return self.name.replace("-", "_")

    @property
    def authority(self) -> str:
        return READ_ONLY if self.read_only else CAN_EDIT

    @property
    def title(self) -> str:
        words = self.snake_name.split("_")
        if words and words[0] == "hoi4":
            words = words[1:]
        return " ".join(word.upper() if word in {"ai", "ui", "3d"} else word.capitalize() for word in words)


@dataclass(frozen=True)
class Runtime:
    key: str
    label: str
    agent_dir: Path
    map_path: Optional[Path]
    extension: str


RUNTIMES: Dict[str, Runtime] = {
    "codex": Runtime("codex", "Codex", MOD_ROOT / ".codex" / "agents", None, ".toml"),
    "cursor": Runtime("cursor", "Cursor", MOD_ROOT / ".cursor" / "agents", MOD_ROOT / ".cursor" / "agent-map.md", ".md"),
    "qoder": Runtime("qoder", "Qoder", MOD_ROOT / ".qoder" / "agents", MOD_ROOT / ".qoder" / "agent-map.md", ".md"),
    "opencode": Runtime("opencode", "OpenCode", MOD_ROOT / ".opencode" / "agent", MOD_ROOT / ".opencode" / "agent-map.md", ".md"),
    "claude": Runtime("claude", "Claude Code", CANONICAL_DIR, MOD_ROOT / ".claude" / "agent-map.md", ".md"),
}


class SyncError(RuntimeError):
    pass


def load_profiles() -> dict:
    try:
        return json.loads(PROFILES_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SyncError(f"missing runtime profile file: {PROFILES_PATH.relative_to(MOD_ROOT)}")
    except json.JSONDecodeError as error:
        raise SyncError(f"{PROFILES_PATH.relative_to(MOD_ROOT)} is not valid JSON: {error}")


def parse_frontmatter(path: Path) -> Tuple[Dict[str, str], str]:
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    if not text.startswith("---\n"):
        raise SyncError(f"{path.name}: the file must start with a '---' frontmatter block")
    end = text.find("\n---\n", 4)
    if end < 0:
        raise SyncError(f"{path.name}: the frontmatter block is not closed with '---'")
    fields: Dict[str, str] = {}
    for line in text[4:end].split("\n"):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        key, separator, value = stripped.partition(":")
        if not separator:
            raise SyncError(f"{path.name}: frontmatter line is not 'key: value': {stripped}")
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] == '"':
            value = value[1:-1].replace('\\"', '"').replace("\\\\", "\\")
        fields[key.strip()] = value
    return fields, text[end + 5 :].strip() + "\n"


def load_agents() -> List[Agent]:
    if not CANONICAL_DIR.is_dir():
        raise SyncError(f"canonical agent folder not found: {CANONICAL_DIR.relative_to(MOD_ROOT)}")
    agents: List[Agent] = []
    problems: List[str] = []
    for path in sorted(CANONICAL_DIR.glob("*.md")):
        try:
            fields, body = parse_frontmatter(path)
        except SyncError as error:
            problems.append(str(error))
            continue
        name = fields.get("name", "")
        description = fields.get("description", "")
        model = fields.get("model", "")
        effort = fields.get("effort", "")
        if effort not in {"low", "medium", "high", "xhigh", "max"}:
            problems.append(f"{path.name}: valid per-agent effort is required")
        if name != path.stem or not NAME_PATTERN.match(name):
            problems.append(f"{path.name}: 'name' must be the lowercase hyphen-case file name ({path.stem})")
        if not description:
            problems.append(f"{path.name}: 'description' is required")
        if model not in MODEL_TIERS:
            problems.append(f"{path.name}: 'model' must be one of {', '.join(MODEL_TIERS)}, not '{model or 'missing'}'")
        if not body.strip():
            problems.append(f"{path.name}: the agent prompt body is empty")
        disallowed = {item.strip() for item in fields.get("disallowedTools", "").split(",") if item.strip()}
        read_only = {"Write", "Edit"}.issubset(disallowed)
        agents.append(Agent(name, description, model, effort, read_only, body, path.name))
    if problems:
        raise SyncError("canonical agent definitions need fixing:\n  " + "\n  ".join(problems))
    if not agents:
        raise SyncError(f"no canonical agents found in {CANONICAL_DIR.relative_to(MOD_ROOT)}")
    return agents


def runtime_body(runtime_key: str, body: str) -> str:
    phrases = RUNTIME_PHRASES["codex" if runtime_key == "codex" else "other"]
    for canonical, replacement in phrases:
        body = body.replace(canonical, replacement)
    return body.rstrip() + "\n"


def yaml_quote(value: str) -> str:
    return '"{}"'.format(value.replace("\\", "\\\\").replace('"', '\\"'))


def toml_basic(value: str) -> str:
    return '"{}"'.format(value.replace("\\", "\\\\").replace('"', '\\"'))


def toml_multiline(value: str) -> str:
    if "'''" not in value:
        return "'''\n" + value + "'''"
    escaped = value.replace("\\", "\\\\").replace('"""', '\\"\\"\\"')
    return '"""\n' + escaped + '"""'


def header(agent: Agent) -> str:
    return f"Generated from .claude/agents/{agent.source_name} by .tools/sync/sync_agents.py. Edit the source and rerun it."


def render_codex(agent: Agent, profiles: dict) -> str:
    tier = profiles["codex"]["tiers"][agent.model]
    lines = [
        f"# {header(agent)}",
        f"name = {toml_basic(agent.snake_name)}",
        f"description = {toml_basic(agent.description)}",
    ]
    for key in ("model", "model_reasoning_effort"):
        if tier.get(key):
            lines.append(f"{key} = {toml_basic(tier[key])}")
    sandbox = profiles["codex"]["sandbox"][agent.authority]
    lines.append(f"sandbox_mode = {toml_basic(sandbox)}")
    lines.append(f"nickname_candidates = [{toml_basic(agent.title)}]")
    lines.append("")
    lines.append(f"developer_instructions = {toml_multiline(runtime_body('codex', agent.body))}")
    return "\n".join(lines) + "\n"


def render_markdown(runtime: Runtime, agent: Agent, profiles: dict) -> str:
    body = runtime_body(runtime.key, agent.body)
    if runtime.key == "qoder":
        tools = profiles["qoder"]["tools"][agent.authority]
        lines = ["---", f"name: {agent.name}", f"description: {yaml_quote(agent.description)}", f"tools: {tools}", "---", f"<!-- {header(agent)} -->"]
    elif runtime.key == "cursor":
        lines = ["---", f"# {header(agent)}", f"name: {agent.name}", f"description: {yaml_quote(agent.description)}", f"model: {profiles['cursor']['model']}", "---"]
    else:
        lines = ["---", f"# {header(agent)}", f"description: {yaml_quote(agent.description)}", "mode: subagent", f"model: {profiles['opencode']['model']}", "---"]
    return "\n".join(lines + ["", body.rstrip(), ""])


def render_map(runtime: Runtime, agents: List[Agent]) -> str:
    folder = runtime.agent_dir.relative_to(MOD_ROOT).as_posix()
    if runtime.key == "claude":
        intro = f"These are the canonical subagent definitions in `{folder}/`. Edit them directly, then run `python .tools/sync/sync_agents.py` to regenerate the Codex, Cursor, Qoder, and OpenCode projections."
        rows = [f"| `{a.name}` | `{a.model}` | `{a.effort}` | {a.authority} |" for a in agents]
        table = "| Agent | Model | Effort | Authority |\n| --- | --- | --- | --- |"
    else:
        intro = f"Generated from the canonical Claude Code agents in `.claude/agents/`. Edit the canonical file and run `python .tools/sync/sync_agents.py`; never edit `{folder}/` by hand."
        rows = [f"| `{a.name}` | `{a.name}` | `{a.model}` | {a.authority} |" for a in agents]
        table = f"| Canonical | {runtime.label} | Claude tier | Authority |\n| --- | --- | --- | --- |"
    return (
        f"<!-- Generated by .tools/sync/sync_agents.py. Do not hand-edit. -->\n"
        f"# {runtime.label} Subagent Map\n\n{intro}\n\n{table}\n" + "\n".join(rows) + "\n\n"
        "Read-only agents may not edit project files. The prompt body is the final scope contract when a runtime cannot express an equivalent tool allowlist.\n"
    )


AGENT_TABLE = re.compile(r"^\[agents\.([A-Za-z0-9_]+)\]\s*$")
TABLE_HEADER = re.compile(r"^\s*\[")
PORTRAIT_START = "# HOI4_MOD_SETUP_PORTRAITS_START"
PORTRAIT_END = "# HOI4_MOD_SETUP_PORTRAITS_END"
PORTRAIT_AGENT = "hoi4_portrait_creator"


def render_codex_registry(existing: str, agents: List[Agent]) -> str:
    """Replace every `[agents.<name>]` table that points at a projected TOML."""
    known = {agent.snake_name for agent in agents}
    lines = existing.replace("\r\n", "\n").split("\n")
    kept: List[str] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        if line.strip() in (PORTRAIT_START, PORTRAIT_END):
            index += 1
            continue
        match = AGENT_TABLE.match(line.strip())
        if match:
            block = [line]
            index += 1
            while index < len(lines) and not TABLE_HEADER.match(lines[index]) and lines[index].strip() not in (PORTRAIT_START, PORTRAIT_END):
                block.append(lines[index])
                index += 1
            config_line = next((item for item in block if item.strip().startswith("config_file")), "")
            generated = f'"agents/{match.group(1)}.toml"' in config_line
            if generated:
                continue
            kept.extend(block)
            continue
        kept.append(line)
        index += 1
    text = "\n".join(kept).rstrip() + "\n"
    blocks: List[str] = []
    for agent in agents:
        if agent.snake_name == PORTRAIT_AGENT:
            continue
        blocks.append(f"[agents.{agent.snake_name}]\ndescription = {toml_basic(agent.description)}\nconfig_file = \"agents/{agent.snake_name}.toml\"\n")
    if PORTRAIT_AGENT in known:
        portrait = next(agent for agent in agents if agent.snake_name == PORTRAIT_AGENT)
        blocks.append(
            f"{PORTRAIT_START}\n[agents.{PORTRAIT_AGENT}]\ndescription = {toml_basic(portrait.description)}\nconfig_file = \"agents/{PORTRAIT_AGENT}.toml\"\n{PORTRAIT_END}\n"
        )
    return text + "\n" + "\n".join(blocks)


def expected_outputs(runtime_key: str, agents: List[Agent], profiles: dict) -> Dict[Path, str]:
    runtime = RUNTIMES[runtime_key]
    outputs: Dict[Path, str] = {}
    if runtime_key == "codex":
        for agent in agents:
            outputs[runtime.agent_dir / f"{agent.snake_name}.toml"] = render_codex(agent, profiles)
        if CODEX_CONFIG.exists():
            outputs[CODEX_CONFIG] = render_codex_registry(CODEX_CONFIG.read_text(encoding="utf-8"), agents)
    elif runtime_key != "claude":
        for agent in agents:
            outputs[runtime.agent_dir / f"{agent.name}.md"] = render_markdown(runtime, agent, profiles)
    if runtime.map_path is not None:
        outputs[runtime.map_path] = render_map(runtime, agents)
    return outputs


def generated_files(runtime_key: str) -> List[Path]:
    """Files in a projection folder that this synchronizer wrote earlier."""
    runtime = RUNTIMES[runtime_key]
    if runtime_key == "claude" or not runtime.agent_dir.exists():
        return []
    marker = "by .tools/sync/sync_agents.py"
    return [path for path in runtime.agent_dir.glob(f"*{runtime.extension}") if marker in path.read_text(encoding="utf-8", errors="replace")]


def runtime_present(runtime_key: str) -> bool:
    """A projection is maintained only for runtimes installed in this project."""
    if runtime_key == "claude":
        return True
    runtime = RUNTIMES[runtime_key]
    return runtime.agent_dir.exists() or (runtime.map_path is not None and runtime.map_path.exists())


def synchronize(runtime_keys: List[str], check: bool) -> int:
    try:
        profiles = load_profiles()
        agents = load_agents()
    except SyncError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    failures = 0
    for runtime_key in runtime_keys:
        outputs = expected_outputs(runtime_key, agents, profiles)
        drift = [path for path, content in outputs.items() if not path.exists() or path.read_text(encoding="utf-8").replace("\r\n", "\n") != content]
        stale = sorted(set(generated_files(runtime_key)) - set(outputs))
        if check:
            for path in drift:
                print(f"DRIFT: {path.relative_to(MOD_ROOT).as_posix()}")
            for path in stale:
                print(f"STALE: {path.relative_to(MOD_ROOT).as_posix()}")
            if drift or stale:
                failures += 1
            else:
                print(f"{runtime_key}: {len(agents)} agents in sync.")
            continue
        for path in drift:
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("w", encoding="utf-8", newline="") as handle:
                handle.write(outputs[path])
        for path in stale:
            path.unlink()
        print(f"{runtime_key}: {len(agents)} agents; {len(drift)} written, {len(stale)} removed.")
    return 1 if failures else 0


def verify(runtime_keys: List[str]) -> int:
    """Check role policies and read back each generated runtime definition."""
    try:
        agents = load_agents()
        profiles = load_profiles()
        policy = profiles["tier_policy"]
        efforts = profiles["effort_policy"]
        declared = [name for tier in MODEL_TIERS for name in policy.get(tier, [])]
        names = {agent.name for agent in agents}
        if len(declared) != len(set(declared)) or set(declared) - names:
            raise SyncError("tier_policy contains duplicate or absent canonical agents")
        failures = []
        for agent in agents:
            tier = next((tier for tier in MODEL_TIERS if agent.name in policy.get(tier, [])), policy["default"])
            if agent.model != tier:
                failures.append(f"{agent.name}: model is {agent.model}; policy requires {tier}")
            if agent.effort != efforts[tier]:
                failures.append(f"{agent.name}: effort is {agent.effort}; policy requires {efforts[tier]}")
            if profiles["codex"]["tiers"][tier]["model_reasoning_effort"] != efforts[tier]:
                failures.append(f"{tier}: Codex effort does not match the canonical effort policy")
        if failures:
            raise SyncError("agent policy verification failed:\n  " + "\n  ".join(failures))
    except (SyncError, KeyError, TypeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    # Comparing bytes reads the complete installed definition, including its
    # tier, effort, sandbox, provider markers and runtime-specific wording.
    result = synchronize(runtime_keys, check=True)
    if result == 0:
        print(f"Verified tier, effort and runtime definitions for {len(agents)} canonical agents.")
    return result


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Project canonical .claude/agents into the other agent runtimes.")
    parser.add_argument("--check", action="store_true", help="report drift without writing; exit 1 when out of sync")
    parser.add_argument("--verify", action="store_true", help="verify canonical tier/effort policy and generated definitions without writing")
    parser.add_argument("--runtime", action="append", choices=sorted(RUNTIMES), help="limit to one runtime (repeatable); default: every runtime present in this project")
    args = parser.parse_args(argv)
    keys = args.runtime or [key for key in RUNTIMES if runtime_present(key)]
    return verify(keys) if args.verify else synchronize(keys, args.check)
