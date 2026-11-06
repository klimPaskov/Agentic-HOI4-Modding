---
name: hoi4-diplomacy-war
description: Use when scripting Hearts of Iron IV diplomacy, factions, subjects, autonomy, wargoals, war and peace, guarantees, military access, opinion modifiers, annexation, release or state transfers.
---

# HOI4 Diplomacy and War

Generic guidance for scripting relations between countries: factions, subjects, wargoals, war, peace, and territory transfer.
Use it to choose the right mechanism, write it with verified syntax and scopes, and avoid the silent failures.
Use `hoi4-ai-strategies` for steering how the AI uses these systems (`conquer`, `befriend`, `diplo_action_*`, peace desires), `hoi4-decisions-missions` for decision and mission structure, and `hoi4-events` for event wiring when working in this repository.

This file is a router. It keeps the mechanism table, scope rules, validation list, repository conventions and mistake list that apply to every task. Open the reference for your mechanism from the map below before you write exact syntax.

Rules that always apply (full text in the references named):

- Check the scope direction of every effect (kept below under Scope and target rules). `set_autonomy` and `release_autonomy` run in the overlord's scope, `add_autonomy_score` in the subject's, `add_to_faction` in the scope of a country already in the destination faction, and `transfer_state` in the receiver's.
- `puppet` picks a `default = yes` autonomous state whose `allowed` is true and crashes when none qualifies. Pass `end_wars` and `end_civil_wars` to `set_autonomy` explicitly. See [Subjects, autonomy and territory](references/subjects-autonomy-and-territory.md).
- Every decision, mission or event that ends in war needs `war_with_on_*` so the AI prepares, and `declare_war_on` needs a defined wargoal type. See [Wargoals, war and peace](references/wargoals-war-and-peace.md).
- Guard targets with `country_exists`, and copy on-action names exactly, because a misspelled hook fails silently. See [Relations, hooks and localisation](references/relations-hooks-and-localisation.md).
- Faction rules need a rule group and the vanilla plural `type` names. See [Factions](references/factions.md).
- The user performs in-game checks; do not launch the game.

Existing references: [syntax-reference.md](references/syntax-reference.md) holds the exact effect and trigger parameters, the autonomy game rules, faction rule types, the vanilla file index, faction goals and manifests detail, the on-action scope table and the scripted diplomatic action skeleton. Read it for exact parameters and before relying on ROOT or FROM in an on action. [intelligence-operations.md](references/intelligence-operations.md) covers intelligence agencies, operations and agency upgrades.

## Reference map

- [Source map](references/source-map.md): Read to find the authoritative documentation, wiki page and vanilla precedent for a diplomacy topic before you cite or mirror it. Covers: Contents; Source map.
- [Factions](references/factions.md): Read before creating or changing factions, faction templates, rules, rule groups, goals or manifests. Covers: Factions.
- [Subjects, autonomy and territory](references/subjects-autonomy-and-territory.md): Read before scripting puppets, autonomous states, release, annexation or state transfer between countries. Covers: Subjects and autonomous states; Territory, release, annexation, and puppets.
- [Wargoals, war and peace](references/wargoals-war-and-peace.md): Read before defining wargoal types, declaring or joining wars, warning the AI, or scripting white peace and peace conferences. Covers: Wargoals, declaring war, and joining wars; Peace.
- [Relations, hooks and localisation](references/relations-hooks-and-localisation.md): Read before scripting guarantees, access, embargoes or opinion modifiers, writing on-action handlers or scripted diplomatic actions, or adding AI hooks and diplomacy localisation. Covers: Diplomatic relations; On actions for diplomacy and war; Scripted diplomatic actions; AI hooks; Localisation and tooltips.

## Decision procedure: which mechanism

