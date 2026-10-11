# Map Geometry Reference

Reference for `hoi4-map-states`.
Read it when you edit or audit the files under `map/`: provinces, definitions, strategic regions, adjacencies, supply nodes, railways, and bitmaps.
Paths, `GAME`, and `WIKI` mean the same as in the main skill.

## The map folder, file by file

All paths are under `GAME/map/` for vanilla and the mod's `map/` folder for overrides.
`GAME/map/default.map` names the main files and can redirect them (`provinces`, `definitions`, `terrain`, `rivers`, `heightmap`, `tree_definition`, `continent`, `adjacency_rules`, `adjacencies`, `ambient_object`, `seasons`, `positions`) and lists the tree palette indices that count as trees for automatic terrain assignment.

| File | Purpose | Format and notes |
| --- | --- | --- |
| `provinces.bmp` | Province borders; each province is one flat colour | 24-bit RGB, no compression, no colour-space header; width and height multiples of 256; the wiki gives a total-pixel ceiling of about 13,238,272; vanilla is 5632 x 2048 (reported by `hoi4_map_inspect`) |
| `definition.csv` | Province id, colour, type, coastal flag, terrain, continent | `id;r;g;b;land\|sea\|lake;coastal;terrain;continent`; ids contiguous from 0; CRLF line endings |
| `terrain.bmp`, `heightmap.bmp`, `world_normal.bmp`, `rivers.bmp`, `trees.bmp`, `cities.bmp` | Cosmetic layers | 8-bit indexed (terrain, rivers, trees, cities) or 8-bit greyscale (heightmap); the game reads palette indices, never colours |
| `continent.txt` | Continent names, ids by order | `continents = { europe north_america ... }`; every land province needs a nonzero continent |
| `buildings.txt` | Model positions for buildings | `state_id;building;x;y;z;rotation;adjacent_sea_province`; one row per model; naval bases and floating harbours need the sea province |
| `unitstacks.txt` | Unit and victory-point model positions per province | `province;type;x;y;z;rotation;offset`; type 38 is the victory-point marker |
| `supply_nodes.txt` | Starting supply hubs | `level province` per line (level 1 only) |
| `railways.txt` | Starting railways | `level count province_1 ... province_n` per line |
| `adjacencies.csv` | Strait, canal, and impassable links | `From;To;Type;Through;start_x;start_y;stop_x;stop_y;adjacency_rule_name;Comment` |
| `adjacency_rules.txt` | Who may pass an adjacency | `adjacency_rule = { name required_provinces is_disabled icon offset contested enemy friend neutral }`; file must be UTF-8 without BOM |
| `strategicregions/*.txt` | Region membership and weather | one or more `strategic_region = { id name provinces weather }` per file |
| `weatherpositions.txt` | Where weather objects appear | `region;x;y;z;small\|large`; at least one small and one large object overall |
| `ambient_object.txt`, `cities.txt`, `seasons.txt`, `positions.txt`, `colors.txt` | Cosmetic objects, city models, season colours | rarely touched in script-level work |
| `terrain/` | Atlases, border textures, colour maps | DDS with mipmaps; terrain atlas needs DXT5 |
| `supplyareas/` | Pre-1.11 supply areas | Present in the install; the wiki says supply areas were replaced by `supply_nodes.txt` and `railways.txt`; do not extend it |

`airports.txt` and `rocketsites.txt` are not in the installed `GAME/map/`; the Map modding wiki says they were removed in patch 1.15 although the State modding wiki still describes them. Trust the installed folder. Rocket sites and similar buildings are positioned through `buildings.txt` rows and building `spawn_point` definitions.

BMP handling rules (full text in Map modding, sections BMP format and Correcting a broken 8-bit map):

- Paint.NET and MS Paint cannot edit the indexed or greyscale bitmaps; they rebuild the palette. `provinces.bmp` and `world_normal.bmp` are 24-bit and tolerate more editors.
- In GIMP, tick "do not write color space information" on export; the engine rejects the BITMAPV5HEADER. A 32-bit `provinces.bmp` produces a bitdepth error on load.
- Never change an indexed bitmap's mode in the editor; copy the pixels into a copy of the vanilla file instead.
- Debug mode is essentially required for map work; without it any MAP_ERROR prevents loading.

## Provinces: provinces.bmp and definition.csv

Definition rows look like:

```
7;212;179;179;sea;true;ocean;0
114;40;15;15;land;false;plains;1
260;170;235;235;land;true;urban;1
```

