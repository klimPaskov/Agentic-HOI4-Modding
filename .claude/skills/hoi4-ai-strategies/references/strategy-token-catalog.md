# AI strategy token catalog

Read this file when you need the exact parameters or value meaning of one `ai_strategy` type.
Primary source: the installed game's `common/ai_strategy/_documentation.md` (updated 2024-11), cross-checked against `paradox_wiki/AI modding - Hearts of Iron 4 Wiki.md` and the usage counts in vanilla `common/ai_strategy/*.txt`.
The token list there is the authority; if a token is missing here, read the installed file.
Tokens seen in vanilla but absent from the documentation list are marked "vanilla only".

## Contents

- Value conventions
- Diplomacy tokens
- Fronts, armies, and force concentration
- Navy tokens
- Production, ratios, and buildings
- Equipment market
- Research, PP, and XP spend
- Intelligence and operations
- Faction, scientist, and other vanilla-only tokens

## Value conventions

| Convention | Meaning | Tokens |
| --- | --- | --- |
| Additive weight | Summed with other active strategies of the same type and target. Sign matters. | `conquer`, `antagonize`, `befriend`, `ignore`, `alliance`, `protect`, `support`, `contain`, `consider_weak`, `prepare_for_war`, `declare_war`, desire and acceptance tokens |
| Percent factor | 50 means plus 50 percent of the perceived need or score, -30 means minus 30 percent. | `equipment_production_factor`, `research_weight_factor`, `front_unit_request`, `invasion_unit_request`, `force_concentration_*`, `unit_ratio` (non-air), `raid_target_country`, `equipment_market_*_factor` |
| Absolute count | An exact number of things. | `equipment_production_min_factories*`, `building_target`, `theatre_distribution_demand_increase`, `equipment_market_*_threshold`, `equipment_market_max_for_sale`, `equipment_market_min_for_sale` |
| Binary | Any positive value turns it on, zero or negative turns it off. | `dont_defend_ally_borders`, `ignore_claim` (documented as boolean 1) |
| Weighted selection | Compared against other strategies of the same type to pick one. | `build_building`, `operative_operation`, `operative_mission` |
| Percentage 0 to 100 | | `naval_dominance`, `convoy_raiding_target`, `naval_blockade`, `coast_defense` |

## Diplomacy tokens

All take `id = <country>` unless noted.
Examples are in `GAME/common/ai_strategy/default.txt`, `GER.txt`, `FRA.txt`, `SOV.txt`, `BUL.txt`.

| Token | Parameters | Meaning | Notes |
| --- | --- | --- | --- |
| `alliance` | id, value | Seek an alliance and the same faction. | Negative values block seeking. |
| `antagonize` | id, value | Treat as a potential war target and refuse most diplomatic actions. | |
| `avoid_starting_wars` | value | Targetless, additive with `conquer`. | "Very specific situations, should not be used widely." Pair with a positive `conquer` on one target to whitelist it. |
| `asking_foreign_garrison` | id (optional), value | Ask for foreign manpower for garrisons. | No `id` applies to everyone. |
| `befriend` | id, value | Accept and propose friendly actions. | |
| `conquer` | id, value | Prefer for war declaration and wargoal justification. | Does not change frontline control. |
| `consider_weak` | id, value | Lowers hesitation to declare war and makes alliance less likely. | |
| `contain` | id, value | Protect whoever the target would antagonize or invade. | Vanilla uses -800 to disable. |
| `declare_war` | id, value | Declare war if a wargoal already exists. | |
| `diplo_action_acceptance` | id, target, value | Raise or lower acceptance of one action requested by `id`. | Does not make the AI propose it. |
| `diplo_action_desire` | id, target, value | Desire to request one action toward `id`. | Does not make the target accept it. |
| `dont_join_wars_with` | id, target_country, value | Avoid joining a war with `id` against `target_country`. | Does not affect joining with other partners against that target. |
| `ignore` | id, value | Reduce desire and acceptance of any diplomatic action. | |
| `ignore_claim` | id, value = 1 | Ignore own claims on `id`. | Boolean. |
| `influence` | id, value | In the token list; no example in the documentation. | Unverified semantics. |
| `prepare_for_war` | id, value | Move troops to the target's border. | |
| `protect` | id, value | Guarantee or add to faction. | Negative total: never guarantee. |
| `send_lend_lease_desire` | id, value | Desire to lend-lease. | Defines such as `PROPOSE_LEND_LEASE_AIDESIRE_SAME_IDEOLOGY` add to it. |
| `send_volunteers_desire` | id, value | Desire to send volunteers. | `SEND_VOLUNTEER_AIDESIRE_SAME_IDEOLOGY` adds to it. |
| `support` | id, value | Aid in wars: lend-lease, volunteers, expeditionary forces. | |

