# Mod structure

*Offline snapshot of the Hearts of Iron IV Wiki page "Mod structure", revision 96970, captured 2026-10-31. Wiki text by the wiki's contributors under CC BY-SA 3.0 (see LICENSE.txt); kit blocks are local additions under the same license.*

<!-- kit:begin id="review" at="top" build="1.19.3.0" checked="2026-10-31" revision="96970" sources="launcher-settings.json steam_appid.txt dlc/ localisation/english/loading_tips_l_english.yml common/ pdx_launcher/common/localisation/l_english.yml hoi4.exe" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Checked against: `launcher-settings.json`, `steam_appid.txt`, `dlc/*/*.dlc`, the launcher localisation, vanilla `loading_tips_l_english.yml`, the byte order mark of every vanilla script and localisation file, all 81 folders and 13 loose files under `common/` (28 folders ship documentation), and `hoi4.exe` strings.
Kit blocks added: `mod-structure-workshop-descriptor` (the workshop sample is not a HOI4 descriptor), `mod-structure-descriptors` (which file holds `path`, a 1.19 example), `mod-structure-encoding` (vanilla BOM counts), `mod-structure-loading-tips` (wrong file name and path in the walkthrough), and the common folder index.
Gaps left: no game file defines the descriptor format, so key behaviour rests on launcher texts and `hoi4.exe` strings and stays [unverified]. The thumbnail size and aspect ratio rules and the case-sensitivity note for Mac and Linux cannot be checked on a Windows install. The kit pages named in the index are written separately; their links resolve once those pages are saved.
<!-- kit:end id="review" -->

## Table of contents

