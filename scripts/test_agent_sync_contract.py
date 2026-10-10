#!/usr/bin/env python3
"""Contract checks for the Claude-first runtime synchronizers and templates."""

import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10 and older
    tomllib = None


ROOT = Path(__file__).resolve().parents[1]
SYNC = ROOT / ".tools" / "sync"

EXPECTED_TIERS = {
    "hoi4-improvement-loop-planner": "opus",
    "hoi4-3d-model-pipeline": "sonnet",
    "hoi4-feature-completion-auditor": "sonnet",
    "hoi4-localisation-auditor": "sonnet",
    "hoi4-scripted-system-architect": "sonnet",
    "hoi4-skill-maintainer": "sonnet",
}
READ_ONLY = {
    "hoi4-repo-explorer",
    "hoi4-feature-completion-auditor",
    "hoi4-ai-probability-auditor",
    "hoi4-improvement-loop-planner",
}


def load_module():
    sys.path.insert(0, str(SYNC))
    spec = importlib.util.spec_from_file_location("agent_sync_common", SYNC / "agent_sync_common.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def hard_wraps(text):
    """Report markdown lines that continue one prose sentence on the next line."""
    in_fence = False
    previous = ""
    previous_hard_break = False
    findings = []
    for number, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            previous = ""
            previous_hard_break = False
            continue
        if in_fence:
            previous = ""
            previous_hard_break = False
            continue
        if previous and stripped and not previous_hard_break:
            ends_sentence = previous.endswith((".", ":", ";", "!", "?", "|", "-->"))
            starts_new_block = stripped[0] in "#-*+>0123456789|<"
            if not ends_sentence and not starts_new_block:
                findings.append(f"line {number}: {stripped[:70]}")
        previous = stripped
        previous_hard_break = line.endswith("  ") and not line.endswith("   ")
    return findings


def run_tool(name, *args):
    return subprocess.run([sys.executable, "-B", str(SYNC / name), *args], cwd=ROOT, capture_output=True, text=True)


def main():
    module = load_module()
    agents = module.load_agents()
    names = {agent.name for agent in agents}
    assert len(agents) == 23, len(agents)
    for agent in agents:
        assert agent.model == EXPECTED_TIERS.get(agent.name, "haiku"), (agent.name, agent.model)
        assert agent.read_only == (agent.name in READ_ONLY), agent.name
        for forbidden in ("fork_turns", "fork_context", "$imagegen", "ImageGen", "AGENTS.md", ".codex/agents/*.toml"):
            assert forbidden not in agent.body, (agent.name, forbidden)
    assert not any("state_ledger" in agent.name for agent in agents)

    profiles = module.load_profiles()
    for runtime_key in ("codex", "cursor", "qoder", "opencode", "claude"):
        assert module.synchronize([runtime_key], check=True) == 0, runtime_key
        outputs = module.expected_outputs(runtime_key, agents, profiles)
        for agent in agents:
            if runtime_key == "codex":
                path = ROOT / ".codex" / "agents" / f"{agent.snake_name}.toml"
                content = outputs[path]
                assert 'fork_turns="none"' in content and "fork_context=false" in content, agent.name
                assert "CLAUDE.md" not in content, agent.name
                if tomllib is not None:
                    data = tomllib.loads(content)
                    assert data["name"] == agent.snake_name
                    assert data["sandbox_mode"] == ("read-only" if agent.read_only else "workspace-write")
                    assert data["model_reasoning_effort"] == profiles["codex"]["tiers"][agent.model]["model_reasoning_effort"]
            elif runtime_key == "claude":
                continue
            else:
                folder = "agent" if runtime_key == "opencode" else "agents"
                content = outputs[ROOT / f".{runtime_key}" / folder / f"{agent.name}.md"]
                assert agent.description in content
                assert "by .tools/sync/sync_agents.py" in content
                assert "image-generation MCP workflow" not in content
    if tomllib is not None:
        config = tomllib.loads((ROOT / ".codex" / "config.toml").read_text(encoding="utf-8"))
        registered = {name for name in config["agents"] if isinstance(config["agents"][name], dict)}
        assert registered == {name.replace("-", "_") for name in names}, registered ^ {name.replace("-", "_") for name in names}

    for tool in ("sync_instructions.py", "check_guidance_size.py"):
        result = run_tool(tool, "--check") if tool.startswith("sync") else run_tool(tool)
        assert result.returncode == 0, (tool, result.stdout, result.stderr)
    result = run_tool("sync_skills.py", "--check")
    assert result.returncode == 0, result.stdout

    settings = json.loads((ROOT / ".claude" / "settings.json").read_text(encoding="utf-8"))
    mcp = json.loads((ROOT / ".mcp.json").read_text(encoding="utf-8"))
    assert settings["$schema"] == "https://json.schemastore.org/claude-code-settings.json"
    assert mcp["mcpServers"]["hoi4_agent_tools"]["command"] == "hoi4-agent-tools.cmd"
    for runtime in ("cursor", "qoder", "opencode"):
        runtime_settings = json.loads((ROOT / f".{runtime}" / "settings.json").read_text(encoding="utf-8"))
        assert runtime_settings["agents"]["source"] == ".claude/agents"

    template = (ROOT / "CLAUDE_template.md").read_text(encoding="utf-8")
    for required in ("[MOD_NAME]", "[MOD_PREFIX]", "[HOI4_GAME_DIR]", "## Placeholder Guide", "## 0. Required Reading", "## 1. Coding Style", "## 5. Completion", "## 10. Git", "### Agent runtimes", "#### Claude Code runtime", "#### DeepSeek Harness (DSH) runtime", "docs/runtimes.md", "sync_agents.py", "| Opus | `hoi4_improvement_loop_planner` |"):
        assert required in template, required
    for forbidden in ("ImageGen", "$imagegen", "Program Files (x86)/Steam/steamapps/common/Hearts of Iron IV/", "sync_claude_agents", "OneDrive", "klimp", "Chaos Redux", "chaosx"):
        assert forbidden not in template.replace("for example `C:/Program Files (x86)/Steam/steamapps/common/Hearts of Iron IV`", ""), forbidden
    markers = re.findall(r"<!-- HOI4_MOD_SETUP:COMPONENT:([a-z0-9._]+):(START|END) -->", template)
    stack = []
    for component, kind in markers:
        if kind == "START":
            assert not stack, f"nested component block {component}"
            stack.append(component)
        else:
            assert stack and stack.pop() == component, f"unbalanced component block {component}"
    assert not stack and markers, "component blocks must be balanced"
    agents_template = (ROOT / "AGENTS_template.md").read_text(encoding="utf-8")
    assert "native ImageGen" in agents_template and "image-generation MCP workflow" not in agents_template

    runtimes_doc = (ROOT / "docs" / "runtimes.md").read_text(encoding="utf-8")
    assert "@path" in runtimes_doc and "mcp__" in runtimes_doc and "sync_skills.py" in runtimes_doc

    for path in ("CLAUDE_template.md", "AGENTS_template.md", "docs/runtimes.md", ".tools/sync/README.md"):
        wraps = hard_wraps((ROOT / path).read_text(encoding="utf-8"))
        assert not wraps, f"{path} has mid-sentence hard wraps: {wraps[:3]}"

    print(f"Runtime synchronization contract passed for {len(agents)} canonical agents and 4 projected runtimes.")


if __name__ == "__main__":
    main()
