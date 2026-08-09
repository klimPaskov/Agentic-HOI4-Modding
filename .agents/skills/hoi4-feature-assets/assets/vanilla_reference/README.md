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
- decision-category pictures: `icons/decision_categories/pictures/`, a larger presentation family separate from small category icons
- unit visual pipelines: the separate equipment, land, air, naval, and
  `units/models_3d/` families

These families are not interchangeable. Preserve the cataloged native canvas,
transparency, frame order, and owning definition.

## Decision category picture references

The canonical larger-picture family lives at `icons/decision_categories/pictures/`. Its owning surface is a decision category's `picture` field, normally consumed through a `GFX_decision_cat_*` sprite in vanilla `interface/decisions.gfx`; it is not a small category icon, decision icon, scripted-GUI background, or full mechanic-window asset.

The shelf contains 13 user-provided vanilla reference PNGs. Each is a lossless `114x101` RGBA review copy whose decoded pixels match the corresponding installed DDS after BGRA-to-RGBA decoding. `CATALOG.md` records the installed source, sprite and category consumer, native dimensions, contact sheet, and PNG SHA-256. Source identity is accepted only where the installed DDS, `.gfx` sprite, and category consumer agree.

The PNGs and `contact_sheet.png` are review-only. Do not wire, recolour, trace, ship, or copy them into runtime GFX, and do not infer a redistribution licence from their presence. The contact sheet labels every filename and native dimension.

## Maintenance

The checksum- and frame-level provenance for the references is in `REFERENCE_MANIFEST.md`.

Future updates should land in this skill-local root with exact provenance, native dimensions, and a labeled contact sheet.
