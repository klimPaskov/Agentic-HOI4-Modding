# State modding

<!-- kit:begin id="review" build="1.19.4.1" checked="2026-11-01" revision="67186" sources="history/states/ common/state_category/ common/strategic_locations/ common/buildings/ map/ map/buildings.txt map/strategicregions/ localisation/english/strategic_region_names_l_english.yml documentation/effects_documentation.md documentation/triggers_documentation.md hoi4.exe" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Checked against: all 1081 vanilla state files (parsed, not sampled), the 13 state categories, `common/strategic_locations/documentation.md` and its vanilla file, and the owner and controller effects in the effects documentation.
Kit blocks added: file names and ids, the state category rules, `impassable` with `force_link_ownership_to`, resources and supply keys, history keys with the strategic location effects, owner and controller effects, the filled-in Buildings section, and corrections for the `airports.txt` note, the building list and the category table.
The "outdated" marker in the page is a phrase about unitstacks files, not a stale section. Still stale: the airport and rocket site note, the 12-row category table and the building list, all corrected below.
Gaps left: the wiki rule that date blocks run only for start dates strictly after the block date was not tested. Exe-only strings are tagged `[unverified]`.
**1.19.4.1 re-check (2026-11-01).** 21 tagged statements depended on files the update changed (13 state history files, `map/buildings.txt`, scripts scanned for effect counts, state names and building localisation, `hoi4.exe` strings) and all were re-measured. Numbers that moved: `victory_points` 1500 -> 1502, `add_core_of` 1531 -> 1529, `add_claim_by` 41 -> 43, files testing `has_dlc` 77 -> 78, state-level `air_base` entries 352 -> 353, `set_state_owner_to` 30 in 16 files -> 31 in 15, `transfer_state` 2278 in 152 files -> 2279 in 154, strategic location effects now sit in 15 files (not 16), state files with a `resources` block 512 -> 511 (one is commented out), and the exe has no `statetemplate.cpp` string any more. Every other statement cites files that are byte-identical in 1.19.4.1 (Steam depot manifest diff).
<!-- kit:end id="review" -->

<!-- kit:begin id="state-ids-files" at="section:mandatory" -->
Ids and file names in 1.19.4.1. All rows: [vanilla-confirmed 1.19.4.1] `history/states/` (1081 files).

- The ids are exactly 1 to 1081, each once, and every state has `name = "STATE_<id>"` (with the quotes). The English names are in `localisation/english/state_names_l_english.yml`.
- File names are irregular: 967 are `<id>-<name>.txt`, 113 are `<id> - <name>.txt` (spaces around the dash, for example `1014 - Bahrain.txt`) and one is `1013 -Musamdam.txt`. The wiki says the file name is not read, which fits these irregular names, so match files by the `id` inside, not by name.
- Every land province of `map/definition.csv` (10154 of them) is in exactly one state, no province is in two states, and 118 non-land provinces are listed in states too.
- Four files (`190-Kurzeme.txt`, `433-Rajputana.txt`, `440-West Punjab.txt`, `816-West Virginia.txt`) write `state_category` twice. Do not copy that.
<!-- kit:end id="state-ids-files" -->

<!-- kit:begin id="state-category-rule" at="section:mandatory" -->
`state_category` must name a category that exists in `common/state_category/`. The exe has the message " does not have a category defined." (in 1.19.4.1 no source file name `statetemplate.cpp` string is left next to it). `state_category = b8_missing` in `history/states/64-Brandenburg.txt` logged "State #64 does not have a category defined." at load, and at game start "64 -  Brandenburg has too many buildings : -9". The message names the state by number, not the category, and the fallback category the game uses was not read. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, one-mod launch, error.log read. For the effect and trigger the exe has "Invalid category in set_state_category effect" and "Invalid category in has_state_category trigger". [unverified] Strings found in `hoi4.exe` only, not run. All 1081 vanilla states name one of the 13 vanilla categories; 11 files put the name in quotes (`state_category = "pastoral"`), so quotes are accepted. [vanilla-confirmed 1.19.4.1] `history/states/`, `common/state_category/`

