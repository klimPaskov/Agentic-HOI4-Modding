# Shared canonical asset-reference library

This copy is retained as a legacy review mirror. The 2026-08-04 audit also
synchronized the new vanilla references requested for the agentic HOI4 Modding
repository, while active workflows continue to use the canonical Chaos Redux
reference root below.

The active canonical source is:

`C:\Users\klimp\OneDrive\Documents\Paradox Interactive\Hearts of Iron IV\mod\chaos_redux\.agents\skills\chaos-redux-event-assets\assets\vanilla_reference`

This mirror keeps the same relative family layout under
`.agents/skills/hoi4-feature-assets/assets/vanilla_reference/`. Reference PNGs
are review material only; never wire, ship, trace, recolour, or copy them into
final art.
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

The checksum- and frame-level provenance for the synchronized additions is in
`REFERENCE_MANIFEST.md`. Future updates should land in the canonical root first
and mirror here only when explicitly requested, with exact provenance, native
dimensions, and a labeled contact sheet.
