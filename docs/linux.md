# Native Linux setup

HOI4 Mod Setup supports native Linux alongside Windows and macOS. This package records native Linux x86_64/glibc HOI4 Agent Tools evidence measured on Ubuntu 24.04. Shared instructions, skills and specialist definitions have the same ownership and model tiers on every platform. The app writes native MCP registrations for Claude Code, Codex, Cursor, Qoder and OpenCode when selected; a coding client must itself be available on the host.

## Prerequisites and files

Install Git, Python 3.10 or newer, and native x64 [Node.js](https://nodejs.org/en/download) 22.19+ within major 22, or Node.js 24 LTS, with npm. The Linux bootstrap does not install system dependencies or invoke sudo. Imported Windows Node/npm paths in WSL do not satisfy this prerequisite. `node --version`, `npm --version` and `python3 --version` should resolve native executables. Setup uses trusted system executables; its Linux launch environment uses `/usr/bin:/bin`.

Use the setup app for a new or existing mod, or copy the canonical files following the README's manual steps. Set the game and Workshop placeholders to the installed native Steam library. Common game locations include `~/.local/share/Steam/steamapps/common/Hearts of Iron IV` and `~/.steam/steam/steamapps/common/Hearts of Iron IV`; select the actual library instead of assuming either path. The usual mod folder is `~/.local/share/Paradox Interactive/Hearts of Iron IV/mod`.

From the mod root, install the recorded public package:

```bash
python3 -I .tools/mcp/bootstrap_hoi4_agent_tools.py
```

The bootstrap checks the published npm SHA-512, package name/version, complete native tree and entry bytes. It uses `$XDG_DATA_HOME/hoi4-mod-setup/npm`, or `~/.local/share/hoi4-mod-setup/npm` when unset. A set XDG_DATA_HOME must be an absolute path. Native modules live under `<prefix>/lib/node_modules/hoi4-agent-tools`; the locator is `<prefix>/bin/hoi4-agent-tools`. The two npm-generated internal links and the root locator must have their exact reviewed targets. Missing, substituted or escaping links fail verification.

Package installation uses a private SHA-512-pinned npm 10.9.9 CLI with isolated
configuration and cache, regardless of the system npm version. npm 11 produces
a different optional-dependency tree on Linux, so ambient npm is never used to
realize this reviewed package. The private toolchain does not replace the
system npm executable or configuration.

## Manual client registration

The source archive's raw MCP examples use `hoi4-agent-tools.cmd`. The app adapts them automatically on Linux. For manual setup, use the verified absolute native Node path as `command` and `<prefix>/lib/node_modules/hoi4-agent-tools/dist/bin/stdio.js` as its sole argument. Replace `<prefix>` with the actual absolute current-user prefix and retain each client's mod working-directory setting. Start clients from the mod root when that client has no project working-directory field. No shell wrapper or global PATH amendment is needed.

| Client | File | Native registration shape |
| --- | --- | --- |
| Claude Code | `.mcp.json` | `mcpServers.hoi4_agent_tools` has `type: "stdio"`, `command: "/usr/bin/node"` and `args: ["<absolute entry>"]`. |
| Codex | `.codex/config.toml` | `[mcp_servers.hoi4_agent_tools]` has `command = "/usr/bin/node"`, `args = ["<absolute entry>"]` and the mod's `cwd`. |
| Cursor | `.cursor/mcp.json` | `mcpServers.hoi4_agent_tools` has `command: "/usr/bin/node"` and `args: ["<absolute entry>"]`. |
| Qoder | `.qoder/mcp.json` | `mcpServers.hoi4_agent_tools` has `command: "/usr/bin/node"` and `args: ["<absolute entry>"]`. |
| OpenCode | `opencode.json` | `mcp.hoi4_agent_tools` has `type: "local"`, `command: ["/usr/bin/node", "<absolute entry>"]` and `enabled: true`. |

Here `/usr/bin/node` is the tested native system location; use the verified absolute executable on the actual host. Preserve unrelated servers and local client settings. DSH has no project MCP registry; adapt the active profile's command and argument list using [its runtime contract](runtimes.md#mcp-registration).

Generate the shared projections after changing canonical guidance:

```bash
python3 .tools/sync/sync_instructions.py
python3 .tools/sync/sync_agents.py
python3 .tools/sync/sync_skills.py --target agents
python3 .tools/sync/sync_agents.py --verify
```

Use `--target qoder` for Qoder's skill copy and `--check` to detect projection drift. Approve each selected client's project server and inspect its advertised tool list. An offline tool handshake does not establish running-game behavior.

## Images and credentials

GPTImage installs its locked dependencies through native Node and npm's resolved JavaScript entry, including the usual `/usr/bin/npm` symlink layout. Its source-tree and lock hashes are independent of line endings; a fresh Linux CLI installation and three-tool handshake were verified without signing in. Actual image generation still needs the selected provider's normal sign-in or API authorization.

API-backed image routes use the same package-owned Python adapter. Saved keys stay in the Linux desktop Secret Service, matching the app's keyring service and opaque credential references. Install `libsecret-tools` and use a desktop session with a working D-Bus session bus and unlocked Secret Service. The adapter invokes `/usr/bin/secret-tool` with exact entry attributes and returns unavailable when the helper or vault cannot answer. It does not save a fallback plaintext key or put keys in project configuration. Hosted OAuth, local and manual routes retain their own prerequisites.

## Live testing and 3D

Clausewitz MCP connects directly on a native Linux host. It supports native HOI4 **1.19.2 only**, at source commit `97c85437081904d5ad07bae1623ec58d1c0a5b9e`. Follow [upstream setup](https://github.com/smerss/Clausewitz-MCP/tree/97c85437081904d5ad07bae1623ec58d1c0a5b9e) to prepare the game, Python environment and process-read permissions. Setup's native convention is `~/tools/Clausewitz-MCP/.venv/bin/python` launching `~/tools/Clausewitz-MCP/clausewitz.py serve`; readiness requires those files and the compatible game/server environment. Confirm that readiness separately before registering `clausewitz_linux`. Provider selection and an installer test do not verify game compatibility or launch the game.

Windows still connects through WSL and macOS through SSH to Linux. HOI4 Live Tools and the Meshy/Blender 3D bootstrap remain Windows-verified workflows and are not installed as native Linux routes. Manual testing registers no live server. See [the live setup guide](../.claude/skills/hoi4-live-playtest/references/setup.md) for bounded tests and capability gates.

## Manifest compatibility

The single canonical manifest uses schema 5 because Linux platform declarations and exact native integrity evidence are incompatible with the closed schema 4 contract. Older setup apps must upgrade before consuming this manifest. Each health pin records the platform's complete tree, file count, entry identity and explicit link map; the shared npm package version and SHA-512 remain unchanged.
