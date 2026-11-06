---
name: hoi4-scripted-triggers-effects
description: Use when defining, calling, scoping, tooltipping or documenting a reusable HOI4 scripted effect or scripted trigger, or when debugging scripted_effects and scripted_triggers files.
---

# HOI4 Scripted Triggers and Effects

Checklist for `common/scripted_effects/` and `common/scripted_triggers/`: define, feed, scope, call, tooltip and document reusable logic. Weighted values belong to `hoi4-mtth`, meta effects to `hoi4-events` (`references/meta-effects.md`) and `common/on_actions/` hooks to `hoi4-on-actions`. The `hoi4-scripted-system-architect` agent and the main agent use it when designing a helper.

Tags: `[vanilla-confirmed 1.19.4.2]` was checked in the installed game (counts come from a name-match scan of `common/`, `events/`, `history/`, `interface/`, `map/`). `[docs]` comes only from game documentation or the kit wiki (snapshot 1.19.4.1). `[unverified]` was not checked. Kit rules name their `CLAUDE.md` section or the `hoi4-project-rules` reference that holds them.

## Source map

The installed `documentation/` has no page on scripted effects or triggers and neither folder ships a documentation file. [vanilla-confirmed 1.19.4.2]

| Topic | Wiki | Installed game |
| --- | --- | --- |
| Definition, call form | [effects](../../../hoi4_wiki/effects.md#scripted-effects), [triggers](../../../hoi4_wiki/triggers.md#scripted-triggers) | headers of `00_scripted_effects.txt` and `00_scripted_triggers.txt` |
| Inputs, variables | [variable types](../../../hoi4_wiki/data_structures.md#variable-types), [unset values](../../../hoi4_wiki/data_structures.md#additional-usage) | `lerp` (`SWE_scripted_effects.txt`), `instantiate_collaboration_government` |
| Scopes | [dual scopes](../../../hoi4_wiki/scopes.md#dual-scopes), [PREV usage](../../../hoi4_wiki/scopes.md#prev-usage) | `ROOT_inherit_current_scope_wars_effect`, `can_ROOT_get_wargoal_on_THIS` |
| Flow control | [if statements](../../../hoi4_wiki/effects.md#if-statements), [trigger flow](../../../hoi4_wiki/triggers.md#flow-control-tools) | `## if` entries in both documentation files |
| Tooltips | [tooltip manipulation](../../../hoi4_wiki/effects.md#tooltip-manipulation) | tooltip and `hidden_*` entries in both documentation files |
| Load order | [loading files](../../../hoi4_wiki/modding.md#loading-files) | none |
| Engine hook triggers | [diplomacy](../../../hoi4_wiki/triggers.md#diplomacy-scripted-triggers), [resistance](../../../hoi4_wiki/triggers.md#resistance-initiation-triggers) | `diplomacy_scripted_triggers.txt`, `00_diplo_action_valid_triggers.txt`, `00_resistance_initiate_triggers.txt` |
| Debugging | [debug loop](../../../hoi4_wiki/troubleshooting.md#a-debugging-loop-for-scripted-changes), [console](../../../hoi4_wiki/console_commands.md#modding-useful-commands) | `log` and `print_variables` entries, `zz_debug_effects.txt` |

## Checklist

1. Define `name = { <body> }` at the top level of a `.txt` file in `common/scripted_effects/` or `common/scripted_triggers/`, with the body written as inline script. [vanilla-confirmed 1.19.4.2]
2. Call an effect as `name = yes` and a trigger as `name = yes` or `name = no`, as vanilla does in 7,431 effect calls (all `= yes`) and 12,313 trigger calls (902 `= no`). [vanilla-confirmed 1.19.4.2]
3. Name for function and scope and add the mod prefix only where the surrounding files use it (CLAUDE.md section 3), as vanilla writes scope into names such as `can_ROOT_get_wargoal_on_THIS`. [vanilla-confirmed 1.19.4.2]
4. Pass no arguments, because no vanilla call passes a block and `$NAME$` appears in no scripted effect or trigger file. The "inputs" of `hoi4-project-rules` coding-style 13 are variables. [vanilla-confirmed 1.19.4.2]
5. Set each input in a variable just before the call and list it in the header, as `lerp` reads `lerp_x`, `lerp_a` and `lerp_b` and `instantiate_collaboration_government` reads `country_to_initiate`. [vanilla-confirmed 1.19.4.2]
6. Expect a temp variable set before the call to reach the body, and one created inside the body to possibly vanish after the call. [docs]
7. Return results in a regular variable of the calling scope, as `lerp` writes `lerp_result`. [vanilla-confirmed 1.19.4.2]
8. Give every input a default, because an unset variable reads 0, using the `?` fallback (`var_name?100`) or an `if` on `has_variable`. [docs] Vanilla writes `args^0?0.1` in `zz_debug_effects.txt`. [vanilla-confirmed 1.19.4.2]
9. Set and read regular inputs in the scope the body runs in, because only regular variables are scoped and `ROOT.my_temp` does nothing (`hoi4-project-rules` coding-style 4). [docs]
10. Read tuning numbers from `constant:` script constants or variables (`hoi4-project-rules` coding-style 3, 9). Use `meta_effect` only for a field that rejects variables (`hoi4-events`).
11. Treat the body as running in the caller's scope, with ROOT, THIS, PREV and FROM as in the caller, as `HUN = { ROOT_inherit_current_scope_wars_effect = yes }` shows by declaring wars for the caller's ROOT. A definition cannot declare a scope, so say it in the header comment and the name, as vanilla's `#State scope` comments do. [vanilla-confirmed 1.19.4.2]
12. Enter the right scope first, for example `owner = { name = yes }` from a state, because a native command in an unsupported scope logs `Invalid Scope, supported: X, provided: Y` and a trigger test read false. [docs]
13. Read an engine hook trigger's file header before overriding it. `should_initiate_resistance` runs in state scope with FROM the occupier, `DIPLOMACY_*_ENABLE_TRIGGER` has ROOT as initiator and FROM as target, and `is_diplomatic_action_valid_*` reverses that. [vanilla-confirmed 1.19.4.2]
14. Keep only triggers in a scripted trigger. No vanilla one calls a scripted effect or uses `hidden_effect`, and 2 use `set_temp_variable`, which the docs list as a trigger. [vanilla-confirmed 1.19.4.2] [docs]
15. Let a scripted effect call other scripted effects (273 vanilla definitions do) and scripted triggers (99 do). [vanilla-confirmed 1.19.4.2]
16. Branch with `if`, `else_if` and `else` and put `limit` only inside them or an iterator. None of vanilla's 2,509 definitions has a body-level `limit`, and 378 effects and 10 triggers use `else_if`. [vanilla-confirmed 1.19.4.2]
17. Remember that a trigger `if` whose `limit` fails returns true, so a body of only `if` blocks is true when no limit matches. [docs]
18. Keep call chains short and never recurse, because vanilla's deepest chains are 5 effects (from `SOV_check_for_a_new_purge_effect`) and 3 triggers, with no self-call or cycle. [vanilla-confirmed 1.19.4.2]
19. Bound loops, because loop effects stop after `MAX_EFFECT_ITERATION` = 1000 iterations (`hoi4-project-rules` coding-style 15). [vanilla-confirmed 1.19.4.2]
20. Look a new name up in vanilla and the mod before defining it, with `hoi4.source_lookup` for exact definitions and override status (`CLAUDE.md` section 0).
21. Expect the later-evaluated definition of a duplicate trigger name to win (ASCII order), a mod file at a vanilla path to replace that whole file, and `replace_path` on `common/scripted_triggers` to drop the hook triggers. [docs] Vanilla ships `has_soviet_tribute` twice (identical) and an empty `on_daily` effect twice, so no pair shows a winner. [vanilla-confirmed 1.19.4.2]
22. Never name a scripted trigger like a native trigger, because `hoi4.exe` holds the error "Scripted trigger uses same name as coded trigger". [vanilla-confirmed 1.19.4.2]
23. Hide a body's effects with `hidden_effect` and describe them with `custom_effect_tooltip`, as `instantiate_collaboration_government` does (285 vanilla effects use the first, 398 the second). `effect_tooltip` shows effects without running them and `custom_override_tooltip` runs them under one custom tooltip. [vanilla-confirmed 1.19.4.2] [docs]
24. Wrap implementation-only checks in `hidden_trigger` (32 vanilla triggers) and give one readable line with `custom_trigger_tooltip` (215), as vanilla's diplomacy header advises. The docs call it an alias of `custom_override_tooltip`. [vanilla-confirmed 1.19.4.2] [docs]
25. Name the tooltip key like the trigger and add a `_NOT` key for `NOT` and `= no`, as `is_controlled_by_ROOT_or_ally` and `is_controlled_by_ROOT_or_ally_NOT` do. [vanilla-confirmed 1.19.4.2] [docs]
26. Do not point `PREV` at an `every_` or `any_` scope inside a visible body, because a tooltip shows only the first scope. Hide the body and describe it. [docs]
27. Open each file with an overview comment (`hoi4-project-rules` mechanic-checklist item 11) and document every new dynamic effect or trigger in `docs/<mod_prefix>_dynamic_effects.md` in the same change, reusing an entry before adding one (Coding Style 13). The comment above the definition repeats the entry, as vanilla `lerp` does:

```
### name_of_effect
Purpose: what it does in one line.
Scope: country (ROOT = ..., FROM = ...)
Inputs and defaults: temp variable `x` (type, unit, value when unset)
Outputs: variable `y` in the calling scope
Side effects: flags, variables, events, tooltip text
Example: set_temp_variable = { x = 5 } name_of_effect = yes
```

## Silent failures

- An unset input, or one set in a different scope, reads 0 and the body runs on zero (rules 8, 9). A temp variable made in the body may be gone after the call (rule 6).
- A trigger made of `if` blocks is true when no limit matches (rule 17).
- An undefined or misspelled name logs `Unknown effect-type` or `Unknown trigger-type` in `error.log`. [docs]
- A duplicate name or a same-path file replaces the older definition (rule 21).
- `<=`, `>=` and `= -variable` break or do nothing (`hoi4-project-rules` coding-style 2, 11).
- A loop stops at 1000 iterations (rule 19).
- `hidden_effect` hides side effects, so the `custom_effect_tooltip` text must state them (`hoi4-project-rules` mechanic-checklist item 12).

## Validation

- `hoi4.script_validate` in file mode checks bodies under the scope the file fixes, treats the mod's own scripted effects and triggers as known commands, and reports `checksPerformed`, `KNOWN_MISTAKE_*`, unresolved helpers and unchecked argument blocks. It does not prove that the caller's scope fits, that inputs are set, tooltip text, parameter semantics or execution. [docs] `docs/systems/hoi4_agent_tools_mcp_integration.md`
- `python -B .tools/check.py quick` runs `script-rules`, a lexical scan of `common/`, `events/` and `history/` for `<=`, `>=`, `= -token` and `§` or `£` in scripted localisation. It checks no scopes, names, calls or tooltips.
- `hoi4.source_lookup` shows whether a name is defined or overridden in vanilla, DLC and mod layers and suggests near misses. It proves existence, not scope fit.
- Debug aids that exist: `log = "..."` (effect and trigger, to `game.log`), `print_variables`, `debug = yes` in `meta_effect` and `meta_trigger`, console commands `effect` and `trigger` (`<tag> name`), and `d_` effect names, which become console commands. [docs] The `d_` rule is also [vanilla-confirmed 1.19.4.2].
- Remove temporary `log` lines when done (`hoi4-project-rules` mechanic-checklist item 18). Game runs belong to `hoi4-live-playtest` or the user (`hoi4-project-rules` mechanic-checklist item 15).

## Unverified or open points

- Whether the engine accepts `$NAME$` arguments in a call block, and what a missing or unused one does. [unverified]
- Which definition wins for two scripted effects with one name, across files or mods. The wiki states the rule for triggers only. [unverified]
- Whether one name may be both an effect and a trigger (vanilla shares none), and whether `name = no` is valid for an effect. [unverified]
- What the engine does after the "same name as coded trigger" error, any nesting or recursion limit, and whether a body in the wrong scope fails like a native command. [unverified]
- Whether `save_event_target_as` inside a body is visible to the caller afterwards. [unverified]
- Calling a scripted effect by a built name (`name_[ID] = yes` in `meta_effect`) has no vanilla precedent. Vanilla's `meta_effect` builds idea names. [unverified]
- Whether a localisation key named like a scripted trigger is used automatically, and what a missing `_NOT` key shows. [unverified]
