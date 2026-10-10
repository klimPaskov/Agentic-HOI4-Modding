---
name: hoi4-diplomacy-war
description: Use when scripting Hearts of Iron IV diplomacy, factions, subjects and autonomy states, wargoals, declarations of war, white peace or peace conferences, guarantees, military access, embargoes, opinion modifiers, annexation, release, or state transfer between countries.
---

# HOI4 Diplomacy and War

Generic guidance for scripting relations between countries: factions, subjects, wargoals, war, peace, and territory transfer.
Use it to choose the right mechanism, write it with verified syntax and scopes, and avoid the silent failures.
Use `hoi4-ai-strategies` for steering how the AI uses these systems (`conquer`, `befriend`, `diplo_action_*`, peace desires), `hoi4-decisions-missions` for decision and mission structure, and `hoi4-events` for event wiring when working in this repository.

## Contents

- Source map
- Decision procedure: which mechanism for which goal
- Scope and target rules for diplomacy effects
- Factions
- Subjects and autonomous states
- Diplomatic relations
- Wargoals, declaring war, and joining wars
- Peace: white peace, limited conferences, and conference hooks
- Territory, release, annexation, and puppets
- On actions for diplomacy and war
- Scripted diplomatic actions
- AI hooks
- Localisation and tooltips
- Validation
- Repository conventions
- Common mistakes
- Unverified or conflicting points

Argument tables and longer skeletons are in `references/syntax-reference.md` inside this skill folder.
Read it when you need exact parameters of an effect or trigger, the list of autonomy game rules, faction rule types, or vanilla file indexes.

## Source map

`GAME` means the installed Hearts of Iron IV folder named in `CLAUDE.md`.
`WIKI` means the offline snapshot in `paradox_wiki/` at the mod root.
Installed documentation outranks the wiki; record any disagreement.

| Topic | Authoritative text | Vanilla precedent |
| --- | --- | --- |
| Effect syntax | `GAME/documentation/effects_documentation.md` (search the effect name); `WIKI/Effects - Hearts of Iron 4 Wiki.md` sections "Diplomacy", "Autonomy", "War", "Factions" | Decisions, events, and `GAME/common/scripted_effects/00_scripted_effects.txt` |
| Trigger syntax | `GAME/documentation/triggers_documentation.md` | |
| Factions: goals, rules, rule groups, templates, manifests, member upgrades | `GAME/common/factions/_documentation.md`; `WIKI/Faction modding - Hearts of Iron 4 Wiki.md` | `GAME/common/factions/templates/generic_factions.txt`, `rules/joining_rules.txt`, `rules/war_declaration_rules.txt`, `goals/faction_goals_short_term.txt` |
| Autonomous states | `WIKI/Autonomy state modding - Hearts of Iron 4 Wiki.md` (there is no installed documentation file for this folder) | `GAME/common/autonomous_states/puppet.txt`, `dominion.txt`, `integrated_puppet.txt` |
| Wargoal types | No installed or wiki documentation page; read the vanilla definition | `GAME/common/wargoals/00_invasion.txt` |
| Opinion modifiers | Header comments of `GAME/common/opinion_modifiers/00_opinion_modifiers.txt`; wiki Effects, "Diplomacy" | `00_opinion_modifiers.txt`, `00_diplomatic.txt` |
| Scripted diplomatic actions | Commented template at the top of `GAME/common/scripted_diplomatic_actions/scripted_diplomatic_actions.txt` | The same file (documentation only in vanilla) |
| Peace conference cost modifiers and AI desires | `GAME/common/peace_conference/cost_modifiers/_documentation.md`, `ai_peace/_documentation.md` | `cost_modifiers/00_generic_peace.txt`, `ai_peace/00_misc.txt` |
| On actions | `GAME/common/on_actions/_documentation.md` (list, updated 2024-11); `WIKI/On actions - Hearts of Iron 4 Wiki.md` (scopes) | `GAME/common/on_actions/00_on_actions.txt` |
| Rules, game-rule options | `WIKI/Autonomy state modding` rule table; `set_rule` / `has_rule` in the effects and triggers docs | |
| Decision war warnings | `WIKI/Decision modding - Hearts of Iron 4 Wiki.md` ("Warning for war", missions) | |
| Tuning constants | `GAME/common/defines/00_defines.lua` (`NDefines.NCountry`, `NFactions`, `NAI`, wargoal and tension entries); `WIKI/Defines - Hearts of Iron 4 Wiki.md` | |

