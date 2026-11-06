# hoi4-frame-animation: Output package, names, .gfx snippet and wiring handoff

Part of the [hoi4-frame-animation](../SKILL.md) skill. Read before building the output package, naming files, writing the .gfx snippet or handing the sprite to the wiring agent.

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
docs/assets/<feature_slug>/animations/<asset_slug>/
 brief.md
 frame_plan.md
 source_frames/
 processed_frames/
 sheets/
 previews/
 notes/
```

Final in-game DDS files must still move into the correct mod asset folders. Do not leave final game assets under `docs/assets/`.

The feature-scoped `docs/assets/<feature_slug>/animations/<asset_slug>/` tree is temporary evidence and working material. Keep it while the animation is active, blocked, awaiting review, or undergoing acceptance scenarios. Before declaring the feature fully complete, promote durable frame metadata, provenance, review results, coverage, and sprite handoff facts into permanent feature or plan documentation, verify that no runtime reference points into `docs/assets/`, and delete the complete feature-scoped workspace. An absent workspace is expected after full completion. Never delete the skill-local reference library or another feature's workspace.

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

The handoff must include a ready-to-copy snippet, but the implementation agent must verify it against local vanilla and repository examples before using it.

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
- local wiki page, vanilla file, or mod example used as wiring precedent
- any syntax uncertainty found during vanilla or repo example inspection

If the animated sprite is for a character portrait, record the character key and portrait field that should reference the animated sprite name. If the animated sprite is for a scripted GUI, record the scripted GUI entry point and the static fallback sprite used when the animation is hidden, unsupported, or disabled.

