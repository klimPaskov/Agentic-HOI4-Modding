# Balance of power modding

<!-- kit:begin id="review" build="1.19.4.1" checked="2026-11-01" revision="67049" sources="common/bop/ documentation/loc_objects_documentation.md common/modifiers/ common/decisions/ localisation/english/Juno_bop_l_english.yml localisation/english/bba_bop_l_english.yml documentation/effects_documentation.md documentation/triggers_documentation.md documentation/modifiers_documentation.md documentation/dynamic_variables_documentation.md" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Checked against: all 10 vanilla files in `common/bop/` (including `_test.txt`), every BoP effect, trigger, modifier and dynamic variable in the documentation, and vanilla use of each.
- Kit blocks added: `bop-initial-value-typo`, `bop-vanilla-format`, `bop-example-rule-fix`, `bop-variables-and-modifiers`, `bop-scopes-and-operators`, `bop-triggers-1193` (bottom).
- Errors found: `intial_value` (typo) and `can_create_faction` (the rule is `can_create_factions`) in wiki examples; no vanilla range uses `rule`; the "tracked globally" claim held in a game run on 2026-11-02 (see the kit section at the bottom).
- Gaps left: the clamping of `add_power_balance_value` beyond -1 and 1 and the exact end-point rule for `max` are not documented; the wiki's version column (1.12) was not re-checked.
**1.19.4.1 re-check (2026-11-01).** Seven statements depended on files the update changed (the vanilla decision, focus, scripted effect and static modifier files), and all seven were re-measured. Two facts changed: `tooltip_side = ITA_communism_side` now appears 6 times in the Italian scripted effects (was 3), and the two `SWI_DEBUG_*` BoP modifiers have no loc key. Every other statement cites files that are byte-identical in 1.19.4.1 (Steam depot manifest diff).
<!-- kit:end id="review" -->

