---
name: hoi4-subagents
description: Use when coordinating custom Codex subagents for HOI4 mod implementation, asset production, text and audio research, audits, active small patches, planning handoffs, or documentation work.
---

# HOI4 Subagents

Use this skill when a HOI4 modding task should be split across custom Codex subagents.

The parent Codex agent remains responsible for final integration, validation, and completion claims. Subagents can inspect, patch, create assets, write addenda, or produce reports. The parent must review their outputs, wire final cross-surface behavior, and carry blockers into the final report.

Do not use subagents to hide uncertainty or pass off responsibility. A subagent handoff is evidence for the parent, not a replacement for parent review.

## Fork context rule

All custom Codex subagents must be spawned with `fork_context=false`.

Do not spawn any subagent with inherited parent-thread context. The parent prompt must include every path, user correction, task constraint, scope boundary, previous handoff status, accepted plan, queued plan, and design rule the subagent needs.

If the needed context only exists in conversation, summarize it into the subagent prompt or write it to the relevant spec, plan, handoff, or repo file before spawning. Then spawn the subagent with `fork_context=false`.

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


## Available subagents

Use `hoi4_repo_explorer` only for read-only repo exploration when touched-file mapping, pattern search, vanilla reference mapping, missing-file recovery, dependency mapping, or edit-order planning is actually unclear. It is not a default preflight agent.

Use `hoi4_improvement_loop_planner` for feature improvement loop planning, detailed expansion specs, historical and regional research notes, and implementation-ready improvement handoffs. This replaces the old mechanic-expander role. It writes plans and addenda. It does not patch gameplay files.

Use `hoi4_asset_source_researcher` for real or archival image sourcing, real leader portraits, historical flags, historical symbols, user-provided source photos, source-image processing, animated portrait bases, and report, news, or custom feature images that must depict real historical material.

Use `hoi4_generated_feature_art` for generated non-icon art, including fictional or alternate-history report images, news images, custom feature images, fictional portraits, fictional flags, faction emblems, UI panels, dossier art, progression-state base art, and animated non-icon presentation pieces.

Use `hoi4_icon_artist` for focus icons, idea icons, national spirit icons, officer corps icons, decision icons, decision category icons, achievement icons, tech icons, formable seals, scripted GUI icons, and small animated icon or button sprites.

Use `hoi4_quote_remark_researcher` for main quotes, exact wording checks, attribution confidence, source comparison, button text, cultural remarks, slogans, allusions, and short references.

Use `hoi4_audio_researcher` for licensed or public domain audio research, source verification, download, `.ogg` conversion, and audio handoff notes.

Use `hoi4_focus_tree_auditor` for focus tree audits and active small patches covering branch depth, route coverage, icons, localisation, rewards, prerequisites, mutual exclusions, AI, focus-formable links, and simplification.

Use `hoi4_decision_mission_auditor` for decision and mission audits and active small patches covering category lifecycle, objective quality, costs, tooltips, scripted GUI decision hooks, AI behavior, cleanup, balance, and exploit risk.

Use `hoi4_country_package_auditor` for country package audits and active small patches covering tags, history, states, leaders, portraits, flags, parties, focus loading, ideas, advisors, units, technologies, claims, cores, localisation, AI, formables, and playable setup.

Use `hoi4_localisation_auditor` for localisation and scripted localisation audits and active small patches covering missing keys, duplicate keys, encoding, tooltip quality, broken dynamic text, namespace consistency, dynamic cost text, and cross-surface text mismatch.

Use `hoi4_scripted_system_architect` for reusable scripted system design and active narrow implementation covering scripted effects, scripted triggers, script constants, event targets, meta effects, variables, tuning values, formable helpers, scripted GUI button helpers, and dynamic helper logic.

Use `hoi4_documentation_curator` for documentation cleanup and consistency during long implementation. It reconciles specs, plans, docs, handoffs, manifests, prompts, reports, and README files, writes source-of-truth maps and resume packets, marks superseded docs, records plan dispositions, and flags contradictions. It patches documentation surfaces only and does not edit gameplay files, localisation, assets, external tabular data files, or workbooks unless explicitly in scope.

Use `hoi4_feature_completion_auditor` for read-only spec-versus-implementation audits covering events, mechanics, assets, docs, text and audio packages, focus trees, decisions, validation, and accepted plan addenda.

Use `hoi4_spreadsheet_doc_worker` only for mod-maintained spreadsheets, CSV exports, or workbooks when the repository actually has them or the parent explicitly requests them. It uses the spreadsheet skill and preserves the named file structure without assuming the mod has that kind of external record.

Do not route new work to obsolete planner aliases. Use `hoi4_improvement_loop_planner` and the `hoi4-improvement-loop` skill.

## Repo explorer use gate

`hoi4_repo_explorer` is an optional scout for uncertain or broad work. It should save time by finding files, patterns, precedents, and edit order before the parent starts a complex implementation.

