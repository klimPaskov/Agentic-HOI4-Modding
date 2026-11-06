# Equipment modding

<!-- kit:begin id="review" build="1.19.4.1" checked="2026-11-01" revision="104717" sources="common/units/equipment/ common/units/equipment/modules/ common/equipment_groups/ common/script_enums.txt interface/equipmentdesigner/ gfx/interface/equipmentdesigner/graphic_db/ localisation/english/equipment_l_english.yml hoi4.exe" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Checked against `common/units/equipment/_documentation.md`, `common/equipment_groups/_documentation.md`, the two equipment designer `_documentation.info` files, all 45 vanilla equipment files (308 equipment blocks and 34 duplicated archetypes), the module files, `script_enum_equipment_category` and `script_enum_equipment_stat`, and a token search of `hoi4.exe`.
Kit blocks added: `equipment-keys` (keys the templates omit, `manpower` and `is_frame` corrections), `equipment-types` (real type values), `equipment-group-by`, `equipment-interface-categories`, `equipment-designer-notes` (`duplicate_archetypes`, window lookup, graphic_db, modules), `equipment-stats-enum`, `equipment-naval-stats-warning` (four dead stat names), `equipment-air-stats`, `equipment-localization`.
Gaps left: the in-game effect of `group_by`, `visual_level`, `priority` and `abbreviation` is not documented and is marked [unverified]; module files are summarised, not documented key by key.
**1.19.4.1 re-check (2026-11-01).** 13 statements depended on files the update changed (`tank_chassis.txt`, `sam_missile.txt` and `00_tank_modules.txt` in `common/units/equipment/`, plus the sub-unit files in `common/units/`), and all 13 were re-measured: the 308 equipment blocks, 34 duplicated archetypes, 316 modules and every per-key count are unchanged except two. `multiply_stats` is written in 207 modules (205 before), and the list of secondary types was missing `carrier`, which the submarine carrier hull uses. Every other statement cites files that are byte-identical in 1.19.4.1 (Steam depot manifest diff).
<!-- kit:end id="review" -->

<!-- kit:begin id="equipment-keys" at="section:equipment" -->
### Equipment keys in 1.19.4.1

Two statements in the templates above are out of date, and both templates leave out keys that vanilla uses.

- `manpower` is not naval only. The documentation says so, but vanilla also sets it on plane airframes (`plane_airframes.txt`, `x_plane_airframes.txt`, `quad_engine_airframe.txt`), tank chassis (`tank_chassis.txt`) and railway guns. It is on 125 of the 308 equipment blocks. [vanilla-confirmed 1.19.4.1] `common/units/equipment/*.txt`
- `is_frame` and `max_dockyard_factories` are real keys: both are in the documentation and both strings are in `hoi4.exe`. No vanilla file sets either. `max_military_factories` is set in 3 blocks (value 5; `artillery.txt` twice, `tank_chassis.txt` once). [docs] `common/units/equipment/_documentation.md`, [vanilla-confirmed 1.19.4.1] for the usage counts
- The documentation's `type` list includes `naval_transport`, but no vanilla equipment uses it and it is not in `script_enum_equipment_category`. [vanilla-confirmed 1.19.4.1] `common/script_enums.txt`

Keys vanilla uses that the templates do not show. Counts are blocks in `common/units/equipment/*.txt` out of 308 (archetypes and regular equipment). Source of every row: [vanilla-confirmed 1.19.4.1] unless the row says [docs].

