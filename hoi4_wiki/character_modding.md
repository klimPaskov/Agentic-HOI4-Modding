# Character modding

*Offline snapshot of the Hearts of Iron IV Wiki page "Character modding", revision 99479, captured 2026-10-31. Wiki text by the wiki's contributors under CC BY-SA 3.0 (see LICENSE.txt); kit blocks are local additions under the same license.*

<!-- kit:begin id="review" at="top" build="1.19.4.1" checked="2026-11-01" revision="99479" sources="common/characters/ common/characters/_documentation.md common/country_leader/ common/unit_leader/ common/scientist_traits/ common/special_projects/specialization/ common/ideologies/ common/opinion_modifiers/ common/on_actions/ common/operations/ common/raids/ history/general/ history/countries/ interface/ dlc/ documentation/effects_documentation.md documentation/triggers_documentation.md documentation/" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Checked against: all 232 files in `common/characters/` (5,404 characters, parsed), `common/characters/_documentation.md`, the four `common/country_leader/` files (2,103 traits), the `common/unit_leader/` files (194 traits plus the skill-level files), `common/scientist_traits/`, the character effects and triggers in the documentation, and `hoi4.exe` strings.
Kit blocks added: role and key counts, portrait casing counts, advisor keys, country leader keys, skill-level values (corrects the skill table), captured generals, scientist roles, instances, leader effects (promote, add role, rename, kill versus retire, recruit timing), effect and trigger reference, `generate_character` use, trait data (corrects `command_cap`, `parent`), full example notes.
Gaps left: recruit and portrait behaviour that only the running game shows (case-insensitive sprite lookup, what a second scientist specialization does, `allowed_civil_war` on a character) are marked `[unverified]`. `UKR_nestor_makhno` is the wiki's own example character, not a vanilla one. `command_cap` is not a game key (see the correction under "Country leader traits").
**1.19.4.1 re-check (2026-11-01).** About 75 statements depended on files the update changed (20 character files, the country leader and unit leader trait files, the interface sprite files, `hoi4.exe` and the vanilla-wide effect counts), and all were re-measured. Characters went from 5,404 to 5,409, country leader traits from 2,103 to 2,116 and unit leader traits from 194 to 196, `anarchism` is now used by a country leader, and most portrait, advisor and effect-use counts moved by a few. Every other statement cites files that are byte-identical in 1.19.4.1 (Steam depot manifest diff).
<!-- kit:end id="review" -->

## Table of contents

