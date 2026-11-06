---
name: hoi4-technology-doctrines
description: Use when creating or scripting HOI4 technologies and folders, unlocks, research bonuses, sharing groups, grand doctrines and mastery, or when a tech or doctrine is invisible or unresearchable.
---

# Hearts of Iron IV Technologies and Doctrines

Use this skill for `common/technologies/`, `common/technology_tags/`, `common/technology_sharing/`, `common/doctrines/`, the technology tree and doctrine interface files, and the effects, triggers, and modifiers that grant, test, or speed up research and doctrines.
Equipment definitions that a technology unlocks belong to `hoi4-equipment`, sub-units and templates to `hoi4-units-divisions`, ideas that carry `research_bonus` to `hoi4-ideas-modifiers`, and AI weighting strategies to `hoi4-ai-strategies`.

In this skill `GAME` means the installed Hearts of Iron IV folder named in `CLAUDE.md` and `WIKI` means the repository folder `hoi4_wiki`.
Installed documentation is more authoritative than the wiki; where they disagree this skill says so.

Read the engine contract and decision table below, then open only the reference for the phase of work. This file also keeps the repository conventions, the tools, the silent-failure list and the validation steps, which apply to every task.

Rules that always apply (full text in the references named):

- A visible technology needs a folder position, a `path` parent or its own gridbox, and the folder's interface pieces. Without them it never renders ([technology definitions](references/technology-definitions.md), [tree GUI](references/technology-tree-gui.md)).
- A technology only a script grants is a hidden technology: `allow = { always = no }`, no `folder`, granted with `set_technology`.
- `on_research_complete` does not run for techs listed in a country history file, and unresearching with `set_technology = { x = 0 }` leaves the unlocks usable.
- `XOR` must be written on every technology of the group, and a category bonus does nothing unless the category exists in `technology_tags` and the technology lists it ([folders and effects](references/folders-effects-and-sharing.md)).
- Use exact vanilla doctrine ids (`new_mobile_warfare`, not the documentation's `mobile_warfare`). Track `index` and `track` numbers are 0-based, and doctrine blocks use `equipment_bonus`, not the `add_equipment_bonus` effect ([doctrine rules](references/doctrine-system-rules.md)).
- The technology tools are read-only, and the first call on a large workspace reports deferred helper projections, which is not a defect.

Two deeper references already exist:

- [Technology tree GUI](references/technology-tree-gui.md): read before building the folder tab, folder container, gridboxes and item containers for a visible folder.
- [Doctrine authoring](references/doctrine-authoring.md): read before writing a new doctrine folder, grand doctrine, track or sub-doctrine, its localisation, sprites and interface.

## Reference map

- [Technology definitions, AI weights and localisation](references/technology-definitions.md): Read before writing or changing a technology block, its unlocks, hidden-tech pattern, AI weighting, localisation or tile icon. Covers: Technology definitions; AI and technology; Localisation and graphics.
- [Folders, research effects and sharing groups](references/folders-effects-and-sharing.md): Read before defining technology folders and categories, scripting research effects, triggers or bonuses, or adding a technology sharing group. Covers: Folders and categories; Technology effects, triggers, and research bonuses; Technology sharing groups.
- [Doctrine system rules](references/doctrine-system-rules.md): Read before scripting grand doctrines, sub-doctrines, mastery or doctrine effects, triggers and modifiers. Covers: Doctrines.

## Read the engine contract first

Use `hoi4.reference_context` with `surface = technology`, then `hoi4.reference_search` and `hoi4.reference_read` for the cited sections, and `hoi4.source_lookup` for vanilla definitions.
If a route fails once, retry once with narrower input, then read the local files directly.

| Question | Read |
| --- | --- |
| Technology fields, cost, paths, folders, GUI, sharing groups | `WIKI/technology_modding.md` |
| Doctrine concepts, effects, triggers, modifiers | `GAME/common/doctrines/_documentation.md` |
| Doctrine folder, grand doctrine, track, and sub-doctrine syntax | `GAME/common/doctrines/folders/_documentation.md`, `grand_doctrines/_documentation.md`, `tracks/_documentation.md`, `subdoctrines/_documentation.md` |
| Effects (`set_technology`, `add_tech_bonus`, `set_grand_doctrine`, and the rest) | `GAME/documentation/effects_documentation.md` |
| Triggers (`has_tech`, `has_doctrine`, `has_mastery`, and the rest) | `GAME/documentation/triggers_documentation.md` |
| Modifiers (`research_speed_factor`, `<folder>_doctrine_cost_factor`, mastery gain factors) | `GAME/documentation/modifiers_documentation.md` |
| Defines (`NTechnology`, `NDoctrines`) | `GAME/common/defines/00_defines.lua` |
| Research weighting for the AI | `WIKI/technology_modding.md` (AI weighting), `WIKI/ai_focuses.md`, `hoi4-ai-strategies` |

The tree and folder interface authoring detail is in `references/technology-tree-gui.md`.
Doctrine authoring skeletons, loc keys, and GUI notes are in `references/doctrine-authoring.md`.

## Decision table

| Goal | Mechanism |
| --- | --- |
| A visible researchable technology | Technology in a folder with a position, plus the folder container, item containers, and a gridbox in the folder window |
| A technology only a script or country setup can grant | Hidden technology: `allow = { always = no }`, no `folder`, granted by `set_technology` |
| Unlock equipment, modules, sub-units, buildings, or tactics | `enable_equipments`, `enable_equipment_modules`, `enable_subunits`, `enable_building`, `enable_tactic` on the technology |
| One extra ahead-of-time or branch-gated variant tile | `sub_technologies` on the parent |
| Apply a flat country modifier on research | Any country-scoped modifier written directly in the technology |
| Boost a sub-unit or category, optionally per terrain | Sub-unit or category block inside the technology |
| Run an effect once on research | `on_research_complete` with optional `on_research_complete_limit` |
| Grant a free partial boost to future research | `add_tech_bonus` (limited uses) |
| Speed research of one category | `research_bonus = { category = factor }` in an idea or leader trait |
| Speed all research | The `research_speed_factor` modifier |
| Share research between countries | A `technology_sharing_group` plus `add_to_tech_sharing_group` |
| Give or replace doctrines | `set_grand_doctrine` and `set_sub_doctrine`; mastery through `add_mastery`, `add_daily_mastery`, `add_mastery_bonus` |
| A new doctrine system | Folder, grand doctrines, tracks, sub-doctrines in `common/doctrines/` |
| Understand or verify an existing tree | The `hoi4.tech_inspect`, `hoi4.tech_render`, and `hoi4.tech_inspect` with `mode: "compare"` tools |

## Repository conventions that apply

- Indent with tabs, never use `<=` or `>=`, put tuning values in `common/script_constants/`, and reuse the project's dynamic scripted effects library (`common/scripted_effects/<prefix>_dynamic_effects.txt`, named in `CLAUDE.md`) before adding new ones.
- Localisation is UTF-8 with BOM and keys carry no `:0`; player-facing text describes the current world state.
- Keep technology folders and categories that the mod adds in their own file under `common/technology_tags/` (for example `<prefix>_tech_tags.txt`), a separate file of the same two top-level blocks the vanilla `00_technology.txt` uses.
- The repository holds a full copy of `interface/countrytechtreeview.gui` and `.gfx`; GUI additions for new folders go into that copy, and a game update needs a re-merge of the vanilla changes.
- A new concrete equipment type, sub-unit, special project, doctrine, or general system must be registered with the test-country setup effect described in `CLAUDE.md`.
- Document each new mechanic in `docs/` with the icons it needs, the `.gfx` file that references them, and the names used in code and localisation.

## Tools

The `hoi4_agent_tools` technology tools are read-only.
Verify with the connected tool list before relying on them; first call returns a resource link and a code such as `TECH_INSPECTED_PARTIAL`.

- `hoi4.tech_inspect` `mode`: `scan`, `folders`, `trace` (with `direction`, `maxDepth`), `explain`, `unlocks` (with `technologyId` or a `targetId` and `targetKind`), `bonus_coverage`, `lint`, `impact` (rename or removal), `helper_expansion`.
  Narrow with `technologyId`, `folderId`, or `categoryId`.
- `hoi4.tech_render` `view`: `summary`, `folder`, `dependencies`, `technology`, `doctrine`, `exclusive`, `memberships`, `bonuses`, `grants`, `unlocks`, `metadata`, `assets`, `unresolved`; an optional `scenario` takes a year and researched ids.
- `hoi4.tech_inspect` with `mode: "compare"` compares revisions or proposed sources; it never writes.
- On a large workspace the first call reports `validation.passed = false` with the check "Helper projections were deferred"; the counts, folder list, and linked artifact are still usable evidence, and the deferral is not a defect.
- Follow the repository retry rule: one read-only request plus at most one corrected retry per failure, then read source directly and say the check was not run.
- Use `helper_expansion` only after confirming the server version and task negotiation as required by `CLAUDE.md`.

## Common mistakes and silent failures

- Tech is unreachable: no `path` parent, no gridbox for a tech without `path`, no `folder` block, or `allow_branch` is false.
- A tech without `path` parents and without its own gridbox definition in the folder window does not render (wiki).
- Tech shows but cannot be researched: `allow` is false, which is the intended hidden-tech pattern.
- Equipment or sub-unit still locked: the tech lists a mistyped id, the tech was not granted, or the object is `active = yes` elsewhere.
- `on_research_complete` did not fire for a starting tech: history-file techs do not run it.
- Unresearching a tech with `set_technology = { x = 0 }` leaves unlocks usable and cannot remove exclusive techs.
- A category-based bonus does nothing: the category is not in `technology_tags`, or the technology does not list it in `categories`.
- `XOR` written on one side only does not make the techs exclusive.
- Doctrine rewards named in the wrong order: milestones follow the order of `tracks` in the grand doctrine; rewards follow the list order in the sub-doctrine.
- `set_grand_doctrine` or `set_sub_doctrine` used with an id from the documentation example instead of a vanilla id.
- A track filter `index` or `track` number is 0-based among all tracks in the folder.
- A technology cost change is ignored because a `start_year` far in the future adds large ahead-of-time penalties; compute the cost with the defines before balancing.

## Validation

- `hoi4.tech_inspect` with `mode = unlocks` or `trace` on each new technology, and `lint` for the changed folder when the workspace allows it.
- `hoi4.script_validate` on effect and trigger bodies with `scope = country`.
- Check each `enable_*` id resolves with `hoi4.source_lookup`, each category exists, each localisation key and sprite exists, and the folder interface pieces exist for any visible folder.
- For doctrines, confirm every track listed in a grand doctrine exists, every sub-doctrine names a valid track, the milestone count equals the track count, and each reward has a localisation key.
- Report the checks that were not run, such as tree layout, tooltip text, and mastery accrual rates, as unobserved.
