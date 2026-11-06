# Supply areas modding

The format on this page is not used by 1.19.3, and a new map does not need it. The evidence below points that way, and in 1.19.4.1 the game does not parse the folder: a valid `map/supplyareas/2-SupplyArea.txt` (`id=2`, `name="SUPPLYAREA_2"`, `value=999`, `states={ 5 }`) and a garbage file (`this is garbage { text ] = =`) both logged no new line in error.log and no mention of the file in any log, and the game did not crash and started a new game. This rests on the absence of a parse error. The supply map mode and the supply of state 5 were not read, and a map built without the folder was not tried.

- `map/supplyareas/` still exists in 1.19.3 but holds one file, `1-SupplyArea.txt`, with a single area: `id=1`, `name="SUPPLYAREA_1"`, `value=12`, `states = { 5 85 763 807 }`.
- `localisation/english/supply_area_names_l_english.yml` still defines `SUPPLYAREA_1` to `SUPPLYAREA_357`, all with the text "SupplyArea".
- `hoi4.exe` holds the file path strings `map/supply_nodes.txt` and `map/railways.txt` but no string `supplyareas` or `supply_area` as a path. (unverified) Exe string search only.
- `map/default.map` does not list the folder, and no vanilla script mentions `supply_area`. The only other trace is a "Supply Areas" checkbox in `interface/nudge.gui` (the nudger window).

**NOTE: Supply areas are deprecated as of patch 1.11 Barbarossa/No Step Back. The following only applies to version 1.10 and before.**

Supply areas are defined in `/Hearts of Iron IV/map/supplyareas/*.txt`.

Each supply area is typically stored in it's own file, although you can store multiple supply area definitions within the same file, as the ID is defined within the supply area definition, rather than the file title.

Here is a generic example of a supply area:

```text
supply_area = {
    id = <int>
    name = <localization key>
    value = <amount>
    states = {
        <state id>
    }
}
```

- **id** defines the numerical id used by the supply area. The supply area IDs must be added sequentially, skipping numbers will cause crashes.

- **name** defines the localization key the supply area uses. You can use a non-localized string (i.e. "Paris"), but it is best practice to use localized strings.

- **value** defines the amount of base supply the supply area grants. In vanilla, the supply varies from 0 to 16.

- **states** scope defines which states the supply area covers. Note that supply areas should normally cover more than one state.

## Tips

- When placing supply areas, the states they are compose of should be contiguous. This means islands should have their own supply areas.
- The average supply value in vanilla is 10.

## What replaced supply areas

Supply since 1.11 comes from supply nodes joined by railways, plus a per-state number.

| Part | Where | Vanilla 1.19.4.1 |
| --- | --- | --- |
| Starting supply nodes | `map/supply_nodes.txt`, one row `<level> <province>` per line | 727 rows, all level 1, 727 different provinces |
| Starting railways | `map/railways.txt`, one row `<level> <count> <province> <province> ...` | 909 rows; levels used are 1 (467 rows), 2 (406), 3 (29) and 4 (7); `<count>` is the number of provinces listed in all 909 rows; 2 to 19 provinces per row |
| Node and railway as buildings | `common/buildings/00_buildings.txt`: `supply_node` and `rail_way`, both `province_max = 1` | `supply_node` costs 20000 and `rail_way` 170 plus 130 per level; the railway level cap comes from the define `NSupply.MAX_RAILWAY_LEVEL = 5` (`common/defines/00_defines.lua`) |
| Base supply of a state | `local_supplies = <number>` in the state file | present in 1069 of 1081 states; values 0.0 to 16.0; 846 of them are 0.0 |
| Terrain effect | `supply_flow_penalty_factor` in `common/terrain/00_terrain.txt` | for example 0.08 forest, 0.12 mountain, 0.14 desert, 0.16 jungle and marsh, -0.2 urban |
| Tuning | `NSupply` defines | `CAPITAL_*`, `NODE_*`, `NAVAL_BASE_*`, `FLOATING_HARBOR_*` and `RAILWAY_*` families, `INFRA_TO_SUPPLY = 0.3`, `RIVER_RAILWAY_LEVEL = 1` |

Script that works on this system.

| Name | Kind and scope | Use |
| --- | --- | --- |
| `build_railway` | effect, any scope | `level`, and a path by `path = { ... }`, by `start_province` / `target_province`, or by `start_state` / `target_state` |
| `can_build_railway`, `has_railway_connection` | trigger, any scope | same path options as `build_railway` |
| `has_railway_level` | trigger, any scope | `level` and `state` |
| `num_of_supply_nodes` | trigger, country | counts the country's supply nodes |
| `supply_node_range`, `local_supplies`, `local_supplies_for_controller`, `local_supply_impact_factor`, `supply_factor` | modifiers | country or state |

`add_building_construction = { type = supply_node ... }` is used in 72 blocks across 21 vanilla files, so supply nodes can be added during play without `build_railway`. Railways added during play go through `build_railway` (222 lines in 45 vanilla files); no vanilla file builds `rail_way` with `add_building_construction`, and the only vanilla uses of `type = rail_way` are `damage_building` calls in `common/decisions/SOV.txt` and `common/on_actions/08_bba_on_actions.txt`.
