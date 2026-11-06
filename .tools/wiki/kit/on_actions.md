# On actions

<!-- kit:begin id="review" build="1.19.4.1" checked="2026-11-01" revision="102346" sources="common/on_actions/ common/military_industrial_organization/organizations/_documentation.md hoi4.exe" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Checked against: `common/on_actions/_documentation.md` (its list is dated 2024-11), all 17 vanilla on-action files (337 hook blocks, 117 distinct names, 33 of them per-tag) with their scope comments, the MIO documentation and strings in `hoi4.exe`.
Kit blocks added: the file shape and vanilla counts, per-tag hooks with a fix for the broken `on_weekly_BHR` example, notes per section (politics, diplomacy, faction, autonomy, states, wargoals, unit leaders, military, aces, resistance, MIO, special projects) and a hook inventory at the bottom.
Errors found in the wiki text: `on_operative_on_mission_spotted` has ROOT and FROM swapped; `on_operative_detected_during_operation` is described and exemplified as the death hook; the `on_units_paradropped_in_state` example is the `on_paradrop` one; `on_weekly_BHR` lacks its `effect` block. 14 hooks in the tables appear nowhere in the documentation or in vanilla.
Gaps left: the 14 unconfirmed hooks and the exe-only names stay [unverified]; hook firing order and timing were not run. The inventory's unknown keys (`SOV_escalate_the_war_effect`, `USA_unrest`, `on_monthly_USA`, `on_weekly_BHR`, `to_be_updated_daily`) are placeholders in examples; `on_stage_coup` is a hook name that no 1.19.3 file defines.
**1.19.4.1 re-check (2026-11-01).** 42 statements depended on the on-action files that the update changed, and all 42 were re-measured on the installed files. Numbers moved: 346 hook blocks (was 337), 121 distinct names (117), 36 per-tag names (33), 655 `effect` blocks (630) and 21 monthly tags (LEB, SYR and USA are new), and 13 of the 15 `on_state_control_changed` files carry the scope comment (was 14), while a generic `on_daily`, a second generic `on_weekly`, two more `on_peaceconference_ended` scope comments and a second job for `on_project_completion` are new facts. Every other statement cites files that are byte-identical in 1.19.4.1 (Steam depot manifest diff).
<!-- kit:end id="review" -->

<!-- kit:begin id="onaction-file-shape" at="section:file-example" -->
The file shape in 1.19.4.1, counted from vanilla.

- `common/on_actions/` has 17 vanilla files, `00_on_actions.txt` to `16_taog_on_actions.txt` (no `11_`; `00_testing_on_actions.txt` is one of them). Every file is one `on_actions = { ... }` block. [vanilla-confirmed 1.19.4.1] `common/on_actions/*.txt`.
- Inside a hook block vanilla uses only `effect` (655 times) and `random_events` (13 times). A hook may hold both, as `on_ace_promoted` and `on_nuke_drop` do. Several `random_events` blocks in one hook each pick one event: `on_new_term_election` has several. [vanilla-confirmed 1.19.4.1]
- Hooks with `random_events` in vanilla: `on_new_term_election`, `on_nuke_drop`, `on_justifying_wargoal_pulse`, `on_wargoal_expire` and five ace hooks. `on_justifying_wargoal_pulse` ends its list with `17000 = 0`, the "nothing happens" weight the page describes. [vanilla-confirmed 1.19.4.1] `common/on_actions/00_on_actions.txt`.
- The same hook is defined in many files: `on_capitulation` in 14 files, `on_state_control_changed` in 15 (16 blocks), `on_startup` in 14, `on_declare_war` in 11. Each DLC file adds its own block and none repeats another's work, so blocks from different files are additive. [vanilla-confirmed 1.19.4.1] counts. The additive rule held in a test: `on_startup` blocks from three mod files all ran, in file name order (a, b, c) in each of three sessions. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, game.log read after the start. The file names were a, b and c, so name order and load order cannot be told apart. A capitalised hook name (`ON_STARTUP`) and a capitalised effect keyword (`IF`) worked too.
- `on_startup` blocks in vanilla scope explicitly into tags (`GER = { ... }`), as the vanilla comment "Not run on a specific country." and the page's `none` default scope imply. [vanilla-confirmed 1.19.4.1] `00_on_actions.txt`.
<!-- kit:end id="onaction-file-shape" -->

