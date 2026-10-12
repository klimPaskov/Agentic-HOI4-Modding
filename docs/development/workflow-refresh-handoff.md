# Workflow refresh handoff

Prepared on 2026-10-13 on `workflow-refresh-source-audit`. This package work is the first release job; Linux support remains a separate follow-up. The source commit is the parent of the manifest evidence commit, as required by `RELEASING.md`. The manifest's `generated_for_revision` records the exact source snapshot.

## Pins and primary evidence

| Route | Reviewed installation pin | Evidence |
| --- | --- | --- |
| HOI4 Agent Tools | npm `4.0.3` | [npm package metadata](https://registry.npmjs.org/hoi4-agent-tools/4.0.3), [release](https://github.com/klimPaskov/hoi4-agent-tools/releases/tag/v4.0.3), [successful release workflow](https://github.com/klimPaskov/hoi4-agent-tools/actions/runs/38308101602). Clean installation measured 5,387 files and the unchanged 28 advertised routes. |
| HOI4 Live Tools | `v1.1.0` | [latest release asset](https://github.com/klimPaskov/HOI4-Live-Tools/releases/tag/v1.1.0): 1,155,994 bytes, SHA-256 `15d6d86b3d7d6d6795bd2a9598d56d312831ff8b4f9c518a38eec522c8c623e4`; existing bootstrap pin matches. |
| Clausewitz MCP | `97c85437081904d5ad07bae1623ec58d1c0a5b9e` | [latest source commit](https://github.com/smerss/Clausewitz-MCP/commit/97c85437081904d5ad07bae1623ec58d1c0a5b9e). Upstream declares native Linux HOI4 1.19.2; its release API lists no published builds. Existing compatible pin retained. |
| GPTImage | `dfb4948b6877b5b7febf73e1342fcfacd862a1ed`, package `0.1.0` | [latest source commit](https://github.com/Connected-Mate/gptimage/commit/dfb4948b6877b5b7febf73e1342fcfacd862a1ed), [source comparison](https://github.com/Connected-Mate/gptimage/compare/49273481195c9795a4b6dc47b28549139c977025...dfb4948b6877b5b7febf73e1342fcfacd862a1ed). Vendored runtime changes add reference discovery; local Windows login and dependency-lock fixes remain. |
| Meshy MCP | npm `@meshy-ai/meshy-mcp-server@0.6.2`, upstream `40dad8600850121f889d394f02833f700cb11b79` | [npm metadata](https://registry.npmjs.org/@meshy-ai%2fmeshy-mcp-server/0.6.2), [release](https://github.com/meshy-dev/meshy-mcp-server/releases/tag/v0.6.2). Clean `npm ci` measured 3,952 files. Published `tools/list` exposes 24 tools, including all eight required workflow tools. |
| Blender Lab MCP | `dbbf836ad4b1025f14a2b3b504c43903f39e0b04` | [verified default-head source](https://projects.blender.org/lab/blender_mcp/commit/dbbf836ad4b1025f14a2b3b504c43903f39e0b04), fetched in a clean shallow checkout. Its `mcp/pyproject.toml` exposes `blender-mcp`; its addon requires Blender 5.1 or newer. Installation now fetches this exact commit and verifies origin and detached HEAD. |
| io_pdx_mesh | `0.91` | [latest upstream release](https://github.com/ross-g/io_pdx_mesh/releases/tag/0.91), asset size 235,195 bytes. Existing source checksum and derived Blender 5.2 compatibility archive remain unchanged. |

Agent Tools npm integrity is `sha512-pgiQYcQiWsba78IOK1DzOb7feEl0ktpiZg3LdyxSMcklA7HV+Zofo3hdR5BOp9YWlWHubrTkl6AMtBgDhqnUmQ==`. Complete package-tree SHA-256 is `b93b47b341e6bc33a0822d631e187af7e3c29eec48196ccd10c89f957729dc35`; `dist/bin/stdio.js` is 4,205 bytes with SHA-256 `e503ef634bcd473b5a7225f6752ff7d99c9897cb2126dac3eb2c4cc55859f24e`.

Meshy npm integrity is `sha512-xEgw7YE5vmK1mT8kBwO6ytmZf+zdaxPd3jdIvO/4o+YFKSSmv9VDnFob3PE2HojC20g57uslQt7m1w4iaWGFZA==`. Runtime package and lock SHA-256 values are `1741490e35df4fd92eb7ffe6c31aa753f1c85063cd08948543928331752f79c7` and `5b28ae2903d9b67b9324e3799b6fcf776739dcaa2beb375bcf595df10629dd58`; complete runtime-tree SHA-256 is `3ad84a9d8f6a1c4ccd97fe8cc15d710d9102911960664ece373d79f0b32430db`. SDK 1.29.0 remains lockfile-resolved. Coordinate these values with the app-owned trusted launcher before installing this package's 3D workflow.

## Generic workflow changes

The source library retains its 31 `hoi4-*` skills plus the shared `xlsx` skill and 23 canonical agents. Model tiers remain Opus for the improvement planner, Sonnet for the five established specialist roles, and Haiku for the other roles. `sync_agents.py --verify` now checks the explicit role/effort policies and reads generated definitions back; regression checks reject valid-but-wrong tiers and efforts. Existing single-read splitting and the 20,000-token ceiling remain in force. Optional skill mirrors are materialized by setup from the complete selected canonical library, including shared skills.

Generic comparison of the existing mod's guidance informed stricter tier verification and reference usage. No mod files were changed or mod-specific mechanics, identifiers, assets or records imported. The integration guide now covers diagnostic positions, nested blocks, definition-only reads, source/revision continuation, skipped reference coverage and known-mistake findings. Ordinary implementation uses error logs only when supplied or requested.

GPTImage's selected provider table and generated runtime catalog advertise `list_references` and avoid promising an underlying image model that its configured text route cannot establish. The bootstrap resolves Node and npm's JavaScript entry directly, preserving argument boundaries for Windows paths containing spaces or `&`. It retains the lockfile, source-tree checks, sanitized child environment and disabled install scripts. Other image routes use package-owned adapters or external hosted/native/manual services; reference MCP examples are not installed npm packages. The provider research document's broader service facts remain dated 2026-10-12.

Meshy 0.6.2 still accepts explicit `meshy-7`, although upstream now marks it deprecated in favor of `meshy-7.1`. The server upgrade preserves the approved generation-model policy. The schema lock records actual published declarations and distinguishes them from policy restrictions. No balance, generation, paid operation or authenticated provider probe was run. Existing app-owned launcher and production capability gates remain required.

## Verification

- Python 3.13 source contract suite: 126 tests pass; agent synchronization contract passes for 23 agents and four projected runtimes.
- 3D pipeline unit suite: 262 tests pass; compilation and source environment verification pass.
- Asset tool suite: 25 tests pass; spreadsheet suite: five tests pass.
- Provider/GPTImage tests exercise reference discovery, MIME decoding, versioned output preservation, Windows browser handling, direct npm argument boundaries and missing executable behavior.
- Agent Tools 4.0.3 and Meshy 0.6.2 initialize and return their expected tool lists with credentials excluded; no game launched.
- Guidance size: 57 files below the ceiling. Wiki snapshot: 54 pages and all 134 referenced media files pass. Release inventory and local links pass. Runtime projections and `git diff --check` pass.
- An initial source run found stale provider data in the pre-refresh manifest; refreshed canonical provider records resolved the equality failure before the final passing run.

Blender's installed-addon bridge and native export integration were not exercised. Published source/tool declarations and unit tests do not establish authenticated Meshy production behavior or live game results. The parent release workflow owns the real disposable-mod installer test, remote publication, archive and tag.

## Linux follow-up boundaries

The current Agent Tools bootstrap discovers Windows Node/npm and its `.cmd` launcher; core manifest platform lists and expected executable evidence omit Linux. Image credential guidance and vault implementation describe Windows Credential Manager and macOS Keychain. The 3D trusted launcher, Windows wrapper scripts and dependency paths also require a separately reviewed Linux route. Live Tools remains Windows-only; Clausewitz supports native Linux, but setup currently presents external WSL/SSH paths and provider platform lists omit a direct Linux host route. Address these as the next package/app job after the first release passes its scratch installation. No Linux source implementation is included here.
