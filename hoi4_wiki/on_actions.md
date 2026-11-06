# On actions

On actions are blocks that are executed when a certain action occurs, such as a country declaring war on a different country or a state changing control. On actions are stored in `/Hearts of Iron IV/common/on_actions/*.txt` files.

Each on action is a separate block within the `on_actions = { ... }` block, which is the root block of the on actions file. Each on_action has up to 2 arguments:

- `effect = { ... }` is present for every single on action, being an effect block the insides of which are executed when needed.
- `random_events = { ... }` is present for on_actions where the default scope (Same as ROOT, if not specified otherwise) is a country, such as on_new_term_election. This instantly fires a random one of the specified events within with the given weights being applied. This is done with a probability-proportional-to-size sampling approach.

Putting `0` instead of an event ID will ensure that nothing will happen if the chance lands on this.
Additionally, an event cannot be fired using `random_events = { ... }` if the event's `trigger = { ... }` block evaluates as false. In this case, each scope is treated the same as on action's: on action's FROM is treated as the event's FROM, same with FROM.FROM.
If there are multiple random_events blocks, one event will be picked from each.

Note that in terms of [Scopes](scopes.md), ROOT is the default assumed scope unless specified otherwise (in on_actions that have THIS as a separate entity from ROOT), while FROM and FROM.FROM can serve as secondary blocks that are provided in addition.

Each on action can only be executed after the game's start, ignoring any effects done within history files or the bookmark's `effects = { ... }` section that normally would trigger one, such as [set_politics](effects.md).

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

The file shape in 1.19.4.1, counted from vanilla.

- `common/on_actions/` has 17 vanilla files, `00_on_actions.txt` to `16_taog_on_actions.txt` (no `11_`; `00_testing_on_actions.txt` is one of them). Every file is one `on_actions = { ... }` block.
- Inside a hook block vanilla uses only `effect` (655 times) and `random_events` (13 times). A hook may hold both, as `on_ace_promoted` and `on_nuke_drop` do. Several `random_events` blocks in one hook each pick one event: `on_new_term_election` has several.
- Hooks with `random_events` in vanilla: `on_new_term_election`, `on_nuke_drop`, `on_justifying_wargoal_pulse`, `on_wargoal_expire` and five ace hooks. `on_justifying_wargoal_pulse` ends its list with `17000 = 0`, the "nothing happens" weight the page describes.
- The same hook is defined in many files: `on_capitulation` in 14 files, `on_state_control_changed` in 15 (16 blocks), `on_startup` in 14, `on_declare_war` in 11. Each DLC file adds its own block and none repeats another's work, so blocks from different files are additive. The additive rule held in a test: `on_startup` blocks from three mod files all ran, in file name order (a, b, c) in each of three sessions. The file names were a, b and c, so name order and load order cannot be told apart. A capitalised hook name (`ON_STARTUP`) and a capitalised effect keyword (`IF`) worked too.
- `on_startup` blocks in vanilla scope explicitly into tags (`GER = { ... }`), as the vanilla comment "Not run on a specific country." and the page's `none` default scope imply.

## General on actions

| Name | Description | Examples | Notes | Version Added |
| --- | --- | --- | --- | --- |
| on_startup | Trigger the following commands at the first day of a new game, after country selection. Doesn't work with save loading. | *(example below)* | **Has a default scope of `none`**, instead of firing for each country individually as in other Paradox games such as Europa Universalis IV. Many effects that usually can be used in any scope will not work, without manual [scoping](scopes.md) into countries, states, or elsewhere. | 1.3.3 |
| on_daily | Triggers each day for **every country separately** (performance heavy, use carefully) | *(example below)* | Useful for scripted guis and mods adding new mechanics (can increment a variable daily e.g.). **Only use scoping if you're careful to avoid duplicate effects**. This being executed for every country separately means that this is essentially equivalent to a single effect executed daily inside of every_country. e.g. `effect = { GER = { add_political_power = 1 } }` will add ~100 political power to ![Flag of Germany](media/effect_ec2e2a02fa__img1.png) Germany daily, as there being ~100 countries on the world map means that this will get executed ~100 times per day. | 1.5.2 |
| on_daily_TAG | Triggers each day for the specified country only | *(example below)* | Only runs the effects if the country exists. | 1.9 |
| on_weekly | Triggers each week for every country separately | *(example below)* | Useful for ai scripting. Runs on the beginning of the day if the num_days variable is divisible by 7. | 1.9 |
| on_weekly_TAG | Triggers each week for the specified country only | *(example below)* | Only runs the effects if the country exists. Runs on the beginning of the day if the num_days variable is divisible by 7. | 1.9 |
| on_monthly | Triggers each month for every country separately | *(example below)* |  | 1.9 |
| on_monthly_TAG | Triggers each month for the specified country only | *(example below)* | Only runs the effects if the country exists. | 1.9 |

