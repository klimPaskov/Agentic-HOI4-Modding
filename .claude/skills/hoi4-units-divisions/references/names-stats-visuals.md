# Division Names, Stats and Modifiers, Visuals

Read this when writing a division name group, tuning sub-unit stats or modifiers, or wiring sprites and counters for a new sub-unit.

## Division names

Name groups live in `common/units/names_divisions/*.txt` (file name irrelevant; wiki limits a file to about 1500 lines). The header of `GER_names_divisions.txt` documents each key:

```text
MY_INF_01 = {
	name = "Infantry Divisions"
	for_countries = { TAG }
	can_use = { always = yes }
	division_types = { "infantry" }
	fallback_name = "%d. Division"
	link_numbering_with = { OTHER_GROUP }
	unordered = { "Name without a number" }
	ordered = {
		1 = { "%d. Division" "optional localisable description" }
		2 = { "%s. Division" }
	}
}
```

- `%d` inserts a decimal number, `%s` a Roman numeral. Numbers must start at 1, cannot repeat inside one group and may have gaps.
- `for_countries` empty or missing means all countries; `can_use` is a country-scope trigger; `division_types` is only a hint for automatic choice (the template needs at least one of the listed types).
- Redefining the same group id and number in a later file overrides the earlier name.
- A template without `division_names_group` gets one chosen from its sub-units (wiki). The reaction to a group id that does not exist is undocumented; verify every referenced id exists.
- Character names for generated leaders live in `common/names/` and portraits in `portraits/`; see `hoi4-characters-leaders`.


## Stats and modifiers

- Land stats on a sub-unit: `manpower`, `max_strength` (HP), `max_organisation`, `default_morale`, `combat_width`, `supply_consumption`, `weight`, `training_time`, `suppression`, `breakthrough`, `soft_attack`, `hard_attack`, `defense`, `entrenchment`, `armor_value`, `hardness`, `recon`, `initiative`, `maximum_speed`, `casualty_trickleback`, `experience_loss_factor`, plus terrain blocks. Wiki: `Unit modding` > Stats and Modifiers. Vanilla uses `defense` and `defence` in different positions: top-level stat is `defense`, terrain blocks use `defence`.
- Stat meanings and vanilla ranges: wiki `Unit modding` lists them (for example vanilla `max_organisation`: infantry support 20, armor 10, ship 40, cavalry 70). Numbers in the wiki can lag the installed game; read the vanilla unit file you copy.
- Naval and air sub-unit stats are on the equipment, not the sub-unit.
- Country and army modifiers that touch units: `training_time_factor`, `conscription_factor`, `weekly_manpower`, `army_attack_factor`, `army_defence_factor`, `army_org_factor`, `army_morale_factor`, `max_command_power`, `command_power_gain`, `experience_gain_army_factor`, `unit_upkeep_attrition_factor`, `additional_brigade_column_size`. Names and scopes are in `documentation/modifiers_documentation.md` under `army`, `naval`, `air`, `unit_leader`.
- Sub-unit and category bonuses from technologies and `add_unit_bonus`:

```text
add_unit_bonus = {
	category_light_infantry = { soft_attack = 0.05 name = MY_LOC_KEY }
	cavalry = { soft_attack = 0.05 hard_attack = 0.05 }
}
```

- Dynamic modifiers can hold variable-driven values (`common/dynamic_modifiers`, `add_dynamic_modifier`); vanilla uses them for per-country army modifiers.
- Modifier names shown in tooltips need localisation (`modifier_army_sub_unit_<id>_attack_factor` and the others).


## Visuals and counters (overview)

- Division map models come from entities: `sprite = X` resolves `X_entity` in `gfx/entities/*.asset`. A division shows the model of the plurality sub-unit (highest `priority` among equals). `override_model` on the template forces an entity.
- Counters and icons are sprites in `interface/subuniticons.gfx`; naming pattern verified in the vanilla file: `GFX_unit_<id>_icon_medium` (large `divisions_large` art), `GFX_unit_<id>_icon_medium_white` (`divisions_small` on-map art) and `GFX_unit_<id>_icon_small` (text icon, defined in `interface/texticons.gfx`), each with `noOfFrames = 2`. Group icon: `GFX_group_<name>_icon`. Template counter: `GFX_div_templ_<n>_large` and `_small`.
- A sub-unit without sprites shows random or placeholder counters in the designer (wiki). Define all three sprite names even when reusing a vanilla texture.
- Do not duplicate asset production here: custom models, rigs, animations, sound hooks and the green counter handoff are in `hoi4-3d-model-pipeline`; sprite wiring, flags and icon art are in `hoi4-feature-assets`; animated frame sheets are in `hoi4-frame-animation`.
- Register new sprites before requesting art so file names do not change later.