<!-- kit:begin id="bop-initial-value-typo" at="section:code-structure" -->
The first bullet above misspells the key. It is `initial_value` (11 BoP blocks in vanilla use it, including the wiki's own example and `_test.txt`). [vanilla-confirmed 1.19.3] `common/bop/*.txt`. A misspelled `intial_value` is ignored, leaving the start value at about 0: a balance with the typo read neither above 0.05 nor below -0.05, the same as a balance with no start value, while `initial_value = 0.5` read above 0.45. The typo is also reported at load as "Unexpected token: intial_value". [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, trigger ladder on `power_balance_value` and error.log read. The value is a ladder reading, not an exact number.
<!-- kit:end id="bop-initial-value-typo" -->

<!-- kit:begin id="bop-vanilla-format" at="section:code-structure" -->
What the 10 vanilla BoP files use in 1.19.4.1. All lines: [vanilla-confirmed 1.19.4.1] `common/bop/*.txt` (parsed by script) and `localisation/english/Juno_bop_l_english.yml`, `bba_bop_l_english.yml`.

- Root block keys: `initial_value`, `left_side`, `right_side`, `decision_category`, `side`, `range`. Side keys: `id`, `icon`, `range`. Range keys: `id`, `min`, `max`, `modifier`, `on_activate`, `on_deactivate`. No vanilla range sets `rule`. [vanilla-confirmed 1.19.4.1] `common/bop/*.txt` (10 files). The loc object `GetActiveRangeRuleDesc` implies that a range can carry a rule. [docs] `documentation/loc_objects_documentation.md`. A `rule = { can_create_factions = yes }` block inside a range takes effect while that range is active: `has_rule = can_create_factions` read TRUE in that range and FALSE before the balance and in the left-side range, which has no rule. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, `has_rule` read in game.log. The test country's baseline was FALSE, so a range with `= no` cannot be told from no rule at all. The loc object `[THIS.GetActiveRangeRuleDesc]` printed a "Rules:" header and "Can Create Factions" for that range and nothing for the range with `= no`, and `[THIS.GetActiveRangeName]` printed the range id when no loc key existed. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, `log` effect and game.log.
- Vanilla has 10 BoPs (`BRA`, `CZE`, `DEN` twice, `ETH`, `FIN`, `ITA`, `PRC`, `SWE`, `SWI`), plus `_test_balance` in `_test.txt`, which is the wiki's example without `decision_category` and `rule`. Sides per BoP: 2 for most (both `DEN` BoPs included), 3 for `PRC`, 4 for `ETH`, 9 for `ITA`. So a BoP really can hold more sides than the two shown.
- Neighbouring ranges share their boundary value (for example -1 to -0.7, -0.7 to -0.4, -0.4 to -0.1), and the middle range sits directly in the BoP, outside any side.
- `on_activate` and `on_deactivate` are effect blocks; 135 of the 218 vanilla ones are empty. The 83 filled ones swap ideas (`swap_ideas` with `add_idea` and `remove_idea`, 23 blocks), set variables (22), call `promote_character` (10) and `log` (4), and in 38 blocks call `set_power_balance_gfx` to change a side's icon. `promote_character` is documented for country and character scope. [docs] `documentation/effects_documentation.md`. The block runs in the owner country's scope: when another country's effect set the value, `THIS`, `ROOT`, `FROM` and `PREV` inside `on_activate`, and `THIS` and `ROOT` inside `on_deactivate`, all read the balance's owner, and each change logged an `on_deactivate` and an `on_activate`. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, `log` effect and game.log. One stand-in owner was used.
- Every id needs a loc entry of the same name: the BoP id, each side id, each range id and the decision category id (`BRA_political_military_balance`, `BRA_bop_left_side`, `BRA_unstable_government`, `BRA_balance_of_power_category` in `Juno_bop_l_english.yml`).
- `BRA_political_military_balance` is referenced only by its own file and its loc, and its `decision_category` `BRA_balance_of_power_category` is defined in no decision file: a vanilla leftover, not a pattern to copy.
<!-- kit:end id="bop-vanilla-format" -->

<!-- kit:begin id="bop-example-rule-fix" at="section:example" -->
The example's `can_create_faction = yes` is not a rule. The game rule is `can_create_factions` (plural), used in vanilla and listed in the rule table of [Autonomy state modding](autonomy_state_modding.md). [vanilla-confirmed 1.19.4.1] `common/`, searched by script. A misspelled rule name is not ignored silently: an unknown rule name in a range, including the singular `can_create_faction`, is reported at load as "unknown rule '<name>'", and the balance still loads and activates. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, error.log read. Whether the unknown rule is dropped from the range was not tested.
<!-- kit:end id="bop-example-rule-fix" -->

<!-- kit:begin id="bop-variables-and-modifiers" at="section:balance-of-power-modifiers" -->
Facts about the modifier side of a BoP in 1.19.4.1.

- `power_balance_daily` and `power_balance_weekly` are country modifiers with two decimals. [docs] `documentation/modifiers_documentation.md`.
- Vanilla keeps BoP modifiers in `common/modifiers/` (`AAT_power_balance_modifiers.txt`, `BBA_power_balance_modifiers.txt`, `MUN_power_balance_modifiers.txt`) and gives each a loc key of the same name, which the tooltip shows (`FIN_bop_modifier_eradicate_socialism` in `aat_bop_l_english.yml`). The two `SWI_DEBUG_*` entries in the BBA file have no loc key. `00_static_modifiers.txt` holds a test one, `_test_power_balance_mod = { power_balance_daily = 0.02 }`. [vanilla-confirmed 1.19.4.1] files named.
- `power_balance_weekly` can also be driven by a variable inside a dynamic modifier: `power_balance_weekly = DEN_resistance_power_balance_weekly` in `common/dynamic_modifiers/aat_dynamic_modifiers.txt`. This pushes the balance without a static BoP modifier. [vanilla-confirmed 1.19.3] `common/dynamic_modifiers/aat_dynamic_modifiers.txt`.
- Three dynamic variables read the country's active BoP: `power_balance_value` (current value), `power_balance_daily` and `power_balance_weekly` (current total change). Vanilla reads the value with `set_temp_variable = { fascism_to_add = power_balance_value }` after `has_power_balance`. [docs] `documentation/dynamic_variables_documentation.md`; [vanilla-confirmed 1.19.4.1] `common/national_focus/czechoslovakia_mu.txt`.
<!-- kit:end id="bop-variables-and-modifiers" -->

<!-- kit:begin id="bop-scopes-and-operators" at="section:effects" -->
Scopes and the parameters of `set_power_balance` in 1.19.3. All lines: [docs] `documentation/effects_documentation.md`.

| Effect | Scope | Parameters |
| --- | --- | --- |
| `set_power_balance` | country only | `id`, `left_side`, `right_side`, `set_default` (default no; yes resets to `initial_value`), `set_value` (sets the value when present) |
| `remove_power_balance` | country only | `id` |
| `add_power_balance_value` | any | `id`, `value` (added to the current value), `tooltip_side` (optional, names a side in the tooltip) |
| `add_power_balance_modifier`, `remove_power_balance_modifier` | any | `id`, `modifier` (a static modifier) |
| `remove_all_power_balance_modifiers` | any | `id` |
| `set_power_balance_gfx` | any | `id`, `side`, `gfx` |

Vanilla starts a BoP in a country's history with `set_power_balance = { id = FIN_power_balance left_side = FIN_bad_side right_side = FIN_good_side set_value = -0.45 }`, and resets one with `set_default = yes` (`SWI_centralization_bop` in `common/national_focus/switzerland.txt`). `tooltip_side = ITA_communism_side` appears 6 times in `common/scripted_effects/ITA_scripted_effects.txt`. [vanilla-confirmed 1.19.4.1] `history/countries/FIN - Finland.txt`, `common/national_focus/switzerland.txt`, `common/scripted_effects/ITA_scripted_effects.txt`.
<!-- kit:end id="bop-scopes-and-operators" -->

<!-- kit:begin id="bop-triggers-1193" at="bottom" -->
## Balance of power triggers, scopes and the global claim

Scopes of the BoP triggers, from the documentation: `has_power_balance` and `has_any_power_balance` are country-scope only; `power_balance_value`, `power_balance_daily_change`, `power_balance_weekly_change`, `is_power_balance_in_range`, `is_power_balance_side_active` and `has_power_balance_modifier` are documented for any scope, but read the BoP of the country in scope. The three value triggers accept `>`, `<` and `=` on `value`. [docs] `documentation/triggers_documentation.md`.

- Vanilla also writes `range < SWI_centralization_bop_balanced` and `range > ...` in `is_power_balance_in_range`, so the strict comparison form on `range` is real. A plain `range = <id>` is the documented form. [vanilla-confirmed 1.19.4.1] `common/decisions/SWI.txt`, `common/national_focus/switzerland.txt`.
- The `side` argument of `is_power_balance_side_active` is a side id, for example `side = FIN_good_side`. The wiki example passes a name ending in `_right_range`, which reads like a range id; a range id is not a side. [vanilla-confirmed 1.19.3] `common/on_actions/09_aat_on_actions.txt`, `common/bop/FIN.txt`.
- Vanilla guards reads with `has_power_balance = { id = X }` when the BoP may not be active yet, for example before reading `power_balance_value` in `common/national_focus/czechoslovakia_mu.txt`. [vanilla-confirmed 1.19.4.1]
- The introduction says a BoP is "tracked globally" and identical in all countries that have it. The documentation words it per country: `set_power_balance` sets the "active power balance for country", `remove_power_balance` removes it "from country", `has_power_balance` is country scope, and the dynamic variables `power_balance_value`, `power_balance_daily` and `power_balance_weekly` are country scope. Vanilla starts each BoP in one country's history. [docs] `documentation/effects_documentation.md`, `documentation/triggers_documentation.md`, `documentation/dynamic_variables_documentation.md`. The global claim holds in the game: DEN starts with `DEN_balance_of_power` (welfare low range) and GER has none. As GER, `bop_set DEN_balance_of_power` activated it at 0 and `bop_add DEN_balance_of_power 0.3` moved it to 0.3, and DEN then read 0.3 as well (warfare medium range). `has_power_balance` and `power_balance_value > 0.2` were true for both DEN and GER, so one value per id is shared. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, console commands and trigger checks with Arms Against Tyranny active. In a run without any DLC, DEN had no balance at all.
<!-- kit:end id="bop-triggers-1193" -->
