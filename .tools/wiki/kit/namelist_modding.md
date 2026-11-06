# Namelist modding

<!-- kit:begin id="review" build="1.19.4.1" checked="2026-11-01" revision="93543" sources="common/units/names_divisions/ common/units/names_ships/ common/units/names/ common/units/codenames_operatives/ common/names/ history/units/ documentation/effects_documentation.md" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Checked against: the 100 files with 1025 groups in `common/units/names_divisions/`, the 65 files with 620 groups in `common/units/names_ships/`, the 8 files of `common/units/names/`, the 14 operative codename lists in `common/units/codenames_operatives/`, `common/names/00_names.txt`, and the usage of `division_names_group` in `history/units/`.
Kit blocks added: vanilla key census and the file's own header rules for division names, corrections for the ship name example, the real layout of `common/units/names/`, the answer for `codename_list_id`, a block on `common/names/`.
Gaps left: how the game picks a group when several match, and what the "1500 line limit" on the page refers to, are not written in any game file.
**1.19.4.1 re-check (2026-11-01).** 6 tagged statements depended on files the update changed (`common/names/00_names.txt`, `history/units/`, the operatives localisation and `common/defines/00_defines.lua`), and all of them were re-measured. Nothing moved: 369 country blocks, 788 `division_names_group` lines, the `OPERATIVE_GENERIC_CODENAME_PATTERN` text and `HISTORICAL_ORDER_NAME_EXHAUSTION = false`. Every other statement cites files that are byte-identical in 1.19.4.1 (Steam depot manifest diff).
<!-- kit:end id="review" -->

<!-- kit:begin id="namelist-division-notes" at="section:divisions-names" -->
The vanilla file `common/units/names_divisions/NEP_names_divisions.txt` opens with a comment that defines the keys. In short: the group id is a made-up tag; `for_countries` lists the countries that can use it, and an empty list or a missing key means every country; `can_use` is a country-scope trigger; `division_types` is a hint for automatic choice (the template must have at least one of the listed types); `fallback_name` is used when the numbered names run out, and leaving it out falls back to the old naming; `ordered` numbers start at 1, must not repeat inside one group, and a later file that scripts the same number overrides it; the name must contain `%d` (decimal) or `%s` (Roman numerals); an optional second string is a description shown in the tooltip, and an optional third string is a URL that does not work yet. [vanilla-confirmed 1.19.3] `common/units/names_divisions/NEP_names_divisions.txt`

- Key census over the 1025 vanilla groups: `name`, `for_countries` and `division_types` in all, `can_use` in 1024, `fallback_name` on 1027 lines, `ordered` in 1019 and `link_numbering_with` in 385. [vanilla-confirmed 1.19.3] `common/units/names_divisions/`
- The header also documents `unordered` (names without a number). No vanilla group uses it, and no vanilla `ordered` line uses the second string. [vanilla-confirmed 1.19.3] `common/units/names_divisions/`
- `division_types` tokens in vanilla: `"infantry"` (272 groups), `"cavalry"`, `"motorized"`, `"mechanized"`, `"mountaineers"`, `"paratrooper"`, `"marine"`, `"ranger_battalion"`, `"militia"`, `"bicycle_battalion"`, and a list of armor types (`"light_armor"` `"medium_armor"` ...). [vanilla-confirmed 1.19.3] `common/units/names_divisions/`
- The group id is what a division template names: `division_names_group = GER_Inf_01` (788 uses in `history/units/`). It is also valid inside `division_template` effects and in AI templates. [vanilla-confirmed 1.19.4.1] `history/units/GER_1936.txt`. [docs] `documentation/effects_documentation.md`, `common/ai_templates/_documentation.md`
- `link_numbering_with = { GER_Inf_01 }` makes the group draw numbers from another group, so two groups never hand out the same number. The page calls it an alternative to the fallback name; the vanilla header describes it as a number reservation system tied to another group and does not call it a fallback. [vanilla-confirmed 1.19.3] `common/units/names_divisions/NEP_names_divisions.txt`, `common/units/names_divisions/GER_names_divisions.txt`
<!-- kit:end id="namelist-division-notes" -->

