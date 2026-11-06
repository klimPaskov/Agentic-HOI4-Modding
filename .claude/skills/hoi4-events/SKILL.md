---
name: hoi4-events
description: Use when implementing, updating, auditing or documenting HOI4 events and event chains, including country, news and report events, on_actions, event text, localisation, pictures, hooks and validation.
---

# HOI4 Events

Use this skill for ordinary HOI4 event work in a mod repository.

This includes:

- adding or updating country events, hidden events, news events, report-style events, and narrative event chains
- wiring events through `on_actions`, decisions, focuses, scripted effects, scripted triggers, scripted localisation, and optional mod-specific registration hooks
- keeping localisation, event pictures, report pictures, news pictures, text and audio packages, docs, and any parent-provided tracking records aligned
- validating event ids, namespaces, scopes, triggers, effects, options, localisation keys, pictures, and follow-up hooks

Repository-wide reading and style rules live in `AGENTS.md`. This skill adds the event-specific implementation contract. It does not replace focus-tree, decision, asset, animation, text and audio research, or subagent skills.

When event work creates broad visible text, use `hoi4_localisation_auditor` before completion when that subagent is available. When repeated dynamic logic appears across events, decisions, focuses, GUI, or country setup, use `hoi4_scripted_system_architect` before duplicating logic.

Read this file first, then open the reference for the phase you are in. Every reference holds complete rules moved verbatim out of this file, and each rule there is as binding as a rule here.

Workflow:

1. Before the first source write, run the MCP event-chain pass below (baseline `hoi4.event_inspect`).
2. Classify the event and map the systems it touches: [event-anatomy-and-classification.md](references/event-anatomy-and-classification.md), then [touched-systems-and-country-packages.md](references/touched-systems-and-country-packages.md).
3. Implement, opening the matching reference for scopes, options and AI, text, spec fidelity, formables, 3D models and assets.
4. Before reporting completion, read [completion-checklist.md](references/completion-checklist.md) and run the quick check under Validation checks.

Rules that always apply (short form, the full text is in the named reference):

- Keep existing event ids and namespaces stable and never renumber them for tidiness ([event-anatomy-and-classification.md](references/event-anatomy-and-classification.md)).
- Player-facing and doc text is finished in-world prose: no em dashes or semicolons, no dialectical hedging or thesis-antithesis-synthesis, no staccato lines, no empty filler, no process notes, no hidden routes or spoilers ([event-text-and-localisation.md](references/event-text-and-localisation.md)).
- Every player-facing string is localised, including options, tooltips, news and report text and dynamic values. Text drawn on light parchment uses plain text with no `§` colours (same file).
- Spec-mapped content is acceptance criteria. Do not silently shrink it, default to political-power-only costs, or leave tiny decorative effects ([spec-fidelity.md](references/spec-fidelity.md)).
- Entering another country scope does not rebind ROOT. Save scopes you need later as event targets and clean them up ([scopes-and-helper-outputs.md](references/scopes-and-helper-outputs.md), [country-activation.md](references/country-activation.md)).
- Every chain cleans up its flags, variables, event targets, missions, decisions and temporary ideas ([options-ai-hooks-and-cleanup.md](references/options-ai-hooks-and-cleanup.md)).
- Never hide placeholders, missing assets, missing localisation or missing AI in a completion report.

Existing references, still current:

- [country-activation.md](references/country-activation.md): read before implementing country activation, deferred setup, player transfer, coalesced refreshes or callback-to-helper scope chains.
- [variables-and-math.md](references/variables-and-math.md): read before writing script variables, arrays, loops or math.
- [meta-effects.md](references/meta-effects.md): read before using `meta_effect` or `meta_trigger` to feed variables into static-token effects.
- [event-presentation.md](references/event-presentation.md) and [major-event-aftermath.md](references/major-event-aftermath.md): see the two pointer sections below.

## Reference map

- [Event anatomy and classification](references/event-anatomy-and-classification.md): Read before editing an event chain, to classify each event block and keep ids, event types and stages consistent. Covers: Working model; Event anatomy; Event implementation workflow.
- [Touched systems and country packages](references/touched-systems-and-country-packages.md): Read before mapping which files and systems an event touches, and when an event creates a country, a special project override or a unit family.
- [Scopes and helper outputs](references/scopes-and-helper-outputs.md): Read before writing effects that change scope or call scripted helpers that return values.
- [Options, AI, hooks and cleanup](references/options-ai-hooks-and-cleanup.md): Read before writing immediate and option effects, AI chance, news or report events, on_action hooks, the text and audio handoff, or chain cleanup.
- [MCP evidence and subagent ownership](references/mcp-evidence-and-subagents.md): Read before treating an MCP inspection, render or probability result as evidence, and before delegating event work to subagents. Covers: Parent and subagent implementation ownership.
- [Spec fidelity](references/spec-fidelity.md): Read before implementing an event feature from docs/specs, and before deciding to merge, skip or simplify a mapped item. Covers: Spec and plan locations; Spec fidelity and implementation quality.
- [Event text and localisation](references/event-text-and-localisation.md): Read before writing or editing any player-facing event text, documentation prose or localisation. Covers: Event writing and player-facing text; Localisation and scripted localisation.
- [Formables, 3D models and generated assets](references/formables-3d-and-assets.md): Read before an event creates formable routes, a 3D unit or building, or generated visual assets. Covers: Formable nations as event surfaces; 3D model and entity integration; Generated asset handling.
- [Documentation and completion checklist](references/completion-checklist.md): Read before reporting completion, and before writing or updating event documentation. Covers: Documentation rules; Final event checklist.

