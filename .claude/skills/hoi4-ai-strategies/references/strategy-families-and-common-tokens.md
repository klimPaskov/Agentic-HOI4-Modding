# HOI4 AI Strategies: Strategy families and common tokens

Part of the [hoi4-ai-strategies](../SKILL.md) skill. Read to pick a diplomacy, front, production or research strategy type and its typical values before opening the full token catalog.

## Strategy families and the common tokens

The full token list is in `GAME/common/ai_strategy/_documentation.md` ("List of available strategy tokens").
Families: diplomacy, fronts and armies, navies, intelligence, production and resources, airforce, raids.
This section covers the ones most used when scripting behaviour; the catalog covers every parameter.

### Diplomacy

| Token | Effect on the AI | Typical value |
| --- | --- | --- |
| `conquer` | Prefer the target for war declaration and wargoal justification. Does not change frontline control once at war. | 100 to 800; negative to protect |
| `antagonize` | Treat the target as an antagonist and refuse most diplomatic actions with it. | 100 |
| `befriend` | Accept and propose friendly actions; opposite of `antagonize`. | 100 to 200 |
| `ignore` | Reduce desire and acceptance for any diplomatic action with the target. | 200 |
| `alliance` | Seek alliance or join the same faction. | -200 to block, 100 to 200 to seek |
| `protect` | Guarantee or add to the faction. A negative total means the AI never guarantees the target. | -200 / 200 |
| `contain` | Protect countries the target would attack or invade; target-based containment. | -800 to disable |
| `support` | Aid the target in wars (lend-lease, volunteers, expeditionary forces). | 200 |
| `consider_weak` | Lower hesitation to attack the target. | 100 |
| `prepare_for_war` | Move troops to the border of the target. | 100 |
| `declare_war` | Declare war on the target when a wargoal already exists. | 100 |
| `dont_join_wars_with` | With `id`, avoid joining a war on the same side as `id` against `target_country`. | 100 |
| `send_lend_lease_desire`, `send_volunteers_desire` | Desire to send lend-lease or volunteers to `id`. | 100 |
| `diplo_action_desire` / `diplo_action_acceptance` | Desire to request or acceptance of one action, with `target = <action>`. Actions seen in vanilla: `improve_relation`, `military_access`, `docking_rights`, `offer_docking_rights`, `air_base_access`, `offer_air_base_access`, `call_allies`, `join_allies`, `guarantee`, `market_access_rights`, `befriend`. | 50 to 1000 |
| `ignore_claim` | Ignore the AI's own claims on `id`; value is boolean 1. | 1 |
| `avoid_starting_wars` | Targetless additive modifier to conquer weights. | -200 to -400 |

Action names come from the title localisation keys (`DIPLOMACY_<NAME>_TITLE`, lower-cased) in the base localisation file `diplomacy_l_english.yml`, according to the wiki.

### Army and fronts

`area_priority` (id = AI area key, value percent), `force_defend_ally_borders`, `dont_defend_ally_borders` (binary, positive value turns it on), `front_control`, `front_unit_request`, `invasion_unit_request`, `put_unit_buffers`, `garrison`, `theatre_distribution_demand_increase`, `force_concentration_factor`, `force_concentration_front_factor`, `force_concentration_target_weight`, `invade`, `front_armor_score`.
Targeted types accept several of `tag`, `state`, `strategic_region`, `area`, `country_trigger`, `state_trigger`, and when more than one target kind is given all must match.
`front_control` only changes orders on an existing front; it does not create units or fronts.

### Production, research, and spend

`role_ratio` (division role weights; also ship and tank roles from AI equipment), `template_prio`, `unit_ratio`, `build_army`, `equipment_production_factor`, `equipment_variant_production_factor`, `equipment_production_min_factories`, `equipment_production_min_factories_archetype`, `build_building`, `building_target`, `research_tech`, `research_weight_factor`, `pp_spend_priority`, `pp_spend_amount`, `land_xp_spend_priority`, `air_xp_spend_priority`, `navy_xp_spend_priority`, `build_airplane` (computed by the game from air `unit_ratio`; see the catalog for the formula).
`research_tech` forces the tech as soon as possible; `research_weight_factor` multiplies the tech's `ai_will_do` (50 means plus 50 percent).
`stockpile_fuel` (added in 1.19.4.1) has no `value`: optional `start_below` and `stop_above`, percent of wanted max fuel, make the AI stand down new attacks and throttle air and naval fuel until fuel recovers. `stop_above` must be above `start_below`; the catalog has the rest.
`GAME/common/ai_strategy/default.txt` shows vanilla uses of nearly all of these.

