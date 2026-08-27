# Claude Code Project Instructions

@AGENTS.md

## Claude Code Runtime

Treat the imported `AGENTS.md` as the project workflow authority.
Canonical custom-subagent prompts live in `.codex/agents/*.toml`; `.claude/agents/*.md` files are generated Claude Code projections and must not be hand-edited.
After changing a canonical prompt, run `python .tools/sync/sync_claude_agents.py` and then `python .tools/sync/sync_claude_agents.py --check`.

Invoke the generated lowercase hyphen-case specialist through Claude Code's `Agent` tool and give it a fully explicit, self-contained task message.
Claude Code subagents receive their own context plus project `CLAUDE.md`; do not assume they inherit the parent conversation.
Read and follow every applicable skill from `.agents/skills/<skill-name>/SKILL.md` before changing an owned surface.

The project-scoped HOI4 MCP registration lives in `.mcp.json`.
Claude Code requires a one-time trust decision before using a project-scoped MCP server; after trust, verify `hoi4_agent_tools` with `/mcp` and require its advertised routes exactly as described in `AGENTS.md`.
Keep credentials and personal overrides out of shared files; use environment variables and `.claude/settings.local.json` for machine-local values.
