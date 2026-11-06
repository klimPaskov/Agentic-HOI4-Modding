# HOI4 Map and States: State files, categories and buildings

Part of the [hoi4-map-states](../SKILL.md) skill. Read before writing or editing history/states files, state categories, building definitions or their map models.

## State history files: skeleton and keys

Files live in `history/states/*.txt`. The filename is not read; only the contents and the `id` matter. Because of that, renaming a vanilla file in a mod can load both the vanilla state and the mod state, so override by keeping the filename or by using `replace_path` for the folder.

Skeleton assembled from `GAME/history/states/1-France.txt` and `116-Malta.txt`:

```
state = {
	id = 1
	name = "STATE_1"
	manpower = 322900
	state_category = town
	history = {
		owner = FRA
		victory_points = { 3838 1 }
		buildings = {
			infrastructure = 2
			industrial_complex = 1
			air_base = 1
			3838 = {
				naval_base = 3
			}
		}
		add_core_of = COR
		add_core_of = FRA
		1939.1.1 = {
			controller = ITA
		}
	}
	provinces = {
		3838 9851 11804
	}
	local_supplies = 0.0
}
```

Top-level keys seen in the 1,081 vanilla state files: `id`, `name`, `manpower`, `state_category`, `history`, `provinces`, `local_supplies` (most files), `resources` (about half), `buildings_max_level_factor`, `impassable`, `force_link_ownership_to`, `impassable_ignored_links`.

- `id`: must be contiguous from 1 to the highest id; a gap crashes unless debug mode is on. Delete by moving the last state into the gap and fixing every reference.
- `name = "STATE_<id>"` keys live in `localisation/english/state_names_l_english.yml` by default; `set_state_name` and `reset_state_name` rename at runtime.
- `manpower`: total population (recruitable and not). Read it in script with `state_population_k` (thousands) to avoid overflow.
- `state_category`: a key from `common/state_category`. Unknown keys are an error.
- `impassable = yes`: troops cannot enter, provinces go to the nearest passable controller, no provincial buildings. Vanilla impassable enclaves also set `force_link_ownership_to = <state id>` and optionally `impassable_ignored_links = { <state ids> }`; those two keys are used in 21 and 1 vanilla files respectively and are not documented in the wiki or installed docs, so copy them only from the vanilla precedent.
- `resources = { steel = 10 ... }`: integers per resource; keys are the resources in `common/resources`.
- `local_supplies`: one unit equals 0.2 supply; default 0.
- `history` is an effect block executed at game start. Common contents: `owner`, `controller` (only when different), `add_core_of`, `add_claim_by`, `victory_points`, `buildings`, `set_demilitarized_zone`, `add_dynamic_modifier`, `set_variable`, `strategic_province_location`, `strategic_state_location`, `set_compliance`, `start_resistance`, and `IF` or `if` blocks with `has_dlc`.
- Dated blocks (`1939.1.1 = { ... }`) run only when the start date is strictly after the date (State modding, History).
- A state with no `owner` loads, but executing nearly any effect on it (including a transfer) crashes. Always give an owner, even to a placeholder tag, if script will touch the state.
- `buildings = { ... }` sets levels. Plain keys set state-level buildings; a province id block (`3838 = { naval_base = 3 }`) sets provincial buildings. A dated `buildings` block only changes the levels it names (the wiki example notes that raising infrastructure there does not change factory counts). Coastal-only buildings cannot be listed in landlocked states, even at 0.
- `victory_points = { <province> <value> }` takes one province per line; repeat the line for several. Localise each as `VICTORY_POINTS_<province>` in `victory_points_l_english.yml`. The marker position comes from `unitstacks.txt` type 38.
- `strategic_province_location = { <location_name> = <province> }` and `strategic_state_location` assign entries from `common/strategic_locations` that add or subtract provincial building caps (vanilla example in `116-Malta.txt`).
- Quotes: the Nudger strips quotation marks from state files, which breaks `has_dlc = "..."` checks. Reread any state file the Nudger rewrote.
- `has_dlc` strings in state files carry no diacritics, for example `Gotterdammerung` and `Waking the Tiger`. [vanilla-confirmed 1.19.4.1]

## State categories and building slots

`common/state_category/*.txt` (one file per category in vanilla):

```
state_categories = {
	city = {
		local_building_slots = 6
		color = { 0 200 0 }
	}
}
```

