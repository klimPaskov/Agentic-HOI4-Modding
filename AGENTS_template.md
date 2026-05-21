# Repository Guidelines

This file describes how coding agents should read, edit, validate, and extend this Hearts of Iron IV mod.

## Placeholder Guide

Replace these placeholders before using this file in a real mod repo:

- `[MOD_NAME]` = full mod name
- `[MOD_PREFIX]` = script prefix, namespace, or short internal prefix used by the mod
- `[OFFLINE_WIKI_PATH]` = path to the offline Paradox wiki snapshot
- `[HOI4_VANILLA_PATH]` = path to the vanilla Hearts of Iron IV installation
- `[REFERENCE_MOD_NAME]` = approved large reference mod, if any
- `[REFERENCE_MOD_PATH]` = path to the approved reference mod, if any
- `[REFERENCE_MOD_2_NAME]` = second approved reference mod, if any
- `[REFERENCE_MOD_2_PATH]` = path to the second approved reference mod, if any
- `[DOCS_FOLDER]` = documentation folder path, usually `docs/`
- `[EVENT_SKILL_NAME]` = repo skill for event implementation
- `[ASSET_SKILL_NAME]` = repo skill for visual asset work
- `[SUPER_EVENT_SKILL_NAME]` = repo skill for super-events or major presentation events
- `[FOCUS_TREE_SKILL_NAME]` = repo skill for national focus trees
- `[DECISION_MISSION_SKILL_NAME]` = repo skill for decisions and missions
- `[MTTH_SKILL_NAME]` = repo skill for MTTH or weighted timing logic
- `[SUBAGENT_SKILL_NAME]` = repo skill for coordinating custom subagents, if used
- `[REPO_EXPLORER_AGENT]` = optional subagent for repo exploration and pattern mapping
- `[ASSET_SOURCE_AGENT]` = optional subagent for sourced or archival visual assets
- `[GENERATED_ART_AGENT]` = optional subagent for generated non-icon visual assets
- `[ICON_AGENT]` = optional subagent for icon production
- `[SUPER_EVENT_TEXT_AGENT]` = optional subagent for super-event quote and remark research
- `[SUPER_EVENT_AUDIO_AGENT]` = optional subagent for super-event audio research and conversion
- `[FOCUS_TREE_AUDITOR_AGENT]` = optional subagent for focus-tree audits
- `[DECISION_MISSION_AUDITOR_AGENT]` = optional subagent for decision and mission audits
- `[COUNTRY_PACKAGE_AUDITOR_AGENT]` = optional subagent for country package audits
- `[LOCALISATION_AUDITOR_AGENT]` = optional subagent for localisation audits
- `[SCRIPTED_SYSTEM_ARCHITECT_AGENT]` = optional subagent for reusable scripted-system design
- `[EVENT_COMPLETION_AUDITOR_AGENT]` = optional subagent for spec-versus-implementation audits
- `[SPREADSHEET_DOC_WORKER_AGENT]` = optional subagent for docs, manifests, spreadsheets, and completion reports

Example-only placeholders such as `[STATE_A]`, `[STATE_B]`, `[STATE_C]`, `[NAMED_REGION]`, `[CAPITAL_A]`, `[CAPITAL_B]`, `[EQUIPMENT_BASE]`, and `[EQUIPMENT_LEVEL]` appear inside examples. Replace them only if you copy those examples into real project instructions or code.

Remove sections for skills, subagents, spreadsheets, super-events, or assets if the target mod does not use them.

---

## 0. Required Reading Before Any Change

### Project identity

This repository is the source for `[MOD_NAME]`.

Before editing, understand the mod's existing structure, naming conventions, documentation, and implemented patterns. Do not assume vanilla structure is enough when the mod already has its own pattern.

If this mod has project skills, read them as required implementation guidance, not optional notes.

### Paradox Wiki

Before opening or editing mod files, consult the relevant Hearts of Iron IV modding pages from the offline Paradox wiki snapshot in `[OFFLINE_WIKI_PATH]`.

