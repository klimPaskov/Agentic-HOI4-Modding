# Posteffect modding

Posteffects are color correction effects that are applied to the lighting in certain areas (volumes) on the map map. They are used to tint the lighting for areas where the lighting would be noticable different, i.e. deserts.

All posteffects are found in `/Hearts of Iron IV/gfx/posteffect_volumes.txt`.

## Posteffect Values

A posteffect values entry follows this format:

```text
posteffect_values = {
    name = <name>
    inherit = <name>

    lut = <path>

    hdr_min_adjustment = <float>
    hdr_max_adjustment = <float>

    BLOOM_WIDTH = <float>
    BLOOM_SCALE = <float>
    BRIGHT_THRESHOLD = <float>

    tonemap_middlegrey = <float>

}
```

**name** is the name of the posteffect values entry.

**inherit** causes the values for the current posteffect to be inherited from the specified posteffect.

**lut** is the path for the tone map used for this entry.

**hdr_min_adjustment** defines the minimum adjustment used in the HDR effect.

**hdr_max_adjustment** defines the maximum adjustment used in the HDR effect.

**BLOOM_WIDTH** defines the width of the bloom effect.

**BLOOM_SCALE** defines the scale of the bloom effect.

**BRIGHT_THRESHOLD** defines the threshold of the bloom effect.

**tonemap_middlegrey** defines the middle grey used in the tone map.

What vanilla does with the keys above. All 22 `posteffect_values` blocks set `name` and `lut`. `inherit` is set in 19 of them; the three without it are `standard` (the base), `southafrica` and `medither`. `tonemap_middlegrey` is set in 12, `BLOOM_WIDTH`, `BLOOM_SCALE` and `BRIGHT_THRESHOLD` together in 4, `hdr_min_adjustment` in 4 and `hdr_max_adjustment` in 3.

`standard` sets `lut = "gfx/world/colorcorrection.tga"`, `BLOOM_WIDTH = 1.5`, `BLOOM_SCALE = 0.9`, `BRIGHT_THRESHOLD = 0.9` and `tonemap_middlegrey = 0.55`; the other entries inherit these and change what they list. The bloom keys are written in capitals, the others in lower case.

All 17 distinct `lut` files in vanilla are uncompressed 24-bit `.tga` images of 1024 by 32 pixels (a 32 step colour cube laid out in one strip). The 32 step reading is an inference from the size. (unverified) for the layout.

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

Vanilla entry without its comment lines.

A vanilla comment describes `MIN_HDR_ADJUSTMENT` as how the image adapts to dark areas (smaller value gives more night vision) and `MAX_HDR_ADJUSTMENT` as the same for bright areas. Both appear only in comments in capitals; the live keys are lower case `hdr_min_adjustment` and `hdr_max_adjustment`.

## Volumes

### Position Volume

A volume entry specifies an area on the map in which posteffect values are applied. It follows this format:

```text
posteffect_volumes = {
    posteffect_volume = {
        name = <name>
        posteffect_values_day = <name>
        posteffect_values_night = <name>
        posteffect_values_day_winter = <name>
        posteffect_values_night_winter = <name>

        position = {
            <x>
            <y>
            <z>
        }
        size = {
            <width>
            <height>
            <depth>
        }
        fade_distance = <float>
    }
}
```

**name** is the name of the volume entry.

**posteffect_values_day** is the posteffect values entry to use during the day.

**posteffect_values_night** is the posteffect values entry to use during the night.

**posteffect_values_day_winter** is the posteffect values entry to use during the day during winter months.

**posteffect_values_night_winter** is the posteffect values entry to use during the night during winter months.

**position** defines the location of the volume center.

**size** defines the size of the volume box.

**fade_distance** defines the fade distance for the posteffect values.

Facts about the 27 vanilla `posteffect_volume` blocks.

- All 27 set `name`, `posteffect_values_day`, `posteffect_values_night`, `position`, `size` and `fade_distance`. The two winter keys are optional: `posteffect_values_day_winter` is set in 14, `posteffect_values_night_winter` in 13.
- `position` and `size` are written on one line with three numbers: `position = { 1900.0 300.0 800.0 }`, `size = { 500.0 800.0 400.0 }`. The numbers are map coordinates; see [Map modding](map_modding.md#coordinate-system) for the axes. The middle number is the height axis in vanilla (300 centre, 800 size). (unverified) `gfx/posteffect_volumes.txt`
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

Vanilla volume.

Three vanilla volumes name values that no `posteffect_values` block defines: `south_Asia` uses `posteffect_values_night_winter = blue`, and `japan` and `australia` use `posteffect_values_day_winter = winter_values`. Vanilla ships these dangling references. An unknown name is tolerated, but what it falls back to is not stated, so use only names you have defined. A volume with `posteffect_values_day = b9_missing_values` logged "Could not find post effect values for 'b9_missing_values'" at game start, and the game kept running. The exe message "No posteffect_values_day scripted for %s" did not appear. The line names the missing values but not the volume. The camera was not moved over the volume and no screenshot was taken, so the default grade was not seen. The console command `reload posteffectvolumes` exists: it replied "posteffectvolumes reloaded!" and logged the same missing-values line again.

### Height Volume

A height volume entry specifies a height at which to apply posteffect values. It follows this format:

```text
posteffect_volumes = {
    posteffect_height_volume = {
        name = <name>
        posteffect_values_day = <name>
        posteffect_values_night = <name>

        height = <float>
        fade_distance = <float>
    }
}
```

**name** is the name of the volume entry.

**posteffect_values_day** is the posteffect values entry to use during the day.

**posteffect_values_night** is the posteffect values entry to use during the night.

**height** defines at which height the values are applied.

**fade_distance** defines the fade distance for the posteffect values.

Vanilla has three height volumes and they form the base layer of the whole map. Each sets exactly `name`, `posteffect_values_day`, `posteffect_values_night`, `height` and `fade_distance`; none sets winter values.

| Name | Day values | Night values | `height` | `fade_distance` |
| --- | --- | --- | --- | --- |
| `"Base Highest"` | `max_distance` | `max_distance_night` | 1600 | 200 |
| `"Base Medium"` | `mid_distance` | `mid_distance_night` | 900 | 200 |
| `"Base"` | `default` | `default_night` | 0 | 0 |

The `height` values match the camera zoom, as the names `max_distance` and `mid_distance` suggest. No game file states this and it is untested. (unverified) `gfx/posteffect_volumes.txt`

## Tips

Make use of the console commands: `PostEffectVolumes.Enabled` and `PostEffectVolumes.Draw` when working with posteffects. Currently developer-only.

You can reload posteffects by using `reload posteffectvolumes` in the console.

The console commands named above are booleans that the documentation marks as unavailable in a release build: `PostEffectVolumes.Enabled` and `PostEffectVolumes.Draw`. A third command, `PostEffectVolumes.Default <posteffect_values name>`, "toggles default posteffect values" and is not mentioned by the page.

The first lines of `gfx/posteffect_volumes.txt` are comments that list `##reload posteffectvolumes`, `#PostEffectVolumes.Enabled` and `#PostEffectVolumes.Draw`. A `reload posteffectvolumes` command is not in the console documentation, which lists only `PostEffectVolumes.Default`, `.Draw` and `.Enabled` (all "not available in release build"). (unverified) that the reload command exists.
