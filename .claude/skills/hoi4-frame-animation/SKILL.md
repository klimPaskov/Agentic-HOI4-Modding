---
name: hoi4-frame-animation
description: Use when a HOI4 mod needs animated sprites, icons, portraits, GUI pieces, pulses or frame sheets; the final asset is a frame-sheet texture built from real per-frame art, never a GIF.
---

# hoi4-frame-animation

This skill produces HOI4 animation packages: animated decision seals, scripted GUI pieces, route emblems, icons and leader portraits. The final in-game animation is a frame-sheet texture (usually one horizontal row) wired through a verified `.gfx`/`.gui` pattern, normally `frameAnimatedSpriteType`. A GIF is only a review preview and is never the final asset. It needs real per-frame source artwork or source frames.

Always apply these rules:

- Every meaningful visual state has its own generated, sourced or hand-authored source frame. Scripts may only assemble, align, crop, pad, sheet, preview and convert frames. They must never create the motion by shifting, scaling, rotating, blurring, recoloring or glowing one still, and primitive geometry is never final art (Core rule below; `references/frame-planning.md`).
- Alpha-backed families request genuine native transparency in the first image-generation call and keep the alpha through DDS conversion (`references/frame-production-and-sheet.md`).
- Use the image generator for frame art. If it is unavailable, stop and report the blocker; do not invent another route (Blockers below).
- Inspect the local wiki page, vanilla file and repository example for the target surface before wiring, and record which one was used (Required HOI4 references below).
- Never put `.gif` in a `.gfx` texture path, never replace an animated final asset with a static image, and never claim a final animation exists when only a GIF or mockup was made.
- Final DDS files go to the real mod asset folders. The temporary `docs/assets/<feature_slug>/animations/` workspace is promoted into permanent documentation and deleted before the feature is complete (`references/package-naming-and-gfx-handoff.md`).

Work in this order: plan (`frame-planning`), produce (`frame-production-and-sheet`), package and hand off (`package-naming-and-gfx-handoff`), add `leader-portrait-overlays` when the animation sits over a leader portrait, and pass `quality-gates` before reporting completion.

## Reference map

- [Source frames, brief and frame plan](references/frame-planning.md): Read before writing the animation brief or frame plan, or when judging whether a frame counts as real source art. Covers: What counts as a real source frame; Required animation brief; Frame plan.
- [Frame generation, processing and sheet construction](references/frame-production-and-sheet.md): Read before generating or sourcing frames, running scripts on them, or assembling the horizontal sheet. Covers: Generation rules; Deterministic processing rules; HOI4 sheet construction.
- [Output package, names, .gfx snippet and wiring handoff](references/package-naming-and-gfx-handoff.md): Read before building the output package, naming files, writing the .gfx snippet or handing the sprite to the wiring agent. Covers: Required output package; Naming rules; `.gfx` handoff pattern; HOI4 wiring handoff.
- [Leader portrait overlay animations](references/leader-portrait-overlays.md): Read before animating over a country leader portrait with a scripted GUI overlay instead of replacing the portrait. Covers: Leader portrait overlay animations.
- [Quality gates](references/quality-gates.md): Read before marking an animation complete or reporting completion. Covers: Quality gates.

## 1. Core rule

A final mod animation is a HOI4 frame-sheet asset package.

Every meaningful visual state in the loop must have its own source frame or source layer. A local script may assemble, align, crop, resize, pad, preview, sheet, and convert those frames, but it must not create the main animation by translating, scaling, rotating, warping, blurring, recoloring, adding glow pulses, or offsetting one still image.

Do not use primitive shape animation as final art. Circles, rectangles, lines, gradients, simple icons, oscilloscope-style waves, bars, and other geometry-only frames are acceptable only as explicitly labeled planning diagrams or temporary debug previews, never as final mod artwork.

A GIF is only a review preview. Never treat a GIF as the final HOI4 asset. Do not convert a GIF directly and call the result complete.

The normal HOI4 deliverable is:

- source frame PNGs
- processed frame PNGs
- a horizontal frame-sheet PNG
- a frame-sheet DDS in the correct gameplay asset folder
- a static fallback DDS
- a `.gfx` sprite definition, usually `frameAnimatedSpriteType`
- `.gui`, character, focus, decision, or scripted GUI wiring that references the sprite name
- a GIF preview only for human review
- manifest and handoff notes

If the user explicitly asks for a temporary mockup, a transform-only preview may be created, but it must be marked as a mockup and never recorded as a final asset.

## 2. HOI4 animation model

HOI4 does not play a GIF as a game asset.

The usual HOI4 animation pattern is a texture sheet plus sprite metadata:

- put frames into one texture sheet
- define the sheet in a `.gfx` file
- use `frameAnimatedSpriteType` for automatic animation
- set `noOfFrames` to the number of frames in the sheet
- set `animation_rate_fps` to the playback rate
- set `looping = yes` or `looping = no`
- set `play_on_show = yes` when the animation should restart when the GUI element appears
- reference the sprite name from the relevant `.gui`, character, focus, decision, or scripted GUI surface

