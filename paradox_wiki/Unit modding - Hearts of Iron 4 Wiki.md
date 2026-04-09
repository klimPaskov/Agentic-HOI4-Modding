# Table of contents

- [Unit Categories](#unit-categories)
- [Units](#units)
  - [How to add new Groups](#how-to-add-new-groups)
  - [Models](#models)
  - [Internal Types](#internal-types)
  - [Group Types](#group-types)
  - [Map Icon Types](#map-icon-types)
- [Stats](#stats)
- [Modifiers](#modifiers)
  - [Base](#base)
  - [Costs](#costs)
  - [Offensive](#offensive)
  - [Defensive](#defensive)
  - [Unique](#unique)
  - [Boolean](#boolean)
  - [Navy-specific](#navy-specific)
  - [Air-specific](#air-specific)
- [Localization](#localization)
- [Icons](#icons)


---

Units are the base object that equipment is applied to. Internally, units are actually sub-units of the hardcoded unit types, such as infantry, cavalry, fighter, etc.

## Unit Categories

Unit categories are found in /Hearts of Iron IV/common/unit\_tags/00\_categories.txt.

Each unit is assigned a category that is used in technologies to apply effects to groups of units at once.

The following example from a technology grants bonuses to all units with the *category\_all\_infantry* category:

```text
category_all_infantry = {
    hard_attack = 0.25
    ap_attack = 1
}
```

## Units

Units are found in /Hearts of Iron IV/common/units/\*.txt.

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

### How to add new Groups

Inside any unit file, type the name of the new group in the "group" argument. The game will internally create the group and asign it to the current unit. For example:

```text
group = <group name>
```

Then, to add a localisation for our newly created group we must go to any localization file (preferably /Hearts of Iron IV/localisation/unit\_I\_english.yml) and define a new loc key as follows:

```text
group_<group name>_title:0 "Group name here"
```

To assign an icon to the new group you must go to /Hearts of Iron IV/interface/subuniticons.gfx and define a new spritetype as follows:

```text
spriteType = { name = "GFX_group_<group name>_icon"	     textureFile = "gfx/interface/counters/divisions_large/<icon file name>.dds" noOfFrames = 2 }
```

Note that the textureFile path doesn't have to be strictly /Hearts of Iron IV/gfx/interface/counters/divisions\_large/, it can be any path.

### Models

*See also: [Entity modding](<Entity modding - Hearts of Iron 4 Wiki.md>)*

The model is assigned with the `sprite = SPRITE` attribute, which assigns the entity with the base name of `SPRITE_entity` by default to units whose division template has a plurality of this sub-unit. Similar to [country names](<Country creation - Hearts of Iron 4 Wiki.md#name>), it is possible to assign further conditions by changing the name of the model, in this case by prepending a prefix to the base name. The priority starts with the default name as the lowest, then allowing using unique models for [graphical cultures](<Country creation - Hearts of Iron 4 Wiki.md#country-file>), countries, or cosmetic tags.

An example /Hearts of Iron IV/gfx/entities/\*.asset file is as such:

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

### Internal Types

- infantry
- support
- artillery
- anti\_tank
- anti\_air
- armor
- fighter
- cas
- naval\_bomber
- interceptor
- suicide
- tactical\_bomber
- strategic\_bomber
- air\_transport
- missile
- submarine
- screen\_ship
- capital\_ship
- carrier
- motorized
- mechanized
- flame
- amphibious

### Group Types

- infantry
- support
- mobile
- armor

### Map Icon Types

- infantry
- armored
- other
- ship
- transport
- uboat

## Stats

Units use modifiers to determine which stats they have and what special actions they may take.

Typically air units will not use any modifiers, whilst naval units use only *supply\_consumption* and *max\_organisation*.

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

For *max\_organisation*, vanilla uses the following values:

- infantry support: 20
- armor: 10
- armor support: 0
- ship: 40
- cavalry: 70

For *combat\_width*, vanilla uses the following values:

- infantry: 0
- artillery: 0
- armor support: 1
- armor: 2

## Modifiers

The following list is all the valid modifiers for use in units (and equipment):

### Base

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

### Costs

```text
lend_lease_cost = 1             # Space taken up in convoy
build_cost_ic = 0.4             # Production Cost - How much factory output this piece of equipment needs
manpower = 300                  # Manpower - Cost in manpower to produce
training_time = 120             # Training time - Time in days to train this unit
```

### Offensive

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

### Defensive

```text
# Defensive
defense = 0.1                   # Defense - How many enemy attacks a unit can avoid whilst on the defensive, effectively allowing it to stay on the defensive longer.
max_strength = 2                # HP - Strength represents how much damage this unit can suffer before it is destroyed
armor_value = 0                 # Armor - Armor that is higher than the opponents Piercing value reduces damage taken and allows more attacks to occur
hardness = 0.5                  # Hardness - Represents how much of your divsion is made up of armoured vehicles. High Hardness = High Hard Attacks, Low Soft Attack
entrenchment = 5                # Entrenchment - The ability to make proper defensive entrenchments before a hostile attack
```

### Unique

```text
movement = 0.1                  # Movement - Changes the unit's speed
experience_loss_factor = 0.1    # Exp. Loss - How much experience is lost in a division when they take casualities and have to replace them
casualty_trickleback = 0.2      # Trickleback - The proportion of losses in combat that can be saved and returned to the manpower pool
suppression_factor = 0.1        # Suppression bonus - Ability to supress local resistance
reliability_factor = 0.05       # Reliability - Applies to an equipment type's reliability and reduces the chance of breakdowns and accidents
recon = 1                       # Reconnaissance - Increases the chance that this unit can pick better tactics in battle
initiative = 0.2                # Initiative - The higher the initiative, the quicker it can reinforce into battle, and the quick is completes its planning
```

### Boolean

```text
can_be_parachuted = yes         # May be parachuted into battle
can_license = yes                # Can be licesed
is_convertable = yes            # Can be converted
carrier_capable = yes           # Is usable in carriers (air only)
```

### Navy-specific

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

### Air-specific

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

## Localization

Each unit must be localized in a *.yml* file in the *localisation* folder within your mod.

```text
<unit>: ""
<unit>_desc: ""
```

## Icons

When adding a new unit it may appear, that your unit gets random icons in the division designer (like anti air icon, or what ever)
This is caused, because the actual unit has no icon. You can provide sprites in /Hearts of Iron IV/gfx/interface/counters.
Create a new gfx file for your new unit. Add the following content for each unit in /Hearts of Iron IV/interface/subuniticons.gfx

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

**[Modding](<Modding - Hearts of Iron 4 Wiki.md>)**
