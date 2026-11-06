# HOI4 Focus Trees: Audit, documentation and handoff

Part of the [hoi4-focus-trees](../SKILL.md) skill. Read before reporting completion, running the focus audit, writing focus-tree documentation, reviewing rewards for exploits, or handing off a subagent patch.

## 5.7 Achievement hooks and route coverage proof

Large focus trees should include achievement hooks for difficult route completions, rare branch combinations, expansion outcomes, successful internal reform, avoiding foreign dependency, forming leagues, surviving high-chaos paths, or completing hard late-game ambitions.

For every major focus tree, the completion report must include a route coverage table comparing the spec's required routes against implemented routes.

Required table columns:

| Required route | Implemented route or focus branch | Status | Notes |
| --- | --- | --- | --- |

Missing, renamed, merged, simplified, fallback, or replaced routes must be reported.


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


## Subagent patches for focus trees

Focus tree subagents are active small-patch agents by default inside the current task scope. They can patch prerequisite fixes, mutual exclusion fixes, bypasses, route locks, AI weights, icon references, focus filters, localisation keys, small reward variety, existing decision hooks, and existing formable unlock hooks without waiting for a separate permission prompt.

They should not redesign a whole tree, add a full route family, create a new formable chain, or change the country identity. When the tree needs broader depth, they should write an improvement plan under `docs/plans/<event_id>_<event_slug>_plans/` and leave implementation to the main agent.

Every patch must write a handoff with changed files, changed focus ids, route behavior before and after, meaningful validation, skipped task-specific validation, and remaining route risks.

## 16. Documentation and audit

Before the focus audit, run `python -B .tools/check.py quick` on the changed files and fix every error it lists; it checks localisation keys, icon and sprite wiring, script syntax and MCP script validation, not route logic or layout, which stay with `hoi4.focus_inspect` and the auditor.

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
- opening structure and first meaningful choices
- national constraints and the route answers they create
- focus duration logic
- temporary power windows and aftermath
- interactive focus requirements
- limited-war rules when used
- civil-war handling when used
- leader or institution customization when used

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
- authored gameplay values that are not rounded to multiples of 5 without a documented exception
- routes that can hold more than three focus-tree-created national spirits at once
- focus-tree asset sets that reuse the same colour palette across distinct branches
- dead-end branches with no capstone, convergence, or follow-up gameplay
- national spirits that are too easy to earn for their importance
- national spirits that have no lifecycle, route commitment, mechanic hook, or decision hook
- layout readability
- overlapping focus boxes, overlapping connectors, or intersecting path lines
- long prerequisite lines that could be shortened by repositioning focuses
- fake non-linearity created by offsetting an otherwise linear chain
- unnecessary ladder, staircase, zigzag, or decorative detour layouts
- asymmetric sibling branches or off-center route families without a real structural reason
- unnecessary starting spirit stacks or military setup complexity
- an opening that exposes too many choices before the player understands the country problem
- first meaningful choices delayed behind filler focuses
- political routes added only to satisfy an ideology quota
- focus durations that do not match the decision or reward
- several consecutive focuses with no choice, requirement, event, map objective, or mechanic interaction
- national constraints erased before they shape a route
- underused branches with no cross-branch utility
- temporary bonuses with no stated window, cost, or aftermath
- permanent extreme policies with no exit when an exit should exist
- interactive gates that are arbitrary, unclear, or impossible to pursue intentionally
- external-event gates that can permanently strand a branch
- optional side investments made mandatory without a route reason
- early-war routes that force total war when a limited objective is intended
- limited wars without peace, escalation, AI, cleanup, or postwar rules
- repeated or uncontrolled civil wars
- leader customization that produces one dominant trait stack

