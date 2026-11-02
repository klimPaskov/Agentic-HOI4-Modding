# Shared canonical asset-reference library

This skill-local library holds the vanilla references of the asset workflow: 40 `hoi4-imagegen` families, built from HOI4 1.19.4.1. `hoi4-imagegen` takes its style references from the mod's own art first and from this shelf second, and the same folders serve as review material for hand-made art.

Keep the same relative family layout under `.claude/skills/hoi4-feature-assets/assets/vanilla_reference/`.

Reference PNGs are review and style material only; never wire, ship, trace, recolour, or copy them into final art.
Use `README.md` and `CATALOG.md` at the root, then inspect the matching
contact sheet and owning `.gfx`, `.gui`, `.asset`, or `.mesh` definition. `REFERENCE_MANIFEST.md` lists every file with its source texture and SHA-256 values.

## Reference families

`CATALOG.md` has the table of every family with its folder, canvas, frame count and file count. The folders by group:

- portraits: `portraits/leaders/`, `portraits/commanders/`, `portraits/operatives/`, `portraits/scientists/` and the advisor cards in `portraits/advisors/`
- flags: `flags/normal/`, `flags/medium/`, and `flags/small/`, one set of tags at the three sizes
- event art: `event_art/report/`, `event_art/news/` and `event_art/operation/`
- gameplay icons: the separate families under `icons/` (focus, ideas, decisions, modifiers, MIO, traits, medals and more)
- decision-category pictures: `icons/decision_categories/pictures/`, a larger presentation family separate from the small category icons in `icons/decision_categories/`
- unit art: `units/land/counters_large/`, `units/land/map_counters/`, `units/air/map_counters/`, `units/naval/map_counters/` and `units/land/division_template_emblems/`
- 3D and equipment pipeline inputs: `units/equipment/technology_art/` and `units/models_3d/`
- GUI windows: `interface/vanilla/`, the review shelf for `hoi4-scripted-gui` and window art

The `super_event` family has no shelf folder, because Super Events are a mod pattern with no vanilla texture, and `gui_texture` follows `interface/vanilla/`. Missions use the decision icons.

These families are not interchangeable. Preserve the cataloged native canvas,
transparency, frame order, and owning definition. A mod's own sizes live in its `.tools/gfx/profiles.json`, which starts from the vanilla sizes recorded here.

## Tool inputs that are not references

Three groups of files are inputs of the kit's tools. The shelf rebuild never replaces them and `CATALOG.md` lists them:

- `icons/achievements/template/`: the completed and grey 64x64 achievement backgrounds and the unchanged red not-eligible overlay. Use them only through `tools/process_achievement_icons.py` (or `hoi4-imagegen`, which runs it). Preserve their filenames, dimensions, alignment and SHA-256 values.
- `portraits/advisors/advisor_template.png`: the advisor card template that `tools/create_advisor_icon.py` and `hoi4-imagegen` composite onto an approved portrait.
- `units/equipment/technology_art/`, `units/models_3d/` and `interface/vanilla/`: review folders for the 3D, unit and GUI workflows.

## Decision category pictures

The larger-picture family lives at `icons/decision_categories/pictures/`. Its owning surface is a decision category's `picture` field, normally consumed through a `GFX_decision_cat_*` sprite in vanilla `interface/decisions.gfx`. It is not a small category icon, decision icon, scripted-GUI background, or full mechanic-window asset. Each PNG is a lossless `114x101` RGBA decode of the installed DDS.

## Maintenance

`.tools/gfx/shelf/build_shelf.py` rebuilds the shelf from an installed game, and `CATALOG.md` has the command. Do not edit a reference by hand: `python .tools/audits/audit_shelf.py` (the `shelf` check of `.tools/check.py`) fails when a PNG, a family folder or a document drifts from `.tools/gfx/shelf/catalog.json`. After a game update, rebuild, copy the result in, then run `python .tools/audits/audit_shelf.py --write-docs`.
