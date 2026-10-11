# Character Effects and Triggers

Read this when you need the exact signature, scope or caveat of a character effect or trigger.
Everything below comes from installed `documentation/effects_documentation.md` and `documentation/triggers_documentation.md` (headings `## <name>`; the lists `Effects for scope CHARACTER` and `Triggers for scope CHARACTER` enumerate the character-scope set) unless a wiki source is named.
Scope abbreviations: COUNTRY, CHARACTER. A "both" effect takes `character = ID` in country scope and omits it inside a character scope.

## Recruit, roles and ownership

| Effect | Scope | Signature and notes |
| --- | --- | --- |
| `recruit_character` | COUNTRY | `recruit_character = TAG_person`. Attaches the character to the country. Wiki: do this in country history, not as the last line of the file |
| `generate_character` | COUNTRY | `generate_character = { token_base = x name = "..." advisor = { idea_token = y slot = z traits = { } } }`, one copy per iterated country |
| `add_country_leader_role` | both | `{ character = ID promote_leader = yes country_leader = { ideology = socialism expire = "1965.1.1.1" traits = { t } } }`. No effect if the character already has a role in that ideology group |
| `add_advisor_role` | both | `{ character = ID advisor = { slot = air_chief cost = 50 idea_token = tok traits = { t } allowed = { } } activate = yes }`. No script blocks beyond the above |
| `add_corps_commander_role` | both | `{ character = ID traits = { } skill = 4 attack_skill = 2 defense_skill = 3 planning_skill = 3 logistics_skill = 5 }` |
| `add_field_marshal_role` | both | Same keys as corps commander |
| `add_naval_commander_role` | both | `{ character = ID traits = { } skill = 4 attack_skill = 3 defense_skill = 3 maneuvering_skill = 3 coordination_skill = 4 }` |
| `add_scientist_role` | both | `{ character = ID scientist = { desc traits skills } }`; no `visible` when added by effect |
| `remove_advisor_role` | both | `{ character = ID slot = air_chief }` |
| `remove_country_leader_role` | both | `{ character = ID ideology = socialism }` |
| `remove_unit_leader_role` | both | `remove_unit_leader_role = yes` in character scope; with `character =` in country scope |
| `remove_scientist_role` | CHARACTER | Removes the scientist role |
| `retire_character` | COUNTRY | `retire_character = ID`; unassigns the character from the nation and all jobs. See the conflict note in `SKILL.md` about re-adding |
| `retire` | CHARACTER | `retire = yes` (documentation: retires the character) |
| `set_nationality` | both | `ID = { set_nationality = TAG }` or country scope `{ target_country = TAG character = ID }`; transfers the character |
| `kill_country_leader`, `kill_ideology_leader` | COUNTRY | Remove the sitting leader completely; next in line takes over |
| `retire_country_leader`, `retire_ideology_leader` | COUNTRY | Remove the person from the line of succession; documentation says the next recruited character becomes leader; the wiki says the old leader keeps roles |

## Promotion and hiring

- `promote_character` (both): country scope `promote_character = ID` or `{ character = ID ideology = nazism }`; character scope `promote_character = yes`, `= nazism` or `{ ideology = nazism }`. "Promotes character to the head of their political party. If this is the ruling party, the character becomes country leader." The ideology is mandatory when the character has several leader roles.
- `activate_advisor = idea_token` (COUNTRY): hires the advisor into its slot. Works in country history.
- `promote_leader = yes` (CHARACTER): general to field marshal. `demote_leader = yes`: field marshal to general.
- `set_can_be_fired_in_advisor_role = { character = ID slot = political_advisor value = no }` (both). `slot` is mandatory when the character holds several advisor roles.
- `party_leader = { limit = { has_ideology = communism } ... }` (COUNTRY): iterates party leaders; per the wiki the `has_ideology` in `limit` must name an ideology type for the party.

## Traits and growth

- Country leader and advisor traits: `add_country_leader_trait` and `remove_country_leader_trait` (both). In character scope pass the ideology when the character has several leader roles: `{ ideology = oligarchism trait = anti_communist }`. `swap_country_leader_traits = { remove = a add = b ideology = x }` (CHARACTER).
- `add_trait` and `remove_trait` (both): `{ character = ID trait = x slot = political_advisor ideology = fascism_ideology }`; `slot` only for advisors, `ideology` only for country leaders.
- Unit leader traits (CHARACTER): `add_unit_leader_trait = x`, `remove_unit_leader_trait = x`, `replace_unit_leader_trait`, `add_timed_unit_leader_trait`, `add_random_trait = { a b c }`, `add_max_trait = 1`.
- Skills: `add_skill_level = 1`, `add_attack = 1`, `add_defense`, `add_planning`, `add_logistics`, `add_maneuver`, `add_coordination`, `boost_planning`, `gain_xp = 5` (cannot remove experience; promotes at thresholds), `supply_units = 24` (hours of supply).
- Scientists: `add_scientist_level`, `add_scientist_xp`, `add_scientist_trait`, `generate_scientist_character`, `injure_scientist_for_days`.
- Modifiers: `add_dynamic_modifier = { modifier = x days = N }` and `remove_dynamic_modifier`, `force_update_dynamic_modifier` (CHARACTER scope accepted).

