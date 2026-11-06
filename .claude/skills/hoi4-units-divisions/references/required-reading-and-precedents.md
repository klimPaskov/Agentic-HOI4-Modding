# HOI4 Units, Divisions and Orders of Battle: Required reading and vanilla precedents

Part of the [hoi4-units-divisions](../SKILL.md) skill. Read before writing script to find the installed documentation, wiki pages and vanilla files to mirror.

## Contents

- Required reading and vanilla precedents
- Mental model and decision table
- Sub-unit definitions (`common/units`)
- Units versus equipment
- Division templates
- Division placement in an order of battle
- Division names
- Loading orders of battle
- Runtime effects, triggers and scopes (overview)
- Manpower
- Stats and modifiers
- Unit leaders, battle plans and AI
- Visuals and counters (overview)
- Localisation
- Repository conventions
- Common mistakes and silent failures
- Validation checklist

## Required reading and vanilla precedents

Read the sections that bear on the task before writing script.
With the HOI4 MCP, use `hoi4.reference_search` and `hoi4.reference_read` for the sections below and `hoi4.source_lookup` for vanilla definitions; if a route fails once, retry once, then read the local files directly.

Installed game documentation is more authoritative than the wiki.
Root: the installed Hearts of Iron IV folder named in `CLAUDE.md`.

| Topic | Primary source |
| --- | --- |
| Unit effects (`division_template`, `create_unit`, `load_oob`, `set_oob`, `set_naval_oob`, `set_air_oob`, `set_keyed_oob`, `add_units_to_division_template`, `delete_unit`, `delete_units`, `delete_unit_template_and_units`, `set_division_template_lock`, `set_division_template_cap`, `set_division_force_allow_recruiting`, `change_division_template`, `create_colonial_division_template`, `create_ship`, `transfer_units_fraction`, `unlock_subunit`, `add_unit_bonus`, `add_manpower`, `damage_units`) | `documentation/effects_documentation.md` (search `## <effect>`) |
| Unit triggers (`has_template`, `has_template_majority_unit`, `has_template_containing_unit`, `division_has_majority_template`, `division_has_battalion_in_template`, `divisions_in_state`, `num_divisions`, `has_army_size`, `has_army_manpower`, `any_country_division`, `any_state_division`) | `documentation/triggers_documentation.md` |
| Manpower as a readable value (`manpower_k`, `max_manpower_k`, `max_available_manpower_k`, `deployed_army_manpower_k`, `has_manpower`) | `documentation/dynamic_variables_documentation.md` |
| Modifier names and scopes (`army`, `naval`, `air`, `unit_leader` scopes, `training_time_factor`, `conscription_factor`, `weekly_manpower`) | `documentation/modifiers_documentation.md` |
| Localisation objects for units and leaders | `documentation/loc_objects_documentation.md` (UnitLeader, Character) |
| Script constants | `documentation/script_concept_documentation.md`, `common/script_constants/documentation.md` |
| Equipment schema, `type` values, archetypes, modules | `common/units/equipment/_documentation.md`, `common/equipment_groups/_documentation.md` |
| AI division templates and role ratios | `common/ai_templates/_documentation.md`, `common/ai_strategy/_documentation.md` |
| Unit and division defines (grid sizes, experience levels, leader deploy cooldowns) | `common/defines/00_defines.lua` (`NDefines.NMilitary`) |

Offline wiki (`hoi4_wiki/`): `unit_modding.md` (sub-units, categories, groups, stats, icons), `division_modding.md` (templates, placement, navy and air OOB, unit name lists), `country_creation.md` (Order of battle, Variants), `namelist_modding.md` (division, ship and generic name lists), `technology_modding.md` (`enable_subunits`, sub-unit bonuses), `equipment_modding.md`, `entity_modding.md`, `scopes.md` (division and combatant scopes).

Vanilla precedents to mirror:

- Sub-unit definitions: `common/units/infantry.txt`, `artillery.txt`, `medium_armor.txt`, `recon.txt`, `engineer.txt`, `fire_support.txt` (regimental support), `hq_support.txt` (Army HQ companies), `destroyer.txt` (ship), `air.txt` (air wing).
- Unit categories: `common/unit_tags/00_categories.txt`.
- Per-sub-unit modifier registration: `common/units/unit_modifiers/unit_modifiers.txt`.
- Land OOB with templates, names and `regimental_support`: `history/units/GER_1936_nsb.txt`, `CZE_1936_nsb.txt`; DLC-split OOBs: `GER_1936.txt` versus `GER_1936_nsb.txt`.
- Naval OOB: `history/units/GER_1936_naval_mtg.txt` (Man the Guns) and the matching `*_naval_legacy.txt`.
- Air OOB: `history/units/ENG_1936_air_bba.txt` (By Blood Alone airframes) and `GRE_1936_air_legacy.txt`; aces: `ITA_aquila_magna.txt`.
- OOB registration in country history: `history/countries/GER - Germany.txt` (`set_oob` inside `if`, `set_air_oob`, `set_naval_oob`, `create_equipment_variant`).
- Templates created by effect: `history/general/taog_hq_template.txt` (Army HQ), `common/decisions/AUS.txt` (templates plus `create_unit`), `common/decisions/GER.txt` (`add_units_to_division_template`, `load_oob` after a state transfer).
- Division name groups: `common/units/names_divisions/GER_names_divisions.txt` (the file header documents every key).
- Ship name groups: `common/units/names_ships/*.txt`; generic equipment names: `common/units/names/*.txt`.
- Sprites: `interface/subuniticons.gfx`; entities: `gfx/entities/units_infantry.asset`.
- Unit localisation: `localisation/english/unit_l_english.yml`, `deployment_l_english.yml` (group titles).

