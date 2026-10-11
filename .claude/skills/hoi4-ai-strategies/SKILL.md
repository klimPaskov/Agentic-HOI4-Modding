---
name: hoi4-ai-strategies
description: Use when designing, implementing, tuning, or debugging Hearts of Iron IV country AI behaviour, including common/ai_strategy blocks, add_ai_strategy, AI strategy plans, AI focuses and areas, ai_will_do and ai_chance weights, AI templates, equipment and navy AI, AI peace desires, and AI research or diplomacy weighting.
---

# HOI4 AI Strategies

Generic guidance for steering the Hearts of Iron IV country AI from mod script.
Use it to choose the right AI mechanism, write it with verified syntax, tune weights without misreading score as probability, and debug the result.
Use `hoi4-mtth` for MTTH variables and centralised weight logic, `hoi4-decisions-missions` for decision and mission `ai_will_do`, `hoi4-focus-trees` for focus `ai_will_do`, and `hoi4-diplomacy-war` for the diplomacy, faction, subject, wargoal, and peace mechanics that AI strategies steer.

## Contents

- Source map: where the authoritative text lives
- Decision procedure: which mechanism for which goal
- Weight semantics: ai_will_do, ai_chance, base, add, factor
- common/ai_strategy: structure, lifecycle, stacking
- add_ai_strategy and flag-gated strategies
- Strategy families and the common tokens
- AI strategy plans
- AI focuses, research weights, and AI areas
- Other AI systems (templates, equipment, navy, theaters, peace) in the reference file
- Debugging and verification
- Repository conventions
- Common mistakes
- Unverified or conflicting points

Deeper material lives in two reference files inside this skill folder:

- `references/strategy-token-catalog.md`: read when you need the exact parameters, ids, value semantics, or unit-ratio arithmetic of a specific `ai_strategy` type (production, market, front, navy, intelligence, research, XP and PP spend).
- `references/other-ai-systems.md`: read when you touch `common/ai_templates`, `common/ai_equipment`, `common/ai_navy`, `common/ai_faction_theaters`, `common/peace_conference/ai_peace`, `ai_attitudes`, or the AI-facing blocks of factions, autonomy, and scripted diplomatic actions.

## Source map

`GAME` means the installed Hearts of Iron IV folder named in `CLAUDE.md`.
`WIKI` means the offline snapshot in `paradox_wiki/` at the mod root.
Installed documentation is more authoritative than the wiki; where they disagree, follow the installed file and record the conflict.

