---
name: hoi4-ideas-modifiers
description: Use when creating, editing, auditing, or scripting Hearts of Iron IV ideas, national spirits, hidden ideas, laws, advisor or designer ideas, dynamic modifiers, static or custom modifiers, timed ideas, or modifier tooltips and localisation.
---

# HOI4 Ideas and Modifiers

Generic guidance for applying lasting numeric effects in Hearts of Iron IV: choosing between an idea, a dynamic modifier, a static modifier, or a custom modifier definition, writing each with verified syntax, and avoiding the silent failures.
Use `hoi4-map-states` for state-scoped effects that are not modifiers (ownership, buildings, categories), `hoi4-ai-strategies` for `ai_will_do` weights inside ideas, `hoi4-mtth` for MTTH variables that feed dynamic modifiers, and `hoi4-decisions-missions` for decisions that add or swap ideas.

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
`WIKI` means the offline snapshot in `paradox_wiki/` at the mod root.
Installed documentation is more authoritative than the wiki; where they disagree, follow the installed file and record the conflict.

| Topic | Authoritative text | Vanilla precedent |
| --- | --- | --- |
| Idea fields, categories, slots, cost, hidden ideas, slot cost modifiers | `WIKI/Idea modding - Hearts of Iron 4 Wiki.md` | `GAME/common/ideas/_event.txt` (event-granted spirits and a hidden idea), `_economic.txt` and `_manpower.txt` (laws), `GER.txt` (designers `tank_manufacturer`, advisors, `custom_modifier_tooltip`), `_debug_spirits.txt` |
| Idea categories and slots | same page, section Categories | `GAME/common/idea_tags/00_idea.txt` |
| Advisor characters (`advisor = { idea_token ... }`) | `WIKI/Character modding - Hearts of Iron 4 Wiki.md` | `GAME/common/characters/GER.txt` |
| Idea effects and triggers | `GAME/documentation/effects_documentation.md` (`add_ideas`, `remove_ideas`, `swap_ideas`, `add_timed_idea`, `modify_timed_idea`, `remove_ideas_with_trait`, `show_ideas_tooltip`, `add_dynamic_modifier`, `remove_dynamic_modifier`, `force_update_dynamic_modifier`, `custom_effect_tooltip`), `triggers_documentation.md` (`has_idea`, `has_idea_with_trait`, `has_dynamic_modifier`, `amount_taken_ideas`, `has_allowed_idea_with_traits`, `has_available_idea_with_traits`) | |
| Argument tables for those effects | `WIKI/Effects - Hearts of Iron 4 Wiki.md`, rows `add_ideas`, `add_timed_idea`, `modify_timed_idea`, `swap_ideas`, `remove_ideas`, `add_dynamic_modifier` | |
| Modifier mechanics, dynamic modifiers, static modifiers, modifier definitions, tooltips | `WIKI/Modifiers - Hearts of Iron 4 Wiki.md` | `GAME/common/dynamic_modifiers/0_dynamic_modifiers.txt`, `bba_dynamic_modifiers.txt` (state), `TAOG_dynamic_modifiers.txt` (variable-driven country spirit), `GAME/common/modifiers/00_static_modifiers.txt`, `01_event_modifiers.txt`, `GAME/common/modifier_definitions/modifier_definitions.txt` |
| Complete modifier list by scope and the template modifiers | `GAME/documentation/modifiers_documentation.md` (sections "Modifiers for scope country", "state", "unit_leader", and the `<Building>`, `<Resource>`, `<IdeaGroup>` templates) | |
| Modifier values as variables | `GAME/documentation/dynamic_variables_documentation.md` (`modifier@`, `leader_modifier@`, `unit_modifier@`) | |
| Idea description formatter | `GAME/documentation/loc_formatter_documentation.md` (`idea_desc`, `idea_name`) | `custom_effect_tooltip = idea_desc\|<idea>` in `GAME/common/decisions/GER.txt` |
| Script constants | `GAME/documentation/script_concept_documentation.md` (Script Constants) | |

Use the hoi4 MCP reference routes (`hoi4_reference_context` with surface `idea`, `hoi4_reference_search`, `hoi4_reference_read`, `hoi4_source_lookup`) to cite exact line spans.
If a route fails once, retry once with narrower input, then read the local file directly.

## Decision procedure: which mechanism

