# HOI4 AI Strategies: Strategy plans, AI focuses and AI areas

Part of the [hoi4-ai-strategies](../SKILL.md) skill. Read before writing an AI strategy plan, an AI focus posture, research weights on a technology or an AI area.

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
- Game rules define no rule-level `desc` in vanilla, since every option sets its own, and 18 rule ids are referenced in a different case than they are defined, so copy the definition's spelling. [vanilla-confirmed 1.19.3]
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

