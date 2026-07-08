---
name: hoi4-improvement-loop
description: Use when recursively deepening HOI4 mod mechanics, events, focus trees, countries, decisions, assets, lore, sourced text or audio packages, scripted GUI, formables, and implementation audits into concrete expansion specs and improvement handoffs.
---

# HOI4 Improvement Loop

Use this skill for loop improvement of features and feature-adjacent systems when a feature works, has a draft, or has an audit result, but the design still feels thin, generic, disconnected, static, or too small for the idea.

This skill writes expansion specs. It is not a checklist and it is not a code patch skill. The structure of each addendum should follow the mechanic. Some addenda need a route map. Some need a country package matrix. Some need a UI description. Some need a short design note that changes one decision category. The output should be open in form and concrete in content.

Use the `hoi4_improvement_loop_planner` subagent when the parent agent wants a plan-writing helper.

## Feature loop improvement role

This skill is the main feature-improvement loop for the mod. It is used after a feature, mechanic, country package, decision system, focus route, formable, scripted GUI, asset set, or presentation material has enough shape to evaluate, but before the main agent calls the feature finished.

The loop should expand ideas and existing mechanics thoroughly using `hoi4-feature-planning` as the quality standard. It should turn rough systems into playable designs with regional logic, player choices, AI behavior, consequences, visual support, and implementation-ready handoffs. It is especially useful for large feature reworks where the first implementation pass creates many surfaces that now need deeper connections.

The loop should not write a checklist for the main agent to mechanically fill in. It should write a real expansion spec. The spec can include narrative paths, decision families, focus route architecture, country packages, formables, state groups, scripted GUI concepts, animated sprite needs, source-researched text or audio thresholds, achievements, and acceptance criteria when those make the feature stronger.

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

- `hoi4-feature-planning` is the standard for expansion spec quality. The addendum should be idea-first, detailed, and implementation-ready, but not forced into a rigid template.
- `hoi4-events` owns event chains, event details, escalation variants, optional mod-specific logging surfaces when event work uses them, docs, and documentation alignment.
- `hoi4-focus-trees` owns route depth, branch interaction, focus rewards, route AI, focus icons, and focus documentation.
- `hoi4-decisions-missions` owns decisions, missions, costs, objectives, scripted GUI decision surfaces, hidden decision visibility, tooltips, AI actions, and cleanup.
- `hoi4-feature-assets` owns visual assets, animated sprites, animated portraits, source rules, DDS outputs, manifests, contact sheets, and sprite handoffs.
- `hoi4-text-audio-research` owns sourced quotes, cultural remarks, slogans, title-like references, audio source checks, license checks, attribution notes, and copyright-risk notes. The owning implementation skill handles wiring and alignment with any explicitly scoped repository surfaces.
- `hoi4-subagents` explains when to use a planner subagent, a patch-capable system subagent, an asset worker, a read-only auditor, or other subagents.

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

## Specs and plans folders

Full feature specification packs belong under:

```text
docs/specs/<feature_slug>/
```

Improvement addenda, audit follow-up plans, subagent handoffs, and implementation notes belong under:

```text
docs/plans/<feature_slug>/
```

The plans folder is where subagents add working handoffs. The specs folder is where accepted source-of-truth feature specs live.

If an improvement addendum is accepted as source design, the main agent should either implement it or fold the design into the relevant spec file under `docs/specs/<feature_slug>/`. Do not let accepted design live only as a loose plan if the final spec is meant to be complete.

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

## Feature improvement

For features, improve the idea into a chain or system only when the concept benefits from it. Ask what the event starts, what it pressures, what it changes, and what later systems remember.

A feature addendum can define event families for escalation, negotiation, failure, outside reaction, and aftermath. It can define baseline stages, optional escalation variants that unlock new behavior, decisions and missions, AI strategies, country-specific reactions, ideology-specific reactions, source-researched text or audio thresholds, and defeat aftermath.

## Focus tree improvement

