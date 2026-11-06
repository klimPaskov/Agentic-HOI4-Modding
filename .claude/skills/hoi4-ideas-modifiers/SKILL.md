---
name: hoi4-ideas-modifiers
description: Use when creating or auditing HOI4 ideas, national spirits, hidden ideas, laws, advisor ideas, dynamic, static or custom modifiers, timed ideas and modifier tooltips or localisation.
---

# HOI4 Ideas and Modifiers

Generic guidance for applying lasting numeric effects in Hearts of Iron IV: choosing between an idea, a dynamic modifier, a static modifier, or a custom modifier definition, writing each with verified syntax, and avoiding the silent failures.
Use `hoi4-map-states` for state-scoped effects that are not modifiers (ownership, buildings, categories), `hoi4-ai-strategies` for `ai_will_do` weights inside ideas, `hoi4-mtth` for MTTH variables that feed dynamic modifiers, and `hoi4-decisions-missions` for decisions that add or swap ideas.

Pick the mechanism with the decision procedure below, then open only the reference for the phase of work. This file also keeps how modifiers work, the repository conventions, the silent-failure list and the validation procedure, which apply to every task.

`GAME` means the installed Hearts of Iron IV folder named in `CLAUDE.md`. `WIKI` means the offline snapshot in `hoi4_wiki/` at the mod root. Installed documentation is more authoritative than the wiki. Use the hoi4 MCP reference routes (`hoi4_reference_context` with surface `idea`, `hoi4_reference_search`, `hoi4_reference_read`, `hoi4_source_lookup`) to cite exact line spans, and read the local file directly if a route fails twice.

Rules that always apply (full text in the references named):

- An idea `modifier = { }` block takes static numbers only. Variable-driven values, and any modifier on a state, unit leader or special project, need a dynamic modifier ([dynamic modifiers](references/dynamic-modifiers.md)).
- `research_bonus`, `equipment_bonus`, `rule` and `targeted_modifier` belong to ideas, advisors and leader traits. Dynamic modifiers reject them, and they never go inside `modifier = { }` ([idea fields](references/idea-files-and-fields.md)).
- `on_add` does not run when an idea is added from `history/countries` or a bookmark. `allowed_civil_war` defaults to false, so an event-granted spirit disappears at civil war unless it says otherwise ([idea fields](references/idea-files-and-fields.md)).
- Every modifier name must appear verbatim in `GAME/documentation/modifiers_documentation.md` with a category that matches the block's scope. A wrong name logs an error and does nothing.
- `picture` already gets the `GFX_idea_` prefix. An advisor character needs a unique `idea_token` ([spirits, laws and advisors](references/spirits-laws-and-idea-effects.md)).
- A dynamic modifier file cannot be hot-reloaded, and `scope =` must match on every add, check and removal ([dynamic modifiers](references/dynamic-modifiers.md)).

## Reference map

- [Sources and open questions](references/sources-and-open-questions.md): Read first to find the authoritative documentation and vanilla precedent for a topic, or before relying on a point the sources leave unverified. Covers: Contents; Source map; Unverified or conflicting points.
- [Idea files, slots and fields](references/idea-files-and-fields.md): Read before writing an idea, adding a slot or category, or deciding which idea field to use. Covers: Ideas: files, categories, slots; Idea body: every field that matters.
- [Spirits, laws and idea effects](references/spirits-laws-and-idea-effects.md): Read before defining a spirit, hidden idea, law, designer or advisor idea, or before scripting add, remove, swap or timed ideas. Covers: Spirits, hidden ideas, laws, designers, advisors; Adding, removing, swapping, and timing ideas.
- [Dynamic modifiers](references/dynamic-modifiers.md): Read before writing, attaching, scoping, refreshing or removing a dynamic modifier. Covers: Dynamic modifiers.
- [Static and custom modifiers, localisation and triggers](references/static-custom-modifiers-and-localisation.md): Read before defining a static, province, relation or custom modifier, or before writing idea and modifier localisation, icons and tooltips. Covers: Static, province, relation, and custom modifiers; Localisation, GFX, and tooltips; Idea and modifier triggers.

## Decision procedure: which mechanism