<!-- kit:begin id="onaction-general-corrections" at="section:general-on-actions" -->
Per-tag hooks, and the broken `on_weekly_BHR` example.

- The `on_weekly_BHR` example above puts its `if` directly in the hook with no `effect = { }` around it. A hook block holds `effect` or `random_events` and nothing else, so the working form is `on_weekly_BHR = { effect = { if = { ... } } }`. [vanilla-confirmed 1.19.4.1] `common/on_actions/*.txt`.
- The tag in `on_daily_TAG`, `on_weekly_TAG` and `on_monthly_TAG` is a country tag written into the hook name. Vanilla defines 6 daily tags (AST, ETH, GER, ITA, SOV, SWE), 9 weekly (BUL, ECU, ETH, FIN, GER, RAJ, SOV, SWE, VEN) and 21 monthly (AFG, AUS, BUL, CHI, COG, CZE, ENG, GER, INS, JAP, LEB, MEX, NOR, PAL, PER, RAJ, SIA, SOV, SWE, SYR, USA). [vanilla-confirmed 1.19.4.1] `common/on_actions/*.txt`.
- Vanilla has one generic `on_daily` (`04_mtg_on_actions.txt`, limited to naval treaty signatories), two generic `on_weekly` (`04_mtg_on_actions.txt` and `05_lar_on_actions.txt`, where AI countries with an intelligence agency run `update_operation_ai`) and two generic `on_monthly` blocks. The per-tag form is the vanilla way to run code for one country each day. [vanilla-confirmed 1.19.4.1]
- `_documentation.md` lists `on_startup`, `on_daily`, `on_weekly`, `on_monthly` and the three `_TAG` forms, and puts `on_nuke_drop`, `on_pride_of_the_fleet_sunk`, `on_naval_invasion` and `on_paradrop` in the same General group (this page files them under Military). [docs] `common/on_actions/_documentation.md`.
- `hoi4.exe` contains the message "%s is not a valid tag of on_daily", so a wrong tag in a per-tag hook name is probably reported. [unverified] An `on_daily_ZZZ` hook wrote "ZZZ is not a valid tag of on_daily" to `error.log` at load, and the hook never fired in about 13 game days. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, error.log and game.log read.
<!-- kit:end id="onaction-general-corrections" -->

<!-- kit:begin id="onaction-politics" at="section:politics" -->
Politics hooks against the documentation and vanilla.

- `on_stage_coup` has no block in any vanilla file and is not in the documentation list. The documented politics hooks are `on_coup_succeeded`, `on_government_change`, `on_ruling_party_change`, `on_ruling_party_change_immediate`, `on_new_term_election` and the three peace conference hooks. Whether `on_stage_coup` exists in the engine is [unverified]; do not build on it. [docs] `common/on_actions/_documentation.md`, [vanilla-confirmed 1.19.4.1] `common/on_actions/*.txt`.
- `on_ruling_party_change_immediate` is listed as deprecated ("unsafe behavior, prefer using on_ruling_party_change"). No vanilla block uses it. [docs] `common/on_actions/_documentation.md`.
- `on_peaceconference_ended` has two scope descriptions in vanilla: "ROOT is winner #FROM is loser" in `03_wtt`, `04_mtg`, `05_lar`, `08_bba` and `14_sea` (the last two phrase it as "ROOT is the winner, FROM is the loser"), and "ROOT - country that just went to peace" in `00_on_actions.txt` and `07_nsb`. The documentation says ROOT is the winner and FROM the loser, called for every winner and loser pair. Log both scopes before relying on one. [docs] `common/on_actions/_documentation.md`, [vanilla-confirmed 1.19.4.1] `common/on_actions/*.txt`.
- `on_new_term_election` is commented "# country": ROOT is the country that holds the election. [vanilla-confirmed 1.19.4.1] `common/on_actions/00_on_actions.txt`.
<!-- kit:end id="onaction-politics" -->

<!-- kit:begin id="onaction-diplomacy" at="section:diplomacywar" -->
Diplomacy and war hooks against the documentation and vanilla.