Use the hoi4 MCP routes (`hoi4_reference_search`, `hoi4_reference_read`, `hoi4_source_lookup`, `hoi4_script_validate`) to cite exact lines.
If a route fails once, retry once with narrower input, then read the local file directly.

## Decision procedure: which mechanism

| Intent | Use | Notes |
| --- | --- | --- |
| Put a country under another at game start | `puppet` or `set_autonomy` in the overlord's scope in `history/countries` | Place before political setup in the subject's history, see the subject section. |
| Change a subject's level during play | `set_autonomy` in the overlord's scope | Use `add_autonomy_score` or `add_autonomy_ratio` in the subject's scope to move gradually. |
| Make a subject independent | `set_autonomy` with `autonomy_state = autonomy_free` in the overlord's scope, or `end_puppet` | `set_autonomy` has to run in the current overlord's scope. |
| Create a new country as a subject from owned or controlled land | `release_autonomy`, `release_puppet`, `release_puppet_on_controlled`, `release_on_controlled` | These do nothing if the country already exists. |
| Annex a country | `annex_country = { target = X transfer_troops = yes }` | Omitting `transfer_troops` loses the annexed divisions' equipment. |
| Move one state between countries | `transfer_state` (country scope, state argument) or `transfer_state_to` / `set_state_owner_to` (state scope) | Ownership and control differ between these. |
| Put countries in or out of a faction | `create_faction_from_template`, `add_to_faction`, `remove_from_faction`, `leave_faction`, `dismantle_faction` | Needs the `can_create_factions` rule to be allowed. |
| Restrict who may join or lead a faction, or declare war inside it | Faction rules in `common/factions/rules` | Install them through templates or `set_faction_rule`. |
| Give a faction a quest | Faction goals and manifests | Needs the Deeper Factions DLC feature set per the wiki. |
| Open or close a bilateral relation (guarantee, military access, NAP, docking, air base, embargo) | `diplomatic_relation`, `give_guarantee`, `give_military_access`, `send_embargo`, `give_market_access` | `diplomatic_relation` with `active = no` is the documented way to end one. |
| Change how much a country likes another | `add_opinion_modifier`, `reverse_add_opinion_modifier`, `remove_opinion_modifier` with a modifier defined in `common/opinion_modifiers` | Direction matters. |
| Apply a targeted modifier between two countries | `add_relation_modifier` with a modifier from `common/modifiers` | Different system from opinion. |
| Let the player propose a custom accept/reject offer to other countries | `common/scripted_diplomatic_actions` | See the section below. |
| Prepare a war the player or AI must justify | `create_wargoal`, then `declare_war_on` or the player's own diplomacy | Pair decisions with `war_with_on_*`. |
| Force a war immediately | `declare_war_on = { target = X type = <wargoal> }` | Needs a defined wargoal type. |
| Pull a country into an existing war | `add_to_war` | Not a declaration against a new enemy. |
| End a war with no winner | `white_peace` | ROOT counts as winner for name and on-action purposes. |
| End a war with spoils | `start_peace_conference` (limited conference) | Score fraction controls the outcome. |
| React after the fact | On actions (`on_declare_war`, `on_peaceconference_ended`, `on_join_faction`, `on_subject_free`, ...) | Mind the ROOT and FROM meanings. |
| Block or enable a diplomatic capability without a new mechanism | `set_rule`, or `rule` in an autonomous state, or faction rules | Rules are overrides; see the rule notes. |

## Scope and target rules

