---
name: chaos-redux-frame-animation
description: Use when Chaos Redux needs animated sprites, animated icons, animated scripted GUI pieces, animated portraits, GIF previews, frame sheets, hover loops, pulsing glows, floating seals, warning pulses, route emblems, or frame-by-frame asset packages. Requires real per-frame source artwork or source frames. For HOI4, the final in-game animation must be a frame sheet texture wired through the verified `.gfx` and `.gui` pattern, usually `frameAnimatedSpriteType`, not a saved GIF.
---

## 1. Core rule

A final Chaos Redux animation is a HOI4 frame-sheet asset package.

Every meaningful visual state in the loop must have its own source frame or source layer. A local script may assemble, align, crop, resize, pad, preview, sheet, and convert those frames, but it must not create the main animation by translating, scaling, rotating, warping, blurring, recoloring, adding glow pulses, or offsetting one still image.

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

Do not assume every HOI4 surface accepts animated sprites in the same way. Before wiring, inspect the offline Paradox wiki snapshot, vanilla examples, local documentation, and existing Chaos Redux examples for the exact target surface.

## 3. Relationship with other skills

Use this skill with `chaos-redux-event-assets`.

`chaos-redux-event-assets` owns source mode, reference folders, DDS conversion, manifests, final asset placement, and sprite handoffs. This skill owns frame planning, per-frame generation discipline, anchor normalization, sheet construction, GIF previews, contact sheets, and HOI4 animation QA.

Use `$imagegen` for generated frame art. If `$imagegen` is unavailable, stop and report the blocker. Do not invent another image generation route.

Use `chaos-redux-super-events`, `hoi4-focus-trees`, `hoi4-decisions-missions`, or `chaos-redux-events` for the gameplay surface that uses the animation.

## 4. Required HOI4 references before wiring

Before wiring an animated asset into the game, inspect the local sources that apply to the target surface.

Required references:

- `paradox_wiki/Graphical asset modding - Hearts of Iron 4 Wiki.md`
- `paradox_wiki/Interface modding - Hearts of Iron 4 Wiki.md` when the animation appears in GUI
- `paradox_wiki/Scripted GUI Modding - Hearts of Iron 4 Wiki.md` when the animation appears in scripted GUI
- `paradox_wiki/Character modding - Hearts of Iron 4 Wiki.md` when the animation is a portrait
- relevant vanilla `.gfx` and `.gui` files under `~/projects/Hearts of Iron IV/`
- existing Chaos Redux `.gfx`, `.gui`, portrait, focus, decision, and scripted GUI examples when available

The agent must record which local example was used.

If the wiki and vanilla examples disagree, prefer vanilla and document the difference.

If the surface has no clear vanilla or Chaos Redux animated precedent, report a blocker or ask for permission to run a narrow exploration pass.

## 5. When to use this skill

Use this skill for:

- animated decision category seals
- animated scripted GUI buttons, cards, meters, borders, warning frames, and progress states
- hover loops, pulse loops, shimmer loops, glow loops, and particle loops
- animated focus route emblems
- animated leader portraits for special routes, hidden formables, supernatural leaders, symbolic leaders, or high-chaos identities
- animated icons, small sprites, warning sprites, route-state sprites, and formable seals
- GIF previews and contact sheets for asset review
- frame sheets that will be wired through `.gfx` or `.gui`

## 6. What counts as a real source frame

A valid source frame can be:

- a separate `$imagegen` output created from the frame plan
- an edit of the approved seed frame where the frame prompt asks for a specific visual state
- a sourced historical image frame when the animation is based on real material
- a user-provided frame
- a hand-authored frame created by an approved art workflow

A valid source frame is not:

- the same image shifted up or down
- the same image scaled or rotated
- the same image with only blur, brightness, glow, opacity, hue, saturation, or contrast changes
- a contact sheet sliced into frames when the sheet itself was not generated as an animation source
- a script-made particle layer placed over one still image unless the parent explicitly requested a mockup
- a GIF split into frames when the GIF itself was created from one transformed still

Subtle effects still need source frames. For example, a glowing seal loop should have generated or sourced frame variants for weak glow, rising glow, peak glow, falling glow, and rest. A floating occult emblem should have source frames where the emblem and light behavior are intentionally drawn for each pose or state.

## 7. Required animation brief

Before generating frames, write a short animation brief.

The brief must include:

