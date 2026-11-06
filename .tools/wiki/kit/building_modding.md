# Building modding

<!-- kit:begin id="review" build="1.19.4.1" checked="2026-11-01" revision="104005" sources="common/buildings/ interface/countrystateview.gfx gfx/interface/buildings/building_icon_strip.dds gfx/entities/buildings.asset map/buildings.txt common/terrain/00_terrain.txt common/state_category/ common/special_projects/specialization/ common/defines/00_defines.lua localisation/english/ history/states/ documentation/effects_documentation.md documentation/triggers_documentation.md documentation/modifiers_documentation.md documentation/dynamic_variables_documentation.md" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Checked against: both files in `common/buildings/` (all 55 buildings parsed), the building defines, the building effects, triggers and modifier families, the icon strip, and the model position file.
Kit blocks added: every building key vanilla uses that the page lacks or has wrong, the full building list with costs and level caps, corrections (`special_icon` is a sprite name, `enable_for_controllers` needs `=`, `noOfFrames` is 31, the state modifier localisation key, `max_level` in the example), and the script that works with buildings.
The "need to be updated" marker is an instruction about the icon strip, not a stale section. The five footnoted defines all still have the quoted values.
Gaps left: what `affects_energy`, `need_detection`, `centered` and `base_cost_conversion` do is not stated in any game file; the blocks say `[unverified]`.
**1.19.4.1 re-check (2026-11-01).** 10 tagged statements depended on files the update changed (the defines file, `map/buildings.txt`, English localisation, state history, and scripts scanned for effect counts) and all were re-measured. One number moved: `add_offsite_building` is used in 98 files (was 99). Every other statement cites files that are byte-identical in 1.19.4.1 (Steam depot manifest diff).
<!-- kit:end id="review" -->

<!-- kit:begin id="building-cost-notes" at="section:cost" -->
Cost keys used in vanilla: `base_cost` (all 55 buildings), `per_level_extra_cost` (5), `per_controlled_building_extra_cost` (5, on the facilities and the naval headquarters) and `base_cost_conversion` (2: `arms_factory` 4000 and `industrial_complex` 9000). [vanilla-confirmed 1.19.3] `common/buildings/00_buildings.txt`

- `per_level_extra_cost` may be negative: `fuel_silo` uses `-500`, so each extra level is cheaper. [vanilla-confirmed 1.19.3] `common/buildings/00_buildings.txt`
- What `base_cost_conversion` does is not stated in any game file; it appears only on the two factory types, which suggests a factory conversion cost. [unverified]
- The "4 IC per day" figure is the base speed of an unpowered factory. 1.19.4.1 has separate defines: `BASE_FACTORY_SPEED = 4`, `BASE_FACTORY_SPEED_MIL = 3.5`, `BASE_FACTORY_SPEED_NAV = 2.0`, and for powered factories (the energy system) `POWERED_FACTORY_SPEED = 5`, `POWERED_FACTORY_SPEED_MIL = 4.5`, `POWERED_FACTORY_SPEED_NAV = 2.5`, all in `NProduction`. [vanilla-confirmed 1.19.4.1] `common/defines/00_defines.lua`
- Modifiers that act on one building type: `production_cost_<Building>_factor` (cost), `production_speed_<Building>_factor` (speed) and `repair_speed_<Building>_factor` at country level, and `state_production_speed_<Building>_factor` and `state_repair_speed_<Building>_factor` at state level. The documentation lists all 55 buildings for each of these five families. [docs] `documentation/modifiers_documentation.md`
<!-- kit:end id="building-cost-notes" -->

<!-- kit:begin id="building-slot-notes" at="section:slots" -->
`level_cap` keys as vanilla uses them. All rows: [vanilla-confirmed 1.19.3] `common/buildings/*.txt`.

| Key | Buildings using it | Notes |
| --- | --- | --- |
| `province_max` | 38 | makes the building provincial |
| `state_max` | 20 | the facilities set both `province_max = 1` and `state_max = 1` (one per province and one per state) |
| `shares_slots` | 13 | `yes` = uses the shared slots of the state |
| `group_by` | 9 | values `special_project_facility` (4 facilities), `reactors` (3 reactors), `infrastructure_keystone` (2 grids) |
| `exclusive_with` | 2 | `mega_gun_emplacement` and `rocket_site` exclude each other |

