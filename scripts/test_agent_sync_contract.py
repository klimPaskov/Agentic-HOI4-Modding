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
        # A trailing double space in the source line is a deliberate markdown
        # line break, so this line is an intended continuation, not a hard wrap.
        if previous and stripped and not previous_hard_break:
            ends_sentence = previous.endswith((".", ":", ";", "!", "?", "|"))
            starts_new_block = stripped[0] in "#-*+>0123456789|"
            if not ends_sentence and not starts_new_block:
                findings.append(f"line {number}: {stripped[:70]}")
        previous = stripped
        previous_hard_break = line.endswith("  ") and not line.endswith("   ")
    return findings


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

    # The Claude template is a complete standalone instruction file. It must
    # carry the whole workflow, may not depend on an AGENTS.md import, and must
    # document that the import form is opt-in for projects that really keep both.
    assert "@AGENTS.md" in claude_template
    import_lines = [line for line in claude_template.splitlines() if line.strip() == "@AGENTS.md"]
    assert len(import_lines) == 1, "the template must show the import exactly once, as an opt-in example"
    for section in ("## 0. Required Reading", "## 1. Coding Style", "## 5. Completion Proof", "## 10. Git"):
        assert section in claude_template, f"standalone template is missing {section}"
    assert "### Agent runtimes" in claude_template
    assert "#### Claude Code runtime" in claude_template
    assert "#### DeepSeek Harness (DSH) runtime" in claude_template
    assert "docs/runtimes.md" in claude_template

    runtimes_doc = (ROOT / "docs" / "runtimes.md").read_text(encoding="utf-8")
    assert "@path" in runtimes_doc and "mcp__" in runtimes_doc

    for path in ("AGENTS_template.md", "CLAUDE_template.md", "docs/runtimes.md"):
        wraps = hard_wraps((ROOT / path).read_text(encoding="utf-8"))
        assert not wraps, f"{path} has mid-sentence hard wraps: {wraps[:3]}"

    for runtime_key, runtime in module.RUNTIMES.items():
        outputs = module.expected_outputs(runtime, agents)
        assert len(outputs) == 24
        # The projections are checked against the files committed in the
        # source repository, not only against the renderer's in-memory output.
        # This keeps every native runtime package derived from the canonical
        # Codex TOMLs and makes drift fail the source validation workflow.
        assert module.synchronize(runtime_key, check=True) == 0
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
