---
name: hoi4-map-states
description: Use when creating, editing, auditing, or scripting Hearts of Iron IV map and state data, including map/ files, history/states, strategic regions, state categories, buildings, victory points, supply and railways, state-scope effects and triggers, state iteration, and the MCP map tools.
---

# HOI4 Map and States

Generic guidance for the Hearts of Iron IV map and state system: what each map file does, how a state is defined, how script changes states at runtime, and which engine mistakes fail silently.
Use `hoi4-decisions-missions` for decisions that target states, and `hoi4-events` for event chains that mutate states.
Dynamic modifiers on states are covered in `hoi4-ideas-modifiers`, state transfers as diplomacy (peace deals, release, annexation) in `hoi4-diplomacy-war`, and `load_oob`, `create_unit`, and division spawning in `hoi4-units-divisions`.

## Contents

- Source map: where the authoritative text lives
- Decision procedure: which mechanism for which goal
- Map folder summary (full formats in references/map-geometry.md)
- State history files: skeleton and keys
- State categories and building slots
- Buildings (common/buildings) and building models
- Runtime state effects
- Runtime state triggers
- Iterating states and the loop cap
- Flags, variables, and modifiers on states
- Victory points, resources, supply, railways at runtime
- Map modes and map GFX
- MCP map tools
- Validation procedure
- Repository conventions
- Common mistakes and silent failures
- Unverified or conflicting points

## Source map

`GAME` means the installed Hearts of Iron IV folder named in `CLAUDE.md`.
`WIKI` means the offline snapshot in `paradox_wiki/` at the mod root.
Installed documentation is more authoritative than the wiki; where they disagree, follow the installed file and record the conflict.

| Topic | Authoritative text | Vanilla precedent |
| --- | --- | --- |
| Map folder overview, BMP rules, provinces, terrain, adjacencies, supply files | `WIKI/Map modding - Hearts of Iron 4 Wiki.md` | `GAME/map/` |
| State file keys, history block, state categories, building list | `WIKI/State modding - Hearts of Iron 4 Wiki.md` | `GAME/history/states/1-France.txt` (minimal), `116-Malta.txt` (strategic_province_location), `1022 - Interior Borneo.txt` (impassable enclave), `1032 - Yanan.txt` (IF with has_dlc inside history) |
| Strategic region file, weather periods | `WIKI/Strategic region modding - Hearts of Iron 4 Wiki.md` | `GAME/map/strategicregions/1-Southern England.txt`, `100-Red Sea.txt` |
| Building definition fields, slots, spawn points | `WIKI/Building modding - Hearts of Iron 4 Wiki.md` | `GAME/common/buildings/00_buildings.txt`, `01_landmark_buildings.txt` |
| Strategic locations (extra provincial building cap) | `GAME/common/strategic_locations/documentation.md` | `GAME/common/strategic_locations/strategic_locations.txt` |
| Scripted map modes | `GAME/common/map_modes/documentation.md` | none in vanilla (documentation only) |
| Resources | `GAME/common/resources/_documentation.md`, `WIKI/Resources modding - Hearts of Iron 4 Wiki.md` | `GAME/common/resources/00_resources.txt` |
| State effects | `GAME/documentation/effects_documentation.md`, section "Effects for scope STATE", plus the individual entries named below | `GAME/common/national_focus/*.txt`, `GAME/events/*.txt` |
| State triggers | `GAME/documentation/triggers_documentation.md`, section "Triggers for scope STATE" | same |
| Effect argument tables (more detail than the installed file for building and flag effects) | `WIKI/Effects - Hearts of Iron 4 Wiki.md` (rows `add_building_construction`, `set_building_level`, `set_state_flag`, `build_railway`, `add_resource`, `transfer_state_to`) | |
| Collections, `game:all_states` | `GAME/documentation/script_concept_documentation.md` (Collections), `script_collection_input.md`, `script_collection_operator.md` | |
| Loop cap | `GAME/common/defines/00_defines.lua` (`MAX_EFFECT_ITERATION = 1000`) | |
| State modifiers | `GAME/documentation/modifiers_documentation.md`, section "Modifiers for scope state" | `GAME/common/state_category/*.txt` |

