---
name: hoi4-focus-trees
description: Use when designing, implementing, auditing, or fixing Hearts of Iron IV national focus trees.
---

# HOI4 Focus Trees

Use this skill when a task touches national focus trees, focus-tree loading, focus effects, focus layout, focus localisation, focus icons, focus AI, focus-tree documentation, or event-created country trees.

Use this skill together with:

- `AGENTS.md` for repository-wide rules
- `hoi4-events` when the tree belongs to an event
- `hoi4-decisions-missions` when focuses unlock, modify, or depend on decisions and missions
- `hoi4-feature-assets` when focus icons, leader portraits, flags, or idea icons are required
- `hoi4-improvement-loop` when a tree needs broader route depth or a near-completion anti-bloat pass
- `hoi4-subagents` before routing focus audits, improvement plans, or active small patches
- the installed `hoi4-agent-tools` MCP server for mandatory `hoi4.focus_inspect` and `hoi4.focus_render` work, plus bounded `hoi4.focus_rewrite` work. Use it to inspect, render, lint, compare, and improve focus-tree structure, then review every returned layout and diagnostic. Route every in-scope focus-weight audit through `hoi4_ai_probability_auditor`. If the required MCP route is unavailable, record the exact blocker and do not treat source-only review as equivalent. MCP does not replace required source review, wiki and vanilla documentation checks, repository validation, or parent review.


## Core design baseline

A strong focus tree should:

- introduce one or two manageable starting problems for a stable small or medium country
- begin with a small set of clear choices and reveal more complexity later
- use 35-day focuses for early strategic forks, focused reforms, and short opportunity windows
- give concrete rewards the player can feel immediately
- offer distinct strategies, including short-term power and long-term growth when the country supports that choice
- allow strong bonuses when the cost, duration, and aftermath are clear
- keep optional support investments skippable unless full commitment defines the route
- use existing systems such as diplomacy, production, supply, laws, compliance, stockpiles, and map control
- provide meaningful early action through war, diplomacy, internal politics, construction, intervention, or another active objective
- end major goals with a visible payoff such as territory, cores, a formable, a new government, a faction, or a lasting mechanic
- use a compact, symmetrical layout with short direct connectors that show the real route structure without visual tricks

At normal in-game zoom, a reviewer should be able to identify every supported major family from the render alone: opening trunk, politics and its forks, industry/economy, military with army/navy/air where relevant, diplomacy or faction, expansion or settlement, special mechanics, and late-game payoff. Give every visible focus one primary branch home or an explicit convergence role. If a branch cannot be understood without tracing every connector or reading every tooltip, redesign the route, names, icons, or layout before completion.

Large trees must use the current engine's focus search filters consistently. Give each focus accurate `search_filters` tags that match its primary role, and use Focus Navigation shortcuts for spatially separate major branch families. Each shortcut needs a localized label, distinct icon, stable branch anchor, useful pan/zoom target, and reveal-safe visibility. Navigation does not excuse interleaved or meaningless routes.

Reject trees that:

- overload the opening with penalties, currencies, national spirits, templates, or specialist mechanics
- expose too many branches before the player understands the country
- use long chains of small standalone modifiers as filler
- present a choice where one option dominates in nearly every plausible campaign
- create shallow ideology paths to fill a political quota
- leave meaningful content dependent on one foreign AI action
- delay the country's main premise through years of generic preparation
- use repeated or uncontrolled civil wars
- rely on automatic reward dumps as the main progression model
- encourage focus clicking without changing the player's build, objectives, decisions, or strategy
- fake non-linearity by offsetting a linear chain or routing long prerequisite lines around focuses
- use unnecessary ladder, staircase, zigzag, or decorative connector patterns to suggest depth
- allow overlapping focuses, overlapping connectors, intersecting path lines, or connectors that cross unrelated branches
- use long path lines when the same prerequisite can be shown with a shorter and cleaner placement

The duration and reward rules need context. A 35-day focus works when the click creates a real choice, action, event, requirement, or opportunity. A 5 percent modifier can be meaningful when it affects a sensitive statistic, supports a larger reward package, contributes to a visible stacking system, or completes an idea lifecycle. Repeated small standalone rewards remain a design defect. Early action can be military, diplomatic, political, industrial, or crisis-driven.

## 1. Required checks

Before editing focus files:

- Verify live schemas for `hoi4.reference_context`, `hoi4.reference_search`, `hoi4.reference_read`, and `hoi4.source_lookup`. Request focus context, locate exact rules, and read pertinent cited sections of National focus modding and installed game documentation. Retain source paths, lines, and revisions. Resolve any live `omittedSources` by raising the context limit or targeted search/read before claiming source coverage; `missing` denotes absent files. If a route is unavailable, use targeted local reads and record the exact gap; do not claim the MCP retrieval ran.
- Treat installed vanilla documentation as primary for syntax and inspect an exact vanilla focus precedent. Reference retrieval does not replace focus inspect/render evidence or the weighted-logic audit.
- Inspect existing repository focus trees and feature-created focus-tree loading patterns.
- Read `AGENTS.md`.
- Read `hoi4-decisions-missions` when focuses unlock decisions, timed objectives, missions, or dynamic mechanics.

Do not rely on memory for prerequisite behavior, layout behavior, AI syntax, or search filters.

## 2. Prerequisite semantics

HOI4 focus prerequisites are easy to invert.

This means OR:

```txt
prerequisite = { focus = a focus = b }
```

