# Decision modding

<!-- kit:begin id="review" build="1.19.4.1" checked="2026-11-01" revision="103880" sources="common/decisions/ common/wargoals/ dlc/ common/defines/00_graphics.lua documentation/effects_documentation.md documentation/dynamic_variables_documentation.md documentation/console_commands_documentation.md hoi4.exe localisation/english/ common/decisions/_documentation.md" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Checked against: `common/decisions/_documentation.md`, all 88 decision files (4,148 decisions) and 57 category files (597 categories) in `common/decisions/`, the decision effects, triggers and dynamic variables in `documentation/`, the colour define in `common/defines/00_graphics.lua`, and message strings in `hoi4.exe`.
- Kit blocks added: gate semantics and vanilla gating habits, the `state_target` key name, key usage counts, timer notes, mission facts with the related effects and triggers, `war_with_*` keys, highlight colour indexes, category keys.
- Errors found in the wiki text: the DLC name "One Step Back" (should be "No Step Back"), the wargoal `puppet_focus_wargoal` (should be `puppet_wargoal_focus`) and the trigger `has_command_power` (should be `command_power`); highlight colours are indexes into a 15 entry define, not 0 to 3, and an unset colour is probably "no highlight"; `visible` is written in 315 of 443 vanilla missions although the wiki says it does nothing there; the state selector is `state_target` in vanilla and `state_trigger` in the documentation.
- Gaps left: `war_with_on_timeout` and `war_with_target_on_complete` are real tokens that no vanilla file uses, and the meaning of `name`, `desc`, `cosmetic_tag` and category `custom_icon` is inferred from usage only (the `custom_icon` `tag` holds a country tag in all 24 vanilla blocks). `BHR_category`, `QAT_category`, `find_resources` and `develop_infrastructure` are placeholder names in the wiki examples.
**1.19.4.1 re-check (2026-11-01).** About 60 statements depended on files the update changed (52 decision files plus the new `TIB.txt`, the category files, the highlight colour define file and the vanilla-wide effect counts), and all were re-measured. Decisions went from 4,148 in 88 files to 4,186 in 89 and categories from 597 to 598, with the key, cost, timer, `on_map_mode`, `highlight_states` and effect counts moving with them; missions did not change (443 in 46 files), 18 categories (was 14) hold no decision, and `host` is also used in `_exiled_governments_decisions.txt`. Every other statement cites files that are byte-identical in 1.19.4.1 (Steam depot manifest diff).
<!-- kit:end id="review" -->

<!-- kit:begin id="decision-gates" at="section:triggers" -->
Gate semantics, from `common/decisions/_documentation.md`. All rows: [docs] `common/decisions/_documentation.md`.

| Block | THIS and FROM | When checked | Purpose |
| --- | --- | --- | --- |
| `allowed` | THIS = country | once per game at start, or when a save is loaded | drops decisions a country can never have, usually with `original_tag = XXX`; important for performance on targeted decisions |
| `visible` | THIS = country; FROM = target country or state when targeted | on every interface refresh, if `allowed` was true | whether the decision is listed; can get expensive on targeted decisions |
| `available` | the same as `visible` | on every interface refresh, if `allowed` and `visible` were true | whether a listed decision can be taken now; no condition here should be impossible to meet |
| `target_root_trigger` | THIS = country | once a day (one of the 24 hourly ticks, depending on the country), if `allowed` was true | cheap pre-check of the acting country; should be a subset of `visible` |
| `target_trigger` | THIS = country; FROM = target country or state | once a day for each state or country in the world, if `allowed` and `target_root_trigger` were true | picks the targets; each match creates its own decision entry; should be a subset of `visible` |

