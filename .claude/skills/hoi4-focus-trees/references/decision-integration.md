# HOI4 Focus Trees: Focus and decision integration

Part of the [hoi4-focus-trees](../SKILL.md) skill. Read before a focus unlocks, modifies or stages decisions and missions.

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

