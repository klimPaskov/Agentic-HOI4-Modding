# Namelist modding

*Offline snapshot of the Hearts of Iron IV Wiki page "Namelist modding", captured 2026-09-19.*

## Table of contents

- [Divisions Names](#Divisions_Names)
- [Naval Names](#Naval_Names)
- [Generic Names](#Generic_Names)
- [Operative codenames](#Operative_codenames)

---

Units, both land and naval, obtain their names from either a set list of names.

## Divisions Names <a id="Divisions_Names"></a>

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

Namelist files seem to have a limit of \~1500 lines. Any namelists beyond that limit may not work correctly, or not appear entirely.

## Naval Names <a id="Naval_Names"></a>

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

## Generic Names <a id="Generic_Names"></a>

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

## Operative codenames <a id="Operative_codenames"></a>

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

---

## Navigation

**[Modding](<Modding - Hearts of Iron 4 Wiki.md>)**

- **Documentation**: [Effects](<Effects - Hearts of Iron 4 Wiki.md>) • [Triggers](<Triggers - Hearts of Iron 4 Wiki.md>) • [Defines](<Defines - Hearts of Iron 4 Wiki.md>) • [Modifiers](<Modifiers - Hearts of Iron 4 Wiki.md>) • [List of modifiers](<List of modifiers - Hearts of Iron 4 Wiki.md>) • [Scopes](<Scopes - Hearts of Iron 4 Wiki.md>) • [Localisation](<Localisation - Hearts of Iron 4 Wiki.md>) • [On actions](<On actions - Hearts of Iron 4 Wiki.md>) • [Data structures](<Data structures - Hearts of Iron 4 Wiki.md>) • [Flags](<Data structures - Hearts of Iron 4 Wiki.md#Flags>) • [Event targets](<Data structures - Hearts of Iron 4 Wiki.md#Event_targets>) • [Country tag aliases](<Data structures - Hearts of Iron 4 Wiki.md#Country_tag_aliases>) • [Variables](<Data structures - Hearts of Iron 4 Wiki.md#Variables>) • [Arrays](<Data structures - Hearts of Iron 4 Wiki.md#Arrays>)
- **Scripting**: [Achievements](<Achievement modding - Hearts of Iron 4 Wiki.md>) • [AI](<AI modding - Hearts of Iron 4 Wiki.md>) • [AI focuses](<AI focuses - Hearts of Iron 4 Wiki.md>) • [Autonomous states](<Autonomy state modding - Hearts of Iron 4 Wiki.md>) • [Balances of power](<Balance of power modding - Hearts of Iron 4 Wiki.md>) • [Bookmarks/Scenarios](<Bookmark modding - Hearts of Iron 4 Wiki.md>) • [Game rules](<Bookmark modding - Hearts of Iron 4 Wiki.md#Game_rules>) • [Buildings](<Building modding - Hearts of Iron 4 Wiki.md>) • [Characters and traits](<Character modding - Hearts of Iron 4 Wiki.md>) • [Cosmetic tags](<Cosmetic tag modding - Hearts of Iron 4 Wiki.md>) • [Countries](<Country creation - Hearts of Iron 4 Wiki.md>) • [Divisions](<Division modding - Hearts of Iron 4 Wiki.md>) • [Decisions](<Decision modding - Hearts of Iron 4 Wiki.md>) • [Doctrines](<Doctrine modding - Hearts of Iron 4 Wiki.md>) • [Equipment](<Equipment modding - Hearts of Iron 4 Wiki.md>) • [Events](<Event modding - Hearts of Iron 4 Wiki.md>) • [Factions](<Faction modding - Hearts of Iron 4 Wiki.md>) • [Ideas](<Idea modding - Hearts of Iron 4 Wiki.md>) • [Ideologies](<Ideology modding - Hearts of Iron 4 Wiki.md>) • [Military industrial organizations](<Military industrial organization modding - Hearts of Iron 4 Wiki.md>) • [National focuses](<National focus modding - Hearts of Iron 4 Wiki.md>) • [Resources](<Resources modding - Hearts of Iron 4 Wiki.md>) • [Scripted GUI](<Scripted GUI modding - Hearts of Iron 4 Wiki.md>) • [Technologies and doctrines](<Technology modding - Hearts of Iron 4 Wiki.md>) • [Units](<Unit modding - Hearts of Iron 4 Wiki.md>)
- **Map**: [Map](<Map modding - Hearts of Iron 4 Wiki.md>) • [States](<State modding - Hearts of Iron 4 Wiki.md>) • [Supply areas](<Supply areas modding - Hearts of Iron 4 Wiki.md>) • [Strategic regions](<Strategic region modding - Hearts of Iron 4 Wiki.md>)
- **Graphical**: [Interface](<Interface modding - Hearts of Iron 4 Wiki.md>) • [Graphical assets](<Graphical asset modding - Hearts of Iron 4 Wiki.md>) • [Entities](<Entity modding - Hearts of Iron 4 Wiki.md>) • [Posteffects](<Posteffect modding - Hearts of Iron 4 Wiki.md>) • [Particles](<Particle modding - Hearts of Iron 4 Wiki.md>) • [Fonts](<Font modding - Hearts of Iron 4 Wiki.md>)
- **Cosmetic**: [Portraits](<Portrait modding - Hearts of Iron 4 Wiki.md>) • [Music](<Music modding - Hearts of Iron 4 Wiki.md>) • [Sound](<Sound modding - Hearts of Iron 4 Wiki.md>)
- **Other**: [Console commands](<Console commands - Hearts of Iron 4 Wiki.md>) • [Troubleshooting](<Troubleshooting - Hearts of Iron 4 Wiki.md>) • [Mod structure](<Mod structure - Hearts of Iron 4 Wiki.md>) • [Mods](<Mods - Hearts of Iron 4 Wiki.md>) • [Nudger](<Nudger - Hearts of Iron 4 Wiki.md>)
