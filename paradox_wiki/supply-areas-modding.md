# Supply areas modding

*Offline snapshot of the Hearts of Iron IV Wiki page "Supply areas modding", revision 67235, captured 2026-10-31. Wiki text by the wiki's contributors under CC BY-SA 3.0 (see LICENSE.txt); kit blocks are local additions under the same license.*

<!-- kit:begin id="review" at="top" build="1.19.3.0" checked="2026-10-31" revision="67235" sources="map/supplyareas/ map/supply_nodes.txt map/railways.txt map/default.map history/states/ common/buildings/00_buildings.txt common/defines/00_defines.lua common/terrain/00_terrain.txt localisation/english/supply_area_names_l_english.yml interface/nudge.gui documentation/effects_documentation.md documentation/triggers_documentation.md hoi4.exe" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Checked against: the `map/` folder listing, `map/supply_nodes.txt` and `map/railways.txt` (parsed in full), the state files, the supply defines and the exe's file path strings.
Kit blocks added: one correction (supply areas are vestigial in 1.19.3 and what replaced them) and a table of the new system with vanilla counts.
The "deprecated" marker holds: no vanilla script or exe path string refers to the area format. The game still ships one leftover file, described below.
Gaps left: whether the engine still parses `map/supplyareas/` could not be tested; the `[unverified]` tags say so.
<!-- kit:end id="review" -->

<!-- kit:begin id="supply-areas-vestigial" at="top" -->
**Kit correction** The format on this page is not used by 1.19.3, and a new map does not need it. [unverified] Inference from the evidence below; the game was not run.

- `map/supplyareas/` still exists in 1.19.3 but holds one file, `1-SupplyArea.txt`, with a single area: `id=1`, `name="SUPPLYAREA_1"`, `value=12`, `states = { 5 85 763 807 }`. [vanilla-confirmed 1.19.3] `map/supplyareas/1-SupplyArea.txt`
- `localisation/english/supply_area_names_l_english.yml` still defines `SUPPLYAREA_1` to `SUPPLYAREA_357`, all with the text "SupplyArea". [vanilla-confirmed 1.19.3] `localisation/english/supply_area_names_l_english.yml`
- `hoi4.exe` holds the file path strings `map/supply_nodes.txt` and `map/railways.txt` but no string `supplyareas` or `supply_area` as a path. [unverified] Exe string search only.
- `map/default.map` does not list the folder, and no vanilla script mentions `supply_area`. The only other trace is a "Supply Areas" checkbox in `interface/nudge.gui` (the nudger window). [vanilla-confirmed 1.19.3] `map/default.map`, `interface/nudge.gui`
<!-- kit:end id="supply-areas-vestigial" -->

## Table of contents

- [Tips](#Tips)
- [Kit: What replaced supply areas](#kit-supply-replacement)

---

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

## Tips <a id="Tips"></a>

- When placing supply areas, the states they are compose of should be contiguous. This means islands should have their own supply areas.
- The average supply value in vanilla is 10.

<!-- kit:begin id="supply-replacement" at="bottom" -->
## Kit: What replaced supply areas <a id="kit-supply-replacement"></a>

Supply since 1.11 comes from supply nodes joined by railways, plus a per-state number. All rows: [vanilla-confirmed 1.19.3] `map/supply_nodes.txt`, `map/railways.txt`, `history/states/`, `common/buildings/00_buildings.txt`, `common/terrain/00_terrain.txt`, `common/defines/00_defines.lua`.

| Part | Where | Vanilla 1.19.3 |
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

`add_building_construction = { type = supply_node ... }` is used in 72 blocks across 21 vanilla files, so supply nodes can be added during play without `build_railway`. [vanilla-confirmed 1.19.3] `common/` and `events/`. Railways added during play go through `build_railway` (231 lines in 45 vanilla files); no vanilla file builds `rail_way` with `add_building_construction`, and the only vanilla use of `type = rail_way` is `damage_building` in `common/decisions/SOV.txt`.
<!-- kit:end id="supply-replacement" -->

---

## Navigation

**[Modding](<modding.md>)**

- **Documentation**: [Effects](<effects.md>) • [Triggers](<triggers.md>) • [Defines](<defines.md>) • [Modifiers](<modifiers.md>) • [List of modifiers](<list-of-modifiers.md>) • [Scopes](<scopes.md>) • [Localisation](<localisation.md>) • [On actions](<on-actions.md>) • [Data structures](<data-structures.md>) • [Flags](<data-structures.md#Flags>) • [Event targets](<data-structures.md#Event_targets>) • [Country tag aliases](<data-structures.md#Country_tag_aliases>) • [Variables](<data-structures.md#Variables>) • [Arrays](<data-structures.md#Arrays>)
- **Scripting**: [Achievements](<achievement-modding.md>) • [AI](<ai-modding.md>) • [AI focuses](<ai-focuses.md>) • [Autonomous states](<autonomy-state-modding.md>) • [Balances of power](<balance-of-power-modding.md>) • [Bookmarks/Scenarios](<bookmark-modding.md>) • [Game rules](<bookmark-modding.md#Game_rules>) • [Buildings](<building-modding.md>) • [Characters and traits](<character-modding.md>) • [Cosmetic tags](<cosmetic-tag-modding.md>) • [Countries](<country-creation.md>) • [Divisions](<division-modding.md>) • [Decisions](<decision-modding.md>) • [Doctrines](<doctrine-modding.md>) • [Equipment](<equipment-modding.md>) • [Events](<event-modding.md>) • [Factions](<faction-modding.md>) • [Ideas](<idea-modding.md>) • [Ideologies](<ideology-modding.md>) • [Military industrial organizations](<military-industrial-organization-modding.md>) • [National focuses](<national-focus-modding.md>) • [Resources](<resources-modding.md>) • [Scripted GUI](<scripted-gui-modding.md>) • [Technologies and doctrines](<technology-modding.md>) • [Units](<unit-modding.md>)
- **Map**: [Map](<map-modding.md>) • [States](<state-modding.md>) • [Strategic regions](<strategic-region-modding.md>)
- **Graphical**: [Interface](<interface-modding.md>) • [Graphical assets](<graphical-asset-modding.md>) • [Entities](<entity-modding.md>) • [Posteffects](<posteffect-modding.md>) • [Particles](<particle-modding.md>) • [Fonts](<font-modding.md>)
- **Cosmetic**: [Portraits](<portrait-modding.md>) • [Namelists](<namelist-modding.md>) • [Music](<music-modding.md>) • [Sound](<sound-modding.md>)
- **Other**: [Console commands](<console-commands.md>) • [Troubleshooting](<troubleshooting.md>) • [Mod structure](<mod-structure.md>) • [Mods](<mods.md>) • [Nudger](<nudger.md>)
- **Kit pages (not on the wiki)**: [Collection modding](<collection-modding.md>) • [Game rule modding](<game-rule-modding.md>) • [Intelligence operation modding](<intelligence-operation-modding.md>) • [Map mode modding](<map-mode-modding.md>) • [Occupation and resistance modding](<occupation-and-resistance-modding.md>) • [Peace conference modding](<peace-conference-modding.md>) • [Raid modding](<raid-modding.md>) • [Script constant modding](<script-constant-modding.md>) • [Special project modding](<special-project-modding.md>)