Use the hoi4 MCP reference routes (`hoi4_reference_context` with surface `map`, `hoi4_reference_search`, `hoi4_reference_read`, `hoi4_source_lookup`) to cite exact line spans; `hoi4_source_lookup` finds exact vanilla and mod definitions, overrides, and indexed usages.
If a route fails once, retry once with narrower input, then read the local file directly.

## Decision procedure: which mechanism

1. Change what a state or province is at game start (owner, cores, buildings, VPs, resources): edit the `history/states/*.txt` file, not script effects. Use a dated block (`1936.1.1 = { ... }`) when only some bookmarks need the change.
2. Change ownership or control during play: `transfer_state_to` (state scope) or `transfer_state` (country scope) moves owner and controller together. Use `set_state_owner_to` or `set_state_controller_to` only when the two must differ. Use `set_province_controller` for a single province.
3. Give or remove buildings during play: `add_building_construction` (queues construction, `instant_build = yes` skips it), `set_building_level` (sets an exact level), `remove_building`, `damage_building`. Railways and supply hubs use `build_railway` and its own checks, never these (see Buildings).
4. Make a building type that does not exist: `common/buildings`, plus an icon frame, localisation, and (for model-bearing buildings) an entity and `map/buildings.txt` rows.
5. Change the map geometry (new province, state split, new strategic region): use the Agent Nudger MCP routes (`hoi4_map_inspect`, `hoi4_map_inspect` with render arguments (`layer`, `overlays`, `scale`, `tile`, or `area`), `hoi4_map_rewrite`) rather than hand-editing BMPs and CSVs. See MCP map tools.
6. Apply a lasting effect to a state without editing its file: a state dynamic modifier (`add_dynamic_modifier` in state scope; see `hoi4-ideas-modifiers`), a state category change (`set_state_category`), or `add_extra_state_shared_building_slots`. Ideas are country-only and cannot carry a state modifier.
7. Track per-state progress or memory: state flags for presence and small integers, state variables for numbers (see Flags, variables).
8. Visualise per-state data on the map: a scripted map mode (see Map modes).
9. Sweep many states: a scope iterator (`every_owned_state` and siblings), never a numeric loop over state ids (see Iterating states).

## Map folder summary

Geometry files live under `map/` (`GAME/map/` in vanilla). Full file-by-file formats, province and strategic-region rules, adjacency rows, and supply and railway files are in `references/map-geometry.md`; read it before touching any file in this table.

| File | Purpose |
| --- | --- |
| `provinces.bmp` + `definition.csv` | Province borders (24-bit RGB) and per-province id, colour, type, coastal flag, terrain, continent; ids contiguous from 0 |
| `strategicregions/*.txt` | Region membership (every province in exactly one region, all provinces of a state in the same region) and weather; ids sequential |
| `buildings.txt` | Building model positions per state; naval bases and floating harbours need an adjacent sea province |
| `adjacencies.csv`, `adjacency_rules.txt` | Straits, canals, impassable borders |
| `supply_nodes.txt`, `railways.txt` | Starting supply hubs and rails; must reference state-owned land provinces |
| `unitstacks.txt`, `weatherpositions.txt` | Unit, victory-point, and weather object positions |
| `default.map`, `continent.txt` | File redirects and continent list |

`airports.txt` and `rocketsites.txt` are not in the installed `GAME/map/` (the Map modding wiki says they were removed in patch 1.15, while State modding still describes them); trust the installed folder.
Use the MCP map tools for geometry changes instead of hand-editing bitmaps and CSVs.

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

Definitions live in `common/buildings/*.txt` under `buildings = { name = { ... } }` (`GAME/common/buildings/00_buildings.txt`). Fields verified in the vanilla file and `WIKI/Building modding`:

- Cost: `base_cost`, `per_level_extra_cost`, `per_controlled_building_extra_cost`, `infrastructure_construction_effect = yes`.
- Slot class from `level_cap`: `shares_slots = yes` (shared, uses state slots), `state_max = N` (non-shared state building), `province_max = N` (provincial), `group_by`, `exclusive_with`. Default `state_max` is 15 when unset.
- Behaviour: `military_production`, `general_production`, `naval_production`, `infrastructure`, `air_base`, `supply_node`, `is_port`, `land_fort`, `naval_fort`, `refinery`, `fuel_silo`, `radar`, `rocket_production`, `rocket_launch_capacity`, `nuclear_reactor`, `gun_emplacement`.
- Effects: `country_modifiers = { modifiers = { ... } }`, `state_modifiers = { ... }`, `show_modifier = yes`, `province_damage_modifiers`, `state_damage_modifier`.
- Availability and UI: `only_costal` (sic), `disabled_in_dmz`, `need_supply`, `allied_build`, `is_buildable = no`, `dlc_allowed`, `icon_frame` (frame in `GFX_buildings_strip`), `special_icon`, `only_display_if_exists`, `tags`, `value`, `damage_factor`, `specialization`.
- Models: `show_on_map`, `show_on_map_meshes`, `always_shown`, `has_destroyed_mesh`, `centered`, `spawn_point = <name>`. Spawn points are declared in the same file under `spawn_points = { name = { type = state|province max = N only_costal = yes } }`; several buildings can share one (vanilla `naval_base_spawn`, `rocket_site_spawn`, `dam_spawn`). The entity name must be `building_<name>`, with `_1`, `_2` suffixes for multiple meshes and `_destroyed` for the destroyed mesh.
- Terrain limits: `buildings_max_level` inside `common/terrain` categories; `strategic_locations` add per-province offsets.

Localisation for building `my_building`: `my_building`, `my_building_desc`, `my_building_plural`, and for the generated modifiers `modifier_production_speed_my_building_factor` (and `_desc`) and `modifier_state_production_my_building_factor` (and `_desc`). Adding an equipment type, building, or other modifier-bearing archetype may also need `common/script_enums.txt` entries in this repository.

`need_detection` is only safe on provincial buildings. Vanilla sets it only on facilities and dams (`naval_facility`, `nuclear_facility`, `air_facility`, `land_facility`, `dam`, `dam_mountain`, `cataract_dam_mountain`), all with `province_max = 1`, together with `detecting_intel_type`. A state-level building with `need_detection = yes` crashed the map in live testing when a foreign player zoomed onto it; the engine keeps raid-detection records for provincial buildings only. The installed wiki marks the field's meaning as unknown.

Railways (`rail_way`) and supply hubs (`supply_node`) are provincial buildings, but the wiki states that `add_building_construction` and the other generic building effects crash on them; use `build_railway` instead.

## Runtime state effects

State-scope effects verified against `GAME/documentation/effects_documentation.md`:

| Goal | Effect | Scope and notes |
| --- | --- | --- |
| Owner and controller | `transfer_state_to = <country>` | STATE; wiki: sets both |
| Owner and controller | `transfer_state = <state id or var>` | COUNTRY; makes the scoped country owner and controller |
| Owner only | `set_state_owner_to = <country>` / `set_state_owner = <state>` | STATE / COUNTRY; control may stay behind, so prefer transfer |
| Controller only | `set_state_controller_to = <country>` / `set_state_controller = <state>` | STATE / COUNTRY |
| Per-province control | `set_state_province_controller = { controller = TAG limit = { ... } }` | STATE; `limit` runs on each province's current controller; no tooltip |
| Single province control | `set_province_controller = <province>` | COUNTRY; peace or peacetime resets it to the owner unless the controller is at war with the owner |
| Cores | `add_core_of`, `remove_core_of` (STATE); `add_state_core`, `remove_state_core` (COUNTRY, takes a state id) | |
| Claims | `add_claim_by`, `remove_claim_by` (STATE); `add_state_claim`, `remove_state_claim` (COUNTRY) | |
| Buildings | `add_building_construction`, `set_building_level`, `remove_building`, `damage_building`, `construct_building_in_random_province` | `add_building_construction` and `set_building_level` accept `type`, `level`, `instant_build`, and a `province` filter block (`all_provinces`, `id`, `limit_to_coastal`, `limit_to_naval_base`, `limit_to_border`, `limit_to_victory_point`, `limit_to_supply_node`, `level`) |
| Demilitarisation | `set_demilitarized_zone = yes` | STATE |
| Resources | `add_resource = { type = steel amount = 5 days = 60 show_state_in_tooltip = no }` | STATE or COUNTRY; `days` makes it temporary; amounts may be variables |
| Category and slots | `set_state_category`, `add_extra_state_shared_building_slots` | STATE |
| Names | `set_state_name = "..."`, `reset_state_name = yes` | STATE |
| Flags | `set_state_flag`, `clr_state_flag`, `modify_state_flag` | STATE; see Flags |
| Province modifiers | `add_province_modifier = { static_modifiers = { m } province = N days = N }` and `remove_province_modifier` | STATE; static modifiers come from `common/modifiers` |
| Dynamic modifier | `add_dynamic_modifier`, `remove_dynamic_modifier`, `force_update_dynamic_modifier` | STATE, COUNTRY, CHARACTER, SPECIAL_PROJECT |
| Victory points | `add_victory_points = { province = N value = N }`, `set_victory_points = { province = N value = N }` | any scope; accept negative values |
| Railways | `build_railway = { level = 1 start_province = N target_province = N }` (also `path`, `start_state`, `target_state`, `fallback`, `build_only_on_allied`, `controller_priority`) | any scope |
| Occupation | `start_resistance`, `cancel_resistance`, `set_resistance`, `add_resistance`, `set_compliance`, `add_compliance`, `set_garrison_strength`, `set_occupation_law`, `force_enable_resistance`, `force_disable_resistance`, `add_resistance_target` | STATE |
| Units | `teleport_armies = { limit = { ... } to_state = N }` (also `to_province`, `to_state_array`), `create_unit` | STATE |
| Events | `state_event = { id = x days = N }` | STATE or COUNTRY |
| Border wars | `set_border_war = yes` | STATE |
| Strategic locations | `strategic_province_location`, `strategic_state_location` | STATE |

