# Unit Leader Traits, Skills and Abilities

Read this when defining or auditing traits in `common/unit_leader/`, trait assignment trees, experience rules, unit-leader skill levels, abilities, or officer-corps advisor conversions.
Primary sources: the header comment of installed `common/unit_leader/00_traits.txt` (the schema), `paradox_wiki/Character modding - Hearts of Iron 4 Wiki.md` > Unit leader traits, `documentation/modifiers_documentation.md` (`unit_leader`, `army`, `naval` scopes), `documentation/triggers_documentation.md` (COMBATANT and CHARACTER sections), and `common/defines/00_defines.lua`.
Root is the installed Hearts of Iron IV folder named in `CLAUDE.md`.

## File and keys

Folder `common/unit_leader/`, any file name, root `leader_traits = { ... }`. Vanilla splits by purpose: `00_traits.txt` (shared), `NSB_traits.txt`, country files (`JAP_traits.txt`, `ETH_traits.txt`, ...), and `00_attack_skills.txt`, `00_defense_skills.txt`, `00_logistics_skills.txt`, `00_planning_skills.txt`, `00_maneuvering_skills.txt`, `00_coordination_skills.txt`, `00_skills.txt` for skill levels.
The trait ids must be unique across the unit-leader database; unit leader traits and country leader traits are separate databases that use the same root key, so keep ids distinct to avoid confusion.

Schema from the vanilla header comment (all keys optional):

```text
trait_key = {
	type = all                     # all, land, navy, operative, corps_commander, field_marshal, or { land navy }
	trait_type = basic_trait       # basic_trait, status_trait, personality_trait, assignable_trait, basic_terrain_trait, assignable_terrain_trait, exile
	attack_skill = 0               # integer, flat
	defense_skill = 0
	logistics_skill = 0
	planning_skill = 0
	maneuvering_skill = 0
	coordination_skill = 0
	attack_skill_factor = 0.0      # decimal, multiplicative (1 adds 100 percent)
	defense_skill_factor = 0.0
	logistics_skill_factor = 0.0
	planning_skill_factor = 0.0
	maneuvering_skill_factor = 0.0
	coordination_skill_factor = 0.0
	show_in_combat = yes
	override_effect_tooltip = ""   # loc key, replaces the effect list
	custom_effect_tooltip = ""     # loc key, appended
	custom_prerequisite_tooltip = ""
	custom_gain_xp_trigger_tooltip = ""
	mutually_exclusive = other_trait
	parent = { traits = { A B C } num_parents_needed = 1 }
	any_parent = { A B C }         # shorthand, one needed
	all_parents = { A B C }        # shorthand, all needed
	gui_row = 0                    # starts at 0; unset or -1 hides it from the unlockable tree
	gui_column = 0                 # unset or -1 means automatic
	allowed = { }                  # scope: unit leader; FROM is the recruiting country
	prerequisites = { }            # scope: unit leader
	gain_xp = { }                  # scope: combatant
	gain_xp_leader = { }           # scope: unit leader
	gain_xp_on_spotting = 0
	modifier = { }                 # applies to the divisions the leader leads
	non_shared_modifier = { }      # applies to the leader only, different tooltip
	corps_commander_modifier = { } # when acting as a corps commander
	field_marshal_modifier = { }   # when acting as a field marshal over generals
	sub_unit_modifiers = { }       # per sub-unit adjusters
	trait_xp_factor = { }          # trait_key = decimal
	on_add = { }                   # scope: unit leader
	on_remove = { }
	daily_effect = { }
	cost = 1000                    # experience to assign
	ai_will_do = { }
	new_commander_weight = { }
	enable_ability = ability_key
}
```

Additional keys seen in vanilla `00_traits.txt` and the wiki: `slot`, `specialist_advisor_trait`, `expert_advisor_trait`, `genius_advisor_trait` (officer-corps conversion to an advisor role using three country leader traits), `unit_type` (limits to sub-unit types), `unit_trigger` (division-scope trigger for modifiers, for example `division_has_majority_template`), `country_trigger` and `allowed_ship_equipments` (navy traits; the latter limits to ship hull groups such as `ship_hull_submarine`), `leader_default_proximity_offset` (personality traits), `custom_gain_xp_trigger_tooltip`.

## Trait types

| `trait_type` | Role (wiki and vanilla use) |
| --- | --- |
| `basic_trait` | Operative or basic traits; hidden from the unlockable tree |
| `personality_trait` | Starting character traits; `new_commander_weight` applies only here |
| `assignable_trait` | Earned with experience, shown in the trait tree (`gui_row`, `parent`, `cost`, `gain_xp`) |
| `basic_terrain_trait`, `assignable_terrain_trait` | Terrain specialists (basic start versus earned) |
| `status_trait` | Wounded, captured and similar states |
| `exile` | Exile leaders |

## Assignment and experience

