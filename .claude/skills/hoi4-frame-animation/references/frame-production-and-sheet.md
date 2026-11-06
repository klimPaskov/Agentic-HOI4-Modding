# hoi4-frame-animation: Frame generation, processing and sheet construction

Part of the [hoi4-frame-animation](../SKILL.md) skill. Read before generating or sourcing frames, running scripts on them, or assembling the horizontal sheet.

## 9. Generation rules

Generate or source the frames separately.

For generated frames:

1. Create or approve the static fallback or seed frame first.
2. Keep one subject, one camera angle, one palette, and one composition across all frames.
3. Use the same target framing and anchor language in every frame prompt.
4. Vary only the planned motion state, light state, expression, particle state, or route-state element.
5. For an alpha-backed family, request real transparency in the first image-generation call for every frame and retain the native-alpha source. Do not plan routine background removal.
6. Do not ask for text in generated frames.
7. Save every source frame before processing.
8. Reject frames with drifted silhouettes, wrong subject identity, wrong palette, opaque background for an alpha-backed family, fake checkerboards, halos, matte pixels, alpha drift, visible generated text, or broken loop behavior.

If a frame fails native-transparency validation, use the `hoi4-feature-assets` fallback order: targeted a built-in edit-to-transparency request to the image generator first, then an actually available verified local removal process only if necessary. Preserve the untouched source, record the fallback and settings, and reject clipped silhouettes, coloured spill, internal holes, or edge drift. Never allow one repaired frame to use materially different alpha bounds from the rest of the family without an explicit motion reason.

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
- each frame must use the target asset type's background rule; alpha-backed families default to native image-generator transparency, while deliberately painted full-canvas families remain opaque only when their inspected consumer requires it
- frame order is left to right
- sheet width must be `frame_width * noOfFrames`
- sheet height must be `frame_height`
- do not include gaps, borders, contact-sheet labels, frame numbers, checkerboard backgrounds, or preview-only overlays inside the final sheet
- do not duplicate frame 000 at the end of the final sheet unless the intended loop truly needs that extra frame and `noOfFrames` includes it
- keep the GIF preview separate from the final sheet
- convert the sheet PNG to the final sheet DDS

No texture side may exceed 16384 pixels, the DirectX 11 texture limit. When `frame_width * noOfFrames` would exceed it, first reduce the frame count or frame size. If neither is acceptable, split every frame into the same vertical strips of width `S`, where `S` divides the frame width and `S * noOfFrames` is at most 16384. Register one `frameAnimatedSpriteType` per strip with identical `noOfFrames`, `animation_rate_fps`, `looping`, `play_on_show`, and `pause_on_loop`, and show one GUI child per strip at contiguous x positions with no gaps or overlap. When a child uses `Orientation = center` and `Origo = center`, its position is the strip centre, so strip `i` of a frame `W` pixels wide sits at `x = -W/2 + S/2 + i * S`.

A sheet path should describe that it is a sheet:

```text
<asset_slug>_sheet.png
<asset_slug>_sheet.dds
```

Do not call the sheet `<asset_slug>_animated.gif`. Do not put `.gif` in `.gfx` texture paths.

