# HOI4 Decisions and Missions: Values, costs and rewards

Part of the [hoi4-decisions-missions](../SKILL.md) skill. Read before choosing a decision's costs, dynamic values, rewards or penalties, and when checking a system for reward dust and exploits.

## 4. Dynamic values

Everything that acts like cost, duration, cooldown, support, chance, pressure, threat, reward, mission difficulty, influence, aid amount, or AI willingness should be dynamic by default.

A fixed value can be a tuning anchor, but the system should explain what changes it.

Useful factors:

- country size
- industry
- manpower
- equipment stockpile
- stability
- war support
- war state
- current fronts
- supply
- rail control
- ports
- fuel
- trains
- convoys
- terrain
- distance
- local support
- legitimacy
- foreign access
- faction membership
- previous failures
- previous successes
- chaos tier or event pressure
- AI strategy situation

Do not copy the same cost or duration across every country unless the story and balance justify it.

## 4.1 Effect strength and no fairy-dust rewards

Do not fill decision systems, missions, scripted GUI buttons, or formable routes with tiny bonuses that feel meaningless. Small values such as plus 1 percent, plus 2 percent, minus 3 percent, tiny political power, tiny stability, tiny war support, small generic stockpiles, or slight production nudges do not count as meaningful design by themselves.

A decision or mission reward should usually do at least one meaningful thing:

- change what the player chooses next
- open or upgrade a decision family, mission family, formable step, advisor path, unit path, special mechanic, or route action
- move a visible value by enough that the player cares, such as legitimacy, authority, cohesion, readiness, corruption, recognition, panic, threat, local support, or sponsor pressure
- change the map, production, logistics, diplomacy, army behavior, intelligence behavior, or internal politics in a visible way
- create a real tradeoff, risk, deadline, escalation, partial success, or failure state
- transform an existing idea, national spirit, or mechanic stage into a stronger or weaker form
- connect to later events, focus routes, super-events, or country identity changes

Tiny modifiers are allowed only when they belong to a visible stacking system, frequent tick, temporary crisis push, dynamic scaling formula, or larger effect package. They should never be the whole reward for an important decision, mission, GUI button, formable step, route unlock, or crisis response.

If a decision family has many small rewards, combine them into fewer stronger actions, convert them into staged idea upgrades, make them change a visible mechanic value. Do not scatter small bonuses across a category to create the appearance of progress.

Starting penalties and negative mission outcomes must also matter. A failed objective, broken authority value, bad crisis decision, or starting debuff should create pressure the player must answer. Harmless negative modifiers that can be ignored are not valid crisis design.

Scripted GUI presentation cannot compensate for weak gameplay. Do not use glowing buttons, animated seals, long tooltips, or dramatic localisation to make a tiny effect look important. If the action is important enough to receive custom presentation, its gameplay effect must be important too.

## 5. Cost and sacrifice design

Political power and command power are allowed, but they should not be the default answer.

Use varied costs that fit the action:

- army XP
- navy XP
- air XP
- command power (can't be expensive, command power costs must be conservative. A decision can't cost more than 60 command power)
- political power only when the action is genuinely bureaucratic or political
- infantry equipment
- support equipment
- artillery
- trucks
- trains
- convoys
- aircraft
- ships
- tanks
- fuel (don't use conservative values)
- manpower
- stability
- war support
- local support
- legitimacy
- faction cohesion
- foreign influence debt
- intelligence exposure
- supply strain
- temporarily tied-down divisions
- civilian factory burden
- military factory output loss
- dockyard commitment
- construction capacity
- rail access
- depot control
- port control
- route access
- deadlines
- map objectives

A military crackdown may use command power, but it should also strain units, consume equipment, risk stability, or affect local resistance when appropriate.

A foreign aid decision may use political power, but it should also require relations, convoys, equipment, route access, consumer goods burden, intelligence exposure, or patronage risk.

A mobilisation decision may require manpower, equipment, training time, supply, local support, or unit placement.

## 15.6 Reward dumps and exploit checks

Avoid one-time reward dumps as the main decision or mission design. A decision or mission can give units, equipment, factories, buildings, resources, or influence, but important decisions should usually connect to a repeatable system, timed objective family, mechanic value, advisor path, route branch, or long-term gameplay loop.

A large decision system should not become a sequence of buttons that only give free rewards.

A large decision system should also not become a sequence of tiny fairy-dusted rewards. Repeated minor modifiers, token stockpiles, small stability changes, and tiny production nudges are not better than reward dumps when they do not change play. Treat low-impact reward dust as a design failure unless it is part of a visible cumulative system with clear thresholds and consequences.

Balance review must include exploit checks and impact checks. The question is not only whether the decision can be abused. The question is also whether a reasonable player would notice the reward, care about the failure, and plan around the system.

Check for:

- repeatable rewards without meaningful cost
- free unit loops
- cheap factory construction loops
- equipment farming
- influence farming
- puppet abuse
- war-goal spam
- claim or core spam
- advisor discount stacking
- bypass abuse
- repeated mission success farming
- decisions that can be clicked without real risk
- AI taking decisions that create broken loops

Fix exploits with route locks, flags, cooldowns, dynamic costs, limited targets, escalating costs, one-time completion flags, scripted triggers, AI limits, or cleanup effects.


