# Mods

*Offline snapshot of the Hearts of Iron IV Wiki page "Mods", revision 105602, captured 2026-10-31. Wiki text by the wiki's contributors under CC BY-SA 3.0 (see LICENSE.txt); kit blocks are local additions under the same license.*

<!-- kit:begin id="review" at="top" build="1.19.3.0" checked="2026-10-31" revision="105602" sources="launcher-settings.json steam_appid.txt pdx_launcher/common/localisation/l_english.yml hoi4.exe" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Checked against: `launcher-settings.json`, `steam_appid.txt`, the launcher localisation in `pdx_launcher/` and strings in `hoi4.exe`. No statement on the page was found to be wrong for 1.19.3.
Kit blocks added: `mods-mod-lists` (fills the empty "Mod lists" section).
Gaps left: what the Paradox Mods site, the Steam Workshop and the "Paradox official mod list" currently offer cannot be checked from the game files. The Linux and Mac folder paths were not checked (Windows install only).
<!-- kit:end id="review" -->

## Table of contents

- [Good practice](#Good_practice)
- [Installation](#Installation)
- [Mod lists](#Mod_lists)
- [Mods with Wiki pages](#Mods_with_Wiki_pages)

---

*For information on the structure and making of mods, see [modding](<Modding - Hearts of Iron 4 Wiki.md>)*

A **Mod**, short for *modification*, is an alteration of the game files to change the game's functionality. It also makes it more fun. You can add cheats like EasyBuff or Go back to WW1 in The Great War Redux.

## Good practice <a id="Good_practice"></a>

Make sure that your mod contains a good description of what it does, as well as having a good front page image.

## Installation <a id="Installation"></a>

Mods can be installed manually from sources such as the Paradox Forums, installed automatically from Paradox Mods by the launcher or via the Steam Workshop.

The folder that stores mods for the game is:

- Windows: `...\Documents\Paradox Interactive\Hearts of Iron IV\mod\`
- GNU/Linux: `~/.local/share/Paradox Interactive/Hearts of Iron IV/mod/`
- Mac: `~/Documents/Paradox Interactive/Hearts of Iron IV/mod/`

Manually downloaded mods should include a *.mod* text file along with a folder. If so, the files can simply be dropped into the mod folder. If one is downloading a newer version of a mod they already have installed, one should remove the older files first.

## Mod lists <a id="Mod_lists"></a>

- Paradox official mod list

<!-- kit:begin id="mods-mod-lists" at="section:Mod_lists" -->
**Kit addition** How a list of enabled mods reaches the game in 1.19.3.

- The launcher keeps the ordered list of enabled mods (a playset). At start the game reads the enabled mods from `dlc_load.json` in the user directory, which also carries the disabled DLCs. `hoi4.exe` contains the strings `dlc_load.json`, `enabled_mods`, `disabled_dlcs` and `mods_registry.json`. The format of `dlc_load.json` is described on [Modding](<Modding - Hearts of Iron 4 Wiki.md#Mod_structure>). [unverified] (file names found only as strings in `hoi4.exe`)
- A mod appears as "outdated" in the launcher when its `supported_version` does not fit the game. The launcher text says either "The mod does not have supported_version set." or "The mod supports version ...". The installed build is `1.19.3.0`, so a mod that targets it uses `supported_version = "1.19.*"` or `"1.19.3.0"`. [vanilla-confirmed 1.19.3] `pdx_launcher/common/localisation/l_english.yml`, `launcher-settings.json`.
- The Steam Workshop folder name is the game's Steam app id: `steam_appid.txt` is `394360`, matching `workshop/content/394360` on [Mod structure](<Mod structure - Hearts of Iron 4 Wiki.md#Steam_Workshop_Mods>). [vanilla-confirmed 1.19.3] `steam_appid.txt`.
<!-- kit:end id="mods-mod-lists" -->

## Mods with Wiki pages <a id="Mods_with_Wiki_pages"></a>

*Wiki pages for modifications are the responsibility of the modification team, not the Paradox wiki team*

- Ancient Formable Nations
- Equestria At War
- HOI4 ULTRA (Historical Industry Project)
- Kaiserreich
- The Road to 56
- Victoria 2 to Hearts of Iron IV converter
- Victoria 3 to Hearts of Iron IV converter
