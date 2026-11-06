# Modifiers

<!-- kit:begin id="review" build="1.19.4.1" checked="2026-11-01" revision="102188" sources="documentation/modifiers_documentation.md documentation/effects_documentation.md documentation/triggers_documentation.md documentation/dynamic_variables_documentation.md documentation/console_commands_documentation.md common/dynamic_modifiers/ common/modifier_definitions/ common/modifiers/ common/difficulty_settings/ common/opinion_modifiers/ common/units/unit_modifiers/ common/peace_conference/cost_modifiers/ common/ideas/ common/operations/ localisation/english/modifiers_l_english.yml" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Checked against the modifier documentation (722 modifiers, 38 template families), the dynamic modifier, modifier definition, static modifier, difficulty, opinion modifier and sub-unit modifier files, and the effect, trigger, variable and console documentation.
- Kit blocks added: values and variables, tooltip helpers, dynamic modifier scopes, arguments and add/remove, static, relation, province, balance of power, definition and opinion modifier notes, one table per section for the 167 documented modifiers the page never named, `template-families`, and corrections for sub-unit modifiers, `license_purchase_cost_factor` and the annex and puppet cost note.
- Wiki errors found: sub-unit modifiers exist only when registered, `license_purchase_cost_factor` does not exist, dynamic modifiers also work on special projects, the `scope` claim has no support, annex and puppet cost factors are not removed, several lists are short.
- Gaps left: meanings starting with `~` are guesses; the effect of `scope`, of `days` at or below 0 and of the annex and puppet factors is untested; the Modifier type and scope columns were not re-checked, only the names. The version column was checked on 2026-11-01 as far as the installed files allow (see the note under List of modifiers).
**1.19.4.1 re-check (2026-11-01).** About 40 statements depended on files the update changed, and all were re-measured on the 1.19.4.1 files. Numbers that moved: modifier assignments in ideas 13,384 to 13,444 and in dynamic modifiers 5,097 to 5,092, `custom_modifier_tooltip` 367 to 371 uses, `add_dynamic_modifier` calls 1,549 to 1,552, opinion modifiers 810 to 811, and `navy_screen_attack_factor_against` is now used in `common/ideas/japan.txt`; the meaning column cannot be diffed against the old text file. Every other statement cites files that are byte-identical in 1.19.4.1 (Steam depot manifest diff).
<!-- kit:end id="review" -->

<!-- kit:begin id="modifier-values" at="section:applying-a-modifier" -->
Precision, variables and reading a modifier total.

- Every modifier value accepts up to 3 decimal places. The decimal places shown in the game's modifier documentation (and in the "dp" columns of the tables below) are display only. [docs] `documentation/modifiers_documentation.md`
- A modifier written in an idea, trait or decision never takes a variable. `common/ideas/` holds 13,444 modifier assignments (12,547 in `modifier` blocks and 897 in `targeted_modifier` blocks) and none of them is a variable name or a constant. [vanilla-confirmed 1.19.4.1]
- Outside dynamic modifiers the only non-numeric modifier values in vanilla are `@constant` references: 72 in `common/country_leader/00_traits.txt`, 65 in `common/decisions/` and 5 in `common/military_industrial_organization/`. [vanilla-confirmed 1.19.4.1]
- In `common/dynamic_modifiers/` 4,249 of 5,092 modifier assignments (83 percent) are variable names, so variable values are a dynamic modifier feature. [vanilla-confirmed 1.19.4.1]
- `modifier@token` reads a total in country, state and military industrial organization scope (for example `modifier@military_industrial_organization_research_bonus`), and a state can be addressed by id as `123.modifier@local_manpower`. In unit leader scope use `leader_modifier@token`, `unit_modifier@token` or `sum_unit_terrain_modifier@token`. [docs] `documentation/dynamic_variables_documentation.md`
- `leader_modifier@wounded_chance_factor` is read in `common/on_actions/00_on_actions.txt`. [vanilla-confirmed 1.19.4.1]
- Console: `list_modifiers <scope>` lists the modifiers of the selected country, state or unit leader, and `loc_check_modifiers` checks modifiers for missing localisation. [docs] `documentation/console_commands_documentation.md`
<!-- kit:end id="modifier-values" -->

<!-- kit:begin id="tooltip-vanilla" at="section:tooltip-modification" -->
Vanilla use of the tooltip helpers.

- `custom_modifier_tooltip` appears 371 times in 54 files (ideas, country leader traits, decisions, dynamic modifiers, continuous focuses, faction rules, occupation laws, unit leader and scientist traits, balance of power). `hidden_modifier` appears 20 times in 5 files (ideas, country leader traits, continuous focuses, ideologies). [vanilla-confirmed 1.19.4.1] `common/`
- Dynamic commands in the tooltip text are confirmed: `GER_motor_and_mech_attack_tt: "[GetMotorMechAttack]"` in `localisation/english/wuw_ideas_l_english.yml` is the `custom_modifier_tooltip` of `GER_blitzkrieg_modifier`. [vanilla-confirmed 1.19.4.1]
<!-- kit:end id="tooltip-vanilla" -->

<!-- kit:begin id="dynamic-scopes" at="section:dynamic-modifiers" -->
Dynamic modifiers can also be added to special projects, and the refresh effect is documented.

- `add_dynamic_modifier`, `remove_dynamic_modifier` and `force_update_dynamic_modifier` work in state, country, character (unit leader) and special project scope. The text above names only the first three. [docs] `documentation/effects_documentation.md`
- The header of `common/dynamic_modifiers/0_dynamic_modifiers.txt` says the same ("countries, states, unit leaders or special projects") and says dynamic modifiers are updated daily unless `force_update_dynamic_modifier` forces it. [vanilla-confirmed 1.19.4.1]
- `force_update_dynamic_modifier = yes` refreshes the scope's dynamic modifiers at once. Vanilla calls it three times: twice in `common/national_focus/congo_shared.txt` and once in `common/scripted_effects/PHI_scripted_effects.txt`. [docs] [vanilla-confirmed 1.19.4.1]
- Adding a dynamic modifier that is already present refreshes it ("updates the cooldown if exists"), which matters for timed modifiers. [docs] `documentation/effects_documentation.md`
- `has_dynamic_modifier` tests for one in state, country and character scope. It takes either `has_dynamic_modifier = name` or a block with `modifier` and an optional `scope`. [docs] `documentation/triggers_documentation.md`
- Vanilla defines 679 dynamic modifiers in 11 files under `common/dynamic_modifiers/`. [vanilla-confirmed 1.19.4.1]
- The console documentation lists no command that reloads dynamic modifier definitions. [docs] `documentation/console_commands_documentation.md` That fits the restart claim above but does not prove it. [unverified]
<!-- kit:end id="dynamic-scopes" -->

<!-- kit:begin id="dynamic-arguments" at="section:arguments" -->
What vanilla puts inside a dynamic modifier.