- In targeted decisions THIS (ROOT) is the country that takes the decision and FROM is the target, in `visible`, `available` and `target_trigger`. [docs] `common/decisions/_documentation.md`.
- Vanilla gates with `allowed`: 2,536 of 4,186 decisions have one. 1,593 test `original_tag`, 298 test `tag`, 211 are empty and 96 are `allowed = { always = no }`, the pattern for decisions that only appear through an activation effect. [vanilla-confirmed 1.19.4.1] `common/decisions/`.
- Categories follow the same habit: 582 of 598 have `allowed`, and 387 of those test `original_tag` (213 with only that test, 162 together with `has_dlc`). Country categories are gated with `allowed = { original_tag = X }`. [vanilla-confirmed 1.19.4.1] `common/decisions/categories/`.
- The effects documentation says `activate_mission` and `activate_targeted_decision` ignore the normal trigger conditions of what they activate. [docs] `documentation/effects_documentation.md`.
- Vanilla pairs `allowed = { always = no }` with an activation effect, with the comment "Activated from effect" (for example in `common/decisions/JAP.txt`). [vanilla-confirmed 1.19.4.1] `common/decisions/`.
- The `has_dlc` example in the `allowed` text above uses a DLC name that does not exist. The DLC is called "No Step Back" (`dlc/dlc034_no_step_back/dlc034.dlc`; about 950 vanilla lines write `has_dlc = "No Step Back"`), and no vanilla file contains "One Step Back". [vanilla-confirmed 1.19.4.1]
- The documentation also names a `state_trigger` key; see the note on state targeted decisions below for what vanilla writes instead. [docs] `common/decisions/_documentation.md`.
<!-- kit:end id="decision-gates" -->

<!-- kit:begin id="decision-highlight-colours" at="section:state-highlighting" -->
`highlight_color_before_active` and `highlight_color_while_active` are indexes into the `BORDER_COLOR_CUSTOM_HIGHLIGHTS` list in `common/defines/00_graphics.lua`. The list has 15 entries (0 to 14), not four. [vanilla-confirmed 1.19.4.1] `common/defines/00_graphics.lua`.

| Index | Meaning in the define's comment |
| --- | --- |
| 0 | mouse hover |
| 1 | bad, while active |
| 2 | good, while active |
| 3 | bad, while passive |
| 4 | good, while passive |
| 5 and 6 | controlled and neutral positive, not ours and neutral negative |
| 7 to 12 | construction targets: valid, invalid and foreign, primary then secondary |
| 13 and 14 | faction theater colours |

All rows: [vanilla-confirmed 1.19.4.1] `common/defines/00_graphics.lua`.

- The wiki says an unset colour is a white outline. The error text in `hoi4.exe` says the value should be -1 for no highlight, "the default if not specified", or an index into that list. Treat an unset colour as no highlight. [unverified] (string in `hoi4.exe`).
- Vanilla values: `highlight_color_while_active` is 1 (21 uses), 2 (21) or 3 (1); `highlight_color_before_active` is 3 (20) or 2 (1). [vanilla-confirmed 1.19.4.1] `common/decisions/`.
- Inside `highlight_states` blocks vanilla uses `highlight_state_targets` 793 times and `highlight_states_trigger` 101 times (one in a category). [vanilla-confirmed 1.19.4.1] `common/decisions/`, `common/decisions/categories/`.
<!-- kit:end id="decision-highlight-colours" -->

<!-- kit:begin id="decision-highlight-provinces" at="section:province-highlighting" -->
`highlight_provinces` is used 13 times in vanilla. Two decisions (`common/decisions/HOL.txt`, `common/decisions/IRQ.txt`) add `highlight_only_provinces = yes` next to it, which the wiki does not mention; the token exists in `hoi4.exe`, and the likely meaning is that only the listed provinces are outlined and not the whole state. [vanilla-confirmed 1.19.4.1] for the usage, [unverified] for the meaning. A test decision with `highlight_only_provinces = yes` beside `highlight_provinces` loaded with no error.log line. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, error.log read. The outline on the map was not looked at.

```text
highlight_states = {
    highlight_state_targets = { state = 7 }
    highlight_provinces = { 9498 391 11456 6241 }
    highlight_only_provinces = yes
}
```
<!-- kit:end id="decision-highlight-provinces" -->

<!-- kit:begin id="decision-category-vanilla" at="section:category-examples" -->
Category keys in vanilla 1.19.4.1 (598 categories in 57 files of `common/decisions/categories/`). Counts are categories that use the key. All rows: [vanilla-confirmed 1.19.4.1] `common/decisions/categories/`.

