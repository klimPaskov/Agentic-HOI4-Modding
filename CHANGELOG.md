# Changelog

## Unreleased

- Publish setup manifest format 6. Each coding client declares whether HOI4 Mod Setup manages a project MCP file, the client keeps MCP servers in its own settings, or it has no MCP support, so an app that cannot register a client never offers it.
- Add packages for GitHub Copilot (VS Code), Gemini CLI, Antigravity, Grok Build, Kilo Code, Kiro, and Qwen Code with project MCP registration, and for Cline, Devin Desktop, Augment, Continue, and Aider with project guidance only.
- Share one `.agents/skills/` copy between Codex, Gemini CLI, Antigravity, Kilo Code, and Devin Desktop; generate native subagents for seven more clients from the canonical Claude agents.
- Move the OpenCode MCP registration into `opencode.json`, the only file OpenCode reads, and retire `.opencode/mcp.json`.
- Merge this format only together with the HOI4 Mod Setup release that reads it; earlier releases report that the setup package needs a newer app.

## 2026-10-13

- Add native Linux Agent Tools installation with exact platform trees and reviewed link targets in schema 5, keeping one canonical manifest route.
- Support native Linux client registration, direct Clausewitz connections and Secret Service image credentials; document Windows-only 3D and Live Tools boundaries.

- Pin HOI4 Agent Tools 4.0.3 and Meshy MCP 0.6.2 with verified public package integrity and complete runtime identities.
- Refresh GPTImage to the latest reviewed source, add reference-image discovery, and fix direct npm startup on Windows.
- Give GPTImage separate empty npm user and global configuration files; a fresh real installation now reaches `ready` instead of npm's double-loading configuration error.
- Freeze Blender MCP to its reviewed source commit; retain the verified Live Tools 1.1.0, Clausewitz native Linux HOI4 1.19.2, and io_pdx_mesh 0.91 pins.
- Verify specialist model tiers and efforts, and expand the reference-tools workflow for nested definitions, diagnostics and continuation reads.
- Keep every guidance file below its single-read ceiling and preserve generated client projections.

## 2026-10-11

- Keep the package's canonical guidance together and create matching files for the coding clients selected in HOI4 Mod Setup.
- Pin the 28-tool HOI4 Agent Tools 4.0.0 package and the optional Windows HOI4 Live Tools 1.1.0 release with complete integrity evidence.
- Keep portraits, 3D models, Super Events, and live game testing optional, with complete manifest-declared workflow packages.
- Publish installation guides, screenshots, and downloadable setup and MCP demonstration videos.
- License original package code and guidance under Apache-2.0; preserve separate third-party terms and provenance.

## 2026-10-12

- Let each mod choose an image-generation service; HOI4 Mod Setup adds the right tool names and instructions for that service.
- Offer subscription, API, local, Codex, manual-art, and no-provider choices; keep API keys in the operating-system credential store.
- Make one image per call and check saved transparency, reference handling, size limits, and supported edit or background-removal steps.
