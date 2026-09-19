# Nudger

*Offline snapshot of the Hearts of Iron IV Wiki page "Nudger", captured 2026-09-19.*

## Table of contents

- [Overview](#Overview)
- [States](#States)
  - [Buildings](#Buildings)
- [Strategic regions](#Strategic_regions)
  - [Weather](#Weather)
    - [Weather positions](#Weather_positions)
    - [Weather chances](#Weather_chances)
- [Database](#Database)
- [Units](#Units)
- [Supply](#Supply)
- [References and notes](#References_and_notes)

---

The nudger is a tool in Hearts of Iron IV used in creation of map-related files.

The nudger is accessed via the [nudge console command](<Console commands - Hearts of Iron 4 Wiki.md>) or the "Nudge!" button in the main menu, which appears when the [debug launch option](<Modding - Hearts of Iron 4 Wiki.md>) is used when launching the game. Upon launching, it will show the default state of the world, as it appears in the [bookmark](<Bookmark modding - Hearts of Iron 4 Wiki.md>) that's set to be the default. If there is no default bookmark, then the map will appear as having no countries.

The nudger will always output the files directly into the [user directory](<Modding - Hearts of Iron 4 Wiki.md>), such as `C:/Users/username/Documents/Paradox Interactive/Hearts of Iron IV/` (the default location on Windows without OneDrive). **Unless moved, the generated files will be loaded when opening the base game**, potentially causing crashes and at the very least map definition errors that cause the game to close itself without the debug mode. This potentially includes the `history/states/`, `map/`, and `localisation/english/`.

## Overview <a id="Overview"></a>

- States: Used to edit the state history files. It doesn't modify the state-wide building model positions, necessary for a new state to work as intended.
- Supply areas: The supply areas were removed in 1.11 (the update with the ![No Step Back](media/country-creation-hearts-of-iron-4-wiki_1d4220f262__img16.png)No Step Back DLC), and the button is currently non-functional.
- Strategic regions: Edits the strategic region borders and, for naval regions, terrain and modifiers.
- Ambient objects: Edits the 3D models rendered consistently on the world's map, most notably the borders on the North and the South.
- Database: Edits the `/Hearts of Iron IV/map/definition.csv` file, used for province information.
- Weather: Edits the weather within strategic regions and the position of meshes used for the weather effects.
- Buildings: Used for positioning building models, assigning the neighbouring sea province for naval bases and floating harbours, and for assigning each state a single province where the air base and the rocket launch base are located. **Will cause crashes if a new state is created without that being adjusted.**
- Units: Used for establishing the exact position of unit models and victory points.
- Supply: Used for positioning the starting locations and levels of supply hubs and railways.
- Leave nudge: Attempts to return to the main menu. If the nudger was entered using the console instead of the main menu, results in a crash to desktop.

## States <a id="States"></a>

*See also: [State modding](<State modding - Hearts of Iron 4 Wiki.md>)*

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

## Strategic regions <a id="Strategic_regions"></a>

\*Please help improve this article or section by expanding it .\*

### Weather <a id="Weather"></a>

*See also: [Map modding § Weather](<Map modding - Hearts of Iron 4 Wiki.md#Weather>)*

![Nudger weather](media/nudger-hearts-of-iron-4-wiki_14dc29a6a3__img2.png)Instruments in the Weather section

*Instruments in the Weather section*

The weather section of the nudger is used for deciding the chance for weather-related province modifiers during a time period in strategic regions and for determining the positions of particle spawners for weather effects. This edits `/Hearts of Iron IV/map/strategic_regions/` and `/Hearts of Iron IV/map/weatherpositions.txt`.

The weather instruments can be split into 4 general groups: previewing effects on the far left (as a separate window), weather chances on the left, period selection on the right, and weather position modifying on the far right. For the weather positions, the previewing effects on the far left and weather position modifying on the far right are used; for modifying the chances of province modifiers, the weather chances on the left and period selection on the right are used.

Weather can only be modified with a strategic region selected. When a region is selected, yellow gizmos representing the weather positions will be shown on the map, with the text "small" or "big" representing the volume of the generated particles.

"Save" in the bottom left will output all of the changes to the user directory, "Cancel" will purge all of the changes from memory, while "Reload regions" in the top left will purge the changes from memory and re-read the strategic region and weather position files.

#### Weather positions <a id="Weather_positions"></a>

The menu on the far right is used for the positions of weather-related particle effects, in particular these buttons are used:

- "Random In Selected", once selected, will randomly change the locations of the existing weather positions to be evenly distributed in the area of the strategic region. This will not change the amount of weather positions nor their sizes. However, if the strategic region lacks any weather positions, the nudger will create 2 big weather positions first.
- "Random In All" will randomise every strategic region's weather positions using the same process as above.
- "Add" is used for creating a new weather position. Upon creation, it will be centered in the province of the strategic region that has the smallest province ID.
- The list of weather positions below allows selecting a single weather position. Upon one being selected, the map will change to highlight the selected weather position in red and hide all other positions. Right clicking on a location will allow to move the weather position there.
- "Set Small" and "Set Big" change the volume of particles emitted by the weather position. If a weather position is selected, then only it will change in size. Otherwise, every weather position in the selected strategic region will change in size.
- "Remove" is used for deleting a weather position from the region.

The "Preview effects" is used for previewing how the particle effects will look like in-game. Only one weather effect can be selected in a strategic region at a time, however they can be played over multiple strategic regions at the same time. **Enabling weather in the graphics settings is mandatory for this to have effect**. Selecting an effect will show the particles associated with it generated by the weather positions. "Disable" is used for removing the particle effects from the currently-selected strategic region, while "Disable All" removes the effect from every single strategic region.

#### Weather chances <a id="Weather_chances"></a>

The weather chances are decided by the time periods. On the right, a list of periods is given, and "Add Period" will create a new one in the list. The checkbox in the top-right will select the current weather period, while "Delete" will remove it from existence. "Between Day.Month" is used for applying the time during which the time period should apply, in the Day.Month format. Both begin with 1 as the first day or month, and the range includes both ends. "Apply" is used to set the changes to the period's length, as they will otherwise reset upon creating a new period and will not save.
**Periods in the nudger aren't region-specific**: editing the lengths of periods and adding/removing them will result in changes for every single strategic region. "Check errors" in the bottom left is used for checking the period-related errors, such as there being days covered by no periods or several of them at once.

The menu on the left allows changing the temperature range and the chances for each of the weather modifiers. For editing this, a strategic region and a period must be selected. Most of these are sliders allowing to set a value between 0 and 1, including both ends. There are the following exceptions:

- "Temperature" is the temperature range of the region. This allows setting a minimum and maximum temperature as separate ranges. Very cold or hot temperatures will modify the combat with the ranges listed in Weather § Temperature.
- The button next to "Mud" allows instantly changing the chance of Arctic Water to either 1.00 or 0.00. This is generally useful for setting a lot of sea strategic regions to be always frozen in a certain period.

## Database <a id="Database"></a>

*See also: Province modding*

The database section of the nudger is used for editing the `/Hearts of Iron IV/map/definition.csv` file used for province definitions. Within the user directory, this edits the `/Hearts of Iron IV/map/definition.csv.cache` and `/Hearts of Iron IV/map/definition.csv.fixed.csv` file. Despite the different name, the "fixed" province definition will still get read and have priority over `definition.csv`.

**Most of the buttons of the database section are likely to crash the game if no playthrough has yet started.** It is advisable to start a new game, go through the process of selecting a country and starting a playthrough, exit to the main menu, and access the nudger from there. Using the console command works to avoid the crash, but will cause a game crash when trying to leave the nudger.
Most of the selectable buttons change the appearance of the world map in a certain way. However, after changing once, the world map stays static, without registering any of the changes made in the nudger or switching to a different options. Refreshing the state of the map is possible by exiting the database section of the nudge by switching to a different tab or exiting the nudger in entirety.

There are the following buttons present in the Database section:

- "Generate RGB" is used to provide a RGB code that's certainly not yet present in the `map/definition.csv` file. This can be used to safely modify the province bitmap without worrying about overlap.
- "Save" is used to output the changes into the `/Hearts of Iron IV/map/definition.csv.fixed.csv` file.
- "Cancel" purges all changes to province definitions that are stored in memory but aren't yet saved and deselects every option.
- "Type" is used to decide on whether a province is a sea, lake, or land province. Selecting either of the three options and clicking onto a province changes its type. Note that changing the coastal status will also be mandatory. The world map switches to an entirely empty mapmode devoid of all countries, but the tooltip can be used to determine the current type of a province.
- "Coastal" is used to change whether a province is considered coastal or not within the province definition file. Clicking on a province will make it be coastal, changing nothing if it already is. "Generate" available in this mode will automatically assign the coastal status to every province based on the types of neighbouring provinces. The map mode changes to an empty one with coastal provinces marked with yellow stripes.
- "Continent" is used for assigning a continent to a province. By default, the first continent is selected, but it can be changed with the buttons showing a list of continents. Clicking onto a province will change the province's continent to the currently-selected one and change the text in the bottom to "Continent". Despite that, the previously-selected continent is still used to paint provinces and clicking onto another province will change its continent as well. The map mode shows each continent in its own colour. AI areas are not updated within the nudger, so the only way to check the continents after the painting is to reset the map by switching onto another tab.
- "Show colors" changes the map mode to have each province's colour in `map/provinces.bmp` get overlaid as stripes over it.

## Units <a id="Units"></a>

\*Please help improve this article or section by expanding it .\*

## Supply <a id="Supply"></a>

*"Supply hub" and "Supply node" are used interchangeably here**See also: [Map modding § Supply](<Map modding - Hearts of Iron 4 Wiki.md#Supply>)*

The supply section in the nudge is used for determining the starting positions and levels of supply hubs and railways. This edits the `/Hearts of Iron IV/map/supply_nodes.txt` and `/Hearts of Iron IV/map/railways.txt` files. **If either of these files contains references to provinces that don't exist or aren't in any state, the nudger will crash upon selecting this tab.**

Upon selecting it, the nudger will show the world map with supply-related constructions highlighted, in particular:

- If a province has at least 2 victory points, it will have a small cyan rotation gizmo.
- If the province is a capital of the country, it will have a large yellow rotation gizmo.
- If the province has a naval base, it will have a medium dark blue rotation gizmo. This doesn't show up if the province is a capital of the country.
- If the province has a supply hub built at the start, it will have a medium pink rotation gizmo. This doesn't show up if the province is a capital or has a naval base.
- All railways are represented as grey edges connecting the provinces.

The gizmos and the nodes of the railway graph are placed using the position of the "Standstill" model within unitstacks. If none can be found, it resets to the default of being in the middle of the province.

Clicking onto a province with an existing railway will select it. In case of overlap, only the first-defined railway can get selected. This allows changing its level through the `\land` and `\lor` symbols and deleting it with "Delete Railway".

While `^Ctrl`, the edit mode is enabled. Letting go of `^Ctrl` will immediately leave the edit mode, regardless the context. If there's a selected railway that wasn't yet created, its path will be lost. The edit mode allows for the following:

- If nothing is selected, clicking onto a land province located in a non-impassable state will select it. This allows creating or editing the supply node:
  - If the supply node doesn't exist, "Create Node" will create one with the specified level. If the level is higher than the maximum level set in `/Hearts of Iron IV/common/buildings/`, then it gets clamped to the maximum.
  - If the supply node exists, "Delete Node" will remove it from memory and the file.
  - If the supply node exists, "Update Node" will change the building level of the node. If the level is higher than the maximum level set in `/Hearts of Iron IV/common/buildings/`, then it gets clamped to the maximum.
- If there's only one province selected, clicking onto it again will unselect it.
- If there's only one province selected, clicking onto another province with a passable land connection to it will cause the game to make a path between these two provinces located on land provinces crossing no impassable states and select a railway that follows that path. The created railway isn't created yet, however. The path may cross impassable borders between individual provinces.
- If a railway is selected, regardless of whether it exists or not, clicking onto a province at the very edge of the railway will remove that province from the railway, while clicking onto a passable land province not already in the railway that borders either end will expand the path of the railway to cover that province. In case of overlap, the province that was added to the railway last will get priority. For an existing railway to get selected, it must be selected before entering the edit mode.
- If a non-existing railway is selected, "Add Railway" is used to create it on the world map, allowing it to exist in-game and outside of the edit mode. The level it'll be created on is the same as the one entered on the right of the menu. If the selected level is higher than the maximum possible level of railways, it resets to 1.

"Update" is used to re-read only the `/Hearts of Iron IV/map/supply_nodes.txt` file, while ignoring the changes to railways. **This cannot delete existing supply nodes**, this can only create new supply nodes or change the building level of them. To remove a supply node from memory, it must be deleted individually.
"Load" is used to disregard all unsaved changes and re-read the supply files among the [loaded files](<Modding - Hearts of Iron 4 Wiki.md#Loading_files>). If the railways were manually changed, such as by moving the outputs into the mod files from the user directory, this is necessary to load them without restarting the game. This cannot delete supply nodes from memory, similarly to "Update".
"Save" is used to write all changes to the user directory. Upon doing so, the changes to railways will be purged from memory and the game will re-read the supply files among the [loaded files](<Modding - Hearts of Iron 4 Wiki.md#Loading_files>). **If the railway files in the user directory are overwritten or unloaded by mod files, it will appear that (some of) the changes will instantly revert, however they'll still be present in the user directory.** This will require moving the railways file into the mod's files and updating the state of the game with "Load". This cannot delete supply nodes from memory, similarly to "Update".

## References and notes <a id="References_and_notes"></a>

---

## Navigation

**[Modding](<Modding - Hearts of Iron 4 Wiki.md>)**

- **Documentation**: [Effects](<Effects - Hearts of Iron 4 Wiki.md>) • [Triggers](<Triggers - Hearts of Iron 4 Wiki.md>) • [Defines](<Defines - Hearts of Iron 4 Wiki.md>) • [Modifiers](<Modifiers - Hearts of Iron 4 Wiki.md>) • [List of modifiers](<List of modifiers - Hearts of Iron 4 Wiki.md>) • [Scopes](<Scopes - Hearts of Iron 4 Wiki.md>) • [Localisation](<Localisation - Hearts of Iron 4 Wiki.md>) • [On actions](<On actions - Hearts of Iron 4 Wiki.md>) • [Data structures](<Data structures - Hearts of Iron 4 Wiki.md>) • [Flags](<Data structures - Hearts of Iron 4 Wiki.md#Flags>) • [Event targets](<Data structures - Hearts of Iron 4 Wiki.md#Event_targets>) • [Country tag aliases](<Data structures - Hearts of Iron 4 Wiki.md#Country_tag_aliases>) • [Variables](<Data structures - Hearts of Iron 4 Wiki.md#Variables>) • [Arrays](<Data structures - Hearts of Iron 4 Wiki.md#Arrays>)
- **Scripting**: [Achievements](<Achievement modding - Hearts of Iron 4 Wiki.md>) • [AI](<AI modding - Hearts of Iron 4 Wiki.md>) • [AI focuses](<AI focuses - Hearts of Iron 4 Wiki.md>) • [Autonomous states](<Autonomy state modding - Hearts of Iron 4 Wiki.md>) • [Balances of power](<Balance of power modding - Hearts of Iron 4 Wiki.md>) • [Bookmarks/Scenarios](<Bookmark modding - Hearts of Iron 4 Wiki.md>) • [Game rules](<Bookmark modding - Hearts of Iron 4 Wiki.md#Game_rules>) • [Buildings](<Building modding - Hearts of Iron 4 Wiki.md>) • [Characters and traits](<Character modding - Hearts of Iron 4 Wiki.md>) • [Cosmetic tags](<Cosmetic tag modding - Hearts of Iron 4 Wiki.md>) • [Countries](<Country creation - Hearts of Iron 4 Wiki.md>) • [Divisions](<Division modding - Hearts of Iron 4 Wiki.md>) • [Decisions](<Decision modding - Hearts of Iron 4 Wiki.md>) • [Doctrines](<Doctrine modding - Hearts of Iron 4 Wiki.md>) • [Equipment](<Equipment modding - Hearts of Iron 4 Wiki.md>) • [Events](<Event modding - Hearts of Iron 4 Wiki.md>) • [Factions](<Faction modding - Hearts of Iron 4 Wiki.md>) • [Ideas](<Idea modding - Hearts of Iron 4 Wiki.md>) • [Ideologies](<Ideology modding - Hearts of Iron 4 Wiki.md>) • [Military industrial organizations](<Military industrial organization modding - Hearts of Iron 4 Wiki.md>) • [National focuses](<National focus modding - Hearts of Iron 4 Wiki.md>) • [Resources](<Resources modding - Hearts of Iron 4 Wiki.md>) • [Scripted GUI](<Scripted GUI modding - Hearts of Iron 4 Wiki.md>) • [Technologies and doctrines](<Technology modding - Hearts of Iron 4 Wiki.md>) • [Units](<Unit modding - Hearts of Iron 4 Wiki.md>)
- **Map**: [Map](<Map modding - Hearts of Iron 4 Wiki.md>) • [States](<State modding - Hearts of Iron 4 Wiki.md>) • [Supply areas](<Supply areas modding - Hearts of Iron 4 Wiki.md>) • [Strategic regions](<Strategic region modding - Hearts of Iron 4 Wiki.md>)
- **Graphical**: [Interface](<Interface modding - Hearts of Iron 4 Wiki.md>) • [Graphical assets](<Graphical asset modding - Hearts of Iron 4 Wiki.md>) • [Entities](<Entity modding - Hearts of Iron 4 Wiki.md>) • [Posteffects](<Posteffect modding - Hearts of Iron 4 Wiki.md>) • [Particles](<Particle modding - Hearts of Iron 4 Wiki.md>) • [Fonts](<Font modding - Hearts of Iron 4 Wiki.md>)
- **Cosmetic**: [Portraits](<Portrait modding - Hearts of Iron 4 Wiki.md>) • [Namelists](<Namelist modding - Hearts of Iron 4 Wiki.md>) • [Music](<Music modding - Hearts of Iron 4 Wiki.md>) • [Sound](<Sound modding - Hearts of Iron 4 Wiki.md>)
- **Other**: [Console commands](<Console commands - Hearts of Iron 4 Wiki.md>) • [Troubleshooting](<Troubleshooting - Hearts of Iron 4 Wiki.md>) • [Mod structure](<Mod structure - Hearts of Iron 4 Wiki.md>) • [Mods](<Mods - Hearts of Iron 4 Wiki.md>)
