---
name: hoi4-characters-leaders
description: Use when defining, recruiting, promoting, retiring or scripting Hearts of Iron IV characters and their roles (country leaders, advisors, field marshals, corps commanders, admirals, scientists), leader traits, ideologies and parties, or character portraits and localisation. Covers the character database, the effects and triggers, and the silent failures.
---

# HOI4 Characters, Leaders and Traits

Generic HOI4 modding guidance for the character system introduced in patch 1.11.
Divisions, templates, orders of battle and manpower belong to `hoi4-units-divisions`.
Weighted AI choices (`ai_will_do`, `new_commander_weight` tuning) belong to `hoi4-ai-strategies`.
Portrait production (research, placeholders, the configured image generator, DDS, wiring, manifests) belongs entirely to `hoi4-feature-assets` and the `hoi4_portrait_creator` subagent; this skill only covers how a portrait is referenced from a character.
Unit-leader trait schema, selection trees, experience rules and abilities are in `references/unit-leader-traits.md`.
Exact signatures and scope notes of the character effects and triggers are in `references/effects-triggers.md`.

## Contents

- Required reading and vanilla precedents
- Mental model and decision table
- Character definition
- Portraits and GFX wiring (overview)
- Country leader role, ideologies and parties
- Advisor role
- Unit leader roles
- Scientists and operatives
- Country leader traits (also used by advisors and ideas)
- Unit leader traits (summary)
- Lifecycle at runtime
- Generated characters
- Triggers and scopes
- Localisation
- Repository conventions
- Common mistakes and silent failures
- Validation checklist

## Required reading and vanilla precedents

With the HOI4 MCP, use `hoi4.reference_search` / `hoi4.reference_read` for the sections below and `hoi4.source_lookup` for vanilla definitions; if a route fails once, retry once, then read the local files directly.
Installed documentation is more authoritative than the wiki. Root: the installed Hearts of Iron IV folder named in `CLAUDE.md`.

| Topic | Primary source |
| --- | --- |
| Character database root, `can_be_captured`, `scientist` block | `common/characters/_documentation.md` (short; the wiki page is the fuller reference) |
| Character-scope effects and country-scope character effects | `documentation/effects_documentation.md` (`## Effects for scope CHARACTER` list, then `## <effect>`) |
| Character, unit-leader and country-leader triggers | `documentation/triggers_documentation.md` (`## Triggers for scope CHARACTER` list, `## <trigger>`) |
| Localisation objects for characters and unit leaders | `documentation/loc_objects_documentation.md` (`## Character`, `## UnitLeader`) |
| Modifier names usable in traits | `documentation/modifiers_documentation.md` (`country`, `army`, `naval`, `air`, `unit_leader`, `character`, `scientist` scopes) |
| Script constants | `documentation/script_concept_documentation.md`, `common/script_constants/documentation.md` |
| Unit leader trait schema | Header comment of `common/unit_leader/00_traits.txt` |
| Idea categories and character slots | `common/idea_tags/00_idea.txt` |
| Ideology types | `common/ideologies/00_ideologies.txt` |

Offline wiki (`paradox_wiki/`): `Character modding - Hearts of Iron 4 Wiki.md` (primary), `Country creation - Hearts of Iron 4 Wiki.md` (Starting characters, Character names, Character portraits), `Ideology modding - Hearts of Iron 4 Wiki.md`, `Idea modding - Hearts of Iron 4 Wiki.md` (advisor-as-idea arguments, categories), `Portrait modding - Hearts of Iron 4 Wiki.md`, `Scopes - Hearts of Iron 4 Wiki.md` (character iterators, `owner`, `party_leader`), `Effects - Hearts of Iron 4 Wiki.md` and `Triggers - Hearts of Iron 4 Wiki.md`.

Vanilla precedents to mirror:

