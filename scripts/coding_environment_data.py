"""Source-owned coding-client declarations for the HOI4 Mod Setup manifest.

Each client entry names the project surfaces its package installs and how the
client registers MCP servers:

- ``project``: a client-recognized project file the installer manages. The
  registration names that file, its format, and the component that installs it.
- ``manual``: the client reads MCP servers only from user, IDE, or cloud
  settings. The installer never writes them; the app shows a to-do.
- ``none``: the client has no native MCP support.

Generated agent projections come from ``.tools/sync/sync_agents.py``; skill
copies are re-rooted views of the canonical ``.claude/skills`` tree. File
evidence is added by ``generate_manifest_evidence.py`` at one exact revision.
"""

from __future__ import annotations

import copy
from typing import Dict, List, Optional

PORTRAIT_AGENT = "hoi4-portrait-creator.md"
SUPER_EVENT_AGENTS = "hoi4-super-event-*.md"
SHARED_SKILLS_CLIENTS = ["gemini_cli", "antigravity", "kilo_code", "devin_desktop"]

# id, display name, description, open command, MCP support, registration
# (component, path, format), reviewed documentation for the MCP setup.
ENVIRONMENTS = [
    ("claude_code", "Claude Code", "Canonical CLAUDE.md, skills, and agents in .claude, shared settings, and project MCP registration", "claude", "project", ("runtime.claude.mcp", ".mcp.json", "json_mcp_servers"), None),
    ("codex", "Codex", "AGENTS.md, the .agents/skills copy, generated .codex agents, and Codex MCP configuration", "codex", "project", ("codex.config", ".codex/config.toml", "toml_mcp_servers"), None),
    ("cursor", "Cursor", "Generated .cursor agents, project settings, map, and MCP", None, "project", ("runtime.cursor.mcp", ".cursor/mcp.json", "json_mcp_servers"), None),
    ("qoder", "Qoder", "Generated .qoder agents, project settings, map, and MCP", None, "project", ("runtime.qoder.mcp", ".qoder/mcp.json", "json_mcp_servers"), None),
    ("opencode", "OpenCode", "Generated .opencode agents, map, and opencode.json with instructions and MCP", None, "project", ("runtime.opencode.config", "opencode.json", "local_command_array"), "https://opencode.ai/docs/mcp-servers/"),
    ("github_copilot", "GitHub Copilot (VS Code)", "A Copilot instructions file, the canonical .claude agents and skills, and VS Code project MCP", None, "project", ("runtime.copilot.mcp", ".vscode/mcp.json", "vscode_servers"), "https://code.visualstudio.com/docs/copilot/customization/mcp-servers"),
    ("gemini_cli", "Gemini CLI", "GEMINI.md that imports AGENTS.md, generated .gemini agents, the shared .agents skills copy, and project MCP", "gemini", "project", ("runtime.gemini.mcp", ".gemini/settings.json", "json_mcp_servers"), "https://geminicli.com/docs/tools/mcp-server/"),
    ("antigravity", "Antigravity", "AGENTS.md, generated .agents agents, the shared .agents skills copy, and project MCP", "agy", "project", ("runtime.antigravity.mcp", ".agents/mcp_config.json", "json_mcp_servers"), "https://antigravity.google/docs/mcp"),
    ("grok_build", "Grok Build", "AGENTS.md, a .grok skills copy, and project MCP", "grok", "project", ("runtime.grok.mcp", ".grok/config.toml", "toml_mcp_servers"), "https://docs.x.ai/build/features/mcp-servers"),
    ("kilo_code", "Kilo Code", "AGENTS.md, generated .kilo agents, the shared .agents skills copy, and project MCP", "kilo", "project", ("runtime.kilo.mcp", ".kilo/kilo.json", "local_command_array"), "https://kilo.ai/docs/automate/mcp/using-in-kilo-code"),
    ("kiro", "Kiro", "AGENTS.md, generated .kiro agents, a .kiro skills copy, and project MCP", None, "project", ("runtime.kiro.mcp", ".kiro/settings/mcp.json", "json_mcp_servers"), "https://kiro.dev/docs/mcp/configuration/"),
    ("qwen_code", "Qwen Code", "AGENTS.md, generated .qwen agents, a .qwen skills copy, and project MCP", "qwen", "project", ("runtime.qwen.mcp", ".qwen/settings.json", "json_mcp_servers"), "https://qwenlm.github.io/qwen-code-docs/en/users/features/mcp/"),
    ("cline", "Cline", "AGENTS.md, a Cline rule, and the canonical .claude skills; MCP servers are added in Cline", None, "manual", None, "https://docs.cline.bot/mcp/configuring-mcp-servers"),
    ("devin_desktop", "Devin Desktop", "AGENTS.md, generated .devin agents, and the shared .agents skills copy; MCP servers are added in Devin", None, "manual", None, "https://docs.devin.ai/desktop/devin-local"),
    ("augment", "Augment (Auggie CLI)", "AGENTS.md, generated .augment agents, and the canonical .claude skills; MCP servers are added in Auggie", "auggie", "manual", None, "https://docs.augmentcode.com/cli/integrations"),
    ("continue", "Continue", "A Continue rule that points to AGENTS.md and the skills; MCP servers are added in Continue", None, "manual", None, "https://docs.continue.dev/customize/deep-dives/mcp"),
    ("aider", "Aider", "An .aider.conf.yml that reads AGENTS.md; Aider has no MCP support", "aider", "none", None, "https://aider.chat/docs/usage/conventions.html"),
]

