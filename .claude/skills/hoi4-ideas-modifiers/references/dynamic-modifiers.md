# HOI4 Ideas and Modifiers: Dynamic modifiers

Part of the [hoi4-ideas-modifiers](../SKILL.md) skill. Read before writing, attaching, scoping, refreshing or removing a dynamic modifier.

## Dynamic modifiers

Source: `WIKI/modifiers.md`, section Dynamic modifiers; `GAME/common/dynamic_modifiers/0_dynamic_modifiers.txt` header comment; effects documentation.

Definition (`common/dynamic_modifiers/*.txt`, no wrapper block):

```
my_dynamic_modifier = {
	icon = GFX_modifiers_my_dynamic_modifier        # optional; without it the modifier is hidden in the GUI
	enable = { always = yes }                       # optional; modifiers apply only while true
	remove_trigger = { NOT = { has_variable = my_var } }   # optional; removes the modifier when true
	attacker_modifier = no                          # state scope only: also affects attackers into the state
	political_power_gain = my_var                   # variable name as the value
	weekly_manpower = 1000                          # constant value
	stability_factor = GER.my_stability_var         # a variable of a named scope
}
```

Use:

```
add_dynamic_modifier = { modifier = my_dynamic_modifier }
add_dynamic_modifier = { modifier = my_dynamic_modifier days = 30 }                  # temporary, may be a variable
add_dynamic_modifier = { modifier = my_dynamic_modifier scope = POL }                # applied here, variables read from POL
remove_dynamic_modifier = { modifier = my_dynamic_modifier }                          # repeat scope = if used on add
force_update_dynamic_modifier = yes                                                   # refresh now
has_dynamic_modifier = my_dynamic_modifier                                            # or { modifier = x scope = GER }
```

- Allowed scopes: country, state, character (unit leader), special project. The same definition can be added anywhere; the scope of the `add_dynamic_modifier` call decides where it applies and where variables are read.
- `days` is optional on `add_dynamic_modifier` (175 of 1,552 vanilla calls pass it, none with a negative value), so omit it for a permanent attach. [vanilla-confirmed 1.19.4.1] [docs]
- Variables come from the scope the modifier is attached to: for a state modifier, the state's variable, not the owner's. Use `scope =` to read another scope's variable.
- Daily refresh: at the start of each day every variable-valued modifier resets to 0, then dynamic modifiers evaluate in the order they were added, each treated as 0 until its variables resolve. Changes take effect at most one day later unless you call `force_update_dynamic_modifier = yes` in the same scope. Re-adding an existing modifier updates its timer instead of stacking a second copy.
- Inside `enable` and `remove_trigger` for state modifiers, `ROOT` is the state and `OWNER` reaches the owner (vanilla `sabotaged_resources` and `autonomous_state` in `0_dynamic_modifiers.txt`).
- A state-side `add_dynamic_modifier = { modifier = my_dynamic_modifier scope = GER }` restricts the beneficiary to GER: the modifier stays on the state and applies only for that country. It does not move the holder off the state. [docs] `GAME/documentation/effects_documentation.md`, `add_dynamic_modifier`
- With `scope =`, variables are read from the bound scope by default, while `ROOT` stays the scope that ran the effect ("root is the effect scope" in the `0_dynamic_modifiers.txt` header). For a country view of state data, read `ROOT.my_state_variable` and write state conditions in `enable` and `remove_trigger` as `ROOT = { ... }`. [docs]
- Compute shared values such as severity and duration once in the source state, then bind each eligible country to those results. Do not repeat the arithmetic for each beneficiary.
- Match holder, modifier id and `scope` in every add, `has_dynamic_modifier` check and removal. `remove_dynamic_modifier` says its `scope` must match the one used in `add_dynamic_modifier`. [docs] `effects_documentation.md`, `triggers_documentation.md`
- The documentation supports one id bound to several distinct scopes, but reading the source does not prove that such bindings coexist in the running engine. Say so in the handoff. [unverified]
- A binding has a lifecycle: country creation, release and retirement, changes of eligibility, state cleanup and expiry. Register a newly eligible country through the path that makes it eligible, and remove a stale binding with its original `scope`.
- When registration leaves a country flag as a receipt, set and test a targeted flag (`my_flag_@THIS`) in that country's scope, so a receipt copied to another tag does not block a released or cloned tag. [docs] `WIKI/data_structures.md`, targeted flags
- Dynamic modifiers accept modifiers only. They reject `research_bonus`, `equipment_bonus`, `rule`, and other idea attributes.
- Definitions cannot be hot-reloaded; any change to a dynamic modifier file needs a game restart. Ideas can be reloaded.
- The `add_dynamic_modifier` tooltip does not list variable-valued modifiers (it lists constants). Add a `custom_effect_tooltip` line and hide the add with `hidden_effect`; the vanilla pattern is a `_tt` key: `"Modify §Y$ETH_state_development_dynamic_modifier$§! by: \n$MODIFIER_STATE_PRODUCTION_SPEED_BUILDINGS_FACTOR$: §G+10%§!"` (`GAME/localisation/english/bba_decisions_l_english.yml`).
- Cost: a dynamic modifier is re-evaluated every day for every scope that holds it, so it is less efficient than an idea. If the value is constant and the scope is a country, use an idea.
- MTTH variables can feed a dynamic modifier through the same variable slots; they also reset and recalculate daily.