- The header of `common/dynamic_modifiers/0_dynamic_modifiers.txt` lists four optional keys and nothing else: `icon` (shown in GUIs only when given), `enable`, `remove_trigger` and `attacker_modifier`. Everything else in the block is a modifier. [vanilla-confirmed 1.19.4.1]
- `attacker_modifier = yes` is used once in vanilla, by `unplanned_offensive` in `0_dynamic_modifiers.txt` (with `army_attack_factor = -0.9` and `army_speed_factor = -0.75`). [vanilla-confirmed 1.19.4.1]
- A value can be a plain number or a variable name: `max_fuel = var_max_fuel` (header example), a scope-prefixed variable such as `global.HABSBURG_army_war_stability_factor` (`common/dynamic_modifiers/HABSBURG_dynamic_modifiers.txt`), or `temporary_state_resource_oil = sabotaged_oil` (`0_dynamic_modifiers.txt`). 843 of the 5,092 assignments are plain numbers. [vanilla-confirmed 1.19.4.1]
- `custom_modifier_tooltip` is used inside dynamic modifiers in 8 files. [vanilla-confirmed 1.19.4.1]
<!-- kit:end id="dynamic-arguments" -->

<!-- kit:begin id="dynamic-add-remove" at="section:adding-a-dynamic-modifier" -->
Parameters of the effect, and what `scope` really does.

| Key | Meaning | Source |
| --- | --- | --- |
| `modifier` | Name from `common/dynamic_modifiers/`. | [docs] `documentation/effects_documentation.md` |
| `days` | Optional. Makes the modifier temporary. May be a variable. | [docs] `documentation/effects_documentation.md` |
| `scope` | Optional. A state, a country tag or a variable holding one. | [docs] `documentation/effects_documentation.md` |

- The documentation example adds a modifier to state 12 with `scope = GER` and says it is added to the state "but only applies for country GER". Nothing in the documentation or in the header comment says the variables are read from the `scope` target, which is what the wiki text above claims. [docs] `documentation/effects_documentation.md`
- Vanilla uses `scope` to restrict who a state modifier applies to. `GER_blitzkrieg_modifier` is added in `every_state` with `scope = GER` in `common/decisions/GER.txt`, and its values are constants. `scope = THIS.owner` is used the same way in `common/decisions/CHL.txt`. [vanilla-confirmed 1.19.4.1]
- The variables are read off the `scope` country, as the wiki text above claims. With the variable at 0.1 for GER, 0.3 for ENG and 0.5 for NEP, a state owned by GER that got the modifier with `scope = ENG` read ENG's 0.3, and a state with `scope = GER` read GER's 0.1. A state modifier added with no `scope` read 0, not its owner's variable. A country modifier with no `scope` read the country's own variable (NEP 0.5). The values were identical when read at once and two days later. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, read back through a custom modifier with `modifier@`, not the tooltip. The engine also wrote "Token ... is a dynamic token, this can cause OOS", a multiplayer warning.
- `remove_dynamic_modifier` and `has_dynamic_modifier` need the same `scope` that `add_dynamic_modifier` used. [docs] `documentation/effects_documentation.md` One id can be bound to two scopes on the same state at once. After `add_dynamic_modifier` with `scope = GER` and again with `scope = ENG` on one state, `has_dynamic_modifier` with each scope read TRUE, the second add did not replace the first, and the console tooltip listed both bindings. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, effect run from the console, game.log read, no error.log line. The tooltip text is from OCR, and one state was used.
- Vanilla has 1,552 `add_dynamic_modifier` calls (1,217 in `common/`, 147 in `events/`, 188 in `history/`). 175 pass `days` (168 positive numbers and 7 use the variable `duration`) and 142 pass `scope`. No call passes a negative `days`, and `remove_dynamic_modifier` appears 730 times. What a zero or negative `days` does is not shown. [vanilla-confirmed 1.19.4.1]
- The usual timed form in vanilla:

```text
add_dynamic_modifier = {
    modifier = GER_blitzkrieg_modifier
    scope = GER
    days = 45
}
```
<!-- kit:end id="dynamic-add-remove" -->

<!-- kit:begin id="static-files" at="section:static-modifiers" -->
Where vanilla keeps them.

- `common/modifiers/` holds `00_static_modifiers.txt` (global, weather, resistance and compliance, stability, difficulty, intelligence, relation and country-specific modifiers), `01_event_modifiers.txt` (an empty file) and three balance of power files: `AAT_power_balance_modifiers.txt`, `BBA_power_balance_modifiers.txt` and `MUN_power_balance_modifiers.txt`. [vanilla-confirmed 1.19.4.1]
- The header of `00_static_modifiers.txt` says the names are used by code and cannot be removed or renamed. [vanilla-confirmed 1.19.3]
- Some global modifiers are targeted. The comments in `00_static_modifiers.txt` say `passive_decryption_modifier` applies once a country's cipher is fully decrypted and `active_decryption_modifier` applies while active decryption bonuses are used against it. [vanilla-confirmed 1.19.3]
<!-- kit:end id="static-files" -->

<!-- kit:begin id="difficulty-vanilla" at="section:difficulty-modifiers" -->
Vanilla has one file, `common/difficulty_settings/00_difficulty.txt`, with 8 settings. Each uses a quoted key such as `key = "custom_diff_strong_ger"`, `modifier = diff_strong_ai_generic` (defined in `00_static_modifiers.txt`) and `multiplier = 2.0`. `weaken_country` in the example above is not a vanilla modifier. [vanilla-confirmed 1.19.3]
<!-- kit:end id="difficulty-vanilla" -->

<!-- kit:begin id="relation-vanilla" at="section:relation-modifiers" -->
Relation modifiers in vanilla and their trigger.

- 18 relation modifiers are defined in `common/modifiers/00_static_modifiers.txt` (every entry with a `valid_relation_trigger`), for example `ROM_license_german_equipment`, `free_license` and `SOV_soviet_chinese_relations`. `ROM_license_german_equipment` sets `license_purchase_cost`, `ai_license_acceptance`, `license_production_speed` and `license_tech_difference_speed`. [vanilla-confirmed 1.19.4.1]
- `add_relation_modifier` is called 55 times in vanilla, `remove_relation_modifier` and `has_relation_modifier` 4 times each. [vanilla-confirmed 1.19.4.1]
- `has_relation_modifier = { target = TAG modifier = name }` is the trigger. Effects and trigger run in country scope. [docs] `documentation/effects_documentation.md` `documentation/triggers_documentation.md`
<!-- kit:end id="relation-vanilla" -->

<!-- kit:begin id="province-params" at="section:province-modifiers" -->
Parameters of the effects (scope: state).

- `add_province_modifier` takes `static_modifiers = { mod_1 mod_2 }`, an optional `days` (temporary, may be a variable) and a province selector: `province = 500`, or `province = { ... }` with repeated `id = N`, `all_provinces`, `limit_to_coastal`, `limit_to_border`, `limit_to_naval_base` and `limit_to_victory_point`. `remove_province_modifier` takes the same selectors. [docs] `documentation/effects_documentation.md`
- Vanilla calls `add_province_modifier` 21 times and `remove_province_modifier` 7 times, for example `static_modifiers = { flooded }` with `province = { id = 9498 id = 391 }` in `common/decisions/HOL.txt`. [vanilla-confirmed 1.19.4.1]
- Static modifiers marked `# on Province` in `00_static_modifiers.txt` include `weather_mud`, `weather_extreme_cold`, `flooded` and `unplanned_offensive`. [vanilla-confirmed 1.19.3]
<!-- kit:end id="province-params" -->

