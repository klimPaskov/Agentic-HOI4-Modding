# HOI4 Map and States: Source map

Part of the [hoi4-map-states](../SKILL.md) skill. Read to find the authoritative documentation, wiki page and vanilla precedent for a map or state topic before you cite or mirror it.

## Contents

- Source map: where the authoritative text lives
- Decision procedure: which mechanism for which goal
- Map folder summary (full formats in references/map-geometry.md)
- State history files: skeleton and keys
- State categories and building slots
- Buildings (common/buildings) and building models
- Runtime state effects
- Runtime state triggers
- Iterating states and the loop cap
- Flags, variables, and modifiers on states
- Victory points, resources, supply, railways at runtime
- Map modes and map GFX
- MCP map tools
- Validation procedure
- Repository conventions
- Common mistakes and silent failures
- Unverified or conflicting points

## Source map

`GAME` means the installed Hearts of Iron IV folder named in `CLAUDE.md`.
`WIKI` means the offline snapshot in `hoi4_wiki/` at the mod root.
Installed documentation is more authoritative than the wiki; where they disagree, follow the installed file and record the conflict.

| Topic | Authoritative text | Vanilla precedent |
| --- | --- | --- |
| Map folder overview, BMP rules, provinces, terrain, adjacencies, supply files | `WIKI/map_modding.md` | `GAME/map/` |
| State file keys, history block, state categories, building list | `WIKI/state_modding.md` | `GAME/history/states/1-France.txt` (minimal), `116-Malta.txt` (strategic_province_location), `1022 - Interior Borneo.txt` (impassable enclave), `1032 - Yanan.txt` (IF with has_dlc inside history) |
| Strategic region file, weather periods | `WIKI/strategic_region_modding.md` | `GAME/map/strategicregions/1-Southern England.txt`, `100-Red Sea.txt` |
| Building definition fields, slots, spawn points | `WIKI/building_modding.md` | `GAME/common/buildings/00_buildings.txt`, `01_landmark_buildings.txt` |
| Strategic locations (extra provincial building cap) | `GAME/common/strategic_locations/documentation.md` | `GAME/common/strategic_locations/strategic_locations.txt` |
| Scripted map modes | `GAME/common/map_modes/documentation.md` | none in vanilla (documentation only) |
| Resources | `GAME/common/resources/_documentation.md`, `WIKI/resources_modding.md` | `GAME/common/resources/00_resources.txt` |
| State effects | `GAME/documentation/effects_documentation.md`, section "Effects for scope STATE", plus the individual entries named below | `GAME/common/national_focus/*.txt`, `GAME/events/*.txt` |
| State triggers | `GAME/documentation/triggers_documentation.md`, section "Triggers for scope STATE" | same |
| Effect argument tables (more detail than the installed file for building and flag effects) | `WIKI/effects.md` (rows `add_building_construction`, `set_building_level`, `set_state_flag`, `build_railway`, `add_resource`, `transfer_state_to`) | |
| Collections, `game:all_states` | `GAME/documentation/script_concept_documentation.md` (Collections), `script_collection_input.md`, `script_collection_operator.md` | |
| Loop cap | `GAME/common/defines/00_defines.lua` (`MAX_EFFECT_ITERATION = 1000`) | |
| State modifiers | `GAME/documentation/modifiers_documentation.md`, section "Modifiers for scope state" | `GAME/common/state_category/*.txt` |

Use the hoi4 MCP reference routes (`hoi4_reference_context` with surface `map`, `hoi4_reference_search`, `hoi4_reference_read`, `hoi4_source_lookup`) to cite exact line spans; `hoi4_source_lookup` finds exact vanilla and mod definitions, overrides, and indexed usages.
If a route fails once, retry once with narrower input, then read the local file directly.

