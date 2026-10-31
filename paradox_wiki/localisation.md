# Localisation

*Offline snapshot of the Hearts of Iron IV Wiki page "Localisation", revision 105503, captured 2026-10-31. Wiki text by the wiki's contributors under CC BY-SA 3.0 (see LICENSE.txt); kit blocks are local additions under the same license.*

<!-- kit:begin id="review" at="top" build="1.19.3.0" checked="2026-10-31" revision="105503" sources="documentation/loc_objects_documentation.md documentation/loc_formatter_documentation.md documentation/script_concept_documentation.md documentation/effects_documentation.md documentation/triggers_documentation.md documentation/console_commands_documentation.md localisation/ interface/core.gfx interface/texticons.gfx common/scripted_localisation/ launcher-settings.json hoi4.exe" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Checked against: the localisation object, formatter and script-concept documentation, the 2,083 vanilla `.yml` files (encoding, file names, key lines, colour, format and icon use), `interface/core.gfx` and `interface/texticons.gfx`, all 42 files of `common/scripted_localisation/`, `launcher-settings.json` and strings in `hoi4.exe`.
Kit blocks added: vanilla file facts, colour codes with real use and the dynamic `§[Name]` colour, variable format letters (`U`, `H`, `^`, `*`), text icons, bindable tooltip rules, the missing `country_leader_desc` formatter, the object and promotion table with the three missing properties, the scripted localisation scope rule and `seed`, war names, division ranks and the `loc_check` commands.
Errors found in the wiki text: the language setting file name (`pdx_settings.txt` versus `pdx_settings.json`), `GetCallsign` listed for operatives (the documentation puts it on aces), pronoun functions listed for characters only, and the formatter list lacks `country_leader_desc`.
Gaps left: the stub markers "to be added" and "incomplete" are false positives (an `INDENT` description and the page's own caveat that its list of places where `[...]` works may be incomplete, which was not extended). `DATA`, `NAME`, `USRNAME` and `temp_display_B`, `_M`, `_T` are placeholder names in examples. The `0xC0000005` crash, the `replace` folder priority and the meaning of the `U` format letter cannot be shown from files and stay [unverified].
<!-- kit:end id="review" -->

## Table of contents

- [Quick checklist](#Quick_checklist)
- [Basics](#Basics)
- [Replacing](#Replacing)
- [Special characters](#Special_characters)
  - [Colouring characters](#Colouring_characters)
    - [Errors](#Errors)
  - [Formatting variables](#Formatting_variables)
  - [Country's flags](#Country.27s_flags)
  - [Text icons](#Text_icons)
- [Nesting strings](#Nesting_strings)
- [Bindable localisation](#Bindable_localisation)
  - [Usage of Bindable Localization](#Usage_of_Bindable_Localization)
  - [Context-Aware Tooltips](#Context-Aware_Tooltips)
  - [Localization Formatters](#Localization_Formatters)
- [Localization Formatters](#Localization_Formatters_2)
- [Contextual Localization](#Contextual_Localization)
  - [Using a localization object](#Using_a_localization_object)
  - [Condition in contextual localization](#Condition_in_contextual_localization)
  - [Relation to Event Scopes](#Relation_to_Event_Scopes)
  - [Documentation of localized objects](#Documentation_of_localized_objects)
- [Namespaces](#Namespaces)
  - [Functions](#Functions)
    - [Country scope](#Country_scope)
    - [Other scopes](#Other_scopes)
- [Scripted localisation](#Scripted_localisation)
  - [Dynamic scripted localisation](#Dynamic_scripted_localisation)
  - [Temporary variable display](#Temporary_variable_display)
- [Hard-to-find Localisation Info](#Hard-to-find_Localisation_Info)
  - [War Naming](#War_Naming)
  - [Division Commander Ranks](#Division_Commander_Ranks)
- [References](#References)
- [Kit: checking localisation](#kit-checking-localisation)

---

HOI4 uses the modified YAML **localisation** system used by modern Paradox games.

The localisation is stored within the `/Hearts of Iron IV/localisation/` folder, in which any sub-folder can be used. Each file is assigned a language with its filename by adding it in the end, with the following languages existing:

- `l_english`: English, as in `/Hearts of Iron IV/localisation/english/filename_l_english.yml`
- `l_french`: French, as in `/Hearts of Iron IV/localisation/french/mod_file_l_french.yml`
- `l_german`: German, as in `/Hearts of Iron IV/localisation/german/state_names_l_german.yml`
- `l_spanish`: Spanish, as in `/Hearts of Iron IV/localisation/spanish/mod_germany_l_spanish.yml`
- `l_braz_por`: Brazilian Portuguese, as in `/Hearts of Iron IV/localisation/braz_por/bahrain_l_braz_por.yml`
- `l_polish`: Polish, as in `/Hearts of Iron IV/localisation/polish/myfile_l_polish.yml`
- `l_russian`: Russian, as in `/Hearts of Iron IV/localisation/russian/siberia_l_russian.yml`
- `l_japanese`: Japanese, as in `/Hearts of Iron IV/localisation/japanese/kuril_l_japanese.yml`
- `l_simp_chinese`: Simplified Chinese, as in `/Hearts of Iron IV/localisation/simp_chinese/khalkha_l_simp_chinese.yml`
- `l_korean`: Korean, as in `/Hearts of Iron IV/localisation/korean/victory_points_l_korean.yml`

The filename **has to contain the language's internal name** as the file will not be loaded otherwise.
The currently-enabled language is chosen within the user directory's `/Hearts of Iron IV/pdx_settings.txt` file, however, more languages cannot be added directly other than these listed languages.

## Quick checklist <a id="Quick_checklist"></a>

In order for a file to work, it must have the following:

- The file has the .yml extension. By default, Windows hides file extensions, so this must be turned off to change the extension and to easily see it.
- The file's name, minus the extension, has to contain the internal name of the language, e.g. `filename_l_english.yml`. In this case, **`l` is a lowercase L.**
- **The file has to be encoded in UTF-8-BOM** - the UTF-8 encoding with the EFBBBF byte order mark at the beginning of the file. The game throws an error in the log if this is not met.
- The localisation values must be assigned to a database with the same name as the internal language. Most commonly, this means that *the first line of the file must be the language followed by a colon*, such as `l_english:`
  - If a language has never been assigned in the file and the file is encoded with UTF-8-BOM and contains a localization key, it might cause **a crash with error 0xC0000005(3221225477)**.
- Each of the localisation keys are structured in the format of `localisation_key:0 "Localisation value"`, in particular:
  - The localisation key may only have the English alphabet, underscores, dots, hyphens, and numbers. Anything else such as spaces, letters with diacritics, or non-Latin script will break the rest of the file.
  - The optional version number, 0 in this case, may only consist of numeric digits. Anything else such as hyphens or letters will break the rest of the file.
  - The localisation value must be surrounded by a U+022 quotation mark on both sides and must lie strictly on one line. Failing to meet this will break the rest of the file.

<!-- kit:begin id="loc-vanilla-file-facts" at="section:Quick_checklist" -->
**Kit addition** What the 1.19.3 localisation folder looks like. All items: [vanilla-confirmed 1.19.3] `localisation/`, unless tagged otherwise.

- There are 2,083 `.yml` files and every one starts with the UTF-8 byte order mark. 2,082 sit in the ten language folders (`english`, `braz_por`, `french`, `german`, `japanese`, `korean`, `polish`, `russian`, `simp_chinese`, `spanish`), and 2,081 of those are named `<name>_l_<language>.yml` for their folder's language. The exception is `french/career_profile_zelosissimo.yml`, a leftover that holds only comments. The 2,083rd file is `localisation/languages.yml`, the table of language names.
- `languages.yml` has one block per language with the same ten entries as the page's list. `l_braz_por` is "Português do Brasil", Brazilian Portuguese.
- 2,073 files start with the matching `l_<language>:` header on line 1; the other 9 begin with a `# === [LocEditor:...]` comment. No file in a language folder holds two language headers, although the page says one is allowed; `languages.yml` holds ten.
- There are 1,309,915 key lines. 1,307,569 have no version number (`key: "text"`), 2,067 use `key:0` and 279 use `key:1` to `key:4`. New files can drop the number, as the page says.
- A key line can end with a `# comment` after the closing quote; 319 English lines do.
- No vanilla language folder has a `replace` subfolder. `hoi4.exe` contains the strings `/replace/`, "Duplicate localization found", "The game has loc key collisions. Check logs/text.log" and "should be in in utf-8-bom encoding", which fit the page's `replace` and `text.log` text. [unverified] (strings in `hoi4.exe`)
- The page says the language is set in `pdx_settings.txt`. `launcher-settings.json` names `pdx_settings.json` as `ingameSettingsPath`, and `hoi4.exe` still contains the string `pdx_settings.txt`. Which file holds the language is [unverified]. [vanilla-confirmed 1.19.3] `launcher-settings.json` for the first part.
<!-- kit:end id="loc-vanilla-file-facts" -->

## Basics <a id="Basics"></a>

Localisation is created within any file in the localisation folder: the filename aside from the file extension is irrelevant aside from deciding which language is chosen.
**Every localisation file must use the UTF-8-BOM encoding**, i.e. the UTF-8 encoding with the byte order mark in the beginning of the file. Exact details depend on the text editor:

- Notepad++: Top bar's "Encoding" menu provides a selection of encodings. UTF-8-BOM is used in this case.
- Sublime Text: Top bar's "File" menu provides the "Save with Encoding" selection. UTF-8 with BOM is used in this case.
- Visual Studio Code: In the bottom bar, there's the "Select Encoding" button titled with the current encoding (Usually "UTF-8" or "UTF-8 with BOM"). To convert, this must be pressed and then "Save with encoding" must be selected with "UTF-8 with BOM".

Each localisation key must be assigned to a language database, marked with a line containing the language name ending with a colon, and nothing else. For example, `l_english:`. Until the next database entry or the end of file, this will assign every localisation key afterwards to the English language. A single file may contain entries for databases of multiple languages at the same time, however the filename must also contain each of these languages.

Next lines are structured in the format of `localisation_key:0 "Localisation value"`. In here:

- localisation_key is the localisation key that is being localised. This is usually the same as the name of the database entry (e.g. a focus with the name of TAG_focusname will have TAG_focusname as the needed localisation key). Other times, it's possible or required to set in the database entry itself (e.g. `title = my_event.1.t` within an event). Commonly, appending _desc as TAG_focusname_desc provides the localisation key for the description, such as with characters, focuses, ideas, traits, and so on.

**The localisation key cannot have special characters in it**, where a special character is defined as taking up more than 1 byte using the UTF-8 encoding. This includes every character other than those in the ASCII character system, so in essence localisation keys shouldn't have anything other than English letters, underscores, dots, and numbers. Localisation keys additionally cannot include spaces in them. Either one will show up within the error log as an error of the sort of `Expected colon(:) at line <...>`.

- 0 is the version number, used for Paradox's internal translation tracking.[1] This is never read in-game, and it can be omitted entirely with no difference in interpretation. Since this is introduced by Paradox and is invalid in standard YAML formatting, this may break the default syntax highlighting used for YAML in text editors. The version number can only contain numeric characters, anything else such as a hyphen is unexpected.
- Localisation value refers to the text that will show up in-game. **This must be on one line total**, multiple lines will break the file. Instead, newlines are marked using `\n` (Note that this is a backslash rather than a regular slash), such as `localisation_key: "First line.\nSecond line."` A space after the \n should be avoided, as it will appear in-game as offsetting the next lines. If you want to include quotation marks in text then `localisation_key: "Quote: \"This is a quote\""` should be used to avoid errors.

Any issue with localisation, such as special characters or spaces in localisation keys or a missing quote, will break the localisation file starting with the point where the syntax first stopped being followed correctly.

An example of a localisation file's contents is the following:

```yaml
l_english:
 infantry_equipment: "Infantry Equipment"
 infantry_equipment_short: "Inf. Eq."
 infantry_equipment_desc: "This is infantry equipment"
```

Nearly any printable character is allowed to use within the localisation value, other than certain special characters with special meaning, such as square brackets, or newlines. However, only some select characters are present in the fonts that are used in the game, and the selection of characters differs depending on the font. If the used font doesn't include a representation of a character, the game will replace it with a question mark (?). This affects only the font representation: this may be remedied by switching the used font within the [interface](<interface-modding.md>) or by [changing the font](<font-modding.md>) to include the letter.

## Replacing <a id="Replacing"></a>

Typically, localisation key overlap must be avoided, overlap being the same localisation key being defined several times in the same language's files. This is tracked within [user directory](<modding.md>)'s `/Hearts of Iron IV/logs/text.log` file, which contains a list of overlapping localisation keys if any. The value that'll get chosen does not seem to have a consistent pattern, but seems to prioritise base game files.

However, if the localisation file is contained within a folder with the name of "replace" (such as `/Hearts of Iron IV/localisation/english/replace`, still must be inside of localisation), it will get priority over the entries that are not. This can be helpful to overwrite only specific localisation keys without porting over the entire file, such as if the file gets frequently updated in base game.

For example, if desiring to change the name of the effect to add political power from the default  `POLITICS_ADD_POLITICAL_POWER:0 "Political Power: $VAL|=+0$."`, it may be undesirable to port over the entire `/Hearts of Iron IV/localisation/english/effects_l_english.yml` file to the mod, as new effects frequently get added to the game which would mean the file has to be kept in check.
However, instead creating a new localisation file within the `/Hearts of Iron IV/localisation/english/replace/` folder and defining the POLITICS_ADD_POLITICAL_POWER localisation key there will result in the value of the key getting changed without needing to copy the entire localisation file, meaning that the mod is now easier to port to future updates.

For example, `/Hearts of Iron IV/localisation/english/replace/mod_replace_l_english.yml` would contain the following content:

```yaml
l_english:
 POLITICS_ADD_POLITICAL_POWER: "New mana: $VAL|=+0$."
```

## Special characters <a id="Special_characters"></a>

### Colouring characters <a id="Colouring_characters"></a>

Various characters can be added to a string to alter its colour in-game. A colouring character formatting begins with a section sign (§) and includes a single letter (byte) afterwards used to identify the colour. The exclamation point is used to mark the end of a colouring rule. The end of a string doesn't necessarily mean that the colouring rule will end, meaning its use is mandatory with every colouring rule to avoid spillover into the next text, even if it should last until the end of the string. On Windows, the `Alt`+`21` alt code can be used to input a section sign.

The following formatting characters are implemented in the base game (The colour provided is the default generic colour and may be different depending on the font):

| Code | Effect | Exact colour |
| --- | --- | --- |
| §! | Ends the current formatting rule. | None. |
| §C | Colours the text cyan. | ( 35, 206, 255 ) |
| §L | Colours the text a dirty orange-gray (labeled "lilac"). | ( 195, 176, 145 ) |
| §W | Colours the text white. | ( 255, 255, 255 ) |
| §B | Colours the text blue. | ( 0, 0, 255 ) |
| §G | Colours the text green. | ( 0, 159, 3 ) |
| §R | Colours the text red. | ( 255, 50, 50 ) |
| §b | Colours the text black. | ( 0, 0, 0 ) |
| §g | Colours the text light gray. | ( 176, 176, 176 ) |
| §Y | Colours the text yellow. | ( 255, 189, 0 ) |
| §H | Colours the text yellow (same as §Y, labeled "header"). | ( 255, 189, 0 ) |
| §T | Colours the text white (same as §W, labeled "Title"). | ( 255, 255, 255 ) |
| §O | Colours the text orange. | ( 255, 112, 25 ) |
| §0 | Colours the text purple (labeled "Gradient Step 0"). | ( 203, 0, 203 ) |
| §1 | Colours the text lilac (labeled "Gradient Step 1"). | ( 128, 120, 211 ) |
| §2 | Colours the text blue (labeled "Gradient Step 2"). | ( 81, 112, 243 ) |
| §3 | Colours the text gray-blue (labeled "Gradient Step 3"). | ( 81, 143, 220 ) |
| §4 | Colours the text light blue (labeled "Gradient Step 4"). | ( 90, 190, 231 ) |
| §5 | Colours the text dull cyan (labeled "Gradient Step 5"). | ( 63, 181, 194 ) |
| §6 | Colours the text turquoise (labeled "Gradient Step 6"). | ( 119, 204, 186 ) |
| §7 | Colours the text light green (labeled "Gradient Step 7"). | ( 153, 209, 153 ) |
| §8 | Colours the text an orange-yellow (labeled "Gradient Step 8"). | ( 204, 163, 51 ) |
| §9 | Colours the text white-orange (labeled "Gradient Step 9"). | ( 252, 169, 125 ) |
| §t | Colours the text vivid red (labeled "Gradient Step 10"). | ( 255, 76, 77 ) |

Here is an example of the colour formatting:

```yaml
l_english:
 example_key: "This is my text, §Bthis text is blue§!, and §Rthis text is red§!"
```

New text colours can be added by expanding the `textcolors = { ... }` array in `/Hearts of Iron IV/interface/core.gfx`. Colour keys *cannot* have more than one letter (i.e. "BU = {0 255 0}"), and will attempt to overwrite another colour key with the same first letter. It is also possible to make a colouring character represent a different colour from default when a certain font is used within the [bitmapfont definition](<font-modding.md#Defining_bitmaps>) of that font.

<!-- kit:begin id="loc-colour-codes" at="section:Colouring_characters" -->
**Kit addition** The colour table checked against the game.

- The global `textcolors` table in `interface/core.gfx` has exactly the 23 one-character keys of the table above: `C L W B G R b g Y H T O`, `0` to `9` and `t`. [vanilla-confirmed 1.19.3] `interface/core.gfx`.
- Fonts can change single letters. 30 `textcolors` blocks exist in three files (`core.gfx` 27, `core_bare_minimum.gfx` 1, `load_screen_font.gfx` 2): the global table plus per-font tables. The `vic_18_black` font redefines `G`, `R`, `Y`, `H` and `T`; there `Y` is black (`0 0 0`). [vanilla-confirmed 1.19.3] `interface/core.gfx`.
- Use in the 207 English files: `§!` 19,949 times, `Y` 12,131, `G` 2,819, `R` 2,249, `H` 1,837, `L` 391, `T` 213, `W` 184, `g` 88, `O` 11, `b` 4, `B` 2, and `0`, `7` and `8` seven times in total. `C`, `t` and the digits `1` to `6` and `9` are never used. `B` is pure blue (`0 0 255`) and nearly unused; vanilla highlights with `Y`, good and bad values with `G` and `R`, headings with `H`. [vanilla-confirmed 1.19.3] `localisation/english/*.yml`.
- A colour letter can come from scripted localisation: `§[GetColorX]text§!`. In `WUW_GER_scripted_loc.txt` the entries are `localization_key = R` and `localization_key = G`; no localisation key named `R` or `G` exists, so the game prints the key text itself, which is the colour letter. Vanilla uses this form 13 times in 5 English files, for example `§[GetColorForCurrentIntegratedPuppetEconomiesValue][?GER_puppet_economies_integrated]§!`. [vanilla-confirmed 1.19.3] `common/scripted_localisation/WUW_GER_scripted_loc.txt`, `localisation/english/WUW_decisions_l_english.yml`.
- Both error messages in the Errors section below exist in `hoi4.exe`: "Could not find coloring for character '%c'" and "Could not find coloring for character id '%u'". [unverified] (strings in `hoi4.exe`)
<!-- kit:end id="loc-colour-codes" -->

#### Errors <a id="Errors"></a>

The errors related to the colouring characters can be fairly unintuitive to find, considering that they do not provide the location of the file.
There are three types of the error:

- `Could not find coloring for character 'M'` – This exact example means that, somewhere, the game found `§M` within localisation; however, since "M" isn't a valid colour, this is an unexpected result. The exact character is provided, so finding the cause should be elementary. A space is also considered a character, so `Could not find coloring for character ' '` means that somewhere in localisation `§`  is present, with a symbol specifying the beginning or end of a colouring rule omitted.
- `Could not find coloring for character id '17'` – Note that it specifies the character ID. In this case, the printable Unicode character ID is provided. This is typically done where providing the actual character would be confusing (e.g. for the number "1", the game would specify the character id "17" if such a colour doesn't exist. Since "1" is the 18th printed character, it has the id of 17, as the numeration typically starts from 0.)

This has a notable exception: the character id '0' may refer to the NULL character rather than a space. In other words, the character id '0' means there is *absolutely nothing* after the § symbol, i.e. the string ends with §. As such, locating this error would be done by searching for `§"` This is usually caused by omitting the exclamation mark from the character to end the colour formatting, which would properly be `§!`.

- If trying to use a character that takes several bytes to write in the UTF-8 encoding, the game will only try to read the last byte of the character rather than the entirety of it. This may result in either of the previous errors, but it makes finding the cause much harder. For example, trying to use `§Ā Some text §!`, where Ā has the code of U+0100, will result in the game throwing an error of `Could not find coloring for character id '0'`, and trying to use `§ō Some text §!`, where ō has the code of U+014D, will result in the game throwing an error of `Could not find coloring for character 'M'` (as the character 'M' has the code of U+004D).

Searching can be done using a text editor with the "Find in Files" functionality. **Windows Explorer cannot be used**, as it does not search inside of YAML files. For example, this is how the functionality is accessed in the more common editors to use:

- **Notepad++** – This is located in the "Search" topbar menu as "Find in Files...". By default, no folder is provided. "Follow current doc." allows the text editor to automatically input the currently-opened document's folder as the place for the search, or it can be entered manually. Alternatively, this menu can be opened from the right-click menu of a folder within the "Folder as Workspace" menu – accessed by a button in the topbar – which'll automatically set the folder location to be that folder.
- **Sublime Text** – This is located in the "Find" topbar menu as "Find in Files...". In order to add a folder to search, the menu to the right of the "Where:" line can be opened, with either "Add Folder" (to select an individual folder) or "Add Open Folders" (To automatically select all folders opened via Sublime Text) buttons serving to do so.
- **Visual Studio Code** – Visual Studio Code by default searches only the currently opened folder. A folder is opened either through the "Open Folder..." button in the "File" topbar menu or the "Explorer" menu, accessed through the bar on the left. After this, the functionality can be accessed in the "Edit" menu as "Find in Files". To search in other folders, open the 'search details' menu, represented with an ellipsis, and enter the full path to the folder in the 'Files to include' area. In order to speed up the search, filename filters can be used. For example, `localisation/english/*.yml` within "files to include" will only search every \*.yml file within the `<currently opened folder>/localisation/english/` folder, where `*` stands for any amount (including 0) of any characters within the filename. Similar filters can be used in the previous two text editors, however without allowing folders to be filtered — only the filenames.

### Formatting variables <a id="Formatting_variables"></a>

*See also: [Variables](<data-structures.md>)*

Variables have a unique way for applying colouring, also allowing extra formatting characters. These are applied after a pipe placed at the end of the variable's name, such as `[?my_variable|R]` that will turn the colour of the variable `my_variable` red. If no colouring is applied, it will use the same colour as regular text: the §-colour block, textbox's `text_color_mode`, or the font's default colour in that order.

The list of formatting characters that are restricted to variables only are the following:

| Code | Effect |
| --- | --- |
| \* | Converts the variable to SI units—appends "K" or "M" and divides the variable appropriately, such as 65 536 becoming 65.53K and 1 500 000 becoming 1.50M. Displays 2 decimals after the dot by default. |
| ^ | Same as \*. |
| = | Prefixes the variable with **+** if the value is positive or **-** if it is negative. |
| 0..9 | Controls the number of decimals to display. Due to the nature of the game's variables, there are no more than 5 decimals that can be shown. Using any digit greater than 5 will instead have the same result as 5. |
| % | Converts the variable to percentage, multiplying by 100 and appending a %. By default, will show 2 digits after the decimal point, though the second digit will always be 0. |
| %% | Appends a percentage to the end of the variable without multiplying by 100. |
| + | Colours the variable green if positive, yellow if zero, red if negative. |
| - | Colours the variable red if positive, yellow if zero, green if negative. |

Any unrecognised symbols will neither change how the variable is localised nor get recognised as an error in-game. For example, it's common practice in the base game to prepend a dot before the digit used to control the amount of displayed digits as `[?var|.1]`. In case of overlap between mutually-exclusive rules, the last-used one will be prioritised. However, static colouring has a lower priority than dynamic colouring (e.g. `[?var|+Y]` will be treated as `[?var|+]`), and using `%%` will also override `%`.

Some examples of formatting characters in usage:

```yaml
l_english:
 loc_key: "Democratic party popularity: [?party_popularity@democracy|%G0]"
 loc_key_2: "Modifier token's value: [?modifier@my_modifier|.1%%+]"
 pol_power_trigger_tt: "Has more than [?var_name|Y] political power"
```

Within these examples, the first string depicts the current scope's democratic popularity as a percentage multiplied by 100 (%), in green (G), rounded to a whole number with 0 decimals (0). The second string displays the `my_modifier` [modifier token](<modifiers.md>)'s value as a 'good' number (+ making it green if positive, red if negative), with a percentage sign appended in the end (%%) and rounded to a number with one decimal (.1). The third string displays the variable in yellow colouring (as is common in the base game's tooltips), leaving it unchanged otherwise.

<!-- kit:begin id="loc-variable-formats" at="section:Formatting_variables" -->
**Kit addition** Format letters as vanilla uses them. All items: [vanilla-confirmed 1.19.3] `localisation/english/*.yml`.

- The same letters work on `$KEY|fmt$` placeholders as on `[?var|fmt]`. English vanilla has 352 distinct `$KEY|fmt$` strings and 40 distinct `[?var|fmt]` strings. The commonest `$KEY|fmt$` forms are `|H` (2,880 uses), `|Y` (1,313), `|+=%1` (288) and `|UY` (191). The commonest `[?var|fmt]` forms are `|+0` (145), `|Y0` (82) and `|%` (60).
- Any colour letter from the colour table can be a format letter: `H`, `Y`, `R`, `G`, `g`, `W`, `L`, `T` and `O` all occur after the pipe. `H` leads in placeholders, `Y` in `[?var|...]`.
- A dot in the format string, as in `|.1`, occurs 308 times, `*` 115 times and `^` 67 times, and `%%` occurs as in `$LIMIT|R.0%%$`, so these forms from the table are all in real use.
- The letter `U`, not in the table above, occurs 352 times, mostly as `$COUNTRY|U$` or `$COUNTRY|UY$` at the start of a sentence. It presumably upper-cases the first letter. [unverified] (meaning inferred from the sentence position)
<!-- kit:end id="loc-variable-formats" -->

### Country's flags <a id="Country.27s_flags"></a><a id="Country's_flags"></a>

The following in localisation will display the default, `/Hearts of Iron IV/gfx/flags/TAG.tga`, flag of a country: `@TAG`
It's recommended to use the GetFlag namespace when possible instead, however, this can be used on localisation that doesn't support namespaces, such as custom modifier tooltips or the game rules.

### Text icons <a id="Text_icons"></a>

Icons can be displayed within strings using the **£** notation.

```yaml
l_english:
 example_key: "£GFX_army_experience"
```

Text icons are added as `spriteType = { ... }` definitions in `/Hearts of Iron IV/interface/*.gfx` files within an overarching `spriteTypes = { ... }`. An example definition of one looks like:

```text
	spriteType = {
		name = "GFX_my_text_icon"
		texturefile = "gfx/texticons/filename.dds"
		legacy_lazy_load = no
	}
```

The text icon's name is equal to the text icon with the GFX_ part in the beginning removed, being `£my_text_icon` in this case.

If the sprite of the text icon is made out of multiple frames, then the specified frame can be used in localisation as `£icon_name|1`, this example being the first frame. Note that `legacy_lazy_load = no` is necessary for multi-framed text icons to work properly. It is also required to make the icon appear on game start without reloading/modifying interface files, so you should include it.

<!-- kit:begin id="loc-text-icons" at="section:Text_icons" -->
**Kit addition** Text icons in 1.19.3. All items: [vanilla-confirmed 1.19.3] `interface/texticons.gfx`, `localisation/english/*.yml`.

- Vanilla defines its text icons in `interface/texticons.gfx`: 472 sprite blocks with textures in `gfx/texticons/` (427 written `spriteType`, 45 written `SpriteType`). 471 set `legacy_lazy_load = no` and 259 set `noOfFrames`, the frame count that `£name|N` indexes.
- Both ways to write the icon occur. English vanilla uses `£army_experience` style 1,760 times and `£GFX_army_experience` style 284 times, and `£name|N` with a frame 150 times. Prefer the short form, as the page's own paragraph describes.
<!-- kit:end id="loc-text-icons" -->

## Nesting strings <a id="Nesting_strings"></a>

The dollar sign special symbol is used for nesting other strings within any given localisation key's value. In particular, there are 4 primary usage cases for it:

- Nesting other localisation keys. For example,  `some_modifier_tooltip:0 "$modifier_production_speed_infrastructure_factor$: §R-10%§!"` will show up in-game as `Infrastructure construction speed: -10%`, assuming that `modifier_production_speed_infrastructure_factor`'s definition is unchanged from the base game.

This is useful with localisation key values that need to be re-used within others, but can be easily changed during the development of the mod, as to not need to adjust every single localisation value that uses it when changing it. This can also be used to expand compatibility with base game updates or other mods that may potentially change the localisation value but should still be compatible with the mod.
When used within `pdx_tooltip` of an interface element, this does not work properly, instead showing up with the dollar signs visible. This can be bypassed using [scripted localisation](#Scripted_localisation), as a scripted localisation entry that points towards a key, the value of which contains nested localisation entry, will work as intended.

- Inputting a dollar sign itself. This is done by doubling the dollar sign in localisation, such as  `cost_tooltip: "This option costs $$100"`.
- Nesting a boundable variable. Introduced in patch 1.15, boundable variables allow modders to define custom variables for use in localisation keys, functioning similarly to internal variables. These can be assigned within any effect, trigger block, or on a scripted GUI. For example, by using a loacalisation key like: `my_boundable_tooltip: "My name is $NAME$."`, `$NAME$` in this case would be a custom boundable variable that can be defined elsewhere by the modder. This provides significant flexibility for dynamic localisation that adapts to gameplay conditions. For further details on defining and binding these variables, refer to the boundable localisation section.

- Nesting a strictly internal variable. This is particularly common within base game's localisation that corresponds to game mechanics rather than database entries, such as  `confirm_cancel_national_focus_desc:0 "Are you sure you want to cancel the national focus §H$FOCUS_NAME$§!?"`. In these cases, the specified internal variable only exists within the scope of that localisation key and cannot be used anywhere else.

One notable usage of strictly internal variables is in country names, as these offer a variety of internal variables fetching the non-ideology name of the country and the overlord's name in either regular, ADJ, or DEF form, such as `COUNTRY_autonomy_collaboration_government:0 "$OVERLORDADJ$ $NONIDEOLOGY$"`.

<!-- kit:begin id="loc-nesting-dollar" at="section:Nesting_strings" -->
**Kit note** The doubled dollar sign has no vanilla precedent.

- In vanilla, `$$` appears where two placeholders touch, as in `$TAG$$CONTROL|H$` or `$VAL_HIGH|G%$$VAL_MID|H%$` (130 English values). No English vanilla value uses `$$` as a literal dollar sign before a digit, bracket or space. [vanilla-confirmed 1.19.3] `localisation/english/*.yml`.
- The page's `$$100` and `$$[?temp_display_T|2]T` examples rest on the wiki alone. If a literal dollar must appear, test the exact string in game with `reload loc` first. [unverified]
- Three examples on this page are real vanilla lines: `confirm_cancel_national_focus_desc` (`$FOCUS_NAME$`), `SCIENTIST_ROSTER_SORT_BUTTON_TOOLTIP` (`$REASON|Y$`) and `COUNTRY_autonomy_collaboration_government` (`$OVERLORDADJ$ $NONIDEOLOGY$`). [vanilla-confirmed 1.19.3] `localisation/english/*.yml`.
<!-- kit:end id="loc-nesting-dollar" -->

## Bindable localisation <a id="Bindable_localisation"></a>

**Bindable Localization** was introduced in **patch 1.15**, allowing variables to be dynamically bound to localization keys through scripting.

Previously, variables in localization keys (e.g., `$OVERLOADJ$`) were strictly internal and provided directly by the game, limiting modders' flexibility. For example:

```text
SCIENTIST_ROSTER_SORT_BUTTON_TOOLTIP: "§YClick§! to sort according to $REASON|Y$"
```

Before patch 1.15, `$REASON$` would be internal and unmodifiable. With the introduction of bindable localization, modders can now define their own bound variables, reducing the need for hundreds of similar localization keys that only differ in minor ways. Bindable localisation can only be used within very specific contexts, most of which are documented. However, there are 3 very useful places they can be used on, namely:

- `custom_effect_tooltip`,
- `custom_trigger_tooltip`,
- and to GUI files using the `bound_tooltip` construct.

<!-- kit:begin id="loc-bindable-tooltips" at="section:Bindable_localisation" -->
**Kit addition** Bindable localisation, as the game documents it.

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

### Usage of Bindable Localization <a id="Usage_of_Bindable_Localization"></a>

Consider the following localization key:

```text
my_bindable_tooltip: "Hello $NAME|Y$. I am $USRNAME$. Good $TIME$"
```

Bindable localization allows you to dynamically define the variables (`$NAME$`, `$USRNAME$`, and `$TIME$`) using script. For example:

```text
custom_effect_tooltip = {
    localization_key = my_bindable_tooltip
    NAME = "John"
    USRNAME = "George"
    TIME = "Morning"
}
```

This would result in the tooltip:
`Hello John. I am George. Good Morning.`

If you want to use it within a `custom_trigger_tooltip`, then you can use a similar concept. For example:

```text
custom_trigger_tooltip = {
    tooltip = {
        localization_key = my_bindable_tooltip
        NAME = "Dave"
        USRNAME = "Steve"
        TIME = "Evening"
    }
    <triggers>
}
```

This would result in the tooltip: `Hello Dave. I am Steve. Good Evening.`

Bound localization also supports recursion, allowing you to nest localization keys dynamically. For example:

```text
custom_effect_tooltip = {
    localization_key = my_bindable_tooltip
    NAME = "John"
    USRNAME = "George"
    TIME = {
        localization_key = COLOR_YELLOW
        DATA = "Morning"
    }
}
```

Here, `$TIME$` refers to another localization key, `COLOR_YELLOW`, defined as:

```text
COLOR_YELLOW: "§Y$DATA$§!"
```

The resulting tooltip would render `$TIME$` as "§YMorning§!" (with the text in yellow).

Instead of using inline strings, bindable localization can reference other localization keys directly, like [scripted localisation](#Scripted_localisation). For example:

```text
custom_effect_tooltip = {
    localization_key = my_bindable_tooltip
    IDEA_NAME = GER_mefo_bills
}
```

In this case, `GER_mefo_bills` is a predefined localization key, and its value will replace `$IDEA_NAME$`.

### Context-Aware Tooltips <a id="Context-Aware_Tooltips"></a>

**Context-aware tooltips** extend bound localization by allowing tooltips to be localized based on a context provided by the game. They are used strictly on GUI files, like `bound_tooltip`.

They are used with the `context_aware_tooltip` construct. The context is provided directly by the game’s source code and can only be used in specific, documented places.

Additionally, the context is recursive: if a parent object is localized with a context, all child objects will inherit the same context.

### Localization Formatters <a id="Localization_Formatters"></a>

Localization formatters provide a syntax for retrieving localized text properties of static tokens. The general format is:

```text
<formatter>|<token>
```

Localization formatters can also accept parameters that modify their output, as shown with `INDENT` in the example below:

```text
custom_effect_tooltip = {
    localization_key = building_state_modifier|dam
    INDENT = "    "
}
```

This syntax is in the German focus tree, it is used to retrieve the localized name of a state modifier for the `dam` building.

Here:

- `building_state_modifier|dam` retrieves the localized text property for the token `dam`.
- `INDENT` adjusts the indentation of the tooltip text.

## Localization Formatters <a id="Localization_Formatters_2"></a>

**character_name**

The character_name formatter gets the name of the character.
Example:

```text
custom_effect_tooltip = character_name|hjalmar_schacht
```

**country_culture**

The country_culture formatter formats the string using the country's cultural override (TAG_token) if it exists, otherwise the generic version (token).
Localization Scope Object
The formatter requires the following Localization Scope Objets to be defined:

Country - The country that the idea is associated with.
Example

```text
custom_effect_tooltip = country_culture|generic_tank_organisation
```

**idea_name**

The idea_name formatter formats gets the name for the idea.
Localization Scope Object
The formatter requires the following Localization Scope Objects to be defined:

Country - The country that the idea is associated with.
Example

```text
custom_effect_tooltip = idea_name|canadian_pacific_railway
```

**advisor_desc**

The advisor_desc formatter gets the description for the advisor.
Localization Scope Object
The formatter requires the following Localization Scope Objets to be defined:

Country - The country that the idea is associated with.
Example

```text
custom_effect_tooltip = advisor_desc|hjalmar_schacht
```

**tech_effect**

The tech_effect formatter gets the effect of finishing a technology.
Localization Scope Object
The formatter requires the following Localization Scope Objects to be defined:

Country - The country that the tech is associated with.
Example

```text
custom_effect_tooltip = tech_effect|early_transport_plane
```

**idea_desc**

The idea_desc formatter gets the description for the idea.
Localization Scope Object
The formatter requires the following Localization Scope Objects to be defined:

Country - The country that the idea is associated with.
Example

```text
custom_effect_tooltip = idea_desc|canadian_pacific_railway
```

**building_state_modifier**

The building_state_modifier gets the state modifiers for the provided building template and the provided scope.

The formatter takes special care of the following parameters:

INDENT: The indent to be added to all lines of the state modifier description (including header line).
Example:

```text
custom_effect_tooltip = building_state_modifier|dam
```

<!-- kit:begin id="loc-formatters-complete" at="section:Localization_Formatters_2" -->
**Kit addition** The formatter list is one short.

The game documents eight formatters: `advisor_desc`, `building_state_modifier`, `character_name`, `country_culture`, `country_leader_desc`, `idea_desc`, `idea_name` and `tech_effect`. The list above lacks `country_leader_desc`. [docs] `documentation/loc_formatter_documentation.md`.

`country_leader_desc|<character token>` gets the description of a possible country leader, found in the database by ideology. It needs no scope object. `IDEOLOGY` is mandatory and is an ideology group token written `token:fascism`; `INDENT` is optional. [docs] `documentation/loc_formatter_documentation.md`.

```text
custom_effect_tooltip = {
	localization_key = country_leader_desc|hjalmar_schacht
	IDEOLOGY = token:fascism
}
```

Vanilla uses `idea_desc|` 263 times (249 in `common/`, 14 in `events/`), `building_state_modifier|` 27 times and `tech_effect|` 24 times; the other five formatters have no vanilla use. Vanilla passes `INDENT = "    "` as literal spaces; the documentation's `2_SPACES` is not a localisation key in vanilla. [vanilla-confirmed 1.19.3] `common/`, `events/`, `localisation/english/`.
<!-- kit:end id="loc-formatters-complete" -->

## Contextual Localization <a id="Contextual_Localization"></a>

Contextual localization is a way to access data from Localization Objects when localizing a string.
The concept differs slightly from standard values ($VAL$) that can be injected into the localization string by allowing the localization string
to select which properties to add to the resulting string and where.
When a string is contextually localized with a localization object, then there's one root object (either a `[Scope]`(loc_objects_documentation.md#scope) or \[Localization Environment(loc_objects_documentation.md#localization_environment)\].
In general this object can only be used for two purposes: Accessing other objects and getting the current date.

Some of the localization objects are :

- Ace
- Building
- Character
- Country
- IndustrialOrg
- Operation
- Province
- PurchaseContract
- SpecialProject
- State
- Terrain
- UnitLeader

### Using a localization object <a id="Using_a_localization_object"></a>

The localization objects are used with the following syntax: `[(Object.)+Property]`.
`(Object.)+` refers to a sequence of at least one object accessor and `Property` is the property
that is accessed by the last object in the sequence. For example, if the localization string is localized with an `[Character]`(loc_objects_documentation.md#character) object
the following queries would get the character's name and the name of the country that the character belongs to `[Character.GetName]`
and `[Character.Owner.GetName]`, respectively.

### Condition in contextual localization <a id="Condition_in_contextual_localization"></a>

Conditions in contextual localization can be used to check if objects are null or not. The basic syntax for the condition is `[(OBJECT ? TRUE_CASE : FALSE_CASE)]`.
Where:

- `OBJECT` is any object you can use to access a property from (for example, `Character` and `Character.Owner` are valid objects).
- `TRUE_CASE` and `FALSE_CASE` are what is to be localized if `OBJECT` is not null and null, respectively. These can hold one of the following values:

1. `'LOC_KEY` - A localization key (`LOC_KEY`, note the prepending `'` that means that it's a localization key) that will be localized using the same context as the root contextual localization.
2. `(OBJECT.)+Property` - Standard access of a property from an object (discards the object before the `?`). `(OBJECT.)+` stands for a sequence of at least one object, with dots as separators.
3. (true case only) `.(OBJECT.)*Property` - Continue that object sequence from the object before the `?`. `(OBJECT.)*` stands for a potentially empty sequence of objects with dots as separators. This is more efficient than the second option since it will not redo the object getters before the `?`.

As an example loc. If there is character to scope into it gets the character name and if that fails it shows the loc key:

```text
 PROGRAM_SCIENTIST_NAME: "[(Character?.GetName:'PROGRAM_NO_SCIENTIST_ASSIGNED)]"
 PROGRAM_NO_SCIENTIST_ASSIGNED: "Assign a Scientist to start a project"
```

### Relation to Event Scopes <a id="Relation_to_Event_Scopes"></a>

When a localization string is localized from a scoped context (for example effects or triggers), then the root [Scope](<scopes.md>) is created
from the event scope of that context. For example, an effect that creates a trade route between two countries `FROM` and `THIS`
could be localized with: `LOC_KEY: "Creates a trade route between [FROM.GetName] and [THIS.GetName]"`. For more information on
how the scope accessors `FROM`, `THIS`, `PREV` and `ROOT` works on `Scope` see [Dual Scopes](<scopes.md#Dual_scopes>)

### Documentation of localized objects <a id="Documentation_of_localized_objects"></a>

In general a scoped context (for example, effects and triggers) are localized using a [Scope](<scopes.md>) object based on the scope of that context.
However, there are legacy systems where this may not hold. For other places where localization keys are provided, please see the documentation
for which localization objects that are defined for that context.

<!-- kit:begin id="loc-objects-promotions" at="section:Documentation_of_localized_objects" -->
**Kit addition** The documented localization objects, with the promotions the page does not describe. A promotion is the next object in a chain, as in `[ROOT.Capital.GetName]`. All rows: [docs] `documentation/loc_objects_documentation.md`.

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
- The ten pronoun functions (`GetSheHe`, `GetSheHeCap`, `GetHerHim`, `GetHerHimCap`, `GetHerHis`, `GetHerHisCap`, `GetHersHis`, `GetHersHisCap`, `GetHerselfHimself`, `GetHerselfHimselfCap`) exist on `Country` (for the country's leader), `UnitLeader`, `Ace` and `Character`. The page lists them under characters only. Vanilla usually chains through the leader, as in `[FROM.GetLeader.GetHerHis]`. [docs] `documentation/loc_objects_documentation.md`, [vanilla-confirmed 1.19.3] `localisation/english/*.yml`.
- `GetCallsign` belongs to `Ace` and `GetCodeName` to `UnitLeader` (the operative leader). The "Other scopes" table above gives `GetCallsign` as an operative function. Vanilla uses `[From.GetCallsign]` and `[Prev.GetCallsign]` in ace texts. [docs] `documentation/loc_objects_documentation.md`, [vanilla-confirmed 1.19.3] `localisation/english/*.yml`.
- Promotions work inside ordinary bracket chains. Vanilla uses `[ROOT.Capital.GetName]` and `[ROOT.Capital.GetCapitalVictoryPointName]`, `[From.Owner.GetAdjective]` (14 uses) and `[FROM.Controller.GetNameDef]`. Vanilla GUI text roots a chain at an object: `[Character.GetName]` (35 uses), `[SpecialProject.GetName]` (22), `[State.GetName]` (10), `[Country.GetNameWithFlag]` (6), and the condition form `[(Character?.GetName:'KEY)]` twice. [vanilla-confirmed 1.19.3] `localisation/english/*.yml`.
- `GetDateString`, `GetDateStringShortMonth`, `GetDateStringNoHour`, `GetDateStringNoHourLong`, `GetTokenKey` and `GetTokenLocalizedKey` in the tables above are not in the objects documentation. They are strings in `hoi4.exe`. Vanilla localisation uses two of them: `[?global.date.GetDateStringShortMonth]` and `[?BUL.BUL_date_of_tsars_death.GetDateStringNoHourLong]`. [unverified] (strings in `hoi4.exe`), [vanilla-confirmed 1.19.3] for the two uses.
<!-- kit:end id="loc-objects-promotions" -->

## Namespaces <a id="Namespaces"></a>

Namespaces refer to obtaining certain information from some scope to display in localisation. For example, getting the name of a country, the surname of a character, the ID of a state, and etc.
A namespace is marked with the square brackets on either side as in `my_localisation_key: "[GetDateText]"`. By default, **there is no scope assumed**. A [scope](<scopes.md>) can be added, separated from the namespace with a dot, in order to let the game know from whom to obtain information, such as `my_localisation_key: "[QAT.GetRulingParty]"`, which'll result in the ruling party of the country QAT appearing in localisation. Any dual scope that can be used as a target may be used in localisation. [THIS](<scopes.md>) can be used in order to refer to the scope of where it's used, such as  `effect_tooltip: "[ROOT.GetNameDefCap] declares war on [THIS.GetNameDef]"`.

Variables and event targets can be used within namespaces as well. For example, this grants the name of the capital state of OMA using the 'capital' variable:  `my_localisation_key: "[OMA.capital.GetName]"`. A list of built-in variables that can be used can be seen in [the respective wiki page](<data-structures.md#Game_variables>). Another common ones to use include 'owner' and 'controller' for states, such as `my_localisation_key: "Owner of South-West England: [123.owner.GetName]"`.

**Characters only exist within the scope of the country where they're recruited**, in versions prior to 1.12.8. What this means is that before scoping into the character, one must first scope into the country that they are assigned to, such as  `current_name_of_fdr:0 "[USA.USA_franklin_delano_roosevelt.GetFullName]"`. If the character is marked with some other token (such as THIS or ROOT), this is unnecessary, but it is necessary for direct character IDs. Characters also support scoping to the `GetLeader` localisation function beforehand, such as `leader_pronoun: "[ROOT.GetLeader.GetHeShe]"` In this case, scoping into the country is still necessary.

Note that namespaces cannot be used everywhere. In the majority of the user interface, such as the names for wars or countries, they will not work properly, instead appearing exactly as in localisation, with the square brackets still visible. A list of locations where namespaces *do* work is:

| Location | Notes |
| --- | --- |
| Focuses | Requires `dynamic = yes` within the focus to work correctly for the title, otherwise it generates a value at the game's start and it remains unchanging until the next reload (either of the savefile or the focus tree). Not required for the description, which always dynamically refreshes localisation. |
| Ideas and [dynamic modifiers](<modifiers.md>) | Support for dynamic modifiers was added in 1.13. |
| Decisions |  |
| Events | At times it may be better to use [completely different localisation keys within events](<event-modding.md#Localisation>) instead of using scripted localisation. |
| Custom effect/trigger tooltips | Despite the fact that it works for [effects](<effects.md>) and [triggers](<triggers.md>), custom [modifier](<modifiers.md>) tooltips do not support scripted localisation. |
| Boolean flags | The names of the boolean flags, appearing in the tooltip when checked for them with triggers such as `has_country_flag = flag_name` or `has_character_flag = flag_name` |
| Operations |  |
| Adjacency rule tooltips | Referring to the tooltip that appears when hovering over a strait that's disabled for this country. |
| [Custom interface elements](<interface-modding.md>) | The container with the UI element must be attached to a scripted GUI that has a valid `context_type` within the corresponding `/Hearts of Iron IV/common/scripted_guis/*.txt` file. May require a game restart for it to apply. |

The list may be incomplete, so something not being mentioned does not necessitate that localisation does not work there, but that does make it unlikely. Other localisation functions, not involving square brackets, do still work in this case, however.

### Functions <a id="Functions"></a>

Sometimes, the result of a function may be interpreted as a localisation key itself, but only if the string consists entirely out of that function. For example, `log = "[THIS.GetTag]"` will result in the non-ideology name being logged instead if one exists, since that localisation key consists only of the country tag. However, `log = "loc_key_[ALB.GetTag]"` will log `loc_key_ALB`, even if a localisation key exists with that name.

#### Country scope <a id="Country_scope"></a>

| Name | Example | Description |
| --- | --- | --- |
| GetName | `[GER.GetName]` | Gets the name of the country, the name of the state, or the name of the character. For aces, only gets the first name: see GetFullName. |
| GetTag | `[GER.GetTag]` | Puts the tag of the country into localisation. Particularly useful for [Meta effects](<effects.md#Meta_effects>). |
| GetLeader | `[POL.GetLeader]` | Gets the name of the leader of the country. Can be further scoped into the pronoun-related namespaces, such as `[THIS.GetLeader.GetSheHe]`. |
| GetManpower | `[ENG.GetManpower]` | Gets the total population of the country, including civilians. |
| GetFactionName | `[SOV.GetFactionName]` | Gets the name of the faction that the country is located in. |
| GetAgency | `[FRA.GetAgency]` | Gets the name of the country's intelligence agency. |
| GetFlag | `[GER.GetFlag]` | Gets the current flag of the country. |
| GetNameWithFlag | `[ITA.GetNameWithFlag]` | Gets the current flag of the country and adds the name afterwards. |
| GetNameDef | `[SPR.GetNameDef]` | Gets the DEF name of the country, primarily used to tell if "the" is needed to be put in the beginning. |
| GetNameDefCap | `[POR.GetNameDefCap]` | Gets the DEF name of the country, primarily used to tell if "The" is needed to be put in the beginning, capitalising the first letter as well. |
| GetAdjective | `[YUG.GetAdjective]` | Gets the adjective for the country, such as ![Flag of United Kingdom](media/localisation_0824ba8845__img2.png) British. |
| GetAdjectiveCap | `[CAN.GetAdjectiveCap]` | Gets the adjective for the country, capitalising the first letter. |
| GetOldName | `[RAJ.GetOldName]` | Gets the name of the country without any cosmetic tags applied. |
| GetOldNameDef | `[MAL.GetOldNameDef]` | Gets the DEF name of the country, primarily used to tell if "the" is needed to be put in the beginning, without any cosmetic tags applied. |
| GetOldNameDefCap | `[AST.GetOldNameDefCap]` | Gets the DEF name of the country, primarily used to tell if "The" is needed to be put in the beginning, without any cosmetic tags applied, capitalising the first letter. |
| GetOldAdjective | `[NZL.GetOldAdjective]` | Gets the adjective for the country without any cosmetic tags applied. |
| GetOldAdjectiveCap | `[HAW.GetOldAdjectiveCap]` | Gets the adjective for the country without any cosmetic tags applied, capitalising the first letter. |
| GetNonIdeologyName | `[JAP.GetNonIdeologyName]` | Gets the non-ideology name of the country, defined with `TAG:0 "Country name"` |
| GetNonIdeologyNameDef | `[SAU.GetNonIdeologyNameDef]` | Gets the non-ideology DEF name of the country, primarily used to tell if "the" is needed to be put in the beginning. |
| GetNonIdeologyNameDefCap | `[SWE.GetNonIdeologyNameDefCap]` | Gets the non-ideology DEF name of the country, primarily used to tell if "The" is needed to be put in the beginning, capitalising the first letter. |
| GetNonIdeologyAdjective | `[DEN.GetNonIdeologyAdjective]` | Gets the non-ideology adjective for the country. |
| GetNonIdeologyAdjectiveCap | `[NOR.GetNonIdeologyAdjectiveCap]` | Gets the non-ideology adjective for the country, capitalising the first letter. |
| GetPartySupport | `[ICE.GetPartySupport]` | Gets the percentage of the ruling party, on the scale from 0 to 100. Does not have the % symbol in the end. |
| GetLastElection | `[ROOT.GetLastElection]` | Gets the date when the last country's election occurred in the "HH:00, DD Month, YYYY" format, such as "01:00, 1 January, 1936". |
| GetRulingParty | `[HOL.GetRulingParty]` | Gets the short name of the party ruling over the country. |
| GetRulingPartyLong | `[BEL.GetRulingPartyLong]` | Gets the long name of the party ruling over the country. |
| GetRulingIdeology | `[LUX.GetRulingIdeology]` | Gets the name of the country's ideology group, in adjective form. |
| GetRulingIdeologyNoun | `[GER.GetRulingIdeologyNoun]` | Gets the name of the country's ideology group, in noun form. |
| GetCommunistParty | `[HUN.GetCommunistParty]` | Gets the name of the ![Communism](media/character-modding_41494a4f46__img8.png)Communist party. |
| GetDemocraticParty | `[AUS.GetDemocraticParty]` | Gets the name of the ![Democracy](media/character-modding_cee5ae9645__img1.png)Democratic party. |
| GetFascistParty | `[CZE.GetFascistParty]` | Gets the name of the ![Fascism](media/character-modding_58ea48332f__img14.png)Fascist party. |
| GetNeutralParty | `[ROM.GetNeutralParty]` | Gets the name of the ![Neutrality](media/ai-modding_25696e0a81__img2.png)Non-aligned party. |
| GetCommunistLeader | `[BUL.GetCommunistLeader]` | Gets the name of the leader of the country's ![Communism](media/character-modding_41494a4f46__img8.png)Communist party. |
| GetDemocraticLeader | `[GRE.GetDemocraticLeader]` | Gets the name of the leader of the country's ![Democracy](media/character-modding_cee5ae9645__img1.png)Democratic party. |
| GetFascistLeader | `[ALB.GetFascistLeader]` | Gets the name of the leader of the country's ![Fascism](media/character-modding_58ea48332f__img14.png)Fascist party. |
| GetNeutralLeader | `[TUR.GetNeutralLeader]` | Gets the name of the leader of the country's ![Neutrality](media/ai-modding_25696e0a81__img2.png)Non-aligned party. |
| GetPowerBalanceName | `[ITA.GetPowerBalanceName]` | Gets the name of the country's currently-active balance of power. |
| GetPowerBalanceModDesc | `[ITA.GetPowerBalanceModDesc]` | Gets the names of the country's currently-active [balance of power modifiers](<modifiers.md#Balance_of_power_modifiers>) and their effects towards the BoP. For the modifiers applied by the active range, see GetActiveRangeModDesc. |
| GetRightSideName | `[ITA.GetRightSideName]` | Gets the name of the country's right side in the currently-active balance of power. |
| GetLeftSideName | `[ITA.GetLeftSideName]` | Gets the name of the country's left side in the currently-active balance of power. |
| GetActiveSideName | `[ITA.GetActiveSideName]` | Gets the name of the side in the country's currently-active balance of power that has more power. |
| GetTrendingSideName | `[ITA.GetTrendingSideName]` | Gets the name of the side in the country's currently-active balance of power that the balance is changing towards. |
| GetActiveRangeName | `[ITA.GetActiveRangeName]` | Gets the name of the range in the country's currently-active balance of power that is currently active, granting its modifiers. |
| GetActiveRangeModDesc | `[ITA.GetActiveRangeModDesc]` | Gets the modifiers applied by the active range in the country's currently-active balance of power. Uses the `BOP_RANGE_MODIFIER` localisation key. |
| GetActiveRangeRuleDesc | `[ITA.GetActiveRangeRuleDesc]` | Gets the game rules modified by the active range in the country's currently-active balance of power. Uses the `BOP_RANGE_RULE` localisation key. |
| GetActiveRangeActivationEffect | `[ITA.GetActiveRangeActivationEffect]` | Gets the tooltip for the effects executed when entering the active range in the country's currently-active balance of power. Uses the `BOP_RANGE_ACTIVATION_EFFECT` localisation key. |
| GetActiveRangeDeactivationEffect | `[ITA.GetActiveRangeDeactivationEffect]` | Gets the tooltip for the effects executed when exiting the active range in the country's currently-active balance of power. Uses the `BOP_RANGE_DEACTIVATION_EFFECT` localisation key. |
| GetChangeRateDesc | `[ITA.GetChangeRateDesc]` | Gets the rate by which the balance of power is changed weekly and/or daily and towards which side. May use `BOP_CHANGE_RATE_DAILY` or `BOP_CHANGE_RATE_WEEKLY` localisation keys depending on the current BoP modifiers, prioritising the former if possible. |
| GetBopTrendTextIcon | `[ITA.GetBopTrendTextIcon]` | Selects the text icon corresponding towards which side is getting power. May select either `GFX_BoP_left_texticon`, `GFX_BoP_right_texticon`, or nothing. |

#### Other scopes <a id="Other_scopes"></a>

Date variable in this case refers to a variable set to a date value. Using it with the current date can be done by using the global.date variable as `[?global.date.GetDateString]`.

| Name | Scope | Example | Description |
| --- | --- | --- | --- |
| GetName | State, character, operative, ace | `[123.GetName]`<br> `[POL.POL_character.GetName]` | Gets the name of the state or the name of the character. For aces, only gets the first name: see GetFullName. |
| GetName | MIO | `[?ID.GetName]``[?BEL_cockerill_organization.GetName]` | Gets the name of the MIO. |
| GetDateText | Any | `[GetDateText]` | Gets the date in the format of "HH:00, DD Month, YYYY", such as "12:00, 1 January, 1936". |
| GetDate | Any | `[GetDate]` | Gets the date in the format of YYYY.MM.DD.HH, such as 1936.1.1.12. |
| GetMonth | Any | `[GetMonth]` | Gets the current month. |
| GetYear | Any | `[GetYear]` | Gets the current year. |
| GetID | State | `[123.GetID]` | Gets the ID of the state. Particularly useful for [Meta effects](<effects.md>). |
| GetCapitalVictoryPointName | State | `[540.GetCapitalVictoryPointName]` | Gets the name of the capital victory point (i.e. the province with the largest amount of victory points) of the state. |
| GetSheHe | Character | `[PRU.GetLeader.GetSheHe]` | Results in either "she" or "he" depending on the gender of the character, beginning with lowercase letters. |
| GetSheHeCap | Character | `[MEX.MEX_character.GetSheHeCap]` | Results in either "She" or "He" depending on the gender of the character, beginning with uppercase letters. |
| GetHerHim | Character | `[BRA.BRA_character.GetHerHim]` | Results in either "her" or "him" depending on the gender of the character, beginning with lowercase letters. |
| GetHerHimCap | Character | `[ARG.ARG_character.GetHerHimCap]` | Results in either "Her" or "Him" depending on the gender of the character, beginning with uppercase letters. |
| GetHerHis | Character | `[CHI.CHI_character.GetHerHis]` | Results in either "her" or "his" depending on the gender of the character, beginning with lowercase letters. |
| GetHerHisCap | Character | `[CHL.CHL_character.GetHerHisCap]` | Results in either "Her" or "His" depending on the gender of the character, beginning with uppercase letters. |
| GetHersHis | Character | `[PRC.PRC_character.GetHersHis]` | Results in either "hers" or "his" depending on the gender of the character, beginning with lowercase letters. |
| GetHersHisCap | Character | `[YUN.YUN_character.GetHersHisCap]` | Results in either "Hers" or "His" depending on the gender of the character, beginning with uppercase letters. |
| GetHerselfHimself | Character | `[GXC.GXC_character.GetHerselfHimself]` | Results in either "herself" or "himself" depending on the gender of the character, beginning with lowercase letters. |
| GetHerselfHimselfCap | Character | `[XSM.XSM_character.GetHerselfHimselfCap]` | Results in either "Herself" or "Himself" depending on the gender of the character, beginning with uppercase letters. |
| GetIdeology | Country leader | `[?country_leader.GetIdeology]` | Gets the ideology *group* assigned to the country leader, such as ![Democracy](media/character-modding_cee5ae9645__img1.png)Democratic or ![Neutrality](media/ai-modding_25696e0a81__img2.png)Non-aligned. |
| GetIdeologyGroup | Country leader | `[?country_leader.GetIdeologyGroup]` | Gets the ideology *type* assigned to the country leader, such as Liberalism or Centrism. The name is misleading. |
| GetRank | Unit leader | `[MEN.MEN_character.GetRank]` | Gets the rank of the unit leader, such as Corps Commander or Field Marshal. |
| GetCodeName | Operative | `[THIS.GetCodeName]` | Gets the codename of the operative. |
| GetCallsign | Operative | `[THIS.GetCallsign]` | Gets the callsign of the operative. |
| GetSurname | Ace | `[LIB.GetLeader.GetSurname]` | Gets the last name of the ace. |
| GetFullName | Ace | `[ECU.ECU_character.GetFullName]` | Gets the full name of the ace, with both first and last names. |
| GetWing | Ace | `[THIS.GetWing]` | Gets the wing that the ace is assigned to. |
| GetWingShort | Ace | `[THIS.GetWingShort]` | Gets the shortened name of the wing that the ace is assigned to. |
| GetAceType | Ace | `[THIS.GetAceType]` | Gets the type of the ace. |
| GetMissionRegion | Ace | `[THIS.GetMissionRegion]` | Gets the region that the ace is assigned to. |
| GetTokenKey | Any [token variable](<data-structures.md#Token-valued_variables>) | `[?global.variablename.GetTokenKey]` | Gets the token of the variable, such as infantry_equipment, instead of the internal ID. Particularly useful for [Meta effects](<effects.md>). |
| GetTokenLocalizedKey | Any [token variable](<data-structures.md#Token-valued_variables>) | `[?GER.variablename.GetTokenLocalizedKey]` | Returns the *localised* name of the variable, such as "Infantry Equipment", by converting an internal identifier or database object, such as `infantry_equipment` into its localised equivalent, provided a localization key exists for it. This functionality becomes invaluable for advanced abstraction techniques. For instance, it can approximate arbitrary string interpolation (string interpolaration is the ability to embed expressions or variables within a string literal in a programming language) in [Meta effects](<effects.md>) by applying it to token variables that reference dummy objects (e.g., empty ideas) with predefined arbitrary localization strings. By passing token variables that resolve to localized dummy objects, developers can achieve a level of flexibility similar to direct string manipulation.  Additionally, concatenating the localization values of two dummy tokens can produce a new token string. This string can then be inserted into a token variable within a Meta effect, provided the resulting token string corresponds to a valid existing token. If the resulting token is invalid, the function will simply return an integer value of 0.  Effectively, this approach allows for the derivation of previously-unknown token variables from known ones, following a template defined by another known token variable. This is particularly useful when the destination token follows a templated variation (via prefixes or suffixes) of the source token. |
| GetDateString | Date variable | `[?global.date.GetDateString]` | Gets the date in the format of "HH:00, DD Month, YYYY", such as "12:00, 1 January, 1936". |
| GetDateStringShortMonth | Date variable | `[?global.date.GetDateStringShortMonth]` | Gets the date in the format of "HH:00, DD Mon., YYYY", such as "12:00, 1 Jan., 1936". |
| GetDateStringNoHour | Date variable | `[?global.date.GetDateStringNoHour]` | Gets the date in the format of YYYY.MM.DD, such as 1936.1.1. |
| GetDateStringNoHourLong | Date variable | `[?global.date.GetDateStringNoHourLong]` | Gets the date in the format of "DD Month, YYYY", such as "1 January, 1936". |

## Scripted localisation <a id="Scripted_localisation"></a>

Scripted localisation is similar to creating your own namespaces. It is defined in `/Hearts of Iron IV/common/scripted_localisation/*.txt` and used in localisation in a similar manner to namespaces. However, unlike namespaces, by default the current scope is assumed when using scripted localisation, making scoping optional.
An example of a scripted localisation definition is:

```text
defined_text = {
    name = mod_scripted_loc
    text = {
        trigger = {
            tag = FRA
        }
        localization_key = FRA_localization_key
    }
    text = {
        localization_key = mod_localization_key
    }
}
```

This consists of these entries:

- `name = my_scripted_loc` - The name of the scripted localisation used to refer to it within regular localisation.
- `text = { ... }` - A possible choice for localisation. The game picks the topmost `text = { ... }` block to serve as the localisation's output. In particular, these are used in the example:
  - `trigger = { ... }` is the trigger block evaluated for the checked scope, using this scripted localisation if true. [Temporary variables](<data-structures.md>) set in this trigger block will remain set when displaying the localisation key, allowing math to be done between different variables or using scripted localisation recursively (such as to display every element of an [array](<data-structures.md>)).
  - `localization_key = my_loc_key` (Note the American spelling with Z rather than the British spelling with S used elsewhere) assigns the localisation key to be used with this scripted localisation option.

The example above will show the FRA_localization_key localisation key for France and the mod_localization_key one otherwise as a backup. **The first localization key that meets the triggers will be used**, meaning it is often more intuitive to specify localisation entries with more specific requirements first before those with more general triggers. In localisation, that example can be used as

```yaml
l_english:
 some_localisation: "[mod_scripted_loc]"
 FRA_localization_key: "France-exclusive localisation"
 mod_localization_key: "Generic localisation"
```

Scripted localisation also allows randomisation of the localisation key that would be chosen, using [random_list](<effects.md>). For example, the following code will give a 60% and a 40% chance respectively for mod_localization_key_1 or mod_localization_key_2 to be chosen when this scripted localisation entry is used:

```text
defined_text = {
    name = mod_scripted_loc
    text = {
        random_list = {
            30 = { localization_key = mod_localization_key_1 }
            20 = { localization_key = mod_localization_key_2 }
        }
    }
}
```

<!-- kit:begin id="loc-scripted-scope-and-seed" at="section:Scripted_localisation" -->
**Kit addition** Scripted localisation as vanilla writes it. All items: [vanilla-confirmed 1.19.3] `common/scripted_localisation/`.

- The header comment of `00_scripted_localisation.txt` says the `trigger` blocks must be valid for the scope the key is called in, giving Root or From.From as examples. Vanilla calls the entry as `[ROOT.GetImportOrDomesticFilmIndustry]` and also as a bare `[GetReichsWerkeName]`, so write the call with the scope your triggers expect.
- Vanilla has 1,537 `defined_text` entries in 42 files. Entries commented `# Country` expect a country scope.
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

### Dynamic scripted localisation <a id="Dynamic_scripted_localisation"></a>

The `localization_key` argument now directly supports the use of dynamic localisation. That is, it is possible to use a piece of dynamic localisation *as part* of a localisation key call. This allows for a far more streamlined system of localisation automation when it is needed. For example:

```text
defined_text = {
    name = mod_scripted_loc
    text = {
        localization_key = "mod_localization_version_[?my_variable]"
    }
}
```

When the scripted localisation is called, it will read the value of `my_variable` and place the value into the string of the localisation key as specified and evaluate the entire localisation key as a whole after the variable has been implemented.

```yaml
l_english:
 some_localisation: "[mod_scripted_loc]"
 mod_localization_version_1: "This localization will be called when my_variable is equal to 1."
 mod_localization_version_2: "This localization will be called when my_variable is equal to 2."
 mod_localization_version_3: "This localization will be called when my_variable is equal to 3."
```

### Temporary variable display <a id="Temporary_variable_display"></a>

Temporary variables allow for [calculations within triggers](<data-structures.md#Trigger_usage>), and with scripted localisation, the result of such calculations can be directly shown in text without the need to use a separate variable. This is especially useful if a desired value is inherently tied to another variable, saving the necessity of having to constantly update a variable to the new value.

An example of this use case is to display money with dynamic units, i.e. millions, billions, trillions, where the basic unit assigned to a variable `gdp_value` is in **billions**, and we wish to change the display units to **millions** when `gdp_value` is under 1 and to **trillions** when `gdp_value` reaches 1,000. Below is an implementation of it using scripted localisation and local temporary variable calculation.

```text
defined_text = {
    name = gdp_display_units
    text = {
        trigger = {
            check_variable = {
                var = gdp_value
                value = 1000
                compare = greater_than_or_equals
            }

            # 1 trillion is 1,000 billion
            set_temp_variable = { temp_display_T = gdp_value }
            divide_temp_variable = { temp_display_T = 1000 }
        }
        localization_key = trillions
    }
    text = {
        trigger = {
            check_variable = {
                var = gdp_value
                value = 1
                compare = greater_than_or_equals
            }

            # billions display case
            set_temp_variable = { temp_display_B = gdp_value } # note that the localization could simply use [?gdp_value|2] instead of [?temp_display_B|2]. This is done as such for demonstration.
        }
        localization_key = billions
    }
    text = {
        trigger = {
            # 1 million is 0.001 billion
            set_temp_variable = { temp_display_M = gdp_value }
            multiply_temp_variable = { temp_display_M = 1000 }
        }
        localization_key = millions
    }
}
```

In localisation,

```yaml
l_english:
 total_gdp: "Our total GDP is [gdp_display_units]"
 # localisation keys belonging to [gdp_display_units]
 trillions: "$$[?temp_display_T|2]T"
 billions: "$$[?temp_display_B|2]B"
 millions: "$$[?temp_display_M|2]M"
```

*Note that the double dollar signs (`$$`) are necessary to differentiate this from a localization key call.*

In this example, a `gdp_value` of 5000 will display as `$5.00T`, a `gdp_value` of 300 will display as `$300.00B`, and a `gdp_value` of 0.520 will display as `$520.00M`

As can be seen, the temporary variable value that has been calculated within their corresponding `trigger` blocks can be called like any other variable, but is only accessible within the scripted localisation itself and nowhere else. While the temporary variables can be accessed by localisation keys further down from the `trigger` (and subsequently `text`) block that it was calculated in, it is still good practice to organize it this way to not lose track of which temporary variable calculations belong to which localisation key.\\

## Hard-to-find Localisation Info <a id="Hard-to-find_Localisation_Info"></a>

The following localisation entries are undocumented and hard to find within base-game code

### War Naming <a id="War_Naming"></a>

Custom names for wars can be set through

```text
WAR_NAME_TAG1_TAG2:""
```

TAG1 is the attacker, TAG2 is the defender. The naming supports using $FIRST$ and $SECOND$ to directly access the adjective forms of the respective tags. $FIRST$ would be the same as `[TAG1.GetAdjective]`

<!-- kit:begin id="loc-war-name-keys" at="section:War_Naming" -->
**Kit addition** The war name keys vanilla defines. All rows: [vanilla-confirmed 1.19.3] `localisation/english/war_l_english.yml`.

| Key | Vanilla value | Placeholders |
| --- | --- | --- |
| `WAR_NAME` | `$ORDER$$FIRST$-$SECOND$ War` | `$ORDER$`, `$FIRST$`, `$SECOND$` |
| `CIVIL_WAR_NAME` | `$ORDER$$SECOND$ Civil War` | `$ORDER$`, `$SECOND$` |
| `INDEPENDENCE_WAR_NAME` | `$ORDER$$FIRST$ War of Independence` | `$ORDER$`, `$FIRST$` |
| `WAR_TAKE_CORE_NAME` | `$ORDER$$FIRST$ reclamation of $STATE$` | `$ORDER$`, `$FIRST$`, `$STATE$` |
| `WAR_TAKE_CLAIM_NAME` | `$ORDER$$FIRST$ Aggression for $STATE$` | `$ORDER$`, `$FIRST$`, `$STATE$` |
| `WAR_NAME_ITA_ETH` | `Italian War on Ethiopia` | none; the only vanilla key of the form `WAR_NAME_TAG1_TAG2` |

The keys `ST`, `ND`, `RD` and `TH` next to them hold the ordinal suffixes, so `$ORDER$` is presumably the war's ordinal. [unverified] (inferred from the neighbouring keys)
<!-- kit:end id="loc-war-name-keys" -->

### Division Commander Ranks <a id="Division_Commander_Ranks"></a>

```text
DIVISION_EXPERIENCE_TITLE_ARMY_EXPERIENCE_0:""
DIVISION_EXPERIENCE_TITLE_ARMY_EXPERIENCE_1:""
DIVISION_EXPERIENCE_TITLE_ARMY_EXPERIENCE_2:""
DIVISION_EXPERIENCE_TITLE_ARMY_EXPERIENCE_3:""
DIVISION_EXPERIENCE_TITLE_ARMY_EXPERIENCE_4:""
```

The base game default goes from Brigadier (0) to Lieutenant-General (4)

<!-- kit:begin id="loc-division-rank-overrides" at="section:Division_Commander_Ranks" -->
**Kit addition** Each key can be prefixed with a tag: `GER_DIVISION_EXPERIENCE_TITLE_ARMY_EXPERIENCE_0` overrides the generic key for Germany. Vanilla English defines the override for 25 tags (`CHI`, `ETH`, `FIN`, `FRA`, `GDC`, `GER`, `GSM`, `GXC`, `HBC`, `ITA`, `JAP`, `KHM`, `KUM`, `NOR`, `NXM`, `PRC`, `SHX`, `SIC`, `SIK`, `SND`, `SOV`, `USA`, `XIC`, `XSM`, `YUN`); `USA` defines only levels 0 and 1. The generic values are `Brigadier` for 0 and 1, `Major-General` for 2 and 3, and `Lt-General` for 4. [vanilla-confirmed 1.19.3] `localisation/english/unit_medals_l_english.yml`.
<!-- kit:end id="loc-division-rank-overrides" -->

## References <a id="References"></a>

1. ↑ https://twitter.com/Martin_Anward/status/1039175213773144066

<!-- kit:begin id="loc-checks" at="bottom" -->
## Kit: checking localisation <a id="kit-checking-localisation"></a>

**Kit addition** Console commands that find missing localisation, and the file that silences them.

- `loc_check` checks for missing localization; `loc_check_characters`, `loc_check_decisions`, `loc_check_events`, `loc_check_focuses`, `loc_check_modifiers` and `loc_check_national_spirits` do the same for one kind of entry. [docs] `documentation/console_commands_documentation.md`.
- `update_loc <localization tag>` updates the localization tag file. `dump_equipment_loc` writes equipment names, or descriptions with `desc`, to `logs/equipment_loc.csv` by default, with `path=<filepath>` to change the file. [docs] `documentation/console_commands_documentation.md`.
- `localisation/ignored_loc_keys.txt` begins "Add loc keys to this file to have them ignored by the loc_check* console commands" and lists test keys such as `test.1.a`. [vanilla-confirmed 1.19.3] `localisation/ignored_loc_keys.txt`.
<!-- kit:end id="loc-checks" -->

---

## Navigation

**[Modding](<modding.md>)**

- **Documentation**: [Effects](<effects.md>) • [Triggers](<triggers.md>) • [Defines](<defines.md>) • [Modifiers](<modifiers.md>) • [List of modifiers](<list-of-modifiers.md>) • [Scopes](<scopes.md>) • [On actions](<on-actions.md>) • [Data structures](<data-structures.md>) • [Flags](<data-structures.md#Flags>) • [Event targets](<data-structures.md#Event_targets>) • [Country tag aliases](<data-structures.md#Country_tag_aliases>) • [Variables](<data-structures.md#Variables>) • [Arrays](<data-structures.md#Arrays>)
- **Scripting**: [Achievements](<achievement-modding.md>) • [AI](<ai-modding.md>) • [AI focuses](<ai-focuses.md>) • [Autonomous states](<autonomy-state-modding.md>) • [Balances of power](<balance-of-power-modding.md>) • [Bookmarks/Scenarios](<bookmark-modding.md>) • [Game rules](<bookmark-modding.md#Game_rules>) • [Buildings](<building-modding.md>) • [Characters and traits](<character-modding.md>) • [Cosmetic tags](<cosmetic-tag-modding.md>) • [Countries](<country-creation.md>) • [Divisions](<division-modding.md>) • [Decisions](<decision-modding.md>) • [Doctrines](<doctrine-modding.md>) • [Equipment](<equipment-modding.md>) • [Events](<event-modding.md>) • [Factions](<faction-modding.md>) • [Ideas](<idea-modding.md>) • [Ideologies](<ideology-modding.md>) • [Military industrial organizations](<military-industrial-organization-modding.md>) • [National focuses](<national-focus-modding.md>) • [Resources](<resources-modding.md>) • [Scripted GUI](<scripted-gui-modding.md>) • [Technologies and doctrines](<technology-modding.md>) • [Units](<unit-modding.md>)
- **Map**: [Map](<map-modding.md>) • [States](<state-modding.md>) • [Supply areas](<supply-areas-modding.md>) • [Strategic regions](<strategic-region-modding.md>)
- **Graphical**: [Interface](<interface-modding.md>) • [Graphical assets](<graphical-asset-modding.md>) • [Entities](<entity-modding.md>) • [Posteffects](<posteffect-modding.md>) • [Particles](<particle-modding.md>) • [Fonts](<font-modding.md>)
- **Cosmetic**: [Portraits](<portrait-modding.md>) • [Namelists](<namelist-modding.md>) • [Music](<music-modding.md>) • [Sound](<sound-modding.md>)
- **Other**: [Console commands](<console-commands.md>) • [Troubleshooting](<troubleshooting.md>) • [Mod structure](<mod-structure.md>) • [Mods](<mods.md>) • [Nudger](<nudger.md>)
- **Kit pages (not on the wiki)**: [Collection modding](<collection-modding.md>) • [Defines additions](<defines-additions.md>) • [Game rule modding](<game-rule-modding.md>) • [Intelligence operation modding](<intelligence-operation-modding.md>) • [Map mode modding](<map-mode-modding.md>) • [Occupation and resistance modding](<occupation-and-resistance-modding.md>) • [Peace conference modding](<peace-conference-modding.md>) • [Raid modding](<raid-modding.md>) • [Script constant modding](<script-constant-modding.md>) • [Special project modding](<special-project-modding.md>)
