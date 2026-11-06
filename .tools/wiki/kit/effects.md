# Effects

<!-- kit:begin id="review" build="1.19.4.1" checked="2026-11-01" revision="105661" sources="documentation/effects_documentation.md documentation/triggers_documentation.md documentation/script_math_functions.md common/raids/ common/strategic_locations/ common/scripted_effects/ common/game_rules/ common/resistance_compliance_modifiers/ common/special_projects/ common/operations/ common/medals/ common/on_actions/" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Checked against `documentation/effects_documentation.md` (all 553 effects: scope, parameter keys and stated defaults compared with the tables), the raid, strategic location, game rule, scripted effect and special project files under `common/`, and text searches of vanilla script and `hoi4.exe`.
- Kit blocks added: 34, from `coverage` (scope check, the 21 effects the wiki never named, non-effects) to `scripted-effect-corrections`. Each is named after what it fixes or adds.
- Wrong or stale wiki text found: `add_temporary_buff_to_units` (not in 1.19.3); the examples for `modify_project_flag` and `set_mio_funds_gain_factor`; the first `raid_damage_units` parameter row; the `end_wars` default of `set_autonomy`; the "inclusive" bounds of `random_hours` and `random_days`; `tag` for `remove_building`; the notes "Only works on missions" (`activate_targeted_decision`) and "Deprecated" (`create_corps_commander`); the set_rule list; and the paths `commmon/autonomous_states`, `common/decisions/catergories` and `common/resistance_modifiers.txt`.
- Deprecated or obsolete notes: `create_faction` and the three unit leader flag effects match the documentation; "extremely buggy" for `replace_unit_leader_trait` is unverified. Example keys flagged as unknown are documented (`controller_priority`, `mapmode`, `copy_completed_from`, `base_bonus`, `scores`, `set_root`, `ignore_death_chance`, and `prototyp_reward_option` in the documentation's own spelling) or are placeholders (`EQ_TYPE`, `EQ_LEVEL`, `eq_amount`, `NESTEDLOC`, `specialization_token`, `d_transfer_states`).
- Gaps left: values and defaults were compared only where the documentation states them; effects with a one-line documentation stub (`boost_planning`, `ai_message`, `set_leader_name`, `add_scaled_political_power`) stay `[unverified]` beyond the load and run results tagged `[game-tested 1.19.4.1]`. The "Version Added" column was checked on 2026-11-01 as far as the installed files allow (see the note under Effect scopes).
**1.19.4.1 re-check (2026-11-01).** 51 statements depended on vanilla scans or files that the update changed, and all 51 were re-measured on the installed files. Numbers moved: `while_loop_effect` in 21 files (was 20), `random_hours` in 92 (91), `leader_score` in 7 (8), `destroy_unit` 10 uses (8), `activate_targeted_decision` 63 distinct decisions (62), `add_to_war` with `single_target_only` in 3 files (2), `create_field_marshal` 4 blocks (5), 23 of the 27 `set_rule` names occur in vanilla (24), and vanilla now passes `version_name` to `create_production_license` in 3 blocks, while four older notes (the ribbons use of `career_profile_set_temp_variable`, `legacy_id`, the 13 character files with `navy`, and the `seed` and `log` counts) were corrected against the installed files. Every other statement cites files that are byte-identical in 1.19.4.1 (Steam depot manifest diff).
<!-- kit:end id="review" -->

<!-- kit:begin id="coverage" at="top" -->
How this page lines up with the 1.19.3 documentation.

- `documentation/effects_documentation.md` documents 553 effects. The wiki text names 532 of them; the other 21 are described on this page: `for_each_loop`, `for_loop_effect`, `while_loop_effect`, `random_scope_in_array`, `get_highest_scored_country`, `get_sorted_scored_countries` and `print_variables` (under "Arrays"), `randomize_variable` and `randomize_temp_variable` (under "Variables"), `clear_rule`, `set_relation_rule` and `ai_message` (under "Country scope > General"), `add_scaled_political_power` (under "Mana"), `capture_by`, `release_captured_generals_from`, `release_from_captivity`, `set_leader_name`, `set_leader_description` and `set_leader_portrait` (under "Unit leaders"), `boost_planning` (under "Combat") and `add_region_efficiency` (under "Other scopes"). [docs]
- Every effect row in the scope sections sits under a scope that the documentation also supports. For the effects below the documentation names one more scope than the page shows. Treat the extra scope as documented but unproven: vanilla runs `remove_unit_leader_role` and `set_portraits` inside character scope, for example `GER_karl_donitz = { remove_unit_leader_role = yes }`. [docs] `documentation/effects_documentation.md`, [vanilla-confirmed 1.19.4.1] `common/decisions/GER.txt`

| Effect | Where the page shows it | Scopes in the documentation |
| --- | --- | --- |
| `state_event` | State scope | STATE, COUNTRY |
| `remove_building` | State scope, Buildings | STATE, COUNTRY (pass `state` or `province`) |
| `set_portraits` | Character scope | COUNTRY, CHARACTER (pass `character = <token>`) |
| `remove_unit_leader_role` | Character scope, Unit leaders | COUNTRY, CHARACTER |
| `set_occupation_law_where_available`, `set_faction_name`, `activate_targeted_decision`, `remove_targeted_decision` | Country scope | STATE, COUNTRY |
| `add_dynamic_modifier`, `remove_dynamic_modifier`, `force_update_dynamic_modifier` | Any scope (country, state, character) | also SPECIAL_PROJECT |

- Names in the tables that are not engine effects: `overlord`, `owner`, `controller`, `faction_leader` and `capital_scope` are scopes, and the rows under "Useful scripted effects" are scripted effects written in vanilla script. [vanilla-confirmed 1.19.4.1] `common/scripted_effects/00_scripted_effects.txt`
- `career_profile_set_temp_variable` and `career_profile_set_temp_playthrough_variable` are listed in `documentation/triggers_documentation.md`, not in the effects documentation. [docs]
- `add_temporary_buff_to_units` is not in the effects documentation and no vanilla script uses it (see the correction under "Combat"). [docs] `documentation/effects_documentation.md`, [vanilla-confirmed 1.19.4.1] `common/`, `events/`, `history/`. That the engine rejects it is [unverified].
<!-- kit:end id="coverage" -->

<!-- kit:begin id="iterator-options" at="section:effect-scopes" -->
Optional keys of the `every_*` and `random_*` effect scopes. Besides `limit`, the documentation lists these keys for the iterators in the table above. [docs] `documentation/effects_documentation.md`

| Key | Applies to | Meaning |
| --- | --- | --- |
| `tooltip = <loc key>` | most `every_*`; some `random_*` such as `random_unit_leader`, `random_army_leader`, `random_navy_leader`, `random_character`, `random_scientist`, `random_state_division` | Replaces the tooltip title of the block. `every_allied_country` also takes a bindable localisation block here. |
| `random_select_amount = <int>` | `every_*` only | Runs the block on that many randomly picked matches instead of on all of them. |
| `display_individual_scopes = yes` | `every_*` only | Default `no`: the block's effects are shown once in the tooltip. `yes` shows them once per matching scope. |
| `include_invisible = yes` | `every_unit_leader`, `every_army_leader`, `every_navy_leader`, `every_character`, `every_scientist`, `every_active_scientist`, `every_military_industrial_organization`, and `random_unit_leader`, `random_army_leader`, `random_navy_leader`, `random_military_industrial_organization` | Default `no`. The documentation gives no further detail. |

Usage in vanilla: `random_select_amount` in 32 files, `display_individual_scopes` in 13 files and `include_invisible` in 1 file (`common/national_focus/finland.txt`, inside `every_army_leader`). [vanilla-confirmed 1.19.4.1]

```text
every_other_country = {
    limit = { has_war_with = ROOT }
    random_select_amount = 3
    display_individual_scopes = yes
    country_event = my_event.1
}
```

`every_country_with_original_tag` and `random_country_with_original_tag` need `original_tag_to_check`. `random_state` and the other `random_*state` scopes take `prioritize = { <state id> ... }`. [docs]
<!-- kit:end id="iterator-options" -->

<!-- kit:begin id="version-added-column" at="section:effect-scopes" -->
**The "Version Added" column.** The column is the wiki's claim. No installed file records when an effect was added (`changelog.txt` only links to the forum), and the documentation names no versions. [vanilla-confirmed 1.19.4.1] `changelog.txt`, `documentation/`. No effect was added or removed in 1.19.4. [docs] `documentation/effects_documentation.md`

- Rows with no usable version: the cell is blank for `random_country_with_original_tag`, `add_state_resistance_compliance_modifier`, `remove_state_resistance_compliance_modifier`, `effect_tooltip` and `promote_officer_to_general`. It says `???` for `add_unit_bonus`, `career_profile_step_missiolini`, `get_highest_scored_country_temp`, `get_sorted_scored_countries_temp`, `get_supply_vehicles` and `get_supply_vehicles_temp`. In the `set_technology` and `create_operative_leader` rows, other wiki text has slipped into the column.
<!-- kit:end id="version-added-column" -->

<!-- kit:begin id="general-corrections" at="section:general" -->
Notes for the "Any scope" effects above.

- The dynamic modifier effects also run in special project scope. `days` may be a variable, and `remove_dynamic_modifier` takes the same optional `scope` key as `add_dynamic_modifier`; it must match the value used when the modifier was added. [docs] `documentation/effects_documentation.md`
- The folder named in the notes of `add_state_resistance_compliance_modifier` and `remove_state_resistance_compliance_modifier` is wrong. The files are `common/resistance_compliance_modifiers/resistance_modifiers.txt` and `common/resistance_compliance_modifiers/compliance_modifiers.txt`. A modifier must carry `is_dynamic = yes` to be added or removed by these effects, and this works only for state resistance and state compliance modifiers. [vanilla-confirmed 1.19.4.1] `common/resistance_compliance_modifiers/resistance_modifiers.txt`
- `custom_override_tooltip` accepts a plain localisation key or a block for `tooltip`; the block holds `localization_key` plus named replacements, as for `custom_effect_tooltip`. [docs]
- `not_tooltip` (in the `custom_override_tooltip` row) is not in the effects documentation, which lists only `tooltip`. The trigger documentation does describe it for the trigger `custom_override_tooltip`. [docs] `documentation/triggers_documentation.md`. No vanilla script uses it. [vanilla-confirmed 1.19.4.1] The string exists once in `hoi4.exe`. The effect form does not accept it: `not_tooltip` inside the effect `custom_override_tooltip` logged "Invalid effect 'not_tooltip'", and the block still ended. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, effect run from the console, error.log read.
<!-- kit:end id="general-corrections" -->

<!-- kit:begin id="border-war-keys" at="section:border-wars" -->
`start_border_war` keys that the row above leaves out. [docs] `documentation/effects_documentation.md`

| Key | Where | Meaning |
| --- | --- | --- |
| `combat_width = <int>` | top level | Combat width of the border war. |
| `minimum_duration_in_days = <int>` | top level | Minimum duration of the fight. |
| `leader_score = { base = <n> modifier = { ... } }` | inside `attacker` | Scores candidate commanders to pick the leader. |

Vanilla sets all three: `minimum_duration_in_days` in 6 files and `leader_score` in 7 files, for example `common/decisions/IRQ.txt`, which also sets `combat_width = 180`. [vanilla-confirmed 1.19.4.1]

```text
start_border_war = {
    change_state_after_war = no
    combat_width = 180
    minimum_duration_in_days = 40
    attacker = {
        state = 676
        num_provinces = 2
        on_win = my_event.1
        on_lose = my_event.2
        on_cancel = my_event.2
        leader_score = {
            base = 1
            modifier = { skill > 2 factor = 5 }
        }
    }
    defender = {
        state = 680
        num_provinces = 2
        on_win = my_event.2
        on_lose = my_event.1
        on_cancel = my_event.2
    }
}
```
<!-- kit:end id="border-war-keys" -->

<!-- kit:begin id="variables-corrections" at="section:variables" -->
`randomize_variable` and `randomize_temp_variable`, which the wiki text does not mention. Scope: any. `randomize_variable` takes the same keys as the temp form. [docs] `documentation/effects_documentation.md`

| Form | Keys |
| --- | --- |
| `randomize_temp_variable = <var>` | Short form: a uniform draw, the same as `distribution = uniform` with `min = 0` and `max = 1`. |
| `distribution = uniform` | `min` and `max`, defaults 0 and 1. |
| `distribution = binomial` | `min` is optional; `max` is required when `min` is given. |
| `distribution = poisson` | `lambda` is required; `min` is optional. |

```text
randomize_temp_variable = {
    var = my_roll
    distribution = binomial
    min = 0
    max = 100
}
```

Vanilla uses the binomial form above in `common/scripted_effects/BUL_scripted_effects.txt`, and `randomize_variable` with `distribution = uniform`, `min = 3000`, `max = 6500` in `common/on_actions/13_goe_on_actions.txt`. [vanilla-confirmed 1.19.4.1] The documentation's comment on the binomial form ("with N=2") is garbled, so the exact meaning of `min` and `max` for `binomial` and `poisson` is not stated. The docs only say that `binomial` needs `max` when `min` is given and that `poisson` needs `lambda`. [docs] `documentation/effects_documentation.md` What the numbers do to the result was run in the game. For `binomial`, `min` and `max` set the range, and the draws are not whole numbers: 200 draws with `min = 0 max = 100` fell between 3.7 and 95.3 with a mean of 52.2, and `min = 0 max = 10` gave 0.29 to 9.51 with a mean of 4.97. With no `min` and no `max` the draws were between 0.001 and 0.998, and the load logged "min (0) is greater or equal to max (0)" but the effect still ran. For `poisson`, `min` is added to the draw as an offset, not used as a floor: `lambda = 10` alone gave whole numbers from 3 to 20 with a mean of 10.1, and `lambda = 10 min = 10` gave 13 to 30 with a mean of 20.1 and none below 10. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, scripted effect run from the console, game.log read. One run of 200 draws per variant, and the shape of the binomial was not analysed beyond min, max and mean.

`career_profile_set_temp_playthrough_variable` and `career_profile_set_temp_variable` in the table above are documented as triggers, not effects. Vanilla uses `career_profile_set_temp_variable` inside the `bronze`, `silver` and `gold` trigger blocks of `common/medals/00_medals.txt` (24 uses) and in the condition blocks of `common/ribbons/00_ribbons.txt` (5 uses). [docs] `documentation/triggers_documentation.md`, [vanilla-confirmed 1.19.4.1] `common/medals/00_medals.txt`
<!-- kit:end id="variables-corrections" -->

<!-- kit:begin id="loop-and-scorer-effects" at="section:arrays" -->
Loop, scorer and variable-dump effects. The full rows are in [Data structures](data_structures.md#arguments) (loops), [Scorers](data_structures.md#scorers) and [Debugging variables](data_structures.md#debugging-variables). Scope and defaults below. All rows: [docs] `documentation/effects_documentation.md`

| Effect | Scope | Keys and defaults |
| --- | --- | --- |
| `for_each_loop` | any | `array`; `value` (temp variable, default `v`); `index` (default `i`); `break` (default `break`). |
| `for_loop_effect` | any | `start` (0), `end` (0), `compare` (default `less_than`), `add` (1), `value` (default `v`), `break`. |
| `while_loop_effect` | any | `limit` (checked before each pass); `break`. |
| `random_scope_in_array` | any | `array`, `limit`, `break`. Runs the effects once, on one random element. |
| `get_highest_scored_country` | COUNTRY | `scorer`; `var` (default `highest_scored_country`). |
| `get_sorted_scored_countries` | COUNTRY | `scorer`; `array` (default `sorted_country_list`); `scores` (default `country_list_scores`). |
| `print_variables` | STATE, COUNTRY, CHARACTER | `file`, `text`, `append`, `print_global`, optional `var_list = { a b c }`. |

- Setting the `break` temp variable to a non-zero value ends the loop. [docs]
- With the default `compare = less_than` the loop stops before `end`; use `compare = less_than_or_equals` to include it. [docs]
- Vanilla uses `for_each_loop` (4 files), `for_loop_effect` (9), `while_loop_effect` (21), `random_scope_in_array` (2), `get_highest_scored_country` (2, with `var = GLOBAL.<name>`) and `print_variables` (1, in `common/scripted_effects/00_scripted_effects.txt`). `get_sorted_scored_countries` is not used in vanilla script. [vanilla-confirmed 1.19.4.1]

```text
for_each_loop = {
    array = SOV.many_weapons_array
    value = weapons_country
    add_equipment_to_stockpile = {
        type = infantry_equipment
        amount = 200
        producer = var:weapons_country
    }
}
```
<!-- kit:end id="loop-and-scorer-effects" -->

<!-- kit:begin id="event-effect-options" at="section:general-1" -->
Keys of `country_event`, `news_event`, `state_event`, `unit_leader_event` and `operative_leader_event`. The rows above show only some of them, and their "inclusive" bounds for `random_hours` and `random_days` are wrong. [docs] `documentation/effects_documentation.md`

| Key | Meaning |
| --- | --- |
| `id` | The event to fire. |
| `hours`, `days`, `months` | Delays that are added together. A month counts as 30 days. `months` is missing from the rows above. |
| `random_hours = N` | Adds a random number of hours from 0 up to but not including N. |
| `random_days = N` | Adds a random number of days from 0 up to one hour less than N. |
| `random = N` | Same as `random_hours`, kept for old scripts. |
| `random = { chance = 50 ... }` | A different use of `random`: a group of child effects that run together with the given percent chance. |
| `tooltip = <loc key>` | Picks the tooltip text for this effect. |

- `random_hours` and `random_days` can be used together; their results are added too. [docs]
- `trigger_for` belongs to `state_event` only: one of `controller`, `owner`, `occupied`, `from`, `prev`, `root` or a tag. `operative_leader_event` also takes `originator`, `recipient`, `set_from`, `set_from_from` and `set_root`. [docs]
- Vanilla uses `months` inside event effects in 7 files (for example `events/AAT_Sweden.txt`) and `random_hours` in 92 files. [vanilla-confirmed 1.19.4.1]

```text
country_event = { id = AAT_Sweden.9 months = 26 random_days = 70 }
```
<!-- kit:end id="event-effect-options" -->

<!-- kit:begin id="country-rule-effects" at="section:general-1" -->
Rule effects, a deprecated one and a stub. Scope for all of them: country. [docs] `documentation/effects_documentation.md`

- `clear_rule = { <rule> = yes }` clears a rule that `set_rule` added; the documentation's example clears `can_not_declare_war = yes`. `set_rule` overrides all other rules on the country and takes a `desc`. [docs]
- Vanilla uses `clear_rule` twice, in `common/ideas/bulgaria.txt`, inside idea blocks next to `country_lock_all_division_template = no`. [vanilla-confirmed 1.19.4.1]
- `set_relation_rule` is marked deprecated in the documentation; use `add_relation_rule_override` and `remove_relation_rule_override` above. No vanilla script uses it. [docs], [vanilla-confirmed 1.19.4.1]
- `ai_message`: the documentation entry is only the text "ai message... ?". No vanilla script uses it and the documentation lists no keys. [docs] `documentation/effects_documentation.md`, [vanilla-confirmed 1.19.4.1] `common/`, `events/`, `history/` `ai_message = yes` is rejected at load with "Non assign effect is not enclosed in {}: ai_message", yet its block still ran to the end. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, effect run from the console, error.log and game.log read.

Corrections to the "Game rule list" in the `set_rule` row:

- `can_use_underway_replenishment` is a valid rule that the list lacks. Vanilla sets it with `set_rule` in `common/special_projects/projects/naval_projects.txt`. [vanilla-confirmed 1.19.4.1]
- `can_join_factions_not_allowed_diplomacy` is only a localisation key (`CAN_JOIN_FACTIONS_NOT_ALLOWED_DIPLOMACY` in `localisation/english/rules_l_english.yml`). The lowercase name is in neither vanilla script nor `hoi4.exe`. [vanilla-confirmed 1.19.4.1] for the localisation key and the script search, [unverified] for the absence from `hoi4.exe`. It is not a rule you can set: the game reported it at load as "unknown rule 'can_join_factions_not_allowed_diplomacy'", `has_rule` on it failed to validate, and `set_rule` left nothing set. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, scripted effect, error.log and game.log read.
- Of the 27 listed names, 23 occur in vanilla script. The four that do not are `can_declare_war_without_wargoal_when_in_war`, `can_join_factions_not_allowed_diplomacy`, `can_not_build_buildings` and `can_occupy_non_war`; all but `can_join_factions_not_allowed_diplomacy` occur once each as strings in `hoi4.exe`. [vanilla-confirmed 1.19.4.1] for the counts (scan of `common/`, `events/`, `history/`), [unverified] for the `hoi4.exe` strings. Three of the four names work with `set_rule`: for `can_not_build_buildings`, `can_occupy_non_war` and `can_declare_war_without_wargoal_when_in_war`, `has_rule` read TRUE after the set and FALSE after `= no`. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, scripted effect and game.log read. `can_occupy_non_war` was already TRUE for the test country before the set, so only its FALSE after the reset shows the effect.
- The documentation for `add_relation_rule_override` spells a supported rule `can_send_volunteer`; vanilla uses `can_send_volunteers`, as the row above says. [vanilla-confirmed 1.19.4.1] `common/decisions/AUS.txt`
- The documentation example for `set_party_rule` spells the party selector `ideologly`, while the row above says `ideology`. No vanilla script uses `set_party_rule`. [docs] `documentation/effects_documentation.md`, [vanilla-confirmed 1.19.4.1] `common/`, `events/`, `history/`. The engine accepts `ideology` and not `ideologly`. Do not copy the documentation example: `set_party_rule` with the `ideologly` spelling was reported at load as "unknown rule 'ideologly'", and running the effect crashed the game with an access violation (EXCEPTION_ACCESS_VIOLATION, one second after the last game.log line). `set_party_rule = { ideology = democratic ... }` worked: `has_rule = can_not_declare_war` read FALSE before, TRUE after the set and FALSE after the reset. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, scripted effect, error.log, game.log and the crash folder read. The crash is placed by the last game.log line and the time gap, and the stack trace has no names. No run isolated the missing selector key as the cause, though the correct spelling worked.
<!-- kit:end id="country-rule-effects" -->

<!-- kit:begin id="mana-scaled-political-power" at="section:mana" -->
`add_scaled_political_power` (scope: country). The documentation says it adds political power scaled by the difference in industrial capacity between the receiver and another country. It lists no keys, no vanilla script uses it, and the string exists once in `hoi4.exe`, so the argument layout is unknown. [docs] `documentation/effects_documentation.md`, [vanilla-confirmed 1.19.4.1] no vanilla use, [unverified] for the argument layout. `add_scaled_political_power = yes` loaded without an error, ran, and logged "CAddScaledPoliticalPowerEffect AddPoliticalpower 0", so it added 0. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, effect run from the console, error.log read.
<!-- kit:end id="mana-scaled-political-power" -->

<!-- kit:begin id="release-effects-wording" at="section:diplomacy" -->
The documentation describes `release` and `release_on_controlled` as releasing the country "as a puppet". The effect tooltips say otherwise: `EFFECT_RELEASE_NATION` reads `Release $COUNTRY|Y$.`, `EFFECT_RELEASE_PUPPET` reads `Release $COUNTRY|Y$ as puppet.` and `EFFECT_RELEASE_AUTONOMY` reads `Release $COUNTRY|Y$ as $NAME|H$.` So `release` frees a nation, while `release_puppet` and `release_autonomy` create subjects, as the rows above say. [vanilla-confirmed 1.19.3] `localisation/english/effects_l_english.yml`, [docs] `documentation/effects_documentation.md`
<!-- kit:end id="release-effects-wording" -->

<!-- kit:begin id="autonomy-defaults" at="section:autonomy" -->
`set_autonomy`, `puppet` and `release_autonomy`.

- The documentation names the key `autonomy_state` and gives `end_wars` and `end_civil_wars` a default of `yes`. The `set_autonomy` row says `autonomous_state` and says `end_wars` defaults to no. [docs] `documentation/effects_documentation.md`
- Vanilla accepts both key names. Within a few lines of `set_autonomy = {` it writes `autonomy_state` on 522 lines and `autonomous_state` on 83 (for example `common/decisions/JAP.txt`). Prefer `autonomy_state`. [vanilla-confirmed 1.19.4.1]
- `keep_subjects` is not in the documentation; vanilla uses it twice in `common/national_focus/australia_taog.txt`. [vanilla-confirmed 1.19.4.1]
- `release_autonomy` has two more keys, both default `no`: `release_non_owned_controlled = yes` also releases states you only control, and `force_change_controller_for_non_ally_controlled = yes` changes the controller of states that neither you nor your allies control. [docs]
- Vanilla uses the first key in 3 files and the second once (`common/national_focus/indonesia.txt`). [vanilla-confirmed 1.19.4.1]
- The `puppet` row writes the folder as `commmon/autonomous_states/`; it is `common/autonomous_states/`. [vanilla-confirmed 1.19.4.1]
<!-- kit:end id="autonomy-defaults" -->

<!-- kit:begin id="war-keys" at="section:war" -->
Keys the documentation lists that the rows in this section lack. [docs] `documentation/effects_documentation.md`

- `add_to_war` takes `single_target_only = yes`: join only against the given `enemy` instead of against every enemy of `targeted_alliance`. Vanilla uses it in 3 files (`common/decisions/SOV.txt`). [docs], [vanilla-confirmed 1.19.4.1]
- `launch_nuke` takes `province`. The documentation's own example misspells it as `provinve`; do not copy that. [docs]
<!-- kit:end id="war-keys" -->

<!-- kit:begin id="resource-days-key" at="section:resources" -->
`add_resource` also takes `days = <int>` in the documentation: the resource is added or removed temporarily. No vanilla script passes `days`. [docs] `documentation/effects_documentation.md`, [vanilla-confirmed 1.19.4.1]
<!-- kit:end id="resource-days-key" -->

<!-- kit:begin id="targeted-decision-correction" at="section:decisions" -->
The note on `activate_targeted_decision` ("Only works on missions; regular decisions targeted this way become visible but do not activate") does not match 1.19.3. The documentation says the effect activates targeted decisions "or mission", ignoring the normal trigger conditions, the cooldown and fire-only-once, and that it cannot activate one that is already active in the interface. Its `target` may be a country tag or a state. [docs] `documentation/effects_documentation.md`

Vanilla passes 63 distinct decisions to the effect, and 44 of them have no `days_mission_timeout`, so they are not missions. One example is `BUL_aircraft_agreements` in `common/decisions/BUL.txt`, which has `allowed = { always = no }` with the comment "Activated from effect". [vanilla-confirmed 1.19.4.1]

The `unlock_decision_category_tooltip` row names the folder `common/decisions/catergories/`. The folder is `common/decisions/categories/`. [vanilla-confirmed 1.19.4.1]
<!-- kit:end id="targeted-decision-correction" -->

<!-- kit:begin id="swap-ideas-keys" at="section:ideas" -->
`swap_ideas` also takes `days = <n>` (the duration of the new idea) and `add_days = <n>` (added to or subtracted from the duration). The documentation's syntax line calls the effect `swap_idea`; the name is `swap_ideas`. No vanilla script uses either key. [docs] `documentation/effects_documentation.md`, [vanilla-confirmed 1.19.4.1]
<!-- kit:end id="swap-ideas-keys" -->

<!-- kit:begin id="equipment-license-key" at="section:equipment" -->
`create_production_license` takes `version_name = "<name>"` inside `equipment` to pick a variant by name. `new_prioritised` (default yes) ignores `version` but not `version_name`. If nothing matches, no license is created. Vanilla uses `version_name` in 3 `create_production_license` blocks, in `common/national_focus/siam.txt` and `common/on_actions/07_nsb_on_actions.txt`. [docs] `documentation/effects_documentation.md`, [vanilla-confirmed 1.19.4.1]
<!-- kit:end id="equipment-license-key" -->

<!-- kit:begin id="navy-transfer-key" at="section:military" -->
`transfer_navy` has an optional `is_government_in_exile = yes` (default no): the navy is then tagged as exile and goes back to its owner if the owner returns from exile. The effect does not support carriers. [docs] `documentation/effects_documentation.md`

Vanilla uses the key in 3 files, for example `common/decisions/_exiled_governments_decisions.txt`. [vanilla-confirmed 1.19.4.1]
<!-- kit:end id="navy-transfer-key" -->

<!-- kit:begin id="create-leader-keys" at="section:unit-leaders" -->
Keys of `create_corps_commander`, `create_field_marshal` and `create_navy_leader`.

- The documentation entries are one-line stubs and do not call the effects deprecated, and vanilla script still uses them (33, 4 and 3 blocks in 14, 1 and 3 files). The "Deprecated" note in the `create_corps_commander` row comes from the wiki. [docs] `documentation/effects_documentation.md`, [vanilla-confirmed 1.19.4.1]
- Vanilla gives the portrait as `gfx = GFX_...` (24 blocks) or `portrait_path = "..."` (7 blocks), never as `picture`. [vanilla-confirmed 1.19.4.1]
- The numeric leader id is written `id = <n>` in vanilla (9 `create_corps_commander` blocks, for example `id = 600` in `common/national_focus/china_shared.txt`), not `legacy_id`. `legacy_id` is not used in the vanilla blocks of these three effects (it appears in character definitions and `add_*_role` blocks) and occurs once as a string in `hoi4.exe`. `remove_unit_leader = <id>` takes that id. [vanilla-confirmed 1.19.4.1], [docs]
<!-- kit:end id="create-leader-keys" -->

<!-- kit:begin id="unit-leader-captivity" at="section:unit-leaders" -->
`release_captured_generals_from` (scope: country). Makes the scoped country release the generals it holds from the given country; `province` limits it to generals held in that province, otherwise all are released. [docs] `documentation/effects_documentation.md`

```text
release_captured_generals_from = FROM
release_captured_generals_from = { target = GER province = 1234 }
```

Vanilla runs `FROM = { release_captured_generals_from = ROOT }` in the outcome blocks of a rescue operation in `common/operations/00_operations.txt`. [vanilla-confirmed 1.19.3] Its tooltip is `EFFECT_RELEASE_GENERALS` ("Release all captured Commanders from ..."); the tooltip of `release_from_captivity` is `EFFECT_RELEASE_FROM_CAPTIVITY` ("Is released from captivity"). [vanilla-confirmed 1.19.3] `localisation/english/effects_l_english.yml` Related triggers: `has_any_captured_general`, `has_any_general_captured_by`, `is_general_captured`. [docs] `documentation/triggers_documentation.md`
<!-- kit:end id="unit-leader-captivity" -->

<!-- kit:begin id="history-only-claim" at="section:history" -->
"Only within history files" is documented for the order of battle effects: `set_oob`, `set_air_oob`, `set_naval_oob` and `set_keyed_oob` are "only intended to be used within history files". The documentation does not say this for `recruit_character` (it says "must be in country scope") or `generate_character` (its example runs inside `every_country`). [docs] `documentation/effects_documentation.md`

Vanilla uses `recruit_character` in 257 history files and `generate_character` only in 3 files under `history/general/`; no vanilla file uses `set_keyed_oob`. [vanilla-confirmed 1.19.4.1]
<!-- kit:end id="history-only-claim" -->

<!-- kit:begin id="state-event-and-locations" at="section:general-2" -->
`state_event` and strategic locations.

- `state_event` supports `trigger_for` (see the `event-effect-options` block above), which the parameter list lacks although the example uses it. Vanilla uses `trigger_for = controller` on all 10 lines that use the key, for example in `events/USA.txt`. [docs], [vanilla-confirmed 1.19.4.1]
- The strategic location effects are `strategic_province_location` and `strategic_state_location`. The pair inside is `<location id> = <province id>`; the location ids are defined in `common/strategic_locations/strategic_locations.txt`. [docs] `documentation/effects_documentation.md`
- Vanilla puts both effects inside the `history = { }` block of a state file (11 and 8 files), for example `history/states/116-Malta.txt`: `strategic_province_location = { defensible_coastline = 12003 }`. [vanilla-confirmed 1.19.4.1]
- `common/strategic_locations/documentation.md` names the effect `strategic_location_building` and shows a `strategic_location` block; the effects documentation's example also writes `strategic_location`. Neither is the effect name vanilla uses. [docs], [vanilla-confirmed 1.19.4.1]
<!-- kit:end id="state-event-and-locations" -->

<!-- kit:begin id="building-tags" at="section:buildings-1" -->
The `remove_building` row uses `tag`; the documentation uses `tags = <tag>` or `tags = { <tag> ... }`, as the `damage_building` row does. The row also omits `state` and `province`. Both take a number or a variable. Without them the effect runs only in state scope and only finds state buildings; it does not search the state's provinces for province buildings. [docs] `documentation/effects_documentation.md`

For `damage_building` with only a `state` given, all provinces of that state are searched for the first matching province building. [docs]

No vanilla script uses `tag` or `tags` with `remove_building`. It uses `province` in 3 files, for example `common/national_focus/germany.txt`. [vanilla-confirmed 1.19.4.1]
<!-- kit:end id="building-tags" -->

<!-- kit:begin id="character-portrait-groups" at="section:general-3" -->
The `set_portraits` row labels its keys "Army scope" and "Character scope". The keys are portrait groups, each holding `small` and `large`, in the same shape as `portraits = { }` in a character file; the documentation's example uses `army` and `civilian`. `character = <token>` is only needed outside character scope. [docs] `documentation/effects_documentation.md`

Of 53 vanilla `set_portraits` blocks in 23 files, 36 use `civilian`, 27 use `army` and none uses `navy`, although vanilla character files use `navy` in 13 files. Whether `set_portraits` accepts `navy` is not documented. [vanilla-confirmed 1.19.4.1] `common/decisions/JAP.txt`, [unverified] for whether `navy` is accepted.

```text
JAP_kozo_sasaki = {
    set_portraits = {
        civilian = { small = GFX_portrait_JAP_kozo_sasaki_imprisoned }
    }
}
```
<!-- kit:end id="character-portrait-groups" -->

<!-- kit:begin id="character-leader-edits" at="section:unit-leaders-1" -->
Captivity and cosmetic effects for the unit leader in scope.

| Effect | Scope | Use |
| --- | --- | --- |
| `capture_by` | unit leader (must be a general) | `capture_by = GER` or `capture_by = { country = GER province = 1234 }`; `province` is where the leader is held. |
| `release_from_captivity` | CHARACTER | `release_from_captivity = yes`; no effect if the leader is not captured. |
| `set_leader_name` | CHARACTER | `set_leader_name = "Name"`; no tooltip. |
| `set_leader_description` | CHARACTER | `set_leader_description = "DESC_KEY"`; no tooltip. |
| `set_leader_portrait` | CHARACTER | `set_leader_portrait = "GFX_..."`; no tooltip. |

All rows: [docs] `documentation/effects_documentation.md`.

- Vanilla uses `capture_by` in `common/on_actions/00_on_actions.txt` (`on_deployed_leader_defeated`, guarded by `can_be_captured = yes`, with `capture_by = FROM`) and in `common/decisions/_debug_decisions.txt`. It runs `var:target_leader = { release_from_captivity = yes }` in `victim_effects` of `common/raids/land_infiltration_raids.txt`. [vanilla-confirmed 1.19.4.1]
- No vanilla script uses the three `set_leader_*` effects. [vanilla-confirmed 1.19.4.1]
- The `set_leader_*` names look like the older unit leader versions of `set_character_name` and `set_portraits`; whether they still work on recruited characters is not documented. [unverified]
- `replace_unit_leader_trait`: its documentation entry says only "add trait to unit leader" and no vanilla script uses it, so the keys `trait` and `replace` and the "extremely buggy" warning in its row are unverified. [unverified] `replace_unit_leader_trait = { trait = brilliant_strategist replace = yes }` logged "Invalid trait: yes" at load, and running it on a random GER army leader crashed the game (EXCEPTION_ACCESS_VIOLATION). So `replace` is read as a trait name and `yes` is not one. The crash came from the whole call, and the call was not seen to finish, so the `replace` key may not be its only cause. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, effect run from the console, crash folder.
- The documentation's example for `remove_unit_leader_role` names `remove_corps_commander_role`, which is not an effect. The effect is `remove_unit_leader_role = yes` and removes every unit leader role. [docs]
<!-- kit:end id="character-leader-edits" -->

<!-- kit:begin id="combat-corrections" at="section:combat" -->
`add_temporary_buff_to_units` is not an effect in 1.19.4.1. It is absent from `documentation/effects_documentation.md`, from all vanilla script and from the strings of `hoi4.exe`; so are its keys `combat_offense` and `combat_breakthrough`. Several other keys in its row (`org_damage_multiplier`, `str_damage_multiplier`, `war_support_reduction_on_damage`) are modifier names. Do not use the row or its example; `add_timed_unit_leader_trait` above is the documented way to give a leader a time-limited bonus. [docs] `documentation/effects_documentation.md`, `documentation/modifiers_documentation.md`, [vanilla-confirmed 1.19.4.1] `common/`, `events/`, `history/`. The engine rejects the effect: `add_temporary_buff_to_units = { combat_offense = 0.1 }` logged "Invalid effect 'add_temporary_buff_to_units'" and "Unknown effect-type" at load, and the surrounding block still ended. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, effect run from the console, error.log read.

`boost_planning` (scope: CHARACTER). The documentation says it boosts the planning of the units that belong to the army group or navy of the unit leader. It lists no keys, and no vanilla script uses it. [docs] `documentation/effects_documentation.md`, [vanilla-confirmed 1.19.4.1] no vanilla use, [unverified] for the argument layout. `every_army_leader = { boost_planning = yes }` produced no error. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, effect run from the console, error.log read.
<!-- kit:end id="combat-corrections" -->

<!-- kit:begin id="division-scope-notes" at="section:division-scope" -->
Division scope effects. All statements are [docs] `documentation/effects_documentation.md` unless marked.

- `change_division_template` is documented as `change_division_template = "My Template Name"`. Vanilla uses only the block form of the example above, `change_division_template = { division_template = "..." }`, in 4 files, for example `common/national_focus/sweden.txt`. [vanilla-confirmed 1.19.4.1]
- `set_unit_organization = <0 to 1>` is described as "set unit organization to current * value". Vanilla runs it on enemy divisions with `0.50` in `common/scripted_effects/00_scripted_effects.txt` (`SF_PARA_combat_effect`). [vanilla-confirmed 1.19.4.1]
- `promote_officer_to_general = yes`: the value is ignored. No vanilla script uses it.
- `reseed_division_commander` is marked as a debug and testing effect, and `add_random_valid_trait_from_unit` works only when the division scope is the root scope. No vanilla script uses either.
- `destroy_unit = yes` is used in the `division_effects` of raid outcomes (10 uses in 2 files, `common/raids/land_infiltration_custom.txt` and `common/raids/naval_commando_raids.txt`). [vanilla-confirmed 1.19.4.1]
<!-- kit:end id="division-scope-notes" -->

<!-- kit:begin id="mio-scope-notes" at="section:mio-scope" -->
The "Examples" cell of `set_mio_funds_gain_factor` reads `set_mio_funds = 0.1`. The effect is `set_mio_funds_gain_factor`; like the other MIO effects it takes a number or a variable, and the value cannot be negative. [docs] `documentation/effects_documentation.md`

```text
mio:my_mio = {
    set_mio_funds_gain_factor = 0.9
    set_mio_funds_gain_factor = var:my_number_var
}
```
<!-- kit:end id="mio-scope-notes" -->

<!-- kit:begin id="raid-scope-notes" at="section:raid-scope" -->
The first parameter row of `raid_damage_units` (`<flag>`, "to identify the project flag") is a copy error from the special project flag effects. The effect takes only `damage`, `org_damage`, `str_damage`, `plane_loss` and `ratio`, as the example shows. [docs] `documentation/effects_documentation.md`

Where raid scope comes from. Each outcome of a raid (`failure`, `limited_success`, `success`, `critical_success`) has `actor_effects` and `victim_effects`, both in raid instance scope, and `division_effects` in division scope. [docs] `common/raids/_documentation.md`

- Raid instance scope has the dynamic variables `var:actor_country`, `var:victim_country`, `var:target_state` and `var:target_province`; use them to change scope, for example `var:target_state = { damage_building = { type = dam damage = 1 province = var:ROOT.target_province } }`. [docs] `common/raids/_documentation.md`
- Vanilla also changes scope with `var:target_leader` in `victim_effects` of `common/raids/land_infiltration_raids.txt`. [vanilla-confirmed 1.19.4.1]
<!-- kit:end id="raid-scope-notes" -->

<!-- kit:begin id="special-project-corrections" at="section:special-project-scope" -->
- The `modify_project_flag` example is written `modify_mproject_flag`, which is not an effect. Use `modify_project_flag = { flag = my_flag value = 3 }`. The documentation's own example calls it `modify_facility_flag`, which is a copy error as well. [docs] `documentation/effects_documentation.md`
- `modify_mproject_flag` is absent from the documentation, from vanilla script and from `hoi4.exe`. [vanilla-confirmed 1.19.4.1]
- `prototyp_reward_option` in `complete_prototype_reward_option` is not a typo on the wiki. The documentation spells the key this way, and the string exists in `hoi4.exe`. Keep the spelling. [docs] `documentation/effects_documentation.md`
- No vanilla script uses `complete_prototype_reward_option`. [vanilla-confirmed 1.19.4.1] `common/special_projects/prototype_rewards/`
- `raid_reduce_project_progress_ratio` (State scope, "Raids" section above) runs with a raid instance as root. [docs]
<!-- kit:end id="special-project-corrections" -->

<!-- kit:begin id="region-efficiency" at="section:other-scopes" -->
`add_region_efficiency` is the only effect the documentation lists for strategic region scope. Run in a country scope it logged "add_region_efficiency: Invalid Scope, supported: StrategicRegion, provided: Country". [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, `add_region_efficiency = 1` run from the console, error.log read. The text reads "add efficiency factor to strategic region for from country". It gives no keys, no vanilla script uses it, and the documentation does not say how to enter strategic region scope. [docs] `documentation/effects_documentation.md`, [vanilla-confirmed 1.19.4.1] no vanilla use, [unverified] for the argument layout.
<!-- kit:end id="region-efficiency" -->

<!-- kit:begin id="random-list-options" at="section:random-effects" -->
Two keys of `random_list` that the text above omits. [docs] `documentation/effects_documentation.md`

- `log = yes` writes the dice roll to `game.log`.
- `seed = <variable|constant|random>` makes the list pick with that seed instead of the scope's seed.

```text
random_list = {
    seed = random
    10 = { add_political_power = 10 }
    my_variable = { add_political_power = 100 }
}
```

Vanilla has 43 `seed =` lines across 12 files (47 in 15 when commented-out lines count) and uses `log = yes` inside `random_list` in 3 files. [vanilla-confirmed 1.19.4.1] `common/decisions/CHI_decisions.txt`. Using `seed = random` to get a fresh result on repeated runs is not a documented guarantee, but it held in a test. Ten separate console runs of a two-way `random_list` with `seed = random` gave 4 of one result and 6 of the other, and a loop of 30 draws gave 15 and 15. A constant `seed = 7` gave the same result in six separate runs and in all 30 loop draws. Six separate runs with no `seed` all gave the same result, which fits a seed fixed per game hour but was not shown to be one. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, effect run from the console, game.log read. The case after the game date moves on was not tested.

`fixed_random_seed` is not in any game documentation file. Vanilla script uses it only under `common/decisions/` (13 files), which fits the statement above that it is for decisions. [vanilla-confirmed 1.19.4.1] `common/decisions/BUL.txt`
<!-- kit:end id="random-list-options" -->

<!-- kit:begin id="meta-effect-notes" at="section:meta-effects" -->
`meta_effect` replaces each `[NAME]` in `text` with the key of the same name in the block. The values can be literals or localisation expressions. `debug = yes` shows what the game actually executes. [docs] `documentation/effects_documentation.md`

```text
meta_effect = {
    text = {
        add_ideas = CZE_skoda_tanks_focus_optimization_[SKODA_OPT]_idea
    }
    SKODA_OPT = "[?skoda_optimization_tier]"
}
```

- Vanilla builds idea names like this in `common/scripted_effects/CZE_scripted_effects.txt`, with the bare `[?variable]` form and no `|.0` suffix; the matching ideas are named `..._1_idea` and so on. `meta_effect` appears in 2 vanilla files. [vanilla-confirmed 1.19.4.1]
- The wiki's `|.0` suffix (above) is not needed to keep decimals. `meta_effect` substitutes `[?var]` as the plain number (2.5 stays 2.5 and 2 stays 2, with no padded zeros), and `[?var|.0]` gives a whole number (2.5 became 2). A `[A]` key was replaced inside quotes too. `debug = yes` prints each built effect to `game.log` as `meta_effect<file>:<line>: meta_effect` followed by the effect text. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, scripted effect run from the console, game.log read. Only 2.5 and 2 were tested, so it is not known whether `|.0` truncates or rounds half down.
<!-- kit:end id="meta-effect-notes" -->

<!-- kit:begin id="scripted-effect-console" at="section:scripted-effects" -->
Custom console commands. The `effect` console command is described on [Console commands](console_commands.md).

- Vanilla ships `common/scripted_effects/zz_debug_effects.txt`, which defines `d_` effects such as `d_add_tech`, `d_retire_country_leader` and `d_collaboration`. [vanilla-confirmed 1.19.3]
- The same file reads command arguments from the `args` array with a fallback value: `args^0?0.1` is the first argument, or 0.1 when none is given. [vanilla-confirmed 1.19.3] `common/scripted_effects/zz_debug_effects.txt`
<!-- kit:end id="scripted-effect-console" -->

<!-- kit:begin id="scripted-effect-corrections" at="section:useful-scripted-effects" -->
Notes on the scripted effects above. They are defined in `common/scripted_effects/00_scripted_effects.txt`, except `lerp`. [vanilla-confirmed 1.19.4.1]

- `lerp` is defined in `common/scripted_effects/SWE_scripted_effects.txt`, a Sweden file, not in the generic base file. It reads `lerp_a`, `lerp_b` and `lerp_x` from variables of any kind (vanilla sets `lerp_x` as a temp variable and the other two with `set_variable`) and writes the regular variable `lerp_result` in the calling scope. [vanilla-confirmed 1.19.3]
- Prefer the native `lerp` math function, `{ value = 10 lerp = { to = 20 alpha = 0.5 } }`, which clamps `alpha` between 0 and 1. [docs] `documentation/script_math_functions.md`
- `add_potential_special_forces_tree` raises the variable `sf_trees` (it starts at 2 when unset); `remove_potential_special_forces_tree` lowers it. [vanilla-confirmed 1.19.4.1]
- `remove_any_country_role_from_character` removes the advisor roles in the slots it lists: `air_chief`, `army_chief`, `navy_chief`, `high_command`, `theorist` and `political_advisor`. [vanilla-confirmed 1.19.4.1]
- `add_ruling_to_fas`, `add_ruling_to_com` and `add_ruling_to_neu` exist next to `add_ruling_to_dem`. [vanilla-confirmed 1.19.4.1]
<!-- kit:end id="scripted-effect-corrections" -->
