# Posteffect modding

*Offline snapshot of the Hearts of Iron IV Wiki page "Posteffect modding", revision 23212, captured 2026-10-31. Wiki text by the wiki's contributors under CC BY-SA 3.0 (see LICENSE.txt); kit blocks are local additions under the same license.*

<!-- kit:begin id="review" at="top" build="1.19.3.0" checked="2026-10-31" revision="23212" sources="gfx/posteffect_volumes.txt gfx/world/ documentation/console_commands_documentation.md hoi4.exe" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Checked against: all of `gfx/posteffect_volumes.txt` (22 `posteffect_values`, 27 `posteffect_volume`, 3 `posteffect_height_volume`), the 17 colour lookup textures it names in `gfx/world/`, the `PostEffectVolumes.*` entries of `documentation/console_commands_documentation.md`, and token strings in `hoi4.exe`.
Kit blocks added: key usage and an example for `posteffect_values`, the texture format of `lut`, position and height volume facts, three vanilla references to undefined value names, the third console command.
Gaps left: no game file explains the HDR and bloom keys; what happens when two volumes overlap, or when a referenced values name does not exist, is not documented.
<!-- kit:end id="review" -->

## Table of contents

- [Posteffect Values](#Posteffect_Values)
- [Volumes](#Volumes)
  - [Position Volume](#Position_Volume)
  - [Height Volume](#Height_Volume)
- [Tips](#Tips)

---

Posteffects are color correction effects that are applied to the lighting in certain areas (volumes) on the map map. They are used to tint the lighting for areas where the lighting would be noticable different, i.e. deserts.

All posteffects are found in `/Hearts of Iron IV/gfx/posteffect_volumes.txt`.

## Posteffect Values <a id="Posteffect_Values"></a>

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

<!-- kit:begin id="posteffect-values-notes" at="section:Posteffect_Values" -->
**Kit note** What vanilla does with the keys above. All 22 `posteffect_values` blocks set `name` and `lut`. `inherit` is set in 19 of them; the three without it are `standard` (the base), `southafrica` and `medither`. `tonemap_middlegrey` is set in 12, `BLOOM_WIDTH`, `BLOOM_SCALE` and `BRIGHT_THRESHOLD` together in 4, `hdr_min_adjustment` in 4 and `hdr_max_adjustment` in 3. [vanilla-confirmed 1.19.3] `gfx/posteffect_volumes.txt`

`standard` sets `lut = "gfx/world/colorcorrection.tga"`, `BLOOM_WIDTH = 1.5`, `BLOOM_SCALE = 0.9`, `BRIGHT_THRESHOLD = 0.9` and `tonemap_middlegrey = 0.55`; the other entries inherit these and change what they list. The bloom keys are written in capitals, the others in lower case. [vanilla-confirmed 1.19.3] `gfx/posteffect_volumes.txt`

All 17 distinct `lut` files in vanilla are uncompressed 24-bit `.tga` images of 1024 by 32 pixels (a 32 step colour cube laid out in one strip). The 32 step reading is an inference from the size. [vanilla-confirmed 1.19.3] `gfx/world/colorcorrection*.tga`. [unverified] for the layout.

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

## Volumes <a id="Volumes"></a>

### Position Volume <a id="Position_Volume"></a>

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

<!-- kit:begin id="posteffect-position-notes" at="section:Position_Volume" -->
**Kit note** Facts about the 27 vanilla `posteffect_volume` blocks. All rows: [vanilla-confirmed 1.19.3] `gfx/posteffect_volumes.txt`.

- All 27 set `name`, `posteffect_values_day`, `posteffect_values_night`, `position`, `size` and `fade_distance`. The two winter keys are optional: `posteffect_values_day_winter` is set in 14, `posteffect_values_night_winter` in 13.
- `position` and `size` are written on one line with three numbers: `position = { 1900.0 300.0 800.0 }`, `size = { 500.0 800.0 400.0 }`. The numbers are map coordinates; see [Map modding](<Map modding - Hearts of Iron 4 Wiki.md#Coordinate_system>) for the axes. The middle number is the height axis in vanilla (300 centre, 800 size). [unverified] `gfx/posteffect_volumes.txt`
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

Three vanilla volumes name values that no `posteffect_values` block defines: `south_Asia` uses `posteffect_values_night_winter = blue`, and `japan` and `australia` use `posteffect_values_day_winter = winter_values`. Vanilla ships these dangling references. [vanilla-confirmed 1.19.3] `gfx/posteffect_volumes.txt`. That suggests an unknown name is tolerated, but what it falls back to is not stated, so use only names you have defined. The exe has the message "No posteffect_values_day scripted for %s". [unverified] `hoi4.exe`
<!-- kit:end id="posteffect-position-notes" -->

### Height Volume <a id="Height_Volume"></a>

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

<!-- kit:begin id="posteffect-height-notes" at="section:Height_Volume" -->
**Kit note** Vanilla has three height volumes and they form the base layer of the whole map. Each sets exactly `name`, `posteffect_values_day`, `posteffect_values_night`, `height` and `fade_distance`; none sets winter values. [vanilla-confirmed 1.19.3] `gfx/posteffect_volumes.txt`

| Name | Day values | Night values | `height` | `fade_distance` |
| --- | --- | --- | --- | --- |
| `"Base Highest"` | `max_distance` | `max_distance_night` | 1600 | 200 |
| `"Base Medium"` | `mid_distance` | `mid_distance_night` | 900 | 200 |
| `"Base"` | `default` | `default_night` | 0 | 0 |

All rows: [vanilla-confirmed 1.19.3] `gfx/posteffect_volumes.txt`.

The `height` values match the camera zoom, as the names `max_distance` and `mid_distance` suggest. [unverified] `gfx/posteffect_volumes.txt`
<!-- kit:end id="posteffect-height-notes" -->

## Tips <a id="Tips"></a>

Make use of the console commands: `PostEffectVolumes.Enabled` and `PostEffectVolumes.Draw` when working with posteffects. Currently developer-only.

You can reload posteffects by using `reload posteffectvolumes` in the console.

<!-- kit:begin id="posteffect-console" at="section:Tips" -->
**Kit note** The console commands named above are booleans that the documentation marks as unavailable in a release build: `PostEffectVolumes.Enabled` and `PostEffectVolumes.Draw`. A third command, `PostEffectVolumes.Default <posteffect_values name>`, "toggles default posteffect values" and is not mentioned by the page. [docs] `documentation/console_commands_documentation.md`

The first lines of `gfx/posteffect_volumes.txt` are comments that list `##reload posteffectvolumes`, `#PostEffectVolumes.Enabled` and `#PostEffectVolumes.Draw`. A `reload posteffectvolumes` command is not in the console documentation. [vanilla-confirmed 1.19.3] `gfx/posteffect_volumes.txt`. [unverified] that the reload command exists.
<!-- kit:end id="posteffect-console" -->

---

## Navigation

**[Modding](<Modding - Hearts of Iron 4 Wiki.md>)**

- **Documentation**: [Effects](<Effects - Hearts of Iron 4 Wiki.md>) • [Triggers](<Triggers - Hearts of Iron 4 Wiki.md>) • [Defines](<Defines - Hearts of Iron 4 Wiki.md>) • [Modifiers](<Modifiers - Hearts of Iron 4 Wiki.md>) • [List of modifiers](<List of modifiers - Hearts of Iron 4 Wiki.md>) • [Scopes](<Scopes - Hearts of Iron 4 Wiki.md>) • [Localisation](<Localisation - Hearts of Iron 4 Wiki.md>) • [On actions](<On actions - Hearts of Iron 4 Wiki.md>) • [Data structures](<Data structures - Hearts of Iron 4 Wiki.md>) • [Flags](<Data structures - Hearts of Iron 4 Wiki.md#Flags>) • [Event targets](<Data structures - Hearts of Iron 4 Wiki.md#Event_targets>) • [Country tag aliases](<Data structures - Hearts of Iron 4 Wiki.md#Country_tag_aliases>) • [Variables](<Data structures - Hearts of Iron 4 Wiki.md#Variables>) • [Arrays](<Data structures - Hearts of Iron 4 Wiki.md#Arrays>)
- **Scripting**: [Achievements](<Achievement modding - Hearts of Iron 4 Wiki.md>) • [AI](<AI modding - Hearts of Iron 4 Wiki.md>) • [AI focuses](<AI focuses - Hearts of Iron 4 Wiki.md>) • [Autonomous states](<Autonomy state modding - Hearts of Iron 4 Wiki.md>) • [Balances of power](<Balance of power modding - Hearts of Iron 4 Wiki.md>) • [Bookmarks/Scenarios](<Bookmark modding - Hearts of Iron 4 Wiki.md>) • [Game rules](<Bookmark modding - Hearts of Iron 4 Wiki.md#Game_rules>) • [Buildings](<Building modding - Hearts of Iron 4 Wiki.md>) • [Characters and traits](<Character modding - Hearts of Iron 4 Wiki.md>) • [Cosmetic tags](<Cosmetic tag modding - Hearts of Iron 4 Wiki.md>) • [Countries](<Country creation - Hearts of Iron 4 Wiki.md>) • [Divisions](<Division modding - Hearts of Iron 4 Wiki.md>) • [Decisions](<Decision modding - Hearts of Iron 4 Wiki.md>) • [Doctrines](<Doctrine modding - Hearts of Iron 4 Wiki.md>) • [Equipment](<Equipment modding - Hearts of Iron 4 Wiki.md>) • [Events](<Event modding - Hearts of Iron 4 Wiki.md>) • [Factions](<Faction modding - Hearts of Iron 4 Wiki.md>) • [Ideas](<Idea modding - Hearts of Iron 4 Wiki.md>) • [Ideologies](<Ideology modding - Hearts of Iron 4 Wiki.md>) • [Military industrial organizations](<Military industrial organization modding - Hearts of Iron 4 Wiki.md>) • [National focuses](<National focus modding - Hearts of Iron 4 Wiki.md>) • [Resources](<Resources modding - Hearts of Iron 4 Wiki.md>) • [Scripted GUI](<Scripted GUI modding - Hearts of Iron 4 Wiki.md>) • [Technologies and doctrines](<Technology modding - Hearts of Iron 4 Wiki.md>) • [Units](<Unit modding - Hearts of Iron 4 Wiki.md>)
- **Map**: [Map](<Map modding - Hearts of Iron 4 Wiki.md>) • [States](<State modding - Hearts of Iron 4 Wiki.md>) • [Supply areas](<Supply areas modding - Hearts of Iron 4 Wiki.md>) • [Strategic regions](<Strategic region modding - Hearts of Iron 4 Wiki.md>)
- **Graphical**: [Interface](<Interface modding - Hearts of Iron 4 Wiki.md>) • [Graphical assets](<Graphical asset modding - Hearts of Iron 4 Wiki.md>) • [Entities](<Entity modding - Hearts of Iron 4 Wiki.md>) • [Particles](<Particle modding - Hearts of Iron 4 Wiki.md>) • [Fonts](<Font modding - Hearts of Iron 4 Wiki.md>)
- **Cosmetic**: [Portraits](<Portrait modding - Hearts of Iron 4 Wiki.md>) • [Namelists](<Namelist modding - Hearts of Iron 4 Wiki.md>) • [Music](<Music modding - Hearts of Iron 4 Wiki.md>) • [Sound](<Sound modding - Hearts of Iron 4 Wiki.md>)
- **Other**: [Console commands](<Console commands - Hearts of Iron 4 Wiki.md>) • [Troubleshooting](<Troubleshooting - Hearts of Iron 4 Wiki.md>) • [Mod structure](<Mod structure - Hearts of Iron 4 Wiki.md>) • [Mods](<Mods - Hearts of Iron 4 Wiki.md>) • [Nudger](<Nudger - Hearts of Iron 4 Wiki.md>)
- **Kit pages (not on the wiki)**: [Collection modding](<Collection modding - Hearts of Iron 4 Wiki.md>) • [Game rule modding](<Game rule modding - Hearts of Iron 4 Wiki.md>) • [Intelligence operation modding](<Intelligence operation modding - Hearts of Iron 4 Wiki.md>) • [Map mode modding](<Map mode modding - Hearts of Iron 4 Wiki.md>) • [Occupation and resistance modding](<Occupation and resistance modding - Hearts of Iron 4 Wiki.md>) • [Peace conference modding](<Peace conference modding - Hearts of Iron 4 Wiki.md>) • [Raid modding](<Raid modding - Hearts of Iron 4 Wiki.md>) • [Script constant modding](<Script constant modding - Hearts of Iron 4 Wiki.md>) • [Special project modding](<Special project modding - Hearts of Iron 4 Wiki.md>)
