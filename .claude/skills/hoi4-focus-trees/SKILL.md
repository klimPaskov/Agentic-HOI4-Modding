---
name: hoi4-focus-trees
description: Use when designing, implementing, auditing or fixing Hearts of Iron IV national focus trees, including routes, branches, prerequisites, layout, rewards, ideas, AI and localisation.
---

# HOI4 Focus Trees

Use this skill when a task touches national focus trees, focus-tree loading, focus effects, focus layout, focus localisation, focus icons, focus AI, focus-tree documentation, or event-created country trees.

Use this skill together with:

- `AGENTS.md` for repository-wide rules
- `hoi4-events` when the tree belongs to an event
- `hoi4-decisions-missions` when focuses unlock, modify, or depend on decisions and missions
- `hoi4-feature-assets` when focus icons, leader portraits, flags, or idea icons are required
- `hoi4-improvement-loop` when a tree needs broader route depth or a near-completion anti-bloat pass
- `hoi4-subagents` before routing focus audits, improvement plans, or active small patches
- the installed `hoi4-agent-tools` MCP server for mandatory `hoi4.focus_inspect` and `hoi4.focus_render` work, plus bounded `hoi4.focus_rewrite` work. Use it to inspect, render, lint, compare, and improve focus-tree structure, then review every returned layout and diagnostic. Route every in-scope focus-weight audit through `hoi4_ai_probability_auditor`. If the required MCP route is unavailable, record the exact blocker and do not treat source-only review as equivalent. MCP does not replace required source review, wiki and vanilla documentation checks, repository validation, or parent review.

This file is a router: it keeps the rules every focus-tree task needs and points to the references that hold the rest of the standard. References are as binding as this file, and no rule was dropped.

How to work:

1. Before touching any focus file, apply "1. Required checks" and "2. Prerequisite semantics" below. Never rely on memory for prerequisite, layout, AI or search-filter behaviour.
2. When planning the route set, read [branch-structure](references/branch-structure.md) and [opening-and-pacing](references/opening-and-pacing.md), then [route-design](references/route-design.md) for visibility, pacing, tradeoffs and failure states.
3. For a specific part, open the matching reference in the map. Rewards, ideas and national spirits are in [rewards-and-ideas](references/rewards-and-ideas.md).
4. Before placing focuses or changing coordinates, read [layout-rules](references/layout-rules.md). Layouts must be compact and symmetrical with short direct connectors and no overlaps, fake non-linearity or decorative ladders.
5. Before reporting completion, read [audit-documentation-and-handoff](references/audit-documentation-and-handoff.md) and then [completion-rules](references/completion-rules.md). Run `python -B .tools/check.py quick` first.

Costly to miss (full text in the references): a branch is real only with several focuses, a mechanical unlock, a meaningful choice and a payoff, and terminal focuses must be real capstones. No political routes to fill an ideology quota. Focuses must unlock gameplay, not only flat modifiers or one-time reward dumps. Every major route needs its own AI, localisation tone and a safe way out when an external event never happens.

## Reference map

