# Bookmark modding

*Offline snapshot of the Hearts of Iron IV Wiki page "Bookmark modding", revision 81580, captured 2026-10-31. Wiki text by the wiki's contributors under CC BY-SA 3.0 (see LICENSE.txt); kit blocks are local additions under the same license.*

<!-- kit:begin id="review" at="top" build="1.19.4.1" checked="2026-11-01" revision="81580" sources="common/bookmarks/ common/game_rules/00_game_rules.txt common/difficulty_settings/00_difficulty.txt common/modifiers/00_static_modifiers.txt common/defines/00_defines.lua interface/frontendgamesetupview.gui interface/frontendgamesetupview.gfx documentation/effects_documentation.md" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Checked against: both vanilla bookmark files, the game rule and difficulty setting files, the setup screen GUI and the START_DATE defines.
- Kit blocks added: `bookmark-1193-keys` (bookmark and country-entry keys the wiki lacks: `filters`, `version`, `required_dlc`, `assume_not_played_if_missing_data`, `override_leader_portrait`, six commented layout switches), `bookmark-effect-weather`, `bookmark-date-defines`, `bookmark-ui-limits`, `bookmark-difficulty-vanilla`, `bookmark-game-rules-1193`.
- Errors found: the focus card limit is 4, not 3, in the 1.19.3 GUI; the stated default date `2.1.1.1` is not confirmed; the example rule group names are examples only.
- Gaps left: what `version`, `assume_not_played_if_missing_data` and the `new_content` filter do at runtime is not documented anywhere in the game files.
**1.19.4.1 re-check (2026-11-01).** 8 tagged statements depended on files the update changed (`common/bookmarks/blitzkrieg.txt`, `common/defines/00_defines.lua` and the setup screen localisation), and all of them were re-measured. Nothing moved: still 152 country entries, the same `version` values, 3 focuses on every entry, the seeds 12345 and 22345, and the START_DATE defines. The statement that vanilla entries list 3 ideas is corrected to 114 of 152, since some entries list fewer or more. Every other statement cites files that are byte-identical in 1.19.4.1 (Steam depot manifest diff).
<!-- kit:end id="review" -->

## Table of contents