Diplomatic action names for `target`: derive from localisation `DIPLOMACY_<NAME>_TITLE` keys in `localisation/english/diplomacy_l_english.yml` (wiki).
Vanilla-observed values: `improve_relation`, `military_access`, `docking_rights`, `offer_docking_rights`, `air_base_access`, `offer_air_base_access`, `call_allies`, `join_allies`, `guarantee`, `market_access_rights`, `befriend`.

## Fronts, armies, and force concentration

| Token | Parameters | Meaning |
| --- | --- | --- |
| `area_priority` | id = AI area key, value | Prefer putting units in the area (vanilla values 0 to 110). |
| `dont_defend_ally_borders` | id = country, value | Binary. Ignore frontlines belonging to that ally. |
| `force_defend_ally_borders` | id = country or AI area, value | Put troops on the ally's borders with its enemies. |
| `front_armor_score` | id, value | Make divisions with `role = armor` or `front_role_override = offence` more likely to be assigned to a front against `id`. |
| `front_control` | tag / state / strategic_region / area / country_trigger / state_trigger, ratio, priority, ordertype, execution_type, execute_order, manual_attack | Modify orders on an existing front or invasion. `ordertype` is `front` or `invasion`; `execution_type` is `careful`, `balanced`, `rush`, or `rush_weak`; `execute_order` is yes or no; `manual_attack` defaults to yes. `ratio` is the minimum share of the front covered by the targets. Higher `priority` wins on conflict. Multiple target kinds must all match. |
| `front_unit_request` | target selectors as above, value | Percent factor on units requested for fronts. Value is added "as a factor over regular requests". |
| `invasion_unit_request` | target selectors as above, value | Same for naval invasions; checks the invasion target. |
| `garrison` | value | Share of units on victory point and port garrisons versus the line. |
| `garrison_reinforcement_priority` | value | Reinforce garrison units earlier. |
| `ignore_army_incompetence` | value | Ignore the division inexperience modifier in AI calculations. |
| `invade` | id, value | Naval invasions against `id`. Negative avoids invading completely; positive multiplies the importance of invasions against a potential enemy (60 means times 1.6). |
| `occupation_policy` | in token list | No documented example. |
| `put_unit_buffers` | ratio, order_id, states = { ... }, area = ..., subtract_invasions_from_need, subtract_fronts_from_need | Hold a share of total armies as buffers/garrisons for orders in the listed areas. Same `order_id` share one ratio. If no listed state is friendly the strategy is invalid. |
| `spare_unit_factor` | value | Spare more units to defend allies. |
| `theatre_distribution_demand_increase` | id = state id, value | Raise unit demand (value 10 means 10 units) in the theatre containing the state. |
| `scorched_earth_prio` | id = owner country, states = { ... }, value | Use scorched earth in those states. |
| `force_concentration_factor` | value | Added to the base share of "non-essential" units used for concentrated pushes (`FORCE_CONCENTRATION_UNIT_RATIO_BASE`); 20 means plus 20 points. A large negative value disables force concentration. |
| `force_concentration_front_factor` | selectors, ratio, value | Percent factor for concentration priority on matching fronts. |
| `force_concentration_target_weight` | selectors, value | Percent factor for offensive target score. |

Selector semantics in `country_trigger` and `state_trigger`: country scope is the enemy country with FROM as the AI's own country; state scope is the state with FROM the enemy country and FROM.FROM the AI's own country.

## Navy tokens

`naval_avoid_region` (id = strategic region), `naval_convoy_raid_region` (region), `naval_invasion_focus` (value), `naval_invasion_dominance_weight` (value), `naval_mission_threshold` (id = mission token; higher value means less likely; token derives from `NAVAL_MISSION_NAME_<X>` in `core_l_english.yml` as `MISSION_<X>`), `strike_force_home_base` (region), `naval_dominance` (id = AI area key or region id, value 0 to 100), `convoy_raiding_target` (id = country, value 0 to 100), `naval_blockade` (target_country, id = region, value 0 to 100), `coast_defense` (id = region, value 0 to 100), `naval_invasion_support_priority` (vanilla only).

