# Codex agent and configuration synchronization

## Scope

This handoff records the comparison from `chaos_redux/.codex/agents/` and `chaos_redux/.codex/config.toml` into the starter repository's `.codex/agents/` and `.codex/config.toml`.

The target repository has no root `AGENTS.md`; the source `chaos_redux/AGENTS.md`, the target `hoi4-subagents` skill, the target agent definitions, and the named MCP package evidence were read before editing.

Only `.codex/agents/**`, `.codex/config.toml`, and this handoff were in scope. Chaos Redux was not modified. Gameplay, skills, tools, README files, manifests, and root guidance were not modified.

## Applied changes

### 3D model pipeline

`.codex/agents/hoi4_3d_model_pipeline.toml` and its registry description in `.codex/config.toml` now require the verified Meshy 7 route and exact `meshy-7` model identifier instead of the stale Meshy 6 wording.

The 3D prompt now requires the pinned `@meshy-ai/meshy-mcp-server`, `meshy_animate` action-source candidates, exact live tool and schema evidence, and an explicit blocker when Meshy 7 is unavailable.

Required skeletal motion must come from verified `meshy_animate` output or an explicitly user-approved professional source. Blender may import, retarget, clean, correct contacts or roots, normalize, bake, synchronize, export, and reimport approved motion, but may not create final replacement motion through manual keys, simple procedural transforms, whole-rig movement, static-pose aliases, or semantic reuse of another role.

The prompt also requires multi-frame role evidence for applicable attack or fire and death actions, records source task or action identifiers and approvals, preserves one-image Meshy input discipline, and requests native alpha for workflow-generated references when the inspected consumer permits transparency.

The 3D prompt's stale Technology Tree Viewer absence claim now points to the installed read-only `hoi4.tech_inspect`, `hoi4.tech_render`, and `hoi4.tech_compare` routes and requires an exact blocker if a linked route is unavailable.

### Technology MCP wording

`.codex/agents/hoi4_repo_explorer.toml` now routes technology and doctrine exploration through `hoi4.tech_inspect`, `hoi4.tech_render`, and `hoi4.tech_compare` when advertised.

`.codex/agents/hoi4_localisation_auditor.toml` now uses those same read-only routes for linked technology or doctrine localisation evidence instead of claiming that the viewer is absent.

The other target agents already had the current MCP ownership, unavailable-route blocker, source-only non-equivalence, and weighted audit-patch-compare rules. No duplicate router or tool-specific wrapper was added.

### Optional dependency configuration

The target config retains `max_threads = 24`, `max_depth = 2`, the existing approval and sandbox settings, the implicit workspace `cwd = "."`, and the optional Comfy Cloud portrait entry.

Chaos Redux's active Meshy, Blender, Blender Lab, absolute repository paths, `CHAOS_REDUX_*` environment variables, and Chaos-specific allowlists were deliberately not copied. The starter config continues to omit 3D MCP entries until a feature needs 3D; the repository-owned bootstrap materializes the concrete Meshy and Blender routes then. This preserves ordinary-mod startup without optional 3D dependencies and keeps provider credentials out of the baseline config.

## Definition comparison and exclusions

The direct source-to-target comparison covered every source definition and every target definition.

| Chaos Redux source definition | Target disposition |
| --- | --- |
| `chaosx_3d_model_pipeline` | Updated `hoi4_3d_model_pipeline` with generalized Meshy 7 and approved-action rules. |
| `chaosx_ai_probability_auditor` | No change; the target version already has the richer scenario, candidate-pool, structural MCP, and audit-patch-compare contract. |
| `chaosx_asset_source_researcher` | No change; the target version is already generic and preserves source, licensing, portrait, and GFX handoff boundaries. |
| `chaosx_country_package_auditor` | No change; the target version is already generic and has current probability and MCP routing. |
| `chaosx_decision_mission_auditor` | No change; the target version already contains the bounded GUI ownership and decision value-budget guidance. |
| `chaosx_documentation_curator` | No change; the target version generalizes feature paths and tabular-data boundaries. |
| `chaosx_event_completion_auditor` | Not copied; the target's `hoi4_feature_completion_auditor` is the generalized counterpart. |
| `chaosx_event_ui_worker` | No change; the target version is already event-owned, generic, and MCP-complete. |
| `chaosx_focus_tree_auditor` | No change; the target version already has current focus and probability routing. |
| `chaosx_generated_event_art` | Not copied; the target's `hoi4_generated_feature_art` is the generalized counterpart. |
| `chaosx_icon_artist` | No change; the target version already covers generic icon families and exact counter evidence. |
| `chaosx_improvement_loop_planner` | No change; the target version generalizes event planning to features and already routes MCP evidence. |
| `chaosx_localisation_auditor` | Updated only to remove the stale Technology Tree Viewer absence claim. |
| `chaosx_portrait_creator` | No change; the target version already uses the generic portrait-production and provider-routing contract. |
| `chaosx_repo_explorer` | Updated only to remove the stale Technology Tree Viewer absence claim. |
| `chaosx_scripted_system_architect` | No change; the target version already has current helper ownership and weighted/MCP routing. |
| `chaosx_skill_maintainer` | No change; the target version already has context isolation, reusable-skill scope, and MCP guidance ownership. |
| `chaosx_spreadsheet_doc_worker` | Not copied; the target version intentionally supports any named repository workbook or CSV rather than the Chaos event catalog. |
| `chaosx_super_event_audio_researcher` | No change; the target version is the selected-only, generic, rights-checked super-event audio route. |
| `chaosx_super_event_text_researcher` | Not copied; the target's `hoi4_quote_remark_researcher` and `hoi4_super_event_quote_researcher` split generic and registered-super-event quote work. |

Target-only definitions remain registered because they are reusable general routes: `hoi4_audio_researcher`, `hoi4_feature_completion_auditor`, `hoi4_generated_feature_art`, `hoi4_quote_remark_researcher`, `hoi4_super_event_art_researcher`, and `hoi4_super_event_quote_researcher`.

Chaos-only event ids, Chaos namespaces, Chaos event catalog paths, Chaos-specific portrait and asset folders, and source-specific absolute paths were not generalized into the target definitions.

## Validation

- Parsed all 24 target TOML files with Python `tomli` successfully.
- Confirmed the config registry has 23 agent entries, 23 matching agent files, and no missing or unregistered definitions.
- Confirmed target `.codex/agents/**` and `.codex/config.toml` contain no Chaos-specific paths, no stale Meshy 6 references, and no stale Technology Tree Viewer absence claims.
- Confirmed the installed tool surface advertises the read-only `mcp__hoi4_agent_tools__hoi4_tech_inspect`, `mcp__hoi4_agent_tools__hoi4_tech_render`, and `mcp__hoi4_agent_tools__hoi4_tech_compare` routes, plus the required probability, focus, event, GUI, and map routes used by the existing agent contracts.
- `git diff --check -- .codex` completed without whitespace errors.
- Hearts of Iron IV was not launched.

## Out-of-scope follow-up

The target README, `AGENTS_template.md`, 3D skill, 3D tool README, Meshy tool contract, and bootstrap still contain older Meshy 6 or Technology Viewer wording outside the assigned `.codex/**` ownership. They were intentionally left unchanged for the parent to reconcile in a separate documentation/tooling task; the agent and config surfaces in this handoff no longer repeat those stale claims.
