# AI modding

<!-- kit:begin id="review" build="1.19.4.1" checked="2026-11-01" revision="105110" sources="common/ai_strategy/ common/ai_strategy_plans/ common/ai_areas/ common/ai_focuses/ common/ai_templates/ common/ai_equipment/ common/ai_navy/ common/ai_faction_theaters/ common/peace_conference/ai_peace/ common/factions/_documentation.md common/defines/00_defines.lua documentation/triggers_documentation.md documentation/modifiers_documentation.md documentation/console_commands_documentation.md documentation/dynamic_variables_documentation.md documentation/effects_documentation.md" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Checked against: every `_documentation.md` of the AI folders (strategy, templates, equipment, navy, taskforce, faction theaters, peace) and the vanilla files of each folder, counted by script.
- Kit blocks added: strategy file keys, 32 documented strategy tokens the page lacked, 6 vanilla-only tokens, unit ratio rules, AI areas wrapper, peace corrections (including `take_navy`), strategy plan facts and fixes, template and equipment additions, and bottom sections for AI navy, task forces, faction theaters and the documented AI triggers, modifiers and console commands.
- Errors found: `take_navy` is not a peace action type and the pre-1.12 `common/ai_peace/` folder is gone; the "outdated" pointer to `documentation.info` leads nowhere (`_documentation.md` is the real list); `FORCE_CONCENTRATION_UNIT_RATIO_BASE` is `NAI.AIFC_UNIT_RATIO_BASE`; the plan example trait `fascist_demagouge` is `fascist_demagogue`; the AI areas example lacks the `areas = { }` wrapper; `allowed_types` is in neither the docs nor vanilla.
- Gaps left: meaning of `template_prio`, `save_equipment`, `ai_wanted_divisions_factor` and the other tokens the documentation lists without a description is unverified; peace `ai_desire` scale is covered on the Peace conference page.
**1.19.4.1 re-check (2026-11-01).** 65 statements (counting each bullet and table row) depended on files the update changed, and all of them were re-measured on the 1.19.4.1 files and added a `stockpile_fuel` row. Changed: documented tokens 104 to 105 (32 missing from the tables, 6 vanilla-only instead of 9), strategy blocks 925 to 968 in 50 files, AI areas 56 to 57, AI peace files 15 to 16, plan files testing `is_historical_focus_on = yes` 72 to 70, several "Used" counts, and a few wording fixes where the files disagreed with older text (`convoy_raiding_target`, `naval_dominance`, `template_prio` and `front_role_override` values, `ai_front_id`). Every other statement cites files that are byte-identical in 1.19.4.1 (Steam depot manifest diff).
<!-- kit:end id="review" -->

<!-- kit:begin id="ai-strategy-file-keys" at="section:arguments" -->
Facts about `common/ai_strategy/` in 1.19.4.1. All lines: [vanilla-confirmed 1.19.4.1] `common/ai_strategy/*.txt`, counted by script, unless tagged [docs] `common/ai_strategy/_documentation.md`.

