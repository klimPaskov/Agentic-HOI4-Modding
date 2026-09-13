# Latest reusable workflow sync

> Historical September 8 snapshot. The [September 13 integrated sync](latest_workflow_sync_2026_09_13.md) supersedes current-status and routing claims here, including the firearm geometry policy. Keep this report as earlier validation evidence, not current instructions.

Date: 2026-09-08

## Result

The general Agentic HOI4 Modding workflow was reconciled against Chaos Redux at commit `4a45b07adb15595ee0bc4ff1d6d017dad25a444c`. The target baseline was `59cc276cd79db5e69b0b39280f09c831d86a2348` plus the pre-existing working-tree changes that were preserved during this sync.

Only reusable, mod-agnostic workflow practices and tools were ported. Chaos Redux state ledgers were explicitly excluded, as were project gameplay, identifiers, generated artifacts, event-specific closure records, asset-result files, and source-specific runtime state.

## Reusable changes adopted

- Added the generic `hoi4-scripted-gui` skill with reference-image mapping, live MCP preview iteration, matched comparison evidence, interaction-state checks, content/action budgets, and optional reviewed GUI rewrite support.
- Updated decisions, missions, events, focus trees, planning, improvement-loop, animation, debugging, MTTH, feature-asset, and subagent guidance with the latest reusable validation and routing practices.
- Restored the reusable repository `xlsx` skill and hardened its LibreOffice recalculation helper with executable discovery, cross-platform subprocess timeouts, JSON failure reporting, and provider-free unit tests. Chaos Redux's event-catalog export contract was excluded.
- Added reusable achievement icon templates and an icon-processing tool, including eligible, grey, and not-eligible output handling.
- Updated the canonical Codex agents and regenerated the Claude, Cursor, OpenCode, and Qoder projections. The event UI worker now owns one event-scoped window and follows the live scripted-GUI review workflow.
- Updated `AGENTS_template.md`, repository documentation, and Codex agent descriptions. The repository intentionally continues to ship a template rather than a root `AGENTS.md`.
- Updated the generic 3D adapter, client, repair modules, tests, and documentation with reusable direct-Blender recovery, explicit skin repair, fitted humanoid repair, manual creature rigging, material visibility diagnostics, winding/seam repair, skeletal export partition checks, evaluated preview bounds, and PDX roughness-to-glossiness packing.
- Adopted the current 3D route policy: firearm units use a weapon-free body plus separately modeled and attached props; existing repair jobs route directly to Blender; other new animated units get at most one supported provider rig/action attempt before Blender continuation.
- Added posed-versus-rest deformation review, bounded seam selection, anatomical support-contact checks, and world-vertical grounding guidance from Chaos Redux commit `00c0e49b72`.

## Intentional exclusions

- All state-ledger skills, templates, helpers, tests, runtime files, and documentation. State ledgers remain Chaos Redux-specific.
- Chaos Redux country, event, Africa, balance, focus, decision, localisation, GFX, sound, and asset-result files.
- Chaos-specific tags, namespaces, IDs, paths, environment variables, scene properties, jobs, locks, receipts, manifests, and generated reports.
- Chaos-owned Meshy wrapper architecture and provider artifact persistence. The general repository retains its app-owned launcher and security contract.
- Completed source-specific 3D assets and skeletal actions. Only reusable code and policy were adopted.
- A root `AGENTS.md`; `AGENTS_template.md` remains the reusable source. `AGENTS_chaos_redux.md` remains an optional example and received only the reusable agent-context, scripted-GUI, and 3D routing corrections; no state-ledger section was imported into it.

## Validation evidence

- All 20 real skills passed `quick_validate.py`, including the newly restored generic `xlsx` repository skill.
- All 25 `.codex` TOML files parsed with Python 3.13 `tomllib`.
- All 23 canonical agents matched their four generated runtime projections; every generator also passed its `--check` mode.
- The feature-asset tool suite passed 25 tests.
- The generic spreadsheet recalculation helper passed 5 provider-free tests, and its help and compile paths passed under Python 3.13 without requiring `openpyxl` at import time.
- The 3D pipeline suite passed 76 tests.
- Manifest-evidence tests passed 8 tests; bootstrap contract suites passed 5 MCP and 16 3D tests.
- The published-manifest validator passed for the current committed revision. New workflow files must be included through normal manifest regeneration after they are committed; revision evidence was not fabricated for the dirty working tree.
- The reusable surfaces had no `chaos_redux`, `chaos-redux`, `chaosx`, or state-ledger identifier hits.
- `git diff --check` passed; only Windows line-ending conversion notices were emitted.
- Achievement template SHA-256 values were verified as:
  - `achievement_template.png`: `248DB006611EB3942550C43DF83802AA6FB24761035FC928B5D34586C0C4C5BA`
  - `achievement_template_grey.png`: `70E073694C1A7D9FE40C63B1EB2E987A8A45B3FFD15CCF789EEAA5B843B90022`
  - `overlay.png`: `89BC80C6AC975BF6F1FF000FF3070B20C337BFB8B8AE966AE35A5540C004D6DD`

No provider call, Blender session, HOI4 launch, live GUI preview, or in-game validation was performed during this repository-level synchronization. Those checks remain job-scoped and must run when an actual mod feature uses the corresponding workflow.
