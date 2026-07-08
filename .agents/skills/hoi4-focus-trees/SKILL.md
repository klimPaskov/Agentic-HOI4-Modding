---
name: hoi4-focus-trees
description: Use when designing, implementing, auditing, or fixing Hearts of Iron IV national focus trees.
---

# HOI4 Focus Trees

Use this skill when a task touches national focus trees, focus-tree loading, focus effects, focus layout, focus localisation, focus icons, focus AI, focus-tree documentation, or feature-created country trees.

This skill is the detailed focus-tree source of truth for `AGENTS.md`. Keep the root `AGENTS.md` concise and put reusable focus-tree design, implementation, audit, and completion standards here.

Use this skill together with:

- `AGENTS.md` for repository-wide rules
- `hoi4-events` when the tree belongs to an event
- `hoi4-decisions-missions` when focuses unlock, modify, or depend on decisions and missions
- `hoi4-feature-assets` when focus icons, leader portraits, flags, or idea icons are required

## 1. Required checks

Before editing focus files:

- Read the offline Paradox wiki National focus modding page.
- Read relevant vanilla documentation from `<HOI4_INSTALL_DIR>/documentation`.
- Inspect vanilla focus files for syntax and layout precedent.
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

A focus tree is not a list of rewards. It is the playable identity of a country.

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

The final tree must preserve the route logic and gameplay intent from the spec.

## 5. Major country tree requirements

Large, playable, long-lived, or feature-created countries need real focus trees.

A major tree should usually include:

- opening survival or state-building path
- main political path family
- internal faction path when relevant
- industry and economy path
- military path
- diplomacy path
- distinct expansion or settlement path
- special mechanic path
- hidden, crisis, or extreme-route path when relevant
- late-game ambition path

Do not collapse everything into one political ladder.


## 5.2 Branch interaction and payoff

Political, industry, and expansion are the minimum branch families, not a full large-country tree. Important countries should usually also have military, diplomacy, internal faction, intelligence or security, special mechanic, and late-game branches when their identity supports them.

Branches should not be isolated columns. Political choices should alter which expansion, industry, military, diplomacy, and decision paths are available. Industry should support military or expansion. Expansion should create political consequences. Diplomacy should affect both foreign aid and war options.

Every major branch needs a clear payoff.

Examples:

- a political branch can end in a new government, leader, ideology, law system, ruling party, or country identity
- an industry branch can end in a rebuilt economy, arsenal, resource system, railway authority, construction mechanic, or production network
- an expansion branch can end in a league, empire, federation, protectorate network, reunification, liberation order, regional settlement, or external war plan
- a military branch can end in a doctrine, special force, command structure, defensive network, or offensive system
- a diplomacy branch can end in recognition, neutrality, sponsor alignment, balanced sponsorship, faction creation, or anti-puppet protection

A focus should usually unlock new gameplay, not only stats. Strong focus rewards unlock decisions, missions, units, advisors, leaders, laws, claims, cores, war goals, buildings, events, mechanics, route access, or AI behavior. Flat modifiers are supporting rewards, not the main design.

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

Leader changes require portrait handling. Real leaders use sourced portraits. Fictional leaders, councils, symbolic leaders, or extreme-route authorities can use generated portraits through the asset skill.

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

A branch made of one or two generic focuses is not a branch. It is a support node.

Large-country branches should not be shallow labels. If a tree says it has a political branch, industry branch, expansion branch, military branch, or diplomacy branch, each of those branches must have enough content to be felt in play.

### Branch closure and dead-end standard

Do not leave large focus trees full of dead ends. A terminal focus is acceptable only when it is a real capstone, convergence point, failure state, route lock, formable completion, settlement outcome, late-game ambition, or deliberately optional side payoff.

A focus line has failed if it stops after a small modifier, an isolated national spirit, a token equipment grant, a generic stability reward, or a decorative political power payout. Side branches can end, but their final focus must feed back into the country identity, a decision family, a mechanic value, a new unit path, a map change, an advisor set, an expansion route, or another visible route payoff.

Do not create one-focus or two-focus spurs just to fill space. Merge them into a nearby branch, turn them into decisions, make them part of an idea lifecycle, or build them into a real side path with a clear purpose.

Every major branch should answer what the player does after finishing it. Good answers include a stronger decision category, a new diplomatic stance, a changed army system, postwar integration work, a formable route, a crisis response loop, a new expansion policy, or a late-game convergence path. A finished branch that only leaves the player with passive numbers is not enough.

## 5.5 Route-specific AI and localisation tone