| Topic | Authoritative text | Vanilla precedent |
| --- | --- | --- |
| Every `ai_strategy` token, value semantics, unit ratios | `GAME/common/ai_strategy/_documentation.md` (updated 2024-11) | `GAME/common/ai_strategy/default.txt` (generic), `GER.txt`, `FRA.txt`, `INS.txt` (reversed), `SOV.txt` (front_control) |
| AI strategy plans, ai_will_do math, ai_chance, AI areas | `WIKI/AI modding - Hearts of Iron 4 Wiki.md` (sections MTTH blocks, AI strategies, AI areas, AI strategy plans) | `GAME/common/ai_strategy_plans/GER_historical_strategy_plan.txt`, `ENG_historical_strategy_plan.txt` |
| Research and focus weighting | `WIKI/AI focuses - Hearts of Iron 4 Wiki.md` | `GAME/common/ai_focuses/generic.txt`, `GER.txt` |
| Focus `ai_will_do` and the plan override | `WIKI/National focus modding - Hearts of Iron 4 Wiki.md` (AI will do, AI strategy plans) | `GAME/common/national_focus/*.txt` |
| Decision `ai_will_do` | `WIKI/Decision modding - Hearts of Iron 4 Wiki.md` (AI section) | `GAME/common/decisions/political_decisions.txt` |
| Event option `ai_chance` | `WIKI/Event modding - Hearts of Iron 4 Wiki.md` (options) | `GAME/events/Germany.txt` |
| Technology `ai_will_do`, `ai_research_weights` | `WIKI/Technology modding - Hearts of Iron 4 Wiki.md` | `GAME/common/technologies/*.txt` |
| AI templates | `GAME/common/ai_templates/_documentation.md` (updated 2024-08) | `GAME/common/ai_templates/generic.txt`, `templates_ENG.txt` |
| AI equipment designer | `GAME/common/ai_equipment/_documentation.md` | `GAME/common/ai_equipment/generic_tank.txt` |
| Goal-based naval AI | `GAME/common/ai_navy/_documentation.md`, `ai_navy/taskforce/_documentation.md` | `GAME/common/ai_navy/goals/goals_generic.txt`, `fleet/generic_fleet_templates.txt` |
| Faction theaters | `GAME/common/ai_faction_theaters/_documentation.md` | `ai_faction_theaters.txt` in the same folder |
| AI peace desires | `GAME/common/peace_conference/ai_peace/_documentation.md` | `GAME/common/peace_conference/ai_peace/00_misc.txt` |
| Faction AI (rules, goals, initiative spend) | `GAME/common/factions/_documentation.md` | `GAME/common/factions/rules/joining_rules.txt` |
| Effects and triggers touching AI | `GAME/documentation/effects_documentation.md` (`add_ai_strategy`, `ai_message`), `triggers_documentation.md` (`is_ai`, `ai_irrationality`, `ai_has_role_division`, `ai_has_role_template`, `ai_liberate_desire`, `ai_wants_divisions`) | |
| AI modifiers (`ai_focus_*_factor`, `ai_desired_divisions_factor`, `ai_get_ally_desire_factor`, `ai_join_ally_desire_factor`, `ai_call_ally_desire_factor`, `ai_badass_factor`, `ai_license_acceptance`) | `GAME/documentation/modifiers_documentation.md`, section "Modifiers for scope ai" | |
| AI tuning constants | `GAME/common/defines/00_defines.lua`, table `NAI` | |
| Debug commands | `GAME/documentation/console_commands_documentation.md` | |

Use the hoi4 MCP reference routes (`hoi4_reference_context` with surface `ai`, `hoi4_reference_search`, `hoi4_reference_read`, `hoi4_source_lookup`) to cite exact line spans.
If a route fails once, retry once with narrower input, then read the local file directly.

## Decision procedure: which mechanism

Pick the narrowest mechanism that expresses the intent.
Reaching for a global strategy when a local `ai_will_do` suffices is the most common over-reach.

| Intent | Mechanism | Notes |
| --- | --- | --- |
| Make the AI take or avoid one decision, mission, focus, idea, advisor, tech, MIO policy, faction rule, or faction goal | `ai_will_do` on that object | Decisions are never picked without an `ai_will_do` (Decision modding wiki, AI section). |
| Make the AI pick one event option over another | `ai_chance` on the option | Proportional weights, effective resolution 1 percent. |
| Steer who the AI befriends, antagonizes, ignores, guarantees, allies with, attacks, or sends aid to | `ai_strategy` types `befriend`, `antagonize`, `ignore`, `alliance`, `protect`, `conquer`, `declare_war`, `support`, `send_lend_lease_desire`, `send_volunteers_desire` | Targeted by `id = TAG`. |
| Make the AI accept or request one specific diplomatic action | `diplo_action_acceptance` / `diplo_action_desire` with `target = <action>` | Acceptance does not raise desire to propose, and the reverse. |
| Change what the AI builds, produces, researches, or spends | production, market, research, XP and PP strategy types | See the token catalog. |
| Change troop distribution, fronts, invasions, garrisons | `area_priority`, `front_control`, `front_unit_request`, `invasion_unit_request`, `put_unit_buffers`, `force_defend_ally_borders` | Needs `ai_areas` for `area`. |
| Give a country a long-lived overall plan (focus order, research bias, advisors, strategies) | `common/ai_strategy_plans` | Preferred over `ai_historical_focus_list`. |
| Change which research categories a general AI posture favours | `common/ai_focuses` | Per-country via tag postfix. |
| Force a condition-gated strategy that can later be undone | `common/ai_strategy` block with `enable` / `abort` keyed on a flag | Prefer over `add_ai_strategy` when reversibility matters. |
| One-shot permanent nudge from a focus, decision, or event | `add_ai_strategy` effect | Cannot be removed by an effect; see below. |
| Influence division design or composition | `common/ai_templates` plus `role_ratio` and `template_prio` strategies | Reference file. |
| Influence tank, plane, or ship variant design | `common/ai_equipment` | Reference file. |
| Influence naval missions | `common/ai_navy` goals, taskforce and fleet templates, `naval_*` strategies | Reference file. |
| Influence post-war outcomes the AI picks | `common/peace_conference/ai_peace` `peace_ai_desires`, plus `use_for_peace_conference_weight` in autonomous states | Reference file. |
| Tune a global AI behaviour constant | `NAI` defines | Last resort; affects every country and every mod system. |