- Diplomacy and war effects execute in the scope of the acting country; the argument is the other party. `GER = { declare_war_on = { target = POL type = take_state } }` makes Germany the aggressor.
- Direction conventions that are easy to reverse:
  - `add_opinion_modifier`: the scoped country gains opinion toward `target`. `reverse_add_opinion_modifier`: `target` gains opinion toward the scoped country. For a modifier flagged `trade = yes` the behaviour is reversed.
  - `add_to_faction = X`: X joins the scoped country's faction. `remove_from_faction = X`: removes X from the faction the scoped country leads. `leave_faction = yes`: the scoped country leaves.
  - `puppet = X`, `release_puppet = X`, `end_puppet = X`, `annex_country = { target = X }`: the scoped country is the overlord or annexer.
  - `set_autonomy`, `release_autonomy`: run in the overlord's scope with `target = subject`. `add_autonomy_score` and `add_autonomy_ratio`: run in the subject's scope.
  - `give_guarantee = X` and `give_military_access = X`: the scoped country gives them to X. Mutual access needs two calls (vanilla `common/decisions/BEL.txt`).
  - `send_embargo = X`: scoped country embargoes X. `break_embargo = X` always applies to ROOT per the wiki, so use `diplomatic_relation` with `relation = embargo` to break another country's embargo.
  - `white_peace = X` and `start_peace_conference`: the scoped country is the winner.
  - `transfer_state` acts in the receiving country's scope; `transfer_state_to` acts in the state scope.
- Targets can be tags, scopes (`ROOT`, `PREV`, `FROM`, `OWNER`, `CONTROLLER`, `OCCUPIED`, `CAPITAL`), or variables (`target = var:my_var`, or a scoped variable name). Diplomatic effects list `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL` as supported targets in the effects documentation.
- A removed or non-existent country is not a valid scope. Guard with `country_exists = TAG` (or `exists = yes` on a stored variable scope) before targeting it.
- Temporary variables carry no scope; use normal variables or event targets to remember countries across scope changes.

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

## Subjects and autonomous states

### Definition (`common/autonomous_states/*.txt`; wiki "Autonomy state modding")

```
autonomy_state = {
	id = autonomy_example
	default = yes
	is_puppet = yes
	use_overlord_color = yes
	min_freedom_level = 0.4
	peace_conference_initial_freedom = 0.5
	manpower_influence = 0.9
	rule = {
		desc = "RULE_DESC_IS_A_SUBJECT"
		can_not_declare_war = yes
		can_decline_call_to_war = no
	}
	modifier = {
		autonomy_manpower_share = 0.9
		extra_trade_to_overlord_factor = 1.0
	}
	ai_subject_wants_higher = { factor = 1.0 }
	ai_overlord_wants_lower = { factor = 1.0 }
	ai_overlord_wants_garrison = { always = no }
	allowed = { OVERLORD = { NOT = { has_government = fascism } } }
	use_for_peace_conference_weight = { base = 0 }
	can_take_level = { }
	can_lose_level = { }
	allowed_levels_filter = { autonomy_example autonomy_other }
}
```

Facts:

- `min_freedom_level` orders the states on the freedom scale; the points needed between two levels are the difference times `AUTONOMOUS_TOTAL_SCORE` (5000) per the wiki. Avoid two states with the same `min_freedom_level`.
- `default = yes` makes the state a candidate for the `puppet` effect and for puppeting in peace deals, filtered by `allowed`.
- The `puppet` effect picks a state with `default = yes` whose `allowed` is true. The wiki states it crashes to desktop if none qualifies, so keep at least one default state whose `allowed` can always be satisfied, and test any `allowed` that depends on DLC or overlord.
- `allowed` supports the `OVERLORD` scope. `use_for_peace_conference_weight` has ROOT as the subject and FROM as the potential overlord.
- `is_puppet = yes` makes `is_puppet` and `is_puppet_of` true. A subject state with `is_puppet = no` (for example `autonomy_dominion`) is still a subject for `is_subject` and `is_subject_of`.
- A state that must only be reachable by `set_autonomy` can use `allowed = { OR = { is_subject = no has_autonomy_state = autonomy_my_state } }`; the wiki notes this keeps `set_autonomy` working only while the target is independent and prevents it being cleared by level changes.
- To replace the default autonomy ladder (as unique mod autonomy systems do), disable vanilla states through `allowed` or `allowed_levels_filter`, and also disable them so they do not appear during puppeting.
- `rule = { ... }` entries are the game rules in the autonomy reference table (in the reference file). `has_rule = <rule>` tests them in a trigger, `set_rule` adds an override on a country.
- Icon sprite name: `GFX_<autonomy state id>_icon`. Localisation: the state id is the name key; country-specific names use `TAG_<id>`, and overlord-specific names use `TAG_OVERLORD_<id>` (vanilla `countries_cosmetic_l_english.yml` has `INS_HOL_autonomy_dominion`, plus `_DEF` and `INS_HOL_FLAG_...` variants). The wiki's example prefix order (`ENG_FRA_...`) is the same pattern.