- asset name
- in-game use
- gameplay surface that uses it
- target frame size
- frame count
- sheet size, calculated as frame width times frame count by frame height for the common horizontal pattern
- static fallback sprite name
- animated sprite name
- frame timing or frames per second
- loop behavior
- `play_on_show` expectation when relevant
- anchor point, usually center or bottom-center
- source mode for each frame
- whether the subject is real, fictional, symbolic, supernatural, UI-only, or route-state art
- reference folder or existing repo example inspected
- final DDS, PNG, sheet, and preview paths
- target `.gfx` file
- target `.gui`, character, focus, decision, or scripted GUI file if known

## 8. Frame plan

Create a frame plan before calling `$imagegen`.

Recommended frame plan table:

| Frame | Motion state | Visual change | Prompt delta | Anchor note | Loop note |
| --- | --- | --- | --- | --- | --- |
| 000 | rest | base pose and lowest glow | approved seed frame | bottom-center | matches final frame |
| 001 | rising | small upward change and brighter rim | same subject, same camera | bottom-center | easing in |
| 002 | peak | strongest light or highest pose | same subject, same camera | bottom-center | hold if needed |
| 003 | falling | lower light and return motion | same subject, same camera | bottom-center | easing out |

For loops, the first and last frames must connect cleanly. Either repeat the first frame at the end only in the GIF preview, or make the final frame visually close enough to frame 000 that the loop does not pop.

Frame count should usually stay small unless the animation needs more frames. Prefer 4 to 12 frames for small GUI loops. Larger portrait or super-event-adjacent loops may use more frames only when the target surface and performance cost are acceptable.

## 9. Generation rules

Generate or source the frames separately.

For generated frames:

1. Create or approve the static fallback or seed frame first.
2. Keep one subject, one camera angle, one palette, and one composition across all frames.
3. Use the same target framing and anchor language in every frame prompt.
4. Vary only the planned motion state, light state, expression, particle state, or route-state element.
5. Do not ask for text in generated frames.
6. Save every source frame before processing.
7. Reject frames with drifted silhouettes, wrong subject identity, wrong palette, opaque background when transparency is required, visible generated text, or broken loop behavior.

For real people, do not generate fake motion that implies real footage, speech, or new real-world behavior. Use sourced stills and subtle symbolic layers only when the parent scope allows it. Keep the result clearly an in-game portrait or UI asset.

## 10. Deterministic processing rules

Local scripts may do only mechanical processing:

- verify frame count
- check dimensions
- crop transparent padding
- normalize all frames to one shared scale
- align all frames to one shared anchor
- pad to the exact target frame canvas
- create contact sheets
- create GIF previews
- create the horizontal sheet PNG
- verify sheet width equals frame width times frame count
- verify sheet height equals frame height
- create static fallbacks from approved source frames
- convert the static fallback PNG to DDS through the repository workflow
- convert the horizontal sheet PNG to DDS through the repository workflow
- write frame metadata and manifests

Local scripts may not create the animation's main visual change. If a script changes position, opacity, glow, or scale, that output is a preview or assembly artifact unless the same visual change already exists in the generated or sourced frames.

## 11. HOI4 sheet construction

For the common `frameAnimatedSpriteType` pattern, build a one-row horizontal sheet.

Rules:

- every processed frame must have identical dimensions
- each frame must use the same transparent or opaque background rule as the target asset type
- frame order is left to right
- sheet width must be `frame_width * noOfFrames`
- sheet height must be `frame_height`
- do not include gaps, borders, contact-sheet labels, frame numbers, checkerboard backgrounds, or preview-only overlays inside the final sheet
- do not duplicate frame 000 at the end of the final sheet unless the intended loop truly needs that extra frame and `noOfFrames` includes it
- keep the GIF preview separate from the final sheet
- convert the sheet PNG to the final sheet DDS

A sheet path should describe that it is a sheet:

```text
<asset_slug>_sheet.png
<asset_slug>_sheet.dds
```

Do not call the sheet `<asset_slug>_animated.gif`. Do not put `.gif` in `.gfx` texture paths.

## 12. Required output package

An animation package must include:

- source frame PNGs
- processed frame PNGs at exact target frame size
- horizontal sheet PNG
- final horizontal sheet DDS
- static fallback PNG and DDS
- GIF preview for review
- contact sheet when practical
- manifest entry
- `gfx_handoff.md` entry
- frame count, frame timing, loop behavior, target frame size, sheet size, and anchor point
- static fallback sprite name and animated sprite name
- source mode and source notes for every frame
- validation notes

Recommended working structure:

```text
docs/assets/<event_id>_<event_slug>/animations/<asset_slug>/
  brief.md
  frame_plan.md
  source_frames/
  processed_frames/
  sheets/
  previews/
  notes/
```

Final in-game DDS files must still move into the correct mod asset folders. Do not leave final game assets under `docs/assets/`.

