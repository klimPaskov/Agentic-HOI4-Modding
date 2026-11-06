---
name: hoi4-characters-leaders
description: Use when defining, recruiting, promoting or retiring HOI4 characters and their roles (leaders, advisors, commanders, scientists), leader traits, ideologies, portraits and localisation.
---

# HOI4 Characters, Leaders and Traits

Generic HOI4 modding guidance for the character system introduced in patch 1.11.
Divisions, templates, orders of battle and manpower belong to `hoi4-units-divisions`.
Weighted AI choices (`ai_will_do`, `new_commander_weight` tuning) belong to `hoi4-ai-strategies`.
Portrait production (research, placeholders, the configured image generator, DDS, wiring, manifests) belongs entirely to `hoi4-feature-assets` and the `hoi4_portrait_creator` subagent; this skill only covers how a portrait is referenced from a character.
Unit-leader trait schema, selection trees, experience rules and abilities are in `references/unit-leader-traits.md`.
Exact signatures and scope notes of the character effects and triggers are in `references/effects-triggers.md`.

Read the mental model and decision table below, then open only the reference for the phase of work. This file also keeps the repository conventions, the silent-failure list and the validation checklist, which apply to every task.

Rules that always apply (full text in the references named):

- A character does nothing until a country recruits it: `recruit_character` in country history, before `set_politics`, and never as the last line of the file ([lifecycle](references/runtime-lifecycle-and-scopes.md)).
- A role's `ideology` is an ideology type such as `liberalism`, never a group such as `democratic`, and a country leader `desc` must be a localisation key ([country leader role](references/country-leader-role-and-traits.md)).
- An advisor needs a unique `idea_token`. `on_add` and `on_remove` run in character scope (reach the country with `owner`), and a role added by effect cannot carry `visible`, `available` or `on_add` blocks ([advisor and other roles](references/advisor-unit-leader-and-scientist-roles.md)).
- Country leader traits (`common/country_leader/`) and unit leader traits (`common/unit_leader/`) are different databases.
- A wrong portrait sprite name silently shows a random portrait. This skill only wires the reference; portrait production goes to `hoi4-feature-assets` and the `hoi4_portrait_creator` subagent ([definition and portraits](references/character-definition-and-portraits.md)).
- Read the vanilla precedent for every role and effect before writing it ([required reading](references/required-reading-and-precedents.md)).

Two deeper references already exist:

- [Effects and triggers](references/effects-triggers.md): read before using any character effect or trigger, for exact signatures and scope notes.
- [Unit leader traits](references/unit-leader-traits.md): read before authoring `common/unit_leader/` traits, selection trees, experience rules or abilities.

## Reference map

- [Required reading and precedents](references/required-reading-and-precedents.md): Read before writing or reviewing any character script, to find the authoritative documentation and the vanilla files to mirror. Covers: Contents; Required reading and vanilla precedents.
- [Character definition, portraits and localisation](references/character-definition-and-portraits.md): Read before writing a character entry, wiring its portrait sprites, or localising characters, traits and parties. Covers: Character definition; Portraits and GFX wiring (overview); Localisation.
- [Country leader role and leader traits](references/country-leader-role-and-traits.md): Read before defining a country_leader role, ideology and party wiring, or a country leader or unit leader trait. Covers: Country leader role, ideologies and parties; Country leader traits (also used by advisors and ideas); Unit leader traits (summary).
- [Advisor, unit leader and scientist roles](references/advisor-unit-leader-and-scientist-roles.md): Read before defining an advisor, field marshal, corps commander, admiral or scientist role. Covers: Advisor role; Unit leader roles; Scientists and operatives.
- [Runtime lifecycle, generated characters and scopes](references/runtime-lifecycle-and-scopes.md): Read before scripting recruitment, promotion, retirement, transfer or generate_character, or before writing character triggers and scope iteration. Covers: Lifecycle at runtime; Generated characters; Triggers and scopes.

## Mental model and decision table

- A character is a database entry in `common/characters/` that can hold several roles at once: `country_leader` (one per ideology type), `advisor` (one per slot), one army or navy command role, and a `scientist` role.
- Defining a character does nothing. Each character must be recruited by a country with `recruit_character` in country history (or by `generate_character`). Unrecruited characters never appear.
- Operatives are not characters; they use `create_operative_leader` and are out of scope here.
- Roles can be declared in the character file or added later by effect. A role added by effect cannot carry script blocks (see advisors).

