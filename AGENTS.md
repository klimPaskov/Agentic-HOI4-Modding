# Repository Guidelines

This file describes how you should read, edit, and extend the [MOD_NAME] codebase.

---

## Placeholder Guide

Replace these placeholders:

- `[MOD_NAME]` = full mod name
- `[MOD_PREFIX]` = script prefix or namespace used by the mod
- `[OFFLINE_WIKI_PATH]` = path to the offline Paradox wiki snapshot
- `[HOI4_VANILLA_PATH]` = path to the vanilla Hearts of Iron IV installation
- `[REFERENCE_MOD_NAME]` = approved large reference mod, if any
- `[DOCS_FOLDER]` = docs folder path, usually `docs/`

---

## 0. Required Reading Before Any Change

### Paradox Wiki

Before you open or edit any [MOD_NAME] file, you must consult the relevant Hearts of Iron IV modding pages from the offline Paradox wiki snapshot in `[OFFLINE_WIKI_PATH]/`.

Rules:

- Treat the offline snapshot as the required wiki reference. Do not access the Paradox wiki on the web.
- Keep the key pages open while you work and treat them as the primary reference for syntax and engine behavior.

Always open at least these core pages from `[OFFLINE_WIKI_PATH]/`:

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

If your task touches some other system, for example GUI, open Interface Modding and Scripted GUI Modding pages. For country creation, national focuses, equipment, divisions, or technology, open the corresponding wiki snapshot page as well. Do not rely on memory when a page exists.

Web access:

- For general web research, use `ddg-search`.
- Do not use any other web browsing tools unless the repository instructions explicitly allow them.

### Vanilla References

Use HOI4 vanilla as the main example set.

- The vanilla game directory is available at  
  `[HOI4_VANILLA_PATH]`

- Vanilla Hearts of Iron IV includes official documentation files, often in markdown.
  - The folder `[HOI4_VANILLA_PATH]/documentation` contains documentation files that must be read.
  - Vanilla game files may also include documentation files in other folders. These documentation files must be consulted when they exist for the systems you touch.
  - Treat vanilla documentation as more authoritative, more complete, and more up to date than the Paradox wiki.
  - The Paradox wiki must still be consulted in parallel. Both sources are required.
  - Do not rely on memory or assumptions when documentation files exist. Read them directly.

- When implementing a mechanic, event, decision, or UI, find at least one vanilla precedent if possible and mirror its structure.

If [MOD_NAME] already has a pattern for the same thing, follow that over vanilla for consistency, but still inspect a vanilla implementation.

### Mod References Beyond Vanilla

If vanilla examples are insufficient or unclear, you are allowed to inspect well known large mods for additional reference.

- `[REFERENCE_MOD_NAME]` is approved as a reference mod for structure, patterns, and edge case handling.
- You may read `[REFERENCE_MOD_NAME]` files to understand how similar systems are implemented when vanilla does not provide a clear or complete example.

---

## 1. Coding Style

Clausewitz script is picky. Follow these rules strictly.

1. Indent script blocks with tabs. Use lowercase keys and snake_case for variables and script names.
2. Never use `<=` or `>=`. They are not supported and will break the game.
   - Use `check_variable` with `compare = greater_than_or_equals` or `compare = less_than_or_equals` instead.
   - This does not mean you should always use the long variant. Use the long variant only when necessary. Default to shortened versions for readability, meaning you are allowed to use `<` and `>`.
3. Remove magic numbers. The system must rely on variables so that tuning happens in one place. Everything must be dynamic. Never hardcode anything unless the repository rules explicitly require it.
4. Temporary variables do not have a scope, so `ROOT.my_temp_var` or `PREV.my_temp_var` will do nothing. Only normal variables have a scope.
5. Try to use loops when they improve clarity and avoid repetition.
6. Use flags for true or false state, not numeric variables that only ever take 0 or 1.
7. Move repeated logic into `scripted_effects` or `scripted_triggers`.
8. `on_weekly`, `on_daily`, `on_monthly`, and similar on actions iterate over all countries by default unless a narrower scope is explicitly required. But these on actions can slow down the game.
   - Only use these types of on actions when the user explicitly asks for it.
   - If you believe a whole world iteration is required, stop and ask for permission. Do not implement it until permission is granted.