This means AND:

```txt
prerequisite = { focus = a }
prerequisite = { focus = b }
```

Use vanilla examples before changing complex prerequisite and mutual-exclusion structures.

## 3. Focus tree design purpose

A focus tree defines the playable identity of a country. Rewards should express that identity and change how the country plays.

A good focus tree gives the country:

- political routes
- ideology choices where the country identity supports them
- internal faction choices
- military development
- industry and logistics development
- diplomacy
- expansion or settlement policy
- special mechanics
- crisis or failure routes
- late-game ambitions
- AI route behavior
- visual identity through icons, names, leaders, flags, and ideas

A tree should not stay politically static unless the country is intentionally fixed by its concept.

## 4. Path-level implementation

Use path-level design unless the user explicitly asks for a focus-by-focus blueprint.

The spec usually defines:

- route families
- branch logic
- anchor focuses or focus groups
- mutual exclusions
- reward style
- idea lifecycles
- route end states
- AI behavior

The implementation agent owns:

- final focus count
- final focus names
- x/y positions
- exact prerequisites
- bypasses
- detailed focus connections
- clean in-game layout
- symmetrical branch geometry and centered route families
- the shortest clean connector path for every prerequisite relationship
- removal of overlapping focuses, intersecting lines, fake branches, and unnecessary layout ladders

The final tree must preserve the route logic and gameplay intent from the spec.


## 4.1 Route plausibility and ideology restraint

Do not build political paths to satisfy an ideology quota.

A political route needs a clear basis in at least one of these:

- the country's history, institutions, leaders, movements, or regional position
- the event or crisis that created the country
- a believable alternate-history divergence
- a researched ideological movement with enough local support to sustain a full route
- a high-chaos transformation with a clear reveal, internal logic, and gameplay identity

Two or three deep political routes are better than four shallow ideology routes. Do not add a five-focus communist, democratic, fascist, monarchist, or non-aligned branch only to claim that every ideology is represented.

A route can be unlikely. It still needs enough political actors, internal conflict, decisions, consequences, AI logic, and late-game purpose to feel complete. High-chaos routes can break ordinary plausibility when the route earns that break through events, mechanics, or campaign state.

When an ideology does not support a full route, leave it out, use it as a minor faction inside another route, or represent it through decisions and events.

## 5. Major country tree requirements

Large, playable, long-lived, or event-created countries need real focus trees.

A major tree should usually include:

- opening survival or state-building path
- main political path family
- internal faction path when relevant
- industry and economy path
- military path
- diplomacy path
- distinct expansion or settlement path
- special mechanic path
- hidden, crisis, or high-chaos path when relevant
- late-game ambition path

Do not collapse everything into one political ladder.


## 5.1 Lean opening, national constraints, and staged complexity

The opening should be understandable before the player studies the whole tree.

For a stable small or medium country, prefer zero to two focus-tree-owned starting national spirits. Use three only when each one represents a separate major problem or institution with a real lifecycle. Do not invent a long stack of national crises so the opening appears busy.

New crisis countries and collapsed states may start with several serious problems, but those problems should be consolidated into no more than three deep spirits under the normal spirit limit. Each starting spirit should change early priorities and have a visible route for mitigation, exploitation, transformation, or failure.

The starting army, navy, air force, production setup, and political situation should also be readable. Preserve real historical complexity for large powers and colonial empires. Do not add extra templates, fleets, laws, or mechanics when they do not create meaningful early choices.

Treat national weaknesses as route incentives. Resource scarcity, weak supply, low industrial capacity, poor access to steel or fuel, an obsolete navy, diplomatic isolation, or exposed borders should give the country a reason to act. The tree should offer distinct responses such as:

- build civilian capacity and import the missing resource
- invest in domestic substitution or extraction
- seek a foreign sponsor or commercial agreement
- use a military route to secure nearby supply
- accept a temporary shortage in exchange for another advantage

Do not erase the country's main constraint in the first focus. Let the player choose how to answer it.

Stage complexity across the opening:

1. Begin with one clear opening focus or a very small opening group.
2. Reveal two to four meaningful early choices in most trees.
3. Open larger route families after the player has seen the country's starting problem.
4. Reveal specialist, crisis, hidden, or high-chaos branches only when their conditions become relevant.

Use the numbers above as design guidance. A historically complex major can expose more choices when the layout groups them clearly.

The first few focuses should establish a real direction. Do not delay the first meaningful choice behind several generic political power, stability, research, or factory focuses.

### Opening choice test

Every early choice should change at least one of these:

- the player's immediate build plan
- the country's military timetable
- the route used to solve a resource or supply problem
- foreign alignment
- political leadership
- a special mechanic
- access to an early war, limited conflict, or diplomatic action
- the balance between short-term strength and long-term growth

If two early options lead to the same build and the same next focus, combine them or make their consequences more distinct.

### Focus duration and click value

Focus duration should match the size of the decision and the amount of play it creates.

Useful duration roles include:

- 7 days for a narrow policy switch, emergency response, route handoff, or reversible commitment
- 35 days for an early strategic fork, focused reform, event choice, or action that changes the next phase
- 70 days for a major program, normal institutional reform, or substantial construction and military work
- longer durations for sustained national commitments whose value and risk justify the wait

These are guidance bands. Follow vanilla and project precedent when a system needs another duration.

Do not split one 70-day reward into two 35-day focuses when the player gains no new choice, requirement, event, or mechanic between them. More clicks do not create more depth.