`fuel_silo` has `shares_slots = yes` and no `state_max`, so its cap is `MAX_BUILDING_LEVELS = 15`, the default the wiki states. Also in `NBuildings`: `MAX_SHARED_SLOTS = 25` and `OWNER_CHANGE_EXTRA_SHARED_SLOTS_FACTOR = 1`. [vanilla-confirmed 1.19.4.1] `common/defines/00_defines.lua`

Three more places cap levels. Terrain: only `bunker` (3, 4 or 5) and `coastal_bunker` (6) appear in `buildings_max_level` blocks of `common/terrain/00_terrain.txt`. State categories: the island categories carry `buildings_max_level = { naval_base = N air_base = N }` (see the State modding page). Modifiers: `<Building>_max_level_terrain_limit` and `state_<Building>_max_level_terrain_limit`, plus per-terrain forms such as `air_base_desert_max_level_terrain_limit` (building name plus terrain name, 770 combinations). The two plain families list 54 buildings, all but `dam_mountain`. [vanilla-confirmed 1.19.3] `common/terrain/00_terrain.txt`, `common/state_category/`. [docs] `documentation/modifiers_documentation.md`

The slots a state offers come from its category (`local_building_slots`), and the modifiers `local_building_slots`, `local_building_slots_factor`, `global_building_slots` and `global_building_slots_factor` change them. [docs] `documentation/modifiers_documentation.md`
<!-- kit:end id="building-slot-notes" -->

<!-- kit:begin id="building-modifier-syntax" at="section:modifiers" -->
The example above leaves out the equals sign. Vanilla writes `enable_for_controllers = { ENG }` (22 times, all in `01_landmark_buildings.txt`); the form without `=` appears only in the comment copied into the example. [vanilla-confirmed 1.19.3] `common/buildings/01_landmark_buildings.txt`

```text
country_modifiers = {
	enable_for_controllers = { ENG }
	modifiers = {
		political_power_factor = 0.03
	}
}
```

`country_modifiers` is used by 28 buildings, `state_modifiers` by 9 and `show_modifier = yes` by 33. A building can use several `state_modifiers` keys, for example the dams: `state_production_speed_buildings_factor`, `local_building_slots_factor`, `state_resources_factor` and `local_factory_energy_consumption`. [vanilla-confirmed 1.19.3] `common/buildings/00_buildings.txt`
<!-- kit:end id="building-modifier-syntax" -->

<!-- kit:begin id="building-argument-notes" at="section:additional-arguments" -->
`special_icon` takes a sprite name, not an integer. All 31 vanilla uses are `GFX_...` names (for example `special_icon = GFX_specialization_naval`, `GFX_dam_icon_small`). [vanilla-confirmed 1.19.3] `common/buildings/*.txt`

Arguments vanilla uses that the list above lacks, or marks as unknown. All rows: [vanilla-confirmed 1.19.3] `common/buildings/*.txt` (counts are buildings).

| Key | Count | Form and use |
| --- | --- | --- |
| `dlc_allowed` | 25 | `dlc_allowed = { has_dlc = Gotterdammerung }`; other values seen: `"No Compromise, No Surrender"`, `"Graveyard of Empires"`, `"Peace For Our Time"` (a single word such as Gotterdammerung is unquoted) |
| `missing_tech_loc` | 3 | a block, not a plain key: `missing_tech_loc = { localization_key = SP_BUILDING_MISSING_PROJECT PROJECT = sp_nuclear_reactor }` |
| `hide_if_missing_tech` | 5 | `yes` on `stronghold_network`, `mega_gun_emplacement` and the three reactors |
| `building_prerequisite` | 2 | `building_prerequisite = { building_dependency = { building = naval_base level = 8 } }` on `naval_supply_hub` and `naval_headquarters` |
| `modules` | 1 | `modules = { naval_leader_module }` on `naval_headquarters` |
| `need_detection` | 7 | `yes` on the facilities and the three dam types; the wiki's `?`. The effect is not stated in any game file [unverified] |
| `detecting_intel_type` | 6 | `civilian` (3 dams), `army`, `airforce`, `navy` (one facility each), as the wiki says |
| `province_damage_modifiers` | 3 | `{ flooded }` on the dams, a static modifier (`common/modifiers/00_static_modifiers.txt`, "on Province"). Resolves the wiki's "need confirmation" |
| `state_damage_modifier` | 2 | `{ kiel_canal_damaged_modifier }` and `{ panama_canal_damaged_modifier }` on the canals, dynamic modifiers (`common/dynamic_modifiers/`). Resolves the wiki's "need confirmation" |
| `affects_energy` | 6 | `yes` on `infrastructure`, `commercial_nuclear_reactor`, the three dams and `energy_infrastructure`. The effect is not stated in any game file [unverified] |
| `tags` | 16 | tags used: `supply_building`, `facility`, `naval_buildings_tag`, `specialization_nuclear`, `dam_building`, `locks_building` |
| `specialization` | 4 | `specialization_naval`, `specialization_nuclear`, `specialization_air`, `specialization_land` |
| `is_buildable` | 27 | `no` on the 3 dams, 2 canals and 22 landmarks |
| `allied_build` | 5 | `infrastructure`, `air_base`, `supply_node`, `naval_base`, `radar_station` |
| `repair_speed_factor` | 22 | the landmarks, via `@landmark_repair_speed_factor = 0.15` (default factor 1.0) |
| `disable_grow_animation`, `drawn_at_distance` | 22, 20 | the landmarks |
| `only_display_if_exists` | 31 | see the wiki text above |

