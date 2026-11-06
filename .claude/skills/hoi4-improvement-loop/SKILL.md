---
name: hoi4-improvement-loop
description: Use when a working or drafted HOI4 feature, focus tree, decision system, country, formable, GUI or asset set still feels thin and needs a concrete expansion spec or improvement handoff.
---

# HOI4 Improvement Loop

Use this skill for loop improvement of features and feature-adjacent systems when a feature works, has a draft, or has an audit result, but the design still feels thin, generic, disconnected, static, or too small for the idea.

This skill writes expansion specs. It is not a checklist and it is not a code patch skill. The structure of each addendum should follow the mechanic. Some addenda need a route map. Some need a country package matrix. Some need a UI description. Some need a short design note that changes one decision category. The output should be open in form and concrete in content.

Use the `hoi4_improvement_loop_planner` subagent when the parent agent wants a plan-writing helper.

Open the reference that matches the work (see the Reference map) before writing or reviewing an addendum.

Always apply these rules:

- Write a real addendum shaped by the mechanic, not a checklist. Name the route, action, state group, cost, reveal condition, failure consequence, asset family and AI behavior (full guidance in `references/addendum-writing.md`).
- Run the loop after a meaningful tranche of work and before a feature is called finished, but never stack passes: no new planner pass until the previous addendum is implemented, folded into `docs/specs/<feature_slug>/`, queued with a reason, or rejected with a reason (Deployment cadence below).
- Stop when more mechanics would bloat the system, and write a closure handoff of only the final small tasks (Stop condition below).
- Weighted AI, timing or random-selection weaknesses need named scenarios and measurable expectations, and the mandatory read-only pass through `hoi4_ai_probability_auditor` (baseline with `hoi4.probability_inspect`, then `hoi4.probability_analyze` with `analysis: "compare"`). Source-only review is not equivalent; record the exact blocker if the MCP route is unavailable (`references/addendum-writing.md`).
- Technology or doctrine changes need `hoi4.tech_inspect` and `hoi4.tech_render` evidence (`references/mechanic-improvement-guides.md`). Unit, building, creature, vehicle or map-entity changes need a 3D model review routed to `hoi4_3d_model_pipeline` (`references/presentation-improvement.md`).
- `docs/assets/<feature_slug>/` is a temporary workspace: promote durable facts into permanent documentation and delete it before the feature is fully complete, never touching skill-local reference assets or another feature's workspace (`references/presentation-improvement.md`).
- Accepted design is folded into specs, not left in loose plans, and the main agent never claims a feature complete while an accepted addendum is unimplemented and unreported (Parent agent responsibility below).

## Reference map

- [Writing the expansion addendum](references/addendum-writing.md): Read before writing or reviewing an expansion addendum. Covers: Feature loop improvement role; Research and historical connection standard; The improvement question; What the addendum should contain; Design moves that matter.
- [Improving features, focus trees, decisions, formables, countries and AI](references/mechanic-improvement-guides.md): Read when the addendum touches a feature chain, focus tree, decision or mission system, formable, country package or AI behavior. Covers: Feature improvement; Focus tree improvement; Decision and mission improvement; Formable nation improvement; Country package improvement; AI improvement.
- [Improving scripted GUI, assets, super-events and sourced text or audio](references/presentation-improvement.md): Read when the addendum touches a scripted GUI, animated presentation, asset or model, super-event, or sourced text or audio. Covers: Scripted GUI and animated presentation improvement; Asset and visual improvement; Super-event improvement; Text and audio research improvement.
- [Planner and patch subagents](references/planner-subagent.md): Read before launching the improvement loop planner, acting as one, or delegating small improvement patches. Covers: Subagent behavior.

## Core purpose

A feature should not stop when it compiles. It can still fail if the player has no hard choices, the AI has no plan, the visuals are static, the focus tree is a reward ladder, the decisions are passive buttons, the country package is only a tag, or the event text promises a larger system than the mechanics deliver.

The improvement loop turns that weakness into a playable expansion spec. The spec should explain what the stronger version is, how it plays, how it escalates, how it can fail, what the AI does, what visual and text support is needed, and what the main agent should build.

Good improvement changes play. It does not only add size.

## When to use it

Use this skill during implementation or audit when a system feels technically present but thin.

Common triggers:

- the user says a mechanic is shallow, too rigid, too generic, or missing its intended identity
- an auditor finds repeated rewards, passive decisions, weak route logic, missing AI, or missing cleanup
- a country exists but has no starting problem, survival loop, route identity, or ambition
- a formable exists but has no discovery, integration, price, recognition, or post-formation play
- a decision category has many buttons but no pressure, mission, timer, target, or visible state
- a scripted GUI exists but it is only decoration and does not help the player manage a mechanic
- an event has one popup but no consequence memory, reaction logic, or escalation path
- sourced quote, remark, or audio research has presentation pieces but no campaign threshold that justifies it
- assets do not change when route, danger, phase, or identity changes

Do not use this skill to inflate simple bug fixes. Use it when the bug reveals a real design gap.

## Deployment cadence

The main agent should actively deploy the improvement loop during large feature implementation, especially after a meaningful tranche of work adds several new mechanics, countries, focus routes, formables, decision systems, scripted GUI elements, or source-researched text or audio candidates. This is the best moment to ask whether the new surfaces are connected, reactive, regionally grounded, and worth playing.