### Effects and triggers

- `puppet = X`, or `puppet = { target = X end_wars = yes end_civil_wars = yes }` (both default to yes).
- `set_autonomy = { target = X autonomy_state = ID freedom_level = 0.5 end_wars = yes end_civil_wars = yes }`. The installed documentation example spells `autonomy_state`; vanilla history files and decisions also spell it `autonomous_state` and the wiki table uses that spelling. Both appear in vanilla scripts; prefer the documented `autonomy_state`. The installed documentation says `end_wars` and `end_civil_wars` default to yes; the wiki table says `end_wars` defaults to no and that omitting it strands enemy units. Pass them explicitly.
- `release_autonomy = { target autonomy_state freedom_level release_non_owned_controlled force_change_controller_for_non_ally_controlled }` creates the subject from owned (and optionally controlled) states and does nothing if the country exists.
- `release`, `release_on_controlled`, `release_puppet`, `release_puppet_on_controlled` create a free nation or a puppet from owned or controlled states; all states cored by the target move to it and the releaser loses its own core on a transferred state.
- `end_puppet = X` (overlord scope), `annex_country`, `add_autonomy_score = { value localization }`, `add_autonomy_ratio = { value localization }` (subject scope; the localisation key names the modifier line in the UI).
- Triggers: `is_subject`, `is_subject_of`, `is_puppet`, `is_puppet_of`, `has_autonomy_state`, `compare_autonomy_state > state`, `compare_autonomy_progress_ratio > 0.5`, `has_rule`, iterators `any_subject_country`, `every_subject_country`, `random_subject_country`, `all_subject_countries`.
- History setup: the wiki says autonomy effects overwrite the subject's political setup (leaders, ruling party, popularities), so run `set_autonomy` before recruiting characters and defining politics. A vanilla history file does it in the overlord's file, inside the DLC gate (`history/countries/DEN - Denmark.txt` uses `IF = { limit = { has_dlc ... } set_autonomy ... ELSE = { puppet = ICE } }`). Setting it only in the overlord's file is called a source of ideology mistakes in the wiki; do not change country load order to compensate.
- Setup details for collaboration governments and autonomy defines are in `references/syntax-reference.md`.

## Diplomatic relations

| Need | Effect | Notes |
| --- | --- | --- |
| Guarantee | `give_guarantee = X` | End with `diplomatic_relation = { country = X relation = guarantee active = no }` (the common vanilla pattern, 30+ uses). |
| Military access | `give_military_access = X` | Two calls for mutual access; end with `diplomatic_relation ... relation = military_access active = no`. |
| Non-aggression pact | `diplomatic_relation = { country = X relation = non_aggression_pact active = yes }` | Most-used relation in vanilla. |
| Docking rights, air base access | `diplomatic_relation` with `docking_rights` or `air_base_access` | Documented relation types: `non_aggression_pact`, `guarantee`, `puppet`, `military_access`, `docking_rights`, `embargo`, `air_base_access`. |
| Embargo | `send_embargo = X`; end with `break_embargo` (ROOT only) or `diplomatic_relation relation = embargo active = no` | |
| Market access | `give_market_access = X` | Mutual: both sides gain access. |
| Resource rights | `give_resource_rights = { receiver state resources }` | `receiver` and `state` accept keywords or variables. |
| Truce | `set_truce = { target = X days = N }` | |
| Opinion | `add_opinion_modifier = { target = X modifier = ID }` | Modifier defined in `common/opinion_modifiers`. |
| Targeted modifier | `add_relation_modifier = { target = X modifier = ID }` | Modifier in `common/modifiers`; trigger `has_relation_modifier`. |
| Rule override between two countries | `add_relation_rule_override = { target = X can_not_declare_war = yes }` or `trigger = named_trigger` | Documented rules include `can_send_volunteer` and `can_access_market`; positive rules combine with AND, negative with OR. |
| Equipment gift | `send_equipment`, `send_equipment_fraction` | Lend-lease contracts themselves are a player or AI diplomatic action; the trigger `is_lend_leasing` reads them. |
| Volunteers | `recall_volunteers_from`; trigger `has_volunteers_amount_from` | Sending volunteers is a diplomatic action, not an effect. |
| Attaché | `recall_attache`; triggers `has_attache`, `has_attache_from` | |
| World tension | `add_threat`, `add_named_threat = { threat name }` | `name` is a localisation key shown in the tension tooltip. |

