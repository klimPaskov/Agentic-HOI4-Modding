# Data structures

<!-- kit:begin id="review" build="1.19.4.1" checked="2026-11-01" revision="103616" sources="documentation/dynamic_variables_documentation.md interface/core.gfx documentation/effects_documentation.md documentation/triggers_documentation.md documentation/script_concept_documentation.md documentation/script_math_functions.md documentation/script_collection_input.md documentation/script_collection_operator.md documentation/loc_formatter_documentation.md common/script_constants/ common/country_tag_aliases/ common/scorers/ common/mtth/ common/modifier_definitions/ common/defines/ common/factions/goals/ common/unit_leader/ localisation/english/" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Checked against: the effect, trigger, dynamic variable, script concept, math function, collection and formatter documentation, plus vanilla script and English localisation for usage counts.
Kit blocks added: script constants, define files, flag types (corrects the five-scope list), event-target commands, tag alias rules, `hidden_trigger` evaluation, variable tooltips (corrects "check_variable has no tooltip"), variable format codes, bindable localisation, operator additions (`randomize_variable`), math expression rules, modifier token defaults, a collections pointer, loop and array defaults, scorer notes (corrects an example), and the 41 dynamic variables the page never named.
Gaps left: the lifetime rule for regular event targets beyond a one-day event chain, what `clear_global_event_targets` clears (a test with `ROOT` and `THIS` cleared nothing), `days_left` and the `id` rows cannot be confirmed from the docs and stay `[unverified]`. The three conscription rows were run: they are triggers, not variables (see the dynamic variables section). The 1.12 list of tokenizable types and the variable range text were not re-checked. Inventory code keys such as `fascom_pop`, `CAN_beavers` and `flag_counter` are page-local example names; `pow`, `sin`, `print_global`, `var_list` and `scores` are real keys of the math functions, `print_variables` and `get_sorted_scored_countries`; `majors_owned_states` is corrected below.
**1.19.4.1 re-check (2026-11-01).** 33 statements depended on files the update changed (vanilla scans of `common/`, `events/`, `history/` and English localisation, and the define values) and all 33 were re-measured. Numbers that moved: script constants are read in 23 files (was 19), `save_event_target_as` 516 lines (was 515), event-target block openers in 80 files (was 79), `$RIGHT` 525 lines in 16 files, 444 format-code references (was 440, with new counts for `%` and `0` and a new `2` row), `localization_key` in 99 files (was 98), six variable-operator block totals, and the `is_in_array`, `any_of` and `while_loop_effect` counts. Every other statement cites files that are byte-identical in 1.19.4.1 (Steam depot manifest diff).
<!-- kit:end id="review" -->

<!-- kit:begin id="script-constants" at="section:constants" -->
### Script constants with constant:

The `@` constants above only work inside the file that defines them. HOI4 1.19.3 also has script constants, which any script file can read through the `constant:` prefix. [docs] `documentation/script_concept_documentation.md`

- Where: definition files sit in `common/script_constants/`. Vanilla ships `country_groups.txt`, `state_groups.txt`, `propaganda_campaigns.txt` and `special_project_constants.txt`. [vanilla-confirmed 1.19.4.1] `common/script_constants/`
- Format: one block per category. Its first entry must be `schema = { ... }`, which uses either `key = name` or `any_key = yes`, plus a `data` rule (`int`, `fixed_point`, a nested rule list, or `array = country` as in `country_groups.txt`). All other entries are the data. [docs] `common/script_constants/documentation.md`
- Reading: `constant:<category>.<entry>`, with a dot between category and entry. Every scoped variable accepts a constant that holds one fixed-point number; everything else works only where the entry's documentation says it takes script constants. [docs] `documentation/script_concept_documentation.md`
- Reloading: reload the constants database first, then the database that reads them, because the values are injected into the script when it loads. [docs] `common/script_constants/documentation.md`
- Vanilla reads constants in 23 files under `common/`, `events/` and `interface/`, both as target lists and as variable values. [vanilla-confirmed 1.19.4.1] `common/decisions/CHI_decisions.txt`, `common/decisions/SIA.txt`

```text
# common/script_constants/country_groups.txt (shortened)
country_groups = {
    schema = { any_key = yes  array = country }
    nordics = { SWE NOR FIN DEN ICE }
}

# reading it, in the style of common/decisions/CHI_decisions.txt
any_country_with_original_tag_of = {
    target = constant:country_groups.nordics
    has_defensive_war = yes
}
```
<!-- kit:end id="script-constants" -->

