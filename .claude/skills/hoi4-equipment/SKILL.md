---
name: hoi4-equipment
description: Use when creating, changing, or scripting Hearts of Iron IV equipment, including equipment archetypes and variants, equipment groups and categories, modular tank, ship, and aircraft designs, stockpile and production effects, lend-lease and licences, equipment bonuses, and the equipment designer and AI design files. Also use when an equipment type, module, or bonus silently does nothing.
---

# Hearts of Iron IV Equipment

Use this skill for anything under `common/units/equipment/`, `common/equipment_groups/`, `common/ai_equipment/`, the equipment designer interface, and every effect, trigger, or modifier that creates, moves, produces, or boosts equipment.
Sub-unit (battalion) definitions, division templates, and orders of battle belong to `hoi4-units-divisions`.
Technology that unlocks equipment, and doctrine rewards, belong to `hoi4-technology-doctrines`.
The idea or national spirit that carries an `equipment_bonus` belongs to `hoi4-ideas-modifiers`.
AI strategy tokens, `ai_will_do`, and role ratios belong to `hoi4-ai-strategies`.

In this skill `GAME` means the installed Hearts of Iron IV folder named in `CLAUDE.md` and `WIKI` means the repository folder `paradox_wiki`.
Installed documentation is more authoritative than the wiki.
Where they differ, this skill says so.

## Read the engine contract first

Gather the relevant sections through `hoi4.reference_context`, `hoi4.reference_search`, and `hoi4.reference_read`, and look up vanilla definitions through `hoi4.source_lookup`.
If a route fails once, retry once with narrower input, then read the local files directly.
Do not reproduce the files below from memory; read the section that bears on the change.

| Question | Read |
| --- | --- |
| Equipment definition fields, module slots, count limits, default modules | `GAME/common/units/equipment/_documentation.md` |
| Equipment categories used by bonuses | `GAME/common/script_enums.txt` (`script_enum_equipment_category`, `script_enum_equipment_bonus_type`, `script_enum_equipment_stat`) |
| Equipment groups | `GAME/common/equipment_groups/_documentation.md` |
| AI designs | `GAME/common/ai_equipment/_documentation.md`, `GAME/common/ai_equipment/generic_tank.txt` |
| Designer windows | `GAME/interface/equipmentdesigner/_documentation.info` |
| Icon and model pools | `GAME/gfx/interface/equipmentdesigner/graphic_db/_documentation.info` |
| Effects (`add_equipment_to_stockpile`, `create_equipment_variant`, and the rest) | `GAME/documentation/effects_documentation.md` |
| Triggers (`has_equipment`, `has_license`, and the rest) | `GAME/documentation/triggers_documentation.md` |
| Dynamic variables such as `num_equipment@type` | `GAME/documentation/dynamic_variables_documentation.md` |
| Modifiers (`equipment_conversion_speed`, licence modifiers, design cost factors) | `GAME/documentation/modifiers_documentation.md` |
| Defines (stockpile, licence, module XP costs) | `GAME/common/defines/00_defines.lua` |
| Concepts and legacy notes | `WIKI/Equipment modding - Hearts of Iron 4 Wiki.md`, `WIKI/Division modding - Hearts of Iron 4 Wiki.md` (equipment production), `WIKI/Country creation - Hearts of Iron 4 Wiki.md` (Variants) |

The detailed module, designer, and AI design material is in `references/modular-equipment-and-designer.md`.
The full effect, trigger, and dynamic variable catalogue is in `references/production-and-stockpile.md`.

## Decision table

| Goal | Mechanism |
| --- | --- |
| New non-modular equipment line (rifles, artillery, trucks) | Archetype plus numbered types in a new `common/units/equipment/*.txt`; unlock with a technology |
| New tank chassis, ship hull, or airframe | Modular archetype with `module_slots`, numbered chassis types, a designer window, and module definitions |
| Anti-air, artillery, or tank-destroyer variant of an existing chassis | `duplicate_archetypes` file evaluated after the base archetypes |
| Give a country a ready-made design | `create_equipment_variant` |
| Put finished equipment in a stockpile | `add_equipment_to_stockpile` |
| Start a production line | `add_equipment_production` |
| Permanent percentage boost to an equipment family | `equipment_bonus` in an idea, doctrine, or sub-doctrine; the `add_equipment_bonus` effect for a source that is not removed with its owner |
| Boost every variant a country designs from now on | `equipment_bonus` without `instant`, or `add_equipment_bonus` without `instant` |
| Make a bonus to existing equipment apply immediately | `instant = yes` inside the equipment entry |
| Let a country build another country's design | `create_production_license` |
| Move equipment between countries | `send_equipment`, `send_equipment_fraction`, or a purchase contract |
| Check how much equipment a country has | `has_equipment`, `stockpile_ratio`, or the `num_equipment@type` dynamic variable |
| Steer how the AI designs or builds | `common/ai_equipment` for designs; `hoi4-ai-strategies` for production strategies |

## Repository conventions that apply