| Key | Count | What vanilla shows |
| --- | --- | --- |
| `default_modules` | 87 | `<slot> = <module>` or `<slot> = empty`; the modules of the default variant. [docs] `common/units/equipment/_documentation.md` |
| `ai_type` | 1 (plus 4 duplicated archetypes) | Overrides `type` for AI unit ratios. Documented values `cv_fighter`, `cv_interceptor`, `cv_cas`, `cv_naval_bomber`, `cv_suicide`, `heavy_fighter`. [docs] |
| `abbreviation` | 83 | Short string such as `"lt1"` or `"afs0"`. Use is not documented. [unverified] |
| `derived_variant_name` | 35 | Localisation key such as `light_tank_equipment_0`. A string in `hoi4.exe` says it names derived designs. [unverified] |
| `can_convert_from` | 37 | List of equipment ids; hull and chassis upgrades use it (carrier hulls list cruiser and heavy hulls). |
| `allow_mission_type`, `forbid_mission_type` | 29, 3 | Lists of air mission names (`barrage_mission`, `training`). |
| `picture` | 41 | Archetype picture name such as `archetype_light_tank_equipment`. For 37 of the 41 values a sprite `GFX_<picture>_medium` exists in `interface/` (for example `GFX_archetype_light_tank_equipment_medium`). The three values without one are in the note below the table. That the game builds the sprite name this way is [unverified]. |
| `sprite`, `model` | 28, 22 | `sprite` names a map sprite (`missile_default`, `convoy`); `model` names a ship model (`repair_ship`, `ship_hull_super_carrier`). |
| `visual_level` | 144 | Integer 0 to 3 on regular equipment. The wiki calls it the image priority in the production screen. [unverified] |
| `visual_tech_level_addition` | 2 | Integer on carrier and heavy hulls. |
| `weight` | 21 | Plane stat, for example `weight = 3`. |
| `interface_overview_category_index` | 7 (plus 10 duplicated) | Index of the airforce overview row; `-1` hides the plane from the intel and airforce overview (comment in `x_plane_airframes.txt`). |
| `air_map_icon_frame` | 12 (plus 13 duplicated) | Frame number of the air map icon. |
| `one_use_only` | 10 | `yes` on missiles; `no` on `emplacement_gun_ammo`. |
| `type_override`, `allowed_types` | 4, 6 | Airframes set `type_override = fixed_main_weapon_slot` and list the types a plane may take, for example `allowed_types = { fighter interceptor }`. |
| `modifier_stat` | 4 | Support ships: `modifier = naval_repair_support`, `value = 100`, `type = naval_support`. |
| `offensive_weapons` | 5 | `no` on convoys and carriers; the vanilla comment calls it a hidden combat behaviour stat. |
| `alias`, `substitute`, `family`, `supply_truck`, `upgrade_window_override` | 2, 1, 9, 2, 1 | Single-purpose keys: hull aliases (`alias = destroyer`), a plane that replaces another on carriers, a tank family label, a truck flag on motorised equipment, an upgrade window override on one cruiser hull. |
| `naval_dominance_factor`, `naval_weather_penalty_factor` | 50, 7 | Ship hull stats, for example `naval_dominance_factor = 20` on `ship_hull_light`. |
| `fuel_consumption` | 156 | Land and air stat, for example `fuel_consumption = 2.4` on `mechanized.txt`. |

Notes on rows of the table above:

- `picture`: The three values without one are `archetype_specialist_armored_vehicles`, `archetype_amphibious_tank_equipment` and `archetype_rocket_interceptor_equipment`.
<!-- kit:end id="equipment-keys" -->

<!-- kit:begin id="equipment-types" at="section:air" -->
#### Equipment type values in 1.19.4.1

The three lists above are partly obsolete. `heavy_tank_chassis`, `light_tank_chassis` and `medium_tank_chassis` are archetype ids, not types (tank chassis have `type = armor`), `support_equipment` is the equipment id and the type is `support`, `strat_bomber` is `strategic_bomber`, and `naval_transport` does not exist. The valid values are the 38 entries of `script_enum_equipment_category`; every `type` that vanilla equipment uses is in it. [vanilla-confirmed 1.19.4.1] `common/script_enums.txt`, `common/units/equipment/*.txt`

| Group | Values |
| --- | --- |
| Land | `infantry`, `support`, `artillery`, `anti_tank`, `anti_air`, `armor`, `motorized`, `mechanized`, `rocket`, `amphibious`, `flame`, `land_cruiser`, `railway_gun`, `train` |
| Naval | `capital_ship`, `carrier`, `screen_ship`, `submarine`, `convoy`, `support_ship`, `floating_harbor`, `missile_launcher` |
| Air | `fighter`, `heavy_fighter`, `interceptor`, `cas`, `naval_bomber`, `tactical_bomber`, `strategic_bomber`, `scout_plane`, `maritime_patrol_plane`, `air_transport`, `suicide`, `missile`, `ballistic_missile`, `nuclear_missile`, `sam_missile`, `emplacement_gun_ammo` |

