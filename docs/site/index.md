---
layout: default
title: Agentic HOI4 Modding
---
# Agentic HOI4 Modding

Build Hearts of Iron IV mods with your coding agent. Make focus trees, events, decisions and maps, fix broken script and balance the AI. Modding skills, specialist helpers, an offline wiki and HOI4 tools help your agent do the work.

Choose any supported coding client, including Claude Code, Codex, Cursor, Qoder, or OpenCode. HOI4 Mod Setup creates project files and registers tools for the clients you select.

## Install with HOI4 Mod Setup

1. Download [HOI4 Mod Setup](https://github.com/klimPaskov/HOI4-Mod-Setup/releases/latest).
2. Choose a new mod or an existing Git project, then enter the mod name, prefix, game folder, and Workshop folder.
3. Select any supported coding client and the workflows you need: core modding, image generation, portraits, 3D, Super Events, or live testing.
4. Review the planned changes and install. Open the mod in your coding client, approve the project MCP server, and check the connection.

The app installs the MCP releases pinned in the package manifest. Its update and repair flows preserve local additions and let you review instruction conflicts. You can change the image provider later and have the app update its MCP registrations and guidance.

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

The [catalog](https://github.com/klimPaskov/Agentic-HOI4-Modding/blob/main/docs/catalog.md) covers focus trees, decisions, events, game systems, interfaces, assets, portraits, 3D models, live testing and Super Events. Describe the task; your agent chooses the skills and specialists it needs.

Specialist roles use model tiers matched to the work. The package maps those tiers to settings supported by each selected coding client.

## Image generation and modding tools

HOI4 Mod Setup selects ChatGPT through the GPTImage MCP by default. You can choose another hosted or local provider, use Codex image generation, or make art yourself. The app keeps API keys in the operating-system credential store and updates the asset guidance for your choice. See the [provider research](../image-generation-providers.md) for models, access needs, costs, and size limits.

## Modding and live testing

**HOI4 Agent Tools** (`hoi4_agent_tools`) helps your agent build focus trees, events, decisions and maps, preview windows and trees, find modding rules, fix script and balance AI choices. The project bootstrap installs the release selected by the package manifest.

**HOI4 Live Tools** (`hoi4-live`) works with the running game on Windows: launch and load, events and effects, time advancement, popups, screen evidence, saves, and error-log changes. It installs per user and registers with supported clients. For manual installation:

```powershell
python .tools/mcp/bootstrap_hoi4_live_tools.py
```

Reconnect the client and follow the [Live Tools setup guide](https://github.com/klimPaskov/Agentic-HOI4-Modding/blob/main/.claude/skills/hoi4-live-playtest/references/setup.md). The optional 3D workflow adds Meshy and Blender MCP routes through its own bootstrap.

## Watch the workflow

- [Setup app tutorial MP4](https://github.com/klimPaskov/Agentic-HOI4-Modding/releases/latest/download/setup_app_tutorial.mp4).
- [HOI4 Agent Tools promo MP4](https://github.com/klimPaskov/Agentic-HOI4-Modding/releases/latest/download/hoi4_agent_tools_promo.mp4).
- [Video tutorial playlist](https://www.youtube.com/playlist?list=PLh6JmuEabQioc4V8IYGEsMtqiw-xemeX3).

![Choose coding environments in HOI4 Mod Setup](images/setup-coding-environments.png)

![Choose an image-generation provider in HOI4 Mod Setup](images/setup-image-generation.png)

## License

Original package code and guidance use the [Apache License 2.0](https://github.com/klimPaskov/Agentic-HOI4-Modding/blob/main/LICENSE). Third-party material retains its own terms; see [NOTICE](https://github.com/klimPaskov/Agentic-HOI4-Modding/blob/main/NOTICE).

## Upgrade an older checkout

Back up and commit your mod work, then use the setup app to update or repair the package and MCP installation. Review custom instruction changes, regenerate runtime files for your selected coding clients, and reconnect them.