| Key | Categories | Notes |
| --- | --- | --- |
| `allowed` | 582 | see the gate note above |
| `icon` | 557 | |
| `visible` | 437 | |
| `priority` | 436 | |
| `picture` | 253 | |
| `visible_when_empty` | 185 | 143 write `no`, 42 write `yes` |
| `on_map_area` | 39 | 55 blocks; every block has `name` and `zoom`; `state` in 43, `target_array` in 24, `target_trigger` in 16, `target_root_trigger` in 9 and `targets` in 9 |
| `scripted_gui` | 19 | |
| `available` | 12 | |
| `custom_icon` | 9 | 24 blocks, each with `tag`, `value`, `desc` and `visible` |
| `visibility_type` | 3 | `map_and_decisions_view` twice, `always` once |
| `highlight_states` | 1 | |

- `visibility_type` and `custom_icon` are not described on this page or in `common/decisions/_documentation.md`. All 24 `custom_icon` blocks (7 files in `common/decisions/categories/`) set `tag`, `value` and `desc`. `tag` holds a country tag such as `GER`, `ENG` or `SB1`, not a flag, and `value` and `desc` hold localisation keys that exist in `localisation/english/`. [vanilla-confirmed 1.19.4.1] What the interface does with them is [unverified].
- 18 vanilla categories contain no decision, for example `BRA_propaganda_campaigns` and `USA_war_measures`. [vanilla-confirmed 1.19.4.1] `common/decisions/`.
- The `targets = { capital }` line in the wiki's map category example has no vanilla precedent: in all 4,186 decisions `targets` holds only country tags, `state = <id>` entries and the word `host`. [vanilla-confirmed 1.19.4.1] What the engine does with `capital` is [unverified], so use `state`, `target_array` or `target_trigger` for a dynamic map area. A test decision with `targets = { capital }` loaded with no error.log line, and the decision list was not read. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, error.log read.
<!-- kit:end id="decision-category-vanilla" -->

<!-- kit:begin id="decision-keys-vanilla" at="section:arguments-for-decisions" -->
Decision keys in vanilla 1.19.4.1. Counts are decisions that use the key (4,186 decisions in 89 files). All rows: [vanilla-confirmed 1.19.4.1] `common/decisions/`.

| Key | Decisions | Files | Values seen |
| --- | --- | --- | --- |
| `targets` | 280 | 39 | country tags, state ids (bare or as `state = N`, 118 entries), and `host` (10 uses, 7 in `NOR.txt` and 3 in `_exiled_governments_decisions.txt`) |
| `target_array` | 180 | 28 | `ROOT.core_states` 18, `ROOT.allies` 15, `subjects` 13, `ROOT.subjects` 9, `exiles` 8, `global.is_chinese_warlord` 8, `AUS.expansion_targets` 8 |
| `targets_dynamic` | 51 | 8 | always `yes` |
| `target_non_existing` | 11 | 7 | always `yes` |
| `state_target` | 278 | 47 | see the note on state targeted decisions |
| `on_map_mode` | 569 | 53 | `map_only` 267, `map_and_decisions_view` 167, `decision_view_only` 135 |
| `highlight_states` | 898 | 45 | |
| `activation` | 382 | 43 | 371 of them in missions |
| `days_mission_timeout` | 443 | 46 | number, script constant or variable |
| `timeout_effect` | 436 | 46 | |
| `is_good` | 432 | 48 | `no` 327, `yes` 105 |
| `selectable_mission` | 66 | 12 | `no` 54, `yes` 12 |
| `fixed_random_seed` | 102 | 13 | `no` 98, `yes` 4 |
| `targeted_modifier` | 37 | 9 | |
| `name` | 71 | 12 | a localisation key, often shared by several decisions |
| `desc` | 21 | 1 | a localisation key |
| `cosmetic_tag` and `cosmetic_ideology` | 21 each | 2 | missions in `ITA.txt` and `SOV.txt` |