`land_cruiser` and `missile_launcher` are in the enum but no vanilla equipment block uses them as `type`. The grouping in the table is editorial, not the game's. [vanilla-confirmed 1.19.4.1]

`type` may be a list: the first value is the main type and the rest are secondary types, for example `type = { screen_ship anti_air }` on `light_cruiser_1` and `type = { armor anti_air }` for the anti-air tank chassis. Every secondary value that vanilla uses (`anti_air`, `anti_tank`, `artillery`, `amphibious`, `flame`, `rocket`, `support`, `infantry`, `motorized`, and `carrier` on the submarine carrier hull) is also a sub-unit `type` in `common/units/*.txt`. The wiki adds that a new type needs at least one sub-unit using it. [vanilla-confirmed 1.19.4.1] `common/units/equipment/ship_hull_cruiser.txt`, `common/units/equipment/x_tank_chassis.txt`; the wiki's rule [unverified]

These values are also the keys that `equipment_bonus` and military industrial organizations accept, together with equipment ids and groups (`script_enum_equipment_bonus_type`). [vanilla-confirmed 1.19.3] `common/script_enums.txt`
<!-- kit:end id="equipment-types" -->

<!-- kit:begin id="equipment-group-by" at="section:group-by-types" -->
`group_by` has two values, `archetype` and `type`. Vanilla sets it only on archetypes: 37 blocks use `archetype` (every tank chassis, `small_plane_airframe`, `convoy`, `ship_hull_carrier`, `ship_hull_submarine`, the land equipment archetypes) and 5 use `type` (`ballistic_missile_equipment`, `explosive_ammo_equipment`, `guided_missile_equipment`, `nuclear_missile_equipment`, `sam_missile_equipment`). The other ship hull archetypes set no `group_by`. The token is in `hoi4.exe`; the documentation does not describe it, and the wiki's explanation (how the equipment is grouped in the production screen) is the only description. [vanilla-confirmed 1.19.4.1] `common/units/equipment/*.txt`; the effect [unverified]
<!-- kit:end id="equipment-group-by" -->

<!-- kit:begin id="equipment-interface-categories" at="section:interface-categories" -->
The six values above are the only ones vanilla equipment uses: `interface_category_land` 17 blocks, `interface_category_air` 12, `interface_category_armor` 9, `interface_category_other_ships` 7, `interface_category_screen_ships` 4 and `interface_category_capital_ships` 2. `hoi4.exe` also holds `interface_category_resources`, `_stockpiling`, `_reinforcing`, `_upgrading` and `_outdated`; these are not used by any vanilla equipment and their purpose is unknown. [vanilla-confirmed 1.19.4.1] `common/units/equipment/*.txt`; the extra tokens [unverified]
<!-- kit:end id="equipment-interface-categories" -->

<!-- kit:begin id="equipment-designer-notes" at="section:equipment-designer" -->
#### Designer windows, variants and modules

Where the designer windows and variants really live in 1.19.3.

**Variants are duplicated archetypes.** The wiki's `<equipment_archetype>_my_variant = { archetype = ... type = { ... } for_each = { ... } }` sits inside a root block `duplicate_archetypes = { }`, in a file that is evaluated after the files that define the archetypes. Vanilla keeps them in `x_tank_chassis.txt` (21 duplicates) and `x_plane_airframes.txt` (13). The attributes `alias`, `type`, `variant_name` and `derived_variant_name` are not copied from the archetype, so each duplicate sets its own `type`. `for_each` sets stats on every generated equipment; planes may instead map names with `variant_name = { <equipment> = <loc key> }`. Plane duplicates also use `only_duplicate_archetype`, `substitute`, `ai_type` and `forbid_mission_type`. [vanilla-confirmed 1.19.3] `common/units/equipment/x_tank_chassis.txt`, `common/units/equipment/x_plane_airframes.txt`

```text
duplicate_archetypes = {
    light_tank_aa_chassis = {
        archetype = light_tank_chassis
        type = { armor anti_air }
        for_each = {
            variant_name = { find_and_replace = { "chassis" "equipment" } }
            hardness = { set = 0.5 }
        }
    }
}
```

The wiki says new variants must be listed in "script_enums"; the file is `common/script_enums.txt` and the two relevant enums are `script_enum_equipment_category` (valid `type` values) and `script_enum_equipment_bonus_type` (names that `equipment_bonus` and military industrial organizations accept, including equipment ids such as `light_tank_chassis_1`). The second enum's comment says it should be updated whenever equipment is added and that the game logs an error at startup when it is stale. [vanilla-confirmed 1.19.3] `common/script_enums.txt`

