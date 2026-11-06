# HOI4 Characters, Leaders and Traits: Advisor, unit leader and scientist roles

Part of the [hoi4-characters-leaders](../SKILL.md) skill. Read before defining an advisor, field marshal, corps commander, admiral or scientist role.

## Advisor role

Advisors are ideas placed in character slots; most idea rules apply (`Idea modding` wiki).

- `slot`: `political_advisor`, `theorist`, `army_chief`, `navy_chief`, `air_chief`, `high_command`. Slots are declared by `character_slot` in `common/idea_tags/00_idea.txt` (political_advisor appears three times, high_command three times; theorist is in `research_production`).
- `idea_token`: mandatory and unique. It is the idea id used by `has_idea`, `show_ideas_tooltip` and `activate_advisor`. A missing token acts as a null id and makes other tokenless advisors disappear from selection (wiki). Localise it like any idea (vanilla `ideas_l_english.yml`).
- `ledger`: required for `theorist` and `high_command`; values `army`, `air`, `navy`, `military`, `civilian`, `all`, `hidden`. The other slots inherit their ledger.
- `cost` (political power, default 150 from the category), `removal_cost` (-1 prevents manual removal), `can_be_fired = no` (cannot be dismissed; the old `removal_cost = -1` trick no longer works for this since 1.12.8 per the wiki).
- Trigger blocks: `allowed` (checked once at start or on load; use for country and DLC), `visible` (continuous; hides the advisor), `available` (continuous; greys out), vanilla writes country triggers directly in these blocks (`original_tag`, `has_completed_focus`, `has_country_flag`, `has_government`).
- `on_add` and `on_remove` run in character scope, not country scope; enter the country with `owner = { ... }`.
- `traits`: country leader traits that give modifiers to the country while the advisor is hired and a subtext icon.
- Dual roles: if one character can sit in two slots, guard each with `available = { not_already_hired_except_as = <slot> }` so they cannot fill both.
- `activate_advisor = <idea_token>` (country scope) hires a person in their slot, including in history.
- `add_advisor_role = { character = ID advisor = { slot = ... cost = ... idea_token = ... traits = { ... } allowed = {} } activate = yes }`: roles added by effect cannot contain script blocks (`visible`, `available`, `on_add`). For anything conditional, define the role in the character file with `visible`. Do not `remove_advisor_role` on advisors defined with script; the script cannot be restored.
- A `has_country_flag` placed in `available` or `visible` of a player-visible advisor shows the raw flag name in the tooltip unless localised or wrapped (see Localisation).
- `set_can_be_fired_in_advisor_role = { character = ID slot = ... value = no }` toggles firing at runtime.
- Military advisor tiers (`army_chief_offensive_1` and so on) are country leader traits that cost command power and give experience gain; mirror `common/country_leader/00_traits.txt`.
- Inspect with `is_advisor`, `has_advisor_role = <slot>`, `is_hired_as_advisor`, `is_political_advisor`, `is_army_chief`, `is_navy_chief`, `is_air_chief`, `is_high_command`, `is_theorist`, `advisor_can_be_fired`, `has_idea` (using the token), `has_available_idea_with_traits`.

## Unit leader roles

- Blocks: `corps_commander`, `field_marshal`, `navy_leader`. Keys: `skill`, `attack_skill`, `defense_skill`; army roles also `planning_skill`, `logistics_skill`; navy roles `maneuvering_skill`, `coordination_skill`; `traits = { ... }` from `common/unit_leader/`; `visible = { ... }` (character plus country triggers); `legacy_id` (obsolete).
- What each skill does (wiki table): per level, army attack +2.5% offence, defense +2.5% defence, planning +5% planning speed and +2% max planning bonus, logistics -2.5% supply consumption; navy skill adds hit chance and fleet coordination, attack +5% damage, defense +5% defence, maneuvering +2.5% positioning, coordination +2% fleet coordination. Skill level costs and modifiers are defined in `common/unit_leader/00_*_skills.txt`; read the installed values before quoting them.
- Add by effect: `add_corps_commander_role`, `add_field_marshal_role`, `add_naval_commander_role` (country scope with `character = ID`, or character scope). Remove: `remove_unit_leader_role = yes` (character scope) or with `character =` (the docs example text mentions `remove_corps_commander_role`, but the documented effect name is `remove_unit_leader_role`; use the name in the effect list).
- `promote_leader = yes` (character scope) promotes a general to field marshal; `demote_leader = yes` demotes. This is separate from the `promote_leader = yes` key inside `add_country_leader_role`.
- Legacy creators `create_corps_commander`, `create_field_marshal`, `create_navy_leader` still exist in the documentation but the wiki marks them deprecated: leaders created that way have no portrait for the officer corps and cause errors. Create a character and add the role instead.
- Growth: `gain_xp = N` (character scope, grants experience and promotes at thresholds), `add_skill_level`, `add_attack`, `add_defense`, `add_planning`, `add_logistics`, `add_maneuver`, `add_coordination`, `add_max_trait`, trait effects `add_unit_leader_trait`, `remove_unit_leader_trait`, `replace_unit_leader_trait`, `add_timed_unit_leader_trait`, `add_random_trait`.
- Division officers: an OOB `division = { officer = { name = KEY portraits = { army = { large = GFX_x small = GFX_y } } } }` defines a commander who can be promoted to general; see `hoi4-units-divisions`.
- Command assignment is runtime engine state (armies, army groups); the script surface is limited to reading it (`is_assigned`, `is_leading_army`, `is_leading_army_group`, `num_units`, `is_leading_army_in_province`) and the planning effects.
- Supply: `supply_units = N` (character scope) gives hours of supply to the leader's units.
- Iteration and counting: `every_unit_leader`, `every_army_leader`, `every_navy_leader`, `random_*` variants, `any_unit_leader` and friends (country scope). They skip leaders whose role is not visible unless you add `include_invisible = yes`.

## Scientists and operatives

- A `scientist = { traits = { ... } skills = { specialization_x = N } desc = KEY visible = { ... } }` role is documented in `common/characters/_documentation.md`; the effects `add_scientist_role`, `generate_scientist_character`, `add_scientist_level`, `add_scientist_xp`, `add_scientist_trait`, `remove_scientist_role`, `injure_scientist_for_days` exist. Roles added by effect cannot carry `visible`. Wiki known bug: scientist descriptions do not show.
- Operatives are separate objects: `create_operative_leader`, `operative_leader_event`, `capture_operative`, `free_operative`, `kill_operative` and so on. Do not model them as characters.

