#!/usr/bin/env python3
"""Shared one-way renderer for alternate agent runtimes."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    try:
        import tomli as tomllib
    except ModuleNotFoundError:
        sys.exit("ERROR: install tomli or run Python 3.11+.")


MOD_ROOT = Path(__file__).resolve().parents[2]
CODEX_AGENTS = MOD_ROOT / ".codex" / "agents"

READ_ONLY = "read-only / plan-only"
PATCH_CAPABLE = "patch-capable"
ASSET_RESEARCH = "asset / research (web)"

# Keep this single map aligned with hoi4-subagents. Runtime-specific tools are
# deliberately derived here so three generated formats cannot drift apart.
AUTHORITY = {
    "hoi4_repo_explorer": READ_ONLY,
    "hoi4_feature_completion_auditor": READ_ONLY,
    "hoi4_ai_probability_auditor": READ_ONLY,
    "hoi4_improvement_loop_planner": READ_ONLY,
    "hoi4_documentation_curator": PATCH_CAPABLE,
    "hoi4_scripted_system_architect": PATCH_CAPABLE,
    "hoi4_decision_mission_auditor": PATCH_CAPABLE,
    "hoi4_focus_tree_auditor": PATCH_CAPABLE,
    "hoi4_country_package_auditor": PATCH_CAPABLE,
    "hoi4_localisation_auditor": PATCH_CAPABLE,
    "hoi4_event_ui_worker": PATCH_CAPABLE,
    "hoi4_skill_maintainer": PATCH_CAPABLE,
    "hoi4_spreadsheet_doc_worker": PATCH_CAPABLE,
    "hoi4_asset_source_researcher": ASSET_RESEARCH,
    "hoi4_generated_feature_art": ASSET_RESEARCH,
    "hoi4_icon_artist": ASSET_RESEARCH,
    "hoi4_portrait_creator": ASSET_RESEARCH,
    "hoi4_quote_remark_researcher": ASSET_RESEARCH,
    "hoi4_audio_researcher": ASSET_RESEARCH,
    "hoi4_super_event_art_researcher": ASSET_RESEARCH,
    "hoi4_super_event_quote_researcher": ASSET_RESEARCH,
    "hoi4_super_event_audio_researcher": ASSET_RESEARCH,
    "hoi4_3d_model_pipeline": ASSET_RESEARCH,
}

BODY_SUBSTITUTIONS = (
    (
        r"fork_context=false",
        "a fully explicit, self-contained prompt (no inherited conversation context)",
    ),
    (r"Agent Nudger writes", "UI-assisted writes"),
    (r"native ImageGen", "the configured image-generation route"),
)


@dataclass(frozen=True)
class Agent:
    name: str
    description: str
    body: str
    source_name: str

    @property
    def runtime_name(self) -> str:
        return self.name.replace("_", "-")


@dataclass(frozen=True)
class Runtime:
    key: str
    agent_dir: Path
    map_path: Path


RUNTIMES = {
    "qoder": Runtime("qoder", MOD_ROOT / ".qoder" / "agents", MOD_ROOT / ".qoder" / "agents" / "README.md"),
    "cursor": Runtime("cursor", MOD_ROOT / ".cursor" / "agents", MOD_ROOT / ".cursor" / "agent-map.md"),
    "opencode": Runtime("opencode", MOD_ROOT / ".opencode" / "agent", MOD_ROOT / ".opencode" / "agent-map.md"),
}


def yaml_quote(value: str) -> str:
    return '"{}"'.format(value.replace("\\", "\\\\").replace('"', '\\"'))


def load_agents() -> list[Agent]:
    if not CODEX_AGENTS.is_dir():
        raise RuntimeError(f"canonical source folder not found: {CODEX_AGENTS}")

    agents = []
    for path in sorted(CODEX_AGENTS.glob("*.toml")):
        with path.open("rb") as handle:
            data = tomllib.load(handle)
        name = data.get("name") or path.stem
        description = data.get("description", "").strip()
        body = data.get("developer_instructions", "").strip()
        if not description or not body:
            raise RuntimeError(f"{path} is missing description or developer_instructions")
        for pattern, replacement in BODY_SUBSTITUTIONS:
            body = re.sub(pattern, replacement, body)
        agents.append(Agent(name, description, body + "\n", path.name))

    source_names = {agent.name for agent in agents}
    unmapped = sorted(source_names - AUTHORITY.keys())
    orphaned = sorted(AUTHORITY.keys() - source_names)
    if unmapped or orphaned:
        parts = []
        if unmapped:
            parts.append("unmapped canonical agents: " + ", ".join(unmapped))
        if orphaned:
            parts.append("authority entries without a TOML source: " + ", ".join(orphaned))
        raise RuntimeError("; ".join(parts))
    return agents


def render_agent(runtime: Runtime, agent: Agent) -> str:
    source = agent.source_name
    name = agent.runtime_name
    if runtime.key == "qoder":
        qoder_tools = {
            READ_ONLY: "Read, Grep, Glob, Bash, Write",
            PATCH_CAPABLE: "Read, Grep, Glob, Bash, Edit, Write",
            ASSET_RESEARCH: "Read, Grep, Glob, Bash, Edit, Write, WebFetch, WebSearch",
        }
        lines = [
            "---",
            f"name: {name}",
            f"description: {yaml_quote(agent.description)}",
            f"tools: {qoder_tools[AUTHORITY[agent.name]]}",
            "---",
            f"<!-- Generated from .codex/agents/{source} by .tools/sync/sync_qoder_agents.py. Do not hand-edit. -->",
            "",
            agent.body.rstrip(),
            "",
        ]
    elif runtime.key == "cursor":
        lines = [
            "---",
            f"# Generated from .codex/agents/{source} by .tools/sync/sync_cursor_agents.py. Do not hand-edit.",
            f"name: {name}",
            f"description: {yaml_quote(agent.description)}",
            "model: inherit",
            "---",
            "",
            agent.body.rstrip(),
            "",
        ]
    else:
        lines = [
            "---",
            f"# Generated from .codex/agents/{source} by .tools/sync/sync_opencode_agents.py. Do not hand-edit.",
            f"description: {yaml_quote(agent.description)}",
            "mode: subagent",
            "model: inherit",
            "---",
            "",
            agent.body.rstrip(),
            "",
        ]
    return "\n".join(lines)


def render_map(runtime: Runtime, agents: list[Agent]) -> str:
    runtime_label = "OpenCode" if runtime.key == "opencode" else runtime.key.title()
    agent_folder = f".{runtime.key}/{'agent' if runtime.key == 'opencode' else 'agents'}"
    rows = "\n".join(
        f"| `{agent.name}` | `{agent.runtime_name}` | {AUTHORITY[agent.name]} |"
        for agent in agents
    )
    return f"""<!-- Generated by .tools/sync/sync_{runtime.key}_agents.py. Do not hand-edit. -->