## Weight semantics

### The shared MTTH-style block

Most `ai_will_do` and `ai_chance` blocks use the same arithmetic (WIKI AI modding, "MTTH blocks"; Decision, Focus, Technology, Event wiki pages).

- The value starts at 1.
- `base = N` replaces the running value, `add = N` adds, `factor = N` multiplies.
- `modifier = { <triggers> add/factor/base }` applies its change only when the triggers are true.
- Top-level operations and `modifier` blocks apply in the order written, so a `factor` written before an `add` does not scale that add.
- Scope is the evaluated country (ROOT). Some surfaces add FROM scopes (targeted decisions, peace desires, faction goals and rules).
- A temporary variable set inside a `modifier` must be defined before the `add`/`factor` that uses it.
- Variables may be used in `add`, `factor`, and `base`. For repeated or shared weights use `hoi4-mtth` instead of copying modifier ladders.
- `factor = 0` inside a matching modifier forces the whole result to zero and is the standard hard block.

A worked check, taken from the wiki example: `base = 10.5`, `modifier add 1 (major)`, `modifier factor 3 add 2.5 (FRA)`, `factor = 2` gives 21 for a minor, 23 for another major, and 74 for FRA when FRA is a major.
Within the FRA modifier the wiki computes `factor` before `add` (`(10.5 + 1) * 3 + 2.5`, then times 2).

### Score is not probability

- Focus selection: for each available focus the game draws a random decimal between 0 and the focus value, multiplies the draw by 1.5 if the focus follows one just completed, multiplies by the strategy plan `focus_factors` entry, and picks the highest draw (National focus modding wiki, "AI will do"). A focus with value 4 beside a focus with value 8 wins far less than one third of the time. The wiki gives closed-form chances; small values lose disproportionately. Never read the ratio of two values as the ratio of chances.
- If no focus has a value above 0, the AI takes none and falls to continuous focuses or idles.
- Technology selection: every 7 days (`NAI.RESEARCH_DAYS_BETWEEN_WEIGHT_UPDATE`) a random draw between 0 and the weight is made per tech, with cost, bonus, and ahead-of-time modifiers on top. `NAI.RESEARCH_WEIGHT_TRUNCATION_THRESHOLD` picks randomly among scores within a fraction of the top score.
- Event options: weight divided by the sum of weights, rolled as a d100, so a weight share below 1 percent behaves like 0 and the share is rounded to whole percents. If every weight is 0 the first option is chosen. The result is deterministic for a given seed, time, and country across reloads (Event modding wiki).
- Decisions: the AI only considers decisions with an `ai_will_do`, compares them with a priority system, and may pick a lower-priority decision early within `NAI.DECISION_PRIORITY_RANDOMIZER` (0.1). Idea scores are scaled into `MIN/MAX_SCALED_IDEA_WEIGHT_TO_COMPARE_WITH_DECISIONS` (100 to 200). `CRITICAL_DECISION_PRIORITY` (200) lets a high-priority decision fire early. A decision that leads to war should declare it with `war_with_on_remove`, `war_with_on_complete`, or `war_with_on_timeout` so the AI prepares (see `hoi4-diplomacy-war`).
- Strategy `value`: not a probability. Each type defines its own meaning (additive weight, percent factor, absolute count, binary, threshold). Always read the token entry before choosing a number. Typical vanilla magnitudes: diplomacy weights 100 to 800, hard blocks at -800 to -1000, production percent factors 10 to 100, `role_ratio` small integers.
- A strategy with the wrong magnitude can be invisible or dominant, because several active strategies of the same type and target add together.

