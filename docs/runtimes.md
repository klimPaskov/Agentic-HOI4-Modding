# Agent runtimes

This repository can be opened in more than one coding-agent runtime.
The HOI4 rules themselves are runtime-neutral; only the discovery paths, the subagent registry, and MCP registration differ per runtime.

The package keeps canonical instruction, skill, and subagent sources under `.claude`. Choose any supported coding client; the setup app creates the matching client files.
Every other runtime reads a generated projection of the same instructions, skills, and subagents.
Edit the canonical file, then regenerate the projections with the synchronizers in `.tools/sync/`.

| Canonical source | Projection | Synchronizer |
| --- | --- | --- |
| `CLAUDE.md` | `AGENTS.md` | `python .tools/sync/sync_instructions.py` |
| `.claude/skills/<name>/` | `.agents/skills/<name>/` (Codex, DSH), `.qoder/skills/<name>/` (Qoder) | `python .tools/sync/sync_skills.py` |
| `.claude/agents/<name>.md` | `.codex/agents/<name>.toml` and the `[agents.*]` registry in `.codex/config.toml`, `.cursor/agents/`, `.qoder/agents/`, `.opencode/agent/`, and every `agent-map.md` | `python .tools/sync/sync_agents.py` |

Run each synchronizer with `--check` during validation; it exits with status 1 when a projection is out of date.
Never hand-edit a projection.

## Instruction files

Each runtime loads its project instructions from a different file name.

| Runtime | Project instruction file | Discovery |
| --- | --- | --- |
| Claude Code | `CLAUDE.md` (canonical) | Project root. `@path` import lines are interpreted. |
| Codex | `AGENTS.md` | Project root, bounded by the configured project-document byte budget. |
| DSH | `AGENTS.md` and `CLAUDE.md` | Every directory from the project root down to the working directory, broad-to-specific, plus the user-global `$DSH_HOME/AGENTS.md`. |
| Cursor | `AGENTS.md` | Declared in `.cursor/settings.json`. |
| Qoder | `AGENTS.md` | Declared in `.qoder/settings.json`. |
| OpenCode | `AGENTS.md` | Declared in `.opencode/settings.json` and the root `opencode.json`. |

`AGENTS.md` is a projection of `CLAUDE.md`. It keeps provider-neutral image guidance until HOI4 Mod Setup fills the marked section from the selected image-generation provider table.
The source package ships `CLAUDE_template.md` and its projection `AGENTS_template.md`; HOI4 Mod Setup adapts both for a new mod.

Consequences worth knowing:

- DSH does **not** interpret `@path` import lines.
- DSH collapses sibling files in one directory only when their content is byte-identical after trimming surrounding whitespace. Because `AGENTS.md` differs from `CLAUDE.md` in a few runtime phrases, DSH loads both.
- DSH caps the whole rendered instruction baseline at 65,536 bytes by default, and a single source file above 1 MiB is not loaded at all. It drops broader files whole before it truncates the most specific one and reports the omission in a visible `Workspace instruction budget` notice. Split rarely used detail into skills or `docs/` pages that the agent reads on demand.
- DSH finds the project root by the nearest ancestor containing `.git`. Without a `.git` marker, discovery falls back to the working directory and instructions above it stay invisible.
- Cursor, Qoder, and OpenCode read the file named in their own settings. Renaming the project instructions without updating those settings silently removes all project rules.
- DSH and Claude Code both accept local overlays: `CLAUDE.local.md` and `AGENTS.local.md`. Keep machine-local paths, credentials, and personal preferences there, and keep them out of Git.

## Skills

| Runtime | Skill root it reads |
| --- | --- |
| Claude Code | `.claude/skills/` (canonical) |
| Cursor | `.claude/skills/` as a compatibility root, plus `.cursor/skills/` and `.agents/skills/` |
| OpenCode | `.claude/skills/` as a compatibility root, plus `.opencode/skills/` and `.agents/skills/` |
| Codex | `.agents/skills/` (copy) |
| DSH | `<project_root>/.dsh/skills` and `<project_root>/.agents/skills` (copy), then configured, user, and bundled roots |
| Qoder | `.qoder/skills/` (copy) |