Do not spawn the improvement loop planner repeatedly for the same feature while the previous addendum is still waiting. Before another loop pass, the previous plan should be implemented, folded into `docs/specs/<feature_slug>/`, explicitly queued with a reason, or rejected with a reason. This prevents endless plan stacking.

A second loop pass is justified when the main agent has implemented the previous addendum and the new implemented layer creates new design questions. It is also justified after a completion auditor finds a different large design gap that was not covered by the previous plan.

## Stop condition and anti-bloat rule

The improvement loop is not infinite. Its job is to improve the event until the design is deep, connected, replayable, and clean enough to finish. If another expansion would add noise, bloat, repeated mechanics, unnecessary darkness, duplicate routes, or more maintenance burden than gameplay value, the loop should say so clearly.

The planner should recommend stopping expansion when all of these are true:

- the event has no known simplifications, fallbacks, or shallow placeholder content
- the implemented mechanics match the accepted specs and plans
- player choices have real consequences and replay value
- AI behavior exists for systems that AI countries can use
- localisation, optional feature history or logging surfaces, docs, assets, GUI surfaces, focus routes, decisions, formables, and sourced text or audio packages are properly aligned where relevant
- open gaps are small finalization tasks, validation tasks, polish, or documentation alignment, not missing design depth
- previous improvement addenda are implemented, folded into specs, queued with a reason, or rejected with a reason

When this condition is met, the planner should not write a new large expansion. It should write a closure handoff instead. That handoff should list only the final small tasks, such as last localisation checks, final validation scenarios, asset handoff verification, alignment with any explicitly scoped external records, audit reruns, or cleanup. It should explicitly say that broad expansion is no longer recommended because the system is now clean and additional mechanics would bloat it.

A closure handoff should not claim implementation completion on its own. It tells the main agent that the design loop can stop, the new plan can be finished, final validations can run, and the goal can be marked complete if the main agent verifies there are no blockers, simplifications, fallbacks, or unresolved accepted plans.

## Relationship with other skills

Use the system skill that owns the surface being improved.

When an addendum affects any supported focus, event-chain, technology/doctrine, weighted-logic, scripted-GUI, or map surface, require the matching MCP baseline and post-change evidence under its owner skill. Weighted audit-patch-compare evidence must route through `hoi4_ai_probability_auditor`. Exact unavailable routes remain blockers or unresolved evidence, and source-only review is not equivalent.

- `hoi4-feature-planning` is the standard for expansion spec quality. The addendum should be idea-first, detailed, and implementation-ready, but not forced into a rigid template.
- `hoi4-events` owns event chains, event details, escalation variants, optional mod-specific logging surfaces when event work uses them, docs, and documentation alignment.
- `hoi4-focus-trees` owns route depth, branch interaction, focus rewards, route AI, focus icons, and focus documentation.
- `hoi4-decisions-missions` owns decisions, missions, costs, objectives, gameplay-changing GUI actions, hidden decision visibility, tooltips, AI actions, and cleanup.
- `hoi4-scripted-gui` owns scripted GUI reference mapping, layout and content budgets, iterative MCP preview and comparison, click-region and state review, and visual acceptance.
- `hoi4-feature-assets` owns visual assets, animated sprites, animated portraits, source rules, DDS outputs, manifests, contact sheets, and sprite handoffs.
- `hoi4-text-audio-research` owns sourced quotes, cultural remarks, slogans, title-like references, audio source checks, license checks, attribution notes, and copyright-risk notes. The owning implementation skill handles wiring and alignment with any explicitly scoped repository surfaces.
- `hoi4-subagents` explains when to use a planner subagent, a patch-capable system subagent, an asset worker, a read-only auditor, or other subagents.

## Specs and plans folders

Full feature specification packs belong under:

```text
docs/specs/<feature_slug>/
```

Improvement addenda, audit follow-up plans, subagent handoffs, and implementation notes belong under:

```text
docs/plans/<feature_slug>/
```

The plans folder holds working handoffs. A spec path, status label, old handoff, or implementation evidence does not establish design approval. Record the explicit user decision or parent acceptance within existing authorization that supports each accepted claim. Preserve unsupported or conflicting claims as unresolved.

If an improvement addendum is accepted as source design, fold it into the relevant spec under `docs/specs/<feature_slug>/` or record it as accepted and queued with its acceptance basis and reason. Record implementation evidence separately. Do not let accepted design live only as an unclassified loose plan.

## Parent agent responsibility

The main agent decides what to do with the addendum. It can implement it now, queue it, reject it with a reason, or ask for a narrower pass. When the user takes part, present the proposals as one round answered with Adopt, Adapt, Defer or Reject, and record each answer in the feature's `decisions.md` with the mapping in `hoi4-feature-planning/references/consultation-questions.md`.

Do not claim a major feature is complete while an accepted expansion addendum is unimplemented and unreported. If the addendum is queued, say where it is queued and why it was not included in the current implementation.

Accept an improvement when it makes the system more playable, reactive, readable, visually coherent, regionally specific, or integrated with mod systems. Reject it when it only adds size, noise, difficulty, darkness, or spectacle without improving play.

If the improvement loop returns a closure handoff, the main agent should finish the listed final tasks, run final validations, confirm that no accepted plan remains unresolved, and then mark the goal complete only if the completion evidence supports it.
