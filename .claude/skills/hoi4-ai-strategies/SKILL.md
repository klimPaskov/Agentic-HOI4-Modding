---
name: hoi4-ai-strategies
description: Use when designing, tuning or debugging HOI4 country AI, from ai_strategy blocks, add_ai_strategy and strategy plans to AI focuses, ai_will_do and ai_chance weights, and AI templates.
---

# HOI4 AI Strategies

Generic guidance for steering the Hearts of Iron IV country AI from mod script.
Use it to choose the right AI mechanism, write it with verified syntax, tune weights without misreading score as probability, and debug the result.
Use `hoi4-mtth` for MTTH variables and centralised weight logic, `hoi4-decisions-missions` for decision and mission `ai_will_do`, `hoi4-focus-trees` for focus `ai_will_do`, and `hoi4-diplomacy-war` for the diplomacy, faction, subject, wargoal, and peace mechanics that AI strategies steer.

Choose the narrowest mechanism with the decision procedure below, then open only the reference for the phase of work. This file also keeps the debugging and verification routine, the repository conventions and the common-mistakes list, which apply to every task.

`GAME` means the installed Hearts of Iron IV folder named in `CLAUDE.md`. `WIKI` means the offline snapshot in `hoi4_wiki/` at the mod root. Installed documentation is more authoritative than the wiki. Use the hoi4 MCP reference routes (`hoi4_reference_context` with surface `ai`, `hoi4_reference_search`, `hoi4_reference_read`, `hoi4_source_lookup`) to cite exact line spans, and read the local file directly if a route fails twice.

Rules that always apply (full text in the references named):

- A strategy `value` is not a probability, and two `ai_will_do` values are not a ratio of chances. Each strategy type defines its own meaning, so read its token entry before choosing a number ([weight semantics](references/weight-semantics.md)).
- Strategies of the same type and target from every active block add up. A country override must exclude the generic block in its `enable`, or it double-counts ([strategy blocks](references/strategy-blocks-and-add-ai-strategy.md)).
- Every `common/ai_strategy` block needs `abort` or `abort_when_not_enabled`, and `allowed` is checked only once at start.
- `add_ai_strategy` is permanent and has no removal effect. Anything temporary or conditional is a flag-gated `common/ai_strategy` block.
- `ai_will_do` is a weight, not a gate. Eligibility belongs in `available` or `allow`, and a decision without `ai_will_do` is never taken.
- Do not add `on_daily`, `on_weekly` or `on_monthly` hooks for AI behaviour without permission. Agents never launch the game, so console debug commands are for the player.

Two deeper references already exist:

- [Strategy token catalog](references/strategy-token-catalog.md): read when you need the exact parameters, ids, value semantics or unit-ratio arithmetic of a specific `ai_strategy` type (production, market, front, navy, intelligence, research, XP and PP spend).
- [Other AI systems](references/other-ai-systems.md): read when you touch `common/ai_templates`, `common/ai_equipment`, `common/ai_navy`, `common/ai_faction_theaters`, `common/peace_conference/ai_peace`, `ai_attitudes`, or the AI-facing blocks of factions, autonomy and scripted diplomatic actions.

## Reference map

- [Sources and open questions](references/sources-and-open-questions.md): Read first to find the authoritative text and vanilla precedent for each AI surface, or before relying on a point the sources leave open. Covers: Contents; Source map; Unverified or conflicting points.
- [Weight semantics](references/weight-semantics.md): Read before writing or tuning any ai_will_do, ai_chance or strategy value, and before comparing two weights. Covers: Weight semantics.
- [Strategy blocks and add_ai_strategy](references/strategy-blocks-and-add-ai-strategy.md): Read before writing a common/ai_strategy block, judging how it stacks with others, or using add_ai_strategy. Covers: common/ai_strategy: structure and lifecycle; add_ai_strategy and flag-gated strategies.
- [Strategy families and common tokens](references/strategy-families-and-common-tokens.md): Read to pick a diplomacy, front, production or research strategy type and its typical values before opening the full token catalog. Covers: Strategy families and the common tokens.
- [Strategy plans, AI focuses and AI areas](references/strategy-plans-ai-focuses-and-areas.md): Read before writing an AI strategy plan, an AI focus posture, research weights on a technology or an AI area. Covers: AI strategy plans; AI focuses, research weights, and AI areas.

