# HOI4 Diplomacy and War: Wargoals, war and peace

Part of the [hoi4-diplomacy-war](../SKILL.md) skill. Read before defining wargoal types, declaring or joining wars, warning the AI, or scripting white peace and peace conferences.

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
- `pc_is_untouched_loser` and `pc_is_liberated_by`, which the wiki lists, do not exist in 1.19.3. [docs]
- Peace cost modifiers: `common/peace_conference/cost_modifiers/*.txt` (`peace_action_modifiers`, `peace_action_type`, `enable`, `cost_multiplier` greater than 0, `category`). Faction peace rules attach them with `peace_action_modifiers`. Action types: `take_states`, `puppet`, `force_government`, `liberate`.
- Peace action scopes inside those blocks: `ROOT` negotiator, `FROM` taker, `FROM.FROM` giver, `FROM.FROM.FROM` state.
- Inside a nested scope such as `ROOT = { }` in a peace block, `FROM` no longer means the taker, so write `ROOT.FROM`. [docs] `cost_modifiers/_documentation.md`
- The peace action type is `take_states`. Vanilla 1.19.3 spelled it `take_state` in two entries (`cost_modifiers/00_generic_peace.txt`, `ai_peace/00_misc.txt`), a typo not to copy, and 1.19.4.1 no longer does. [vanilla-confirmed 1.19.4.1]
- Vanilla repeats entry names inside a single peace file (`DEN_take_former_overlords_state`, `unlikely_countries`, `ETH_agreed_expansion`, `SOV_wants_memel`), so give every entry a unique name. [vanilla-confirmed 1.19.4.1]
- Exactly one peace action category may carry `default = yes`. [vanilla-confirmed 1.19.3] comment in the category file
- AI desire for those actions lives in `peace_conference/ai_peace`; see `hoi4-ai-strategies`.
- Peace conference hooks: `on_before_peace_conference_start`, `on_peaceconference_started`, `on_peaceconference_ended` (ROOT winner, FROM loser, called for every winner against every loser), `on_puppet`, `on_liberate`, `on_force_government`, `on_annex`.
- To remember a pending peace outcome, set a country flag in the effect that starts the conference and consume it in `on_peaceconference_ended` (ROOT winner, FROM loser), clearing it afterwards. This is a repository pattern, not an engine feature. Because the on action fires for every winner-loser pair, make the handler idempotent.

