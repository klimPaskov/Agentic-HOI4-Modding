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

- For general web research, use your default web search tool. If that fails, then use the fallback `ddg-search` MCP server.

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

- Kaiserreich (1521695605) is approved as a reference mod for structure, patterns, and edge case handling.
- You may read Kaiserreich files to understand how similar systems are implemented when vanilla does not provide a clear or complete example.
- You may read other mod files as well (for example Kaiserredux 2076426030), if you don't find what you are looking for inside Kaiserreich.

### Repo Skills

Use repo skills as required implementation guidance, not as optional notes.

- Use `chaos-redux-events` for Chaos Redux event implementation, event logs, evolutions, event details, documentation, and spreadsheet alignment.
- Use `chaos-redux-event-assets` when an event needs visual assets, icons, flags, portraits, UI art, report images, news images, achievement icons, final DDS files, asset manifests, or sprite handoff notes.
- Use `chaos-redux-frame-animation` when a task needs animated sprites, frame sequences, sprite sheets, GIF previews, animated UI pieces, animated portraits, hover loops, pulse loops, route emblems, or frame-by-frame visual packages. This skill forbids final animation made only by moving, scaling, rotating, warping, blurring, recoloring, or filtering one still image.
- Use `chaos-redux-super-events` when a task creates, updates, researches, or wires a super-event.
- Use `hoi4-focus-trees` before editing national focus trees.
- Use `hoi4-decisions-missions` before editing decisions/missions
- Use `hoi4-mtth` when MTTH logic or weighted timing would reduce clutter or make AI and release logic clearer.
- Use `chaos-redux-subagents` when coordinating custom Codex subagents, routing bounded work, or defining parent/subagent ownership boundaries.
- Use `chaos-redux-improvement-loop` when an implemented or planned mechanic needs recursive depth expansion, spec addenda, improvement handoffs, or checks for shallow, duplicated, generic, disconnected, or low-impact content.

### Subagents

Use project custom Codex agents when a task needs bounded research, asset production, audit, recursive expansion, or documentation work that can be separated from main implementation.

`chaos-redux-subagents` is the detailed source of truth for subagent routing, ownership boundaries, handoff quality, audit cadence, asset routing, super-event routing, and the recursive mechanic expansion loop.

The main agent remains responsible for final implementation, final wiring, final review, validation, and completion claims. Subagents return evidence, files, manifests, spec addenda, patches, or handoff notes depending on the parent-granted mode. The main agent must review their outputs and carry blockers or uncertainty into the final report.

All project custom Codex subagents must be spawned with `fork_context=false`. Do not spawn any project subagent with inherited parent-thread context. If a subagent needs a user correction, task constraint, current implementation status, or prior handoff detail, the parent must pass it explicitly in the subagent prompt or write it into the relevant spec, plan, handoff, or repo file before spawning.

Use these high-level routing rules:

- Use `chaosx_repo_explorer` only when file locations, existing patterns, vanilla references, likely touchpoints, missing-file recovery, or implementation order are unclear. Do not use it for small known-file edits, provided-file edits, direct skill or prompt updates, localisation-only cleanup, asset-only production, or tasks already bounded to exact files. The parent should inspect the known files directly for those cases.
- Use asset subagents for visual production: `chaosx_asset_source_researcher`, `chaosx_generated_event_art`, and `chaosx_icon_artist`.
- When an asset subagent is asked to produce animation, the parent prompt must require `chaos-redux-frame-animation` and must ask for separate generated, sourced, or provided source frames, static fallback, manifest, contact sheet, preview, and `.gfx` or `.gui` handoff.
- Use super-event subagents for specialised research: `chaosx_super_event_text_researcher` and `chaosx_super_event_audio_researcher`.
- Use audit subagents before completion claims: `chaosx_focus_tree_auditor`, `chaosx_decision_mission_auditor`, `chaosx_country_package_auditor`, `chaosx_localisation_auditor`, and `chaosx_event_completion_auditor`.
- Use `chaosx_scripted_system_architect` for reusable scripted effects, triggers, script constants, event targets, meta effects, variable patterns, and dynamic helper design.
- Use `chaosx_spreadsheet_doc_worker` only after implementation facts are available. Spreadsheet event-detail, evolution-detail, and cluster-detail fields must match the in-game localisation wording.
- Use `chaosx_skill_maintainer` for non-trivial skill creation, cleanup, routing updates, or multi-skill consistency work.
- Use `chaosx_improvement_loop_planner` during large event implementation when a mechanic, focus tree, country package, decision system, super-event, visual progression, lore package, or audit finding needs deeper design. It creates concrete event expansion addenda with research, historical connections, playable mechanics, and implementation surfaces for the main agent. It does not patch gameplay files. Do not spawn it again for the same event until the previous addendum has been implemented, folded into specs, queued with a reason, or rejected.

