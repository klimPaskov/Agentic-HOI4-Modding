# Mods

<!-- kit:begin id="review" build="1.19.4.1" checked="2026-11-01" revision="105602" sources="launcher-settings.json steam_appid.txt pdx_launcher/common/localisation/l_english.yml hoi4.exe" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Checked against: `launcher-settings.json`, `steam_appid.txt`, the launcher localisation in `pdx_launcher/` and strings in `hoi4.exe`. No statement on the page was found to be wrong for 1.19.3.
Kit blocks added: `mods-mod-lists` (fills the empty "Mod lists" section).
Gaps left: what the Paradox Mods site, the Steam Workshop and the "Paradox official mod list" currently offer cannot be checked from the game files. The Linux and Mac folder paths were not checked (Windows install only).
**1.19.4.1 re-check (2026-11-01).** 2 statements depended on files the update changed (`launcher-settings.json` and the strings in `hoi4.exe`) and both were re-measured. The installed build is now `1.19.4.1`, so the example `supported_version` value changed from `"1.19.3.0"`, and the four `hoi4.exe` file-name strings are still present. Every other statement cites files that are byte-identical in 1.19.4.1 (Steam depot manifest diff).
<!-- kit:end id="review" -->

<!-- kit:begin id="mods-mod-lists" at="section:mod-lists" -->
How a list of enabled mods reaches the game in 1.19.4.1.

- The launcher keeps the ordered list of enabled mods (a playset). At start the game reads the enabled mods from `dlc_load.json` in the user directory, which also carries the disabled DLCs. `hoi4.exe` contains the strings `dlc_load.json`, `enabled_mods`, `disabled_dlcs` and `mods_registry.json`. The format of `dlc_load.json` is described on [Modding](modding.md#mod-structure). [unverified] (file names found only as strings in `hoi4.exe`)
- A mod appears as "outdated" in the launcher when its `supported_version` does not fit the game. The launcher text says either "The mod does not have supported_version set." or "The mod supports version ...". The installed build is `1.19.4.1`, so a mod that targets it uses `supported_version = "1.19.*"` or `"1.19.4.1"`. [vanilla-confirmed 1.19.4.1] `pdx_launcher/common/localisation/l_english.yml`, `launcher-settings.json`.
- The Steam Workshop folder name is the game's Steam app id: `steam_appid.txt` is `394360`, matching `workshop/content/394360` on [Mod structure](mod_structure.md#steam-workshop-mods). [vanilla-confirmed 1.19.3] `steam_appid.txt`.
<!-- kit:end id="mods-mod-lists" -->
