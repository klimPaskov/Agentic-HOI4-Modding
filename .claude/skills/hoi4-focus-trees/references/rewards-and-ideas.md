# Focus rewards and idea lifecycle

This reference belongs to the `hoi4-focus-trees` skill and holds complete sections moved out of `SKILL.md` to keep it within the single-read ceiling. Every rule here is as binding as the rules in `SKILL.md`.

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

When a focus grants, unlocks, removes, or redirects a technology, doctrine, or research bonus, use `hoi4.tech_inspect` in `impact`, `unlocks`, or `bonus_coverage` mode to verify the linked graph and references. Render the affected folder or branch with `hoi4.tech_render`, then use `hoi4.tech_inspect` with `mode: "compare"` after source edits. Treat missing assets, disconnected prerequisites, misplaced items, exclusivity errors, and unresolved dynamic behavior as implementation findings instead of guessing.

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

A 5 percent modifier can be meaningful when the affected statistic is sensitive, the effect belongs to a larger reward package, the route builds a visible stack toward a threshold, or the modifier completes a staged idea. Judge the gameplay impact and context, not the number in isolation.

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

A focus tree must never grant or maintain more than three focus-tree-created national spirits at the same time for one country. This is a hard maximum. Treat three as an upper bound.

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
- a failure, corruption, radicalisation, dependency, or high-chaos form when the route goes badly
- decision or mission hooks that make the spirit more than passive stats
- mechanic value hooks, such as legitimacy, cohesion, authority, readiness, recognition, corruption, panic, or local support
- route-specific localisation and icon direction
- clear AI priority for solving, exploiting, upgrading, or avoiding it

Reject a tree if it has many easy-to-achieve national spirits that feel unrelated, passive, or unrewarding. Merge them into one staged institution, convert some into timed modifiers, move some effects into decisions or missions, or require a stronger route commitment before granting them.
