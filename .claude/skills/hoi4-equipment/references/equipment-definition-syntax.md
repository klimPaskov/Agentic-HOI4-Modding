# Hearts of Iron IV Equipment: Equipment definition syntax

Part of the [hoi4-equipment](../SKILL.md) skill. Read before writing or changing an equipment archetype, numbered type, upgrade chain, modular chassis, hull or airframe, or duplicated archetype.

## Equipment definitions

### Non-modular archetype and types

Vanilla precedent: `GAME/common/units/equipment/infantry.txt`.

```
equipments = {
	my_equipment = {					# archetype: shared stats, never built directly
		year = 1936
		is_archetype = yes
		is_buildable = no
		picture = archetype_my_equipment	# sprite GFX_archetype_my_equipment_medium
		type = infantry					# internal type, see below
		group_by = archetype
		interface_category = interface_category_land
		active = yes					# usable without a technology unlock
		reliability = 0.9
		maximum_speed = 4
		defense = 20
		breakthrough = 2
		soft_attack = 3
		hard_attack = 0.5
		ap_attack = 1
		lend_lease_cost = 1				# convoy space
		build_cost_ic = 0.43
		resources = { steel = 2 }
	}
	my_equipment_0 = {
		year = 1918
		archetype = my_equipment
		active = yes
		priority = 05
		visual_level = 0
	}
	my_equipment_1 = {
		year = 1936
		archetype = my_equipment
		parent = my_equipment_0			# the type it supersedes
		priority = 10
		visual_level = 1
		soft_attack = 6
		build_cost_ic = 0.50
	}
}
```

Rules that follow from `_documentation.md` and vanilla:

- `is_archetype = yes` and `archetype =` are mutually exclusive.
  A type inherits every stat from its archetype and overrides only what it lists.
- `parent` names the previous version and cannot name an archetype.
- `year` is the earliest year the equipment appears; `priority` decides which type is used first; `visual_level` orders images in the production screen.
- `active = yes` makes the equipment available without a technology.
  Otherwise a technology must list it in `enable_equipments`.
  Equipment that no technology unlocks and that is not `active` can never be built.
- `can_be_produced = { ... }` (country scope) and `can_be_lend_leased = { ... }` (country scope, `FROM` is the receiver) gate production and lend-lease.
  Vanilla puts them on the archetype.
- `max_military_factories` and `max_dockyard_factories` cap factories per line.
- `resources` is limited to three different strategic resources per equipment (`MAX_EQUIPMENT_RESOURCES_NEED` in `GAME/common/defines/00_defines.lua`).
- Stats are limited to the names the engine knows; the list is in `script_enum_equipment_stat` and in the Equipment modding wiki Stats section.
  `fire_range`, `shore_bombardment`, `port_capacity_usage` and `evasion` are not equipment stats in 1.19.4.1. [vanilla-confirmed 1.19.4.1]
  Land stats are per unit of equipment, air stats are per aircraft, naval stats are per ship.
- The internal `type` values are the 38 entries of `script_enum_equipment_category` in `common/script_enums.txt` [vanilla-confirmed 1.19.3], which `_documentation.md` describes: land (`armor`, `infantry`, `motorized`, `mechanized`, `anti_air`, `artillery`, `anti_tank`, `rocket`, `support`), naval (`capital_ship`, `submarine`, `screen_ship`, `carrier`, `convoy`; its `naval_transport` is in neither the enum nor vanilla), air (`air_transport`, `fighter`, `cas`, `interceptor`, `tactical_bomber`, `strategic_bomber`, `naval_bomber`, `missile`, `suicide`).
  A list is allowed, as in `type = { armor anti_air }`.
  `ai_type` only changes which AI strategy bucket the equipment counts in.
  `strat_bomber`, `support_equipment` and the `*_tank_chassis` names are not equipment types. [vanilla-confirmed 1.19.4.1]

### Non-modular upgrade chains

