# Console commands

*Offline snapshot of the Hearts of Iron IV Wiki page "Console commands", captured 2026-09-19.*

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

## List of commands <a id="List_of_commands"></a>

Press Shift+2, §, ~, \\, \`, ", º, ^ or ALT+2+1, or Shift+3 to access the console (key varies based on keyboard layout)

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