# {runtime_label} Subagent Map

Canonical definitions live in `.codex/agents/*.toml`. Generated agent files
live in `{agent_folder}/`; edit the TOML source and rerun the synchronizer.

| Canonical (Codex) | {runtime_label} | Authority |
| --- | --- | --- |
{rows}

Authority follows `hoi4-subagents`. The generated prompt body is the final
scope contract when a runtime cannot express an equivalent tool allowlist.
"""


def expected_outputs(runtime: Runtime, agents: list[Agent]) -> dict[Path, str]:
    outputs = {
        runtime.agent_dir / f"{agent.runtime_name}.md": render_agent(runtime, agent)
        for agent in agents
    }
    outputs[runtime.map_path] = render_map(runtime, agents)
    return outputs


def synchronize(runtime_key: str, check: bool = False) -> int:
    runtime = RUNTIMES[runtime_key]
    try:
        agents = load_agents()
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    outputs = expected_outputs(runtime, agents)
    expected_agent_files = {path.name for path in outputs if path.parent == runtime.agent_dir}
    stale = sorted(
        path for path in runtime.agent_dir.glob("*.md")
        if path.name not in expected_agent_files
    ) if runtime.agent_dir.exists() else []
    drift = [
        path for path, content in outputs.items()
        if not path.exists() or path.read_text(encoding="utf-8") != content
    ]

    if check:
        if drift or stale:
            for path in drift:
                print(f"DRIFT: {path.relative_to(MOD_ROOT)}")
            for path in stale:
                print(f"STALE: {path.relative_to(MOD_ROOT)}")
            return 1
        print(f"{runtime.key}: {len(agents)} generated agents are synchronized.")
        return 0

    for path, content in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        if path in drift:
            with path.open("w", encoding="utf-8", newline="") as handle:
                handle.write(content)
    print(f"{runtime.key}: synchronized {len(agents)} agents; {len(drift)} file(s) written.")
    for path in stale:
        print(f"WARNING: stale generated file not deleted: {path.relative_to(MOD_ROOT)}")
    return 1 if stale else 0


def run_cli(runtime_key: str) -> None:
    parser = argparse.ArgumentParser(description=f"Synchronize Codex agents to {runtime_key}.")
    parser.add_argument("--check", action="store_true", help="fail on generated-output drift without writing")
    args = parser.parse_args()
    raise SystemExit(synchronize(runtime_key, args.check))
