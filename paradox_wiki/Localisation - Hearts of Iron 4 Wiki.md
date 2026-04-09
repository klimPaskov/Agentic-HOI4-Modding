# Table of contents

- [Quick checklist](#quick-checklist)
- [Basics](#basics)
- [Replacing](#replacing)
- [Special characters](#special-characters)
  - [Colouring characters](#colouring-characters)
    - [Errors](#errors)
  - [Formatting variables](#formatting-variables)
  - [Country's flags](#countrys-flags)
  - [Text icons](#text-icons)
- [Nesting strings](#nesting-strings)
- [Bindable localisation](#bindable-localisation)
    - [Usage of Bindable Localization](#usage-of-bindable-localization)
  - [Context-Aware Tooltips](#context-aware-tooltips)
  - [Localization Formatters](#localization-formatters)
- [Localization Formatters](#localization-formatters)
- [Contextual Localization](#contextual-localization)
  - [Using a localization object](#using-a-localization-object)
  - [Condition in contextual localization](#condition-in-contextual-localization)
  - [Relation to Event Scopes](#relation-to-event-scopes)
  - [Documentation of localized objects](#documentation-of-localized-objects)
- [Namespaces](#namespaces)
  - [Functions](#functions)
    - [Country scope](#country-scope)
    - [Other scopes](#other-scopes)
- [Scripted localisation](#scripted-localisation)
  - [Dynamic Scripted Localisation](#dynamic-scripted-localisation)
- [References](#references)


---

HOI4 uses the modified YAML **localisation** system used by modern Paradox games.

The localisation is stored within the /Hearts of Iron IV/localisation/ folder, in which any sub-folder can be used. Each file is assigned a language with its filename by adding it in the end, with the following languages existing:

- `l_english`: English, as in /Hearts of Iron IV/localisation/english/filename\_l\_english.yml
- `l_french`: French, as in /Hearts of Iron IV/localisation/french/mod\_file\_l\_french.yml
- `l_german`: German, as in /Hearts of Iron IV/localisation/german/state\_names\_l\_german.yml
- `l_spanish`: Spanish, as in /Hearts of Iron IV/localisation/spanish/mod\_germany\_l\_spanish.yml
- `l_braz_por`: Brazilian Portuguese, as in /Hearts of Iron IV/localisation/braz\_por/bahrain\_l\_braz\_por.yml
- `l_polish`: Polish, as in /Hearts of Iron IV/localisation/polish/myfile\_l\_polish.yml
- `l_russian`: Russian, as in /Hearts of Iron IV/localisation/russian/siberia\_l\_russian.yml
- `l_japanese`: Japanese, as in /Hearts of Iron IV/localisation/japanese/kuril\_l\_japanese.yml
- `l_simp_chinese`: Simplified Chinese, as in /Hearts of Iron IV/localisation/simp\_chinese/khalkha\_l\_simp\_chinese.yml
- `l_korean`: Korean, as in /Hearts of Iron IV/localisation/korean/victory\_points\_l\_korean.yml

The filename **has to contain the language's internal name** as the file will not be loaded otherwise.  
The currently-enabled language is chosen within the user directory's /Hearts of Iron IV/pdx\_settings.txt file, however, more languages cannot be added directly other than these listed languages.

## Quick checklist

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

## Basics

Localisation is created within any file in the localisation folder: the filename aside from the file extension is irrelevant aside from deciding which language is chosen.  
**Every localisation file must use the UTF-8-BOM encoding**, i.e. the UTF-8 encoding with the byte order mark in the beginning of the file. Exact details depend on the text editor:

- Notepad++: Top bar's "Encoding" menu provides a selection of encodings. UTF-8-BOM is used in this case.
- Sublime Text: Top bar's "File" menu provides the "Save with Encoding" selection. UTF-8 with BOM is used in this case.
- Visual Studio Code: In the bottom bar, there's the "Select Encoding" button titled with the current encoding (Usually "UTF-8" or "UTF-8 with BOM"). To convert, this must be pressed and then "Save with encoding" must be selected with "UTF-8 with BOM".

Each localisation key must be assigned to a language database, marked with a line containing the language name ending with a colon, and nothing else. For example, `l_english:`. Until the next database entry or the end of file, this will assign every localisation key afterwards to the English language. A single file may contain entries for databases of multiple languages at the same time, however the filename must also contain each of these languages.

Next lines are structured in the format of `localisation_key:0 "Localisation value"`. In here:

- localisation\_key is the localisation key that is being localised. This is usually the same as the name of the database entry (e.g. a focus with the name of TAG\_focusname will have TAG\_focusname as the needed localisation key). Other times, it's possible or required to set in the database entry itself (e.g. `title = my_event.1.t` within an event). Commonly, appending \_desc as TAG\_focusname\_desc provides the localisation key for the description, such as with characters, focuses, ideas, traits, and so on.

**The localisation key cannot have special characters in it**, where a special character is defined as taking up more than 1 byte using the UTF-8 encoding. This includes every character other than those in [the ASCII character system](http://en.wikipedia.org/wiki/ASCII#Printable_character), so in essence localisation keys shouldn't have anything other than English letters, underscores, dots, and numbers. Localisation keys additionally cannot include spaces in them. Either one will show up within the error log as an error of the sort of `Expected colon(:) at line <...>`.

- 0 is the version number, used for Paradox's internal translation tracking. This is never read in-game, and it can be omitted entirely with no difference in interpretation. Since this is introduced by Paradox and is invalid in standard YAML formatting, this may break the default syntax highlighting used for YAML in text editors. The version number can only contain numeric characters, anything else such as a hyphen is unexpected.
- Localisation value refers to the text that will show up in-game. **This must be on one line total**, multiple lines will break the file. Instead, newlines are marked using `\n` (Note that this is a backslash rather than a regular slash), such as `localisation_key: "First line.\nSecond line."` A space after the \n should be avoided, as it will appear in-game as offsetting the next lines. If you want to include quotation marks in text then `localisation_key: "Quote: \"This is a quote\""` should be used to avoid errors.

Any issue with localisation, such as special characters or spaces in localisation keys or a missing quote, will break the localisation file starting with the point where the syntax first stopped being followed correctly.

An example of a localisation file's contents is the following:

```text
l_english
infantry_equipment
"Infantry
 
Equipment"

 
infantry_equipment_short
"Inf.
 
Eq."

 
infantry_equipment_desc
"This
 
is
 
infantry
 
equipment"
```

Nearly any printable character is allowed to use within the localisation value, other than certain special characters with special meaning, such as square brackets, or newlines. However, only some select characters are present in the fonts that are used in the game, and the selection of characters differs depending on the font. If the used font doesn't include a representation of a character, the game will replace it with a question mark (?). This affects only the font representation: this may be remedied by switching the used font within the [interface](<Interface modding - Hearts of Iron 4 Wiki.md>) or by changing the font to include the letter.

## Replacing

Typically, localisation key overlap must be avoided, overlap being the same localisation key being defined several times in the same language's files. This is tracked within [user directory](<Modding - Hearts of Iron 4 Wiki.md>)'s /Hearts of Iron IV/logs/text.log file, which contains a list of overlapping localisation keys if any. The value that'll get chosen does not seem to have a consistent pattern, but seems to prioritise base game files.

However, if the localisation file is contained within a folder with the name of "replace" (such as /Hearts of Iron IV/localisation/english/replace, still must be inside of localisation), it will get priority over the entries that are not. This can be helpful to overwrite only specific localisation keys without porting over the entire file, such as if the file gets frequently updated in base game.

For example, if desiring to change the name of the effect to add political power from the default  `POLITICS_ADD_POLITICAL_POWER:0 "Political Power: $VAL|=+0$."`, it may be undesirable to port over the entire /Hearts of Iron IV/localisation/english/effects\_l\_english.yml file to the mod, as new effects frequently get added to the game which would mean the file has to be kept in check.  
However, instead creating a new localisation file within the /Hearts of Iron IV/localisation/english/replace/ folder and defining the POLITICS\_ADD\_POLITICAL\_POWER localisation key there will result in the value of the key getting changed without needing to copy the entire localisation file, meaning that the mod is now easier to port to future updates.

For example, /Hearts of Iron IV/localisation/english/replace/mod\_replace\_l\_english.yml would contain the following content:

```text
l_english
POLITICS_ADD_POLITICAL_POWER
"New
 
mana:
 
$VAL|=+0$."
```

## Special characters

### Colouring characters

Various characters can be added to a string to alter its colour in-game. A colouring character formatting begins with a section sign (§) and includes a single letter (byte) afterwards used to identify the colour. The exclamation point is used to mark the end of a colouring rule. The end of a string doesn't necessarily mean that the colouring rule will end, meaning its use is mandatory with every colouring rule to avoid spillover into the next text, even if it should last until the end of the string. On Windows, the `Alt`+`21` [alt code](http://en.wikipedia.org/wiki/Alt_code) can be used to input a section sign.

The following formatting characters are implemented in the base game (The colour provided is the default generic colour and may be different depending on the font):

- **§!**
  - Effect: Ends the current formatting rule.
  - Exact colour: None.

- **§C**
  - Effect: Colours the text cyan.
  - Exact colour: ( 35, 206, 255 )

- **§L**
  - Effect: Colours the text a dirty orange-gray (labeled "lilac").
  - Exact colour: ( 195, 176, 145 )

- **§W**
  - Effect: Colours the text white.
  - Exact colour: ( 255, 255, 255 )

- **§B**
  - Effect: Colours the text blue.
  - Exact colour: ( 0, 0, 255 )

- **§G**
  - Effect: Colours the text green.
  - Exact colour: ( 0, 159, 3 )

- **§R**
  - Effect: Colours the text red.
  - Exact colour: ( 255, 50, 50 )

- **§b**
  - Effect: Colours the text black.
  - Exact colour: ( 0, 0, 0 )

- **§g**
  - Effect: Colours the text light gray.
  - Exact colour: ( 176, 176, 176 )

- **§Y**
  - Effect: Colours the text yellow.
  - Exact colour: ( 255, 189, 0 )

- **§H**
  - Effect: Colours the text yellow (same as §Y, labeled "header").
  - Exact colour: ( 255, 189, 0 )

- **§T**
  - Effect: Colours the text white (same as §W, labeled "Title").
  - Exact colour: ( 255, 255, 255 )

- **§O**
  - Effect: Colours the text orange.
  - Exact colour: ( 255, 112, 25 )

- **§0**
  - Effect: Colours the text purple (labeled "Gradient Step 0").
  - Exact colour: ( 203, 0, 203 )

- **§1**
  - Effect: Colours the text lilac (labeled "Gradient Step 1").
  - Exact colour: ( 128, 120, 211 )

- **§2**
  - Effect: Colours the text blue (labeled "Gradient Step 2").
  - Exact colour: ( 81, 112, 243 )

- **§3**
  - Effect: Colours the text gray-blue (labeled "Gradient Step 3").
  - Exact colour: ( 81, 143, 220 )

- **§4**
  - Effect: Colours the text light blue (labeled "Gradient Step 4").
  - Exact colour: ( 90, 190, 231 )

- **§5**
  - Effect: Colours the text dull cyan (labeled "Gradient Step 5").
  - Exact colour: ( 63, 181, 194 )

- **§6**
  - Effect: Colours the text turquoise (labeled "Gradient Step 6").
  - Exact colour: ( 119, 204, 186 )

- **§7**
  - Effect: Colours the text light green (labeled "Gradient Step 7").
  - Exact colour: ( 153, 209, 153 )

- **§8**
  - Effect: Colours the text an orange-yellow (labeled "Gradient Step 8").
  - Exact colour: ( 204, 163, 51 )

- **§9**
  - Effect: Colours the text white-orange (labeled "Gradient Step 9").
  - Exact colour: ( 252, 169, 125 )

- **§t**
  - Effect: Colours the text vivid red (labeled "Gradient Step 10").
  - Exact colour: ( 255, 76, 77 )

Here is an example of the colour formatting:

```text
l_english
example_key
"This
 
is
 
my
 
text,
 
§Bthis
 
text
 
is
 
blue§!,
 
and
 
§Rthis
 
text
 
is
 
red§!"
```

New text colours can be added by expanding the `textcolors = { ... }` array in /Hearts of Iron IV/interface/core.gfx. Colour keys *cannot* have more than one letter (i.e. "BU = {0 255 0}"), and will attempt to overwrite another colour key with the same first letter. It is also possible to make a colouring character represent a different colour from default when a certain font is used within the bitmapfont definition of that font.

#### Errors

The errors related to the colouring characters can be fairly unintuitive to find, considering that they do not provide the location of the file.  
There are three types of the error:

- `Could not find coloring for character 'M'` – This exact example means that, somewhere, the game found `§M` within localisation; however, since "M" isn't a valid colour, this is an unexpected result. The exact character is provided, so finding the cause should be elementary. A space is also considered a character, so `Could not find coloring for character ' '` means that somewhere in localisation `§`  is present, with a symbol specifying the beginning or end of a colouring rule omitted.
- `Could not find coloring for character id '17'` – Note that it specifies the character ID. In this case, the [printable Unicode character ID is provided](http://en.wikipedia.org/wiki/List_of_Unicode_characters#Latin_script). This is typically done where providing the actual character would be confusing (e.g. for the number "1", the game would specify the character id "17" if such a colour doesn't exist. Since "1" is the 18th printed character, it has the id of 17, as the numeration typically starts from 0.)

This has a notable exception: the character id '0' may refer to the NULL character rather than a space. In other words, the character id '0' means there is *absolutely nothing* after the § symbol, i.e. the string ends with §. As such, locating this error would be done by searching for `§"` This is usually caused by omitting the exclamation mark from the character to end the colour formatting, which would properly be `§!`.

- If trying to use a character that takes several bytes to write in the UTF-8 encoding, the game will only try to read the last byte of the character rather than the entirety of it. This may result in either of the previous errors, but it makes finding the cause much harder. For example, trying to use `§Ā Some text §!`, where Ā has the code of U+0100, will result in the game throwing an error of `Could not find coloring for character id '0'`, and trying to use `§ō Some text §!`, where ō has the code of U+014D, will result in the game throwing an error of `Could not find coloring for character 'M'` (as the character 'M' has the code of U+004D).

Searching can be done using a text editor with the "Find in Files" functionality. **Windows Explorer cannot be used**, as it does not search inside of YAML files. For example, this is how the functionality is accessed in the more common editors to use:

- **Notepad++** – This is located in the "Search" topbar menu as "Find in Files...". By default, no folder is provided. "Follow current doc." allows the text editor to automatically input the currently-opened document's folder as the place for the search, or it can be entered manually. Alternatively, this menu can be opened from the right-click menu of a folder within the "Folder as Workspace" menu – accessed by a button in the topbar – which'll automatically set the folder location to be that folder.
- **Sublime Text** – This is located in the "Find" topbar menu as "Find in Files...". In order to add a folder to search, the menu to the right of the "Where:" line can be opened, with either "Add Folder" (to select an individual folder) or "Add Open Folders" (To automatically select all folders opened via Sublime Text) buttons serving to do so.
- **Visual Studio Code** – Visual Studio Code by default searches only the currently opened folder. A folder is opened either through the "Open Folder..." button in the "File" topbar menu or the "Explorer" menu, accessed through the bar on the left. After this, the functionality can be accessed in the "Edit" menu as "Find in Files". To search in other folders, open the 'search details' menu, represented with an ellipsis, and enter the full path to the folder in the 'Files to include' area. In order to speed up the search, filename filters can be used. For example, `localisation/english/*.yml` within "files to include" will only search every \*.yml file within the <currently opened folder>/localisation/english/ folder, where `*` stands for any amount (including 0) of any characters within the filename. Similar filters can be used in the previous two text editors, however without allowing folders to be filtered — only the filenames.

### Formatting variables

*See also: Variables*

Variables have a unique way for applying colouring, also allowing extra formatting characters. These are applied after a pipe placed at the end of the variable's name, such as `[?my_variable|R]` that will turn the colour of the variable `my_variable` red. If no colouring is applied, it will use the same colour as regular text: the §-colour block, textbox's `text_color_mode`, or the font's default colour in that order.

The list of formatting characters that are restricted to variables only are the following:

- *****
  - Effect: Converts the variable to SI units—appends "K" or "M" and divides the variable appropriately, such as 65 536 becoming 65.53K and 1 500 000 becoming 1.50M. Displays 2 decimals after the dot by default.

- **^**
  - Effect: Same as *.

- **=**
  - Effect:
    ```text
    Prefixes the variable with
    +
    if the value is positive or
    -
    if it is negative.
    ```

- **0..9**
  - Effect: Controls the number of decimals to display. Due to the nature of the game's variables, there are no more than 3 decimals that can be shown. Using any digit greater than 3 will instead have the same result as 3.

- **%**
  - Effect: Converts the variable to percentage, multiplying by 100 and appending a %. By default, will show 2 digits after the decimal point, though the second digit will always be 0.

- **%%**
  - Effect: Appends a percentage to the end of the variable without multiplying by 100.

- **+**
  - Effect: Colours the variable green if positive, yellow if zero, red if negative.

- **-**
  - Effect: Colours the variable red if positive, yellow if zero, green if negative.

Any unrecognised symbols will neither change how the variable is localised nor get recognised as an error in-game. For example, it's common practice in the base game to prepend a dot before the digit used to control the amount of displayed digits as `[?var|.1]`. In case of overlap between mutually-exclusive rules, the last-used one will be prioritised. However, static colouring has a lower priority than dynamic colouring (e.g. `[?var|+Y]` will be treated as `[?var|+]`), and using `%%` will also override `%`.

Some examples of formatting characters in usage:

```text
l_english
loc_key
"Democratic
 
party
 
popularity:
 
[?party_popularity@democracy|%G0]"
 

 
loc_key_2
"Modifier
 
token's
 
value:
 
[?modifier@my_modifier|.1%%+]"

 
pol_power_trigger_tt
"Has
 
more
 
than
 
[?var_name|Y]
 
political
 
power"
```

Within these examples, the first string depicts the current scope's democratic popularity as a percentage multiplied by 100 (%), in green (G), rounded to a whole number with 0 decimals (0). The second string displays the `my_modifier` [modifier token](<Modifiers - Hearts of Iron 4 Wiki.md#modifier-tokens>)'s value as a 'good' number (+ making it green if positive, red if negative), with a percentage sign appended in the end (%%) and rounded to a number with one decimal (.1). The third string displays the variable in yellow colouring (as is common in the base game's tooltips), leaving it unchanged otherwise.

### Country's flags

The following in localisation will display the default, /Hearts of Iron IV/gfx/flags/TAG.tga, flag of a country: `@TAG`  
It's recommended to use the GetFlag namespace when possible instead, however, this can be used on localisation that doesn't support namespaces, such as custom modifier tooltips or the game rules.

### Text icons

Icons can be displayed within strings using the **£** notation.

```text
l_english
example_key
"£GFX_army_experience"
```

Text icons are added as `spriteType = { ... }` definitions in /Hearts of Iron IV/interface/\*.gfx files within an overarching `spriteTypes = { ... }`. An example definition of one looks like:

```text
	spriteType = {
		name = "GFX_my_text_icon"
		texturefile = "gfx/texticons/filename.dds"
		legacy_lazy_load = no
	}
```

The text icon's name is equal to the text icon with the GFX\_ part in the beginning removed, being `£my_text_icon` in this case.

If the sprite of the text icon is made out of multiple frames, then the specified frame can be used in localisation as `£icon_name|1`, this example being the first frame. Note that `legacy_lazy_load = no` is necessary for multi-framed text icons to work properly.

## Nesting strings

The dollar sign special symbol is used for nesting other strings within any given localisation key's value. In particular, there are 4 primary usage cases for it:

- Nesting other localisation keys. For example,  `some_modifier_tooltip:0 "$modifier_production_speed_infrastructure_factor$: §R-10%§!"` will show up in-game as `Infrastructure construction speed: -10%`, assuming that `modifier_production_speed_infrastructure_factor`'s definition is unchanged from the base game.

This is useful with localisation key values that need to be re-used within others, but can be easily changed during the development of the mod, as to not need to adjust every single localisation value that uses it when changing it. This can also be used to expand compatibility with base game updates or other mods that may potentially change the localisation value but should still be compatible with the mod.
When used within `pdx_tooltip` of an interface element, this does not work properly, instead showing up with the dollar signs visible. This can be bypassed using [scripted localisation](#scripted-localisation), as a scripted localisation entry that points towards a key, the value of which contains nested localisation entry, will work as intended.

- Inputting a dollar sign itself. This is done by doubling the dollar sign in localisation, such as  `cost_tooltip: "This option costs $$100"`.
- Nesting a boundable variable. Introduced in patch 1.15, boundable variables allow modders to define custom variables for use in localisation keys, functioning similarly to internal variables. These can be assigned within any effect, trigger block, or on a scripted GUI. For example, by using a loacalisation key like: `my_boundable_tooltip: "My name is $NAME$."`, `$NAME$` in this case would be a custom boundable variable that can be defined elsewhere by the modder. This provides significant flexibility for dynamic localisation that adapts to gameplay conditions. For further details on defining and binding these variables, refer to the [boundable localisation](#boundable-localisation) section.

- Nesting a strictly internal variable. This is particularly common within base game's localisation that corresponds to game mechanics rather than database entries, such as  `confirm_cancel_national_focus_desc:0 "Are you sure you want to cancel the national focus §H$FOCUS_NAME$§!?"`. In these cases, the specified internal variable only exists within the scope of that localisation key and cannot be used anywhere else.

One notable usage of strictly internal variables is in country names, as these offer a variety of internal variables fetching the non-ideology name of the country and the overlord's name in either regular, ADJ, or DEF form, such as `COUNTRY_autonomy_collaboration_government:0 "$OVERLORDADJ$ $NONIDEOLOGY$"`.

## Bindable localisation

**Bindable Localization** was introduced in **patch 1.15**, allowing variables to be dynamically bound to localization keys through scripting.

Previously, variables in localization keys (e.g., `$OVERLOADJ$`) were strictly internal and provided directly by the game, limiting modders' flexibility. For example:

```text
SCIENTIST_ROSTER_SORT_BUTTON_TOOLTIP: "§YClick§! to sort according to $REASON|Y$"
```

Before patch 1.15, `$REASON$` would be internal and unmodifiable. With the introduction of bindable localization, modders can now define their own bound variables, reducing the need for hundreds of similar localization keys that only differ in minor ways. Bindable localisation can only be used within very specific contexts, most of which are documented. However, there are 3 very useful places they can be used on, namely:

- `custom_effect_tooltip`,
- `custom_trigger_tooltip`,
- and to GUI files using the `bound_tooltip` construct.

#### Usage of Bindable Localization

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

Instead of using inline strings, bindable localization can reference other localization keys directly, like [scripted localisation](#scripted-localisation). For example:

```text
custom_effect_tooltip = {
    localization_key = my_bindable_tooltip
    IDEA_NAME = GER_mefo_bills
}
```

In this case, `GER_mefo_bills` is a predefined localization key, and its value will replace `$IDEA_NAME$`.

### Context-Aware Tooltips

**Context-aware tooltips** extend bound localization by allowing tooltips to be localized based on a context provided by the game. They are used strictly on GUI files, like `bound_tooltip`.

They are used with the `context_aware_tooltip` construct. The context is provided directly by the game’s source code and can only be used in specific, documented places.

Additionally, the context is recursive: if a parent object is localized with a context, all child objects will inherit the same context.

### Localization Formatters

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

## Localization Formatters

**character\_name**

The character\_name formatter gets the name of the character.
Example:

```text
custom_effect_tooltip = character_name|hjalmar_schacht
```

**country\_culture**

The country\_culture formatter formats the string using the country's cultural override (TAG\_token) if it exists, otherwise the generic version (token).
Localization Scope Object
The formatter requires the following Localization Scope Objets to be defined:

Country - The country that the idea is associated with.
Example

```text
custom_effect_tooltip = country_culture|generic_tank_organisation
```

**idea\_name**

The idea\_name formatter formats gets the name for the idea.
Localization Scope Object
The formatter requires the following Localization Scope Objects to be defined:

Country - The country that the idea is associated with.
Example

```text
custom_effect_tooltip = idea_name|canadian_pacific_railway
```

**advisor\_desc**

The advisor\_desc formatter gets the description for the advisor.
Localization Scope Object
The formatter requires the following Localization Scope Objets to be defined:

Country - The country that the idea is associated with.
Example

```text
custom_effect_tooltip = advisor_desc|hjalmar_schacht
```

**tech\_effect**

The tech\_effect formatter gets the effect of finishing a technology.
Localization Scope Object
The formatter requires the following Localization Scope Objects to be defined:

Country - The country that the tech is associated with.
Example

```text
custom_effect_tooltip = tech_effect|early_transport_plane
```

**idea\_desc**

The idea\_desc formatter gets the description for the idea.
Localization Scope Object
The formatter requires the following Localization Scope Objects to be defined:

Country - The country that the idea is associated with.
Example

```text
custom_effect_tooltip = idea_desc|canadian_pacific_railway
```

**building\_state\_modifier**

The building\_state\_modifier gets the state modifiers for the provided building template and the provided scope.

The formatter takes special care of the following parameters:

INDENT: The indent to be added to all lines of the state modifier description (including header line).
Example:

```text
custom_effect_tooltip = building_state_modifier|dam
```

## Contextual Localization

Contextual localization is a way to access data from Localization Objects when localizing a string.
The concept differs slightly from standard values ($VAL$) that can be injected into the localization string by allowing the localization string
to select which properties to add to the resulting string and where.
When a string is contextually localized with a localization object, then there's one root object (either a Scope or [Localization Environment(loc\_objects\_documentation.md#localization\_environment)].
In general this object can only be used for two purposes: Accessing other objects and getting the current date.

Some of the localization objects are :

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

### Using a localization object

The localization objects are used with the following syntax: `[(Object.)+Property]`.
`(Object.)+` refers to a sequence of at least one object accessor and `Property` is the property
that is accessed by the last object in the sequence. For example, if the localization string is localized with an Character object
the following queries would get the character's name and the name of the country that the character belongs to `[Character.GetName]`
and `[Character.Owner.GetName]`, respectively.

### Condition in contextual localization

Conditions in contextual localization can be used to check if objects are null or not. The basic syntax for the condition is `[(OBJECT ? TRUE_CASE : FALSE_CASE)]`.
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

### Relation to Event Scopes

When a localization string is localized from a scoped context (for example effects or triggers), then the root [Scope](<Scopes - Hearts of Iron 4 Wiki.md>) is created
from the event scope of that context. For example, an effect that creates a trade route between two countries `FROM` and `THIS`
could be localized with: `LOC_KEY: "Creates a trade route between [FROM.GetName] and [THIS.GetName]"`. For more information on
how the scope accessors `FROM`, `THIS`, `PREV` and `ROOT` works on `Scope` see [Dual Scopes](<Scopes - Hearts of Iron 4 Wiki.md#dual-scopes>)

### Documentation of localized objects

In general a scoped context (for example, effects and triggers) are localized using a [Scope](<Scopes - Hearts of Iron 4 Wiki.md>) object based on the scope of that context.
However, there are legacy systems where this may not hold. For other places where localization keys are provided, please see the documentation
for which localization objects that are defined for that context.

## Namespaces

Namespaces refer to obtaining certain information from some scope to display in localisation. For example, getting the name of a country, the surname of a character, the ID of a state, and etc.  
A namespace is marked with the square brackets on either side as in `my_localisation_key: "[GetDateText]"`. By default, **there is no scope assumed**. A [scope](<Scopes - Hearts of Iron 4 Wiki.md>) can be added, separated from the namespace with a dot, in order to let the game know from whom to obtain information, such as `my_localisation_key: "[QAT.GetRulingParty]"`, which'll result in the ruling party of the country QAT appearing in localisation. Any dual scope that can be used as a target may be used in localisation. [THIS](<Scopes - Hearts of Iron 4 Wiki.md#this>) can be used in order to refer to the scope of where it's used, such as  `effect_tooltip: "[ROOT.GetNameDefCap] declares war on [THIS.GetNameDef]"`.

Variables and event targets can be used within namespaces as well. For example, this grants the name of the capital state of OMA using the 'capital' variable:  `my_localisation_key: "[OMA.capital.GetName]"`. A list of built-in variables that can be used can be seen in [the respective wiki page](<Data structures - Hearts of Iron 4 Wiki.md#game-variables>). Another common ones to use include 'owner' and 'controller' for states, such as `my_localisation_key: "Owner of South-West England: [123.owner.GetName]"`.

**Characters only exist within the scope of the country where they're recruited**, in versions prior to 1.12.8. What this means is that before scoping into the character, one must first scope into the country that they are assigned to, such as  `current_name_of_fdr:0 "[USA.USA_franklin_delano_roosevelt.GetFullName]"`. If the character is marked with some other token (such as THIS or ROOT), this is unnecessary, but it is necessary for direct character IDs. Characters also support scoping to the `GetLeader` localisation function beforehand, such as `leader_pronoun: "[ROOT.GetLeader.GetHeShe]"` In this case, scoping into the country is still necessary.

Note that namespaces cannot be used everywhere. In the majority of the user interface, such as the names for wars or countries, they will not work properly, instead appearing exactly as in localisation, with the square brackets still visible. A list of locations where namespaces *do* work is:

- **Focuses**
  - Notes:
    ```text
    Requires
    dynamic = yes
    within the focus to work correctly for the title, otherwise it generates a value at the game's start and it remains unchanging until the next reload (either of the savefile or the focus tree). Not required for the description, which always dynamically refreshes localisation.
    ```

- **Ideas and**
  - Notes: Support for dynamic modifiers was added in 1.13.

- **Decisions**

- **Events**
  - Notes:
    ```text
    At times it may be better to use
    completely different localisation keys within events
    instead of using scripted localisation.
    ```

- **Custom effect/trigger tooltips**
  - Notes:
    ```text
    Despite the fact that it works for
    effects
    and
    triggers
    , custom
    modifier
    tooltips do not support scripted localisation.
    ```

- **Boolean flags**
  - Notes:
    ```text
    The names of the boolean flags, appearing in the tooltip when checked for them with triggers such as
    has_country_flag = flag_name
    or
    has_character_flag = flag_name
    ```

- **Operations**

- **Adjacency rule tooltips**
  - Notes: Referring to the tooltip that appears when hovering over a strait that's disabled for this country.

- **Custom interface elements**
  - Notes:
    ```text
    The container with the UI element must be attached to a
    scripted GUI
    that has a valid
    context_type
    within the corresponding
    /Hearts of Iron IV/common/scripted_guis/*.txt
    file. May require a game restart for it to apply.
    ```

The list may be incomplete, so something not being mentioned does not necessitate that localisation does not work there, but that does make it unlikely. Other localisation functions, not involving square brackets, do still work in this case, however.

### Functions

Sometimes, the result of a function may be interpreted as a localisation key itself, but only if the string consists entirely out of that function. For example, `log = "[THIS.GetTag]"` will result in the non-ideology name being logged instead if one exists, since that localisation key consists only of the country tag. However, `log = "loc_key_[ALB.GetTag]"` will log `loc_key_ALB`, even if a localisation key exists with that name.

#### Country scope

- **GetName**
  - Example: [GER.GetName]
  - Description: Gets the name of the country, the name of the state, or the name of the character. For aces, only gets the first name: see GetFullName.

- **GetTag**
  - Example: [GER.GetTag]
  - Description:
    ```text
    Puts the tag of the country into localisation. Particularly useful for
    Meta effects
    .
    ```

- **GetLeader**
  - Example: [POL.GetLeader]
  - Description:
    ```text
    Gets the name of the leader of the country. Can be further scoped into the pronoun-related namespaces, such as
    [THIS.GetLeader.GetSheHe]
    .
    ```

- **GetManpower**
  - Example: [ENG.GetManpower]
  - Description: Gets the total population of the country, including civilians.

- **GetFactionName**
  - Example: [SOV.GetFactionName]
  - Description: Gets the name of the faction that the country is located in.

- **GetAgency**
  - Example: [FRA.GetAgency]
  - Description: Gets the name of the country's intelligence agency.

- **GetFlag**
  - Example: [GER.GetFlag]
  - Description: Gets the current flag of the country.

- **GetNameWithFlag**
  - Example: [ITA.GetNameWithFlag]
  - Description: Gets the current flag of the country and adds the name afterwards.

- **GetNameDef**
  - Example: [SPR.GetNameDef]
  - Description: Gets the DEF name of the country, primarily used to tell if "the" is needed to be put in the beginning.

- **GetNameDefCap**
  - Example: [POR.GetNameDefCap]
  - Description: Gets the DEF name of the country, primarily used to tell if "The" is needed to be put in the beginning, capitalising the first letter as well.

- **GetAdjective**
  - Example: [YUG.GetAdjective]
  - Description:
    ```text
    Gets the adjective for the country, such as
    British
    .
    ```

- **GetAdjectiveCap**
  - Example: [CAN.GetAdjectiveCap]
  - Description: Gets the adjective for the country, capitalising the first letter.

- **GetOldName**
  - Example: [RAJ.GetOldName]
  - Description: Gets the name of the country without any cosmetic tags applied.

- **GetOldNameDef**
  - Example: [MAL.GetOldNameDef]
  - Description: Gets the DEF name of the country, primarily used to tell if "the" is needed to be put in the beginning, without any cosmetic tags applied.

- **GetOldNameDefCap**
  - Example: [AST.GetOldNameDefCap]
  - Description: Gets the DEF name of the country, primarily used to tell if "The" is needed to be put in the beginning, without any cosmetic tags applied, capitalising the first letter.

- **GetOldAdjective**
  - Example: [NZL.GetOldAdjective]
  - Description: Gets the adjective for the country without any cosmetic tags applied.

- **GetOldAdjectiveCap**
  - Example: [HAW.GetOldAdjectiveCap]
  - Description: Gets the adjective for the country without any cosmetic tags applied, capitalising the first letter.

- **GetNonIdeologyName**
  - Example: [JAP.GetNonIdeologyName]
  - Description:
    ```text
    Gets the non-ideology name of the country, defined with
    TAG:0 "Country name"
    ```

- **GetNonIdeologyNameDef**
  - Example: [SAU.GetNonIdeologyNameDef]
  - Description: Gets the non-ideology DEF name of the country, primarily used to tell if "the" is needed to be put in the beginning.

- **GetNonIdeologyNameDefCap**
  - Example: [SWE.GetNonIdeologyNameDefCap]
  - Description: Gets the non-ideology DEF name of the country, primarily used to tell if "The" is needed to be put in the beginning, capitalising the first letter.

- **GetNonIdeologyAdjective**
  - Example: [DEN.GetNonIdeologyAdjective]
  - Description: Gets the non-ideology adjective for the country.

- **GetNonIdeologyAdjectiveCap**
  - Example: [NOR.GetNonIdeologyAdjectiveCap]
  - Description: Gets the non-ideology adjective for the country, capitalising the first letter.

- **GetPartySupport**
  - Example: [ICE.GetPartySupport]
  - Description: Gets the percentage of the ruling party, on the scale from 0 to 100. Does not have the % symbol in the end.

- **GetLastElection**
  - Example: [ROOT.GetLastElection]
  - Description: Gets the date when the last country's election occurred in the "HH:00, DD Month, YYYY" format, such as "01:00, 1 January, 1936".

- **GetRulingParty**
  - Example: [HOL.GetRulingParty]
  - Description: Gets the short name of the party ruling over the country.

- **GetRulingPartyLong**
  - Example: [BEL.GetRulingPartyLong]
  - Description: Gets the long name of the party ruling over the country.

- **GetRulingIdeology**
  - Example: [LUX.GetRulingIdeology]
  - Description: Gets the name of the country's ideology group, in adjective form.

- **GetRulingIdeologyNoun**
  - Example: [GER.GetRulingIdeologyNoun]
  - Description: Gets the name of the country's ideology group, in noun form.

- **GetCommunistParty**
  - Example: [HUN.GetCommunistParty]
  - Description:
    ```text
    Gets the name of the
    Communist
    party.
    ```

- **GetDemocraticParty**
  - Example: [AUS.GetDemocraticParty]
  - Description:
    ```text
    Gets the name of the
    Democratic
    party.
    ```

- **GetFascistParty**
  - Example: [CZE.GetFascistParty]
  - Description:
    ```text
    Gets the name of the
    Fascist
    party.
    ```

- **GetNeutralParty**
  - Example: [ROM.GetNeutralParty]
  - Description:
    ```text
    Gets the name of the
    Non-aligned
    party.
    ```

- **GetCommunistLeader**
  - Example: [BUL.GetCommunistLeader]
  - Description:
    ```text
    Gets the name of the leader of the country's
    Communist
    party.
    ```

- **GetDemocraticLeader**
  - Example: [GRE.GetDemocraticLeader]
  - Description:
    ```text
    Gets the name of the leader of the country's
    Democratic
    party.
    ```

- **GetFascistLeader**
  - Example: [ALB.GetFascistLeader]
  - Description:
    ```text
    Gets the name of the leader of the country's
    Fascist
    party.
    ```

- **GetNeutralLeader**
  - Example: [TUR.GetNeutralLeader]
  - Description:
    ```text
    Gets the name of the leader of the country's
    Non-aligned
    party.
    ```

- **GetPowerBalanceName**
  - Example: [ITA.GetPowerBalanceName]
  - Description:
    ```text
    Gets the name of the country's currently-active
    balance of power
    .
    ```

- **GetPowerBalanceModDesc**
  - Example: [ITA.GetPowerBalanceModDesc]
  - Description:
    ```text
    Gets the names of the country's currently-active
    balance of power modifiers
    and their effects towards the BoP. For the modifiers applied by the active range, see
    GetActiveRangeModDesc
    .
    ```

- **GetRightSideName**
  - Example: [ITA.GetRightSideName]
  - Description: Gets the name of the country's right side in the currently-active balance of power.

- **GetLeftSideName**
  - Example: [ITA.GetLeftSideName]
  - Description: Gets the name of the country's left side in the currently-active balance of power.

- **GetActiveSideName**
  - Example: [ITA.GetActiveSideName]
  - Description: Gets the name of the side in the country's currently-active balance of power that has more power.

- **GetTrendingSideName**
  - Example: [ITA.GetTrendingSideName]
  - Description: Gets the name of the side in the country's currently-active balance of power that the balance is changing towards.

- **GetActiveRangeName**
  - Example: [ITA.GetActiveRangeName]
  - Description: Gets the name of the range in the country's currently-active balance of power that is currently active, granting its modifiers.

- **GetActiveRangeModDesc**
  - Example: [ITA.GetActiveRangeModDesc]
  - Description:
    ```text
    Gets the modifiers applied by the active range in the country's currently-active balance of power. Uses the
    BOP_RANGE_MODIFIER
    localisation key.
    ```

- **GetActiveRangeRuleDesc**
  - Example: [ITA.GetActiveRangeRuleDesc]
  - Description:
    ```text
    Gets the game rules modified by the active range in the country's currently-active balance of power. Uses the
    BOP_RANGE_RULE
    localisation key.
    ```

- **GetActiveRangeActivationEffect**
  - Example: [ITA.GetActiveRangeActivationEffect]
  - Description:
    ```text
    Gets the tooltip for the effects executed when entering the active range in the country's currently-active balance of power. Uses the
    BOP_RANGE_ACTIVATION_EFFECT
    localisation key.
    ```

- **GetActiveRangeDeactivationEffect**
  - Example: [ITA.GetActiveRangeDeactivationEffect]
  - Description:
    ```text
    Gets the tooltip for the effects executed when exiting the active range in the country's currently-active balance of power. Uses the
    BOP_RANGE_DEACTIVATION_EFFECT
    localisation key.
    ```

- **GetChangeRateDesc**
  - Example: [ITA.GetChangeRateDesc]
  - Description:
    ```text
    Gets the rate by which the balance of power is changed weekly and/or daily and towards which side. May use
    BOP_CHANGE_RATE_DAILY
    or
    BOP_CHANGE_RATE_WEEKLY
    localisation keys depending on the current BoP modifiers, prioritising the former if possible.
    ```

- **GetBopTrendTextIcon**
  - Example: [ITA.GetBopTrendTextIcon]
  - Description:
    ```text
    Selects the text icon corresponding towards which side is getting power. May select either
    GFX_BoP_left_texticon
    ,
    GFX_BoP_right_texticon
    , or nothing.
    ```

#### Other scopes

Date variable in this case refers to a variable set to a date value. Using it with the current date can be done by using the global.date variable as `[?global.date.GetDateString]`.

- **GetName**
  - Scope: State, character, operative, ace
  - Example:
    ```text
    [123.GetName]
    [POL.POL_character.GetName]
    ```
  - Description:
    ```text
    Gets the name of the state or the name of the character. For aces, only gets the first name: see
    GetFullName
    .
    ```

- **GetName**
  - Scope: MIO
  - Example:
    ```text
    [?ID.GetName]
    [?BEL_cockerill_organization.GetName]
    ```
  - Description: Gets the name of the MIO.

- **GetDateText**
  - Scope: Any
  - Example: [GetDateText]
  - Description: Gets the date in the format of "HH:00, DD Month, YYYY", such as "12:00, 1 January, 1936".

- **GetDate**
  - Scope: Any
  - Example: [GetDate]
  - Description: Gets the date in the format of YYYY.MM.DD.HH, such as 1936.1.1.12.

- **GetMonth**
  - Scope: Any
  - Example: [GetMonth]
  - Description: Gets the current month.

- **GetYear**
  - Scope: Any
  - Example: [GetYear]
  - Description: Gets the current year.

- **GetID**
  - Scope: State
  - Example: [123.GetID]
  - Description:
    ```text
    Gets the ID of the state. Particularly useful for
    Meta effects
    .
    ```

- **GetCapitalVictoryPointName**
  - Scope: State
  - Example: [540.GetCapitalVictoryPointName]
  - Description: Gets the name of the capital victory point (i.e. the province with the largest amount of victory points) of the state.

- **GetSheHe**
  - Scope: Character
  - Example: [PRU.GetLeader.GetSheHe]
  - Description: Results in either "she" or "he" depending on the gender of the character, beginning with lowercase letters.

- **GetSheHeCap**
  - Scope: Character
  - Example: [MEX.MEX_character.GetSheHeCap]
  - Description: Results in either "She" or "He" depending on the gender of the character, beginning with uppercase letters.

- **GetHerHim**
  - Scope: Character
  - Example: [BRA.BRA_character.GetHerHim]
  - Description: Results in either "her" or "him" depending on the gender of the character, beginning with lowercase letters.

- **GetHerHimCap**
  - Scope: Character
  - Example: [ARG.ARG_character.GetHerHimCap]
  - Description: Results in either "Her" or "Him" depending on the gender of the character, beginning with uppercase letters.

- **GetHerHis**
  - Scope: Character
  - Example: [CHI.CHI_character.GetHerHis]
  - Description: Results in either "her" or "his" depending on the gender of the character, beginning with lowercase letters.

- **GetHerHisCap**
  - Scope: Character
  - Example: [CHL.CHL_character.GetHerHisCap]
  - Description: Results in either "Her" or "His" depending on the gender of the character, beginning with uppercase letters.

- **GetHersHis**
  - Scope: Character
  - Example: [PRC.PRC_character.GetHersHis]
  - Description: Results in either "hers" or "his" depending on the gender of the character, beginning with lowercase letters.

- **GetHersHisCap**
  - Scope: Character
  - Example: [YUN.YUN_character.GetHersHisCap]
  - Description: Results in either "Hers" or "His" depending on the gender of the character, beginning with uppercase letters.

- **GetHerselfHimself**
  - Scope: Character
  - Example: [GXC.GXC_character.GetHerselfHimself]
  - Description: Results in either "herself" or "himself" depending on the gender of the character, beginning with lowercase letters.

- **GetHerselfHimselfCap**
  - Scope: Character
  - Example: [XSM.XSM_character.GetHerselfHimselfCap]
  - Description: Results in either "Herself" or "Himself" depending on the gender of the character, beginning with uppercase letters.

- **GetIdeology**
  - Scope: Country leader
  - Example: [?country_leader.GetIdeology]
  - Description:
    ```text
    Gets the ideology
    group
    assigned to the country leader, such as
    Democratic
    or
    Non-aligned
    .
    ```

- **GetIdeologyGroup**
  - Scope: Country leader
  - Example: [?country_leader.GetIdeologyGroup]
  - Description:
    ```text
    Gets the ideology
    type
    assigned to the country leader, such as Liberalism or Centrism. The name is misleading.
    ```

- **GetRank**
  - Scope: Unit leader
  - Example: [MEN.MEN_character.GetRank]
  - Description: Gets the rank of the unit leader, such as Corps Commander or Field Marshal.

- **GetCodeName**
  - Scope: Operative
  - Example: [THIS.GetCodeName]
  - Description: Gets the codename of the operative.

- **GetCallsign**
  - Scope: Operative
  - Example: [THIS.GetCallsign]
  - Description: Gets the callsign of the operative.

- **GetSurname**
  - Scope: Ace
  - Example: [LIB.GetLeader.GetSurname]
  - Description: Gets the last name of the ace.

- **GetFullName**
  - Scope: Ace
  - Example: [ECU.ECU_character.GetFullName]
  - Description: Gets the full name of the ace, with both first and last names.

- **GetWing**
  - Scope: Ace
  - Example: [THIS.GetWing]
  - Description: Gets the wing that the ace is assigned to.

- **GetWingShort**
  - Scope: Ace
  - Example: [THIS.GetWingShort]
  - Description: Gets the shortened name of the wing that the ace is assigned to.

- **GetAceType**
  - Scope: Ace
  - Example: [THIS.GetAceType]
  - Description: Gets the type of the ace.

- **GetMissionRegion**
  - Scope: Ace
  - Example: [THIS.GetMissionRegion]
  - Description: Gets the region that the ace is assigned to.

- **GetTokenKey**
  - Scope:
    ```text
    Any
    token variable
    ```
  - Example: [?global.variablename.GetTokenKey]
  - Description:
    ```text
    Gets the token of the variable, such as infantry_equipment, instead of the internal ID. Particularly useful for
    Meta effects
    .
    ```

- **GetTokenLocalizedKey**
  - Scope:
    ```text
    Any
    token variable
    ```
  - Example: [?GER.variablename.GetTokenLocalizedKey]
  - Description:
    ```text
    Returns the
    localised
    name of the variable, such as "Infantry Equipment", by converting an internal identifier or database object, such as
    infantry_equipment
    into its localised equivalent, provided a localization key exists for it.
    This functionality becomes invaluable for advanced abstraction techniques. For instance, it can approximate arbitrary string interpolation (string interpolaration is the ability to embed expressions or variables within a string literal in a programming language) in
    Meta effects
    by applying it to token variables that reference dummy objects (e.g., empty ideas) with predefined arbitrary localization strings. By passing token variables that resolve to localized dummy objects, developers can achieve a level of flexibility similar to direct string manipulation.
    Additionally, concatenating the localization values of two dummy tokens can produce a new token string. This string can then be inserted into a token variable within a Meta effect, provided the resulting token string corresponds to a valid existing token. If the resulting token is invalid, the function will simply return an integer value of 0.
    Effectively, this approach allows for the derivation of previously-unknown token variables from known ones, following a template defined by another known token variable. This is particularly useful when the destination token follows a templated variation (via prefixes or suffixes) of the source token.
    ```

- **GetDateString**
  - Scope: Date variable
  - Example: [?global.date.GetDateString]
  - Description: Gets the date in the format of "HH:00, DD Month, YYYY", such as "12:00, 1 January, 1936".

- **GetDateStringShortMonth**
  - Scope: Date variable
  - Example: [?global.date.GetDateStringShortMonth]
  - Description: Gets the date in the format of "HH:00, DD Mon., YYYY", such as "12:00, 1 Jan., 1936".

- **GetDateStringNoHour**
  - Scope: Date variable
  - Example: [?global.date.GetDateStringNoHour]
  - Description: Gets the date in the format of YYYY.MM.DD, such as 1936.1.1.

- **GetDateStringNoHourLong**
  - Scope: Date variable
  - Example: [?global.date.GetDateStringNoHourLong]
  - Description: Gets the date in the format of "DD Month, YYYY", such as "1 January, 1936".

## Scripted localisation

Scripted localisation is similar to creating your own namespaces. It is defined in /Hearts of Iron IV/common/scripted\_localisation/\*.txt and used in localisation in a similar manner to namespaces. However, unlike namespaces, by default the current scope is assumed when using scripted localisation, making scoping optional.
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
  - `trigger = { ... }` is the trigger block evaluated for the checked scope, using this scripted localisation if true. Temporary variables set in this trigger block will remain set when displaying the localisation key, allowing math to be done between different variables or using scripted localisation recursively (such as to display every element of an array).
  - `localization_key = my_loc_key` (Note the American spelling with Z rather than the British spelling with S used elsewhere) assigns the localisation key to be used with this scripted localisation option.

The example above will show the FRA\_localization\_key localisation key for France and the mod\_localization\_key one otherwise as a backup. The first localization key that meets the triggers will be used. In localisation, that example can be used as

```text
l_english
some_localisation
"[mod_scripted_loc]"

 
FRA_localization_key
"France-exclusive
 
localisation"

 
mod_localization_key
"Generic
 
localisation"
```

Scripted localisation also allows randomisation of the localisation key that would be chosen, using [random\_list](<Effect - Hearts of Iron 4 Wiki.md#random-list>). For example, the following code will give a 60% and a 40% chance respectively for mod\_localization\_key\_1 or mod\_localization\_key\_2 to be chosen when this scripted localisation entry is used:

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

### Dynamic Scripted Localisation

The `localization_key` argument now directly supports the use of dynamic localisation. That is, it is possible put a piece of dynamic localisation *as part* of a localisation key call. This allows for a much streamlined system of localisation automation when it is needed. For example:

```text
defined_text = {
    name = mod_scripted_loc
    text = {
        localization_key = "mod_localization_version_[?my_variable]"
    }
}
```

When the scripted localisation is called, it will read the value of `my_variable` and place the value into the string of the localisation key as specified and evaluate the entire localisation key as a whole after the variable has been implemented.

```text
l_english
some_localisation
"[mod_scripted_loc]"

 
mod_localization_version_1
"This
 
localization
 
will
 
be
 
called
 
when
 
my_variable
 
is
 
equal
 
to
 
1."

 
mod_localization_version_2
"This
 
localization
 
will
 
be
 
called
 
when
 
my_variable
 
is
 
equal
 
to
 
2."

 
mod_localization_version_3
"This
 
localization
 
will
 
be
 
called
 
when
 
my_variable
 
is
 
equal
 
to
 
3."
```

## References

1. [↑](#cite-ref-1) <https://twitter.com/Martin_Anward/status/1039175213773144066>

**[Modding](<Modding - Hearts of Iron 4 Wiki.md>)**
