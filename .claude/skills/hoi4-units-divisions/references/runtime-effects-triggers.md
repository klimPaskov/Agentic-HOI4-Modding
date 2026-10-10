# Runtime Unit Effects and Triggers

Read this when scripting divisions, templates, manpower or fleets during play (events, decisions, focuses, scripted effects).
Every signature below is from installed `documentation/effects_documentation.md` or `documentation/triggers_documentation.md` (search the `## <name>` heading), with vanilla call sites named for mirroring.
Scope abbreviations: COUNTRY, STATE, DIVISION (the scope entered by the division iterators), CHARACTER, any.

## Creating units

- `create_unit` (scope any, `owner` is required): spawns divisions like an OOB `division = {}` block. Vanilla: `common/decisions/AUS.txt`.

```text
create_unit = {
	division = "name = \"3. Example Division\" division_template = \"Example Division\" start_experience_factor = 0.6"
	owner = PREV
	prioritize_location = 12406
	allow_spawning_on_enemy_provs = no
	country_score = { base = 100 modifier = { tag = TAG add = 100 } }
	count = 1
	id = 42
	divisional_commander_xp = 4
}
```

  The `division` value is a string holding OOB division keys (escape inner quotes). `prioritize_location` is a province id. `country_score` scores which provinces to prefer (owned first, friendly second by default). `id` lets `delete_unit` target the unit later. No tooltip is generated.
- `division_template = { ... }` (COUNTRY): adds a template. Same body as in an OOB. No tooltip.
- `create_colonial_division_template = { subject = TAG division_template = { ... } }` (COUNTRY, overlord).
- `load_oob = "file"` (COUNTRY): loads an OOB immediately; see the loading caveats in `SKILL.md`.
- `create_ship = { type = ship_hull_submarine_1 equipment_variant = "S Class" creator = ENG name = "..." amount = 5 }` (COUNTRY): adds ships to the reserve fleet; `creator` and `name` optional.
- `unlock_subunit = id` (COUNTRY): unlocks a sub-unit for the country.
- `add_equipment_production`, `add_equipment_to_stockpile`, `create_equipment_variant`: equipment-side, documented in the equipment sources.

## Editing templates

- `add_units_to_division_template = { template_name = "..." regiments = { infantry = 0 cavalry = 2 } support = { military_police = 0 } regimental_support = { field_guns = 0 } }` (COUNTRY, or DIVISION without `template_name`): the number is the column `x`; the unit goes into the first free slot of that column. Adds only.
- `change_division_template = "Name"` (DIVISION): moves the division to another existing template.
- `set_division_template_lock = { division_template = "..." is_locked = yes }`, `set_division_template_cap = { division_template = "..." division_cap = 12 }`, `clear_division_template_cap = { division_template = "..." }`, `set_division_force_allow_recruiting = { division_template = "..." force_allow_recruiting = yes }` (COUNTRY).
- `country_lock_all_division_template = yes` or `{ is_locked = yes desc = LOC_KEY }` (COUNTRY): country-level lock with a reason key; the per-template lock effect cannot undo it.
- `delete_unit_template_and_units = { division_template = "..." disband = no }` (COUNTRY): removes the template and its divisions; `disband = yes` refunds equipment and manpower.

## Removing, moving and damaging units

- `delete_unit = { division_template = "..." id = 42 state = 64 disband = yes }` (COUNTRY): filters are optional; default `disband = no` (no refund). No tooltip.
- `delete_units = { division_template = "..." disband = no }` (COUNTRY).
- `destroy_unit = yes` (DIVISION): destroys the scoped division.
- `destroy_ships = { type = light_cruiser count = all }` (COUNTRY): count may be a number.
- `damage_units = { province = 42 state = 5 region = 5 limit = { always = yes } damage = 0.5 org_damage = 0.5 str_damage = 0.5 ratio = yes template = "name" army = yes navy = yes }` (any scope): location filters are optional; `ratio = yes` treats damage as a ratio of maximum. No tooltip.
- `set_unit_organization = 0.5` (DIVISION): sets organisation to current times the value (0 to 1).
- `transfer_units_fraction = { target = ROOT size = 0.4 stockpile_ratio = 0.3 army_ratio = 0.1 navy_ratio = 0.2 air_ratio = 0.4 keep_unit_leaders = { 700 701 } keep_unit_leaders_trigger = { ... } }` (COUNTRY): moves a fraction of army, navy, air, stockpile and unit leaders. In the leaders trigger THIS is the leader, ROOT the recipient and FROM the sender.
- `transfer_navy = { target = TAG is_government_in_exile = no }` and `transfer_ship = { prefer_name = "..." type = ... target = TAG exclude_refitting = yes }` (COUNTRY).

## Division-scope effects

Entered through `every_country_division`, `random_country_division`, `every_state_division`, `random_state_division` (optional keys: `limit`, `tooltip`, `random_select_amount`, `display_individual_scopes`).
Division scope accepts: `change_division_template`, `add_units_to_division_template`, `destroy_unit`, `set_unit_organization`, `add_divisional_commander_xp = N`, `promote_officer_to_general = yes`, `add_history_entry = { key = loc_key subject = "text" allow = yes }`, `add_unit_medal_to_latest_entry = { unit_medals = key }`, `reseed_division_commander` (debug and testing effect), and `add_random_valid_trait_from_unit = FROM` (for use only with the unit as ROOT and a character target).

## Country-scope bonuses

- `add_unit_bonus = { <sub_unit or category> = { <stat> = value name = LOC_KEY } }`: permanent sub-unit or category bonus.
- `add_manpower = N` (COUNTRY or STATE).
- `add_dynamic_modifier = { modifier = name days = N scope = TAG }` for variable-driven modifiers.

## Triggers

Country scope: `has_template = "Name"`, `has_template_majority_unit = id`, `has_template_containing_unit = id`, `num_divisions` (divisions controlled; use `has_army_size` when strength matters), `has_army_size = { size > N type = infantry }` (type optional; majority-battalion divisions count; size needs `>` or `<`), `has_army_manpower = { size > N }`, `num_divisions_in_states = { count > N states = { ... } types = { ... } exclude = { ... } }`, `divisions_in_state = { state = 64 size > 3 type = infantry unit = light_tank }`, `divisions_in_border_state`, `any_country_division = { ... }`, `has_manpower > N`, `manpower_k`, `max_manpower_k`, `max_available_manpower_k`, `deployed_army_manpower_k`, `amount_manpower_in_deployment_queue`, `foreign_manpower`, `ai_has_role_template`, `ai_has_role_division`, `ai_wants_divisions`.
State scope: `any_state_division = { ... }`, `army_manpower_in_state`.
Division scope: `division_has_majority_template = id`, `division_has_battalion_in_template = id`, `has_officer_name = key`, `is_unit_template_reserves = yes`, `unit_strength < 1`, `unit_organization < 1`, `owner = { ... }` to reach the country.
Combatant scope (inside combat-evaluated trait and tactic triggers only): `has_unit_type`, `has_reserves`, `skill`, `phase`, `is_attacker`, `is_defender`, `dig_in`, and the others listed under `COMBATANT` in the triggers documentation.

## Iterating safely

- `every_country_division` and `any_country_division` need a bounded country scope. Do not nest them under an all-countries iterator in a periodic hook without permission.
- `random_select_amount` selects a bounded number of divisions.
- `while_loop_effect` and `for_loop_effect` stop after 1,000 iterations; unit loops over very large armies should rely on the scope iterators.
- Show a tooltip with `custom_effect_tooltip` and run the silent effects in `hidden_effect` so the player sees the cost of divisions removed or spawned.