- Indent with tabs, never use `<=` or `>=`, put tuning numbers in `common/script_constants/`, and reuse the project's dynamic scripted effects library (`common/scripted_effects/<prefix>_dynamic_effects.txt`, named in `CLAUDE.md`) before writing new dynamic helpers.
- Localisation is UTF-8 with BOM, keys have no `:0`, and player-facing text describes the current world, not history.
- Every new equipment type, archetype, or category that can be named in `equipment_bonus` or a military industrial organization must be added to `script_enum_equipment_bonus_type` in `common/script_enums.txt` in the same change.
  The repository file replaces the vanilla file of the same path, so it carries the vanilla list plus additions; after a game update, re-merge any new vanilla entries.
- A new concrete equipment type, sub-unit, special project, or doctrine must also follow the test-country registration rule in `CLAUDE.md` (package-owned idempotent setup effect and hidden-idea carrier).
- When a new mechanic is added, document it in a `docs/` markdown file with its icons and the `.gfx` file that references them.
- Read manpower through `manpower_k`, never the plain `manpower` variable, which overflows.

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
  Land stats are per unit of equipment, air stats are per aircraft, naval stats are per ship.
- The internal `type` values come from `_documentation.md`: land (`armor`, `infantry`, `motorized`, `mechanized`, `anti_air`, `artillery`, `anti_tank`, `rocket`, `support`), naval (`capital_ship`, `submarine`, `screen_ship`, `carrier`, `convoy`, `naval_transport`), air (`air_transport`, `fighter`, `cas`, `interceptor`, `tactical_bomber`, `strategic_bomber`, `naval_bomber`, `missile`, `suicide`).
  A list is allowed, as in `type = { armor anti_air }`.
  `ai_type` only changes which AI strategy bucket the equipment counts in.

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

## Categories, groups, and equipment bonuses

- Categories are the lowercase category words in `script_enum_equipment_category` (`armor`, `infantry`, `capital_ship`, `fighter`, and so on).
  Any category, archetype, or type that appears in `script_enum_equipment_bonus_type` can be the key of an `equipment_bonus` entry or of a military industrial organization equipment type.
- An equipment group collects types, archetypes, categories, and other groups under a name.
  Syntax: `GAME/common/equipment_groups/_documentation.md`.
  A group can be used as a bonus key.
- `equipment_bonus` appears in ideas, doctrine activation blocks, and the `add_equipment_bonus` effect:

```
equipment_bonus = {
	artillery = {
		instant = yes
		build_cost_ic = -0.2
	}
	infantry_equipment = {
		soft_attack = 0.1
	}
}
```

- Without `instant = yes` the bonus applies only to variants created afterwards, which is why a bonus can appear to do nothing on existing stock.
- Doctrines say to use `equipment_bonus` in the doctrine block instead of the `add_equipment_bonus` effect, because the effect does not remove the bonus when the doctrine is replaced.
- `add_equipment_bonus` takes `bonus = { type = { stat = value instant = yes } }` plus optional `name` (loc key), `prefix`, and `project` (a special project scope that supplies the display name).
- `add_design_template_bonus` gives a limited number of design discounts: `uses`, `cost_factor`, `equipment` (repeatable, at least one), `name`.
  `uses` and `cost_factor` accept a script constant.

## Variants, stockpile, production, and transfers

Full parameter lists and examples are in `references/production-and-stockpile.md`.
The rules that cause most mistakes:

- `create_equipment_variant` needs a `type` (not an archetype).
  Without `allow_without_tech = yes` the variant is created only when the technology for that type is researched.
  `modules` and `upgrades` are inherited from the parent when omitted.
  `parent_version` selects the parent, default 0.
  Ships and tanks need DLC-specific branches when a vanilla design is mirrored; vanilla history files wrap them in `if = { limit = { has_dlc = "..." } }`.
- `add_equipment_to_stockpile` accepts a type or an archetype, a negative `amount` removes, and `producer` restricts which stock is touched.
  `variant_name` is required when the equipment is modular and a variant must exist.
  The producer must have unlocked the equipment for the effect to succeed.
- `add_equipment_production` with a modular type needs `version_name` of an existing variant.
  `creator` is the owner of the design when it differs from the scope.
- `create_production_license` needs a non-archetype `type`, an optional `version`, and a `target` country.
- `send_equipment = { equipment = <type or archetype> amount = <n> target = <country> }` cannot send more than the scope holds; the target receives only what was removed.
- Reading amounts: `num_equipment@infantry_equipment` is a dynamic variable that can be compared with `check_variable`.
  `has_equipment = { type > 100 }` allows only `>` or `<`; do not assume how the boundary value counts, and use a dynamic variable when an exact comparison matters.
  `stockpile_ratio` compares stockpile to fielded and requires `>` or `<`.

## Sub-unit needs

A sub-unit lists the equipment it consumes in `need = { archetype_or_type = amount }` and `essential = { ... }` (`GAME/common/units/light_armor.txt`: `need = { light_tank_chassis = 60 }`).
A new equipment family is useless until a sub-unit names its archetype in `need`, and a sub-unit that is not `active = yes` must be unlocked by `enable_subunits` on a technology or `unlock_subunit`.
Design the sub-unit with `hoi4-units-divisions`.

