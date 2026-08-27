# Starter documentation and tools audit handoff

> Historical handoff, partially superseded on 2026-08-27. The repository now uses one shared renderer with Qoder, Cursor, and OpenCode wrappers under `.tools/sync/`, while generated runtime folders remain ignored and machine-local. References below to a deleted root synchronizer, tracked Qoder outputs, a separate v2 manifest filename, or optional Qoder manifest components describe the earlier tranche and are not current source-of-truth instructions.

## Scope and result

Audited the reusable starter documentation, setup manifests, and target tool surface against the current Chaos Redux repository without modifying Chaos Redux and without editing executable or tool files.

Updated the generic instructions and the optional Chaos Redux fixture so the documented HOI4 MCP contract requires `hoi4.tech_inspect`, `hoi4.tech_render`, and `hoi4.tech_compare`, and the documented 3D contract requires Meshy 7 rather than Meshy 6.

Added generic optional Codex-to-Qoder documentation and corresponding optional manifest components and profile entries because the concurrent target Qoder worker now provides `.qoder/` outputs and `.tools/sync_qoder_agents.py`.

## Source-of-truth map

| Surface | Current authority | Status and boundary |
| --- | --- | --- |
| Reusable project instructions | `AGENTS_template.md` | Patched; this remains the generic source copied or adapted into a mod’s root `AGENTS.md`. |
| Reviewed Chaos Redux example | `AGENTS_chaos_redux.md` | Patched as an optional fixture; it remains intentionally Chaos-specific and is not the generic source. |
| Starter package workflow | `README.md` | Patched; it documents manual setup, MCP route health, Meshy 7, and optional Qoder usage. |
| MCP evidence and recovery contract | `docs/systems/hoi4_agent_tools_mcp_integration.md` | Left unchanged because it already names all technology and doctrine routes and has no accidental prose hard wraps. |
| Super Events workflow reference | `docs/super_events/README.md` | Patched only to join accidental mid-sentence prose wraps; runtime content and lineage claims were preserved. |
| Current setup manifest | `hoi4-mod-setup.v2.manifest.json` | Patched with optional Qoder runtime and synchronization components plus `core_with_qoder`; regenerate evidence after the final commit. |
| Legacy manifest projection | `hoi4-mod-setup.manifest.json` | Patched with the matching parameter-free Qoder components and profile; regenerate the exact schema-1 projection after the final commit. |
| Canonical Codex agents | `.codex/agents/*.toml` | Concurrent worker-owned source; not modified by this audit. |
| Generated Qoder agents | `.qoder/agents/*.md` | Concurrent worker-owned generated output; validated read-only and not hand-edited by this audit. |
| Qoder synchronization | `.tools/sync_qoder_agents.py` | Concurrent worker-owned executable; audited read-only and referenced by the new manifest components. |
| 3D workflow | `.tools/3d_pipeline/` and its checked-in contracts | Concurrent worker-owned tool surface; current target files already declare Meshy 7, so no executable or lock edits were made here. |

The target does not need a root `AGENTS.md`. This repository is the reusable starter itself, and the manifest’s `core.agents` component correctly installs the adapted template as `AGENTS.md` in a destination mod; adding a root file here would make the package’s own instructions project-specific and would create a second source competing with `AGENTS_template.md`.

## Reconciled contradictions

| Contradiction | Evidence | Resolution |
| --- | --- | --- |
| Generic template claimed the documented package had no Technology Tree Viewer while the README, MCP guide, manifest capabilities, and current target bootstrap require the three technology routes. | Previous `AGENTS_template.md` MCP section; `README.md`; `docs/systems/hoi4_agent_tools_mcp_integration.md`; both manifests. | Replaced the absence claim with the required `hoi4.tech_inspect`, `hoi4.tech_render`, and `hoi4.tech_compare` health gate and exact blocker behavior. |
| Generic starter README and template named Meshy 6 while the current Chaos Redux workflow and concurrent target 3D contract require Meshy 7. | Previous `README.md` and `AGENTS_template.md`; source Chaos Redux `AGENTS.md`; target `.tools/3d_pipeline/README.md` and `config/meshy_tool_contract.json`. | Updated README, generic template, and Chaos fixture to Meshy 7 and forbade silent downgrade. |
| Target had no reusable documentation for a second agent runtime while the concurrent Qoder worker added a generated Qoder runtime. | New `.qoder/agents/`, `.qoder/mcp.json`, `.tools/sync_qoder_agents.py`, and `qoder_sync.md`. | Added optional generic Qoder guidance and `runtime.qoder.sync`, `runtime.qoder.agents`, and `core_with_qoder` manifest entries; the default core profile remains Codex-only. |