- `_documentation.md` also lists `on_recall_volunteers` and `on_force_government`, which the table above lacks. No vanilla file uses either and the documentation gives no scopes, so their ROOT and FROM are unknown. `on_force_government` is also a string in `hoi4.exe`. [docs] `common/on_actions/_documentation.md`; scopes [unverified].
- `on_call_allies` and `on_join_allies` are defined in vanilla (`12_wuw_on_actions.txt`, `16_taog_on_actions.txt`) with the scopes in the table, but are missing from the documentation list. [vanilla-confirmed 1.19.4.1]
- Order: a vanilla comment says `on_war_relation_added` "fires in 2nd place (1st is on_declare_war)" and "is triggered ALWAYS". `on_war` fires when a country goes from peace to war and not again for later enemies. [vanilla-confirmed 1.19.4.1] `common/on_actions/05_lar_on_actions.txt`, `00_on_actions.txt`.
- Thirteen hooks in this and the Politics table have no vanilla block and no documentation entry: `on_guarantee`, `on_military_access`, `on_offer_military_access`, `on_lend_lease`, `on_incoming_lend_lease`, `on_send_expeditionary_force`, `on_return_expeditionary_forces`, `on_request_expeditionary_forces`, `on_ask_for_state_control`, `on_give_state_control`, `on_peace_proposal`, `on_send_attache` (here) and `on_stage_coup` (Politics). Their scopes in the table cannot be checked. `hoi4.exe` has the bare names of several (for example `send_attache`, `peace_proposal`) but not the full `on_` strings, and it also lacks the full string for vanilla hooks such as `on_declare_war`, so that proves nothing. Test a hook with a `log` effect before relying on it. The missing block and entry are [vanilla-confirmed 1.19.4.1] `common/`, `events/`, `history/` and `interface/`, and [docs] `common/on_actions/_documentation.md`; whether the engine knows these hooks is [unverified].
<!-- kit:end id="onaction-diplomacy" -->

<!-- kit:begin id="onaction-faction" at="section:faction" -->
Joining a faction has two hooks, and vanilla comments say which one fires for `add_to_faction`.

- `on_join_faction`: "THIS DOES NOT FIRE ON ADD_TO_FACTION EFFECT! USE ON_OFFER_JOIN_FACTION!" (comment on the hook in seven vanilla files). ROOT is the joining country and FROM the faction leader. [vanilla-confirmed 1.19.4.1] `common/on_actions/00_on_actions.txt`, `16_taog_on_actions.txt`.
- `on_offer_join_faction`: ROOT (and THIS) is the faction leader and FROM the country invited. A vanilla comment says it also fires when the invited country actually joins and for the `add_to_faction` effect. [vanilla-confirmed 1.19.4.1] `common/on_actions/08_bba_on_actions.txt`, `09_aat_on_actions.txt`, `12_wuw_on_actions.txt`, `13_goe_on_actions.txt`.
<!-- kit:end id="onaction-faction" -->

<!-- kit:begin id="onaction-autonomy" at="section:autonomy" -->
`16_taog_on_actions.txt` defines `on_subject_annex`, without the final "ed". The documented hook is `on_subject_annexed`, and `hoi4.exe` has only that spelling. The Indonesia block under the misspelled name therefore probably never runs, and nothing seen here reports a wrong hook name. [vanilla-confirmed 1.19.4.1] `common/on_actions/16_taog_on_actions.txt` (the name); the failure is [unverified].
<!-- kit:end id="onaction-autonomy" -->

<!-- kit:begin id="onaction-states" at="section:states" -->
`on_state_control_changed` is defined in 15 vanilla files, 13 of them with a comment such as "ROOT is new controller #FROM is old controller #FROM.FROM is state ID". FROM.FROM is a state scope: vanilla runs `FROM.FROM = { state = 36 }` and `FROM.FROM = { is_core_of = FRA }` inside it. [vanilla-confirmed 1.19.4.1] `common/on_actions/00_on_actions.txt`.

`hoi4.exe` also contains `on_state_owner_changed` (next to the strings " NewOwner:" and " NewController:") but neither the documentation nor any vanilla file uses it. [docs] `common/on_actions/_documentation.md`, [vanilla-confirmed 1.19.4.1] `common/`. Do not rely on it. The exe string is [unverified].
<!-- kit:end id="onaction-states" -->

<!-- kit:begin id="onaction-wargoals" at="section:wargoals" -->
`on_generate_wargoal` has no vanilla block and no line in `_documentation.md`; `hoi4.exe` does contain that name as a string. [docs] `common/on_actions/_documentation.md`, [vanilla-confirmed 1.19.4.1] `common/on_actions/` for the missing block and line. The exe string and the scopes in the row above are [unverified].

