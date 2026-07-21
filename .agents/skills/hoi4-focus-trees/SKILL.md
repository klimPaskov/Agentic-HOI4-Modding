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
- `improvement-loop` when a tree needs broader route depth or a near-completion anti-bloat pass
- `subagents` before routing focus audits, improvement plans, or active small patches
- the installed `hoi4-agent-tools` MCP server for `hoi4.focus_inspect`, `hoi4.focus_render`, and bounded `hoi4.focus_rewrite` work. Use it to inspect, render, lint, compare, and improve focus-tree structure, then review every returned layout and diagnostic. MCP supports this skill and does not replace required source, wiki, vanilla, balance, localisation, asset, or AI review.

## 1. Required checks

Before editing focus files:

- Read the offline Paradox wiki National focus modding page.
- Read relevant vanilla documentation from `<HOI4_INSTALL_DIR>/documentation`.
- Inspect vanilla focus files for syntax and layout precedent.
- Inspect existing repository focus trees and feature-created focus-tree loading patterns.
- Read `AGENTS.md`.
- Read `hoi4-decisions-missions` when focuses unlock decisions, timed objectives, missions, or dynamic mechanics.

Do not rely on memory for prerequisite behavior, layout behavior, AI syntax, or search filters.

Use `hoi4.focus_inspect` and `hoi4.focus_render` before major layout work or complex audits. Use bounded `hoi4.focus_rewrite` only after the route design and ownership are clear. Review the returned source diff, diagnostics, and rendered artifacts before accepting any MCP write.


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

A focus tree is the playable identity of a country. It should define what problems matter, which strategies solve them, and what kind of state the player builds.

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

### 3.1 Starting simplicity and player-built identity

Do not begin a country with a long stack of focus-tree-owned national spirits, currencies, decision categories, and unrelated penalties merely to create work for the opening branches.

For a new or focus-tree-owned country setup, prefer zero to two starting national spirits. Use a third only when all three represent separate problems or institutions that the player can understand immediately. The hard simultaneous limit in section 9 still applies. Established countries can retain historically necessary starting systems, but their opening presentation should still identify the few pressures that matter first.

Choose one to three strategic constraints that define the opening. Good constraints include resource shortage, weak supply, limited civilian capacity, disputed legitimacy, dependence on a sponsor, an underdeveloped officer corps, or vulnerable borders. Each constraint must create choices and have more than one credible response. Do not use a long stack of debuffs as a substitute for country identity.

The starting army, navy, air force, economy, and decision layer should be simple enough that the player can understand the country's immediate problem in one pass. A large historical empire can remain geographically complex, but the tree should still give it a clear first priority and delay secondary problems until they matter.

Do not remove all scarcity in the opening focuses. Scarcity can create the reason to trade, industrialize, seek a patron, change laws, build logistics, or expand. The tree should let different routes solve or exploit the same constraint in different ways.

### 3.2 Progressive disclosure and opening choice budget

A large tree can contain many routes without presenting all of them on day one. Required route coverage applies to the complete tree, not to the number of root focuses visible at game start.

Use a narrow opening by default:

- one common opener or a small set of clearly different entry focuses
- two to four meaningful early choices after the opening
- deeper political, military, industry, diplomatic, and expansion options revealed as the country commits or the campaign changes
- hidden, crisis-gated, event-gated, and extreme routes kept out of the ordinary opening view until their reveal conditions matter

More opening choices are allowed when the country genuinely begins with several simultaneous emergencies, but each visible option must answer a different urgent question. Do not create an octopus root where the player must inspect the whole tree before unpausing.

The first few focuses should establish the campaign plan. Good early choices distinguish short-term mobilization, medium-term institution building, and long-term transformation. Bad early choices grant interchangeable small bonuses and only become meaningful several focuses later.

Complexity should expand downward. Later branches can become intricate after the player understands the country, its constraints, and the consequences of the first commitment.

### 3.3 Route relevance and no ideology quota

Do not add political routes to satisfy an ideology checklist. A focus tree does not need democratic, communist, fascist, monarchist, anarchist, religious, and military routes merely because those labels exist.

A political route earns a place only when it has:

- country-specific actors, institutions, factions, or historical and alternate-history support
- a distinct campaign promise and mechanical loop
- visible identity changes or political consequences
- enough content for a real branch
- a payoff that is exciting and specific, with more depth than a generic ideology swap

