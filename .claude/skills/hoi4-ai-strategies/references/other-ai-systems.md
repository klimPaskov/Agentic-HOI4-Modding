# Other AI systems

Read this file when you edit AI division templates, AI equipment designs, goal-based naval AI, faction theaters, AI peace desires, or the AI-facing blocks inside factions, autonomous states, and scripted diplomatic actions.
`GAME` is the installed Hearts of Iron IV folder named in `CLAUDE.md`.

## Contents

- AI templates (`common/ai_templates`)
- AI equipment designs (`common/ai_equipment`)
- Goal-based naval AI (`common/ai_navy`)
- Faction theaters (`common/ai_faction_theaters`)
- AI peace desires (`common/peace_conference/ai_peace`)
- AI attitudes and personalities
- AI hooks inside other definitions

## AI templates (`common/ai_templates`)

Authority: `GAME/common/ai_templates/_documentation.md` (updated 2024-08); wiki `AI modding`, "AI templates".
Vanilla: `generic.txt`, `templates_ENG.txt` (gated progression), `templates_GER.txt`.

How it works:

- A role-level entry names a `role` and holds one or more target templates.
- For each role the AI selects the currently targeted template from `upgrade_prio`, `enable`, and `replace_with` (deterministic highest priority, no randomness at this level; ties go to the first listed).
- It finds the existing division template with the best match score (1.0 is a full match), copies it, and edits the copy toward the target. It never edits in place.
- `role_ratio` and `template_prio` strategies decide how many divisions each role gets and which role is preferred.

Skeleton:

```
infantry_generic = {
	blocked_for = { GER JAP }
	role = infantry
	upgrade_prio = { base = 1 modifier = { factor = 5 } }

	infantry_1 = {
		reinforce_prio = 0
		upgrade_prio = { factor = 1 }
		enable = { date < 1940.3.14 }
		can_upgrade_in_field = { has_equipment = { infantry_equipment > 3000 } }
		target_template = {
			support = { engineer = 1 anti_air = 1 }
			regiments = { infantry = 6 }
		}
		replace_at_match = 0.9
		replace_with = infantry_2
		target_min_match = 0.9
	}
	infantry_2 = {
		target_template = {
			support = { engineer = 1 recon = 1 }
			regiments = { infantry = 9 artillery_brigade = 2 }
		}
	}
}
```

Rules from the documentation:

- Use exactly one of `blocked_for` or `available_for`. Using neither or both gives undefined behaviour.
- Each country should have at most one role-level entry per role. When adding a custom entry for a country, also block that country from the generic entry for the same role.
- Role-level `upgrade_prio` is a weighted random pick of which role to upgrade; 0 stops the AI spending XP on that role. Target-level `upgrade_prio` is a deterministic highest-wins choice.
- `reinforce_prio`: 0 for garrison, 1 default, 2 elite. `custom_icon` and `division_names_group` are optional.
- `can_upgrade_in_field` allows field upgrades to the `replace_with` template when manpower and equipment allow.
- `replace_at_match` is the match score of this template at which the AI moves on; `target_min_match` is the minimum match between the best existing template and the next target for the switch to happen. Use `target_min_match` to hold the AI at a gated step until `upgrade_prio` (for example a tech check) takes over, as `templates_ENG.txt` does for tank generations.
- Some older parameters are being deprecated or renamed; prefer the names in the 2024 documentation.
- Roles seen in vanilla: `infantry`, `armor`, `garrison`, `marines`, `mountaineers`, `paratroopers`, `militias`, `motorized`, `mobile`, `heavy_armor`, `anti_armor`, `mechanized_assault`, `suppression`, `irregular_infantry`, `hq_role`, and special breakthrough roles.
- Triggers for checking AI state: `ai_has_role_template`, `ai_has_role_division`, `ai_wants_divisions`, `has_template_ai_majority_unit` (GAME/documentation/triggers_documentation.md).
- Debug: console `imgui show ai_templates` (targets and best matches) and `imgui show ai_division_production` (wanted divisions per role).

## AI equipment designs (`common/ai_equipment`)

Authority: `GAME/common/ai_equipment/_documentation.md`; vanilla `generic_tank.txt`, `generic_naval.txt`, `generic_planes.txt`, and per-country files.
The AI uses these to create equipment variants and upgrade existing ones.