9. Constants `@MY_CONSTANT` cannot cross file boundaries. They are file scoped.
   - Prefer HOI4 `script_constants` for shared tuning values. They are global, improve readability, and have no runtime cost.
   - Required vanilla docs:
     - `[HOI4_VANILLA_PATH]/documentation/script_concept_documentation.md` and its Script Constants section
     - `[HOI4_VANILLA_PATH]/common/script_constants/documentation.md`
   - Where to put them:
     - `common/script_constants/` only
     - Create multiple files by subsystem
   - When to use them:
     - Use for groups of related constants such as tiers, thresholds, AI tuning tables, ratio ladders, and similar values.
     - Use for values referenced across multiple files where `@` would force duplication.
   - Important limitation: `script_constants` cannot be used everywhere. Unsupported fields will throw errors. In that case, use `@` constants.
   - Prefer the explicit fixed point access: `constant:category.key`
10. Use event targets `event_target:` to persist a scope pointer across blocks or events when variables or scopes alone are insufficient.
    - Required references:
      - `[OFFLINE_WIKI_PATH]/Data structures - Hearts of Iron 4 Wiki.md`
      - `[HOI4_VANILLA_PATH]/documentation/effects_documentation.md`
      - `[HOI4_VANILLA_PATH]/documentation/triggers_documentation.md`
    - Prefer regular event targets `save_event_target_as` for short lived chains.
    - Use global event targets `save_global_event_target_as` only when persistence beyond a single chain is required, and clean them up afterwards.
    - Use them as scopes or targets with `event_target:my_target`.
    - In localisation, when using an event target as a localisation scope namespace, do not include the `event_target:` prefix.
11. Do not use unary `-` on variable tokens such as `value = -my_var`. Negate via `multiply_*_variable` first.
12. If an effect or trigger does not accept dynamic values, use `meta_effect` or `meta_trigger` with `text = { ... }` to inject computed variables/localisation into otherwise static fields.
    - meta effects can be used in all sorts of creative ways, for example: `my_scripted_effect_[ID] = yes`, so you can even choose a scripted effect dynamically. Meta effects are very powerful and useful.
13. Prefer reusable dynamic scripted effects or scripted triggers for complex or dynamic logic.
    - First check existing dynamic effects in (in `common/scripted_effects/[MOD_PREFIX]_dynamic_effects.txt`) and use them instead of duplicating logic.
    - If no existing effect fits, create a new dynamic effect and document it in (`common/scripted_effects/[MOD_PREFIX]_dynamic_effects.md`) in the same change.
    - Keep effect docs explicit: purpose, scope, inputs, outputs, defaults, and a usage example.
14. If MTTH variables are required to reduce AI or script clutter, especially in `ai_will_do` blocks, use the `hoi4-mtth` skill or documented MTTH guidance before implementing.

### Meta effect example

Meta effects allow you to use non dynamic effects as if they were accepting variables.

```txt
add_equipment_to_stockpile = {
    type = infantry_equipment_2
    amount = eq_amount
}
```

In the effect shown above, the amount of equipment added is dynamic and can be set using the variable `eq_amount`. However, this effect does not let you use a variable as equipment type.

Meta effects let you build effects as text and run them. For example:

```txt
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

```txt
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

```txt
add_equipment_to_stockpile = {
    type = artillery_equipment_2
    amount = eq_amount
}
```

This gives 10 units of `artillery_equipment_2`.

---

## 2. Localisation and UI

Localisation and UI must always be kept in sync with gameplay changes.