# Clients with a generated agent projection: environment, component prefix,
# projection folder, label, and platforms of the base package.
AGENT_PROJECTIONS = [
    ("gemini_cli", "gemini", ".gemini", "Gemini CLI", ["all"]),
    ("antigravity", "antigravity", ".agents", "Antigravity", ["all"]),
    ("kilo_code", "kilo", ".kilo", "Kilo Code", ["all"]),
    ("kiro", "kiro", ".kiro", "Kiro", ["all"]),
    ("qwen_code", "qwen", ".qwen", "Qwen Code", ["all"]),
    ("devin_desktop", "devin", ".devin", "Devin Desktop", ["all"]),
    # Auggie runs on macOS and Linux; Windows is reached only through WSL,
    # which has no verified route here.
    ("augment", "augment", ".augment", "Augment", ["macos", "linux"]),
]

# Clients that read skills only from their own folder get a re-rooted copy.
SKILL_COPIES = [
    ("grok_build", "grok", ".grok/skills/", "Grok Build"),
    ("kiro", "kiro", ".kiro/skills/", "Kiro"),
    ("qwen_code", "qwen", ".qwen/skills/", "Qwen Code"),
]

# Single-file packages: environment, component id, source, destination,
# ownership, label.
FILE_PACKAGES = [
    ("gemini_cli", "runtime.gemini.context", "GEMINI_template.md", "GEMINI.md", "Gemini CLI project context"),
    ("github_copilot", "runtime.copilot", ".github/instructions/hoi4-mod-setup.instructions.md", ".github/instructions/hoi4-mod-setup.instructions.md", "GitHub Copilot instructions"),
    ("cline", "runtime.cline", ".clinerules/hoi4-mod-setup.md", ".clinerules/hoi4-mod-setup.md", "Cline project rule"),
    ("continue", "runtime.continue", ".continue/rules/hoi4-mod-setup.md", ".continue/rules/hoi4-mod-setup.md", "Continue project rule"),
    ("aider", "runtime.aider", ".aider.conf.yml", ".aider.conf.yml", "Aider project configuration"),
]

# Project MCP registrations other than the original five clients.
MCP_REGISTRATIONS = [
    ("github_copilot", "runtime.copilot.mcp", ".vscode/mcp.json", "runtime.copilot", "GitHub Copilot (VS Code)", "three_way_merge"),
    ("gemini_cli", "runtime.gemini.mcp", ".gemini/settings.json", "runtime.gemini", "Gemini CLI", "three_way_merge"),
    ("antigravity", "runtime.antigravity.mcp", ".agents/mcp_config.json", "runtime.antigravity", "Antigravity", "three_way_merge"),
    ("grok_build", "runtime.grok.mcp", ".grok/config.toml", "runtime.grok.skills", "Grok Build", "toml_merge"),
    ("kilo_code", "runtime.kilo.mcp", ".kilo/kilo.json", "runtime.kilo", "Kilo Code", "three_way_merge"),
    ("kiro", "runtime.kiro.mcp", ".kiro/settings/mcp.json", "runtime.kiro", "Kiro", "three_way_merge"),
    ("qwen_code", "runtime.qwen.mcp", ".qwen/settings.json", "runtime.qwen", "Qwen Code", "three_way_merge"),
]

