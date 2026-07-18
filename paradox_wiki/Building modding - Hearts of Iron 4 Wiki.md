# Table of contents

- [Buildings](#buildings)
  - [Cost](#cost)
  - [Slots](#slots)
  - [Modifiers](#modifiers)
  - [Additional arguments](#additional-arguments)
  - [Icon](#icon)
  - [Models](#models)
  - [Effects](#effects)
  - [Example](#example)
- [Spawn point](#spawn-point)
- [Localization](#localization)
- [Types](#types)
- [References](#references)

---

A building is a structure built using Civilian factories in states or provinces.

## <a id="buildings"></a>Buildings

Buildings are defined within /Hearts of Iron IV/common/buildings/\*.txt. Each building entry lies within the `buildings = { ... }` block, serving as its own block with arguments within defining the building, as this:

```text
buildings = {
    my_building = {
        <...>
    }
}
```

### <a id="cost"></a>Cost

Each building has a set price in industrial capacity required.

This cost is defined with:

- `base_cost = <int>` - Required base cost of building.
- `per_level_extra_cost = <int>` - Optional additional cost per building in state/province.
- `per_controlled_building_extra_cost = <int>` - Optional additional cost per building controlled by country.

`base_cost` is the primary cost to build the building, added to each building level, `per_level_extra_cost` gets added for each building level in state or province in an arithmetic progression. With the example of 1000 base\_cost and 100 per\_level\_extra\_cost, the first level will cost 1000 IC to build, while the 5th level will cost 1400 IC, as 4 levels have been built before that. `per_controlled_building_extra_cost` adds additional cost per building controlled by country.

By default, each civilian factory provides 4 IC per day<a id="cite-ref-1"></a>[[1]](#cite-note-1), which can be taken into account when calculating the cost. For comparison, by default a civilian factory costs 10800 IC, while infrastructure costs 6000 IC.

Additionally, `infrastructure_construction_effect = yes`, if included, will make the building get the building speed boost from any infrastructure built in the state. Maximum infrastructure level increase buidling speed by factor of 1<a id="cite-ref-2"></a>[[2]](#cite-note-2). Dividing that value by `level_cap` of infrastructure (5) gives a +20% boost per infastructure level.

### <a id="slots"></a>Slots

In general, buildings fall into 3 categories by used building slots:

- Shared, which use the same, by default, 25 shared slots<a id="cite-ref-3"></a>[[3]](#cite-note-3) for each state, such as civilian and military factories.
- Non-shared, defined for states, but using slots that are unique for each building in particular, such as infrastructure or air bases.
- Provincial, which get built for each province, using slots that are unique for each building in particular, such as forts or naval bases.

The 3 categories have separate zones in the country construction view where they are located.

Slot for building is defined inside `level_cap` block. Which possible parameters are:

- `shares_slots = <bool>` - Wheter building should use shared slots for state.
- `state_max = <int>` - Maximum level in a state.
- `province_max = <int>` - Maximum level in a province. Defines building as provincial.
- `group_by = <string>` - Group of buildings, limiting all building with the same category to the same maximum used slots.
- `exclusive_with = <building_id>` - Prohibits the construction of certain buildings in the same state/province.

By default building is defined as state building. If `state_max` is unspecified, it gets assumed to be 15<a id="cite-ref-4"></a>[[4]](#cite-note-4) by default.

Additional maximum level limit for provincial buldings for each terrain type can be set within /Hearts of Iron IV/common/terrain/\*.txt files.

```text
buildings_max_level = {
  bunker = <int>
  coastal_bunker = <int>
}
```

By default, all levels of the building are unlocked by default. However, if there are [technologies](<Technology modding - Hearts of Iron 4 Wiki.md>) that enable construction of this building to a specified level, it becomes impossible to build without obtaining at least one of these technologies. It is to be noted that the [add\_building\_construction effect](<Effects - Hearts of Iron 4 Wiki.md#add-building-construction>) or the [starting state buildings](<State modding - Hearts of Iron 4 Wiki.md#buildings>) can still be used to bypass the technological limit, while still not being possible to bypass the max level total.

### <a id="modifiers"></a>Modifiers

Bulding can provide modifiers to country or/and state:

- `country_modifiers = { modifiers = { ... } }` - Accept only country modifiers.
- `state_modifiers = { ... }` - Accept only state modifiers.

Country modifiers can be restricted to specific countries by `enable_for_controllers = { ... }` list of tags block inside `country_modifiers`. Modifiers will apply only if the controller of province/state is in the list, or if the list is empty.

Adding `show_modifier = yes` will make the modifiers show up in the tooltip of the building.

Example:

```text
building = {
  country_modifiers = {
    enable_for_controllers { GER ENG }
    modifiers = {
       political_power_factor = 2.0
    }
  }
  state_modifiers = {
    local_building_slots_factor = 2
  }
}
```

### <a id="additional-arguments"></a>Additional arguments

Common arguments applicable to every building:

- `dlc_allowed = { ... }` - Limit building to specific dlc. Uses has\_dlc trigger.
- `special_icon = <int>` - Used to display icons for specific buildings starting from the left side of the terrain interface within the state interface.(See provinces with facilities for details.)
- `value = 3` - Decides the base health of a building for air bombing campaigns, which gets multiplied for each level of the building. Additionally, this also determines the price of the state to get during peace conferences or the cost in ![Political Power](media/building-modding-hearts-of-iron-4-wiki_811161eae8__img1.png) Political Power to occupy.
- `damage_factor = 0.3` - Modifies the damage that this building gets from air bombing or land combat. Positive values increase it, while negatives decrease it. At 0, building can't be damaged.
- `allied_build = <bool>` - If specified, makes the building count as an allied building, making its modifiers apply not just on the country that built it, but also its allies (i.e. subjects, overlord, and/or faction members).
- `only_costal = yes` (sic) - If specified, will make the building only be possible to build in either provinces that are [defined as coastal](<Map modding - Hearts of Iron 4 Wiki.md#province-map>) or states that contain any such provinces, depending on the type of the building.
- `disabled_in_dmz = <bool>` - If added, will make the building impossible to build or use in states that are demilitarised zones.
- `need_supply = <bool>` - Whether building needs supply for operation.
- `hide_if_missing_tech = <bool>` - Hides building in the construction tab if the required technology has not been researched.
- `missing_tech_loc = { ... }` - Custom localized tooltip when the required technology has not been researched.
- `need_detection = <bool>` - ?
- `detecting_intel_type = <intel_type>` - Define what type of intelligence affects this building.Types of intelligence available:`civilian`,`army`,`airforce`,`navy`
- `only_display_if_exists = <bool>` - The details of the building will only appear in the terrain interface of the province when it is constructed in a province of that state.(Usually used in conjunction with the special\_icon parameter mentioned above.)At the same time, the terrain interface maps of other provinces in the state will not show the icon of this building. If set to 'no', all provinces in the entire state will display the icon and detailed information of the building, but provinces without the building will show a level of 0, even though this building can only be constructed once within the same state.
- `specialization = { ... }` - Associate the types of special projects.Defined in this path:/Hearts of Iron IV/common/special\_projects/specialization/specializations.txt
- `tags = { ... }` - Building tags, used to target buildings in raids and in [damage\_building](<Effects - Hearts of Iron 4 Wiki.md#damage-building>) effect.
- `is_buildable = <bool>` - Whether building can be build manually. Default to yes.
- `province_damage_modifiers = { ... }` - Modifiers to add to province if building is damaged/destroyed. [Need confirmation]
- `state_damage_modifier = { ... }` - Modifiers to add to state if building is damaged/destroyed. [Need confirmation]
- `affects_energy = yes/no` - Determine whether the building will affect energy consumption.[Need confirmation]

### <a id="icon"></a>Icon

The building icon is defined as `icon_frame = 10`. The integer shows which frame within the GFX\_buildings\_strip sprite gets used for this building.

By default, GFX\_buildings\_strip is defined within /Hearts of Iron IV/interface/countrystateview.gfx, however, it can be overwritten in any /Hearts of Iron IV/interface/\*.gfx which is positioned later by filename order:

```text
spriteType = {
    name = "GFX_buildings_strip"
    textureFile = "gfx/interface/buildings/building_icon_strip.dds"
    noOfFrames = 16     # As of 1.11
}
```

The noOfFrames decides in how many frames the specified sprite is divided into, dividing the image horizontally into chunks of approximately equal width. If planning to add a new building icon rather than using a base game one, the building icon strip will need to be updated both in the noOfFrames and in the .dds file. By default, each building has a 46x46 resolution in pixels.

Within the building construction menu, buildings are divided into 3 zones depending on their used building slots category. In order to change where they are to adjust for new or missing buildings, the elements within the possible\_constructions container in /Hearts of Iron IV/interface/countryconstructionsview.gui can have their positions changed.

### <a id="models"></a>Models

*Main article: [Entity modding](<Entity modding - Hearts of Iron 4 Wiki.md>)*

There are several arguments related to models within buildings.  
`show_on_map = 3` decides how many building models should there be per state or per province (depending on the building type) defined for the building. Each building construction will add one more model. If unspecified, will have no map models.  
`show_on_map_meshes = 2` decides how many entities are used for each building model. By default assumed to be 1.  
`always_shown = yes`, if specified, will make the building model appear regardless whether it's covered by the fog of war or not.  
`has_destroyed_mesh = yes`, if specified, will make the game use a separate model if the building has been destroyed by air bombing or occupation.  
`centered = yes`, if specified, will mak

In order to assign an entity to a building, it must have a name of `building_<building name>`, like `building_my_building`, within the /Hearts of Iron IV/gfx/entities/\*.asset file. If a building is set to use several entities, then the number will get appended in the end like `building_my_building_1`, starting with 1. If there's a destroyed mesh, then it'll append \_destroyed in the end as `building_my_building_destroyed`

The locations of building models for each state are defined in /Hearts of Iron IV/map/buildings.txt. An entry in that file is defined as such (If unspecified, assume a number with up to 2 decimal digits):

`State ID (integer); building ID (string); X position; Y position; Z position; Rotation; Adjacent sea province (integer)`

- State ID defines which state the building is located in. Even for provincial buildings, this is the ID of the state, not the province. Instead, provincial buildings have several entries per state, with the XYZ position being used by the game to know which province it's for.
- Building ID is defines which model is being located. While this includes each building, this also includes floating harbours as floating\_harbor.
- X, Y, and Z position represent the position on the map of the building model using the 3-dimensional Cartesian coordinate system. The X and Z positions are equivalent to the X and Y axes on the province bitmap with 1 pixel equalling 1 unit, left-to-right and down-to-up respectively. This is also what the game uses to know which province it's for for provincial buildings. The Y position, on the scale of 0 to 25.5, can be calculated with the heightmap by taking the [colour value](http://en.wikipedia.org/wiki/Lightness) of the pixel at that position and making it fit on the scale of 0 to 25.5 (Such as by dividing it by 10 if it's on the scale of 0 to 255).
- Rotation is measured in radians. A rotation of 0 will result in the building model pointing in the same direction as the model is set, while positives will rotate it counter-clockwise and negatives will rotate it clockwise. A full rotation resulting in the same position as 0 is equal to the number π multiplied by 2, roughly 6.28.
- Adjacent sea province is only necessary to define for naval bases and floating harbours, in order to let the game know from which sea province ships or convoys can access the land province where it is located. If the building type is not a naval base, it should be left at 0.

It is preferable to generate the building models in the building section in the nudger, rather than filling it out manually. However, note that the game will crash if the currently-existing /Hearts of Iron IV/map/buildings.txt file is entirely empty, so there should be at least one definition, even if incorrect.

### <a id="effects"></a>Effects

Each building can accept any [state-scoped modifier](<Modifiers - Hearts of Iron 4 Wiki.md#state-scope>) within itself, applying that to the state when built. Some used in base game include `local_resources_<resource>`, `air_defence` (for anti-air) and `air_defence`. In case of provincial buildings, province-level modifiers are accepted instead. This can also be used with [modifier tokens](<Modifiers - Hearts of Iron 4 Wiki.md#modifier-tokens>) to create a custom effect as a variable system.

Aside from state-scoped modifiers, there are several other arguments to make the building have the same effect as a base game building or be considered one for the AI:
| Name | Effects | Examples | Type | Notes |
| --- | --- | --- | --- | --- |
| military\_production | Adds the specified amount of military factories to the controller. | `military_production = 0.5` | Flat. | A value that's larger than 1 will be the same as 1 factory, but it can fall between 0 and 1. |
| general\_production | Adds the specified amount of civilian factories to the controller. | `general_production = 0.5` | Flat. | A value that's larger than 1 will be the same as 1 factory, but it can fall between 0 and 1. |
| naval\_production | Adds the specified amount of dockyards to the controller. | `naval_production = 0.5` | Flat. | A value that's larger than 1 will be the same as 1 factory, but it can fall between 0 and 1. |
| infrastructure | Makes the building be marked as infrastructure. | `infrastructure = yes` | Boolean. | Includes the construction speed bonus and extra resources. |
| air\_base | Makes the building be marked as an air base. | `air_base = yes` | Boolean. |  |
| supply\_node | Makes the building be marked as a supply node. | `supply_node = yes` | Boolean. |  |
| is\_port | Makes the building be marked as a naval port. | `is_port = yes` | Boolean. |  |
| land\_fort | Adds that many land forts to the province. | `land_fort = 1` | Flat. |  |
| naval\_fort | Adds that many coastal forts to the province. | `naval_fort = 1` | Flat. |  |
| refinery | Makes the building be marked as a synthetic refinery. | `refinery = yes` | Boolean. |  |
| fuel\_silo | Makes the building be marked as a fuel silo. | `fuel_silo = yes` | Boolean. |  |
| radar | Makes the building be marked as a radar station. | `radar = yes` | Boolean. |  |
| rocket\_production | Defines how much progress on rocket production is done daily. | `rocket_production = 5` | Flat. |  |
| rocket\_launch\_capacity | Defines how many rockets the build can launch daily. | `rocket_launch_capacity = 5` | Flat. |  |
| nuclear\_reactor | Makes the building be marked as a nuclear reactor. | `nuclear_reactor = yes` | Boolean. |  |
| gun\_emplacement |  | `gun_emplacement = yes` | Boolean. |  |

### <a id="example"></a>Example

```text
buildings = {
    my_provincial_building = {
        base_cost = 10000
        infrastructure_construction_effect = yes
        
        value = 1
        
        icon_frame = 17
        
        show_on_map = 1
        always_shown = yes

        spawn_point = my_provincial_building_spawn

        country_modifiers = {
            modifiers = {
                army_attack_factor = 0.01
                army_defence_factor = 0.01
            }
        }

        level_cap = {
            province_max = 3
        }
    }
    my_shared_building = {
        base_cost = 1000
        per_level_extra_cost = 200
        infrastructure_construction_effect = yes
        
        value = 15
        only_costal = yes
        
        icon_frame = 18
        
        show_on_map = 3
        show_on_map_meshes = 3
        has_destroyed_mesh = yes
        
        military_production = 1
        general_production = 1
        naval_production = 1

        level_cap = {
            shares_slots = yes
            # Max level of 15 since undefined
        }
    }
    my_non_shared_building = {
        base_cost = 1000
        per_level_extra_cost = 2000
        
        max_level = 2
        
        value = 5
        
        icon_frame = 19     # No model is defined
        
        state_modifiers = {
            recruitable_population_factor = 0.5
        }

        level_cap = {
            state_max = 2
        }
    }
}
```

## <a id="spawn-point"></a>Spawn point

Coordinates for each building on map by default are defined using building name. Spawn point can be defined to to use 1 position for diffrent types of buildings.

Parameters:

- `type` - Can be `state` or `province`.
- `max = <int>` - How many spawn points state/province should have.
- `only_costal = <bool>` - Limit spawn point to coastal states/provinces.
- `disable_auto_nudging = <bool>` - Disable automatic positioning with nudging tool.

Example:

```text
spawn_points = {
  my_building_type_spawn = {
    type = state
    max = 1
  }
  my_province_building_type_spawn = {
    type = province
    max = 1
    only_costal = yes
  }
}
```

Now multiple buildings can use `spawn_point = my_building_type_spawn`.

## <a id="localization"></a>Localization

Buildings use the following localization keys, using my\_building as an example:

```text
 my_building: "My building"
 my_building_desc: "My building's description"
 my_building_plural: "My buildings"

 modifier_production_speed_my_building_factor: "§Y$my_building$§! construction speed"
 modifier_production_speed_my_building_factor_desc: "Modifies the speed of §Y$my_building$§! construction."
 modifier_state_production_my_building_factor: "§Y$my_building$§! construction speed"
 modifier_state_production_my_building_factor_desc: "Modifies the speed of §Y$my_building$§! construction in this state."
```

The first 3 are used for the building itself in various UI elements, while the last 4 are used to localise the modifiers automatically created for each building: `production_speed_<building>_factor` and `state_production_speed_<building>_factor`.

## <a id="types"></a>Types

These are the different types of buildings in the game (Can also be found inside /Hearts of Iron IV/common/buildings/00\_buildings.txt):
| Icon | Localised name | Internal name | Maximum level | Type |
| --- | --- | --- | --- | --- |
| <a id="infrastructure"></a> ![Infrastructure.png](media/building-modding-hearts-of-iron-4-wiki_811161eae8__img5.png) | Infrastructure | infrastructure | 5 | Non-shared |
| <a id="arms-factory"></a> ![Military factory.png](media/building-modding-hearts-of-iron-4-wiki_811161eae8__img6.png) | Military factory | arms\_factory | 20 | Shared |
| <a id="industrial-complex"></a> ![Civilian factory.png](media/building-modding-hearts-of-iron-4-wiki_811161eae8__img7.png) | Civilian factory | industrial\_complex | 20 | Shared |
| <a id="air-base"></a> ![Air base.png](media/building-modding-hearts-of-iron-4-wiki_811161eae8__img8.png) | Air base | air\_base | 10 | Non-shared |
| <a id="supply-node"></a> ![Supply hub.png](media/building-modding-hearts-of-iron-4-wiki_811161eae8__img9.png) | Supply hub | supply\_node | 1 | Provincial |
| <a id="rail-way"></a> ![Railway.png](media/building-modding-hearts-of-iron-4-wiki_811161eae8__img10.png) | Railway | rail\_way | 5<a id="cite-ref-5"></a>[[5]](#cite-note-5) | Provincial |
| <a id="naval-facility"></a> ![Naval engineering facility.png](media/building-modding-hearts-of-iron-4-wiki_811161eae8__img11.png) | Naval Engineering Facility | naval\_facility | 1 | Provincial |
| <a id="naval-base"></a> ![Naval base.png](media/building-modding-hearts-of-iron-4-wiki_811161eae8__img12.png) | Naval base | naval\_base | 10 | Provincial |
| <a id="bunker"></a> ![Land fort.png](media/building-modding-hearts-of-iron-4-wiki_811161eae8__img13.png) | Land fort | bunker | 10 | Provincial |
| <a id="coastal-bunker"></a> ![Coastal fort.png](media/building-modding-hearts-of-iron-4-wiki_811161eae8__img14.png) | Coastal fort | coastal\_bunker | 10 | Provincial |
| <a id="stronghold-network"></a> ![Stronghold Network.png](media/building-modding-hearts-of-iron-4-wiki_811161eae8__img15.png) | Stronghold Network | stronghold\_network | 1 | Shared |
| <a id="dockyard"></a> ![Naval dockyard.png](media/building-modding-hearts-of-iron-4-wiki_811161eae8__img16.png) | Naval dockyard | dockyard | 20 | Shared |
| <a id="anti-air-building"></a> ![Anti-air (building).png](media/building-modding-hearts-of-iron-4-wiki_811161eae8__img17.png) | Anti-air | anti\_air\_building | 5 | Non-shared |
| <a id="synthetic-refinery"></a> ![Synthetic refinery.png](media/building-modding-hearts-of-iron-4-wiki_811161eae8__img18.png) | Synthetic refinery | synthetic\_refinery | 3 | Shared |
| <a id="fuel-silo"></a> ![Fuel silo.png](media/building-modding-hearts-of-iron-4-wiki_811161eae8__img19.png) | Fuel silo | fuel\_silo | 15 | Shared |
| <a id="radar-station"></a> ![Radar station.png](media/building-modding-hearts-of-iron-4-wiki_811161eae8__img20.png) | Radar station | radar\_station | 6 | Non-shared |
| <a id="mega-gun-emplacement"></a> ![Multi-Charge Large Caliber Gun.png](media/building-modding-hearts-of-iron-4-wiki_811161eae8__img21.png) | Multi-Charge Large Caliber Gun(\*) | mega\_gun\_emplacement | 1 | Shared |
| <a id="rocket-site"></a> ![Rocket site.png](media/building-modding-hearts-of-iron-4-wiki_811161eae8__img22.png) | Rocket site(\*) | rocket\_site | 3 | Shared |
| <a id="naval-supply-hub"></a> ![Naval supply hub.png](media/building-modding-hearts-of-iron-4-wiki_811161eae8__img23.png) | Naval supply hub (\*) | naval\_supply\_hub | 1 | Provincial |
| <a id="naval-headquarters"></a> ![Naval headquarters.png](media/building-modding-hearts-of-iron-4-wiki_811161eae8__img24.png) | Naval headquarters (\*) | naval\_headquarters | 1 | Provincial |
| <a id="nuclear-reactor"></a> ![Nuclear reactor.png](media/building-modding-hearts-of-iron-4-wiki_811161eae8__img25.png) | Nuclear reactor | nuclear\_reactor | 1 | Shared |
| <a id="nuclear-reactor-heavy-water"></a> ![Nuclear reactor.png](media/building-modding-hearts-of-iron-4-wiki_811161eae8__img25.png) | Heavy Water Nuclear Reactor | nuclear\_reactor\_heavy\_water | 1 | Shared |
| <a id="commercial-nuclear-reactor"></a> ![Civilian Nuclear Reactor.png](media/building-modding-hearts-of-iron-4-wiki_811161eae8__img27.png) | Civilian Nuclear Reactor | commercial\_nuclear\_reactor | 1 | Shared |
| <a id="nuclear-facility"></a> ![Nuclear research facility.png](media/building-modding-hearts-of-iron-4-wiki_811161eae8__img28.png) | Nuclear Research Facility | nuclear\_facility | 1 | Provincial |
| <a id="air-facility"></a> ![Aerodynamics and avionics facility.png](media/building-modding-hearts-of-iron-4-wiki_811161eae8__img29.png) | Aerodynamics and Avionics Facility | air\_facility | 1 | Provincial |
| <a id="land-facility"></a> ![Land warfare facility.png](media/building-modding-hearts-of-iron-4-wiki_811161eae8__img30.png) | Land Warfare Facility | land\_facility | 1 | Provincial |
| <a id="dam"></a> ![Dam.png](media/building-modding-hearts-of-iron-4-wiki_811161eae8__img31.png) | Dam | dam | 1 | Provincial |
| <a id="dam-mountain"></a> ![Dam.png](media/building-modding-hearts-of-iron-4-wiki_811161eae8__img31.png) | Dam | dam\_mountain | 1 | Provincial |
| <a id="canal-kiel"></a> ![Canal Locks.png](media/building-modding-hearts-of-iron-4-wiki_811161eae8__img33.png) | Kiel Canal Locks | canal\_kiel | 1 | Provincial |
| <a id="canal-panama"></a> ![Canal Locks.png](media/building-modding-hearts-of-iron-4-wiki_811161eae8__img33.png) | Panama Canal Locks | canal\_panama | 1 | Provincial |
| <a id="energy-infrastructure"></a> ![Reinforced electrical grid.png](media/building-modding-hearts-of-iron-4-wiki_811161eae8__img35.png) | Reinforced electrical grid(\*) | energy\_infrastructure | 1 | Shared |
| <a id="industrial-infrastructure"></a> ![High capacity electrical grid.png](media/building-modding-hearts-of-iron-4-wiki_811161eae8__img36.png) | High capacity electrical grid(\*) | industrial\_infrastructure | 1 | Shared |

Note that while railways and supply nodes are buildings, not all traditional building operations apply to them. Their starting level is defined [outside of state history](<Map modding - Hearts of Iron 4 Wiki.md#supply-nodes-and-railways>) and [a separate effect](<Effects - Hearts of Iron 4 Wiki.md#build-railway>) must be used to construct railways mid-game, with the default [add\_building\_construction](<Effects - Hearts of Iron 4 Wiki.md#add-building-construction>) or other building-related effects crashing the game.

## <a id="references"></a>References

<a id="cite-note-1"></a>1. [↑](#cite-ref-1) `NDefines.NProduction.BASE_FACTORY_SPEED = 4` in [Defines](<Defines - Hearts of Iron 4 Wiki.md>).
<a id="cite-note-2"></a>2. [↑](#cite-ref-2) `NDefines.NProduction.INFRA_MAX_CONSTRUCTION_COST_EFFECT = 1` in [Defines](<Defines - Hearts of Iron 4 Wiki.md>).
<a id="cite-note-3"></a>3. [↑](#cite-ref-3) `NDefines.NBuildings.MAX_SHARED_SLOTS = 25` in [Defines](<Defines - Hearts of Iron 4 Wiki.md>).
<a id="cite-note-4"></a>4. [↑](#cite-ref-4) `NDefines.NBuildings.MAX_BUILDING_LEVELS = 15` in [Defines](<Defines - Hearts of Iron 4 Wiki.md>).
<a id="cite-note-5"></a>5. [↑](#cite-ref-5) `NDefines.NSupply.MAX_RAILWAY_LEVEL = 5` in [Defines](<Defines - Hearts of Iron 4 Wiki.md>).

**[Modding](<Modding - Hearts of Iron 4 Wiki.md>)**
