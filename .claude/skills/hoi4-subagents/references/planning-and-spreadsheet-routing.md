# HOI4 Subagents: Improvement and spreadsheet routing

Part of the [hoi4-subagents](../SKILL.md) skill. Read before deploying `hoi4_improvement_loop_planner` again for a feature, or before routing work to `hoi4_spreadsheet_doc_worker`.

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
- the repository `xlsx` skill
- the named workbook or CSV
- the exact source files needed to mirror player-facing text, implementation status, asset status, route coverage, balance values, or documentation fields
- named source files explicitly provided by the parent

It should not read HOI4 wiki pages, vanilla documentation, vanilla files, broad implementation guides, or unrelated repo systems. It should not edit docs, specs, plans, manifests, gameplay files, localisation files, assets, GFX, GUI, events, focuses, decisions, ideas, history, scripted effects, scripted triggers, or other workbooks unless the parent explicitly expands scope.

The worker must preserve workbook or CSV structure, formatting, formulas, filters, and validation unless the parent explicitly asks for structural changes.


