# HOI4 Subagents: Active small patches

Part of the [hoi4-subagents](../SKILL.md) skill. Read before spawning or briefing a patch-capable agent, before any patch to an AI weight or probability (audit-patch-compare cycle), or when deciding whether a fix is a small patch or needs a plan. It holds the "Active small-patch agents" subsection.

### Active small-patch agents

These agents are patch-capable by default inside the current task scope:

- `hoi4_scripted_system_architect`
- `hoi4_decision_mission_auditor`
- `hoi4_focus_tree_auditor`
- `hoi4_country_package_auditor`
- `hoi4_localisation_auditor`
- `hoi4_event_ui_worker` for an accepted event-owned UI only

They do not need a separate permission prompt to fix small, local issues that are clearly connected to the current feature, mechanic, country, focus tree, decision category, GUI surface, or localisation surface.

They should inspect first, then patch only when the fix is narrow, reversible, and supported by the relevant skill. They may edit files they own for the current task surface and directly related dependency files. They must not search for unrelated cleanup outside the feature they were spawned for. In a checkout shared with other lanes they revert or commit only their own hunks (`git restore -p`, `git add -p`, or `hoi4-shared-git-commit`) and never restore a whole file another lane edits.

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

Any patch to an AI weight, probability-bearing modifier, MTTH-backed score, random-selection weight, strategy factor, or weighted target check requires an audit-patch-compare cycle. Run `hoi4_ai_probability_auditor` first to establish named baseline scenarios. Before editing, the owner preserves an immutable pre-edit source copy at a real filesystem path, the exact scenario fixture, and SHA-256 hashes of the copied bytes. The owner applies the bounded change, then the auditor runs `hoi4.probability_analyze` with `analysis: "compare"` against the same scenarios using actual before and after paths. The probability auditor remains read-only, does not choose the intended balance target, and does not patch source.

If immutable probability snapshots are committed as durable before-source evidence, preserve the copied bytes through narrowly scoped Git attributes and any clean filters.
When attributes change after staging, plain `git add` may reuse cached normalization; force a path-specific `git add --renormalize` under byte-preserving attributes and filters, or explicitly promote a blob with `git hash-object -w --no-filters` and a path-specific index update.
Verify that the raw committed blob's SHA-256 matches the recorded copied-byte hash, reading it without text decoding, newline conversion, or checkout filters.
Preserve the physical original and keep any mismatch and dependent comparison proof unresolved until repaired and reverified.

Active small patches do not include:

- creating or expanding a whole mechanic
- adding a full event chain
- replacing a focus route family
- designing a new formable suite
- inventing an unplanned or shared scripted GUI system; implementing the accepted bounded UI introduced by a named event belongs to `hoi4_event_ui_worker`
- creating a new country package from scratch
- changing broad balance philosophy
- rewriting large localisation sets for tone only
- changing asset source rules
- claiming final completion of the parent feature

When a patch-capable subagent sees a broad design gap, it writes a plan handoff and stops. The main agent decides whether to implement it.