## Production, ratios, and buildings

| Token | Parameters | Meaning |
| --- | --- | --- |
| `role_ratio` | id = role, value | Wanted number of templates (land) or ship and tank roles per the AI templates and AI equipment definitions. Vanilla values are small integers (garrison 4, infantry 80 in generic production, mountaineers 0 to 4, cavalry -100). |
| `template_prio` | id = role, value | Priority for division template roles (vanilla uses 100 to 150 for armor roles and -100 to block). |
| `unit_ratio` | id = unit or equipment type, value | See unit ratio arithmetic below. |
| `build_army` | id = role, value | Modifies the desired division amount for the role. |
| `force_build_armies` | value | Build divisions above the desired amount. |
| `ai_wanted_divisions_factor` | value | Scales wanted division count (vanilla only). |
| `equipment_production_factor` | id = equipment category (`script_enum_equipment_category`), value | Percent on the perceived factories needed. |
| `equipment_variant_production_factor` | id = archetype, value | More of that archetype. |
| `equipment_production_min_factories` | id = equipment `type`, value | At least this many factories on any equipment of that type (for example `motorized` includes trucks and armored cars). Stacks; ignores how many factories exist. |
| `equipment_production_min_factories_archetype` | id = archetype | Same for one archetype (for example `motorized_equipment` includes trucks only). The documentation example block mistakenly repeats `type = equipment_production_min_factories`; vanilla uses the real token `equipment_production_min_factories_archetype` in `GAME/common/ai_strategy/*.txt`. |
| `equipment_production_surplus_management` | id = equipment type or concrete equipment, value | Weights where factories go once all needs are met. Very high values interfere with normal needs. |
| `equipment_stockpile_surplus_ratio` | value | Share of equipment held in stockpile. |
| `production_upgrade_desire_offset` | id = equipment type, value | Push production line upgrades. |
| `save_equipment` | id = equipment, value | In the token list; vanilla uses it with ids such as `transport_plane_equipment` and value 10. Exact semantics not described. |
| `added_military_to_civilian_factory_ratio` | value | Positive means more military factories. |
| `dockyard_to_military_factory_ratio` | value | Positive means more dockyards. |
| `air_factory_balance` | value | Positive means more airforce. |
| `railway_gun_divisions_ratio` | value | Added to `RAILWAY_GUN_PRODUCTION_BASE_DIVISIONS_RATIO_PERCENT`. |
| `factory_build_score_factor` | target = state, value | Prefer building in the state. |
| `build_building` | id = building, target = state or province id (optional), value | Weighted random choice among all `build_building` strategies, including ones the game creates internally at weight 1. With no `target` the location is random, except convertible buildings convert instead. Ignored if already under construction there. |
| `building_target` | id = building, value = count | Build until the country has at least that total (own, occupied, traded, and subject-received buildings all count). |
| `build_airplane` | derived | Set by the game from air `unit_ratio`; not authored directly. |
| `min_wanted_supply_trucks`, `wanted_supply_trucks`, `min_wanted_supply_trains`, `wanted_supply_trains` | value | Override wanted supply vehicles. |
| `fuel_buffer`, `convoy_efficiency_to_cancel_trades`, `min_convoy_efficiency_factor_for_war_support_hit` | value | In the token list without examples. |

### Unit ratio arithmetic

From the "UNIT RATIOS" section of the documentation:

- Air: `unit_ratio` values are weights, defaulting to 0, and a DLC-locked plane type's ratio is ignored. Land-based and carrier planes are separate. The game computes the total wanted land-based planes as air base capacity (excluding carriers) times `WANTED_LAND_PLANES_PER_BASE_CAPACITY_FACTOR` plus wanted divisions times `WANTED_LAND_PLANES_PER_DIVISION`, minus planes in wings, clamped between 0 and wanted divisions times `WANTED_LAND_PLANES_TOTAL_MAX_PER_DIVISION`, then multiplied by the hardcoded `AI_FOCUS_AVIATION` times the modifier `ai_focus_aviation_factor`. Carrier planes use deck capacity (plus decks of carriers finishing soon), `AI_FOCUS_NAVAL_AIR`, and `ai_focus_naval_air_factor`. Each type's `build_airplane` is its share of the weights times the total.
- Everything else: ratios are a base of 100 plus the strategy value, so -40 gives 60 percent of the wanted number. How the AI reaches the goal is affected by other factors.
- `equipment_production_factor` follows the same percent logic on the calculated factories needed.