## 13. Naming rules

Use lowercase snake_case.

Recommended frame and sheet names:

```text
<asset_slug>_000_source.png
<asset_slug>_001_source.png
<asset_slug>_002_source.png
<asset_slug>_003_source.png
<asset_slug>_004_source.png
<asset_slug>_005_source.png
<asset_slug>_006_source.png
<asset_slug>_007_source.png
<asset_slug>_000.png
<asset_slug>_001.png
<asset_slug>_002.png
<asset_slug>_003.png
<asset_slug>_004.png
<asset_slug>_005.png
<asset_slug>_006.png
<asset_slug>_007.png
<asset_slug>_sheet.png
<asset_slug>_sheet.dds
<asset_slug>_preview.gif
<asset_slug>_contact.png
<asset_slug>_static.png
<asset_slug>_static.dds
```

Sprite names should make the fallback explicit:

```text
GFX_<asset_slug>
GFX_<asset_slug>_animated
```

Keep names stable once the main agent wires them.

## 14. `.gfx` handoff pattern

The handoff must include a ready-to-copy snippet, but the implementation agent must verify it against local vanilla and Chaos Redux examples before using it.

Typical static fallback:

```txt
spriteTypes = {
	spriteType = {
		name = "GFX_<asset_slug>"
		texturefile = "gfx/interface/<folder>/<asset_slug>_static.dds"
	}
}
```

Typical animated sheet:

```txt
spriteTypes = {
	frameAnimatedSpriteType = {
		name = "GFX_<asset_slug>_animated"
		texturefile = "gfx/interface/<folder>/<asset_slug>_sheet.dds"
		noOfFrames = <frame_count>
		animation_rate_fps = <fps>
		looping = yes
		play_on_show = yes
	}
}
```

This snippet is a starting pattern, not proof that a specific GUI surface supports it. The implementation agent must confirm the target surface and existing repo conventions.

## 15. HOI4 wiring handoff

The animation handoff must give the implementation agent enough information to wire without guessing.

For every animated asset, record:

- final static DDS path
- final sheet DDS path
- final sheet PNG path
- proposed static sprite name
- proposed animated sprite name
- target `.gfx` file
- target `.gui` file if relevant
- target frame size
- calculated sheet size
- frame count
- animation rate
- loop behavior
- `play_on_show` behavior
- whether it is decorative or state-driven
- state value, route flag, decision availability, focus route, or GUI state that controls it
- static fallback behavior
- local wiki page, vanilla file, or Chaos Redux example used as wiring precedent
- any syntax uncertainty found during vanilla or repo example inspection

If the animated sprite is for a character portrait, record the character key and portrait field that should reference the animated sprite name. If the animated sprite is for a scripted GUI, record the scripted GUI entry point and the static fallback sprite used when the animation is hidden, unsupported, or disabled.

## 16. Quality gates

Before marking an animation complete, verify:

- every frame has a source PNG
- every processed frame has the same exact dimensions
- transparent assets have real transparent unused pixels
- subject identity, silhouette, palette, camera, and scale stay consistent
- the anchor is stable across frames
- the loop returns cleanly to the starting state
- the GIF preview shows the intended motion
- the GIF preview is marked as review-only
- the contact sheet makes frame drift visible
- static fallback exists and looks acceptable by itself
- sheet PNG exists
- sheet DDS exists
- sheet width equals target frame width times frame count
- sheet height equals target frame height
- `.gfx` snippet uses the sheet DDS path, not a GIF path
- `noOfFrames` equals the number of frames in the final sheet
- `animation_rate_fps`, `looping`, and `play_on_show` are documented
- final DDS files exist in the correct location
- the manifest records source mode, frame count, timing, frame size, sheet size, paths, and status
- `gfx_handoff.md` names the static and animated sprites
- no fake transform-only animation is being presented as final art

## 17. Blockers

Stop and report a blocker when:

- `$imagegen` is unavailable for generated frame art
- required source frames for a sourced animation cannot be found
- the offline HOI4 wiki page, vanilla file, or existing Chaos Redux example needed for wiring cannot be inspected
- the repo has no safe known pattern for the requested animated sprite type and the parent did not authorize exploration
- the target surface may not support `frameAnimatedSpriteType` and no tested alternative exists
- frame identity drifts too much to pass review
- DDS conversion fails
- the sheet dimensions do not match the expected frame count
- the parent prompt gives a frame count, sprite name, target size, or path conflict that cannot be resolved cleanly

Do not silently replace an animated final asset with a static image. Do not claim a final animation exists when only a GIF preview or mockup was created.
