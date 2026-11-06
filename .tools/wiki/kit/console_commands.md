# Console commands

<!-- kit:begin id="review" build="1.19.4.1" checked="2026-11-01" revision="105778" sources="documentation/console_commands_documentation.md localisation/ignored_loc_keys.txt launcher-settings.json documentation/triggers_documentation.md documentation/effects_documentation.md" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Checked against: `documentation/console_commands_documentation.md` (386 commands and 44 tweakable variables), `localisation/ignored_loc_keys.txt`, `launcher-settings.json`, and a string search of `hoi4.exe` for commands the documentation does not list.
Kit blocks added: an intro and a glossary, three correction blocks (rows that differ from the documentation, commands that are gone or undocumented, and the "no longer exists" and "unknown what" notes), a table of the commands that matter most for modding (`loc_check` family, `debug_checkportraitssanity`, reload commands, `event`, `effect`, `eval_effect`, `trigger`, `error`, `list_*`), eight tables for the 180 documented commands the page never named, and the 33 tweakable variables it never named.
Gaps left: the documentation gives one line per command, so what `loc_check` counts as a bad key is [unverified]. Commands were not run in the game before 2026-11-02. Since then only the statements tagged `[game-tested 1.19.4.1]` have been run.
**1.19.4.1 re-check (2026-11-01).** The documentation index diff shows one change: `debug_types` is gone, so the file now lists 385 commands (70 of them not in release builds) and the same 44 tweakable variables, and `hoi4.exe` 1.19.4.1 no longer contains the string. The correction block at the end of the page now lists it as removed, and the build named in the [docs] blocks is 1.19.4.1. The two other statements that cite changed files were re-measured: the debug launch arguments in `launcher-settings.json` and the `FUNDS_FOR_SIZE_UP` default of 700. Every other statement cites files that are byte-identical in 1.19.4.1 (Steam depot manifest diff).
<!-- kit:end id="review" -->

<!-- kit:begin id="cc-intro" at="section:list-of-commands" -->
What the installed documentation covers. `documentation/console_commands_documentation.md` lists 385 console commands and 44 tweakable variables. 70 of the commands and 30 of the variables carry the label "Not available in release build". [docs] 1.19.4.1 removed `debug_types`, which 1.19.3 listed as not available in release builds. [docs]

- Rows below marked "Not in release build" are those labelled commands. Do not rely on them in the shipped game; 32 of them are rows already on this page (listed in the correction block at the end of the page). [docs]
- A tweakable variable is a switch you type by name. A Boolean one toggles when typed alone, turns on with a non-zero number after it, and off with `0` (`Agency.AutoComplete 1`). All 44 variables in 1.19.4.1 are Boolean. [docs]
- `help` prints all commands or one description, `helplog` writes the whole command list to `game.log`, and `trigger_docs` (aliases `effect_docs`, `scripting_docs`, `docs`) prints the trigger, effect and variable documentation. [docs]
- Debug launch: the Paradox launcher entry "Open game in Debug Mode" starts `hoi4.exe` with `-gdpr-compliant -debug_mode` (`launcher-settings.json`). [vanilla-confirmed 1.19.4.1] The `is_debug` trigger documentation names the argument `-debug`. [docs] The two are not the same: with `-debug` the main menu version string ended "(D) (S)" and `is_debug` was TRUE, while with `-debug_mode` alone, or with no arguments, the string ended "(S)" and `is_debug` was FALSE. The console worked in all three. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, `hoi4.exe` started directly with each argument set. The Steam launch option route through the Paradox launcher was not tested.
- `Focus.NoChecks`, `Decision.NoChecks`, `Operation.Instant` and the other dotted names in the variable list are tweakable variables, not commands, so they are typed alone to toggle. `Agency.Instant` is the exception: it is a command that switches on four other switches. [docs]
<!-- kit:end id="cc-intro" -->

<!-- kit:begin id="cc-glossary" at="section:glossary" -->
Terms used on this page and in the console documentation. All rows: [docs] `documentation/console_commands_documentation.md` unless another file is named.

| Term | Meaning |
| --- | --- |
| Alias | A second name for the same command. The documentation lists them per command and either name works. |
| Selected scope | Many commands act on what is currently selected: `effect`, `eval_effect`, `trigger`, `eval_trigger` run in the selected scope, and `list_flags`, `list_vars` and `list_modifiers` read the selected country, state or unit leader. |
| Tweakable variable | A named on/off switch (all Boolean in 1.19.4.1) that is toggled by typing its name. |
| Release build | The shipped game. Commands labelled "Not available in release build" are missing from it. |
| Debug mode | The game started with the debug launch option. The `debug` command toggles it on and off. |
| MIO | Military industrial organisation (`AddFunds`, `AddSize`, `AddTaskCapacity`). |
| OOB | Order of battle (`reloadoob`). |
| BoP | Balance of power; the documentation calls it a "power balance" (`bop_add`, `bop_set` and the other `bop_` commands). |
| FI | Faction initiative (`faction_initiative`, alias `fi`). |
| PP, CP | Political power (`pp`) and command power (`cp`). |
| Loc | Localisation. `loc_check` and its variants look for missing localisation keys. |
| Intel pool | A stored intel value one country has on another (`add_intel`, `clear_intel_pools`). |
<!-- kit:end id="cc-glossary" -->

<!-- kit:begin id="cc-fix-useful" at="section:useful-commands" -->
Rows in the table above that differ from the 1.19.4.1 documentation. All rows: [docs] `documentation/console_commands_documentation.md`, except where a cell says [unverified].