- [Mod File Structure](#Mod_File_Structure)
  - [Local Mod](#Local_Mod)
  - [Steam Workshop Mods](#Steam_Workshop_Mods)
- [Creating a New Mod](#Creating_a_New_Mod)
  - [General rules](#General_rules)
  - [Creating a simple local mod](#Creating_a_simple_local_mod)
  - [Creating a Submod](#Creating_a_Submod)
- [Adding Mod Content](#Adding_Mod_Content)
- [Tips](#Tips)
- [See also](#See_also)
- [Kit: common folder index for 1.19.3](#kit-common-folder-index)

---

## Mod File Structure <a id="Mod_File_Structure"></a>

### Local Mod <a id="Local_Mod"></a>

Local Mod files must be located in the folder `~/.local/share/Paradox Interactive/Hearts of Iron IV/mod` or `C:\Users\<Username>\Documents\Paradox Interactive\Hearts of Iron IV\mod`, which must contain:

- **The '.mod' file**, to tell the launcher what to do with the mod-folder (For local use only, any name possible; this file does not get uploaded, when publishing the mod via Steam Workshop)
- **The mod folder** or zip containing the mod data. The mod data must have the same file and folder structure as the game's directory itself.
- **descriptor.mod file** inside the mod folder - this file should contain the same information as the first .mod file (Note: The File must use the descriptor.mod name and must NOT be saved in UTF-8 BOM format)
- Mod picture (optional) - a file named **thumbnail.png** in the mod folder, to serve as Steam Workshop mod picture (Note: Must use .png format and 'thumbnail.png' name; dimensions aren't important but should be 1:1 ratio). In addition, thumbnail files should be less than **1MB** in size, otherwise they cannot be uploaded to ParadoxMods.

The game launcher's mod config tool **can create basic structure automatically**. Just go to *Mods* tab, then click *Mod Tools* and *Create Mod*.
Note that folder and file names are case sensitive on Mac OS X and Linux.

### Steam Workshop Mods <a id="Steam_Workshop_Mods"></a>

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

<!-- kit:begin id="mod-structure-workshop-descriptor" at="section:Steam_Workshop_Mods" -->
**Kit correction** The sample descriptor above is not a current HOI4 descriptor.

- `archive="workshop/content/281990/..."` uses Steam app id `281990`. HOI4's app id is `394360`, the id in the folder path at the start of this section, so the sample was taken from another game or an old layout. The page's own note says mods since 1.9.0 are not stored as `.zip`, so a current Workshop descriptor has no `archive`. [vanilla-confirmed 1.19.3] `steam_appid.txt`.
- `supported_version="1.11.*"` is far behind the installed build `1.19.3.0`. A mod for this build writes `supported_version="1.19.*"`. [vanilla-confirmed 1.19.3] `launcher-settings.json` (`rawVersion`).
- The keys are real. `hoi4.exe` contains the messages "Invalid supported_version in %s" and "Could not find archive for mod: %s" and the key names `remote_file_id` and `user_dir`. [unverified] (strings in `hoi4.exe` only)
- The launcher text "The mod does not have supported_version set." shows that a descriptor without `supported_version` is accepted and only flagged as outdated. [vanilla-confirmed 1.19.3] `pdx_launcher/common/localisation/l_english.yml`.
<!-- kit:end id="mod-structure-workshop-descriptor" -->

## Creating a New Mod <a id="Creating_a_New_Mod"></a>

### General rules <a id="General_rules"></a>

- Mods modify the game with the same file structure as in the vanilla game.
- All appropriate files found in the folder are loaded
- All .txt files should use UTF-8 without BOM format, Localisation files should use UTF-8 BOM Format
- To overwrite the vanilla file, use the same file name
- To add content without changing any vanilla files, use a different file name
- The Game will not check any further than the file directory for changes. If one is trying to add a line to a text file, one must copy the entire text file and add the line within said text file.

<!-- kit:begin id="mod-structure-encoding" at="section:General_rules" -->
**Kit note** Encoding in practice. Vanilla does not follow "no BOM in every `.txt`".

| Vanilla files | With a byte order mark |
| --- | --- |
| `localisation/**/*.yml` | 2,083 of 2,083 |
| `common/**/*.txt` | 235 of 2,218 |
| `events/*.txt` | 87 of 128 |
| `history/**/*.txt` | 942 of 2,058 |
| `interface/*.gfx` and `interface/*.gui` | 0 of 615 |
| `map/**/*.txt` | 0 of 317 |

All rows: [vanilla-confirmed 1.19.3] first three bytes of each file.

Script files that carry a BOM load fine in vanilla, so a BOM in script is tolerated. No BOM stays the safe choice for new script files. Localisation is the strict case: every vanilla `.yml` has the BOM, and `hoi4.exe` contains the message "Localization file '%s' should be in in utf-8-bom encoding". [unverified] (the message is a string in `hoi4.exe`)
<!-- kit:end id="mod-structure-encoding" -->

### Creating a simple local mod <a id="Creating_a_simple_local_mod"></a>

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

<!-- kit:begin id="mod-structure-descriptors" at="section:Creating_a_simple_local_mod" -->
**Kit correction** Which file holds `path`, and an example for 1.19.

The page says `descriptor.mod` "should contain the same information as the first .mod file". The [Modding](<Modding - Hearts of Iron 4 Wiki.md#Mod_structure>) page is more exact: only the user-specific file in `mod/` carries `path`, and `replace_path` has to be written in both files. Follow that page. [unverified] (wiki statement; no game file defines the descriptor format)

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

Vanilla's own DLC descriptors, such as `dlc/dlc049_no_compromise_no_surrender/dlc049.dlc`, use the same `key = value` syntax. Their `path` is relative to the game folder, uses forward slashes and is written without quotes. [vanilla-confirmed 1.19.3] `dlc/*/dlc*.dlc`.
<!-- kit:end id="mod-structure-descriptors" -->

### Creating a Submod <a id="Creating_a_Submod"></a>

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

## Adding Mod Content <a id="Adding_Mod_Content"></a>

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

<!-- kit:begin id="mod-structure-loading-tips" at="section:Adding_Mod_Content" -->
**Kit correction** The loading tips walkthrough names the wrong file and the wrong place.

- The vanilla file is `localisation/english/loading_tips_l_english.yml`, with a lowercase L in `_l_`. The page writes `loading_tips_I_english.yml` (capital I) and `loading_tips_L_english.yml` (capital L). Use the vanilla spelling: all 2,081 language files in vanilla use lowercase `_l_`. [vanilla-confirmed 1.19.3] `localisation/*/*.yml`.
- The file sits in the `english` subfolder. The page's tree puts the copy directly in `localisation/`, which is a different path and so, by the same-name-same-place rule on the [Modding](<Modding - Hearts of Iron 4 Wiki.md#Loading_files>) page, a second file instead of a replacement. [vanilla-confirmed 1.19.3] `localisation/english/` for the folder; the rule is [unverified].
- Vanilla defines 163 tips, `LOADING_TIP_0` to `LOADING_TIP_162`, written without a version number (`LOADING_TIP_0: "text"`). A mod file that only defines `LOADING_TIP_0` leaves the other 162 tips in place. The page's result "the only quote shown will be Test1 mod" needs a file that replaces the vanilla one at the same relative path (`localisation/english/loading_tips_l_english.yml`) and defines nothing else. [vanilla-confirmed 1.19.3] `localisation/english/loading_tips_l_english.yml`; the replacement rule is [unverified] (per the [Modding](<Modding - Hearts of Iron 4 Wiki.md#Loading_files>) page).
<!-- kit:end id="mod-structure-loading-tips" -->

## Tips <a id="Tips"></a>

- To understand how certain things in the code work, it can be useful to look into game files and search for things similar to what your mod is supposed to change
- Alternatively, you can search the files of other users' mods in `...\steamapps\workshop\content\394360`
- Try to minimize vanilla file overwrites, this will make it both easier for you to manage your mod content to keep it up to date and reduce risk of conflict with other mods
- When testing the mod, it can be very useful to look into Error log `...\Documents\Paradox Interactive\Hearts of Iron IV\logs\error.log` to gain a clue when something isn't working
- To keep your mod updated between smaller updates, replace the third number in your version with a \*. For example, replace "1.5.4" with "1.5.\*" to make that mod work with all versions of 1.5

## See also <a id="See_also"></a>

Depending on what your mod is supposed to do, you may want to visit some of these pages relating to some more basic game content modding:

- [Country creation](<Country creation - Hearts of Iron 4 Wiki.md>) - How to create a new country, assign flag, place the new country into the game
- National Focus modding - How to edit National Focus tree
- [Idea modding](<Idea modding - Hearts of Iron 4 Wiki.md>) - How to add/edit National Ideas
- [Event modding](<Event modding - Hearts of Iron 4 Wiki.md>) - How to add/edit an Event

<!-- kit:begin id="common-folder-index" at="bottom" -->
## Kit: common folder index for 1.19.3 <a id="kit-common-folder-index"></a>

**Kit addition** `GAME\common\` holds 81 folders and 13 loose files in 1.19.3. Each folder is read for the entries named in its row; a file's name inside a folder rarely matters (see the exceptions in the [Modding](<Modding - Hearts of Iron 4 Wiki.md#Notes>) notes). "Files" counts every file under the folder in vanilla, documentation included. "Doc" names the game's own documentation for that folder: 28 of the 81 folders have one, some only in a subfolder. Open it before writing entries. [vanilla-confirmed 1.19.3] `common/`.

All rows: file lists and file heads are [vanilla-confirmed 1.19.3] under `common/`; every name in the Doc column is [docs] `common/<folder>/`. The links to Collection modding, Game rule modding, Intelligence operation modding, Map mode modding, Occupation and resistance modding, Peace conference modding, Raid modding, Script constant modding and Special project modding point to kit pages of this snapshot.

| Folder | Files | Defines | Snapshot page | Doc |
| --- | --- | --- | --- | --- |
| `abilities` | 6 | Unit leader abilities a commander can trigger (`ability = { type = army_leader ... }`) | [Character modding (`enable_ability`)](<Character modding - Hearts of Iron 4 Wiki.md>) | none |
| `aces` | 1 | Air ace modifier tags per aircraft type, with a chance (`modifiers = { }`) | [Effects (`add_ace`)](<Effects - Hearts of Iron 4 Wiki.md>) | none |
| `ai_areas` | 1 | Named groups of strategic regions for AI strategies (`areas = { }`) | [AI modding](<AI modding - Hearts of Iron 4 Wiki.md#AI_areas>) | none |
| `ai_equipment` | 23 | AI equipment design groups: roles, modules, priorities | [AI modding](<AI modding - Hearts of Iron 4 Wiki.md#AI_equipment>) | `_documentation.md` |
| `ai_faction_theaters` | 2 | Theaters (connected strategic region sets) the AI faction leader assigns members to | none | `_documentation.md` |
| `ai_focuses` | 8 | AI focus presets that weight research per focus name | [AI focuses](<AI focuses - Hearts of Iron 4 Wiki.md>) | none |
| `ai_navy` | 26 | Goal-based naval AI: fleets, goals and taskforce roles (subfolders `fleet`, `goals`, `taskforce`) | none | `_documentation.md`, `taskforce/_documentation.md` |
| `ai_strategy` | 50 | AI strategy entries that weight AI behaviour (alliances, wars, unit roles, areas) | [AI modding](<AI modding - Hearts of Iron 4 Wiki.md#AI_strategies>) | `_documentation.md` |
| `ai_strategy_plans` | 128 | Per-country AI strategy plans | [AI modding](<AI modding - Hearts of Iron 4 Wiki.md#AI_strategy_plans>) | none |
| `ai_templates` | 16 | Target division templates the AI upgrades toward, by role | [AI modding](<AI modding - Hearts of Iron 4 Wiki.md#AI_templates>) | `_documentation.md` |
| `autonomous_states` | 21 | Autonomy states (`autonomy_state`) | [Autonomy state modding](<Autonomy state modding - Hearts of Iron 4 Wiki.md>) | none |
| `bookmarks` | 2 | Start-date bookmarks and their country entries | [Bookmark modding](<Bookmark modding - Hearts of Iron 4 Wiki.md>) | none |
| `bop` | 10 | Balance of power definitions | [Balance of power modding](<Balance of power modding - Hearts of Iron 4 Wiki.md>) | none |
| `buildings` | 2 | Building types, spawn points and landmark buildings | [Building modding](<Building modding - Hearts of Iron 4 Wiki.md>) | none |
| `characters` | 233 | Character database (`characters = { }`), one file per country group | [Character modding](<Character modding - Hearts of Iron 4 Wiki.md>) | `_documentation.md` |
| `collections` | 3 | Named script collections (`prefix:name` inputs for collection triggers) | [Collection modding](<Collection modding - Hearts of Iron 4 Wiki.md>) | `_documentation.md` |
| `continuous_focus` | 1 | Continuous focus palettes | [National focus modding](<National focus modding - Hearts of Iron 4 Wiki.md#Continuous_focuses>) | none |
| `countries` | 442 | Country definition files (colour, graphical culture) plus `colors.txt` and `cosmetic.txt` | [Country creation](<Country creation - Hearts of Iron 4 Wiki.md>) | none |
| `country_leader` | 4 | Country leader traits (`leader_traits`) | [Character modding](<Character modding - Hearts of Iron 4 Wiki.md#Country_leader_traits>) | none |
| `country_tag_aliases` | 1 | Country tag aliases usable as scopes | [Data structures](<Data structures - Hearts of Iron 4 Wiki.md#Country_tag_aliases>) | none |
| `country_tags` | 2 | The list of country tags and the file each tag points to | [Country creation](<Country creation - Hearts of Iron 4 Wiki.md>) | none |
| `decisions` | 146 | Decisions and missions; categories in `categories/` | [Decision modding](<Decision modding - Hearts of Iron 4 Wiki.md>) | `_documentation.md` |
| `defines` | 3 | Lua defines (`NDefines`) | [Defines](<Defines - Hearts of Iron 4 Wiki.md>) | none |
| `difficulty_settings` | 1 | Custom difficulty settings: a modifier with a multiplier for listed countries | [Bookmark modding](<Bookmark modding - Hearts of Iron 4 Wiki.md#Difficulty_settings>) | none |
| `doctrines` | 27 | Doctrine folders, tracks, grand doctrines and subdoctrines (four subfolders) | [Doctrine modding](<Doctrine modding - Hearts of Iron 4 Wiki.md>) | `_documentation.md`, `folders/_documentation.md`, `grand_doctrines/_documentation.md`, `subdoctrines/_documentation.md`, `tracks/_documentation.md` |
| `dynamic_modifiers` | 11 | Dynamic modifiers (modifiers driven by variables) | [Modifiers](<Modifiers - Hearts of Iron 4 Wiki.md#Dynamic_modifiers>) | none |
| `equipment_groups` | 2 | Named groups of equipment types, used by MIO categories and equipment bonuses | [Equipment modding](<Equipment modding - Hearts of Iron 4 Wiki.md>) | `_documentation.md` |
| `factions` | 30 | Faction goals, icons, member upgrades and rules (four subfolders) | [Faction modding](<Faction modding - Hearts of Iron 4 Wiki.md>) | `_documentation.md` |
| `focus_inlay_windows` | 7 | Inlay windows shown inside a focus tree | [National focus modding](<National focus modding - Hearts of Iron 4 Wiki.md#Inlay_window>) | `documentation.md` |
| `frontend` | 1 | Main-menu background database (`backgrounds/base_backgrounds.txt`) | none | none |
| `game_rules` | 1 | Game rule definitions and their options | [Game rule modding](<Game rule modding - Hearts of Iron 4 Wiki.md>), [Bookmark modding](<Bookmark modding - Hearts of Iron 4 Wiki.md#Game_rules>) | none |
| `generation` | 1 | `idea_generation`: trait conditions for generated advisors, chiefs and theorists (mostly empty in vanilla) | none | none |
| `idea_tags` | 1 | Idea categories (slots) and slot ledgers | [Idea modding](<Idea modding - Hearts of Iron 4 Wiki.md#Other_idea_categories>) | none |
| `ideas` | 213 | Ideas, national spirits, laws and advisor ideas | [Idea modding](<Idea modding - Hearts of Iron 4 Wiki.md>) | none |
| `ideologies` | 1 | Ideology groups, ideologies and party names | [Ideology modding](<Ideology modding - Hearts of Iron 4 Wiki.md>) | none |
| `intelligence_agencies` | 1 | Intelligence agency names and logos | [Intelligence agency modding](<Intelligence agency modding - Hearts of Iron 4 Wiki.md>) | none |
| `intelligence_agency_upgrades` | 2 | Agency upgrade branches and upgrades | [Intelligence agency modding](<Intelligence agency modding - Hearts of Iron 4 Wiki.md>) | `_documentation.md` |
| `map_modes` | 1 | Scripted map modes (vanilla ships only the documentation, no definitions) | [Map mode modding](<Map mode modding - Hearts of Iron 4 Wiki.md>) | `documentation.md` |
| `medals` | 1 | Career profile medals with bronze, silver and gold tiers | none | none |
| `military_industrial_organization` | 63 | MIO organizations, policies and AI bonus weights (three subfolders) | [Military industrial organization modding](<Military industrial organization modding - Hearts of Iron 4 Wiki.md>) | `ai_bonus_weights/_documentation.md`, `organizations/_documentation.md`, `policies/_documentation.md` |
| `modifier_definitions` | 2 | Modifier definitions (colour, value type, category) | [Modifiers](<Modifiers - Hearts of Iron 4 Wiki.md#Modifier_definitions>) | none |
| `modifiers` | 5 | Static modifiers, event modifiers and balance-of-power modifiers | [Modifiers](<Modifiers - Hearts of Iron 4 Wiki.md#Static_modifiers>) | none |
| `mtth` | 1 | MTTH variables read as `mtth:name` | [Data structures](<Data structures - Hearts of Iron 4 Wiki.md#MTTH_variables>) | none |
| `names` | 1 | Random name pools per tag: characters, aces, callsigns and operation names | [Country creation](<Country creation - Hearts of Iron 4 Wiki.md#Character_names>) | none |
| `national_focus` | 81 | Focus trees, shared and joint focuses, titlebar styles, search filters | [National focus modding](<National focus modding - Hearts of Iron 4 Wiki.md>) | none |
| `occupation_laws` | 1 | Occupation laws | [Occupation and resistance modding](<Occupation and resistance modding - Hearts of Iron 4 Wiki.md>) | none |
| `on_actions` | 18 | On-action hooks (`on_actions = { }`) | [On actions](<On actions - Hearts of Iron 4 Wiki.md>) | `_documentation.md` |
| `operation_phases` | 17 | Phases of intelligence operations | [Intelligence operation modding](<Intelligence operation modding - Hearts of Iron 4 Wiki.md>) | `_documentation.md` |
| `operation_tokens` | 2 | Tokens that operations require or grant | [Intelligence operation modding](<Intelligence operation modding - Hearts of Iron 4 Wiki.md>) | `_documentation.md` |
| `operations` | 7 | Intelligence operations | [Intelligence operation modding](<Intelligence operation modding - Hearts of Iron 4 Wiki.md>) | `_documentation.md` |
| `opinion_modifiers` | 13 | Opinion modifiers | [Modifiers](<Modifiers - Hearts of Iron 4 Wiki.md#Opinion_modifiers>) | none |
| `peace_conference` | 36 | Peace conference actions, categories, cost modifiers and AI desires | [Peace conference modding](<Peace conference modding - Hearts of Iron 4 Wiki.md>) | `ai_peace/_documentation.md`, `cost_modifiers/_documentation.md` |
| `profile_backgrounds` | 1 | Unlockable career profile backgrounds | none | none |
| `profile_pictures` | 1 | Unlockable career profile pictures | none | none |
| `raids` | 10 | Raid types and categories | [Raid modding](<Raid modding - Hearts of Iron 4 Wiki.md>) | `_documentation.md` |
| `resistance_activity` | 1 | Resistance activity (sabotage) types | [Occupation and resistance modding](<Occupation and resistance modding - Hearts of Iron 4 Wiki.md>) | none |
| `resistance_compliance_modifiers` | 2 | Modifiers applied at compliance and resistance thresholds | [Occupation and resistance modding](<Occupation and resistance modding - Hearts of Iron 4 Wiki.md>) | none |
| `resources` | 2 | Resource definitions | [Resources modding](<Resources modding - Hearts of Iron 4 Wiki.md>) | `_documentation.md` |
| `ribbons` | 1 | Career profile ribbons | none | none |
| `scientist_traits` | 2 | Scientist traits (they apply to special projects only) | [Special project modding](<Special project modding - Hearts of Iron 4 Wiki.md>) | `_documentation.md` |
| `scorers` | 4 | AI country scorers (`scorers/country/`) | [Data structures](<Data structures - Hearts of Iron 4 Wiki.md#Scorers>) | none |
| `script_constants` | 5 | Script constants (`constant:group.name`) | [Script constant modding](<Script constant modding - Hearts of Iron 4 Wiki.md>) | `documentation.md` |
| `scripted_diplomatic_actions` | 1 | Scripted diplomatic actions (vanilla ships only a commented template) | [Scripted GUI modding](<Scripted GUI modding - Hearts of Iron 4 Wiki.md>) | none |
| `scripted_effects` | 52 | Scripted effects | [Effects](<Effects - Hearts of Iron 4 Wiki.md#Scripted_effects>) | none |
| `scripted_guis` | 18 | Scripted GUI definitions | [Scripted GUI modding](<Scripted GUI modding - Hearts of Iron 4 Wiki.md>) | `_documentation.md` |
| `scripted_localisation` | 42 | Scripted localisation (`defined_text`) | [Localisation](<Localisation - Hearts of Iron 4 Wiki.md#Scripted_localisation>) | none |
| `scripted_triggers` | 54 | Scripted triggers | [Triggers](<Triggers - Hearts of Iron 4 Wiki.md#Scripted_triggers>) | none |
| `special_projects` | 17 | Special projects, project tags, prototype rewards and specialisations (four subfolders) | [Special project modding](<Special project modding - Hearts of Iron 4 Wiki.md>) | `special_projects_documentation.md`, `projects/documentation.md`, `prototype_rewards/documentation.md`, `specialization/documentation.md` |
| `state_category` | 13 | State categories (building slots per category) | [State modding](<State modding - Hearts of Iron 4 Wiki.md#State_categories>) | none |
| `strategic_locations` | 2 | Strategic locations: extra province building levels, applied with `strategic_state_location` | none | `documentation.md` |
| `synchronized_dynamic_tokens` | 1 | One token per line (53 lines of resource, equipment, building and ideology names); purpose not documented | none | none |
| `technologies` | 13 | Technologies | [Technology modding](<Technology modding - Hearts of Iron 4 Wiki.md>) | none |
| `technology_sharing` | 11 | Technology sharing groups | [Technology modding](<Technology modding - Hearts of Iron 4 Wiki.md#Technology_sharing_groups>) | none |
| `technology_tags` | 1 | Technology categories and technology folders | [Technology modding](<Technology modding - Hearts of Iron 4 Wiki.md#Categories>) | none |
| `terrain` | 1 | Terrain categories and graphical terrain | [Map modding](<Map modding - Hearts of Iron 4 Wiki.md#Provincial_terrain>) | none |
| `timed_activities` | 1 | Equipment needs of timed activities (vanilla: `stage_coup`) | none | none |
| `unit_leader` | 13 | Unit leader traits and skill-level definitions | [Character modding](<Character modding - Hearts of Iron 4 Wiki.md#Unit_leader_traits>) | none |
| `unit_medals` | 1 | Unit medals and the unit modifiers they grant | none | none |
| `unit_tags` | 1 | Sub-unit categories (`sub_unit_categories`) | [Unit modding](<Unit modding - Hearts of Iron 4 Wiki.md#Unit_Categories>) | none |
| `units` | 297 | One file per sub-unit; subfolders `equipment`, `critical_parts`, `names*`, `unit_modifiers`, `codenames_operatives` | [Unit modding](<Unit modding - Hearts of Iron 4 Wiki.md>), [Equipment modding](<Equipment modding - Hearts of Iron 4 Wiki.md>), [Division modding](<Division modding - Hearts of Iron 4 Wiki.md>) | `equipment/_documentation.md` |
| `wargoals` | 1 | Wargoal types (`wargoal_types`) | none | none |

Loose files directly in `common/`, 13 in total. [vanilla-confirmed 1.19.3] `common/*.txt`, `common/msgrdk_achievements.json`.

| File | Holds |
| --- | --- |
| `acclimatation.txt` | Acclimatisation rules (units adapt to cold and hot climates; `gain_when` static modifiers) |
| `achievements.txt` | Achievement definitions (8,288 lines); see [Achievement modding](<Achievement modding - Hearts of Iron 4 Wiki.md>) |
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
<!-- kit:end id="common-folder-index" -->

---

## Navigation

**[Modding](<Modding - Hearts of Iron 4 Wiki.md>)**

- **Documentation**: [Effects](<Effects - Hearts of Iron 4 Wiki.md>) • [Triggers](<Triggers - Hearts of Iron 4 Wiki.md>) • [Defines](<Defines - Hearts of Iron 4 Wiki.md>) • [Modifiers](<Modifiers - Hearts of Iron 4 Wiki.md>) • [List of modifiers](<List of modifiers - Hearts of Iron 4 Wiki.md>) • [Scopes](<Scopes - Hearts of Iron 4 Wiki.md>) • [Localisation](<Localisation - Hearts of Iron 4 Wiki.md>) • [On actions](<On actions - Hearts of Iron 4 Wiki.md>) • [Data structures](<Data structures - Hearts of Iron 4 Wiki.md>) • [Flags](<Data structures - Hearts of Iron 4 Wiki.md#Flags>) • [Event targets](<Data structures - Hearts of Iron 4 Wiki.md#Event_targets>) • [Country tag aliases](<Data structures - Hearts of Iron 4 Wiki.md#Country_tag_aliases>) • [Variables](<Data structures - Hearts of Iron 4 Wiki.md#Variables>) • [Arrays](<Data structures - Hearts of Iron 4 Wiki.md#Arrays>)
- **Scripting**: [Achievements](<Achievement modding - Hearts of Iron 4 Wiki.md>) • [AI](<AI modding - Hearts of Iron 4 Wiki.md>) • [AI focuses](<AI focuses - Hearts of Iron 4 Wiki.md>) • [Autonomous states](<Autonomy state modding - Hearts of Iron 4 Wiki.md>) • [Balances of power](<Balance of power modding - Hearts of Iron 4 Wiki.md>) • [Bookmarks/Scenarios](<Bookmark modding - Hearts of Iron 4 Wiki.md>) • [Game rules](<Bookmark modding - Hearts of Iron 4 Wiki.md#Game_rules>) • [Buildings](<Building modding - Hearts of Iron 4 Wiki.md>) • [Characters and traits](<Character modding - Hearts of Iron 4 Wiki.md>) • [Cosmetic tags](<Cosmetic tag modding - Hearts of Iron 4 Wiki.md>) • [Countries](<Country creation - Hearts of Iron 4 Wiki.md>) • [Divisions](<Division modding - Hearts of Iron 4 Wiki.md>) • [Decisions](<Decision modding - Hearts of Iron 4 Wiki.md>) • [Doctrines](<Doctrine modding - Hearts of Iron 4 Wiki.md>) • [Equipment](<Equipment modding - Hearts of Iron 4 Wiki.md>) • [Events](<Event modding - Hearts of Iron 4 Wiki.md>) • [Factions](<Faction modding - Hearts of Iron 4 Wiki.md>) • [Ideas](<Idea modding - Hearts of Iron 4 Wiki.md>) • [Ideologies](<Ideology modding - Hearts of Iron 4 Wiki.md>) • [Military industrial organizations](<Military industrial organization modding - Hearts of Iron 4 Wiki.md>) • [National focuses](<National focus modding - Hearts of Iron 4 Wiki.md>) • [Resources](<Resources modding - Hearts of Iron 4 Wiki.md>) • [Scripted GUI](<Scripted GUI modding - Hearts of Iron 4 Wiki.md>) • [Technologies and doctrines](<Technology modding - Hearts of Iron 4 Wiki.md>) • [Units](<Unit modding - Hearts of Iron 4 Wiki.md>)
- **Map**: [Map](<Map modding - Hearts of Iron 4 Wiki.md>) • [States](<State modding - Hearts of Iron 4 Wiki.md>) • [Supply areas](<Supply areas modding - Hearts of Iron 4 Wiki.md>) • [Strategic regions](<Strategic region modding - Hearts of Iron 4 Wiki.md>)
- **Graphical**: [Interface](<Interface modding - Hearts of Iron 4 Wiki.md>) • [Graphical assets](<Graphical asset modding - Hearts of Iron 4 Wiki.md>) • [Entities](<Entity modding - Hearts of Iron 4 Wiki.md>) • [Posteffects](<Posteffect modding - Hearts of Iron 4 Wiki.md>) • [Particles](<Particle modding - Hearts of Iron 4 Wiki.md>) • [Fonts](<Font modding - Hearts of Iron 4 Wiki.md>)
- **Cosmetic**: [Portraits](<Portrait modding - Hearts of Iron 4 Wiki.md>) • [Namelists](<Namelist modding - Hearts of Iron 4 Wiki.md>) • [Music](<Music modding - Hearts of Iron 4 Wiki.md>) • [Sound](<Sound modding - Hearts of Iron 4 Wiki.md>)
- **Other**: [Console commands](<Console commands - Hearts of Iron 4 Wiki.md>) • [Troubleshooting](<Troubleshooting - Hearts of Iron 4 Wiki.md>) • [Mods](<Mods - Hearts of Iron 4 Wiki.md>) • [Nudger](<Nudger - Hearts of Iron 4 Wiki.md>)
- **Kit pages (not on the wiki)**: [Collection modding](<Collection modding - Hearts of Iron 4 Wiki.md>) • [Game rule modding](<Game rule modding - Hearts of Iron 4 Wiki.md>) • [Intelligence operation modding](<Intelligence operation modding - Hearts of Iron 4 Wiki.md>) • [Map mode modding](<Map mode modding - Hearts of Iron 4 Wiki.md>) • [Occupation and resistance modding](<Occupation and resistance modding - Hearts of Iron 4 Wiki.md>) • [Peace conference modding](<Peace conference modding - Hearts of Iron 4 Wiki.md>) • [Raid modding](<Raid modding - Hearts of Iron 4 Wiki.md>) • [Script constant modding](<Script constant modding - Hearts of Iron 4 Wiki.md>) • [Special project modding](<Special project modding - Hearts of Iron 4 Wiki.md>)
