# HOI4 Characters, Leaders and Traits: Runtime lifecycle, generated characters and scopes

Part of the [hoi4-characters-leaders](../SKILL.md) skill. Read before scripting recruitment, promotion, retirement, transfer or generate_character, or before writing character triggers and scope iteration.

## Lifecycle at runtime

Typical sequences (installed effects documentation plus wiki `Character modding` > Using in-game):

1. Recruit once in country history: `recruit_character = TAG_person`. The wiki says recruitment cannot take place outside country history and that the effect must not be the last line of the file. Vanilla bring-in-later patterns instead recruit in the history of the tag that will own them (even for countries not on the map at start) and move them with `set_nationality`.
2. Add a role later: `TAG_person = { add_country_leader_role = { promote_leader = yes country_leader = { ... } } }` or `add_advisor_role`, `add_corps_commander_role`, and so on.
3. Take power: `promote_character`. Hire an advisor: `activate_advisor = idea_token`.
4. Remove a role: `remove_country_leader_role = { character = ID ideology = type }`, `remove_advisor_role = { character = ID slot = slot }`, `remove_unit_leader_role`.
5. Dismiss: `retire_character = ID` (country scope) or `retire = yes` (character scope) removes the character from the country with all roles. The character wiki says `set_nationality` can bring a retired character back with roles retained; the Effects wiki table says a retired character cannot be re-recruited. These pages conflict. Do not plan to resurrect a retired character without testing it; use `remove_*_role` plus a flag when the person may return.
6. Kill effects: `kill_country_leader` and `kill_ideology_leader` behave like `retire_character` for the leader; `retire_country_leader` and `retire_ideology_leader` only remove the person from the line of succession and keep their roles (wiki).
7. Transfer: `set_nationality = TAG` in character scope, or country scope with `target_country` and `character`.
8. State on a character: `set_character_flag`, `clr_character_flag`, `modify_character_flag`; the flag lives with the character.
9. Dynamic modifiers on characters: `add_dynamic_modifier` in character scope.

## Generated characters

`generate_character` creates and recruits a generic character per country in an iteration; vanilla uses it in `history/general/*.txt`. It requires `token_base`; advisor `idea_token` becomes `<token_base>_<idea_token>`, or `<token_base>_<slot>` when omitted. It can be used mid-game only if the same template was already run in history (the template can be registered under a false `limit = { always = no }` so it creates nobody at start); using the full effect directly mid-game does not work (wiki). Do not use it as a substitute for named characters; generated characters have limits.

## Triggers and scopes

- Scope entry: `<character_id> = { ... }` from anywhere except within another character scope; iterators in country scope: `every_character`, `random_character`, `any_character`, `all_character`, `every_unit_leader`, `every_army_leader`, `every_navy_leader`, `party_leader` (requires a `has_ideology = <type>` in `limit`), scientists iterators. `include_invisible = yes` includes characters whose role `visible` fails. `owner` returns the recruiting country; in advisor `on_add` this is how to reach the country.
- A variable holding a character scope can be entered as `var:my_var = { ... }`, and some character effects accept `character = var:my_var` (documented for `add_scientist_role` and `set_can_be_fired_in_advisor_role`); check each effect's documentation before relying on it.
- Character-scope triggers: `is_unit_leader`, `is_army_leader`, `is_navy_leader`, `is_corps_commander`, `is_field_marshal`, `is_country_leader`, `is_advisor`, `is_character`, `has_trait`, `has_id`, `attack_skill_level`, `defense_skill_level`, `planning_skill_level`, `logistics_skill_level`, `average_stats`, `has_character_flag`, `is_female`, `is_exiled_leader`, `can_select_trait`, `has_ability`, `num_units`, `is_assigned`, `is_promoted_from_unit`.
- Country-scope triggers: `has_character`, `has_country_leader`, `has_country_leader_ideology`, `has_country_leader_with_trait`, `is_leader_visible`, `can_be_country_leader`, `has_idea_with_trait`, `has_unit_leader`, `any_character` family.
- Loc namespaces: character `[Character.GetName]`, `GetSheHe`, `GetHerHim`, `GetHerHis`, `GetIdeology`, `GetIdeologyGroup`, `Owner`; unit leader `GetName`, `GetLeaderSkill`, pronouns; country `[Root.GetLeader]` (and party leaders `GetDemocraticLeader`, `GetCommunistLeader`, `GetNeutralLeader`, `GetFascistLeader`). From `documentation/loc_objects_documentation.md`.

