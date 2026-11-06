# Namelist modding

Units, both land and naval, obtain their names from either a set list of names.

## Divisions Names

Division names are defined in `/Hearts of Iron IV/common/units/names_divisions` in country specific text files. The name of the file does not matter, though generally follow the following format *TAG_names_divisions.txt*.

Once in the file, you want to start off with the name list set in your OOB found in `/Hearts of Iron IV/history/units`, for example NEP_MTN_01. You will want to follow the following formatting:

```text
NEP_MTN_01 = { # DIVISIONS_NAME_GROUP, set in your units folder
	name = "Mountain Divisions" # The name you want for your name list, can either be a string or in quotes.
	for_countries = { NEP } # Sets what countries can use this name list, change NEP to your countries tag
	can_use = { always = yes } # A country scope trigger that can lock or unlock a division name group given certain triggers
	division_types = { "mountaineers" } # Sets what types of units can use this name list, replace mountaineers with whatever type of unit you are using
	fallback_name = "%d Nepali Dibhijana" # This will be used if you run out of numbered divisions. Always use either %d for decimal numbers or %s for Roman numerals but you can change the rest
	link_numbering_with = { NEP_INF_01 } # Alternative to fallback name, if you run out of numbers in this group you can use another list after it.
	ordered = {
		1 = { "%d Nepali Dibhijana" } # The first division.
		2 = { "%d Nepali Dibhijana" } # Numbers must always start from 1 and go up
		4 = { "%d Nepali Dibhijana" } # The numbers do not need to be sequential
	}
}
```

Namelist files seem to have a limit of ~1500 lines. Any namelists beyond that limit may not work correctly, or not appear entirely.

The vanilla file `common/units/names_divisions/NEP_names_divisions.txt` opens with a comment that defines the keys. In short: the group id is a made-up tag; `for_countries` lists the countries that can use it, and an empty list or a missing key means every country; `can_use` is a country-scope trigger; `division_types` is a hint for automatic choice (the template must have at least one of the listed types); `fallback_name` is used when the numbered names run out, and leaving it out falls back to the old naming; `ordered` numbers start at 1, must not repeat inside one group, and a later file that scripts the same number overrides it; the name must contain `%d` (decimal) or `%s` (Roman numerals); an optional second string is a description shown in the tooltip, and an optional third string is a URL that does not work yet.

- Key census over the 1025 vanilla groups: `name`, `for_countries` and `division_types` in all, `can_use` in 1024, `fallback_name` on 1027 lines, `ordered` in 1019 and `link_numbering_with` in 385.
- The header also documents `unordered` (names without a number). No vanilla group uses it, and no vanilla `ordered` line uses the second string.
- `division_types` tokens in vanilla: `"infantry"` (272 groups), `"cavalry"`, `"motorized"`, `"mechanized"`, `"mountaineers"`, `"paratrooper"`, `"marine"`, `"ranger_battalion"`, `"militia"`, `"bicycle_battalion"`, and a list of armor types (`"light_armor"` `"medium_armor"` ...).
- The group id is what a division template names: `division_names_group = GER_Inf_01` (788 uses in `history/units/`). It is also valid inside `division_template` effects and in AI templates.
- `link_numbering_with = { GER_Inf_01 }` makes the group draw numbers from another group, so two groups never hand out the same number. The page calls it an alternative to the fallback name; the vanilla header describes it as a number reservation system tied to another group and does not call it a fallback.

The page says namelist files seem to be limited to about 1500 lines. Vanilla has larger files: `common/units/names_divisions/SOV_names_divisions.txt` has 1905 lines, `GER_names_divisions.txt` 1590, and `common/units/names_ships/GER_ship_name.txt` 3688. A limit of 1500 lines per file is not shown by the base game.

## Naval Names

Naval names are defined in `/Hearts of Iron IV/common/units/names_ships` in country specific text files. The name of the file does not matter, though generally follow the following format *TAG_ship_names.txt*.

