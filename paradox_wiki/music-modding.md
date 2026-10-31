# Music modding

*Offline snapshot of the Hearts of Iron IV Wiki page "Music modding", revision 88012, captured 2026-10-31. Wiki text by the wiki's contributors under CC BY-SA 3.0 (see LICENSE.txt); kit blocks are local additions under the same license.*

<!-- kit:begin id="review" at="top" build="1.19.3.0" checked="2026-10-31" revision="88012" sources="music/ interface/music_station_base.gui interface/music_station_classic.gui interface/musicplayer.gui localisation/english/music_l_english.yml common/defines/00_defines.lua documentation/effects_documentation.md" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Checked against: `music/` and the `music/` folders of every DLC (13 `.asset` files, 124 songs, 13 song assignment `.txt` files with 120 assigned songs), `interface/music_station_base.gui`, `interface/music_station_classic.gui`, `interface/musicplayer.gui`, `integrated_dlc/dlc023_man_the_guns/interface/mtg_music.gui`, `localisation/english/music_l_english.yml`, and `play_song` in `documentation/effects_documentation.md`.
Kit blocks added: song definition census (volume range, subfolders, localisation), what the `chance` block can contain in vanilla, the two vanilla stations and their interface windows, the script side (`play_song`).
Gaps left: no game file defines the play modes, so "Weighted Shuffle" and how a chance of 0 behaves stay as the wiki states them; the 63 character limit on song names is not shown by vanilla.
<!-- kit:end id="review" -->

## Table of contents

