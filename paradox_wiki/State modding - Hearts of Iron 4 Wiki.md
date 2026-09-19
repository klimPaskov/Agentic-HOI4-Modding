# State modding

*Offline snapshot of the Hearts of Iron IV Wiki page "State modding", captured 2026-09-19.*

## Table of contents

- [Arguments](#Arguments)
  - [Mandatory](#Mandatory)
  - [Optional](#Optional)
  - [History](#History)
- [Examples](#Examples)
- [Notes](#Notes)
- [Using the nudger](#Using_the_nudger)
  - [Buildings](#Buildings)
- [Building types](#Building_types)
- [State categories](#State_categories)

---

States (and their history) are defined in `/Hearts of Iron IV/history/states/*.txt` files. While it is typical to reserve one file to a state, that is not necessary. Unlike, for example, `/Hearts of Iron IV/history/countries/`, **the filename does not get read in how the file should be handled**, only its contents do. For that reason, unless a [replace_path](<Modding - Hearts of Iron 4 Wiki.md>) is defined to the folder, it should be avoided to change the filenames of already-existing files, as this can make it so that both the base game and the mod's state files will get read.

## Arguments <a id="Arguments"></a>

Each state is contained within a `state = { ... }` block that must encompass everything. These are the arguments that can be used.

### Mandatory <a id="Mandatory"></a>

`id = 123` is the ID number of the state. It must be an integer.
**State IDs have to follow a numerical order,** starting from 1: the game will expect every number between 1 and the largest state ID within the mod to be a state. If that expectation is not met, the game will crash when loading the game if the [debug mode](<Modding - Hearts of Iron 4 Wiki.md>) is not turned on, as the map is deemed too erroneous to be played normally.
As such, when deleting a state, the state IDs have to be shifted in order respectively, such as by changing the last state's ID to fit the now-missing ID. When doing that, everything that referenced the now-different state IDs will have to be adjusted, and [searching every text file in the mod using a text editor](<Modding - Hearts of Iron 4 Wiki.md>) can be used to do so.

`name = STATE_123` is a localisation key that will become the name of the state, depending on which language is turned on. For English, this gets defined in any `/Hearts of Iron IV/localisation/english/*_l_english.yml` file as such:

```yaml
l_english:
 STATE_123: "My state name"
```

By default, the game uses `state_names_l_english.yml`.

`manpower = 500000` is the total population of the state at the game's start, both recruitable and non-recruitable. This will be the starting population on every scenario, without population growth being simulated between the first start date and the scenario's beginning. However, a single tick of monthly population growth will be done for each scenario, increasing the state's population by 0.125%.[1]

`state_category = my_category` is the category that the state uses. This sets the state modifiers that the state starts with (Including the amount of starting unlocked shared building slots), as well as assigning a colour to the state in the state view map mode. [Details on the state categories are covered later in the article.](#State_categories)

`provinces = { 123 456 7890 }` is the list of provinces that are defined as belonging to the state, separated with whitespace characters.

### Optional <a id="Optional"></a>

`impassable = yes`, if added in the state, will mark it as impassable. This includes making troops unable to enter it; its provinces going to the controller of the nearest passable provinces; making it impossible to build provincial buildings within it; marking it as true for the [impassable trigger](<Triggers - Hearts of Iron 4 Wiki.md>).

`resources = { steel = 10 aluminium = 20 }` assigns resources to the state. Each resource is added in the format of `<resource> = <int>`. Base game resources include `oil`, `aluminium` (With the spelling used in British English), `rubber`, `tungsten`, `steel`, and `chromium`, although more can be added.

`local_supplies = 8.3` decides the base supply of the state. One unit of local_supplies is equal to 0.2 units of supply. If undefined, assumed to be 0.

`buildings_max_level_factor = 0.5` adds an additional multiplier on the amount of unlocked shared building slots. Recommended to avoid, instead using state categories.

### History <a id="History"></a>

All of these are contained within `history = { ... }`, which is defined within the state. Additionally, these can be used within a YYYY.MM.DD-formatted datestamp inside of history, such as `1939.1.1 = { ... }`. This will make them be executed only if the start date is strictly after the specified date.

`owner = POL` defines the initial owner of the state. If a state does not have an owner, the game will run without issues; however, executing nearly any effect on that state, such as transferring it to a country, will crash the game.

`controller = LIT` defines the initial controller of the state. Optional to define - only necessary if the owner differs from the controller.

`victory_points = { 1234 10 }` defines the amount of victory points on a specified province, where the first number is the province and the second number is the amount of victory points. **Only one province can be defined within one victory_points**. In order to have multiple provinces with victory points in one state, several instances of `victory_points = { ... }` need to be put in.
The localisation key that gets used for the victory point depending on the language of the game is `VICTORY_POINTS_1234`, where 1234 is the ID of the province. For English, this gets defined in any `/Hearts of Iron IV/localisation/english/*_l_english.yml` file as such:

```yaml
l_english:
 VICTORY_POINTS_1234: "My city name"
```

By default, the game uses `victory_points_l_english.yml`. For positioning the icon of a victory point on the map, the [unitstacks file](<Map modding - Hearts of Iron 4 Wiki.md>) is edited. Note that the icon of a victory point doesn't have to be inside of the province itself: if several victory points show up in the same place, it could be from different provinces with an outdated unitstacks file, which would need to be adjusted in the Nudge's Units section accordingly.

`buildings = { ... }` defines the initial buildings that the state has. A single building entry consists of the [the ID of the building](#Building_types) followed by its amount after an equality sign as `dockyard = 10`. Within `buildings = { ... }`, it is also possible to specify a province by using `1234 = { ... }` and putting the province's buildings within, where 1234 is the province's ID. An example definition of buildings that uses this:

```text
buildings = {
    dockyard = 10
    1234 = {
        bunker = 5
        coastal_bunker = 6
    }
}
```

If a building is not mentioned, it does not change the initial value, which is 0 by default; however, the initial building level may be different if the buildings block is within a datestamp rather than being executed immediately. In landlocked states, buildings that can only be built on coastal states/provinces cannot be defined, even if set to 0.

Additionally, history serves as an [effect block](<Effects - Hearts of Iron 4 Wiki.md>). Common effects to use within state history include `add_core_of = POL` or `add_claim_by = LIT`, but any effect can be used.

## Examples <a id="Examples"></a>

Bare minimum:

```text
state = {
    id = 123
    name = STATE_123
    manpower = 50000
    state_category = large_town

    history = {
        owner = ITA
    }

    provinces = {
        1234 5678
    }
}
```

Average state:

```text
state = {
    id = 124
    name = STATE_124
    manpower = 50035
    state_category = megalopolis

    resources = {
        oil = 10
        chromium = 50
    }

    history = {
        owner = SWI
        add_core_of = SWI
        buildings = {
            infrastructure = 3
            industrial_complex = 1
            arms_factory = 1
            dockyard = 10
            7777 = {
                coastal_bunker = 5
                naval_base = 10
            }
        }
        victory_points = { 5555 15 }
        victory_points = { 6666 10 }
        1939.1.1 = {
            controller = ITA
            set_state_name = ITA_STATE_124
            buildings = {
                infrastructure = 4  # This will not change the amount of civilian or military factories.
            }
        }
    }

    provinces = { 1111 2222 3333 4444 5555 6666 7777 8888 9999 }

    local_supplies = 10
}
```

## Notes <a id="Notes"></a>

The building model positions for each state are defined separately from the states themselves, instead being defined in `/Hearts of Iron IV/map/buildings.txt`. A mismatch will cause errors, taking up space in the log and potentially crashes. For example, if a province is lacking a definition for a naval base or a floating harbour within a province, whether it's set in the wrong state in the buildings.txt file or missing entirely, **attempting to use one within that province (whether by the player or the AI) will cause a crash**, marked with [the last read script being client_ping](<Troubleshooting - Hearts of Iron 4 Wiki.md#Crash_data_log>). The simplest way to compile the positions of models is to use the building section in the [nudger](<Nudger - Hearts of Iron 4 Wiki.md>).
`/Hearts of Iron IV/map/airports.txt` and `/Hearts of Iron IV/map/rocketsites.txt` decide in which province in the state the game should put airports or rocket sites. This is also edited in the building section in the [nudger](<Nudger - Hearts of Iron 4 Wiki.md>). **If either is incorrect or missing, the game will not be possible to open without debug mode.**

The state borders must follow [strategic regions](<Strategic region modding - Hearts of Iron 4 Wiki.md>), defined in `/Hearts of Iron IV/map/strategicregions/*.txt`. If one province in the state belongs to one strategic region, while a different province in the same state belongs to a different strategic region, a map error will be created, which will cause a game crash on launch if the debug mode is not turned on. Make sure that strategic region borders are followed, either by adjusting the state or the strategic regions.

## Using the nudger <a id="Using_the_nudger"></a>

*Parts of this section are transcluded from [Nudger § States](<Nudger - Hearts of Iron 4 Wiki.md#States>)*

The [nudger](<Nudger - Hearts of Iron 4 Wiki.md>) is a map editing tool, accessed through the main menu with the `-debug` launch option enabled. For the states, it can be used in order to change the borders of states and in order to generate the building models.

The state section of the nudger is used for defining the borders and names of states. Any state border changes will also automatically change the borders of the strategic regions that cover the states, taking provinces out of strategic regions completely for new states. Within the user directory, this edits the `/Hearts of Iron IV/history/states/` and `/Hearts of Iron IV/map/strategicregions/` folders and the `/Hearts of Iron IV/localisation/english/state_names_l_english.yml` file (for the English language).
**The nudger will remove quotation marks from the state file, aside from the `name` attribute.** This can break the rest of the script that's located inside of them. Most commonly, this will break any [has_dlc](<Triggers - Hearts of Iron 4 Wiki.md>) checks, which will result in the entirety of the state breaking thereafter.
**The nudger interprets version number–less [localisation](<Localisation - Hearts of Iron 4 Wiki.md>) values as having a version of -1**, and writes that in the output. As the game only expects numeric values in the version number, this will break the localisation after that point, with an error of the `Expected quotation mark (") at line 113 and column 16 in ...` sort.

Clicking onto a province is used to select a province. After a province is selected, `⇧Shift`-clicking onto a province causes the following behaviour, depending on the selected and clicked provinces:

- If the selected provinces are in a state and the shift-clicked province is in a different state or none at all, the game will adjust the borders of the state and the strategic regions to cover the shift-clicked province. It will also be selected.
  - If the shift-clicked province isn't in any state, it will be added to the state's strategic region without checking if it's already in one. **This may cause the province to be defined twice in the same strategic region or be defined in two different strategic regions.** This has to be fixed manually.
- If the selected provinces are in a state and the shift-clicked province is in the same state, it will be removed from the state and the strategic region without being selected. The same happens if the selected provinces aren't in any state.
- If the selected provinces and the shift-clicked province are both not in any state, it will get added to the selection.
- If the shift-clicked province is already selected, it will get removed from the selection and, if it's in one, the state it's currently in.

If a province or several not in any state are selected, it is possible to create a state. That requires entering a state name into the textbox and selecting "Create state".

- **The state name must only contain ASCII characters that are possible to use in filenames**. If there are any characters that aren't in ASCII, such as diacritics or non-Latin script, the game will crash to desktop instead of creating the state, but it will be able to remove the provinces from the old state first and save the changes there. Characters that are impossible to use in filenames include, on Windows, `\ / : * " < > |`.
- **Creating a new state (and occasionally editing state borders) requires changing the building model positions and airport/rocket launch site locations to avoid crashes**.

If the selected province(s) are in a state, it is possible to select "Open file" or "Delete state":

- Opening the file will use the default text editor for .txt files to open the file of the state in the user directory. If the user directory doesn't contain the file, a copy will be created. This copy doesn't contain the changes made in the nudger and instead will have those that were loaded into the memory when the files were last fetched (by opening the game, with "Update", or with "Save"). If the button is used and the file's version in the user directory is deleted, the button will do nothing until the next fetch of state files.
- "Delete state" will not necessarily delete the state, but instead remove the file from the user directory (if it exists) and unload from memory all changes that were made to it in the nudger. This will also cause the game to try reading the state files related to the state ID: if the [loaded files](<Modding - Hearts of Iron 4 Wiki.md#Loading_files>) contain a state with the same ID, it will get used for the state's information, otherwise it will be deleted.

Among the buttons that can always be selected, there are "Delete all empty" and "Find collision".

- "Delete all empty" works similarly to deleting an individual state: it checks for all provinces that have no provinces in memory (taking unsaved changes into consideration). If it finds any, the state gets deleted from memory and the user directory. Afterwards, the game will try finding a file to use as the new state information for each of the deleted states.
- "Find collision" detects provinces that are located in several states at the same time. When pressed, it will move the player's camera to one of such provinces and give a selection of which state it must remain in; upon making a choice, it will be removed from every other state.

"Update" is used to disregard all unsaved changes and re-read the state files among the [loaded files](<Modding - Hearts of Iron 4 Wiki.md#Loading_files>). If the state borders were manually changed, such as by moving the outputs into the mod files from the user directory, this is necessary to load them without restarting the game.
"Save" is used to write all changes to the user directory. Upon doing so, the changes will be purged from memory and the game will re-read the state files among the [loaded files](<Modding - Hearts of Iron 4 Wiki.md#Loading_files>). **If the state files in the user directory are overwritten or unloaded by mod files, it will appear that (some of) the changes will instantly revert, however they'll still be present in the user directory.** This will require moving the files into the mod's files and updating the state of the game with "Update". Only the files since the last fetching of files will be created or changed within the user directory after saving.

### Buildings <a id="Buildings"></a>

\*Please help improve this article or section by expanding it .\*

## Building types <a id="Building_types"></a>

:   *Main article: [Building modding](<Building modding - Hearts of Iron 4 Wiki.md>)*

These are the different types of buildings in the game (Can also be found inside `/Hearts of Iron IV/common/buildings/00_buildings.txt`):

| Icon | Localised name | Internal name | Maximum level | Type |
| --- | --- | --- | --- | --- |
| ![Infrastructure.png](media/building-modding-hearts-of-iron-4-wiki_811161eae8__img5.png) | Infrastructure | infrastructure | 5 | Non-shared |
| ![Military factory.png](media/building-modding-hearts-of-iron-4-wiki_811161eae8__img6.png) | Military factory | arms_factory | 20 | Shared |
| ![Civilian factory.png](media/building-modding-hearts-of-iron-4-wiki_811161eae8__img7.png) | Civilian factory | industrial_complex | 20 | Shared |
| ![Air base.png](media/building-modding-hearts-of-iron-4-wiki_811161eae8__img8.png) | Air base | air_base | 10 | Non-shared |
| ![Supply hub.png](media/building-modding-hearts-of-iron-4-wiki_811161eae8__img9.png) | Supply hub | supply_node | 1 | Provincial |
| ![Railway.png](media/building-modding-hearts-of-iron-4-wiki_811161eae8__img10.png) | Railway | rail_way | 5[2] | Provincial |
| ![Naval engineering facility.png](media/building-modding-hearts-of-iron-4-wiki_811161eae8__img11.png) | Naval Engineering Facility | naval_facility | 1 | Provincial |
| ![Naval base.png](media/building-modding-hearts-of-iron-4-wiki_811161eae8__img12.png) | Naval base | naval_base | 10 | Provincial |
| ![Land fort.png](media/building-modding-hearts-of-iron-4-wiki_811161eae8__img13.png) | Land fort | bunker | 10 | Provincial |
| ![Coastal fort.png](media/building-modding-hearts-of-iron-4-wiki_811161eae8__img14.png) | Coastal fort | coastal_bunker | 10 | Provincial |
| ![Stronghold Network.png](media/building-modding-hearts-of-iron-4-wiki_811161eae8__img15.png) | Stronghold Network | stronghold_network | 1 | Shared |
| ![Naval dockyard.png](media/building-modding-hearts-of-iron-4-wiki_811161eae8__img16.png) | Naval dockyard | dockyard | 20 | Shared |
| ![Anti-air (building).png](media/building-modding-hearts-of-iron-4-wiki_811161eae8__img17.png) | Anti-air | anti_air_building | 5 | Non-shared |
| ![Synthetic refinery.png](media/building-modding-hearts-of-iron-4-wiki_811161eae8__img18.png) | Synthetic refinery | synthetic_refinery | 3 | Shared |
| ![Fuel silo.png](media/building-modding-hearts-of-iron-4-wiki_811161eae8__img19.png) | Fuel silo | fuel_silo | 15 | Shared |
| ![Radar station.png](media/building-modding-hearts-of-iron-4-wiki_811161eae8__img20.png) | Radar station | radar_station | 6 | Non-shared |
| ![Multi-Charge Large Caliber Gun.png](media/building-modding-hearts-of-iron-4-wiki_811161eae8__img21.png) | Multi-Charge Large Caliber Gun(\*) | mega_gun_emplacement | 1 | Shared |
| ![Rocket site.png](media/building-modding-hearts-of-iron-4-wiki_811161eae8__img22.png) | Rocket site(\*) | rocket_site | 3 | Shared |
| ![Naval supply hub.png](media/building-modding-hearts-of-iron-4-wiki_811161eae8__img23.png) | Naval supply hub (\*) | naval_supply_hub | 1 | Provincial |
| ![Naval headquarters.png](media/building-modding-hearts-of-iron-4-wiki_811161eae8__img24.png) | Naval headquarters (\*) | naval_headquarters | 1 | Provincial |
| ![Nuclear reactor.png](media/building-modding-hearts-of-iron-4-wiki_811161eae8__img25.png) | Nuclear reactor | nuclear_reactor | 1 | Shared |
| ![Nuclear reactor.png](media/building-modding-hearts-of-iron-4-wiki_811161eae8__img25.png) | Heavy Water Nuclear Reactor | nuclear_reactor_heavy_water | 1 | Shared |
| ![Civilian Nuclear Reactor.png](media/building-modding-hearts-of-iron-4-wiki_811161eae8__img27.png) | Civilian Nuclear Reactor | commercial_nuclear_reactor | 1 | Shared |
| ![Nuclear research facility.png](media/building-modding-hearts-of-iron-4-wiki_811161eae8__img28.png) | Nuclear Research Facility | nuclear_facility | 1 | Provincial |
| ![Aerodynamics and avionics facility.png](media/building-modding-hearts-of-iron-4-wiki_811161eae8__img29.png) | Aerodynamics and Avionics Facility | air_facility | 1 | Provincial |
| ![Land warfare facility.png](media/building-modding-hearts-of-iron-4-wiki_811161eae8__img30.png) | Land Warfare Facility | land_facility | 1 | Provincial |
| ![Dam.png](media/building-modding-hearts-of-iron-4-wiki_811161eae8__img31.png) | Dam | dam | 1 | Provincial |
| ![Dam.png](media/building-modding-hearts-of-iron-4-wiki_811161eae8__img31.png) | Dam | dam_mountain | 1 | Provincial |
| ![Canal Locks.png](media/building-modding-hearts-of-iron-4-wiki_811161eae8__img33.png) | Kiel Canal Locks | canal_kiel | 1 | Provincial |
| ![Canal Locks.png](media/building-modding-hearts-of-iron-4-wiki_811161eae8__img33.png) | Panama Canal Locks | canal_panama | 1 | Provincial |
| ![Reinforced electrical grid.png](media/building-modding-hearts-of-iron-4-wiki_811161eae8__img35.png) | Reinforced electrical grid(\*) | energy_infrastructure | 1 | Shared |
| ![High capacity electrical grid.png](media/building-modding-hearts-of-iron-4-wiki_811161eae8__img36.png) | High capacity electrical grid(\*) | industrial_infrastructure | 1 | Shared |

Note that while railways and supply nodes are buildings, not all traditional building operations apply to them. Their starting level is defined [outside of state history](<Map modding - Hearts of Iron 4 Wiki.md>) and [a separate effect](<Effects - Hearts of Iron 4 Wiki.md>) must be used to construct railways mid-game, with the default [add_building_construction](<Effects - Hearts of Iron 4 Wiki.md>) or other building-related effects crashing the game.

## State categories <a id="State_categories"></a>

The base game state categories and their corresponding number of building slots:

| Localised name | Internal name | Amount of slots | Color |
| --- | --- | --- | --- |
| Wasteland | wasteland | 0 |  |
| Enclave | enclave | 0 |  |
| Tiny island | tiny_island | 0 |  |
| Pastoral region | pastoral | 1 |  |
| Small island | small_island | 1 |  |
| Rural region | rural | 2 |  |
| Developed Rural Region | town | 4 |  |
| Sparse Urban Region | large_town | 5 |  |
| Urban Region | city | 6 |  |
| Dense Urban Region | large_city | 8 |  |
| Metropolis Region | metropolis | 10 |  |
| Megalopolis Region | megalopolis | 12 |  |

State categories can be added in `/Hearts of Iron IV/common/state_category/*.txt` files. Each state category is contained within the `state_categories = { ... }`, as a code block with the name of the state category's ID.

A state category is a [modifier block](<Modifiers - Hearts of Iron 4 Wiki.md#State_scope>), where any state-scoped modifier can be used. The only modifier that the base game uses is `local_building_slots`, set to an integer, but any can be used. Additionally, the `color = { 0 0 255 }` block corresponds to the state's colour in the state map mode. It is defined in the RGB format, where each value is an integer on the scale from 0 to 255.

Example:

```text
state_categories={
    my_state_category = {
        color = { 0 255 0 }
        local_building_slots = 14
    }
    my_second_category = {
        color = { 255 0 0 }
        local_building_slots = 4
        resistance_growth = 0.1
    }
}
```

The `set_state_category = category_id` effect can be used to change the state category of a state mid-game.

1. ↑ `NDefines.NCountry.POPULATION_YEARLY_GROWTH_BASE = 0.015`
2. ↑ `NDefines.NSupply.MAX_RAILWAY_LEVEL = 5` in [Defines](<Defines - Hearts of Iron 4 Wiki.md>).

---

## Navigation

**[Modding](<Modding - Hearts of Iron 4 Wiki.md>)**

- **Documentation**: [Effects](<Effects - Hearts of Iron 4 Wiki.md>) • [Triggers](<Triggers - Hearts of Iron 4 Wiki.md>) • [Defines](<Defines - Hearts of Iron 4 Wiki.md>) • [Modifiers](<Modifiers - Hearts of Iron 4 Wiki.md>) • [List of modifiers](<List of modifiers - Hearts of Iron 4 Wiki.md>) • [Scopes](<Scopes - Hearts of Iron 4 Wiki.md>) • [Localisation](<Localisation - Hearts of Iron 4 Wiki.md>) • [On actions](<On actions - Hearts of Iron 4 Wiki.md>) • [Data structures](<Data structures - Hearts of Iron 4 Wiki.md>) • [Flags](<Data structures - Hearts of Iron 4 Wiki.md#Flags>) • [Event targets](<Data structures - Hearts of Iron 4 Wiki.md#Event_targets>) • [Country tag aliases](<Data structures - Hearts of Iron 4 Wiki.md#Country_tag_aliases>) • [Variables](<Data structures - Hearts of Iron 4 Wiki.md#Variables>) • [Arrays](<Data structures - Hearts of Iron 4 Wiki.md#Arrays>)
- **Scripting**: [Achievements](<Achievement modding - Hearts of Iron 4 Wiki.md>) • [AI](<AI modding - Hearts of Iron 4 Wiki.md>) • [AI focuses](<AI focuses - Hearts of Iron 4 Wiki.md>) • [Autonomous states](<Autonomy state modding - Hearts of Iron 4 Wiki.md>) • [Balances of power](<Balance of power modding - Hearts of Iron 4 Wiki.md>) • [Bookmarks/Scenarios](<Bookmark modding - Hearts of Iron 4 Wiki.md>) • [Game rules](<Bookmark modding - Hearts of Iron 4 Wiki.md#Game_rules>) • [Buildings](<Building modding - Hearts of Iron 4 Wiki.md>) • [Characters and traits](<Character modding - Hearts of Iron 4 Wiki.md>) • [Cosmetic tags](<Cosmetic tag modding - Hearts of Iron 4 Wiki.md>) • [Countries](<Country creation - Hearts of Iron 4 Wiki.md>) • [Divisions](<Division modding - Hearts of Iron 4 Wiki.md>) • [Decisions](<Decision modding - Hearts of Iron 4 Wiki.md>) • [Doctrines](<Doctrine modding - Hearts of Iron 4 Wiki.md>) • [Equipment](<Equipment modding - Hearts of Iron 4 Wiki.md>) • [Events](<Event modding - Hearts of Iron 4 Wiki.md>) • [Factions](<Faction modding - Hearts of Iron 4 Wiki.md>) • [Ideas](<Idea modding - Hearts of Iron 4 Wiki.md>) • [Ideologies](<Ideology modding - Hearts of Iron 4 Wiki.md>) • [Military industrial organizations](<Military industrial organization modding - Hearts of Iron 4 Wiki.md>) • [National focuses](<National focus modding - Hearts of Iron 4 Wiki.md>) • [Resources](<Resources modding - Hearts of Iron 4 Wiki.md>) • [Scripted GUI](<Scripted GUI modding - Hearts of Iron 4 Wiki.md>) • [Technologies and doctrines](<Technology modding - Hearts of Iron 4 Wiki.md>) • [Units](<Unit modding - Hearts of Iron 4 Wiki.md>)
- **Map**: [Map](<Map modding - Hearts of Iron 4 Wiki.md>) • [Supply areas](<Supply areas modding - Hearts of Iron 4 Wiki.md>) • [Strategic regions](<Strategic region modding - Hearts of Iron 4 Wiki.md>)
- **Graphical**: [Interface](<Interface modding - Hearts of Iron 4 Wiki.md>) • [Graphical assets](<Graphical asset modding - Hearts of Iron 4 Wiki.md>) • [Entities](<Entity modding - Hearts of Iron 4 Wiki.md>) • [Posteffects](<Posteffect modding - Hearts of Iron 4 Wiki.md>) • [Particles](<Particle modding - Hearts of Iron 4 Wiki.md>) • [Fonts](<Font modding - Hearts of Iron 4 Wiki.md>)
- **Cosmetic**: [Portraits](<Portrait modding - Hearts of Iron 4 Wiki.md>) • [Namelists](<Namelist modding - Hearts of Iron 4 Wiki.md>) • [Music](<Music modding - Hearts of Iron 4 Wiki.md>) • [Sound](<Sound modding - Hearts of Iron 4 Wiki.md>)
- **Other**: [Console commands](<Console commands - Hearts of Iron 4 Wiki.md>) • [Troubleshooting](<Troubleshooting - Hearts of Iron 4 Wiki.md>) • [Mod structure](<Mod structure - Hearts of Iron 4 Wiki.md>) • [Mods](<Mods - Hearts of Iron 4 Wiki.md>) • [Nudger](<Nudger - Hearts of Iron 4 Wiki.md>)
