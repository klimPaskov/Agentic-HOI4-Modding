# hoi4-frame-animation: Quality gates

Part of the [hoi4-frame-animation](../SKILL.md) skill. Read before marking an animation complete or reporting completion.

## 17. Quality gates

Before marking an animation complete, verify:

- every frame has a source PNG
- every processed frame has the same exact dimensions
- alpha-backed assets retain real native transparent unused pixels, or contain a documented and edge-validated fallback repair
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
- before full completion, durable sprite and frame facts from the temporary handoff are copied into permanent feature or plan documentation and the feature-scoped workspace is deleted
- scripted GUI leader overlays parent to a valid loaded window, not an unverified nested `*_instance`
- leader overlay handoffs record the vanilla file, portrait element, parent window, context type, position, scale, and any summed offsets
- no fake transform-only animation is being presented as final art

