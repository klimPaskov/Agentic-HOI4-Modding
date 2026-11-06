# HOI4 Focus Trees: Opening and pacing

Part of the [hoi4-focus-trees](../SKILL.md) skill. Read before designing a tree's opening, starting national spirits, the first choices, or focus durations.

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

Focus `cost` counts weeks, because `FOCUS_POINT_DAYS = 7`, so `cost = 10` takes 70 days. [vanilla-confirmed 1.19.3]

Do not split one 70-day reward into two 35-day focuses when the player gains no new choice, requirement, event, or mechanic between them. More clicks do not create more depth.

A short focus should earn its place through a meaningful choice, immediate action, new requirement, new event, temporary opportunity window, or route change. Reject short filler focuses that only divide one reward into several buttons.

