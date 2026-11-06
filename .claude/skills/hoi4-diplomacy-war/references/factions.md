# HOI4 Diplomacy and War: Factions

Part of the [hoi4-diplomacy-war](../SKILL.md) skill. Read before creating or changing factions, faction templates, rules, rule groups, goals or manifests.

## Factions

### Effects (GAME/common/factions/_documentation.md, effects documentation)

- `create_faction_from_template = template_id`, or with `name`, `icon`, `color` (name is a localisation key, icon a `GFX_` sprite, color a three-number block). `create_faction` is marked deprecated (it uses the default template if the Deeper Factions DLC is enabled).
- `add_to_faction`, `remove_from_faction`, `leave_faction`, `dismantle_faction`, `set_faction_leader`, `set_faction_name`, `set_faction_rule`, `set_faction_manifest`, `add_faction_goal`, `remove_faction_goal`, `add_faction_initiative`, `add_faction_power_projection`, `add_faction_influence_score`, `add_faction_influence_ratio`, `set_faction_spymaster`, `set_faction_upgrade`, `set_faction_member_upgrade_min`, `set_faction_military_unlocked`, `set_faction_research_unlocked`.
- Creating a faction needs `can_create_factions`; vanilla scripts set it first: `hidden_effect = { set_rule = { can_create_factions = yes } }` (see `AST_scripted_effects.txt`).
- Typical sequence in vanilla (`common/scripted_effects/AST_scripted_effects.txt`, `events/BBA_Italy.txt`): `LEADER = { create_faction_from_template = template  add_to_faction = MEMBER }`. If the leader is already a faction leader, skip creation and call `add_to_faction`.

### Triggers

`is_in_faction`, `is_in_faction_with`, `is_faction_leader`, `has_faction_template`, `faction_manifest_fulfillment`, `faction_power_projection`, `faction_influence_score|ratio|rank`, `has_faction_goal`, `has_completed_faction_goal`, `faction_goal_fulfillment`, `has_manpower_to_become_leader`, `has_industry_to_become_leader`, plus scope iterators `any_/every_/random_faction_member` and the `faction_leader` scope.

### Definition files (all under `common/factions`)

- Template (`templates/*.txt`):

```
faction_template_my_pact = {
	name = my_pact_name
	manifest = faction_manifest_strength_in_unity
	icon = GFX_faction_logo_generic
	can_leader_join_other_factions = yes
	visible = { always = no }
	available = { has_government = democratic }
	goals = { faction_goal_a_military_base }
	default_rules = {
		joining_rule_neighbors_only
		dismissal_rule_offensive_war
		change_leader_rule_manpower
	}
}
```

  An empty `visible` hides the template from the creation screen, which makes it script-only. A template icon strip has two 100-pixel logos in a 200 by 100 file and needs a `_miniature` sprite of the same name (wiki). `can_leader_join_other_factions = yes` means the leader cannot leave without dismantling the faction.
- Rules (`rules/*.txt`) carry `type`, `visible`, `available`, `can_remove`, `trigger`, `modifier`, `effect`, `ai_will_do`, and for peace rules `peace_action_modifiers`. The rule `type` tokens used by vanilla are plural: `joining_rules`, `war_declaration_rules`, `call_to_war_rules`, `change_leader_rules`, `dismissal_rules`, `member_rules`, `contribution_rule`, `peace_conference_rules`; the installed documentation comment and the wiki spell some singular (`joining_rule`, `war_declaration_rule`), so copy the vanilla spelling.
- Rule scopes depend on type: for `joining_rules` ROOT is the joining country and FROM the faction leader; for `war_declaration_rules` ROOT declares and FROM is the target; for `call_to_war_rules` ROOT calls and FROM is the target; for `change_leader_rules` ROOT is the candidate leader; for `member_rules` and `peace_conference_rules` ROOT is the leader.
- A rule does not appear unless it belongs to at least one rule group (`rules/groups/*.txt`: `group_id = { default_rule = ... rules = { ... } }`). A template's `default_rules` overrides group defaults.
- `available` does not block `set_faction_rule`, and `can_remove` does not block removal by effect.
- Goals (`goals/*.txt`) and manifests: ROOT is the faction leader and FROM the viewing member in `visible`, `available`, and `ai_will_do`; FROM is unsupported in effect blocks, `completed`, and `cancel`. Details, continuous `ratio_progress`, and slot rules are in `references/syntax-reference.md`.
- Faction initiative spending priorities for AI come from strategies (`spent_faction_initiative_priority`) and rule `ai_will_do`; see `hoi4-ai-strategies`.