Opinion modifier definition (`common/opinion_modifiers/*.txt`, header comment lists the keys `value`, `min_trust`, `max_trust`, `decay`, `months/years/days`, `trade`):

```
opinion_modifiers = {
	my_incident = {
		value = -25
		months = 12
		decay = 1
	}
}
```

Localise the modifier id (it is the line shown in the opinion tooltip). Triggers: `has_opinion = { target = X value > 20 }` (form used in vanilla `events/Germany.txt`), `has_opinion_modifier`.

## Wargoals, declaring war, and joining wars

### Wargoal type definition (`common/wargoals/00_invasion.txt`)

There is no documentation page for this folder; the fields below are taken from the vanilla file.

```
wargoal_types = {
	my_goal = {
		war_name = MY_WAR_NAME
		allowed = { always = no }
		available = { }
		take_states = { is_claimed_by = ROOT is_owned_by = PREV is_controlled_by = PREV }
		generate_base_cost = 125
		generate_per_state_cost = 10
		take_states_limit = 5
		take_states_cost = -50
		expire = 730
		threat = 0.15
	}
}
```

- Comments in vanilla: `PREV` is the original target country and `ROOT` the goal owner.
- Other keys seen: `puppet = { }` with `puppet_cost`, `liberate = { }`, `force_government_cost`, `take_states_threat_factor`. The comment-free `take_states = { }` with no triggers means any state.
- `allowed = { always = no }` is the idiom for types only created from script (`take_state_focus`, `puppet_wargoal_focus`, `annex_everything`, `topple_government`, `liberate_wargoal`, `independence_wargoal`, `civil_war`).
- `war_name` is a localisation key for the war's displayed name.
- Vanilla wargoal types used by script: `annex_everything` (most common), `take_state_focus`, `puppet_wargoal_focus`, `topple_government`, `take_claimed_state`, `liberate_wargoal`, `independence_wargoal`, `take_core_state`, `take_state`. The wiki's decision example uses `puppet_focus_wargoal`, which does not exist in vanilla; the real id is `puppet_wargoal_focus`.

### Effects

- `create_wargoal = { type = ID target = X generator = { state_ids } expire = days }`. `generator` supplies the states for state-taking goals and accepts an array reference (vanilla `GER.txt` focuses pass `generator = PREV.<array>`). `expire = 0` or unset never expires. The creator is the scoped country.
- `declare_war_on = { target = X type = ID generator = { ... } }`. Documented as immediate; a wargoal type that exists in `common/wargoals` is required.
- `add_to_war = { targeted_alliance = ALLY enemy = X hostility_reason = asked_to_join single_target_only = yes }` makes the scoped country join the ally's side against `enemy`.
- `remove_wargoal = { target = X type = ID|all }`, `add_civil_war_target`, `remove_civil_war_target`, `start_civil_war` (ideology, size, states, filters; see the effects documentation).
- Border war: `start_border_war`, `set_border_war`, `finalize_border_war`, `cancel_border_war` exist; read their documentation entries before use.
- Claims and cores that wargoals use: `add_state_claim`, `add_claim_by`, `add_core_of`, `add_state_core`, and their `remove_` forms.

