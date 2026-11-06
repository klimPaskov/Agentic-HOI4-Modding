# Project rules: Agent runtimes

Part of the [hoi4-project-rules](../SKILL.md) skill. `CLAUDE.md` summarizes section 0 (Agent runtimes). Read before editing a canonical instruction, skill or agent file, or when working in a client other than Claude Code.

### Agent runtimes

HOI4 Mod Setup lets you choose any supported coding client. This package keeps canonical instructions, skills, and agent definitions together under `.claude`, then creates the matching files for the clients you select. Do not assume the selected client is Claude Code.

- `CLAUDE.md`: project instructions. `AGENTS.md` is generated from it.
- `.claude/skills/<name>/SKILL.md`: the skill library. `.agents/skills/` and each client's own skill folder (`.qoder/`, `.grok/`, `.kiro/`, `.qwen/`) are generated copies.
- `.claude/agents/<name>.md`: specialist subagents, with the Claude model tier in the `model` field. Every other client's agents are generated from them.
- `.claude/settings.json` and the root `.mcp.json`: shared Claude Code settings and project MCP servers.

In Claude Code a hook regenerates the projections of each canonical file you edit; commit them with it. Elsewhere, regenerate after editing a canonical file and run it with `--check` during validation (`.tools/sync/generators.json` lists every generator):

```powershell
python .tools/sync/generators.py
```

Never hand-edit a generated file; edit the canonical file and regenerate. Agents working in another runtime edit the same canonical files and run the same command, or report that they could not. Runtime settings that are not part of a prompt, such as the Codex reasoning effort for each Claude tier, live in `.tools/sync/agent_profiles.json`.

- Each runtime owns its MCP registration. Do not copy one runtime's approval, sandbox, absolute-path, environment, or tool-allowlist settings into another without a verified equivalent.

The per-runtime layout, discovery rules, instruction-file precedence, and model policy are documented in `docs/runtimes.md`. Read it before adapting a runtime-specific file.

#### Claude Code runtime

- Invoke a specialist through the `Agent` tool by its hyphen-case file name (`hoi4-repo-explorer` for the routing name `hoi4_repo_explorer`) and give it a fully explicit, self-contained task message. Subagents receive their own context plus `CLAUDE.md`; they do not inherit the parent conversation.
- Do not substitute the built-in `Explore`, `Plan`, or `general-purpose` agents for a named project specialist.
- Claude Code asks once before it starts a project-scoped MCP server. After approval, confirm the `hoi4_agent_tools` registration with `/mcp`.
- Keep credentials and personal overrides out of shared files; use environment variables and `.claude/settings.local.json` for machine-local values.

#### DeepSeek Harness (DSH) runtime

- DSH has no named-subagent registry, so write the role boundary, allowed and forbidden files, evidence format, handoff path, and any required model route into each delegated prompt, and record the route used in the handoff.
- `docs/runtimes.md` covers the DSH skill copy, `@path` handling, instruction budget and MCP profile registration.
