# Reference asset examples

This reference belongs to the `hoi4-feature-assets` skill and holds complete sections moved out of `SKILL.md` to keep it within the single-read ceiling. Every rule here is as binding as the rules in `SKILL.md`.

## 4. Reference asset examples

This skill uses the shared canonical vanilla HOI4 visual-reference library. Read
the library rules and catalog before generating, sourcing, processing, or wiring
an asset.

Start with:

- `README.md`
- `CATALOG.md`

Every semantic reference directory contains a labeled `contact_sheet.png`.
There is no shared `contact_sheets/` directory.
Contact sheets are review aids, not final assets. Common icon families target 15 references; other tracked families target at least 5.

Canonical portrait paths:

- country leaders: `portraits/leaders/`
- army and navy commanders: `portraits/commanders/`
- operatives: `portraits/operatives/`

Canonical flag and event-art paths:

- flat flags: `flags/normal/`, `flags/medium/`, and `flags/small/`
- report-event art: `event_art/report/`
- news-event art: `event_art/news/`
- large presentation art: use the closest report, news, or custom feature reference set for the owning UI surface

For interface composition, use the [vanilla interface review shelf](../assets/vanilla_reference/interface/README.md) and its actual `interface/vanilla/` families, then inspect paired installed-vanilla `.gui` and `common/scripted_guis` sources under `hoi4-scripted-gui`. Structural precedents and inherited reference renders do not replace the new window's accepted compositional reference or current MCP evidence. Do not redirect callers to missing migration folders.

Canonical gameplay-icon paths:

- national focus: `icons/national_focus/`
- ideas and national spirits: `icons/ideas/`
- decisions: `icons/decisions/`
- missions: `icons/missions/`
- decision category icons: `icons/decision_categories/`
- decision category pictures: `icons/decision_categories/pictures/`
- achievement state triplets: `icons/achievements/`
- officer corps spirits: `icons/officer_corps_spirits/`
- technologies: `icons/technologies/`
- special projects: `icons/special_projects/`
- balance of power: `icons/balance_of_power/`
- intelligence agencies and operations: `icons/intelligence_agency/` and `icons/intelligence_operations/`
- commander traits, medals, and military raids: their separate folders under `icons/`
- state modifiers, military industrial organizations, factions, buildings, and modifiers: their separate folders under `icons/`

The decision category picture family contains the larger visual pictures used to establish a category's theme or territorial context. It is separate from the small category icon family. The current references use a native `114x101` canvas, but that is a reference-family canvas rather than a universal runtime prescription; inspect the active sprite and GUI consumer before selecting a target.

The picture folder must contain its own labeled `contact_sheet.png`. If it is missing, create it before category-picture work and update the reference `README.md` and `CATALOG.md` with filenames, native dimensions, provenance, and surface ownership. Reference images and the contact sheet are review-only; never wire, recolour, trace, copy, or ship them as runtime art.

Canonical unit-visual paths:

- equipment and technology art: `units/equipment/technology_art/`
- large land-unit counters: `units/land/counters_large/`
- land map counters: `units/land/map_counters/`
- division-template emblems: `units/land/division_template_emblems/`
- air map counters: `units/air/map_counters/`
- naval map counters: `units/naval/map_counters/`
- land, air, and naval model materials: their separate folders under `units/models_3d/`

These families are not interchangeable. Follow the cataloged native canvas, transparency, frame order, and owning `.gfx`, `.gui`, `.asset`, or `.mesh` definition. Reference PNGs are never final assets: do not copy, wire, recolor, or trace them.

The reusable achievement creation inputs live under `icons/achievements/template/`: `achievement_template.png` is the completed background, `achievement_template_grey.png` is the grey and not-eligible background, and `overlay.png` is the unchanged red-cross overlay. They are workflow inputs rather than reference examples, so exclude them from the achievement contact sheet and coverage count and preserve them byte-for-byte at native alignment.

When validating inherited GUI or GFX references, check both the mod and installed vanilla roots before declaring a DDS or other resource missing. A missing literal `effectFile` `.lua` path alone does not prove a missing asset. Inspect matching installed-vanilla `.gfx` declarations and the associated shader resource before reporting a missing source. Record the exact declaration, resource path, and lookup evidence without assuming a generic `.lua` to `.shader` mapping. Source linkage evidence does not prove rendered behavior or live-game correctness.

If no category matches, inspect the closest canonical category plus direct
vanilla or established repository precedents before choosing a style.
