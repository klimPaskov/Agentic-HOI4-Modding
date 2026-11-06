# Triggers

<!-- kit:begin id="review" build="1.19.4.1" checked="2026-11-01" revision="105091" sources="documentation/triggers_documentation.md documentation/script_math_functions.md common/collections/ common/scripted_triggers/ common/factions/goals/ common/medals/ common/ribbons/ common/on_actions/ common/raids/ common/operations/ common/unit_leader/ common/combat_tactics.txt common/decisions/ common/national_focus/ common/equipment_groups/ common/military_industrial_organization/ common/special_projects/ common/technologies/ common/ai_strategy/ common/scripted_effects/ events/ localisation/english/ hoi4.exe" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Checked against `documentation/triggers_documentation.md` (all 596 triggers: scope lists, parameter keys, stated notes), the collection, scripted trigger, faction goal, medal, ribbon, on action, raid, operation and unit leader files under `common/`, and text searches of vanilla script and `hoi4.exe`.
- Kit blocks added (30): `coverage`, `comparison-notes`, `scope-row-corrections`, `scope-iterator-additions`, `collection-triggers`, `scope-keyword-notes`, `flow-control-notes`, `any-scope-general`, `career-profile-notes`, `variable-array-triggers`, `country-general-notes`, `country-trigger-additions`, `ideas-keys`, `military-notes`, `intelligence-keys`, `peace-conference-corrections`, `state-scope-corrections`, `character-trigger-additions`, `advisor-warning`, `unit-leader-notes`, `scientist-names`, `combat-notes`, `division-scope-notes`, `mio-scope-notes`, `contract-name`, `other-scopes`, `meta-trigger-notes`, `diplomacy-scripted-trigger-notes`, `resistance-trigger-notes`, `useful-scripted-triggers-check`.
- Wrong or stale wiki text found: the "last updated in 1.17.0" statement; `all_purchase_contract` (engine name `all_purchase_contracts`); swapped `all_core_state` and `any_core_state` descriptions; `pc_is_untouched_loser` and `pc_is_liberated_by` (not in 1.19.3); `ships_in_area` and `skill_advantage` under the wrong scope; `limit` instead of `level` in `any_province_building_level`; `frits` for `first` in `career_profile_check_playthrough_ratio`; the `has_mines` example; `is_mio_available` description and `token` keys in the MIO examples; `common/equipment_groups.txt` (now a folder); `tag` in the state-scope resistance example; `owner` and `controller` marked unusable as targets; `pc_is_state_claimed` parameter; `is_scientist_active` and `deal_completition` spellings.
- Example keys the inventory flagged: `achievement`, `mod`, `ai_area`, `check_mio_parent_completed`, `goal`, `not_tooltip` and `var_list` are in the documentation; `medal` and `ribbon` are unused in vanilla script (their example ids are real); `EQUIPMENT_ARCHETYPE` is a meta trigger placeholder; `state_is_in_area` is an example name vanilla does not define; `should_initiate_resistance_123_321` follows the vanilla naming pattern.
- Gaps left: parameters were compared only where the documentation or vanilla script states them. The "must use > or <" operator notes, the Dual scopes table (covered on Scopes) were not re-checked. The "Version Added" column was checked on 2026-11-01 as far as the installed files allow (see the note under Trigger scopes). Engine behaviour was not run, so inclusive comparisons beyond `collection_size` stay unverified.
**1.19.4.1 re-check (2026-11-01).** 43 statements depended on vanilla scans or files that the update changed, and all 43 were re-measured on the installed files. Numbers moved: `any_other_country_with_original_tag_of` is used in 17 files (was 1), `any_collection_element` in 180 blocks (was 45), `owner = {` 1086 times (was 1001), `custom_trigger_tooltip` 1818 times (was 1782), `controls_or_subject_of` 436 times (was 76), `has_navy_size` 226 blocks (was 221), `any_province_building_level` 141 blocks (was 140), and vanilla defines 24 of the 43 listed diplomacy enable triggers (was 23). Vanilla now has two `meta_trigger` blocks, and the MIO trait note is corrected because vanilla does use `has_mio_trait` and `is_mio_trait_completed` with a bare token. Every other statement cites files that are byte-identical in 1.19.4.1 (Steam depot manifest diff).
<!-- kit:end id="review" -->

<!-- kit:begin id="coverage" at="top" -->
How this page lines up with `documentation/triggers_documentation.md` of build 1.19.3.0.

- The file documents 596 triggers under 13 scope headings: ACE, CHARACTER, COMBATANT, COUNTRY, FACTION, INDUSTRIAL_ORG, OPERATION, PURCHASE_CONTRACT, RAID_INSTANCE, SPECIAL_PROJECT, STATE, STRATEGIC_REGION and any. There is no DIVISION heading, and the division triggers show an empty scope list. [docs] `documentation/triggers_documentation.md`
- The wiki text above says the file was last updated in 1.17.0 (as of 1.17.1.1). That is stale: the wiki tables never named 56 of the 596 triggers. They are described on this page: the iterator and collection triggers under "Trigger scopes"; the temp-variable, array, loop and expression triggers under "Variables"; `career_profile_set_temp_variable`, `career_profile_set_temp_playthrough_variable` and `num_of_career_profile_points` under "Career profile"; `scope_exists` under "General" (any scope); ten country triggers under "General" of the country scope; four character triggers under "General" of the character scope; `has_cavalry_ratio` and `province_vp` under "Combat"; `is_operation_type` under "Special projects". [docs] `documentation/triggers_documentation.md`
- `all_purchase_contract`, `pc_is_untouched_loser` and `pc_is_liberated_by` are not documented triggers in 1.19.3 (corrections under "Trigger scopes" and "Peace conferences"). [docs] `documentation/triggers_documentation.md`
- The rows under "Useful scripted triggers" are scripted triggers defined in vanilla script, not engine triggers. [vanilla-confirmed 1.19.4.1] `common/scripted_triggers/00_scripted_triggers.txt`
- The only trigger the documentation marks deprecated is `has_unit_leader_flag`; it still works in vanilla (see "Unit leaders"). [docs] `documentation/triggers_documentation.md`
<!-- kit:end id="coverage" -->

<!-- kit:begin id="comparison-notes" at="section:operators" -->
Which comparisons the 1.19.3 documentation spells out.