- [Song definition](#Song_definition)
- [Assigning to a station](#Assigning_to_a_station)
- [Radio stations](#Radio_stations)

---

Music files are stored in the \*.ogg format within the `/Hearts of Iron IV/music/` folder or one of its subfolders.

The Music Mod Creation Tool is a quick and easy-to-use modding tool that will generate all the files described below to add music and a radio station to the game.

## Song definition <a id="Song_definition"></a>

Songs are defined within files of the \*.asset format, located in the same folder as the \*.ogg files. A definition is formatted as following:

```text
music = {
    name = "song_name"
    file = "song_file.ogg"
    volume = 0.65
}
```

*name* is the song's ID, as well as its localisation key for name assignment within a [Localisation](<localisation.md>) file as  `song_name:0 "Song's Name"`. It cannot contain more than 63 characters.
*file* is the song's filename, including the \*.ogg extension.
*volume* allows to adjust the volume of the \*.ogg file without editing it.

<!-- kit:begin id="music-song-notes" at="section:Song_definition" -->
**Kit note** Facts from the 124 vanilla `music` blocks. All rows: [vanilla-confirmed 1.19.3] `music/music.asset`, `music/hoi2/hoi2_music.asset`, `music/hoi3/`, and the `music/` folder of each DLC.

- Every block sets exactly `name`, `file` and `volume`.
- `volume` runs from 0.4 to 1.5. The most common values are 0.8 (32 songs) and 0.65 (28). Eight songs are above 1.0 (1.1 three times, 1.2, 1.4 twice, 1.45, 1.5), so `volume` is not capped at 1.
- `file` is relative to the folder of the `.asset` file and may name a subfolder: `file = "China/stillness_over_the_north.ogg"` in the No Compromise, No Surrender DLC.
- The longest song name in vanilla has 34 characters, so the page's limit of 63 is never reached. The limit itself is not shown by any game file. [unverified] `music/`
- The name doubles as the localisation key, written without a version number: ` general_peace_1: "Hearts of Men"` in `localisation/english/music_l_english.yml`.
- Vanilla `.asset` file names vary (`music.asset`, `music_ncns.asset`, `hoi2_music.asset`); no name is required.
<!-- kit:end id="music-song-notes" -->

## Assigning to a station <a id="Assigning_to_a_station"></a>

In order to work properly, songs must be assigned to a station. The assignments are stored in \*.txt files, within the same folder as the \*.asset and \*.ogg files.
An assignment file, before defining any songs, must be assigned to a station. Multiple files can be assigned to the same station. This is done with the following line of code:

```text
music_station = "station_name"
```

A typical assignment of a song is formatted accordingly:

```text
music = {
    song = "song_name"
    chance = {
        base = 1
        modifier = {
            factor = 0
            has_war = no
        }
    }
}
```

*song* accepts the ID of the song, defined as its name within the \*.asset file.
*chance* defines the chance for a song to be picked if the playmode is set to Weighted Shuffle. The allowed arguments are `factor`, for multiplying the chance, `add`, for adding to the chance, and `base`, replacing the chance entirely. `modifier = {}` allows the argument to modify the chance only be executed if all of the [triggers](<triggers.md>) within are met.

<!-- kit:begin id="music-chance-notes" at="section:Assigning_to_a_station" -->
**Kit note** What the vanilla assignment files show about `music_station` and `chance`. All rows: [vanilla-confirmed 1.19.3] `music/_songs.txt`, `music/hoi2/hoi2_soundtrack.txt`, `music/hoi3/hoi3_soundtrack.txt`, and the `*_songs.txt` of each DLC.

- Two stations have songs: `"base_music"` (11 files: the base game and 10 DLC folders) and `"classic"` (the Hearts of Iron 2 and 3 soundtracks). `music_station = "..."` is the first line of the file.
- Of 120 `music` assignments, 35 have no `chance` block at all, so `chance` is optional.
- When present, `chance` holds only `modifier` blocks (22 assignments), `factor` and `modifier` together (35), `base` and `modifier` together (18), `factor` alone (7) or `base` alone (3). `add`, which the page lists, is not used by vanilla.
- A `modifier` with no trigger and only `factor = 0.5` is valid and applies to every case: this is how `maintheme` is written. Triggers seen inside `modifier` include `has_war`, `has_government`, `original_tag`, `is_in_faction_with`, `has_war_with`, `any_enemy_country`, `has_idea_with_trait`, `has_completed_focus`, `NOT` and `OR`; they run in country scope. The scope is an inference from the triggers used. [unverified] `music/_songs.txt`
- 4 songs are defined but assigned to no station: `resistance_spanish`, `resistance_french`, `resistance_fascist`, `resistance_spying`. [vanilla-confirmed 1.19.3] `dlc/dlc028_la_resistance/music/`

```text
music_station = "base_music"

music = {
	song = "general_peace_1"
	chance = {
		modifier = {
			factor = 1
			has_war = no
		}
	}
}
```

Vanilla assignment, one of several peace songs. [vanilla-confirmed 1.19.3] `music/_songs.txt`
<!-- kit:end id="music-chance-notes" -->

## Radio stations <a id="Radio_stations"></a>

A radio station is defined as an [user interface](<interface-modding.md>) file, `/Hearts of Iron IV/interface/*.gui`. The contents of the file are required to be the following, with `<MUSIC STATION>` being replaced with the music station's name:

```text
guiTypes = {
	containerWindowType = {
		name = "<MUSIC STATION>_faceplate"
		position = { x =0 y=0 }
		size = { width = 590 height = 46 }

		iconType ={
			name ="musicplayer_header_bg"
			spriteType = "GFX_musicplayer_header_bg"
			position = { x= 0 y = 0 }
			alwaystransparent = yes
		}

		instantTextboxType = {
			name = "track_name"
			position = { x = 72 y = 20 }
			font = "hoi_20b"
			text = "Roger Pontare - Nar vindarna viskar mitt namn"
			maxWidth = 450
			maxHeight = 25
			format = center
		}

		instantTextboxType = {
			name = "track_elapsed"
			position = { x = 124 y = 30 }
			font = "hoi_18b"
			text = "00:00"
			maxWidth = 50
			maxHeight = 25
			format = center
		}

		instantTextboxType = {
			name = "track_duration"
			position = { x = 420 y = 30 }
			font = "hoi_18b"
			text = "02:58"
			maxWidth = 50
			maxHeight = 25
			format = center
		}

		buttonType = {
			name = "prev_button"
			position = { x = 220 y = 20 }
			quadTextureSprite ="GFX_musicplayer_previous_button"
			buttonFont = "Main_14_black"
			Orientation = "LOWER_LEFT"
			clicksound = click_close
			pdx_tooltip = "MUSICPLAYER_PREV"
		}

		buttonType = {
			name = "play_button"
			position = { x = 263 y = 20 }
			quadTextureSprite ="GFX_musicplayer_play_pause_button"
			buttonFont = "Main_14_black"
			Orientation = "LOWER_LEFT"
			clicksound = click_close
		}

		buttonType = {
			name = "next_button"
			position = { x = 336 y = 20 }
			quadTextureSprite ="GFX_musicplayer_next_button"
			buttonFont = "Main_14_black"
			Orientation = "LOWER_LEFT"
			clicksound = click_close
			pdx_tooltip = "MUSICPLAYER_NEXT"
		}

		extendedScrollbarType = {
			name = "volume_slider"
			position = { x = 100 y = 45}
			size = { width = 75 height = 18 }
			tileSize = { width = 12 height = 12}
			maxValue =100
			minValue =0
			stepSize =1
			startValue = 50
			horizontal = yes
			orientation = lower_left
			origo = lower_left
			setTrackFrameOnChange = yes

			slider = {
				name = "Slider"
				quadTextureSprite = "GFX_scroll_drager"
				position = { x=0 y = 1 }
				pdx_tooltip = "MUSICPLAYER_ADJUST_VOL"
			}

			track = {
				name = "Track"
				quadTextureSprite = "GFX_volume_track"
				position = { x=0 y = 3 }
				alwaystransparent = yes
				pdx_tooltip = "MUSICPLAYER_ADJUST_VOL"
			}
		}

		buttonType = {
			name = "shuffle_button"
			position = { x = 425 y = 20 }
			quadTextureSprite ="GFX_toggle_shuffle_buttons"
			buttonFont = "Main_14_black"
			Orientation = "LOWER_LEFT"
			clicksound = click_close
		}
	}

	containerWindowType={
		name = "<MUSIC STATION>_stations_entry"
		size = { width = 162 height = 130 }

		checkBoxType = {
			name = "select_station_button"
			position = { x = 0 y = 0 }
			quadTextureSprite = "<SPRITE>"
			clicksound = decisions_ui_button
		}
	}
}
```

The name is assigned by using its ID as a [localisation](<localisation.md>) key within `/Hearts of Iron IV/localisation/<language>/*_l_<language>.yml`:  `<MUSIC STATION>:0 "Music station's name"`.
The album cover is assigned a sprite as the quadTextureSprite within select_station_button. A sprite must be defined within `/Hearts of Iron IV/interface/*.gfx` as the following:

```text
	spriteType = {
		name = "<SPRITE>"
		texturefile = "gfx//interface//topbar//musicplayer//<FILE NAME>.dds"
		noOfFrames = 2
	}
```

The \*.dds file must be split horizontally into 2 sprites: when it is unselected, and when it is selected.

<!-- kit:begin id="music-station-notes" at="section:Radio_stations" -->
**Kit note** What 1.19.3 ships for stations. `interface/music_station_base.gui` defines `base_music_faceplate` and `base_music_stations_entry`; `interface/music_station_classic.gui` defines `classic_faceplate` and `classic_stations_entry`. The entry window holds one `checkBoxType` named `select_station_button` whose `quadTextureSprite` is the album art (`GFX_classic_album_art`). Both names follow the page's `<MUSIC STATION>_faceplate` and `<MUSIC STATION>_stations_entry` pattern. [vanilla-confirmed 1.19.3] `interface/music_station_base.gui`, `interface/music_station_classic.gui`

The player window `interface/musicplayer.gui` has the grids that these windows fill: a `faceplate` slot, `default_stations_window` with `stations_grid`, and a `tracks_grid`. [vanilla-confirmed 1.19.3] `interface/musicplayer.gui`

The Man the Guns DLC has `man_the_guns_faceplate` and `man_the_guns_stations_entry` in `integrated_dlc/dlc023_man_the_guns/interface/mtg_music.gui`, but its `mtg_songs.txt` assigns songs to `base_music`, so no song uses that station. [vanilla-confirmed 1.19.3] `integrated_dlc/dlc023_man_the_guns/`

The define `MUSIC_PLAYER_RECENTLY_PLAYED_SIZE = 10` is the size of the list of recently played songs that the player uses to avoid repeats. [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua`
<!-- kit:end id="music-station-notes" -->

<!-- kit:begin id="music-script-effects" at="bottom" -->
**Kit addition** Script can play a song from a decision, focus or event. `play_song = "<song name>"` plays a song from the song database in any scope, and `scoped_play_song` plays it only for the player of the current scope. [docs] `documentation/effects_documentation.md`

Vanilla uses `play_song = "comintern_war_1"` in `common/national_focus/soviet.txt` and `play_song = "peace_in_our_time"` in `common/scripted_effects/zzz_play_speech_effects.txt`. [vanilla-confirmed 1.19.3] `common/national_focus/soviet.txt`

`play_song = "bella_ciao"` in `common/national_focus/italy.txt` names a song that no `music` block in the game files defines. [vanilla-confirmed 1.19.3] `common/national_focus/italy.txt`, `music/`. What the game does with an undefined song name is not shown; define every name you use. [unverified] `common/national_focus/italy.txt`
<!-- kit:end id="music-script-effects" -->

---

## Navigation

**[Modding](<modding.md>)**

- **Documentation**: [Effects](<effects.md>) • [Triggers](<triggers.md>) • [Defines](<defines.md>) • [Modifiers](<modifiers.md>) • [List of modifiers](<list-of-modifiers.md>) • [Scopes](<scopes.md>) • [Localisation](<localisation.md>) • [On actions](<on-actions.md>) • [Data structures](<data-structures.md>) • [Flags](<data-structures.md#Flags>) • [Event targets](<data-structures.md#Event_targets>) • [Country tag aliases](<data-structures.md#Country_tag_aliases>) • [Variables](<data-structures.md#Variables>) • [Arrays](<data-structures.md#Arrays>)
- **Scripting**: [Achievements](<achievement-modding.md>) • [AI](<ai-modding.md>) • [AI focuses](<ai-focuses.md>) • [Autonomous states](<autonomy-state-modding.md>) • [Balances of power](<balance-of-power-modding.md>) • [Bookmarks/Scenarios](<bookmark-modding.md>) • [Game rules](<bookmark-modding.md#Game_rules>) • [Buildings](<building-modding.md>) • [Characters and traits](<character-modding.md>) • [Cosmetic tags](<cosmetic-tag-modding.md>) • [Countries](<country-creation.md>) • [Divisions](<division-modding.md>) • [Decisions](<decision-modding.md>) • [Doctrines](<doctrine-modding.md>) • [Equipment](<equipment-modding.md>) • [Events](<event-modding.md>) • [Factions](<faction-modding.md>) • [Ideas](<idea-modding.md>) • [Ideologies](<ideology-modding.md>) • [Military industrial organizations](<military-industrial-organization-modding.md>) • [National focuses](<national-focus-modding.md>) • [Resources](<resources-modding.md>) • [Scripted GUI](<scripted-gui-modding.md>) • [Technologies and doctrines](<technology-modding.md>) • [Units](<unit-modding.md>)
- **Map**: [Map](<map-modding.md>) • [States](<state-modding.md>) • [Supply areas](<supply-areas-modding.md>) • [Strategic regions](<strategic-region-modding.md>)
- **Graphical**: [Interface](<interface-modding.md>) • [Graphical assets](<graphical-asset-modding.md>) • [Entities](<entity-modding.md>) • [Posteffects](<posteffect-modding.md>) • [Particles](<particle-modding.md>) • [Fonts](<font-modding.md>)
- **Cosmetic**: [Portraits](<portrait-modding.md>) • [Namelists](<namelist-modding.md>) • [Sound](<sound-modding.md>)
- **Other**: [Console commands](<console-commands.md>) • [Troubleshooting](<troubleshooting.md>) • [Mod structure](<mod-structure.md>) • [Mods](<mods.md>) • [Nudger](<nudger.md>)
- **Kit pages (not on the wiki)**: [Collection modding](<collection-modding.md>) • [Defines additions](<defines-additions.md>) • [Game rule modding](<game-rule-modding.md>) • [Intelligence operation modding](<intelligence-operation-modding.md>) • [Map mode modding](<map-mode-modding.md>) • [Occupation and resistance modding](<occupation-and-resistance-modding.md>) • [Peace conference modding](<peace-conference-modding.md>) • [Raid modding](<raid-modding.md>) • [Script constant modding](<script-constant-modding.md>) • [Special project modding](<special-project-modding.md>)
