# Occupation and resistance modding

*Kit page: written by the Agentic HOI4 Modding Kit from the Hearts of Iron IV 1.19.3.0 game files. The wiki has no page for this topic. CC BY-SA 3.0 (see LICENSE.txt).*
<!-- kit:page -->

<!-- kit:begin id="review" at="top" build="1.19.3.0" checked="2026-10-31" sources="common/occupation_laws/ common/resistance_activity/ common/resistance_compliance_modifiers/ common/defines/00_defines.lua common/scripted_triggers/00_resistance_initiate_triggers.txt documentation/effects_documentation.md documentation/triggers_documentation.md documentation/modifiers_documentation.md documentation/dynamic_variables_documentation.md localisation/english/resistance_and_occupation_l_english.yml interface/countryoccupationview.gfx" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Written from: the header comments and all vanilla blocks of the three folders (22 laws, 20 activities, 9 modifiers), the `NResistance` and related defines, and the resistance and compliance entries of the effects, triggers, modifiers and dynamic variables documentation.
Corrections found: the law header documents `main_fallback_law`, which no vanilla law uses and `hoi4.exe` does not contain; the modifier header spells two keys differently from vanilla (`icon_small`, `core_compliancemodifier`).
Gaps left: the exact resistance and compliance formulas, the timing of resistance activity rolls, the meaning of `alert_level`/`alert_margin` and the scopes inside resistance activity blocks are not stated in the files.
<!-- kit:end id="review" -->

## Table of contents