### Common ai_will_do traps

- Putting a hard prerequisite only in `ai_will_do` when the player can also do the action. The AI weight is not a gate; use `available` or `allow`.
- Giving every option `ai_chance` 0 (first option wins) or a lone positive value on a branch that the AI cannot legally pick.
- Using `ai_irrationality` (a trigger, vanilla focuses use it with `factor`) as if it were a random number; it is a country property read with comparisons.
- Forgetting that `base = 0` plus conditional `add` modifiers is the idiom for "never unless". Starting at the implicit 1 means the object is always eligible.
- Sharing one large `modifier` ladder across dozens of objects instead of computing one variable once.

## common/ai_strategy: structure and lifecycle

File skeleton (GAME/common/ai_strategy/_documentation.md, "Examples of AI strategy usage"):

```
my_strategy_name = {
	allowed = {
		original_tag = TAG
	}
	enable = {
		date > 1938.1.1
	}
	abort = {
		num_of_military_factories > 30
	}
	abort_when_not_enabled = yes

	ai_strategy = {
		type = befriend
		id = ENG
		value = 100
	}
	ai_strategy = {
		type = equipment_production_factor
		id = tactical_bomber
		value = 50
	}
}
```

Rules, with sources:

- The block name is free-form and only appears in AI dumps and in the player-facing "has strategic reasons" diplomatic tooltip (WIKI AI modding, "AI strategies"). Overlapping names are tolerated, but use unique names so dumps are readable.
- `allowed` is checked once, before the game starts. Use it only for permanent country or DLC filters (`original_tag`, `has_dlc`). Do not put expensive or time-varying triggers in it (documentation comment: "avoid expensive triggers").
- `enable` is continuous. By default, an `enable` that turns false does not cancel the strategy.
- `abort` removes a strategy when true and, per the wiki, also prevents it from being added. The installed documentation says to always include either `abort` or `abort_when_not_enabled`. If the strategy genuinely never ends, write `abort = { always = no }`.
- `abort_when_not_enabled = yes` turns `enable` into a live switch and is the usual choice.
- A block may hold any number of `ai_strategy` entries, all active together.
- `reversed = yes` with `enable_reverse = { ... }` swaps holder and target for strategies that use `id = TAG` (WIKI AI modding, "Arguments"; vanilla `GAME/common/ai_strategy/INS.txt` and `FRA.txt`). `enable_reverse` has no default scope, so scope into a country explicitly. The wiki and the vanilla files do not fully pin down which country is evaluated by `enable` versus `enable_reverse`, so verify a reversed strategy with the debug tools before trusting it.
- Parameters such as `tag`, `state`, `strategic_region`, `area`, `country_trigger`, `state_trigger`, `ratio`, `priority` are used by targeted front and unit-request types; see the catalog.
- `id` may be a country tag (quoted tags like `"POL"` appear in vanilla and are fine), a state id, a strategic region id, an AI area key, an equipment category or archetype, a building, a role, or a tech, depending on the type.
- Several parameters accept variables or scopes in recent versions (`operation = var:...`, `mission_target = var:...`, `seller = <scoped variable>` in `GAME/common/ai_strategy/generic_operation_strats.txt` and the documentation). Do not assume other parameters do.

### Stacking

- Strategies of the same type and target from all active blocks sum. The vanilla comment in `default.txt` says it directly: country-unique blocks stack with the generic ones unless the generic block excludes those countries in its `enable`.
- So a country-specific override must either exclude the country from the generic block (`NOT = { original_tag = TAG }` in the generic `enable`) or add a compensating value. Check by reading every `ai_strategy` block that can be active for that country, including DLC-specific ones.
- `avoid_starting_wars` is targetless and additive with `conquer`; the documentation uses opposing `conquer` values to whitelist a single target (see the endgame blocks in `default.txt`).
- Production and ratio strategies add to what the AI computed, they do not replace it, unless the documentation says an exact count (for example `build_army` as a role target).