1. Constant country modifiers, visible in the politics screen: a national spirit (`country` category) added with `add_ideas`, or `add_timed_idea` when it expires.
2. A staged progression (levels 1 to 3 of the same theme): one idea per stage and `swap_ideas`; give the stages the same display name via `name =` so it reads as one upgraded idea.
3. A country modifier whose value depends on a variable, or any modifier on a state, unit leader, or special project: a dynamic modifier. Ideas cannot hold variables.
4. A bonus that is not a modifier (`research_bonus`, `equipment_bonus`, `rule`, `targeted_modifier`): an idea, advisor, or country leader trait; dynamic modifiers reject these.
5. An invisible bonus or marker: a `hidden_ideas` idea (it is a tokenised idea; no vanilla precedent in this install tests it with `has_idea`, so verify before relying on that), or a `hidden_modifier` block inside a visible idea. Prefer a country flag when you only need a boolean and no database token.
6. A modifier on one province: a static modifier from `common/modifiers` applied with `add_province_modifier`.
7. A modifier of one country towards another: `targeted_modifier = { tag = XXX ... }` in an idea, or a relation modifier with `add_relation_modifier`.
8. A numeric accumulator that other script reads (summed across ideas, traits, dynamic modifiers): a modifier definition in `common/modifier_definitions`, read as `modifier@name`.
9. A selectable political, economic, or manufacturer choice: a law, designer, or advisor category with `cost`, `available`, `visible`.
10. Diplomatic opinion: an opinion modifier, not a modifier (see below).

## How modifiers work

Source: `WIKI/Modifiers`, intro and section Applying a modifier.

- A modifier is `name = number`. Values add: `political_power_gain = 0.2` and `political_power_gain = -0.05` from two sources give +0.15. A value of 0 does nothing. Booleans are numbers and must be 1 to have an effect. Modifiers have no `if`; use dynamic modifiers for conditions.
- Total value is readable as a variable: `set_variable = { v = modifier@political_power_gain }` in country or state scope; unit leaders use `unit_modifier@name` and `leader_modifier@name`. A modifier definition with no engine effect can still accumulate this way.
- Scope matters. `GAME/documentation/modifiers_documentation.md` groups modifiers under `country`, `state`, `unit_leader`, `scientist`, `army`, `naval`, `air`, and so on; each entry lists its **Categories**. Use a modifier only in a block whose scope matches one of its categories. A state modifier such as `local_building_slots` belongs in state categories, dynamic modifiers on states, buildings' `state_modifiers`, and `common/state_category` blocks.
- Template modifiers expand over database keys: `production_speed_<Building>_factor`, `production_cost_<Building>_factor`, `state_production_speed_<Building>_factor`, `<Building>_max_level_terrain_limit`, `local_resources_<Resource>_factor`, `state_resource_<Resource>`, `temporary_state_resource_<Resource>`, `country_resource_<Resource>`, `<IdeaGroup>_cost_factor` (for example `economy_cost_factor`), `<Technology>_cost_factor`, `<Ideology>_drift`, `experience_gain_<Unit>_combat_factor`, `unit_<Unit>_design_cost_factor`. Confirm the exact expanded name against the "Modified types" list in the documentation entry.
- Not modifiers: `research_bonus`, `equipment_bonus`, opinion modifiers (`common/opinion_modifiers`, applied with `add_opinion_modifier`).
- Modifier blocks accept `hidden_modifier = { ... }` (applies but is not shown) and `custom_modifier_tooltip = <loc key>` (shows your text as a line). Vanilla precedent: `GAME/common/ideas/italy.txt` and `czechoslovakia.txt`.
- Look up a modifier name by searching `modifiers_documentation.md` for the exact heading. A misspelled or nonexistent modifier name produces a log error and no effect; there is no autocorrect.

## Ideas: files, categories, slots