In this file, it does not rely upon a set name within your OOB file like in division names, instead it is any ship. You will want to follow the following formatting:

```text
PAK_DD_HISTORICAL = { # Any name you want
	name = NAME_THEME_HISTORICAL_DESTROYERS # The name you want to appear in the naval designer, can either be a string or in quotes.
	for_countries = { PAK } # Sets what countries can use this name list, change PAK to your countries tag
	type = ship # Do not change
	ship_types = { ship_hull_light destroyer } # First one is MTG technology, second is non-MTG technology. Set it to the technology you are using
	prefix = "PNS " # The name that comes before your ships
	fallback_Name = "Destroyer %d" # This will be used if you run out of numbered divisions. Always use either %d for decimal numbers or %s for Roman numerals but you can change the rest
	unique = {
		"Shamsher" "Tippu Sultan" "Tariq" # List all of the custom ship names they could use, do not use commas
	}
}
```

The example spells the fallback key `fallback_Name`. Vanilla writes `fallback_name` in lower case on all 1692 lines that use it (comments included) over divisions and ships; write it in lower case. No vanilla file writes `fallback_Name` (0 of 1692). Whether the engine also accepts `fallback_Name` is untested. (unverified)

Key census over the 620 vanilla ship groups: `name`, `for_countries` and `type = ship` in all; `unique` in 574, `fallback_name` in 530, `ship_types` in 521, `prefix` in 498, `can_use` in 141, `ordered` in 46 and `link_numbering_with` in 8. So ship groups can use `can_use` and `ordered` as division groups do. `name` is a localisation key (`NAME_THEME_HISTORICAL_DESTROYERS`).

`ship_types` lists a hull token followed by the older type token. The pairs in vanilla are `{ ship_hull_light destroyer }` (76 groups), `{ ship_hull_carrier carrier }` (70), `{ ship_hull_cruiser light_cruiser }` (69), `{ ship_hull_submarine submarine }` (68), `{ ship_hull_cruiser heavy_cruiser }` (66), `{ ship_hull_heavy battleship }` (66) and `{ ship_hull_heavy battle_cruiser }` (65). A few groups list one token or three. Which of the two tokens belongs to Man the Guns technology is the wiki's claim and is untested. (unverified) `common/units/names_ships/ARG_ship_names.txt`

A group id such as `USA_CV_HISTORICAL` is what `create_equipment_variant` takes as `name_group`; it is optional and a variant inherits its parent's group when it is left out.

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

Vanilla group with the name list shortened.

## Generic Names

Defined in `/Hearts of Iron IV/common/units/names/*.txt`, for countries that lack specific names for types of equipment, especially for custom equipment that not every nation will use.

```text
generic = { # Makes it apply to all countries
	submarine = { # Name of the equipment
		prefix = "" # The name that comes before equipment
		generic = { "Submarine" } # Sets the equipments name
		unique = {  } # For generic equipment, do not put anything here
	}
}
```

The real layout of `common/units/names/`. It holds 8 files: `00_names.txt` (the `generic` block and 55 country tags) and one file each for ENG, FRA, GER, ITA, JAP, SOV and USA. The vanilla header says names are based on equipment types, choosing the type with the largest amount in the pool, and `generic` is used for countries that are not scripted.

