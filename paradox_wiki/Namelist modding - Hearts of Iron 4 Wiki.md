# Table of contents

- [Divisions Names](#divisions-names)
- [Naval Names](#naval-names)
- [Generic Names](#generic-names)
- [Operative codenames](#operative-codenames)


---

Units, both land and naval, obtain their names from either a set list of names.

## Divisions Names

Division names are defined in /Hearts of Iron IV/common/units/names\_divisions in country specific text files. The name of the file does not matter, though generally follow the following format *TAG\_names\_divisions.txt*.

Once in the file, you want to start off with the name list set in your OOB found in /Hearts of Iron IV/history/units, for example NEP\_MTN\_01. You will want to follow the following formatting:

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

## Naval Names

Naval names are defined in /Hearts of Iron IV/common/units/names\_ships in country specific text files. The name of the file does not matter, though generally follow the following format *TAG\_ship\_names.txt*.

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

## Generic Names

Defined in /Hearts of Iron IV/common/units/names/\*.txt, for countries that lack specific names for types of equipment, especially for custom equipment that not every nation will use.

```text
generic = { # Makes it apply to all countries
	submarine = { # Name of the equipment
		prefix = "" # The name that comes before equipment
		generic = { "Submarine" } # Sets the equipments name
		unique = {  } # For generic equipment, do not put anything here
	}
}
```

## Operative codenames

Stored in /Hearts of Iron IV/common/units/codenames\_operatives, these codenames will be randomly assigned to operatives of the specified countries. An example definition looks like:

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

**[Modding](<Modding - Hearts of Iron 4 Wiki.md>)**
