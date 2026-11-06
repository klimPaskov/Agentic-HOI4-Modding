# Mod structure

## Mod File Structure

### Local Mod

Local Mod files must be located in the folder `~/.local/share/Paradox Interactive/Hearts of Iron IV/mod` or `C:\Users\<Username>\Documents\Paradox Interactive\Hearts of Iron IV\mod`, which must contain:

- **The '.mod' file**, to tell the launcher what to do with the mod-folder (For local use only, any name possible; this file does not get uploaded, when publishing the mod via Steam Workshop)
- **The mod folder** or zip containing the mod data. The mod data must have the same file and folder structure as the game's directory itself.
- **descriptor.mod file** inside the mod folder - this file should contain the same information as the first .mod file (Note: The File must use the descriptor.mod name and must NOT be saved in UTF-8 BOM format)
- Mod picture (optional) - a file named **thumbnail.png** in the mod folder, to serve as Steam Workshop mod picture (Note: Must use .png format and 'thumbnail.png' name; dimensions aren't important but should be 1:1 ratio). In addition, thumbnail files should be less than **1MB** in size, otherwise they cannot be uploaded to ParadoxMods.

The game launcher's mod config tool **can create basic structure automatically**. Just go to *Mods* tab, then click *Mod Tools* and *Create Mod*.
Note that folder and file names are case sensitive on Mac OS X and Linux.

### Steam Workshop Mods

Subscribed and downloaded mods from the steam workshop are in `.../Paradox Interactive/Hearts of Iron IV/workshop/content/394360` or sometimes `...\SteamLibrary\steamapps\workshop\content\394360`

Mods downloaded from the Steam Workshop are treated differently than those manually installed or created:
Though the mods .mod files will appear in the mod folder (represented by a *remote_file_id*), The content of the mod will be stored in `...\Paradox\Hearts of Iron IV\workshop\content\394360\<remote_file_id>`
The *remote_file_id* is an ID given to mods from the workshop. The ID is displayed as the name of the mod's .mod and zip files, but is further represented within the .mod and descriptor.mod files as such:

```text
name="New Ideologies"
archive="workshop/content/281990/678893824/newideologies.zip"
tags={
	"Balance"
	"Gameplay"
}
remote_file_id="678893824"
supported_version="1.11.*"
```

**Note:** Newer mods, starting with game version 1.9.0 are no longer stored in a .zip archive

The sample descriptor above is not a current HOI4 descriptor.

- `archive="workshop/content/281990/..."` uses Steam app id `281990`. HOI4's app id is `394360`, the id in the folder path at the start of this section, so the sample was taken from another game or an old layout. The page's own note says mods since 1.9.0 are not stored as `.zip`, so a current Workshop descriptor has no `archive`.
- `supported_version="1.11.*"` is far behind the installed build `1.19.4.1`. A mod for this build writes `supported_version="1.19.*"`.
- The keys are real. `hoi4.exe` contains the messages "Invalid supported_version in %s" and "Could not find archive for mod: %s" and the key names `remote_file_id` and `user_dir` (executable strings). The two messages do not behave alike. A bad `supported_version` (`supported_version="abc"` in `descriptor.mod` and in the outer `mod/igc_g.mod`) wrote "Invalid supported_version in file: mod/igc_g.mod line: 3" to error.log (the `%s` is empty, and the file and line follow), and the mod still loaded. An `archive="mod/missing.zip"` pointing to a missing zip did not write "Could not find archive for mod". The game wrote `Incorrect MOD descriptor: "mod/igc_g.mod"` and loaded no mod (Active Mod Count 0). No "Could not find" or "archive" text appeared in error.log, system.log, setup.log, game.log or text.log. The launcher was not used (the runner starts `hoi4.exe` with a scratch user folder), so launcher warnings were not seen, and "Could not find archive" may exist for another path form. What `remote_file_id` does was not tested. (unverified)
- The launcher text "The mod does not have supported_version set." shows that a descriptor without `supported_version` is accepted and only flagged as outdated.

## Creating a New Mod

### General rules

- Mods modify the game with the same file structure as in the vanilla game.
- All appropriate files found in the folder are loaded
- All .txt files should use UTF-8 without BOM format, Localisation files should use UTF-8 BOM Format
- To overwrite the vanilla file, use the same file name
- To add content without changing any vanilla files, use a different file name
- The Game will not check any further than the file directory for changes. If one is trying to add a line to a text file, one must copy the entire text file and add the line within said text file.

Encoding in practice. Vanilla does not follow "no BOM in every `.txt`".

| Vanilla files | With a byte order mark |
| --- | --- |
| `localisation/**/*.yml` | 2,093 of 2,093 |
| `common/**/*.txt` | 235 of 2,224 |
| `events/*.txt` | 87 of 128 |
| `history/**/*.txt` | 942 of 2,058 |
| `interface/*.gfx` and `interface/*.gui` | 0 of 616 |
| `map/**/*.txt` | 0 of 317 |

Script files that carry a BOM load fine in vanilla (1,264 of 4,410 `.txt` files in `common/`, `events/` and `history/` start with one), so a BOM in script is tolerated. No BOM stays the safe choice for new script files. Localisation is the strict case: every vanilla `.yml` has the BOM (2,093 of 2,093), and `hoi4.exe` contains the message "Localization file '%s' should be in in utf-8-bom encoding". (unverified) (the message is a string in `hoi4.exe`)

### Creating a simple local mod

For example, to create a mod called "Test1", create a new text file called *test1.mod* and a folder named 'test1' within `...\Paradox\Hearts of Iron IV\mod`.

The contents of *test1.mod* should be as follows (the order of the lines does not matter):

```text
name="Test1"
path="mod/test1"
tags={                         # Tag used for filtering in the Steam Workshop. Full and updated list of tags can be found there. Optional.
	"Alternative History"
}
picture="thumbnail.png"        # Optional picture for the mod, visible in the game launcher and Steam Workshop (note: the picture is only shown for the mods you download, not your own local mods)
supported_version="1.17.*"     # Supported game version (checked by the game) - can be either in the format with asterisk* (all 1.17 versions) or a specific game version, like "1.17.3.0"
version="1.0b"                 # Mod version displayed in the game launcher. This is different from the "supported_version" and can be anything. Optional.
```

This is done to provide the game launcher with information about the mod. This includes the mod's name, location (from the mod file), tags (extra descriptors), supported game version, and other optional information.

Which file holds `path`, and an example for 1.19.

The page says `descriptor.mod` "should contain the same information as the first.mod file". The [Modding](modding.md#mod-structure) page is more exact: only the user-specific file in `mod/` carries `path`, and it says `replace_path` has to be written in both files. The game reads `replace_path` from the user-specific file alone: `replace_path="events"` in the outer `mod/<name>.mod` replaced the vanilla `events/` folder (`germany.112` was gone: "*Tried to trigger non-existant event: germany.112", after further lines of the same kind at load for other vanilla events), while the same line in the mod folder's `descriptor.mod` alone had no effect (`germany.112` still ran, with no such line). Writing it in both files gave the same result as the outer file alone, so both files are not needed. Only the `events/` folder was tested, and the dump file of the events was not read. The test mod loaded with `path` only in the outer file, as the runner writes it.

```text
# mod/test1.mod  (user-specific, next to the mod folder)
name="Test1"
path="mod/test1"
version="1.0"
supported_version="1.19.*"
tags={
	"Alternative History"
}

# mod/test1/descriptor.mod  (mod-specific, inside the mod folder, no path)
name="Test1"
version="1.0"
supported_version="1.19.*"
tags={
	"Alternative History"
}
```

Vanilla's own DLC descriptors, such as `dlc/dlc049_no_compromise_no_surrender/dlc049.dlc`, use the same `key = value` syntax. Their `path` is relative to the game folder and uses forward slashes. It is written without quotes in `dlc049.dlc` and in some other descriptors, and with quotes in others (`dlc001.dlc`, `dlc002.dlc`).

### Creating a Submod

Sometimes you will want your mod to depend on other mods, and also require a certain loading order. Mods will usually load in alphabetical order (so the mod last in the list will overwrite the earlier). But some things may affect this so if you need a certain load order and be clear that you have dependencies this needs to be specified by including its full name in the .mod file under "dependencies".

```text
name="testmodB"
path="mod/testmodb/"

# this guarantees we load testmodA first before our testmodB is loaded
dependencies= {
	"testmodA"
}
supported_version="1.11.*"
```

## Adding Mod Content

For example, a simple modification could be changing the text that appears in the game.

To change the quotes that appear in the loading screen, copy the "localisation/loading_tips_I_english.yml" file from the base install of the game, ".../Hearts of Iron IV/localisation/loading_tips_I_english.yml" to a "localisation" folder you create in the new "mod/test1" folder.

The file structure now looks like the following:

```text
 ...\Paradox Interactive\Hearts of Iron IV\mod
     test1.mod
     test1 (dir)
       localisation (dir)
         loading_tips_L_english.yml
```

As "loading_tips_I_english.yml" is unaltered, the game will run the same as usual. However, if it is changed, the information will be used by the game instead of the usual "loading_tips_I_english.yml". Modify the "loading_tips_I_english.yml" file in the mod folder so that it contains this:

```text
 l_english:
  LOADING_TIP_0:0 "Test1 mod"
```

When the game is loading with this mod active in the English language, the only quote shown will be "Test1 mod".

The loading tips walkthrough names the wrong file and the wrong place.

- The vanilla file is `localisation/english/loading_tips_l_english.yml`, with a lowercase L in `_l_`. The page writes `loading_tips_I_english.yml` (capital I) and `loading_tips_L_english.yml` (capital L). Use the vanilla spelling: all 2,091 language files in vanilla use lowercase `_l_`.
- The file sits in the `english` subfolder. The page's tree puts the copy directly in `localisation/`, which is a different path and so, by the same-name-same-place rule on the [Modding](modding.md#loading-files) page, a second file instead of a replacement. The rule holds: the same file at the folder root, `localisation/loading_tips_l_english.yml`, was loaded as a second file next to the vanilla one, and text.log logged the shared key as a duplicate ("Duplicate localization found, key: LOADING_TIP_0" for both files) with error.log adding "The game has loc key collisions". The vanilla value was the one used for `LOADING_TIP_0`, and the other vanilla tips stayed. The duplicate key was seen in one placement only, and only English loading tips were tested.
- Vanilla defines 163 tips, `LOADING_TIP_0` to `LOADING_TIP_162`, written without a version number (`LOADING_TIP_0: "text"`). A mod file that only defines `LOADING_TIP_0` leaves the other 162 tips in place. The page's result "the only quote shown will be Test1 mod" needs a file that replaces the vanilla one at the same relative path (`localisation/english/loading_tips_l_english.yml`) and defines nothing else. The replacement rule holds. A mod file at `localisation/english/loading_tips_l_english.yml` with only `LOADING_TIP_0` ("Test1 mod") replaced the vanilla file whole: the log showed "Test1 mod" for tip 0 and the bare keys `LOADING_TIP_1` and `LOADING_TIP_2` for the next two, where the control showed vanilla text for all three.

## Tips

- To understand how certain things in the code work, it can be useful to look into game files and search for things similar to what your mod is supposed to change
- Alternatively, you can search the files of other users' mods in `...\steamapps\workshop\content\394360`
- Try to minimize vanilla file overwrites, this will make it both easier for you to manage your mod content to keep it up to date and reduce risk of conflict with other mods
- When testing the mod, it can be very useful to look into Error log `...\Documents\Paradox Interactive\Hearts of Iron IV\logs\error.log` to gain a clue when something isn't working
- To keep your mod updated between smaller updates, replace the third number in your version with a \*. For example, replace "1.5.4" with "1.5.\*" to make that mod work with all versions of 1.5

## See also

Depending on what your mod is supposed to do, you may want to visit some of these pages relating to some more basic game content modding:

- [Country creation](country_creation.md) - How to create a new country, assign flag, place the new country into the game
- National Focus modding - How to edit National Focus tree
- [Idea modding](idea_modding.md) - How to add/edit National Ideas
- [Event modding](event_modding.md) - How to add/edit an Event

## Common folder index for 1.19.4.1

`GAME\common\` holds 81 folders and 13 loose files in 1.19.4.1. Each folder is read for the entries named in its row; a file's name inside a folder rarely matters (see the exceptions in the [Modding](modding.md#notes) notes). "Files" counts every file under the folder in vanilla, documentation included. "Doc" names the game's own documentation for that folder: 28 of the 81 folders have one, some only in a subfolder. Open it before writing entries.

The links to Collection modding, Game rule modding, Intelligence operation modding, Map mode modding, Occupation and resistance modding, Peace conference modding, Raid modding, Script constant modding and Special project modding point to pages that the live wiki does not have.

| Folder | Files | Defines | Snapshot page | Doc |
| --- | --- | --- | --- | --- |
| `abilities` | 6 | Unit leader abilities a commander can trigger (`ability = { type = army_leader ... }`) | [Character modding (`enable_ability`)](character_modding.md) | none |
| `aces` | 1 | Air ace modifier tags per aircraft type, with a chance (`modifiers = { }`) | [Effects (`add_ace`)](effects.md) | none |
| `ai_areas` | 1 | Named groups of strategic regions for AI strategies (`areas = { }`) | [AI modding](ai_modding.md#ai-areas) | none |
| `ai_equipment` | 23 | AI equipment design groups: roles, modules, priorities | [AI modding](ai_modding.md#ai-equipment) | `_documentation.md` |
| `ai_faction_theaters` | 2 | Theaters (connected strategic region sets) the AI faction leader assigns members to | none | `_documentation.md` |
| `ai_focuses` | 8 | AI focus presets that weight research per focus name | [AI focuses](ai_focuses.md) | none |
| `ai_navy` | 26 | Goal-based naval AI: fleets, goals and taskforce roles (subfolders `fleet`, `goals`, `taskforce`) | none | `_documentation.md`, `taskforce/_documentation.md` |
| `ai_strategy` | 51 | AI strategy entries that weight AI behaviour (alliances, wars, unit roles, areas) | [AI modding](ai_modding.md#ai-strategies) | `_documentation.md` |
| `ai_strategy_plans` | 128 | Per-country AI strategy plans | [AI modding](ai_modding.md#ai-strategy-plans) | none |
| `ai_templates` | 16 | Target division templates the AI upgrades toward, by role | [AI modding](ai_modding.md#ai-templates) | `_documentation.md` |
| `autonomous_states` | 21 | Autonomy states (`autonomy_state`) | [Autonomy state modding](autonomy_state_modding.md) | none |
| `bookmarks` | 2 | Start-date bookmarks and their country entries | [Bookmark modding](bookmark_modding.md) | none |
| `bop` | 10 | Balance of power definitions | [Balance of power modding](balance_of_power_modding.md) | none |
| `buildings` | 2 | Building types, spawn points and landmark buildings | [Building modding](building_modding.md) | none |
| `characters` | 233 | Character database (`characters = { }`), one file per country group | [Character modding](character_modding.md) | `_documentation.md` |
| `collections` | 3 | Named script collections (`prefix:name` inputs for collection triggers) | [Collection modding](collection_modding.md) | `_documentation.md` |
| `continuous_focus` | 1 | Continuous focus palettes | [National focus modding](national_focus_modding.md#continuous-focuses) | none |
| `countries` | 442 | Country definition files (colour, graphical culture) plus `colors.txt` and `cosmetic.txt` | [Country creation](country_creation.md) | none |
| `country_leader` | 4 | Country leader traits (`leader_traits`) | [Character modding](character_modding.md#country-leader-traits) | none |
| `country_tag_aliases` | 1 | Country tag aliases usable as scopes | [Data structures](data_structures.md#country-tag-aliases) | none |
| `country_tags` | 2 | The list of country tags and the file each tag points to | [Country creation](country_creation.md) | none |
| `decisions` | 147 | Decisions and missions; categories in `categories/` | [Decision modding](decision_modding.md) | `_documentation.md` |
| `defines` | 3 | Lua defines (`NDefines`) | [Defines](defines.md) | none |
| `difficulty_settings` | 1 | Custom difficulty settings: a modifier with a multiplier for listed countries | [Bookmark modding](bookmark_modding.md#difficulty-settings) | none |
| `doctrines` | 27 | Doctrine folders, tracks, grand doctrines and subdoctrines (four subfolders) | [Doctrine modding](doctrine_modding.md) | `_documentation.md`, `folders/_documentation.md`, `grand_doctrines/_documentation.md`, `subdoctrines/_documentation.md`, `tracks/_documentation.md` |
| `dynamic_modifiers` | 11 | Dynamic modifiers (modifiers driven by variables) | [Modifiers](modifiers.md#dynamic-modifiers) | none |
| `equipment_groups` | 2 | Named groups of equipment types, used by MIO categories and equipment bonuses | [Equipment modding](equipment_modding.md) | `_documentation.md` |
| `factions` | 30 | Faction goals, icons, member upgrades and rules (four subfolders) | [Faction modding](faction_modding.md) | `_documentation.md` |
| `focus_inlay_windows` | 7 | Inlay windows shown inside a focus tree | [National focus modding](national_focus_modding.md#inlay-window) | `documentation.md` |
| `frontend` | 1 | Main-menu background database (`backgrounds/base_backgrounds.txt`) | none | none |
| `game_rules` | 1 | Game rule definitions and their options | [Game rule modding](game_rule_modding.md), [Bookmark modding](bookmark_modding.md#game-rules) | none |
| `generation` | 1 | `idea_generation`: trait conditions for generated advisors, chiefs and theorists (mostly empty in vanilla) | none | none |
| `idea_tags` | 1 | Idea categories (slots) and slot ledgers | [Idea modding](idea_modding.md#other-idea-categories) | none |
| `ideas` | 213 | Ideas, national spirits, laws and advisor ideas | [Idea modding](idea_modding.md) | none |
| `ideologies` | 1 | Ideology groups, ideologies and party names | [Ideology modding](ideology_modding.md) | none |
| `intelligence_agencies` | 1 | Intelligence agency names and logos | [Intelligence agency modding](intelligence_agency_modding.md) | none |
| `intelligence_agency_upgrades` | 2 | Agency upgrade branches and upgrades | [Intelligence agency modding](intelligence_agency_modding.md) | `_documentation.md` |
| `map_modes` | 1 | Scripted map modes (vanilla ships only the documentation, no definitions) | [Map mode modding](map_mode_modding.md) | `documentation.md` |
| `medals` | 1 | Career profile medals with bronze, silver and gold tiers | none | none |
| `military_industrial_organization` | 63 | MIO organizations, policies and AI bonus weights (three subfolders) | [Military industrial organization modding](military_industrial_organization_modding.md) | `ai_bonus_weights/_documentation.md`, `organizations/_documentation.md`, `policies/_documentation.md` |
| `modifier_definitions` | 2 | Modifier definitions (colour, value type, category) | [Modifiers](modifiers.md#modifier-definitions) | none |
| `modifiers` | 5 | Static modifiers, event modifiers and balance-of-power modifiers | [Modifiers](modifiers.md#static-modifiers) | none |
| `mtth` | 1 | MTTH variables read as `mtth:name` | [Data structures](data_structures.md#mtth-variables) | none |
| `names` | 1 | Random name pools per tag: characters, aces, callsigns and operation names | [Country creation](country_creation.md#character-names) | none |
| `national_focus` | 81 | Focus trees, shared and joint focuses, titlebar styles, search filters | [National focus modding](national_focus_modding.md) | none |
| `occupation_laws` | 1 | Occupation laws | [Occupation and resistance modding](occupation_and_resistance_modding.md) | none |
| `on_actions` | 18 | On-action hooks (`on_actions = { }`) | [On actions](on_actions.md) | `_documentation.md` |
| `operation_phases` | 17 | Phases of intelligence operations | [Intelligence operation modding](intelligence_operation_modding.md) | `_documentation.md` |
| `operation_tokens` | 2 | Tokens that operations require or grant | [Intelligence operation modding](intelligence_operation_modding.md) | `_documentation.md` |
| `operations` | 7 | Intelligence operations | [Intelligence operation modding](intelligence_operation_modding.md) | `_documentation.md` |
| `opinion_modifiers` | 13 | Opinion modifiers | [Modifiers](modifiers.md#opinion-modifiers) | none |
| `peace_conference` | 37 | Peace conference actions, categories, cost modifiers and AI desires | [Peace conference modding](peace_conference_modding.md) | `ai_peace/_documentation.md`, `cost_modifiers/_documentation.md` |
| `profile_backgrounds` | 1 | Unlockable career profile backgrounds | none | none |
| `profile_pictures` | 1 | Unlockable career profile pictures | none | none |
| `raids` | 10 | Raid types and categories | [Raid modding](raid_modding.md) | `_documentation.md` |
| `resistance_activity` | 1 | Resistance activity (sabotage) types | [Occupation and resistance modding](occupation_and_resistance_modding.md) | none |
| `resistance_compliance_modifiers` | 2 | Modifiers applied at compliance and resistance thresholds | [Occupation and resistance modding](occupation_and_resistance_modding.md) | none |
| `resources` | 2 | Resource definitions | [Resources modding](resources_modding.md) | `_documentation.md` |
| `ribbons` | 1 | Career profile ribbons | none | none |
| `scientist_traits` | 2 | Scientist traits (they apply to special projects only) | [Special project modding](special_project_modding.md) | `_documentation.md` |
| `scorers` | 4 | AI country scorers (`scorers/country/`) | [Data structures](data_structures.md#scorers) | none |
| `script_constants` | 5 | Script constants (`constant:group.name`) | [Script constant modding](script_constant_modding.md) | `documentation.md` |
| `scripted_diplomatic_actions` | 1 | Scripted diplomatic actions (vanilla ships only a commented template) | [Scripted GUI modding](scripted_gui_modding.md) | none |
| `scripted_effects` | 52 | Scripted effects | [Effects](effects.md#scripted-effects) | none |
| `scripted_guis` | 20 | Scripted GUI definitions | [Scripted GUI modding](scripted_gui_modding.md) | `_documentation.md` |
| `scripted_localisation` | 42 | Scripted localisation (`defined_text`) | [Localisation](localisation.md#scripted-localisation) | none |
| `scripted_triggers` | 55 | Scripted triggers | [Triggers](triggers.md#scripted-triggers) | none |
| `special_projects` | 17 | Special projects, project tags, prototype rewards and specialisations (four subfolders) | [Special project modding](special_project_modding.md) | `special_projects_documentation.md`, `projects/documentation.md`, `prototype_rewards/documentation.md`, `specialization/documentation.md` |
| `state_category` | 13 | State categories (building slots per category) | [State modding](state_modding.md#state-categories) | none |
| `strategic_locations` | 2 | Strategic locations: extra province building levels, applied with `strategic_state_location` | none | `documentation.md` |
| `synchronized_dynamic_tokens` | 1 | One token per line (53 lines of resource, equipment, building and ideology names); purpose not documented | none | none |
| `technologies` | 13 | Technologies | [Technology modding](technology_modding.md) | none |
| `technology_sharing` | 11 | Technology sharing groups | [Technology modding](technology_modding.md#technology-sharing-groups) | none |
| `technology_tags` | 1 | Technology categories and technology folders | [Technology modding](technology_modding.md#categories) | none |
| `terrain` | 1 | Terrain categories and graphical terrain | [Map modding](map_modding.md#provincial-terrain) | none |
| `timed_activities` | 1 | Equipment needs of timed activities (vanilla: `stage_coup`) | none | none |
| `unit_leader` | 13 | Unit leader traits and skill-level definitions | [Character modding](character_modding.md#unit-leader-traits) | none |
| `unit_medals` | 1 | Unit medals and the unit modifiers they grant | none | none |
| `unit_tags` | 1 | Sub-unit categories (`sub_unit_categories`) | [Unit modding](unit_modding.md#unit-categories) | none |
| `units` | 297 | One file per sub-unit; subfolders `equipment`, `critical_parts`, `names*`, `unit_modifiers`, `codenames_operatives` | [Unit modding](unit_modding.md), [Equipment modding](equipment_modding.md), [Division modding](division_modding.md) | `equipment/_documentation.md` |
| `wargoals` | 1 | Wargoal types (`wargoal_types`) | none | none |

Loose files directly in `common/`, 13 in total.

| File | Holds |
| --- | --- |
| `acclimatation.txt` | Acclimatisation rules (units adapt to cold and hot climates; `gain_when` static modifiers) |
| `achievements.txt` | Achievement definitions (8,288 lines); see [Achievement modding](achievement_modding.md) |
| `ai_attitudes.txt` | Attitudes the AI can take toward another nation (`antagonize`, `annex`, `weaken`, `coalition`, ...) |
| `ai_personalities.txt` | AI personalities (vanilla: one empty `ai_balanced`) |
| `alerts.txt` | Alert definitions with a category `HIGH`, `MEDIUM` or `LOW` |
| `combat_tactics.txt` | Combat phases and tactics (tactic names must start with `tactic_` to work with technologies) |
| `event_modifiers.txt` | Empty in vanilla (0 lines); event modifiers live in `modifiers/01_event_modifiers.txt` |
| `graphicalculturetype.txt` | Graphical culture names (`western_european_gfx`, ...) |
| `msgrdk_achievements.json` | Mapping from `pdx_id` to `xbla_id` for achievements |
| `region_colors.txt` | A list of RGB colours (`color = { r g b }`) |
| `script_enums.txt` | Script enums such as `script_enum_operative_mission_type` |
| `triggered_modifiers.txt` | Empty in vanilla (0 lines) |
| `weather.txt` | Weather phenomena and how terrain changes their chance |
