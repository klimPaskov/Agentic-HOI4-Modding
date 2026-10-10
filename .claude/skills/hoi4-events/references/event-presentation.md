# Scripted GUI and animated event presentation

This reference belongs to the `hoi4-events` skill and holds complete sections moved out of `SKILL.md` to keep it within the single-read ceiling. Every rule here is as binding as the rules in `SKILL.md`.

## Scripted GUI and animated event presentation

Major event mechanics can use scripted GUI windows, decision-category interfaces, animated leader portraits, or custom buttons when they make the system easier to play. Treat that UI as part of the event contract, not as decoration added later. Static and animated category pictures must pass the simple-category eligibility gate in `hoi4-decisions-missions`: description, ordinary decision list, and at most basic formatted value tables, with no complex GUI, meters, extra custom controls, rich panels, or other animations alongside the picture.

When the event specifically adds a dedicated scripted GUI or mechanic window, route its bounded layout implementation and visual-quality pass to `hoi4_event_ui_worker`. The worker must follow `hoi4-scripted-gui` for the accepted reference, native-element mapping, mandatory `hoi4.gui_inspect`, iterative `hoi4.gui_render` state/resolution/hierarchy/click-region views, corrections, and matched post-change comparison evidence. Reviewed source edits may be applied directly or through optional `hoi4.gui_rewrite`. Do not send shared event logs, event-detail frameworks, settings, super-event frameworks, shared registries, or unrelated existing UIs to this worker. A UI is eligible only when the accepted event spec or source proves that the event introduces and owns it.

When an event uses a custom interface, align these surfaces:

- decision category or entry button
- scripted GUI definition
- scripted triggers and effects
- costs and tooltips
- animated and static sprites
- localisation and scripted localisation
- AI fallback behavior
- cleanup and invalidation rules
- documentation and asset manifest

For a formable state puzzle, add the manifest-to-category attachment crosswalk to the event handoff and verify every in-scope category against the generated scripted-GUI identifier and window. Use the actual read-only map and GUI inspect/render routes for the linked category; a state-piece render alone never proves category coverage.

Every player-clickable GUI button that changes gameplay must validate the same requirements as a normal decision. It must show costs and missing requirements clearly. It must call scripted effects that can also be used by AI, decisions, focuses, and cleanup systems.

Animated leader portraits, animated route emblems, glow effects, particles, and float effects should be used for major reveals, extreme-route escalation, hidden formables, supernatural leaders, or final transformations. Each animated asset needs a static fallback and manifest entry.
