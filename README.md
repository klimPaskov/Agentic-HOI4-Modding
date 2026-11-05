<p align="center">
  <img src="https://raw.githubusercontent.com/klimPaskov/Agentic-HOI4-Modding/main/docs/images/logo.svg" width="96" height="96" alt="Agentic HOI4 Modding">
</p>

<h1 align="center">Agentic HOI4 Modding</h1>

<p align="center">
  Skills, specialist agents, an offline wiki and HOI4 tools that let your coding agent build <em>Hearts of Iron IV</em> mods.
</p>

<p align="center">
  <a href="https://github.com/klimPaskov/Agentic-HOI4-Modding/releases/latest"><img alt="Download" src="https://img.shields.io/github/v/release/klimPaskov/Agentic-HOI4-Modding?label=Download&logo=github&color=2ea44f"></a>
  <a href="https://discord.gg/rAXesGcT2t"><img alt="Discord" src="https://img.shields.io/badge/Discord-Join%20Community-7289da?logo=discord&logoColor=white"></a>
  <a href="https://www.youtube.com/@ChaosRedux"><img alt="YouTube" src="https://img.shields.io/badge/YouTube-Chaos%20Redux-ff0000?logo=youtube&logoColor=white"></a>
  <a href="https://ko-fi.com/klimpaskov"><img alt="Ko-fi" src="https://img.shields.io/badge/Ko--fi-Support%20the%20Project-ff5e5b?logo=kofi&logoColor=white"></a>
  <a href="https://github.com/klimPaskov/Agentic-HOI4-Modding/issues"><img alt="Issues" src="https://img.shields.io/badge/Bugs%20%26%20Ideas-Issues-24292f?logo=github&logoColor=white"></a>
</p>

<p align="center">
  <a href="#get-started">Get started</a> ·
  <a href="https://github.com/klimPaskov/Agentic-HOI4-Modding/blob/main/docs/catalog.md">Skills and agents</a> ·
  <a href="https://github.com/klimPaskov/Agentic-HOI4-Modding/blob/main/docs/manual-setup.md">Manual setup</a> ·
  <a href="https://github.com/klimPaskov/Agentic-HOI4-Modding/blob/main/docs/runtimes.md">Coding clients</a> ·
  <a href="https://klimpaskov.github.io/Agentic-HOI4-Modding/">Guide</a>
</p>

Make focus trees, events, decisions and maps, fix broken script and balance the AI. Works with Claude Code, Codex, Cursor, GitHub Copilot and [many more coding clients](https://github.com/klimPaskov/Agentic-HOI4-Modding/blob/main/docs/runtimes.md).

## Get started

1. Download **[HOI4 Mod Setup](https://github.com/klimPaskov/HOI4-Mod-Setup/releases/latest)** and create a mod or import an existing one.
2. Pick your coding client and the workflows you want. The app installs the kit, the HOI4 tools and the MCP registrations, and can update, repair or remove them later.
3. Open the mod in your coding client and describe what you want to build or fix.

Prefer to do it by hand? Follow the [manual setup](https://github.com/klimPaskov/Agentic-HOI4-Modding/blob/main/docs/manual-setup.md).

## What you get

- **Project instructions** (`CLAUDE.md`, or `AGENTS.md` for other clients) with your mod name, prefix and game folder.
- **Skills and specialist agents** for focus trees, events, decisions, country content, interfaces and assets. See the [catalog](https://github.com/klimPaskov/Agentic-HOI4-Modding/blob/main/docs/catalog.md).
- **An offline HOI4 wiki** (`hoi4_wiki/`) the agent can read and search.
- **HOI4 tools** that build, preview and check the mod (below).

## Tools

- **[HOI4 Agent Tools](https://github.com/klimPaskov/hoi4-agent-tools)** builds focus trees, events, decisions and maps, previews them, finds modding rules and fixes script.
- **[hoi4-imagegen](https://github.com/klimPaskov/hoi4-imagegen-mcp)** makes focus icons, event pictures, portraits, flags and the rest at the game's sizes. Sign in with ChatGPT or use an API key.
- **Live testing** (optional) drives the running game through Clausewitz MCP or HOI4 Live Tools. See the [live-testing setup](https://github.com/klimPaskov/Agentic-HOI4-Modding/blob/main/.claude/skills/hoi4-live-playtest/references/setup.md).
- **3D models** (optional) through Meshy and Blender.

## Repository layout

| Path | Contents |
| --- | --- |
| `.claude/` | The canonical skills, agents and settings (Claude Code) |
| `.codex/`, `AGENTS_template.md` | Codex |
| `.tools/clients/` | The files of every other client, which HOI4 Mod Setup installs at their real place |
| `.tools/` | Synchronizers, repository checks, the MCP bootstrap and the 3D pipeline |
| `hoi4_wiki/` | The offline HOI4 wiki |
| `docs/` | Guides and references |

Skills, agents and instructions are written once, for Claude Code. `python .tools/sync/generators.py` regenerates every other client's copy ([details](https://github.com/klimPaskov/Agentic-HOI4-Modding/blob/main/.tools/sync/README.md)).

## License

[Apache License 2.0](https://github.com/klimPaskov/Agentic-HOI4-Modding/blob/main/LICENSE), the same as HOI4 Mod Setup. Third-party material keeps its own terms (see [NOTICE](https://github.com/klimPaskov/Agentic-HOI4-Modding/blob/main/NOTICE) and the [Super Events asset lineage](https://github.com/klimPaskov/Agentic-HOI4-Modding/blob/main/docs/super_events/README.md)). Most `hoi4_wiki/` pages come from the [Hearts of Iron IV Wiki](https://hoi4.paradoxwikis.com/Category:Modding) under CC BY-SA 3.0 (see `hoi4_wiki/LICENSE.txt`), and each page names its source page and revision.