<!-- kit:begin id="bop-modifiers" at="section:balance-of-power-modifiers" -->
Effects, trigger and console commands.

- `add_power_balance_modifier = { id = ... modifier = ... }` runs in any scope. The modifier "must be defined in the static modifier database". `remove_power_balance_modifier` takes the same keys and `remove_all_power_balance_modifiers = { id = ... }` takes only the id. `has_power_balance_modifier` tests for one. [docs] `documentation/effects_documentation.md` `documentation/triggers_documentation.md`
- Console: `bop_addmod <ID> <ModID>` and `bop_rmmod <ID> <ModID>`. [docs] `documentation/console_commands_documentation.md`
- Vanilla calls `add_power_balance_modifier` 38 times and `remove_power_balance_modifier` 61 times. The only definition in `00_static_modifiers.txt` is the test entry `_test_power_balance_mod` (`power_balance_daily = 0.02`). [vanilla-confirmed 1.19.4.1]
<!-- kit:end id="bop-modifiers" -->

<!-- kit:begin id="definitions-defaults" at="section:modifier-definitions" -->
Defaults and vanilla use, from the header of `common/modifier_definitions/modifier_definitions.txt`.

| Key | Allowed values | Default |
| --- | --- | --- |
| `color_type` | `good`, `neutral`, `bad` | `bad` |
| `value_type` | `number`, `percentage`, `percentage_in_hundred`, `yes_no` | `number` |
| `precision` | decimals shown in the tooltip, up to 3 | not stated |
| `postfix` | `none`, `days`, `hours`, `daily` | `none` |
| `category` | `none`, `all`, `naval`, `air`, `unit_leader`, `country`, `state`, `army`, `peace`, `politics`, `ai`, `defensive`, `aggressive`, `war_production`, `military_advancements`, `military_equipment`, `autonomy`, `government_in_exile`, `intelligence_agency` (repeat the key for several) | `all` |

All rows: [vanilla-confirmed 1.19.3] `common/modifier_definitions/modifier_definitions.txt`.

- The header says the game itself never uses these definitions: read them with `modifier@token` (state and country), or `leader_modifier@token` and `unit_modifier@token` (unit leader). The token doubles as the localisation key. [vanilla-confirmed 1.19.3]
- Vanilla defines only three, all in `common/modifier_definitions/lar_operation_modifiers_pre_definition.txt`: `operation_outcome`, `operation_cost` and `operation_infiltrate_outcome`, with the comment that modifiers used in static modifiers must be predefined there. [vanilla-confirmed 1.19.3]
- The modifier documentation also uses the categories `faction`, `character` and `scientist`. [docs] `documentation/modifiers_documentation.md`
- The definition header lists none of those three. [vanilla-confirmed 1.19.3] Only `scientist` is accepted in a definition. In a test file `category = scientist` and `category = state` loaded with no error.log line, while `category = faction` and `category = character` were each rejected at load as "Unexpected token: category", the same error a made-up category got. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, error.log read at load, line numbers mapped to the generated file. `scientist` counts as accepted only because no error line appeared, and the modifier was not read back.
<!-- kit:end id="definitions-defaults" -->

<!-- kit:begin id="opinion-vanilla" at="section:opinion-modifiers" -->
What vanilla actually uses.

- The header of `common/opinion_modifiers/00_opinion_modifiers.txt` lists `value`, `min_trust`, `max_trust`, `decay`, `months`/`years`/`days` and `trade`, and no other keys. [vanilla-confirmed 1.19.3]
- 811 opinion modifiers are defined in 13 files, with 794 distinct ids, so 17 ids are defined twice. Key use: `value` 811, `months` 258, `trade` 58, `years` 55, `decay` 41, and `days`, `min_trust` and `max_trust` once each. [vanilla-confirmed 1.19.4.1]
- `target = yes` appears once, on the second `guarantee` entry (`value = 35`, in `00_opinion_modifiers.txt`) next to a plain `guarantee` with `value = 0`. It is not in the header. [vanilla-confirmed 1.19.4.1] What it does is not shown. [unverified]
- Vanilla examples of the bounds: `justifying_war_goal = { value = -10 min_trust = -10 days = 10 decay = 1 }` and `improve_relation = { value = 0 months = 0 decay = 3 max_trust = 100 }`. [vanilla-confirmed 1.19.3]
- The localisation key is the modifier id, for example `holds_our_cores:` in `localisation/english/diplomacy_l_english.yml`. [vanilla-confirmed 1.19.4.1]
<!-- kit:end id="opinion-vanilla" -->

<!-- kit:begin id="opinion-effects" at="section:implementation" -->
Vanilla calls: `add_opinion_modifier` 2,266, `reverse_add_opinion_modifier` 89, `remove_opinion_modifier` 151 and `has_opinion_modifier` 98. All four run in country scope. [vanilla-confirmed 1.19.4.1] [docs] `documentation/effects_documentation.md` `documentation/triggers_documentation.md`
<!-- kit:end id="opinion-effects" -->

<!-- kit:begin id="list-outdated" at="heading:list-of-modifiers" -->
The tables below are incomplete for 1.19.3. The game documents 722 plain modifiers and 38 template families (`production_speed_<Building>_factor` and similar). 167 of the 722 are never named on this page; the tables under each section add them. [docs] `documentation/modifiers_documentation.md`
<!-- kit:end id="list-outdated" -->

<!-- kit:begin id="added-tables-legend" at="section:list-of-modifiers" -->
### How the added tables read

- Modifier, Categories and Format come from the game documentation. `dp` is the number of decimals the tooltip shows; any value accepts up to 3 decimals. [docs] `documentation/modifiers_documentation.md`
- Meaning is the in-game wording from `localisation/english/modifiers_l_english.yml` and the MIO and effect strings, paraphrased. [vanilla-confirmed 1.19.3] The text file changed in 1.19.4.1 and the old text is gone, so a reworded single row would not show. A word-overlap check of the meaning column against the new file found no row that contradicts it. [unverified]
- A meaning that starts with `~` is a guess from the name and its vanilla use. [unverified]
- An empty meaning means the name is self-explanatory. `(not described in the docs)` means there is no in-game text and no clear vanilla use.
- "Unused in vanilla" means no `key = value` use in `common/`, `events/` or `history/`. [vanilla-confirmed 1.19.4.1]
- Sample checks against vanilla use: `army_non_core_attack_factor` is negative in `common/ideas/australia.txt`; `naval_invasion_prep_days` is -5 and -10 in `special_forces_subdoctrines.txt` and `MTG_naval_Support.txt`; `army_intel_to_others` is -15 and -50 in a trait and a decision; `peace_score_ratio_transferred_to_players` is used by the `diff_*_ai` static modifiers; `river_crossing_factor_against` sits inside `targeted_modifier` in `common/ideas/GER.txt`. [vanilla-confirmed 1.19.4.1]
<!-- kit:end id="added-tables-legend" -->

<!-- kit:begin id="template-families" at="section:list-of-modifiers" -->
### Template modifier families

The documentation lists these as template entries; each pattern stands for one modifier per slot value. Several wiki rows below name only some of the values. All rows: [docs] `documentation/modifiers_documentation.md`