- Character files: `common/characters/GER.txt` (country leaders, advisors with `visible`/`available`/`on_add`, corps commanders, field marshals, admirals, scientists, `allowed_civil_war`), `common/characters/AFG.txt` (`instance` blocks by DLC).
- Country leader and advisor traits: `common/country_leader/00_traits.txt` (header constants, leader traits, `army_chief_*` tiers).
- Unit leader traits: `common/unit_leader/00_traits.txt` (documented schema), `NSB_traits.txt`, `common/unit_leader/00_*_skills.txt` (skill level costs and modifiers).
- Country history recruiting: `history/countries/GER - Germany.txt` and any other tag file (`recruit_character`, then `set_politics`).
- Generic characters by effect: `history/general/generic_advisors.txt`, `china_shared_advisors.txt`, `spain_shared_advisors.txt`.
- Runtime role changes: `common/decisions/TUR.txt` (`remove_unit_leader_role = yes`), `common/decisions/CHI_decisions.txt` (`add_corps_commander_role`), `common/national_focus/belgium.txt` (`set_nationality` then `add_advisor_role`), `common/scripted_effects/SOV_scripted_effects.txt` (`has_character`, `set_nationality`, `promote_character = { character = ... ideology = ... }`).
- Portrait pools for generated characters: `portraits/*.txt`; generated-leader names: `common/names/*.txt`.
- Sprites: `interface/ideas.gfx` (`GFX_idea_traits_strip`), `interface/unitleaderwindow.gfx` (unit leader trait icons `GFX_trait_<id>`), `interface/*_characters.gfx` for portrait sprite files.
- Localisation: `localisation/english/nsb_characters_l_english.yml` (character names), `traits_l_english.yml` (trait names and descriptions), `parties_l_english.yml` (ideology and party names), `ideas_l_english.yml` (advisor idea tokens).
- Abilities for unit leaders: `common/abilities/*.txt`.

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

## Character definition

Skeleton (wiki `Character modding` and vanilla `common/characters/GER.txt`):

```text
characters = {
	TAG_example_person = {
		name = TAG_example_person
		gender = female
		can_be_captured = no
		portraits = {
			civilian = {
				large = GFX_portrait_TAG_example_person
				small = GFX_portrait_TAG_example_person_small
			}
			army = {
				large = GFX_portrait_TAG_example_person_army
			}
		}
		country_leader = {
			ideology = liberalism
			traits = { my_leader_trait }
			expire = "1965.1.1.1"
		}
		advisor = {
			slot = political_advisor
			idea_token = TAG_example_person
			traits = { my_advisor_trait }
			cost = 150
			allowed = { original_tag = TAG }
			available = { has_completed_focus = TAG_some_focus }
			visible = { has_country_flag = TAG_person_visible }
			on_add = { }
			on_remove = { }
		}
		corps_commander = {
			traits = { }
			skill = 3
			attack_skill = 3
			defense_skill = 2
			planning_skill = 3
			logistics_skill = 2
		}
	}
}
```

Rules and notes:

- The character id (outer key) is what `recruit_character`, `promote_character` and scope entry use (`TAG_example_person = { ... }`). File names do not matter.
- `name`: a localisation key. If the name or portrait is missing, the engine generates them from gender, country name lists and portrait pools.
- `gender`: `undefined` (default, behaves like male in almost all respects), `male`, `female`. Used for pronouns in `[Character.GetSheHe]` style loc and for generating missing names or portraits.
- `can_be_captured = no`: general cannot be captured (installed `common/characters/_documentation.md`). Characters with a country leader role are always uncapturable.
- `instance = { allowed = { ... } <whole character body> }`: alternative definitions evaluated once at game start; each instance needs an `allowed` block and the character needs multiple instances to make sense (`common/characters/AFG.txt`). A single-state character should omit `instance`.
- One role block per slot: repeat `advisor = {}` for several slots; repeat `country_leader = {}` for several ideologies.
- Role keys seen in vanilla characters: `country_leader`, `advisor`, `corps_commander`, `field_marshal`, `navy_leader`, `scientist`, plus `allowed_civil_war` (a trigger block seen in vanilla, for example `GER_heinrich_himmler`; it is not in the sources read, so treat it as civil-war side selection by inference and check a vanilla example before using it).
- `id = -1` and `legacy_id = N` are leftovers from the pre-1.11 leader system. Omit them in new content and use character-specific triggers.
- Do not rely on file ordering; ids must be globally unique across all character files.

## Portraits and GFX wiring (overview)