| I want to... | Use |
| --- | --- |
| Add a named historical person with fixed roles | Entry in `common/characters/*.txt` plus `recruit_character` in history |
| Hold a person back until an event happens | Define without the role and add it with `add_*_role`, or keep the role and gate it with `visible` |
| Have a leader exist in several ideologies | Several `country_leader` blocks in one character |
| Change who rules | `promote_character`, or `add_country_leader_role` with `promote_leader = yes` |
| Remove someone from power but keep them | `remove_country_leader_role`, or just promote another character |
| Remove someone permanently | `retire_character` (country scope) or `retire` (character scope) |
| Move a person to another country | `set_nationality` (works on any character; also used to bring back a retired one per the character wiki) |
| Create many anonymous advisors/leaders | `generate_character` templates in `history/general/` |
| Show an advisor only under a condition | `advisor = { visible = { ... } available = { ... } }` in the character file |
| Change a name or portrait in play | `set_character_name`, `set_portraits`, `set_leader_name`, `set_leader_portrait` |
| Per-leader state | `set_character_flag`, `has_character_flag` (character scope) |
| Give a trait the player can pick or earn | Unit leader trait in `common/unit_leader/`; advisor and leader traits in `common/country_leader/` |

## Repository conventions

These follow the project rules in `CLAUDE.md`, which remain the authority:

- Tabs, lowercase snake_case, no `<=` or `>=` (use `check_variable` with `compare`), no magic numbers: costs, skill levels used in formulas, thresholds and durations go in `common/script_constants/` (`constant:category.key`); copy to a variable where a field rejects constants.
- Reuse the project's dynamic scripted effects library (`common/scripted_effects/<prefix>_dynamic_effects.txt`, named in `CLAUDE.md`) before writing bespoke logic and document new dynamic effects in its documentation file as `CLAUDE.md` requires in the same change. Use `meta_effect` for fields that reject variables.
- Do not add world-wide `on_daily`, `on_weekly` or `on_monthly` hooks for characters without explicit permission; scope iterations to one country.
- Document each new script file with an overview comment at the top, keep a docs file for the mechanic, and list icons, `.gfx` files and portrait sprite names in it.
- Use the portrait route above for every character portrait; placeholders stay documented as pending until the final art exists.
- Never launch the game to test; the user validates live.

## Common mistakes and silent failures

- Defining a character and never recruiting it: it never appears.
- `recruit_character` as the last line of a history file: no recruitment (wiki).
- Recruiting leaders after `set_politics`: a random leader was already generated, so the intended leader is not the ruler.
- Two leaders of the same ideology group recruited: the first wins; the other stays a candidate until `promote_character`.
- `promote_character` for a multi-role character without `ideology`: the effect has no unique role to promote.
- `ideology = democratic` (a group) in a role: must be a type such as `liberalism`.
- `desc =` with literal text: not shown; must be a loc key.
- Missing `idea_token` on an advisor: other tokenless advisors vanish.
- `on_add` expecting country scope: it is character scope; use `owner`.
- Putting `visible`/`available`/`on_add` inside `add_advisor_role`: script is not supported there.
- Unit leader traits listed on a character but not defined in `common/unit_leader/`, or country traits defined in the wrong folder: trait ignored.
- Expecting `research_bonus` or `rule` in a country leader trait: unsupported.
- A trait icon `sprite = N` beyond the strip frame count: wrong or no icon.
- Portrait sprite typo or wrong extension: a random portrait appears instead and nothing errors.
- Army leader without a small portrait: officer-corps minister portrait problems (also true for deprecated `create_*`).
- `retire_character` when you may want the person back: conflicting documentation; test or use role removal.
- Using `kill_country_leader` when a specific person must be removed: it hits whoever currently rules.
- `every_unit_leader` ignoring hidden leaders: add `include_invisible = yes` when the audit needs them.
- Using `generate_character` mid-game with no history-registered template: no character is generated.

## Validation checklist

1. Read the vanilla precedent for each role and effect used; mirror its structure.
2. For each character: unique id, `name` key exists, every referenced trait exists in the correct database, every portrait sprite exists in a `.gfx` file with an existing texture, recruited in history of the right tag, `idea_token` unique and localised for advisors.
3. For country leaders: ideology type valid, `expire` after the start date, recruited before `set_politics`, party leader resolves as expected for the start date.
4. For runtime scripts: right scope (country versus character), guards (`has_character`, `is_*` role triggers, flags) to keep effects idempotent, hidden effects with visible tooltips, no unbounded all-country iteration.
5. For traits: sprite frame exists, modifiers exist for the scope, `ai_will_do` and `new_commander_weight` reviewed (see `hoi4-ai-strategies`), localisation present.
6. Use `hoi4.script_validate` for effect and trigger bodies under their explicit scope when exposed; its true result covers only the listed checks.
7. In the report, separate what is source-verified from what is wiki-only or untested in game.
