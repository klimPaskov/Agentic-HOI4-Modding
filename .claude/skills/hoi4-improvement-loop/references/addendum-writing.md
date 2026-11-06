# HOI4 Improvement Loop: Writing the expansion addendum

Part of the [hoi4-improvement-loop](../SKILL.md) skill. Read before writing or reviewing an expansion addendum.

## Feature loop improvement role

This skill is the main feature-improvement loop for the mod. It is used after a feature, mechanic, country package, decision system, focus route, formable, scripted GUI, asset set, or presentation material has enough shape to evaluate, but before the main agent calls the feature finished.

The loop should expand ideas and existing mechanics thoroughly using `hoi4-feature-planning` as the quality standard. It should turn rough systems into playable designs with regional logic, player choices, AI behavior, consequences, visual support, and implementation-ready handoffs. It is especially useful for large feature reworks where the first implementation pass creates many surfaces that now need deeper connections.

The loop should not write a checklist for the main agent to mechanically fill in. It should write a real expansion spec. The spec can include narrative paths, decision families, focus route architecture, country packages, formables, state groups, scripted GUI concepts, animated sprite needs, source-researched text or audio thresholds, achievements, and acceptance criteria when those make the feature stronger.

## Research and historical connection standard

Deep research is part of improvement, not decoration. When a feature has historical, cultural, political, regional, military, scientific, religious, or ideological inspiration, the loop should look for concrete anchors that can improve the design.

Research should help the planner find:

- plausible historical parallels and contrasts
- local institutions, factions, military traditions, myths, old borders, treaties, rival claims, and political symbols
- names for routes, formables, councils, ministries, movements, decisions, spirits, and events
- region-specific consequences instead of generic global effects
- foreign reactions that make sense for the period and the campaign state
- asset and portrait constraints for real people, real symbols, and real historical images
- hidden branches that feel earned because the region, ideology, leader, artifact, or prior event supports them

Use the approved repository research method from `AGENTS.md` when the existing files do not provide enough support. Do not invent source claims. If a historical connection is uncertain, mark it as uncertain and use it as inspiration rather than as a factual assertion.

The result should still play well. Research should make mechanics sharper, not turn the plan into a dry history note.

## The improvement question

Start with the feature promise. Ask what the player expects the system to be about.

A civil war event promises fear, rupture, faction choices, and aftermath. A formable route promises identity, territory, recognition, integration, and a new political horizon. A strange-state mechanic promises hidden logic, unsettling progression, and consequences that normal diplomacy cannot explain. A scripted GUI promises a system important enough to see and manage.

Then compare that promise with the current feature. The gap is the expansion target.

Do not turn every gap into more buttons. Some features need fewer buttons and clearer stakes. Some focus trees need stronger route locks, not more focuses. Some country packages need one memorable mechanic, not ten small modifiers. Some GUI panels need better hierarchy, not more art.

## What the addendum should contain

The structure should follow the mechanic. Write naturally, but make the design complete enough for implementation.

A strong addendum usually explains:

- whether expansion is still useful or whether the loop should stop because more mechanics would bloat the system
- the playable promise
- the part that feels shallow or disconnected
- the stronger loop that should replace or extend it
- the choices that change outcomes
- the values, timers, missions, state targets, or route locks that make the loop work
- the AI behavior and limits
- the visual, localisation, audio, GUI, and asset needs
- the failure states and cleanup needs
- the accepted limits, including what should not be added

Use prose, route maps, state diagrams, package tables, UI descriptions, event families, decision groups, or branch maps only when they make the idea clearer. Avoid forcing every addendum into the same heading order.

Do not write vague lines such as `add more flavor`, `make decisions deeper`, `add a hidden formable`, `improve AI`, or `add animations`. Name the route, action, state group, cost type, reveal condition, failure consequence, asset family, and AI behavior where they matter.

When the weakness is weighted AI, timing, or random selection, turn the intended improvement into named scenarios and measurable ordering, timing, dominance, or starvation expectations. Route the mandatory read-only pass through `hoi4_ai_probability_auditor`: establish the baseline with `hoi4.probability_inspect`, select evaluation, sweep, simulation, sequence, comparison, or render evidence according to the declared scenario, let the owner apply any bounded patch, and require `hoi4.probability_analyze` with `analysis: "compare"` against the same scenarios afterward. The auditor does not choose balance targets or patch source. If the required MCP route is unavailable, record the exact blocker and leave the improvement unvalidated; source-only review is not equivalent. Do not ask the implementation agent to prove an exact probability from an incomplete candidate pool or undeclared external state.

## Design moves that matter

Good improvement usually adds pressure, consequence, identity, or feedback.

Useful moves include:

- a pressure value that rises, falls, and changes available actions
- a deadline that can be met, missed, delayed, or exploited
- a rival faction inside the country with its own route consequences
- two incompatible philosophies inside one route family
- focuses that unlock decisions which keep mattering after the focus completes
- rewards that depend on state control, local support, legitimacy, supply, faction cohesion, or recognition
- partial success and failure outcomes instead of binary success
- AI route plans based on war state, stability, industry, ideology, threat, and faction position
- assets that evolve across route stages, danger states, extreme-route corruption, or formable completion
- formables that require proof through territory, politics, leadership, or feature history
- scripted GUI only when visual management is clearer than normal decisions

Weak moves include more flat modifiers, more repeated buttons, more generic events, more hidden content without a reveal path, and more spectacle without gameplay.

