# Table of contents

- [Attributes](#attributes)
- [File example](#file-example)
- [User interface](#user-interface)
- [Notes](#notes)
- [Game rules](#game-rules)
  - [Difficulty settings](#difficulty-settings)
  - [Game rules](#game-rules_2)
- [References and notes](#references-and-notes)

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

## <a id="attributes"></a>Attributes

These attributes go into a `bookmark = { ... }` block. Each of the arguments of a bookmark is theoretically optional.

- `name = loc_key` decides on the [localisation](<Localisation - Hearts of Iron 4 Wiki.md>) key used for the name of the bookmark used during the start date selection. Defaults to showing nothing.
- `desc = loc_key` decides on the [localisation](<Localisation - Hearts of Iron 4 Wiki.md>) key used for the description of the bookmark used during the start date selection. Defaults to showing nothing.
- `date = 1936.1.1.12` decides on the date which notes when the game should start, written in the YYYY.MM.DD.HH format. Defaults to 2.1.1.1, and no earlier date can be used.
- `picture = GFX_select_date_1936` decides on the [spriteType](https://hoi4.paradoxwikis.com/SpriteType) definition used for the start date, defined in any `/Hearts of Iron IV/interface/*.gfx` file. Defaults to being pure black.
- `default = yes` is used to mark the bookmark as default, resulting in the game pre-loading its conditions during the main menu and making the player choose it by default. Defaults to false, only one bookmark should have this.
- `default_country = GER` decides on the country tag that should be chosen by the player by default. The country must be among the interesting countries.
- `effect = { ... }` is an [effect](<Effects - Hearts of Iron 4 Wiki.md>) block that will be executed when the bookmark is selected. This is done after the history folder but before the player can select a country. In particular, [randomize\_weather](<Effects - Hearts of Iron 4 Wiki.md#randomize-weather>) should be used to ensure that the weather works properly, but this can also be used to ensure that the bookmark has different conditions from another one on the same date.
- `TAG = { ... }` is used to create an entry for a country among the interesting countries. Using the tag of `---` will be taken as the "other countries" menu, allowing the player to enter the country selection without any selected. The same country may have several definitions. In particular, these are used as arguments inside:
  - `history = loc_key` decides on the [localisation](<Localisation - Hearts of Iron 4 Wiki.md>) key used for the description shown to the player when this country is chosen.
  - `ideology = neutrality` is the [ideology](https://hoi4.paradoxwikis.com/Ideology) group that the country starts with. This is used to determine the country leader, the ideology icon, the name of the country, and the flag.
  - `minor = yes` is used to mark the country as minor, making it appear in the lower menu with small flags instead of the top one where the leader is shown. **This will also requires the country to start with a national focus tree that doesn't have `default = yes` to show up in the selection**, used in the base game to make the interesting country selection depend on the [DLCs](https://hoi4.paradoxwikis.com/DLC).
  - `available = { has_dlc = "Poland: United and Ready" }` is a [trigger](<Triggers - Hearts of Iron 4 Wiki.md>) block that must be fulfilled for the country to show up in the selection. This is typically only used for DLC checks, as nothing else may reasonably change before country selection.
  - `ideas = { TAG_idea_1 TAG_idea_2 TAG_idea_3 }` is the list of [national spirits](https://hoi4.paradoxwikis.com/National_spirit) that should be shown to the player when the country is selected. This doesn't modify or depend on the actual spirits that the country will have on startup, which is typically handled in [country history](<Country creation - Hearts of Iron 4 Wiki.md#country-history>) or [state history](<State modding - Hearts of Iron 4 Wiki.md#history>). By default, limited to 3 entries.[[1]](#cite-note-1)
  - `focuses = { TAG_focus_1 TAG_focus_2 TAG_focus_3 }` is the list of [national focuses](<National focus modding - Hearts of Iron 4 Wiki.md>) that should be shown to the player when the country is selected. By default, limited to 3 entries.[[2]](#cite-note-2)

## <a id="file-example"></a>File example

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

## <a id="user-interface"></a>User interface

<a id="interface"></a>

*See also: [Interface modding](<Interface modding - Hearts of Iron 4 Wiki.md>)*

| General sprite overview |
| --- |
| For loading GFX, the game uses the sprite system. Sprites are code definitions that attach a name to an image file, as well as optionally adding additional information, such as animation, the amount of frames, the way that the image will be loaded, and so on. This means **placing an image into the gfx folder isn't enough for it to work**, a sprite has to use that image file as well. Sprites are defined in any `/Hearts of Iron IV/interface/*.gfx` file (this is separate from `gfx/interface/`), opened with a text editor. To create a new .gfx file, a text file can be created and renamed to change the extension (on Windows, the [Windows Explorer needs to show the extensions, which it doesn't by default](https://support.microsoft.com/en-gb/windows/common-file-name-extensions-in-windows-da4a4430-8e76-89c5-59f7-1cdbbc75cb01)). In particular, sprites are defined within a `spriteTypes = { ... }` block, as to separate from fonts and map arrows also defined in that folder, while the simplest sprite with the least mandatory properties is a `spriteType = { ... }`. The simplest sprite definition looks like the following: `spriteTypes = { spriteType = { name = GFX_first_sprite # In some cases, beginning with GFX_ is mandatory for it to work. texturefile = gfx/interface/folder/filename.dds # The folder and filename don't matter, as long as they are correct } # Only the forward slash '/' (can be doubled as '//') can be used to separate folders. spriteType = { # The image doesn't have to be .dds, as .tga and .png are acceptable. name = GFX_second_sprite texturefile = gfx/interface/folder2/filename2.dds noOfFrames = 2 # Splits the image into 2 halves, which may be switched between dynamically in GUI } }` In this case, this creates a sprite with the name of `GFX_first_sprite` and attaches the `/Hearts of Iron IV/gfx/interface/folder/filename.dds` image to it, and a second sprite similarly. The second sprite will be split into 2 frames: this is decided by having the left half of the image as the first frame and the right half as the second frame (more frames would further split the image horizontally). This doesn't make the sprite animated, just turns on the option to switch between the two halves as needed. `GFX_second_sprite:1` serves as a reference to the first frame, and GUI can be set up to change the shown frame depending on context, such as with radio stations.  In order to add animation, a [frameAnimatedSpriteType](<Graphical asset modding - Hearts of Iron 4 Wiki.md#frameanimatedspritetype>) is used.  **It's never mandatory to copy a base game file to change a sprite**. If there are duplicate definitions of a sprite with the same name in different files, the game will prioritise the one that would be [evaluated later, based on the filename](<Modding - Hearts of Iron 4 Wiki.md#loading-files>), and the older sprite will be ignored in entirety. This can be ensured by beginning the replacement file's name with a symbol late in the ASCII character table. Typically the lowercase letter 'z' is used for this purpose. For example, to change the amount of frames in `GFX_idea_traits_strip` to 10, it is possible to define a sprite with that name with 10 frames in the mod's `modname/interface/zz_replace.gfx` file instead of copying over the base game file.  Since most .gfx files define integral parts of the user interface, copying them over can lead to the mod's loaded files missing sprites upon a major game update, which would appear in-game as the default image, which is the error dog by default. As to ease the burden of needing to check the interface files, it's best to never copy over .gfx files, unless more additions would be actively harmful to the mod, such as with `interface/subuniticons.gfx` |

In the base game, the images used to represent a bookmark (e.g. `GFX_select_date_1936`) have the size of 180x104 pixels, with there being a gap in the bottom to prevent overlap with the frame. This gap can be created by selecting and deleting a circle with a radius of ~35 pixels and the centre approximately 90 pixels to the right from the left edge and 130 pixels below the top edge.

By default, the selection of bookmarks and interesting countries within bookmarks is defined in the `/Hearts of Iron IV/interface/frontendgamesetupview.gui` file. In particular, these changes are common to make:

- The `bookmarks_grid` gridbox is used for positioning the bookmarks for the player to select, and the `bookmark_entry` container windows are the individual elements of that gridbox. If the amount of bookmarks doesn't match the ones in the base game, this is necessary to edit:
  - By default, having one bookmark in the loaded files skips the bookmark selection entirely. This can be circumvented by having two bookmarks, but hiding the second one from view. Adding `max_slots_horizontal = 1` to the gridbox will prevent more than 1 from showing. The gridbox may be edited in the opposite case of more than 2 bookmarks as well, by increasing the amount of possible rows.
  - If the amount of bookmark differs from the default, the size of each bookmark may be changed. This would require changing the coordinate positions of elements inside of each bookmark, as well as changing the image used for the frame and/or the font size.
- There are 3 `countries_grid` gridboxes in the file used for positioning the interesting countries. The one inside of the `countries` container window is used for major countries, while the ones inside `countries_medium` and `countries_mini` are for minor countries, changing from one to the other after a 9th minor country is added.
  - There is no way to make either gridbox not follow a grid pattern. However, it is instead possible to create dummy country entries and hide them from the final product by placing [iconTypes](<Interface modding - Hearts of Iron 4 Wiki.md#icontype>) inside of the `gamesetup_interesting_countries_window` container window after the gridbox, set to use an image that covers up the minor interesting country with the background.

## <a id="notes"></a>Notes

- If there is only one bookmark defined within the loaded files, the game will skip the bookmark selection for the player and go straight into the bookmark selection. From that menu, going back to the main menu, either with the interface button or by using hte hotkey, is impossible. This can be avoided by still having a second bookmark but hiding it from the player, as in [§ User interface](#user-interface).
- The start date cannot be placed before the year 2. If the earliest start date is changed from default, it is necessary to edit the [Defines](<Defines - Hearts of Iron 4 Wiki.md>) in an [override file](<Defines - Hearts of Iron 4 Wiki.md#overrides>). In particular,[NGame.START\_DATE](<Defines - Hearts of Iron 4 Wiki.md#start-date>), [NGame.END\_DATE](<Defines - Hearts of Iron 4 Wiki.md#end-date>), and [NDiplomacy.TENSION\_TIME\_SCALE\_START\_DATE](<Defines - Hearts of Iron 4 Wiki.md#tension-time-scale-start-date>) are the ones may need changing.
- In order for the in-game state to change between the start dates, it is possible to place date blocks in [country history](<Country creation - Hearts of Iron 4 Wiki.md#adding-history-for-other-bookmarks>) or [state history](<State modding - Hearts of Iron 4 Wiki.md#history>), which will be executed if and only if the start date is strictly later than the specified date. For example, this state history block will make it be owned by ABC on the game's start, but by DEF if the start date is later than 1937.1.1:

```text
history = {
    owner = ABC
    1937.1.1 = {
        owner = DEF
    }
}
```

- If there should be a difference between bookmarks with the same date, then the `effect` attribute can be used.
- The bookmarks are positioned in the order of their start dates. If two bookmarks have the same date, then they are positioned in the order [in which they are evaluated](<Modding - Hearts of Iron 4 Wiki.md#loading-files>). The interesting countries are positioned in the order in which they are written in the bookmark.

## <a id="game-rules"></a>Game rules

The game rules allow the player to change the gameplay conditions that will apply after the country selection has been finished. There are two types of database elements that are grouped under "Game rules" for the player:

- Difficulty settings, in `/Hearts of Iron IV/common/difficulty_settings/*.txt` files. These are used to apply a modifier to a country or a group of countries and present themselves as a slider.
- Game rules, in `/Hearts of Iron IV/common/game_rules/*.txt` files. These are used to present a dropdown menu to the player out of a few options.

**Either one having no valid entries will result in the player being unable to open the menu for editing the game rules.**

### <a id="difficulty-settings"></a>Difficulty settings

Difficulty settings will apply a [static modifier](https://hoi4.paradoxwikis.com/Static_modifier) to a country or a group of countries based on the slider that the player chooses, defined within `/Hearts of Iron IV/common/difficulty_settings/*.txt` files. This is unrelated to the difficulty itself that the player chooses.[[a]](#cnote-a)

The files are structured with a unified `difficulty_settings = { ... }` entry, with each difficulty setting being a separate `difficulty_setting = { ... }` inside of it. In particular, these attributes exist:

- `key = custom_diff_strong_tag` is the [localisation](<Localisation - Hearts of Iron 4 Wiki.md>) key used as the name of the setting in the game rules menu.
- `modifier = diff_strong_ai_generic` is the [static modifier](https://hoi4.paradoxwikis.com/Static_modifier) that gets used for the setting.
- `countries = { ABC DEF GHI }` is a list of country tags that should have the modifier applied.
- `multiplier = 2.0` is how much the modifier should be multiplied to on the maximum scale. This scales linearly depending on which value the player chose out of 5 total positions the slider can take, from 0 to the number in the attribute. For example, if the static modifier contains `stability_factor = 0.4` and the multiplier is set to 2.0, each position of the slider from left to right will respectively give the country 0%, 20%, 40%, 60%, and 80% ![Stability](media/country-creation-hearts-of-iron-4-wiki_1d4220f262__img10.png)[Stability](https://hoi4.paradoxwikis.com/Stability).

The sliders are positioned in the order [in which they are evaluated](<Modding - Hearts of Iron 4 Wiki.md#loading-files>). In particular, the [files in the folder are sorted using the ASCII character order](http://en.wikipedia.org/wiki/ASCII#Printable_characters), then the sliders are added in the order that they are defined in the files.

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

### <a id="game-rules_2"></a>Game rules

Game rules apply allow the player to choose an option among the selection of a few choices before the game's start, defined in `/Hearts of Iron IV/common/game_rules/*.txt` files. For any new game rules, this will **only** change how the [has\_game\_rule trigger](<Triggers - Hearts of Iron 4 Wiki.md#has-game-rule>) evaluates, which can be used in [conditional statements](<Effects - Hearts of Iron 4 Wiki.md#if>) to give a different result based on the game rule.

There are these three general categories of game rules that exist in the base game:

- One-time change in-game: This usually changes some aspect of the world immediately after the game starts, using [the on\_startup on action](<On actions - Hearts of Iron 4 Wiki.md#on-startup>). For example, the "nation fragmentation" game rules fall into this category.
- Mechanical change: This changes how some mechanic works by continuously checking for the game rule being set in-game. For example, the game rule to hide obsolete [national focus](<National focus modding - Hearts of Iron 4 Wiki.md>) branches does so by including a check for the game rule being set in the [allow\_branch of the national focuses to hide](<National focus modding - Hearts of Iron 4 Wiki.md#allow-branch>). These two subsets are particularly notable:

:   - Diplomatic actions: these game rules modify the prerequisites necessary to execute a diplomatic action. These are usually handled with [diplomacy scripted triggers](https://hoi4.paradoxwikis.com/Diplomacy_scripted_triggers), though occassionally there is distinction that's purely hard-coded (Usually this is the difference between the "Limited" and "Free" options).
    - AI behaviour: these game rules are checked for within [AI strategy plans](https://hoi4.paradoxwikis.com/AI_strategy_plans) and enable one to choose a random focus path. The "random" option is typically handled by setting a [country flag](https://hoi4.paradoxwikis.com/Flag) using [random\_list](<Effects - Hearts of Iron 4 Wiki.md#random-list>) within the [the on\_startup on action](<On actions - Hearts of Iron 4 Wiki.md#on-startup>).

- Entirely hard-coded game rules: Some game rules' values are checked directly in the game's binary and thus are unmoddable for the most part with the exception of deleting them or some options of them. For example, the game rule that changes the maximum level of land forts falls under this category.

Each game rule is defined as a separate root-level block within the `common/game_rules/` file, where the ID of the game rule is the name of this block. These attributes can be used:

- `name = loc_key` is the [localisation](<Localisation - Hearts of Iron 4 Wiki.md>) key used as the name of the game rule shown to the player. In particular, the localisation values for this usually include [flags of countries](<Localisation - Hearts of Iron 4 Wiki.md#country-27s-flags>) or [text icons](https://hoi4.paradoxwikis.com/Text_icon).
- `group = group_id` is the group where this game rule is positioned. **A group needs no other definition** and will be automatically created if any game rule uses this group. The group ID also serves as the [localisation](<Localisation - Hearts of Iron 4 Wiki.md>) key used for the name in the currently-enabled language.
- `icon = GFX_example_sprite` is the [spriteType](https://hoi4.paradoxwikis.com/SpriteType) used as the icon of the game rule. In the base game, these link to images approximately 32x32 pixels large.
- `required_dlc = "Wojtek Expansion Pack"` is the DLC required for the game rule to be *created*. If the DLC isn't enabled, then the game rule will not be created entirely, which may also manifest in additional entries in error.log when evaluating trigger blocks that reference the game rule. Optional, defaults to the game rule requiring no DLC.
- `exclude_dlc` opposite to `required_dlc`.
- `option = { ... }` and `default = { ... }` are used to define options of the game rule, with the latter being automatically selected by default. These can be replicated multiple times. In particular, these have the following attributes:
  - `name = option_name` is the ID of the option used for the [has\_game\_rule trigger](<Triggers - Hearts of Iron 4 Wiki.md#has-game-rule>) and occassionally hard-coded checks.
  - `text = loc_key` the [localisation](<Localisation - Hearts of Iron 4 Wiki.md>) key deciding the name of the game rule shown to the player.
  - `desc = loc_key` the [localisation](<Localisation - Hearts of Iron 4 Wiki.md>) key deciding the text shown to the player when they hover over the option.
  - `allow_achievements = yes` makes a game rule not disable achievements upon being selected. Since modifying game rules inherently changes the [checksum](https://hoi4.paradoxwikis.com/Checksum) from the base game, which disables achievements, this will not result in any change in a mod. Only works inside of `option = { ... }`, as the default option already allows achievements.

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

## <a id="references-and-notes"></a>References and notes

**[^](#ref-a)** **a:** The difficulty itself applies a [static modifier](https://hoi4.paradoxwikis.com/Static_modifier) to every country. There can only be 5 (though others can be hidden from the UI, it will still be possible to select them as the last selected difficulty carries over across savefiles), and different modifiers are granted to the players and AI. In particular, `diff_very_easy_player` to `diff_very_hard_player` are given to the player-led countries, and `diff_very_easy_ai` to `diff_very_hard_ai` are given to the AI-led countries.

1. [↑](#cite-ref-1) Decided by the max slots in the `ideas_grid` gridbox in `gamesetup_interesting_countries_window`, by default defined in `/Hearts of Iron IV/interface/frontendgamesetupview.gui`
2. [↑](#cite-ref-2) Decided by the max slots in the `focus_grid` gridbox in `gamesetup_interesting_countries_window`, by default defined in `/Hearts of Iron IV/interface/frontendgamesetupview.gui`

**[Modding](<Modding - Hearts of Iron 4 Wiki.md>)**

|  |  |
| --- | --- |
| Documentation | [Effects](<Effects - Hearts of Iron 4 Wiki.md>) • [Triggers](https://hoi4.paradoxwikis.com/Conditions) • [Defines](<Defines - Hearts of Iron 4 Wiki.md>) • [Modifiers](<Modifiers - Hearts of Iron 4 Wiki.md>) • [List of modifiers](https://hoi4.paradoxwikis.com/List_of_modifiers) • [Scopes](<Scopes - Hearts of Iron 4 Wiki.md>) • [Localisation](<Localisation - Hearts of Iron 4 Wiki.md>) • [On actions](<On actions - Hearts of Iron 4 Wiki.md>) • [Data structures](<Data structures - Hearts of Iron 4 Wiki.md>) ([Flags](<Data structures - Hearts of Iron 4 Wiki.md#flags>), [Event targets](<Data structures - Hearts of Iron 4 Wiki.md#event-targets>), [Country tag aliases](<Data structures - Hearts of Iron 4 Wiki.md#country-tag-aliases>), [Variables](<Data structures - Hearts of Iron 4 Wiki.md#variables>), [Arrays](<Data structures - Hearts of Iron 4 Wiki.md#arrays>)) |

|  |  |
| --- | --- |
| Scripting | [Achievements](<Achievement modding - Hearts of Iron 4 Wiki.md>) • [AI](<AI modding - Hearts of Iron 4 Wiki.md>) • [AI focuses](<AI focuses - Hearts of Iron 4 Wiki.md>) • [Autonomous states](<Autonomy state modding - Hearts of Iron 4 Wiki.md>) • [Balances of power](<Balance of power modding - Hearts of Iron 4 Wiki.md>) • Bookmarks/Scenarios ([Game rules](<Bookmark modding - Hearts of Iron 4 Wiki.md#game-rules>)) • [Buildings](<Building modding - Hearts of Iron 4 Wiki.md>) • [Characters and traits](<Character modding - Hearts of Iron 4 Wiki.md>) • [Cosmetic tags](<Cosmetic tag modding - Hearts of Iron 4 Wiki.md>) • [Countries](<Country creation - Hearts of Iron 4 Wiki.md>) • [Divisions](<Division modding - Hearts of Iron 4 Wiki.md>) • [Decisions](<Decision modding - Hearts of Iron 4 Wiki.md>) • [Doctrines](<Doctrine modding - Hearts of Iron 4 Wiki.md>) • [Equipment](<Equipment modding - Hearts of Iron 4 Wiki.md>) • [Events](<Event modding - Hearts of Iron 4 Wiki.md>) • [Factions](<Faction modding - Hearts of Iron 4 Wiki.md>) • [Ideas](<Idea modding - Hearts of Iron 4 Wiki.md>) • [Ideologies](<Ideology modding - Hearts of Iron 4 Wiki.md>) • [Military industrial organizations](<Military industrial organization modding - Hearts of Iron 4 Wiki.md>) • [National focuses](<National focus modding - Hearts of Iron 4 Wiki.md>) • [Resources](<Resources modding - Hearts of Iron 4 Wiki.md>) • [Scripted GUI](<Scripted GUI modding - Hearts of Iron 4 Wiki.md>) • [Technologies and doctrines](<Technology modding - Hearts of Iron 4 Wiki.md>) • [Units](<Unit modding - Hearts of Iron 4 Wiki.md>) |

|  |  |
| --- | --- |
| Map | [Map](<Map modding - Hearts of Iron 4 Wiki.md>) • [States](<State modding - Hearts of Iron 4 Wiki.md>) • [Supply areas](<Supply areas modding - Hearts of Iron 4 Wiki.md>) • [Strategic regions](<Strategic region modding - Hearts of Iron 4 Wiki.md>) |

|  |  |
| --- | --- |
| Graphical | [Interface](<Interface modding - Hearts of Iron 4 Wiki.md>) • [Graphical assets](<Graphical asset modding - Hearts of Iron 4 Wiki.md>) • [Entities](<Entity modding - Hearts of Iron 4 Wiki.md>) • [Posteffects](<Posteffect modding - Hearts of Iron 4 Wiki.md>) • [Particles](<Particle modding - Hearts of Iron 4 Wiki.md>) • [Fonts](<Font modding - Hearts of Iron 4 Wiki.md>) |

|  |  |
| --- | --- |
| Cosmetic | [Portraits](<Portrait modding - Hearts of Iron 4 Wiki.md>) • [Namelists](<Namelist modding - Hearts of Iron 4 Wiki.md>) • [Music](<Music modding - Hearts of Iron 4 Wiki.md>) • [Sound](<Sound modding - Hearts of Iron 4 Wiki.md>) |

|  |  |
| --- | --- |
| Other | [Console commands](<Console commands - Hearts of Iron 4 Wiki.md>) • [Troubleshooting](<Troubleshooting - Hearts of Iron 4 Wiki.md>) • [Mod structure](https://hoi4.paradoxwikis.com/Mod_structure) • [Mods](https://hoi4.paradoxwikis.com/Mods) • [Nudger](https://hoi4.paradoxwikis.com/Nudger) |
