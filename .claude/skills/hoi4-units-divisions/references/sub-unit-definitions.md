# HOI4 Units, Divisions and Orders of Battle: Sub-unit definitions

Part of the [hoi4-units-divisions](../SKILL.md) skill. Read before creating or changing a sub-unit in common/units, including its equipment needs, stats, sprites, counters and localisation.

## Sub-unit definitions (`common/units`)

Files are loaded by folder; every file starts with `sub_units = { ... }` and contains any number of entries keyed by the sub-unit id.
The id is the token used in templates, `need` lookups, technologies (`enable_subunits`), localisation and modifier names.

Land battalion skeleton (fields as used by `common/units/infantry.txt` and `medium_armor.txt`):

```text
sub_units = {
	my_infantry = {
		abbreviation = "MYI"
		sprite = infantry
		map_icon_category = infantry

		priority = 600
		ai_priority = 200
		active = no

		type = { infantry }
		group = infantry

		categories = {
			category_front_line
			category_light_infantry
			category_all_infantry
			category_army
		}

		combat_width = 2

		max_strength = 25
		max_organisation = 60
		default_morale = 0.3
		manpower = 1000
		training_time = 90
		suppression = 1.5
		weight = 0.5
		supply_consumption = 0.06

		need = {
			infantry_equipment = 100
		}

		hills = { attack = 0.1 movement = 0.05 }
	}
}
```

Support company differences (`common/units/artillery.txt`, `recon.txt`, `hq_support.txt`):

```text
		group = support
		type = { infantry support }
		categories = { category_support_battalions category_divisional_support_battalions category_army }
		regimental = no
		affects_speed = no
		combat_width = 0
		same_support_type = recon
```

Field notes, each verified against vanilla files named above and `Unit modding` on the wiki:

- `sprite` is the entity base name. The engine looks up an entity named `<sprite>_entity` (with graphical-culture, country and cosmetic-tag prefixed variants). Wiki: `Unit modding` (Models) and `Entity modding`.
- `map_icon_category`: wiki lists `infantry`, `armored`, `other`, `ship`, `transport`, `uboat`. Vanilla `infantry.txt` header comment lists the same families. You cannot add new map icon categories or new internal `type` values.
- `type = { ... }`: internal types. Wiki list: infantry, support, artillery, anti_tank, anti_air, armor, fighter, cas, naval_bomber, interceptor, suicide, tactical_bomber, strategic_bomber, air_transport, missile, submarine, screen_ship, capital_ship, carrier, motorized, mechanized, flame, amphibious. The `type` values drive built-in rules, so copy the closest vanilla unit instead of inventing combinations.
- `group`: `infantry`, `mobile`, `armor`, `support` in the wiki; vanilla also uses `combat_support`, `mobile_combat_support`, `armor_combat_support` (see `allowed_battalion_groups` in `fire_support.txt`). The group sets the template tab and the row the sub-unit may occupy. A new group name used in `group =` is created automatically; give it `group_<name>_title` localisation and a `GFX_group_<name>_icon` sprite (wiki, `Unit modding` > How to add new Groups; vanilla title keys live in `deployment_l_english.yml`).
- `priority`: which sub-unit's icon and model wins when several are present. Support entries use 0 in vanilla.
- `ai_priority`: AI preference when picking sub-units.
- `active = yes` means usable without unlocking; `active = no` means a technology must unlock it via `enable_subunits = { id }` in a technology (wiki: `Technology modding`). Script can also unlock with `unlock_subunit = id` in country scope (installed effects documentation; vanilla use in `common/doctrines/subdoctrines/special_forces/`).
- `categories`: tags from `common/unit_tags/00_categories.txt`. Technologies and `add_unit_bonus` address categories (for example `category_all_infantry`). A new category is declared in a `sub_unit_categories = { ... }` list like the vanilla file (put it in a new file of the same folder; confirm it loads without a duplicate-definition complaint) and needs a localisation key (vanilla: `category_light_infantry` in `unit_l_english.yml`).
- Flags: `special_forces`, `marines`, `mountaineers`, `rangers`, `cavalry`, `can_be_parachuted`, `can_exfiltrate_from_coast`, `affects_speed`. Vanilla comment in `infantry.txt`: for `can_exfiltrate_from_coast` all non-support sub-units in the division must have it.
- `transport = <equipment>`: the equipment that sets movement speed (motorized and mechanized). Wiki: sets speed via equipment.
- `need`: map of equipment archetype or category to the quantity per battalion. Keys such as `infantry_equipment` are archetypes, not concrete variants such as `infantry_equipment_1`.
- `essential`: list of equipment keys. Vanilla comment in `infantry.txt` for `mechanized`: "needed since we give so much bonus to infantry even with no mech equipment". Treat it as "this sub-unit loses its bonus without these"; verify behaviour in game for a new unit.
- `regimental = no`, `divisional = no`, `allowed_battalion_groups = { ... }`: placement rules. `divisional = no` plus `allowed_battalion_groups` define a regimental support company that may attach only to battalions of the listed groups (`fire_support.txt`). `regimental = no` marks a plain divisional support company.
- `same_support_type = token`: only one sub-unit with a given token per template. Several tokens may be listed (`recon.txt` lists `recon` and `helicopter_recon`).
- `allow_in_army_hq` / `allow_in_non_army_hq`: gate Army HQ templates (`hq_support.txt`).
- `required_dlc = { "..." }`: restricts the entry.
- Terrain blocks (`forest`, `hills`, `mountain`, `jungle`, `marsh`, `urban`, `river`, `amphibious`, `plains`, `desert`, `snow`, `fort`) hold `attack`, `defence`, `movement`.
- Naval and air entries are thin (`destroyer.txt`, `air.txt`): `sprite`, `priority`, `active`, `type`, `need = { ship_hull_light = 1 }` or `need = { small_plane_airframe = 1 }`, `categories`, wing sizes (`land_air_wing_size`, `carrier_air_wing_size`), `critical_parts`, `hit_profile_mult`. Their real stats live on the equipment.

