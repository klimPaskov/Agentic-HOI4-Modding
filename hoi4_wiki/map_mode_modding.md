# Map mode modding

*Kit page: written by the Agentic HOI4 Modding Kit from the Hearts of Iron IV 1.19.3.0 game files and re-checked against 1.19.4.1. The wiki has no page for this topic. CC BY-SA 3.0 (see LICENSE.txt).*
<!-- kit:page -->

<!-- kit:begin id="review" at="top" build="1.19.4.1" checked="2026-11-01" sources="common/map_modes/ common/decisions/ common/scripted_guis/ common/defines/ documentation/effects_documentation.md documentation/console_commands_documentation.md interface/ localisation/english/" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Written from: `common/map_modes/documentation.md` (the only file in that folder), the `force_update_map_mode` entry in `documentation/effects_documentation.md`, the map mode bar in `interface/mapmodes_interface.gui`/`.gfx`, `localisation/english/mapmode_l_english.yml` and the `NMapMode` defines.
Checked by search: no vanilla script, event or scripted GUI defines or switches a scripted map mode, so every key below is documented but untested.
Gaps left: whether `color` accepts conditions, the value range of the colour variables, the icon size of a scripted mode and how the "all map modes" window lists scripted modes are not stated anywhere in the files.
**1.19.4.1 re-check (2026-11-01).** 9 kit statements depended on files the update changed (the whole-game text search, the graphics defines, the map mode localisation, the map mode bar interface file, the decisions and scripted GUI folders and the strings of `hoi4.exe`) and all were re-measured. One number moved: `on_map_mode` has 569 uncommented uses in `common/decisions/` (was 528), still with the same three values. Every other statement cites files that are byte-identical in 1.19.4.1 (Steam depot manifest diff).
<!-- kit:end id="review" -->

## Table of contents

