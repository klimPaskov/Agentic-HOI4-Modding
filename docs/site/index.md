---
layout: default
title: Agentic HOI4 Modding
---
# Agentic HOI4 Modding

Build Hearts of Iron IV mods with Claude Code, reusable skills, specialist agents, an offline wiki, and two complementary MCP servers. Codex, Cursor, Qoder, and OpenCode use generated runtime files from the same Claude sources.

## Install with HOI4 Mod Setup

1. Download [HOI4 Mod Setup](https://github.com/klimPaskov/HOI4-Mod-Setup/releases/latest).
2. Choose a new mod or an existing Git project, then enter the mod name, prefix, game folder, and Workshop folder.
3. Select Claude Code or your preferred runtime and the workflows you need: core modding, portraits, 3D, Super Events, or live testing.
4. Review the planned changes and install. Open the mod in your coding client, approve the project MCP server, and check the connection.

The app installs the MCP releases pinned in the package manifest. Its update and repair flows preserve local additions and let you review instruction conflicts.

[Setup app screenshots](https://github.com/klimPaskov/HOI4-Mod-Setup/tree/main/docs/screenshots) show the install and maintenance screens.

## Install manually

Use Python 3.13, Node.js LTS with npm, Git, and an installed copy of HOI4. Start from the [package source](https://github.com/klimPaskov/Agentic-HOI4-Modding) or [release ZIP](https://github.com/klimPaskov/Agentic-HOI4-Modding/releases/latest/download/Agentic-HOI4-Modding.zip).

Copy `CLAUDE_template.md` as `CLAUDE.md`, replace all mod and game-path placeholders, and remove optional workflow blocks you do not install. Copy `.claude/`, `.mcp.json`, `.tools/sync/`, `.tools/mcp/`, `paradox_wiki/`, and the runtime and MCP integration guides into the mod. Run:

```powershell
python .tools/mcp/bootstrap_hoi4_agent_tools.py
```

For another runtime, copy its `.codex/`, `.cursor/`, `.qoder/`, or `.opencode/` folder (plus root `opencode.json` for OpenCode), then generate its project files:

```powershell
python .tools/sync/sync_instructions.py
python .tools/sync/sync_agents.py --runtime codex
python .tools/sync/sync_skills.py --target agents
```

Replace `codex` with `cursor`, `qoder`, or `opencode` as appropriate. Qoder needs `--target qoder`; Cursor and OpenCode read the canonical skill root directly. On Windows, use `py -3.13` if `python` selects an older installation.

For optional workflows, copy the complete tools, references, and runtime assets declared in the manifest. Follow the [full installation guide](https://github.com/klimPaskov/Agentic-HOI4-Modding/blob/main/README.md) and [runtime reference](https://github.com/klimPaskov/Agentic-HOI4-Modding/blob/main/docs/runtimes.md).

## Skills and specialist agents

The [catalog](https://github.com/klimPaskov/Agentic-HOI4-Modding/blob/main/docs/catalog.md) explains all 32 skills and 23 agents. Skills cover focus trees, decisions, events, engine systems, planning, assets, portraits, 3D, scripted GUI, saves, live testing, and Super Events. Specialist agents research, implement bounded systems, produce assets, or audit completion with explicit ownership and evidence.

Claude routing uses **Opus** for the improvement planner; **Sonnet** for 3D, completion, localisation, architecture, and skill maintenance; and **Haiku** for the other agents. Claude agents explicitly set effort to `xhigh`, `high`, or `medium` where supported. Codex translates those tiers to per-agent `xhigh`, `high`, and `medium` reasoning effort.

## Two MCP servers

**HOI4 Agent Tools** (`hoi4_agent_tools`) works with mod source: focus and technology trees, events, weighted logic, scripted GUIs, maps, documentation, and source lookup. The project bootstrap installs and verifies the manifest-pinned npm package.

**HOI4 Live Tools** (`hoi4-live`) works with the running game on Windows: launch and load, events and effects, time advancement, popups, screen evidence, saves, and error-log changes. It installs per user and registers with supported clients. For manual installation:

```powershell
python .tools/mcp/bootstrap_hoi4_live_tools.py
```

Reconnect the client and follow the [Live Tools setup guide](https://github.com/klimPaskov/Agentic-HOI4-Modding/blob/main/.claude/skills/hoi4-live-playtest/references/setup.md). Use live testing when the task authorizes it. The optional 3D workflow adds Meshy and Blender MCP routes through its own bootstrap.

## Watch the workflow

- [Setup app tutorial MP4](https://github.com/klimPaskov/Agentic-HOI4-Modding/releases/latest/download/setup_app_tutorial.mp4).
- [HOI4 Agent Tools promo MP4](https://github.com/klimPaskov/Agentic-HOI4-Modding/releases/latest/download/hoi4_agent_tools_promo.mp4).
- [Video tutorial playlist](https://www.youtube.com/playlist?list=PLh6JmuEabQioc4V8IYGEsMtqiw-xemeX3).

![Choose coding environments in HOI4 Mod Setup](https://raw.githubusercontent.com/klimPaskov/HOI4-Mod-Setup/main/docs/screenshots/15-coding-environments.png)

## License

Original package code and guidance use the [Apache License 2.0](https://github.com/klimPaskov/Agentic-HOI4-Modding/blob/main/LICENSE). Third-party material retains its own terms; see [NOTICE](https://github.com/klimPaskov/Agentic-HOI4-Modding/blob/main/NOTICE).

## Upgrade an older checkout

Back up and commit your mod work, then use the setup app to update or repair the package and MCP installation. Review custom instruction merges, regenerate runtime files from the Claude sources, and reconnect clients. Older Codex-first packages and Agent Tools 3.9.0 need this migration before using the new workflow.
