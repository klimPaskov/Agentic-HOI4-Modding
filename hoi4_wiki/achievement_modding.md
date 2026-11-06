# Achievement modding

Paradox allowed the creation of custom achievements to be displayed in the Career Profile of a player. The ability to create these achievements came with the Avalanche (1.12.1) release.

Achievements are found in the career profile (in-game this button is called "Playthrough Overview"), images are available on the Paradox Forum.

## File structure

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

## Coding syntax

- **unique_id** - This is mandatory and custom to your mod. It references the name of the cloudsavefile that will store the achievements.
- **custom_achievement/custom_ribbon** - This is a unique identifier for your particular achievement.
- **possible** - This checks at the game's start whether a ribbon or achievement is possible to get in the playthrough. **If false at the game's start, getting the achievement will never be possible.**
  - This is similar to `allowed` in decisions or ideas, though it is evaluated at the game's start rather than before.
  - Some common triggers not used in the code example are tag checks (with either [tag](triggers.md) or [original_tag](triggers.md)) or ironman checks (`is_ironman = yes`).
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

How vanilla differs from the mod format described above, and what the page's code keys are.

- Vanilla defines its 293 achievements in one file, `common/achievements.txt`, not in a `common/achievements/` folder. Each block has a numeric `id` (unique, from 2 to 294) and the two trigger blocks `possible` and `happened`; one block adds `hidden = yes` (`vojtek_commander`). There is no `unique_id` and no `ribbon` key anywhere in the file.
- The file header says what the two blocks are for: `possible` filters achievements out at game start so the game does not check them all the time, and `happened` is checked to see whether the achievement was earned.
- `unique_id` is the mod's own identifier. The trigger text for `has_completed_custom_achievement` says its `mod` argument is the id "set in common/achievements files". `hoi4.exe` also holds the load error "Achievement read error ... unique_id is mandatory in achievement file" next to the strings `common/achievements.txt` and `common/achievements/`, so a mod file without it is probably rejected. (unverified)
- `custom_achievement` and `custom_ribbon` in the example are the tokens of the two achievements, which you replace with your own. The same token names the icon files: all 293 vanilla tokens have a `<token>.dds` in `gfx/achievements/`. In the trigger, the token is the `achievement` argument.
- `mod` and `achievement` are the two arguments of `has_completed_custom_achievement` and appear only there.
- The `ribbon = { frames = { ... } colors = { ... } }` block is mod-side syntax from the wiki tutorial and has no counterpart in vanilla `common/achievements.txt`. Its shape matches vanilla ribbons, which live in `common/ribbons/00_ribbons.txt` and write `frames` and `colors` directly: all 36 vanilla ribbons give 4 frame numbers (values 1 to 3) and 4 colours as `{ R G B A }` with R, G and B up to 255.0 and A as 1.0. Whether the engine reads the wrapper block from a mod achievement file cannot be checked in the game files. (unverified)
- Vanilla ribbons and medals are a separate career-profile system. Their blocks (`name`, `description`, `quote_text`, `frames`, `colors`, `happened` or `bronze`/`silver`/`gold`, and a `debug` list) read career-profile values through `career_profile_check_value`, `career_profile_check_ratio` and `career_profile_set_temp_variable`. No documentation file mentions `common/ribbons/` or `common/medals/`, so nothing says that mods can add to them. The engine does read mod files in `common/ribbons/`: a mod ribbon file with a deliberate unknown trigger in its `happened` block was reported at load under the mod file's name ("Unknown trigger-type"), and a valid mod ribbon file drew no error line. Whether a mod ribbon shows in the career profile was not seen.

Habits of the 293 vanilla achievements that the page's example mirrors or leaves out.

| Habit | Vanilla |
| --- | --- |
| `is_ironman = yes` in `possible` | 293 of 293. The wiki example omits it. `documentation/triggers_documentation.md` only says `is_ironman` checks "if current game is ironman"; whether a mod achievement also needs ironman is unverified |
| `difficulty > 1`, `has_any_custom_difficulty_setting = no`, `game_rules_allow_achievements = yes` in `possible` | 293 of 293 |
| `has_start_date < 1936.01.02` in `possible` | 289 of 293 (the other four use other bookmark dates) |
| tag checks (`tag`, `original_tag`) in `possible` | common, so an achievement is only possible for one country |
| `has_dlc = "..."` | 18 lines over six DLCs, either in `possible` (`original_tag = TUR` with `has_dlc = "Battle for the Bosporus"`) or inside `happened` in an `if = { limit = { has_dlc = ... } }` block |
| `happened` driven by a country flag | for example `has_country_flag = achievement_has_joined_faction`; 42 distinct flags named `achievement_*` are set with `set_country_flag` in `common/`, `events/` and `history/` (38 as `set_country_flag = <flag>` and 4 in the `{ flag = <flag> }` form) |

