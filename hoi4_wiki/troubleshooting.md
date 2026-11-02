# Troubleshooting

*Offline snapshot of the Hearts of Iron IV Wiki page "Troubleshooting", revision 105132, captured 2026-10-31. Wiki text by the wiki's contributors under CC BY-SA 3.0 (see LICENSE.txt); kit blocks are local additions under the same license.*

<!-- kit:begin id="review" at="top" build="1.19.4.1" checked="2026-11-01" revision="105132" sources="launcher-settings.json documentation/console_commands_documentation.md documentation/effects_documentation.md documentation/triggers_documentation.md localisation/ignored_loc_keys.txt common/script_enums.txt map/ localisation/english/core_l_english.yml" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Checked against: `launcher-settings.json`, the console, effect and trigger documentation, the `common/` and `map/` folder listings, and string searches of `hoi4.exe`. Log file names and contents also come from the log folder of an earlier 1.19.3 session, which is a user file and not part of the game.
Kit blocks added: corrections for the fatal-error file (`exceptions.log` is not in this build), the console command table and the log file names; a log file table; debug launch and start-up arguments; what a crash folder holds; a warning that `map/rocketsites.txt` no longer exists; a table of 26 engine messages with their log and likely meaning; and a short debugging loop.
Gaps left: most of the page's crash causes could not be re-created without running the game, so they stay as the wiki states them. The words "incomplete", "outdated" and "unknown what" on this page are ordinary prose, not placeholders. Nothing was run in the game before 2026-11-02, and since then only the statements tagged `[game-tested 1.19.4.1]` have been.
**1.19.4.1 re-check (2026-11-01).** Twenty-eight statements depended on files the update changed (the console commands documentation, `launcher-settings.json`, `hoi4.exe` and the folder listings), and all 28 were re-measured on the installed files. No fact changed: every documented command, `hoi4.exe` string, launcher argument and file name still holds, and the page never mentions the removed console command `debug_types`. Every other statement cites files that are byte-identical in 1.19.4.1 (Steam depot manifest diff).
<!-- kit:end id="review" -->

## Table of contents