| Pattern | Categories | Format | What fills the slot |
| --- | --- | --- | --- |
| `<Building>_max_level_terrain_limit`<br>`state_<Building>_max_level_terrain_limit` | country<br>state | 0 dp | Two forms: a building token (54 tokens, for example `bunker`) or a building plus a terrain (770 tokens, for example `bunker_hills`). |
| `production_cost_<Building>_factor`<br>`production_speed_<Building>_factor`<br>`repair_speed_<Building>_factor` | country | 2 dp | 55 building tokens, listed below the table. |
| `state_production_speed_<Building>_factor`<br>`state_repair_speed_<Building>_factor` | state | 2 dp | The same 55 building tokens. |
| `country_resource_<Resource>`<br>`country_resource_cost_<Resource>`<br>`local_resources_<Resource>_factor` | country | 0 dp | 7 resources: `aluminium`, `chromium`, `coal`, `oil`, `rubber`, `steel`, `tungsten`. |
| `state_resource_<Resource>`<br>`state_resource_cost_<Resource>`<br>`temporary_state_resource_<Resource>`<br>`state_resources_<Resource>_factor` | state | 0 dp | The same 7 resources. |
| `experience_gain_<Unit>_combat_factor`<br>`experience_gain_<Unit>_mission_factor`<br>`experience_gain_<Unit>_training_factor` | naval, country | 0 dp | 157 unit tokens: sub-units, ships and aircraft (for example `infantry`, `armored_car`, `destroyer`, `fighter`). The documentation lists three variants (combat, mission, training); the wiki tables name only combat and training. |
| `unit_<Unit>_design_cost_factor` | naval, country, army | 2 dp | The same 157 unit tokens. |
| `<Equipment>_design_cost_factor` | country | 0 dp | 195 equipment, chassis and airframe tokens (for example `infantry_equipment`, `light_tank_chassis`, `medium_plane_fighter_airframe_2`). |
| `module_<EquipmentModule>_design_cost_factor` | naval, country, army | 2 dp | 312 equipment module tokens (for example `engine_1_1x`, `armor_plate_large`). |
| `production_cost_max_<NavalEquipment>` | naval | 0 dp | 9 tokens: `convoy`, `floating_harbor_equipment`, `repair_ship_hull`, `ship_hull_carrier`, `ship_hull_cruiser`, `ship_hull_heavy`, `ship_hull_light`, `ship_hull_submarine`, `support_ship_hull`. |
| `<Doctrine>_mastery_gain_factor` | country | 0 dp | Three kinds of token: the 4 doctrine folders (`air`, `land`, `naval`, `special_forces`), 12 grand doctrines and 95 sub-doctrines. |
| `<Doctrine>_track_mastery_gain_factor` | country | 0 dp | 14 tracks: `armor`, `capital_ships`, `carriers`, `combat_support`, `fighter_aircraft`, `heavy_aircraft`, `infantry`, `medium_aircraft`, `operations`, `screens`, `special_forces_first`, `special_forces_second`, `strike_aircraft`, `submarines`. |
| `<Technology>_cost_factor` | country | 0 dp | 39 technology category tokens, all starting with `cat_` (for example `cat_mobile_warfare`, `cat_synth_oil`, `cat_torpedoes`). Not limited to doctrines. |
| `<IdeaGroup>_cost_factor` | country | 0 dp | 25 idea groups (for example `economy`, `army_chief`, `hidden_ideas`, `army_spirit`). |
| `<IdeaCategory>_category_type_cost_factor` | country | 0 dp | `air_spirit`, `army_spirit`, `navy_spirit`. |
| `<Ideology>_acceptance`<br>`<Ideology>_drift`<br>`<Ideology>_drift_from_guarantees` | politics | 0 dp, 2 dp, 2 dp | `communism`, `democratic`, `fascism`, `neutrality`. |
| `<Operation>_cost`<br>`<Operation>_outcome`<br>`<Operation>_risk` | intelligence_agency | 0 dp | 41, 39 and 42 slot values: operation ids from `common/operations/` (for example `operation_infiltrate_civilian`, `bruneval_raid`, `FRA_coup_in_indochina`) plus the generic tokens `operation`, `operation_coup`, `operation_infiltrate`, `operation_steal_tech` and `target_sabotage`. The three sets differ slightly: `_cost` has no `operation_steal_tech`, and `_outcome` and `_risk` have no `operation_coup`. Which of them vanilla operations read is in the note below the table. |
| `<SpecialProject>_speed_factor` | country, state | 0 dp | 66 tokens: the `sp_*` projects and `specialization_air`, `specialization_land`, `specialization_naval`, `specialization_nuclear`. |
| `<Trait>_xp_gain_factor` | naval, country, army | 2 dp | For 29 unit leader traits whose token already starts with `trait_` (for example `trait_cautious`, giving `trait_cautious_xp_gain_factor`). |
| `trait_<Trait>_xp_gain_factor` | naval, country, army | 2 dp | For 165 traits whose token has no `trait_` prefix (for example `BALTIC_anti_bolshevik`). |
| `<CombatTactic>_preferred_weight_factor` | country | 2 dp | 56 tokens: `nullCombatTactic` and the `tactic_*` combat tactics. The documentation text calls it a naval weight. |
| `<ModifierStat>_factor`<br>`<ModifierStatValue>_value_factor` | country, state | 0 dp | Only `naval_general_support` and `naval_repair_support`, the support-ratio static modifiers in `common/modifiers/00_static_modifiers.txt`. (not described in the docs) |

Notes on rows of the table above:

- `<Operation>_cost`, `<Operation>_outcome`, `<Operation>_risk`: An operation only reacts to a modifier it names in its own `cost_modifiers`, `outcome_modifiers` or `risk_modifiers` list (`common/operations/_documentation.md`) [docs]. Vanilla operations name only `operation_cost`, `operation_infiltrate_cost`, `operation_coup_cost`, `target_sabotage_cost`, `operation_outcome`, `operation_infiltrate_outcome`, `operation_steal_tech_outcome`, `boost_resistance_factor`, `target_sabotage_factor`, `operation_risk`, `operation_infiltrate_risk`, `operation_steal_tech_risk` and `target_sabotage_risk`, so per-operation names such as `bruneval_raid_cost` are valid but no vanilla operation reads them in `common/operations/` [vanilla-confirmed 1.19.4.1].

The 55 building tokens:

```text
air_base, air_facility, anti_air_building, arms_factory, bunker, canal_kiel, canal_panama,
cataract_dam_mountain, coastal_bunker, commercial_nuclear_reactor, dam, dam_mountain, dockyard,
energy_infrastructure, fuel_silo, industrial_complex, industrial_infrastructure,
infrastructure, land_facility, landmark_berlin_reichstag, landmark_berlin_volkshalle,
landmark_big_ben, landmark_bojnice_castle, landmark_colosseum, landmark_cristo_redentor,
landmark_eiffel_tower, landmark_forbidden_city, landmark_great_wall_section,
landmark_hagia_sophia, landmark_hakko_ichiu, landmark_hofburg_palace, landmark_kremlin,
landmark_nanjing_presidential_palace, landmark_nanjing_presidential_palace_gen,
landmark_nanjing_presidential_palace_prc, landmark_national_diet, landmark_prague_castle,
landmark_sadabad_complex, landmark_statue_of_liberty, landmark_taj_mahal,
landmark_tokyo_imperial_palace, mega_gun_emplacement, naval_base, naval_facility,
naval_headquarters, naval_supply_hub, nuclear_facility, nuclear_reactor,
nuclear_reactor_heavy_water, radar_station, rail_way, rocket_site, stronghold_network,
supply_node, synthetic_refinery
```

