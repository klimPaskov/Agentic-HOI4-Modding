# On actions

*Offline snapshot of the Hearts of Iron IV Wiki page "On actions", captured 2026-09-19.*

## Table of contents

- [File example](#File_example)
- [General on actions](#General_on_actions)
- [Politics](#Politics)
- [Diplomacy/War](#Diplomacy.2FWar)
- [Faction](#Faction)
- [Autonomy](#Autonomy)
- [Governments in Exile](#Governments_in_Exile)
- [States](#States)
- [Wargoals](#Wargoals)
- [Unit Leader](#Unit_Leader)
- [Military](#Military)
- [Aces](#Aces)
- [La Résistance](#La_R.C3.A9sistance)
- [Military Industrial Organization](#Military_Industrial_Organization)
- [Special Projects](#Special_Projects)

---

On actions are blocks that are executed when a certain action occurs, such as a country declaring war on a different country or a state changing control. On actions are stored in `/Hearts of Iron IV/common/on_actions/*.txt` files.

Each on action is a separate block within the `on_actions = { ... }` block, which is the root block of the on actions file. Each on_action has up to 2 arguments:

- `effect = { ... }` is present for every single on action, being an effect block the insides of which are executed when needed.
- `random_events = { ... }` is present for on_actions where the default scope (Same as ROOT, if not specified otherwise) is a country, such as on_new_term_election. This instantly fires a random one of the specified events within with the given weights being applied. This is done with a probability-proportional-to-size sampling approach.

Putting `0` instead of an event ID will ensure that nothing will happen if the chance lands on this.
Additionally, an event cannot be fired using `random_events = { ... }` if the event's `trigger = { ... }` block evaluates as false. In this case, each scope is treated the same as on action's: on action's FROM is treated as the event's FROM, same with FROM.FROM.
If there are multiple random_events blocks, one event will be picked from each.

Note that in terms of [Scopes](<Scopes - Hearts of Iron 4 Wiki.md>), ROOT is the default assumed scope unless specified otherwise (in on_actions that have THIS as a separate entity from ROOT), while FROM and FROM.FROM can serve as secondary blocks that are provided in addition.

Each on action can only be executed after the game's start, ignoring any effects done within history files or the bookmark's `effects = { ... }` section that normally would trigger one, such as [set_politics](<Effects - Hearts of Iron 4 Wiki.md>).

## File example <a id="File_example"></a>

```text
on_actions = {
    on_startup = {
        effect = { # NEVER FORGET! Important to include this line to distinguish it from random_events = { ... }
            every_country = {
                limit = {
                    is_ai = no
                }
                country_event = welcome_event.1
            }
            ENG = {
                country_event = {
                    id = new_year.1
                    days = 365  # Fires on January 1 1937. Remember that leap days do not exist in-game.
                }
            }
        }
    }
    on_state_control_changed = {
        random_events = {
            1 = germany_state_control.1 # Assuming the triggers for the events are met, then
            1 = germany_state_control.2 # fires one of germany_state_control.1 or germany_state_control.2
            3 = 0                       # Each has a 20% chance, and there's 60% chance nothing happens.
        }
        effect = {
            if = {
                limit = {   # Execute if Italy captures Corsica or Savoy from France
                    tag = ITA
                    FROM = { tag = FRA }
                    FROM.FROM = {
                        OR = {
                            state = 1
                            state = 735
                        }
                    }
                }
                FROM.FROM = {
                    set_resistance = 60
                    damage_building = {
                        type = infrastructure
                        damage = 2
                    }
                }
            }
        }
    }
}
```

## General on actions <a id="General_on_actions"></a>

| Name | Description | Examples | Notes | Version Added |
| --- | --- | --- | --- | --- |
| on_startup | Trigger the following commands at the first day of a new game, after country selection. Doesn't work with save loading. | `on_startup = {`<br>`    effect = {`<br>`        ENG = {`<br>`            news_event = { id = news_event.1 days = 31 random_days = 27 } # Fires a news event in February 1936`<br>`        }  # assuming the default start date`<br>`    }      # Scoping into ENG is necessary, since`<br>`}          # news_event is a country-scoped effect` | **Has a default scope of `none`**, instead of firing for each country individually as in other Paradox games such as Europa Universalis IV. Many effects that usually can be used in any scope will not work, without manual [scoping](<Scopes - Hearts of Iron 4 Wiki.md>) into countries, states, or elsewhere. | 1.3.3 |
| on_daily | Triggers each day for **every country separately** (performance heavy, use carefully) | `on_daily = {`<br>`    effect = {`<br>`        if = {`<br>`            limit = { has_variable = to_be_updated_daily }`<br>`            add_to_variable = { to_be_updated_daily = 1 }`<br>`        }`<br>`    }`<br>`}` | Useful for scripted guis and mods adding new mechanics (can increment a variable daily e.g.). **Only use scoping if you're careful to avoid duplicate effects**. This being executed for every country separately means that this is essentially equivalent to a single effect executed daily inside of every_country. e.g. `effect = { GER = { add_political_power = 1 } }` will add ~100 political power to ![Flag of Germany](media/effect-hearts-of-iron-4-wiki_ec2e2a02fa__img1.png) Germany daily, as there being ~100 countries on the world map means that this will get executed ~100 times per day. | 1.5.2 |
| on_daily_TAG | Triggers each day for the specified country only | `on_daily_SOV = {`<br>`    effect = {`<br>`        if = {`<br>`            limit = { has_war_with = GER }`<br>`            SOV_escalate_the_war_effect = yes`<br>`        }`<br>`    }`<br>`}` | Only runs the effects if the country exists. | 1.9 |
| on_weekly | Triggers each week for every country separately | `on_weekly = {`<br>`    effect = {`<br>`        if = {`<br>`            limit = {`<br>`                has_intelligence_agency = yes`<br>`                is_ai = yes`<br>`            }`<br>`            update_operation_ai = yes`<br>`        }`<br>`    }`<br>`}` | Useful for ai scripting. Runs on the beginning of the day if the num_days variable is divisible by 7. | 1.9 |
| on_weekly_TAG | Triggers each week for the specified country only | `on_weekly_BHR = {`<br>`    if = {`<br>`        limit = {`<br>`            has_country_flag = BHR_must_control_states`<br>`            any_owned_state = {`<br>`                NOT = { is_controlled_by = ROOT }`<br>`            }`<br>`            has_stability < 0.5`<br>`        }`<br>`        country_event = BHR_event.0`<br>`        clr_country_flag = BHR_must_control_states`<br>`    }`<br>`}` | Only runs the effects if the country exists. Runs on the beginning of the day if the num_days variable is divisible by 7. | 1.9 |
| on_monthly | Triggers each month for every country separately | `on_monthly = {`<br>`    random_events = {`<br>`        1 = random_event.0`<br>`        99 = 0`<br>`    }`<br>`}` |  | 1.9 |
| on_monthly_TAG | Triggers each month for the specified country only | `on_monthly_USA = {`<br>`    effect = {`<br>`        add_to_variable = { USA_unrest = 1 }`<br>`        clamp_variable = {`<br>`            var = USA_unrest`<br>`            max = 10`<br>`        }`<br>`        if = {`<br>`            limit = {`<br>`                check_variable = { USA_unrest = 10 }`<br>`            }`<br>`            country_event = usa.rebellion.0`<br>`        }`<br>`    }`<br>`}` | Only runs the effects if the country exists. | 1.9 |

## Politics <a id="Politics"></a>

| Name | Description | Examples | Notes | Version Added |
| --- | --- | --- | --- | --- |
| on_stage_coup | For the non ![La Résistance](media/ai-modding-hearts-of-iron-4-wiki_04cfcba22e__img6.png)La Résistance stage coup. Trigger the following commands whenever a coup is stage. | `on_stage_coup = {`<br>`    effect = {`<br>`    }`<br>`}` | ROOT is the country that stages the coup, FROM is the target country. | 1.0 |
| on_coup_succeeded | For the non ![La Résistance](media/ai-modding-hearts-of-iron-4-wiki_04cfcba22e__img6.png)La Résistance stage coup. Trigger the following commands whenever a coup succeeds. | `on_coup_succeeded = {`<br>`    effect = {`<br>`        random_other_country = {`<br>`            limit = {`<br>`                has_government = democratic`<br>`                original_tag = ROOT`<br>`            }`<br>`            set_politics = { elections_allowed = yes }`<br>`        }`<br>`    }`<br>`}` | ROOT is the country that coup succeeded in, FROM is the stager of the coup | 1.0 |
| on_government_change | Trigger the following commands whenever a country switches its government. | `on_government_change = { effect = {  …  } }` | This includes `set_politics` and `start_civil_war` (always for both sides) and excludes being puppeted. Will always also trigger on_ruling_party_change. | 1.0 |
| on_ruling_party_change | Trigger the following commands whenever a country switches its ideology. | `on_ruling_party_change = { effect = {  …  } }` | `old_ideology_token` is a [temporary variable](<Data structures - Hearts of Iron 4 Wiki.md#Variable_types>) that stores the old ideology as a token. Alongside what triggers on_government_change, also includes being puppeted or changing the ideology via a console command. | 1.9 |
| on_new_term_election | Trigger the following commands whenever an election happens or is called by the **hold_election** command. | `on_new_term_election = { random_events = { 100 = usa.6 } }` |  | 1.0 |
| on_before_peace_conference_start | Trigger the following commands after capitulation but before a peace conference starts. | `on_before_peace_conference_start = { effect = { … } }` | ROOT is winner, FROM is loser (called for all winners against all losers). | 1.15.2 |
| on_peaceconference_ended | Trigger the following commands whenever a peace conference ends. | `on_peaceconference_ended = { effect = { … } }` | ROOT is the winner, FROM is the loser. Is also triggered by the [white_peace](<Effects - Hearts of Iron 4 Wiki.md>) effect is used or when a conditional surrender is accepted. | 1.5 |
| on_peaceconference_started | Trigger the following commands whenever a peace conference starts. | `on_peaceconference_started = { effect = { … } }` | ROOT is the winner, FROM is the loser. Is also triggered by the [white_peace](<Effects - Hearts of Iron 4 Wiki.md>) effect is used or when a conditional surrender is accepted. | 1.12.3 |

## Diplomacy/War <a id="Diplomacy.2FWar"></a><a id="Diplomacy/War"></a>

| Name | Description | Examples | Notes | Version Added |
| --- | --- | --- | --- | --- |
| on_send_volunteers | Trigger the following commands whenever a country send volunteers to another. | `on_send_volunteers = {`<br>`    effect = { … }`<br>`}` | ROOT is sender, FROM is receiver. | 1.9 |
| on_border_war_lost | Trigger the following commands whenever a country loses a border war. | `on_border_war_lost = {`<br>`    effect = {`<br>`        owner = {`<br>`            add_ideas = lost_conflict`<br>`        }`<br>`    }`<br>`}` | "Border war" refers to the state-based border wars enabled with [set_border_war](<Effects - Hearts of Iron 4 Wiki.md>), represented with orange stripes over the state, rather than border wars that simulate combat between countries. The default scope is the state that lost the border war. | 1.0 |
| on_war_relation_added | fired when two countries end up at war with each other (on_war is fired when a country goes to war against anyone and is not fired again when it enters war against another country unless it went to peace first) | `on_war_relation_added = {`<br>`    effect = { … }`<br>`}` | ROOT is attacker, FROM is defender | 1.9.3 |
| on_declare_war | Trigger the following commands whenever a country declares war. | `on_declare_war = {`<br>`    effect = {`<br>`        if = {`<br>`            limit = {`<br>`                tag = GER`<br>`                FROM = { tag = SOV }`<br>`            }`<br>`            add_ideas = GER_barbarossa`<br>`        }`<br>`    }`<br>`}` | FROM is war target. ROOT is for the country who is declaring war | 1.0 |
| on_war | Trigger the following commands whenever a country has just entered a state of war from initially being at peace. | `on_war = {`<br>`    effect = { … }`<br>`}` | THIS is country that has just gotten into a war. | 1.7 |
| on_peace | Trigger the following commands whenever a country is no longer at war. | `on_peace = {`<br>`    effect = { … }`<br>`}` | THIS is country that is no longer at war. | 1.7 |
| on_capitulation | Trigger the following commands whenever a country capitulates, in the middle of the process. | `on_capitulation = {`<br>`    effect = { … }`<br>`}` | ROOT is capitulated country, FROM is winner. Several processes such as the deletion of units and transfer of equipment have already been executed by this point. | 1.0 |
| on_capitulation_immediate | Trigger the following commands whenever a country capitulates, at the beginning of the process. | `on_capitulation_immediate = {`<br>`    effect = { … }`<br>`}` | ROOT is capitulated country, FROM is winner. | 1.11.5 |
| on_uncapitulation | Trigger the following commands whenever a country that was previously capitulated changes its status to no longer having capitulated. | `on_uncapitulation = {`<br>`    effect = { … }`<br>`}` | ROOT is the country affected. | 1.4 |
| on_annex | Trigger the following commands whenever a country is annexed. | `on_annex = {`<br>`    effect = { … }`<br>`}` | ROOT is winner, FROM gets annexed. For civil wars **on_civil_war_end** is also fired. | 1.3.3 |
| on_civil_war_end_before_annexation | Trigger the following commands just before FROM gets annexed, meaning the country and everything it owns still exists. | `on_civil_war_end_before_annexation = {`<br>`    effect = { … }`<br>`}` | ROOT is winner, FROM gets annexed. It will also fire **on_annex** and **on_civil_war_end**. | 1.6 |
| on_civil_war_end | Trigger the following commands whenever a civil war ends. | `on_civil_war_end = {`<br>`    effect = { … }`<br>`}` | ROOT is civil war winner, FROM gets annexed. This will also fire **on_annex**. | 1.0 |
| on_puppet | Trigger the following commands whenever a country is puppeted in a **peace conference only**. | `on_puppet = {`<br>`    effect = { … }`<br>`}` | ROOT is the nation being puppeted, FROM is the overlord. | 1.0 |
| on_liberate | Trigger the following commands whenever a country is liberated in a **peace conference only**. | `on_liberate = {`<br>`    effect = { … }`<br>`}` | ROOT is the nation being liberated, FROM is the leader of the liberators. | 1.0 |
| on_release_as_free | Trigger the following commands whenever a country is released. | `on_release_as_free = {`<br>`    effect = { … }`<br>`}` | #ROOT is free nation FROM is releaser. | 1.3 |
| on_release_as_puppet | Trigger the following commands whenever puppeting through the occupied territories menu during peace time (or when releasing from non-core but owned territory). | `on_release_as_puppet = {`<br>`    effect = { … }`<br>`}` | ROOT is the nation being released, FROM is the overlord. | 1.3 |
| on_guarantee | Trigger the following commands whenever a country guarantees independence of another country. |  | ROOT is the country which guarantees, FROM is the country that is guaranteed. |  |
| on_military_access | Trigger the following commands whenever a country accepts the request for military access. |  | ROOT is the country which requested, FROM is the country that accepted. |  |
| on_offer_military_access | Trigger the following commands whenever a country accepts the offer for military access. |  | ROOT is the country which offered, FROM is the country that accepted. |  |
| on_call_allies | Trigger the following commands whenever a country accepts the call to war. |  | ROOT is the country which called, FROM is the country that joined. |  |
| on_join_allies | Trigger the following commands whenever a country joins a war of an ally. |  | ROOT is the country which joined, FROM is the country whose war was joined. |  |
| on_lend_lease | Trigger the following commands whenever a country has their lend lease accepted. |  | ROOT is the country that sent the lend lease, FROM is the country that accepted. |  |
| on_incoming_lend_lease | Trigger the following commands whenever a country accepts a requested lend lease. |  | ROOT is the country that accepted, FROM is the country that requested. |  |
| on_send_expeditionary_force | Trigger the following commands whenever a country accepts sent expeditionary forces. |  | ROOT is the country that sent, FROM is the country that accepted. |  |
| on_return_expeditionary_forces | Trigger the following commands whenever a country returns their expeditionary forces. |  | ROOT is the owner of the forces, FROM is the country where the forces were sent. |  |
| on_request_expeditionary_forces | Trigger the following commands whenever a country requests expeditionary forces. |  | ROOT is the country that requests, FROM is the target of the request. |  |
| on_ask_for_state_control | Trigger the following commands whenever a country accepts the request for control of a state. |  | ROOT is the requester, FROM is the country in control of the state. |  |
| on_give_state_control | Trigger the following commands whenever a country accepts being given control of a state. |  | ROOT is the giver, FROM is the receiver. |  |
| on_peace_proposal | Trigger the following commands whenever a country accepts a conditional surrender. |  | ROOT is sender of conditional surrender, FROM is the receiver. |  |
| on_send_attache | Triggers actions on an attache being accepted. |  | Default scope is sender, FROM = receiver |  |

## Faction <a id="Faction"></a>

| Name | Description | Examples | Notes | Version Added |
| --- | --- | --- | --- | --- |
| on_create_faction | Trigger the following commands whenever a country create a faction. | `on_create_faction = { effect = { … } }` | FROM is the one that joins the faction. | 1.0 |
| on_faction_formed | Trigger the following commands when a faction is formed. | `on_faction_formed = { effect = { news_event = { id = news.159 } } }` |  | 1.0 |
| on_offer_join_faction | Trigger the following commands whenever a country joins a faction after being invited. | `on_offer_join_faction = { effect = { … } }` | FROM is the country invited, THIS and ROOT are the faction leader. | 1.0 |
| on_join_faction | Trigger the following commands for a faction leader whenever a country joins after they ask to do so. | `on_join_faction = { effect = { … } }` | FROM is faction leader, ROOT and THIS are the country that joins. | 1.0 |
| on_assume_faction_leadership | Trigger the following commands whenever a country assumes leadership of a faction. | `on_assume_faction_leadership = { effect = { … } }` | ROOT is the new faction leader FROM is the old faction leader | 1.7 |
| on_leave_faction | Trigger the following commands whenever a country leave a faction. | `on_leave_faction = { effect = { if = { limit = { AND = { tag = CAN NOT = { has_dlc = "Together for Victory" } } } drop_cosmetic_tag = yes } }` | FROM is the faction Leader, ROOT is the country leaving the faction | 1.0 |

## Autonomy <a id="Autonomy"></a>

| Name | Description | Examples | Notes | Version Added |
| --- | --- | --- | --- | --- |
| on_subject_annexed | Trigger the following commands when a country annex a subject. | `on_subject_annexed = { effect = {  …  } }` | ROOT is the subject, FROM is the overlord. | 1.0 |
| on_subject_free | Trigger the following commands when a country grants freedom to a puppet. | `on_subject_free = { effect = {  …  } }` | ROOT is the subject, FROM is the previous overlord. | 1.0 |
| on_subject_autonomy_level_change | Trigger the following commands when the autonomy level of a puppet changes. | `on_subject_autonomy_level_change = { effect = {  …  } }` | ROOT is the subject, FROM is the overlord. | 1.0 |

## Governments in Exile <a id="Governments_in_Exile"></a>

| Name | Description | Examples | Notes | Version Added |
| --- | --- | --- | --- | --- |
| on_government_exiled | Trigger the following commands whenever a country becomes a government in exile. | `on_government_exiled = { effect = { = { … } }` | ROOT is the government in exile, FROM is the country that is hosting the government in exile. | 1.6 |
| on_host_changed_from_capitulation | Trigger the following commands whenever a country that is hosting a government in exile has capitulated. | `on_host_changed_from_capitulation= { effect = { = { … } }` | ROOT is the government in exile, FROM is the new country hosting the government in exile, FROM:FROM is the old country that was hosting the government in exile. | 1.6 |
| on_exile_government_reinstated | Trigger the following commands whenever a country has returned from governing in exile. | `on_exile_government_reinstated = { effect = { = { … } }` | ROOT is the government in exile, FROM is the country that was hosting the government in exile. | 1.6 |

## States <a id="States"></a>

| Name | Description | Examples | Notes | Version Added |
| --- | --- | --- | --- | --- |
| on_state_control_changed | Trigger the following commands when a state's controller changes. | `on_state_control_changed = {`<br>`    effect = {`<br>`        if = {`<br>`            limit = {`<br>`                FROM.FROM = { state = 123 }`<br>`            }`<br>`            if =  {`<br>`                limit = {`<br>`                    tag = BHR`<br>`                }`<br>`                FROM.FROM = {`<br>`                    set_state_name = STATE_123_BHR`<br>`                    set_province_name = {`<br>`                        id = 1234`<br>`                        name = VICTORY_POINTS_1234_BHR`<br>`                    }`<br>`                }`<br>`            }`<br>`            else = { # Unnested else is preferred over nested`<br>`                FROM.FROM = {`<br>`                    reset_state_name = yes`<br>`                    reset_province_name = 1234`<br>`                }`<br>`            }`<br>`        }`<br>`    }`<br>`}` | ROOT is new controller, FROM is old controller, FROM.FROM is state ID. | 1.4 |

## Wargoals <a id="Wargoals"></a>

| Name | Description | Examples | Notes | Version Added |
| --- | --- | --- | --- | --- |
| on_generate_wargoal | Trigger the following commands whenever the country generates a wargoal. | `on_generate_wargoal = {  }` | ROOT is the wargoal owner, FROM is the wargoal target |  |
| on_justifying_wargoal_pulse | Trigger the following commands whenever the country is targeted by a wargoal under justification. | `on_justifying_wargoal_pulse = { random_events = { 100 = war_justification.1 } }` | FROM = target nation. Checked every day. | 1.0 |
| on_wargoal_expire | Trigger the following commands whenever a wargoal expire. | `on_wargoal_expire = { random_events = { 100 = war_justification.301 } }` | FROM is the wargoal owner. | 1.0 |

## Unit Leader <a id="Unit_Leader"></a>

| Name | Description | Examples | Notes | Version Added |
| --- | --- | --- | --- | --- |
| on_unit_leader_created | Trigger the following commands when an army leader is created. | `on_unit_leader_created = { effect = { … } }` | FROM is owner country, ROOT is the unit leader. | 1.5 |
| on_army_leader_daily | Trigger the following commands on an army leader each day. | `on_army_leader_daily = { effect = { … } }` | FROM is owner country, ROOT is the unit leader. | 1.0 |
| on_army_leader_won_combat | Trigger the following commands whenever an army leader won a combat. | `on_army_leader_won_combat = { effect = { … } }` | FROM is owner country, ROOT is the unit leader. | 1.0 |
| on_army_leader_lost_combat | Trigger the following commands whenever an army leader lost a combat. | `on_army_leader_lost_combat = { effect = { … } }` | FROM is owner country, ROOT is the unit leader. | 1.0 |
| on_unit_leader_level_up | Trigger the following commands when a leader gain a level. | `on_unit_leader_level_up = { effect = { … } }` | FROM is owner country, ROOT is the unit leader. | 1.0 |
| on_army_leader_promoted | Trigger the following commands whenever a corps commander is promoted to a field marshal. | `on_army_leader_promoted = { effect = { add_timed_unit_leader_trait = { trait = recently_promoted days = 100 } } }` | FROM is owner country, ROOT is the unit leader. | 1.0 |
| on_unit_leader_promote_from_ranks_veteran | Triggers the following commands whenever an unit commander gets promoted to a general. | `on_unit_leader_promote_from_ranks_veteran = { effect = { … } }` | FROM is unit, OWNER is owner country, ROOT is the unit leader. | 1.12 |
| on_unit_leader_promote_from_ranks_green | Triggers the following commands whenever an unit commander gets promoted to a general. | `on_unit_leader_promote_from_ranks_green = { effect = { … } }` | FROM is unit, OWNER is owner country, ROOT is the unit leader. | 1.12 |

## Military <a id="Military"></a>

| Name | Description | Examples | Notes | Version Added |
| --- | --- | --- | --- | --- |
| on_nuke_drop | Trigger the following commands whenever a country drops a nuke. | `on_nuke_drop = {`<br>`    effect = {`<br>`        set_global_flag = first_nuke_dropped`<br>`    }`<br>`}` | ROOT is the country that launched the nuke, FROM is the nuked state. | 1.0 |
| on_pride_of_the_fleet_sunk | Triggers when a country's pride of the fleet is sunk | `on_pride_of_the_fleet_sunk = {`<br>`    effect = {`<br>`        if = {`<br>`            limit = {`<br>`                tag = ENG`<br>`            }`<br>`            FROM = { set_country_flag = achievements_pride_and_extreme_prejudice }`<br>`        }`<br>`    }`<br>`}` | FROM is the killer country, ROOT is the country of that lost its pride of the fleet. | 1.6 |
| on_naval_invasion | Triggers the following commands whenever a sea invasion is made. | `on_naval_invasion = {`<br>`    effect = {`<br>`        ROOT = {    # Unlike most on_actions, ROOT isn't the default scope`<br>`            add_political_power = 100`<br>`        }`<br>`    }`<br>`}` | THIS (default scope) is the invaded state, ROOT is the country that invades, FROM is the state where the invasion started | 1.9 |
| on_paradrop | Triggers the following commands whenever a landing occurs. | `on_paradrop = {`<br>`    effect = {`<br>`        FROM = {`<br>`            controller = {`<br>`                add_war_support = 0.01`<br>`            }`<br>`        }`<br>`    }`<br>`}` | THIS (default scope) is the invaded state, ROOT is the country that invades, FROM is the state where the invasion started | 1.9 |
| on_units_paradropped_in_state | This differs from on_paradrop in that it is run once per paradrop, not once per unit dropped. | `on_paradrop = {`<br>`    effect = {`<br>`        FROM = {`<br>`            controller = {`<br>`                add_war_support = 0.01`<br>`            }`<br>`        }`<br>`    }`<br>`}` | ROOT is the state that was dropped into, FROM is the dropping country. |  |
| on_add_history | Triggers the following commands whenever receiving a history entry. | `on_add_history = { effect = { … } }` | ROOT is the unit. | 1.12 |

## Aces <a id="Aces"></a>

| Name | Description | Examples | Notes | Version Added |
| --- | --- | --- | --- | --- |
| on_ace_promoted | Trigger the following commands whenever an ace is created. | `on_ace_promoted = { random_events = { 100 = ace_promoted.1 } }` | FROM = ace. | 1.0 |
| on_ace_killed | Trigger the following commands whenever an aces is killed. | `on_ace_killed = { random_events = { 100 = ace_died.1 } }` | FROM = ace. | 1.0 |
| on_ace_killed_on_accident | Trigger the following commands whenever our aces died on accident. | `on_ace_killed_on_accident = { random_events = { 100 = ace_died.1 } }` | FROM = our ace died in accident. | 1.9 |
| on_non_ace_killed_other_ace | Trigger the following commands whenever non ace killed enemy ace. | `on_non_ace_killed_other_ace = { FROM = { random_events = { 100 = ace_died.1 } } }` | FROM = enemy ace. | 1.9 |
| on_ace_killed_by_ace | Trigger the following commands whenever an aces is killed by another ace. | `on_ace_killed_by_ace = { random_events = { 100 = ace_killed_by_ace.1 } }` | FROM = our ace, PREV = enemy ace, has killed FROM. | 1.0 |
| on_ace_killed_other_ace | Trigger the following commands whenever an aces is killed by another ace (surviving ace side). | `on_ace_killed_other_ace = { random_events = { 100 = ace_killed_other_ace.1 } }` | FROM = our ace, PREV = enemy ace, killed by FROM. | 1.0 |
| on_aces_killed_each_other | Trigger the following commands whenever two aces kill each other in air duel. | `on_aces_killed_each_other = { random_events = { 100 = aces_killed_each_other.1 } }` | FROM = ace, PREV = enemy ace. | 1.0 |

## La Résistance <a id="La_R.C3.A9sistance"></a><a id="La_Résistance"></a>

| Name | Description | Examples | Notes | Version Added |
| --- | --- | --- | --- | --- |
| on_operation_completed | Trigger the following commands whenever an operation is completed before the outcome effect is executed and the operative detection chance is rolled. | `on_operation_completed = { effect = { … } }` | THIS - the operation, ROOT - the initiating country, FROM - the target country. | 1.9 |
| on_operative_detected_during_operation | Trigger the following commands whenever an operative dies. | `on_operative_death = { effect = { … } }` | THIS - the operative, ROOT - the killer country (optional), FROM - the country the operative is operating for, FROM.FROM - operation state (will only be set if the operation has a specific selection_target). | 1.9 |
| on_operative_on_mission_spotted | Trigger the following commands whenever an operative performing an offensive mission in a country. | `on_operative_on_mission_spotted = { effect = { … } }` | THIS - the operative, FROM - the country the operative was performing its mission in, ROOT - the country the operative is operating for. | 1.9 |
| on_operative_captured | Trigger the following commands whenever an operative is captured. | `on_operative_captured = { effect = { … } }` | THIS - the operative, ROOT - the country the operative was performing its mission in, FROM - the country the operative is operating for. | 1.9 |
| on_operative_created | Trigger the following commands whenever an operative is created. | `on_operative_created = { effect = { … } }` | THIS - the operative, FROM - the country the operative is created by. | 1.9.1 |
| on_operative_death | Trigger the following commands whenever an operative dies. | `on_operative_death = { effect = { … } }` | THIS - the operative, ROOT - the killer country (optional), FROM - the country the operative is operating for. | 1.9 |
| on_operative_recruited | Trigger the following commands whenever an operative is recruited. | `on_operative_recruited = { effect = { … } }` | THIS - the operative, FROM - the country the operative is created by. | 1.9.1 |
| on_fully_decrypted_cipher | Trigger the following commands whenever a country fully decrypts cipher of a target country. | `on_fully_decrypted_cipher = { effect = { … } }` | THIS - the target country that its cipher is decrypted, FROM - the decrypter country. | 1.9 |
| on_activated_active_decryption_bonuses | Trigger the following commands whenever a country activates its active cipher bonuses against a target. | `on_activated_active_decryption_bonuses = { effect = { … } }` | THIS - the target country, FROM - the country that activates its bonuses. | 1.9 |

## Military Industrial Organization <a id="Military_Industrial_Organization"></a>

| Name | Description | Examples | Notes | Version Added |
| --- | --- | --- | --- | --- |
| on_mio_size_increased | Trigger the following commands whenever a MIO increases in size (levels up). |  | ROOT is the Military Industrial Organization, FROM is the owner of the MIO country | 1.13 |
| on_mio_design_team_assigned_to_tech | Trigger the following commands whenever a MIO is assigned to technology research. |  | ROOT is the Military Industrial Organization, FROM is the owner of the MIO | 1.13 |
| on_mio_design_team_assigned_to_variant | Trigger the following commands whenever a MIO is asigned to a variant. |  | ROOT is the Military Industrial Organization, FROM is the owner of the MIO country | 1.13 |
| on_mio_industrial_manufacturer_assigned | Trigger the following commands whenever a MIO assigned to a production line. |  | ROOT is the Military Industrial Organization, FROM is the owner of the MIO | 1.13 |
| on_mio_industrial_manufacturer_unassigned | Trigger the following commands whenever a MIO is unnasigned from a production line. |  | ROOT is the Military Industrial Organization, FROM is the owner of the MIO | 1.13 |

## Special Projects <a id="Special_Projects"></a>

| Name | Description | Examples | Notes | Version Added |
| --- | --- | --- | --- | --- |
| on_project_completion | Triggered when a project is completed | on_project_completion = { effect = { #achievement check  IF = {  limit = {  ROOT = { original_tag = BEL }  }  add_to_variable = { BEL.special_projects_completed = 1 }  }  }  } | ROOT Tag FROM Project | 1.15 |

---

## Navigation

**[Modding](<Modding - Hearts of Iron 4 Wiki.md>)**

- **Documentation**: [Effects](<Effects - Hearts of Iron 4 Wiki.md>) • [Triggers](<Triggers - Hearts of Iron 4 Wiki.md>) • [Defines](<Defines - Hearts of Iron 4 Wiki.md>) • [Modifiers](<Modifiers - Hearts of Iron 4 Wiki.md>) • [List of modifiers](<List of modifiers - Hearts of Iron 4 Wiki.md>) • [Scopes](<Scopes - Hearts of Iron 4 Wiki.md>) • [Localisation](<Localisation - Hearts of Iron 4 Wiki.md>) • [Data structures](<Data structures - Hearts of Iron 4 Wiki.md>) • [Flags](<Data structures - Hearts of Iron 4 Wiki.md#Flags>) • [Event targets](<Data structures - Hearts of Iron 4 Wiki.md#Event_targets>) • [Country tag aliases](<Data structures - Hearts of Iron 4 Wiki.md#Country_tag_aliases>) • [Variables](<Data structures - Hearts of Iron 4 Wiki.md#Variables>) • [Arrays](<Data structures - Hearts of Iron 4 Wiki.md#Arrays>)
- **Scripting**: [Achievements](<Achievement modding - Hearts of Iron 4 Wiki.md>) • [AI](<AI modding - Hearts of Iron 4 Wiki.md>) • [AI focuses](<AI focuses - Hearts of Iron 4 Wiki.md>) • [Autonomous states](<Autonomy state modding - Hearts of Iron 4 Wiki.md>) • [Balances of power](<Balance of power modding - Hearts of Iron 4 Wiki.md>) • [Bookmarks/Scenarios](<Bookmark modding - Hearts of Iron 4 Wiki.md>) • [Game rules](<Bookmark modding - Hearts of Iron 4 Wiki.md#Game_rules>) • [Buildings](<Building modding - Hearts of Iron 4 Wiki.md>) • [Characters and traits](<Character modding - Hearts of Iron 4 Wiki.md>) • [Cosmetic tags](<Cosmetic tag modding - Hearts of Iron 4 Wiki.md>) • [Countries](<Country creation - Hearts of Iron 4 Wiki.md>) • [Divisions](<Division modding - Hearts of Iron 4 Wiki.md>) • [Decisions](<Decision modding - Hearts of Iron 4 Wiki.md>) • [Doctrines](<Doctrine modding - Hearts of Iron 4 Wiki.md>) • [Equipment](<Equipment modding - Hearts of Iron 4 Wiki.md>) • [Events](<Event modding - Hearts of Iron 4 Wiki.md>) • [Factions](<Faction modding - Hearts of Iron 4 Wiki.md>) • [Ideas](<Idea modding - Hearts of Iron 4 Wiki.md>) • [Ideologies](<Ideology modding - Hearts of Iron 4 Wiki.md>) • [Military industrial organizations](<Military industrial organization modding - Hearts of Iron 4 Wiki.md>) • [National focuses](<National focus modding - Hearts of Iron 4 Wiki.md>) • [Resources](<Resources modding - Hearts of Iron 4 Wiki.md>) • [Scripted GUI](<Scripted GUI modding - Hearts of Iron 4 Wiki.md>) • [Technologies and doctrines](<Technology modding - Hearts of Iron 4 Wiki.md>) • [Units](<Unit modding - Hearts of Iron 4 Wiki.md>)
- **Map**: [Map](<Map modding - Hearts of Iron 4 Wiki.md>) • [States](<State modding - Hearts of Iron 4 Wiki.md>) • [Supply areas](<Supply areas modding - Hearts of Iron 4 Wiki.md>) • [Strategic regions](<Strategic region modding - Hearts of Iron 4 Wiki.md>)
- **Graphical**: [Interface](<Interface modding - Hearts of Iron 4 Wiki.md>) • [Graphical assets](<Graphical asset modding - Hearts of Iron 4 Wiki.md>) • [Entities](<Entity modding - Hearts of Iron 4 Wiki.md>) • [Posteffects](<Posteffect modding - Hearts of Iron 4 Wiki.md>) • [Particles](<Particle modding - Hearts of Iron 4 Wiki.md>) • [Fonts](<Font modding - Hearts of Iron 4 Wiki.md>)
- **Cosmetic**: [Portraits](<Portrait modding - Hearts of Iron 4 Wiki.md>) • [Namelists](<Namelist modding - Hearts of Iron 4 Wiki.md>) • [Music](<Music modding - Hearts of Iron 4 Wiki.md>) • [Sound](<Sound modding - Hearts of Iron 4 Wiki.md>)
- **Other**: [Console commands](<Console commands - Hearts of Iron 4 Wiki.md>) • [Troubleshooting](<Troubleshooting - Hearts of Iron 4 Wiki.md>) • [Mod structure](<Mod structure - Hearts of Iron 4 Wiki.md>) • [Mods](<Mods - Hearts of Iron 4 Wiki.md>) • [Nudger](<Nudger - Hearts of Iron 4 Wiki.md>)
