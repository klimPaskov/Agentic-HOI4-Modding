# Shared canonical asset-reference library

This skill-local library contains the vanilla references used by the generic HOI4 asset workflow.

Keep the same relative family layout under `.agents/skills/hoi4-feature-assets/assets/vanilla_reference/`.

Reference PNGs are review material only; never wire, ship, trace, recolour, or copy them into final art.
Use `README.md` and `CATALOG.md` at the root, then inspect the matching
contact sheet and owning `.gfx`, `.gui`, `.asset`, or `.mesh` definition.

## Reference families

- portraits: `portraits/leaders/`, `portraits/commanders/`, and
  `portraits/operatives/`
- flags: `flags/normal/`, `flags/medium/`, and `flags/small/`
- event art: `event_art/report/`, `event_art/news/`, and
  `event_art/super_event/`
- gameplay icons: the separate families under `icons/`
- unit visual pipelines: the separate equipment, land, air, naval, and
  `units/models_3d/` families

These families are not interchangeable. Preserve the cataloged native canvas,
transparency, frame order, and owning definition.

## Maintenance

The checksum- and frame-level provenance for the references is in `REFERENCE_MANIFEST.md`.

Future updates should land in this skill-local root with exact provenance, native dimensions, and a labeled contact sheet.
