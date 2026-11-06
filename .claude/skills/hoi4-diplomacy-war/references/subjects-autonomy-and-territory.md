# HOI4 Diplomacy and War: Subjects, autonomy and territory

Part of the [hoi4-diplomacy-war](../SKILL.md) skill. Read before scripting puppets, autonomous states, release, annexation or state transfer between countries.

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
- `is_puppet = yes` makes `is_puppet` and `is_puppet_of` true. A subject state without `is_puppet = yes` (for example `autonomy_dominion`) is still a subject for `is_subject` and `is_subject_of`.
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
- `has_autonomy_state` and `compare_autonomy_state` take the full id such as `autonomy_puppet`, although documentation examples drop the prefix. [vanilla-confirmed 1.19.4.1]
- History setup: the wiki says autonomy effects overwrite the subject's political setup (leaders, ruling party, popularities), so run `set_autonomy` before recruiting characters and defining politics. A vanilla history file does it in the overlord's file, inside the DLC gate (`history/countries/DEN - Denmark.txt` uses `IF = { limit = { has_dlc ... } set_autonomy ... ELSE = { puppet = ICE } }`). Setting it only in the overlord's file is called a source of ideology mistakes in the wiki; do not change country load order to compensate.
- Setup details for collaboration governments and autonomy defines are in `references/syntax-reference.md`.

## Territory, release, annexation, and puppets

- `transfer_state = STATE_ID` in the receiving country's scope, or `transfer_state = PREV` from a state-iterating scope while the receiver is the outer country (vanilla `instantiate_collaboration_government`). It sets owner and controller. Cores and claims are separate effects.
- `set_state_owner_to` (state scope) sets only the owner; `transfer_state_to` (state scope) sets owner and controller.
- `set_state_owner` and `set_state_controller` are country-scope effects that take a state, while `set_state_owner_to` and `set_state_controller_to` are state-scope effects that take a tag. [docs]
- Vanilla never uses `set_state_owner` and uses `transfer_state` 2,279 times. [vanilla-confirmed 1.19.4.1]
- `annex_country` with `transfer_troops = yes` keeps the annexed divisions. Fires `on_annex` with ROOT the annexer and FROM the annexed country.
- Release family: states cored by the released tag move to it; own cores on moved states are lost. States owned but not controlled go to the released country without control, which can create occupation anomalies.
- After a subject is freed or annexed, `on_subject_free` (ROOT the subject, FROM the previous overlord) and `on_subject_annexed` fire.
- Governments in exile: `become_exiled_in = { target legitimacy }`, `end_exile`, trigger `is_government_in_exile`; faction rules control whether they are allowed.
- All 439 vanilla country tags have exactly three characters, so keep a new tag to three and check it against `common/country_tags` first, since `SCO`, `BRN`, `CHI`, `HUN` and `SHX` are already taken. [vanilla-confirmed 1.19.3]

