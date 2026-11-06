---
name: hoi4-decisions-missions
description: Use when designing, implementing, auditing, or fixing HOI4 decisions, missions, timed objectives, decision categories, costs, cost and mission localisation, AI weights and balance.
---

# HOI4 Decisions and Missions

Use this skill when a task touches decisions, missions, timed objectives, decision categories, mission UI, costs, trigger tooltips, scripted localisation, AI decision behavior, or balance around decision-driven systems.

This skill is for implementation and cleanup. For broader event wiring, use `hoi4-events`. For focus trees, use `hoi4-focus-trees`. For visual assets, use `hoi4-feature-assets`. For scripted GUI composition, layout, and visual evidence, use [hoi4-scripted-gui](../hoi4-scripted-gui/SKILL.md).

For large or reworked decision systems, spawn `hoi4_decision_mission_auditor` after implementation and before completion. The subagent is patch-capable by default inside the current task scope. It should audit objective quality, costs, tooltips, AI validity, cleanup, duplicate missions, route integration, fairy-dust rewards, exploit risk, localisation, and balance evidence. Route every in-scope decision or mission weight to `hoi4_ai_probability_auditor` for the mandatory MCP probability pass. The probability auditor remains read-only. The decision auditor may directly patch small decision, mission, tooltip, dynamic localisation, AI, cleanup, cooldown, visibility, and existing formable requirement issues when the fix is local and clearly safer.

Read the required reading and the core design rule below, then open the reference for the phase you are in. Every reference holds complete rules moved verbatim out of this file, and each rule there is as binding as a rule here.

Workflow:

1. Design: read the core rule and the types below, then [values-costs-and-rewards.md](references/values-costs-and-rewards.md) and, for missions, [mission-design.md](references/mission-design.md).
2. Implement: open the reference for triggers, cost text, focus integration, mechanic values, influence and formation, AI and localisation as each comes up (see the map).
3. Before reporting completion, read [completion-and-balance-review.md](references/completion-and-balance-review.md), run the duplicate-mission audit and the quick check, and for large or reworked systems spawn the auditors named above.

Rules that always apply (short form, the full text is in the named reference):

- A reward or penalty must change play. No store of tiny stat modifiers (plus 1 percent and the like), no political-power-only pricing, no scripted GUI polish standing in for a weak effect, and one-time reward dumps are not the main pattern ([values-costs-and-rewards.md](references/values-costs-and-rewards.md)).
- Costs are dynamic and varied. A decision cannot cost more than 60 command power. An action spends at most four distinct resource types, and no fifth payment may hide in a tooltip or effect ([values-costs-and-rewards.md](references/values-costs-and-rewards.md), [cost-localisation-and-payment.md](references/cost-localisation-and-payment.md)).
- Inline cost text shows at most three values, each with its texticon, and no filler words between them. Display, affordability gate and debit must agree ([cost-localisation-and-payment.md](references/cost-localisation-and-payment.md)).
- Requirements name their places or a named region. Long triggers become scripted triggers, custom tooltips or short summaries ([trigger-clarity-and-engine-facts.md](references/trigger-clarity-and-engine-facts.md)).
- Missions are real actions, never passive checklists. Goal-style missions auto-complete without a second click. Easy missions last at least 90 days and timers vary. Every decision-level `modifier` needs `days_remove` ([mission-design.md](references/mission-design.md)).
- Every important decision or mission family needs AI behavior (analysed through `hoi4_ai_probability_auditor`), lifecycle cleanup and complete localisation that never mentions implementation history ([ai-lifecycle-and-localisation.md](references/ai-lifecycle-and-localisation.md)).
- Never report completion with simplifications, placeholders or blockers left unreported.

Existing references, still current: [scripted-gui-decision-surfaces.md](references/scripted-gui-decision-surfaces.md) and [formable-nation-decisions.md](references/formable-nation-decisions.md), each introduced by a pointer section below.

## Reference map

