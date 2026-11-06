# HOI4 Units, Divisions and Orders of Battle: Templates, OOBs and loading

Part of the [hoi4-units-divisions](../SKILL.md) skill. Read before writing division templates, OOB division blocks or division names, or registering and loading an order of battle.

## Division templates

Template block (valid in OOB files and as an effect in country scope; skeleton from `history/units/GER_1936_nsb.txt` and the wiki):

```text
division_template = {
	name = "Example Division"
	division_names_group = GER_Inf_01
	role = infantry
	regiments = {
		infantry = { x = 0 y = 0 }
		infantry = { x = 0 y = 1 }
		infantry = { x = 1 y = 0 }
		infantry = { x = 1 y = 1 }
	}
	regimental_support = {
		field_guns = { x = 0 y = 0 }
	}
	support = {
		engineer = { x = 0 y = 0 }
		artillery = { x = 0 y = 1 }
	}
}
```

Optional keys (wiki `Division modding`, `Effects` > `division_template`, and vanilla use): `division_names_group`, `is_locked`, `force_allow_recruiting`, `division_cap` (template must be locked), `priority` (supply priority 0 reserves, 1 default, 2 elite), `template_counter` (icon id; sprites `GFX_div_templ_<n>_large` and `GFX_div_templ_<n>_small` in `interface/subuniticons.gfx`), `ingame_set_template_counter = yes` (vanilla `INS_1936.txt`; makes the counter editable in game), `override_model` (an entity name), `role` (an AI role label seen in vanilla OOBs such as `GER_1936_nsb.txt`; use it only to match `common/ai_templates` roles), `is_army_hq = yes` (Army HQ templates, `history/general/taog_hq_template.txt`).

Grid rules:

- `x` is the column (left to right), `y` the row (top to bottom), both starting at 0.
- Defaults from `NDefines.NMilitary` in `common/defines/00_defines.lua`: regiments 5 by 5 (`MAX_DIVISION_BRIGADE_WIDTH`, `MAX_DIVISION_BRIGADE_HEIGHT`), division support 1 by 5, regimental support 5 by 1, Army HQ templates 1 by 4 with 1 by 4 support and no regimental support. The defines also set a designer minimum regiment height (`MIN_DIVISION_BRIGADE_HEIGHT = 4`).
- Sub-units placed in `support` must have `group = support`; sub-units placed in `regiments` must not. Wiki: the group cannot change within a single column; vanilla keeps one group per `x` column.
- Avoid duplicate coordinates, out-of-range coordinates, sub-units that are not unlocked, and `same_support_type` clashes; the exact engine reaction to each is not documented, so treat them as defects to prevent by review.
- Templates are identified by `name` per country. Two templates with the same name collide: new divisions refer to the template by name.

Runtime template editing:

- `add_units_to_division_template = { template_name = "..." regiments = { infantry = 0 } support = { engineer = 0 } regimental_support = { ... } }` adds battalions to the first free slot of the given column (the number is the column `x`). It adds only; it cannot remove or move. In division scope `template_name` is optional. Vanilla: `common/decisions/GER.txt`.
- To restructure, create a new template and `delete_unit_template_and_units` the old one, or use `change_division_template = "Name"` in division scope to move a division to another template. Vanilla: `common/scripted_effects/NOR_scripted_effects.txt`.
- Locks and caps: `set_division_template_lock = { division_template = "..." is_locked = yes }`, `set_division_template_cap = { division_template = "..." division_cap = 12 }`, `clear_division_template_cap`, `set_division_force_allow_recruiting`, `country_lock_all_division_template`. The country-level lock (`country_lock_all_division_template`) cannot be undone with the per-template effect; unlock it the same way.
- Overlord-owned colonial templates: `create_colonial_division_template = { subject = TAG division_template = { ... } }`.
- Test existence with `has_template`, `has_template_majority_unit`, `has_template_containing_unit` before adding, editing or deleting.

## Division placement in an order of battle

Divisions live in the `units = { ... }` block of an OOB file (wiki: `Division modding` > Division placement; keys frequency-checked against all vanilla `history/units/*.txt`).

