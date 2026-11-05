# Manual setup

[HOI4 Mod Setup](https://github.com/klimPaskov/HOI4-Mod-Setup/releases/latest) does all of this for you, and can update, repair or remove it later. Use these steps only when you set up a mod without the app. Start from a clone of this repository or the [release ZIP](https://github.com/klimPaskov/Agentic-HOI4-Modding/releases/latest/download/Agentic-HOI4-Modding.zip).

## Claude Code

1. Put your mod in a Git repository and open that repository as the agent's workspace.
2. Copy [CLAUDE_template.md](../CLAUDE_template.md) to your mod as `CLAUDE.md` and replace its placeholders (`[MOD_NAME]`, `[MOD_PREFIX]`, `[HOI4_GAME_DIR]`, `[STEAM_WORKSHOP_DIR]`). Delete the blocks for optional workflows you do not install.
3. Copy `.claude/skills/`, `.claude/agents/`, `.claude/settings.json`, `.mcp.json` and `.tools/sync/` into the mod. Make the installed game files and the included `hoi4_wiki/` folder readable to the agent.
4. Copy `.tools/mcp/`, [docs/runtimes.md](runtimes.md) and [docs/systems/hoi4_agent_tools_mcp_integration.md](systems/hoi4_agent_tools_mcp_integration.md) into the mod. Install Python 3.13 and native x64 Node.js 22.19 or later within major 22, or Node.js 24 LTS, with npm on PATH. On Windows, `py -3.13` can replace `python` in these commands.
5. Install HOI4 Agent Tools with `python -I .tools/mcp/bootstrap_hoi4_agent_tools.py`, then approve the project server in your coding client and check that it connects. The bootstrap uses its own verified npm toolchain and leaves your npm installation alone.

On native Linux, follow the [Linux setup guide](linux.md) for the Node.js and Python prerequisites, the current-user install prefix and every client's MCP registration.

## Other coding clients

Claude Code's files are the canonical ones. Every other client reads instructions, skills and agents generated from them.

For **Codex**, copy `.codex/` into the mod.

For any other client, copy its files from [`.tools/clients/`](../.tools/clients) to the same paths in the mod. For example `.tools/clients/.cursor/` becomes `.cursor/`, and `.tools/clients/opencode.json` becomes `opencode.json`.

| Client | Files in `.tools/clients/` | Agents key | Skills target |
| --- | --- | --- | --- |
| Codex | none (`.codex/` at the root) | `codex` | `agents` |
| Cursor | `.cursor/` | `cursor` | none |
| GitHub Copilot (VS Code) | `.github/instructions/`, `.vscode/mcp.json` | none | none |
| Qoder | `.qoder/` | `qoder` | `qoder` |
| OpenCode | `.opencode/`, `opencode.json` | `opencode` | none |
| Gemini CLI | `.gemini/`, and `GEMINI_template.md` as `GEMINI.md` | `gemini` | `agents` |
| Antigravity | `.agents/` | `antigravity` | `agents` |
| Grok Build | `.grok/` | none | `grok` |
| Kilo Code | `.kilo/` | `kilo` | `agents` |
| Kiro | `.kiro/` | `kiro` | `kiro` |
| Qwen Code | `.qwen/` | `qwen` | `qwen` |
| Devin Desktop | `.devin/` | `devin` | `agents` |
| Augment (Auggie CLI) | `.augment/` | `augment` | none |
| Cline | `.clinerules/` | none | none |
| Continue | `.continue/` | none | none |
| Aider | `.aider.conf.yml` | none | none |

Then generate the client's files from the Claude sources, using the keys from the table:

```powershell
python .tools/sync/sync_instructions.py                # AGENTS.md
python .tools/sync/sync_agents.py --runtime cursor     # the client's agents
python .tools/sync/sync_skills.py --target agents      # the client's skill copy
```

Clients with no skills target read `.claude/skills/` directly. Cline, Devin Desktop, Augment and Continue keep MCP servers in their own settings, and Aider has no MCP support. The [runtime reference](runtimes.md) lists what each client reads.

## Optional workflows

- **Live testing:** choose a provider and follow the [live-testing setup guide](../.claude/skills/hoi4-live-playtest/references/setup.md). Clausewitz MCP needs a manual Linux game and server setup. HOI4 Live Tools uses the Windows bootstrap.
- **Portraits, 3D and Super Events:** copy the workflow's references, tools and runtime assets together. The [manifest](../hoi4-mod-setup.manifest.json) is the file inventory.
- **ChatGPT project sources:** copy `.tools/package_chatgpt_project_sources.py` (and its Windows `.bat` launcher) and run it yourself. See the [packaging tool guide](../.tools/README.md#chatgpt-source-packaging).

The templates are starting points. Keep only the workflows your mod uses and add project rules as the mod develops.

## Updating

Back up and commit your mod first. HOI4 Mod Setup's update and repair flow shows changes to managed files, keeps your local additions and updates the MCP registrations for the clients you choose. By hand, copy the new files over and run `python .tools/sync/generators.py`.
