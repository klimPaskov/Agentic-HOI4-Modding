# Hearts of Iron IV Equipment: Bonuses, variants, stockpile effects and sub-unit needs

Part of the [hoi4-equipment](../SKILL.md) skill. Read before writing equipment categories, groups or bonuses, variant, stockpile, production or transfer effects, or sub-unit equipment needs.

## Categories, groups, and equipment bonuses

- Categories are the lowercase category words in `script_enum_equipment_category` (`armor`, `infantry`, `capital_ship`, `fighter`, and so on).
  Any category, archetype, or type that appears in `script_enum_equipment_bonus_type` can be the key of an `equipment_bonus` entry or of a military industrial organization equipment type.
- An equipment group collects types, archetypes, categories, and other groups under a name.
  Syntax: `GAME/common/equipment_groups/_documentation.md`.
  A group can be used as a bonus key.
- `equipment_bonus` appears in ideas, doctrine activation blocks, and the `add_equipment_bonus` effect:

```
equipment_bonus = {
	artillery = {
		instant = yes
		build_cost_ic = -0.2
	}
	infantry_equipment = {
		soft_attack = 0.1
	}
}
```

- Without `instant = yes` the bonus applies only to variants created afterwards, which is why a bonus can appear to do nothing on existing stock.
- Doctrines say to use `equipment_bonus` in the doctrine block instead of the `add_equipment_bonus` effect, because the effect does not remove the bonus when the doctrine is replaced.
- `add_equipment_bonus` takes `bonus = { type = { stat = value instant = yes } }` plus optional `name` (loc key), `prefix`, and `project` (a special project scope that supplies the display name).
- `add_design_template_bonus` gives a limited number of design discounts: `uses`, `cost_factor`, `equipment` (repeatable, at least one), `name`.
  `uses` and `cost_factor` accept a script constant.

## Variants, stockpile, production, and transfers

Full parameter lists and examples are in `references/production-and-stockpile.md`.
The rules that cause most mistakes:

- `create_equipment_variant` needs a `type` (not an archetype).
  Without `allow_without_tech = yes` the variant is created only when the technology for that type is researched.
  `modules` and `upgrades` are inherited from the parent when omitted.
  `parent_version` selects the parent, default 0.
  Ships and tanks need DLC-specific branches when a vanilla design is mirrored; vanilla history files wrap them in `if = { limit = { has_dlc = "..." } }`.
- `add_equipment_to_stockpile` accepts a type or an archetype, a negative `amount` removes, and `producer` restricts which stock is touched.
  `variant_name` is required when the equipment is modular and a variant must exist.
  The producer must have unlocked the equipment for the effect to succeed.
- `add_equipment_production` with a modular type needs `version_name` of an existing variant.
  `creator` is the owner of the design when it differs from the scope.
- `create_production_license` needs a non-archetype `type`, an optional `version`, and a `target` country.
- `send_equipment = { equipment = <type or archetype> amount = <n> target = <country> }` cannot send more than the scope holds; the target receives only what was removed.
- Reading amounts: `num_equipment@infantry_equipment` is a dynamic variable that can be compared with `check_variable`.
  `has_equipment = { type > 100 }` allows only `>` or `<`; do not assume how the boundary value counts, and use a dynamic variable when an exact comparison matters.
  `stockpile_ratio` compares stockpile to fielded and requires `>` or `<`.

## Sub-unit needs

A sub-unit lists the equipment it consumes in `need = { archetype_or_type = amount }` and `essential = { ... }` (`GAME/common/units/light_armor.txt`: `need = { light_tank_chassis = 60 }`).
A new equipment family is useless until a sub-unit names its archetype in `need`, and a sub-unit that is not `active = yes` must be unlocked by `enable_subunits` on a technology or `unlock_subunit`.
Design the sub-unit with `hoi4-units-divisions`.

