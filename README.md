# Agentic HOI4 Modding

[![Discord](https://img.shields.io/badge/Discord-Join%20Community-7289da?logo=discord&logoColor=white)](https://discord.gg/rAXesGcT2t)

A reusable starting kit for building Hearts of Iron IV mods with coding agents. It includes project instructions, an offline Paradox wiki snapshot, reusable skills, specialist agent profiles, and optional workflows such as portraits, 3D models, and Super Events.

[Download the complete package](https://github.com/klimPaskov/Agentic-HOI4-Modding/releases/latest/download/Agentic-HOI4-Modding.zip) · [Video tutorials](https://www.youtube.com/playlist?list=PLh6JmuEabQioc4V8IYGEsMtqiw-xemeX3)

## Get started

Use [HOI4 Mod Setup](https://github.com/klimPaskov/HOI4-Mod-Setup/releases/latest) to create a mod or prepare an existing one. The app selects and adapts the files for your mod, previews changes, and can update or repair the installation later.

For a manual setup:

1. Put your mod in a Git repository and open that repository as the agent's workspace.
2. Copy [AGENTS_template.md](AGENTS_template.md) to your mod as `AGENTS.md`, then replace its placeholders with your mod's real paths, names, and rules. For Claude Code, use the standalone [CLAUDE_template.md](CLAUDE_template.md) as `CLAUDE.md`.
3. Make your installed Hearts of Iron IV files and the included `paradox_wiki/` snapshot readable to the agent.
4. Copy the skills you need from `.agents/skills/`. Add specialist profiles from `.codex/agents/` when a task benefits from a bounded helper.
5. Install and verify the optional tools you select. HOI4 Mod Setup handles their configuration and the manifest-pinned versions.

The templates are starting points. Keep only the workflows your mod uses and add project rules as the mod develops. [Runtime setup details](docs/runtimes.md) cover Codex, Claude Code, Cursor, Qoder, OpenCode, and DeepSeek Harness.

## Codex configuration

The package's [`.codex/config.toml`](.codex/config.toml) registers the specialist agents and the HOI4 Agent Tools MCP server. In an installed mod, set the server's `cwd` to that mod's root if your setup does not supply it automatically:

```toml
[mcp_servers.hoi4_agent_tools]
command = "hoi4-agent-tools.cmd"
cwd = "C:\\path\\to\\your_mod"
startup_timeout_sec = 120
tool_timeout_sec = 180
```

Restart Codex after changing MCP registration, then verify that the server and the routes needed for your task are available. The optional 3D routes are configured when a model task actually needs them. Keep API keys in your user environment, never in `config.toml`. The setup app manages the Windows tool installation and version checks.

Canonical subagent instructions live in `.codex/agents/*.toml`. After editing one, regenerate the checked-in Claude Code, Cursor, Qoder, and OpenCode copies with the scripts in [`.tools/sync/`](.tools/sync/README.md).

## What's inside

| Folder | Purpose |
| --- | --- |
| `.agents/skills/` | Reusable HOI4 workflows and their references |
| `.codex/agents/` | Specialist agent definitions |
| `paradox_wiki/` | Offline wiki reference |
| `.tools/` | Agent synchronization, wiki, MCP, and optional 3D tooling |
| `docs/` | Runtime and system reference |
| `hoi4-mod-setup.manifest.json` | File selection and verification for HOI4 Mod Setup |

The project instructions and each selected skill define the work and evidence required for a feature. A generated asset or passing tool result still needs the relevant game files wired and reviewed.

## License

You may adapt this package for your own HOI4 modding workflow.
