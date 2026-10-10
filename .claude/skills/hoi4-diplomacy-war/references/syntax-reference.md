# Diplomacy and war syntax reference

Read this file when you need exact parameters, scope tables, or vanilla file indexes for the mechanisms summarised in `SKILL.md`.
`GAME` is the installed Hearts of Iron IV folder named in `CLAUDE.md`; `WIKI` is `paradox_wiki/` at the mod root.
Primary sources: `GAME/documentation/effects_documentation.md`, `GAME/documentation/triggers_documentation.md`, `GAME/common/factions/_documentation.md`, `GAME/common/on_actions/_documentation.md`, `WIKI/Effects - Hearts of Iron 4 Wiki.md`, `WIKI/Autonomy state modding - Hearts of Iron 4 Wiki.md`, `WIKI/Faction modding - Hearts of Iron 4 Wiki.md`, `WIKI/On actions - Hearts of Iron 4 Wiki.md`.

## Contents

- Effect argument table
- Trigger notes
- Autonomy game rules
- Autonomy setup details
- Faction rule types and vanilla file index
- Faction goals and manifests detail
- On action scope table
- Scripted diplomatic action skeleton

## Effect argument table

| Effect | Scope | Arguments | Source note |
| --- | --- | --- | --- |
| `puppet` | overlord | `X` or `{ target end_wars end_civil_wars }` | Both flags default to yes (installed docs and wiki). |
| `end_puppet` | overlord | `X` | |
| `set_autonomy` | overlord | `{ target autonomy_state freedom_level end_wars end_civil_wars }` | Installed doc example; `autonomous_state` spelling also in vanilla. |
| `release_autonomy` | releaser | `{ target autonomy_state freedom_level release_non_owned_controlled force_change_controller_for_non_ally_controlled }` | `target` may be a variable. Does nothing if the country exists. |
| `release`, `release_on_controlled` | releaser | `X` | Free nation from owned (or owned or controlled) states. |
| `release_puppet`, `release_puppet_on_controlled` | overlord | `X` | Puppet from owned (or owned or controlled) states. |
| `annex_country` | annexer | `{ target transfer_troops }` | |
| `add_autonomy_score` | subject | `{ value localization }` | Exact freedom score. |
| `add_autonomy_ratio` | subject | `{ value localization }` | Percent of the freedom score. |
| `create_faction_from_template` | leader | `template_id` or `{ template name icon color }` | |
| `add_to_faction` | member or leader | `X` | X joins the scoped country's faction. |
| `remove_from_faction` | leader | `X` | |
| `leave_faction`, `dismantle_faction` | member / leader | `yes` | |
| `set_faction_rule` | member of faction | `rule_id` | `available` does not block it. |
| `set_faction_name` | country | `LOC_KEY` | |
| `add_faction_goal`, `remove_faction_goal` | country | `goal_id` | |
| `set_faction_manifest` | country | `goal_id` | Replaces the previous manifest. |
| `add_faction_initiative` | country | `N` | |
| `give_guarantee`, `give_military_access`, `give_market_access`, `send_embargo`, `break_embargo` | giver | `X` | `break_embargo` applies to ROOT only. |
| `diplomatic_relation` | country | `{ country relation active }` | relation in `non_aggression_pact`, `guarantee`, `puppet`, `military_access`, `docking_rights`, `embargo`, `air_base_access`. |
| `add_opinion_modifier`, `reverse_add_opinion_modifier`, `remove_opinion_modifier` | country | `{ target modifier }` | Direction differs; see SKILL.md. |
| `add_relation_modifier`, `remove_relation_modifier` | country | `{ target modifier }` | Modifier from `common/modifiers`. |
| `add_relation_rule_override`, `remove_relation_rule_override` | country | `{ target or trigger, usage_desc, <rule> = yes }` | `set_relation_rule` is deprecated. |
| `set_truce` | country | `{ target days }` | |
| `declare_war_on` | aggressor | `{ target type generator }` | |
| `create_wargoal` | owner | `{ target type generator expire }` | |
| `remove_wargoal` | owner | `{ target type }` (`all` allowed) | |
| `add_to_war` | joiner | `{ targeted_alliance enemy hostility_reason single_target_only }` | |
| `white_peace` | winner | `X` or `{ tag message }` | |
| `start_peace_conference` | winner | `{ tag score_factor winner_scope loser_scope message }` | |
| `transfer_state` | receiver | `STATE_ID` (or `PREV` in state iteration) | Sets owner and controller. |
| `transfer_state_to`, `set_state_owner_to` | state | `COUNTRY` | Owner and controller / owner only. |
| `add_threat`, `add_named_threat` | country | `N` / `{ threat name }` | |
| `set_rule` | country | `{ desc <rule> = yes }` | Overrides other rules on the country. |

