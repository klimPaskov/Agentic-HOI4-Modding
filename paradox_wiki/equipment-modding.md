# Equipment modding

*Offline snapshot of the Hearts of Iron IV Wiki page "Equipment modding", revision 104717, captured 2026-10-31. Wiki text by the wiki's contributors under CC BY-SA 3.0 (see LICENSE.txt); kit blocks are local additions under the same license.*

<!-- kit:begin id="review" at="top" build="1.19.3.0" checked="2026-10-31" revision="104717" sources="common/units/equipment/ common/units/equipment/modules/ common/equipment_groups/ common/script_enums.txt interface/equipmentdesigner/ gfx/interface/equipmentdesigner/graphic_db/ localisation/english/equipment_l_english.yml hoi4.exe" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Checked against `common/units/equipment/_documentation.md`, `common/equipment_groups/_documentation.md`, the two equipment designer `_documentation.info` files, all 45 vanilla equipment files (308 equipment blocks and 34 duplicated archetypes), the module files, `script_enum_equipment_category` and `script_enum_equipment_stat`, and a token search of `hoi4.exe`.
Kit blocks added: `equipment-keys` (keys the templates omit, `manpower` and `is_frame` corrections), `equipment-types` (real type values), `equipment-group-by`, `equipment-interface-categories`, `equipment-designer-notes` (`duplicate_archetypes`, window lookup, graphic_db, modules), `equipment-stats-enum`, `equipment-naval-stats-warning` (four dead stat names), `equipment-air-stats`, `equipment-localization`.
Gaps left: the in-game effect of `group_by`, `visual_level`, `priority` and `abbreviation` is not documented and is marked [unverified]; module files are summarised, not documented key by key.
<!-- kit:end id="review" -->

## Table of contents

