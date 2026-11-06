# HOI4 Units, Divisions and Orders of Battle: Runtime effects, manpower and AI

Part of the [hoi4-units-divisions](../SKILL.md) skill. Read before spawning, editing or removing units during play, handling manpower, or touching unit leaders, battle plans and AI division templates.

## Runtime effects, triggers and scopes (overview)

Signatures and examples for each are in `references/runtime-effects-triggers.md`. Summary:

- Create: `division_template`, `create_unit`, `create_ship`, `load_oob`, `create_colonial_division_template`.
- Edit templates: `add_units_to_division_template`, `change_division_template`, lock and cap effects.
- Remove or damage: `delete_unit`, `delete_units`, `delete_unit_template_and_units`, `destroy_unit`, `destroy_ships`, `damage_units`.
- Transfer: `transfer_units_fraction`, `transfer_navy`, `transfer_ship`.
- Division scopes: `every_country_division`, `random_country_division`, `every_state_division`, `random_state_division`, and the trigger forms `any_country_division`, `any_state_division`. The scope inside is a division; `owner` returns the country.
- Combatant scope exists only inside combat triggers (traits, abilities, tactics); it is not reachable from ordinary country script.
- Silent behaviours: `create_unit` and `delete_unit` produce no tooltip; wrap with `custom_effect_tooltip` and `hidden_effect`.

## Manpower

- Read manpower through `manpower_k`, `max_manpower_k`, `max_available_manpower_k` (values in thousands), or the `has_manpower` trigger. The plain `manpower`, `max_manpower` and `max_available_manpower` variables are deprecated and overflow at about 2.1 million (`documentation/dynamic_variables_documentation.md`).
- `add_manpower` works in country scope (the pool) and state scope (local manpower). A negative value subtracts.
- Other readable values: `deployed_army_manpower_k`, `deployed_navy_manpower_k`, `deployed_airforce_manpower_k`, `deployed_total_manpower_k`, `amount_manpower_in_deployment_queue`, `foreign_manpower`, `has_army_manpower`, `manpower_per_military_factory`.
- Division creation consumes manpower from the pool unless `start_manpower_factor` limits it; recruiting from the designer is limited by the same pool and `training_time`.
- Never write recomputed manpower numbers into a script as literal magic values; keep them in script constants or variables.

## Unit leaders, battle plans and AI

- Unit leaders (corps commanders, field marshals, admirals) are characters; all definition, trait, recruiting and effect guidance is in `hoi4-characters-leaders`. A division's own commander appears as `officer = {}` in an OOB or through promotion from the division.
- Battle plans (planned attacks, army group orders) are runtime AI and player state. There is no effect to create, issue or cancel a battle plan. The script surface around them is planning bonuses: `add_planning`, `boost_planning` (character scope), `has_max_planning` and `min_planning` (combatant triggers), `planning_skill_level`, and planning modifiers. Do not promise battle-plan automation from script.
- AI composition: `common/ai_templates/*.txt` target templates by `role`; `ai_strategy` types `role_ratio`, `template_prio` and `unit_ratio` set how many divisions per role (`common/ai_strategy/_documentation.md`). Debug with the console commands `imgui show ai_templates` and `imgui show ai_division_production` (`common/ai_templates/_documentation.md`). Use `ai_has_role_template` and `ai_has_role_division` as triggers.
- New sub-units are unknown to AI templates until a target template lists them and `ai_priority` is non-zero. For wider AI weighting and strategy work use the `hoi4-ai-strategies` skill.

