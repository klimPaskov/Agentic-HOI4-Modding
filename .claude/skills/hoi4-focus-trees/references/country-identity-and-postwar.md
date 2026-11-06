# HOI4 Focus Trees: Country identity, AI and localisation

Part of the [hoi4-focus-trees](../SKILL.md) skill. Read before a route changes the visible country package (leader, flag, advisors), before writing route AI, localisation or icons, or for event-created countries.

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

