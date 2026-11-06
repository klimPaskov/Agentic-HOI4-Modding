# Localisation

<!-- kit:begin id="review" build="1.19.4.1" checked="2026-11-01" revision="105503" sources="documentation/loc_objects_documentation.md documentation/loc_formatter_documentation.md documentation/script_concept_documentation.md documentation/effects_documentation.md documentation/triggers_documentation.md documentation/console_commands_documentation.md localisation/ interface/core.gfx interface/texticons.gfx common/scripted_localisation/ launcher-settings.json hoi4.exe" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Checked against: the localisation object, formatter and script-concept documentation, the 2,083 vanilla `.yml` files (encoding, file names, key lines, colour, format and icon use), `interface/core.gfx` and `interface/texticons.gfx`, all 42 files of `common/scripted_localisation/`, `launcher-settings.json` and strings in `hoi4.exe`.
Kit blocks added: vanilla file facts, colour codes with real use and the dynamic `§[Name]` colour, variable format letters (`U`, `H`, `^`, `*`), text icons, bindable tooltip rules, the missing `country_leader_desc` formatter, the object and promotion table with the three missing properties, the scripted localisation scope rule and `seed`, war names, division ranks and the `loc_check` commands.
Errors found in the wiki text: the language setting file name (`pdx_settings.txt` versus `pdx_settings.json`), `GetCallsign` listed for operatives (the documentation puts it on aces), pronoun functions listed for characters only, and the formatter list lacks `country_leader_desc`.
Gaps left: the stub markers "to be added" and "incomplete" are false positives (an `INDENT` description and the page's own caveat that its list of places where `[...]` works may be incomplete, which was not extended). `DATA`, `NAME`, `USRNAME` and `temp_display_B`, `_M`, `_T` are placeholder names in examples. The `0xC0000005` crash, the `replace` folder priority and the meaning of the `U` format letter cannot be shown from files and stay [unverified].
**1.19.4.1 re-check (2026-11-01).** 27 statements depended on files the update changed (the localisation folder, `interface/core.gfx`, `interface/texticons.gfx`, `hoi4.exe`, `launcher-settings.json`, `common/scripted_localisation/` and the console command documentation) and all 27 were re-measured. Numbers that moved: 2,093 `.yml` files (the 10 new ones are `keybinds_l_<language>.yml`), 1,336,123 key lines, 346 English lines with a trailing comment, the colour letter and format letter counts, 473 text icon sprite blocks, the `£` style counts and 1,546 `defined_text` entries in 41 files (the removed `debug_types` console command is not mentioned on this page). Every other statement cites files that are byte-identical in 1.19.4.1 (Steam depot manifest diff).
<!-- kit:end id="review" -->

<!-- kit:begin id="loc-vanilla-file-facts" at="section:quick-checklist" -->
What the 1.19.4.1 localisation folder looks like. All items: [vanilla-confirmed 1.19.4.1] `localisation/`, unless tagged otherwise.

- There are 2,093 `.yml` files and every one starts with the UTF-8 byte order mark. 2,092 sit in the ten language folders (`english`, `braz_por`, `french`, `german`, `japanese`, `korean`, `polish`, `russian`, `simp_chinese`, `spanish`), and 2,091 of those are named `<name>_l_<language>.yml` for their folder's language. The exception is `french/career_profile_zelosissimo.yml`, a leftover that holds only comments. The 2,093rd file is `localisation/languages.yml`, the table of language names.
- `languages.yml` has one block per language with the same ten entries as the page's list. `l_braz_por` is "Português do Brasil", Brazilian Portuguese.
- 2,083 files start with the matching `l_<language>:` header on line 1; the other 9 begin with a `# === [LocEditor:...]` comment. No file in a language folder holds two language headers, although the page says one is allowed; `languages.yml` holds ten.
- There are 1,336,123 key lines. 1,333,745 have no version number (`key: "text"`), 2,099 use `key:0` and 279 use `key:1` to `key:4`. New files can drop the number, as the page says.
- A key line can end with a `# comment` after the closing quote; 346 English lines do.
- No vanilla language folder has a `replace` subfolder (0 of 10 folders). [vanilla-confirmed 1.19.4.1] `localisation/`. `hoi4.exe` contains the strings `/replace/`, "Duplicate localization found", "The game has loc key collisions. Check logs/text.log" and "should be in in utf-8-bom encoding", which fit the page's `replace` and `text.log` text. [unverified] (strings in `hoi4.exe`)
- Duplicate keys. In a test, a key defined in two normal files of one mod was listed in `text.log` once per file ("Duplicate localization found, key: ..." with the file and the value), and the first file by name (`a` before `b`) won. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, text.log and game.log read. The winner comes from one pair of files only.
- The `replace` folder. In a test, a key defined again under `localisation/replace/english/`, `localisation/english/replace/` and `localisation/replace/` was overridden by the replace file in all three spellings, with no duplicate line in `text.log`. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, text.log and game.log read.
- A missing BOM. In a test, a `.yml` file without the BOM was reported in `error.log` as "Missing UTF8 BOM in" followed by the file's path under `localisation/english/`, and its key printed as the raw key name, so the key was not loaded. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, error.log and game.log read. That the key is not loaded is shown only by the raw key in the log.
- The page says the language is set in `pdx_settings.txt`. `launcher-settings.json` names `pdx_settings.json` as `ingameSettingsPath`, and `hoi4.exe` still contains the string `pdx_settings.txt`. [vanilla-confirmed 1.19.4.1] `launcher-settings.json` for the first part. The game reads the language from `pdx_settings.txt`: it holds `"System" = { "language" = { value="l_english" } }`, and no `pdx_settings.json` existed in the scratch user folder or in the maintainer's backed-up folder. With only `pdx_settings.txt` set to `l_german` and `settings.txt` left at `l_english`, the main menu came up in German (Einzelspieler, Mehrspieler, Optionen). On exit the game wrote `language="l_german"` into `settings.txt` as well. Editing `settings.txt` alone was not tested. The file was edited with the game closed, not through the Options screen, and the game was started without the Paradox launcher. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, main menu screenshot and the files compared before and after.
<!-- kit:end id="loc-vanilla-file-facts" -->

<!-- kit:begin id="loc-colour-codes" at="section:colouring-characters" -->
The colour table checked against the game.

- The global `textcolors` table in `interface/core.gfx` has exactly the 23 one-character keys of the table above: `C L W B G R b g Y H T O`, `0` to `9` and `t`. [vanilla-confirmed 1.19.4.1] `interface/core.gfx`.
- Fonts can change single letters. 30 `textcolors` blocks exist in three files (`core.gfx` 27, `core_bare_minimum.gfx` 1, `load_screen_font.gfx` 2): the global table plus per-font tables. The `vic_18_black` font redefines `G`, `R`, `Y`, `H` and `T`; there `Y` is black (`0 0 0`). [vanilla-confirmed 1.19.4.1] `interface/core.gfx`.
- Use in the 208 English files: `§!` 20,262 times, `Y` 12,297, `G` 2,893, `R` 2,298, `H` 1,860, `L` 391, `T` 213, `W` 185, `g` 89, `O` 10, `b` 4, `B` 2, and `0`, `7` and `8` seven times in total. `C`, `t` and the digits `1` to `6` and `9` are never used. `B` is pure blue (`0 0 255`) and nearly unused; vanilla highlights with `Y`, good and bad values with `G` and `R`, headings with `H`. [vanilla-confirmed 1.19.4.1] `localisation/english/*.yml`.
- A colour letter can come from scripted localisation: `§[GetColorX]text§!`. In `WUW_GER_scripted_loc.txt` the entries are `localization_key = R` and `localization_key = G`; no localisation key named `R` or `G` exists, so the game prints the key text itself, which is the colour letter. Vanilla uses this form 13 times in 5 English files, for example `§[GetColorForCurrentIntegratedPuppetEconomiesValue][?GER_puppet_economies_integrated]§!`. [vanilla-confirmed 1.19.4.1] `common/scripted_localisation/WUW_GER_scripted_loc.txt`, `localisation/english/WUW_decisions_l_english.yml`.
- Both error messages in the Errors section below exist in `hoi4.exe`: "Could not find coloring for character '%c'" and "Could not find coloring for character id '%u'". [unverified] (strings in `hoi4.exe`) The first one is logged for an unknown colour letter: `§Z` in an event text wrote "Could not find coloring for character 'Z'" to `error.log`, and the same line appeared again when a loc key holding it was printed with the `log` effect. The event window dropped the code and showed "A red B", and the log route kept the letter and removed the section signs ("A Zred! B"). [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, error.log and game.log read, event window checked in a screenshot. The two lines have identical text, so a second message was not seen, and which line belongs to which route rests on their time stamps. The "character id" form was not triggered.
<!-- kit:end id="loc-colour-codes" -->

<!-- kit:begin id="loc-variable-formats" at="section:formatting-variables" -->
Format letters as vanilla uses them. All items: [vanilla-confirmed 1.19.4.1] `localisation/english/*.yml`.

- The same letters work on `$KEY|fmt$` placeholders as on `[?var|fmt]`. English vanilla has 353 distinct `$KEY|fmt$` strings and 41 distinct `[?var|fmt]` strings. The commonest `$KEY|fmt$` forms are `|H` (2,896 uses), `|Y` (1,323), `|+=%1` (288) and `|UY` (191). The commonest `[?var|fmt]` forms are `|+0` (145), `|Y0` (82) and `|%` (50).
- Any colour letter from the colour table can be a format letter: `H`, `Y`, `R`, `G`, `g`, `W`, `L`, `T` and `O` all occur after the pipe. `H` leads in placeholders, `Y` in `[?var|...]`.
- A dot in the format string, as in `|.1`, occurs 309 times, `*` 115 times and `^` 69 times, and `%%` occurs as in `$LIMIT|R.0%%$`, so these forms from the table are all in real use.
- The letter `U`, not in the table above, occurs 352 times in format codes, mostly as `$COUNTRY|U$` or `$COUNTRY|UY$` at the start of a sentence. [vanilla-confirmed 1.19.4.1] `localisation/english/`. It presumably upper-cases the first letter. [unverified] (meaning inferred from the sentence position) In a test, a loc key holding `$igc_b_g148_o|U$` showed an empty string, not the upper-cased text, so the first-letter reading did not show. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, loc key logged with the `log` effect. The same reference without `|U` was not tested, so the empty text may come from the reference and not from the format.
<!-- kit:end id="loc-variable-formats" -->

<!-- kit:begin id="loc-text-icons" at="section:text-icons" -->
Text icons in 1.19.4.1. All items: [vanilla-confirmed 1.19.4.1] `interface/texticons.gfx`, `localisation/english/*.yml`.

- Vanilla defines its text icons in `interface/texticons.gfx`: 473 sprite blocks, most with textures in `gfx/texticons/` (428 written `spriteType`, 45 written `SpriteType`). 472 set `legacy_lazy_load = no` and 260 set `noOfFrames`, the frame count that `£name|N` indexes.
- Both ways to write the icon occur. English vanilla uses `£army_experience` style 1,580 times and `£GFX_army_experience` style 351 times, and `£name|N` with a frame 150 times. All counts are a `£` followed by letters, digits and underscores. Prefer the short form, as the page's own paragraph describes.
<!-- kit:end id="loc-text-icons" -->

<!-- kit:begin id="loc-nesting-dollar" at="section:nesting-strings" -->
The doubled dollar sign has no vanilla precedent.

- In vanilla, `$$` appears where two placeholders touch, as in `$TAG$$CONTROL|H$` or `$VAL_HIGH|G%$$VAL_MID|H%$` (130 English values). No English vanilla value uses `$$` as a literal dollar sign before a digit, bracket or space. [vanilla-confirmed 1.19.4.1] `localisation/english/*.yml`.
- The page's `$$100` and `$$[?temp_display_T|2]T` examples rest on the wiki alone. [unverified] `$$100` in a loc key printed `$100`, one literal dollar sign. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, loc key logged with the `log` effect. A string written directly in a `log` effect does not expand `$...$` at all (`$$100` stayed `$$100`). The `$$[?temp_display_T|2]T` form was not tested.
- Three examples on this page are real vanilla lines: `confirm_cancel_national_focus_desc` (`$FOCUS_NAME$`), `SCIENTIST_ROSTER_SORT_BUTTON_TOOLTIP` (`$REASON|Y$`) and `COUNTRY_autonomy_collaboration_government` (`$OVERLORDADJ$ $NONIDEOLOGY$`). [vanilla-confirmed 1.19.4.1] `localisation/english/*.yml`.
<!-- kit:end id="loc-nesting-dollar" -->

<!-- kit:begin id="loc-bindable-tooltips" at="section:bindable-localisation" -->
Bindable localisation, as the game documents it.

- A bindable value accepts a formatted localization (a localisation key, a string, or `formatter|token`) or a bound object `{ localization_key = KEY PARAM = <bindable> ... }`. A parameter value can itself be a bound object. [docs] `documentation/script_concept_documentation.md`.
- `custom_trigger_tooltip` is kept as an alias of the trigger `custom_override_tooltip`, and the documentation says to prefer the new name. The trigger takes `tooltip` for the positive text and `not_tooltip` for the text under `NOT`. With no positive tooltip given and a plain localisation key as root, the negative text is that key plus `_NOT`. Both fields are bindable. [docs] `documentation/triggers_documentation.md`.
- The effect `custom_override_tooltip = { tooltip = <bindable> <effects> }` replaces the tooltips of the effects inside it; `custom_effect_tooltip` takes a bindable directly. [docs] `documentation/effects_documentation.md`.
- The `tooltip` field of `any_country_of`, `all_country_of`, `any_other_country_of`, `any_state_of`, `all_claimant` and their siblings is also bindable. [docs] `documentation/triggers_documentation.md`.

```text
custom_override_tooltip = {
	tooltip = MY_TOOLTIP
	not_tooltip = MY_TOOLTIP_NOT   # optional: MY_TOOLTIP_NOT is implied
	<triggers>
}
```
<!-- kit:end id="loc-bindable-tooltips" -->

<!-- kit:begin id="loc-formatters-complete" at="section:localization-formatters-1" -->
The formatter list is one short.

The game documents eight formatters: `advisor_desc`, `building_state_modifier`, `character_name`, `country_culture`, `country_leader_desc`, `idea_desc`, `idea_name` and `tech_effect`. The list above lacks `country_leader_desc`. [docs] `documentation/loc_formatter_documentation.md`.

`country_leader_desc|<character token>` gets the description of a possible country leader, found in the database by ideology. It needs no scope object. `IDEOLOGY` is mandatory and is an ideology group token written `token:fascism`; `INDENT` is optional. [docs] `documentation/loc_formatter_documentation.md`.

```text
custom_effect_tooltip = {
	localization_key = country_leader_desc|hjalmar_schacht
	IDEOLOGY = token:fascism
}
```

Vanilla uses `idea_desc|` 263 times (249 in `common/`, 14 in `events/`), `building_state_modifier|` 27 times and `tech_effect|` 24 times; the other five formatters have no vanilla use. Vanilla passes `INDENT = "    "` as literal spaces; the documentation's `2_SPACES` is not a localisation key in vanilla. [vanilla-confirmed 1.19.4.1] `common/`, `events/`, `localisation/english/`.
<!-- kit:end id="loc-formatters-complete" -->

<!-- kit:begin id="loc-objects-promotions" at="section:documentation-of-localized-objects" -->
The documented localization objects, with the promotions the page does not describe. A promotion is the next object in a chain, as in `[ROOT.Capital.GetName]`. All rows: [docs] `documentation/loc_objects_documentation.md`.

| Object | Promotions | Properties missing from the tables above |
| --- | --- | --- |
| `Scope` (root of a scoped text) | `Player`, `This` and `THIS` (no effect), `Root`, `Prev`, `From`, `Country`, `State`, `Character`, `Operation`, `Unit`, `Ace`, `IndustrialOrganisation`, `PurchaseContract`, `SpecialProject`, `Combatant` | none |
| `LocalizationEnvironment` | `Faction`, `Building`, `Province`, `Terrain` | none |
| `Country` | `Capital`, `OriginalCapital`, `Overlord`, `FactionLeader` | none (59 properties) |
| `State` | `Owner`, `Controller`, `Occupied` | `GetContinent` |
| `Character` | `Owner` | none |
| `UnitLeader` | `Owner` | `GetLeaderSkill` |
| `Ace` | `Owner` | none |
| `Faction` | `Leader` | `GetName` |
| `SpecialProject` | `Owner` | `GetName` |
| `Operation` | `Target`, `Initiator`, `Operative0` to `Operative3` | `GetName` |
| `Province` | `Controller`, `Terrain` | `GetName` |
| `PurchaseContract` | `Buyer`, `Seller` | `GetDeliveredPayment` |
| `Building` | none | `GetName` |
| `Terrain` | none | `GetName` |
| `IndustrialOrg` | `Owner` | none |

- The list "Some of the localization objects are" above omits `Faction`, `LocalizationEnvironment` and `Scope`. [docs] `documentation/loc_objects_documentation.md`.
- The ten pronoun functions (`GetSheHe`, `GetSheHeCap`, `GetHerHim`, `GetHerHimCap`, `GetHerHis`, `GetHerHisCap`, `GetHersHis`, `GetHersHisCap`, `GetHerselfHimself`, `GetHerselfHimselfCap`) exist on `Country` (for the country's leader), `UnitLeader`, `Ace` and `Character`. The page lists them under characters only. Vanilla usually chains through the leader, as in `[FROM.GetLeader.GetHerHis]`. [docs] `documentation/loc_objects_documentation.md`, [vanilla-confirmed 1.19.4.1] `localisation/english/*.yml`.
- `GetCallsign` belongs to `Ace` and `GetCodeName` to `UnitLeader` (the operative leader). The "Other scopes" table above gives `GetCallsign` as an operative function. Vanilla uses `[From.GetCallsign]` and `[Prev.GetCallsign]` in ace texts. [docs] `documentation/loc_objects_documentation.md`, [vanilla-confirmed 1.19.4.1] `localisation/english/*.yml`.
- Promotions work inside ordinary bracket chains. Vanilla uses `[ROOT.Capital.GetName]` and `[ROOT.Capital.GetCapitalVictoryPointName]`, `[From.Owner.GetAdjective]` (14 uses) and `[FROM.Controller.GetNameDef]`. Vanilla GUI text roots a chain at an object: `[Character.GetName]` (35 uses), `[SpecialProject.GetName]` (22), `[State.GetName]` (10), `[Country.GetNameWithFlag]` (6), and the condition form `[(Character?.GetName:'KEY)]` twice. [vanilla-confirmed 1.19.4.1] `localisation/english/*.yml`.
- `GetDateString`, `GetDateStringShortMonth`, `GetDateStringNoHour`, `GetDateStringNoHourLong`, `GetTokenKey` and `GetTokenLocalizedKey` in the tables above are not in the objects documentation (0 matches). [docs] `documentation/loc_objects_documentation.md`. They are strings in `hoi4.exe`. Vanilla localisation uses two of them: `[?global.date.GetDateStringShortMonth]` and `[?BUL.BUL_date_of_tsars_death.GetDateStringNoHourLong]`. [unverified] (strings in `hoi4.exe`), [vanilla-confirmed 1.19.4.1] for the two uses. All four date getters work through `[?global.date.Get...]` at the 1936 start: `GetDateString` gave "12:00, 1 January, 1936", `GetDateStringNoHour` gave "1936.1.1", `GetDateStringNoHourLong` gave "1 January, 1936" and `GetDateStringShortMonth` gave "12:00, 1 Jan, 1936", with no dot after "Jan". [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, loc key and inline expression logged with the `log` effect.
<!-- kit:end id="loc-objects-promotions" -->

<!-- kit:begin id="loc-scripted-scope-and-seed" at="section:scripted-localisation" -->
Scripted localisation as vanilla writes it. All items: [vanilla-confirmed 1.19.4.1] `common/scripted_localisation/`.

- The header comment of `00_scripted_localisation.txt` says the `trigger` blocks must be valid for the scope the key is called in, giving Root or From.From as examples. Vanilla calls the entry as `[ROOT.GetImportOrDomesticFilmIndustry]` and also as a bare `[GetReichsWerkeName]`, so write the call with the scope your triggers expect.
- Vanilla has 1,546 `defined_text` entries in 41 of the 42 files (`WUW_BEL_scripted_loc.txt` holds only the comment template). Entries commented `# Country` expect a country scope.
- `random_list` takes `seed = <scoped variable>` before its weights. The vanilla comment: without a seed the roll is drawn from the country and gives the same result each time. `00_war_propaganda_scripted_loc.txt` uses `seed = num_of_controlled_factories` in its 12 `random_list` blocks.
- A quoted `localization_key` that is not a key is printed as written, with `[?var]` references resolved: `localization_key = "[?PRC_initialize_five_year_plan_current_civ_factories] / [?PRC_initialize_five_year_plan_goal_civ_factories]"`. No yml entry is needed. `SEA_PRC_scripted_loc.txt` has several.

```text
text = {
	trigger = { tag = AST }
	random_list = {
		seed = num_of_controlled_factories
		10 = { localization_key = men_of_timor }
		10 = { localization_key = soldiers_without_uniform }
	}
}
```
<!-- kit:end id="loc-scripted-scope-and-seed" -->

<!-- kit:begin id="loc-war-name-keys" at="section:war-naming" -->
The war name keys vanilla defines. All rows: [vanilla-confirmed 1.19.3] `localisation/english/war_l_english.yml`.

| Key | Vanilla value | Placeholders |
| --- | --- | --- |
| `WAR_NAME` | `$ORDER$$FIRST$-$SECOND$ War` | `$ORDER$`, `$FIRST$`, `$SECOND$` |
| `CIVIL_WAR_NAME` | `$ORDER$$SECOND$ Civil War` | `$ORDER$`, `$SECOND$` |
| `INDEPENDENCE_WAR_NAME` | `$ORDER$$FIRST$ War of Independence` | `$ORDER$`, `$FIRST$` |
| `WAR_TAKE_CORE_NAME` | `$ORDER$$FIRST$ reclamation of $STATE$` | `$ORDER$`, `$FIRST$`, `$STATE$` |
| `WAR_TAKE_CLAIM_NAME` | `$ORDER$$FIRST$ Aggression for $STATE$` | `$ORDER$`, `$FIRST$`, `$STATE$` |
| `WAR_NAME_ITA_ETH` | `Italian War on Ethiopia` | none; the only vanilla key of the form `WAR_NAME_TAG1_TAG2` |

The keys `ST`, `ND`, `RD` and `TH` next to them hold the ordinal suffixes. [vanilla-confirmed 1.19.4.1] `localisation/english/war_l_english.yml`. So `$ORDER$` is presumably the war's ordinal. [unverified] (inferred from the neighbouring keys)
<!-- kit:end id="loc-war-name-keys" -->

<!-- kit:begin id="loc-division-rank-overrides" at="section:division-commander-ranks" -->
Each key can be prefixed with a tag: `GER_DIVISION_EXPERIENCE_TITLE_ARMY_EXPERIENCE_0` overrides the generic key for Germany. Vanilla English defines the override for 25 tags (`CHI`, `ETH`, `FIN`, `FRA`, `GDC`, `GER`, `GSM`, `GXC`, `HBC`, `ITA`, `JAP`, `KHM`, `KUM`, `NOR`, `NXM`, `PRC`, `SHX`, `SIC`, `SIK`, `SND`, `SOV`, `USA`, `XIC`, `XSM`, `YUN`); `USA` defines only levels 0 and 1. The generic values are `Brigadier` for 0 and 1, `Major-General` for 2 and 3, and `Lt-General` for 4. [vanilla-confirmed 1.19.4.1] `localisation/english/unit_medals_l_english.yml`.
<!-- kit:end id="loc-division-rank-overrides" -->

<!-- kit:begin id="loc-checks" at="bottom" -->
## Checking localisation

Console commands that find missing localisation, and the file that silences them.

- `loc_check` checks for missing localization; `loc_check_characters`, `loc_check_decisions`, `loc_check_events`, `loc_check_focuses`, `loc_check_modifiers` and `loc_check_national_spirits` do the same for one kind of entry. [docs] `documentation/console_commands_documentation.md`.
- `update_loc <localization tag>` updates the localization tag file. `dump_equipment_loc` writes equipment names, or descriptions with `desc`, to `logs/equipment_loc.csv` by default, with `path=<filepath>` to change the file. [docs] `documentation/console_commands_documentation.md`.
- `localisation/ignored_loc_keys.txt` begins "Add loc keys to this file to have them ignored by the loc_check* console commands" and lists test keys such as `test.1.a`. [vanilla-confirmed 1.19.3] `localisation/ignored_loc_keys.txt`.
<!-- kit:end id="loc-checks" -->
