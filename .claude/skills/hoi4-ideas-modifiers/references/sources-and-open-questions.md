# HOI4 Ideas and Modifiers: Sources and open questions

Part of the [hoi4-ideas-modifiers](../SKILL.md) skill. Read first to find the authoritative documentation and vanilla precedent for a topic, or before relying on a point the sources leave unverified.

## Contents

- Source map: where the authoritative text lives
- Decision procedure: which mechanism for which goal
- How modifiers work
- Ideas: files, categories, slots
- Idea body: every field that matters
- Spirits, hidden ideas, laws, designers, advisors
- Adding, removing, swapping, and timing ideas
- Dynamic modifiers
- Static, province, relation, and custom modifiers
- Localisation, GFX, and tooltips
- Idea and modifier triggers
- Validation procedure
- Repository conventions
- Common mistakes and silent failures
- Unverified or conflicting points

## Source map

`GAME` means the installed Hearts of Iron IV folder named in `CLAUDE.md`.
`WIKI` means the offline snapshot in `hoi4_wiki/` at the mod root.
Installed documentation is more authoritative than the wiki; where they disagree, follow the installed file and record the conflict.

| Topic | Authoritative text | Vanilla precedent |
| --- | --- | --- |
| Idea fields, categories, slots, cost, hidden ideas, slot cost modifiers | `WIKI/idea_modding.md` | `GAME/common/ideas/_event.txt` (event-granted spirits and a hidden idea), `_economic.txt` and `_manpower.txt` (laws), `GER.txt` (designers `tank_manufacturer`, advisors, `custom_modifier_tooltip`), `_debug_spirits.txt` |
| Idea categories and slots | same page, section Categories | `GAME/common/idea_tags/00_idea.txt` |
| Advisor characters (`advisor = { idea_token ... }`) | `WIKI/character_modding.md` | `GAME/common/characters/GER.txt` |
| Idea effects and triggers | `GAME/documentation/effects_documentation.md` (`add_ideas`, `remove_ideas`, `swap_ideas`, `add_timed_idea`, `modify_timed_idea`, `remove_ideas_with_trait`, `show_ideas_tooltip`, `add_dynamic_modifier`, `remove_dynamic_modifier`, `force_update_dynamic_modifier`, `custom_effect_tooltip`), `triggers_documentation.md` (`has_idea`, `has_idea_with_trait`, `has_dynamic_modifier`, `amount_taken_ideas`, `has_allowed_idea_with_traits`, `has_available_idea_with_traits`) | |
| Argument tables for those effects | `WIKI/effects.md`, rows `add_ideas`, `add_timed_idea`, `modify_timed_idea`, `swap_ideas`, `remove_ideas`, `add_dynamic_modifier` | |
| Modifier mechanics, dynamic modifiers, static modifiers, modifier definitions, tooltips | `WIKI/modifiers.md` | `GAME/common/dynamic_modifiers/0_dynamic_modifiers.txt`, `bba_dynamic_modifiers.txt` (state), `TAOG_dynamic_modifiers.txt` (variable-driven country spirit), `GAME/common/modifiers/00_static_modifiers.txt`, `01_event_modifiers.txt`, `GAME/common/modifier_definitions/modifier_definitions.txt` |
| Complete modifier list by scope and the template modifiers | `GAME/documentation/modifiers_documentation.md` (sections "Modifiers for scope country", "state", "unit_leader", and the `<Building>`, `<Resource>`, `<IdeaGroup>` templates) | |
| Modifier values as variables | `GAME/documentation/dynamic_variables_documentation.md` (`modifier@`, `leader_modifier@`, `unit_modifier@`) | |
| Idea description formatter | `GAME/documentation/loc_formatter_documentation.md` (`idea_desc`, `idea_name`) | `custom_effect_tooltip = idea_desc\|<idea>` in `GAME/common/decisions/GER.txt` |
| Script constants | `GAME/documentation/script_concept_documentation.md` (Script Constants) | |

Use the hoi4 MCP reference routes (`hoi4_reference_context` with surface `idea`, `hoi4_reference_search`, `hoi4_reference_read`, `hoi4_source_lookup`) to cite exact line spans.
If a route fails once, retry once with narrower input, then read the local file directly.

## Unverified or conflicting points

- Whether `on_remove` runs when a timed idea expires: the wiki states cancellation triggers it, and the installed documentation does not mention expiry.
- What `add_ideas` does when the country already has the idea, and whether re-adding a timed idea resets its timer.
- `cancel_if_invalid` and `continue_if_invalid` meaning for ideas; used in vanilla laws but absent from the wiki idea page and installed documentation.
- Whether a custom modifier definition's tooltip key is the plain id (wiki) or `MODIFIER_<UPPERCASE_ID>` (vanilla built-ins); defining both is a safe workaround rather than a documented rule.
- Whether dynamic modifier values accept `constant:` tokens or arithmetic; the wiki and vanilla only show variable names and numeric literals.
- Whether duplicate idea ids across files resolve by filename order like other databases; the wiki states this only for sprites and opinion modifiers.
- The wiki says a dynamic modifier's icon is hidden when absent; the exact GUI placement for character-scope dynamic modifiers is not described.
