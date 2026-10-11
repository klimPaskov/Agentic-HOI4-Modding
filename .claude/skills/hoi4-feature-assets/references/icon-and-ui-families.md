# Decision category pictures and portrait icons

This reference belongs to the `hoi4-feature-assets` skill and holds complete sections moved out of `SKILL.md` to keep it within the single-read ceiling. Every rule here is as binding as the rules in `SKILL.md`.

## 18.1 Decision category pictures

A decision category picture is a larger visual surface used inside or beside a decision category. It is not a `32x32` decision icon, a small category icon, a custom-window background, or a substitute for an interactive scripted GUI.

Use a category picture when the normal decision list already carries the actions but the category benefits from identity, historical context, propaganda, territorial orientation, or a readable theme. Suitable subjects include propaganda and public campaigns; civil-war mobilization, insurgency, and preparedness; elections, ideology, monarchy, party control, and trade-union politics; faction management, treaties, naval agreements, and intervention; formable territory maps; and documentary or symbolic scenes.

Apply the [category-picture eligibility gate](../../hoi4-decisions-missions/SKILL.md#decision-category-presentation-hierarchy) before requesting static or animated art. Only simple categories with a description, ordinary decision list, and at most basic formatted value tables qualify. Existing complex UI, meters, extra custom controls, rich interactive panels, or other animations exclude an additional category picture. Ordinary decision buttons are allowed, and the picture itself may be animated. An interactive state puzzle cannot also receive a category picture.

Choose the source route by content:

- use `hoi4_asset_source_researcher` for real propaganda posters, photographs, archival maps, documents, and other verifiable historical material
- use `hoi4_generated_feature_art` for fictional or alternate-history posters, symbolic category pictures, generated documentary scenes, and non-icon illustrated panels
- use deterministic installed-map data and exact state geometry for formable territory pictures and state-puzzle pieces; never ask the image generator to invent state borders

Generated category pictures must not contain fake controls, meters, buttons, unreadable generated text, modern UI, or decoration that implies a click action. A static picture is the normal choice. Use an animated picture only when motion communicates a changing state or supports an active propaganda, mobilization, crisis, or transformation theme. Animated pictures follow `hoi4-frame-animation` and require real source frames, a static fallback, a sheet, preview, manifest, and sprite handoff.

Before production, inspect `assets/vanilla_reference/icons/decision_categories/pictures/contact_sheet.png` and the exact active consumer. The manifest and handoff must classify the output as a small category icon, static category picture, animated category picture, compact scripted GUI display, or full mechanic-window asset.

## 21.1 Advisor and high-command portrait icons

Advisor, theorist, military-high-command, officer-corps, and army-small dossier
portraits are a distinct native `65x67` asset family. Inspect
`assets/vanilla_reference/portraits/advisors/` and its contact sheet before
production. Do not satisfy an advisor requirement by shrinking a `156x210`
leader texture or by reusing an unrelated icon.

Apply the same identity gate. A grounded real subject first needs an
independently approved full portrait candidate and retained attribution. An
allowed fictional subject needs its own full-resolution generated master; do
not reuse a leader crop. Institutional or collective briefs must state whether
the card is people-free or depicts a governing group.

Use the bundled compositor:

```powershell
python -B .claude/skills/hoi4-feature-assets/tools/create_advisor_icon.py `
  --source <approved_portrait> `
  --portrait-size <width> <height> `
  --rotation <degrees> `
  --portrait-offset <right> <down> `
  --preview <review.png> `
  --output <runtime.dds>
```

The tool loads the complete approved source without a pre-crop or warp, measures the template opening, and uses one uniform aspect-preserving cover scale. It expands the opening with the centralized under-frame bleed and portrait-edge guard, masks the covering portrait to that safe region, and composites the exact `advisor_template.png` once as the untouched top layer. Never clip to the exact visible opening: translucent antialiased inner-edge pixels need portrait coverage beneath the frame. Do not anisotropically stretch, redraw, recolour, or replace the frame, paper, seal, bevel, patina, or shadows.

Require a per-person placement study, native preview, nearest-neighbour `4x` review preview, alignment overlay, metadata, and staged DDS. Record source/template hashes, measured opening center/size/angle, uniform cover geometry, bleed/guard constants, transformed dimensions, center, offset, rotation, alpha coverage (`opening_alpha_gap_pixels`, `inner_edge_alpha_gap_pixels`, `exterior_alpha_leak_pixels`), preview and DDS hashes, runtime path, and independent reviewer. Review against solid and checker backgrounds at native and `4x` size. Automated dimension and alpha checks are evidence, not visual approval. Reject gaps, matte pixels, exterior leakage, padded strips, visible stretching, or a neutral transform that recreates a frame-only card.

When a character defines `army.large` and `army.small`, keep the approved
`156x210` commander texture for `large` and create a separate native `65x67`
dossier portrait for `small`. Validate and document both sprites independently.
