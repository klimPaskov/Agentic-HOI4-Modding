# Table of contents

- [List of commands](#list-of-commands)
  - [Internal IDs](#internal-ids)
  - [Disambiguation](#disambiguation)
  - [Glossary](#glossary)
  - [Useful commands](#useful-commands)
  - [Modding-useful commands](#modding-useful-commands)
  - [Other in-game commands](#other-in-game-commands)
- [See also](#see-also)
- [References](#references)

---

This page lists the codes which may be input into the Console Window, a special debugging window which may be accessed on non-ironman games by hitting `^` , `°` or tilde (~) (key varies based on keyboard layout). Press the up or down arrow keys to traverse through previously executed commands. Many codes can be turned off by repeating the command, but sometimes reloading the save or exiting the game is necessary. Please note that many of these commands come in and out with each DLC making some of them not work. Mods may introduce commands and more commonly, tags into the game to enhance their gameplay.

Also of note, commands may not work in ironman games by design.

## <a id="list-of-commands"></a>List of commands

Press Shift+2, §, ~, \, `, ", º, ^ or ALT+2+1, or Shift+3 to access the console (key varies based on keyboard layout)

### <a id="internal-ids"></a>Internal IDs

*See also: Countries*

Console commands use internal IDs, which may be obtained in a variety of different ways.

An easy way to tell internal IDs is debug mode. `debug` as a console command will turn on debug mode which can provide information about certain database entries, such as focuses, national spirits (and other ideas such as laws or designers), or technologies when hovering over them, as well as obtaining information when hovering over a province of IDs of the state and the province, as well as the 3-letter country tag of the country it belongs to. [Note that while modding, the console command does not do everything that the launch option does and cannot serve as a substitute.](<Modding - Hearts of Iron 4 Wiki.md#advantages-to-using-debug>)

If that is impossible, using localisation is an alternative. To do that, navigate to the folder where the game is contained, then to the /Hearts of Iron IV/localisation/english/ folder. Each file in there contains localisation keys with values that actually appear in-game assigned to them. Using a non-default text editor can also allow using the 'Search in files' function (Such as in Notepad++, Sublime Text, or Visual Studio Code) in order to search through every single localisation file at the same time to find a specified value.

### <a id="disambiguation"></a>Disambiguation

In this article, there are 3 types of brackets used within commands:

- Regular brackets as in `instantconstruction(ic)` are used to show aliases, alternate names for the console commands. In this case, using `ic` or `instantconstruction` has the same effect in-game.
- Square brackets as in `fow [Province ID]` signify an *optional* argument. In this case, both `fow` and `fow 1234` will work, but may have different effects.
- Square brackets in combination with angle brackets as in `event [<event ID>]` signify a *mandatory* argument. In this case, `event generic.1` will work, but `event` will not.

### <a id="glossary"></a>Glossary

MIOs is an acronym for Military Industrial Organizations

### <a id="useful-commands"></a>Useful commands
| Command | Effect | Example/Comment |
| --- | --- | --- |
| <a id="help"></a> help [command name] | Print out all console commands or a specific command description. |  |
| <a id="tag"></a> tag [<Country tag>] | Changes the country that the player controls. |  |
| <a id="event"></a> event [<event id>] [Target country tag] | Executes an event | Event pages can be used to tell the IDs of events. If the event has a `trigger = { ... }` block, it says which triggers were met and which weren't. |
| <a id="finish-decision"></a> finish\_decision [<decision id>] or "all" | Finish timed missions instantly. |  |
| <a id="add-ideas"></a> add\_ideas [<idea name>] | Adds ideas with <id> to the country. Can also replace laws. |  |
| <a id="remove-ideas"></a> remove\_ideas [<idea name>] | Removes national idea. |  |
| <a id="energy-ratio"></a> energy\_ratio (er) [<ratio>] | Set Energy Ratio from 0 to 1 for the factories without coal consumption. |  |
| FI [amount} | Adds to faction initiative | FI 5 adds 5 faction initiative |
| <a id="mastery"></a> mastery [<mastery amount>], [track name] | Give doctrine mastery, globally or to a specific track. |  |
| <a id="gain-xp"></a> gain\_xp [<amount>] | Adds experience to selected Leader/General/Admiral | gain\_xp 100000(level capped at 9) |
| <a id="gain-xp"></a> gain\_xp [<trait>] | Adds **gainable** trait to selected Leader/General/Admiral | ie: gain\_xp seawolf  **Note** To make it work with new, generic created Admirals:  1. Open  *'Documents\Paradox Interactive\Hearts of Iron IV\settings.txt'*  with a text editor and change "save\_as\_binary=yes" to "save\_as\_binary=no".  2. Start game, load savegame and save as new file, exit game.  3. Open  *'Documents\Paradox Interactive\Hearts of iron IV\Save Games'* , open the newly created savegame file, search (CTRL-F) for the name of your generic created Admiral   4. Go a few lines below to **max\_traits=0.000** and add the following code block behind it   `in_progress={ seawolf=0.000 superior_tactician=0.000 spotter=0.000 fly_swatter=0.000 ironside=0.000 air_controller=0.000 }`   5. Make sure to save the file with **ANSI** encoding format.  6. Start game, load save game, use gain\_xp command, enjoy.  (Optional turn back on binarization in settings.txt) |
| <a id="cp"></a> cp [<amount>] | Adds Command Power | cp 100 (capped at 100) |
| <a id="st"></a> st [<amount>] | Adds Stability | st 100 (capped at 100) |
| <a id="add-war-support"></a> add\_war\_support(ws) [<amount>] | Adds War Support | ws 100 (capped at 100) |
| <a id="reduce-opinion"></a> reduce\_opinion [<country tag>] | Reduce opinion to/from tag. |  |
| <a id="allowtraits"></a> allowtraits | Allows free assignment of general traits |  |
| <a id="add-equipment"></a> add\_equipment(ae) [<equipment amount>] [<equipment name>] | Adds equipment | Equipment uses the basic name so 'ae 1000 infantry\_equipment\_1'.You can only add researched equipment. Does not support Naval equipment. (with the exception of convoy: 'ae 1000 convoy\_1') To add ships, consider using instantconstruction(ic) or instanttraining (it) ('ic' or 'it' also effects AI). To add modified equipment, you have to address it by given name. Example: You create a variant of 'Matilda LP'-tank with better Armor and Main Gun and name it 'Matilda LP Mk. IV'. Now use 'add\_equipment 1000 Matilda LP Mk. IV'. |
| <a id="add-latest-equipment"></a> add\_latest\_equipment(ale) [<equipment amount>] | Gives player amount of latest equipment variants | To add only a specific type of your latest equipment, you have to address it's given name. Example: You create a variant of 'Matilda LP'-tank with better Armor and Main Gun and name it 'Matilda LP Mk. IV'. Now use 'add\_latest\_equipment 1000 Matilda LP Mk. IV'. |
| addfunds | Adds funds to all MIOs | Adds 1000 funds to every MIO (military industrial organisation) |
| addTaskCapacity [number] | Adds task capacity to all MIOs | Defaults to 1 if no input given. To add task capacity to only a specific MIO, you will need to find the MIO id in *\Hearts of Iron IV\common\military\_industrial\_organization\organizations\<your country's tag>.txt* Then you use addTaskCapacity [<MIO id>] [number] |
| addSize [number] | Adds trait points to all MIOs | Defaults to 1 if no input given. To add trait points to only a specific MIO, you will need to find the MIO id in *\Hearts of Iron IV\common\military\_industrial\_organization\organizations\<your country's tag>.txt* Then you use addSize [<MIO id>] [number] |
| add\_cic\_bank [number] | Adds Economic Capacity Surplus for the player in the International Market | Defaults to 1 if no input given |
| <a id="whitepeace"></a> whitepeace(wp) [<country tags>] | White peace with the specified countries. |  |
| <a id="teleport"></a> teleport(tp) | Activates the Teleportation tool | Can teleport units where ever you tell them to go (right click a province with a selected unit) |
| <a id="allowdiplo"></a> allowdiplo(adiplo,nocb) | Allows to use all diplomatic actions for no matter the rules. (Can declare war without justification) | This is likely the most effective way of wanting to start a war **without** needing to wait for the justification. If you only want instant justification and not the extra options it comes with, then use (instant\_wargoal). |
| <a id="debug-crash"></a> debug\_crash(crash) | Crashes the game. |  |
| <a id="instantconstruction"></a> instantconstruction (ic) | Toggles instant construction cheat. | Affects AI. Ships are also constructed instantly. |
| <a id="research"></a> research [<slot id> or "all"] | Researches a technology from research slot or all. | Research all will instant research all technologies |
| <a id="research-on-icon-click"></a> research\_on\_icon\_click (roic) | Research a technology when clicking on technology tree icon | Will Allow you to research an item without its prerequisite or two mutually exclusive items |
| <a id="toggle-hidden-techs"></a> toggle\_hidden\_techs (tht) | Toggle show/hide all hidden techs. |  |
| <a id="sp-breakthrough"></a> sp\_breakthrough [<number>] sp\_breakthrough [<number> optional <specialisation>] (sp\_br) | Adds special project breakthrough points for all facilities. | ex: sp\_breakthrough 1 ex: sp\_br 20 specialization\_land  Specialization are: specialization\_land, specialization\_air, specialization\_naval, specialization\_nuclear (For the one added by mod it's in Mod Path\common\special\_projects\specialization) |
| <a id="sp-fast"></a> sp\_fast | Skips the prototyping stage and progresses the iteration stage for special projects |  |
| <a id="sp-instant"></a> sp\_instant | Autocompletes current special projects |  |
| <a id="sp-available"></a> sp\_available | Unlocks/Locks all special projects with unfufilled research prerequisites | E.g. Unlocks nuclear special projects without researching the "Atomic Research" technology |
| <a id="sp-unlock-all"></a> sp\_unlock\_all | All Special Projects are always visible and available. Whether or not the triggers returns true, and whether the parents are completed. |  |
| <a id="sp-research-all"></a> sp\_research\_all (sp\_ra) | Research all special projects. If no scientist exist it will create one, otherwise it will pick an arbitrary one. |  |
| <a id="sp-prototype-reward"></a> sp\_prototype\_reward | Trigger a specified prototype reward during a project. |  |
| <a id="sp-add-scientist"></a> sp\_add\_scientist sp\_add\_scientist [<level> (optional)] [<specialisation> (optional)] | Adds a generic scientist with no or specified specialisation/skill level | sp\_add\_scientist 3 nuclear sp\_add\_scientist 1 |
| sp\_add\_mastermind | Adds a generic scientist with all specialisations and max skill level |  |
| sp\_set\_selected\_scientist\_level [<level>] | Sets scientist's level | The facility view GUI with the assigned scientist must be opened |
| sp\_add\_selected\_scientist\_trait [<trait>] | Adds the specified trait to the scientist | ex: sp\_add\_selected\_scientist\_trait scientist\_trait\_brilliant\_theorist Adds the brilliant scientist trait to the selected scientist. The facility view GUI with the assigned scientist must be opened Traits are found in "Hearts of Iron IV\common\scientist\_traits\00\_traits.txt" |
| <a id="annex"></a> annex [<Target Country Tag> or "all"] | Begin annex/annexes the specified tag | annex USA or annex d01 or annex all |
| <a id="puppet"></a> puppet [<Puppeteer Country Tag>] [<Puppet Target Country Tag>] | Turns the target country into a puppet of the puppeteer | puppet GER CZE (Czechoslovakia becomes a puppet of German Reich) |
| <a id="manpower"></a> manpower [amount] | Adds manpower to player | Defaults to 10 million if the number isn't specified. |
| <a id="add-opinion"></a> add\_opinion [<Country tag>] | Add opinion to/from tag | Adds 100 opinion (hardcoded number) to and from target country (add\_opinion ENG for instance). A successfull call prints "<country> have 100 more opinion about you" and it appears as "cheat\_opinion\_modified\_good" in the diplomacy screen |
| add\_legitimacy [<Country tag>] [<value>] | Adds legitimacy to specified tag. | Example: add\_legitimacy POL 22 |
| <a id="observe"></a> observe(spectator) | Switches to play no country at all, and no longer shows messages or pauses the game. However, it also interferes with AI performance and is not a good indication of what the AI will do if observe mode is not used. |  |
| <a id="tdebug"></a> tdebug | Toggles Debug info | Helpful for finding nation tags and ID's |
| <a id="occupationpaint"></a> occupationpaint(op) | Toggles occupation painting. If used with country tag occupies all of their owned, not controlled, land, | op JAP |
| <a id="setowner"></a> setowner [<country tag>] | Sets state owner | Select the state you would like to set owner as. Select a state by clicking it. You need to click the state as the state id no longer works. |
| <a id="setcontroller"></a> setcontroller [<country tag>] [province id] | Sets province controller |  |
| <a id="xp"></a> xp [<XP amount>] | Gives Army, navy and air experience to player | Can be used once per day |
| <a id="pp"></a> pp(fuhrer\_mana,political\_power) [PP amount] | Gives(or removes) political power to player | Defaults to 1000 if the amount is unset. |
| <a id="fuel"></a> fuel [<amount>] | Adds Fuel | fuel 100000 (capped at your deposits capacity, adding much more will result in decreasing fuel) |
| <a id="civilwar"></a> civilwar [<ideology>] [<target country tag>] | Spawns a civil war | civilwar fascism ENG : Other Valid ideologies "communism" "democratic" "neutrality" |
| <a id="add-party-popularity"></a> add\_party\_popularity <ideology group> <value> | Adds party popularity | ideology group has shortcuts d f n c for vanilla HOI groups. |
| <a id="set-ruling-party"></a> set\_ruling\_party <ideology group> | Sets ruling party | ideology group has shortcuts d f n c for vanilla HOI groups. |
| <a id="focus-autocomplete"></a> Focus.AutoComplete (fa) | Allows national focuses to be instantly finished | Affects AI |
| <a id="focus-nochecks"></a> Focus.NoChecks | Ignores focus requirements | Affects AI |
| <a id="focus-ignoreprerequisites"></a> Focus.IgnorePrerequisites | Ignores focus prerequisites | Allows you to start a focus in the middle of the tree. Affects AI |
| <a id="freefocuses"></a> freefocuses (ff) | Enable freely activating any focuses | Combination of [Focus.AutoComplete (fa)](#focus-autocomplete), [Focus.NoChecks](#focus-nochecks) and [Focus.IgnorePrerequisites](#focus-ignoreprerequisites). |
| <a id="decision-fastremove"></a> Decision.FastRemove | Shortens decisions to 1 day |  |
| <a id="decision-nochecks"></a> Decision.NoChecks | Ignores decision requirements | Also disables cost, affects AI |
| <a id="instant-prepare"></a> instant\_prepare | Instantly prepares naval invasions | Only works in debug mode. |
| <a id="instanttraining"></a> instanttraining (it) | Instantly trains divisions and ships | Affects AI |
| <a id="nuke"></a> nuke [number] | Adds nukes | Add 100 or 1000 |
| <a id="ai-accept"></a> ai\_accept (yesman) | AI will accept all diplomatic offers |  |
| <a id="add-core"></a> add\_core <state\_id> | Adds cores |  |
| <a id="agency-instant"></a> Agency.Instant | Makes everything regarding agencies instant. | Equivalent to a combination of Operation.Instant, IntelNetwork.Instant, Agency.InstantSlotUnlock, and Agency.Autocomplete |
| <a id="agency-instantslotunlock"></a> Agency.InstantSlotUnlock | Removes wait time between agent recruits |  |
| <a id="agency-autocomplete"></a> Agency.Autocomplete | Instantly completes agency upgrades |  |
| <a id="prevent-operative-detection"></a> prevent\_operative\_detection | Your operatives/spies won't be detected anymore |  |
| <a id="force-operative-detection"></a> force\_operative\_detection | Your operatives/spies will be detected |  |
| Operation.instant | Instantly finishes all operations | Affects AI |
| <a id="agency"></a> agency.keepexcessoperatives |  |  |
| <a id="deleteallunits"></a> deleteallunits(delall) [country] | Delete all armies and fleets of the specified countries. | deleteallunits SPR |
| <a id="deleteallunitsbut"></a> deleteallunitsbut(delallbut) [country] | Delete all countries' armies and fleets, with the exception of one country. | delallbut SPR |
| <a id="add-autonomy"></a> add\_autonomy [<Target Country Tag>] [num] | Changes a country's autonomy level | add\_autonomy PHI -200 |
| <a id="resistance"></a> resistance | Increases resistance in the selected province by set amount | ex: (selects one of the provinces in Berlin) resistance 100 |
| <a id="compliance"></a> compliance | Increases compliance in the selected province in game by set amount | ex: (selects one of the provinces in Danzig) compliance 100 |
| add\_intel [<Country tag 1>] [Country Tag 2] [civilian,army,navy,airforce]=[number] add\_intel [<Target Country tag>] [civilian,army,navy,airforce]=[number] | Sets the inputted intel the first tag has against the second tag. The set intel amount is a static value (will be permanent for the rest of the game). | ex (sets intel player has against France to max): add\_intel FRA ex (sets army intel Germany has against USA to 20%): add\_intel GER USA army=20  ex (sets airforce and civilian intel Player has against Japan to 90% and 76% respectively): add\_intel JAP airforce=90 civilian=76 |
| add\_mines | Maximises player owned naval mines in the selected regions |  |
| acclimization [<climate type>] [<number>] | Sets the selected division's acclimization to the specified climate type and its percentage (reduces penalties from cold/hot weather or temperature debuffs) | ex: acclimization cold\_climate 75 ex: acclimization hot\_climate 20 **Note** that it resets the opposite climate type to 0% |
| <a id="debug-smooth"></a> debug\_smooth | Toggle framesmoothing | Can increase game speed significantly, depending on system typically between 10 and 35 percent |

### <a id="modding-useful-commands"></a>Modding-useful commands

Several other commands previously mentioned, such as [event](#event), are useful in modding too.
| Command | Effect | Example/Comment |
| --- | --- | --- |
| <a id="guibounds"></a> guibounds(gui) | Toggles the GUI bounds debug, allowing to test for different window sizes easier. | Also grants the name of the sprite and the interface element the player is hovering on, allowing to find the location of the image by [searching every /Hearts of Iron IV/interface/\*.gfx file at the same time.](<Modding - Hearts of Iron 4 Wiki.md#universal-modding-concepts>) |
| <a id="set-var"></a> set\_var [<variable>] [<value>] | Changes the value of a variable to the specified value. |  |
| <a id="get-var"></a> get\_var [<variable>] | Shows the value of a variable in the console |  |
| <a id="list-vars"></a> list\_vars | Lists the variables set in the selected scope and their values. |  |
| <a id="set-country-flag"></a> set\_country\_flag [<Country Flag>] | Adds a country flag to currently played nation. | Does not work if you put another nations tag in the command such as "set\_country\_flag flag AUS", even if it says in console that it does. |
| <a id="set-global-flag"></a> set\_global\_flag [<Global Flag>] | Adds a global flag. |  |
| <a id="list-flags"></a> list\_flags | Lists currently active flags in the console windows. | Context senstive if nothing (global\_flag), country (country\_flag) or state (state\_flag) is selected when entering this command. |
| <a id="fast-forward"></a> fast\_forward [<amount of days>], [observer] | Fast forward a set amount of days. |  |
| <a id="list-hidden-focuses"></a> list\_hidden\_focuses | Lists all of the hidden focuses from a country. |  |
| <a id="show-focuses"></a> show\_focuses | Shows all the hidden focuses. |  |
| <a id="trigger"></a> trigger [<scripted\_trigger\_name>] | Checks if a scripted trigger is true or not. |  |
| <a id="eval-trigger"></a> eval\_trigger [<trigger code block>] | Checks if the trigger code following the command is true or not, within the currently selected scope. | Example: `eval_trigger OR = { has_completed_focus = GER_remilitarize_the_rhineland has_war_support > 0.5 }` |
| <a id="effect"></a> effect (e) [<scripted\_effect\_name>] | Executes a scripted effect, within the currently selected scope. | Example: `e POL_remove_danzig_effect` on a state will execute that effect on the state. |
| <a id="eval-effect"></a> eval\_effect [<effect code block>] | Executes the effect code following the command, within the currently selected scope. | Example: `eval_effect load_focus_tree = german_focus` would switch the country currently selected to the German focus tree. |
| <a id="ai"></a> ai [country tag...] | Toggles the AI on or off | Without parameters toggles the AI for all countries. With parameters, toggles exceptions for those countries from the general rule. Can be used to confirm if a crash is AI-related. |
| <a id="aiview"></a> aiview | Enable AI debug info |  |
| <a id="human-ai"></a> human\_ai | Makes the AI control the country currently led by the player while the player also remains in control. | AI will also create logs within /Hearts of Iron IV/logs/scripted\_ai.log in the [user directory](<Modding - Hearts of Iron 4 Wiki.md>). |
| <a id="set-cosmetic-tag"></a> set\_cosmetic\_tag [<country tag>] [<cosmetic tag>] | changes the name and flag of the country | set\_cosmetic\_tag USA SOV |
| <a id="reload"></a> reload [<type>] | Reloads files of a given type. Also accepts individual files within the /Hearts of Iron IV/interface/ folder. Equivalent to the effect done automatically when saving over a file with debug mode turned on via launch options. | - reload loc (reloads localisation files) - reload focus (reloads focuses) - reload landcombat.gui (reloads land combat interface) |
| <a id="reloadoob"></a> reloadoob [<Target Country Tag>] | Reloads orders of battle. |  |
| <a id="reloadinterface"></a> reloadinterface | Reloads the entire interface |  |
| <a id="reloadtechnologies"></a> reloadtechnologies | Reloads the technology database |  |
| <a id="updateequipments"></a> updateequipments | Updates the equipment database |  |
| <a id="updatesubunits"></a> updatesubunits | Updates the subunit database |  |
| <a id="update-loc"></a> update\_loc [localization tag] | Updates the localization tag file |  |
| <a id="error"></a> error | Opens the error log file. | If there are special characters in the folder path, this won't work. Equivalent to pressing on the error dog if enabling debug mode in launch options. |
| <a id="imgui"></a> imgui | Controls ImGui UIs. Use `imgui show` to list the available subcommands. These UIs cover a wide variety of useful modding tools, such as script profiling, AI debugging, and listing characters. |  |
| <a id="goto-province"></a> goto\_province [province id] | Moves the camera position to the specified province. |  |
| <a id="goto-state"></a> goto\_state [state id] | Moves the camera position to the specified state. |  |

### <a id="other-in-game-commands"></a>Other in-game commands
| Command | Effect | Example/Comment |
| --- | --- | --- |
| province\_ids (pid) | Show province IDs on the map |  |
| ShowTechBonus | Unknown what it does, however with the name we can make a guess it has to do something with tech bonuses. | Only for developers. |
| normals | Unknown what it does. | Only for developers. |
| <a id="rendertype"></a> rendertype | Reports what render backend is used |  |
| <a id="tweakergui"></a> tweakergui | Spawns a tweaker GUI |  |
| <a id="time"></a> time | What time is it? |  |
| <a id="reloadfx"></a> reloadfx [Arguments: map/mapname/postfx or \*.fx filename] | Reloads the shader |  |
| <a id="particle-editor"></a> particle\_editor | Spawns a particle editor |  |
| <a id="analyzetheatres"></a> analyzetheatres (anth) | Analyze theatres for errors. |  |
| <a id="massconquer"></a> massconquer (massc) | Mass conquer tool. Requires direct province names. | Only for developers. |
| <a id="aircombat"></a> aircombat (airc) [<scenario name>] [<result name>] [<province id>] [<state id with airbase>] [<state id with airbase>] [<equipment type>] [<equipment type>] [<equipment creator country>] [<equipment creator country>] | Spawns an air combat in desired location. | Only for developers. |
| <a id="fronts"></a> fronts | Toggle visibility of the foreign fronts |  |
| <a id="ai-front-dump"></a> ai\_front\_dump (aifrontdump) | Dump AI front data to log file, needs to have a unit selected |  |
| <a id="traderoutes"></a> traderoutes | Toggle visibility of trade routes |  |
| <a id="debug-tactics"></a> debug\_tactics | Toggle visibility of debug tooltip for tactics |  |
| <a id="reloadsupply"></a> reloadsupply (relsup) | Reinitializes the supply systems. |  |
| <a id="deltat"></a> deltat [<speed factor>] | control animation speeds |  |
| <a id="building-health"></a> building\_health (bhealth) [<building type>] [<state or prov id>] [<building level>] [<health to add>] | Changes specified building health |  |
| <a id="nomapicons"></a> nomapicons | Toggles map icons. |  |
| <a id="nopausetext"></a> nopausetext | Toggles the pausebanner for nicer screenshots. |  |
| <a id="nextsong"></a> nextsong | Changes the currently playing soundtrack. |  |
| <a id="combatsound"></a> combatsound | How often does the combat view give a random sound? 0-50 |  |
| <a id="morehumans"></a> morehumans (humans) [num] | Adds more humans |  |
| <a id="window"></a> window (wnd) [Arguments: open/close] [window gui name] | Opens or closes the specified window |  |
| <a id="poll"></a> poll | Polls valid Events |  |
| <a id="pause-in-hours"></a> pause\_in\_hours | Pauses the game after X hours have passed after command is called |  |
| <a id="winwars"></a> winwars | Gives max war score in all wars for the country | Command no longer exists as of patch 1.9.1 |
| <a id="testevent"></a> testevent [<Event ID>] [<Character ID>] | Tests an event without triggering it |  |
| <a id="resign"></a> resign | Resign from the game |  |
| <a id="add-interest"></a> add\_interest [<Country tag>] | Add specified country tag to your interest |  |
| <a id="remove-interest"></a> remove\_interest [<Country tag>] | Removes specified country tag from your interest |  |
| <a id="add-diplo"></a> add\_diplo | Adds diplomatic entroute |  |
| <a id="printsynchstuff"></a> PrintSynchStuff | Prints random count and seed |  |
| <a id="setrandomcount"></a> SetRandomCount | Sets the random count to 0 or arg |  |
| <a id="ai-invasion"></a> ai\_invasion | Toggles AI AI naval invasions |  |
| <a id="ai-pp-log"></a> ai\_pp\_log | Prints AI use of PP to log |  |
| <a id="ai-idea-desire-log"></a> ai\_idea\_desire\_log | Prints AI desire for ideas to log. For current country only |  |
| <a id="ai-force-template"></a> ai\_force\_template | Force the AI to only spend army XP on template design |  |
| <a id="ai-force-equipment"></a> ai\_force\_equipment | Force the AI to only spend army XP on equipment design |  |
| <a id="ai-front-id"></a> ai\_front\_id | Get the address of selected group's front debug ID |  |
| <a id="fow"></a> fow (debug\_fow) [Province ID] | Turns off fog of war, only within a province if specified. |  |
| <a id="collision"></a> collision (debug\_collision) | Toggles debug display of normals/bounding boxes/collision |  |
| <a id="savegame"></a> savegame | Creates a savefile. |  |
| <a id="savecheck"></a> savecheck | Makes a save file (Test\_01), loads the save file, makes a new savegame (Test\_02). Those save files should look the same. |  |
| <a id="ip"></a> IP | Shows your IP |  |
| <a id="requestgamestate"></a> requestgamestate | Requests the gamestate from host |  |
| <a id="nudge"></a> nudge | Go to the nudge tool |  |
| <a id="mapmode"></a> mapmode [Mapmode type (int)] | Change mapmode. |  |
| <a id="fullscreen"></a> fullscreen | Toggles fullscreen |  |
| <a id="prices"></a> prices | Price Info |  |
| <a id="remove-core"></a> remove\_core [<State ID>] [<Country Tag>] | Remove core. | Command does not work |
| <a id="debug-zoom"></a> debug\_zoom | Zooms in the game |  |
| <a id="debug-types"></a> debug\_types | Will print the data type for all dynamic reference objects. Can only be used if using RTTI. |  |
| <a id="debug-show-event-id"></a> debug\_show\_event\_ID | Shows event ID |  |
| <a id="debug-commands"></a> debug\_commands | Printing commandcount to message.log |  |
| <a id="debug-events"></a> debug\_events | Start Counting events |  |
| <a id="debug-dumpevents"></a> debug\_dumpevents | Dump Event data to game log |  |
| <a id="debug-diploactions"></a> debug\_diploactions | Start Counting diplomatic actions |  |
| <a id="debug-dumpdiploactions"></a> debug\_dumpdiploactions | Dump diplomatic action data to game log |  |
| <a id="debug-assert"></a> debug\_assert | Toggles asserts on/off |  |
| <a id="debug-nomouse"></a> debug\_nomouse | Toggles mouse scrollwheel on/off |  |
| <a id="debug-terrain"></a> debug\_terrain | Toggles Terrain on/off |  |
| <a id="debug-cities"></a> debug\_cities | Toggles Cities painting mode on/off |  |
| <a id="debug-water"></a> debug\_water | Toggles Water on/off |  |
| <a id="debug-fronts"></a> debug\_fronts | Toggles interpolated fronts debug |  |
| <a id="debug-off-front-snap"></a> debug\_off\_front\_snap (dbg\_fsnap) | Toggles offensive fronts snapping debug |  |
| <a id="debug-borders"></a> debug\_borders | Toggles Borders on/off |  |
| <a id="debug-trees"></a> debug\_trees | Toggles Trees on/off |  |
| <a id="debug-rivers"></a> debug\_rivers | Toggles Rivers on/off |  |
| <a id="debug-postfx"></a> debug\_postfx | Toggles PostFX on/off |  |
| <a id="debug-sky"></a> debug\_sky | Toggles Sky on/off |  |
| <a id="debug-bloom"></a> debug\_bloom | Toggles Bloom on/off |  |
| <a id="debug-tooltip"></a> debug\_tooltip | Toggles Tooltips on/off |  |
| debug\_nuking | Allows to nuke every province without checking any conditions. | Command no longer exists as of patch 1.15.1 |
| <a id="flagsoutput"></a> flagsoutput [<path>] | Creates texture atlas files from memory. |  |
| <a id="cityreload"></a> cityreload | Reloads the cities |  |
| <a id="version"></a> version | Show current game version |  |
| <a id="debug-nogui"></a> debug\_nogui | Toggles GUI on/off |  |
| <a id="debug-volume"></a> debug\_volume [<Volume Delta>] | Modifies music volume |  |
| <a id="debug-lockcamera"></a> debug\_lockcamera | Toggles Camera locked on/off |  |
| <a id="debug-lines"></a> debug\_lines | Toggles Debuglines |  |
| <a id="debug-entities"></a> debug\_entities | Toggles Debug entities |  |
| <a id="debug-info"></a> debug\_info | Toggles Debug info |  |
| <a id="debug-particle"></a> debug\_particle | Toggles Particles Debug info |  |
| <a id="debug-ai-budget"></a> debug\_ai\_budget [CountryTag] | Show ai budget data |  |
| <a id="debug-textures"></a> debug\_textures | Writes Texture info to application debug log |  |
| <a id="debug-texture"></a> debug\_texture | draws textures like bloom |  |
| <a id="debug-wireframe"></a> debug\_wireframe | Toggles forced wireframe on/off |  |
| <a id="debug-achievements-clear"></a> debug\_achievements\_clear | Clear all achievements and user stats | Only for developers. |
| <a id="moveunit"></a> moveunit [<Unit ID>] [<Province ID>] | Moves a unit to a province |  |
| <a id="spawnactor"></a> spawnactor [<Actorname>] [<Province ID>] [<Animation> OPTIONAL] | Spawns an actor with an optional animation |  |
| <a id="cameraclamp"></a> cameraclamp | Toggles the camera clamping |  |
| <a id="provtooltipdebug"></a> provtooltipdebug (tdebug) | Toggles the debug info in province tooltip |  |
| <a id="reloadweather"></a> reloadweather [<randomseed>] | Reload and regenerate weather |  |
| <a id="weather"></a> weather | Toggle weather simulation |  |
| <a id="debug-air-vs-land"></a> debug\_air\_vs\_land (dbg\_cas) | Toggle debug mode for air vs land combat. |  |
| <a id="mapnames"></a> mapnames | Toggle map names |  |
| <a id="gbreload"></a> gbreload | Reloads gradient borders | Only for developers. |
| <a id="gbpaint"></a> gbpaint [layer] [channel] | Toggles gradient border painting |  |
| <a id="profilelog"></a> profilelog | Prints out the profiling informations into time.log |  |
| <a id="run"></a> run | Runs the specified file with list of commands |  |
| <a id="oos"></a> oos | Out of Synch | Only for developers. |
| <a id="trigger-docs"></a> trigger\_docs (effect\_docs, scripting\_docs, docs) | Print docs for triggers, effects, and variables | Documentation for triggers/effects printed to game.log file |
| <a id="threat"></a> threat [Threat amount] | Adds or show threat level of the current tag, which is the world tension generated by the tag. | Positive values will add to the world tension generated by the active tag, while negative values will subtract from the world tension generated by the active tag, with corresponding entries in the world tension history log. By tag-switching, it is possible to raise or lower the world tension generated by any particular country. If one does "threat 999999999" it will reset the world tension to 0. |
| <a id="3dstats"></a> 3dstats | Toggles 3D Stats |  |
| <a id="hdr"></a> hdr | Toggles hdr |  |
| <a id="hdr-debug"></a> hdr\_debug | Toggles hdr debugging |  |
| <a id="srgb"></a> srgb | Toggles sRGB |  |
| <a id="bloom"></a> bloom | Toggles bloom |  |
| <a id="posteffectvolumes-default"></a> PostEffectVolumes.Default [posteffect\_values name] | Toggles default posteffect values |  |
| <a id="night"></a> night | Toggles night | \*as of 1.01 this does not seem to work (filed under developer-only command) This command can be emulated via the day/night loop option at the bottom right toolbar (shortcut key 'N') |
| <a id="filewatcher"></a> filewatcher | Toggles filewatcher |  |
| <a id="createlean"></a> createlean | Create LEAN textures |  |
| <a id="helplog"></a> helplog | Print out all console commands to game.log file. |  |
| <a id="helphelp"></a> helphelp | Double Rainbow help. |  |
| <a id="hsv"></a> hsv | Converts RGB to HSV |  |
| <a id="tag-color"></a> tag\_color | Test setting a country's color |  |
| <a id="browser"></a> browser [url] | Show browser window |  |
| <a id="browser-base-url"></a> browser\_base\_url [url] | Set browser base url |  |
| <a id="airealism"></a> airealism | Enable realistic AI | An easter egg making the AI smacktalk in chats. Useless since unactivable in multiplayer and chat unactivable in singleplayer.<a id="cite-ref-1"></a>[[1]](#cite-note-1) |
| <a id="instant-wargoal"></a> instant\_wargoal | Will allow instant justificatiion of war goals on countries |  |
| <a id="allowideas"></a> allowideas | Allows the player to pick any idea even if normally unavailable | This overrides the `available` and `visible` triggers of ideas, but not the `allowed` trigger |
| <a id="release"></a> release [<country tag>] | Releases a country or releasable nation | release slv releases Slovenia |
| InternationalMarket.AddSubsidyForTags [<economic capacity>] [<equipment>] [<country tag>] | Adds a subsidy for the player to buy off from a specified country. | ex (Adds a subsidy for the player to be able to help buy German sold light tanks for up to 5k EC): InternationalMarket.AddSubsidyForTags 5000 light\_tank\_chassis GER |
| random\_seed | Randomises the current seed the game is using | The AI uses this seed to decide all their focuses and decisions. You can use this to generate a more favourable outcome to any ai action you dislike (e.g. you want to ally with country) |
| eval\_effect [<country tag>] = { create\_faction = "[faction name]" } | Creates a faction with a specified name | The leader of the faction will be the inserted country tag |
| eval\_effect [<country tag>] = { dismantle\_faction = yes } | Deletes the faction of specified country |  |
| eval\_effect [<country tag>] = { add\_to\_faction = [<country tag>] } | Adds a country to a faction | The second tag is the country which will join the first tag's faction |
| eval\_effect [<country tag>] = { remove\_from\_faction = [<country tag>] } | Removes a country from a faction | The second tag is the country which will join the first tag's faction |
| eval\_effect [<country tag>] = { set\_faction\_name = "[faction name]" } | Renames the faction of the specified country |  |
| toggle\_silhouette\_portraits | Enables and disables silhouette portraits. | Only for developers. |

## <a id="see-also"></a>See also

- [Modding](<Modding - Hearts of Iron 4 Wiki.md>)

## <a id="references"></a>References

<a id="cite-note-1"></a>1. [↑](#cite-ref-1) A comment of podcat about the command been found <https://www.reddit.com/r/hoi4/comments/6cb8vh/the_secrets_of_hoi4/dhtdr4x/>

**Hearts of Iron IV**
|  |  |
| --- | --- |
| Game | Achievements • Features • Game rules • Ironman |
|  |  |
| --- | --- |
| Guides | Beginner's guide • Console commands • Hotkeys • Map modes • Tutorial videos • User interface |
|  |  |
| --- | --- |
| Development | Developer diaries • Downloadable content • Patches |
|  |  |
| --- | --- |
| Community | Jargon • [Modding](<Modding - Hearts of Iron 4 Wiki.md>) |

**[Modding](<Modding - Hearts of Iron 4 Wiki.md>)**