| Intent | Use | Notes |
| --- | --- | --- |
| Put a country under another at game start | `puppet` or `set_autonomy` in the overlord's scope in `history/countries` | Place before political setup in the subject's history, see the subject section. |
| Change a subject's level during play | `set_autonomy` in the overlord's scope | Use `add_autonomy_score` or `add_autonomy_ratio` in the subject's scope to move gradually. |
| Make a subject independent | `set_autonomy` with `autonomy_state = autonomy_free` in the overlord's scope, or `end_puppet` | `set_autonomy` has to run in the current overlord's scope. |
| Create a new country as a subject from owned or controlled land | `release_autonomy`, `release_puppet`, `release_puppet_on_controlled`, `release_on_controlled` | These do nothing if the country already exists. |
| Annex a country | `annex_country = { target = X transfer_troops = yes }` | Omitting `transfer_troops` loses the annexed divisions' equipment. |
| Move one state between countries | `transfer_state` (country scope, state argument) or `transfer_state_to` / `set_state_owner_to` (state scope) | Ownership and control differ between these. |
| Put countries in or out of a faction | `create_faction_from_template`, `add_to_faction`, `remove_from_faction`, `leave_faction`, `dismantle_faction` | Needs the `can_create_factions` rule to be allowed. |
| Restrict who may join or lead a faction, or declare war inside it | Faction rules in `common/factions/rules` | Install them through templates or `set_faction_rule`. |
| Give a faction a quest | Faction goals and manifests | Needs the Deeper Factions DLC feature set per the wiki. |
| Open or close a bilateral relation (guarantee, military access, NAP, docking, air base, embargo) | `diplomatic_relation`, `give_guarantee`, `give_military_access`, `send_embargo`, `give_market_access` | `diplomatic_relation` with `active = no` is the documented way to end one. |
| Change how much a country likes another | `add_opinion_modifier`, `reverse_add_opinion_modifier`, `remove_opinion_modifier` with a modifier defined in `common/opinion_modifiers` | Direction matters. |
| Apply a targeted modifier between two countries | `add_relation_modifier` with a modifier from `common/modifiers` | Different system from opinion. |
| Let the player propose a custom accept/reject offer to other countries | `common/scripted_diplomatic_actions` | See the section below. |
| Prepare a war the player or AI must justify | `create_wargoal`, then `declare_war_on` or the player's own diplomacy | Pair decisions with `war_with_on_*`. |
| Force a war immediately | `declare_war_on = { target = X type = <wargoal> }` | Needs a defined wargoal type. |
| Pull a country into an existing war | `add_to_war` | Not a declaration against a new enemy. |
| End a war with no winner | `white_peace` | ROOT counts as winner for name and on-action purposes. |
| End a war with spoils | `start_peace_conference` (limited conference) | Score fraction controls the outcome. |
| React after the fact | On actions (`on_declare_war`, `on_peaceconference_ended`, `on_join_faction`, `on_subject_free`, ...) | Mind the ROOT and FROM meanings. |
| Block or enable a diplomatic capability without a new mechanism | `set_rule`, or `rule` in an autonomous state, or faction rules | Rules are overrides; see the rule notes. |

## Scope and target rules

- Diplomacy and war effects execute in the scope of the acting country; the argument is the other party. `GER = { declare_war_on = { target = POL type = take_state } }` makes Germany the aggressor.
- Direction conventions that are easy to reverse:
  - `add_opinion_modifier`: the scoped country gains opinion toward `target`. `reverse_add_opinion_modifier`: `target` gains opinion toward the scoped country. For a modifier flagged `trade = yes` the behaviour is reversed.
  - `add_to_faction = X`: X joins the scoped country's faction. `remove_from_faction = X`: removes X from the faction the scoped country leads. `leave_faction = yes`: the scoped country leaves.
  - `puppet = X`, `release_puppet = X`, `end_puppet = X`, `annex_country = { target = X }`: the scoped country is the overlord or annexer.
  - `set_autonomy`, `release_autonomy`: run in the overlord's scope with `target = subject`. `add_autonomy_score` and `add_autonomy_ratio`: run in the subject's scope.
  - `give_guarantee = X` and `give_military_access = X`: the scoped country gives them to X. Mutual access needs two calls (vanilla `common/decisions/BEL.txt`).
  - `send_embargo = X`: scoped country embargoes X. `break_embargo = X` always applies to ROOT per the wiki, so use `diplomatic_relation` with `relation = embargo` to break another country's embargo.
  - `white_peace = X` and `start_peace_conference`: the scoped country is the winner.
  - `transfer_state` acts in the receiving country's scope; `transfer_state_to` acts in the state scope.