Rules:

- Treat the offline snapshot as the required wiki reference unless the repo explicitly says otherwise.
- Keep the relevant pages open while working.
- Do not rely on memory when a wiki page exists.

Always open at least these core pages when the task touches script, events, decisions, ideas, localisation, or UI:

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

If the task touches another system, open the corresponding wiki page as well. Examples include Interface Modding, Scripted GUI Modding, National focus modding, Country creation, Units, Equipment, Technologies, Characters, and Music modding.

### Vanilla references

Use vanilla HOI4 as the main example set.

The vanilla game directory is expected at:

```text
[HOI4_VANILLA_PATH]
```

Vanilla Hearts of Iron IV includes official documentation files, often in markdown. Read relevant documentation from:

```text
[HOI4_VANILLA_PATH]/documentation
```

Vanilla game files may also include documentation files in other folders. Consult them when they exist.

Treat vanilla documentation as more authoritative than memory and usually more up to date than old wiki pages. Still consult the offline wiki in parallel.

When implementing a mechanic, event, decision, focus, UI element, idea, country package, or asset, find at least one vanilla precedent if possible and mirror its valid structure.

If this mod already has a pattern for the same feature, follow the mod pattern over vanilla for consistency, but still check vanilla for syntax and edge cases.

### Mod references beyond vanilla

If vanilla examples are insufficient or unclear, inspect approved reference mods.

Recommended placeholders:

```text
[REFERENCE_MOD_NAME] = approved reference mod name
[REFERENCE_MOD_PATH] = approved reference mod path
[REFERENCE_MOD_2_NAME] = optional second reference mod name
[REFERENCE_MOD_2_PATH] = optional second reference mod path
```

Use reference mods to understand structure, patterns, and edge-case handling. Do not copy content blindly. Adapt only the implementation pattern. If no reference mod is approved, remove this subsection.

### Repo skills

Use repo skills as required workflow guidance.

Replace this list with the real skills used by the mod:

- Use `[EVENT_SKILL_NAME]` for event implementation, event logs, event details, evolutions, documentation, and spreadsheet alignment.
- Use `[ASSET_SKILL_NAME]` when a task needs visual assets, icons, flags, portraits, UI art, report images, news images, achievement icons, final DDS files, asset manifests, or sprite handoff notes.
- Use `[SUPER_EVENT_SKILL_NAME]` when a task creates, updates, researches, or wires a super-event.
- Use `[FOCUS_TREE_SKILL_NAME]` before editing national focus trees.
- Use `[DECISION_MISSION_SKILL_NAME]` before editing decisions, missions, timed objectives, decision categories, or decision AI.
- Use `[MTTH_SKILL_NAME]` when mean-time-to-happen logic or weighted timing would reduce clutter or make AI and release logic clearer.
- Use `[SUBAGENT_SKILL_NAME]` when coordinating custom subagents for research, asset production, audits, or documentation.

If a listed skill does not exist yet, either create it with the skill-creator workflow or remove the line.

### Subagents

Use project custom Codex subagents when a task needs bounded research, asset production, audit, or documentation work that can be separated from the main implementation.

The main agent remains responsible for final implementation, final wiring, final review, final validation, and final reporting. Subagents return evidence, files, manifests, or handoff notes. Do not let subagents silently change gameplay scope unless the parent prompt explicitly grants that scope.

If this repo uses a subagent skill, follow `[SUBAGENT_SKILL_NAME]` for the full routing and handoff rules.

Example routing placeholders:

Use `[REPO_EXPLORER_AGENT]` to find relevant repo files, existing patterns, required docs, vanilla references, and likely touchpoints before editing.

Use `[ASSET_SOURCE_AGENT]` for real, archival, documentary, historical, public-domain, Creative Commons, or user-provided visual sources. This includes report images, news images, documentary super-event images, real leader portraits, historical flags, and historically attested symbols.

