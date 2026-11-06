# Map modding

<!-- kit:begin id="review" build="1.19.4.1" checked="2026-11-01" revision="105627" sources="map/ map/default.map map/definition.csv map/adjacencies.csv map/adjacency_rules.txt map/buildings.txt map/unitstacks.txt map/weatherpositions.txt map/ambient_object.txt map/cities.txt map/supply_nodes.txt map/railways.txt map/terrain/ map/strategicregions/ map/supplyareas/ common/terrain/00_terrain.txt common/defines/00_defines.lua common/defines/00_graphics.lua gfx/entities/trees.gfx hoi4.exe" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Checked against: the full `map/` folder of the installed game (every file listed, the bitmaps and DDS headers read, the CSV and text files parsed), `common/terrain/00_terrain.txt`, the river and supply defines, and map error strings in `hoi4.exe`.
Kit blocks added: the real file list and bitmap table, corrections for `weatherpositions.txt` sizes, line endings, the terrain palette ids 27 and 31, the terrain values, adjacency format and rules, plus counts, a defaults table for `default.map` and the map error texts the exe still holds.
The "deprecated" marker is the supply area note (still true; see the Supply areas page) and "incomplete" is about a definition file, not about the page.
Gaps left: exe-only strings are `[unverified]`. The wiki's size limits (13,238,272 pixels, 65536 borders) and the sea level of 9.5 are in no game file I could read; vanilla provinces.bmp is 11,534,336 pixels.
**1.19.4.1 re-check (2026-11-01).** 13 kit statements depended on files the update changed (`map/buildings.txt`, the defines file and the strings of `hoi4.exe`) and all were re-measured. One fact changed: all 2334 `floating_harbor` rows in `map/buildings.txt` name a land province in the last column, not a sea province. Every other statement cites files that are byte-identical in 1.19.4.1 (Steam depot manifest diff).
<!-- kit:end id="review" -->

<!-- kit:begin id="map-folder-1193" at="section:quick-overview" -->
The `map/` folder of 1.19.4.1, complete. All rows: [vanilla-confirmed 1.19.4.1] folder listing and file contents of `map/`.

| Entry | What it is |
| --- | --- |
| `default.map` | names the files it loads (keys at the end of this page); 13 active keys |
| `provinces.bmp`, `definition.csv`, `terrain.bmp`, `heightmap.bmp`, `rivers.bmp`, `trees.bmp`, `world_normal.bmp`, `cities.bmp` | the bitmaps and the province table (sizes and depths in the BMP section) |
| `adjacencies.csv`, `adjacency_rules.txt` | adjacencies and strait rules |
| `continent.txt` | 7 continents |
| `buildings.txt`, `unitstacks.txt`, `cities.txt`, `weatherpositions.txt`, `ambient_object.txt`, `supply_nodes.txt`, `railways.txt` | placement and start data; the exe holds these as fixed paths (`map/buildings.txt`, `map/unitstacks.txt`, `map/cities.txt`, `map/weatherpositions.txt`, `map/supply_nodes.txt`, `map/railways.txt`) |
| `seasons.txt` | 4 season blocks: `winter`, `spring`, `summer`, `autumn`, each with `start_date` and `end_date` written `00.<month>.<day>` (for example `00.12.01`) and `hsv_north` / `hsv_center` / `hsv_south` and `colorbalance_north` / `_center` / `_south` |
| `positions.txt` | listed in `default.map`, but the file is empty (0 bytes) |
| `colors.txt` | 200 lines of `color = { r g b }` [vanilla-confirmed 1.19.4.1] `map/colors.txt` (200 of 200 lines match). No game file explains the use [unverified] |
| `strategicregions/` | 304 region files (see Strategic region modding) |
| `supplyareas/` | one leftover file (see Supply areas modding) |
| `terrain/` | 64 DDS and BMP files: the atlases, colour maps, borders, river surface, mud, snow, fog of war and underwater textures |

`map/airports.txt` and `map/rocketsites.txt` are absent, which agrees with the wiki line above. [vanilla-confirmed 1.19.4.1] folder listing of `map/`
<!-- kit:end id="map-folder-1193" -->

<!-- kit:begin id="map-bitmap-table" at="section:bmp-format" -->
The vanilla bitmaps, read from their headers. All rows: [vanilla-confirmed 1.19.3] `map/*.bmp`. All are uncompressed.

