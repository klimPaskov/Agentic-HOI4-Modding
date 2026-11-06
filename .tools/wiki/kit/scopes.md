# Scopes

<!-- kit:begin id="review" build="1.19.4.1" checked="2026-11-01" revision="103725" sources="documentation/effects_documentation.md documentation/triggers_documentation.md documentation/dynamic_variables_documentation.md documentation/script_concept_documentation.md documentation/script_collection_input.md documentation/script_collection_operator.md common/script_constants/ common/country_tag_aliases/ common/factions/ common/raids/ common/special_projects/ common/combat_tactics.txt" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Checked against: the scope lists and every `every_`, `random_`, `any_` and `all_` name in the effect and trigger documentation, the script concept and collection docs, the faction, raid and special project docs, and vanilla script for usage counts.
Kit blocks added: the scope types the docs name (COMBATANT, ACE, FACTION, OPERATION, RAID_INSTANCE, STRATEGIC_REGION and more), `include_invisible`, tooltip keys, undocumented `visible_when_empty`, the five `prioritize` effects, scope keyword spelling, eleven trigger names the table lacks with five corrections to it, effect scope notes, array scope use, and flow control additions (`custom_override_tooltip`, `tooltip_evaluation`, `random_list` seed).
Gaps left: how ACE and STRATEGIC_REGION scopes are entered, what `OCCUPIED` and `CAPITAL` select as targets of an effect, and what `any_claim = yes` matches stay `[unverified]`. A game run on 2026-11-02 settled the `count` option on ordinary `any_` triggers, the two keywords as scope switches, and the scope of `global_every_army_leader`. The version-added columns were not re-checked. The inventory keys `ai_area` (an `any_state_in` argument) and `not_tooltip` (a `custom_override_tooltip` argument) are real documented keys.
**1.19.4.1 re-check (2026-11-01).** 15 statements depended on vanilla scans over folders that the update changed, and all 15 were re-measured on the installed files. Numbers moved: the scope-word table (for example `owner` is now 1086 lines in 133 files, was 1001 in 123), the vanilla file counts of the `_of` and collection triggers (for example `any_state_of` 7 files, was 1, and `any_collection_element` 43, was 2) and `random_allied_country`, which now has one use. Every other statement cites files that are byte-identical in 1.19.4.1 (Steam depot manifest diff).
<!-- kit:end id="review" -->

<!-- kit:begin id="scope-types-1-19-3" at="section:types" -->
### Scope types in the 1.19.3 documentation

The list above misses several scope types. The effect and trigger documentation sorts commands under the types below. Counts are the commands listed for that type; scope-agnostic commands are listed under `any`. All rows: [docs] `documentation/effects_documentation.md` and `documentation/triggers_documentation.md`.

| Scope type | Effects | Triggers | What the docs list there |
| --- | --- | --- | --- |
| COUNTRY | 323 | 336 | the bulk of the commands |
| STATE | 58 | 63 | state commands |
| CHARACTER | 68 | 64 | unit leaders, country leaders, advisors, scientists, operatives |
| COMBATANT | 0 | 44 | combat triggers such as `is_attacker`, `is_winning`, `phase`, `has_trait` |
| ACE | 0 | 3 | `hidden_trigger`, `is_female`, `meta_trigger` |
| FACTION | 0 | 2 | `hidden_trigger`, `meta_trigger` |
| INDUSTRIAL_ORG | 24 | 16 | military industrial organization commands |
| OPERATION | 3 | 5 | effects `every_operative`, `random_operative`, `execute_operation_coordinated_strike`; triggers `all_operative_leader`, `any_operative_leader`, `is_operation_type` |
| PURCHASE_CONTRACT | 1 | 6 | effect `cancel_purchase_contract`; triggers `buyer`, `seller`, `contract_contains_equipment`, `deal_completion` |
| RAID_INSTANCE | 3 | 2 | effects `add_raid_history_entry`, `raid_add_unit_experience`, `raid_damage_units` |
| SPECIAL_PROJECT | 8 | 3 | project flags, dynamic modifiers, `add_project_progress_ratio`, `complete_prototype_reward_option` |
| STRATEGIC_REGION | 1 | 2 | effect `add_region_efficiency` |
| any | 104 | 94 | commands that work in every scope |

