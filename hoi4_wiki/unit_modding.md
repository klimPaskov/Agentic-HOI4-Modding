# Unit modding

*Offline snapshot of the Hearts of Iron IV Wiki page "Unit modding", revision 71837, captured 2026-10-31. Wiki text by the wiki's contributors under CC BY-SA 3.0 (see LICENSE.txt); kit blocks are local additions under the same license.*

<!-- kit:begin id="review" at="top" build="1.19.4.1" checked="2026-11-01" revision="71837" sources="common/units/ common/unit_tags/00_categories.txt common/terrain/00_terrain.txt common/script_enums.txt interface/subuniticons.gfx localisation/english/deployment_l_english.yml localisation/english/unit_l_english.yml documentation/ hoi4.exe" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Checked against all 45 vanilla files in `common/units/` (158 sub-units), `common/unit_tags/00_categories.txt`, the terrain file, `script_enum_equipment_category`, the unit icon and group localisation, and a token search of `hoi4.exe`.
Kit blocks added: `unit-keys` (what every sub-unit sets and the keys the template omits), `unit-terrain-keys`, `unit-internal-types` (33 real values), `unit-group-types` (7 groups), `unit-map-icon-types`, `unit-stat-values` (the page's "vanilla uses" numbers are wrong), `unit-boolean-note`, `unit-navy-air-note` (equipment stats are not sub-unit keys; `fire_range`, `shore_bombardment`, `evasion` and `port_capacity_usage` do not exist), `unit-icons-note`.
Gaps left: the in-game meaning of `priority`, `ai_priority`, `map_icon_category` and `abbreviation` is inferred from usage, and the Models section was not re-checked against `gfx/entities/`.
**1.19.4.1 re-check (2026-11-01).** 17 statements depended on files the update changed (`infantry.txt`, `cavalry.txt`, `amphibious_mech.txt`, the self-propelled and tank destroyer brigade files in `common/units/`, and `deployment_l_english.yml`), and all 17 were re-measured: the 158 sub-units, the 7 groups, the 33 type values and the terrain counts are unchanged. Counts that moved or were corrected: `breakthrough` 63 to 64, `soft_attack` 46 to 49, `hard_attack` 32 to 37, `defense` 36 to 46, all 18 `required_dlc` sub-units need Thunder at Our Gates (not 17), and the `max_organisation` list now includes the values it left out. Every other statement cites files that are byte-identical in 1.19.4.1 (Steam depot manifest diff).
<!-- kit:end id="review" -->

## Table of contents

- [Unit Categories](#Unit_Categories)
- [Units](#Units)
  - [Kit: Sub-unit keys in 1.19.3](#kit-unit-keys)
  - [How to add new Groups](#How_to_add_new_Groups)
  - [Models](#Models)
  - [Internal Types](#Internal_Types)
  - [Group Types](#Group_Types)
  - [Map Icon Types](#Map_Icon_Types)
- [Stats](#Stats)
- [Modifiers](#Modifiers)
  - [Base](#Base)
  - [Costs](#Costs)
  - [Offensive](#Offensive)
  - [Defensive](#Defensive)
  - [Unique](#Unique)
  - [Boolean](#Boolean)
  - [Navy-specific](#Navy-specific)
  - [Air-specific](#Air-specific)
- [Localization](#Localization)
- [Icons](#Icons)

---

Units are the base object that equipment is applied to. Internally, units are actually sub-units of the hardcoded unit types, such as infantry, cavalry, fighter, etc.

## Unit Categories <a id="Unit_Categories"></a>

Unit categories are found in `/Hearts of Iron IV/common/unit_tags/00_categories.txt`.

Each unit is assigned a category that is used in technologies to apply effects to groups of units at once.

The following example from a technology grants bonuses to all units with the *category_all_infantry* category:

```text
category_all_infantry = {
    hard_attack = 0.25
    ap_attack = 1
}
```

## Units <a id="Units"></a>

Units are found in `/Hearts of Iron IV/common/units/*.txt`.

Units follow the following format:

```text
sub_units = {
    <unit name> = {
        sprite = <entity> # Refers to <name>_entity in a gfx/entities/.*.asset file - Controls the unit used on the map

        # Controls the map icon category used for the unit
        map_icon_category = <type>

        priority = <int>    # Controls which icon is used if multiple subunits of the same type exist
        ai_priority = <int>

        active = yes / no       # Whether the unit is usable without explicit unlocking in technology
        cavalry = yes           # Used to define subunit as cavalry
        special_forces = yes    # Used to define subunit as special forces
        marines = yes           # Used to define subunit as marine
        can_exfiltrate_from_coast = yes # Used to define subunit opportunity of leaving the coast without a naval base
        mountaineers = yes      # Used to define subunit as mountaineers
        can_be_parachuted = yes # Used to define subunit as paratroopers.
        affects_speed = yes     # Used to check if the unit will affect the template's speed, support companies have it set to no.

        transport = <equipment> # Sets the speed of subunit via equipment. Used for motorized/mechanized

        # How the unit is grouped division-wise, i.e. appearing in the Support tab. Not used for air or naval units
        group = <group>

        # Internal types
        type = {
            <type>
        }

        # Categories the unit belongs to.
        categories = {
            <categories>
        }

        # Equipment that is required for this unit. Used when active = no
        essential = {
            <equipment>
        }

        # Equipment needed to produce this unit. Unit won't be available until the nation has this equipment
        need = {
            <equipment>
        }

        # Modifiers control the stats of the unit. More detail under the Stats section.
        <modifiers>

        # Modifiers that occur only in specific terrain
        <terrain> = {
            <modifiers>
        }
    }
}
```

You cannot add new internal or map icon types, but you can add new groups.

<!-- kit:begin id="unit-keys" at="section:Units" -->
### Kit: Sub-unit keys in 1.19.4.1 <a id="kit-unit-keys"></a>

**Kit addition** Every one of the 158 vanilla sub-units sets `sprite`, `priority`, `active` and `type`. Those four are the safe minimum; vanilla never omits them. [vanilla-confirmed 1.19.4.1] `common/units/*.txt` (158 of 158)

`type` takes two forms. Land and naval sub-units use a block (`type = { infantry support }`, 133 sub-units); the 25 air sub-units use a single value (`type = fighter`). The first entry is the main type. `need` is a block of equipment ids with amounts (`need = { infantry_equipment = 100 }`) and is set by 156 sub-units; the two that omit it, `battle_cruiser` and `battleship`, use `need_equipment` and `need_equipment_modules` instead (the modules form takes an `any = { module = 1 }` list). [vanilla-confirmed 1.19.4.1] `common/units/battleship.txt`, `common/units/air.txt`

Keys vanilla sub-units use, with the number of sub-units (of 158) that set each. Counts are [vanilla-confirmed 1.19.4.1] `common/units/*.txt`. Meanings are read from usage and from comments in the vanilla files. No documentation file describes the sub-unit format. [vanilla-confirmed 1.19.4.1] `documentation/*.md`, `common/units/`. The meanings are [unverified].

| Key | Count | Notes |
| --- | --- | --- |
| `sprite` | 158 | Entity base name (`infantry`, `light_plane`, `submarine`). |
| `priority` | 158 | Integer. Examples: `infantry` 600, `submarine` 2, `fighter` 1, `engineer` 0. The template says it picks the icon when several sub-units share a type. |
| `active` | 158 | `yes` for 100, `no` for 58. `no` sub-units need a technology or effect to unlock them. |
| `type` | 158 | See above. |
| `need` | 156 | Equipment required per battalion. |
| `essential` | 49 | Equipment ids that must be owned for the unit to be usable (for example `support_equipment`). |
| `categories` | 138 | Unit categories from `common/unit_tags/00_categories.txt`, which defines 49. The 20 sub-units without it are all ships, both railway guns, the missiles and explosive ammo, `suicide_craft`, `cv_suicide_craft`, `rocket_interceptor` and `transport_plane`. |
| `map_icon_category` | 133 | `infantry`, `armored`, `ship` or `other`; air sub-units omit it. |
| `group` | 122 | Division designer group; air, naval and railway gun sub-units omit it. |
| `abbreviation` | 121 | Short quoted code such as `"INF"`. |
| `ai_priority` | 122 | Integer; examples: `engineer` 0, `bicycle_battalion` 150, `infantry` 200. |
| `max_organisation`, `max_strength`, `weight`, `manpower`, `default_morale`, `training_time`, `supply_consumption`, `combat_width` | 131, 124, 124, 122, 122, 120, 118, 113 | The base stat set the template lists. |
| `breakthrough`, `suppression`, `soft_attack`, `hard_attack`, `defense`, `armor_value`, `air_attack`, `ap_attack`, `recon`, `entrenchment`, `maximum_speed` | 64, 56, 49, 37, 46, 14, 11, 8, 12, 6, 9 | Optional combat stats, mostly on support companies. |
| `can_be_parachuted` | 57 | `yes` 39, `no` 18. |
| `affects_speed` | 42 | `no` 40, `yes` 2; support companies set `no`. |
| `regimental` | 55 | Always `no`; set on support companies and brigades. |
| `divisional` | 15 | Always `no`; set on the regimental fire support sub-units. |
| `same_support_type` | 31 | A support company id that cannot be combined with this one in a template (`same_support_type = recon`). |
| `battalion_mult` | 22 | Block with `category`, a stat and `add = yes`: a stat bonus per battalion of a category. |
| `allowed_battalion_groups` | 14 | Group list restricting which line battalions a regimental support unit attaches to. |
| `is_artillery_brigade` | 18 | `yes` 16, `no` 2. |
| `special_forces`, `marines`, `cavalry`, `mountaineers`, `rangers`, `can_exfiltrate_from_coast` | 11, 7, 2, 1, 1, 1 | Boolean role flags, all `yes`. `special_forces` also feeds `category_special_forces`. |
| `transport` | 10 | Equipment id that sets the speed of a motorised sub-unit: `motorized_equipment` (8), `mechanized_equipment` (1), `amphibious_mechanized_equipment` (1). |
| `required_dlc` | 18 | List of DLC names; all 18 need "Thunder at Our Gates" and `hq_armored_car` also lists "La Resistance". |
| `allow_in_army_hq`, `allow_in_non_army_hq`, `deployment_cost`, `division_3d_model_priority`, `deployed_leader_modifiers`, `enable_ability` | 18, 18, 18, 1, 11, 5 | Headquarters support companies. |
| `land_air_wing_size`, `carrier_air_wing_size`, `mega_carrier_air_wing_size`, `submarine_carrier_air_wing_size` | 25, 8, 19, 8 | Air wing sizes (for example 100 planes on land, 10 on a carrier). |
| `critical_parts`, `critical_part_damage_chance_mult`, `hit_profile_mult` | 7, 7, 7 | Ship damage model keys. |
| `own_equipment_fuel_consumption_mult` | 12 | Fuel use multiplier, `0.0` for non-fuel support. |
<!-- kit:end id="unit-keys" -->

<!-- kit:begin id="unit-terrain-keys" at="section:Units" -->
**Kit addition** Terrain blocks. 73 of the 158 sub-units contain at least one terrain block. The keys vanilla uses are `forest` (67), `jungle` (66), `marsh` (63), `river` (63), `mountain` (60), `amphibious` (56), `hills` (48), `urban` (45), `fort` (21), `plains` (17), `desert` (14) and `snow` (2). Inside a terrain block vanilla uses only three keys: `attack` (420 times), `movement` (308) and `defence` (81, spelled with a `c`). [vanilla-confirmed 1.19.4.1] `common/units/*.txt`

`forest`, `jungle`, `marsh`, `hills`, `mountain`, `plains`, `urban` and `desert` are terrain ids from `common/terrain/00_terrain.txt`. `river`, `amphibious`, `fort` and `snow` are not terrain ids in that file. The wiki's Technology modding page says `amphibious` applies to naval invasions and `river` to river crossings; the meaning of `fort` is not documented, but `localisation/english/unit_l_english.yml` defines the labels `fort`, `river`, `amphibious` and `snow`. [vanilla-confirmed 1.19.4.1] What the engine does with `fort` is [unverified]. The two sub-units that use `snow`, in `recon.txt`, carry the comment "This can end up stacking with terrain benefits". [vanilla-confirmed 1.19.4.1] `common/terrain/00_terrain.txt`, `common/units/recon.txt`

```text
bicycle_battalion = {
    ...
    plains = { movement = 0.2 }
    river = { movement = -0.05 }
    amphibious = { movement = -0.05 }
}
```

The snippet is from `common/units/infantry.txt`. [vanilla-confirmed 1.19.4.1]
<!-- kit:end id="unit-terrain-keys" -->

### How to add new Groups <a id="How_to_add_new_Groups"></a>

Inside any unit file, type the name of the new group in the "group" argument. The game will internally create the group and asign it to the current unit. For example:

```text
group = <group name>
```

Then, to add a localisation for our newly created group we must go to any localization file (preferably `/Hearts of Iron IV/localisation/unit_I_english.yml`) and define a new loc key as follows:

```text
group_<group name>_title:0 "Group name here"
```

To assign an icon to the new group you must go to `/Hearts of Iron IV/interface/subuniticons.gfx` and define a new spritetype as follows:

```text
spriteType = { name = "GFX_group_<group name>_icon"	     textureFile = "gfx/interface/counters/divisions_large/<icon file name>.dds" noOfFrames = 2 }
```

Note that the textureFile path doesn't have to be strictly `/Hearts of Iron IV/gfx/interface/counters/divisions_large/`, it can be any path.

### Models <a id="Models"></a>

*See also: [Entity modding](<entity_modding.md>)*

The model is assigned with the `sprite = SPRITE` attribute, which assigns the entity with the base name of `SPRITE_entity` by default to units whose division template has a plurality of this sub-unit. Similar to [country names](<country_creation.md#Name>), it is possible to assign further conditions by changing the name of the model, in this case by prepending a prefix to the base name. The priority starts with the default name as the lowest, then allowing using unique models for [graphical cultures](<country_creation.md#Country_file>), countries, or cosmetic tags.

An example `/Hearts of Iron IV/gfx/entities/*.asset` file is as such:

```text
entity = {
	name = SPRITE_entity # A simple model for a land unit
	pdxmesh = example_mesh # References a mesh defined in a *.gfx file

	default_state = idle
	state = { name = attack			animation = attack 					animation_blend_time = 0.0  animation_speed = 1.0 }
	state = { name = defend			animation = defend 			animation_blend_time = 0.3  animation_speed = 1.0 }
	state = { name = support_attack	animation = support_attack 	animation_blend_time = 0.3 animation_speed = 1.0 }
	state = { name = move				animation = move 		 		animation_blend_time = 1.0 animation_speed = 1.0 }
	state = { name = retreat			animation = retreat 	 		animation_blend_time = 0.3 animation_speed = 1.0 }
	state = { name = death			animation = death 			animation_blend_time = 0.3 animation_speed = 1.0 }
	state = { name = idle				animation = idle       		animation_blend_time = 0.3 animation_speed = 1.0 }
	state = { name = training				animation = training 			animation_blend_time = 0.3 animation_speed = 1.0 }

	scale = 0.8
}
entity = {
    name = middle_eastern_gfx_SPRITE_entity # Countries with the middle_eastern_gfx graphical culture will use a different mesh, with all other details the same
    clone = SPRITE_entity
    pdxmesh = middle_eastern_example_mesh
}
entity = {
    name = BHR_SPRITE_entity # The country BHR will use a unique mesh
    clone = SPRITE_entity
    pdxmesh = BHR_example_mesh
}
entity = {
    name = COSMETICTAG_SPRITE_ENTITY # Countries with the cosmetic tag of COSMETICTAG will use BHR's version entity
    clone = BHR_SPRITE_entity
}
```

### Internal Types <a id="Internal_Types"></a>

- infantry
- support
- artillery
- anti_tank
- anti_air
- armor
- fighter
- cas
- naval_bomber
- interceptor
- suicide
- tactical_bomber
- strategic_bomber
- air_transport
- missile
- submarine
- screen_ship
- capital_ship
- carrier
- motorized
- mechanized
- flame
- amphibious

<!-- kit:begin id="unit-internal-types" at="section:Internal_Types" -->
**Kit correction** The list is correct but incomplete. Vanilla sub-units use 33 type values: the 23 above plus `heavy_fighter`, `scout_plane`, `maritime_patrol_plane`, `ballistic_missile`, `nuclear_missile`, `sam_missile`, `emplacement_gun_ammo`, `railway_gun`, `rocket` and `support_ship`. All 33 are in `script_enum_equipment_category`, which has five more values that no sub-unit uses: `convoy`, `train`, `floating_harbor`, `land_cruiser`, `missile_launcher`. Sub-unit types and equipment types draw from the same enum. A block may list secondary types after the main one: `type = { infantry support }`, `type = { armor anti_tank }`, `type = { support armor anti_air }`. Air sub-units write a single value, not a block. [vanilla-confirmed 1.19.4.1] `common/units/*.txt`, `common/script_enums.txt`. How the engine matches sub-unit types against equipment types is not documented [unverified]
<!-- kit:end id="unit-internal-types" -->

### Group Types <a id="Group_Types"></a>

- infantry
- support
- mobile
- armor

<!-- kit:begin id="unit-group-types" at="section:Group_Types" -->
**Kit addition** `group` has 7 values in vanilla, three more than the list above. Counts are sub-units of 122 that set `group`. [vanilla-confirmed 1.19.4.1] `common/units/*.txt`

| Group | Count | What it holds | Loc key and icon |
| --- | --- | --- | --- |
| `infantry` | 13 | line infantry, bicycle, marines, mountaineers, rangers, paratroopers, militia, headquarters infantry | `group_infantry_title`, `GFX_group_infantry_icon` |
| `mobile` | 9 | cavalry, camelry, motorized, mechanized, armored cars, buses, headquarters | `group_mobile_title`, `GFX_group_mobile_icon` |
| `armor` | 11 | tank battalions | `group_armor_title`, `GFX_group_armor_icon` |
| `combat_support` | 4 | artillery, anti-air, anti-tank and rocket brigades (regimental) | `group_combat_support_title`, `GFX_group_combat_support_icon` |
| `mobile_combat_support` | 5 | the motorised versions of those brigades | `group_mobile_combat_support_title`, `GFX_group_mobile_combat_support_icon` |
| `armor_combat_support` | 12 | self-propelled anti-air, artillery and tank destroyer brigades | `group_armor_combat_support_title`, `GFX_group_armor_combat_support_icon` |
| `support` | 68 | support companies (engineers, recon, hospitals, logistics, headquarters companies) and the battery-level artillery, anti-air and anti-tank sub-units | `group_support_title`; no `GFX_group_support_icon` exists |

The 36 sub-units without `group` are all air, naval and railway gun sub-units. Group titles are in `localisation/english/deployment_l_english.yml` and group icons in `interface/subuniticons.gfx`. The wiki's steps for a new group (a `group_<name>_title` key and a `GFX_group_<name>_icon` sprite) match what vanilla defines for six of the seven groups; `support` has a title but no icon sprite. The `allowed_battalion_groups` key lists group names (`{ infantry mobile combat_support }`). [vanilla-confirmed 1.19.4.1] What each group does in the division designer is inferred from the loc titles [unverified]
<!-- kit:end id="unit-group-types" -->

### Map Icon Types <a id="Map_Icon_Types"></a>

- infantry
- armored
- other
- ship
- transport
- uboat

<!-- kit:begin id="unit-map-icon-types" at="section:Map_Icon_Types" -->
**Kit addition** The vanilla files document the options in a header comment (`common/units/infantry.txt` and others): land `infantry`, `armored`, `other`; sea `ship`, `transport`, `uboat`. Vanilla sub-units actually use four: `infantry` (75), `armored` (45), `ship` (9, including `submarine`) and `other` (4: `cavalry`, `camelry`, `railway_gun`, `super_heavy_railway_gun`). `transport` and `uboat` appear only in the comment, although `uboat` is also a token in `hoi4.exe`. The 25 air sub-units set no `map_icon_category`. The keyword picks the counter shown on the map. [vanilla-confirmed 1.19.4.1] `common/units/*.txt`; the counter effect [unverified]
<!-- kit:end id="unit-map-icon-types" -->

## Stats <a id="Stats"></a>

Units use modifiers to determine which stats they have and what special actions they may take.

Typically air units will not use any modifiers, whilst naval units use only *supply_consumption* and *max_organisation*.

Land units almost always use the following:

```text
manpower = <int>
max_strength = <int>
training_time = <int>
weight = <float>
default_morale = <float>
max_organisation = <int>
combat_width = <int>
supply_consumption = <float>
```

For *max_organisation*, vanilla uses the following values:

- infantry support: 20
- armor: 10
- armor support: 0
- ship: 40
- cavalry: 70

For *combat_width*, vanilla uses the following values:

- infantry: 0
- artillery: 0
- armor support: 1
- armor: 2

<!-- kit:begin id="unit-stat-values" at="section:Stats" -->
**Kit correction** The "vanilla uses" values are outdated. Measured over the 158 sub-units in 1.19.4.1 [vanilla-confirmed 1.19.4.1] `common/units/*.txt`:

| Stat | Wiki says | 1.19.4.1 shows |
| --- | --- | --- |
| `max_organisation` | infantry support 20, armor 10, armor support 0, ship 40, cavalry 70 | `infantry` group 70 (7), 60 (3), 100 (1), 50 (1), 45 (1); `armor` 10 (8 of 11); `mobile` 60 (5), 70 (2), 20 (1), 100 (1); `support` 0 (22), 20 (21), 30 (16), 10 (4), 60 (2), 12 (1), 45 (1), 70 (1); the three brigade groups 0; ships (no group) 40 (5), 50 (2), 35 (1), 30 (1) |
| `combat_width` | infantry 0, artillery 0, armor support 1, armor 2 | `infantry`, `mobile` and `armor` battalions 2 (one infantry sub-unit has 1); `support` 0 for every sub-unit that sets it (59 of 68); `combat_support` and `mobile_combat_support` 1 or 3; `armor_combat_support` 2 |

The template lists eight stats as "almost always" used; counts above show `max_organisation` 131, `max_strength` 124, `weight` 124, `manpower` 122, `default_morale` 122, `training_time` 120, `supply_consumption` 118 and `combat_width` 113 of 158, which fits. [vanilla-confirmed 1.19.4.1]
<!-- kit:end id="unit-stat-values" -->

## Modifiers <a id="Modifiers"></a>

The following list is all the valid modifiers for use in units (and equipment):

### Base <a id="Base"></a>

```text
max_organisation = 20           # Organisation indicates combat readiness and how organized a unit is.
                                # Units with no organisation can't fight or move effectively.

reliability = 0.9               # Reliability controls how often equipment will suffer random failures.

weight = 0.1                    # Weight controls how many transports a unit needs to embark.

maximum_speed = 0.5             # Maximum speed acts as a "bonus" mulitipler to the speed determined by the unit equipment in km/h.
                                # The formula for the calculated speed is <base speed> * (1 + maximum_speed)km/h; thus a maximum_speed
                                # of 0.5 gives a movement speed 50% faster, a maximum_speed of 2 equals 200% faster, etc.

supply_consumption = 0.02       # Supply consumption determmines how much supply a unit consumes per day

default_morale = 0.3            # Default morale determines how much extra organisation can be regained
                                # hourly when not in combat

combat_width = 0.5              # Combat width determines how much this unit contributes to overall combat width.
```

### Costs <a id="Costs"></a>

```text
lend_lease_cost = 1             # Space taken up in convoy
build_cost_ic = 0.4             # Production Cost - How much factory output this piece of equipment needs
manpower = 300                  # Manpower - Cost in manpower to produce
training_time = 120             # Training time - Time in days to train this unit
```

### Offensive <a id="Offensive"></a>

```text
# Offensive
attack = 0.1                    # Firepower - Amount of damage done per attack
soft_attack = -0.1              # Soft Attack - How many attacks the unit can make versus enemies with low hardness. (In this example here, this would mean that the unit would get 10% less Soft Attack than they
would usually get from its equipment
hard_attack = -0.5              # Hard Attack - How many attacks the unit can make versus enemies with high hardness
air_attack = 1                  # Air Attack - How much damage we can do against airplanes. High Air Attack also helps to counter enemy Air Superiority effects
ap_attack = 1                   # Piercing - Having equal or greater Piercing to the targets Armor value allows you to do more damage.
breakthrough = 0.5              # Breakthrough - How many enemy attacks a unit can attempt to avoid while on the offensive, effectively allowing it to stay on the offense longer.
```

### Defensive <a id="Defensive"></a>

```text
# Defensive
defense = 0.1                   # Defense - How many enemy attacks a unit can avoid whilst on the defensive, effectively allowing it to stay on the defensive longer.
max_strength = 2                # HP - Strength represents how much damage this unit can suffer before it is destroyed
armor_value = 0                 # Armor - Armor that is higher than the opponents Piercing value reduces damage taken and allows more attacks to occur
hardness = 0.5                  # Hardness - Represents how much of your divsion is made up of armoured vehicles. High Hardness = High Hard Attacks, Low Soft Attack
entrenchment = 5                # Entrenchment - The ability to make proper defensive entrenchments before a hostile attack
```

### Unique <a id="Unique"></a>

```text
movement = 0.1                  # Movement - Changes the unit's speed
experience_loss_factor = 0.1    # Exp. Loss - How much experience is lost in a division when they take casualities and have to replace them
casualty_trickleback = 0.2      # Trickleback - The proportion of losses in combat that can be saved and returned to the manpower pool
suppression_factor = 0.1        # Suppression bonus - Ability to supress local resistance
reliability_factor = 0.05       # Reliability - Applies to an equipment type's reliability and reduces the chance of breakdowns and accidents
recon = 1                       # Reconnaissance - Increases the chance that this unit can pick better tactics in battle
initiative = 0.2                # Initiative - The higher the initiative, the quicker it can reinforce into battle, and the quick is completes its planning
```

### Boolean <a id="Boolean"></a>

<!-- kit:begin id="unit-boolean-note" at="heading:Boolean" -->
**Kit correction** Only `can_be_parachuted` is a sub-unit key (57 vanilla sub-units). `can_license`, `is_convertable` and `carrier_capable` are equipment keys: vanilla sets them on equipment (`can_license` 5 blocks, `is_convertable` 25, `carrier_capable` 11) and on no sub-unit. Other boolean sub-unit keys that vanilla uses are `affects_speed`, `regimental`, `divisional`, `is_artillery_brigade`, `special_forces`, `marines`, `cavalry`, `mountaineers`, `rangers` and `can_exfiltrate_from_coast`. [vanilla-confirmed 1.19.4.1] `common/units/*.txt`, `common/units/equipment/*.txt`
<!-- kit:end id="unit-boolean-note" -->

```text
can_be_parachuted = yes         # May be parachuted into battle
can_license = yes                # Can be licesed
is_convertable = yes            # Can be converted
carrier_capable = yes           # Is usable in carriers (air only)
```

### Navy-specific <a id="Navy-specific"></a>

<!-- kit:begin id="unit-navy-air-note" at="heading:Navy-specific" -->
**Kit correction** None of the names in this section or in "Air-specific" is a sub-unit key in vanilla: `naval_speed`, `torpedo_attack`, `anti_air_attack`, `surface_detection`, `naval_range`, `air_range`, `air_agility`, `air_bombing`, `air_superiority`, `carrier_size` and the others are equipment stats (all in `script_enum_equipment_stat`), set in `common/units/equipment/` and on modules. No vanilla sub-unit sets any of them, except `air_attack`, which 11 land anti-air sub-units set as a damage stat against planes. Whether the engine would accept them on a sub-unit was not tested. Four names in this list do not exist at all in 1.19.4.1: `fire_range`, `shore_bombardment`, `evasion` and `port_capacity_usage` (see the Equipment modding page for the evidence). Do not write them. Real sub-unit stats for ships are `max_organisation` and `supply_consumption`, plus the damage model keys `critical_parts`, `critical_part_damage_chance_mult` and `hit_profile_mult`. [vanilla-confirmed 1.19.4.1] `common/units/submarine.txt`, `common/units/battleship.txt`, `common/script_enums.txt`; the engine behaviour [unverified]
<!-- kit:end id="unit-navy-air-note" -->

```text
naval_speed = 28                        # Max Speed - maximum speed in kilometres per hour of the ship, higher means faster in combat too
fire_range = 32                         # Fire Range - The range of the ship's main guns
torpedo_attack = 1                      # Torpedo attack - How much damage we can do when using the ship's torpedos
anti_air_attack = 5                     # Anti-air - How much anti-air firepower the ship carries for shooting down enemy planes
shore_bombardment = 8                   # Shore Bombard - A unit's ability to do shore bombardment to help out in land battles neighbouring its sea province when on Hold mission
evasion = 15                            # Evasion - Ability for ships to evade enemy fire through maneuvering. Evasion is checked against enemy evasion, so high evasion improves hits against high evasion targets
surface_detection = 12                  # Surface detection - Ability to detect surface vessels
sub_detection = 5                       # Sub detection - Ability to detect submarines
surface_visibility = 25                 # Surface Visibility - How hard to find this ship is
sub_visibility = 20                     # Sub Visibility - How easy it is to detect this submarine
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
air_bombing = 300                       # Strategic Bombing - how good the plane is at bombing
air_superiority = 1                     # Air Superiority - How much the plane helps the overall air superiority of a strategic area
naval_strike_attack = 1.5               # Naval Attack - how much damage the plane does against ships
naval_strike_targetting = 0.5           # Naval Targeting - how likely the plane is to hit a ship
carrier_size = 0.05
default_carrier_composition_weight = 1
```

## Localization <a id="Localization"></a>

Each unit must be localized in a *.yml* file in the *localisation* folder within your mod.

```text
<unit>: ""
<unit>_desc: ""
```

## Icons <a id="Icons"></a>

When adding a new unit it may appear, that your unit gets random icons in the division designer (like anti air icon, or what ever)
This is caused, because the actual unit has no icon. You can provide sprites in `/Hearts of Iron IV/gfx/interface/counters`.
Create a new gfx file for your new unit. Add the following content for each unit in `/Hearts of Iron IV/interface/subuniticons.gfx`

```text
spriteTypes = {

   spriteType = {
     name = "GFX_unit_<your unit name>_icon_medium"
     textureFile = "gfx/interface/counters/divisions_large/<your unit name>_icon.dds"  ## Thats the paradox shepe, but you can use any path and file naming you want
     noOfFrames = 2
   }

   spriteType = {
     name = "GFX_unit_<your unit name>_icon_medium_white" # Do not omit "medium"
     textureFile = "gfx/interface/counters/divisions_small/onmap_unit_<your unit name>_icon.dds"
     noOfFrames = 2
   }

   spriteType = {
     name = "GFX_unit_<your unit name>_icon_small"
     texturefile = "gfx/texticons/unit_<your unit name>_icon_small.dds"
     legacy_lazy_load = no
     noOfFrames = 2
   }

}
```

<!-- kit:begin id="unit-icons-note" at="section:Icons" -->
**Kit addition** In `interface/subuniticons.gfx` vanilla defines three sprite suffixes per sub-unit: `GFX_unit_<name>_icon_medium` (184 sprites, `divisions_large` art, 2 frames), `GFX_unit_<name>_icon_medium_white` (138, `divisions_small/onmap_` art) and `GFX_unit_<name>_icon_medium_black` (12). The `_small` sprite the template shows is not in that file. Group icons use `GFX_group_<group>_icon` (6 of the 7 groups; `support` has none). [vanilla-confirmed 1.19.3] `interface/subuniticons.gfx`
<!-- kit:end id="unit-icons-note" -->

---

## Navigation

**[Modding](<modding.md>)**

- **Documentation**: [Effects](<effects.md>) • [Triggers](<triggers.md>) • [Defines](<defines.md>) • [Modifiers](<modifiers.md>) • [List of modifiers](<list_of_modifiers.md>) • [Scopes](<scopes.md>) • [Localisation](<localisation.md>) • [On actions](<on_actions.md>) • [Data structures](<data_structures.md>) • [Flags](<data_structures.md#Flags>) • [Event targets](<data_structures.md#Event_targets>) • [Country tag aliases](<data_structures.md#Country_tag_aliases>) • [Variables](<data_structures.md#Variables>) • [Arrays](<data_structures.md#Arrays>)
- **Scripting**: [Achievements](<achievement_modding.md>) • [AI](<ai_modding.md>) • [AI focuses](<ai_focuses.md>) • [Autonomous states](<autonomy_state_modding.md>) • [Balances of power](<balance_of_power_modding.md>) • [Bookmarks/Scenarios](<bookmark_modding.md>) • [Game rules](<bookmark_modding.md#Game_rules>) • [Buildings](<building_modding.md>) • [Characters and traits](<character_modding.md>) • [Cosmetic tags](<cosmetic_tag_modding.md>) • [Countries](<country_creation.md>) • [Divisions](<division_modding.md>) • [Decisions](<decision_modding.md>) • [Doctrines](<doctrine_modding.md>) • [Equipment](<equipment_modding.md>) • [Events](<event_modding.md>) • [Factions](<faction_modding.md>) • [Ideas](<idea_modding.md>) • [Ideologies](<ideology_modding.md>) • [Military industrial organizations](<military_industrial_organization_modding.md>) • [National focuses](<national_focus_modding.md>) • [Resources](<resources_modding.md>) • [Scripted GUI](<scripted_gui_modding.md>) • [Technologies and doctrines](<technology_modding.md>)
- **Map**: [Map](<map_modding.md>) • [States](<state_modding.md>) • [Supply areas](<supply_areas_modding.md>) • [Strategic regions](<strategic_region_modding.md>)
- **Graphical**: [Interface](<interface_modding.md>) • [Graphical assets](<graphical_asset_modding.md>) • [Entities](<entity_modding.md>) • [Posteffects](<posteffect_modding.md>) • [Particles](<particle_modding.md>) • [Fonts](<font_modding.md>)
- **Cosmetic**: [Portraits](<portrait_modding.md>) • [Namelists](<namelist_modding.md>) • [Music](<music_modding.md>) • [Sound](<sound_modding.md>)
- **Other**: [Console commands](<console_commands.md>) • [Troubleshooting](<troubleshooting.md>) • [Mod structure](<mod_structure.md>) • [Mods](<mods.md>) • [Nudger](<nudger.md>)
- **Kit pages (not on the wiki)**: [Collection modding](<collection_modding.md>) • [Defines additions](<defines_additions.md>) • [Game rule modding](<game_rule_modding.md>) • [Intelligence operation modding](<intelligence_operation_modding.md>) • [Map mode modding](<map_mode_modding.md>) • [Occupation and resistance modding](<occupation_and_resistance_modding.md>) • [Peace conference modding](<peace_conference_modding.md>) • [Raid modding](<raid_modding.md>) • [Script constant modding](<script_constant_modding.md>) • [Special project modding](<special_project_modding.md>)
