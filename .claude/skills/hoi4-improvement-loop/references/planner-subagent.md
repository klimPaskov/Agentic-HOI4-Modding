# HOI4 Improvement Loop: Planner and patch subagents

Part of the [hoi4-improvement-loop](../SKILL.md) skill. Read before launching the improvement loop planner, acting as one, or delegating small improvement patches.

## Subagent behavior

Use `hoi4_improvement_loop_planner` when the parent agent wants a helper to write feature expansion addenda. That planner writes design handoffs under `docs/plans/<feature_slug>/`. It should not edit gameplay files, localisation files, GUI files, scripted effects, focus trees, decisions, assets, or external records.

The planner should be deployed during implementation when a large event has gained enough new content that the design needs a second pass. It should use `hoi4-feature-planning` to expand the idea deeply, research historical and regional connections, define mechanics that the main agent can implement, and explain how the addendum should be promoted into specs if accepted.

The planner should not be deployed again for the same feature until its previous addendum has been implemented, folded into specs, queued with a reason, or rejected with a reason. Audit subagents should point to the latest unresolved addendum before asking for another planner pass.

Audit subagents should use this skill when they find shallow design. They may include a compact improvement handoff in their audit. If the gap is broad enough to require new design, they should recommend `hoi4_improvement_loop_planner` or write a bounded plan if the parent explicitly asked for that kind of audit output.

Patch-capable subagents are active by default for small, file-specific improvements inside the current task scope. Examples include varied costs, clearer dynamic localisation, safer AI weights, missing trigger tooltips, small helper calls, cleanup hooks, route-aware icon references, and obvious formable requirement fixes. They should not expand a whole mechanic through a small patch. For broad expansions, they should write a plan handoff and leave implementation to the main agent.