<!-- kit:begin id="defines-files" at="section:defines" -->
In 1.19.4.1 `common/defines/` holds three base files: `00_defines.lua`, `00_graphics.lua` and `01_career_profile.lua`. The warning above names only the first two. [vanilla-confirmed 1.19.4.1] `common/defines/`. A same-name copy of `01_career_profile.lua` with its last define line (`PROFILE_PICTURE_BACKGROUND_OPACITY`) deleted logged "LUA Error: incorrect lua value: PROFILE_PICTURE_BACKGROUND_OPACITY" at load, the only line not in the clean controls. The game did not crash: it reached the main menu and ran to 1936.01.01. So the damage seen from this file was a define error that names the missing define. The career profile screen was not opened, and the value the game used in place of the missing define was not read. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, one-mod launch, error.log and game.log read.

The values behind the references below are unchanged: `EVENT_TIMEOUT_DEFAULT = 13`, `FOCUS_TREE_CONTINUE_FACTOR = 1.5`, `END_DATE = "1949.1.1.1"`, `UNIT_EXP_LEVELS = { 0.1, 0.3, 0.75, 0.9 }` and `MAX_EFFECT_ITERATION = 1000`. [vanilla-confirmed 1.19.4.1] `common/defines/00_defines.lua`
<!-- kit:end id="defines-files" -->

<!-- kit:begin id="flag-types" at="section:flags" -->
The list of five flag scopes above is incomplete for 1.19.3. There are six current flag types and one deprecated type. Every row: [docs] `documentation/effects_documentation.md` and `documentation/triggers_documentation.md`.

| Flag type | Set / clear / modify (effects) | Check (trigger) | Scope |
| --- | --- | --- | --- |
| global | `set_global_flag` / `clr_global_flag` / `modify_global_flag` | `has_global_flag` | any |
| country | `set_country_flag` / `clr_country_flag` / `modify_country_flag` | `has_country_flag` | COUNTRY |
| state | `set_state_flag` / `clr_state_flag` / `modify_state_flag` | `has_state_flag` | STATE |
| character | `set_character_flag` / `clr_character_flag` / `modify_character_flag` | `has_character_flag` | CHARACTER |
| military industrial organization | `set_mio_flag` / `clr_mio_flag` / `modify_mio_flag` | `has_mio_flag` | INDUSTRIAL_ORG |
| special project | `set_project_flag` / `clr_project_flag` / `modify_project_flag` | `has_project_flag` | SPECIAL_PROJECT |
| unit leader (deprecated) | `set_unit_leader_flag` / `clr_unit_leader_flag` / `modify_unit_leader_flag` | `has_unit_leader_flag` | CHARACTER |

- Special project flags are the type the wiki text never mentions. Vanilla uses them in 4 files under `common/special_projects/` (61 `set_project_flag` lines, 66 `has_project_flag` lines). `has_project_flag` measures `date` and `days` from the last time the flag was modified. [vanilla-confirmed 1.19.4.1] `common/special_projects/projects/land_projects.txt`
- MIO flags are documented but no vanilla file sets or checks one. [vanilla-confirmed 1.19.4.1] `common/` (0 files)
- The docs mark `set_unit_leader_flag` as deprecated in favour of `set_character_flag`, and `has_unit_leader_flag` in favour of `has_character_flag`. Vanilla still uses the old pair (14 and 21 files), so it keeps working; write new script with the character pair. The wiki's guess that it will be removed soon is [unverified]. [docs] `documentation/effects_documentation.md`
- `modify_<type>_flag = { flag = <name> value = <number> }` only changes a flag that already exists. Vanilla uses `modify_country_flag` in 7 files, `modify_state_flag` in 7 and `modify_global_flag` in 3; `modify_character_flag` has no vanilla use. [docs] `documentation/effects_documentation.md`
- The block form with a timer is common in vanilla: `set_country_flag = { flag = ENG_trade_unions_demand_timer value = 1 days = 30 }` appears on 22 lines. [vanilla-confirmed 1.19.4.1] `common/decisions/ENG.txt`
<!-- kit:end id="flag-types" -->

<!-- kit:begin id="event-target-commands" at="section:event-targets" -->
The four event-target commands as the 1.19.3 documentation describes them. The docs give one line each and say nothing about lifetime. Wording column: [docs] `documentation/effects_documentation.md`, `documentation/triggers_documentation.md`.