## Equipment market

`equipment_market_spend_factories` (value; 20 gives factor 1.2 on `EQUIPMENT_MARKET_MAX_CIVS_FOR_PURCHASES_RATIO`), `equipment_market_for_sale_threshold` (id = equipment, absolute surplus before selling), `equipment_market_for_sale_factor` (id, percent on `EQUIPMENT_MARKET_BASE_MARKET_RATIO`; 50 gives 1.5), `equipment_market_max_for_sale` (id, absolute; 0 is ignored), `equipment_market_min_for_sale` (id, absolute lower limit and multiple, overrides `EQUIPMENT_MARKET_DEFAULT_CIC_CHUNK_FOR_SALE`), `equipment_market_buying_threshold` (id = archetype, absolute offset on perceived need; 50 buys 50 more, -20 buys only with a deficit above 20), `equipment_market_buy` (equipment_type and/or seller, value feeding `EQUIPMENT_MARKET_SCORE_FACTOR_AI_STRAT_WEIGHT`), `equipment_market_trade_desire` (id = partner, value added to acceptance and desire for purchase requests and market access).

## Research, PP, and XP spend

- `research_tech`: id = tech, positive value forces research as soon as possible; magnitude does not matter.
- `research_weight_factor`: id = tech, percent on the tech `ai_will_do`.
- `land_xp_spend_priority`, `air_xp_spend_priority`, `navy_xp_spend_priority`: id selects the action: `division_template`, `unlock_doctrine`, `equipment_variant`, `upgrade_xp_cutoff` (an XP cutoff for the legacy upgrade system, not a desire), and `army_spirit` / `air_spirit` / `navy_spirit` (must match the category).
- `pp_spend_priority`: id examples in the wiki are `admiral`, `guarantee`, `relation`, `decision`; vanilla also uses ids `navy_chief`, `become_faction_leader`, and `supportive_scientist`.
- `pp_spend_amount`: id examples `idea` and `decision`; political power the AI preserves for that purpose (vanilla `default_pp_spend_amount`).
- `recruit_scientist`: id = specialization token such as `specialization_land` or `specialization_nuclear`, value (vanilla only).

## Intelligence and operations

- `activate_crypto`, `decrypt_target`, `become_spymaster` (weight for a faction leader to take the spymaster role; added in 1.15.2 per the wiki), `agency_ai_base_num_factories_factor`, `agency_ai_per_upgrade_factories_factor` (1 equals 1 percent over the define baseline), `intelligence_agency_branch_desire_factor` (id = branch from `common/intelligence_agency_upgrades`; -50 means minus 50 percent), `intelligence_agency_usable_factories`, `operation_equipment_priority`.
- `operative_mission`: `mission` (token), `mission_target`, optional `state` (several allowed), `priority` (highest wins), optional `num_operatives`, `value` as a score compared with other operations and missions. `mission_target` accepts `var:` scopes in vanilla.
- `operative_operation`: `operation`, `operation_target`, optional `state` and `region`, `priority`, `value`. Both `operation` and `operation_target` accept `var:` values in vanilla `generic_operation_strats.txt`.
- `raid_target_country`: id = target, value percent on raid probability (200 means plus 200 percent).

## Faction, scientist, and other vanilla-only tokens

- `spent_faction_initiative_priority`: id is one of `program`, `unlock_doctrine_sharing`, `unlock_faction_commander` (factions documentation), value weight.
- `become_head_of_crypto`, `become_head_of_counter_intel`, `become_head_of_operations`: faction intel advisor weights (factions documentation).
- Faction rule initiative spending is scripted inside the rule's `ai_will_do`, not in strategies.
- `strategic_air_importance`: id = strategic region id, value added to the region's air-mission importance score; scores are in the tens of thousands, so use values like 10000 (documentation example; a stocked main front in active combat is "usually around 35,000").
