# Table of contents

- [Song definition](#song-definition)
- [Assigning to a station](#assigning-to-a-station)
- [Radio stations](#radio-stations)


---

Music files are stored in the \*.ogg format within the /Hearts of Iron IV/music/ folder or one of its subfolders.

The [Music Mod Creation Tool](https://runite-drill.github.io/music-mod-creation-tool/) is a quick and easy-to-use modding tool that will generate all the files described below to add music and a radio station to the game.

## Song definition

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

## Assigning to a station

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
*chance* defines the chance for a song to be picked if the playmode is set to Weighted Shuffle. The allowed arguments are `factor`, for multiplying the chance, `add`, for adding to the chance, and `base`, replacing the chance entirely. `modifier = {}` allows the argument to modify the chance only be executed if all of the triggers within are met.

## Radio stations

A radio station is defined as an [user interface](<Interface modding - Hearts of Iron 4 Wiki.md>) file, /Hearts of Iron IV/interface/\*.gui. The contents of the file are required to be the following, with `<MUSIC STATION>` being replaced with the music station's name:

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

The name is assigned by using its ID as a [localisation](<Localisation - Hearts of Iron 4 Wiki.md>) key within /Hearts of Iron IV/localisation/<language>/\*\_l\_<language>.yml:  `<MUSIC STATION>:0 "Music station's name"`.  
The album cover is assigned a sprite as the quadTextureSprite within select\_station\_button. A sprite must be defined within /Hearts of Iron IV/interface/\*.gfx as the following:

```text
	spriteType = {
		name = "<SPRITE>"
		texturefile = "gfx//interface//topbar//musicplayer//<FILE NAME>.dds"
		noOfFrames = 2
	}
```

The \*.dds file must be split horizontally into 2 sprites: when it is unselected, and when it is selected.

**[Modding](<Modding - Hearts of Iron 4 Wiki.md>)**
