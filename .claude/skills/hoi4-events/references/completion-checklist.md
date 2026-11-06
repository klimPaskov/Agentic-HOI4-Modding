# HOI4 Events: Documentation and completion checklist

Part of the [hoi4-events](../SKILL.md) skill. Read before reporting completion, and before writing or updating event documentation.

## Documentation rules

Event-specific documentation belongs in `docs/events/`.

Preferred naming pattern:

- `docs/events/<feature_slug>.md`, using the same feature slug as the related spec, plan, and asset folders.

Keep one canonical doc per event chain instead of splitting mechanics across multiple top-level docs unless the user explicitly asks for that.

Event doc structure:

1. What the event is.
2. Event map and subevents.
3. Trigger and runtime flow.
4. Main gameplay effects.
5. Supporting systems touched.
6. AI behavior if relevant.
7. Baseline progression, escalation variant tracks, and escalation flow if relevant.
8. Campaign-ending and source-researched text or audio integration if relevant.
9. Connections with other events if relevant.
10. Asset wiring and sprite expectations if relevant.
11. Limitations if any.
12. Open tuning notes and future expansion ideas.

### Docs and gameplay must stay aligned

When mechanics change, update the matching event doc in the same change.

Do not leave the doc describing:

- old triggers
- old cooldowns
- old stage counts
- removed branches
- removed assets
- outdated external record or deck expectations

### Retiring unused helpers

- Before deleting a scripted effect, trigger, or `defined_text`, search every placeholder constructor (`[ID]`-style `meta_effect` or `meta_trigger` text, `@` token pasting, and dynamically suffixed effect names) and the GUI, `.gfx`, localisation, and docs for the name; a zero literal token count alone does not prove the code is dead.
- Delete the comment header attached directly above the removed block, or it will describe the next definition.
- After each removal pass, rescan for helpers, localisation keys, and script-constant keys whose only consumer was the removed code, and repeat until nothing new appears.
- Repository files can mix CRLF and LF line endings; edit them line by line with their own endings instead of splitting on one newline style.


## Final event checklist

After editing report or news text, audit every colour-bearing key drawn on a light parchment consumer, including scripted localisation output, and resolve each hit; use the repository's report-colour audit tool when one exists.

Before closing an event task, verify the surfaces that actually exist for the feature:

1. Event script files are updated, ids are stable, and namespaces are unique.
2. Firing path is correct: decision, focus, on_action, hidden event, scripted effect, or optional mod registry.
3. Triggers, scopes, immediate effects, option effects, and cleanup effects match the design.
4. Shared effects, triggers, script constants, and event targets are updated when needed.
5. Localisation exists for titles, descriptions, options, tooltips, news/report text, and dynamic values.
6. News events, report events, and researched text or audio packages are wired only when they are real surfaces in the design.
7. Supporting decisions, missions, ideas, focuses, AI, country setup, or scripted GUI surfaces are aligned when relevant. Every event-owned scripted GUI has a reviewed `hoi4_event_ui_worker` handoff with intermediate MCP preview evidence, corrected defects, and matched before-and-after layout evidence under `hoi4-scripted-gui`; shared UIs remain outside that worker's scope.
8. Event pictures, report images, news images, icons, flags, portraits, animated sprites, and fallbacks exist when required.
9. Generated or sourced assets are resized, converted, moved into correct folders, wired in `.gfx`, and recorded in manifests when they are part of the task.
10. Documentation, specs, plans, manifests, and any explicitly scoped external records are updated only when the repository actually uses those surfaces.
11. Spec-mapped mechanics, routes, countries, decisions, achievements, assets, and researched text or audio packages are implemented or clearly reported as blocked, merged, renamed, skipped, or simplified.
12. Dynamic values, concrete costs, mechanic visibility, decision filtering, cleanup, AI behavior, and effect strength are checked where the spec calls for them.
13. Focus trees preserve route structure, focus filters, varied rewards, idea lifecycles, route-specific AI, and visible branch payoffs where relevant.
14. New fighting countries have dynamic starting forces, template assumptions, equipment and manpower handling, and reinforcement pathways.
15. When the repository has a shared unit-family provider API, every in-scope family has an explicit standalone-provider, support-attachment, or parent-owned disposition, idempotent owner registration or documented engine constraint, and concrete token and presentation coverage.
16. No fallback, placeholder, missing localisation, missing asset, missing AI behavior, or shallow substitute is hidden in the completion report.