Structure (per the documentation syntax block and the vanilla example):

```
my_design_group = {
	category = land
	blocked_for = { GER }
	available_for = { }
	roles = { land_light_tank }
	priority = { factor = 1000 }

	my_design = {
		priority = {
			factor = 100
			modifier = { has_tech = improved_light_tank_chassis factor = 0 }
		}
		enable = { }
		history = yes
		target_variant = {
			match_value = 1000
			type = light_tank_chassis_0
			modules = {
				main_armament_slot = tank_heavy_machine_gun
				special_type_slot_1 = empty
			}
			upgrades = { tank_nsb_engine_upgrade = 3 }
		}
		allowed_modules = { tank_heavy_machine_gun }
	}
}
```

- `category` is `naval` (since 1.6.0) or `land` (since 1.11.0); vanilla also has plane files.
- Module slot comparisons: `slot = category`, `slot = module`, `slot < module`, `slot > module`, `slot = empty`, `slot > empty`, nested `{ module = ... any_of = { ... } upgrade > current }`. A lesser restriction favours the earliest module, a greater one the latest.
- `roles` are generated dynamically and can be used with `role_ratio`.
- `allowed_modules` fills remaining open slots after requirements are met; modules not in the list are not used.
- The documentation does not state a precedence rule between a group `priority` and a design `priority`; both are described as adding weight. Compare cases rather than assuming a product or a sum.
- `priority` factors of 0 on a design ("let's not waste XP here" in vanilla) stop the AI spending XP on obsolete designs.
- Related strategy types: `equipment_variant_production_factor`, `production_upgrade_desire_offset`, `*_xp_spend_priority` (`equipment_variant`).

## Goal-based naval AI (`common/ai_navy`)

Authority: `GAME/common/ai_navy/_documentation.md` and `ai_navy/taskforce/_documentation.md`.
Three layers:

1. Goals (`ai_navy/goals/*.txt`): a high-level operation with a priority range.
2. Objectives: a goal applied to a target; the game scores `min_priority + (max_priority - min_priority) * importance` where importance is 0 to 1. Objectives from different goals interleave, so a high-importance objective of a low goal can outrank a low-importance objective of a higher goal.
3. Taskforce and fleet templates (`ai_navy/taskforce/*.txt`, `ai_navy/fleet/*.txt`): compositions and fleets built from taskforces.

Goal skeleton:

```
my_goal = {
	objective_type = convoy_protection
	available_for = { ENG }
	blocked_for = { GER }
	min_priority = 5
	max_priority = 10
}
```

- `objective_type` values: `naval_invasion_support`, `naval_invasion_defense`, `mines_sweeping`, `coast_defense`, `convoy_protection`, `convoy_raiding`.
- If `available_for` is present the goal is disabled for everyone else; if `blocked_for` is present those countries are excluded.
- Taskforce template: `allowed`, `ai_will_do` (<= 0 disables the template), `mission = { naval_patrol }` (currently only one), `min_composition`, `optimal_composition` with ship type counts.
- Fleet template: `required_taskforces = { Name = count }` and `optional_taskforces`.
- Strategy tokens that interact: `naval_avoid_region`, `naval_convoy_raid_region`, `naval_dominance`, `naval_mission_threshold`, `convoy_raiding_target`, `naval_blockade`, `coast_defense`, `strike_force_home_base`.
- Debug: console `imgui show ai_navy`.

## Faction theaters (`common/ai_faction_theaters`)

Authority: `GAME/common/ai_faction_theaters/_documentation.md`; vanilla `ai_faction_theaters.txt`.

```
theater_id = {
	name = theater_loc_key
	ai_will_do = { base = 0 modifier = { add = 1 capital_scope = { is_on_continent = europe } } }
	cancel = { has_war = no }
	regions = { 19 5 7 }
	can_skip_first_region = yes
	preferred_countries = { ENG FRA }
}
```

- `name` is evaluated with the faction leader as the country environment.
- `ai_will_do` and `cancel` are evaluated in the actor country scope.
- Region ids are strategic regions and the theater area must be connected.
- By default the first listed region must be available to create the theater; `can_skip_first_region = yes` relaxes that to any one available region.
- `preferred_countries` is a priority list; the AI does not assign every listed country, only enough to meet the theater's needs.

