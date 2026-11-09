# macOS setup

HOI4 Mod Setup supports macOS alongside Windows and native Linux. HOI4 Agent Tools runs on Apple Silicon Macs (arm64); this package records its macOS evidence measured on macOS 26.5. Intel Macs have no reviewed route, because the package bundles its native engine and image libraries for darwin-arm64 only. Shared instructions, skills and specialist definitions are the same on every platform. The app writes MCP registrations for every selected coding client that has a project MCP file; the coding client must itself be installed.

HOI4 Live Tools and the Meshy/Blender 3D bootstrap remain Windows-verified workflows and are not offered on macOS. Image generation (hoi4-imagegen) is offered on every platform.

## Prerequisites and files

Install Git and Python 3.10 or newer (`python3 --version`). You do not need to install Node.js: the bootstrap installs a private copy of the official build.

Use the setup app for a new or existing mod, or copy the canonical files following the README's manual steps. The usual game folder is `~/Library/Application Support/Steam/steamapps/common/Hearts of Iron IV`, and the usual mod folder is `~/Documents/Paradox Interactive/Hearts of Iron IV/mod`.

From the mod root, install the recorded public package:

```bash
python3 -I .tools/mcp/bootstrap_hoi4_agent_tools.py
```

The bootstrap works in `~/Library/Application Support/hoi4-mod-setup/npm` and does three things:

1. It downloads the official Node.js 24.22.0 `darwin-arm64` archive from `https://nodejs.org/dist`, checks its SHA-256, and keeps only the `node` executable at `<prefix>/node/bin/node`. It checks that executable's SHA-256 and its Developer ID signature: Apple-anchored, Node.js Foundation, Team ID `HX7739G8FX`. Nothing outside the prefix changes. Your own Node.js, Homebrew and PATH are not used or modified.
2. It installs the exact `hoi4-agent-tools` package with a private, SHA-512-pinned npm 10.9.9 that has its own configuration and cache.
3. It verifies the published npm SHA-512, the package name and version, the complete native tree and the entry bytes. Modules live under `<prefix>/lib/node_modules/hoi4-agent-tools`. The locator `<prefix>/bin/hoi4-agent-tools` and the three npm-generated internal links must have their exact reviewed targets.

Later runs reuse a matching runtime and package, so they finish in about a second. A changed or missing file is downloaded and checked again.

## Client registration

The source archive's raw MCP examples use `hoi4-agent-tools.cmd`, and the app adapts them automatically on macOS. Setup checks the private Node.js signature again and writes its absolute path as the `command`. It writes the absolute `<prefix>/lib/node_modules/hoi4-agent-tools/dist/bin/stdio.js` as the only argument.

For manual setup, use the same two absolute paths in the shapes from [the Linux guide](linux.md#manual-client-registration), replacing `/usr/bin/node` with `<prefix>/node/bin/node`. The path contains a space (`Application Support`), so keep it as a single JSON or TOML string and never split it. No shell wrapper or PATH change is needed.

Claude Code asks once before it starts a project server, and Gemini CLI starts project servers only in a trusted folder.