Lifetime of a regular target against a global one: a regular target saved with `save_event_target_as` was gone in a later, separate effect run, while a global target saved with `save_global_event_target_as` was still there. In the same effect, and in events fired from the saving event both at once and after a delay of one day, the regular target was still available, so the wiki's rule that it disappears with the event chain it started did not show in a one-day chain. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, effects run from the console and events, game.log read. Only a one-day delay was tested.

| Command | Kind and scope | Docs wording | Vanilla use |
| --- | --- | --- | --- |
| `save_event_target_as` | effect, any scope | save an event target | 516 lines in 83 files |
| `save_global_event_target_as` | effect, any scope | save a global event target | 134 lines in 40 files |
| `clear_global_event_target` | effect, any scope | clear a global event target | 61 lines in 17 files |
| `clear_global_event_targets` | effect, takes a scope keyword | clear all global event targets | none |
| `has_event_target` | trigger, any scope | checks if the current scope or the global scope has the target saved | 105 lines in 16 files |

Use column: [vanilla-confirmed 1.19.4.1] `common/`, `events/`, `history/` (line and file counts of the command name).

- `clear_global_event_targets` accepts the scope keywords THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED and CAPITAL as its value, but vanilla never uses it. What a keyword selects is not documented. Clear named targets one at a time with `clear_global_event_target = <name>` instead. [docs] `documentation/effects_documentation.md` In a test, `clear_global_event_targets = ROOT` (run in GER, with ROOT being ENG) and `clear_global_event_targets = THIS` each left both saved global targets alive. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, effect log scan. `= yes` was not tried.
- A saved target is read as a scope (`event_target:name = { ... }`, 639 block openers in 80 files) and as a value (`key = event_target:name`, 459 lines in 75 files, for example `tag`, `target` and `is_in_faction_with`). Both kinds of target use the same `event_target:` prefix. [vanilla-confirmed 1.19.4.1] `common/`, `events/`, `history/`
<!-- kit:end id="event-target-commands" -->

<!-- kit:begin id="tag-alias-rules" at="section:country-tag-aliases" -->
Rules from the comment header of the vanilla alias file, which the wiki list above only partly covers. All bullets: [vanilla-confirmed 1.19.3] `common/country_tag_aliases/tag_aliases.txt`.

- An alias name is a three-letter tag and must differ from every real tag.
- `variable`, `event_target` and `global_event_target` map the alias straight to one target. Use only one of them; once one is present the game does no other check.
- Otherwise the candidates come from any mix of `original_tag`, `targets` and `target_array`. With none of them the game scans every existing country, which the file warns against for performance.
- Inside the alias trigger list the current scope is the candidate country and `PREV` is the scope that wrote the alias.
- Without `country_score` the alias returns the first existing country that matches. With it, the highest score above 0 wins. `fallback` is used without any trigger or score check.
- The file defines 21 aliases. The Spanish civil war sides `SPA` to `SPD` use `original_tag = SPR` plus a country flag, `VIC` uses `has_focus_tree`, and `SOS` uses `has_cosmetic_tag`.
<!-- kit:end id="tag-alias-rules" -->

<!-- kit:begin id="hidden-trigger-evaluation" at="section:trigger-usage" -->
A `hidden_trigger` is not shown in the tooltip, but the game can still evaluate it while it builds the tooltip. Set `tooltip_evaluation = eval` when the hidden trigger has side effects such as temp variable changes or uses random choices. `no_eval` skips that evaluation and is only safe when there are no side effects or random parts. `legacy` is the old, less predictable behaviour and the docs call explicit use very likely a bug. [docs] `documentation/triggers_documentation.md` (the three values are listed in the HTML copy; the Markdown copy drops that text)

Vanilla sets `tooltip_evaluation = eval` twice, both in `common/factions/goals/faction_goals_short_term.txt`. [vanilla-confirmed 1.19.4.1]

The temp variable operators that count as triggers are the `_temp_` forms of set, add, subtract, multiply, divide, modulo, clamp, round and random, the temp array operators, `find_highest_in_array`, `find_lowest_in_array`, the `_temp` scorer triggers, `log` and `print_variables`. `randomize_temp_variable` is documented as an effect only. [docs] `documentation/triggers_documentation.md`
<!-- kit:end id="hidden-trigger-evaluation" -->