State scope has `set_state_category = <category>` (effect) and `has_state_category = <category>` (trigger). [docs] `documentation/effects_documentation.md`, `documentation/triggers_documentation.md`
<!-- kit:end id="state-category-rule" -->

<!-- kit:begin id="state-impassable" at="section:optional" -->
`impassable = yes` appears in 21 vanilla states, and all 21 also have `force_link_ownership_to = <state id>`, so the two always go together in vanilla. [vanilla-confirmed 1.19.4.1] `history/states/` (21 of 21; a 22nd file, `674-Central Australia.txt`, has both lines commented out)

```text
impassable = yes
force_link_ownership_to = 334 # Kalimantan
impassable_ignored_links = { 1024 } # Sabah
```

- `force_link_ownership_to` takes a state id: another, regional state (Kalimantan for Interior Borneo, Amazonas for most Deep Amazonas states). What exactly it links is not documented; the wiki says the provinces of an impassable state go to the controller of the nearest passable provinces. The exe prints "force_link_ownership_to is only effective when used on impassable states", and it does: `force_link_ownership_to = 10` on the passable state 64 logged that line at load and did nothing, as state 64 stayed with GER and not with the owner of state 10 (POL). [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, one-mod launch, error.log and a script probe read in game.log. The linking on an impassable state was not tested, so what it links rests on the wiki text. [unverified]
- `impassable_ignored_links = { <state id> ... }` is used once, in state 1022, and it is not documented anywhere in the game files. [vanilla-confirmed 1.19.4.1] `history/states/1022 - Interior Borneo.txt`
- The 21 states are 19 `wasteland` and 2 `enclave`, categories that both have 0 building slots. 18 vanilla states write `infrastructure = 0`. [vanilla-confirmed 1.19.4.1] `history/states/`, `common/state_category/`
- Trigger `impassable` (state scope) checks the flag. [docs] `documentation/triggers_documentation.md`
<!-- kit:end id="state-impassable" -->

<!-- kit:begin id="state-optional-keys" at="section:optional" -->
Base game resources in 1.19.3 are seven, not six: `oil`, `aluminium`, `rubber`, `tungsten`, `steel`, `chromium` and `coal`. See [Resources modding](resources_modding.md). 511 of 1081 vanilla state files have a `resources` block (`801-Moesia.txt` has one commented out). [vanilla-confirmed 1.19.4.1] `common/resources/00_resources.txt`, `history/states/`

`local_supplies` is in 1069 of 1081 vanilla states, with values from 0.0 to 16.0; 846 of them are 0.0. It replaces the supply area value (see [Supply areas modding](supply_areas_modding.md)). The wiki's "one unit equals 0.2 supply" is not stated in the game files. [vanilla-confirmed 1.19.4.1] `history/states/` for the counts. [unverified] for the 0.2 factor.

`buildings_max_level_factor` is set in 340 vanilla states (all `1.0`), although the wiki recommends avoiding it. [vanilla-confirmed 1.19.4.1] `history/states/`
<!-- kit:end id="state-optional-keys" -->

<!-- kit:begin id="state-history-keys" at="section:history" -->
What 1.19.4.1 state history files contain, by key. All rows: [vanilla-confirmed 1.19.4.1] `history/states/` (1081 files).

| Key inside `history = { }` | Files or uses |
| --- | --- |
| `owner` | 1081 (every state) |
| `buildings` | 1065 |
| `victory_points` | 1502 blocks |
| `add_core_of` | 1529 |
| `add_claim_by` | 43 |
| `strategic_province_location`, `strategic_state_location` | 16 and 8 (see below) |
| `add_dynamic_modifier`, `set_variable` | 21 and 23 |
| `set_compliance`, `set_resistance`, `start_resistance`, `set_demilitarized_zone` | 8, 7, 3 and 5 |
| `add_extra_state_shared_building_slots` | 2 |
| dated blocks such as `1939.1.1 = { }` | 13 distinct dates; `1939.1.1` is by far the most used (114 blocks) |
| `IF` / `if` blocks | 21; 78 files test `has_dlc` (most often "No Compromise, No Surrender") |

The wiki rule under History above, that a dated block runs only if the start date is strictly after its date, is wrong for the exact start moment. With the start at 1936.1.1.12 and `add_core_of = POL` in a dated block of state 64, the block dated `1936.1.1` ran, the one dated `1936.1.2` did not, and blocks dated `1936.1.1.12` (the exact start moment) and `1936.1.1.11` both ran, so a block runs when its date is the start date or earlier. The hour forms `.11` and `.12` were accepted without a date parse error. Core ownership was read with `is_core_of` in a probe, only one start date and one effect were tested. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, new game 1936, script probe read in game.log.

A different controller is written inside a dated block (for example `controller = JAP` under `1938.10.25 = { }` in Suzhou) or with `set_province_controller`. 61 of the 62 `controller = TAG` lines in vanilla state files sit inside a dated block or an `if`; the one at history level is in `764-West Banat.txt`. [vanilla-confirmed 1.19.4.1] `history/states/1034 - Suzhou.txt`, `history/states/764-West Banat.txt`
<!-- kit:end id="state-history-keys" -->

<!-- kit:begin id="state-owner-effects" at="section:history" -->
#### Setting owner and controller

Each pair has one effect per scope. The names differ by a `_to` suffix, and the argument is reversed. All rows: [docs] `documentation/effects_documentation.md` for scope and argument; the last column is [vanilla-confirmed 1.19.4.1] `common/`, `events/`, `history/`.

| Effect | Scope | Argument | Vanilla uses |
| --- | --- | --- | --- |
| `set_state_owner = <state id>` | country | the state | 0 |
| `set_state_owner_to = <TAG>` | state | the new owner | 31 in 15 files |
| `set_state_controller = <state id>` | country | the state | 79 in 9 files |
| `set_state_controller_to = <TAG>` | state | the new controller | 92 in 17 files |
| `transfer_state = <state id>` | country | the state; sets owner and controller | 2279 in 154 files |
| `transfer_state_to = <TAG>` | state | the new owner; sets owner and controller | 811 in 97 files |

```text
GER = { transfer_state = 64 }
64 = { set_state_owner_to = GER }
```

The country-scope forms are the ones to read as "this country takes that state". Vanilla never uses `set_state_owner`, so prefer `transfer_state` or `set_state_owner_to`. Also in state scope: `add_core_of`, `add_claim_by`, `remove_core_of`, `remove_claim_by`, `set_state_name`, `reset_state_name`, `set_demilitarized_zone`, `set_compliance`, `set_resistance`, `set_state_province_controller` (all [docs] `documentation/effects_documentation.md`).
<!-- kit:end id="state-owner-effects" -->

<!-- kit:begin id="state-strategic-locations" at="section:history" -->
#### Strategic locations

A strategic location is a named bonus (or malus) to the maximum level of province buildings, defined in `common/strategic_locations/` and attached to a province from state history. [docs] `common/strategic_locations/documentation.md`

```text
natural_harbor = {
	naval_base = 2
}
```

Vanilla defines four, each +2 to one building: `natural_harbor` (naval_base), `defensive_chokepoint` (bunker), `defensible_coastline` (coastal_bunker) and `favorable_approach` (air_base). A negative number lowers the maximum level (the documentation example uses `naval_base = -2`). [docs] `common/strategic_locations/documentation.md`. [vanilla-confirmed 1.19.3] `common/strategic_locations/strategic_locations.txt`

Apply them in state scope. The effect names in the effects documentation are the ones vanilla uses: `strategic_province_location` for the province form and `strategic_state_location` for the state form. [vanilla-confirmed 1.19.4.1] `history/states/526-Okinawa.txt` and 14 more files (24 uses: 8 `defensible_coastline`, 8 `favorable_approach`, 5 `natural_harbor`, 3 `defensive_chokepoint`)

```text
strategic_province_location = {
	defensible_coastline = 11932
}
strategic_state_location = {
	favorable_approach = 11932
}
```

Correction to the documentation file: it tells you to use an effect `strategic_location_building` and shows a `strategic_location = { }` wrapper. The effects documentation has no effect of that name; it lists `strategic_province_location` and `strategic_state_location`, although its own example text for the first still shows the old wrapper `strategic_location = { }`. No vanilla file uses `strategic_location_building` or `strategic_location`. [docs] `documentation/effects_documentation.md`. [vanilla-confirmed 1.19.4.1] `common/`, `events/`, `history/`

The right-hand number is a province id in both forms. The difference between the two effects is not explained in the game files; the docs call the first "add a strategic location to a province" and the second "add strategic locations to a state". [docs] `documentation/effects_documentation.md`
<!-- kit:end id="state-strategic-locations" -->

<!-- kit:begin id="state-notes-correction" at="heading:notes" -->
`map/airports.txt` and `map/rocketsites.txt` do not exist in 1.19.4.1 (the Map modding page says they were removed in patch 1.15), so the second paragraph below no longer applies. The positions of air bases, rocket sites and gun emplacements are now rows in `map/buildings.txt` (ids `air_base`, `rocket_site_spawn`, `anti_air_building` and so on). The exe still prints map errors such as "no air base site defined for state" and "no rocket site defined for state", so a state that lacks those rows is still reported. [vanilla-confirmed 1.19.4.1] folder listing of `map/`, row ids of `map/buildings.txt`. With every row of state 64 removed from `map/buildings.txt` the game logged "MAP_ERROR: no air base site defined for state 64", "MAP_ERROR: no rocket site defined for state 64" and a third line, "MAP_ERROR: no gun emplacement defined for state 64", at game start, and a history error for the same state from `history/units/GER_1936_air_bba.txt` ("State 64 has no air base"). The mod file had 72 fewer lines than the unmodified one, so one line beyond the rows of state 64 may have gone as well. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, one-mod launch, error.log read.

The strategic region rule below holds in vanilla: none of the 1081 states has provinces in two strategic regions. [vanilla-confirmed 1.19.4.1] `history/states/`, `map/strategicregions/`
<!-- kit:end id="state-notes-correction" -->

<!-- kit:begin id="state-buildings-fill" at="section:buildings" -->
What state history gives a state at start, from the 1081 vanilla files. All rows: [vanilla-confirmed 1.19.4.1] `history/states/`.

State-level entries (written directly in `buildings = { }`; the number is how many times the key is written, and the highest level used):

| Key | Entries | Highest level |
| --- | --- | --- |
| `infrastructure` | 1069 | 5 |
| `industrial_complex` | 531 | 11 |
| `air_base` | 353 | 10 |
| `arms_factory` | 257 | 10 |
| `dockyard` | 110 | 8 |
| `anti_air_building` | 18 | 5 |
| `fuel_silo` | 15 | 1 |
| `synthetic_refinery` | 9 | 3 |
| `radar_station` | 7 | 1 |

Province-level entries sit in a nested block `<province id> = { ... }` inside `buildings` (counts are entries): `naval_base` (536), `coastal_bunker` (59), `bunker` (55), `dam` (15), `naval_headquarters` (9), `naval_supply_hub` (8), `naval_facility` (8), `land_facility` (4), `air_facility` (4), one `dam_mountain`, and 21 `landmark_*` entries of 17 kinds (5 of them `landmark_great_wall_section`). `supply_node` and `rail_way` never appear in state history; they start from `map/supply_nodes.txt` and `map/railways.txt`.

```text
buildings = {
	infrastructure = 2
	air_base = 3
	11932 = {
		naval_base = 3
	}
}
```

- 117 `buildings` blocks sit inside a dated block or an `if` / `IF`, which is how the 1936 and 1939 starts differ. The numbers in a dated block are the new total level, not an addition (the wiki example shows `infrastructure = 4` in a `1939.1.1` block). [unverified] for the "total, not addition" reading; the wiki states it and vanilla is consistent with it.
- A level of 0 is legal: 18 states write `infrastructure = 0`.
- The wiki's rule that coastal-only buildings cannot be set in landlocked states matches `only_costal = yes` in `common/buildings/`, which `naval_facility`, `naval_base`, `coastal_bunker`, `dockyard`, `naval_supply_hub` and `naval_headquarters` carry. [vanilla-confirmed 1.19.3] `common/buildings/00_buildings.txt`
- Positions of the models are not in the state file. `map/buildings.txt` has one row per model (66664 rows in vanilla, 22 distinct ids); see [Map modding](map_modding.md#buildings). [vanilla-confirmed 1.19.4.1] `map/buildings.txt`
<!-- kit:end id="state-buildings-fill" -->

<!-- kit:begin id="state-building-types-correction" at="section:building-types" -->
The table is incomplete for 1.19.3. `common/buildings/` defines 55 buildings, not 32: the table lacks `cataract_dam_mountain` and 22 `landmark_*` buildings. The full list with level caps and flags is on [Building modding](building_modding.md#types). [vanilla-confirmed 1.19.3] `common/buildings/00_buildings.txt`, `common/buildings/01_landmark_buildings.txt`

The closing note is partly wrong for supply hubs. Vanilla script builds them with `add_building_construction = { type = supply_node province = <id> level = 1 instant_build = yes }` (72 blocks in 21 files), so the effect does not crash for `supply_node`. No vanilla file builds `rail_way` that way; railways go through `build_railway`. [vanilla-confirmed 1.19.4.1] `common/decisions/SIA.txt`, `common/decisions/GUAY_decisions.txt` and others
<!-- kit:end id="state-building-types-correction" -->

<!-- kit:begin id="state-categories-correction" at="section:state-categories" -->
Vanilla 1.19.3 has 13 categories (one file each in `common/state_category/`), not 12. The table above lacks `large_island`. The "only modifier" claim is also out of date: the island categories use a `buildings_max_level` block. All rows: [vanilla-confirmed 1.19.4.1] `common/state_category/*.txt`, `localisation/english/`.

| Internal name | Slots (`local_building_slots`) | `color` | Extra |
| --- | --- | --- | --- |
| `wasteland` | 0 | 40 40 40 | |
| `enclave` | 0 | 40 40 40 | |
| `tiny_island` | 0 | 40 40 40 | `buildings_max_level = { naval_base = 3 air_base = 2 }` |
| `pastoral` | 1 | 160 160 0 | |
| `small_island` | 1 | 200 160 0 | `buildings_max_level = { naval_base = 6 air_base = 4 }` |
| `large_island` | 3 | 200 160 0 | `buildings_max_level = { naval_base = 8 air_base = 6 }` |
| `rural` | 2 | 240 160 0 | |
| `town` | 4 | 200 200 0 | |
| `large_town` | 5 | 240 240 0 | |
| `city` | 6 | 0 200 0 | |
| `large_city` | 8 | 0 240 0 | |
| `metropolis` | 10 | 0 200 200 | |
| `megalopolis` | 12 | 0 240 240 | |

Each file is `state_categories = { <name> = { local_building_slots = N color = { r g b } } }`. Vanilla localises every category twice: plain keys such as `town: "Developed Rural Region"` (the names in the wiki table) and `STATE_CATEGORY_<name>` keys with shorter names such as `STATE_CATEGORY_town: "Town"`. [vanilla-confirmed 1.19.4.1] `localisation/english/`
<!-- kit:end id="state-categories-correction" -->