- 968 strategy blocks in 50 files: `default.txt`, `doctrines.txt`, `operatives_default.txt`, `generic_operation_strats.txt`, three `*_operation_strats.txt` files and one file per country. Keys at the top of a block: `enable` (968), `allowed` (841), `abort_when_not_enabled` (608), `abort` (367), `reversed` (9), `enable_reverse` (4), and `ai_strategy` (2684 entries in all).
- The documentation asks for either `abort` or `abort_when_not_enabled` in every block, and says to write `abort = { always = no }` for a strategy that should never end. It calls `allowed` a first-step filter that should avoid expensive triggers. [docs]
- Entry keys vanilla uses besides `type`, `id` and `value`: `target` (149), `ratio` (134), `state` and `states`, `area`, `tag`, `strategic_region`, `ordertype`, `execution_type`, `priority`, `execute_order`, `manual_attack`, `target_country` (21), `mission`, `mission_target`, `operation`, `operation_target`, `equipment_type`, `seller`, `num_operatives`, `country_trigger`, `state_trigger`, `order_id`, `subtract_invasions_from_need` and `subtract_fronts_from_need`.
- `add_ai_strategy` is a country effect with the same block as an entry: `add_ai_strategy = { type = contain id = "SOV" value = -800 }` (`common/scripted_effects/00_scripted_effects.txt`). [docs] `documentation/effects_documentation.md` (one-line description).
- The `BHR_*` strategy names on this page (`BHR_invade_qatar`, `BHR_support_neutrals`) and `BHR_ai_behavior` are invented examples. Real ids follow `<TAG>_ai_behavior`, see the game rule notes on [Bookmark modding](bookmark_modding.md#game-rules-1).
<!-- kit:end id="ai-strategy-file-keys" -->

<!-- kit:begin id="ai-types-doc-pointer" at="heading:types" -->
The file named in the next paragraph, `common/ai_strategy/documentation.info`, does not exist in 1.19.4.1. The folder holds `common/ai_strategy/_documentation.md`, headed "updated 2024-11", with 105 strategy tokens in seven groups (diplomacy, fronts and armies, navies, intelligence, production and resources, airforce, raids). This page's tables list 73 of them. The block `ai-types-missing` after the tables lists the 32 it lacks (1.19.4.1 added `stockpile_fuel`), and `ai-types-vanilla-only` adds the 6 types that vanilla uses without the documentation listing them. [docs] `common/ai_strategy/_documentation.md`; [vanilla-confirmed 1.19.4.1] folder listing of `common/ai_strategy/`.
<!-- kit:end id="ai-types-doc-pointer" -->

<!-- kit:begin id="ai-types-missing" at="section:types" -->
The 32 strategy tokens of the documentation's list that no table above names. `id` is the target unless stated. "Used" counts strategy entries in vanilla `ai_strategy/` and `ai_strategy_plans/` (a lower bound). All rows: [docs] `common/ai_strategy/_documentation.md` for token, parameters and meaning; [vanilla-confirmed 1.19.4.1] for "Used" and for the vanilla values named in rows. Define values quoted in rows: [vanilla-confirmed 1.19.4.1] `common/defines/00_defines.lua`. Cells marked [unverified] have no description in the documentation.

| Type | Parameters | Meaning and value | Used |
| --- | --- | --- | --- |
| `avoid_starting_wars` | `value` | Targetless and additive with `conquer`; for narrow situations only. Doc example: -200 here plus `conquer` 200 on GER leaves GER at 0 and everyone else at -200. Vanilla writes -400 in `default.txt` | 5 |
| `naval_invasion_dominance_weight` | `value` | Makes the AI spend more of its navy on supremacy in regions that its naval invasions pass through. Doc example 30; vanilla 30, 40 and 50 in `USA.txt` | 3 |
| `naval_dominance` | `id` = AI area key or strategic region id, `value` | Wanted naval dominance in that area as a percentage, 0 to 100 (vanilla also writes -100 in `ENG.txt` and `USA.txt`, and 150 for two zones in `ENG.txt`) | 48 |
| `convoy_raiding_target` | `id` = country, `value` | Importance of convoy raiding against that country, percentage 0 to 100. Vanilla (`ENG.txt`, `JAP.txt`) instead writes a strategic region id as `id` (for example 18, the English Channel) and `value = 150`; comments there say the values sum per naval base and the objective asserts past 150 | 7 |
| `naval_blockade` | `target_country`, `id` = strategic region, `value` | Blockade importance, percentage 0 to 100. In the doc examples but not in its token list | 0 |
| `coast_defense` | `id` = strategic region, `value` | Coast defense importance, percentage 0 to 100. In the doc examples but not in its token list | 0 |
| `equipment_production_surplus_management` | `id` = equipment type, `value` | Weight of what to produce once all normal needs are met. Very high values can disturb the normal need calculation. Vanilla: `infantry_equipment` 10, `support_equipment` 5 | 6 |
| `equipment_market_spend_factories` | `value` | Factor on the define `NAI.EQUIPMENT_MARKET_MAX_CIVS_FOR_PURCHASES_RATIO` (0.1): 20 gives a factor of 1.2 | 3 |
| `equipment_market_for_sale_threshold` | `id` = equipment, `value` | Units of surplus needed before the AI offers the equipment for sale (absolute number) | 32 |
| `equipment_market_for_sale_factor` | `id` = equipment, `value` | Factor on `NAI.EQUIPMENT_MARKET_BASE_MARKET_RATIO` (0.2): 50 gives 1.5 | 8 |
| `equipment_market_max_for_sale` | `id` = equipment, `value` | Most units put on the market; a value of 0 is ignored | 1 |
| `equipment_market_min_for_sale` | `id` = equipment, `value` | Smallest lot on offer, kept in multiples; overrides `EQUIPMENT_MARKET_DEFAULT_CIC_CHUNK_FOR_SALE` (150) | 2 |
| `equipment_market_buying_threshold` | `id` = equipment archetype, `value` | Absolute units: 50 means buy 50 more than needed, -20 means buy only when the deficit exceeds 20 | 5 |
| `equipment_market_buy` | `equipment_type` and or `seller`, `value` | Part of the score of what to buy; at least one of the two keys. Related define `EQUIPMENT_MARKET_SCORE_FACTOR_AI_STRAT_WEIGHT` (50) | 4 |
| `equipment_market_trade_desire` | `id` = trade partner, `value` | Raises acceptance and desire to trade with that country | 13 |
| `research_tech` | `id` = technology, `value` | Forces research as soon as possible; any positive value | 0 |
| `air_xp_spend_priority`, `navy_xp_spend_priority` | `id`, `value` | Same ids as `land_xp_spend_priority`: `division_template`, `unlock_doctrine`, `equipment_variant`, `upgrade_xp_cutoff`, and `army_spirit`, `air_spirit` or `navy_spirit` matching the category | 1 and 2 |
| `raid_target_country` | `id` = country, `value` | Percentage change of the raid chance toward that country: 200 is +200 percent | 1 |
| `stockpile_fuel` | `start_below`, `stop_above`; both optional and both percentages of the AI's wanted max fuel; no `id`, `target` or `value` | Fuel saving mode: the AI pauses fuel-hungry operations until its reserves recover. `start_below` switches the mode on under that fuel level, `stop_above` keeps it on until fuel climbs above that level. More in the note below the table | 0 |
| `save_equipment` | `id` = equipment type, `value` | No description; vanilla writes `transport_plane_equipment` 10 and `support_equipment` 100 in `GER.txt`. Probably keeps stock back [unverified] | 9 |
| `template_prio` | `id`, `value` | No description; ids are unit or role tokens (`medium_armor` 21, `light_armor` 19, `cavalry` 17, `motorized` 16, `heavy_armor` 14, `paratroopers` 14, `infantry` 14 and others), values mostly -100 to 100 (10 entries use 111 to 200, and `militia` in `SWI.txt` uses 100000) [vanilla-confirmed 1.19.4.1] `common/ai_strategy/*.txt`, `common/ai_strategy_plans/*.txt` (143 uncommented entries) | 143 |
| `ai_wanted_divisions_factor` | `value` | No description; vanilla writes 100 and 1000 in `CHI.txt` [vanilla-confirmed 1.19.4.1] `common/ai_strategy/CHI.txt` | 6 |
| `occupation_policy`, `influence`, `activate_crypto`, `decrypt_target` | `id` = country | Listed without description; each has a readable variable `ai_strategy_<type>@<country>` [docs] `documentation/dynamic_variables_documentation.md` | 0 |
| `build_airplane`, `build_ship` | | Listed without description. The unit ratio text says the game itself sets `build_airplane` values from `unit_ratio`, so do not script it | 0 |
| `convoy_efficiency_to_cancel_trades`, `min_convoy_efficiency_factor_for_war_support_hit`, `fuel_buffer`, `wanted_supply_trucks`, `wanted_supply_trains` | `value` | Listed without description; the page already covers `min_wanted_supply_trucks` and `min_wanted_supply_trains` | 0 |

Notes on rows of the table above:

- `stockpile_fuel`: while the mode is on, the fuel budget of air and naval missions is throttled and land attack plans are stood down, plans already executing included. Army fuel use itself is not throttled, so units already moving, exercising or in combat keep burning fuel. `stop_above` must be above `start_below`; an inverted pair, a `start_below` without `stop_above` and a block with neither are errors on load. `stop_above` alone adds no trigger and only replaces the default recovery threshold, the define `NAI.FUEL_RATIO_TO_EXIST_FUEL_SAVING_MODE` (0.6, so 60 percent). Wanted max fuel follows the country's maximum army, navy and air fuel use (the `WANTED_MAX_FUEL_BUFFER_IN_DAYS_FOR_*` defines, 60 days each), can be scaled with `fuel_buffer`, and is capped at the real fuel capacity, so a `stop_above` near 100 asks for a nearly full stockpile. Several active blocks do not add up: the strictest value of each threshold wins. `front_control` with `execute_order = yes` and fronts the AI considers desperate override it, faction attack pings do not. Doc example: `start_below = 30`, `stop_above = 80`

All 32 tokens (and `naval_blockade`, `coast_defense`) are also standalone strings in the 1.19.4.1 `hoi4.exe`. [unverified] read-only grep, no test.
<!-- kit:end id="ai-types-missing" -->

<!-- kit:begin id="ai-types-vanilla-only" at="section:types" -->
Types that vanilla uses but the 1.19.4.1 token list does not contain. All rows: [vanilla-confirmed 1.19.4.1] `common/ai_strategy/*.txt`; meaning of `recruit_scientist` and `naval_invasion_support_priority` is read from the ids, not stated in a game file [unverified].

| Type | Seen as | Used |
| --- | --- | --- |
| `spent_faction_initiative_priority` | `id` = `program`, `unlock_doctrine_sharing` or `unlock_faction_commander`, `value`. Ids and meaning are in `common/factions/_documentation.md` [docs]; see the end of [Faction modding](faction_modding.md) | 9 |
| `become_head_of_crypto`, `become_head_of_counter_intel`, `become_head_of_operations` | `value` only; the same shape as `become_spymaster`, listed in `common/factions/_documentation.md` [docs] | 2, 1, 1 |
| `recruit_scientist` | `id = specialization_land` or `specialization_nuclear`, `value = 100`, in `default.txt`. Probably weighs which scientist specialization to recruit | 4 |
| `naval_invasion_support_priority` | `id` = strategic region number (the comment says "Central Mediterranean" for 29), `value = 200` for five regions and 25 and then -100 for region 84, in `ENG.txt`. Probably raises where invasion support goes | 7 |
<!-- kit:end id="ai-types-vanilla-only" -->

<!-- kit:begin id="ai-types-corrections" at="section:types" -->
Three fixes to the tables above.

- `force_concentration_factor` refers to `FORCE_CONCENTRATION_UNIT_RATIO_BASE`. No such define exists in `common/defines/00_defines.lua` or `hoi4.exe`. The matching define is `NDefines.NAI.AIFC_UNIT_RATIO_BASE = 0.15`: after front minimums are met, this share of the extra units goes to force concentration. [vanilla-confirmed 1.19.4.1] `common/defines/00_defines.lua`; the documentation uses the wrong name too. [docs] `common/ai_strategy/_documentation.md`.
- The `front_unit_request` and `invasion_unit_request` rows say `tag` is "the state to target" and `area` is `<state>`. `tag` is a country tag and `area` is an AI area key. [docs] `common/ai_strategy/_documentation.md`.
- `invade`: a negative value makes the AI avoid invading that country at all; a positive value multiplies the importance of invasions against it while it is a potential enemy (60 means 1.6 times). `dont_defend_ally_borders` is binary, any value above 0 turns it on. [docs] `common/ai_strategy/_documentation.md`.
<!-- kit:end id="ai-types-corrections" -->

<!-- kit:begin id="ai-unit-ratios" at="section:types" -->
How `unit_ratio`, `role_ratio` and `equipment_production_factor` turn into numbers. All lines: [docs] `common/ai_strategy/_documentation.md`; the define values are [vanilla-confirmed 1.19.4.1] `common/defines/00_defines.lua` (`NDefines.NAI`).

- Land, naval and other non-air types: the wanted share is 100 plus the strategy value. A `unit_ratio` of -40 gives 60 percent of the wanted number. `equipment_production_factor` works the same way on the factory count that the need calculation yields.
- Air types are weights, not percentages. A type without a `unit_ratio` has weight 0, and a plane type locked by a missing DLC is treated as 0. Land-based and carrier planes are counted separately.
- Wanted land-based planes: total air base capacity (without carriers) times `WANTED_LAND_PLANES_PER_BASE_CAPACITY_FACTOR` (1), plus wanted divisions times `WANTED_LAND_PLANES_PER_DIVISION` (20), minus planes already in air wings, limited to 0 and to wanted divisions times `WANTED_LAND_PLANES_TOTAL_MAX_PER_DIVISION` (100). The result is multiplied by the hard-coded aviation focus value, which `ai_focus_aviation_factor` has already scaled.
- Wanted carrier planes: carrier deck capacity times `WANTED_CARRIER_PLANES_PER_CARRIER_CAPACITY_FACTOR` (1.5), plus deck capacity of carriers finishing within `CARRIER_CAPACITY_IN_PRODUCTION_MAX_DAYS_LEFT_TO_INCLUDE_FACTOR` (365) days times `WANTED_CARRIER_PLANES_PER_CARRIER_CAPACITY_IN_PRODUCTION_FACTOR` (1), minus carrier planes in air wings, at least 0. The result is multiplied by the naval air focus value, scaled by `ai_focus_naval_air_factor`.
- Each plane type then gets its `unit_ratio` divided by the sum of the `unit_ratio` values of its group, times the wanted total; that sets the `build_airplane` values.
<!-- kit:end id="ai-unit-ratios" -->

<!-- kit:begin id="ai-areas-wrapper" at="section:ai-areas" -->
The example above leaves out the root block. Vanilla `common/ai_areas/default.txt` is one `areas = { ... }` block holding every area, for example `areas = { suez = { strategic_regions = { 128 28 232 } } ... }`. It defines 57 areas; 51 use `strategic_regions` and 6 use `continents`, and no area uses another key. [vanilla-confirmed 1.19.4.1] `common/ai_areas/default.txt`. Write the wrapper as vanilla does. An area id defined in a file without it was not known: an AI strategy that used the id drew "Malformed token" at load, exactly as an id defined nowhere did, and an id from a file with the wrapper drew no line. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, error.log read. The evidence is the strategy loader's complaint about the ids, and the AI's behaviour with the areas was not observed.

Strategies that take an AI area key: `area_priority`, `front_control`, `front_unit_request`, `invasion_unit_request`, `force_concentration_front_factor`, `force_concentration_target_weight`, `put_unit_buffers` (`area`) and `naval_dominance` (`id`, a key or a region id). [docs] `common/ai_strategy/_documentation.md`.
<!-- kit:end id="ai-areas-wrapper" -->

<!-- kit:begin id="ai-focuses-content-fix" at="section:ai-focuses" -->
`common/ai_focuses/` files do not choose national focuses. In 1.19.3 each block holds only `research = { <technology category> = <weight> }`. National focus lists belong to strategy plans (`ai_national_focuses`, `focus_factors`) below. The nine focus ids, their `ai_focus_<x>_factor` modifiers and the file format are on [AI focuses](ai_focuses.md). [vanilla-confirmed 1.19.3] `common/ai_focuses/*.txt`.
<!-- kit:end id="ai-focuses-content-fix" -->

<!-- kit:begin id="ai-peace-1193" at="heading:ai-peace" -->
This section is partly outdated for 1.19.4.1. The checked reference is [Peace conference modding](peace_conference_modding.md). What differs:

- The "Pre-1.12" folder `common/ai_peace/` does not exist in 1.19.4.1. The only peace AI folder is `common/peace_conference/ai_peace/` (16 files: `00_misc.txt`, `yalta.txt`, `warlords.txt` and country files). The old action blocks `annex`, `puppet_all` and `puppet_state` have no counterpart: entries now have exactly `peace_action_type`, `enable` and `ai_desire`. [vanilla-confirmed 1.19.4.1] `common/peace_conference/ai_peace/`, folder listing of `common/`.
- The documented action types are `take_states`, `puppet`, `force_government` and `liberate`. `take_navy`, listed above as a fifth type, is not one: no vanilla file uses it as a `peace_action_type`, so give a `take_navy` AI desire no weight. [docs] `common/peace_conference/ai_peace/_documentation.md`; [vanilla-confirmed 1.19.4.1] `common/peace_conference/` (no file contains `take_navy`).
- Scopes in an entry, as the documentation states them: `ROOT` is the negotiator, `FROM` the taker (who owns the result), `FROM.FROM` the giver and `FROM.FROM.FROM` the state. The text above calls `FROM` the country that undergoes the action; that reading differs. [docs] `common/peace_conference/ai_peace/_documentation.md`.
- All active entries for an action are summed and a total of 0 or lower means the AI does not take it; the documentation example also reads `ai_desire = 100` as +100 percent. The -1000 and 1000 meanings stated above are not in the documentation. The scale is discussed on the Peace conference page. [docs] `common/peace_conference/ai_peace/_documentation.md`.
- `dont_puppet_warlord_countries` in the example is an invented name. The real warlord entry is `warlords_want_to_conquer_china` in `warlords.txt`. [vanilla-confirmed 1.19.4.1] `common/peace_conference/ai_peace/` (the invented name occurs in no file).
<!-- kit:end id="ai-peace-1193" -->

<!-- kit:begin id="ai-plans-1193" at="section:ai-strategy-plans" -->
Facts about plans in 1.19.4.1. All lines: [vanilla-confirmed 1.19.4.1] `common/ai_strategy_plans/*.txt`, counted by script.

- 376 plan blocks in 128 files. Top-level keys and how often they occur: `enable` 376, `abort` 368, `name` 366, `allowed` 366, `ideas` 365, `desc` 364, `weight` 362, `ai_national_focuses` 352, `research` 351, `focus_factors` 252, `traits` 125, `ai_strategy` 61. A plan can repeat a key: `focus_factors` sits in 250 plans and the 61 `ai_strategy` entries sit in 32 plans. No other top-level key occurs, so the key list above is complete.
- `weight` is a weight block: 361 plans use `modifier` and 359 use `factor`. `research` keys are technology categories such as `artillery` (96 plans), `infantry_tech` (88), `support_tech` (88) and `industry` (87). `traits` lists country leader or advisor trait ids such as `captain_of_industry` (75 plans) and `war_industrialist` (56). `ideas` lists idea ids and spirits.
- 70 plan files test `is_historical_focus_on = yes` in `enable`, usually together with `has_game_rule` (68 of them). Plan ids and file names follow `<TAG>_historical_strategy_plan` and `<TAG>_alternate_strategy_plan` by habit, nothing requires it.
- 124 plan files carry an `ai_national_focuses` list; `focus_factors` of 0 bans a focus (`GER_prioritize_economic_growth = 0` in `GER_historical_strategy_plan.txt`).
<!-- kit:end id="ai-plans-1193" -->

<!-- kit:begin id="ai-plan-example-fixes" at="section:example-1" -->
In the example, `traits = { fascist_demagouge = 0 }` has a misspelled id. The country leader trait is `fascist_demagogue`, defined in `common/country_leader/00_traits.txt`; the misspelled key matches no trait. `BHR_historical`, `BHR_alternate`, `BHR_advisor`, `BHR_focus_name_1` to `5`, `BHR_ai_behavior` and the `BHR_AI_RANDOM_*` flags are placeholders, as is the `OMA` abort condition. [vanilla-confirmed 1.19.4.1] `common/country_leader/00_traits.txt` (`fascist_demagogue`). A typo'd key is ignored without an error: plans with the misspelled key, the right spelling and a trait that exists nowhere all loaded with no log line, and the game ran 4 days. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, error.log read. Only the missing log line was observed, so nothing shows that the plans were evaluated for those countries.

Game rule options named in `has_game_rule` must be option names of a rule in `common/game_rules/`; vanilla uses `DEFAULT`, `FASCIST`, `DEMOCRATIC`, `RANDOM` and similar. See [Bookmark modding](bookmark_modding.md#game-rules-1). [vanilla-confirmed 1.19.3] `common/ai_strategy_plans/GER_historical_strategy_plan.txt`.
<!-- kit:end id="ai-plan-example-fixes" -->

<!-- kit:begin id="ai-templates-1193" at="section:ai-templates" -->
What the 1.19.4.1 documentation and vanilla add for division templates.

- The documentation (headed "updated 2024-08") says the system was reworked in 2023-10 and that some old parameters are being deprecated or renamed. It names two debug commands: `imgui show ai_templates` (targeted templates and best matches) and `imgui show ai_division_production` (divisions wanted per role). [docs] `common/ai_templates/_documentation.md`.
- Vanilla has 69 role entries and 143 target templates in 15 files. Role-level keys: `role`, `upgrade_prio` (all), `available_for` (58), `blocked_for` (7) and `front_role_override = offence` (2: `mechanized_assault` for GER and `heavy_armor` for SOV; the `front_armor_score` documentation mentions it). No vanilla role entry has a role-level `enable`, though the list above gives one: the only `enable` in vanilla (`templates_JAP.txt`) sits inside a target template. [vanilla-confirmed 1.19.4.1] `common/ai_templates/*.txt`. The documentation's role example shows none either. [docs] `common/ai_templates/_documentation.md`. The engine does not accept one at role level: an `enable = { always = no }` block directly next to `role =` logged "Unexpected token: always" with the line inside the block, while an `enable` inside a target template drew no error. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, error.log read. The test file was new, not a copy of a vanilla templates file, and the AI's template behaviour was not compared.
- Target-template keys in vanilla: `upgrade_prio` and `target_template` (143 each), `division_names_group` (54), `custom_icon` (20), `reinforce_prio` and `replace_at_match` (19 each), `replace_with` and `target_min_match` (18 each), `can_upgrade_in_field` (7), `enable` (1). [vanilla-confirmed 1.19.4.1] `common/ai_templates/*.txt`.
- `target_template` takes `regiments` (143), `support` (142) and `regimental_support` (114): `regimental_support = { anti_air_battery = 1 mot_fire_support = 1 }` in `templates_GER.txt`. The block is in neither the template documentation nor the list above. [vanilla-confirmed 1.19.4.1] `common/ai_templates/*.txt`, the example is in `templates_GER.txt`.
- Role tokens vanilla defines: `armor`, `garrison`, `infantry`, `mountaineers`, `marines`, `paratroopers`, `militias`, `motorized`, `mobile`, `suppression`, `heavy_armor`, `anti_armor`, `mechanized_assault`, `irregular_infantry`, `rangers_role`, `hq_role`, `mega_heavy_breakthrough_role`, `super_heavy_breakthrough_role`. `role_ratio` strategies target these (313 uses). [vanilla-confirmed 1.19.4.1] `common/ai_templates/`, `common/ai_strategy/`.
- `infantry_1` and `infantry_2` in the example are free block names, as in the documentation's own example. Real vanilla names are like `light_armor_default_ENG` and `medium_armor_2_ENG`. [docs] `common/ai_templates/_documentation.md`.
- Triggers that read this system: `ai_has_role_template = <role>` (used in `ai_templates/generic.txt`), `ai_has_role_division`, `has_template_ai_majority_unit`. [docs] `documentation/triggers_documentation.md`.
<!-- kit:end id="ai-templates-1193" -->

<!-- kit:begin id="ai-equipment-1193" at="section:ai-equipment" -->
What the 1.19.4.1 documentation and vanilla add for equipment designs.

- Vanilla has 268 design groups with 822 designs in 22 files: `category = land` 147, `naval` 81 and `air` 40. The documentation notes that naval support began in 1.6.0 and land in 1.11.0; it does not name `air`, which vanilla uses (`generic_planes.txt` and others). [vanilla-confirmed 1.19.4.1] `common/ai_equipment/*.txt`; [docs] `common/ai_equipment/_documentation.md`.
- `available_for` and `blocked_for`: if `available_for` is empty every country not in `blocked_for` may use the group; if it is not empty only listed countries that are not in `blocked_for` may. So `blocked_for` still applies together with `available_for`, unlike the list above suggests. `generic_planes.txt` writes `blocked_for = {GER ENG USA ITA}` with an empty `available_for = {}`. [docs] `common/ai_equipment/_documentation.md`; [vanilla-confirmed 1.19.3] `common/ai_equipment/generic_planes.txt`.
- Design keys the list above lacks: `history = yes` (820 of 822 designs; the documentation says it decides the designer folder the design appears in), `visible = no` (9), `design_team = <id>` (1, `ENG_naval.txt`), and the capitalised `Name = illustrious_class` (1) next to `name` (82). `role_icon_index` appears in 296 designs, all in naval files. [docs] `common/ai_equipment/_documentation.md` (`history`); [vanilla-confirmed 1.19.4.1] `common/ai_equipment/*.txt`.
- `allowed_types`, described above, is in neither the documentation nor any vanilla `ai_equipment` file. Do not rely on it. [vanilla-confirmed 1.19.4.1] `common/ai_equipment/` (no match). [docs] `common/ai_equipment/_documentation.md` (no mention). Whether the engine still reads it is [unverified].
- `target_variant` always has `match_value`, `type` and `modules`; `upgrades` appears in 368 designs; `requirements` in 33; `enable` in 255. `upgrade > current` inside a slot block is used 12 times, all in naval files (the form `upgrade = current` that the documentation also shows is never used). A slot written `<slot> = empty` fails the match for any module; `<slot> > empty` fails only an empty slot. [vanilla-confirmed 1.19.4.1] `common/ai_equipment/*.txt`; [docs] `common/ai_equipment/_documentation.md`.
- `BHR_light_tanks` in the example is an invented group name. Roles are free tokens and also the ids of `role_ratio` strategies; vanilla naval roles include `naval_screen`, `naval_escort`, `naval_submarine`, `naval_carrier`, `naval_cruiser_light`, `naval_cruiser_heavy`, `naval_capital_bb`, `naval_capital_bc`, `naval_mine_layer` and `naval_mine_sweeper`. [vanilla-confirmed 1.19.4.1] `common/ai_strategy/*.txt`.
<!-- kit:end id="ai-equipment-1193" -->

<!-- kit:begin id="ai-navy-1193" at="bottom" -->
## AI navy goals, fleets and task forces

The goal-based naval AI replaces the older mission-priority system. It has three layers of files under `common/ai_navy/`. All of it is checked against `common/ai_navy/_documentation.md` and `common/ai_navy/taskforce/_documentation.md` [docs] and the vanilla files [vanilla-confirmed 1.19.3] (74 goals, 32 fleets, 61 task force templates, in 8 files each for goals, fleets and task forces: a generic file plus ENG, FRA, GER, ITA, JAP, SOV, USA).

**Goals** (`ai_navy/goals/goals_<TAG>.txt`). A goal is a type of operation; an objective is the goal applied to a target. All active objectives of a country are scored and executed from the best down. Score of an objective = `min_priority` + (`max_priority` - `min_priority`) times its importance, where importance is a value from 0 to 1. Doc example: naval invasion support with priorities 5 to 10 and importance 0.8 scores 9.0. [docs] `common/ai_navy/_documentation.md`.

```text
ENG_naval_invasion_support = {
    objective_type = naval_invasion_support
    available_for = { ENG }
    min_priority = 4
    max_priority = 14
}
```

Example: [vanilla-confirmed 1.19.3] `common/ai_navy/goals/goals_ENG.txt`.

- Keys: `objective_type`, `min_priority` and `max_priority` (all 74 goals), `available_for` (64) and `blocked_for` (10). With `available_for` present the goal is off for every other country; `blocked_for` switches it off for the listed ones. [docs]
- The documentation lists six objective types: `naval_invasion_support`, `naval_invasion_defense`, `mines_sweeping`, `coast_defense`, `convoy_protection`, `convoy_raiding`. Vanilla also uses `naval_dominance`, `mines_planting`, `training` (8 goals each) and `naval_blockade` (2). [docs]; [vanilla-confirmed 1.19.3] `common/ai_navy/goals/`.
- Debug with the console command `imgui show ai_navy`. [docs]

**Task force templates** (`ai_navy/taskforce/<TAG>_taskforce_templates.txt`). A template says which ships a task force wants and for which mission.

```text
GER_ConvoyRaiding_1 = {
    allowed = { original_tag = GER }
    ai_will_do = { factor = 1 }
    keep_updated = yes
    mission = { convoy_raiding }
    min_composition = { submarine = { amount = 4 } }
    optimal_composition = { submarine = { amount = 6 } }
}
```

Example: [vanilla-confirmed 1.19.3] `common/ai_navy/taskforce/GER_taskforce_templates.txt` (spaced onto fewer lines).

- Documented keys: `allowed` (country scope), `ai_will_do` (a weight, 0 or lower means the AI never uses the template), `mission` (a list, currently limited to one entry), `min_composition` and `optimal_composition`. [docs] `common/ai_navy/taskforce/_documentation.md`
- The documentation writes compositions as `carrier = 1`. Vanilla writes every ship type as a block with `amount`, and 24 composition entries add `role = 4`: `destroyer = { amount = 2 role = 4 }`. `keep_updated = yes` is set on 25 of the 61 templates and is not documented. [vanilla-confirmed 1.19.3] `common/ai_navy/taskforce/*.txt`.
- Ship types in vanilla compositions: `destroyer`, `light_cruiser`, `heavy_cruiser`, `battleship`, `battle_cruiser`, `submarine`, `carrier`. Missions in vanilla: `naval_patrol` (17), `convoy_raiding` (14), `naval_strike` (11), `mines_planting` (8), `convoy_escort` (8), `naval_invasion_support` (3). [vanilla-confirmed 1.19.3] `common/ai_navy/taskforce/*.txt`.

**Fleet templates** (`ai_navy/fleet/<TAG>_fleet_templates.txt`). Not covered by either documentation file. A fleet lists task force template ids and how many of each:

```text
generic_dominance_fleet_1 = {
    required_taskforces = { StrikeForce_1 = 1 PatrolReconForce_1 = 2 }
    optional_taskforces = { StrikeForce_1 = 1 PatrolReconForce_1 = 1 }
}
```

Example: [vanilla-confirmed 1.19.3] `common/ai_navy/fleet/generic_fleet_templates.txt` (shortened). Of 32 fleets in the 8 files of `common/ai_navy/fleet/`, 24 have `required_taskforces` and all 32 have `optional_taskforces` [vanilla-confirmed 1.19.4.1]. The documentation does not mention either key. The meaning of required and optional is read from the names [unverified].

Strategies that feed this system: `naval_dominance`, `naval_blockade`, `coast_defense`, `convoy_raiding_target`, `naval_invasion_dominance_weight`, `naval_invasion_support_priority`, `naval_mission_threshold`, `strike_force_home_base`. See `ai-types-missing`.
<!-- kit:end id="ai-navy-1193" -->

<!-- kit:begin id="ai-faction-theaters-1193" at="bottom" -->
## AI faction theaters

`common/ai_faction_theaters/ai_faction_theaters.txt` tells the AI which theaters a faction leader creates and which members it assigns. Keys per theater, from the documentation: `name` (loc key, faction leader loc scope), `ai_will_do` (how likely the AI creates it, scope the acting country), `cancel` (when the AI drops its theater), `regions` (strategic region ids, the area must be connected), `can_skip_first_region` and `preferred_countries` (priority list of members). By default the first region must be available to create the theater; `can_skip_first_region = yes` lets at least one available region suffice. [docs] `common/ai_faction_theaters/_documentation.md`.

Vanilla defines 30 theaters (`western_europe`, `eastern_europe`, `barbarossa_north`, `north_africa`, `chinese_coastline`, `central_pacific` and others). Every theater has `name`, `regions`, `cancel` and `ai_will_do`; only 3 use `preferred_countries` (for example `GER SLO`) and none use `can_skip_first_region`. [vanilla-confirmed 1.19.3] `common/ai_faction_theaters/ai_faction_theaters.txt`.

```text
western_europe = {
    name = theater_western_europe
    regions = { 19 5 7 208 6 18 1 275 20 42 21 }
    cancel = { has_war = no }
    ai_will_do = { base = 0 modifier = { add = 1 capital_scope = { is_on_continent = europe } } }
}
```

Example: [vanilla-confirmed 1.19.3] `common/ai_faction_theaters/ai_faction_theaters.txt` (the vanilla `cancel` and `ai_will_do` are longer; this keeps the shape). The `name` key `theater_western_europe` is localised in `localisation/english/factions_l_english.yml`.

Related defines (`NDefines.NFactions`): `MAX_FACTION_THEATERS` 4, `AI_THEATER_CREATION_PENALTY` 2.5 (each existing theater lowers the creation chance linearly), `AI_FACTION_THEATER_TEMPLATE_SELECTION_RANDOMNESS` 1, `AI_FACTION_THEATER_COMMANDER_SELECTION_RANDOMNESS` 1, `FACTION_UNLOCK_COMMANDER_COST` 1 (faction initiative). The AI spends that initiative through the strategy `spent_faction_initiative_priority` with `id = unlock_faction_commander`. [vanilla-confirmed 1.19.4.1] `common/defines/00_defines.lua`; [docs] `common/factions/_documentation.md`. See [Faction modding](faction_modding.md).
<!-- kit:end id="ai-faction-theaters-1193" -->

<!-- kit:begin id="ai-docs-surface-1193" at="bottom" -->
## Documented AI script surface

Items from the game documentation that read or steer the AI and that the page above never names.

| Name | Kind | What it does |
| --- | --- | --- |
| `is_ai` | trigger | True if the country is AI controlled |
| `ai_has_role_template`, `ai_has_role_division` | triggers | The AI country has a template, or fielded divisions, for a role |
| `has_template_ai_majority_unit` | trigger | The country has a division template whose majority unit matches, counted by AI priorities rather than visually |
| `ai_wants_divisions` | trigger | Compares with the number of divisions the AI wants |
| `ai_irrationality` | trigger and variable | The AI irrationality value |
| `ai_liberate_desire` | trigger | The liberation desire toward a given country |
| `ai_message` | effect | Documented only as "ai message... ?", no usable description |
| `ai_badass_factor`, `ai_call_ally_desire_factor`, `ai_desired_divisions_factor`, `ai_get_ally_desire_factor`, `ai_join_ally_desire_factor`, `ai_license_acceptance` | modifiers | Category `ai`; listed without description |
| `ai_focus_<x>_factor` | modifiers | Nine of them, see [AI focuses](ai_focuses.md) |
| `ai_strategy_<type>@<country>` | dynamic variable | Value of a strategy toward a country, for example `GER.ai_strategy_conquer@ENG`. Exists for `alliance`, `antagonize`, `befriend`, `conquer`, `consider_weak`, `contain`, `declare_war`, `dont_defend_ally_borders`, `force_defend_ally_borders`, `ignore`, `ignore_claim`, `invade`, `prepare_for_war`, `protect`, `send_volunteers_desire`, `support`, `influence`, `occupation_policy`, `activate_crypto`, `decrypt_target` |
| `ai_attitude_<x>_weight@<country>`, `ai_attitude_wants_<x>`, `ai_attitude_is_threatened` | dynamic variables | Weights of an AI attitude toward a country (allied, friendly, hostile, neutral, outraged, protective, threatened), and flags such as `ai_attitude_wants_ally`, which is 1 if the AI wants an ally; siblings exist for antagonize, ignore, protect and weaken |

All rows above: [docs] `documentation/triggers_documentation.md`, `effects_documentation.md`, `modifiers_documentation.md`, `dynamic_variables_documentation.md`.

Console commands for AI work. All rows: [docs] `documentation/console_commands_documentation.md`; several are marked "Not available in release build".

| Command | Use |
| --- | --- |
| `aiview` | Show AI debug info |
| `ai_accept` (alias `yesman`) | Toggle the AI accepting every diplomatic request |
| `ai_invasion` | Toggle AI naval invasions |
| `ai_force_equipment`, `ai_force_template` | Make the AI spend army XP only on equipment designs, or only on templates |
| `ai_idea_desire_log`, `ai_pp_log`, `ai_research_log` | Print AI idea desire, political power use and research choices to the log (the last is not in release builds) |
| `ai_dump`, `ai_front_dump`, `ai_front_id`, `ai_trace` | Dump AI data and fronts, get the front debug id of the selected group, or open the trace window; all but `ai_front_id` are not in release builds |
| `enable_ai`, `disable_ai`, `human_ai` | Switch the AI on or off, or give human countries AI control |
| `emulate_ai_operative_assignment` | Log what the operative AI would do this tick |
| `imgui show ai_templates`, `imgui show ai_division_production`, `imgui show ai_navy` | Debug views for templates, wanted divisions and naval goals. [docs] the AI template and AI navy documentation files |
<!-- kit:end id="ai-docs-surface-1193" -->
