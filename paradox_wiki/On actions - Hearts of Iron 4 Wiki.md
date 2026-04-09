# Table of contents

- [File example](#file-example)
- [General on actions](#general-on-actions)
- [Politics](#politics)
- [Diplomacy/War](#diplomacywar)
- [Faction](#faction)
- [Autonomy](#autonomy)
- [Governments in Exile](#governments-in-exile)
- [States](#states)
- [Wargoals](#wargoals)
- [Unit Leader](#unit-leader)
- [Military](#military)
- [Aces](#aces)
- [La Résistance](#la-résistance)
- [Military Industrial Organization](#military-industrial-organization)


---

On actions are blocks that are executed when a certain action occurs, such as a country declaring war on a different country or a state changing control. On actions are stored in /Hearts of Iron IV/common/on\_actions/\*.txt files.

Each on action is a separate block within the `on_actions = { ... }` block, which is the root block of the on actions file. Each on\_action has up to 2 arguments:

- `effect = { ... }` is present for every single on action, being an effect block the insides of which are executed when needed.
- `random_events = { ... }` is present for on\_actions where the default scope (Same as ROOT, if not specified otherwise) is a country, such as on\_new\_term\_election. This instantly fires a random one of the specified events within with the given weights being applied. This is done with a [probability-proportional-to-size sampling](<http://en.wikipedia.org/wiki/Sampling_(statistics>)#Probability-proportional-to-size_sampling) approach.

Putting `0` instead of an event ID will ensure that nothing will happen if the chance lands on this.
Additionally, an event cannot be fired using `random_events = { ... }` if the event's `trigger = { ... }` block evaluates as false. In this case, each scope is treated the same as on action's: on action's FROM is treated as the event's FROM, same with FROM.FROM.
If there are multiple random\_events blocks, one event will be picked from each.

Note that in terms of [Scopes](<Scopes - Hearts of Iron 4 Wiki.md>), ROOT is the default assumed scope unless specified otherwise (in on\_actions that have THIS as a separate entity from ROOT), while FROM and FROM.FROM can serve as secondary blocks that are provided in addition.

Each on action can only be executed after the game's start, ignoring any effects done within history files or the bookmark's `effects = { ... }` section that normally would trigger one, such as [set\_politics](<Effect - Hearts of Iron 4 Wiki.md#set-politics>).

## File example

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

## General on actions

- **on_startup**
  - Description: Trigger the following commands at the first day of a new game, after country selection. Doesn't work with save loading.
  - Example:
    ```text
    on_startup = { 
        effect = {
            ENG = {
                news_event = { id = news_event.1 days = 31 random_days = 27 } # Fires a news event in February 1936
            }  # assuming the default start date
        }      # Scoping into ENG is necessary, since
    }          # news_event is a country-scoped effect
    ```
  - Notes:
    ```text
    Has a default scope of
    none
    , instead of firing for each country individually as in other Paradox games such as Europa Universalis IV. Many effects that usually can be used in any scope will not work, without manual
    scoping
    into countries, states, or elsewhere.
    ```
  - Version Added: 1.3.3

- **on_daily**
  - Description:
    ```text
    Triggers each day for
    every country separately
    (performance heavy, use carefully)
    ```
  - Example:
    ```text
    on_daily = {
        effect = {
            if = {
                limit = { has_variable = to_be_updated_daily }
                add_to_variable = { to_be_updated_daily = 1 }
            } 
        }
    }
    ```
  - Notes:
    ```text
    Useful for scripted guis and mods adding new mechanics (can increment a variable daily e.g.).
    Only use scoping if you're careful to avoid duplicate effects
    . This being executed for every country separately means that this is essentially equivalent to a single effect executed daily inside of every_country. e.g.
    effect = { GER = { add_political_power = 1 } }
    will add ~100 political power to
    Germany
    daily, as there being ~100 countries on the world map means that this will get executed ~100 times per day.
    ```
  - Version Added: 1.5.2

- **on_daily_TAG**
  - Description: Triggers each day for the specified country only
  - Example:
    ```text
    on_daily_SOV = {
        effect = {  
            if = {
                limit = { has_war_with = GER }
                SOV_escalate_the_war_effect = yes
            }
        }
    }
    ```
  - Notes: Only runs the effects if the country exists.
  - Version Added: 1.9

- **on_weekly**
  - Description: Triggers each week for every country separately
  - Example:
    ```text
    on_weekly = {
        effect = {
            if = {
                limit = { 
                    has_intelligence_agency = yes
                    is_ai = yes
                }
                update_operation_ai = yes
            }
        }
    }
    ```
  - Notes:
    ```text
    Useful for ai scripting. Runs on the beginning of the day if the
    num_days variable
    is divisible by 7.
    ```
  - Version Added: 1.9

- **on_weekly_TAG**
  - Description: Triggers each week for the specified country only
  - Example:
    ```text
    on_weekly_BHR = {
        if = {
            limit = {
                has_country_flag = BHR_must_control_states
                any_owned_state = {
                    NOT = { is_controlled_by = ROOT }
                }
                has_stability < 0.5
            }
            country_event = BHR_event.0
            clr_country_flag = BHR_must_control_states
        }
    }
    ```
  - Notes:
    ```text
    Only runs the effects if the country exists. Runs on the beginning of the day if the
    num_days variable
    is divisible by 7.
    ```
  - Version Added: 1.9

- **on_monthly**
  - Description: Triggers each month for every country separately
  - Example:
    ```text
    on_monthly = { 
        random_events = {
            1 = random_event.0
            99 = 0
        }
    }
    ```
  - Version Added: 1.9

- **on_monthly_TAG**
  - Description: Triggers each month for the specified country only
  - Example:
    ```text
    on_monthly_USA = {
        effect = {
            add_to_variable = { USA_unrest = 1 }
            clamp_variable = {
                var = USA_unrest
                max = 10
            }
            if = {
                limit = { 
                    check_variable = { USA_unrest = 10 }
                }
                country_event = usa.rebellion.0
            }
        }
    }
    ```
  - Notes: Only runs the effects if the country exists.
  - Version Added: 1.9

## Politics

- **on_stage_coup**
  - Description:
    ```text
    For the non
    La Résistance
    stage coup. Trigger the following commands whenever a coup is stage.
    ```
  - Example:
    ```text
    on_stage_coup = { 
        effect = { 
        }
    }
    ```
  - Notes: ROOT is the country that stages the coup, FROM is the target country.
  - Version Added: 1.0

- **on_coup_succeeded**
  - Description:
    ```text
    For the non
    La Résistance
    stage coup. Trigger the following commands whenever a coup succeeds.
    ```
  - Example:
    ```text
    on_coup_succeeded = { 
        effect = { 
            random_other_country = { 
                limit = { 
                    has_government = democratic
                    original_tag = ROOT
                } 
                set_politics = { elections_allowed = yes }
            }
        }
    }
    ```
  - Notes: ROOT is the country that coup succeeded in, FROM is the stager of the coup
  - Version Added: 1.0

- **on_government_change**
  - Description: Trigger the following commands whenever a country switches its government.
  - Example:
    ```text
    on_government_change = { effect = {  …  } }
    ```
  - Notes:
    ```text
    This includes
    set_politics
    and
    start_civil_war
    (always for both sides) and excludes being puppeted. Will always also trigger
    on_ruling_party_change
    .
    ```
  - Version Added: 1.0

- **on_ruling_party_change**
  - Description: Trigger the following commands whenever a country switches its ideology.
  - Example:
    ```text
    on_ruling_party_change = { effect = {  …  } }
    ```
  - Notes:
    ```text
    old_ideology_token
    is a
    temporary variable
    that stores the old ideology as a token. Alongside what triggers
    on_government_change
    , also includes being puppeted or changing the ideology via a console command.
    ```
  - Version Added: 1.9

- **on_new_term_election**
  - Description:
    ```text
    Trigger the following commands whenever an election happens or is called by the
    hold_election
    command.
    ```
  - Example:
    ```text
    on_new_term_election = { random_events = { 100 = usa.6 } }
    ```
  - Version Added: 1.0

- **on_before_peace_conference_start**
  - Description: Trigger the following commands after capitulation but before a peace conference starts.
  - Example:
    ```text
    on_before_peace_conference_start = { effect = { … } }
    ```
  - Notes: ROOT is winner, FROM is loser (called for all winners against all losers).
  - Version Added: 1.15.2

- **on_peaceconference_ended**
  - Description: Trigger the following commands whenever a peace conference ends.
  - Example:
    ```text
    on_peaceconference_ended = { effect = { … } }
    ```
  - Notes:
    ```text
    ROOT is the winner, FROM is the loser. Is also triggered by the
    white_peace
    effect is used or when a conditional surrender is accepted.
    ```
  - Version Added: 1.5

- **on_peaceconference_started**
  - Description: Trigger the following commands whenever a peace conference starts.
  - Example:
    ```text
    on_peaceconference_started = { effect = { … } }
    ```
  - Notes:
    ```text
    ROOT is the winner, FROM is the loser. Is also triggered by the
    white_peace
    effect is used or when a conditional surrender is accepted.
    ```
  - Version Added: 1.12.3

## Diplomacy/War

- **on_send_volunteers**
  - Description: Trigger the following commands whenever a country send volunteers to another.
  - Example:
    ```text
    on_send_volunteers = {
        effect = { … }
    }
    ```
  - Notes: ROOT is sender, FROM is receiver.
  - Version Added: 1.9

- **on_border_war_lost**
  - Description: Trigger the following commands whenever a country loses a border war.
  - Example:
    ```text
    on_border_war_lost = {
        effect = {
            owner = {
                add_ideas = lost_conflict
            }
        }
    }
    ```
  - Notes:
    ```text
    "Border war" refers to the state-based border wars enabled with
    set_border_war
    , represented with orange stripes over the state, rather than border wars that simulate combat between countries. The default scope is the state that lost the border war.
    ```
  - Version Added: 1.0

- **on_war_relation_added**
  - Description: fired when two countries end up at war with each other (on_war is fired when a country goes to war against anyone and is not fired again when it enters war against another country unless it went to peace first)
  - Example:
    ```text
    on_war_relation_added = {
        effect = { … }
    }
    ```
  - Notes: ROOT is attacker, FROM is defender
  - Version Added: 1.9.3

- **on_declare_war**
  - Description: Trigger the following commands whenever a country declares war.
  - Example:
    ```text
    on_declare_war = {
        effect = {
            if = {
                limit = {
                    tag = GER
                    FROM = { tag = SOV }
                }
                add_ideas = GER_barbarossa
            }
        }
    }
    ```
  - Notes:
    ```text
    FROM is war target.
    ROOT is for the country who is declaring war
    ```
  - Version Added: 1.0

- **on_war**
  - Description: Trigger the following commands whenever a country has just entered a state of war from initially being at peace.
  - Example:
    ```text
    on_war = {
        effect = { … }
    }
    ```
  - Notes: THIS is country that has just gotten into a war.
  - Version Added: 1.7

- **on_peace**
  - Description: Trigger the following commands whenever a country is no longer at war.
  - Example:
    ```text
    on_peace = {
        effect = { … }
    }
    ```
  - Notes: THIS is country that is no longer at war.
  - Version Added: 1.7

- **on_capitulation**
  - Description: Trigger the following commands whenever a country capitulates, in the middle of the process.
  - Example:
    ```text
    on_capitulation = {
        effect = { … }
    }
    ```
  - Notes: ROOT is capitulated country, FROM is winner. Several processes such as the deletion of units and transfer of equipment have already been executed by this point.
  - Version Added: 1.0

- **on_capitulation_immediate**
  - Description: Trigger the following commands whenever a country capitulates, at the beginning of the process.
  - Example:
    ```text
    on_capitulation_immediate = {
        effect = { … }
    }
    ```
  - Notes: ROOT is capitulated country, FROM is winner.
  - Version Added: 1.11.5

- **on_uncapitulation**
  - Description: Trigger the following commands whenever a country that was previously capitulated changes its status to no longer having capitulated.
  - Example:
    ```text
    on_uncapitulation = {
        effect = { … }
    }
    ```
  - Notes: ROOT is the country affected.
  - Version Added: 1.4

- **on_annex**
  - Description: Trigger the following commands whenever a country is annexed.
  - Example:
    ```text
    on_annex = {
        effect = { … }
    }
    ```
  - Notes:
    ```text
    ROOT is winner, FROM gets annexed. For civil wars
    on_civil_war_end
    is also fired.
    ```
  - Version Added: 1.3.3

- **on_civil_war_end_before_annexation**
  - Description: Trigger the following commands just before FROM gets annexed, meaning the country and everything it owns still exists.
  - Example:
    ```text
    on_civil_war_end_before_annexation = {
        effect = { … }
    }
    ```
  - Notes:
    ```text
    ROOT is winner, FROM gets annexed. It will also fire
    on_annex
    and
    on_civil_war_end
    .
    ```
  - Version Added: 1.6

- **on_civil_war_end**
  - Description: Trigger the following commands whenever a civil war ends.
  - Example:
    ```text
    on_civil_war_end = {
        effect = { … }
    }
    ```
  - Notes:
    ```text
    ROOT is civil war winner, FROM gets annexed. This will also fire
    on_annex
    .
    ```
  - Version Added: 1.0

- **on_puppet**
  - Description:
    ```text
    Trigger the following commands whenever a country is puppeted in a
    peace conference only
    .
    ```
  - Example:
    ```text
    on_puppet = {
        effect = { … }
    }
    ```
  - Notes: ROOT is the nation being puppeted, FROM is the overlord.
  - Version Added: 1.0

- **on_liberate**
  - Description:
    ```text
    Trigger the following commands whenever a country is liberated in a
    peace conference only
    .
    ```
  - Example:
    ```text
    on_liberate = {
        effect = { … }
    }
    ```
  - Notes: ROOT is the nation being liberated, FROM is the leader of the liberators.
  - Version Added: 1.0

- **on_release_as_free**
  - Description: Trigger the following commands whenever a country is released.
  - Example:
    ```text
    on_release_as_free = {
        effect = { … }
    }
    ```
  - Notes: #ROOT is free nation FROM is releaser.
  - Version Added: 1.3

- **on_release_as_puppet**
  - Description: Trigger the following commands whenever puppeting through the occupied territories menu during peace time (or when releasing from non-core but owned territory).
  - Example:
    ```text
    on_release_as_puppet = {
        effect = { … }
    }
    ```
  - Notes: ROOT is the nation being released, FROM is the overlord.
  - Version Added: 1.3

- **on_guarantee**
  - Description: Trigger the following commands whenever a country guarantees independence of another country.
  - Notes: ROOT is the country which guarantees, FROM is the country that is guaranteed.

- **on_military_access**
  - Description: Trigger the following commands whenever a country accepts the request for military access.
  - Notes: ROOT is the country which requested, FROM is the country that accepted.

- **on_offer_military_access**
  - Description: Trigger the following commands whenever a country accepts the offer for military access.
  - Notes: ROOT is the country which offered, FROM is the country that accepted.

- **on_call_allies**
  - Description: Trigger the following commands whenever a country accepts the call to war.
  - Notes: ROOT is the country which called, FROM is the country that joined.

- **on_join_allies**
  - Description: Trigger the following commands whenever a country joins a war of an ally.
  - Notes: ROOT is the country which joined, FROM is the country whose war was joined.

- **on_lend_lease**
  - Description: Trigger the following commands whenever a country has their lend lease accepted.
  - Notes: ROOT is the country that sent the lend lease, FROM is the country that accepted.

- **on_incoming_lend_lease**
  - Description: Trigger the following commands whenever a country accepts a requested lend lease.
  - Notes: ROOT is the country that accepted, FROM is the country that requested.

- **on_send_expeditionary_force**
  - Description: Trigger the following commands whenever a country accepts sent expeditionary forces.
  - Notes: ROOT is the country that sent, FROM is the country that accepted.

- **on_return_expeditionary_forces**
  - Description: Trigger the following commands whenever a country returns their expeditionary forces.
  - Notes: ROOT is the owner of the forces, FROM is the country where the forces were sent.

- **on_request_expeditionary_forces**
  - Description: Trigger the following commands whenever a country requests expeditionary forces.
  - Notes: ROOT is the country that requests, FROM is the target of the request.

- **on_ask_for_state_control**
  - Description: Trigger the following commands whenever a country accepts the request for control of a state.
  - Notes: ROOT is the requester, FROM is the country in control of the state.

- **on_give_state_control**
  - Description: Trigger the following commands whenever a country accepts being given control of a state.
  - Notes: ROOT is the giver, FROM is the receiver.

- **on_peace_proposal**
  - Description: Trigger the following commands whenever a country accepts a conditional surrender.
  - Notes: ROOT is sender of conditional surrender, FROM is the receiver.

- **on_send_attache**
  - Description: Triggers actions on an attache being accepted.
  - Notes: Default scope is sender, FROM = receiver

## Faction

- **on_create_faction**
  - Description: Trigger the following commands whenever a country create a faction.
  - Example:
    ```text
    on_create_faction = { effect = { … } }
    ```
  - Notes: FROM is the one that joins the faction.
  - Version Added: 1.0

- **on_faction_formed**
  - Description: Trigger the following commands when a faction is formed.
  - Example:
    ```text
    on_faction_formed = { effect = { news_event = { id = news.159 } } }
    ```
  - Version Added: 1.0

- **on_offer_join_faction**
  - Description: Trigger the following commands whenever a country joins a faction after being invited.
  - Example:
    ```text
    on_offer_join_faction = { effect = { … } }
    ```
  - Notes: FROM is the country invited, THIS and ROOT are the faction leader.
  - Version Added: 1.0

- **on_join_faction**
  - Description: Trigger the following commands for a faction leader whenever a country joins after they ask to do so.
  - Example:
    ```text
    on_join_faction = { effect = { … } }
    ```
  - Notes: FROM is faction leader, ROOT and THIS are the country that joins.
  - Version Added: 1.0

- **on_assume_faction_leadership**
  - Description: Trigger the following commands whenever a country assumes leadership of a faction.
  - Example:
    ```text
    on_assume_faction_leadership = { effect = { … } }
    ```
  - Notes: ROOT is the new faction leader FROM is the old faction leader
  - Version Added: 1.7

- **on_leave_faction**
  - Description: Trigger the following commands whenever a country leave a faction.
  - Example:
    ```text
    on_leave_faction = { effect = { if = { limit = { AND = { tag = CAN NOT = { has_dlc = "Together for Victory" } } } drop_cosmetic_tag = yes } }
    ```
  - Notes: FROM is the faction Leader, ROOT is the country leaving the faction
  - Version Added: 1.0

## Autonomy

- **on_subject_annexed**
  - Description: Trigger the following commands when a country annex a subject.
  - Example:
    ```text
    on_subject_annexed = { effect = {  …  } }
    ```
  - Notes: ROOT is the subject, FROM is the overlord.
  - Version Added: 1.0

- **on_subject_free**
  - Description: Trigger the following commands when a country grants freedom to a puppet.
  - Example:
    ```text
    on_subject_free = { effect = {  …  } }
    ```
  - Notes: ROOT is the subject, FROM is the previous overlord.
  - Version Added: 1.0

- **on_subject_autonomy_level_change**
  - Description: Trigger the following commands when the autonomy level of a puppet changes.
  - Example:
    ```text
    on_subject_autonomy_level_change = { effect = {  …  } }
    ```
  - Notes: ROOT is the subject, FROM is the overlord.
  - Version Added: 1.0

## Governments in Exile

- **on_government_exiled**
  - Description: Trigger the following commands whenever a country becomes a government in exile.
  - Example:
    ```text
    on_government_exiled = { effect = { = { … } }
    ```
  - Notes: ROOT is the government in exile, FROM is the country that is hosting the government in exile.
  - Version Added: 1.6

- **on_host_changed_from_capitulation**
  - Description: Trigger the following commands whenever a country that is hosting a government in exile has capitulated.
  - Example:
    ```text
    on_host_changed_from_capitulation= { effect = { = { … } }
    ```
  - Notes: ROOT is the government in exile, FROM is the new country hosting the government in exile, FROM:FROM is the old country that was hosting the government in exile.
  - Version Added: 1.6

- **on_exile_government_reinstated**
  - Description: Trigger the following commands whenever a country has returned from governing in exile.
  - Example:
    ```text
    on_exile_government_reinstated = { effect = { = { … } }
    ```
  - Notes: ROOT is the government in exile, FROM is the country that was hosting the government in exile.
  - Version Added: 1.6

## States

- **on_state_control_changed**
  - Description: Trigger the following commands when a state's controller changes.
  - Example:
    ```text
    on_state_control_changed = {
        effect = {
            if = {
                limit = {
                    FROM.FROM = { state = 123 }
                }
                if =  {
                    limit = {
                        tag = BHR
                    }
                    FROM.FROM = {
                        set_state_name = STATE_123_BHR
                        set_province_name = {
                            id = 1234
                            name = VICTORY_POINTS_1234_BHR
                        }
                    }
                }
                else = { # Unnested else is preferred over nested
                    FROM.FROM = {
                        reset_state_name = yes
                        reset_province_name = 1234
                    }
                }
            }
        }
    }
    ```
  - Notes: ROOT is new controller, FROM is old controller, FROM.FROM is state ID.
  - Version Added: 1.4

## Wargoals

- **on_generate_wargoal**
  - Description: Trigger the following commands whenever the country generates a wargoal.
  - Example:
    ```text
    on_generate_wargoal = {  }
    ```
  - Notes: ROOT is the wargoal owner, FROM is the wargoal target

- **on_justifying_wargoal_pulse**
  - Description: Trigger the following commands whenever the country is targeted by a wargoal under justification.
  - Example:
    ```text
    on_justifying_wargoal_pulse = { random_events = { 100 = war_justification.1 } }
    ```
  - Notes: FROM = target nation. Checked every day.
  - Version Added: 1.0

- **on_wargoal_expire**
  - Description: Trigger the following commands whenever a wargoal expire.
  - Example:
    ```text
    on_wargoal_expire = { random_events = { 100 = war_justification.301 } }
    ```
  - Notes: FROM is the wargoal owner.
  - Version Added: 1.0

## Unit Leader

- **on_unit_leader_created**
  - Description: Trigger the following commands when an army leader is created.
  - Example:
    ```text
    on_unit_leader_created = { effect = { … } }
    ```
  - Notes: FROM is owner country, ROOT is the unit leader.
  - Version Added: 1.5

- **on_army_leader_daily**
  - Description: Trigger the following commands on an army leader each day.
  - Example:
    ```text
    on_army_leader_daily = { effect = { … } }
    ```
  - Notes: FROM is owner country, ROOT is the unit leader.
  - Version Added: 1.0

- **on_army_leader_won_combat**
  - Description: Trigger the following commands whenever an army leader won a combat.
  - Example:
    ```text
    on_army_leader_won_combat = { effect = { … } }
    ```
  - Notes: FROM is owner country, ROOT is the unit leader.
  - Version Added: 1.0

- **on_army_leader_lost_combat**
  - Description: Trigger the following commands whenever an army leader lost a combat.
  - Example:
    ```text
    on_army_leader_lost_combat = { effect = { … } }
    ```
  - Notes: FROM is owner country, ROOT is the unit leader.
  - Version Added: 1.0

- **on_unit_leader_level_up**
  - Description: Trigger the following commands when a leader gain a level.
  - Example:
    ```text
    on_unit_leader_level_up = { effect = { … } }
    ```
  - Notes: FROM is owner country, ROOT is the unit leader.
  - Version Added: 1.0

- **on_army_leader_promoted**
  - Description: Trigger the following commands whenever a corps commander is promoted to a field marshal.
  - Example:
    ```text
    on_army_leader_promoted = { effect = { add_timed_unit_leader_trait = { trait = recently_promoted days = 100 } } }
    ```
  - Notes: FROM is owner country, ROOT is the unit leader.
  - Version Added: 1.0

- **on_unit_leader_promote_from_ranks_veteran**
  - Description: Triggers the following commands whenever an unit commander gets promoted to a general.
  - Example:
    ```text
    on_unit_leader_promote_from_ranks_veteran = { effect = { … } }
    ```
  - Notes: FROM is unit, OWNER is owner country, ROOT is the unit leader.
  - Version Added: 1.12

- **on_unit_leader_promote_from_ranks_green**
  - Description: Triggers the following commands whenever an unit commander gets promoted to a general.
  - Example:
    ```text
    on_unit_leader_promote_from_ranks_green = { effect = { … } }
    ```
  - Notes: FROM is unit, OWNER is owner country, ROOT is the unit leader.
  - Version Added: 1.12

## Military

- **on_nuke_drop**
  - Description: Trigger the following commands whenever a country drops a nuke.
  - Example:
    ```text
    on_nuke_drop = {
        effect = {
            set_global_flag = first_nuke_dropped
        }
    }
    ```
  - Notes: ROOT is the country that launched the nuke, FROM is the nuked state.
  - Version Added: 1.0

- **on_pride_of_the_fleet_sunk**
  - Description: Triggers when a country's pride of the fleet is sunk
  - Example:
    ```text
    on_pride_of_the_fleet_sunk = {
        effect = {
            if = {
                limit = {
                    tag = ENG
                }
                FROM = { set_country_flag = achievements_pride_and_extreme_prejudice }
            }
        }
    }
    ```
  - Notes: FROM is the killer country, ROOT is the country of that lost its pride of the fleet.
  - Version Added: 1.6

- **on_naval_invasion**
  - Description: Triggers the following commands whenever a sea invasion is made.
  - Example:
    ```text
    on_naval_invasion = {
        effect = { 
            ROOT = {    # Unlike most on_actions, ROOT isn't the default scope
                add_political_power = 100
            }
        }
    }
    ```
  - Notes: THIS (default scope) is the invaded state, ROOT is the country that invades, FROM is the state where the invasion started
  - Version Added: 1.9

- **on_paradrop**
  - Description: Triggers the following commands whenever a landing occurs.
  - Example:
    ```text
    on_paradrop = { 
        effect = {
            FROM = {
                controller = {
                    add_war_support = 0.01
                }
            }
        }
    }
    ```
  - Notes: THIS (default scope) is the invaded state, ROOT is the country that invades, FROM is the state where the invasion started
  - Version Added: 1.9

- **on_units_paradropped_in_state**
  - Description: This differs from on_paradrop in that it is run once per paradrop, not once per unit dropped.
  - Example:
    ```text
    on_paradrop = { 
        effect = {
            FROM = {
                controller = {
                    add_war_support = 0.01
                }
            }
        }
    }
    ```
  - Notes: ROOT is the state that was dropped into, FROM is the dropping country.

- **on_add_history**
  - Description: Triggers the following commands whenever receiving a history entry.
  - Example:
    ```text
    on_add_history = { effect = { … } }
    ```
  - Notes: ROOT is the unit.
  - Version Added: 1.12

## Aces

- **on_ace_promoted**
  - Description: Trigger the following commands whenever an ace is created.
  - Example:
    ```text
    on_ace_promoted = { random_events = { 100 = ace_promoted.1 } }
    ```
  - Notes: FROM = ace.
  - Version Added: 1.0

- **on_ace_killed**
  - Description: Trigger the following commands whenever an aces is killed.
  - Example:
    ```text
    on_ace_killed = { random_events = { 100 = ace_died.1 } }
    ```
  - Notes: FROM = ace.
  - Version Added: 1.0

- **on_ace_killed_on_accident**
  - Description: Trigger the following commands whenever our aces died on accident.
  - Example:
    ```text
    on_ace_killed_on_accident = { random_events = { 100 = ace_died.1 } }
    ```
  - Notes: FROM = our ace died in accident.
  - Version Added: 1.9

- **on_non_ace_killed_other_ace**
  - Description: Trigger the following commands whenever non ace killed enemy ace.
  - Example:
    ```text
    on_non_ace_killed_other_ace = { FROM = { random_events = { 100 = ace_died.1 } } }
    ```
  - Notes: FROM = enemy ace.
  - Version Added: 1.9

- **on_ace_killed_by_ace**
  - Description: Trigger the following commands whenever an aces is killed by another ace.
  - Example:
    ```text
    on_ace_killed_by_ace = { random_events = { 100 = ace_killed_by_ace.1 } }
    ```
  - Notes: FROM = our ace, PREV = enemy ace, has killed FROM.
  - Version Added: 1.0

- **on_ace_killed_other_ace**
  - Description: Trigger the following commands whenever an aces is killed by another ace (surviving ace side).
  - Example:
    ```text
    on_ace_killed_other_ace = { random_events = { 100 = ace_killed_other_ace.1 } }
    ```
  - Notes: FROM = our ace, PREV = enemy ace, killed by FROM.
  - Version Added: 1.0

- **on_aces_killed_each_other**
  - Description: Trigger the following commands whenever two aces kill each other in air duel.
  - Example:
    ```text
    on_aces_killed_each_other = { random_events = { 100 = aces_killed_each_other.1 } }
    ```
  - Notes: FROM = ace, PREV = enemy ace.
  - Version Added: 1.0

## La Résistance

- **on_operation_completed**
  - Description: Trigger the following commands whenever an operation is completed before the outcome effect is executed and the operative detection chance is rolled.
  - Example:
    ```text
    on_operation_completed = { effect = { … } }
    ```
  - Notes: THIS - the operation, ROOT - the initiating country, FROM - the target country.
  - Version Added: 1.9

- **on_operative_detected_during_operation**
  - Description: Trigger the following commands whenever an operative dies.
  - Example:
    ```text
    on_operative_death = { effect = { … } }
    ```
  - Notes: THIS - the operative, ROOT - the killer country (optional), FROM - the country the operative is operating for, FROM.FROM - operation state (will only be set if the operation has a specific selection_target).
  - Version Added: 1.9

- **on_operative_on_mission_spotted**
  - Description: Trigger the following commands whenever an operative performing an offensive mission in a country.
  - Example:
    ```text
    on_operative_on_mission_spotted = { effect = { … } }
    ```
  - Notes: THIS - the operative, FROM - the country the operative was performing its mission in, ROOT - the country the operative is operating for.
  - Version Added: 1.9

- **on_operative_captured**
  - Description: Trigger the following commands whenever an operative is captured.
  - Example:
    ```text
    on_operative_captured = { effect = { … } }
    ```
  - Notes: THIS - the operative, ROOT - the country the operative was performing its mission in, FROM - the country the operative is operating for.
  - Version Added: 1.9

- **on_operative_created**
  - Description: Trigger the following commands whenever an operative is created.
  - Example:
    ```text
    on_operative_created = { effect = { … } }
    ```
  - Notes: THIS - the operative, FROM - the country the operative is created by.
  - Version Added: 1.9.1

- **on_operative_death**
  - Description: Trigger the following commands whenever an operative dies.
  - Example:
    ```text
    on_operative_death = { effect = { … } }
    ```
  - Notes: THIS - the operative, ROOT - the killer country (optional), FROM - the country the operative is operating for.
  - Version Added: 1.9

- **on_operative_recruited**
  - Description: Trigger the following commands whenever an operative is recruited.
  - Example:
    ```text
    on_operative_recruited = { effect = { … } }
    ```
  - Notes: THIS - the operative, FROM - the country the operative is created by.
  - Version Added: 1.9.1

- **on_fully_decrypted_cipher**
  - Description: Trigger the following commands whenever a country fully decrypts cipher of a target country.
  - Example:
    ```text
    on_fully_decrypted_cipher = { effect = { … } }
    ```
  - Notes: THIS - the target country that its cipher is decrypted, FROM - the decrypter country.
  - Version Added: 1.9

- **on_activated_active_decryption_bonuses**
  - Description: Trigger the following commands whenever a country activates its active cipher bonuses against a target.
  - Example:
    ```text
    on_activated_active_decryption_bonuses = { effect = { … } }
    ```
  - Notes: THIS - the target country, FROM - the country that activates its bonuses.
  - Version Added: 1.9

## Military Industrial Organization

- **on_mio_size_increased**
  - Description: Trigger the following commands whenever a MIO increases in size (levels up).
  - Notes: ROOT is the Military Industrial Organization, FROM is the owner of the MIO country
  - Version Added: 1.13

- **on_mio_design_team_assigned_to_tech**
  - Description: Trigger the following commands whenever a MIO is assigned to technology research.
  - Notes: ROOT is the Military Industrial Organization, FROM is the owner of the MIO
  - Version Added: 1.13

- **on_mio_design_team_assigned_to_variant**
  - Description: Trigger the following commands whenever a MIO is asigned to a variant.
  - Notes: ROOT is the Military Industrial Organization, FROM is the owner of the MIO country
  - Version Added: 1.13

- **on_mio_industrial_manufacturer_assigned**
  - Description: Trigger the following commands whenever a MIO assigned to a production line.
  - Notes: ROOT is the Military Industrial Organization, FROM is the owner of the MIO
  - Version Added: 1.13

- **on_mio_industrial_manufacturer_unassigned**
  - Description: Trigger the following commands whenever a MIO is unnasigned from a production line.
  - Notes: ROOT is the Military Industrial Organization, FROM is the owner of the MIO
  - Version Added: 1.13

**[Modding](<Modding - Hearts of Iron 4 Wiki.md>)**