- The second level is a unit or equipment type key. Ship keys: `submarine`, `destroyer`, `light_cruiser`, `heavy_cruiser`, `battle_cruiser`, `battleship`, `SH_battleship`, `carrier`. Land keys: `infantry`, `cavalry`, `light_armor`, `medium_armor`, `heavy_armor`, `motorized`, `mechanized`, `mountaineers`, `marine`, `paratrooper`, `militia`, `artillery_brigade`, `engineer` and others. Air keys end in `_airframe` or `_equipment` (`small_plane_airframe`, `jet_fighter_equipment`). There is also `codename` for operatives.
- Each entry sets `prefix`, `generic` and `unique` (772 entries). 344 also set `generic_pattern`, a localisation key whose text uses `$NR$` and `$NAME$` (`UNIT_GENERIC_NAME_GENERIC_INFANTRY` is `"$NR$. $NAME$"`; `OPERATIVE_GENERIC_CODENAME_PATTERN` is `"Agent $NR$"`).
- Country blocks also set `air_wing_names_template` (28 uses) and `fleet_names_template` (3), each a localisation key such as `AIR_WING_NAME_ENG_FALLBACK`.
- In the `generic` block every `unique` list is empty, as the page says, except the `codename` entry (`unique = { "Agent 007" }`).

## Operative codenames

Stored in `/Hearts of Iron IV/common/units/codenames_operatives`, these codenames will be randomly assigned to operatives of the specified countries. An example definition looks like:

```text
codename_list_id = {				# ID of the namelist
	name = codename_list_name		# Name of the namelist, can match ID

	for_countries = { TAG1 TAG2 }	# Countries using it

	type = codename					# To notify to the game that it's a codename list

	fallback_name = "Agent %d"		# In case uniques run out.

	unique = {						# Unique codenames, only 1 operative at a time can use them
		"Codename 1"
		"Codename 2"
	}
}
```

`codename_list_id` in the example is only a placeholder for the id of the list; it is not a key. Real ids in vanilla are `SOV_OPERATIVE_CODENAME_HISTORICAL` and `GENERIC_ENG_OPERATIVE_CODENAME_HISTORICAL`.

Vanilla has 14 lists in 14 files (13 country files and `generic_opertive_codenames.txt`; two file names misspell "operative", which does not matter). Each list sets exactly `name`, `for_countries`, `type = codename`, `fallback_name` and `unique`. `name` is a localisation key in the generic file (`NAME_THEME_HISTORICAL_OPERATIVES`) and equals the id in the SOV file. The generic list serves several countries at once: `for_countries = { USA CAN NZL AST RAJ SAF }`.

```text
SOV_OPERATIVE_CODENAME_HISTORICAL = {
	name = SOV_OPERATIVE_CODENAME_HISTORICAL
	for_countries = { SOV }
	type = codename
	fallback_name = "Agent %d"
	unique = { "Perseus" "Farewell" "Vano" }
}
```

Vanilla list with the name list shortened.

The page does not cover `common/names/`. Its only vanilla file, `common/names/00_names.txt`, holds 369 country blocks with the names of aces (pilots) and operation names. The header comments state: surnames can depend on gender; names and surnames are picked at random and a combination never repeats; a callsign is optional and, once used, is never given again; the operation name pools are drawn from until used up.

| Key | Content |
| --- | --- |
| `male = { names = { ... } surnames = { ... } callsigns = { ... } }`, `female = { ... }` | gender specific lists (`male` in all 369 blocks, `female` in 368) |
| `surnames = { ... }`, `callsigns = { ... }` | lists that apply to both genders |
| `prefix = o_operation` | the operation name prefix, as a localisation key; the comment says to treat these as keys, not strings |
| `operation = { 0 = { o_default_operation } }` | pools of operation name keys per strategic region index; `0` is the generic national pool |
| `first = { ... }` / `second = { ... }` | words for a two part operation name (6 blocks); the header says a first and a second part are picked at random after the historical pool |
| `use_geographical_default_operation_names`, `offensive_operation_suffix`, `defensive_operation_suffix`, `naval_operation_suffix` | set once in `default` |

Whether a historically named operation is used up once chosen is controlled by the define `HISTORICAL_ORDER_NAME_EXHAUSTION`, which is `false` in 1.19.4.1.

The `default` block is the fallback and uses English names. A country block can list names without quotes when they have no spaces (`Adolf Alfred Anton`) and with quotes when they do (`"Abd al-Rahman"`).
