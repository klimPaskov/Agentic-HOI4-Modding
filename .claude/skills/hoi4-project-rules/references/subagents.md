# Project rules: Subagents

Part of the [hoi4-project-rules](../SKILL.md) skill. `CLAUDE.md` summarizes section 0 (Subagents). Read before delegating to a project subagent, choosing a model tier or reviewing a subagent handoff.

### Subagents

Use project custom subagents when a task needs bounded research, asset production, audit, recursive expansion, or documentation work that can be separated from main implementation.

`hoi4-subagents` is the detailed source of truth for subagent routing, ownership boundaries, handoff quality, audit cadence, asset routing, text and audio research routing, and the recursive mechanic expansion loop.

The main agent remains responsible for final implementation, final wiring, final review, validation, and completion claims. Subagents return evidence, files, manifests, spec addenda, patches, or handoff notes depending on the parent-granted mode. The main agent must review their outputs and carry blockers or uncertainty into the final report.

All project custom subagents must receive a fully explicit, self-contained prompt and no inherited conversation context. Claude Code subagents start isolated, Codex agents are spawned with `fork_turns="none"`, the other generated runtimes use their isolated agent route, and DSH composes the subagent from the prompt alone. If a subagent needs a user correction, task constraint, current implementation status, or prior handoff detail, the parent must pass it explicitly in the prompt or write it into the relevant spec, plan, handoff, or repo file before spawning.

Each specialist runs on the Claude model tier set by the `model` field of its canonical file in `.claude/agents/`:

| Tier | Agents |
| --- | --- |
| Opus | `hoi4_improvement_loop_planner` |
| Sonnet | `hoi4_3d_model_pipeline`, `hoi4_feature_completion_auditor`, `hoi4_localisation_auditor`, `hoi4_scripted_system_architect`, `hoi4_skill_maintainer` |
| Haiku | `hoi4_ai_probability_auditor`, `hoi4_asset_source_researcher`, `hoi4_audio_researcher`, `hoi4_country_package_auditor`, `hoi4_decision_mission_auditor`, `hoi4_documentation_curator`, `hoi4_event_ui_worker`, `hoi4_focus_tree_auditor`, `hoi4_generated_feature_art`, `hoi4_icon_artist`, `hoi4_portrait_creator`, `hoi4_quote_remark_researcher`, `hoi4_repo_explorer`, `hoi4_spreadsheet_doc_worker`, and the `hoi4_super_event_*` researchers |

A parent may request a stronger model for one task when that task clearly needs it. To change a tier permanently, edit the canonical agent file and rerun `python .tools/sync/sync_agents.py`; other runtimes map the tier through `.tools/sync/agent_profiles.json`.

Use these high-level routing rules:

- Use `hoi4_repo_explorer` only when file locations, existing patterns, vanilla references, likely touchpoints, missing-file recovery, or implementation order are unclear. Do not use it for small known-file edits, provided-file edits, direct skill or prompt updates, localisation-only cleanup, asset-only production, or tasks already bounded to exact files. The parent should inspect the known files directly for those cases.
- Use asset subagents for non-portrait visual production: `hoi4_asset_source_researcher`, `hoi4_generated_feature_art`, and `hoi4_icon_artist`. All character portrait work belongs to `hoi4_portrait_creator`.
- Use `hoi4_event_ui_worker` only for a dedicated scripted GUI introduced and owned by one named event or event-owned mechanic, under the Event UI worker gate in `hoi4-subagents` (ownership proof, prompt contents, what the worker and the parent own, and what stays out of scope).
- Use `hoi4_portrait_creator` for complete portrait production: grounded source research and wired source placeholders, fictional portraits through the selected image-generation route, user-supplied grounded-final validation, processing, DDS conversion, portrait-specific wiring, manifests, and handoffs. The user owns the configured grounded-subject provider run; the agent never operates RunPod.
- When an asset subagent is asked to produce animation or a 3D model, the parent prompt must require `hoi4-frame-animation` for 2D frame sheets and `hoi4-3d-model-pipeline` for skeletal `.anim` actions, and must carry the complete 3D prompt contract in the `3D model-production agents` section of `hoi4-subagents` (source and refinement evidence, the profile's generation model and one image per geometry task, the route chosen under the production guide's Route selection, the job's credit budget, sourced unit audio with selection audio, bespoke vanilla-green counters, scale crosswalk, and reimport proof). The parent owns `.asset`, entity, counter GFX, sound definitions, runtime wiring, and live proof.
- Use quote and audio research subagents only for specialised sourced text or audio work: `hoi4_quote_remark_researcher` and `hoi4_audio_researcher`.
<!-- HOI4_MOD_SETUP:COMPONENT:workflow.super_events:START -->
- Use `hoi4-super-events` for the complete installed Super Events runtime and presentation contract, and the Super Events sections of `hoi4-feature-planning`, `hoi4-events`, `hoi4-feature-assets`, `hoi4-text-audio-research`, and `hoi4-subagents` for their normal ownership boundaries. Keep registration, caller, text, quote, response, image, optional or explicitly required audio, provenance, documentation, cleanup, and the acceptance scenario aligned. Spawn `hoi4_super_event_quote_researcher`, `hoi4_super_event_audio_researcher`, or `hoi4_super_event_art_researcher` only when its narrow handoff is needed.
<!-- HOI4_MOD_SETUP:COMPONENT:workflow.super_events:END -->
- Use audit subagents before completion claims: `hoi4_focus_tree_auditor`, `hoi4_decision_mission_auditor`, `hoi4_country_package_auditor`, `hoi4_localisation_auditor`, `hoi4_ai_probability_auditor`, and `hoi4_feature_completion_auditor`.
- Use `hoi4_ai_probability_auditor` for read-only scenario-based audits of AI weights, MTTH, event `ai_chance`, random lists, focus and research selection, decision and mission scores, AI strategy factors, and declared custom weighted pools. It uses the available HOI4 MCP probability routes or calculations from the actual script, returns scenario-specific findings, and does not patch source or choose the intended balance target.
- Use `hoi4_scripted_system_architect` for reusable scripted effects, triggers, script constants, event targets, meta effects, variable patterns, and dynamic helper design.
- Use `hoi4_documentation_curator` during long implementation when specs, plans, docs, manifests, prompts, reports, or subagent handoffs may be stale, duplicated, contradictory, or too numerous; `hoi4-subagents` defines its documentation-only authority.
- Use `hoi4_spreadsheet_doc_worker` only when this repository actually has a maintained workbook or planning spreadsheet and implementation facts are available. Spreadsheet fields that mirror in-game wording must match the in-game localisation wording.
- When a maintained workbook generates CSV or other tabular exports, declare the workbook as the sole editable source, name the repository exporter command and generated outputs, run the exporter after every successful workbook update, and never edit or treat a stale export as source of truth.
- Use `hoi4_skill_maintainer` for non-trivial skill creation, cleanup, routing updates, or multi-skill consistency work.
- Use `hoi4_improvement_loop_planner` after meaningful implementation tranches of major feature work, when a mechanic, focus tree, country package, decision system, text or audio research need, visual progression, lore package, or audit finding needs deeper design. It does not patch gameplay files. Do not spawn it again for the same feature until the previous addendum has been implemented, folded into specs, queued with a reason, or rejected; Improvement routing in `hoi4-subagents` defines its addenda.

Patch-capable subagents are allowed to make small, local improvements by default when the change is inside the current task surface and directly improves the feature. They may vary costs, add clearer dynamic localisation, improve tooltips, adjust safe AI weights, add narrow helper calls, fix route locks, add cleanup hooks, or correct existing formable checks. `hoi4_event_ui_worker` may implement the accepted bounded GUI introduced by a named event, but no subagent may invent an unplanned or shared scripted GUI system, expand a whole mechanic, redesign a route family, add a new country package, or change the requested design on its own. Broad gaps become a plan under `docs/plans/<feature_slug>/`. Every subagent edit needs a handoff that lists changed files, identifiers, meaningful validation when it affects confidence, and remaining risks. Documentation cleanup work should also record which specs, plans, handoffs, manifests, or reports were promoted, queued, rejected, superseded, or left unresolved.

For a changed AI weight, MTTH-backed score, random selection, strategy factor, or weighted target, compare representative named scenarios before and after through `hoi4_ai_probability_auditor` as `hoi4-subagents` describes; calculations from the actual script are sufficient when the analyzer fails, provided assumptions and the difference between scores and probabilities are explicit. The auditor stays read-only and does not choose balance targets.