Every major route needs route-specific AI strategy. AI should not only have generic focus weights.

AI should understand:

- when to choose each political route
- when to pursue expansion
- when to prioritize industry
- when to join or form factions
- when to accept or reject foreign influence
- when to avoid high-risk paths
- when extreme-route routes are allowed
- when a route no longer makes sense because the campaign state changed

Every major route also needs a distinct localisation tone. A socialist route, military route, democratic route, nationalist route, religious route, machine route, death-state route, foreign client route, and extreme-route route should not sound the same.

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
- extreme-route routes unlock strange councils, symbolic leaders, cult officers, machine boards, death-state authorities, or other route-specific figures

## 5.7 Achievement hooks and route coverage proof

Large focus trees should include achievement hooks for difficult route completions, rare branch combinations, expansion outcomes, successful internal reform, avoiding foreign dependency, forming leagues, surviving extreme-route paths, or completing hard late-game ambitions.

For every major focus tree, the completion report must include a route coverage table comparing the spec's required routes against implemented routes.

Required table columns:

| Required route | Implemented route or focus branch | Status | Notes |
| --- | --- | --- | --- |

Missing, renamed, merged, simplified, fallback, or replaced routes must be reported.


## 5.8 Route visibility, pacing, tradeoffs, and failure states

A major route should leave visible evidence in the game. This can include map changes, new decisions, new units, new advisors, changed leader, changed flag, changed cosmetic name, new faction behavior, new focus availability, changed diplomacy, or a visible mechanic. A route that only changes hidden variables or tiny modifiers is not meaningful.

Large focus trees should have early, middle, and late pacing.

- Early focuses solve survival, first institutions, first units, first industry, and basic identity.
- Middle focuses create route mechanics, meaningful choices, decision families, military systems, diplomacy, and branch interaction.
- Late focuses deliver major payoffs, expansion, faction or League outcomes, extreme-route routes, postwar settlement, or international-order ambitions.

Every major route should have a tradeoff. A military route may reduce freedom or legitimacy. A foreign-aid route may increase dependency. An expansion route may create resistance or foreign backlash. An industry route may consume civilian capacity or weaken short-term defense. A extreme-route route may give power while damaging stability, diplomacy, or normal politics.

Do not overuse mutual exclusions. Mutually exclusive paths should represent real identity changes, strategic commitments, or incompatible institutions. Support branches like industry, army, diplomacy, and logistics should usually coexist unless the route logic says otherwise.

Important routes should define failure states. A failed political reform can empower radicals. Failed expansion can trigger backlash or settlement. Failed industry can create dependency. Failed foreign-aid balancing can create a client state. Failed military centralization can create rogue generals or militias.

Focus and decision localisation should tell the player the visible baseline effect of the route or action. It should not reveal hidden effects, secret outcomes, hidden variables, or future surprises. The player should understand what the focus visibly does, such as moving toward military rule, opening an industry program, unlocking a public diplomatic route, forming a League office, or preparing border claims, without being told about hidden follow-up effects.


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

Mechanic values should unlock or block content. A value should not only be a number. Values should affect focuses, decisions, missions, events, advisors, leaders, laws, factions, war goals, reforms, crises, or endings.

Important internal struggles should consider a balance of power or equivalent mechanic. Good balance-of-power conflicts include army versus parliament, factory councils versus ministries, monarchists versus republicans, foreign patrons versus national independence, security service versus civilian cabinet, or cult authority versus military command. Focuses and decisions should push the balance and unlock branch content, risks, leaders, laws, advisors, or events.

When a focus tree creates or leads a faction, league, bloc, compact, coalition, or alliance, that faction needs goals and rules. Define membership conditions, joining logic, refusal logic, expulsion logic where relevant, war goals, shared decisions, AI behavior, victory conditions, and failure conditions. Important feature-created factions should usually have a mechanic such as cohesion, shared command, war council support, joint reserves, recognition, member confidence, sponsor pressure, or strategic goals.

Factions should not form too easily. Define minimum membership, crisis conditions, ideological compatibility, war pressure, diplomatic preparation, and regional logic.


## 5.10 Mechanic presentation, validity, and shared-tree rules

Special mechanics must be visible somewhere the player can understand them. A mechanic can appear in a decision category header, custom scripted GUI, progress meter, scripted localisation tooltip, focus tooltip, national spirit tooltip, or a combination of these.

