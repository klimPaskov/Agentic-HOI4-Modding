---
name: hoi4-feature-planning
description: Use when expanding Hearts of Iron IV mod feature ideas into detailed specifications before implementation.
---

# HOI4 Feature Planning

Use this skill to design or expand features for a Hearts of Iron IV mod.

This skill creates feature specifications. It does not implement code. Implementation belongs to the owning implementation skill for the surface being designed, such as `hoi4-events` for event content, `hoi4-focus-trees` for focus trees, `hoi4-decisions-missions` for decisions and missions, and repository-specific implementation rules for other systems. Visual asset generation and processing belongs to `hoi4-feature-assets`. Animated sprite planning, frame-sheet requirements, animated portrait packages, and animation handoff details belong to `hoi4-frame-animation` when motion is needed. Quote, remark, and audio research belongs to `hoi4-text-audio-research`.

Treat the accepted specification as the design source of truth. Plans, prompts, manifests, audits, and handoffs may refine or report it, but an accepted design change must be promoted into the relevant spec or explicitly queued/rejected with a reason. Keep implementation prompts context-complete: pass stable feature identifiers, exact spec/plan paths, file ownership, outputs, dependencies, named MCP evidence requirements, known blockers, and forbidden simplifications instead of relying on inherited chat context.

## 1. Required reading

Before writing the feature specification, use the following as the design baseline:

- `AGENTS.md`
- `hoi4-events` when the feature includes ordinary HOI4 events, news events, report events, event chains, or event-triggered content
- `hoi4-feature-assets` when the feature needs visual assets
- `hoi4-frame-animation` when the feature has animated sprites, animated UI, animated route emblems, animated portraits, warning pulses, hover loops, glow loops, float loops, particle loops, or frame-by-frame presentation needs
- `hoi4-text-audio-research` when the feature needs sourced quotes, cultural remarks, or audio research
- `hoi4-improvement-loop` before a near-completion review, and whenever the design may still be shallow, disconnected, bloated, or missing deeper playable consequences
- `hoi4-subagents` before spawning `hoi4_improvement_loop_planner` or any other project subagent
- `hoi4-focus-trees` or the current focus-tree skill when the feature needs focus trees
- `hoi4-decisions-missions` when the feature needs decisions, missions, timed objectives, influence actions, or decision-driven mechanics
- parent-provided planning rows, CSV exports, or external records when the repository includes them and the parent explicitly provides them
- provided existing feature docs
- provided mod mechanics docs

Use those sources to understand how the target repository works, then expand creatively from there.

Inspecting the repo is mandatory, but the specification should not read like a technical audit. Use repo findings to prevent mistakes and match patterns. Keep proof of inspection in the final response checklist, not in admin sections inside the spec.

## 2. Input

The user will provide either:

- a rough feature idea
- a partly developed concept
- an existing feature that needs deeper rework
- a detailed spec that needs cleanup before implementation

Treat the user idea as the starting point. Do not assume it is final.

When the idea is rough, expand it into a deeper design.

When the idea is already detailed, preserve the core direction and improve structure, clarity, missing connections, and implementation readiness.

## 3. Design purpose

The goal is to create a feature that feels like a layered mod system, not a basic popup.

The feature should have atmosphere, player choice, consequences, escalation, lore, replay value, and enough visual support to feel finished.

The design should be ambitious. Do not get lazy, conservative, or minimal unless the feature is genuinely small. Depth matters more than speed. Take the time needed to research, compare patterns, think through consequences, and design the feature as if the coding agent will implement exactly what is written.

The finished spec should make the coding agent feel that the feature has already been designed in full.

## 3.1 Idea-first specification style

The spec should focus on the feature idea, not on obvious implementation plumbing.

Do not put sections such as:

- `Scope`
- `Source baseline`
- `Repository context`
- `External tracking row`
- `Existing implementation audit`
- `Generic trigger safeguards`

The spec should be player-facing design and implementation-relevant feature design.

Avoid obvious lines such as:

- the feature only runs if enabled
- the feature should not run after a campaign-ending branch
- disabled features should not run
- the coding agent should use valid syntax
- the system should respect existing global settings

Those are baseline system responsibilities. Include technical notes only when they prevent a likely mistake, explain non-obvious behavior, or define a unique rule for this feature. Otherwise, its just noise.

Do not create negative capability notes for absent feature surfaces. If a feature does not have a campaign-ending branch, do not mention campaign-ending branches. If another surface is absent, omit that surface instead of documenting its absence. Do not write sections, bullets, feature-detail notes, parent-provided external record summaries, implementation prompts, or player-facing text that say negative absence wording such as `no special branch`, `no manual variant`, or similar. Omit the surface completely unless it actually exists or the user explicitly asks for an explanation of why it is absent.

### Tone and presentation direction standard

For every player-facing text surface, the planning spec should define the writing direction and leave finished wording to implementation. This includes feature titles and descriptions, report text, news text, focus text, decision text, option text, achievement text, text or audio research setup, GUI labels, route flavour, feature-detail text, and parent-provided external record summaries.

Give the coding agent clear direction for:

- actor or viewpoint
- force driving the feature
- information visible to the player
- information that should remain uncertain
- tone, severity, and humour mode
- references that need research
- words, frames, or clichés to avoid
- dynamic actors, states, countries, values, or routes that final text should mention