**Window lookup.** The designer finds the top-level container by trying `equipment_designer_<TYPE>_<TAG>`, `equipment_designer_<ARCHETYPE>_<TAG>`, `equipment_designer_<TYPE>` and `equipment_designer_<ARCHETYPE>`, in that order. Inside it, `module_slots` holds one container per slot, named like the slot; inside that, one container per module. A module's container is found by trying the module name, the module GFX name, the module category name and the slot name, in that order. A `@highlight` suffix names the highlight element (`ship_heavy_battery@highlight`), and a bare `@highlight` is the fallback. [docs] `interface/equipmentdesigner/_documentation.info`

**Files.** Vanilla splits designer windows into `interface/equipmentdesigner/planes/`, `ships/` and `tanks/`; the file name does not matter. [vanilla-confirmed 1.19.3] `interface/equipmentdesigner/`

**Icons and models per equipment (graphic_db).** `gfx/interface/equipmentdesigner/graphic_db/*.txt` (vanilla: `00_tank_icons.txt`, `00_plane_icons.txt`, `00_hq_icons.txt`) maps an equipment type or archetype to icons and 3D models. Root keys are `default`, a continent name or a country tag; under them each key is an equipment type or archetype holding `pool` blocks. A `pool` may hold `limit` (trigger), `weight` (sort order, default 1), `icons` (GFX names), `models` (entity names) and three filters: `sub_units`, `ideologies` and `cultures` (graphical culture keys from `common/graphicalculturetype.txt`); an empty filter is unrestricted, and every filter that is set must match. Country beats continent beats `default`, type beats archetype, and later definitions beat earlier ones when weights tie. [docs] `gfx/interface/equipmentdesigner/graphic_db/_documentation.info`

**Module files.** Modules are defined in `common/units/equipment/modules/` (vanilla: `00_tank_modules.txt`, `00_ship_modules.txt`, `00_plane_modules.txt`), inside `equipment_modules = { }`: 316 modules. Keys they use: `category` and `abbreviation` (312 each), `add_stats` (311), `sfx` (280), `multiply_stats` (207), `can_convert_from` (168), `xp_cost` (153), `dismantle_cost_ic` (129), `parent` (114), `build_cost_resources` (66), `critical_parts` (54), `add_equipment_type` (47), `gfx` (42), `mission_type_stats` (33), `allow_mission_type` (30), `gui_category` (28), `add_average_stats` (28), `allow_equipment_type` (23), `allowed_module_categories` (11), `forbid_module_categories` (10), `forbid_equipment_type` and `forbid_equipment_type_exact_match` (4 and 6). Technologies unlock modules with `enable_equipment_modules`. [vanilla-confirmed 1.19.4.1] `common/units/equipment/modules/*.txt`
<!-- kit:end id="equipment-designer-notes" -->

<!-- kit:begin id="equipment-stats-enum" at="section:stats" -->
### Valid equipment stat names

The stat names that equipment, `equipment_bonus` and military industrial organizations accept are the 78 entries of `script_enum_equipment_stat`. [vanilla-confirmed 1.19.3] `common/script_enums.txt`

```text
default_morale defense breakthrough hardness soft_attack hard_attack recon entrenchment
initiative casualty_trickleback supply_consumption_factor supply_consumption suppression
suppression_factor experience_loss_factor equipment_capture_factor recovery
additional_collateral_damage fuel_capacity surface_detection sub_detection surface_visibility
sub_visibility lg_attack lg_armor_piercing hg_attack hg_armor_piercing torpedo_attack sub_attack
anti_air_attack amphibious_defense naval_speed naval_range mines_planting mines_sweeping
naval_light_gun_hit_chance_factor naval_heavy_gun_hit_chance_factor naval_torpedo_hit_chance_factor
naval_torpedo_damage_reduction_factor naval_torpedo_enemy_critical_chance_factor
convoy_raiding_coordination patrol_coordination search_and_destroy_coordination air_range
air_defence air_attack air_agility air_bombing air_superiority naval_strike_attack
naval_strike_targetting air_ground_attack air_visibility_factor railway_gun_attack
railway_gun_attack_range_index_in_define railway_gun_annex_ratio
railway_gun_hours_between_redistribution max_organisation max_strength maximum_speed
armor_value ap_attack reliability reliability_factor weight thrust fuel_consumption
fuel_consumption_factor strategic_attack carrier_size submarine_carrier_size
carrier_surface_detection carrier_sub_detection acclimatization_hot_climate_gain_factor
acclimatization_cold_climate_gain_factor night_penalty build_cost_ic naval_weather_penalty_factor
```

