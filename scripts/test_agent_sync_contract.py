#!/usr/bin/env python3
"""Contract checks for alternate-runtime subagent generation."""

import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / ".tools" / "sync" / "agent_sync_common.py"


def load_module():
    spec = importlib.util.spec_from_file_location("agent_sync_common", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main():
    module = load_module()
    agents = module.load_agents()
    assert len(agents) == len(module.AUTHORITY) == 23
    assert not any("state_ledger" in agent.name or "state-ledger" in agent.body.lower() for agent in agents)
    assert not any("Codex's official $imagegen skill" in agent.body for agent in agents)
    assert not any("restart the shell or Codex" in agent.body for agent in agents)

    settings = json.loads((ROOT / ".claude" / "settings.json").read_text(encoding="utf-8"))
    mcp = json.loads((ROOT / ".mcp.json").read_text(encoding="utf-8"))
    claude_template = (ROOT / "CLAUDE_template.md").read_text(encoding="utf-8")
    assert settings["$schema"] == "https://json.schemastore.org/claude-code-settings.json"
    assert mcp["mcpServers"]["hoi4_agent_tools"]["command"] == "hoi4-agent-tools.cmd"
    assert "@AGENTS.md" in claude_template

    for runtime_key, runtime in module.RUNTIMES.items():
        outputs = module.expected_outputs(runtime, agents)
        assert len(outputs) == 24
        assert runtime.map_path in outputs
        for agent in agents:
            path = runtime.agent_dir / f"{agent.runtime_name}.md"
            content = outputs[path]
            assert agent.description in content
            assert "fork_context=false" not in content
            assert "Agent Nudger writes" not in content
            if runtime_key == "qoder":
                assert "tools:" in content
            elif runtime_key == "cursor":
                assert f"name: {agent.runtime_name}" in content
                assert "model: inherit" in content
            elif runtime_key == "opencode":
                assert "mode: subagent" in content
                assert "model: inherit" in content
            else:
                assert f"name: {agent.runtime_name}" in content
                assert "model: inherit" in content
                if module.AUTHORITY[agent.name] == module.READ_ONLY:
                    assert "disallowedTools: Write, Edit, NotebookEdit" in content
                else:
                    assert "disallowedTools:" not in content

    print("Agent synchronization contract passed for 23 agents and 4 runtimes.")


if __name__ == "__main__":
    main()
