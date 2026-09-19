# Music modding

*Offline snapshot of the Hearts of Iron IV Wiki page "Music modding", captured 2026-09-19.*

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

*name* is the song's ID, as well as its localisation key for name assignment within a [Localisation](<Localisation - Hearts of Iron 4 Wiki.md>) file as  `song_name:0 "Song's Name"`. It cannot contain more than 63 characters.
*file* is the song's filename, including the \*.ogg extension.
*volume* allows to adjust the volume of the \*.ogg file without editing it.

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
*chance* defines the chance for a song to be picked if the playmode is set to Weighted Shuffle. The allowed arguments are `factor`, for multiplying the chance, `add`, for adding to the chance, and `base`, replacing the chance entirely. `modifier = {}` allows the argument to modify the chance only be executed if all of the [triggers](<Triggers - Hearts of Iron 4 Wiki.md>) within are met.

## Radio stations <a id="Radio_stations"></a>

A radio station is defined as an [user interface](<Interface modding - Hearts of Iron 4 Wiki.md>) file, `/Hearts of Iron IV/interface/*.gui`. The contents of the file are required to be the following, with `<MUSIC STATION>` being replaced with the music station's name:

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

The name is assigned by using its ID as a [localisation](<Localisation - Hearts of Iron 4 Wiki.md>) key within `/Hearts of Iron IV/localisation/<language>/*_l_<language>.yml`:  `<MUSIC STATION>:0 "Music station's name"`.
The album cover is assigned a sprite as the quadTextureSprite within select_station_button. A sprite must be defined within `/Hearts of Iron IV/interface/*.gfx` as the following:

```text
	spriteType = {
		name = "<SPRITE>"
		texturefile = "gfx//interface//topbar//musicplayer//<FILE NAME>.dds"
		noOfFrames = 2
	}
```

The \*.dds file must be split horizontally into 2 sprites: when it is unselected, and when it is selected.

---

## Navigation

**[Modding](<Modding - Hearts of Iron 4 Wiki.md>)**

- **Documentation**: [Effects](<Effects - Hearts of Iron 4 Wiki.md>) • [Triggers](<Triggers - Hearts of Iron 4 Wiki.md>) • [Defines](<Defines - Hearts of Iron 4 Wiki.md>) • [Modifiers](<Modifiers - Hearts of Iron 4 Wiki.md>) • [List of modifiers](<List of modifiers - Hearts of Iron 4 Wiki.md>) • [Scopes](<Scopes - Hearts of Iron 4 Wiki.md>) • [Localisation](<Localisation - Hearts of Iron 4 Wiki.md>) • [On actions](<On actions - Hearts of Iron 4 Wiki.md>) • [Data structures](<Data structures - Hearts of Iron 4 Wiki.md>) • [Flags](<Data structures - Hearts of Iron 4 Wiki.md#Flags>) • [Event targets](<Data structures - Hearts of Iron 4 Wiki.md#Event_targets>) • [Country tag aliases](<Data structures - Hearts of Iron 4 Wiki.md#Country_tag_aliases>) • [Variables](<Data structures - Hearts of Iron 4 Wiki.md#Variables>) • [Arrays](<Data structures - Hearts of Iron 4 Wiki.md#Arrays>)
- **Scripting**: [Achievements](<Achievement modding - Hearts of Iron 4 Wiki.md>) • [AI](<AI modding - Hearts of Iron 4 Wiki.md>) • [AI focuses](<AI focuses - Hearts of Iron 4 Wiki.md>) • [Autonomous states](<Autonomy state modding - Hearts of Iron 4 Wiki.md>) • [Balances of power](<Balance of power modding - Hearts of Iron 4 Wiki.md>) • [Bookmarks/Scenarios](<Bookmark modding - Hearts of Iron 4 Wiki.md>) • [Game rules](<Bookmark modding - Hearts of Iron 4 Wiki.md#Game_rules>) • [Buildings](<Building modding - Hearts of Iron 4 Wiki.md>) • [Characters and traits](<Character modding - Hearts of Iron 4 Wiki.md>) • [Cosmetic tags](<Cosmetic tag modding - Hearts of Iron 4 Wiki.md>) • [Countries](<Country creation - Hearts of Iron 4 Wiki.md>) • [Divisions](<Division modding - Hearts of Iron 4 Wiki.md>) • [Decisions](<Decision modding - Hearts of Iron 4 Wiki.md>) • [Doctrines](<Doctrine modding - Hearts of Iron 4 Wiki.md>) • [Equipment](<Equipment modding - Hearts of Iron 4 Wiki.md>) • [Events](<Event modding - Hearts of Iron 4 Wiki.md>) • [Factions](<Faction modding - Hearts of Iron 4 Wiki.md>) • [Ideas](<Idea modding - Hearts of Iron 4 Wiki.md>) • [Ideologies](<Ideology modding - Hearts of Iron 4 Wiki.md>) • [Military industrial organizations](<Military industrial organization modding - Hearts of Iron 4 Wiki.md>) • [National focuses](<National focus modding - Hearts of Iron 4 Wiki.md>) • [Resources](<Resources modding - Hearts of Iron 4 Wiki.md>) • [Scripted GUI](<Scripted GUI modding - Hearts of Iron 4 Wiki.md>) • [Technologies and doctrines](<Technology modding - Hearts of Iron 4 Wiki.md>) • [Units](<Unit modding - Hearts of Iron 4 Wiki.md>)
- **Map**: [Map](<Map modding - Hearts of Iron 4 Wiki.md>) • [States](<State modding - Hearts of Iron 4 Wiki.md>) • [Supply areas](<Supply areas modding - Hearts of Iron 4 Wiki.md>) • [Strategic regions](<Strategic region modding - Hearts of Iron 4 Wiki.md>)
- **Graphical**: [Interface](<Interface modding - Hearts of Iron 4 Wiki.md>) • [Graphical assets](<Graphical asset modding - Hearts of Iron 4 Wiki.md>) • [Entities](<Entity modding - Hearts of Iron 4 Wiki.md>) • [Posteffects](<Posteffect modding - Hearts of Iron 4 Wiki.md>) • [Particles](<Particle modding - Hearts of Iron 4 Wiki.md>) • [Fonts](<Font modding - Hearts of Iron 4 Wiki.md>)
- **Cosmetic**: [Portraits](<Portrait modding - Hearts of Iron 4 Wiki.md>) • [Namelists](<Namelist modding - Hearts of Iron 4 Wiki.md>) • [Sound](<Sound modding - Hearts of Iron 4 Wiki.md>)
- **Other**: [Console commands](<Console commands - Hearts of Iron 4 Wiki.md>) • [Troubleshooting](<Troubleshooting - Hearts of Iron 4 Wiki.md>) • [Mod structure](<Mod structure - Hearts of Iron 4 Wiki.md>) • [Mods](<Mods - Hearts of Iron 4 Wiki.md>) • [Nudger](<Nudger - Hearts of Iron 4 Wiki.md>)