Use `hoi4_repo_explorer` when at least one of these is true:

- the parent does not know the likely touched files
- the task spans several systems and the edit order is uncertain
- the correct repository pattern or vanilla precedent is unclear
- a named spec, prompt, source file, classification, sprite, tag, localisation key, or helper appears missing and needs recovery evidence
- the feature has enough cross-surface risk that a file map and meaningful validation plan will prevent missed work

Do not spawn `hoi4_repo_explorer` for small or already bounded work, including:

- known-file edits
- user-provided file updates
- direct skill, prompt, or TOML updates
- small bug fixes where the relevant files are already named
- localisation-only cleanup with known keys
- asset-only production that belongs to an asset subagent
- tabular-data-only updates that belong to `hoi4_spreadsheet_doc_worker`
- simple report, docs, or markdown edits where the parent can inspect the provided files directly

When the task is small, the parent should read the known files directly and proceed. Do not use repo exploration as a ritual step or as a replacement for parent review.

## Authority model

Subagents should act at the level their role requires. Do not make every subagent read-only by default.

### Read-only agents

These agents do not patch gameplay files:

- `hoi4_repo_explorer`
- `hoi4_feature_completion_auditor`

They may write reports only when a report path is provided or obvious from the task.

### Plan-only agents

`hoi4_improvement_loop_planner` writes feature expansion specs, improvement addenda, deep research notes, historical connection notes, and implementation handoffs. It does not edit gameplay, localisation, GUI, scripted effects, focus trees, decisions, assets, external tabular data files, workbooks, or country files.

When an event mechanic needs more depth, new branches, new countries, a new formable suite, a new scripted GUI system, deeper regional logic, historical anchors, or a larger route redesign, the planner writes a plan under `docs/plans/<feature_slug>/`. The main agent decides what to implement.

The parent should use this planner after a meaningful implementation tranche, not after every small patch. Do not spawn it again for the same feature until its previous addendum has been implemented, folded into specs, queued with a reason, or rejected with a reason.

### Documentation curation agents

`hoi4_documentation_curator` is patch-capable for documentation surfaces only. It may update Markdown specs, docs, plans, handoffs, manifests, prompt files, README files, route coverage tables, source-of-truth ledgers, resume packets, and documentation indexes inside the current task scope.

Use it after long implementation tranches, after several subagent handoffs, before a major resume, or whenever docs may be stale, contradictory, duplicated, or too numerous. It should reduce confusion for the parent agent by recording what is current, what is superseded, what is queued, what is rejected, and what still needs a decision.

It must not edit gameplay files, localisation, scripted localisation, GUI, GFX, events, focuses, decisions, ideas, scripted effects, scripted triggers, on_actions, country setup, history, AI files, assets, audio, binary files, or external tabular data files. It does not replace `hoi4_feature_completion_auditor`, `hoi4_localisation_auditor`, `hoi4_spreadsheet_doc_worker`, or `hoi4_repo_explorer`.

### Asset-production agents

Asset subagents create source files, processed previews, final DDS outputs, contact sheets, manifests, and asset handoffs. They do not wire gameplay, localisation, GFX, GUI, events, focuses, decisions, or workbooks unless the parent gives a narrow exception.

### Active small-patch agents

These agents are patch-capable by default inside the current task scope:

- `hoi4_scripted_system_architect`
- `hoi4_decision_mission_auditor`
- `hoi4_focus_tree_auditor`
- `hoi4_country_package_auditor`
- `hoi4_localisation_auditor`

They do not need a separate permission prompt to fix small, local issues that are clearly connected to the current feature, mechanic, country, focus tree, decision category, GUI surface, or localisation surface.

They should inspect first, then patch only when the fix is narrow, reversible, and supported by the relevant skill. They may edit files they own for the current task surface and directly related dependency files. They must not search for unrelated cleanup outside the feature they were spawned for.

Active small patches include:

- varying decision costs inside an existing category
- making cost and requirement text clearer
- adding dynamic localisation for existing variables, targets, state names, route names, or cost values
- replacing raw trigger exposure with custom trigger tooltips
- adjusting safe AI weights or target checks
- fixing obvious availability, visibility, cooldown, bypass, and cleanup gaps
- fixing focus prerequisites, route locks, mutual exclusions, focus filters, icon references, and small reward variety
- adding a narrow scripted helper plus a few direct call sites when repeated logic is already present
- fixing an existing formable decision check, reveal condition, or state-control requirement
- correcting country package references such as focus loading, party names, leader ids, tag setup, localisation, and simple starting setup

Active small patches do not include:

- creating or expanding a whole mechanic
- adding a full event chain
- replacing a focus route family
- designing a new formable suite
- building a new scripted GUI system
- creating a new country package from scratch
- changing broad balance philosophy
- rewriting large localisation sets for tone only
- changing asset source rules
- claiming final completion of the parent feature

