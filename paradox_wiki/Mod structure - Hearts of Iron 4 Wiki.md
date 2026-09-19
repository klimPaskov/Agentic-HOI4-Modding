# Mod structure

*Offline snapshot of the Hearts of Iron IV Wiki page "Mod structure", captured 2026-09-19.*

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

---

### Mod File Structure <a id="Mod_File_Structure"></a>

#### Local Mod <a id="Local_Mod"></a>

Local Mod files must be located in the folder `~/.local/share/Paradox Interactive/Hearts of Iron IV/mod` or `C:\Users\<Username>\Documents\Paradox Interactive\Hearts of Iron IV\mod`, which must contain:

- **The '.mod' file**, to tell the launcher what to do with the mod-folder (For local use only, any name possible; this file does not get uploaded, when publishing the mod via Steam Workshop)
- **The mod folder** or zip containing the mod data. The mod data must have the same file and folder structure as the game's directory itself.
- **descriptor.mod file** inside the mod folder - this file should contain the same information as the first .mod file (Note: The File must use the descriptor.mod name and must NOT be saved in UTF-8 BOM format)
- Mod picture (optional) - a file named **thumbnail.png** in the mod folder, to serve as Steam Workshop mod picture (Note: Must use .png format and 'thumbnail.png' name; dimensions aren't important but should be 1:1 ratio). In addition, thumbnail files should be less than **1MB** in size, otherwise they cannot be uploaded to ParadoxMods.

The game launcher's mod config tool **can create basic structure automatically**. Just go to *Mods* tab, then click *Mod Tools* and *Create Mod*.
Note that folder and file names are case sensitive on Mac OS X and Linux.

#### Steam Workshop Mods <a id="Steam_Workshop_Mods"></a>

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

### Creating a New Mod <a id="Creating_a_New_Mod"></a>

#### General rules <a id="General_rules"></a>

- Mods modify the game with the same file structure as in the vanilla game.
- All appropriate files found in the folder are loaded
- All .txt files should use UTF-8 without BOM format, Localisation files should use UTF-8 BOM Format
- To overwrite the vanilla file, use the same file name
- To add content without changing any vanilla files, use a different file name
- The Game will not check any further than the file directory for changes. If one is trying to add a line to a text file, one must copy the entire text file and add the line within said text file.

#### Creating a simple local mod <a id="Creating_a_simple_local_mod"></a>

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

#### Creating a Submod <a id="Creating_a_Submod"></a>

Sometimes you will want your mod to depend on other mods, and also require a certain loading order. Mods will usually load in alphabetical order (so the mod last in the list will overwrite the earlier). But some things may affect this so if you need a certain load order and be clear that you have dependencies this needs to be specified by including its full name in the .mod file under "dependencies".

```text
name="testmodB"
path="mod/testmodb/"

## this guarantees we load testmodA first before our testmodB is loaded
dependencies= {
	"testmodA"
}
supported_version="1.11.*"
```

### Adding Mod Content <a id="Adding_Mod_Content"></a>

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

### Tips <a id="Tips"></a>

- To understand how certain things in the code work, it can be useful to look into game files and search for things similar to what your mod is supposed to change
- Alternatively, you can search the files of other users' mods in `...\steamapps\workshop\content\394360`
- Try to minimize vanilla file overwrites, this will make it both easier for you to manage your mod content to keep it up to date and reduce risk of conflict with other mods
- When testing the mod, it can be very useful to look into Error log `...\Documents\Paradox Interactive\Hearts of Iron IV\logs\error.log` to gain a clue when something isn't working
- To keep your mod updated between smaller updates, replace the third number in your version with a \*. For example, replace "1.5.4" with "1.5.\*" to make that mod work with all versions of 1.5

### See also <a id="See_also"></a>

Depending on what your mod is supposed to do, you may want to visit some of these pages relating to some more basic game content modding:

- [Country creation](<Country creation - Hearts of Iron 4 Wiki.md>) - How to create a new country, assign flag, place the new country into the game
- National Focus modding - How to edit National Focus tree
- [Idea modding](<Idea modding - Hearts of Iron 4 Wiki.md>) - How to add/edit National Ideas
- [Event modding](<Event modding - Hearts of Iron 4 Wiki.md>) - How to add/edit an Event

---

## Navigation

**[Modding](<Modding - Hearts of Iron 4 Wiki.md>)**

- **Documentation**: [Effects](<Effects - Hearts of Iron 4 Wiki.md>) • [Triggers](<Triggers - Hearts of Iron 4 Wiki.md>) • [Defines](<Defines - Hearts of Iron 4 Wiki.md>) • [Modifiers](<Modifiers - Hearts of Iron 4 Wiki.md>) • [List of modifiers](<List of modifiers - Hearts of Iron 4 Wiki.md>) • [Scopes](<Scopes - Hearts of Iron 4 Wiki.md>) • [Localisation](<Localisation - Hearts of Iron 4 Wiki.md>) • [On actions](<On actions - Hearts of Iron 4 Wiki.md>) • [Data structures](<Data structures - Hearts of Iron 4 Wiki.md>) • [Flags](<Data structures - Hearts of Iron 4 Wiki.md#Flags>) • [Event targets](<Data structures - Hearts of Iron 4 Wiki.md#Event_targets>) • [Country tag aliases](<Data structures - Hearts of Iron 4 Wiki.md#Country_tag_aliases>) • [Variables](<Data structures - Hearts of Iron 4 Wiki.md#Variables>) • [Arrays](<Data structures - Hearts of Iron 4 Wiki.md#Arrays>)
- **Scripting**: [Achievements](<Achievement modding - Hearts of Iron 4 Wiki.md>) • [AI](<AI modding - Hearts of Iron 4 Wiki.md>) • [AI focuses](<AI focuses - Hearts of Iron 4 Wiki.md>) • [Autonomous states](<Autonomy state modding - Hearts of Iron 4 Wiki.md>) • [Balances of power](<Balance of power modding - Hearts of Iron 4 Wiki.md>) • [Bookmarks/Scenarios](<Bookmark modding - Hearts of Iron 4 Wiki.md>) • [Game rules](<Bookmark modding - Hearts of Iron 4 Wiki.md#Game_rules>) • [Buildings](<Building modding - Hearts of Iron 4 Wiki.md>) • [Characters and traits](<Character modding - Hearts of Iron 4 Wiki.md>) • [Cosmetic tags](<Cosmetic tag modding - Hearts of Iron 4 Wiki.md>) • [Countries](<Country creation - Hearts of Iron 4 Wiki.md>) • [Divisions](<Division modding - Hearts of Iron 4 Wiki.md>) • [Decisions](<Decision modding - Hearts of Iron 4 Wiki.md>) • [Doctrines](<Doctrine modding - Hearts of Iron 4 Wiki.md>) • [Equipment](<Equipment modding - Hearts of Iron 4 Wiki.md>) • [Events](<Event modding - Hearts of Iron 4 Wiki.md>) • [Factions](<Faction modding - Hearts of Iron 4 Wiki.md>) • [Ideas](<Idea modding - Hearts of Iron 4 Wiki.md>) • [Ideologies](<Ideology modding - Hearts of Iron 4 Wiki.md>) • [Military industrial organizations](<Military industrial organization modding - Hearts of Iron 4 Wiki.md>) • [National focuses](<National focus modding - Hearts of Iron 4 Wiki.md>) • [Resources](<Resources modding - Hearts of Iron 4 Wiki.md>) • [Scripted GUI](<Scripted GUI modding - Hearts of Iron 4 Wiki.md>) • [Technologies and doctrines](<Technology modding - Hearts of Iron 4 Wiki.md>) • [Units](<Unit modding - Hearts of Iron 4 Wiki.md>)
- **Map**: [Map](<Map modding - Hearts of Iron 4 Wiki.md>) • [States](<State modding - Hearts of Iron 4 Wiki.md>) • [Supply areas](<Supply areas modding - Hearts of Iron 4 Wiki.md>) • [Strategic regions](<Strategic region modding - Hearts of Iron 4 Wiki.md>)
- **Graphical**: [Interface](<Interface modding - Hearts of Iron 4 Wiki.md>) • [Graphical assets](<Graphical asset modding - Hearts of Iron 4 Wiki.md>) • [Entities](<Entity modding - Hearts of Iron 4 Wiki.md>) • [Posteffects](<Posteffect modding - Hearts of Iron 4 Wiki.md>) • [Particles](<Particle modding - Hearts of Iron 4 Wiki.md>) • [Fonts](<Font modding - Hearts of Iron 4 Wiki.md>)
- **Cosmetic**: [Portraits](<Portrait modding - Hearts of Iron 4 Wiki.md>) • [Namelists](<Namelist modding - Hearts of Iron 4 Wiki.md>) • [Music](<Music modding - Hearts of Iron 4 Wiki.md>) • [Sound](<Sound modding - Hearts of Iron 4 Wiki.md>)
- **Other**: [Console commands](<Console commands - Hearts of Iron 4 Wiki.md>) • [Troubleshooting](<Troubleshooting - Hearts of Iron 4 Wiki.md>) • [Mods](<Mods - Hearts of Iron 4 Wiki.md>) • [Nudger](<Nudger - Hearts of Iron 4 Wiki.md>)