A short focus should earn its place through a meaningful choice, immediate action, new requirement, new event, temporary opportunity window, or route change. Reject short filler focuses that only divide one reward into several buttons.

## 5.2 Branch interaction and payoff

Political, industry, and expansion form the minimum branch set. Important countries should usually also have military, diplomacy, internal faction, intelligence or security, special mechanic, and late-game branches when their identity supports them.

Branches should not be isolated columns. Political choices should alter which expansion, industry, military, diplomacy, and decision paths are available. Industry should support military or expansion. Expansion should create political consequences. Diplomacy should affect both foreign aid and war options.

Every major branch needs a clear payoff.

Examples:

- a political branch can end in a new government, leader, ideology, law system, ruling party, or country identity
- an industry branch can end in a rebuilt economy, arsenal, resource system, railway authority, construction mechanic, or production network
- an expansion branch can end in a league, empire, federation, protectorate network, reunification, liberation order, regional settlement, or external war plan
- a military branch can end in a doctrine, special force, command structure, defensive network, or offensive system
- a diplomacy branch can end in recognition, neutrality, sponsor alignment, balanced sponsorship, faction creation, or anti-puppet protection

A focus should usually unlock new gameplay. Strong focus rewards unlock decisions, missions, units, advisors, leaders, laws, claims, cores, war goals, buildings, events, mechanics, route access, or AI behavior. Flat modifiers should support the main reward.


### Cross-branch utility

Branches that players often ignore should support the wider country loop.

Examples:

- a navy branch can improve commercial shipping, resource imports, convoy security, coastal industry, port construction, fuel access, or limited overseas operations
- an air branch can support reconnaissance, logistics, industrial protection, border control, or a special strike mechanic
- an intelligence branch can improve diplomatic leverage, target selection, resistance work, foreign investment, or limited-war preparation
- an industry branch can change the army the country can sustain instead of giving factories in isolation
- a military branch can unlock diplomatic intimidation, expeditionary support, border missions, or postwar integration tools

Cross-branch rewards should fit the country's identity. Do not add unrelated bonuses only to make a branch attractive.

A branch should offer value to players who are not already committed to its subsystem. The naval branch should have a reason to exist beyond giving naval bonuses to a player who had already decided to build a navy.

## 5.3 Country identity changes

Political routes should update the visible country package where relevant:

- leader
- leader portrait
- advisor roster
- high command
- ruling party
- party names
- ideology drift or ideology swap
- cosmetic name
- flag
- national spirits or idea lifecycle
- AI strategy
- diplomacy behavior

Leader changes require portrait handling. Route sourced real portraits and generated fictional, council, symbolic, or high-chaos portraits to `hoi4_portrait_creator`.

Expansion branches should create consequences. Claims, cores, and war goals should usually interact with diplomacy, factions, resistance, foreign guarantees, local leagues, legitimacy, threat, or postwar settlement decisions.

Industry branches should usually create visible map or production changes: factories, infrastructure, railways, supply hubs, forts, anti-air, airbases, dockyards, resources, production lines, or construction decisions.

Decision categories should evolve with focus progress. Early focuses may unlock basic decisions. Later focuses should add new targets, stronger actions, cheaper costs, new risks, or new mission families. A decision category should feel different after a route develops.

The fixed-purpose exception is narrow. A country is fixed-purpose only when its concept clearly cannot support normal politics, such as a death-state, machine-state, plague-state, or pure destruction actor. It still needs meaningful internal branches around method, hierarchy, economy, recruitment, expansion, and endgame.


## 5.4 Real branch depth standard

A branch does not count as a real branch unless it has enough content to change gameplay.

A real branch should usually include:

- several focuses or focus groups
- at least one mechanical unlock
- at least one meaningful choice, lock, fork, or route consequence
- at least one interaction with decisions, missions, ideas, leaders, units, buildings, diplomacy, map changes, AI, or events
- a clear end-state or payoff

Treat one or two generic focuses as a support node.

Large-country branches should not be shallow labels. If a tree says it has a political branch, industry branch, expansion branch, military branch, or diplomacy branch, each of those branches must have enough content to be felt in play.

### Branch closure and dead-end standard

Do not leave large focus trees full of dead ends. A terminal focus is acceptable only when it is a real capstone, convergence point, failure state, route lock, formable completion, settlement outcome, late-game ambition, or deliberately optional side payoff.

A focus line has failed if it stops after a small modifier, an isolated national spirit, a token equipment grant, a generic stability reward, or a decorative political power payout. Side branches can end, but their final focus must feed back into the country identity, a decision family, a mechanic value, a new unit path, a map change, an advisor set, an expansion route, or another visible route payoff.

Do not create one-focus or two-focus spurs just to fill space. Merge them into a nearby branch, turn them into decisions, make them part of an idea lifecycle, or build them into a real side path with a clear purpose.

Every major branch should answer what the player does after finishing it. Good answers include a stronger decision category, a new diplomatic stance, a changed army system, postwar integration work, a formable route, a crisis response loop, a new expansion policy, or a late-game convergence path. A finished branch that only leaves the player with passive numbers is not enough.

## 5.5 Route-specific AI and localisation tone

Every major route needs route-specific AI strategy. Generic focus weights alone are insufficient.

AI should understand:

- when to choose each political route
- when to pursue expansion
- when to prioritize industry
- when to join or form factions
- when to accept or reject foreign influence
- when to avoid high-risk paths
- when high-chaos routes are allowed
- when a route no longer makes sense because the campaign state changed