## Localisation and graphics

- Equipment: `<type>`, `<type>_short`, `<type>_desc`; a country-specific name is `<TAG>_<type>` with the same suffixes.
  Vanilla: `GAME/localisation/english/equipment_l_english.yml`, `equip_air_l_english.yml`, `equip_naval_l_english.yml`.
- A technology without its own name borrows the name of the equipment it unlocks.
- Modules: `<module>`, `<module>_desc`, and optionally `<module>_short`; categories `EQ_MOD_CAT_<category>_TITLE`; slots `EQ_MOD_SLOT_<slot>_TITLE`.
  Vanilla: `tank_modules_l_english.yml`, `ship_modules_l_english.yml`.
- Icons: archetype pictures are sprites named `GFX_<picture>_medium` in an `interface/*.gfx` file (`GAME/interface/Technologies.gfx` holds `GFX_archetype_infantry_equipment_medium`).
  A type's icon is `GFX_<type>_medium`, with a country override `GFX_<TAG>_<type>_medium`.
  If a type has no own icon, it uses the icon of the technology that unlocks it.
  Module icons use `GFX_EMI_<module>` (`GAME/interface/tank_modules_icons.gfx`).
  Per-country icon and model pools for variants are set in `gfx/interface/equipmentdesigner/graphic_db/*.txt`.
- Register every sprite in a `.gfx` file before requesting art so the file name does not change later.

## New equipment line checklist

Work through these in one change; each item is a separate failure point.

1. Definition: archetype, numbered types with `archetype`, `parent`, `year`, `priority`, `visual_level`, and an unlock path (`active = yes` or a technology).
2. Enum: archetype and types added to `script_enum_equipment_bonus_type` (and `script_enum_equipment_category` only if a new category word is introduced).
3. Unlock: a technology with `enable_equipments`, and for modular lines `enable_equipment_modules` (see `hoi4-technology-doctrines`).
4. Consumer: a sub-unit whose `need` names the archetype, unlocked with `enable_subunits` or `active = yes` (see `hoi4-units-divisions`).
5. Modular only: modules, slot and category titles, designer windows, filters, and a default variant check.
6. Text and art: `<type>`, `_short`, `_desc` keys, archetype picture sprite, type sprites, and module sprites registered in `.gfx`.
7. Stock and production entry points: a scripted way to grant or build it, using the effects above, with `variant_name` or `version_name` for modular lines.
8. AI: a design group for modular lines and, where relevant, production strategy tokens (see `hoi4-ai-strategies`).
9. Docs and tests: the mechanic document, any test-country or debug setup the project uses, and the dynamic-effects documentation if a helper was added.

## Common mistakes and silent failures

- Equipment appears in the bonus list but the bonus does nothing: the type is missing from `script_enum_equipment_bonus_type`, or `instant = yes` is missing and no new variant has been designed.
  The enum file comment says a startup log error reminds you to update it.
- Equipment cannot be built: no `active = yes` and no technology `enable_equipments`, or `can_be_produced` is false for that country.
- `add_equipment_to_stockpile` of a modular type does nothing: no `variant_name`, no matching variant, or the producer has not unlocked the type.
- A new airframe or chassis never shows in the designer: the designer window or, for airframes, the entry in `GAME/interface/equipmentdesigner/planes/plane_blueprints_generic.gui` is missing (vanilla comment at the top of `plane_airframes.txt`).
- A module appears to be missing from a slot: the module `category` is not in the slot's `allowed_module_categories`, a `forbid_*` rule excludes it, or the module technology is not researched.
- Gun modules that need a turret fail: the turret slot is defined after the gun slot.
  Vanilla notes that dependent slots must be defined in operational order for the AI and historical templates.
- Mixing type and archetype: `create_equipment_variant.type` and `create_production_license.equipment.type` need a type; stockpile effects and bonuses accept either.
- A bonus or modifier is silently ignored when it names a stat the equipment does not carry; check the stat list, and remember that stats on the battalion (for example `recon`) cannot be used by military industrial organizations.
- Removing stock with `set_equipment_fraction` models a loss; do not use it to split stockpiles in a civil war because `start_civil_war` already divides them (Effects wiki).
- Deleted stockpiled equipment moves to a hidden pool for `NUM_DAYS_TO_FULLY_DELETE_STOCKPILED_EQUIPMENT` days and can still be seized; do not assume instant erasure.

## Validation

- Read back the definition through `hoi4.source_lookup` and confirm archetype, parent chain, `year`, unlock, and enum registration.
- For a technology that unlocks the equipment, run `hoi4.tech_inspect` in `unlocks` mode with the technology id and confirm the equipment appears; see `hoi4-technology-doctrines`.
- Run `hoi4.script_validate` on the effect or trigger bodies that touch equipment, with `kind` and `scope = country`.
  A passing result covers only the listed checks; argument semantics and engine behaviour stay unverified.
- Check that every key in a new localisation set exists for the type, `_short`, and `_desc`, and that every sprite name resolves.
- State what was not verified: designer layout, module availability, and live production behaviour need the game.