```text
units = {
	division = {
		division_name = {
			is_name_ordered = yes
			name_order = 25
		}
		location = 6334
		division_template = "Infanterie-Division"
		start_experience_factor = 0.3
		start_equipment_factor = 0.8
		start_manpower_factor = 0.9
		force_equipment_variants = { infantry_equipment_1 = { owner = "GER" } }
		officer = { name = TAG_officer_loc_key portraits = { army = { large = GFX_x small = GFX_y } } }
	}
	division = {
		name = "1st Example Division"
		location = 9392
		division_template = "Example Division"
	}
}
```

- Exactly one naming method: `name = "literal"` or `division_name = { is_name_ordered = yes name_order = N }` (uses the template's name group; unmatched numbers use the group `fallback_name`).
- `location` is a province id, not a state id. Vanilla places divisions only in provinces of the owning country; assume other placements are unsafe unless a precedent shows otherwise.
- `start_experience_factor` is 0 to 1 (experience levels at 0.1, 0.3, 0.75, 0.9 per `UNIT_EXP_LEVELS`). `start_equipment_factor` defaults to 1 and does not subtract from the stockpile (wiki). `start_manpower_factor` unset means manpower is subtracted from the pool as far as it goes.
- `force_equipment_variants`: key is the concrete equipment type; subkeys `owner`, `creator`, `amount`, `version_name`. Versions are mandatory for variant-based equipment (modern tanks, ships, airframes). The owner or creator must have the technology and the variant must exist in its history.
- `officer = { ... }` defines a division commander character; keep it consistent with `hoi4-characters-leaders` (large portrait for the commander, small for the officer corps; the engine falls back to `<large>_small`).

Equipment production lines go in the OOB `instant_effect` block (any effect is valid there):

```text
instant_effect = {
	add_equipment_production = {
		equipment = { type = infantry_equipment_0 creator = "GER" }
		requested_factories = 1
		progress = 0.19
		efficiency = 100
	}
}
```

Ships need `version_name` for hull-based equipment; air wings need airframe names under By Blood Alone. Details in `references/naval-air-oob.md`.

## Division names

Name groups live in `common/units/names_divisions/*.txt` (ordered `%d` or `%s` entries, `fallback_name`, `link_numbering_with`, `for_countries`, `can_use`); templates select one with `division_names_group`, OOB divisions with `division_name = { is_name_ordered = yes name_order = N }`. The full skeleton and rules are in `references/names-stats-visuals.md`.

## Loading orders of battle

An OOB file does nothing until a country loads it.

| Mechanism | Where | Notes |
| --- | --- | --- |
| `oob = "file"` | country history file as an argument | Not an effect, so it cannot sit inside `if` |
| `set_oob = "file"` | country history, effect | Replaces the previous OOB with no key; usable inside `if`; history only |
| `set_naval_oob`, `set_air_oob` | country history, effect | Replace the OOB with key `naval` or `air` |
| `set_keyed_oob = { key = x name = "file" }` | country history, effect | Replaces the OOB registered under the key; history only |
| `load_oob = "file"` | any effect in country scope | Loads immediately and adds to the country's current state |

The filename of the OOB is irrelevant as long as the registering call uses the same string without `.txt` (wiki: Order of battle).

DLC splits: By Blood Alone (air) and Man the Guns (navy) are incompatible with the legacy systems, so vanilla keeps separate files (`*_air_bba` / `*_air_legacy`, `*_naval_mtg` / `*_naval_legacy`), and No Step Back splits land OOBs that mention tank equipment (`GER_1936.txt` / `GER_1936_nsb.txt`). Register them with `if = { limit = { has_dlc = "..." } set_oob = "..." }` and the negated twin. In country history files `else` works only in its nested form (wiki).

`load_oob` caveats:

- Wiki: not recommended in history files because it loads immediately; loading before the needed technologies exist, or a file that contains divisions, can fail or crash.
- Observed in this repository's live testing: `load_oob` on a country that owns no state does nothing silently. Load after the first state has been transferred, or register with `set_oob` in the country's history. Vanilla precedent: `common/decisions/GER.txt` transfers states and gives the new country manpower and technology first, then runs `load_oob = "RK_OOB"`.
- It adds to what the country already has. Reloading the same file duplicates divisions, and templates with the same name collide. Guard with a flag or `has_template`, or use unique template names.
- It also runs the file's `instant_effect` block. Do not put one-time economy effects in an OOB that will be loaded more than once.
- A country with no OOB at game start has broken buildings (wiki: Order of battle). Every playable or scripted-in country needs at least a minimal OOB.

