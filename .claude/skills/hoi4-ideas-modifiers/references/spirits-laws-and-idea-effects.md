# HOI4 Ideas and Modifiers: Spirits, laws and idea effects

Part of the [hoi4-ideas-modifiers](../SKILL.md) skill. Read before defining a spirit, hidden idea, law, designer or advisor idea, or before scripting add, remove, swap or timed ideas.

## Spirits, hidden ideas, laws, designers, advisors

- National spirit: category `country`. `GAME/common/ideas/_event.txt` shows the event-granted pattern (`allowed = { always = no # Triggered via event }`, `picture`, `modifier`, `ai_will_do = { factor = 0 }`).
- Hidden idea: category `hidden_ideas`; same fields as a spirit, but no politics-screen slot. Vanilla example `GEN_cheaper_amphib` in `_event.txt` carries an `equipment_bonus` and a `cancel` trigger. Localise it if it can cancel (a pop-up appears) or if it feeds modifier tooltips such as the stability or research-speed hover.
- Hidden idea as a token carrier: a modifier-free hidden idea is a database-enumerable token that a dispatcher can read as an idea key. It is not a spirit and needs no icon or localisation when it is never applied to a country.
- Law: a category with `law = yes` and usually `use_list_view = yes`; each idea has `cost`, `removal_cost`, optional `level`, `default`, `available`, `allowed_to_remove`. `GAME/common/ideas/_economic.txt` and `_manpower.txt`.
- Designer: a slot such as `tank_manufacturer` with `designer = yes`; fields `allowed`, `visible`, `available`, `research_bonus`, `traits`, `on_add`, `ai_will_do`. `GAME/common/ideas/GER.txt` around its `tank_manufacturer` block.
- Advisor, two forms. Legacy idea-based: `political_advisor = { id = { picture traits allowed do_effect ai_will_do } }` (for example `GAME/common/ideas/andalusia.txt`). Current character-based: a character with `advisor = { slot = political_advisor idea_token = my_token allowed visible available traits cost can_be_fired }` in `common/characters/*.txt` (`GAME/common/characters/GER.txt`). `idea_token` is mandatory: without it recruiting that character hides every other token-less advisor, and `has_idea` and `show_ideas_tooltip` take the token, not the character id. `on_add` and `on_remove` in an advisor block run in character scope; use `owner = { ... }` to reach the country. See `WIKI/character_modding.md`.

## Adding, removing, swapping, and timing ideas

Verified against `GAME/documentation/effects_documentation.md` and `WIKI/effects.md`.

```
add_ideas = my_idea                      # one
add_ideas = { idea_a idea_b }            # several
remove_ideas = my_idea
remove_ideas_with_trait = my_trait       # removes every idea with that trait

swap_ideas = {
	remove_idea = old_idea
	add_idea = new_idea
	days = 25                            # optional: duration for the new idea
	add_days = 10                        # optional: adjust the replaced idea's remaining time
}

add_timed_idea = { idea = my_timed_idea days = 365 }          # days, months (30), years (365)
add_timed_idea = { idea = my_timed_idea years = 1 months = 2 days = my_days_var }
modify_timed_idea = { idea = my_timed_idea days = -5 }        # negative shortens

show_ideas_tooltip = my_idea             # tooltip only, does not add
```

- `add_ideas` into a category with a single slot replaces the current occupant. All forms are country scope. `add_ideas` bypasses `allowed`.
- `swap_ideas` shows a tooltip of the modifier difference; if both ideas share one display name it reads as a modification. The add happens before the removal. There is no way to edit an idea in place.
- Timed ideas: at least one of `days`, `months`, `years` is mandatory, values may be variables, and the tooltip echoes the unit you wrote. For a duration field that rejects `constant:`, assign the constant to a variable first.
- Starting ideas: `add_ideas` in `history/countries/*.txt`, and `ideas = { }` in the bookmark entry so they appear on the selection screen. `on_add` does not run there.
- A bookmark card shows three ideas and four focuses, and every bookmark `effect` block ends with `randomize_weather`, which a vanilla comment calls obligatory. [vanilla-confirmed 1.19.4.1]
- Reading: `has_idea = my_idea` (country scope; for advisors the argument is the `idea_token`), `has_idea_with_trait = my_trait`, `amount_taken_ideas = { amount > 2 slots = { political_advisor } }` (excludes spirits, hidden ideas, and laws), `has_available_idea_with_traits` and `has_allowed_idea_with_traits` (`idea`, `limit`, `characters`, `ignore`).

