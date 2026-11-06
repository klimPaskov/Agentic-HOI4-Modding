# Project rules: Coding style

Part of the [hoi4-project-rules](../SKILL.md) skill. `CLAUDE.md` summarizes section 1. Read before writing or reviewing any Clausewitz script.

In this file `GAME` is the vanilla Hearts of Iron IV folder, `WORKSHOP` the Workshop content folder and `PREFIX` the mod's script prefix. `CLAUDE.md` names all three.

## 1. Coding Style

Clausewitz script is picky. Follow these rules strictly.

Markdown prose must not be hard-wrapped in the middle of a sentence. Keep each sentence on one physical line and place line breaks only between sentences or paragraphs.

1. Indent script blocks with tabs. Use lowercase keys and snake_case for variables and script names.
2. Never use `<=` or `>=`. They are not supported and will break the game.
   - Use `check_variable` with `compare = greater_than_or_equals` or `compare = less_than_or_equals` instead. But this doesn't mean that you should always use the long variant. Use the long variant only when necessary, default to shortened versions for readability, meaning that you are encouraged to use `<` and `>`.
3. Remove magic numbers. The system must rely on variables so that tuning happens in one place. Everything must be dynamic, never hardcode anything.
4. Temporary variables don't have a scope, so `ROOT.my_temp_var` or `PREV.my_temp_var` will do nothing. Only normal variables have a scope.
5. Try to use loops when they improve clarity and avoid repetition.
6. Use flags for true or false state, not numeric variables that only ever take 0 or 1.
7. Move repeated logic into `scripted_effects` or `scripted_triggers`.
8. `on_weekly`, `on_daily`, `on_monthly` and similar on actions iterate over all countries by default unless a narrower scope is explicitly required. `on_daily_TAG` are allowed.
   - Only use these types of on actions (which iterate through every country by default) when the user explicitly asks for it.
   - If you believe a whole world iteration is required, stop and ask for permission. Do not implement it until permission is granted.
9. Constants `@MY_CONSTANT` cannot cross file boundaries. They are file scoped.
   - Prefer HOI4 `script_constants` for shared tuning values. They are global (available across script files), improve readability, and have no runtime cost (they are injected on load).
   - Script constants are the preferred tuning source, but not every effect field parses `constant:` tokens. For duration fields that reject constants, such as `days =` inside timed flags, assign the constant to a normal or temporary variable first and pass that variable to `days =`.
   - Required vanilla docs:
     - `GAME/documentation/script_concept_documentation.md` (Script Constants section)
     - `GAME/common/script_constants/documentation.md` (schema + examples)
   - Where to put them:
     - `common/script_constants/` only.
     - Create multiple files by subsystem, such as events, settings, UI, or country systems.
   - When to use them:
     - Use for groups of related constants (tiers, thresholds, AI tuning “tables”, ratio ladders, etc), even if currently only used in one file, if it makes the system clearer and easier to tune.
     - Use for values referenced across multiple files (effects/decisions/events/localisation/etc), where `@` would force duplication or “keep in sync” comments.
   - Important limitation: `script_constants` cannot be used everywhere. Unsupported fields will throw errors. In that case, use `@` constants.
   - Prefer the explicit fixed-point access: `constant:category.key` (e.g. `value = constant:system_ratio.low`).
10. Use event targets (`event_target:`) to persist a scope pointer across blocks/events when variables/scopes alone are insufficient.
    - Required references:
    - `hoi4_wiki/data_structures.md` (Event targets section)
    - `GAME/documentation/effects_documentation.md` (`save_event_target_as`, `save_global_event_target_as`, `clear_global_event_target`, `clear_global_event_targets`)
    - `GAME/documentation/triggers_documentation.md` (`has_event_target`)
    - Prefer regular event targets (`save_event_target_as`) for short-lived chains, they automatically clear when the originating effect chain ends (but do carry into events fired from that chain).
    - Use global event targets (`save_global_event_target_as`) only when you need persistence beyond a single chain/system, they do not auto-clear and must be cleaned up (e.g. `clear_global_event_target = my_target`).
    - Use them as scopes/targets with `event_target:my_target`.
    - Localisation: when using an event target as a localization scope namespace, the `event_target:` prefix is not used (e.g. `[my_target.GetName]`).
11. Do not use unary `-` on variable tokens (e.g. `value = -my_var`), negate via `multiply_*_variable` first.
12. If an effect or trigger does not accept dynamic values, use `meta_effect` or `meta_trigger` with `text = { ... }` to inject computed variables/localisation into otherwise static fields. A worked example is in `.claude/skills/hoi4-events/references/meta-effects.md`.
    - meta effects can be used in all sorts of creative ways, for example: `my_scripted_effect_[ID] = yes`, so you can even choose a scripted effect dynamically. Meta effects are very powerful and useful, use them often.
    - When only one part of a flag or variable name is dynamic, prefer targeting over a meta effect: `set_country_flag = my_flag_@PREV` appends that country's tag (only `@ROOT`, `@PREV`, `@FROM`, and `@THIS`, one per name), and `my_var_@var:id` or `my_var_@PREV` keys a variable by a stored value or scope. The wiki's Data structures page describes targeting as faster and more readable than meta-effect token pasting.
13. Prefer reusable dynamic scripted effects/triggers for complex/dynamic logic.
    - First check existing dynamic effects (in `common/scripted_effects/PREFIX_dynamic_effects.txt`) and use them instead of duplicating logic.
    - If no existing effect fits, create a new dynamic effect and document it in the matching markdown file `docs/PREFIX_dynamic_effects.md` in the same change.
    - Keep effect docs explicit: purpose, scope, inputs/outputs, defaults, side effects, and a usage example.
14. If MTTH (mean time to happen) variables are required to reduce AI/script clutter, use `hoi4-mtth` before implementing and route probability validation through `hoi4_ai_probability_auditor`.
15. Some engine values and triggers fail silently.
    - Read manpower through `manpower_k`, `max_manpower_k`, or `max_available_manpower_k` (values in thousands), or through `has_manpower`. The plain `manpower`, `max_manpower`, and `max_available_manpower` dynamic variables are deprecated and overflow at about 2.1 million.
    - `collection_size` comparisons are inclusive, so `value > 3` means at least 3.
    - `scope_exists` is always true on a variable scope. Validate a stored target with an object-specific check such as `exists = yes` or `country_exists` instead.
    - `while_loop_effect` and `for_loop_effect` stop after 1,000 iterations (`MAX_EFFECT_ITERATION` in vanilla defines), so a loop over a larger set, such as every state, needs a scope iterator or bounded batches.
