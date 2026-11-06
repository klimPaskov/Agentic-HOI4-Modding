---
name: hoi4-equipment
description: Use when creating, changing or scripting HOI4 equipment, archetypes, variants, bonuses, modular designs, stockpile or production effects, or when equipment or a bonus silently does nothing.
---

# Hearts of Iron IV Equipment

Use this skill for anything under `common/units/equipment/`, `common/equipment_groups/`, `common/ai_equipment/`, the equipment designer interface, and every effect, trigger, or modifier that creates, moves, produces, or boosts equipment.
Sub-unit (battalion) definitions, division templates, and orders of battle belong to `hoi4-units-divisions`.
Technology that unlocks equipment, and doctrine rewards, belong to `hoi4-technology-doctrines`.
The idea or national spirit that carries an `equipment_bonus` belongs to `hoi4-ideas-modifiers`.
AI strategy tokens, `ai_will_do`, and role ratios belong to `hoi4-ai-strategies`.

In this skill `GAME` means the installed Hearts of Iron IV folder named in `CLAUDE.md` and `WIKI` means the repository folder `hoi4_wiki`.
Installed documentation is more authoritative than the wiki.
Where they differ, this skill says so.

Open the reference that matches the task before writing definitions or effects. Do not write equipment from memory: read the engine contract below first, and remember installed documentation outranks the wiki.

Always apply these rules:

- Every new archetype, type or category that can be named in `equipment_bonus` or by a military industrial organization goes into `script_enum_equipment_bonus_type` in `common/script_enums.txt` in the same change (Repository conventions below).
- A new equipment family needs an unlock (`active = yes` or a technology with `enable_equipments`), a sub-unit whose `need` names the archetype, and text and art registered in `.gfx` (`references/new-line-text-checklist-and-failures.md`).
- `equipment_bonus` without `instant = yes` affects only variants created afterwards. Stockpile and production effects on modular equipment need `variant_name` or `version_name` of an existing variant. `create_equipment_variant` and `create_production_license` need a type, not an archetype (`references/bonuses-variants-and-subunit-needs.md`).
- Modular lines need `module_slots`, `default_modules`, a designer window and module definitions (`references/equipment-definition-syntax.md`).
- State what was not verified in the final report (Validation below).

Deeper existing references: [modules, designer and AI designs](references/modular-equipment-and-designer.md), [effect, trigger and dynamic variable catalogue](references/production-and-stockpile.md), [military industrial organisations and special projects](references/mios-and-special-projects.md).

## Reference map

- [Equipment definition syntax](references/equipment-definition-syntax.md): Read before writing or changing an equipment archetype, numbered type, upgrade chain, modular chassis, hull or airframe, or duplicated archetype. Covers: Equipment definitions.
- [Bonuses, variants, stockpile effects and sub-unit needs](references/bonuses-variants-and-subunit-needs.md): Read before writing equipment categories, groups or bonuses, variant, stockpile, production or transfer effects, or sub-unit equipment needs. Covers: Categories, groups, and equipment bonuses; Variants, stockpile, production, and transfers; Sub-unit needs.
- [Text, art, new-line checklist and silent failures](references/new-line-text-checklist-and-failures.md): Read when finishing a new equipment line with its text, icons and registrations, or when equipment, a module or a bonus silently does nothing. Covers: Localisation and graphics; New equipment line checklist; Common mistakes and silent failures.

## Read the engine contract first

Gather the relevant sections through `hoi4.reference_context`, `hoi4.reference_search`, and `hoi4.reference_read`, and look up vanilla definitions through `hoi4.source_lookup`.
If a route fails once, retry once with narrower input, then read the local files directly.
Do not reproduce the files below from memory; read the section that bears on the change.