- `name` and `desc` replace the localisation key a decision would otherwise take from its id, and `cosmetic_tag` with `cosmetic_ideology` pick the flag shown on a mission. That reading comes from the usage (for example `ENG_trade_unions_demand_minister_appointment_1` through `_5` all use one `name`) and was not tested in the interface. [unverified] A test decision with `name` and `desc` keys loaded with no error.log line. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, error.log read.
<!-- kit:end id="decision-keys-vanilla" -->

<!-- kit:begin id="decision-cost-notes" at="section:decision-cost" -->
Cost keys in vanilla 1.19.4.1. All counts: [vanilla-confirmed 1.19.4.1] `common/decisions/`.

- `cost` is set in 2,957 decisions: 2,591 integers, 10 script constants and 356 variable names.
- `custom_cost_trigger` and `custom_cost_text` are always used together (368 decisions each, 38 files). The `_blocked` suffix described above exists in vanilla localisation, for example `decision_cost_50_convoy_25_pp_blocked` in `localisation/english/aat_tooltips_l_english.yml`.
- `ai_hint_pp_cost` is set in 72 decisions.
- The console command `easy_decisions` makes every decision with `days_remove` take one day to be removed and removes all costs and cost triggers, which helps when testing. [docs] `documentation/console_commands_documentation.md`.
<!-- kit:end id="decision-cost-notes" -->

<!-- kit:begin id="decision-timer-notes" at="section:timer-upon-selection" -->
Timer keys in vanilla 1.19.4.1 (4,186 decisions). All counts: [vanilla-confirmed 1.19.4.1] `common/decisions/`.

