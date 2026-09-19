# Equipment modding

*Offline snapshot of the Hearts of Iron IV Wiki page "Equipment modding", captured 2026-09-19.*

## Table of contents

- [Equipment](#Equipment)
  - [Internal Types](#Internal_Types)
    - [Land](#Land)
    - [Naval](#Naval)
    - [Air](#Air)
  - [Group By types](#Group_By_types)
  - [Interface Categories](#Interface_Categories)
  - [Equipment Designer](#Equipment_Designer)
- [Stats](#Stats)
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

### Equipment <a id="Equipment"></a>

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

#### Internal Types <a id="Internal_Types"></a>

##### Land <a id="Land"></a>

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

##### Naval <a id="Naval"></a>

- capital_ship
- carrier
- convoy
- naval_transport
- screen_ship
- submarine

##### Air <a id="Air"></a>

- air_transport
- cas
- fighter
- interceptor
- tactical_bomber
- missile
- naval_bomber
- strat_bomber
- suicide

#### Group By types <a id="Group_By_types"></a>

- archetype
- type

#### Interface Categories <a id="Interface_Categories"></a>

- interface_category_land
- interface_category_armor
- interface_category_capital_ships
- interface_category_screen_ships
- interface_category_other_ships
- interface_category_air

#### Equipment Designer <a id="Equipment_Designer"></a>

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

### Stats <a id="Stats"></a>

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

### Modifiers <a id="Modifiers"></a>

The following list is all the valid modifiers for use in equipment (and units):

#### All <a id="All"></a>

```text
lend_lease_cost = 1             # Space taken up in convoy
build_cost_ic = 0.4             # Production Cost - How much factory output this piece of equipment needs
manpower = 300                  # Manpower - Cost in manpower to produce
can_license = no                # Can be licensed
is_convertable = yes            # Can be converted
```

#### Land <a id="Land_2"></a>

##### Base <a id="Base"></a>

```text
reliability = 0.9               # Reliability - The lower the reliability, the more likely the equipment will suffer random failure
maximum_speed = 4               # Max Speed - How quickly this unit can traverse terrain under optimal circumtances, in kilometres per hour
```

##### Offensive <a id="Offensive"></a>

```text
## Offensive
soft_attack = -0.1              # Soft Attack - How many attacks the unit can make versus enemies with low hardness
hard_attack = -0.5              # Hard Attack - How many attacks the unit can make versus enemies with high hardness
air_attack = 1                  # Air Attack - How much damage we can do against airplanes. High Air Attack also helps to counter enemy Air Superiority effects
ap_attack = 1                   # Piercing - Having equal or greater Piercing to the targets Armor value allows you to do more damage.
breakthrough = 0.5              # Breakthrough - How many enemy attacks a unit can attempt to avoid while on the offensive, effectively allowing it to stay on the offense longer.
```

##### Defensive <a id="Defensive"></a>

```text
## Defensive
defense = 0.1                   # Defense - How many enemy attacks a unit can avoid whilst on the defensive, effectively allowing it to stay on the defensive longer.
max_strength = 2                # HP - Strength represents how much damage this unit can suffer before it is destroyed
armor_value = 0                 # Armor - Armor that is higher than the opponents Piercing value reduces damage taken and allows more attacks to occur
hardness = 0.5                  # Hardness - Represents how much of your divsion is made up of armoured vehicles. High Hardness = High Hard Attacks, Low Soft Attack
entrenchment = 5                # Entrenchment - The ability to make proper defensive entrenchments before a hostile attack
```

##### Unique <a id="Unique"></a>

```text
recon = 1                       # Reconnaissance - Increases the chance that this unit can pick better tactics in battle
```

#### Navy-specific <a id="Navy-specific"></a>

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

#### Air-specific <a id="Air-specific"></a>

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

### Localization <a id="Localization"></a>

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

---

## Navigation

**[Modding](<Modding - Hearts of Iron 4 Wiki.md>)**

- **Documentation**: [Effects](<Effects - Hearts of Iron 4 Wiki.md>) • [Triggers](<Triggers - Hearts of Iron 4 Wiki.md>) • [Defines](<Defines - Hearts of Iron 4 Wiki.md>) • [Modifiers](<Modifiers - Hearts of Iron 4 Wiki.md>) • [List of modifiers](<List of modifiers - Hearts of Iron 4 Wiki.md>) • [Scopes](<Scopes - Hearts of Iron 4 Wiki.md>) • [Localisation](<Localisation - Hearts of Iron 4 Wiki.md>) • [On actions](<On actions - Hearts of Iron 4 Wiki.md>) • [Data structures](<Data structures - Hearts of Iron 4 Wiki.md>) • [Flags](<Data structures - Hearts of Iron 4 Wiki.md#Flags>) • [Event targets](<Data structures - Hearts of Iron 4 Wiki.md#Event_targets>) • [Country tag aliases](<Data structures - Hearts of Iron 4 Wiki.md#Country_tag_aliases>) • [Variables](<Data structures - Hearts of Iron 4 Wiki.md#Variables>) • [Arrays](<Data structures - Hearts of Iron 4 Wiki.md#Arrays>)
- **Scripting**: [Achievements](<Achievement modding - Hearts of Iron 4 Wiki.md>) • [AI](<AI modding - Hearts of Iron 4 Wiki.md>) • [AI focuses](<AI focuses - Hearts of Iron 4 Wiki.md>) • [Autonomous states](<Autonomy state modding - Hearts of Iron 4 Wiki.md>) • [Balances of power](<Balance of power modding - Hearts of Iron 4 Wiki.md>) • [Bookmarks/Scenarios](<Bookmark modding - Hearts of Iron 4 Wiki.md>) • [Game rules](<Bookmark modding - Hearts of Iron 4 Wiki.md#Game_rules>) • [Buildings](<Building modding - Hearts of Iron 4 Wiki.md>) • [Characters and traits](<Character modding - Hearts of Iron 4 Wiki.md>) • [Cosmetic tags](<Cosmetic tag modding - Hearts of Iron 4 Wiki.md>) • [Countries](<Country creation - Hearts of Iron 4 Wiki.md>) • [Divisions](<Division modding - Hearts of Iron 4 Wiki.md>) • [Decisions](<Decision modding - Hearts of Iron 4 Wiki.md>) • [Doctrines](<Doctrine modding - Hearts of Iron 4 Wiki.md>) • [Events](<Event modding - Hearts of Iron 4 Wiki.md>) • [Factions](<Faction modding - Hearts of Iron 4 Wiki.md>) • [Ideas](<Idea modding - Hearts of Iron 4 Wiki.md>) • [Ideologies](<Ideology modding - Hearts of Iron 4 Wiki.md>) • [Military industrial organizations](<Military industrial organization modding - Hearts of Iron 4 Wiki.md>) • [National focuses](<National focus modding - Hearts of Iron 4 Wiki.md>) • [Resources](<Resources modding - Hearts of Iron 4 Wiki.md>) • [Scripted GUI](<Scripted GUI modding - Hearts of Iron 4 Wiki.md>) • [Technologies and doctrines](<Technology modding - Hearts of Iron 4 Wiki.md>) • [Units](<Unit modding - Hearts of Iron 4 Wiki.md>)
- **Map**: [Map](<Map modding - Hearts of Iron 4 Wiki.md>) • [States](<State modding - Hearts of Iron 4 Wiki.md>) • [Supply areas](<Supply areas modding - Hearts of Iron 4 Wiki.md>) • [Strategic regions](<Strategic region modding - Hearts of Iron 4 Wiki.md>)
- **Graphical**: [Interface](<Interface modding - Hearts of Iron 4 Wiki.md>) • [Graphical assets](<Graphical asset modding - Hearts of Iron 4 Wiki.md>) • [Entities](<Entity modding - Hearts of Iron 4 Wiki.md>) • [Posteffects](<Posteffect modding - Hearts of Iron 4 Wiki.md>) • [Particles](<Particle modding - Hearts of Iron 4 Wiki.md>) • [Fonts](<Font modding - Hearts of Iron 4 Wiki.md>)
- **Cosmetic**: [Portraits](<Portrait modding - Hearts of Iron 4 Wiki.md>) • [Namelists](<Namelist modding - Hearts of Iron 4 Wiki.md>) • [Music](<Music modding - Hearts of Iron 4 Wiki.md>) • [Sound](<Sound modding - Hearts of Iron 4 Wiki.md>)
- **Other**: [Console commands](<Console commands - Hearts of Iron 4 Wiki.md>) • [Troubleshooting](<Troubleshooting - Hearts of Iron 4 Wiki.md>) • [Mod structure](<Mod structure - Hearts of Iron 4 Wiki.md>) • [Mods](<Mods - Hearts of Iron 4 Wiki.md>) • [Nudger](<Nudger - Hearts of Iron 4 Wiki.md>)
