# Hearts of Iron IV Equipment: Text, art, new-line checklist and silent failures

Part of the [hoi4-equipment](../SKILL.md) skill. Read when finishing a new equipment line with its text, icons and registrations, or when equipment, a module or a bonus silently does nothing.

## Localisation and graphics

- Equipment: `<type>`, `<type>_short`, `<type>_desc`; a country-specific name is `<TAG>_<type>` with the same suffixes.
  Vanilla: `GAME/localisation/english/equipment_l_english.yml`, `equip_air_l_english.yml`, `equip_naval_l_english.yml`.
- A technology without its own name borrows the name of the equipment it unlocks.
- Modules: `<module>`, `<module>_desc`, and optionally `<module>_short`; categories `EQ_MOD_CAT_<category>_TITLE`; slots `EQ_MOD_SLOT_<slot>_TITLE`.
  Vanilla: `tank_modules_l_english.yml`, `ship_modules_l_english.yml`.
- Icons: archetype pictures are sprites named `GFX_<picture>_medium` in an `interface/*.gfx` file (`GAME/interface/Technologies.gfx` holds `GFX_archetype_infantry_equipment_medium`).
  A type's icon is `GFX_<type>_medium`, with a country override `GFX_<TAG>_<type>_medium`.
  If a type has no own icon, it uses the icon of the technology that unlocks it.
  Module icons use `GFX_EMI_<module>` (`GAME/interface/tank_modules_icons.gfx`).
  Per-country icon and model pools for variants are set in `gfx/interface/equipmentdesigner/graphic_db/*.txt`.
- Register every sprite in a `.gfx` file before requesting art so the file name does not change later.

## New equipment line checklist

Work through these in one change; each item is a separate failure point.

1. Definition: archetype, numbered types with `archetype`, `parent`, `year`, `priority`, `visual_level`, and an unlock path (`active = yes` or a technology).
2. Enum: archetype and types added to `script_enum_equipment_bonus_type` (and `script_enum_equipment_category` only if a new category word is introduced).
3. Unlock: a technology with `enable_equipments`, and for modular lines `enable_equipment_modules` (see `hoi4-technology-doctrines`).
4. Consumer: a sub-unit whose `need` names the archetype, unlocked with `enable_subunits` or `active = yes` (see `hoi4-units-divisions`).
5. Modular only: modules, slot and category titles, designer windows, filters, and a default variant check.
6. Text and art: `<type>`, `_short`, `_desc` keys, archetype picture sprite, type sprites, and module sprites registered in `.gfx`.
7. Stock and production entry points: a scripted way to grant or build it, using the effects above, with `variant_name` or `version_name` for modular lines.
8. AI: a design group for modular lines and, where relevant, production strategy tokens (see `hoi4-ai-strategies`).
9. Docs and tests: the mechanic document, any test-country or debug setup the project uses, and the dynamic-effects documentation if a helper was added.

## Common mistakes and silent failures

- Equipment appears in the bonus list but the bonus does nothing: the type is missing from `script_enum_equipment_bonus_type`, or `instant = yes` is missing and no new variant has been designed.
  The enum file comment says a startup log error reminds you to update it.
- Equipment cannot be built: no `active = yes` and no technology `enable_equipments`, or `can_be_produced` is false for that country.
- `add_equipment_to_stockpile` of a modular type does nothing: no `variant_name`, no matching variant, or the producer has not unlocked the type.
- A new airframe or chassis never shows in the designer: the designer window or, for airframes, the entry in `GAME/interface/equipmentdesigner/planes/plane_blueprints_generic.gui` is missing (vanilla comment at the top of `plane_airframes.txt`).
- A module appears to be missing from a slot: the module `category` is not in the slot's `allowed_module_categories`, a `forbid_*` rule excludes it, or the module technology is not researched.
- Gun modules that need a turret fail: the turret slot is defined after the gun slot.
  Vanilla notes that dependent slots must be defined in operational order for the AI and historical templates.
- Mixing type and archetype: `create_equipment_variant.type` and `create_production_license.equipment.type` need a type; stockpile effects and bonuses accept either.
- A bonus or modifier is silently ignored when it names a stat the equipment does not carry; check the stat list, and remember that stats on the battalion (for example `recon`) cannot be used by military industrial organizations.
- Removing stock with `set_equipment_fraction` models a loss; do not use it to split stockpiles in a civil war because `start_civil_war` already divides them (Effects wiki).
- Deleted stockpiled equipment moves to a hidden pool for `NUM_DAYS_TO_FULLY_DELETE_STOCKPILED_EQUIPMENT` days and can still be seized; do not assume instant erasure.