<!-- kit:begin id="variable-tooltip-correction" at="section:localisation" -->
The text above says `check_variable` cannot take a tooltip. In 1.19.3 it can. [docs] `documentation/triggers_documentation.md`

- `check_variable` accepts `tooltip = <loc key>`, and the text may use `$LEFT$` and `$RIGHT$`. [docs] `documentation/triggers_documentation.md`
- `set_variable` and `set_temp_variable` document the same `tooltip`. [docs] `documentation/effects_documentation.md`
- `add_to_variable` and its siblings do not list `tooltip` in the docs, yet vanilla uses it on most `add_to_variable` blocks. Counts are block-form uses with a direct `tooltip` key, temp and regular variants together. [vanilla-confirmed 1.19.4.1] `common/` (scan of all `.txt` files under `common/`, `events/`, `history/`)

| Operator | Blocks | With tooltip | Files with tooltip |
| --- | --- | --- | --- |
| `add_to_variable` | 6593 | 3973 | 97 |
| `set_variable` | 8255 | 147 | 18 |
| `subtract_from_variable` | 882 | 18 | 7 |
| `check_variable` | 5619 | 37 | 6 |
| `multiply_variable` | 492 | 0 | 0 |
| `divide_variable` | 161 | 0 | 0 |
| `modulo_variable` | 3 | 0 | 0 |
| `clamp_variable` | 272 | 0 | 0 |