### Triggers

`has_war`, `has_war_with`, `has_offensive_war`, `has_offensive_war_with`, `has_defensive_war`, `has_defensive_war_with`, `has_war_together_with`, `has_war_with_major`, `has_wargoal_against = X` or `{ target = X type = ID }`, `has_war_with_wargoal_against`, `is_justifying_wargoal_against`, `can_declare_war_on`, `has_truce_with`, `has_capitulated`, `surrender_progress`, `days_since_capitulated`, `has_added_tension_amount`.

### Warnings to the AI and the target

- A decision that ends in war should name the target in `war_with_on_complete`, `war_with_on_remove`, or `war_with_on_timeout` (for missions) so the AI moves troops and the target and its allies get a justification notification. `war_with_on_*` does not work when the target is `FROM` in a targeted decision; use `war_with_target_on_complete = yes`, `war_with_target_on_remove = yes`, or `war_with_target_on_timeout = yes` instead (wiki "Targeted Decisions: Warning for War").
- `NAI.WILL_LEAD_TO_WAR_DECISION_PERSISTENCE` (30 days) keeps the AI preparing after such a decision completes.
- Wargoal justification can be hooked by `on_justifying_wargoal_pulse` (FROM is the target, daily) and `on_wargoal_expire` (FROM is the owner).

## Peace

- `white_peace = X`, or `white_peace = { tag = X message = LOC_KEY }`. The scoped country is the winner for naming and on-action scopes. The effect fires `on_peaceconference_started` and `on_peaceconference_ended`.
- `start_peace_conference = { tag = LOSER score_factor = 0.0..1.0|variable winner_scope = FACTION loser_scope = FACTION message = LOC_KEY }`: a limited conference where the scoped country wins against `tag` and its subjects. `score_factor` is the fraction of conference score allocated to winners; 0 is a white peace. Scopes: `ALL`, `FACTION`, `LIMITED_FACTION` (default), `LIMITED`. Allowed only while at war with the target.
- Conference triggers: `is_in_peace_conference`, `pc_is_winner`, `pc_is_loser`, `pc_is_on_winning_side`, `pc_is_puppeted`, `pc_is_puppeted_by`, `pc_is_liberated`, `pc_is_forced_government`, `pc_is_state_claimed`, `pc_is_state_claimed_by`, `pc_is_state_claimed_and_taken_by`, `pc_current_score`, `pc_total_score`, `pc_turn`, and others in `triggers_documentation.md`. Relations and ownership are not updated until the conference finishes, so inside `enable` blocks of peace modifiers use `pc_*` checks.
- Peace cost modifiers: `common/peace_conference/cost_modifiers/*.txt` (`peace_action_modifiers`, `peace_action_type`, `enable`, `cost_multiplier` greater than 0, `category`). Faction peace rules attach them with `peace_action_modifiers`. Action types: `take_states`, `puppet`, `force_government`, `liberate`.
- Peace action scopes inside those blocks: `ROOT` negotiator, `FROM` taker, `FROM.FROM` giver, `FROM.FROM.FROM` state.
- AI desire for those actions lives in `peace_conference/ai_peace`; see `hoi4-ai-strategies`.
- Peace conference hooks: `on_before_peace_conference_start`, `on_peaceconference_started`, `on_peaceconference_ended` (ROOT winner, FROM loser, called for every winner against every loser), `on_puppet`, `on_liberate`, `on_force_government`, `on_annex`.
- To remember a pending peace outcome, set a country flag in the effect that starts the conference and consume it in `on_peaceconference_ended` (ROOT winner, FROM loser), clearing it afterwards. This is a repository pattern, not an engine feature. Because the on action fires for every winner-loser pair, make the handler idempotent.

## Territory, release, annexation, and puppets

