# Nudger

<!-- kit:begin id="review" build="1.19.4.1" checked="2026-11-01" revision="97432" sources="interface/nudge.gui interface/nudge.gfx interface/frontendmainview.gui map/buildings.txt map/unitstacks.txt map/supply_nodes.txt map/railways.txt map/weatherpositions.txt map/definition.csv map/strategicregions/ history/states/ buildings_nudger_markers.txt unit_nudger_markers.txt common/defines/00_graphics.lua documentation/console_commands_documentation.md" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Checked against: the nudger's own interface file `interface/nudge.gui` (every window and button label), `interface/frontendmainview.gui`, the map files the nudger reads and writes (row counts and column layout of `map/buildings.txt` and `map/unitstacks.txt`, sizes of the others), the two marker files in the game folder, the nudger define, the `nudge` console command, and class names in `hoi4.exe`.
Kit blocks added: the nudger menu in 1.19.3, the filled "Strategic regions", "Buildings", "Units" and "References and notes" sections, a folder name correction in "Weather".
Gaps left: the wiki's long behaviour descriptions (shift-click rules, save and update semantics, crash causes) cannot be checked from game files and are left as written. What the "Mark/Unmark", "Random" and "Validate" buttons do exactly, and what the marker files hold, is not documented, so those statements are marked `[unverified]`.
**1.19.4.1 re-check (2026-11-01).** 9 kit statements depended on files the update changed (`map/buildings.txt`, `history/states/`, the core localisation, the graphics defines and the strings and class names of `hoi4.exe`) and all were re-measured. One fact changed: the last column of the 2334 `floating_harbor` rows in `map/buildings.txt` is a land province, not a sea province (only the 2362 `naval_base_spawn` rows name a sea province). Every other statement cites files that are byte-identical in 1.19.4.1 (Steam depot manifest diff).
<!-- kit:end id="review" -->

<!-- kit:begin id="nudger-menu" at="section:overview" -->
The nudger menu as 1.19.3 defines it. The selection window is headed "Choose nudger" and lists, in this order: States, Supply Areas, Strategic Regions, Ambient objects, Database, Weather, Buildings, Units, Supply, and a "Leave Nudge" button. The main menu button is `nudge_button`, labelled "Nudge!". [vanilla-confirmed 1.19.3] `interface/nudge.gui`, `interface/frontendmainview.gui`

The console command `nudge` is documented as "Go to the nudge tool". [docs] `documentation/console_commands_documentation.md`

"Supply Areas" is still in the menu and `nudge_window_supplyarea` is still in the interface file (fields "Supply area name" and "Base value", buttons "Apply value", "Generate", "Regenerate All", "Open File", "Delete region", "Create region", "Update", "Save"). `hoi4.exe` has nudger classes for states, strategic regions, ambient objects, the database, weather, buildings, units and supply hubs, and none for supply areas, which fits the page's remark that the button does nothing. [vanilla-confirmed 1.19.3] `interface/nudge.gui`. The class list is [unverified] `hoi4.exe`. The button does nothing visible in 1.19.4.1: from the main menu "Nudge!", the "Choose nudger" list showed States, Supply Areas, Strategic Regions, Ambient objects, Database, Weather, Buildings, Units, Supply and Leave Nudge, and clicking Supply Areas changed nothing on screen, from the start view and from the States view, while clicking States switched the map to a state-border view. No file was written to the user folder. The exe class part was not checked, because no binary was inspected. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, Nudge from the main menu, screenshots.

The game's own map error text tells the player: "You can still access the Nudger to attempt to fix the issues", and after coming back from it, restart the game so everything reloads. [vanilla-confirmed 1.19.4.1] `localisation/english/core_l_english.yml` (`MAP_LOADING_ERROR_INGAME_MITIGATION`)
<!-- kit:end id="nudger-menu" -->