`on_justifying_wargoal_pulse` is commented "during justifying wargoals; triggered daily, so make sure there is a sink somewhere not firing events; country, FROM = target nation". Vanilla fires `war_justification.1` to `war_justification.19` from it with a `17000 = 0` sink. `on_wargoal_expire` fires `war_justification.301`. [vanilla-confirmed 1.19.4.1] `common/on_actions/00_on_actions.txt`.
<!-- kit:end id="onaction-wargoals" -->

<!-- kit:begin id="onaction-unit-leader" at="section:unit-leader" -->
Unit leader hooks missing from the table.

- `on_navy_leader_won_combat` and `on_navy_leader_lost_combat` are documented and exist in vanilla (`00_on_actions.txt` empty, `14_sea_on_actions.txt` with content). Scopes: "THIS is the admiral, From is owner country, FromFrom is the combatant". [docs] `common/on_actions/_documentation.md`, [vanilla-confirmed 1.19.4.1] `common/on_actions/00_on_actions.txt`.
- `on_deployed_leader_defeated` is documented. Vanilla runs it in the defeated leader's scope with FROM as the winning country: if `can_be_captured = yes` it does `capture_by = FROM`, otherwise it adds the `wounded` trait for 90 days. [docs] `common/on_actions/_documentation.md`, [vanilla-confirmed 1.19.4.1] `common/on_actions/00_on_actions.txt`.
- `on_unit_leader_level_up` also has `FROM.FROM`: the original owner for exiled leaders. [vanilla-confirmed 1.19.4.1] `common/on_actions/07_nsb_on_actions.txt`.
- `on_unit_leader_promote_from_ranks_veteran` and `_green` exist only in vanilla (not in the documentation list). The vanilla comment reads "Unit leader scope, FROM is unit". [vanilla-confirmed 1.19.4.1] `common/on_actions/00_on_actions.txt`.
<!-- kit:end id="onaction-unit-leader" -->

<!-- kit:begin id="onaction-military" at="section:military" -->
The "Example: on_units_paradropped_in_state" above repeats the `on_paradrop` example, with the wrong hook name. The vanilla block is `on_units_paradropped_in_state`, commented "root is the state that was dropped into; from is the dropping country; this differs from on_paradrop in that it is run once per paradrop, not once per unit dropped". [vanilla-confirmed 1.19.4.1] `common/on_actions/00_on_actions.txt`.

`on_naval_invasion` and `on_paradrop` match their vanilla comments: ROOT is the invading country, the default scope is the invaded state and FROM is the state where the invasion started. `on_add_history` is commented "Unit Scope". Neither `on_units_paradropped_in_state` nor `on_add_history` is in the documentation list. [vanilla-confirmed 1.19.4.1] `common/on_actions/00_on_actions.txt`.
<!-- kit:end id="onaction-military" -->

<!-- kit:begin id="onaction-aces" at="section:aces" -->
`on_aces_killed_each_other` fires twice, once for each ace, so ROOT and FROM swap between the two calls. [vanilla-confirmed 1.19.4.1] `common/on_actions/00_on_actions.txt` (comment "This event fires twice, once for each ace"). `on_ace_killed_on_accident` and `on_non_ace_killed_other_ace` are empty blocks in vanilla.
<!-- kit:end id="onaction-aces" -->

<!-- kit:begin id="onaction-resistance" at="section:la-résistance" -->
Two rows above are wrong against the vanilla scope comments.

- `on_operative_on_mission_spotted`: ROOT is the country the operative was performing its mission in, and FROM is the country the operative is operating for. The row has them the other way round. THIS is the operative. [vanilla-confirmed 1.19.4.1] `common/on_actions/05_lar_on_actions.txt`.
- `on_operative_detected_during_operation` is a different hook from `on_operative_death`; the row and the example above describe the death hook. In vanilla the scope is the operative and the block runs `capture_operative = { captured_by = FROM }` and `kill_operative = { killed_by = FROM }`, so FROM is the country that detected the operative. `FROM.FROM` is the operation's state, set only when the operation has a `selection_target`. [vanilla-confirmed 1.19.4.1] `common/on_actions/05_lar_on_actions.txt`.

`on_operative_created` and `on_operative_recruited` are documented but have no vanilla block. The other rows match their vanilla comments. [docs] `common/on_actions/_documentation.md`, [vanilla-confirmed 1.19.4.1]
<!-- kit:end id="onaction-resistance" -->