Use `[GENERATED_ART_AGENT]` for generated non-icon event art. This includes fictional or symbolic super-event images, fictional portraits, fictional flags, faction emblems, UI panels, and progression-state art.

Use `[ICON_AGENT]` for focus icons, idea icons, national spirit icons, officer corps spirit icons, decision icons, decision category icons, achievement icons, and tech icons.

Use `[SUPER_EVENT_TEXT_AGENT]` for super-event main quotes, exact wording checks, attribution confidence, source comparison, button text, cultural remarks, slogans, allusions, and short references.

Use `[SUPER_EVENT_AUDIO_AGENT]` for super-event audio source research, license verification, download, conversion, and audio research notes.

Use `[FOCUS_TREE_AUDITOR_AGENT]` after creating or heavily reworking focus trees. It should check branch depth, route coverage, icons, localisation, reward variety, prerequisites, AI, and simplification.

Use `[DECISION_MISSION_AUDITOR_AGENT]` after creating or heavily changing decision categories, timed missions, mission pools, influence systems, intervention systems, aid systems, objective pools, or focus-unlocked decision families.

Use `[COUNTRY_PACKAGE_AUDITOR_AGENT]` after creating, releasing, transforming, splitting, puppeting, or substantially changing playable or AI-controlled countries. Use it when tags, history files, state ownership, leaders, portraits, flags, focus loading, starting forces, or country AI were touched.

Use `[LOCALISATION_AUDITOR_AGENT]` after broad visible-content changes across events, focuses, decisions, ideas, super-events, GUI, scripted localisation, or event logs.

Use `[SCRIPTED_SYSTEM_ARCHITECT_AGENT]` before implementing repeated, dynamic, cross-file logic that should become a scripted effect, scripted trigger, script constant category, event target pattern, variable pattern, or meta-effect pattern. Also use it to refactor duplicated logic found during implementation.

Use `[EVENT_COMPLETION_AUDITOR_AGENT]` before calling a large event implementation complete, especially when the task came from a long spec, multiple prompt files, or a user complaint about simplification.

Use `[SPREADSHEET_DOC_WORKER_AGENT]` only after implementation facts are available. It must document actual repo state, not intended state. If this mod has event detail, evolution detail, or cluster detail spreadsheet fields, those fields must use the same wording as the in-game localisation unless the project says otherwise.

#### Visual asset ownership split

The main agent owns `.gfx` edits, GUI references, localisation references, event references, icon assignments, documentation that depends on implementation, and final validation.

Visual asset subagents own only asset package production:

- source files
- processed PNG previews
- final DDS files
- contact sheets
- manifests
- `[DOCS_FOLDER]/assets/<asset_package_slug>/gfx_handoff.md`

Visual asset subagents must not edit `.gfx`, localisation, GUI, event, focus, idea, decision, scripted effect, scripted trigger, history, country, or spreadsheet files unless the parent prompt explicitly expands scope.

For mixed asset packages, spawn narrow agents separately. Use the source-image agent for real or archival photos, the generated-art agent for fictional or symbolic non-icon art, and the icon agent for gameplay icons.

#### Super-event research ownership split

For super-events, split research when useful:

- `[SUPER_EVENT_TEXT_AGENT]` finds and verifies the main quote and short cultural remark.
- `[SUPER_EVENT_AUDIO_AGENT]` finds, verifies, downloads, converts, and documents audio.
- `[ASSET_SOURCE_AGENT]` or `[GENERATED_ART_AGENT]` handles the image source mode according to `[ASSET_SKILL_NAME]`.

The main agent still owns super-event slot wiring, scripted localisation, audio id wiring, settings-aware playback integration, `.gfx` image wiring, event trigger wiring, docs alignment, and spreadsheet alignment.

#### Audit and documentation cadence

Use audit subagents before completion claims, not after claiming completion.

A subagent report is not final proof. The main agent must inspect the report, make the fixes, rerun relevant checks, and clearly report anything still blocked.

---

## 1. Coding Style

Clausewitz script is picky. Follow these rules strictly.