Every major route also needs a distinct localisation tone. A socialist route, military route, democratic route, nationalist route, religious route, machine route, death-state route, foreign client route, and high-chaos route should not sound the same.

Focus titles and descriptions should make the route identity clear without using generic filler language.

## 5.6 Geography, postwar handling, and advisor routing

Expansion branches must define what happens after victory.

War goals alone are not enough. Expansion routes should include postwar handling such as:

- cores
- claims
- puppet options
- protectorates
- occupation decisions
- integration missions
- border settlement events
- resistance risks
- diplomacy reactions
- local league consequences
- faction consequences
- achievement tracking

Industry branches should be geographically grounded. Important factories, resources, ports, railways, supply hubs, forts, anti-air, and airbases should be tied to relevant states or named regions when possible, not granted only as abstract country-wide bonuses.

Advisor unlocks should match route identity.

Examples:

- political routes unlock ideological advisors, ministers, councils, reformers, agitators, or internal faction figures
- industry routes unlock engineers, factory boards, construction trusts, resource planners, or railway administrators
- military routes unlock commanders, high command, training officers, doctrine theorists, or militia leaders
- diplomacy routes unlock envoys, negotiators, foreign liaisons, intelligence contacts, or recognition specialists
- high-chaos routes unlock strange councils, symbolic leaders, cult officers, machine boards, death-state authorities, or other route-specific figures

## 5.7 Achievement hooks and route coverage proof

Large focus trees should include achievement hooks for difficult route completions, rare branch combinations, expansion outcomes, successful internal reform, avoiding foreign dependency, forming leagues, surviving high-chaos paths, or completing hard late-game ambitions.

For every major focus tree, the completion report must include a route coverage table comparing the spec's required routes against implemented routes.

Required table columns:

| Required route | Implemented route or focus branch | Status | Notes |
| --- | --- | --- | --- |

Missing, renamed, merged, simplified, fallback, or replaced routes must be reported.


## 5.8 Route visibility, pacing, tradeoffs, and failure states

Read [`references/route-design.md`](references/route-design.md) before designing route visibility, pacing, tradeoffs, or failure states. It contains the complete standard for this section and its subsections.

## 5.9 Special mechanics, values, and faction rules

Large focus trees should interact with the event or country special mechanic. A major tree should not sit beside the mechanic without changing it.

Special mechanic values can include:

- legitimacy
- authority
- influence
- faction cohesion
- command obedience
- public panic
- regional control
- military readiness
- industrial capacity
- corruption
- foreign penetration
- religious authority
- revolutionary zeal
- balance-of-power position
- league cohesion
- sponsor pressure

Focuses should affect mechanic values directly when the country has such a mechanic. Political focuses can change legitimacy, balance of power, party strength, faction cohesion, or authority. Industry focuses can change industrial capacity, construction pressure, resource control, or economic recovery. Military focuses can change readiness, command obedience, recruitment, or defensive preparedness. Diplomacy focuses can change influence, recognition, sponsor pressure, faction cohesion, or foreign penetration. Expansion focuses can change threat, legitimacy, claims, resistance, local support, or faction goals.

Mechanic values should unlock or block content and create gameplay consequences. Values should affect focuses, decisions, missions, events, advisors, leaders, laws, factions, war goals, reforms, crises, or endings.

Important internal struggles should consider a balance of power or equivalent mechanic. Good balance-of-power conflicts include army versus parliament, factory councils versus ministries, monarchists versus republicans, foreign patrons versus national independence, security service versus civilian cabinet, or cult authority versus military command. Focuses and decisions should push the balance and unlock branch content, risks, leaders, laws, advisors, or events.

When a focus tree creates or leads a faction, league, bloc, compact, coalition, or alliance, that faction needs goals and rules. Define membership conditions, joining logic, refusal logic, expulsion logic where relevant, war goals, shared decisions, AI behavior, victory conditions, and failure conditions. Important event-created factions should usually have a mechanic such as cohesion, shared command, war council support, joint reserves, recognition, member confidence, sponsor pressure, or strategic goals.

Factions should not form too easily. Define minimum membership, crisis conditions, ideological compatibility, war pressure, diplomatic preparation, and regional logic.


## 5.10 Mechanic presentation, validity, and shared-tree rules

Special mechanics must be visible somewhere the player can understand them. A mechanic can appear in a decision category header, custom scripted GUI, progress meter, scripted localisation tooltip, focus tooltip, national spirit tooltip, or a combination of these.

When a mechanic is important enough for a custom scripted GUI, consider visual presentation beyond static text. Useful presentation can include progress bars, meter fill variants, state icons, status frames, warning frames, selected and locked variants, animated frames, or frame-by-frame visual changes that make the mechanic feel alive. The visuals should clarify the mechanic, not clutter it.

Special mechanics may hide future surprises. Basic cause and effect must remain clear. The player should understand why a visible value rose or fell, which public action changed it, and what broad type of response is available.

When a mechanic must remain visible while the player reads and chooses focuses, use a focus inlay window only when it materially improves tree-local decisions. Verify the current vanilla `focus_inlay_windows` syntax and precedent, reserve its footprint before final coordinates, and keep the inlay aligned with its GUI container and `inlay_window` tree attachment. It must not cover focuses, connectors, filters, Focus Navigation controls, or continuous focuses, and must update from real state with readable tooltips and visibility rules. Use `hoi4.focus_render` plus `hoi4.gui_inspect`/`hoi4.gui_render` for tree and inlay evidence; a clean focus graph alone is insufficient.