Scope and quirks:

- `add_building_construction` and `set_building_level` only work in a state scope; in a country scope they do nothing. Provincial buildings need the state that contains the province in scope even when `province = N` is given.
- If the building's controller has no order of battle assigned in history, new buildings do not appear in the production menu until a recalculation (for example changing consumer goods or reloading). `load_oob` on a country that owns no states silently does nothing, so load after the first transfer, or use `set_oob` in the country history file.
- Technology gates on building levels are bypassed by `add_building_construction` and state history, but the maximum level cap is not.
- `remove_building` and `damage_building` can name a building by `type` or by `tags`. `remove_building` without `province` in state scope removes state-level buildings only and does not search the state's provinces; `damage_building` in state scope does find provincial buildings through the state. Both can also be called in country scope with an explicit `state` or `province`.
- `add_victory_points` and `set_victory_points` take a province id, not a state id, and need no state scope.

## Runtime state triggers

State-scope: `is_owned_by`, `is_controlled_by`, `is_owned_and_controlled_by`, `is_fully_controlled_by`, `is_core_of`, `is_claimed_by`, `is_capital`, `is_coastal`, `is_island_state`, `is_one_state_island`, `is_on_continent`, `is_on_same_continent_as`, `is_in_home_area`, `impassable`, `is_demilitarized_zone`, `has_state_category`, `has_state_flag`, `has_dynamic_modifier`, `state_population`, `state_population_k`, `has_resources_amount`, `resource_count_trigger`, `building_count_trigger`, `non_damaged_building_level`, `free_building_slots`, `can_construct_building`, `any_province_building_level`, `has_resistance`, `resistance`, `compliance`, `occupation_law`, `num_owned_neighbour_states`, `any_neighbor_state`, `all_neighbor_state`, `any_country_with_core`, `any_state_division`, `region`, `area`, `state`, `distance_to`, `state_strategic_value`.

Country-scope: `owns_state`, `controls_state`, `has_full_control_of_state`, `owns_any_state_of`, `controls_province`, `num_of_controlled_states`, `num_of_supply_nodes`, `any_owned_state`, `all_owned_state`, `any_controlled_state`, `any_core_state`, `any_state`, `all_state`, `has_railway_level`, `can_build_railway`, `has_railway_connection`.

Argument shapes verified in the installed triggers file:

```
free_building_slots = {
	building = industrial_complex
	size > 0
	include_locked = no      # only meaningful for shared-slot buildings
	province = 42            # optional, checks provincial buildings
}
has_resources_amount = { resource = chromium amount > 10 }
building_count_trigger = { industrial_complex > 5 }   # usage: <building> <compare> <int>, STATE or COUNTRY
non_damaged_building_level = { building = arms_factory level = 5 }
has_state_flag = { flag = my_flag value < 3 days > 10 }
any_state_of = { target = { 1 42 1992 } controller = { has_defensive_war = yes } }
any_state_in = { continent = europe <triggers> }       # also array, ai_area, strategic_region
```