- [Branch structure and depth](references/branch-structure.md): Read before planning a tree's branch set, judging whether a branch is real, or adding side branches, spurs and terminal focuses. Covers: Focus tree design purpose; Route plausibility and ideology restraint; Major country tree requirements; Branch interaction and payoff; Real branch depth standard.
- [Opening and pacing](references/opening-and-pacing.md): Read before designing a tree's opening, starting national spirits, the first choices, or focus durations. Covers: Lean opening, national constraints, and staged complexity.
- [Country identity, AI and localisation](references/country-identity-and-postwar.md): Read before a route changes the visible country package (leader, flag, advisors), before writing route AI, localisation or icons, or for event-created countries. Covers: Country identity changes; Route-specific AI and localisation tone; Geography, postwar handling, and advisor routing; Event-created versus existing countries; AI behavior; Localisation and icons.
- [Special mechanics and shared trees](references/special-mechanics.md): Read before tying focuses to a country mechanic, balance of power or faction rules, building a mechanic GUI or focus inlay, or sharing a tree between countries. Covers: Special mechanics, values, and faction rules; Mechanic presentation, validity, and shared-tree rules.
- [Focus and decision integration](references/decision-integration.md): Read before a focus unlocks, modifies or stages decisions and missions. Covers: Decision category clutter control; Focuses and decisions must interconnect.
- [Expansion and limited war](references/expansion-and-limited-war.md): Read before designing an expansion, reunification or settlement branch, or an early limited war. Covers: Distinct expansion branch; Early action and limited-war architecture.
- [Political depth and route locks](references/political-depth-and-route-locks.md): Read before designing political branches, leader customization, civil war or internal conflict, mutual exclusions, or gates on external events. Covers: Political depth; Leader and institution customization; Civil war restraint and controlled internal conflict; Route locks and mutual exclusions.
- [Formable routes and addenda](references/formable-routes.md): Read before a focus tree prepares, reveals or completes a formable nation, uses animated leader portraits, or is deepened by an addendum. Covers: Focus routes that lead to formable nations; Formation route architecture; Focus rewards tied to formation decisions; Animated leader portraits and visual route payoffs; Improvement addenda and formation routes.
- [Audit, documentation and handoff](references/audit-documentation-and-handoff.md): Read before reporting completion, running the focus audit, writing focus-tree documentation, reviewing rewards for exploits, or handing off a subagent patch. Covers: Achievement hooks and route coverage proof; Reward dumps and exploit checks; Subagent patches for focus trees; Documentation and audit.

## Core design baseline

A strong focus tree should:

- introduce one or two manageable starting problems for a stable small or medium country
- begin with a small set of clear choices and reveal more complexity later
- use 35-day focuses for early strategic forks, focused reforms, and short opportunity windows
- give concrete rewards the player can feel immediately
- offer distinct strategies, including short-term power and long-term growth when the country supports that choice
- allow strong bonuses when the cost, duration, and aftermath are clear
- keep optional support investments skippable unless full commitment defines the route
- use existing systems such as diplomacy, production, supply, laws, compliance, stockpiles, and map control
- provide meaningful early action through war, diplomacy, internal politics, construction, intervention, or another active objective
- end major goals with a visible payoff such as territory, cores, a formable, a new government, a faction, or a lasting mechanic
- use a compact, symmetrical layout with short direct connectors that show the real route structure without visual tricks

At normal in-game zoom, a reviewer should be able to identify every supported major family from the render alone: opening trunk, politics and its forks, industry/economy, military with army/navy/air where relevant, diplomacy or faction, expansion or settlement, special mechanics, and late-game payoff. Give every visible focus one primary branch home or an explicit convergence role. If a branch cannot be understood without tracing every connector or reading every tooltip, redesign the route, names, icons, or layout before completion.

Large trees must use the current engine's focus search filters consistently. Give each focus accurate `search_filters` tags that match its primary role, and use Focus Navigation shortcuts for spatially separate major branch families. Each shortcut needs a localized label, distinct icon, stable branch anchor, useful pan/zoom target, and reveal-safe visibility. Navigation does not excuse interleaved or meaningless routes.

Reject trees that:

- overload the opening with penalties, currencies, national spirits, templates, or specialist mechanics
- expose too many branches before the player understands the country
- use long chains of small standalone modifiers as filler
- present a choice where one option dominates in nearly every plausible campaign
- create shallow ideology paths to fill a political quota
- leave meaningful content dependent on one foreign AI action
- delay the country's main premise through years of generic preparation
- use repeated or uncontrolled civil wars
- rely on automatic reward dumps as the main progression model
- encourage focus clicking without changing the player's build, objectives, decisions, or strategy
- fake non-linearity by offsetting a linear chain or routing long prerequisite lines around focuses
- use unnecessary ladder, staircase, zigzag, or decorative connector patterns to suggest depth
- allow overlapping focuses, overlapping connectors, intersecting path lines, or connectors that cross unrelated branches
- use long path lines when the same prerequisite can be shown with a shorter and cleaner placement