`python .tools/sync/sync_skills.py` refreshes every copy that exists; `--target agents` or `--target qoder` creates one.
Copies are the default because HOI4 Mod Setup tracks the files it installs; `--mode link` replaces a copy with a junction or symbolic link in a project that does not use the app.
A skill folder that exists only in a copy is reported and left alone.
Cursor and OpenCode would see a skill twice if both `.claude/skills/` and an `.agents/skills/` copy exist; both copies are identical, so the duplicate is harmless.

A skill is `<name>/SKILL.md` or a flat `<name>.md` at the top of a scanned root; nested `SKILL.md` files below the first level are not discovered.
Frontmatter requires `name` and `description`; `name` must be kebab-case and match the bundle or file name.
DSH additionally accepts an optional `whenToUse` string, and reads `metadata`, `disable-model-invocation`, and `user-invocable` as optional keys. It rejects the camel-case spellings of the two invocation keys with an explicit warning instead of ignoring them.
A skill with missing or invalid frontmatter is skipped with a warning rather than surfaced as broken, so a skill that does not appear in the catalog usually has a frontmatter problem.

Every skill, agent prompt, and instruction file must stay within the single-read ceiling in `.tools/sync/read_limits.json`; `python .tools/sync/check_guidance_size.py` reports a file above it.

## Subagents

The canonical definitions are Claude Code subagent files: `.claude/agents/<hyphen-name>.md` with `name`, `description`, `model` (`opus`, `sonnet`, or `haiku`), `effort`, and `disallowedTools: Write, Edit, NotebookEdit` for read-only roles.
Prose uses the snake_case routing name (`hoi4_repo_explorer`); the Claude, Cursor, Qoder, and OpenCode files use the hyphen form and the Codex file uses the snake form.

| Runtime | Registry | Source |
| --- | --- | --- |
| Claude Code | `.claude/agents/<hyphen-name>.md` | Canonical. |
| Codex | `.codex/agents/<snake_name>.toml`, registered by `[agents.<snake_name>]` rows in `.codex/config.toml` | Generated by `sync_agents.py`. |
| Cursor | `.cursor/agents/<hyphen-name>.md` | Generated. |
| Qoder | `.qoder/agents/<hyphen-name>.md` | Generated. |
| OpenCode | `.opencode/agent/<hyphen-name>.md` | Generated. |
| DSH | None | Not applicable. |

`sync_agents.py` maintains a projection only for runtimes whose folder exists in the project, removes projection files it generated earlier when their canonical agent is gone, and rewrites only the `[agents.*]` rows of `.codex/config.toml` that point at generated TOML files.
The prompt text is shared; a few runtime phrases change, for example "spawned without inherited conversation context" becomes `fork_turns="none"` for Codex.

DSH is the exception.
It ships no project-local registry of named subagents, so no name, description, sandbox, or model field reaches a DSH subagent.
In DSH the snake_case identifiers remain routing and ownership contracts, and the parent must write the role boundary, allowed files, forbidden files, ownership limits, evidence format, and handoff path into the delegated prompt itself.
Because no definition supplies the model, confirm the child route explicitly when the task depends on a particular model or reasoning effort, and record the route that was actually used in the handoff.

## Model selection

Each canonical agent declares its Claude tier in the `model` field, which keeps cost and capability fixed per role instead of following the parent session.
The project instructions list the tier of every role.

