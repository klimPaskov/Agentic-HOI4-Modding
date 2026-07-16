# Canonical asset-reference library

This directory is the canonical, skill-local review library for
`hoi4-feature-assets`. It is organized by the owning visual surface so an
agent can compare the right canvas, transparency treatment, frame layout, or
event-art presentation before creating original mod art.

Reference PNGs are never runtime mod assets. Do not wire, ship, trace, recolor,
or copy the depicted people and symbols into final art. For implementation,
inspect the cataloged source and its `.gfx`, `.gui`, `.asset`, or `.mesh`
precedent, then create original or properly sourced mod assets.

## Provenance and coverage

- Vanilla source root: `C:/Program Files (x86)/Steam/steamapps/common/Hearts of Iron IV/`
- Review format: lossless RGBA PNG decoded from source DDS, TGA, or PNG
- Pixel policy: preserve the source texture canvas exactly; do not crop,
  stretch, repaint, or normalize transparent bounds during extraction
- Inventory and dimensions: see [CATALOG.md](CATALOG.md)

The catalog records the exact source path, native dimensions, related
definition, and local contact sheet for every reference. All entries in this
generic library are vanilla HOI4 references.

Common icon families—national focus, ideas, decisions, decision categories,
technologies, and achievement states—target at least 15 references. Other
tracked families target at least 5. Counts exclude contact sheets.

## Contact sheets

Every semantic folder owns one labeled `contact_sheet.png` beside its reference
PNGs. There is deliberately no broad `contact_sheets/` directory. Sheets use a
checkerboard review background, show filenames and native dimensions, and
preserve each source family's aspect ratio. The checkerboard is not part of
any extracted image.

## Reference families

Portraits and dossier cards:

- `portraits/leaders/`
- `portraits/commanders/`
- `portraits/operatives/`
- `portraits/advisors/`

Flags and event art:

- `flags/normal/`, `flags/medium/`, and `flags/small/`
- `event_art/report/`, `event_art/news/`, and `event_art/super_event/`

Gameplay icons:

- `icons/national_focus/`, `icons/ideas/`, `icons/technologies/`
- `icons/decisions/`, `icons/missions/`, and `icons/decision_categories/`
- `icons/achievements/`, `icons/officer_corps_spirits/`, and
  `icons/special_projects/`
- `icons/balance_of_power/`, `icons/intelligence_agency/`, and
  `icons/intelligence_operations/`
- `icons/commander_traits/`, `icons/medals/`, and `icons/military_raids/`
- `icons/state_modifiers/`, `icons/military_industrial_organizations/`,
  `icons/factions/`, `icons/buildings/`, and `icons/modifiers/`

Unit visual pipelines:

- `units/equipment/technology_art/`
- `units/land/counters_large/`, `units/land/map_counters/`, and
  `units/land/division_template_emblems/`
- `units/air/map_counters/` and `units/naval/map_counters/`
- `units/models_3d/land_materials/`, `air_materials/`, and `naval_materials/`

These families are not interchangeable. Follow the cataloged native canvas,
transparency, frame order, and owning definition. Model materials are UV
references paired with mesh/entity definitions; they are not 2D icons, renders,
or concept sheets.

## Maintenance

When the installed game build changes, rebuild the reference library from
vanilla and regenerate each semantic contact sheet and `CATALOG.md`. Do not
recreate the old shared contact-sheet directory or add reference images beside
this tree.