## add_ai_strategy and flag-gated strategies

`add_ai_strategy` is a country-scope effect (GAME/documentation/effects_documentation.md: "Adds strategy entry to country AI"; it has no further documentation there).
Syntax verified in vanilla `GAME/common/scripted_effects/00_scripted_effects.txt` and many focuses and decisions:

```
add_ai_strategy = {
	type = contain
	id = "SOV"
	value = -800
}
```

- The wiki calls the result permanent.
- No effect to remove a strategy exists in the installed effects documentation. The documented ways to undo one are an opposing value (the only repeat pattern in vanilla) or not using the effect in the first place.
- Whether a second `add_ai_strategy` with the same type and id replaces or adds to the first is not documented here. Treat it as unverified and test with the debug tools before relying on either.
- Therefore: when the intent is temporary, conditional, or must change with game state, write a `common/ai_strategy` block with `enable` on a country flag or on the real world condition, set or clear the flag from the focus, decision, or event, and use `abort_when_not_enabled = yes`.
- Use `add_ai_strategy` for one-way narrative commitments such as a country permanently dropping a diplomatic goal.
- For many similar calls, wrap them in a scripted effect (vanilla `GER_democratic_nations_ai_strategies`, `SOV_anglo_soviet_invasion_add_ai_strategies_effect`) instead of pasting blocks.

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
`GAME/common/ai_strategy/default.txt` shows vanilla uses of nearly all of these.

## AI strategy plans

Location: `common/ai_strategy_plans/*.txt` (WIKI AI modding, "AI strategy plans"; vanilla `GER_historical_strategy_plan.txt`).
A plan is a long-lived package that can carry a focus order, focus factors, research biases, idea and trait preferences, and embedded strategies.

```
TAG_historical = {
	name = "Historical plan for TAG"
	desc = "Free text for aiview only"
	allowed = { original_tag = TAG }
	enable = {
		is_historical_focus_on = yes
	}
	abort = {
		TAG = { has_government = communism }
	}
	ai_national_focuses = {
		TAG_focus_a
		TAG_focus_b
	}
	focus_factors = {
		TAG_focus_c = 0
	}
	research = {
		artillery = 2
	}
	ideas = {
		TAG_advisor = 3
	}
	traits = {
		fascist_demagogue = 0
	}
	ai_strategy = {
		type = conquer
		id = POL
		value = 100
	}
	weight = {
		factor = 1.0
	}
}
```

- `name` and `desc` are never shown to players and need no localisation.
- `allowed` is checked once at start. `enable` is checked daily; once true the plan stays assigned even if `enable` later turns false. `abort` is checked daily and, when true, drops the plan and blocks it from being picked.
- `ai_national_focuses` is an ordered list taken first; while following it the AI ignores focus `ai_will_do`. If every listed focus is complete or impossible, normal `ai_will_do` resumes.
- `focus_factors = { FOCUS = N }` multiplies that focus's `ai_will_do`. A factor of 0 means the focus is never chosen unless listed in `ai_national_focuses`. Use it to enforce a political path without enumerating the whole route.
- `research`, `ideas`, `traits` multiply the AI weight of research categories, individual ideas or advisors (by idea token), and country leader traits.
- `weight` is an MTTH block that scales the plan's factors (a weight of 1.25 turns a focus factor of 4 into 5). Vanilla recommends about 1.0 because the value is also used as a factor for some research needs.
- Several plans can be active at once. Make mutually exclusive plans exclude each other in `enable` or `abort`, usually through a game rule option or a randomisation flag set in `on_startup` (`has_game_rule`, `is_historical_focus_on`, `has_country_flag`).
- `ai_historical_focus_list_<tag>` in `common/ai_focuses` is superseded by plans (vanilla `ai_focuses/USA.txt` has it commented out).
- Plans are the right place for a path-level decision such as "this country should take the democratic route"; a single focus `ai_will_do` is the right place for local preference.

## AI focuses, research weights, and AI areas

### AI focuses