Corrections to the rows below. [docs] `documentation/modifiers_documentation.md`

- Resources: there are 7, and `coal` exists for every resource pattern.
- Buildings: `production_speed_<building>_factor`, `repair_speed_<building>_factor`, `production_cost_<building>_factor` and the `state_` variants take 55 tokens, including `air_facility`, `land_facility`, `naval_facility`, `nuclear_facility`, `energy_infrastructure`, `supply_node` and the landmarks.
- Tracks: `<doctrine track>_track_mastery_gain_factor` also accepts `special_forces_first` and `special_forces_second`.
- Mastery: `<land/air/naval>_mastery_gain_factor` also accepts `special_forces`, every grand doctrine and every sub-doctrine.
- Technology cost: `<doctrine category>_cost_factor` is the `<Technology>_cost_factor` family and takes any of the 39 `cat_*` technology categories, not only doctrines.
<!-- kit:end id="template-families" -->

<!-- kit:begin id="version-added-column" at="section:list-of-modifiers" -->
**The "Version added" column.** The column is the wiki's claim. No installed file records when a modifier was added (`changelog.txt` only links to the forum), and the documentation names no versions. [vanilla-confirmed 1.19.4.1] `changelog.txt`, `documentation/`. No modifier was added or removed in 1.19.4. [docs] `documentation/modifiers_documentation.md`

- Rows with no usable version: the cell is blank for `land`, `state_bunker_max_level_terrain_limit` and `state_coastal_bunker_max_level_terrain_limit`, says `Unknown` for the `production_cost_` row and `???` for the three `modifier_army_sub_unit_` rows. In the `idea` row, other wiki text has slipped into the column.
<!-- kit:end id="version-added-column" -->

