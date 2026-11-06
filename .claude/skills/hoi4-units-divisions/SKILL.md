---
name: hoi4-units-divisions
description: Use when creating or changing Hearts of Iron IV sub-units, division templates, orders of battle (land, naval, air), division names, unit spawning and removal, manpower and sub-unit stats.
---

# HOI4 Units, Divisions and Orders of Battle

Generic HOI4 modding guidance for land, naval and air units.
Characters, unit leaders and their traits belong to `hoi4-characters-leaders`.
Equipment types, variants, modules and production belong to `hoi4-equipment`; technologies that unlock sub-units belong to `hoi4-technology-doctrines`; ideas and modifier definitions belong to `hoi4-ideas-modifiers`; wider AI weighting belongs to `hoi4-ai-strategies`; state, province and supply data belong to `hoi4-map-states`. This skill only covers how a unit consumes equipment and how units are defined, loaded and scripted.
Custom 3D unit models, animations, counters and sounds belong to `hoi4-3d-model-pipeline`; counter and flag art belongs to `hoi4-feature-assets`; frame-sheet animation belongs to `hoi4-frame-animation`.
Reference files, read when the task needs them: `references/naval-air-oob.md` (fleets, ships, air wings, carrier wings, aces, ship name lists, DLC splits), `references/runtime-effects-triggers.md` (exact signatures of runtime unit, template, manpower effects and triggers, division scope), `references/names-stats-visuals.md` (division name group skeleton, stat and modifier lists, sprite and counter wiring).

This file is a router. It keeps the five-layer mental model, the repository conventions, the silent-failure list and the validation checklist, which apply to every task. Open the reference for your phase from the map below before you write script, and read the existing reference files named above when the task touches their topics.

Rules that always apply (full text in the references named):

- An order of battle does nothing until a country registers it: `set_oob`, `set_naval_oob`, `set_air_oob` or `set_keyed_oob` in country history, or `load_oob` at runtime on a country that owns at least one state. `oob =` is a history argument and cannot sit inside `if`, and reloading the same file duplicates divisions and templates. See [Templates, OOBs and loading](references/templates-oobs-and-loading.md).
- Template, sub-unit and name-group names are exact strings, and every sub-unit in a template must be unlocked and placed in the right grid region. See [Templates, OOBs and loading](references/templates-oobs-and-loading.md).
- `location` is a province id for divisions, fleets and task forces, and a state id for air wings.
- Man the Guns (navy) and By Blood Alone (air) are incompatible with the legacy systems, so split OOB files by DLC and never mix legacy and DLC equipment names in one file. See `references/naval-air-oob.md`.
- A new sub-unit also needs its unlock path, localisation, sprites and, for targetable modifiers, an entry in `unit_modifiers.txt`. See [Sub-unit definitions](references/sub-unit-definitions.md).
- Read manpower through the `_k` variables, guard `create_unit` and template edits with `has_template`, and do not launch the game. See [Runtime effects, manpower and AI](references/runtime-manpower-and-ai.md).

## Reference map

- [Required reading and vanilla precedents](references/required-reading-and-precedents.md): Read before writing script to find the installed documentation, wiki pages and vanilla files to mirror. Covers: Contents; Required reading and vanilla precedents.
- [Sub-unit definitions](references/sub-unit-definitions.md): Read before creating or changing a sub-unit in common/units, including its equipment needs, stats, sprites, counters and localisation. Covers: Sub-unit definitions (`common/units`); Units versus equipment; Stats and modifiers; Visuals and counters (overview); Localisation.
- [Templates, OOBs and loading](references/templates-oobs-and-loading.md): Read before writing division templates, OOB division blocks or division names, or registering and loading an order of battle. Covers: Division templates; Division placement in an order of battle; Division names; Loading orders of battle.
- [Runtime effects, manpower and AI](references/runtime-manpower-and-ai.md): Read before spawning, editing or removing units during play, handling manpower, or touching unit leaders, battle plans and AI division templates. Covers: Runtime effects, triggers and scopes (overview); Manpower; Unit leaders, battle plans and AI.

## Mental model and decision table

Five layers, each defined in a different place:

1. Sub-unit (battalion or company type): `common/units/*.txt`. Defines stats, which equipment it consumes (`need`), and where it can sit in a template (`group`).
2. Equipment: `common/units/equipment/*.txt`. What sub-units consume. Produced by factories, stockpiled per country, and also fixes the sub-unit speed (`transport`) and many stats.
3. Division template: a country-owned grid of sub-units. Created by `division_template` in an order-of-battle file or as an effect.
4. Division (a unit on the map): created from a template by an OOB `division = { ... }` block, by `create_unit`, by the player's recruiting, or by AI production.
5. Order of battle (OOB): a file in `history/units/` containing templates, divisions, fleets, air wings and an `instant_effect` block. It does nothing until a country loads it.

