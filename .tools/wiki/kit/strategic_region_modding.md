# Strategic region modding

<!-- kit:begin id="review" build="1.19.4.1" checked="2026-11-01" revision="54730" sources="map/strategicregions/ map/definition.csv map/weatherpositions.txt common/weather.txt common/terrain/ common/modifiers/00_static_modifiers.txt history/states/ localisation/english/strategic_region_names_l_english.yml documentation/effects_documentation.md documentation/triggers_documentation.md hoi4.exe" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Checked against: all 304 vanilla files in `map/strategicregions/` (parsed, not sampled), `common/weather.txt`, the terrain categories and the state files.
Kit blocks added: the keys vanilla uses that the wiki omits (`naval_terrain`, `static_modifiers`, `arctic_water`), vanilla counts, script that takes a region id, and the map errors the exe prints.
Gaps left: map errors that exist only as strings in `hoi4.exe` are tagged `[unverified]`. The page's statement that skipped ids crash the game was not tested.
The "no longer used" marker is the struck-through `temperature_day_night` line; vanilla agrees (no region file uses it).
**1.19.4.1 re-check (2026-11-01).** 4 kit statements depended on files the update changed (the state history files, the strings of `hoi4.exe` and the script folders scanned for `add_region_efficiency`) and all were re-measured. Nothing changed: none of the 1081 state files has provinces in two regions, the three exe error texts are still there and no vanilla file uses `add_region_efficiency`. Every other statement cites files that are byte-identical in 1.19.4.1 (Steam depot manifest diff).
<!-- kit:end id="review" -->

<!-- kit:begin id="region-weather-keys" at="section:weather" -->
Keys of a `period` block in 1.19.3. All 304 vanilla regions have exactly 12 periods (3648 in total), one per month, written as `between = { 0.<month> <last day>.<month> }` with day and month counted from 0 (January is `0.0 30.0`, February `0.1 27.1`). [vanilla-confirmed 1.19.3] `map/strategicregions/*.txt`

| Key | Vanilla use |
| --- | --- |
| `between`, `temperature`, `no_phenomenon`, `rain_light`, `rain_heavy`, `snow`, `blizzard`, `mud`, `sandstorm`, `min_snow_level` | in all 3648 periods |
| `arctic_water` | weight like the other weather types; in 3636 of 3648 periods, missing from the wiki example above |
| `temperature_day_night` | in no vanilla period (consistent with the struck-through line above) |

`common/weather.txt` is not a list of weather states. It holds `terrain_modifiers` (extra weight per terrain for `no_phenomenon`, `mud`, `rain_light`, `rain_heavy`, `snow`, `blizzard`, `sandstorm`, plus extra degrees for `temperature`) and a `settings` block with `temperature`, `mud`, `snowing`, `arctic_water`, `chance_increase`, `duration` and `performance` tuning. [vanilla-confirmed 1.19.3] `common/weather.txt`
<!-- kit:end id="region-weather-keys" -->

<!-- kit:begin id="region-tips-checks" at="section:tips" -->
`hoi4.exe` contains the map error text "Strategic region ... is fractioned! The following provinces are separated from the rest". It is a check on naval regions, not on a land region made of disconnected provinces. A far-away land province (1217) added to region 1, Southern England, and removed from `193-Northern Australia.txt` did not log a "fractioned" line. It logged the state error "MAP_ERROR: State "Northern Territory"(#520) has provinces (#1217, #1410) belonging to different strategic areas: "Southern England" (#1), "Northern Australia" (#193)" at load. The "fractioned" text exists in this build with the wording "Naval strategic region <name> is fractioned! The following provinces are separated from the rest:" followed by province ids: 17 such entries (for example "Naval strategic region Northern England is fractioned!") appeared in a run that deleted province 3's row from `definition.csv`, a different construct. Whether a land-only disconnection is ever checked rests on the one land-province case, and no new game was started in that run. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, one-mod launches, error.log read.

Vanilla also satisfies the other rules around regions: each of the 13413 provinces in `map/definition.csv` (every id except 0) is listed in exactly one region, sea and lake provinces included, and none of the 1081 state files has provinces in two different regions. [vanilla-confirmed 1.19.4.1] `map/strategicregions/`, `map/definition.csv`, `history/states/`

