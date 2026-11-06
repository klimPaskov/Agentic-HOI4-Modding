# HOI4 Map and States: State flags, victory points and map modes

Part of the [hoi4-map-states](../SKILL.md) skill. Read before using state flags or variables, victory points, resources, supply, railways or scripted map modes at runtime.

## Flags, variables, and modifiers on states

- State flags are 32-bit integers scoped to one state. `set_state_flag = my_flag` sets 1; the block form is `set_state_flag = { flag = my_flag value = 3 days = 50 }`; `modify_state_flag = { flag = x value = N }` changes an existing flag only; `has_state_flag` tests presence, and its block form tests value and age. Flags have no definition file.
- A flag name can carry a targeted suffix (`my_flag_@PREV` appends the scope's tag); only `@ROOT`, `@PREV`, `@FROM`, `@THIS` are supported, one per name.
- State variables: `set_variable`, `add_to_variable`, and friends executed in state scope write that state's variable. Read another state's variable with a numeric prefix (`123.my_var`), a stored scope (`var:target_state.my_var`), or a chain (`province_controllers^1234:capital:my_var`) per `WIKI/data_structures.md`. Temporary variables have no scope.
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
- No effect switches the player's map mode, and the `on_map_mode` key in decisions is unrelated to scripted map modes. [vanilla-confirmed 1.19.4.1]
- Map-facing sprites and entities: building icon strip `GFX_buildings_strip` in `interface/countrystateview.gfx`; building models are entities named `building_<id>` in `gfx/entities/*.asset`; terrain and border textures are in `GAME/map/terrain/`.