Do not provide pasteable localisation. Do not include `sample line`, `possible line`, `placeholder text`, `temporary title`, or exact draft wording that could be copied into localisation. When a structural label is needed for a file, row, route, branch, asset, or prompt, mark it as a working label, not final localisation.

Text direction should avoid bland map-summary framing and generic communications clichés. Do not make the emotional center of a feature a changed map, a line of advance, a staff-table scene, a failed broadcast, or another stock image of crisis administration.

When planning player-facing warning, threat, suspicious-report, and escalation text, do not instruct the coding agent to say that something is a warning, that something is not a warning, that a threat is coming, or that a danger signal has appeared. The text should show the pattern through partial information: fearful witnesses, rumours, anomalies, mysterious powers seen, etc

A report can make the player uneasy without naming the unease. Use mystery, information gaps, fear, rumours, etc. The player should infer that something may be wrong from the content and consequences, not from a label.

When a concept benefits from mystery, fantasy, surrealism, myth, occult signs, prophecy, impossible resolve, strange energy, or unclear public rumours, state that direction clearly without drafting the final prose.

### Feature option humour, irony, and cultural remark direction

The planning spec may define what an option should feel like, what stance it represents, and how it should vary by route or actor. It must not write final option text.

Do not let the implementation agent default to bland buttons unless plainness is intentional. Describe the intended option style, such as official denial, sarcastic acceptance, bitter understatement, cultural allusion direction, period propaganda tone, frightened understatement, arrogant boast, administrative absurdity, local proverb direction, or grim irony that condemns the speaker.

For each important option or option family, define:

- who is speaking or reacting
- what the option means mechanically and narratively
- whether the tone should be serious, ironic, sarcastic, cruel, frightened, resigned, bureaucratic, or absurd
- what kinds of cultural references may fit
- which references need research before wording is written
- how route, ideology, escalation tier, campaign state, or country culture should change the reaction

Humour should fit the stakes. Minor chaotic features can use sharper jokes and visible sarcasm. Major disasters, massacres, atrocities, mass death, and real-world suffering should use severity, official euphemism, cynical propaganda, hypocrisy, or self-damning grim irony. Cheap comedy is forbidden there.

Cultural remarks should be treated as research directions unless already sourced. The spec may say that a line should draw from a period slogan, military idiom, folk saying, religious register, old newspaper style, literary echo, propaganda formula, or local public habit. It must not invent the exact remark.

Do not list example option lines. Do not write sample buttons. Do not write placeholder localisation for options. Coding agents may paste those into the game.

Some features need one cutting reaction direction and one plain practical reaction direction. Some need several route-specific reaction directions. The spec should state the intended option tone and purpose, then leave the final wording to the coding agent.

## 3.2 Depth standard

The specification should be as deep as the feature idea deserves.

For small features, this may mean a compact but complete spec. For major features, large crises, custom UI systems, feature chains, focus trees, custom tags, or features with escalation variants, the spec should become very large and multi-part.

Do not aim for a short answer. Aim for a complete design.

For larger features, it is acceptable and expected for the finished specification to span many files and potentially reach tens of thousands or more than 100,000 lines. A huge feature with multiple countries, full focus trees, rare variants, and international-order routes can justify 100,000+ lines, and even more, across all parts if the content is meaningful. Do not shorten the spec because it becomes long.

Do not add filler to reach a size target. Add depth by thinking through the feature from every useful angle:

- player experience
- feature pacing
- escalation
- alternate paths
- rare outcomes
- decision maps
- branch maps
- AI strategy matrices
- country package matrices
- starting armies, unit templates, force-growth decisions, and dynamic military setup for newly appearing countries
- dynamic country identities, cosmetic names, flags, leaders, and politics
- AI behavior
- world reactions
- country-specific reactions
- ideological interpretations
- UI presentation
- optional feature history or logging surface presence
- assets
- text and audio packages
- achievements and difficult achievement routes
- campaign-ending branches
- linked feature group behavior
- focus trees
- clear focus-tree path maps with major routes, anchor focuses, mutual exclusions, and branch logic
- custom tags
- flag, portrait, emblem, and country-identity asset needs
- historical source needs for real flags, leaders, symbols, and portraits
- interactions with existing mod systems
- documentation needs

Every section should add usable design, player-facing detail, implementation clarity, asset direction, or system connection.

## 3.3 Research depth standard

Use research to make the feature richer. Do not rely on the first obvious idea.

When the feature has historical, cultural, scientific, political, regional, military, religious, or ideological inspiration, research enough to produce specific variants, names, factions, symbols, motives, and consequences.

Research should help answer:

- what real or plausible movements inspire the feature
- what old conflicts, myths, institutions, military traditions, or political factions can return
- what regional differences should matter
- what foreign governments would believe
- what soldiers, civilians, journalists, scientists, diplomats, or observers would think
- what rare branches can appear only in unusual campaign states
- what assets and symbols would fit each branch
- what focus tree paths each new country should have
- what starting forces and later unit-generation routes each new country should have
- what each major focus path and anchor focus should do, unlock, represent, and connect to
- what achievements would reward deep mastery, rare routes, and difficult campaign outcomes

If the topic is niche, current, uncertain, or historically specific, verify with reliable sources. Do not invent source claims. If a source-dependent point is uncertain, mark it as uncertain.

Research should not make the spec dry. Use it to create better feature content.

## 3.4 Full decision, rare variant, and branch mapping

When the feature includes decisions, rare variants, country paths, custom actors, or special outcomes, map them out fully.