- [Equipment](#Equipment)
  - [Kit: Equipment keys in 1.19.3](#kit-equipment-keys)
  - [Internal Types](#Internal_Types)
    - [Land](#Land)
    - [Naval](#Naval)
    - [Air](#Air)
    - [Kit: Equipment type values in 1.19.3](#kit-equipment-types)
  - [Group By types](#Group_By_types)
  - [Interface Categories](#Interface_Categories)
  - [Equipment Designer](#Equipment_Designer)
    - [Kit: Designer windows, variants and modules](#kit-equipment-designer-notes)
- [Stats](#Stats)
  - [Kit: Valid equipment stat names](#kit-equipment-stats-enum)
- [Modifiers](#Modifiers)
  - [All](#All)
  - [Land](#Land_2)
    - [Base](#Base)
    - [Offensive](#Offensive)
    - [Defensive](#Defensive)
    - [Unique](#Unique)
  - [Navy-specific](#Navy-specific)
  - [Air-specific](#Air-specific)
- [Localization](#Localization)

---

## Equipment <a id="Equipment"></a>

Equipment is found in `/Hearts of Iron IV/common/units/equipment/*.txt`. Equipment is split into two types, archetype and regular. Archetype equipment is used to assign more general attributes that regular equipment then inherits via the *archetype* attribute.

Archetype equipment follows the following format:

```text
equipments = {
	<equipment> = {
		year = <int>		# Limits the equipment from appearing before the specified year. Optional
		picture = <name>	# GFX reference used to define equipment picture in lend-lease
		priority = <value> # ?
                archetype = <equipment archetype name> - archetype of equipment, mutually exclusive with is_archetype = yes
                parent = <equipment type name> - previous version of equipment, can't be archetype
		can_be_produced = {	# Optional, specifies when equipment of this category can be produced.
			<triggers>
		}
	        can_be_lend_leased = {
                # a trigger to check if a country can lend lease to another country. scope is country, from is the country we will lend lease to
                }
		is_archetype = yes	# Specifies an entry as an archetype entry. All non-archetype entries inherit
		is_buildable = no	# Prevents this equipment from being built.
		active = yes		# Determines if this equipment is available without unlocking from a technology.

		type = <type>	   	# Internal type: what kind of unit can use this equipment
                is_frame = <yes|no> #  Default yes for modular equipment, not applicable for non-modular equipment. Frame refers to tank chassis, ship hulls, and airplane frames.
		group_by = <group>			  # How the equipment is grouped in the production screen
		interface_category = <type>	 # Which category the equipment appears in the production screen
                max_military_factories = <amount>/max_dockyard_factories = <amount> 	# Limit the amount of military factories or dockyards assignable to the type

                module_slots = {
                # List of module slots and their details
                # Fixed slots will be grouped together in the equipment designer window, and always start with "fixed_". They represent slots that are used for a single purpose or related purposes.
                fixed_<slot name> = {
			required = <yes|no>
			allowed_module_categories = {
				# List of module category names
			}
		}
                # Custom slots will be grouped together in the equipment designer window, and cannot start with "fixed_". They represent slots that can be used for a lot of different purposes.
                <custom slot name> = {
			required = <yes|no>
			allowed_module_categories = {
				# List of module category names
			}
		}
                <slot name> = <earlier slot name> # A later slot can inherit the exact same attributes from an earlier slot.
                <slot name> = inherit # A slot can inherit the exact same attributes from the parent equipment type.
                }
                module_slots = inherit # alternative way to setup modules, equipment will use same modules as parent
                # Any number of module count limits can be specified.They are automatically inherited by child equipment types.
		module_count_limit = {
                # Match conditions:  A module or slot only needs to match one of the specified conditions for the limit to apply.
		module = <module name> # Match a specific module.
                category = <module category name> # Match any module belonging to a category.
			module = any # Match any module.
			category = any # Match any module.
			module = empty # Match an empty module slot.

			# Specify the upper limit on the number of matching modules.
			count < <number>
			# -or- Specify the lower limit on the number of matching modules.
			count > <number>
			# -or- Specify the exact requirement on the number of matching modules.
			count = <number>
			# -or- Allow any number of matching modules.  Useful for overriding limits inherited from parent equipment type.
			count = any

			# Optional override of the limitation title used in tool tips.
			# If not specified, the single module, category, any, or empty configuration will be used if possible.
			title = <text or localization key>
                        # An inherited limit is overridden if the child has a limit with exactly the same match conditions.
                }
		# Resources used to build this equipment
		resources = {
			<resource> = <amount>
		}
		upgrades = {
			# List of upgrade names
		} # Upgrades of equipment, mostly used for non equipment designer versions of equipment

		# Modifiers the equipment uses
		<unit stat name> = <value>

                manpower = <value> # Manpower required to produce one unit of the equipment (naval only)
	}
}
```

Regular equipment follows the following format:

```text
equipments = {
    <equipment> = {
        year = <int>        # Limits the equipment from appearing before the specified year. Optional

        active = yes            # Determines if this equipment is available without unlocking from a technology.

        archetype = <equipment> # Which archetype equipment this equipment inherits from.
        parent = <equipment>    # Which equipment is parent to this equipment (i.e. which does it supercede)
        priority = <int>        # Priority for usage over other equipment.
        visual_level = <int>    # Image priority in production screen

        # Resources used to build this equipment
        resources = {
            <resource> = <amount>
        }

        # Modifiers the equipment uses
        <modifiers>
    }
}
```

<!-- kit:begin id="equipment-keys" at="section:Equipment" -->
### Kit: Equipment keys in 1.19.3 <a id="kit-equipment-keys"></a>

**Kit correction** Two statements in the templates above are out of date, and both templates leave out keys that vanilla uses.

- `manpower` is not naval only. The documentation says so, but vanilla also sets it on plane airframes (`plane_airframes.txt`, `x_plane_airframes.txt`, `quad_engine_airframe.txt`), tank chassis (`tank_chassis.txt`) and railway guns. It is on 125 of the 308 equipment blocks. [vanilla-confirmed 1.19.3] `common/units/equipment/*.txt`
- `is_frame` and `max_dockyard_factories` are real keys: both are in the documentation and both strings are in `hoi4.exe`. No vanilla file sets either. `max_military_factories` is set in 3 blocks (value 5; `artillery.txt` twice, `tank_chassis.txt` once). [docs] `common/units/equipment/_documentation.md`, [vanilla-confirmed 1.19.3] for the usage counts
- The documentation's `type` list includes `naval_transport`, but no vanilla equipment uses it and it is not in `script_enum_equipment_category`. [vanilla-confirmed 1.19.3] `common/script_enums.txt`

Keys vanilla uses that the templates do not show. Counts are blocks in `common/units/equipment/*.txt` out of 308 (archetypes and regular equipment). Source of every row: [vanilla-confirmed 1.19.3] unless the row says [docs].

| Key | Count | What vanilla shows |
| --- | --- | --- |
| `default_modules` | 87 | `<slot> = <module>` or `<slot> = empty`; the modules of the default variant. [docs] `common/units/equipment/_documentation.md` |
| `ai_type` | 1 (plus 4 duplicated archetypes) | Overrides `type` for AI unit ratios. Documented values `cv_fighter`, `cv_interceptor`, `cv_cas`, `cv_naval_bomber`, `cv_suicide`, `heavy_fighter`. [docs] |
| `abbreviation` | 83 | Short string such as `"lt1"` or `"afs0"`. Use is not documented. [unverified] |
| `derived_variant_name` | 35 | Localisation key such as `light_tank_equipment_0`. A string in `hoi4.exe` says it names derived designs. [unverified] |
| `can_convert_from` | 37 | List of equipment ids; hull and chassis upgrades use it (carrier hulls list cruiser and heavy hulls). |
| `allow_mission_type`, `forbid_mission_type` | 29, 3 | Lists of air mission names (`barrage_mission`, `training`). |
| `picture` | 35 | Archetype picture name such as `archetype_light_tank_equipment`. A sprite `GFX_archetype_light_tank_equipment_medium` exists in `interface/Technologies.gfx`, so the mapping is probably picture name with `GFX_` before and `_medium` after. [unverified] |
| `sprite`, `model` | 28, 22 | `sprite` names a map sprite (`missile_default`, `convoy`); `model` names a ship model (`repair_ship`, `ship_hull_super_carrier`). |
| `visual_level` | 144 | Integer 0 to 3 on regular equipment. The wiki calls it the image priority in the production screen. [unverified] |
| `visual_tech_level_addition` | 2 | Integer on carrier and heavy hulls. |
| `weight` | 21 | Plane stat, for example `weight = 3`. |
| `interface_overview_category_index` | 7 (plus 10 duplicated) | Index of the airforce overview row; `-1` hides the plane from the intel and airforce overview (comment in `x_plane_airframes.txt`). |
| `air_map_icon_frame` | 12 (plus 13 duplicated) | Frame number of the air map icon. |
| `one_use_only` | 10 | `yes` on missiles; `no` on `emplacement_gun_ammo`. |
| `type_override`, `allowed_types` | 4, 6 | Airframes set `type_override = fixed_main_weapon_slot` and list the types a plane may take, for example `allowed_types = { fighter interceptor }`. |
| `modifier_stat` | 4 | Support ships: `modifier = naval_repair_support`, `value = 100`, `type = naval_support`. |
| `offensive_weapons` | 5 | `no` on convoys and carriers; the vanilla comment calls it a hidden combat behaviour stat. |
| `alias`, `substitute`, `family`, `supply_truck`, `upgrade_window_override` | 2, 1, 9, 2, 1 | Single-purpose keys: hull aliases (`alias = destroyer`), a plane that replaces another on carriers, a tank family label, a truck flag on motorised equipment, an upgrade window override on one cruiser hull. |
| `naval_dominance_factor`, `naval_weather_penalty_factor` | 50, 7 | Ship hull stats, for example `naval_dominance_factor = 20` on `ship_hull_light`. |
| `fuel_consumption` | 156 | Land and air stat, for example `fuel_consumption = 2.4` on `mechanized.txt`. |
<!-- kit:end id="equipment-keys" -->

### Internal Types <a id="Internal_Types"></a>

#### Land <a id="Land"></a>

- anti_air
- anti_tank
- armor
- artillery
- heavy_tank_chassis
- infantry
- light_tank_chassis
- mechanized
- medium_tank_chassis
- motorized
- rocket
- support_equipment

#### Naval <a id="Naval"></a>

- capital_ship
- carrier
- convoy
- naval_transport
- screen_ship
- submarine

#### Air <a id="Air"></a>

- air_transport
- cas
- fighter
- interceptor
- tactical_bomber
- missile
- naval_bomber
- strat_bomber
- suicide

<!-- kit:begin id="equipment-types" at="section:Air" -->
#### Kit: Equipment type values in 1.19.3 <a id="kit-equipment-types"></a>

**Kit correction** The three lists above are partly obsolete. `heavy_tank_chassis`, `light_tank_chassis` and `medium_tank_chassis` are archetype ids, not types (tank chassis have `type = armor`), `support_equipment` is the equipment id and the type is `support`, `strat_bomber` is `strategic_bomber`, and `naval_transport` does not exist. The valid values are the 38 entries of `script_enum_equipment_category`; every `type` that vanilla equipment uses is in it. [vanilla-confirmed 1.19.3] `common/script_enums.txt`, `common/units/equipment/*.txt`

| Group | Values |
| --- | --- |
| Land | `infantry`, `support`, `artillery`, `anti_tank`, `anti_air`, `armor`, `motorized`, `mechanized`, `rocket`, `amphibious`, `flame`, `land_cruiser`, `railway_gun`, `train` |
| Naval | `capital_ship`, `carrier`, `screen_ship`, `submarine`, `convoy`, `support_ship`, `floating_harbor`, `missile_launcher` |
| Air | `fighter`, `heavy_fighter`, `interceptor`, `cas`, `naval_bomber`, `tactical_bomber`, `strategic_bomber`, `scout_plane`, `maritime_patrol_plane`, `air_transport`, `suicide`, `missile`, `ballistic_missile`, `nuclear_missile`, `sam_missile`, `emplacement_gun_ammo` |

`land_cruiser` and `missile_launcher` are in the enum but no vanilla equipment block uses them as `type`. The grouping in the table is the kit's, not the game's. [vanilla-confirmed 1.19.3]

`type` may be a list: the first value is the main type and the rest are secondary types, for example `type = { screen_ship anti_air }` on `light_cruiser_1` and `type = { armor anti_air }` for the anti-air tank chassis. Every secondary value that vanilla uses (`anti_air`, `anti_tank`, `artillery`, `amphibious`, `flame`, `rocket`, `support`, `infantry`, `motorized`) is also a sub-unit `type` in `common/units/*.txt`. The wiki adds that a new type needs at least one sub-unit using it. [vanilla-confirmed 1.19.3] `common/units/equipment/ship_hull_cruiser.txt`, `common/units/equipment/x_tank_chassis.txt`; the wiki's rule [unverified]

These values are also the keys that `equipment_bonus` and military industrial organizations accept, together with equipment ids and groups (`script_enum_equipment_bonus_type`). [vanilla-confirmed 1.19.3] `common/script_enums.txt`
<!-- kit:end id="equipment-types" -->

### Group By types <a id="Group_By_types"></a>

- archetype
- type

<!-- kit:begin id="equipment-group-by" at="section:Group_By_types" -->
**Kit addition** `group_by` has two values, `archetype` and `type`. Vanilla sets it only on archetypes: 37 blocks use `archetype` (every tank chassis, `small_plane_airframe`, `convoy`, `ship_hull_carrier`, `ship_hull_submarine`, the land equipment archetypes) and 5 use `type` (`ballistic_missile_equipment`, `explosive_ammo_equipment`, `guided_missile_equipment`, `nuclear_missile_equipment`, `sam_missile_equipment`). The other ship hull archetypes set no `group_by`. The token is in `hoi4.exe`; the documentation does not describe it, and the wiki's explanation (how the equipment is grouped in the production screen) is the only description. [vanilla-confirmed 1.19.3] `common/units/equipment/*.txt`; the effect [unverified]
<!-- kit:end id="equipment-group-by" -->

### Interface Categories <a id="Interface_Categories"></a>

- interface_category_land
- interface_category_armor
- interface_category_capital_ships
- interface_category_screen_ships
- interface_category_other_ships
- interface_category_air

<!-- kit:begin id="equipment-interface-categories" at="section:Interface_Categories" -->
**Kit addition** The six values above are the only ones vanilla equipment uses: `interface_category_land` 17 blocks, `interface_category_air` 12, `interface_category_armor` 9, `interface_category_other_ships` 7, `interface_category_screen_ships` 4 and `interface_category_capital_ships` 2. `hoi4.exe` also holds `interface_category_resources`, `_stockpiling`, `_reinforcing`, `_upgrading` and `_outdated`; these are not used by any vanilla equipment and their purpose is unknown. [vanilla-confirmed 1.19.3] `common/units/equipment/*.txt`; the extra tokens [unverified]
<!-- kit:end id="equipment-interface-categories" -->

### Equipment Designer <a id="Equipment_Designer"></a>

Added in the Man the Guns, No Step Back and By Blood Alone, equipment designer is the interface to design equipment with different modules, allowing to change type of equipment or just add additional stats to the equipment.

**Any equipment that utilizes modules must have equipment designer set-up, if equipment designer not presented it will instead utilize upgrade system/**

The game equipment designers can be found in interface/equipmentdesigner/type where type is tanks/ships/planes. **The name of the file doesn't mater.Equipment linked differently.**

To connect designer to the equipment you need to name containerWindowType with one of 4 types:

"equipment_designer_" EQUIPMENT_TYPE "_" COUNTRY_TAG - used to specify equipment designer for specific tag and specific equipment

"equipment_designer_" EQUIPMENT_ARCHETYPE "_" COUNTRY_TAG - used to specify equipment designer for specific tag and equipment archetype

"equipment_designer_" EQUIPMENT_TYPE - used to specify designer for equipment

"equipment_designer_" EQUIPMENT_ARCHETYPE - used to specify equipment designer for equipment archetype

Within these equipment designer windows for a specific piece of equipment, there is an inner container window named "module_slots". Each module slot that is possible for any equipment using this designer window should have its own container window inside here, using the same name as the module slot.

Inside a module slot container window, further container windows should be listed, corresponding to the modules that can be installed in that module slot.Within them, you can include the iconType elements or any other elements appropriate for displaying the associated module on the equipment for that slot

**Like previously mentioned new system allows for creating a special types of equipment (e.g. Anti-tank tank or Anti-Air tank), in order to do this you need a module that allows this type, this type should be present in script_enums and must have at least one battalion using it.**

To create equipment variant you need to use this code:

<equipment_archetype>_my_variant = {

archetype = <equipment_archetype>

type = { innitial_type anti_air }

for_each = {

variant_name = { find_and_replace = { "chassis" "equipment" } } # optional, set variant_name by taking what would be used as the localization key (the name of the type) and run a find-and-replace on it. Example: light_tank_aa_chassis_1 gets variant_name light_tank_aa_equipment_1.

hardness = { set = 0.5 } # additional stats new type of equipment would get

}

}

**All new variants must be present in script_enums, so if you duplicate equipment archetype with 5 variants of equipment you must specified all in scripted_enums (e.g. <equipment_archetype>_my_variant, <equipment_archetype>_my_variant_0, <equipment_archetype>_my_variant_1...)**

<!-- kit:begin id="equipment-designer-notes" at="section:Equipment_Designer" -->
#### Kit: Designer windows, variants and modules <a id="kit-equipment-designer-notes"></a>

**Kit addition** Where the designer windows and variants really live in 1.19.3.

**Variants are duplicated archetypes.** The wiki's `<equipment_archetype>_my_variant = { archetype = ... type = { ... } for_each = { ... } }` sits inside a root block `duplicate_archetypes = { }`, in a file that is evaluated after the files that define the archetypes. Vanilla keeps them in `x_tank_chassis.txt` (21 duplicates) and `x_plane_airframes.txt` (13). The attributes `alias`, `type`, `variant_name` and `derived_variant_name` are not copied from the archetype, so each duplicate sets its own `type`. `for_each` sets stats on every generated equipment; planes may instead map names with `variant_name = { <equipment> = <loc key> }`. Plane duplicates also use `only_duplicate_archetype`, `substitute`, `ai_type` and `forbid_mission_type`. [vanilla-confirmed 1.19.3] `common/units/equipment/x_tank_chassis.txt`, `common/units/equipment/x_plane_airframes.txt`

```text
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

The wiki says new variants must be listed in "script_enums"; the file is `common/script_enums.txt` and the two relevant enums are `script_enum_equipment_category` (valid `type` values) and `script_enum_equipment_bonus_type` (names that `equipment_bonus` and military industrial organizations accept, including equipment ids such as `light_tank_chassis_1`). The second enum's comment says it should be updated whenever equipment is added and that the game logs an error at startup when it is stale. [vanilla-confirmed 1.19.3] `common/script_enums.txt`

**Window lookup.** The designer finds the top-level container by trying `equipment_designer_<TYPE>_<TAG>`, `equipment_designer_<ARCHETYPE>_<TAG>`, `equipment_designer_<TYPE>` and `equipment_designer_<ARCHETYPE>`, in that order. Inside it, `module_slots` holds one container per slot, named like the slot; inside that, one container per module. A module's container is found by trying the module name, the module GFX name, the module category name and the slot name, in that order. A `@highlight` suffix names the highlight element (`ship_heavy_battery@highlight`), and a bare `@highlight` is the fallback. [docs] `interface/equipmentdesigner/_documentation.info`

**Files.** Vanilla splits designer windows into `interface/equipmentdesigner/planes/`, `ships/` and `tanks/`; the file name does not matter. [vanilla-confirmed 1.19.3] `interface/equipmentdesigner/`

**Icons and models per equipment (graphic_db).** `gfx/interface/equipmentdesigner/graphic_db/*.txt` (vanilla: `00_tank_icons.txt`, `00_plane_icons.txt`, `00_hq_icons.txt`) maps an equipment type or archetype to icons and 3D models. Root keys are `default`, a continent name or a country tag; under them each key is an equipment type or archetype holding `pool` blocks. A `pool` may hold `limit` (trigger), `weight` (sort order, default 1), `icons` (GFX names), `models` (entity names) and three filters: `sub_units`, `ideologies` and `cultures` (graphical culture keys from `common/graphicalculturetype.txt`); an empty filter is unrestricted, and every filter that is set must match. Country beats continent beats `default`, type beats archetype, and later definitions beat earlier ones when weights tie. [docs] `gfx/interface/equipmentdesigner/graphic_db/_documentation.info`

**Module files.** Modules are defined in `common/units/equipment/modules/` (vanilla: `00_tank_modules.txt`, `00_ship_modules.txt`, `00_plane_modules.txt`), inside `equipment_modules = { }`: 316 modules. Keys they use: `category` and `abbreviation` (312 each), `add_stats` (311), `sfx` (280), `multiply_stats` (205), `can_convert_from` (168), `xp_cost` (153), `dismantle_cost_ic` (129), `parent` (114), `build_cost_resources` (66), `critical_parts` (54), `add_equipment_type` (47), `gfx` (42), `mission_type_stats` (33), `allow_mission_type` (30), `gui_category` (28), `add_average_stats` (28), `allow_equipment_type` (23), `allowed_module_categories` (11), `forbid_module_categories` (10), `forbid_equipment_type` and `forbid_equipment_type_exact_match` (4 and 6). Technologies unlock modules with `enable_equipment_modules`. [vanilla-confirmed 1.19.3] `common/units/equipment/modules/*.txt`
<!-- kit:end id="equipment-designer-notes" -->

## Stats <a id="Stats"></a>

Equipment uses modifiers to determine which stats it confers to its assigned unit.

Typically an equipment will include the following:

```text
build_cost_ic = <float>
lend_lease_cost = <float>
reliability = <float>
maximum_speed = <float>
defense = <float>
breakthrough = <float>
hardness = <float>
armor_value = <float>
soft_attack = <float>
hard_attack = <float>
ap_attack = <float>
air_attack = <float>
```

Note that the default *maximum_speed* is 4, so you don't need to include it when you want equipment to confer the default *maximum_speed*.

<!-- kit:begin id="equipment-stats-enum" at="section:Stats" -->
### Kit: Valid equipment stat names <a id="kit-equipment-stats-enum"></a>

**Kit addition** The stat names that equipment, `equipment_bonus` and military industrial organizations accept are the 78 entries of `script_enum_equipment_stat`. [vanilla-confirmed 1.19.3] `common/script_enums.txt`

```text
default_morale defense breakthrough hardness soft_attack hard_attack recon entrenchment
initiative casualty_trickleback supply_consumption_factor supply_consumption suppression
suppression_factor experience_loss_factor equipment_capture_factor recovery
additional_collateral_damage fuel_capacity surface_detection sub_detection surface_visibility
sub_visibility lg_attack lg_armor_piercing hg_attack hg_armor_piercing torpedo_attack sub_attack
anti_air_attack amphibious_defense naval_speed naval_range mines_planting mines_sweeping
naval_light_gun_hit_chance_factor naval_heavy_gun_hit_chance_factor naval_torpedo_hit_chance_factor
naval_torpedo_damage_reduction_factor naval_torpedo_enemy_critical_chance_factor
convoy_raiding_coordination patrol_coordination search_and_destroy_coordination air_range
air_defence air_attack air_agility air_bombing air_superiority naval_strike_attack
naval_strike_targetting air_ground_attack air_visibility_factor railway_gun_attack
railway_gun_attack_range_index_in_define railway_gun_annex_ratio
railway_gun_hours_between_redistribution max_organisation max_strength maximum_speed
armor_value ap_attack reliability reliability_factor weight thrust fuel_consumption
fuel_consumption_factor strategic_attack carrier_size submarine_carrier_size
carrier_surface_detection carrier_sub_detection acclimatization_hot_climate_gain_factor
acclimatization_cold_climate_gain_factor night_penalty build_cost_ic naval_weather_penalty_factor
```

The enum's own comment says stats owned by the battalion rather than the equipment do not work with military industrial organizations: `default_morale`, `recon`, `initiative`, `casualty_trickleback`, the supply consumption and suppression stats, `experience_loss_factor`, `equipment_capture_factor`, `railway_gun_attack`, `max_organisation`, `max_strength` and the two acclimatization factors. `entrenchment` only works for tanks with dozer blades, not infantry. No vanilla equipment block sets `entrenchment` or `recon`, although the Stats and Modifiers sections below list them for equipment. `lend_lease_cost`, `manpower`, `can_license` and `is_convertable` are not in the enum but are ordinary equipment keys. [vanilla-confirmed 1.19.3] `common/script_enums.txt`, `common/units/equipment/*.txt`
<!-- kit:end id="equipment-stats-enum" -->

## Modifiers <a id="Modifiers"></a>

The following list is all the valid modifiers for use in equipment (and units):

### All <a id="All"></a>

```text
lend_lease_cost = 1             # Space taken up in convoy
build_cost_ic = 0.4             # Production Cost - How much factory output this piece of equipment needs
manpower = 300                  # Manpower - Cost in manpower to produce
can_license = no                # Can be licensed
is_convertable = yes            # Can be converted
```

### Land <a id="Land_2"></a>

#### Base <a id="Base"></a>

```text
reliability = 0.9               # Reliability - The lower the reliability, the more likely the equipment will suffer random failure
maximum_speed = 4               # Max Speed - How quickly this unit can traverse terrain under optimal circumtances, in kilometres per hour
```

#### Offensive <a id="Offensive"></a>

```text
# Offensive
soft_attack = -0.1              # Soft Attack - How many attacks the unit can make versus enemies with low hardness
hard_attack = -0.5              # Hard Attack - How many attacks the unit can make versus enemies with high hardness
air_attack = 1                  # Air Attack - How much damage we can do against airplanes. High Air Attack also helps to counter enemy Air Superiority effects
ap_attack = 1                   # Piercing - Having equal or greater Piercing to the targets Armor value allows you to do more damage.
breakthrough = 0.5              # Breakthrough - How many enemy attacks a unit can attempt to avoid while on the offensive, effectively allowing it to stay on the offense longer.
```

#### Defensive <a id="Defensive"></a>

```text
# Defensive
defense = 0.1                   # Defense - How many enemy attacks a unit can avoid whilst on the defensive, effectively allowing it to stay on the defensive longer.
max_strength = 2                # HP - Strength represents how much damage this unit can suffer before it is destroyed
armor_value = 0                 # Armor - Armor that is higher than the opponents Piercing value reduces damage taken and allows more attacks to occur
hardness = 0.5                  # Hardness - Represents how much of your divsion is made up of armoured vehicles. High Hardness = High Hard Attacks, Low Soft Attack
entrenchment = 5                # Entrenchment - The ability to make proper defensive entrenchments before a hostile attack
```

#### Unique <a id="Unique"></a>

```text
recon = 1                       # Reconnaissance - Increases the chance that this unit can pick better tactics in battle
```

### Navy-specific <a id="Navy-specific"></a>

<!-- kit:begin id="equipment-naval-stats-warning" at="heading:Navy-specific" -->
**Kit correction** Four stat names in the list below do not exist in 1.19.3: `fire_range`, `shore_bombardment`, `evasion` and `port_capacity_usage`. None is set in any vanilla equipment or unit file, none is in the game documentation or in `script_enum_equipment_stat`, and `hoi4.exe` holds no script token with these exact names (only the longer `shore_bombardment_bonus` and `shore_bombardment_collateral_damage_factor` exist). The word `evasion` survives only in the comments of the defines `COMBAT_EVASION_TO_HIT_CHANCE` and `COMBAT_EVASION_TO_HIT_CHANCE_TORPEDO_MULT` in `common/defines/00_defines.lua`. The wiki already marks the first three OBSOLETE; treat all four as dead and do not write them. `search_and_destroy_coordination` and `convoy_raiding_coordination` are valid stats (in the enum), but no vanilla equipment block sets them. Real naval hull stats that the list omits include `naval_dominance_factor` (50 blocks), `naval_weather_penalty_factor` (7), `lg_attack`, `hg_attack` and the armour piercing pair (see the enum above). [vanilla-confirmed 1.19.3] `common/script_enums.txt`, `common/units/equipment/ship_hull_*.txt`
<!-- kit:end id="equipment-naval-stats-warning" -->

```text
naval_speed = 28                        # Max Speed - maximum speed in kilometres per hour of the ship, higher means faster in combat and contributes to evasion
fire_range = 32                         # Fire Range - The range of the ship's main guns (OBSOLETE)
lg_armor_piercing = 12                  # Light gun armor piercing - Determines how much armor ship's light gun attack can pierce
lg_attack = 18                          # Light gun attack - How much damage the ship does with light guns (more effective against screens)
hg_armor_piercing = 25                  # Heavy gun armor piercing - Determines how much armor ship's heavy gun attack can pierce
hg_attack = 12                          # Heavy gun attack - How much damage the ship does with heavy guns (more effective against capitals and carriers)
torpedo_attack = 1                      # Torpedo attack - How much damage we can do when using the ship's torpedos (more effective against capitals and carriers)
anti_air_attack = 5                     # Anti-air - How much anti-air firepower the ship carries for shooting down enemy planes
shore_bombardment = 8                   # Shore Bombard - Ship's ability to help out in land battles neighbouring its sea province when on Hold mission (OBSOLETE, lg_attack and hg_attack determine shore bombardment)
evasion = 15                            # Evasion - Ship's ability to evade enemy fire through maneuvering. (OBSOLETE, naval_speed contributes to evasion instead)
surface_detection = 12                  # Surface detection - Ability to detect surface vessels
sub_attack = 10                         # Anti-submarine attack - How much damage this ship deals to enemy submarines using depth charges
sub_detection = 5                       # Sub detection - Ability to detect submarines
surface_visibility = 25                 # Surface Visibility - How easy to find this ship is (lower is better)
sub_visibility = 20                     # Sub Visibility - How easy it is to detect this submarine (lower is better)
naval_range = 3000                      # Naval Range - max distance in kilometres the ship can travel from it's nearest Naval Base
port_capacity_usage = 1                 # Port capacity usage - How much room the ship requires in port
search_and_destroy_coordination = 0.1
convoy_raiding_coordination = 0.1
```

### Air-specific <a id="Air-specific"></a>

```text
air_attack = 50                         # Air Attack - amount of damage done against other planes
air_defence = 50                        # Air Defence - how many hits a plane takes before being shot down
air_range = 500                         # Range - How far away missions the plane can perform
air_agility = 10                        # Agility - How agile a plane is. Agility effects how easy it is to hit another plane, and avoid being hit
air_ground_attack = 100                 # Ground Attack - damage done to ground forces during CAS missions
air_bombing = 300                       # Strategic Bombing - how good the plane is at bombing
air_superiority = 1                     # Air Superiority - How much the plane helps the overall air superiority of a strategic area
naval_strike_attack = 1.5               # Naval Attack - how much damage the plane does against ships
naval_strike_targetting = 0.5           # Naval Targeting - how likely the plane is to hit a ship
carrier_size = 0.05
default_carrier_composition_weight = 1
carrier_capable = yes           # Is usable in carriers (air only)
```

<!-- kit:begin id="equipment-air-stats" at="section:Air-specific" -->
**Kit addition** `carrier_capable` is a boolean equipment key, not a stat: 11 vanilla airframes set `carrier_capable = yes`. `default_carrier_composition_weight` is set in two vanilla blocks and is not in `script_enum_equipment_stat`. `air_ground_attack` (12 blocks), `air_bombing` (21), `air_superiority` (52), `naval_strike_attack` (72), `naval_strike_targetting` (70) and `carrier_size` (6) are all in the enum. [vanilla-confirmed 1.19.3] `common/units/equipment/*.txt`, `common/script_enums.txt`
<!-- kit:end id="equipment-air-stats" -->

## Localization <a id="Localization"></a>

Each equipment must be localized in a *.yml* file in the *localisation* folder within your mod.

```text
<equipment>: ""
<equipment>_desc: ""
<equipment>_short: ""
```

For country-specific localization, prefix with the tag:

```text
<tag>_<equipment>: ""
<tag>_<equipment>_desc: ""
<tag>_<equipment>_short: ""
```

<!-- kit:begin id="equipment-localization" at="section:Localization" -->
**Kit addition** Vanilla defines `<TAG>_<equipment>` and `<TAG>_<equipment>_short` pairs for country names (`CHI_light_tank_equipment_1` with `CHI_light_tank_equipment_1_short`), 1626 `_short` keys in `equipment_l_english.yml`. Chassis, hulls and airframes are named in module and ship files (`tank_modules_l_english.yml` holds `light_tank_chassis: "Light Tank"`). A comment in `x_tank_chassis.txt` says `variant_name` is what would otherwise be the localisation key (`light_tank_aa_chassis_1` gets `light_tank_aa_equipment_1`). [vanilla-confirmed 1.19.3] `localisation/english/equipment_l_english.yml`, `localisation/english/tank_modules_l_english.yml`, `common/units/equipment/x_tank_chassis.txt`
<!-- kit:end id="equipment-localization" -->

---

## Navigation

**[Modding](<modding.md>)**

- **Documentation**: [Effects](<effects.md>) • [Triggers](<triggers.md>) • [Defines](<defines.md>) • [Modifiers](<modifiers.md>) • [List of modifiers](<list-of-modifiers.md>) • [Scopes](<scopes.md>) • [Localisation](<localisation.md>) • [On actions](<on-actions.md>) • [Data structures](<data-structures.md>) • [Flags](<data-structures.md#Flags>) • [Event targets](<data-structures.md#Event_targets>) • [Country tag aliases](<data-structures.md#Country_tag_aliases>) • [Variables](<data-structures.md#Variables>) • [Arrays](<data-structures.md#Arrays>)
- **Scripting**: [Achievements](<achievement-modding.md>) • [AI](<ai-modding.md>) • [AI focuses](<ai-focuses.md>) • [Autonomous states](<autonomy-state-modding.md>) • [Balances of power](<balance-of-power-modding.md>) • [Bookmarks/Scenarios](<bookmark-modding.md>) • [Game rules](<bookmark-modding.md#Game_rules>) • [Buildings](<building-modding.md>) • [Characters and traits](<character-modding.md>) • [Cosmetic tags](<cosmetic-tag-modding.md>) • [Countries](<country-creation.md>) • [Divisions](<division-modding.md>) • [Decisions](<decision-modding.md>) • [Doctrines](<doctrine-modding.md>) • [Events](<event-modding.md>) • [Factions](<faction-modding.md>) • [Ideas](<idea-modding.md>) • [Ideologies](<ideology-modding.md>) • [Military industrial organizations](<military-industrial-organization-modding.md>) • [National focuses](<national-focus-modding.md>) • [Resources](<resources-modding.md>) • [Scripted GUI](<scripted-gui-modding.md>) • [Technologies and doctrines](<technology-modding.md>) • [Units](<unit-modding.md>)
- **Map**: [Map](<map-modding.md>) • [States](<state-modding.md>) • [Supply areas](<supply-areas-modding.md>) • [Strategic regions](<strategic-region-modding.md>)
- **Graphical**: [Interface](<interface-modding.md>) • [Graphical assets](<graphical-asset-modding.md>) • [Entities](<entity-modding.md>) • [Posteffects](<posteffect-modding.md>) • [Particles](<particle-modding.md>) • [Fonts](<font-modding.md>)
- **Cosmetic**: [Portraits](<portrait-modding.md>) • [Namelists](<namelist-modding.md>) • [Music](<music-modding.md>) • [Sound](<sound-modding.md>)
- **Other**: [Console commands](<console-commands.md>) • [Troubleshooting](<troubleshooting.md>) • [Mod structure](<mod-structure.md>) • [Mods](<mods.md>) • [Nudger](<nudger.md>)
- **Kit pages (not on the wiki)**: [Collection modding](<collection-modding.md>) • [Defines additions](<defines-additions.md>) • [Game rule modding](<game-rule-modding.md>) • [Intelligence operation modding](<intelligence-operation-modding.md>) • [Map mode modding](<map-mode-modding.md>) • [Occupation and resistance modding](<occupation-and-resistance-modding.md>) • [Peace conference modding](<peace-conference-modding.md>) • [Raid modding](<raid-modding.md>) • [Script constant modding](<script-constant-modding.md>) • [Special project modding](<special-project-modding.md>)
