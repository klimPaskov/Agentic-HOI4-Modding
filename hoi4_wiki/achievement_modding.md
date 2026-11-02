# Achievement modding

*Offline snapshot of the Hearts of Iron IV Wiki page "Achievement modding", revision 101492, captured 2026-10-31. Wiki text by the wiki's contributors under CC BY-SA 3.0 (see LICENSE.txt); kit blocks are local additions under the same license.*

<!-- kit:begin id="review" at="top" build="1.19.4.1" checked="2026-11-01" revision="101492" sources="common/achievements.txt common/ribbons/ common/medals/ gfx/achievements/ interface/ documentation/triggers_documentation.md documentation/console_commands_documentation.md localisation/english/career_profile_achievements_l_english.yml localisation/english/core_l_english.yml localisation/english/frontend_l_english.yml hoi4.exe" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Checked against vanilla `common/achievements.txt` (293 achievements), `common/ribbons/00_ribbons.txt` (36 ribbons), `common/medals/00_medals.txt` (33 medals), the 882 files in `gfx/achievements/`, the achievement triggers and console commands in `documentation/`, and the achievement strings in `hoi4.exe`.
- Kit blocks added: how vanilla differs from the mod format (numeric `id` against `unique_id`), the `possible` and `happened` habits of vanilla, the meaning of the inventory's flagged keys (`unique_id`, `mod`, `achievement`, `ribbon`), icon size and naming from vanilla, localisation notes, and the trigger and console-command checks.
- Errors found in the wiki text: none that vanilla contradicts. The `custom_achievement` and `custom_ribbon` names in the example are only placeholder tokens. The example omits `is_ironman = yes`, which all 293 vanilla achievements require in `possible`.
- Gaps left: the mod-side format (`unique_id`, the `ribbon = { frames colors }` block, `_NAME` and `_DESC` keys, the three icon suffixes) has no vanilla or documentation source except the trigger text and a few engine strings in `hoi4.exe`, so those facts stay [unverified]. The icon suffixes and token names are now settled from `gfx/achievements/` (see the icon notes). Nothing was run in the game.
**1.19.4.1 re-check (2026-11-01).** 7 tagged statements depended on files the update changed (`common/achievements.txt`, three localisation files and `interface/`), and all of them were re-measured. The achievement list is the same size (293, ids 2 to 294) and the habit counts are unchanged, but the flags named `achievement_*` that vanilla script sets are now 42 (the earlier 31 cannot be reproduced). The console command bullets cite the changed console commands documentation: `debug_custom_achievements`, `debug_achievements`, `debug_achievements_clear`, `show_all_ribbons` and `show_all_medals` are all still listed, and only `debug_types` was removed. Every other statement cites files that are byte-identical in 1.19.4.1 (Steam depot manifest diff).
<!-- kit:end id="review" -->

## Table of contents