- `days_remove` is set in 2,152 decisions: 1,799 integers (19 of them `-1`), 20 script constants such as `@DAYS_REMOVE_INFILTRATE_STATE`, and 333 variable names (89 written `name?default`). 17 of the 19 `-1` decisions also have a `remove_trigger` or `cancel_trigger`, so the decision ends on a condition and not on time.
- Every one of the 930 decisions with a non-empty `modifier` block also has `days_remove` or `days_mission_timeout`. The 109 decisions that have neither carry an empty `modifier = {}`. `hoi4.exe` has the message "Decision scripted with modifier, but no days_remove duration. ID: %s", so give every decision that has a `modifier` a timer. [unverified] (string in `hoi4.exe`). The message is logged: a test decision with a `modifier` and no `days_remove` drew "Decision scripted with modifier, but no days_remove duration" at load, and it could still be taken by effect (`activate_decision`, then `has_decision` TRUE). [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, error.log and game.log read.
- `cancel_if_not_visible` is set in 392 decisions (375 `yes`, 17 `no`). `cancel_trigger` is in 647, `cancel_effect` in 403, `remove_effect` in 2,091 and `remove_trigger` in 25.
- `days_re_enable` is set in 407 decisions; 123 write `0`. It also takes a variable, for example `SOV_default_propaganda_campaign_cooldown`.
<!-- kit:end id="decision-timer-notes" -->

<!-- kit:begin id="decision-war-with-keys" at="section:warning-for-war" -->
The `war_with_*` family. All six names below exist as tokens in `hoi4.exe`; a `war_with_on_add` form does not exist in any vanilla script or in `hoi4.exe`. Vanilla counts are for `common/decisions/`. [vanilla-confirmed 1.19.4.1] for the counts, [unverified] for the `hoi4.exe` tokens.

| Key | Value | Vanilla use |
| --- | --- | --- |
| `war_with_on_complete` | tag | 2 decisions, both in `CZE.txt` (`HUN` and `AUS`) |
| `war_with_on_remove` | tag; may repeat | 7 decisions in 5 files (`FIN.txt`, `INS.txt`, `JAP.txt`, `PRC.txt`, `SLO.txt`); one in `PRC.txt` lists three tags |
| `war_with_on_timeout` | tag | none |
| `war_with_target_on_complete` | `yes` | none |
| `war_with_target_on_remove` | `yes` | 5 decisions in `JAP.txt`, `USA.txt` and `WTT_border_conflicts.txt` |
| `war_with_target_on_timeout` | `yes` | 6 missions in `JAP.txt` and `WTT_border_conflicts.txt` |

- The two names with no vanilla use (`war_with_on_timeout`, `war_with_target_on_complete`) appear in the wiki examples on this page. They are real tokens, but untested, so check the tooltip in game before relying on them. [unverified] In one test setup a mission with a 1-day timeout, `war_with_on_timeout`, `war_with_target_on_complete = yes`, a `cosmetic_tag` and a `cosmetic_ideology` ran its `timeout_effect` after the timeout, but at day 3 the country was not at war with the target and had no cosmetic tag, so those keys did nothing there. All three test missions were gone by day 3, including two with a 30-day timeout, and why those two ended is not shown. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, missions activated by effect, game.log read. The tooltip was not read, and another rule could have blocked the war.
- Vanilla missions that warn a target of a coming war use `war_with_target_on_timeout = yes` together with `allowed = { always = no }` and activation by effect, for example `JAP_border_conflict_warning_SOV` in `JAP.txt`. [vanilla-confirmed 1.19.4.1] `common/decisions/JAP.txt`.
<!-- kit:end id="decision-war-with-keys" -->

<!-- kit:begin id="decision-example-corrections" at="section:decision-examples" -->
Errors in the two decision examples below. Sources: `common/wargoals/00_invasion.txt`, `common/decisions/`, `documentation/triggers_documentation.md`.

| In the example | In 1.19.4.1 |
| --- | --- |
| `type = puppet_focus_wargoal` in `QAT_example` | the wargoal is `puppet_wargoal_focus`; the name written in the example exists nowhere in the game files |
| `has_command_power > 14` in `BHR_example` | no trigger called `has_command_power` exists; the trigger is `command_power > 14`, which vanilla writes 13 times in `custom_cost_trigger` blocks |

All rows: [vanilla-confirmed 1.19.4.1] and, for `command_power`, [docs].

- `QAT_category` and `BHR_category` are placeholders for categories you define in `common/decisions/categories/`, and `find_resources` (category) and `develop_infrastructure` (decision) in the cost example are invented names. No vanilla category or decision uses any of the four names. [vanilla-confirmed 1.19.4.1] `common/decisions/`.
<!-- kit:end id="decision-example-corrections" -->

<!-- kit:begin id="decision-missions-vanilla" at="section:missions" -->
Missions in vanilla 1.19.4.1: a mission is a decision with `days_mission_timeout`, and there are 443 of them in 46 files. All counts: [vanilla-confirmed 1.19.4.1] `common/decisions/`.

- 441 have `available`, 435 have `timeout_effect`, 402 set `is_good`, 371 have `activation`, 258 have `allowed`, 163 have `complete_effect` and 65 set `selectable_mission`.
- The wiki says `visible` does nothing in missions. Vanilla still writes a `visible` block in 315 of the 443 missions (36 of them empty). `common/decisions/_documentation.md` never mentions missions, so it does not say that `visible` is ignored for them. [docs] Whether the engine ignores it is [unverified].
- Only 3 missions carry a `cost`: `TSR_pay_for_support_from_warlord_PP`, `_manpower` and `_equipment` in `CHI_warlord_decisions.txt`, all with `selectable_mission = yes`. `hoi4.exe` has the message "Cost for normal missions not implemented. ID: %s", so do not put `cost` on a mission that is not selectable. [unverified] (string in `hoi4.exe`). The message is logged: a test mission with `cost = 10` and no `selectable_mission` drew "Cost for normal missions not implemented. ID: ..." at load. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, error.log read.

Documented effects, triggers and dynamic variables for decisions and missions. All rows: [docs] `documentation/effects_documentation.md`, `documentation/triggers_documentation.md`, `documentation/dynamic_variables_documentation.md`. Uses are counted over `events/`, `common/` and `history/` ([vanilla-confirmed 1.19.4.1]).

| Name | What the documentation says | Vanilla uses |
| --- | --- | --- |
| `activate_decision = <id>` | activates the decision for the scoped country | 44 |
| `activate_mission = <id>` | activates a mission and ignores its normal trigger conditions; cannot activate a mission that is already active | 574 |
| `activate_targeted_decision = { target = <TAG or state> decision = <id> }` | activates a targeted decision or mission and ignores its trigger conditions, cooldown and `fire_only_once`; cannot activate it while it is active in the interface | 191 |
| `remove_decision = <id>` | removes an active decision without running `remove_effect` or starting a cooldown; ignores `fire_only_once` | 9 |
| `remove_mission = <id>` | removes a mission without running its complete or timeout effects | 52 |
| `remove_targeted_decision = { target = <TAG> decision = <id> }` | removes a targeted decision or mission | 35 |
| `remove_decision_on_cooldown = <id>` | removes a decision from cooldown so that it can be reactivated or removed | 11 |
| `add_days_remove = { decision = <id> days = N }` | adds days to the `days_remove` value of a decision | 1 |
| `add_days_mission_timeout = { mission = <id> days = N }` | adds days to a mission's timeout | 180 |
| `unlock_decision_tooltip = <id>` or a block with `decision`, `show_effect_tooltip`, `show_modifiers` | shows what a decision does; both show flags default to `no` | 689 |
| `unlock_decision_category_tooltip`, `activate_mission_tooltip` | tooltip helpers for a category and for a mission | 136 and 16 |
| `has_decision = <id>`, `has_active_mission = <id>` | country triggers for an active decision and an active mission | 107 and 314 |
| `days_mission_timeout@<mission id>`, `days_decision_timeout@<decision id>` | country dynamic variables: days left on a timed mission or decision, for example `days_mission_timeout@GER_mefo_bills_mission` | used in `GER.txt`, `PHI.txt`, `china_nationalist_sea.txt` and `spain.txt` (mission form only) |
<!-- kit:end id="decision-missions-vanilla" -->

<!-- kit:begin id="decision-war-with-target" at="section:warning-for-war-1" -->
The three `war_with_target_on_*` keys take only `yes` in vanilla (11 uses in `common/decisions/`), and they stand for FROM, the target of the decision. The table of all six `war_with_*` keys is in the note on the first "Warning for war" section above. [vanilla-confirmed 1.19.4.1] `common/decisions/`.
<!-- kit:end id="decision-war-with-target" -->

<!-- kit:begin id="decision-state-target-key" at="section:state-targeted-decisions" -->
`common/decisions/_documentation.md` calls the state selector `state_trigger` (values `yes`, `no`, `any`, `any_owned_state`, `any_controlled_state` or a continent key such as `europe`). Vanilla never writes `state_trigger`; all 278 state targeted decisions write `state_target`. Use `state_target`. [docs] for the documented name, [vanilla-confirmed 1.19.4.1] `common/decisions/` for the usage.

- `state_target` values in vanilla: `yes` 209, `any_controlled_state` 34, `any_owned_state` 20, and continent keys 15 (`asia`, `middle_east` and `africa` 3 each, `south_america` and `europe` 2 each, `north_america` and `australia` 1 each). `any` is never written. [vanilla-confirmed 1.19.4.1] `common/decisions/`.
- The 138 vanilla decisions that combine `state_target` with `targets` or `target_array` all use `state_target = yes`. The 140 that use `yes`, `any_owned_state`, `any_controlled_state` or a continent key without explicit targets all have a `target_trigger`. This matches the documentation: the selector only matters without explicit targets, and with them it must be `any` or `yes`. [vanilla-confirmed 1.19.4.1] and [docs] `common/decisions/_documentation.md`.
- The documentation says `any_owned_state` is the faster equal of `owner = ROOT` in the `target_trigger`, `any_controlled_state` of `is_controlled_by = ROOT`, and a continent key of `is_on_continent = <key>`. [docs] `common/decisions/_documentation.md`.
- Both `state_trigger` and `state_target` exist as tokens in `hoi4.exe`, so whether the documented name is accepted as an alias was unknown. It is not accepted in a decision: `state_trigger = any` was rejected at load as "Unexpected token: state_trigger", and the `target_trigger` that went with it was then run against the country and logged "state: Invalid Scope, supported: State, provided: Country" over and over. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, error.log read. Use `state_target`.
- `on_map_mode` is set in 569 decisions; the values are listed in the key table in the "Arguments for decisions" section. [vanilla-confirmed 1.19.4.1] `common/decisions/`.
<!-- kit:end id="decision-state-target-key" -->
