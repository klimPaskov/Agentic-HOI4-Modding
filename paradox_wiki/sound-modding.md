# Sound modding

*Offline snapshot of the Hearts of Iron IV Wiki page "Sound modding", revision 79549, captured 2026-10-31. Wiki text by the wiki's contributors under CC BY-SA 3.0 (see LICENSE.txt); kit blocks are local additions under the same license.*

<!-- kit:begin id="review" at="top" build="1.19.3.0" checked="2026-10-31" revision="79549" sources="sound/ integrated_dlc/dlc022_waking_the_tiger/sound/ dlc/dlc021_anniversary_pack/sound/ interface/ documentation/effects_documentation.md gfx/entities/" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Checked against: the 22 `.asset` files in `sound/` and the `sound/` folders of the DLC (3387 `sound`, 796 `soundeffect`, 16 `falloff` and 22 `category` blocks, plus the two global compressors), the 982 `.wav` headers in `sound/`, the `clicksound` and `oversound` keys of `interface/*.gui` and `interface/*.gfx`, and `sound_effect` in `documentation/effects_documentation.md`.
Kit blocks added: a correction of the audio format advice, vanilla key census for `sound`, `soundeffect`, `falloff` and `category`, the two global compressors, and how GUI, entities and script refer to a sound effect.
Gaps left: no game file explains `looping_delay_random_offset`, `looping_playbackrate_random_offset`, `polyphony` or the unit of `playbackrate_random_offset`, and the compressor values have no documentation.
<!-- kit:end id="review" -->

## Table of contents

