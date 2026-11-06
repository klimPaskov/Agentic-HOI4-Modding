# Autonomy state modding

<!-- kit:begin id="review" build="1.19.4.1" checked="2026-11-01" revision="100160" sources="common/autonomous_states/ common/defines/00_defines.lua common/special_projects/projects/naval_projects.txt interface/countrypoliticsview.gfx localisation/english/autonomy_l_english.yml documentation/effects_documentation.md documentation/triggers_documentation.md documentation/modifiers_documentation.md documentation/dynamic_variables_documentation.md" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Checked against: all 21 vanilla autonomy state files, the autonomy defines, the autonomy effects, triggers, modifiers and the rule list.
- Kit blocks added: `autonomy-vanilla-values` (what vanilla sets, min_freedom_level table), `autonomy-rule-list-fixes` (rule names the wiki table gets wrong or lacks), `autonomy-effects-keys` (set_autonomy key spellings, full ids, related effects, triggers, modifiers), `autonomy-defines-extra`.
- Errors found: the rule name `can_join_factions_not_allowed_diplomacy` is not found in the game; `can_use_underway_replenishment` is missing from the rule table; docs examples write `has_autonomy_state = puppet` while vanilla always writes the full id.
- Gaps left: the effect of `peace_conference_initial_freedom` when absent (wiki says 0.5) is not confirmed; `autonomy_free` and `autonomy_annex` have no definition file to check.
**1.19.4.1 re-check (2026-11-01).** Five tagged statements depended on files the update changed (`dominion.txt` and the vanilla-wide scans of rule names, `set_autonomy`, `has_autonomy_state` and `freedom_level`), and all were re-measured. One number moved (`autonomous_state` is used in 81 `set_autonomy` blocks in 24 files, was 80 in 23), and two older statements were corrected (`is_puppet = yes` is also absent from `supervised_state.txt`, and `can_force_government` and `can_lower_tension` are keys of the ideology `rules` blocks). Every other statement cites files that are byte-identical in 1.19.4.1 (Steam depot manifest diff).
<!-- kit:end id="review" -->

<!-- kit:begin id="autonomy-vanilla-values" at="section:arguments" -->
What the 21 vanilla files in `common/autonomous_states/` actually set, to calibrate new states. All lines: [vanilla-confirmed 1.19.4.1] `common/autonomous_states/*.txt`.

- `min_freedom_level` is a decimal from 0 to 1. Vanilla values: 0.0 (personal union, collaboration government, defense council member, Indonesian union state, EU member), 0.2 (integrated puppet, reichskommissariat, imperial protectorate, Austro-Hungarian subject, volkskommissariat), 0.4 puppet, 0.5 reichsprotectorate and integrated warlord subject, 0.6 colony and warlord subject, 0.7 imperial associate, 0.75 supervised state, 0.8 dominion, satellite, associated dominion and imperial subject.
- Several vanilla states share a value (four at 0.8, five at 0.0, five at 0.2). They are kept apart by `allowed` and `allowed_levels_filter`, so the wiki's advice to avoid equal values is a safe default, not an engine error.
- `is_puppet = yes` is absent from dominion, satellite, associated dominion and supervised state, so those subjects are not puppets for `is_puppet` and `is_puppet_of`. `wtt_imperial_subject.txt` writes `is_puppet = no` explicitly.
- `default = yes` appears in 7 files: puppet, reichsprotectorate, warlord subject, imperial protectorate, imperial subject, Austro-Hungarian subject and EU puppet.
- The `rule` block of every file starts with `desc = "RULE_DESC_IS_A_SUBJECT"`, a loc key for the tooltip text. `rule` keys vanilla uses: `can_not_declare_war`, `can_decline_call_to_war`, `can_be_spymaster` (all 21), `can_create_collaboration_government` (18), `contributes_operatives` (15), `units_deployed_to_overlord` (9).
- `use_for_peace_conference_weight` is set only in `puppet.txt` and `supervised_state.txt`. The vanilla comment reads "ROOT is puppet - FROM is potential OVERLORD". `peace_conference_initial_freedom` is set only in `supervised_state.txt` (0.001). [vanilla-confirmed 1.19.4.1] `common/autonomous_states/*.txt` (21 files). The wiki's "0.5 when unset" is [unverified].
- `allowed_levels_filter` is set only in `nsb_personal_union.txt` and `supervised_state.txt`, and each lists only its own id, which locks the subject at that level. `can_lose_level = { always = no }` is used the same way. A stub `can_take_level = { }` that holds only a comment is legal and adds no condition.
- `ai_overlord_wants_garrison` is a trigger-style block, not a weight: 19 files set it, 10 to `always = yes`, 9 to `always = no`.
- `autonomy_free` (independent) and `autonomy_annex` (annexed) have no definition file but have loc keys in `localisation/english/autonomy_l_english.yml` and icons `GFX_autonomy_free_icon` and `GFX_autonomy_annex_icon` in `interface/countrypoliticsview.gfx`. `autonomy_free` is a valid `set_autonomy` value in vanilla focuses (`common/national_focus/australia.txt`).
<!-- kit:end id="autonomy-vanilla-values" -->