| I want to... | Use |
| --- | --- |
| Add a new battalion or company type | New `sub_units` entry in `common/units/`, plus unlock, localisation, sprites, optional modifiers registration |
| Change stats of an existing sub-unit | Override the whole entry in a same-named file later in load order, or give a country a modifier; do not edit the vanilla file |
| Give a country a starting army, navy or air force | OOB files registered from country history with `set_oob`, `set_naval_oob`, `set_air_oob` |
| Give an existing country new templates or divisions mid-game | `division_template` effect plus `create_unit`, or `load_oob` on a country that owns at least one state |
| Spawn a division at a place chosen by script | `create_unit` with `prioritize_location` or `country_score` |
| Reshape a template the country already has | `add_units_to_division_template` (adds only), `change_division_template` in division scope, or delete and recreate with `delete_unit_template_and_units` |
| Stop the player editing or over-building a template | `is_locked`, `division_cap`, `force_allow_recruiting` on the template, or the matching effects |
| Remove divisions | `delete_unit` (filters), `delete_units` (template), `delete_unit_template_and_units`, `destroy_unit` in division scope |
| Give or take manpower | `add_manpower`; read through `manpower_k` style variables or `has_manpower` |
| Buff or nerf one sub-unit type | Technology `<sub_unit> = {}` bonus, `add_unit_bonus`, or a registered `modifier_army_sub_unit_<name>_*` modifier |

## Repository conventions

These follow the project rules in `CLAUDE.md`, which remain the authority:

- Tabs for indentation, lowercase snake_case, no `<=` or `>=` (use `check_variable` with `compare`), no magic numbers: tuning values (division caps, manpower amounts, equipment amounts, experience factors) go in `common/script_constants/` and are read as `constant:category.key`; where a field rejects constants (some duration and amount fields), copy the constant to a variable and pass the variable.
- Reuse the project's dynamic scripted effects library (`common/scripted_effects/<prefix>_dynamic_effects.txt`, named in `CLAUDE.md`) before writing bespoke logic; document new dynamic effects in its documentation file as `CLAUDE.md` requires in the same change. Use `meta_effect` where an effect rejects variables (equipment type names, template names).
- Loops over all divisions use `every_country_division` in a bounded country scope; do not add world-wide `on_daily`, `on_weekly` or `on_monthly` iteration without explicit permission.
- A new equipment type, archetype or category also needs `common/script_enums.txt` (`script_enum_equipment_bonus_type`).
- When the project keeps a test country or debug setup, a new land sub-unit, concrete equipment type or similar package registers its setup there in the same change.
- Document each new script file with an overview comment at the top, a docs file for the mechanic, and keep localisation, sprites and `.gfx` registration in the same change.
- Never launch the game for testing; the user performs live validation.

## Common mistakes and silent failures

- Writing an OOB and never registering it: no error, no units.
- `oob =` inside `if`: it is a history argument, not an effect; use `set_oob`.
- `set_oob` or `set_naval_oob` outside country history (in an event or decision): documented as history-only. Use `load_oob` for runtime.
- `load_oob` on a stateless country: nothing happens (observed).
- Re-running `load_oob`: duplicates divisions and templates.
- A template naming a sub-unit that is not unlocked, or placing it in the wrong grid region or past the grid size: entry dropped or template invalid.
- Referencing a template that does not exist in a `division = { division_template = "..." }` block; the OOB wiki says to use the template defined in the same file. Treat template names as exact strings (case and punctuation).
- Mixing legacy and DLC equipment names in one OOB (tank, ship or air equipment from the other system): fails or produces empty units; split files by DLC.
- Ships and variant-based tanks or planes without `version_name`, or with an owner lacking the technology: not created.
- `location` set to a state id instead of a province id (divisions, fleets, task forces use provinces; air wings use state ids): units spawn elsewhere or not at all.
- Air wings in a state with no air base: the wiki says the state should have an air base set.
- `division_cap` on an unlocked template: ignored (wiki).
- Using `start_equipment_factor` expecting stockpile deduction: it does not subtract.
- Hard-coding manpower from deprecated variables: overflow above about 2.1 million.
- Adding a sub-unit and forgetting `unit_modifiers.txt`, category registration, localisation, or sprites: raw keys in tooltips, random icons, modifiers that cannot target it.
- `same_support_type` clashes make a second recon, engineer or similar support impossible to add to a template that already has one.
- `add_units_to_division_template` adds only "if possible" (wiki): a full or out-of-range column likely adds nothing and gives no tooltip, so re-read the template after changing it in test.
- `create_unit` for an owner that lacks the named template: expect no division; guard with `has_template`.
- `division_names_group` pointing to a missing group, or an `ordered` number repeated in a group: wrong or fallback names.
- Treating the wiki numbers as current: the installed game is newer (Army HQ templates, regimental support, deployable generals). Prefer the installed files.

## Validation checklist

Run the checks that can realistically fail for the change; do not report boilerplate.

1. Read the vanilla precedent for each construct used and mirror its structure.
2. For each new sub-unit: unlock path (`active` or `enable_subunits`), `need` keys exist in `common/units/equipment`, categories exist in `common/unit_tags`, `group` valid for its template region, localisation keys, three sprite names, optional `unit_modifiers` registration, AI priority.
3. For each template: every sub-unit exists and is unlockable, `group` matches region, coordinates are unique and in range, `same_support_type` tokens do not clash, name is unique per country, locked or capped flags are intentional, name group exists.
4. For each OOB: registered by exactly one call per branch (land, naval, air), DLC split files exist for both branches, provinces and states exist and are owned by the country, ship variants and airframes exist for the owner, `instant_effect` runs once.
5. For runtime effects: country scope correct, existence guards (`has_template`, state ownership), idempotence flags, hidden effects wrapped with a visible tooltip, no unbounded world loops.
6. Use `hoi4.script_validate` for effect and trigger bodies under their explicit scope when exposed; its true result covers only the listed checks, and engine behaviour remains unproven until the user tests in game.
7. State clearly in the report which statements are source-verified, which come from the wiki only, and which depend on in-game behaviour.
