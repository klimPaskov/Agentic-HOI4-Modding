# Table of contents

- [Equipment](#equipment)
  - [Internal Types](#internal-types)
    - [Land](#land)
    - [Naval](#naval)
    - [Air](#air)
  - [Group By types](#group-by-types)
  - [Interface Categories](#interface-categories)
- [Stats](#stats)
- [Modifiers](#modifiers)
  - [All](#all)
  - [Land](#land)
    - [Base](#base)
    - [Offensive](#offensive)
    - [Defensive](#defensive)
    - [Unique](#unique)
  - [Navy-specific](#navy-specific)
  - [Air-specific](#air-specific)
- [Localization](#localization)


---

## Equipment

Equipment is found in /Hearts of Iron IV/common/units/equipment/\*.txt. Equipment is split into two types, archetype and regular. Archetype equipment is used to assign more general attributes that regular equipment then inherits via the *archetype* attribute.

Archetype equipment follows the following format:

```text
equipments = {
	<equipment> = {
		year = <int>		# Limits the equipment from appearing before the specified year. Optional
		picture = <name>	# GFX reference used to define equipment picture in lend-lease
		
		can_be_produced = {	# Optional, specifies when equipment of this category can be produced.
			<triggers>
		}
		
		is_archetype = yes	# Specifies an entry as an archetype entry. All non-archetype entries inherit 
		is_buildable = no	# Prevents this equipment from being built.
		active = yes		# Determines if this equipment is available without unlocking from a technology.
		
		type = <type>	   	# Internal type: what kind of unit can use this equipment

		group_by = <group>			  # How the equipment is grouped in the production screen
		interface_category = <type>	 # Which category the equipment appears in the production screen
		
		# Resources used to build this equipment
		resources = {
			<resource> = <amount>
		}
		
		# Modifiers the equipment uses
		<modifiers> 
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

### Internal Types

#### Land

- anti\_air
- anti\_tank
- armor
- artillery
- heavy\_tank\_chassis
- infantry
- light\_tank\_chassis
- mechanized
- medium\_tank\_chassis
- motorized
- rocket
- support\_equipment

#### Naval

- capital\_ship
- carrier
- convoy
- naval\_transport
- screen\_ship
- submarine

#### Air

- air\_transport
- cas
- fighter
- interceptor
- tactical\_bomber
- missile
- naval\_bomber
- strat\_bomber
- suicide

### Group By types

- archetype
- type

### Interface Categories

- interface\_category\_land
- interface\_category\_armor
- interface\_category\_capital\_ships
- interface\_category\_screen\_ships
- interface\_category\_other\_ships
- interface\_category\_air

## Stats

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

Note that the default *maximum\_speed* is 4, so you don't need to include it when you want equipment to confer the default *maximum\_speed*.

## Modifiers

The following list is all the valid modifiers for use in equipment (and units):

### All

```text
lend_lease_cost = 1             # Space taken up in convoy
build_cost_ic = 0.4             # Production Cost - How much factory output this piece of equipment needs
manpower = 300                  # Manpower - Cost in manpower to produce
can_license = no                # Can be licensed
is_convertable = yes            # Can be converted
```

### Land

#### Base

```text
reliability = 0.9               # Reliability - The lower the reliability, the more likely the equipment will suffer random failure
maximum_speed = 4               # Max Speed - How quickly this unit can traverse terrain under optimal circumtances, in kilometres per hour
```

#### Offensive

```text
# Offensive
soft_attack = -0.1              # Soft Attack - How many attacks the unit can make versus enemies with low hardness
hard_attack = -0.5              # Hard Attack - How many attacks the unit can make versus enemies with high hardness
air_attack = 1                  # Air Attack - How much damage we can do against airplanes. High Air Attack also helps to counter enemy Air Superiority effects
ap_attack = 1                   # Piercing - Having equal or greater Piercing to the targets Armor value allows you to do more damage.
breakthrough = 0.5              # Breakthrough - How many enemy attacks a unit can attempt to avoid while on the offensive, effectively allowing it to stay on the offense longer.
```

#### Defensive

```text
# Defensive
defense = 0.1                   # Defense - How many enemy attacks a unit can avoid whilst on the defensive, effectively allowing it to stay on the defensive longer.
max_strength = 2                # HP - Strength represents how much damage this unit can suffer before it is destroyed
armor_value = 0                 # Armor - Armor that is higher than the opponents Piercing value reduces damage taken and allows more attacks to occur
hardness = 0.5                  # Hardness - Represents how much of your divsion is made up of armoured vehicles. High Hardness = High Hard Attacks, Low Soft Attack
entrenchment = 5                # Entrenchment - The ability to make proper defensive entrenchments before a hostile attack
```

#### Unique

```text
recon = 1                       # Reconnaissance - Increases the chance that this unit can pick better tactics in battle
```

### Navy-specific

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

### Air-specific

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

## Localization

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

**[Modding](<Modding - Hearts of Iron 4 Wiki.md>)**