Patch-capable subagents are allowed to make small, local improvements by default when the change is inside the current task surface and directly improves the feature. They may vary costs, add clearer dynamic localisation, improve tooltips, adjust safe AI weights, add narrow helper calls, fix route locks, add cleanup hooks, or correct existing formable checks. They must not expand a whole mechanic, redesign a route family, add a new country package, create a new scripted GUI system, or change the requested design on their own. Broad gaps become a plan under `docs/plans/<event_id>_<event_slug>_plans/`. Every subagent edit needs a handoff that lists changed files, identifiers, validation, and remaining risks.

For major event work, the main agent should use the improvement loop after meaningful implementation tranches when several new mechanics have been added and now need deeper connections. The planner should expand ideas using the event-planning skill and relevant research. It should not be used repeatedly while a previous plan for the same event is still unresolved.

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
   - Script constants are the preferred tuning source, but not every effect field parses `constant:` tokens. For duration fields that reject constants, such as `days =` inside timed flags, assign the constant to a normal or temporary variable first and pass that variable to `days =`.
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
    - Prefer regular event targets (`save_event_target_as`) for short-lived chains, they automatically clear when the originating effect chain ends (but do carry into events fired from that chain).
    - Use global event targets (`save_global_event_target_as`) only when you need persistence beyond a single chain/system, they do not auto-clear and must be cleaned up (e.g. `clear_global_event_target = my_target`).
    - Use them as scopes/targets with `event_target:my_target`.
    - Localisation: when using an event target as a localization scope namespace, the `event_target:` prefix is not used (e.g. `[my_target.GetName]`).
11. Do not use unary `-` on variable tokens (e.g. `value = -my_var`), negate via `multiply_*_variable` first.
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

## 2. Localisation and UI

Localisation and UI must always be kept in sync with gameplay changes.

1. Localisation files must be encoded as **UTF 8 with BOM**. Wrong encoding breaks strings in game.
2. When you add or rename anything that appears on screen, update localisation in the same change.
3. In scripted localisation, do not write format characters like `§` or `£` directly.
4. Player-facing game text must describe the current world state and player choices, not implementation history or tuning mechanics. Do not say a value was capped, hardcoded, newly added, reworked, or changed because of an update request, keep those notes in docs or comments instead.
5. Localisation keys:
   - Do not use `:0`. Write keys as `key_name: "Text"` without `0` and without a leading space before the key.
   - Keep key names consistent and readable. No unnecessary prefixes.
6. Icons and UI assets:
   - Define icons in `interface/...` and keep naming stable.
   - When something needs icons, define them in a correct `.gfx` file. I will provide the sprites myself, you just have to tell me what folder to put them in and with what name.
   - Copy placeholder sprites from vanilla files that match the new gfx definition, so later I can replace them with real sprites easily and that the game would run without complaining about missing sprites.
   - Register new UI assets before requesting art so filenames do not need to change later.

## 3. Naming and Prefix Rules

Use prefixes only where they are needed.

Add prefixes if a folder is dedicated to Chaos Redux files that all share the prefix. Do not add the `chaosx` prefix to variable names, scripted effects, or scripted triggers unless the surrounding context uses it consistently.
Prefer short, descriptive names that reflect function and scope.

Unnecessary prefixes make code harder to read and maintain. Keep names clean.

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
18. When updating content (for example reworking an event), write as if the feature has always existed. Do not use meta wording like “now it is,” “now it has been reworked,” “newly added,” or similar update-history phrasing.

Follow these rules and your changes will be easier to review, safer to merge and more consistent with the rest of the project.
If this checklist cannot be satisfied, stop and request more design input instead of guessing.

## 5. Completion Proof and Simplification Reporting

A goal can never be marked complete unless it is actually complete.

For every goal, especially large event, mechanic, focus-tree, country-package, balance, UI, or asset goals, completion requires evidence. The agent must finish the requested implementation, update all related files, run or document the required checks, and report any blocker or simplification.

Do not claim completion when:

- only the most visible part was implemented
- a focus tree was generated but not reviewed, customized, balanced, localized, and wired
- a large batch of countries received generic or copied content
- balance checks were skipped
- validation scenarios were skipped
- localisation is missing
- AI behavior is missing
- assets are missing, unwired, or undocumented
- event logs, docs, spreadsheet rows, or manifests are stale
- any requested route, country, decision, mission, achievement, evolution, or super-event is missing
- a fallback or simplification was used without explicit approval

Balance checks are implementation work, not optional polish. If the spec or user asks for balance validation, the agent must inspect the relevant variables, scripted effects, decisions, mission outcomes, trigger conditions, AI weights, and scenario behavior. A vague statement that balance was adjusted is not enough.

Do not replace real implementation work with tooling work. Do not spend the goal creating Python scripts, report generators, or bulk-generation helpers while leaving the actual content shallow or incomplete. Small scripts may be used for mechanical audits such as counting focus blocks, checking duplicate ids, or finding missing localisation keys, but they are not a substitute for implementing and validating the content.

Do not bulk-generate large focus trees, country packages, decisions, localisation, or validation reports and call them complete. Generated or scripted drafts are acceptable only when every result is manually reviewed, customized to the country or route, wired into the mod, localized, given AI behavior, documented, and checked against the spec.

