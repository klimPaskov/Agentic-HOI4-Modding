# Country creation

<!-- kit:begin id="review" build="1.19.4.1" checked="2026-11-01" revision="71937" sources="common/country_tags/ common/countries/ common/graphicalculturetype.txt history/countries/ history/units/ gfx/flags/ common/defines/00_graphics.lua common/factions/ localisation/english/ localisation/languages.yml documentation/effects_documentation.md" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Checked against: all 439 tags in `common/country_tags/`, the 364 history files in `history/countries/`, the OOB selection pattern, the `common/countries/` files, and the TGA headers of every file in `gfx/flags/` (2203 standard, 2203 medium and 2226 small flags).
Kit blocks added: tag counts and a warning that `SCO` already exists in vanilla, country file and colour facts, the vanilla OOB-by-DLC pattern with counts, effect corrections (`set_autonomy`, `create_faction`, `set_stability`, `set_politics`), flag size, header and naming facts, the language list, and the placeholder status of the example character.
The "obsolete" marker is `obsolete = yes` inside `create_equipment_variant`, a valid key; no section is stale.
Gaps left: the dynamic-tag counts the wiki gives for medium and small flags (about 10 and 20) and the date-block rule ("strictly later") are in no game file and were not tested.
**1.19.4.1 re-check (2026-11-01).** 14 tagged statements depended on files the update changed (`history/countries/`, `history/units/`, `gfx/flags/`, `common/defines/00_graphics.lua` and `localisation/english/`), and all of them were re-measured. The flag folders grew (2,207 standard, 2,222 medium and 2,318 small files, and the small folder now has all four group flags for 302 tags), `set_politics` key counts are 419 to 424, and history files use no `name` in `set_politics`; the order of battle counts are unchanged. Every other statement cites files that are byte-identical in 1.19.4.1 (Steam depot manifest diff).
<!-- kit:end id="review" -->

<!-- kit:begin id="country-tag-counts" at="section:tag" -->
Tags in 1.19.3. All rows: [vanilla-confirmed 1.19.3] `common/country_tags/00_countries.txt`, `common/country_tags/zz_dynamic_countries.txt`.

- 439 tags, and every one has exactly 3 characters: 364 static tags in `00_countries.txt` and 75 dynamic tags (`D01` to `D75`) in `zz_dynamic_countries.txt`, after a line `dynamic_tags = yes`. No static tag contains a digit or a lowercase letter; only the dynamic ones carry digits.
- Each static tag has exactly one file in `history/countries/` (364 of 364); dynamic tags have none.
- Tags share country files: 439 tags use 404 distinct files in `common/countries/`. 35 of the 75 dynamic tags reuse the file of an earlier one (for example `D16 = "countries/D01.txt"`, `D21 = "countries/D01.txt"`) and 40 have their own file. That is the "many tags, one file" case the page describes.
- `SCO` is already defined in vanilla (`SCO = "countries/Scotland.txt"`, with `history/countries/SCO - Scotland.txt`). The wiki uses `SCO` as an example for a new country; in a mod pick a tag that vanilla does not use, or you override Scotland instead of adding a country.
- The trigger-like names in the table above (`NOT`, `AND`, `TAG`, `OOB`, `LOG`, `NUM`, `RED`) are not used as tags by vanilla. [vanilla-confirmed 1.19.3] `common/country_tags/`
<!-- kit:end id="country-tag-counts" -->

<!-- kit:begin id="country-file-facts" at="section:country-file" -->
What the 440 vanilla country files in `common/countries/` contain. All rows: [vanilla-confirmed 1.19.3] `common/countries/*.txt`, `common/graphicalculturetype.txt`.

- Keys: `graphical_culture`, `graphical_culture_2d` and `color`. The 75 files `D01.txt` to `D75.txt` have only `color`. Vanilla values for `graphical_culture`: `asian_gfx` (88), `african_gfx` (64), `western_european_gfx` (62), `eastern_european_gfx` (57), `southamerican_gfx` (38), `middle_eastern_gfx` (32), `commonwealth_gfx` (22), `sami_gfx` (1). `common/graphicalculturetype.txt` lists 16 names (the `_gfx` set plus the `_2d` set). One country file (`Guangxi.txt`) uses `asian_european_gfx`, which that list does not contain.
- `color` is written without a colour model in 314 country files (`color = { 106 119 89 }`) and with one in 126 (`color = rgb { 232 232 0 }`). The model requirement the wiki gives is about `colors.txt` entries: 302 of its 306 entries use `rgb` and 4 use `HSV` or `hsv` (both spellings are accepted).
- `common/countries/colors.txt` entries are `TAG = { color = rgb { ... } color_ui = rgb { ... } }`. `common/countries/cosmetic.txt` has the same shape for cosmetic tags (for example `RAJ_UK`).
- The two modifiers behind the footnote live in `NGraphics` in `common/defines/00_graphics.lua` (not in `00_defines.lua`): `COUNTRY_COLOR_SATURATION_MODIFIER = 0.6` and `COUNTRY_COLOR_BRIGHTNESS_MODIFIER = 0.8`.
<!-- kit:end id="country-file-facts" -->

