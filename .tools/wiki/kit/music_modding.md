# Music modding

<!-- kit:begin id="review" build="1.19.4.1" checked="2026-11-01" revision="88012" sources="music/ interface/music_station_base.gui interface/music_station_classic.gui interface/musicplayer.gui localisation/english/music_l_english.yml common/defines/00_defines.lua documentation/effects_documentation.md" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Checked against: `music/` and the `music/` folders of every DLC (13 `.asset` files, 124 songs, 13 song assignment `.txt` files with 120 assigned songs), `interface/music_station_base.gui`, `interface/music_station_classic.gui`, `interface/musicplayer.gui`, `integrated_dlc/dlc023_man_the_guns/interface/mtg_music.gui`, `localisation/english/music_l_english.yml`, and `play_song` in `documentation/effects_documentation.md`.
Kit blocks added: song definition census (volume range, subfolders, localisation), what the `chance` block can contain in vanilla, the two vanilla stations and their interface windows, the script side (`play_song`).
Gaps left: no game file defines the play modes, so "Weighted Shuffle" and how a chance of 0 behaves stay as the wiki states them; the 63 character limit on song names is not shown by vanilla.
**1.19.4.1 re-check (2026-11-01).** 6 tagged statements depended on files the update changed (`common/national_focus/`, `common/defines/00_defines.lua`) or on the DLC folder the manifest diff cannot compare (its `music/` folder), and all of them were re-measured on the installed files. Nothing moved: still 13 `.asset` files, 124 songs, 13 assignment files with 120 assignments and 4 unassigned songs, and `MUSIC_PLAYER_RECENTLY_PLAYED_SIZE = 10`. Every other statement cites files that are byte-identical in 1.19.4.1 (Steam depot manifest diff).
<!-- kit:end id="review" -->

<!-- kit:begin id="music-song-notes" at="section:song-definition" -->
Facts from the 124 vanilla `music` blocks. All rows: [vanilla-confirmed 1.19.4.1] `music/music.asset`, `music/hoi2/hoi2_music.asset`, `music/hoi3/`, and the `music/` folder of each DLC.

- Every block sets exactly `name`, `file` and `volume`.
- `volume` runs from 0.4 to 1.5. The most common values are 0.8 (32 songs) and 0.65 (28). Eight songs are above 1.0 (1.1 three times, 1.2, 1.4 twice, 1.45, 1.5), so `volume` is not capped at 1.
- `file` is relative to the folder of the `.asset` file and may name a subfolder: `file = "China/stillness_over_the_north.ogg"` in the No Compromise, No Surrender DLC.
- The longest song name in vanilla has 34 characters, so the page's limit of 63 is never reached (`sanctuary_of_hope_acoustic_version`). [vanilla-confirmed 1.19.4.1] `music/`, DLC `music/` folders. The limit itself is not shown by any game file. [unverified]
- The name doubles as the localisation key, written without a version number: ` general_peace_1: "Hearts of Men"` in `localisation/english/music_l_english.yml`.
- Vanilla `.asset` file names vary (`music.asset`, `music_ncns.asset`, `hoi2_music.asset`); no name is required.
<!-- kit:end id="music-song-notes" -->

<!-- kit:begin id="music-chance-notes" at="section:assigning-to-a-station" -->
What the vanilla assignment files show about `music_station` and `chance`. All rows: [vanilla-confirmed 1.19.4.1] `music/_songs.txt`, `music/hoi2/hoi2_soundtrack.txt`, `music/hoi3/hoi3_soundtrack.txt`, and the `*_songs.txt` of each DLC.

- Two stations have songs: `"base_music"` (11 files: the base game and 10 DLC folders) and `"classic"` (the Hearts of Iron 2 and 3 soundtracks). `music_station = "..."` is the first line of the file.
- Of 120 `music` assignments, 35 have no `chance` block at all, so `chance` is optional.
- When present, `chance` holds only `modifier` blocks (22 assignments), `factor` and `modifier` together (35), `base` and `modifier` together (18), `factor` alone (7) or `base` alone (3). `add`, which the page lists, is not used by vanilla.
- A `modifier` with no trigger and only `factor = 0.5` is valid and applies to every case: this is how `maintheme` is written. Triggers seen inside `modifier` include `has_war`, `has_government`, `original_tag`, `is_in_faction_with`, `has_war_with`, `any_enemy_country`, `has_idea_with_trait`, `has_completed_focus`, `NOT` and `OR`; they run in country scope. [vanilla-confirmed 1.19.4.1] `music/_songs.txt`, DLC `music/*_songs.txt` for the trigger names and the bare `maintheme` modifier. The scope is an inference from the triggers used and is untested. [unverified]
- 4 songs are defined but assigned to no station: `resistance_spanish`, `resistance_french`, `resistance_fascist`, `resistance_spying`. [vanilla-confirmed 1.19.4.1] `dlc/dlc028_la_resistance/music/`

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

<!-- kit:begin id="music-station-notes" at="section:radio-stations" -->
What 1.19.3 ships for stations. `interface/music_station_base.gui` defines `base_music_faceplate` and `base_music_stations_entry`; `interface/music_station_classic.gui` defines `classic_faceplate` and `classic_stations_entry`. The entry window holds one `checkBoxType` named `select_station_button` whose `quadTextureSprite` is the album art (`GFX_classic_album_art`). Both names follow the page's `<MUSIC STATION>_faceplate` and `<MUSIC STATION>_stations_entry` pattern. [vanilla-confirmed 1.19.3] `interface/music_station_base.gui`, `interface/music_station_classic.gui`

The player window `interface/musicplayer.gui` has the grids that these windows fill: a `faceplate` slot, `default_stations_window` with `stations_grid`, and a `tracks_grid`. [vanilla-confirmed 1.19.3] `interface/musicplayer.gui`

The Man the Guns DLC has `man_the_guns_faceplate` and `man_the_guns_stations_entry` in `integrated_dlc/dlc023_man_the_guns/interface/mtg_music.gui`, but its `mtg_songs.txt` assigns songs to `base_music`, so no song uses that station. [vanilla-confirmed 1.19.3] `integrated_dlc/dlc023_man_the_guns/`

The define `MUSIC_PLAYER_RECENTLY_PLAYED_SIZE = 10` is the size of the list of recently played songs that the player uses to avoid repeats. [vanilla-confirmed 1.19.4.1] `common/defines/00_defines.lua`
<!-- kit:end id="music-station-notes" -->

<!-- kit:begin id="music-script-effects" at="bottom" -->
Script can play a song from a decision, focus or event. `play_song = "<song name>"` plays a song from the song database in any scope, and `scoped_play_song` plays it only for the player of the current scope. [docs] `documentation/effects_documentation.md`

Vanilla uses `play_song = "comintern_war_1"` in `common/national_focus/soviet.txt` and `play_song = "peace_in_our_time"` in `common/scripted_effects/zzz_play_speech_effects.txt`. [vanilla-confirmed 1.19.4.1] `common/national_focus/soviet.txt`

`play_song = "bella_ciao"` in `common/national_focus/italy.txt` names a song that no `music` block in the game files defines. [vanilla-confirmed 1.19.4.1] `common/national_focus/italy.txt`, `music/`, and no `.asset` file anywhere in the install defines it (`localisation/english/bba_music_l_english.yml` does have the key). Define every name you use. An undefined song name is logged and nothing worse: `play_song` with a name no `music` block defines wrote `Song doesnt exist: <name>` to `error.log`, the rest of the effect block ran, and the game ran 48 more hours with no crash. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, effect run from the console, error.log and game.log read. One call was tried.
<!-- kit:end id="music-script-effects" -->