AI strategy must respect route validity. AI should not pick a branch that requires a missing state, dead sponsor, non-existent faction, unavailable ideology, disabled evolution, impossible border, or absent enemy. Invalid routes should be hidden, bypassed, or weighted to zero.

Every new playable country package needs a specific identity, starting problem, political direction, map role, military style, economy, diplomacy, AI behavior, and at least one mechanic or decision family that makes it play differently from other new countries.

Shared trees are allowed, but they must be adapted. Shared trees need country-specific localisation, route names, decisions, AI weights, leaders, rewards, icons, and scripted localisation where relevant. If every country using a shared tree reads and plays the same, the tree has failed.

When a route changes leader, ideology, faction, cosmetic name, flag, advisor roster, or special mechanic identity, the focus-tree spec and implementation should account for the needed visible assets and whether they are reused, sourced, generated, or blocked.

Important mechanic thresholds, caps, gains, losses, duration bands, AI weights, and scaling values should be centralized in script constants or a clearly documented tuning file. Do not scatter magic numbers across focus files, decisions, events, scripted effects, and scripted triggers.


## 5.11 Reward dumps and exploit checks

Avoid one-time reward dumps as the main design. A focus can give factories, units, equipment, resources, or buildings, but important focuses should often unlock a repeatable decision, timed mission family, production route, advisor, mechanic, route branch, or long-term gameplay system.

A one-time reward is acceptable when it fits the story and balance, but it should not be the main reward pattern of a large tree.

Before claiming completion, review the tree for exploits:

- free unit loops
- repeated factory rewards
- cheap cores or claims
- war-goal spam
- repeated equipment dumps
- advisor discount stacking
- influence farming
- focus bypass abuse
- repeatable decision abuse
- puppet or annexation shortcuts
- route switching to collect incompatible rewards

If an exploit is possible, fix it with limits, flags, dynamic costs, cooldowns, route locks, scripted triggers, AI limits, or one-time completion flags.


## 5.12 Decision category clutter control

Focus trees that unlock many decisions should also define how those decisions are staged.

Do not unlock every possible decision at once. Large decision systems should use phases, caps, priorities, regional pools, route locks, or crisis-state filters so the player sees the decisions that matter now.

A decision category should feel curated by the current country route and campaign state, not like a debug menu.

Focuses can control clutter by:

- unlocking early, middle, and late decision tiers
- opening regional decision pools one at a time
- hiding decisions whose route is no longer valid
- replacing basic decisions with stronger later versions
- limiting active mission count
- gating decisions behind visible mechanic values
- closing obsolete decisions after wars, settlements, or route changes

## 6. Distinct expansion branch

Every large focus tree should have a distinct expansion, reunification, liberation, federation, settlement, or regional ambition branch.

This branch must be separate from the main political tree and separate from the industry tree.

The expansion branch should actually change the map or diplomatic order. It should not be a line of generic bonuses.

Good expansion branch effects include:

- claims
- cores
- war goals
- border settlement decisions
- puppet or protectorate decisions
- guarantees
- faction invitations
- league or bloc formation
- liberation decisions
- regional intervention decisions
- peace or treaty events
- state transfer events
- postwar settlement missions
- outside-border ambition routes when the country identity supports them

Expansion should follow the country's ideology, geography, trauma, economy, military doctrine, foreign patron, crisis state, or special identity.

Bad expansion branches:

- five focuses that only add political power
- a straight list of generic claims with no diplomacy or consequences
- claims hidden inside the political branch with no separate strategic route
- expansion focuses that do not unlock wars, claims, cores, decisions, treaties, or interventions


## 6.1 Early action and limited-war architecture

A major playable tree should offer meaningful active play early enough to affect the campaign when the country's identity supports it. Active play can mean a limited war, border settlement, intervention, expedition, foreign-aid race, internal crisis, regional league, or another action with real risk.

Do not force every country into an early war. Pacifist, defensive, isolated, or institution-building countries can use other early active goals. Do not make the player wait through years of filler before the tree begins doing what its premise promises.

When an early expansion route would otherwise create an unreasonable total war, consider a limited-war system.

A limited-war route must define:

- the exact target states or objectives
- who can participate
- what causes outside escalation
- how guarantees and faction membership are handled
- the conditions for an early peace
- what each side keeps after the settlement
- what happens when the attacker exceeds the limited objective
- what happens when the defender reverses the war
- AI willingness and AI peace behavior
- cleanup for war goals, missions, flags, participants, and temporary modifiers
- postwar compliance, resistance, integration, recognition, or border-settlement work

The early route can trade long-term strength for immediate action. It can use temporary military bonuses, economic exhaustion, diplomatic backlash, lower legitimacy, or restricted objectives to keep the choice meaningful.

A limited war should produce a clear campaign goal and a satisfying visible payoff. The route can culminate in a formable, regional settlement, restored border, resource corridor, protectorate system, or other identity change after the player proves control and completes the postwar work.

## 7. Political depth

Large focus trees must alter politics directly.

Political branches should include meaningful changes such as:

- ideology shifts
- ruling party changes
- party popularity changes
- leader changes
- new advisors
- advisor cost discounts
- ministers or high command unlocks
- laws
- scripted leader traits
- balance-of-power changes
- internal faction decisions
- coups, compromises, elections, councils, juntas, congresses, regencies, cult offices, syndicates, committees, or directorates
- cosmetic country names
- flag changes
- focus-route names
- ideology-specific party names
- local support or legitimacy mechanics

A country should not remain politically static through a major focus tree unless that is the explicit concept.

Examples of route families:

- socialism
- democratic legalism
- nationalism
- monarchism
- military government
- anarchism
- religious government
- foreign client government
- revolutionary council
- security directorate
- high-chaos cult
- machine or factory state
- death-state actor

Fixed-purpose chaos countries can have narrower political design. For example, a country whose entire identity is death, plague, machine rule, or total destruction may have one ideological purpose. Even then, its tree should still create mechanical choices inside that purpose, such as doctrine, expansion method, internal hierarchy, recruitment, economy, and endgame ambition.


## 7.1 Leader and institution customization

Some routes should let the player build a leader, regency, council, cabinet, doctrine, or governing institution through several choices.

A customization sequence can use events, focuses, decisions, or a dedicated mechanic to select traits and priorities. Useful dimensions include construction, military command, diplomacy, reform, logistics, research, legitimacy, or faction management.

A strong customization system should:

- give two or three clear choices at each stage
- let repeated investment in one theme unlock a specialist threshold bonus
- allow mixed choices to create a generalist
- cap or price stacking so one combination does not become the automatic answer
- update the visible leader, traits, portrait, institution, or national spirit
- give AI route-specific profiles instead of random trait stacking
- preserve a regent, council, or interim authority as a valid final choice when the route supports it

Do not use leader customization as a menu of small percentage bonuses. The selected traits should change build priorities, decisions, route access, or how the country handles its main problem.

Use this system only when leadership construction is part of the route fantasy.

## 7.2 Civil war restraint and controlled internal conflict

Do not use a vanilla civil war as the default climax for political disagreement.

Prefer controlled alternatives when they fit:

- balance-of-power struggle
- coup attempt
- election crisis
- timed loyalty contest
- state-by-state allegiance
- targeted regional secession
- negotiated settlement
- purge or officer removal
- rival council mechanic
- limited mutiny
- leader replacement
- staged takeover through decisions and events

A full civil war is justified when territorial control and military command are central to the route.

When a focus tree uses a civil war:

- determine the participating states through clear route logic
- control division transfer where the engine and project patterns allow it
- tell the player which areas and forces are at risk
- avoid arbitrary loss of half the army
- define stockpile, navy, air force, commander, subject, and faction handling
- define postwar reintegration and the fate of surviving units
- give AI a viable war plan
- clean up all temporary tags, flags, decisions, ideas, and route locks
- make the result affect later politics instead of returning immediately to the same tree state

Do not repeat several similar civil wars inside one tree unless repeated fragmentation is the country's central mechanic. Use different internal-conflict forms for different political struggles.

## 8. Focus reward diversity

Read [`references/rewards-and-ideas.md`](references/rewards-and-ideas.md) before writing focus rewards, ideas, or national spirits. It contains the complete standard for this section and its subsections.

## 9. Idea lifecycle

Read [`references/rewards-and-ideas.md`](references/rewards-and-ideas.md) before writing focus rewards, ideas, or national spirits. It contains the complete standard for this section and its subsections.

## 10. Focuses and decisions must interconnect

Focus trees and decision systems must not feel separate.

Focuses should unlock, modify, improve, or restrict decisions and missions.

Examples:

- expansion focuses unlock decisions to send declarations, issue ultimatums, create leagues, sponsor border incidents, demand territory, form protectorates, or start settlement talks
- industry focuses unlock decisions to build factories, repair infrastructure, expand railways, construct supply hubs, build forts, add anti-air, or run construction programs
- military focuses unlock decisions to raise reserves, train special units, convert militias, guard borders, seize depots, or prepare offensives
- diplomacy focuses unlock recognition missions, aid corridors, foreign advisors, volunteer requests, anti-puppet clauses, or sponsor-balancing decisions
- political focuses unlock elections, councils, purges, compromises, advisor appointments, party campaigns, reform missions, or leader-change events
- League or faction focuses unlock shared reserves, common front missions, member votes, joint war declarations, intervention forces, or regional arbitration decisions

A focus that unlocks a decision family should state:

- which decisions or mission family it unlocks
- what new choices it adds
- what costs or risks those decisions use
- how AI uses them
- how they interact with the branch's later focuses

A decision family unlocked by focuses should reference the relevant route in docs and localisation.

## Focus routes that lead to formable nations

A focus tree can prepare, reveal, enable, or stabilize a formable nation, but the final formation should usually be handled by a decision when state control matters. Use focuses to build the political claim. Use decisions to verify the map and perform the formation.

A formation route in a focus tree should define:

- narrative reason the country can claim the formable identity
- route family that unlocks the claim
- focuses that reveal the formation decision
- focuses that mark required regions, start border commissions, invite subjects, sponsor plebiscites, or prepare integration
- mutually exclusive formable routes
- compatible support branches, such as industry, army, diplomacy, intelligence, or legitimacy
- hidden formables that require rare events, special leaders, secret focuses, high chaos, or unusual state control
- post-formation focuses that stabilize the new country, integrate regions, resolve opposition, change capital, update advisors, or expand claims
- AI route behavior and AI safety checks
- asset needs, including flags, cosmetic tags, leader portraits, focus icons, decision icons, and possible animated route portraits

