# Project rules: Completion proof and simplification reporting

Part of the [hoi4-project-rules](../SKILL.md) skill. `CLAUDE.md` summarizes section 5. Read before claiming a goal complete and before writing the final report.

## 5. Completion Proof and Simplification Reporting

A goal can never be marked complete unless it is actually complete.

For every goal, especially large event, mechanic, focus-tree, country-package, balance, UI, or asset goals, completion requires evidence. The agent must finish the requested implementation, update all related files, run or document the required checks, and report any blocker or simplification.
Unavailable tools, inconclusive analysis, or missing historical evidence limit what was checked; they do not by themselves prevent completing otherwise finished implementation.
Use the MCP retry limits in `mcp-usage.md`, keep source review distinct from observed game behavior, and never report an unavailable check as passed.
After reviewing the relevant rules and code and the useful available checks, finish when the requested implementation is present and no known defect remains.
Further investigation needs a specific unanswered question that could change the implementation; if an indispensable answer is unavailable, state that obstacle once and finish independent work instead of repeating the investigation.
Do not wait for or request user-owned game testing as a completion step.
If a specific render, measurement, or test result is itself a requested output, its absence still leaves that output incomplete.

Validation reporting must be useful. Run basic syntax hygiene internally when helpful, but do not spend the final report listing checks that only restate mandatory rules, such as unsupported operator checks or brackets balance or BOM encoding checks, etc. Never tell the user directly: `Validation passed: diff whitespace check, brace balance on touched scripts, no unsupported <=/>=, localisation BOM intact, git diff --check passed, no remaining X references, workspace is clean.` Mention validation only when it is task-specific, could realistically fail, found a problem, changed the implementation, or gives the user useful evidence. Leave passing boilerplate checks out of the user-facing report.

Do not claim completion when:

- only the most visible part was implemented
- a focus tree was created but not reviewed, customized, balanced, localized, and wired
- a large batch of countries received generic or copied content
- balance checks were skipped
- localisation is missing
- AI behavior is missing
- assets are missing, unwired, or undocumented
- a named event-owned scripted GUI is missing its `hoi4_event_ui_worker` handoff, intermediate MCP preview and correction evidence, or matched final layout comparison
- a custom unit model is missing its rights-checked sourced sound package, source evidence, animation synchronization map, bespoke vanilla-green counter package, mandatory installed-vanilla counter inspection, or runtime handoff
- maintained event logs, documentation, tables, or manifests that describe the changed system are stale
- any requested route, country, decision, mission, achievement, event chain, focus path, custom progression milestone, researched text or audio package, or asset is missing
- a fallback or simplification was used without explicit approval

Balance checks are implementation work, not optional polish. If the spec or user asks for balance validation, the agent must inspect the relevant variables, scripted effects, decisions, mission outcomes, trigger conditions, AI weights, and scenario behavior. A vague statement that balance was adjusted is not enough.
When a tool cannot analyze the mechanic, calculate representative cases from the actual scripted values and conditions, distinguish AI scores from probabilities, and state important assumptions.

Do not bulk-generate large focus trees, country packages, decisions, localisation, or validation reports and call them complete. Generated or scripted drafts are acceptable only when every result is manually reviewed, customized to the country or route, wired into the mod, localized, given AI behavior, documented, and checked against the spec.

If any requested item is not implemented to the fullest extent, report it under a clear section such as `Simplifications, omissions, and blockers`. Even small deviations must be listed. If no simplifications were made, the final report must explicitly say so and provide evidence through files changed, audits, meaningful validation notes, and completed checklists.

Do not claim a goal is complete just because the game loads or because the most visible part works.

For large events, mechanics, focus-tree rewrites, country packages, balance passes, or multi-system goals, produce a concrete completion report. The report should list files changed, systems touched, balance checks, tests or meaningful validation scenarios, assets reused or created, documentation updated, and remaining blockers.
Update one current report instead of creating repeated status reports, and explain concretely what does not work, what could not be checked, and what action is needed.
Lead with the result and any needed user action; keep hashes, internal status labels, and long check inventories in technical notes unless the user requests them.

Every simplification must be reported. This includes skipped routes, fallback trees used in place of bespoke trees, missing assets, missing localisation, missing AI behavior, missing focus paths, missing dynamic scaling, hardcoded values where dynamic logic was requested, placeholder content, or weaker substitutes.

If there are no simplifications, say so explicitly and provide evidence through audits, docs, or changed files. If the goal cannot be fully implemented, report that the goal is incomplete instead of presenting partial work as done.