1. Constant country modifiers, visible in the politics screen: a national spirit (`country` category) added with `add_ideas`, or `add_timed_idea` when it expires.
2. A staged progression (levels 1 to 3 of the same theme): one idea per stage and `swap_ideas`; give the stages the same display name via `name =` so it reads as one upgraded idea.
3. A country modifier whose value depends on a variable, or any modifier on a state, unit leader, or special project: a dynamic modifier. Ideas cannot hold variables.
4. A bonus that is not a modifier (`research_bonus`, `equipment_bonus`, `rule`, `targeted_modifier`): an idea, advisor, or country leader trait; dynamic modifiers reject these.
5. An invisible bonus or marker: a `hidden_ideas` idea (it is a tokenised idea, and vanilla tests at least 161 of its 291 hidden ideas with `has_idea`), or a `hidden_modifier` block inside a visible idea. Prefer a country flag when you only need a boolean and no database token.
6. A modifier on one province: a static modifier from `common/modifiers` applied with `add_province_modifier`.
7. A modifier of one country towards another: `targeted_modifier = { tag = XXX ... }` in an idea, or a relation modifier with `add_relation_modifier`.
8. A numeric accumulator that other script reads (summed across ideas, traits, dynamic modifiers): a modifier definition in `common/modifier_definitions`, read as `modifier@name`.
9. A selectable political, economic, or manufacturer choice: a law, designer, or advisor category with `cost`, `available`, `visible`.
10. Diplomatic opinion: an opinion modifier, not a modifier (see below).

## How modifiers work

Source: `WIKI/modifiers.md`, intro and section Applying a modifier.

- A modifier is `name = number`. Values add: `political_power_gain = 0.2` and `political_power_gain = -0.05` from two sources give +0.15. A value of 0 does nothing. Booleans are numbers and must be 1 to have an effect. Modifiers have no `if`; use dynamic modifiers for conditions.
- Total value is readable as a variable: `set_variable = { v = modifier@political_power_gain }` in country or state scope; unit leaders use `unit_modifier@name` and `leader_modifier@name`. A modifier definition with no engine effect can still accumulate this way.
- Scope matters. `GAME/documentation/modifiers_documentation.md` groups modifiers under `country`, `state`, `unit_leader`, `scientist`, `army`, `naval`, `air`, and so on; each entry lists its **Categories**. Use a modifier only in a block whose scope matches one of its categories. A state modifier such as `local_building_slots` belongs in state categories, dynamic modifiers on states, buildings' `state_modifiers`, and `common/state_category` blocks.
- Template modifiers expand over database keys: `production_speed_<Building>_factor`, `production_cost_<Building>_factor`, `state_production_speed_<Building>_factor`, `<Building>_max_level_terrain_limit`, `local_resources_<Resource>_factor`, `state_resource_<Resource>`, `temporary_state_resource_<Resource>`, `country_resource_<Resource>`, `<IdeaGroup>_cost_factor` (for example `economy_cost_factor`), `<Technology>_cost_factor`, `<Ideology>_drift`, `experience_gain_<Unit>_combat_factor`, `unit_<Unit>_design_cost_factor`. Confirm the exact expanded name against the "Modified types" list in the documentation entry.
- Not modifiers: `research_bonus`, `equipment_bonus`, opinion modifiers (`common/opinion_modifiers`, applied with `add_opinion_modifier`).
- Modifier blocks accept `hidden_modifier = { ... }` (applies but is not shown) and `custom_modifier_tooltip = <loc key>` (shows your text as a line). Vanilla precedent: `GAME/common/ideas/italy.txt` and `czechoslovakia.txt`.
- Modifier values support up to three decimal places. [docs] `modifiers_documentation.md`
- Look up a modifier name by searching `modifiers_documentation.md` for the exact heading. A misspelled or nonexistent modifier name produces a log error and no effect; there is no autocorrect.

## Validation procedure