For focus trees, improve route meaning before adding length. A tree is the playable identity of a country. The player should be able to look at the branches and understand what kind of country they are building.

A focus addendum can define route families, branch interactions, route locks, crisis branches, late-game payoffs, hidden branches, anchor focus groups, and route AI. It does not need to list every focus unless the user asked for a focus-by-focus blueprint.

Good focus improvements make political choices alter industry, army, diplomacy, formables, internal factions, and expansion options. Industry supports a strategy. Expansion creates consequences. Diplomacy changes survival. Military branches solve concrete problems. Hidden branches have reveal logic and failure logic.

Do not reward every route with the same factories, equipment, stability, war support, and political power.

## Decision and mission improvement

Decision systems should ask the player to do something. A decision commits resources, risks escalation, creates a timer, changes a value, targets a state, opens a mission, or shifts a route.

A decision addendum can define pressure values, timed missions, visible objectives, target states, costs beyond political power, AI equivalents, scripted GUI buttons, dynamic localisation, cleanup, and custom tooltips.

A decision category should not become a store. If it is only a store, redesign it around the action the country is taking.

## Formable nation improvement

Formables should matter when a country earns a larger identity. They can be public, route-locked, ideology-locked, hidden, extreme-route, feature-created, leader-bound, artifact-bound, or tied to a specific prior crisis.

A formable addendum should explain the formation fantasy and the proof required. It should name the region clearly, describe required state groups or exact states when known, explain whether subjects or allies count, define the decision that forms it, and describe the cost of integration.

Formation can change tag or cosmetic tag, country name, adjective, flag, emblem, leader, party names, ideology, cores, claims, compliance, resistance, focus access, overlay routes, decisions, integration missions, faction behavior, diplomatic reactions, source-researched text or audio eligibility, and achievements

Hidden formables require more design, not less. Define how the player discovers them, what conditions reveal the decision, what routes disqualify them, what assets are needed, how AI treats them, and how post-formation gameplay avoids instant runaway power.

Do not grant every core for free unless the story and balance justify it. Prefer staged integration for large, contested, foreign, or culturally mixed formables.

## Scripted GUI and animated presentation improvement

A scripted GUI is useful when the player needs to manage a living system visually. It is not useful when a normal decision category would be clearer.

A GUI addendum should describe what the player sees, what values matter, what buttons can be clicked, what costs they use, what tooltips explain, what states or targets are locked, what warning states appear, what animation communicates, and how the UI closes or changes when the mechanic ends.

Good scripted GUI use cases include congress vote boards, patron influence networks, formable progress panels, crisis meters, corruption webs, occult pressure seals, expedition logistics boards, faction cohesion screens, target cards, and reform panels with competing factions.

Every GUI action needs script ownership. Buttons need costs, requirements, tooltips, scripted effects, scripted triggers, AI equivalents, cleanup, and validation. Animation should clarify state. A glow can show availability. A pulse can show danger. A float loop can show active power. Particles can show extreme-route corruption. Animation should not replace readable text.

Animated leader portraits should be reserved for major identity changes, extreme-route leaders, supernatural leaders, final formables, route reveals, and dramatic defeat aftermath. Define the trigger, static fallback, source mode, visual mood, frame behavior, sprite handoff, and removal or replacement condition.

## Country package improvement

A country package is weak if it only has a tag, flag, leader, and generic tree. It should have a starting problem, a political identity, a reason to survive, and a route plan.

A country addendum can define why the country exists, what states it can receive, what states are claims only, how it avoids invalid map states, starting leader, ruling party, advisors, ideas, units, technology, industry, supply, focus or overlay route, decisions, missions, survival tools, formables, claims, integration routes, diplomatic ambitions, asset needs, historical source needs, AI behavior, and cleanup.

If a shared tag can appear through more than one event, define origin logic. The same tag can use different mechanics depending on release origin, formation origin, or route origin.

## Asset and visual improvement

Visual improvement should support mechanic clarity. It should not become decoration detached from gameplay.

