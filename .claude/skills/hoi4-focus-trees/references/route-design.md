# Route visibility, pacing, tradeoffs, and failure states

This reference belongs to the `hoi4-focus-trees` skill and holds complete sections moved out of `SKILL.md` to keep it within the single-read ceiling. Every rule here is as binding as the rules in `SKILL.md`.

## 5.8 Route visibility, pacing, tradeoffs, and failure states

A major route should leave visible evidence in the game. This can include map changes, new decisions, new units, new advisors, changed leader, changed flag, changed cosmetic name, new faction behavior, new focus availability, changed diplomacy, or a visible mechanic. A route that only changes hidden variables or tiny modifiers is not meaningful.

Large focus trees should have early, middle, and late pacing.

- Early focuses solve survival, first institutions, first units, first industry, and basic identity.
- Middle focuses create route mechanics, meaningful choices, decision families, military systems, diplomacy, and branch interaction.
- Late focuses deliver major payoffs, expansion, faction or League outcomes, high-chaos routes, postwar settlement, or world-order ambitions.

Every major route should have a tradeoff. A military route may reduce freedom or legitimacy. A foreign-aid route may increase dependency. An expansion route may create resistance or foreign backlash. An industry route may consume civilian capacity or weaken short-term defense. A high-chaos route may give power while damaging stability, diplomacy, or normal politics.

Do not overuse mutual exclusions. Mutually exclusive paths should represent real identity changes, strategic commitments, or incompatible institutions. Support branches like industry, army, diplomacy, and logistics should usually coexist unless the route logic says otherwise.

Important routes should define failure states. A failed political reform can empower radicals. Failed expansion can trigger backlash or settlement. Failed industry can create dependency. Failed foreign-aid balancing can create a client state. Failed military centralization can create rogue generals or militias.

Focus and decision localisation should tell the player the visible baseline effect of the route or action. It should not reveal hidden effects, secret outcomes, hidden variables, or future surprises. The player should understand what the focus visibly does, such as moving toward military rule, opening an industry program, unlocking a public diplomatic route, forming a League office, or preparing border claims, without being told about hidden follow-up effects.


### Strategic time horizons

Important early branches should offer different time horizons when the country concept supports them.

A useful three-way structure is:

- a short-term gamble that gives immediate military, industrial, or diplomatic power with a clear later cost
- a balanced route that gives moderate permanent strength and lower risk
- a long-term investment that delays power for a larger later payoff

Do not make the long-term option automatically correct. The short-term route needs a real campaign use, and its later cost should be serious enough that timing matters.

Possible costs include production exhaustion, resource consumption, consumer-goods burden, debt, foreign dependency, lower efficiency growth, weaker research, reduced civilian construction, political instability, or a timed obligation to act.

### Temporary power windows and aftermath

Large bonuses are allowed when their duration, cost, and aftermath create a real decision.

A temporary power focus should define:

- what the player is expected to accomplish during the window
- the exact public duration or end condition
- the resource, political, or military pressure created while it is active
- what happens when the window closes
- whether the player can prepare for, reduce, or accept the aftermath
- how AI decides when the window is worth using

A strong construction surge can consume more fuel or resources and leave an exhausted economy. A short-war plan can give immediate factories and output, then reduce efficiency or civilian capacity after the campaign window. A naval surge can improve dockyard output while reducing factory output.

Do not hide the basic tradeoff. The player should understand the public cost before committing.

Permanent extreme policies should usually have an exit, replacement, or later reform route. A permanent penalty is acceptable when it defines the final country identity and the player knowingly commits to it.

### Interactive focus requirements and anti-autopilot play

Use existing game systems when they make a focus feel earned.

Good focus requirements can ask the player to:

- reach a visible relations threshold with named countries
- control a named state, port, rail hub, or resource area
- produce or stockpile a meaningful amount of trucks, trains, aircraft, ships, or other relevant equipment
- place a capital ship in port
- maintain a law, trade policy, or economy policy
- build compliance or local support in named territory
- complete a decision, mission, special project, or diplomatic action
- keep a supply route open
- field a route-specific unit or template
- survive a timed commitment

The requirement must connect directly to the payoff. A truck stockpile can gate a logistics program. Relations can gate foreign construction aid. Compliance can gate integration. A capital ship can support a temporary power-generation or prestige scheme.

Do not use arbitrary requirements that force unrelated busywork.

Every non-obvious gate needs clear localisation. Tell the player the exact target, amount, state group, law, or action required.

When a difficult gate is central to the route, give the player tools to pursue it. A formable that needs compliance can unlock costly compliance decisions. A foreign investment route can unlock relation-building actions. A naval gate can provide a clear shipbuilding or acquisition route.

A focus chain has become autopilot when several consecutive focuses require no new choice, no changed build, no map objective, no decision, no event, and no interaction with the country mechanic. Merge, shorten, or redesign such chains.

### Optional investment and safe stopping points

Support branches should allow selective investment.

Do not require every side focus when one or two choices are enough to establish the route. The player should often be able to choose one sponsor, one military preparation, or one industry method and continue.

A branch can contain deeper optional investments for players who want to specialize. The player should also have a clear stable point where they can stop without leaving the country broken or the main route blocked.

Large risk policies should be optional unless the country's concept makes them unavoidable. A player who declines an extreme construction surge, naval conversion, foreign dependency deal, or total mobilization scheme should still have a coherent route forward.

### Commitment mechanics

A focus can start a timed commitment instead of granting a flat reward.

Examples include war fervor, public credit, mobilization pressure, emergency production, national savings, rearmament promises, or a diplomatic deadline.

A commitment mechanic should:

- build a visible benefit over time
- require the player to act before a deadline or threshold
- create a consequence when the promise is abandoned
- offer decisions or focuses that help manage the commitment
- give AI a clear condition for entering, fulfilling, or cancelling it

Use consequences that fit the commitment. Do not default every missed deadline to a civil war.