The `damage_factor` values in vanilla are `0` (cannot be damaged by strategic bombing, as the wiki says), `-1` on dams and canals, and small positives such as `0.1` to `0.5`. [vanilla-confirmed 1.19.3] `common/buildings/00_buildings.txt`

`specialization` names are defined in `common/special_projects/specialization/specializations.txt`, as the wiki says. [vanilla-confirmed 1.19.3] file listing of `common/special_projects/specialization/`
<!-- kit:end id="building-argument-notes" -->

<!-- kit:begin id="building-icon-correction" at="section:icon" -->
In 1.19.3 `GFX_buildings_strip` has `noOfFrames = 31`, not 16. `gfx/interface/buildings/building_icon_strip.dds` is 1426 x 46 pixels, which is 31 frames of 46 x 46, and the highest `icon_frame` in use is 31 (`industrial_infrastructure`). [vanilla-confirmed 1.19.3] `interface/countrystateview.gfx`, DDS header of the strip, `common/buildings/00_buildings.txt`

`icon_frame` is 1-based: `infrastructure` is 3, `arms_factory` 2, `industrial_complex` 1. All landmarks share frame 22. [vanilla-confirmed 1.19.3] `common/buildings/*.txt`
<!-- kit:end id="building-icon-correction" -->

<!-- kit:begin id="building-model-notes" at="section:models" -->
The sentence above about `centered = yes` is cut off in the wiki capture. In vanilla `centered = yes` is set on `supply_node` and `radar_station` only; its effect is not stated in any game file. [unverified] `common/buildings/00_buildings.txt`

Other model keys in vanilla: `show_on_map_meshes = 3` (`naval_base`, `dockyard`; entities `building_dockyard_1` to `building_dockyard_3` exist), `has_destroyed_mesh = yes` (`bunker`, `coastal_bunker`, `stronghold_network`) and `always_shown = yes` (26 buildings). The entities are in `gfx/entities/buildings.asset` (107 entities named `building_*`). [vanilla-confirmed 1.19.3] `common/buildings/00_buildings.txt`, `gfx/entities/buildings.asset`

In `map/buildings.txt` the second column is the building id or, for a building with `spawn_point = X`, the spawn point name `X`. Vanilla has 66664 rows and 22 distinct ids: the spawn names `naval_base_spawn`, `special_project_facility_spawn`, `rocket_site_spawn`, `nuclear_reactor_spawn`, `dam_spawn`, `locks_spawn`, `landmark_spawn`, the building ids `air_base`, `anti_air_building`, `arms_factory`, `bunker`, `coastal_bunker`, `dockyard`, `fuel_silo`, `industrial_complex`, `naval_headquarters`, `naval_supply_hub`, `radar_station`, `stronghold_network`, `supply_node`, `synthetic_refinery`, and `floating_harbor`. There are 10154 `supply_node` rows, the same as the number of land provinces. [vanilla-confirmed 1.19.4.1] `map/buildings.txt`
<!-- kit:end id="building-model-notes" -->

<!-- kit:begin id="building-property-keys" at="section:effects" -->
Building properties that vanilla uses and the table above lacks. They are keys of the building definition, not modifiers. All rows: [vanilla-confirmed 1.19.3] `common/buildings/00_buildings.txt`.