Omit a route when it would be a short filler branch with generic party popularity, political power, and one cosmetic change. Political variety can come from rival institutions, leaders, factions, constitutional models, patron relationships, or methods of rule inside the same broad ideology.

Route coverage tables compare the accepted spec with the implementation. They are not a generic ideology quota. A deliberately omitted ideology is not a defect when the country concept and source design do not support it.

### 3.4 Fast quality test

Use this test before expanding a route map or accepting an implementation.

A strong tree usually:

- starts with zero to two focus-tree-owned national spirits and one to three understandable strategic problems
- presents one common opener or a small opening set, followed by two to four meaningful choices
- uses 35-day focuses often enough to create quick, noticeable early progress when each click changes the player's plan
- gives rewards the player feels immediately, such as factories, supply improvements, decisions, units, claims, war goals, or access to a mechanic
- separates short-term power, medium-term institution building, and long-term growth through real tradeoffs
- lets optional military, industry, diplomacy, intelligence, navy, and air branches stay optional unless the route truly depends on them
- uses laws, diplomacy, production, trade, state control, compliance, stockpiles, unit placement, and other existing mechanics where they fit
- offers early active play and, for suitable expansion countries, an early high-risk or limited-conflict route
- ends major goals with a visible payoff such as cores, territory, a formable, a new government, a faction, a doctrine, or a lasting gameplay system

Reject or redesign a tree when it:

- starts with a pile of penalties, currencies, or unrelated national spirits
- exposes so many branches at the root that the player must study the whole tree before unpausing
- uses long chains of `2-5%` bonuses or other low-impact rewards
- contains one route that dominates its alternatives in nearly every plausible campaign
- adds ideology branches only to complete a political checklist
- depends on another country's AI behavior with no alternate gate, replacement route, or bypass
- delays the country's main gameplay until 1940 or 1941 without giving the player meaningful work during the delay
- repeats opaque civil wars that randomly divide states, divisions, equipment, or commanders
- grants most factories, units, and bonuses automatically without asking the player to use the country's mechanics
- can be completed on autopilot without changing production, diplomacy, laws, deployment, strategy, or risk tolerance

This test is a design gate, not a rigid template. A direct factory or equipment reward can be good. A 70-day focus can be good. A peaceful country can omit early war. The tree must still provide clear choices, visible progress, meaningful interaction, and a payoff that fits its identity.

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
- hidden, crisis, or extreme path when relevant
- late-game ambition path

Do not collapse everything into one political ladder.


## 5.1 Strategic constraints, active play, and payoff ladder

Every major tree should identify the country's opening constraint and the actions it creates. A shortage of steel, fuel, convoys, trained officers, supply, legitimacy, civilian capacity, recognition, or secure borders can be good design when the player can respond through several strategies.

Do not make the first branch simply erase every weakness. Different routes should answer the constraint differently. Examples include domestic substitution, foreign trade, patron aid, legal reform, infrastructure, military seizure, limited expansion, or accepting dependency in exchange for speed.

Domestic-development and foreign-integration routes must use different mechanics and incentives. Different factory totals alone do not create distinct routes. A domestic route can emphasize resource surveys, substitution, savings, law interactions, construction burdens, or slower self-sufficiency. A foreign route can use relations, investment, market access, technology exchange, convoys, sponsor pressure, or dependency risk.

The tree should provide an active play opportunity early. Depending on country identity, this can be a limited conflict, border intervention, diplomatic campaign, construction program, military preparation mission, internal political contest, or resource strategy. The player should not have to complete years of filler before the country begins doing what its campaign concept promises.

Use a payoff ladder:

- the opening establishes the immediate problem and first commitment
- the middle unlocks the route's repeatable mechanic, decision family, military system, diplomatic stance, or construction loop
- the late route delivers a visible capstone such as a new state identity, regional order, formable, doctrine, industrial network, faction, or postwar system

When a payoff requires compliance, stockpiles, relations, state control, laws, unit placement, or another non-focus condition, the route must provide tools that help the player reach it. A requirement without supporting gameplay is obstruction, not depth.

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