- [Overview](#Overview)
- [File and keys](#File_and_keys)
  - [Map mode keys](#Map_mode_keys)
  - [Layer keys](#Layer_keys)
  - [Layer types and scopes](#Layer_types_and_scopes)
- [Colour output](#Colour_output)
- [Targets](#Targets)
- [Text and updates](#Text_and_updates)
- [Localisation and GFX](#Localisation_and_GFX)
- [Activating a map mode](#Activating_a_map_mode)
- [Minimal example](#Minimal_example)
- [Traps](#Traps)

---

A scripted map mode is a map mode whose country or state border colours are computed by script. [docs] `common/map_modes/documentation.md`. The game ships the feature and its documentation but no scripted map mode of its own, so a mod supplies the whole set: one definition file, localisation keys and two button sprites. [vanilla-confirmed 1.19.3] `common/map_modes/` holds only `documentation.md`.

## Overview <a id="Overview"></a>

- A map mode is one block in `scripted_map_modes = { ... }` inside a `.txt` file of `common/map_modes/`. The block name is the map mode id. [docs] `common/map_modes/documentation.md`.
- `common/map_modes/` contains only `documentation.md` in 1.19.4.1, and no other vanilla file, event, decision or scripted GUI mentions `scripted_map_modes`. [vanilla-confirmed 1.19.4.1] text search of the whole game folder; only `documentation.md` and `hoi4.exe` match.
- The string `scripted_map_modes` is present in `hoi4.exe`, so the folder is read by the engine. [unverified] string match only.
- The map mode has two draw layers, `bottom` and `top`, drawn in that order. Each layer asks the script for a colour per border. [docs] `common/map_modes/documentation.md`.

## File and keys <a id="File_and_keys"></a>

### Map mode keys <a id="Map_mode_keys"></a>

All rows: [docs] `common/map_modes/documentation.md`.

| Key | Value | Meaning |
| --- | --- | --- |
| `top` | block | The layer drawn last. Layer keys below. |
| `bottom` | block | The layer drawn first. Same structure as `top`. |
| `far_text` | `none`, `country`, `state`, `faction`, `player` | Text shown on the map when zoomed out. |
| `near_text` | same values | Text shown when zoomed in. |
| `update_daily` | `yes` / `no` | `yes` rebuilds the map mode every day. Otherwise it is rebuilt only by the `force_update_map_mode` effect. |

### Layer keys <a id="Layer_keys"></a>

All rows: [docs] `common/map_modes/documentation.md`.

| Key | Value | Meaning |
| --- | --- | --- |
| `type` | see the next table | Which borders the layer draws, or one of the hard-coded layers. |
| `color` | block | Run once per border to be drawn. It sets the colour through temp variables (see Colour output). |
| `targets` | block | Limits which countries or states are drawn. The doc calls it "highly recommended for performance"; without it the game tries every scope. It takes what targeted decisions take: `target_array`, `targets`, `target_trigger` and so on. |
| `thickness` | `yes` | Set it when the border has a thickness. Then `color` must also set the `thickness` temp variable. |

A layer you do not need is written `bottom = { type = none }`. [docs]

### Layer types and scopes <a id="Layer_types_and_scopes"></a>

All rows: [docs] `common/map_modes/documentation.md`. Inside `color` and `targets` the scope is the player country; `FROM` depends on the layer type.

| `type` | Borders used | `FROM` |
| --- | --- | --- |
| `none` | Nothing is drawn. | not used |
| `country` | Country provinces. | The country being drawn. |
| `state` | State provinces. | The state being drawn. |
| `state_controller` | State provinces split by controller. A state shared between countries is asked once per country. | The state being drawn; `FROM.FROM` is the controller of that part of the state. |
| `game_map_mode_country`, `game_map_mode_states`, `game_map_mode_diplomacy`, `game_map_mode_players`, `game_map_mode_factions`, `game_map_mode_ideology` | The hard-coded vanilla layers. If one is used, all other entries of that layer are ignored. | not applicable |

The six `game_map_mode_*` names are also strings in `hoi4.exe`. [unverified] string match only.

## Colour output <a id="Colour_output"></a>

The `color` block sets these temp variables. [docs] `common/map_modes/documentation.md`.

| Temp variable | Use |
| --- | --- |
| `red`, `green`, `blue` | The border colour. The doc example uses `0.0` and `1.0`. |
| `alpha` | Opacity. The doc example uses `1.0`. |
| `thickness` | Border width. The doc example uses `10.0`. Only read when the layer has `thickness = yes`. |
| `highlighted` | If set, the border pulsates. The doc example sets `1.0`. |

- The documentation example uses 0.0 to 1.0 per channel. [docs] `common/map_modes/documentation.md`. The three map mode colour tables in `common/defines/00_graphics.lua` also keep every colour column between 0 and 1. [vanilla-confirmed 1.19.4.1] Whether `color` accepts values outside that range is [unverified].
- The doc says the colour trigger "returns true" for a border it wants drawn, and that the game then expects the temp variables. Whether an `if` with a `limit` inside `color` hides a border is not stated; limit the drawn scopes with `targets` instead. [unverified]
- There is no gradient key. A gradient is a number you compute from game data and write into the channels, for example a value between 0 and 1 copied into `green` with `red` set to one minus that value (see the example). [unverified] design advice built on the documented temp variables.
- The built-in resistance, compliance and temperature modes use fixed gradient tables in `common/defines/00_graphics.lua`. Each row is a value followed by red, green, blue, alpha, and the colour is interpolated between the two nearest rows. The names are `OCCUPATION_RESISTANCE_MAP_MODE_COLORS`, `OCCUPATION_COMPLIANCE_MAP_MODE_COLORS` and `TEMPERATURE_MAP_MODE_COLORS`. [vanilla-confirmed 1.19.4.1] `common/defines/00_graphics.lua`. Scripted modes cannot read these tables. [unverified]

## Targets <a id="Targets"></a>

- `targets` is the performance control. For `type = country` list countries (for example `target_array = global.majors`); for state layers list states. [docs] `common/map_modes/documentation.md`.
- The doc names `target_array`, `targets` and `target_trigger` as keys that can sit inside `targets`. Their exact behaviour here is borrowed from targeted decisions: see [Decision modding](<decision_modding.md#Targeted_decisions>) and [Game arrays](<data_structures.md#Game_arrays>). [docs] for the names, [unverified] for the equivalence.
- A bare `FROM` in `target_trigger` is not confirmed to be the drawn scope. Test it before relying on it. [unverified]

## Text and updates <a id="Text_and_updates"></a>

- `far_text` and `near_text` choose what the game writes on the map. Allowed values: `none`, `country`, `state`, `faction`, `player`. [docs] `common/map_modes/documentation.md`.
- `update_daily = yes` rebuilds once a day. For a map mode that depends on events, leave it off and rebuild with `force_update_map_mode`. [docs]
- `force_update_map_mode = { limit = { always = yes } mapmode = my_mod_map_mode }` rebuilds a scripted map mode. It works in any scope, makes no tooltip, and `limit` is "limit to check against player". [docs] `documentation/effects_documentation.md`.
- No vanilla file calls `force_update_map_mode`. [vanilla-confirmed 1.19.4.1] text search of `common/`, `events/`, `history/` and `interface/`.

## Localisation and GFX <a id="Localisation_and_GFX"></a>

For a map mode with id `my_mod_map_mode` the game looks for these keys and sprites. [docs] `common/map_modes/documentation.md`.

| Need | Name |
| --- | --- |
| Short name | `MAPMODE_MY_MOD_MAP_MODE` |
| Name | `MAPMODE_MY_MOD_MAP_MODE_NAME` |
| Description | `MAPMODE_MY_MOD_MAP_MODE_DESCRIPTION` |
| Tooltip | `my_mod_map_mode_tooltip` |
| Delayed tooltip | `my_mod_map_mode_tooltip_delayed` |
| Button icon, not selected | `GFX_mapmode_buttons_deselected_small_my_mod_map_mode` |
| Button icon, selected | `GFX_mapmode_buttons_selected_small_my_mod_map_mode` |

- The loc keys are the upper-case id; the two tooltip keys use the id as written. [docs]
- Vanilla modes follow the same pattern: `MAPMODE_FACTIONS`, `MAPMODE_FACTIONS_NAME` and `MAPMODE_FACTIONS_DESCRIPTION` exist. [vanilla-confirmed 1.19.4.1] `localisation/english/mapmode_l_english.yml`.
- The vanilla small icons are one strip per state: `GFX_mapmode_buttons_selected_small` and `GFX_mapmode_buttons_deselected_small` have 18 frames in a 360 by 18 texture, so one frame is 20 by 18 pixels. [vanilla-confirmed 1.19.3] `interface/mapmodes_interface.gfx`, DDS header of `gfx/interface/mapmode/mapmode_buttons_selected_small.dds`.
- The documentation does not state whether a scripted mode's own sprite must use the same 20 by 18 size. [docs] `common/map_modes/documentation.md`. Define the two sprites as plain `spriteType` entries in a `.gfx` file ([Graphical asset modding](<graphical_asset_modding.md#spriteType>)). Whether the engine needs the vanilla size is [unverified].

## Activating a map mode <a id="Activating_a_map_mode"></a>

- There is no effect, trigger or on action that switches the player to a map mode. The only map mode effect in the documentation is `force_update_map_mode`, which rebuilds one. [vanilla-confirmed 1.19.3] the effect names in `documentation/effects_documentation.md` were searched for "map" and "mode"; only `force_update_map_mode` matches.
- The player selects a scripted mode in the map mode bar. How the bar and the "all map modes" window list scripted modes is not stated in the files. The bar has configurable slots 4 to 10 (`UI_CONFIGURABLE_SLOT_FROM` and `UI_CONFIGURABLE_SLOT_TO`, 0-based). [vanilla-confirmed 1.19.4.1] `common/defines/00_graphics.lua`, `interface/mapmodes_interface.gui`.
- Console: `mapmode <int>` changes the map mode by number, and `rebuildlayers` reloads the map modes. [docs] `documentation/console_commands_documentation.md`. Use `rebuildlayers` after editing a map mode file during a test. The documentation gives only "Mapmode type (int)" and no number for a scripted mode. [docs] Which number a scripted mode gets is [unverified]. In a test, `mapmode 12` to `mapmode 20` and `mapmode 1` each answered "Unknown mapmode", so the integer form selected no scripted mode there and no scripted mode number was found. No game crash followed. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, console replies read by OCR. The last reply could belong to the previous command, and `mapmode 0` and names such as `mapmode factions` were not tried.
- `on_map_mode` in decisions is a different feature. Its three values `map_only`, `map_and_decisions_view` and `decision_view_only` choose where a decision is shown. [vanilla-confirmed 1.19.4.1] 569 uncommented uses in `common/decisions/`, no other value.
- A scripted GUI can be limited to a map mode with `map_mode = map_mode_name`. No vanilla scripted GUI sets it. [docs] `common/scripted_guis/_documentation.md`. See [Scripted GUI modding](<scripted_gui_modding.md>). The documentation shows only the placeholder `map_mode_name` and lists no valid names. [docs] 1.19.4.1 does not accept the key at all: a `scripted_gui` block with `map_mode` was rejected at load as "Unexpected token: map_mode", whether the name was a scripted map mode id, a hard-coded layer name (`game_map_mode_factions`) or a made-up name. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, error.log read at load. Because the key itself is rejected, nothing is known about which names would be valid, and whether the rest of those scripted GUIs loaded was not checked.

## Minimal example <a id="Minimal_example"></a>

Colours every major country from red to green by stability. Built only from `common/map_modes/documentation.md`; no vanilla file confirms it works. [unverified]

`common/map_modes/my_mod_map_modes.txt`

```text
scripted_map_modes = {
	my_mod_stability = {
		top = {
			type = country
			targets = { target_array = global.majors }
			color = {
				set_temp_variable = { green = FROM.stability }
				set_temp_variable = { red = 1 }
				subtract_from_temp_variable = { red = FROM.stability }
				set_temp_variable = { blue = 0.1 }
				set_temp_variable = { alpha = 0.8 }
			}
		}
		bottom = { type = none }
		far_text = country
		near_text = none
		update_daily = yes
	}
}
```

`localisation/english/my_mod_map_modes_l_english.yml`

```text
l_english:
 MAPMODE_MY_MOD_STABILITY: "§HStability§! map mode"
 MAPMODE_MY_MOD_STABILITY_NAME: "Stability"
 MAPMODE_MY_MOD_STABILITY_DESCRIPTION: "Major powers from red (unstable) to green (stable)."
 my_mod_stability_tooltip: "Stability map mode"
 my_mod_stability_tooltip_delayed: "Shows national stability."
```

`interface/my_mod_map_modes.gfx` needs `GFX_mapmode_buttons_deselected_small_my_mod_stability` and `GFX_mapmode_buttons_selected_small_my_mod_stability`.

## Traps <a id="Traps"></a>

- The game derives the loc keys, tooltip keys and sprite names from the map mode id, so all of them must spell the id exactly as the file does. [docs] `common/map_modes/documentation.md`
- Without `targets` the game tries to render every scope, which the doc flags as a performance problem. [docs] `common/map_modes/documentation.md`
- A hard-coded `game_map_mode_*` layer ignores the other keys of that layer. [docs]

---

## Navigation

**[Modding](<modding.md>)**

- **Documentation**: [Effects](<effects.md>) • [Triggers](<triggers.md>) • [Defines](<defines.md>) • [Modifiers](<modifiers.md>) • [List of modifiers](<list_of_modifiers.md>) • [Scopes](<scopes.md>) • [Localisation](<localisation.md>) • [On actions](<on_actions.md>) • [Data structures](<data_structures.md>) • [Flags](<data_structures.md#Flags>) • [Event targets](<data_structures.md#Event_targets>) • [Country tag aliases](<data_structures.md#Country_tag_aliases>) • [Variables](<data_structures.md#Variables>) • [Arrays](<data_structures.md#Arrays>)
- **Scripting**: [Achievements](<achievement_modding.md>) • [AI](<ai_modding.md>) • [AI focuses](<ai_focuses.md>) • [Autonomous states](<autonomy_state_modding.md>) • [Balances of power](<balance_of_power_modding.md>) • [Bookmarks/Scenarios](<bookmark_modding.md>) • [Game rules](<bookmark_modding.md#Game_rules>) • [Buildings](<building_modding.md>) • [Characters and traits](<character_modding.md>) • [Cosmetic tags](<cosmetic_tag_modding.md>) • [Countries](<country_creation.md>) • [Divisions](<division_modding.md>) • [Decisions](<decision_modding.md>) • [Doctrines](<doctrine_modding.md>) • [Equipment](<equipment_modding.md>) • [Events](<event_modding.md>) • [Factions](<faction_modding.md>) • [Ideas](<idea_modding.md>) • [Ideologies](<ideology_modding.md>) • [Military industrial organizations](<military_industrial_organization_modding.md>) • [National focuses](<national_focus_modding.md>) • [Resources](<resources_modding.md>) • [Scripted GUI](<scripted_gui_modding.md>) • [Technologies and doctrines](<technology_modding.md>)
- **Map**: [Map](<map_modding.md>) • [States](<state_modding.md>) • [Supply areas](<supply_areas_modding.md>) • [Strategic regions](<strategic_region_modding.md>)
- **Graphical**: [Interface](<interface_modding.md>) • [Graphical assets](<graphical_asset_modding.md>) • [Entities](<entity_modding.md>) • [Posteffects](<posteffect_modding.md>) • [Particles](<particle_modding.md>) • [Fonts](<font_modding.md>)
- **Cosmetic**: [Portraits](<portrait_modding.md>) • [Namelists](<namelist_modding.md>) • [Music](<music_modding.md>) • [Sound](<sound_modding.md>)
- **Other**: [Console commands](<console_commands.md>) • [Troubleshooting](<troubleshooting.md>) • [Mod structure](<mod_structure.md>) • [Mods](<mods.md>) • [Nudger](<nudger.md>)
- **Kit pages (not on the wiki)**: [Collection modding](<collection_modding.md>) • [Defines additions](<defines_additions.md>) • [Game rule modding](<game_rule_modding.md>) • [Intelligence operation modding](<intelligence_operation_modding.md>) • [Map mode modding](<map_mode_modding.md>) • [Occupation and resistance modding](<occupation_and_resistance_modding.md>) • [Peace conference modding](<peace_conference_modding.md>) • [Raid modding](<raid_modding.md>) • [Script constant modding](<script_constant_modding.md>) • [Special project modding](<special_project_modding.md>)
