# Naval and Air Orders of Battle

Read this when writing or auditing fleets, task forces, ships, air wings, carrier wings, aces, ship name lists, or the DLC splits for navy and air.
Primary sources: `paradox_wiki/Division modding - Hearts of Iron 4 Wiki.md` (Adding Air Wings, Adding Navies, List of Units), `paradox_wiki/Country creation - Hearts of Iron 4 Wiki.md` (Order of battle, Variants), `paradox_wiki/Namelist modding - Hearts of Iron 4 Wiki.md` (Naval Names), installed `documentation/effects_documentation.md` (`create_ship`, `create_equipment_variant`, `set_naval_oob`, `set_air_oob`, `transfer_ship`, `transfer_navy`, `destroy_ships`, `add_equipment_production`), and the vanilla files named below under the installed game's ``.

## The DLC split

- Man the Guns (MTG) changes ships to hull-plus-module equipment; By Blood Alone (BBA) changes aircraft to airframes with variants. Orders of battle written for one system are not compatible with the other (wiki: Order of battle).
- Vanilla keeps one file per system and chooses by `has_dlc` in the country history file. Names are arbitrary as long as the registering call matches; vanilla examples: `history/units/GER_1936_naval_mtg.txt`, `ENG_1936_Naval.txt` (MTG) versus `ENG_1936_Naval_Legacy.txt`, `ENG_1936_air_bba.txt` versus `ENG_1936_air_legacy.txt`.
- Registration (see `history/countries/ARG - Argentina.txt`):

```text
if = {
	limit = { has_dlc = "Man the Guns" }
	set_naval_oob = "TAG_1936_naval_mtg"
}
if = {
	limit = { NOT = { has_dlc = "Man the Guns" } }
	set_naval_oob = "TAG_1936_naval_legacy"
}
if = {
	limit = { has_dlc = "By Blood Alone" }
	set_air_oob = "TAG_1936_air_bba"
}
if = {
	limit = { NOT = { has_dlc = "By Blood Alone" } }
	set_air_oob = "TAG_1936_air_legacy"
}
```

- A mod that supports both systems needs both variants of every naval and air file, plus the matching `create_equipment_variant` blocks and starting technology for each system. Mod-added equipment must exist for both systems or be gated by the same `has_dlc` checks.

## Fleets, task forces and ships

Skeleton (wiki Adding Navies; vanilla `history/units/GER_1936_naval_mtg.txt`, which writes each ship on one line):

```text
units = {
	fleet = {
		name = "Example Fleet"
		naval_base = 241
		task_force = {
			name = "Example Task Force"
			location = 241
			ship = {
				name = "Example Ship"
				pride_of_the_fleet = yes
				definition = heavy_cruiser
				start_experience_factor = 0.3
				equipment = {
					ship_hull_cruiser_panzerschiff = {
						amount = 1
						owner = TAG
						version_name = "Example Class"
					}
				}
			}
		}
	}
}
```

- `naval_base` and `location` are province ids of a port. Vanilla uses the port province (for example 241 Wilhelmshaven).
- `definition` selects the ship category. Wiki list: battleship, carrier, destroyer, battle_cruiser, heavy_cruiser, light_cruiser, submarine.
- `equipment` holds one concrete type with `amount = 1` (wiki: keep it at one), `owner` and `version_name`. The wiki adds `creator` for hulls the owner has not unlocked. The owner or creator needs the technology, and the variant must exist in its history (wiki note).
- `pride_of_the_fleet = yes` on at most one ship per country (wiki).
- Equipment names by system (wiki lists): MTG hulls `ship_hull_light_1..4`, `ship_hull_cruiser_1..4`, `ship_hull_heavy_1..4`, `ship_hull_super_heavy_1`, `ship_hull_carrier_1..3`, `ship_hull_submarine_1..4`, `ship_hull_pre_dreadnought`, `ship_hull_cruiser_panzerschiff`, `ship_hull_cruiser_submarine`, conversions `ship_hull_carrier_conversion_bb` and `_ca`. Legacy: `destroyer_1..4`, `light_cruiser_1..4`, `heavy_cruiser_1..4`, `battleship_1..4`, `battle_cruiser_1..2`, `carrier_1..4`, `submarine_1..4`.
- Variants for ships are created in country history with `create_equipment_variant` (`type` must be the concrete type, not an archetype; `parent_version`, `upgrades` for legacy ships, `modules` for MTG ships, `obsolete`). The effect also accepts `name_group` for ship names, `allow_without_tech`, `model`, `icon`, `role_icon_index`, `mark_older_equipment_obsolete`. Source: installed effects documentation, `create_equipment_variant`. Vanilla: `history/countries/GER - Germany.txt`.

