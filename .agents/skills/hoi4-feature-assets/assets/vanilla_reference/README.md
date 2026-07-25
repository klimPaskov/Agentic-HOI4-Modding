# Shared canonical asset-reference library

This copy is retained only as legacy reference data. It is not an active asset
source for this mod, and no workflow may use its path.

All active asset skills and agents use this single canonical reference root:

`C:\Users\klimp\OneDrive\Documents\Paradox Interactive\Hearts of Iron IV\mod\chaos_redux\.agents\skills\chaos-redux-event-assets\assets\vanilla_reference`

All paths below are relative to that canonical root. Reference PNGs are review
material only; never wire, ship, trace, recolour, or copy them into final art.
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

Do not rebuild or extend this legacy copy. Add or update references only in the
canonical root above, with exact provenance, native dimensions, and a labeled
contact sheet.