- The operator table above lists `tooltip` for `multiply_variable`, `divide_variable` and `modulo_variable`. The docs do not list it there [docs] `documentation/effects_documentation.md`, and no vanilla block uses it (0 of 492, 161 and 3 blocks, temp forms included) [vanilla-confirmed 1.19.4.1] `common/`. The engine accepts it on `multiply_variable` and `divide_variable`: with `tooltip = <key>` the variables gave the expected values (4 and 4). On `modulo_variable` a `tooltip` key made the effect fail with "modulo is not positive" in `error.log` and the variable stayed unchanged, while the same modulo without a tooltip worked (value 1). The `tooltip = <key>` string form on `add_to_variable` also worked (value 2). [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, scripted effects, game.log and error.log read. The block form `tooltip = { <key> }` on `add_to_variable` broke the parse of the effect (load logged "Non assign effect is not enclosed in {}") and the variable stayed unchanged. The tooltip text itself was not read.
- The example on this page uses `tooltip = add_cats_to_dogs_tt` but defines the key `add_cat_to_dogs_tt`. The two spellings differ, so copy one spelling into both places. [unverified]
- `$LEFT$` and `$RIGHT$` take the same pipe codes as `[?var|code]`. Vanilla writes `$RIGHT|+=%1$` 288 times, `$RIGHT|-=%1$` 81 times and `$RIGHT|0Y$` 5 times. `$LEFT` appears on only 8 lines in 6 files, `$RIGHT` on 525 lines in 16 files. [vanilla-confirmed 1.19.4.1] `localisation/english/`
<!-- kit:end id="variable-tooltip-correction" -->

<!-- kit:begin id="variable-format-codes" at="section:localisation" -->
Codes after the pipe in `[?variable|code]` that vanilla localisation uses. There are 444 such references in `localisation/english/`; the table lists the most common ones. All rows: [vanilla-confirmed 1.19.4.1] `localisation/english/`.

| Code | Uses | Files |
| --- | --- | --- |
| `+0` | 145 | 5 |
| `Y0` | 82 | 14 |
| `%` | 50 | 5 |
| `0` | 20 | 6 |
| `%Y0` | 19 | 2 |
| `G0` | 14 | 3 |
| `R0` | 12 | 1 |
| `%G0` | 9 | 1 |
| `H0` | 9 | 2 |
| `0H` | 8 | 4 |
| `2` | 8 | 1 |
| `%0G` | 5 | 2 |
| `%+` | 4 | 1 |
| `+%0` | 3 | 1 |

- The digit, the colour letter and the sign or percent symbol can come in either order (`%G0` and `%0G`, `H0` and `0H`). [vanilla-confirmed 1.19.4.1] `localisation/english/`
- The colour letter `H` is common in vanilla (19 references) but the table above does not explain it. It is the header colour: `interface/core.gfx` gives `H` the same yellow as `Y` and comments it "Header". [vanilla-confirmed 1.19.4.1] `interface/core.gfx`. The exact code `%+0` does not occur in 1.19.4.1 vanilla `[?variable|code]` references; `+0`, `%+` and `+%0` do.
<!-- kit:end id="variable-format-codes" -->

<!-- kit:begin id="bindable-localisation" at="section:localisation" -->
#### Bindable and formatted localisation

Many 1.19.3 tooltip arguments take more than a plain key.

- Bound object: `tooltip = { localization_key = KEY PARAM = <value> }`. Each `PARAM` fills `$PARAM$` in the text of `KEY`, and a value can itself be a plain key, a string or another bound object. [docs] `documentation/script_concept_documentation.md`
- Formatted form: `formatter|token`, for example `custom_effect_tooltip = idea_desc|canadian_pacific_railway`. The shipped formatters are `advisor_desc`, `building_state_modifier`, `character_name`, `country_culture`, `country_leader_desc`, `idea_desc`, `idea_name` and `tech_effect`. [docs] `documentation/loc_formatter_documentation.md`
- Vanilla uses `localization_key =` in 99 files under `common/` and `events/`, and a parameter value may be a scripted localisation call such as `CHARACTER = [GetAscendedAdvisorName1]`. [vanilla-confirmed 1.19.4.1] `common/scripted_effects/GER_scripted_effects.txt`
- Formatter strings on `custom_effect_tooltip` appear on 18 vanilla lines. [vanilla-confirmed 1.19.4.1] `common/` and `events/`
- Support is per argument. `custom_effect_tooltip` and `custom_override_tooltip` take it, and the docs say the `tooltip` of `every_allied_country`, `random_allied_country`, `any_country_of` and `all_claimant` does too. [docs] `documentation/effects_documentation.md`, `documentation/triggers_documentation.md`
- The `tooltip` of the variable operators is documented only as a loc key with LEFT and RIGHT tokens, so the bound-object form there is [unverified].
<!-- kit:end id="bindable-localisation" -->

<!-- kit:begin id="operator-additions" at="section:operators" -->
Operators and details the table above lacks.

- `randomize_variable` and `randomize_temp_variable` draw a value from a distribution. The short form `randomize_temp_variable = num_dogs` is uniform from 0 to 1. The block form takes `var`, `distribution` (`uniform`, `binomial` or `poisson`), `min`, `max` and, for poisson, `lambda`; binomial needs `max` when `min` is given. The temp form is an effect only. [docs] `documentation/effects_documentation.md`
- Vanilla has 9 such blocks in 3 files. [vanilla-confirmed 1.19.4.1] `common/scripted_effects/BUL_scripted_effects.txt`, `common/on_actions/13_goe_on_actions.txt`, `history/countries/BUL - Bulgaria.txt`

```text
randomize_temp_variable = {
    var = BUL_random_ff_forming_chance
    distribution = binomial
    min = 0
    max = 100
}
```

- Every arithmetic operator accepts a math expression where it takes a number, for example `add_to_variable = { num_dogs = { value = num_cats multiply = 2 } }`. The docs list this for set, add, subtract, multiply and divide, and do not list it for `modulo_variable` or `clamp_variable`. [docs] `documentation/effects_documentation.md`
- `clamp_variable` computes max(min(var, max), min), and logs an error (debug mode) when `max` is below `min`. [docs] `documentation/effects_documentation.md`
- `career_profile_set_temp_variable` and `career_profile_set_temp_playthrough_variable` are documented only in the trigger documentation and take `var` and `value`. The example above uses a `sum` key that the docs do not mention, so treat that example as wrong. [docs] `documentation/triggers_documentation.md`
<!-- kit:end id="operator-additions" -->

<!-- kit:begin id="math-expression-details" at="section:math-functions" -->
Rules the 1.19.3 documentation adds to the function table above.

- A math expression is a `value` accumulator that sequential statements change. Statement kinds: no-argument operations (`round = yes`), operations that take a number, variable or nested expression (`add = 5`, `clamp = { min = 0 max = 100 }`), flow control (`if` whose `limit` is itself a math expression, plus `else`), and collection iterators (`every_collection`). [docs] `documentation/script_concept_documentation.md`
- All arithmetic is fixed point. Any non-zero value is true, and every comparison or logic function returns 1.0 or 0.0. [docs] `documentation/script_concept_documentation.md`
- Silent failure: an expression that does not parse is replaced by 0.0 at runtime. [docs] `documentation/script_concept_documentation.md`
- The docs expect expressions to run faster than the same calculation spread over temp variables. [docs] `documentation/script_concept_documentation.md`
- The documentation's table of contents names the comparison functions `<` and `>`, while its examples use `less_than` and `greater_than`, as the table above does. [docs] `documentation/script_math_functions.md`
- Vanilla writes `else_if` after `if` inside an expression and passes a nested expression as an argument, for example `multiply = { value = 0 if = { limit = { value = num_researched_technologies less_than = 50 } add = 1.25 } else_if = { ... } }`. [vanilla-confirmed 1.19.3] `common/factions/goals/faction_goals_short_term.txt`
- `every_collection = { named_collection = <name> <statements> }` runs the statements once per element with that element as the scope. The named collection comes from `common/collections/`; vanilla uses `faction_members`. [vanilla-confirmed 1.19.3] `common/factions/goals/faction_goals_short_term.txt`. For collections see [Collection modding](collection_modding.md).
- An expression also works as a trigger: `check_expr = { value = num_infantry greater_than = { value = num_units multiply = 0.8 } }` in unit leader trait `gain_xp` blocks. [vanilla-confirmed 1.19.4.1] `common/unit_leader/00_traits.txt`
- A scan of vanilla blocks that start with `value =` found 28 expressions in 3 files. They use only `add`, `subtract`, `multiply`, `divide`, `clamp`, `round`, `less_than`, `greater_than`, `if`/`else_if` and `every_collection`. The other documented functions (`and`, `or`, `not`, `xor`, `equals`, `not_equals`, `greater_than_or_equals`, `less_than_or_equals`, `min`, `max`, `mod`, `pow`, `root`, `log`, `lerp`, `sin`, `cos`, `tan`, `atan`, `atan2`) have no vanilla use. Their syntax is documented but not exercised. [vanilla-confirmed 1.19.4.1] `common/factions/goals/faction_goals_short_term.txt`, `common/unit_leader/00_traits.txt`, `common/scripted_effects/INS_scripted_effects.txt`
<!-- kit:end id="math-expression-details" -->

<!-- kit:begin id="modifier-token-defaults" at="section:modifier-tokens" -->
Defaults and reach that the section above leaves out. All bullets: [vanilla-confirmed 1.19.3] `common/modifier_definitions/modifier_definitions.txt`.

- Defaults in the shipped template: `color_type` is `bad`, `value_type` is `number`, `postfix` is `none`, `category` is `all`.
- `modifier@token` reads a token in state and country scope; `leader_modifier@token` and `unit_modifier@token` read it in unit leader scope. The dynamic variable documentation also lists `modifier` for military industrial organizations (`modifier@military_industrial_organization_research_bonus`) and for states (`123.modifier@local_manpower`).
- The shipped file contains only the commented template. Vanilla defines no custom modifier tokens, so every token you read this way must be defined by your mod.
<!-- kit:end id="modifier-token-defaults" -->

<!-- kit:begin id="collections-pointer" at="section:arrays" -->
Collections are the 1.19.3 alternative to an array plus a loop when you need to build or filter a set of scopes: a collection has an `input`, optional `operators` and an optional `name`. The docs call them more efficient and easier to script in many cases, and warn that a collection can contain the same object more than once. [docs] `documentation/script_concept_documentation.md`

Syntax, inputs, operators and the triggers and effects that read collections are on [Collection modding](collection_modding.md).
<!-- kit:end id="collections-pointer" -->

<!-- kit:begin id="loop-array-defaults" at="section:arguments" -->
Defaults the 1.19.3 documentation gives for the commands above. All rows: [docs] `documentation/effects_documentation.md` and `documentation/triggers_documentation.md`.

| Command | Documented defaults |
| --- | --- |
| `for_each_loop` | `value` is `v`, `index` is `i`, `break` is `break` |
| `for_loop_effect` | `start` 0, `end` 0, `compare` `less_than`, `add` 1, `value` `v`, `break` `break` |
| `while_loop_effect` | `break` is `break`; `limit` is tested before every iteration |
| `for_each_scope_loop` | `break` is `break`; optional `tooltip` |
| `random_scope_in_array` | `break` is `break`; optional `limit` |
| `find_highest_in_array`, `find_lowest_in_array` | `value` is `v`, `index` is `i`; both optional |
| `all_of` | `value` is `v`, `index` is `i` |
| `any_of` | `value` is `value`, `index` is `index` |
| `add_to_array` | `value` optional (the current scope is added); `index` optional (default end, later elements shift) |
| `remove_from_array` | `value` or `index`; with neither, the last element goes |
| `resize_array` | `value` optional, default 0, fills new slots |

- The docs disagree between `any_of` and `all_of` on the default names. Name `value` and `index` explicitly in both. [docs] `documentation/triggers_documentation.md`
- A loop stops when the temp variable named by `break` is set to a non-zero value. [docs] `documentation/effects_documentation.md`
- Correction: the `for_loop_effect` row says its limit is checked at the beginning and after each run. `for_loop_effect` has no `limit`; `start`, `end`, `compare` and `add` control it. `while_loop_effect` is the one with a `limit`. [docs] `documentation/effects_documentation.md`
- The loop cap is `MAX_EFFECT_ITERATION = 1000` ("maximum allowed iteration for loop effects"), so the wiki figure still holds. [vanilla-confirmed 1.19.4.1] `common/defines/00_defines.lua`
- Vanilla use (lines / files): `for_each_scope_loop` 187 / 49, `is_in_array` 325 / 68, `any_of` 249 / 23, `all_of_scopes` 61 / 16, `while_loop_effect` 46 / 21, `for_loop_effect` 23 / 9, `for_each_loop` 6 / 4, `random_scope_in_array` 3 / 2. `all_of`, `find_lowest_in_array` and `resize_array` have no vanilla use. [vanilla-confirmed 1.19.4.1] `common/`, `events/`, `history/`
<!-- kit:end id="loop-array-defaults" -->

<!-- kit:begin id="scorer-notes" at="section:scorers" -->
The first scorer example wraps `targets` in an extra block named `majors_owned_states`. Vanilla scorer files put `targets` directly under the scorer name, as the second example on this page does. Drop the wrapper when copying it. [vanilla-confirmed 1.19.3] `common/scorers/country/generic_platonic_scorers.txt`

- A `targets` block may repeat `target_array`; one vanilla scorer lists four arrays (`potential_and_current_enemies`, `enemies_of_allies`, `neighbors`, `global.majors`). The other keys vanilla uses in scorers are `targets_dynamic`, `target_non_existing`, `target_trigger`, `target_root_trigger`, `score` and `base`. [vanilla-confirmed 1.19.3] `common/scorers/country/`
- In `score` the vanilla comment says THIS is the target and FROM is the initiator, so `FROM.ai_strategy_conquer@THIS` reads the initiator's strategy value towards the target. [vanilla-confirmed 1.19.3] `common/scorers/country/`
- Defaults when you leave names out: `get_highest_scored_country` stores into `highest_scored_country`, and `get_sorted_scored_countries` uses `sorted_country_list` and `country_list_scores`. Only the `_temp` forms exist as triggers. [docs] `documentation/effects_documentation.md`, `documentation/triggers_documentation.md`
- The docs describe the plain `get_highest_scored_country` as writing a temp variable and the `_temp` form as writing a regular one. Vanilla shows the opposite: the plain form writes scoped regular variables, for example `var = GLOBAL.platonic_big_fascist` (9 uses). This matches the page. [vanilla-confirmed 1.19.4.1] `common/scripted_effects/00_scripted_effects.txt`
- `get_sorted_scored_countries` has no vanilla use. It sorts descending: index 0 of the score array and of the country array is the highest score. With `fascist_major_scorer` at the 1936 start both arrays held 99 entries, and the order began GER (306), ITA (233.9), PRU (15) and ended in zero scores. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, effect run from the console, game.log read. Only the first six and the last three entries were printed, so the order among tied scores is not known.
<!-- kit:end id="scorer-notes" -->

<!-- kit:begin id="dynamic-variables-1-19-3" at="section:game-variables" -->
### Dynamic variables in 1.19.3

The game documents these read-only variables as dynamic variables, in six scopes: global, country, state, unit_leader, military_industrial_organization and special_project. There is no operative scope: the operative rows in the tables above (`operation_country`, `operative_captor` and the rest) are listed under unit_leader. [docs] `documentation/dynamic_variables_documentation.md`

- Variables per scope: country 265, unit_leader 66, state 22, global 19, military_industrial_organization 8, special_project 3. [docs] `documentation/dynamic_variables_documentation.md`
- Some names exist in several scopes: `modifier` (country, state, MIO), `resource` (country, state), `power_balance_value` (country, global), and `num_battalions`, `num_battalions_with_type`, `num_equipment`, `num_ships`, `num_ships_with_type` (country, unit_leader). [docs] `documentation/dynamic_variables_documentation.md`
- 94 entries are generated from the trigger of the same name. [docs] `documentation/dynamic_variables_documentation.md`
- Targets use `@`, for example `GER.air_intel@ENG` or `faction_resource_extracted@steel`. [docs] `documentation/dynamic_variables_documentation.md`

The 41 documented variables this page never named. Every row: [docs] `documentation/dynamic_variables_documentation.md` (meanings restated, not quoted).

| Variable | Scope | Meaning |
| --- | --- | --- |
| `army_chief`, `navy_chief`, `air_chief`, `theorist` | country | the character currently hired in that slot |
| `high_command`, `political_advisor` | country | an array of the currently hired high command members or political advisors |
| `air_intel` | country | air intel on a target country (`GER.air_intel@ENG`); the page's `airforce_intel` row uses a different name |
| `avg_unit_entrenchment_ratio` | unit_leader | average entrenchment ratio over the leader's units |
| `convoys_destroyed` | country | total convoys this country has sunk |
| `days_until_next_election` | country | days until the next election, -1 if there will never be one |
| `deployed_total_manpower_k` | country | total deployed manpower in thousands |
| `energy_ratio` | country | current energy fulfilment compared with what the factories need, 1 is 100% |
| `facility_province_id`, `facility_state` | special_project | province and state where the project is researched |
| `scientist` | special_project | the scientist researching the project |
| `faction_influence_rank`, `faction_influence_ratio`, `faction_influence_score` | country | the country's influence rank, ratio and value inside its faction |
| `faction_manifest_fulfillment` | country | fulfilment value of the country's faction manifest |
| `faction_power_projection` | country | power value of the country's faction projection |
| `faction_resource_extracted` | country | resource extracted by the country's faction, resource as target (`@steel`) |
| `faction_resource_extracted_total` | country | all resources extracted by the country's faction |
| `global_resource_extracted` | global | resource extracted by the whole world, resource as target (`@steel`) |
| `global_resource_extracted_total` | global | all resources extracted by the world |
| `longest_war_length` | country | months the country has been at war |
| `num_nukes_being_dropped` | country | nukes currently ready to be dropped |
| `num_nukes_left_to_drop` | country | nukes still to drop in this game tick, useful between drops such as in `on_nuke_drop` |
| `num_of_civilian_factories_in_cores`, `num_of_military_factories_in_cores`, `num_of_naval_factories_in_cores` | country | factories of that type in the scope country's core states controlled by the target country (`num_of_civilian_factories_in_cores@GER`); the docs text of all three says "civilian" |
| `num_of_controlled_states` | country | number of controlled states; the page's `num_controlled_states` is a separate row |
| `total_constructed_gun_emplacement`, `total_constructed_naval_headquarter`, `total_constructed_naval_supply_hub` | country | buildings of that type the country has constructed in total |
| `total_equipment_produced_ballistic_missile`, `total_equipment_produced_emplacement_gun_ammo`, `total_equipment_produced_land_cruiser`, `total_equipment_produced_missile_launcher`, `total_equipment_produced_nuclear_missile`, `total_equipment_produced_sam_missile`, `total_equipment_produced_support_ship` | country | total produced equipment of that type |

- The page's `airforce_intel` row has no counterpart in the docs. Vanilla uses `airforce_intel` only as a key of `intel_level_over` and `add_intel`, never as a variable, so use `air_intel`. [vanilla-confirmed 1.19.4.1] `common/achievements.txt`, `common/operations/00_operations.txt`
- Not in the dynamic variable docs: `id` (but `THIS.id` is used in vanilla, for example `common/decisions/CZE.txt`), `days_left`, `target_conscription_amount`, `conscription_ratio` and `current_conscription_amount` (the last three exist as triggers). Treat their variable use as [unverified], except `THIS.id`, which vanilla uses [vanilla-confirmed 1.19.4.1], and the three conscription names. Those three are triggers and not variables: as triggers `current_conscription_amount`, `target_conscription_amount` and `conscription_ratio` read real values for GER (`> 0` was true), but read as variables (bare, as `THIS.<name>` or in loc) they gave 0, and `check_variable` on them was false while a stability control was true. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, effect and trigger run from the console, game.log read. `days_left` was not tested.
- Vanilla localisation prints a dynamic variable the same way as any other, for example `[?days_until_next_election|0Y]`. [vanilla-confirmed 1.19.4.1] `localisation/english/`
<!-- kit:end id="dynamic-variables-1-19-3" -->