Leader changes require portrait handling. Real leaders use sourced portraits. Fictional leaders, councils, symbolic leaders, or extreme authorities can use generated portraits through the asset skill.

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
- when extreme routes are allowed
- when a route no longer makes sense because the campaign state changed

Every major route also needs a distinct localisation tone. A socialist route, military route, democratic route, nationalist route, religious route, machine route, death-state route, foreign client route, and extreme route should not sound the same.

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
- extreme routes unlock strange councils, symbolic leaders, cult officers, machine boards, death-state authorities, or other route-specific figures

## 5.7 Achievement hooks and route coverage proof

Large focus trees should include achievement hooks for difficult route completions, rare branch combinations, expansion outcomes, successful internal reform, avoiding foreign dependency, forming leagues, surviving extreme paths, or completing hard late-game ambitions.

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
- Late focuses deliver major payoffs, expansion, faction or League outcomes, extreme routes, postwar settlement, or international-order ambitions.

Every major route should have a tradeoff. A military route may reduce freedom or legitimacy. A foreign-aid route may increase dependency. An expansion route may create resistance or foreign backlash. An industry route may consume civilian capacity or weaken short-term defense. A extreme route may give power while damaging stability, diplomacy, or normal politics.

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

AI strategy must respect route validity. AI should not pick a branch that requires a missing state, dead sponsor, non-existent faction, unavailable ideology, disabled event variant, impossible border, or absent enemy. Invalid routes should be hidden, bypassed, or weighted to zero.

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

## 5.13 Focus cadence and click value

Focus duration should match the decision value and campaign tempo. Duration is not a reward-strength number and should not be forced into the general round-value rule. Established weekly focus cadences such as 7, 14, 21, 28, 35, 56, and 70 days are valid when the role of the focus justifies them.

A short focus is useful when it does one of these things:

- resolves a real route choice
- responds to a crisis or changed campaign state
- asks the player to adapt production, diplomacy, deployment, or laws
- unlocks an interaction that the player can use immediately
- completes a leader, cabinet, council, or institutional selection
- creates a deliberate short-term versus long-term commitment

A short focus is click tax when it only divides one ordinary reward into several pieces. Do not split a 70-day factory, research, or modifier reward into two 35-day focuses unless the first half changes the player's decision or creates a meaningful intermediate state.

Use 7-day transition focuses sparingly for immediate political resolutions, route conversions, emergency responses, or post-event handoffs. Do not use them for large unconditional reward dumps. Use longer focuses for major institutions, strategic preparations, and capstones when the delay itself creates planning pressure.

As a normal target, a major tree should present a meaningful choice within the first 70 days and an active route interaction within the first 180 days. This is a pacing target, not a universal hard gate. A deliberate exception must explain what the player is doing during the delay and why the delay belongs to the country concept.

## 5.14 Strong rewards, real prices, and time horizons

Meaningful bonuses can be large. Balance strong effects with costs, timing, risk, or counterplay instead of reducing every reward to a small modifier.

Useful prices include:

- a temporary bonus followed by exhaustion
- higher resource, fuel, convoy, or equipment consumption
- civilian factory burden or lower output elsewhere
- dependency on a foreign sponsor
- weaker long-term research or production for immediate mobilization
- stability, legitimacy, cohesion, or diplomatic backlash
- an opportunity cost that locks a competing route
- a deadline that rewards preparation and punishes mistiming
- a failure state that is understandable before commitment

Short-term, medium-term, and long-term options should feel different in play. An immediate mobilization path can deliver fast factories or units with a later hangover. A permanent-output path can be slower and narrower. A long-war path can improve research, doctrine, logistics, or scaling while leaving the opening weaker. Do not make one horizon strictly dominate the others in every plausible campaign.

High-risk focuses can be optional. Do not force every player through a powerful temporary boom and its penalty merely to reach unrelated content. The tooltip must explain the visible price and duration without exposing hidden follow-up events.

When a strong tradeoff represents an ongoing policy, consider letting the player suspend, replace, or reverse it through a decision, law, or later focus. Irreversible institutions can justify permanent commitment. Permanent penalties are appropriate when the route is an identity commitment. They are not appropriate merely because no off-switch was designed.

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

### Early action and limited-conflict routes

When the country's concept includes expansion, intervention, border revision, or reunification, consider an early high-risk route and a slower preparation route. The early route should let the player act before the wider war when geography and balance support it. The long route can build alliances, compliance tools, logistics, recognition, or overwhelming strength.