**Example: on_startup**

```text
on_startup = {
    effect = {
        ENG = {
            news_event = { id = news_event.1 days = 31 random_days = 27 } # Fires a news event in February 1936
        }  # assuming the default start date
    }      # Scoping into ENG is necessary, since
}          # news_event is a country-scoped effect
```

**Example: on_daily**

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

**Example: on_daily_TAG**

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

**Example: on_weekly**

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

**Example: on_weekly_TAG**

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

**Example: on_monthly**

```text
on_monthly = {
    random_events = {
        1 = random_event.0
        99 = 0
    }
}
```

**Example: on_monthly_TAG**

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

Per-tag hooks, and the broken `on_weekly_BHR` example.

- The `on_weekly_BHR` example above puts its `if` directly in the hook with no `effect = { }` around it. A hook block holds `effect` or `random_events` and nothing else, so the working form is `on_weekly_BHR = { effect = { if = { ... } } }`.
- The tag in `on_daily_TAG`, `on_weekly_TAG` and `on_monthly_TAG` is a country tag written into the hook name. Vanilla defines 6 daily tags (AST, ETH, GER, ITA, SOV, SWE), 9 weekly (BUL, ECU, ETH, FIN, GER, RAJ, SOV, SWE, VEN) and 21 monthly (AFG, AUS, BUL, CHI, COG, CZE, ENG, GER, INS, JAP, LEB, MEX, NOR, PAL, PER, RAJ, SIA, SOV, SWE, SYR, USA).
- Vanilla has one generic `on_daily` (`04_mtg_on_actions.txt`, limited to naval treaty signatories), two generic `on_weekly` (`04_mtg_on_actions.txt` and `05_lar_on_actions.txt`, where AI countries with an intelligence agency run `update_operation_ai`) and two generic `on_monthly` blocks. The per-tag form is the vanilla way to run code for one country each day.
- `_documentation.md` lists `on_startup`, `on_daily`, `on_weekly`, `on_monthly` and the three `_TAG` forms, and puts `on_nuke_drop`, `on_pride_of_the_fleet_sunk`, `on_naval_invasion` and `on_paradrop` in the same General group (this page files them under Military).
- `hoi4.exe` contains the message "%s is not a valid tag of on_daily", so a wrong tag in a per-tag hook name is probably reported. (unverified) An `on_daily_ZZZ` hook wrote "ZZZ is not a valid tag of on_daily" to `error.log` at load, and the hook never fired in about 13 game days.

## Politics