When a patch-capable subagent sees a broad design gap, it writes a plan handoff and stops. The main agent decides whether to implement it.

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

If a patch touches localisation, list the keys changed. If it touches decisions or focuses, list affected ids. If it touches scripted helpers, list helper names and call sites. If it touches country setup, list tags and state ids or state groups.

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

## Asset routing

Do not use one broad asset worker for mixed visual packages.

Use:

- `hoi4_asset_source_researcher` for real, archival, historical, documentary, or public-source images when the asset must show real historical material
- `hoi4_generated_feature_art` for generated non-icon fictional, alternate-history, symbolic, extreme-route, or unique event art
- `hoi4_icon_artist` for generated gameplay icons, formable seals, decision category icons, and small animated icon or button sprites

The parent agent must give each asset subagent a bounded prompt with exact asset names, target sizes, source mode, final folders, sprite names when already registered, reference folders, and constraints.

For flags, the parent prompt must state whether each flag is a base flag, ideology variant, route variant, cosmetic-tag flag, historical flag, or fictional flag. Base flags for existing countries must be preserved unless explicitly in scope. Ideology variants must be distinct designs, not recolors or copied emblems. Historical flags and attested symbols belong with `hoi4_asset_source_researcher`. Fictional or alternate-history variants belong with `hoi4_generated_feature_art`.

Asset subagents may create source files, PNG previews, DDS files, contact sheets, manifests, and `gfx_handoff.md`. They must not edit `.gfx`, localisation, GUI, event, focus, idea, decision, script, history, country, or workbook files unless the parent explicitly expands scope.

## Quote, remark, and audio research routing

Use separate research agents when the text and audio package has enough work to justify it.

Use `hoi4_quote_remark_researcher` for quotes, exact wording, attribution confidence, button text, cultural remarks, slogans, allusions, and short references.

Use `hoi4_audio_researcher` for audio research, license verification, download, `.ogg` conversion, and audio handoff notes.

Use `hoi4_asset_source_researcher` or `hoi4_generated_feature_art` for image work according to the source mode required by `hoi4-feature-assets`.

The main agent owns final wording, localisation, audio wiring, playback helpers, and docs alignment.

## Improvement routing

Use `hoi4_improvement_loop_planner` when a feature or feature-adjacent mechanic needs new design material, not just an audit finding.

The planner should read `hoi4-improvement-loop`, `hoi4-feature-planning`, and relevant system skills. It should inspect actual implementation, specs, plans, docs, localisation, and asset notes when available. It should then write concrete design material that expands the feature through playable mechanics, historical or regional connections, AI behavior, and visual needs. It should not patch gameplay files.

The main agent should deploy the planner often enough to keep major features from becoming shallow after new mechanics are added, but not so often that plans pile up. For the same feature, do not deploy another planner pass until the previous addendum is implemented, promoted to specs, queued with a reason, or rejected.

Audit subagents may include compact improvement handoffs inside their reports. If a gap requires a new route family, new GUI system, new formable suite, new country package, or new event chain, they should recommend a plan-mode pass rather than trying to patch it.

## Optional spreadsheet and workbook routing

`hoi4_spreadsheet_doc_worker` is a context-light spreadsheet or workbook worker, not a general documentation agent.

Use it only when the required output is a spreadsheet, CSV export, XLSX workbook, balancing table, route matrix, asset ledger, localisation tracking sheet, or similar table that already exists in the repository or is explicitly requested by the parent.

The parent prompt must provide the workbook or CSV path, sheet, ids, row targets, source localisation keys, or exact fields to update when possible.

The worker should read only:

- the parent prompt
- the repository spreadsheet skill
- the named workbook or CSV
- the exact source files needed to mirror player-facing text, implementation status, asset status, route coverage, balance values, or documentation fields
- named source files explicitly provided by the parent

It should not read HOI4 wiki pages, vanilla documentation, vanilla files, broad implementation guides, or unrelated repo systems. It should not edit docs, specs, plans, manifests, gameplay files, localisation files, assets, GFX, GUI, events, focuses, decisions, ideas, history, scripted effects, scripted triggers, or other workbooks unless the parent explicitly expands scope.

The worker must preserve workbook or CSV structure, formatting, formulas, filters, and validation unless the parent explicitly asks for structural changes.


## Parent review

The parent agent must review every subagent output before relying on it.

Before final completion, the parent should check:

- subagent changes are inside approved scope
- patch handoffs identify changed files and ids
- plan handoffs are either implemented, queued, or rejected with a reason
- documentation curator handoffs identify promoted, queued, rejected, superseded, and unresolved documents when one was used
- assets are wired or reported as pending
- validation reflects the final repo state
- docs, specs, plans, and any explicitly scoped external records agree

A subagent patch can reduce workload. It never owns the final completion claim.
