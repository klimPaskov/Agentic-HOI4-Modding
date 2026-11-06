# HOI4 Subagents: Spawn gates

Part of the [hoi4-subagents](../SKILL.md) skill. Read before spawning `hoi4_event_ui_worker` or `hoi4_repo_explorer`. This file holds the "Event UI worker gate" and the "Repo explorer use gate" sections.

## Event UI worker gate

Spawn `hoi4_event_ui_worker` without inherited conversation context only when the accepted event spec or implementation explicitly introduces a dedicated scripted GUI or mechanic window. The parent prompt must provide the event id or stable feature slug, exact GUI identifiers and owning files, entry point, accepted layout brief, intended states and resolutions, linked decisions and scripted-GUI identifiers, approved asset handoffs, allowed files, and handoff path.

The worker is patch-capable for the accepted event-owned `.gui`, presentation-only `common/scripted_guis` wiring, event-owned `.gfx`, and event-owned GUI localisation. It owns layout implementation, visual hierarchy, spacing, alignment, background coverage, state presentation, click-region accuracy, and MCP before-and-after evidence. The parent and decision worker retain event outcomes, decision costs, AI, balance, reusable helper logic, final integration, and in-game validation.

Do not route a GUI to this worker merely because an event references or opens it. Event logs, event-detail frameworks, settings, super-event frameworks, shared registries, generic utility windows, debug windows, and unrelated existing UIs remain out of scope. The prompt must identify the exact source or accepted specification proving that the named event owns the UI.

Mandatory event-UI evidence includes `hoi4.gui_inspect`, pre-change `hoi4.gui_render` full-window and relevant cropped, annotated, state, resolution, hierarchy, click-region, and comparison views, intermediate live previews after every meaningful layout tranche, corrected-defect rerenders, and final inspect/render comparison over matching states, values, resolutions, UI scales, language, and assets. The worker may apply reviewed edits directly or use optional `hoi4.gui_rewrite`; a rewrite transaction is not itself a completion gate. If a required inspection or render route is unavailable, the worker records the exact blocker and does not substitute source-only review.

## Repo explorer use gate

`hoi4_repo_explorer` is an optional scout for uncertain or broad work. It should save time by finding files, patterns, precedents, and edit order before the parent starts a complex implementation.

Use `hoi4_repo_explorer` when at least one of these is true:

- the parent does not know the likely touched files
- the task spans several systems and the edit order is uncertain
- the correct repository pattern or vanilla precedent is unclear
- a named spec, prompt, source file, classification, sprite, tag, localisation key, or helper appears missing and needs recovery evidence
- the feature has enough cross-surface risk that a file map and meaningful validation plan will prevent missed work

Do not spawn `hoi4_repo_explorer` for small or already bounded work, including:

- known-file edits
- user-provided file updates
- direct skill, prompt, or agent-definition updates
- small bug fixes where the relevant files are already named
- localisation-only cleanup with known keys
- asset-only production that belongs to an asset subagent
- tabular-data-only updates that belong to `hoi4_spreadsheet_doc_worker`
- simple report, docs, or markdown edits where the parent can inspect the provided files directly

When the task is small, the parent should read the known files directly and proceed. Do not use repo exploration as a ritual step or as a replacement for parent review.