When a mechanic is important enough for a custom scripted GUI, consider visual presentation beyond static text. Useful presentation can include progress bars, meter fill variants, state icons, status frames, warning frames, selected and locked variants, animated frames, or frame-by-frame visual changes that make the mechanic feel alive. The visuals should clarify the mechanic, not clutter it.

Special mechanics can hide future surprises, but they should not hide basic cause and effect. The player should understand why a visible value rose or fell, which public action changed it, and what broad type of response is available.

AI strategy must respect route validity. AI should not pick a branch that requires a missing state, dead sponsor, non-existent faction, unavailable ideology, disabled escalation variant, impossible border, or absent enemy. Invalid routes should be hidden, bypassed, or weighted to zero.

A new playable country package must not be generic. It needs a specific identity, starting problem, political direction, map role, military style, economy, diplomacy, AI behavior, and at least one mechanic or decision family that makes it play differently from other new countries.

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
- extreme-route cult
- machine or factory state
- death-state actor

Fixed-purpose special feature-created countries can have narrower political design. For example, a country whose entire identity is death, plague, machine rule, or total destruction may have one ideological purpose. Even then, its tree should still create mechanical choices inside that purpose, such as doctrine, expansion method, internal hierarchy, recruitment, economy, and endgame ambition.

## 8. Focus reward diversity

Focus rewards must be concrete and varied.

Do not make most focuses grant:

- a new idea
- political power
- stability
- war support
- small flat modifiers
- generic equipment
- generic manpower

Use effects that change play.

Good rewards include:

- civilian factories
- military factories
- dockyards
- forts
- coastal forts
- anti-air
- radar
- airbases
- infrastructure
- railways
- supply hubs
- resources
- building slots
- production lines
- equipment stockpiles
- unit templates
- route-specific units
- manpower recovery decisions
- commanders
- advisors
- advisor discounts
- laws
- technologies or research bonuses
- decisions
- timed missions
- decision categories
- claims
- cores
- war goals
- border settlement events
- leader changes
- party popularity
- ruling party changes
- cosmetic names
- flag changes
- faction mechanics
- local leagues
- foreign aid mechanics
- crisis value effects
- event chains

Small numeric modifiers can support a focus, but they should not be the main point of most focuses.

### No fairy-dust reward standard

Do not fairy dust a focus tree with many tiny bonuses and call it depth. A branch made from small pieces such as `+2%`, `+3%`, minor political power, tiny stability, tiny war support, small generic equipment, or slight production bonuses will feel meaningless.

A focus reward should usually do at least one of these things:

- unlock or upgrade a decision family, mission family, mechanic, route, advisor, unit type, template, law, formable, or diplomatic action
- change the map through factories, infrastructure, railways, supply hubs, ports, airbases, forts, resources, claims, cores, or border settlement work
- move an important visible value by enough that the player cares, such as legitimacy, authority, cohesion, readiness, corruption, recognition, panic, threat, or local support
- create a real tradeoff, cost reduction, risk, deadline, failure state, or new action loop
- alter army, industry, diplomacy, intelligence, logistics, state control, or internal politics for a meaningful period
- transform an existing idea or national spirit into a new stage with visible play consequences

If a focus mainly gives a small flat modifier, the implementation must justify why that modifier matters. It can be acceptable as one part of a larger reward package, a frequent stack, a temporary crisis push, or a final adjustment to an existing mechanic. It is not acceptable as the whole reward for an important focus.

Do not scatter many tiny modifiers across a tree to create the appearance of progression. Combine weak rewards into fewer stronger focuses, convert them into staged idea upgrades, or replace them with decisions, missions, map changes, unit paths, advisors, mechanic thresholds, or route access.

Completion reports and focus audits must flag fairy-dust rewards. A route with many tiny standalone rewards should be treated as incomplete until the rewards are merged, strengthened, connected to a mechanic, or replaced with visible gameplay.

## 9. Idea lifecycle

Do not create a new idea in every focus.

Use an idea only when it represents a lasting institution, doctrine, route identity, military structure, economic system, or crisis condition.

When an idea already represents the institution, later focuses should usually:

- modify it
- upgrade it
- replace it
- add a temporary modifier to it
- unlock decisions tied to it
- change how it interacts with missions
- worsen it after failure
- remove it after reform

New or unstable countries should often start with a few negative or mixed ideas, then solve or transform them through the tree.

Examples:

- broken administration
- improvised command
- disputed legitimacy
- militia fragmentation
- supply confusion
- foreign dependence
- ruined industry
- factional mistrust
- old movement pressure

Every important starting idea should have a lifecycle:

- starting form
- mitigated form
- route-specific upgrade
- failure or corruption form
- final form or removal path

