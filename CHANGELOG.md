# Changelog

## Unreleased

- Document that Meshy API task creation needs a paid Meshy plan: on the free plan every create returns HTTP 402 and charges nothing.
- Review the offline wiki snapshot and the skills against HOI4 1.19.4.1 (Operation Postern v1.19.4.1.99a5). The game's documentation changed in two places: the AI strategy token `stockpile_fuel` is new (now in AI modding and the `hoi4-ai-strategies` token catalog), and the console command `debug_types` is gone (Console commands). Steam's depot manifests show 1,511 changed game files, so every tagged statement whose files changed was re-measured on 1.19.4.1 and retagged, and statements on unchanged files keep their 1.19.3 tags. `defines_additions.md` gains a 1.19.4.1 section: 19 new defines (volunteer recall, player auto-import, focus tree mini-map, casualty trickleback) and one changed value.
- Record the installed Steam depot manifest ids in `game_docs_index.json`. After a game update, `wiki_status.py` lists the game files that changed (read from the depot cache by the new `steam_depots.py`) and flags pages whose `sources` cover them, not only pages that cite documentation.
- Check out the Meshy runtime `package.json` and `package-lock.json` with LF endings on every platform. On a Windows checkout with `core.autocrlf=true` their hashes no longer matched the bootstrap pins, so the runtime lock test failed and the 3D bootstrap would refuse the runtime.
- Report a Meshy refusal (an MCP error result, such as HTTP 402 when the account's plan cannot create API tasks) with Meshy's own message instead of "Meshy response did not contain a task id".
- Move the Meshy MCP pin from 0.6.2 to 0.6.7 (runtime lock, bootstrap identities and the tool schema lock re-captured from a live `tools/list`). The Text-to-Motion tools the contract named did not exist; it now names `meshy_text_to_motion`, `meshy_list_animations` and the generic task tools, and the deprecated `meshy_rig` `texture_image_url` is never sent.
- Make the Meshy generation model a per-profile `generation` block in `asset_profiles.json`. The shipped values keep today's request (`meshy-7`, standard, `should_remesh` false). Retired models (`meshy-t1`, `meshy-5`, `meshy-4`, `lowpoly`), unpinned aliases, Smart Topology face caps and a standard-model target that Meshy would ignore are refused before any paid call.
- Read every credit estimate from `config/meshy_pricing.json` (docs.meshy.ai pricing page, retrieved 2026-10-31) instead of hard-coded 30/5/3 constants and a 44-credit fallback.
- Require a `credit_budget` for paid jobs. A paid create that would exceed the remaining budget, the contract's attempt limit for its operation, or the live balance stops before submission with the shortfall named; renaming a stage no longer bypasses the no-retry guard.
- Reuse before paying: a succeeded stage in the job, then a succeeded result in another job with the same request fingerprint; an unreconciled submission for the same request blocks the call.
- Record every paid attempt, stop, reuse and local rig route in `provider/credits/ledger.jsonl`, and add `run_pilot.py --credits-report` (no API key, no provider call).
- Run the 3D pipeline suite in `.tools/check.py full`.
- Make the 3D model pipeline's silent checks fail closed. The profile texture-size cap reads the PNG header itself instead of running `ffprobe`, and an unreadable texture or a profile without a cap blocks the conversion. `candidate_gate` also blocks on non-manifold edges, boundary edges, loose components, a triangle count outside the profile's preferred range, too many material slots, and residual zero-weight deforming vertices; a measurement missing from the report blocks too. Each profile in `asset_profiles.json` gets a `validation` block of limits and an `exceptions` list; a profile waives one check only by listing it with a reason, and the gate record lists every exception applied.
- Capture what io_pdx_mesh reports during mesh and animation export instead of returning an empty `warnings` list. When the exporter's logger cannot be reached, `warnings` is `null` with an `exporter_report` that says why, and the Blender client refuses that export unless the profile records an `exporter_report` exception. The worker's geometry metrics gain `loose_component_count`.
- Start the reference image's `visual_preflight` flags unreviewed (`null`) with `reference_preflight.json` at `pending_review`. `init_pilot_jobs.py --record-visual-review SLUG --reviewer NAME --review-file answers.json` records the parent's answers, and `run_pilot.py` refuses to proceed from a job still in preflight until the review passes, before any paid call.
- Pin Blender: `dependencies.lock.json` lists the supported minors (5.1 and 5.2), `find_blender` picks the highest supported minor and refuses others, and every supported minor installs the deterministic io_pdx_mesh compatibility archive with its patched files hash-checked. Blender 5.1.2 bundles Python 3.13.9 without the `imp` module that the upstream 0.91 archive imports. A bootstrap on a machine with an existing Blender 5.1 `io_pdx_mesh` whose patched files do not match the lock replaces that folder.
- Rewrite the 3D model pipeline instructions to match the code: each rule now lives once (route selection, the key snippet and the credit rules are defined in the production guide, with `SKILL.md`, the agent and the README linking to it), the one-budget-per-job credit rule replaces the standing pre-authorization, the generation model is the profile's, and the guide adds the visual review step, `--credits-report`, the fail-closed checks, the Blender 5.1/5.2 pin, a clean `GFX-3D-*` static audit in the handoff and a parent-owned in-game check recipe (marked unconfirmed).
- Check 3D model registration in the `asset-wiring` audit (`GFX-3D-*`): `.mesh` and `.anim` files that are missing, `pdxmesh` animation types no `animation` block defines, entities whose `pdxmesh` is defined nowhere, sub-unit `sprite` tokens without a `<sprite>_entity`, `meshsettings` names that are not objects of the exported PDX `.mesh` (read by a small read-only PDX binary reader), and missing model textures. Each finding carries `file:line`; `--calibrate-vanilla` reports how often each rule fires on the installed game.
- The diffuse texture of a `pdxmesh` under `gfx/` or `interface/` is now reported once, as `GFX-3D-TEXTURE-MISSING`, instead of as `GFX-MISSING-FILE` without a line.
- Route the Codex 3D model pipeline, event UI worker, generated feature art and icon artist agents to GPT-6.1 Terra (`gpt-6.1-terra`) through a Codex-only `codex.agent_models` map in `.tools/sync/agent_profiles.json`; Terra needs Codex CLI 0.159.0 or later. `sync_agents.py --verify` fails when the map names an agent that does not exist.

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
