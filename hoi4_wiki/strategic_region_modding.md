# Strategic region modding

Strategic regions are defined in `/Hearts of Iron IV/map/strategicregions/*.txt`.

Each strategic region is typically stored in it's own file, although you can store multiple strategic region definitions within the same file, as the ID is defined within the strategic region definition, rather than the file title.

Here is a generic example of a strategic region:

```text
strategic_region = {
    id = <int>
    name = <localization key>

    provinces = {
        <province ids>
    }

    weather = {
        period = {
            between = { <min> <max> }
            temperature = { <min> <max> }
            no_phenomenon = <weight>
            rain_light = <weight>
            rain_heavy = <weight>
            snow = <weight>
            blizzard = <weight>
            mud = <weight>
            sandstorm = <weight>
            min_snow_level = <amount>
        }
    }
}
```

- **id** defines the numerical id used by the strategic region. The strategic region IDs must be added sequentially, skipping numbers will cause crashes.

- **name** defines the localization key the strategic region uses. You can use a non-localized string (i.e. "Paris"), but it is best practice to use localized strings.

- **provinces** scope defines which provinces the strategic region is composed over.

- **weather** scope determines the weather within the provinces covered by the strategic region.

## Weather

Each strategic region has a **weather** scope that determines how the weather changes for provinces within it.

Each weather system is defined within a **period** scope within the **weather** scope.

- **between** scope determines when the weather system occurs, the notation is `day.month day.month`, i.e. `0.0 30.0` means the weather system occurs between the 1st of January and the 31st, including these days. Note that the first day and the first month are marked as 0, not as 1.

- **temperature** scope determines the minimum and maximum temperature for the weather system.

- ~~**temperature_day_night** scope determines the minimum and maximum temperature variability during day and night for the weather system.~~ (This is no longer used since version 1.11, set all temperature ranges via temperature)

- **min_snow_level** scope determines the minimum amount of snow that is always present in the weather system. Typically only used for areas with year-round snow.

Each of the weather states are given a weight, determining how likely the state will occur within the weather system. The weather states can be found in `/Hearts of Iron IV/common/weather.txt`.

Keys of a `period` block in 1.19.3. All 304 vanilla regions have exactly 12 periods (3648 in total), one per month, written as `between = { 0.<month> <last day>.<month> }` with day and month counted from 0 (January is `0.0 30.0`, February `0.1 27.1`).

| Key | Vanilla use |
| --- | --- |
| `between`, `temperature`, `no_phenomenon`, `rain_light`, `rain_heavy`, `snow`, `blizzard`, `mud`, `sandstorm`, `min_snow_level` | in all 3648 periods |
| `arctic_water` | weight like the other weather types; in 3636 of 3648 periods, missing from the wiki example above |
| `temperature_day_night` | in no vanilla period (consistent with the struck-through line above) |

`common/weather.txt` is not a list of weather states. It holds `terrain_modifiers` (extra weight per terrain for `no_phenomenon`, `mud`, `rain_light`, `rain_heavy`, `snow`, `blizzard`, `sandstorm`, plus extra degrees for `temperature`) and a `settings` block with `temperature`, `mud`, `snowing`, `arctic_water`, `chance_increase`, `duration` and `performance` tuning.

## Tips

- When placing strategic regions, the provinces they are compose of should be contiguous. This means islands are normally part of a *sea* strategic region.

`hoi4.exe` contains the map error text "Strategic region ... is fractioned! The following provinces are separated from the rest". It is a check on naval regions, not on a land region made of disconnected provinces. A far-away land province (1217) added to region 1, Southern England, and removed from `193-Northern Australia.txt` did not log a "fractioned" line. It logged the state error "MAP_ERROR: State "Northern Territory"(#520) has provinces (#1217, #1410) belonging to different strategic areas: "Southern England" (#1), "Northern Australia" (#193)" at load. The "fractioned" text exists in this build with the wording "Naval strategic region <name> is fractioned! The following provinces are separated from the rest:" followed by province ids: 17 such entries (for example "Naval strategic region Northern England is fractioned!") appeared in a run that deleted province 3's row from `definition.csv`, a different construct. Whether a land-only disconnection is ever checked rests on the one land-province case, and no new game was started in that run.

Vanilla also satisfies the other rules around regions: each of the 13413 provinces in `map/definition.csv` (every id except 0) is listed in exactly one region, sea and lake provinces included, and none of the 1081 state files has provinces in two different regions.

The exe also has the error texts "The land province ... has no strategic region assigned" and a state definition "belonging to different strategic areas". Both are logged at load as MAP_ERROR lines: "MAP_ERROR: The province 221 - has no strategic region assigned." (province 221 removed from region 1) and "MAP_ERROR: State "Brandenburg"(#64) has provinces (#375, #478) belonging to different strategic areas: "Altai" (#261), "Eastern Germany" (#8)" (province 375 of state 64 moved from `8-Eastern Germany.txt` to `261-Altai.txt`). With the second error the main menu showed a dialog "Failed to load the map" that warns that launching a game will likely crash and offers the Nudger to fix the issues, but a new game still started. The dialog text in the screenshot was partly covered by a tooltip.

The page says that skipping strategic region ids causes crashes. It does: removing the file of region 100 so that the ids skip from 99 to 101 crashed 1.19.4.1 at load (EXCEPTION_ACCESS_VIOLATION), and so did a variant that moved all provinces of region 100 into a new region 305 (only the id gap differs). The mod's `.mod` file carried `replace_path="map/strategicregions"` in both runs. Before each crash error.log logged "map/weatherpositions.txt error at line 207: invalid region id." and the same for line 208, because the vanilla `map/weatherpositions.txt` still names region 100 in both variants. So the crash may come from that dangling reference and not from the id gap itself. A variant that also edits `weatherpositions.txt` was not run.

## Region files in 1.19.3

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

Both sit directly inside `strategic_region = { ... }`, next to `provinces` and `weather`. In vanilla they are separate: the 10 regions with `static_modifiers` (for example region 75) have no `naval_terrain`.

- `naval_terrain = <terrain>` names a terrain category from `common/terrain/00_terrain.txt` that has `naval_terrain = yes`. Vanilla values: `water_deep_ocean` (37 regions), `water_fjords` (14), `water_shallow_sea` (12). In `definition.csv` all 3133 sea provinces have the terrain `ocean`, so a deep, shallow or fjord terrain can only come from this key (the Map modding page says the same).
- `static_modifiers = { <static modifier> = always }` applies a static modifier from `common/modifiers/` to the region. Vanilla uses it only for `water_modifier_shark_infested` (`navy_casualty_on_sink = 0.6`) in 10 Pacific regions.

Script that takes a region id or scope (docs name the files):

| Name | Scope | Meaning |
| --- | --- | --- |
| `has_naval_control = <id>` | country | friendly navies control the region |
| `has_enemy_naval_control = <id>` | country | an enemy has naval control of the region |
| `region` | state | trigger that checks the state's strategic region id |
| `any_state_in = { strategic_region = <id> ... }` | any | iterate states of a region |
| `add_mines = { region = <id> amount = <n> }` | country | add mines to a region |
| `add_region_efficiency` | `STRATEGIC_REGION` | the only effect with that scope; no vanilla file uses it |
