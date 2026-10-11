# Production, stockpile, licences, and equipment script catalogue

Read this file when you write an effect, trigger, or modifier that creates, produces, moves, licenses, or counts equipment.
`GAME` is the installed Hearts of Iron IV folder named in `CLAUDE.md`.
Every parameter list below was read from `GAME/documentation/effects_documentation.md` or `triggers_documentation.md`; the section name is the effect or trigger name.

## Effects (country scope unless stated)

### create_equipment_variant

```
create_equipment_variant = {
	name = "Yorktown Class"			# optional
	name_group = USA_CV_HISTORICAL		# optional, ships only; inherits the parent's group
	type = ship_hull_carrier_1			# a type, never an archetype
	allow_without_tech = yes			# default no: otherwise created when the type's research completes
	parent_version = 3				# default 0; falls back to the default variant
	obsolete = yes					# default no
	mark_older_equipment_obsolete = yes	# default no; same archetype, niche, and mission set (planes)
	show_position = no				# wiki: removes the version suffix from the name
	role_icon_index = 3				# ships only; default auto; 0 unsets
	upgrades = { ship_deckspace_upgrade = 1 }	# inherited from the parent when omitted
	modules = {
		fixed_ship_engine_slot = carrier_ship_engine_2
		fixed_ship_secondaries_slot = empty	# clears an inherited module
	}
	model = "GER_light_armor_2_entity"		# optional entity name
	icon = "GFX_GER_basic_light_tank_medium"	# optional sprite name or a texture path
	design_team = mio:my_mio_token		# optional military industrial organization
}
```

- Vanilla precedent for history files: `GAME/history/countries/GER - Germany.txt` (search `create_equipment_variant`).
  It uses `if = { limit = { has_dlc = "No Step Back" } ... }` branches because ship, tank, and airplane designs differ with and without DLC.
- A non-modular type (pre-designer) takes `upgrades` only; a modular type takes `modules` and `upgrades`.
- The module slot names in `modules` come from the type's archetype in `common/units/equipment/`; the module names come from `common/units/equipment/modules/`.
- Whether a module the country has not unlocked is applied is not stated in the documentation; unlock the modules first with `set_technology`, and check the variant in the designer view.

### Stockpile and production

