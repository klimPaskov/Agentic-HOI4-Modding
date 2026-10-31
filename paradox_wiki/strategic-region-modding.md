# Strategic region modding

*Offline snapshot of the Hearts of Iron IV Wiki page "Strategic region modding", revision 54730, captured 2026-10-31. Wiki text by the wiki's contributors under CC BY-SA 3.0 (see LICENSE.txt); kit blocks are local additions under the same license.*

<!-- kit:begin id="review" at="top" build="1.19.3.0" checked="2026-10-31" revision="54730" sources="map/strategicregions/ map/definition.csv map/weatherpositions.txt common/weather.txt common/terrain/ common/modifiers/00_static_modifiers.txt history/states/ localisation/english/strategic_region_names_l_english.yml documentation/effects_documentation.md documentation/triggers_documentation.md hoi4.exe" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Checked against: all 304 vanilla files in `map/strategicregions/` (parsed, not sampled), `common/weather.txt`, the terrain categories and the state files.
Kit blocks added: the keys vanilla uses that the wiki omits (`naval_terrain`, `static_modifiers`, `arctic_water`), vanilla counts, script that takes a region id, and the map errors the exe prints.
Gaps left: map errors that exist only as strings in `hoi4.exe` are tagged `[unverified]`. The page's statement that skipped ids crash the game was not tested.
The "no longer used" marker is the struck-through `temperature_day_night` line; vanilla agrees (no region file uses it).
<!-- kit:end id="review" -->

## Table of contents