Do not write vague lines such as:

- add some decisions
- add rare variants
- create several flavor events
- the country should get a focus tree
- the branch can become extreme
- some strange countries may appear

Instead, define the content. For each meaningful decision or decision group, map:

- who sees it
- when it becomes available
- what it means in the story
- what the player is choosing between
- what short-term consequence follows
- what long-term consequence it can create
- what pressures, cooldowns, costs, sacrifices, or risks it changes
- what the decision costs beyond political power or command power, such as army XP, navy XP, air XP, equipment, manpower, stability, war support, fuel, trains, convoys, supply strain, tied-down divisions, local support, faction cohesion, foreign influence debt, legitimacy, or crisis pressure
- what AI should prefer and why
- what variants or follow-up events it can unlock
- what assets, icons, or localisation it needs

For rare variants, map:

- the conditions that make them possible
- the campaign state that makes them more likely
- what the player first sees
- how observers interpret it
- what new rules or actors it adds
- what decisions, focuses, spirits, features, or text and audio packages it unlocks
- how it ends, spreads, mutates, or is contained
- what makes it different from the baseline feature

For branch trees or outcome webs, show the structure. Use headings, named routes, tables, or lists. The coding agent should not have to invent the branch map.

## 3.5 Focus tree path design standard

Read [`references/focus-tree-path-design.md`](references/focus-tree-path-design.md) whenever the specification plans national focus routes, their ideas, branch interactions, special mechanics, or faction outcomes. It contains the complete standard for this section and its subsections.

## 3.6 Focus tree visual planning standard

Focus tree visuals should help the user and implementation agent understand the intended branch structure. The spec may include a high-level branch diagram, lane map, or route sketch for major trees, but it should not try to lock every final focus coordinate unless the user explicitly asks for that.

A useful focus tree visual should show:

- major path families
- route locks
- mutually exclusive choices
- hidden or rare paths
- convergence points
- late-game route families
- which paths should be visually separate
- which paths should be placed near each other because they interact

The visual should be readable, symmetrical where possible, and free of tangled connector lines. It should not contain random crossing lines or misleading geometry.

If the spec creates a graph or diagram, it should be treated as a design guide unless the user says it must match the final in-game tree exactly. The implementation agent may adjust the final layout to make the actual HOI4 tree cleaner.

Do not spend excessive planning effort forcing exact graph coordinates if the result becomes ugly, brittle, or unhelpful. A clear path architecture is more important than a fake exact graph.

### MCP implementation handoff

When the planned feature includes a focus tree, event chain, technology or doctrine tree, weighted logic, scripted GUI, or map surface supported by `hoi4-agent-tools`, make the matching MCP pass mandatory in the implementation prompt. Require the matching read-only inspect and render evidence before source edits, compare evidence after edits, and bounded rewrite operations only where the discovered route exists. For weighted logic, require `hoi4_ai_probability_auditor` to establish named baseline scenarios, the owner to apply the bounded patch, and mandatory `hoi4.probability_analyze` with `analysis: "compare"` against the same scenarios. If any required route is unavailable, record the exact missing tool or selector and do not treat source-only review as equivalent. The normal owning skill still controls design, source review, assets, and final validation.

If the feature is a named event that specifically introduces a dedicated scripted GUI, include a bounded `hoi4_event_ui_worker` handoff in the implementation prompt. Name the event-owned GUI identifiers, files, entry point, layout regions, states, resolutions, decisions, assets, and handoff path. Require the accepted reference, native-element mapping, iterative MCP inspection/render/correction loop, and matched final comparison under `hoi4-scripted-gui`. Reviewed source edits may be applied directly or with optional rewrite. Do not route shared event logs, event-detail frameworks, settings, super-event frameworks, or unrelated existing UIs to that worker.


## 3.7 Achievement design standard

Achievements are mandatory for feature specifications unless the user explicitly says not to include them or the feature is so small that achievements would be dishonest. Major features, custom countries, deep focus trees, rare variants, international-order routes, or text and audio packages always need achievements.

Achievements should be creative and difficult. Do not design achievements that unlock just because the feature appeared, because the player clicked the obvious option, or because a country survived a few days. Achievements should reward mastery, unusual campaign states, risky choices, hidden routes, hard containment, difficult victories, or rare escalated outcomes.

A good achievement should usually require several conditions at once, such as:

- playing a specific country or route
- completing a difficult focus tree branch
- surviving a dangerous crisis state
- defeating or containing a major enemy
- avoiding an easy exploit, puppet shortcut, or foreign bailout
- triggering or suppressing a specific escalation variant track
- forming a special faction under strict conditions
- completing a rare extreme-route route
- winning while keeping a fragile coalition together
- using a special mechanic successfully without taking the safest path

Do not make achievements conservative. If the feature has dark paths, extreme-route tags, strange mechanics, foreign influence systems, coalition politics, or international-order ambitions, design achievements for them. Difficult achievements can require long campaigns, high escalation, multiple wars, internal crises, and careful decision play.

For each achievement, define:

- achievement id or working key
- title direction or working label, not final title
- player-facing description direction
- eligible starting country or countries
- exact story route or campaign situation required
- unlock conditions
- failure or disqualifying conditions
- whether it is visible, hidden, rare, or secret
- difficulty tier
- why it is interesting and not trivial
- icon direction and visual motif
- related focus paths, decisions, escalation variants, tags, factions, text and audio packages, or assets
- implementation notes for tracking if the unlock cannot be checked from a single final state

