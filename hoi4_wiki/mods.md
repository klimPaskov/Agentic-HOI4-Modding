# Mods

*For information on the structure and making of mods, see [modding](modding.md)*

A **Mod**, short for *modification*, is an alteration of the game files to change the game's functionality. It also makes it more fun. You can add cheats like EasyBuff or Go back to WW1 in The Great War Redux.

## Good practice

Make sure that your mod contains a good description of what it does, as well as having a good front page image.

## Installation

Mods can be installed manually from sources such as the Paradox Forums, installed automatically from Paradox Mods by the launcher or via the Steam Workshop.

The folder that stores mods for the game is:

- Windows: `...\Documents\Paradox Interactive\Hearts of Iron IV\mod\`
- GNU/Linux: `~/.local/share/Paradox Interactive/Hearts of Iron IV/mod/`
- Mac: `~/Documents/Paradox Interactive/Hearts of Iron IV/mod/`

Manually downloaded mods should include a *.mod* text file along with a folder. If so, the files can simply be dropped into the mod folder. If one is downloading a newer version of a mod they already have installed, one should remove the older files first.

## Mod lists

- Paradox official mod list

How a list of enabled mods reaches the game in 1.19.4.1.

- The launcher keeps the ordered list of enabled mods (a playset). At start the game reads the enabled mods from `dlc_load.json` in the user directory, which also carries the disabled DLCs. `hoi4.exe` contains the strings `dlc_load.json`, `enabled_mods`, `disabled_dlcs` and `mods_registry.json`. The format of `dlc_load.json` is described on [Modding](modding.md#mod-structure). (unverified) (file names found only as strings in `hoi4.exe`)
- A mod appears as "outdated" in the launcher when its `supported_version` does not fit the game. The launcher text says either "The mod does not have supported_version set." or "The mod supports version ...". The installed build is `1.19.4.1`, so a mod that targets it uses `supported_version = "1.19.*"` or `"1.19.4.1"`.
- The Steam Workshop folder name is the game's Steam app id: `steam_appid.txt` is `394360`, matching `workshop/content/394360` on [Mod structure](mod_structure.md#steam-workshop-mods).

## Mods with Wiki pages

*Wiki pages for modifications are the responsibility of the modification team, not the Paradox wiki team*

- Ancient Formable Nations
- Equestria At War
- HOI4 ULTRA (Historical Industry Project)
- Kaiserreich
- The Road to 56
- Victoria 2 to Hearts of Iron IV converter
- Victoria 3 to Hearts of Iron IV converter