The enum's own comment says stats owned by the battalion rather than the equipment do not work with military industrial organizations: `default_morale`, `recon`, `initiative`, `casualty_trickleback`, the supply consumption and suppression stats, `experience_loss_factor`, `equipment_capture_factor`, `railway_gun_attack`, `max_organisation`, `max_strength` and the two acclimatization factors. `entrenchment` only works for tanks with dozer blades, not infantry. No vanilla equipment block sets `entrenchment` or `recon`, although the Stats and Modifiers sections below list them for equipment. `lend_lease_cost`, `manpower`, `can_license` and `is_convertable` are not in the enum but are ordinary equipment keys. [vanilla-confirmed 1.19.4.1] `common/script_enums.txt`, `common/units/equipment/*.txt`
<!-- kit:end id="equipment-stats-enum" -->

<!-- kit:begin id="equipment-naval-stats-warning" at="heading:navy-specific" -->
Four stat names in the list below do not exist in 1.19.4.1: `fire_range`, `shore_bombardment`, `evasion` and `port_capacity_usage`. None is set in any vanilla equipment or unit file, none is in the game documentation or in `script_enum_equipment_stat`, and `hoi4.exe` holds no script token with these exact names (only the longer `shore_bombardment_bonus` and `shore_bombardment_collateral_damage_factor` exist). The word `evasion` survives only in the comments of the defines `COMBAT_EVASION_TO_HIT_CHANCE` and `COMBAT_EVASION_TO_HIT_CHANCE_TORPEDO_MULT` in `common/defines/00_defines.lua`. The wiki already marks the first three OBSOLETE; treat all four as dead and do not write them. `search_and_destroy_coordination` and `convoy_raiding_coordination` are valid stats (in the enum), but no vanilla equipment block sets them. Real naval hull stats that the list omits include `naval_dominance_factor` (50 blocks), `naval_weather_penalty_factor` (7), `lg_attack`, `hg_attack` and the armour piercing pair (see the enum above). [vanilla-confirmed 1.19.4.1] `common/script_enums.txt`, `common/units/equipment/ship_hull_*.txt`
<!-- kit:end id="equipment-naval-stats-warning" -->

<!-- kit:begin id="equipment-air-stats" at="section:air-specific" -->
`carrier_capable` is a boolean equipment key, not a stat: 11 vanilla airframes set `carrier_capable = yes`. `default_carrier_composition_weight` is set in two vanilla blocks and is not in `script_enum_equipment_stat`. `air_ground_attack` (12 blocks), `air_bombing` (21), `air_superiority` (52), `naval_strike_attack` (72), `naval_strike_targetting` (70) and `carrier_size` (6) are all in the enum. [vanilla-confirmed 1.19.4.1] `common/units/equipment/*.txt`, `common/script_enums.txt`
<!-- kit:end id="equipment-air-stats" -->

<!-- kit:begin id="equipment-localization" at="section:localization" -->
Vanilla defines `<TAG>_<equipment>` and `<TAG>_<equipment>_short` pairs for country names (`CHI_light_tank_equipment_1` with `CHI_light_tank_equipment_1_short`), 1626 `_short` keys in `equipment_l_english.yml`. Chassis, hulls and airframes are named in module and ship files (`tank_modules_l_english.yml` holds `light_tank_chassis: "Light Tank"`). A comment in `x_tank_chassis.txt` says `variant_name` is what would otherwise be the localisation key (`light_tank_aa_chassis_1` gets `light_tank_aa_equipment_1`). [vanilla-confirmed 1.19.3] `localisation/english/equipment_l_english.yml`, `localisation/english/tank_modules_l_english.yml`, `common/units/equipment/x_tank_chassis.txt`
<!-- kit:end id="equipment-localization" -->