Achievement design must include asset planning. Each achievement needs a 64x64 completed icon direction, and the asset prompt must hand those icons to `hoi4-feature-assets`. Grey, locked, and not-eligible variants can be produced later if the achievement system requires them.

The achievement list should include a spread of routes. Do not put all achievements on the safest or most obvious path. Cover containment, failure recovery, republic victories, foreign influence, special factions, strange countries, extreme-route routes, and secret or hard branches when those exist.

If a feature creates many playable tags, design achievements for the most important ones and for the feature-wide systems. A large feature can justify dozens of achievements. The achievement prompt should still explain which ones are highest priority if implementation must be staged.

## 3.8 Baseline stages and escalation variants

Baseline stages and escalation variants are different.

Baseline stages describe the ordinary flow of the feature. They are the expected crisis lifecycle, such as first outbreak, containment attempt, spread, coalition formation, deep collapse, settlement, or defeat.

Escalation variants are mutation tracks layered on top of the baseline. They make the feature more predictable in some ways, more severe, stranger, more patterned, or more replayable. They can add new actors, new rules, new incidents, new tags, old movements, strange variants, stronger breakaways, or rare side branches.

Do not treat ordinary stages as special escalation variants.

Do not use escalation tiers as simple walls that lock ordinary stage progression. Ordinary stages should flow from the feature state. Escalation should affect intensity, probability, severity, weirdness, and opening strength.

### Escalation variant entry paths

When a feature has escalation variants, the spec must say how each escalation variant enters play. Do not write escalation variants only as future modifiers or only as post-fire upgrades unless that is truly the design.

Use two separate entry-path concepts when the feature supports both.

**Active feature escalation variant** means the feature is already active and an escalation variant unlocks while one or more actors from that feature still exist or the feature system is still active. The spec must define what changes immediately for the active actors: focus paths, decision families, national spirits, unit growth, targeting rules, AI strategy, faction behavior, source-researched text or audio eligibility, and cleanup. The feature should not need to activate again for the active actor to receive the escalation variant content.

**Pre-activation escalated opening** means the feature has not started yet, but the world state, escalation tier, previous escalation variant memory, or other allowed feature trigger lets the first activation start in a more escalated form. The spec must define the changed opening package: number of actors, target selection, starting ideas, initial units, first decisions, opening features, AI plan.

If both entry paths exist, write both explicitly under one escalation variant. For example, a feature may have an active escalation variant that unlocks a focus path for an already spawned country, while a later first run may start with multiple spawned countries.

If the repository uses a staged escalation model, keep stages readable and avoid stacking multiple unrelated variants behind the same threshold.

Good escalation variants can include:

- the same kind of crisis becoming easier to recognize and harder to stop
- foreign liaison networks appearing
- old historical movements returning in changed form
- new custom tags appearing that did not exist in vanilla
- extremist, occult, scientific, cultic, or ideological splinters appearing at high escalation
- strange fighter movements, partisan networks, or paramilitary identities forming
- new focus tree routes and decision categories opening

Each escalation variant should define:

- what changes from the baseline
- what conditions make it possible
- what makes it more likely
- what new player-facing content appears
- what new incidents or variants it unlocks
- what optional history or documentation title direction should represent
- how it interacts with escalation tier without being only a escalation-tier lock
- how it can be contained, spread, or escalate

## 3.9 Dynamic mechanics standard

Everything that acts like pressure, cooldown, progress, chance, support, duration, cost, tempo, AI willingness, spawn strength, aid amount, stage movement, or recognition should be dynamic by default.

Avoid fixed values as design answers. A fixed number may exist as a tuning anchor, but the spec should define the factors that shape it.

Dynamic factors can include:

- escalation tier and escalation value
- current wars
- stability and war support
- ideology and reforms
- political power, command power, army XP, navy XP, and air XP
- manpower, equipment, fuel, trains, convoys, and supply
- military losses
- supply and rail control
- distance and terrain
- local legitimacy
- foreign access
- diplomatic recognition
- previous choices
- previous the features
- escalation variant state
- crisis duration
- faction cohesion
- AI personality and strategic situation

Do not say only that a cooldown is 30 days or a pressure increase is 5. Say what makes it shorter, longer, stronger, weaker, safer, or more dangerous.

Dynamic behavior should still be readable. Define cause and effect clearly so the player can learn the pattern through features and decisions.


## 3.10 Cost and sacrifice design standard

Political power and command power are useful, but they are usually the least interesting costs. Do not let major decisions, missions, focuses, or crisis responses become a long list of political power and command power purchases.

A good cost should express what the country is actually spending, risking, or sacrificing in the story. A military crackdown may spend command power, but it should also strain units, consume equipment, lower stability, damage war support, pull divisions away from another front, increase resistance, or worsen a crisis pressure. A foreign intervention may spend political power, but it should also require relations work, liaison access, convoys, fuel, equipment shipments, intelligence exposure, or patronage risk. A mobilization decision may use manpower, infantry equipment, support equipment, training time, army XP, supply, local support, or legitimacy.

When mapping costs, use a varied cost palette where it fits the mechanic:

- army XP, navy XP, and air XP
- infantry equipment, support equipment, artillery, trucks, trains, convoys, ships, aircraft, tanks, or special equipment
- manpower, trained reserves, officer quality, or temporary unit locks
- fuel, supply capacity, rail access, port access, convoy routes, or depot control
- stability, war support, legitimacy, local support, public trust, or faction cohesion
- command power and political power only when they match the story
- construction capacity, civilian factories, military factories, dockyards, repair capacity, or production disruption
- relations, recognition pressure, foreign influence debt, intelligence exposure, or diplomatic credibility
- crisis pressure, threat-meter components, condemnation, deaths, pollution, contamination, or other repository-specific system values when relevant
- time, deadlines, objective failure risk, opportunity cost, or visible map requirements such as holding borders, guarding depots, or placing divisions in key states

Political power or command power may still be one part of a cost, but they should not be the default answer. If a section uses mostly political power or command power, redesign it unless the story clearly demands bureaucratic or command attention.

Costs should be dynamic. The amount and type of cost should react to country size, escalation tier, stability, war state, equipment stockpiles, supply state, front pressure, foreign access, local legitimacy, previous choices, AI situation, and current feature pressure. A weak country should not pay the same cost as a strong country when the story says the burden is different.

Map blocked localisation for nonstandard costs. The player should understand whether they lack infantry equipment, support equipment, divisions in the right state, local support, army XP, fuel, rail control, relations, foreign route access, or another requirement.

For every major decision family, include at least one cost or requirement that is not political power or command power unless the spec explains why that family is purely bureaucratic.

Plan at most four distinct spendable cost types per action, with non-consumed requirements identified separately. The inline native row shows at most three values and at most four ordinary words, using proper texticons and no duplicate native payment. Require the complete cost tooltip and longest available/blocked native-render checks under `hoi4-decisions-missions`.


## 3.11 AI strategy and behavior mapping standard

Major feature specs must include a real AI section. Do not leave AI behavior as a vague note that the coding agent can decide later.

The AI section should map how every important affected country behaves across the feature. This includes the feature owner, breakaways, custom tags, transformed existing tags, foreign sponsors, faction leaders, nearby countries, rivals, allies, and countries that can exploit or contain the feature.

For each important AI actor or actor group, define:

- what routes it can choose
- which routes it prefers under ordinary conditions
- which routes it only chooses under high escalation, desperation, ideology, war, foreign pressure, hidden path, or special escalation variant conditions
- what choices it should almost never make
- how it evaluates decisions, focuses, faction formation, volunteers, recognition, military action, negotiation, puppeting, annexation, and escalation
- how it reacts to dynamic pressures such as strength, stability, war state, proximity, casualties, supply, escalation tier, ideology, and previous outcomes
- how it uses or avoids rare variants and escalated tracks
- how it behaves when it is player-adjacent, major-power-adjacent, or a possible snowball threat
- what cleanup or fallback behavior it should use if its preferred route becomes impossible

For weighted behavior, give the implementation agent named scenarios and the expected ordering, timing band, dominance limit, or starvation limit to test. Route the pass through `hoi4_ai_probability_auditor`, which must establish the named baseline with `hoi4.probability_inspect`, use `hoi4.probability_inspect` for the scenario matrix and `hoi4.probability_analyze` with `analysis: "sweep"` for thresholds or rank reversals, let the owner apply a bounded patch, and run mandatory `hoi4.probability_analyze` with `analysis: "compare"` after implementation against the same scenarios. Reserve `hoi4.probability_analyze` with `analysis: "simulate"` for explicitly declared uncertain inputs and `hoi4.probability_analyze` with `analysis: "sequence"` for a complete declared custom pool with cadence and state transitions. Request `hoi4.probability_analyze` with `analysis: "render"` when a ranking, matrix, timing, sensitivity, sequence, comparison, or unresolved view will make the handoff easier to review. The auditor does not choose balance targets or patch source. If the route is unavailable, record the exact blocker and leave the result unresolved. Do not specify an exact selection probability when the candidate pool or external factors are not complete.

For focus trees, the spec must define AI path behavior at the branch level and for key individual focuses. If a large tree has mutually exclusive paths, secret routes, or dangerous extreme-route paths, specify which AI personalities or campaign states can choose them. Extreme-route AI should be allowed to make strange or extreme choices when that is the point, but ordinary AI should not accidentally choose suicidal or nonsensical branches.

For foreign influence mechanics, the AI section must explain how major powers decide whether to recognize, fund, arm, infiltrate, puppet, betray, or abandon new countries. If volunteers, expeditionary support, proxy wars, or faction invitations exist, AI behavior must be mapped for those too.

A good AI section should make the implementation agent unable to create generic AI weights while claiming to follow the spec.

## 3.12 Country package and dynamic identity standard

Read [`references/country-packages-and-formables.md`](references/country-packages-and-formables.md) whenever the specification creates or changes a country package, a dynamic identity, or a formable nation. It contains the complete standard for this section and its subsections. It also holds `Formable nations and formation routes`.

## 3.13 Starting forces and reinforcement pathway standard

Read [`references/forces-and-3d-planning.md`](references/forces-and-3d-planning.md) whenever the specification adds starting forces, reinforcements, a new unit type, or any 3D model or skeletal animation. It contains the complete standard for this section and its subsections. It also holds `3.13.1 3D model and skeletal animation planning standard`.

## 3.14 Mandatory asset coverage and source-mode standard

Everything visible or meaningful needs an asset plan. A major spec should not only define a few feature images. It should identify assets for countries, focus trees, decisions, ideas, national spirits, achievements, flags, portraits, faction emblems, text and audio packages, feature images, UI, unit systems, and route-specific identity changes.

