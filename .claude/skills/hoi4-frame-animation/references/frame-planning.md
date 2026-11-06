# hoi4-frame-animation: Source frames, brief and frame plan

Part of the [hoi4-frame-animation](../SKILL.md) skill. Read before writing the animation brief or frame plan, or when judging whether a frame counts as real source art.

## 6. What counts as a real source frame

A valid source frame can be:

- a separate image-generator output created from the frame plan
- an edit of the approved seed frame where the frame prompt asks for a specific visual state
- a sourced historical image frame when the animation is based on real material
- a user-provided frame
- a hand-authored frame created by an approved art workflow

A valid source frame is not:

- the same image shifted up or down
- the same image scaled or rotated
- the same image with only blur, brightness, glow, opacity, hue, saturation, or contrast changes
- frames made from only primitive shapes, waveform lines, bars, gradients, or other geometry-only placeholders
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
- background mode for the family and every exception: `native_transparent`, `consumer_opaque`, or `fallback_removed`
- whether the subject is real, fictional, symbolic, supernatural, UI-only, or route-state art
- reference folder or existing repo example inspected
- final DDS, PNG, sheet, and preview paths
- target `.gfx` file
- target `.gui`, character, focus, decision, or scripted GUI file if known

## 8. Frame plan

Create a frame plan before calling the image generator.

Recommended frame plan table:

| Frame | Motion state | Visual change | Prompt delta | Anchor note | Loop note |
| --- | --- | --- | --- | --- | --- |
| 000 | rest | base pose and lowest glow | approved seed frame | bottom-center | matches final frame |
| 001 | rising | small upward change and brighter rim | same subject, same camera | bottom-center | easing in |
| 002 | peak | strongest light or highest pose | same subject, same camera | bottom-center | hold if needed |
| 003 | falling | lower light and return motion | same subject, same camera | bottom-center | easing out |

For loops, the first and last frames must connect cleanly. Either repeat the first frame at the end only in the GIF preview, or make the final frame visually close enough to frame 000 that the loop does not pop.

Use enough real source frames for the motion to be smooth. More sprites are better than a choppy loop when the target surface and texture size can reasonably support them, especially for subtle pulses, breathing light, drifting particles, animated portraits, and slow UI state changes.

Do not be lazy with frame count. Do not choose a small number of frames just to finish faster, and do not hide a rough low-frame loop behind filters, transforms, or opacity tricks. If a low frame count is used, the brief must justify it with the target size, performance cost, or intentionally stepped motion.

