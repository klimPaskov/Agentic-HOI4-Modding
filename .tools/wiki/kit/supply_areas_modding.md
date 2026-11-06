# Supply areas modding

<!-- kit:begin id="review" build="1.19.4.1" checked="2026-11-01" revision="67235" sources="map/supplyareas/ map/supply_nodes.txt map/railways.txt map/default.map history/states/ common/buildings/00_buildings.txt common/defines/00_defines.lua common/terrain/00_terrain.txt localisation/english/supply_area_names_l_english.yml interface/nudge.gui documentation/effects_documentation.md documentation/triggers_documentation.md hoi4.exe" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Checked against: the `map/` folder listing, `map/supply_nodes.txt` and `map/railways.txt` (parsed in full), the state files, the supply defines and the exe's file path strings.
Kit blocks added: one correction (supply areas are vestigial in 1.19.3 and what replaced them) and a table of the new system with vanilla counts.
The "deprecated" marker holds: no vanilla script or exe path string refers to the area format. The game still ships one leftover file, described below.
Gaps left: whether the engine still parses `map/supplyareas/` could not be tested; the `[unverified]` tags say so.
**1.19.4.1 re-check (2026-11-01).** 6 kit statements depended on files the update changed (state history, the defines file, scripts scanned for supply and railway use, and the strings of `hoi4.exe`) and all were re-measured. Changed: the effect `build_railway` has 222 lines in 45 files (the old 231 also counted `can_build_railway`), and `type = rail_way` is now also used by a `damage_building` call in `common/on_actions/08_bba_on_actions.txt`. Every other statement cites files that are byte-identical in 1.19.4.1 (Steam depot manifest diff).
<!-- kit:end id="review" -->

<!-- kit:begin id="supply-areas-vestigial" at="top" -->
The format on this page is not used by 1.19.3, and a new map does not need it. The evidence below points that way, and in 1.19.4.1 the game does not parse the folder: a valid `map/supplyareas/2-SupplyArea.txt` (`id=2`, `name="SUPPLYAREA_2"`, `value=999`, `states={ 5 }`) and a garbage file (`this is garbage { text ] = =`) both logged no new line in error.log and no mention of the file in any log, and the game did not crash and started a new game. This rests on the absence of a parse error. The supply map mode and the supply of state 5 were not read, and a map built without the folder was not tried. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, one-mod launches, error.log read.

- `map/supplyareas/` still exists in 1.19.3 but holds one file, `1-SupplyArea.txt`, with a single area: `id=1`, `name="SUPPLYAREA_1"`, `value=12`, `states = { 5 85 763 807 }`. [vanilla-confirmed 1.19.3] `map/supplyareas/1-SupplyArea.txt`
- `localisation/english/supply_area_names_l_english.yml` still defines `SUPPLYAREA_1` to `SUPPLYAREA_357`, all with the text "SupplyArea". [vanilla-confirmed 1.19.3] `localisation/english/supply_area_names_l_english.yml`
- `hoi4.exe` holds the file path strings `map/supply_nodes.txt` and `map/railways.txt` but no string `supplyareas` or `supply_area` as a path. [unverified] Exe string search only.
- `map/default.map` does not list the folder, and no vanilla script mentions `supply_area`. The only other trace is a "Supply Areas" checkbox in `interface/nudge.gui` (the nudger window). [vanilla-confirmed 1.19.4.1] `map/default.map`, `interface/nudge.gui`
<!-- kit:end id="supply-areas-vestigial" -->

<!-- kit:begin id="supply-replacement" at="bottom" -->
## What replaced supply areas

Supply since 1.11 comes from supply nodes joined by railways, plus a per-state number. All rows: [vanilla-confirmed 1.19.4.1] `map/supply_nodes.txt`, `map/railways.txt`, `history/states/`, `common/buildings/00_buildings.txt`, `common/terrain/00_terrain.txt`, `common/defines/00_defines.lua`.

| Part | Where | Vanilla 1.19.4.1 |
| --- | --- | --- |
| Starting supply nodes | `map/supply_nodes.txt`, one row `<level> <province>` per line | 727 rows, all level 1, 727 different provinces |
| Starting railways | `map/railways.txt`, one row `<level> <count> <province> <province> ...` | 909 rows; levels used are 1 (467 rows), 2 (406), 3 (29) and 4 (7); `<count>` is the number of provinces listed in all 909 rows; 2 to 19 provinces per row |
| Node and railway as buildings | `common/buildings/00_buildings.txt`: `supply_node` and `rail_way`, both `province_max = 1` | `supply_node` costs 20000 and `rail_way` 170 plus 130 per level; the railway level cap comes from the define `NSupply.MAX_RAILWAY_LEVEL = 5` (`common/defines/00_defines.lua`) |
| Base supply of a state | `local_supplies = <number>` in the state file | present in 1069 of 1081 states; values 0.0 to 16.0; 846 of them are 0.0 |
| Terrain effect | `supply_flow_penalty_factor` in `common/terrain/00_terrain.txt` | for example 0.08 forest, 0.12 mountain, 0.14 desert, 0.16 jungle and marsh, -0.2 urban |
| Tuning | `NSupply` defines | `CAPITAL_*`, `NODE_*`, `NAVAL_BASE_*`, `FLOATING_HARBOR_*` and `RAILWAY_*` families, `INFRA_TO_SUPPLY = 0.3`, `RIVER_RAILWAY_LEVEL = 1` |

Script that works on this system. All rows: [docs] `documentation/effects_documentation.md`, `documentation/triggers_documentation.md`, `documentation/modifiers_documentation.md`.

| Name | Kind and scope | Use |
| --- | --- | --- |
| `build_railway` | effect, any scope | `level`, and a path by `path = { ... }`, by `start_province` / `target_province`, or by `start_state` / `target_state` |
| `can_build_railway`, `has_railway_connection` | trigger, any scope | same path options as `build_railway` |
| `has_railway_level` | trigger, any scope | `level` and `state` |
| `num_of_supply_nodes` | trigger, country | counts the country's supply nodes |
| `supply_node_range`, `local_supplies`, `local_supplies_for_controller`, `local_supply_impact_factor`, `supply_factor` | modifiers | country or state |

`add_building_construction = { type = supply_node ... }` is used in 72 blocks across 21 vanilla files, so supply nodes can be added during play without `build_railway`. [vanilla-confirmed 1.19.4.1] `common/` and `events/`. Railways added during play go through `build_railway` (222 lines in 45 vanilla files); no vanilla file builds `rail_way` with `add_building_construction`, and the only vanilla uses of `type = rail_way` are `damage_building` calls in `common/decisions/SOV.txt` and `common/on_actions/08_bba_on_actions.txt`.
<!-- kit:end id="supply-replacement" -->