- [Overview](#Overview)
- [Testing](#Testing)
- [Log files](#Log_files)
- [Crash data log](#Crash_data_log)
- [Common crash causes](#Common_crash_causes)
  - [Main menu loading](#Main_menu_loading)
  - [During country selection](#During_country_selection)
  - [Middle of the game](#Middle_of_the_game)
- [Additional details](#Additional_details)
  - [Kit: Engine messages a modding agent meets most](#kit-engine-messages)
  - [Kit: A debugging loop for scripted changes](#kit-debug-loop)

---

*Troubleshooting* is the identification of the cause of crashes, bugs or other problems.

## Overview <a id="Overview"></a>

In general, there are two kinds of errors: fatal and non-fatal.

Fatal errors occur when the game cannot load a vital piece of data and cannot operate without it present. This causes a crash to desktop (CTD). When fatal errors occur, an exception will be printed to the **exceptions.log**. Typically these errors occur during the loading process or when a specific action is taken in-game.

Non-fatal errors occur when the game encountered invalid data or broken syntax. These errors are almost always printed to the **error.log**.

<!-- kit:begin id="ts-fatal-errors" at="section:Overview" -->
**Kit correction** The wiki says fatal errors print an exception to `exceptions.log`. hoi4.exe 1.19.4.1 has no `exceptions.log` string. It has the strings `crashes/`, `exceptions/`, `meta.yml` and `LastRead: %s (%d)`, which fits a per-crash folder under the user folder, `crashes/hoi4_<yyyymmdd>_<hhmmss>/` (see the crash data section below). [unverified] Three real crashes in the 1.19.4.1 game wrote exactly that folder, and no `exceptions.log` exists anywhere in the user folder. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, crash folders and a file listing of the user folder.

The game's own interface text says map-definition errors "have been logged to error.log" (`localisation/english/core_l_english.yml`, key `MAP_LOADING_ERROR_INTRO`). [vanilla-confirmed 1.19.4.1] Other non-fatal errors go to `logs/error.log` as well, with the mod file and line, for example `common/raids/igc_raids.txt:350: original_tag: Invalid Scope ...` from a test mod. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, error.log read after a script error.

Two debug-only behaviours matter when an error "does nothing" in a normal run. Some effects show their tooltips only in debug mode (`activate_shine_on_focus`, `deactivate_shine_on_focus`, `has_shine_effect_on_focus`), and `clamp_variable` logs an error for `max < min` only in debug mode. [docs] `documentation/effects_documentation.md`, `documentation/triggers_documentation.md`
<!-- kit:end id="ts-fatal-errors" -->

## Testing <a id="Testing"></a>

Performing testing is vital to debugging a mod. Typically this is done via the in-game console with commands.

These are useful console commands for modders:

| Command | Usage |
| --- | --- |
| reloadfx all | Reloads most of the effects used in the game, such as fog of war, the HDR and opacity of country borders, ect. |
| reload texture | Reloads most of the textures used in the game, such as leader portraits, technology icons, etc. |
| reload localization | Reloads most of the localization used in-game, such as event titles and descriptions. |
| reload defines | Reloads the defines files from `/Hearts of Iron IV/common/defines/`. |
| reload focus | Reloads the focus trees in `/Hearts of Iron IV/common/national_focuses/`. |
| reloadoob | Reloads the starting OOB file for the specified tag. |
| reloadtechnologies | Reloads the technology files. Will cause a crash if an error is encountered. |
| reloadinterface | Reloads the interface files (.gui). |
| reload decision | Reloads the decision files (.gui and common/decisions). |
| tdebug | Activates the debug tooltips, displaying important information such as state ID, province ID, etc. |
| event | Fires the specified event immediate for the current player country. |
| nocb | Removes restrictions on diplomatic actions. |
| observe | Places the player into the observer slot, allowing the game to pass without player input. |
| aiview | Displays the AI priorities when hovering over specific buttons, such as technology. |
| tag | Switches the player to another country. |
| update_loc | Reloads the specified localization key. |
| updateequipments | Reloads the equipment files in `/Hearts of Iron IV/common/units/equipment/`. |
| updatesubunits | Reloads the unit files in `/Hearts of Iron IV/common/units/`. |
| research_on_icon_click | Activates research on click, allowing you to click on technologies to research them instantly. |
| Focus.NoChecks | Removes the trigger checks for focuses. |
| Focus.AutoComplete | Activates instant completion for focuses. |
| set_country_flag | Sets the specified country flag for the current country. |
| add_ideas | Adds the specified idea to the current country. |

<!-- kit:begin id="ts-testing-check" at="section:Testing" -->
**Kit correction** The rows above checked against 1.19.4.1. Rows not named here exist as written: `event`, `nocb` (alias of `allowdiplo`), `observe` (alias `spectator`), `aiview`, `tag`, `update_loc`, `updateequipments`, `updatesubunits`, `research_on_icon_click` (alias `roic`), `Focus.NoChecks`, `Focus.AutoComplete`, `set_country_flag` and `add_ideas`. [docs] `documentation/console_commands_documentation.md`

| Wiki row | In 1.19.4.1 |
| --- | --- |
| `reload texture` | The documented command is `reload_textures` (aliases `rt`, `reload_texture`) with optional file-name filters. [docs] `documentation/console_commands_documentation.md` |
| `reload localization` | The documented command is `update_loc <localization tag>`. There is no `reload` entry in the documentation. [docs] `documentation/console_commands_documentation.md` |
| `reload defines`, `reload focus`, `reload decision` | `reload` is not documented. [docs] hoi4.exe contains the message `defines reloaded!` and keeps the short names `focus`, `cfocus`, `ideas`, `ability`, `scriptedgui` and `scripted_effects` next to `common/` folder paths, so `reload <name>` probably exists (executable strings). It does exist: `reload defines`, `reload focus` and `reload decision` each printed "<name> reloaded!" in the game, as did seven other targets listed in [Console commands](<console_commands.md#Modding-useful_commands>). [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, console reply. |
| `reload focus` ("`common/national_focuses/`") | The folder is `common/national_focus/`. There is no `national_focuses` folder in the installed game. [vanilla-confirmed 1.19.4.1] folder listing of `common/` |
| `reloadfx all` | `reloadfx` is documented with `map`, `mapname`, `postfx` or a `*.fx` file name. [docs] `documentation/console_commands_documentation.md` hoi4.exe also prints `reloadfx all` in its usage message (executable string). `reloadfx all` works: it printed "all reloaded!", and `reloadfx postfx` printed "Map reloaded". [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, console reply. |
| `reloadtechnologies` ("will cause a crash if an error is encountered") | Documented only as "Reloads the technology database". [docs] `documentation/console_commands_documentation.md` The crash remark is not in the documentation, and whether a faulty file crashes the game is untested. [unverified] |
| `tdebug` | Alias of `provtooltipdebug`, which toggles the debug info in the province tooltip. [docs] `documentation/console_commands_documentation.md` |
| `reloadoob`, `reloadinterface`, `updateequipments`, `updatesubunits` | Exist with the documented effect "reload orders of battle" (argument `<Target Country Tag>`), "reload the entire interface", "update the equipment database" and "update the sub-unit database". [docs] `documentation/console_commands_documentation.md` |

Commands that are more useful for finding script mistakes than the ones above are `loc_check`, `loc_check_events`, `loc_check_focuses`, `loc_check_decisions`, `loc_check_characters`, `loc_check_modifiers`, `loc_check_national_spirits`, `debug_checkportraitssanity`, `error`, `list_flags`, `list_vars`, `list_ideas`, `list_modifiers`, `eval_effect`, `eval_trigger` and `testevent`. All exist in 1.19.4.1. [docs] `documentation/console_commands_documentation.md` They are described in [Console commands](<console_commands.md#Modding-useful_commands>).
<!-- kit:end id="ts-testing-check" -->

## Log files <a id="Log_files"></a>

The game stores various log files in your HOI4 user folder: (Windows: `\Documents\Paradox Interactive\Hearts of Iron IV\logs\`, Linux: `.local/share/Paradox Interactive/Hearts of Iron IV/logs`). These are overwritten every time the game is started.

To enable full error logging, add the `-debug` launch command via *Set Launch Options* in Steam.

| File | Description | Usefulness |
| --- | --- | --- |
| ai.log | Prints the AI choices undertaken. | Medium |
| ai_trace.log | Prints the AI movements undertaken (divisions, ships, air, etc.) | Low |
| error.log | Prints the various non-fatal errors. Many errors can be ignored, although almost all errors relating to files in the *common* folder should be fixed. | High |
| exceptions.log | Prints the stack trace when the game crashes to desktop. | Low |
| executedcommands.log | Prints the internal commands uses by the player and AI. | Low |
| game.log | Prints the actions that were taken by countries in-game. Useful when the crash is due to a specific action. | High |
| graphics.log | Prints the graphical errors relating to positions, rivers, and trees. | Low |
| memory.log | Prints the memory used during setup. Useful for crashes during the loading process, to see when the game crashed. | High |
| message.log | Prints the session info for the current session. | Low |
| postedcommands.log |  | Low |
| random.log | Prints times for game state changes. | Low |
| receivedcommands.log | Prints the internal commands received by the player in multiplayer. | Low |
| sentcommands.log | Prints the internal commands sent by the player in multiplayer. | Low |
| setup.log | Prints the completion of setup loading for each part of the process. Very useful for discovering which file may be causing a crash. | High |
| system.log | Prints the system information HOI4 is loaded on. | Low |
| system_debug.log | Prints interface errors. | Medium |
| text.log | Prints asserts on localization keys. | Medium |
| time.log | Prints the time it takes for the various loading steps to complete, and the tick interval. Very useful for crashes during the loading process, to see when the game crashed. | Medium |

<!-- kit:begin id="ts-log-files" at="section:Log_files" -->
**Kit correction** Log file names and locations in 1.19.3.

- User folder: `launcher-settings.json` sets `gameDataPath` to `%USER_DOCUMENTS%/Paradox Interactive/Hearts of Iron IV`, so the logs are in `logs/` under that folder. [vanilla-confirmed 1.19.4.1] `launcher-settings.json` The Windows Documents folder can be redirected (for example by OneDrive), so look where `%USER_DOCUMENTS%` points. hoi4.exe also contains the argument `userdir=` and the file name `userdir.txt`, which suggests the folder can be moved. [unverified]
- The four command logs use underscores: `executed_commands.log`, `posted_commands.log`, `received_commands.log` and `sent_commands.log`. The wiki table spells them without underscores. The names `executed_commands`, `posted_commands`, `received_commands`, `sent_commands`, `error`, `game`, `graphics`, `memory`, `message`, `random`, `setup`, `system_debug`, `text`, `time` and `ai_trace` are strings in hoi4.exe, next to `code_revisions`, `scenario_testing` and `custom_automated_stats`. [unverified]
- `exceptions.log` has no matching string in hoi4.exe; a crash writes a folder under `crashes/` instead (see the crash data section). [unverified] Three real crashes wrote such a folder, and no `exceptions.log` exists anywhere in the user folder. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, crash folders and a file listing of the user folder.
- A line starts with `[hh:mm:ss][game date]:`. The game date reads `no_game_date` until a game has started, so a line reads `[hh:mm:ss][no_game_date]: text` before a game and `[hh:mm:ss][1936.01.01.12]: text` in a game. 1.19.4.1 prints no `[file.cpp:line]` part. A line written by the `log` effect repeats the time and date inside the message. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, log files read after a menu start and a 1936 game. An earlier 1.19.3 session had shown a `[source.cpp:line]` part. [unverified] (seen in the log files of that session, not in the installed game files)
- The `logs/` folder of the 1.19.4.1 game held `ai.log`, `ai_trace.log`, `code_revisions.log`, `error.log`, `executed_commands.log`, `game.log`, `graphics.log`, `memory.log`, `message.log`, `pdxsdk.log`, `posted_commands.log`, `random.log`, `received_commands.log`, `scenario_testing.log`, `sent_commands.log`, `setup.log`, `system.log`, `system_debug.log`, `text.log` and `time.log`, plus the folders `metrics/` and `variable_dumps/`. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, file listing. What each file holds is the "Holds" column below. The multiplayer part, whether the four command logs get content in a lobby, was not run.

All rows below: [unverified]. The "Holds" column describes log files written by an earlier 1.19.3 session (modded, single player); it is not taken from the installed game files.

| File | Listed on the wiki | Holds |
| --- | --- | --- |
| `error.log` | yes | Script, database, interface and file errors with the file path and line. The largest log in the observed session (about 17 MB, modded); start here. |
| `text.log` | yes | `Duplicate localization found, key: <KEY>, file: <path>, value: <text>` lines. Both files that define the key are listed. |
| `system_debug.log` | yes | Interface layout warnings, for example `Object "<name>" has illegal position with x: <n> in "<window>"`. |
| `game.log` | yes | Start-up summary (`<n> defines loaded`, `Loaded <n> provinces`, history execution, the `Launching SINGLEPLAYER-game` banner) and output of the `log` effect. |
| `setup.log` | yes | One line per loaded database entry or file group (`Ideas loaded ...`, `StaticModifier #<n> tag = ...`). Shows how far loading got. |
| `memory.log` | yes | Memory use after each start-up step. |
| `system.log` | yes | Operating system, processor, memory and graphics adapter data. |
| `graphics.log` | yes | Map generation notices such as `Circular river found at <x>, <y>`. |
| `ai.log` | yes | AI diplomacy decisions (`WillAIAccept: ...`). |
| `ai_trace.log`, `message.log`, `time.log`, `pdxsdk.log`, `scenario_testing.log` | partly | Empty in the observed session. |
| `random.log`, `random_1.log`, `random_2.log` | `random.log` only | Random-number and game-reset timing notes. |
| `code_revisions.log` | no | Game and engine commit hashes with timestamps (`game_hash_long`, `external_libs_hash_long`). Quote it in bug reports. |
| `executed_commands.log`, `posted_commands.log`, `received_commands.log`, `sent_commands.log` | spelled without underscores | Command queue logs; empty in the observed single-player session. |
| `metrics/`, `variable_dumps/` | no | Sub-folders. hoi4.exe contains the path `logs/variable_dumps/`, probably where `print_variables` writes. |

Script can write to the logs on purpose. The `log` effect and the `log` trigger print a message to `game.log`; the effect also prints to the console and to the history logger. `random_list` accepts `log = yes` to record each dice roll in `game.log`. `print_variables` writes all variables in scope to a file (`file`, `text`, `append`, `print_global`, optional `var_list`). [docs] `documentation/effects_documentation.md`, `documentation/triggers_documentation.md`
<!-- kit:end id="ts-log-files" -->

<!-- kit:begin id="ts-debug-launch" at="section:Log_files" -->
**Kit note** Debug launch and start-up arguments.

- The Paradox launcher offers an alternative executable labelled "Open game in Debug Mode" that runs `hoi4.exe` with `-gdpr-compliant -debug_mode`. The normal entry passes only `-gdpr-compliant`. [vanilla-confirmed 1.19.4.1] `launcher-settings.json`
- The `is_debug` trigger returns true when the game runs in debug mode and its documentation names the argument `-debug`. [docs] `documentation/triggers_documentation.md` The wiki's advice to add `-debug` as a Steam launch option therefore matches the documentation. How `-debug` and `-debug_mode` relate inside the engine is not documented. [unverified]
- The game files do not show whether a Steam launch option reaches `hoi4.exe` through the Paradox launcher, whose only listed arguments are the ones above. [unverified]
- The `debug` console command toggles debug mode while the game runs. [docs] `documentation/console_commands_documentation.md`
- hoi4.exe contains these argument names, so they probably exist: `debug`, `crash_data_log`, `nofilewatcher`, `noai`, `nothreadedload`, `suppress_error_log`, `log_messaging`, `gamelog`, `dumpdb`, `dump_script_doc`, `dump_history`, `logprefix=`, `logpostfix=`, `userdir=`, `settings=`, `mod=`, `exclude_dlc=`, `start_tag=`, `start_save`, `auto_run=`, `start_speed=`, `autosave=`, `hands_off`, `quickstart`, `ai_view`, `human_ai`, `asserts`, `noasserts`, `force_text_save`, `disableoutdatedmodwarning`, `allowoldsave`. What each one does is not documented. [unverified]
<!-- kit:end id="ts-debug-launch" -->

## Crash data log <a id="Crash_data_log"></a>

When the game crashes, it provides information on system settings and what caused it to crash in the [user directory's](<modding.md>) `/Hearts of Iron IV/crashes/` folder. Although most of the time this is not beneficial as to what caused it to crash, the error log could contain clues. However, one important logging mechanism can be additionally turned on:

Adding the `-crash_data_log` launch command via *Launch Options* in Steam will also cause the `meta.yml` file in that folder (*Directly within*, not in the `/logs/` subfolder) to contain the last read line of code before crashing, as well as turning on the debug mode. This slows down the game by a significant amount, so it shouldn't be used outside of crash debugging. **If the last read line of the file given is the last line in the file, it's rather likely the game crashed on the *next* read file instead, which is quite difficult to locate.** In some cases, the game can grant a script instead of a file, such as a savefile or client_ping.
This can appear like `LastRead: map/supply_nodes.txt (727)` (Where the number represents the line of the file that was last read before the crash occurred) or `LastRead: client_ping (1)`.

Note that while -crash_data_log enables debug mode, not all benefits of the launch option get applied by default and require using both launch options. For example, edits to files indexed during the main menu loading will not get automatically loaded, requiring a console command usage to get reloaded instead. However, -crash_data_log's debug does include the game loading into the main menu with map errors, the nudge being available for selection, and the debug information when hovering over a province or a country.

<!-- kit:begin id="ts-crash-folder" at="section:Crash_data_log" -->
**Kit note** What a 1.19.3 crash leaves behind.

- hoi4.exe contains the format strings `LastRead: %s (%d)` and `LastScript: %s`, so the crash data can name the last script as well as the last file read. The wiki mentions only `LastRead`. [unverified]
- A crash folder from an earlier 1.19.3 session was named `crashes/hoi4_<yyyymmdd>_<hhmmss>/` and held `exception.txt` (stack trace and exception code), `meta.yml`, `minidump.dmp`, copies of `settings.txt`, `pdx_settings.txt`, `gameplaysettings.txt`, `dlc_load.json` and `mods_registry.json`, and a `logs/` folder with copies of `error.log`, `system.log` and `code_revisions.log`. [unverified] (observed in a user folder, not in the installed game) Three real crashes in 1.19.4.1 each left `dlc_load.json`, `exception.txt`, `gameplaysettings.txt`, `logs/` (`code_revisions.log`, `error.log`, `system.log`), `meta.yml`, `minidump.dmp` (12 MB), `mods_registry.json` (0 bytes), `pdx_settings.txt` and `settings.txt`. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, crash folders listed.
- The `meta.yml` of that crash listed the build (`AppVersion`, `SCMCommit`), the system, `LaunchArguments`, `DataChecksum`, `HasMods` and `Mods`. It had no `LastRead` line, and the run did not use `-crash_data_log`. [unverified] (same observation) The `meta.yml` of the three real 1.19.4.1 crashes also had no `LastRead` or `LastScript` line and listed the active mods. They were not run with `-crash_data_log`. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, meta.yml read.
- A stack trace that points only into `hoi4.exe` carries no mod information. In the three real crashes `exception.txt` showed only `hoi4.exe`, `KERNEL32` and `ntdll` frames and named no mod file. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, exception.txt read. The copied `error.log` is the part of the folder that names mod files. [unverified]
<!-- kit:end id="ts-crash-folder" -->

## Common crash causes <a id="Common_crash_causes"></a>

**A variety of crash types are caused by recklessly unloading folders with [replace_path](<modding.md#Mod_structure>)**, leading to the game detecting there not being any database entries of a certain type. It's best practice to port over generic files to the mod if overwriting a folder in entirety for this reason, as well as to avoid unintuitive errors.

In case of a different crash, note that if a file is completely empty, the game may skip reading it in entirety. As such, the same crash may display a different file if the one in this list is empty.
It's best to completely clean the error log before trying to find a crash, as some errors may appear innocuous while still crashing the game.

If the last read file proves useless, it's possible to temporarily remove files from the mod and slowly re-add them to find the exact cause; upon finding the cause folder, it should be adjusted accordingly. A sort of binary search can be used by adding/removing the files large chunks at the time. replace_paths can be removed aside from essential ones: `history/states/` and `map/strategicregions`. Note that [**both** \*.mod files need to be edited for replace_paths to apply.](<modding.md#Mod_structure>)

**This list is non-exhaustive**: There are more potential crashes, and any given file or script can have more causes that are not outlined in the list. This has been broken up into sections on when they happen for easier navigation. The file provided is the file marked as last read by the crash data log.

<!-- kit:begin id="ts-last-read-labels" at="section:Common_crash_causes" -->
**Kit note** The "last read" labels the wiki uses are partly present in 1.19.4.1. hoi4.exe contains the exact strings `client_ping`, `hourly_tick`, `set_controller` and `shared_focus`, so those labels can still appear in `LastRead` or `LastScript`. It contains no string `savegame.hoi4` or `numbers.pr`. [unverified]
<!-- kit:end id="ts-last-read-labels" -->

### Main menu loading <a id="Main_menu_loading"></a>

<!-- kit:begin id="ts-menu-loading-fix" at="heading:Main_menu_loading" -->
**Kit correction** The `map/rocketsites.txt` bullets are out of date. The installed 1.19.4.1 `map/` folder has no `rocketsites.txt` (it holds `adjacencies.csv`, `adjacency_rules.txt`, `ambient_object.txt`, `buildings.txt`, `cities.txt`, `colors.txt`, `continent.txt`, `default.map`, `definition.csv`, `positions.txt`, `railways.txt`, `seasons.txt`, `supply_nodes.txt`, `unitstacks.txt`, `weatherpositions.txt`, the bitmaps and the `strategicregions`, `supplyareas` and `terrain` folders), and hoi4.exe has no `rocketsites` string. The "last read" file for those crashes will be a different one now. [vanilla-confirmed 1.19.4.1] folder listing; [unverified] for hoi4.exe and for the new last-read file.

`numbers.pr` is also absent from hoi4.exe. The career profile file in the user folder is named `career_profile_<id>_v3.pr` in a 1.19.3 install. [unverified]

Files named in the other bullets still exist in 1.19.4.1: `common/countries/cosmetic.txt`, `gfx/models/supply/railroad.shader`, `tutorial/tutorial.txt`, `map/cities.txt`, `map/buildings.txt`, `map/supply_nodes.txt`, `map/railways.txt`, `history/general/`, `history/countries/`, `history/units/`, `common/ai_templates/`, `common/national_focus/`, `common/continuous_focus/`, `common/unit_leader/` and `common/country_tags/` (which holds `00_countries.txt` and `zz_dynamic_countries.txt`). [vanilla-confirmed 1.19.4.1]
<!-- kit:end id="ts-menu-loading-fix" -->

- `common/countries/cosmetic.txt` – Caused by a complete overwriting of `common/national_focus/` or `common/continuous_focus/`.
- `map/rocketsites.txt` – Caused by a complete overwriting of `history/states/` or `common/unit_leader/`. As there are no "generic files" for states, one should be created manually instead.
- `common/national_focus/*.txt` – This crash, granted that it's the last line of the last file in the folder, can be caused by a focus tree using a `shared_focus = my_focus` argument, specifying a shared focus that does not exist.
- `gfx/models/supply/railroad.shader` – Caused by an error within the [the .bmp files creating the map](<map_modding.md>). This can be a wide variety of causes. Some causes include provinces.bmp having dimensions as numbers that are undivisible by 256, having a size of over 40 MiB, the dimensions changing between different bitmaps (aside from trees.bmp, where the size changes the density of static models), or an incorrect DIB header formatting (such as setting encoding to be used or using BITMAPV5HEADER instead of BITMAPINFOHEADER) in any bitmap.
- `history/general/*.txt` / `history/countries/*.txt` / `map/rocketsites.txt` (In order in which they'd appear with replace_paths to the previous ones) — One of the states within the mod has a `victory_points = { ... }` definition that attempts to assign victory points to a province that does not exist within the game.
- `savegame.hoi4` (takes on the name of a savefile, not necessarily one that exists right now) or `map/cities.txt` – Caused by there being a large quantity of countries defined while there are few (such as 15) or no dynamic countries. The exact amount of countries that the game can handle is not a consistent number, usually falling in the range of 40–80. Typically caused by a reckless overwriting of `common/country_tags` or the file that stores the dynamic countries being outdated.
- `numbers.pr` or `career_profile_*.pr` - Caused primarily by the strategic regions being broken (usually by a lot of provinces not having one). Since in this state it's impossible to get to the nudger to fix them from there, it is possible to edit their files in a text editor, preferably with help of a tool that helps visualize the map (like the HOI4 Mod Utilities extension for Visual Studio Code).

### During country selection <a id="During_country_selection"></a>

This also includes the loading after a country has been selected, but it's not yet possible to play.

- `set_controller` – This crash typically happens when trying to select a country in a bookmark if the country doesn't have a valid capital defined within its `/Hearts of Iron IV/history/countries/TAG*.txt` file. The game uses the capital in order to determine what portion of the map to zoom onto, and not getting one is unexpected.
- `history/units/filename.txt` – One of the naval orders of battle in the mod has a carrier defined with airwings directly inside, as was done in 1.11 and earlier. Adjust the orders of battle in the mod as needed. Note that the file shown as the last read one is not necessarily the one that crashes the game.
- `history/units/filename.txt` / `map/railways.txt` – Caused by a country having a division template, yet not finding any possible `/Hearts of Iron IV/common/ai_templates` entry to use to expand on the template. The exact file/script in question depends on *when* the country obtains the division template: an order of battle (which'll be last read) or another history file (leading to railways).
- `map/supply_nodes.txt` or `map/railways.txt` – This crash is most commonly caused by the specified building types being placed on invalid provinces, such as those that are not located in states. This crash occurs both when trying to open the supply menu in nudge or when trying to start a single player game. This can be corrected by emptying the files in question and [optionally creating a proper definition of the files, either manually or via nudge](<map_modding.md>).
- `tutorial/tutorial.txt` – This crash is caused by the tutorial file being erroneous. This can be represented as a link to an invalid state ID within the file (such as if every base game state was erased) or as the file lacking a `tutorial = { ... }` definition of any kind entirely. Replacing the entire file's contents with `tutorial = { }` works to solve the crash.

This is also the last file that gets read after the country selection process finishes. If a crash occurs directly afterwards and the game fails to write the file properly, it will land on this one.

### Middle of the game <a id="Middle_of_the_game"></a>

- `client_ping` or `hourly_tick` – This crash is caused by the in-game AI, which can be seen by turning off the AI [using the console](<console_commands.md>). There are several causes for this occurring, including but not limited to:
  - A country has a division template, yet couldn't find any `/Hearts of Iron IV/common/ai_templates` entry to use to expand on the template. Typically caused by a reckless overwriting of the folder with replace_path or an error in setting up the `blocked_for = { ... }`/`available_for = { ... }` blocks.
  - Any state not having an owner defined in the history file. In general, such states always run unstably, with a lot of actions crashing them, such as right-clicking or attempting to transfer one to a country. One of such actions is attempting an air mission over that state. As the AI is able to use airplanes, they will try to attempt to at least evaluate the value of doing a mission over the state, which results in a crash to desktop.
  - [An incomplete `map/buildings.txt`](<map_modding.md#Buildings>). The buildings file is used for determining into which sea province the naval bases and floating harbours will go out into, alongside positioning building models. This information is necessary when attempting to use any naval base or floating harbour, as the game would have no idea via which province the province connects to the sea otherwise. The game also checks this information when attempting to *build* a naval base, and if the game attempts to evaluate an invalid naval base definition, the game gets stuck in an infinite loop of attempting to obtain the naval base information, resulting in a CPU/GPU overload and a game crash. This also results in an error.log entry of `Province 12345 is setup as coastal but has no port building in the nudger. This will likely crash the game.` after launching the game.
  - One or more equipment that's in the game, doesn't have a sub-unit defined for it. Can be cause of reckless overwriting of the units file from base game by creating a file with same name or use of replace_path `/Hearts of Iron IV/common/units`.

## Additional details <a id="Additional_details"></a>

A version tracking website, such as `[Gitlab]` or `[Github]`, can be used to keep track of updates to the code. As such, it can be beneficial to use them and regularly push mod's updates to them in order to limit the selection of possibly problematic files when trying to debug an issue.

When the game has a major update, it can be important to read the patch notes to fix the newly-appearing errors. For example, the 1.12's patch notes provide an "Important modding notes" section, which also serves as a check-list of necessary things to fix in the mod in order to avoid a crash. It is also important to avoid overwriting most base game files when possible in order to ease compatibility, though this is not always possible. One folder where it's incredibly important to do is [defines, where an override file is essentially mandatory](<defines.md#Overrides>) in order to avoid even minor game updates from introducing crashes.

In case the game crashes on startup, but there's no obvious reason why in the error log and it's unknown what was last changed since the last time, the mod could have folders strategically removed. As an example, it is almost always possible to remove the entire `/Hearts of Iron IV/common/` folder from the mod without the game crashing, provided debug mode is turned on and there are no replace_paths to the folder.

<!-- kit:begin id="ts-engine-messages" at="section:Additional_details" -->
### Kit: Engine messages a modding agent meets most <a id="kit-engine-messages"></a>

Every message in the first column is a string in hoi4.exe 1.19.4.1. [unverified] The "Seen in" column records which log held the message in an earlier 1.19.3 session (modded, single player); "not seen" means it was not in those logs. The "Usual meaning" column is an interpretation of the message text and the surrounding strings, not a documented rule. [unverified]

Most script errors carry two numbers, `near line: <a>` inside the message and `near line: <b>` after the file path. Treat both as pointers and look at the lines between them. [unverified]

| Message | Seen in | Usual meaning |
| --- | --- | --- |
| `Unknown effect-type: <name>`, `Unknown trigger-type: <name>` | `error.log` | The name is not an effect or trigger at that place: a typo, a removed token, an undefined scripted effect or trigger, or a country tag written as a bare key. |
| `Invalid effect '<name>' in <file> line : <n>`, `Invalid trigger '<name>' in <file> line : <n>` | `error.log` | The validation pass rejects the token as an effect or trigger. It often repeats an `Unknown ...-type` error. |
| `Trigger failed to validate: <file>:<line>: <trigger>` | `error.log` | A trigger sits in a block where it is not allowed or its scope is wrong (observed with `has_completed_focus` inside a military industrial organization file). |
| `Invalid scope for trigger`, `Invalid scope for effect` | not seen | An effect or trigger runs in a scope it does not support. Check the scope list in [Effects](<effects.md>) or [Triggers](<triggers.md>). |
| `Duplicate localization found, key: <KEY>, file: <path>, value: <text>` | `text.log` | Two files of the same language define one key, and each defining file gets a line. The report also listed keys that a `localisation/replace/` file overrides on purpose, so a listed pair is a mistake only when you did not intend the override. |
| `The game has loc key collisions. Check logs/text.log for more details` | not seen | The on-screen counterpart of the previous line. |
| `Duplicate database id <id>` | `error.log` | An id that must be unique within its database is defined twice (observed for special project specialisations). |
| `Warning: Found duplicate equipment "<id>" in file "<path>" line: <n>. Overriding old.` | `error.log` | The later definition replaces the earlier one. hoi4.exe has matching messages for upgrades and modules. |
| `Mutual exclusive paths are not symmetric` | not seen | A technology lists a mutually exclusive technology that does not list it back. Related strings: `Mutually exclusive Technologies <a> and <b> have different starting points in folder <f> for parent <p>` and `Technology <t> has no coordinates in folder <f> for parent <p>`. |
| `Found no grid box for tech <tech>` | `error.log` | The technology tree interface has no grid box for the folder that technology belongs to. Compare with `interface/countrytechtreeview.gui`. |
| `<focus> does not exist. Relative focus must be scripted before this.` | not seen | A focus whose `relative_position_id` names a focus that is missing or written later in the file. Put the referenced focus first. |
| `Focus <id> (<tree>) does not have a default icon case`, `Missing icon for focus: <id>` | not seen | A focus has alternate icons without a default, or its icon sprite is missing. |
| `<event>: Event is missing a title.`, `... missing a desc.`, `... has no options.` | not seen | Event validation. Related strings: `Event is triggered only, but does not have a 1 base-factor.`, `Event is set to trigger every day.` and `Event is a leader event and has to be triggered only.` |
| `Value does not belong to designated Script EnumType: <x> not in <enum>` | `error.log` | A token is not in the list of its script enum in `common/script_enums.txt` (observed enum: `script_enum_equipment_bonus_type`). |
| `<x> is an equipment type or equipment category but is not in script enum script_enum_equipment_bonus_type` | `error.log` | A new equipment type or category needs an entry in that enum in `common/script_enums.txt`. |
| `<TAG> - is not in the tag list` | `error.log` | The tag is used somewhere but not defined in `common/country_tags/`. |
| `<path> - expecting country tag or (generic) keyword.` | `error.log` | A file in `common/units/names/` starts with a key that is neither a known tag nor `generic`. |
| `<gui file> (line <n> ): Could not find "<element>" in window <window>` | `error.log` | A GUI file or script refers to an element that the window does not define, usually after a mod replaces a vanilla `.gui` file. |
| `Object "<name>" has illegal position with x: <n> in "<window>"` | `system_debug.log` | An interface element lies outside its container. A layout warning that vanilla also produces. |
| `<file>:<line>: recruit_character: Unknown character <id>` | `error.log` | `recruit_character` names a character that no loaded file defines. |
| `Collection input type is empty: <token>` | `error.log` | A collection operator got an empty or unrecognised input. |
| `invalid database object for effect/trigger: ... use var:var_name to explicitly use variables in effects/triggers` | `error.log` | A variable name stands where a database token is expected; write it as `var:<name>`. |
| `Country "<TAG>" does not have any equipment variant for type "<type>"` | `error.log` | A history or order-of-battle file uses an equipment type for which the country has no variant. |
| ``Incorrect usage of `supply_factor` modifier (use `supply_consumption_factor` instead)`` | `error.log` | The modifier name is wrong. The message names the replacement. |
| `Province <id> is setup as coastal but has no port building in the nudger. This will likely crash the game.` | not seen | The `map/buildings.txt` case described in the crash causes below. |
| `No missing or bad loc keys found`, `<n> missing loc keys found`, `<n> bad loc keys found` | not seen | Result lines of the `loc_check` commands. |
<!-- kit:end id="ts-engine-messages" -->

<!-- kit:begin id="ts-debug-loop" at="section:Additional_details" -->
### Kit: A debugging loop for scripted changes <a id="kit-debug-loop"></a>

1. Start from empty logs. The wiki says the logs are overwritten on every start, so a fresh start is enough. Every launch truncates and rewrites `logs/`. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, logs compared across launches.
2. Run the failing action in a debug-mode game, then open `logs/error.log` and search for your mod's folder name or ids. Entries name the file and line. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, error.log read after script errors.
3. Open `logs/text.log` for duplicate localisation keys and run `loc_check` in the console for missing ones. Keys listed in `localisation/ignored_loc_keys.txt` are skipped by the check. [docs] `documentation/console_commands_documentation.md`, [vanilla-confirmed 1.19.3] `localisation/ignored_loc_keys.txt`
4. For portraits run `debug_checkportraitssanity`; failures go to the error log. [docs] `documentation/console_commands_documentation.md`
5. To see why a trigger or effect misbehaves, put a `log` effect or trigger in the script and read `game.log`, or use `eval_trigger`, `eval_effect`, `list_flags` and `list_vars` in the console. [docs] `documentation/effects_documentation.md`, `documentation/console_commands_documentation.md`
6. If the game crashes at start-up, `setup.log` can show the last loaded entry, but its tail did not name the faulty file in one test. After a start-up crash (an integer divide by zero) the last line was an unrelated `on_actions` entry (`16_taog_on_actions.txt ... on_subject_annex`). [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, setup.log read after the crash. Then read the copy of `error.log` in the crash folder. [unverified]
7. Fix the first error in `error.log` before the later ones. Many later lines are caused by the first. [unverified]
<!-- kit:end id="ts-debug-loop" -->

---

## Navigation

**[Modding](<modding.md>)**

- **Documentation**: [Effects](<effects.md>) • [Triggers](<triggers.md>) • [Defines](<defines.md>) • [Modifiers](<modifiers.md>) • [List of modifiers](<list_of_modifiers.md>) • [Scopes](<scopes.md>) • [Localisation](<localisation.md>) • [On actions](<on_actions.md>) • [Data structures](<data_structures.md>) • [Flags](<data_structures.md#Flags>) • [Event targets](<data_structures.md#Event_targets>) • [Country tag aliases](<data_structures.md#Country_tag_aliases>) • [Variables](<data_structures.md#Variables>) • [Arrays](<data_structures.md#Arrays>)
- **Scripting**: [Achievements](<achievement_modding.md>) • [AI](<ai_modding.md>) • [AI focuses](<ai_focuses.md>) • [Autonomous states](<autonomy_state_modding.md>) • [Balances of power](<balance_of_power_modding.md>) • [Bookmarks/Scenarios](<bookmark_modding.md>) • [Game rules](<bookmark_modding.md#Game_rules>) • [Buildings](<building_modding.md>) • [Characters and traits](<character_modding.md>) • [Cosmetic tags](<cosmetic_tag_modding.md>) • [Countries](<country_creation.md>) • [Divisions](<division_modding.md>) • [Decisions](<decision_modding.md>) • [Doctrines](<doctrine_modding.md>) • [Equipment](<equipment_modding.md>) • [Events](<event_modding.md>) • [Factions](<faction_modding.md>) • [Ideas](<idea_modding.md>) • [Ideologies](<ideology_modding.md>) • [Military industrial organizations](<military_industrial_organization_modding.md>) • [National focuses](<national_focus_modding.md>) • [Resources](<resources_modding.md>) • [Scripted GUI](<scripted_gui_modding.md>) • [Technologies and doctrines](<technology_modding.md>) • [Units](<unit_modding.md>)
- **Map**: [Map](<map_modding.md>) • [States](<state_modding.md>) • [Supply areas](<supply_areas_modding.md>) • [Strategic regions](<strategic_region_modding.md>)
- **Graphical**: [Interface](<interface_modding.md>) • [Graphical assets](<graphical_asset_modding.md>) • [Entities](<entity_modding.md>) • [Posteffects](<posteffect_modding.md>) • [Particles](<particle_modding.md>) • [Fonts](<font_modding.md>)
- **Cosmetic**: [Portraits](<portrait_modding.md>) • [Namelists](<namelist_modding.md>) • [Music](<music_modding.md>) • [Sound](<sound_modding.md>)
- **Other**: [Console commands](<console_commands.md>) • [Mod structure](<mod_structure.md>) • [Mods](<mods.md>) • [Nudger](<nudger.md>)
- **Kit pages (not on the wiki)**: [Collection modding](<collection_modding.md>) • [Defines additions](<defines_additions.md>) • [Game rule modding](<game_rule_modding.md>) • [Intelligence operation modding](<intelligence_operation_modding.md>) • [Map mode modding](<map_mode_modding.md>) • [Occupation and resistance modding](<occupation_and_resistance_modding.md>) • [Peace conference modding](<peace_conference_modding.md>) • [Raid modding](<raid_modding.md>) • [Script constant modding](<script_constant_modding.md>) • [Special project modding](<special_project_modding.md>)