Per-sub-unit modifiers: `modifier_army_sub_unit_<id>_attack_factor`, `_defence_factor`, `_speed_factor`, `_max_org_factor`, `_org_recovery_cap_factor`, and `modifier_army_sub_unit_category_<cat>_*` are available only for names listed in `common/units/unit_modifiers/unit_modifiers.txt`. A new sub-unit that should be targetable by such modifiers must be added there (a new file in that folder, same `sub_unit_modifiers = { ... }` structure). `common/modifier_definitions` contains no entries for these names in vanilla, so the registration is what creates them; localise each in the style of `modifiers_l_english.yml` (`modifier_army_sub_unit_infantry_attack_factor: "Infantry Attack"` plus the `_tt` form). The vanilla file notes that `_speed_factor` and `_max_org_factor` cannot be applied to support battalions.

## Units versus equipment

- A sub-unit asks for equipment (`need`). A division fields the sum of its battalions' needs; deficits lower strength and bonuses, and AI and players fill them from the stockpile.
- Equipment files define `archetype`, `type`, stats, `resources`, `year`, upgrades and modules (`common/units/equipment/_documentation.md`). Infantry weapons: `infantry_equipment` is the archetype, `infantry_equipment_0/1/2/3` are the concrete types (`common/units/equipment/infantry.txt`).
- Unlock chain: technology `enable_equipments` and `enable_subunits` -> equipment becomes buildable and the sub-unit becomes selectable.
- Equipment stats flow into the division (soft attack, defense, breakthrough, armor, speed). A sub-unit's own stats add on top.
- `common/equipment_groups/` groups equipment types for `equipment_bonus` and AI; see `common/equipment_groups/_documentation.md`.
- In OOBs `force_equipment_variants` pins which equipment variant a division uses, and `add_equipment_production` (inside `instant_effect`) starts production lines.
- Naval and air sub-units are driven almost entirely by equipment (`ship_hull_*`, airframes); see `references/naval-air-oob.md`.

## Stats and modifiers

Sub-unit stats (`max_strength`, `max_organisation`, `manpower`, `supply_consumption`, `combat_width`, terrain blocks), country and army modifiers, `add_unit_bonus`, and the `defense` versus `defence` spelling rule are in `references/names-stats-visuals.md`. Naval and air stats live on the equipment.

## Visuals and counters (overview)

A sub-unit's `sprite` resolves the entity `<sprite>_entity`; counters are `GFX_unit_<id>_icon_medium`, `_medium_white` and `_small` sprites in `interface/subuniticons.gfx`, plus `GFX_group_<name>_icon` for groups and `GFX_div_templ_<n>_large`/`_small` for template counters. Details are in `references/names-stats-visuals.md`. Custom models, animations, sound and counter art belong to `hoi4-3d-model-pipeline`, `hoi4-feature-assets` and `hoi4-frame-animation`.

## Localisation

- Sub-unit: `<id>: "Name"` and `<id>_desc: "..."` (vanilla `infantry`, `infantry_desc`, `marine`, `marine_desc` in `unit_l_english.yml`). The `abbreviation = "XXX"` field is a literal string, not a key.
- Categories: `category_<name>: "..."`. Group titles: `group_<name>_title: "..."`.
- Templates and divisions use literal names or name-group strings; name-group descriptions may be loc keys.
- Modifier names for new sub-unit modifiers need keys; tooltip text uses `$modifier_...$` references.
- Files: UTF-8 with BOM, `l_english:` header, keys without the `:0` suffix in this repository.