| Key | Used by | Value |
| --- | --- | --- |
| `anti_air` | `anti_air_building` | `yes` |
| `air_defence` | `anti_air_building` | `1`; the modifier documentation has `air_defence_factor` but no plain `air_defence` [docs] `documentation/modifiers_documentation.md`. Whether the wiki sentence above is right to group it with state modifiers is [unverified] |
| `local_resources_<resource>` | `synthetic_refinery` (`local_resources_rubber = 1`, a commented `local_resources_oil`) | the comment in the file says any resource name may follow |
| `naval_supply_hub` | `naval_supply_hub` | `yes` |
| `naval_headquarter` | `naval_headquarters` | `yes` (singular key) |
| `nuclear_reactor` | the three reactors | `yes` |
| `rocket_production`, `rocket_launch_capacity` | `rocket_site` | `0` and `1` |
| `military_production`, `general_production`, `naval_production` | `arms_factory`, `industrial_complex`, `dockyard` | `1` each |

Keys already in the table are used as: `land_fort = 1` on `bunker`, `naval_fort = 1` on `coastal_bunker`, `is_port = yes` on `naval_base`, `refinery = yes`, `fuel_silo = yes`, `radar = yes`, `gun_emplacement = yes`, `infrastructure = yes` and `air_base = yes` and `supply_node = yes` on the buildings of the same name. A building with none of these keys is just a state or country modifier carrier, like the two electrical grids.
<!-- kit:end id="building-property-keys" -->

<!-- kit:begin id="building-example-note" at="section:example" -->
`max_level = 2` in `my_non_shared_building` is not a building key. No vanilla building uses it; the cap is `level_cap = { state_max = 2 }`, which the example also sets. Leave `max_level` out. [vanilla-confirmed 1.19.3] `common/buildings/*.txt`

The modifiers the examples use (`recruitable_population_factor`, `army_attack_factor`, `army_defence_factor`, `political_power_factor`, `local_building_slots_factor`) exist in the modifier documentation. [docs] `documentation/modifiers_documentation.md`
<!-- kit:end id="building-example-note" -->

<!-- kit:begin id="building-spawn-notes" at="section:spawn-point" -->
`spawn_points = { ... }` sits in the same file as `buildings = { ... }` (a second top-level block). Vanilla defines seven; a building opts in with `spawn_point = <name>` (37 buildings). [vanilla-confirmed 1.19.3] `common/buildings/00_buildings.txt`, `common/buildings/01_landmark_buildings.txt`

| Spawn point | `type` | Extra keys |
| --- | --- | --- |
| `nuclear_reactor_spawn` | state | `max = 1` |
| `rocket_site_spawn` | state | `max = 1` (also used by `mega_gun_emplacement`) |
| `special_project_facility_spawn` | province | `max = 1` |
| `naval_base_spawn` | province | `max = 1`, `only_costal = yes` |
| `dam_spawn`, `locks_spawn`, `landmark_spawn` | province | `max = 1`, `disable_auto_nudging = yes` |
<!-- kit:end id="building-spawn-notes" -->

<!-- kit:begin id="building-loc-correction" at="section:localization" -->
The last two keys in the list above are wrong. The state modifier key is `modifier_state_production_speed_<building>_factor` (with `speed`), matching the modifier `state_production_speed_<building>_factor` that the wiki names below it. Vanilla: `modifier_state_production_speed_infrastructure_factor` and its `_desc`. [vanilla-confirmed 1.19.4.1] `localisation/english/`

Vanilla also localises the other families, for example `modifier_repair_speed_infrastructure_factor` and `modifier_state_repair_speed_bunker_factor`, and uses `$bunker$` references inside the text. The building names themselves are plain keys: `infrastructure`, `infrastructure_desc`, `infrastructure_plural`. [vanilla-confirmed 1.19.4.1] `localisation/english/`
<!-- kit:end id="building-loc-correction" -->

<!-- kit:begin id="building-types-all" at="section:types" -->
The table above lists 32 of the 55 buildings in 1.19.3 and gives `rail_way` a maximum of 5. `common/buildings/00_buildings.txt` defines 33 buildings (the table lacks `cataract_dam_mountain`) and `01_landmark_buildings.txt` defines 22 more, all `landmark_*`. In the file `rail_way` has `province_max = 1`; the maximum railway level is the define `NSupply.MAX_RAILWAY_LEVEL = 5`, as footnote 5 says. [vanilla-confirmed 1.19.4.1] `common/buildings/00_buildings.txt`, `common/defines/00_defines.lua`