## Presentation

- `set_portraits = { character = ID civilian = { large = GFX_x small = GFX_y } army = { small = GFX_z } }` (both). Sprites or direct paths.
- `set_character_name = { character = ID name = loc_or_literal }` (both; character scope `set_character_name = key`).
- `set_leader_name = "Literal"`, `set_leader_portrait = "GFX_x"`, `set_leader_description = "KEY"` (CHARACTER; unit-leader flavour; no tooltip).
- `set_country_leader_name = { ideology = x name = "..." }`, `set_country_leader_portrait = { ideology = x portrait = "GFX_x" }`, `set_country_leader_description = { ideology = x desc = "KEY" }` (COUNTRY; no tooltip; `ideology` optional).
- `set_country_leader_ideology` (COUNTRY): changes the ideology type of the active leader.
- `character_list_tooltip = { limit = { } }` (COUNTRY): shows matching characters in a tooltip. `show_unit_leaders_tooltip` shows unit leader names.

## Flags

- `set_character_flag = flag`, `clr_character_flag = flag`, `modify_character_flag = { flag = f value = n }` (only modifies an existing flag). `set_unit_leader_flag`, `clr_unit_leader_flag`, `modify_unit_leader_flag` are the older equivalents.
- Trigger: `has_character_flag = flag` or `{ flag = f value < n date > d days > n }`; `has_unit_leader_flag` is deprecated in favour of it.

## Character-scope triggers

Roles: `is_character = ID`, `is_advisor`, `is_hired_as_advisor`, `has_advisor_role = slot`, `is_character_slot` (alias), `is_political_advisor`, `is_army_chief`, `is_navy_chief`, `is_air_chief`, `is_high_command`, `is_theorist`, `not_already_hired_except_as = slot`, `advisor_can_be_fired = yes|{ slot = x }` (false when the role is missing; check `has_advisor_role` first), `is_country_leader`, `is_unit_leader`, `is_army_leader`, `is_navy_leader`, `is_corps_commander`, `is_field_marshal`, `is_operative`, `is_active_scientist`, `has_scientist_level`, `is_theorist`.
Ideology: `has_ideology = type`, `has_ideology_group = group`.
Unit leader state: `attack_skill_level`, `defense_skill_level`, `planning_skill_level`, `logistics_skill_level`, `average_stats`, `has_trait = x`, `can_select_trait`, `has_ability`, `num_units`, `is_assigned`, `is_leading_army`, `is_leading_army_group`, `is_leading_army_in_province`, `is_promoted_from_unit`, `is_general_captured`, `can_be_captured`, `is_exiled_leader`, `is_exiled_leader_from = TAG`, `has_dynamic_modifier`, `is_female`, `is_in_state`, `has_id` (legacy), `has_nationality` (operatives only).
Ledgers: `has_air_ledger`, `has_army_ledger`, `has_navy_ledger`.

## Country-scope character triggers

`has_character = ID`, `can_be_country_leader = ID`, `has_country_leader = { character = ID ruling_only = no }` (`name` and `id` are alternatives), `has_country_leader_ideology = type`, `has_country_leader_with_trait = trait`, `is_leader_visible`, `has_idea_with_trait`, `has_allowed_idea_with_traits` and `has_available_idea_with_traits` (`{ idea = trait_or_list limit = 1 characters = yes ignore = id }`), `has_unit_leader = ID` (legacy), `any_character`, `all_character`, `any_unit_leader`, `all_unit_leader`, `any_army_leader`, `all_army_leader`, `any_navy_leader`, `all_navy_leader`, `any_operative_leader`.

## Iteration scopes (country scope)

`every_character`, `random_character`, `every_unit_leader`, `random_unit_leader`, `every_army_leader`, `random_army_leader`, `every_navy_leader`, `random_navy_leader`, `global_every_army_leader`. Optional keys documented: `tooltip = key`, `random_select_amount = N`, `include_invisible = yes`, `display_individual_scopes = yes`, plus `limit`.
Wiki `Scopes`: invisible unit leaders (role `visible` not satisfied) are excluded by default.

## Dependable patterns

Add a new role to an existing person and make them rule:

```text
TAG_person = {
	add_country_leader_role = {
		promote_leader = yes
		country_leader = {
			ideology = conservatism
			traits = { my_leader_trait }
		}
	}
}
```

Move a person between countries and hire them (vanilla `common/national_focus/belgium.txt`):

```text
TAG_person = {
	set_nationality = TAG2
	add_advisor_role = {
		advisor = {
			slot = political_advisor
			cost = 150
			idea_token = TAG_person
			traits = { my_advisor_trait }
			allowed = {}
		}
	}
}
```

Guard idempotence in repeated scripts: test `has_character`, `is_country_leader`, `has_advisor_role`, or a character flag before the effect, and clear the flag when the state ends.