- [Sound](#Sound)
- [Sound Effect](#Sound_Effect)
- [Falloff](#Falloff)
- [Categories](#Categories)
- [Compressors](#Compressors)

---

Sound definitions are found in `/Hearts of Iron IV/sound`. A sound file should be saved as a **WAV** file in Stereo, as a mono channel, at 44100Hz and as a 32-bit float.

All of the sound definition files must be saved as **.asset** files.

## Sound <a id="Sound"></a>

<!-- kit:begin id="sound-format-correction" at="heading:Sound" -->
**Kit correction** The format line in the intro ("Stereo, as a mono channel, at 44100Hz and as a 32-bit float") contradicts itself and does not match vanilla. All 982 `.wav` files in `sound/` are uncompressed PCM at 44100 Hz. 959 are 16-bit and 23 are 24-bit; 687 are stereo and 295 mono. None is 32-bit float, and `sound/` holds no `.ogg` file. [vanilla-confirmed 1.19.3] `sound/` (WAV headers)

Both stereo and mono files are used by 3D effects (`is3d = yes`): 371 stereo and 304 mono sound references. So mono is not required for 3D playback in vanilla. [vanilla-confirmed 1.19.3] `sound/soundeffects.asset`

Sound definitions are plain `.asset` text files, and every `sound` file is relative to the `sound` folder that holds the `.asset` (`menu/confirm_dog.wav`; in a DLC, `pol/pol_idle_001.wav` inside `dlc/dlc021_anniversary_pack/sound/`). [vanilla-confirmed 1.19.3] `sound/sound.asset`, `dlc/dlc021_anniversary_pack/sound/`
<!-- kit:end id="sound-format-correction" -->

A **sound** entry is used to define a sound. It follows this format:

```text
sound = {
    name = <name>
    file = <path>
    always_load = <bool>
    volume = <float>
}
```

**name** is the name of the sound definition that is referred to by other files.

**file** is the path to the sound file, relative to the Hearts of Iron IV **sound** folder.

**always_load** defines whether the sound is always loaded.

**volume** defines the volume of the sound.

<!-- kit:begin id="sound-sound-notes" at="section:Sound" -->
**Kit note** Over the 3387 vanilla `sound` blocks: all set `name` and `file`; `always_load` is written in 185 (`no` 169, `yes` 16) and `volume` in 161 (0.5 in 111 of them, then 0.6, 0.55, 1.8). [vanilla-confirmed 1.19.3] `sound/sound.asset`

A `sound` and a `soundeffect` may share a name. `click_default` is both a `sound` (in `sound/sound.asset`) and a `soundeffect` that plays it (in `sound/gui/gui_sound_effects.asset`). All sound names in `soundeffect` blocks resolve to a `sound`. [vanilla-confirmed 1.19.3] `sound/sound.asset`, `sound/gui/gui_sound_effects.asset`

Nine vanilla `sound` entries name `.wav` files that are not in the folder, for example `audiofiles/building_large_fall_slow_01.wav` (the folder has `building_large_fall_slow_01_01.wav`). The game ships with them, so a wrong path does not stop the game; keep paths exact anyway. [vanilla-confirmed 1.19.3] `sound/sound.asset`, `sound/audiofiles/`. That a wrong path is harmless in general is an inference. [unverified] `sound/sound.asset`

```text
sound = {
	name = "confirm_dog"
	file = "menu/confirm_dog.wav"
	always_load = no
}
```

Vanilla block, whitespace changed. [vanilla-confirmed 1.19.3] `sound/sound.asset`
<!-- kit:end id="sound-sound-notes" -->

## Sound Effect <a id="Sound_Effect"></a>

A **soundeffect** entry is used to define a soundeffect. It follows this format:

```text
soundeffect = {
    name = <name>
    falloff = <name>
    sounds = {
        sound = <name>
        weighted_sound = {
            sound = <name>
            weight = int
        }
    }

    loop = <bool>
    is3d = <bool>
    random_sound_when_looping = <bool>

    max_audible = <int>
    max_audible_behaviour = <type>

    volume = <float>
    fade_in = <float>
    fade_out = <float>

	looping_delay_random_offset = <bool>
    delay_random_offset = {
        <float>
        <float>
    }

	looping_playbackrate_random_offset = <bool>
    playbackrate_random_offset = {
        <float>
        <float>
    }

    volume_random_offset = {
        <float>
        <float>
    }

    prevent_random_repetition = <bool>
}
```

**name** is the name of the soundeffect.

**falloff** is the falloff entry used by the sound effect.

**sounds** is the sound entries used by the sound effect.

**loop** defines whether the soundeffect loops.

**is3d** defines whether the sound effect should utilise 3D sound.

**random_sound_when_looping** defines whether the soundeffect picks a random sound when looping, rather than picking iteratively.

**max_audible** defines the maximum amount of instances of the sound effect in one moment.

**max_audible_behaviour** defines what happens when more than *max_audible* instances happens. It is always **fail**.

**volume** defines the volume of the sound effect.

**fade_in** defines the fade in duration for the sound effect.

**fade_out** defines the fade out duration for the sound effect.

**looping_delay_random_offset** ???

**delay_random_offset** defines the minimum and maximum random offset to the delay between sound loops.

**looping_playbackrate_random_offset** ???

**playbackrate_random_offset** defines the minimum and maximum random offset to the playback rate between sound loops.

**volume_random_offset** defines the minimum and maximum random offset to the volume between sound loops.

**prevent_random_repetition** prevents the same sounds from playing right after it was played

<!-- kit:begin id="sound-effect-notes" at="section:Sound_Effect" -->
**Kit note** Key counts over the 796 vanilla `soundeffect` blocks. All rows: [vanilla-confirmed 1.19.3] `sound/soundeffects.asset`, `sound/gui/gui_sound_effects.asset`, `integrated_dlc/dlc022_waking_the_tiger/sound/wtt_soundeffects.asset`.

| Key | Sets | Values in vanilla |
| --- | --- | --- |
| `name`, `sounds` | 796 | `name` may be bare or quoted |
| `volume` | 719 | 0.55 (114), 0.85 (92), 0.65 (66), 0.45 (65), 0.35 (62), 1.0 (45) |
| `max_audible` | 620 | 1 (372), 3 (80), 2 (57), 4 (54), 5 (46), 8 (10), 6 (1) |
| `max_audible_behaviour` | 592 | always `fail` |
| `is3d` | 302 | `yes` 241, `no` 61 |
| `falloff` | 253 | `falloff_100` (173), `falloff_trains_medium` (33), `falloff_combat_ambient` (11), `falloff_80` (11), `falloff_weather` (7) |
| `playbackrate_random_offset` | 259 | a pair such as `{ -5.0 5.0 }` |
| `volume_random_offset` | 224 | a pair |
| `loop` | 184 | `yes` 113, `no` 71 |
| `delay_random_offset` | 79 | a pair such as `{ 0.0 1.5 }` |
| `prevent_random_repetition` | 60 | `yes` 57, `no` 3 |
| `random_sound_when_looping` | 48 | `no` 45, `yes` 3 |
| `fade_out` | 46 | 0.40 and 2.0 (11 each), 0.4, 0.5, 0.8 |
| `fade_in` | 43 | 0.2, 0.20, 0.3, 0.5, 0.45 |
| `looping_delay_random_offset` | 16 | `no` 9, `yes` 7 (the page marks it ???) |
| `polyphony` | 10 | 3 (5), 2 (4), 1 (1); not on the page |
| `looping_playbackrate_random_offset` | 1 | `yes` (the page marks it ???) |

The `sounds` block holds `sound = <name>` lines (5232 in vanilla) and `weighted_sound = { sound = <name> weight = <int> }` lines (62). Vanilla mixes a silent buffer into a weighted list to make a sound rare: ten train horns with `weight = 2` and `silence_buffer_1s` with `weight = 42`. [vanilla-confirmed 1.19.3] `sound/soundeffects.asset`

```text
soundeffect = {
	name = click_default
	volume = 0.45
	sounds = {
		sound = click_default
	}
}
```

Smallest vanilla form: only `name`, `volume` and `sounds`. [vanilla-confirmed 1.19.3] `sound/gui/gui_sound_effects.asset`
<!-- kit:end id="sound-effect-notes" -->

## Falloff <a id="Falloff"></a>

Falloff entries define the falloff attributes for sound. They are added in sound effects, and follow this format:

```text
falloff = {
    name = <name>

    min_distance = <float>
    max_distance = <float>
    height_scale = <float>
}
```

**name** is the name of the falloff entry.

**min_distance** is the minimum distance before falloff is applied, i.e. max volume

**max_distance** is the maximum distance before no sound is heard.

**height_scale** is a scalar for the height between the sound source and the player camera.

<!-- kit:begin id="sound-falloff-notes" at="section:Falloff" -->
**Kit note** The 16 vanilla falloffs. 15 are in `sound/falloff.asset`; `falloff_combat_ambient` is in the Waking the Tiger DLC (`min_distance = 120`, `max_distance = 190`, `height_scale = 0.9`) and is the only one with a `type`, which is `linear`. `height_scale` is missing from one entry. [vanilla-confirmed 1.19.3] `sound/falloff.asset`, `integrated_dlc/dlc022_waking_the_tiger/sound/`

| Name | `min_distance` | `max_distance` | `height_scale` |
| --- | --- | --- | --- |
| `falloff_50` | 50 | 60 | 1.0 |
| `falloff_80` | 20 | 80 | 0.6 |
| `falloff_100` | 20 | 120 | 0.6 |
| `falloff_200` | 30 | 200 | 0.5 |
| `falloff_300` | 40 | 300 | 0.5 |
| `falloff_weather` | 30 | 180 | 0.6 |
| `falloff_nuke` | 100 | 500 | 0.7 |
| `falloff_distance` | 80 | 250 | 0.9 |
| `falloff_infantry` | 30 | 60 | 0.7 |
| `falloff_ocean` | 200 | 450 | 1.9 |
| `falloff_trains_medium` | 25 | 66 | 0.5 |

All rows: [vanilla-confirmed 1.19.3] `sound/falloff.asset`. The file also has `falloff_airplane_light`, `falloff_airplane_medium`, `falloff_airplane_heavy` and `falloff_floating_harbour`.

A `soundeffect` refers to a falloff by name, bare or quoted: `falloff = "falloff_100"`. [vanilla-confirmed 1.19.3] `sound/soundeffects.asset`
<!-- kit:end id="sound-falloff-notes" -->

## Categories <a id="Categories"></a>

Sound effects can be placed in sound categories that apply a specific compressor to the sounds. The categories follow this format:

```text
category = {
    name = <name>
    soundeffects = {
        <name>
    }
    compressor = {
        enabled = yes
        pregain = <float>
        postgain = <float>
        ratio = <float>
        threshold = <float>
        attacktime = <float>
        releasetime = <float>
    }
}
```

**name** is the name of the soundeffect category.

**soundeffects** is a list of the sound effects belong to the category.

**compressor** is the compressor to use for the category, see below for more information on the attributes.

<!-- kit:begin id="sound-category-notes" at="section:Categories" -->
**Kit note** Vanilla has 22 `category` blocks. `sound/category.asset` defines `"Effects"`, `"Battle"`, `"UI"`, `"nonControllableEntities"` and `"Atmosphere"`; DLC files add `"Voices"` blocks (for example `POR_infantry_idle`). `soundeffects` is a bare list of sound effect names, one per line, with `#` comment lines allowed. A `compressor` block appears in 6 categories and always sets all of `enabled`, `pregain`, `postgain`, `ratio`, `threshold`, `attacktime`, `releasetime`. [vanilla-confirmed 1.19.3] `sound/category.asset`, `dlc/dlc021_anniversary_pack/sound/`

```text
category = {
	name = "Voices"
	soundeffects = {
		POR_infantry_idle
		POR_infantry_neutral_combat
	}
}
```

Vanilla block, shortened. [vanilla-confirmed 1.19.3] `dlc/dlc028_la_resistance/sound/`
<!-- kit:end id="sound-category-notes" -->

## Compressors <a id="Compressors"></a>

There are two global compressors: **master_compressor** used for sounds and **music_compressor** used for music. Individual compressors can be defined for sounds within categories.

The compressors use the following format:

```text
<name> = {
    pregain = <float>
    postgain = <float>
    ratio = <float>
    threshold = <float>
    attacktime = <float>
    releasetime = <float>
}
```

<!-- kit:begin id="sound-compressor-values" at="section:Compressors" -->
**Kit note** The two global compressors are in `sound/compressor.asset`. They are written as bare top-level blocks without `enabled`. [vanilla-confirmed 1.19.3] `sound/compressor.asset`

| Block | `pregain` | `postgain` | `ratio` | `threshold` | `attacktime` | `releasetime` |
| --- | --- | --- | --- | --- | --- | --- |
| `master_compressor` | 4.0 | 5.0 | 5 | -10 | 0.030 | 1.20 |
| `music_compressor` | 0.0 | -2.0 | 0 | 0 | 0.00 | 0.0 |

All rows: [vanilla-confirmed 1.19.3] `sound/compressor.asset`.
<!-- kit:end id="sound-compressor-values" -->

<!-- kit:begin id="sound-usage" at="bottom" -->
**Kit addition** Where a sound effect name is used.

- Interface elements: `clicksound = <soundeffect>` and `oversound = <soundeffect>` on buttons and similar widgets. Vanilla top-level `interface/*.gui` files have 1704 `clicksound` lines (`click_default` 758, `click_checkbox` 347, `click_close` 227, `click_scroll` 81, `click_ok` 51) and 297 `oversound` lines (`ui_menu_over` 284, `traits_ui_over` 7). All of these names are `soundeffect` blocks in `sound/gui/gui_sound_effects.asset`. [vanilla-confirmed 1.19.3] `interface/*.gui`, `sound/gui/gui_sound_effects.asset`
- Sprites: 23 `spriteType` blocks set `clicksound` in `.gfx` (see [Graphical asset modding](<graphical-asset-modding.md#spriteType>)). [vanilla-confirmed 1.19.3] `interface/chat.gfx`
- Entities: `event = { sound = { soundeffect = <name> } }` (see [Entity modding](<entity-modding.md#Event>)). [vanilla-confirmed 1.19.3] `gfx/entities/buildings.asset`
- Script: `sound_effect = <name>` plays a sound effect in any scope and `scoped_sound_effect` plays it only for the player of the scope. Vanilla uses `sound_effect = command_power_ability_offensive` (8 times) and quoted names such as `"Martial_Law_Interface_No_Garrison"`. [docs] `documentation/effects_documentation.md`. The vanilla uses are [vanilla-confirmed 1.19.3] `common/`
- Music uses a separate system; see [Music modding](<music-modding.md>). [vanilla-confirmed 1.19.3] `music/`
<!-- kit:end id="sound-usage" -->

---

## Navigation

**[Modding](<modding.md>)**

- **Documentation**: [Effects](<effects.md>) • [Triggers](<triggers.md>) • [Defines](<defines.md>) • [Modifiers](<modifiers.md>) • [List of modifiers](<list-of-modifiers.md>) • [Scopes](<scopes.md>) • [Localisation](<localisation.md>) • [On actions](<on-actions.md>) • [Data structures](<data-structures.md>) • [Flags](<data-structures.md#Flags>) • [Event targets](<data-structures.md#Event_targets>) • [Country tag aliases](<data-structures.md#Country_tag_aliases>) • [Variables](<data-structures.md#Variables>) • [Arrays](<data-structures.md#Arrays>)
- **Scripting**: [Achievements](<achievement-modding.md>) • [AI](<ai-modding.md>) • [AI focuses](<ai-focuses.md>) • [Autonomous states](<autonomy-state-modding.md>) • [Balances of power](<balance-of-power-modding.md>) • [Bookmarks/Scenarios](<bookmark-modding.md>) • [Game rules](<bookmark-modding.md#Game_rules>) • [Buildings](<building-modding.md>) • [Characters and traits](<character-modding.md>) • [Cosmetic tags](<cosmetic-tag-modding.md>) • [Countries](<country-creation.md>) • [Divisions](<division-modding.md>) • [Decisions](<decision-modding.md>) • [Doctrines](<doctrine-modding.md>) • [Equipment](<equipment-modding.md>) • [Events](<event-modding.md>) • [Factions](<faction-modding.md>) • [Ideas](<idea-modding.md>) • [Ideologies](<ideology-modding.md>) • [Military industrial organizations](<military-industrial-organization-modding.md>) • [National focuses](<national-focus-modding.md>) • [Resources](<resources-modding.md>) • [Scripted GUI](<scripted-gui-modding.md>) • [Technologies and doctrines](<technology-modding.md>) • [Units](<unit-modding.md>)
- **Map**: [Map](<map-modding.md>) • [States](<state-modding.md>) • [Supply areas](<supply-areas-modding.md>) • [Strategic regions](<strategic-region-modding.md>)
- **Graphical**: [Interface](<interface-modding.md>) • [Graphical assets](<graphical-asset-modding.md>) • [Entities](<entity-modding.md>) • [Posteffects](<posteffect-modding.md>) • [Particles](<particle-modding.md>) • [Fonts](<font-modding.md>)
- **Cosmetic**: [Portraits](<portrait-modding.md>) • [Namelists](<namelist-modding.md>) • [Music](<music-modding.md>)
- **Other**: [Console commands](<console-commands.md>) • [Troubleshooting](<troubleshooting.md>) • [Mod structure](<mod-structure.md>) • [Mods](<mods.md>) • [Nudger](<nudger.md>)
- **Kit pages (not on the wiki)**: [Collection modding](<collection-modding.md>) • [Game rule modding](<game-rule-modding.md>) • [Intelligence operation modding](<intelligence-operation-modding.md>) • [Map mode modding](<map-mode-modding.md>) • [Occupation and resistance modding](<occupation-and-resistance-modding.md>) • [Peace conference modding](<peace-conference-modding.md>) • [Raid modding](<raid-modding.md>) • [Script constant modding](<script-constant-modding.md>) • [Special project modding](<special-project-modding.md>)