<!-- kit:begin id="autonomy-rule-list-fixes" at="section:arguments" -->
Corrections to the game rule table above (the same table is on the [Faction modding](faction_modding.md) page).

- Rule names used in vanilla script (in autonomy `rule` blocks, `set_rule`, `has_rule` or other `rule` blocks): `can_access_market`, `can_be_spymaster`, `can_boost_other_ideologies`, `can_boost_own_ideology`, `can_create_collaboration_government`, `can_create_factions`, `can_declare_war_on_same_ideology`, `can_declare_war_without_wargoal_when_in_war`, `can_decline_call_to_war`, `can_generate_female_aces`, `can_generate_female_country_leaders`, `can_generate_female_unit_leaders`, `can_guarantee_other_ideologies`, `can_join_factions`, `can_join_opposite_factions`, `can_not_declare_war`, `can_only_justify_war_on_threat_country`, `can_puppet`, `can_send_volunteers`, `can_use_kamikaze_pilots`, `contributes_operatives`, `units_deployed_to_overlord`. [vanilla-confirmed 1.19.4.1] `common/`, `events/`, `history/`, searched by script.
- Missing from the table: `can_use_underway_replenishment`, set by `set_rule = { can_use_underway_replenishment = yes }` in a naval special project. [vanilla-confirmed 1.19.3] `common/special_projects/projects/naval_projects.txt`.
- Not used in any autonomy `rule` block, `set_rule` or `has_rule`, but present as strings in `hoi4.exe`: `can_force_government`, `can_lower_tension`, `can_not_build_buildings`, `can_occupy_non_war`. The first two are keys of the `rules` blocks in `common/ideologies/00_ideologies.txt`, the last two occur in no vanilla script. [vanilla-confirmed 1.19.4.1] All four load without a message in an autonomy state's `rule` block, so they are known rule keys, while a made-up name in the same place is reported as "unknown rule". [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, error.log read. Whether any of them has its effect (blocking construction or occupation, for example) was not tested, because the test states were never given to a country. Treat their effect as unverified. [unverified]
- `can_join_factions_not_allowed_diplomacy` occurs in no vanilla file; the rule that exists is `can_join_factions` (for example in `common/decisions/FRA.txt`). [vanilla-confirmed 1.19.4.1] `common/`, `events/`, `history/`, `interface/`, `localisation/`, `documentation/`. That the name is also absent from `hoi4.exe` is [unverified]. The game does not ignore it silently: in an autonomy state's `rule` block it is reported at load as "unknown rule 'can_join_factions_not_allowed_diplomacy'", the same message a made-up name gets, while `can_join_factions = no` in the same place drew none. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, error.log read. Do not use the long name.
- `has_rule = <rule>` checks a rule on the scoped country, `set_rule = { desc = <loc key> <rule> = yes }` overrides it, and `add_relation_rule_override` overrides `can_send_volunteer` or `can_access_market` toward one target or a named trigger. [docs] `documentation/triggers_documentation.md` (`has_rule`), `documentation/effects_documentation.md` (`set_rule`, `add_relation_rule_override`).
<!-- kit:end id="autonomy-rule-list-fixes" -->