Early action does not require unrestricted total war. Limited-conflict systems can make small-country expansion playable without forcing an immediate fight to total capitulation against a major power. A limited conflict should define:

- the exact political or territorial objective
- target states or control conditions
- escalation conditions
- ceasefire, scripted peace, withdrawal, or settlement behavior
- failure and timeout consequences
- AI willingness and safety checks
- postwar compliance, integration, resistance, diplomacy, and cooldown handling

A limited conflict must not become a cheap annexation shortcut. The objective should be narrow, the settlement should match what was achieved, and repeated use should create costs, resistance, diplomatic pressure, or stronger opposition.

When a branch represents war fervor, mobilization pressure, or a public promise to fight, prefer a visible timed commitment over several instant war-support rewards. The commitment can build readiness or war support over time, then ask the player to begin the promised action before a deadline. Failure should create route-appropriate political backlash, lost legitimacy, demobilization, or a harder settlement. Do not default to a generic civil war merely because the deadline was missed.

Not every country needs an early war. A country without a plausible conflict route still needs early active play through diplomacy, internal politics, resource policy, construction, military objectives, or another system that fits its identity.

Expansion should usually answer a real strategic need such as resources, secure borders, ports, supply access, diaspora protection, ideological goals, or regional legitimacy. Map growth without a country-specific reason is not a branch identity.

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
- extremist cult
- machine or factory state
- death-state actor

Fixed-purpose special feature-created countries can have narrower political design. For example, a country whose entire identity is death, plague, machine rule, or total destruction may have one ideological purpose. Even then, its tree should still create mechanical choices inside that purpose, such as doctrine, expansion method, internal hierarchy, recruitment, economy, and endgame ambition.

### Leader and institution construction

When a political route centers on choosing or creating a leader, regent, council, junta, cabinet, or symbolic authority, consider letting the player construct that identity through events or decisions. Avoid granting one fixed trait package when personal construction is central to the route.

A leader-construction sequence should normally offer a small number of consequential choices, such as economic priority, military temperament, constitutional relationship, diplomatic posture, or personal doctrine. The choices should:

- change gameplay beyond a cosmetic trait
- create synergies and tradeoffs, with no obvious best combination
- have clear caps or exclusions so trait stacking cannot be exploited
- affect later focuses, decisions, advisors, or crisis responses where relevant
- include route-specific AI selection profiles
- update portrait, name, traits, and localisation consistently when identity changes

Do not add leader customization to every tree. Use it when personal rule, a regency, a council struggle, or a constructed political identity is central to the country concept.

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

Fairy-dusted values are prohibited. Do not spread many tiny bonuses across a focus tree and present them as depth. Values such as `+2%`, `+3%`, `+7%`, `12`, `18`, tiny political power grants, tiny stability or war support changes, token equipment, and slight generic production bonuses are completion-blocking defects unless an engine-defined formula or hard technical constraint requires that exact value.

Use round balance values in multiples of 5 wherever the value is authored for gameplay tuning. Prefer values such as `5`, `10`, `15`, `20`, `25`, and corresponding percentage values. Do not use arbitrary-looking values such as `2`, `3`, `7`, `12`, `18`, or `23` for focus rewards, mechanic gains or losses, thresholds, caps, durations, AI weights, or costs without a documented reason. Engine-required values, binary flags, coordinate values, dates, state ids, and formula-derived results are exempt.

A focus tree with repeated fairy-dusted rewards must be rejected during audit. Do not excuse the pattern because each individual value is technically useful. Merge weak rewards, strengthen them into meaningful round values, turn them into staged upgrades, or replace them with decisions, missions, map changes, units, advisors, laws, mechanics, or route access.

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

### National spirit count limit

A focus tree must never grant or maintain more than three focus-tree-created national spirits at the same time for one country. This is a hard maximum, not a target.

Before adding a fourth spirit, the implementation must upgrade, replace, merge, transform, or remove one of the existing three. Starting national spirits that belong to the same focus-tree package count toward this limit when the tree is responsible for their lifecycle. Temporary timed modifiers do not count when they are clearly short-lived and are not being used to evade the limit.

