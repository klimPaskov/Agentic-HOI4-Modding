---
name: hoi4-subagents
description: Use when coordinating HOI4 project subagents for implementation, asset production, text and audio research, audits, small patches, planning handoffs or documentation work.
---

# HOI4 Subagents

Use this skill when a HOI4 modding task should be split across project subagents.

The parent agent remains responsible for final integration, validation, and completion claims. Subagents can inspect, patch, create assets, write addenda, or produce reports. The parent must review their outputs, wire final cross-surface behavior, and carry blockers into the final report. Subagents never ask the user; they list open questions in their handoff, and the parent adds them to its next batch of questions (Upfront consultation in `CLAUDE.md`).

Capture a task baseline before patch-capable subagents begin. Assign disjoint files and serialize any work that would touch the same source.

Do not use subagents to hide uncertainty or pass off responsibility. A subagent handoff is evidence for the parent, not a replacement for parent review.

This file is a router for delegating HOI4 modding work. It keeps the rules that apply to every delegation (parent ownership, fork context rule, the authority model principle, handoff after any patch, parent review) and points to the references that hold the rest, including the role subsections of the Authority model. References are as binding as this file, and no rule was dropped.

Quick routing. The full roster, with model tiers and each role's boundaries, is in [agent-roster](references/agent-roster.md): read it before spawning any agent.

- scouting: `hoi4_repo_explorer`, only when files or patterns are really unclear
- plans and docs: `hoi4_improvement_loop_planner` (plans only), `hoi4_documentation_curator` (documentation only)
- images: `hoi4_asset_source_researcher` (real or archival), `hoi4_portrait_creator` (every character portrait), `hoi4_generated_feature_art` (non-icon art), `hoi4_icon_artist` (icons, seals, small animated sprites)
- 3D: `hoi4_3d_model_pipeline`
- text and audio: `hoi4_quote_remark_researcher`, `hoi4_audio_researcher`, and the three `hoi4_super_event_*` researchers below
- audits with small patches: `hoi4_focus_tree_auditor`, `hoi4_decision_mission_auditor`, `hoi4_country_package_auditor`, `hoi4_localisation_auditor`, `hoi4_scripted_system_architect`, and `hoi4_event_ui_worker` for an event-owned UI only
- read-only audits: `hoi4_feature_completion_auditor`, `hoi4_ai_probability_auditor`
- tables: `hoi4_spreadsheet_doc_worker`

How to work:

1. Pick the agent from the roster, then read the reference for its kind of work (gates, authority, asset routing, 3D, small patches, planning) before writing its prompt.
2. Spawn it without inherited conversation context and put every path, constraint and prior decision in the prompt.
3. Require a handoff for every edit. Read-only and audit agents return their findings inline. Audit and patch-capable roles run `python -B .tools/check.py quick --paths <files>` before reporting, and delegation prompts name this step ([read-only-plan-and-docs-agents](references/read-only-plan-and-docs-agents.md)).
4. When the task touches focus trees, event chains, technology or doctrine trees, weighted logic, scripted GUI or maps, MCP evidence is mandatory and source-only review is not equivalent ([mcp-evidence-in-handoffs](references/mcp-evidence-in-handoffs.md)).
5. Review every output yourself (Parent review below). A subagent never owns the completion claim.

Costly to miss, with the full text in the references: `hoi4_event_ui_worker` only for a UI that a named event owns ([spawn-gates](references/spawn-gates.md)). Any patch to an AI weight or probability needs the audit-patch-compare cycle ([active-small-patches](references/active-small-patches.md)). A 3D job needs its credit budget, the `MESHY_API_KEY` gate and sourced audio in the prompt ([3d-model-production](references/3d-model-production.md)). Asset agents work in the temporary `docs/assets/<feature_slug>/` workspace, which the parent cleans up only at full completion ([asset-research-routing](references/asset-research-routing.md)).

## Reference map

- [Agent roster](references/agent-roster.md): Read before choosing which specialist to spawn, or when a task could fit several agents. It holds each role's job, model tier and boundaries. Covers: Available subagents.
- [Spawn gates](references/spawn-gates.md): Read before spawning `hoi4_event_ui_worker` or `hoi4_repo_explorer`. This file holds the "Event UI worker gate" and the "Repo explorer use gate" sections. Covers: Event UI worker gate; Repo explorer use gate.
- [Read-only, plan-only and documentation agents](references/read-only-plan-and-docs-agents.md): Read before spawning a read-only auditor, `hoi4_improvement_loop_planner` or `hoi4_documentation_curator`, or before telling an agent to write a report. It holds the "Read-only agents", "Plan-only agents" and "Documentation curation agents" subsections of the Authority model.
- [Asset and research routing](references/asset-research-routing.md): Read before spawning an asset, portrait, icon, quote or audio specialist, writing its prompt, or cleaning up the `docs/assets/` workspace. It holds the "Asset-production agents" subsection, "Asset routing" and "Quote, remark, and audio research routing". Covers: Asset routing; Quote, remark, and audio research routing.
- [3D model production](references/3d-model-production.md): Read before routing or briefing `hoi4_3d_model_pipeline`. This file holds the "3D model-production agents" subsection of the Authority model, including the prompt requirements, the handoff content and the parent-owned wiring.
- [Active small patches](references/active-small-patches.md): Read before spawning or briefing a patch-capable agent, before any patch to an AI weight or probability (audit-patch-compare cycle), or when deciding whether a fix is a small patch or needs a plan. It holds the "Active small-patch agents" subsection.
- [MCP evidence in handoffs](references/mcp-evidence-in-handoffs.md): Read before routing a task that touches focus trees, event chains, technology or doctrine trees, weighted logic, scripted GUI or maps, and before writing or accepting a handoff that cites MCP evidence. Covers: MCP evidence in handoffs.
- [Improvement and spreadsheet routing](references/planning-and-spreadsheet-routing.md): Read before deploying `hoi4_improvement_loop_planner` again for a feature, or before routing work to `hoi4_spreadsheet_doc_worker`. Covers: Improvement routing; Optional spreadsheet and workbook routing.