<!-- kit:begin id="autonomy-defines-extra" at="section:related-defines" -->
`NDefines.NDiplomacy.AUTONOMY_LEVEL_CHANGE_SANCTUARY = 30` is not in the wiki list: the number of days after an autonomy level change during which neither side can change the level again. The values the wiki gives for the other defines match 1.19.3, for example `AUTONOMOUS_TOTAL_SCORE` 5000 and `AUTONOMOUS_SPILLOVER` 0.025 (both in `NDefines.NCountry`), `AUTONOMY_LEVEL_CHANGE_PP_COST_BASE` 50 and `MASTER_BUILD_AUTONOMY_FACTOR` -0.7 (both in `NDefines.NDiplomacy`). [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua`.
<!-- kit:end id="autonomy-defines-extra" -->

<!-- kit:begin id="autonomy-effects-keys" at="section:additional-notes" -->
Script that reads or changes autonomy, checked against the documentation and vanilla.

| Name | Kind | Syntax or note |
| --- | --- | --- |
| `set_autonomy` | effect, country scope | `set_autonomy = { target = TAG autonomy_state = autonomy_puppet freedom_level = 0.5 end_wars = yes end_civil_wars = yes }`. The scope is the overlord, `target` the subject; both `end_` switches default to yes |
| `release_autonomy` | effect | `target`, `autonomy_state`, `freedom_level`, plus `release_non_owned_controlled` (default no) and `force_change_controller_for_non_ally_controlled` (default no) |
| `add_autonomy_ratio`, `add_autonomy_score` | effects | `{ value = 0.05 localization = LOC_KEY }`; ratio adds a share of the freedom score, score adds an exact amount |
| `puppet` | effect | `puppet = TAG` or `puppet = { target = TAG end_wars = yes end_civil_wars = yes }` |
| `end_puppet`, `release_puppet`, `release_puppet_on_controlled` | effects | Free a puppet, or release it from owned, or owned and controlled, states |
| `has_autonomy_state` | trigger | `has_autonomy_state = autonomy_puppet` |
| `compare_autonomy_state` | trigger | `compare_autonomy_state > autonomy_colony`; checks whether the state is higher than another |
| `compare_autonomy_progress_ratio` | trigger | `compare_autonomy_progress_ratio > 0.5` |
| `is_subject`, `is_subject_of`, `is_puppet`, `is_puppet_of`, `has_subject`, `num_subjects` | triggers | Subject relations |
| `pc_is_puppeted`, `pc_is_puppeted_by` | triggers | Also true for a country released as a puppet in a peace conference; see [Peace conference modding](peace_conference_modding.md) |
| `autonomy_ratio` | dynamic variable | Country scope; -1 if the country is not a subject |
| `autonomy_gain`, `autonomy_gain_global_factor`, `autonomy_gain_trade`, `autonomy_gain_trade_factor`, `autonomy_gain_warscore`, `autonomy_gain_warscore_factor`, `autonomy_gain_ll_to_overlord`, `autonomy_gain_ll_to_overlord_factor`, `autonomy_gain_ll_to_subject`, `autonomy_gain_ll_to_subject_factor` | modifiers | Autonomy gain modifiers |
| `autonomy_manpower_share`, `autonomy_manpower_share_from_subjects`, `master_build_autonomy_factor`, `subjects_autonomy_gain` | modifiers | Other autonomy-related country modifiers |

All rows: [docs] `documentation/effects_documentation.md`, `triggers_documentation.md`, `modifiers_documentation.md`, `dynamic_variables_documentation.md`.

Trap: the documentation examples write the short name (`has_autonomy_state = puppet`, `compare_autonomy_state > puppet`), but every vanilla use writes the full state id (`autonomy_puppet`, `autonomy_colony`, `autonomy_reichsprotectorate`), which is the `id` of the state file. Use the full id. [vanilla-confirmed 1.19.4.1] `has_autonomy_state` and `compare_autonomy_state` in `common/`, `events/`, `history/`.

Trap: the key for the state inside `set_autonomy` is `autonomy_state` in the documentation and in 500 vanilla `set_autonomy` blocks (34 more in `release_autonomy`). A second spelling, `autonomous_state`, is used in 81 vanilla `set_autonomy` blocks in 24 files, among them `history/countries/ENG - Britain.txt` (11) and `common/decisions/SLO.txt`, and is a string in `hoi4.exe`. Write `autonomy_state`. [vanilla-confirmed 1.19.4.1] `common/`, `events/`, `history/`, counted by script. The other spelling takes effect: `set_autonomy = { target = TIB autonomous_state = autonomy_puppet }` made TIB a puppet of the acting country, with no error line. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, scripted effect and game.log. The test left out `autonomy_state`, so a default puppet state when no state key is read is not ruled out, but no unknown-key error was logged for `autonomous_state`.

`freedom_level` is a decimal. Vanilla values run from 0 to 1; the most common are 0.5 (62 uses), 0.2 (28), 1 (10) and 0.8 (9). [vanilla-confirmed 1.19.4.1] `common/`, `events/`, `history/`.
<!-- kit:end id="autonomy-effects-keys" -->