# Components this builder owns. Any other component is left unchanged.
REMOVED_COMPONENTS = ["runtime.opencode.mcp"]


def build_coding_environment_table() -> List[dict]:
    table = []
    for identifier, name, description, command, support, registration, documentation in ENVIRONMENTS:
        entry: Dict[str, object] = {"id": identifier, "display_name": name, "description": description}
        if identifier == "claude_code":
            entry["default_primary"] = True
        if command:
            entry["open_command"] = command
        entry["mcp_support"] = support
        if registration:
            component, path, fmt = registration
            entry["mcp_registration"] = {"component_id": component, "path": path, "format": fmt}
        if documentation:
            entry["documentation_url"] = documentation
        table.append(entry)
    return table


def _base(component_id: str, name: str, description: str, environment: str, optional: bool, platforms: List[str], source: dict, destination: str, ownership: str, dependencies: List[str], conflicts: str, policy: str, validation: List[dict], capabilities: List[str]) -> dict:
    strategy = {"three_way_merge": "three_way_merge", "toml_merge": "toml_merge"}.get(policy, "replace_if_unmodified")
    return {
        "id": component_id,
        "display_name": name,
        "description": description,
        "category": "environment",
        "coding_environment": environment,
        "optional": optional,
        "platforms": platforms,
        "source": source,
        "destination": {"path": destination, "ownership": ownership, "outside_project": False},
        "dependencies": dependencies,
        "conflicts": [conflicts],
        "conflict_policy": policy,
        "validation": validation,
        "update": {"strategy": strategy, "remove_obsolete": strategy == "replace_if_unmodified", "preserve_local_additions": True},
        "capabilities": capabilities,
        "expected_files": [],
    }


def _exists(identifier: str, target: str) -> dict:
    return {"id": identifier, "severity": "block", "kind": "exists", "target": target}


