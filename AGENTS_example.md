# Repository Guidelines

This file describes how you should read, edit and extend the Chaos Redux codebase.

---

## 0. Required Reading Before Any Change

### Paradox Wiki

Before you open or edit any Chaos Redux file, you must consult the relevant Hearts of Iron IV modding pages from the offline Paradox wiki snapshot in `paradox_wiki/`.

Rules:

- Treat the offline snapshot as the required wiki reference. Do not access the Paradox wiki on the web.
- Keep the key pages open while you work and treat them as the primary reference for syntax and engine behavior.

Always open at least these core pages from `paradox_wiki/`:

- Data structures
- Triggers
- Effects
- Modifiers
- Localisation
- Scopes
- On actions
- Event modding
- Decision modding
- Idea modding
- AI modding

If your task touches some other system, for example for gui, open Interface Modding and Scripted GUI Modding pages. For country creation, national focuses, equipment, divisions or technology, open the corresponding wiki snapshot page(s) from `paradox_wiki/` as well. Do not rely on memory when a page exists.

Web access:

- For general web research, use the `ddg-search` MCP server.
- Do not use any other web browsing tools.

### Vanilla References

Use HOI4 vanilla as the main example set.

- The vanilla game directory is available at  
  `~/projects/Hearts of Iron IV/`

- Vanilla Hearts of Iron IV includes official documentation files (often in markdown).
  - The folder `~/projects/Hearts of Iron IV/documentation` contains markdown documentation files that **must be read**.
  - Vanilla game files may also include documentation files in other folders. These documentation files **must be consulted when they exist** for the systems you touch.
  - Treat vanilla documentation as more authoritative, more complete, and more up to date than the Paradox wiki.
  - The Paradox wiki must still be consulted in parallel. Both sources are required.
  - Do not rely on memory or assumptions when documentation files exist. Read them directly.

- When implementing a mechanic, event, decision or UI, find at least one vanilla precedent (if possible) and mirror its structure.

If Chaos Redux already has a pattern for the same thing, follow that over vanilla for consistency, but still take a look at a vanilla implementation.

### Mod References Beyond Vanilla

If vanilla examples are insufficient or unclear, you are allowed to inspect well known large mods for additional reference.

- Kaiserreich is approved as a reference mod for structure, patterns, and edge case handling.
- You may read Kaiserreich files to understand how similar systems are implemented when vanilla does not provide a clear or complete example.

---

## 1. Coding Style

Clausewitz script is picky. Follow these rules strictly.

1. Indent script blocks with tabs. Use lowercase keys and snake_case for variables and script names.
2. Never use `<=` or `>=`. They are not supported and will break the game.
   - Use `check_variable` with `compare = greater_than_or_equals` or `compare = less_than_or_equals` instead. But this doesn't mean that you should always use the long variant. Use the long variant only when necessary, default to shortened versions for readability, meaning that you are allowed to use `<` and `>`.
3. Remove magic numbers. The system must rely on variables so that tuning happens in one place. Everything must be dynamic, never hardcode anything.
4. Temporary variables don't have a scope, so `ROOT.my_temp_var` or `PREV.my_temp_var` will do nothing. Only normal variables have a scope.
5. Try to use loops when they improve clarity and avoid repetition.
6. Use flags for true or false state, not numeric variables that only ever take 0 or 1.
7. Move repeated logic into `scripted_effects` or `scripted_triggers`.
8. `on_weekly`, `on_daily`, `on_monthly` and similar on actions iterate over all countries by default unless a narrower scope is explicitly required. But these on actions can slow down the game.
   - Only use these types of on actions (which iterate through every country by default) when I explicitly ask for it.
   - If you believe a whole world iteration is required, stop and ask for permission. Do not implement it until permission is granted.
9. Constants `@MY_CONSTANT` cannot cross file boundaries. They are file scoped.
   - Prefer HOI4 `script_constants` for shared tuning values. They are global (available across script files), improve readability, and have no runtime cost (they are injected on load).
   - Required vanilla docs:
     - `~/projects/Hearts of Iron IV/documentation/script_concept_documentation.md` (Script Constants section)
     - `~/projects/Hearts of Iron IV/common/script_constants/documentation.md` (schema + examples)
   - Where to put them:
     - `common/script_constants/` only.
     - Create multiple files by subsystem (chemical warfare, events, settings, etc).
   - When to use them:
     - Use for groups of related constants (tiers, thresholds, AI tuning “tables”, ratio ladders, etc), even if currently only used in one file, if it makes the system clearer and easier to tune.
     - Use for values referenced across multiple files (effects/decisions/events/localisation/etc), where `@` would force duplication or “keep in sync” comments.
   - Important limitation: `script_constants` cannot be used everywhere. Unsupported fields will throw errors. In that case, use `@` constants.
   - Prefer the explicit fixed-point access: `constant:category.key` (e.g. `value = constant:chem_cylinder_ratio.low`).