Claude definitions set `effort` per agent: Opus `xhigh`, Sonnet `high`, and Haiku `medium`. Models use the field where they support effort controls; the `CLAUDE_CODE_EFFORT_LEVEL` environment variable overrides it. See the [official Claude subagent effort reference](https://code.claude.com/docs/en/sub-agents#choose-an-effort-level).

Other runtimes translate the tier through `.tools/sync/agent_profiles.json`:

- Codex: the tier sets `model_reasoning_effort` (and, when configured, `model`); the read-only or editing authority sets `sandbox_mode`. Without a `model` entry the agent uses the session's model.
- Cursor and OpenCode: `model: inherit`.
- Qoder: the authority sets the tool list.

Change a role's tier in its canonical file and rerun `sync_agents.py`; change a runtime's translation in `agent_profiles.json`.
Keep provider credentials out of shared files.

## MCP registration

Each runtime owns its own MCP registration.
Do not copy one runtime's approval, sandbox, absolute-path, environment, or tool-allowlist keys into another runtime unless that runtime has a verified equivalent.

| Runtime | Registration file | Shape |
| --- | --- | --- |
| Claude Code | `.mcp.json` | `{"mcpServers": {"<name>": {"type": "stdio", "command": "...", "args": [], "env": {}}}}`. Claude Code asks once before it starts a project server. |
| Codex | `.codex/config.toml` | `[mcp_servers.<name>]` with `command`, optional `cwd`, timeouts, and approval mode. |
| Cursor | `.cursor/mcp.json` | `{"mcpServers": {"<name>": {"command": "...", "args": []}}}`. |
| Qoder | `.qoder/mcp.json` | `{"mcpServers": {"<name>": {"command": "...", "args": []}}}`. |
| OpenCode | `.opencode/mcp.json` | `{"mcpServers": {"<name>": {"command": ["..."]}}}`. |
| DSH | `$DSH_HOME/profiles/<profile>/cordis.patch.yml` | A loader patch row inserting `@deepseek-ai/dsh-mcp-client`, one row per server. |

On Windows every project-scoped file above points at the `hoi4-agent-tools.cmd` wrapper that npm installs globally; HOI4 Mod Setup and `.tools/mcp/bootstrap_hoi4_agent_tools.py` install the release recorded in `hoi4-mod-setup.manifest.json`.

On native Linux, HOI4 Mod Setup adapts the registrations for every selected coding client to the verified absolute Node executable and package entry. The current-user npm prefix is `$XDG_DATA_HOME/hoi4-mod-setup/npm`, or `~/.local/share/hoi4-mod-setup/npm` when XDG_DATA_HOME is unset. The native `bin/hoi4-agent-tools` locator points to the reviewed entry; setup verifies it and launches the entry directly. Shared skill and agent projections remain identical across platforms. The source package's raw MCP examples use Windows commands, so manual Linux setup must adapt them as described in [the Linux guide](linux.md).

DSH has no project-scoped MCP file.
Its servers are deployment configuration, not repository content, so the registration lives in the active profile and stays out of Git.
One row per server, and the profile must also depend on the MCP client package:

```yaml
- id: mcp-hoi4-agent-tools
  name: '@deepseek-ai/dsh-mcp-client'
  config:
    serverName: hoi4_agent_tools
    transport: stdio
    command: hoi4-agent-tools.cmd
    cwd: "<path to your mod>"
    failOnStartupError: true
```

DSH namespaces every bridged tool as `mcp__<serverName>__<rawToolName>`, so the HOI4 routes appear in a session as `mcp__hoi4_agent_tools__hoi4_focus_inspect` and similar.
A `serverName` may only contain letters, digits, underscore, and hyphen.

### Live testing (optional)

Choose Clausewitz MCP (default), experimental HOI4 Live Tools, or None for manual testing. Common `workflow.live_testing` guidance works with all supported clients. HOI4 Mod Setup manages project registrations for the selected clients: Claude Code, Codex, Cursor, Qoder and OpenCode, using their project MCP files described above. It updates the selected route and guidance during update or repair.

Clausewitz MCP (`clausewitz_linux`) supports native Linux HOI4 1.19.2 only. Linux connects directly; Windows connects through WSL; macOS connects through SSH to Linux. Complete manual Linux, game and server setup, then confirm the Linux game and server are ready in HOI4 Mod Setup before registration.

HOI4 Live Tools (`hoi4-live`) is Windows verified only; upstream macOS support is incomplete. It is experimental, slower and not thoroughly tested. The app installs the pinned runtime under `%LOCALAPPDATA%\hoi4-live-tools` with `--quiet --register none`, then writes project registrations for selected clients. The manual bootstrap defaults to detected user-client registration; use `--register none` for runtime installation alone.

None registers no server. Agents provide bounded manual recipes and record user observations. No automatic desktop fallback is allowed. See `.claude/skills/hoi4-live-playtest/references/setup.md` for setup and troubleshooting, and inspect the selected server's advertised tools before each test.

The MCP evidence rules in the project instructions do not change per runtime: use the routes the connected server advertises, apply the bounded retry policy, and record an unavailable route once before continuing with local references.