All 33 buildings of `00_buildings.txt` as 1.19.3 defines them. "Kind" follows the page's wording: shared slots, state-level own slots, or provincial. Cost is `base_cost`, with extra cost terms in brackets. All rows: [vanilla-confirmed 1.19.3] `common/buildings/00_buildings.txt`.

| Building | Kind | Level cap | Cost | Flags |
| --- | --- | --- | --- | --- |
| `infrastructure` | Non-shared | state 5 | 6000 |  |
| `arms_factory` | Shared | state 20 | 7200 (conversion 4000) |  |
| `industrial_complex` | Shared | state 20 | 10800 (conversion 9000) |  |
| `air_base` | Non-shared | state 10 | 1250 |  |
| `supply_node` | Provincial | province 1 | 20000 |  |
| `rail_way` | Provincial | province 1 | 170 (+130/level) |  |
| `naval_facility` | Provincial | province 1, state 1 | 10000 (+6000/building owned) | coastal only; group special_project_facility; spawn naval_base_spawn |
| `naval_base` | Provincial | province 10 | 5000 (+1000/level) | coastal only; spawn naval_base_spawn |
| `bunker` | Provincial | province 10 | 500 (+500/level) |  |
| `coastal_bunker` | Provincial | province 10 | 500 (+500/level) | coastal only |
| `stronghold_network` | Shared | state 1 | 20000 | DLC |
| `dockyard` | Shared | state 20 | 6400 | coastal only |
| `anti_air_building` | Non-shared | state 5 | 2500 |  |
| `synthetic_refinery` | Shared | state 3 | 14500 |  |
| `fuel_silo` | Shared | state 15 (default) | 5000 (-500/level) |  |
| `radar_station` | Non-shared | state 6 | 3375 |  |
| `mega_gun_emplacement` | Shared | state 1 | 20000 | DLC; excludes rocket_site; spawn rocket_site_spawn |
| `rocket_site` | Shared | state 3 | 6400 | excludes mega_gun_emplacement; spawn rocket_site_spawn |
| `naval_supply_hub` | Provincial | province 1 | 12500 | coastal only |
| `naval_headquarters` | Provincial | province 1 | 10000 (+5000/building owned) | DLC; coastal only |
| `nuclear_reactor` | Shared | state 1 | 30000 | group reactors; spawn nuclear_reactor_spawn |
| `nuclear_reactor_heavy_water` | Shared | state 1 | 25000 | group reactors; spawn nuclear_reactor_spawn |
| `commercial_nuclear_reactor` | Shared | state 1 | 35000 | DLC; group reactors; spawn nuclear_reactor_spawn |
| `nuclear_facility` | Provincial | province 1, state 1 | 15000 (+5000/building owned) | group special_project_facility; spawn special_project_facility_spawn |
| `air_facility` | Provincial | province 1, state 1 | 10000 (+6000/building owned) | group special_project_facility; spawn special_project_facility_spawn |
| `land_facility` | Provincial | province 1, state 1 | 10000 (+6000/building owned) | group special_project_facility; spawn special_project_facility_spawn |
| `dam` | Provincial | province 1 | 20000 | not buildable; spawn dam_spawn |
| `dam_mountain` | Provincial | province 1 | 20000 | not buildable; spawn dam_spawn |
| `cataract_dam_mountain` | Provincial | province 1 | 20000 | not buildable; spawn dam_spawn |
| `canal_kiel` | Provincial | province 1 | 20000 | not buildable; spawn locks_spawn |
| `canal_panama` | Provincial | province 1 | 20000 | not buildable; spawn locks_spawn |
| `energy_infrastructure` | Shared | state 1 | 12000 | group infrastructure_keystone |
| `industrial_infrastructure` | Shared | state 1 | 12000 | group infrastructure_keystone |

The 22 landmarks (`landmark_big_ben`, `landmark_colosseum`, `landmark_cristo_redentor`, `landmark_eiffel_tower`, `landmark_statue_of_liberty`, `landmark_kremlin`, `landmark_hofburg_palace`, `landmark_berlin_reichstag`, `landmark_berlin_volkshalle`, `landmark_taj_mahal`, `landmark_sadabad_complex`, `landmark_hagia_sophia`, `landmark_forbidden_city`, `landmark_nanjing_presidential_palace`, `landmark_nanjing_presidential_palace_prc`, `landmark_nanjing_presidential_palace_gen`, `landmark_great_wall_section`, `landmark_tokyo_imperial_palace`, `landmark_national_diet`, `landmark_hakko_ichiu`, `landmark_prague_castle`, `landmark_bojnice_castle`) are provincial (`province_max = 1`), cost 20000, are not buildable (`is_buildable = no`), use `landmark_spawn` and `icon_frame = 22`, and each grants a country modifier to the controllers named in its `enable_for_controllers`. 17 of them appear in vanilla state history. [vanilla-confirmed 1.19.4.1] `common/buildings/01_landmark_buildings.txt`, `history/states/`

