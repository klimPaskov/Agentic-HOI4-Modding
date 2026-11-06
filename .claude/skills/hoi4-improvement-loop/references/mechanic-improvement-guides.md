# HOI4 Improvement Loop: Improving features, focus trees, decisions, formables, countries and AI

Part of the [hoi4-improvement-loop](../SKILL.md) skill. Read when the addendum touches a feature chain, focus tree, decision or mission system, formable, country package or AI behavior.

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

## Country package improvement

A country package is weak if it only has a tag, flag, leader, and generic tree. It should have a starting problem, a political identity, a reason to survive, and a route plan.

A country addendum can define why the country exists, what states it can receive, what states are claims only, how it avoids invalid map states, starting leader, ruling party, advisors, ideas, units, technology, industry, supply, focus or overlay route, decisions, missions, survival tools, formables, claims, integration routes, diplomatic ambitions, asset needs, historical source needs, AI behavior, and cleanup.

If the improvement changes a technology or doctrine tree, require `hoi4.tech_inspect` evidence for prerequisites, placement, exclusivity, unlocks, grants, bonuses, references, and missing assets; use `hoi4.tech_render` for the affected folder or branch and `hoi4.tech_inspect` with `mode: "compare"` for the implemented change.

If a shared tag can appear through more than one event, define origin logic. The same tag can use different mechanics depending on release origin, formation origin, or route origin.

## AI improvement

AI depth is part of design, not a late patch. The addendum should explain how AI chooses routes and when it refuses risky actions.

AI should consider war state, stability, war support, industry, manpower, equipment, supply, enemy strength, faction membership, ideology, route flags, threat, distance, naval access, patronage, legitimacy, and scripted values. AI should not click hidden formables or dangerous GUI buttons only because they are available.

When the player has an interface, the AI needs an equivalent action path. It can use decisions, scripted effects, timed pulses, strategy plans, or weighted events. A human-only GUI with no AI equivalent is incomplete for systems that AI countries can use.

