# Division modding

<!-- kit:begin id="review" build="1.19.4.1" checked="2026-11-01" revision="105628" sources="history/units/ history/countries/ common/units/ common/units/names_divisions/ common/defines/00_defines.lua documentation/effects_documentation.md hoi4.exe" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Checked against all 609 files in `history/units/` (land, `_nsb`, `_air_legacy`, `_air_bba`, `_naval_legacy`, `_naval_mtg` and event OOBs), the `oob`, `set_oob`, `set_naval_oob` and `set_air_oob` lines of the country history files, 1025 division name groups in `common/units/names_divisions/`, the `NMilitary` defines, the unit effects in the documentation, and tokens in `hoi4.exe`.
Kit blocks added: `division-oob-files` (file naming and DLC selection; the wiki's `_legacy` land example is wrong), `division-template-keys`, `division-unit-effects`, `division-placement-keys`, `division-name-groups`, `division-equipment-production`, `division-air-wings`, `division-navy-keys`, `division-regiments-correction`, `division-support-correction`, `division-aircraft-note`, `division-ship-lists-note`, `division-references-note`.
Gaps left: the effect of the root-level `start_equipment_factor` and of template `role` and `obsolete` is inferred from usage, and the ship `ordered_name` lookup was not traced to a name file.
**1.19.4.1 re-check (2026-11-01).** 17 statements depended on files the update changed (five files in `history/units/`, 35 country history files and the sub-unit files in `common/units/`), and all 17 were re-measured. Nothing moved: the 609 OOB files, 804 templates, 5074 divisions, 270 fleets, 692 task forces, 6682 ships, 507 air wing entries, 923 production lines, the sub-unit groups and the `oob` lines in country history are the same as before. Every other statement cites files that are byte-identical in 1.19.4.1 (Steam depot manifest diff).
<!-- kit:end id="review" -->

<!-- kit:begin id="division-oob-files" at="section:land-units" -->
### How vanilla names and selects order of battle files

The land example above is out of date: vanilla has no `TAG_1936_legacy` land file. The land file without a suffix is the base-game version (`set_oob = "AFG_1936"` when the country does not have No Step Back) and `TAG_1936_nsb` is the No Step Back version (`set_oob = "AFG_1936_nsb"`), each under its own `if` with `has_dlc = "No Step Back"` or `NOT = { has_dlc = ... }`. The suffix `_legacy` appears only on air and naval files. [vanilla-confirmed 1.19.4.1] `history/countries/AFG - Afghanistan.txt`, `history/units/`

File names in `history/units/` (609 files). The file name is free; the string in the effect must match it. Suffix counts are files. [vanilla-confirmed 1.19.4.1] `history/units/`

| Suffix | Files | Holds | Selected by |
| --- | --- | --- | --- |
| `<TAG>_<year>.txt` | 177 | land templates, divisions, starting production | `oob = "..."` or `set_oob` |
| `_nsb` | 24 | land version for No Step Back | `has_dlc = "No Step Back"` |
| `_air_bba` / `_air_legacy` | 89 / 89 | air wings | `has_dlc = "By Blood Alone"` or not |
| `_naval_mtg` / `_naval_legacy` | 57 / 62 | fleets | `has_dlc = "Man the Guns"` or not |
| `_naval`, `_Naval`, `_Naval_Legacy` | 7, 2, 2 | fleets in countries without the MTG split | plain `set_naval_oob` |
| `_sea` | 15 | a main OOB with division templates (`CHI_1936_sea.txt`); used by `oob` (8) and `set_oob` (7) | plain `oob` or `set_oob` |
| other suffixes (`_ncns`, `_lar`, `_LaR`, `_mun`, `_GOE`, `_BBA`, `_nsb_LaR`, ...) | 11 | DLC variants chosen with `set_oob` | their own `has_dlc` gates; `_mun` files only a No Step Back check [vanilla-confirmed 1.19.4.1] `history/countries/` |
| event and decision files | the rest | `load_oob` targets such as `unlock_tanks`, `cossack_host`, `Civil_War` | `load_oob = "..."` |

In country history files vanilla uses these lines: top-level `oob = "TAG_1936"` (192 uses across 110 files), `set_oob` (56 plain, 25 with `_nsb`), `set_naval_oob` (62 `_naval_legacy`, 57 `_naval_mtg`, 7 `_naval`) and `set_air_oob` (95 `_air_legacy`, 95 `_air_bba`). The air and naval pair is chosen like this: [vanilla-confirmed 1.19.4.1] `history/countries/ARG - Argentina.txt`

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

What the effects do. `set_oob`, `set_naval_oob` and `set_air_oob` register an order of battle to load at game start; each replaces an earlier registration with the same key (no key, `naval`, `air`), so a mod can swap only the air file. `set_keyed_oob = { key = naval name = "ENG_1936_Naval" }` does the same for any key. They are meant for history files. `load_oob` loads a file immediately and is used in decisions, events and focuses (32 vanilla files). [docs] `documentation/effects_documentation.md`; [vanilla-confirmed 1.19.4.1] `common/decisions/GER.txt`

Root keys that vanilla OOB files use: `division_template` (804 blocks), `units` (408 files), `instant_effect` (329), `air_wings` (188), `start_equipment_factor` (22), `create_colonial_division_template` (5). [vanilla-confirmed 1.19.4.1] `history/units/*.txt`
<!-- kit:end id="division-oob-files" -->

<!-- kit:begin id="division-template-keys" at="section:division-template" -->
### Division template keys and limits

Grid sizes. The page's reference [1] still holds, and there is a third grid: `MAX_REGIMENTAL_SUPPORT_WIDTH` is 5 and `MAX_REGIMENTAL_SUPPORT_HEIGHT` is 1 (a row), with `REGIMENTAL_SUPPORT_REQUIRED_BATTALIONS = { 3 }` (a regimental support needs 3 battalions in its row). Headquarters templates have `MAX_HQ_REGIMENTAL_SUPPORT_WIDTH` and `_HEIGHT` of 0. In vanilla templates, `regiments` coordinates reach x 4 and y 4, `support` always uses `x = 0` with y up to 4, and `regimental_support` (4 templates, all CZE) uses `x = 1 y = 0`. [vanilla-confirmed 1.19.4.1] `common/defines/00_defines.lua`, `history/units/CZE_1936.txt`

Usage of the documented keys across the 804 vanilla templates, and keys the page omits. [vanilla-confirmed 1.19.4.1] `history/units/*.txt`

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

No game documentation file describes `role` or `obsolete` in a division template. [vanilla-confirmed 1.19.4.1] `documentation/*.md`. The meaning of `role` is read from usage, so it stays [unverified]. `obsolete = yes` hides the template from the list used to recruit and deploy: as ITA, `has_template = "Divisione Ascari Libica"` was true, yet the Recruit and Deploy template list showed 8 templates without the three `obsolete = yes` Ascari templates, with an unticked "Show decommissioned templates" box above it. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, template list and screenshot. The ticked view was not captured.
<!-- kit:end id="division-template-keys" -->

<!-- kit:begin id="division-unit-effects" at="section:division-template" -->
Effects that create or change divisions and templates after the game has started, all in country scope unless noted. [docs] `documentation/effects_documentation.md`

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

<!-- kit:begin id="division-placement-keys" at="section:division-placement" -->
### Division placement keys in vanilla

Counts over the 5074 divisions in vanilla `units = { }` blocks. [vanilla-confirmed 1.19.4.1] `history/units/*.txt`

| Key | Divisions | Notes |
| --- | --- | --- |
| `location`, `division_template` | 5074 | Always present. |
| `division_name` | 3773 | Always `is_name_ordered = yes`; `name_order` in 3694 of them. |
| `name` | 1245 | Direct name. |
| `start_experience_factor` | 4500 | |
| `start_equipment_factor` | 3744 | |
| `force_equipment_variants` | 753 | 754 entries: `owner` (754), `version_name` (90), `creator` (38), `amount` (20). |
| `officer` | 115 | Only `name` (115) and `portraits` (2) seen. |
| `bonus` | 3 | Integer in the Azad Hind file `CA1.txt` (all 3 uses; no vanilla script loads `CA1`). [vanilla-confirmed 1.19.4.1] `common/`, `events/`, `history/`. No documentation describes it, and its meaning is [unverified]. |
| `start_manpower_factor` | 0 | No `history/units` division uses it, but 38 files in `common/` and `events/` write it in `create_unit` division strings (213 lines, for example `common/decisions/AFG.txt`). [vanilla-confirmed 1.19.4.1] An OOB division accepts it: `start_manpower_factor = 0.5` in a `history/units` division block was accepted with no error.log line and halved the starting manpower. The deployed army manpower of the test country rose by 0.5 thousand for that division, against 1 thousand for a plain division of the same template. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, deployed manpower read in game.log. |

The page's reference [2] holds: `UNIT_EXP_LEVELS = { 0.1, 0.3, 0.75, 0.9 }` in `NDefines.NMilitary`. [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua`
<!-- kit:end id="division-placement-keys" -->

<!-- kit:begin id="division-name-groups" at="section:division-placement" -->
Name groups, the files `division_names_group` refers to, live in `common/units/names_divisions/` (100 files, 1025 groups in vanilla). A group holds `name`, `for_countries`, `can_use` (trigger), `division_types` (sub-unit ids such as `"infantry"` or `"light_armor"`), `fallback_name` (a string with `%d`), `ordered` (a table of numbered names) and, in 385 groups, `link_numbering_with` (another group id whose numbering it continues). `division_types` values seen: `infantry` (281 groups), `cavalry`, `motorized`, `mechanized`, the armor classes, `marine`, `mountaineers`, `paratrooper`, `ranger_battalion`, `militia` and a few others. [vanilla-confirmed 1.19.3] `common/units/names_divisions/*.txt`; the meaning of `link_numbering_with` is inferred from its name [unverified]
<!-- kit:end id="division-name-groups" -->

<!-- kit:begin id="division-equipment-production" at="section:equipment-production" -->
Vanilla `instant_effect` blocks hold `add_equipment_production` 923 times (plus a few `if` wrappers). The effect takes more keys than the page lists: `name` (172 uses; a string shown for the line), `amount` (399; number of items to build, a value or variable) and `industrial_manufacturer` (614; a military industrial organization written as `mio:<token>`). `requested_factories` and `progress` are set in all 923, `efficiency` in 524; vanilla efficiency values are percentages (100 in 420 uses, 50 in 108), while the documentation example shows `0.1`. [docs] `documentation/effects_documentation.md`; [vanilla-confirmed 1.19.4.1] `history/units/*.txt`
<!-- kit:end id="division-equipment-production" -->

<!-- kit:begin id="division-air-wings" at="section:adding-air-wings" -->
### Air wing keys in vanilla

The key of each entry in `air_wings` is a state id (453 of 507 entries) or, for carrier-based wings, a quoted ship name (`"HMS Furious" = { ... }`, 54 entries). Carrier wings can also sit in an `air_wings = { }` block inside the `ship` itself (10 ships in the naval files). Each equipment entry holds `owner` and `amount` (1274 of 1274), plus `version_name` (661), `creator` (187) and `create_if_missing` (5). A wing can carry a `name = "..."` string (43) and an optional `ace` block with `modifier`, `name`, `surname`, `callsign`, `is_female` and `portrait` (21 in vanilla); the vanilla comment says the order is important and the ace joins the equipment entry above it. [vanilla-confirmed 1.19.4.1] `history/units/*_air_*.txt`, `history/units/ENG_1936_air_bba.txt`, `history/units/GER_1936_air_bba.txt`

The equipment ids differ by file family: `_air_legacy` files use ids like `fighter_equipment_0` and `CAS_equipment_1` (the page's list), `_air_bba` files use airframe ids such as `small_plane_airframe_0` (138 uses), `medium_plane_airframe_1` (84) and `small_plane_cas_airframe_0` (47), usually with a `version_name`. Both id families exist in `common/units/equipment/` in 1.19.4.1. [vanilla-confirmed 1.19.4.1] `history/units/*.txt`, `common/units/equipment/`

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

<!-- kit:begin id="division-navy-keys" at="section:adding-navies" -->
### Fleet, task force and ship keys in vanilla

Counts over the 270 fleets, 692 task forces and 6682 ships in vanilla naval OOBs. [vanilla-confirmed 1.19.4.1] `history/units/*.txt`

| Level | Keys (count) |
| --- | --- |
| `fleet` | `name` (270), `naval_base` (270, a province id), `task_force` (692) |
| `task_force` | `name`, `location` (692 each), `ship` (6682), `base` (3, a province id; equal to `location` in `AST_1939_naval.txt`) |
| `ship` | `definition` (6682), `equipment` (6682), `name` (6427) or `ordered_name` (255), `pride_of_the_fleet` (64), `start_experience_factor` (769), `officer` (16), `air_wings` (10) |
| ship `equipment` entry | `amount` (6682), `owner` (6682), `version_name` (4289), `creator` (100), `create_if_missing` (3) |

`definition` takes the sub-unit id of the ship category, and vanilla uses exactly seven: `destroyer` (3124), `submarine` (2209), `light_cruiser` (590), `heavy_cruiser` (430), `battleship` (230), `carrier` (69) and `battle_cruiser` (30); all are ids in `common/units/`. `ordered_name = 5` replaces `name` (255 ships); how the number resolves to a ship name was not traced. Every vanilla ship equipment entry sets `owner`, so omitting it (the page's Note 2) is untested in vanilla. [vanilla-confirmed 1.19.4.1] `history/units/*.txt`, `common/units/`; the `ordered_name` meaning [unverified]
<!-- kit:end id="division-navy-keys" -->

<!-- kit:begin id="division-regiments-correction" at="heading:regiments" -->
This list is incomplete and wrong in four entries. By the page's own rule, a sub-unit's `group` decides where it goes: `group = support` sub-units go in `support = { }` (column `x = 0`) and every other group goes in `regiments = { }`. Four ids in the list below have `group = support` and so belong in `support`: `super_heavy_armor`, `super_heavy_sp_anti_air_brigade`, `super_heavy_sp_artillery_brigade`, `super_heavy_tank_destroyer_brigade`. Vanilla has 54 sub-units in the regiment groups (`infantry`, `mobile`, `armor`, `combat_support`, `mobile_combat_support`, `armor_combat_support`). Regiment-group ids that the list lacks: `amphibious_light_armor`, `amphibious_medium_armor`, `amphibious_heavy_armor`, `bus`, `hq_infantry`, `hq_motorized`, `hq_armored_car`, `hq_paratrooper`, `hq_light_armor`, `hq_medium_armor`, `hq_heavy_armor`, `marine_commando`, `ranger_battalion`, `fake_intel_unit`, `penal_battalion`, `irregular_infantry`, `militia`. The `hq_*` entries are headquarters sub-units that need Thunder at Our Gates. Vanilla OOB files themselves use only 18 regiment ids: `infantry`, `cavalry`, `motorized`, `bicycle_battalion`, `marine`, `paratrooper`, `mountaineers`, `ranger_battalion`, `irregular_infantry`, `militia`, `light_armor`, `medium_armor`, `heavy_armor`, `armored_car`, `artillery_brigade`, `mot_artillery_brigade`, `anti_tank_brigade` and `light_tank_destroyer_brigade`. [vanilla-confirmed 1.19.4.1] `common/units/*.txt`, `history/units/*.txt`
<!-- kit:end id="division-regiments-correction" -->

<!-- kit:begin id="division-support-correction" at="heading:support-companies" -->
This list names 14 of the 68 sub-units with `group = support`. The other 54 are listed here, including the four super-heavy ids that the Regiments list wrongly holds. Regimental support sub-units (`field_guns`, `fire_support`, `mot_fire_support`, `rocket_battery`, `anti_air_battery`, `anti_tank_battery`) go in a `regimental_support` block, which 4 vanilla templates use (in `history/units`, all with only `field_guns`); the documentation's `add_units_to_division_template` example also puts `military_police` there [docs] `documentation/effects_documentation.md`. Whether the game accepts the other support ids in that block is [unverified]. Vanilla OOB files use only 12 support ids: `anti_air`, `anti_tank`, `armored_car_recon`, `artillery`, `engineer`, `light_tank_recon`, `logistics_company`, `maintenance_company`, `military_police`, `mot_recon`, `recon` and `signal_company`. [vanilla-confirmed 1.19.4.1] `common/units/*.txt`, `history/units/*.txt`

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

<!-- kit:begin id="division-aircraft-note" at="heading:aircraft" -->
The list shows the legacy air equipment ids. With By Blood Alone the ids in vanilla air OOBs are the airframe ids (`small_plane_airframe_0` and so on) with a `version_name`; see the air wings notes above. Both families exist as equipment in 1.19.4.1. [vanilla-confirmed 1.19.4.1] `history/units/*_air_bba.txt`, `common/units/equipment/`
<!-- kit:end id="division-aircraft-note" -->

<!-- kit:begin id="division-ship-lists-note" at="heading:ship-categories" -->
These seven values are exactly the `definition` values vanilla naval OOBs use. The ship equipment lists below are checked: every id in the MTG and Non-MTG lists exists in `common/units/equipment/` in 1.19.4.1, and the 36 hull and ship equipment ids that vanilla OOBs use are all valid equipment ids. [vanilla-confirmed 1.19.4.1] `history/units/*.txt`, `common/units/equipment/*.txt`
<!-- kit:end id="division-ship-lists-note" -->

<!-- kit:begin id="division-references-note" at="section:references" -->
Both references still hold in 1.19.3: `MAX_DIVISION_BRIGADE_WIDTH` 5, `MAX_DIVISION_BRIGADE_HEIGHT` 5, `MAX_DIVISION_SUPPORT_WIDTH` 1, `MAX_DIVISION_SUPPORT_HEIGHT` 5 and `UNIT_EXP_LEVELS = { 0.1, 0.3, 0.75, 0.9 }`. [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua`
<!-- kit:end id="division-references-note" -->