The documentation describes the helper triggers: `difficulty` compares against the difficulty enum 0 to 2 (so `difficulty > 1` leaves only the highest level), `has_start_date` compares the start date of the game, `has_any_custom_difficulty_setting` is true when any custom difficulty is on, `game_rules_allow_achievements` is true when every active game rule allows achievements, and `is_ironman` checks the ironman flag. All are usable in any scope.

## Icon

Images for achievements require three different images which are provided in `gfx/achievements`. These do not require a spriteType in interface.

- custom_achievement_test.dds
  - Refers to the colorized icon that is available should you complete the achievement.
- custom_achievement_test_not_eligible.dds
  - Refers to the icon if it is not able to be earned during that playthrough.
- custom_achievement_test_grey.dds
  - Refers to the icon if it is possible to be earned during that playthrough

Icon size and naming in vanilla. The folder `gfx/achievements/` holds 882 files: 295 base icons, 294 `_grey` and 293 `_not_eligible`, one trio per achievement token. Every one is a DDS texture of 64 by 64 px; 792 are uncompressed and 90 use DXT5. Use 64 by 64 px for the three mod icons. No `spriteType` refers to them, which agrees with the page: no `.gfx` or `.gui` file under `interface/` mentions `gfx/achievements`.

The names are the achievement token plus a suffix (`<token>.dds`, `<token>_grey.dds`, `<token>_not_eligible.dds`). `hoi4.exe` contains `gfx/achievements/`, `_grey` and `_not_eligible` as separate strings, which fits the engine building the path from the token. (unverified) Vanilla follows this rule: 293 of 293 tokens have `<token>.dds` and `<token>_grey.dds`, and 292 of 293 have `<token>_not_eligible.dds` (see the exception below). Vanilla has two irregular names that you should not copy: `sapmi_united_by_the_fire` has no matching trio but a stray `sapmi_united_by_the_fire_eligible.dds`, and `urugorn.dds` matches no achievement.

## Localization

Localization for the achievement is done in two loc keys. The suffix NAME refers to the title of the achievement and the DESC refers to the description that can be either some funny joke or how you describe to achieve the achievement.

```text
 custom_achievement_test_NAME: "Custom Achievement Title"
 custom_achievement_test_DESC: "Custom Achievement Description"
```

Vanilla's own achievement texts are not in `localisation/english/`: no `<token>_NAME` or `<token>_DESC` key exists there for tokens such as `friend_in_need`. The two-key scheme on this page therefore rests on the wiki tutorial and on a `_NAME` string that sits beside `gfx/achievements/` in `hoi4.exe`. (unverified)

The game does have interface strings that show a mod achievement's conditions in the career profile, for example `CAREER_PROFILE_MOD_ACHIEVEMENT_AVAILABLE_WHEN` ("Will be available when:") and `ACHIEVEMENT_UNLOCKED_WHEN` ("Will be earned when:"), and the front end shows `ACHIEVEMENTS_MOD_OK` ("Can get Achievements from mods!") when a mod has achievements. That the condition text is built from the `possible` and `happened` triggers is a reading of those strings. (unverified)

## Triggers

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

Checks of the trigger table above.

- `has_completed_custom_achievement` is usable in any scope. It is true when the achievement is found in the currently loaded mods and was completed in this game or in an earlier one, and its two arguments are `mod` (the `unique_id`) and `achievement` (the token). This matches the table, including the false result when the mod is not loaded.
- The console command `debug_custom_achievements` clears the completion status of mod achievements (it deletes the files on cloud storage) and reloads the mod achievement files, which makes it the way to retest an achievement. `debug_achievements` turns on achievement popups and `debug_achievements_clear` clears all achievements and user stats; the documentation marks both as not available in the release build. See [Console commands](console_commands.md).
- `show_all_ribbons` and `show_all_medals` (argument `bronze`, `silver` or `gold`) show every career-profile ribbon or medal as achieved without earning it; they concern vanilla ribbons and medals, not mod achievements.
- The related triggers `career_profile_check_ribbon` and `career_profile_check_medal` test whether a vanilla ribbon or medal is earned and collected, in any scope. In a test, `career_profile_check_ribbon` written as `= token` was refused at load with "Non assign trigger is not enclosed in {}" and its result was not usable. The accepted block form was not tested.

## References

- [1] Achievements for mods
- [2] Tutorial to design ribbons in mod achievement
- [3] Tutorial to write achievements files in your mod
