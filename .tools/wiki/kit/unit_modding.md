# Unit modding

<!-- kit:begin id="review" build="1.19.4.1" checked="2026-11-01" revision="71837" sources="common/units/ common/unit_tags/00_categories.txt common/terrain/00_terrain.txt common/script_enums.txt interface/subuniticons.gfx localisation/english/deployment_l_english.yml localisation/english/unit_l_english.yml documentation/ hoi4.exe" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Checked against all 45 vanilla files in `common/units/` (158 sub-units), `common/unit_tags/00_categories.txt`, the terrain file, `script_enum_equipment_category`, the unit icon and group localisation, and a token search of `hoi4.exe`.
Kit blocks added: `unit-keys` (what every sub-unit sets and the keys the template omits), `unit-terrain-keys`, `unit-internal-types` (33 real values), `unit-group-types` (7 groups), `unit-map-icon-types`, `unit-stat-values` (the page's "vanilla uses" numbers are wrong), `unit-boolean-note`, `unit-navy-air-note` (equipment stats are not sub-unit keys; `fire_range`, `shore_bombardment`, `evasion` and `port_capacity_usage` do not exist), `unit-icons-note`.
Gaps left: the in-game meaning of `priority`, `ai_priority`, `map_icon_category` and `abbreviation` is inferred from usage, and the Models section was not re-checked against `gfx/entities/`.
**1.19.4.1 re-check (2026-11-01).** 17 statements depended on files the update changed (`infantry.txt`, `cavalry.txt`, `amphibious_mech.txt`, the self-propelled and tank destroyer brigade files in `common/units/`, and `deployment_l_english.yml`), and all 17 were re-measured: the 158 sub-units, the 7 groups, the 33 type values and the terrain counts are unchanged. Counts that moved or were corrected: `breakthrough` 63 to 64, `soft_attack` 46 to 49, `hard_attack` 32 to 37, `defense` 36 to 46, all 18 `required_dlc` sub-units need Thunder at Our Gates (not 17), and the `max_organisation` list now includes the values it left out. Every other statement cites files that are byte-identical in 1.19.4.1 (Steam depot manifest diff).
<!-- kit:end id="review" -->

<!-- kit:begin id="unit-keys" at="section:units" -->
### Sub-unit keys in 1.19.4.1

Every one of the 158 vanilla sub-units sets `sprite`, `priority`, `active` and `type`. Those four are the safe minimum; vanilla never omits them. [vanilla-confirmed 1.19.4.1] `common/units/*.txt` (158 of 158)

`type` takes two forms. Land and naval sub-units use a block (`type = { infantry support }`, 133 sub-units); the 25 air sub-units use a single value (`type = fighter`). The first entry is the main type. `need` is a block of equipment ids with amounts (`need = { infantry_equipment = 100 }`) and is set by 156 sub-units; the two that omit it, `battle_cruiser` and `battleship`, use `need_equipment` and `need_equipment_modules` instead (the modules form takes an `any = { module = 1 }` list). [vanilla-confirmed 1.19.4.1] `common/units/battleship.txt`, `common/units/air.txt`

Keys vanilla sub-units use, with the number of sub-units (of 158) that set each. Counts are [vanilla-confirmed 1.19.4.1] `common/units/*.txt`. Meanings are read from usage and from comments in the vanilla files. No documentation file describes the sub-unit format. [vanilla-confirmed 1.19.4.1] `documentation/*.md`, `common/units/`. The meanings are [unverified].

| Key | Count | Notes |
| --- | --- | --- |
| `sprite` | 158 | Entity base name (`infantry`, `light_plane`, `submarine`). |
| `priority` | 158 | Integer. Examples: `infantry` 600, `submarine` 2, `fighter` 1, `engineer` 0. The template says it picks the icon when several sub-units share a type. |
| `active` | 158 | `yes` for 100, `no` for 58. `no` sub-units need a technology or effect to unlock them. |
| `type` | 158 | See above. |
| `need` | 156 | Equipment required per battalion. |
| `essential` | 49 | Equipment ids that must be owned for the unit to be usable (for example `support_equipment`). |
| `categories` | 138 | Unit categories from `common/unit_tags/00_categories.txt`, which defines 49. The 20 sub-units without it are all ships, both railway guns, the missiles and explosive ammo, `suicide_craft`, `cv_suicide_craft`, `rocket_interceptor` and `transport_plane`. |
| `map_icon_category` | 133 | `infantry`, `armored`, `ship` or `other`; air sub-units omit it. |
| `group` | 122 | Division designer group; air, naval and railway gun sub-units omit it. |
| `abbreviation` | 121 | Short quoted code such as `"INF"`. |
| `ai_priority` | 122 | Integer; examples: `engineer` 0, `bicycle_battalion` 150, `infantry` 200. |
| `max_organisation`, `max_strength`, `weight`, `manpower`, `default_morale`, `training_time`, `supply_consumption`, `combat_width` | 131, 124, 124, 122, 122, 120, 118, 113 | The base stat set the template lists. |
| `breakthrough`, `suppression`, `soft_attack`, `hard_attack`, `defense`, `armor_value`, `air_attack`, `ap_attack`, `recon`, `entrenchment`, `maximum_speed` | 64, 56, 49, 37, 46, 14, 11, 8, 12, 6, 9 | Optional combat stats, mostly on support companies. |
| `can_be_parachuted` | 57 | `yes` 39, `no` 18. |
| `affects_speed` | 42 | `no` 40, `yes` 2; support companies set `no`. |
| `regimental` | 55 | Always `no`; set on support companies and brigades. |
| `divisional` | 15 | Always `no`; set on the regimental fire support sub-units. |
| `same_support_type` | 31 | A support company id that cannot be combined with this one in a template (`same_support_type = recon`). |
| `battalion_mult` | 22 | Block with `category`, a stat and `add = yes`: a stat bonus per battalion of a category. |
| `allowed_battalion_groups` | 14 | Group list restricting which line battalions a regimental support unit attaches to. |
| `is_artillery_brigade` | 18 | `yes` 16, `no` 2. |
| `special_forces`, `marines`, `cavalry`, `mountaineers`, `rangers`, `can_exfiltrate_from_coast` | 11, 7, 2, 1, 1, 1 | Boolean role flags, all `yes`. `special_forces` also feeds `category_special_forces`. |
| `transport` | 10 | Equipment id that sets the speed of a motorised sub-unit: `motorized_equipment` (8), `mechanized_equipment` (1), `amphibious_mechanized_equipment` (1). |
| `required_dlc` | 18 | List of DLC names; all 18 need "Thunder at Our Gates" and `hq_armored_car` also lists "La Resistance". |
| `allow_in_army_hq`, `allow_in_non_army_hq`, `deployment_cost`, `division_3d_model_priority`, `deployed_leader_modifiers`, `enable_ability` | 18, 18, 18, 1, 11, 5 | Headquarters support companies. |
| `land_air_wing_size`, `carrier_air_wing_size`, `mega_carrier_air_wing_size`, `submarine_carrier_air_wing_size` | 25, 8, 19, 8 | Air wing sizes (for example 100 planes on land, 10 on a carrier). |
| `critical_parts`, `critical_part_damage_chance_mult`, `hit_profile_mult` | 7, 7, 7 | Ship damage model keys. |
| `own_equipment_fuel_consumption_mult` | 12 | Fuel use multiplier, `0.0` for non-fuel support. |
<!-- kit:end id="unit-keys" -->

<!-- kit:begin id="unit-terrain-keys" at="section:units" -->
Terrain blocks. 73 of the 158 sub-units contain at least one terrain block. The keys vanilla uses are `forest` (67), `jungle` (66), `marsh` (63), `river` (63), `mountain` (60), `amphibious` (56), `hills` (48), `urban` (45), `fort` (21), `plains` (17), `desert` (14) and `snow` (2). Inside a terrain block vanilla uses only three keys: `attack` (420 times), `movement` (308) and `defence` (81, spelled with a `c`). [vanilla-confirmed 1.19.4.1] `common/units/*.txt`

`forest`, `jungle`, `marsh`, `hills`, `mountain`, `plains`, `urban` and `desert` are terrain ids from `common/terrain/00_terrain.txt`. `river`, `amphibious`, `fort` and `snow` are not terrain ids in that file. The wiki's Technology modding page says `amphibious` applies to naval invasions and `river` to river crossings; the meaning of `fort` is not documented, but `localisation/english/unit_l_english.yml` defines the labels `fort`, `river`, `amphibious` and `snow`. [vanilla-confirmed 1.19.4.1] The division designer reads the `fort` block and labels it. In the Engineer Company tooltip of the Infanterie-Division template, a "Fort" line lists Attack +10.0% and Defense +25.0% next to River, Amphibious, Forest, Hills, Jungle and Marsh, which matches `fort = { attack = 0.1 defence = 0.25 }` in vanilla `common/units/engineer.txt`. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, division designer tooltip, screenshot. Only the tooltip was read. Whether the bonus applies in a battle against a fort was not tested. [unverified] The two sub-units that use `snow`, in `recon.txt`, carry the comment "This can end up stacking with terrain benefits". [vanilla-confirmed 1.19.4.1] `common/terrain/00_terrain.txt`, `common/units/recon.txt`

```text
bicycle_battalion = {
    ...
    plains = { movement = 0.2 }
    river = { movement = -0.05 }
    amphibious = { movement = -0.05 }
}
```

The snippet is from `common/units/infantry.txt`. [vanilla-confirmed 1.19.4.1]
<!-- kit:end id="unit-terrain-keys" -->

<!-- kit:begin id="unit-internal-types" at="section:internal-types" -->
The list is correct but incomplete. Vanilla sub-units use 33 type values: the 23 above plus `heavy_fighter`, `scout_plane`, `maritime_patrol_plane`, `ballistic_missile`, `nuclear_missile`, `sam_missile`, `emplacement_gun_ammo`, `railway_gun`, `rocket` and `support_ship`. All 33 are in `script_enum_equipment_category`, which has five more values that no sub-unit uses: `convoy`, `train`, `floating_harbor`, `land_cruiser`, `missile_launcher`. Sub-unit types and equipment types draw from the same enum. A block may list secondary types after the main one: `type = { infantry support }`, `type = { armor anti_tank }`, `type = { support armor anti_air }`. Air sub-units write a single value, not a block. [vanilla-confirmed 1.19.4.1] `common/units/*.txt`, `common/script_enums.txt`. How the engine matches sub-unit types against equipment types is not documented [unverified]
<!-- kit:end id="unit-internal-types" -->

<!-- kit:begin id="unit-group-types" at="section:group-types" -->
`group` has 7 values in vanilla, three more than the list above. Counts are sub-units of 122 that set `group`. [vanilla-confirmed 1.19.4.1] `common/units/*.txt`

| Group | Count | What it holds | Loc key and icon |
| --- | --- | --- | --- |
| `infantry` | 13 | line infantry, bicycle, marines, mountaineers, rangers, paratroopers, militia, headquarters infantry | `group_infantry_title`, `GFX_group_infantry_icon` |
| `mobile` | 9 | cavalry, camelry, motorized, mechanized, armored cars, buses, headquarters | `group_mobile_title`, `GFX_group_mobile_icon` |
| `armor` | 11 | tank battalions | `group_armor_title`, `GFX_group_armor_icon` |
| `combat_support` | 4 | artillery, anti-air, anti-tank and rocket brigades (regimental) | `group_combat_support_title`, `GFX_group_combat_support_icon` |
| `mobile_combat_support` | 5 | the motorised versions of those brigades | `group_mobile_combat_support_title`, `GFX_group_mobile_combat_support_icon` |
| `armor_combat_support` | 12 | self-propelled anti-air, artillery and tank destroyer brigades | `group_armor_combat_support_title`, `GFX_group_armor_combat_support_icon` |
| `support` | 68 | support companies (engineers, recon, hospitals, logistics, headquarters companies) and the battery-level artillery, anti-air and anti-tank sub-units | `group_support_title`; no `GFX_group_support_icon` exists |

The 36 sub-units without `group` are all air, naval and railway gun sub-units. Group titles are in `localisation/english/deployment_l_english.yml` and group icons in `interface/subuniticons.gfx`. The wiki's steps for a new group (a `group_<name>_title` key and a `GFX_group_<name>_icon` sprite) match what vanilla defines for six of the seven groups; `support` has a title but no icon sprite. The `allowed_battalion_groups` key lists group names (`{ infantry mobile combat_support }`). [vanilla-confirmed 1.19.4.1] The division designer files each battalion under the title of its group. As GER in 1936, an empty battalion column offered Infantry Battalions (Infantry, Mountaineers), Mobile Battalions (Armored Car, Cavalry, Motorized Infantry), Armored Battalions (Light, Medium and Heavy Tank), Combat Support Battalions (Anti-Air, Artillery) and Mobile Combat Support Battalions (Motorized Anti-Air, Motorized Artillery), each under its own title. A column that already held infantry offered only Infantry and Mountaineers, and the Support column offered only `support` units. Every unit listed matched its `group` in `common/units`. `armor_combat_support` had no entry because GER has no such unit researched in 1936, and hidden or unresearched units were not listed, so a mismatch could show only for researched units. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, division designer, screenshots.
<!-- kit:end id="unit-group-types" -->

<!-- kit:begin id="unit-map-icon-types" at="section:map-icon-types" -->
The vanilla files document the options in a header comment (`common/units/infantry.txt` and others): land `infantry`, `armored`, `other`; sea `ship`, `transport`, `uboat`. Vanilla sub-units actually use four: `infantry` (75), `armored` (45), `ship` (9, including `submarine`) and `other` (4: `cavalry`, `camelry`, `railway_gun`, `super_heavy_railway_gun`). `transport` and `uboat` appear only in the comment, although `uboat` is also a token in `hoi4.exe`. The 25 air sub-units set no `map_icon_category`. [vanilla-confirmed 1.19.4.1] `common/units/*.txt`. The keyword does not pick the counter picture on its own. On the map as GER in 1936 with the default counter style, an Infanterie-Division showed a helmet, the motorized division a truck, the Panzer division a tank, the Gebirgs-Brigade a mountain and the Kavallerie-Brigade a horse. That is five pictures for three categories, because vanilla gives `infantry` to infantry, motorized and mountaineers, `armored` to the tanks and `other` to cavalry, and the motorized and mountaineer counters do not show the infantry helmet. In these cases the picture follows the division's leading sub-unit type. What `map_icon_category` controls was not identified. The NATO counter option and the zoomed-out map were not checked. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, GER 1936 map counters, screenshots.
<!-- kit:end id="unit-map-icon-types" -->

<!-- kit:begin id="unit-stat-values" at="section:stats" -->
The "vanilla uses" values are outdated. Measured over the 158 sub-units in 1.19.4.1 [vanilla-confirmed 1.19.4.1] `common/units/*.txt`:

| Stat | Wiki says | 1.19.4.1 shows |
| --- | --- | --- |
| `max_organisation` | infantry support 20, armor 10, armor support 0, ship 40, cavalry 70 | `infantry` group 70 (7), 60 (3), 100 (1), 50 (1), 45 (1); `armor` 10 (8 of 11); `mobile` 60 (5), 70 (2), 20 (1), 100 (1); `support` 0 (22), 20 (21), 30 (16), 10 (4), 60 (2), 12 (1), 45 (1), 70 (1); the three brigade groups 0; ships (no group) 40 (5), 50 (2), 35 (1), 30 (1) |
| `combat_width` | infantry 0, artillery 0, armor support 1, armor 2 | `infantry`, `mobile` and `armor` battalions 2 (one infantry sub-unit has 1); `support` 0 for every sub-unit that sets it (59 of 68); `combat_support` and `mobile_combat_support` 1 or 3; `armor_combat_support` 2 |

The template lists eight stats as "almost always" used; counts above show `max_organisation` 131, `max_strength` 124, `weight` 124, `manpower` 122, `default_morale` 122, `training_time` 120, `supply_consumption` 118 and `combat_width` 113 of 158, which fits. [vanilla-confirmed 1.19.4.1]
<!-- kit:end id="unit-stat-values" -->

<!-- kit:begin id="unit-boolean-note" at="heading:boolean" -->
Only `can_be_parachuted` is a sub-unit key (57 vanilla sub-units). `can_license`, `is_convertable` and `carrier_capable` are equipment keys: vanilla sets them on equipment (`can_license` 5 blocks, `is_convertable` 25, `carrier_capable` 11) and on no sub-unit. Other boolean sub-unit keys that vanilla uses are `affects_speed`, `regimental`, `divisional`, `is_artillery_brigade`, `special_forces`, `marines`, `cavalry`, `mountaineers`, `rangers` and `can_exfiltrate_from_coast`. [vanilla-confirmed 1.19.4.1] `common/units/*.txt`, `common/units/equipment/*.txt`
<!-- kit:end id="unit-boolean-note" -->

<!-- kit:begin id="unit-navy-air-note" at="heading:navy-specific" -->
None of the names in this section or in "Air-specific" is a sub-unit key in vanilla: `naval_speed`, `torpedo_attack`, `anti_air_attack`, `surface_detection`, `naval_range`, `air_range`, `air_agility`, `air_bombing`, `air_superiority`, `carrier_size` and the others are equipment stats (all in `script_enum_equipment_stat`), set in `common/units/equipment/` and on modules. No vanilla sub-unit sets any of them, except `air_attack`, which 11 land anti-air sub-units set as a damage stat against planes. Whether the engine would accept them on a sub-unit was not tested. Four names in this list do not exist at all in 1.19.4.1: `fire_range`, `shore_bombardment`, `evasion` and `port_capacity_usage` (see the Equipment modding page for the evidence). Do not write them. Real sub-unit stats for ships are `max_organisation` and `supply_consumption`, plus the damage model keys `critical_parts`, `critical_part_damage_chance_mult` and `hit_profile_mult`. [vanilla-confirmed 1.19.4.1] `common/units/submarine.txt`, `common/units/battleship.txt`, `common/script_enums.txt`; the engine behaviour [unverified]
<!-- kit:end id="unit-navy-air-note" -->

<!-- kit:begin id="unit-icons-note" at="section:icons" -->
In `interface/subuniticons.gfx` vanilla defines three sprite suffixes per sub-unit: `GFX_unit_<name>_icon_medium` (184 sprites, `divisions_large` art, 2 frames), `GFX_unit_<name>_icon_medium_white` (138, `divisions_small/onmap_` art) and `GFX_unit_<name>_icon_medium_black` (12). The `_small` sprite the template shows is not in that file. Group icons use `GFX_group_<group>_icon` (6 of the 7 groups; `support` has none). [vanilla-confirmed 1.19.3] `interface/subuniticons.gfx`
<!-- kit:end id="unit-icons-note" -->