- `hidden_trigger` and `meta_trigger` are listed for all twelve trigger scope types. [docs] `documentation/triggers_documentation.md`
- There is no DIVISION section. Division commands are listed under `any` and are reached through `every_country_division`, `every_state_division`, `any_country_division` and `any_state_division`. [docs] `documentation/effects_documentation.md`
- Where vanilla enters these scopes: COMBATANT in the `trigger` block of a combat tactic, whose comment calls it a "combined scope for both country and combatant"; FACTION as `scope:faction = { ... }` in faction goal effects (4 uses in one file); RAID_INSTANCE in the `actor_effects` and `victim_effects` blocks of a raid outcome; SPECIAL_PROJECT through `sp:<id>`; INDUSTRIAL_ORG through `mio:<id>`. [vanilla-confirmed 1.19.3] `common/combat_tactics.txt`, `common/factions/goals/faction_goals_short_term.txt`, `common/raids/_documentation.md`
- How a script enters ACE or STRATEGIC_REGION scope is not shown in the docs, which name no iterator or scope switch for either, or in vanilla script, which has none. [docs] `documentation/effects_documentation.md`, `documentation/triggers_documentation.md`, [vanilla-confirmed 1.19.4.1] `common/`, `events/`, `history/`. Whether the engine offers a way in is [unverified].
- The pattern table says every `any_<object>` has an optional `count`. The docs describe `count` only for `any_collection_element`, and no vanilla `any_` block sets it directly, so the docs do not promise it for the ordinary iterators. [docs] `documentation/triggers_documentation.md`, [vanilla-confirmed 1.19.4.1] `common/`, `events/`, `history/` (0 blocks). The option works anyway and means at least N: `any_owned_state = { is_coastal = yes count = N }` for GER was true for N from 1 to 8, false for 12, 20 and 100, and wrote no error (the control without `count` was true, and GER has 8 to 11 coastal states). [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, trigger run from the console, game.log and error.log read.
<!-- kit:end id="scope-types-1-19-3" -->

<!-- kit:begin id="limiting-additions" at="section:limiting" -->
`include_invisible = yes` (default no) is documented on more iterators than the page names: `every_unit_leader`, `every_army_leader`, `global_every_army_leader`, `every_character`, `every_scientist`, `every_military_industrial_organization` and the trigger `any_unit_leader`. [docs] `documentation/effects_documentation.md`, `documentation/triggers_documentation.md`

Vanilla sets it once, in `common/national_focus/finland.txt`, so most vanilla script relies on the default. `random_select_amount` is documented on the `every_` iterators and appears in 32 vanilla files. [vanilla-confirmed 1.19.4.1] `common/`, `events/`
<!-- kit:end id="limiting-additions" -->

<!-- kit:begin id="tooltip-additions" at="section:tooltip" -->
`tooltip = <key>` replaces the title on the `every_`, `random_`, `any_` and `all_` iterators the docs describe. On `every_allied_country`, `random_allied_country`, the `_of` triggers (`any_country_of`, `all_country_of` and their relatives) and `all_claimant` the value can be a bound localisation object, not only a key; see [Data structures](data_structures.md#bindable-and-formatted-localisation). [docs] `documentation/effects_documentation.md`, `documentation/triggers_documentation.md`

`display_individual_scopes = yes` (default no) is documented on the `every_` iterators and used in 13 vanilla files. [vanilla-confirmed 1.19.4.1] `common/`, `events/`
<!-- kit:end id="tooltip-additions" -->

<!-- kit:begin id="visible-when-empty-undocumented" at="section:empty-effect-scopes" -->
`visible_when_empty` does not appear anywhere in `documentation/effects_documentation.md`, yet 45 vanilla files use it, so it is a working but undocumented key. [vanilla-confirmed 1.19.4.1] `common/`, `events/`
<!-- kit:end id="visible-when-empty-undocumented" -->

<!-- kit:begin id="prioritize-effects" at="section:priority" -->
`prioritize = { <state id> ... }` is documented for exactly five effects: `random_state`, `random_owned_state`, `random_core_state`, `random_controlled_state` and `random_owned_controlled_state`. [docs] `documentation/effects_documentation.md`

Vanilla uses it in 75 files, mostly under `random_owned_controlled_state`; `random_neighbor_state` is not among the documented five. [vanilla-confirmed 1.19.4.1] `common/`, `events/`
<!-- kit:end id="prioritize-effects" -->

<!-- kit:begin id="scope-keywords" at="section:dual-scopes" -->
Scope keywords and prefixes the table above does not cover.

- The docs name eight keywords that can stand as a scope target: THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED and CAPITAL. They do not describe `OCCUPIED` or `CAPITAL`, and vanilla never opens a scope with either (0 uses) [vanilla-confirmed 1.19.4.1], so what they select as targets is [unverified]. [docs] `documentation/effects_documentation.md` (Supported Targets lines) Neither works as a scope switch in an effect: `CAPITAL = { ... }` was rejected at load with "Invalid effect 'CAPITAL'" and "Unknown effect-type: CAPITAL", and `OCCUPIED = { ... }` inside a state scope logged "occupied: invalid event target: OCCUPIED" at run time (the state tested was one nobody occupies). The lower-case keyword `owner` worked in `is_owned_by = owner` and gave the same result as `OWNER`, with no error. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, effects and triggers run from the console, error.log and game.log read. Whether they are valid as the target of some other effect was not tested.
- Vanilla spells several scope words in both cases. Counts are scope blocks opened with the word at the start of a line (lines / files). [vanilla-confirmed 1.19.4.1] `common/`, `events/`, `history/`

| Word | Lower case | Upper case |
| --- | --- | --- |
| owner | 1086 / 133 | 601 / 82 |
| controller | 1331 / 118 | 509 / 47 |
| overlord | 105 / 32 | 450 / 86 |
| faction_leader | 51 / 25 | 3 / 1 |
| capital_scope | 761 / 147 | none |

- `scope:<name>` is a saved scope that vanilla uses only inside faction goals (`scope:faction`). It is separate from `save_event_target_as`. [vanilla-confirmed 1.19.4.1] `common/factions/goals/faction_goals_short_term.txt`
- `temp_var:<name> = { ... }` inside `random_list` is a weight, not a scope. `game:`, `collection:`, `constant:` and `token:` are prefixes for values, not for scope blocks. [vanilla-confirmed 1.19.4.1] `common/on_actions/05_lar_on_actions.txt`, `common/collections/collections.txt`
<!-- kit:end id="scope-keywords" -->

<!-- kit:begin id="trigger-scope-additions" at="section:trigger-scopes" -->
### Trigger scopes missing from the table

The docs list 61 `any_` and `all_` iterator triggers. These are the ones the table above lacks. Description and scope column: [docs] `documentation/triggers_documentation.md`; use column: [vanilla-confirmed 1.19.4.1] `common/`, `events/`, `history/`.

| Trigger | Scope | What the docs say | Vanilla files |
| --- | --- | --- | --- |
| `any_country_of`, `all_country_of` | any | any or all of the countries in `target` pass the triggers | 5, 1 |
| `any_other_country_of` | any | like `any_country_of`, without the current country | 1 |
| `any_state_of` | any | any state in `target` passes the triggers | 7 |
| `any_country_with_original_tag_of` | any | any country whose original tag matches a listed country | 10 |
| `any_other_country_with_original_tag_of` | any | the same, excluding the current country | 17 |
| `all_claimant` | STATE | all countries that claim the state in scope | 1 |
| `any_claim` | COUNTRY | "check if there is a claim between a country and all others" | 0 |
| `any_collection_element`, `all_collection_elements` | any | trigger block over a collection; `any_collection_element` takes an optional `count` | 43, 0 |
| `scope_exists` | any | true if the current scope exists, which differs from `exists` (does the country exist); variable scopes always exist | 0 |

- `target` takes either a list (`target = { SWE NOR FIN DEN ICE }`) or `constant:<category>.<entry>`. Collection triggers are covered on [Collection modding](collection_modding.md#triggers). [docs] `documentation/triggers_documentation.md`
- `any_claim` is documented in one line, as a check for a claim between the country in scope and all others. [docs] `documentation/triggers_documentation.md` Its exact meaning is [unverified]. `any_claim = yes` is accepted and takes a boolean, not a block: the block form `any_claim = { always = yes }` logged "Not a valid value: {" at load. The boolean form read false for GER, ITA, HUN, JAP, SOV and LUX in 1936, with no error, and no country with claims was found to test a true result. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, trigger run from the console, error.log and game.log read.

Errors in the table and examples above:

- `all_purchase_contract` is not a trigger. The documented name is `all_purchase_contracts`; `any_purchase_contract` is singular. [docs] `documentation/triggers_documentation.md`
- `all_core_state` and `any_core_state` have their descriptions swapped: `all_` checks that every core state passes, `any_` that at least one does. [docs] `documentation/triggers_documentation.md`
- `any_scientist` is described as "active scientist". The docs give two separate pairs: `any_scientist` / `all_scientists` and `any_active_scientist` / `all_active_scientist`. The example `all_scientistst` has a typo. [docs] `documentation/triggers_documentation.md`
- The `_of` examples write `constant:country_groups:nordics` with a colon. Vanilla separates category and entry with a dot, as in `target = constant:country_groups.literally_china`. The `any_state_of` example also takes a country group; state groups live in `common/script_constants/state_groups.txt`. [vanilla-confirmed 1.19.4.1] `common/decisions/CHI_decisions.txt`, `common/script_constants/state_groups.txt`
- The docs example under `any_other_country_with_original_tag_of` shows the name `any_country_with_original_tag_of`; the documented heading is the longer name. [docs] `documentation/triggers_documentation.md`
<!-- kit:end id="trigger-scope-additions" -->

<!-- kit:begin id="effect-scope-notes" at="section:effect-scopes" -->
The effect side of the table is complete for 1.19.3: all 53 `every_`, `random_` and `global_every_` iterator effects in the documentation (not counting `random_list` and `random_scope_in_array`) are listed above. [docs] `documentation/effects_documentation.md` (compared by name)

- The docs list `every_other_country` and `every_country_with_original_tag` for country scope only, and `random_other_country` and `random_country_with_original_tag` for any scope; the table above says otherwise for some of them. Call all four from country scope, which both readings allow. [docs] `documentation/effects_documentation.md`
- `global_every_army_leader` is listed under COUNTRY scope in the docs and has no vanilla use (0 files) [vanilla-confirmed 1.19.4.1], so the docs do not back the table's "Always usable". [docs] `documentation/effects_documentation.md` It needs a country scope: from GER it visited every country's leaders (1862 visits against GER's 19 army leaders), and inside a state scope it logged "global_every_army_leader: Invalid Scope, supported: Country, provided: State" and visited none. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, effect run from the console, game.log and error.log read.
- Vanilla use (lines / files): `every_faction_member` 128 / 7, `every_allied_country` 24 / 16, `every_collection_element` 26 / 4. `random_allied_country` 1 / 1, and `party_leader` has none. [vanilla-confirmed 1.19.4.1] `common/`, `events/`, `history/`
- For `every_collection_element` see [Collection modding](collection_modding.md#effects-and-math).
<!-- kit:end id="effect-scope-notes" -->

<!-- kit:begin id="array-scope-notes" at="section:array-scopes" -->
`for_each_scope_loop` also takes `tooltip = <loc>`, which prints the sub-effects under that title, and every array scope names its break variable `break` unless you set another. [docs] `documentation/effects_documentation.md`

Vanilla use (lines / files): `for_each_scope_loop` 187 / 49, `all_of_scopes` 61 / 16, `any_of_scopes` 24 / 11, `random_scope_in_array` 3 / 2. [vanilla-confirmed 1.19.4.1] `common/`, `events/`, `history/`

Collections do the same job without a stored array: [Collection modding](collection_modding.md#collections-and-loops) compares them with the array loops. Loop defaults are in [Data structures](data_structures.md#arguments).
<!-- kit:end id="array-scope-notes" -->

<!-- kit:begin id="flow-control-additions" at="section:flow-control-tools" -->
Details the table above lacks.

- `custom_trigger_tooltip` is an alias of `custom_override_tooltip`, kept for old script; the docs prefer `custom_override_tooltip` for new triggers. `custom_override_tooltip` also exists as an effect and takes a bound localisation object, see [Data structures](data_structures.md#bindable-and-formatted-localisation). [docs] `documentation/triggers_documentation.md`, `documentation/effects_documentation.md`
- `hidden_trigger` accepts `tooltip_evaluation = eval`, `no_eval` or `legacy`. Use `eval` when the hidden trigger sets temp variables or uses random choices; see [Data structures](data_structures.md#trigger-usage). [docs] `documentation/triggers_documentation.md`
- `random_list` accepts `log = yes`, which writes the roll to `game.log`, and `seed = <variable, constant or random>`, which replaces the scope's seed. Weights may be variables. [docs] `documentation/effects_documentation.md`
- Vanilla has a `seed =` line in 12 files, for example `seed = random` inside a `random_list`. [vanilla-confirmed 1.19.4.1] `common/`, `events/`
- Loop caps: `MAX_EFFECT_ITERATION = 1000`, which matches the 1000 in the table. [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua`
<!-- kit:end id="flow-control-additions" -->