- [Overview](#Overview)
- [Numbers behind the system](#Numbers_behind_the_system)
- [Occupation laws](#Occupation_laws)
  - [Law keys](#Law_keys)
  - [Offering and gating laws](#Offering_and_gating_laws)
  - [Fallback laws](#Fallback_laws)
  - [Law AI](#Law_AI)
  - [Vanilla laws](#Vanilla_laws)
  - [Law localisation and GFX](#Law_localisation_and_GFX)
- [Resistance activities](#Resistance_activities)
- [Resistance and compliance modifiers](#Resistance_and_compliance_modifiers)
  - [Modifier keys](#Modifier_keys)
  - [Types, scopes and thresholds](#Types_scopes_and_thresholds)
  - [Vanilla modifiers](#Vanilla_modifiers)
- [Script interface](#Script_interface)
- [Starting resistance](#Starting_resistance)
- [Minimal example](#Minimal_example)
- [Traps](#Traps)

---

When a country holds states that belong to someone else, each state tracks resistance and compliance, and the occupier chooses an occupation law. Three folders of `common/` shape this system: laws, resistance activities and the resistance and compliance modifiers that switch on at thresholds. [vanilla-confirmed 1.19.3] `common/occupation_laws/`, `common/resistance_activity/`, `common/resistance_compliance_modifiers/`. Effects, triggers and modifiers for it are listed under [Effects](<effects.md#Resistance_and_compliance>), [Triggers](<triggers.md#Resistance_and_Compliance>) and [Modifiers](<modifiers.md#Resistance_and_compliance>).

## Overview <a id="Overview"></a>

| Folder | Defines | Vanilla content |
| --- | --- | --- |
| `common/occupation_laws/` | Laws the occupier sets, with state modifiers and AI weights. | `occupation_laws.txt`, 22 laws |
| `common/resistance_activity/` | Actions the resistance may take against garrisons: sabotage. | `resistance_activity.txt`, 20 activities |
| `common/resistance_compliance_modifiers/` | Modifiers that turn on when resistance or compliance passes a threshold. | `resistance_modifiers.txt` (4), `compliance_modifiers.txt` (5) |

All rows: [vanilla-confirmed 1.19.3] file lists and block counts of the three folders.

- Resistance and compliance are percentages from 0 to 100 per state. The scripted `threshold` values are percentages, and the defines call them percentages. [vanilla-confirmed 1.19.3] `common/resistance_compliance_modifiers/`, `common/defines/00_defines.lua`.
- Compliance gives economy and manpower back to the occupier and lowers the resistance target. Resistance fights the garrison and, at high values, turns on penalties for the occupier. [vanilla-confirmed 1.19.3] the vanilla compliance and resistance modifiers listed below and `localisation/english/resistance_and_occupation_l_english.yml`.
- Garrisons are division templates with a suppression value. A template with suppression 0 cannot be chosen, and special-forces templates are refused. [vanilla-confirmed 1.19.3] `localisation/english/resistance_and_occupation_l_english.yml` (`OCCUPATION_BAD_GARRISON_NO_SUPPRESSION`, `OCCUPATION_BAD_GARRISON_SPECIAL_FORCES`).

## Numbers behind the system <a id="Numbers_behind_the_system"></a>

The block `NResistance` of `common/defines/00_defines.lua` holds most values. The full list is in [Defines](<defines.md#NResistance>). All rows: [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua`.

| Define | Value | Use |
| --- | --- | --- |
| `NResistance.INITIAL_STATE_RESISTANCE` / `INITIAL_STATE_COMPLIANCE` | 1.0 / 0.0 | Values of a state at capture. |
| `NResistance.RESISTANCE_TARGET_BASE` | 35.0 | Base resistance target. |
| `RESISTANCE_TARGET_MODIFIER_HAS_CLAIM` | -5.0 | Target change when the controller has a claim. |
| `RESISTANCE_TARGET_MODIFIER_PER_STABILITY_LOSS` | 0.2 | Target change per point of stability below 100%. |
| `RESISTANCE_TARGET_MODIFIER_PER_COMPLIANCE` | -0.5 | Target change per point of compliance. |
| `RESISTANCE_TARGET_MODIFIER_IS_AT_PEACE` | -10.0 | Target change when the controller is at peace. |
| `RESISTANCE_TARGET_MODIFIER_STATE_VP` | 0/0.0, 5/5.0, 20/10.0, 50/20.0 | Pairs of state victory points and target change. |
| `RESISTANCE_TARGET_MODIFIER_OCCUPIED_CAPITULATED` | 10.0 | Target change when the occupied country has capitulated. |
| `RESISTANCE_TARGET_MODIFIER_OCCUPIED_IS_EXILE_MIN` / `_MAX` | 2.0 / 20.0 | Range for an exiled owner, interpolated by legitimacy. |
| `RESISTANCE_TARGET_MODIFIER_POP_LOW` / `POP_VERY_LOW` | -20.0 / -50.0 | Target change under `RESISTANCE_POP_LOW_CUTOFF` 10000 / `RESISTANCE_POP_VERY_LOW_CUTOFF` 1000 population. |
| `RESISTANCE_TARGET_MIN_CAP_FOR_NON_COMPLIANCE` | 10 | Floor of the target unless compliance lowers it further. |
| `RESISTANCE_GROWTH_BASE` / `_MIN` / `_MAX` | 0.2 / 0.01 / 100.0 | Base resistance growth. |
| `RESISTANCE_DECAY_BASE` / `_MIN` / `_MAX` | 0.1 / 0.01 / 100.0 | Decay when above target. |
| `RESISTANCE_DECAY_MODIFIER_HAS_CLAIM` | 25.0 | Decay modifier for a controller with a claim. |
| `RESISTANCE_DECAY_MODIFIER_FACTORS` | 10/-50, 20/-25 | Decay modifier below 10% and below 20% resistance. |
| `COMPLIANCE_GROWTH_BASE` | 0.075 | Base compliance growth (min -100.0, max 100.0). |
| `COMPLIANCE_GROWTH_IS_AT_PEACE` / `COMPLIANCE_GROWTH_HAS_CLAIM` | 10 / 5 | Growth bonuses. |
| `COMPLIANCE_DECAY_AT_MAX_COMPLIANCE` | -0.083 | Decay that lets compliance settle at a level. |
| `COMPLIANCE_FACTOR_ON_STATE_CONTROLLER_CHANGE` | -0.5 | Factor on compliance when the controller changes. |
| `RESISTANCE_RATIO_DIFF_TO_SPREAD` | 0.5 | Share of the resistance difference that spreads to a neighbour state. |
| `RESISTANCE_ACTIVITY_CHANCE_AT_MAX_RESISTANCE` | 0.312 | Chance of resistance activity at the highest resistance. |
| `RESISTANCE_ACTIVITY_MIN_GARRISON_PENETRATE_CHANCE` | 0.02 | Lowest chance that activity gets through the garrison. |
| `RESISTANCE_TARGET_TO_REENABLE_RESISTANCE` | 10 | Resistance stopped at 0 only restarts when the target is above this. |
| `NO_COMPLIANCE_GAIN_ENABLE_LIMIT` | 0.5 | Share of no-garrison law needed before `no_compliance_gain` applies. |
| `SUPPRESSION_NEEDED_BY_RESISTANCE_POINT` | 0.75 | Suppression needed per resistance point (capped between 10 and 50). |
| `GARRISON_MANPOWER_LOST_BY_ATTACK` / `GARRISON_EQUIPMENT_LOST_BY_ATTACK` | 0.016 / 0.02 | Garrison losses per resistance attack. |

- Built-in map mode colours for resistance and compliance are `OCCUPATION_RESISTANCE_MAP_MODE_COLORS` and `OCCUPATION_COMPLIANCE_MAP_MODE_COLORS` (rows of value, red, green, blue, alpha). [vanilla-confirmed 1.19.3] `common/defines/00_graphics.lua`.
- The resistance target is the sum of these defines plus the `resistance_target` modifier. The files do not give the exact formula or the unit mix of fractions (modifiers) and points (defines). [unverified]

## Occupation laws <a id="Occupation_laws"></a>

### Law keys <a id="Law_keys"></a>

Law block name = law id = loc key of the law name. Documented keys: [docs] header of `common/occupation_laws/occupation_laws.txt`. Counts: [vanilla-confirmed 1.19.3] over the 22 laws.

| Key | Value | Used by | Meaning |
| --- | --- | --- | --- |
| `icon` | frame number, or `"GFX_name:frame"` | 22 | Frame in a strip. Default strip `GFX_occupation_policy_icon_strip` (17 frames of 30 by 30). Vanilla uses frames 1 to 17 as bare numbers. |
| `sound_effect` | sound name | 22 | Plays when the law is chosen. |
| `state_modifier` | modifier block | 22 | Applied to states under the law. |
| `suppressed_state_modifier` | modifier block | 1 | Used instead of `state_modifier` in states whose resistance is suppressed (at 0). Only `no_garrison` sets it. |
| `visible` | trigger | 15 | Hides the law completely when false. |
| `available` | trigger | 0 | Shows the law greyed out and unselectable when false. |
| `ai_will_do` | weight block | 21 | Score for the AI. See Law AI. |
| `fallback_law` | law id | 9 | Law to use when this one stops being visible or available. |
| `tooltip` | loc key | 0 | Description text of the law. |
| `gui_order` | number | 0 | Sort order in the window (default 0, otherwise load order). |
| `main_fallback_law` | `yes` | 0 | Documented as the one law used when there is no `fallback_law`. See Fallback laws. |
| `default_law` | `yes` | 1 | On `military_governor_occupation`. Not in the header. |
| `starting_law` | `yes` | 1 | On `military_governor_occupation`. Not in the header. |
| `missing_garrison_law` | `yes` | 1 | On `missing_garrison_scaled_effect`. Not in the header. |

- The `state_modifier` keys vanilla uses are `resistance_target`, `compliance_gain`, `required_garrison_factor`, `resistance_damage_to_garrison`, `local_resources`, `local_factories`, `local_manpower`, `resistance_decay`, `no_compliance_gain`, `repair_speed_*_factor`, `enemy_operative_detection_chance_over_occupied_tag`, `enemy_intel_network_gain_factor_over_occupied_tag` and `custom_modifier_tooltip`. Any state modifier from [Modifiers](<modifiers.md#Resistance_and_compliance>) fits. [vanilla-confirmed 1.19.3] `occupation_laws.txt`.
- `missing_garrison_scaled_effect` has `visible = { always = no }`. Its comment says a law with missing garrison scales toward the law marked `missing_garrison_law`, otherwise toward `default_law`. [vanilla-confirmed 1.19.3] `occupation_laws.txt`.

### Offering and gating laws <a id="Offering_and_gating_laws"></a>

- `visible` is checked with the occupier as scope. The header says the occupied country is not set there, but 10 of the 15 vanilla `visible` blocks test `FROM = { original_tag = ... }`, so `FROM` is the occupied country in practice. [docs] header; [vanilla-confirmed 1.19.3] `reconciliation`, `colonial_police*`, `secretaries_general`, `independent_rule`, `princely_subjugation`, `senbu_occupation_law`, `GEACPS_*`.
- `available` has the occupier as scope and `FROM` as the occupied country. [docs] header.
- Vanilla gates laws by government (`autonomous_occupation`: `has_government = democratic`, `liberate_workers_occupation`: `communism`, `brutally_oppressive_occupation`: `fascism`), by DLC and country plus completed focus (`colonial_police`, `independent_rule`), and by the occupied tag. [vanilla-confirmed 1.19.3] `occupation_laws.txt`.
- Laws are set at three levels: the occupier's default law, an override per occupied country, and an override per state. `set_occupation_law = my_law` sets the level of its scope; `set_occupation_law = default_law` clears an override or, on a country's own default, restores the law marked `starting_law = yes`. [docs] `documentation/effects_documentation.md`.
- `set_occupation_law_where_available` tries the default level first, then each country, then each state, and clears the overrides below the level where it succeeded. Use it for a law only some targets may have. [docs] `documentation/effects_documentation.md`.
- The trigger `occupation_law` reads the same three levels in the same scopes. [docs] `documentation/triggers_documentation.md`.
- Vanilla calls `set_occupation_law_where_available` 7 times (focus, events, one on action) and `set_occupation_law` 3 times. [vanilla-confirmed 1.19.3] `common/national_focus/india_goe.txt`, `events/`, `common/on_actions/13_goe_on_actions.txt`.

### Fallback laws <a id="Fallback_laws"></a>

- Header: when the current law stops being visible or available, the state falls back to its `fallback_law`; if that is not set, to the one law marked `main_fallback_law = yes`. With too little garrison manpower or equipment, law bonuses blend toward the fallback law, and at 0 manpower the player must switch. [docs] header of `occupation_laws.txt`.
- Vanilla marks `military_governor_occupation` with `default_law = yes` and `starting_law = yes`, uses `fallback_law` on 9 laws, and never writes `main_fallback_law`. The string `main_fallback_law` is not in `hoi4.exe`, while `default_law` and `starting_law` are. A mod that only adds laws leaves the vanilla `default_law` alone and gives its own laws a `fallback_law`. [vanilla-confirmed 1.19.3] `occupation_laws.txt`; that `default_law` replaced `main_fallback_law` is [unverified].
- The loc text says an invalid default law makes territories "default to No Garrison". It conflicts with the header and the cause is unclear. [vanilla-confirmed 1.19.3] `OCCUPATION_INVALID_DEFAULT_LAW` in `resistance_and_occupation_l_english.yml`.
- Fallback chains in vanilla: `colonial_police` to `colonial_police_improved` to `colonial_police_final` to `foreign_civilian_oversight`; `secretaries_general` and `princely_subjugation` to `military_governor_occupation`. [vanilla-confirmed 1.19.3] `occupation_laws.txt`.

### Law AI <a id="Law_AI"></a>

- `ai_will_do` scores a law per state. Scope is the state, `FROM` is the occupier and `FROM.FROM` the occupied country. Temp variables available: `ai_desire_<resource>` (0 to 1), `uncapped_resistance_target`, `resistance_target_without_law`, `garrison_min_support_ratio`, `garrison_equipment_support_ratio`, `garrison_manpower_support_ratio`. [docs] header of `occupation_laws.txt`.
- Vanilla pattern: `base = 0` plus `modifier` blocks that test `check_variable = { resistance_target_without_law > 0.44 }` and add 200 to 500. [vanilla-confirmed 1.19.3] `military_governor_occupation`, `martial_law_occupation`, `colonial_police`.
- Anti-flapping: four laws test their own selection and switch to a looser limit while selected, for example `if = { limit = { occupation_law = martial_law_occupation } set_temp_variable = { resistance_limit = 35 } }`. [vanilla-confirmed 1.19.3] `martial_law_occupation`, `military_governor_occupation`, `forced_labor_occupation`, `local_police_force_garrison`.
- `forced_labor_occupation` multiplies the score to 0 below a garrison support ratio of 1.5 (1.3 when selected). [vanilla-confirmed 1.19.3] `occupation_laws.txt`.
- The `ai_strategy` type `occupation_policy` is listed in the AI strategy documentation without a description, and the dynamic variable `ai_strategy_occupation_policy` exists (`GER.ai_strategy_occupation_policy@ENG`). No vanilla file uses the strategy. [docs] `common/ai_strategy/_documentation.md`, `documentation/dynamic_variables_documentation.md`; [vanilla-confirmed 1.19.3] search of `common/ai_strategy/`.
- Garrison strategies exist as well: `garrison`, `garrison_reinforcement_priority`, `asking_foreign_garrison`. [docs] `common/ai_strategy/_documentation.md`.

### Vanilla laws <a id="Vanilla_laws"></a>

State modifier values of the laws without a country or DLC gate, as a calibration table. All rows: [vanilla-confirmed 1.19.3] `occupation_laws.txt`. Empty cells are not set. `rt` = `resistance_target`, `cg` = `compliance_gain`, `rgf` = `required_garrison_factor`, `rdg` = `resistance_damage_to_garrison`.

| Law | rt | cg | rgf | rdg | `local_resources` | `local_factories` | Gate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `no_garrison` | 0.4 | | -1 | | | | none (hidden for RAJ by a flag) |
| `autonomous_occupation` | 0.10 | 0.02 | -0.40 | -0.25 | | | democratic |
| `foreign_civilian_oversight` | | 0.000 | -0.25 | -0.25 | 0.00 | 0.00 | none |
| `local_police_force_garrison` | -0.15 | -0.025 | -0.35 | -0.5 | 0.00 | 0.00 | none |
| `secret_police_oversight` | -0.30 | -0.04 | -0.15 | -0.15 | 0.05 | 0.05 | none |
| `liberate_workers_occupation` | -0.15 | -0.025 | -0.15 | 0.25 | 0.3 | 0.2 | communism |
| `military_governor_occupation` | -0.35 | -0.045 | 0.0 | | 0.10 | | none, default |
| `martial_law_occupation` | -0.60 | -0.055 | | | 0.1 | | none |
| `forced_labor_occupation` | -0.40 | -0.08 | 0.15 | 0.3 | 0.40 | 0.05 | none |
| `harsh_quotas_occupation` | -0.40 | -0.08 | 0.15 | 0.50 | 0.05 | 0.25 | none |
| `brutally_oppressive_occupation` | -0.75 | -0.11 | 0.25 | 1.0 | 0.10 | | fascism |

The other laws are country or DLC specific: `reconciliation`, `colonial_police` (three tiers), `secretaries_general`, `independent_rule`, `princely_subjugation`, `senbu_occupation_law`, `GEACPS_exploitation_occupation_law`, `GEACPS_prosperity_occupation_law`. `missing_garrison_scaled_effect` is the hidden scaling law. [vanilla-confirmed 1.19.3] `occupation_laws.txt`.

### Law localisation and GFX <a id="Law_localisation_and_GFX"></a>

- The law name is the loc key equal to the law id (`military_governor_occupation: "Military Governor"`). `tooltip` is the optional description key. [vanilla-confirmed 1.19.3] `localisation/english/resistance_and_occupation_l_english.yml`; [docs] header.
- `custom_modifier_tooltip = "key"` inside `state_modifier` adds a text line, as in `forced_labor_occupation`. [vanilla-confirmed 1.19.3] `occupation_laws.txt`.
- The default icon strip `GFX_occupation_policy_icon_strip` (`interface/countryoccupationview.gfx`) is 510 by 30 with 17 frames. [vanilla-confirmed 1.19.3] `interface/countryoccupationview.gfx`, DDS header of `gfx/interface/occupation/occupation_policy_icon_strip.dds`.

## Resistance activities <a id="Resistance_activities"></a>

An activity is one action the resistance can take once it gets through the garrison. [vanilla-confirmed 1.19.3] `localisation/english/resistance_and_occupation_l_english.yml` (`RESISTANCE_ACTIVITY_LIST_TITLE`: "One of the following effects will apply when the resistance penetrates the garrisons"; each entry shows its chance).

Keys, [docs] header of `common/resistance_activity/resistance_activity.txt` and [vanilla-confirmed 1.19.3] counts over the 20 activities:

| Key | Used by | Meaning |
| --- | --- | --- |
| `available` | 20 | Trigger. The activity is only in the pool when it holds. |
| `weight` | 20 | `base` plus `modifier` blocks with `add`. Chance of the activity relative to the others in the pool. |
| `effect` | 20 | Effect run when the activity fires. |
| `alert_text` | 20 | Loc key of the alert on the map (`building_is_sabotaged`, `resource_is_sabotaged`). |
| `max_amount`, `duration`, `state_modifier` | 0 | Documented in the header; unused in vanilla. |

- The roll has two steps in the UI text: a chance for activity at all (`RESISTANCE_CHANCE_FOR_ACTIVITY`, with 0.312 at maximum resistance as the define above) and a chance to get through the garrison (`RESISTANCE_CHANCE_FOR_GARRISON_PENETRATE`, at least 0.02); then one of the available activities applies. How often it is rolled is not stated. [vanilla-confirmed 1.19.3] `localisation/english/resistance_and_occupation_l_english.yml`, `common/defines/00_defines.lua`; the timing is [unverified].
- All vanilla blocks use state-scope triggers and effects directly (`non_damaged_building_level`, `has_resources_amount`, `damage_building`, `add_dynamic_modifier`), so the scope is the state. The meaning of `ROOT` and `FROM` is not stated. [vanilla-confirmed 1.19.3] `resistance_activity.txt`; `ROOT`/`FROM` [unverified].
- Vanilla activities: 13 building sabotage (`sabotage_arms_factory`, `_infrastructure`, `_industrial_complex`, `_air_base`, `_dockyard`, `_anti_air_building`, `_synthetic_refinery`, `_fuel_silo`, `_radar_station`, `_rocket_site`, `_nuclear_reactor`, `_nuclear_reactor_heavy_water`, `_commercial_nuclear_reactor`) and 7 resource sabotage (`_oil`, `_aluminium`, `_rubber`, `_tungsten`, `_steel`, `_chromium`, `_coal`). [vanilla-confirmed 1.19.3] `resistance_activity.txt`.
- Building sabotage calls `damage_building = { type = ... damage = N }`: 0.25 for most buildings, 0.5 for infrastructure, 0.15 for the three nuclear reactors; the targeted-sabotage variants of arms factory, civilian factory and infrastructure use 0.5, 0.5 and 1.0. Resource sabotage adds a negative value to a state variable such as `sabotaged_oil` (-12) and adds the dynamic modifier `sabotaged_resources` for 180 days (135 under `forced_labor_occupation`). [vanilla-confirmed 1.19.3] `resistance_activity.txt`.
- The intelligence operations `operation_targeted_sabotage_*` feed this system: they add to the state variables `targeted_sabotage_industry`, `_infrastructure` and `_resources`, and the activities raise their `weight` by 4 while the variable is above 0 and consume one point per use. [vanilla-confirmed 1.19.3] `common/operations/00_operations.txt`, `resistance_activity.txt`. See [Intelligence operation modding](<intelligence-operation-modding.md>).
- Laws change activity weights through `occupation_law = harsh_quotas_occupation` and `forced_labor_occupation` tests in `weight` (add -0.25). [vanilla-confirmed 1.19.3] `resistance_activity.txt`.
- The modifiers `resistance_activity` and `resistance_garrison_penetration_chance` are shown to the player as "Resistance Activity Chance" and "Garrison Penetration Chance". [vanilla-confirmed 1.19.3] `localisation/english/modifiers_l_english.yml`.

## Resistance and compliance modifiers <a id="Resistance_and_compliance_modifiers"></a>

### Modifier keys <a id="Modifier_keys"></a>

Block name = modifier id = loc key of its name. Documented keys: [docs] header of `resistance_modifiers.txt` (`compliance_modifiers.txt` points to it). Counts over the 9 vanilla modifiers: [vanilla-confirmed 1.19.3].

| Key | Used by | Meaning |
| --- | --- | --- |
| `type` | 9 | One of `state_resistance_modifier`, `core_resistance_modifier`, `state_compliance_modifier`, `core_compliance_modifier`. |
| `threshold` | 9 | Percentage at which the modifier turns on. |
| `margin` | 9 | It turns off again when the value is below `threshold - margin`. Vanilla uses 2 everywhere. |
| `state_modifier` | 9 | Modifiers applied while enabled. Empty in `compliance_80`. |
| `icon`, `small_icon` | 9 | `"GFX_name:frame"`. Defaults `GFX_occupation_modifier_strip` and `GFX_occupation_modifier_small_strip`. The header calls the second key `icon_small`; vanilla writes `small_icon`. |
| `visible` | 1 | If false the modifier appears nowhere. |
| `enabled` | 1 | If false the modifier stays off even above the threshold and is switched off if it was on. |
| `on_enable`, `on_disable` | 2, 0 | Effects run when the modifier turns on or off. |
| `is_dynamic` | 0 | Documented: not added to states by default, active only after the threshold and an `add_state_resistance_compliance_modifier` call. State types only. |
| `tooltip` | 0 | Description text. |
| `alert_level`, `alert_margin` | 1 | Only on `resistance_90` (`high`, 20). Not documented. The alert list shows modifiers that are active or about to activate, so these probably set when the map alert appears. [unverified] |

### Types, scopes and thresholds <a id="Types_scopes_and_thresholds"></a>

- State types measure one state. Scope is the state; the header says the occupier is `FROM` (and root) and `FROM.FROM` the occupied country. Core types measure the average over all states of an occupied country: scope and root are the occupier, `FROM` the occupied country. [docs] header of `resistance_modifiers.txt`.
- The header writes `core_compliancemodifier` for the fourth type; vanilla and `hoi4.exe` use `core_compliance_modifier`. [vanilla-confirmed 1.19.3] `compliance_modifiers.txt`.
- In a core type `on_enable`, `var:occupied_country` is the occupied country. [vanilla-confirmed 1.19.3] `resistance_modifiers.txt` (`resistance_90`).
- Enable when the value reaches `threshold`, disable below `threshold - margin`. The tooltip says "goes above" for enabling. [docs] header; [vanilla-confirmed 1.19.3] `OCCUPATION_MODIFIER_ACTIVE` and `OCCUPATION_MODIFIER_NOT_ACTIVE` in `resistance_and_occupation_l_english.yml`.
- Effects that need to reach state controllers should not run in `on_enable` of a core type. The vanilla comment in `resistance_90` says to avoid them, and it fires the event through a hidden `country_event` with `hours = 1`. [vanilla-confirmed 1.19.3] `resistance_modifiers.txt`.
- Icon strips: compliance 5 frames (`GFX_occupation_compliance_modifier_strip`, 31 by 31 each; small 19 by 19), resistance 4 frames (31 by 31; small 19 by 19). [vanilla-confirmed 1.19.3] `interface/countryoccupationview.gfx`, DDS headers.

### Vanilla modifiers <a id="Vanilla_modifiers"></a>

All rows: [vanilla-confirmed 1.19.3] `common/resistance_compliance_modifiers/`.

| Id | Type | Threshold | State modifier |
| --- | --- | --- | --- |
| `resistance_25` | state resistance | 25 | `resistance_garrison_penetration_chance` 0.5 |
| `resistance_50` | state resistance | 50 | `resistance_damage_to_garrison` 1 |
| `resistance_75` | state resistance | 75 | `army_speed_factor_for_controller` -0.5, `local_supplies_for_controller` -0.5, `attrition_for_controller` 0.3, `disable_strategic_redeployment_for_controller` 1 |
| `resistance_90` | core resistance | 90 | `local_factories` -0.03; `on_enable` fires event `occupied_countries.2`; the tooltip says the resistance declares independence on the occupied core states |
| `compliance_15` | core compliance | 15 | `enemy_operative_detection_chance` 0.25 |
| `compliance_25` | core compliance | 25 | `required_garrison_factor` -0.25, `recruitable_population` 0.005 |
| `compliance_40` | core compliance | 40 | `local_factories` 0.1, `local_resources` 0.1 |
| `compliance_60` | core compliance | 60 | `recruitable_population_factor` 0.2 |
| `compliance_80` | core compliance | 80 | none; `enabled` needs `is_available_to_collaboration_government`; `on_enable` fires `occupied_countries.1` |

Script reads these ids with `has_core_occupation_modifier`: one decision in `common/decisions/foreign_influence.txt` is `visible` at `compliance_60` and `available` at `compliance_80` (`has_core_occupation_modifier = { occupied_country_tag = FROM modifier = compliance_80 }`). [vanilla-confirmed 1.19.3] `common/decisions/foreign_influence.txt`.

## Script interface <a id="Script_interface"></a>

Scopes and arguments: [docs] `documentation/effects_documentation.md`, `documentation/triggers_documentation.md`, `documentation/modifiers_documentation.md`, `documentation/dynamic_variables_documentation.md`.

| Kind | Names |
| --- | --- |
| State effects | `add_resistance`, `set_resistance`, `add_compliance`, `set_compliance`, `add_resistance_target` (`id`, `amount`, `occupied`, `occupier`, `days`, `tooltip`), `remove_resistance_target`, `start_resistance`, `cancel_resistance`, `force_enable_resistance`, `force_disable_resistance` (`clear`, `occupier`, `occupied`), `set_garrison_strength` |
| State or country effects | `set_occupation_law`, `set_occupation_law_where_available` |
| Any-scope effects | `add_state_resistance_compliance_modifier`, `remove_state_resistance_compliance_modifier` (`modifier`, `state`; only for `is_dynamic = yes` modifiers) |
| Country effects | `every_occupied_country`, `random_occupied_country` |
| State triggers | `resistance`, `compliance`, `resistance_target`, `resistance_speed`, `compliance_speed`, `has_resistance`, `has_active_resistance`, `occupied_country_tag`, `has_occupation_modifier`, `occupation_law` |
| Country triggers | `core_resistance`, `core_compliance` (`occupied_country_tag`, `value`), `has_core_occupation_modifier`, `num_occupied_states`, `garrison_manpower_need`, `any_occupied_country`, `all_occupied_country`, `occupation_law` |
| Variables | state: `resistance`, `compliance`, `resistance_target`, `resistance_speed`, `compliance_speed`; country: `core_resistance`, `core_compliance`, `garrison_manpower_need`, `num_occupied_states`, array `occupied_countries` |
| State and country modifiers | `resistance_target`, `resistance_growth`, `resistance_decay`, `resistance_activity`, `resistance_damage_to_garrison`, `resistance_garrison_penetration_chance`, `required_garrison_factor`, `compliance_gain`, `compliance_growth`, `no_compliance_gain` (boolean), `starting_compliance` |
| `..._on_our_occupied_states` modifiers | `resistance_target`, `resistance_growth`, `resistance_decay`, `resistance_damage_to_garrison` and `compliance_growth` each have an `_on_our_occupied_states` form for our states held by the enemy |
| Agency modifiers | `boost_resistance_factor`, `root_out_resistance_effectiveness_factor`, `occupied_operative_recruitment_chance` |

- The documentation text of `has_occupation_modifier` repeats the text of `occupied_country_tag`; it reads "compares occupied country that creates resistance to a tag" and shows `has_occupation_modifier = modifier_name`. [docs] `documentation/triggers_documentation.md`. No vanilla file uses `has_occupation_modifier` or `add_state_resistance_compliance_modifier`, so both are documented only. [vanilla-confirmed 1.19.3]
- Console: `resistance <amount>` and `compliance <amount>` raise or lower the value in a state. [docs] `documentation/console_commands_documentation.md`.

## Starting resistance <a id="Starting_resistance"></a>

- Whether a state gets resistance is decided by the scripted trigger `should_initiate_resistance` in `common/scripted_triggers/00_resistance_initiate_triggers.txt`. Scope is the state, `FROM` the occupier, `FROM.FROM` the occupied country (always the original tag). It runs when owner or controller changes and daily while resistance is active. [vanilla-confirmed 1.19.3] comments in that file.
- Vanilla version: the state is not impassable, `core_countries^num > 0` (the file's comment says "have no cores", but the check is for more than zero), and the state is never a core of the occupier; one extra branch is specific to Spain (`SPR_original_core`, `scw_over`). [vanilla-confirmed 1.19.3] same file.
- A trigger named `should_initiate_resistance_<id>_<id>` replaces it for those state ids, as in the commented examples of the file. See [Triggers](<triggers.md#Resistance_initiation_triggers>). [vanilla-confirmed 1.19.3] same file.
- `force_enable_resistance` and `start_resistance` start resistance in states the trigger would exclude, for example cores; `force_disable_resistance` and `cancel_resistance` stop it. [docs] `documentation/effects_documentation.md`.
- History files can set `set_resistance`, `set_compliance` and `start_resistance` per state, for example `history/states/1050-Ajteh.txt`. [vanilla-confirmed 1.19.3] `history/states/`.

## Minimal example <a id="Minimal_example"></a>

All three blocks follow vanilla shapes. [vanilla-confirmed 1.19.3] shape only; ids and numbers are made up.

`common/occupation_laws/my_mod_laws.txt`

```text
my_mod_garrison_tax = {
	icon = 8
	sound_effect = "Martial_Law_Interface_Forced_Labor_Occupation"
	fallback_law = military_governor_occupation
	visible = {
		has_completed_focus = MYM_garrison_tax
		FROM = { original_tag = POL }
	}
	state_modifier = {
		resistance_target = -0.2
		compliance_gain = -0.03
		required_garrison_factor = 0.1
		local_resources = 0.2
	}
	ai_will_do = {
		base = 0
		modifier = {
			check_variable = { resistance_target_without_law > 0.3 }
			add = 150
		}
	}
}
```

`common/resistance_activity/my_mod_activity.txt`

```text
sabotage_my_mod_radio = {
	available = {
		non_damaged_building_level = { building = radar_station level > 0 }
	}
	weight = { base = 1 }
	effect = {
		damage_building = { type = radar_station damage = 0.25 }
	}
	alert_text = building_is_sabotaged
}
```

`common/resistance_compliance_modifiers/my_mod_modifiers.txt`

```text
my_mod_resistance_60 = {
	type = state_resistance_modifier
	icon = "GFX_occupation_resistance_modifier_strip:3"
	small_icon = "GFX_occupation_resistance_modifier_small_strip:3"
	threshold = 60
	margin = 2
	state_modifier = {
		resistance_damage_to_garrison = 0.5
	}
}
```

Localisation: `my_mod_garrison_tax`, `sabotage_my_mod_radio` and `my_mod_resistance_60` are the name keys (for example `my_mod_garrison_tax: "Garrison Tax"`); `building_is_sabotaged` already exists. Set the law with `set_occupation_law = my_mod_garrison_tax` in an effect, or let the AI pick it by weight. [vanilla-confirmed 1.19.3] `resistance_and_occupation_l_english.yml` for the key pattern.

## Traps <a id="Traps"></a>

- Do not mark a second law `default_law = yes` or `starting_law = yes`; vanilla has exactly one of each, and `main_fallback_law` from the header is unused. [vanilla-confirmed 1.19.3] `occupation_laws.txt`; the effect of a second marker is [unverified].
- `visible` of a law is also read with `FROM` set, although the header says otherwise. Test `FROM` there only when you accept this. [vanilla-confirmed 1.19.3] 10 of 15 vanilla `visible` blocks.
- Use `small_icon` and `core_compliance_modifier`, the vanilla spellings, not the header's `icon_small` and `core_compliancemodifier`. [vanilla-confirmed 1.19.3] all 9 vanilla modifiers.
- Modifier thresholds are percentages (0 to 100). A threshold of 0.5 means half a percent. [unverified] inferred from the vanilla values 15 to 90.
- `is_dynamic = yes` modifiers are never active unless a script adds them with `add_state_resistance_compliance_modifier`. [docs] header of `resistance_modifiers.txt`.
- The operations that feed sabotage change variables on the selected state (`FROM.FROM` in operation scope). Vanilla activities that read these variables spend them with `subtract_from_variable`; a custom activity that reads one should do the same. [vanilla-confirmed 1.19.3] `common/operations/00_operations.txt`, `resistance_activity.txt`.

---

## Navigation

**[Modding](<modding.md>)**

- **Documentation**: [Effects](<effects.md>) • [Triggers](<triggers.md>) • [Defines](<defines.md>) • [Modifiers](<modifiers.md>) • [List of modifiers](<list-of-modifiers.md>) • [Scopes](<scopes.md>) • [Localisation](<localisation.md>) • [On actions](<on-actions.md>) • [Data structures](<data-structures.md>) • [Flags](<data-structures.md#Flags>) • [Event targets](<data-structures.md#Event_targets>) • [Country tag aliases](<data-structures.md#Country_tag_aliases>) • [Variables](<data-structures.md#Variables>) • [Arrays](<data-structures.md#Arrays>)
- **Scripting**: [Achievements](<achievement-modding.md>) • [AI](<ai-modding.md>) • [AI focuses](<ai-focuses.md>) • [Autonomous states](<autonomy-state-modding.md>) • [Balances of power](<balance-of-power-modding.md>) • [Bookmarks/Scenarios](<bookmark-modding.md>) • [Game rules](<bookmark-modding.md#Game_rules>) • [Buildings](<building-modding.md>) • [Characters and traits](<character-modding.md>) • [Cosmetic tags](<cosmetic-tag-modding.md>) • [Countries](<country-creation.md>) • [Divisions](<division-modding.md>) • [Decisions](<decision-modding.md>) • [Doctrines](<doctrine-modding.md>) • [Equipment](<equipment-modding.md>) • [Events](<event-modding.md>) • [Factions](<faction-modding.md>) • [Ideas](<idea-modding.md>) • [Ideologies](<ideology-modding.md>) • [Military industrial organizations](<military-industrial-organization-modding.md>) • [National focuses](<national-focus-modding.md>) • [Resources](<resources-modding.md>) • [Scripted GUI](<scripted-gui-modding.md>) • [Technologies and doctrines](<technology-modding.md>)
- **Map**: [Map](<map-modding.md>) • [States](<state-modding.md>) • [Supply areas](<supply-areas-modding.md>) • [Strategic regions](<strategic-region-modding.md>)
- **Graphical**: [Interface](<interface-modding.md>) • [Graphical assets](<graphical-asset-modding.md>) • [Entities](<entity-modding.md>) • [Posteffects](<posteffect-modding.md>) • [Particles](<particle-modding.md>) • [Fonts](<font-modding.md>)
- **Cosmetic**: [Portraits](<portrait-modding.md>) • [Namelists](<namelist-modding.md>) • [Music](<music-modding.md>) • [Sound](<sound-modding.md>)
- **Other**: [Console commands](<console-commands.md>) • [Troubleshooting](<troubleshooting.md>) • [Mod structure](<mod-structure.md>) • [Mods](<mods.md>) • [Nudger](<nudger.md>)
- **Kit pages (not on the wiki)**: [Collection modding](<collection-modding.md>) • [Game rule modding](<game-rule-modding.md>) • [Intelligence operation modding](<intelligence-operation-modding.md>) • [Map mode modding](<map-mode-modding.md>) • [Occupation and resistance modding](<occupation-and-resistance-modding.md>) • [Peace conference modding](<peace-conference-modding.md>) • [Raid modding](<raid-modding.md>) • [Script constant modding](<script-constant-modding.md>) • [Special project modding](<special-project-modding.md>)