## Fork context rule

All project subagents must be spawned without inherited conversation context.

Claude Code subagents start isolated: invoke the specialist through the `Agent` tool by its hyphen-case name (`hoi4-repo-explorer` for `hoi4_repo_explorer`). In Codex, spawn the generated agent with `fork_turns="none"`. Cursor, Qoder, and OpenCode isolate their generated agents by runtime. Never substitute a generic built-in agent for a named HOI4 specialist.

Do not spawn any subagent with inherited parent-thread context. The parent prompt must include every path, user correction, task constraint, scope boundary, previous handoff status, accepted plan, queued plan, and design rule the subagent needs.

If the needed context only exists in conversation, summarize it into the subagent prompt or write it to the relevant spec, plan, handoff, or repo file before spawning. Then spawn the subagent without inherited conversation context.

This rule applies to every subagent type:

- read-only agents
- plan-only agents
- asset-production agents
- text and audio research agents
- active small-patch agents
- scripted-system agents
- documentation agents
- skill-maintenance agents

The goal is to keep subagents narrow, reproducible, and grounded in explicit inputs instead of inherited conversation state.

## Authority model

Subagents should act at the level their role requires. Do not make every subagent read-only by default.

## Mandatory handoff after any patch

Every subagent that edits files must write a handoff back to the parent. If the feature slug is known, place it under:

```text
docs/plans/<feature_slug>/subagent_handoffs/
```

The handoff should include:

- files changed
- exact gameplay surface changed
- changed ids, keys, tags, helper names, or state groups
- before and after behavior
- why the change is safe and bounded
- meaningful validation run, limited to task-specific checks that affect confidence
- skipped meaningful validation and why
- remaining issues or design gaps
- any follow-up the parent must implement

Do not fill handoffs with passing boilerplate checks that only restate AGENTS.md rules. Basic syntax hygiene can be done internally unless it found a problem or materially changed the patch.

## Plan and spec paths

Full accepted feature specs belong under:

```text
docs/specs/<feature_slug>/
```

Subagent plans, expansion addenda, audit follow-up notes, blocked reports, implementation handoffs, and patch handoffs belong under:

```text
docs/plans/<feature_slug>/
```

The plans folder is the working area. The specs folder is the source-of-truth design area. If a plan is accepted as source design, the main agent should fold it into the relevant spec file or clearly report that it remains queued.

Do not create new planning folder names such as `docs/planning/` unless the user explicitly asks.

## Parent review

The parent agent must review every subagent output before relying on it.

Before final completion, the parent should check:

- subagent changes are inside approved scope
- patch handoffs identify changed files and ids
- plan handoffs are either implemented, queued, or rejected with a reason
- documentation curator handoffs identify promoted, queued, rejected, superseded, and unresolved documents when one was used
- assets are wired or reported as pending
- custom-unit sound packages include defensible Internet sources, immutable originals, licensing evidence, checksums, synchronization maps, and parent-owned runtime status, or are explicitly blocked
- validation reflects the final repo state
- docs, specs, plans, and any explicitly scoped external records agree

A subagent patch can reduce workload. It never owns the final completion claim.

<!-- HOI4_MOD_SETUP_SUPER_EVENTS_START -->
## Super Events research routes

When the installed `hoi4-super-events` workflow is selected, route bounded work to `hoi4_super_event_quote_researcher` for quote candidates, attribution, response text, cultural fit, and copyright notes; `hoi4_super_event_audio_researcher` for source, license, download, verified conversion, and audio evidence; and `hoi4_super_event_art_researcher` for image direction, source-mode research, named-reference review, and explicitly authorized image production.

Spawn each without inherited conversation context. Include the mod root, stable registration ID, presentation role, owning caller, accepted plan path, exact question, named inputs, exact outputs and handoff path, source mode or audio decision, user constraints, and forbidden files. These agents do not edit gameplay, event, GUI, GFX, localisation, scripted localisation, sound definitions, or registry files; the main agent reviews the handoff and owns final wiring and completion.
<!-- HOI4_MOD_SETUP_SUPER_EVENTS_END -->