- [Attributes](#Attributes)
- [File example](#File_example)
- [User interface](#User_interface)
- [Notes](#Notes)
- [Game rules](#Game_rules)
  - [Difficulty settings](#Difficulty_settings)
  - [Game rules](#Game_rules_2)
- [References and notes](#References_and_notes)

---

A bookmark is a scenario chosen by the player at the start of the game, allowing changing the interesting countries recommended to the player and the starting date.

The `/Hearts of Iron IV/common/bookmarks/*.txt` files are used for defining the selctable bookmarks.

Each file consists of a `bookmarks = { ... }` block that contains each bookmark, each as a separate `bookmark = { ... }` definition. In particular, a file with two bookmarks will be structured as such:

```text
bookmarks = {
    bookmark = {
         <...>
    }
    bookmark = {
         <...>
    }
}
```

## Attributes <a id="Attributes"></a>

These attributes go into a `bookmark = { ... }` block. Each of the arguments of a bookmark is theoretically optional.

- `name = loc_key` decides on the [localisation](<localisation.md>) key used for the name of the bookmark used during the start date selection. Defaults to showing nothing.
- `desc = loc_key` decides on the [localisation](<localisation.md>) key used for the description of the bookmark used during the start date selection. Defaults to showing nothing.
- `date = 1936.1.1.12` decides on the date which notes when the game should start, written in the YYYY.MM.DD.HH format. Defaults to 2.1.1.1, and no earlier date can be used.
- `picture = GFX_select_date_1936` decides on the [spriteType](<graphical_asset_modding.md>) definition used for the start date, defined in any `/Hearts of Iron IV/interface/*.gfx` file. Defaults to being pure black.
- `default = yes` is used to mark the bookmark as default, resulting in the game pre-loading its conditions during the main menu and making the player choose it by default. Defaults to false, only one bookmark should have this.
- `default_country = GER` decides on the country tag that should be chosen by the player by default. The country must be among the interesting countries.
- `effect = { ... }` is an [effect](<effects.md>) block that will be executed when the bookmark is selected. This is done after the history folder but before the player can select a country. In particular, [randomize_weather](<effects.md>) should be used to ensure that the weather works properly, but this can also be used to ensure that the bookmark has different conditions from another one on the same date.
- `TAG = { ... }` is used to create an entry for a country among the interesting countries. Using the tag of `---` will be taken as the "other countries" menu, allowing the player to enter the country selection without any selected. The same country may have several definitions. In particular, these are used as arguments inside:
  - `history = loc_key` decides on the [localisation](<localisation.md>) key used for the description shown to the player when this country is chosen.
  - `ideology = neutrality` is the ideology group that the country starts with. This is used to determine the country leader, the ideology icon, the name of the country, and the flag.
  - `minor = yes` is used to mark the country as minor, making it appear in the lower menu with small flags instead of the top one where the leader is shown. **This will also requires the country to start with a national focus tree that doesn't have `default = yes` to show up in the selection**, used in the base game to make the interesting country selection depend on the DLCs.
  - `available = { has_dlc = "Poland: United and Ready" }` is a [trigger](<triggers.md>) block that must be fulfilled for the country to show up in the selection. This is typically only used for DLC checks, as nothing else may reasonably change before country selection.
  - `ideas = { TAG_idea_1 TAG_idea_2 TAG_idea_3 }` is the list of national spirits that should be shown to the player when the country is selected. This doesn't modify or depend on the actual spirits that the country will have on startup, which is typically handled in [country history](<country_creation.md>) or [state history](<state_modding.md#History>). By default, limited to 3 entries.[1]
  - `focuses = { TAG_focus_1 TAG_focus_2 TAG_focus_3 }` is the list of national focuses that should be shown to the player when the country is selected. By default, limited to 3 entries.[2]

<!-- kit:begin id="bookmark-1193-keys" at="section:Attributes" -->
**Kit addition** Keys of the 1.19.3 bookmark format that the list above does not name.

Bookmark-level keys. Row 1: [vanilla-confirmed 1.19.4.1] `common/bookmarks/the_gathering_storm.txt` and `blitzkrieg.txt` (both set `filters = { new_content continent }`). Rows 2 to 8 exist only in comments of `the_gathering_storm.txt`: no uncommented use of any of the seven tokens in `common/`, `events/`, `history/` or `interface/`. [vanilla-confirmed 1.19.4.1] Each token is also a string in `hoi4.exe`, and the defaults are the comment's and untested [unverified].

| Key | Value | Meaning |
| --- | --- | --- |
| `filters` | list of tokens | Filter buttons above the country list. Vanilla uses `new_content` and `continent`. The vanilla comment says the list "can also contain `label`" |
| `label` (country entry) | `label = { label_1 label_2 }` | Labels are gathered from all entries and become filter buttons, only when `label` is in `filters` |
| `label_order` | `{ label_1 label_2 }` | Forces the button order. The comment says a warning is logged for a label that countries use but the list lacks |
| `sort_unplayed_first` | yes/no, default yes | Countries with unplayed content are listed first |
| `include_majors_in_minor_list` | yes/no, default yes | When a filter is active, majors also show in the small list |
| `apply_filter_to_majors` | yes/no, default no | When yes, the major row obeys the filter too |
| `apply_filter_to_other_country` | yes/no, default no | By default the `"---"` entry is always shown; when yes it obeys the filter |
| `scrollable_country_list` | yes/no, default no | Scrolls the small-flag list with a vertical scrollbar instead of the overflow dropdown |

Country-entry keys beyond the wiki list. Counts are from both vanilla files together. [vanilla-confirmed 1.19.4.1] `common/bookmarks/` for the keys and counts (152 entries: 85 and 67 uncommented `version` lines); what the engine does with `version` and `assume_not_played_if_missing_data` is [unverified].

| Key | Seen | Meaning |
| --- | --- | --- |
| `version = base_game` | on every one of the 152 entries | Name of the content version of this entry. The 12 values seen are in the note below the table. Probably what the `new_content` filter and the unplayed sorting key on [unverified] |
| `required_dlc = { "Name" }` | 46 and 31 entries | Entry exists only with every listed DLC. The block takes several names (`{ "Gotterdammerung" "No Compromise, No Surrender" }`, 2 entries). The value is a block here, unlike `required_dlc = "Name"` in game rules |
| `assume_not_played_if_missing_data = yes` | 6 and 5 entries | Set mostly on entries of newer DLC: 8 `thunder_at_our_gates` and 1 `peace_for_our_time`, plus 2 `base_game` entries (the Australia fallbacks shown without Thunder at Our Gates) [vanilla-confirmed 1.19.4.1]. Name suggests the entry counts as unplayed when the profile has no data for it [unverified] |
| `override_leader_portrait = JAP_emperor_hirohito` | 3 entries, all Japan | Character id from `common/characters/JAP.txt` whose portrait is shown instead of the leader's |

Notes on rows of the table above:

- `version`: Values seen: `base_game`, `no_compromise_no_surrender`, `trial_of_allegiance`, `graveyard_of_empires`, `gotterdammerung`, `thunder_at_our_gates`, `arms_against_tyranny`, `by_blood_alone`, `la_resistance`, `man_the_guns`, `no_step_back`, `peace_for_our_time`.

Base-plus-DLC pair, the vanilla pattern for a country that changes with a DLC:

```text
"FRA"={
    history = "FRA_GATHERING_STORM_DESC"
    ideology = democratic
    version = base_game
    available = { NOT = { has_dlc = "La Resistance" } }
    ideas = { FRA_victors_of_wwi FRA_disjointed_government FRA_protected_by_the_maginot_line }
    focuses = { FRA_form_the_popular_front FRA_revive_the_national_bloc FRA_france_leads }
}
"FRA"={
    history = "FRA_GATHERING_STORM_DESC"
    ideology = democratic
    version = la_resistance
    required_dlc = { "La Resistance" }
    ideas = { FRA_victors_of_wwi FRA_disjointed_government FRA_protected_by_the_maginot_line }
    focuses = { FRA_invite_communist_ministers FRA_utilize_the_leagues FRA_je_suis_la_deluge }
}
```

Example: [vanilla-confirmed 1.19.3] `common/bookmarks/the_gathering_storm.txt` (FRA entries, ideas and focuses shortened to one line). Vanilla `ideology` values: `neutrality` (76), `democratic` (45), `fascism` (21), `communism` (10). [vanilla-confirmed 1.19.4.1] `common/bookmarks/`.
<!-- kit:end id="bookmark-1193-keys" -->

<!-- kit:begin id="bookmark-effect-weather" at="section:Attributes" -->
**Kit note** Both vanilla bookmarks end with an `effect` block whose only live line is `randomize_weather = <seed>`, followed by the vanilla comment "Obligatory in every bookmark". Seeds are 12345 in `blitzkrieg.txt` and 22345 in `the_gathering_storm.txt`; give each bookmark of a mod its own seed. [vanilla-confirmed 1.19.4.1] `common/bookmarks/blitzkrieg.txt`, `the_gathering_storm.txt`.

`randomize_weather` is documented as a one-line effect usable in any scope and takes no documented parameters. [docs] `documentation/effects_documentation.md`. The commented line `#123 = { rain_light = yes }` in both files is not a documented effect (`rain_light` is a weather type defined in `common/weather.txt`), so do not copy it as a working example. [vanilla-confirmed 1.19.4.1] `common/weather.txt`; no `rain_light` effect in `documentation/effects_documentation.md`.
<!-- kit:end id="bookmark-effect-weather" -->

## File example <a id="File_example"></a>

```text
bookmarks = {
    bookmark = {    # Relatively empty bookmark
        name = example_bookmark_1
        desc = example_bookmark_1_desc
        date = 1936.1.1.12
        picture = GFX_select_date_1936

        "---" = {
            history = OTHER_SCENARIO1_DESC
        }
        effect = {
            randomize_weather = 1228
        }
    }
    bookmark = {    # A bookmark with a few countries.
        name = example_bookmark_2
        desc = example_bookmark_2_desc
        date = 1936.1.1.12
        picture = GFX_select_date_1936

        default = yes
        default_country = BHR

        BHR = {
            history = BHR_SCENARIO2_DESC
            ideology = neutrality

            focuses = { BHR_focus_1 }
            ideas = {
                BHR_idea_1
                BHR_idea_2
            }
        }
        QAT = {
            history = QAT_SCENARIO2_DESC
            ideology = democratic
            minor = yes

            available = { NOT = { has_dlc = "Arms Against Tyranny" } }
        }
        QAT = {
            history = QAT_SCENARIO2_DESC
            ideology = democratic
            minor = yes

            focuses = {
                QAT_focus_1
                QAT_focus_2
            }
            available = { has_dlc = "Arms Against Tyranny" }
        }
        "---" = {
            history = OTHER_SCENARIO2_DESC
        }
        effect = {
            randomize_weather = 45768
            321 = { transfer_state_to = QAT }  # Despite being on the same date as the previous bookmark, it will have different starting history
        }
    }
}
```

## User interface <a id="User_interface"></a>

*See also: [Interface modding](<interface_modding.md>)*

**General sprite overview**

For loading GFX, the game uses the sprite system. Sprites are code definitions that attach a name to an image file, as well as optionally adding additional information, such as animation, the amount of frames, the way that the image will be loaded, and so on. This means **placing an image into the gfx folder isn't enough for it to work**, a sprite has to use that image file as well.

Sprites are defined in any `/Hearts of Iron IV/interface/*.gfx` file (this is separate from `gfx/interface/`), opened with a text editor. To create a new .gfx file, a text file can be created and renamed to change the extension (on Windows, the Windows Explorer needs to show the extensions, which it doesn't by default). In particular, sprites are defined within a `spriteTypes = { ... }` block, as to separate from fonts and map arrows also defined in that folder, while the simplest sprite with the least mandatory properties is a `spriteType = { ... }`. The simplest sprite definition looks like the following:

```text
spriteTypes = {
    spriteType = {
        name = GFX_first_sprite                         # In some cases, beginning with GFX_ is mandatory for it to work.
        texturefile = gfx/interface/folder/filename.dds # The folder and filename don't matter, as long as they are correct
    }                                                   # Only the forward slash '/' (can be doubled as '//') can be used to separate folders.
    spriteType = {                                      # The image doesn't have to be .dds, as .tga and .png are acceptable.
        name = GFX_second_sprite
        texturefile = gfx/interface/folder2/filename2.dds
        noOfFrames = 2 # Splits the image into 2 halves, which may be switched between dynamically in GUI
    }
}
```

In this case, this creates a sprite with the name of `GFX_first_sprite` and attaches the `/Hearts of Iron IV/gfx/interface/folder/filename.dds` image to it, and a second sprite similarly. The second sprite will be split into 2 frames: this is decided by having the left half of the image as the first frame and the right half as the second frame (more frames would further split the image horizontally). This doesn't make the sprite animated, just turns on the option to switch between the two halves as needed. `GFX_second_sprite:1` serves as a reference to the first frame, and GUI can be set up to change the shown frame depending on context, such as with radio stations.
In order to add animation, a [frameAnimatedSpriteType](<graphical_asset_modding.md#frameAnimatedSpriteType>) is used.

**It's never mandatory to copy a base game file to change a sprite**. If there are duplicate definitions of a sprite with the same name in different files, the game will prioritise the one that would be [evaluated later, based on the filename](<modding.md#Loading_files>), and the older sprite will be ignored in entirety. This can be ensured by beginning the replacement file's name with a symbol late in the ASCII character table. Typically the lowercase letter 'z' is used for this purpose. For example, to change the amount of frames in `GFX_idea_traits_strip` to 10, it is possible to define a sprite with that name with 10 frames in the mod's `modname/interface/zz_replace.gfx` file instead of copying over the base game file.
Since most .gfx files define integral parts of the user interface, copying them over can lead to the mod's loaded files missing sprites upon a major game update, which would appear in-game as the default image, which is the error dog by default. As to ease the burden of needing to check the interface files, it's best to never copy over .gfx files, unless more additions would be actively harmful to the mod, such as with `interface/subuniticons.gfx`

In the base game, the images used to represent a bookmark (e.g. `GFX_select_date_1936`) have the size of 180x104 pixels, with there being a gap in the bottom to prevent overlap with the frame. This gap can be created by selecting and deleting a circle with a radius of ~35 pixels and the centre approximately 90 pixels to the right from the left edge and 130 pixels below the top edge.

By default, the selection of bookmarks and interesting countries within bookmarks is defined in the `/Hearts of Iron IV/interface/frontendgamesetupview.gui` file. In particular, these changes are common to make:

- The `bookmarks_grid` gridbox is used for positioning the bookmarks for the player to select, and the `bookmark_entry` container windows are the individual elements of that gridbox. If the amount of bookmarks doesn't match the ones in the base game, this is necessary to edit:
  - By default, having one bookmark in the loaded files skips the bookmark selection entirely. This can be circumvented by having two bookmarks, but hiding the second one from view. Adding `max_slots_horizontal = 1` to the gridbox will prevent more than 1 from showing. The gridbox may be edited in the opposite case of more than 2 bookmarks as well, by increasing the amount of possible rows.
  - If the amount of bookmark differs from the default, the size of each bookmark may be changed. This would require changing the coordinate positions of elements inside of each bookmark, as well as changing the image used for the frame and/or the font size.
- There are 3 `countries_grid` gridboxes in the file used for positioning the interesting countries. The one inside of the `countries` container window is used for major countries, while the ones inside `countries_medium` and `countries_mini` are for minor countries, changing from one to the other after a 9th minor country is added.
  - There is no way to make either gridbox not follow a grid pattern. However, it is instead possible to create dummy country entries and hide them from the final product by placing [iconTypes](<interface_modding.md#iconType>) inside of the `gamesetup_interesting_countries_window` container window after the gridbox, set to use an image that covers up the minor interesting country with the background.

<!-- kit:begin id="bookmark-ui-limits" at="section:User_interface" -->
**Kit correction** The card limits in `interface/frontendgamesetupview.gui` of 1.19.3: `ideas_grid` has `max_slots = { x = 3 y = 1 }` and `focus_grid` has `max_slots = { x = 4 y = 1 }`, so a country card shows up to 3 ideas and up to 4 focuses (the wiki says 3 for both). Vanilla entries list 3 focuses each (all 152) and usually 3 ideas (114 of 152, the rest list 0 to 2, 4 or 5). [vanilla-confirmed 1.19.4.1] `interface/frontendgamesetupview.gui`, `common/bookmarks/`.

Other grids: `bookmarks_grid` has `slotsize` 260 wide and `max_slots_vertical = 1`; `countries_medium` holds 8 slots per row; `countries_mini` holds 23 per row and 2 rows; a new `filters` element (`OverlappingElementsBoxType`) holds the filter buttons, and the `country_filter` window defines one such button. [vanilla-confirmed 1.19.3] `interface/frontendgamesetupview.gui`.

Bookmark pictures: `GFX_select_date_1936` and `GFX_select_date_1939` are defined in `interface/frontendgamesetupview.gfx` and both textures (`gfx/interface/select_date_1936.dds`, `select_date_1939.dds`) are 180 by 104 pixels, matching the wiki. [vanilla-confirmed 1.19.3] `interface/frontendgamesetupview.gfx`, DDS header.
<!-- kit:end id="bookmark-ui-limits" -->

## Notes <a id="Notes"></a>

- If there is only one bookmark defined within the loaded files, the game will skip the bookmark selection for the player and go straight into the bookmark selection. From that menu, going back to the main menu, either with the interface button or by using hte hotkey, is impossible. This can be avoided by still having a second bookmark but hiding it from the player, as in [§ User interface](#User_interface).
- The start date cannot be placed before the year 2. If the earliest start date is changed from default, it is necessary to edit the [Defines](<defines.md>) in an [override file](<defines.md#Overrides>). In particular,[NGame.START_DATE](<defines.md>), [NGame.END_DATE](<defines.md>), and [NDiplomacy.TENSION_TIME_SCALE_START_DATE](<defines.md>) are the ones may need changing.
- In order for the in-game state to change between the start dates, it is possible to place date blocks in [country history](<country_creation.md>) or [state history](<state_modding.md#History>), which will be executed if and only if the start date is strictly later than the specified date. For example, this state history block will make it be owned by ABC on the game's start, but by DEF if the start date is later than 1937.1.1:

```text
history = {
    owner = ABC
    1937.1.1 = {
        owner = DEF
    }
}
```

- If there should be a difference between bookmarks with the same date, then the `effect` attribute can be used.
- The bookmarks are positioned in the order of their start dates. If two bookmarks have the same date, then they are positioned in the order [in which they are evaluated](<modding.md#Loading_files>). The interesting countries are positioned in the order in which they are written in the bookmark.

<!-- kit:begin id="bookmark-date-defines" at="section:Notes" -->
**Kit correction** The wiki's "defaults to 2.1.1.1" for `date` is not confirmed. What 1.19.4.1 shows: `NDefines.NGame.START_DATE = "1936.1.1.12"`, `END_DATE = "1949.1.1.1"` and `NDefines.NDiplomacy.TENSION_TIME_SCALE_START_DATE = "1936.1.1.12"`. The bookmark dates are `1936.1.1.12` (`the_gathering_storm.txt`) and `1939.8.14.12` (`blitzkrieg.txt`). [vanilla-confirmed 1.19.4.1] `common/defines/00_defines.lua`, `common/bookmarks/`. A mod that starts earlier than 1936.1.1.12 should override all three defines, as the wiki says; whether an earlier date also needs other defines is [unverified].

The history-date rule above (a block in `history/` applies when the start date is later than the block's date) is the wiki's statement and is not re-checked here. [unverified]
<!-- kit:end id="bookmark-date-defines" -->

## Game rules <a id="Game_rules"></a>

The game rules allow the player to change the gameplay conditions that will apply after the country selection has been finished. There are two types of database elements that are grouped under "Game rules" for the player:

- Difficulty settings, in `/Hearts of Iron IV/common/difficulty_settings/*.txt` files. These are used to apply a modifier to a country or a group of countries and present themselves as a slider.
- Game rules, in `/Hearts of Iron IV/common/game_rules/*.txt` files. These are used to present a dropdown menu to the player out of a few options.

**Either one having no valid entries will result in the player being unable to open the menu for editing the game rules.**

### Difficulty settings <a id="Difficulty_settings"></a>

Difficulty settings will apply a [static modifier](<modifiers.md>) to a country or a group of countries based on the slider that the player chooses, defined within `/Hearts of Iron IV/common/difficulty_settings/*.txt` files. This is unrelated to the difficulty itself that the player chooses.`[a]`

The files are structured with a unified `difficulty_settings = { ... }` entry, with each difficulty setting being a separate `difficulty_setting = { ... }` inside of it. In particular, these attributes exist:

- `key = custom_diff_strong_tag` is the [localisation](<localisation.md>) key used as the name of the setting in the game rules menu.
- `modifier = diff_strong_ai_generic` is the [static modifier](<modifiers.md>) that gets used for the setting.
- `countries = { ABC DEF GHI }` is a list of country tags that should have the modifier applied.
- `multiplier = 2.0` is how much the modifier should be multiplied to on the maximum scale. This scales linearly depending on which value the player chose out of 5 total positions the slider can take, from 0 to the number in the attribute. For example, if the static modifier contains `stability_factor = 0.4` and the multiplier is set to 2.0, each position of the slider from left to right will respectively give the country 0%, 20%, 40%, 60%, and 80% ![Stability](media/country_creation_1d4220f262__img10.png)Stability.

The sliders are positioned in the order [in which they are evaluated](<modding.md#Loading_files>). In particular, the files in the folder are sorted using the ASCII character order, then the sliders are added in the order that they are defined in the files.

Example file structure:

```text
difficulty_settings = {
    difficulty_setting = {
        key = "custom_diff_strong_bhr"
        modifier = diff_strong_ai_generic
        countries = { BHR }
        multiplier = 2.0
    }
    difficulty_setting = {
        key = "custom_diff_weak_arab"
        modifier = diff_weak_ai_generic # Doesn't exist in the base game
        countries = { BHR QAT OMA YEM SAU }
        multiplier = 4.0
    }
}
```

<!-- kit:begin id="bookmark-difficulty-vanilla" at="section:Difficulty_settings" -->
**Kit note** Vanilla `common/difficulty_settings/00_difficulty.txt` holds 8 settings, all with `multiplier = 2.0` and the static modifier `diff_strong_ai_generic`: GER, ITA, SOV, FRA, ENG, USA, JAP (`{ JAP MEN MAN }`) and CHI (`{ CHI PRC }`). Keys are `custom_diff_strong_<tag>` and the loc key `custom_diff_strong_ger` exists in `localisation/english/frontend_l_english.yml`. [vanilla-confirmed 1.19.4.1] `common/difficulty_settings/00_difficulty.txt`, `localisation/english/frontend_l_english.yml`.

`diff_weak_ai_generic` in the wiki example does not exist; `diff_strong_ai_generic` is the only generic modifier. The per-difficulty modifiers are `diff_very_easy_player` to `diff_very_hard_player` and `diff_very_easy_ai` to `diff_very_hard_ai`, as footnote a says. [vanilla-confirmed 1.19.3] `common/modifiers/00_static_modifiers.txt` (11 `diff_*` blocks).
<!-- kit:end id="bookmark-difficulty-vanilla" -->

### Game rules <a id="Game_rules_2"></a>

Game rules apply allow the player to choose an option among the selection of a few choices before the game's start, defined in `/Hearts of Iron IV/common/game_rules/*.txt` files. For any new game rules, this will **only** change how the [has_game_rule trigger](<triggers.md>) evaluates, which can be used in [conditional statements](<effects.md>) to give a different result based on the game rule.

There are these three general categories of game rules that exist in the base game:

- One-time change in-game: This usually changes some aspect of the world immediately after the game starts, using [the on_startup on action](<on_actions.md>). For example, the "nation fragmentation" game rules fall into this category.
- Mechanical change: This changes how some mechanic works by continuously checking for the game rule being set in-game. For example, the game rule to hide obsolete national focus branches does so by including a check for the game rule being set in the [allow_branch of the national focuses to hide](<national_focus_modding.md>). These two subsets are particularly notable:

- Diplomatic actions: these game rules modify the prerequisites necessary to execute a diplomatic action. These are usually handled with [diplomacy scripted triggers](<triggers.md>), though occassionally there is distinction that's purely hard-coded (Usually this is the difference between the "Limited" and "Free" options).
- AI behaviour: these game rules are checked for within [AI strategy plans](<ai_modding.md>) and enable one to choose a random focus path. The "random" option is typically handled by setting a [country flag](<data_structures.md>) using [random_list](<effects.md>) within the [the on_startup on action](<on_actions.md>).

- Entirely hard-coded game rules: Some game rules' values are checked directly in the game's binary and thus are unmoddable for the most part with the exception of deleting them or some options of them. For example, the game rule that changes the maximum level of land forts falls under this category.

Each game rule is defined as a separate root-level block within the `common/game_rules/` file, where the ID of the game rule is the name of this block. These attributes can be used:

- `name = loc_key` is the [localisation](<localisation.md>) key used as the name of the game rule shown to the player. In particular, the localisation values for this usually include [flags of countries](<localisation.md#Country.27s_flags>) or [text icons](<localisation.md>).
- `group = group_id` is the group where this game rule is positioned. **A group needs no other definition** and will be automatically created if any game rule uses this group. The group ID also serves as the [localisation](<localisation.md>) key used for the name in the currently-enabled language.
- `icon = GFX_example_sprite` is the [spriteType](<graphical_asset_modding.md>) used as the icon of the game rule. In the base game, these link to images approximately 32x32 pixels large.
- `required_dlc = "Wojtek Expansion Pack"` is the DLC required for the game rule to be *created*. If the DLC isn't enabled, then the game rule will not be created entirely, which may also manifest in additional entries in error.log when evaluating trigger blocks that reference the game rule. Optional, defaults to the game rule requiring no DLC.
- `exclude_dlc` opposite to `required_dlc`.
- `option = { ... }` and `default = { ... }` are used to define options of the game rule, with the latter being automatically selected by default. These can be replicated multiple times. In particular, these have the following attributes:
  - `name = option_name` is the ID of the option used for the [has_game_rule trigger](<triggers.md>) and occassionally hard-coded checks.
  - `text = loc_key` the [localisation](<localisation.md>) key deciding the name of the game rule shown to the player.
  - `desc = loc_key` the [localisation](<localisation.md>) key deciding the text shown to the player when they hover over the option.
  - `allow_achievements = yes` makes a game rule not disable achievements upon being selected. Since modifying game rules inherently changes the checksum from the base game, which disables achievements, this will not result in any change in a mod. Only works inside of `option = { ... }`, as the default option already allows achievements.

Example file structure:

```text
allow_new_diplo_option = {
    name = "RULE_ALLOW_SCRIPTED_DIPLO_OPTION"
    group = "RULE_GROUP_GENERAL_FOREIGN_POLICY"
    icon = "GFX_new_icon"
    default = {
        name = "ALLOWED"
        text = "RULE_OPTION_ALLOWED"
        desc = "RULE_ALLOW_SCRIPTED_DIPLO_OPTION_ALLOWED_DESC"
    }
    option = {
        name = "BLOCKED"
        text = "RULE_OPTION_BLOCKED"
        desc = "RULE_ALLOW_SCRIPTED_DIPLO_OPTION_BLOCKED_DESC"
    }
}
BHR_ai_behavior = {
    name = "BHR_AI_BEHAVIOR"
    group = "RULE_GROUP_AI_BEHAVIOR"
    default = {
        name = DEFAULT
        text = "RULE_OPTION_DEFAULT"
        desc = "RULE_OPTION_DEFAULT_AI_DESC"
    }
    option = {
        name = COMMUNIST
        text = "RULE_OPTION_COMMUNIST"
        desc = "RULE_OPTION_COMMUNIST_BHR_AI_DESC"
    }
    option = {
        name = DEMOCRATIC
        text = "RULE_OPTION_DEMOCRATIC"
        desc = "RULE_OPTION_DEMOCRATIC_BHR_AI_DESC"
    }
    option = {
        name = FASCIST
        text = "RULE_OPTION_FASCIST"
        desc = "RULE_FASCIST_BHR_AI_DESC"
    }
    option = {
        name = RANDOM
        text = "RULE_OPTION_RANDOM"
        desc = "RULE_OPTION_RANDOM_AI_DESC"
    }
}
```

<!-- kit:begin id="bookmark-game-rules-1193" at="section:Game_rules_2" -->
**Kit note** Facts about `common/game_rules/00_game_rules.txt` in 1.19.3 (86 root blocks, 434 `option` and 78 `default` entries). All lines: [vanilla-confirmed 1.19.3] `common/game_rules/00_game_rules.txt`.

- The file's own header comment says the first `option` is the default unless a `default = { ... }` entry exists, and that `allow_achievements` defaults to yes for the default option and no for every other option. Vanilla sets `allow_achievements = yes` on 61 options and `= no` on 108 (the other options rely on the default).
- The same header comment says one rule can be in several groups (repeat `group`), but no vanilla rule has more than one `group` line. The 10 vanilla groups are `RULE_GROUP_AI_BEHAVIOR`, `COUNTRY_SPECIFIC`, `COVERT_ACTIONS`, `DIVISION_TEMPLATES`, `GAMEPLAY`, `GAME_SETUP`, `GENERAL_FOREIGN_POLICY`, `GENERAL_UI`, `PEACE_SCORE` and `RESEARCH`.
- `required_dlc = "Name"` is a plain string here (130 uses) and `exclude_dlc` appears 14 times. This differs from the block form `required_dlc = { "Name" }` of bookmark country entries.
- Country AI rules are named `<TAG>_ai_behavior` (51 blocks, a few written `<TAG>_AI_BEHAVIOR`); `BHR_ai_behavior` in the example above is an invented name that follows this pattern. The root block id is what scripts use: `has_game_rule = { rule = GER_ai_behavior option = FASCIST }`. Vanilla writes the AFG rule both as `rule = AFG_AI_BEHAVIOR` (10 uses) and `rule = AFG_ai_behavior` (2 uses) though the block id is `AFG_ai_behavior`, so the lookup may ignore case; write the exact block id to be safe [unverified].
- Option names in `has_game_rule` are the `name` of the option (`FASCIST`, `DEMOCRATIC`, `RANDOM`), not the loc key.
<!-- kit:end id="bookmark-game-rules-1193" -->

## References and notes <a id="References_and_notes"></a>

**^** **a:** The difficulty itself applies a [static modifier](<modifiers.md>) to every country. There can only be 5 (though others can be hidden from the UI, it will still be possible to select them as the last selected difficulty carries over across savefiles), and different modifiers are granted to the players and AI. In particular, `diff_very_easy_player` to `diff_very_hard_player` are given to the player-led countries, and `diff_very_easy_ai` to `diff_very_hard_ai` are given to the AI-led countries.

1. ↑ Decided by the max slots in the `ideas_grid` gridbox in `gamesetup_interesting_countries_window`, by default defined in `/Hearts of Iron IV/interface/frontendgamesetupview.gui`
2. ↑ Decided by the max slots in the `focus_grid` gridbox in `gamesetup_interesting_countries_window`, by default defined in `/Hearts of Iron IV/interface/frontendgamesetupview.gui`

---

## Navigation

**[Modding](<modding.md>)**

- **Documentation**: [Effects](<effects.md>) • [Triggers](<triggers.md>) • [Defines](<defines.md>) • [Modifiers](<modifiers.md>) • [List of modifiers](<list_of_modifiers.md>) • [Scopes](<scopes.md>) • [Localisation](<localisation.md>) • [On actions](<on_actions.md>) • [Data structures](<data_structures.md>) • [Flags](<data_structures.md#Flags>) • [Event targets](<data_structures.md#Event_targets>) • [Country tag aliases](<data_structures.md#Country_tag_aliases>) • [Variables](<data_structures.md#Variables>) • [Arrays](<data_structures.md#Arrays>)
- **Scripting**: [Achievements](<achievement_modding.md>) • [AI](<ai_modding.md>) • [AI focuses](<ai_focuses.md>) • [Autonomous states](<autonomy_state_modding.md>) • [Balances of power](<balance_of_power_modding.md>) • [Game rules](<bookmark_modding.md#Game_rules>) • [Buildings](<building_modding.md>) • [Characters and traits](<character_modding.md>) • [Cosmetic tags](<cosmetic_tag_modding.md>) • [Countries](<country_creation.md>) • [Divisions](<division_modding.md>) • [Decisions](<decision_modding.md>) • [Doctrines](<doctrine_modding.md>) • [Equipment](<equipment_modding.md>) • [Events](<event_modding.md>) • [Factions](<faction_modding.md>) • [Ideas](<idea_modding.md>) • [Ideologies](<ideology_modding.md>) • [Military industrial organizations](<military_industrial_organization_modding.md>) • [National focuses](<national_focus_modding.md>) • [Resources](<resources_modding.md>) • [Scripted GUI](<scripted_gui_modding.md>) • [Technologies and doctrines](<technology_modding.md>) • [Units](<unit_modding.md>)
- **Map**: [Map](<map_modding.md>) • [States](<state_modding.md>) • [Supply areas](<supply_areas_modding.md>) • [Strategic regions](<strategic_region_modding.md>)
- **Graphical**: [Interface](<interface_modding.md>) • [Graphical assets](<graphical_asset_modding.md>) • [Entities](<entity_modding.md>) • [Posteffects](<posteffect_modding.md>) • [Particles](<particle_modding.md>) • [Fonts](<font_modding.md>)
- **Cosmetic**: [Portraits](<portrait_modding.md>) • [Namelists](<namelist_modding.md>) • [Music](<music_modding.md>) • [Sound](<sound_modding.md>)
- **Other**: [Console commands](<console_commands.md>) • [Troubleshooting](<troubleshooting.md>) • [Mod structure](<mod_structure.md>) • [Mods](<mods.md>) • [Nudger](<nudger.md>)
- **Kit pages (not on the wiki)**: [Collection modding](<collection_modding.md>) • [Defines additions](<defines_additions.md>) • [Game rule modding](<game_rule_modding.md>) • [Intelligence operation modding](<intelligence_operation_modding.md>) • [Map mode modding](<map_mode_modding.md>) • [Occupation and resistance modding](<occupation_and_resistance_modding.md>) • [Peace conference modding](<peace_conference_modding.md>) • [Raid modding](<raid_modding.md>) • [Script constant modding](<script_constant_modding.md>) • [Special project modding](<special_project_modding.md>)
