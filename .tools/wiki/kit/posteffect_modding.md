# Posteffect modding

<!-- kit:begin id="review" build="1.19.4.1" checked="2026-11-01" revision="23212" sources="gfx/posteffect_volumes.txt gfx/world/ documentation/console_commands_documentation.md hoi4.exe" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Checked against: all of `gfx/posteffect_volumes.txt` (22 `posteffect_values`, 27 `posteffect_volume`, 3 `posteffect_height_volume`), the 17 colour lookup textures it names in `gfx/world/`, the `PostEffectVolumes.*` entries of `documentation/console_commands_documentation.md`, and token strings in `hoi4.exe`.
Kit blocks added: key usage and an example for `posteffect_values`, the texture format of `lut`, position and height volume facts, three vanilla references to undefined value names, the third console command.
Gaps left: no game file explains the HDR and bloom keys; what happens when two volumes overlap, or when a referenced values name does not exist, is not documented.
**1.19.4.1 re-check (2026-11-01).** One statement (the `PostEffectVolumes.*` console commands) cited the changed console commands documentation, and it was re-checked: the three commands are still listed and only `debug_types` was removed, so nothing on this page changes. The `hoi4.exe` message about `posteffect_values_day` is still in the 1.19.4.1 executable. Every other statement cites files that are byte-identical in 1.19.4.1 (Steam depot manifest diff).
<!-- kit:end id="review" -->

<!-- kit:begin id="posteffect-values-notes" at="section:posteffect-values" -->
What vanilla does with the keys above. All 22 `posteffect_values` blocks set `name` and `lut`. `inherit` is set in 19 of them; the three without it are `standard` (the base), `southafrica` and `medither`. `tonemap_middlegrey` is set in 12, `BLOOM_WIDTH`, `BLOOM_SCALE` and `BRIGHT_THRESHOLD` together in 4, `hdr_min_adjustment` in 4 and `hdr_max_adjustment` in 3. [vanilla-confirmed 1.19.3] `gfx/posteffect_volumes.txt`

`standard` sets `lut = "gfx/world/colorcorrection.tga"`, `BLOOM_WIDTH = 1.5`, `BLOOM_SCALE = 0.9`, `BRIGHT_THRESHOLD = 0.9` and `tonemap_middlegrey = 0.55`; the other entries inherit these and change what they list. The bloom keys are written in capitals, the others in lower case. [vanilla-confirmed 1.19.3] `gfx/posteffect_volumes.txt`

All 17 distinct `lut` files in vanilla are uncompressed 24-bit `.tga` images of 1024 by 32 pixels (a 32 step colour cube laid out in one strip). The 32 step reading is an inference from the size. [vanilla-confirmed 1.19.4.1] `gfx/world/colorcorrection*.tga`, 17 of 17 (TGA header type 2, 24 bits per pixel). [unverified] for the layout.

```text
posteffect_values = {
	name = green_night
	inherit = standard
	lut = "gfx/world/colorcorrection_green_night3.tga"
	tonemap_middlegrey = 0.7
	BLOOM_WIDTH = 2.0
	BLOOM_SCALE = 1.5
	BRIGHT_THRESHOLD = 0.8
	hdr_min_adjustment = 0.8
	hdr_max_adjustment = 0.6
}
```

Vanilla entry without its comment lines. [vanilla-confirmed 1.19.3] `gfx/posteffect_volumes.txt`

A vanilla comment describes `MIN_HDR_ADJUSTMENT` as how the image adapts to dark areas (smaller value gives more night vision) and `MAX_HDR_ADJUSTMENT` as the same for bright areas. Both appear only in comments in capitals; the live keys are lower case `hdr_min_adjustment` and `hdr_max_adjustment`. [vanilla-confirmed 1.19.3] `gfx/posteffect_volumes.txt`
<!-- kit:end id="posteffect-values-notes" -->

<!-- kit:begin id="posteffect-position-notes" at="section:position-volume" -->
Facts about the 27 vanilla `posteffect_volume` blocks. All rows: [vanilla-confirmed 1.19.3] `gfx/posteffect_volumes.txt`.

