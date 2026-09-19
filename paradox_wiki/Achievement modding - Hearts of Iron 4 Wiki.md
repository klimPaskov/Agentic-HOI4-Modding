# Achievement modding

*Offline snapshot of the Hearts of Iron IV Wiki page "Achievement modding", captured 2026-09-19.*

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
  - Some common triggers not used in the code example are tag checks (with either [tag](<Triggers - Hearts of Iron 4 Wiki.md>) or [original_tag](<Triggers - Hearts of Iron 4 Wiki.md>)) or ironman checks (`is_ironman = yes`).
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

## Icon <a id="Icon"></a>

Images for achievements require three different images which are provided in `gfx/achievements`. These do not require a spriteType in interface.

- custom_achievement_test.dds
  - Refers to the colorized icon that is available should you complete the achievement.
- custom_achievement_test_not_eligible.dds
  - Refers to the icon if it is not able to be earned during that playthrough.
- custom_achievement_test_grey.dds
  - Refers to the icon if it is possible to be earned during that playthrough

## Localization <a id="Localization"></a>

Localization for the achievement is done in two loc keys. The suffix NAME refers to the title of the achievement and the DESC refers to the description that can be either some funny joke or how you describe to achieve the achievement.

```text
 custom_achievement_test_NAME: "Custom Achievement Title"
 custom_achievement_test_DESC: "Custom Achievement Description"
```

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

## References <a id="References"></a>

- [1] Achievements for mods
- [2] Tutorial to design ribbons in mod achievement
- [3] Tutorial to write achievements files in your mod

---

## Navigation

**[Modding](<Modding - Hearts of Iron 4 Wiki.md>)**

- **Documentation**: [Effects](<Effects - Hearts of Iron 4 Wiki.md>) • [Triggers](<Triggers - Hearts of Iron 4 Wiki.md>) • [Defines](<Defines - Hearts of Iron 4 Wiki.md>) • [Modifiers](<Modifiers - Hearts of Iron 4 Wiki.md>) • [List of modifiers](<List of modifiers - Hearts of Iron 4 Wiki.md>) • [Scopes](<Scopes - Hearts of Iron 4 Wiki.md>) • [Localisation](<Localisation - Hearts of Iron 4 Wiki.md>) • [On actions](<On actions - Hearts of Iron 4 Wiki.md>) • [Data structures](<Data structures - Hearts of Iron 4 Wiki.md>) • [Flags](<Data structures - Hearts of Iron 4 Wiki.md#Flags>) • [Event targets](<Data structures - Hearts of Iron 4 Wiki.md#Event_targets>) • [Country tag aliases](<Data structures - Hearts of Iron 4 Wiki.md#Country_tag_aliases>) • [Variables](<Data structures - Hearts of Iron 4 Wiki.md#Variables>) • [Arrays](<Data structures - Hearts of Iron 4 Wiki.md#Arrays>)
- **Scripting**: [AI](<AI modding - Hearts of Iron 4 Wiki.md>) • [AI focuses](<AI focuses - Hearts of Iron 4 Wiki.md>) • [Autonomous states](<Autonomy state modding - Hearts of Iron 4 Wiki.md>) • [Balances of power](<Balance of power modding - Hearts of Iron 4 Wiki.md>) • [Bookmarks/Scenarios](<Bookmark modding - Hearts of Iron 4 Wiki.md>) • [Game rules](<Bookmark modding - Hearts of Iron 4 Wiki.md#Game_rules>) • [Buildings](<Building modding - Hearts of Iron 4 Wiki.md>) • [Characters and traits](<Character modding - Hearts of Iron 4 Wiki.md>) • [Cosmetic tags](<Cosmetic tag modding - Hearts of Iron 4 Wiki.md>) • [Countries](<Country creation - Hearts of Iron 4 Wiki.md>) • [Divisions](<Division modding - Hearts of Iron 4 Wiki.md>) • [Decisions](<Decision modding - Hearts of Iron 4 Wiki.md>) • [Doctrines](<Doctrine modding - Hearts of Iron 4 Wiki.md>) • [Equipment](<Equipment modding - Hearts of Iron 4 Wiki.md>) • [Events](<Event modding - Hearts of Iron 4 Wiki.md>) • [Factions](<Faction modding - Hearts of Iron 4 Wiki.md>) • [Ideas](<Idea modding - Hearts of Iron 4 Wiki.md>) • [Ideologies](<Ideology modding - Hearts of Iron 4 Wiki.md>) • [Military industrial organizations](<Military industrial organization modding - Hearts of Iron 4 Wiki.md>) • [National focuses](<National focus modding - Hearts of Iron 4 Wiki.md>) • [Resources](<Resources modding - Hearts of Iron 4 Wiki.md>) • [Scripted GUI](<Scripted GUI modding - Hearts of Iron 4 Wiki.md>) • [Technologies and doctrines](<Technology modding - Hearts of Iron 4 Wiki.md>) • [Units](<Unit modding - Hearts of Iron 4 Wiki.md>)
- **Map**: [Map](<Map modding - Hearts of Iron 4 Wiki.md>) • [States](<State modding - Hearts of Iron 4 Wiki.md>) • [Supply areas](<Supply areas modding - Hearts of Iron 4 Wiki.md>) • [Strategic regions](<Strategic region modding - Hearts of Iron 4 Wiki.md>)
- **Graphical**: [Interface](<Interface modding - Hearts of Iron 4 Wiki.md>) • [Graphical assets](<Graphical asset modding - Hearts of Iron 4 Wiki.md>) • [Entities](<Entity modding - Hearts of Iron 4 Wiki.md>) • [Posteffects](<Posteffect modding - Hearts of Iron 4 Wiki.md>) • [Particles](<Particle modding - Hearts of Iron 4 Wiki.md>) • [Fonts](<Font modding - Hearts of Iron 4 Wiki.md>)
- **Cosmetic**: [Portraits](<Portrait modding - Hearts of Iron 4 Wiki.md>) • [Namelists](<Namelist modding - Hearts of Iron 4 Wiki.md>) • [Music](<Music modding - Hearts of Iron 4 Wiki.md>) • [Sound](<Sound modding - Hearts of Iron 4 Wiki.md>)
- **Other**: [Console commands](<Console commands - Hearts of Iron 4 Wiki.md>) • [Troubleshooting](<Troubleshooting - Hearts of Iron 4 Wiki.md>) • [Mod structure](<Mod structure - Hearts of Iron 4 Wiki.md>) • [Mods](<Mods - Hearts of Iron 4 Wiki.md>) • [Nudger](<Nudger - Hearts of Iron 4 Wiki.md>)