Runtime ship effects (country scope): `create_ship = { type = ... equipment_variant = "..." creator = TAG name = "..." amount = N }` adds ships to the reserve fleet; `destroy_ships = { type = light_cruiser count = all }`; `transfer_ship = { prefer_name = "..." type = ... target = TAG exclude_refitting = yes }`; `transfer_navy = { target = TAG }` (does not support carriers per its documentation); `transfer_units_fraction` moves army, navy and air fractions together with stockpile and unit leaders.

## Ship and generic name lists

- Ship name groups: `common/units/names_ships/*.txt`, one group per class family (wiki Naval Names; vanilla `ARG_ship_names.txt`):

```text
TAG_DD_HISTORICAL = {
	name = NAME_THEME_HISTORICAL_DESTROYERS
	for_countries = { TAG }
	type = ship
	ship_types = { ship_hull_light destroyer }
	prefix = "XXS "
	fallback_name = "Destroyer %d"
	unique = {
		"Name One" "Name Two"
	}
}
```

- `ship_types` pairs the MTG archetype with the legacy category (first is MTG, second is legacy). Names are space-separated quoted strings without commas.
- Variants bind to a group through `name_group` in `create_equipment_variant`.
- Generic names for equipment without a country list: `common/units/names/*.txt` (wiki Generic Names). Vanilla country files such as `common/units/names/00_ENG_names.txt` use `<TAG> = { <equipment> = { prefix generic unique } }`.
- `NAME_THEME_*` keys are localised in the usual yml files.

## Air wings

Land-based wings (wiki Adding Air Wings; vanilla `history/units/ENG_1936_air_bba.txt`, `GER_1936_air_bba.txt`):

```text
air_wings = {
	763 = {
		small_plane_airframe_0 = {
			owner = "GER"
			amount = 40
			version_name = "He 51"
		}
		name = "Jagdgeschwader 232"
	}
}
```

- The key is a state id, and the state should have an air base (wiki). It is not a province id.
- BBA airframe archetypes seen in vanilla: `small_plane_airframe_0`, `medium_plane_airframe_1`, `large_plane_airframe_3`, plus specialised small airframes such as `small_plane_cas_airframe_0` and `small_plane_naval_bomber_airframe_0`. A BBA variant needs `version_name`.
- Legacy aircraft use plain equipment types (`fighter_equipment_0`, `tac_bomber_equipment_0`, `CAS_equipment_1`, `nav_bomber_equipment_1`, ...). The wiki lists the full set; carrier variants are prefixed `cv_`. Vanilla legacy example `GRE_1936_air_legacy.txt` also sets `create_if_missing = yes` per entry; its semantics are not documented in the sources read, so copy it only alongside that precedent.
- Vanilla repeats the same equipment entry several times under one state key (`ENG_1936_air_bba.txt`); `name = "..."` names the wing.
- Aces: an `ace = { modifier = ... name = ... surname = ... callsign = ... }` block placed after the entry attaches to the wing above it ("order is important" in `ITA_aquila_magna.txt`). The effect `add_ace` exists in country scope for runtime aces (its documentation is a single line, so copy a vanilla call such as the ones in `common/national_focus/austria.txt`).
- Carrier wings: the key is the quoted ship name instead of a state id (`history/units/JAP_1936_air_bba.txt` keys `"Akagi"`), using `cv_` airframes (`cv_small_plane_airframe_0`, `cv_small_plane_cas_airframe_0`, `cv_small_plane_naval_bomber_airframe_0`).
- Sub-unit entries for aircraft in `common/units/air.txt` set wing size per role (`land_air_wing_size`, `carrier_air_wing_size`, `mega_carrier_air_wing_size`, `submarine_carrier_air_wing_size`).

## Starting production and variants

- Starting production belongs in the OOB `instant_effect` or in country history; the effect is `add_equipment_production` (wiki Equipment production). Ships and BBA aircraft need `version_name` and optionally `name`. The installed documentation also lists `amount` and `industrial_manufacturer` (military industrial organization token).
- Technologies needed to field the equipment are set in country history with `set_technology`. Order of statements matters for `load_oob` (units that depend on technology must load after it).

## Checks

1. Both DLC branches exist for every naval and air file you add, or the content is explicitly gated.
2. Every `version_name` has a matching `create_equipment_variant` for that owner.
3. Task-force `location` and fleet `naval_base` are port provinces; air wing keys are states with air bases; carrier wing keys match an existing ship name in the same country.
4. Equipment names are valid for the chosen system (hull versus legacy category; airframe versus legacy equipment).
5. No hull or airframe is listed for an owner or creator without the technology.
