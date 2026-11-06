---
name: hoi4-on-actions
description: Use when adding or reviewing HOI4 on_actions, meaning common/on_actions hooks such as on_startup, on_daily_TAG, on_weekly, on_monthly, random_events and on_declare_war.
---

# HOI4 On Actions

This skill covers hooking script to engine events through `common/on_actions/`: file layout, block shape, scopes, the iterating hooks, per-tag hooks and validation. `hoi4-events` owns the events a hook fires, `hoi4-scripted-triggers-effects` owns the helper effects and triggers a hook calls, and `hoi4-decisions-missions` owns decisions and missions (no hook exists for them, see rule 25).

`GAME` is the installed game folder named in `CLAUDE.md` (build 1.19.4.2). `[vanilla-confirmed 1.19.4.2]` means read in the installed script. `[docs]` means only a document says it (the game's `documentation/` and `_documentation.md`, or the wiki snapshot written for 1.19.4.1). `[unverified]` means not confirmed. Installed files beat the wiki.

## Source map

| Topic | Wiki (`hoi4_wiki/`) | Installed |
| --- | --- | --- |
| File shape, merging, mod override | [file example](../../../hoi4_wiki/on_actions.md#file-example), [general rules](../../../hoi4_wiki/mod_structure.md#general-rules) | `GAME/common/on_actions/*.txt` |
| Hook list, per-tag hooks | [general hooks](../../../hoi4_wiki/on_actions.md#general-on-actions), [hook inventory](../../../hoi4_wiki/on_actions.md#hook-inventory-for-11941) | `GAME/common/on_actions/_documentation.md` (dated 2024-11) |
| Scopes (ROOT, FROM, PREV) | [politics](../../../hoi4_wiki/on_actions.md#politics), [diplomacy and war](../../../hoi4_wiki/on_actions.md#diplomacywar), [states](../../../hoi4_wiki/on_actions.md#states), [PREV usage](../../../hoi4_wiki/scopes.md#prev-usage) | comment above each hook in `00_on_actions.txt` and the DLC files |
| Firing events | [events and on actions](../../../hoi4_wiki/event_modding.md#integration-with-on-actions) | `GAME/documentation/effects_documentation.md` |
| Validation | none | [MCP integration](../../../docs/systems/hoi4_agent_tools_mcp_integration.md), [.tools README](../../../.tools/README.md) |

## Checklist

1. Put hooks in `common/on_actions/<name>.txt`, one root `on_actions = { }` block per file. [vanilla-confirmed 1.19.4.2] (17 vanilla files)
2. Give the mod file a new name, because the same file name as a vanilla file overwrites that whole vanilla file and its hooks. [docs] mod_structure general rules
3. Hooks of the same name in different files add up: vanilla defines `on_startup` in 14 files and `on_state_control_changed` in 15, each adding its own work. [vanilla-confirmed 1.19.4.2] A wiki test ran `on_startup` from three mod files. [docs] (wiki: game-tested 1.19.4.1)
4. A hook block holds only `effect = { }` and `random_events = { }`, never bare effects. All 346 vanilla hook blocks do this, often with several `effect` blocks (119 blocks) or both keys (`on_nuke_drop`). [vanilla-confirmed 1.19.4.2]
5. Put conditions inside `effect` as `if = { limit = { } }`, because no vanilla hook uses a hook-level `trigger`, `limit`, `fire_only_once` or `random_on_action`. [vanilla-confirmed 1.19.4.2]
6. `random_events` lines are `weight = event_id`, and `weight = 0` fires nothing. `on_justifying_wargoal_pulse` ends with `17000 = 0` under the comment "triggered daily, so make sure there is a sink somewhere not firing events". [vanilla-confirmed 1.19.4.2]
7. Each `random_events` block picks one entry in proportion to its weight, and an event whose own `trigger` is false cannot be picked. [docs] Several blocks in one hook are normal (`on_new_term_election` has three in `00_on_actions.txt`). [vanilla-confirmed 1.19.4.2]
8. Vanilla events fired from `random_events` carry `is_triggered_only = yes` and a `trigger` that reads the hook's scopes (`war_justification.1` reads FROM). [vanilla-confirmed 1.19.4.2] `events/WarJustification.txt`
9. `random_events` is never used inside `effect` in vanilla. Inside `effect` fire events with `country_event`, `news_event` or `state_event`, and add `hours`, `days`, `months`, `random_hours` or `random_days` for a delay. [vanilla-confirmed 1.19.4.2] [docs] `effects_documentation.md`
10. `_documentation.md` gives scopes only for the three peace conference hooks (ROOT winner, FROM loser, for every pair). [docs] Every other hook's scope is the comment above it in vanilla, for example `on_state_control_changed`: ROOT new controller, FROM old controller, FROM.FROM the state. Read that comment before using FROM. [vanilla-confirmed 1.19.4.2]
11. `on_peaceconference_ended` is described two ways: "ROOT - country that just went to peace" in `00_on_actions.txt` and `07_nsb`, and ROOT winner with FROM loser in the other files, so log both before depending on one. [vanilla-confirmed 1.19.4.2]
12. Most country hooks have ROOT as the default scope, but `on_naval_invasion` and `on_paradrop` default to the invaded state with ROOT the invading country, so wrap country effects in `ROOT = { }`. Unit leader hooks default to the leader with FROM the owner country (`on_army_leader_daily`). Some hooks add PREV: the ace hooks say "FROM = our ace, PREV = enemy ace". [vanilla-confirmed 1.19.4.2]
13. `on_startup` has no default scope (vanilla: "Not run on a specific country"), so scope into a country, a state or `every_country` first. `country_event` is COUNTRY scope only. [vanilla-confirmed 1.19.4.2] [docs]
14. `on_startup` fires at the start of a new game only, never on loading a save, and hooks do not fire for effects run in history files. [docs] Vanilla adds a weekly hook that "backfills saves made before the list existed". [vanilla-confirmed 1.19.4.2] `04_mtg_on_actions.txt`
15. Generic `on_daily`, `on_weekly` and `on_monthly` run once per country with ROOT as that country. Vanilla's `on_daily` comment: "Only signatories are checked, so this is a handful of countries a day rather than every tag in the game". [vanilla-confirmed 1.19.4.2] An effect such as `GER = { add_political_power = 1 }` inside one runs about 100 times a day. [docs]
16. House rule, repeated exactly from rule 8 of `hoi4-project-rules/references/coding-style.md` (summarized in `CLAUDE.md` section 1), and it requires explicit user permission:
    > `on_weekly`, `on_daily`, `on_monthly` and similar on actions iterate over all countries by default unless a narrower scope is explicitly required. `on_daily_TAG` are allowed.
    > - Only use these types of on actions (which iterate through every country by default) when the user explicitly asks for it.
    > - If you believe a whole world iteration is required, stop and ask for permission. Do not implement it until permission is granted.
17. Per-tag hooks write a real tag into the name (`on_daily_GER`, `on_weekly_GER`, `on_monthly_GER`) and run in that country's scope: `on_daily_GER` reads `surrender_progress` directly in its `limit`. Vanilla has 6 daily, 9 weekly and 21 monthly tags. [vanilla-confirmed 1.19.4.2] They run only while the country exists. [docs]
18. A wrong tag is reported as "ZZZ is not a valid tag of on_daily" and the hook never fires. [docs] (wiki: game-tested 1.19.4.1) The daily, weekly and monthly messages are strings in `hoi4.exe`. [vanilla-confirmed 1.19.4.2]
19. There is no yearly hook. `_documentation.md` and vanilla define none, and `00_on_actions.txt` holds only the commented-out `#on_bi_yearly_pulse` and `#on_five_year_pulse`, so count months in a variable from a per-tag hook. [vanilla-confirmed 1.19.4.2]
20. `on_army_leader_daily` fires each day per army leader [docs] and `on_justifying_wargoal_pulse` daily while a wargoal is justified. [vanilla-confirmed 1.19.4.2] Ask the user first for work that grows with leaders or wargoals.
21. Guard a one-time reaction with a global or country flag, since a hook fires on every occurrence of its engine event. [docs] `fire_only_once` is an event key, not a hook key.
22. No effect in `effects_documentation.md` fires a named on_action. Only `turn_operative` mentions one: it fires `on_operative_death`, and the hook "might execute immediatly, before any effect listed after". [docs] Share logic through a `scripted_effect` that the hook calls, as `09_aat_on_actions.txt` does with `DEN_puppet_on_action_effects`. [vanilla-confirmed 1.19.4.2]
23. The wiki says `hold_election` fires `on_new_term_election` and `set_politics` fires `on_government_change`, but the game documentation for `hold_election` says only "Immediately holds an election". [docs] wiki only
24. Use only hook names that `_documentation.md` or a vanilla block shows. Vanilla also ships `on_subject_annex` beside the documented `on_subject_annexed`, so that block probably never runs. [vanilla-confirmed 1.19.4.2]
25. No hook exists for focus completion, decisions, missions, ideas or technology completion (the only research hooks are MIO ones), so put such effects in the focus, decision or event itself. [vanilla-confirmed 1.19.4.2]

## Silent failures

- Hook names found only in wiki tables (`on_stage_coup`, `on_guarantee`, `on_lend_lease`, `on_generate_wargoal` and others in the hook inventory) have no vanilla block and no `_documentation.md` entry. Whether the engine knows them is [unverified].
- Documented but never defined in vanilla: `on_recall_volunteers`, `on_force_government`, `on_operative_created`, `on_operative_recruited`, deprecated `on_ruling_party_change_immediate`. `_documentation.md` spells `on_mio_tech_reseach_completed` and `_cancelled` with "reseach", vanilla blocks use "research". [vanilla-confirmed 1.19.4.2]
- `on_join_faction` does not fire for `add_to_faction`, so use `on_offer_join_faction`. [vanilla-confirmed 1.19.4.2] vanilla comment in `00_on_actions.txt`
- `on_puppet` is for puppeting in a peace conference (vanilla comment), so a `puppet` effect does not reach it. [vanilla-confirmed 1.19.4.2] The effect part is [docs].
- A daily pulse hook without a `0` sink can fire an event every day, and a `random_events` entry whose `trigger` is false fires nothing. [vanilla-confirmed 1.19.4.2]

## Validation

- `hoi4.script_validate` with the on_actions file `path` checks every effect and trigger body under the scope the file's structure fixes, and knows the mod's own scripted effects and triggers. A true result covers only its `checksPerformed` and does not establish parameter semantics or game execution. [docs] MCP integration. Whether it flags an unknown hook name or a wrong FROM is [unverified].
- `python -B .tools/check.py quick --paths common/on_actions/<file>.txt` runs `script-rules` (lexical: `<=`, `>=`, unary minus, scans `common/`) and `script-validate` (skipped with a notice when HOI4 Agent Tools cannot start, unresolved commands are warnings). Neither runs the game. [docs] .tools README
- Static checks you can do yourself: hook name against `_documentation.md` and the vanilla files, hook-level keys limited to `effect` and `random_events`, tags valid, every `random_events` event defined with `is_triggered_only = yes`.
- Proof that a hook fires needs game output. Put `log = "text"` in the hook (documented: prints to game.log) and ask the player to run it, because agents do not launch the game. Until then report the hook as statically checked only. [docs] `effects_documentation.md`

## Unverified or open points

- Whether a second same-name block in one file runs. Vanilla does it (`on_startup` twice in `00_on_actions.txt`, `on_weekly_SWE` twice in `09_aat_on_actions.txt`), so prefer one block per hook per file. [unverified]
- Run order of several `effect` blocks, blocks in several files and `effect` against `random_events`. The wiki test used file names a, b, c, so name order and load order are not separated. [unverified]
- Whether a hook-level `trigger` or `limit` is rejected or ignored, and whether an unknown hook name is logged. [unverified]
- Scopes of hooks with no comment and no documentation (`on_recall_volunteers`, `on_force_government`). [unverified]
- Hook name case: vanilla writes `ON_OFFER_JOIN_FACTION` and the wiki test ran `ON_STARTUP`. Keep lowercase. [unverified]
