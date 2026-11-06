# HOI4 Map and States: Runtime state effects

Part of the [hoi4-map-states](../SKILL.md) skill. Read before scripting ownership, control, building, resource, modifier or occupation changes on a state during play.

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
- `should_initiate_resistance` runs in state scope with `FROM` as the occupier, so write `FROM = { tag = X }`. [vanilla-confirmed 1.19.3]
- An occupation law `visible` block is evaluated with `FROM` set in 10 of 15 vanilla blocks despite the header comment, and `main_fallback_law` is unused in vanilla and absent from `hoi4.exe`, which use `default_law` and `starting_law`. [vanilla-confirmed 1.19.4.1]
- The resistance modifier header comment misspells `icon_small` and `core_compliancemodifier`, where vanilla uses `small_icon` and `core_compliance_modifier`. [vanilla-confirmed 1.19.4.1]