- [Values, costs and rewards](references/values-costs-and-rewards.md): Read before choosing a decision's costs, dynamic values, rewards or penalties, and when checking a system for reward dust and exploits. Covers: Dynamic values; Effect strength and no fairy-dust rewards; Cost and sacrifice design; Reward dumps and exploit checks.
- [Cost localisation and payment](references/cost-localisation-and-payment.md): Read before writing cost text, custom_cost_text keys, affordability gates, debits or refunds for a paid decision. Covers: Cost localisation.
- [Trigger clarity and engine facts](references/trigger-clarity-and-engine-facts.md): Read before writing available, visible, allowed or target triggers and the requirement text the player sees. Covers: Trigger and requirement clarity.
- [Mission design](references/mission-design.md): Read before designing a mission's objective, duration, native timer, outcomes or active-mission cap. Covers: Mission quality; Mission duration; Success, failure, and partial success; Objective capacity.
- [Influence decisions, stackable ideas and formation missions](references/influence-ideas-and-formation-missions.md): Read before writing foreign aid or intervention decisions, mission-driven idea upgrades, or integration missions after a formable (the formation decision itself is in formable-nation-decisions.md). Covers: Influence, aid, and intervention decisions; Stackable ideas from missions; Formation missions and integration projects.
- [Focus integration and category progression](references/focus-integration-and-category-progression.md): Read before tying a decision family to a focus route, or deciding how a category deepens, paces and differs by route. Covers: Focus and decision integration; Progressive decision categories; Route-aware decision depth; Decision pacing, tradeoffs, and visible effects.
- [Mechanic values, factions and category clutter](references/mechanic-values-and-category-clutter.md): Read before adding special mechanic values, faction or league goals, value breakdowns, or deciding which decisions a category shows at once. Covers: Special mechanic values and faction goals; Mechanic presentation, value clarity, and faction outcomes; Decision category clutter control.
- [Animated category presentation and improvement addenda](references/animated-presentation-and-addenda.md): Read before animating a decision category or turning an improvement addendum into decisions and mechanic windows. Covers: Animated decision category presentation; Improvement addenda for decisions and mechanic windows.
- [AI, lifecycle cleanup and localisation](references/ai-lifecycle-and-localisation.md): Read before writing ai_will_do for decisions and missions, cleanup of ended systems, or decision and mission localisation. Covers: AI behavior; Category cleanup and lifecycle; Localisation requirements.
- [Balance review and completion report](references/completion-and-balance-review.md): Read before reporting completion, before the balance review, and before delegating patches to decision subagents. Covers: Duplicate mission cleanup; Balance review; Subagent patches for decision systems; Completion report.

## 1. Required reading

Before editing decisions or missions, read:

- `AGENTS.md`
- relevant cited sections found through the live schemas of `hoi4.reference_context`, `hoi4.reference_search`, and `hoi4.reference_read`: Decision modding and whichever trigger, effect, localisation, modifier, scope, or data-structure rule the task uses. Keep paths, lines, and revisions. Resolve any live `omittedSources` by raising the context limit or targeted search/read before claiming source coverage; `missing` denotes absent files. Use `hoi4.source_lookup` for exact definitions and usages. If a route is unavailable, read the pertinent local sections directly and record the exact gap.
- vanilla decision files from `C:/Program Files (x86)/Steam/steamapps/common/Hearts of Iron IV/`
- vanilla documentation in `C:/Program Files (x86)/Steam/steamapps/common/Hearts of Iron IV/documentation`
- existing repository decision categories and scripted effects that do similar work
- `.claude/skills/hoi4-decisions-missions/templates/formable_state_puzzle/README.md` and its category-attachment audit when exact state control is the formation proof

Do not rely on memory when syntax or UI behavior is documented.
Installed vanilla documentation remains the primary syntax authority; inspect an exact vanilla precedent. Reference retrieval does not replace decision scenarios, weighted-logic comparisons, or required UI evidence.

## 2. Core design rule

A decision or mission should represent something the country is actually doing. Decisions should also connect to focus routes and wider mechanics instead of sitting as isolated buttons.

Avoid turning decisions into a store where the player spends political power for small modifiers. Do not make a decision category feel like a tray of tiny stat dust. A good decision or mission usually asks the player to commit resources, move units, hold a location, secure supply, manage foreign access, spend equipment, accept risk, meet a deadline, or change a living pressure system.

A mission should feel like an order or objective. A decision should feel like a meaningful choice.

## 3. Decision and mission types

Use the right tool for the job.

### Clickable decisions

Use clickable decisions when the player chooses to start an action, spend resources, accept risk, begin a project, send aid, escalate, negotiate, or select a target.

Clickable decisions should have clear costs, clear requirements, and clear consequences.

### Timed missions

Use timed missions when the player needs to achieve something before a deadline.

Timed missions are good for:

- holding capitals
- guarding borders
- securing rail hubs
- placing divisions in named states
- maintaining supply
- blocking foreign routes
- completing local support work
- holding a depot belt
- preventing a cascade
- proving authority before an enemy does

### Goal-style auto-completing objectives

Use goal-style missions when the player should not click again after doing the work.

If the objective is "place divisions here," "hold this capital," "secure this rail hub," or "reach this influence threshold," it should auto-complete when conditions are met.

Do not make the player pay a second click after already satisfying the goal.

## Decision category presentation hierarchy

Read [`references/scripted-gui-decision-surfaces.md`](references/scripted-gui-decision-surfaces.md) whenever a decision system uses a scripted GUI category, a mechanic window, or a category presentation choice. It contains the complete standard for this section and its subsections.

## Formable nation decisions

Read [`references/formable-nation-decisions.md`](references/formable-nation-decisions.md) whenever a decision system forms, unifies, or restores a nation. It contains the complete standard for this section and its subsections.

## Scripted GUI decision categories and mechanic windows

Read [`references/scripted-gui-decision-surfaces.md`](references/scripted-gui-decision-surfaces.md) whenever a decision system uses a scripted GUI category, a mechanic window, or a category presentation choice. It contains the complete standard for this section and its subsections.