No unresolved documentation contradiction remains inside the patched surfaces. The manifest evidence revision remains unresolved until the parent commits the concurrent Qoder and tool files and regenerates both manifests.

## Plan and handoff dispositions

| Document or handoff | Disposition | Reason |
| --- | --- | --- |
| `docs/plans/workflow_sync/subagent_handoffs/qoder_sync.md` | Implemented by concurrent worker; reviewed and left unchanged | It provides the Qoder file list, authority decisions, exclusions, and synchronization validation that the new generic manifest references. |
| `docs/plans/workflow_sync/subagent_handoffs/docs_tools_audit.md` | Implemented by this audit | This handoff records the source map, reconciliation, tool recommendations, validation, and remaining parent action. |
| `docs/systems/hoi4_agent_tools_mcp_integration.md` | Left unchanged | It already matches the current technology-route and evidence contract. |
| `docs/super_events/README.md` | Implemented cleanup | Accidental prose hard wraps were joined without changing the workflow or asset lineage. |
| No other named workflow plan or handoff | Not present in the target scope | No additional plan disposition was invented. |

## Duplicate, superseded, and stale-document audit

- No duplicate current-state starter README was found; `README.md` remains the package-level workflow reference and `docs/systems/hoi4_agent_tools_mcp_integration.md` remains the detailed MCP contract.
- `AGENTS_chaos_redux.md` is an optional reviewed fixture, not a second generic template; its manifest component remains opt-in and its Chaos-specific rules were not generalized into the default template.
- No stale prompt file was found in the named target documentation scope.
- The source Chaos Redux root `AGENTS.md` contains project-only rules such as Chaos event ids, CXT setup carriers, event spreadsheets, and Chaos paths; those were intentionally excluded from the generic starter and are not treated as reusable requirements.
- The source Chaos Redux `.tools` package contains project-only Event 006, Soviet Collapse, Chaos tag, state-puzzle, event-catalog, and packaging scripts; those were not copied or exposed by the generic manifest.

## Markdown hard-wrap audit

The following accidental hard wraps were corrected:

- `README.md`: joined prose paragraphs in the package overview, setup, subagent, Super Events, portrait, and completion sections while preserving fenced and indented code blocks and list structure.
- `docs/super_events/README.md`: joined prose paragraphs and the wrapped caller instruction while preserving the runtime list, code block, and source-lineage note.

No accidental mid-sentence or mid-clause prose hard wraps remain in `AGENTS_template.md`, `AGENTS_chaos_redux.md`, `README.md`, `docs/systems/hoi4_agent_tools_mcp_integration.md`, or `docs/super_events/README.md` under the audit detector; deliberate Markdown structures were preserved.

## Tool and script audit recommendations

The target tool files were audited read-only as required.

- Keep the target generic 3D workflow additions from the concurrent worker, including `README.md`, `meshy_tool_contract.json`, `meshy_tool_schema.lock.json`, `meshy_client.py`, `blender_client.py`, `run_pilot.py`, `verify_environment.py`, and the adapter tests; they generalize the source Chaos Redux Meshy 7 route without copying Chaos asset job roots.
- Preserve the target’s app-owned Meshy credential route and job-root containment. Do not copy source Chaos absolute paths, `CHAOS_REDUX_*` environment variables, pilot job registries, or provider artifacts into the starter.
- If a future generic 3D task needs the source wrapper behavior, add a reviewed generic Meshy wrapper and manifest evidence only through the owning 3D workflow; do not copy `run_meshy_mcp.cmd` or `run_meshy_mcp.ps1` unchanged because the source versions carry Chaos-specific runtime assumptions.
- Do not add source `.tools/audit_event6_*`, `.tools/audit_chaosx_country_tags.py`, `.tools/audit_hoi4_country_tags.py`, `.tools/audit_event6_country_api.py`, or `.tools/audit_event6_flags.py` to the generic package; they protect named Chaos Event 006/Soviet Collapse surfaces and cannot be generalized by path renaming alone.
- Do not add source `.tools/build_formable_state_puzzle_consumer.py`, `.tools/build_formable_state_registry.py`, `.tools/generate_formable_state_geometry_registry.py`, `.tools/generate_formable_state_puzzle_runtime.mjs`, or `.tools/generate_state_puzzle_asia.py` to the generic package until their Chaos schemas, `chaosx_*` identifiers, map artifacts, and asset converter paths are replaced by a separately accepted generic state-puzzle workflow.
- Do not add source `.tools/generate_chaosx_building_positions.py` or `.tools/hoi4_dds.dpf` to the generic package; the generator preserves Chaos-specific camp and facility rows and the profile is not a standalone reusable contract.
- Do not add source `.tools/export_event_catalog_csv.py` or `.tools/package_chatgpt_project_sources.*`; they depend on Chaos workbook/catalog names and project packaging paths and belong in a project-specific workflow.
- The generic Qoder synchronizer should remain the canonical reusable addition; its read-only `--check` mode is now a manifest block validation, and generated Qoder outputs must stay opt-in and absent from the default core profile.