1. Indent script blocks with tabs. Use lowercase keys and snake_case for variables, effects, triggers, and script names unless vanilla or the existing mod pattern requires otherwise.
2. Never use `<=` or `>=`. They are not supported and will break the game.
   - Use `check_variable` with `compare = greater_than_or_equals` or `compare = less_than_or_equals` when needed.
   - Use `<` and `>` where supported and clearer.
3. Remove magic numbers. Tuning should be centralized in variables, constants, scripted effects, scripted triggers, or clearly named values.
4. Temporary variables do not have a scope. `ROOT.temp_var` or `PREV.temp_var` will not work. Only normal variables have scope.
5. Use loops when they improve clarity and reduce repetition.
6. Use flags for true or false state, not numeric variables that only ever become 0 or 1.
7. Move repeated logic into scripted effects or scripted triggers.
8. Avoid broad `on_daily`, `on_weekly`, `on_monthly`, or similar world-iteration logic unless the user explicitly requested it or the system truly requires it. If a whole-world iteration is required, explain why before implementing.
9. Constants declared as `@MY_CONSTANT` are file scoped and cannot cross file boundaries.
   - Prefer HOI4 `script_constants` for shared tuning values.
   - Put global constants in `common/script_constants/`.
   - Use explicit fixed-point access when supported, such as `constant:category.key`.
   - Some fields reject constants. In those cases, assign the value to a variable first or use a file-scoped `@` constant only when appropriate.
10. Use event targets to persist scope pointers across blocks or events when variables and scopes are insufficient.
    - Prefer regular event targets for short-lived chains.
    - Use global event targets only when persistence beyond one effect chain is required.
    - Clear global event targets when they are no longer needed.
11. Do not use unary `-` on variable tokens such as `value = -my_var`. Negate through a temporary variable or multiplication first.
12. Use `meta_effect` or `meta_trigger` when an effect or trigger does not accept dynamic values and the repo pattern supports generated script text.
13. Prefer reusable dynamic scripted effects and triggers for complex or repeated logic.
14. If MTTH variables would reduce clutter or centralize AI weighting, use `[MTTH_SKILL_NAME]`.

### Meta effect example

Meta effects can build static script from dynamic variables and scripted localisation.

```txt
set_variable = { equipment_amount = 10 }
set_variable = { equipment_level = 2 }

meta_effect = {
	text = {
		add_equipment_to_stockpile = {
			type = [EQUIPMENT_BASE]_[EQUIPMENT_LEVEL]
			amount = equipment_amount
		}
	}
	EQUIPMENT_LEVEL = "[?equipment_level|.0]"
	EQUIPMENT_BASE = "[This.GetEquipmentBaseName]"
}
```

The scripted localisation used in the meta effect must be implemented and documented. Do not use meta effects as a substitute for simple static code when static code is clearer.

---

## 2. Localisation and UI

Localisation and UI must stay in sync with gameplay changes.

1. Localisation files must be encoded as UTF-8 with BOM unless this project explicitly uses another verified encoding.
2. When adding or renaming anything visible on screen, update localisation in the same change.
3. In scripted localisation, follow the project's established handling of formatting symbols and icons.
4. Player-facing text must describe the current world state and player choices, not implementation history or tuning mechanics.
5. Do not say a value was capped, hardcoded, newly added, reworked, or changed because of an update request in player-facing text.
6. Localisation keys should be consistent and readable.
7. Do not use `:0` if the project convention is `key_name: "Text"`. Follow the project convention.
8. Define icons and UI assets in the correct `.gfx` file and keep naming stable.
9. Register new UI assets before requesting art so filenames do not need to change later.
10. If using placeholder sprites so the game can load, document that they are placeholders and where final sprites must go.

### Trigger, prerequisite, and tooltip clarity

Long trigger blocks should not be exposed raw to the player. Hide them or use scripted localisation, custom trigger tooltips, or named scripted triggers.