| File | Size in pixels | Bit depth | DIB header size |
| --- | --- | --- | --- |
| `provinces.bmp` | 5632 x 2048 | 24 | 40 |
| `heightmap.bmp` | 5632 x 2048 | 8 | 40 |
| `rivers.bmp` | 5632 x 2048 | 8 | 40 |
| `cities.bmp` | 5632 x 2048 | 8 | 40 |
| `terrain.bmp` | 5632 x 2048 | 8 | 124 |
| `trees.bmp` | 1650 x 600 | 8 | 124 |
| `world_normal.bmp` | 2816 x 1024 | 24 | 40 |

Two vanilla files, `terrain.bmp` and `trees.bmp`, carry a 124-byte header (the BITMAPV5HEADER the section above says the game does not recognise), so the statement is not true for every bitmap; the wiki's advice to export with BITMAPINFOHEADER (40 bytes) still matches the other six. [vanilla-confirmed 1.19.3] `map/terrain.bmp`, `map/trees.bmp`. A `terrain.bmp` of 8 bit, 5632 x 2048 with a 40-byte header was accepted by the game: no new error.log line against the clean control, no crash, and a new game started. The terrain was not screenshotted or compared, so a silent fallback to the vanilla picture is not excluded. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, one-mod launch, error.log read. The same loader does check `rivers.bmp` (see the rivers notes below). What the engine accepts for the other bitmaps was not tested. [unverified]

`trees.bmp` is exactly 75/256 of the province bitmap in each direction (5632 x 75 / 256 = 1650, 2048 x 75 / 256 = 600), and `world_normal.bmp` and the colour maps are half size. The province-sized bitmaps and `world_normal.bmp` are multiples of 256; `trees.bmp` (1650 x 600) is not, so the multiple-of-256 rule applies to the province bitmap and its full-size companions only. [vanilla-confirmed 1.19.3] `map/*.bmp`
<!-- kit:end id="map-bitmap-table" -->

<!-- kit:begin id="map-weatherpositions-correction" at="section:weather" -->
The two sizes in `weatherpositions.txt` are `small` and `big`, not `large`. Vanilla has 588 rows: 452 `big` and 136 `small`, in the layout `region id;x;y;z;size` (for example `1;2781.24;9.90;1571.49;small`). [vanilla-confirmed 1.19.3] `map/weatherpositions.txt`

The `period` keys vanilla actually uses, including `arctic_water`, and the `naval_terrain` and `static_modifiers` keys of a region are listed in [Strategic region modding](strategic_region_modding.md). [vanilla-confirmed 1.19.3] `map/strategicregions/`
<!-- kit:end id="map-weatherpositions-correction" -->

<!-- kit:begin id="map-definition-facts" at="section:provinces" -->
The line ending advice is not a general rule in 1.19.3. Vanilla `map/definition.csv` has LF-only line endings (13413 line feeds, no carriage return), and so do `adjacencies.csv`, `railways.txt` and `supply_nodes.txt`. The game loads these, so CRLF is not required for them. The "has no continent" error for every province has some other cause; the wiki's CRLF explanation covers at most files saved by some editors. [vanilla-confirmed 1.19.3] `map/definition.csv`, `map/adjacencies.csv`, `map/railways.txt`, `map/supply_nodes.txt`

What vanilla `definition.csv` contains. All rows: [vanilla-confirmed 1.19.3] `map/definition.csv`.

- 13414 rows, ids 0 to 13413 with no gap. Row 0 is `0;0;0;0;land;false;unknown;0`. There is no header row, no BOM and no final newline.
- Types: 10155 `land` (including row 0), 3133 `sea`, 126 `lake`. Every sea province has terrain `ocean`, every lake has `lakes`, and `unknown` is used only by row 0.
- Land terrain counts: plains 3031, forest 2364, mountain 1708, hills 1352, desert 815, jungle 477, urban 265, marsh 142.
- Continents: 1 Europe 3321, 2 North America 1157, 3 South America 558, 4 Australia 376, 5 Africa 743, 6 Asia 3560, 7 Middle East 489; 3133 sea provinces have 0 and so do 76 of the 126 lakes (the other 50 lakes have a continent), which agrees with the wiki ("lakes may be kept at 0").
- The 5th field `true` / `false` is the coastal flag, written as in the wiki's example.