- Ideas live in `common/ideas/*.txt`: `ideas = { <slot_or_category> = { <idea_id> = { ... } } }`. Keep idea ids unique across files and slots (duplicate-id resolution is unverified). Files load in Unicode filename order (capitals, then underscore, then lowercase).
- Category and slot declarations live in `common/idea_tags/*.txt` under `idea_categories = { ... }` with keys `slot`, `character_slot`, `type`, `cost`, `removal_cost`, `ledger`, `hidden`, `politics_tab`. Vanilla `GAME/common/idea_tags/00_idea.txt` declares `hidden_ideas` (`hidden = yes`, `removal_cost = -1`), `country` (`type = national_spirit`, `cost = 0`, `removal_cost = -1`), `government` (slots `economy`, `trade_laws`, `mobilization_laws`, character slots `political_advisor` x3), `research_production`, `military_staff`, and spirit categories with `type = army_spirit`, `navy_spirit`, `air_spirit`.
- The block name inside `ideas = { }` is the slot (or the category for `country` and `hidden_ideas`): `economy = { law = yes ... }`, `tank_manufacturer = { designer = yes ... }`, `political_advisor = { ... }`.
- A new slot needs a category entry, a sprite `GFX_idea_slot_<slot>` for the empty-slot icon (see `GAME/interface/countrypoliticsview.gfx`), and GUI room: the politics view gridbox defaults to 7 horizontal slots per row, and `GFX_idea_categories` is a frame strip whose frame count must match the number of categories (`WIKI/Idea modding`, GFX and GUI).
- Cost factors: the modifier `<slot>_cost_factor` only works if the slot already has an idea or character defined when the modifier is loaded. Idea files starting with a capital letter load before `_economic.txt` and `_manpower.txt`, so an idea in `GER.txt` using `economy_cost_factor` errors; name country idea files with lowercase initials or add a placeholder idea in an earlier-loading file. Character slots (for example `political_advisor_cost_factor`) need at least one idea defined in the slot for the same reason.

## Idea body: every field that matters

