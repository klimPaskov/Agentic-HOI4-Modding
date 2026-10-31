# Console commands

*Offline snapshot of the Hearts of Iron IV Wiki page "Console commands", revision 105778, captured 2026-10-31. Wiki text by the wiki's contributors under CC BY-SA 3.0 (see LICENSE.txt); kit blocks are local additions under the same license.*

<!-- kit:begin id="review" at="top" build="1.19.3.0" checked="2026-10-31" revision="105778" sources="documentation/console_commands_documentation.md localisation/ignored_loc_keys.txt launcher-settings.json documentation/triggers_documentation.md documentation/effects_documentation.md" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Checked against: `documentation/console_commands_documentation.md` (386 commands and 44 tweakable variables), `localisation/ignored_loc_keys.txt`, `launcher-settings.json`, and a string search of `hoi4.exe` for commands the documentation does not list.
Kit blocks added: an intro and a glossary, three correction blocks (rows that differ from the documentation, commands that are gone or undocumented, and the "no longer exists" and "unknown what" notes), a table of the commands that matter most for modding (`loc_check` family, `debug_checkportraitssanity`, reload commands, `event`, `effect`, `eval_effect`, `trigger`, `error`, `list_*`), eight tables for the 180 documented commands the page never named, and the 33 tweakable variables it never named.
Gaps left: the documentation gives one line per command, so what `loc_check` counts as a bad key, which `reload <target>` names work, and how `setowner` and `annex all` take arguments are [unverified]. Commands were not run in the game.
<!-- kit:end id="review" -->

## Table of contents

