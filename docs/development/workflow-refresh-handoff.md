# Workflow refresh handoff

Prepared on 2026-10-13 on `workflow-refresh-source-audit`. This package work is the first release job; Linux support remains a separate follow-up. The source commit is the parent of the manifest evidence commit, as required by `RELEASING.md`. The manifest's `generated_for_revision` records the exact source snapshot.

## Pins and primary evidence

| Route | Reviewed installation pin | Evidence |
| --- | --- | --- |
| HOI4 Agent Tools | npm `4.0.3` | [npm package metadata](https://registry.npmjs.org/hoi4-agent-tools/4.0.3), [release](https://github.com/klimPaskov/hoi4-agent-tools/releases/tag/v4.0.3), [successful release workflow](https://github.com/klimPaskov/hoi4-agent-tools/actions/runs/38308101602). Clean installation measured 5,387 files and the unchanged 28 advertised routes. |
| HOI4 Live Tools | `v1.1.0` | [latest release asset](https://github.com/klimPaskov/HOI4-Live-Tools/releases/tag/v1.1.0): 1,155,994 bytes, SHA-256 `15d6d86b3d7d6d6795bd2a9598d56d312831ff8b4f9c518a38eec522c8c623e4`; existing bootstrap pin matches. |
| Clausewitz MCP | `97c85437081904d5ad07bae1623ec58d1c0a5b9e` | [latest source commit](https://github.com/smerss/Clausewitz-MCP/commit/97c85437081904d5ad07bae1623ec58d1c0a5b9e). Upstream declares native Linux HOI4 1.19.2; its release API lists no published builds. Existing compatible pin retained. |
| GPTImage | `dfb4948b6877b5b7febf73e1342fcfacd862a1ed`, package `0.1.0` | [latest source commit](https://github.com/Connected-Mate/gptimage/commit/dfb4948b6877b5b7febf73e1342fcfacd862a1ed), [source comparison](https://github.com/Connected-Mate/gptimage/compare/49273481195c9795a4b6dc47b28549139c977025...dfb4948b6877b5b7febf73e1342fcfacd862a1ed). Vendored runtime changes add reference discovery; local Windows login and dependency-lock fixes remain. |
| Meshy MCP | npm `@meshy-ai/meshy-mcp-server@0.6.7`, upstream `0f4c10a3c37f74a2625a922aeaff03b2f878887f` | [npm metadata](https://registry.npmjs.org/@meshy-ai%2fmeshy-mcp-server/0.6.7). The runtime tree has 3,954 files. The schema lock was captured from a live `tools/list` and lists all eight required workflow tools plus the optional Text-to-Motion tools. (The 2026-10-13 refresh pinned 0.6.2.) |
| Blender Lab MCP | `dbbf836ad4b1025f14a2b3b504c43903f39e0b04` | [verified default-head source](https://projects.blender.org/lab/blender_mcp/commit/dbbf836ad4b1025f14a2b3b504c43903f39e0b04), fetched in a clean shallow checkout. Its `mcp/pyproject.toml` exposes `blender-mcp`; its addon requires Blender 5.1 or newer. Installation now fetches this exact commit and verifies origin and detached HEAD. |
| io_pdx_mesh | `0.91` | [latest upstream release](https://github.com/ross-g/io_pdx_mesh/releases/tag/0.91), asset size 235,195 bytes. Existing source checksum remains unchanged; the derived compatibility archive now serves every supported Blender minor (5.1 and 5.2). |

Agent Tools npm integrity is `sha512-pgiQYcQiWsba78IOK1DzOb7feEl0ktpiZg3LdyxSMcklA7HV+Zofo3hdR5BOp9YWlWHubrTkl6AMtBgDhqnUmQ==`. Complete package-tree SHA-256 is `b93b47b341e6bc33a0822d631e187af7e3c29eec48196ccd10c89f957729dc35`; `dist/bin/stdio.js` is 4,205 bytes with SHA-256 `e503ef634bcd473b5a7225f6752ff7d99c9897cb2126dac3eb2c4cc55859f24e`.

Meshy npm integrity is `sha512-kmOyjdcW+FZuc+TZHK4aUjfOID+LbjmQAM7W9YLtLhApW7b7lo+aZLnLl6xnNfM2KvktODXCF61kgDhjwP7dUg==`. Runtime package and lock SHA-256 values are `a786752193cacd1c01c20db7c1a47d0a4d52fada7eed2ac7b47b7245687aec0b` and `672707686e4a59b644f5bb7e1af58c8987a26f6caadcbf0c5e7e196b7bfa7c18`; complete runtime-tree SHA-256 is `dbd2ebfce197a18875c3d367ad4b5325a345b92ce54c2a33440f5490efe7f6b3`. SDK 1.29.0 remains lockfile-resolved. Coordinate these values with the app-owned trusted launcher before installing this package's 3D workflow.

## Generic workflow changes

The source library retains its 31 `hoi4-*` skills plus the shared `xlsx` skill and 23 canonical agents. Model tiers remain Opus for the improvement planner, Sonnet for the five established specialist roles, and Haiku for the other roles. `sync_agents.py --verify` now checks the explicit role/effort policies and reads generated definitions back; regression checks reject valid-but-wrong tiers and efforts. Existing single-read splitting and the 20,000-token ceiling remain in force. Optional skill mirrors are materialized by setup from the complete selected canonical library, including shared skills.

Generic comparison of the existing mod's guidance informed stricter tier verification and reference usage. No mod files were changed or mod-specific mechanics, identifiers, assets or records imported. The integration guide now covers diagnostic positions, nested blocks, definition-only reads, source/revision continuation, skipped reference coverage and known-mistake findings. Ordinary implementation uses error logs only when supplied or requested.

GPTImage's selected provider table and generated runtime catalog advertise `list_references` and avoid promising an underlying image model that its configured text route cannot establish. The bootstrap resolves Node and npm's JavaScript entry directly, preserving argument boundaries for Windows paths containing spaces or `&`. It retains the lockfile, source-tree checks, sanitized child environment and disabled install scripts. Other image routes use package-owned adapters or external hosted/native/manual services; reference MCP examples are not installed npm packages. The provider research document's broader service facts remain dated 2026-10-12.

Meshy 0.6.7 still accepts explicit `meshy-7`, although upstream marks it deprecated in favor of `meshy-7.1`. The generation model is each profile's `generation.ai_model` in `config/asset_profiles.json`, and the server upgrade does not change it. The schema lock records actual published declarations and distinguishes them from policy restrictions. No balance, generation, paid operation or authenticated provider probe was run. Existing app-owned launcher and production capability gates remain required.

## Verification

- Python 3.13 source contract suite: 126 tests pass; agent synchronization contract passes for 23 agents and four projected runtimes.
- 3D pipeline unit suite: 262 tests pass; compilation and source environment verification pass.
- Asset tool suite: 25 tests pass; spreadsheet suite: five tests pass.
- Provider/GPTImage tests exercise reference discovery, MIME decoding, versioned output preservation, Windows browser handling, direct npm argument boundaries and missing executable behavior.
- Agent Tools 4.0.3 and Meshy (0.6.2 at that refresh, since moved to 0.6.7) initialize and return their expected tool lists with credentials excluded; no game launched.
- Guidance size: 57 files below the ceiling. Wiki snapshot: 54 pages and all 134 referenced media files pass. Release inventory and local links pass. Runtime projections and `git diff --check` pass.
- An initial source run found stale provider data in the pre-refresh manifest; refreshed canonical provider records resolved the equality failure before the final passing run.

Blender's installed-addon bridge and native export integration were not exercised. Published source/tool declarations and unit tests do not establish authenticated Meshy production behavior or live game results. The parent release workflow owns the real disposable-mod installer test, remote publication, archive and tag.

## GPTImage real-installer correction

The disposable app installation exposed a source defect that mocked dependency installation did not catch. Exact Git blobs from `d154db7a65c122e5e7015bc3d0a0371d9a9cac6e` matched the published source-tree and dependency-lock hashes, and Node/npm discovery succeeded. The unmodified CLI still exited 1 before dependency downloads: npm reported `double-loading config` because the bootstrap supplied one temporary file to both `--userconfig` and `--globalconfig`.

Branch `fix/gptimage-npm-config` supplies two distinct empty files inside the same private temporary cache. The regression checks both path identities and empty contents during installation, while preserving cache cleanup and direct Node invocation. A disposable real npm run with only those corrected arguments installed 93 locked packages in six seconds, emitted no stderr, returned `ready` and created the SDK package. Source hashes and the runtime catalog are regenerated with the fix. These checks use no credentials, sign-in, image generation or other provider operations.

## Linux follow-up boundaries

The current Agent Tools bootstrap discovers Windows Node/npm and its `.cmd` launcher; core manifest platform lists and expected executable evidence omit Linux. Image credential guidance and vault implementation describe Windows Credential Manager and macOS Keychain. The 3D trusted launcher, Windows wrapper scripts and dependency paths also require a separately reviewed Linux route. Live Tools remains Windows-only; Clausewitz supports native Linux, but setup currently presents external WSL/SSH paths and provider platform lists omit a direct Linux host route. Address these as the next package/app job after the first release passes its scratch installation. No Linux source implementation is included here.