Prefer one staged national spirit with several lifecycle forms over several separate spirits covering closely related themes. Political institutions, military structures, economic systems, foreign dependence, legitimacy crises, and similar systems should usually evolve through replacement or modification chains.

Audits and completion reports must list the maximum number of simultaneously active focus-tree-created national spirits for every major route. A route exceeding three is incomplete until the spirits are consolidated.

### National spirit reward complexity standard

Do not use national spirits as easy badges for completing shallow focus lines. A national spirit should represent an institution, doctrine, crisis condition, political identity, economic system, military structure, foreign relationship, or special mechanic that changes how the country plays.

A major national spirit should not be earned by one easy focus with no cost, risk, prerequisite, route commitment, decision follow-up, or mechanic interaction. If the spirit is powerful, it should usually require a real path commitment, a branch milestone, a mission success, a crisis choice, a reform chain, a formable step, or a meaningful sacrifice. If the spirit is easy to obtain, it should be modest, temporary, narrow, or part of a larger staged system.

A national spirit is unrewarding when it has only a flat modifier and no lifecycle. Before adding a new spirit, decide whether the existing idea can be upgraded, modified, replaced, worsened, temporarily strengthened, or tied to decisions. Prefer a smaller number of deep spirits over a long list of shallow spirits.

Important national spirits should usually have at least two of these:

- a visible starting problem, benefit, tradeoff, or route identity
- staged upgrades or mitigations through later focuses, decisions, missions, events, or reforms
- a failure, corruption, radicalisation, dependency, or extreme form when the route goes badly
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

### Interaction checkpoints and anti-autopilot design

A focus tree should sometimes require the player to do something outside the focus interface before continuing. Good interaction checkpoints include:

- building relations with named countries
- producing or retaining a meaningful equipment stockpile
- changing an economy, conscription, or trade law
- stationing a capital ship, air wing, or supplied divisions in a relevant place
- controlling a port, rail hub, border region, or resource state
- completing a mission or decision chain
- reaching compliance, legitimacy, cohesion, recognition, or another visible threshold
- securing foreign access, a convoy route, or a sponsor agreement

The checkpoint must be thematic, visible, achievable, and connected to the reward. It should make the player adapt a plan. Passive waiting for a number the country already satisfies does not qualify. Nonstandard requirements need clear custom tooltips or scripted localisation.

Prefer making existing HOI4 systems matter before inventing a bespoke meter or button. A good focus can recontextualize laws, relations, trade, markets, stockpiles, ships, air wings, state control, compliance, or production through a clear reward and tradeoff. Use a custom mechanic when the route needs information or choices that existing systems cannot present cleanly.

A route that asks for an unusual condition must provide supporting tools. If a capstone requires compliance, the branch should unlock compliance, occupation, or integration actions. If it requires trucks, ships, or aircraft, earlier content should explain why and give the player enough time or production support to prepare.

Use interaction checkpoints at branch milestones, not on every node. Too many gates create chores. Too few can turn the tree into an automatic click conveyor where the player reads only the reward line.

A focus can also open an event choice with several valid results. The event should present real alternatives that fit the route, carry different costs or time horizons, and remain valid for AI.

## Focus routes that lead to formable nations

A focus tree can prepare, reveal, enable, or stabilize a formable nation, but the final formation should usually be handled by a decision when state control matters. Use focuses to build the political claim. Use decisions to verify the map and perform the formation.

A formation route in a focus tree should define:

- narrative reason the country can claim the formable identity
- route family that unlocks the claim
- focuses that reveal the formation decision
- focuses that mark required regions, start border commissions, invite subjects, sponsor plebiscites, or prepare integration
- mutually exclusive formable routes
- compatible support branches, such as industry, army, diplomacy, intelligence, or legitimacy
- hidden formables that require rare events, special leaders, secret focuses, an extreme campaign state, or unusual state control
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
- hidden behind ideology, leader, campaign-state tier, patron, or secret route
- available only if another country does not exist
- available only if the forming country has the correct release origin or feature origin

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

Focus trees should consider animated portraits or animated route emblems for major political transformations. Use them for route payoffs such as a supernatural leader reveal, a restored dynasty, a revolutionary cult, a final formable proclamation, or an extreme route state identity.