Do not make a formable route a linear claim ladder by default. The best formation routes usually combine legitimacy, state control, diplomatic recognition, military readiness, local integration, and a visible identity change.

## Formation route architecture

When mapping a focus tree that can form countries, include a formation lane or route overlay in the architecture map.

Useful formation lane structure:

1. claim preparation focus group
2. required-region survey or claim office focus group
3. diplomacy or internal legitimacy focus group
4. decision unlock focus
5. map-control decision handled in a decision category
6. formation event or news event
7. post-formation stabilization branch
8. late ambition or hidden second-stage formable, if justified

The tree should state whether the formable is:

- visible from game start
- revealed by a normal focus
- revealed by a rare event
- hidden until the player controls key states
- hidden behind ideology, leader, chaos tier, patron, or secret route
- available only if another country does not exist
- available only if the forming country has the correct release origin or event origin

For shared event-created trees, formables must use origin and package checks so unrelated countries do not receive the wrong route.

## Focus rewards tied to formation decisions

Focus rewards can:

- unlock formation decisions
- add claims on required regions
- reduce integration costs
- add temporary legitimacy for a formation crisis
- reveal hidden state requirements in a tooltip
- invite subjects or allies to join the formation
- open border plebiscite missions
- create a custom scripted GUI meter for formation progress
- unlock post-formation branch content
- switch to animated leader portraits or route emblems after a dramatic transformation

Focus rewards should not:

- grant all required states without gameplay reason
- create a formable without checking map requirements
- give instant full cores on large conquered regions without integration work
- bypass route locks or hidden formable conditions
- leave obsolete pre-formation focuses visible after the formation completes

## Animated leader portraits and visual route payoffs

Focus trees should consider animated portraits or animated route emblems for major political transformations. Use them for route payoffs such as a supernatural leader reveal, a restored dynasty, a revolutionary cult, a final formable proclamation, or a high-chaos state identity.

Animated portraits need static fallbacks. They should be assigned through the same leader, character, or cosmetic identity logic as the route itself. `hoi4_portrait_creator` owns the sourced or generated base portrait before `hoi4-frame-animation` creates the animation package.

Do not make every leader animated. Animation should signal a special route, a high-chaos identity, a super-event-level transformation, or a rare hidden outcome.

## 11. Route locks and mutual exclusions

Use mutual exclusions when the country's identity changes.

Good mutual exclusions include:

- socialism versus nationalism versus democratic legalism
- civilian government versus military junta
- foreign client path versus independent path
- death cult takeover versus normal republic
- local league leadership versus isolationism
- negotiated settlement versus expansion war

Do not use mutual exclusions for branches that should logically coexist, such as army and industry.

When a route becomes impossible, use bypasses or availability logic cleanly.


A route must not depend forever on one external country taking one scripted action.

If a branch expects an invasion, alliance offer, foreign conference, sponsor decision, or historical war, define at least one safe resolution:

- an alternate valid aggressor or sponsor
- a campaign-state trigger that represents the same pressure
- a timed reveal after the historical opportunity passes
- a player decision that provokes or requests the interaction
- a bypass into the appropriate aftermath route
- a clean route closure when the premise can no longer happen

Do not leave a meaningful branch permanently inaccessible because one AI country chose another focus.

External-event gates need AI and multiplayer checks. Verify that alternate history, missing countries, dead leaders, faction changes, and player-controlled foreign actors cannot strand the tree.

## 12. Layout rules

Read [`references/layout-rules.md`](references/layout-rules.md) before placing focuses, changing coordinates, or reviewing a rendered tree layout. It contains the complete standard for this section and its subsections.

## 13. Event-created versus existing countries

When an event creates or releases a country, set a flag showing that the event created that country.

Only load or replace a runtime focus tree if the event actually created the country.

Existing countries with their own meaningful tree should usually receive additive crisis branches, decisions, ideas, or events. Blind tree replacement needs explicit design support.

For every event-created country, verify:

- tag
- localisation
- flags
- leader or council
- starting ideas
- starting units
- focus tree assignment
- AI
- decisions
- assets
- docs

## 14. AI behavior

Every major route needs AI behavior.

AI should consider:

- ideology
- war state
- stability
- strength
- local support
- foreign influence
- faction membership
- crisis pressure
- available territory
- nearby enemies
- route compatibility
- high-chaos conditions
- player proximity

Avoid flat AI weights when campaign state matters.

For every in-scope focus-weight audit, route baseline and post-patch comparison evidence through `hoi4_ai_probability_auditor`. Establish named baseline campaign scenarios before any patch with `hoi4.probability_inspect`, and `hoi4.probability_analyze` with `analysis: "sweep"` as appropriate. The focus owner chooses the intended balance and applies the source patch; the auditor remains read-only. After the patch, require `hoi4.probability_analyze` with `analysis: "compare"` against the same named scenarios and use `hoi4.probability_analyze` with `analysis: "simulate"` only for explicitly declared uncertain inputs. Use `hoi4.probability_analyze` with `analysis: "render"` when a ranking, matrix, sensitivity, comparison, or unresolved view is clearer than a compact trace. The focus adapter models the verified independent score race, not weight divided by the sum of weights. Supply the complete available-focus pool and declare prerequisite, bypass, strategy, and external factors; keep anything the analyzer cannot resolve visible as uncertainty. Use the result as balance evidence while this skill retains ownership of route design and tuning decisions.