## Trigger notes

- `has_opinion = { target = X value > N }` is the vanilla form (`GAME/events/Germany.txt`).
- `has_wargoal_against = X` or `{ target = X type = ID }`; `type` is optional.
- `has_autonomy_state = ID`, `compare_autonomy_state > ID`, `compare_autonomy_progress_ratio > N` take no target.
- `is_puppet` differs from `is_subject`: a subject autonomy state with `is_puppet = no` is still a subject.
- Scope iterators for this domain: `any_/every_/random_subject_country`, `any_/every_allied_country`, `any_/every_enemy_country`, `any_/every_faction_member`, `all_subject_countries`, `all_enemy_country`.
- `has_war_with_wargoal_against` means a war started with a wargoal, not that a wargoal exists.

## Autonomy game rules

Valid names in an autonomous state `rule = { ... }` block (wiki table, which also lists their localised names): `can_access_market`, `can_be_spymaster`, `can_boost_other_ideologies`, `can_boost_own_ideology`, `can_create_collaboration_government`, `can_create_factions`, `can_declare_war_on_same_ideology`, `can_declare_war_without_wargoal_when_in_war`, `can_decline_call_to_war`, `can_force_government`, `can_generate_female_aces`, `can_generate_female_country_leaders`, `can_generate_female_unit_leaders`, `can_guarantee_other_ideologies`, `can_join_factions`, `can_join_factions_not_allowed_diplomacy`, `can_join_opposite_factions`, `can_lower_tension`, `can_not_build_buildings` (the wiki says it does not seem to work), `can_not_declare_war` (prevents generating wargoals but not using existing ones), `can_occupy_non_war`, `can_only_justify_war_on_threat_country`, `can_puppet`, `can_send_volunteers`, `can_use_kamikaze_pilots`, `contributes_operatives` (subjects only), `units_deployed_to_overlord` (subjects only).
`desc` inside `rule` names the reason string shown in tooltips (vanilla uses `RULE_DESC_IS_A_SUBJECT`).
`set_rule` and `has_rule` use the same names; the wiki notes each rule can only be toggled a few times before a reload.

## Autonomy setup details

- Gradual autonomy movement comes from defines (`NDefines.NCountry` entries listed in the wiki: resource trade, war score share, lend-lease, attaché, master building, capitulation). Do not duplicate them with scripted point streams unless needed.
- Collaboration governments use `autonomy_collaboration_government` and `create_dynamic_country`; see `instantiate_collaboration_government` in vanilla `00_scripted_effects.txt` for the pattern (release if the tag is free, otherwise create the dynamic country, transfer controlled states with `transfer_state = PREV`, then `puppet` and `set_autonomy`).

## Faction rule types and vanilla file index

Rule `type` values found in vanilla `GAME/common/factions/rules/*.txt` (counts of definitions): `joining_rules` (24), `war_declaration_rules` (11), `dismissal_rules` (7), `peace_conference_rules` (7), `call_to_war_rules` (5), `change_leader_rules` (5), `contribution_rule` (3), `member_rules` (2).
Rule scopes (installed documentation comment): joining ROOT is the joining country and FROM the leader; war declaration ROOT declares and FROM is the target; call to war ROOT calls and FROM is the target; member rules ROOT is the leader; change leader ROOT is the candidate; peace conference rules carry `peace_action_modifiers`.
Other rule keys: `government_in_exile_allowed_trigger`, `dismiss_member_trigger` (wiki).

| Folder under `GAME/common/factions` | Contents |
| --- | --- |
| `templates` | `generic_factions.txt`, `axis.txt`, `allies.txt`, `soviet_factions.txt`, `unique_minor_factions.txt` and others |
| `rules` | One file per rule family, plus `rules/groups` |
| `goals` | `faction_goals_short_term.txt`, `_medium_term`, `_long_term`, `faction_manifests.txt` |
| `member_upgrades`, `upgrades` | Faction member upgrades and groups |
| `icons` | `pool.txt` |