Rules and consequences (Map modding, section Provinces):

- Province ids must be contiguous from 0. A gap shifts the properties of every later province onto the wrong colour because the game reads rows by position. Fill a deleted id with the highest id rather than leaving a gap.
- Every row's colour must exist in `provinces.bmp`, and every colour in the bitmap needs a row. The game writes a corrected copy (`definition.csv.fixed`) in the user directory; delete stale copies after editing.
- Sea provinces use terrain `ocean` and continent 0; lakes use terrain `lakes`; every land province needs a continent greater than 0. The coastal flag in the CSV is overridden by what the bitmap says.
- Province errors you will meet: X crossing (four provinces meeting at a corner), TOO LARGE BOX (width or height over one eighth of the map, or two provinces sharing a colour), fewer than 8 pixels, "Prov N has no continent" (also caused by LF instead of CRLF endings), "has no pixels in provinces.bmp".
- Keep the province count low; the wiki cites an integer overflow in border drawing at roughly 65,536 borders (around 21,000 provinces). Vanilla has 13,414 definitions (reported by `hoi4_map_inspect`).
- Provincial terrain (combat and movement) comes from `definition.csv` for land and from the strategic region for sea (`naval_terrain = <terrain>`); graphical terrain in `terrain.bmp` is cosmetic. Terrain categories live in `GAME/common/terrain/00_terrain.txt` (`categories = { ... }`, with `is_water`, `naval_terrain`, `movement_cost`, `combat_width`, `buildings_max_level`) and graphical terrain in its `terrain = { ... }` block.

## Strategic regions and weather

Skeleton verified against `GAME/map/strategicregions/100-Red Sea.txt`:

```
strategic_region = {
	id = 100
	name = "STRATEGICREGION_100"
	provinces = {
		2753 2776 2800
	}
	weather = {
		period = {
			between = { 0.0 30.0 }
			temperature = { 5.0 30.0 }
			no_phenomenon = 0.500
			rain_light = 1.000
			rain_heavy = 0.150
			snow = 0.200
			blizzard = 0.000
			arctic_water = 0.000
			mud = 0.300
			sandstorm = 0.000
			min_snow_level = 0.000
		}
	}
}
```

- Ids must be sequential; skipping a number crashes. Vanilla has 304 regions (`hoi4_map_inspect` reports 304).
- Every province needs exactly one region, and every province of a state must sit in the same region. A state whose provinces straddle two regions is a map error that stops loading without debug mode.
- `between = { day.month day.month }` counts from 0 (`0.0 30.0` is 1 to 31 January). The weights are chances per province; `no_phenomenon` gates the rest.
- Weather states are defined in `GAME/common/weather.txt`. `temperature_day_night` is no longer used.
- The only strategic-region script effect is `add_region_efficiency` (scope STRATEGIC_REGION). The state-scope triggers `region` and `area` compare a strategic region id (the installed text for both is "check state's strategic area id", so the difference between them is unverified).
- Regions should be contiguous; islands normally belong to a sea region.

## Adjacencies, supply nodes, railways

Adjacency rows (verified against `GAME/map/adjacencies.csv`):

```
6891;3838;sea;5579;-1;-1;-1;-1;;Sardinia-Corsica
10910;12807;impassable;-1;-1;-1;-1;-1;;Himalayas
8857;2284;sea;7617;1560;1009;1556;1016;PANAMA_CANAL;Panama
```

- `sea` links two provinces of the same type that need not touch; a `Through` province is mandatory when they do not touch, and enemy control of it blocks the link. `impassable` blocks a real border and takes -1 for through, positions, and an empty rule field.
- The file ends with a terminator row. The wiki gives `-1;-1;-1;-1;-1;-1;-1;-1;-1`; the installed file ends with `-1;-1;;-1;-1;-1;-1;-1;-1`. Keep whatever row the file already ends with, and keep entries above it.
- An adjacency rule name used in the CSV must exist in `adjacency_rules.txt`.
- `supply_nodes.txt` and `railways.txt` must reference real, state-owned land provinces. An invalid or stateless province in either file can crash on opening singleplayer or the Nudger supply view. Vanilla railway lines start with the level and the province count, for example `3 4 6521 11444 3312 6282`.
- Maximum starting supply-hub level is 1 and maximum railway level is 5 (`NDefines.NSupply.MAX_RAILWAY_LEVEL`, per the State modding references).