<!-- kit:begin id="nudger-buildings" at="section:buildings" -->
The Buildings section writes `map/buildings.txt` (to the user directory, like the other sections). The row layout is `state id;building id;x;y;z;rotation;province` (see the last column below) and is explained on [Map modding](map_modding.md#buildings) and [Building modding](building_modding.md#models). The output path is inferred from the file names in the exe. [unverified] `hoi4.exe`

What a correct vanilla file looks like, to check a nudged file against. All rows: [vanilla-confirmed 1.19.4.1] `map/buildings.txt`.

- 66664 rows, each with exactly 7 `;` separated columns, LF line ends, no final newline, coordinates with 2 decimals.
- State ids run from 1 to 1081 and every one of the 1081 files in `history/states/` has rows.
- Every state has exactly 1 `air_base`, 1 `rocket_site_spawn`, 1 `nuclear_reactor_spawn`, 1 `synthetic_refinery`, 1 `fuel_silo`, 1 `radar_station` and 1 `stronghold_network` row, 3 `anti_air_building` rows, 6 `arms_factory` rows and 6 `industrial_complex` rows.
- The last column is non-zero in all 4696 `naval_base_spawn` and `floating_harbor` rows and 0 in all other rows. It is a sea province in the 2362 `naval_base_spawn` rows and a land province in the 2334 `floating_harbor` rows.
- The page's overview says each state needs one province for the air base and the rocket site. The 1081 single `air_base` and `rocket_site_spawn` rows are the data behind that.
- The page warns that a new state without these rows crashes the game. Why it crashes is not stated in any game file. [unverified] `map/buildings.txt`

The window `nudge_window_buildings` has these controls. All rows: [vanilla-confirmed 1.19.3] `interface/nudge.gui`.

| Control | Label or key |
| --- | --- |
| Check boxes | "Show state only", "Show type only" |
| Lists | `templates_list` (building types), `instances_list` (placed instances) |
| Buttons | "Add", "Remove", "Clear state", "Remove All", "Open file" |
| Positioning | "Random In State", "Random All States", "Random All Unmarked" |
| Checking | "Validate In State" (key `v`), "Validate All States", "Find Error" (key `f`) |
| Marking | "Mark/Unmark" (key `m`) |
| Output | "Save", "Cancel" |
| Text boxes | `hints` and `message`, filled in by the game at run time |

What the buttons do is read from their labels; no game file describes them. In particular "Random" probably places models and "Validate" probably checks the rows against rules like the list above. [unverified] `interface/nudge.gui`

The define `DEFAULT_NUDGE_FLOATING_HARBOR_DIST = 7.0` is the default distance of a floating harbor from the coast in pixels, "for nudger". [vanilla-confirmed 1.19.4.1] `common/defines/00_graphics.lua`

The game folder holds `buildings_nudger_markers.txt` (874 bytes). Every byte is NUL (0x00), so it is not a readable text file; its name is also a string in `hoi4.exe`. It probably stores the marks set with "Mark/Unmark", but no game file says so. [vanilla-confirmed 1.19.4.1] `buildings_nudger_markers.txt`. The purpose is [unverified] `hoi4.exe`
<!-- kit:end id="nudger-buildings" -->

<!-- kit:begin id="nudger-strategic-regions" at="section:strategic-regions" -->
The strategic region window in `interface/nudge.gui`. All rows: [vanilla-confirmed 1.19.3] `interface/nudge.gui`.

| Part | Controls |
| --- | --- |
| Header | text "Strategic region name:" and a name box |
| File buttons | "Open File", "Delete region", "Create region", "Update", "Save" |
| Modifiers panel | heading "Modifiers", boxes "Name" and "Trigger", buttons "Update" and "Delete", a list of the region's modifiers |
| Naval Terrains panel | heading "Naval Terrains", ten buttons: the first is labelled "Default"; the other nine are all labelled "Supply Areas" in the file, which looks like a copy-paste placeholder |

The panels line up with the page's overview line "Edits the strategic region borders and, for naval regions, terrain and modifiers". What each button does is read from its label only. [unverified] `interface/nudge.gui`

The panel was seen in the running game. With Nudge! from the main menu and then Strategic Regions, the regions are coloured, and clicking a region (Eastern Germany) opened a panel with a region name field, the buttons Open File, Delete region, Update and Save, a Naval Terrains list with Default, Ocean, Fjords and Archipelagos, Shallow Sea and Deep Oceans, and a Modifiers block with Name, Trigger, Update and Delete. So the terrain list shows five terrain names and not the nine "Supply Areas" labels of the file. Open File showed nothing and opened no window, and no file changed in the install map folder or the scratch user folder. Update, Save, Delete region and the terrain and modifier buttons were not pressed, because the particle editor showed that debug tools can write into the game install at once, so what they do is still [unverified]. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, Nudge from the main menu, screenshot.

Vanilla has 304 strategic region files in `map/strategicregions/` (for example `1-Southern England.txt`). Their format is on [Map modding](map_modding.md#strategic-regions) and [Strategic region modding](strategic_region_modding.md). [vanilla-confirmed 1.19.3] `map/strategicregions/`
<!-- kit:end id="nudger-strategic-regions" -->

<!-- kit:begin id="nudger-weather-correction" at="section:weather" -->
The text above names `/Hearts of Iron IV/map/strategic_regions/`. The vanilla folder is `map/strategicregions/` without an underscore, as the States section writes it. [vanilla-confirmed 1.19.3] `map/strategicregions/`

`map/weatherpositions.txt` has one row per weather position: `region id;x;y;z;size`, with `size` either `small` or `big`. Vanilla has 588 rows over 287 regions (452 `big`, 136 `small`), for example `1;2781.24;9.90;1571.49;small`. [vanilla-confirmed 1.19.3] `map/weatherpositions.txt`. The first column is the strategic region id, the number at the start of the region's file name: all 287 distinct values match a region file, and 552 of 588 positions fall on a province that belongs to that region (checked with `map/provinces.bmp`, `map/definition.csv` and `map/strategicregions/`). [vanilla-confirmed 1.19.4.1] `map/weatherpositions.txt`
<!-- kit:end id="nudger-weather-correction" -->

<!-- kit:begin id="nudger-units" at="section:units" -->
The Units section writes `map/unitstacks.txt`. The row layout is `province id;type;x;y;z;rotation;offset`, with 39 types (0 Standstill ... 38 Victory point); the type table is on [Map modding](map_modding.md#unit-model-and-victory-point-positions). The output path is inferred from the file name in the exe. [unverified] `hoi4.exe`

Vanilla `map/unitstacks.txt`, as a reference for a nudged file. All rows: [vanilla-confirmed 1.19.3] `map/unitstacks.txt`.

- 265355 rows with 7 columns each, LF line ends, final newline present.
- Rows cover 13282 provinces. 132 provinces of `map/definition.csv` have no rows (ids 0, 1, 843, 1050 and others).
- 13281 provinces have exactly one type 0 (Standstill) row and exactly one type 38 (victory point) row. Province 13257 has rows for types 1 and 2 only, and no type 0 and no type 38 row. Type 38 exists for every province, not only for provinces that hold a victory point.
- The supply nudger takes the position of the "Standstill" model as the province's position, as the Supply section says, so a province without a type 0 row falls back to the middle of the province.
- The `offset` column holds small positive decimals (0.18 to 1.34 seen at the top of the file).

The window `nudge_window_units` has: "Save", "Cancel", "Mark/Unmark" (key `m`), "Auto in Prov" (key `a`), "Auto in All", a list `stacks_list` and a `hints` text box. All rows: [vanilla-confirmed 1.19.3] `interface/nudge.gui`. "Auto" probably generates positions for the selected province or for all provinces; that is read from the label only. [unverified] `interface/nudge.gui`

The game folder holds `unit_nudger_markers.txt` (13208 bytes), also all NUL bytes and named in `hoi4.exe`, probably the unit counterpart of the buildings marker file. [vanilla-confirmed 1.19.4.1] `unit_nudger_markers.txt`. The purpose is [unverified] `hoi4.exe`
<!-- kit:end id="nudger-units" -->

<!-- kit:begin id="nudger-references" at="section:references-and-notes" -->
Which file each nudger section works on, with the size of the vanilla file. The file names come from the page text; the sizes were counted in the installed game. All rows: [vanilla-confirmed 1.19.4.1] the files named in the table.

| Section | File | Vanilla size |
| --- | --- | --- |
| States | `history/states/*.txt` | 1081 files |
| States, Strategic regions | `map/strategicregions/*.txt` | 304 files |
| Buildings | `map/buildings.txt` | 66664 rows |
| Units | `map/unitstacks.txt` | 265355 rows |
| Supply | `map/supply_nodes.txt` | 727 lines |
| Supply | `map/railways.txt` | 909 lines |
| Weather | `map/weatherpositions.txt` | 588 rows |
| Database | `map/definition.csv` | 13414 lines (ids 0 to 13413) |
| Ambient objects | `map/ambient_object.txt` | see [Entity modding](entity_modding.md) |
| Supply areas | `map/supplyareas/` | 1 file, `1-SupplyArea.txt` |

Related pages: [Map modding](map_modding.md), [State modding](state_modding.md), [Strategic region modding](strategic_region_modding.md), [Supply areas modding](supply_areas_modding.md), [Building modding](building_modding.md), [Console commands](console_commands.md).

The nudger's own windows are in `interface/nudge.gui` (about 2760 lines) and its sprites in `interface/nudge.gfx`. [vanilla-confirmed 1.19.3] `interface/nudge.gui`, `interface/nudge.gfx`
<!-- kit:end id="nudger-references" -->