## Relationship with other skills

Use this skill with:

- `hoi4-feature-planning` when the user asks for event design or a deeper event specification before implementation
- `hoi4-feature-assets` when the event needs event pictures, report images, news images, icons, flags, portraits, or final DDS assets
- `hoi4-3d-model-pipeline` when the event creates or changes a visible 3D unit, building, creature, vehicle, aircraft, naval object, or map entity
- `hoi4-frame-animation` when event presentation needs animated sprites, animated portraits, animated UI pieces, frame sheets, or GIF previews for review
- `hoi4-text-audio-research` when an event needs sourced quotes, cultural references, title-like references, slogans, or music and audio research
- `hoi4-focus-trees` when the event creates, unlocks, modifies, or depends on focus trees
- `hoi4-decisions-missions` when the event creates or depends on decisions, missions, timed objectives, formables, or decision-driven mechanics
- `hoi4-scripted-gui` when the event owns or opens a scripted GUI; that skill owns reference-image mapping, layout, iterative MCP previews, and visual acceptance while this event skill retains gameplay and lifecycle ownership
- `hoi4-subagents` when bounded research, asset production, event-owned UI layout work, small patches, or completion audits should be delegated
- `hoi4_3d_model_pipeline` for bounded model geometry, textures, rigs, skeletal actions, sourced custom-unit audio research and synchronization design, `.mesh`/`.anim` exports, reimport proof, and runtime handoff when the event owns a 3D unit or building surface
- `hoi4-improvement-loop` when an implemented event works but is still shallow, generic, disconnected, or underdeveloped
- the installed `hoi4-agent-tools` MCP route for mandatory event-chain inspection, rendering, comparison, and lint-mode diagnostics without replacing the source-editing workflow

The parent agent remains responsible for final integration, final validation, and completion claims. Subagents and helper skills provide evidence, patches, assets, or plans. They do not replace parent review.

## MCP event-chain pass

For every event-chain surface supported by the installed MCP server, use the event tools as mandatory evidence before and after source edits. If the required route is unavailable, record the exact blocker and do not treat source-only review as equivalent engine evidence.

1. Before any parent or subagent source write, call `hoi4.event_inspect` in `scan` or `roots` mode and record the returned revision as the comparison baseline.
2. Use a narrow selector with `trace`, `explain_path`, `state_flow`, or `impact`.
3. Read linked JSON only when the compact result lacks necessary evidence.
4. Edit the event and connected mod files through the normal source workflow.
5. Run `hoi4.event_inspect` with `mode: "compare"` with the baseline revision as `before`, then run `hoi4.event_inspect` in `lint` mode and the most relevant `hoi4.event_render` view.

The event tools are read-only. Comparison refreshes edited source by default. Use bounded depth and node limits so MCP remains one small part of the larger skills, subagent, and repository workflow.

## Major-event defeat aftermath

Read [`references/major-event-aftermath.md`](references/major-event-aftermath.md) whenever a major event can be defeated, contained, or end with an aftermath state. It contains the complete standard for this section and its subsections.

## Scripted GUI and animated event presentation

Read [`references/event-presentation.md`](references/event-presentation.md) whenever an event adds a scripted GUI, an animated presentation, or a custom popup. It contains the complete standard for this section and its subsections.

## Validation checks

Before review, run `python -B .tools/check.py quick` on the changed files and fix every error it lists; it covers localisation and GFX wiring, the script syntax rules and MCP script validation, and proves only those properties (`AGENTS.md` section 4a).

Use task-specific validation that can realistically catch mistakes.

Common useful checks:

- duplicate event ids inside a namespace
- duplicate namespaces
- event file contains `namespace = ...`
- referenced events exist
- `country_event`, `news_event`, or `state_event` type matches the intended use
- option names and localisation keys exist
- event picture sprites exist and point to real files
- `fire_only_once`, `is_triggered_only`, and `hidden = yes` match the trigger path
- on_action hook calls the expected event or effect
- scripted effects and triggers referenced by the event exist
- global event targets created by the event are cleaned up
- decision or focus unlocks referenced by the event exist
- news/report images have final DDS files and `.gfx` definitions
- dynamic localisation selectors return fallback-safe text for every visible route
- AI chance exists for meaningful choices
- docs and manifests match final ids and assets

Do not fill the final report with boilerplate checks that only restate repo-wide rules. Report validation when it affected confidence, found a problem, or directly proves a task-specific surface is wired.

<!-- HOI4_MOD_SETUP_SUPER_EVENTS_START -->
## Super Events integration

When the installed `hoi4-super-events` workflow is selected, treat the owning gameplay transition and its presentation registration as one feature. Read `hoi4-super-events`, establish the announced state before showing the presentation, reserve one stable unused registration ID, add every required title, description, quote, response, image, and optional audio branch, call the project-scoped show effect from one reachable owner, suppress duplicate callers, and clear visibility, registration, and playback state through the installed close path.

Validate the live caller, state ordering, registration uniqueness, sprite and texture resolution, localisation coverage, duplicate suppression, cleanup, permanent documentation, and one named in-game scenario. Never invent helpers, commands, sound conventions, or project-specific paths. Optional audio must not break the visual package; audio marked required by the accepted project plan remains a completion blocker until its source, rights, sound ID, definition, playback, and documentation agree.
<!-- HOI4_MOD_SETUP_SUPER_EVENTS_END -->
