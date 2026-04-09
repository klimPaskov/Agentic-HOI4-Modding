# Table of contents

- [File structure](#file-structure)
- [Coding syntax](#coding-syntax)
- [Icon](#icon)
- [Localization](#localization)
- [Triggers](#triggers)
- [References](#references)


---

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

- **unique\_id** - This is mandatory and custom to your mod. It references the name of the cloudsavefile that will store the achievements.
- **custom\_achievement/custom\_ribbon** - This is a unique identifier for your particular achievement.
- **possible** - This checks at the game's start whether a ribbon or achievement is possible to get in the playthrough. **If false at the game's start, getting the achievement will never be impossible.**
  - This is similar to `allowed` in decisions or ideas, though it is evaluated at the game's start rather than before.
  - Some common triggers not used in the code example are tag checks (with either [tag](<Triggers - Hearts of Iron 4 Wiki.md#tag>) or [original\_tag](<Triggers - Hearts of Iron 4 Wiki.md#original-tag>)) or ironman checks (`is_ironman = yes`).
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

## Icon

Images for achievements require three different images which are provided in `gfx/achievements`. These do not require a spriteType in interface.

- custom\_achievement\_test.dds
  - Refers to the colorized icon that is available should you complete the achievement.
- custom\_achievement\_test\_not\_eligible.dds
  - Refers to the icon if it is not able to be earned during that playthrough.
- custom\_achievement\_test\_grey.dds
  - Refers to the icon if it is possible to be earned during that playthrough

## Localization

Localization for the achievement is done in two loc keys. The suffix NAME refers to the title of the achievement and the DESC refers to the description that can be either some funny joke or how you describe to achieve the achievement.

```text
 custom_achievement_test_NAME: "Custom Achievement Title"
 custom_achievement_test_DESC: "Custom Achievement Description"
```

## Triggers

Achievement related triggers.

- **has_completed_custom_achievement**
  - Parameters:
    ```text
    mod = <mod ID>
    The mod where the achievement is from.
    achievement = <achievement ID>
    The name of the achievement.
    ```
  - Example:
    ```text
    has_completed_custom_achievement = {
        mod = my_mod_unique_id
        achievement = my_achievement_token
    }
    ```
  - Description: Checks if the player controlling the current scope has completed the specified custom achievement.
  - Notes:
    ```text
    The achievement (including the ID of the mod it's from) is defined within
    /Hearts of Iron IV/common/achievements/*.txt
    files. The achievement could be completed during a previous session, not necessarily the current one.
    If the mod defining the achievement is not loaded, the trigger evaluates as false.
    ```
  - Version Added: 1.12.5

## References

- [ Achievements for mods](https://forum.paradoxplaza.com/forum/index.php?threads/1544899)
- [ Tutorial to design ribbons in mod achievement](https://forum.paradoxplaza.com/forum/index.php?threads/1544902)
- [ Tutorial to write achievements files in your mod](https://forum.paradoxplaza.com/forum/index.php?threads/1544901)

**[Modding](<Modding - Hearts of Iron 4 Wiki.md>)**