<!-- kit:begin id="onaction-mio" at="section:military-industrial-organization" -->
The documentation list also names `on_mio_tech_reseach_cancelled` and `on_mio_tech_reseach_completed`, spelled "reseach". `hoi4.exe` has the same misspelling. Vanilla's `09_aat_on_actions.txt` declares empty blocks under the correct spelling, `on_mio_tech_research_cancelled` and `on_mio_tech_research_completed`. Those names are not the documented hooks, so do not copy them. [docs] `common/on_actions/_documentation.md`, [vanilla-confirmed 1.19.3] `common/on_actions/09_aat_on_actions.txt`; the exe spelling is [unverified].

Each of these hooks also exists at MIO level without the `mio_` part (`on_design_team_assigned_to_tech`, `on_design_team_assigned_to_variant`, `on_industrial_manufacturer_assigned`, `on_industrial_manufacturer_unassigned`, `on_tech_research_cancelled`, `on_tech_research_completed`). Use the on action for code that applies to any MIO and the MIO-level hook for one organization. [docs] `common/military_industrial_organization/organizations/_documentation.md`, vanilla comment in `09_aat_on_actions.txt`.
<!-- kit:end id="onaction-mio" -->

<!-- kit:begin id="onaction-special-projects" at="section:special-projects" -->
`on_project_completion` is defined only in `12_wuw_on_actions.txt` (an achievement counter for Belgium and a flag for the US AI) with the comment "ROOT Tag FROM Project", which matches the row. It is not in `_documentation.md`. [vanilla-confirmed 1.19.4.1] `common/on_actions/12_wuw_on_actions.txt`.
<!-- kit:end id="onaction-special-projects" -->

<!-- kit:begin id="onaction-inventory" at="bottom" -->
## Hook inventory for 1.19.4.1

Where each hook name on this page comes from. Vanilla has 121 distinct hook names in 346 blocks: 85 general names and 36 per-tag names. `_documentation.md` lists 84 names: 74 have a vanilla block under that exact name, the three `_TAG` forms have the 36 per-tag names, and 7 have no vanilla block (first row below). [vanilla-confirmed 1.19.4.1] `common/on_actions/*.txt`, [docs] `common/on_actions/_documentation.md`.

| Group | Names | Source |
| --- | --- | --- |
| Documented, no vanilla block | `on_force_government`, `on_mio_tech_reseach_cancelled`, `on_mio_tech_reseach_completed`, `on_operative_created`, `on_operative_recruited`, `on_recall_volunteers`, `on_ruling_party_change_immediate` (deprecated) | [docs] |
| Vanilla block, not documented | `on_add_history`, `on_call_allies`, `on_join_allies`, `on_project_completion`, `on_unit_leader_promote_from_ranks_green`, `on_unit_leader_promote_from_ranks_veteran`, `on_units_paradropped_in_state` | [vanilla-confirmed 1.19.4.1] |
| Vanilla names that look like typos | `on_subject_annex`, `on_mio_tech_research_cancelled`, `on_mio_tech_research_completed` | [vanilla-confirmed 1.19.4.1] |
| Wiki tables only | `on_stage_coup`, `on_guarantee`, `on_military_access`, `on_offer_military_access`, `on_lend_lease`, `on_incoming_lend_lease`, `on_send_expeditionary_force`, `on_return_expeditionary_forces`, `on_request_expeditionary_forces`, `on_ask_for_state_control`, `on_give_state_control`, `on_peace_proposal`, `on_send_attache`, `on_generate_wargoal` | [docs] and [vanilla-confirmed 1.19.4.1] show none of them (0 files); existence in the engine [unverified] |
| Strings in `hoi4.exe` only | `on_state_owner_changed`, `on_become_faction_member` | [docs] and [vanilla-confirmed 1.19.4.1] show neither (0 files); the exe strings [unverified] |

`13_goe_on_actions.txt` writes the hook `ON_OFFER_JOIN_FACTION` and the effect `IF` in capitals, so vanilla uses both spellings. [vanilla-confirmed 1.19.4.1] `common/on_actions/13_goe_on_actions.txt`. Name matching is therefore probably case-insensitive. [unverified]

Use the documented and vanilla names. Treat the last two groups as unconfirmed until a test run shows the hook firing with a `log` effect.
<!-- kit:end id="onaction-inventory" -->