AI should not accidentally choose suicidal or nonsensical routes just because they are visible.

## 15. Localisation and icons

Every focus needs:

- title localisation
- description localisation
- completion reward tooltip
- icon assignment
- AI behavior when relevant

Every political route needs localisation that makes the route identity clear.

Leader changes require leader portraits. Route both sourced real portraits and generated fictional or symbolic council portraits to `hoi4_portrait_creator`.

Flag or cosmetic-name changes require flag and localisation coverage.

Focus-tree assets must not reuse one uniform colour palette across the whole tree. Political routes, military routes, industry routes, diplomacy routes, expansion routes, crisis routes, and hidden or high-chaos routes should use visibly distinct palette families where their identities differ. Separate branches should not look like recoloured copies of the same icon set.

Do not solve asset variety by taking the same composition and changing only its hue. Vary subject matter, framing, lighting, contrast, symbols, materials, and background treatment while keeping the tree visually coherent and readable in the HOI4 interface.

## Improvement addenda and formation routes

When an improvement addendum deepens a focus tree, preserve the route idea before adding nodes. Aim for a sharper country identity, stronger branch interaction, clearer route locks, better rewards, stronger AI, and more visible consequences.

Formation routes should usually combine focus preparation with a decision that verifies state control. Focuses can discover old claims, call a congress, unlock a seal, prepare integration, recruit elites, expose a hidden identity, or open the formation decision. The decision then checks the map and performs the formation.

Hidden formables can be routed through secret focuses, events, leader changes, chaos tiers, ancient artifacts, internal factions, or custom GUI investigation. Hidden content should still have a full implementation handoff. It needs reveal logic, visibility rules, localisation, assets, AI handling, post-formation gameplay, and disqualifiers.

Animated leader portraits and animated route emblems should be reserved for major transformations. Use them when the route payoff changes the country's identity, reveals a high-chaos leader, forms a new state, or completes a dramatic ideological break. Keep a static fallback and ensure the animation has a clear trigger and cleanup state.

## Subagent patches for focus trees

Focus tree subagents are active small-patch agents by default inside the current task scope. They can patch prerequisite fixes, mutual exclusion fixes, bypasses, route locks, AI weights, icon references, focus filters, localisation keys, small reward variety, existing decision hooks, and existing formable unlock hooks without waiting for a separate permission prompt.

They should not redesign a whole tree, add a full route family, create a new formable chain, or change the country identity. When the tree needs broader depth, they should write an improvement plan under `docs/plans/<event_id>_<event_slug>_plans/` and leave implementation to the main agent.

Every patch must write a handoff with changed files, changed focus ids, route behavior before and after, meaningful validation, skipped task-specific validation, and remaining route risks.

## 16. Documentation and audit

For large focus-tree work, update documentation.

Include:

- tree id
- country or countries using it
- before and after focus count
- route families
- mutual exclusions
- major decisions unlocked
- idea lifecycle
- reward categories
- AI behavior
- icons or icon families
- remaining blockers
- opening structure and first meaningful choices
- national constraints and the route answers they create
- focus duration logic
- temporary power windows and aftermath
- interactive focus requirements
- limited-war rules when used
- civil-war handling when used
- leader or institution customization when used

Before completion, audit:

- duplicate focuses
- duplicate ideas
- missing icons
- missing localisation
- missing AI
- missing route decisions
- missing expansion branch
- missing political change
- missing branch payoff
- isolated branches that do not interact
- expansion branch without claims, cores, war goals, diplomacy, leagues, or settlements
- industry branch without map, construction, logistics, production, or resource effects
- generic flat rewards
- fairy-dust reward patterns made from many tiny bonuses
- authored gameplay values that are not rounded to multiples of 5 without a documented exception
- routes that can hold more than three focus-tree-created national spirits at once
- focus-tree asset sets that reuse the same colour palette across distinct branches
- dead-end branches with no capstone, convergence, or follow-up gameplay
- national spirits that are too easy to earn for their importance
- national spirits that have no lifecycle, route commitment, mechanic hook, or decision hook
- layout readability
- overlapping focus boxes, overlapping connectors, or intersecting path lines
- long prerequisite lines that could be shortened by repositioning focuses
- fake non-linearity created by offsetting an otherwise linear chain
- unnecessary ladder, staircase, zigzag, or decorative detour layouts
- asymmetric sibling branches or off-center route families without a real structural reason
- unnecessary starting spirit stacks or military setup complexity
- an opening that exposes too many choices before the player understands the country problem
- first meaningful choices delayed behind filler focuses
- political routes added only to satisfy an ideology quota
- focus durations that do not match the decision or reward
- several consecutive focuses with no choice, requirement, event, map objective, or mechanic interaction
- national constraints erased before they shape a route
- underused branches with no cross-branch utility
- temporary bonuses with no stated window, cost, or aftermath
- permanent extreme policies with no exit when an exit should exist
- interactive gates that are arbitrary, unclear, or impossible to pursue intentionally
- external-event gates that can permanently strand a branch
- optional side investments made mandatory without a route reason
- early-war routes that force total war when a limited objective is intended
- limited wars without peace, escalation, AI, cleanup, or postwar rules
- repeated or uncontrolled civil wars
- leader customization that produces one dominant trait stack

## 17. Completion rules

Read [`references/completion-rules.md`](references/completion-rules.md) before claiming any focus-tree work is complete. It contains the complete standard for this section and its subsections.

