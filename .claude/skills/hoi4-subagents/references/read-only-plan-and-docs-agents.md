# HOI4 Subagents: Read-only, plan-only and documentation agents

Part of the [hoi4-subagents](../SKILL.md) skill. Read before spawning a read-only auditor, `hoi4_improvement_loop_planner` or `hoi4_documentation_curator`, or before telling an agent to write a report. It holds the "Read-only agents", "Plan-only agents" and "Documentation curation agents" subsections of the Authority model.

### Read-only agents

These agents do not patch gameplay files:

- `hoi4_repo_explorer`
- `hoi4_feature_completion_auditor`
- `hoi4_ai_probability_auditor`

They may write reports only when a report path is provided or obvious from the task.

Some runtimes refuse report-file writes from subagents. Ask every read-only or audit subagent to return its complete findings inline as well, and allow scratch helper files only for intermediate data such as scan outputs or range lists that the parent can read afterwards.
Audit and patch-capable roles run `python -B .tools/check.py quick --paths <their changed or audited files>` before reporting, list its errors and warnings by rule id, and state that a passing run covers only the properties its checks name (`AGENTS.md` section 4a); delegation prompts name this step.

### Plan-only agents

`hoi4_improvement_loop_planner` writes feature expansion specs, improvement addenda, deep research notes, historical connection notes, and implementation handoffs. It does not edit gameplay, localisation, GUI, scripted effects, focus trees, decisions, assets, external tabular data files, workbooks, or country files.

When an event mechanic needs more depth, new branches, new countries, a new formable suite, a new scripted GUI system, deeper regional logic, historical anchors, or a larger route redesign, the planner writes a plan under `docs/plans/<feature_slug>/`. The main agent decides what to implement.

The parent should use this planner after a meaningful implementation tranche, not after every small patch. Do not spawn it again for the same feature until its previous addendum has been implemented, folded into specs, queued with a reason, or rejected with a reason.

### Documentation curation agents

`hoi4_documentation_curator` is patch-capable for documentation surfaces only. It may update Markdown specs, docs, plans, handoffs, manifests, prompt files, README files, route coverage tables, source-of-truth ledgers, resume packets, and documentation indexes inside the current task scope.

Use it after long implementation tranches, after several subagent handoffs, before a major resume, or whenever docs may be stale, contradictory, duplicated, or too numerous. It should reduce confusion for the parent agent by recording what is current, what is superseded, what is queued, what is rejected, and what still needs a decision.

It must not edit gameplay files, localisation, scripted localisation, GUI, GFX, events, focuses, decisions, ideas, scripted effects, scripted triggers, on_actions, country setup, history, AI files, assets, audio, binary files, or external tabular data files. It does not replace `hoi4_feature_completion_auditor`, `hoi4_localisation_auditor`, `hoi4_spreadsheet_doc_worker`, or `hoi4_repo_explorer`.