Animated portraits need static fallbacks. They should be assigned through the same leader, character, or cosmetic identity logic as the route itself. Real historical portraits require sourced material and careful treatment. Fictional or symbolic leaders can use generated animated portrait packages through the asset skill.

Do not make every leader animated. Animation should signal a special route, an extreme route identity, sourced quote, remark, or audio research-level transformation, or a rare hidden outcome.

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

### External dependencies and dead-route prevention

A route that depends on another country, war, faction, event, leader, or historical sequence must define four things:

1. the primary valid condition
2. an alternate condition, replacement route, or clean bypass when the original condition no longer exists
3. the point at which obsolete content is hidden, bypassed, or transformed
4. AI behavior for the primary and alternate states

Prefer role-based conditions when the identity of the counterpart is not essential. A route can target the regional hegemon, colonial holder, faction leader, sponsor, border enemy, or controller of named states instead of one hardcoded tag. Use a specific tag when the relationship with that exact country is the point of the route.

Do not leave a substantial branch permanently locked because an external country chose an alternate-history path, disappeared, changed faction, lost the relevant states, or never fired one event. Historical routes may depend on historical sequences in historical mode, but alternate-history and multiplayer campaigns need coherent route validity.

A bypass should preserve pacing and prevent dead content. It must not grant incompatible rewards for free or let the player collect both the original and replacement branches.

### Civil conflict and player agency

Do not use the generic civil-war pattern as the default way to make politics dramatic. Random or opaque division and territory splits can remove player agency, destroy carefully built forces, and make the route feel punitive instead of strategic.

Prefer alternatives when they fit the conflict:

- balance-of-power escalation
- coup missions and counter-coup decisions
- deterministic state-based uprisings
- rival administrations or regional secession
- command-loyalty, garrison, or officer-defection mechanics
- targeted mutinies, strikes, sabotage, or capital seizures
- negotiated constitutional crises with failure branches

When a true civil war is central to the route, define the split clearly. The player should understand the threatened states, likely units, stockpile treatment, leaders, preparation choices, and victory consequences before commitment. Earlier focuses and decisions should let the player influence loyalty, territory, equipment, or timing. The aftermath must restore or integrate surviving institutions and prevent repeated reward collection across both sides.

## 12. Layout rules

The tree must be readable in game.

Use the MCP focus tools to find layout deformities before rewriting. `hoi4.focus_inspect` and `hoi4.focus_render` report overlapping focus boxes, excessive gaps, cramped spacing, connector crossings, path lines that run through focuses or stretch too far, dangling connectors, bad prerequisite presentation, unbalanced branches, off-center layouts, and related diagnostics. Review the artifacts, then call `hoi4.focus_rewrite` with `layoutMode: "compact"` for cleanup or a complete route plan for creation. Review the rewritten artifacts and source diff. MCP supplies shared parsing, layout, rendering, and writes, while this skill owns design, prerequisites, localisation, AI, icons, balance, and completion.

Required layout checks:

- prerequisite parents are above children
- no duplicate coordinates
- no unnecessary crossing lines
- no connector runs through focus boxes or unrelated branches
- horizontal and vertical gaps are neither excessive nor cramped
- visible connectors agree with the scripted prerequisite structure
- route families remain balanced and centered
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

## 13. Feature-created versus existing countries

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
- extreme conditions
- player proximity

Avoid flat AI weights when campaign state matters.

AI should not accidentally choose suicidal or nonsensical routes just because they are visible.

## 15. Localisation and icons

Focus-tree assets must not reuse one uniform colour palette across the whole tree. Political routes, military routes, industry routes, diplomacy routes, expansion routes, crisis routes, and hidden or extreme paths should use visibly distinct palette families where their identities differ. Separate branches should not look like recoloured copies of the same icon set.

Do not solve asset variety by taking the same composition and changing only its hue. Vary subject matter, framing, lighting, contrast, symbols, materials, and background treatment while keeping the tree visually coherent and readable in the HOI4 interface.

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

Hidden formables can be routed through secret focuses, events, leader changes, campaign-state tiers, ancient artifacts, internal factions, or custom GUI investigation. Hidden content should still have a full implementation handoff. It needs reveal logic, visibility rules, localisation, assets, AI handling, post-formation gameplay, and disqualifiers.