- `transfer_state = STATE_ID` in the receiving country's scope, or `transfer_state = PREV` from a state-iterating scope while the receiver is the outer country (vanilla `instantiate_collaboration_government`). It sets owner and controller. Cores and claims are separate effects.
- `set_state_owner_to` (state scope) sets only the owner; `transfer_state_to` (state scope) sets owner and controller.
- `annex_country` with `transfer_troops = yes` keeps the annexed divisions. Fires `on_annex` with ROOT the annexer and FROM the annexed country.
- Release family: states cored by the released tag move to it; own cores on moved states are lost. States owned but not controlled go to the released country without control, which can create occupation anomalies.
- After a subject is freed or annexed, `on_subject_free` (ROOT the subject, FROM the previous overlord) and `on_subject_annexed` fire.
- Governments in exile: `become_exiled_in = { target legitimacy }`, `end_exile`, trigger `is_government_in_exile`; faction rules control whether they are allowed.

## On actions for diplomacy and war

The full list is in `GAME/common/on_actions/_documentation.md` and the scope notes in `WIKI/On actions - Hearts of Iron 4 Wiki.md`; the scope table is in `references/syntax-reference.md`.
Groups: diplomacy and war (`on_declare_war`, `on_war_relation_added`, `on_war`, `on_peace`, `on_capitulation`, `on_annex`, `on_puppet`, `on_liberate`, `on_release_as_free`, `on_release_as_puppet`), factions (`on_create_faction`, `on_faction_formed`, `on_offer_join_faction`, `on_join_faction`, `on_assume_faction_leadership`, `on_leave_faction`), autonomy (`on_subject_annexed`, `on_subject_free`, `on_subject_autonomy_level_change`), peace (`on_before_peace_conference_start`, `on_peaceconference_started`, `on_peaceconference_ended`), and wargoals (`on_justifying_wargoal_pulse`, `on_wargoal_expire`).
ROOT and FROM differ per action (for example `on_declare_war` has ROOT as the aggressor and FROM as the target, `on_capitulation` has ROOT as the loser and FROM as the winner), so read the table before using FROM.
Repository rule: `on_daily`, `on_weekly`, and `on_monthly` iterate all countries and need explicit permission; prefer these event-style on actions, which fire only on the relevant change.

## Scripted diplomatic actions

`common/scripted_diplomatic_actions/*.txt` lets a mod add a custom offer with sender and receiver scopes, optional scripted GUIs, and AI acceptance and desire blocks.
The only installed file is a commented template, so the skeleton in `references/syntax-reference.md` is unconfirmed against a working vanilla definition.

## AI hooks

- The AI uses `befriend`, `antagonize`, `ignore`, `conquer`, `alliance`, `protect`, `contain`, `support`, `declare_war`, `prepare_for_war`, `consider_weak`, and `diplo_action_*` strategies; see `hoi4-ai-strategies` and its token catalog.
- Autonomous states carry `ai_subject_wants_higher`, `ai_overlord_wants_lower`, `ai_overlord_wants_garrison`, `use_for_peace_conference_weight`. A factor of 0 makes the AI never move that way through the autonomy system.
- Faction rules and goals carry `ai_will_do`; a rule with a total of 0 or less is not used.
- Country modifiers `ai_get_ally_desire_factor`, `ai_join_ally_desire_factor`, `ai_call_ally_desire_factor`, and `ai_license_acceptance` change AI willingness without strategies.
- Testing the AI response to a diplomatic scripted change: console `ai_accept` toggles always-accept; the player runs it, agents do not launch the game.

## Localisation and tooltips

- Opinion modifier ids, autonomy state ids, faction template and rule ids, goal `name` and `description`, `war_name`, `message` keys passed to `white_peace` and `start_peace_conference`, `localization` for `add_autonomy_*`, and `add_named_threat` names all need localisation keys.
- Faction rule name is evaluated with country and faction localisation environments; goal names with faction and player country.
- A flag trigger in a player-visible block shows the flag identifier as its tooltip unless it has a localisation key or is hidden and replaced by `custom_trigger_tooltip`.
- Use `effect_tooltip` for the visible description of diplomatic effects performed in `hidden_effect`, as vanilla does for access and faction changes (`common/decisions/BEL.txt`).
- Player-facing diplomacy text describes the current situation and options, not implementation history.