- All 27 set `name`, `posteffect_values_day`, `posteffect_values_night`, `position`, `size` and `fade_distance`. The two winter keys are optional: `posteffect_values_day_winter` is set in 14, `posteffect_values_night_winter` in 13.
- `position` and `size` are written on one line with three numbers: `position = { 1900.0 300.0 800.0 }`, `size = { 500.0 800.0 400.0 }`. The numbers are map coordinates; see [Map modding](map_modding.md#coordinate-system) for the axes. [vanilla-confirmed 1.19.4.1] `gfx/posteffect_volumes.txt`, 27 of 27 with three numbers each. The middle number is the height axis in vanilla (300 centre, 800 size). [unverified] `gfx/posteffect_volumes.txt`
- `fade_distance` ranges from 30.0 to 300.0 in the position volumes; the most common values are 75.0 (5 volumes) and 200.0 (4 volumes).
- `name` is written bare (`Brazil`) or quoted (`"Base Highest"`).

```text
posteffect_volume = {
	name = Brazil
	posteffect_values_day = green
	posteffect_values_night = green_night
	posteffect_values_day_winter = winter_values_day
	posteffect_values_night_winter = winter_values_night
	position = { 1900.0 300.0 800.0 }
	size = { 500.0 800.0 400.0 }
	fade_distance = 75.0
}
```

Vanilla volume. [vanilla-confirmed 1.19.3] `gfx/posteffect_volumes.txt`

Three vanilla volumes name values that no `posteffect_values` block defines: `south_Asia` uses `posteffect_values_night_winter = blue`, and `japan` and `australia` use `posteffect_values_day_winter = winter_values`. Vanilla ships these dangling references. [vanilla-confirmed 1.19.4.1] `gfx/posteffect_volumes.txt`, still 3 volumes. An unknown name is tolerated, but what it falls back to is not stated, so use only names you have defined. A volume with `posteffect_values_day = b9_missing_values` logged "Could not find post effect values for 'b9_missing_values'" at game start, and the game kept running. The exe message "No posteffect_values_day scripted for %s" did not appear. The line names the missing values but not the volume. The camera was not moved over the volume and no screenshot was taken, so the default grade was not seen. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, one-mod launch, error.log read. The console command `reload posteffectvolumes` exists: it replied "posteffectvolumes reloaded!" and logged the same missing-values line again. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, console reply and error.log read.
<!-- kit:end id="posteffect-position-notes" -->

<!-- kit:begin id="posteffect-height-notes" at="section:height-volume" -->
Vanilla has three height volumes and they form the base layer of the whole map. Each sets exactly `name`, `posteffect_values_day`, `posteffect_values_night`, `height` and `fade_distance`; none sets winter values. [vanilla-confirmed 1.19.3] `gfx/posteffect_volumes.txt`

| Name | Day values | Night values | `height` | `fade_distance` |
| --- | --- | --- | --- | --- |
| `"Base Highest"` | `max_distance` | `max_distance_night` | 1600 | 200 |
| `"Base Medium"` | `mid_distance` | `mid_distance_night` | 900 | 200 |
| `"Base"` | `default` | `default_night` | 0 | 0 |

All rows: [vanilla-confirmed 1.19.3] `gfx/posteffect_volumes.txt`.

The `height` values match the camera zoom, as the names `max_distance` and `mid_distance` suggest. No game file states this and it is untested. [unverified] `gfx/posteffect_volumes.txt`
<!-- kit:end id="posteffect-height-notes" -->

<!-- kit:begin id="posteffect-console" at="section:tips" -->
The console commands named above are booleans that the documentation marks as unavailable in a release build: `PostEffectVolumes.Enabled` and `PostEffectVolumes.Draw`. A third command, `PostEffectVolumes.Default <posteffect_values name>`, "toggles default posteffect values" and is not mentioned by the page. [docs] `documentation/console_commands_documentation.md`

The first lines of `gfx/posteffect_volumes.txt` are comments that list `##reload posteffectvolumes`, `#PostEffectVolumes.Enabled` and `#PostEffectVolumes.Draw`. A `reload posteffectvolumes` command is not in the console documentation, which lists only `PostEffectVolumes.Default`, `.Draw` and `.Enabled` (all "not available in release build"). [vanilla-confirmed 1.19.4.1] `gfx/posteffect_volumes.txt`. [docs] `documentation/console_commands_documentation.md`. [unverified] that the reload command exists.
<!-- kit:end id="posteffect-console" -->