### National spirit reward complexity standard

Do not use national spirits as easy badges for completing shallow focus lines. A national spirit should represent an institution, doctrine, crisis condition, political identity, economic system, military structure, foreign relationship, or special mechanic that changes how the country plays.

A major national spirit should not be earned by one easy focus with no cost, risk, prerequisite, route commitment, decision follow-up, or mechanic interaction. If the spirit is powerful, it should usually require a real path commitment, a branch milestone, a mission success, a crisis choice, a reform chain, a formable step, or a meaningful sacrifice. If the spirit is easy to obtain, it should be modest, temporary, narrow, or part of a larger staged system.

A national spirit is unrewarding when it has only a flat modifier and no lifecycle. Before adding a new spirit, decide whether the existing idea can be upgraded, modified, replaced, worsened, temporarily strengthened, or tied to decisions. Prefer a smaller number of deep spirits over a long list of shallow spirits.

Important national spirits should usually have at least two of these:

- a visible starting problem, benefit, tradeoff, or route identity
- staged upgrades or mitigations through later focuses, decisions, missions, events, or reforms
- a failure, corruption, radicalisation, dependency, or extreme-route form when the route goes badly
- decision or mission hooks that make the spirit more than passive stats
- mechanic value hooks, such as legitimacy, cohesion, authority, readiness, recognition, corruption, panic, or local support
- route-specific localisation and icon direction
- clear AI priority for solving, exploiting, upgrading, or avoiding it

Reject a tree if it has many easy-to-achieve national spirits that feel unrelated, passive, or unrewarding. Merge them into one staged institution, convert some into timed modifiers, move some effects into decisions or missions, or require a stronger route commitment before granting them.

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
- hidden formables that require rare events, special leaders, secret focuses, high escalation, or unusual state control
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
- hidden behind ideology, leader, escalation tier, patron, or secret route
- available only if another country does not exist
- available only if the forming country has the correct release origin or event origin

For shared feature-created trees, formables must use origin and package checks so unrelated countries do not receive the wrong route.

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

Focus trees should consider animated portraits or animated route emblems for major political transformations. Use them for route payoffs such as a supernatural leader reveal, a restored dynasty, a revolutionary cult, a final formable proclamation, or a extreme-route state identity.

Animated portraits need static fallbacks. They should be assigned through the same leader, character, or cosmetic identity logic as the route itself. Real historical portraits require sourced material and careful treatment. Fictional or symbolic leaders can use generated animated portrait packages through the asset skill.

Do not make every leader animated. Animation should signal a special route, a extreme-route identity, sourced quote, remark, or audio research-level transformation, or a rare hidden outcome.

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

## 12. Layout rules

The tree must be readable in game.

Required layout checks:

- prerequisite parents are above children
- no duplicate coordinates
- no unnecessary crossing lines
- mutually exclusive branches are spaced comfortably
- branches are visually distinct
- continuous focuses are placed somewhere convenient
- hidden branches do not clutter ordinary routes
- large branches are not stacked in one vertical column
- the tree does not look like one long checklist
- branch endings are visually and mechanically clear
- side branches feed back into the main route, a mechanic, a decision family, or a real capstone
- the layout does not create random dangling focus chains with weak terminal rewards

If an `available = { has_completed_focus = ... }` condition gates a focus, decide whether it should also be a visible prerequisite. Do not add a visible prerequisite if it creates crossing lines. Move the branch or redesign the gate.

## 13. Event-created versus existing countries

When an event creates or releases a country, set a flag showing that the event created that country.

Only load or replace a runtime focus tree if the event actually created the country.

Existing countries with their own meaningful tree should usually receive additive crisis branches, decisions, ideas, or events, not a blind tree replacement.

For every feature-created country, verify:

- tag
- history setup
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
- extreme-route conditions
- player proximity

Avoid flat AI weights when campaign state matters.

AI should not accidentally choose suicidal or nonsensical routes just because they are visible.

## 15. Localisation and icons

Every focus needs:

- title localisation
- description localisation
- completion reward tooltip
- icon assignment
- AI behavior when relevant

Every political route needs localisation that makes the route identity clear.

Leader changes require leader portraits. Real leaders use sourced portraits. Fictional leaders and symbolic councils can use generated portraits through the asset skill.

Flag or cosmetic-name changes require flag and localisation coverage.

## Improvement addenda and formation routes

When an improvement addendum deepens a focus tree, preserve the route idea before adding nodes. The goal is not a longer tree. The goal is a sharper country identity, stronger branch interaction, clearer route locks, better rewards, stronger AI, and more visible consequences.