<!-- kit:begin id="country-history-oob-pattern" at="section:order-of-battle" -->
How vanilla history files choose an order of battle. All rows: [vanilla-confirmed 1.19.4.1] `history/countries/*.txt` (364 files) and `history/units/` (609 files).

- Plain countries write `oob = "ALB_1936"` once. Countries whose army depends on a DLC use `set_oob`, `set_naval_oob` and `set_air_oob` inside a DLC check. Key counts (active lines, any indentation): `set_air_oob` 188, `oob` 165, `set_naval_oob` 128, `set_oob` 104, `load_oob` 4 (in 3 files), and `OOB` in capitals 2, so vanilla itself writes the key in both cases.
- A DLC check selects the file with a name suffix. A text scan (nearest `has_dlc` within 8 lines above the line) puts about 156 of the `set_air_oob` lines under "By Blood Alone" (files `<TAG>_1936_air_bba` and `_air_legacy`), about 110 of the `set_naval_oob` lines under "Man the Guns" (`_naval_mtg` and `_naval_legacy`), and about 50 of the `set_oob` lines under "No Step Back" (`_nsb`). `set_oob` is also used with "No Compromise, No Surrender" (about 21), "Gotterdammerung" (about 8), "La Resistance", "Trial of Allegiance", "By Blood Alone" and "Graveyard of Empires". In `history/units/` there are 31 files with `_nsb`, 57 with `_naval_mtg`, 62 with `_naval_legacy`, 89 with `_air_bba` and 89 with `_air_legacy`.
- The vanilla form of the if/else, with `IF` and `ELSE` in capitals and the `ELSE` nested inside (the wiki's note that `else` only works nested):

```text
oob = "ARG_1936"
IF = {
	limit = { has_dlc = "Man the Guns" }
	set_naval_oob = "ARG_1936_naval_mtg"
	ELSE = {
		set_naval_oob = "ARG_1936_naval_legacy"
	}
}
```

- 149 of the 364 history files name no order of battle at all (countries that only appear later or have no army), so the "buildings break without an OOB" rule matters for countries that exist at the start. 5 of them (`DON`, `KUB`, `KUM`, `KUR`, `RUT`) have a file with their prefix in `history/units/`. 64 of the 609 unit files are never named in a country history; events load such files with `load_oob` (for example `events/USA.txt` loads `ENG_destroyers_for_bases`). [vanilla-confirmed 1.19.4.1] `history/countries/`, `history/units/`

`set_oob`, `set_naval_oob` and `set_air_oob` replace the OOB registered under the same key (no key, `naval`, `air`). `load_oob` loads the file at once. [docs] `documentation/effects_documentation.md`
<!-- kit:end id="country-history-oob-pattern" -->

<!-- kit:begin id="country-history-effect-corrections" at="section:effects" -->
Differences between the page and the 1.19.3 documentation or vanilla history files. Tags per row.

| Page says | 1.19.3 |
| --- | --- |
| `set_stability = 0.7` (scale 0 to 1) | Vanilla history files use fractions: the 364 files never go above 0.9. The effect documentation's own example says `set_stability = 80`, which does not match vanilla use. [vanilla-confirmed 1.19.4.1] `history/countries/`. [docs] `documentation/effects_documentation.md` |
| `set_autonomy = { target = SCO autonomous_state = autonomy_integrated_puppet }` | The documentation names the key `autonomy_state` and adds `freedom_level`, `end_wars`, `end_civil_wars`. Vanilla history: `autonomous_state` 23 times, `autonomy_state` once, `target` 24, `freedom_level` 16. [docs] `documentation/effects_documentation.md`. [vanilla-confirmed 1.19.4.1] `history/countries/` |
| `create_faction = key` | The documentation marks `create_faction` as deprecated and recommends `create_faction_from_template`. Vanilla history uses `create_faction_from_template = faction_template_axis` and similar in 5 files (`CHI`, `ENG`, `GER`, `SOV`, `USA`) and no plain `create_faction`. [docs] `documentation/effects_documentation.md`. [vanilla-confirmed 1.19.4.1] `history/countries/` |
| `set_politics = { ruling_party last_election election_frequency elections_allowed }` | The keys are right (419 to 424 uses each). [vanilla-confirmed 1.19.4.1] `history/countries/`. The documentation lists two more keys and leaves out two: see the note below the table. |
| `set_popularities` "if it doesn't add up to 100 it fails" | The documentation says the values must add up to exactly 100, and shows decimals (`54.5` and `45.5`). 415 vanilla uses. [docs] `documentation/effects_documentation.md`. [vanilla-confirmed 1.19.4.1] `history/countries/` |
| `set_technology = { ... }` | also accepts `popup = no` inside the block. [docs] `documentation/effects_documentation.md` |
| `create_equipment_variant` keys | the documentation also has `allow_without_tech`, `parent_version`, `mark_older_equipment_obsolete` and `role_icon_index`; `obsolete = yes` is a valid key (default no). [docs] `documentation/effects_documentation.md` |
| `capital = 121` as a history key | present in 363 of 364 vanilla files (not in `PRC - ComChina.txt`). The effect `set_capital = { state = N remember_old_capital = no }` also exists in country scope. [vanilla-confirmed 1.19.4.1] `history/countries/`. [docs] `documentation/effects_documentation.md` |

Notes on rows of the table above:

- `set_politics`: the documentation also lists `long_name` and `name` to rename the party, and does not list `last_election` or `election_frequency`. [docs] `documentation/effects_documentation.md`. No vanilla history file uses `long_name` or `name`, but `set_politics` blocks in events, focuses and scripted effects do. [vanilla-confirmed 1.19.4.1] `history/countries/`, `events/`, `common/national_focus/`, `common/scripted_effects/`

`recruit_character`, `add_ideas`, `set_research_slots` (values 2, 3, 4, 5 in vanilla; 3 most often) and `add_to_tech_sharing_group` (8 uses) are used as the page says. [vanilla-confirmed 1.19.4.1] `history/countries/`
<!-- kit:end id="country-history-effect-corrections" -->

<!-- kit:begin id="country-date-block-rule" at="section:date-dependent-history" -->
The "strictly later" rule is wrong for the exact start moment. In a test on state history with the start at 1936.1.1.12, a block dated `1936.1.1` ran, the one dated `1936.1.2` did not, and blocks dated `1936.1.1.12` (the start moment) and `1936.1.1.11` both ran, so a block runs when its date is the start date or earlier. The test used state history (`add_core_of` in state 64), not a country file. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, new games, script probe read in game.log. See [State modding](state_modding.md#history).
<!-- kit:end id="country-date-block-rule" -->

<!-- kit:begin id="country-flag-facts" at="section:flag" -->
What the vanilla flag files look like, from the TGA headers. All rows: [vanilla-confirmed 1.19.4.1] `gfx/flags/`, `gfx/flags/medium/`, `gfx/flags/small/`.

| Folder | Files | Size | Headers |
| --- | --- | --- | --- |
| `gfx/flags/` | 2207 | 82 x 52 (one file, `SPB_kingdom_neutrality.tga`, is 82 x 55) | 2191 uncompressed 32-bit (5 with the top-left origin bit set); 9 uncompressed 24-bit; 1 uncompressed 16-bit; 6 run-length encoded (type 10, two of them 24-bit) |
| `gfx/flags/medium/` | 2222 | 41 x 26 (one file, `SPB_kingdom_neutrality.tga`, is 41 x 28) | 2206 uncompressed 32-bit (219 with the top-left origin bit set); 7 uncompressed 24-bit; 9 run-length encoded |
| `gfx/flags/small/` | 2318 | 10 x 7 (one file, `FRA_VICHY_democratic.tga`, is 10 x 6) | 2308 uncompressed 32-bit; 7 uncompressed 24-bit; 3 run-length encoded |

So the "no RLE" and "32-bit only" rules on this page are not met by every vanilla file. The engine does not read all of them: it refuses at least one run-length encoded vanilla flag, `KOM_democratic.tga` (a 32 bit type 10 file), with the message in the next paragraph. [vanilla-confirmed 1.19.4.1] `gfx/flags/KOM_democratic.tga` (TGA header).

Two new files that break the rules were tried as `GER_fascism.tga` in `gfx/flags/`. A 24 bit uncompressed file (82 x 52, type 2) loaded with a warning: "Error loading flag for country GER : Ideology fascism : Path gfx/flags/ : Warning slow to read format - Consider using 32bpp instead of 24bpp". A 32 bit run-length encoded file (type 10) is not just slow. The loader refused it with "Error loading country flag overlay: gfx/flags/GER_fascism.tga : Unsupported format. Expected 32bpp, uncompressed, no color palette" and reported the flag as "File not found". The same two lines appear in every run for the vanilla `KOM_democratic.tga`. A flipped image and the slow start were not checked: no screenshot was taken, and the menu times were not a controlled comparison. Only the large folder `gfx/flags/` was changed. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, one-mod launch, error.log read.

The sizes match the defines `COUNTRY_FLAG_TEX_WIDTH = 82`, `COUNTRY_FLAG_TEX_HEIGHT = 52`, the `_MEDIUM_` pair 41 x 26 and the `_SMALL_` pair 10 x 7 in `NGraphics` (`common/defines/00_graphics.lua`), which also has `COUNTRY_FLAG_TEX_MAX_SIZE = 256`, `COUNTRY_FLAG_MEDIUM_TEX_MAX_SIZE = 1024` and `COUNTRY_FLAG_SMALL_TEX_MAX_SIZE = 256`, each with the comment "Tweak dependly on amount of countries". [vanilla-confirmed 1.19.4.1] `common/defines/00_graphics.lua`. These are probably the sizes of the textures the flags are packed into, which would explain the wiki's remark about many tags; that reading is [unverified].

Naming in vanilla: the four ideology groups `neutrality`, `democratic`, `communism` and `fascism` are the suffixes (`ABK_communism.tga`, `ABK_democratic.tga`). Of the 364 static tags, 302 have all four group flags in `gfx/flags/`, 77 have a plain `TAG.tga` (8 of those have no ideology flag), and the 75 dynamic tags have no flag file. The medium folder has 302 tags with all four files too, and so has the small folder. Cosmetic tags and other named countries use the same pattern with a longer stem (`gojjam_democratic.tga`; 354 stems in the standard folder do not start with a vanilla tag), and tags can have extra variants (`PHI_asean_tag_communism.tga`; 453 files of that kind). The three folders do not hold the same names: 112 small flags and 16 medium flags have no standard flag of the same name, and one standard flag (`PLACEHOLDER.tga`) has no medium or small flag. [vanilla-confirmed 1.19.4.1] `gfx/flags/`
<!-- kit:end id="country-flag-facts" -->

<!-- kit:begin id="country-name-languages" at="section:name" -->
The language list is out of date. `localisation/languages.yml` in 1.19.3 names ten: `l_english`, `l_braz_por`, `l_french`, `l_german`, `l_polish`, `l_russian`, `l_spanish`, `l_japanese`, `l_simp_chinese` and `l_korean`, and the folders `localisation/korean/` and `localisation/simp_chinese/` exist next to the others. The page's "limited to" list misses Korean and Simplified Chinese. [vanilla-confirmed 1.19.3] `localisation/languages.yml`, `localisation/` folder listing

Vanilla writes country names in `localisation/english/countries_l_english.yml` (for example `GER_fascism`, `GER_fascism_DEF`, `GER_fascism_ADJ`) and the plain tag name `GER: "Germany"`, and party names as `GER_communism_party` and `GER_communism_party_long`. Subject name templates exist in `countries_cosmetic_l_english.yml` (`INS_subject: "$OVERLORDADJ$ East Indies"`). [vanilla-confirmed 1.19.4.1] `localisation/english/`
<!-- kit:end id="country-name-languages" -->

<!-- kit:begin id="country-character-placeholders" at="section:starting-characters" -->
`SCO_ronald_mcdonald`, the trait `scary_clown` and the sprite `GFX_SCO_ronald_mcdonald` in this example are placeholders. None of them exists in vanilla (no match in `common/`, `interface/` or `localisation/`), so a mod has to define the character, the trait and the sprite itself; `recruit_character = SCO_ronald_mcdonald` fails when the character does not exist. [vanilla-confirmed 1.19.4.1] Search of the installed game. With an unknown character id, `recruit_character` logs "recruit_character: Unknown character" to `error.log` (no id is printed after the text), and the rest of the effect block still runs. The engine also warns "recruit_character should only happen in game/history files in order to be executed only at game start". [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, effect run from the console and `error.log` read. The ideology `socialism` used in the example is a type defined in `common/ideologies/00_ideologies.txt`. [vanilla-confirmed 1.19.3] `common/ideologies/00_ideologies.txt`
<!-- kit:end id="country-character-placeholders" -->