If any requested item is not implemented to the fullest extent, report it under a clear section such as `Simplifications, omissions, and blockers`. Even small deviations must be listed. If no simplifications were made, the final report must explicitly say so and provide evidence through files changed, audits, validation notes, and completed checklists.

Do not claim a goal is complete just because the game loads or because the most visible part works.

For large events, mechanics, focus-tree rewrites, country packages, balance passes, or multi-system goals, produce a concrete completion report. The report should list files changed, systems touched, balance checks, tests or validation scenarios, assets reused or created, documentation updated, and remaining blockers.

Every simplification must be reported. This includes skipped routes, fallback trees used in place of bespoke trees, missing assets, missing localisation, missing AI behavior, missing event-log entries, missing focus paths, missing dynamic scaling, hardcoded values where dynamic logic was requested, placeholder content, or weaker substitutes.

If there are no simplifications, say so explicitly and provide evidence through audits, docs, or changed files. If the goal cannot be fully implemented, report that the goal is incomplete instead of presenting partial work as done.

### Specs and Plans

Event source specifications belong under `docs/specs/<event_id>_<event_slug>_specs/`.

Subagent plans, improvement addenda, audit follow-up notes, blocked reports, and implementation handoffs belong under `docs/plans/<event_id>_<event_slug>_plans/`.

The plans folder is a working area. The specs folder is the source-of-truth design area. If an accepted plan changes the event design, the main agent should merge it into the relevant spec or report that it remains queued.

## 6. Event Integration

For Chaos Redux event implementation, use the repo skill `chaos-redux-events`.

1. Keep the entry event root format `chaosx.nr<ID>.1`.
2. Wire event script, category registration, auto-firing, localisation/name mappings, event log actor mapping, and event details window content together in the same change.
3. If the event has evolutions or world-end branches, wire the log entries, super-event integration, and related localisation in the same change.
4. Keep gameplay files, docs, the event spreadsheet/presentation, and any other details aligned.

## 7. Focus Trees and Large Content

For national focus work, use `hoi4-focus-trees` before editing. That skill is the detailed source of truth for focus-tree depth, reward variety, route logic, AI, localisation, icons, ideas, country identity changes, focus-decision integration, route coverage proof, and completion standards.

Before claiming focus-tree completion, use the appropriate audit route from `chaos-redux-subagents`. If a tree works but feels shallow, duplicated, generic, or disconnected from gameplay, use `chaos-redux-improvement-loop` and consider a plan-mode pass from `chaosx_improvement_loop_planner`.

## 8. Agent-generated Visual Assets

For final visual assets, use `chaos-redux-event-assets`. That skill is the detailed source of truth for image generation rules.

For animated visual assets, use `chaos-redux-frame-animation` in addition to `chaos-redux-event-assets`. Final animation assets must be built from real planned frames and must not be transform-only mockups.

Use `chaos-redux-subagents` for detailed asset subagent routing. Asset subagents create source files, processed PNGs, DDS files, manifests, and handoff notes. The main agent owns `.gfx` edits, gameplay references, localisation references, documentation alignment, and final validation.

## 9. Skill Maintenance

Use skills actively. Skills are not only for cleanup at the end of a task. They are the agent's memory for repeated workflows, project-specific patterns, hard-won fixes, and instructions that should not be rediscovered every time.

When a task reveals a repeated workflow, repeated mistake, reusable process, repo-specific convention, validation pattern, asset workflow, prompt pattern, or useful implementation rule, use `chaosx_skill_maintainer` or OpenAI’s official `skill-creator` skill to capture it cleanly.

Create or update skills more often during long tasks, especially when working through many events, mechanics, assets, localisation passes, or UI patterns. If the same reasoning would likely be needed again later in the run, spawn `chaosx_skill_maintainer` or update the relevant skill before moving on.

Never put event specific context inside skills! This is very important!

Rules:

1. Check whether an existing skill already covers the workflow before creating a new one.
2. Use `chaosx_skill_maintainer` for non-trivial skill creation, skill cleanup, routing updates, or multi-skill consistency work.
3. Prefer updating an existing skill when the workflow belongs there.
4. Create a new skill when the workflow is reusable, distinct, and not covered by an existing skill.
5. Add concise, specific rules based on actual task experience, not speculation.
6. Record repo paths, commands, examples, gotchas, source folders, validation steps, and handoff rules when they prevent rediscovery.
7. Keep each skill focused on one reusable workflow.
8. Do not bloat skills with one-off details that will not help future tasks.
9. During large multi-event runs, review skill gaps after each completed event or shared system. Update or create skills before starting the next event if something reusable was learned.
10. Report which skills were used, created, or updated at the end of each task.

## 10. Git

After completing each meaningful goal, create a Git commit.

The commit must only include changes related to that goal. Before committing, review the diff, verify that the implementation is complete.

Use a clear commit message that describes what was implemented.

Do not commit broken, unrelated, or half-finished work. If the goal cannot be completed cleanly, report the blocker instead of creating a misleading commit.