Every focus in a mapped focus tree needs an icon direction. Large trees may use reusable icon packs, but the spec must still state which focuses use which motif or icon category. Do not leave hundreds of focuses with no asset guidance.

Every decision, decision category, idea, national spirit, achievement, faction emblem, UI panel, news image, report image, custom feature image, leader or council portrait, and important special-unit identity that appears in the feature needs an asset entry or a clear asset-family entry.

Every country package must include flags. Required flag coverage includes normal, medium, and small sizes for each implemented flag state. If the country has ideology-specific names, focus-tree transformations, puppet identities, restored historical forms, radical routes, or extreme-route mutations, the spec must identify whether those states need separate flags.

Historical and real-world flags should not be invented with the image generator by default. If a country, movement, party, military authority, or restoration path has a real historical flag or a well-attested symbolic design, the asset prompt should instruct the asset agent to source that flag or symbol from a reliable source, document it, and convert it into HOI4 flag sizes. Use the image generator only for fictional, alternate, supernatural, or deliberately invented flag identities when generated art is appropriate.

Historical or real leaders should not be generated. The spec should route every portrait to `hoi4_portrait_creator`, which sources and archives real images, records provenance and rights status, creates crops and placeholders, and processes user-supplied styled finals. For fictional leaders, council portraits, cult leaders, alternate invented officers, and symbolic committee portraits, the portrait worker invokes the image generator and completes production.

When an asset source is historically sensitive, disputed, or politically loaded, the asset prompt must require source notes, and a clear distinction between sourced historical use and fictional alternate-history invention.


## 3.15 Effect strength and impact standard

Do not design important feature effects with timid, decorative, or micro values. If an idea, decision, focus, mission, national spirit, crisis response, starting debuff, or route payoff is supposed to matter, its effects must be strong enough for the player to feel and plan around.

Micro modifiers do not count as meaningful design. Avoid values such as plus 2 percent, minus 3 percent, or tiny flat changes as the main reward, penalty, starting debuff, crisis modifier, or route payoff. A small modifier can support a larger effect package only when it belongs to a visible stacking system, a frequent tick, or a clearly explained cumulative mechanic. It cannot be the whole design.

Starting negative debuffs must matter. They should create real pressure on survival, production, mobilisation, logistics, legitimacy, command, diplomacy, state control, AI behavior, or player priorities. A starting problem that the player can ignore has failed. The spec should map how the player feels the debuff, why it exists, which choices mitigate it, and what happens if it is left unresolved.

A good effect package should do at least one meaningful thing:

- change player incentives
- unlock a new decision, mission, focus branch, unit type, mechanic, or route
- move a crisis, loyalty, legitimacy, recognition, stability, or threat value in a visible way
- create a real cost, risk, or tradeoff
- apply a strong positive or negative modifier that changes army, economy, diplomacy, internal politics, logistics, production, intelligence, state control, or AI behavior in a visible way
- create an urgent weakness, route identity, or route payoff the player cannot ignore
- change how a country plays for a meaningful period
- connect to later features, escalation variants, achievements, or text and audio packages

Effects should fit the feature story. A desperate military measure should affect units, equipment, losses, command, supply, stability, or war support. A logistical crisis should interact with trains, fuel, depots, supply, equipment, routes, or tied-down units. A legitimacy crisis should affect stability, war support, recognition, internal factions, local support, or authority. A foreign intervention system should create influence, dependence, access, backlash, or diplomatic consequences.

Normal countries still need balance, but balance must come from costs, timing, risks, limits, tradeoffs, counterplay, AI validity, and route locks. Do not create fake balance by making the numbers too small to matter.

Special feature-created countries are different. They do not have to be balanced against ordinary countries. If a special feature-created country finishes its path, final route, extreme-route transformation, or full mechanic loop, the payoff must be absurd, dangerous, and visibly overpowered when the concept supports it. A completed special feature-created country can receive extreme buffs, extreme penalties to enemies, impossible-seeming armies, unnatural production, severe combat bonuses, global pressure, map-changing powers, or other absurd effects if the route earned them.

The spec should still prevent accidental exploits for ordinary countries, repeated free rewards, and unintended cross-route stacking. It should not weaken a completed special feature-created country into ordinary balance values. The absurdity must be intentional, visible, and connected to the feature identity.

The spec should explain why a value is strong, weak, temporary, risky, conditional, escalating, or deliberately absurd. Reject effect plans whose main outcomes are tiny percentage modifiers, flavour-only ideas, harmless starting debuffs, invisible penalties, or rewards that the player would not notice during normal play.

## 4. What the specification should explore

A strong specification usually explores:

- the core feature concept
- why the feature matters
- how the feature first appears
- what the player sees and chooses
- what tone the feature options use, including irony, sarcasm, cultural remarks, humour, or plain severity where appropriate
- what consequences follow
- how the situation can escalate
- what rare variants can happen
- how AI countries react and choose routes
- how the feature changes under different world conditions
- what decisions exist and how they interlock
- whether the feature should create focus tree content
- whether the feature should create new tags or transform existing countries
- what starting units and reinforcement routes new countries receive
- how each new or transformed country changes names, flags, leaders, ideologies, parties, and politics
- whether the feature needs sourced quotes, cultural remarks, or audio
- what achievements should exist and why they are difficult
- what UI or visual presentation would make it stronger
- what other mod systems it should interact with
- what assets the feature needs, including all route-specific country assets
- what historical flags, symbols, and portraits must be sourced rather than generated
- what the coding agent needs to know before implementation

