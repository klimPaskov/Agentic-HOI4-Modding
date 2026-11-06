# Project rules: Specs, plans and upfront consultation

Part of the [hoi4-project-rules](../SKILL.md) skill. `CLAUDE.md` summarizes section 0 (Specs and Plans, Upfront consultation). Read before writing a spec or plan, deciding whether a plan is accepted, or asking the user about a new feature.

### Specs and Plans

Source specifications belong under `docs/specs/<feature_slug>/`.

Subagent plans, improvement addenda, audit follow-up notes, blocked reports, and implementation handoffs belong under `docs/plans/<feature_slug>/`.

The plans folder is a working area. The specs folder holds source design, with acceptance recorded for each relevant claim.
Distinguish explicit user decisions, accepted design with its acceptance basis, implementation evidence, and proposals.
A spec location, date, status label, or old handoff does not prove approval.
Record the user decision or parent acceptance within the user-authorized scope that supports accepted design.
If that basis is missing or conflicting, keep the claim unresolved rather than promoting it through documentation cleanup.
Give every plan or addendum one disposition: implemented with evidence, promoted to a named spec, queued with a reason, rejected with a reason, superseded by a named document, or blocked by an exact limitation.
If an accepted plan changes the feature design, the main agent should merge it into the relevant spec or report that it remains queued.

Keep feature-scoped `docs/assets/<feature_slug>/` workspaces while work is active, blocked, awaiting review, or undergoing acceptance scenarios. Before declaring the feature complete, promote durable provenance, licensing, checksums, review, QA, and runtime-handoff facts into permanent specs, plans, or feature documentation, verify that no runtime reference points into `docs/assets/`, then remove only that completed feature workspace. Never remove a skill-local reference library or another feature's workspace.

### Upfront consultation

For a new or reshaped feature, system, country, route set or asset set, inspect the project first, then ask the genuine open questions once, grouped, each with a suggested answer. Record the answers in `docs/specs/<feature_slug>/decisions.md` and continue without avoidable interruptions; never ask routine implementation questions. Follow `hoi4-feature-planning/references/consultation-questions.md`.
