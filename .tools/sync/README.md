# Agent synchronizers

The Codex TOML definitions in `.codex/agents/` are the only authoring source for project subagents.
These one-way generators project those definitions into the Qoder, Cursor, OpenCode, and Claude Code runtime formats:

```powershell
python .tools/sync/sync_qoder_agents.py
python .tools/sync/sync_cursor_agents.py
python .tools/sync/sync_opencode_agents.py
python .tools/sync/sync_claude_agents.py
```

Run all four after changing a Codex definition.
After generation, use `--check` to fail on missing, outdated, stale, or authority-unmapped generated files.
Qoder, Cursor, and OpenCode runtime folders are machine-local and ignored. Claude Code project agents are generated and tracked so a checkout works immediately; they still must not be edited by hand.

The generators translate only runtime mechanics.
The prompt body remains the scope and authority contract, and repository-specific MCP registration stays a separate runtime setup step.