## Decision procedure: which mechanism

Pick the narrowest mechanism that expresses the intent.
Reaching for a global strategy when a local `ai_will_do` suffices is the most common over-reach.

| Intent | Mechanism | Notes |
| --- | --- | --- |
| Make the AI take or avoid one decision, mission, focus, idea, advisor, tech, MIO policy, faction rule, or faction goal | `ai_will_do` on that object | Decisions are never picked without an `ai_will_do` (Decision modding wiki, AI section). |
| Make the AI pick one event option over another | `ai_chance` on the option | Proportional weights, effective resolution 1 percent. |
| Steer who the AI befriends, antagonizes, ignores, guarantees, allies with, attacks, or sends aid to | `ai_strategy` types `befriend`, `antagonize`, `ignore`, `alliance`, `protect`, `conquer`, `declare_war`, `support`, `send_lend_lease_desire`, `send_volunteers_desire` | Targeted by `id = TAG`. |
| Make the AI accept or request one specific diplomatic action | `diplo_action_acceptance` / `diplo_action_desire` with `target = <action>` | Acceptance does not raise desire to propose, and the reverse. |
| Change what the AI builds, produces, researches, or spends | production, market, research, XP and PP strategy types | See the token catalog. |
| Change troop distribution, fronts, invasions, garrisons | `area_priority`, `front_control`, `front_unit_request`, `invasion_unit_request`, `put_unit_buffers`, `force_defend_ally_borders` | Needs `ai_areas` for `area`. |
| Give a country a long-lived overall plan (focus order, research bias, advisors, strategies) | `common/ai_strategy_plans` | Preferred over `ai_historical_focus_list`. |
| Change which research categories a general AI posture favours | `common/ai_focuses` | Per-country via tag postfix. |
| Force a condition-gated strategy that can later be undone | `common/ai_strategy` block with `enable` / `abort` keyed on a flag | Prefer over `add_ai_strategy` when reversibility matters. |
| One-shot permanent nudge from a focus, decision, or event | `add_ai_strategy` effect | Cannot be removed by an effect; see below. |
| Influence division design or composition | `common/ai_templates` plus `role_ratio` and `template_prio` strategies | Reference file. |
| Influence tank, plane, or ship variant design | `common/ai_equipment` | Reference file. |
| Influence naval missions | `common/ai_navy` goals, taskforce and fleet templates, `naval_*` strategies | Reference file. |
| Influence post-war outcomes the AI picks | `common/peace_conference/ai_peace` `peace_ai_desires`, plus `use_for_peace_conference_weight` in autonomous states | Reference file. |
| Tune a global AI behaviour constant | `NAI` defines | Last resort; affects every country and every mod system. |

## Debugging and verification

Console commands (GAME/documentation/console_commands_documentation.md; the player runs them in game, agents do not launch the game):

| Command | Use |
| --- | --- |
| `aiview` | Overlay AI debug information; with plans, shows names and descriptions. |
| `ai_trace` | AI trace window (not in release builds). |
| `ai_dump` / `aidump` | Dump AI data to the log (not in release builds). |
| `ai_front_dump` | Dump front data for the selected unit. |
| `ai_research_log` | Toggle research decision logging (not in release builds). |
| `ai_pp_log` | Political power spend log. |
| `ai_idea_desire_log` | Idea desire log for the current country. |
| `ai_accept` / `yesman` | Make the AI accept all diplomacy. |
| `ai_force_template`, `ai_force_equipment` | Force XP spend on templates or equipment. |
| `imgui show ai_templates`, `imgui show ai_division_production`, `imgui show ai_navy` | Template, division demand, and naval goal debug UIs named in the template and navy documentation. |
| `tdebug`, `debug` | Province, state, and strategic region ids. |

