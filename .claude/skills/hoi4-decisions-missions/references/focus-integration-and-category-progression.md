# HOI4 Decisions and Missions: Focus integration and category progression

Part of the [hoi4-decisions-missions](../SKILL.md) skill. Read before tying a decision family to a focus route, or deciding how a category deepens, paces and differs by route.

## 15. Focus and decision integration

Focuses and decisions should be designed together.

A decision system should not feel detached from the focus tree. Focuses should unlock new decision families, expand existing mechanics, change decision costs, alter mission success conditions, add new targets, or open new diplomatic, military, industry, or expansion choices.

Common patterns:

- expansion focuses unlock declarations, ultimatums, league votes, protectorate demands, border settlement decisions, war-preparation missions, and postwar integration decisions
- industry focuses unlock factory construction, rail repair, supply hub expansion, airbase construction, anti-air construction, fortification, resource extraction, and infrastructure programs
- military focuses unlock reserve mobilisation, special unit training, template conversion, border defense missions, depot seizure missions, commander recruitment, and offensive preparation
- diplomacy focuses unlock recognition missions, aid corridors, advisor missions, volunteer transfers, anti-puppet clauses, sponsor-balancing decisions, and foreign investment decisions
- political focuses unlock elections, councils, purges, compromises, advisor appointments, party campaigns, reform missions, leader changes, and ideology decisions
- faction or league focuses unlock shared reserve decisions, member votes, joint declarations, common fronts, intervention forces, and arbitration missions

When a focus unlocks decisions, document:

- focus id or route
- decision category or family unlocked
- new decision targets
- costs and requirements
- AI behavior
- success and failure effects
- follow-up events or missions
- cleanup rules

When a decision family is route-locked, localisation should explain which political, expansion, industry, military, diplomacy, or league route enabled it.

Industry decision families should generally do real map work, such as building or repairing factories, railways, forts, anti-air, airbases, infrastructure, supply hubs, ports, or resources.

Expansion decision families should generally create real strategic options, such as claims, cores, war goals, protectorates, leagues, declarations, border incidents, treaties, ultimatums, or postwar settlement choices.


## 15.1 Progressive decision categories

Decision categories should evolve as the focus tree develops.

A decision category should not remain a static list of buttons after a country changes ideology, builds an industry route, joins a league, chooses an expansion path, or accepts foreign influence.

Focus progress can change decision systems by:

- unlocking new decision families
- adding new targets
- reducing or changing costs
- adding new risks
- changing success or failure effects
- unlocking stronger versions of earlier decisions
- adding mission variants
- changing AI priorities
- changing localisation
- closing decisions that no longer fit the route

Examples:

- an industry route starts with small repair decisions, then unlocks factory projects, rail expansion, supply hub construction, anti-air construction, airbase construction, and resource extraction
- an expansion route starts with border incidents, then unlocks guarantees, ultimata, claims, cores, protectorates, local leagues, war goals, and settlement decisions
- a military route starts with emergency units, then unlocks templates, training missions, offensive planning, border defense, and special force recruitment
- a political route starts with legitimacy decisions, then unlocks party campaigns, advisor appointments, leader changes, purges, elections, councils, laws, and cosmetic identity changes
- a diplomacy route starts with observers, then unlocks recognition, aid corridors, volunteer transfers, anti-puppet clauses, sponsor rivalry, and treaty decisions

If a focus branch says it changes the country, the decision layer should reflect that change.


## 15.2 Route-aware decision depth

A decision family unlocked by a focus path must have enough content to matter.

A route-unlocked decision family should usually include:

- several decisions or missions, not only one button
- route-specific costs
- route-specific risks
- route-specific AI behavior
- route-specific localisation
- visible consequences
- cleanup when the route, war, target, or crisis ends

Expansion decision families should include postwar handling when they create conflict. War goals, declarations, ultimatums, and border incidents should connect to occupation, integration, protectorate, puppet, resistance, league, faction, or settlement decisions.

Industry decision families should be geographically grounded where possible. Construction, rail, supply, anti-air, fort, airbase, dockyard, port, and resource decisions should name states or regions, and they should change the map or production system.

Political decision families should interact with leaders, advisors, parties, laws, ideology, legitimacy, councils, internal factions, cosmetic names, or flags when the focus route changes politics.

Advisor, leader, and council decisions should match the route that unlocked them. Do not unlock generic advisors unrelated to the route identity.

Decision families can include achievement tracking when they support difficult route completions, rare combinations, expansion victories, internal reform, or survival under high-chaos conditions.


## 15.3 Decision pacing, tradeoffs, and visible effects

Decision categories unlocked by focuses should progress over time.

- Early decisions should be limited, urgent, and tied to survival or first institutions.
- Middle decisions should add stronger tools, new targets, route mechanics, influence actions, military actions, and construction options.
- Late decisions should support route payoffs, expansion, integration, faction leadership, League leadership, postwar settlement, or high-chaos end states.

Decision families should have tradeoffs. A powerful decision should cost or risk something that fits the action: equipment, manpower, stability, war support, consumer goods burden, foreign dependency, legitimacy, faction cohesion, unit commitment, fuel, convoys, or crisis pressure.

Do not overuse mutually exclusive decision paths. Use them when the choices represent incompatible policy, route identity, foreign alignment, or institutional structure. Support actions should usually coexist unless the design says otherwise.

Important decision families should define failure states. Failed reforms, failed influence balancing, failed expansion, failed military centralisation, failed construction, or failed diplomacy should create visible follow-up problems where the mechanic supports it.

Decision localisation should describe the visible baseline effect of the decision. Do not reveal hidden outcomes, secret variables, hidden follow-up events, or future surprise branches. The player should understand the public action and likely visible direction without being spoiled.


