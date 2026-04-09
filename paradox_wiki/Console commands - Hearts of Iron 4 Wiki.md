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

## List of commands

Press Shift+2, §, ~, \, `, ", ^ or ALT+2+1, or Shift+3 to access the console (key varies based on keyboard layout)

### Internal IDs

*See also: Countries*

Console commands use internal IDs, which may be obtained in a variety of different ways.

An easy way to tell internal IDs is debug mode. `debug` as a console command will turn on debug mode which can provide information about certain database entries, such as focuses, national spirits (and other ideas such as laws or designers), or technologies when hovering over them, as well as obtaining information when hovering over a province of IDs of the state and the province, as well as the 3-letter country tag of the country it belongs to. [Note that while modding, the console command does not do everything that the launch option does and cannot serve as a substitute.](<Modding - Hearts of Iron 4 Wiki.md#advantages-to-using-debug>)

If that is impossible, using localisation is an alternative. To do that, navigate to the folder where the game is contained, then to the /Hearts of Iron IV/localisation/english/ folder. Each file in there contains localisation keys with values that actually appear in-game assigned to them. Using a non-default text editor can also allow using the 'Search in files' function (Such as in Notepad++, Sublime Text, or Visual Studio Code) in order to search through every single localisation file at the same time to find a specified value.

### Disambiguation

In this article, there are 3 types of brackets used within commands:

- Regular brackets as in `instantconstruction(ic)` are used to show aliases, alternate names for the console commands. In this case, using `ic` or `instantconstruction` has the same effect in-game.
- Square brackets as in `fow [Province ID]` signify an *optional* argument. In this case, both `fow` and `fow 1234` will work, but may have different effects.
- Square brackets in combination with angle brackets as in `event [<event ID>]` signify a *mandatory* argument. In this case, `event generic.1` will work, but `event` will not.

### Glossary

MIOs is an acronym for Military Industrial Organizations

### Useful commands

- **help [command name]**
  - Effect: Print out all console commands or a specific command description.

- **tag [<Country tag>]**
  - Effect: Changes the country that the player controls.

- **event [<event id>] [Target country tag]**
  - Effect: Executes an event
  - Example/Comment:
    ```text
    Event pages
    can be used to tell the IDs of events. If the event has a
    trigger = { ... }
    block, it says which triggers were met and which weren't.
    ```

- **finish_decision [<decision id>] or "all"**
  - Effect: Finish timed missions instantly.

- **add_ideas [<idea name>]**
  - Effect: Adds ideas with <id> to the country

- **remove_ideas [<idea name>]**
  - Effect: Removes national idea.

- **energy_ratio (er) [<ratio>]**
  - Effect: Set Energy Ratio from 0 to 1 for the factories without coal consumption.

- **FI [amount}**
  - Effect: Adds to faction initiative
  - Example/Comment: FI 5 adds 5 faction initiative

- **mastery [<mastery amount>], [track name]**
  - Effect: Give doctrine mastery, globally or to a specific track.

- **gain_xp [<amount>]**
  - Effect: Adds experience to selected Leader/General/Admiral
  - Example/Comment: gain_xp 100000(level capped at 9)

- **gain_xp [<trait>]**
  - Effect:
    ```text
    Adds
    gainable
    trait to selected Leader/General/Admiral
    ```
  - Example/Comment:
    ```text
    ie: gain_xp seawolf
    Note
    To make it work with new, generic created Admirals:
    1. Open
    'Documents\Paradox Interactive\Hearts of Iron IV\settings.txt'
    with a text editor and change "save_as_binary=yes" to "save_as_binary=no".
    2. Start game, load savegame and save as new file, exit game.
    3. Open
    'Documents\Paradox Interactive\Hearts of iron IV\Save Games'
    , open the newly created savegame file, search (CTRL-F) for the name of your generic created Admiral
    4. Go a few lines below to
    max_traits=0.000
    and add the following code block behind it
    5. Make sure to save the file with
    ANSI
    encoding format.
    6. Start game, load save game, use gain_xp command, enjoy.
    (Optional turn back on binarization in settings.txt)
    ```
  - Example:
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

- **cp [<amount>]**
  - Effect: Adds Command Power
  - Example/Comment: cp 100 (capped at 100)

- **st [<amount>]**
  - Effect: Adds Stability
  - Example/Comment: st 100 (capped at 100)

- **add_war_support(ws) [<amount>]**
  - Effect: Adds War Support
  - Example/Comment: ws 100 (capped at 100)

- **reduce_opinion [<country tag>]**
  - Effect: Reduce opinion to/from tag.

- **allowtraits**
  - Effect: Allows free assignment of general traits

- **add_equipment(ae) [<equipment amount>] [<equipment name>]**
  - Effect: Adds equipment
  - Example/Comment:
    ```text
    Equipment uses the basic name so 'ae 1000 infantry_equipment_1'.You can only add researched equipment. Does not support Naval equipment. (with the exception of convoy: 'ae 1000 convoy_1') To add ships, consider using instantconstruction(ic) or instanttraining (it) ('ic' or 'it' also effects AI).
    To add modified equipment, you have to address it by given name. Example: You create a variant of 'Matilda LP'-tank with better Armor and Main Gun and name it 'Matilda LP Mk. IV'.
    Now use 'add_equipment 1000 Matilda LP Mk. IV'.
    ```

- **add_latest_equipment(ale) [<equipment amount>]**
  - Effect: Gives player amount of latest equipment variants
  - Example/Comment:
    ```text
    To add only a specific type of your latest equipment, you have to address it's given name. Example: You create a variant of 'Matilda LP'-tank with better Armor and Main Gun and name it 'Matilda LP Mk. IV'.
    Now use 'add_latest_equipment 1000 Matilda LP Mk. IV'.
    ```

- **addfunds**
  - Effect: Adds funds to all MIOs
  - Example/Comment: Adds 1000 funds to every MIO (military industrial organisation)

- **addTaskCapacity [number]**
  - Effect: Adds task capacity to all MIOs
  - Example/Comment:
    ```text
    Defaults to 1 if no input given.
    To add task capacity to only a specific MIO, you will need to find the MIO id in
    \Hearts of Iron IV\common\military_industrial_organization\organizations\<your country's tag>.txt
    Then you use addTaskCapacity [<MIO id>] [number]
    ```

- **addSize [number]**
  - Effect: Adds trait points to all MIOs
  - Example/Comment:
    ```text
    Defaults to 1 if no input given.
    To add trait points to only a specific MIO, you will need to find the MIO id in
    \Hearts of Iron IV\common\military_industrial_organization\organizations\<your country's tag>.txt
    Then you use addSize [<MIO id>] [number]
    ```

- **add_cic_bank [number]**
  - Effect: Adds Economic Capacity Surplus for the player in the International Market
  - Example/Comment: Defaults to 1 if no input given

- **whitepeace(wp) [<country tags>]**
  - Effect: White peace with the specified countries.

- **teleport(tp)**
  - Effect: Activates the Teleportation tool
  - Example/Comment: Can teleport units where ever you tell them to go (right click a province with a selected unit)

- **allowdiplo(adiplo,nocb)**
  - Effect: Allows to use all diplomatic actions for no matter the rules. (Can declare war without justification)
  - Example/Comment:
    ```text
    This is likely the most effective way of wanting to start a war
    without
    needing to wait for the justification. If you only want instant justification and not the extra options it comes with, then use (instant_wargoal).
    ```

- **debug_crash(crash)**
  - Effect: Crashes the game.

- **instantconstruction (ic)**
  - Effect: Toggles instant construction cheat.
  - Example/Comment: Affects AI. Ships are also constructed instantly.

- **research [<slot id> or "all"]**
  - Effect: Researches a technology from research slot or all.
  - Example/Comment: Research all will instant research all technologies

- **research_on_icon_click (roic)**
  - Effect: Research a technology when clicking on technology tree icon
  - Example/Comment: Will Allow you to research an item without its prerequisite or two mutually exclusive items

- **toggle_hidden_techs (tht)**
  - Effect: Toggle show/hide all hidden techs.

- **sp_breakthrough [<number>]**
  - Effect: Adds special project breakthrough points for all facilities.
  - Example/Comment:
    ```text
    ex: sp_breakthrough 1
    ex: sp_br 20 specialization_land
    Specialization are: specialization_land, specialization_air, specialization_naval, specialization_nuclear (For the one added by mod it's in Mod Path\common\special_projects\specialization)
    ```

- **sp_fast**
  - Effect: Skips the prototyping stage and progresses the iteration stage for special projects

- **sp_instant**
  - Effect: Autocompletes current special projects

- **sp_available**
  - Effect: Unlocks/Locks all special projects with unfufilled research prerequisites
  - Example/Comment: E.g. Unlocks nuclear special projects without researching the "Atomic Research" technology

- **sp_unlock_all**
  - Effect: All Special Projects are always visible and available. Whether or not the triggers returns true, and whether the parents are completed.

- **sp_research_all (sp_ra)**
  - Effect: Research all special projects. If no scientist exist it will create one, otherwise it will pick an arbitrary one.

- **sp_prototype_reward**
  - Effect: Trigger a specified prototype reward during a project.

- **sp_add_scientist**
  - Effect: Adds a generic scientist with no or specified specialisation/skill level
  - Example/Comment:
    ```text
    sp_add_scientist 3 nuclear
    sp_add_scientist 1
    ```

- **sp_add_mastermind**
  - Effect: Adds a generic scientist with all specialisations and max skill level

- **sp_set_selected_scientist_level [<level>]**
  - Effect: Sets scientist's level
  - Example/Comment: The facility view GUI with the assigned scientist must be opened

- **sp_add_selected_scientist_trait [<trait>]**
  - Effect: Adds the specified trait to the scientist
  - Example/Comment:
    ```text
    ex: sp_add_selected_scientist_trait scientist_trait_brilliant_theorist
    Adds the brilliant scientist trait to the selected scientist. The facility view GUI with the assigned scientist must be opened Traits are found in "Hearts of Iron IV\common\scientist_traits\00_traits.txt"
    ```

- **annex [<Target Country Tag> or "all"]**
  - Effect: Begin annex/annexes the specified tag
  - Example/Comment: annex USA or annex d01 or annex all

- **puppet [<Puppeteer Country Tag>] [<Puppet Target Country Tag>]**
  - Effect: Turns the target country into a puppet of the puppeteer
  - Example/Comment: puppet GER CZE (Czechoslovakia becomes a puppet of German Reich)

- **manpower [amount]**
  - Effect: Adds manpower to player
  - Example/Comment: Defaults to 10 million if the number isn't specified.

- **add_opinion [<Country tag>]**
  - Effect: Add opinion to/from tag
  - Example/Comment: Adds 100 opinion (hardcoded number) to and from target country (add_opinion ENG for instance). A successfull call prints "<country> have 100 more opinion about you" and it appears as "cheat_opinion_modified_good" in the diplomacy screen

- **add_legitimacy [<Country tag>] [<value>]**
  - Effect: Adds legitimacy to specified tag.
  - Example/Comment: Example: add_legitimacy POL 22

- **observe(spectator)**
  - Effect: Switches to play no country at all, and no longer shows messages or pauses the game. However, it also interferes with AI performance and is not a good indication of what the AI will do if observe mode is not used.

- **tdebug**
  - Effect: Toggles Debug info
  - Example/Comment: Helpful for finding nation tags and ID's

- **occupationpaint(op)**
  - Effect: Toggles occupation painting. If used with country tag occupies all of their owned, not controlled, land,
  - Example/Comment: op JAP

- **setowner [<country tag>]**
  - Effect: Sets state owner
  - Example/Comment: Select the state you would like to set owner as. Select a state by clicking it. You need to click the state as the state id no longer works.

- **setcontroller [<country tag>] [province id]**
  - Effect: Sets province controller

- **xp [<XP amount>]**
  - Effect: Gives Army, navy and air experience to player
  - Example/Comment: Can be used once per day

- **pp(fuhrer_mana,political_power) [PP amount]**
  - Effect: Gives(or removes) political power to player
  - Example/Comment: Defaults to 1000 if the amount is unset.

- **fuel [<amount>]**
  - Effect: Adds Fuel
  - Example/Comment: fuel 100000 (capped at your deposits capacity, adding much more will result in decreasing fuel)

- **civilwar [<ideology>] [<target country tag>]**
  - Effect: Spawns a civil war
  - Example/Comment:
    ```text
    civilwar fascism ENG :
    Other Valid ideologies "communism" "democratic" "neutrality"
    ```

- **add_party_popularity <ideology group> <value>**
  - Effect: Adds party popularity
  - Example/Comment: ideology group has shortcuts d f n c for vanilla HOI groups.

- **set_ruling_party <ideology group>**
  - Effect: Sets ruling party
  - Example/Comment: ideology group has shortcuts d f n c for vanilla HOI groups.

- **Focus.AutoComplete (fa)**
  - Effect: Allows national focuses to be instantly finished
  - Example/Comment: Affects AI

- **Focus.NoChecks**
  - Effect: Ignores focus requirements
  - Example/Comment: Affects AI

- **Focus.IgnorePrerequisites**
  - Effect: Ignores focus prerequisites
  - Example/Comment: Allows you to start a focus in the middle of the tree. Affects AI

- **freefocuses (ff)**
  - Effect: Enable freely activating any focuses
  - Example/Comment:
    ```text
    Combination of
    Focus.AutoComplete (fa)
    ,
    Focus.NoChecks
    and
    Focus.IgnorePrerequisites
    .
    ```

- **Decision.FastRemove**
  - Effect: Shortens decisions to 1 day

- **Decision.NoChecks**
  - Effect: Ignores decision requirements
  - Example/Comment: Also disables cost, affects AI

- **instant_prepare**
  - Effect: Instantly prepares naval invasions
  - Example/Comment: Only works in debug mode.

- **instanttraining (it)**
  - Effect: Instantly trains divisions and ships
  - Example/Comment: Affects AI

- **nuke [number]**
  - Effect: Adds nukes
  - Example/Comment: Add 100 or 1000

- **ai_accept**
  - Effect: AI will accept all diplomatic offers

- **add_core <state_id>**
  - Effect: Adds cores

- **Agency.Instant**
  - Effect: Makes everything regarding agencies instant.
  - Example/Comment: Equivalent to a combination of Operation.Instant, IntelNetwork.Instant, Agency.InstantSlotUnlock, and Agency.Autocomplete

- **Agency.InstantSlotUnlock**
  - Effect: Removes wait time between agent recruits

- **Agency.Autocomplete**
  - Effect: Instantly completes agency upgrades

- **prevent_operative_detection**
  - Effect: Your operatives/spies won't be detected anymore

- **force_operative_detection**
  - Effect: Your operatives/spies will be detected

- **Operation.instant**
  - Effect: Instantly finishes all operations
  - Example/Comment: Might affect ai

- **agency.keepexcessoperatives**

- **deleteallunits(delall) [country]**
  - Effect: Delete all armies and fleets of the specified countries.
  - Example/Comment: deleteallunits SPR

- **deleteallunitsbut(delallbut) [country]**
  - Effect: Delete all countries' armies and fleets, with the exception of one country.
  - Example/Comment: delallbut SPR

- **add_autonomy [<Target Country Tag>] [num]**
  - Effect: Changes a country's autonomy level
  - Example/Comment: add_autonomy PHI -200

- **resistance**
  - Effect: Increases resistance in the selected province by set amount
  - Example/Comment: ex: (selects one of the provinces in Berlin) resistance 100

- **compliance**
  - Effect: Increases compliance in the selected province in game by set amount
  - Example/Comment: ex: (selects one of the provinces in Danzig) compliance 100

- **add_intel [<Country tag 1>] [Country Tag 2] [civilian,army,navy,airforce]=[number]**
  - Effect: Sets the inputted intel the first tag has against the second tag. The set intel amount is a static value (will be permanent for the rest of the game).
  - Example/Comment:
    ```text
    ex (sets intel player has against France to max): add_intel FRA
    ex (sets army intel Germany has against USA to 20%): add_intel GER USA army=20
    ex (sets airforce and civilian intel Player has against Japan to 90% and 76% respectively): add_intel JAP airforce=90 civilian=76
    ```

- **add_mines**
  - Effect: Maximises player owned naval mines in the selected regions

- **acclimization [<climate type>] [<number>]**
  - Effect: Sets the selected division's acclimization to the specified climate type and its percentage (reduces penalties from cold/hot weather or temperature debuffs)
  - Example/Comment:
    ```text
    ex: acclimization cold_climate 75
    ex: acclimization hot_climate 20
    Note
    that it resets the opposite climate type to 0%
    ```

- **debug_smooth**
  - Effect: Toggle framesmoothing
  - Example/Comment: Can increase game speed significantly, depending on system typically between 10 and 35 percent

### Modding-useful commands

Several other commands previously mentioned, such as [event](#event), are useful in modding too.

- **guibounds(gui)**
  - Effect: Toggles the GUI bounds debug, allowing to test for different window sizes easier.
  - Example/Comment:
    ```text
    Also grants the name of the sprite and the interface element the player is hovering on, allowing to find the location of the image by
    searching every
    /Hearts of Iron IV/interface/*.gfx
    file at the same time.
    ```

- **set_var [<variable>] [<value>]**
  - Effect: Changes the value of a variable to the specified value.

- **get_var [<variable>]**
  - Effect: Shows the value of a variable in the console

- **list_vars**
  - Effect: Lists the variables set in the selected scope and their values.

- **set_country_flag [<Country Flag>]**
  - Effect: Adds a country flag to currently played nation.
  - Example/Comment: Does not work if you put another nations tag in the command such as "set_country_flag flag AUS", even if it says in console that it does.

- **set_global_flag [<Global Flag>]**
  - Effect: Adds a global flag.

- **list_flags**
  - Effect: Lists currently active flags in the console windows.
  - Example/Comment: Context senstive if nothing (global_flag), country (country_flag) or state (state_flag) is selected when entering this command.

- **fast_forward [<amount of days>], [observer]**
  - Effect: Fast forward a set amount of days.

- **list_hidden_focuses**
  - Effect: Lists all of the hidden focuses from a country.

- **show_focuses**
  - Effect: Shows all the hidden focuses.

- **trigger [<scripted_trigger_name>]**
  - Effect: Checks if a scripted trigger is true or not.

- **eval_trigger [<trigger code block>]**
  - Effect: Checks if the trigger code following the command is true or not, within the currently selected scope.
  - Example/Comment:
    ```text
    Example:
    eval_trigger OR = { has_completed_focus = GER_remilitarize_the_rhineland has_war_support > 0.5 }
    ```

- **effect (e) [<scripted_effect_name>]**
  - Effect:
    ```text
    Executes a
    scripted effect
    , within the currently selected scope.
    ```
  - Example/Comment:
    ```text
    Example:
    e POL_remove_danzig_effect
    on a state will execute that effect on the state.
    ```

- **eval_effect [<effect code block>]**
  - Effect: Executes the effect code following the command, within the currently selected scope.
  - Example/Comment:
    ```text
    Example:
    eval_effect load_focus_tree = german_focus
    would switch the country currently selected to the German focus tree.
    ```

- **ai [country tag...]**
  - Effect: Toggles the AI on or off
  - Example/Comment: Without parameters toggles the AI for all countries. With parameters, toggles exceptions for those countries from the general rule. Can be used to confirm if a crash is AI-related.

- **aiview**
  - Effect: Enable AI debug info

- **human_ai**
  - Effect: Makes the AI control the country currently led by the player while the player also remains in control.
  - Example/Comment:
    ```text
    AI will also create logs within
    /Hearts of Iron IV/logs/scripted_ai.log
    in the
    user directory
    .
    ```

- **set_cosmetic_tag [<country tag>] [<cosmetic tag>]**
  - Effect: changes the name and flag of the country
  - Example/Comment: set_cosmetic_tag USA SOV

- **reload [<type>]**
  - Effect:
    ```text
    Reloads files of a given type. Also accepts individual files within the
    /Hearts of Iron IV/interface/
    folder. Equivalent to the effect done automatically when saving over a file with debug mode turned on via launch options.
    ```
  - Example/Comment:
    ```text
    reload loc (reloads localisation files)
    reload focus (reloads focuses)
    reload landcombat.gui (reloads land combat interface)
    ```

- **reloadoob [<Target Country Tag>]**
  - Effect: Reloads orders of battle.

- **reloadinterface**
  - Effect: Reloads the entire interface

- **reloadtechnologies**
  - Effect: Reloads the technology database

- **updateequipments**
  - Effect: Updates the equipment database

- **updatesubunits**
  - Effect: Updates the subunit database

- **update_loc [localization tag]**
  - Effect: Updates the localization tag file

- **error**
  - Effect: Opens the error log file.
  - Example/Comment: If there are special characters in the folder path, this won't work. Equivalent to pressing on the error dog if enabling debug mode in launch options.

- **imgui**
  - Effect:
    ```text
    Controls ImGui UIs. Use
    imgui show
    to list the available subcommands. These UIs cover a wide variety of useful modding tools, such as script profiling, AI debugging, and listing characters.
    ```

- **goto_province [province id]**
  - Effect: Moves the camera position to the specified province.

- **goto_state [state id]**
  - Effect: Moves the camera position to the specified state.

### Other in-game commands

- **province_ids (pid)**
  - Effect: Show province IDs on the map

- **ShowTechBonus**
  - Effect: Unknown what it does, however with the name we can make a guess it has to do something with tech bonuses.
  - Example/Comment: Only for developers.

- **normals**
  - Effect: Unknown what it does.
  - Example/Comment: Only for developers.

- **rendertype**
  - Effect: Reports what render backend is used

- **tweakergui**
  - Effect: Spawns a tweaker GUI

- **time**
  - Effect: What time is it?

- **reloadfx [Arguments: map/mapname/postfx or *.fx filename]**
  - Effect: Reloads the shader

- **particle_editor**
  - Effect: Spawns a particle editor

- **analyzetheatres (anth)**
  - Effect: Analyze theatres for errors.

- **massconquer (massc)**
  - Effect: Mass conquer tool. Requires direct province names.
  - Example/Comment: Only for developers.

- **aircombat (airc) [<scenario name>] [<result name>] [<province id>] [<state id with airbase>] [<state id with airbase>] [<equipment type>] [<equipment type>] [<equipment creator country>] [<equipment creator country>]**
  - Effect: Spawns an air combat in desired location.
  - Example/Comment: Only for developers.

- **fronts**
  - Effect: Toggle visibility of the foreign fronts

- **ai_front_dump (aifrontdump)**
  - Effect: Dump AI front data to log file, needs to have a unit selected

- **traderoutes**
  - Effect: Toggle visibility of trade routes

- **debug_tactics**
  - Effect: Toggle visibility of debug tooltip for tactics

- **reloadsupply (relsup)**
  - Effect: Reinitializes the supply systems.

- **deltat [<speed factor>]**
  - Effect: control animation speeds

- **building_health (bhealth) [<building type>] [<state or prov id>] [<building level>] [<health to add>]**
  - Effect: Changes specified building health

- **nomapicons**
  - Effect: Toggles map icons.

- **nopausetext**
  - Effect: Toggles the pausebanner for nicer screenshots.

- **nextsong**
  - Effect: Changes the currently playing soundtrack.

- **combatsound**
  - Effect: How often does the combat view give a random sound? 0-50

- **morehumans (humans) [num]**
  - Effect: Adds more humans

- **window (wnd) [Arguments: open/close] [window gui name]**
  - Effect: Opens or closes the specified window

- **poll**
  - Effect: Polls valid Events

- **pause_in_hours**
  - Effect: Pauses the game after X hours have passed after command is called

- **winwars**
  - Effect: Gives max war score in all wars for the country
  - Example/Comment: Command no longer exists as of patch 1.9.1

- **testevent [<Event ID>] [<Character ID>]**
  - Effect: Tests an event without triggering it

- **resign**
  - Effect: Resign from the game

- **add_interest [<Country tag>]**
  - Effect: Add specified country tag to your interest

- **remove_interest [<Country tag>]**
  - Effect: Removes specified country tag from your interest

- **add_diplo**
  - Effect: Adds diplomatic entroute

- **PrintSynchStuff**
  - Effect: Prints random count and seed

- **SetRandomCount**
  - Effect: Sets the random count to 0 or arg

- **ai_invasion**
  - Effect: Toggles AI AI naval invasions

- **ai_pp_log**
  - Effect: Prints AI use of PP to log

- **ai_idea_desire_log**
  - Effect: Prints AI desire for ideas to log. For current country only

- **ai_force_template**
  - Effect: Force the AI to only spend army XP on template design

- **ai_force_equipment**
  - Effect: Force the AI to only spend army XP on equipment design

- **ai_front_id**
  - Effect: Get the address of selected group's front debug ID

- **fow (debug_fow) [Province ID]**
  - Effect: Turns off fog of war, only within a province if specified.

- **collision (debug_collision)**
  - Effect: Toggles debug display of normals/bounding boxes/collision

- **savegame**
  - Effect: Creates a savefile.

- **savecheck**
  - Effect: Makes a save file (Test_01), loads the save file, makes a new savegame (Test_02). Those save files should look the same.

- **IP**
  - Effect: Shows your IP

- **requestgamestate**
  - Effect: Requests the gamestate from host

- **nudge**
  - Effect: Go to the nudge tool

- **mapmode [Mapmode type (int)]**
  - Effect: Change mapmode.

- **fullscreen**
  - Effect: Toggles fullscreen

- **prices**
  - Effect: Price Info

- **remove_core [<State ID>] [<Country Tag>]**
  - Effect: Remove core.
  - Example/Comment: Command Does not work

- **debug_zoom**
  - Effect: Zooms in the game

- **debug_types**
  - Effect: Will print the data type for all dynamic reference objects. Can only be used if using RTTI.

- **debug_show_event_ID**
  - Effect: Shows event ID

- **debug_commands**
  - Effect: Printing commandcount to message.log

- **debug_events**
  - Effect: Start Counting events

- **debug_dumpevents**
  - Effect: Dump Event data to game log

- **debug_diploactions**
  - Effect: Start Counting diplomatic actions

- **debug_dumpdiploactions**
  - Effect: Dump diplomatic action data to game log

- **debug_assert**
  - Effect: Toggles asserts on/off

- **debug_nomouse**
  - Effect: Toggles mouse scrollwheel on/off

- **debug_terrain**
  - Effect: Toggles Terrain on/off

- **debug_cities**
  - Effect: Toggles Cities painting mode on/off

- **debug_water**
  - Effect: Toggles Water on/off

- **debug_fronts**
  - Effect: Toggles interpolated fronts debug

- **debug_off_front_snap (dbg_fsnap)**
  - Effect: Toggles offensive fronts snapping debug

- **debug_borders**
  - Effect: Toggles Borders on/off

- **debug_trees**
  - Effect: Toggles Trees on/off

- **debug_rivers**
  - Effect: Toggles Rivers on/off

- **debug_postfx**
  - Effect: Toggles PostFX on/off

- **debug_sky**
  - Effect: Toggles Sky on/off

- **debug_bloom**
  - Effect: Toggles Bloom on/off

- **debug_tooltip**
  - Effect: Toggles Tooltips on/off

- **debug_nuking**
  - Effect: Allows to nuke every province without checking any conditions.
  - Example/Comment: Command no longer exists as of patch 1.15.1

- **flagsoutput [<path>]**
  - Effect: Creates texture atlas files from memory.

- **cityreload**
  - Effect: Reloads the cities

- **version**
  - Effect: Show current game version

- **debug_nogui**
  - Effect: Toggles GUI on/off

- **debug_volume [<Volume Delta>]**
  - Effect: Modifies music volume

- **debug_lockcamera**
  - Effect: Toggles Camera locked on/off

- **debug_lines**
  - Effect: Toggles Debuglines

- **debug_entities**
  - Effect: Toggles Debug entities

- **debug_info**
  - Effect: Toggles Debug info

- **debug_particle**
  - Effect: Toggles Particles Debug info

- **debug_ai_budget [CountryTag]**
  - Effect: Show ai budget data

- **debug_textures**
  - Effect: Writes Texture info to application debug log

- **debug_texture**
  - Effect: draws textures like bloom

- **debug_wireframe**
  - Effect: Toggles forced wireframe on/off

- **debug_achievements_clear**
  - Effect: Clear all achievements and user stats
  - Example/Comment: Only for developers.

- **moveunit [<Unit ID>] [<Province ID>]**
  - Effect: Moves a unit to a province

- **spawnactor [<Actorname>] [<Province ID>] [<Animation> OPTIONAL]**
  - Effect: Spawns an actor with an optional animation

- **cameraclamp**
  - Effect: Toggles the camera clamping

- **provtooltipdebug (tdebug)**
  - Effect: Toggles the debug info in province tooltip

- **reloadweather [<randomseed>]**
  - Effect: Reload and regenerate weather

- **weather**
  - Effect: Toggle weather simulation

- **debug_air_vs_land (dbg_cas)**
  - Effect: Toggle debug mode for air vs land combat.

- **mapnames**
  - Effect: Toggle map names

- **gbreload**
  - Effect: Reloads gradient borders
  - Example/Comment: Only for developers.

- **gbpaint [layer] [channel]**
  - Effect: Toggles gradient border painting

- **profilelog**
  - Effect: Prints out the profiling informations into time.log

- **run**
  - Effect: Runs the specified file with list of commands

- **oos**
  - Effect: Out of Synch
  - Example/Comment: Only for developers.

- **trigger_docs (effect_docs, scripting_docs, docs)**
  - Effect: Print docs for triggers, effects, and variables
  - Example/Comment: Documentation for triggers/effects printed to game.log file

- **threat [Threat amount]**
  - Effect: Adds or show threat level of the current tag, which is the world tension generated by the tag.
  - Example/Comment: Positive values will add to the world tension generated by the active tag, while negative values will subtract from the world tension generated by the active tag, with corresponding entries in the world tension history log. By tag-switching, it is possible to raise or lower the world tension generated by any particular country. If one does "threat 999999999" it will reset the world tension to 0.

- **3dstats**
  - Effect: Toggles 3D Stats

- **hdr**
  - Effect: Toggles hdr

- **hdr_debug**
  - Effect: Toggles hdr debugging

- **srgb**
  - Effect: Toggles sRGB

- **bloom**
  - Effect: Toggles bloom

- **PostEffectVolumes.Default [posteffect_values name]**
  - Effect: Toggles default posteffect values

- **night**
  - Effect: Toggles night
  - Example/Comment: *as of 1.01 this does not seem to work (filed under developer-only command)  This command can be emulated via the day/night loop option at the bottom right toolbar (shortcut key 'N')

- **filewatcher**
  - Effect: Toggles filewatcher

- **createlean**
  - Effect: Create LEAN textures

- **helplog**
  - Effect: Print out all console commands to game.log file.

- **helphelp**
  - Effect: Double Rainbow help.

- **hsv**
  - Effect: Converts RGB to HSV

- **tag_color**
  - Effect: Test setting a country's color

- **browser [url]**
  - Effect: Show browser window

- **browser_base_url [url]**
  - Effect: Set browser base url

- **airealism**
  - Effect: Enable realistic AI
  - Example/Comment: An easter egg making the AI smacktalk in chats. Useless since unactivable in multiplayer and chat unactivable in singleplayer.

- **instant_wargoal**
  - Effect: Will allow instant justificatiion of war goals on countries

- **allowideas**
  - Effect: Allows the player to pick any idea even if normally unavailable
  - Example/Comment:
    ```text
    This overrides the
    available
    and
    visible
    triggers of ideas, but not the
    allowed
    trigger
    ```

- **release [<country tag>]**
  - Effect: Releases a country or releasable nation
  - Example/Comment: release slv releases Slovenia

- **InternationalMarket.AddSubsidyForTags [<economic capacity>] [<equipment>] [<country tag>]**
  - Effect: Adds a subsidy for the player to buy off from a specified country.
  - Example/Comment: ex (Adds a subsidy for the player to be able to help buy German sold light tanks for up to 5k EC): InternationalMarket.AddSubsidyForTags 5000 light_tank_chassis GER

- **random_seed**
  - Effect: Randomises the current seed the game is using
  - Example/Comment:
    ```text
    The AI uses this seed to decide all their focuses and decisions.
    You can use this to generate a more favourable outcome to any ai action you dislike (e.g. you want to ally with country)
    ```

- **eval_effect [<country tag>] = { create_faction = "[faction name]" }**
  - Effect: Creates a faction with a specified name
  - Example/Comment: The leader of the faction will be the inserted country tag

- **eval_effect [<country tag>] = { dismantle_faction = yes }**
  - Effect: Deletes the faction of specified country

- **eval_effect [<country tag>] = { add_to_faction = [<country tag>] }**
  - Effect: Adds a country to a faction
  - Example/Comment: The second tag is the country which will join the first tag's faction

- **eval_effect [<country tag>] = { remove_from_faction = [<country tag>] }**
  - Effect: Removes a country from a faction
  - Example/Comment: The second tag is the country which will join the first tag's faction

- **eval_effect [<country tag>] = { set_faction_name = "[faction name]" }**
  - Effect: Renames the faction of the specified country

- **toggle_silhouette_portraits**
  - Effect: Enables and disables silhouette portraits.
  - Example/Comment: Only for developers.

## See also

- [Modding](<Modding - Hearts of Iron 4 Wiki.md>)

## References

1. [↑](#cite-ref-1) A comment of podcat about the command been found <https://www.reddit.com/r/hoi4/comments/6cb8vh/the_secrets_of_hoi4/dhtdr4x/>

**[Modding](<Modding - Hearts of Iron 4 Wiki.md>)**

**Hearts of Iron IV**