1. Every idea id is unique; its slot exists in `common/idea_tags` (or is `country` / `hidden_ideas`).
2. Every modifier name appears verbatim in `modifiers_documentation.md` with a category matching the block's scope; template modifiers expand to a listed "Modified type".
3. No variable inside an idea `modifier` block; variable-driven values live in a dynamic modifier.
4. Event-granted ideas have `allowed = { always = no }` and an explicit `allowed_civil_war` decision.
5. Add, remove, and swap pairs are balanced: each added idea has a removal path (explicit, `cancel`, timed, or intentional permanence).
6. For history-granted ideas, the `on_add` effect is replicated where the idea is added.
7. Localisation exists for the idea (and `_desc`), every `custom_modifier_tooltip` key, and each dynamic modifier name; sprite and `.gfx` entries exist for each `picture` and `icon`.
8. A dynamic modifier added in a state has its variables set in that state's scope; the first value is set before or in the same effect as the add, and `force_update_dynamic_modifier` is used if the value must apply immediately.
9. Use `hoi4_script_validate` on `on_add`, `on_remove`, and effect bodies under their explicit scope when exposed; it checks only its listed `checksPerformed`.
10. Live behaviour (daily refresh timing, tooltip rendering, civil-war survival) is a game-side check; do not report it as verified from source reading.

## Repository conventions

- Tabs for indentation, lowercase snake_case, no `<=` or `>=` (use `check_variable` with `compare = ...` or `<`, `>`), localisation UTF-8 with BOM, localisation keys written without `:0`.
- No magic numbers: put tuning in `common/script_constants/` and read it as `constant:category.key` where the field supports it. Idea `modifier` blocks accept literal numbers only (not variables), so a tunable value either uses a dynamic modifier fed by a variable set from a constant, or repeats a literal that is documented once in the idea file header. Timed `days =` fields may need a variable assigned from a constant first.
- Declare `fixed_point` in a script constant group that holds non-integers, since vanilla's `propaganda_campaigns.txt` declares `int` yet stores 1.35. [vanilla-confirmed 1.19.3]
- Reloading only the constant database leaves stale values, because the database that consumes the constant must reload too. [docs]
- Reuse the project's dynamic scripted effects library (`common/scripted_effects/<prefix>_dynamic_effects.txt`, named in `CLAUDE.md`) before writing new helpers; document new dynamic effects in its documentation file as `CLAUDE.md` requires.
- On-action fan-out (`on_daily`, `on_weekly`, `on_monthly`) over all countries to refresh ideas or dynamic modifiers needs explicit permission; refresh from the effect that changes the underlying variable instead.
- Player-facing idea text describes the world and the player's options, not tuning history or "newly added" wording.
- Use `hoi4-mtth` for MTTH-fed variables and `hoi4-decisions-missions` when a decision grants or swaps the idea.

## Common mistakes and silent failures

1. Variables inside an idea `modifier` block (ignored or wrong); use a dynamic modifier.
2. `research_bonus` or `equipment_bonus` placed inside `modifier = { }` or a dynamic modifier.
3. `picture = GFX_something` (prefixed twice) or a sprite not named `GFX_idea_*`; the error icon shows.
4. Expecting `on_add` to run from `history/countries` or a bookmark.
5. A spirit lost at civil war because `allowed_civil_war` was left at its false default.
6. Editing a dynamic modifier file and expecting a hot reload.
7. A state dynamic modifier reading the owner's variable instead of the state's.
8. Waiting for a dynamic modifier's tooltip to show variable values; it does not.
9. Using `<slot>_cost_factor` where the slot's ideas load later than the idea file (error), including capitalised file names.
10. A misspelled or wrong-scope modifier name; the log shows an error and the modifier does nothing.
11. Leaving a previous stage idea behind after a progression; check that the old idea is present before `swap_ideas` (behaviour when it is absent is undocumented).
12. Advisor characters without an `idea_token` (other token-less advisors vanish).
13. Putting tag or DLC checks in `visible` instead of `allowed`.
14. Adding a hidden idea for a boolean that a country flag would express more cheaply.
15. Reusing one dynamic modifier on two scopes and removing it without the matching `scope =`.
16. Forgetting that modifiers of the same name add rather than compound, so two `-0.5` factors from different sources sum to -1.0 (whether the engine clamps the result is not documented).
17. A zero-valued modifier left in a block (no effect) or a boolean modifier set to something other than 1.
18. Adding a timed idea with no unit field; one of `days`, `months`, `years` is mandatory.
19. Player text that mentions removed or reworked ideas.
20. Correcting the spelling of `foreign_subversive_activites`, because the game token is the misspelled form (72 vanilla uses). [docs]
21. Placing naval `*_against` modifiers or `river_crossing_factor_against` directly in `modifier`, when they belong inside `targeted_modifier = { tag = ... }`. [vanilla-confirmed 1.19.4.1]

