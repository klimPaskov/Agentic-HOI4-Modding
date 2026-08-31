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
All four runtime projections are checked in so a fresh checkout works immediately. They are generated artifacts, not authoring sources, and must not be edited by hand. The setup manifest packages optional Portrait Production and Super Events projections separately from each runtime's core agents. Qoder's map lives at `.qoder/agent-map.md`; its project and Windows-only MCP settings are `.qoder/settings.json` and `.qoder/mcp.json`.

The generators translate only runtime mechanics.
The prompt body remains the scope and authority contract. Native project settings and MCP registration are distributed with the selected runtime package and remain provider-neutral.