Equipment without a designer uses `upgrades = { ... }` on the archetype, defined in `GAME/common/units/equipment/upgrades/*.txt` with `max_level`, `cost = land|air|naval`, per-level stat changes, and optional `level_requirements` tied to technologies.
Vanilla precedent: `GAME/common/units/equipment/upgrades/land_upgrades.txt` (`tank_nsb_engine_upgrade` shows `linear_cost`, `level_requirements`, `resource_cost_thresholds`, and `add_stats`).
A variant records upgrade levels through `create_equipment_variant { upgrades = { ... } }`.

### Modular chassis, hulls, and airframes

Tanks, ships, and aircraft are modular.
The archetype declares `module_slots`, `module_count_limit`, and `default_modules`.
Each numbered type has `module_slots = inherit`, a `parent`, and its own base stats.
Vanilla precedent: `GAME/common/units/equipment/tank_chassis.txt` (`light_tank_chassis` and `light_tank_chassis_0` to `_3`), `ship_hull_light.txt`, `plane_airframes.txt`.

```
my_chassis = {
	year = 1922
	is_archetype = yes
	is_buildable = no
	picture = archetype_my_chassis
	type = armor
	group_by = archetype
	interface_category = interface_category_armor
	priority = 2000
	module_slots = {
		turret_type_slot = {			# define a turret slot before any gun slot that depends on it
			required = yes
			allowed_module_categories = { tank_light_turret_type }
		}
		main_armament_slot = {
			required = yes
			allowed_module_categories = { tank_small_main_armament }
		}
		special_type_slot_1 = {
			required = no
			allowed_module_categories = { tank_special_module tank_radio_module }
		}
	}
	module_count_limit = { category = tank_radio_module count < 2 }
	default_modules = {
		turret_type_slot = tank_light_one_man_tank_turret
		main_armament_slot = empty
	}
	maximum_speed = 4
	build_cost_ic = 2
	reliability = 0.8
	armor_value = 10
	resources = { steel = 1 }
	lend_lease_cost = 10
	manpower = 2
}
my_chassis_0 = {
	abbreviation = "mc0"
	derived_variant_name = my_equipment_0	# name of the generated default variant
	visual_level = 0
	year = 1922
	archetype = my_chassis
	priority = 2000
	module_slots = inherit
}
```

Facts about modular definitions:

- Slot names starting with `fixed_` are grouped together in the designer; custom slots cannot start with `fixed_`.
  A slot may be `= <earlier slot>` or `= inherit`.
- `module_count_limit` accepts `module`, `category`, `any`, or `empty` as the match, and `count <`, `count >`, `count =`, or `count = any`.
  Inherited limits are overridden only by a limit with exactly the same match.
- Vanilla gives every modular archetype `default_modules` (tank, hull, and airframe files alike), and a slot may be set to `empty`.
  Mirror that, because the default variant is built from it.
- A modular type has no usable look in the designer until a window named after the type or archetype exists; see `references/modular-equipment-and-designer.md`.
- Modules are defined in `GAME/common/units/equipment/modules/` and unlocked by `enable_equipment_modules` on a technology.

### Duplicated archetypes (specialised chassis variants)

`GAME/common/units/equipment/x_tank_chassis.txt` and `x_plane_airframes.txt` use a `duplicate_archetypes` block (the plane file also sets `picture` and a `variant_name` rule per duplicate).
The file must be evaluated after the files that define the archetypes being duplicated.
`alias`, `type`, `variant_name`, and `derived_variant_name` are not duplicated.

```
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

The wiki says every generated variant name (`<name>`, `<name>_0`, `<name>_1`, and so on) must also be listed in the script enums.
A module that is meant to allow the new type uses `allow_equipment_type = anti_air`, and that type must be used by at least one sub-unit.
Register the generated names in `script_enum_equipment_bonus_type`.
Search filters for the designer list live in `tank_filters.txt` and `plane_filters.txt`.