| Page row | What 1.19.4.1 documents |
| --- | --- |
| `acclimization` | The command is spelled `acclimatization`, alias `acc`, arguments `<climate_name>, <value 0-100>`. The spelling `acclimization` appears nowhere in the documentation. [docs] hoi4.exe has no such string either (executable string). The console rejects the page's spelling with "Unknown command" in red. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, console reply. See the notes below the table. |
| `add_core <state_id>` | Takes a `<Province ID>`, not a state id. |
| `remove_core [<State ID>] [<Country Tag>]` | Takes a single `<Province ID>`. The documentation lists the command and does not say it is broken. [docs] `remove_core 375` (a province id of state 64), `remove_core 64 GER` and `remove_core 64` each printed only the command in red, and state 64 was still a GER core after each, so none of the three removed the core. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, console reply. |
| `puppet [<Puppeteer>] [<Target>]` | One argument, `<Target Country Tag>`. The two-tag form is not documented. [docs] The engine accepts it: `puppet GER CZE` made CZE a GER puppet. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, console reply. |
| `teleport(tp)` | Takes `<province_id>` and teleports the selected armies or ships there. |
| `setowner [<country tag>]` | The argument list is `country tag, state id`. The page's claim that a state id no longer works is not in the documentation. [docs] A state id works: `setowner FRA 64` printed "France now owns State Brandenburg". `setowner 64` printed "Specify a tag and a state id or specify a tag select a state". [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, console reply. |
| `annex [<tag>] or "all"` | One `<Target Country Tag>` is documented. The `all` form is not. [docs] `annex all` runs: the game had 89 countries before it and 2 after. `annex HUN` removed HUN. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, console reply. |
| `debug_crash(crash)` | Labelled "Not available in release build". |
| `tdebug` (first row, "Toggles Debug info") | `tdebug` is the alias of `provtooltipdebug`, which toggles the debug info in the province tooltip (the page lists that command again further down). The command that toggles generic Debug info is `debug_info`, and it is not in release builds. |
| `pp(fuhrer_mana,political_power)` | Only `political_power` is a documented alias. `fuhrer_mana` is not in the documentation. [docs] It is not in hoi4.exe either (executable string). `fuhrer_mana 10` printed "Unknown command" in red, and `political_power 10` printed "Granted 10 political power to German Reich". [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, console reply. |
| `FI [amount}` | The command is `faction_initiative`, alias `fi`, arguments `amount, countrytag` (tag optional, default the player). |
| `st`, `ws` | Aliases of `add_stability` and `add_war_support`. Both document the argument as "unity amount". |
| `nuke [number]` | Alias of `nukes`, argument `<count>`. |
| `fuel [<amount>]` | Also has the alias `army_juice`. `fuel_gain` changes the daily fuel gain instead. |
| `add_ideas`, `remove_ideas` | Accept `all` or several idea ids separated by spaces. |
| `add_mines` | Alias `mines`, argument `<Amount of naval mines>`, applied to the selected region(s). The page's "maximises" is not stated. [docs] The command adds the given amount, and the default amount is 1000. With the North Sea selected, `add_mines 10` replied "Added 10 naval mines to the selected region(s).", `add_mines 1000000` replied "Added 1000000 naval mines ..." and `add_mines` with no argument replied "Added 1000 naval mines ...". The region panel's "Our mine presence in the region" read 0% until the next hour tick and then 100%. The value after 10 mines alone was not read, because the three commands ran before the tick, so whether a small amount raises the presence only a part of the way is untested. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, console reply and the region panel, screenshots. |
| `add_autonomy` | Listed with no description and no arguments. |
| `set_country_flag` | The documentation says it sets the flag on a given tag for a duration and defaults to the current country, value 1 and no expiry, but its argument list shows only the flag name. The page's note that another tag does not work is not in the documentation. [docs] Another tag does not work in the game. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, console reply. See the notes below the table. |
| `Focus.AutoComplete (fa)` | `fa` is documented as its own Boolean tweakable variable next to `Focus.AutoComplete`. |
| `addfunds` ("adds 1000 funds") | The command is `AddFunds` with aliases `mio.AddFunds` and `IndustrialOrganisation.AddFunds`. The first argument is an optional MIO token, the second an optional amount. With no amount it adds `NDefines::NIndustrialOrganisation::FUNDS_FOR_SIZE_UP`, which is 700 in 1.19.4.1 (`common/defines/00_defines.lua`, [vanilla-confirmed 1.19.4.1]), not 1000. |
| `addTaskCapacity`, `addSize` | Real names `AddTaskCapacity` and `AddSize`, with the same `mio.` and `IndustrialOrganisation.` aliases. A negative task capacity is allowed but the result is capped at 0. |
| `add_cic_bank` | Also has the aliases `stonks`, `cic` and `bank`. A negative value subtracts. |
| `force_operative_detection` | Alias `snitch`. The documentation text is a copy of `print_intel_network`'s, so its description is unreliable. |
| `list_hidden_focuses` | Alias `list_hd`; the argument is a country tag. |
| `release` | Alias `rls`. |

Notes on rows of the table above:

- `acclimization`: the documented `acclimatization arctic 50` is accepted and answered "Unknown climate definition: arctic. Valid options are: cold_climate, hot_climate". [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, console reply.
- `set_country_flag`: `set_country_flag b1_flag_b POL` printed "set to 1 for Poland", but the flag landed on the player's country (GER) and `list_flags POL` answered "No flags set". `set_country_flag b1_flag_c 5` printed "set to 5", which shows the number as the flag value. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, console reply. Whether a number also acts as a duration is untested. [unverified]
<!-- kit:end id="cc-fix-useful" -->

<!-- kit:begin id="cc-fix-modding" at="section:modding-useful-commands" -->
Rows in the table above that differ from the 1.19.4.1 documentation. All rows: [docs] `documentation/console_commands_documentation.md`, except where a cell says [unverified].

| Page row | What 1.19.4.1 documents |
| --- | --- |
| `reload [<type>]` | There is no `reload` entry in the documentation. [docs] The page's examples work all the same: ten targets each printed "<name> reloaded!", and bare `reload` printed "Please specify the file name:target". [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, console reply. The targets run and the documented reload commands are in the notes below the table. |
| `effect (e) [<scripted_effect_name>]` | Arguments are `<tag> scripted_effect_name`. It runs a scripted effect on the selected scope. Inline effect code goes through `eval_effect`. |
| `trigger [<scripted_trigger_name>]` | Alias `t`, arguments `<tag> scripted_trigger_name`. It runs a scripted trigger on the selected scope. Inline trigger code goes through `eval_trigger`. |
| `event [<event id>] [Target country tag]` | The documented arguments are `event id, <Target Country Tag>`. |
| `error` | Documented as "Show errors in log". Whether it opens a file is not stated. [docs] Run in the console, it printed nothing back and wrote only a header line, `======== show errors from console ========`, plus about 11 blank lines to `error.log`. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, console and error.log read. The user folder was not listed before and after, so a separate file is not ruled out. |
| `set_var`, `get_var` | The documentation lists only `<var name>` for both. The page's `[<value>]` for `set_var` is not documented. [docs] `set_var` takes a value: after `set_var b1_v 5`, `get_var b1_v` printed "b1_v = Ermland-Masuren (5)", the value 5 shown with the name of the state that has id 5. `set_var b1_w` with no value printed "Incorrect number of arguments". [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, console reply. |
| `list_flags`, `list_vars` | Optional `<scope>` argument. They list the flags or variables of that scope, or of the selected country, state or unit leader. |
| `trigger_docs` | Aliases `effect_docs`, `scripting_docs`, `docs`. Documented as printing the trigger, effect and variable docs; where it prints is not stated. [docs] Run in the console, it replied that the documentation was printed to the game log, and `game.log` then held a `== TRIGGER DOCUMENTATION ==` section of about 11,700 lines. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, console reply and game.log read. The console reply was read by OCR. |
| `human_ai` | Documented as "Toggles AI for Human countries". |
| `ai [country tag...]` | Documented only as "Toggles the AI on or off". `enable_ai` and `disable_ai` are separate commands. |

Notes on rows of the table above:

- `reload` targets that printed "<name> reloaded!": `loc`, `focus`, `defines`, `decision`, `landcombat.gui`, `ideas`, `ability`, `scriptedgui`, `scripted_effects` and `cfocus`. `reload ideas` also wrote 239 parse errors for vanilla idea files to error.log. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, console reply and error.log read.
- `reload`: The documented reload commands are `reloadoob`, `reloadinterface`, `reloadtechnologies`, `reload_textures` (aliases `rt`, `reload_texture`), `reloadfx`, `reloadweather`, `cityreload`, `rebuildlayers`, `update_loc`, `updateequipments` and `updatesubunits`. [docs] hoi4.exe contains the string `reload %s` and the messages `' reloaded!`, `No such reload target that takes arguments: '`, `Please specify the file name/target` and `defines reloaded!` (executable strings).
<!-- kit:end id="cc-fix-modding" -->

<!-- kit:begin id="cc-modding-highlights" at="section:modding-useful-commands" -->
#### Commands that matter most when modding

Every command here exists in 1.19.4.1 under exactly this name, and none is labelled "Not available in release build". All rows: [docs] `documentation/console_commands_documentation.md`, the 39 names in the first column checked one by one, except the one cell marked as not verified.

| Command | Aliases | Arguments (as documented) | Use |
| --- | --- | --- | --- |
| `loc_check` |  |  | Checks the localisation the game knows about for missing keys. Per-kind variants are in the next row. The exclusion list is `localisation/ignored_loc_keys.txt` (see the note below the table). |
| `loc_check_characters`, `loc_check_decisions`, `loc_check_events`, `loc_check_focuses`, `loc_check_modifiers`, `loc_check_national_spirits` | | | The same check restricted to one kind of content. These six are the only variants in 1.19.4.1. |
| `debug_checkportraitssanity` |  |  | Checks the portraits of all characters and writes failures to the error log. Run it after adding characters or portrait sprites, then read `error.log`. |
| `error` |  |  | Shows errors from the log. |
| `event` |  | `event id, <Target Country Tag>` | Fires an event for the target country. |
| `testevent` |  | `<Event ID>, <Character ID>` | Tests an event without firing it; the second argument is a character id. |
| `effect` | `e` | `<tag> scripted_effect_name` | Runs a named scripted effect (from `common/scripted_effects`) on the selected scope. Note the leading tag argument. |
| `eval_effect` |  |  | Runs effect code typed after the command on the selected scope. |
| `trigger` | `t` | `<tag> scripted_trigger_name` | Evaluates a named scripted trigger on the selected scope. |
| `eval_trigger` |  |  | Evaluates trigger code typed after the command on the selected scope. |
| `list_flags` |  | `<scope>` | Lists the flags of a scope, or of the selected country, state or unit leader. |
| `list_vars` |  | `<scope>` | Lists the variables of a scope, or of the selected country, state or unit leader. |
| `list_modifiers` |  | `<scope>` | Lists the modifiers of a scope, or of the selected country, state or unit leader. |
| `list_ideas` |  |  | Dumps all ideas to the console (ministers and national spirits). |
| `list_leader_modifiers` |  |  | Lists the leader and unit modifiers on the leader of each selected army. |
| `get_flag`, `set_flag`, `get_country_flag` | | `<flag name>` | Read or write a flag; `get_country_flag` defaults to the current country. The page already lists `set_country_flag` and `set_global_flag`. |
| `reloadoob` |  | `<Target Country Tag>` | Reloads the orders of battle of a country. |
| `reloadinterface` |  |  | Reloads the whole interface (GUI files). |
| `reloadtechnologies` |  |  | Reloads the technology database. |
| `updateequipments`, `updatesubunits` | | | Update the equipment database and the sub-unit database. |
| `update_loc` |  | `localization tag` | Updates the localisation file for one localisation tag. |
| `reload_textures` | `rt`, `reload_texture` | `<optional file name filters...>` | Reloads all textures, or only files whose name contains the given text. |
| `reloadfx` |  | `map/mapname/postfx or *.fx filename` | Reloads shaders. hoi4.exe also prints `all` in its usage message (executable string). `reloadfx all` is accepted and printed "all reloaded!". `reloadfx postfx` printed "Map reloaded". [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, console reply. |
| `instantevents` |  |  | Ignores event MTTH values. |
| `easy_decisions` | `ezd` |  | Toggle: decisions with `days_remove` last 1 day, and decisions lose their cost and cost trigger. |
| `dump_equipment_loc` | | `desc`, country tags, equipment types, `path=<filepath>` (all optional) | Writes equipment localisation strings to a CSV, by default `logs/equipment_loc.csv`. `desc` dumps descriptions instead of names; type words such as `armor anti_tank` narrow the list. |
| `log_advisor_trait_errors` |  |  | Logs every unit-leader advisor that lacks the matching unit-leader trait. |
| `focus_count` |  | `<Target Country Tag>` | Counts the focuses a tag has. |
| `history_logger` |  |  | Toggles the history logger (the `log` effect can write to it; see [Troubleshooting](troubleshooting.md#log-files)). |
| `trigger_docs`, `helplog` | `effect_docs`, `scripting_docs`, `docs` (for `trigger_docs`) | | Print the trigger, effect and variable documentation; write the command list to `game.log`. |

`localisation/ignored_loc_keys.txt` is the exclusion list for the `loc_check` commands: its first line says keys added to it are ignored by the `loc_check*` commands, and the installed file holds 11 placeholder keys (`test.1.a`, `test_state.1.d` and similar). [vanilla-confirmed 1.19.3] hoi4.exe contains that path and the result lines `No missing or bad loc keys found`, `missing loc keys found`, `bad loc keys found` and `, check error log` (executable strings). The details are in the error log: `loc_check_events` and `loc_check` printed only a count in the console ("122 missing loc keys found and 3 bad loc keys found in events, check error log" and "8060 missing loc keys found and 532 bad loc keys found, check error log"), and `error.log` then held the lists under "Missing loc keys found in events:" and "Missing loc keys found:", each key printed as `key: "TODO"`. A key that exists in a mod loc file was not listed. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, console (OCR) and error.log read. The mod's own `localisation/ignored_loc_keys.txt` was not tested.

Duplicate localisation keys are not a console check. The game reports them at start-up in `text.log`; see [Log files](troubleshooting.md#log-files). Two files of one mod that define the same key each got a line there with the key, the file and the value ("Duplicate localization found, key: ..."), and the key was not in `error.log`. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, text.log read. The main menu message for a collision is UI and was not observed.
<!-- kit:end id="cc-modding-highlights" -->

<!-- kit:begin id="cc-fix-other" at="section:other-in-game-commands" -->
Rows in the tables above that the 1.19.4.1 documentation does not support. Sources: [docs] `documentation/console_commands_documentation.md`; where a cell says [unverified], the evidence is a string search in `hoi4.exe`.

| Page row | Status in 1.19.4.1 |
| --- | --- |
| `winwars`, `debug_nuking` | Absent from the documentation. [docs] No such string is in hoi4.exe either (executable string). The console rejects them: both printed "Unknown command" in red, followed by the command. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, console reply. That agrees with the page's "no longer exists" notes (1.9.1 and 1.15.1). The documented replacement for nuking is `launch_nuke` (alias `ln`): it launches a nuke at given provinces without checking conditions. |
| `nextsong`, `poll`, `reloadsupply (relsup)`, `add_interest`, `remove_interest`, `requestgamestate`, `debug_commands`, `debug_volume`, `debug_ai_budget`, `profilelog`, `filewatcher`, `browser_base_url` | Not in the documentation, under any name or alias. [docs] No matching command string is in hoi4.exe either. All of them, including the alias `relsup`, printed "Unknown command" in red, like the nonsense word `zzzz`. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, console reply. Treat them as removed. See the note below the table. |
| `normals` | Not documented. The only mention of the word is in the description of `collision` ("Toggles debug display of normals/bounding boxes/collision"). [docs] `normals` is still a command: it printed "Command available only for developers." [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, console reply. |
| `rendertype`, `tweakergui`, `particle_editor` | Not documented. [docs] hoi4.exe contains the strings `rendertype`, `tweakergui` and `particle_editor save/restart/undo/redo/exit` (executable strings). All three are console commands in the game. `rendertype` printed "DirectX 11.1", `particle_editor` printed "Load a particle effect before running the editor", and `tweakergui` printed "You need to provide at least one tweakable variable!". [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, console reply. |
| `ShowTechBonus` ("unknown what it does") | A Boolean tweakable variable, labelled "Not available in release build", with no description in the documentation. |
| `night`, `massconquer`, `aircombat`, `debug_achievements_clear`, `gbreload`, `oos`, `toggle_silhouette_portraits` | The page calls these developer-only or not working. The documentation confirms it: all are labelled "Not available in release build". |
| `remove_core` ("Command does not work") | Documented with a `<Province ID>` argument. Whether it works is not stated. [docs] It did not work in the test: `remove_core 375`, `remove_core 64 GER` and `remove_core 64` each printed only the command in red, and state 64 stayed a GER core after each. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, console reply. |
| `debug_types` | Removed in 1.19.4.1. 1.19.3 documented it as not available in release builds; the 1.19.4.1 documentation no longer lists it and hoi4.exe 1.19.4.1 contains no `debug_types` string. [docs] |

Notes on rows of the table above:

- `filewatcher` and `requestgamestate`: hoi4.exe has only a `nofilewatcher` launch argument and game-state command class names, not a `filewatcher` or `requestgamestate` console string.

The page rows that the documentation labels "Not available in release build" are: `debug_crash`, `ShowTechBonus`, `massconquer`, `aircombat`, `ai_front_dump`, `debug_diploactions`, `debug_dumpdiploactions`, `debug_assert`, `debug_fronts`, `debug_off_front_snap`, `debug_lines`, `debug_entities`, `debug_info`, `debug_particle`, `debug_textures`, `debug_texture`, `debug_wireframe`, `debug_achievements_clear`, `debug_air_vs_land`, `gbreload`, `gbpaint`, `oos`, `hdr`, `hdr_debug`, `srgb`, `bloom`, `PostEffectVolumes.Default`, `night`, `createlean`, `hsv`, `browser`, `toggle_silhouette_portraits`. Do not expect them to work in the shipped game. [docs]
<!-- kit:end id="cc-fix-other" -->

<!-- kit:begin id="cc-economy" at="section:other-in-game-commands" -->
#### Economy, research and the international market

All rows: [docs] `documentation/console_commands_documentation.md`. No row in this block quotes hoi4.exe. Commands not on the wiki page.

| Command | Aliases | Arguments (as documented) | What it does |
| --- | --- | --- | --- |
| `add_stability` | `st` | `unity amount` | Adds or removes stability for the player. The page already lists its alias `st`. |
| `add_exile_manpower` |  | `<TAG>, <value>` | The name points at exile manpower, but the docs text is copied from `add_legitimacy`, so the real effect is not documented. |
| `fuel_gain` |  | `Daily Fuel amount` | Adds or removes daily fuel income for the player. |
| `empty_fuel_tanks` |  | `Fuel amount` | Empties the fuel tanks of all armies; the docs list a fuel amount argument. |
| `research_fast` |  |  | Sets the base cost of every technology to 1 research point. |
| `add_tech` |  |  | Listed with no description and no arguments. |
| `clear_tech` |  |  | Listed with no description and no arguments. |
| `add_subsidies` |  |  | Listed with no description and no arguments. |
| `add_subsidies_second` |  |  | Listed with no description and no arguments. |
| `InternationalMarket.AddSubsidyForTrigger` |  | `<CIC>, <Archetype>, <ScriptedTrigger>` | Like `InternationalMarket.AddSubsidyForTags` (on the page), but the sellers are chosen by a scripted trigger instead of a tag. |
| `InternationalMarket.CancelPurchase` |  | `<SellerTag>, <BuyerTag>, <ContractIndex>` | Cancels the purchase contract between a seller and a buyer. |
| `InternationalMarket.Dev.SetMarketRequestAutomation` |  | `<AcceptMarketAccess>, <SendMarketAccess>, <AcceptPurchase>` | Sets how market requests are automated (accept market access, send market access, accept purchase). |
| `InternationalMarket.ReleaseFromMarketStockpile` |  | `<EquipmentName>, <EquipmentAmount>` | Moves equipment from the market stockpile back to the main stockpile. |
| `InternationalMarket.RequestPurchase` |  | `<SellerTag>, <BuyerTag>, <PaidCivs>, <EquipmentName>, <EquipmentAmount>` | Requests an equipment purchase; the arguments are seller tag, buyer tag, PaidCivs, equipment name and amount. |
| `InternationalMarket.ReserveToMarketStockpile` |  | `<EquipmentName>, <EquipmentAmount>` | Moves equipment from the main stockpile into the market stockpile. |
| `InternationalMarket.SetPriceLevel` |  | `<EquipmentName>, <Level>` | Sets the price level of one equipment type in the market stockpile. |
<!-- kit:end id="cc-economy" -->

<!-- kit:begin id="cc-politics" at="section:other-in-game-commands" -->
#### Politics, diplomacy, factions and balance of power

All rows: [docs] `documentation/console_commands_documentation.md`. No row in this block quotes hoi4.exe. Commands not on the wiki page.

| Command | Aliases | Arguments (as documented) | What it does |
| --- | --- | --- | --- |
| `no_wargoal` |  |  | Lets the player declare war without a wargoal. |
| `allowoperations` |  |  | Allows every operation to be executed. |
| `drop_cosmetic_tag` |  | `<country tag>` | Removes the cosmetic tag of a country (the page lists `set_cosmetic_tag`, the opposite). |
| `retire_country_leader` |  |  | Listed with no description and no arguments. |
| `bop_add` |  | `<ID>, <value>` | Changes the value of a balance of power by the given amount. |
| `bop_addmod` |  | `<ID>, <ModID>` | Adds a static modifier to a balance of power. |
| `bop_remove` |  | `<ID>` | Deactivates a balance of power for the current country. |
| `bop_rmmod` |  | `<ID>, <ModID>` | Removes a static modifier from a balance of power. |
| `bop_set` |  | `<ID>` | Activates a balance of power for the current country. |
| `bop_show` |  |  | Shows the balances of power active for the current country. |
| `faction_goal_slot` | `fgs` | `category, amount` | Adds a faction goal slot; the category is `short`, `medium` or `long`. |
| `faction_influence` | `finf` | `amount, countrytag` | Adds stored faction influence to a country; without a tag it uses the player country. |
| `faction_initiative` | `fi` | `amount, countrytag` | Adds faction initiative to a country; without a tag it uses the player country. The page lists it as `FI`. |
| `faction_unlock` | `fu` | `type` | Unlocks a part of the faction: military (`m`) or research (`r`). |
| `debug_force_capitulate` | `dfc` | `<tag>` | Forces a country to capitulate on the next daily tick. |
| `prep_for_war` |  | `<TAG>` | Makes an AI country prepare for a fight with another country (the docs text is vague about which one). |
| `collaboration` |  |  | Adds collaboration against the selected country; the docs example is a right-click selection followed by `collaboration 0.3`. |
| `capture_commander` |  | `<owner_tag>, <leader>` | Captures an enemy commander for the player country; the docs say a province id is needed if the commander is not deployed. |
| `get_capital` |  | `<Country tag>` | Looks up the capital of a country. |
| `war_relations` |  | `<tag>` | Prints war relation information for a tag. |
<!-- kit:end id="cc-politics" -->

<!-- kit:begin id="cc-projects" at="section:other-in-game-commands" -->
#### Special projects, medals and achievements

All rows: [docs] `documentation/console_commands_documentation.md`. No row in this block quotes hoi4.exe. Commands not on the wiki page.

| Command | Aliases | Arguments (as documented) | What it does |
| --- | --- | --- | --- |
| `sp_add_selected_scientist_level` |  | `<Level>, <Specialization> (optional)` | Adds levels to the selected scientist, optionally for one specialisation only. Needs the facility view with an attached scientist open. |
| `sp_remove_selected_scientist_trait` |  |  | Removes a trait from the selected scientist. Needs the facility view with an attached scientist open. |
| `show_all_medals` |  | `<bronze\|silver\|gold>` | Shows every medal as achieved in the medal grid without earning it; the tier is `bronze`, `silver` or `gold`. |
| `show_all_ribbons` |  |  | Shows every ribbon as achieved in the grid without earning it. |
| `show_medal` |  | `<medal_token>, <bronze\|silver\|gold>` | Shows the award popup for a medal without earning it. |
| `show_ribbon` |  | `<ribbon_token>` | Shows the award popup for a ribbon without earning it. |
| `forget_medals_and_ribbons` |  |  | Makes the game forget the medals and ribbons you earned. Not in release build. |
| `debug_achievements` |  |  | Turns on achievement popups so achievements can be debugged. Not in release build. |
| `debug_custom_achievements` |  |  | For testing custom achievements: clears their completion state (cloud storage files) and reloads the mod achievement files. |
<!-- kit:end id="cc-projects" -->

<!-- kit:begin id="cc-intel" at="section:other-in-game-commands" -->
#### Intelligence, operations and raids

All rows: [docs] `documentation/console_commands_documentation.md`. No row in this block quotes hoi4.exe. Commands not on the wiki page.

| Command | Aliases | Arguments (as documented) | What it does |
| --- | --- | --- | --- |
| `operation_debug` |  | `Operation ID, Target Tag` | Takes an operation id and a target tag. The docs text is copied from `allowoperations`. |
| `operation_start` |  | `Operation ID, Target Tag` | Starts an operation against a target tag. The docs text is copied from `allowoperations`. |
| `operation_test_phase_selection` |  | `Operation ID, Target Tag` | Tests the phase selection of an operation against a target tag. |
| `print_operation_tokens` |  |  | Prints operation tokens. The docs text is copied from `effect`, so treat the description as unreliable. |
| `emulate_ai_operative_assignment` |  |  | Logs what the operative AI would assign this tick. The first argument is the tag to test; the default is the player. |
| `grow_intel_network` |  |  | Grows the intel network against the specified tag. |
| `clear_intel_pools` |  |  | Resets the specified intel pool. |
| `add_fake_armies` |  |  | Creates fake intel armies for the player. |
| `print_intel_network` |  |  | Prints intel network information. |
| `print_intel_values` |  |  | Prints how much intel one country has on another. |
| `print_radar_intel` |  |  | Prints the intel value breakdown that radar generates. |
| `lock_air_det` |  | `<CountryTag>, <Detection> (0.0-1.0) OPTIONAL` | Locks a country's air detection at a value from 0.0 to 1.0; leave the value out to reset it. |
| `lock_air_eff` |  | `<CountryTag>, <Efficiency> (0.0-1.0) OPTIONAL` | Locks a country's air efficiency at a value from 0.0 to 1.0; leave the value out to reset it. |
| `prepareraids` |  | `<[Optional] the degree to which the raid should be prepared (0.0-1.0)>` | Completes the preparation of all active raids at once, or to a given progress from 0.0 to 1.0. Not in release build. |
| `endraids` |  | `<Success Level: 1-4 OR { failure, limitedsuccess, success, criticalsuccess}>` | Ends all active raids at once; the optional argument is the success level (1 to 4, or `failure`, `limitedsuccess`, `success`, `criticalsuccess`). Not in release build. |
<!-- kit:end id="cc-intel" -->

<!-- kit:begin id="cc-military" at="section:other-in-game-commands" -->
#### Units, combat and fronts

All rows: [docs] `documentation/console_commands_documentation.md`. No row in this block quotes hoi4.exe. Commands not on the wiki page.

| Command | Aliases | Arguments (as documented) | What it does |
| --- | --- | --- | --- |
| `acclimatization` | `acc` | `<climate_name>, <value 0-100>` | Sets the acclimatisation of the selected division(s) for one climate. The page spells this `acclimization`. |
| `add_critical_hit` |  | `<critical_hit_name>` | Adds a named critical hit to the selected ships. |
| `clear_critical_hits` |  |  | Clears all critical hits. |
| `bypass_invasion_superiority_check` | `bisc` |  | Ignores the naval superiority check in the strategic regions an invasion order crosses. |
| `createarmygroup` |  |  | Creates a field marshal group from the selected groups. |
| `damage_units` |  | `<org>, <str>, <num>` | Damages or heals the selected units, or the unit under the pointer if none is selected. One argument applies to both stats, two set them separately. |
| `combat_analyzer` |  | `<TAG1>, <TAG2>, <OOB1>, <OOB2>, <num runs> OPTIONAL, <num days> OPTIONAL` | Runs a combat between two orders of battle owned by two tags, until it ends or for a number of days, optionally several times with averaged results. |
| `combattest` |  |  | Runs a combat simulation process. Not in release build. |
| `deleteallairwings` | `delallair` |  | Deletes all air wings. |
| `instantshiprefit` | `isr` |  | Toggles instant ship refitting. |
| `launch_nuke` | `ln` | `[Nuke Type], <Province ID>, ...` | Launches a nuke at the given province(s) without checking any conditions; the nuke type is optional. |
| `nukes` | `nuke` | `<count>` | Adds nukes. The page lists the alias `nuke`. |
| `spawn` |  | `<SubUnit Type>, <Province ID>, <Amount>` | Spawns a number of sub-units of a type in a province. Not in release build. |
| `spawn_3D_models` |  |  | Listed with no description and no arguments. |
| `unit_address` |  |  | Prints the memory address of the first selected unit. |
| `unit_stats` |  |  | Lists the stats of the selected units. |
| `show_xp_gain` | `xp_gain` |  | Shows experience gain information. |
| `trigger_ability` |  | `<ability_name>` | Triggers a named ability. |
| `railwaygun` | `rg` |  | Creates a railway gun in the supply capital. Not in release build. |
| `railwaygun_damage` | `rg_damage` |  | Damages railway guns. Not in release build. |
| `theatersrebuild` | `trebuild` |  | Rebuilds all theatres in the world and clears all orders. Not in release build. |
| `rebuildfronts` |  | `<Country tag>` | Rebuilds the fronts of a country. Not in release build. |
| `build_war_blobs` |  |  | Prints a list of all your wars. |
| `dbg_task_force_role_insignia_assignment` | `tfria` |  | Prints the role the game would assign to the selected task force. |
| `dbg_tf_fulfillment` |  |  | Shows the managed fulfilment of a task force (the number of ships expected after all ships have merged in). |
| `set_debug_unit_controller` | `dbg_unit_controller` |  | Sets the debug unit controller tag; other countries stop updating their units. Not in release build. |
| `debug_unit_controller_weights` | `dbg_ucw` | `<weight token>` | Visualises unit controller weights. Run `track_unit_controller_weights` first. |
| `track_unit_controller_weights` | `track_ucw` |  | Starts tracking unit controller weights for the current country, to be viewed with `debug_unit_controller_weights`. |
| `navalcombatlog` |  |  | Logs naval combat. Not in release build. |
| `test_naval_move_danger` |  | `<from region id>, <to region id>` | Tests whether the path between two regions is blocked for surface warships. Not in release build. |
| `debug_army_entity` | `dae` |  | Shows the debug entity for all armies. |
| `debug_unit_entity` | `dbg_ue` |  | Prints the entity hierarchy. |
| `debug_front_sections` | `dbg_fs` | `<Theatre index>, <Front index>, <Section index>` | Visual debug of theatres, fronts and front sections. |
| `debug_orders_tree` | `dot` |  | Prints debug information about an order chain. Not in release build. |
| `highlight_encirclements` |  |  | Toggles highlighting of detected encirclements. |
<!-- kit:end id="cc-military" -->

<!-- kit:begin id="cc-ai" at="section:other-in-game-commands" -->
#### AI and pathfinding debugging

All rows: [docs] `documentation/console_commands_documentation.md`. No row in this block quotes hoi4.exe. Commands not on the wiki page.

| Command | Aliases | Arguments (as documented) | What it does |
| --- | --- | --- | --- |
| `enable_ai` |  |  | Enables the AI. |
| `disable_ai` |  |  | Disables the AI. |
| `ai_dump` | `aidump` |  | Dumps AI data to a log file. Not in release build. |
| `ai_research_log` |  |  | Toggles AI research logging. Not in release build. |
| `ai_trace` |  |  | Toggles the AI Trace window. Not in release build. |
| `toggle_offset_ai_daily_update` |  |  | Toggles whether a country's AI daily update is spread over the day. Not in release build. |
| `pathfind_cache` |  | `on / off` | Enables or disables the pathfinding cache. Not in release build. |
| `pathfind_stats` |  |  | Prints pathfinding cache statistics. Not in release build. |
<!-- kit:end id="cc-ai" -->

<!-- kit:begin id="cc-map-view" at="section:other-in-game-commands" -->
#### Map, weather and display

All rows: [docs] `documentation/console_commands_documentation.md`. Only the `set_weather` cell quotes hoi4.exe, and a game run checked it. Commands not on the wiki page.

| Command | Aliases | Arguments (as documented) | What it does |
| --- | --- | --- | --- |
| `add_rain` |  | `<rain_amount>` | Adds rain to the selected province. |
| `add_snow` |  | `<snow_amount>` | Adds snow to the selected province. |
| `set_mud` |  |  | Makes the selected province muddy. |
| `set_weather` |  | `<weather_type>` | Sets the weather of the selected province and its region. A hoi4.exe message lists the types `clear`, `rain`, `storm`, `snow`, `blizzard`, `sandstorm` (executable string). All six types are accepted, and an unknown type lists the valid ones. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, console reply and province tooltip. See the note below the table. |
| `enable_weather` |  |  | Turns weather simulation on. |
| `disable_weather` |  |  | Turns weather simulation off. |
| `goto_region` |  | `region id` | Centres the camera on a strategic region. |
| `debug_norender` |  |  | Toggles rendering of the map. |
| `railroads` |  |  | Toggles rendering of railroads. |
| `show_enemy_ships` |  |  | Toggles always showing enemy ships. |
| `show_ships` |  |  | Toggles always showing your own ships. |
| `simplified_transport` |  |  | Toggles simplified naval transports. |
| `add_fleet_arrow` |  | `color` | Adds an arrow around a strategic region. Not in release build. |
| `add_temp_supply_node` |  |  | Adds a temporary supply node. Not in release build. |
| `supply_toggle_flow_penalties` |  |  | Toggles the supply penalties caused by bad supply flow. Not in release build. |
| `dbg_prov` |  | `<int>` | Chooses the kind of debug information drawn on provinces. Not in release build. |
| `dbg_enable_scripted_gui` |  | `<scope>` | Enables scripted GUIs for a scope. Not in release build. |
| `debug_validate_supply` | `dbg_sply` |  | Toggles validation of the supply cache. Not in release build. |
| `ListIncorrectCenterOfRegions` |  |  | Lists regions whose centre point lies inside another region. Not in release build. |
| `map_icon_reload_type` |  | `<NUM> or <help>` | Picks one map icon type to reload; `help` lists the numbers. Not in release build. |
| `rebuildlayers` |  |  | Reloads the map modes. |

- `set_weather`: with a Brandenburg province selected, `set_weather clear`, `rain`, `storm`, `snow`, `blizzard` and `sandstorm` each replied "Weather was set to '<type>' in the selected province (and its corresponding region)". After `sandstorm` the province tooltip read "Weather: Sandstorm (0C)" and the Eastern Germany region showed the haze. `set_weather zzz` replied "You must specify weather type (one of <clear, rain, storm, snow, blizzard, sandstorm>)". [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, console reply and province tooltip.
<!-- kit:end id="cc-map-view" -->

<!-- kit:begin id="cc-session" at="section:other-in-game-commands" -->
#### Game session, timing, checksums and developer tools

All rows: [docs] `documentation/console_commands_documentation.md`. No row in this block quotes hoi4.exe. Commands not on the wiki page.

| Command | Aliases | Arguments (as documented) | What it does |
| --- | --- | --- | --- |
| `gamespeed` |  | `speed <0-5>` | Sets the game speed from 0 to 5; 0 pauses. |
| `auto_unpause` |  | `[speed 1-5]` | Unpauses automatically at a given speed once clients have caught up; no argument turns it off. Not in release build. |
| `sleep` | `wait` | `time in sec` | Waits for the given number of seconds. Not in release build. |
| `pause_on_trigger` |  |  | Pauses the game when a trigger fires. |
| `gamestate_timer` | `gstimer` | `on / off` | Switches recording of how long an hour, day or week takes to process on or off. |
| `timer` |  |  | Prints debug timing information. |
| `timer_dump` |  |  | Dumps debug timing information. |
| `timer_reset` |  |  | Resets debug timing. |
| `timer_restart` |  |  | Resets and restarts debug timing. |
| `timer_start` |  |  | Starts debug timing. |
| `timer_stop` |  |  | Stops debug timing. |
| `ct` |  |  | Puts timer information on the clipboard. |
| `profile` |  | `<on> <off> <print> <clear>` | Controls profiling: `on`, `off`, `print`, `clear`. |
| `metrics` |  | `log_units\|log_pools\|player\|air_mission\|global\|unit_assignments <days>\|decision\|log\|file<=file_name>\|tag=<country_tag>\|add_tag=<country_tag>` | Toggles collection of metrics; the argument selects what to log. Not in release build. |
| `ironman` |  |  | Applies ironman status to the current game. Not in release build. |
| `deironman` |  |  | Removes ironman status from the current game. Not in release build. |
| `restart` |  |  | Restarts the game as the current country. Not in release build. |
| `print_controllers` |  |  | Prints the countries controlled by human players. |
| `morehumanswithcountries` |  | `num` | Adds more humans and assigns them to the highest scoring free countries. |
| `test` |  |  | Placeholder for local debug code. Not in release build. |
| `test_log` |  |  | Enables or disables tests. |
| `test_save_mode` |  |  | Chooses whether the save for a failed test is from the current or the previous day. |
| `testrtti` |  | `<test case>` | Tests RTTI performance with a test case. |
| `testtool` |  |  | Opens a testing tool. Not in release build. |
| `randomlog` | `rlog` |  | Toggles the random logs. Not in release build. |
| `oos_dump` | `oosdump` |  | Generates an out-of-sync dump on demand for the local client. Not in release build. |
| `dump_checksum` |  |  | Computes the checksum and stores it in a file. |
| `compare_to_last_checksum` |  |  | Compares the current checksum with the most recent dump. |
| `dump_synchronized_members` |  |  | Dumps the synchronised game state (the one with checksum id 2). |
| `dump_cached_random_logs` |  |  | Dumps cached random logs. |
| `dump_garrison_templates` |  |  | Dumps garrison templates to the game log. |
| `select` | `sel` | `<object id>, <object type id> (optional)` | Selects an object by id (and optional object type id). Not in release build. |
| `Audio.PlayEffect` |  | `effect_name` | Plays a sound effect by name. |
| `CrashReporter.DeleteCrashData` |  |  | Deletes local crash dumps older than a number of days. |
| `CrashReporter.SimulateCrash` |  |  | Simulates a crash; the game exits. |
<!-- kit:end id="cc-session" -->

<!-- kit:begin id="cc-tweakables" at="section:other-in-game-commands" -->
#### Tweakable variables not on the page

All rows: [docs] `documentation/console_commands_documentation.md`. The documentation gives only the type (Boolean) for every variable and no description. Type the name alone to toggle it, add a non-zero number to force it on, or `0` to force it off.

Available in the release build:

`CounterIntelligence.TestShieldColors`, `Debug.OldCombat`, `IntelNetwork.Instant`, `resistance_system`

Labelled "Not available in release build":

`Audio.Compressor`, `Audio.Debug`, `Audio.Debug.ExtendedRange`, `BattleSound.Debug`, `BattleSound.PlayBackground`, `BorderLOD.Threaded`, `Debug.DeleteUnitEachTick`, `Draw.Borders`, `Draw.Objects`, `Draw.Postfx`, `Draw.Refractions`, `Draw.Rivers`, `Draw.ShadowBlur`, `Draw.Shadows`, `Draw.Terrain`, `Draw.Transparent`, `Draw.Tree`, `Draw.Water`, `PostEffectVolumes.Draw`, `PostEffectVolumes.Enabled`, `ShowBorderTypes`, `Terrain.MipLevels`, `Tree.MipLevels`, `Update.Animations`, `Update.Particles`, `supply_debug.show_debug_lines_rail`, `supply_debug.show_debug_lines_supply`, `supply_debug.show_debug_lines_train`, `supply_debug.show_debug_rivers`

The page already covers `Agency.AutoComplete`, `Agency.InstantSlotUnlock`, `Agency.KeepExcessOperatives`, `Decision.FastRemove`, `Decision.NoChecks`, `Focus.AutoComplete`, `Focus.IgnorePrerequisites`, `Focus.NoChecks`, `Operation.Instant`, `fa` and `ShowTechBonus`.  The documentation gives each of them only a type and a release-build flag, with no description. [docs] The variable names suggest draw toggles (`Draw.*`), audio and debug lines, but what they do is untested. [unverified] Typing `Draw.Water`, `Draw.Rivers`, `Draw.Terrain` or `Audio.Debug` printed "Command available only for developers.", so the console refused those four. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, console reply.
<!-- kit:end id="cc-tweakables" -->