def build_coding_environment_components(components: List[dict]) -> List[dict]:
    """Declarations for the clients this table adds. ``components`` supplies
    the published Codex skill-copy templates so copies stay identical."""
    by_id = {component["id"]: component for component in components}
    built: List[dict] = []
    for environment, prefix, folder, label, platforms in AGENT_PROJECTIONS:
        agent_folder = f"{folder}/agents"
        dependencies = ["core.subagents", "runtime.agent_sync"]
        if environment in SHARED_SKILLS_CLIENTS:
            dependencies.append("runtime.codex.skills")
        built.append(_base(
            f"runtime.{prefix}", f"{label} coding environment",
            f"Install the {label} subagents and map generated from the canonical Claude Code agents.",
            environment, False, platforms,
            {"kind": "tree", "path": folder, "include": ["agent-map.md", "agents/*.md"], "exclude": [f"agents/{PORTRAIT_AGENT}", f"agents/{SUPER_EVENT_AGENTS}"]},
            f"{folder}/", "managed", dependencies,
            f"existing {label} agent or map with the same path", "replace_if_unmodified",
            [_exists(f"{prefix}.agents.exists", agent_folder)],
            [f"{label} subagents"],
        ))
        built.append(_base(
            f"runtime.{prefix}.portrait_agent", f"{label} portrait subagent",
            f"Install the {label} projection only when Portrait Production is selected.",
            environment, True, platforms,
            {"kind": "file", "path": f"{agent_folder}/{PORTRAIT_AGENT}"},
            f"{agent_folder}/{PORTRAIT_AGENT}", "managed", [f"runtime.{prefix}", "workflow.portraits.subagent"],
            f"existing {label} portrait subagent", "replace_if_unmodified",
            [_exists(f"{prefix}.portrait_agent.exists", f"{agent_folder}/{PORTRAIT_AGENT}")],
            [f"{label} portrait subagent"],
        ))
        built.append(_base(
            f"runtime.{prefix}.super_event_agents", f"{label} Super Events subagents",
            f"Install the {label} projections only when Super Events is selected.",
            environment, True, platforms,
            {"kind": "tree", "path": agent_folder, "include": [SUPER_EVENT_AGENTS]},
            f"{agent_folder}/", "managed", [f"runtime.{prefix}", "workflow.super_events.subagents"],
            f"existing {label} Super Events subagent", "replace_if_unmodified",
            [_exists(f"{prefix}.super_event_agents.exists", agent_folder)],
            [f"{label} Super Events subagents"],
        ))
    for environment, component_id, source, destination, label in FILE_PACKAGES:
        dependencies = ["core.agents"]
        if environment == "gemini_cli":
            dependencies.append("runtime.gemini")
        built.append(_base(
            component_id, label,
            f"Install the {label.lower()} that points the client at the project instructions.",
            environment, False, ["all"],
            {"kind": "file", "path": source}, destination, "managed", dependencies,
            f"existing {destination}", "replace_if_unmodified",
            [_exists(f"{component_id.removeprefix('runtime.')}.exists", destination)],
            [label],
        ))
    template = by_id["runtime.codex.skills"]
    workflow_templates = [component for component in components if component.get("coding_environment") == "codex" and component["id"].startswith("runtime.codex.") and component["id"].endswith("_skill")]
    for environment, prefix, destination, label in SKILL_COPIES:
        skills = copy.deepcopy(template)
        skills.update({
            "id": f"runtime.{prefix}.skills",
            "display_name": f"{label} skill copy",
            "description": f"Install the {destination} copy of the canonical skill library for {label}.",
            "coding_environment": environment,
            "dependencies": ["core.skills"],
            "conflicts": [f"existing skill with the same name in {destination.rstrip('/')}"],
            "expected_files": [],
        })
        skills["destination"] = {**template["destination"], "path": destination}
        skills.pop("shared_coding_environments", None)
        built.append(skills)
        for workflow in workflow_templates:
            item = copy.deepcopy(workflow)
            suffix = workflow["id"].removeprefix("runtime.codex.")
            item.update({
                "id": f"runtime.{prefix}.{suffix}",
                "display_name": workflow["display_name"].replace("Codex copy", f"{label} copy").replace("Shared .agents/skills copy", f"{label} copy"),
                "coding_environment": environment,
                "dependencies": [f"runtime.{prefix}.skills" if dependency == "runtime.codex.skills" else dependency for dependency in workflow["dependencies"]],
                "conflicts": [conflict.replace("codex copy", f"{label} copy") for conflict in workflow.get("conflicts", [])],
                "expected_files": [],
            })
            item["destination"] = {**workflow["destination"], "path": workflow["destination"]["path"].replace(".agents/skills/", destination, 1)}
            item.pop("shared_coding_environments", None)
            built.append(item)
    for environment, component_id, path, base, label, policy in MCP_REGISTRATIONS:
        validation = [_exists(f"{component_id.removeprefix('runtime.')}.exists", path)]
        if policy == "toml_merge":
            validation.append({"id": f"{component_id.removeprefix('runtime.')}.toml", "severity": "block", "kind": "toml_parse", "target": path})
        component = _base(
            component_id, f"{label} HOI4 MCP configuration",
            "Install the project registration for the verified HOI4 Agent Tools server.",
            environment, True, ["windows", "linux"],
            {"kind": "file", "path": path}, path, "merged", [base, "mcp.hoi4_agent_tools"],
            f"existing {label} project MCP server id", policy, validation,
            [f"{label} MCP registration", "HOI4 Agent Tools"],
        )
        component["update"]["remove_obsolete"] = False
        built.append(component)
    return built


def apply_coding_environments(manifest: dict) -> None:
    """Rewrite the client table and the components this module owns."""
    manifest["coding_environments"] = build_coding_environment_table()
    components = [component for component in manifest["components"] if component["id"] not in REMOVED_COMPONENTS]
    for component in components:
        if component.get("coding_environment") == "codex" and (component["id"] == "runtime.codex.skills" or (component["id"].startswith("runtime.codex.") and component["id"].endswith("_skill"))):
            component["shared_coding_environments"] = list(SHARED_SKILLS_CLIENTS)
            component["display_name"] = component["display_name"].replace("Codex skill copy", "Shared .agents/skills copy").replace("Codex copy", "Shared .agents/skills copy")
        if component["id"] == "runtime.opencode.config":
            component["display_name"] = "OpenCode project configuration and MCP"
            component["description"] = "Install opencode.json with the project instructions and the HOI4 Agent Tools registration, which HOI4 Mod Setup adapts or removes per platform."
    generated = build_coding_environment_components(components)
    generated_ids = {component["id"] for component in generated}
    replaced = [component for component in components if component["id"] not in generated_ids]
    by_id = {component["id"]: component for component in components}
    for component in generated:
        previous: Optional[dict] = by_id.get(component["id"])
        if previous is not None:
            component["expected_files"] = previous.get("expected_files", [])
    manifest["components"] = replaced + generated