The exe also has the error texts "The land province ... has no strategic region assigned" and a state definition "belonging to different strategic areas". Both are logged at load as MAP_ERROR lines: "MAP_ERROR: The province 221 -  has no strategic region assigned." (province 221 removed from region 1) and "MAP_ERROR: State "Brandenburg"(#64) has provinces (#375, #478) belonging to different strategic areas: "Altai" (#261), "Eastern Germany" (#8)" (province 375 of state 64 moved from `8-Eastern Germany.txt` to `261-Altai.txt`). With the second error the main menu showed a dialog "Failed to load the map" that warns that launching a game will likely crash and offers the Nudger to fix the issues, but a new game still started. The dialog text in the screenshot was partly covered by a tooltip. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, one-mod launches, error.log read and a screenshot.

The page says that skipping strategic region ids causes crashes. It does: removing the file of region 100 so that the ids skip from 99 to 101 crashed 1.19.4.1 at load (EXCEPTION_ACCESS_VIOLATION), and so did a variant that moved all provinces of region 100 into a new region 305 (only the id gap differs). The mod's `.mod` file carried `replace_path="map/strategicregions"` in both runs. Before each crash error.log logged "map/weatherpositions.txt error at line 207: invalid region id." and the same for line 208, because the vanilla `map/weatherpositions.txt` still names region 100 in both variants. So the crash may come from that dangling reference and not from the id gap itself. A variant that also edits `weatherpositions.txt` was not run. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, one-mod launches, error.log and the crash folders read.
<!-- kit:end id="region-tips-checks" -->

<!-- kit:begin id="region-vanilla-format" at="bottom" -->
## Region files in 1.19.3

All rows: [vanilla-confirmed 1.19.3] `map/strategicregions/` (304 files), `localisation/english/strategic_region_names_l_english.yml`.

| Fact | Detail |
| --- | --- |
| Files | 304, named `<id>-<name>.txt`, one `strategic_region = { ... }` block each; the file name prefix equals the `id` in all 304 |
| Ids | 1 to 304 with no gaps |
| Name keys | `name = "STRATEGICREGION_<id>"`; the localisation file defines `STRATEGICREGION_1` to `STRATEGICREGION_304` |
| Top-level keys | `id`, `name`, `provinces`, `weather` in all 304; `naval_terrain` in 63; `static_modifiers` in 10 |

Two keys the wiki page does not describe:

```text
naval_terrain = water_deep_ocean

static_modifiers = {
	water_modifier_shark_infested = always
}
```

Both sit directly inside `strategic_region = { ... }`, next to `provinces` and `weather`. In vanilla they are separate: the 10 regions with `static_modifiers` (for example region 75) have no `naval_terrain`. [vanilla-confirmed 1.19.3] `map/strategicregions/`

- `naval_terrain = <terrain>` names a terrain category from `common/terrain/00_terrain.txt` that has `naval_terrain = yes`. Vanilla values: `water_deep_ocean` (37 regions), `water_fjords` (14), `water_shallow_sea` (12). In `definition.csv` all 3133 sea provinces have the terrain `ocean`, so a deep, shallow or fjord terrain can only come from this key (the Map modding page says the same). [vanilla-confirmed 1.19.3] `map/strategicregions/`, `map/definition.csv`
- `static_modifiers = { <static modifier> = always }` applies a static modifier from `common/modifiers/` to the region. Vanilla uses it only for `water_modifier_shark_infested` (`navy_casualty_on_sink = 0.6`) in 10 Pacific regions. [vanilla-confirmed 1.19.3] `map/strategicregions/`, `common/modifiers/00_static_modifiers.txt`

Script that takes a region id or scope (docs name the files): [docs] `documentation/effects_documentation.md`, `documentation/triggers_documentation.md`.

| Name | Scope | Meaning |
| --- | --- | --- |
| `has_naval_control = <id>` | country | friendly navies control the region |
| `has_enemy_naval_control = <id>` | country | an enemy has naval control of the region |
| `region` | state | trigger that checks the state's strategic region id |
| `any_state_in = { strategic_region = <id> ... }` | any | iterate states of a region |
| `add_mines = { region = <id> amount = <n> }` | country | add mines to a region |
| `add_region_efficiency` | `STRATEGIC_REGION` | the only effect with that scope; no vanilla file uses it |
<!-- kit:end id="region-vanilla-format" -->