<!-- kit:begin id="namelist-line-limit" at="section:divisions-names" -->
The page says namelist files seem to be limited to about 1500 lines. Vanilla has larger files: `common/units/names_divisions/SOV_names_divisions.txt` has 1905 lines, `GER_names_divisions.txt` 1590, and `common/units/names_ships/GER_ship_name.txt` 3688. A limit of 1500 lines per file is not shown by the base game. [vanilla-confirmed 1.19.3] `common/units/names_divisions/`, `common/units/names_ships/`
<!-- kit:end id="namelist-line-limit" -->

<!-- kit:begin id="namelist-ship-notes" at="section:naval-names" -->
The example spells the fallback key `fallback_Name`. Vanilla writes `fallback_name` in lower case on all 1692 lines that use it (comments included) over divisions and ships; write it in lower case. No vanilla file writes `fallback_Name` (0 of 1692). [vanilla-confirmed 1.19.4.1] `common/units/names_divisions/` (1137 lines), `common/units/names_ships/` (555 lines). Whether the engine also accepts `fallback_Name` is untested. [unverified]

Key census over the 620 vanilla ship groups: `name`, `for_countries` and `type = ship` in all; `unique` in 574, `fallback_name` in 530, `ship_types` in 521, `prefix` in 498, `can_use` in 141, `ordered` in 46 and `link_numbering_with` in 8. So ship groups can use `can_use` and `ordered` as division groups do. `name` is a localisation key (`NAME_THEME_HISTORICAL_DESTROYERS`). [vanilla-confirmed 1.19.3] `common/units/names_ships/`

`ship_types` lists a hull token followed by the older type token. The pairs in vanilla are `{ ship_hull_light destroyer }` (76 groups), `{ ship_hull_carrier carrier }` (70), `{ ship_hull_cruiser light_cruiser }` (69), `{ ship_hull_submarine submarine }` (68), `{ ship_hull_cruiser heavy_cruiser }` (66), `{ ship_hull_heavy battleship }` (66) and `{ ship_hull_heavy battle_cruiser }` (65). A few groups list one token or three. [vanilla-confirmed 1.19.4.1] `common/units/names_ships/`, counts unchanged. Which of the two tokens belongs to Man the Guns technology is the wiki's claim and is untested. [unverified] `common/units/names_ships/ARG_ship_names.txt`

A group id such as `USA_CV_HISTORICAL` is what `create_equipment_variant` takes as `name_group`; it is optional and a variant inherits its parent's group when it is left out. [docs] `documentation/effects_documentation.md`

```text
ARG_DD_HISTORICAL = {
	name = NAME_THEME_HISTORICAL_DESTROYERS
	for_countries = { ARG }
	type = ship
	ship_types = { ship_hull_light destroyer }
	prefix = "ARA "
	fallback_name = "Destructor %d"
	unique = { "Catamarca" "Jujuy" "Cordoba" "La Plata" }
}
```

Vanilla group with the name list shortened. [vanilla-confirmed 1.19.3] `common/units/names_ships/ARG_ship_names.txt`
<!-- kit:end id="namelist-ship-notes" -->

<!-- kit:begin id="namelist-generic-layout" at="section:generic-names" -->
The real layout of `common/units/names/`. It holds 8 files: `00_names.txt` (the `generic` block and 55 country tags) and one file each for ENG, FRA, GER, ITA, JAP, SOV and USA. The vanilla header says names are based on equipment types, choosing the type with the largest amount in the pool, and `generic` is used for countries that are not scripted. [vanilla-confirmed 1.19.3] `common/units/names/00_names.txt`

- The second level is a unit or equipment type key. Ship keys: `submarine`, `destroyer`, `light_cruiser`, `heavy_cruiser`, `battle_cruiser`, `battleship`, `SH_battleship`, `carrier`. Land keys: `infantry`, `cavalry`, `light_armor`, `medium_armor`, `heavy_armor`, `motorized`, `mechanized`, `mountaineers`, `marine`, `paratrooper`, `militia`, `artillery_brigade`, `engineer` and others. Air keys end in `_airframe` or `_equipment` (`small_plane_airframe`, `jet_fighter_equipment`). There is also `codename` for operatives. [vanilla-confirmed 1.19.3] `common/units/names/00_names.txt`
- Each entry sets `prefix`, `generic` and `unique` (772 entries). 344 also set `generic_pattern`, a localisation key whose text uses `$NR$` and `$NAME$` (`UNIT_GENERIC_NAME_GENERIC_INFANTRY` is `"$NR$. $NAME$"`; `OPERATIVE_GENERIC_CODENAME_PATTERN` is `"Agent $NR$"`). [vanilla-confirmed 1.19.4.1] `common/units/names/00_names.txt`, `localisation/english/equipment_l_english.yml`, `localisation/english/operatives_l_english.yml`
- Country blocks also set `air_wing_names_template` (28 uses) and `fleet_names_template` (3), each a localisation key such as `AIR_WING_NAME_ENG_FALLBACK`. [vanilla-confirmed 1.19.3] `common/units/names/00_ENG_names.txt`
- In the `generic` block every `unique` list is empty, as the page says, except the `codename` entry (`unique = { "Agent 007" }`). [vanilla-confirmed 1.19.3] `common/units/names/00_names.txt`
<!-- kit:end id="namelist-generic-layout" -->