An asset addendum can define route-specific report images, decision icons, idea icons, focus icon families, flags, portraits, faction emblems, scripted GUI panels, animated sprites, animated portrait variants, progression states, and contact sheets.

For animated assets, define the state. The asset worker needs to know what frame set means inactive, active, dangerous, locked, completed, corrupted, hidden, or formed. The main agent needs static fallbacks and sprite names. The docs need manifest data to prove the asset was sourced or generated correctly.

Use source-based assets for real people, real flags, real symbols, and real historical images. Use generated assets for fictional, symbolic, supernatural, or impossible content. If an asset cannot be sourced or generated safely, mark it blocked instead of substituting a weak image.

## Text and audio research improvement

Sourced quote, remark, or audio research addendum should explain why the moment is larger than a normal popup. Define the role first. Examples include first reveal, faction formation, global escalation, defeat aftermath, campaign-ending threshold, hidden route reveal, final formable reveal, or regional order change.

A good quote, remark, or audio research addendum includes trigger meaning, title direction, description direction, button tone, quote direction, image direction, audio direction, docs, and alignment with any explicitly scoped external records. It should not choose a dramatic quote or image without a campaign threshold that justifies it.

Formables can deserve sourced text or audio packages when they alter a region, revive a major historical identity, complete a hidden route, or announce a new bloc. Most small formables do not need one.

## AI improvement

AI depth is part of design, not a late patch. The addendum should explain how AI chooses routes and when it refuses risky actions.

AI should consider war state, stability, war support, industry, manpower, equipment, supply, enemy strength, faction membership, ideology, route flags, threat, distance, naval access, patronage, legitimacy, and scripted values. AI should not click hidden formables or dangerous GUI buttons only because they are available.

When the player has an interface, the AI needs an equivalent action path. It can use decisions, scripted effects, timed pulses, strategy plans, or weighted events. A human-only GUI with no AI equivalent is incomplete for systems that AI countries can use.

## Subagent behavior

Use `hoi4_improvement_loop_planner` when the parent agent wants a helper to write feature expansion addenda. That planner writes design handoffs under `docs/plans/<feature_slug>/`. It should not edit gameplay files, localisation files, GUI files, scripted effects, focus trees, decisions, assets, or external records.

The planner should be deployed during implementation when a large event has gained enough new content that the design needs a second pass. It should use `hoi4-feature-planning` to expand the idea deeply, research historical and regional connections, define mechanics that the main agent can implement, and explain how the addendum should be promoted into specs if accepted.

The planner should not be deployed again for the same feature until its previous addendum has been implemented, folded into specs, queued with a reason, or rejected with a reason. Audit subagents should point to the latest unresolved addendum before asking for another planner pass.

Audit subagents should use this skill when they find shallow design. They may include a compact improvement handoff in their audit. If the gap is broad enough to require new design, they should recommend `hoi4_improvement_loop_planner` or write a bounded plan if the parent explicitly asked for that kind of audit output.

Patch-capable subagents are active by default for small, file-specific improvements inside the current task scope. Examples include varied costs, clearer dynamic localisation, safer AI weights, missing trigger tooltips, small helper calls, cleanup hooks, route-aware icon references, and obvious formable requirement fixes. They should not expand a whole mechanic through a small patch. For broad expansions, they should write a plan handoff and leave implementation to the main agent.

## Parent agent responsibility

The main agent decides what to do with the addendum. It can implement it now, queue it, reject it with a reason, or ask for a narrower pass.

Do not claim a major feature is complete while an accepted expansion addendum is unimplemented and unreported. If the addendum is queued, say where it is queued and why it was not included in the current implementation.

Accept an improvement when it makes the system more playable, reactive, readable, visually coherent, regionally specific, or integrated with mod systems. Reject it when it only adds size, noise, difficulty, darkness, or spectacle without improving play.

If the improvement loop returns a closure handoff, the main agent should finish the listed final tasks, run final validations, confirm that no accepted plan remains unresolved, and then mark the goal complete only if the completion evidence supports it.