Repository verification without launching the game:

1. Read the actual block and compute representative cases by hand. For `ai_will_do`, `ai_chance`, strategy plans and MTTH-backed weights prefer `hoi4_probability_inspect` (adapters: `event_option_ai_chance`, `decision_ai_will_do`, `mission_ai_will_do`, `national_focus_ai_will_do`, `technology_ai_will_do`, `doctrine_ai_will_do`, `ai_strategy_factor`, `random_list`, `direct_random`, `custom_weighted_pool`, `event_mean_time_to_happen`), then `hoi4_probability_inspect` or `hoi4_probability_analyze` with `analysis: "compare"` with explicit named scenarios (country, date, flags, government, factory counts).
2. Report assumptions, and state whether a number is a score, a share of a proportional pool, or a random-draw win chance.
3. Use `hoi4_script_validate` for trigger and effect bodies in the right scope.
4. Use `hoi4_source_lookup` for every other active definition of the same strategy type and target, so stacking is visible.
5. Remember the analyzer models source, not observed game behaviour; the AI's runtime inputs (threat, factories, borders) are not simulated.
6. If a probability route fails on invalid inputs, retry once with corrected inputs, then calculate from the source and say so.

## Repository conventions

These follow the project rules in `CLAUDE.md`, which remain the authority.

- Tabs for indentation, lowercase snake_case, no `<=` or `>=` (use `check_variable` with `compare = ...` where a comparison is needed and the short `<` and `>` elsewhere).
- No magic numbers: put shared tuning values in `common/script_constants/` and read them with `constant:category.key` where the field supports it. Several AI strategy fields may not parse `constant:`; then use an `@` file constant or compute a variable first. Verify per field.
- Reuse the project's dynamic scripted effects library (`common/scripted_effects/<prefix>_dynamic_effects.txt`, named in `CLAUDE.md`); document any new dynamic effect in its documentation file as `CLAUDE.md` requires in the same change.
- Use `hoi4-mtth` for MTTH variables and to keep `ai_will_do` readable.
- `on_daily`, `on_weekly`, and `on_monthly` iterate over every country; do not add them to implement AI behaviour without explicit permission. Gate behaviour in `common/ai_strategy` `enable` blocks instead, which the engine already evaluates.
- A flag trigger inside a player-visible requirement block shows its raw identifier unless localised; AI-only gating belongs in `ai_will_do` or `enable`, which are not player-visible.
- Do not write player-facing text describing AI tuning history.

## Common mistakes

1. Treating `value` as a probability or comparing values across unlike types.
2. Forgetting that same-type, same-target strategies from every active block add up; a country override that does not exclude the generic block double-counts.
3. Omitting `abort` or `abort_when_not_enabled`, leaving a strategy permanently active after `enable` turns false.
4. Putting time-varying conditions in `allowed` (checked once at start).
5. Using `add_ai_strategy` for something that must end, then having no way to end it.
6. Expecting `conquer` to change frontline behaviour (it does not) or `front_control` to create units.
7. Giving a decision or mission no `ai_will_do` and wondering why the AI never takes it.
8. Relying on `ai_will_do` for eligibility; the AI weight does not stop the player or other scripts.
9. Reading focus `ai_will_do` ratios as probabilities; the random draw favours large values.
10. Giving a focus a strategy-plan `focus_factors` of 0 and forgetting that `ai_national_focuses` can still force it.
11. Leaving two role-level AI templates active for the same country and role (undefined behaviour per the template documentation).
12. Using the wiki's `AI areas` example without the `areas = { }` wrapper that vanilla uses.
13. Using a negative `protect` value expecting only a reduction; a negative total stops guaranteeing entirely.
14. Using a numeric `id` where a tag is required (or the reverse); state, region, and tag ids are not interchangeable.
15. Designing AI-only behaviour that only works for one scripted route, then having a different route silently disable it. Test each route's flags.
16. Leaving debug `log` effects in the finished script.
17. Using weekly or daily on_actions to poll for AI state when an `enable` trigger would do.

