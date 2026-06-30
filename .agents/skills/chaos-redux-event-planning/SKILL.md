---
name: chaos-redux-event-planning
description: Use when expanding Chaos Redux event ideas into detailed specifications before implementation.
---

# Chaos Redux Event Planning

Use this skill to design or expand events for the Hearts of Iron IV mod Chaos Redux (https://github.com/klimPaskov/Chaos-Redux).

This skill creates event specifications. It does not implement code. Implementation belongs to `chaos-redux-events`. Visual asset generation and processing belongs to `chaos-redux-event-assets`. Animated sprite planning, frame-sheet requirements, animated portrait packages, and animation handoff details belong to `chaos-redux-frame-animation` when motion is needed. Super-event quote, remark, music, and presentation research belongs to `chaos-redux-super-events`.

## 1. Required reading

Before writing the event specification, use the following as the design baseline:

- `AGENTS.md`
- `chaos-redux-events`
- `chaos-redux-event-assets` when the event needs visual assets
- `chaos-redux-frame-animation` when the event has animated sprites, animated UI, animated route emblems, animated portraits, warning pulses, hover loops, glow loops, float loops, particle loops, or frame-by-frame presentation needs
- `chaos-redux-super-events` when the event needs a super-event
- `hoi4-focus-trees` or the current focus-tree skill when the event needs focus trees
- `hoi4-decisions-missions` when the event needs decisions, missions, timed objectives, influence actions, or decision-driven mechanics
- provided event spreadsheet rows
- provided existing event docs
- provided Chaos Redux mechanics docs

Use those sources to understand how Chaos Redux already works, then expand creatively from there.

Inspecting the repo is mandatory, but the specification should not read like a technical audit. Use repo findings to prevent mistakes and match patterns. Keep proof of inspection in the final response checklist, not in admin sections inside the spec.

## 2. Input

The user will provide either:

- a rough event idea
- a partly developed concept
- an existing event that needs deeper rework
- a detailed spec that needs cleanup before implementation

Treat the user idea as the starting point. Do not assume it is final.

When the idea is rough, expand it into a deeper design.

When the idea is already detailed, preserve the core direction and improve structure, clarity, missing connections, and implementation readiness.

## 3. Design purpose

The goal is to create an event that feels like a layered Chaos Redux system, not a basic popup.

The event should have atmosphere, player choice, consequences, escalation, lore, replay value, and enough visual support to feel finished.

The design should be ambitious. Do not get lazy, conservative, or minimal unless the event is genuinely small. Depth matters more than speed. Take the time needed to research, compare patterns, think through consequences, and design the event as if the coding agent will implement exactly what is written.

The finished spec should make the coding agent feel that the event has already been designed in full.

## 3.1 Idea-first specification style

The spec should focus on the event idea, not on obvious implementation plumbing.

Do not put sections such as:

- `Scope`
- `Source baseline`
- `Repository context`
- `Spreadsheet row`
- `Existing implementation audit`
- `Generic trigger safeguards`

The final response may mention that the repo and spreadsheet were inspected. The spec should be player-facing design and implementation-relevant event design.

Avoid obvious lines such as:

- the event only fires if enabled
- the event should not fire after a world-end scenario
- disabled events should not fire
- the coding agent should use valid syntax
- the system should respect existing global settings

Those are baseline system responsibilities. Include technical notes only when they prevent a likely mistake, explain non-obvious behavior, or define a unique rule for this event. Otherwise, its just noise.

Do not create negative capability notes for absent event surfaces. If an event does not have a world-end scenario, do not mention world-end scenarios. If an event does not have a manual triggerable scenario, do not mention triggerable scenarios. Do not write sections, bullets, event-detail notes, spreadsheet-facing summaries, implementation prompts, or player-facing text that say `no world-end scenario`, `does not have a world-end scenario`, `no manual triggerable scenario`, `does not have a triggerable scenario`, or similar absence wording. Omit the surface completely unless it actually exists or the user explicitly asks for an explanation of why it is absent.

### Tone and presentation direction standard

For every player-facing text surface, the planning spec should define the writing direction and leave finished wording to implementation. This includes event titles, event descriptions, report text, news text, focus text, decision text, option text, achievement text, super-event setup, GUI labels, route flavour, event-detail text, and spreadsheet-facing summaries.

Give the coding agent clear direction for:

- actor or viewpoint
- force driving the event
- information visible to the player
- information that should remain uncertain
- tone, severity, and humour mode
- references that need research
- words, frames, or clichés to avoid
- dynamic actors, states, countries, values, or routes that final text should mention

Do not provide pasteable localisation. Do not include `sample line`, `possible line`, `placeholder text`, `temporary title`, or exact draft wording that could be copied into localisation. When a structural label is needed for a file, row, route, branch, asset, or prompt, mark it as a working label, not final localisation.

Text direction should avoid bland map-summary framing and generic communications clichés. Do not make the emotional center of an event a changed map, a line of advance, a staff-table scene, a failed broadcast, or another stock image of crisis administration.

When planning player-facing warning, threat, suspicious-report, and escalation text, do not instruct the coding agent to say that something is a warning, that something is not a warning, that a threat is coming, or that a danger signal has appeared. The text should show the pattern through partial information: fearful witnesses, rumours, anomalies, mysterious powers seen, etc

A report can make the player uneasy without naming the unease. Use mystery, information gaps, fear, institutional caution, rumours, and uncertain public interpretation. The player should infer that something may be wrong from the content and consequences, not from a label.

When a concept benefits from mystery, fantasy, surrealism, myth, occult signs, prophecy, impossible resolve, strange energy, or unclear public rumours, state that direction clearly without drafting the final prose.

### Event option humour, irony, and cultural remark direction

The planning spec may define what an option should feel like, what stance it represents, and how it should vary by route or actor. It must not write final option text.

Do not let the implementation agent default to bland buttons unless plainness is intentional. Describe the intended option style, such as official denial, sarcastic acceptance, bitter understatement, cultural allusion direction, period propaganda tone, frightened understatement, arrogant boast, administrative absurdity, local proverb direction, or grim irony that condemns the speaker.

For each important option or option family, define:

- who is speaking or reacting
- what the option means mechanically and narratively
- whether the tone should be serious, ironic, sarcastic, cruel, frightened, resigned, bureaucratic, or absurd
- what kinds of cultural references may fit
- which references need research before wording is written
- which jokes are forbidden because the subject is too severe
- how route, ideology, chaos tier, campaign state, or country culture should change the reaction

Humour should fit the stakes. Minor chaotic events can use sharper jokes and visible sarcasm. Major disasters, massacres, atrocities, mass death, and real-world suffering should use severity, official euphemism, cynical propaganda, hypocrisy, or self-damning grim irony. Cheap comedy is forbidden there.

Cultural remarks should be treated as research directions unless already sourced. The spec may say that a line should draw from a period slogan, military idiom, folk saying, religious register, old newspaper style, literary echo, propaganda formula, or local public habit. It must not invent the exact remark.

Do not list example option lines. Do not write sample buttons. Do not write placeholder localisation for options. Coding agents may paste those into the game.

Some events need one cutting reaction direction and one plain practical reaction direction. Some need several route-specific reaction directions. Some need no joke because a quiet response fits better. The spec should state the intended option tone and purpose, then leave the final wording to the coding agent.

## 3.2 Depth standard

The specification should be as deep as the event idea deserves.

For small events, this may mean a compact but complete spec. For major events, world crises, custom UI systems, event chains, focus trees, custom tags, or events with evolutions, the spec should become very large and multi-part.

Do not aim for a short answer. Aim for a complete design.

For larger events, it is acceptable and expected for the finished specification to span many files and potentially reach tens of thousands or more than 100,000 lines. A huge event with multiple countries, full focus trees, rare variants, and world-order routes can justify 100,000+ lines, and even more, across all parts if the content is meaningful. Do not shorten the spec because it becomes long.

Do not add filler to reach a size target. Add depth by thinking through the event from every useful angle:

- player experience
- event pacing
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
- event log presence
- assets
- super-events
- achievements and difficult achievement routes
- world-end branches
- event cluster behavior
- focus trees
- clear focus-tree path maps with major routes, anchor focuses, mutual exclusions, and branch logic
- custom tags
- flag, portrait, emblem, and country-identity asset needs
- historical source needs for real flags, leaders, symbols, and portraits
- interactions with existing Chaos Redux systems
- documentation needs

Every section should add usable design, player-facing detail, implementation clarity, asset direction, or system connection.

## 3.3 Research depth standard

Use research to make the event richer. Do not rely on the first obvious idea.

When the event has historical, cultural, scientific, political, regional, military, religious, or ideological inspiration, research enough to produce specific variants, names, factions, symbols, motives, and consequences.

Research should help answer:

- what real or plausible movements inspire the event
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

Research should not make the spec dry. Use it to create better event content.

## 3.4 Full decision, rare variant, and branch mapping

When the event includes decisions, rare variants, country paths, custom actors, or special outcomes, map them out fully.

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
- what decisions, focuses, spirits, events, or super-events it unlocks
- how it ends, spreads, mutates, or is contained
- what makes it different from the baseline event

For branch trees or outcome webs, show the structure. Use headings, named routes, tables, or lists. The coding agent should not have to invent the branch map.

## 3.5 Focus tree path design standard

Focus trees must be planned clearly, but the event-planning spec should not try to micromanage every final focus node, every coordinate, or every exact connection. The spec writer should define the tree's routes, branch architecture, major choices, mutual exclusions, story logic, mechanics, rewards, and design standards. The implementation agent should then create the final in-game focus tree layout and exact focus connections cleanly.

A good focus-tree spec should answer:

- what major paths the country has
- what each path means in the story
- what each path changes mechanically
- which paths are mutually exclusive
- which paths can cooperate or converge
- which paths are hidden, rare, chaos-locked, evolution-locked, foreign-aid-locked, or crisis-locked, etc
- what kinds of focuses belong in each path
- what kinds of rewards each path uses
- what decisions, missions, units, ideas, leaders, flags, claims, buildings, factions, or events each path should unlock
- what starting weaknesses the tree lets the country solve
- what late-game ambitions each route can reach
- how AI should choose between the routes

Do not write only vague branch names. A focus-tree plan must still be detailed enough to prevent generic or boring implementation. The spec should describe the internal logic of each path, the rough order of ideas inside it, its major focus groups, its expected route locks, and its major payoff. It should also name important focuses or focus groups where the story requires them.

Do not require a literal list of every focus unless the user specifically asks for a focus-by-focus blueprint. The default planning style should be path-level and branch-level design. It is acceptable to provide non-final focus-role labels or important anchor focus groups.

### Focus tree architecture map

Every major focus tree still needs an architecture map. The architecture map should show the intended path structure, not every final focus.

The map should include:

- opening situation and early survival choices
- main political routes
- industry and economy branches
- military branches
- diplomacy and faction branches
- expansion or reunification branches
- internal faction or balance-of-power branches
- hidden, rare, crisis, evolution, and high-chaos branches where relevant
- late-game ambition routes
- mutually exclusive route families
- paths that can converge later
- paths that require foreign aid, high threat, chaos, war, a specific evolution, or prior choices

Use a readable structure such as a table, bullet tree, route diagram, or lane map. The implementation agent should understand the intended tree shape and design, but does not need exact focus coordinates from the spec unless the user asks for them.

### Branch and path detail

For each major path, define:

- path name or working route label
- narrative role
- mechanical role
- unlock conditions
- mutually exclusive paths
- compatible paths
- rough focus groups inside the path
- key anchor focuses when needed
- major decisions, missions, ideas, units, leaders, advisors, advisor discounts, flags, country names, party changes, claims, cores, war goals, buildings, leagues, or events unlocked
- reward style and what should be avoided
- AI behavior
- late-game outcome or failure state

For each important anchor focus or focus group, define:

- rough purpose
- what it connects to
- whether it is a route opener, route lock, side branch, convergence point, hidden branch, crisis branch, or finisher
- what it unlocks or changes
- what kind of reward it should use
- what idea, decision, mission, unit, building, leader, flag, or event it affects
- what should be mutually exclusive with it, if anything

The coding agent may create more or fewer individual focuses than the spec examples as long as the final tree preserves the path design, story logic, route choices, and gameplay depth.

### Focus reward diversity standard

Focus rewards must be varied. Do not design focus trees where most focuses add a new national spirit, add political power, add stability, add war support, or repeat the same modifier pattern.

A new national spirit or idea should be used only when the focus creates a persistent institution, doctrine, crisis condition, political identity, military structure, economic system, or long-term route effect. If the branch already has an idea representing that institution, prefer modifying, upgrading, replacing, temporarily strengthening, or adding a timed modifier to the existing idea instead of creating another separate idea.

Good focus reward types include:

- civilian factories
- military factories
- dockyards
- forts
- coastal forts
- anti-air buildings
- radar stations
- airbases
- infrastructure
- railways
- supply hubs
- resources
- building slots
- production lines
- equipment stockpiles
- unit templates
- route-specific spawned units
- commanders or advisors
- decisions
- timed missions or objective families
- laws
- technologies or research bonuses
- claims or cores
- leader changes
- ruling party changes
- cosmetic names
- flag changes
- faction mechanics
- diplomacy routes
- foreign aid systems
- crisis value changes
- objective completion bonuses
- events or event chains

Every focus path should have a distinct purpose. If two focus groups would grant nearly the same effect, merge them, rewrite one, or make one an upgrade of the other.

Reject focus trees where most focus groups grant new ideas without a clear reason. A tree that uses repeated new ideas as filler has failed even if it has many focuses.

### Dynamic idea lifecycle standard

New countries, transformed countries, civil-war splinters, emergency governments, and unstable successor states should not start with a long stack of generic positive ideas. It is usually better for them to start with a small number of deep, readable ideas that define their starting weakness, identity, and strategic problems.

Starting ideas can be negative, mixed, unstable, or conditional. These ideas should represent real problems the country must solve, such as broken administration, improvised command, disputed legitimacy, militia fragmentation, supply confusion, foreign dependence, refugee pressure, factional mistrust, ruined industry, contested railways, disorganized officers, or unclear laws.

Negative starting ideas should not be permanent dead weight unless the story requires that. The spec should map how decisions, missions, focuses, leader choices, foreign aid, victories, reforms, purges, compromises, or crisis outcomes can mitigate, transform, upgrade, or remove them.

Prefer fewer ideas with more depth over many shallow ideas. A good idea can have a lifecycle:

- starting negative or mixed form
- mitigated form after early stabilization
- reformed form after a political or institutional branch
- positive route-specific form after the country commits to a path
- corrupted, radicalized, or dangerous form after a high-chaos or failure route

When designing focus trees, do not create a new idea in every focus. If an institution already exists as an idea, prefer changing that existing idea through staged upgrades, replacing it with a route-specific version, adding a temporary modifier, unlocking decisions tied to it, or changing how it interacts with missions and crisis values.

For every important idea, define:

- why the country starts with it or unlocks it
- whether it is negative, mixed, positive, temporary, staged, or route-specific
- what decisions, focuses, missions, events, or outcomes change it
- what its upgraded or mitigated forms are called
- what route can remove it completely
- whether it can become worse through failure, high chaos, foreign dependence, civil war, or bad decisions
- what icon direction it needs
- how AI should prioritize solving or exploiting it

Every major country package should include a starting idea plan and an idea lifecycle table. The table should show which ideas exist at start, which are unlocked later, which are upgraded, which are removed, and which are route-specific.

Example table:

| Idea | Start or unlock | Starting role | Mitigation path | Upgrade path | Failure path | Final forms |
| --- | --- | --- | --- | --- | --- | --- |

Reject specs where a country starts with too many unrelated ideas, where every focus creates a separate idea, or where negative ideas cannot be meaningfully addressed through play.


### Focus, politics, expansion, and decision integration

When planning a major focus tree, define more than politics and industry. A large tree needs a distinct expansion, reunification, liberation, settlement, or regional ambition branch. This branch should be separate from the main political tree and separate from the industry tree.

Expansion branches should define real strategic effects, such as claims, cores, war goals, protectorates, guarantees, declarations, leagues, border settlements, ultimatum decisions, or postwar integration choices. Do not reduce expansion to generic bonuses.

Political branches should change politics directly. Define ideology paths, ruling party shifts, party popularity changes, leader changes, advisor unlocks, advisor discounts, laws, councils, juntas, congresses, committees, faction struggles, cosmetic names, and flag changes where they fit. Leader changes imply portrait needs. Real leaders need sourced portraits. Fictional leaders and symbolic councils can use generated portraits through the asset skill.

Fixed-purpose chaos countries can have narrower politics when their identity demands it. A death-state, plague-state, machine-state, or pure destruction actor may have one ideological purpose. Even then, the tree should still provide meaningful internal choices inside that purpose, such as doctrine, expansion method, recruitment, economy, hierarchy, or endgame ambition.

Focus trees and decision systems must be planned together. Focuses should unlock or change decisions and missions. Industry focuses can unlock construction decisions. Military focuses can unlock unit, depot, border, or offensive missions. Diplomacy focuses can unlock recognition, aid, volunteer, and influence decisions. Expansion focuses can unlock declarations, league votes, protectorate demands, border incidents, claims, cores, war goals, and settlement decisions.

For each major focus path, describe which decision or mission families it unlocks and how those decisions expand the mechanic.


### Branch interaction, payoff, and country identity

Political, industry, and expansion are the minimum branch families, not the full design for important countries. Important countries should usually also define military, diplomacy, internal faction, intelligence or security, special mechanic, and late-game branches when their identity supports them.

Branches should not be isolated columns. Political choices should change which expansion, industry, military, diplomacy, and decision paths are available. Industry should support military or expansion. Expansion should create political consequences. Diplomacy should affect foreign aid, war options, faction choices, and sponsor risk.

Every major branch needs a clear payoff. A political branch can end in a new government, leader, ideology, law system, ruling party, or country identity. An industry branch can end in a rebuilt economy, arsenal, resource system, railway authority, construction mechanic, or production network. An expansion branch can end in a league, empire, federation, protectorate network, reunification, liberation order, regional settlement, or external war plan.

A good focus path should unlock new gameplay, not only stats. The plan should describe decisions, missions, units, advisors, leaders, laws, claims, cores, war goals, buildings, events, mechanics, route access, and AI behavior where they fit. Flat modifiers are supporting rewards, not the main design.

Political routes should update the visible country package where relevant: leader, leader portrait, advisor roster, high command, ruling party, party names, ideology drift or swap, cosmetic name, flag, ideas, and AI strategy. Leader changes imply portrait needs.

Expansion branches should create consequences. Claims, cores, and war goals should interact with diplomacy, factions, resistance, foreign guarantees, local leagues, legitimacy, threat, or postwar settlement decisions.

Industry branches should create map or production changes. Define factories, infrastructure, railways, supply hubs, forts, anti-air, airbases, dockyards, resources, production lines, or construction decisions.

Decision categories should evolve with focus progress. Early focuses may unlock basic decisions. Later focuses should add new targets, stronger actions, cheaper costs, new risks, or new mission families. A decision category should feel different after a route develops.

The fixed-purpose exception is narrow. A country is fixed-purpose only when its concept clearly cannot support normal politics, such as a death-state, machine-state, plague-state, or pure destruction actor. It still needs meaningful internal branches around method, hierarchy, economy, recruitment, expansion, and endgame.


### Branch depth, AI, localisation, and aftermath

A branch does not count as real unless it changes gameplay. In the spec, each major branch should have several focus groups, a mechanical unlock, a route consequence, and an end-state or payoff.

Major routes need route-specific AI plans. Do not let the implementation use generic focus weights for every route. The spec should say which AI types choose each route and when they avoid it.

Major routes need distinct localisation tone. A socialist route, military route, democratic route, nationalist route, religious route, machine route, death-state route, or foreign client route should not read like the same generic branch with different rewards.

Expansion branches should include postwar handling. War goals alone are not enough. Define claims, cores, puppet options, protectorates, occupation decisions, integration missions, border settlement events, resistance risks, diplomacy reactions, faction consequences, or achievement tracking.

Industry branches should be geographically grounded where possible. Define which states or regions receive factories, resources, ports, railways, supply hubs, forts, anti-air, dockyards, airbases, or infrastructure.

Advisor unlocks should match route identity. Political routes unlock ideological and government figures. Industry routes unlock engineers and economic boards. Military routes unlock commanders and high command. Diplomacy routes unlock envoys and foreign liaisons. High-chaos routes unlock route-specific councils, symbolic leaders, or strange authorities.

Large focus trees should include achievement hooks for difficult route completions, rare branch combinations, expansion outcomes, internal reform, avoiding foreign dependency, league formation, high-chaos survival, or late-game ambitions.

The final implementation prompt should ask for a route coverage table comparing required routes against implemented routes. Missing, renamed, merged, simplified, fallback, or replaced routes must be reported.


### Route visibility, pacing, tradeoffs, and failure states

A major route should leave visible evidence in the game. The spec should describe what the player actually sees or gains: map changes, decisions, units, advisors, leaders, flags, cosmetic names, faction behavior, focus availability, diplomacy, or visible mechanics. A route that only changes hidden variables or tiny modifiers is not meaningful.

Large focus trees should have early, middle, and late pacing. Early content solves survival and basic identity. Middle content creates route mechanics and real choices. Late content delivers major payoffs, expansion, faction or League outcomes, high-chaos routes, postwar settlement, or world-order ambitions.

Every major route should have a tradeoff. The spec should define what the route risks or sacrifices. Military routes may reduce freedom or legitimacy. Foreign-aid routes may create dependency. Expansion routes may create backlash. Industry routes may consume civilian capacity or weaken short-term defense. High-chaos routes may gain power while damaging stability, diplomacy, or normal politics.

Do not overuse mutual exclusions. Mutually exclusive paths should represent real identity changes, strategic commitments, or incompatible institutions. Support branches such as industry, army, diplomacy, and logistics should usually coexist unless the route logic says otherwise.

Important routes should define failure states. A failed political reform can empower radicals. Failed expansion can trigger backlash or settlement. Failed industry can create dependency. Failed foreign-aid balancing can create a client state. Failed military centralization can create rogue generals or militias.

Focus and decision localisation should describe the visible baseline effect of the route or action. It should not reveal hidden effects, secret outcomes, hidden variables, or future surprises. The player-facing text should explain the public action and visible direction, not the hidden implementation.


### Special mechanics, dynamic values, and faction systems

Large events should usually include at least one special mechanic. A special mechanic can be a pressure meter, influence system, balance of power, faction cohesion system, legitimacy system, corruption system, outbreak tracker, coalition command system, resource race, regional authority map, or similar play layer.

A special mechanic should define its important values clearly. Examples include legitimacy, authority, influence, cohesion, obedience, corruption, foreign penetration, military readiness, industrial capacity, public panic, faction unity, sponsor pressure, religious authority, revolutionary zeal, or regional control.

Mechanic values must be dynamic. They should move through focuses, decisions, missions, events, wars, state control, foreign influence, AI actions, and prior outcomes. Do not design a mechanic where values only drift passively or change through a few flat scripted effects.

Every important mechanic value should have a consistent colour identity in localisation. If several values contribute to a total, each contributing value should use its own colour consistently across tooltips, scripted localisation, decision text, event text, and UI summaries. If a mechanic has a total value made from components, the tooltip should show a readable breakdown with named and coloured components.

If a mechanic has values such as legitimacy, authority, influence, cohesion, obedience, power, or readiness, then focuses, decisions, and missions should interact with those values directly. A focus tree should not sit beside the mechanic without changing it. A decision system should not sit beside the mechanic without changing it.

Mechanic values should unlock or block content: decisions, focuses, events, missions, leaders, advisors, factions, war goals, reforms, crises, achievements, super-events, or endings. A mechanic should change what the player can do.

When a country has two or more internal power centers, consider a balance-of-power or equivalent system. Focuses and decisions should push the balance, unlock branch content, create risks, and change leaders, laws, advisors, events, or crises.

When an event creates a faction, league, bloc, coalition, compact, or alliance, define its goals and internal rules. The faction should have a reason to exist, membership rules, joining conditions, refusal logic, expulsion or removal logic where relevant, war goals, shared decisions, AI behavior, victory conditions, and failure conditions.

Important event-created factions should usually have a mechanic such as cohesion, shared command, war council support, joint reserves, recognition, member confidence, sponsor pressure, or strategic goals. Focuses and decisions should interact with that faction mechanic.

A faction should not form just because one country exists. Define minimum membership, crisis conditions, ideological compatibility, war pressure, diplomatic preparation, and regional logic.

A special mechanic should define success, failure, partial success, and runaway failure states. These states should unlock events, decisions, focus branches, faction changes, wars, reforms, aftermath, achievements, or super-events.

AI must understand mechanic values. It should know when to lower threat, build legitimacy, increase influence, join a faction, avoid dependence, push balance of power, or trigger escalation.

For every special mechanic, the completion report should list mechanic values, what changes them, what they unlock, UI and localisation coverage, AI behavior, focus hooks, decision hooks, event hooks, and balance checks.


### Mechanic presentation, faction outcomes, validity, and tuning

Every special mechanic should define where the player sees it: decision category header, custom scripted GUI, progress meter, scripted localisation tooltip, focus tooltip, national spirit tooltip, or another clear presentation surface. Important mechanic values should not exist only as hidden variables.

When a special mechanic uses a scripted GUI, consider visual presentation beyond static text. Useful designs can include progress bars, meter fill variants, state icons, status frames, warning frames, selected or locked variants, animated frames, or frame-by-frame visual changes that make the mechanic feel alive. The visual layer should make the mechanic easier to understand.

Special mechanics can hide future surprises, but they should not hide basic cause and effect. The player should understand why a visible value rose or fell, which public action changed it, and what kind of response is available.

Faction, league, bloc, or coalition goals should have rewards and failure states. A successful faction goal can unlock shared decisions, war goals, legitimacy, cohesion, member rewards, or postwar settlements. A failed goal can reduce cohesion, trigger exits, invite foreign pressure, start leadership contests, or weaken shared defenses.

New playable country packages must not be generic. Each needs a specific identity, starting problem, political direction, map role, military style, economy, diplomacy, AI behavior, and at least one mechanic or decision family that makes it play differently.

AI strategy must respect route validity. AI should not pick a branch or action that requires a missing state, dead sponsor, non-existent faction, unavailable ideology, disabled evolution, impossible border, invalid target, or absent enemy. Invalid routes should be hidden, bypassed, or weighted to zero.

When a route changes leader, ideology, faction, cosmetic name, flag, advisor roster, or special mechanic identity, define the needed visible assets and whether they are sourced, generated, reused, or blocked.

Shared trees are allowed, but they must have country-specific localisation, route names, decisions, AI weights, leaders, rewards, icons, and scripted localisation where relevant. A shared tree fails if every country using it reads and plays the same.

Important mechanic thresholds, caps, gains, losses, duration bands, AI weights, and scaling values should be centralized in script constants or a clearly documented tuning file. Do not scatter magic numbers across decisions, events, focuses, scripted effects, and scripted triggers.


### Reward dumps and exploit checks

Avoid one-time reward dumps as the main design. A focus, decision, or mission can give factories, units, equipment, resources, buildings, or influence, but important content should often unlock a repeatable decision, timed mission family, production route, advisor, mechanic, route branch, or long-term gameplay system.

One-time rewards are acceptable when they fit the story and balance. They should not become the default design pattern for a major event, large focus tree, or decision system.

Balance planning should include exploit checks. Look for free unit loops, repeated factory rewards, cheap construction loops, equipment farming, influence farming, puppet abuse, war-goal spam, claim or core spam, advisor discount stacking, bypass abuse, mission success farming, and decisions that can be clicked without meaningful cost or risk.

The spec should tell the implementation agent how to prevent abuse with flags, cooldowns, dynamic costs, escalating costs, one-time completion flags, route locks, target limits, AI limits, cleanup effects, or scripted triggers.


### Decision category clutter control

Large decision systems should not show every possible decision at once. The spec should define how decision categories stay readable.

Use phases, caps, priorities, regional pools, route locks, mechanic thresholds, or crisis-state filters so the player sees decisions that matter in the current situation.

Good planning patterns include:

- early, middle, and late decision tiers
- active mission caps
- region pools that rotate or unlock gradually
- decisions hidden when their route is invalid
- obsolete decisions removed after war, peace, settlement, or route change
- basic decisions replaced by stronger later decisions
- decisions grouped by target region, sponsor, faction, or mechanic value
- emergency decisions visible only during emergency states
- late-game decisions hidden until the route payoff is reached

A decision category should feel curated by the current route and campaign state, not like a debug menu.

### What the implementation agent owns

The implementation agent is responsible for the final exact focus tree shape unless the user asks otherwise.

The implementation agent should:

- choose the exact number of focuses needed for each path
- write final focus names and descriptions from the path design
- place focuses cleanly in the in-game grid
- create visually readable branches
- avoid ugly, tangled, or overly linear layouts
- create exact prerequisites and `mutually_exclusive` blocks
- wire bypasses and availability
- assign icons and search filters
- balance focus durations and rewards
- implement AI path weights
- report any design gap that prevents clean implementation

The spec should give enough creative and structural direction that the agent cannot make a shallow generic tree, while still allowing the agent to build a clean in-game layout.


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


## 3.7 Achievement design standard

Achievements are mandatory for event specifications unless the user explicitly says not to include them or the event is so small that achievements would be dishonest. Major events, custom countries, deep focus trees, rare variants, world-order routes, or super-events always need achievements.

Achievements should be creative and difficult. Do not design achievements that unlock just because the event fired, because the player clicked the obvious option, or because a country survived a few days. Achievements should reward mastery, unusual campaign states, risky choices, hidden routes, hard containment, difficult victories, or rare evolved outcomes.

A good achievement should usually require several conditions at once, such as:

- playing a specific country or route
- completing a difficult focus tree branch
- surviving a dangerous crisis state
- defeating or containing a major enemy
- avoiding an easy exploit, puppet shortcut, or foreign bailout
- triggering or suppressing a specific evolution track
- forming a special faction under strict conditions
- completing a rare high-chaos route
- winning while keeping a fragile coalition together
- using a special mechanic successfully without taking the safest path

Do not make achievements conservative. If the event has dark paths, high-chaos tags, strange mechanics, foreign influence systems, coalition politics, or world-order ambitions, design achievements for them. Difficult achievements can require long campaigns, high chaos, multiple wars, internal crises, and careful decision play.

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
- related focus paths, decisions, evolutions, tags, factions, super-events, or assets
- implementation notes for tracking if the unlock cannot be checked from a single final state

Achievement design must include asset planning. Each achievement needs a 64x64 completed icon direction, and the asset prompt must hand those icons to `chaos-redux-event-assets`. Grey, locked, and not-eligible variants can be produced later if the achievement system requires them.

The achievement list should include a spread of routes. Do not put all achievements on the safest or most obvious path. Cover containment, failure recovery, republic victories, foreign influence, special factions, strange countries, high-chaos routes, and secret or hard branches when those exist.

If an event creates many playable tags, design achievements for the most important ones and for the event-wide systems. A large event can justify dozens of achievements. The achievement prompt should still explain which ones are highest priority if implementation must be staged.

## 3.8 Baseline stages versus evolutions

Baseline stages and evolutions are different.

Baseline stages describe the ordinary flow of the event. They are the expected crisis lifecycle, such as first outbreak, containment attempt, spread, coalition formation, deep collapse, settlement, or defeat.

Evolutions are mutation tracks layered on top of the baseline. They make the event more predictable in some ways, more severe, stranger, more patterned, or more replayable. They can add new actors, new rules, new incidents, new tags, old movements, strange variants, stronger breakaways, or rare side branches.

Do not log ordinary stages as evolutions.

Do not use chaos tiers as simple walls that lock ordinary stage progression. Ordinary stages should flow from the event state. Chaos should affect intensity, probability, severity, weirdness, and opening strength.

### Evolution entry paths

When an event has evolutions, the spec must say how each evolution enters play. Do not write evolutions only as future modifiers or only as post-fire upgrades unless that is truly the design.

Use two separate entry-path concepts when the event supports both.

**Active-event evolution** means the event has already fired and an evolution unlocks while one or more actors from that event still exist or the event system is still active. The spec must define what changes immediately for the active actors: focus paths, decision families, national spirits, unit growth, targeting rules, AI strategy, faction behavior, super-event eligibility, and cleanup. The event should not need to fire again for the active actor to receive the evolution content.

**Pre-fire evolved opening** means the event has not fired yet, but the world state, chaos tier, previous evolution memory, or other allowed event trigger lets the first firing start in a more evolved form. The spec must define the changed opening package: number of actors, target selection, starting ideas, initial units, first decisions, opening events, AI plan.

If both entry paths exist, write both explicitly under one evolution. For example, an event may have an active evolution that unlocks a focus path for an already spawned country, while a later first firing may start with multiple spawned countries.

Each chaos tier can have only one evolution stage. The maximum amount of evolutions is 5.

Good evolutions can include:

- the same kind of crisis becoming easier to recognize and harder to stop
- foreign liaison networks appearing
- old historical movements returning in changed form
- new custom tags appearing that did not exist in vanilla
- extremist, occult, scientific, cultic, or ideological splinters appearing at high chaos
- strange fighter movements, partisan networks, or paramilitary identities forming
- new focus tree routes and decision categories opening

Each evolution should define:

- what changes from the baseline
- what conditions make it possible
- what makes it more likely
- what new player-facing content appears
- what new incidents or variants it unlocks
- what the evolution log title direction should represent
- how it interacts with chaos tier without being only a chaos-tier lock
- how it can be contained, spread, or escalate

## 3.9 Dynamic mechanics standard

Everything that acts like pressure, cooldown, progress, chance, support, duration, cost, tempo, AI willingness, spawn strength, aid amount, stage movement, or recognition should be dynamic by default.

Avoid fixed values as design answers. A fixed number may exist as a tuning anchor, but the spec should define the factors that shape it.

Dynamic factors can include:

- chaos tier and chaos value
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
- previous Chaos Redux events
- evolution state
- crisis duration
- faction cohesion
- AI personality and strategic situation

Do not say only that a cooldown is 30 days or a pressure increase is 5. Say what makes it shorter, longer, stronger, weaker, safer, or more dangerous.

Dynamic behavior should still be readable. Define cause and effect clearly so the player can learn the pattern through events and decisions.


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
- crisis pressure, threat-meter components, condemnation, deaths, pollution, contamination, or other Chaos Redux system values when relevant
- time, deadlines, objective failure risk, opportunity cost, or visible map requirements such as holding borders, guarding depots, or placing divisions in key states

Political power or command power may still be one part of a cost, but they should not be the default answer. If a section uses mostly political power or command power, redesign it unless the story clearly demands bureaucratic or command attention.

Costs should be dynamic. The amount and type of cost should react to country size, chaos tier, stability, war state, equipment stockpiles, supply state, front pressure, foreign access, local legitimacy, previous choices, AI situation, and current event pressure. A weak country should not pay the same cost as a strong country when the story says the burden is different.

Map blocked localisation for nonstandard costs. The player should understand whether they lack infantry equipment, support equipment, divisions in the right state, local support, army XP, fuel, rail control, relations, foreign route access, or another requirement.

For every major decision family, include at least one cost or requirement that is not political power or command power unless the spec explains why that family is purely bureaucratic.


## 3.11 AI strategy and behavior mapping standard

Major event specs must include a real AI section. Do not leave AI behavior as a vague note that the coding agent can decide later.

The AI section should map how every important affected country behaves across the event. This includes the event owner, breakaways, custom tags, transformed existing tags, foreign sponsors, faction leaders, nearby countries, rivals, allies, and countries that can exploit or contain the event.

For each important AI actor or actor group, define:

- what routes it can choose
- which routes it prefers under ordinary conditions
- which routes it only chooses under high chaos, desperation, ideology, war, foreign pressure, hidden path, or special evolution conditions
- what choices it should almost never make
- how it evaluates decisions, focuses, faction formation, volunteers, recognition, military action, negotiation, puppeting, annexation, and escalation
- how it reacts to dynamic pressures such as strength, stability, war state, proximity, casualties, supply, chaos tier, ideology, and previous outcomes
- how it uses or avoids rare variants and evolved tracks
- how it behaves when it is player-adjacent, major-power-adjacent, or a possible snowball threat
- what cleanup or fallback behavior it should use if its preferred route becomes impossible

For focus trees, the spec must define AI path behavior at the branch level and for key individual focuses. If a large tree has mutually exclusive paths, secret routes, or dangerous high-chaos paths, specify which AI personalities or campaign states can choose them. High-chaos AI should be allowed to make strange or extreme choices when that is the point, but ordinary AI should not accidentally choose suicidal or nonsensical branches.

For foreign influence mechanics, the AI section must explain how major powers decide whether to recognize, fund, arm, infiltrate, puppet, betray, or abandon new countries. If volunteers, expeditionary support, proxy wars, or faction invitations exist, AI behavior must be mapped for those too.

A good AI section should make the implementation agent unable to create generic AI weights while claiming to follow the spec.

## 3.12 Country package and dynamic identity standard

When an event creates, releases, transforms, or significantly modifies a country, the spec must define that country as a full package. This applies to new custom tags and to existing countries that gain event-specific political identities, focus trees, flags, leaders, cosmetic names, ideology names, starting forces, or mechanics.

For every new country, and every existing country that is meaningfully changed, the spec should provide a country package matrix or equivalent structured section. It must cover:

- tag or placeholder tag, with a note that final tags must avoid conflicts
- spawn, release, transformation, or takeover conditions
- core territory, claimed territory, disputed territory, and fallback territory
- history file needs and starting setup
- public country name and cosmetic names, following the country naming rules below
- ideology-specific names
- focus-tree route names
- faction names and possible faction cosmetic names
- ruling party names, sub-ideology labels, and political movement names
- starting politics and possible ideology shifts
- starting military package, including initial divisions, template families, manpower, equipment, command structure, supply assumptions, and dynamic scaling factors
- unit growth routes through decisions, focuses, objectives, volunteers, mobilisation, depots, foreign support, faction reserves, or special mechanics
- starting leader, leader traits, portraits, and possible leader replacements
- council, junta, committee, regency, cult, military, monarchist, democratic, communist, fascist, anarchist, or factional leadership variants when relevant
- flags for the base country, ideology variants, focus-tree variants, cosmetic variants, puppet variants, and major route transformations
- national spirits, ideas, decisions, events, focus tree, achievements, mechanics, and unit systems tied to that country
- AI behavior and route preferences
- asset needs for every visible identity state
- localisation tone and naming rules
- documentation needs
- compatibility notes if the country already exists in vanilla, Chaos Redux, or common mods

Do not treat a custom country as complete because it has a tag and one flag. A serious country needs identity, politics, names, flags, leaders, starting forces, force-growth routes, mechanics, decisions, AI, localisation, assets, and route changes. If the country is only temporary and does not need a full package, the spec must explain why.

Political identity should be dynamic when the content supports it. Focus routes, ideology changes, coups, faction victories, foreign puppeting, religious transformations, high-chaos mutations, monarchist restorations, military takeovers, revolutionary councils, or world-order paths should be able to change the country name, flag, ruling party, leader, leader portrait, leader trait, cosmetic tag, national spirits, available decisions, and available recruitment systems when appropriate.

### Country naming rules

Country names must be direct public country names that remain readable on the map.

Do not build public country names from internal political attachments. Avoid names that use terms such as `Military Office`, `Compact`, `Bureau`, `Authority`, `Mission`, `Board`, or similar administrative labels as the country name. These terms can exist as mechanics, focus groups, advisors, decisions, councils, ministries, internal institutions, route labels, or faction mechanics when they fit. They should not be the public name printed on the map.

Ideology-specific country names are allowed when they fit the route. Sultanate, Kingdom, Empire, Republic, Union, Commune, Federation, and similar public state forms are valid when they match the ideology, historical claim, route, or formable identity.

Prefer names built from the country, people, dynasty, region, or formable identity, then add a simple public state form only when it improves clarity. Style examples include:

- `Asante`
- `Kingdom of Asante`
- `Asante Republic`
- `Sultanate of Kilwa`
- `Kongo`
- `Kongo Commune`

Do not overload country names with political office language. The political office, emergency cabinet, military committee, colonial mission, compact council, bureau, authority, or board can be a mechanic or institution inside the country package. The map name should stay short and readable.

Names may depend on ideology, route, leader, formable status, puppet status, or high-chaos transformation. Even then, the public name should remain a country name, not an agency name.

For alternate governments, design internal bodies and party names separately from public country names. A route can have named councils, committees, directorates, juntas, congresses, restoration offices, cult offices, leagues, syndicates, ministries, synods, communes, or military commands. Those institution names should fit the country story, region, history, route, and ideological language without replacing the public country name.

## Formable nations and formation routes

When an event creates, transforms, releases, or empowers countries, check whether formable nations should be part of the design. A formable is a meaningful country identity that appears after a country satisfies territorial, political, event, focus, or hidden-route requirements. Do not treat formables as only a cosmetic rename.

Formable public names must follow the country naming rules above. The formation decision, congress, authority structure, charter, settlement, or council can have its own institutional name, but the formed map name should stay a direct country or formable name.

A formable design should define:

- formable name and tag handling
- whether it uses a new tag, an existing tag, a cosmetic tag, or a dynamic country name
- required owned and controlled states
- required cores, claims, subjects, puppets, allies, faction members, or occupied areas
- alternate state sets for different borders or reduced maps
- focus route or event route that reveals the formation
- decision that performs the formation
- hidden unlock conditions, if the formable is secret
- ideology, leader, government, legitimacy, recognition, chaos tier, crisis, patron, or achievement gates
- effects on cores, claims, compliance, resistance, subjects, puppets, factions, advisors, laws, technologies, and ideas
- visible country identity after formation, including name, adjective, flag, leader, portrait, parties, ruling ideology, advisors, and focus tree access
- post-formation ambitions, claims, diplomatic reactions, rivals, league or faction behavior, and failure states
- AI willingness to pursue the formable and AI safety checks that prevent impossible or suicidal formation attempts
- super-event, achievement, and asset implications

Do not write vague lines such as `can form a greater country`. Define the concrete formation web. If the player must control this state, this state, and this state, name those states or name the scripted state group and explain what it contains. If the exact state ids are left to implementation, describe the intended geographic set clearly enough that the implementation agent can build a scripted trigger without guessing.

Hidden formables should still be designed fully. The spec can hide player-facing names and spoilers, but the implementation handoff must describe the unlock route, required flags, reveal event, decision visibility, AI behavior, rewards, assets, and disqualifiers.

Formation routes should interact with focus trees and decisions. A focus can reveal or prepare the claim, while a decision performs the formation after the map requirement is met. A decision can form the country directly, while later focuses stabilize it, core it, claim further territory, or resolve internal factions. Avoid giving a formable through a focus alone when the player should prove control over named land first.

## 3.13 Starting forces and reinforcement pathway standard

When an event creates, releases, transforms, restores, or revives a country that is expected to fight, survive, defend itself, or matter militarily, the spec must define its starting forces. Newly appearing countries should not spawn as empty tags unless they are explicitly non-military administrative placeholders and the spec explains why.

Starting units must be dynamic. Do not define one flat number of divisions for every country. The spec should explain what makes the starting force stronger, weaker, larger, smaller, better equipped, more irregular, more professional, more defensive, more foreign-backed, or stranger.

Useful scaling factors include:

- chaos tier and chaos value
- event threat, crisis pressure, evolution state, and ordinary stage state
- local population, industry, terrain, ports, rail hubs, depots, and capital control
- local legitimacy, public support, militia networks, and command obedience
- defecting army districts, security units, sailors, railway guards, border guards, police forces, or factory guards
- captured equipment, depot vulnerability, foreign aid, volunteer corridors, and faction support
- parent-country weakness, missed deadlines, lost objectives, supply failure, war state, and previous choices
- whether the tag is an ordinary republic, emergency committee, factory state, ancient restoration, partisan movement, cult, railway state, naval state, or other special actor

For every meaningful new or transformed country, map:

- starting division families or template concepts
- expected starting strength in weak, normal, severe, and high-chaos openings
- equipment and manpower source
- whether units are militia, regular defectors, border guards, mountain detachments, factory guards, railway troops, sailors, cavalry, foreign volunteers, ancient levies, or special high-chaos formations
- starting commanders, officer shortages, or leader ties when relevant
- defensive bonuses, training penalties, supply weaknesses, morale problems, or legitimacy risks
- how the package affects threat meters, foreign attention, depot pressure, old-movement resurgence, or parent-country authority
- what report, event text, or localisation direction should explain why those troops exist

The spec must also map how newly appearing countries can get more units after spawning. This should include decisions, timed objectives, focus rewards, volunteer systems, depot captures, foreign missions, local mobilization, League or faction training, factory guard mobilization, border guard formation, or special high-chaos recruitment where appropriate.

Do not make reinforcement depend only on political power or command power. Use concrete goals and resources such as holding a capital, guarding a border, controlling a depot, controlling rail lines, spending army XP, consuming equipment, committing manpower, using fuel or trains, securing local support, opening a foreign corridor, finishing a construction quota, proving legitimacy by a deadline, placing divisions in required states, or keeping a volunteer route open.

Unit-creating focuses and decisions must be specific. Avoid repeated generic rewards such as `add two infantry divisions` across many countries. A unit reward should explain the institution and story behind the unit, such as capital defense committees, local garrison defections, railway guards, factory guard shifts, mountain pass detachments, Black Banner columns, sailor battalions, Basmachi cavalry, ancient host militias, medical volunteers, foreign-trained cadres, or high-chaos special units.

Each unit-creating focus or decision should define:

- what unit or template family appears
- what unlocks it
- what non-political-power requirements it uses when appropriate
- whether it is repeatable, timed, risky, route-locked, or one-time
- what pressure or threat values it changes
- what downside it creates if repeated or failed
- what AI should do with it
- what blocked localisation direction should communicate when requirements are missing
- what icon, spirit, report event, or commander asset it needs when relevant

For focus trees, military growth should be integrated into branches. Some focuses can spawn units directly, but others should unlock decisions, improve templates, recruit commanders, create volunteer corridors, integrate militias, convert irregulars into regulars, expand special units, or change mobilisation rules. A deep tree should offer different ways to build an army depending on politics, foreign influence, economy, terrain, ideology, and chaos state.

## 3.14 Mandatory asset coverage and source-mode standard

Everything visible or meaningful needs an asset plan. A major spec should not only define a few event pictures. It should identify assets for countries, focus trees, decisions, ideas, national spirits, achievements, flags, portraits, faction emblems, super-events, event pictures, UI, unit systems, and route-specific identity changes.

Every focus in a mapped focus tree needs an icon direction. Large trees may use reusable icon packs, but the spec must still state which focuses use which motif or icon category. Do not leave hundreds of focuses with no asset guidance.

Every decision, decision category, idea, national spirit, achievement, faction emblem, UI panel, news image, report image, super-event image, leader or council portrait, and important special-unit identity that appears in the event needs an asset entry or a clear asset-family entry.

Every country package must include flags. Required flag coverage includes normal, medium, and small sizes for each implemented flag state. If the country has ideology-specific names, focus-tree transformations, puppet identities, restored historical forms, radical routes, or high-chaos mutations, the spec must identify whether those states need separate flags.

Historical and real-world flags should not be invented with `$imagegen` by default. If a country, movement, party, military authority, or restoration path has a real historical flag or a well-attested symbolic design, the asset prompt should instruct the asset agent to source that flag or symbol from a reliable source, document it, and convert it into HOI4 flag sizes. Use `$imagegen` only for fictional, alternate, supernatural, or deliberately invented flag identities when generated art is appropriate.

Historical or real leaders should not be generated. The spec should identify likely real portrait needs and instruct the asset agent to source real images, document source and license status, and crop them to HOI4 portrait size. Fictional leaders, council portraits, cult leaders, alternate invented officers, and symbolic committee portraits can use `$imagegen` when generated art is appropriate.

When an asset source is historically sensitive, disputed, or politically loaded, the asset prompt must require source notes, and a clear distinction between sourced historical use and fictional alternate-history invention.


## 3.15 Effect strength and impact standard

Do not design important event effects with timid or decorative values. If an idea, decision, focus, mission, national spirit, or crisis response is supposed to matter, its effects should be strong enough for the player to feel and plan around.

Avoid conservative values such as plus 2 percent or minus 3 percent as the main reward or penalty unless the spec explains that they are part of a wider stacking system. A small modifier can support a larger effect package, but it should not be the whole design.

A good effect package should do at least one meaningful thing:

- change player incentives
- unlock a new decision, mission, focus branch, unit type, mechanic, or route
- move a crisis, loyalty, legitimacy, recognition, stability, or threat value in a visible way
- create a real cost, risk, or tradeoff
- alter army, economy, diplomacy, internal politics, logistics, production, or intelligence behavior
- change how a country plays for a meaningful period
- connect to later events, evolutions, achievements, or super-events

Effects should fit the event story. A desperate military measure should not only cost political power. A logistical crisis should interact with trains, fuel, depots, supply, equipment, routes, or tied-down units. A legitimacy crisis should affect stability, war support, recognition, internal factions, local support, or authority. A foreign intervention system should create influence, dependence, access, backlash, or diplomatic consequences.

The spec should explain why a value is strong, weak, temporary, risky, or conditional. Do not make every effect huge, but do not hide a major event behind barely noticeable numbers. Special chaos countries usually do have absurd numbers, because the country itself is absurd and that justifies it.


## 4. What the specification should explore

A strong specification usually explores:

- the core event concept
- why the event matters
- how the event first appears
- what the player sees and chooses
- what tone the event options use, including irony, sarcasm, cultural remarks, humour, or plain severity where appropriate
- what consequences follow
- how the situation can escalate
- what rare variants can happen
- how AI countries react and choose routes
- how the event changes under different world conditions
- what decisions exist and how they interlock
- whether the event should create focus tree content
- whether the event should create new tags or transform existing countries
- what starting units and reinforcement routes new countries receive
- how each new or transformed country changes names, flags, leaders, ideologies, parties, and politics
- whether the event should use a super-event
- what achievements should exist and why they are difficult
- what UI or visual presentation would make it stronger
- what other Chaos Redux systems it should interact with
- what assets the event needs, including all route-specific country assets
- what historical flags, symbols, and portraits must be sourced rather than generated
- what the coding agent needs to know before implementation

When exploring these areas, do not stop at the first obvious answer. Consider multiple versions and choose or describe the strongest ones.

For important events, think through edge cases, country differences, country package completeness, player incentives, AI incentives, abuse risks, pacing, cooldown factors, narrative tone, repeat play, and evolved behavior.

## 5. Chaos Redux system awareness

Consider links to existing Chaos Redux systems when they strengthen the event.

Possible links include:

- Chaos Meter
- evolutions
- super-events
- world-end scenarios
- event clusters
- condemnation
- deaths
- air cleanliness
- chemical warfare
- biological warfare
- world threats
- existing or planned events

Leave out connections that feel artificial.

## 6. Escalation and uncertainty

Dangerous systems should not reveal themselves too early.

Player-facing escalation text must not label itself as a warning, a non-warning, a threat, a danger signal, or a world-ending risk. Do not tell the coding agent to write text that announces what the player is supposed to infer. Do not frame an event-detail entry, report, news item, tooltip, decision category, focus description, super-event direction, or spreadsheet-facing summary around that direct label.

Use mysterious information, fear, and uncertainty instead. Early information should feel incomplete because people cannot yet explain what is happening.

Do not build mystery from bureaucratic document motifs, archive-style secrecy, diplomatic evasions, or paperwork drama. Avoid staged contrast formulas that make tension from one side saying or seeing something while an official body denies, delays, softens, avoids, or reacts to it. Avoid timing formulas that make one observation happen before an official admission, public reaction, government response, or wider consequence. Describe the observed fear and uncertainty directly.

The player should understand deeper danger through patterns and consequences over time. It should not explain that the content is a warning or reassure the player that it is not one.

## 7. Depth and hidden connections

Look for design connections the user may not have considered.

Useful connection types can include:

- callbacks to existing events
- links to planned events
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

Add these when they make the event stronger.

## 8. Custom UI and presentation

If the event benefits from custom UI, design one.

Describe what the player sees, how it changes, and what visual assets are needed.

Map the UI states if the UI represents pressure, route choice, threat, stage, faction cohesion, recognition, contamination, loyalty, or any other living value.

## Interactive mechanic UI and animated presentation in event specs

When an event has an important mechanic, decide whether the decision category needs a richer scripted GUI or a separate mechanic window. The spec should define the player-facing interface when the system is important enough to manage visually.

For major events, important decision categories, custom mechanic windows, formable routes, high-chaos route reveals, active crisis meters, special leader transformations, faction boards, patron influence networks, or occult and supernatural systems, run an animation planning pass by default. The pass must either define useful animated sprites or state why static presentation is better for that exact surface. Do not skip the question simply because static assets are easier.

A mechanic UI spec should include:

- where the UI appears, such as decision category header, attached scripted GUI, custom window, event-details panel, or country mechanic panel
- what button opens or closes the window
- what values, targets, meters, cards, lists, tabs, or map states the player sees
- what buttons the player can click and what each costs
- how unavailable buttons explain missing requirements
- what scripted effects and scripted triggers own the button logic
- how AI performs equivalent actions without relying on human-only clicks
- how the UI cleans itself up after route change, tag change, annexation, civil war, peace, or event completion
- what localisation and scripted localisation the UI needs
- what static assets, animated sprites, hover states, selected states, locked states, warning states, and progress variants it needs
- what animated state communicates, such as available action, rising pressure, critical danger, selected target, active ritual, foreign influence spread, reform momentum, hidden route reveal, route corruption, or completion
- which animation surfaces are state-driven and which are decorative
- which static fallback appears when animation is disabled, unsupported, not yet produced, or hidden by route state

The spec should not make an interactive window for every small modifier. Use custom UI when it improves readability, choice, atmosphere, or management of a living system.

Animated presentation should be planned more often than static-only presentation for mechanics that feel alive. Use it for pressure rising, corruption spreading, a council activating, an occult meter pulsing, a patron influence network glowing, a formable seal becoming available, a faction board entering crisis mode, a route emblem changing after a focus, or a warning frame appearing near failure. Animation should clarify the mechanic and improve presentation. It should not hide information or add noise.

Animation is especially useful when the player needs to notice a changed state without reading a long tooltip. Good default candidates include decision category seals, category headers, scripted GUI buttons, meter frames, status cards, selected target cards, warning borders, hidden route seals, formable progress emblems, faction cohesion panels, patron influence nodes, and high-chaos route emblems.

For each planned animated asset, the spec should define the in-game use, target surface, state logic, frame count expectation, loop behavior, static fallback, source mode, asset handoff owner, and proposed sprite names when they are known. The final animation must follow `chaos-redux-frame-animation`, meaning real source frames, a frame sheet, a static fallback, a preview GIF for review only, and a `.gfx` handoff. Do not describe a GIF, filter pulse, recolour loop, shifted still image, or transform-only mockup as the final game animation.

Leader portraits can have animated variants for major route reveals, high-chaos leaders, supernatural leaders, symbolic councils, final formables, or dramatic country transformations. The spec should say when the animated portrait appears, what static fallback exists, whether the portrait is sourced or generated, what state or route controls it, what removes or replaces it, and how the animation remains period-appropriate and readable at leader-portrait size.

## 9. Super-event planning

If the event needs a super-event, design the super-event as part of the event emotional and gameplay pacing.

A super-event should not be used only because something large happens. It should mark a moment that changes how the player understands the campaign, the event chain, the world state, or the stakes of the current crisis.

When planning a super-event, define:

- why this moment deserves super-event treatment
- what exact event state triggers it
- whether it is a reveal, escalation, transformation, defeat, aftermath, or world-end moment
- what the player should feel when it appears
- what the world believes has happened
- what information is still uncertain
- what image direction would fit
- what quote direction would fit
- what cultural remark direction would fit
- what audio mood would fit
- whether it needs follow-up events, decisions, or focus routes

Keep the super-event tone specific to the event. Do not make every super-event feel like the same apocalypse with a different image.

Do not fully research quotes, cultural remarks, or music inside this skill. Use `chaos-redux-super-events` for that work.

The event spec should provide enough direction for `chaos-redux-super-events` to find real quotes, meaningful cultural remarks, and suitable audio.

### Super-event text boundary and research gate

This skill is direction-only for super-event title text, `.a` button text, `.q` quote text, and any cultural reference. Do not write a final title, option, button line, quote, lyric fragment, slogan, proverb, scripture excerpt, literary allusion, or film, song, book, or game reference inside the event spec unless the exact wording has already been researched, sourced, and documented through the super-event skill or a provided source file.

If research has not been done, use neutral research gates instead of lines that could be pasted into localisation:

- `Reveal super-event title: research required`
- `Button remark: research required`
- `Main quote: research required`
- `Cultural reference: research required`

Do not include unresearched `possible line`, `sample title`, `placeholder quote`, or `temporary button text`. Implementation agents may treat those as final localisation.

Describe the desired shape instead. For example, write `short title direction about public recognition of the threat, avoiding generic apocalypse wording`, not a finished title.

Functional labels are allowed for spec structure, asset filenames, and prompt routing, but they must be neutral and explicitly non-final. Use labels such as `mainland reveal super-event`, `world-end super-event`, or `se_death_mainland_reveal`. Do not name assets, localisation keys, or prompt files after unresearched title concepts.

### Major-event defeat aftermath

Some major events should also have a structured aftermath when the threat is beaten.

Use a defeat aftermath package when all of these are true:

- the defeated threat was global or near-global in reach
- the campaign lasted long enough to feel like a world crisis
- the cost in casualties, destruction, or political disruption was high enough that the world should not simply snap back to normal

Typical aftermath content:

- a defeat super-event or defeat-stage super-event effect
- postwar treaties, compacts, or new world orders
- recurring remembrance, reconstruction, or vigilance events
- lasting ideas, tech-sharing groups, or diplomatic rules that exist because the world learned from the crisis

Do not add a treaty/new world order after every contained or short-lived disaster. Those only make sense when the event genuinely reshaped the campaign.

## 10. Writing style

For player-facing text, define the same style as direction only. Event description direction can stay grounded while option direction can use irony, sarcasm, cultural remarks, and humour that fit the actor and stakes.

Avoid:

- generic disaster wording
- empty dramatic language
- making every event apocalyptic
- random chaos without purpose
- implementation code
- excessive technical detail
- filler text that repeats obvious system behavior
- displaying event effects in event details
- long sentences without actually saying anything
- short staccato sentences that are dramatic and just make comprehension more confusing
- option direction that would lead to bland placeholder buttons
- absence notes for systems that are not present, such as saying an event has no world-end scenario or no manual triggerable scenario

Mention implementation only where it matters for the design, such as super-event treatment, custom UI, AI behavior, documentation, assets, dynamic factors, focus tree structure, custom tags, or important system connections.

This planning skill defines direction for player-facing text. It must not write final player-facing localisation. This includes event titles, event option text, event descriptions, news and report prose, decision names, decision descriptions, focus names, focus descriptions, achievement titles, achievement descriptions, GUI labels, event-detail text, spreadsheet-facing wording, super-event titles, super-event button text, super-event quotes, cultural remarks, source-like allusions, and final audio selections.

The planning spec may define tone, actor viewpoint, structure, visible information, route variation, dynamic placeholders that final text should use, and research needs. If a working label is needed for a row, filename, prompt, branch, route, asset, diagram, or internal handoff, mark it clearly as `working label, not final localisation`.

Important super-event boundary: this planning skill may define super-event role, trigger, tone, image direction, quote direction, cultural-remark direction, and audio mood. Any source-dependent wording belongs to `chaos-redux-super-events` and must stay blocked until researched and documented.

### General text writing style

1. Never use the em dash or semicolons in sentences.
2. Absolutely avoid dialectical hedging. Do not frame sentences as thesis, antithesis, synthesis.
  - Dialectical hedging examples:
    - `The invasion is not merely a border crisis, but a crisis of identity.`
    - `The regime is not only losing the war, it is losing itself.`
    - `This is not just a strike. This is a warning.`
    - `The cult is not fighting for land, but for meaning.`
    - `The disaster is both a local tragedy and a global sign.`
    - `The government is neither dead nor alive, but something worse.`
    - `The army did not collapse. It transformed.`
    - `This is less a rebellion than a confession.`
    - `The question is not whether order can return, but what kind of order will survive.`
    - `What looks like defeat is actually a new form of power.`
  - Thesis, antithesis, synthesis examples:
    - `The army claims the province is secure. Refugees say it is already lost. The truth lies between them.`
    - `Some call the new state liberation. Others call it occupation. In reality, it is both.`
    - `The priests call it a miracle. The generals call it a weapon. History will call it both.`
    - `The committee promises order. The opposition sees tyranny. The new system contains both impulses.`
    - `The papers call it a victory. The hospitals call it a defeat. The country has become both at once.`
    - `The rebels ask for justice. The regime asks for peace. The settlement gives neither and both.`
3. Avoid AI-style explanatory templates. Do not write lines that sound prebuilt or reusable across any event.
4. Absolutely avoid staccato sentences. Do not split one simple thought into a chain of tiny lines for artificial weight or dramatic effect. Use complete, readable sentences with enough context to be clear.
  - Staccato examples:
    - `The radios died. The roads emptied. The city listened.`
    - `No orders. No mercy. No dawn.`
    - `The border fell. Then the capital. Then the government.`
    - `They marched. They burned. They vanished.`
    - `A knock at the door. A list on the table. A train in the dark.`
    - `The guns stopped. The screaming did not.`
    - `First hunger. Then anger. Then flags.`
    - `No king. No cabinet. No law.`
    - `Ash in the streets. Smoke over the port. Silence at noon.`
    - `One order. One shot. One missing officer.`
    - `The gate opened. The crowd moved. The guards ran.`
5. Avoid staged contrast formulas. Do not write sentences or paired clauses built as `claim X while officials Y`, `reports say X while authorities Y`, `people do X before governments Y`, `X happens before Y admits it`, or similar. Do not manufacture tension by contrasting unofficial fear with official denial, silence, delay, admission, or reaction. Write the observed fear, behaviour, rumours, anomalies, and consequences directly.
6. Absolutely avoid empty dramatic filler. Do not lean on vague intensity words when concrete detail would do the work.
7. Do not paste instruction text, task labels, prompt fragments, or process notes into in-game text, specs, docs, localisation, spreadsheet fields, or reports.
  - For example, when I say: `Do not reveal the hidden mechanics here.`, don't write `This path purposely doesn't reveal the hidden mechanics`

## 11. Specification shape

Do not force the specification into a fixed template.

Choose the structure that best fits the event idea.

The specification should still be easy for a coding agent to use. Use clear headings, explain the logic in a natural order, and make sure important design decisions are not buried.

For major events, split the spec into parts if needed. Do not compress deep design just to fit one file.

Only include sections for surfaces that exist or that need design. If a world-end scenario, manual triggerable scenario, super-event, focus tree, custom country, achievement set, or asset family is absent, omit that section instead of writing that it is absent. Because negative notes create noise and can mislead later agents into thinking the absence is a designed feature.

## 12. Depth and continuation

Do not compress the spec so much that important ideas become shallow.

The goal is depth, not speed.

Think through the event as far as the idea can reasonably go. If the event has multiple branches, evolutions, rare variants, custom countries, focus trees, UI elements, super-events, or major system connections, treat each of those as deserving real design space.

Large events should be written across multiple parts instead of being rushed into one response.

Each part should be complete enough to be useful on its own. Stop at a clean section boundary or a clean subsection boundary when possible. If the response must stop in the middle of a large design surface, stop after a complete paragraph, table, or list item instead of cutting a thought in half.

Do not summarize later sections just because the current response is getting long. Continue in the next part instead. Use the available response space for real specification content. Do not hold back important design material for a shorter answer.

When a large event specification cannot fit into one response, end the current part with a temporary continuation prompt for the next iteration. This continuation prompt is not part of the final specification, not part of the downloadable package, and not part of any event docs. It is only a working handoff that the user can paste back so the next response continues from the exact stopping point.

The continuation prompt should be concise but precise. It should include:

- the event id, event name, and current part number when known
- the exact section and subsection where the previous part stopped
- the last completed heading or table
- the next heading, table, route, country package, decision family, asset group, or prompt package to write
- any constraints that must continue to apply, including direction-only localisation, country naming rules, asset source rules, and the user's core event idea
- a reminder to continue with full-depth design and not summarize missing sections
- a reminder to avoid repeating already completed sections except for short context needed to continue cleanly

Use a clear temporary heading such as `Temporary continuation prompt, not part of the spec`. Keep it outside the saved spec content. In the final compiled package, remove all temporary continuation prompts and only keep the complete specification, asset prompt, implementation prompt, and any other requested final files.

If several iterations are needed, each part should write a new continuation prompt that reflects the new stopping point. Do not reuse an older continuation prompt after the design has moved forward.

When the final part is complete, do not write a continuation prompt. Instead, provide the final package or completion summary and make clear that the specification has reached the planned end.

For major events, the final combined specification may be extremely long. That is acceptable. A 10,000 line, 50,000 line, or 100,000+ line specification is valid if the event truly needs that much design detail. Do not compress focus trees, rare variants, or decision webs into summaries just to keep the file short.

Avoid filler. Every section should add useful design, player-facing detail, implementation clarity, asset direction, or system connection.

Before saving the final spec, run a cleanup pass. Remove generic safeguards, obvious implementation boilerplate, empty labels, repeated wording, and admin audit sections.

## 13. Asset planning

The event specification should identify all important visual assets. For major events, assume every visible system needs asset planning unless the spec explicitly explains why it does not.

Consider whether the event needs:

- idea icons
- national spirit icons
- focus icons for every focus or focus-family in each mapped tree
- decision category icons
- decision icons
- achievement icons
- news event pictures
- report event pictures
- super-event images
- leader portraits
- council, committee, regency, cult, junta, or symbolic leadership portraits
- faction emblems
- flags for every new country, modified country identity, ideology variant, focus-route variant, puppet identity, and major cosmetic transformation
- UI
- animated decision category seals, mechanic-window elements, warning pulses, route emblems, hover loops, selected states, glow loops, float loops, particle loops, and animated leader portraits when motion clarifies the mechanic
- progression-state variants
- static fallbacks for every animated UI piece, route emblem, icon, or portrait
- country-selection, event-log, or custom-window graphics when relevant

Asset generation, sourcing, cropping, resizing, DDS conversion, file placement, sprite handoff notes, and manifests belong to `chaos-redux-event-assets`. Animated frame planning and frame-sheet handoff requirements belong to `chaos-redux-frame-animation`. Final `.gfx` wiring belongs to the main implementation agent unless a parent prompt explicitly grants that scope.

This skill should define what assets are needed, what they should represent, what source mode they require, and which visible states should be animated. If a major mechanic has no animated sprite plan, the spec should explain why the static presentation is stronger.

Historical or real-world assets need special care. Historical flags, historical symbols, and real leader portraits should be sourced from reliable references and converted to HOI4 style rather than generated. Generated art is appropriate for fictional flags, fictional leaders, symbolic council portraits, invented high-chaos identities, idea icons, focus icons, decision icons, achievements, faction emblems, UI art, and fictional or alternate-history report/news/super-event images unless the user says otherwise.

### Reference examples for asset planning

When a spec or asset prompt asks for generated or sourced assets, tell the asset agent to inspect the matching reference examples before creating anything.

Use Linux project paths:

```text
C:/Users/klimp/OneDrive/Documents/Paradox Interactive/Hearts of Iron IV/mod/chaos_redux/.agents/skills/chaos-redux-event-assets/assets/ideas
C:/Users/klimp/OneDrive/Documents/Paradox Interactive/Hearts of Iron IV/mod/chaos_redux/.agents/skills/chaos-redux-event-assets/assets/news_event_images
C:/Users/klimp/OneDrive/Documents/Paradox Interactive/Hearts of Iron IV/mod/chaos_redux/.agents/skills/chaos-redux-event-assets/assets/report_event_images
C:/Users/klimp/OneDrive/Documents/Paradox Interactive/Hearts of Iron IV/mod/chaos_redux/.agents/skills/chaos-redux-event-assets/assets/super_event_images
C:/Users/klimp/OneDrive/Documents/Paradox Interactive/Hearts of Iron IV/mod/chaos_redux/.agents/skills/chaos-redux-event-assets/assets/tech_icons
C:/Users/klimp/OneDrive/Documents/Paradox Interactive/Hearts of Iron IV/mod/chaos_redux/.agents/skills/chaos-redux-event-assets/assets/achievements
C:/Users/klimp/OneDrive/Documents/Paradox Interactive/Hearts of Iron IV/mod/chaos_redux/.agents/skills/chaos-redux-event-assets/assets/decisions
C:/Users/klimp/OneDrive/Documents/Paradox Interactive/Hearts of Iron IV/mod/chaos_redux/.agents/skills/chaos-redux-event-assets/assets/flags
C:/Users/klimp/OneDrive/Documents/Paradox Interactive/Hearts of Iron IV/mod/chaos_redux/.agents/skills/chaos-redux-event-assets/assets/focuses
```

Reference mapping:

- idea and national spirit icons: `assets/ideas`
- news event images: `assets/news_event_images`
- report event images: `assets/report_event_images`
- super-event images: `assets/super_event_images`
- tech icons: `assets/tech_icons`
- achievement icons: `assets/achievements`
- decision and decision category icons: `assets/decisions`
- flags: `assets/flags`
- focus icons: `assets/focuses`
- and others if needed

The event spec does not need to analyze those images itself. It should make the handoff explicit so the asset agent knows which example set to inspect before generation, sourcing, cropping, or wiring.

## 14. Asset prompt handoff

After the full event specification is complete, create a separate asset prompt file for `chaos-redux-event-assets`.

The asset prompt should include:

- required assets
- visual style
- symbols and motifs
- target sizes
- intended in-game use
- country package asset coverage, including base flags, ideology flags, focus-route flags, cosmetic flags, leaders, portraits, and faction emblems
- suggested filenames
- suggested sprite names
- suggested static fallback sprite names and animated sprite names when animation is planned
- whether each asset is for an event, report event, news event, super-event, decision, idea, focus, achievement, flag, leader portrait, faction emblem, or UI element
- animation brief needs for every animated asset, including state logic, frame count target, target frame size, expected sheet size, frames per second, loop behavior, `play_on_show` expectation, static fallback, source mode, and target `.gfx` or `.gui` surface when known
- achievement icon list with completed icon directions for every achievement
- manifest requirements
- source mode, including whether a flag, symbol, or portrait must be sourced historically instead of generated
- reference example folder that must be inspected before asset work

The asset prompt must state the correct source mode where relevant.

It must also state the relevant reference folder from the list above when a matching folder exists.

Use `chaos-redux-event-assets` rules for source selection. Symbolic icons usually use `$imagegen`. News event images, report event images, and super-event images may be sourced or generated. prefer generated assets for fictional, alternate-history, symbolic, high-chaos, or unique scenes, and sourced assets for real historical people, real photographed events, and real archival artifacts. Historical flags and historically attested symbols should be sourced and documented, then converted to HOI4 flag sizes. Fictional, supernatural, invented, or alternate-history flags can use `$imagegen` through `chaos-redux-event-assets` when appropriate.

Do not make the asset prompt vague. If a country has multiple cosmetic identities, ideology names, focus-route transformations, or leader changes, the asset prompt must list the required assets for each visible identity state. If any visible identity state is important enough to feel like a reveal, crisis mode, high-chaos form, completed formable, or living mechanic state, the asset prompt should usually include an animated sprite or animated portrait plan plus a static fallback.

## 15. HOI4 asset size reference

Use these sizes when planning assets:

- report event images: 210x176
- news event images: 397x153, black and white
- leader portraits: 156x210
- flags small: 10x7
- flags medium: 41x26
- flags normal: 82x52
- tech icons small: 64x64
- tech icons medium: 132x52
- achievements: 64x64
- super-event images: 457x328
- decision icons: 32x32
- idea and national spirit icons: 64x64
- focus icons: 94x86

Use other sizes when the event UI or asset type requires it.

## 16. Asset style reference

When planning visuals, use these style expectations.

Report and news event images should look like documentary photographs, whether sourced or generated. News event images should be black and white.

Super-event images should have a strong central composition, clear dramatic theme, readable subject, and enough contrast for HOI4 UI.

Focus icons should look like HOI4 focus icons, with a central symbol, readable silhouette, aged texture, painterly detail, and strong contrast.

Idea and national spirit icons should look like compact HOI4 icon art. They need strong symbolic shapes and clear readability at 64x64. They are similar to focus icons, but they are missing the main frame.

Achievement icons should be readable at 64x64 and have a clear completion theme. The completed version is generated first. Grey and not-eligible variants can be produced later.

Flags should use clean symbols that remain readable at HOI4 flag sizes.

Progression-state variants may include selected, dim, active, locked, completed, rejected, damaged, corrupted, urgent, meter-fill, and bar-fill states.

## 17. Super-event research handoff

If the event has one or more super-events, create a separate super-event prompt file for `chaos-redux-super-events`.

The prompt should ask that skill to research or create the full super-event presentation package.

For each super-event, include:

- super-event purpose
- trigger moment
- tone
- title direction, not a final title unless researched and sourced
- description direction
- quote direction, not quote text unless researched and sourced
- cultural remark direction, not final button text unless researched and sourced
- audio mood, not a final track unless researched and licensed
- image direction
- whether it is a normal escalation, defeat moment, aftermath moment, or world-end moment
- any special constraints from the event spec

The `chaos-redux-super-events` prompt should ask the agent to:

- find a real quote using the repository web research workflow from `AGENTS.md`
- verify quote wording and attribution
- find a meaningful cultural remark, reference, allusion, or short line where appropriate
- follow copyright limits for songs, films, books, and other protected works
- find suitable public domain or clearly licensed audio
- document all sources, license notes, and uncertainties
- coordinate super-event image needs with `chaos-redux-event-assets`

Do not claim a quote, cultural reference, or audio track is usable without checking.

If a license or attribution is unclear, mark it as uncertain.

The super-event prompt must explicitly state that unresearched titles, button text, quotes, cultural remarks, slogans, lyric fragments, allusions, and audio choices are blockers. The implementation agent must not convert research directions, working labels, achievement names, asset names, or draft-like wording into final super-event localisation.

## Improvement-loop expansion specs

When `chaos-redux-improvement-loop` produces an expansion addendum, treat it as event-planning input. The addendum should be folded into the main spec pack with the same seriousness as the original user idea. Do not treat it as a loose suggestion if the parent accepted it.

An improvement-derived spec can be shaped freely. It does not need to copy the section order of this skill. It should still make the design concrete. A useful addendum explains the playable promise, the route or mechanic that feels shallow, the deeper player loop, the choices that change outcomes, the AI behavior, the visual and localisation needs, and the surfaces that must align.

## General localisation handoff

When a spec includes text-bearing content, give a localisation handoff, not final copy.

The handoff should list each needed text surface and describe its direction:

- event title direction
- event description direction
- option reaction direction
- news or report direction
- decision name and description direction
- focus name and description direction
- achievement title and description direction
- GUI label direction
- event-detail and event-log wording direction
- dynamic placeholders the coding agent should use
- research gates for quotes, slogans, songs, films, books, speeches, scriptures, proverbs, or other source-dependent references

The coding agent writes the final in-game text during implementation. The planning spec should not provide final prose for the coding agent to paste.

The planning agent should preserve the open structure of the addendum where that helps the idea. Use tables, route maps, prose, diagrams, or country package matrices only when they make the design easier to implement. Do not convert every improvement into a rigid checklist.

When an improvement addendum proposes formables, scripted GUI, animated sprites, animated portraits, or hidden routes, the final spec pack should carry those ideas into the relevant files instead of leaving them isolated. The core spec explains why the expansion matters. The decision and focus files explain how the player reaches it. The asset prompt explains the static and animated visual work. The coding prompt and goal prompt tell the implementation agent to wire and validate it.


## Specification folder convention

From now on, event source specifications should live in event-specific subfolders under `docs/specs/`.

Use this shape:

```text
docs/specs/<event_id>_<event_slug>_specs/
```

Examples:

```text
docs/specs/006_independence_wave_specs/006_independence_wave_spec.md
docs/specs/006_independence_wave_specs/006_independence_wave_focus_trees.md
docs/specs/006_independence_wave_specs/006_independence_wave_country_packages.md
```

Use `docs/plans/<event_id>_<event_slug>_plans/` for subagent plans, improvement addenda, audit follow-up notes, blocked reports, and implementation handoffs. Plans can become source design later, but the main agent should promote or merge them into `docs/specs/` when they are accepted as part of the final event design.

## 18. Output rules

The event specification itself should be created as Markdown files.

Full event specification output belongs under `docs/specs/<event_id>_<event_slug>_specs/`. This is the source-of-truth design folder for the event spec pack.

Subagent planning addenda, audit follow-up plans, implementation notes, and temporary handoffs belong under `docs/plans/<event_id>_<event_slug>_plans/`. The plans folder is a working area. Accepted plan content should be folded into the relevant spec under `docs/specs/` when the final source-of-truth spec is updated.

Do not create new event specs, addenda, prompt packages, or extracted handoffs under `docs/planning/`, `planning/`, or any other planning folder. If a prompt says "planning folder", interpret that as `docs/plans/` for subagent plans and `docs/specs/` for source specs unless the user explicitly provides a different path.

The spec file should contain only the event specification.

Do not put the asset prompt, super-event prompt, coding-agent prompt, or goal prompt inside the spec file.

Keep planning files readable as design handoffs, not implementation blueprints. Prefer route purpose, player-facing behavior, balance intent, asset direction, AI intent, and acceptance criteria. Avoid long technical tables, exact constant lists, full scripted-effect recipes, exhaustive file inventories, parser-level implementation notes, and detailed code wiring unless the user explicitly asks for a technical blueprint.

Create sequential files:

- `<event_id>_<event_slug>_spec_part_1_core.md`
- `<event_id>_<event_slug>_spec_part_2_<theme>.md`
- `<event_id>_<event_slug>_spec_part_3_<theme>.md`

Do not repeat earlier sections unless needed for clarity.


## 18.1 Final zip package requirement

The final output should be delivered as one zip file that contains every necessary file for the planning handoff.

The zip should include, when relevant:

- all spec Markdown files
- focus-tree path spec parts
- optional focus tree path diagrams or route sketches when useful
- asset prompt file
- super-event prompt file
- achievement prompt file
- coding-agent prompt file
- goal prompt file
- research notes or bibliography files
- any country package matrices, AI matrices, decision maps, or acceptance criteria files created separately

Do not make the user collect many loose files manually. The main deliverable should be a single zip package.

Use a clear package name such as:

`event_name_planning_package.zip`

The package should have a clean internal structure, for example:

```text
specs/
prompts/
focus_graphs/
research/
matrices/
```

The goal prompt inside the package must still be under 4000 characters.
The extracted zip should be placed in `docs/specs/<event_id>_<event_slug>_specs/` when it is the event source spec pack. If the zip contains only subagent plans, follow-up handoffs, or audits, place it under `docs/plans/<event_id>_<event_slug>_plans/`.

## 19. Final prompt files

Only after the full specification is complete, create separate prompt files outside the spec file and include them in the final zip package.

Required prompt files:

- `event_name_asset_prompt.md`
- `event_name_super_event_prompt.md` when the event has one or more super-events
- `event_name_achievement_prompt.md`
- `event_name_decision_mission_prompt.md` when the event has large decision or mission systems
- `event_name_coding_prompt.md`
- `event_name_goal_prompt.md`

The final answer should point to the final zip package as the deliverable and briefly summarize what the package contains.

### Asset prompt file

Create an asset prompt for `chaos-redux-event-assets`.

The prompt should cover all required visual assets, progression-state variants, final asset packaging, reference folders, source modes, and manifest requirements.

### Super-event prompt file

Create a super-event prompt for `chaos-redux-super-events` if the event has one or more super-events.

The prompt should cover title direction, description direction, quote research, cultural remark research, audio research, image direction, source documentation, licensing notes, and coordination with asset work.

The prompt must not provide unresearched final titles, button text, quotes, slogans, lyric fragments, cultural references, or final audio choices. Use research gates and role labels instead. It must tell the super-event researcher to produce the final text package only after source checks.

### Achievement prompt file

Create a separate achievement prompt file for the coding and asset agents.

The achievement prompt must include every planned achievement with id, title direction or working label, description direction, eligible countries, unlock conditions, disqualifiers, difficulty, hidden or visible status, why it is not trivial, icon direction, and all required tracking notes.

The achievement prompt should tell the implementation agent to inspect existing achievement patterns, implement the achievements, wire localisation and icons, create any required tracking flags or variables, document them, and avoid easy unlocks.

### Coding-agent prompt file

Create a coding-agent implementation prompt that summarizes the finished event spec.

The prompt must tell the coding agent to:

- implement the event according to the spec
- implement all mapped decisions, variants, evolutions, focus trees, custom tags, country packages, achievements, assets, and super-events included in the spec
- implement the mapped cost and sacrifice model, avoiding boring political power or command power only decisions when the spec calls for XP, equipment, manpower, stability, war support, fuel, supply, units, local support, foreign access, or other concrete costs
- implement focus trees according to the path design, with coherent non-linear branches, route locks, side paths, convergence nodes, hidden routes, focus filter tags or search categories, varied reward types, proper icons, final localisation written from the spec direction, AI behavior, event integration, and no filler shortcuts
- create the final exact focus layout and connections cleanly in implementation while preserving the spec's path logic
- implement every country package from the spec, including tag, history, names, cosmetic names, ideology names, ruling parties, leaders, leader changes, flags, route-specific identity changes, starting divisions, dynamic unit packages, force-growth decisions and focuses, volunteer routes, decisions, ideas, AI behavior, localisation, assets, and docs
- implement the full AI strategy matrix from the spec, including route preferences, foreign influence behavior, focus choices, unit-raising choices, decision choices, faction behavior, and high-chaos exceptions
- follow `AGENTS.md`
- follow `chaos-redux-events`
- use `chaos-redux-event-assets` if visual assets are required
- use `chaos-redux-super-events` if super-events are required
- write final player-facing event, decision, focus, achievement, GUI, event-detail, and spreadsheet-facing localisation from the direction in the spec. Do not expect the planning spec to provide finished copy
- treat unresearched super-event titles, button text, quotes, cultural remarks, slogans, allusions, and audio choices as blockers, not as implementation-ready localisation
- keep all Chaos Redux systems aligned
- report anything that cannot be implemented cleanly
- keep iterating until the full spec is implemented to its fullest extent
- avoid fallbacks, simplifications, temporary versions, and good-enough approximations
- not claim completion until the implemented files satisfy the spec

### Goal prompt file

Create a separate `/goal` prompt file.

The goal prompt must be less than 4000 characters.

The goal prompt should not contain the whole spec or all long instructions. It should point to the spec files and the other prompt files, then state the most important pass or fail requirements.

The goal prompt must tell the implementation agent to keep iterating until the goal is accomplished to its fullest extent. It must also say not to claim completion until the implemented files satisfy the spec.

A good goal prompt should include:

- the spec file path
- the coding prompt file path
- the asset prompt file path
- the super-event prompt file path when relevant
- the achievement prompt file path
- the required skills or docs to follow
- the top design non-negotiables
- the requirement to create all required static and animated assets, static fallbacks, tags, starting divisions, reinforcement pathways, non-linear focus trees based on the mapped paths, focus filter tags, decisions, evolutions, achievements, and docs
- the requirement to research and source final super-event titles, button text, quotes, cultural remarks, and audio through the proper super-event workflow when super-events exist
- the requirement to provide a concrete completion report

If the goal prompt is near 4000 characters, shorten it by pointing to files instead of repeating details.

## Formation and UI questions for planning passes

Before finishing a major event spec, ask:

- Can any country created or empowered by the event form a larger state later?
- Are there regional, ideological, hidden, or high-chaos formables that should be locked behind focuses, decisions, or events?
- Does each formable have concrete map requirements and a clear post-formation identity?
- Do formation rewards avoid free core spam, free war-goal spam, and instant runaway snowballing?
- Does the decision category need a scripted GUI, progress meter, custom window, or animated presentation?
- Has every important mechanic, formable route, high-chaos route, hidden reveal, faction board, patron network, crisis meter, and major transformation received an animation planning pass?
- Are animated sprites, leader portraits, particles, glow, float loops, warning pulses, selected states, hover states, or button states planned where they would make the mechanic clearer?
- If a major surface stays static, does the spec explain why motion would add clutter instead of clarity?
- Does the asset prompt include all static and animated UI pieces, frame-sheet needs, sprite names, state logic, and fallbacks?
- Does the goal prompt tell the implementation agent to verify formables, UI windows, animated sprites, frame-sheet handoffs, and fallbacks?

## 20. Final response checklist

The final response should include:

- spec file created
- spreadsheet row used when applicable
- repo context inspected
- event cluster role defined when relevant
- assets defined when needed, including country identity assets
- animation planning pass completed for important mechanics, custom UI, formables, route reveals, high-chaos states, and major leader transformations
- animated sprite and animated portrait needs mapped with static fallbacks, state logic, and `chaos-redux-frame-animation` handoff expectations when relevant
- historical flags, real symbols, and real leader portraits marked for sourced asset work when relevant
- super-event direction defined when needed
- general localisation handoff uses direction only for event titles, options, descriptions, decision text, focus text, achievement text, GUI labels, event-detail text, and spreadsheet-facing wording
- super-event text research gates used when final title, button text, quote, cultural remark, or audio has not been researched
- no unresearched super-event title, button text, quote, cultural remark, slogan, lyric fragment, or allusion presented as final localisation
- country package matrices created for new or modified countries when relevant
- starting force and reinforcement pathway plans created for new or transformed fighting countries, including dynamic scaling, template families, unit sources, and later reinforcement routes
- AI strategy matrix created for major events or country-creation events
- focus tree paths mapped clearly when the event creates playable or long-lived countries, with major routes, anchor focuses, mutual exclusions, rewards, and filter categories described
- every major focus tree written with clear path logic, not vague branch names
- every major focus tree includes a non-linear architecture map with trunk focuses, fork points, route locks, optional branches, convergence nodes, hidden routes, crisis branches, and late-game branches where relevant
- every major focus tree includes focus reward diversity and an idea audit when ideas or national spirits are used
- focus rewards include varied buildings, factories, military, industry, diplomacy, decisions, missions, identities, and mechanics where appropriate, not mostly new ideas
- final zip package created with all spec files, prompt files, route diagrams if used, research notes, and matrices
- focus tree files split into separate parts when the tree is too large for one file
- decisions and rare variants mapped when they exist
- event option tone mapped where event options exist, including irony, sarcasm, cultural remarks, humour, or deliberate plain severity
- evolution entry paths mapped when evolutions exist, including active-event evolution, pre-fire evolved opening, or a clear reason only one path applies
- decision and objective costs use varied resources, sacrifices, requirements, and risks instead of defaulting to political power or command power
- achievements mapped with difficult conditions, icon directions, and tracking notes
- ideology-specific names, cosmetic names, leader changes, and flag changes mapped when relevant
- unit-creating focuses and decisions mapped with requirements, template families, pressure effects, AI behavior, and blocked localisation notes when relevant
- uncertainties or blockers
- idea, spirit, decision, mission, and focus effects are strong enough to matter and not only conservative small modifiers
- downloadable link to the final zip package

## 21. Cleanup and quality gate

Before saving the final files, perform a strict review.

Reject the draft if it has any of these problems:

- vague placeholder decisions
- vague rare variants
- vague country paths
- custom tags without full country identity, assets, politics, leaders, flags, AI, and content expectations
- new or modified countries without country package matrices when they matter
- newly appearing crisis countries without dynamic starting unit packages or a clear reason why they start without troops
- country-created crisis specs without decisions, focuses, objectives, depots, volunteers, or faction systems that let those countries gain more units later
- new fighting countries without starting force plans, dynamic unit scaling, or reinforcement pathways
- long-lived new countries without dynamically scaled starting units or credible reinforcement routes
- newly appearing or transformed countries without mapped starting divisions, unit templates, equipment/manpower assumptions, and dynamic scaling factors
- countries with no designed way to gain, improve, convert, or coordinate more units through focuses, decisions, objectives, volunteers, depots, or faction mechanics
- generic repeated unit focuses or unit decisions that hand out identical divisions without story, route identity, or conditional requirements
- historical countries or movements with invented `$imagegen` flags when sourced historical flags should be used
- real historical leaders planned as generated portraits instead of sourced portraits
- playable countries without clear focus-tree path maps
- focus tree sections that list only branch names without explaining path logic, mutual exclusions, rewards, and connections
- focus tree plans that give only vague samples without enough path detail for implementation
- focus trees where most focuses grant a new idea or national spirit without a clear reason
- focus trees with repeated new ideas where modifying or upgrading an existing idea would be better
- focus trees without an idea audit when many ideas or national spirits are used
- focus rewards that are mostly political power, stability, war support, or repeated flat modifiers
- focus trees missing varied reward types such as factories, forts, anti-air, airbases, railways, supply hubs, units, decisions, missions, advisors, leaders, identities, claims, or diplomacy where those rewards would fit
- major focus paths without focus filter categories or search categories
- major focus trees without a focus filter taxonomy or path category table
- major countries without separate political, military, industry, diplomacy, and expansion or special-mechanic sections when those sections fit the country
- focus trees that are too small, generic, linear, or boring for the country role
- focus trees missing distinct political, industry, and expansion branches
- important country trees with isolated branches that do not affect each other
- major branches without clear payoff
- political branches that do not change politics, leaders, advisors, parties, laws, names, flags, or country identity where relevant
- industry branches that do not change the map, production, logistics, construction, or resources
- expansion branches that do not create claims, cores, war goals, leagues, protectorates, settlement decisions, or external diplomacy
- expansion routes without postwar handling
- industry routes without geographic grounding where relevant
- major routes without route-specific AI behavior or localisation tone
- large events without a special mechanic or clear reason for not needing one
- special mechanics without clearly named values
- mechanic values without dynamic focus, decision, mission, event, war, state-control, foreign-influence, or AI hooks
- important mechanic values without consistent colour identity or readable breakdowns
- focus trees or decision systems disconnected from the mechanic values they should affect
- event-created factions without goals, rules, membership logic, shared decisions, AI behavior, rewards, or success and failure states
- special mechanics without a defined player-facing presentation surface
- scripted GUI mechanics that would benefit from progress meters, status frames, variants, or animation but define only static text
- special mechanics that hide basic visible cause and effect
- generic playable country packages with no specific identity, map role, military style, economy, diplomacy, AI, or mechanic
- shared trees with no country-specific localisation, route names, decisions, AI weights, leaders, or rewards
- AI routes that can choose invalid, impossible, or unavailable branches
- important mechanic values scattered as magic numbers instead of script constants or documented tuning
- reward dump design used as the main pattern
- balance plans without exploit checks for free units, factory loops, equipment farming, influence farming, puppet abuse, war-goal spam, claim or core spam, advisor stacking, bypass abuse, or repeatable decision abuse
- decision systems that show every possible action at once instead of using phases, caps, priorities, pools, route locks, thresholds, or crisis filters
- factions that form too easily without minimum membership, crisis pressure, ideological compatibility, war state, or diplomatic preparation
- routes with no visible game evidence beyond hidden variables or tiny modifiers
- large trees with no early, middle, and late pacing
- routes with no tradeoff or failure state
- overuse of mutual exclusions where support branches should coexist
- localisation that reveals hidden effects, secret outcomes, or future surprises instead of visible baseline effects
- route-unlocked advisors that do not match route identity
- major focus trees without achievement hooks
- completion prompts missing a route coverage table requirement
- focus trees where unit rewards are repeated generic division spawns instead of route-specific military institutions, decisions, templates, or mobilization systems
- unit-granting focuses that exist only as filler or repeated free divisions with no story, route logic, or constraints
- major focus trees that read like one vertical checklist instead of a branching system
- focus tree sections without an architecture map or path plan showing route locks, optional branches, convergence points, hidden routes, crisis branches, and late-game branches where relevant
- branches where every focus simply follows the previous one without a strong story reason
- expansion trees that are only linear claim ladders instead of ideology, trauma, patron, military, economic, or chaos-driven ambitions
- evolutions that are really just ordinary stages
- evolution specs that do not define whether each evolution enters through active-event evolution, pre-fire evolved opening, or both
- active-event evolutions that do not state what changes immediately for existing active actors
- pre-fire evolved openings that do not state how the first firing changes before the ordinary baseline starts
- triggerable scenarios with prerequisites, such as Chaos Meter state, event progression, evolution unlocks, date gates, global flags, or prior campaign state, unless the user explicitly requested a locked scenario
- triggerable scenarios that do not create instant chaos directly from setup controls, intensity sliders, or scenario options
- fixed cooldowns or pressure values without dynamic factors
- decision, mission, or focus cost plans that rely mostly on political power or command power when concrete costs such as XP, equipment, manpower, fuel, stability, war support, supply, local support, foreign access, or unit commitments would fit better
- achievements missing from a major event spec
- achievements that unlock too easily or only reward the obvious route
- achievements without conditions, disqualifiers, icon directions, or tracking notes
- missing asset handoff for required assets
- major mechanic, formable, hidden reveal, high-chaos route, scripted GUI, or dramatic leader transformation with no animation planning pass and no reason for staying static
- animated asset plan that lacks static fallback, state logic, frame-sheet handoff, target surface, sprite names, or `chaos-redux-frame-animation` ownership
- missing asset coverage for country names, cosmetic identities, ideology flags, focus-route flags, leader changes, portraits, faction emblems, decisions, focuses, ideas, achievements, and UI where relevant
- missing AI route matrix for major events, country-creation events, or foreign-influence systems
- missing super-event handoff for required super-events
- final event titles, event options, event descriptions, report prose, news prose, decision names, decision descriptions, focus names, focus descriptions, achievement titles, achievement descriptions, GUI labels, event-detail text, or spreadsheet-facing wording written as pasteable localisation when the spec should give direction only
- sample, possible, temporary, or placeholder player-facing text included in the spec when the coding agent should write the final wording
- super-event title, button text, quote, cultural remark, slogan, lyric fragment, allusion, or audio choice written as final content without research and source documentation
- placeholder, sample, or working super-event text that could be pasted into localisation
- role labels, asset names, achievement titles, or prompt filenames reused as final super-event localisation without research
- coding prompt or goal prompt that lets unresearched super-event text be implemented instead of treating it as blocked
- goal prompt over 4000 characters
- goal prompt that tries to contain the whole spec instead of pointing to files
- missing final zip package containing all required spec files, prompt files, route diagrams if used, research notes, and matrices
- admin audit sections inside the spec
- major event ideas or spirits whose main effect is a tiny modifier with no meaningful strategic role
- obvious system plumbing repeated as design

The spec should be ambitious, detailed, researched, and usable. Do not stop at a conservative minimum when the idea supports more.
