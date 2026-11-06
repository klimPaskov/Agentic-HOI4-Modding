# HOI4 Ideas and Modifiers: Static and custom modifiers, localisation and triggers

Part of the [hoi4-ideas-modifiers](../SKILL.md) skill. Read before defining a static, province, relation or custom modifier, or before writing idea and modifier localisation, icons and tooltips.

## Static, province, relation, and custom modifiers

- Static modifiers (`common/modifiers/*.txt`, one block per id) cover hard-coded global modifiers (`stability_good_modifier`, `non_core`, `resistance_effect`, and so on in `00_static_modifiers.txt`), province modifiers, relation modifiers, difficulty modifiers, and balance-of-power modifiers.
- Province modifiers: `add_province_modifier = { static_modifiers = { m1 m2 } province = N days = N }` and `remove_province_modifier`, state scope; `province = { id = N all_provinces = yes limit_to_coastal = yes ... }` selects several. Vanilla: `flooded` in `00_static_modifiers.txt`. Many state modifiers work in province scope. A visible icon needs a sprite `GFX_modifiers_<name>_icon` and an `iconType` in `countrystateview.gui`.
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
- `GFX_idea_unknown` is a base-game placeholder sprite, declared in `interface/countrydiplomacyview.gfx`. [vanilla-confirmed 1.19.3]
- Idea description in another tooltip: `custom_effect_tooltip = idea_desc|my_idea` (formatter `idea_desc`, scope country; `idea_name` for the name). `show_ideas_tooltip = my_idea` prints the idea's effects.
- Flag triggers inside player-visible `available` or `allow` blocks use the flag name as the tooltip key; give such flags a key or wrap them in `hidden_trigger` with a `custom_trigger_tooltip`.

## Idea and modifier triggers

`has_idea`, `has_idea_with_trait`, `amount_taken_ideas`, `has_allowed_idea_with_traits`, `has_available_idea_with_traits`, `has_dynamic_modifier` (state, country, character), `has_country_flag`, and comparisons on `modifier@name` through `check_variable`. For a pure presence test prefer a country flag over a hidden idea unless the token itself is needed.

