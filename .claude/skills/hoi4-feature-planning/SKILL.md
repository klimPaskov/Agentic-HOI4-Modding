---
name: hoi4-feature-planning
description: Use when expanding a Hearts of Iron IV mod feature idea into a deep, implementation-ready specification covering focus trees, decisions, AI, achievements and asset prompts, before coding.
---

# HOI4 Feature Planning

Use this skill to design or expand features for a Hearts of Iron IV mod.

This skill creates feature specifications. It does not implement code. Implementation belongs to the owning implementation skill for the surface being designed, such as `hoi4-events` for event content, `hoi4-focus-trees` for focus trees, `hoi4-decisions-missions` for decisions and missions, and repository-specific implementation rules for other systems. Visual asset generation and processing belongs to `hoi4-feature-assets`. Animated sprite planning, frame-sheet requirements, animated portrait packages, and animation handoff details belong to `hoi4-frame-animation` when motion is needed. Quote, remark, and audio research belongs to `hoi4-text-audio-research`.

Treat the accepted specification as the design source of truth. Plans, prompts, manifests, audits, and handoffs may refine or report it, but an accepted design change must be promoted into the relevant spec or explicitly queued/rejected with a reason. Keep implementation prompts context-complete: pass stable feature identifiers, exact spec/plan paths, file ownership, outputs, dependencies, named MCP evidence requirements, known blockers, and forbidden simplifications instead of relying on inherited chat context.

This file is a router. It keeps the preconditions and the rules that apply to every spec, and every other design standard sits, moved verbatim, in exactly one reference below. Open the reference that matches the part of the spec you are writing.

Always apply:

- Give text direction, never pasteable localisation, sample lines or draft wording (`spec-style-and-text-direction.md`).
- Before committing to a mechanic, confirm it exists in the installed game and tag the evidence `[game-tested <version>]`, `[vanilla-confirmed <version>]`, `[docs]` or `[unverified]` ("Feasibility check" in `exploration-depth-and-feasibility.md`).
- Every major spec needs achievements, an asset plan for everything visible, a real AI section, dynamic values instead of fixed ones, costs beyond political and command power, and effects strong enough to be felt (`achievements-and-asset-coverage.md`, `mechanics-costs-ai-and-effects.md`).
- Source specs go under `docs/specs/<feature_slug>/` and plans under `docs/plans/<feature_slug>/` (folder convention below). The spec files hold only the specification, prompts live in separate files, and the final output is one zip (`spec-output-and-packaging.md`).

Deep standards that already sit in their own files, to open directly: [focus-tree-path-design.md](references/focus-tree-path-design.md) (focus routes), [country-packages-and-formables.md](references/country-packages-and-formables.md), [forces-and-3d-planning.md](references/forces-and-3d-planning.md), [presentation-and-research-planning.md](references/presentation-and-research-planning.md) (interactive UI, animation, quote and audio research), [writing-style.md](references/writing-style.md), [specification-delivery.md](references/specification-delivery.md) (long specs, resume notes, improvement-loop expansions), [asset-and-research-handoffs.md](references/asset-and-research-handoffs.md).

Final step: before writing the final prompt files and before the final response of every planning pass, read [final-handoff-and-quality-gate.md](references/final-handoff-and-quality-gate.md) (final response checklist, cleanup and quality gate).

## Reference map

- [Exploration, depth and feasibility](references/exploration-depth-and-feasibility.md): Read while expanding a rough idea into a deep design, and before the spec commits to any mechanic. Covers: Depth standard; Research depth standard; What the specification should explore; Mod system awareness; Depth and hidden connections.
- [Spec style and text direction](references/spec-style-and-text-direction.md): Read before writing tone and presentation direction, option humour and irony direction, or any other player-facing text direction in a spec. Covers: Writing style.
- [Branching and escalation design](references/branching-and-escalation-design.md): Read before mapping decisions, rare variants, branches, baseline stages, escalation variants or escalation text. Covers: Full decision, rare variant, and branch mapping; Baseline stages and escalation variants; Escalation and uncertainty.
- [Mechanics, costs, AI and effects](references/mechanics-costs-ai-and-effects.md): Read before designing dynamic values, costs and sacrifices, AI behaviour or effect strength. Covers: Dynamic mechanics standard; Cost and sacrifice design standard; AI strategy and behavior mapping standard; Effect strength and impact standard.
- [Focus trees, countries and UI planning](references/focus-country-and-ui-planning.md): Read before planning focus trees, country packages and formables, starting forces and 3D units, custom UI and animation, quote and audio research, or the MCP implementation handoff. Covers: Focus tree path design standard; Focus tree visual planning standard; Country package and dynamic identity standard; Starting forces and reinforcement pathway standard; Custom UI and presentation; Interactive mechanic UI and animated presentation in feature specs; Quote, remark, and audio research planning.
- [Achievements and asset coverage](references/achievements-and-asset-coverage.md): Read before planning the achievements or the asset coverage of a spec. Covers: Achievement design standard; Mandatory asset coverage and source-mode standard; Asset planning.
- [Spec output and packaging](references/spec-output-and-packaging.md): Read before choosing the spec's shape, splitting it into files, writing the localisation handoff or packaging the output zip. Covers: Specification shape; Depth, file splitting, and internal resume notes; Improvement-loop expansion specs; General localisation handoff; Output rules; Final zip package requirement.

## 1. Required reading

Before writing the feature specification, use the following as the design baseline:

- `AGENTS.md`
- `hoi4-events` when the feature includes ordinary HOI4 events, news events, report events, event chains, or event-triggered content
- `hoi4-feature-assets` when the feature needs visual assets
- `hoi4-frame-animation` when the feature has animated sprites, animated UI, animated route emblems, animated portraits, warning pulses, hover loops, glow loops, float loops, particle loops, or frame-by-frame presentation needs
- `hoi4-text-audio-research` when the feature needs sourced quotes, cultural remarks, or audio research
- `hoi4-improvement-loop` before a near-completion review, and whenever the design may still be shallow, disconnected, bloated, or missing deeper playable consequences
- `hoi4-subagents` before spawning `hoi4_improvement_loop_planner` or any other project subagent
- `hoi4-focus-trees` or the current focus-tree skill when the feature needs focus trees
- `hoi4-decisions-missions` when the feature needs decisions, missions, timed objectives, influence actions, or decision-driven mechanics
- parent-provided planning rows, CSV exports, or external records when the repository includes them and the parent explicitly provides them
- provided existing feature docs
- provided mod mechanics docs

Use those sources to understand how the target repository works, then expand creatively from there.

Inspecting the repo is mandatory, but the specification should not read like a technical audit. Use repo findings to prevent mistakes and match patterns. Keep proof of inspection in the final response checklist, not in admin sections inside the spec.

## 2. Input

The user will provide either:

- a rough feature idea
- a partly developed concept
- an existing feature that needs deeper rework
- a detailed spec that needs cleanup before implementation

Before drafting, hold the upfront consultation from `CLAUDE.md` with the standard questions in `references/consultation-questions.md`. Its answers in `decisions.md` are fixed inputs.

Treat the user idea as the starting point. Do not assume it is final.

When the idea is rough, expand it into a deeper design.

When the idea is already detailed, preserve the core direction and improve structure, clarity, missing connections, and implementation readiness.

## 3. Design purpose

The goal is to create a feature that feels like a layered mod system, not a basic popup.

The feature should have atmosphere, player choice, consequences, escalation, lore, replay value, and enough visual support to feel finished.

The design should be ambitious. Do not get lazy, conservative, or minimal unless the feature is genuinely small. Depth matters more than speed. Take the time needed to research, compare patterns, think through consequences, and design the feature as if the coding agent will implement exactly what is written.

The finished spec should make the coding agent feel that the feature has already been designed in full.

## 3.1 Idea-first specification style

The spec should focus on the feature idea, not on obvious implementation plumbing.

Do not put sections such as:

- `Scope`
- `Source baseline`
- `Repository context`
- `External tracking row`
- `Existing implementation audit`
- `Generic trigger safeguards`

The spec should be player-facing design and implementation-relevant feature design.

Avoid obvious lines such as:

- the feature only runs if enabled
- the feature should not run after a campaign-ending branch
- disabled features should not run
- the coding agent should use valid syntax
- the system should respect existing global settings

Those are baseline system responsibilities. Include technical notes only when they prevent a likely mistake, explain non-obvious behavior, or define a unique rule for this feature. Otherwise, its just noise.

Do not create negative capability notes for absent feature surfaces. If a feature does not have a campaign-ending branch, do not mention campaign-ending branches. If another surface is absent, omit that surface instead of documenting its absence. Do not write sections, bullets, feature-detail notes, parent-provided external record summaries, implementation prompts, or player-facing text that say negative absence wording such as `no special branch`, `no manual variant`, or similar. Omit the surface completely unless it actually exists or the user explicitly asks for an explanation of why it is absent.

## Specification folder convention

From now on, source specifications should live in feature-specific subfolders under `docs/specs/`.

Use this shape:

```text
docs/specs/<feature_slug>/
```

Examples:

```text
docs/specs/<feature_slug>/<feature_slug>_spec.md
docs/specs/<feature_slug>/<feature_slug>_focus_trees.md
docs/specs/<feature_slug>/<feature_slug>_country_packages.md
```

Use `docs/plans/<feature_slug>/` for subagent plans, improvement addenda, audit follow-up notes, blocked reports, and implementation handoffs. Plans can become source design later, but the main agent should promote or merge them into `docs/specs/` when they are accepted as part of the final feature design.

## 19. Final prompt files

Read [`references/final-handoff-and-quality-gate.md`](references/final-handoff-and-quality-gate.md) before writing the final prompt files and before the final response of every planning pass. It contains the complete standard for this section and its subsections. It also holds `Formation and UI questions for planning passes`, `20. Final response checklist`, `21. Cleanup and quality gate`.

<!-- HOI4_MOD_SETUP_SUPER_EVENTS_START -->
## Super Events planning

When the installed `hoi4-super-events` workflow is selected, use it only for a campaign-scale first reveal, irreversible escalation, world-order change, rare ideological victory, catastrophic collapse, global defeat, or genuine ending. The plan must name the owning caller, the state established before presentation, one stable registration ID, duplicate-suppression and close-cleanup behavior, title and description direction, quote and response themes, image direction and source mode, audio decision, runtime touchpoints, permanent documentation, and one acceptance scenario.

Treat title, response, quote, cultural reference, image, and audio choices as research briefs rather than invented final assets. Audio is optional unless the user, accepted specification, or verified project convention explicitly makes it required. Route implementation through `hoi4-events`, visual work through `hoi4-feature-assets`, sourced wording and audio through `hoi4-text-audio-research`, and the complete presentation contract through `hoi4-super-events`.
<!-- HOI4_MOD_SETUP_SUPER_EVENTS_END -->