`common/ai_focuses/*.txt` maps the country-wide AI postures to research category weights (WIKI AI focuses).
Postures: `ai_focus_defense`, `ai_focus_aggressive`, `ai_focus_war_production`, `ai_focus_military_equipment`, `ai_focus_military_advancements`, `ai_focus_peaceful`, `ai_focus_naval`, `ai_focus_naval_air`, `ai_focus_aviation`.

```
ai_focus_aggressive_TAG = {
	research = {
		offensive = 5.0
		armor = 20.0
	}
}
```

- A tag postfix gives that country its own table; the generic name serves everyone else (vanilla `ai_focuses/generic.txt` and `GER.txt`).
- Each posture's numeric default depends on war state and economy (defensive 50 at peace, 100 in a defensive war, 0 in an aggressive war; aggressive 50 at peace and 75 for fascist countries; peaceful 100 at peace and 0 at war; naval, naval air, and aviation scale with dockyards, carriers, and airports, and are -999 without them; see the wiki page for all nine).
- Shift a posture for a country with the modifier `ai_focus_<x>_factor` (for example `ai_focus_naval_air_factor = 0.5` adds 50 percent), usually via an idea or national spirit. This is the right tool to make a country "more naval" without scripting strategies.
- A continuous focus is only eligible for the AI if it names `supports_ai_strategy = ai_focus_<x>` (vanilla `GAME/common/continuous_focus/generic.txt`).

### Research weights on a technology

- `ai_will_do` on the tech scales its base weight; `ai_research_weights = { offensive = -1.0 }` on the tech makes it more or less attractive under a posture (Technology modding wiki).
- `research_weight_factor` and `research_tech` strategies are the per-country overrides.
- `AI research logging`: console `ai_research_log` (not in release builds).

### AI areas

`common/ai_areas/*.txt` defines named areas used by `area_priority`, `force_defend_ally_borders`, `front_control`, `put_unit_buffers`, `naval_dominance`, and similar.
The vanilla file wraps all areas in one `areas = { ... }` block and defines each area with `continents = { ... }` and/or `strategic_regions = { ... }`; the wiki example omits that wrapper, so copy the structure of `GAME/common/ai_areas/default.txt`.
A province can belong to several areas or none, and a province matches an area if it matches any entry.
Use the continent token name (for example `europe`), not the numeric id from `definition.csv`.

## Debugging and verification

Console commands (GAME/documentation/console_commands_documentation.md; the player runs them in game, agents do not launch the game):

| Command | Use |
| --- | --- |
| `aiview` | Overlay AI debug information; with plans, shows names and descriptions. |
| `ai_trace` | AI trace window (not in release builds). |
| `ai_dump` / `aidump` | Dump AI data to the log (not in release builds). |
| `ai_front_dump` | Dump front data for the selected unit. |
| `ai_research_log` | Toggle research decision logging (not in release builds). |
| `ai_pp_log` | Political power spend log. |
| `ai_idea_desire_log` | Idea desire log for the current country. |
| `ai_accept` / `yesman` | Make the AI accept all diplomacy. |
| `ai_force_template`, `ai_force_equipment` | Force XP spend on templates or equipment. |
| `imgui show ai_templates`, `imgui show ai_division_production`, `imgui show ai_navy` | Template, division demand, and naval goal debug UIs named in the template and navy documentation. |
| `tdebug`, `debug` | Province, state, and strategic region ids. |

Repository verification without launching the game:

1. Read the actual block and compute representative cases by hand. For `ai_will_do`, `ai_chance`, strategy plans and MTTH-backed weights prefer `hoi4_probability_inspect` (adapters: `event_option_ai_chance`, `decision_ai_will_do`, `mission_ai_will_do`, `national_focus_ai_will_do`, `technology_ai_will_do`, `doctrine_ai_will_do`, `ai_strategy_factor`, `random_list`, `direct_random`, `custom_weighted_pool`, `event_mean_time_to_happen`), then `hoi4_probability_inspect` or `hoi4_probability_analyze` with `analysis: "compare"` with explicit named scenarios (country, date, flags, government, factory counts).
2. Report assumptions, and state whether a number is a score, a share of a proportional pool, or a random-draw win chance.
3. Use `hoi4_script_validate` for trigger and effect bodies in the right scope.
4. Use `hoi4_source_lookup` for every other active definition of the same strategy type and target, so stacking is visible.
5. Remember the analyzer models source, not observed game behaviour; the AI's runtime inputs (threat, factories, borders) are not simulated.
6. If a probability route fails on invalid inputs, retry once with corrected inputs, then calculate from the source and say so.

