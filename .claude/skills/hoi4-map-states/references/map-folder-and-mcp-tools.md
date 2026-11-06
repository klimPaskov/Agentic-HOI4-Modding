# HOI4 Map and States: Map folder and MCP map tools

Part of the [hoi4-map-states](../SKILL.md) skill. Read before changing map geometry or calling the hoi4_map_inspect and hoi4_map_rewrite tools, and read it together with `references/map-geometry.md` before touching any file under `map/`.

## Map folder summary

Geometry files live under `map/` (`GAME/map/` in vanilla). Full file-by-file formats, province and strategic-region rules, adjacency rows, and supply and railway files are in `references/map-geometry.md`; read it before touching any file in this table.

| File | Purpose |
| --- | --- |
| `provinces.bmp` + `definition.csv` | Province borders (24-bit RGB) and per-province id, colour, type, coastal flag, terrain, continent; ids contiguous from 0 |
| `strategicregions/*.txt` | Region membership (every province in exactly one region, all provinces of a state in the same region) and weather; ids sequential |
| `buildings.txt` | Building model positions per state; naval bases and floating harbours need an adjacent sea province |
| `adjacencies.csv`, `adjacency_rules.txt` | Straits, canals, impassable borders |
| `supply_nodes.txt`, `railways.txt` | Starting supply hubs and rails; must reference state-owned land provinces |
| `unitstacks.txt`, `weatherpositions.txt` | Unit, victory-point, and weather object positions |
| `default.map`, `continent.txt` | File redirects and continent list |

`airports.txt` and `rocketsites.txt` are not in the installed `GAME/map/` (the Map modding wiki says they were removed in patch 1.15, while State modding still describes them); trust the installed folder.
Use the MCP map tools for geometry changes instead of hand-editing bitmaps and CSVs.

## MCP map tools

The Agent Nudger exposes three tools; inspect and render never write source, rewrite writes the configured mod.

- `hoi4_map_inspect`: full validation plus overview by default; set `lookupOnly = true` for bounded lookups. Inputs: `stateIds`, `regionIds`, `provinceIds` (max 32), `coordinates` (`pixel` x/y or `map` x/z), `query`, and `allocationRequests` (ask for the next free state id or an unused province colour). A lookup call returned the workspace totals (13,414 province definitions, 1,081 states, 304 regions, 5,632 x 2,048 pixels, 534 ports) and linked a JSON artifact.
- `hoi4_map_inspect` with render arguments (`layer`, `overlays`, `scale`, `tile`, or `area`): layers `province`, `state`, `strategic-region`, `terrain`, `continent`, `owner`, `controller`, `cores`, `claims`, `coast`; overlays `coastlines`, `ports`, `victory-points`, `resources`, `state-buildings`, `province-buildings`, `supply-nodes`, `railways`, `adjacencies`, `building-positions`, `unit-positions`, `weather-positions`; restrict with `area` (state, region, province ids) or a pixel `tile`.
- `hoi4_map_rewrite`: applies map creation, edits, and id swaps with visual and semantic evidence. Use `requestKey` for stable background retries and check source state before retrying an uncertain write. The operation schema is opaque in the tool listing (`operations` is an array of "complete map operation" objects); one probe with a made-up operation was rejected as invalid arguments, so read the live schema before composing operations.
- Use inspect first to learn current ids and to allocate new ids, render to check geometry, rewrite only for declarative geometry or id changes. For a script-only task (owner changes, buildings, flags) read the state file and use `hoi4_source_lookup`; the map tools are unnecessary.
- If a map route fails once, retry once with narrower input, then read the files directly.

