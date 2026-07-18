# Table of contents

- [Quick checklist](#quick-checklist)
- [Arguments](#arguments)
  - [Name](#name)
  - [Portraits](#portraits)
  - [Gender](#gender)
  - [Advisors](#advisors)
  - [Country leaders](#country-leaders)
  - [Unit leaders](#unit-leaders)
  - [Scientists](#scientists)
- [Full example](#full-example)
- [Instances](#instances)
- [Using in-game](#using-in-game)
  - [The special case of generate_character](#the-special-case-of-generate-character)
- [Country leader traits](#country-leader-traits)
  - [Sprite](#sprite)
- [Unit leader traits](#unit-leader-traits)
  - [Localisation](#localisation)
  - [GFX](#gfx)
  - [General arguments](#general-arguments)
  - [Modifiers and effects](#modifiers-and-effects)
  - [Selection](#selection)
  - [Example](#example)
- [References](#references)

---

*For adding operatives, see [create\_operative\_leader](<Effects - Hearts of Iron 4 Wiki.md#create-operative-leader>), as they are not characters.*

Characters are a system added in [patch 1.11](https://hoi4.paradoxwikis.com/Patch_1.11), allowing to use the same character for multiple roles, including different advisor types, country leaders and unit leaders. However, operatives are not considered characters and are still created with the [create\_operative\_leader](<Effects - Hearts of Iron 4 Wiki.md#create-operative-leader>) effect.

Characters are defined within `/Hearts of Iron IV/common/characters/*.txt` files **and need to be recruited in `/Hearts of Iron IV/history/countries/TAG*.txt` files.**. Note that while it's common to put the characters in a file with the name the same as the tag of the country, the filename does not actually matter aside from organisation and for overwriting previously-loaded files with the same name. Generic characters are typically created within `/Hearts of Iron IV/history/general/*.txt` files by using the [generate\_character](<Effects - Hearts of Iron 4 Wiki.md#generate-character>) effect, although it is to be noted that that folder is merely an effect block executed before startup, so other effects can be used there too.

Each character definition is contained within the `characters = { ... }` block, which encompasses the entirety of the file to mark them as characters. Each character is defined with a code block with the name of the character ID. For example, if the following is put within a file within the `/Hearts of Iron IV/common/characters/` folder, the blank characters my\_character\_1 and my\_character\_2 will be created:

```text
characters = {
    my_character_1 = {
    }
    my_character_2 = {
    }
}
```

Every character must be assigned to a country in that country's file in the `/Hearts of Iron IV/history/countries/` folder by using the `recruit_character = my_character` effect. Recruitment cannot take place outside of country history. **If the character is not recruited, they will never appear.** Similarly to most other folders, the game does not care about neither the filename nor the name of the characters, which is why recruitment is mandatory.

## <a id="quick-checklist"></a>Quick checklist

<a id="in-a-nutshell"></a>

- The character is created in any `/Hearts of Iron IV/common/characters/*.txt` file with no regard to the filename:
  - `name = TAG_loc_key` uses a localisation key that's defined for the English language in any `/Hearts of Iron IV/localisation/english/*_l_english.yml` file.
  - `portraits = { ... }` use spriteTypes that are defined in any `/Hearts of Iron IV/interface/*.gfx` file.

    :   While it's common practice to store images in subfolders of `/Hearts of Iron IV/gfx/` (usually `/Hearts of Iron IV/gfx/leaders/` for country or unit leaders and `/Hearts of Iron IV/gfx/interface/ideas/` for advisors), a sprite's `texturefile` can theoretically lead to any folder within the mod rather than being limited to `/Hearts of Iron IV/gfx/`.
- The character is assigned to a country using [recruit\_character](<Effects - Hearts of Iron 4 Wiki.md#recruit-character>) in any history file, usually done in the country's corresponding `/Hearts of Iron IV/history/countries/` file. This cannot be placed on the last line of the file.
- If the character isn't intended to have one of their roles at the start, then the character is created without that role, having it added with any [effect](<Effects - Hearts of Iron 4 Wiki.md>) block using [add\_country\_leader\_role](<Effects - Hearts of Iron 4 Wiki.md#add-country-leader-role>), [add\_corps\_commander\_role](<Effects - Hearts of Iron 4 Wiki.md#add-corps-commander-role>), [add\_field\_marshal\_role](<Effects - Hearts of Iron 4 Wiki.md#add-field-marshal-role>), [add\_naval\_commander\_role](<Effects - Hearts of Iron 4 Wiki.md#add-naval-commander-role>), or [add\_advisor\_role](<Effects - Hearts of Iron 4 Wiki.md#add-advisor-role>). Since `add_advisor_role` is limited in what is possible to add and what isn't, instead using `visible = { ... }` with a [flag](https://hoi4.paradoxwikis.com/Flag) is an alternative for creating advisors.

## <a id="arguments"></a>Arguments

These arguments are within the character itself.

### <a id="name"></a>Name

:   *Main article: [Localisation](<Localisation - Hearts of Iron 4 Wiki.md>)*

`name = my_character` defines a localisation key to be used to create the character's name depending on the language that is currently turned on. This will get localised in any working `/Hearts of Iron IV/localisation/english/*_l_english.yml` file, assuming the English language, as  `my_character: "My character's name"`

### <a id="portraits"></a>Portraits

Portraits fall into 3 categories: `civilian`, `army`, and `navy`. Within these categories, the `small` and `large` decide whether it gets used as an advisor portrait or as a large portrait, used for country and unit leaders. Advisor portraits can be defined in any of the 3 categories, as long as it is a small portrait, while large portraits are specific to the category.
If there is no valid portrait definition for a role, a random pair of small-large portraits will be created for the role from the possible selection for the country/cosmetic tag in the `/Hearts of Iron IV/portraits/*.txt` files; if either category has a valid sprite definition for one size but not the other, the random generation will not happen for the size where a portrait has no sprite.
An example with an advisor portrait, a country leader, and a corps commander portrait is the following:

```text
portraits = {
    civilian = {
        large = GFX_my_country_leader_portrait
        small = GFX_my_advisor_portrait
    }
    army = {
        large = GFX_my_unit_leader_portrait
    }
}
```

The portraits themselves are defined in any `/Hearts of Iron IV/interface/*.gfx` file. By default, the game uses a wide variety of files, including `/Hearts of Iron IV/dlc/dlc001_german_historical_portraits/interface/ghp_ideas_characters.gfx` (loaded in-game as `interface/ghp_ideas_characters.gfx`) or `/Hearts of Iron IV/interface/ideas.gfx`, however, editing a base game file is never necessary: a file with a higher evaluation order decided by filename (Using [ASCII character IDs](http://en.wikipedia.org/wiki/Ascii#Printable_characters) to order) will overwrite any spriteType defined in an earlier file, which the game uses for replacing DLC portraits.
**It is preferable to create a new file rather than overwriting base game files.** This is done by creating a new file and renaming it, changing the extension to .gfx from .txt. **Unhiding the file extension from the filename within the Windows file explorer is mandatory to do this** if doing it on Windows.
Simplest possible definitions of portraits are defined using `spriteType` definitions within a larger `spriteTypes = { ... }` block as such:

```text
spriteTypes = {
    spriteType = {
        name = GFX_my_advisor_portrait
        texturefile = gfx/foldername/advisor_filename.dds
    }
    spriteType = {
        name = GFX_my_country_leader_portrait
        texturefile = gfx/foldername/country_leader_filename.dds
    }
    spriteType = {
        name = GFX_my_unit_leader_portrait
        texturefile = gfx/foldername/army_leader_filename.dds
    }
}
```

The name of the spriteType has limitations: **it must begin with `GFX_`** and be made up of one word total with no whitespaces or non-[ASCII](http://en.wikipedia.org/wiki/ASCII) characters. The image file must match up with the folder and name specified in the sprite's `texturefile` with no other limits on the filename and folder location. If both restrictions are met, the sprite will work. **The file extension, hidden by default on Windows, is a part of the filename.** By default, the game stores advisor portraits in `/Hearts of Iron IV/gfx/interface/ideas/`, while country/unit leader portraits are stored in `/Hearts of Iron IV/gfx/leaders/<TAG>/`. The background used for country/unit leader portraits is found in `/Hearts of Iron IV/tools/art/portrait_leader_background.png`.

**If a portrait doesn't work and is replaced with a randomly-selected one**, there are two possible causes for this:

- The reference to the `spriteType` within the character definition is invalid. Check if the `name = ""` in the `/Hearts of Iron IV/interface/*.gfx` file is spelt in the exact same way as the portrait assignment in the character definition. This can also stem as an issue with the entire file, whether it's missing the `spriteTypes = { ... }` in the beginning or has the wrong file extension.
- The `texturefile` argument within the sprite is incorrect. Double-check not only the filename, but also the folders leading to it. Most commonly, this can be the wrong folder, omitting or having the wrong file extension in the sprite, using backslashes instead of forward slashes to separate the folders, or a regular typo in the filename.

Due to being affected by [cosmetic tags](<Cosmetic tag modding - Hearts of Iron 4 Wiki.md>), randomly-selected portraits get assigned only after country selection. Characters not assigned a valid portrait will show up as having no portrait or a default silhouette during the country selection process, only receiving a generic portrait after the game's start.

In regards to army leaders, a small portrait is also mandatory to exist as officer corps allow assigning officers as ministers. There are two primary ways to ensure about creating it:

- Manually specifying the portrait within `portraits = { ... }`.
- Creating another sprite to serve as the small portrait, which consists of the large portrait with a `_small` suffix. This also works for randomly-chosen portraits defined within `/Hearts of Iron IV/portraits/*.txt` files. If the character has `army = { large = GFX_my_unit_leader_portrait }`, then the following definition will work for creating a sprite that'll assign the minister portrait as soon as they get promoted:

```text
spriteTypes = {
    spriteType = {
        name = GFX_my_unit_leader_portrait_small
        texturefile = gfx/foldername/officer_minister_filename.dds
    }
}
```

Similarly to all other sprites, animated portraits can be done by creating a [frameAnimatedSpriteType instead of a regular spriteType](<Graphical asset modding - Hearts of Iron 4 Wiki.md#frameanimatedspritetype>).

For changing portraits by effect in game, [set\_portraits](<Effects - Hearts of Iron 4 Wiki.md#set-portraits>) is used. See [Using in-game](<Character modding - Hearts of Iron 4 Wiki.md#using-in-game>) for more.

Although using sprites for the portraits is the standard and recommended way, it is possible to define the portraits using the path directly. This is done in the same way as the texturefile of a spritetype, such as:

```text
portraits = {
    civilian = {
        large = "gfx/leaders/TAG/TAG_Leader_civilian.png"
        small = "gfx/advisors/TAG/TAG_Leader_civilian.png"
    }
    army = {
        large = "gfx/leaders/TAG/TAG_Leader_army.png"
        small = "gfx/advisors/TAG/TAG_Leader_army.png"
    }
}
```

### <a id="gender"></a>Gender

This is primarily used in some localisation namespaces to select the pronouns for the character. Possible values are `undefined`, `male`, and `female`. The default is `gender = undefined`. If the name or the portrait are not defined, gender is used to automatically generate them. In almost all respects, `gender = undefined` behaves like `gender = male`. If a character created dynamically with `generate_character` has `undefined` gender, it will be randomly assigned using FEMALE\_UNIT\_LEADER\_BASE\_CHANCE[[1]](#cite-note-1) or, if the character can exclusively be a unit leader, based on the `female` attribute of the unit leader definition.

### <a id="advisors"></a>Advisors

A character has an advisor role added by defining one within the `advisor = { ... }` block. This definition is [similar to ideas in many ways](<Idea modding - Hearts of Iron 4 Wiki.md>), but there are a few extra arguments:

`slot = political_advisor` is used to determine the [character slot](<Idea modding - Hearts of Iron 4 Wiki.md#categories>) on the country politics view that the character occupies. By default, these character slots exist in the base game:

| Internal name | Localised name | Intelligence ledger | Category | Notes |
| --- | --- | --- | --- | --- |
| <a id="political-advisor"></a>political\_advisor | Political advisor | Civilian | Laws & Government |  |
| <a id="theorist"></a>theorist | Theorist | Invalid | Research & Production | The ledger must be specified for each theorist individually as, for example, `ledger = navy`. Possible values are `army`, `air`, `navy`, `military` (Appearing on each of the prior ledgers), `civilian`, `all`, and `hidden`. |
| <a id="army-chief"></a>army\_chief | Chief of Army | Army | Military Staff |  |
| <a id="navy-chief"></a>navy\_chief | Chief of Navy | Navy | Military Staff |  |
| <a id="air-chief"></a>air\_chief | Chief of Airforce | Air | Military Staff |  |
| <a id="high-command"></a>high\_command | Military High Command | Invalid | Military Staff | The ledger must be specified for each theorist individually as, for example, `ledger = navy`. Possible values are `army`, `air`, `navy`, `military` (Appearing on each of the prior ledgers), `civilian`, `all`, and `hidden`. |

`idea_token = my_character` is the ID used for the character when treated as an idea within this particular slot. For example, [the has\_idea trigger](<Triggers - Hearts of Iron 4 Wiki.md#has-idea>) or [the show\_ideas\_tooltip effect](<Effects - Hearts of Iron 4 Wiki.md#show-ideas-tooltip>) do not expect the character ID, but the idea token of the character instead. Since it is impossible to have two of the same idea, any other character with the same idea token will be impossible to take. As not having an idea token is treated as having a null one, **this is mandatory**. Otherwise, recruiting this character will make every other advisor without an idea token specified disappear from the selection.

`can_be_fired = no` assigns the advisor as impossible to fire manually. *Note:* Prior to 1.12.8, `removal_cost = -1` could've been used for this purpose, but this does not work after the patch.

Everything else regarding advisors is identical to ideas. Commonly, the `traits = { ... }` block is used, where [each country leader trait](#country-leader-traits) that the character has is listed, separated with a whitespace, as `traits = { my_trait_1 my_trait_2 }`. These would apply modifiers on the country if the advisor is recruited, as well as adding a subtext and an icon in the bottom right of the advisor's picture.
[available, cost, and visible](<Idea modding - Hearts of Iron 4 Wiki.md#additional-arguments_2>) arguments are also common.
`on_add = { ... }` and `on_remove = { ... }` attributes use the character scope instead of the country scope as they do in ideas. In order to scope into the country that the advisor is assigned to, use [the owner scope](<Scopes - Hearts of Iron 4 Wiki.md#owner>).

Adding the same character to multiple different character slots is done by defining `advisor = { ... }` multiple times.

Example:

```text
advisor = {
    slot = theorist
    idea_token = my_character
    ledger = army
    traits = { military_theorist }      # Unspecified cost defaults to 150.
}
```

### <a id="country-leaders"></a>Country leaders

*See also: [Ideology modding](<Ideology modding - Hearts of Iron 4 Wiki.md>)*

Country leaders are defined with the `country_leader = { ... }` block. The following arguments can be used within:

`ideology = socialist` is the ideology **type** that the leader is assigned. An ideology group (such as [democratic](https://hoi4.paradoxwikis.com/Ideology#Democracy)) cannot be assigned here directly, rather ideology types are defined for each leader to decide the ideology group the party of which the character leads.
The difference between ideology types is mostly cosmetic, changing the description shown when hovering over the ideology icon and, [if defined so](<Ideology modding - Hearts of Iron 4 Wiki.md#gfx>), the icon itself. Additionally, countries with the same ruling ideology group but a different leader ideology type will have the *Same Ideology* ( **+10** Opinion) modifier towards each other, while countries with the same leader ideology type will have the *Same Ruling Party* ( **+20** Opinion) modifier towards each other.
These are the ideology types in base game across groups, defined in `/Hearts of Iron IV/common/ideologies/*.txt`:

| Internal name | Localised name | Ideology group | Notes |
| --- | --- | --- | --- |
| <a id="conservatism"></a>conservatism | Conservatism | democratic |  |
| <a id="liberalism"></a>liberalism | Liberalism | democratic |  |
| <a id="socialism"></a>socialism | Socialism | democratic |  |
| <a id="populism"></a>populism | Populism | democratic |  |
| <a id="marxism"></a>marxism | Marxism | communism |  |
| <a id="leninism"></a>leninism | Leninism | communism |  |
| <a id="stalinism"></a>stalinism | Stalinism | communism |  |
| <a id="anti-revisionism"></a>anti\_revisionism | Anti-Revisionism | communism |  |
| <a id="anarchist-communism"></a>anarchist\_communism | Anarchist Communism | communism |  |
| <a id="buddhist-socialism"></a>buddhist\_socialism | Buddhist Socialism | communism | Cannot be randomly selected. |
| <a id="nazism"></a>nazism | Nazism | fascism |  |
| <a id="gen-nazism"></a>gen\_nazism | Nazism | fascism | Generic in the sense that the description is changed to not reference Germany. |
| <a id="fascism-ideology"></a>fascism\_ideology | Fascism | fascism |  |
| <a id="falangism"></a>falangism | Falangism | fascism |  |
| <a id="rexism"></a>rexism | Rexism | fascism |  |
| <a id="emperor-fascism"></a>emperor\_fascism | Emperor Fascism | fascism | Cannot be randomly selected. |
| <a id="despotism"></a>despotism | Despotic | neutrality |  |
| <a id="oligarchism"></a>oligarchism | Oligarchic | neutrality |  |
| <a id="anarchism"></a>anarchism | Anarchism | neutrality | Cannot be randomly selected. Has a unique ideology icon. |
| <a id="moderatism"></a>moderatism | Moderatism | neutrality |  |
| <a id="centrism"></a>centrism | Centrism | neutrality |  |
| <a id="japan-militarism-ideology"></a>japan\_militarism\_ideology | Militarism | neutrality | Cannot be randomly selected. |

`traits = { my_trait_1 my_trait_2 }` is, similarly to advisors, a list of [country leader traits](#country-leader-traits) that the country leader has, which would apply modifiers on the country if the character is leading the country.

`expire = 1949.1.1` marks the date at which the leader expires. If the **start** date is after this amount, they cannot be used, even if recruited. Optional.

`id = 100` is a leftover from the pre-NSB country leader system, making the leader have the specified ID for the [has\_country\_leader trigger](https://hoi4.paradoxwikis.com/Conditions#has_country_leader). Unnecessary and should be omitted, use character specific triggers instead.

`desc = MY_LEADER_DESCRIPTION` is the localisation key that gets used for the leader's description depending on the currently turned on language. This **must** be a localisation key, a directly-defined description will not appear in-game.

Example:

```text
country_leader = {
    ideology = centrism
    desc = MY_LEADER_DESCRIPTION
}
```

If a country leader is recruited in the country history file, then they will be attempted to be placed as the leader of their parties. That will fail if there is already a suitable leader for the party. This can happen in two circumstances:

- A different character is already recruited as the party leader. In other words, in case of overlap between political parties in different characters, the game will place the first-recruited one as the party leader.
- A randomly-generated character is forced to be created prior to recruitment. This can be caused by a different character being fired from their slot as the political party leader (such as if the leader needs to change between start dates) or, in some cases, by `set_politics = { ... }`. It's best to recruit characters before setting the political information for the country.
- In case of differences between startdates, use the [promote\_character](<Effects - Hearts of Iron 4 Wiki.md#promote-character>) effect to ensure the new character becomes leader.

### <a id="unit-leaders"></a>Unit leaders

Unit leaders include corps commanders, field marshals, and admirals. Respectively, these use `corps_commander = { ... }`, `field_marshal = { ... }`, and `navy_leader = { ... }` blocks for definition, which are similar in structure.

`traits = { my_trait_1 my_trait_2 }` is the list of [unit leader traits](#unit-leader-traits) assigned to the unit leader, defined in `/Hearts of Iron IV/common/unit_leader/*.txt`.

`skill = 4` is the overall skill level of the unit leader. In addition, specific skills also can be set, with `attack_skill = 3` and `defense_skill = 2` being shared across all unit leaders, `planning_skill = 5` and `logistics_skill = 6` being only for army leaders, and `coordination_skill = 3` and `maneuvering_skill = 5` being only for navy leaders. To put what each skill level grants to the leader in more detail:

| Internal name | Localised name | Unit leader type | Effect per level |
| --- | --- | --- | --- |
| <a id="skill"></a>skill | Skill | Any unit leader | Army leaders: Nothing  Navy leaders: +5% hit chance, +2% fleet coordination. |
| <a id="attack-skill"></a>attack\_skill | Attack | Any unit leader | Army leaders: +2.5% offense  Navy leaders: +5% damage |
| <a id="defense-skill"></a>defense\_skill | Defense | Any unit leader | Army leaders: +2.5% defense  Navy leaders: +5% defense |
| <a id="planning-skill"></a>planning\_skill | Planning | Army leaders only | +5% planning speed  +2% max bonus from planning |
| <a id="logistics-skill"></a>logistics\_skill | Logistics | Army leaders only | -2.5% supply consumption |
| <a id="maneuvering-skill"></a>maneuvering\_skill | Maneuvering | Navy leaders only | +2.5% positioning  +1% naval retreat speed |
| <a id="coordination-skill"></a>coordination\_skill | Coordination | Navy leaders only | +2% fleet coordination |

`legacy_id = 100` is a leftover from the pre-NSB country leader system, making the leader have the specified ID for the [has\_id trigger](https://hoi4.paradoxwikis.com/Conditions#has_id), the [has\_unit\_leader trigger](https://hoi4.paradoxwikis.com/Conditions#has_unit_leader), and elsewhere. Unnecessary and should be omitted, use character specific triggers instead.

`visible = { ... }` is a trigger block that the character must fulfill in order for the unit leader to be visible and possible to pick. Additionally, country-scoped triggers are also supported, which'll assume the country that recruited the character. Unnecessary in most cases, as it's possible to [create the unit leader role](<Effects - Hearts of Iron 4 Wiki.md#add-corps-commander-role>) within an effect block mid-game.

Examples:

```text
field_marshal = {
    traits = { my_trait_1 my_trait_2 }
    skill = 10
    attack_skill = 8
    defense_skill = 1
    planning_skill = 10
    logistics_skill = 10
}
corps_commander = {
    skill = 1
    attack_skill = 2
    defense_skill = 3
    planning_skill = 4
    logistics_skill = 5
}
navy_leader = {
    skill = 3
    attack_skill = 1
    defense_skill = 3
    maneuvering_skill = 5
    coordination_skill = 4
    legacy_id = 10
    visible = { has_stability > 0.3 }
}
```

### <a id="scientists"></a>Scientists

To give the character the role of a scientist, the `scientist` block can be added. It's structure is in principle the same as for `corps_commander` etc. They use scientist traits instead of commander traits (as expected), and instead of merely having a skill level they assign a skill level to one of the specializations (four types in the basegame, but there might be more types added by some mods). While adding more than one specialization doesn't produce an error, any specializations beyond the first one are ignored by the game.

**Known bug:** The description of scientists doesn't show up.

```text
scientist = {
    traits = { scientist_trait_rocketry_specialist scientist_trait_bright }
    skills = {
        specialization_air = 3
    }

    desc = my_scientist_desc
    visible = {
        owner = {
            has_country_flag = TAG_show_this_scientist
        }
    }
}
```

## <a id="full-example"></a>Full example

Within any `/Hearts of Iron IV/common/characters/*.txt` file

```text
characters = {
    UKR_nestor_makhno = {
        name = UKR_nestor_makhno
        portraits = {
            civilian = {
                large = "GFX_portrait_UKR_nestor_makhno"
            }
        }
        country_leader = {
            ideology = anarchist_communism
            traits = { agrarian_activist }
            desc = UKR_nestor_makhno_desc
        }
    }
    SOV_georgy_zhukov = {
        name = SOV_georgy_zhukov
        portraits = {
            army = {
                small = "GFX_idea_georgy_zhukov"
                large = "GFX_portrait_SOV_georgy_zhukov"
            }
        }
        corps_commander = {
            traits = { media_personality armor_officer war_hero winter_specialist }
            skill = 5
            attack_skill = 5
            defense_skill = 2
            planning_skill = 4
            logistics_skill = 5
            legacy_id = 410
            visible = { NOT = { has_character_flag = SOV_exiled_flag } }
        }
        advisor = {
            slot = theorist
            idea_token = georgy_zhukov
            ledger = army
            allowed = { original_tag = SOV } # Optional, doesn't change anything.
            available = {
                has_completed_focus = SOV_positive_heroism
            }
            traits = { mass_assault_expert }
        }
    }
}
```

Within any `/Hearts of Iron IV/history/countries/*.txt` file:

```text
recruit_character = UKR_nestor_makhno
recruit_character = SOV_georgy_zhukov
```

## <a id="instances"></a>Instances

It is also possible for a character to have a different definition depending on set preconditions checked at the game's start. This is done with `instance = { ... }`. The character will take on every instance where `allowed = { ... }` is true **at the game's start**. For example, this can be used to make the character to have a different role depending on which DLCs the player has enabled:

```text
my_character = {
    instance = {
        allowed = { has_dlc = "Poland: United and Ready" }
        advisor = {
            slot = political_advisor
            traits = { polish_person }
        }
    }
    instance = {
        allowed = { NOT = { has_dlc = "Poland: United and Ready" } }
        corps_commander = {
            skill = 10
            attack_skill = 10
            defense_skill = 10
            planning_skill = 10
            logistics_skill = 10
            traits = { not_polish_person }
        }
    }
}
```

Due to its purpose, each instance must have an `allowed` block and the character must have multiple instances to work properly. If the character only has a single pre-determined state, then the instance should be omitted.

## <a id="using-in-game"></a>Using in-game

*See also: [Effect § Character scope](<Effects - Hearts of Iron 4 Wiki.md#character-scope>)*

*See also: [Effect § Characters](<Effects - Hearts of Iron 4 Wiki.md#characters>)*

After being created, a character is mandatory to be assigned to a country. Since the filenames are only used for organisation purposes, this is done within the country's history file (in `/Hearts of Iron IV/history/countries/`) as such:

```text
recruit_character = TAG_character_name
```

**If this is not done, the character cannot ever be used**. The recruitment will fail if the effect is placed as the last line in the file: there must be at least one line after the recruitment, even if it's empty.

For characters with a country leader role, the first character recruited from each ideology group will start as country leader for the party of that ideology. For example, let's say that the country history file has the following:

```text
recruit_character = TAG_marxist_leader      # 'ideology = marxism', falls under communism
recruit_character = TAG_stalinist_leader    # 'ideology = stalinism', falls under communism
recruit_character = TAG_liberal_leader      # 'ideology = liberalism', falls under democratic
recruit_character = TAG_conservative_leader # 'ideology = conservatism', falls under democratic
recruit_character = TAG_centrist_leader     # 'ideology = centrism', falls under neutrality (non-aligned)
recruit_character = TAG_despotic_leader     # 'ideology = despotism', falls under neutrality (non-aligned)
recruit_character = TAG_falangist_leader    # 'ideology = falangism', falls under fascism
recruit_character = TAG_rexist_leader       # 'ideology = rexism', falls under fascism
set_politics = {                            # Since set_politics forces a leader to come to power, this will create
    ruling_party = democratic               # a randomly-generated character if no country leader has yet been recruited.
    elections_allowed = no                  # Due to this, set_politics must be placed after character recruitment.
}
```

In this case, TAG\_liberal\_leader will be the leader of the democratic ideology/party and thus the starting country leader. TAG\_marxist\_leader will be the leader of the communist party, TAG\_centrist\_leader will be the leader of the non-aligned party and TAG\_falangist\_leader will be the leader of the fascist party.

The characters TAG\_stalinist\_leader, TAG\_conservative\_leader, TAG\_despotic\_leader and TAG\_rexist\_leader do not start as leaders in this case and will remain only as possible leaders to be used later on. For this reason, it is not necessary for country leader characters to be defined without the role, as long as their ideology group has another character as leader.

Characters that are recruited but not currently the leader of their party, such as the TAG\_conservative\_leader above can later be promoted to leader using the [promote\_character](<Effects - Hearts of Iron 4 Wiki.md#promote-character>) effect. Retiring the previous leader or removing their role is not necessary. Example:

```text
#Used in character scope
TAG_conservative_leader = {
    promote_character = yes #when the character has only one leader role, yes is enough
}

TAG_conservative_leader = {
    promote_character = conservatism #if the character has more than one leader role, needs to specify the ideology
}

#Used in country scope
promote_character = TAG_conservative_leader #short version can be used when the character has only one leader role

promote_character = { #if the character has more than one leader role, needs to specify the ideology
    character = TAG_conservative_leader
    ideology = conservatism
}
```

If an ideology group is intended to start with a generic country leader, but get a new character country leader later on, it's possible to define this leader as an initially empty character, such as the following:

```text
characters = {
    TAG_new_leader = {
        name = TAG_new_leader
        gender = female
        portraits = {
            civilian = {
                large = GFX_portrait_TAG_new_leader
            }
        }
    }
}
```

**This character should still be recruited with `recruit_character = TAG_new_leader`**
After doing so, this character can be *given* a role within an effect block using the effect [add\_country\_leader\_role](<Effects - Hearts of Iron 4 Wiki.md#add-country-leader-role>). For example, this completion reward for a focus makes a character lead the democratic party:

```text
completion_reward = {
    add_country_leader_role = {
        character = TAG_new_leader  # Must be recruited
        promote_leader = yes  # Makes the character be promoted to leader of the party
        country_leader = {
            ideology = conservatism
            traits = { my_trait }
        }
    }
}
```

If a character is intended to be removed from the game "permanently", as in death or retirement, [retire\_character](<Effects - Hearts of Iron 4 Wiki.md#retire-character>) (country scope) and [retire](<Effects - Hearts of Iron 4 Wiki.md#retire>) (character scope) can be used. This is basically a reverse effect of `recruit_character`, the character will be dismissed from the country completely. However, this effect is not actually permanent, the character can be re-added to the game using the effect [set\_nationality](<Effects - Hearts of Iron 4 Wiki.md#set-nationality>) and all their roles will be retained. For scoping purposes, the character is located in the same country as before.

- Removing a character is not always needed. For example when another character is set to become country leader, using the effect `promote_character` is enough already as the old leader will not affect it in any way. The effect [remove\_country\_leader\_role](<Effects - Hearts of Iron 4 Wiki.md#remove-country-leader-role>) can also be used the remove the leader role from a character, and other roles will also have effects that can be used.

It is not recommended to use effects such as `kill_country_leader`, `retire_country_leader`, `kill_ideology_leader` and `retire_ideology_leader`, as these effects will affect *any character* that is currently the leader without further confirmation, instead of being able to specify who should be removed.

- When dealing with characters, `kill_country_leader` and `kill_ideology_leader` will behave exactly the same way as `retire_character`, meaning the character is dismissed and can be re-added with `set_nationality`.
- As for `retire_country_leader` and `retire_ideology_leader`, these effects will only remove the leader from the "line of succession" of their political party, meaning the next character recruited will be promoted to leader of the party. The old leader will not be removed and will retain all their roles, being able to come back using `promote_character`.

Other effects on this topic include [add\_corps\_commander\_role](<Effects - Hearts of Iron 4 Wiki.md#add-corps-commander-role>), [add\_field\_marshal\_role](<Effects - Hearts of Iron 4 Wiki.md#add-field-marshal-role>), [add\_naval\_commander\_role](<Effects - Hearts of Iron 4 Wiki.md#add-naval-commander-role>), [add\_advisor\_role](<Effects - Hearts of Iron 4 Wiki.md#add-advisor-role>), and others.

Advisor roles created with `add_advisor_role` cannot contain script, such as `visible = { ... }`, `available = { ... }`, `on_add = { ... }`. It is recommended instead to use `visible = { ... }` with an appropriate [trigger](<Triggers - Hearts of Iron 4 Wiki.md>) for creating advisors that should not be visible at game start. For the same reason, it is not recommended to use `remove_advisor_role` on advisors that contain script, as all the triggers and effects will be lost and cannot be added back if needed later on. Usage of these effects should be reserved for characters with more static roles, as in have no conditions or other script.

In order to hire an advisor to be within their proper slot, [activate\_advisor](<Effects - Hearts of Iron 4 Wiki.md#activate-advisor>) is used as such:

```text
activate_advisor = TAG_character_name_token
```

Where `TAG_character_name_token` is the `idea_token` defined in the character's advisor role. As an effect, this works within country history files as well.

Portraits of characters, both small and large, can be changed later in game using the effect [set\_portraits](<Effects - Hearts of Iron 4 Wiki.md#set-portraits>), which works both in character scope and country scope. The same rules as on [Portraits](<Character modding - Hearts of Iron 4 Wiki.md#portraits>) apply. For example:

```text
TAG_New_Leader = {
    set_portraits = { #in character scope
        civilian = {
            large = "gfx/leaders/TAG/TAG_New_Leader.png" #just like the character definition, supports both sprites and direct path
            small = "gfx/advisors/TAG/TAG_New_Leader.png"
        }
    }
}
set_portraits = {
    character = TAG_New_Leader #in country scope, specify the character
    civilian = {
        large = GFX_Large_Civilian_Portrait_TAG_New_Leader #just like the character definition, supports both sprites and direct path
        small = GFX_Small_Civilian_Portrait_TAG_New_Leader
    }
}
```

### <a id="the-special-case-of-generate-character"></a>The special case of generate\_character

The effect [generate\_character](<Effects - Hearts of Iron 4 Wiki.md#generate-character>) is used to create generic characters, such as the generic advisors present in the base game. **These have limitations and should not be used as a replacement for regular characters.** Example:

```text
every_country = {
    limit = { OR = { original_tag = KOR original_tag = SER original_tag = ICE } }
    generate_character = { #create + recruit
        token_base = army_chief_defensive_1 # Mandatory, character token will be token_base
        name = "Character's Name" # Optional, no name provided means random name for each generated character
        # Then whatever you would put when writing character
        advisor = {
            idea_token = ac # Full idea token will be token_base_idea_token (to ensure unicity). In this case will be army_chief_defensive_1_ac. Optional, slot will be used if missing, as in army_chief_defensive_1_army_chief.
            slot = army_chief
            traits = { army_chief_defensive_1 }
        }
    }
}
```

Although this effect is usually known as being exclusive to history files, it is possible to create the characters mid-game:

- First step is creating the full effect in the history file, such as the example above. This will be used as a "template".
- For the in-game effect, `generate_character = { token_base = character_token_base }` is used.

The first step recruiting the character beforehand can be bypassed by adding a false trigger in the code, such as the following:

```text
every_possible_country = {
    limit = {
        always = no
    }
    generate_character = {
        token_base = generic_guy
        name = "Advisor Clone"
        advisor = {
            slot = political_advisor
            idea_token = pol # Full idea token will be generic_guy_pol
            traits = { my_trait }
        }
    }
}
```

Due to the always false trigger, the character will not be recruited by any country, but the template will still work. This character can be added to the game later with the effect:

```text
generate_character = { token_base = generic_guy }
```

**The effect will fail if the "template" does not exist in the history files.** Using the full effect directly mid-game will not work.

## <a id="country-leader-traits"></a>Country leader traits

*"Trait modding" redirects here. For unit leader traits, see [§ Unit leader traits](#unit-leader-traits)*

Despite their name, country leader traits can be applied to either advisors, ideas, or country leaders. Country leader traits are defined in any `/Hearts of Iron IV/common/country_leader/*.txt` file.
 The traits' modifiers will apply to the country that has the character or idea on which the trait is applied.
Traits in the file are contained within the `leader_traits = { ... }` block, and will not work otherwise.

An example trait file is defined as following:

```text
leader_traits = {
    my_trait = {
        random = no
        sprite = 1
        political_power_gain = 0.1
        equipment_bonus = {
            train_equipment = {
                build_cost_ic = 0.05
                reliability = 0.15
            }
        }
        ai_will_do = {
            base = 2
        }
        command_cap = @tier1
    }
}
```

Within country leader traits, these are the arguments that are used:

- `random = no` decides whether there's a possibility that a randomly-created country leader can appear with this trait.
- `sprite = 1` decides the sprite that appears in the bottom left of an advisor that has this trait. This must be a number, which corresponds with the frame of the `GFX_idea_traits_strip` spriteType, defined within `/Hearts of Iron IV/interface/ideas.gfx` by default. Optional.
- `ai_will_do` is a [MTTH block](<AI modding - Hearts of Iron 4 Wiki.md#ai-will-do>) that modifies the chance for AI to pick an advisor or idea that has this trait assigned. 1 by default.

- `command_cap` determines the price of the political advisor to which this trait is assigned in [Command power](https://hoi4.paradoxwikis.com/Command_power). Mainly applied to military advisors.

Additionally, [special modifier types that can be used in ideas](<Idea modding - Hearts of Iron 4 Wiki.md#modifiers>): `targeted_modifier = { ... }` and `equipment_bonus = { ... }` - can be used within traits alongside regular modifiers, in the exact same manner as within ideas. The same does not apply to `research_bonus = { ... }` and `rule = { ... }`, however.

Localisation is defined by using the trait's name as a localisation key within any localisation file, with an entry as  `my_trait: "My trait"`.

### <a id="sprite"></a>Sprite

*See also: [Sprite overview](https://hoi4.paradoxwikis.com/Template:Sprite_overview)*

The `sprite = 1` argument decides shown on the paper for the advisor when an advisor has this. This uses the `GFX_idea_traits_strip` [spriteType](https://hoi4.paradoxwikis.com/SpriteType), which can be defined in any `/Hearts of Iron IV/interface/*.gfx` file, by default `ideas.gfx`. However, it's generally better to avoid overlap in files from the base game to decrease the needed amount of work to make the mod be up to date. Instead, it's possible to overwrite the sprite in a new file.
In particular, in case of there being defined several spriteTypes with the same name, the game picks the one that was evaluated later. The filename is used to order the files for the evaluation, using [ASCII order](http://en.wikipedia.org/wiki/ASCII#Printable_characters), so a file later in that order may contain an overriding sprite. For example, it may be `interface/xyz_override.gfx`, since "x" is later than "i" in the ASCII alphabet. This may be its contents:

```text
spriteTypes = {
	SpriteType = {
		name = "GFX_idea_traits_strip"
		texturefile = "gfx/interface/ideas/idea_traits_strip.dds"
		noOfFrames = 18 # Base game contains this many as of 1.12
	}
}
```

`noOfFrames` decides on the number of sections that the file is separated into, always horizontally. For example, with 3, it'd be divided into the left third (frame 1), middle third (frame 2), and the right third (frame 3). This is used in the `sprite` of the trait: `sprite = 1` would pick frame 1 and thus the left third, while `sprite = 3` will pick the right third.

In particular, these are the important notes:

- **It is mandatory to change the noOfFrames** if the image is changed from the base game's default
- **Base game's `ideas.gfx` should not exist within the mod** in most cases. If the image for the trait strip is edited, it will not break the mod as much upon game updates to keep it copied, however any newly-added sprites will become unusable unless manually ported over, which can be avoided by just using a different file for new sprites.

## <a id="unit-leader-traits"></a>Unit leader traits

Units leader traits are defined in any `/Hearts of Iron IV/common/unit_leader/*.txt` file, possible to assign to unit leader characters of any type as well as operatives. Each one is defined within the `leader_traits = { ... }` block as a separate entry with the name of the trait's ID.

### <a id="localisation"></a>Localisation

Localisation is defined by using the trait's name as a localisation key within any localisation file, with an entry as  `my_trait: "My trait"`. A description can be added by appending `_desc` to the end as `my_trait_desc: "My description"`.

### <a id="gfx"></a>GFX

The picture is defined in any `/Hearts of Iron IV/interface/*.gfx` file as a spriteType with the name of `GFX_trait_<trait's name>`. As an example with a trait of the name `not_polish_person`, a sprite definition with the name of `GFX_trait_not_polish_person` will be used. The `/Hearts of Iron IV/interface/*.gfx` file containing the sprite will have these contents:

```text
spriteTypes = {
    spriteType = {
        name = GFX_trait_not_polish_person
        texturefile = gfx/foldername/filename.dds
    }
}
```

### <a id="general-arguments"></a>General arguments

| Argument | Value type | Example | Effects | Notes |
| --- | --- | --- | --- | --- |
| <a id="type"></a>type | Type(s) | `type = corps_commander``type = { land navy }` | Assigns a type to the trait, which gets used to assign which characters are able to receive it. | The types include `all`, `land`, `navy`, `operative`, `corps_commander`, and `field_marshal` |
| <a id="trait-type"></a>trait\_type | Trait type | `trait_type = assignable_trait` | Assigns a type to the trait, which gets used to assign where it's positioned on the user interface, as well as deciding if and when it's possible to assign. | The types include `basic_trait` (for operatives), `personality_trait`, `assignable_trait`, `basic_terrain_trait`, `assignable_terrain_trait`, `status_trait`, and `exile` |
| <a id="show-in-combat"></a>show\_in\_combat | Boolean | `show_in_combat = yes` | Makes this specified trait show up in the combat menu among other bonuses. |  |
| <a id="allowed"></a>allowed | Triggers | `allowed = { FROM = { tag = POL } }` | Triggers that are checked when trying to assign the trait to a unit leader, making it fail to assign if false. Checked in the scope of the unit leader. | FROM is the country that recruited the character. |
| <a id="ai-will-do"></a>ai\_will\_do | [MTTH block](<AI modding - Hearts of Iron 4 Wiki.md#ai-will-do>) | `ai_will_do = { base = 3 modifier = { FROM = { tag = POL } } }` | Decides the weight that AI has for picking this trait. | A weight of 0 will result in AI never picking it. |
| <a id="new-commander-weight"></a>new\_commander\_weight | [MTTH block](<AI modding - Hearts of Iron 4 Wiki.md#ai-will-do>) | `new_commander_weight = { base = 0 }` | Decides the weight that the trait has for new randomly-generated unit leaders. | A weight of 0 will result in it never appearing for randomly-generated unit leaders. Only can be defined for traits with the personality\_trait type. |
| <a id="slot"></a>slot | [Character slot](#political-advisor) | `slot = army_chief` | Decides which advisor slot gets used by the [officer corps](https://hoi4.paradoxwikis.com/Officer_corps) role that can be assigned to this unit leader. |  |
| <a id="specialist-advisor-trait"></a>specialist\_advisor\_trait | [Country leader trait](#country-leader-traits) | `specialist_advisor_trait = my_trait` | Creates a specialist [officer corps](https://hoi4.paradoxwikis.com/Officer_corps) role that can be assigned to this unit leader using the specified advisor trait as the base. |  |
| <a id="expert-advisor-trait"></a>expert\_advisor\_trait | [Country leader trait](#country-leader-traits) | `expert_advisor_trait = my_trait` | Creates a expert [officer corps](https://hoi4.paradoxwikis.com/Officer_corps) role that can be assigned to this unit leader using the specified advisor trait as the base. |  |
| <a id="genius-advisor-trait"></a>genius\_advisor\_trait | [Country leader trait](#country-leader-traits) | `genius_advisor_trait = my_trait` | Creates a genius [officer corps](https://hoi4.paradoxwikis.com/Officer_corps) role that can be assigned to this unit leader using the specified advisor trait as the base. |  |
| <a id="unit-type"></a>unit\_type | `type = <sub-unit type>` | `unit_type = { type = infantry type = militia }` | Limits the selection of units on which the modifiers can apply on to those that have the sub-unit in a composition. | Sub-units are defined within `/Hearts of Iron IV/common/units/*.txt` files. In order for it to apply those that are majority-made out of a sub-unit, [division\_has\_majority\_template](<Triggers - Hearts of Iron 4 Wiki.md#division-has-majority-template>) can be used in [unit\_trigger](#unit-trigger). |
| <a id="unit-trigger"></a>unit\_trigger | Triggers | `unit_trigger = { division_has_majority_template = camelry owner = { neutrality > 0.5 } }` | Applies a division-scoped trigger block that must be met for the unit to be modified. |  |

### <a id="modifiers-and-effects"></a>Modifiers and effects

These arguments are for the modifiers that the trait gives to the unit leader, whether it's the modifiers themselves or something related to them, as well as effects executed related to the trait.

| Argument | Value type | Example | Effects | Notes |
| --- | --- | --- | --- | --- |
| <a id="modifier"></a>modifier | Modifiers | `modifier = { planning_speed = 0.2 urban = { movement = 0.1 } }` | Assigns the [modifiers](<Modifiers - Hearts of Iron 4 Wiki.md>) that the trait grants to the divisions that the unit leader leads. | Possible to specify the terrain by scoping into it. Terrain types are defined in `/Hearts of Iron IV/common/terrain/*.txt`. |
| <a id="non-shared-modifier"></a>non\_shared\_modifier | Modifiers | `non_shared_modifier = { experience_gain_factor = 0.3 }` | Assigns the [modifiers](<Modifiers - Hearts of Iron 4 Wiki.md>) that the trait grants to the unit leader themselves. | While in theory identical to [the prior modifier](#modifier), this has a different tooltip, so it shows up differently in-game. |
| <a id="corps-commander-modifier"></a>corps\_commander\_modifier | Modifiers | `corps_commander_modifier = { max_commander_army_size = 3 }` | Assigns the [modifiers](<Modifiers - Hearts of Iron 4 Wiki.md>) that the trait grants to the army leader when in the role of a corps commander, i.e. leading units directly rather than leading other generals. | If a field marshal is assigned to lead divisions directly rather than other generals, this will apply on them. |
| <a id="field-marshal-modifier"></a>field\_marshal\_modifier | Modifiers | `field_marshal_modifier = { supply_consumption_factor = 0.5 }` | Assigns the [modifiers](<Modifiers - Hearts of Iron 4 Wiki.md>) that the trait grants to the army leader when in the role of a field marshal, i.e. leading other generals that lead divisions. | If a field marshal is assigned to lead divisions directly rather than other generals, this will *not* apply on them. |
| <a id="sub-unit-modifiers"></a>sub\_unit\_modifiers | Modifiers | `sub_unit_modifiers = { artillery_brigade = { max_strength = 0.1 } }` | Assigns the [modifiers](<Modifiers - Hearts of Iron 4 Wiki.md>) that the trait grants to the division brigades that make up the divisions that the army leader leads or, similarly, ships that make up the fleet that the navy leader leads. | Brigades are defined in `/Hearts of Iron IV/common/units/*.txt`. What's used in the definition as arguments is possible to apply as a multiplicatory sub-unit modifier. |
| <a id="unit-leader-skill"></a><skill type> | Integer | `attack_skill = 2` | Adds a flat bonus to the specified skill. | [The list of skills defined for unit leaders earlier in the page](#skill) |
| <a id="unit-leader-skill-factor"></a><skill type>\_factor | Percentual | `defense_skill_factor = 1` | Adds a multiplicatory bonus to the specified skill. `1` would add 100%, doubling it, for example. | [The list of skills defined for unit leaders earlier in the page](#skill) |
| <a id="override-effect-tooltip"></a>override\_effect\_tooltip | Localisation key | `override_effect_tooltip = my_effect_tt` | Hides the effects of the trait, replacing the tooltip with the value of this localisation key. | English localisation is defined in any `/Hearts of Iron IV/localisation/english/*_l_english.yml` file. Similarly for other languages. |
| <a id="custom-effect-tooltip"></a>custom\_effect\_tooltip | Localisation key | `custom_effect_tooltip = my_effect_tt` | Appends the value of this localisation key to the tooltip showing the effects of the trait. | English localisation is defined in any `/Hearts of Iron IV/localisation/english/*_l_english.yml` file. Similarly for other languages. |
| <a id="enable-ability"></a>enable\_ability | Ability | `enable_ability = my_ability` | Enables an ability that can be used by the unit leader in combat. | Abilities are defined in `/Hearts of Iron IV/common/abilities/*.txt` |
| <a id="on-add"></a>on\_add | Effects | `on_add = { promote_leader = yes }` | Defines the effects that would be executed on the unit leader when the trait is added. |  |
| <a id="on-remove"></a>on\_remove | Effects | `on_remove = { remove_unit_leader = yes }` | Defines the effects that would be executed on the unit leader when the trait is removed. |  |
| <a id="daily-effect"></a>daily\_effect | Effects | `daily_effect = { gain_xp = 1 }` | Defines the effects that would be executed on the unit leader every day if they have the trait. |  |

### <a id="selection"></a>Selection

These arguments are related to the menu for selecting traits. This includes experience. If the trait is manually assigned only, these can be omitted.

| Argument | Value type | Example | Effects | Notes |
| --- | --- | --- | --- | --- |
| <a id="mutually-exclusive"></a>mutually\_exclusive | Trait | `mutually_exclusive = my_trait` | Makes the specified trait mutually exclusive with the other trait, making it impossible to pick if that one was selected and drawing the arrows in the menu. | Both traits require defining this to work properly. |
| <a id="parent"></a>parent | Trait | `parent = my_trait` | Makes the specified trait be marked as a parent, making it be required to pick the current trait and drawing the line in the menu. | Multiple parents can be specified by defining `parent = my_trait_2` several times. |
| <a id="num-parents-needed"></a>num\_parents\_needed | Integer | `num_parents_needed = 3` | Sets the required amount of parents needed to select the trait. | If omitted or set to `-1`, then assumes that all parents are necessary. |
| <a id="gui-row"></a>gui\_row | Integer | `gui_row = 3` | Sets the row on which the trait is located. | If omitted or set to `-1`, then the trait does not appear in the unlockable trait tree. Starts at 0. |
| <a id="gui-column"></a>gui\_column | Integer | `gui_column = 3` | Sets the column on which the trait is located. | If omitted or set to `-1`, then one is automatically picked [depending on the trait\_type](#trait-type). |
| <a id="prerequisites"></a>prerequisites | Triggers | `prerequisites = { defense_skill_level > 3 }` | Triggers that must be met in order for assigning the trait to be possible. | Checked in the unit leader scope. |
| <a id="custom-prerequisite-tooltip"></a>custom\_prerequisite\_tooltip | Localisation key | `custom_prerequisite_tooltip = my_prerequisite_tt` | Changes the tooltip of the conditions required for picking the trait to the following localisation key. Useful if a trigger within has no tooltip. | English localisation is defined in any `/Hearts of Iron IV/localisation/english/*_l_english.yml` file. Similarly for other languages. |
| <a id="cost"></a>cost | Decimal | `cost = 1500` | The experience required in order to assign this trait to a unit leader. |  |
| <a id="gain-xp"></a>gain\_xp | Triggers | `gain_xp = { is_amphibious_invasion = yes }` | Triggers that must be met in order to gain experience that'd make assigning this trait possible. | Checked in the [combatant](https://hoi4.paradoxwikis.com/Conditions#Combat) scope. |
| <a id="gain-xp-leader"></a>gain\_xp\_leader | Triggers | `gain_xp_leader = { num_units > 10 }` | Triggers that must be met in order to gain experience that'd make assigning this trait possible. | Checked in the unit leader scope. |
| <a id="gain-xp-on-spotting"></a>gain\_xp\_on\_spotting | Decimal | `gain_xp_on_spotting = 7` | The amount of experience gained when the admiral spots an enemy fleet. |  |
| <a id="custom-gain-xp-trigger-tooltip"></a>custom\_gain\_xp\_trigger\_tooltip | Localisation key | `custom_gain_xp_trigger_tooltip = my_prerequisite_tt` | Changes the tooltip of the conditions required for gaining experience for the trait to the following localisation key. Useful if a trigger within has no tooltip. | English localisation is defined in any `/Hearts of Iron IV/localisation/english/*_l_english.yml` file. Similarly for other languages. |
| <a id="trait-xp-factor"></a>trait\_xp\_factor | Triggers | `trait_xp_factor = { my_trait = 0.1 }` | Modifies the amount of experience gained towards other traits if the unit leader has this trait. | 0.1 would mean that the unit leader gains 10% more experience, not that it gains 10% as much. |

### <a id="example"></a>Example

```text
leader_traits = {
    my_trait_1 = {
        type = { land navy }
        trait_type = personality_trait
        non_shared_modifier = {
            promote_cost_factor = -0.5
        }
        attack_skill_factor = 1
        new_commander_weight = {
            factor = 0  # Scripted starting leaders only
        }
    }
    my_trait_2 = {
        type = land
        gain_xp = {
            num_units > 10
        }
        cost = 3000
        field_marshal_modifier = {
            org_loss_when_moving = -0.30
        }

        slot = army_chief
        specialist_advisor_trait = army_chief_trait_1
        expert_advisor_trait = army_chief_trait_2
        genius_advisor_trait = army_chief_trait_3
        ai_will_do = {
            factor = 10
        }
        trait_type = assignable_trait
        gui_row = 10
    }
}
```

## <a id="references"></a>References

1. [↑](#cite-ref-1) `NDefines.NCountry.FEMALE_UNIT_LEADER_BASE_CHANCE = { 0.5, 0.5, 0.5, 0.5, 0.5, 0.5 }`

**[Modding](<Modding - Hearts of Iron 4 Wiki.md>)**

|  |  |
| --- | --- |
| Documentation | [Effects](<Effects - Hearts of Iron 4 Wiki.md>) • [Triggers](https://hoi4.paradoxwikis.com/Conditions) • [Defines](<Defines - Hearts of Iron 4 Wiki.md>) • [Modifiers](<Modifiers - Hearts of Iron 4 Wiki.md>) • [List of modifiers](https://hoi4.paradoxwikis.com/List_of_modifiers) • [Scopes](<Scopes - Hearts of Iron 4 Wiki.md>) • [Localisation](<Localisation - Hearts of Iron 4 Wiki.md>) • [On actions](<On actions - Hearts of Iron 4 Wiki.md>) • [Data structures](<Data structures - Hearts of Iron 4 Wiki.md>) ([Flags](<Data structures - Hearts of Iron 4 Wiki.md#flags>), [Event targets](<Data structures - Hearts of Iron 4 Wiki.md#event-targets>), [Country tag aliases](<Data structures - Hearts of Iron 4 Wiki.md#country-tag-aliases>), [Variables](<Data structures - Hearts of Iron 4 Wiki.md#variables>), [Arrays](<Data structures - Hearts of Iron 4 Wiki.md#arrays>)) |

|  |  |
| --- | --- |
| Scripting | [Achievements](<Achievement modding - Hearts of Iron 4 Wiki.md>) • [AI](<AI modding - Hearts of Iron 4 Wiki.md>) • [AI focuses](<AI focuses - Hearts of Iron 4 Wiki.md>) • [Autonomous states](<Autonomy state modding - Hearts of Iron 4 Wiki.md>) • [Balances of power](<Balance of power modding - Hearts of Iron 4 Wiki.md>) • [Bookmarks/Scenarios](<Bookmark modding - Hearts of Iron 4 Wiki.md>) ([Game rules](<Bookmark modding - Hearts of Iron 4 Wiki.md#game-rules>)) • [Buildings](<Building modding - Hearts of Iron 4 Wiki.md>) • Characters and traits • [Cosmetic tags](<Cosmetic tag modding - Hearts of Iron 4 Wiki.md>) • [Countries](<Country creation - Hearts of Iron 4 Wiki.md>) • [Divisions](<Division modding - Hearts of Iron 4 Wiki.md>) • [Decisions](<Decision modding - Hearts of Iron 4 Wiki.md>) • [Doctrines](<Doctrine modding - Hearts of Iron 4 Wiki.md>) • [Equipment](<Equipment modding - Hearts of Iron 4 Wiki.md>) • [Events](<Event modding - Hearts of Iron 4 Wiki.md>) • [Factions](<Faction modding - Hearts of Iron 4 Wiki.md>) • [Ideas](<Idea modding - Hearts of Iron 4 Wiki.md>) • [Ideologies](<Ideology modding - Hearts of Iron 4 Wiki.md>) • [Military industrial organizations](<Military industrial organization modding - Hearts of Iron 4 Wiki.md>) • [National focuses](<National focus modding - Hearts of Iron 4 Wiki.md>) • [Resources](<Resources modding - Hearts of Iron 4 Wiki.md>) • [Scripted GUI](<Scripted GUI modding - Hearts of Iron 4 Wiki.md>) • [Technologies and doctrines](<Technology modding - Hearts of Iron 4 Wiki.md>) • [Units](<Unit modding - Hearts of Iron 4 Wiki.md>) |

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