- [Weather](#Weather)
- [Tips](#Tips)
- [Kit: Region files in 1.19.3](#kit-region-vanilla-format)

---

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

## Weather <a id="Weather"></a>

Each strategic region has a **weather** scope that determines how the weather changes for provinces within it.

Each weather system is defined within a **period** scope within the **weather** scope.

- **between** scope determines when the weather system occurs, the notation is `day.month day.month`, i.e. `0.0 30.0` means the weather system occurs between the 1st of January and the 31st, including these days. Note that the first day and the first month are marked as 0, not as 1.

- **temperature** scope determines the minimum and maximum temperature for the weather system.

- ~~**temperature_day_night** scope determines the minimum and maximum temperature variability during day and night for the weather system.~~ (This is no longer used since version 1.11, set all temperature ranges via temperature)

- **min_snow_level** scope determines the minimum amount of snow that is always present in the weather system. Typically only used for areas with year-round snow.

Each of the weather states are given a weight, determining how likely the state will occur within the weather system. The weather states can be found in `/Hearts of Iron IV/common/weather.txt`.

<!-- kit:begin id="region-weather-keys" at="section:Weather" -->
**Kit addition** Keys of a `period` block in 1.19.3. All 304 vanilla regions have exactly 12 periods (3648 in total), one per month, written as `between = { 0.<month> <last day>.<month> }` with day and month counted from 0 (January is `0.0 30.0`, February `0.1 27.1`). [vanilla-confirmed 1.19.3] `map/strategicregions/*.txt`

| Key | Vanilla use |
| --- | --- |
| `between`, `temperature`, `no_phenomenon`, `rain_light`, `rain_heavy`, `snow`, `blizzard`, `mud`, `sandstorm`, `min_snow_level` | in all 3648 periods |
| `arctic_water` | weight like the other weather types; in 3636 of 3648 periods, missing from the wiki example above |
| `temperature_day_night` | in no vanilla period (consistent with the struck-through line above) |

`common/weather.txt` is not a list of weather states. It holds `terrain_modifiers` (extra weight per terrain for `no_phenomenon`, `mud`, `rain_light`, `rain_heavy`, `snow`, `blizzard`, `sandstorm`, plus extra degrees for `temperature`) and a `settings` block with `temperature`, `mud`, `snowing`, `arctic_water`, `chance_increase`, `duration` and `performance` tuning. [vanilla-confirmed 1.19.3] `common/weather.txt`
<!-- kit:end id="region-weather-keys" -->

## Tips <a id="Tips"></a>

- When placing strategic regions, the provinces they are compose of should be contiguous. This means islands are normally part of a *sea* strategic region.

<!-- kit:begin id="region-tips-checks" at="section:Tips" -->
**Kit note** `hoi4.exe` contains the map error text "Strategic region ... is fractioned! The following provinces are separated from the rest", which suggests that a region made of disconnected provinces is reported as a MAP_ERROR. [unverified] Exe string only (`hoi4.exe`), not run.

Vanilla also satisfies the other rules around regions: each of the 13413 provinces in `map/definition.csv` (every id except 0) is listed in exactly one region, sea and lake provinces included, and none of the 1081 state files has provinces in two different regions. [vanilla-confirmed 1.19.3] `map/strategicregions/`, `map/definition.csv`, `history/states/`

The exe also has the error texts "The land province ... has no strategic region assigned" and a state definition "belonging to different strategic areas". [unverified] Exe strings only.
<!-- kit:end id="region-tips-checks" -->

<!-- kit:begin id="region-vanilla-format" at="bottom" -->
## Kit: Region files in 1.19.3 <a id="kit-region-vanilla-format"></a>

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

---

## Navigation

**[Modding](<modding.md>)**

- **Documentation**: [Effects](<effects.md>) • [Triggers](<triggers.md>) • [Defines](<defines.md>) • [Modifiers](<modifiers.md>) • [List of modifiers](<list-of-modifiers.md>) • [Scopes](<scopes.md>) • [Localisation](<localisation.md>) • [On actions](<on-actions.md>) • [Data structures](<data-structures.md>) • [Flags](<data-structures.md#Flags>) • [Event targets](<data-structures.md#Event_targets>) • [Country tag aliases](<data-structures.md#Country_tag_aliases>) • [Variables](<data-structures.md#Variables>) • [Arrays](<data-structures.md#Arrays>)
- **Scripting**: [Achievements](<achievement-modding.md>) • [AI](<ai-modding.md>) • [AI focuses](<ai-focuses.md>) • [Autonomous states](<autonomy-state-modding.md>) • [Balances of power](<balance-of-power-modding.md>) • [Bookmarks/Scenarios](<bookmark-modding.md>) • [Game rules](<bookmark-modding.md#Game_rules>) • [Buildings](<building-modding.md>) • [Characters and traits](<character-modding.md>) • [Cosmetic tags](<cosmetic-tag-modding.md>) • [Countries](<country-creation.md>) • [Divisions](<division-modding.md>) • [Decisions](<decision-modding.md>) • [Doctrines](<doctrine-modding.md>) • [Equipment](<equipment-modding.md>) • [Events](<event-modding.md>) • [Factions](<faction-modding.md>) • [Ideas](<idea-modding.md>) • [Ideologies](<ideology-modding.md>) • [Military industrial organizations](<military-industrial-organization-modding.md>) • [National focuses](<national-focus-modding.md>) • [Resources](<resources-modding.md>) • [Scripted GUI](<scripted-gui-modding.md>) • [Technologies and doctrines](<technology-modding.md>) • [Units](<unit-modding.md>)
- **Map**: [Map](<map-modding.md>) • [States](<state-modding.md>) • [Supply areas](<supply-areas-modding.md>)
- **Graphical**: [Interface](<interface-modding.md>) • [Graphical assets](<graphical-asset-modding.md>) • [Entities](<entity-modding.md>) • [Posteffects](<posteffect-modding.md>) • [Particles](<particle-modding.md>) • [Fonts](<font-modding.md>)
- **Cosmetic**: [Portraits](<portrait-modding.md>) • [Namelists](<namelist-modding.md>) • [Music](<music-modding.md>) • [Sound](<sound-modding.md>)
- **Other**: [Console commands](<console-commands.md>) • [Troubleshooting](<troubleshooting.md>) • [Mod structure](<mod-structure.md>) • [Mods](<mods.md>) • [Nudger](<nudger.md>)
- **Kit pages (not on the wiki)**: [Collection modding](<collection-modding.md>) • [Game rule modding](<game-rule-modding.md>) • [Intelligence operation modding](<intelligence-operation-modding.md>) • [Map mode modding](<map-mode-modding.md>) • [Occupation and resistance modding](<occupation-and-resistance-modding.md>) • [Peace conference modding](<peace-conference-modding.md>) • [Raid modding](<raid-modding.md>) • [Script constant modding](<script-constant-modding.md>) • [Special project modding](<special-project-modding.md>)