Faction member upgrade keys (installed documentation): upgrade `name`, `desc`, `icon`, `upgrade_cost` (faction initiative), `bonus`; group `name`, `desc`, `icon`, `upgrades`; the code-supported type is `faction_member_upgrade_manpower`.

## Faction goals and manifests detail

- Goals (`goals/*.txt`): `name`, `description`, `category` (`short_term`, `medium_term`, `long_term`), `group`, `visible`, `available`, `allowed` (checked once), `completed`, `cancel`, `ai_will_do`, `complete_effect`, `select_effect`, `remove_effect`, `cancel_effect`, optional `ratio_progress` or `progress` for continuous goals. ROOT is the faction leader; FROM is the viewing member in `visible`/`available`/`ai_will_do` and is unsupported in the effect blocks and in `completed`/`cancel`. `select_effect` does not run for goals added by a template. By default a faction holds one goal per category; `add_faction_goal_slot` adds extra slots.
- Continuous goals use `ratio_progress` with `total_amount_collection` and `completed_amount_collection` (scripted collections from `common/collections`), or fixed `total_amount` and `completed_amount`; `range = { min max }` maps the ratio to progress.
- Manifests are goals with `is_manifest = yes`, set through the template `manifest` or `set_faction_manifest`.

Goal `group` accepts the focus search filters and custom ones created the same way as focus filters.
`locked_goal = yes` makes a goal irreplaceable until completed (wiki).
`allowed` on a goal is checked once at start or load; adding the goal by `add_faction_goal` bypasses it.

## On action scope table

| On action | Scope notes |
| --- | --- |
| `on_declare_war` | ROOT declares; FROM is the target. |
| `on_war_relation_added` | ROOT attacker, FROM defender; fires for each pair. |
| `on_war` | THIS entered a war from peace. `on_peace`: THIS is no longer at war. |
| `on_capitulation`, `on_capitulation_immediate` | ROOT capitulated, FROM winner. |
| `on_annex` | ROOT winner, FROM annexed. |
| `on_puppet` | ROOT puppeted (peace conference only), FROM overlord. |
| `on_liberate` | ROOT liberated (peace conference only), FROM the liberator leader. |
| `on_release_as_free` | ROOT free nation, FROM releaser. |
| `on_release_as_puppet` | ROOT released nation, FROM overlord (peacetime occupied-territory release). |
| `on_subject_annexed`, `on_subject_free`, `on_subject_autonomy_level_change` | ROOT subject, FROM overlord (previous overlord for free). |
| `on_create_faction` | FROM is the one that joins. `on_faction_formed`: no scope note. |
| `on_offer_join_faction` | FROM invited, THIS and ROOT the leader. `on_join_faction`: ROOT and THIS joiner, FROM leader. |
| `on_assume_faction_leadership` | ROOT new leader, FROM old leader. |
| `on_leave_faction` | ROOT leaving, FROM faction leader. |
| `on_peaceconference_*` | ROOT winner, FROM loser; also triggered by `white_peace`. |
| `on_justifying_wargoal_pulse`, `on_wargoal_expire` | See above. |

## Scripted diplomatic action skeleton

`common/scripted_diplomatic_actions/*.txt`. The only installed file is a commented template, so the structure below follows that comment and has not been confirmed against a working vanilla definition.

```
scripted_diplomatic_actions = {
	my_action = {
		allowed = { always = yes }
		visible = { always = yes }
		selectable = { always = yes }
		requires_acceptance = yes
		cost = 10
		command_power = 0
		on_sent_effect = { }
		complete_effect = { }
		reject_effect = { }
		can_be_sent = { always = yes }
		can_be_accepted = { always = yes }
		ai_acceptance = { condition = { base = 100 } }
		ai_desire = { base = -1 }
	}
}
```

- ROOT is the sender and THIS the receiver in effects, triggers, and variables.
- Optional customisation: `send_scripted_gui`, `receive_scripted_gui`, `reset_send_effect`, `reset_receive_effect`, `send_description`, `receive_description`, `accept_title`, `accept_description`, `reject_title`, `reject_description`, `cost_string`, `show_acceptance_on_action_button`, `icon`.
- `ai_acceptance` is a list of named conditions whose names are used for localisation; `ai_desire` decides whether the AI sends it.