When exploring these areas, do not stop at the first obvious answer. Consider multiple versions and choose or describe the strongest ones.

For important features, think through edge cases, country differences, country package completeness, player incentives, AI incentives, abuse risks, pacing, cooldown factors, narrative tone, repeat play, and escalated behavior.

## 5. Mod system awareness

Consider links to existing mod systems when they strengthen the feature. Do not copy a system from another repository just because the source package had one.

Possible generic links include:

- escalation values or pressure meters that already exist in the target repository
- optional feature history or logging surfaces that already exist in the target repository
- text and audio packages
- decisions, missions, focus trees, country packages, scripted GUI, achievements, and formables
- diplomacy, war, ideology, casualties, public panic, contamination, legitimacy, recognition, or other mechanics that the target repository already supports
- existing or planned features in the same mod

Leave out connections that feel artificial. Optional registry hooks, debug menus, parent-provided tracking records, and custom UI surfaces should be used only when the target repository actually has them.


## 6. Escalation and uncertainty

Dangerous systems should not reveal themselves too early.

Player-facing escalation text must not label itself as a warning, a non-warning, a threat, a danger signal, or a campaign-ending risk. Do not tell the coding agent to write text that announces what the player is supposed to infer. Do not frame a feature-detail entry, report, news item, tooltip, decision category, focus description, quote, remark, image, or audio direction, or external record summary around that direct label.

Use mysterious information, fear, and uncertainty instead. Early information should feel incomplete because people cannot yet explain what is happening.

Do not build mystery from bureaucratic document motifs, archive-style secrecy, diplomatic evasions, or paperwork drama. Avoid staged contrast formulas that make tension from one side saying or seeing something while an official body denies, delays, softens, avoids, or reacts to it. Avoid timing formulas that make one observation happen before an official admission, public reaction, government response, or wider consequence. Describe the observed fear and uncertainty directly.

The player should understand deeper danger through patterns and consequences over time. It should not explain that the content is a warning or reassure the player that it is not one.

## 7. Depth and hidden connections

Look for design connections the user may not have considered.

Useful connection types can include:

- callbacks to existing features
- links to planned features
- rare unlock conditions
- alternate branches
- campaign-state dependent outcomes
- ideological interpretations
- historical parallels
- secret projects
- military exploitation
- propaganda themes
- myths or rumours
- diplomatic consequences
- internal faction disputes
- scientific uncertainty
- black market effects
- civilian behaviour
- regional differences
- long-term instability
- old movements returning under new conditions
- custom countries that only make sense in specific campaign states

Add these when they make the feature stronger.

## 8. Custom UI and presentation

If the feature benefits from custom UI, design one.

Describe what the player sees, how it changes, and what visual assets are needed.

Map the UI states if the UI represents pressure, route choice, threat, stage, faction cohesion, recognition, contamination, loyalty, or any other living value.

## Interactive mechanic UI and animated presentation in feature specs

Read [`references/presentation-and-research-planning.md`](references/presentation-and-research-planning.md) whenever the specification plans an interactive mechanic UI, animated presentation, or quote, remark, and audio research. It contains the complete standard for this section and its subsections.

## 9. Quote, remark, and audio research planning

Read [`references/presentation-and-research-planning.md`](references/presentation-and-research-planning.md) whenever the specification plans an interactive mechanic UI, animated presentation, or quote, remark, and audio research. It contains the complete standard for this section and its subsections.

## 10. Writing style

Read [`references/writing-style.md`](references/writing-style.md) before writing tone, options, localisation handoffs, or any player-facing text in a specification. It contains the complete standard for this section and its subsections.

## 11. Specification shape

Do not force the specification into a fixed template.

Choose the structure that best fits the feature idea.

The specification should still be easy for a coding agent to use. Use clear headings, explain the logic in a natural order, and make sure important design decisions are not buried.

For major features, split the spec into parts if needed. Do not compress deep design just to fit one file.

Only include sections for surfaces that exist or that need design. If a researched text package, custom presentation surface, focus tree, custom country, achievement set, asset family, or other major surface is absent, omit that section instead of writing that it is absent. Because negative notes create noise and can mislead later agents into thinking the absence is a designed feature.

## 12. Depth, file splitting, and internal resume notes

Read [`references/specification-delivery.md`](references/specification-delivery.md) when shaping, splitting, or resuming a long specification, or writing an improvement-loop expansion spec. It contains the complete standard for this section and its subsections.

## 13. Asset planning

Read [`references/asset-and-research-handoffs.md`](references/asset-and-research-handoffs.md) whenever the specification plans assets, writes asset prompts, or hands off text and audio research. It contains the complete standard for this section and its subsections. It also holds `14. Asset prompt handoff`, `15. HOI4 asset size reference`, `16. Asset style reference`, `17. Text and audio research handoff`.

## Improvement-loop expansion specs

Read [`references/specification-delivery.md`](references/specification-delivery.md) when shaping, splitting, or resuming a long specification, or writing an improvement-loop expansion spec. It contains the complete standard for this section and its subsections.

## General localisation handoff

When a spec includes text-bearing content, give a localisation handoff, not final copy.

The handoff should list each needed text surface and describe its direction:

