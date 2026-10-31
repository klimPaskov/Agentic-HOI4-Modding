# Changelog

## 2026-10-31

- List every generator and generated-file check in `.tools/sync/generators.json` and run them through one runner, `.tools/sync/generators.py`, which `check.py`, `check.py setup`, CI and the release check share. A change to one skill regenerates only that skill's copies, and unrelated edits start nothing.
- Regenerate projections automatically in Claude Code: a `PostToolUse` hook in `.claude/settings.json` reruns the generators a canonical edit affects, names the outputs to commit with it, and refuses hand edits of generated files. Deny rules stop the edit tools from writing generated files. `.tools/py.sh` starts the first working Python for the hooks.
- Make sync failures visible: a missing or crashing generator, a broken registry or a folder with nothing to check now exits 2 instead of passing, `check.py setup` exits non-zero when a generator fails, and an installed mod with `.codex/` or `.qoder/` fails the check when its skill copy is missing.
- Add `--root` to every sync tool, `--skill` to `sync_skills.py`, and the `UNUSED` check for instruction replacements whose phrase no longer occurs. `check.py setup --git-hook` adds an optional pre-commit check of staged changes.
- Test every synchronization requirement on fixture mods (`.tools/tests/test_sync.py`) on Linux, macOS and Windows in CI, and stop the contract test from hard-coding the number of agents.
- Ask the genuine questions of a new feature once, at the start: the template's Upfront consultation rule and `hoi4-feature-planning/references/consultation-questions.md` sort open points, give each question a suggested answer, record answers in `docs/specs/<feature_slug>/decisions.md`, and list what is never asked. Skills with late questions point to it.
- Add `hoi4-investigate`, a static root-cause protocol (root cause before any edit, premise tripwires, an evidence ladder, parser cascades, and a reading order for logs the user supplies), and point `hoi4-debug-playtest` to it.
- Import the engine traps confirmed on HOI4 1.19.3 into the system skills, each with its evidence tag, and add references for military industrial organisations and special projects, intelligence operations, and script variables and math. Correct six skill rules that vanilla contradicts (`state_target`, supply hub construction, weather position sizes, the force concentration define, the equipment type enum, the special project documentation).
- Add a feasibility check to `hoi4-feature-planning`, evidence tags for engine facts in skills, and `LESSONS.md`, which ties each incident-driven rule to its regression fixture.
- Resolve the contradiction between the template and the skills on unavailable MCP routes: the evidence is reported as missing and marked unresolved, never passed. Shorten three subagent routing bullets whose full rules live in `hoi4-subagents`; `docs/development/guidance-audit-2026-10-31.md` lists every moved or changed sentence.
- Review the offline Paradox wiki snapshot against HOI4 1.19.3: kit blocks hold every local correction and addition and survive a refresh, each page records the game build and sources it was checked against, and nine kit pages cover systems the wiki lacks (special projects, raids, peace conferences, collections, script constants, intelligence operations, map modes, game rules, occupation and resistance).
- Add `.tools/wiki/wiki_status.py`, which compares the installed game's documentation with the recorded index and lists the pages to re-check after a game update.
- Name the snapshot's files after the page title in lowercase snake_case (`scripted_gui_modding.md`) instead of `<Page Title> - Hearts of Iron 4 Wiki.md`. HOI4 Agent Tools reads the underscore as a space, so its page lookups keep working. The sync and the verify check enforce the scheme, and a mod with its own copy replaces the whole `paradox_wiki/` folder.
- Move the Defines page's new-define tables into the kit page `defines_additions.md`, so the wiki page stays an unchanged snapshot.
- Mark the claims only a game run can settle (`collection_size` inclusivity, the peace `ai_desire` scale, special project reward thresholds, the raid `target_type` scope, MIO task capacity) with a "Needs a game run" note on their pages.
- Record the snapshot's CC BY-SA 3.0 license in `paradox_wiki/LICENSE.txt`, the manifest and `NOTICE`.

## 2026-10-18

- Bound the Blender adapter to the `mcp` 1.x SDK; a fresh bootstrap resolved `mcp` 2.3.0, which removed `FastMCP`, and the adapter crashed at startup.
- Resolve the DDS converter from the `hoi4-feature-assets` skill in whichever skill folder is installed; the 3D pilot and adapter no longer call the removed `hoi4-event-assets` path or require the Codex mirror.
- Keep the pinned `sources` and io_pdx_mesh `compatibility` evidence when the bootstrap rewrites `dependencies.lock.json`, so a second bootstrap succeeds.
- Start the materialized Blender adapter in `verify_environment.py` and require its MCP `initialize` and `tools/list` to serve exactly the source's tools.
- Fix `python -m hoi4_blender_mcp` exiting with `NameError`, register `hoi4_blender_segment_creature_components` once, and keep adapter subprocesses off the MCP stdin pipe.
- Run every `convert_to_dds.py` child process with an empty stdin and pass `-nostdin` to ffmpeg; under the stdio adapter the ffmpeg fallback waited on the inherited MCP pipe until the 600-second texture timeout.
- Drop the NLA tracks that `Object.copy()` carries onto the working rig, so action-phase patching accepts it; the protected provider source keeps its tracks.
- Fingerprint the NLA tracks of protected provider and read-only reference blocks during promotion instead of refusing them; drivers, and NLA on editable blocks, are still refused.
- Lower the humanoid working triangle target to 21,000 so the body exports as one stream within the 65,535 index-entry budget.
- Ground root channels through the Hips location axis with the strongest world-Z response; in-place sanitization now locks only horizontal root motion and keeps the provider's vertical motion, so Meshy glTF rigs no longer slide sideways.

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