| Effect | Parameters read from the documentation |
| --- | --- |
| `add_equipment_to_stockpile` | `type` (type or archetype), `amount` (value or variable, negative removes), `producer` (optional tag; when removing, only that producer's stock), `variant_name` (wiki: required if a variant must be created) |
| `add_equipment_production` | `equipment = { type creator version_name }`, optional `name`, `requested_factories`, `progress`, `efficiency`, `amount` (value or variable), `industrial_manufacturer = mio:token` |
| `set_equipment_fraction` | A fraction in 0 to 1 (wiki: the fraction removed); reduces the whole stockpile |
| `set_equipment_version_number` | `type`, `version`; the next variant of that type gets version `N + 1`; no tooltip |
| `add_equipment_subsidy` | `cic`, `equipment_type` (archetype), and either `seller_tags = { ... }` or `seller_trigger` (mutually exclusive; in the scripted trigger `ROOT` has the subsidy and `FROM` is the seller) |
| `add_cic` | Wiki: economic capacity for the international market; a negative total caps at 0 |
| `add_design_template_bonus` | `uses`, `cost_factor` (both accept a script constant), `equipment` (repeatable, one required), `name` |
| `add_equipment_bonus` | `bonus = { <type or archetype or category> = { <stat> = <value> instant = yes } }`, optional `name`, `prefix`, `project` |
| `create_production_license` | `target`, `cost_factor`, `new_prioritised` (default yes; ignores `version` but not `version_name`), `equipment = { type version version_name }` |
| `create_purchase_contract` | Any scope; `seller`, `buyer`, `civilian_factories`, one or more `equipment = { type amount }` |
| `cancel_purchase_contract` | `PURCHASE_CONTRACT` scope only; used as `contract = { cancel_purchase_contract = yes }` |
| `send_equipment` | `equipment` (vanilla `GAME/common/decisions/AST.txt` uses this key; the wiki table says `type` but its own example also uses `equipment`), `amount`, `target`; wiki: the scope loses what the target receives and cannot go negative |
| `send_equipment_fraction` | `target`, `value` in 0 to 1 (clamped) |
| `create_ship` | `type`, `equipment_variant`, `creator` (default scope), `name`, `amount`; the ship joins the reserve fleet |
| `create_railway_gun` | Any scope; `equipment`, `name`, `location` (province; default capital) |
| `unlock_subunit` | A sub-unit key; also available through `enable_subunits` on a technology |
| `delete_unit` / `delete_units` | Filter by `division_template`, `id`, `state`; `disband = yes` refunds equipment and manpower |
| `create_unit` | Any scope; used for spawning divisions, covered by `hoi4-units-divisions` |
| `load_oob` | Loads an order of battle file; covered by `hoi4-units-divisions` |

Starting production in an order of battle uses the same syntax inside an `instant_effect = { add_equipment_production = { ... } }` block (`WIKI/Division modding - Hearts of Iron 4 Wiki.md`, Equipment production).
Division entries accept `force_equipment_variants`, `start_equipment_factor`, and `start_manpower_factor` as documented in the same page.

Meta effects can make the type name dynamic (`type = [EQ_TYPE]_[EQ_LEVEL]`); use `meta_effect` because `type` does not accept variables.
`amount` does accept a variable.

## Triggers (country scope unless stated)

| Trigger | Use |
| --- | --- |
| `has_equipment = { <type> > <n> }` | Only `>` and `<` are allowed; `<n>` may be a variable |
| `stockpile_ratio = { archetype = <a> ratio > <r> }` | Stockpile to fielded; for convoys use a plain count |
| `has_design_based_on = <archetype>` | A buildable non-obsolete design exists |
| `has_license = { from = <TAG> archetype = <a> }` or `equipment = { type version }` | Archetype and equipment are mutually exclusive |
| `is_licensing_to = { target = <TAG> archetype = <a> }` | Same shape as `has_license` |
| `has_any_license`, `is_licensing_any_to`, `is_lend_leasing` | Existence checks |
| `has_tech`, `can_research`, `is_researching_technology` | Unlock checks that gate equipment (see `hoi4-technology-doctrines`) |
| `contract_contains_equipment = <category, archetype, or type>` | `PURCHASE_CONTRACT` scope |
| `buyer`, `seller`, `deal_completion` | `PURCHASE_CONTRACT` scope; the installed example spells the last one `deal_completition`, but the trigger name is `deal_completion` |
| `has_mio_equipment_type` | `INDUSTRIAL_ORG` scope; accepts values from `script_enum_equipment_bonus_type` and `common/equipment_groups` |
| `has_fuel`, `fuel_ratio` | Fuel amount and ratio, `>` or `<` only |

## Dynamic variables (read in `check_variable` and triggers)

- `num_equipment@<type>`: equipment in the country.
- `num_equipment_in_armies@<type>` and `num_equipment_in_armies_k@<type>`: equipment fielded, plain and in thousands.
- `num_target_equipment_in_armies@<type>` and `_k`: equipment the armies need.
- `total_equipment_produced_<category>`: lifetime production per category, for example `total_equipment_produced_armor`.
- `num_deployed_planes_with_type@<type>`, `num_ships_with_type@<type>`, `num_of_military_factories`, `num_of_naval_factories`, `num_of_available_military_factories`.
- The `@` suffix takes an equipment token; the descriptions are in `GAME/documentation/dynamic_variables_documentation.md` under each name.

## Modifiers that affect equipment

Names read from `GAME/documentation/modifiers_documentation.md`.

- Costs and speed: `equipment_conversion_speed`, `refit_ic_cost`, `refit_speed`, `line_change_production_efficiency_factor`, `production_factory_max_efficiency_factor`, `production_factory_efficiency_gain_factor`, `production_factory_start_efficiency_factor`, `production_lack_of_resource_penalty_factor`.
- Upgrade XP: `equipment_upgrade_xp_cost`, `land_equipment_upgrade_xp_cost`, `air_equipment_upgrade_xp_cost`, `naval_equipment_upgrade_xp_cost`.
- Capture and loss: `equipment_capture`, `equipment_capture_factor` and their `_for_controller` forms.
- Licences: `license_purchase_cost`, `license_production_speed`, `license_tech_difference_speed`, and per-family forms such as `license_infantry_eq_cost_factor` and `license_armor_purchase_cost`.
- Lend-lease: `lend_lease_tension`, `lend_lease_tension_with_overlord`.
- Dynamic families: `<Equipment>_design_cost_factor`, `module_<EquipmentModule>_design_cost_factor`, `unit_<Unit>_design_cost_factor`, and for naval `production_cost_max_<NavalEquipment>`; the list of valid suffixes sits under each name.
- Per-equipment stat boosts use `equipment_bonus`, not a modifier.

## Defines that change equipment behaviour

From `GAME/common/defines/00_defines.lua`: `MAX_EQUIPMENT_RESOURCES_NEED`, `NUM_DAYS_TO_FULLY_DELETE_STOCKPILED_EQUIPMENT`, `EQUIPMENT_BASE_LEND_LEASE_WEIGHT`, `LEND_LEASE_DELIVERY_TOTAL_DAYS`, `ANNEX_STOCKPILES_RATIO`, `CAPITULATE_STOCKPILES_RATIO`, the `LICENSE_*` values, `CONVERSION_SPEED_BONUS`, and the `EQUIPMENT_MODULE_*_XP_COST` values.
Override defines with a small file that lists only the changed keys, never a copy of the vanilla file (wiki Technology modding, References).

## Production conversion, lend-lease, and licences

- `is_convertable = yes` on an archetype and `can_convert_from` on a module declare what can be converted cheaply.
  The wiki lists `is_convertable` and `can_license` as equipment fields; the installed `_documentation.md` does not describe them, so copy their use from a vanilla archetype of the same family.
- Lend-lease space is the equipment `lend_lease_cost`, and `can_be_lend_leased` on the archetype gates who may receive it.
- A licence lets another country produce a specific type or archetype from the licensor's design.
  Pricing and speed come from the `LICENSE_*` defines and the licence modifiers.
- A purchase contract is a market trade of equipment for civilian factories; read the scope documentation for its triggers and the single cancel effect.

## Military industrial organizations and special projects

Equipment designers and manufacturers can be attached through military industrial organizations (`common/military_industrial_organization/`) and the `industrial_manufacturer` and `design_team` parameters above.
Equipment types usable there are those in `script_enum_equipment_bonus_type`, and stats usable there come from `script_enum_equipment_stat`.
The enum file notes which stats live on the battalion and cannot be used by these organizations.
Special project prototypes are covered by `GAME/common/special_projects/special_projects_documentation.md`; this skill only notes that prototype rewards can place equipment in a stockpile.

## Local checks for this surface

- `hoi4.script_validate` with `kind = effect`, `scope = country` on the body before use.
- `hoi4.source_lookup` with `symbol` set to the equipment type to confirm it resolves, and `kind` omitted to list usages.
- A single hand calculation of a before and after stockpile for a negative `amount` with and without `producer`, since the removal rule differs.