- A category is a state-scope modifier block plus `color`. `local_building_slots` is the shared-slot count (wasteland 0, rural 2, town 4, city 6, megalopolis 12). `GAME/common/state_category/large_island.txt` shows `buildings_max_level = { naval_base = 8 air_base = 6 }` inside a category.
- Wiki list of vanilla categories: wasteland, enclave, tiny_island, pastoral, small_island, rural, town, large_town, city, large_city, metropolis, megalopolis (the install also contains `large_island`).
- `set_state_category = <key>` changes it at runtime; `has_state_category` tests it; `add_extra_state_shared_building_slots = <int or var>` adds shared slots without changing category; `buildings_max_level_factor` in a state file multiplies the unlocked slots (the wiki recommends categories instead).
- Dynamic variable values with a saved event target must be written `saved_event.var_name`, not `event_target:saved_event.var_name`, for `add_extra_state_shared_building_slots` (Effects wiki note).

## Buildings (common/buildings) and building models

Definitions live in `common/buildings/*.txt` under `buildings = { name = { ... } }` (`GAME/common/buildings/00_buildings.txt`). Fields verified in the vanilla file and `WIKI/building_modding.md`:

- Cost: `base_cost`, `per_level_extra_cost`, `per_controlled_building_extra_cost`, `infrastructure_construction_effect = yes`.
- Slot class from `level_cap`: `shares_slots = yes` (shared, uses state slots), `state_max = N` (non-shared state building), `province_max = N` (provincial), `group_by`, `exclusive_with`. Default `state_max` is 15 when unset.
- Behaviour: `military_production`, `general_production`, `naval_production`, `infrastructure`, `air_base`, `supply_node`, `is_port`, `land_fort`, `naval_fort`, `refinery`, `fuel_silo`, `radar`, `rocket_production`, `rocket_launch_capacity`, `nuclear_reactor`, `gun_emplacement`.
- Effects: `country_modifiers = { modifiers = { ... } }`, `state_modifiers = { ... }`, `show_modifier = yes`, `province_damage_modifiers`, `state_damage_modifier`.
- Availability and UI: `only_costal` (sic), `disabled_in_dmz`, `need_supply`, `allied_build`, `is_buildable = no`, `dlc_allowed`, `icon_frame` (frame in `GFX_buildings_strip`), `special_icon`, `only_display_if_exists`, `tags`, `value`, `damage_factor`, `specialization`.
- Models: `show_on_map`, `show_on_map_meshes`, `always_shown`, `has_destroyed_mesh`, `centered`, `spawn_point = <name>`. Spawn points are declared in the same file under `spawn_points = { name = { type = state|province max = N only_costal = yes } }`; several buildings can share one (vanilla `naval_base_spawn`, `rocket_site_spawn`, `dam_spawn`). The entity name must be `building_<name>`, with `_1`, `_2` suffixes for multiple meshes and `_destroyed` for the destroyed mesh.
- In `map/buildings.txt` a building that has a `spawn_point` is listed under the spawn point name (`naval_base_spawn`, `special_project_facility_spawn`) instead of the building id. [vanilla-confirmed 1.19.4.1]
- Every state in `map/buildings.txt` carries one `air_base`, one `rocket_site_spawn` and one `nuclear_reactor_spawn` row. [vanilla-confirmed 1.19.4.1]
- Terrain limits: `buildings_max_level` inside `common/terrain` categories; `strategic_locations` add per-province offsets.

Localisation for building `my_building`: `my_building`, `my_building_desc`, `my_building_plural`, and for the generated modifiers `modifier_production_speed_my_building_factor` (and `_desc`) and `modifier_state_production_my_building_factor` (and `_desc`). Adding an equipment type, building, or other modifier-bearing archetype may also need `common/script_enums.txt` entries in this repository.

`need_detection` is only safe on provincial buildings. Vanilla sets it only on facilities and dams (`naval_facility`, `nuclear_facility`, `air_facility`, `land_facility`, `dam`, `dam_mountain`, `cataract_dam_mountain`), all with `province_max = 1`, together with `detecting_intel_type`. A state-level building with `need_detection = yes` crashed the map in live testing when a foreign player zoomed onto it; the engine keeps raid-detection records for provincial buildings only. The installed wiki marks the field's meaning as unknown.

Railways (`rail_way`) and supply hubs (`supply_node`) are provincial buildings. Build railways with `build_railway`: vanilla never uses `add_building_construction` for `rail_way`, and the wiki states that the generic building effects crash on it. Supply hubs work with `add_building_construction = { type = supply_node ... }`, which vanilla uses 72 times. [vanilla-confirmed 1.19.4.1]

