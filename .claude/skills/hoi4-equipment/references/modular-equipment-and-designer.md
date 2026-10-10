# Modules, the designer, graphics, and AI designs

Read this file when you add or change modules, slots, a designer window, an icon or model pool, or an AI design group.
`GAME` is the installed Hearts of Iron IV folder named in `CLAUDE.md`.
Vanilla precedents named here were read for this skill; open the cited file before copying a field.

## Module files

Location: `GAME/common/units/equipment/modules/00_tank_modules.txt`, `00_ship_modules.txt`, `00_plane_modules.txt`.
Each file wraps its modules in `equipment_modules = { limit = { has_dlc = "..." } ... }`.
Copy that wrapper shape for a new file; the DLC `limit` is a vanilla gate, not something a module needs for its own definition.

Header comments in the vanilla files give historical equivalence tables and the rule "do not give countries modules they do not have the technology for".
Read them before naming a new module.

### Fields seen in vanilla modules

| Field | Meaning | Seen in |
| --- | --- | --- |
| `abbreviation = "gas"` | Short label shown in lists | all |
| `category = tank_engine_type` | The module category; a slot accepts it through `allowed_module_categories` | all |
| `gui_category = ship_light_battery` | Groups several categories in one designer column | ship, plane |
| `sfx = sfx_ui_sd_module_engine` | Click sound | all |
| `gfx = ship_heavy_battery_5` | Visual set used when the module is shown (ship modules); designer windows also search `MODULE_NAME`, `MODULE_GFX_NAME`, `MODULE_CATEGORY_NAME`, `MODULE_SLOT_NAME` in that order | ship |
| `add_stats = { ... }` | Flat stat changes added to the chassis | all |
| `multiply_stats = { ... }` | Factor changes, for example `naval_speed = -0.08` | all |
| `add_average_stats = { ... }` | Ship stats averaged over the modules of that kind (for example `lg_armor_piercing`) | ship |
| `xp_cost = 1` | Experience cost to design with it | tank, plane |
| `dismantle_cost_ic`, `dismantle_cost_resources` | Cost to remove it | all |
| `build_cost_resources = { steel = 2 }` | Extra strategic resources | all |
| `parent = other_module` | The module it supersedes | all |
| `can_convert_from = { module = x convert_cost_ic = n }` or `{ module_category = c convert_cost_ic = n }` | Cheaper replacement path | all |
| `allowed_module_categories = { slot = { category } }` | Which categories another slot can take once this module is installed (a turret limits the gun categories) | tank |
| `forbid_module_categories = { ... }` | Categories that cannot coexist with this module | ship |
| `allow_equipment_type`, `forbid_equipment_type`, `forbid_equipment_type_exact_match`, `forbid_equipment_type_exact_match_for_category` | Restrict by the chassis internal type | tank |
| `add_equipment_type = { fighter heavy_fighter }` | Makes the airframe count as these types when the module is fitted | plane |
| `allow_mission_type = { air_superiority interception }` | Missions this module unlocks | plane |
| `mission_type_stats = { limit = { interception } multiply_stats = { ... } }` | Per-mission stat changes | plane |
| `critical_parts = { damaged_light_guns }` | Parts that can be damaged in naval combat, defined in `GAME/common/units/critical_parts/00_critical_parts.txt` | ship |

Stat names are from `script_enum_equipment_stat` and the Equipment modding wiki Stats section.
Aircraft modules use `thrust` and `weight`; the formula for agility from thrust and weight is controlled by `THRUST_WEIGHT_AGILITY_FACTOR` in the defines.

### Rules that cause silent failures

- A module has no effect on a slot that does not list its category.
- A module that no technology lists in `enable_equipment_modules` is always selectable (wiki Technology modding, Enabling objects).
  If it should be gated, a technology must list it, and that technology must be researchable or granted.
- A "greater than" or "less than" module requirement in an AI design uses the year order inside the module chain, so give modules a `parent` chain.
- The defines give separate experience costs for adding, replacing, converting, and removing a module (`EQUIPMENT_MODULE_ADD_XP_COST`, `_REPLACE_`, `_CONVERT_`, `_REMOVE_`); `can_convert_from` declares the related modules and their `convert_cost_ic`.
- A turret module that restricts main-armament categories makes some guns unselectable until the turret is fitted; define the turret slot first in the archetype.

## Slots and categories

Slot and category names are identifiers; there is no registry file.
They exist because an archetype's `module_slots` and a module's `category` use them.
Localise them with `EQ_MOD_SLOT_<slot>_TITLE` and `EQ_MOD_CAT_<category>_TITLE` (see `GAME/localisation/english/tank_modules_l_english.yml` and `ship_modules_l_english.yml`).

Vanilla slot sets to mirror when adding a chassis:

- Tank: `turret_type_slot`, `main_armament_slot`, `suspension_type_slot`, `armor_type_slot`, `engine_type_slot`, `special_type_slot_1` to `special_type_slot_4` (`tank_chassis.txt`).
- Ship: `fixed_ship_battery_slot`, `fixed_ship_anti_air_slot`, `fixed_ship_fire_control_system_slot`, `fixed_ship_radar_slot`, `fixed_ship_torpedo_slot`, `fixed_ship_engine_slot`, then `mid_1_custom_slot` and `rear_1_custom_slot` (`ship_hull_light.txt`).
- Aircraft: `fixed_main_weapon_slot`, `fixed_auxiliary_weapon_slot_1`, `engine_type_slot`, `special_type_slot_1`, `special_type_slot_2` (`plane_airframes.txt`).