The closing note is wrong for supply hubs: vanilla builds `supply_node` with `add_building_construction` in 72 blocks across 21 files, and no `rail_way` is built that way (railways use `build_railway`). Starting levels of both still come from `map/supply_nodes.txt` and `map/railways.txt`, not from state history. [vanilla-confirmed 1.19.4.1] `common/decisions/SIA.txt` and others, `history/states/`
<!-- kit:end id="building-types-all" -->

<!-- kit:begin id="building-script-surface" at="bottom" -->
## Script that works with buildings

All rows: [docs] `documentation/effects_documentation.md`, `documentation/triggers_documentation.md`, `documentation/dynamic_variables_documentation.md`, `documentation/modifiers_documentation.md`. The last column adds vanilla syntax where the documentation is a one-liner ([vanilla-confirmed 1.19.4.1] `common/`, `events/`).

| Name | Kind and scope | Syntax or note |
| --- | --- | --- |
| `add_building_construction` | effect, state | `type`, `level`, `instant_build = yes`, and `province = <id>` or a block with `id`, `all_provinces = yes`, `limit_to_coastal`, `limit_to_naval_base`, `limit_to_border`, `limit_to_victory_point`, `limit_to_border_country`, `limit_to_supply_node` (about 4900 uses in `common/`) |
| `set_building_level` | effect, state | `type`, `level`, `province`; vanilla also puts `level < N` inside the `province = { }` block (9 files) |
| `remove_building` | effect, state or country | `type` or `tags`, `level`, `state` or `province` |
| `damage_building` | effect, state or country | `type` or `tags`, `damage`, `repair_speed_modifier`, `state` or `province` |
| `construct_building_in_random_province` | effect, state | `construct_building_in_random_province = { land_facility = 1 }` |
| `add_extra_state_shared_building_slots` | effect, state | a number (155 files) |
| `add_offsite_building` | effect, country | `type`, `level` (98 files) |
| `modify_building_resources` | effect, country | `building`, `resource`, `amount` |
| `build_railway` | effect, any | see [Supply areas modding](supply_areas_modding.md) |
| `building_count_trigger` | trigger, state or country | `<building> < N`; the documentation lists all 55 building ids as supported |
| `free_building_slots` | trigger, state | `building`, `size`, optional `include_locked`, optional `province` |
| `can_construct_building` | trigger, state | `can_construct_building = land_facility` with the country as ROOT |
| `any_province_building_level` | trigger, state | `province = { id / all_provinces / limit_to_* }`, `building`, `level` |
| `non_damaged_building_level` | trigger, state | `building`, `level` |
| `has_damaged_buildings` | trigger, country | no arguments |
| `building_level@<building>`, `damaged_building_level@<building>`, `non_damaged_building_level@<building>` | dynamic variables, state | for example `building_level@arms_factory` |
| `production_speed_buildings_factor`, `state_production_speed_buildings_factor`, `global_building_slots` and the `<Building>` families | modifiers | see the notes above |

Defines in `NBuildings` besides the two named above: `AIRBASE_CAPACITY_MULT = 200`, `ROCKETSITE_CAPACITY_MULT = 100`, `NAVALBASE_REPAIR_MULT = 0.05`, `RADAR_RANGE_BASE = 20`, `RADAR_RANGE_MIN = 20`, `RADAR_RANGE_MAX = 200`, `SUPPLY_PORT_LEVEL_THROUGHPUT = 3`, `BASE_FACTORY_REPAIR = 1.0`, `BASE_FACTORY_REPAIR_FACTOR = 2.0`, `DESTRUCTION_COOLDOWN_IN_WAR = 30`, `ANTI_AIR_SUPERIORITY_MULT = 5.0`. [vanilla-confirmed 1.19.4.1] `common/defines/00_defines.lua`
<!-- kit:end id="building-script-surface" -->