- [File structure](#File_structure)
- [Coding syntax](#Coding_syntax)
- [Icon](#Icon)
- [Localization](#Localization)
- [Triggers](#Triggers)
- [References](#References)

---

Paradox allowed the creation of custom achievements to be displayed in the Career Profile of a player. The ability to create these achievements came with the Avalanche (1.12.1) release.

Achievements are found in the career profile (in-game this button is called "Playthrough Overview"), images are available on the Paradox Forum.

## File structure <a id="File_structure"></a>

```text
custom_achievements/
    common/achievements/
        custom_achievements_achievements.txt
    gfx/achievements/
        custom_achievement_test.dds
        custom_achievement_test_grey.dds
        custom_achievement_test_not_eligible.dds
    localization/english/
        custom_achievements_l_english.yml
```

## Coding syntax <a id="Coding_syntax"></a>

- **unique_id** - This is mandatory and custom to your mod. It references the name of the cloudsavefile that will store the achievements.
- **custom_achievement/custom_ribbon** - This is a unique identifier for your particular achievement.
- **possible** - This checks at the game's start whether a ribbon or achievement is possible to get in the playthrough. **If false at the game's start, getting the achievement will never be possible.**
  - This is similar to `allowed` in decisions or ideas, though it is evaluated at the game's start rather than before.
  - Some common triggers not used in the code example are tag checks (with either [tag](<triggers.md>) or [original_tag](<triggers.md>)) or ironman checks (`is_ironman = yes`).
- **happened** - Once these conditions are met then the achievement is earned. (Usually instant to ~2 in-game hours)
- **ribbon** - (OPTIONAL) This is only required for ribbons. This allows you to change the colors of the ribbon utilizing RGB color code.

```text
unique_id = custom_achievements_123456

custom_achievement = {
    possible = {
        # classic triggers used in all vanilla achievements
        difficulty > 1
        has_start_date < 1936.01.02
        has_any_custom_difficulty_setting = no
        game_rules_allow_achievements = yes
    }

    happened = {
        date > 1936.01.02
    }
}

custom_ribbon = {
    possible = {
        difficulty > 1
        has_start_date < 1936.01.02
        has_any_custom_difficulty_setting = no
        game_rules_allow_achievements = yes
        tag = ITA
    }

    happened = {
        date > 1936.01.02
    }

    ribbon = {
        frames = { 1 1 1 1 }
        colors = {
            { 45.0 64.0 102.0 1.0 }
            { 154.0 73.0 107.0 1.0 }
            { 238.0 189.0 96.0 1.0 }
            { 211.0 181.0 128.0 1.0 }
        }
    }
}
```

<!-- kit:begin id="ach-format-notes" at="section:Coding_syntax" -->
**Kit note** How vanilla differs from the mod format described above, and what the page's code keys are.

- Vanilla defines its 293 achievements in one file, `common/achievements.txt`, not in a `common/achievements/` folder. Each block has a numeric `id` (unique, from 2 to 294) and the two trigger blocks `possible` and `happened`; one block adds `hidden = yes` (`vojtek_commander`). There is no `unique_id` and no `ribbon` key anywhere in the file. [vanilla-confirmed 1.19.4.1] `common/achievements.txt`.
- The file header says what the two blocks are for: `possible` filters achievements out at game start so the game does not check them all the time, and `happened` is checked to see whether the achievement was earned. [vanilla-confirmed 1.19.4.1] `common/achievements.txt`.
- `unique_id` is the mod's own identifier. The trigger text for `has_completed_custom_achievement` says its `mod` argument is the id "set in common/achievements files". [docs] `documentation/triggers_documentation.md`. `hoi4.exe` also holds the load error "Achievement read error ... unique_id is mandatory in achievement file" next to the strings `common/achievements.txt` and `common/achievements/`, so a mod file without it is probably rejected. [unverified]
- `custom_achievement` and `custom_ribbon` in the example are the tokens of the two achievements, which you replace with your own. The same token names the icon files: all 293 vanilla tokens have a `<token>.dds` in `gfx/achievements/`. [vanilla-confirmed 1.19.4.1] `common/achievements.txt`, `gfx/achievements/`. In the trigger, the token is the `achievement` argument. [docs] `documentation/triggers_documentation.md`.
- `mod` and `achievement` are the two arguments of `has_completed_custom_achievement` and appear only there. [docs] `documentation/triggers_documentation.md`.
- The `ribbon = { frames = { ... } colors = { ... } }` block is mod-side syntax from the wiki tutorial and has no counterpart in vanilla `common/achievements.txt`. Its shape matches vanilla ribbons, which live in `common/ribbons/00_ribbons.txt` and write `frames` and `colors` directly: all 36 vanilla ribbons give 4 frame numbers (values 1 to 3) and 4 colours as `{ R G B A }` with R, G and B up to 255.0 and A as 1.0. [vanilla-confirmed 1.19.3] `common/ribbons/00_ribbons.txt`. Whether the engine reads the wrapper block from a mod achievement file cannot be checked in the game files. [unverified]
- Vanilla ribbons and medals are a separate career-profile system. Their blocks (`name`, `description`, `quote_text`, `frames`, `colors`, `happened` or `bronze`/`silver`/`gold`, and a `debug` list) read career-profile values through `career_profile_check_value`, `career_profile_check_ratio` and `career_profile_set_temp_variable`. [vanilla-confirmed 1.19.3] `common/ribbons/00_ribbons.txt`, `common/medals/00_medals.txt`. [docs] `documentation/triggers_documentation.md`. No documentation file mentions `common/ribbons/` or `common/medals/`, so nothing says that mods can add to them. [docs] `documentation/*.md` (searched). Whether the engine loads mod files there stays [unverified].

**Kit note** Habits of the 293 vanilla achievements that the page's example mirrors or leaves out. All rows: [vanilla-confirmed 1.19.4.1] `common/achievements.txt`.

| Habit | Vanilla |
| --- | --- |
| `is_ironman = yes` in `possible` | 293 of 293. The wiki example omits it. `documentation/triggers_documentation.md` only says `is_ironman` checks "if current game is ironman" [docs]; whether a mod achievement also needs ironman is [unverified] |
| `difficulty > 1`, `has_any_custom_difficulty_setting = no`, `game_rules_allow_achievements = yes` in `possible` | 293 of 293 |
| `has_start_date < 1936.01.02` in `possible` | 289 of 293 (the other four use other bookmark dates) |
| tag checks (`tag`, `original_tag`) in `possible` | common, so an achievement is only possible for one country |
| `has_dlc = "..."` | 18 lines over six DLCs, either in `possible` (`original_tag = TUR` with `has_dlc = "Battle for the Bosporus"`) or inside `happened` in an `if = { limit = { has_dlc = ... } }` block |
| `happened` driven by a country flag | for example `has_country_flag = achievement_has_joined_faction`; 42 distinct flags named `achievement_*` are set with `set_country_flag` in `common/`, `events/` and `history/` (38 as `set_country_flag = <flag>` and 4 in the `{ flag = <flag> }` form) |

The documentation describes the helper triggers: `difficulty` compares against the difficulty enum 0 to 2 (so `difficulty > 1` leaves only the highest level), `has_start_date` compares the start date of the game, `has_any_custom_difficulty_setting` is true when any custom difficulty is on, `game_rules_allow_achievements` is true when every active game rule allows achievements, and `is_ironman` checks the ironman flag. All are usable in any scope. [docs] `documentation/triggers_documentation.md`.
<!-- kit:end id="ach-format-notes" -->

## Icon <a id="Icon"></a>

Images for achievements require three different images which are provided in `gfx/achievements`. These do not require a spriteType in interface.

- custom_achievement_test.dds
  - Refers to the colorized icon that is available should you complete the achievement.
- custom_achievement_test_not_eligible.dds
  - Refers to the icon if it is not able to be earned during that playthrough.
- custom_achievement_test_grey.dds
  - Refers to the icon if it is possible to be earned during that playthrough

<!-- kit:begin id="ach-icon-notes" at="section:Icon" -->
**Kit addition** Icon size and naming in vanilla. The folder `gfx/achievements/` holds 882 files: 295 base icons, 294 `_grey` and 293 `_not_eligible`, one trio per achievement token. Every one is a DDS texture of 64 by 64 px; 792 are uncompressed and 90 use DXT5. [vanilla-confirmed 1.19.3] header read of the files in `gfx/achievements/`. Use 64 by 64 px for the three mod icons. No `spriteType` refers to them, which agrees with the page: no `.gfx` or `.gui` file under `interface/` mentions `gfx/achievements`. [vanilla-confirmed 1.19.4.1] `interface/`.

The names are the achievement token plus a suffix (`<token>.dds`, `<token>_grey.dds`, `<token>_not_eligible.dds`). `hoi4.exe` contains `gfx/achievements/`, `_grey` and `_not_eligible` as separate strings, which fits the engine building the path from the token. [unverified] Vanilla follows this rule: 293 of 293 tokens have `<token>.dds` and `<token>_grey.dds`, and 292 of 293 have `<token>_not_eligible.dds` (see the exception below). [vanilla-confirmed 1.19.4.1] `common/achievements.txt`, `gfx/achievements/`. Vanilla has two irregular names that you should not copy: `sapmi_united_by_the_fire` has no matching trio but a stray `sapmi_united_by_the_fire_eligible.dds`, and `urugorn.dds` matches no achievement. [vanilla-confirmed 1.19.3] `gfx/achievements/`.
<!-- kit:end id="ach-icon-notes" -->

## Localization <a id="Localization"></a>

Localization for the achievement is done in two loc keys. The suffix NAME refers to the title of the achievement and the DESC refers to the description that can be either some funny joke or how you describe to achieve the achievement.

```text
 custom_achievement_test_NAME: "Custom Achievement Title"
 custom_achievement_test_DESC: "Custom Achievement Description"
```

<!-- kit:begin id="ach-loc-notes" at="section:Localization" -->
**Kit note** Vanilla's own achievement texts are not in `localisation/english/`: no `<token>_NAME` or `<token>_DESC` key exists there for tokens such as `friend_in_need`. The two-key scheme on this page therefore rests on the wiki tutorial and on a `_NAME` string that sits beside `gfx/achievements/` in `hoi4.exe`. [vanilla-confirmed 1.19.4.1] 0 matches for `friend_in_need` under `localisation/english/`. [unverified]

The game does have interface strings that show a mod achievement's conditions in the career profile, for example `CAREER_PROFILE_MOD_ACHIEVEMENT_AVAILABLE_WHEN` ("Will be available when:") and `ACHIEVEMENT_UNLOCKED_WHEN` ("Will be earned when:"), and the front end shows `ACHIEVEMENTS_MOD_OK` ("Can get Achievements from mods!") when a mod has achievements. [vanilla-confirmed 1.19.4.1] `localisation/english/career_profile_achievements_l_english.yml`, `localisation/english/core_l_english.yml`, `localisation/english/frontend_l_english.yml`. That the condition text is built from the `possible` and `happened` triggers is a reading of those strings. [unverified]
<!-- kit:end id="ach-loc-notes" -->

## Triggers <a id="Triggers"></a>

Achievement related triggers.

General any-scoped triggers:

| Name | Parameters | Examples | Description | Notes | Version Added |
| --- | --- | --- | --- | --- | --- |
| has_completed_custom_achievement | `mod = <mod ID>`<br>The mod where the achievement is from.<br> `achievement = <achievement ID>`<br>The name of the achievement. | *(example below)* | Checks if the player controlling the current scope has completed the specified custom achievement. | The achievement (including the ID of the mod it's from) is defined within `/Hearts of Iron IV/common/achievements/*.txt` files. The achievement could be completed during a previous session, not necessarily the current one. If the mod defining the achievement is not loaded, the trigger evaluates as false. | 1.12.5 |

**Example: has_completed_custom_achievement**

```text
has_completed_custom_achievement = {
    mod = my_mod_unique_id
    achievement = my_achievement_token
}
```

<!-- kit:begin id="ach-trigger-notes" at="section:Triggers" -->
**Kit note** Checks of the trigger table above.

- `has_completed_custom_achievement` is usable in any scope. It is true when the achievement is found in the currently loaded mods and was completed in this game or in an earlier one, and its two arguments are `mod` (the `unique_id`) and `achievement` (the token). [docs] `documentation/triggers_documentation.md`. This matches the table, including the false result when the mod is not loaded.
- The console command `debug_custom_achievements` clears the completion status of mod achievements (it deletes the files on cloud storage) and reloads the mod achievement files, which makes it the way to retest an achievement. [docs] `documentation/console_commands_documentation.md`. `debug_achievements` turns on achievement popups and `debug_achievements_clear` clears all achievements and user stats; the documentation marks both as not available in the release build. [docs] `documentation/console_commands_documentation.md`. See [Console commands](<console_commands.md>).
- `show_all_ribbons` and `show_all_medals` (argument `bronze`, `silver` or `gold`) show every career-profile ribbon or medal as achieved without earning it; they concern vanilla ribbons and medals, not mod achievements. [docs] `documentation/console_commands_documentation.md`.
- The related triggers `career_profile_check_ribbon` and `career_profile_check_medal` test whether a vanilla ribbon or medal is earned and collected, in any scope. [docs] `documentation/triggers_documentation.md`.
<!-- kit:end id="ach-trigger-notes" -->

## References <a id="References"></a>

- [1] Achievements for mods
- [2] Tutorial to design ribbons in mod achievement
- [3] Tutorial to write achievements files in your mod

---

## Navigation

**[Modding](<modding.md>)**

- **Documentation**: [Effects](<effects.md>) • [Triggers](<triggers.md>) • [Defines](<defines.md>) • [Modifiers](<modifiers.md>) • [List of modifiers](<list_of_modifiers.md>) • [Scopes](<scopes.md>) • [Localisation](<localisation.md>) • [On actions](<on_actions.md>) • [Data structures](<data_structures.md>) • [Flags](<data_structures.md#Flags>) • [Event targets](<data_structures.md#Event_targets>) • [Country tag aliases](<data_structures.md#Country_tag_aliases>) • [Variables](<data_structures.md#Variables>) • [Arrays](<data_structures.md#Arrays>)
- **Scripting**: [AI](<ai_modding.md>) • [AI focuses](<ai_focuses.md>) • [Autonomous states](<autonomy_state_modding.md>) • [Balances of power](<balance_of_power_modding.md>) • [Bookmarks/Scenarios](<bookmark_modding.md>) • [Game rules](<bookmark_modding.md#Game_rules>) • [Buildings](<building_modding.md>) • [Characters and traits](<character_modding.md>) • [Cosmetic tags](<cosmetic_tag_modding.md>) • [Countries](<country_creation.md>) • [Divisions](<division_modding.md>) • [Decisions](<decision_modding.md>) • [Doctrines](<doctrine_modding.md>) • [Equipment](<equipment_modding.md>) • [Events](<event_modding.md>) • [Factions](<faction_modding.md>) • [Ideas](<idea_modding.md>) • [Ideologies](<ideology_modding.md>) • [Military industrial organizations](<military_industrial_organization_modding.md>) • [National focuses](<national_focus_modding.md>) • [Resources](<resources_modding.md>) • [Scripted GUI](<scripted_gui_modding.md>) • [Technologies and doctrines](<technology_modding.md>) • [Units](<unit_modding.md>)
- **Map**: [Map](<map_modding.md>) • [States](<state_modding.md>) • [Supply areas](<supply_areas_modding.md>) • [Strategic regions](<strategic_region_modding.md>)
- **Graphical**: [Interface](<interface_modding.md>) • [Graphical assets](<graphical_asset_modding.md>) • [Entities](<entity_modding.md>) • [Posteffects](<posteffect_modding.md>) • [Particles](<particle_modding.md>) • [Fonts](<font_modding.md>)
- **Cosmetic**: [Portraits](<portrait_modding.md>) • [Namelists](<namelist_modding.md>) • [Music](<music_modding.md>) • [Sound](<sound_modding.md>)
- **Other**: [Console commands](<console_commands.md>) • [Troubleshooting](<troubleshooting.md>) • [Mod structure](<mod_structure.md>) • [Mods](<mods.md>) • [Nudger](<nudger.md>)
- **Kit pages (not on the wiki)**: [Collection modding](<collection_modding.md>) • [Defines additions](<defines_additions.md>) • [Game rule modding](<game_rule_modding.md>) • [Intelligence operation modding](<intelligence_operation_modding.md>) • [Map mode modding](<map_mode_modding.md>) • [Occupation and resistance modding](<occupation_and_resistance_modding.md>) • [Peace conference modding](<peace_conference_modding.md>) • [Raid modding](<raid_modding.md>) • [Script constant modding](<script_constant_modding.md>) • [Special project modding](<special_project_modding.md>)