10. Use event targets (`event_target:`) to persist a scope pointer across blocks/events when variables/scopes alone are insufficient.
    - Required references:
    - `paradox_wiki/Data structures - Hearts of Iron 4 Wiki.md` (Event targets section)
    - `~/projects/Hearts of Iron IV/documentation/effects_documentation.md` (`save_event_target_as`, `save_global_event_target_as`, `clear_global_event_target`, `clear_global_event_targets`)
    - `~/projects/Hearts of Iron IV/documentation/triggers_documentation.md` (`has_event_target`)
    - Prefer regular event targets (`save_event_target_as`) for short-lived chains; they automatically clear when the originating effect chain ends (but do carry into events fired from that chain).
    - Use global event targets (`save_global_event_target_as`) only when you need persistence beyond a single chain/system; they do not auto-clear and must be cleaned up (e.g. `clear_global_event_target = my_target`).
    - Use them as scopes/targets with `event_target:my_target`.
    - Localisation: when using an event target as a localization scope namespace, the `event_target:` prefix is not used (e.g. `[my_target.GetName]`).
11. Do not use unary `-` on variable tokens (e.g. `value = -my_var`); negate via `multiply_*_variable` first.
12. If an effect or trigger does not accept dynamic values, use `meta_effect` or `meta_trigger` with `text = { ... }` to inject computed variables/localisation into otherwise static fields.
    - meta effects can be used in all sorts of creative ways, for example: `my_scripted_effect_[ID] = yes`, so you can even choose a scripted effect dynamically. Meta effects are very powerful and useful.
13. Prefer reusable dynamic scripted effects/triggers for complex/dynamic logic.
    - First check existing dynamic effects (in `common/scripted_effects/chaosx_dynamic_effects.txt`) and use them instead of duplicating logic.
    - If no existing effect fits, create a new dynamic effect and document it in the markdown file of the same name (`common/scripted_effects/chaosx_dynamic_effects.md`) in the same change.
    - Keep effect docs explicit: purpose, scope, inputs/outputs, defaults, side effects, and a usage example.
14. If MTTH (mean time to happen) variables are required to reduce AI/script clutter (especially in ai_will_do blocks) by centralizing weighted logic, use the `hoi4-mtth` skill and follow its MTTH guidance before implementing.

### Meta effect example

Meta effects allow you to use non-dynamic effects (the ones that do not accept modifiers and can only use static tokens or constant values) as if they were accepting variables.

```
add_equipment_to_stockpile = {
    type = infantry_equipment_2
    amount = eq_amount
}
```

In the effect shown above, amount of equipment added is dynamic and can be set using the variable `eq_amount`. However, this effect does not let you use a variable as equipment type. You can not store `infantry_equipment_2` in a variable and use it here.

However, meta effects will let you use variables and scripted localisation within them to build effects as if they were texts and run them. Let's make the previous effect accept equipment type and equipment level as variables stored in `eq_type` and `eq_level`.

```
set_variable = { eq_type = 1 }
set_variable = { eq_amount = 10 }
set_variable = { eq_level = 2 }

meta_effect = {
    text = {
        add_equipment_to_stockpile = {
            type = [EQ_TYPE]_[EQ_LEVEL]
            amount = eq_amount
        }
    }
    EQ_LEVEL = "[?eq_level|.0]"
    EQ_TYPE = "[This.GetEquipmentName]"
}
```

The scripted localisation for the `eq_type` variable goes in a scripted localisation file.

```
defined_text = {
    name = GetEquipmentName
    text = {
        trigger = {
            check_variable = { eq_type = 0 }
        }
        localisation_key = "infantry_equipment"
    }
    text = {
        trigger = {
            check_variable = { eq_type = 1 }
        }
        localisation_key = "artillery_equipment"
    }
}
```

This meta effect takes two arguments.

`[EQ_LEVEL]` is replaced by the integer value of `eq_level`.

`[EQ_TYPE]` is replaced by the result of scripted localisation based on `eq_type`.

The final built effect becomes:

```
add_equipment_to_stockpile = {
    type = artillery_equipment_2
    amount = eq_amount
}
```

This gives 10 units of `artillery_equipment_2`.

---

## 2. Localisation and UI

Localisation and UI must always be kept in sync with gameplay changes.

1. Localisation files must be encoded as **UTF 8 with BOM**. Wrong encoding breaks strings in game.
2. When you add or rename anything that appears on screen, update localisation in the same change.
3. Localisation keys:
   - Do not use `:0`. Write keys as `key_name: "Text"` without `0` and without a leading space before the key.
   - Keep key names consistent and readable. No unnecessary prefixes.