Formation routes should usually combine focus preparation with a decision that verifies state control. Focuses can discover old claims, call a congress, unlock a seal, prepare integration, recruit elites, expose a hidden identity, or open the formation decision. The decision then checks the map and performs the formation.

Hidden formables can be routed through secret focuses, events, leader changes, escalation tiers, ancient artifacts, internal factions, or custom GUI investigation. Hidden content should still have a full implementation handoff. It needs reveal logic, visibility rules, localisation, assets, AI handling, post-formation gameplay, and disqualifiers.

Animated leader portraits and animated route emblems should be reserved for major transformations. Use them when the route payoff changes the country's identity, reveals a extreme-route leader, forms a new state, or completes a dramatic ideological break. Keep a static fallback and ensure the animation has a clear trigger and cleanup state.

## Subagent patches for focus trees

Focus tree subagents are active small-patch agents by default inside the current task scope. They can patch prerequisite fixes, mutual exclusion fixes, bypasses, route locks, AI weights, icon references, focus filters, localisation keys, small reward variety, existing decision hooks, and existing formable unlock hooks without waiting for a separate permission prompt.

They should not redesign a whole tree, add a full route family, create a new formable chain, or change the country identity. When the tree needs broader depth, they should write an improvement plan under `docs/plans/<feature_slug>/` and leave implementation to the main agent.

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
- dead-end branches with no capstone, convergence, or follow-up gameplay
- national spirits that are too easy to earn for their importance
- national spirits that have no lifecycle, route commitment, mechanic hook, or decision hook
- layout readability

## 17. Completion rules

A focus tree task is complete only when:

- the tree has distinct political, industry, and expansion branch families, unless it is explicitly documented as a temporary non-playable tag
- large playable countries have military, diplomacy, internal faction, special mechanic, and late-game branches where their identity supports them
- branches interact through prerequisites, decisions, missions, events, AI, crisis values, diplomacy, or route locks
- every major branch has a clear payoff
- political routes change visible country identity where relevant
- industry routes affect the map, production, logistics, or construction
- expansion routes create claims, cores, war goals, leagues, protectorates, settlements, declarations, guarantees, or external diplomacy
- route architecture is implemented
- expansion branch exists for large trees
- political routes actually change politics
- rewards are varied and concrete
- fairy-dust reward patterns have been removed, merged, strengthened, or connected to visible mechanics
- focus terminal nodes are real capstones, convergence points, route locks, failure states, formable steps, or meaningful optional side payoffs
- dead-end branches with weak final rewards have been redesigned
- ideas are not spammed
- national spirits are earned through meaningful route commitment, cost, risk, milestone progress, or mechanic interaction when their effects are important
- important national spirits have lifecycle stages, decision or mission hooks, mechanic hooks, or clear route identity
- easy national spirits are narrow, temporary, modest, or part of a staged system
- focus-decision integration exists
- AI behavior is implemented
- localisation and icons exist
- layout is readable
- documentation is updated
- route coverage table compares required routes with implemented routes
- routes have visible baseline effects without revealing hidden outcomes
- special mechanic values are changed by relevant focus paths
- balance-of-power or equivalent internal struggle mechanics are used when appropriate
- feature-created factions have goals, membership rules, shared mechanics, AI behavior, rewards, and success or failure states
- special mechanics have visible presentation through decision headers, scripted GUI, progress meters, tooltips, or spirits
- important custom GUI mechanics consider progress variants, status frames, warning frames, selected or locked variants, and frame animations where useful
- AI routes respect validity and avoid impossible branches
- shared trees are adapted per country and do not read or play identically
- important tuning values are centralized in script constants or documented tuning files
- one-time reward dumps are not the main branch pattern
- small modifiers are never the main reward pattern for important branches
- exploit checks cover unit loops, factory loops, equipment dumps, cores, claims, war goals, advisor stacking, influence farming, bypass abuse, and puppet abuse
- decision categories avoid showing every possible action at once
- large trees have early, middle, and late pacing
- major routes have real tradeoffs and failure states
- mutual exclusions are not overused
- major routes have distinct AI behavior and localisation tone
- expansion branches include postwar handling
- industry branches are geographically grounded where possible
- advisor unlocks match route identity
- achievement hooks exist for major route accomplishments
- simplifications and blockers are reported

If a tree uses a fallback tree where the spec requires a bespoke tree, report it as a simplification.

If no simplifications were made, say so and provide evidence.