## Stale prompt and instruction audit

- The obsolete template instruction claiming no Technology Tree Viewer was removed.
- All target prose references audited for `Meshy 6` are now `Meshy 7`; no stale target `Meshy 6` or Technology Tree Viewer absence claim remains.
- The generic Qoder section explicitly preserves `.codex/agents/*.toml` as canonical and `.qoder/agents/*.md` as generated, preventing duplicate hand-edit work.
- The source Chaos Redux dual-runtime instructions remain in the Chaos fixture only; Chaos-specific names and paths were not copied into generic starter instructions.
- No stale prompt filename or superseded prompt instruction was found under the named target scope.

## Validation run

- `python .tools/sync_qoder_agents.py --check` passed and reported 24 synchronized generated files.
- `python -m json.tool hoi4-mod-setup.v2.manifest.json` and the legacy manifest both passed JSON parsing.
- Direct Draft 202012 schema validation of `hoi4-mod-setup.v2.manifest.json` passed with 28 components and 3 profiles.
- The legacy manifest equals the exact parameter-free schema-1 projection of the v2 manifest.
- Targeted `rg` checks confirmed the three technology routes, Meshy 7 wording, optional Qoder component ids, and absence of stale Meshy 6 or no-viewer wording.
- The Markdown hard-wrap detector passed for all five named documentation files after excluding deliberate code blocks and list/table structure.

## Skipped or blocked validation

- `python scripts/validate_published_manifests.py` cannot pass until the parent commits the concurrent `.qoder/` and `.tools/sync_qoder_agents.py` additions and regenerates `generated_for_revision` plus every `expected_files` array from that exact commit; the current failure is the expected source-file-missing-at-selected-revision error for `.tools/sync_qoder_agents.py`.
- No gameplay, live MCP, 3D provider, Blender, launcher, or Hearts of Iron IV validation was run because this was documentation-only work and those surfaces are outside scope.
- No executable or tool file was edited by this audit.

## Parent decisions and next actions

1. Keep the optional Qoder components and `core_with_qoder` profile if the concurrent Qoder worker’s files are accepted; otherwise remove the two manifest components and profile together with the Qoder package, not individually.
2. After the final concurrent files are settled, run `python scripts/generate_manifest_evidence.py --manifest hoi4-mod-setup.v2.manifest.json --legacy-manifest hoi4-mod-setup.manifest.json --source-root . --revision <final-40-char-commit>` and then rerun `python scripts/validate_published_manifests.py`.
3. Review the manifest component dependency ordering in the setup application; `runtime.qoder.agents` depends on `runtime.qoder.sync`, and both depend on `core.subagents`.
4. Keep the target without a root `AGENTS.md`; installers should adapt `AGENTS_template.md` into the destination mod’s root.
5. If the generic 3D workflow changes its required generation model again, update the 3D skill, tool contract, bootstrap lock, manifest notes, README, and both AGENTS surfaces as one versioned change.

## Remaining risks

- The manifests are intentionally pending exact-commit evidence regeneration after concurrent files land; using them as a published package before that step will fail closed.
- The optional Qoder MCP file currently registers only the portable `hoi4-agent-tools.cmd` route; Meshy and Blender routes remain deferred until a project activates the 3D workflow and the bootstrap can generate project-local routes safely.
- The Chaos fixture remains project-specific by design and must not be selected as the generic starter’s project instructions without adaptation.