When a decision, mission, focus, event option, or GUI button requires control of states, divisions in states, protected borders, held capitals, rail hubs, depots, ports, or named regions, the player-facing text must name the exact states or a clear named region.

Avoid vague requirement text such as:

- `required states`
- `border states`
- `nearby states`
- `key states`
- `sufficient divisions`
- `enough equipment`

Use clear text instead, for example:

- `Place 8 supplied divisions in [STATE_A], [STATE_B], and [STATE_C].`
- `Hold the [NAMED_REGION] for 120 days.`
- `Keep [CAPITAL_A] and [CAPITAL_B] connected to supply.`

Cost localisation should be short, readable, and icon-first.

Good examples:

- `2,000 <infantry_equipment_texticon>`
- `20 <army_xp_texticon> 20 <command_power_texticon>`
- `200 <support_equipment_texticon>`
- `Depot control`

Avoid filler words between costs.

---

## 3. Naming and Prefix Rules

Use prefixes only where they are needed.

Replace `[MOD_PREFIX]` with the real mod prefix where appropriate.

Add prefixes if a folder is dedicated to files that all share the prefix. Do not add `[MOD_PREFIX]` to every variable, scripted effect, or scripted trigger unless the surrounding context uses it consistently.

Prefer short, descriptive names that reflect function and scope.

Keep names stable once used by script, localisation, sprites, saves, docs, or spreadsheet rows.

---

## 4. HOI4 Modding Rules Summary

When implementing any new mechanic or content package, follow this checklist:

1. Open the required Paradox wiki pages from `[OFFLINE_WIKI_PATH]`.
2. Inspect vanilla files in `[HOI4_VANILLA_PATH]` and read relevant vanilla documentation.
3. Inspect existing mod files that implement a similar system.
4. Use the relevant repo skills.
5. Create or update documentation under `[DOCS_FOLDER]` if the mechanic or content package is significant.
6. List required icons, sprites, image assets, audio assets, and final paths in docs or manifests.
7. Plan variables, flags, event targets, and constants so values are dynamic and centralized.
8. Avoid unsupported operators and constructs.
9. Use loops, meta effects, meta triggers, scripted effects, and scripted triggers where they reduce duplication.
10. Reuse existing dynamic helpers before adding new bespoke logic.
11. Document any new shared helpers in the same change.
12. Keep localisation, icons, UI definitions, docs, and spreadsheet rows aligned with gameplay changes.
13. Confirm decisions, missions, event options, and GUI actions have proper trigger tooltips and effect descriptions.
14. Respect repo style and naming rules.
15. Fallbacks and simplifications must be reported. If the project forbids fallbacks, ask before using one.
16. When debugging unclear runtime behavior, add temporary debug logging only when useful, then remove it after the issue is solved.
17. When updating content, write as if the feature has always existed. Do not use update-history wording in player-facing text.

If this checklist cannot be satisfied, stop and report the blocker instead of guessing.

---

## 5. Completion Proof and Simplification Reporting

A goal can never be marked complete unless it is actually complete.

For every meaningful goal, especially large events, mechanics, focus trees, country packages, balance passes, UI, or asset goals, completion requires evidence. The agent must finish the requested implementation, update all related files, run or document required checks, and report any blocker or simplification.

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
- a fallback or simplification was used without approval when approval is required

Balance checks are implementation work, not optional polish.

Do not replace real implementation work with tooling work. Small scripts may be used for mechanical audits such as counting focus blocks, checking duplicate IDs, or finding missing localisation keys, but they are not a substitute for implementing and validating content.

If any requested item is not implemented to the fullest extent, report it under `Simplifications, omissions, and blockers`.

If no simplifications were made, say so explicitly and provide evidence through files changed, audits, validation notes, and completed checklists.

For large tasks, produce a concrete completion report that lists:

- files changed
- systems touched
- balance checks
- tests or validation scenarios
- assets reused or created
- documentation updated
- subagents used, if any
- remaining blockers

Do not claim a goal is complete just because the game loads or because the most visible part works.