## AI peace desires (`common/peace_conference/ai_peace`)

Authority: `GAME/common/peace_conference/ai_peace/_documentation.md` (current system since 1.12); wiki `AI modding`, "AI peace".
The pre-1.12 `common/ai_peace` format with per-option MTTH blocks (`annex`, `puppet`, `puppet_all`, `puppet_state`, `take_states`) is described only in the wiki; do not mix it with the new format.

```
peace_ai_desires = {
	my_desire_name = {
		peace_action_type = { take_states puppet }
		enable = {
			ROOT = { tag = ROOT.FROM }
			ROOT.FROM.FROM.FROM = { is_core_of = ROOT.FROM }
		}
		ai_desire = 100
	}
}
```

- Scopes: `ROOT` negotiator, `FROM` taker (owner after the conference), `FROM.FROM` giver (previous owner), `FROM.FROM.FROM` the state when the action concerns a state.
- Action types: `take_states`, `puppet`, `force_government`, `liberate` (and `take_navy`, which has no AI support).
- All desires active for an action are summed; a total of 0 or below means the AI will not take it. `ai_desire` is a percent change: 100 adds 100 percent, -50 reduces by 50, -1000 effectively forbids, 1000 makes it a top priority.
- `enable` may use any trigger, including the `pc_*` triggers. Ownership and diplomatic relations are not updated during a conference, so use `pc_is_puppeted_by`, `pc_is_state_claimed_by`, `pc_is_winner`, and the like for in-conference facts.
- The state's controller is whoever occupied it before the conference; the owner is the original owner.
- Cost modifiers (as opposed to desires) live in `common/peace_conference/cost_modifiers` with `cost_multiplier` (greater than 0, keep roughly 0.4 to 3.0, multiplied together) and `category` for tooltip grouping; they affect cost for everyone, not AI desire.

## AI attitudes and personalities

- `GAME/common/ai_attitudes.txt` defines attitude flags (`antagonize`, `annex`, `weaken`, `coalition`, `vassalize`, `ally`, `befriend`, `protect`, `threat`, `ignore`, `warn`) with `ROOT` as the AI and `FROM` as the target; in the installed file only `attitude_neutral` exists and it is empty.
- `GAME/common/ai_personalities.txt` contains only an empty `ai_balanced` block.
- Do not build features on these two files without confirming they are read by the current game.

## AI hooks inside other definitions

| Definition | AI block | Scope and notes |
| --- | --- | --- |
| Faction goal (`common/factions/goals`) | `ai_will_do` | Scope is the faction member country; chance to fill an empty goal slot. |
| Faction rule (`common/factions/rules`) | `ai_will_do` | Scope is the faction leader; `<= 0` means the AI will not use the rule. Rule initiative spending priority lives here. |
| Autonomous state | `ai_subject_wants_higher`, `ai_overlord_wants_lower`, `ai_overlord_wants_garrison`, `use_for_peace_conference_weight` | Weights or triggers; 0 means never gain or lower a level through the autonomy system. See `hoi4-diplomacy-war`. |
| Scripted diplomatic action | `ai_acceptance` (named conditions), `ai_desire` | ROOT sender, THIS receiver. Used to decide whether the AI sends or accepts. |
| Character trait / idea | `ai_will_do` | Weight for choosing an advisor or leader trait; 0 never picks it. |
| MIO policy | `ai_will_do` | Likelihood the AI spends PP on the policy. |
| Operation, raid | AI strategies `operative_operation`, `operative_mission`, `raid_target_country` | Native raid AI fields are documented in `GAME/common/raids/_documentation.md`; use `hoi4-native-raids` in this repository. |
| Country modifiers | `ai_focus_*_factor`, `ai_desired_divisions_factor`, `ai_get_ally_desire_factor`, `ai_join_ally_desire_factor`, `ai_call_ally_desire_factor`, `ai_badass_factor`, `ai_license_acceptance` | Apply from ideas, spirits, or dynamic modifiers; documented in `modifiers_documentation.md`. |