Animated leader portraits and animated route emblems should be reserved for major transformations. Use them when the route payoff changes the country's identity, reveals an extreme route leader, forms a new state, or completes a dramatic ideological break. Keep a static fallback and ensure the animation has a clear trigger and cleanup state.

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
- opening root count and first meaningful choice timing
- first active gameplay opportunity
- strategic constraints and route responses
- route families
- route reveal order and progressive-disclosure plan
- mutual exclusions
- major decisions unlocked
- interaction checkpoints and supporting tools
- external dependency fallbacks or bypasses
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
- opening choice overload or analysis-paralysis root design
- delayed first meaningful choice or years of filler before active play
- ideology-quota branches with no country-specific identity
- short focuses that only split one ordinary reward into extra clicks
- long focuses that delay interaction without creating planning pressure
- missing strategic constraint or routes that erase every constraint immediately
- missing player interaction checkpoints before major payoffs
- unusual route requirements without supporting tools
- external event, country, faction, or war gates that can permanently deadlock a branch
- generic civil wars with opaque or uncontrollable splits
- strong temporary rewards without visible costs, aftereffects, or AI use windows
- missing expansion branch
- missing political change
- missing branch payoff
- isolated branches that do not interact
- expansion branch without claims, cores, war goals, diplomacy, leagues, or settlements
- industry branch without map, construction, logistics, production, or resource effects
- support branches made attractive through unrelated rewards instead of thematic cross-domain utility
- expansion routes with no early-action option or no explanation for delayed action when the country concept supports early conflict
- limited conflicts without objective, settlement, escalation, failure, AI, or postwar rules
- leader or institution customization with one obvious best combination or no later gameplay effect
- generic flat rewards
- fairy-dust reward patterns made from many tiny bonuses
- authored reward, threshold, cap, AI-weight, and cost values that are not rounded to multiples of 5 without a documented exception
- focus cadence values that do not match the focus role or established weekly pacing
- routes that can hold more than three focus-tree-created national spirits at once
- focus-tree asset sets that reuse the same colour palette across distinct branches
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
- authored reward, threshold, cap, AI-weight, and cost values use round multiples of 5 unless a documented engine, formula, or technical exception applies
- focus durations follow deliberate weekly cadence and every short focus has real click value
- no route can maintain more than three focus-tree-created national spirits at the same time
- focus terminal nodes are real capstones, convergence points, route locks, failure states, formable steps, or meaningful optional side payoffs
- dead-end branches with weak final rewards have been redesigned
- ideas are not spammed
- national spirits are earned through meaningful route commitment, cost, risk, milestone progress, or mechanic interaction when their effects are important
- important national spirits have lifecycle stages, decision or mission hooks, mechanic hooks, or clear route identity
- easy national spirits are narrow, temporary, modest, or part of a staged system
- focus-decision integration exists
- AI behavior is implemented
- localisation and icons exist
- distinct focus-tree branches use distinct palette families and do not rely on one repeated colour palette or simple hue-shifted icon composition
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
- fairy-dusted values such as `+2%`, `+3%`, `+7%`, `12`, or `18` are absent unless their exact use is documented and justified
- exploit checks cover unit loops, factory loops, equipment dumps, cores, claims, war goals, advisor stacking, influence farming, bypass abuse, and puppet abuse
- decision categories avoid showing every possible action at once
- large trees have early, middle, and late pacing
- the opening exposes a small, understandable choice set and complexity expands as routes develop
- the first meaningful choice and first active gameplay opportunity arrive at a justified pace
- political routes exist because the country supports them, not because of an ideology quota
- strategic constraints create route choices and are not all erased by the opener
- major routes include interaction outside the focus interface where it improves play
- unusual capstone requirements have route tools that help the player satisfy them
- short focuses resolve choices, adaptation, or immediate transitions instead of adding click tax
- strong rewards use real prices, time horizons, risks, or aftereffects, with no timid balance through negligible values
- early or limited conflict routes exist where the country concept and balance support them
- limited conflicts have objectives, settlements, escalation, failure, AI, and postwar handling
- external dependencies have alternate gates, bypasses, or replacement content and cannot deadlock the tree
- civil conflicts preserve player agency or use a more suitable alternative system
- leader or institution construction has meaningful choices, bounded stacking, and AI profiles where used
- support branches provide thematic cross-domain utility and avoid unrelated rewards added only to force participation
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