---

## 6. Event Integration

For event implementation, use `[EVENT_SKILL_NAME]`.

1. Keep event IDs and namespaces consistent with the existing mod pattern.
2. Wire event script, category registration, auto-firing, localisation, event log actor mapping, event details, docs, and spreadsheet rows together when the feature requires them.
3. If the event has evolutions, escalation stages, defeat aftermaths, world-end branches, or super-events, wire all related log entries, localisation, settings, audio, images, and docs in the same implementation pass.
4. Keep gameplay files, docs, spreadsheet rows, and presentation material aligned.
5. Do not treat events as isolated popups when the mod has event logs, details windows, global pacing, settings, or evolution systems.

---

## 7. Focus Trees and Large Content

For national focus work, use `[FOCUS_TREE_SKILL_NAME]` before editing.

Focus trees should be playable route systems, not long vertical reward lists.

A strong focus tree usually includes:

- readable non-linear branch layout
- real route choices and mutual exclusions where identity changes
- route-specific AI behavior
- icons or icon families
- localisation names and descriptions
- industry and logistics development
- military development
- diplomacy
- expansion, settlement, liberation, or regional ambition
- internal faction or political route logic where appropriate
- documentation of route families and focus counts

Focus rewards must be diverse. Do not make most focuses grant a new idea, political power, stability, war support, or small flat modifiers.

Use rewards that fit the route, such as factories, forts, anti-air, radar, airbases, infrastructure, railways, supply hubs, resources, production lines, equipment, templates, units, commanders, advisors, laws, decisions, missions, claims, cores, war goals, diplomacy, influence mechanics, faction mechanics, events, leader changes, cosmetic names, and flags.

Ideas should have depth. New or unstable countries should usually start with a few meaningful negative or mixed ideas, then mitigate, upgrade, replace, worsen, or remove them through focuses, decisions, missions, events, and route choices.

Before claiming focus-tree completion, audit duplicate focuses, duplicate ideas, generic rewards, missing icons, missing AI, missing localisation, route coverage, and whether the tree is readable in game.

---

## 8. Decisions and Missions

For decisions and missions, use `[DECISION_MISSION_SKILL_NAME]` before editing.

Decisions and missions should represent actions, commitments, objectives, pressure systems, or tradeoffs. Do not turn them into a store where the player spends political power for small modifiers.

Prefer objectives that ask the player or AI to do something real:

- hold named states
- guard borders
- secure rail hubs
- keep capitals connected to supply
- send equipment through aid decisions
- open or close corridors
- build influence
- complete timed crisis objectives
- maintain local support
- protect ports or depots

Use dynamic costs and durations where the system needs scaling. Keep tooltips readable and avoid exposing raw trigger blocks.

---

## 9. Country Packages

Use `[COUNTRY_PACKAGE_AUDITOR_AGENT]` or an equivalent audit when creating, releasing, transforming, splitting, puppeting, or substantially changing countries.

A complete country package may need:

- tag definition
- country history
- state history
- ownership and controller setup
- capital
- cores and claims
- flags
- cosmetic names
- leader and portrait
- characters, advisors, commanders, and parties
- focus tree loading
- ideas and laws
- starting forces and templates
- technologies
- production setup
- AI strategy
- diplomacy behavior
- localisation
- docs and spreadsheet rows

Do not call a country package complete if it only has a tag and ownership.

---

## 10. Agent-generated Visual Assets

When the user asks for final visual assets, use `[ASSET_SKILL_NAME]`.

Use project asset subagents when the work can be separated cleanly:

- `[ASSET_SOURCE_AGENT]` for real, archival, historical, documentary, or public-source images.
- `[GENERATED_ART_AGENT]` for generated non-icon fictional or symbolic art.
- `[ICON_AGENT]` for generated icons.

The relevant asset subagent must read `[ASSET_SKILL_NAME]` and inspect the matching reference folder before creating, sourcing, processing, or converting assets.

