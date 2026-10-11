# Agentic HOI4 Modding

[![Discord](https://img.shields.io/badge/Discord-Join%20Community-7289da?logo=discord&logoColor=white)](https://discord.gg/rAXesGcT2t)

A reusable starting kit for building Hearts of Iron IV mods with coding agents. It includes project instructions, an offline Paradox wiki snapshot, reusable skills, specialist subagents with per-role model tiers, the HOI4 Agent Tools MCP server setup, and optional workflows for portraits, 3D models, Super Events, and live game testing.

Claude Code is the primary environment. Every instruction file, skill, and subagent is authored for Claude Code, and the Codex, Cursor, Qoder, OpenCode, and DeepSeek Harness files are generated from those sources.

[Download the complete package](https://github.com/klimPaskov/Agentic-HOI4-Modding/releases/latest/download/Agentic-HOI4-Modding.zip) · [Video tutorials](https://www.youtube.com/playlist?list=PLh6JmuEabQioc4V8IYGEsMtqiw-xemeX3)

## Get started

Use [HOI4 Mod Setup](https://github.com/klimPaskov/HOI4-Mod-Setup/releases/latest) to create a mod or prepare an existing one. The app selects and adapts the files for your mod, fills in your mod name, prefix, and game folder, installs and registers the HOI4 Agent Tools server, previews every change, and can update, repair, or remove the setup later.

For a manual setup:

1. Put your mod in a Git repository and open that repository as the agent's workspace.
2. Copy [CLAUDE_template.md](CLAUDE_template.md) to your mod as `CLAUDE.md` and replace its placeholders (`[MOD_NAME]`, `[MOD_PREFIX]`, `[HOI4_GAME_DIR]`, `[STEAM_WORKSHOP_DIR]`). Delete the blocks for optional workflows you do not install.
3. Copy `.claude/skills/`, `.claude/agents/`, `.claude/settings.json`, `.mcp.json`, and `.tools/sync/` into the mod. Make the installed game files and the included `paradox_wiki/` snapshot readable to the agent.
4. If you also use another runtime, generate its files from the Claude sources:

   ```powershell
   python .tools/sync/sync_instructions.py   # AGENTS.md
   python .tools/sync/sync_agents.py --runtime codex   # or cursor, qoder, opencode
   python .tools/sync/sync_skills.py --target agents   # .agents/skills for Codex and DSH
   ```

5. Copy `.tools/mcp/` and `docs/runtimes.md` plus `docs/systems/hoi4_agent_tools_mcp_integration.md` into the mod. Install Python 3.13 and a supported Node.js LTS release with npm available on PATH. On Windows, `py -3.13` can replace `python` in these commands.
6. Install HOI4 Agent Tools with `python .tools/mcp/bootstrap_hoi4_agent_tools.py`, then approve the `hoi4_agent_tools` server when Claude Code asks and check it with `/mcp`.

7. For live game testing on Windows, run `python .tools/mcp/bootstrap_hoi4_live_tools.py`, reconnect your coding client, and follow the [Live Tools setup guide](.claude/skills/hoi4-live-playtest/references/setup.md). For portraits, 3D, or Super Events, copy the selected workflow's references, tools, and runtime assets together; use the [manifest](hoi4-mod-setup.manifest.json) as the file inventory. The setup app handles this selection automatically.

The templates are starting points. Keep only the workflows your mod uses and add project rules as the mod develops.

## How the files fit together

| Canonical source | Purpose | Generated for other runtimes |
| --- | --- | --- |
| `CLAUDE.md` (`CLAUDE_template.md` here) | Project instructions | `AGENTS.md` |
| `.claude/skills/<name>/SKILL.md` | Reusable HOI4 workflows and their references | `.agents/skills/` (Codex, DSH), `.qoder/skills/` (Qoder) |
| `.claude/agents/<name>.md` | Specialist subagents with a Claude model tier | `.codex/agents/*.toml`, `.cursor/agents/`, `.qoder/agents/`, `.opencode/agent/` |
| `.mcp.json`, `.claude/settings.json` | Claude Code MCP registration and settings | Each runtime's own MCP file |

Edit only the canonical files and rerun the synchronizers in [`.tools/sync/`](.tools/sync/README.md); add `--check` to find stale projections. [Runtime details](docs/runtimes.md) cover what each runtime reads.

## Subagent model tiers

Each subagent declares its Claude tier in its `model` field so cost and capability stay fixed per role:

- **Opus**: improvement loop planner.
- **Sonnet**: 3D model pipeline, feature completion auditor, localisation auditor, scripted system architect, skill maintainer.
- **Haiku**: every other specialist (repo explorer, focus tree, decision, country package, and AI probability auditors, event UI worker, documentation curator, asset, icon, portrait, quote, and audio workers, spreadsheet worker, Super Events researchers).

Other runtimes translate the tier through [`.tools/sync/agent_profiles.json`](.tools/sync/agent_profiles.json), for example into a Codex reasoning effort.

## Skills and agents

The [complete catalog](docs/catalog.md) describes all 32 skills and 23 agents, with links to their definitions and each agent's model tier and Codex reasoning effort. Skills guide the workflow; agents take bounded tasks with explicit file ownership and evidence requirements.

## Screenshots and videos

- [Setup app screenshots](https://github.com/klimPaskov/HOI4-Mod-Setup/tree/main/docs/screenshots): project creation, component selection, MCP configuration, review, and maintenance.
- [Setup tutorial MP4](https://github.com/klimPaskov/Agentic-HOI4-Modding/releases/latest/download/setup_app_tutorial.mp4) and [Agent Tools promo MP4](https://github.com/klimPaskov/Agentic-HOI4-Modding/releases/latest/download/hoi4_agent_tools_promo.mp4): release assets to upload with this release; these links become available after upload.
- [Video tutorial playlist](https://www.youtube.com/playlist?list=PLh6JmuEabQioc4V8IYGEsMtqiw-xemeX3).
- [GitHub Pages guide](https://klimpaskov.github.io/Agentic-HOI4-Modding/).

## Updating an older installation

Back up and commit local mod work first. Use HOI4 Mod Setup's update or repair flow to review changes to managed files and keep local additions. An older Codex-first checkout with HOI4 Agent Tools 3.9.0 needs an update to this Claude-first package and the manifest-pinned MCP release. Keep custom instructions when resolving conflicts, regenerate runtime projections, and reconnect MCP clients after installation.

## Skill size

Every skill, agent prompt, and instruction file must be readable in one pass. [`.tools/sync/read_limits.json`](.tools/sync/read_limits.json) sets a 20,000-token ceiling, and `python .tools/sync/check_guidance_size.py` reports any file above it. The ceiling is a limit, not a target: large skills keep their full rules and move complete topics into linked `references/` files.

## MCP servers

- **HOI4 Agent Tools** (`hoi4_agent_tools`): source-level tools for focus trees, events, technology trees, weighted logic, scripted GUIs, maps, documentation, and source lookup. HOI4 Mod Setup installs the release recorded in `hoi4-mod-setup.manifest.json` and registers it for the coding environments you choose. Agents use whatever routes the connected server advertises.
- **HOI4 Live Tools** (`hoi4-live`, optional, Windows): drives a running game for live feature tests and campaign play. HOI4 Mod Setup installs the release recorded in `hoi4-mod-setup.manifest.json` for your user and registers it for the coding clients it finds (`python .tools/mcp/bootstrap_hoi4_live_tools.py` does the same by hand). The `hoi4-live-playtest` skill and its [setup guide](.claude/skills/hoi4-live-playtest/references/setup.md) explain how agents use it; `hoi4-debug-playtest` plays through it.
- **Meshy and Blender** (optional 3D workflow): registered by `.tools/3d_pipeline/bootstrap_3d_workflow.py` when a feature needs a model.

## What's inside

| Folder | Purpose |
| --- | --- |
| `.claude/skills/` | Reusable HOI4 workflows and their references |
| `.claude/agents/` | Specialist subagent definitions |
| `.codex/`, `.cursor/`, `.qoder/`, `.opencode/` | Generated runtime packages |
| `paradox_wiki/` | Offline wiki reference |
| `.tools/` | Runtime synchronizers, wiki, MCP bootstrap, and optional 3D tooling |
| `docs/` | Runtime reference, MCP integration contract, and the Super Events guide |
| `hoi4-mod-setup.manifest.json` | File selection and verification for HOI4 Mod Setup |

The project instructions and each selected skill define the work and evidence required for a feature. A generated asset or passing tool result still needs the relevant game files wired and reviewed.

## License

This repository has no declared package license. Resolve the package license and third-party redistribution permissions before public release; the manifest records unverified license evidence. The [Super Events asset lineage](docs/super_events/README.md) and offline wiki require separate review. See [RELEASING.md](RELEASING.md) for release checks and publication steps.