<!-- kit:begin id="namelist-codename-answer" at="section:operative-codenames" -->
`codename_list_id` in the example is only a placeholder for the id of the list; it is not a key. Real ids in vanilla are `SOV_OPERATIVE_CODENAME_HISTORICAL` and `GENERIC_ENG_OPERATIVE_CODENAME_HISTORICAL`. [vanilla-confirmed 1.19.3] `common/units/codenames_operatives/SOV_operative_codenames.txt`, `common/units/codenames_operatives/generic_opertive_codenames.txt`

Vanilla has 14 lists in 14 files (13 country files and `generic_opertive_codenames.txt`; two file names misspell "operative", which does not matter). Each list sets exactly `name`, `for_countries`, `type = codename`, `fallback_name` and `unique`. `name` is a localisation key in the generic file (`NAME_THEME_HISTORICAL_OPERATIVES`) and equals the id in the SOV file. The generic list serves several countries at once: `for_countries = { USA CAN NZL AST RAJ SAF }`. [vanilla-confirmed 1.19.3] `common/units/codenames_operatives/`

```text
SOV_OPERATIVE_CODENAME_HISTORICAL = {
	name = SOV_OPERATIVE_CODENAME_HISTORICAL
	for_countries = { SOV }
	type = codename
	fallback_name = "Agent %d"
	unique = { "Perseus" "Farewell" "Vano" }
}
```

Vanilla list with the name list shortened. [vanilla-confirmed 1.19.3] `common/units/codenames_operatives/SOV_operative_codenames.txt`
<!-- kit:end id="namelist-codename-answer" -->

<!-- kit:begin id="namelist-names-folder" at="bottom" -->
The page does not cover `common/names/`. Its only vanilla file, `common/names/00_names.txt`, holds 369 country blocks with the names of aces (pilots) and operation names. The header comments state: surnames can depend on gender; names and surnames are picked at random and a combination never repeats; a callsign is optional and, once used, is never given again; the operation name pools are drawn from until used up. [vanilla-confirmed 1.19.4.1] `common/names/00_names.txt`

| Key | Content |
| --- | --- |
| `male = { names = { ... } surnames = { ... } callsigns = { ... } }`, `female = { ... }` | gender specific lists (`male` in all 369 blocks, `female` in 368) |
| `surnames = { ... }`, `callsigns = { ... }` | lists that apply to both genders |
| `prefix = o_operation` | the operation name prefix, as a localisation key; the comment says to treat these as keys, not strings |
| `operation = { 0 = { o_default_operation } }` | pools of operation name keys per strategic region index; `0` is the generic national pool |
| `first = { ... }` / `second = { ... }` | words for a two part operation name (6 blocks); the header says a first and a second part are picked at random after the historical pool |
| `use_geographical_default_operation_names`, `offensive_operation_suffix`, `defensive_operation_suffix`, `naval_operation_suffix` | set once in `default` |

All rows: [vanilla-confirmed 1.19.4.1] `common/names/00_names.txt`.

Whether a historically named operation is used up once chosen is controlled by the define `HISTORICAL_ORDER_NAME_EXHAUSTION`, which is `false` in 1.19.4.1. [vanilla-confirmed 1.19.4.1] `common/defines/00_defines.lua`

The `default` block is the fallback and uses English names. A country block can list names without quotes when they have no spaces (`Adolf Alfred Anton`) and with quotes when they do (`"Abd al-Rahman"`). [vanilla-confirmed 1.19.4.1] `common/names/00_names.txt`
<!-- kit:end id="namelist-names-folder" -->