- `collection_size` is documented as inclusive: `value > X` actually means `value >= X`, and `<` is inclusive in the same way. The documentation gives this warning for no other trigger. [docs] `documentation/triggers_documentation.md`
- `any_collection_element` takes an optional `count`, documented as "equal or larger", so `count = 3` passes when at least 3 elements pass. [docs] `documentation/triggers_documentation.md`
- Where the documentation gives worked examples for other triggers they read as strict: for `has_navy_size` it comments `size > 10` as "more than 10" and `size > 39` as "40 or more". [docs] `documentation/triggers_documentation.md`
- Vanilla writes `collection_size` bounds the way a strict comparison would be written, for example `value < 1` and `value > 19` in `common/factions/goals/faction_goals_short_term.txt` and `common/decisions/USA.txt`. [vanilla-confirmed 1.19.4.1] Under the documented inclusive rule these would mean "at most 1" and "at least 19". [docs] `documentation/triggers_documentation.md` The engine reads these comparisons strictly (see the last note).
- The engine does not apply the inclusive rule. With a collection of exactly 3 items, `value > 3` and `value < 3` were false and `value = 3`, `value > 2` and `value < 4` were true. So `value > 0` means at least one, as vanilla writes it. The same strict reading held for `count_in_collection` and `has_resources_in_collection`. Details are under [Comparison notes](collection_modding.md#comparison-notes). [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, eval_effect log scan.
<!-- kit:end id="comparison-notes" -->

<!-- kit:begin id="scope-row-corrections" at="section:trigger-scopes" -->
Rows in the table above that differ from the 1.19.3 documentation.

- `all_purchase_contract` is not the engine name. The documentation has `all_purchase_contracts` (plural) and `any_purchase_contract` (singular). [docs] `documentation/triggers_documentation.md`
- The descriptions of `all_core_state` and `any_core_state` are swapped: `all_core_state` needs every core state of the country to pass, `any_core_state` needs at least one. [docs] `documentation/triggers_documentation.md`
- `all_scientists` is the name; the example `all_scientistst` in that row is a typo. `all_active_scientist` is the documented heading, although the documentation's own example writes `all_active_scientists`. [docs] `documentation/triggers_documentation.md` Both spellings occur as strings in `hoi4.exe`. The plural form `all_active_scientists` is not a trigger in 1.19.4.1: it logged "Invalid trigger 'all_active_scientists'" and "Unknown trigger-type" at load. A scripted trigger whose only content was that unknown trigger still evaluated TRUE. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, scripted trigger run from the console, error.log read.
- `all_other_country` and `any_other_country` are documented with scope `any`, not "country scope only", and both skip the current country. [docs] `documentation/triggers_documentation.md`
- The all_*/any_* iterators accept `tooltip = <loc key>` to override the title. The unit leader, army leader, navy leader and MIO iterators also take `include_invisible = yes` (default no). [docs] `documentation/triggers_documentation.md` Vanilla uses `include_invisible` once, in `common/national_focus/finland.txt`. [vanilla-confirmed 1.19.4.1]
- `any_state_in` takes exactly one of `array`, `continent`, `ai_area` (the id of an AI area) or `strategic_region`, and an optional `tooltip`. The documentation says there is no default tooltip for `array` and `ai_area`, so add `tooltip` for those; its own example misspells `continent` as `conteinent`. [docs] `documentation/triggers_documentation.md` Vanilla has 17 blocks: `strategic_region` in 12, `array` in 5, with `tooltip` in 3. [vanilla-confirmed 1.19.4.1] `common/decisions/INS.txt`
<!-- kit:end id="scope-row-corrections" -->

<!-- kit:begin id="scope-iterator-additions" at="section:trigger-scopes" -->
Scope iterators the table does not list. All rows: [docs] `documentation/triggers_documentation.md`

| Name | Scope | Form |
| --- | --- | --- |
| `any_other_country_of` | any | Like `any_country_of`, but the current country is skipped. |
| `any_country_with_original_tag_of` | any | `{ target = { SWE NOR FIN DEN ICE } <triggers> }` or `target = constant:country_groups:nordics`. True when a country whose original tag is in the list passes. `tooltip` is optional. |
| `any_other_country_with_original_tag_of` | any | The same, skipping the current country. The documentation's example for it names `any_country_with_original_tag_of`, a copy error. |
| `all_claimant` | STATE | `{ tooltip = my_loc <triggers> }`. Every country that claims the state in scope must pass; the triggers run in country scope. |

- Vanilla uses `any_country_with_original_tag_of` in 10 files, `any_other_country_with_original_tag_of` in 17, `any_country_of` in 5, `all_country_of` once (`common/decisions/formable_nation_decisions.txt`), `any_other_country_of` once (`common/national_focus/italy.txt`) and `all_claimant` once (`common/scripted_triggers/ROM_scripted_triggers.txt`, with `has_country_flag` inside). [vanilla-confirmed 1.19.4.1]
<!-- kit:end id="scope-iterator-additions" -->

<!-- kit:begin id="collection-triggers" at="section:trigger-scopes" -->
Collection triggers. A collection is a group of scopes (countries or states) built from an `input` and `operators`. This is the compact syntax; the system itself (inputs, operators, named collections in `common/collections/`) is on [Collection modding](collection_modding.md).

| Trigger | Scope | Form |
| --- | --- | --- |
| `collection_size` | any | `collection_size = { input = <collection> value > N }`. `value` accepts `<`, `>` and `=`, may be repeated, and may be a variable. |
| `any_collection_element` | any | `any_collection_element = { collection = { input = game:scope operators = { controlled_states } } <triggers> count = N }`. `count` is optional. |
| `all_collection_elements` | any | The same `collection` block; every element must pass. |
| `collection_contains` | any | `collection_contains = { collection = game:all_countries countries = { ENG GER } }` (all listed countries) or `country = FRA`. Only countries can be checked. |
| `count_in_collection` | COUNTRY | `count_in_collection = { collection = { ... } size > N }` plus at most one counting mode: `unit = <sub-unit>`, `buildings = { <building> }`, `manpower = yes`; also `unit_category = { ... }`, `stockpile = <archetype>` and `equipment_ratio` (default 0, land units only). `unit`, `buildings` and `manpower` are mutually exclusive. |
| `has_resources_in_collection` | COUNTRY | `has_resources_in_collection = { collection = { ... } resource = <resource> amount > N }` with optional `extracted = yes` and `buildings = yes` (both default no, mutually exclusive). |

All rows: [docs] `documentation/triggers_documentation.md`

- The documentation says `collection_size` is inclusive (`value > X` means `value >= X`). [docs] `documentation/triggers_documentation.md` The game reads it strictly, so `value > X` means more than X. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, eval_effect log scan. The boundary cases are under [Comparison notes](collection_modding.md#comparison-notes).
- Key trap: `collection_size` takes its collection under `input`; the other triggers take it under `collection`. Vanilla follows this in all 122 `collection_size` blocks and in all 180 `any_collection_element`, 26 `count_in_collection` and 88 `has_resources_in_collection` blocks. [vanilla-confirmed 1.19.4.1] `common/factions/goals/`
- The documentation's example for `has_resources_in_collection` writes `collection = { game:scope operators = { country_and_all_subjects } }` without `input =`. Vanilla always writes `input = game:scope`. [vanilla-confirmed 1.19.3] `common/factions/goals/faction_goals_long_term.txt`
- Vanilla collection blocks also carry `name = <KEY>` (all 68 inline collections in `has_resources_in_collection`, 26 of 26 in `count_in_collection`, 45 of 47 in `any_collection_element`). The keys exist in vanilla localisation (`FACTION` in `diplomacy_l_english.yml`, `FACTION_CONTROLLED_STATES` in `factions_l_english.yml`, `COLLECTION_*` in `collections_l_english.yml`). [vanilla-confirmed 1.19.4.1] The concept document says the collection is localised by its `name`, which describes it where it is used. [docs] `documentation/script_concept_documentation.md`
- `all_collection_elements` and `collection_contains` appear only in the documentation, not in vanilla script. [vanilla-confirmed 1.19.4.1]

```text
count_in_collection = {
    collection = {
        input = game:scope
        operators = { faction_members }
        name = FACTION
    }
    unit = capital_ship
    size > 59
}
```
Vanilla form from `common/factions/goals/faction_goals_long_term.txt`. [vanilla-confirmed 1.19.3]
<!-- kit:end id="collection-triggers" -->

<!-- kit:begin id="version-added-column" at="section:trigger-scopes" -->
**The "Version Added" column.** The column is the wiki's claim. No installed file records when a trigger was added (`changelog.txt` only links to the forum), and the documentation names no versions. [vanilla-confirmed 1.19.4.1] `changelog.txt`, `documentation/`. No trigger was added or removed in 1.19.4. [docs] `documentation/triggers_documentation.md`

- Rows with no usable version: the cell is blank for `has_idea`, `has_market_access_with`, `network_national_coverage`, `pc_is_state_claimed_and_taken_by` and `has_officer_name`. It says `???` for the eight `career_profile_*` triggers, `has_advisor_role`, `has_artillery_ratio`, `has_unit_type` and the two `resource` rows.
<!-- kit:end id="version-added-column" -->

<!-- kit:begin id="scope-keyword-notes" at="section:dual-scopes" -->
Scope keywords as vanilla script spells and uses them.

- Vanilla writes the scope keywords in both cases: `owner = {` 1086 times and `OWNER = {` 601, `controller = {` 1331 and `CONTROLLER = {` 509, `overlord = {` 105 and `OVERLORD = {` 450. [vanilla-confirmed 1.19.4.1] `common/`, `events/`, `history/`
- The table marks `owner` and `controller` as not usable as targets. Vanilla uses them as targets of state-scope triggers: `is_fully_controlled_by = controller` inside `609 = { ... }` in `common/decisions/JAP.txt` (8 uses), `is_controlled_by = OWNER` in `common/national_focus/iraq.txt`, and `is_core_of = controller` and `is_owned_by = controller` elsewhere. [vanilla-confirmed 1.19.4.1] In these blocks the scope is a state, so the keyword stands for that state's owner or controller. [unverified]
- The documentation lists THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED and CAPITAL as the supported targets of triggers that take a scope. [docs] `documentation/triggers_documentation.md` Vanilla script never writes `OCCUPIED` or `CAPITAL` as a target. [vanilla-confirmed 1.19.4.1]
<!-- kit:end id="scope-keyword-notes" -->

<!-- kit:begin id="flow-control-notes" at="section:flow-control-tools" -->
Spelling and options of the flow control triggers in 1.19.3.

- Vanilla accepts the flow keywords in either case. It has `IF = {` 6971 times next to `if = {` 20323, `ELSE` 1228 next to `else` 3729, `ELSE_IF` 1653 next to `else_if` 4160, and lowercase `not = {` 933 times, `or = {` 23 and `and = {` 3, in effect and trigger blocks. [vanilla-confirmed 1.19.4.1] `common/`, `events/`, `history/`
- The documentation lists the lowercase `and`, `or` and `not` as triggers of their own (scope any). [docs] `documentation/triggers_documentation.md`
- `hidden_trigger` takes `tooltip_evaluation = eval`, `no_eval` or `legacy`. `eval` is the standard evaluation and is what you want when the hidden block has side effects (temporary variables) or random parts. `no_eval` is slightly faster when it has neither. `legacy` is the old behaviour and using it explicitly is "very likely a bug". [docs] `documentation/triggers_documentation.md` Vanilla uses `eval` twice, in `common/factions/goals/faction_goals_short_term.txt`. [vanilla-confirmed 1.19.4.1]
- `custom_trigger_tooltip` is documented as a backward-compatible alias of `custom_override_tooltip`. [docs] `documentation/triggers_documentation.md` Vanilla still uses `custom_trigger_tooltip` 1818 times in 166 files against 107 uses of `custom_override_tooltip` in 16 files, and never uses `not_tooltip`. [vanilla-confirmed 1.19.4.1]
<!-- kit:end id="flow-control-notes" -->

<!-- kit:begin id="any-scope-general" at="section:general" -->
Notes on the any-scope triggers.

- `scope_exists = yes` (scope any) checks that the scope itself exists. `exists` checks that the country of the scope exists in the game. Variable scopes are always valid. For example `sp:sp_land_flamethrower_tank = { character = { scope_exists = yes } }` is true when the project has an assigned scientist. Vanilla script does not use it. [docs] `documentation/triggers_documentation.md`
- `has_completed_custom_achievement` takes `mod` (the id the mod sets in its achievements file) and `achievement`; the documentation comment says "set in common/achievements files". [docs] `documentation/triggers_documentation.md`
- `has_dlc` strings must match exactly. Vanilla script uses these 16, none with diacritics: "Man the Guns", "Arms Against Tyranny", "No Compromise, No Surrender", "La Resistance", "By Blood Alone", "No Step Back", "Gotterdammerung", "Battle for the Bosporus", "Thunder at Our Gates", "Graveyard of Empires", "Trial of Allegiance", "Together for Victory", "Waking the Tiger", "Peace For Our Time", "Death or Dishonor" and "Poland: United and Ready". [vanilla-confirmed 1.19.4.1] `common/`, `events/`, `history/`
<!-- kit:end id="any-scope-general" -->

<!-- kit:begin id="career-profile-notes" at="section:career-profile" -->
The career profile triggers are used in the `bronze`, `silver` and `gold` blocks of `common/medals/00_medals.txt` and the condition blocks of `common/ribbons/00_ribbons.txt`. [vanilla-confirmed 1.19.3]

- The first key of `career_profile_check_playthrough_ratio` is `first`, not `frits` as the row says; the keys are `first`, `second`, `ratio` and `compare`. `career_profile_check_ratio` takes the same four keys. [vanilla-confirmed 1.19.3] `common/medals/00_medals.txt` (3 blocks), `common/ribbons/00_ribbons.txt` (1 block)
- `career_profile_check_value` and `career_profile_check_playthrough_value` are not "possibly the same as": vanilla uses both with `{ var = <statistic> value = <n> compare = greater_than_or_equals tooltip = "<LOC_KEY>" }` (57 of 68 `career_profile_check_value` blocks) and with a compact form that lists one or more `<statistic> > N` lines in the block (11 `career_profile_check_value` blocks, all in the ribbons file). [vanilla-confirmed 1.19.3] `common/medals/00_medals.txt`, `common/ribbons/00_ribbons.txt`
- The second `career_profile_check_playthrough_value` example above is missing its closing `}`.
- `career_profile_check_medal`, `career_profile_check_ribbon` and `career_profile_check_points` are never used in vanilla script, so their keys (`medal`, `ribbon`, `value`, `compare`, `tooltip`) come from the wiki only: the documentation entries list no keys. [docs] `documentation/triggers_documentation.md`, [vanilla-confirmed 1.19.4.1] `common/`, `events/`, `history/`. Whether the engine accepts most of those keys is [unverified]. `career_profile_check_medal = { medal = raining_debris_medal }` loaded without an error and read TRUE. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, scripted trigger run from the console, error.log read. TRUE says little about the medal itself, which was not checked. The ids in the examples, `raining_debris_medal` and `orchestra_of_boom`, are real vanilla ids. [vanilla-confirmed 1.19.3] `common/medals/00_medals.txt`, `common/ribbons/00_ribbons.txt`
- `career_profile_has_player_flag` is used 14 times in `common/ribbons/00_ribbons.txt`; the vanilla comments say the flags are "Set in code". [vanilla-confirmed 1.19.3]

Three entries documented in `documentation/triggers_documentation.md` (scope any) that the table does not name. [docs] `documentation/triggers_documentation.md`

- `career_profile_set_temp_variable` copies a career profile statistic into a temporary variable. Vanilla writes `career_profile_set_temp_variable = { gained = recent_provinces_gained }` (29 uses, medals and ribbons), then does arithmetic with `subtract_from_temp_variable` or `add_to_temp_variable` and `check_variable`. The documentation shows a `var = ... value = ...` block instead; vanilla never uses that form. [vanilla-confirmed 1.19.3]
- `career_profile_set_temp_playthrough_variable` is the same for playthrough values (documented form `{ var = <temp> value = <playthrough value> }`); vanilla does not use it. [docs]
- `num_of_career_profile_points` checks the amount of gained career points; vanilla does not use it, and the comparison syntax is not given. [docs] `documentation/triggers_documentation.md`, [vanilla-confirmed 1.19.4.1] `common/`, `events/`, `history/` The syntax is [unverified], apart from this: `num_of_career_profile_points > 1` is accepted with no error and read false in the test. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, scripted trigger run from the console, error.log read. It is also listed as a game variable in [Data structures](data_structures.md#game-variables). [docs]
<!-- kit:end id="career-profile-notes" -->

<!-- kit:begin id="variable-array-triggers" at="section:variables" -->
Temp-variable, array and expression entries that the documentation lists as triggers (scope any) but this page never named. Their full rows are on other pages: [Variables](data_structures.md#variables), [Arrays](data_structures.md#arrays), [Math expressions](data_structures.md#math-expressions), [Scorers](data_structures.md#scorers) and, for the effect side, [Effects](effects.md#variables). All rows: [docs] `documentation/triggers_documentation.md`

| Name | Form |
| --- | --- |
| `add_to_temp_variable`, `subtract_from_temp_variable`, `multiply_temp_variable`, `divide_temp_variable` | `{ <temp var> = <number, variable or math expression> }`, for example `add_to_temp_variable = { num_dogs = { value = num_cats multiply = 2 } }`. |
| `modulo_temp_variable` | `{ var = <temp var> value = <divisor> }`, or the short form `{ <temp var> = <divisor> }`, which vanilla also uses (`modulo_temp_variable = { days = 40 }` in `common/ai_strategy/GER.txt`). |
| `round_temp_variable` | `round_temp_variable = <temp var>`. |
| `clamp_temp_variable` | Clamps a temp variable between two values or variables; the documentation gives no syntax. |
| `set_temp_variable_to_random` | `= <var>` draws from [0, 1). The block form takes `var`, `min` (default 0), `max` (default 1) and `integer` (default no); the range is [min, max). |
| `add_to_temp_array` | `{ array = <name> value = 42 index = 3 }`. `value` defaults to the current scope, `index` to the end of the array (later elements shift). Short form `{ <array> = 42 }`. |
| `remove_from_temp_array` | `{ array = <name> value = 42 }` or `index = 3`. With neither, the last element is removed. |
| `clear_temp_array` | `clear_temp_array = <name>`. |
| `resize_temp_array` | `{ array = <name> size = 3 value = 0 }`. `value` fills new elements (default 0). Short form `{ <array> = 3 }`. |
| `find_highest_in_array`, `find_lowest_in_array` | `{ array = <name> value = <var> index = <var> }`. The results go to the temp variables `v` and `i` unless you name others. |
| `is_in_array` | `{ array = <name> value = 42 }` or `{ <array> = 42 }`. |
| `any_of`, `all_of` | `{ array = <name> value = <var> index = <var> <triggers> }`. Loops over the values; the scope does not change. |
| `any_of_scopes`, `all_of_scopes` | `{ array = <name> tooltip = <loc key> <triggers> }`. Scopes into each element. With a `tooltip`, the key with `_NOT` appended is used when the trigger sits inside `NOT`. |
| `get_highest_scored_country_temp` | COUNTRY. `{ scorer = <id> var = <name> }`; `var` defaults to `highest_scored_country`. |
| `get_sorted_scored_countries_temp` | COUNTRY. `{ scorer = <id> array = <name> scores = <name> }`; defaults `sorted_country_list` and `country_list_scores`. |
| `get_supply_vehicles_temp` | COUNTRY. `{ var = <name> type = truck need = yes }`. `type` is `truck` or `train`; `need = yes` (default no) returns the number needed instead of the number in the stockpile. |
| `check_expr` | `check_expr = { value = <x> add = <y> greater_than = <z> }`. True when the math expression evaluates to non-zero. |
| `debug_math_expr` | Evaluates a math expression and writes the number to the tooltip. Always true; for debugging. |

- Vanilla uses (key assignments in `common/`, `events/`, `history/`): `add_to_temp_variable` 535, `subtract_from_temp_variable` 426, `multiply_temp_variable` 235, `divide_temp_variable` 82, `clamp_temp_variable` 35 (`var` always, `min` in 24, `max` in 30), `add_to_temp_array` 29, `round_temp_variable` 12, `clear_temp_array` 6, `modulo_temp_variable` 3, `check_expr` 3 (in `gain_xp` of `common/unit_leader/00_traits.txt`), `set_temp_variable_to_random` 2, `get_supply_vehicles_temp` 2 (`common/ribbons/00_ribbons.txt`), `find_highest_in_array` 1. `remove_from_temp_array`, `resize_temp_array`, `find_lowest_in_array`, `get_highest_scored_country_temp`, `get_sorted_scored_countries_temp`, `debug_math_expr` and `all_of` are not used in vanilla script. [vanilla-confirmed 1.19.4.1]
- Trap: the default names of the loop temp variables are documented differently. `any_of` is documented with `value` and `index`, while `all_of`, `find_highest_in_array` and `find_lowest_in_array` are documented with `v` and `i`. [docs] `documentation/triggers_documentation.md` Vanilla relies on `v` after a bare `any_of = { array = ... }` (six uses, all `var:v = { ... }`, in `common/decisions/ENG.txt`, `JAP.txt` and `SOV.txt`) and on `v` and `i` after `find_highest_in_array = { array = ... }` in `common/scripted_effects/operation_strat_effects.txt`. [vanilla-confirmed 1.19.4.1] Name `value` and `index` explicitly if you do not want to depend on either.
- `any_of` also appears in `common/ai_equipment/` as a plain list of module ids. That is a different keyword use and has nothing to do with the array trigger. [vanilla-confirmed 1.19.3] `common/ai_equipment/generic_tank.txt`
- `check_variable` also takes `tooltip = <loc key>`; the text may contain the tokens `LEFT` and `RIGHT` for the two sides of the comparison. [docs] `documentation/triggers_documentation.md` Vanilla uses it in 37 blocks, 17 of them in `common/decisions/RAJ_GOE.txt`. [vanilla-confirmed 1.19.4.1]
- `set_temp_variable` is documented as a trigger (scope any) too. The wiki text mentions it but gives it no row here; it is covered under [Variables](data_structures.md#variables). [docs] `documentation/triggers_documentation.md`
<!-- kit:end id="variable-array-triggers" -->

<!-- kit:begin id="country-general-notes" at="section:general-1" -->
Scope and key details for rows in the table above.

- `tag` is valid in CHARACTER and COMBATANT scope as well as COUNTRY. `has_dynamic_modifier` is valid in STATE, COUNTRY and CHARACTER scope. `has_border_war` and `has_border_war_with` are valid in STATE and COUNTRY scope. `is_female` is valid in COUNTRY, CHARACTER and ACE scope. [docs] `documentation/triggers_documentation.md`
- `is_dynamic_country` is true for tags D01 to D50. [docs] `documentation/triggers_documentation.md`
- `has_resources_in_country` also takes `only_imported = yes` (default no), which counts only imported resources instead of the country balance. [docs] `documentation/triggers_documentation.md` Vanilla uses `extracted` in 52 blocks, `only_imported` in 2 and `buildings` in 1. [vanilla-confirmed 1.19.4.1]
<!-- kit:end id="country-general-notes" -->

<!-- kit:begin id="country-trigger-additions" at="section:general-1" -->
Country-scope triggers the tables never name. All rows: [docs] `documentation/triggers_documentation.md`

| Trigger | Form | Meaning and vanilla use |
| --- | --- | --- |
| `energy_ratio` | `energy_ratio < 0.9` | Current energy fulfilment compared with the factories, 1 being 100%. Vanilla uses it in AI weights in `common/technologies/industry.txt`. |
| `has_breakthrough_points` | `{ specialization = specialization_nuclear value = 1 }` | The country has at least that many breakthrough points in the specialization. Not used in vanilla script. |
| `has_completed_goal` | `has_completed_goal = <goal id>` | The country was in a faction when that faction goal was completed. It persists after the faction is disbanded or recreated, unlike `has_completed_faction_goal`. Vanilla: 84 uses in `common/factions/goals/`. |
| `has_facility_specialization` | `has_facility_specialization = specialization_nuclear` | The country has a facility with that specialization. Vanilla uses `specialization_land`, `specialization_air`, `specialization_naval` and `specialization_nuclear` in focuses and operations. |
| `has_naval_invasion_against_state` | `= <state>` or `{ state = <state> preparation > 0.1 activated = no }` | The country has a naval invasion against that state. `preparation` defaults to 0.0, `activated` is optional. Vanilla: `common/raids/paratrooper_raids.txt`. |
| `is_leader_visible` | `is_leader_visible = var:target_leader` | The leader passes the `is_visible` trigger of its own script. Vanilla: a raid `show_target` in `common/raids/land_infiltration_raids.txt`. |
| `num_nukes_being_dropped` | `num_nukes_being_dropped < 100` | Total nukes currently ready to be dropped. Vanilla: `on_nuke_drop` in `common/on_actions/00_on_actions.txt`. |
| `num_nukes_left_to_drop` | `num_nukes_left_to_drop > 0` | Nukes left to drop during this game tick; only useful between drops, for example in the `on_nuke_drop` on action. Not used in vanilla script. |
| `has_any_captured_general` | `has_any_captured_general = yes` | Any general of the country is captured by another country. Vanilla: `common/raids/land_infiltration_raids.txt`. |
| `has_any_general_captured_by` | `has_any_general_captured_by = <country>` | The country has a unit leader captured by the target. Vanilla: `common/operations/00_operations.txt`. |

- The vanilla uses named in the last column were read from the files given; counts are of key assignments in `common/`, `events/` and `history/`. [vanilla-confirmed 1.19.4.1]
<!-- kit:end id="country-trigger-additions" -->

<!-- kit:begin id="ideas-keys" at="section:ideas" -->
Keys missing from the idea rows.

- `amount_taken_ideas` also takes `categories = { military_staff }` (optional), next to `slots = { ... }`. It excludes national spirits, hidden ideas and laws. [docs] `documentation/triggers_documentation.md`
- In `has_allowed_idea_with_traits` and `has_available_idea_with_traits`, `idea` can be a list of trait names in braces and `ignore` can be a list of ideas. The first of the two examples above is labelled `has_allowed_idea_with_traits` but calls `has_available_idea_with_traits`; the documentation's own example has the same copy error. [docs] `documentation/triggers_documentation.md`
<!-- kit:end id="ideas-keys" -->

<!-- kit:begin id="military-notes" at="section:military" -->
Keys and examples for rows in the table above.

- `has_navy_size` also takes `unit = <sub-unit>` (a sub unit definition such as `heavy_cruiser` or `battleship`) next to `type` and `archetype`. The documentation comments `size > 39 unit = heavy_cruiser` as "40 or more". [docs] `documentation/triggers_documentation.md` Vanilla uses `unit` in 53 of its 226 `has_navy_size` blocks, `type` in 110 and `archetype` in 24. [vanilla-confirmed 1.19.4.1]
- The example under `has_mines` is wrong: it shows `has_mined` with `target` and `amount`. `has_mines` takes `region` (a strategic region id) and `amount`, for example `has_mines = { region = <strategic region id> amount = 5 }`. `has_mined` takes `target` and `value`. [docs] `documentation/triggers_documentation.md` Vanilla uses `has_mined` once (`common/achievements.txt`) and never uses `has_mines`. [vanilla-confirmed 1.19.4.1]
<!-- kit:end id="military-notes" -->

<!-- kit:begin id="intelligence-keys" at="section:intelligence" -->
`num_finished_operations` also takes a comparison, `value > 35`, next to `target` and `operation`. [docs] `documentation/triggers_documentation.md` Vanilla uses it in 5 blocks (for example `value < 1`) in `common/ai_strategy/GER_operation_strats.txt`, `common/ai_strategy/ENG_operation_strats.txt` and `common/scripted_effects/operation_strat_effects.txt`. [vanilla-confirmed 1.19.4.1]
<!-- kit:end id="intelligence-keys" -->

<!-- kit:begin id="peace-conference-corrections" at="section:peace-conferences" -->
Two triggers in this table do not exist in 1.19.3, and one parameter is mislabelled.

- `pc_is_untouched_loser` and `pc_is_liberated_by` are not in `documentation/triggers_documentation.md`. It documents 19 triggers with the `pc_` prefix: `pc_current_score`, `pc_does_state_stack_demilitarized`, `pc_does_state_stack_dismantled`, `pc_is_forced_government`, `pc_is_forced_government_by`, `pc_is_forced_government_to`, `pc_is_liberated`, `pc_is_loser`, `pc_is_on_same_side_as`, `pc_is_on_winning_side`, `pc_is_puppeted`, `pc_is_puppeted_by`, `pc_is_state_claimed`, `pc_is_state_claimed_and_taken_by`, `pc_is_state_claimed_by`, `pc_is_state_outside_influence_for_winner`, `pc_is_winner`, `pc_total_score` and `pc_turn`. [docs] `documentation/triggers_documentation.md` Both missing triggers are rejected: `pc_is_untouched_loser = yes` and `pc_is_liberated_by = GER` each logged "Invalid trigger" with "Unknown trigger-type" at load. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, scripted triggers loaded, error.log read.
- Neither name occurs in vanilla script or localisation (`common/`, `events/`, `history/`, `interface/`, `localisation/`). [vanilla-confirmed 1.19.4.1] A read-only string search of `hoi4.exe` finds neither name either, so treat both as invalid and do not look for a documented replacement of the same meaning. [unverified]
- Scopes in the documentation: the country triggers above are COUNTRY, the `pc_does_state_stack_*`, `pc_is_state_claimed*` and `pc_is_state_outside_influence_for_winner` triggers are STATE, and `pc_turn` is scope any. [docs] `documentation/triggers_documentation.md`
- `pc_is_state_claimed` takes `yes` or `no` in the documentation (claimed and uncontested in the conference), not a country as the row says; the country form is `pc_is_state_claimed_by`. [docs] `documentation/triggers_documentation.md`
- Vanilla use counts for each `pc_` trigger are in [Peace conference modding](peace_conference_modding.md#triggers).
<!-- kit:end id="peace-conference-corrections" -->

<!-- kit:begin id="state-scope-corrections" at="section:general-2" -->
Scope, key and syntax details for rows in the table above.

- `ships_in_area` is a COUNTRY trigger in the documentation, not a state trigger. It takes `area`, `size` and an optional `type`. Vanilla runs it inside `owner = { ... }`, for example `ships_in_area = { area = 95 size > 29 }` in `common/on_actions/14_sea_on_actions.txt`, and uses `type` in 16 of 32 blocks. A comment there says it counts all ships, convoys and submarines included. [docs] `documentation/triggers_documentation.md`, [vanilla-confirmed 1.19.4.1] `common/on_actions/14_sea_on_actions.txt`
- `any_province_building_level` compares with `level`, not `limit` as the row says (`level < 3`; 141 of 141 vanilla blocks). The `province = { ... }` block takes repeatable `id`, or `all_provinces = yes` (instead of `id`), and the filters `limit_to_border`, `limit_to_coastal`, `limit_to_victory_point` (provinces with more than 0 victory points) and `limit_to_naval_base`, all default no. [docs] `documentation/triggers_documentation.md`, [vanilla-confirmed 1.19.4.1] `common/national_focus/`
- `free_building_slots` also takes `province = <id>` to check the buildings of one province. Vanilla uses it in 146 blocks, mostly bunkers in focuses such as `common/national_focus/austria.txt`. [docs] `documentation/triggers_documentation.md`, [vanilla-confirmed 1.19.4.1]
- `has_railway_connection` and `can_build_railway` are documented with scope any and take the same route keys. They pick the route in this order: `path = { <province ids> }`, then `start_province` and `target_province` (the shortest path), then `start_state` and `target_state` (the best node). `fallback = yes` (default no) lets each option fall back to the next, and `build_only_on_allied = yes` (default no) restricts a country scope to allied territory. `can_build_railway` also takes `controller_priority = { base = 1 modifier = { tag = MAN add = 2 } }`, where a negative value stops pathing to that controller and a non-negative value is the path cost. [docs] `documentation/triggers_documentation.md` Vanilla uses `start_state` and `target_state` (10 blocks), `start_province` and `target_province` (1) and `build_only_on_allied` (1). [vanilla-confirmed 1.19.4.1] `common/`
<!-- kit:end id="state-scope-corrections" -->

<!-- kit:begin id="character-trigger-additions" at="section:general-3" -->
Character-scope triggers the tables never name. All rows: [docs] `documentation/triggers_documentation.md`

| Trigger | Form | Meaning and vanilla use |
| --- | --- | --- |
| `can_be_captured` | `can_be_captured = yes` | The character can be captured while deployed in a division. `can_be_captured = no` is also a field in character definitions (`common/characters/PRC.txt`); as a trigger vanilla uses it in `on_deployed_leader_defeated` in `common/on_actions/00_on_actions.txt`. |
| `is_general_captured` | `is_general_captured = yes` | The unit leader is captured by any country. Vanilla: `common/decisions/_debug_decisions.txt`. |
| `is_promoted_from_unit` | `is_promoted_from_unit = yes` | The unit leader was promoted from a division or ship. Vanilla: `common/achievements.txt`. |
| `is_in_state` | `is_in_state = 64` or `is_in_state = root.capital` | The character is in that state. Works for deployed generals (HQ location), scientists (facility location, faction programs included) and operatives (mission location). Targets: THIS, ROOT, PREV, FROM, CAPITAL. Vanilla: `common/achievements.txt` (9 uses), `common/on_actions/00_on_actions.txt`. |

- The vanilla comment in `on_deployed_leader_defeated` says `is_in_state` needs the leader to be still deployed, so test it before `capture_by`. [vanilla-confirmed 1.19.4.1] `common/on_actions/00_on_actions.txt`
<!-- kit:end id="character-trigger-additions" -->

<!-- kit:begin id="advisor-warning" at="section:advisors" -->
`advisor_can_be_fired` returns false when the character has no advisor role or the role does not match the given `slot`, so a `no` result does not prove the advisor can be fired. Test `has_advisor_role` first. Without `slot` the short `advisor_can_be_fired = yes` form is enough only when the character has a single advisor role. [docs] `documentation/triggers_documentation.md`
<!-- kit:end id="advisor-warning" -->

<!-- kit:begin id="unit-leader-notes" at="section:unit-leaders" -->
Details for rows in the table above.

- `has_unit_leader_flag` is documented as deprecated in favour of `has_character_flag`, which does the same. It still works: vanilla uses it 89 times in 20 files, for example `events/Decisions_Events.txt`. [docs] `documentation/triggers_documentation.md`, [vanilla-confirmed 1.19.4.1]
- `skill_advantage` is a COMBATANT trigger in the documentation ("compare leader skill levels"), not a character trigger. Vanilla uses it only in `common/combat_tactics.txt` (8 uses). [docs] `documentation/triggers_documentation.md`, [vanilla-confirmed 1.19.4.1]
- `is_leading_army_in_province` also has a block form, `{ province = <id> include_field_marshal = yes }`, that counts a field marshal whose subordinate generals have a division in the province. Vanilla uses the block form once, in `common/on_actions/00_on_actions.txt`. [docs] `documentation/triggers_documentation.md`, [vanilla-confirmed 1.19.4.1]
<!-- kit:end id="unit-leader-notes" -->

<!-- kit:begin id="scientist-names" at="section:scientists" -->
The trigger is `is_active_scientist`, as in the first column. The example `is_scientist_active = yes` in the row is copied from the documentation's own example text. Vanilla uses `is_active_scientist` 10 times (`common/factions/goals/faction_goals_short_term.txt`, `common/special_projects/projects/land_projects.txt`) and never uses `is_scientist_active`, although that string also exists in `hoi4.exe`. [vanilla-confirmed 1.19.4.1] `is_scientist_active` is not accepted as an alias: `is_scientist_active = yes` logged "Invalid trigger 'is_scientist_active'" and "Unknown trigger-type" at load. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, scripted trigger loaded, error.log read.
<!-- kit:end id="scientist-names" -->

<!-- kit:begin id="combat-notes" at="section:combat" -->
Combatant-scope triggers beyond the table.

- `has_cavalry_ratio` (ratio of cavalry battalions in one side's composition, for example `has_cavalry_ratio > 0.5`) and `province_vp` (victory points of the combat province, for example `province_vp > 2`) are documented COMBATANT triggers the table never names. `has_artillery_ratio` and `has_unit_type`, shown above with version `???`, are documented too. [docs] `documentation/triggers_documentation.md`
- Vanilla uses `province_vp` once, `has_artillery_ratio` twice and `has_unit_type` 5 times, all in `common/combat_tactics.txt`; it does not use `has_cavalry_ratio`. [vanilla-confirmed 1.19.4.1]
- These triggers from the character tables are also valid in combatant scope: `tag`, `skill`, `attack_skill_level`, `defense_skill_level`, `planning_skill_level`, `logistics_skill_level`, `average_stats`, `can_select_trait`, `has_trait`, `is_border_war`, `is_leading_volunteer_group` and `is_leading_volunteer_group_with_original_country`. `skill_advantage` is combatant-only. [docs] `documentation/triggers_documentation.md`
<!-- kit:end id="combat-notes" -->

<!-- kit:begin id="division-scope-notes" at="section:division-scope" -->
Details for rows in the table above.

- The documentation lists no scope for the division triggers (the field is empty). They run in the scope that `any_country_division`, `any_state_division`, `random_country_division` and similar selectors open, and unit leader traits use them too. Examples: `any_country_division = { division_has_majority_template = militia }` in `common/decisions/NOR.txt`, `random_country_division = { limit = { unit_organization > 0.4 } ... }` in `events/SEA_generic_events.txt`, and 19 uses of `division_has_majority_template` in `common/unit_leader/00_traits.txt`. [vanilla-confirmed 1.19.4.1]
- `is_unit_template_reserves` is a yes/no check ("returns true if this unit's template has the reserves priority"); the note "must use either the < or > operator" in its row is a copy error. [docs] `documentation/triggers_documentation.md`
- `unit_strength` and `unit_organization` compare on a 0 to 1 scale. Vanilla uses `unit_organization` three times and never uses `unit_strength`, `is_unit_template_reserves` or `has_officer_name`. [vanilla-confirmed 1.19.4.1]
<!-- kit:end id="division-scope-notes" -->

<!-- kit:begin id="mio-scope-notes" at="section:mio-scope" -->
Details for rows and examples in this section.

- The documentation uses `trait = <token>` for `has_mio_trait`, `is_mio_trait_available` and `is_mio_trait_completed` (or the bare token as value). The three examples above write `token = ...`, a key the documentation does not mention. [docs] `documentation/triggers_documentation.md` `token` is not accepted: `has_mio_trait = { token = x }` logged "Unexpected token: token" and "has_mio_trait- no trait provided", and run in a country scope also "Invalid Scope, supported: Military Industrial Organisation, provided: Country", and it read false. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, scripted trigger run from the console, error.log read. Vanilla script uses `has_mio_trait` (3 times, `common/national_focus/soviet.txt`) and `is_mio_trait_completed` (5 times, `common/characters/GER.txt` and `common/military_industrial_organization/organizations/AST_organization.txt`) only with a bare token as value, and never uses `is_mio_trait_available`. [vanilla-confirmed 1.19.4.1]
- `is_mio_trait_available` takes two optional switches, `check_mio_parent_completed` and `check_mio_mutually_exclusive`, both yes by default; the wiki row describes them as the parent-trait and mutually-exclusive-trait tests. [docs] `documentation/triggers_documentation.md`
- `is_mio_available` is not a visibility check as its row says: it is true when the MIO's `available` and `visible` triggers both pass. `is_mio_visible` is true when the `visible` trigger passes. [docs] `documentation/triggers_documentation.md`
- Equipment types for `has_mio_equipment_type` come from `script_enum_equipment_bonus_type` in `common/script_enums.txt` and from `common/equipment_groups/` (a folder, holding `mio_equipment_groups.txt` in 1.19.3); the file `common/equipment_groups.txt` named in the row does not exist. Vanilla uses the trigger 195 times in 5 files, mostly the policy files under `common/military_industrial_organization/policies/`. [vanilla-confirmed 1.19.4.1]
- The MIO triggers also run through a variable or `mio:` scope, for example `var:my_mio_var = { has_mio_size > 5 }`; `has_mio_size` and `has_mio_number_of_completed_traits` accept `<` or `>` against a number or a variable. [docs] `documentation/triggers_documentation.md`
<!-- kit:end id="mio-scope-notes" -->

<!-- kit:begin id="contract-name" at="section:contract-scope" -->
The trigger is `deal_completion`. The example in the row (`deal_completition`) repeats a misspelling from the documentation's own example text; the documentation heading and the compared value (0 to 1) are `deal_completion`. [docs] `documentation/triggers_documentation.md` Vanilla script never uses it. [vanilla-confirmed 1.19.4.1]
<!-- kit:end id="contract-name" -->

<!-- kit:begin id="other-scopes" at="section:special-projects" -->
Scopes the documentation has triggers for that the page has no section for.

| Scope | Triggers beyond `hidden_trigger` and `meta_trigger` |
| --- | --- |
| OPERATION | `is_operation_type` ("checks the type of operation"; targets THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL), `all_operative_leader`, `any_operative_leader` |
| ACE | `is_female` |
| FACTION, RAID_INSTANCE, STRATEGIC_REGION | none |

All rows: [docs] `documentation/triggers_documentation.md`

- `is_operation_type` has no syntax example in the documentation and no vanilla use, so the form `is_operation_type = <operation token>` is [unverified]. [docs] `documentation/triggers_documentation.md`, [vanilla-confirmed 1.19.4.1] `common/`, `events/`, `history/` It needs an operation scope: `is_operation_type = x` run in a country scope logged "Invalid Scope, supported: Operation, provided: Country" and read false. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, scripted trigger run from the console, error.log read.
- The "Faction scope" section above is right that there are no faction-specific triggers. [docs] `documentation/triggers_documentation.md`
<!-- kit:end id="other-scopes" -->

<!-- kit:begin id="meta-trigger-notes" at="section:meta-triggers" -->
`meta_trigger` is documented for STATE, COUNTRY, CHARACTER, COMBATANT, ACE, STRATEGIC_REGION, OPERATION, INDUSTRIAL_ORG, PURCHASE_CONTRACT, RAID_INSTANCE, SPECIAL_PROJECT and FACTION scope. The placeholder names (`COUNTRY`, `POW`, and `EQUIPMENT_ARCHETYPE` in the example above) are chosen by the modder: a token written in square brackets in `text` is replaced by the string given under the same name. `debug = yes` shows what the game actually executes. [docs] `documentation/triggers_documentation.md` Vanilla script has two `meta_trigger` blocks, both in `common/on_actions/12_wuw_on_actions.txt`, where `RK_TAG = "[PREV.GetTag]"` fills the placeholder. [vanilla-confirmed 1.19.4.1]
<!-- kit:end id="meta-trigger-notes" -->

<!-- kit:begin id="diplomacy-scripted-trigger-notes" at="section:diplomacy-scripted-triggers" -->
What vanilla actually defines, and the scope rules.

- Of the 43 `DIPLOMACY_*_ENABLE_TRIGGER` names in the list above, vanilla defines 24 in `common/scripted_triggers/diplomacy_scripted_triggers.txt`. These 19 are not defined anywhere in vanilla script, so overriding them does not replace a base-game rule: `DIPLOMACY_AIR_BASE_ACCESS_ENABLE_TRIGGER`, `DIPLOMACY_ASKSTATECONTROL_ENABLE_TRIGGER`, `DIPLOMACY_CANCEL_FOREIGN_MANPOWER_ENABLE_TRIGGER`, `DIPLOMACY_CANCEL_LICENSED_PRODUCTION_ENABLE_TRIGGER`, `DIPLOMACY_CREATE_FACTION_ENABLE_TRIGGER`, `DIPLOMACY_EMBARGO_ENABLE_TRIGGER`, `DIPLOMACY_GIVESTATECONTROL_ENABLE_TRIGGER`, `DIPLOMACY_IMPROVERELATION_ENABLE_TRIGGER`, `DIPLOMACY_NONAGGRESSIONPACT_ENABLE_TRIGGER`, `DIPLOMACY_OFFER_AIR_BASE_ACCESS_ENABLE_TRIGGER`, `DIPLOMACY_PEACE_PROPOSAL_ENABLE_TRIGGER`, `DIPLOMACY_REQUEST_ACCESS_TO_LICENCE_PRODUCTION_ENABLE_TRIGGER`, `DIPLOMACY_REQUEST_EXP_FORCE_ENABLE_TRIGGER`, `DIPLOMACY_REQUEST_FOREIGN_MANPOWER_ENABLE_TRIGGER`, `DIPLOMACY_RETURN_EXP_FORCE_ENABLE_TRIGGER`, `DIPLOMACY_REVOKE_NONAGGRESSIONPACT_ENABLE_TRIGGER`, `DIPLOMACY_SEND_ATTACHE_ENABLE_TRIGGER`, `DIPLOMACY_SEND_EXP_FORCE_ENABLE_TRIGGER` and `DIPLOMACY_WAR_ENABLE_TRIGGER`. The file header uses `DIPLOMACY_WAR_ENABLE_TRIGGER` as its worked example, so overriding these names is legitimate. [vanilla-confirmed 1.19.4.1] Of the 19, only `DIPLOMACY_CANCEL_FOREIGN_MANPOWER_ENABLE_TRIGGER`, `DIPLOMACY_CREATE_FACTION_ENABLE_TRIGGER` and `DIPLOMACY_EMBARGO_ENABLE_TRIGGER` are literal strings in `hoi4.exe`; whether the engine reads the other 16 is [unverified].
- Names that are in the engine but not in the list: `DIPLOMACY_GUARANTEE_ENABLE_TRIGGER_OVERRIDES_GAME_TRIGGER` (defined in vanilla as `NOT = { has_game_rule = { rule = allow_guarantees option = LIMITED } }`, with a comment that it overrides the rule check on guaranteeing other ideologies), `DIPLOMACY_RECALL_VOLUNTEERS_ENABLE_TRIGGER` (defined in the same vanilla file, and a string in `hoi4.exe`) and `DIPLOMACY_REVOKE_GUARANTEE_ENABLE_TRIGGER_OVERRIDES_GAME_TRIGGER`. [vanilla-confirmed 1.19.4.1] `hoi4.exe` also contains `DIPLOMACY_CANCEL_GENERATE_WARGOAL_ENABLE_TRIGGER`, `DIPLOMACY_LEND_LEASE_CANCEL_ENABLE_TRIGGER`, `DIPLOMACY_LEND_LEASE_EXISTING_ENABLE_TRIGGER`, `DIPLOMACY_REVOKE_EMBARGO_ENABLE_TRIGGER` and the revoke-guarantee override string, which appear nowhere in vanilla script. [unverified]
- Scope: for `DIPLOMACY_*_ENABLE_TRIGGER` the vanilla header says ROOT is the country starting the action and FROM the recipient, as the text above states. For `is_diplomatic_action_valid_<token>` it is the other way round: the scope is the target country and FROM is the initiator; in some cases the trigger is checked only for the initiator, and then both are the same country. If the trigger fails, the action does not appear. [vanilla-confirmed 1.19.3] `common/scripted_triggers/00_diplo_action_valid_triggers.txt`
- Vanilla defines only two visibility triggers, `is_diplomatic_action_valid_stage_coup` and `is_diplomatic_action_valid_boost_party_popularity`, both `NOT = { has_dlc = "La Resistance" }` because the DLC has an operation for it. The other tokens in the list above are not defined in vanilla [vanilla-confirmed 1.19.4.1], and whether the engine reads a trigger of that name for them is [unverified]. [vanilla-confirmed 1.19.3] `common/scripted_triggers/00_diplo_action_valid_triggers.txt`
<!-- kit:end id="diplomacy-scripted-trigger-notes" -->

<!-- kit:begin id="resistance-trigger-notes" at="section:resistance-initiation-triggers" -->
The example above tests the wrong scope, and the file defines more than the one trigger.

- `should_initiate_resistance` runs in state scope. `FROM` is the occupier and `FROM.FROM` the occupied country (always its original tag). It is evaluated when the controller or owner of a state changes, and daily while a resistance is active. State-specific overrides are named `should_initiate_resistance_<id>_<id>`. [vanilla-confirmed 1.19.3] `common/scripted_triggers/00_resistance_initiate_triggers.txt`
- `tag = ENG` in the example is a country trigger; the documentation lists `tag` for COUNTRY, CHARACTER and COMBATANT scope only. [docs] `documentation/triggers_documentation.md` In state scope the occupier is tested through `FROM`: `limit = { FROM = { tag = ENG } }`, as the commented example in the vanilla file does for GER. [vanilla-confirmed 1.19.3]
- The vanilla default is true when `impassable = no`, and either `core_countries^num > 0` is true (the state has a core country) or a Spanish civil war special case applies, and the state is not a core of `FROM`. [vanilla-confirmed 1.19.3]
- The same file holds two AI hook scripted triggers for active cryptology, `should_activate_active_crypto_bonuses` and `should_not_activate_active_crypto_bonuses`, both `always = no` in vanilla. Scope is the target country and `FROM` the AI country; the temp variables `activation_score` and `activation_threshold` are available. Returning true overrides the AI decision. [vanilla-confirmed 1.19.3] `common/scripted_triggers/00_resistance_initiate_triggers.txt`
<!-- kit:end id="resistance-trigger-notes" -->

<!-- kit:begin id="useful-scripted-triggers-check" at="section:useful-scripted-triggers" -->
All eight rows were compared with their vanilla definitions and match. They are defined in `common/scripted_triggers/00_scripted_triggers.txt`, except `is_enemy_ideology`, which is in `common/scripted_triggers/ideology_scripted_triggers.txt`. `has_same_ideology` accepts the groups democratic, fascism, communism and neutrality, and `is_free_or_subject_of_root` is true for any country with `is_subject = no` and for subjects of ROOT. Vanilla uses `is_controlled_by_ROOT_or_ally` 508 times, `controls_or_subject_of` 436, `has_same_ideology` 37 and `is_enemy_ideology` 24. [vanilla-confirmed 1.19.4.1]
<!-- kit:end id="useful-scripted-triggers-check" -->