- [List of commands](#List_of_commands)
  - [Internal IDs](#Internal_IDs)
  - [Disambiguation](#Disambiguation)
  - [Glossary](#Glossary)
  - [Useful commands](#Useful_commands)
  - [Modding-useful commands](#Modding-useful_commands)
  - [Other in-game commands](#Other_in-game_commands)
- [See also](#See_also)
- [References](#References)

---

This page lists the codes which may be input into the Console Window, a special debugging window which may be accessed on non-ironman games by hitting `^` , `°` or tilde (~) (key varies based on keyboard layout). Press the up or down arrow keys to traverse through previously executed commands. Many codes can be turned off by repeating the command, but sometimes reloading the save or exiting the game is necessary. Please note that many of these commands come in and out with each DLC making some of them not work. Mods may introduce commands and more commonly, tags into the game to enhance their gameplay.

Also of note, commands may not work in ironman games by design.

```text
Hint: You must launch the game in debug mode `-debug` in order to use the console.
```

## List of commands <a id="List_of_commands"></a>

Press Shift+2, §, ~, \\, \`, ", º, ^ or ALT+2+1, or Shift+3 to access the console (key varies based on keyboard layout)

<!-- kit:begin id="cc-intro" at="section:List_of_commands" -->
**Kit note** What the installed documentation covers. `documentation/console_commands_documentation.md` lists 386 console commands and 44 tweakable variables. 71 of the commands and 30 of the variables carry the label "Not available in release build". [docs]

- Rows below marked "Not in release build" are those labelled commands. Do not rely on them in the shipped game; 33 of them are rows already on this page (listed in the correction block at the end of the page). [docs]
- A tweakable variable is a switch you type by name. A Boolean one toggles when typed alone, turns on with a non-zero number after it, and off with `0` (`Agency.AutoComplete 1`). All 44 variables in 1.19.3 are Boolean. [docs]
- `help` prints all commands or one description, `helplog` writes the whole command list to `game.log`, and `trigger_docs` (aliases `effect_docs`, `scripting_docs`, `docs`) prints the trigger, effect and variable documentation. [docs]
- Debug launch: the Paradox launcher entry "Open game in Debug Mode" starts `hoi4.exe` with `-gdpr-compliant -debug_mode` (`launcher-settings.json`). [vanilla-confirmed 1.19.3] The `is_debug` trigger documentation names the argument `-debug`. [docs] How the game matches the two spellings is not documented. [unverified]
- `Focus.NoChecks`, `Decision.NoChecks`, `Operation.Instant` and the other dotted names in the variable list are tweakable variables, not commands, so they are typed alone to toggle. `Agency.Instant` is the exception: it is a command that switches on four other switches. [docs]
<!-- kit:end id="cc-intro" -->

### Internal IDs <a id="Internal_IDs"></a>

*See also: Countries*

Console commands use internal IDs, which may be obtained in a variety of different ways.

An easy way to tell internal IDs is debug mode. `debug` as a console command will turn on debug mode which can provide information about certain database entries, such as focuses, national spirits (and other ideas such as laws or designers), or technologies when hovering over them, as well as obtaining information when hovering over a province of IDs of the state and the province, as well as the 3-letter country tag of the country it belongs to. [Note that while modding, the console command does not do everything that the launch option does and cannot serve as a substitute.](<Modding - Hearts of Iron 4 Wiki.md>)

If that is impossible, using localisation is an alternative. To do that, navigate to the folder where the game is contained, then to the `/Hearts of Iron IV/localisation/english/` folder. Each file in there contains localisation keys with values that actually appear in-game assigned to them. Using a non-default text editor can also allow using the 'Search in files' function (Such as in Notepad++, Sublime Text, or Visual Studio Code) in order to search through every single localisation file at the same time to find a specified value.

### Disambiguation <a id="Disambiguation"></a>

In this article, there are 3 types of brackets used within commands:

- Regular brackets as in `instantconstruction(ic)` are used to show aliases, alternate names for the console commands. In this case, using `ic` or `instantconstruction` has the same effect in-game.
- Square brackets as in `fow [Province ID]` signify an *optional* argument. In this case, both `fow` and `fow 1234` will work, but may have different effects.
- Square brackets in combination with angle brackets as in `event [<event ID>]` signify a *mandatory* argument. In this case, `event generic.1` will work, but `event` will not.

### Glossary <a id="Glossary"></a>

MIOs is an acronym for Military Industrial Organizations

<!-- kit:begin id="cc-glossary" at="section:Glossary" -->
**Kit addition** Terms used on this page and in the console documentation. All rows: [docs] `documentation/console_commands_documentation.md` unless another file is named.

| Term | Meaning |
| --- | --- |
| Alias | A second name for the same command. The documentation lists them per command and either name works. |
| Selected scope | Many commands act on what is currently selected: `effect`, `eval_effect`, `trigger`, `eval_trigger` run in the selected scope, and `list_flags`, `list_vars` and `list_modifiers` read the selected country, state or unit leader. |
| Tweakable variable | A named on/off switch (all Boolean in 1.19.3) that is toggled by typing its name. |
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

### Useful commands <a id="Useful_commands"></a>

| Command | Effect | Example/Comment |
| --- | --- | --- |
| help `[command name]` | Print out all console commands or a specific command description. |  |
| tag `[<Country tag>]` | Changes the country that the player controls. |  |
| event `[<event id>]` `[Target country tag]` | Executes an event | Event pages can be used to tell the IDs of events. If the event has a `trigger = { ... }` block, it says which triggers were met and which weren't. |
| finish_decision `[<decision id>]` or "all" | Finish timed missions instantly. |  |
| add_ideas `[<idea name>]` | Adds ideas with <id> to the country. Can also replace laws. |  |
| remove_ideas `[<idea name>]` | Removes national idea. |  |
| energy_ratio (er) `[<ratio>]` | Set Energy Ratio from 0 to 1 for the factories without coal consumption. |  |
| FI \[amount} | Adds to faction initiative | FI 5 adds 5 faction initiative |
| mastery `[<mastery amount>]`, `[track name]` | Give doctrine mastery, globally or to a specific track. |  |
| gain_xp `[<amount>]` | Adds experience to selected Leader/General/Admiral | gain_xp 100000(level capped at 9) |
| gain_xp `[<trait>]` | Adds **gainable** trait to selected Leader/General/Admiral | ie: gain_xp seawolf<br> **Note** To make it work with new, generic created Admirals:<br> 1. Open  *'Documents\Paradox Interactive\Hearts of Iron IV\settings.txt'*  with a text editor and change "save_as_binary=yes" to "save_as_binary=no".<br> 2. Start game, load savegame and save as new file, exit game.<br> 3. Open  *'Documents\Paradox Interactive\Hearts of iron IV\Save Games'* , open the newly created savegame file, search (CTRL-F) for the name of your generic created Admiral <br> 4. Go a few lines below to **max_traits=0.000** and add the following code block behind it *(example below)* 5. Make sure to save the file with **ANSI** encoding format.<br> 6. Start game, load save game, use gain_xp command, enjoy.<br> (Optional turn back on binarization in settings.txt) |
| cp `[<amount>]` | Adds Command Power | cp 100 (capped at 100) |
| st `[<amount>]` | Adds Stability | st 100 (capped at 100) |
| add_war_support(ws) `[<amount>]` | Adds War Support | ws 100 (capped at 100) |
| reduce_opinion `[<country tag>]` | Reduce opinion to/from tag. |  |
| allowtraits | Allows free assignment of general traits |  |
| add_equipment(ae) `[<equipment amount>]` `[<equipment name>]` | Adds equipment | Equipment uses the basic name so 'ae 1000 infantry_equipment_1'.You can only add researched equipment. Does not support Naval equipment. (with the exception of convoy: 'ae 1000 convoy_1') To add ships, consider using instantconstruction(ic) or instanttraining (it) ('ic' or 'it' also effects AI). To add modified equipment, you have to address it by given name. Example: You create a variant of 'Matilda LP'-tank with better Armor and Main Gun and name it 'Matilda LP Mk. IV'. Now use 'add_equipment 1000 Matilda LP Mk. IV'. |
| add_latest_equipment(ale) `[<equipment amount>]` | Gives player amount of latest equipment variants | To add only a specific type of your latest equipment, you have to address it's given name. Example: You create a variant of 'Matilda LP'-tank with better Armor and Main Gun and name it 'Matilda LP Mk. IV'. Now use 'add_latest_equipment 1000 Matilda LP Mk. IV'. |
| addfunds | Adds funds to all MIOs | Adds 1000 funds to every MIO (military industrial organisation) |
| addTaskCapacity `[number]` | Adds task capacity to all MIOs | Defaults to 1 if no input given. To add task capacity to only a specific MIO, you will need to find the MIO id in *\Hearts of Iron IV\common\military_industrial_organization\organizations\\<your country's tag>.txt* Then you use addTaskCapacity `[<MIO id>]` `[number]` |
| addSize `[number]` | Adds trait points to all MIOs | Defaults to 1 if no input given. To add trait points to only a specific MIO, you will need to find the MIO id in *\Hearts of Iron IV\common\military_industrial_organization\organizations\\<your country's tag>.txt* Then you use addSize `[<MIO id>]` `[number]` |
| add_cic_bank `[number]` | Adds Economic Capacity Surplus for the player in the International Market | Defaults to 1 if no input given |
| whitepeace(wp) `[<country tags>]` | White peace with the specified countries. |  |
| teleport(tp) | Activates the Teleportation tool | Can teleport units where ever you tell them to go (right click a province with a selected unit) |
| allowdiplo(adiplo,nocb) | Allows to use all diplomatic actions for no matter the rules. (Can declare war without justification) | This is likely the most effective way of wanting to start a war **without** needing to wait for the justification. If you only want instant justification and not the extra options it comes with, then use (instant_wargoal). |
| debug_crash(crash) | Crashes the game. |  |
| instantconstruction (ic) | Toggles instant construction cheat. | Affects AI. Ships are also constructed instantly. |
| research `[<slot id> or "all"]` | Researches a technology from research slot or all. | Research all will instant research all technologies |
| research_on_icon_click (roic) | Research a technology when clicking on technology tree icon | Will Allow you to research an item without its prerequisite or two mutually exclusive items |
| toggle_hidden_techs (tht) | Toggle show/hide all hidden techs. |  |
| sp_breakthrough `[<number>]` sp_breakthrough `[<number> optional <specialisation>]` (sp_br) | Adds special project breakthrough points for all facilities. | ex: sp_breakthrough 1 ex: sp_br 20 specialization_land  Specialization are: specialization_land, specialization_air, specialization_naval, specialization_nuclear (For the one added by mod it's in Mod Path\common\special_projects\specialization) |
| sp_fast | Skips the prototyping stage and progresses the iteration stage for special projects |  |
| sp_instant | Autocompletes current special projects |  |
| sp_available | Unlocks/Locks all special projects with unfufilled research prerequisites | E.g. Unlocks nuclear special projects without researching the "Atomic Research" technology |
| sp_unlock_all | All Special Projects are always visible and available. Whether or not the triggers returns true, and whether the parents are completed. |  |
| sp_research_all (sp_ra) | Research all special projects. If no scientist exist it will create one, otherwise it will pick an arbitrary one. |  |
| sp_prototype_reward | Trigger a specified prototype reward during a project. |  |
| sp_add_scientist sp_add_scientist `[<level> (optional)]` `[<specialisation> (optional)]` | Adds a generic scientist with no or specified specialisation/skill level | sp_add_scientist 3 nuclear sp_add_scientist 1 |
| sp_add_mastermind | Adds a generic scientist with all specialisations and max skill level |  |
| sp_set_selected_scientist_level `[<level>]` | Sets scientist's level | The facility view GUI with the assigned scientist must be opened |
| sp_add_selected_scientist_trait `[<trait>]` | Adds the specified trait to the scientist | ex: sp_add_selected_scientist_trait scientist_trait_brilliant_theorist Adds the brilliant scientist trait to the selected scientist. The facility view GUI with the assigned scientist must be opened Traits are found in "Hearts of Iron IV\common\scientist_traits\00_traits.txt" |
| annex `[<Target Country Tag> or "all"]` | Begin annex/annexes the specified tag | annex USA or annex d01 or annex all |
| puppet `[<Puppeteer Country Tag>]` `[<Puppet Target Country Tag>]` | Turns the target country into a puppet of the puppeteer | puppet GER CZE (Czechoslovakia becomes a puppet of German Reich) |
| manpower `[amount]` | Adds manpower to player | Defaults to 10 million if the number isn't specified. |
| add_opinion `[<Country tag>]` | Add opinion to/from tag | Adds 100 opinion (hardcoded number) to and from target country (add_opinion ENG for instance). A successfull call prints "<country> have 100 more opinion about you" and it appears as "cheat_opinion_modified_good" in the diplomacy screen |
| add_legitimacy `[<Country tag>]` `[<value>]` | Adds legitimacy to specified tag. | Example: add_legitimacy POL 22 |
| observe(spectator) | Switches to play no country at all, and no longer shows messages or pauses the game. However, it also interferes with AI performance and is not a good indication of what the AI will do if observe mode is not used. |  |
| tdebug | Toggles Debug info | Helpful for finding nation tags and ID's |
| occupationpaint(op) | Toggles occupation painting. If used with country tag occupies all of their owned, not controlled, land, | op JAP |
| setowner `[<country tag>]` | Sets state owner | Select the state you would like to set owner as. Select a state by clicking it. You need to click the state as the state id no longer works. |
| setcontroller `[<country tag>]` `[province id]` | Sets province controller |  |
| xp `[<XP amount>]` | Gives Army, navy and air experience to player | Can be used once per day |
| pp(fuhrer_mana,political_power) `[PP amount]` | Gives(or removes) political power to player | Defaults to 1000 if the amount is unset. |
| fuel `[<amount>]` | Adds Fuel | fuel 100000 (capped at your deposits capacity, adding much more will result in decreasing fuel) |
| civilwar `[<ideology>]` `[<target country tag>]` | Spawns a civil war | civilwar fascism ENG : Other Valid ideologies "communism" "democratic" "neutrality" |
| add_party_popularity <ideology group> <value> | Adds party popularity | ideology group has shortcuts d f n c for vanilla HOI groups. |
| set_ruling_party <ideology group> | Sets ruling party | ideology group has shortcuts d f n c for vanilla HOI groups. |
| Focus.AutoComplete (fa) | Allows national focuses to be instantly finished | Affects AI |
| Focus.NoChecks | Ignores focus requirements | Affects AI |
| Focus.IgnorePrerequisites | Ignores focus prerequisites | Allows you to start a focus in the middle of the tree. Affects AI |
| freefocuses (ff) | Enable freely activating any focuses | Combination of Focus.AutoComplete (fa), Focus.NoChecks and Focus.IgnorePrerequisites. |
| Decision.FastRemove | Shortens decisions to 1 day |  |
| Decision.NoChecks | Ignores decision requirements | Also disables cost, affects AI |
| instant_prepare | Instantly prepares naval invasions | Only works in debug mode. |
| instanttraining (it) | Instantly trains divisions and ships | Affects AI |
| nuke `[number]` | Adds nukes | Add 100 or 1000 |
| ai_accept (yesman) | AI will accept all diplomatic offers |  |
| add_core <state_id> | Adds cores |  |
| Agency.Instant | Makes everything regarding agencies instant. | Equivalent to a combination of Operation.Instant, IntelNetwork.Instant, Agency.InstantSlotUnlock, and Agency.Autocomplete |
| Agency.InstantSlotUnlock | Removes wait time between agent recruits |  |
| Agency.Autocomplete | Instantly completes agency upgrades |  |
| prevent_operative_detection | Your operatives/spies won't be detected anymore |  |
| force_operative_detection | Your operatives/spies will be detected |  |
| Operation.instant | Instantly finishes all operations | Affects AI |
| agency.keepexcessoperatives |  |  |
| deleteallunits(delall) `[country]` | Delete all armies and fleets of the specified countries. | deleteallunits SPR |
| deleteallunitsbut(delallbut) `[country]` | Delete all countries' armies and fleets, with the exception of one country. | delallbut SPR |
| add_autonomy `[<Target Country Tag>]` `[num]` | Changes a country's autonomy level | add_autonomy PHI -200 |
| resistance | Increases resistance in the selected province by set amount | ex: (selects one of the provinces in Berlin) resistance 100 |
| compliance | Increases compliance in the selected province in game by set amount | ex: (selects one of the provinces in Danzig) compliance 100 |
| add_intel `[<Country tag 1>]` `[Country Tag 2]` `[civilian,army,navy,airforce]`=`[number]` add_intel `[<Target Country tag>]` `[civilian,army,navy,airforce]`=`[number]` | Sets the inputted intel the first tag has against the second tag. The set intel amount is a static value (will be permanent for the rest of the game). | ex (sets intel player has against France to max): add_intel FRA ex (sets army intel Germany has against USA to 20%): add_intel GER USA army=20  ex (sets airforce and civilian intel Player has against Japan to 90% and 76% respectively): add_intel JAP airforce=90 civilian=76 |
| add_mines | Maximises player owned naval mines in the selected regions |  |
| acclimization `[<climate type>]` `[<number>]` | Sets the selected division's acclimization to the specified climate type and its percentage (reduces penalties from cold/hot weather or temperature debuffs) | ex: acclimization cold_climate 75 ex: acclimization hot_climate 20 **Note** that it resets the opposite climate type to 0% |
| debug_smooth | Toggle framesmoothing | Can increase game speed significantly, depending on system typically between 10 and 35 percent |

**Example: gain_xp `[<trait>]`**

```text
			in_progress={
				seawolf=0.000
				superior_tactician=0.000
				spotter=0.000
				fly_swatter=0.000
				ironside=0.000
				air_controller=0.000
			}
```

<!-- kit:begin id="cc-fix-useful" at="section:Useful_commands" -->
**Kit correction** Rows in the table above that differ from the 1.19.3 documentation. All rows: [docs] `documentation/console_commands_documentation.md`, except where a cell says [unverified].

| Page row | What 1.19.3 documents |
| --- | --- |
| `acclimization` | The command is spelled `acclimatization`, alias `acc`, arguments `<climate_name>, <value 0-100>`. The spelling `acclimization` appears nowhere in the documentation or in hoi4.exe. [unverified] |
| `add_core <state_id>` | Takes a `<Province ID>`, not a state id. |
| `remove_core [<State ID>] [<Country Tag>]` | Takes a single `<Province ID>`. The documentation lists the command; the page's "Command does not work" is not stated anywhere. [unverified] |
| `puppet [<Puppeteer>] [<Target>]` | One argument, `<Target Country Tag>`. The two-tag form is not documented. [unverified] |
| `teleport(tp)` | Takes `<province_id>` and teleports the selected armies or ships there. |
| `setowner [<country tag>]` | The argument list is `country tag, state id`. The page's claim that a state id no longer works is not in the documentation. [unverified] |
| `annex [<tag>] or "all"` | One `<Target Country Tag>` is documented. The `all` form is not. [unverified] |
| `debug_crash(crash)` | Labelled "Not available in release build". |
| `tdebug` (first row, "Toggles Debug info") | `tdebug` is the alias of `provtooltipdebug`, which toggles the debug info in the province tooltip (the page lists that command again further down). The command that toggles generic Debug info is `debug_info`, and it is not in release builds. |
| `pp(fuhrer_mana,political_power)` | Only `political_power` is a documented alias. `fuhrer_mana` is in neither the documentation nor hoi4.exe. [unverified] |
| `FI [amount}` | The command is `faction_initiative`, alias `fi`, arguments `amount, countrytag` (tag optional, default the player). |
| `st`, `ws` | Aliases of `add_stability` and `add_war_support`. Both document the argument as "unity amount". |
| `nuke [number]` | Alias of `nukes`, argument `<count>`. |
| `fuel [<amount>]` | Also has the alias `army_juice`. `fuel_gain` changes the daily fuel gain instead. |
| `add_ideas`, `remove_ideas` | Accept `all` or several idea ids separated by spaces. |
| `add_mines` | Alias `mines`, argument `<Amount of naval mines>`, applied to the selected region(s). The page's "maximises" is not stated. [unverified] |
| `add_autonomy` | Listed with no description and no arguments. |
| `set_country_flag` | The documentation says it sets the flag on a given tag for a duration and defaults to the current country, value 1 and no expiry, but its argument list shows only the flag name. The page's note that another tag does not work is not in the documentation. [unverified] |
| `Focus.AutoComplete (fa)` | `fa` is documented as its own Boolean tweakable variable next to `Focus.AutoComplete`. |
| `addfunds` ("adds 1000 funds") | The command is `AddFunds` with aliases `mio.AddFunds` and `IndustrialOrganisation.AddFunds`. The first argument is an optional MIO token, the second an optional amount. With no amount it adds `NDefines::NIndustrialOrganisation::FUNDS_FOR_SIZE_UP`, which is 700 in 1.19.3 (`common/defines/00_defines.lua`, [vanilla-confirmed 1.19.3]), not 1000. |
| `addTaskCapacity`, `addSize` | Real names `AddTaskCapacity` and `AddSize`, with the same `mio.` and `IndustrialOrganisation.` aliases. A negative task capacity is allowed but the result is capped at 0. |
| `add_cic_bank` | Also has the aliases `stonks`, `cic` and `bank`. A negative value subtracts. |
| `force_operative_detection` | Alias `snitch`. The documentation text is a copy of `print_intel_network`'s, so its description is unreliable. |
| `list_hidden_focuses` | Alias `list_hd`; the argument is a country tag. |
| `release` | Alias `rls`. |
<!-- kit:end id="cc-fix-useful" -->

### Modding-useful commands <a id="Modding-useful_commands"></a>

Several other commands previously mentioned, such as event, are useful in modding too.

| Command | Effect | Example/Comment |
| --- | --- | --- |
| guibounds(gui) | Toggles the GUI bounds debug, allowing to test for different window sizes easier. | Also grants the name of the sprite and the interface element the player is hovering on, allowing to find the location of the image by [searching every `/Hearts of Iron IV/interface/*.gfx` file at the same time.](<Modding - Hearts of Iron 4 Wiki.md#Universal_modding_concepts>) |
| set_var `[<variable>]` `[<value>]` | Changes the value of a variable to the specified value. |  |
| get_var `[<variable>]` | Shows the value of a variable in the console |  |
| list_vars | Lists the variables set in the selected scope and their values. |  |
| set_country_flag `[<Country Flag>]` | Adds a country flag to currently played nation. | Does not work if you put another nations tag in the command such as "set_country_flag flag AUS", even if it says in console that it does. |
| set_global_flag `[<Global Flag>]` | Adds a global flag. |  |
| list_flags | Lists currently active flags in the console windows. | Context senstive if nothing (global_flag), country (country_flag) or state (state_flag) is selected when entering this command. |
| fast_forward `[<amount of days>]`, `[observer]` | Fast forward a set amount of days. |  |
| list_hidden_focuses | Lists all of the hidden focuses from a country. |  |
| show_focuses | Shows all the hidden focuses. |  |
| trigger `[<scripted_trigger_name>]` | Checks if a scripted trigger is true or not. |  |
| eval_trigger `[<trigger code block>]` | Checks if the trigger code following the command is true or not, within the currently selected scope. | Example: `eval_trigger OR = { has_completed_focus = GER_remilitarize_the_rhineland has_war_support > 0.5 }` |
| effect (e) `[<scripted_effect_name>]` | Executes a [scripted effect](<Effects - Hearts of Iron 4 Wiki.md>), within the currently selected scope. | Example: `e POL_remove_danzig_effect` on a state will execute that effect on the state. |
| eval_effect `[<effect code block>]` | Executes the effect code following the command, within the currently selected scope. | Example: `eval_effect load_focus_tree = german_focus` would switch the country currently selected to the German focus tree. |
| ai `[country tag...]` | Toggles the AI on or off | Without parameters toggles the AI for all countries. With parameters, toggles exceptions for those countries from the general rule. Can be used to confirm if a crash is AI-related. |
| aiview | Enable AI debug info |  |
| human_ai | Makes the AI control the country currently led by the player while the player also remains in control. | AI will also create logs within `/Hearts of Iron IV/logs/scripted_ai.log` in the [user directory](<Modding - Hearts of Iron 4 Wiki.md>). |
| set_cosmetic_tag `[<country tag>]` `[<cosmetic tag>]` | changes the name and flag of the country | set_cosmetic_tag USA SOV |
| reload `[<type>]` | Reloads files of a given type. Also accepts individual files within the `/Hearts of Iron IV/interface/` folder. Equivalent to the effect done automatically when saving over a file with debug mode turned on via launch options. | - reload loc (reloads localisation files) - reload focus (reloads focuses) - reload landcombat.gui (reloads land combat interface) |
| reloadoob `[<Target Country Tag>]` | Reloads orders of battle. |  |
| reloadinterface | Reloads the entire interface |  |
| reloadtechnologies | Reloads the technology database |  |
| updateequipments | Updates the equipment database |  |
| updatesubunits | Updates the subunit database |  |
| update_loc `[localization tag]` | Updates the localization tag file |  |
| error | Opens the error log file. | If there are special characters in the folder path, this won't work. Equivalent to pressing on the error dog if enabling debug mode in launch options. |
| imgui | Controls ImGui UIs. Use `imgui show` to list the available subcommands. These UIs cover a wide variety of useful modding tools, such as script profiling, AI debugging, and listing characters. |  |
| goto_province `[province id]` | Moves the camera position to the specified province. |  |
| goto_state `[state id]` | Moves the camera position to the specified state. |  |

<!-- kit:begin id="cc-fix-modding" at="section:Modding-useful_commands" -->
**Kit correction** Rows in the table above that differ from the 1.19.3 documentation. All rows: [docs] `documentation/console_commands_documentation.md`, except where a cell says [unverified].

| Page row | What 1.19.3 documents |
| --- | --- |
| `reload [<type>]` | There is no `reload` entry in the documentation. hoi4.exe contains the string `reload %s` and the messages `' reloaded!`, `No such reload target that takes arguments: '`, `Please specify the file name/target` and `defines reloaded!`. The page's examples (`reload loc`, `reload focus`, `reload landcombat.gui`) are therefore not confirmed. [unverified] The documented reload commands are `reloadoob`, `reloadinterface`, `reloadtechnologies`, `reload_textures` (aliases `rt`, `reload_texture`), `reloadfx`, `reloadweather`, `cityreload`, `rebuildlayers`, `update_loc`, `updateequipments` and `updatesubunits`. |
| `effect (e) [<scripted_effect_name>]` | Arguments are `<tag> scripted_effect_name`. It runs a scripted effect on the selected scope. Inline effect code goes through `eval_effect`. |
| `trigger [<scripted_trigger_name>]` | Alias `t`, arguments `<tag> scripted_trigger_name`. It runs a scripted trigger on the selected scope. Inline trigger code goes through `eval_trigger`. |
| `event [<event id>] [Target country tag]` | The documented arguments are `event id, <Target Country Tag>`. |
| `error` | Documented as "Show errors in log". Whether it opens a file is not stated. [unverified] |
| `set_var`, `get_var` | The documentation lists only `<var name>` for both. The page's `[<value>]` for `set_var` is not documented. [unverified] |
| `list_flags`, `list_vars` | Optional `<scope>` argument. They list the flags or variables of that scope, or of the selected country, state or unit leader. |
| `trigger_docs` | Aliases `effect_docs`, `scripting_docs`, `docs`. Documented as printing the trigger, effect and variable docs; where it prints is not stated. [unverified] |
| `human_ai` | Documented as "Toggles AI for Human countries". |
| `ai [country tag...]` | Documented only as "Toggles the AI on or off". `enable_ai` and `disable_ai` are separate commands. |
<!-- kit:end id="cc-fix-modding" -->

<!-- kit:begin id="cc-modding-highlights" at="section:Modding-useful_commands" -->
#### Kit: Commands that matter most when modding <a id="kit-cc-modding-highlights"></a>

All rows: [docs] `documentation/console_commands_documentation.md`, except the cell marked [unverified]. Every command here exists in 1.19.3 under exactly this name, and none is labelled "Not available in release build".

| Command | Aliases | Arguments (as documented) | Use |
| --- | --- | --- | --- |
| `loc_check` |  |  | Checks the localisation the game knows about for missing keys. Per-kind variants are in the next row. The exclusion list is `localisation/ignored_loc_keys.txt` (see the note below the table). |
| `loc_check_characters`, `loc_check_decisions`, `loc_check_events`, `loc_check_focuses`, `loc_check_modifiers`, `loc_check_national_spirits` | | | The same check restricted to one kind of content. These six are the only variants in 1.19.3. |
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
| `reloadfx` |  | `map/mapname/postfx or *.fx filename` | Reloads shaders. hoi4.exe also accepts `all`. [unverified] |
| `instantevents` |  |  | Ignores event MTTH values. |
| `easy_decisions` | `ezd` |  | Toggle: decisions with `days_remove` last 1 day, and decisions lose their cost and cost trigger. |
| `dump_equipment_loc` | | `desc`, country tags, equipment types, `path=<filepath>` (all optional) | Writes equipment localisation strings to a CSV, by default `logs/equipment_loc.csv`. `desc` dumps descriptions instead of names; type words such as `armor anti_tank` narrow the list. |
| `log_advisor_trait_errors` |  |  | Logs every unit-leader advisor that lacks the matching unit-leader trait. |
| `focus_count` |  | `<Target Country Tag>` | Counts the focuses a tag has. |
| `history_logger` |  |  | Toggles the history logger (the `log` effect can write to it; see [Troubleshooting](<Troubleshooting - Hearts of Iron 4 Wiki.md#Log_files>)). |
| `trigger_docs`, `helplog` | `effect_docs`, `scripting_docs`, `docs` (for `trigger_docs`) | | Print the trigger, effect and variable documentation; write the command list to `game.log`. |

`localisation/ignored_loc_keys.txt` is the exclusion list for the `loc_check` commands: its first line says keys added to it are ignored by the `loc_check*` commands, and the installed file holds 11 placeholder keys (`test.1.a`, `test_state.1.d` and similar). [vanilla-confirmed 1.19.3] hoi4.exe contains that path and the result lines `No missing or bad loc keys found`, `missing loc keys found`, `bad loc keys found` and `, check error log`, so details of a failed check are probably in the error log. [unverified]

Duplicate localisation keys are not a console check. The game reports them at start-up in `text.log`; see [Log files](<Troubleshooting - Hearts of Iron 4 Wiki.md#Log_files>). [unverified]
<!-- kit:end id="cc-modding-highlights" -->

### Other in-game commands <a id="Other_in-game_commands"></a>

| Command | Effect | Example/Comment |
| --- | --- | --- |
| province_ids (pid) | Show province IDs on the map |  |
| ShowTechBonus | Unknown what it does, however with the name we can make a guess it has to do something with tech bonuses. | Only for developers. |
| normals | Unknown what it does. | Only for developers. |
| rendertype | Reports what render backend is used |  |
| tweakergui | Spawns a tweaker GUI |  |
| time | What time is it? |  |
| reloadfx `[Arguments: map/mapname/postfx or \*.fx filename]` | Reloads the shader |  |
| particle_editor | Spawns a particle editor |  |
| analyzetheatres (anth) | Analyze theatres for errors. |  |
| massconquer (massc) | Mass conquer tool. Requires direct province names. | Only for developers. |
| aircombat (airc) `[<scenario name>]` `[<result name>]` `[<province id>]` `[<state id with airbase>]` `[<state id with airbase>]` `[<equipment type>]` `[<equipment type>]` `[<equipment creator country>]` `[<equipment creator country>]` | Spawns an air combat in desired location. | Only for developers. |
| fronts | Toggle visibility of the foreign fronts |  |
| ai_front_dump (aifrontdump) | Dump AI front data to log file, needs to have a unit selected |  |
| traderoutes | Toggle visibility of trade routes |  |
| debug_tactics | Toggle visibility of debug tooltip for tactics |  |
| reloadsupply (relsup) | Reinitializes the supply systems. |  |
| deltat `[<speed factor>]` | control animation speeds |  |
| building_health (bhealth) `[<building type>]` `[<state or prov id>]` `[<building level>]` `[<health to add>]` | Changes specified building health |  |
| nomapicons | Toggles map icons. |  |
| nopausetext | Toggles the pausebanner for nicer screenshots. |  |
| nextsong | Changes the currently playing soundtrack. |  |
| combatsound | How often does the combat view give a random sound? 0-50 |  |
| morehumans (humans) `[num]` | Adds more humans |  |
| window (wnd) `[Arguments: open/close]` `[window gui name]` | Opens or closes the specified window |  |
| poll | Polls valid Events |  |
| pause_in_hours | Pauses the game after X hours have passed after command is called |  |
| winwars | Gives max war score in all wars for the country | Command no longer exists as of patch 1.9.1 |
| testevent `[<Event ID>]` `[<Character ID>]` | Tests an event without triggering it |  |
| resign | Resign from the game |  |
| add_interest `[<Country tag>]` | Add specified country tag to your interest |  |
| remove_interest `[<Country tag>]` | Removes specified country tag from your interest |  |
| add_diplo | Adds diplomatic entroute |  |
| PrintSynchStuff | Prints random count and seed |  |
| SetRandomCount | Sets the random count to 0 or arg |  |
| ai_invasion | Toggles AI AI naval invasions |  |
| ai_pp_log | Prints AI use of PP to log |  |
| ai_idea_desire_log | Prints AI desire for ideas to log. For current country only |  |
| ai_force_template | Force the AI to only spend army XP on template design |  |
| ai_force_equipment | Force the AI to only spend army XP on equipment design |  |
| ai_front_id | Get the address of selected group's front debug ID |  |
| fow (debug_fow) `[Province ID]` | Turns off fog of war, only within a province if specified. |  |
| collision (debug_collision) | Toggles debug display of normals/bounding boxes/collision |  |
| savegame | Creates a savefile. |  |
| savecheck | Makes a save file (Test_01), loads the save file, makes a new savegame (Test_02). Those save files should look the same. |  |
| IP | Shows your IP |  |
| requestgamestate | Requests the gamestate from host |  |
| nudge | Go to the nudge tool |  |
| mapmode `[Mapmode type (int)]` | Change mapmode. |  |
| fullscreen | Toggles fullscreen |  |
| prices | Price Info |  |
| remove_core `[<State ID>]` `[<Country Tag>]` | Remove core. | Command does not work |
| debug_zoom | Zooms in the game |  |
| debug_types | Will print the data type for all dynamic reference objects. Can only be used if using RTTI. |  |
| debug_show_event_ID | Shows event ID |  |
| debug_commands | Printing commandcount to message.log |  |
| debug_events | Start Counting events |  |
| debug_dumpevents | Dump Event data to game log |  |
| debug_diploactions | Start Counting diplomatic actions |  |
| debug_dumpdiploactions | Dump diplomatic action data to game log |  |
| debug_assert | Toggles asserts on/off |  |
| debug_nomouse | Toggles mouse scrollwheel on/off |  |
| debug_terrain | Toggles Terrain on/off |  |
| debug_cities | Toggles Cities painting mode on/off |  |
| debug_water | Toggles Water on/off |  |
| debug_fronts | Toggles interpolated fronts debug |  |
| debug_off_front_snap (dbg_fsnap) | Toggles offensive fronts snapping debug |  |
| debug_borders | Toggles Borders on/off |  |
| debug_trees | Toggles Trees on/off |  |
| debug_rivers | Toggles Rivers on/off |  |
| debug_postfx | Toggles PostFX on/off |  |
| debug_sky | Toggles Sky on/off |  |
| debug_bloom | Toggles Bloom on/off |  |
| debug_tooltip | Toggles Tooltips on/off |  |
| debug_nuking | Allows to nuke every province without checking any conditions. | Command no longer exists as of patch 1.15.1 |
| flagsoutput `[<path>]` | Creates texture atlas files from memory. |  |
| cityreload | Reloads the cities |  |
| version | Show current game version |  |
| debug_nogui | Toggles GUI on/off |  |
| debug_volume `[<Volume Delta>]` | Modifies music volume |  |
| debug_lockcamera | Toggles Camera locked on/off |  |
| debug_lines | Toggles Debuglines |  |
| debug_entities | Toggles Debug entities |  |
| debug_info | Toggles Debug info |  |
| debug_particle | Toggles Particles Debug info |  |
| debug_ai_budget `[CountryTag]` | Show ai budget data |  |
| debug_textures | Writes Texture info to application debug log |  |
| debug_texture | draws textures like bloom |  |
| debug_wireframe | Toggles forced wireframe on/off |  |
| debug_achievements_clear | Clear all achievements and user stats | Only for developers. |
| moveunit `[<Unit ID>]` `[<Province ID>]` | Moves a unit to a province |  |
| spawnactor `[<Actorname>]` `[<Province ID>]` `[<Animation> OPTIONAL]` | Spawns an actor with an optional animation |  |
| cameraclamp | Toggles the camera clamping |  |
| provtooltipdebug (tdebug) | Toggles the debug info in province tooltip |  |
| reloadweather `[<randomseed>]` | Reload and regenerate weather |  |
| weather | Toggle weather simulation |  |
| debug_air_vs_land (dbg_cas) | Toggle debug mode for air vs land combat. |  |
| mapnames | Toggle map names |  |
| gbreload | Reloads gradient borders | Only for developers. |
| gbpaint `[layer]` `[channel]` | Toggles gradient border painting |  |
| profilelog | Prints out the profiling informations into time.log |  |
| run | Runs the specified file with list of commands |  |
| oos | Out of Synch | Only for developers. |
| trigger_docs (effect_docs, scripting_docs, docs) | Print docs for triggers, effects, and variables | Documentation for triggers/effects printed to game.log file |
| threat `[Threat amount]` | Adds or show threat level of the current tag, which is the world tension generated by the tag. | Positive values will add to the world tension generated by the active tag, while negative values will subtract from the world tension generated by the active tag, with corresponding entries in the world tension history log. By tag-switching, it is possible to raise or lower the world tension generated by any particular country. If one does "threat 999999999" it will reset the world tension to 0. |
| 3dstats | Toggles 3D Stats |  |
| hdr | Toggles hdr |  |
| hdr_debug | Toggles hdr debugging |  |
| srgb | Toggles sRGB |  |
| bloom | Toggles bloom |  |
| PostEffectVolumes.Default `[posteffect_values name]` | Toggles default posteffect values |  |
| night | Toggles night | \*as of 1.01 this does not seem to work (filed under developer-only command) This command can be emulated via the day/night loop option at the bottom right toolbar (shortcut key 'N') |
| filewatcher | Toggles filewatcher |  |
| createlean | Create LEAN textures |  |
| helplog | Print out all console commands to game.log file. |  |
| helphelp | Double Rainbow help. |  |
| hsv | Converts RGB to HSV |  |
| tag_color | Test setting a country's color |  |
| browser `[url]` | Show browser window |  |
| browser_base_url `[url]` | Set browser base url |  |
| airealism | Enable realistic AI | An easter egg making the AI smacktalk in chats. Useless since unactivable in multiplayer and chat unactivable in singleplayer.[1] |
| instant_wargoal | Will allow instant justificatiion of war goals on countries |  |
| allowideas | Allows the player to pick any idea even if normally unavailable | This overrides the `available` and `visible` triggers of ideas, but not the `allowed` trigger |
| release `[<country tag>]` | Releases a country or releasable nation | release slv releases Slovenia |
| InternationalMarket.AddSubsidyForTags `[<economic capacity>]` `[<equipment>]` `[<country tag>]` | Adds a subsidy for the player to buy off from a specified country. | ex (Adds a subsidy for the player to be able to help buy German sold light tanks for up to 5k EC): InternationalMarket.AddSubsidyForTags 5000 light_tank_chassis GER |
| random_seed | Randomises the current seed the game is using | The AI uses this seed to decide all their focuses and decisions. You can use this to generate a more favourable outcome to any ai action you dislike (e.g. you want to ally with country) |
| eval_effect `[<country tag>]` = { create_faction = "`[faction name]`" } | Creates a faction with a specified name | The leader of the faction will be the inserted country tag |
| eval_effect `[<country tag>]` = { dismantle_faction = yes } | Deletes the faction of specified country |  |
| eval_effect `[<country tag>]` = { add_to_faction = `[<country tag>]` } | Adds a country to a faction | The second tag is the country which will join the first tag's faction |
| eval_effect `[<country tag>]` = { remove_from_faction = `[<country tag>]` } | Removes a country from a faction | The second tag is the country which will be removed from the first tag's faction |
| eval_effect `[<country tag>]` = { set_faction_name = "`[faction name]`" } | Renames the faction of the specified country |  |
| toggle_silhouette_portraits | Enables and disables silhouette portraits. | Only for developers. |
| armageddon | Causes 100% damage to all state/shared/provincial buildings and facilities every state in every country. | Although the nuke detonation animation is played for all states, it does not give the Nuclear Fallout state modifier. |

<!-- kit:begin id="cc-fix-other" at="section:Other_in-game_commands" -->
**Kit correction** Rows in the tables above that the 1.19.3 documentation does not support. Sources: [docs] `documentation/console_commands_documentation.md`; where a cell says [unverified], the evidence is a string search in `hoi4.exe`.

| Page row | Status in 1.19.3 |
| --- | --- |
| `winwars`, `debug_nuking` | Absent from the documentation, and no such string is in hoi4.exe [unverified]. That agrees with the page's "no longer exists" notes (1.9.1 and 1.15.1). The documented replacement for nuking is `launch_nuke` (alias `ln`): it launches a nuke at given provinces without checking conditions. |
| `nextsong`, `poll`, `reloadsupply (relsup)`, `add_interest`, `remove_interest`, `requestgamestate`, `debug_commands`, `debug_volume`, `debug_ai_budget`, `profilelog`, `filewatcher`, `browser_base_url` | Not in the documentation and no matching command string in hoi4.exe. Treat them as removed. [unverified] hoi4.exe has only a `nofilewatcher` launch argument and game-state command class names, not a `filewatcher` or `requestgamestate` console string. |
| `normals` | Not documented. The only nearby string is the description of `collision`. [unverified] |
| `rendertype`, `tweakergui`, `particle_editor` | Not documented, but hoi4.exe contains the strings `rendertype`, `tweakergui` and `particle_editor save/restart/undo/redo/exit`. Whether they work as console commands in the shipped game is unknown. [unverified] |
| `ShowTechBonus` ("unknown what it does") | A Boolean tweakable variable, labelled "Not available in release build", with no description in the documentation. |
| `night`, `massconquer`, `aircombat`, `debug_achievements_clear`, `gbreload`, `oos`, `toggle_silhouette_portraits` | The page calls these developer-only or not working. The documentation confirms it: all are labelled "Not available in release build". |
| `remove_core` ("Command does not work") | Documented with a `<Province ID>` argument. Whether it works is not stated. [unverified] |

The page rows that the documentation labels "Not available in release build" are: `debug_crash`, `ShowTechBonus`, `massconquer`, `aircombat`, `ai_front_dump`, `debug_types`, `debug_diploactions`, `debug_dumpdiploactions`, `debug_assert`, `debug_fronts`, `debug_off_front_snap`, `debug_lines`, `debug_entities`, `debug_info`, `debug_particle`, `debug_textures`, `debug_texture`, `debug_wireframe`, `debug_achievements_clear`, `debug_air_vs_land`, `gbreload`, `gbpaint`, `oos`, `hdr`, `hdr_debug`, `srgb`, `bloom`, `PostEffectVolumes.Default`, `night`, `createlean`, `hsv`, `browser`, `toggle_silhouette_portraits`. Do not expect them to work in the shipped game. [docs]
<!-- kit:end id="cc-fix-other" -->

<!-- kit:begin id="cc-economy" at="section:Other_in-game_commands" -->
#### Kit: Economy, research and the international market <a id="kit-cc-economy"></a>

All rows: [docs] `documentation/console_commands_documentation.md`. Rows that quote hoi4.exe say so in the cell and are [unverified]. Commands not on the wiki page.

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

<!-- kit:begin id="cc-politics" at="section:Other_in-game_commands" -->
#### Kit: Politics, diplomacy, factions and balance of power <a id="kit-cc-politics"></a>

All rows: [docs] `documentation/console_commands_documentation.md`. Rows that quote hoi4.exe say so in the cell and are [unverified]. Commands not on the wiki page.

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

<!-- kit:begin id="cc-projects" at="section:Other_in-game_commands" -->
#### Kit: Special projects, medals and achievements <a id="kit-cc-projects"></a>

All rows: [docs] `documentation/console_commands_documentation.md`. Rows that quote hoi4.exe say so in the cell and are [unverified]. Commands not on the wiki page.

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

<!-- kit:begin id="cc-intel" at="section:Other_in-game_commands" -->
#### Kit: Intelligence, operations and raids <a id="kit-cc-intel"></a>

All rows: [docs] `documentation/console_commands_documentation.md`. Rows that quote hoi4.exe say so in the cell and are [unverified]. Commands not on the wiki page.

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

<!-- kit:begin id="cc-military" at="section:Other_in-game_commands" -->
#### Kit: Units, combat and fronts <a id="kit-cc-military"></a>

All rows: [docs] `documentation/console_commands_documentation.md`. Rows that quote hoi4.exe say so in the cell and are [unverified]. Commands not on the wiki page.

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

<!-- kit:begin id="cc-ai" at="section:Other_in-game_commands" -->
#### Kit: AI and pathfinding debugging <a id="kit-cc-ai"></a>

All rows: [docs] `documentation/console_commands_documentation.md`. Rows that quote hoi4.exe say so in the cell and are [unverified]. Commands not on the wiki page.

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

<!-- kit:begin id="cc-map-view" at="section:Other_in-game_commands" -->
#### Kit: Map, weather and display <a id="kit-cc-map-view"></a>

All rows: [docs] `documentation/console_commands_documentation.md`. Rows that quote hoi4.exe say so in the cell and are [unverified]. Commands not on the wiki page.

| Command | Aliases | Arguments (as documented) | What it does |
| --- | --- | --- | --- |
| `add_rain` |  | `<rain_amount>` | Adds rain to the selected province. |
| `add_snow` |  | `<snow_amount>` | Adds snow to the selected province. |
| `set_mud` |  |  | Makes the selected province muddy. |
| `set_weather` |  | `<weather_type>` | Sets the weather of the selected province and its region. A hoi4.exe message lists the types `clear`, `rain`, `storm`, `snow`, `blizzard`, `sandstorm`. [unverified] |
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
<!-- kit:end id="cc-map-view" -->

<!-- kit:begin id="cc-session" at="section:Other_in-game_commands" -->
#### Kit: Game session, timing, checksums and developer tools <a id="kit-cc-session"></a>

All rows: [docs] `documentation/console_commands_documentation.md`. Rows that quote hoi4.exe say so in the cell and are [unverified]. Commands not on the wiki page.

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

<!-- kit:begin id="cc-tweakables" at="section:Other_in-game_commands" -->
#### Kit: Tweakable variables not on the page <a id="kit-cc-tweakables"></a>

All rows: [docs] `documentation/console_commands_documentation.md`. The documentation gives only the type (Boolean) for every variable and no description. Type the name alone to toggle it, add a non-zero number to force it on, or `0` to force it off.

Available in the release build:

`CounterIntelligence.TestShieldColors`, `Debug.OldCombat`, `IntelNetwork.Instant`, `resistance_system`

Labelled "Not available in release build":

`Audio.Compressor`, `Audio.Debug`, `Audio.Debug.ExtendedRange`, `BattleSound.Debug`, `BattleSound.PlayBackground`, `BorderLOD.Threaded`, `Debug.DeleteUnitEachTick`, `Draw.Borders`, `Draw.Objects`, `Draw.Postfx`, `Draw.Refractions`, `Draw.Rivers`, `Draw.ShadowBlur`, `Draw.Shadows`, `Draw.Terrain`, `Draw.Transparent`, `Draw.Tree`, `Draw.Water`, `PostEffectVolumes.Draw`, `PostEffectVolumes.Enabled`, `ShowBorderTypes`, `Terrain.MipLevels`, `Tree.MipLevels`, `Update.Animations`, `Update.Particles`, `supply_debug.show_debug_lines_rail`, `supply_debug.show_debug_lines_supply`, `supply_debug.show_debug_lines_train`, `supply_debug.show_debug_rivers`

The page already covers `Agency.AutoComplete`, `Agency.InstantSlotUnlock`, `Agency.KeepExcessOperatives`, `Decision.FastRemove`, `Decision.NoChecks`, `Focus.AutoComplete`, `Focus.IgnorePrerequisites`, `Focus.NoChecks`, `Operation.Instant`, `fa` and `ShowTechBonus`.  The variable names suggest draw toggles (`Draw.*`), audio and debug lines, but the documentation does not describe them. [unverified]
<!-- kit:end id="cc-tweakables" -->

## See also <a id="See_also"></a>

- [Modding](<Modding - Hearts of Iron 4 Wiki.md>)

## References <a id="References"></a>

1. ↑ A comment of podcat about the command been found https://www.reddit.com/r/hoi4/comments/6cb8vh/the_secrets_of_hoi4/dhtdr4x/

---

## Navigation

**[Modding](<Modding - Hearts of Iron 4 Wiki.md>)**

- **Documentation**: [Effects](<Effects - Hearts of Iron 4 Wiki.md>) • [Triggers](<Triggers - Hearts of Iron 4 Wiki.md>) • [Defines](<Defines - Hearts of Iron 4 Wiki.md>) • [Modifiers](<Modifiers - Hearts of Iron 4 Wiki.md>) • [List of modifiers](<List of modifiers - Hearts of Iron 4 Wiki.md>) • [Scopes](<Scopes - Hearts of Iron 4 Wiki.md>) • [Localisation](<Localisation - Hearts of Iron 4 Wiki.md>) • [On actions](<On actions - Hearts of Iron 4 Wiki.md>) • [Data structures](<Data structures - Hearts of Iron 4 Wiki.md>) • [Flags](<Data structures - Hearts of Iron 4 Wiki.md#Flags>) • [Event targets](<Data structures - Hearts of Iron 4 Wiki.md#Event_targets>) • [Country tag aliases](<Data structures - Hearts of Iron 4 Wiki.md#Country_tag_aliases>) • [Variables](<Data structures - Hearts of Iron 4 Wiki.md#Variables>) • [Arrays](<Data structures - Hearts of Iron 4 Wiki.md#Arrays>)
- **Scripting**: [Achievements](<Achievement modding - Hearts of Iron 4 Wiki.md>) • [AI](<AI modding - Hearts of Iron 4 Wiki.md>) • [AI focuses](<AI focuses - Hearts of Iron 4 Wiki.md>) • [Autonomous states](<Autonomy state modding - Hearts of Iron 4 Wiki.md>) • [Balances of power](<Balance of power modding - Hearts of Iron 4 Wiki.md>) • [Bookmarks/Scenarios](<Bookmark modding - Hearts of Iron 4 Wiki.md>) • [Game rules](<Bookmark modding - Hearts of Iron 4 Wiki.md#Game_rules>) • [Buildings](<Building modding - Hearts of Iron 4 Wiki.md>) • [Characters and traits](<Character modding - Hearts of Iron 4 Wiki.md>) • [Cosmetic tags](<Cosmetic tag modding - Hearts of Iron 4 Wiki.md>) • [Countries](<Country creation - Hearts of Iron 4 Wiki.md>) • [Divisions](<Division modding - Hearts of Iron 4 Wiki.md>) • [Decisions](<Decision modding - Hearts of Iron 4 Wiki.md>) • [Doctrines](<Doctrine modding - Hearts of Iron 4 Wiki.md>) • [Equipment](<Equipment modding - Hearts of Iron 4 Wiki.md>) • [Events](<Event modding - Hearts of Iron 4 Wiki.md>) • [Factions](<Faction modding - Hearts of Iron 4 Wiki.md>) • [Ideas](<Idea modding - Hearts of Iron 4 Wiki.md>) • [Ideologies](<Ideology modding - Hearts of Iron 4 Wiki.md>) • [Military industrial organizations](<Military industrial organization modding - Hearts of Iron 4 Wiki.md>) • [National focuses](<National focus modding - Hearts of Iron 4 Wiki.md>) • [Resources](<Resources modding - Hearts of Iron 4 Wiki.md>) • [Scripted GUI](<Scripted GUI modding - Hearts of Iron 4 Wiki.md>) • [Technologies and doctrines](<Technology modding - Hearts of Iron 4 Wiki.md>) • [Units](<Unit modding - Hearts of Iron 4 Wiki.md>)
- **Map**: [Map](<Map modding - Hearts of Iron 4 Wiki.md>) • [States](<State modding - Hearts of Iron 4 Wiki.md>) • [Supply areas](<Supply areas modding - Hearts of Iron 4 Wiki.md>) • [Strategic regions](<Strategic region modding - Hearts of Iron 4 Wiki.md>)
- **Graphical**: [Interface](<Interface modding - Hearts of Iron 4 Wiki.md>) • [Graphical assets](<Graphical asset modding - Hearts of Iron 4 Wiki.md>) • [Entities](<Entity modding - Hearts of Iron 4 Wiki.md>) • [Posteffects](<Posteffect modding - Hearts of Iron 4 Wiki.md>) • [Particles](<Particle modding - Hearts of Iron 4 Wiki.md>) • [Fonts](<Font modding - Hearts of Iron 4 Wiki.md>)
- **Cosmetic**: [Portraits](<Portrait modding - Hearts of Iron 4 Wiki.md>) • [Namelists](<Namelist modding - Hearts of Iron 4 Wiki.md>) • [Music](<Music modding - Hearts of Iron 4 Wiki.md>) • [Sound](<Sound modding - Hearts of Iron 4 Wiki.md>)
- **Other**: [Troubleshooting](<Troubleshooting - Hearts of Iron 4 Wiki.md>) • [Mod structure](<Mod structure - Hearts of Iron 4 Wiki.md>) • [Mods](<Mods - Hearts of Iron 4 Wiki.md>) • [Nudger](<Nudger - Hearts of Iron 4 Wiki.md>)

**Hearts of Iron IV**

- **Game**: Achievements • Features • Game rules • Ironman
- **Guides**: Beginner's guide • Hotkeys • Map modes • Tutorial videos • User interface
- **Development**: Developer diaries • Downloadable content • Patches
- **Community**: Jargon • [Modding](<Modding - Hearts of Iron 4 Wiki.md>)