| Name | Description | Examples | Notes | Version Added |
| --- | --- | --- | --- | --- |
| on_stage_coup | For the non ![La Résistance](media/ai_modding_04cfcba22e__img6.png)La Résistance stage coup. Trigger the following commands whenever a coup is stage. | *(example below)* | ROOT is the country that stages the coup, FROM is the target country. | 1.0 |
| on_coup_succeeded | For the non ![La Résistance](media/ai_modding_04cfcba22e__img6.png)La Résistance stage coup. Trigger the following commands whenever a coup succeeds. | *(example below)* | ROOT is the country that coup succeeded in, FROM is the stager of the coup | 1.0 |
| on_government_change | Trigger the following commands whenever a country switches its government. | `on_government_change = { effect = {  …  } }` | This includes `set_politics` and `start_civil_war` (always for both sides) and excludes being puppeted. Will always also trigger on_ruling_party_change. | 1.0 |
| on_ruling_party_change | Trigger the following commands whenever a country switches its ideology. | `on_ruling_party_change = { effect = {  …  } }` | `old_ideology_token` is a [temporary variable](data_structures.md#variable-types) that stores the old ideology as a token. Alongside what triggers on_government_change, also includes being puppeted or changing the ideology via a console command. | 1.9 |
| on_new_term_election | Trigger the following commands whenever an election happens or is called by the **hold_election** command. | `on_new_term_election = { random_events = { 100 = usa.6 } }` |  | 1.0 |
| on_before_peace_conference_start | Trigger the following commands after capitulation but before a peace conference starts. | `on_before_peace_conference_start = { effect = { … } }` | ROOT is winner, FROM is loser (called for all winners against all losers). | 1.15.2 |
| on_peaceconference_ended | Trigger the following commands whenever a peace conference ends. | `on_peaceconference_ended = { effect = { … } }` | ROOT is the winner, FROM is the loser. Is also triggered by the [white_peace](effects.md) effect is used or when a conditional surrender is accepted. | 1.5 |
| on_peaceconference_started | Trigger the following commands whenever a peace conference starts. | `on_peaceconference_started = { effect = { … } }` | ROOT is the winner, FROM is the loser. Is also triggered by the [white_peace](effects.md) effect is used or when a conditional surrender is accepted. | 1.12.3 |

**Example: on_stage_coup**

```text
on_stage_coup = {
    effect = {
    }
}
```

**Example: on_coup_succeeded**

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

Politics hooks against the documentation and vanilla.

- `on_stage_coup` has no block in any vanilla file and is not in the documentation list. The documented politics hooks are `on_coup_succeeded`, `on_government_change`, `on_ruling_party_change`, `on_ruling_party_change_immediate`, `on_new_term_election` and the three peace conference hooks. Whether `on_stage_coup` exists in the engine is unverified; do not build on it.
- `on_ruling_party_change_immediate` is listed as deprecated ("unsafe behavior, prefer using on_ruling_party_change"). No vanilla block uses it.
- `on_peaceconference_ended` has two scope descriptions in vanilla: "ROOT is winner #FROM is loser" in `03_wtt`, `04_mtg`, `05_lar`, `08_bba` and `14_sea` (the last two phrase it as "ROOT is the winner, FROM is the loser"), and "ROOT - country that just went to peace" in `00_on_actions.txt` and `07_nsb`. The documentation says ROOT is the winner and FROM the loser, called for every winner and loser pair. Log both scopes before relying on one.
- `on_new_term_election` is commented "# country": ROOT is the country that holds the election.

## Diplomacy/War

| Name | Description | Examples | Notes | Version Added |
| --- | --- | --- | --- | --- |
| on_send_volunteers | Trigger the following commands whenever a country send volunteers to another. | *(example below)* | ROOT is sender, FROM is receiver. | 1.9 |
| on_border_war_lost | Trigger the following commands whenever a country loses a border war. | *(example below)* | "Border war" refers to the state-based border wars enabled with [set_border_war](effects.md), represented with orange stripes over the state, rather than border wars that simulate combat between countries. The default scope is the state that lost the border war. | 1.0 |
| on_war_relation_added | fired when two countries end up at war with each other (on_war is fired when a country goes to war against anyone and is not fired again when it enters war against another country unless it went to peace first) | *(example below)* | ROOT is attacker, FROM is defender | 1.9.3 |
| on_declare_war | Trigger the following commands whenever a country declares war. | *(example below)* | FROM is war target. ROOT is for the country who is declaring war | 1.0 |
| on_war | Trigger the following commands whenever a country has just entered a state of war from initially being at peace. | *(example below)* | THIS is country that has just gotten into a war. | 1.7 |
| on_peace | Trigger the following commands whenever a country is no longer at war. | *(example below)* | THIS is country that is no longer at war. | 1.7 |
| on_capitulation | Trigger the following commands whenever a country capitulates, in the middle of the process. | *(example below)* | ROOT is capitulated country, FROM is winner. Several processes such as the deletion of units and transfer of equipment have already been executed by this point. | 1.0 |
| on_capitulation_immediate | Trigger the following commands whenever a country capitulates, at the beginning of the process. | *(example below)* | ROOT is capitulated country, FROM is winner. | 1.11.5 |
| on_uncapitulation | Trigger the following commands whenever a country that was previously capitulated changes its status to no longer having capitulated. | *(example below)* | ROOT is the country affected. | 1.4 |
| on_annex | Trigger the following commands whenever a country is annexed. | *(example below)* | ROOT is winner, FROM gets annexed. For civil wars **on_civil_war_end** is also fired. | 1.3.3 |
| on_civil_war_end_before_annexation | Trigger the following commands just before FROM gets annexed, meaning the country and everything it owns still exists. | *(example below)* | ROOT is winner, FROM gets annexed. It will also fire **on_annex** and **on_civil_war_end**. | 1.6 |
| on_civil_war_end | Trigger the following commands whenever a civil war ends. | *(example below)* | ROOT is civil war winner, FROM gets annexed. This will also fire **on_annex**. | 1.0 |
| on_puppet | Trigger the following commands whenever a country is puppeted in a **peace conference only**. | *(example below)* | ROOT is the nation being puppeted, FROM is the overlord. | 1.0 |
| on_liberate | Trigger the following commands whenever a country is liberated in a **peace conference only**. | *(example below)* | ROOT is the nation being liberated, FROM is the leader of the liberators. | 1.0 |
| on_release_as_free | Trigger the following commands whenever a country is released. | *(example below)* | #ROOT is free nation FROM is releaser. | 1.3 |
| on_release_as_puppet | Trigger the following commands whenever puppeting through the occupied territories menu during peace time (or when releasing from non-core but owned territory). | *(example below)* | ROOT is the nation being released, FROM is the overlord. | 1.3 |
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

**Example: on_send_volunteers**

```text
on_send_volunteers = {
    effect = { … }
}
```

**Example: on_border_war_lost**

```text
on_border_war_lost = {
    effect = {
        owner = {
            add_ideas = lost_conflict
        }
    }
}
```

**Example: on_war_relation_added**

```text
on_war_relation_added = {
    effect = { … }
}
```

**Example: on_declare_war**

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

**Example: on_war**

```text
on_war = {
    effect = { … }
}
```

**Example: on_peace**

```text
on_peace = {
    effect = { … }
}
```

**Example: on_capitulation**

```text
on_capitulation = {
    effect = { … }
}
```

**Example: on_capitulation_immediate**

```text
on_capitulation_immediate = {
    effect = { … }
}
```

**Example: on_uncapitulation**

```text
on_uncapitulation = {
    effect = { … }
}
```

**Example: on_annex**

```text
on_annex = {
    effect = { … }
}
```

**Example: on_civil_war_end_before_annexation**

```text
on_civil_war_end_before_annexation = {
    effect = { … }
}
```

**Example: on_civil_war_end**

```text
on_civil_war_end = {
    effect = { … }
}
```

**Example: on_puppet**

```text
on_puppet = {
    effect = { … }
}
```

**Example: on_liberate**

```text
on_liberate = {
    effect = { … }
}
```

**Example: on_release_as_free**

```text
on_release_as_free = {
    effect = { … }
}
```

**Example: on_release_as_puppet**

```text
on_release_as_puppet = {
    effect = { … }
}
```

Diplomacy and war hooks against the documentation and vanilla.

- `_documentation.md` also lists `on_recall_volunteers` and `on_force_government`, which the table above lacks. No vanilla file uses either and the documentation gives no scopes, so their ROOT and FROM are unknown. `on_force_government` is also a string in `hoi4.exe`. Scopes (unverified).
- `on_call_allies` and `on_join_allies` are defined in vanilla (`12_wuw_on_actions.txt`, `16_taog_on_actions.txt`) with the scopes in the table, but are missing from the documentation list.
- Order: a vanilla comment says `on_war_relation_added` "fires in 2nd place (1st is on_declare_war)" and "is triggered ALWAYS". `on_war` fires when a country goes from peace to war and not again for later enemies.
- Thirteen hooks in this and the Politics table have no vanilla block and no documentation entry: `on_guarantee`, `on_military_access`, `on_offer_military_access`, `on_lend_lease`, `on_incoming_lend_lease`, `on_send_expeditionary_force`, `on_return_expeditionary_forces`, `on_request_expeditionary_forces`, `on_ask_for_state_control`, `on_give_state_control`, `on_peace_proposal`, `on_send_attache` (here) and `on_stage_coup` (Politics). Their scopes in the table cannot be checked. `hoi4.exe` has the bare names of several (for example `send_attache`, `peace_proposal`) but not the full `on_` strings, and it also lacks the full string for vanilla hooks such as `on_declare_war`, so that proves nothing. Test a hook with a `log` effect before relying on it. Whether the engine knows these hooks is unverified.

## Faction

| Name | Description | Examples | Notes | Version Added |
| --- | --- | --- | --- | --- |
| on_create_faction | Trigger the following commands whenever a country create a faction. | `on_create_faction = { effect = { … } }` | FROM is the one that joins the faction. | 1.0 |
| on_faction_formed | Trigger the following commands when a faction is formed. | `on_faction_formed = { effect = { news_event = { id = news.159 } } }` |  | 1.0 |
| on_offer_join_faction | Trigger the following commands whenever a country joins a faction after being invited. | `on_offer_join_faction = { effect = { … } }` | FROM is the country invited, THIS and ROOT are the faction leader. | 1.0 |
| on_join_faction | Trigger the following commands for a faction leader whenever a country joins after they ask to do so. | `on_join_faction = { effect = { … } }` | FROM is faction leader, ROOT and THIS are the country that joins. | 1.0 |
| on_assume_faction_leadership | Trigger the following commands whenever a country assumes leadership of a faction. | `on_assume_faction_leadership = { effect = { … } }` | ROOT is the new faction leader FROM is the old faction leader | 1.7 |
| on_leave_faction | Trigger the following commands whenever a country leave a faction. | `on_leave_faction = { effect = { if = { limit = { AND = { tag = CAN NOT = { has_dlc = "Together for Victory" } } } drop_cosmetic_tag = yes } }` | FROM is the faction Leader, ROOT is the country leaving the faction | 1.0 |

Joining a faction has two hooks, and vanilla comments say which one fires for `add_to_faction`.

- `on_join_faction`: "THIS DOES NOT FIRE ON ADD_TO_FACTION EFFECT! USE ON_OFFER_JOIN_FACTION!" (comment on the hook in seven vanilla files). ROOT is the joining country and FROM the faction leader.
- `on_offer_join_faction`: ROOT (and THIS) is the faction leader and FROM the country invited. A vanilla comment says it also fires when the invited country actually joins and for the `add_to_faction` effect.

## Autonomy

| Name | Description | Examples | Notes | Version Added |
| --- | --- | --- | --- | --- |
| on_subject_annexed | Trigger the following commands when a country annex a subject. | `on_subject_annexed = { effect = {  …  } }` | ROOT is the subject, FROM is the overlord. | 1.0 |
| on_subject_free | Trigger the following commands when a country grants freedom to a puppet. | `on_subject_free = { effect = {  …  } }` | ROOT is the subject, FROM is the previous overlord. | 1.0 |
| on_subject_autonomy_level_change | Trigger the following commands when the autonomy level of a puppet changes. | `on_subject_autonomy_level_change = { effect = {  …  } }` | ROOT is the subject, FROM is the overlord. | 1.0 |

`16_taog_on_actions.txt` defines `on_subject_annex`, without the final "ed". The documented hook is `on_subject_annexed`, and `hoi4.exe` has only that spelling. The Indonesia block under the misspelled name therefore probably never runs, and nothing seen here reports a wrong hook name. The failure is unverified.

## Governments in Exile

| Name | Description | Examples | Notes | Version Added |
| --- | --- | --- | --- | --- |
| on_government_exiled | Trigger the following commands whenever a country becomes a government in exile. | `on_government_exiled = { effect = { = { … } }` | ROOT is the government in exile, FROM is the country that is hosting the government in exile. | 1.6 |
| on_host_changed_from_capitulation | Trigger the following commands whenever a country that is hosting a government in exile has capitulated. | `on_host_changed_from_capitulation= { effect = { = { … } }` | ROOT is the government in exile, FROM is the new country hosting the government in exile, FROM:FROM is the old country that was hosting the government in exile. | 1.6 |
| on_exile_government_reinstated | Trigger the following commands whenever a country has returned from governing in exile. | `on_exile_government_reinstated = { effect = { = { … } }` | ROOT is the government in exile, FROM is the country that was hosting the government in exile. | 1.6 |

## States

| Name | Description | Examples | Notes | Version Added |
| --- | --- | --- | --- | --- |
| on_state_control_changed | Trigger the following commands when a state's controller changes. | *(example below)* | ROOT is new controller, FROM is old controller, FROM.FROM is state ID. | 1.4 |

**Example: on_state_control_changed**

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

`on_state_control_changed` is defined in 15 vanilla files, 13 of them with a comment such as "ROOT is new controller #FROM is old controller #FROM.FROM is state ID". FROM.FROM is a state scope: vanilla runs `FROM.FROM = { state = 36 }` and `FROM.FROM = { is_core_of = FRA }` inside it.

`hoi4.exe` also contains `on_state_owner_changed` (next to the strings " NewOwner:" and " NewController:") but neither the documentation nor any vanilla file uses it. Do not rely on it. The exe string is unverified.

## Wargoals

| Name | Description | Examples | Notes | Version Added |
| --- | --- | --- | --- | --- |
| on_generate_wargoal | Trigger the following commands whenever the country generates a wargoal. | `on_generate_wargoal = {  }` | ROOT is the wargoal owner, FROM is the wargoal target |  |
| on_justifying_wargoal_pulse | Trigger the following commands whenever the country is targeted by a wargoal under justification. | `on_justifying_wargoal_pulse = { random_events = { 100 = war_justification.1 } }` | FROM = target nation. Checked every day. | 1.0 |
| on_wargoal_expire | Trigger the following commands whenever a wargoal expire. | `on_wargoal_expire = { random_events = { 100 = war_justification.301 } }` | FROM is the wargoal owner. | 1.0 |

`on_generate_wargoal` has no vanilla block and no line in `_documentation.md`; `hoi4.exe` does contain that name as a string. The exe string and the scopes in the row above are unverified.

`on_justifying_wargoal_pulse` is commented "during justifying wargoals; triggered daily, so make sure there is a sink somewhere not firing events; country, FROM = target nation". Vanilla fires `war_justification.1` to `war_justification.19` from it with a `17000 = 0` sink. `on_wargoal_expire` fires `war_justification.301`.

## Unit Leader

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

Unit leader hooks missing from the table.

- `on_navy_leader_won_combat` and `on_navy_leader_lost_combat` are documented and exist in vanilla (`00_on_actions.txt` empty, `14_sea_on_actions.txt` with content). Scopes: "THIS is the admiral, From is owner country, FromFrom is the combatant".
- `on_deployed_leader_defeated` is documented. Vanilla runs it in the defeated leader's scope with FROM as the winning country: if `can_be_captured = yes` it does `capture_by = FROM`, otherwise it adds the `wounded` trait for 90 days.
- `on_unit_leader_level_up` also has `FROM.FROM`: the original owner for exiled leaders.
- `on_unit_leader_promote_from_ranks_veteran` and `_green` exist only in vanilla (not in the documentation list). The vanilla comment reads "Unit leader scope, FROM is unit".

## Military

| Name | Description | Examples | Notes | Version Added |
| --- | --- | --- | --- | --- |
| on_nuke_drop | Trigger the following commands whenever a country drops a nuke. | *(example below)* | ROOT is the country that launched the nuke, FROM is the nuked state. | 1.0 |
| on_pride_of_the_fleet_sunk | Triggers when a country's pride of the fleet is sunk | *(example below)* | FROM is the killer country, ROOT is the country of that lost its pride of the fleet. | 1.6 |
| on_naval_invasion | Triggers the following commands whenever a sea invasion is made. | *(example below)* | THIS (default scope) is the invaded state, ROOT is the country that invades, FROM is the state where the invasion started | 1.9 |
| on_paradrop | Triggers the following commands whenever a landing occurs. | *(example below)* | THIS (default scope) is the invaded state, ROOT is the country that invades, FROM is the state where the invasion started | 1.9 |
| on_units_paradropped_in_state | This differs from on_paradrop in that it is run once per paradrop, not once per unit dropped. | *(example below)* | ROOT is the state that was dropped into, FROM is the dropping country. |  |
| on_add_history | Triggers the following commands whenever receiving a history entry. | `on_add_history = { effect = { … } }` | ROOT is the unit. | 1.12 |

**Example: on_nuke_drop**

```text
on_nuke_drop = {
    effect = {
        set_global_flag = first_nuke_dropped
    }
}
```

**Example: on_pride_of_the_fleet_sunk**

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

**Example: on_naval_invasion**

```text
on_naval_invasion = {
    effect = {
        ROOT = {    # Unlike most on_actions, ROOT isn't the default scope
            add_political_power = 100
        }
    }
}
```

**Example: on_paradrop**

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

**Example: on_units_paradropped_in_state**

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

The "Example: on_units_paradropped_in_state" above repeats the `on_paradrop` example, with the wrong hook name. The vanilla block is `on_units_paradropped_in_state`, commented "root is the state that was dropped into; from is the dropping country; this differs from on_paradrop in that it is run once per paradrop, not once per unit dropped".

`on_naval_invasion` and `on_paradrop` match their vanilla comments: ROOT is the invading country, the default scope is the invaded state and FROM is the state where the invasion started. `on_add_history` is commented "Unit Scope". Neither `on_units_paradropped_in_state` nor `on_add_history` is in the documentation list.

## Aces

| Name | Description | Examples | Notes | Version Added |
| --- | --- | --- | --- | --- |
| on_ace_promoted | Trigger the following commands whenever an ace is created. | `on_ace_promoted = { random_events = { 100 = ace_promoted.1 } }` | FROM = ace. | 1.0 |
| on_ace_killed | Trigger the following commands whenever an aces is killed. | `on_ace_killed = { random_events = { 100 = ace_died.1 } }` | FROM = ace. | 1.0 |
| on_ace_killed_on_accident | Trigger the following commands whenever our aces died on accident. | `on_ace_killed_on_accident = { random_events = { 100 = ace_died.1 } }` | FROM = our ace died in accident. | 1.9 |
| on_non_ace_killed_other_ace | Trigger the following commands whenever non ace killed enemy ace. | `on_non_ace_killed_other_ace = { FROM = { random_events = { 100 = ace_died.1 } } }` | FROM = enemy ace. | 1.9 |
| on_ace_killed_by_ace | Trigger the following commands whenever an aces is killed by another ace. | `on_ace_killed_by_ace = { random_events = { 100 = ace_killed_by_ace.1 } }` | FROM = our ace, PREV = enemy ace, has killed FROM. | 1.0 |
| on_ace_killed_other_ace | Trigger the following commands whenever an aces is killed by another ace (surviving ace side). | `on_ace_killed_other_ace = { random_events = { 100 = ace_killed_other_ace.1 } }` | FROM = our ace, PREV = enemy ace, killed by FROM. | 1.0 |
| on_aces_killed_each_other | Trigger the following commands whenever two aces kill each other in air duel. | `on_aces_killed_each_other = { random_events = { 100 = aces_killed_each_other.1 } }` | FROM = ace, PREV = enemy ace. | 1.0 |

`on_aces_killed_each_other` fires twice, once for each ace, so ROOT and FROM swap between the two calls. `on_ace_killed_on_accident` and `on_non_ace_killed_other_ace` are empty blocks in vanilla.

## La Résistance

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

Two rows above are wrong against the vanilla scope comments.

- `on_operative_on_mission_spotted`: ROOT is the country the operative was performing its mission in, and FROM is the country the operative is operating for. The row has them the other way round. THIS is the operative.
- `on_operative_detected_during_operation` is a different hook from `on_operative_death`; the row and the example above describe the death hook. In vanilla the scope is the operative and the block runs `capture_operative = { captured_by = FROM }` and `kill_operative = { killed_by = FROM }`, so FROM is the country that detected the operative. `FROM.FROM` is the operation's state, set only when the operation has a `selection_target`.

`on_operative_created` and `on_operative_recruited` are documented but have no vanilla block. The other rows match their vanilla comments.

## Military Industrial Organization

| Name | Description | Examples | Notes | Version Added |
| --- | --- | --- | --- | --- |
| on_mio_size_increased | Trigger the following commands whenever a MIO increases in size (levels up). |  | ROOT is the Military Industrial Organization, FROM is the owner of the MIO country | 1.13 |
| on_mio_design_team_assigned_to_tech | Trigger the following commands whenever a MIO is assigned to technology research. |  | ROOT is the Military Industrial Organization, FROM is the owner of the MIO | 1.13 |
| on_mio_design_team_assigned_to_variant | Trigger the following commands whenever a MIO is asigned to a variant. |  | ROOT is the Military Industrial Organization, FROM is the owner of the MIO country | 1.13 |
| on_mio_industrial_manufacturer_assigned | Trigger the following commands whenever a MIO assigned to a production line. |  | ROOT is the Military Industrial Organization, FROM is the owner of the MIO | 1.13 |
| on_mio_industrial_manufacturer_unassigned | Trigger the following commands whenever a MIO is unnasigned from a production line. |  | ROOT is the Military Industrial Organization, FROM is the owner of the MIO | 1.13 |

The documentation list also names `on_mio_tech_reseach_cancelled` and `on_mio_tech_reseach_completed`, spelled "reseach". `hoi4.exe` has the same misspelling. Vanilla's `09_aat_on_actions.txt` declares empty blocks under the correct spelling, `on_mio_tech_research_cancelled` and `on_mio_tech_research_completed`. Those names are not the documented hooks, so do not copy them. The exe spelling is unverified.

Each of these hooks also exists at MIO level without the `mio_` part (`on_design_team_assigned_to_tech`, `on_design_team_assigned_to_variant`, `on_industrial_manufacturer_assigned`, `on_industrial_manufacturer_unassigned`, `on_tech_research_cancelled`, `on_tech_research_completed`). Use the on action for code that applies to any MIO and the MIO-level hook for one organization.

## Special Projects

| Name | Description | Examples | Notes | Version Added |
| --- | --- | --- | --- | --- |
| on_project_completion | Triggered when a project is completed | on_project_completion = { effect = { #achievement check  IF = {  limit = {  ROOT = { original_tag = BEL }  }  add_to_variable = { BEL.special_projects_completed = 1 }  }  }  } | ROOT Tag FROM Project | 1.15 |

`on_project_completion` is defined only in `12_wuw_on_actions.txt` (an achievement counter for Belgium and a flag for the US AI) with the comment "ROOT Tag FROM Project", which matches the row. It is not in `_documentation.md`.

## Hook inventory for 1.19.4.1

Where each hook name on this page comes from. Vanilla has 121 distinct hook names in 346 blocks: 85 general names and 36 per-tag names. `_documentation.md` lists 84 names: 74 have a vanilla block under that exact name, the three `_TAG` forms have the 36 per-tag names, and 7 have no vanilla block (first row below).

| Group | Names | Source |
| --- | --- | --- |
| Documented, no vanilla block | `on_force_government`, `on_mio_tech_reseach_cancelled`, `on_mio_tech_reseach_completed`, `on_operative_created`, `on_operative_recruited`, `on_recall_volunteers`, `on_ruling_party_change_immediate` (deprecated) | |
| Vanilla block, not documented | `on_add_history`, `on_call_allies`, `on_join_allies`, `on_project_completion`, `on_unit_leader_promote_from_ranks_green`, `on_unit_leader_promote_from_ranks_veteran`, `on_units_paradropped_in_state` | |
| Vanilla names that look like typos | `on_subject_annex`, `on_mio_tech_research_cancelled`, `on_mio_tech_research_completed` | |
| Wiki tables only | `on_stage_coup`, `on_guarantee`, `on_military_access`, `on_offer_military_access`, `on_lend_lease`, `on_incoming_lend_lease`, `on_send_expeditionary_force`, `on_return_expeditionary_forces`, `on_request_expeditionary_forces`, `on_ask_for_state_control`, `on_give_state_control`, `on_peace_proposal`, `on_send_attache`, `on_generate_wargoal` | Existence in the engine (unverified) |
| Strings in `hoi4.exe` only | `on_state_owner_changed`, `on_become_faction_member` | The exe strings (unverified) |

`13_goe_on_actions.txt` writes the hook `ON_OFFER_JOIN_FACTION` and the effect `IF` in capitals, so vanilla uses both spellings. Name matching is therefore probably case-insensitive. (unverified)

Use the documented and vanilla names. Treat the last two groups as unconfirmed until a test run shows the hook firing with a `log` effect.