Asset subagents produce source files, processed PNG previews, final DDS files, manifests, contact sheets when useful, and `gfx_handoff.md`.

The main agent owns `.gfx` edits, GUI references, localisation references, event references, focus icon assignments, idea icon assignments, decision icon assignments, documentation alignment, and final validation.

If the main agent already registered `.gfx` sprites or texture paths before requesting art, the asset subagent must follow those filenames, sprite names, target DDS paths, and target sizes. It should only propose names or paths when they were not provided.

Rules:

1. Use the configured image generation workflow for generated artwork.
2. Do not create core artwork with Python, simple shapes, contact sheets, or layout-only mockups.
3. Python or scripts may be used after generation or sourcing for cropping, resizing, organizing, contact sheets, manifests, and DDS conversion.
4. Convert final PNG assets to the DDS format expected by this project.
5. Keep the source PNG, processed PNG preview, final DDS path, sprite name, intended use, target size, and inspected reference folder in the asset manifest.
6. Do not leave final assets only in temporary folders.
7. Do not mark visual assets complete until the main agent can wire every sprite without guessing.

---

## 11. Super-events, Audio, and Presentation Moments

Use `[SUPER_EVENT_SKILL_NAME]` when a task creates, updates, researches, or wires a super-event or equivalent major presentation moment.

A complete super-event package may include:

- slot or identifier
- title localisation
- description localisation
- button text
- quote
- image
- audio id
- audio file
- audio documentation
- event trigger or effect wiring
- settings-aware playback
- docs and spreadsheet alignment

Use the text researcher for quotes and remarks, the audio researcher for music and sound, and the asset agents for images when the package is large enough to split.

Do not wire only one part of a super-event package and call it done.

---

## 12. Documentation and Spreadsheet Alignment

Documentation must describe actual implemented repo state, not intended state.

Use `[SPREADSHEET_DOC_WORKER_AGENT]` after implementation facts exist when the task needs docs, event catalog rows, manifests, completion reports, or player-facing summaries.

Rules:

1. Do not invent implementation details.
2. Read the files being documented.
3. Keep docs aligned with actual identifiers, filenames, sprites, event IDs, focus IDs, ideas, decisions, and asset paths.
4. Mark missing or uncertain information honestly.
5. When updating counts, recount actual blocks from files rather than trusting stale docs.
6. If this project mirrors in-game event detail, evolution detail, or cluster detail localisation into spreadsheet fields, use the exact in-game wording there.

---

## 13. Skill Maintenance

Use skills actively. Skills are not only for cleanup at the end of a task.

When a task reveals a repeated workflow, repeated mistake, reusable process, repo-specific convention, validation pattern, asset workflow, prompt pattern, or useful implementation rule, use the project's skill creation workflow.

Rules:

1. Check whether an existing skill already covers the workflow before creating a new one.
2. Prefer updating an existing skill when the workflow belongs there.
3. Create a new skill only when the workflow is reusable, distinct, and not covered by an existing skill.
4. Add concise, specific rules based on actual task experience, not speculation.
5. Record repo paths, commands, examples, gotchas, source folders, validation steps, and handoff rules when they prevent rediscovery.
6. Keep each skill focused on one reusable workflow.
7. Do not bloat skills with one-off details that will not help future tasks.
8. Do not put event-specific, country-specific, or one-off implementation context inside general skills.
9. Report which skills were used, created, or updated at the end of each task.

---

## 14. Git

After completing each meaningful goal, create a Git commit if the user or repo workflow expects commits.

The commit must include only changes related to that goal. Before committing, review the diff and verify that the implementation is complete.

Use a clear commit message that describes what was implemented.

Do not commit broken, unrelated, or half-finished work. If the goal cannot be completed cleanly, report the blocker instead of creating a misleading commit.

---

## 15. Placeholder Checklist

Before using this file in a real mod, complete the Placeholder Guide at the top of this file.

Then remove sections that the mod does not use yet and add project-specific rules when the agent repeats a mistake or when a workflow becomes common.