- The trait tree: `gui_row` places the trait; `parent`/`any_parent`/`all_parents` draw the required links; `mutually_exclusive` must be declared on both traits.
- `cost` is the experience needed to assign the trait; `gain_xp` decides which combat situations grant experience toward it (combatant scope, for example `has_combat_modifier = amphibious_attack`, `temperature < -15`, `dig_in > 10`, or `check_expr` with `num_armored` against `num_units`); `gain_xp = { always = no }` makes a trait non-gainable.
- `gain_xp_leader` is the leader-scope alternative; `trait_xp_factor = { other_trait = 1 }` multiplies experience gained toward other traits (0.1 gives 10 percent more).
- `prerequisites` must hold for the trait to be selectable; add `custom_prerequisite_tooltip` if a trigger inside has no tooltip.
- `allowed` filters whether the trait can be assigned at all; use `FROM = { tag = X }` for country-specific traits (FROM is the recruiting country).
- `new_commander_weight` weights personality traits for generated leaders (`factor = 0` blocks them; vanilla also zeroes weights under officer-academy spirits). `ai_will_do` weights AI picks (0 means never). Keep both reviewed by the AI-probability route.
- Defines affecting leaders (`common/defines/00_defines.lua`): `UNIT_LEADER_INITIAL_TRAIT_SLOT`, `UNIT_LEADER_TRAIT_SLOT_PER_LEVEL`, `UNIT_LEADER_ASSIGN_TRAIT_COST`, `UNIT_LEADER_USE_NONLINEAR_XP_GAIN`, `NEW_COMMANDER_RANDOM_PERSONALITY_TRAIT_CHANCES`, `NEW_ARMY_LEADER_LEVEL_CHANCES`, `FEMALE_UNIT_LEADER_BASE_CHANCE`, the `UNIT_LEADER_MODIFIER_COOLDOWN_*` deploy and withdraw times, `ARMY_LEADER_COST`, `ARMY_LEADER_MAX_COST`. Read the installed values before quoting numbers.

## Modifier blocks

- `modifier = { ... }` applies to the leader's units; terrain scopes nest inside (`urban = { movement = 0.1 }`, `fort = { attack = 0.15 }`).
- `non_shared_modifier` is for stats of the leader itself (for example `experience_gain_factor`, `promote_cost_factor`).
- `corps_commander_modifier` and `field_marshal_modifier` apply by role (for example `max_commander_army_size`, `supply_consumption_factor`, `org_loss_when_moving`). The wiki note: a field marshal who leads divisions directly gets the corps modifier, not the field marshal one.
- `sub_unit_modifiers = { artillery_brigade = { max_strength = 0.1 } }` applies multiplicative sub-unit modifiers (sub-unit ids come from `common/units/`, see `hoi4-units-divisions`).
- Valid modifier names for these blocks come from `documentation/modifiers_documentation.md` under `unit_leader`, `army`, `naval`, `air`; terrain and combat names are listed in the same file.
- Tooltip replacement: `override_effect_tooltip` hides the generated list; `custom_effect_tooltip` appends text.

## Skill levels and skill definitions

- Level definitions: `leader_skills`, `leader_attack_skills` and similar roots in `00_skills.txt`, `00_attack_skills.txt` and siblings, with `cost`, `type = navy` or `land`, `modifier`, and for navy `building_module_modifier`. They are the source for what each level grants; copy structure when adding a new level.
- Character effects that change skill: `add_skill_level`, `add_attack`, `add_defense`, `add_planning`, `add_logistics`, `add_maneuver`, `add_coordination`, `gain_xp`, `add_max_trait`.

## Abilities

- `enable_ability = key` on a trait enables a command-power ability defined in `common/abilities/*.txt` (`generic_leader_abilities.txt` and country files). An ability block in `generic_leader_abilities.txt` has `name`, `desc`, `sound_effect`, `type` (for example `army_leader`), `allowed`, `cost`, `duration`, `unit_modifiers` and `ai_will_do`; copy a vanilla ability.
- `has_ability = key` (character scope) checks it.

## Icons and localisation

- Trait icon: spriteType `GFX_trait_<trait_id>` in any `interface/*.gfx` (vanilla `interface/unitleaderwindow.gfx`, `aat_traits.gfx`, `bba_traits.gfx`). Navy variants have a `_navy` suffix in some vanilla entries.
- Name `<trait_id>: "..."`, description `<trait_id>_desc: "..."` (vanilla `traits_l_english.yml`). Gain-experience tooltips need their own keys (`custom_gain_xp_trigger_tooltip`).
- Define the sprite before requesting art so the file name does not change later. Art production belongs to `hoi4-feature-assets`.

## Worked trait skeletons

Assignable army trait (modeled on vanilla `panzer_leader`):

```text
leader_traits = {
	my_assignable_trait = {
		type = corps_commander
		trait_type = assignable_trait
		gain_xp = { num_units > 10 }
		cost = 700
		gui_row = 1
		modifier = { army_armor_attack_factor = 0.1 }
		ai_will_do = { factor = 1 }
		any_parent = { organizer }
	}
}
```

Personality trait with weighted generation (modeled on `brilliant_strategist`):

```text
	my_personality_trait = {
		type = land
		trait_type = personality_trait
		attack_skill = 1
		attack_skill_factor = 1
		new_commander_weight = { factor = 1 }
	}
```

Check that every referenced parent, exclusive trait, ability, sub-unit and modifier exists before finishing, and that both sides of `mutually_exclusive` are declared.