4. Icons and UI assets:
   - Define icons in `interface/...` and keep naming stable.
   - When something needs icons, define them in a correct `.gfx` file. I will provide the sprites myself, you just have to tell me what folder to put them in and with what name.
   - Copy placeholder sprites from vanilla files that match the new gfx definition, so later I can replace them with real sprites easily and that the game would run without complaining about missing sprites.
   - Register new UI assets before requesting art so filenames do not need to change later.

---

## 3. Naming and Prefix Rules

Use prefixes only where they are needed.

Add prefixes if a folder is dedicated to Chaos Redux files that all share the prefix. Do not add the `chaosx` prefix to variable names, scripted effects, scripted triggers or functions unless the surrounding context uses it consistently.
Prefer short, descriptive names that reflect function and scope.

Unnecessary prefixes make code harder to read and maintain. Keep names clean.

---

## 4. HOI4 Modding Rules Summary

When implementing any new mechanic, follow this checklist:

1. First open the required Paradox wiki pages from `paradox_wiki/` (section 0). Keep Data Structures, Triggers, Effects, Modifiers, and Localisation in front of you while you work.
2. In addition to the Paradox wiki, inspect vanilla files in `~/projects/Hearts of Iron IV/` and read all the necessary documentation, particularly in `~/projects/Hearts of Iron IV/documentation`.
3. Create a new markdown file in `docs/` for the mechanic you've added. Describe what it does, how it works step by step and how it interacts with existing systems. Add a section for future plans and your own suggestions on how the mechanic could be extended or made deeper.
4. In that docs file, list all icons needed for the new features. Write where the sprites should live, which `gfx` file should reference them and what icon names are used in code and localisation, so the wiring rules from this file are also clear inside the docs file.
5. Plan variables and flags so that values are dynamic and centralised.
6. Avoid unsupported operators and constructs. For example, never use `<=` or `>=`.
7. Use loops, meta effects/triggers if needed to make things dynamic, and scripted effects or scripted triggers to remove duplication.
8. Reuse existing dynamic scripted effects before writing new bespoke logic. If new dynamic effects/triggers are added, document them in `common/scripted_effects/chaosx_dynamic_effects.md` in the same change.
9. Keep localisation, icons and UI definitions aligned with changes in the same edit.
10. When adding any new equipment type/archetype/category, also update `common/script_enums.txt` (`script_enum_equipment_bonus_type`) in the same change.
11. Document each new script file with an overview at the top. Do it similarly to `chaosx_logic_effects.txt`.
12. Confirm that all decisions and event options or other effects have proper trigger tooltips and effect descriptions.
13. Respect the repository style and naming rules so new content blends with existing Chaos Redux code.
14. For systems that touch or are related to bio/chemical warfare, review any related docs, and verify integration across events, on_actions, decisions, contamination effects, scripted logic, etc.
15. When the user reports an issue after new changes were made, assume the game has already been reloaded. Do not default to restart/reload advice unless the user explicitly says they did not reload. Do not ask for, request, or search for logs. If the user did not paste any error lines, treat it as having no error lines to use. Do not tell the user to run in-game validation. Assume they will always verify changes in a live session.
16. Fallbacks are never allowed and MUST ALWAYS be discussed with the user.
17. When the user reports that something is wrong and you can't figure out what exactly, then add temporary debug code (for example: `log = "my debug log"`) that exposes the relevant runtime values needed to understand the issue, and remove every debug line you added once the issue is resolved.

Follow these rules and your changes will be easier to review, safer to merge and more consistent with the rest of the project.
If this checklist cannot be satisfied, stop and request more design input instead of guessing.

---

## 5. Event Integration

For Chaos Redux event implementation, use the repo skill `chaos-redux-events`.

1. Keep the entry event root format `chaosx.nr<ID>.1`.
2. Wire event script, category registration, auto-firing, localisation/name mappings, event log actor mapping, and event details window content together in the same change.
3. If the event has evolutions or world-end branches, wire the log entries, super-event integration, and related localisation in the same change.
4. Keep gameplay files, docs, the event spreadsheet/presentation, and any other details aligned.

---

## 6. Git and Worktrees

When I tell you to, use a separate git worktree for a new session. The agent should create and use its own worktree so parallel sessions do not interfere with each other.

The agent may make small frequent commits inside its own worktree during the session, but commits must be meaningful and represent real progress.

When the session is finished, move the result back into the main tree only if there is no overlap with other active worktrees. If there is any conflict risk, stop and leave the merge to the user.

Never run `git push`. The user does that manually.