## Validation

1. Confirm the scope of every effect: acting country, target, and whether the effect expects overlord or subject scope.
2. Confirm every wargoal type, autonomy state, faction template, rule, goal, opinion modifier, and relation modifier id exists (`hoi4_source_lookup`).
3. Check the guard: `country_exists`, `is_subject = no`, `has_war_with`, and `has_capitulated` as required, so the effect cannot fail silently or crash.
4. Check that every war-causing decision, mission, or event declares its target to the AI (`war_with_on_*`).
5. Check on-action scope assumptions against the wiki table.
6. Use `hoi4_script_validate` for an effect or trigger body under its explicit scope. A true result covers only the listed checks; parameter semantics and engine behaviour remain separate evidence.
7. Source review and tools do not prove live behaviour. The user performs in-game validation; do not launch the game.

## Repository conventions

These follow the project rules in `CLAUDE.md`, which remain the authority.

- Tabs, lowercase snake_case, no `<=` or `>=`, no magic numbers (use `common/script_constants` via `constant:category.key` where the field parses it, else variables or `@` constants).
- Reuse the project's dynamic scripted effects library (`common/scripted_effects/<prefix>_dynamic_effects.txt`, named in `CLAUDE.md`) and document any new dynamic effect in its documentation file as `CLAUDE.md` requires.
- Never use `on_daily`, `on_weekly`, or `on_monthly` world-iterating hooks without explicit permission; prefer the event-style on actions above or `on_daily_TAG` for a named country.
- Do not write markers about update history in localisation or player text.
- Keep event-, route-, or country-specific content out of reusable skill files.

## Common mistakes

1. Running `set_autonomy` in the subject's scope; it needs the overlord's scope.
2. Assuming `puppet` always creates `autonomy_puppet`; it picks a `default = yes` state allowed for that overlord, and crashes when none exists (wiki).
3. Using `release_*` on a country that already exists (no effect) or expecting it to move states the releaser does not own.
4. Reversing `add_opinion_modifier` and `reverse_add_opinion_modifier`, or forgetting the reversal for `trade = yes` modifiers.
5. Calling `add_to_faction` from the joiner's scope; the scoped country must be in (or lead) the destination faction.
6. Using `break_embargo` for a third country; it only applies to ROOT.
7. Using singular faction rule type names from the documentation comment instead of vanilla's plural names.
8. Defining a faction rule that belongs to no rule group, so it never appears (rules need at least one group).
9. Declaring war from a decision or event without `war_with_on_*` so the AI never prepares.
10. Using a nonexistent wargoal id (for example the wiki's `puppet_focus_wargoal`); verify ids in `common/wargoals`.
11. Using `declare_war_on` when `add_to_war` is meant (joining an ally's war), or the reverse.
12. Expecting `white_peace` to end a faction-wide war: it pairs two countries.
13. Reading `FROM` in faction goal effect blocks; it is unsupported there.
14. Targeting a non-existent or capitulated country without a guard.
15. Using `transfer_state` in the giver's scope; the argument is the state, scope is the receiver.
16. Setting autonomy in history after political setup, or only in the overlord file, and getting wrong ideology.
17. Leaving two autonomous states with the same `min_freedom_level`.
18. Writing unlocalised opinion modifiers, rules, goals, or `war_name` keys.

## Unverified or conflicting points

- No installed documentation covers `common/autonomous_states` or `common/wargoals`; their field lists come from the wiki and vanilla files.
- `end_wars` default for `set_autonomy`: installed effects documentation says yes, wiki says no. Pass explicitly.
- `autonomy_state` versus `autonomous_state` spelling: both occur in vanilla scripts; only `autonomy_state` is in the installed documentation example.
- Faction rule `type` spelling: vanilla plural versus documentation singular.
- `common/scripted_diplomatic_actions` ships only as a commented template; the skeleton is unconfirmed against a live vanilla action.
- `diplomatic_relation relation = puppet` exists in vanilla (2 uses); prefer `puppet` and `end_puppet`, whose semantics are documented.