- [Quick checklist](#Quick_checklist)
- [Arguments](#Arguments)
  - [Name](#Name)
  - [Portraits](#Portraits)
  - [Gender](#Gender)
  - [Advisors](#Advisors)
  - [Country leaders](#Country_leaders)
  - [Unit leaders](#Unit_leaders)
    - [Kit: Captured generals](#kit-captured-generals)
  - [Scientists](#Scientists)
- [Full example](#Full_example)
- [Instances](#Instances)
- [Using in-game](#Using_in-game)
    - [Kit: Character effects and triggers in the documentation](#kit-character-effects-triggers)
  - [The special case of generate_character](#The_special_case_of_generate_character)
- [Country leader traits](#Country_leader_traits)
  - [Sprite](#Sprite)
- [Unit leader traits](#Unit_leader_traits)
  - [Localisation](#Localisation)
  - [GFX](#GFX)
  - [General arguments](#General_arguments)
  - [Modifiers and effects](#Modifiers_and_effects)
  - [Selection](#Selection)
  - [Example](#Example)
- [References](#References)

---

*For adding operatives, see [create_operative_leader](<effects.md>), as they are not characters.*

Characters are a system added in patch 1.11, allowing to use the same character for multiple roles, including different advisor types, country leaders and unit leaders. However, operatives are not considered characters and are still created with the [create_operative_leader](<effects.md>) effect.

Characters are defined within `/Hearts of Iron IV/common/characters/*.txt` files **and need to be recruited in `/Hearts of Iron IV/history/countries/TAG*.txt` files.**. Note that while it's common to put the characters in a file with the name the same as the tag of the country, the filename does not actually matter aside from organisation and for overwriting previously-loaded files with the same name. Generic characters are typically created within `/Hearts of Iron IV/history/general/*.txt` files by using the [generate_character](<effects.md>) effect, although it is to be noted that that folder is merely an effect block executed before startup, so other effects can be used there too.

Each character definition is contained within the `characters = { ... }` block, which encompasses the entirety of the file to mark them as characters. Each character is defined with a code block with the name of the character ID. For example, if the following is put within a file within the `/Hearts of Iron IV/common/characters/` folder, the blank characters my_character_1 and my_character_2 will be created:

```text
characters = {
    my_character_1 = {
    }
    my_character_2 = {
    }
}
```

Every character must be assigned to a country in that country's file in the `/Hearts of Iron IV/history/countries/` folder by using the `recruit_character = my_character` effect. Recruitment cannot take place outside of country history. **If the character is not recruited, they will never appear.** Similarly to most other folders, the game does not care about neither the filename nor the name of the characters, which is why recruitment is mandatory.

## Quick checklist <a id="Quick_checklist"></a>

- The character is created in any `/Hearts of Iron IV/common/characters/*.txt` file with no regard to the filename:
  - `name = TAG_loc_key` uses a localisation key that's defined for the English language in any `/Hearts of Iron IV/localisation/english/*_l_english.yml` file.
  - `portraits = { ... }` use spriteTypes that are defined in any `/Hearts of Iron IV/interface/*.gfx` file.
    While it's common practice to store images in subfolders of `/Hearts of Iron IV/gfx/` (usually `/Hearts of Iron IV/gfx/leaders/` for country or unit leaders and `/Hearts of Iron IV/gfx/interface/ideas/` for advisors), a sprite's `texturefile` can theoretically lead to any folder within the mod rather than being limited to `/Hearts of Iron IV/gfx/`.
- The character is assigned to a country using [recruit_character](<effects.md>) in any history file, usually done in the country's corresponding `/Hearts of Iron IV/history/countries/` file. This cannot be placed on the last line of the file.
- If the character isn't intended to have one of their roles at the start, then the character is created without that role, having it added with any [effect](<effects.md>) block using [add_country_leader_role](<effects.md>), [add_corps_commander_role](<effects.md>), [add_field_marshal_role](<effects.md>), [add_naval_commander_role](<effects.md>), or [add_advisor_role](<effects.md>). Since `add_advisor_role` is limited in what is possible to add and what isn't, instead using `visible = { ... }` with a [flag](<data_structures.md>) is an alternative for creating advisors.

<!-- kit:begin id="char-vanilla-roles" at="section:Quick_checklist" -->
**Kit note** What vanilla `common/characters/` contains, counted over 5,409 characters in 232 files (parsed with a script, `instance` blocks included).

- Vanilla uses exactly 11 top-level keys in a character: `name`, `portraits`, `gender`, `advisor`, `country_leader`, `corps_commander`, `field_marshal`, `navy_leader`, `scientist`, `instance` and `allowed_civil_war`. Characters that have each key: `portraits` 4,946, `advisor` 3,732, `name` 3,584, `corps_commander` 624, `country_leader` 558, `instance` 463, `navy_leader` 135, `scientist` 102, `allowed_civil_war` 100, `field_marshal` 99, `gender` 60. The `gender` lines are `female` (40) and `male` (24); none writes `undefined`. [vanilla-confirmed 1.19.4.1] `common/characters/`.
- There are six roles: `country_leader`, `corps_commander`, `field_marshal`, `navy_leader`, `advisor`, `scientist`. There is no air commander role and no operative role in the character files; air appears only as the `air_chief` advisor slot and the `specialization_air` scientist specialization. [vanilla-confirmed 1.19.4.1] `common/characters/`.
- Operatives are created with `create_operative_leader` (country scope), not in character files. The documentation still runs the operative effects and triggers in character scope (`is_operative`, `has_nationality`, `is_operative_captured`, `capture_operative`, `free_operative`, `kill_operative`, `turn_operative`), so an operative is addressed as a character scope even though the wiki intro says operatives are not characters. [docs] `documentation/effects_documentation.md`, `documentation/triggers_documentation.md`
- A character can hold several roles. 417 characters have an `advisor` role together with at least one of `corps_commander`, `field_marshal` or `navy_leader`; 284 of them have both blocks at the top level and the rest get one through an `instance`. 121 characters define no role block at all. [vanilla-confirmed 1.19.4.1] `common/characters/`.
- `allowed_civil_war = { ... }` sits at the top level of 100 characters (116 uses in all) and holds triggers, scripted ones such as `NOR_char_cw_democratic = yes` (`common/characters/NOR.txt`) or plain ones such as `has_government = fascism`. [vanilla-confirmed 1.19.4.1] By analogy with ideas it decides which side of a civil war keeps the character. [unverified]
- `can_be_captured = no` is documented as an optional character key (default yes). See [Captured generals](#kit-captured-generals) under "Unit leaders". [docs] `common/characters/_documentation.md`.
<!-- kit:end id="char-vanilla-roles" -->

## Arguments <a id="Arguments"></a>

These arguments are within the character itself.

### Name <a id="Name"></a>

*Main article: [Localisation](<localisation.md>)*

`name = my_character` defines a localisation key to be used to create the character's name depending on the language that is currently turned on. This will get localised in any working `/Hearts of Iron IV/localisation/english/*_l_english.yml` file, assuming the English language, as  `my_character: "My character's name"`

### Portraits <a id="Portraits"></a>

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

The portraits themselves are defined in any `/Hearts of Iron IV/interface/*.gfx` file. By default, the game uses a wide variety of files, including `/Hearts of Iron IV/dlc/dlc001_german_historical_portraits/interface/ghp_ideas_characters.gfx` (loaded in-game as `interface/ghp_ideas_characters.gfx`) or `/Hearts of Iron IV/interface/ideas.gfx`, however, editing a base game file is never necessary: a file with a higher evaluation order decided by filename (Using ASCII character IDs to order) will overwrite any spriteType defined in an earlier file, which the game uses for replacing DLC portraits.
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

The name of the spriteType has limitations: **it must begin with `GFX_`** and be made up of one word total with no whitespaces or non-ASCII characters. The image file must match up with the folder and name specified in the sprite's `texturefile` with no other limits on the filename and folder location. If both restrictions are met, the sprite will work. **The file extension, hidden by default on Windows, is a part of the filename.** By default, the game stores advisor portraits in `/Hearts of Iron IV/gfx/interface/ideas/`, while country/unit leader portraits are stored in `/Hearts of Iron IV/gfx/leaders/<TAG>/`. The background used for country/unit leader portraits is found in `/Hearts of Iron IV/tools/art/portrait_leader_background.png`.

**If a portrait doesn't work and is replaced with a randomly-selected one**, there are two possible causes for this:

- The reference to the `spriteType` within the character definition is invalid. Check if the `name = ""` in the `/Hearts of Iron IV/interface/*.gfx` file is spelt in the exact same way as the portrait assignment in the character definition. This can also stem as an issue with the entire file, whether it's missing the `spriteTypes = { ... }` in the beginning or has the wrong file extension.
- The `texturefile` argument within the sprite is incorrect. Double-check not only the filename, but also the folders leading to it. Most commonly, this can be the wrong folder, omitting or having the wrong file extension in the sprite, using backslashes instead of forward slashes to separate the folders, or a regular typo in the filename.

Due to being affected by [cosmetic tags](<cosmetic_tag_modding.md>), randomly-selected portraits get assigned only after country selection. Characters not assigned a valid portrait will show up as having no portrait or a default silhouette during the country selection process, only receiving a generic portrait after the game's start.

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

Similarly to all other sprites, animated portraits can be done by creating a [frameAnimatedSpriteType instead of a regular spriteType](<graphical_asset_modding.md#frameAnimatedSpriteType>).

For changing portraits by effect in game, [set_portraits](<effects.md>) is used. See [Using in-game](#Using_in-game) for more.

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

<!-- kit:begin id="char-portraits-vanilla" at="section:Portraits" -->
**Kit note** Portrait references in vanilla characters, counted over the 7,557 values inside `portraits = { }` blocks of `common/characters/` (`instance` blocks included).

| Slot | Values |
| --- | --- |
| `army` / `small` | 4,422 |
| `army` / `large` | 1,212 |
| `civilian` / `large` | 1,005 |
| `civilian` / `small` | 850 |
| `navy` / `small` | 41 |
| `navy` / `large` | 27 |

- Prefixes of the values: `GFX_portrait_` 4,157, `GFX_idea_` 3,224 (small portraits reuse idea sprites), `GFX_Portrait_` with a capital P 120, other `GFX_` prefixes 54, direct file paths 2. [vanilla-confirmed 1.19.4.1] `common/characters/`.
- Sprites declared in `interface/` and `dlc/*/interface/`: 3,724 start with `GFX_portrait_` and 407 with `GFX_Portrait_`, so both casings are in use. 25 character references differ from a declared sprite only in letter case, for example `GFX_portrait_Europe_Generic_1` against a declared `GFX_Portrait_Europe_Generic_1`. Script cannot show whether sprite lookup ignores case, so copy the declared name exactly. [vanilla-confirmed 1.19.4.1] `interface/`, `dlc/*/interface/`, `common/characters/`. Case-insensitive lookup is [unverified].
- 1,367 of the 7,555 `GFX_` references have no sprite declared anywhere in `interface/` or `dlc/*/interface/` (6,188 do). Vanilla ships these dangling references, so a clean game log does not prove a portrait works. [vanilla-confirmed 1.19.4.1] `common/characters/`, `interface/`, `dlc/*/interface/`.
<!-- kit:end id="char-portraits-vanilla" -->

### Gender <a id="Gender"></a>

This is primarily used in some localisation namespaces to select the pronouns for the character. Possible values are `undefined`, `male`, and `female`. The default is `gender = undefined`. If the name or the portrait are not defined, gender is used to automatically generate them. In almost all respects, `gender = undefined` behaves like `gender = male`. If a character created dynamically with `generate_character` has `undefined` gender, it will be randomly assigned using FEMALE_UNIT_LEADER_BASE_CHANCE[1] or, if the character can exclusively be a unit leader, based on the `female` attribute of the unit leader definition.

### Advisors <a id="Advisors"></a>

A character has an advisor role added by defining one within the `advisor = { ... }` block. This definition is [similar to ideas in many ways](<idea_modding.md>), but there are a few extra arguments:

`slot = political_advisor` is used to determine the [character slot](<idea_modding.md#Categories>) on the country politics view that the character occupies. By default, these character slots exist in the base game:

| Internal name | Localised name | Intelligence ledger | Category | Notes |
| --- | --- | --- | --- | --- |
| political_advisor | Political advisor | Civilian | Laws & Government |  |
| theorist | Theorist | Invalid | Research & Production | The ledger must be specified for each theorist individually as, for example, `ledger = navy`. Possible values are `army`, `air`, `navy`, `military` (Appearing on each of the prior ledgers), `civilian`, `all`, and `hidden`. |
| army_chief | Chief of Army | Army | Military Staff |  |
| navy_chief | Chief of Navy | Navy | Military Staff |  |
| air_chief | Chief of Airforce | Air | Military Staff |  |
| high_command | Military High Command | Invalid | Military Staff | The ledger must be specified for each theorist individually as, for example, `ledger = navy`. Possible values are `army`, `air`, `navy`, `military` (Appearing on each of the prior ledgers), `civilian`, `all`, and `hidden`. |

`idea_token = my_character` is the ID used for the character when treated as an idea within this particular slot. For example, [the has_idea trigger](<triggers.md>) or [the show_ideas_tooltip effect](<effects.md>) do not expect the character ID, but the idea token of the character instead. Since it is impossible to have two of the same idea, any other character with the same idea token will be impossible to take. As not having an idea token is treated as having a null one, **this is mandatory**. Otherwise, recruiting this character will make every other advisor without an idea token specified disappear from the selection.

`can_be_fired = no` assigns the advisor as impossible to fire manually. *Note:* Prior to 1.12.8, `removal_cost = -1` could've been used for this purpose, but this does not work after the patch.

Everything else regarding advisors is identical to ideas. Commonly, the `traits = { ... }` block is used, where [each country leader trait](#Country_leader_traits) that the character has is listed, separated with a whitespace, as `traits = { my_trait_1 my_trait_2 }`. These would apply modifiers on the country if the advisor is recruited, as well as adding a subtext and an icon in the bottom right of the advisor's picture.
[available, cost, and visible](<idea_modding.md#Additional_arguments_2>) arguments are also common.
`on_add = { ... }` and `on_remove = { ... }` attributes use the character scope instead of the country scope as they do in ideas. In order to scope into the country that the advisor is assigned to, use [the owner scope](<scopes.md>).

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

<!-- kit:begin id="char-advisor-vanilla" at="section:Advisors" -->
**Kit note** What vanilla `advisor` blocks contain, counted over 4,464 blocks (`instance` blocks included). All counts: [vanilla-confirmed 1.19.4.1] `common/characters/`.

- Slots used: `political_advisor` 1,861, `high_command` 932, `theorist` 512, `army_chief` 452, `air_chief` 358, `navy_chief` 349. These are the six slots in the table above.
- Every block has `slot`, `idea_token` and `traits` (4,464 of 4,464), so `idea_token` is not optional in practice. Other keys: `allowed` 4,427, `ai_will_do` 2,923, `cost` 1,926, `available` 1,496, `ledger` 1,455, `visible` 838, `do_effect` 231, `on_add` 190, `on_remove` 172, `name` 75, `can_be_fired` 59, `research_bonus` 15, `removal_cost` 2, `always_show_on_actions_tooltip` 2, `modifier` 1. The wiki page covers `do_effect`, `name` and `research_bonus` only through "everything else is identical to ideas"; `always_show_on_actions_tooltip = yes` (2 blocks in `common/characters/AST.txt`, next to `on_add`) is in neither the wiki nor `documentation/`. [vanilla-confirmed 1.19.4.1] It is also a string in `hoi4.exe`, and its effect is [unverified].
- Advisor-only triggers and effects in the documentation: `has_advisor_role = slot`, `is_hired_as_advisor`, `is_advisor`, `is_political_advisor`, `is_theorist`, `is_army_chief`, `is_navy_chief`, `is_air_chief`, `is_high_command`, `advisor_can_be_fired` (false when the character has no matching advisor role, so test `has_advisor_role` first), and `not_already_hired_except_as = slot` for a character with several advisor roles that must be hired in one only (24 vanilla uses). [docs] `documentation/triggers_documentation.md`
- `set_can_be_fired_in_advisor_role = { character = id slot = political_advisor value = no }` changes the `can_be_fired` flag after the start; `slot` is mandatory if the character has several advisor roles, and the character-scope form omits `character`. [docs] `documentation/effects_documentation.md`
- `add_advisor_role = { character = id advisor = { slot = air_chief idea_token = x traits = { ... } } activate = yes }` adds a role during play and `activate = yes` hires at once; `deactivate_advisor = idea_token` dismisses. `hoi4.exe` carries the message that an advisor role created through script cannot contain effects or triggers, which matches the wiki text above. [docs] `documentation/effects_documentation.md`; the message is [unverified] (executable string only).
<!-- kit:end id="char-advisor-vanilla" -->

### Country leaders <a id="Country_leaders"></a>

*See also: [Ideology modding](<ideology_modding.md>)*

Country leaders are defined with the `country_leader = { ... }` block. The following arguments can be used within:

`ideology = socialist` is the ideology **type** that the leader is assigned. An ideology group (such as ![Democracy](media/character_modding_cee5ae9645__img1.png)democratic) cannot be assigned here directly, rather ideology types are defined for each leader to decide the ideology group the party of which the character leads.
The difference between ideology types is mostly cosmetic, changing the description shown when hovering over the ideology icon and, [if defined so](<ideology_modding.md#GFX>), the icon itself. Additionally, countries with the same ruling ideology group but a different leader ideology type will have the *“Same Ideology”* (![Opinion](media/character_modding_8d43751dba__img2.png) **+10** opinion) modifier towards each other, while countries with the same leader ideology type will have the *“Same Ruling Party”* (![Opinion](media/character_modding_8d43751dba__img2.png) **+20** opinion) modifier towards each other.
These are the ideology types in base game across groups, defined in `/Hearts of Iron IV/common/ideologies/*.txt`:

| Internal name | Localised name | Ideology group | Notes |
| --- | --- | --- | --- |
| conservatism | Conservatism | ![Democracy](media/character_modding_cee5ae9645__img1.png)democratic |  |
| liberalism | Liberalism | ![Democracy](media/character_modding_cee5ae9645__img1.png)democratic |  |
| socialism | Socialism | ![Democracy](media/character_modding_cee5ae9645__img1.png)democratic |  |
| populism | Populism | ![Democracy](media/character_modding_cee5ae9645__img1.png)democratic |  |
| marxism | Marxism | ![Communism](media/character_modding_41494a4f46__img8.png)communism |  |
| leninism | Leninism | ![Communism](media/character_modding_41494a4f46__img8.png)communism |  |
| stalinism | Stalinism | ![Communism](media/character_modding_41494a4f46__img8.png)communism |  |
| anti_revisionism | Anti-Revisionism | ![Communism](media/character_modding_41494a4f46__img8.png)communism |  |
| anarchist_communism | Anarchist Communism | ![Communism](media/character_modding_41494a4f46__img8.png)communism |  |
| buddhist_socialism | Buddhist Socialism | ![Communism](media/character_modding_41494a4f46__img8.png)communism | Cannot be randomly selected. |
| nazism | Nazism | ![Fascism](media/character_modding_58ea48332f__img14.png)fascism |  |
| gen_nazism | Nazism | ![Fascism](media/character_modding_58ea48332f__img14.png)fascism | Generic in the sense that the description is changed to not reference Germany. |
| fascism_ideology | Fascism | ![Fascism](media/character_modding_58ea48332f__img14.png)fascism |  |
| falangism | Falangism | ![Fascism](media/character_modding_58ea48332f__img14.png)fascism |  |
| rexism | Rexism | ![Fascism](media/character_modding_58ea48332f__img14.png)fascism |  |
| emperor_fascism | Emperor Fascism | ![Fascism](media/character_modding_58ea48332f__img14.png)fascism | Cannot be randomly selected. |
| despotism | Despotic | ![Neutrality](media/ai_modding_25696e0a81__img2.png)neutrality |  |
| oligarchism | Oligarchic | ![Neutrality](media/ai_modding_25696e0a81__img2.png)neutrality |  |
| anarchism | Anarchism | ![Anarchism](media/character_modding_04e3359449__img22.png)neutrality | Cannot be randomly selected. Has a unique ideology icon. |
| moderatism | Moderatism | ![Neutrality](media/ai_modding_25696e0a81__img2.png)neutrality |  |
| centrism | Centrism | ![Neutrality](media/ai_modding_25696e0a81__img2.png)neutrality |  |
| japan_militarism_ideology | Militarism | ![Neutrality](media/ai_modding_25696e0a81__img2.png)neutrality | Cannot be randomly selected. |

`traits = { my_trait_1 my_trait_2 }` is, similarly to advisors, a list of [country leader traits](#Country_leader_traits) that the country leader has, which would apply modifiers on the country if the character is leading the country.

`expire = 1949.1.1` marks the date at which the leader expires. If the **start** date is after this amount, they cannot be used, even if recruited. Optional.

`id = 100` is a leftover from the pre-NSB country leader system, making the leader have the specified ID for the [has_country_leader trigger](<triggers.md>). Unnecessary and should be omitted, use character specific triggers instead.

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
- In case of differences between startdates, use the [promote_character](<effects.md>) effect to ensure the new character becomes leader.

<!-- kit:begin id="char-country-leader-vanilla" at="section:Country_leaders" -->
**Kit note** What vanilla `country_leader` blocks contain, counted over 776 blocks (`instance` blocks included). All counts: [vanilla-confirmed 1.19.4.1] `common/characters/`, `common/ideologies/00_ideologies.txt`.

- Keys used: `ideology` 776, `expire` 774, `id` 755, `traits` 543. No vanilla block sets `desc`. The wiki calls `id` a leftover to omit; vanilla still writes it (usually `id = -1`), so it is harmless.
- `expire` is written as `YYYY.M.D.H` in 738 blocks (for example `1965.1.1.1`) and as `YYYY.M.D` in 36.
- `ideology` always names a sub-ideology. Vanilla characters use 21 of the 22 types in the table above; `buddhist_socialism` never appears. `common/ideologies/00_ideologies.txt` defines 22 types in 4 groups, which matches the table. Most used: `despotism` 168, `fascism_ideology` 88, `marxism` 81, `conservatism` 79.
- The two opinion modifiers behind the wiki's "+20" and "+10" are `same_ruling_party` (value 20, shown as "Same Ruling Party") and `similar_ruling_party` (value 10, shown as "Same Ideology"); `different_party_types` is -10 ("Different Ideology"). [vanilla-confirmed 1.19.4.1] `common/opinion_modifiers/00_opinion_modifiers.txt`, `localisation/english/diplomacy_l_english.yml`. Which pair of leaders triggers which one is engine logic. [unverified]
<!-- kit:end id="char-country-leader-vanilla" -->

### Unit leaders <a id="Unit_leaders"></a>

Unit leaders include corps commanders, field marshals, and admirals. Respectively, these use `corps_commander = { ... }`, `field_marshal = { ... }`, and `navy_leader = { ... }` blocks for definition, which are similar in structure.

`traits = { my_trait_1 my_trait_2 }` is the list of [unit leader traits](#Unit_leader_traits) assigned to the unit leader, defined in `/Hearts of Iron IV/common/unit_leader/*.txt`.

`skill = 4` is the overall skill level of the unit leader. In addition, specific skills also can be set, with `attack_skill = 3` and `defense_skill = 2` being shared across all unit leaders, `planning_skill = 5` and `logistics_skill = 6` being only for army leaders, and `coordination_skill = 3` and `maneuvering_skill = 5` being only for navy leaders. To put what each skill level grants to the leader in more detail:

| Internal name | Localised name | Unit leader type | Effect per level |
| --- | --- | --- | --- |
| skill | Skill | Any unit leader | Army leaders: Nothing<br> Navy leaders: +5% hit chance, +2% fleet coordination. |
| attack_skill | Attack | Any unit leader | Army leaders: +2.5% offense<br> Navy leaders: +5% damage |
| defense_skill | Defense | Any unit leader | Army leaders: +2.5% defense<br> Navy leaders: +5% defense |
| planning_skill | Planning | Army leaders only | +5% planning speed<br> +2% max bonus from planning |
| logistics_skill | Logistics | Army leaders only | -2.5% supply consumption |
| maneuvering_skill | Maneuvering | Navy leaders only | +2.5% positioning<br> +1% naval retreat speed |
| coordination_skill | Coordination | Navy leaders only | +2% fleet coordination |

`legacy_id = 100` is a leftover from the pre-NSB country leader system, making the leader have the specified ID for the [has_id trigger](<triggers.md>), the [has_unit_leader trigger](<triggers.md>), and elsewhere. Unnecessary and should be omitted, use character specific triggers instead.

`visible = { ... }` is a trigger block that the character must fulfill in order for the unit leader to be visible and possible to pick. Additionally, country-scoped triggers are also supported, which'll assume the country that recruited the character. Unnecessary in most cases, as it's possible to [create the unit leader role](<effects.md>) within an effect block mid-game.

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

<!-- kit:begin id="char-unit-leader-vanilla" at="section:Unit_leaders" -->
**Kit correction** The skill table above is partly out of date. Per-level values live in `common/unit_leader/00_*_skills.txt`; each file is a block (`leader_attack_skills`, `leader_defense_skills`, `leader_planning_skills`, `leader_logistics_skills`, `leader_maneuvering_skills`, `leader_coordination_skills`, `leader_skills`) of numbered levels with an XP `cost`, a `type` (`corps_commander`, `field_marshal`, `navy`, and `operative` for `leader_skills`) and a `modifier`. All rows: [vanilla-confirmed 1.19.3] `common/unit_leader/`.

| Skill | Levels defined | Modifier per level |
| --- | --- | --- |
| `attack_skill` | 10 | army `offence` +0.025; navy `naval_damage_factor` +0.05 |
| `defense_skill` | 10 | army `defence` +0.025; navy `naval_defense_factor` +0.05 |
| `planning_skill` | 10 | army `planning_speed` +0.05 and `max_planning` +0.02 |
| `logistics_skill` | 10 | army `supply_consumption_factor` -0.025 |
| `maneuvering_skill` | 10 | navy `positioning` +0.025 and `naval_retreat_speed` +0.01 |
| `coordination_skill` | 10 | navy `naval_coordination` 0.01, 0.03, 0.05, 0.07, 0.09, 0.12, 0.14, 0.16, 0.18, 0.20 (not a flat step) |
| `skill` | 9 (navy, corps commander, field marshal) | none: for those three types every `modifier` block in `leader_skills` is empty (the navy ones are commented out), so overall `skill` only sets the level; the wiki's "+5% hit chance, +2% coordination" for navy `skill` has no counterpart in 1.19.3 |

The navy entries in `leader_planning_skills` and `leader_logistics_skills` carry `naval_hit_chance` and `naval_coordination`, but none of the 165 `navy_leader` blocks sets a planning or logistics skill, so no vanilla character reaches those entries. [vanilla-confirmed 1.19.4.1] `common/characters/`. Whether a script could set them on a navy leader is [unverified].

Vanilla characters stay low: `skill` is 1 to 5 for every unit leader type; corps commander and navy `attack_skill`, navy `defense_skill` and navy `coordination_skill` reach 6; navy `maneuvering_skill` reaches 4. The wiki examples with `skill = 10` are above the 9 levels `leader_skills` defines. [vanilla-confirmed 1.19.4.1] `common/characters/`. What happens above the defined levels is [unverified].

Vanilla unit leader blocks use only these keys: `skill`, `attack_skill`, `defense_skill`, `traits`, `legacy_id` (704 of 785 corps commanders), `visible`, plus `planning_skill` and `logistics_skill` (army) or `maneuvering_skill` and `coordination_skill` (navy). Counts: 785 `corps_commander`, 135 `field_marshal`, 165 `navy_leader` blocks. [vanilla-confirmed 1.19.4.1] `common/characters/`.

#### Kit: Captured generals <a id="kit-captured-generals"></a>

**Kit addition** Defeated deployed generals can be captured in 1.19.4.1. All rows: [docs] `common/characters/_documentation.md`, `documentation/effects_documentation.md`, `documentation/triggers_documentation.md`; vanilla counts are [vanilla-confirmed 1.19.4.1] over `common/`.

| Name | Kind and scope | Notes |
| --- | --- | --- |
| `can_be_captured = no` | character key | Default yes. A character with a country leader role is always treated as uncapturable. The only 2 vanilla uses are `no` inside `instance` blocks of `PRC_mao_zedong` in `common/characters/PRC.txt`. |
| `can_be_captured = yes` | trigger, CHARACTER | Whether the character can be captured while deployed in a division. |
| `capture_by` | effect | Captures the unit leader in scope. `capture_by = TAG`, `capture_by = FROM` or `capture_by = { country = TAG province = 1234 }` (the province where the leader is held is optional). The documentation lists the scope as `any`; vanilla runs it with the leader as scope. 3 vanilla uses. |
| `release_from_captivity = yes` | effect, CHARACTER | Releases the captured army leader; no effect if not captured. 3 uses, all in `common/raids/land_infiltration_raids.txt`. |
| `release_captured_generals_from` | effect, COUNTRY | The scoped country (the captor) releases the generals it holds from the target: `release_captured_generals_from = TAG`, or `{ target = TAG province = id }` for only those held in one province. 2 uses in `common/operations/00_operations.txt`. |
| `is_general_captured = yes` | trigger, CHARACTER | True when the leader is captured by any country. |
| `has_any_captured_general = yes` | trigger, COUNTRY | True when any general of the scoped country is captured by another country. |
| `has_any_general_captured_by = TAG` | trigger, COUNTRY | True when the scoped country has a leader captured by the target. |

Vanilla wiring: the `on_deployed_leader_defeated` on action in `common/on_actions/00_on_actions.txt` checks `can_be_captured = yes`, then runs `capture_by = FROM`; a leader that cannot be captured, such as a country leader, instead gets the `wounded` trait for 90 days. [vanilla-confirmed 1.19.4.1] `common/on_actions/00_on_actions.txt`.
<!-- kit:end id="char-unit-leader-vanilla" -->

### Scientists <a id="Scientists"></a>

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

<!-- kit:begin id="char-scientist-vanilla" at="section:Scientists" -->
**Kit note** Scientist roles in 1.19.4.1. Each item ends with its own evidence tag.

1. The documented keys of `scientist = { }` are `desc`, `traits`, `skills` and `visible` (trigger, ROOT is the character). Every specialization starts at level 1 and `skills = { specialization_land = 2 }` overrides only those listed. [docs] `common/characters/_documentation.md`
2. The wiki says specializations after the first are ignored. The documentation says each listed one overrides its level, and vanilla has one scientist that lists two (`SOV_igor_kurchatov`: `specialization_nuclear = 2` and `specialization_naval = 2`). What the game does with the second entry is [unverified]. [docs] `common/characters/_documentation.md`; [vanilla-confirmed 1.19.4.1] `common/characters/SOV.txt`
3. Vanilla has 103 scientist roles; 102 list one specialization and 1 lists two. The four specializations are `specialization_air` (46 entries), `specialization_nuclear` (28), `specialization_naval` (16) and `specialization_land` (14), defined in `common/special_projects/specialization/specializations.txt`. [vanilla-confirmed 1.19.4.1] `common/characters/`, `common/special_projects/specialization/`
4. Scientist traits come from their own database, `common/scientist_traits/00_traits.txt` (21 traits, each a top-level block). All 139 trait references in vanilla scientist roles resolve there, although the character documentation still says the traits come from the country leader database. The folder documentation says scientist traits only affect special projects, so use only modifiers that apply to them. [vanilla-confirmed 1.19.4.1] `common/scientist_traits/00_traits.txt`, `common/characters/`; [docs] `common/scientist_traits/_documentation.md`
5. Role effects: `add_scientist_role`, `remove_scientist_role`, `add_scientist_trait`, `add_scientist_level`, `add_scientist_xp`, `injure_scientist_for_days`, `generate_scientist_character`; triggers `has_scientist_level`, `has_scientist_specialization`, `is_active_scientist`, `is_scientist_injured`. A role added through `add_scientist_role` cannot carry a `visible` trigger. Vanilla uses `generate_scientist_character` 3 times and `add_scientist_role` never. [vanilla-confirmed 1.19.4.1] [docs] `documentation/effects_documentation.md`, `documentation/triggers_documentation.md`
<!-- kit:end id="char-scientist-vanilla" -->

## Full example <a id="Full_example"></a>

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

<!-- kit:begin id="char-full-example-notes" at="section:Full_example" -->
**Kit note** `UKR_nestor_makhno` is the wiki's own example, not a vanilla character (0 vanilla files use the id). `SOV_georgy_zhukov` is the vanilla character; the vanilla version also sets `cost = 150` in the advisor block. No vanilla `country_leader` block sets `desc`, so the example's `desc` line has no vanilla precedent. [vanilla-confirmed 1.19.4.1] `common/characters/SOV.txt`, `common/characters/`.
<!-- kit:end id="char-full-example-notes" -->

## Instances <a id="Instances"></a>

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

<!-- kit:begin id="char-instances-vanilla" at="section:Instances" -->
**Kit note** Vanilla has 882 `instance` blocks in 463 characters, and every block has an `allowed` trigger. 404 characters have 2 instances (typically a `has_dlc` check and its `NOT`), 52 have 1, 6 have 3 and 1 has 4. The 52 single-instance characters show that one gated instance is valid; the wiki's "must have multiple instances" is not a hard rule. `allowed` starts with `has_dlc` in 457 instances and with `NOT` in 411. [vanilla-confirmed 1.19.4.1] `common/characters/`.
<!-- kit:end id="char-instances-vanilla" -->

## Using in-game <a id="Using_in-game"></a>

*See also: [Effect § Character scope](<effects.md#Character_scope>)**See also: [Effect § Characters](<effects.md#Characters>)*

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

In this case, TAG_liberal_leader will be the leader of the democratic ideology/party and thus the starting country leader. TAG_marxist_leader will be the leader of the communist party, TAG_centrist_leader will be the leader of the non-aligned party and TAG_falangist_leader will be the leader of the fascist party.

The characters TAG_stalinist_leader, TAG_conservative_leader, TAG_despotic_leader and TAG_rexist_leader do not start as leaders in this case and will remain only as possible leaders to be used later on. For this reason, it is not necessary for country leader characters to be defined without the role, as long as their ideology group has another character as leader.

Characters that are recruited but not currently the leader of their party, such as the TAG_conservative_leader above can later be promoted to leader using the [promote_character](<effects.md>) effect. Retiring the previous leader or removing their role is not necessary. Example:

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
After doing so, this character can be *given* a role within an effect block using the effect [add_country_leader_role](<effects.md>). For example, this completion reward for a focus makes a character lead the democratic party:

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

If a character is intended to be removed from the game "permanently", as in death or retirement, [retire_character](<effects.md>) (country scope) and [retire](<effects.md>) (character scope) can be used. This is basically a reverse effect of `recruit_character`, the character will be dismissed from the country completely. However, this effect is not actually permanent, the character can be re-added to the game using the effect [set_nationality](<effects.md>) and all their roles will be retained. For scoping purposes, the character is located in the same country as before.

- Removing a character is not always needed. For example when another character is set to become country leader, using the effect `promote_character` is enough already as the old leader will not affect it in any way. The effect [remove_country_leader_role](<effects.md>) can also be used the remove the leader role from a character, and other roles will also have effects that can be used.

It is not recommended to use effects such as `kill_country_leader`, `retire_country_leader`, `kill_ideology_leader` and `retire_ideology_leader`, as these effects will affect *any character* that is currently the leader without further confirmation, instead of being able to specify who should be removed.

- When dealing with characters, `kill_country_leader` and `kill_ideology_leader` will behave exactly the same way as `retire_character`, meaning the character is dismissed and can be re-added with `set_nationality`.
- As for `retire_country_leader` and `retire_ideology_leader`, these effects will only remove the leader from the "line of succession" of their political party, meaning the next character recruited will be promoted to leader of the party. The old leader will not be removed and will retain all their roles, being able to come back using `promote_character`.

Other effects on this topic include [add_corps_commander_role](<effects.md>), [add_field_marshal_role](<effects.md>), [add_naval_commander_role](<effects.md>), [add_advisor_role](<effects.md>), and others.

Advisor roles created with `add_advisor_role` cannot contain script, such as `visible = { ... }`, `available = { ... }`, `on_add = { ... }`. It is recommended instead to use `visible = { ... }` with an appropriate [trigger](<triggers.md>) for creating advisors that should not be visible at game start. For the same reason, it is not recommended to use `remove_advisor_role` on advisors that contain script, as all the triggers and effects will be lost and cannot be added back if needed later on. Usage of these effects should be reserved for characters with more static roles, as in have no conditions or other script.

In order to hire an advisor to be within their proper slot, [activate_advisor](<effects.md>) is used as such:

```text
activate_advisor = TAG_character_name_token
```

Where `TAG_character_name_token` is the `idea_token` defined in the character's advisor role. As an effect, this works within country history files as well.

Portraits of characters, both small and large, can be changed later in game using the effect [set_portraits](<effects.md>), which works both in character scope and country scope. The same rules as on [Portraits](#Portraits) apply. For example:

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

<!-- kit:begin id="char-leader-effects" at="section:Using_in-game" -->
**Kit note** Exact behaviour of the character effects this section names. Syntax: [docs] `documentation/effects_documentation.md`; counts: [vanilla-confirmed 1.19.4.1] over `common/`, `events/` and `history/`.

- `recruit_character = id` runs in country scope. All 5,612 vanilla uses sit in 257 files under `history/countries/`; none is anywhere else, and `generate_character` (128 uses) is only in `history/general/`. [vanilla-confirmed 1.19.4.1] `hoi4.exe` contains the text "recruit_character should only happen in game/history files in order to be executed only at game start", and also "cannot be assigned to ... as it is already assigned to ...", so one character belongs to one country at a time. The documentation sets no timing limit, so treat history-only as a convention; what the engine does outside history is [unverified]. Do not recruit in events or focuses without testing.
- `promote_character` has a country form (`promote_character = id`, or `{ character = id ideology = x }`) and a character form (`promote_character = yes`, `= ideology`, or `{ ideology = x }`). The ideology is mandatory only when the character has several country leader roles. 376 vanilla uses. [docs]
- `add_country_leader_role = { character = id promote_leader = yes country_leader = { ideology = x expire = "1965.1.1.1" traits = { ... } } }` (`character` is optional in character scope). `hoi4.exe` has the messages "Character already has a country leader role for ideology:" and "Character already has a country leader role with this ideology", so adding a second role for an ideology the character already leads for is refused; check with `has_ideology = x` in character scope first. 898 vanilla uses. [vanilla-confirmed 1.19.4.1] [docs] for syntax; the refusal is [unverified] (executable strings only).
- `remove_country_leader_role = { character = id ideology = x }` removes one leader role. 113 vanilla uses.
- `set_character_name` takes the new name, not a character token. Block form: `set_character_name = { character = id name = KEY_OR_TEXT }` in country scope, with `character` dropped inside a character scope; `name` is a localisation key or a literal. Scalar form in character scope: `set_character_name = KEY`. Vanilla passes keys such as `ITA_benito_mussolini_roman_emperor`. 12 vanilla uses.
- `kill_country_leader = yes` (country scope) removes the leader completely and makes the next in line the new party and country leader (42 uses). `retire_country_leader` (163 uses) removes the leader from party leadership and also hands over to the next in line. The documentation matches the wiki's kill/retire split for this pair, but its texts for `kill_ideology_leader` (9 uses) and `retire_ideology_leader` (21 uses) are the other way round, so do not rely on the ideology pair. Prefer `promote_character`, `retire_character` and `remove_country_leader_role`, which name the character.
- `retire_character = id` (country) and `retire = yes` (character) remove the character from the country with all roles; `set_nationality` brings them back. 289 and 41 vanilla uses.
- `set_portraits = { character = id civilian = { large = GFX_x small = GFX_y } army = { ... } }` (country scope; `character` is dropped in character scope). 53 vanilla uses.
<!-- kit:end id="char-leader-effects" -->

<!-- kit:begin id="char-effects-reference" at="section:Using_in-game" -->
#### Kit: Character effects and triggers in the documentation <a id="kit-character-effects-triggers"></a>

**Kit addition** Documented names this page never lists. Scopes and meanings: [docs] `documentation/effects_documentation.md`, `documentation/triggers_documentation.md`. Use counts: [vanilla-confirmed 1.19.4.1].

| Name | Scope | What it does |
| --- | --- | --- |
| `add_corps_commander_role`, `add_field_marshal_role`, `add_naval_commander_role` | COUNTRY, CHARACTER | Add a unit leader role: `{ character = id traits = { } skill = 4 attack_skill = 2 defense_skill = 3 ... }` (army: `planning_skill`, `logistics_skill`; navy: `maneuvering_skill`, `coordination_skill`). 85, 25 and 14 vanilla uses. |
| `remove_unit_leader_role` | COUNTRY, CHARACTER | Removes the unit leader role. The documentation's own example spells it `remove_corps_commander_role`, which no vanilla file uses. 26 uses of the real name. |
| `promote_leader`, `demote_leader` | CHARACTER | General to field marshal and back. `promote_leader = yes` is also the key that makes a new leader take over inside `add_country_leader_role`, which accounts for most of its 912 vanilla uses. |
| `create_corps_commander`, `create_field_marshal`, `create_navy_leader`, `create_country_leader` | COUNTRY | Older direct creation. `create_country_leader` takes `name`, `desc`, `picture`, `expire`, `ideology`, `traits`, and adds the role to an existing character with the same token or name. 33, 4, 3 and 176 uses. |
| `add_country_leader_trait`, `remove_country_leader_trait` | COUNTRY, CHARACTER | `trait_id`, or `{ ideology = x trait = id }` when a character has several leader roles. 269 and 46 uses. |
| `swap_country_leader_traits` | CHARACTER | `{ remove = a add = b ideology = x }`. 84 uses. |
| `add_unit_leader_trait`, `remove_unit_leader_trait`, `add_timed_unit_leader_trait`, `add_random_trait` | CHARACTER | Unit leader traits; the timed form takes `trait` and `days`; `add_random_trait = { a b c }` picks one. 137, 17 and 9 uses for the first, third and fourth. |
| `add_trait`, `remove_trait` | COUNTRY, CHARACTER | `{ character = id trait = id slot = x ideology = y }`; `slot` selects the advisor role, `ideology` the country leader role. |
| `add_skill_level`, `add_attack`, `add_defense`, `add_planning`, `add_logistics`, `add_maneuver`, `add_coordination`, `gain_xp` | CHARACTER | Raise a unit leader skill by the number given; `gain_xp = 5` gives experience and levels the leader up when possible. |
| `set_country_leader_name`, `set_country_leader_portrait`, `set_country_leader_description`, `set_country_leader_ideology` | COUNTRY | Change the current leader. The first three take `{ ideology = x name = "..." }` (or `portrait`, `desc`), where `ideology` can be left out. No tooltip. |
| `set_character_flag`, `clr_character_flag`, `modify_character_flag`, `has_character_flag` | CHARACTER | Character flags. `has_character_flag = { flag = x value < n days > n }`; `has_unit_leader_flag` is deprecated for it. 566 uses of `set_character_flag`. |
| `every_character`, `random_character`, `every_unit_leader`, `every_army_leader`, `every_navy_leader`, `random_unit_leader`, `any_character`, `any_unit_leader` | COUNTRY | Iterate characters; optional `tooltip`, `random_select_amount`, `include_invisible` (default no) and, for the `every_` forms, `display_individual_scopes`. |
| `is_country_leader`, `is_corps_commander`, `is_field_marshal`, `is_navy_leader`, `is_army_leader`, `is_unit_leader`, `is_character = id`, `has_character = id` | CHARACTER / COUNTRY | Role and identity checks (`has_character` is COUNTRY scope, the rest CHARACTER). |
| `has_ideology = sub`, `has_ideology_group = group`, `can_be_country_leader`, `has_country_leader`, `has_country_leader_with_trait`, `has_country_leader_ideology` | CHARACTER / COUNTRY | Does the character hold a leader role for that sub-ideology or group; does the country's leader match. `has_country_leader = { character = id ruling_only = yes }`. |
| `skill`, `attack_skill_level`, `defense_skill_level`, `planning_skill_level`, `logistics_skill_level`, `average_stats`, `has_trait`, `has_ability` | CHARACTER | Unit leader comparisons, for example `attack_skill_level > 5`. |
| `is_assigned`, `is_leading_army`, `is_leading_army_group`, `is_female`, `is_exiled_leader`, `is_promoted_from_unit` | CHARACTER | Further unit leader checks. |
| `set_faction_leader` | COUNTRY | Makes the scoped country leader of its faction (a country effect, not a character one). |

The documentation lists `promote_officer_to_general`, `party_leader`, `set_leader_name`, `set_leader_portrait`, `replace_unit_leader_trait` and `add_max_trait`, but no vanilla file uses them. [docs] `documentation/effects_documentation.md`; the zero counts are [vanilla-confirmed 1.19.4.1].
<!-- kit:end id="char-effects-reference" -->

### The special case of generate_character <a id="The_special_case_of_generate_character"></a>

The effect [generate_character](<effects.md>) is used to create generic characters, such as the generic advisors present in the base game. **These have limitations and should not be used as a replacement for regular characters.** Example:

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

<!-- kit:begin id="char-generate-character-vanilla" at="section:The_special_case_of_generate_character" -->
**Kit note** `generate_character` in 1.19.4.1. Syntax: [docs] `documentation/effects_documentation.md`; counts: [vanilla-confirmed 1.19.4.1] `history/general/`.

- `token_base` is the only mandatory key. The character token is `token_base`; an advisor idea token is `token_base_<idea_token>`, or `token_base_<slot>` when `idea_token` is left out. `name` is optional (a random name when missing), and the rest is written like a character definition.
- All 128 vanilla uses sit in two files in `history/general/` (`generic_advisors.txt` 53, `spain_shared_advisors.txt` 75), none elsewhere. Vanilla builds its generic ideology advisors this way, for example `token_base = generic_communist_revolutionary` with `advisor = { slot = political_advisor traits = { communist_revolutionary } }` and the portrait `GFX_idea_generic_communist_revolutionary`.
- `generate_scientist_character` creates and recruits a scientist (`portrait`, `portrait_tag_override`, `gender`, `skills`, `traits`; all optional). 3 vanilla uses. [docs] `documentation/effects_documentation.md`
<!-- kit:end id="char-generate-character-vanilla" -->

## Country leader traits <a id="Country_leader_traits"></a>

*"Trait modding" redirects here. For unit leader traits, see [§ Unit leader traits](#Unit_leader_traits)*

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
- `ai_will_do` is a [MTTH block](<ai_modding.md>) that modifies the chance for AI to pick an advisor or idea that has this trait assigned. 1 by default.

- `command_cap` determines the price of the political advisor to which this trait is assigned in Command power. Mainly applied to military advisors.

Additionally, [special modifier types that can be used in ideas](<idea_modding.md#Modifiers>): `targeted_modifier = { ... }` and `equipment_bonus = { ... }` - can be used within traits alongside regular modifiers, in the exact same manner as within ideas. The same does not apply to `research_bonus = { ... }` and `rule = { ... }`, however.

Localisation is defined by using the trait's name as a localisation key within any localisation file, with an entry as  `my_trait: "My trait"`.

<!-- kit:begin id="char-country-leader-traits-vanilla" at="section:Country_leader_traits" -->
**Kit correction** `command_cap` is not a game key. It appears in no vanilla file, in no documentation and not in `hoi4.exe`, so the wiki's `command_cap = @tier1` line and the example above do nothing useful. Vanilla traits use two keys instead: `command_power = <cost>` (162 traits), which is the command power price of the advisor, and `command_cap_increase = <amount>` (163 traits), which raises the command power cap. Both take values from constants at the top of `common/country_leader/00_traits.txt`: `@tier1_cp_cost`, `@tier2_cp_cost`, `@tier3_cp_cost` (all 0 in 1.19.4.1) and `@tier1_cp_cap_increase`, `@tier2_cp_cap_increase`, `@tier3_cp_cap_increase` (10, 20, 30). [vanilla-confirmed 1.19.4.1] `common/country_leader/00_traits.txt`. That `command_power` is a price is inferred from the vanilla AI weight `command_power < @tier1_cp_cost` giving factor 0. [unverified]

**Kit note** Country leader traits in vanilla, counted over 2,116 traits in `common/country_leader/00_traits.txt`, `goe_traits.txt`, `taog_traits.txt` and `toa_traits.txt`. All counts: [vanilla-confirmed 1.19.4.1] `common/country_leader/`.

- `random = no` is set on 1,778 traits and `random = yes` on 23. `sprite` is set on 1,553 traits and goes up to 18, matching `noOfFrames = 18` for `GFX_idea_traits_strip` in `interface/ideas.gfx`. `ai_will_do` is on 710 traits.
- `equipment_bonus` (72), `targeted_modifier` (16), `hidden_modifier` (15) and `custom_modifier_tooltip` (74) appear directly in traits. `research_bonus` and `rule` appear in none, as the wiki says.
- Ideology booster traits such as `communist_revolutionary`, `democratic_reformer` and `fascist_demagogue` use `random = no`, `sprite = 13` and `<group>_drift = 0.1`. The `_booster` suffix in the [Ideology modding](<ideology_modding.md#Political_advisor>) template is not a vanilla naming convention (0 vanilla uses).
- Trait ids are exact. `conservative_nationalist` is a country leader trait (defined once in `common/country_leader/00_traits.txt`), but `nationalist` is defined in no country leader, unit leader or scientist trait file and appears in no vanilla script as a trait. [vanilla-confirmed 1.19.4.1] What the game does with an undefined trait id in `traits = { }` is [unverified]; check every id against these folders before use.
<!-- kit:end id="char-country-leader-traits-vanilla" -->

### Sprite <a id="Sprite"></a>

*See also: Sprite overview*

The `sprite = 1` argument decides shown on the paper for the advisor when an advisor has this. This uses the `GFX_idea_traits_strip` [spriteType](<graphical_asset_modding.md>), which can be defined in any `/Hearts of Iron IV/interface/*.gfx` file, by default `ideas.gfx`. However, it's generally better to avoid overlap in files from the base game to decrease the needed amount of work to make the mod be up to date. Instead, it's possible to overwrite the sprite in a new file.
In particular, in case of there being defined several spriteTypes with the same name, the game picks the one that was evaluated later. The filename is used to order the files for the evaluation, using ASCII order, so a file later in that order may contain an overriding sprite. For example, it may be `interface/xyz_override.gfx`, since "x" is later than "i" in the ASCII alphabet. This may be its contents:

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

## Unit leader traits <a id="Unit_leader_traits"></a>

Units leader traits are defined in any `/Hearts of Iron IV/common/unit_leader/*.txt` file, possible to assign to unit leader characters of any type as well as operatives. Each one is defined within the `leader_traits = { ... }` block as a separate entry with the name of the trait's ID.

<!-- kit:begin id="char-unit-leader-traits-vanilla" at="section:Unit_leader_traits" -->
**Kit note** Unit leader traits in vanilla: 196 traits in six `leader_traits` blocks across the `common/unit_leader/` files (`00_traits.txt`, `ETH_traits.txt`, `JAP_traits.txt`, `NSB_traits.txt`, `SIA_traits.txt`, `SWE_traits.txt`). `type` values used: `navy` 62, `land` 42, `all` 42, `corps_commander` 37, `operative` 12, `field_marshal` 10. `trait_type` values used: `personality_trait` 96, `assignable_trait` 46, `status_trait` 15, `basic_terrain_trait` 12, `basic_trait` 8, `assignable_terrain_trait` 2, `exile` 1, which is the full list the wiki gives. [vanilla-confirmed 1.19.4.1] `common/unit_leader/`.

The same folder also holds the skill-level definitions covered under "Unit leaders", and the head of `common/unit_leader/00_traits.txt` is a comment that documents the trait format. [vanilla-confirmed 1.19.4.1] `common/unit_leader/00_traits.txt`.
<!-- kit:end id="char-unit-leader-traits-vanilla" -->

### Localisation <a id="Localisation"></a>

Localisation is defined by using the trait's name as a localisation key within any localisation file, with an entry as  `my_trait: "My trait"`. A description can be added by appending `_desc` to the end as `my_trait_desc: "My description"`.

### GFX <a id="GFX"></a>

The picture is defined in any `/Hearts of Iron IV/interface/*.gfx` file as a spriteType with the name of `GFX_trait_<trait's name>`. As an example with a trait of the name `not_polish_person`, a sprite definition with the name of `GFX_trait_not_polish_person` will be used. The `/Hearts of Iron IV/interface/*.gfx` file containing the sprite will have these contents:

```text
spriteTypes = {
    spriteType = {
        name = GFX_trait_not_polish_person
        texturefile = gfx/foldername/filename.dds
    }
}
```

### General arguments <a id="General_arguments"></a>

| Argument | Value type | Example | Effects | Notes |
| --- | --- | --- | --- | --- |
| type | Type(s) | `type = corps_commander``type = { land navy }` | Assigns a type to the trait, which gets used to assign which characters are able to receive it. | The types include `all`, `land`, `navy`, `operative`, `corps_commander`, and `field_marshal` |
| trait_type | Trait type | `trait_type = assignable_trait` | Assigns a type to the trait, which gets used to assign where it's positioned on the user interface, as well as deciding if and when it's possible to assign. | The types include `basic_trait` (for operatives), `personality_trait`, `assignable_trait`, `basic_terrain_trait`, `assignable_terrain_trait`, `status_trait`, and `exile` |
| show_in_combat | Boolean | `show_in_combat = yes` | Makes this specified trait show up in the combat menu among other bonuses. |  |
| allowed | Triggers | *(example below)* | Triggers that are checked when trying to assign the trait to a unit leader, making it fail to assign if false. Checked in the scope of the unit leader. | FROM is the country that recruited the character. |
| ai_will_do | [MTTH block](<ai_modding.md>) | *(example below)* | Decides the weight that AI has for picking this trait. | A weight of 0 will result in AI never picking it. |
| new_commander_weight | [MTTH block](<ai_modding.md>) | *(example below)* | Decides the weight that the trait has for new randomly-generated unit leaders. | A weight of 0 will result in it never appearing for randomly-generated unit leaders. Only can be defined for traits with the personality_trait type. |
| slot | Character slot | `slot = army_chief` | Decides which advisor slot gets used by the officer corps role that can be assigned to this unit leader. |  |
| specialist_advisor_trait | [Country leader trait](#Country_leader_traits) | `specialist_advisor_trait = my_trait` | Creates a specialist officer corps role that can be assigned to this unit leader using the specified advisor trait as the base. |  |
| expert_advisor_trait | [Country leader trait](#Country_leader_traits) | `expert_advisor_trait = my_trait` | Creates a expert officer corps role that can be assigned to this unit leader using the specified advisor trait as the base. |  |
| genius_advisor_trait | [Country leader trait](#Country_leader_traits) | `genius_advisor_trait = my_trait` | Creates a genius officer corps role that can be assigned to this unit leader using the specified advisor trait as the base. |  |
| unit_type | `type = <sub-unit type>` | *(example below)* | Limits the selection of units on which the modifiers can apply on to those that have the sub-unit in a composition. | Sub-units are defined within `/Hearts of Iron IV/common/units/*.txt` files. In order for it to apply those that are majority-made out of a sub-unit, [division_has_majority_template](<triggers.md>) can be used in unit_trigger. |
| unit_trigger | Triggers | *(example below)* | Applies a division-scoped trigger block that must be met for the unit to be modified. |  |

**Example: allowed**

```text
allowed = {
    FROM = { tag = POL }
}
```

**Example: ai_will_do**

```text
ai_will_do = {
    base = 3
    modifier = {
        FROM = { tag = POL }
    }
}
```

**Example: new_commander_weight**

```text
new_commander_weight = {
    base = 0
}
```

**Example: unit_type**

```text
unit_type = {
    type = infantry
    type = militia
}
```

**Example: unit_trigger**

```text
unit_trigger = {
    division_has_majority_template = camelry
    owner = { neutrality > 0.5 }
}
```

<!-- kit:begin id="char-trait-general-extras" at="section:General_arguments" -->
**Kit addition** Trait keys that vanilla uses but the tables on this page omit. All rows: [vanilla-confirmed 1.19.4.1] `common/unit_leader/00_traits.txt` (counts over 196 traits).

| Key | Uses | Notes |
| --- | --- | --- |
| `country_trigger` | 5 | Trigger block with country-scope triggers (`has_idea = ...`), used to gate officer traits such as `submarine_officer` on the absence of academy spirits. |
| `allowed_ship_equipments` | 5 | List of ship hull ids, for example `ship_hull_submarine`, that the trait applies to. |
| `leader_default_proximity_offset` | 2 | Integer on `trait_cautious` (1) and `trait_reckless` (-1). |
| `any_parent`, `all_parents`, `parent` | 41, 0, 1 | See the correction under "Selection". |
<!-- kit:end id="char-trait-general-extras" -->

### Modifiers and effects <a id="Modifiers_and_effects"></a>

These arguments are for the modifiers that the trait gives to the unit leader, whether it's the modifiers themselves or something related to them, as well as effects executed related to the trait.

| Argument | Value type | Example | Effects | Notes |
| --- | --- | --- | --- | --- |
| modifier | Modifiers | *(example below)* | Assigns the [modifiers](<modifiers.md>) that the trait grants to the divisions that the unit leader leads. | Possible to specify the terrain by scoping into it. Terrain types are defined in `/Hearts of Iron IV/common/terrain/*.txt`. |
| non_shared_modifier | Modifiers | *(example below)* | Assigns the [modifiers](<modifiers.md>) that the trait grants to the unit leader themselves. | While in theory identical to the prior modifier, this has a different tooltip, so it shows up differently in-game. |
| corps_commander_modifier | Modifiers | *(example below)* | Assigns the [modifiers](<modifiers.md>) that the trait grants to the army leader when in the role of a corps commander, i.e. leading units directly rather than leading other generals. | If a field marshal is assigned to lead divisions directly rather than other generals, this will apply on them. |
| field_marshal_modifier | Modifiers | *(example below)* | Assigns the [modifiers](<modifiers.md>) that the trait grants to the army leader when in the role of a field marshal, i.e. leading other generals that lead divisions. | If a field marshal is assigned to lead divisions directly rather than other generals, this will *not* apply on them. |
| sub_unit_modifiers | Modifiers | *(example below)* | Assigns the [modifiers](<modifiers.md>) that the trait grants to the division brigades that make up the divisions that the army leader leads or, similarly, ships that make up the fleet that the navy leader leads. | Brigades are defined in `/Hearts of Iron IV/common/units/*.txt`. What's used in the definition as arguments is possible to apply as a multiplicatory sub-unit modifier. |
| <skill type> | Integer | `attack_skill = 2` | Adds a flat bonus to the specified skill. | The list of skills defined for unit leaders earlier in the page |
| <skill type>_factor | Percentual | `defense_skill_factor = 1` | Adds a multiplicatory bonus to the specified skill. `1` would add 100%, doubling it, for example. | The list of skills defined for unit leaders earlier in the page |
| override_effect_tooltip | Localisation key | `override_effect_tooltip = my_effect_tt` | Hides the effects of the trait, replacing the tooltip with the value of this localisation key. | English localisation is defined in any `/Hearts of Iron IV/localisation/english/*_l_english.yml` file. Similarly for other languages. |
| custom_effect_tooltip | Localisation key | `custom_effect_tooltip = my_effect_tt` | Appends the value of this localisation key to the tooltip showing the effects of the trait. | English localisation is defined in any `/Hearts of Iron IV/localisation/english/*_l_english.yml` file. Similarly for other languages. |
| enable_ability | Ability | `enable_ability = my_ability` | Enables an ability that can be used by the unit leader in combat. | Abilities are defined in `/Hearts of Iron IV/common/abilities/*.txt` |
| on_add | Effects | *(example below)* | Defines the effects that would be executed on the unit leader when the trait is added. |  |
| on_remove | Effects | *(example below)* | Defines the effects that would be executed on the unit leader when the trait is removed. |  |
| daily_effect | Effects | *(example below)* | Defines the effects that would be executed on the unit leader every day if they have the trait. |  |

**Example: modifier**

```text
modifier = {
    planning_speed = 0.2
    urban = {
        movement = 0.1
    }
}
```

**Example: non_shared_modifier**

```text
non_shared_modifier = {
    experience_gain_factor = 0.3
}
```

**Example: corps_commander_modifier**

```text
corps_commander_modifier = {
    max_commander_army_size = 3
}
```

**Example: field_marshal_modifier**

```text
field_marshal_modifier = {
    supply_consumption_factor = 0.5
}
```

**Example: sub_unit_modifiers**

```text
sub_unit_modifiers = {
    artillery_brigade = {
        max_strength = 0.1
    }
}
```

**Example: on_add**

```text
on_add = {
    promote_leader = yes
}
```

**Example: on_remove**

```text
on_remove = {
    remove_unit_leader = yes
}
```

**Example: daily_effect**

```text
daily_effect = {
    gain_xp = 1
}
```

### Selection <a id="Selection"></a>

These arguments are related to the menu for selecting traits. This includes experience. If the trait is manually assigned only, these can be omitted.

| Argument | Value type | Example | Effects | Notes |
| --- | --- | --- | --- | --- |
| mutually_exclusive | Trait | `mutually_exclusive = my_trait` | Makes the specified trait mutually exclusive with the other trait, making it impossible to pick if that one was selected and drawing the arrows in the menu. | Both traits require defining this to work properly. |
| parent | Trait | `parent = my_trait` | Makes the specified trait be marked as a parent, making it be required to pick the current trait and drawing the line in the menu. | Multiple parents can be specified by defining `parent = my_trait_2` several times. |
| num_parents_needed | Integer | `num_parents_needed = 3` | Sets the required amount of parents needed to select the trait. | If omitted or set to `-1`, then assumes that all parents are necessary. |
| gui_row | Integer | `gui_row = 3` | Sets the row on which the trait is located. | If omitted or set to `-1`, then the trait does not appear in the unlockable trait tree. Starts at 0. |
| gui_column | Integer | `gui_column = 3` | Sets the column on which the trait is located. | If omitted or set to `-1`, then one is automatically picked depending on the trait_type. |
| prerequisites | Triggers | *(example below)* | Triggers that must be met in order for assigning the trait to be possible. | Checked in the unit leader scope. |
| custom_prerequisite_tooltip | Localisation key | `custom_prerequisite_tooltip = my_prerequisite_tt` | Changes the tooltip of the conditions required for picking the trait to the following localisation key. Useful if a trigger within has no tooltip. | English localisation is defined in any `/Hearts of Iron IV/localisation/english/*_l_english.yml` file. Similarly for other languages. |
| cost | Decimal | `cost = 1500` | The experience required in order to assign this trait to a unit leader. |  |
| gain_xp | Triggers | *(example below)* | Triggers that must be met in order to gain experience that'd make assigning this trait possible. | Checked in the [combatant](<triggers.md#Combat>) scope. |
| gain_xp_leader | Triggers | *(example below)* | Triggers that must be met in order to gain experience that'd make assigning this trait possible. | Checked in the unit leader scope. |
| gain_xp_on_spotting | Decimal | `gain_xp_on_spotting = 7` | The amount of experience gained when the admiral spots an enemy fleet. |  |
| custom_gain_xp_trigger_tooltip | Localisation key | `custom_gain_xp_trigger_tooltip = my_prerequisite_tt` | Changes the tooltip of the conditions required for gaining experience for the trait to the following localisation key. Useful if a trigger within has no tooltip. | English localisation is defined in any `/Hearts of Iron IV/localisation/english/*_l_english.yml` file. Similarly for other languages. |
| trait_xp_factor | Triggers | *(example below)* | Modifies the amount of experience gained towards other traits if the unit leader has this trait. | 0.1 would mean that the unit leader gains 10% more experience, not that it gains 10% as much. |

**Example: prerequisites**

```text
prerequisites = {
    defense_skill_level > 3
}
```

**Example: gain_xp**

```text
gain_xp = {
    is_amphibious_invasion = yes
}
```

**Example: gain_xp_leader**

```text
gain_xp_leader = {
    num_units > 10
}
```

**Example: trait_xp_factor**

```text
trait_xp_factor = {
    my_trait = 0.1
}
```

<!-- kit:begin id="char-trait-selection-correction" at="section:Selection" -->
**Kit correction** The parent syntax in the table above differs from the vanilla format. The comment at the top of `common/unit_leader/00_traits.txt` documents it as a block: `parent = { traits = { a b c } num_parents_needed = 1 }`, which can be repeated, plus two shorthands: `any_parent = { a b c }` (one of them is enough) and `all_parents = { a b c }` (every one is needed). Vanilla uses `any_parent` in 41 traits and the block `parent` once (with `num_parents_needed = 2`); `all_parents` and a plain `parent = trait_id` appear nowhere. `hoi4.exe` has the validation message "num_parents_needed is superior to the number of parents". The wiki's `parent = my_trait` with a separate `num_parents_needed` is [unverified]; write the vanilla form. [vanilla-confirmed 1.19.4.1] `common/unit_leader/00_traits.txt`; the message is [unverified] (executable string only).
<!-- kit:end id="char-trait-selection-correction" -->

### Example <a id="Example"></a>

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

## References <a id="References"></a>

1. ↑ `NDefines.NCountry.FEMALE_UNIT_LEADER_BASE_CHANCE = { 0.5, 0.5, 0.5, 0.5, 0.5, 0.5 }`

---

## Navigation

**[Modding](<modding.md>)**

- **Documentation**: [Effects](<effects.md>) • [Triggers](<triggers.md>) • [Defines](<defines.md>) • [Modifiers](<modifiers.md>) • [List of modifiers](<list_of_modifiers.md>) • [Scopes](<scopes.md>) • [Localisation](<localisation.md>) • [On actions](<on_actions.md>) • [Data structures](<data_structures.md>) • [Flags](<data_structures.md#Flags>) • [Event targets](<data_structures.md#Event_targets>) • [Country tag aliases](<data_structures.md#Country_tag_aliases>) • [Variables](<data_structures.md#Variables>) • [Arrays](<data_structures.md#Arrays>)
- **Scripting**: [Achievements](<achievement_modding.md>) • [AI](<ai_modding.md>) • [AI focuses](<ai_focuses.md>) • [Autonomous states](<autonomy_state_modding.md>) • [Balances of power](<balance_of_power_modding.md>) • [Bookmarks/Scenarios](<bookmark_modding.md>) • [Game rules](<bookmark_modding.md#Game_rules>) • [Buildings](<building_modding.md>) • [Cosmetic tags](<cosmetic_tag_modding.md>) • [Countries](<country_creation.md>) • [Divisions](<division_modding.md>) • [Decisions](<decision_modding.md>) • [Doctrines](<doctrine_modding.md>) • [Equipment](<equipment_modding.md>) • [Events](<event_modding.md>) • [Factions](<faction_modding.md>) • [Ideas](<idea_modding.md>) • [Ideologies](<ideology_modding.md>) • [Military industrial organizations](<military_industrial_organization_modding.md>) • [National focuses](<national_focus_modding.md>) • [Resources](<resources_modding.md>) • [Scripted GUI](<scripted_gui_modding.md>) • [Technologies and doctrines](<technology_modding.md>) • [Units](<unit_modding.md>)
- **Map**: [Map](<map_modding.md>) • [States](<state_modding.md>) • [Supply areas](<supply_areas_modding.md>) • [Strategic regions](<strategic_region_modding.md>)
- **Graphical**: [Interface](<interface_modding.md>) • [Graphical assets](<graphical_asset_modding.md>) • [Entities](<entity_modding.md>) • [Posteffects](<posteffect_modding.md>) • [Particles](<particle_modding.md>) • [Fonts](<font_modding.md>)
- **Cosmetic**: [Portraits](<portrait_modding.md>) • [Namelists](<namelist_modding.md>) • [Music](<music_modding.md>) • [Sound](<sound_modding.md>)
- **Other**: [Console commands](<console_commands.md>) • [Troubleshooting](<troubleshooting.md>) • [Mod structure](<mod_structure.md>) • [Mods](<mods.md>) • [Nudger](<nudger.md>)
- **Kit pages (not on the wiki)**: [Collection modding](<collection_modding.md>) • [Defines additions](<defines_additions.md>) • [Game rule modding](<game_rule_modding.md>) • [Intelligence operation modding](<intelligence_operation_modding.md>) • [Map mode modding](<map_mode_modding.md>) • [Occupation and resistance modding](<occupation_and_resistance_modding.md>) • [Peace conference modding](<peace_conference_modding.md>) • [Raid modding](<raid_modding.md>) • [Script constant modding](<script_constant_modding.md>) • [Special project modding](<special_project_modding.md>)