Ship hull archetypes also carry `alias`, `upgrades`, and `manpower`.
Airframe archetypes carry `type_override`, `allowed_types`, `allow_mission_type`, `sprite`, `air_map_icon_frame`, `substitute`, and `interface_overview_category_index`.
Copy them from the closest vanilla airframe rather than inventing values.

## Designer windows

Files live in `GAME/interface/equipmentdesigner/tanks/`, `ships/`, and `planes/`.
The file name does not matter; the container window name does.
Window names searched, in order (`GAME/interface/equipmentdesigner/_documentation.info`):

1. `equipment_designer_<TYPE>_<TAG>`
2. `equipment_designer_<ARCHETYPE>_<TAG>`
3. `equipment_designer_<TYPE>`
4. `equipment_designer_<ARCHETYPE>`

Vanilla uses archetype names for tanks and ships (`equipment_designer_amphibious_tank_chassis`, `equipment_designer_ship_hull_light`) and per-type names for airframes (`equipment_designer_small_plane_airframe_0` in `planes/plane_blueprints_generic.gui`).
A plane comment at the top of `plane_airframes.txt` says an airframe must be added to `plane_blueprints_generic.gui` or it will not show up.

Inside the window:

- An inner `containerWindowType` named `module_slots` holds one container per slot, named exactly like the slot.
- Inside each slot container, one container per installable module named by module, GFX name, category, or slot (searched in that order), plus matching `<name>@highlight` containers.
  A bare `@highlight` container is the fallback highlight.
- The base art is an `iconType` named `equipment_image` or `equipment_image_overlay`.

Without a window the equipment falls back to the upgrade system, so a modular chassis without a window appears to have no design screen (wiki Equipment modding, Equipment Designer).

Module art sprites: `GFX_EMI_<module>` for tank modules in `GAME/interface/tank_modules_icons.gfx`; other designer sprites in `equipmentdesignerview.gfx` and `equipmentdesignermoduleicons.gfx`.
Blueprint overlay sprites follow `GFX_TM_<chassis>_<slot>` as seen in `tank_chassis_amphibious_tank.gui`.

## Icon and model pools per country

`GAME/gfx/interface/equipmentdesigner/graphic_db/00_tank_icons.txt`, `00_plane_icons.txt`, and `00_hq_icons.txt` associate equipment types or archetypes with GFX names and 3D entity names.
Syntax and ordering rules are in `_documentation.info` in the same folder.
Key points from that file:

- Root keys are `default`, a continent, or a country tag; inside, keys are equipment types or archetypes.
- A `pool` can hold `limit`, `weight`, `icons`, `models`, and the filters `sub_units`, `ideologies`, and `cultures`; all filters and `limit` must pass.
- Type definitions sort above archetype definitions, country above continent above default, and later files above earlier ones when weights tie.
- Icons within a pool are displayed in reverse order in the interface.

A variant can also fix its icon and model directly with `icon` and `model` in `create_equipment_variant`.

## AI equipment designs

Files in `GAME/common/ai_equipment/` (installed syntax in `_documentation.md`; vanilla precedents `generic_tank.txt`, `ENG_naval.txt`).
They tell the AI which variants to design and refit toward.

```
MY_design_group = {
	category = land				# land, naval, or air
	blocked_for = { }				# tags excluded
	available_for = { MYT }			# empty means every tag not blocked
	roles = { land_light_tank }		# feeds role_ratio; one design per role is kept active
	priority = { factor = 1000 modifier = { factor = 2 has_war = yes } }

	my_design = {
		name = my_class_name			# vanilla files use name, design_team, and role_icon_index
		priority = { factor = 10 }
		enable = { has_tech = my_tech }
		history = yes				# folder in the designer
		target_variant = {
			match_value = 1000
			type = light_tank_chassis_0
			modules = {
				main_armament_slot = tank_heavy_machine_gun	# category, module, empty, < module, > module, or a nested block
				engine_type_slot = tank_gasoline_engine
				special_type_slot_1 = empty
			}
		}
		requirements = { }
		allowed_modules = { tank_heavy_machine_gun tank_gasoline_engine }
	}
}
```

- A nested slot block accepts `module` (category, module, `< module`, `> module`, `empty`, or `> empty`), `any_of = { ... }`, and `upgrade > current` or `upgrade = current` for refits.
  Several entries in one block need only one to match.
- A module not listed in `allowed_modules` is never added to a remaining slot; earlier entries are favoured.
- The wiki additionally lists `upgrades` inside `target_variant` and `allowed_types`; those are not in the installed documentation, so check a vanilla file before relying on them.
- Whether the AI designs a custom chassis that has no group is not documented; if AI use matters, write a group and state the result as unobserved.
- For role ratio, production strategy, and `ai_will_do`, use `hoi4-ai-strategies` and its `references/other-ai-systems.md`.

## Checks for this surface

- Confirm every slot name in the archetype has a container in each designer window you add, and every module category has a matching module.
- Confirm the module has a localisation key, a description, a category title, and a `GFX_EMI_` or equivalent sprite.
- Create a default variant mentally from `default_modules` and verify each default module's category is allowed in its slot, and no `module_count_limit` is violated.
- For an AI design, check that `type` and every named slot exist on the chassis and that each module in `modules` is in `allowed_modules`.
- State that the designer layout and AI design selection were not observed in the game.