- Targets can be tags, scopes (`ROOT`, `PREV`, `FROM`, `OWNER`, `CONTROLLER`, `OCCUPIED`, `CAPITAL`), or variables (`target = var:my_var`, or a scoped variable name). Diplomatic effects list `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL` as supported targets in the effects documentation.
- A removed or non-existent country is not a valid scope. Guard with `country_exists = TAG` (or `exists = yes` on a stored variable scope) before targeting it.
- Temporary variables carry no scope; use normal variables or event targets to remember countries across scope changes.

## Validation

1. Confirm the scope of every effect: acting country, target, and whether the effect expects overlord or subject scope.
2. Confirm every wargoal type, autonomy state, faction template, rule, goal, opinion modifier, and relation modifier id exists (`hoi4_source_lookup`).
3. Check the guard: `country_exists`, `is_subject = no`, `has_war_with`, and `has_capitulated` as required, so the effect cannot fail silently or crash.
4. Check that every war-causing decision, mission, or event declares its target to the AI (`war_with_on_*`).
5. Check on-action scope assumptions against the wiki table.
6. Use `hoi4_script_validate` for an effect or trigger body under its explicit scope. A true result covers only the listed checks; parameter semantics and engine behaviour remain separate evidence.
7. Source review and tools do not prove live behaviour. The user performs in-game validation; do not launch the game.

## Repository conventions

These follow the project rules in `CLAUDE.md`, which remain the authority.

- Tabs, lowercase snake_case, no `<=` or `>=`, no magic numbers (use `common/script_constants` via `constant:category.key` where the field parses it, else variables or `@` constants).
- Reuse the project's dynamic scripted effects library (`common/scripted_effects/<prefix>_dynamic_effects.txt`, named in `CLAUDE.md`) and document any new dynamic effect in its documentation file as `CLAUDE.md` requires.
- Never use `on_daily`, `on_weekly`, or `on_monthly` world-iterating hooks without explicit permission; prefer the event-style on actions above or `on_daily_TAG` for a named country.
- Do not write markers about update history in localisation or player text.
- Keep event-, route-, or country-specific content out of reusable skill files.

## Common mistakes

1. Running `set_autonomy` in the subject's scope; it needs the overlord's scope.
2. Assuming `puppet` always creates `autonomy_puppet`; it picks a `default = yes` state allowed for that overlord, and crashes when none exists (wiki).
3. Using `release_*` on a country that already exists (no effect) or expecting it to move states the releaser does not own.
4. Reversing `add_opinion_modifier` and `reverse_add_opinion_modifier`, or forgetting the reversal for `trade = yes` modifiers.
5. Calling `add_to_faction` from the joiner's scope; the scoped country must be in (or lead) the destination faction.
6. Using `break_embargo` for a third country; it only applies to ROOT.
7. Using singular faction rule type names from the documentation comment instead of vanilla's plural names.
8. Defining a faction rule that belongs to no rule group, so it never appears (rules need at least one group).
9. Declaring war from a decision or event without `war_with_on_*` so the AI never prepares.
10. Using a nonexistent wargoal id (for example the wiki's `puppet_focus_wargoal`); verify ids in `common/wargoals`.
11. Using `declare_war_on` when `add_to_war` is meant (joining an ally's war), or the reverse.
12. Expecting `white_peace` to end a faction-wide war: it pairs two countries.
13. Reading `FROM` in faction goal effect blocks; it is unsupported there.
14. Targeting a non-existent or capitulated country without a guard.
15. Using `transfer_state` in the giver's scope; the argument is the state, scope is the receiver.
16. Setting autonomy in history after political setup, or only in the overlord file, and getting wrong ideology.
17. Leaving two autonomous states with the same `min_freedom_level`.
18. Writing unlocalised opinion modifiers, rules, goals, or `war_name` keys.

## Unverified or conflicting points

- No installed documentation covers `common/autonomous_states` or `common/wargoals`; their field lists come from the wiki and vanilla files.
- `end_wars` default for `set_autonomy`: installed effects documentation says yes, wiki says no. Pass explicitly.
- `autonomy_state` versus `autonomous_state` spelling: both occur in vanilla scripts; only `autonomy_state` is in the installed documentation example.
- Faction rule `type` spelling: vanilla plural versus documentation singular.
- `common/scripted_diplomatic_actions` ships only as a commented template; the skeleton is unconfirmed against a live vanilla action.
- `diplomatic_relation relation = puppet` exists in vanilla (2 uses); prefer `puppet` and `end_puppet`, whose semantics are documented.