The exe still contains these map error texts (strings only, not run): "Map invalid X crossing. Please fix pixels at coords:", "has TOO LARGE BOX. Perhaps pixels are spread around the world in provinces.bmp", "has only", "prov %d has no continent", "Bitmap and province definition disagree on whether or not province", "has no pixels in provinces.bmp", and "We do not support bitdepth at". They match the list above. Two of these texts were produced in the game. A province with its continent field set to 0 logged "prov 2 has no continent". A province row with no pixels logged "Province <n> has no pixels in provinces.bmp", both for a deleted row (province 3) and for an extra row with the colour 254, 254, 254 (province 13414). Deleting the row of province 3 also cascaded into 10739 error.log entries, among them 4561 coastal disagreements, 3099 "map building location is not over the land", 486 "The land province N -  has no state" and 17 "Naval strategic region ... is fractioned!". [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, one-mod launches, error.log read. For the corrected copy of the table the exe holds the string `.fixed.csv` (next to `.cache` and `lake`) and no `definition.csv.fixed`, so the file name given above may be stale. No file ending in `.fixed.csv` appeared in the install map folder or in the user folder after those runs, but the runner kept no before-and-after file list, so the name and the cases that write a corrected copy are still not known. [unverified] Exe strings only (`hoi4.exe`).
<!-- kit:end id="map-definition-facts" -->

<!-- kit:begin id="map-continent-note" at="section:continents" -->
`map/continent.txt` in 1.19.3 has exactly the seven names in the table below, in that order (`europe`, `north_america`, `south_america`, `australia`, `africa`, `asia`, `middle_east`); ids 1 to 7 follow the order. [vanilla-confirmed 1.19.3] `map/continent.txt`
<!-- kit:end id="map-continent-note" -->

<!-- kit:begin id="map-terrain-graphical-corrections" at="section:terrain" -->
The graphical terrain table above has errors against the 1.19.3 palette of `map/terrain.bmp` and its use. All rows: [vanilla-confirmed 1.19.3] `map/terrain.bmp` (palette and pixel counts), `common/terrain/00_terrain.txt`.

- The colours of ids 27 and 31 are swapped: palette index 27 is `(27, 27, 27)` and index 31 is `(243, 199, 147)`. The rest of those two rows (atlas tile 7 for 27, tile 15 for 31, type `mountain`) matches the terrain file.
- Id 31 is used: 2589 pixels in vanilla. Id 27 is used by 18 pixels. Only ids 14 (`lakes`, texture 255) and 18 are unused in the vanilla bitmap.
- Id 22 is used, by 208146 pixels (type `jungle`, atlas tile 5), so "never used in base game" is wrong for it; id 21 uses 30662 pixels.
- A handful of stray pixels use ids outside the table (48, 61, 63, 64, 74, 77 and 80).
- Id 15 is the sea (7.2 million pixels). Ids 16 and 19 are the permanent-snow variants (`perm_snow = yes`).
<!-- kit:end id="map-terrain-graphical-corrections" -->

<!-- kit:begin id="map-terrain-values" at="section:provincial-terrain" -->
The provincial terrain values in the table above (the "optimal combat width" notes and the shallow sea and deep ocean notes) do not match the terrain file of 1.19.3. Vanilla sets `combat_width` and `combat_support_width` directly in each category. All rows: [vanilla-confirmed 1.19.3] `common/terrain/00_terrain.txt`.

| Terrain | `movement_cost` | `combat_width` / `combat_support_width` | `units` attack | `attrition` | `buildings_max_level` bunker / coastal | `supply_flow_penalty_factor` | `truck_attrition_factor` |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `forest` | 1.5 | 60 / 30 | -0.15 | | 4 / 6 | 0.08 | 0.2 |
| `hills` | 1.5 | 70 / 35 | -0.25 | | 5 / 6 | 0.1 | 0.2 |
| `mountain` | 2.0 | 50 / 25 | -0.5 | 0.3 | 4 / 6 | 0.12 | 1.0 |
| `plains` | 1.0 | 70 / 35 | | | 5 / 6 | | |
| `urban` | 1.2 | 80 / 40 | -0.3 | | 5 / 6 | -0.2 | |
| `jungle` | 1.5 | 60 / 30 | -0.3 | 0.2 | 3 / 6 | 0.16 | 3.0 |
| `marsh` | 2.0 | 50 / 25 | -0.4 | 0.35 | 3 / 6 | 0.16 | 4.0 |
| `desert` | 1.05 | 70 / 35 | | 0.15 | 4 / 6 | 0.14 | 0.5 |

`sickness_chance = 1.0` is set on `jungle`, `marsh` and `desert`. `ai_terrain_importance_factor` ranges from 0.1 (`plains`) to 10.0 (`mountain`) and `match_value` from 0.5 to 10. `enemy_army_bonus_air_superiority_factor` is set on forest (-0.1), hills (-0.05), mountain (-0.1), urban (-0.5) and jungle (-0.25). [vanilla-confirmed 1.19.3] `common/terrain/00_terrain.txt`

Naval terrains (`naval_terrain = yes`, `is_water = yes`): `ocean` has `naval_mine_hit_chance = -0.75` and `minimum_seazone_dominance = 250`. `water_fjords` gives -0.2 attack, movement and defence to battle cruisers, battleships, heavy cruisers and carriers (+0.2 fuel use), `navy_visibility = -0.2`, `positioning = -0.15`, dominance 100. `water_shallow_sea` has `submarine = { navy_visibility = 0.33 }` (not +100%), `positioning = -0.05`, `naval_mine_hit_chance = -0.5`, dominance 100. `water_deep_ocean` gives -0.2 to destroyers and -0.1 to light cruisers (attack, movement, defence), submarines -0.15 visibility and -0.25 movement, `naval_mine_hit_chance = -0.95` (not "halved") and dominance 250. `lakes` has no `naval_terrain`. [vanilla-confirmed 1.19.3] `common/terrain/00_terrain.txt`. Keys the page does not list: `naval_mine_hit_chance`, `minimum_seazone_dominance`, `truck_attrition_factor`. [docs] `documentation/modifiers_documentation.md` has `naval_mine_hit_chance` and `truck_attrition_factor`; `minimum_seazone_dominance` is in no documentation file.
<!-- kit:end id="map-terrain-values" -->

<!-- kit:begin id="map-graphical-terrain-dds" at="section:graphical-terrain" -->
The `terrain = { }` block of `common/terrain/00_terrain.txt` has 25 entries in 1.19.3. Names repeat (three blocks are called `desert`, two `jungle_blend_18`), which agrees with the wiki ("the name is irrelevant"). Vanilla uses `spawn_city = yes` once (id 13, `urban`) and `perm_snow = yes` twice (ids 16 and 19). Lakes use `texture = 255`. [vanilla-confirmed 1.19.3] `common/terrain/00_terrain.txt`

`atlas0.dds` and `atlas_normal0.dds` are 2048 x 2048 DXT5 with 10 mip levels, `atlas1.dds` is 1024 x 1024 and `atlas2.dds` 512 x 512, all DXT5. That is the 4 x 4 grid of 512 x 512 tiles the wiki describes. [vanilla-confirmed 1.19.3] DDS headers of `map/terrain/atlas*.dds`
<!-- kit:end id="map-graphical-terrain-dds" -->

<!-- kit:begin id="map-rivers-defines" at="section:rivers" -->
The palette in the table above matches vanilla `rivers.bmp` exactly (indices 0 to 11), and its DIB header says 0 colours, as the page says. Pixel indices 254 and 255 are the "comment" colours (7.5 and 4.0 million pixels); indices 5 and 8 are not used in vanilla. [vanilla-confirmed 1.19.3] `map/rivers.bmp`

The defines behind it, all [vanilla-confirmed 1.19.4.1] `common/defines/00_defines.lua`: `RIVER_SMALL_START_INDEX = 0`, `RIVER_SMALL_STOP_INDEX = 6`, `RIVER_LARGE_STOP_INDEX = 11` (matching "0 to 6 small, up to 11 large"), `RIVER_CROSSING_PENALTY = -0.3` and `RIVER_CROSSING_PENALTY_LARGE = -0.6`, `RIVER_CROSSING_SPEED_PENALTY = -0.25` and `..._LARGE = -0.5`, `NSupply.RIVER_RAILWAY_LEVEL = 1` and `NSupply.SUPPLY_FLOW_PENALTY_CROSSING_RIVERS = 0.2`.

The exe also holds "MAP_ERROR: Bitdepth of rivers.bmp does not equal 8" and "MAP_ERROR: Size of the world map [...] is not equal to the size of rivers.bmp". Both are produced at load. A 24 bit `rivers.bmp` of the full size 5632 x 2048 logged "MAP_ERROR: Bitdepth of rivers.bmp does not equal 8", and the game kept running and started a new game. An 8 bit `rivers.bmp` of half the size (2816 x 1024) logged "MAP_ERROR: Palette in rivers.bmp is probably not correct" and "MAP_ERROR: Size of the world map [5632, 2048] is not equal to the size of rivers.bmp [2816, 1024]", and then the game crashed at load (EXCEPTION_ACCESS_VIOLATION) in the same second as the size line. The palette of the half-size test file differed from the vanilla one, so the crash may come from the size or from the palette. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, one-mod launches, error.log and the crash folder read.
<!-- kit:end id="map-rivers-defines" -->

<!-- kit:begin id="map-trees-facts" at="section:trees" -->
The palette ids and colours in the table above match vanilla `trees.bmp`. Vanilla pixels use only 0 (empty) and the ids 2, 3, 5, 6, 11, 28 and 29. The models are `pdxmesh` entries named `mapobject_<id>` in `gfx/entities/trees.gfx` (7 entries: 2, 3, 5, 6, 11, 28, 29), for example `mapobject_5` with `file = "gfx/models/mapitems/trees/forest_dunge_blend.mesh"` and `scale = 1`. [vanilla-confirmed 1.19.3] `map/trees.bmp`, `gfx/entities/trees.gfx`

`map/default.map` has a line `tree = { 3 4 7 10 }` ("which indices in trees.bmp palette should count as trees for automatic terrain assignment"). Those four ids are not the ids the vanilla bitmap uses, so do not derive the model ids from it. [vanilla-confirmed 1.19.3] `map/default.map`
<!-- kit:end id="map-trees-facts" -->

<!-- kit:begin id="map-colourmap-formats" at="section:colour-maps" -->
Only `colormap_rgb_cityemissivemask_a.dds` follows the "8.8.8.8 ARGB, 32-bit, no mipmaps" rule: it is 2816 x 1024, uncompressed 32-bit, one mip level. The water colour maps are DXT5: `colormap_water_0.dds` is 2816 x 1024, `_1` 1408 x 512 and `_2` 704 x 256, all without mip levels. [vanilla-confirmed 1.19.3] DDS headers of `map/terrain/colormap_*.dds`
<!-- kit:end id="map-colourmap-formats" -->

<!-- kit:begin id="map-buildings-ids" at="section:buildings" -->
The second column of `map/buildings.txt` is a building id or, for a building that sets `spawn_point = X` in `common/buildings/`, the spawn point name `X`; the list of 22 ids and the per-building details are in [Building modding](building_modding.md#models). In vanilla all 2362 `naval_base_spawn` rows have a sea province in the last column, all 2334 `floating_harbor` rows have a land province there, and all 10154 `supply_node` rows have 0. The file has 66664 rows. [vanilla-confirmed 1.19.4.1] `map/buildings.txt`, `map/definition.csv`

The exe prints ": map building location is not over the land ..." for a row whose position is not over a land province. A row `1;arms_factory;10.00;10.00;10.00;0.00;0` appended as the last line of `map/buildings.txt` (line 66665) logged "map/buildings.txt error at line 66665: map building location is not over the land - ignoring instance." at game start, so the row is dropped. A second line, "map/buildings.txt error at line 66666: invalid arguments count.", followed for the next line number, and the cause of that one was not checked. The text says "not over the land", not "not over a land province". [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, one-mod launch, error.log read.
<!-- kit:end id="map-buildings-ids" -->

<!-- kit:begin id="map-unitstacks-facts" at="section:unit-model-and-victory-point-positions" -->
Vanilla `unitstacks.txt` has 265355 rows and uses all 39 types 0 to 38. Type 38 (victory point) has 13281 rows. The exe prints "map/unitstacks.txt: Invalid province id: ... at line:" for a bad province id. [vanilla-confirmed 1.19.3] `map/unitstacks.txt`. The game logs it, with the wording "Error in map/unitstacks.txt at line: <n>: Invalid province id:99999" (no space after the colon). A row `99999;0;3429.00;9.85;1699.00;0.00;0.30` appended as the last line of the file (line 265356) logged "Error in map/unitstacks.txt at line: 265355: Invalid province id:99999" at game start, so the reported line number was one lower than the row's position counted from 1. That off-by-one was seen once, and the `buildings.txt` message above matches the 1-based line. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, one-mod launch, error.log read.
<!-- kit:end id="map-unitstacks-facts" -->

<!-- kit:begin id="map-adjacency-facts" at="section:adjacencies" -->
The real file has a header row, which the format line above does not show: `From;To;Type;Through;start_x;start_y;stop_x;stop_y;adjacency_rule_name;Comment`. The closing line is `-1;-1;;-1;-1;-1;-1;-1;-1` (note the empty third field, and a trailing space in the vanilla file), not nine `-1`. A line starting with `#` is a comment (one in vanilla). [vanilla-confirmed 1.19.3] `map/adjacencies.csv` (253 lines)

Vanilla has 251 entries: 151 `sea`, 93 `impassable`, and 7 with an empty type. The 7 empty-type entries are strait entries between provinces that already border each other: they set `Through` to -1 and only name a rule (`GIBRALTAR_STRAIT` twice, `DANISH_BELTS_STRAIT`, `BOSPHORUS_STRAIT`, `DARDANELLES_STRAIT`, `HORMUZ_STRAIT`, `OTRANTO_STRAIT`). The sea entries that name a rule are `PANAMA_CANAL`, `KIEL_CANAL` and `SUEZ_CANAL`. The file is UTF-8 without BOM with LF line endings. [vanilla-confirmed 1.19.3] `map/adjacencies.csv`
<!-- kit:end id="map-adjacency-facts" -->

<!-- kit:begin id="map-adjacency-rule-facts" at="section:adjacency-rules" -->
The rule names are referenced from `map/adjacencies.csv` (plural), not `adjacency.csv`. The vanilla file `map/adjacency_rules.txt` starts with `# A` (ASCII, no BOM) and defines 9 rules: `SUEZ_CANAL`, `GIBRALTAR_STRAIT`, `DANISH_BELTS_STRAIT`, `PANAMA_CANAL`, `BOSPHORUS_STRAIT`, `DARDANELLES_STRAIT`, `KIEL_CANAL`, `HORMUZ_STRAIT`, `OTRANTO_STRAIT`. [vanilla-confirmed 1.19.3] `map/adjacency_rules.txt`, `map/adjacencies.csv`

Keys the page does not describe, from the header comment of the vanilla file. All rows: [vanilla-confirmed 1.19.3] `map/adjacency_rules.txt`.

- Optional triggers `is_enemy`, `is_friend` and `is_neutral` are checked in that order and can override the relation: with `is_friend` false the neutral rule is used instead of the friend rule, and so on (the comment at the top of the file spells out the order). Vanilla uses only `is_friend`, in `BOSPHORUS_STRAIT` and `DARDANELLES_STRAIT`, with a trigger of the form `TUR_is_friend_for_bosphorus = yes`.
- Each of the four relation blocks `contested`, `enemy`, `friend`, `neutral` has `army`, `navy`, `submarine` and `trade` (36 blocks of each key in vanilla).
- `is_disabled` is used in 5 of the 9 rules, with a `tooltip` key; `has_country_flag`, `has_global_flag` and `has_dynamic_modifier` (with `scope` and `modifier`) appear inside these trigger blocks.
- `required_provinces`, `icon` and `offset` are present in all 9 rules; `offset` is three numbers (vanilla example `offset = { -31.0 0.0 -2.0 }`).
<!-- kit:end id="map-adjacency-rule-facts" -->

<!-- kit:begin id="map-supply-facts" at="section:supply" -->
The formats match vanilla. `map/supply_nodes.txt` has 727 rows, all level 1 (the wiki's limit of 1 holds), and `map/railways.txt` has 909 rows with levels 1 to 4 in use (the define `NSupply.MAX_RAILWAY_LEVEL` is 5), whose second number is the count of provinces listed after it in every row. Both files are LF-only, and the supply rows are space separated with a trailing space. The supply system around them, including the state key `local_supplies` and the defines, is described in [Supply areas modding](supply_areas_modding.md). [vanilla-confirmed 1.19.4.1] `map/supply_nodes.txt`, `map/railways.txt`, `common/defines/00_defines.lua`
<!-- kit:end id="map-supply-facts" -->

<!-- kit:begin id="map-supply-areas-1193" at="heading:supply-areas-for-versions-prior-to-111" -->
The deprecation note below is still accurate for 1.19.4.1: the folder `map/supplyareas/` is not listed in `default.map`, and the exe has no path string for it. The game still ships one file there (`1-SupplyArea.txt`, a single area with `value=12` over states 5, 85, 763 and 807). Do not create supply areas for a new map; see [Supply areas modding](supply_areas_modding.md). [vanilla-confirmed 1.19.3] `map/supplyareas/1-SupplyArea.txt`, `map/default.map`. [unverified] for the exe, which was searched for strings only.
<!-- kit:end id="map-supply-areas-1193" -->

<!-- kit:begin id="map-ambient-facts" at="section:ambient-objects" -->
Vanilla `ambient_object.txt` has 6 `type = { }` blocks: `ambient_wind_entity`, `ambient_water_entity`, `frame_border_entity`, `frame_border_bottom_entity`, `frame_border_logo_entity` and `chinese_wall_entity`. The `frame_border_*` entities are most likely the map frame the page mentions. [unverified] The object names and positions show the sides: `frame_border_entity_top` sits at z 2190 (north of the 2048-pixel map) and `frame_border_bottom_entity_bottom` at z -140 (south). [vanilla-confirmed 1.19.4.1] `map/ambient_object.txt`. The `type` value is quoted (`type="ambient_wind_entity"`), and all six entities are defined in `gfx/entities/mapitems.asset`. [vanilla-confirmed 1.19.3] `map/ambient_object.txt`, `gfx/entities/mapitems.asset`

Keys in use: `type`, `use_animation` (always `no`), `always_visible` (5 blocks), `scale` (values 0.2, 10, 100, 100, 300) and `object = { name position rotation }` (position and rotation are three numbers). `time_duration` from the list above does not appear in the vanilla file, but the exe knows the key. [vanilla-confirmed 1.19.3] `map/ambient_object.txt`. [unverified] for the exe.
<!-- kit:end id="map-ambient-facts" -->

<!-- kit:begin id="map-default-map-keys" at="bottom" -->
## Default.map, cities.txt and the map error texts

`map/default.map` in 1.19.3. All rows: [vanilla-confirmed 1.19.3] `map/default.map`.

| Key | Vanilla value |
| --- | --- |
| `definitions` | `"definition.csv"` |
| `provinces` | `"provinces.bmp"` |
| `positions` | `"positions.txt"` (the file is empty) |
| `terrain` | `"terrain.bmp"` |
| `rivers` | `"rivers.bmp"` |
| `heightmap` | `"heightmap.bmp"` |
| `tree_definition` | `"trees.bmp"` |
| `continent` | `"continent.txt"` |
| `adjacency_rules` | `"adjacency_rules.txt"` |
| `adjacencies` | `"adjacencies.csv"` |
| `ambient_object` | `"ambient_object.txt"` |
| `seasons` | `"seasons.txt"` |
| `tree` | `{ 3 4 7 10 }`, a list of palette ids |
| `climate` | commented out (`#climate = "climate.txt"`) |

`map/cities.txt` starts with `types_source = "map/cities.bmp"`, `pixel_step_x = 2` and `pixel_step_y = 2`, then 4 `city_group = { color_index = N density = X building = { distance = D mesh = { "<mesh name>" } } ... }` blocks. `color_index` is the palette index in `cities.bmp`, `density` the share of pixels that get a model, and the `building` entries are sorted by growing `distance` from the edge of the urban area. [vanilla-confirmed 1.19.3] `map/cities.txt`

Other map error texts still in `hoi4.exe` (strings only, nothing was run). [unverified] Exe strings only.

| Text (fragment) | Looks like |
| --- | --- |
| "Strategic region ... is fractioned! The following provinces are separated from the rest" | a region whose provinces are not connected |
| "The land province ... has no strategic region assigned" | a land province missing from `map/strategicregions/` |
| "Definition for state id ... belonging to different strategic areas" | a state split over two regions |
| "Invalid adjacency rule name" | a rule name in `adjacencies.csv` that `adjacency_rules.txt` lacks |
| "Province is invalid or added twice to the same or different rules" | a duplicate in `required_provinces` |
| "no air base site defined for state", "no rocket site defined for state", "no gun emplacement defined for state" | a state without the matching rows in `map/buildings.txt` |
| "Errors while reading cities.txt" | a broken `cities.txt` |
<!-- kit:end id="map-default-map-keys" -->