- `portraits` has three categories: `civilian`, `army`, `navy`; each holds `large` and `small`. A small portrait in any category serves as an advisor portrait; a large portrait is used for leaders and commanders and is category-specific.
- Values are `spriteType` names defined in `interface/*.gfx` (the name must start with `GFX_`, contain no spaces and be ASCII), or direct `gfx/...` paths. Sprites are the recommended form (wiki).
- Army leaders also need a small portrait (officer corps ministers). Either define `small` explicitly or add a sprite named `<large_sprite_name>_small`; the `_small` suffix convention also applies to portraits drawn from `portraits/*.txt`.
- If a portrait definition is invalid the engine silently substitutes a random portrait. Check, in order: the sprite name spelling, the `interface/*.gfx` file extension and `spriteTypes = { }` wrapper, the `texturefile` path (forward slashes, extension included), and the file on disk.
- Wiki: if a category defines a valid sprite for one size but not the other, no random portrait is generated for the missing size, so it can show blank. Define both sizes.
- Characters without a portrait show a silhouette or nothing during country selection and receive a generated portrait only after the game starts (cosmetic tags decide the pool).
- Portraits can be changed in play with `set_portraits` (country scope with `character = X`, or character scope); animated portraits use `frameAnimatedSpriteType` (see `hoi4-frame-animation`).
- Conventional locations: advisor art in `gfx/interface/ideas/`, leader art in `gfx/leaders/<TAG>/`; the folder is not enforced.
- Prefer new `.gfx` files for mod sprites; a later-sorted file name overrides an earlier sprite of the same name (wiki `Character modding` > Portraits). Never edit vanilla `.gfx` files.
- Production of the art, grounded source handling, DDS conversion and manifests are not documented here: use `hoi4-feature-assets` and route every portrait to `hoi4_portrait_creator`.

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
- Effects that touch the sitting leader without naming a character (`kill_country_leader`, `retire_country_leader`, `kill_ideology_leader`, `retire_ideology_leader`) are discouraged by the wiki because they affect whoever currently holds the role. See `references/effects-triggers.md` for how their behaviours differ.
- Changing a leader's ideology type in play: `set_country_leader_ideology`; names, portraits and descriptions of leaders: `set_country_leader_name`, `set_country_leader_portrait`, `set_country_leader_description` (no tooltip is generated).
- Inspect with `has_country_leader = { character = ID ruling_only = no }`, `has_country_leader_ideology`, `has_country_leader_with_trait`, `can_be_country_leader`, `has_character`, character-scope `is_country_leader`, `has_ideology`, `has_ideology_group`.

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
- `targeted_modifier` and `equipment_bonus` blocks work like in ideas. `research_bonus` and `rule` blocks do not work in traits (wiki).
- `ai_will_do` weights advisor and idea selection by the AI (default 1; 0 means never).
- Modifiers are country modifiers (they apply to the country that holds the leader or advisor). Look up names in `documentation/modifiers_documentation.md`.
- Localisation: `<trait_id>: "Name"` and optionally `<trait_id>_desc`.
- Use script constants for repeated tuning (see repository conventions) instead of file-scoped `@` values in new files.

## Unit leader traits (summary)

File: `common/unit_leader/*.txt`, root `leader_traits = { ... }`. Different database from country leader traits, even though both use the same root key; ids must not collide.
Schema, trait types, assignment trees (`parent`, `any_parent`, `mutually_exclusive`, `gui_row`), experience triggers (`gain_xp`, `gain_xp_leader`, `cost`), modifier blocks (`modifier`, `non_shared_modifier`, `corps_commander_modifier`, `field_marshal_modifier`, `sub_unit_modifiers`), restrictions (`allowed`, `prerequisites`, `unit_type`, `unit_trigger`, `country_trigger`, `allowed_ship_equipments`), advisor conversions (`slot`, `specialist_advisor_trait`, `expert_advisor_trait`, `genius_advisor_trait`), abilities and sprites: see `references/unit-leader-traits.md`.

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

## Localisation

- Character name: the `name` key, in a character name file (vanilla `nsb_characters_l_english.yml`). Keys defined once can be reused with `$other_key$`.
- Character description: the wiki states `<id>_desc`; country leader `desc` must be a key; vanilla characters mostly omit descriptions.
- Advisor idea token: `<idea_token>: "Name"` and optional `<idea_token>_desc`.
- Trait: `<trait>` and `<trait>_desc`; unit leader trait icon `GFX_trait_<trait>`.
- Ideology and party names: `parties_l_english.yml` pattern.
- Advisor ideas are ideas: for generic idea, spirit and modifier mechanics use `hoi4-ideas-modifiers`.
- A flag trigger such as `has_country_flag` placed in a player-visible `available` block uses the flag name as the tooltip key. Localise it or wrap it: `hidden_trigger` plus `custom_trigger_tooltip`.
- Localisation files: UTF-8 with BOM, `l_english:` header, keys without `:0` in this repository.

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