## Repository conventions

These follow the project rules in `CLAUDE.md`, which remain the authority.

- Tabs for indentation, lowercase snake_case, no `<=` or `>=` (use `check_variable` with `compare = ...` where a comparison is needed and the short `<` and `>` elsewhere).
- No magic numbers: put shared tuning values in `common/script_constants/` and read them with `constant:category.key` where the field supports it. Several AI strategy fields may not parse `constant:`; then use an `@` file constant or compute a variable first. Verify per field.
- Reuse the project's dynamic scripted effects library (`common/scripted_effects/<prefix>_dynamic_effects.txt`, named in `CLAUDE.md`); document any new dynamic effect in its documentation file as `CLAUDE.md` requires in the same change.
- Use `hoi4-mtth` for MTTH variables and to keep `ai_will_do` readable.
- `on_daily`, `on_weekly`, and `on_monthly` iterate over every country; do not add them to implement AI behaviour without explicit permission. Gate behaviour in `common/ai_strategy` `enable` blocks instead, which the engine already evaluates.
- A flag trigger inside a player-visible requirement block shows its raw identifier unless localised; AI-only gating belongs in `ai_will_do` or `enable`, which are not player-visible.
- Do not write player-facing text describing AI tuning history.

## Common mistakes

1. Treating `value` as a probability or comparing values across unlike types.
2. Forgetting that same-type, same-target strategies from every active block add up; a country override that does not exclude the generic block double-counts.
3. Omitting `abort` or `abort_when_not_enabled`, leaving a strategy permanently active after `enable` turns false.
4. Putting time-varying conditions in `allowed` (checked once at start).
5. Using `add_ai_strategy` for something that must end, then having no way to end it.
6. Expecting `conquer` to change frontline behaviour (it does not) or `front_control` to create units.
7. Giving a decision or mission no `ai_will_do` and wondering why the AI never takes it.
8. Relying on `ai_will_do` for eligibility; the AI weight does not stop the player or other scripts.
9. Reading focus `ai_will_do` ratios as probabilities; the random draw favours large values.
10. Giving a focus a strategy-plan `focus_factors` of 0 and forgetting that `ai_national_focuses` can still force it.
11. Leaving two role-level AI templates active for the same country and role (undefined behaviour per the template documentation).
12. Using the wiki's `AI areas` example without the `areas = { }` wrapper that vanilla uses.
13. Using a negative `protect` value expecting only a reduction; a negative total stops guaranteeing entirely.
14. Using a numeric `id` where a tag is required (or the reverse); state, region, and tag ids are not interchangeable.
15. Designing AI-only behaviour that only works for one scripted route, then having a different route silently disable it. Test each route's flags.
16. Leaving debug `log` effects in the finished script.
17. Using weekly or daily on_actions to poll for AI state when an `enable` trigger would do.

## Unverified or conflicting points

- Repeated `add_ai_strategy` with the same type and id: replacement versus accumulation is not documented in the installed files.
- `reversed` / `enable_reverse` holder and target scopes are described loosely; vanilla `INS.txt` and `FRA.txt` use them in ways that need in-game confirmation.
- The wiki states `allowed` is checked only at game start and `abort` blocks adding; the installed documentation only states that `abort` deactivates. Behaviour for strategies added by `add_ai_strategy` with `abort` blocks is not described.
- `hoi4_probability_inspect` returned an invalid-arguments error when called with only an adapter name and no source selector; a source or candidate pool is evidently required, but the selector shape was not confirmed in this review.
- Many numeric hardcoded behaviours (for example how conquer weights compare to force factors in declaring war) live in engine code; only `NAI` defines are visible.