1. Localisation files must be encoded as UTF 8 with BOM. Wrong encoding breaks strings in game.
2. When you add or rename anything that appears on screen, update localisation in the same change.
3. Localisation keys:
   - Do not use `:0`.
   - Write keys as `key_name: "Text"` without `0` and without a leading space before the key.
   - Keep key names consistent and readable.
4. Icons and UI assets:
   - Define icons in `interface/...` and keep naming stable.
   - When something needs icons, define them in a correct `.gfx` file.
   - Use placeholder sprites from vanilla files where needed so later they can be replaced with real sprites without changing filenames.
   - Register new UI assets before requesting art so filenames do not need to change later.

---

## 3. Naming and Prefix Rules

Use prefixes only where they are needed.

Add prefixes if a folder is dedicated to [MOD_NAME] files that all share the prefix. Do not add the `[MOD_PREFIX]` prefix to variable names, scripted effects, scripted triggers, or functions unless the surrounding context already uses it consistently.

Prefer short, descriptive names that reflect function and scope.

Unnecessary prefixes make code harder to read and maintain. Keep names clean.

---

## 4. HOI4 Modding Rules Summary

When implementing any new mechanic, follow this checklist:

1. First open the required Paradox wiki pages from `[OFFLINE_WIKI_PATH]/`. Keep Data Structures, Triggers, Effects, Modifiers, and Localisation open while you work.
2. In addition to the Paradox wiki, inspect vanilla files in `[HOI4_VANILLA_PATH]/` and read all necessary documentation, particularly in `[HOI4_VANILLA_PATH]/documentation`.
3. Create a new markdown file in `[DOCS_FOLDER]/` for the mechanic you added. Describe what it does, how it works step by step, and how it interacts with existing systems. Add a section for future plans and extension ideas.
4. In that docs file, list all icons needed for the new features. Write where the sprites should live, which `gfx` file should reference them, and what icon names are used in code and localisation.
5. Plan variables and flags so that values are dynamic and centralised.
6. Avoid unsupported operators and constructs. For example, never use `<=` or `>=`.
7. Use loops, meta effects, or meta triggers if needed to make things dynamic, and use scripted effects or scripted triggers to remove duplication.
8. Reuse existing dynamic scripted effects before writing new bespoke logic. If new dynamic effects or triggers are added, document them in `common/scripted_effects/[MOD_PREFIX]_dynamic_effects.md` in the same change.
9. Keep localisation, icons, and UI definitions aligned with changes in the same edit.
10. When adding any new equipment type, archetype, or category, also update `common/script_enums.txt` and the relevant enum section in the same change.
11. Document each new script file with an overview at the top.
12. Confirm that all decisions, event options, and other visible effects have proper trigger tooltips and effect descriptions.
13. Respect the repository style and naming rules so new content blends with existing [MOD_NAME] code.
14. For systems that touch a larger subsystem, review all related docs and verify integration across events, on_actions, decisions, scripted logic, UI, and localisation.
15. When the user reports an issue after new changes were made, assume the game has already been reloaded. Do not default to restart or reload advice unless the user explicitly says they did not reload. Do not ask for logs unless the user provides them or the repository rules explicitly require them.
16. Fallbacks are never allowed unless the user explicitly approves them.
17. When the user reports that something is wrong and you cannot figure out what exactly, add temporary debug code such as `log = "my debug log"` that exposes the relevant runtime values, and remove every debug line you added once the issue is resolved.

Follow these rules and your changes will be easier to review, safer to merge, and more consistent. If this checklist cannot be satisfied, stop and request more design input instead of guessing.

---

## 6. Git and Worktrees

When the user asks for it, use a separate git worktree for a new session so parallel sessions do not interfere with each other.

The agent may make small frequent commits inside its own worktree during the session, but commits must be meaningful and represent real progress.

When the session is finished, move the result back into the main tree only if there is no overlap with other active worktrees. If there is any conflict risk, stop and leave the merge to the user.

Never run `git push`. The user does that manually.
