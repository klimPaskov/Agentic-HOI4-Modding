# HOI4 Characters, Leaders and Traits: Country leader role and leader traits

Part of the [hoi4-characters-leaders](../SKILL.md) skill. Read before defining a country_leader role, ideology and party wiring, or a country leader or unit leader trait.

## Country leader role, ideologies and parties

Role block:

```text
country_leader = {
	ideology = socialism
	traits = { my_leader_trait }
	expire = "1965.1.1.1"
	desc = TAG_example_person_desc
}
```

- `ideology` is an ideology type from `common/ideologies/00_ideologies.txt` (`types = { ... }` inside a group), never a group such as `democratic`. Vanilla groups and types: democratic (conservatism, liberalism, socialism, populism), communism (marxism, leninism, stalinism, anti_revisionism, anarchist_communism, buddhist_socialism), fascism (nazism, gen_nazism, fascism_ideology, falangism, rexism, emperor_fascism), neutrality (despotism, oligarchism, anarchism, moderatism, centrism, japan_militarism_ideology). Wiki table lists notes such as "cannot be randomly selected".
- Declaring a second block for an ideology group that already exists is reported to discard the whole block and cascade into invalid-ideology errors, and the game executable holds the messages "Duplicate database id" and "is not a valid ideology". [unverified]
- Types change flavour: the tooltip description, an optional type icon, and opinion modifiers: same group gives "Same Ideology" (+10), same type gives "Same Ruling Party" (+20) (wiki).
- `expire`: date after which the leader cannot be used. A start date after `expire` makes the leader unusable even if recruited.
- `desc`: must be a localisation key; literal text does not show.
- `traits`: country leader traits (see below). Applied to the country while the character leads.
- `id`: obsolete; omit.
- Party leadership: when a leader is recruited, the engine tries to make them the leader of that ideology group's party. The first recruited leader of a group wins; later ones wait as candidates. `set_politics` forces a leader to exist, creating a random character if none is recruited yet, so recruit leaders before `set_politics` in country history. Characters recruited afterwards will not replace an already chosen leader.
- Changing leaders later: `promote_character` (country scope: `promote_character = ID` or `{ character = ID ideology = type }`; character scope: `promote_character = yes` or `= type`). The ideology is mandatory when the character has several leader roles. Retiring the previous leader is not required.
- `add_country_leader_role = { character = ID promote_leader = yes country_leader = { ideology = ... traits = { ... } } }`: adds the role to a recruited character; does nothing if the character already has a role in that ideology group.
- Initially empty leaders: define a character without a role, recruit it, and add the role later (wiki `Character modding` > Using in-game).
- `create_country_leader = { name = "..." desc = KEY picture = "..." expire = "..." ideology = ... traits = { ... } }` is the legacy creator. Its documentation says that an existing character with the same token or name only gets the role added. Prefer characters.
- Politics in country history: `set_politics`, `set_popularities` (must total 100). Ideology and party naming: `<type>`, `<type>_desc`, `<group>_party`-style keys in `parties_l_english.yml`; country naming uses `TAG_<ideology>`, `TAG_<ideology>_ADJ`, `TAG_<ideology>_DEF` (wiki `Ideology modding` > Localisation). Ideology icons: `GFX_ideology_<group>_group`, `GFX_ideology_<type>`, with country prefix variants `GFX_ideology_<TAG>_<name>`.
- The `ruling_party` value of `set_politics` and the keys of `set_popularities` are ideology group names, never subtypes. [vanilla-confirmed 1.19.4.1]
- Effects that touch the sitting leader without naming a character (`kill_country_leader`, `retire_country_leader`, `kill_ideology_leader`, `retire_ideology_leader`) are discouraged by the wiki because they affect whoever currently holds the role. See `references/effects-triggers.md` for how their behaviours differ.
- Changing a leader's ideology type in play: `set_country_leader_ideology`; names, portraits and descriptions of leaders: `set_country_leader_name`, `set_country_leader_portrait`, `set_country_leader_description` (no tooltip is generated).
- Inspect with `has_country_leader = { character = ID ruling_only = no }`, `has_country_leader_ideology`, `has_country_leader_with_trait`, `can_be_country_leader`, `has_character`, character-scope `is_country_leader`, `has_ideology`, `has_ideology_group`.

## Country leader traits (also used by advisors and ideas)

File: `common/country_leader/*.txt`, root `leader_traits = { ... }`. Despite the name these traits are usable on advisors, ideas and leaders.

```text
leader_traits = {
	my_leader_trait = {
		random = no
		sprite = 1
		political_power_gain = 0.1
		equipment_bonus = { train_equipment = { build_cost_ic = 0.05 } }
		ai_will_do = { base = 2 }
	}
	army_chief_example_1 = {
		sprite = 7
		army_attack_factor = 0.05
		experience_gain_army = @chief_experience_gain_low
		command_cap_increase = @tier1_cp_cap_increase
		command_power = @tier1_cp_cost
		ai_will_do = { factor = @army_chief_factor_1 }
	}
}
```

- `random = no` keeps the trait out of randomly created leaders.
- `sprite = N` picks frame N (from 1) of the horizontal strip `GFX_idea_traits_strip` (`interface/ideas.gfx`, 18 frames in the installed file, `noOfFrames = 18`). If you replace the strip, redefine the sprite in a later-sorted `.gfx` file with the right `noOfFrames`.
- Command power pricing: vanilla advisor traits use `command_cap_increase` and `command_power` (with file-scoped `@` constants in `00_traits.txt`); the wiki describes `command_cap`. Mirror the installed vanilla file when pricing military advisors.
- `nationalist` is not a country leader trait, while `conservative_nationalist` is. [vanilla-confirmed 1.19.4.1]
- `targeted_modifier` and `equipment_bonus` blocks work like in ideas. `research_bonus` and `rule` blocks do not work in traits (wiki).
- `ai_will_do` weights advisor and idea selection by the AI (default 1; 0 means never).
- Modifiers are country modifiers (they apply to the country that holds the leader or advisor). Look up names in `documentation/modifiers_documentation.md`.
- Localisation: `<trait_id>: "Name"` and optionally `<trait_id>_desc`.
- Use script constants for repeated tuning (see repository conventions) instead of file-scoped `@` values in new files.

## Unit leader traits (summary)

File: `common/unit_leader/*.txt`, root `leader_traits = { ... }`. Different database from country leader traits, even though both use the same root key; ids must not collide.
Schema, trait types, assignment trees (`parent`, `any_parent`, `mutually_exclusive`, `gui_row`), experience triggers (`gain_xp`, `gain_xp_leader`, `cost`), modifier blocks (`modifier`, `non_shared_modifier`, `corps_commander_modifier`, `field_marshal_modifier`, `sub_unit_modifiers`), restrictions (`allowed`, `prerequisites`, `unit_type`, `unit_trigger`, `country_trigger`, `allowed_ship_equipments`), advisor conversions (`slot`, `specialist_advisor_trait`, `expert_advisor_trait`, `genius_advisor_trait`), abilities and sprites: see `references/unit-leader-traits.md`.