| Question | Read |
| --- | --- |
| Equipment definition fields, module slots, count limits, default modules | `GAME/common/units/equipment/_documentation.md` |
| Equipment categories used by bonuses | `GAME/common/script_enums.txt` (`script_enum_equipment_category`, `script_enum_equipment_bonus_type`, `script_enum_equipment_stat`) |
| Equipment groups | `GAME/common/equipment_groups/_documentation.md` |
| AI designs | `GAME/common/ai_equipment/_documentation.md`, `GAME/common/ai_equipment/generic_tank.txt` |
| Designer windows | `GAME/interface/equipmentdesigner/_documentation.info` |
| Icon and model pools | `GAME/gfx/interface/equipmentdesigner/graphic_db/_documentation.info` |
| Effects (`add_equipment_to_stockpile`, `create_equipment_variant`, and the rest) | `GAME/documentation/effects_documentation.md` |
| Triggers (`has_equipment`, `has_license`, and the rest) | `GAME/documentation/triggers_documentation.md` |
| Dynamic variables such as `num_equipment@type` | `GAME/documentation/dynamic_variables_documentation.md` |
| Modifiers (`equipment_conversion_speed`, licence modifiers, design cost factors) | `GAME/documentation/modifiers_documentation.md` |
| Defines (stockpile, licence, module XP costs) | `GAME/common/defines/00_defines.lua` |
| Concepts and legacy notes | `WIKI/equipment_modding.md`, `WIKI/division_modding.md` (equipment production), `WIKI/country_creation.md` (Variants) |

The detailed module, designer, and AI design material is in `references/modular-equipment-and-designer.md`.
The full effect, trigger, and dynamic variable catalogue is in `references/production-and-stockpile.md`.
Military industrial organisations and special projects are in `references/mios-and-special-projects.md`.

## Decision table

| Goal | Mechanism |
| --- | --- |
| New non-modular equipment line (rifles, artillery, trucks) | Archetype plus numbered types in a new `common/units/equipment/*.txt`; unlock with a technology |
| New tank chassis, ship hull, or airframe | Modular archetype with `module_slots`, numbered chassis types, a designer window, and module definitions |
| Anti-air, artillery, or tank-destroyer variant of an existing chassis | `duplicate_archetypes` file evaluated after the base archetypes |
| Give a country a ready-made design | `create_equipment_variant` |
| Put finished equipment in a stockpile | `add_equipment_to_stockpile` |
| Start a production line | `add_equipment_production` |
| Permanent percentage boost to an equipment family | `equipment_bonus` in an idea, doctrine, or sub-doctrine; the `add_equipment_bonus` effect for a source that is not removed with its owner |
| Boost every variant a country designs from now on | `equipment_bonus` without `instant`, or `add_equipment_bonus` without `instant` |
| Make a bonus to existing equipment apply immediately | `instant = yes` inside the equipment entry |
| Let a country build another country's design | `create_production_license` |
| Move equipment between countries | `send_equipment`, `send_equipment_fraction`, or a purchase contract |
| Check how much equipment a country has | `has_equipment`, `stockpile_ratio`, or the `num_equipment@type` dynamic variable |
| Steer how the AI designs or builds | `common/ai_equipment` for designs; `hoi4-ai-strategies` for production strategies |

## Repository conventions that apply

- Indent with tabs, never use `<=` or `>=`, put tuning numbers in `common/script_constants/`, and reuse the project's dynamic scripted effects library (`common/scripted_effects/<prefix>_dynamic_effects.txt`, named in `CLAUDE.md`) before writing new dynamic helpers.
- Localisation is UTF-8 with BOM, keys have no `:0`, and player-facing text describes the current world, not history.
- Every new equipment type, archetype, or category that can be named in `equipment_bonus` or a military industrial organization must be added to `script_enum_equipment_bonus_type` in `common/script_enums.txt` in the same change.
  The repository file replaces the vanilla file of the same path, so it carries the vanilla list plus additions; after a game update, re-merge any new vanilla entries.
- A new concrete equipment type, sub-unit, special project, or doctrine must also follow the test-country registration rule in `CLAUDE.md` (package-owned idempotent setup effect and hidden-idea carrier).
- When a new mechanic is added, document it in a `docs/` markdown file with its icons and the `.gfx` file that references them.
- Read manpower through `manpower_k`, never the plain `manpower` variable, which overflows.

## Validation

- Read back the definition through `hoi4.source_lookup` and confirm archetype, parent chain, `year`, unlock, and enum registration.
- For a technology that unlocks the equipment, run `hoi4.tech_inspect` in `unlocks` mode with the technology id and confirm the equipment appears; see `hoi4-technology-doctrines`.
- Run `hoi4.script_validate` on the effect or trigger bodies that touch equipment, with `kind` and `scope = country`.
  A passing result covers only the listed checks; argument semantics and engine behaviour stay unverified.
- Check that every key in a new localisation set exists for the type, `_short`, and `_desc`, and that every sprite name resolves.
- State what was not verified: designer layout, module availability, and live production behaviour need the game.