The duration and reward rules need context. A 35-day focus works when the click creates a real choice, action, event, requirement, or opportunity. A 5 percent modifier can be meaningful when it affects a sensitive statistic, supports a larger reward package, contributes to a visible stacking system, or completes an idea lifecycle. Repeated small standalone rewards remain a design defect. Early action can be military, diplomatic, political, industrial, or crisis-driven.

## 1. Required checks

Before editing focus files:

- Verify live schemas for `hoi4.reference_context`, `hoi4.reference_search`, `hoi4.reference_read`, and `hoi4.source_lookup`. Request focus context, locate exact rules, and read pertinent cited sections of National focus modding and installed game documentation. Retain source paths, lines, and revisions. Resolve any live `omittedSources` by raising the context limit or targeted search/read before claiming source coverage; `missing` denotes absent files. If a route is unavailable, use targeted local reads and record the exact gap; do not claim the MCP retrieval ran.
- Treat installed vanilla documentation as primary for syntax and inspect an exact vanilla focus precedent. Reference retrieval does not replace focus inspect/render evidence or the weighted-logic audit.
- Inspect existing repository focus trees and feature-created focus-tree loading patterns.
- Read `AGENTS.md`.
- Read `hoi4-decisions-missions` when focuses unlock decisions, timed objectives, missions, or dynamic mechanics.

Do not rely on memory for prerequisite behavior, layout behavior, AI syntax, or search filters.

## 2. Prerequisite semantics

HOI4 focus prerequisites are easy to invert.

This means OR:

```txt
prerequisite = { focus = a focus = b }
```

This means AND:

```txt
prerequisite = { focus = a }
prerequisite = { focus = b }
```

Use vanilla examples before changing complex prerequisite and mutual-exclusion structures.

- Declare `mutually_exclusive` on both focuses, since all 2,614 vanilla pairs are symmetric. [vanilla-confirmed 1.19.4.1]
- Focus ids are unique across the project, as the 10,676 vanilla focus nodes carry 10,676 distinct ids. [vanilla-confirmed 1.19.4.1]
- `allow_branch` hides a branch of the tree (543 vanilla uses). [vanilla-confirmed 1.19.4.1]
- Continuous focuses live in the palette files under `common/continuous_focus/`, and no vanilla focus node declares itself continuous. [vanilla-confirmed 1.19.4.1]

## 4. Path-level implementation

Use path-level design unless the user explicitly asks for a focus-by-focus blueprint.

The spec usually defines:

- route families
- branch logic
- anchor focuses or focus groups
- mutual exclusions
- reward style
- idea lifecycles
- route end states
- AI behavior

The implementation agent owns:

- final focus count
- final focus names
- x/y positions
- exact prerequisites
- bypasses
- detailed focus connections
- clean in-game layout
- symmetrical branch geometry and centered route families
- the shortest clean connector path for every prerequisite relationship
- removal of overlapping focuses, intersecting lines, fake branches, and unnecessary layout ladders

The final tree must preserve the route logic and gameplay intent from the spec.

## 5.8 Route visibility, pacing, tradeoffs, and failure states

Read [`references/route-design.md`](references/route-design.md) before designing route visibility, pacing, tradeoffs, or failure states. It contains the complete standard for this section and its subsections.

## 8. Focus reward diversity

Read [`references/rewards-and-ideas.md`](references/rewards-and-ideas.md) before writing focus rewards, ideas, or national spirits. It contains the complete standard for this section and its subsections.

## 9. Idea lifecycle

Read [`references/rewards-and-ideas.md`](references/rewards-and-ideas.md) before writing focus rewards, ideas, or national spirits. It contains the complete standard for this section and its subsections.

## 12. Layout rules

Read [`references/layout-rules.md`](references/layout-rules.md) before placing focuses, changing coordinates, or reviewing a rendered tree layout. It contains the complete standard for this section and its subsections.

## 17. Completion rules

Read [`references/completion-rules.md`](references/completion-rules.md) before claiming any focus-tree work is complete. It contains the complete standard for this section and its subsections.