- `resource_count_trigger` lists oil, aluminium, rubber, tungsten, steel, chromium, coal; `building_count_trigger` has a fixed supported-building list in the installed text, so a new custom building may not be testable that way; test it with `any_province_building_level` or a state variable you maintain.
- `collection_size` comparisons are inclusive in the repository's observed engine behaviour (`value > 3` means at least 3).
- `scope_exists` is always true on a variable scope; validate a stored state or country with an object-specific check such as `exists = yes` or `country_exists`.
- Flag triggers in player-visible blocks use the flag name as the tooltip key; give state flags a localisation key or hide the check.

## Iterating states and the loop cap

Scope iterators (verified in the installed effects file): `every_state` and `random_state` (any scope, whole map), `every_owned_state`, `random_owned_state`, `every_core_state`, `random_core_state`, `every_controlled_state`, `random_controlled_state`, `random_owned_controlled_state` (country scope), `every_neighbor_state` and `random_neighbor_state` (state scope, the latter does not support `prioritize`). Common optional keys: `limit`, `tooltip`, `random_select_amount`, `display_individual_scopes`, and `prioritize = { <state ids> }` on `random_*` forms. Trigger forms: `any_*`, `all_*`.

```
every_owned_state = {
	limit = {
		is_core_of = ROOT
		free_building_slots = { building = industrial_complex size > 0 include_locked = no }
	}
	random_select_amount = 3
	add_building_construction = { type = industrial_complex level = 1 instant_build = yes }
}
```

Other ways to hold a state set:

- Arrays of state ids with `for_each_loop` (value variable holds the id) or `for_each_scope_loop` (changes scope to each element), and `random_scope_in_array`.
- Collections: `collection_size = { input = game:all_states value > 42 }` and operators such as `owned_states` and `controlled_states` (`script_collection_input.md`, `script_collection_operator.md`). Collections may contain duplicates.
- `any_state_of` accepts a literal id list or a script constant as its `target` (documented with a country-group constant example).

Loop cap: `GAME/common/defines/00_defines.lua` sets `MAX_EFFECT_ITERATION = 1000` ("maximum allowed iteration for loop effects"). Vanilla has 1,081 states, so `for_loop_effect` or `while_loop_effect` over state ids from 1 to the last id stops before finishing. Use a scope iterator for sweeps, or batch the ids across several runs with a stored cursor. The defines comment names loop effects only; no cap is documented for scope iterators.

Whole-world iteration (`every_state`, `every_country`, and any `on_daily`, `on_weekly`, `on_monthly` that fans out over all countries) is expensive. In this repository it needs explicit permission; narrow the scope to the owner, an array, or a tag-specific on action.

## Flags, variables, and modifiers on states

