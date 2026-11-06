# HOI4 Diplomacy and War: Relations, hooks and localisation

Part of the [hoi4-diplomacy-war](../SKILL.md) skill. Read before scripting guarantees, access, embargoes or opinion modifiers, writing on-action handlers or scripted diplomatic actions, or adding AI hooks and diplomacy localisation.

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

17 opinion modifier ids are defined twice in vanilla (811 entries, 794 ids), so give every new id a unique name. [vanilla-confirmed 1.19.4.1]

## On actions for diplomacy and war

The full list is in `GAME/common/on_actions/_documentation.md` and the scope notes in `WIKI/on_actions.md`; the scope table is in `references/syntax-reference.md`.
Groups: diplomacy and war (`on_declare_war`, `on_war_relation_added`, `on_war`, `on_peace`, `on_capitulation`, `on_annex`, `on_puppet`, `on_liberate`, `on_release_as_free`, `on_release_as_puppet`), factions (`on_create_faction`, `on_faction_formed`, `on_offer_join_faction`, `on_join_faction`, `on_assume_faction_leadership`, `on_leave_faction`), autonomy (`on_subject_annexed`, `on_subject_free`, `on_subject_autonomy_level_change`), peace (`on_before_peace_conference_start`, `on_peaceconference_started`, `on_peaceconference_ended`), and wargoals (`on_justifying_wargoal_pulse`, `on_wargoal_expire`).
ROOT and FROM differ per action (for example `on_declare_war` has ROOT as the aggressor and FROM as the target, `on_capitulation` has ROOT as the loser and FROM as the winner), so read the table before using FROM.
`on_join_faction` does not fire when `add_to_faction` adds the member, and vanilla comments in 8 files point to `on_offer_join_faction` for that case. [vanilla-confirmed 1.19.4.1]
A misspelled hook name fails silently: vanilla ships `on_subject_annex` in its `16_taog` file where the engine hook is `on_subject_annexed`, so that handler never runs. [docs] [vanilla-confirmed 1.19.4.1]
14 hooks listed on the wiki, among them `on_guarantee`, `on_military_access` and `on_generate_wargoal`, appear in neither the documentation nor vanilla script, so treat them as unverified. [docs]
Repository rule: `on_daily`, `on_weekly`, and `on_monthly` iterate all countries and need explicit permission; prefer these event-style on actions, which fire only on the relevant change.

## Scripted diplomatic actions

`common/scripted_diplomatic_actions/*.txt` lets a mod add a custom offer with sender and receiver scopes, optional scripted GUIs, and AI acceptance and desire blocks.
The only installed file is a commented template, so the skeleton in `references/syntax-reference.md` is unconfirmed against a working vanilla definition.
The trigger `is_diplomatic_action_valid_<token>` has the target as its scope and `FROM` as the initiator, the reverse of the `DIPLOMACY_*_ENABLE_TRIGGER` direction. [vanilla-confirmed 1.19.4.1]

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

