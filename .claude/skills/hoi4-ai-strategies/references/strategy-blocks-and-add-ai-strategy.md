# HOI4 AI Strategies: Strategy blocks and add_ai_strategy

Part of the [hoi4-ai-strategies](../SKILL.md) skill. Read before writing a common/ai_strategy block, judging how it stacks with others, or using add_ai_strategy.

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