- State flags are 32-bit integers scoped to one state. `set_state_flag = my_flag` sets 1; the block form is `set_state_flag = { flag = my_flag value = 3 days = 50 }`; `modify_state_flag = { flag = x value = N }` changes an existing flag only; `has_state_flag` tests presence, and its block form tests value and age. Flags have no definition file.
- A flag name can carry a targeted suffix (`my_flag_@PREV` appends the scope's tag); only `@ROOT`, `@PREV`, `@FROM`, `@THIS` are supported, one per name.
- State variables: `set_variable`, `add_to_variable`, and friends executed in state scope write that state's variable. Read another state's variable with a numeric prefix (`123.my_var`), a stored scope (`var:target_state.my_var`), or a chain (`province_controllers^1234:capital:my_var`) per `WIKI/Data structures`. Temporary variables have no scope.
- Persist a state pointer across blocks and events with a regular event target (`save_event_target_as`) or a global event target that you clear.
- A state dynamic modifier reads its variables from the state it is attached to, not from the owner. Details, daily refresh, and `scope =` are in `hoi4-ideas-modifiers`; the vanilla state precedent is `ETH_state_development_dynamic_modifier` in `GAME/common/dynamic_modifiers/bba_dynamic_modifiers.txt`.
- Read the total of a modifier on a state with `set_variable = { v = modifier@local_manpower }` in state scope, or `123.modifier@local_manpower` from elsewhere (`dynamic_variables_documentation.md`).

## Victory points, resources, supply, railways at runtime

- Victory points: static in history; runtime `add_victory_points` and `set_victory_points`. There is no state-scope trigger for VP value in the installed triggers file apart from `province_vp` (COMBATANT scope) and the `limit_to_victory_point` province filters. A scripted `GetCapitalVictoryPointName` loc command exists on state scope (Localisation wiki).
- Resources: the permanent source is the state file or a state modifier `state_resource_<Resource>` / `temporary_state_resource_<Resource>` (template modifiers in `modifiers_documentation.md`); `add_resource` with `days` is the effect form. New resources need an entry in `common/resources`, a frame in `GFX_resources_strip`, localisation, and a GUI row, and the AI define `NAI::MIN_FACTORIES_TO_WANT_TO_IMPORT` should be reviewed (`common/resources/_documentation.md`).
- Supply: starting hubs and rails in map files; runtime `build_railway`, `has_railway_level`, `can_build_railway`, `has_railway_connection`, `num_of_supply_nodes`. Railway paths are chosen by explicit `path`, by province pair (shortest path), or by state pair (best supply endpoints), in that order when `fallback = yes`.

## Map modes and map GFX

- Scripted map modes live in `common/map_modes/*.txt` inside `scripted_map_modes = { name = { top = { ... } bottom = { ... } far_text near_text update_daily } }` (`GAME/common/map_modes/documentation.md`). Each layer has `type` (`none`, `country`, `state`, `state_controller`, or a hard-coded `game_map_mode_*`), a `color` trigger block that sets the temporary variables `red`, `green`, `blue`, `alpha` (0 to 1) plus `thickness` and `highlighted`, an optional `targets` block (strongly recommended for performance), and `thickness = yes`. In a state layer `FROM` is the state being rendered. `update_daily = yes` refreshes daily; otherwise call `force_update_map_mode = { mapmode = <id> }`.
- The mode name drives loc keys `MAPMODE_<NAME>`, `MAPMODE_<NAME>_NAME`, `MAPMODE_<NAME>_DESCRIPTION`, `<name>_tooltip`, `<name>_tooltip_delayed`, and sprites `GFX_mapmode_buttons_selected_small_<name>` and `GFX_mapmode_buttons_deselected_small_<name>` (the button strip sprites are declared in `GAME/interface/mapmodes_interface.gfx`).
- Map-facing sprites and entities: building icon strip `GFX_buildings_strip` in `interface/countrystateview.gfx`; building models are entities named `building_<id>` in `gfx/entities/*.asset`; terrain and border textures are in `GAME/map/terrain/`.

## MCP map tools

The Agent Nudger exposes three tools; inspect and render never write source, rewrite writes the configured mod.

- `hoi4_map_inspect`: full validation plus overview by default; set `lookupOnly = true` for bounded lookups. Inputs: `stateIds`, `regionIds`, `provinceIds` (max 32), `coordinates` (`pixel` x/y or `map` x/z), `query`, and `allocationRequests` (ask for the next free state id or an unused province colour). A lookup call returned the workspace totals (13,414 province definitions, 1,081 states, 304 regions, 5,632 x 2,048 pixels, 534 ports) and linked a JSON artifact.
- `hoi4_map_inspect` with render arguments (`layer`, `overlays`, `scale`, `tile`, or `area`): layers `province`, `state`, `strategic-region`, `terrain`, `continent`, `owner`, `controller`, `cores`, `claims`, `coast`; overlays `coastlines`, `ports`, `victory-points`, `resources`, `state-buildings`, `province-buildings`, `supply-nodes`, `railways`, `adjacencies`, `building-positions`, `unit-positions`, `weather-positions`; restrict with `area` (state, region, province ids) or a pixel `tile`.
- `hoi4_map_rewrite`: applies map creation, edits, and id swaps with visual and semantic evidence. Use `requestKey` for stable background retries and check source state before retrying an uncertain write. The operation schema is opaque in the tool listing (`operations` is an array of "complete map operation" objects); one probe with a made-up operation was rejected as invalid arguments, so read the live schema before composing operations.
- Use inspect first to learn current ids and to allocate new ids, render to check geometry, rewrite only for declarative geometry or id changes. For a script-only task (owner changes, buildings, flags) read the state file and use `hoi4_source_lookup`; the map tools are unnecessary.
- If a map route fails once, retry once with narrower input, then read the files directly.

## Validation procedure

1. Confirm every id you added is unique and contiguous: states from 1, strategic regions sequential, provinces from 0. `hoi4_map_inspect` with `allocationRequests` gives the next free ids.
2. Every province in a state is in one strategic region and every state province exists in `definition.csv`.
3. Every state has an `owner`, a known `state_category`, and localisation for `STATE_<id>` and each `VICTORY_POINTS_<province>`.
4. Every naval base or floating harbour has a `buildings.txt` row naming its adjacent sea province; the file is not empty.
5. Supply nodes and railways reference state-owned land provinces.
6. Re-read any state file the Nudger touched (stripped quotes, version-less loc).
7. For script, check each effect's scope against the effects documentation, use `hoi4_script_validate` on the body under its explicit scope when exposed, and treat a `valid` result as covering only its listed checks.
8. Runtime behaviour (ownership after transfer, production-menu visibility, VP markers) is a live-game question; do not report it as verified from source reading alone.

## Repository conventions

- Tabs for indentation, lowercase snake_case, no `<=` or `>=`, UTF-8 with BOM for localisation.
- No magic numbers: put shared tuning (caps, batch sizes, building levels) in `common/script_constants/` and read them with `constant:category.key` where the field supports it; fields that reject constants take a variable or an `@` constant. Duration fields such as `days =` in timed flags may need a variable assigned from the constant first.
- Reuse and extend the project's dynamic scripted effects library (`common/scripted_effects/<prefix>_dynamic_effects.txt`, named in `CLAUDE.md`) before writing new state helpers, such as the existing state building damage and random-state helpers.
- The 1,000-iteration cap and the whole-world iteration permission rule above come from `CLAUDE.md` sections 1 and 4.
- A hidden-idea carrier is a modifier-free idea whose id is a token for a package-owned setup effect (`CLAUDE.md` section 4 item 11); it is unrelated to states.
- Do not write player-facing text about tuning history; state names and VP names describe the world only.

## Common mistakes and silent failures

1. A state without `owner` that script later touches (crash).
2. Gaps in state ids, province ids, or strategic region ids.
3. A state split across two strategic regions.
4. A new naval base or floating harbour without a `buildings.txt` row (late crash when AI or player uses it) or an empty `buildings.txt`.
5. `need_detection = yes` on a state-level building (map crash when zoomed on by a foreign player).
6. `load_oob` for a country that owns no state (silent no-op).
7. Using `add_building_construction` on `rail_way` or `supply_node` (crash per the wiki); use `build_railway`.
8. Calling `add_building_construction` in a country scope (does nothing) or for a provincial building outside the containing state's scope.
9. Looping state ids with `for_loop_effect` past 1,000.
10. `set_state_owner_to` when control should follow; the state keeps the old controller.
11. Province ids that are invalid or belong to no state in `supply_nodes.txt`, `railways.txt`, `unitstacks.txt`, `weatherpositions.txt`, or adjacency rows.
12. LF line endings in `definition.csv` (every continent reads as missing).
13. 32-bit or colour-space-tagged `provinces.bmp`, or editing indexed bitmaps in a tool that rebuilds the palette.
14. Renaming a vanilla state file in a mod (both versions load).
15. Flag triggers in player-visible blocks without a localisation key.
16. Treating `scope_exists` as a state validity check on a stored variable.
17. Treating `add_resource` without `days` as temporary; it stays until a matching negative amount removes it (installed documentation: `days` makes it temporary).
18. Expecting a dated `history` block to run during play; it is evaluated once when the game starts, for dates before the chosen start date.
19. Trusting the wiki claim that `airports.txt` and `rocketsites.txt` are required; the installed game has neither.
20. Forgetting that peace or ceasefire resets `set_province_controller` to the owner.

## Unverified or conflicting points

- `region` versus `area` state triggers: identical installed descriptions; the distinction is not documented.
- `impassable_ignored_links` and `force_link_ownership_to` semantics beyond the vanilla comments.
- Whether scope iterators such as `every_state` are subject to `MAX_EFFECT_ITERATION`; the defines comment names loop effects only.
- `need_detection` meaning: the wiki says "?"; the state-building crash is a live-game observation recorded in this repository, not a documented rule.
- The `hoi4_map_rewrite` operation schema was not readable; no write operation was attempted.
- The wiki claims `add_building_construction` crashes on railways; this was not tested.
- Whether `every_owned_state` or `every_core_state` re-evaluates membership after a `transfer_state_to` inside the loop; the installed documentation only shows `transfer_state_to` inside `every_core_state` and does not describe the iteration order.
- Whether dated history blocks execute in file order or date order.
