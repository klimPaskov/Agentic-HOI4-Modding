# Table of contents

- [Overview](#overview)
- [Testing](#testing)
- [Log files](#log-files)
- [Crash data log](#crash-data-log)
- [Common crash causes](#common-crash-causes)
  - [Main menu loading](#main-menu-loading)
  - [During country selection](#during-country-selection)
  - [Middle of the game](#middle-of-the-game)
- [Additional details](#additional-details)


---

*Troubleshooting* is the identification of the cause of crashes, bugs or other problems.

## Overview

In general, there are two kinds of errors: fatal and non-fatal.

Fatal errors occur when the game cannot load a vital piece of data and cannot operate without it present. This causes a crash to desktop (CTD). When fatal errors occur, an exception will be printed to the **exceptions.log**. Typically these errors occur during the loading process or when a specific action is taken in-game.

Non-fatal errors occur when the game encountered invalid data or broken syntax. These errors are almost always printed to the **error.log**.

## Testing

Performing testing is vital to debugging a mod. Typically this is done via the in-game console with commands.

These are useful console commands for modders:

- **reloadfx all**
  - Usage: Reloads most of the effects used in the game, such as fog of war, the HDR and opacity of country borders, ect.

- **reload texture**
  - Usage: Reloads most of the textures used in the game, such as leader portraits, technology icons, etc.

- **reload localization**
  - Usage: Reloads most of the localization used in-game, such as event titles and descriptions.

- **reload defines**
  - Usage:
    ```text
    Reloads the defines files from
    /Hearts of Iron IV/common/defines/
    .
    ```

- **reload focus**
  - Usage:
    ```text
    Reloads the focus trees in
    /Hearts of Iron IV/common/national_focuses/
    .
    ```

- **reloadoob**
  - Usage: Reloads the starting OOB file for the specified tag.

- **reloadtechnologies**
  - Usage: Reloads the technology files. Will cause a crash if an error is encountered.

- **reloadinterface**
  - Usage: Reloads the interface files (.gui).

- **reload decision**
  - Usage: Reloads the decision files (.gui and common/decisions).

- **tdebug**
  - Usage: Activates the debug tooltips, displaying important information such as state ID, province ID, etc.

- **event**
  - Usage: Fires the specified event immediate for the current player country.

- **nocb**
  - Usage: Removes restrictions on diplomatic actions.

- **observe**
  - Usage: Places the player into the observer slot, allowing the game to pass without player input.

- **aiview**
  - Usage: Displays the AI priorities when hovering over specific buttons, such as technology.

- **tag**
  - Usage: Switches the player to another country.

- **update_loc**
  - Usage: Reloads the specified localization key.

- **updateequipments**
  - Usage:
    ```text
    Reloads the equipment files in
    /Hearts of Iron IV/common/units/equipment/
    .
    ```

- **updatesubunits**
  - Usage:
    ```text
    Reloads the unit files in
    /Hearts of Iron IV/common/units/
    .
    ```

- **research_on_icon_click**
  - Usage: Activates research on click, allowing you to click on technologies to research them instantly.

- **Focus.NoChecks**
  - Usage: Removes the trigger checks for focuses.

- **Focus.AutoComplete**
  - Usage: Activates instant completion for focuses.

- **set_country_flag**
  - Usage: Sets the specified country flag for the current country.

- **add_ideas**
  - Usage: Adds the specified idea to the current country.

## Log files

The game stores various log files in your HOI4 user folder: (Windows: `\\Documents\Paradox Interactive\Hearts of Iron IV\logs\`, Linux: `.local/share/Paradox Interactive/Hearts of Iron IV/logs`). These are overwritten every time the game is started.

To enable full error logging, add the `-debug` launch command via *Set Launch Options* in Steam.

- **ai.log**
  - Description: Prints the AI choices undertaken.
  - Usefulness: Medium

- **ai_trace.log**
  - Description: Prints the AI movements undertaken (divisions, ships, air, etc.)
  - Usefulness: Low

- **error.log**
  - Description:
    ```text
    Prints the various non-fatal errors. Many errors can be ignored, although almost all errors relating to files in the
    common
    folder should be fixed.
    ```
  - Usefulness: High

- **exceptions.log**
  - Description: Prints the stack trace when the game crashes to desktop.
  - Usefulness: Low

- **executedcommands.log**
  - Description: Prints the internal commands uses by the player and AI.
  - Usefulness: Low

- **game.log**
  - Description: Prints the actions that were taken by countries in-game. Useful when the crash is due to a specific action.
  - Usefulness: High

- **graphics.log**
  - Description: Prints the graphical errors relating to positions, rivers, and trees.
  - Usefulness: Low

- **memory.log**
  - Description: Prints the memory used during setup. Useful for crashes during the loading process, to see when the game crashed.
  - Usefulness: High

- **message.log**
  - Description: Prints the session info for the current session.
  - Usefulness: Low

- **postedcommands.log**
  - Usefulness: Low

- **random.log**
  - Description: Prints times for game state changes.
  - Usefulness: Low

- **receivedcommands.log**
  - Description: Prints the internal commands received by the player in multiplayer.
  - Usefulness: Low

- **sentcommands.log**
  - Description: Prints the internal commands sent by the player in multiplayer.
  - Usefulness: Low

- **setup.log**
  - Description: Prints the completion of setup loading for each part of the process. Very useful for discovering which file may be causing a crash.
  - Usefulness: High

- **system.log**
  - Description: Prints the system information HOI4 is loaded on.
  - Usefulness: Low

- **system_debug.log**
  - Description: Prints interface errors.
  - Usefulness: Medium

- **text.log**
  - Description: Prints asserts on localization keys.
  - Usefulness: Medium

- **time.log**
  - Description: Prints the time it takes for the various loading steps to complete, and the tick interval. Very useful for crashes during the loading process, to see when the game crashed.
  - Usefulness: Medium

## Crash data log

When the game crashes, it provides information on system settings and what caused it to crash in the [user directory's](<Modding - Hearts of Iron 4 Wiki.md>) /Hearts of Iron IV/crashes/ folder. Although most of the time this is not beneficial as to what caused it to crash, the error log could contain clues. However, one important logging mechanism can be additionally turned on:

Adding the `-crash_data_log` launch command via *Launch Options* in Steam will also cause the `meta.yml` file in that folder (*Directly within*, not in the /logs/ subfolder) to contain the last read line of code before crashing, as well as turning on the debug mode. This slows down the game by a significant amount, so it shouldn't be used outside of crash debugging. **If the last read line of the file given is the last line in the file, it's rather likely the game crashed on the *next* read file instead, which is quite difficult to locate.** In some cases, the game can grant a script instead of a file, such as a savefile or client\_ping.  
This can appear like `LastRead: map/supply_nodes.txt (727)` (Where the number represents the line of the file that was last read before the crash occurred) or `LastRead: client_ping (1)`.

Note that while -crash\_data\_log enables debug mode, not all benefits of the launch option get applied by default and require using both launch options. For example, edits to files indexed during the main menu loading will not get automatically loaded, requiring a console command usage to get reloaded instead. However, -crash\_data\_log's debug does include the game loading into the main menu with map errors, the nudge being available for selection, and the debug information when hovering over a province or a country.

## Common crash causes

**A variety of crash types are caused by recklessly unloading folders with [replace\_path](<Modding - Hearts of Iron 4 Wiki.md#mod-structure>)**, leading to the game detecting there not being any database entries of a certain type. It's best practice to port over generic files to the mod if overwriting a folder in entirety for this reason, as well as to avoid unintuitive errors.

In case of a different crash, note that if a file is completely empty, the game may skip reading it in entirety. As such, the same crash may display a different file if the one in this list is empty.   
It's best to completely clean the error log before trying to find a crash, as some errors may appear innocuous while still crashing the game.

If the last read file proves useless, it's possible to temporarily remove files from the mod and slowly re-add them to find the exact cause; upon finding the cause folder, it should be adjusted accordingly. A sort of [binary search](http://en.wikipedia.org/wiki/Binary_search_algorithm) can be used by adding/removing the files large chunks at the time. replace\_paths can be removed aside from essential ones: history/states/ and map/strategicregions. Note that [**both** \*.mod files need to be edited for replace\_paths to apply.](<Modding - Hearts of Iron 4 Wiki.md#mod-structure>)

**This list is non-exhaustive**: There are more potential crashes, and any given file or script can have more causes that are not outlined in the list. This has been broken up into sections on when they happen for easier navigation. The file provided is the file marked as last read by the crash data log.

### Main menu loading

- common/countries/cosmetic.txt – Caused by a complete overwriting of common/national\_focus/ or common/continuous\_focus/.
- map/rocketsites.txt – Caused by a complete overwriting of history/states/ or common/unit\_leader/. As there are no "generic files" for states, one should be created manually instead.
- common/national\_focus/\*.txt – This crash, granted that it's the last line of the last file in the folder, can be caused by a focus tree using a `shared_focus = my_focus` argument, specifying a shared focus that does not exist.
- gfx/models/supply/railroad.shader – Caused by an error within the [the .bmp files creating the map](<Map modding - Hearts of Iron 4 Wiki.md>). This can be a wide variety of causes. Some causes include provinces.bmp having dimensions as numbers that are undivisible by 256, having a size of over 40 MiB, the dimensions changing between different bitmaps (aside from trees.bmp, where the size changes the density of static models), or an incorrect DIB header formatting (such as setting encoding to be used or using BITMAPV5HEADER instead of BITMAPINFOHEADER) in any bitmap.
- history/general/\*.txt / history/countries/\*.txt / map/rocketsites.txt (In order in which they'd appear with replace\_paths to the previous ones) — One of the states within the mod has a `victory_points = { ... }` definition that attempts to assign victory points to a province that does not exist within the game.
- savegame.hoi4 (takes on the name of a savefile, not necessarily one that exists right now) or map/cities.txt – Caused by there being a large quantity of countries defined while there are few (such as 15) or no dynamic countries. The exact amount of countries that the game can handle is not a consistent number, usually falling in the range of 40–80. Typically caused by a reckless overwriting of common/country\_tags or the file that stores the dynamic countries being outdated.

### During country selection

This also includes the loading after a country has been selected, but it's not yet possible to play.

- `set_controller` – This crash typically happens when trying to select a country in a bookmark if the country doesn't have a valid capital defined within its /Hearts of Iron IV/history/countries/TAG\*.txt file. The game uses the capital in order to determine what portion of the map to zoom onto, and not getting one is unexpected.
- history/units/filename.txt – One of the naval orders of battle in the mod has a carrier defined with airwings directly inside, as was done in 1.11 and earlier. Adjust the orders of battle in the mod as needed. Note that the file shown as the last read one is not necessarily the one that crashes the game.
- history/units/filename.txt / map/railways.txt – Caused by a country having a division template, yet not finding any possible /Hearts of Iron IV/common/ai\_templates entry to use to expand on the template. The exact file/script in question depends on *when* the country obtains the division template: an order of battle (which'll be last read) or another history file (leading to railways).
- map/supply\_nodes.txt or map/railways.txt – This crash is most commonly caused by the specified building types being placed on invalid provinces, such as those that are not located in states. This crash occurs both when trying to open the supply menu in nudge or when trying to start a single player game. This can be corrected by emptying the files in question and [optionally creating a proper definition of the files, either manually or via nudge](<Map modding - Hearts of Iron 4 Wiki.md#supply-nodes-and-railways>).
- tutorial/tutorial.txt – This crash is caused by the tutorial file being erroneous. This can be represented as a link to an invalid state ID within the file (such as if every base game state was erased) or as the file lacking a `tutorial = { ... }` definition of any kind entirely. Replacing the entire file's contents with `tutorial = { }` works to solve the crash.

This is also the last file that gets read after the country selection process finishes. If a crash occurs directly afterwards and the game fails to write the file properly, it will land on this one.

### Middle of the game

- `client_ping` or `hourly_tick` – This crash is caused by the in-game AI, which can be seen by turning off the AI [using the console](<Console commands - Hearts of Iron 4 Wiki.md>). There are several causes for this occurring, including but not limited to:
  - A country has a division template, yet couldn't find any /Hearts of Iron IV/common/ai\_templates entry to use to expand on the template. Typically caused by a reckless overwriting of the folder with replace\_path or an error in setting up the `blocked_for = { ... }`/`available_for = { ... }` blocks.
  - Any state not having an owner defined in the history file. In general, such states always run unstably, with a lot of actions crashing them, such as right-clicking or attempting to transfer one to a country. One of such actions is attempting an air mission over that state. As the AI is able to use airplanes, they will try to attempt to at least evaluate the value of doing a mission over the state, which results in a crash to desktop.
  - [An incomplete map/buildings.txt](<Map modding - Hearts of Iron 4 Wiki.md#buildings>). The buildings file is used for determining into which sea province the naval bases and floating harbours will go out into, alongside positioning building models. This information is necessary when attempting to use any naval base or floating harbour, as the game would have no idea via which province the province connects to the sea otherwise. The game also checks this information when attempting to *build* a naval base, and if the game attempts to evaluate an invalid naval base definition, the game gets stuck in an infinite loop of attempting to obtain the naval base information, resulting in a CPU/GPU overload and a game crash.

:   This also results in an error.log entry of `Province 12345 is setup as coastal but has no port building in the nudger. This will likely crash the game.` after launching the game.

## Additional details

A version tracking website, such as [[Gitlab](https://about.gitlab.com/)] or [[Github](https://github.com/)], can be used to keep track of updates to the code. As such, it can be beneficial to use them and regularly push mod's updates to them in order to limit the selection of possibly problematic files when trying to debug an issue.

When the game has a major update, it can be important to read the patch notes to fix the newly-appearing errors. For example, the 1.12's patch notes provide an "Important modding notes" section, which also serves as a check-list of necessary things to fix in the mod in order to avoid a crash. It is also important to avoid overwriting most base game files when possible in order to ease compatibility, though this is not always possible. One folder where it's incredibly important to do is [defines, where an override file is essentially mandatory](<Defines - Hearts of Iron 4 Wiki.md#overrides>) in order to avoid even minor game updates from introducing crashes.

In case the game crashes on startup, but there's no obvious reason why in the error log and it's unknown what was last changed since the last time, the mod could have folders strategically removed. As an example, it is almost always possible to remove the entire /Hearts of Iron IV/common/ folder from the mod without the game crashing, provided debug mode is turned on and there are no replace\_paths to the folder.

**[Modding](<Modding - Hearts of Iron 4 Wiki.md>)**