<!-- kit:begin id="add-gen" at="section:general" -->
Documented modifiers this section does not list (5). Format and meaning columns are explained under [How the added tables read](#how-the-added-tables-read). [docs] `documentation/modifiers_documentation.md`

| Modifier | Categories | Format | Meaning |
| --- | --- | --- | --- |
| `energy_gain_factor` | country | 2 dp | Energy gained per unit of coal |
| `energy_scale_per_trade_factory_export_factor` | country | 2 dp | How much traded factories affect factory energy usage (unused in vanilla) |
| `special_project_facility_supply_consumption_factor` | country | 2 dp | Supply used by special project facilities |
| `thermonuclear_production` | country | bool | Allows thermonuclear bombs |
| `thermonuclear_production_factor` | country | 0 dp | Thermonuclear bomb production rate |
<!-- kit:end id="add-gen" -->

<!-- kit:begin id="add-pol" at="section:politics" -->
Documented modifiers this section does not list (2). Format and meaning columns are explained under [How the added tables read](#how-the-added-tables-read). [docs] `documentation/modifiers_documentation.md`

| Modifier | Categories | Format | Meaning |
| --- | --- | --- | --- |
| `army_advisor_cost_factor` | army | 0 dp |  |
| `navy_advisor_cost_factor` | naval | 0 dp |  |
<!-- kit:end id="add-pol" -->

<!-- kit:begin id="add-dip" at="section:diplomacy" -->
Documented modifiers this section does not list (7). Format and meaning columns are explained under [How the added tables read](#how-the-added-tables-read). [docs] `documentation/modifiers_documentation.md`

| Modifier | Categories | Format | Meaning |
| --- | --- | --- | --- |
| `annex_subject_cost_factor` | country | 2 dp |  |
| `can_guarantee_other_ideologies` | country | bool | Allows guaranteeing countries of other ideologies; the same name is also a `rule` in ideas and ideologies |
| `faction_influence_contribution_factor` | faction | 2 dp | Influence gained in a faction from contribution |
| `faction_influence_war_score_factor` | faction | 2 dp | Influence gained in a faction from war score |
| `faction_subject_contribution_gain` | faction | 2 dp | Reduction in contribution gain caused by being a subject |
| `peace_score_ratio_transferred_to_overlord` | peace | 2 dp | Share of a puppet's peace score that goes to its overlord |
| `peace_score_ratio_transferred_to_players` | peace | 2 dp | Share of AI countries' peace score that goes to human players |
<!-- kit:end id="add-dip" -->

<!-- kit:begin id="annex-puppet-status" at="section:diplomacy" -->
The table says `annex_cost_factor` and `puppet_cost_factor` are "partially deprecated". In 1.19.4.1 both are still documented (`annex_cost_factor`: categories peace, aggressive; `puppet_cost_factor`: peace, defensive) and the in-game text still reads "Changes the cost of annexing a country" and "Changes the cost of puppeting a country". [docs] `documentation/modifiers_documentation.md` [vanilla-confirmed 1.19.4.1] `localisation/english/modifiers_l_english.yml`

- Vanilla still sets them: `annex_cost_factor` 22 times in 12 files and `puppet_cost_factor` 21 times in 6 files (country leader traits, balance of power, dynamic modifiers, ideas). [vanilla-confirmed 1.19.4.1]
- `common/peace_conference/cost_modifiers/` is a separate system. Each entry has a `peace_action_type`, an `enable` trigger and a `cost_multiplier` greater than 0, and all active multipliers are multiplied together. [docs] `common/peace_conference/cost_modifiers/_documentation.md`
- No file in `common/peace_conference/` mentions either modifier name. Whether the two modifiers still change peace conference costs is not shown by the files. [vanilla-confirmed 1.19.4.1] [unverified]
<!-- kit:end id="annex-puppet-status" -->

<!-- kit:begin id="add-aut" at="section:autonomy" -->
Documented modifiers this section does not list (2). Format and meaning columns are explained under [How the added tables read](#how-the-added-tables-read). [docs] `documentation/modifiers_documentation.md`

| Modifier | Categories | Format | Meaning |
| --- | --- | --- | --- |
| `autonomy_manpower_share_from_subjects` | autonomy | 2 dp | Amount of manpower demanded from subject forces |
| `resources_to_overlord_factor` | autonomy | 2 dp |  |
<!-- kit:end id="add-aut" -->

<!-- kit:begin id="add-eqp" at="section:equipment" -->
Documented modifiers this section does not list (15). Format and meaning columns are explained under [How the added tables read](#how-the-added-tables-read). [docs] `documentation/modifiers_documentation.md`

| Modifier | Categories | Format | Meaning |
| --- | --- | --- | --- |
| `license_air_purchase_cost` | country | 0 dp |  |
| `license_anti_tank_eq_cost_factor` | country | 0 dp |  |
| `license_anti_tank_eq_production_speed_factor` | country | 0 dp |  |
| `license_anti_tank_eq_tech_difference_speed_factor` | country | 0 dp |  |
| `license_armor_purchase_cost` | country | 0 dp |  |
| `license_artillery_eq_cost_factor` | country | 0 dp |  |
| `license_artillery_eq_production_speed_factor` | country | 0 dp |  |
| `license_artillery_eq_tech_difference_speed_factor` | country | 0 dp |  |
| `license_infantry_eq_cost_factor` | country | 0 dp |  |
| `license_infantry_eq_tech_difference_speed_factor` | country | 0 dp |  |
| `license_infantry_purchase_cost` | country | 0 dp |  |
| `license_light_tank_eq_cost_factor` | country | 0 dp |  |
| `license_light_tank_eq_production_speed_factor` | country | 0 dp |  |
| `license_light_tank_eq_tech_difference_speed_factor` | country | 0 dp |  |
| `license_naval_purchase_cost` | country | 0 dp |  |
<!-- kit:end id="add-eqp" -->

<!-- kit:begin id="license-cost-factor-removed" at="section:equipment" -->
The two `license_purchase_cost_factor` rows name a modifier that is not in 1.19.4.1. The name is absent from the modifier documentation [docs] `documentation/modifiers_documentation.md` and from all vanilla script and localisation [vanilla-confirmed 1.19.4.1]. A read-only search of `hoi4.exe` finds no string either. [unverified] The game rejects it: in an idea's `modifier` block it drew "Unknown modifier: license_purchase_cost_factor", and read back by name it gave 0. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, error.log read at load and the modifier read in game.log.

The documented names are `license_purchase_cost` (all licences), `license_air_purchase_cost`, `license_armor_purchase_cost`, `license_infantry_purchase_cost` and `license_naval_purchase_cost` (by category), and `license_<archetype>_eq_cost_factor`, `license_<archetype>_eq_production_speed_factor` and `license_<archetype>_eq_tech_difference_speed_factor` for `anti_tank`, `artillery`, `infantry` and `light_tank`. Production speed is `license_production_speed` and `license_tech_difference_speed`. [docs] `documentation/modifiers_documentation.md`
<!-- kit:end id="license-cost-factor-removed" -->

<!-- kit:begin id="add-fuel" at="section:fuel-and-supply" -->
Documented modifiers this section does not list (3). Format and meaning columns are explained under [How the added tables read](#how-the-added-tables-read). [docs] `documentation/modifiers_documentation.md`

| Modifier | Categories | Format | Meaning |
| --- | --- | --- | --- |
| `naval_supply_consumption_factor` | naval, defensive, aggressive | 1 dp | Supplies our fleets need to operate |
| `underway_replenishment_convoy_cost` | country | 2 dp | Convoys used to provide underway replenishment |
| `underway_replenishment_range` | country | 2 dp | How far underway replenishment extends fleet range |
<!-- kit:end id="add-fuel" -->

<!-- kit:begin id="add-bld" at="section:buildings" -->
Documented modifiers this section does not list (5). Format and meaning columns are explained under [How the added tables read](#how-the-added-tables-read). [docs] `documentation/modifiers_documentation.md`

| Modifier | Categories | Format | Meaning |
| --- | --- | --- | --- |
| `industrial_capacity_dockyard_powered` | country, war_production | 2 dp | Output of powered dockyards |
| `industrial_capacity_factory_powered` | country, war_production | 2 dp | Output of powered factories |
| `out_of_power_impact_factor` | country, war_production | 2 dp | Reduces the penalties from lack of power |
| `production_speed_buildings_powered_factor` | country, war_production | 2 dp | Construction speed of powered buildings (unused in vanilla) |
| `production_speed_facility_factor` | country | 2 dp | Construction speed of all facilities |
<!-- kit:end id="add-bld" -->

<!-- kit:begin id="add-int" at="section:intelligence" -->
Documented modifiers this section does not list (15). Format and meaning columns are explained under [How the added tables read](#how-the-added-tables-read). [docs] `documentation/modifiers_documentation.md`

| Modifier | Categories | Format | Meaning |
| --- | --- | --- | --- |
| `airforce_intel_decryption_bonus` | intelligence_agency | 0 dp | ~ Extra air intel once an enemy cipher is decrypted (used in passive_decryption_modifier and active_decryption_modifier) |
| `airforce_intel_factor` | intelligence_agency | 0 dp | ~ Scales the agency's air force intelligence |
| `airforce_intel_to_others` | country | 1 dp | ~ Air force intel other countries get about us (negative hides us) |
| `army_intel_decryption_bonus` | intelligence_agency | 0 dp | ~ Extra army intel once an enemy cipher is decrypted (used in passive_decryption_modifier and active_decryption_modifier) |
| `army_intel_factor` | intelligence_agency | 0 dp | ~ Scales the agency's army intelligence |
| `army_intel_to_others` | country | 1 dp | ~ Army intel other countries get about us (negative hides us) |
| `boost_resistance_factor` | intelligence_agency | 0 dp | Strengthen Resistance mission efficiency |
| `civilian_intel_factor` | intelligence_agency | 0 dp | ~ Scales the agency's civilian intelligence |
| `control_trade_mission_factor` | intelligence_agency | 0 dp | Control Trade mission effects |
| `diplomatic_pressure_mission_factor` | intelligence_agency | 0 dp | Diplomatic Pressure mission effects |
| `intelligence_operation_speed` | intelligence_agency | 0 dp | Operation speed factor (unused in vanilla) |
| `navy_intel_decryption_bonus` | intelligence_agency | 0 dp | ~ Extra navy intel once an enemy cipher is decrypted (used in passive_decryption_modifier and active_decryption_modifier) |
| `navy_intel_to_others` | country | 1 dp | ~ Navy intel other countries get about us (negative hides us) |
| `operation_infiltrate_outcome` | intelligence_agency | 0 dp | Infiltration operation effectiveness (defined in modifier_definitions) |
| `propaganda_mission_factor` | intelligence_agency | 0 dp | Propaganda mission effects |
<!-- kit:end id="add-int" -->

<!-- kit:begin id="add-mil" at="section:military-outside-of-combat" -->
Documented modifiers this section does not list (5). Format and meaning columns are explained under [How the added tables read](#how-the-added-tables-read). [docs] `documentation/modifiers_documentation.md`

| Modifier | Categories | Format | Meaning |
| --- | --- | --- | --- |
| `air_doctrine_cost_factor` | country | 2 dp |  |
| `army_experience_from_volunteers` | army | 1 dp |  |
| `naval_doctrine_cost_factor` | country | 2 dp |  |
| `special_forces_doctrine_cost_factor` | country | 2 dp |  |
| `training_time_army` | army, war_production | 1 dp | Division training time (unused in vanilla) |
<!-- kit:end id="add-mil" -->

<!-- kit:begin id="add-ldr" at="section:unit-leaders" -->
Documented modifiers this section does not list (2). Format and meaning columns are explained under [How the added tables read](#how-the-added-tables-read). [docs] `documentation/modifiers_documentation.md`

| Modifier | Categories | Format | Meaning |
| --- | --- | --- | --- |
| `automatic_grant_medal_chance` | country | 0 dp | ~ Chance that a medal is granted automatically |
| `unit_medal_effectiveness` | country | 0 dp | ~ Strength of the bonuses that unit medals give |
<!-- kit:end id="add-ldr" -->

<!-- kit:begin id="fix-sub-unit-modifiers" at="section:land-combat" -->
The `modifier_army_sub_unit_<unit type>_*` rows say any defined battalion works. In 1.19.3 only the modifiers listed in `sub_unit_modifiers = { ... }` in `common/units/unit_modifiers/unit_modifiers.txt` exist, and the documentation names exactly those 54. To get one for a mod battalion, add its names to that block. [vanilla-confirmed 1.19.3] [docs] `documentation/modifiers_documentation.md`

The stats are `_attack_factor`, `_defence_factor`, `_speed_factor`, `_max_org_factor` and `_org_recovery_cap_factor`. The file marks the speed and max organisation modifiers of `armored_car_recon`, `light_tank_recon` and `blackshirt_assault_battalion` "Cannot be applied to support battalions". Two entries use a sub-unit category instead of a sub-unit: `category_special_forces` (max organisation only) and `category_rocket_artillery` (attack only). All 54 rows: categories `army`, format 2 dp. [vanilla-confirmed 1.19.3]

| Sub-unit token | Attack | Defence | Speed | Max organisation | Organisation recovery cap |
| --- | --- | --- | --- | --- | --- |
| `armored_car` | `modifier_army_sub_unit_armored_car_attack_factor` | `modifier_army_sub_unit_armored_car_defence_factor` | `modifier_army_sub_unit_armored_car_speed_factor` | `modifier_army_sub_unit_armored_car_max_org_factor` |  |
| `armored_car_recon` | `modifier_army_sub_unit_armored_car_recon_attack_factor` | `modifier_army_sub_unit_armored_car_recon_defence_factor` | `modifier_army_sub_unit_armored_car_recon_speed_factor` | `modifier_army_sub_unit_armored_car_recon_max_org_factor` |  |
| `blackshirt_assault_battalion` | `modifier_army_sub_unit_blackshirt_assault_battalion_attack_factor` | `modifier_army_sub_unit_blackshirt_assault_battalion_defence_factor` | `modifier_army_sub_unit_blackshirt_assault_battalion_speed_factor` | `modifier_army_sub_unit_blackshirt_assault_battalion_max_org_factor` |  |
| `camelry` | `modifier_army_sub_unit_camelry_attack_factor` | `modifier_army_sub_unit_camelry_defence_factor` | `modifier_army_sub_unit_camelry_speed_factor` |  |  |
| `category_rocket_artillery` | `modifier_army_sub_unit_category_rocket_artillery_attack_factor` |  |  |  |  |
| `category_special_forces` |  |  |  | `modifier_army_sub_unit_category_special_forces_max_org_factor` |  |
| `cavalry` | `modifier_army_sub_unit_cavalry_attack_factor` | `modifier_army_sub_unit_cavalry_defence_factor` | `modifier_army_sub_unit_cavalry_speed_factor` |  |  |
| `infantry` | `modifier_army_sub_unit_infantry_attack_factor` | `modifier_army_sub_unit_infantry_defence_factor` | `modifier_army_sub_unit_infantry_speed_factor` |  |  |
| `irregular_infantry` | `modifier_army_sub_unit_irregular_infantry_attack_factor` | `modifier_army_sub_unit_irregular_infantry_defence_factor` | `modifier_army_sub_unit_irregular_infantry_speed_factor` | `modifier_army_sub_unit_irregular_infantry_max_org_factor` |  |
| `light_tank_recon` | `modifier_army_sub_unit_light_tank_recon_attack_factor` | `modifier_army_sub_unit_light_tank_recon_defence_factor` | `modifier_army_sub_unit_light_tank_recon_speed_factor` | `modifier_army_sub_unit_light_tank_recon_max_org_factor` |  |
| `long_range_patrol_support` | `modifier_army_sub_unit_long_range_patrol_support_attack_factor` | `modifier_army_sub_unit_long_range_patrol_support_defence_factor` |  |  |  |
| `marine` | `modifier_army_sub_unit_marine_attack_factor` | `modifier_army_sub_unit_marine_defence_factor` | `modifier_army_sub_unit_marine_speed_factor` | `modifier_army_sub_unit_marine_max_org_factor` |  |
| `military_police` | `modifier_army_sub_unit_military_police_attack_factor` | `modifier_army_sub_unit_military_police_defence_factor` | `modifier_army_sub_unit_military_police_speed_factor` | `modifier_army_sub_unit_military_police_max_org_factor` |  |
| `militia` | `modifier_army_sub_unit_militia_attack_factor` | `modifier_army_sub_unit_militia_defence_factor` | `modifier_army_sub_unit_militia_speed_factor` | `modifier_army_sub_unit_militia_max_org_factor` | `modifier_army_sub_unit_militia_org_recovery_cap_factor` |
| `mountaineers` | `modifier_army_sub_unit_mountaineers_attack_factor` | `modifier_army_sub_unit_mountaineers_defence_factor` | `modifier_army_sub_unit_mountaineers_speed_factor` | `modifier_army_sub_unit_mountaineers_max_org_factor` |  |
| `paratrooper` | `modifier_army_sub_unit_paratrooper_attack_factor` | `modifier_army_sub_unit_paratrooper_defence_factor` | `modifier_army_sub_unit_paratrooper_speed_factor` | `modifier_army_sub_unit_paratrooper_max_org_factor` |  |
<!-- kit:end id="fix-sub-unit-modifiers" -->

<!-- kit:begin id="add-land" at="section:land-combat" -->
Documented modifiers this section does not list (25). Format and meaning columns are explained under [How the added tables read](#how-the-added-tables-read). [docs] `documentation/modifiers_documentation.md`

| Modifier | Categories | Format | Meaning |
| --- | --- | --- | --- |
| `armor_factor` | army, defensive | 2 dp | (not described in the docs) |
| `army_armor_attack_factor` | army, aggressive | 1 dp |  |
| `army_armor_defence_factor` | army, defensive | 1 dp |  |
| `army_artillery_attack_factor` | army, aggressive | 1 dp |  |
| `army_infantry_attack_factor` | army, aggressive | 1 dp |  |
| `army_infantry_defence_factor` | army, defensive | 1 dp |  |
| `army_non_core_attack_factor` | army, aggressive | 1 dp | Division attack in non-core territory |
| `army_non_core_defence_factor` | army, defensive | 1 dp | Division defence in non-core territory |
| `army_retreat_speed_factor` | army, defensive | 2 dp | Speed of retreating divisions |
| `cannot_retreat_while_attacking` | army, aggressive | bool |  |
| `cannot_retreat_while_defending` | army, defensive | bool |  |
| `casualty_trickleback` | army | 2 dp | (not described in the docs) |
| `cavalry_defence_factor` | army, defensive | 1 dp |  |
| `combat_entrenchment` | army, defensive | 1 dp | Entrenchment combat bonus |
| `mechanized_attack_factor` | army, aggressive | 1 dp |  |
| `mechanized_defence_factor` | army, defensive | 1 dp |  |
| `motorized_attack_factor` | army, aggressive | 1 dp |  |
| `motorized_defence_factor` | army, defensive | 1 dp |  |
| `org_damage_multiplier` | army, defensive | 1 dp | Organisation damage taken |
| `planning_decay_rate_factor` | army, aggressive | 2 dp | How fast a prepared plan decays |
| `shore_bombardment_collateral_damage_factor` | country | 2 dp |  |
| `special_forces_attack_factor` | army, aggressive | 1 dp |  |
| `special_forces_defence_factor` | army, defensive | 1 dp |  |
| `str_damage_multiplier` | army, defensive | 1 dp | Strength damage taken |
| `war_support_reduction_on_damage` | army, defensive | 1 dp | War support lost from casualties |
<!-- kit:end id="add-land" -->

<!-- kit:begin id="add-ninv" at="section:naval-invasions" -->
Documented modifiers this section does not list (8). The `air_invasion_*` rows are about airborne invasions and are listed here because the wiki has no airborne section. Format and meaning columns are explained under [How the added tables read](#how-the-added-tables-read). [docs] `documentation/modifiers_documentation.md`

| Modifier | Categories | Format | Meaning |
| --- | --- | --- | --- |
| `air_invasion_division_cap` | air | 0 dp | Max divisions per airborne invasion order |
| `air_invasion_plan_cap` | country | 0 dp | Max airborne invasions that can be planned and prepared at once |
| `air_invasion_prep_days` | country | 1 dp | ~ Days needed to prepare an airborne invasion (unused in vanilla) |
| `air_invasion_preparation` | air, unit_leader | 1 dp | How quickly an airborne invasion can be prepared |
| `naval_commando_raid_distance` | naval | 0 dp | Maximum distance of naval commando raids |
| `naval_invasion_division_cap` | naval | 0 dp | Max divisions per naval invasion order |
| `naval_invasion_plan_cap` | country | 0 dp | Max naval invasions that can be planned and prepared at once |
| `naval_invasion_prep_days` | country | 0 dp | ~ Days needed to prepare a naval invasion (negative shortens it) |
<!-- kit:end id="add-ninv" -->

<!-- kit:begin id="add-naval" at="section:naval-combat" -->
Documented modifiers this section does not list (5). Format and meaning columns are explained under [How the added tables read](#how-the-added-tables-read). [docs] `documentation/modifiers_documentation.md`

| Modifier | Categories | Format | Meaning |
| --- | --- | --- | --- |
| `headquarters_experience_gain_factor` | naval | 2 dp | Experience gained from naval headquarters (unused in vanilla) |
| `max_organisation` | naval | 0 dp | (not described in the docs) |
| `naval_mission_xp_factor` | naval | 3 dp | Naval mission experience (unused in vanilla) |
| `naval_ship_recovery_chance` | naval | 0 dp |  |
| `naval_ship_recovery_chance_factor` | naval | 0 dp | Unused in vanilla |
<!-- kit:end id="add-naval" -->

<!-- kit:begin id="add-air" at="section:air-combat" -->
Documented modifiers this section does not list (4). Format and meaning columns are explained under [How the added tables read](#how-the-added-tables-read). [docs] `documentation/modifiers_documentation.md`

| Modifier | Categories | Format | Meaning |
| --- | --- | --- | --- |
| `air_strategic_bomber_defence_factor` | air | 2 dp | ~ Defence of strategic bombers |
| `ground_attack` | air, aggressive | 1 dp | Ground attack (unused in vanilla) |
| `naval_strike_agility_factor` | air | 0 dp | Agility of aircraft on naval strike missions |
| `naval_strike_attack_factor` | air | 0 dp | Attack of aircraft on naval strike missions |
<!-- kit:end id="add-air" -->

<!-- kit:begin id="add-targ" at="section:targeted-modifiers" -->
Twelve more targeted modifiers (the section lists ten). They belong in a `targeted_modifier = { tag = X ... }` block, like `attack_bonus_against`. [vanilla-confirmed 1.19.4.1]

- The in-game text of eleven of them ends in "against a country" (for example "Capital Ship Attack Against a Country"), and `river_crossing_factor_against` reads "against country". [vanilla-confirmed 1.19.4.1] `localisation/english/modifiers_l_english.yml`
- All twelve are documented modifiers. [docs] `documentation/modifiers_documentation.md`
- Vanilla uses `spotting_chance_against`, `navy_capital_ship_attack_factor_against` and `navy_screen_attack_factor_against` inside `targeted_modifier` in `common/ideas/japan.txt` (the first two also in `common/ideas/australia.txt`), and `river_crossing_factor_against` in `common/ideas/GER.txt`. The other eight are unused in vanilla. [vanilla-confirmed 1.19.4.1]
- `army_attack_against_major_factor` and its siblings are not targeted: they compare against major and minor countries as a class.

| Modifier | Categories | Format | Meaning |
| --- | --- | --- | --- |
| `amphibious_invasion_against` | naval | 1 dp | Targeted: amphibious invasion strength against one country |
| `invasion_preparation_against` | naval | 1 dp | Targeted: naval invasion preparation against one country |
| `naval_critical_score_chance_factor_against` | naval, unit_leader, aggressive | 2 dp | Targeted: naval critical score chance against one country |
| `naval_hit_chance_against` | naval | 0 dp | Targeted: naval hit chance against one country |
| `navy_capital_ship_attack_factor_against` | naval, aggressive | 2 dp | Targeted: capital ship attack against one country |
| `navy_capital_ship_defence_factor_against` | naval, defensive | 2 dp | Targeted: capital ship defence against one country |
| `navy_screen_attack_factor_against` | naval, aggressive | 2 dp | Targeted: screen ship attack against one country |
| `navy_screen_defence_factor_against` | naval, defensive | 2 dp | Targeted: screen ship defence against one country |
| `navy_submarine_attack_factor_against` | naval, aggressive | 2 dp | Targeted: submarine attack against one country |
| `navy_submarine_defence_factor_against` | naval, defensive | 2 dp | Targeted: submarine defence against one country |
| `river_crossing_factor_against` | army | 2 dp | Targeted: river crossing penalty against one country |
| `spotting_chance_against` | naval | 0 dp | Targeted: naval spotting chance against one country |
<!-- kit:end id="add-targ" -->

<!-- kit:begin id="add-state" at="section:state-scope" -->
Documented modifiers this section does not list (1). Format and meaning columns are explained under [How the added tables read](#how-the-added-tables-read). [docs] `documentation/modifiers_documentation.md`

| Modifier | Categories | Format | Meaning |
| --- | --- | --- | --- |
| `state_production_speed_facility_factor` | state | 2 dp | Local construction speed of facilities (unused in vanilla) |
<!-- kit:end id="add-state" -->

<!-- kit:begin id="weather-statics" at="section:strategic-region-scope" -->
The static modifiers that vanilla marks `# on Region` in `common/modifiers/00_static_modifiers.txt` are `weather_rain_light`, `weather_rain_heavy`, `weather_snow`, `weather_blizzard`, `weather_sandstorm` and `weather_arctic_water`. They use far more modifiers than the five listed above: `air_mission_efficiency`, `air_bombing_targetting`, `carrier_traffic`, `local_org_regain`, `naval_detection`, `naval_hit_chance`, `naval_retreat_speed`, `naval_speed_factor`, `org_loss_when_moving`, `positioning`, `supply_factor`, `supply_consumption_factor`, `truck_attrition_factor`, `army_attack_speed_factor`, `naval_attrition` and others. The ones marked `# on Province` (`weather_mud`, `weather_extreme_cold`, `weather_very_cold`, `weather_very_hot`, `weather_extreme_hot`, `weather_ground_snow_medium`, `weather_ground_snow_high`, `flooded`) use land modifiers such as `army_attack_factor`, `army_speed_factor` and `attrition`. [vanilla-confirmed 1.19.3]
<!-- kit:end id="weather-statics" -->
