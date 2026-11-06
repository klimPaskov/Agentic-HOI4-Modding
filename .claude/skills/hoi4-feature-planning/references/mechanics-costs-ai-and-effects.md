# HOI4 Feature Planning: Mechanics, costs, AI and effects

Part of the [hoi4-feature-planning](../SKILL.md) skill. Read before designing dynamic values, costs and sacrifices, AI behaviour or effect strength.

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