Frequencies are from the 6,000-plus ideas in `GAME/common/ideas/` (each field's count is how often vanilla uses it): `allowed`, `picture`, `modifier`, `removal_cost`, `allowed_civil_war`, `traits`, `name`, `research_bonus`, `ai_will_do`, `available`, `equipment_bonus`, `visible`, `ledger`, `targeted_modifier`, `cancel`, `cost`, `do_effect`, `on_remove`, `on_add`, `rule`, `cancel_if_invalid`, `allowed_to_remove`, `level`, `default`.

```
ideas = {
	country = {
		example_spirit = {
			allowed = { always = no }          # event/focus-granted only; add_ideas bypasses it
			allowed_civil_war = { always = yes }
			picture = generic_war_preparation  # sprite GFX_idea_generic_war_preparation
			name = shared_display_name         # optional alternate loc key
			modifier = {
				political_power_gain = 0.1
				stability_factor = -0.05
				custom_modifier_tooltip = example_spirit_tt
			}
			targeted_modifier = { tag = QAT defense_bonus_against = 0.2 }
			research_bonus = { infantry = 0.1 }
			equipment_bonus = { infantry_equipment = { instant = yes defense = 0.2 } }
			rule = { can_join_factions = no }
			do_effect = { NOT = { has_government = democratic } }   # modifiers apply only while true
			cancel = { has_political_power > 50 }                    # auto-removes when true; runs on_remove
			on_add = { add_stability = 0.05 }
			on_remove = { add_political_power = -50 }
			ai_will_do = { factor = 0 }
		}
	}
}
```

- `modifier = { }`: static numbers only. Variables are not read here ("Variables do not work in this section", `WIKI/Idea modding`). Negative values allowed.
- `targeted_modifier = { tag = TAG <targeted modifiers> }`: applied by the idea holder, effective against TAG; see the Targeted modifiers section of `WIKI/List of modifiers`.
- `research_bonus = { <technology category> = <number> }`: categories from `common/technology_tags/` (examples: `infantry`, `armor`, `dd_tech`, `artillery`).
- `equipment_bonus = { <archetype or type> = { instant = yes <stat> = <number> } }`: without `instant = yes` the bonus applies only to equipment researched after the idea was added. Archetypes and types come from `common/units/equipment/*.txt`.
- `rule = { <game rule> = yes|no }`: tooltip lists only rules that differ from the default. The wiki's table of rules includes `can_join_factions`, `can_create_factions`, `can_send_volunteers`, `can_not_declare_war`, `can_puppet`, `can_boost_own_ideology`.
- `on_add` and `on_remove` are country-scope effects. They do not run when the idea is added by a country history file or bookmark; copy the effect into that block. `cancel` triggers `on_remove` too.
- `allowed_civil_war` defaults to false: the spirit disappears when a civil war starts unless the trigger passes for a side. Vanilla sets `allowed_civil_war = { always = yes }` on ideas that must survive (3,638 uses).
- `do_effect` gates the modifiers, equipment bonus, and research bonus without removing the idea (181 vanilla uses).
- `allowed` is checked once at game start or load, and manual `add_ideas` bypasses it. It restricts selectable ideas (tag, DLC) and by convention `allowed = { always = no }` marks event-granted ideas.
- `visible` and `available` are checked continuously for selectable ideas (laws, designers, advisors); `visible` hides, `available` greys out. Put tag and DLC checks in `allowed`, not `visible`.
- `cost` and `removal_cost` (political power). `removal_cost = -1` forbids manual removal. `cost` falls back to the category value (150 in vanilla for selectable categories, 0 for `country`). `level` makes laws escalate: moving from level 1 to 3 charges the cost of level 2 as well.
- `traits = { ... }` references traits defined in `common/country_leader/*.txt` (for example `heavy_tank_manufacturer`); the trait supplies the modifier and icon.
- `ledger = army|air|navy|military|civilian|all|hidden`: which intelligence ledger shows it; `hidden` suppresses it. Resolution order is idea, then slot, then category.
- `default = yes` marks the law a country starts with when none is assigned (5 vanilla uses). `cancel_if_invalid = no` is used on vanilla laws (31 uses) and is not described in the wiki or installed documentation; copy it only from a vanilla precedent such as `_manpower.txt`.
- `ai_will_do` on a selectable idea steers the AI; on event-granted spirits vanilla uses `factor = 0`. Weight design belongs to `hoi4-ai-strategies`.

## Spirits, hidden ideas, laws, designers, advisors

- National spirit: category `country`. `GAME/common/ideas/_event.txt` shows the event-granted pattern (`allowed = { always = no # Triggered via event }`, `picture`, `modifier`, `ai_will_do = { factor = 0 }`).
- Hidden idea: category `hidden_ideas`; same fields as a spirit, but no politics-screen slot. Vanilla example `GEN_cheaper_amphib` in `_event.txt` carries an `equipment_bonus` and a `cancel` trigger. Localise it if it can cancel (a pop-up appears) or if it feeds modifier tooltips such as the stability or research-speed hover.
- Hidden idea as a token carrier: a modifier-free hidden idea is a database-enumerable token that a dispatcher can read as an idea key. It is not a spirit and needs no icon or localisation when it is never applied to a country.
- Law: a category with `law = yes` and usually `use_list_view = yes`; each idea has `cost`, `removal_cost`, optional `level`, `default`, `available`, `allowed_to_remove`. `GAME/common/ideas/_economic.txt` and `_manpower.txt`.
- Designer: a slot such as `tank_manufacturer` with `designer = yes`; fields `allowed`, `visible`, `available`, `research_bonus`, `traits`, `on_add`, `ai_will_do`. `GAME/common/ideas/GER.txt` around its `tank_manufacturer` block.
- Advisor, two forms. Legacy idea-based: `political_advisor = { id = { picture traits allowed do_effect ai_will_do } }` (for example `GAME/common/ideas/andalusia.txt`). Current character-based: a character with `advisor = { slot = political_advisor idea_token = my_token allowed visible available traits cost can_be_fired }` in `common/characters/*.txt` (`GAME/common/characters/GER.txt`). `idea_token` is mandatory: without it recruiting that character hides every other token-less advisor, and `has_idea` and `show_ideas_tooltip` take the token, not the character id. `on_add` and `on_remove` in an advisor block run in character scope; use `owner = { ... }` to reach the country. See `WIKI/Character modding`.

## Adding, removing, swapping, and timing ideas

Verified against `GAME/documentation/effects_documentation.md` and `WIKI/Effects`.

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
- Reading: `has_idea = my_idea` (country scope; for advisors the argument is the `idea_token`), `has_idea_with_trait = my_trait`, `amount_taken_ideas = { amount > 2 slots = { political_advisor } }` (excludes spirits, hidden ideas, and laws), `has_available_idea_with_traits` and `has_allowed_idea_with_traits` (`idea`, `limit`, `characters`, `ignore`).

## Dynamic modifiers

Source: `WIKI/Modifiers`, section Dynamic modifiers; `GAME/common/dynamic_modifiers/0_dynamic_modifiers.txt` header comment; effects documentation.

Definition (`common/dynamic_modifiers/*.txt`, no wrapper block):

```
my_dynamic_modifier = {
	icon = GFX_modifiers_my_dynamic_modifier        # optional; without it the modifier is hidden in the GUI
	enable = { always = yes }                       # optional; modifiers apply only while true
	remove_trigger = { NOT = { has_variable = my_var } }   # optional; removes the modifier when true
	attacker_modifier = no                          # state scope only: also affects attackers into the state
	political_power_gain = my_var                   # variable name as the value
	weekly_manpower = 1000                          # constant value
	stability_factor = GER.my_stability_var         # a variable of a named scope
}
```

Use:

```
add_dynamic_modifier = { modifier = my_dynamic_modifier }
add_dynamic_modifier = { modifier = my_dynamic_modifier days = 30 }                  # temporary, may be a variable
add_dynamic_modifier = { modifier = my_dynamic_modifier scope = POL }                # applied here, variables read from POL
remove_dynamic_modifier = { modifier = my_dynamic_modifier }                          # repeat scope = if used on add
force_update_dynamic_modifier = yes                                                   # refresh now
has_dynamic_modifier = my_dynamic_modifier                                            # or { modifier = x scope = GER }
```

- Allowed scopes: country, state, character (unit leader), special project. The same definition can be added anywhere; the scope of the `add_dynamic_modifier` call decides where it applies and where variables are read.
- Variables come from the scope the modifier is attached to: for a state modifier, the state's variable, not the owner's. Use `scope =` to read another scope's variable.
- Daily refresh: at the start of each day every variable-valued modifier resets to 0, then dynamic modifiers evaluate in the order they were added, each treated as 0 until its variables resolve. Changes take effect at most one day later unless you call `force_update_dynamic_modifier = yes` in the same scope. Re-adding an existing modifier updates its timer instead of stacking a second copy.
- Inside `enable` and `remove_trigger` for state modifiers, `ROOT` is the state and `OWNER` reaches the owner (vanilla `sabotaged_resources` and `autonomous_state` in `0_dynamic_modifiers.txt`).
- Dynamic modifiers accept modifiers only. They reject `research_bonus`, `equipment_bonus`, `rule`, and other idea attributes.
- Definitions cannot be hot-reloaded; any change to a dynamic modifier file needs a game restart. Ideas can be reloaded.
- The `add_dynamic_modifier` tooltip does not list variable-valued modifiers (it lists constants). Add a `custom_effect_tooltip` line and hide the add with `hidden_effect`; the vanilla pattern is a `_tt` key: `"Modify §Y$ETH_state_development_dynamic_modifier$§! by: \n$MODIFIER_STATE_PRODUCTION_SPEED_BUILDINGS_FACTOR$: §G+10%§!"` (`GAME/localisation/english/bba_decisions_l_english.yml`).
- Cost: a dynamic modifier is re-evaluated every day for every scope that holds it, so it is less efficient than an idea. If the value is constant and the scope is a country, use an idea.
- MTTH variables can feed a dynamic modifier through the same variable slots; they also reset and recalculate daily.

## Static, province, relation, and custom modifiers

- Static modifiers (`common/modifiers/*.txt`, one block per id) cover hard-coded global modifiers (`stability_good_modifier`, `non_core`, `resistance_effect`, and so on in `00_static_modifiers.txt`), province modifiers, relation modifiers, difficulty modifiers, and balance-of-power modifiers.
- Province modifiers: `add_province_modifier = { static_modifiers = { m1 m2 } province = N days = N }` and `remove_province_modifier`, state scope; `province = { id = N all_provinces = yes limit_to_coastal = yes ... }` selects several. Vanilla: `flooded` in `01_event_modifiers.txt`. Many state modifiers work in province scope. A visible icon needs a sprite `GFX_modifiers_<name>_icon` and an `iconType` in `countrystateview.gui`.
- Relation modifiers: a block with `valid_relation_trigger = { FROM = { ... } }` plus targeted modifiers; `add_relation_modifier = { target = TAG modifier = name }` in country scope; `ROOT` is the holder and `FROM` the target.
- Custom modifier definitions (`common/modifier_definitions/*.txt`): `name = { color_type = good|bad|neutral value_type = number|percentage|percentage_in_hundred|yes_no precision = 0..3 postfix = none|days|hours|daily category = <scope categories> }`. They have no engine effect; they exist so ideas, traits, buildings, and dynamic modifiers can add to a value that script reads with `modifier@name`. Header comments are in `GAME/common/modifier_definitions/modifier_definitions.txt`.
- Opinion modifiers (`common/opinion_modifiers`, fields `value`, `trade`, `decay`, `days|months|years`, `min_trust`, `max_trust`) are a separate system added with `add_opinion_modifier` and cannot be placed in a modifier block; to simulate one, pair it with the idea's `on_add`/`on_remove` and a `custom_modifier_tooltip`. Diplomatic use belongs to `hoi4-diplomacy-war`.

## Localisation, GFX, and tooltips

- Idea name and description: `<idea_id>: "Name"` and `<idea_id>_desc: "Description"`. With `name = other_key`, use `other_key` and `other_key_desc`. A national spirit without a name shows its id.
- Dynamic modifier name: `<modifier_id>: "Name"` (vanilla `ETH_state_development_dynamic_modifier` in `bba_ideas_l_english.yml`); `_desc` is not used by that precedent.
- Modifier display names come from `MODIFIER_<UPPERCASE_NAME>` and `MODIFIER_<UPPERCASE_NAME>_DESC` in `GAME/localisation/english/modifiers_l_english.yml`, with `MODIFIER_<NAME>_tt` for the formatted line. A custom modifier definition's id is the key per the wiki; if it renders as a raw id, also define `MODIFIER_<UPPERCASE_ID>` (the vanilla convention).
- `custom_modifier_tooltip = my_key_tt` adds a line; the key may use `[...]` commands, `§` colour codes, and `$KEY$` references.
- Idea picture: sprite `GFX_idea_<picture>` where `picture` defaults to the idea id. The game always adds the `GFX_idea_` prefix, so `picture = GFX_x` looks for `GFX_idea_GFX_x`. The name is looked up first as `GFX_idea_<idea id>` even if `picture` is set. A `_<graphical_culture_2d>` suffix variant is preferred for matching countries. Declare sprites in `interface/*.gfx` (vanilla: `GAME/interface/ideas.gfx`). Vanilla idea icons are 60 x 68 pixels (`GAME/gfx/interface/ideas/idea_generic_agrarian_society.dds`); the trait strip `idea_traits_strip.dds` is 504 x 28 with 18 frames. A wrong `texturefile` makes the idea invisible in the politics view while still applying its modifiers.
- Dynamic modifier icon: any sprite; vanilla uses `GFX_idea_*` and `GFX_modifiers_*` names (`GAME/interface/_dynamic_modifiers.gfx`, `countrystateview.gfx`).
- Idea description in another tooltip: `custom_effect_tooltip = idea_desc|my_idea` (formatter `idea_desc`, scope country; `idea_name` for the name). `show_ideas_tooltip = my_idea` prints the idea's effects.
- Flag triggers inside player-visible `available` or `allow` blocks use the flag name as the tooltip key; give such flags a key or wrap them in `hidden_trigger` with a `custom_trigger_tooltip`.

## Idea and modifier triggers

`has_idea`, `has_idea_with_trait`, `amount_taken_ideas`, `has_allowed_idea_with_traits`, `has_available_idea_with_traits`, `has_dynamic_modifier` (state, country, character), `has_country_flag`, and comparisons on `modifier@name` through `check_variable`. For a pure presence test prefer a country flag over a hidden idea unless the token itself is needed.

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

## Unverified or conflicting points

- Whether `on_remove` runs when a timed idea expires: the wiki states cancellation triggers it, and the installed documentation does not mention expiry.
- What `add_ideas` does when the country already has the idea, and whether re-adding a timed idea resets its timer.
- `cancel_if_invalid` and `continue_if_invalid` meaning for ideas; used in vanilla laws but absent from the wiki idea page and installed documentation.
- Whether a custom modifier definition's tooltip key is the plain id (wiki) or `MODIFIER_<UPPERCASE_ID>` (vanilla built-ins); defining both is a safe workaround rather than a documented rule.
- Whether dynamic modifier values accept `constant:` tokens or arithmetic; the wiki and vanilla only show variable names and numeric literals.
- Whether duplicate idea ids across files resolve by filename order like other databases; the wiki states this only for sprites and opinion modifiers.
- The wiki says a dynamic modifier's icon is hidden when absent; the exact GUI placement for character-scope dynamic modifiers is not described.
