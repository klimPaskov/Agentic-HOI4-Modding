# HOI4 Map and States: State triggers and iteration

Part of the [hoi4-map-states](../SKILL.md) skill. Read before writing triggers on states, iterating a set of states, or sweeping states with a loop.

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
- A bare `any_of` over an array leaves the current element in `v`, which vanilla reads as `var:v`, while the documentation names only `value` and `index`. [vanilla-confirmed 1.19.4.1]
- Collections: `collection_size = { input = game:all_states value > 42 }` and operators such as `owned_states` and `controlled_states` (`script_collection_input.md`, `script_collection_operator.md`). Collections may contain duplicates.
- The key that carries the collection differs per consumer: `collection_size` takes `input =`, other collection triggers take `collection =`, and some consumers take `named_collection =`. [docs] [vanilla-confirmed 1.19.4.1]
- Inside `operators` the filter key is `limit`, not the `trigger` shown in the operator documentation example (194 of 194 vanilla filters use `limit`). [vanilla-confirmed 1.19.4.1]
- `faction_members` is empty for a country that has no faction, so use `country_and_all_subjects` to mean a country and its subjects. [docs]
- `any_state_of` accepts a literal id list or a script constant as its `target` (documented with a country-group constant example).

Loop cap: `GAME/common/defines/00_defines.lua` sets `MAX_EFFECT_ITERATION = 1000` ("maximum allowed iteration for loop effects"). Vanilla has 1,081 states, so `for_loop_effect` or `while_loop_effect` over state ids from 1 to the last id stops before finishing. Use a scope iterator for sweeps, or batch the ids across several runs with a stored cursor. The defines comment names loop effects only; no cap is documented for scope iterators.

Whole-world iteration (`every_state`, `every_country`, and any `on_daily`, `on_weekly`, `on_monthly` that fans out over all countries) is expensive. In this repository it needs explicit permission; narrow the scope to the owner, an array, or a tag-specific on action.