For the common horizontal-sheet pattern, `noOfFrames` divides the texture into equal-width frame columns from left to right. A 64x64 asset with 8 frames should produce a sheet that is 512x64. A 156x210 animated portrait with 10 frames should produce a sheet that is 1560x210.

Do not assume every HOI4 surface accepts animated sprites in the same way. Before wiring, inspect the HOI4 wiki, vanilla examples, local documentation, and existing repository examples for the exact target surface.

## 3. Relationship with other skills

Use this skill with `hoi4-feature-assets`.

`hoi4-feature-assets` owns source mode, reference folders, DDS conversion, manifests, final asset placement, and sprite handoffs. This skill owns frame planning, per-frame generation discipline, anchor normalization, sheet construction, GIF previews, contact sheets, and HOI4 animation QA.

Use the image generator for generated frame art. If the image generator is unavailable, stop and report the blocker. Do not invent another image generation route.

Read [generated source art and review](../hoi4-feature-assets/references/generation-and-review.md) before seed or frame production. Use its model preference only when the actual tool exposes selection. After accepting a seed, use that seed or a neighbouring accepted frame as each edit target, name the exact motion-state delta, and preserve subject, camera, palette, canvas, anchor, and alpha. Record each frame's input candidate and repair lineage. Compare every accepted frame with the seed to detect accumulated drift and loop discontinuity. Each frame still needs its own real visual state.

For every alpha-backed animation family, request a genuine transparent background in the initial image-generation call for every generated source frame and preserve the alpha through normalization, sheet assembly, preview creation, and DDS conversion. Do not generate opaque or chroma-backed frames as the normal route. Use the fallback background-removal workflow in `hoi4-feature-assets` only when native transparency fails or an inherited, sourced, or user-provided frame begins with an unwanted opaque backdrop.

Use `hoi4-focus-trees`, `hoi4-decisions-missions`, `hoi4-events`, or the relevant repository-specific implementation skill for the gameplay surface that uses the animation.

When the animation belongs to a scripted GUI, also use `hoi4-scripted-gui` for the accepted reference mapping, native placement, iterative MCP render review, state and resolution coverage, click-region safety, and final visual acceptance. This animation skill owns the frame package, not the enclosing GUI layout.

Use the owning surface's mandatory MCP evidence whenever frame assets change an in-scope focus, event-chain, technology/doctrine, GUI, or map consumer. Preserve matching baseline and post-change evidence, report the exact unavailable route, and keep the affected surface unresolved if required evidence is missing. Source-only checks or a GIF do not replace that pass.

3D skeletal `.anim` actions are not frame-sheet assets. Route model rigs, retargeting, baked actions, root-motion policy, `.anim` export, reimport proof, and unit or entity runtime binding to `hoi4-3d-model-pipeline`; do not manufacture a skeletal action by moving or filtering one still image, and do not replace a requested action with a 2D frame sheet.

## 4. Required HOI4 references before wiring

Before wiring an animated asset into the game, inspect the local sources that apply to the target surface.

Required references:

- `hoi4_wiki/graphical_asset_modding.md`
- `hoi4_wiki/interface_modding.md` when the animation appears in GUI
- `hoi4_wiki/scripted_gui_modding.md` when the animation appears in scripted GUI
- `hoi4_wiki/character_modding.md` when the animation is a portrait
- relevant vanilla `.gfx` and `.gui` files under `<HOI4_INSTALL_DIR>/`
- existing repository `.gfx`, `.gui`, portrait, focus, decision, and scripted GUI examples when available

The agent must record which local example was used.

If the wiki and vanilla examples disagree, prefer vanilla and document the difference.

If the surface has no clear vanilla or mod animated precedent, report a blocker or ask for permission to run a narrow exploration pass, in the upfront consultation when the spec already shows the gap.

## 5. When to use this skill

Use this skill for:

- animated decision category seals
- animated scripted GUI buttons, cards, meters, borders, warning frames, and progress states
- hover loops, pulse loops, shimmer loops, glow loops, and particle loops
- animated focus route emblems
- animated leader portraits for special routes, hidden formables, supernatural leaders, symbolic leaders, or extreme-route identities
- animated icons, small sprites, warning sprites, route-state sprites, and formable seals
- GIF previews and contact sheets for asset review
- frame sheets that will be wired through `.gfx` or `.gui`

## 18. Blockers

Stop and report a blocker when:

- the image generator is unavailable for generated frame art
- required native transparency cannot be obtained or fallback removal damages the subject, silhouette, or frame-to-frame alpha bounds
- required source frames for a sourced animation cannot be found
- the offline HOI4 wiki page, vanilla file, or existing repository example needed for wiring cannot be inspected
- the repo has no safe known pattern for the requested animated sprite type and the parent did not authorize exploration
- frame identity drifts too much to pass review
- DDS conversion fails
- the sheet dimensions do not match the expected frame count
- the parent prompt gives a frame count, sprite name, target size, or path conflict that cannot be resolved cleanly

Do not silently replace an animated final asset with a static image. Do not claim a final animation exists when only a GIF preview or mockup was created.
