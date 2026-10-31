# Division modding

*Offline snapshot of the Hearts of Iron IV Wiki page "Division modding", revision 105628, captured 2026-10-31. Wiki text by the wiki's contributors under CC BY-SA 3.0 (see LICENSE.txt); kit blocks are local additions under the same license.*

<!-- kit:begin id="review" at="top" build="1.19.3.0" checked="2026-10-31" revision="105628" sources="history/units/ history/countries/ common/units/ common/units/names_divisions/ common/defines/00_defines.lua documentation/effects_documentation.md hoi4.exe" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Checked against all 609 files in `history/units/` (land, `_nsb`, `_air_legacy`, `_air_bba`, `_naval_legacy`, `_naval_mtg` and event OOBs), the `oob`, `set_oob`, `set_naval_oob` and `set_air_oob` lines of the country history files, 1025 division name groups in `common/units/names_divisions/`, the `NMilitary` defines, the unit effects in the documentation, and tokens in `hoi4.exe`.
Kit blocks added: `division-oob-files` (file naming and DLC selection; the wiki's `_legacy` land example is wrong), `division-template-keys`, `division-unit-effects`, `division-placement-keys`, `division-name-groups`, `division-equipment-production`, `division-air-wings`, `division-navy-keys`, `division-regiments-correction`, `division-support-correction`, `division-aircraft-note`, `division-ship-lists-note`, `division-references-note`.
Gaps left: the effect of the root-level `start_equipment_factor` and of template `role` and `obsolete` is inferred from usage, and the ship `ordered_name` lookup was not traced to a name file.
<!-- kit:end id="review" -->

## Table of contents

- [Land units](#Land_units)
  - [Kit: How vanilla names and selects order of battle files](#kit-division-oob-files)
  - [Division template](#Division_template)
  - [Kit: Division template keys and limits](#kit-division-template-keys)
  - [Division placement](#Division_placement)
  - [Kit: Division placement keys in vanilla](#kit-division-placement-keys)
- [Equipment production](#Equipment_production)
- [Adding Air Wings](#Adding_Air_Wings)
  - [Kit: Air wing keys in vanilla](#kit-division-air-wings)
- [Adding Navies](#Adding_Navies)
  - [Kit: Fleet, task force and ship keys in vanilla](#kit-division-navy-keys)
  - [Man the Guns](#Man_the_Guns)
  - [Non-Man The Guns](#Non-Man_The_Guns)
- [List of Units](#List_of_Units)
  - [Regiments](#Regiments)
  - [Support Companies](#Support_Companies)
  - [Aircraft](#Aircraft)
  - [Ship Categories](#Ship_Categories)
  - [MTG Ship Equipment](#MTG_Ship_Equipment)
  - [Non-MTG Ship Equipment](#Non-MTG_Ship_Equipment)
- [References](#References)

---

*This article is for creating divisions as part of a country's military. For sub-units making up the construction of division templates, see [Unit modding](<unit-modding.md>).*

Units are the foundations of Hearts of Iron, and can be broken down into air wings, divisions and naval task forces. The definitions are located within `/Hearts of Iron IV/history/units/*.txt` files and can be loaded by using the [load_oob effect](<effects.md>) or [various attributes inside of country history](<country-creation.md#Order_of_battle>). The filename is irrelevant for interpretation, but it must match up with the effect or the attribute used to load it.

The game uses orders of battle to define the state of the country's military. Traditionally, the starting equipment production is defined in them, using an [effect](<effects.md>) block. Optionally, the current focus progress may be included.
**Each order of battle must be loaded in order for the units to show up.** For the starting state of the country's military, [this is done in country history](<country-creation.md#Order_of_battle>). [The load_oob effect](<effects.md>) can be used to load one mid-game, which will add the information in the order of battle to the current information of the country, creating division templates and units and executing the effects.

The internal names for sub-units can be found in `/Hearts of Iron IV/common/units/*.txt` files, [localisation can be checked as well](<modding.md#Searching_multiple_files>).

## Land units <a id="Land_units"></a>

The land unit order of battle is usually the one that's loaded with `oob` or `set_oob` in country history. Most commonly, one is used since most definitions don't differ by DLC. However, if tank equipment types are referenced, such as when a unit is forced to use a certain tank equipment type or starting equipment production includes tanks, this is split into 2 files divided by the ![No Step Back](media/country-creation_1d4220f262__img16.png)No Step Back DLC, with an if statement in the place that loads it deciding whether one should be loaded, such as the following in a country history file:

```text
if = {
    limit = { has_dlc = "No Step Back" }
    set_oob = "TAG_1936_nsb"
    else = { set_oob = "TAG_1936_legacy" }
}
```

<!-- kit:begin id="division-oob-files" at="section:Land_units" -->
### Kit: How vanilla names and selects order of battle files <a id="kit-division-oob-files"></a>

**Kit correction** The land example above is out of date: vanilla has no `TAG_1936_legacy` land file. The land file without a suffix is the base-game version (`set_oob = "AFG_1936"` when the country does not have No Step Back) and `TAG_1936_nsb` is the No Step Back version (`set_oob = "AFG_1936_nsb"`), each under its own `if` with `has_dlc = "No Step Back"` or `NOT = { has_dlc = ... }`. The suffix `_legacy` appears only on air and naval files. [vanilla-confirmed 1.19.3] `history/countries/AFG - Afghanistan.txt`, `history/units/`

File names in `history/units/` (609 files). The file name is free; the string in the effect must match it. Suffix counts are files. [vanilla-confirmed 1.19.3] `history/units/`

| Suffix | Files | Holds | Selected by |
| --- | --- | --- | --- |
| `<TAG>_<year>.txt` | 177 | land templates, divisions, starting production | `oob = "..."` or `set_oob` |
| `_nsb` | 24 | land version for No Step Back | `has_dlc = "No Step Back"` |
| `_air_bba` / `_air_legacy` | 89 / 89 | air wings | `has_dlc = "By Blood Alone"` or not |
| `_naval_mtg` / `_naval_legacy` | 57 / 62 | fleets | `has_dlc = "Man the Guns"` or not |
| `_naval`, `_Naval`, `_Naval_Legacy` | 7, 2, 2 | fleets in countries without the MTG split | plain `set_naval_oob` |
| `_sea` | 15 | a main OOB with division templates (`CHI_1936_sea.txt`); used by `oob` (8) and `set_oob` (7) | plain `oob` or `set_oob` |
| other suffixes (`_ncns`, `_lar`, `_LaR`, `_mun`, `_GOE`, `_BBA`, `_nsb_LaR`, ...) | a few | DLC or mod-pack variants chosen with `set_oob` | their own `has_dlc` gates [unverified] |
| event and decision files | the rest | `load_oob` targets such as `unlock_tanks`, `cossack_host`, `Civil_War` | `load_oob = "..."` |

In country history files vanilla uses these lines: top-level `oob = "TAG_1936"` (192 uses across 110 files), `set_oob` (56 plain, 25 with `_nsb`), `set_naval_oob` (62 `_naval_legacy`, 57 `_naval_mtg`, 7 `_naval`) and `set_air_oob` (95 `_air_legacy`, 95 `_air_bba`). The air and naval pair is chosen like this: [vanilla-confirmed 1.19.3] `history/countries/ARG - Argentina.txt`

```text
oob = "ARG_1936"
IF = {
    limit = { has_dlc = "Man the Guns" }
    set_naval_oob = "ARG_1936_naval_mtg"
    ELSE = { set_naval_oob = "ARG_1936_naval_legacy" }
}
IF = {
    limit = { has_dlc = "By Blood Alone" }
    set_air_oob = "ARG_1936_air_bba"
    ELSE = { set_air_oob = "ARG_1936_air_legacy" }
}
```

What the effects do. `set_oob`, `set_naval_oob` and `set_air_oob` register an order of battle to load at game start; each replaces an earlier registration with the same key (no key, `naval`, `air`), so a mod can swap only the air file. `set_keyed_oob = { key = naval name = "ENG_1936_Naval" }` does the same for any key. They are meant for history files. `load_oob` loads a file immediately and is used in decisions, events and focuses (32 vanilla files). [docs] `documentation/effects_documentation.md`; [vanilla-confirmed 1.19.3] `common/decisions/GER.txt`

Root keys that vanilla OOB files use: `division_template` (804 blocks), `units` (408 files), `instant_effect` (329), `air_wings` (188), `start_equipment_factor` (22), `create_colonial_division_template` (5). [vanilla-confirmed 1.19.3] `history/units/*.txt`
<!-- kit:end id="division-oob-files" -->

### Division template <a id="Division_template"></a>

*See also: [Effect § division_template](<effects.md>)*

Land units require a template of some sort, which assigns the necessary information. The template definition is equivalent to the `division_template` effect internally. A simple template can be defined as such:

```text
division_template = {
    name = "Blueskirt Division"
    regiments = {
        infantry = { x = 0 y = 0 }
        infantry = { x = 0 y = 1 }
        artillery_brigade = { x = 1 y = 0 }
        artillery_brigade = { x = 1 y = 1 }
    }
    support = {
        artillery = { x = 0 y = 0 }
    }
}
```

- `name = ""` is the name of the division template as it shows up in the template selection. This will also get used for creating or modifying units.
- `regiments = { ... }` and `support = { ... }` decide the sub-units of the template, meaning combat battalions and support companies respectively. In particular:
  - `subunit = { x = 0 y = 0 }` decides the placement of the specified sub-unit. The coordinates represent the Cartesian coordinate system, where (0,0) is the top-left corner, x goes left-to-right, and y goes up-to-down. For a unit to be placed as a support company, it must have `group = support` in its definition, and to be placed in combat battalions, it must have a different group. The group cannot change in a single y column.

By default, the combat battalions have 5 columns and 5 rows, while the support companies have 1 column and 5 rows.[1] The max index is one less than the total amount.

There are also optional arguments:

- `division_names_group = USA_INF_01` forcefully changes the name group used for new divisions, defined in `/Hearts of Iron IV/common/units/names_divisions/*.txt` files. This is used to automatically generate names and numeration for new divisions, such as a division newly created by the player being named "1st 'Big Red One' Division". If not set, the template automatically picks the name group based on the sub-units.
- `is_locked = yes` will make the division locked, preventing the player from changing any of its information and creating/deleting/editing units with it. Defaults to no if unset.
- `force_allow_recruiting = yes` will allow recruiting new divisions from the template even if it locked. Has no effect on non-locked templates. Default to no if unset.
- `division_cap = 12` is the maximum amount of divisions that may be recruited with this template. The template has to be locked. Defaults to no cap if unset.
- `priority = 0` is the supply receiving priority. The options are 0 for "Reserves", 1 for default, and 2 for "Elite". Default to 1 if unset.
- `template_counter = 10` is used to override the default icon used for the position. The particular example with 10 will make sure that the sprites with the name of `GFX_div_templ_10_large` and `GFX_div_templ_10_small` will get used.
- `override_model = GER_infantry_entity` is used to change the [entity](<entity-modding.md>) that is used by divisions made from this template. Defaults to automatically determining based on the sub-units if unset.

<!-- kit:begin id="division-template-keys" at="section:Division_template" -->
### Kit: Division template keys and limits <a id="kit-division-template-keys"></a>

**Kit addition** Grid sizes. The page's reference [1] still holds, and there is a third grid: `MAX_REGIMENTAL_SUPPORT_WIDTH` is 5 and `MAX_REGIMENTAL_SUPPORT_HEIGHT` is 1 (a row), with `REGIMENTAL_SUPPORT_REQUIRED_BATTALIONS = { 3 }` (a regimental support needs 3 battalions in its row). Headquarters templates have `MAX_HQ_REGIMENTAL_SUPPORT_WIDTH` and `_HEIGHT` of 0. In vanilla templates, `regiments` coordinates reach x 4 and y 4, `support` always uses `x = 0` with y up to 4, and `regimental_support` (4 templates, all CZE) uses `x = 1 y = 0`. [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua`, `history/units/CZE_1936.txt`

Usage of the documented keys across the 804 vanilla templates, and keys the page omits. [vanilla-confirmed 1.19.3] `history/units/*.txt`

| Key | Count | Notes |
| --- | --- | --- |
| `name`, `regiments` | 804 | Always present. |
| `division_names_group` | 777 | Almost every template sets it. |
| `support` | 350 | Many templates have none. |
| `template_counter` | 110 | Icon index. |
| `priority` | 135 | Values 0 (102 templates), 2 (27) and 1 (6), as the page describes. |
| `override_model` | 43 | Entity name such as `ITA_infantry_alt_2_entity`. |
| `is_locked` | 43 | |
| `obsolete` | 32 | `yes` on old templates (for example `ITA_1936.txt`); marks the template as obsolete in the template list. |
| `role` | 22 | AI or garrison role. Values seen: `garrison` (8), `infantry` (6), `armor` (2), `militias` (2), `motorized` (2), `mobile` (1), `suppression` (1). |
| `force_allow_recruiting` | 12 | |
| `division_cap` | 8 | |
| `regimental_support` | 4 | Block of regimental support sub-units, for example `field_guns = { x = 1 y = 0 }`. |
| `ingame_set_template_counter` | 2 | `yes` next to `template_counter` (`INS_1936.txt`). |

The meaning of `role` and `obsolete` is read from usage and file comments, not from documentation. [unverified]
<!-- kit:end id="division-template-keys" -->

<!-- kit:begin id="division-unit-effects" at="section:Division_template" -->
**Kit addition** Effects that create or change divisions and templates after the game has started, all in country scope unless noted. [docs] `documentation/effects_documentation.md`

| Effect | Use |
| --- | --- |
| `division_template` | Adds a template to the country (the same block as in an OOB file). |
| `create_unit` | Spawns divisions like an OOB: `division = "name = ... division_template = ..."`, `owner`, `prioritize_location`, `allow_spawning_on_enemy_provs`, `country_score`, `count`, `id`, `divisional_commander_xp`. Any scope. |
| `delete_unit` | Deletes units filtered by `division_template`, `id` or `state`; `disband = yes` refunds equipment and manpower. |
| `delete_units` | Deletes all units of one `division_template`; `disband` as above. |
| `delete_unit_template_and_units` | Deletes a template and its units. |
| `change_division_template` | Switches a division to another template. |
| `add_units_to_division_template` | Adds sub-units to template slots by column: `regiments = { infantry = 0 }`, `support = { ... }`, `regimental_support = { ... }`. |
| `set_division_template_lock`, `set_division_template_cap`, `set_division_force_allow_recruiting` | Block forms `{ division_template = <name> is_locked = yes }`, `{ division_template = <name> division_cap = 12 }` and `{ division_template = <name> force_allow_recruiting = yes }`. |
| `create_colonial_division_template` | Creates a template for an overlord's subject: `subject = RAJ` plus a `division_template` block. |
| `transfer_units_fraction` | Moves a fraction of army, navy, air and stockpile to another country. |
| `unlock_subunit` | Unlocks a sub-unit for the country (used by doctrines and focuses). |
<!-- kit:end id="division-unit-effects" -->

### Division placement <a id="Division_placement"></a>

The `units = { ... }` block is used for positioning land and naval divisions. In particular, a land division placement is done via `division = { ... }`:

```text
units = {
    division= {
        name = "1st Blueskirt Division"
        location = 9392 # Edinburgh
        division_template = "Blueskirt Division"
        start_experience_factor = 0.2
        start_equipment_factor = 0.3
    }
    division= {
        division_name = {
            is_name_ordered = yes
            name_order = 35
        }
        location = 6488
        division_template = "Infanterie-Division"
        force_equipment_variants = { infantry_equipment_0 = { owner = "SCO" } }
        officer = {
            name = SCO_officer_1
            portraits = {
                army = {
                    large = GFX_SCO_officer_1
                    small = GFX_SCO_officer_generic_small
                }
            }
        }
    }
}
```

For the division naming, there are two mutually-exclusive ways to do so:

- `name = "Unit's name"` directly changes the name of the division to the given string.
- `division_name = { ... }` instead uses the name group assigned to the division template:
  - `is_name_ordered = yes` is mandatory to include.
  - `name_order = 35` sets the number that gets used for the numeration. If the name group's `ordered = { ... }` includes this number, that entry gets used. Otherwise, the `fallback_name` is used.

There are these mandatory arguments in addition to the name:

- `location = 1234` is the province where the unit should be positioned.
- `division_template` is the name of the template that the unit should use. Generally best to limit to the one that's defined in the same file.

There are also optional arguments:

- `start_experience_factor = 0.2` sets the experience level of the division (from Greens to Veterans) in the range from 0 to 1. If unset, defaults to 0. The experience level boundaries in the base game are `{ 0.1, 0.3, 0.75, 0.9 }`.[2]
- `start_equipment_factor = 0.5` decides the starting equipment level of the division, not deciding on the manpower. The equipment is not subtracted from the reserves of the country. If unset, defaults to 1.
- `start_manpower_factor = 0.3` decides the starting manpower level of the division. If unset, then it's automatically subtracted from the reserves of the country until the highest possible level.
- `force_equipment_variants = { ... }` is a set of equipment types that the division should use, replacing the default. Each entry in there is `equipment_type = { ... }`, which may include:
  - `owner = TAG` is the owner of the equipment that should be used. This should be the same as the country which gets the order of battle.
  - `creator = TAG` is the original creator of the equipment that should be used. This is used to determine the variants, and it defaults to the owner if not specified.
  - `amount = 14` is how much of the equipment should be there. The rest of required equipment within the archetype will remain ungiven.
  - `version_name = "Variant's name"` is the name of the equipment variant that should be used. If the equipment type requires a variant to use, such as tanks in ![No Step Back](media/country-creation_1d4220f262__img16.png)No Step Back, this is mandatory. Otherwise, this is optional.
- `officer = { ... }` is a [character definition](<character-modding.md>) that will be used for the divisional commander if promoted to a commander or the officer corps system is used. In particular, these attributes are common inside:
  - `name = loc_key` is the [localisation](<localisation.md>) key to be used as the division commander's name.
  - `portraits = { army = { large = "GFX_portrait_SCO_character" small = "GFX_idea_SCO_character" } }` is the portrait that the division commander must use. The large portrait will be used for the corps commander promotion and the small portrait will be used for the officer corps system. If both are unset, [randomly generates a portrait](<country-creation.md#Character_portraits>). If the large is set, the small portrait will default to the name of large portrait with _small appended to the end.

<!-- kit:begin id="division-placement-keys" at="section:Division_placement" -->
### Kit: Division placement keys in vanilla <a id="kit-division-placement-keys"></a>

**Kit addition** Counts over the 5074 divisions in vanilla `units = { }` blocks. [vanilla-confirmed 1.19.3] `history/units/*.txt`

| Key | Divisions | Notes |
| --- | --- | --- |
| `location`, `division_template` | 5074 | Always present. |
| `division_name` | 3773 | Always `is_name_ordered = yes`; `name_order` in 3694 of them. |
| `name` | 1245 | Direct name. |
| `start_experience_factor` | 4500 | |
| `start_equipment_factor` | 3744 | |
| `force_equipment_variants` | 753 | 754 entries: `owner` (754), `version_name` (90), `creator` (38), `amount` (20). |
| `officer` | 115 | Only `name` (115) and `portraits` (2) seen. |
| `bonus` | 3 | Integer in the Azad Hind file `CA1.txt`; meaning not documented. [unverified] |
| `start_manpower_factor` | 0 | Documented by the wiki and a token in `hoi4.exe`, but no vanilla division uses it. [unverified] |

The page's reference [2] holds: `UNIT_EXP_LEVELS = { 0.1, 0.3, 0.75, 0.9 }` in `NDefines.NMilitary`. [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua`
<!-- kit:end id="division-placement-keys" -->

<!-- kit:begin id="division-name-groups" at="section:Division_placement" -->
**Kit addition** Name groups, the files `division_names_group` refers to, live in `common/units/names_divisions/` (100 files, 1025 groups in vanilla). A group holds `name`, `for_countries`, `can_use` (trigger), `division_types` (sub-unit ids such as `"infantry"` or `"light_armor"`), `fallback_name` (a string with `%d`), `ordered` (a table of numbered names) and, in 385 groups, `link_numbering_with` (another group id whose numbering it continues). `division_types` values seen: `infantry` (281 groups), `cavalry`, `motorized`, `mechanized`, the armor classes, `marine`, `mountaineers`, `paratrooper`, `ranger_battalion`, `militia` and a few others. [vanilla-confirmed 1.19.3] `common/units/names_divisions/*.txt`; the meaning of `link_numbering_with` is inferred from its name [unverified]
<!-- kit:end id="division-name-groups" -->

## Equipment production <a id="Equipment_production"></a>

*Main article: [Effect § add_equipment_production](<effects.md>)*

The equipment production is simulated using the `instant_effect = { ... }` block. This is a regular [effect](<effects.md>) block, any effect can be used here. Usually, the production is added in this manner:

```text
instant_effect = {
    add_equipment_production = {
        equipment = {
	    type = infantry_equipment_0
	    creator = "ARG"
	}
	requested_factories = 1
	progress = 0.19
	efficiency = 100
    }
}
```

The `add_equipment_production = { ... }` has these attributes:

- `equipment = { ... }` decides on which equipment specifically should be made, in particular:
  - `creator = TAG` is the creator of the equipment. Usually it's the same person who makes the equipment, but it may be different for lend-leases.
  - `type = infantry_equipment_0` is the exact equipment type that should be produced. The technology to unlock it, if needed, must be researched by the creator. Equipment can be found in `/Hearts of Iron IV/common/units/equipment/*.txt` files.
  - `version_name = "Variant name"` is the variant that should be used for equipment, [usually defined in country history](<country-creation.md#Variants>). This is mandatory if the equipment requires a variant to produce, such as ships in ![Man the Guns](media/country-creation_1d4220f262__img8.png)Man the Guns or airplanes in ![By Blood Alone](media/ai-modding_04cfcba22e__img12.png)By Blood Alone. Otherwise, it's optional.
- `requested_factories = 1` is the amount of military factories or dockyards that should be dedicated towards producing this equipment type. If unfulfilled, the factories will be assigned into the queue.
- `progress = 0.2` is used to assign the current amount of progress towards a single piece of equipment being finished. This is usually changed for expensive equipment, such as battleships.
- `efficiency = 100` is, with 0 as 0% and 100 as 100%, the production efficiency which the factories should have immediately.

<!-- kit:begin id="division-equipment-production" at="section:Equipment_production" -->
**Kit addition** Vanilla `instant_effect` blocks hold `add_equipment_production` 923 times (plus a few `if` wrappers). The effect takes more keys than the page lists: `name` (172 uses; a string shown for the line), `amount` (399; number of items to build, a value or variable) and `industrial_manufacturer` (614; a military industrial organization written as `mio:<token>`). `requested_factories` and `progress` are set in all 923, `efficiency` in 524; vanilla efficiency values are percentages (100 in 420 uses, 50 in 108), while the documentation example shows `0.1`. [docs] `documentation/effects_documentation.md`; [vanilla-confirmed 1.19.3] `history/units/*.txt`
<!-- kit:end id="division-equipment-production" -->

## Adding Air Wings <a id="Adding_Air_Wings"></a>

```text
air_wings = {
    500 = {
        fighter_equipment_0 = {
            owner = "BRA"
            amount = 10
        }
    }
}
```

- **Air Wings** is the command that creates the air wing.
- **500** is the state where the air wing spawns. The state should have an air base set there.
- **fighter_equipment_0** is the type of aircraft that is in the air wing.
- **Owner** is who created the type of aircraft. Does not need to be the country you are making the file for.
- **Amount** is how many of that type of equipment is in that air wing.

<!-- kit:begin id="division-air-wings" at="section:Adding_Air_Wings" -->
### Kit: Air wing keys in vanilla <a id="kit-division-air-wings"></a>

**Kit addition** The key of each entry in `air_wings` is a state id (453 of 507 entries) or, for carrier-based wings, a quoted ship name (`"HMS Furious" = { ... }`, 54 entries). Carrier wings can also sit in an `air_wings = { }` block inside the `ship` itself (10 ships in the naval files). Each equipment entry holds `owner` and `amount` (1274 of 1274), plus `version_name` (661), `creator` (187) and `create_if_missing` (5). A wing can carry a `name = "..."` string (43) and an optional `ace` block with `modifier`, `name`, `surname`, `callsign`, `is_female` and `portrait` (21 in vanilla); the vanilla comment says the order is important and the ace joins the equipment entry above it. [vanilla-confirmed 1.19.3] `history/units/*_air_*.txt`, `history/units/ENG_1936_air_bba.txt`, `history/units/GER_1936_air_bba.txt`

The equipment ids differ by file family: `_air_legacy` files use ids like `fighter_equipment_0` and `CAS_equipment_1` (the page's list), `_air_bba` files use airframe ids such as `small_plane_airframe_0` (138 uses), `medium_plane_airframe_1` (84) and `small_plane_cas_airframe_0` (47), usually with a `version_name`. Both id families exist in `common/units/equipment/` in 1.19.3. [vanilla-confirmed 1.19.3] `history/units/*.txt`, `common/units/equipment/`

```text
air_wings = {
    129 = {
        small_plane_airframe_0 = { owner = "ENG" amount = 72 version_name = "Hawker Fury" }
    }
    "HMS Furious" = {
        cv_small_plane_airframe_0 = { owner = "ENG" amount = 9 version_name = "Hawker Nimrod" }
    }
}
```

The snippet condenses lines of `ENG_1936_air_bba.txt` (state 129 and the "HMS Furious" entry). [vanilla-confirmed 1.19.3]
<!-- kit:end id="division-air-wings" -->

## Adding Navies <a id="Adding_Navies"></a>

<!-- kit:begin id="division-navy-keys" at="section:Adding_Navies" -->
### Kit: Fleet, task force and ship keys in vanilla <a id="kit-division-navy-keys"></a>

**Kit addition** Counts over the 270 fleets, 692 task forces and 6682 ships in vanilla naval OOBs. [vanilla-confirmed 1.19.3] `history/units/*.txt`

| Level | Keys (count) |
| --- | --- |
| `fleet` | `name` (270), `naval_base` (270, a province id), `task_force` (692) |
| `task_force` | `name`, `location` (692 each), `ship` (6682), `base` (3, a province id; equal to `location` in `AST_1939_naval.txt`) |
| `ship` | `definition` (6682), `equipment` (6682), `name` (6427) or `ordered_name` (255), `pride_of_the_fleet` (64), `start_experience_factor` (769), `officer` (16), `air_wings` (10) |
| ship `equipment` entry | `amount` (6682), `owner` (6682), `version_name` (4289), `creator` (100), `create_if_missing` (3) |

`definition` takes the sub-unit id of the ship category, and vanilla uses exactly seven: `destroyer` (3124), `submarine` (2209), `light_cruiser` (590), `heavy_cruiser` (430), `battleship` (230), `carrier` (69) and `battle_cruiser` (30); all are ids in `common/units/`. `ordered_name = 5` replaces `name` (255 ships); how the number resolves to a ship name was not traced. Every vanilla ship equipment entry sets `owner`, so omitting it (the page's Note 2) is untested in vanilla. [vanilla-confirmed 1.19.3] `history/units/*.txt`, `common/units/`; the `ordered_name` meaning [unverified]
<!-- kit:end id="division-navy-keys" -->

### Man the Guns <a id="Man_the_Guns"></a>

```text
units = {
    fleet = {
        name = "Fleet De Custom" # Name 1
        naval_base = 10980
        task_force = {
            name = "Fleet De Custom" # Name 2
            location = 10980
            ship = {
                name = "NRB Minas Gerasis" # Name 3
                pride_of_the_fleet = yes
                definition = battleship
                equipment = {
                    ship_hull_heavy_1 = {
                        amount = 1
                        owner = BRA
                        version_name = "Minas Geras Class"
                    }
                }
            }
        }

        task_force = {
            name = "Fleet De Submarine" # Name 1
            location = 10980
            ship = {
                name = "NRB Humayta" # Name 2
                definition = submarine
                equipment = {
                    ship_hull_submarine_2 = {
                        amount = 1
                        owner = BRA
                        version_name = "Humayta Class"
                    }
                }
            }
        }
    }
}
```

- **Fleet** begins a new fleet which can comprise of multiple task forces.
- **Name 1** is the name of the fleet.
- **Naval Base** is the location of where the fleet is headquartered.
- **Name 2** is the name of the task force.
- **Location** is where the task force spawns.
- **Ship** creates a new ship within the task force.
- **Pride Of The Fleet** designates a ship as the pride of the fleet. Only one ship can be the Pride Of The Fleet at a time. Optional.
- **Definition** sets what type of ship it is.
- **Equipment** sets what level of equipment the ship uses.
- **Amount** is how much of that equipment the ship uses. Should be kept at one.
- **Owner** is who created the equipment the ship uses and who receives it.
- **Creator** is who will create the ship if the owner has not unlocked the technology. Optional.
- **Version Name** is for custom classes of ship. Optional

Note: The owner or creator country needs to have the technology unlocked and the version needs to exist in their countries history file.

Note 2: While the Owner section is technically optional, if there are multiple classes that use the same ship hull (e.g. ship_hull_cruiser_2) and no owner is defined, it will ignore version_name and use the last class defined in the country history of the said ship hull type.

### Non-Man The Guns <a id="Non-Man_The_Guns"></a>

The only main difference between this section and the Man The Guns section is the equipment.

```text
units = {
    fleet = {
        name = "Armada Argentina"
        naval_base = 12364
        task_force = {
            name = "Armada Argentina"
            location = 12364
            ship = {
                name = "ARA Rivadavia"
                definition = battleship
                equipment = {
                    battleship_1 = {
                        amount = 1
                        owner = ARG
                        version_name = "Rivadavia Class"
                    }
                }
            }
        }
    }
}
```

- **Fleet** begins a new fleet which can comprise of multiple task forces.
- **Name 1** is the name of the fleet.
- **Naval Base** is the location of where the fleet is headquartered.
- **Name 2** is the name of the task force.
- **Location** is where the task force spawns.
- **Ship** creates a new ship within the task force.
- **Definition** sets what type of ship it is.
- **Equipment** sets what level of equipment the ship uses.
- **Amount** is how much of that equipment the ship uses. Should be kept at one.
- **Owner** is who created the equipment the ship uses.
- **Version Name** is for custom classes of ship. Optional

## List of Units <a id="List_of_Units"></a>

### Regiments <a id="Regiments"></a>

<!-- kit:begin id="division-regiments-correction" at="heading:Regiments" -->
**Kit correction** This list is incomplete and wrong in four entries. By the page's own rule, a sub-unit's `group` decides where it goes: `group = support` sub-units go in `support = { }` (column `x = 0`) and every other group goes in `regiments = { }`. Four ids in the list below have `group = support` and so belong in `support`: `super_heavy_armor`, `super_heavy_sp_anti_air_brigade`, `super_heavy_sp_artillery_brigade`, `super_heavy_tank_destroyer_brigade`. Vanilla has 54 sub-units in the regiment groups (`infantry`, `mobile`, `armor`, `combat_support`, `mobile_combat_support`, `armor_combat_support`). Regiment-group ids that the list lacks: `amphibious_light_armor`, `amphibious_medium_armor`, `amphibious_heavy_armor`, `bus`, `hq_infantry`, `hq_motorized`, `hq_armored_car`, `hq_paratrooper`, `hq_light_armor`, `hq_medium_armor`, `hq_heavy_armor`, `marine_commando`, `ranger_battalion`, `fake_intel_unit`, `penal_battalion`, `irregular_infantry`, `militia`. The `hq_*` entries are headquarters sub-units that need Thunder at Our Gates. Vanilla OOB files themselves use only 18 regiment ids: `infantry`, `cavalry`, `motorized`, `bicycle_battalion`, `marine`, `paratrooper`, `mountaineers`, `ranger_battalion`, `irregular_infantry`, `militia`, `light_armor`, `medium_armor`, `heavy_armor`, `armored_car`, `artillery_brigade`, `mot_artillery_brigade`, `anti_tank_brigade` and `light_tank_destroyer_brigade`. [vanilla-confirmed 1.19.3] `common/units/*.txt`, `history/units/*.txt`
<!-- kit:end id="division-regiments-correction" -->

```text
infantry
cavalry
camelry
motorized
light_armor
medium_armor
heavy_armor
super_heavy_armor
modern_armor
marine
paratrooper
amphibious_armor
amphibious_mechanized
anti_tank_brigade
anti_air_brigade
armored_car
artillery_brigade
mot_artillery_brigade
mot_anti_tank_brigade
mot_anti_air_brigade
rocket_artillery_brigade
mot_rocket_artillery_brigade
motorized_rocket_brigade
bicycle_battalion
mountaineers
mechanized
light_sp_anti_air_brigade
medium_sp_anti_air_brigade
heavy_sp_anti_air_brigade
super_heavy_sp_anti_air_brigade
modern_sp_anti_air_brigade
light_sp_artillery_brigade
medium_sp_artillery_brigade
heavy_sp_artillery_brigade
super_heavy_sp_artillery_brigade
modern_sp_artillery_brigade
light_tank_destroyer_brigade
medium_tank_destroyer_brigade
heavy_tank_destroyer_brigade
super_heavy_tank_destroyer_brigade
modern_tank_destroyer_brigade
```

### Support Companies <a id="Support_Companies"></a>

<!-- kit:begin id="division-support-correction" at="heading:Support_Companies" -->
**Kit correction** This list names 14 of the 68 sub-units with `group = support`. The other 54 are listed here, including the four super-heavy ids that the Regiments list wrongly holds. Regimental support sub-units (`field_guns`, `fire_support`, `mot_fire_support`, `rocket_battery`, `anti_air_battery`, `anti_tank_battery`) go in a `regimental_support` block, which 4 vanilla templates use; the placement of the other ids is not documented [unverified]. Vanilla OOB files use only 12 support ids: `anti_air`, `anti_tank`, `armored_car_recon`, `artillery`, `engineer`, `light_tank_recon`, `logistics_company`, `maintenance_company`, `military_police`, `mot_recon`, `recon` and `signal_company`. [vanilla-confirmed 1.19.3] `common/units/*.txt`, `history/units/*.txt`

```text
super_heavy_artillery self_propelled_super_heavy_artillery blackshirt_assault_battalion
pioneer_support jungle_pioneers_support assault_engineer armored_engineer
helicopter_field_hospital fire_support mot_fire_support field_guns rocket_battery
anti_air_battery anti_tank_battery light_flame_tank medium_flame_tank heavy_flame_tank
helicopter_brigade hq_support_company hq_engineer hq_recon hq_military_police hq_maintenance
hq_field_hospital hq_logistics hq_signal hq_naval_liaison hq_air_liaison hq_specops
land_cruiser helicopter_transport armored_maintenance motorized_military_police
airborne_light_armor rangers_support northern_territory_recon_support winter_logistics_support
long_range_patrol_support helicopter_recon elephantry armored_signal
super_heavy_sp_anti_air_brigade light_sp_anti_air_support medium_sp_anti_air_support
heavy_sp_anti_air_support modern_sp_anti_air_support super_heavy_sp_artillery_brigade
sturmtruppe_battalion super_heavy_armor super_heavy_tank_destroyer_brigade
light_tank_destroyer_support medium_tank_destroyer_support heavy_tank_destroyer_support
modern_tank_destroyer_support
```
<!-- kit:end id="division-support-correction" -->

```text
anti_air
anti_tank
armored_car_recon
artillery
engineer
field_hospital
light_tank_recon
logistics_company
maintenance_company
military_police
mot_recon
recon
rocket_artillery
signal_company
```

### Aircraft <a id="Aircraft"></a>

<!-- kit:begin id="division-aircraft-note" at="heading:Aircraft" -->
**Kit correction** The list shows the legacy air equipment ids. With By Blood Alone the ids in vanilla air OOBs are the airframe ids (`small_plane_airframe_0` and so on) with a `version_name`; see the air wings kit block above. Both families exist as equipment in 1.19.3. [vanilla-confirmed 1.19.3] `history/units/*_air_bba.txt`, `common/units/equipment/`
<!-- kit:end id="division-aircraft-note" -->

CV references the carrier variant of the aircraft. All aircraft have a carrier variant unless otherwise specified.

```text
fighter_equipment_0
cv_fighter_equipment_0
fighter_equipment_1
fighter_equipment_2
fighter_equipment_3
jet_fighter_equipment_1
jet_fighter_equipment_2

CAS_equipment_1
cv_CAS_equipment_1
CAS_equipment_2
CAS_equipment_3

nav_bomber_equipment_1
cv_nav_bomber_equipment_1
nav_bomber_equipment_2
nav_bomber_equipment_3

tac_bomber_equipment_0

heavy_fighter_equipment_1
heavy_fighter_equipment_2
heavy_fighter_equipment_3

scout_plane_equipment_1
scout_plane_equipment_2

tac_bomber_equipment_1
tac_bomber_equipment_2
tac_bomber_equipment_3

jet_tac_bomber_equipment_1
jet_tac_bomber_equipment_2

strat_bomber_equipment_1
strat_bomber_equipment_2
strat_bomber_equipment_3

jet_strat_bomber_equipment_1

rocket_suicide_equipment_1
```

### Ship Categories <a id="Ship_Categories"></a>

<!-- kit:begin id="division-ship-lists-note" at="heading:Ship_Categories" -->
**Kit addition** These seven values are exactly the `definition` values vanilla naval OOBs use. The ship equipment lists below are checked: every id in the MTG and Non-MTG lists exists in `common/units/equipment/` in 1.19.3, and the 36 hull and ship equipment ids that vanilla OOBs use are all valid equipment ids. [vanilla-confirmed 1.19.3] `history/units/*.txt`, `common/units/equipment/*.txt`
<!-- kit:end id="division-ship-lists-note" -->

```text
battleship
carrier
destroyer
battle_cruiser
heavy_cruiser
light_cruiser
submarine
```

### MTG Ship Equipment <a id="MTG_Ship_Equipment"></a>

```text
ship_hull_carrier_1
ship_hull_carrier_2
ship_hull_carrier_3

ship_hull_carrier_conversion_bb
ship_hull_carrier_conversion_ca

ship_hull_cruiser_1
ship_hull_cruiser_2
ship_hull_cruiser_3
ship_hull_cruiser_4

ship_hull_pre_dreadnought
ship_hull_heavy_1
ship_hull_heavy_2
ship_hull_heavy_3
ship_hull_heavy_4

ship_hull_super_heavy_1

ship_hull_light_1
ship_hull_light_2
ship_hull_light_3
ship_hull_light_4

ship_hull_submarine_1
ship_hull_submarine_2
ship_hull_submarine_3
ship_hull_submarine_4

ship_hull_cruiser_submarine

torpedo_cruiser
ship_hull_torpedo_cruiser
ship_hull_cruiser_panzerschiff

ship_hull_cruiser_coastal_defense_ship

SH_battleship_1
SH_battleship_2
```

### Non-MTG Ship Equipment <a id="Non-MTG_Ship_Equipment"></a>

```text
carrier_1
carrier_2
carrier_3
carrier_4

light_cruiser_1
light_cruiser_2
light_cruiser_3
light_cruiser_4

heavy_cruiser_1
heavy_cruiser_2
heavy_cruiser_3
heavy_cruiser_4

battleship_1
battleship_2
battleship_3
battleship_4

battle_cruiser_1
battle_cruiser_2

destroyer_1
destroyer_2
destroyer_3
destroyer_4

submarine_1
submarine_2
submarine_3
submarine_4
```

## References <a id="References"></a>

1. ↑ `NDefines.NMilitary.MAX_DIVISION_BRIGADE_WIDTH = 5`, `NDefines.NMilitary.MAX_DIVISION_BRIGADE_HEIGHT = 5`, `NDefines.NMilitary.MAX_DIVISION_SUPPORT_WIDTH = 1`, and `NDefines.NMilitary.MAX_DIVISION_SUPPORT_HEIGHT = 5` in [Defines](<defines.md>)
2. ↑ `NDefines.NMilitary.UNIT_EXP_LEVELS = { 0.1, 0.3, 0.75, 0.9 }` in [Defines](<defines.md>).

<!-- kit:begin id="division-references-note" at="section:References" -->
**Kit addition** Both references still hold in 1.19.3: `MAX_DIVISION_BRIGADE_WIDTH` 5, `MAX_DIVISION_BRIGADE_HEIGHT` 5, `MAX_DIVISION_SUPPORT_WIDTH` 1, `MAX_DIVISION_SUPPORT_HEIGHT` 5 and `UNIT_EXP_LEVELS = { 0.1, 0.3, 0.75, 0.9 }`. [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua`
<!-- kit:end id="division-references-note" -->

---

## Navigation

**[Modding](<modding.md>)**

- **Documentation**: [Effects](<effects.md>) • [Triggers](<triggers.md>) • [Defines](<defines.md>) • [Modifiers](<modifiers.md>) • [List of modifiers](<list-of-modifiers.md>) • [Scopes](<scopes.md>) • [Localisation](<localisation.md>) • [On actions](<on-actions.md>) • [Data structures](<data-structures.md>) • [Flags](<data-structures.md#Flags>) • [Event targets](<data-structures.md#Event_targets>) • [Country tag aliases](<data-structures.md#Country_tag_aliases>) • [Variables](<data-structures.md#Variables>) • [Arrays](<data-structures.md#Arrays>)
- **Scripting**: [Achievements](<achievement-modding.md>) • [AI](<ai-modding.md>) • [AI focuses](<ai-focuses.md>) • [Autonomous states](<autonomy-state-modding.md>) • [Balances of power](<balance-of-power-modding.md>) • [Bookmarks/Scenarios](<bookmark-modding.md>) • [Game rules](<bookmark-modding.md#Game_rules>) • [Buildings](<building-modding.md>) • [Characters and traits](<character-modding.md>) • [Cosmetic tags](<cosmetic-tag-modding.md>) • [Countries](<country-creation.md>) • [Decisions](<decision-modding.md>) • [Doctrines](<doctrine-modding.md>) • [Equipment](<equipment-modding.md>) • [Events](<event-modding.md>) • [Factions](<faction-modding.md>) • [Ideas](<idea-modding.md>) • [Ideologies](<ideology-modding.md>) • [Military industrial organizations](<military-industrial-organization-modding.md>) • [National focuses](<national-focus-modding.md>) • [Resources](<resources-modding.md>) • [Scripted GUI](<scripted-gui-modding.md>) • [Technologies and doctrines](<technology-modding.md>) • [Units](<unit-modding.md>)
- **Map**: [Map](<map-modding.md>) • [States](<state-modding.md>) • [Supply areas](<supply-areas-modding.md>) • [Strategic regions](<strategic-region-modding.md>)
- **Graphical**: [Interface](<interface-modding.md>) • [Graphical assets](<graphical-asset-modding.md>) • [Entities](<entity-modding.md>) • [Posteffects](<posteffect-modding.md>) • [Particles](<particle-modding.md>) • [Fonts](<font-modding.md>)
- **Cosmetic**: [Portraits](<portrait-modding.md>) • [Namelists](<namelist-modding.md>) • [Music](<music-modding.md>) • [Sound](<sound-modding.md>)
- **Other**: [Console commands](<console-commands.md>) • [Troubleshooting](<troubleshooting.md>) • [Mod structure](<mod-structure.md>) • [Mods](<mods.md>) • [Nudger](<nudger.md>)
- **Kit pages (not on the wiki)**: [Collection modding](<collection-modding.md>) • [Game rule modding](<game-rule-modding.md>) • [Intelligence operation modding](<intelligence-operation-modding.md>) • [Map mode modding](<map-mode-modding.md>) • [Occupation and resistance modding](<occupation-and-resistance-modding.md>) • [Peace conference modding](<peace-conference-modding.md>) • [Raid modding](<raid-modding.md>) • [Script constant modding](<script-constant-modding.md>) • [Special project modding](<special-project-modding.md>)