- feature title direction
- feature description direction
- option reaction direction
- news or report direction
- decision name and description direction
- focus name and description direction
- achievement title and description direction
- GUI label direction
- feature-detail and feature-log wording direction
- dynamic placeholders the coding agent should use
- research gates for quotes, slogans, songs, films, books, speeches, scriptures, proverbs, or other source-dependent references

The coding agent writes the final in-game text during implementation. The planning spec should not provide final prose for the coding agent to paste.

The planning agent should preserve the open structure of the addendum where that helps the idea. Use tables, route maps, prose, diagrams, or country package matrices only when they make the design easier to implement. Do not convert every improvement into a rigid checklist.

When an improvement addendum proposes formables, scripted GUI, animated sprites, animated portraits, or hidden routes, the final spec pack should carry those ideas into the relevant files instead of leaving them isolated. The core spec explains why the expansion matters. The decision and focus files explain how the player reaches it. The asset prompt explains the static and animated visual work. The coding prompt and goal prompt tell the implementation agent to wire and validate it.


## Specification folder convention

From now on, source specifications should live in feature-specific subfolders under `docs/specs/`.

Use this shape:

```text
docs/specs/<feature_slug>/
```

Examples:

```text
docs/specs/<feature_slug>/<feature_slug>_spec.md
docs/specs/<feature_slug>/<feature_slug>_focus_trees.md
docs/specs/<feature_slug>/<feature_slug>_country_packages.md
```

Use `docs/plans/<feature_slug>/` for subagent plans, improvement addenda, audit follow-up notes, blocked reports, and implementation handoffs. Plans can become source design later, but the main agent should promote or merge them into `docs/specs/` when they are accepted as part of the final feature design.

## 18. Output rules

The feature specification itself should be created as Markdown files.

Full feature or feature specification output belongs under `docs/specs/<feature_slug>/`. This is the source-of-truth design folder for the feature spec pack.

Subagent planning addenda, audit follow-up plans, implementation notes, and temporary handoffs belong under `docs/plans/<feature_slug>/`. The plans folder is a working area. Accepted plan content should be folded into the relevant spec under `docs/specs/` when the final source-of-truth spec is updated.

Do not create new feature specs, addenda, prompt packages, or extracted handoffs under `docs/planning/`, `planning/`, or any other planning folder. If a prompt says "planning folder", interpret that as `docs/plans/` for subagent plans and `docs/specs/` for source specs unless the user explicitly provides a different path.

The spec file should contain only the feature specification.

Do not put the asset prompt, text and audio research prompt, coding-agent prompt, or goal prompt inside the spec file.

Keep planning files readable as design handoffs, not implementation blueprints. Prefer route purpose, player-facing behavior, balance intent, asset direction, AI intent, and acceptance criteria. Avoid long technical tables, exact constant lists, full scripted-effect recipes, exhaustive file inventories, parser-level implementation notes, and detailed code wiring. The specs you create are not implementation oriented. You do not give implementation guidance, you are just handing off ideas.

Create sequential files:

- `<feature_slug>_spec_part_1_core.md`
- `<feature_slug>_spec_part_2_<theme>.md`
- `<feature_slug>_spec_part_3_<theme>.md`
- and more as needed

Do not repeat earlier sections unless needed for clarity.


## 18.1 Final zip package requirement

The final output should be delivered as one zip file that contains every necessary file for the planning handoff.

The zip should include, when relevant:

- all spec Markdown files
- focus-tree path spec parts
- optional focus tree path diagrams or route sketches when useful
- asset prompt file
- text and audio research prompt file
- achievement prompt file
- coding-agent prompt file
- goal prompt file
- research notes or bibliography files
- any country package matrices, AI matrices, decision maps, or acceptance criteria files created separately

Do not make the user collect many loose files manually. The main deliverable should be a single zip package.

Use a clear package name such as:

`feature_slug_planning_package.zip`

The package should have a clean internal structure, for example:

```text
specs/
prompts/
focus_graphs/
research/
matrices/
```

The goal prompt inside the package must still be 3500-4000 characters.
The extracted zip should be placed in `docs/specs/<feature_slug>/` when it is the source spec pack. If the zip contains only subagent plans, follow-up handoffs, or audits, place it under `docs/plans/<feature_slug>/`.

## 19. Final prompt files

Read [`references/final-handoff-and-quality-gate.md`](references/final-handoff-and-quality-gate.md) before writing the final prompt files and before the final response of every planning pass. It contains the complete standard for this section and its subsections. It also holds `Formation and UI questions for planning passes`, `20. Final response checklist`, `21. Cleanup and quality gate`.

<!-- HOI4_MOD_SETUP_SUPER_EVENTS_START -->
## Super Events planning

When the installed `hoi4-super-events` workflow is selected, use it only for a campaign-scale first reveal, irreversible escalation, world-order change, rare ideological victory, catastrophic collapse, global defeat, or genuine ending. The plan must name the owning caller, the state established before presentation, one stable registration ID, duplicate-suppression and close-cleanup behavior, title and description direction, quote and response themes, image direction and source mode, audio decision, runtime touchpoints, permanent documentation, and one acceptance scenario.

Treat title, response, quote, cultural reference, image, and audio choices as research briefs rather than invented final assets. Audio is optional unless the user, accepted specification, or verified project convention explicitly makes it required. Route implementation through `hoi4-events`, visual work through `hoi4-feature-assets`, sourced wording and audio through `hoi4-text-audio-research`, and the complete presentation contract through `hoi4-super-events`.
<!-- HOI4_MOD_SETUP_SUPER_EVENTS_END -->
