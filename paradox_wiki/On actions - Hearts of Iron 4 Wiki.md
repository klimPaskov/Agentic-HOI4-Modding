# Table of contents

- [File example](#file-example)
- [General on actions](#general-on-actions)
- [Politics](#politics)
- [Diplomacy/War](#diplomacy-war)
- [Faction](#faction)
- [Autonomy](#autonomy)
- [Governments in Exile](#governments-in-exile)
- [States](#states)
- [Wargoals](#wargoals)
- [Unit Leader](#unit-leader)
- [Military](#military)
- [Aces](#aces)
- [La Résistance](#la-r-sistance)
- [Military Industrial Organization](#military-industrial-organization)
- [Special Projects](#special-projects)

---

On actions are blocks that are executed when a certain action occurs, such as a country declaring war on a different country or a state changing control. On actions are stored in /Hearts of Iron IV/common/on\_actions/\*.txt files.

Each on action is a separate block within the `on_actions = { ... }` block, which is the root block of the on actions file. Each on\_action has up to 2 arguments:

- `effect = { ... }` is present for every single on action, being an effect block the insides of which are executed when needed.
- `random_events = { ... }` is present for on\_actions where the default scope (Same as ROOT, if not specified otherwise) is a country, such as on\_new\_term\_election. This instantly fires a random one of the specified events within with the given weights being applied. This is done with a [probability-proportional-to-size sampling](http://en.wikipedia.org/wiki/Sampling_(statistics)#Probability-proportional-to-size_sampling) approach.

Putting `0` instead of an event ID will ensure that nothing will happen if the chance lands on this.
Additionally, an event cannot be fired using `random_events = { ... }` if the event's `trigger = { ... }` block evaluates as false. In this case, each scope is treated the same as on action's: on action's FROM is treated as the event's FROM, same with FROM.FROM.
If there are multiple random\_events blocks, one event will be picked from each.

Note that in terms of [Scopes](<Scopes - Hearts of Iron 4 Wiki.md>), ROOT is the default assumed scope unless specified otherwise (in on\_actions that have THIS as a separate entity from ROOT), while FROM and FROM.FROM can serve as secondary blocks that are provided in addition.

Each on action can only be executed after the game's start, ignoring any effects done within history files or the bookmark's `effects = { ... }` section that normally would trigger one, such as [set\_politics](<Effects - Hearts of Iron 4 Wiki.md#set-politics>).

## <a id="file-example"></a>File example

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

## <a id="general-on-actions"></a>General on actions
| Name | Description | Examples | Notes | Version Added |
| --- | --- | --- | --- | --- |
| <a id="on-startup"></a> on\_startup | Trigger the following commands at the first day of a new game, after country selection. Doesn't work with save loading. | `on_startup = { effect = { ENG = { news_event = { id = news_event.1 days = 31 random_days = 27 } # Fires a news event in February 1936 } # assuming the default start date } # Scoping into ENG is necessary, since } # news_event is a country-scoped effect` | **Has a default scope of `none`**, instead of firing for each country individually as in other Paradox games such as Europa Universalis IV. Many effects that usually can be used in any scope will not work, without manual [scoping](<Scopes - Hearts of Iron 4 Wiki.md>) into countries, states, or elsewhere. | 1.3.3 |
| <a id="on-daily"></a> on\_daily | Triggers each day for **every country separately** (performance heavy, use carefully) | `on_daily = { effect = { if = { limit = { has_variable = to_be_updated_daily } add_to_variable = { to_be_updated_daily = 1 } } } }` | Useful for scripted guis and mods adding new mechanics (can increment a variable daily e.g.). **Only use scoping if you're careful to avoid duplicate effects**. This being executed for every country separately means that this is essentially equivalent to a single effect executed daily inside of every\_country. e.g. `effect = { GER = { add_political_power = 1 } }` will add ~100 political power to ![Flag of Germany](media/on-actions-hearts-of-iron-4-wiki_f9b1ef17b8__img1.png) Germany daily, as there being ~100 countries on the world map means that this will get executed ~100 times per day. | 1.5.2 |
| <a id="on-daily-tag"></a> on\_daily\_TAG | Triggers each day for the specified country only | `on_daily_SOV = { effect = { if = { limit = { has_war_with = GER } SOV_escalate_the_war_effect = yes } } }` | Only runs the effects if the country exists. | 1.9 |
| <a id="on-weekly"></a> on\_weekly | Triggers each week for every country separately | `on_weekly = { effect = { if = { limit = { has_intelligence_agency = yes is_ai = yes } update_operation_ai = yes } } }` | Useful for ai scripting. Runs on the beginning of the day if the num\_days variable is divisible by 7. | 1.9 |
| <a id="on-weekly-tag"></a> on\_weekly\_TAG | Triggers each week for the specified country only | `on_weekly_BHR = { if = { limit = { has_country_flag = BHR_must_control_states any_owned_state = { NOT = { is_controlled_by = ROOT } } has_stability < 0.5 } country_event = BHR_event.0 clr_country_flag = BHR_must_control_states } }` | Only runs the effects if the country exists. Runs on the beginning of the day if the num\_days variable is divisible by 7. | 1.9 |
| <a id="on-monthly"></a> on\_monthly | Triggers each month for every country separately | `on_monthly = { random_events = { 1 = random_event.0 99 = 0 } }` |  | 1.9 |
| <a id="on-monthly-tag"></a> on\_monthly\_TAG | Triggers each month for the specified country only | `on_monthly_USA = { effect = { add_to_variable = { USA_unrest = 1 } clamp_variable = { var = USA_unrest max = 10 } if = { limit = { check_variable = { USA_unrest = 10 } } country_event = usa.rebellion.0 } } }` | Only runs the effects if the country exists. | 1.9 |

## <a id="politics"></a>Politics
| Name | Description | Examples | Notes | Version Added |
| --- | --- | --- | --- | --- |
| <a id="on-stage-coup"></a> on\_stage\_coup | For the non ![La Résistance](media/on-actions-hearts-of-iron-4-wiki_f9b1ef17b8__img2.png) La Résistance stage coup. Trigger the following commands whenever a coup is stage. | `on_stage_coup = { effect = { } }` | ROOT is the country that stages the coup, FROM is the target country. | 1.0 |
| <a id="on-coup-succeeded"></a> on\_coup\_succeeded | For the non ![La Résistance](media/on-actions-hearts-of-iron-4-wiki_f9b1ef17b8__img2.png) La Résistance stage coup. Trigger the following commands whenever a coup succeeds. | `on_coup_succeeded = { effect = { random_other_country = { limit = { has_government = democratic original_tag = ROOT } set_politics = { elections_allowed = yes } } } }` | ROOT is the country that coup succeeded in, FROM is the stager of the coup | 1.0 |
| <a id="on-government-change"></a> on\_government\_change | Trigger the following commands whenever a country switches its government. | `on_government_change = { effect = { … } }` | This includes `set_politics` and `start_civil_war` (always for both sides) and excludes being puppeted. Will always also trigger [on\_ruling\_party\_change](#on-ruling-party-change). | 1.0 |
| <a id="on-ruling-party-change"></a> on\_ruling\_party\_change | Trigger the following commands whenever a country switches its ideology. | `on_ruling_party_change = { effect = { … } }` | `old_ideology_token` is a temporary variable that stores the old ideology as a token. Alongside what triggers [on\_government\_change](#on-government-change), also includes being puppeted or changing the ideology via a console command. | 1.9 |
| <a id="on-new-term-election"></a> on\_new\_term\_election | Trigger the following commands whenever an election happens or is called by the **hold\_election** command. | `on_new_term_election = { random_events = { 100 = usa.6 } }` |  | 1.0 |
| <a id="on-before-peace-conference-start"></a> on\_before\_peace\_conference\_start | Trigger the following commands after capitulation but before a peace conference starts. | `on_before_peace_conference_start = { effect = { … } }` | ROOT is winner, FROM is loser (called for all winners against all losers). | 1.15.2 |
| <a id="on-peaceconference-ended"></a> on\_peaceconference\_ended | Trigger the following commands whenever a peace conference ends. | `on_peaceconference_ended = { effect = { … } }` | ROOT is the winner, FROM is the loser. Is also triggered by the [white\_peace](<Effects - Hearts of Iron 4 Wiki.md#white-peace>) effect is used or when a conditional surrender is accepted. | 1.5 |
| <a id="on-peaceconference-started"></a> on\_peaceconference\_started | Trigger the following commands whenever a peace conference starts. | `on_peaceconference_started = { effect = { … } }` | ROOT is the winner, FROM is the loser. Is also triggered by the [white\_peace](<Effects - Hearts of Iron 4 Wiki.md#white-peace>) effect is used or when a conditional surrender is accepted. | 1.12.3 |

## <a id="diplomacy-2fwar"></a><a id="diplomacy-war"></a>Diplomacy/War
| Name | Description | Examples | Notes | Version Added |
| --- | --- | --- | --- | --- |
| <a id="on-send-volunteers"></a> on\_send\_volunteers | Trigger the following commands whenever a country send volunteers to another. | `on_send_volunteers = { effect = { … } }` | ROOT is sender, FROM is receiver. | 1.9 |
| <a id="on-border-war-lost"></a> on\_border\_war\_lost | Trigger the following commands whenever a country loses a border war. | `on_border_war_lost = { effect = { owner = { add_ideas = lost_conflict } } }` | "Border war" refers to the state-based border wars enabled with [set\_border\_war](<Effects - Hearts of Iron 4 Wiki.md#set-border-war>), represented with orange stripes over the state, rather than border wars that simulate combat between countries. The default scope is the state that lost the border war. | 1.0 |
| <a id="on-war-relation-added"></a> on\_war\_relation\_added | fired when two countries end up at war with each other (on\_war is fired when a country goes to war against anyone and is not fired again when it enters war against another country unless it went to peace first) | `on_war_relation_added = { effect = { … } }` | ROOT is attacker, FROM is defender | 1.9.3 |
| <a id="on-declare-war"></a> on\_declare\_war | Trigger the following commands whenever a country declares war. | `on_declare_war = { effect = { if = { limit = { tag = GER FROM = { tag = SOV } } add_ideas = GER_barbarossa } } }` | FROM is war target. ROOT is for the country who is declaring war | 1.0 |
| <a id="on-war"></a> on\_war | Trigger the following commands whenever a country has just entered a state of war from initially being at peace. | `on_war = { effect = { … } }` | THIS is country that has just gotten into a war. | 1.7 |
| <a id="on-peace"></a> on\_peace | Trigger the following commands whenever a country is no longer at war. | `on_peace = { effect = { … } }` | THIS is country that is no longer at war. | 1.7 |
| <a id="on-capitulation"></a> on\_capitulation | Trigger the following commands whenever a country capitulates, in the middle of the process. | `on_capitulation = { effect = { … } }` | ROOT is capitulated country, FROM is winner. Several processes such as the deletion of units and transfer of equipment have already been executed by this point. | 1.0 |
| <a id="on-capitulation-immediate"></a> on\_capitulation\_immediate | Trigger the following commands whenever a country capitulates, at the beginning of the process. | `on_capitulation_immediate = { effect = { … } }` | ROOT is capitulated country, FROM is winner. | 1.11.5 |
| <a id="on-uncapitulation"></a> on\_uncapitulation | Trigger the following commands whenever a country that was previously capitulated changes its status to no longer having capitulated. | `on_uncapitulation = { effect = { … } }` | ROOT is the country affected. | 1.4 |
| <a id="on-annex"></a> on\_annex | Trigger the following commands whenever a country is annexed. | `on_annex = { effect = { … } }` | ROOT is winner, FROM gets annexed. For civil wars **on\_civil\_war\_end** is also fired. | 1.3.3 |
| <a id="on-civil-war-end-before-annexation"></a> on\_civil\_war\_end\_before\_annexation | Trigger the following commands just before FROM gets annexed, meaning the country and everything it owns still exists. | `on_civil_war_end_before_annexation = { effect = { … } }` | ROOT is winner, FROM gets annexed. It will also fire **on\_annex** and **on\_civil\_war\_end**. | 1.6 |
| <a id="on-civil-war-end"></a> on\_civil\_war\_end | Trigger the following commands whenever a civil war ends. | `on_civil_war_end = { effect = { … } }` | ROOT is civil war winner, FROM gets annexed. This will also fire **on\_annex**. | 1.0 |
| <a id="on-puppet"></a> on\_puppet | Trigger the following commands whenever a country is puppeted in a **peace conference only**. | `on_puppet = { effect = { … } }` | ROOT is the nation being puppeted, FROM is the overlord. | 1.0 |
| <a id="on-liberate"></a> on\_liberate | Trigger the following commands whenever a country is liberated in a **peace conference only**. | `on_liberate = { effect = { … } }` | ROOT is the nation being liberated, FROM is the leader of the liberators. | 1.0 |
| <a id="on-release-as-free"></a> on\_release\_as\_free | Trigger the following commands whenever a country is released. | `on_release_as_free = { effect = { … } }` | #ROOT is free nation FROM is releaser. | 1.3 |
| <a id="on-release-as-puppet"></a> on\_release\_as\_puppet | Trigger the following commands whenever puppeting through the occupied territories menu during peace time (or when releasing from non-core but owned territory). | `on_release_as_puppet = { effect = { … } }` | ROOT is the nation being released, FROM is the overlord. | 1.3 |
| <a id="on-guarantee"></a> on\_guarantee | Trigger the following commands whenever a country guarantees independence of another country. |  | ROOT is the country which guarantees, FROM is the country that is guaranteed. |  |
| <a id="on-military-access"></a> on\_military\_access | Trigger the following commands whenever a country accepts the request for military access. |  | ROOT is the country which requested, FROM is the country that accepted. |  |
| <a id="on-offer-military-access"></a> on\_offer\_military\_access | Trigger the following commands whenever a country accepts the offer for military access. |  | ROOT is the country which offered, FROM is the country that accepted. |  |
| <a id="on-call-allies"></a> on\_call\_allies | Trigger the following commands whenever a country accepts the call to war. |  | ROOT is the country which called, FROM is the country that joined. |  |
| <a id="on-join-allies"></a> on\_join\_allies | Trigger the following commands whenever a country joins a war of an ally. |  | ROOT is the country which joined, FROM is the country whose war was joined. |  |
| <a id="on-lend-lease"></a> on\_lend\_lease | Trigger the following commands whenever a country has their lend lease accepted. |  | ROOT is the country that sent the lend lease, FROM is the country that accepted. |  |
| <a id="on-incoming-lend-lease"></a> on\_incoming\_lend\_lease | Trigger the following commands whenever a country accepts a requested lend lease. |  | ROOT is the country that accepted, FROM is the country that requested. |  |
| <a id="on-send-expeditionary-force"></a> on\_send\_expeditionary\_force | Trigger the following commands whenever a country accepts sent expeditionary forces. |  | ROOT is the country that sent, FROM is the country that accepted. |  |
| <a id="on-return-expeditionary-forces"></a> on\_return\_expeditionary\_forces | Trigger the following commands whenever a country returns their expeditionary forces. |  | ROOT is the owner of the forces, FROM is the country where the forces were sent. |  |
| <a id="on-request-expeditionary-forces"></a> on\_request\_expeditionary\_forces | Trigger the following commands whenever a country requests expeditionary forces. |  | ROOT is the country that requests, FROM is the target of the request. |  |
| <a id="on-ask-for-state-control"></a> on\_ask\_for\_state\_control | Trigger the following commands whenever a country accepts the request for control of a state. |  | ROOT is the requester, FROM is the country in control of the state. |  |
| <a id="on-give-state-control"></a> on\_give\_state\_control | Trigger the following commands whenever a country accepts being given control of a state. |  | ROOT is the giver, FROM is the receiver. |  |
| <a id="on-peace-proposal"></a> on\_peace\_proposal | Trigger the following commands whenever a country accepts a conditional surrender. |  | ROOT is sender of conditional surrender, FROM is the receiver. |  |
| <a id="on-send-attache"></a> on\_send\_attache | Triggers actions on an attache being accepted. |  | Default scope is sender, FROM = receiver |  |

## <a id="faction"></a>Faction
| Name | Description | Examples | Notes | Version Added |
| --- | --- | --- | --- | --- |
| <a id="on-create-faction"></a> on\_create\_faction | Trigger the following commands whenever a country create a faction. | `on_create_faction = { effect = { … } }` | FROM is the one that joins the faction. | 1.0 |
| <a id="on-faction-formed"></a> on\_faction\_formed | Trigger the following commands when a faction is formed. | `on_faction_formed = { effect = { news_event = { id = news.159 } } }` |  | 1.0 |
| <a id="on-offer-join-faction"></a> on\_offer\_join\_faction | Trigger the following commands whenever a country joins a faction after being invited. | `on_offer_join_faction = { effect = { … } }` | FROM is the country invited, THIS and ROOT are the faction leader. | 1.0 |
| <a id="on-join-faction"></a> on\_join\_faction | Trigger the following commands for a faction leader whenever a country joins after they ask to do so. | `on_join_faction = { effect = { … } }` | FROM is faction leader, ROOT and THIS are the country that joins. | 1.0 |
| <a id="on-assume-faction-leadership"></a> on\_assume\_faction\_leadership | Trigger the following commands whenever a country assumes leadership of a faction. | `on_assume_faction_leadership = { effect = { … } }` | ROOT is the new faction leader FROM is the old faction leader | 1.7 |
| <a id="on-leave-faction"></a> on\_leave\_faction | Trigger the following commands whenever a country leave a faction. | `on_leave_faction = { effect = { if = { limit = { AND = { tag = CAN NOT = { has_dlc = "Together for Victory" } } } drop_cosmetic_tag = yes } }` | FROM is the faction Leader, ROOT is the country leaving the faction | 1.0 |

## <a id="autonomy"></a>Autonomy
| Name | Description | Examples | Notes | Version Added |
| --- | --- | --- | --- | --- |
| <a id="on-subject-annexed"></a> on\_subject\_annexed | Trigger the following commands when a country annex a subject. | `on_subject_annexed = { effect = { … } }` | ROOT is the subject, FROM is the overlord. | 1.0 |
| <a id="on-subject-free"></a> on\_subject\_free | Trigger the following commands when a country grants freedom to a puppet. | `on_subject_free = { effect = { … } }` | ROOT is the subject, FROM is the previous overlord. | 1.0 |
| <a id="on-subject-autonomy-level-change"></a> on\_subject\_autonomy\_level\_change | Trigger the following commands when the autonomy level of a puppet changes. | `on_subject_autonomy_level_change = { effect = { … } }` | ROOT is the subject, FROM is the overlord. | 1.0 |

## <a id="governments-in-exile"></a>Governments in Exile
| Name | Description | Examples | Notes | Version Added |
| --- | --- | --- | --- | --- |
| <a id="on-government-exiled"></a> on\_government\_exiled | Trigger the following commands whenever a country becomes a government in exile. | `on_government_exiled = { effect = { = { … } }` | ROOT is the government in exile, FROM is the country that is hosting the government in exile. | 1.6 |
| <a id="on-host-changed-from-capitulation"></a> on\_host\_changed\_from\_capitulation | Trigger the following commands whenever a country that is hosting a government in exile has capitulated. | `on_host_changed_from_capitulation= { effect = { = { … } }` | ROOT is the government in exile, FROM is the new country hosting the government in exile, FROM:FROM is the old country that was hosting the government in exile. | 1.6 |
| <a id="on-exile-government-reinstated"></a> on\_exile\_government\_reinstated | Trigger the following commands whenever a country has returned from governing in exile. | `on_exile_government_reinstated = { effect = { = { … } }` | ROOT is the government in exile, FROM is the country that was hosting the government in exile. | 1.6 |

## <a id="states"></a>States
| Name | Description | Examples | Notes | Version Added |
| --- | --- | --- | --- | --- |
| <a id="on-state-control-changed"></a> on\_state\_control\_changed | Trigger the following commands when a state's controller changes. | `on_state_control_changed = { effect = { if = { limit = { FROM.FROM = { state = 123 } } if = { limit = { tag = BHR } FROM.FROM = { set_state_name = STATE_123_BHR set_province_name = { id = 1234 name = VICTORY_POINTS_1234_BHR } } } else = { # Unnested else is preferred over nested FROM.FROM = { reset_state_name = yes reset_province_name = 1234 } } } } }` | ROOT is new controller, FROM is old controller, FROM.FROM is state ID. | 1.4 |

## <a id="wargoals"></a>Wargoals
| Name | Description | Examples | Notes | Version Added |
| --- | --- | --- | --- | --- |
| <a id="on-generate-wargoal"></a> on\_generate\_wargoal | Trigger the following commands whenever the country generates a wargoal. | `on_generate_wargoal = { }` | ROOT is the wargoal owner, FROM is the wargoal target |  |
| <a id="on-justifying-wargoal-pulse"></a> on\_justifying\_wargoal\_pulse | Trigger the following commands whenever the country is targeted by a wargoal under justification. | `on_justifying_wargoal_pulse = { random_events = { 100 = war_justification.1 } }` | FROM = target nation. Checked every day. | 1.0 |
| <a id="on-wargoal-expire"></a> on\_wargoal\_expire | Trigger the following commands whenever a wargoal expire. | `on_wargoal_expire = { random_events = { 100 = war_justification.301 } }` | FROM is the wargoal owner. | 1.0 |

## <a id="unit-leader"></a>Unit Leader
| Name | Description | Examples | Notes | Version Added |
| --- | --- | --- | --- | --- |
| <a id="on-unit-leader-created"></a> on\_unit\_leader\_created | Trigger the following commands when an army leader is created. | `on_unit_leader_created = { effect = { … } }` | FROM is owner country, ROOT is the unit leader. | 1.5 |
| <a id="on-army-leader-daily"></a> on\_army\_leader\_daily | Trigger the following commands on an army leader each day. | `on_army_leader_daily = { effect = { … } }` | FROM is owner country, ROOT is the unit leader. | 1.0 |
| <a id="on-army-leader-won-combat"></a> on\_army\_leader\_won\_combat | Trigger the following commands whenever an army leader won a combat. | `on_army_leader_won_combat = { effect = { … } }` | FROM is owner country, ROOT is the unit leader. | 1.0 |
| <a id="on-army-leader-lost-combat"></a> on\_army\_leader\_lost\_combat | Trigger the following commands whenever an army leader lost a combat. | `on_army_leader_lost_combat = { effect = { … } }` | FROM is owner country, ROOT is the unit leader. | 1.0 |
| <a id="on-unit-leader-level-up"></a> on\_unit\_leader\_level\_up | Trigger the following commands when a leader gain a level. | `on_unit_leader_level_up = { effect = { … } }` | FROM is owner country, ROOT is the unit leader. | 1.0 |
| <a id="on-army-leader-promoted"></a> on\_army\_leader\_promoted | Trigger the following commands whenever a corps commander is promoted to a field marshal. | `on_army_leader_promoted = { effect = { add_timed_unit_leader_trait = { trait = recently_promoted days = 100 } } }` | FROM is owner country, ROOT is the unit leader. | 1.0 |
| <a id="on-unit-leader-promote-from-ranks-veteran"></a> on\_unit\_leader\_promote\_from\_ranks\_veteran | Triggers the following commands whenever an unit commander gets promoted to a general. | `on_unit_leader_promote_from_ranks_veteran = { effect = { … } }` | FROM is unit, OWNER is owner country, ROOT is the unit leader. | 1.12 |
| <a id="on-unit-leader-promote-from-ranks-green"></a> on\_unit\_leader\_promote\_from\_ranks\_green | Triggers the following commands whenever an unit commander gets promoted to a general. | `on_unit_leader_promote_from_ranks_green = { effect = { … } }` | FROM is unit, OWNER is owner country, ROOT is the unit leader. | 1.12 |

## <a id="military"></a>Military
| Name | Description | Examples | Notes | Version Added |
| --- | --- | --- | --- | --- |
| <a id="on-nuke-drop"></a> on\_nuke\_drop | Trigger the following commands whenever a country drops a nuke. | `on_nuke_drop = { effect = { set_global_flag = first_nuke_dropped } }` | ROOT is the country that launched the nuke, FROM is the nuked state. | 1.0 |
| <a id="on-pride-of-the-fleet-sunk"></a> on\_pride\_of\_the\_fleet\_sunk | Triggers when a country's pride of the fleet is sunk | `on_pride_of_the_fleet_sunk = { effect = { if = { limit = { tag = ENG } FROM = { set_country_flag = achievements_pride_and_extreme_prejudice } } } }` | FROM is the killer country, ROOT is the country of that lost its pride of the fleet. | 1.6 |
| <a id="on-naval-invasion"></a> on\_naval\_invasion | Triggers the following commands whenever a sea invasion is made. | `on_naval_invasion = { effect = { ROOT = { # Unlike most on_actions, ROOT isn't the default scope add_political_power = 100 } } }` | THIS (default scope) is the invaded state, ROOT is the country that invades, FROM is the state where the invasion started | 1.9 |
| <a id="on-paradrop"></a> on\_paradrop | Triggers the following commands whenever a landing occurs. | `on_paradrop = { effect = { FROM = { controller = { add_war_support = 0.01 } } } }` | THIS (default scope) is the invaded state, ROOT is the country that invades, FROM is the state where the invasion started | 1.9 |
| <a id="on-units-paradropped-in-state"></a> on\_units\_paradropped\_in\_state | This differs from on\_paradrop in that it is run once per paradrop, not once per unit dropped. | `on_paradrop = { effect = { FROM = { controller = { add_war_support = 0.01 } } } }` | ROOT is the state that was dropped into, FROM is the dropping country. |  |
| <a id="on-add-history"></a> on\_add\_history | Triggers the following commands whenever receiving a history entry. | `on_add_history = { effect = { … } }` | ROOT is the unit. | 1.12 |

## <a id="aces"></a>Aces
| Name | Description | Examples | Notes | Version Added |
| --- | --- | --- | --- | --- |
| <a id="on-ace-promoted"></a> on\_ace\_promoted | Trigger the following commands whenever an ace is created. | `on_ace_promoted = { random_events = { 100 = ace_promoted.1 } }` | FROM = ace. | 1.0 |
| <a id="on-ace-killed"></a> on\_ace\_killed | Trigger the following commands whenever an aces is killed. | `on_ace_killed = { random_events = { 100 = ace_died.1 } }` | FROM = ace. | 1.0 |
| <a id="on-ace-killed-on-accident"></a> on\_ace\_killed\_on\_accident | Trigger the following commands whenever our aces died on accident. | `on_ace_killed_on_accident = { random_events = { 100 = ace_died.1 } }` | FROM = our ace died in accident. | 1.9 |
| <a id="on-non-ace-killed-other-ace"></a> on\_non\_ace\_killed\_other\_ace | Trigger the following commands whenever non ace killed enemy ace. | `on_non_ace_killed_other_ace = { FROM = { random_events = { 100 = ace_died.1 } } }` | FROM = enemy ace. | 1.9 |
| <a id="on-ace-killed-by-ace"></a> on\_ace\_killed\_by\_ace | Trigger the following commands whenever an aces is killed by another ace. | `on_ace_killed_by_ace = { random_events = { 100 = ace_killed_by_ace.1 } }` | FROM = our ace, PREV = enemy ace, has killed FROM. | 1.0 |
| <a id="on-ace-killed-other-ace"></a> on\_ace\_killed\_other\_ace | Trigger the following commands whenever an aces is killed by another ace (surviving ace side). | `on_ace_killed_other_ace = { random_events = { 100 = ace_killed_other_ace.1 } }` | FROM = our ace, PREV = enemy ace, killed by FROM. | 1.0 |
| <a id="on-aces-killed-each-other"></a> on\_aces\_killed\_each\_other | Trigger the following commands whenever two aces kill each other in air duel. | `on_aces_killed_each_other = { random_events = { 100 = aces_killed_each_other.1 } }` | FROM = ace, PREV = enemy ace. | 1.0 |

## <a id="la-r-sistance"></a><a id="la-r-sistance"></a>La Résistance
| Name | Description | Examples | Notes | Version Added |
| --- | --- | --- | --- | --- |
| <a id="on-operation-completed"></a> on\_operation\_completed | Trigger the following commands whenever an operation is completed before the outcome effect is executed and the operative detection chance is rolled. | `on_operation_completed = { effect = { … } }` | THIS - the operation, ROOT - the initiating country, FROM - the target country. | 1.9 |
| <a id="on-operative-detected-during-operation"></a> on\_operative\_detected\_during\_operation | Trigger the following commands whenever an operative dies. | `on_operative_death = { effect = { … } }` | THIS - the operative, ROOT - the killer country (optional), FROM - the country the operative is operating for, FROM.FROM - operation state (will only be set if the operation has a specific selection\_target). | 1.9 |
| <a id="on-operative-on-mission-spotted"></a> on\_operative\_on\_mission\_spotted | Trigger the following commands whenever an operative performing an offensive mission in a country. | `on_operative_on_mission_spotted = { effect = { … } }` | THIS - the operative, FROM - the country the operative was performing its mission in, ROOT - the country the operative is operating for. | 1.9 |
| <a id="on-operative-captured"></a> on\_operative\_captured | Trigger the following commands whenever an operative is captured. | `on_operative_captured = { effect = { … } }` | THIS - the operative, ROOT - the country the operative was performing its mission in, FROM - the country the operative is operating for. | 1.9 |
| <a id="on-operative-created"></a> on\_operative\_created | Trigger the following commands whenever an operative is created. | `on_operative_created = { effect = { … } }` | THIS - the operative, FROM - the country the operative is created by. | 1.9.1 |
| <a id="on-operative-death"></a> on\_operative\_death | Trigger the following commands whenever an operative dies. | `on_operative_death = { effect = { … } }` | THIS - the operative, ROOT - the killer country (optional), FROM - the country the operative is operating for. | 1.9 |
| <a id="on-operative-recruited"></a> on\_operative\_recruited | Trigger the following commands whenever an operative is recruited. | `on_operative_recruited = { effect = { … } }` | THIS - the operative, FROM - the country the operative is created by. | 1.9.1 |
| <a id="on-fully-decrypted-cipher"></a> on\_fully\_decrypted\_cipher | Trigger the following commands whenever a country fully decrypts cipher of a target country. | `on_fully_decrypted_cipher = { effect = { … } }` | THIS - the target country that its cipher is decrypted, FROM - the decrypter country. | 1.9 |
| <a id="on-activated-active-decryption-bonuses"></a> on\_activated\_active\_decryption\_bonuses | Trigger the following commands whenever a country activates its active cipher bonuses against a target. | `on_activated_active_decryption_bonuses = { effect = { … } }` | THIS - the target country, FROM - the country that activates its bonuses. | 1.9 |

## <a id="military-industrial-organization"></a>Military Industrial Organization
| Name | Description | Examples | Notes | Version Added |
| --- | --- | --- | --- | --- |
| <a id="on-mio-size-increased"></a> on\_mio\_size\_increased | Trigger the following commands whenever a MIO increases in size (levels up). |  | ROOT is the Military Industrial Organization, FROM is the owner of the MIO country | 1.13 |
| <a id="on-mio-design-team-assigned-to-tech"></a> on\_mio\_design\_team\_assigned\_to\_tech | Trigger the following commands whenever a MIO is assigned to technology research. |  | ROOT is the Military Industrial Organization, FROM is the owner of the MIO | 1.13 |
| <a id="on-mio-design-team-assigned-to-variant"></a> on\_mio\_design\_team\_assigned\_to\_variant | Trigger the following commands whenever a MIO is asigned to a variant. |  | ROOT is the Military Industrial Organization, FROM is the owner of the MIO country | 1.13 |
| <a id="on-mio-industrial-manufacturer-assigned"></a> on\_mio\_industrial\_manufacturer\_assigned | Trigger the following commands whenever a MIO assigned to a production line. |  | ROOT is the Military Industrial Organization, FROM is the owner of the MIO | 1.13 |
| <a id="on-mio-industrial-manufacturer-unassigned"></a> on\_mio\_industrial\_manufacturer\_unassigned | Trigger the following commands whenever a MIO is unnasigned from a production line. |  | ROOT is the Military Industrial Organization, FROM is the owner of the MIO | 1.13 |

## <a id="special-projects"></a>Special Projects
| Name | Description | Examples | Notes | Version Added |
| --- | --- | --- | --- | --- |
| <a id="on-mio-size-increased"></a> on\_project\_completion | Triggered when a project is completed | on\_project\_completion = {         effect = { #achievement check              IF = {                  limit = {                      ROOT = { original\_tag = BEL }                  }                  add\_to\_variable = { BEL.special\_projects\_completed = 1 }              }          }      } | ROOT Tag FROM Project | 1.15 |

**[Modding](<Modding - Hearts of Iron 4 Wiki.md>)**
