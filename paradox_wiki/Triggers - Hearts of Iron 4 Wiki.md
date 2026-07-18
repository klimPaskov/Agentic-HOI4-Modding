# Table of contents

- [Operators](#operators)
- [Context scopes](#context-scopes)
- [Scopes](#scopes)
  - [Trigger scopes](#trigger-scopes)
  - [Dual scopes](#dual-scopes)
- [Flow control tools](#flow-control-tools)
- [Any scope](#any-scope)
  - [General](#general)
  - [Career profile](#career-profile)
  - [Variables](#variables)
  - [Debugging](#debugging)
- [Country scope](#country-scope)
  - [General](#general_2)
  - [National focuses](#national-focuses)
  - [Politics](#politics)
  - [Balance of power](#balance-of-power)
  - [Buildings](#buildings)
  - [Technology](#technology)
  - [Ideas](#ideas)
  - [Diplomacy](#diplomacy)
  - [Faction](#faction)
  - [War](#war)
  - [State](#state)
  - [Military](#military)
  - [Doctrine](#doctrine)
  - [Equipment](#equipment)
  - [Intelligence](#intelligence)
  - [AI](#ai)
  - [Characters](#characters)
  - [Peace conferences](#peace-conferences)
- [Faction scope](#faction-scope)
- [State scope](#state-scope)
  - [General](#general_3)
  - [Resistance and Compliance](#resistance-and-compliance)
- [Character scope](#character-scope)
  - [General](#general_4)
  - [Advisors](#advisors)
  - [Country leaders](#country-leaders)
  - [Unit leaders](#unit-leaders)
  - [Operatives](#operatives)
  - [Scientists](#scientists)
- [Combat](#combat)
- [Division scope](#division-scope)
- [MIO scope](#mio-scope)
- [Contract scope](#contract-scope)
- [Special projects](#special-projects)
- [Meta triggers](#meta-triggers)
- [Scripted triggers](#scripted-triggers)
  - [Diplomacy scripted triggers](#diplomacy-scripted-triggers)
  - [Resistance initiation triggers](#resistance-initiation-triggers)
  - [Useful scripted triggers](#useful-scripted-triggers)
- [References and notes](#references-and-notes)

---

**Conditions** (also known as **Triggers**) are used to check whether certain conditions are fulfilled in the game's current state or not, without being able to change anything in the game's state.<a id="ref-a"></a>[[a]](#cnote-a) These return a [boolean](http://en.wikipedia.org/wiki/Boolean_data_type) (true or false), which may be interpreted by the block where it's used. Usually blocks that allow using triggers are an [AND](#and) unless stated otherwise, which would instantly stop execution upon receiving a single false statement and return false. Please note that the `yes` and `no` inputs are case-sensitive and must not contain any uppercase letters.

The list of triggers may be outdated. A complete, but unsorted, list of triggers can be found in /Hearts of Iron IV/documentation/triggers\_documentation.html or /Hearts of Iron IV/documentation/triggers\_documentation.md. As of 1.17.1.1, this file was last updated in the version 1.17.0.

## <a id="operators"></a>Operators

Every trigger uses one of the three operators: The equality sign `=` or the comparison signs `>` and `<`.

The equality sign can either mean strict equality (Unlike previous games in the series where it checked for being equal or greater than) or can serve as a way to introduce a block of additional triggers, as in `has_opinion = { target = GRE value < -10 }`. The comparison signs serves as strict comparison: `has_political_power > 100` will not be true if the country has exactly 100 political power, for instance.

Not all triggers support the equality sign or comparison signs. See the details for each trigger in the notes for it. If not stated otherwise, the trigger only supports the equality sign.

## <a id="context-scopes"></a>Context scopes

There are three general scopes all triggers operate in:

- country
- state
- character

They give context to a trigger by stating what the trigger is checking against.

Each country acts as a sub-scope of the general country scope, i.e. `GER = { }` will check only against Germany, whereas `any_country` will check against all countries. Likewise for states and characters.

Triggers won't work in scopes they are not assigned to. Country triggers will not work for states or vice-versa.

## <a id="scopes"></a>Scopes

*Main article: [Scopes](<Scopes - Hearts of Iron 4 Wiki.md>)*

These don't serve as triggers, but rather as scopes that change for whom the triggers are being checked. Each one also serves as an [AND statement](#and).

### <a id="trigger-scopes"></a>Trigger scopes

These can only be used as triggers; trying to use them as [effects](<Effects - Hearts of Iron 4 Wiki.md>) will result in nothing happening.

Trigger scopes:
| Name | Usage | Target type | Example | Description | Version Added |
| --- | --- | --- | --- | --- | --- |
| <a id="all-country"></a> all\_country | Always usable | Country | `all_country = { … }` | Checks if all countries meet the triggers. | 1.0 |
| <a id="any-country"></a> any\_country | Always usable | Country | `any_country = { … }` | Checks if any country meets the triggers. | 1.0 |
| <a id="all-other-country"></a> all\_other\_country | Within country scope only | Country | `all_other_country = { … }` | Checks if all countries other than the one where this scope is located meet the triggers. | 1.0 |
| <a id="any-other-country"></a> any\_other\_country | Within country scope only | Country | `any_other_country = { … }` | Checks if any country other than the one where this scope is located meets the triggers. | 1.0 |
| <a id="all-country-with-original-tag"></a> all\_country\_with\_original\_tag | Always usable | Country | `all_country_with_original_tag = { original_tag_to_check = TAG #required … #triggers to check }` | Checks if all countries originating from the specified country, including the dynamic countries created for civil wars and other purposes, meet the triggers. `original_tag_to_check = TAG` is used to specify the original tag. | 1.9 |
| <a id="any-country-with-original-tag"></a> any\_country\_with\_original\_tag | Always usable | Country | `any_country_with_original_tag = { original_tag_to_check = TAG #required … #triggers to check }` | Checks if any country originating from the specified country, including the dynamic countries created for civil wars and other purposes, meets the triggers. `original_tag_to_check = TAG` is used to specify the original tag. | 1.9 |
| <a id="all-neighbor-country"></a> all\_neighbor\_country | Within country scope only | Country | `all_neighbor_country = { … }` | Checks if all countries that border the one where this scope is located meet the triggers. | 1.0 |
| <a id="any-neighbor-country"></a> any\_neighbor\_country | Within country scope only | Country | `any_neighbor_country = { … }` | Checks if any country that borders the one where this scope is located meets the triggers. | 1.0 |
| <a id="any-home-area-neighbor-country"></a> any\_home\_area\_neighbor\_country | Within country scope only | Country | `any_home_area_neighbor_country = { … }` | Checks if any country that borders the one where this scope is located, as well as being in its home area - meaning a direct land connection between the capitals of countries - meets the triggers. | 1.0 |
| <a id="all-guaranteed-country"></a> all\_guaranteed\_country | Within country scope only | Country | `all_guaranteed_country = { … }` | Checks if all countries that are guaranteed by the one where this scope is located meet the triggers. | 1.9 |
| <a id="any-guaranteed-country"></a> any\_guaranteed\_country | Within country scope only | Country | `any_guaranteed_country = { … }` | Checks if any country that is guaranteed by the one where this scope is located meets the triggers. | 1.9 |
| <a id="all-allied-country"></a> all\_allied\_country | Within country scope only | Country | `all_allied_country = { … }` | Checks if all countries that are allied with the one where this scope is located - meaning that they are either a subject of the country, its overlord, or that they share a faction - meet the triggers. Does not include the country itself. | 1.9 |
| <a id="any-allied-country"></a> any\_allied\_country | Within country scope only | Country | `any_allied_country = { … }` | Checks if any country that is allied with the one where this scope is located - meaning that they are either a subject of the country, its overlord, or that they share a faction - meets the triggers. Does not include the country itself. | 1.9 |
| <a id="all-occupied-country"></a> all\_occupied\_country | Within country scope only | Country | `all_occupied_country = { … }` | Checks if all countries that are occupied by the one where this scope is located - meaning that the occupied country has core states controlled by the occupier country - meet the triggers. | 1.9 |
| <a id="any-occupied-country"></a> any\_occupied\_country | Within country scope only | Country | `any_occupied_country = { … }` | Checks if any country that is occupied by the one where this scope is located - meaning that the occupied country has core states controlled by the occupier country - meets the triggers. | 1.9 |
| <a id="all-enemy-country"></a> all\_enemy\_country | Within country scope only | Country | `all_enemy_country = { … }` | Checks if all countries that are at war with the one where this scope is located meet the triggers. | 1.9 |
| <a id="any-enemy-country"></a> any\_enemy\_country | Within country scope only | Country | `any_enemy_country = { … }` | Checks if any country that are at war with the one where this scope is located meets the triggers. | 1.9 |
| <a id="all-subject-countries"></a> all\_subject\_countries | Within country scope only | Country | `all_subject_countries = { … }` | Checks if all countries that are a subject of the one where this scope is located meet the triggers. Notice the plural spelling in the scope. | 1.11 |
| <a id="any-subject-country"></a> any\_subject\_country | Within country scope only | Country | `any_subject_country = { … }` | Checks if any country that is a subject of the one where this scope is located meets the triggers. | 1.11 |
| <a id="any-country-with-core"></a> any\_country\_with\_core | Within state scope only | Country | `any_country_with_core = { … }` | Checks if any country that has the current scope as a core state meets the triggers. **Does not have an equivalent for other effect/trigger scope types.** | 1.12 |
| <a id="all-country-of"></a> all\_country\_of | Alway usable | Country | `all_country_of = { tooltip = my_loc # Optional bindable localization target = { SWE NOR FIN DEN ICE } has_defensive_war = yes } all_country_of = { tooltip = my_loc # Optional bindable localization target = constant:country_groups:nordics has_defensive_war = yes }` | Checks if all of the provided countries fulfill the specified triggers. The `target` supports script constants and `tooltip` supports bindable localization. | 1.17 |
| <a id="any-country-of"></a> any\_country\_of | Alway usable | Country | `any_country_of = { tooltip = my_loc # Optional bindable localization target = { SWE NOR FIN DEN ICE } has_defensive_war = yes } any_country_of = { tooltip = my_loc # Optional bindable localization target = constant:country_groups:nordics has_defensive_war = yes }` | Checks if any of the provided countries fulfills the specified triggers. The `target` supports script constants and `tooltip` supports bindable localization. | 1.17 |
| <a id="all-state"></a> all\_state | Always usable | State | `all_state = { … }` | Check if all states meet the triggers. | 1.0 |
| <a id="any-state"></a> any\_state | Always usable | State | `any_state = { … }` | Check if any state meets the triggers. | 1.0 |
| <a id="any-state-in"></a> any\_state\_in | Always usable | State | `any_state_in = { array = array_of_states #required … #triggers to check }`  Requires on of the following fields  `array = <array_of_states> continent = <continent_name> ai_area = <ai_area_name> strategic_region = <strategic_region_number>` | Check if any state in the given category meets the trigger. | 1.15 |
| <a id="any-state-of"></a> any\_state\_of | Alway usable | State | `any_state_of = { tooltip = my_loc # Optional bindable localization target = { 1 42 1992 } controller = { has_defensive_war = yes } } any_state_of = { tooltip = my_loc # Optional bindable localization target = constant:country_groups:nordics controller = { has_defensive_war = yes } }` | Checks if any of the provided states fulfills the specified triggers. The `target` supports script constants and `tooltip` supports bindable localization. | 1.17 |
| <a id="all-neighbor-state"></a> all\_neighbor\_state | Within state scope only | State | `all_neighbor_state = { … }` | Check if all states that are neighbour to the one where this scope is located meet the triggers. | 1.0 |
| <a id="any-neighbor-state"></a> any\_neighbor\_state | Within state scope only | State | `any_neighbor_state = { … }` | Check if any state that is neighbour to the one where this scope is located meets the triggers. | 1.0 |
| <a id="all-owned-state"></a> all\_owned\_state | Within country scope only | State | `all_owned_state = { … }` | Check if all states that are owned by the country where this scope is located meet the triggers. | 1.0 |
| <a id="any-owned-state"></a> any\_owned\_state | Within country scope only | State | `any_owned_state = { … }` | Check if any state that is owned by the country where this scope is located meets the triggers. | 1.0 |
| <a id="all-core-state"></a> all\_core\_state | Within country scope only | State | `all_core_state = { … }` | Check if any state that is cored by the country where this scope is located meets the triggers. | 1.11 |
| <a id="any-core-state"></a> any\_core\_state | Within country scope only | State | `any_core_state = { … }` | Check if all states that are cored by the country where this scope is located meet the triggers. | 1.11 |
| <a id="all-controlled-state"></a> all\_controlled\_state | Within country scope only | State | `all_controlled_state = { … }` | Check if all states that are controlled by the country where this scope is located meet the triggers. | 1.9 |
| <a id="any-controlled-state"></a> any\_controlled\_state | Within country scope only | State | `any_controlled_state = { … }` | Check if any state that is controlled by the country where this scope is located meets the triggers. | 1.9 |
| <a id="all-unit-leader"></a> all\_unit\_leader | Within country scope only | Unit Leader | `all_unit_leader = { … }` | Checks if all unit leaders (corps commanders, field marshals, admirals) that are employed by the country where this scope is located meet the triggers. | 1.5 |
| <a id="any-unit-leader"></a> any\_unit\_leader | Within country scope only | Unit Leader | `any_unit_leader = { … }` | Checks if any unit leader (corps commander, field marshal, admiral) that is employed by the country where this scope is located meets the triggers. | 1.5 |
| <a id="all-army-leader"></a> all\_army\_leader | Within country scope only | Unit Leader | `all_army_leader = { … }` | Checks if all army leaders that are employed by the country where this scope is located meet the triggers. | 1.5 |
| <a id="any-army-leader"></a> any\_army\_leader | Within country scope only | Unit Leader | `any_army_leader = { … }` | Checks if any army leader that is employed by the country where this scope is located meets the triggers. | 1.5 |
| <a id="all-navy-leader"></a> all\_navy\_leader | Within country scope only | Unit Leader | `all_navy_leader = { … }` | Checks if all navy leaders that are employed by the country where this scope is located meet the triggers. | 1.5 |
| <a id="any-navy-leader"></a> any\_navy\_leader | Within country scope only | Unit Leader | `any_navy_leader = { … }` | Checks if any navy leader that is employed by the country where this scope is located meets the triggers. | 1.5 |
| <a id="all-operative-leader"></a> all\_operative\_leader | Within country scope or operations only | Operative | `all_operative_leader = { … }` | Checks if all operatives that are employed by the country where this scope is located meet the triggers. | 1.9 |
| <a id="any-operative-leader"></a> any\_operative\_leader | Within country scope or operations only | Operative | `any_operative_leader = { … }` | Checks if any operative that is employed by the country where this scope is located meets the triggers. | 1.9 |
| <a id="all-character"></a> all\_character | Within country scope only | Character | `all_character = { … }` | Checks if all characters that are recruited by the country where this scope is located meet the triggers. | 1.11 |
| <a id="any-character"></a> any\_character | Within country scope only | Character | `any_character = { … }` | Checks if any character that is recruited by the country where this scope is located meets the triggers. | 1.11 |
| <a id="any-country-division"></a> any\_country\_division | Within country scope only | Division | `any_country_division = { … }` | Checks if any division owned by the current country meets the triggers. | 1.12 |
| <a id="any-state-division"></a> any\_state\_division | Within state scope only | Division | `any_state_division = { … }` | Checks if any division within the current state meets the triggers. | 1.12 |
| <a id="all-military-industrial-organization"></a> all\_military\_industrial\_organization | Within country scope only | MIO | `all_military_industrial_organization = { … }` | Checks if all MIOs within the current country meet the conditions. | 1.13 |
| <a id="any-military-industrial-organization"></a> any\_military\_industrial\_organization | Within country scope only | MIO | `any_military_industrial_organization = { … }` | Checks if any MIO within the current country meets the conditions. | 1.13 |
| <a id="all-purchase-contract"></a> all\_purchase\_contract | Within country scope only | Purchase contract | `all_purchase_contract = { … }` | Checks if all purchase contracts within the current country meet the conditions. | 1.13 |
| <a id="any-purchase-contract"></a> any\_purchase\_contract | Within country scope only | Purchase contract | `any_purchase_contract = { … }` | Checks if any purchase contract within the current country meets the conditions. | 1.13 |
| <a id="all-scientists"></a> all\_scientists | Within country scope only | Character | `all_scientistst = { … }` | Checks if all scientists of the Country in scope matches the triggers. | 1.15 |
| <a id="any-scientist"></a> any\_scientist | Within country scope only | Character | `any_scientist = { … }` | Checks if at least one active scientist of the Country in scope matches the triggers. | 1.15 |
| <a id="all-active-scientist"></a> all\_active\_scientist | Within country scope only | Character | `all_active_scientist = { … }` | Checks if all active scientists of the Country in scope matches the triggers. | 1.15 |
| <a id="any-active-scientist"></a> any\_active\_scientist | Within country scope only | Character | `any_active_scientist = { … }` | Checks if at least one active scientist of the Country in scope matches the triggers. | 1.15 |

### <a id="dual-scopes"></a>Dual scopes

The following scopes can be used either as effect or trigger scopes; some can also be used as the right side of some effects and triggers as a target. If usage as a target is possible, it's marked within the table.

Several dual scopes may have a scope that varies depending on where it's used, such as variables, which can be set to anything.

Dual scopes:
| Name | Usage | Target type | Example | Description | Usable as target | Version Added |
| --- | --- | --- | --- | --- | --- | --- |
| <a id="tag"></a> TAG | Always usable | Country scope | `SOV = { country_event = my_event.1 }` | The country defined by the tag or tag alias. Tag aliases are defined in /Hearts of Iron IV/common/country\_tag\_aliases, as a way to refer to a specific country (such as a side in a civil war) in addition to its actual tag. If the country with the exact tag doesn't exist, but a dynamic country originating from the specified tag does, the scope will refer to the dynamic country. | ✓ | 1.0 |
| <a id="state-id"></a> <state\_id> | Always usable | State scope | `123 = { transfer_state_to = SCO }` | The state defined by this id. | ✓ | 1.0 |
| <a id="character"></a> <character> | not within Character scope | Character scope | `ENG_theodore_makhno = { set_nationality = UKR }` | On game versions prior to 1.12.8, the character must be already recruited by the country this is scoped from. | ✓ | 1.11 |
| <a id="mio"></a> mio:<MIO> | Within country scope only | MIO scope | `mio:AST_cockatoo_doe_organization = { … }` | The MIO identified by that ID as defined within the /Hearts of Iron IV/common/military\_industrial\_organization/organizations/\*.txt file. | ✓ | 1.13 |
| sp:<special\_project> | Within country scope only | Special project scope | `sp:sp_land_flamethrower_tank = { … }` | The special project identified by that ID as defined within the /Hearts of Iron IV/common/special\_projects/projects/\*.txt file. | ✓ | 1.15 |
| <a id="root"></a> ROOT | Always usable | Depends on usage | `ENG = { FRA = { GER = { declare_war_on = { target = ROOT type = annex_everything } } } } #GER declares war on ENG (if there is no scope before ENG)` | Targets the root node of the block, an inherent property of each block. Most commonly, this is the default scope: for example, ROOT [within a national focus](<National focus modding - Hearts of Iron 4 Wiki.md>) will always refer to the country doing the focus and ROOT [within a event](<Event modding - Hearts of Iron 4 Wiki.md>) will always refer to the country getting the event. However, some blocks do distinguish between the default scope and ROOT, such as [certain scripted GUI contexts](<Scripted GUI modding - Hearts of Iron 4 Wiki.md>) or [certain on actions](<On actions - Hearts of Iron 4 Wiki.md#la-r-sistance>). If a block doesn't have ROOT defined (such as [on\_startup in on actions](<On actions - Hearts of Iron 4 Wiki.md#on-startup>)), then it is impossible to use it. | ✓ | 1.0 |
| <a id="this"></a> THIS | Always usable | Depends on usage | `set_temp_variable = { target_country = THIS }` | Targets the current scope where it's used. For example, when used in [every\_state](#every-state), it will refer to the state that's currently being evaluated. Primarily useful for variables (as in the example, where omitting it wouldn't work) or for [built-in localisation commands](<Localisation - Hearts of Iron 4 Wiki.md#namespaces>), where some scope must be specified. More rarely, this may help with scope manipulation when using [PREV](#prev). Since omitting it makes no difference in how the code gets interpreted, there is little to no usage outside of these cases. | ✓ | 1.0 |
| <a id="prev"></a> PREV | Always usable | Depends on usage | `FRA = { random_country = { GER = { declare_war_on = { target = PREV type = annex_everything } } } } #Germany declares war on random_country` | Targets the scope that the current scope is contained in. Can have additional applications where the assumed default scope differs from the ROOT, such as in state events or some on\_actions. Can be chained indefinitely as PREV.PREV. **Commonly results in broken-looking tooltips**: what's shown to the player doesn't always correlate with reality.  See also: [PREV usage](<Scopes - Hearts of Iron 4 Wiki.md#prev-usage>). | ✓ | 1.0 |
| <a id="from"></a> FROM | Always usable | Depends on usage | `declare_war_on = { target = FROM type = annex_everything } FROM = { load_oob = defend_ourselves }` | Can be chained indefinitely as FROM.FROM. Used to target various hardcoded scopes inherent to the block, often a secondary scope in addition to ROOT. For example:  In [events](<Event modding - Hearts of Iron 4 Wiki.md>), this refers to the country that sent the event (i.e. if the event was fired [using an effect](<Event modding - Hearts of Iron 4 Wiki.md#effect>), then it's the ROOT scope where it was fired).  In [targeted decisions](<Decision modding - Hearts of Iron 4 Wiki.md#targeted-decisions>) or diplomacy scripted triggers, this refers to the scope that is targeted. | ✓ | 1.0 |
| <a id="overlord"></a> overlord | Within country scope only | Country scope | `overlord = { … }` | The overlord of the country if it is a subject. [Subject to the 'invalid event target' error.](<Scopes - Hearts of Iron 4 Wiki.md#invalid-event-target>) | X | 1.3 |
| <a id="faction-leader"></a> faction\_leader | Within country scope only | Country scope | `faction_leader = { add_to_faction = FROM }` | Faction leader of the faction the country is a part of. [Subject to the 'invalid event target' error.](<Scopes - Hearts of Iron 4 Wiki.md#invalid-event-target>) | X | 1.10.1 |
| <a id="owner"></a> owner | Within state, character, or combatant scope only | Country scope | `owner = { add_ideas = owns_this_state }` | In state scope, the country that owns the state. In combatant scope, the country that owns the divisions. In character scope, the country that has recruited the character. [Subject to the 'invalid event target' error](<Scopes - Hearts of Iron 4 Wiki.md#invalid-event-target>) when used for a state. | X | 1.0 |
| <a id="controller"></a> controller | Within state scope only | Country scope | `controller = { ROOT = { create_wargoal = { target = PREV type = take_state_focus generator = { 123 } } } }` | The controller of the current state. [Subject to the 'invalid event target' error.](<Scopes - Hearts of Iron 4 Wiki.md#invalid-event-target>) | X | 1.0 |
| <a id="capital-scope"></a> capital\_scope | Within country scope only | State scope | `capital_scope = { … }` | The state where the capital of the current country is located in. [Subject to the 'invalid event target' error](<Scopes - Hearts of Iron 4 Wiki.md#invalid-event-target>) in rare cases. | X | 1.0 |
| <a id="event-target"></a> event\_target:<event\_target\_key> | Always usable | Depends on usage | `event_target:my_event_target = { … }` | Saved [event target or global event target](<Data structures - Hearts of Iron 4 Wiki.md#event-targets>), with no space after the colon. [Subject to the 'invalid event target' error.](<Scopes - Hearts of Iron 4 Wiki.md#invalid-event-target>) | ✓ | 1.0 |
| <a id="var"></a> var:<variable> | Always usable | Depends on usage | `var:my_variable = { … }` `add_to_faction = my_variable` or  `add_to_faction = var:my_variable` | Variable set to a scope.  When used as a target rather than a scope, the `var:` can be omitted in most cases. | ✓ | 1.5 |

## <a id="flow-control-tools"></a>Flow control tools

*Main article: [Scopes#Flow control tools](<Scopes - Hearts of Iron 4 Wiki.md#flow-control-tools>)*

These are triggers that serve as more of a way to establish a connection in how triggers are evaluated. Each one serves as a trigger scope with additional arguments and can be used regardless of scope.

Flow control tools:
| Name | Additional parameters | Examples | Description | Notes | Version Added |
| --- | --- | --- | --- | --- | --- |
| <a id="and"></a> AND | None | `AND = { original_tag = GER has_stability > 0.5 }` | Returns false if any sub-trigger returns false, true otherwise. Evaluation stops at the first false sub-trigger. | Only necessary within [OR statements](#or) and [NOT statements](#not), as everything else is implicitly AND. | 1.0 |
| <a id="or"></a> OR | None | `OR = { original_tag = ENG original_tag = USA }` | Returns true if any sub-trigger returns true, false otherwise. Evaluation stops at the first true sub-trigger. |  | 1.0 |
| <a id="not"></a> NOT | None | `NOT = { has_stability > 0.5 has_war_support > 0.5 }` | Returns false if any sub-trigger returns true, true otherwise. Evaluation stops at the first true sub-trigger. | Equivalent to a NOR rather than a NAND. | 1.0 |
| <a id="count-triggers"></a> count\_triggers | `amount = <int>`  The amount of triggers that need to be fulfilled. | `count_triggers = { amount = 2 10 = { state_population = 100000 } 11 = { state_population = 100000 } 12 = { state_population = 100000 } }` | Sums the results of all sub-triggers (false=0, true=1) and returns true if the sum is at least `amount`. |  | 1.5 |
| <a id="if"></a> if | `limit = <trigger block>`  `else_if = <if-trigger>`  Alternative condition. Optional.  `else = <AND-trigger>`  Final alternative condition. Optional. | `if = { limit = { has_dlc = "Poland: United and Ready" } has_political_power > 100 } else_if = { limit = { has_dlc = "Waking the Tiger" } has_war_support > 0.5 } else = { always = no }` | If `limit` is true, the sub-triggers are evaluated like an AND-trigger. If `limit` is false, `else_if` blocks are tried in sequence and finally `else` (if present). *Otherwise true is returned*. | Both nested (As in inside of `if = { ... }`) and unnested (As in the example) `else` and `else_if` exist. In case of overlap, unnested is preferred. Can be useful for tooltip management: same as in effects, if the limit is unmet, nothing appears. If it is met, then the limit is hidden while the condition outside of the limit appears in the tooltip.  `if = { limit = { trigger_1 = yes } trigger_2 = yes }` is equivalent to `OR = { NOT = { trigger_1 = yes } trigger_2 = yes }`, but generates a different tooltip. | 1.0 |
| <a id="hidden-trigger"></a> hidden\_trigger | None | `hidden_trigger = { country_exists = GER }` | Hides the triggers from the tooltip shown to the player. | Also serves as an [AND statement](#and). | 1.0 |
| <a id="custom-trigger-tooltip"></a> custom\_trigger\_tooltip | `tooltip = <string>` The localisation key to use. | `custom_trigger_tooltip = { tooltip = sunrise_invasion_tt any_state = { is_owned_by = JAP is_on_continent = europe is_coastal = yes } }` | Hides the triggers from the tooltip shown to the player and instead uses the specified localisation key. | Alias for [#custom\_override\_tooltip](#custom-override-tooltip) trigger (see that trigger for more info). Kept for backward compatibility. Prefer [#custom\_override\_tooltip](#custom-override-tooltip) instead. Also supports [Localisation#Bindable\_localisation](<Localisation - Hearts of Iron 4 Wiki.md#bindable-localisation>). | 1.0 |
| <a id="custom-override-tooltip"></a> custom\_override\_tooltip | `tooltip = <string>` The localisation key to use. `not_tooltip = <string>` The localisation key to use for NOT block. Optional. | `custom_override_tooltip = { tooltip = { localization_key = GER_inner_circle_focus_in_progress_tt CHARACTER = GER_rudolf_hess FLAG_DAYS = [?GER_rally_the_industrialists_in_progress_flag:days] } not_tooltip = MY_TOOLTIP_NOT <triggers> }` | An [AND](#and) trigger that has an overriden custom tooltip. | A positive tooltip can be set with `tooltip` and the tooltip to be used inside a [NOT](#not) can be set with `not_tooltip`. If no positive tooltip is provided and the root key is a localization key (not a formatter, see formatted localization), then a negative tooltip will be generated by appending `_NOT` to the root localization for the positive tooltip. Both `tooltip` and `not_tooltip` are bindable localizations. [Can also be used as effect.](<Effects - Hearts of Iron 4 Wiki.md#custom-override-tooltip>)  Also supports [Localisation#Bindable\_localisation](<Localisation - Hearts of Iron 4 Wiki.md#bindable-localisation>). | 1.15 |

## <a id="any-scope"></a>Any scope

These triggers do not require any particular scope.

### <a id="general"></a>General

General any-scoped triggers:
| Name | Parameters | Examples | Description | Notes | Version Added |
| --- | --- | --- | --- | --- | --- |
| <a id="always"></a> always | `<bool>` Boolean. | `always = yes` | Always returns true or false. Useful for debugging. |  | 1.0 |
| <a id="has-global-flag"></a> has\_global\_flag | `<string>` The flag to check. | `has_global_flag = my_flag` | Checks if the specified flag has been set. |  | 1.0 |
| <a id="has-global-flag"></a> has\_global\_flag | `flag = <string>` The flag to check.  `value = <int>` The flag value to check for. Optional.  `date = <date>` The flag creation date to check for. Optional.  `days = <int>` The duration the flag existed for. Optional. | `has_global_flag = { flag = my_flag days > 30 date > 1936.6.1 value > 0 }` | Compares the specified flag's last set date, days since last set, and/or value. | If not set, the value comparison is `>0`. `value` is limited between -32768 and 32767. | 1.0 |
| <a id="has-dlc"></a> has\_dlc | `<string>` The DLC name to check for. | `has_dlc = "Waking the Tiger"` | Checks if the specified DLC is enabled. |  | 1.0 |
| <a id="has-start-date"></a> has\_start\_date | `<date>` The date to check for. | `has_start_date > 1950.01.01` | Checks if the specified date was the start date used for the current game. | Year.Month.Day Must use either > or < operators. | 1.0 |
| <a id="date"></a> date | `<date>` The date to check for. | `date < 1950.01.01` | Checks if the specified date against the current date. | Year.Month.Day Must use either > or < operators. | 1.0 |
| <a id="difficulty"></a> difficulty | `<int>` The difficulty value. | `difficulty > 0` | checks if the specified difficulty against the current difficulty. | Must use either > or < operators. | 1.0 |
| <a id="has-any-custom-difficulty-setting"></a> has\_any\_custom\_difficulty\_setting | `<bool>` Boolean. | `has_any_custom_difficulty_setting = yes` | Checks if any custom difficulty setting is changed from their default value. | Custom difficulty in this case refers to /Hearts of Iron IV/common/difficulty\_settings/\*.txt, used in base game to strengthen a specific country. | 1.0 |
| <a id="has-custom-difficulty-setting"></a> has\_custom\_difficulty\_setting | `<string>` The setting to check. | `has_custom_difficulty_setting = custom_diff_strong_sov` | Checks if the specified custom difficulty setting is changed from the default value. | Custom difficulty in this case refers to /Hearts of Iron IV/common/difficulty\_settings/\*.txt, used in base game to strengthen a specific country. | 1.0 |
| <a id="game-rules-allow-achievements"></a> game\_rules\_allow\_achievements | `<bool>` Boolean. | `game_rules_allow_achievements = yes` | Checks if all of the active game rule options allow achievements. |  | 1.9 |
| <a id="country-exists"></a> country\_exists | `<scope> / <variable>` The country to check. | `country_exists = GER` | Checks if the specified country currently exists in game. |  | 1.0 |
| <a id="is-ironman"></a> is\_ironman | `<bool>` Boolean. | `is_ironman = yes` | Checks if the current game is running in Ironman mode. |  | 1.0 |
| <a id="is-historical-focus-on"></a> is\_historical\_focus\_on | `<bool>` Boolean. | `is_historical_focus_on = yes` | Checks if the current game is running with Historical Focuses on. |  | 1.0 |
| <a id="is-tutorial"></a> is\_tutorial | `<bool>` Boolean. | `is_tutorial = yes` | Checks if the current game is running in Tutorial mode. |  | 1.0 |
| <a id="is-debug"></a> is\_debug | `<bool>` Boolean. | `is_debug = yes` | Checks if game is in debug mode (launched with -debug argument). |  | 1.9 |
| <a id="threat"></a> threat | `<float>` The amount to check for. | `threat > 0.5` | Checks if World Tension is above the specified amount. | Must use either > or < operators. | 1.0 |
| <a id="has-game-rule"></a> has\_game\_rule | `<string>` The game rule to check for.  `<string> / <bool>` The option to check. | `has_game_rule = { rule = GER_can_remilitarize_rhineland option = yes }` | Checks if a game rule is set to a particular option. |  | 1.5 |
| <a id="has-completed-custom-achievement"></a> has\_completed\_custom\_achievement | `mod = <mod ID>` The mod where the achievement is from.  `achievement = <achievement ID>` The name of the achievement. | `has_completed_custom_achievement = { mod = my_mod_unique_id achievement = my_achievement_token }` | Checks if the player controlling the current scope has completed the specified custom achievement. | The achievement (including the ID of the mod it's from) is defined within /Hearts of Iron IV/common/achievements/\*.txt files<a id="cite-ref-1"></a>[[1]](#cite-note-1). The achievement could be completed during a previous session, not necessarily the current one.  If the mod defining the achievement is not loaded, the trigger evaluates as false. | 1.12.5 |

### <a id="career-profile"></a>Career profile

Career profile-releated any-scoped triggers:
| Name | Parameters | Examples | Description | Notes | Version Added |
| --- | --- | --- | --- | --- | --- |
| <a id="career-profile-check-medal"></a> career\_profile\_check\_medal | `medal = <medal>` Medal to check. `???` | `career_profile_check_medal = { medal = raining_debris_medal ??? }` | Checks if the required medal is achieved and collected. | Provide no tooltip. | ??? |
| <a id="career-profile-check-ribbon"></a> career\_profile\_check\_ribbon | `ribbon = <ribbon>` Ribbon to check. `tooltip = <loc_key>` Optional. | `career_profile_check_ribbon = { ribbon = orchestra_of_boom tooltip = my_loc_key }` | Checks if the required ribbon is achieved and collected. | By default provide no tooltip. | ??? |
| <a id="career-profile-check-playthrough-ratio"></a> career\_profile\_check\_playthrough\_ratio | `frits = <variable>`  `second = <variable>`   `ratio = <int>` Ratio.  `compare = <type>` The type of comparison. | `career_profile_check_playthrough_ratio = { first = enemy_casualties second = total_own_casualties ratio = 4 compare = greater_than_or_equals }` | Compares the ratio (first/second) of two playthrough values to a number. | Provide no tooltip. Possible compare types:   - less\_than - less\_than\_or\_equals - greater\_than - greater\_than\_or\_equals - equals - not\_equals | ??? |
| <a id="career-profile-check-playthrough-value"></a> career\_profile\_check\_playthrough\_value | `{ ... }`  **OR**  `var = <variable>` Value to compare.  `value = <int>` Value to compare to.  `compare = <type>` The type of comparison. Optional.  `tooltip = <loc_key>` Optional.  `tooltip_value = <int>` Optional. | `career_profile_check_playthrough_value = { plan_landlocked_battleship > 1 plan_landlocked_carrier > 0 }`  `career_profile_check_playthrough_value = { var = deployed_airplanes_with_air_defense_gold value = 100 compare = greater_than_or_equals tooltip = CAREER_PROFILE_TRIGGER_DEPLOYED_AIRPLANES_WITH_AIR_DEFENSE tooltip_value = 100` | Compares a playthrough value to a number. | By default provide no tooltip. Possible compare types:   - less\_than - less\_than\_or\_equals - greater\_than - greater\_than\_or\_equals - equals - not\_equals | ??? |
| <a id="career-profile-check-points"></a> career\_profile\_check\_points | `value = <int>` Value to compare. `compare = <type>` The type of comparison.  `tooltip = <loc_key>` Optional. | `career_profile_check_points = { value = 5000 compare = greater_than_or_equals tooltip = CAREER_PROFILE_TRIGGER_MINED_SEA_REGIONS }` | Compares a career points value to a number. | By default provide no tooltip. Possible compare types:   - less\_than - less\_than\_or\_equals - greater\_than - greater\_than\_or\_equals - equals - not\_equals | ??? |
| <a id="career-profile-check-ratio"></a> career\_profile\_check\_ratio | Possible the same as [#career\_profile\_check\_playthrough\_ratio](#career-profile-check-playthrough-ratio). | Possible the same as [#career\_profile\_check\_playthrough\_ratio](#career-profile-check-playthrough-ratio). | Compares the ratio (first/second) of two career profile values to a number. | Possible the same as [#career\_profile\_check\_playthrough\_ratio](#career-profile-check-playthrough-ratio). | ??? |
| <a id="career-profile-check-value"></a> career\_profile\_check\_value | Possible the same as [#career\_profile\_check\_playthrough\_value](#career-profile-check-playthrough-value). | Possible the same as [#career\_profile\_check\_playthrough\_value](#career-profile-check-playthrough-value). | Compares a career profile value to a number. | Possible the same as [#career\_profile\_check\_playthrough\_value](#career-profile-check-playthrough-value). | ??? |
| <a id="career-profile-has-player-flag"></a> career\_profile\_has\_player\_flag | `<string>` The flag to check. | `career_profile_has_player_flag = career_profile_overrun_infantry_flag` | Checks if the flag is set for the local player. |  | ??? |

### <a id="variables"></a>Variables

Variable-related triggers:
| Name | Parameters | Examples | Description | Notes | Version Added |
| --- | --- | --- | --- | --- | --- |
| <a id="has-variable"></a> has\_variable | `<variable>` The variable to check. | `has_variable = my_var` | Checks if the specified variable exists for the current scope. |  | 1.5 |
| <a id="check-variable"></a> check\_variable | `var = <variable>` The variable to check.  `value = <float> / <variable>` The value to check for.  `compare = <type>` The type of comparison. Optional, can use < or > instead. | `check_variable = { var = my_var value = 10 compare = greater_than_or_equals }`  `check_variable = { my_var > 10 }` | Check the specified variable for the current scope. | Possible compare types:  - less\_than - less\_than\_or\_equals - greater\_than - greater\_than\_or\_equals - equals - not\_equals | 1.5 |

Remember that variables need to refer to the scope they were set in. This means you can't check a country variable in a state scope without scoping the variable.

For example, to get the country variable whilst in a state scope, you'd do the following:

```text
<country> = {
    <state> = {
        limit = {
            check_variable = { from.my_country_var > 0.0 }
        }
    }
}
```

See Variables for more information.

### <a id="debugging"></a>Debugging

These are usable as both effects and triggers and are used for debugging, with the player never seeing them.

Debugging-helpful triggers:
| Name | Parameters | Examples | Description | Notes | Version Added |
| --- | --- | --- | --- | --- | --- |
| <a id="log"></a> log | `<string>` What to log. Supports dynamic localisation. | `log = "Added [?temp_add] to [THIS.GetTag]'s variable [?THIS.varvalue]"` | Appends an entry into the game.log and, if open, the console when evaluating the trigger. | game.log is stored within /Hearts of Iron IV/logs/ in the [user directory](<Modding - Hearts of Iron 4 Wiki.md>) | 1.5 |
| <a id="print-variables"></a> print\_variables | `print_global = <bool>` Print global variables. Defaults to `no`.  `var_list = <list>` The variables to print. Defaults to all variables.  `file = <string>`The file path to log to. Defaults to "variable\_dump". Does not include the `.log` extension.  `text = <string>`Text to prepend. Defaults to "No Header".  `append = <bool>`Whether to append to the file instead of overwrite. Defaults to `yes` | `print_variables = { var_list = { myvar1 myvar2 } file = "my_dump_file" text = "my header" }` | Dumps the specified variables from the current scope and optionally the global scope into a log file with the specified name. | The log will be within /Hearts of Iron IV/logs/variable\_dumps/ in the [user directory](<Modding - Hearts of Iron 4 Wiki.md>). See also debugging variables. | 1.5 |

## <a id="country-scope"></a>Country scope

Can be used in **country** scope.

### <a id="general_2"></a>General

General country-scoped triggers:
| Name | Parameters | Examples | Description | Notes | Version Added |
| --- | --- | --- | --- | --- | --- |
| <a id="exists"></a> exists | `<bool>` Boolean. | `exists = yes` | Checks if the current scope exists in game. |  | 1.0 |
| <a id="tag"></a> tag | `<scope> / <variable>` The country to check. | `tag = GER`  `tag = var:my_country` | Checks if the current scope is the specified country. | Only checks the actual tag while excluding dynamic countries, see [original\_tag](#original-tag) if they should be included. | 1.0 |
| <a id="original-tag"></a> original\_tag | `<scope> / <variable>` The country to check. | `original_tag = GER`  `original_tag = var:my_country` | Checks if the current scope originates from the specified country. | This also includes dynamic countries: civil war breakaways and countries created via [create\_dynamic\_country](<Effects - Hearts of Iron 4 Wiki.md#create-dynamic-country>). True for the original country. | 1.0 |
| <a id="is-ai"></a> is\_ai | `<bool>` Boolean. | `is_ai = yes` | Checks if the current scope is AI. |  | 1.0 |
| <a id="has-collaboration"></a> has\_collaboration | `target = <country>` The country to check.  `value <> <decimal>` The value of the collaboration on the 0-1 scale. | `has_collaboration = { target = GER value > 0.5 }` | Checks if the current scope has a collaboration level in the target scope. | The target is occupied by the current scope. Must use < or > in the value argument. | 1.9 |
| <a id="has-country-flag"></a> has\_country\_flag | `<string>` The flag to check. | `has_country_flag = my_flag` | Checks if the current scope has the specified flag. |  | 1.0 |
| <a id="has-country-flag"></a> has\_country\_flag | `flag = <string>` The flag to check.  `value = <int>` The flag value to check for. Optional.  `date = <date>` The flag creation date to check for. Optional.  `days = <int>` The duration the flag existed for. Optional. | `has_country_flag = { flag = my_flag days > 30 date > 1936.6.1 value > 0 }` | Compares the specified flag's last set date, days since last set, and/or value. | If not set, the value comparison is `>0`. `value` is limited between -32768 and 32767. | 1.0 |
| <a id="has-cosmetic-tag"></a> has\_cosmetic\_tag | `<string>` The cosmetic tag to check. | `has_cosmetic_tag = SOV_custom` | Checks if the current scope has the specified cosmetic tag active. |  | 1.5 |
| <a id="has-event-target"></a> has\_event\_target | `<event target>` The event target to check. | `has_event_target = my_var` | Checks if current scope or global scope has the specified event target saved. |  | 1.0 |
| <a id="has-decision"></a> has\_decision | `<string>` The decision to check. | `has_decision = my_decision` | Checks if the current scope has the specified decision activated. |  | 1.5 |
| <a id="has-dynamic-modifier"></a> has\_dynamic\_modifier | `modifier = <string>` The dynamic\_modifier to check.   `scope = <scope>`  The country to check. Optional, if the original modifier has been targeted. | `has_dynamic_modifier = { modifier = my_dynamic_modifier scope = GER }` | Checks if the current scope has the specified dynamic modifier activated. |  | 1.6 |
| <a id="has-active-mission"></a> has\_active\_mission | `<string>` The mission to check. | `has_active_mission = my_mission` | Checks if the current scope has the specified mission active. |  | 1.5 |
| <a id="has-country-custom-difficulty-setting"></a> has\_country\_custom\_difficulty\_setting | `<bool>` Boolean. | `has_country_custom_difficulty_setting = yes` | Checks if the any custom difficulty setting targeting the current scope is changed from the default value. | Custom difficulty in this case refers to /Hearts of Iron IV/common/difficulty\_settings/\*.txt, used in base game to strengthen a specific country. | 1.0 |
| <a id="has-terrain"></a> has\_terrain | `<terrain>` Terrain. | `has_terrain = urban` | Checks if the current scope has any provinces of the specified terrain. | Only can be used in country scope. | 1.11 |
| <a id="is-dynamic-country"></a> is\_dynamic\_country | `<bool>` Boolean. | `is_dynamic_country = yes` | Checks if the current scope is a dynamic country. | Dynamic countries include those generated in civil wars as well as those generated with the create\_dynamic\_country effect, such as collaboration governments. | 1.11 |
| <a id="num-of-supply-nodes"></a> num\_of\_supply\_nodes | `<int>` The amount to check for. | `num_of_supply_nodes > 10` | Checks if the current scope has the specified amount of supply nodes under control. | Can only use < or > operators. | 1.11 |
| <a id="resource-count-trigger"></a> <resource> (resource\_count\_trigger) | `<int>` The amount to check for. | `tungsten > 10` | Checks if the current scope has the specified amount of the specified resource. | Must use either > or < operators for amount. [Can also be used in state scope.](#s-resource-count-trigger) | ??? |
| <a id="has-resources-in-country"></a> has\_resources\_in\_country | `resource = <resource>` The resource to check for.  `amount = <int>` The amount to check for.  `extracted = <bool>` Limits the checked resources only to those gained from the state's base value and multiplicative modifiers on top of it if true. Optional, defaults to false.  `buildings = <bool>` Limits the checked resources only to those gained from the state's modifiers applied by buildings. Optional, defaults to false. | `has_resources_in_country = { resource = oil amount > 10 extracted = yes }` | Checks if the current scope has the specified amount of the specified resource in reserve. | Must use either > or < operators for amount. 'In reserve' means that it's not spent on equipment production or exports. | 1.12 |

### <a id="national-focuses"></a>National focuses

National focus-related country-scoped triggers:
| Name | Parameters | Examples | Description | Notes | Version Added |
| --- | --- | --- | --- | --- | --- |
| <a id="has-focus-tree"></a> has\_focus\_tree | `<string>` The focus tree to check. | `has_focus_tree = soviet_tree` | Checks if the current scope has the specified focus tree. |  | 1.3 |
| <a id="has-completed-focus"></a> has\_completed\_focus | `<string>` The focus to check. | `has_completed_focus = my_focus` | Checks if the current scope has the specified focus completed. |  | 1.0 |
| <a id="focus-progress"></a> focus\_progress | `focus = <string>` The focus to check.  `progress = <string>` The progress to check for. | `focus_progress = { focus = my_focus progress > 0.5 }` | Checks if the specified focus has been completed the specified percent for the current scope. | Must use either > or < operators for progress. | 1.0 |
| <a id="has-shine-effect-on-focus"></a> has\_shine\_effect\_on\_focus | `<string>` The focus to check. | `has_shine_effect_on_focus = GER_wunderwaffe` | Check if country has shine effect on focus (either manually achieved or by being worked on). | Note that tooltips are only shown in debug mode. Shine can be added manually by selecting focus, or via [activate\_shine\_on\_focus](<Effects - Hearts of Iron 4 Wiki.md#activate-shine-on-focus>) effect. | 1.15 |

### <a id="politics"></a>Politics

Political country-scoped triggers:
| Name | Parameters | Examples | Description | Notes | Version Added |
| --- | --- | --- | --- | --- | --- |
| <a id="ideology-support-trigger"></a> <ideology> (ideology\_support\_trigger) | `<ideology> = <float> / <variable>` The amount of the ideology to check for. | `fascism > 0.5`  `democratic > party_popularity@communism` | Checks if the current scope has popularity of the specified ideology above the specified amount. |  | 1.0 |
| <a id="has-political-power"></a> has\_political\_power | `<float> / <variable>` The amount to check for. | `has_political_power > 100` | Checks if the current scope has the specified amount of political power. | Must use either > or < operators. | 1.0 |
| <a id="political-power-daily"></a> political\_power\_daily | `<float> / <variable>` The amount to check for. | `political_power_daily > 1` | Checks if the current scope has the specified amount of daily political power gain. | Must use either > or < operators. | 1.5 |
| <a id="political-power-growth"></a> political\_power\_growth | `<float> / <variable>` The amount to check for. | `political_power_growth > 1` | Checks if the current scope has the specified amount of daily political power gain. | Must use either > or < operators. | 1.5 |
| <a id="command-power"></a> command\_power | `<float> / <variable>` The amount to check for. | `command_power > 1` | Checks if the current scope has the specified amount of command power. | Must use either > or < operators. | 1.5 |
| <a id="command-power-daily"></a> command\_power\_daily | `<float> / <variable>` The amount to check for. | `command_power_daily > 1` | Checks if the current scope has the specified amount of daily command power gain. | Must use either > or < operators. | 1.5 |
| <a id="has-war-support"></a> has\_war\_support | `<float> / <variable>` The amount to check for. | `has_war_support > 0.5` | Checks if the current scope has the specified percentage of War Support. | Must use either > or < operators. | 1.5 |
| <a id="has-stability"></a> has\_stability | `<float> / <variable>` The amount to check for. | `has_stability > 0.5` | Checks if the current scope has the specified percentage of Stability. | Must use either > or < operators. | 1.5 |
| <a id="has-government"></a> has\_government | `<ideology>` The ideology group to check for.  **OR**  `<country>` The country to compare with. | `has_government = fascism`  `has_government = ROOT` | Checks if the ruling party of the current scope meets the requirements of being either the specified ideology group or having the same ideology group as the specified country. |  | 1.0 |
| <a id="has-elections"></a> has\_elections | `<bool>` Boolean. | `has_elections = yes` | Checks if the current scope holds elections. |  | 1.0 |
| <a id="is-staging-coup"></a> is\_staging\_coup | `<bool>` Boolean. | `is_staging_coup = yes` | Checks if the current scope is staging a coup. |  | 1.3 |
| <a id="is-target-of-coup"></a> is\_target\_of\_coup | `<bool>` Boolean. | `is_target_of_coup = yes` | Checks if the current scope is the target of a coup. |  | 1.0 |
| <a id="has-civil-war"></a> has\_civil\_war | `<bool>` Boolean. | `has_civil_war = yes` | Checks if the current scope has a civil war active. |  | 1.0 |
| <a id="civilwar-target"></a> civilwar\_target | `<scope>` The target country. | `civilwar_target = GER` | Checks if the specified country is a target of a civil war. |  | 1.0 |
| <a id="has-manpower-for-recruit-change-to"></a> has\_manpower\_for\_recruit\_change\_to | `value = <float>` The amount to check for. `group = <group>` The group to check for. | `has_manpower_for_recruit_change_to = { value > 0.05 group = mobilization_laws }` | Checks if the current scope has the specified amount of manpower for changing the specified idea group. | **Must** use either > or < operators as = operator checks for the **exact** value | 1.0 |
| <a id="has-rule"></a> has\_rule | `<string>` The rule to check for. | `has_rule = can_create_factions` | Checks if the current scope has the specified country rule. |  | 1.6 |
| <a id="has-casualties-war-support"></a> has\_casualties\_war\_support | `<float> / <variable>` The amount to check for. | `has_casualties_war_support < 0` | Checks if the current scope has the specified percentage of war support from own combat casualties. | Must use either > or < operators. | 1.12 |
| <a id="has-convoys-war-support"></a> has\_convoys\_war\_support | `<float> / <variable>` The amount to check for. | `has_convoys_war_support < 0` | Checks if the current scope has the specified percentage of war support from own convoys sunk. | Must use either > or < operators. | 1.12 |
| <a id="has-bombing-war-support"></a> has\_bombing\_war\_support | `<float> / <variable>` The amount to check for. | `has_bombing_war_support < 0` | Checks if the current scope has the specified percentage of war support from own states bombed by the enemy. | Must use either > or < operators. | 1.12 |

### <a id="balance-of-power"></a>Balance of power

Balances of power are stored within /Hearts of Iron IV/common/bop/\*.txt files.

Balance of power-related country-scoped triggers:
| Name | Parameters | Examples | Description | Notes | Version Added |
| --- | --- | --- | --- | --- | --- |
| <a id="has-power-balance"></a> has\_power\_balance | `id = <bop ID>` The balance to check for. | `has_power_balance = { id = TAG_my_bop }` | Checks if the current scope has the specified balance of power active. |  | 1.12 |
| <a id="has-any-power-balance"></a> has\_any\_power\_balance | `<bool>` Boolean. | `has_any_power_balance = yes` | Checks if the current scope has any balance of power active. |  | 1.12 |
| <a id="power-balance-value"></a> power\_balance\_value | `id = <bop ID>` The balance to check in.  `value = <float>` The value to check for. | `power_balance_value = { id = TAG_my_bop value > 0.7 }` | Checks if the current scope has the specified value within the balance of power. | Either =, >, or < operators are allowed. | 1.12 |
| <a id="power-balance-daily-change"></a> power\_balance\_daily\_change | `id = <bop ID>` The balance to check in.  `value = <float>` The value to check for. | `power_balance_daily_change = { id = TAG_my_bop value < -0.01 }` | Checks if the current scope's balance of power changes each day by the specified value. | Either =, >, or < operators are allowed. | 1.12 |
| <a id="power-balance-weekly-change"></a> power\_balance\_weekly\_change | `id = <bop ID>` The balance to check in.  `value = <float>` The value to check for. | `power_balance_weekly_change = { id = TAG_my_bop value < -0.01 }` | Checks if the current scope's balance of power changes each week by the specified value. | Either =, >, or < operators are allowed. | 1.12 |
| <a id="is-power-balance-in-range"></a> is\_power\_balance\_in\_range | `id = <bop ID>` The balance to check in.  `range = <range ID>` The range to check for. | `is_power_balance_in_range = { id = TAG_my_bop range > TAG_my_bop_right_range }` | Checks if the current scope's balance of power value lies within the specified range. | Ranges are defined within the balance of power. Can use either =, >, and < operators. In case of > or <, the comparison is 'strict', i.e. excluding the range itself. | 1.12 |
| <a id="is-power-balance-side-active"></a> is\_power\_balance\_side\_active | `id = <bop ID>` The balance to check in.  `side = <side ID>` The side to check. | `is_power_balance_side_active = { id = TAG_my_bop side = TAG_my_bop_right_range }` | Checks if the specified balance of power has a side active. | Sides are defined within the balance of power. "Active" means that the side is among those that are currently visible instead of relying on the current value. | 1.12 |
| <a id="has-power-balance-modifier"></a> has\_power\_balance\_modifier | `id = <bop ID>` The balance to check in.  `modifier = <modifier ID>` The static modifier. | `has_power_balance_modifier = { id = TAG_my_bop modifier = TAG_my_bop_modifier }` | Checks if the current scope's balance of power value activates a modifier. | BoP modifiers are defined within /Hearts of Iron IV/common/modifiers/\*.txt files, while they're activated in the balance of power definition. | 1.12 |

### <a id="buildings"></a>Buildings

Building-related country-scoped triggers:
| Name | Parameters | Examples | Description | Notes | Version Added |
| --- | --- | --- | --- | --- | --- |
| <a id="building-count-trigger"></a> <building> (building\_count\_trigger) | `<int>` The amount of the specified building to to check for. | `arms_factory > 10` | Checks if the current scope has the specified amount of the specified building. | Must use either > or < operators. Works in the state scope as well, unlike the other triggers. [Can also be used in state scope.](#s-building-count-trigger) | 1.0 |
| <a id="num-of-military-factories"></a> num\_of\_military\_factories | `<int>` The amount to check for. | `num_of_military_factories > 10` | Checks if the current scope has the specified amount of military factories. | Must use either > or < operators. | 1.0 |
| <a id="num-of-civilian-factories"></a> num\_of\_civilian\_factories | `<int>` The amount to check for. | `num_of_civilian_factories > 10` | Checks if the current scope has the specified amount of civilian factories. | Must use either > or < operators. | 1.0 |
| <a id="num-of-naval-factories"></a> num\_of\_naval\_factories | `<int>` The amount to check for. | `num_of_naval_factories > 10` | Checks if the current scope has the specified amount of dockyards. | Must use either > or < operators. | 1.0 |
| <a id="num-of-available-military-factories"></a> num\_of\_available\_military\_factories | `<int>` The amount to check for. | `num_of_available_military_factories > 10` | Checks if the current scope has the specified amount of available military factories. | Must use either > or < operators. | 1.0 |
| <a id="num-of-available-civilian-factories"></a> num\_of\_available\_civilian\_factories | `<int>` The amount to check for. | `num_of_available_civilian_factories > 10` | Checks if the current scope has the specified amount of available civilian factories. | Must use either > or < operators. | 1.0 |
| <a id="num-of-available-naval-factories"></a> num\_of\_available\_naval\_factories | `<int>` The amount to check for. | `num_of_available_naval_factories > 10` | Checks if the current scope has the specified amount of available dockyards. | Must use either > or < operators. | 1.0 |
| <a id="num-of-factories"></a> num\_of\_factories | `<int>` The amount to check for. | `num_of_factories > 10` | Checks if the current scope has the specified amount of military, civilian or dockyard factories. | Must use either > or < operators. | 1.0 |
| <a id="num-of-controlled-factories"></a> num\_of\_controlled\_factories | `<int>` The amount to check for. | `num_of_controlled_factories > 10` | Checks if the current scope has the specified amount of military, civilian or dockyard factories under control. | Must use either > or < operators. | 1.11 |
| <a id="num-of-owned-factories"></a> num\_of\_owned\_factories | `<int>` The amount to check for. | `num_of_owned_factories > 10` | Checks if the current scope has the specified amount of military, civilian or dockyard factories under owned states. | Must use either > or < operators. | 1.11 |
| <a id="num-of-civilian-factories-available-for-projects"></a> num\_of\_civilian\_factories\_available\_for\_projects | `<int>` The amount to check for. | `num_of_civilian_factories_available_for_projects > 10` | Checks if the current scope has the specified amount of civilian factories usable for projects. | Must use either > or < operators. | 1.5 |
| <a id="ic-ratio"></a> ic\_ratio | `tag = <scope>` The country to check. `ratio = <float>` The ratio to check for. | `ic_ratio = { tag = GER ratio > 0.5 }` | Checks if the current scope has the specified ratio of factories with the target country. | Must use either > or < operators for ratio. | 1.0 |
| <a id="has-damaged-buildings"></a> has\_damaged\_buildings | `<bool>` Boolean. | `has_damaged_buildings = yes` | Checks if the current scope has any damanged buildings in their states. |  | 1.0 |
| <a id="has-built"></a> has\_built | `type = <building>` The building to check for. `value = <int>` The amount to check for. | `has_built = { type = arms_factory value > 10 }` | Checks if the current scope has built the specified building the specified number of times. | Must use either > or < operators for value. | 1.0 |

### <a id="technology"></a>Technology

Technology-related country-scoped triggers:
| Name | Parameters | Examples | Description | Notes | Version Added |
| --- | --- | --- | --- | --- | --- |
| <a id="has-tech"></a> has\_tech | `<string>` The technology to check for. | `has_tech = my_technology` | Checks if the current scope has the specified technology. |  | 1.0 |
| <a id="is-researching-technology"></a> is\_researching\_technology | `<string>` The technology to check for. | `is_researching_technology = my_tech` | Checks if the current scope is currently researching the specified technology. |  | 1.0 |
| <a id="can-research"></a> can\_research | `<string>` The technology to check for. | `can_research = my_tech` | Checks if the current scope can start researching the specified technology. |  | 1.0 |
| <a id="original-research-slots"></a> original\_research\_slots | `<int>` The amount to check for. | `original_research_slots > 3` | Checks if the current scope had the specified amount of slots at game start. | Must use either > or < operators. | 1.0 |
| <a id="amount-research-slots"></a> amount\_research\_slots | `<int>` The amount to check for. | `amount_research_slots > 3` | Checks if the current scope has the specified amount of research slots. | Must use either > or < operators. | 1.3 |
| <a id="is-in-tech-sharing-group"></a> is\_in\_tech\_sharing\_group | `<string>` The group to check for. | `is_in_tech_sharing_group = us_research` | Checks if the current scope is in the specified technology sharing group. |  | 1.3 |
| <a id="num-tech-sharing-groups"></a> num\_tech\_sharing\_groups | `<int>` The amount to check for. | `num_tech_sharing_groups > 3` | Checks if the current scope is in the specified amount of technology sharing groups. | Must use either > or < operators. | 1.3 |
| <a id="has-tech-bonus"></a> has\_tech\_bonus | `technology = <string>` The technology to check for. Optional.  `category = <string>` The category to check for. Optional. | `has_tech_bonus = { technology = my_tech }`  `has_tech_bonus = { category = my_category }` | Checks if the current scope has a technology bonus in the specified category, or for the specific technology. |  | 1.3 |
| <a id="land-doctrine-level"></a> land\_doctrine\_level | `<int>` The amount to check for. | `land_doctrine_level > 2` | Checks if the current scope has the specified amount of land doctrine technologies. | Must use either > or < operators. | 1.0 |
| <a id="num-researched-technologies"></a> num\_researched\_technologies | `<int>` The amount to check for. | `num_researched_technologies > 10` | Checks how many technologies the target has researched. | Must use either > or < operators. | 1.3 |
| <a id="is-special-project-being-researched"></a> is\_special\_project\_being\_researched | `sp:<string>` A special project to check for. | `is_special_project_being_researched = sp:sp_air_radar` | Checks if the country in scope is currently researching the special project in input. |  | 1.15 |
| <a id="is-special-project-completed"></a> is\_special\_project\_completed | `sp:<string>` A special project to check for. | `is_special_project_completed = sp:sp_land_flamethrower_tank` | Checks if the current scope has the specified special project completed. |  | 1.15 |

### <a id="ideas"></a>Ideas

Idea-related country-scoped triggers:
| Name | Parameters | Examples | Description | Notes | Version Added |
| --- | --- | --- | --- | --- | --- |
| <a id="has-idea"></a> has\_idea | `<string>` The idea to check for. | `has_idea = my_idea` | Checks if the current scope has the specified idea. |  |  |
| <a id="has-idea-with-trait"></a> has\_idea\_with\_trait | `<string>` The trait to check for. | `has_idea_with_trait = my_trait` | Checks if the current scope has any ideas with the specified trait. |  | 1.0 |
| <a id="has-allowed-idea-with-traits"></a> has\_allowed\_idea\_with\_traits | `idea = <string>` The trait to check for.  `limit = <int>` The amount to check for.  `characters = <bool>` If set, will only run this on characters.  `ignore = { <ideas> }` If set, ignores the ideas inside. Optional. | `has_available_idea_with_traits = { idea = my_trait limit = 1 ignore = { generic_head_of_intelligence } }` | Checks if the current scope has the specified amount of ideas with the specified trait. | ignore = idea\_name works for 1 idea. | 1.9.1 |
| <a id="has-available-idea-with-traits"></a> has\_available\_idea\_with\_traits | `idea = <string>` The trait to check for.  `limit = <int>` The amount to check for.  `characters = <bool>` If set, will only run this on characters.  `ignore = { <ideas> }` If set, ignores the ideas inside. Optional. | `has_available_idea_with_traits = { idea = my_trait limit = 1 ignore = { generic_head_of_intelligence } }` | Checks if the current scope has the specified amount of ideas with the specified trait. | ignore = idea\_name works for 1 idea. | 1.0 |
| <a id="amount-taken-ideas"></a> amount\_taken\_ideas | `amount = <int>` The amount to check for. `slots = { <string> }` The slot type. | `amount_taken_ideas = { amount > 3 slots = { political_advisor } }` | Checks if the current scope has the specified amount of ideas of the specified slot type. Excludes spirits, hidden ideas, and laws. | Slots types are found in /Hearts of Iron IV/common/idea\_tags/\*.txt. | 1.4 |

### <a id="diplomacy"></a>Diplomacy

Diplomatic country-scoped triggers:
| Name | Parameters | Examples | Description | Notes | Version Added |
| --- | --- | --- | --- | --- | --- |
| <a id="is-major"></a> is\_major | `<bool>` Boolean. | `is_major = yes` | Checks if the current scope is considered a Major. |  | 1.0 |
| <a id="is-ally-with"></a> is\_ally\_with | `<scope> / <variable>` The country to check for. | `is_ally_with = GER`  `is_ally_with = var:country` | Checks if the current scope is an ally (Faction members or subject-master relation). |  | 1.0 |
| <a id="is-spymaster"></a> is\_spymaster | `<bool>` Boolean. | `is_spymaster = yes` | Checks if the current scope is the spymaster of a faction. |  | 1.9 |
| <a id="has-non-aggression-pact-with"></a> has\_non\_aggression\_pact\_with | `<scope> / <variable>` The country to check for. | `has_non_aggression_pact_with = GER` | Checks if the current scope has a non-aggression pact with the specified country. |  | 1.0 |
| <a id="is-guaranteed-by"></a> is\_guaranteed\_by | `<scope> / <variable>` The country to check for. | `is_guaranteed_by = GER` | Checks if the current scope has been guaranteed by the specified country. |  | 1.0 |
| <a id="has-guaranteed"></a> has\_guaranteed | `<scope> / <variable>` The country to check for. | `has_guaranteed = GER` | Checks if the current scope has guaranteed the specified country. |  | 1.0 |
| <a id="has-military-access-to"></a> has\_military\_access\_to | `<scope> / <variable>` The country to check for. | `has_military_access_to = GER` | Checks if the current scope has military access to the specified country. |  | 1.0 |
| <a id="gives-military-access-to"></a> gives\_military\_access\_to | `<scope> / <variable>` The country to check for. | `gives_military_access_to = GER` | Checks if the current scope gives military to the specified country. |  | 1.0 |
| <a id="is-neighbor-of"></a> is\_neighbor\_of | `<scope> / <variable>` The country to check for. | `is_neighbor_of = GER` | Checks if the current scope is a neighbor of the specified country. |  | 1.0 |
| <a id="is-owner-neighbor-of"></a> is\_owner\_neighbor\_of | `<scope> / <variable>` The country to check for. | `is_owner_neighbor_of = GER` | Checks if the current scope is a neighbor of the specified country with their core territory only. |  | 1.0 |
| <a id="is-puppet-of"></a> is\_puppet\_of | `<scope> / <variable>` The country to check for. | `is_puppet_of = GER` | Checks if the current scope is a puppet of the specified country. | A "puppet" is an autonomous state that has `is_puppet = yes` in its definition within /Hearts of Iron IV/common/autonomous\_states/. For any subject type, see [is\_subject\_of](#is-subject-of). | 1.0 |
| <a id="is-subject-of"></a> is\_subject\_of | `<scope> / <variable>` The country to check for. | `is_subject_of = GER` | Checks if the current scope is a subject of the specified scope. |  | 1.0 |
| <a id="is-puppet"></a> is\_puppet | `<bool>` Boolean. | `is_puppet = yes` | Returns true if the current country is a puppet. | A "puppet" is an autonomous state that has `is_puppet = yes` in its definition within /Hearts of Iron IV/common/autonomous\_states/. For any subject type, see [is\_subject](#is-subject). | 1.0 |
| <a id="is-subject"></a> is\_subject | `<bool>` Boolean. | `is_subject = yes` | Checks if the current scope is a subject. |  | 1.0 |
| <a id="has-subject"></a> has\_subject | `<bool>` Boolean. | `has_subject = GRE` | Checks if the country has for subject the given country. |  | 1.0 |
| <a id="num-subjects"></a> num\_subjects | `<int>` The amount to check for. | `num_subjects > 3` | Checks if the current scope has the specified amount of subjects. | Must use either > or < operators. | 1.3 |
| <a id="has-autonomy-state"></a> has\_autonomy\_state | `<string>` The autonomy state to check for. | `has_autonomy_state = autonomy_dominion` | Checks if the current scope is in the specified autonomous state. |  | 1.0 |
| <a id="compare-autonomy-state"></a> compare\_autonomy\_state | `<string>` The autonomy state to check for. | `compare_autonomy_state > autonomy_dominion` | Checks if the current scope's autonomy state `min_freedom_level` is less or greater than that of the specified autonomy state. The special value "autonomy\_free" compares as greater than any autonomy state. If the current scope is not a subject, it is treated as greater than any autonomy state (including "autonomy\_free"). With `=`, checks if the current scope is in the specified autonomous state. |  | 1.0 |
| <a id="compare-autonomy-progress-ratio"></a> compare\_autonomy\_progress\_ratio | `<float>` The amount to check for. | `compare_autonomy_progress_ratio > 0.5` | Checks if the current scope autonomy progress is at the specified ratio. If the current scope is not a subject, the ratio is 1. |  | 1.3 |
| <a id="has-opinion-modifier"></a> has\_opinion\_modifier | `<string>` The opinion modifier to check for. | `has_opinion_modifier = my_modifier` | Checks if the current scope has the specified opinion modifier. |  | 1.0 |
| <a id="has-opinion"></a> has\_opinion | `target = <scope>` The country to check for. `value = <float>` The amount to check for. | `has_opinion = { target = GER value > 50 }` | Checks if the current scope has the specified opinion of the target country. | Must use either > or < operators. | 1.0 |
| <a id="has-relation-modifier"></a> has\_relation\_modifier | `target = <scope>` The country to check for. `modifier = <modifier>` The modifier to check for. | `has_relation_modifier = { target = GER modifier = my_modifier }` | Checks if the current scope has the specified relation modifier with the specified country. |  | 1.0 |
| <a id="has-legitimacy"></a> has\_legitimacy | `<int>` Amount to check. | `has_legitimacy > 50` | Checks how much legitimacy the current government in exile has. | Must use either > or < operators. Legitimacy ranges from 0 to 100. | 1.6 |
| <a id="is-exile-host"></a> is\_exile\_host | `<bool>` Boolean. | `is_exile_host = yes` | Checks if the current country is hosting an exile. |  | 1.6 |
| <a id="is-hosting-exile"></a> is\_hosting\_exile | `<tag>` Country. | `is_hosting_exile = POL` | Checks if the current country is hosting a specific exile. |  | 1.6 |
| <a id="is-government-in-exile"></a> is\_government\_in\_exile | `<bool>` Boolean. | `is_government_in_exile = yes` | Checks if the current country is exiled in a different country. |  | 1.6 |
| <a id="is-exiled-in"></a> is\_exiled\_in | `<tag>` Country to be exiled in. | `is_exiled_in = POL` | Checks if the current country is exiled in a specific country. |  | 1.6 |
| <a id="received-expeditionary-forces"></a> received\_expeditionary\_forces | `sender = <tag>` Country which sent forces. `value <> <int>` Amount of forces. | `received_expeditionary_forces = { sender = POL value > 10 }` | Checks if the current country received X units in expeditions from the specified country. |  | 1.6 |
| <a id="can-declare-war-on"></a> can\_declare\_war\_on | `<tag>` Country to check. | `can_declare_war_on = POL` | Checks if the current scope is able to declare war on the specified country. |  | 1.9 |
| <a id="foreign-manpower"></a> foreign\_manpower | `<int>` Amount to check. | `foreign_manpower > 10000` | Checks how much foreign manpower we have received for garrisoning. | Must use either > or < operators. | 1.9 |
| <a id="is-embargoed-by"></a> is\_embargoed\_by | `<scope>` Amount to check. | `is_embargoed_by = USA` | Checks if the current scope is embargoed by the specified country. |  | 1.12 |
| <a id="is-embargoing"></a> is\_embargoing | `<scope>` Amount to check. | `is_embargoing = CUB` | Checks if the current scope is embargoing the specified country. |  | 1.12 |

### <a id="faction"></a>Faction

Faction-related country-scoped triggers:
| Name | Parameters | Examples | Description | Notes | Version Added |
| --- | --- | --- | --- | --- | --- |
| <a id="is-in-faction"></a> is\_in\_faction | `<bool>` Boolean. | `is_in_faction = yes` | Checks if the current scope is in a faction. |  | 1.0 |
| <a id="is-in-faction-with"></a> is\_in\_faction\_with | `<scope> / <variable>` The country to check for. | `is_in_faction_with = GER`  `is_in_faction_with = var:country` | Checks if the current scope is in a faction with the specified country. |  | 1.0 |
| <a id="is-faction-leader"></a> is\_faction\_leader | `<bool>` Boolean. | `is_faction_leader = yes` | Checks if the current scope is the leader of a faction. |  | 1.0 |
| <a id="num-faction-members"></a> num\_faction\_members | `<int> / <variable>` The amount to check for. | `num_faction_members > 1` | Checks if the faction of the current scope has the specified amount of members. | Must use either > or < operators. | 1.0 |
| <a id="has-manpower-to-become-leader"></a> has\_manpower\_to\_become\_leader | `<bool>` Boolean | `has_manpower_to_become_leader = yes` | Checks if the current country exceeds the current faction leader and its subjects in deployed manpower. |  | 1.17 |
| <a id="has-industry-to-become-leader"></a> has\_industry\_to\_become\_leader | `<bool>` Boolean | `has_industry_to_become_leader = yes` | Checks if the current country exceeds the faction leader in number of factories. |  | 1.17 |
| <a id="has-enough-influence-for-leadership"></a> has\_enough\_influence\_for\_leadership | `<bool>` Boolean | `has_enough_influence_for_leadership = yes` | Checks if the current country has enough political influence to become faction leader. |  | 1.17 |
| <a id="has-faction-template"></a> has\_faction\_template | `<template_id>` Faction template id. | `has_faction_template = faction_template_chinese_united_front` | Checks if the current country is in a faction with a template. |  | 1.17 |
| <a id="has-active-rule"></a> has\_active\_rule | `<rule_id>` Faction rule id. | `has_active_rule = government_in_exile_allowed` | Checks if the country's faction has a specific active rule. |  | 1.17 |
| <a id="has-faction-goal"></a> has\_faction\_goal | `<goal_id>` Faction goal id. | `has_faction_goal = faction_goal_resource_control` | Checks if the country's faction has an active or completed goal. |  | 1.17 |
| <a id="has-completed-faction-goal"></a> has\_completed\_faction\_goal | `<goal_id>` Faction goal id. | `has_completed_faction_goal = faction_goal_resource_control` | Checks if the country's faction has successfully completed a goal. |  | 1.17 |
| <a id="faction-goal-fulfillment"></a> faction\_goal\_fulfillment | `goal = <goal_id>` Faction goal id. `value = <float> / <variable>` The amount to check for. | `faction_goal_fulfillment = { goal = faction_goal_resource_control value > 0.85 }`  `faction_goal_fulfillment = { goal = faction_goal_resource_control value > 0.5 value < 0.85 }` | Checks fulfillment of a faction goal for the current country's faction. | Value supports > and <, can accept variables, can be repeated multiple times. | 1.17 |
| <a id="faction-manifest-fulfillment"></a> faction\_manifest\_fulfillment | `<float> / <variable>` The amount to check for. | `faction_manifest_fulfillment > 0.95` | Checks manifest fulfillment value of current country's faction manifest. |  | 1.17 |
| <a id="faction-upgrade-level"></a> faction\_upgrade\_level | `<upgrade_token>` Faction upgrade token. | `faction_upgrade_level > upgrade_token` | Checks the active faction member upgrade against the specified upgrade. | Works with >, <, = | 1.17 |
| <a id="faction-power-projection"></a> faction\_power\_projection | `<int> / <variable>` The amount to check for. | `faction_power_projection > 100` | Checks power value of current country's faction projection. |  | 1.17 |
| <a id="faction-influence-rank"></a> faction\_influence\_rank | `<int> / <variable>` The amount to check for. | `faction_influence_rank < 5` | Checks influence rank in the faction of the current country. |  | 1.17 |
| <a id="faction-influence-ratio"></a> faction\_influence\_ratio | `<float> / <variable>` The amount to check for. | `faction_influence_ratio > 0.1` | Checks influence ratio of current country in the faction. |  | 1.17 |
| <a id="faction-influence-score"></a> faction\_influence\_score | `<int> / <variable>` The amount to check for. | `faction_influence_score > 100` | Checks influence value of current country in the faction. |  | 1.17 |
| <a id="can-assign-supportive-scientist-to-faction"></a> can\_assign\_supportive\_scientist\_to\_faction | `<specialization>` Specialization. | `can_assign_supportive_scientist_to_faction = specialization_land` | Checks if the faction from the country in scope has a free slot for a supportive scientist for the country with the specialization type. |  | 1.17 |
| <a id="has-faction-research-unlocked"></a> has\_faction\_research\_unlocked | `<bool>` Boolean. | `has_faction_research_unlocked = yes` | Whether the faction has unlocked the research. |  | 1.17 |
| <a id="has-faction-military-unlocked"></a> has\_faction\_military\_unlocked | `<bool>` Boolean. | `has_faction_military_unlocked = yes` | Whether the faction has unlocked the military operations. |  | 1.17 |
| <a id="compare-ideology-with-faction"></a> compare\_ideology\_with\_faction | `value = <float> / <variable>` The amount to check for. `leader = <tag>` Country to check. | `compare_ideology_with_faction = { value > 0.5 leader = FROM }` | Compares the ideology support of the country's ruling party for the ideology of the faction it wants to join. | Tooltip is visible only if 'leader' is in faction. | 1.17 |

### <a id="war"></a>War

War-related country-scoped triggers:
| Name | Parameters | Examples | Description | Notes | Version Added |
| --- | --- | --- | --- | --- | --- |
| <a id="has-war"></a> has\_war | `<bool>` Boolean. | `has_war = yes` | Checks if the current scope is at war. |  | 1.0 |
| <a id="has-war-with"></a> has\_war\_with | `<scope> / <variable>` The country to check for. | `has_war_with = GER`  `has_war_with = var:country` | Checks if the current scope is at war with the specified country. |  | 1.0 |
| <a id="has-offensive-war-with"></a> has\_offensive\_war\_with | `<scope> / <variable>` The country to check for. | `has_offensive_war_with = GER` | Checks if the current scope is in an offensive war against the specified country. |  | 1.0 |
| <a id="has-offensive-war-without-friend"></a> has\_offensive\_war\_without\_friend | `<scope> / <variable>` The country to check for. | `has_offensive_war_without_friend = GER` | Is country at offensive war without specific ally present. |  | 1.17 |
| <a id="has-defensive-war-with"></a> has\_defensive\_war\_with | `<scope> / <variable>` The country to check for. | `has_defensive_war_with = GER` | Checks if the current scope is in an defensive war against the specified country. |  | 1.0 |
| <a id="has-offensive-war"></a> has\_offensive\_war | `<bool>` Boolean. | `has_offensive_war = yes` | Checks if the current scope is in an offensive war. |  | 1.0 |
| <a id="has-defensive-war"></a> has\_defensive\_war | `<bool>` Boolean. | `has_defensive_war = yes` | Checks if the current scope is in a defensive war. |  | 1.0 |
| <a id="has-war-together-with"></a> has\_war\_together\_with | `<scope> / <variable>` The country to check for. | `has_war_together_with = GER` | Checks if the current scope is in a war alongside the specified country. |  | 1.0 |
| <a id="has-war-with-major"></a> has\_war\_with\_major | `<bool>` Boolean. | `has_war_with_major = yes` | Checks if the current scope is at war with any other country that is considered major. |  | 1.12 |
| <a id="has-war-with-wargoal-against"></a> has\_war\_with\_wargoal\_against | `target = <scope> / <variable>` The country to check for.  `type = <wargoal>` The wargoal to check for. Optional. | `has_war_with_wargoal_against = { target = ENG type = independence_wargoal }` | Checks if the current scope is at war with the specified country with the specified wargoal being active. | Wargoals are stored within /Hearts of Iron IV/common/wargoals/\*.txt files. If no wargoal is specified, checks for *any* wargoal. Joining an ally in their war does not count as a wargoal. | 1.12 |
| <a id="surrender-progress"></a> surrender\_progress | `<float> / <variable>` The amount to check for. | `surrender_progress > 0.1` | Checks if the current scope has the specified amount of surrender progress. | Must use either > or < operators. | 1.0 |
| <a id="any-war-score"></a> any\_war\_score | `<float>` The amount to check for. | `any_war_score > 10` | Highest warscore value can be approximated by interating a variable by 1 for as long as any\_war\_score is greater than the variable. Checking with less than appears broken as a warscore of 0 is sometimes erroneously reported. | Must use either > or < operators. | 1.0 |
| <a id="has-capitulated"></a> has\_capitulated | `<bool>` Boolean. | `has_capitulated = yes` | Checks if the current scope has capitulated. |  | 1.0 |
| <a id="days-since-capitulated"></a> days\_since\_capitulated | `<int>` Amount of days. | `days_since_capitulated > 10` | Checks the amount of days since the target last capitulated. | If the target never capitulated, the amount of days is extremely large. Recommended to combine with has\_capitulated. | 1.9 |
| <a id="has-border-war-with"></a> has\_border\_war\_with | `<scope> / <variable>` The country to check for. | `has_border_war_with = GER` | Checks if the current scope has a border war with the specified country. |  | 1.5 |
| <a id="has-border-war-between"></a> has\_border\_war\_between | `attacker = <scope> / <variable>` The state to check for. `defender = <scope> / <variable>` The state to check for. | `has_border_war_between = { attacker = 1 defender = 2 }` | Checks if there is a border war between the two specified states. |  | 1.5 |
| <a id="has-border-war"></a> has\_border\_war | `<bool>` Boolean. | `has_border_war = yes` | Checks if the current scope has a border war active. |  | 1.5 |
| <a id="has-added-tension-amount"></a> has\_added\_tension\_amount | `<float> / <variable>` The amount to check for. | `has_added_tension_amount > 10` | Checks if the current scope has caused the specified amount of World Tension. | Must use either > or < operators. | 1.0 |
| <a id="has-wargoal-against"></a> has\_wargoal\_against | `<scope> / <variable>` The country to check for. | `has_wargoal_against = GER` | Checks if the current scope has any wargoal against the specified country. |  | 1.0 |
| <a id="has-wargoal-against"></a> has\_wargoal\_against | `target = <scope> / <variable>` The country to check for.  `type = <string>` The type of wargoal to check for. | `has_wargoal_against = { target = FROM type = take_state }` | Checks if the current scope has a specific wargoal type against the specified country. |  | 1.8 |
| <a id="is-justifying-wargoal-against"></a> is\_justifying\_wargoal\_against | `<scope> / <variable>` The country to check for. | `is_justifying_wargoal_against = GER` | Checks if the current scope is justifying a wargoal against the specified country. |  | 1.0 |
| <a id="has-annex-war-goal"></a> has\_annex\_war\_goal | `<scope> / <variable>` The country to check for. | `has_annex_war_goal = GER` | Checks if the current scope has the Annex wargoal against the specified country. |  | 1.0 |
| <a id="any-claim"></a> any\_claim | `<bool>` Boolean. | `any_claim = yes` | Will return true if  1. Is (manually) justifying on another country 2. Is being (manually) justified on 3. Has wargoal on another country 4. Another country has wargoal on the current country | Misleading name. In-game the localization says "Active or generating war goals related to [TAG.GetNameDefCap]" | 1.0 |
| <a id="is-in-peace-conference"></a> is\_in\_peace\_conference | `<bool>` Boolean. | `is_in_peace_conference = yes` | Checks if the current scope is in a peace conference. | Please test this in-game for 1.12. | 1.0 |
| <a id="controls-province"></a> controls\_province | `<id>` The province to check for. | `controls_province = 1239` | Checks if the current scope has control of the specified province. |  | 1.9 |
| <a id="longest-war-length"></a> longest\_war\_length | `<int>` Amount of months. | `longest_war_length > 3` | Checks how long a country has been at war, in months. |  | 1.14 |
| <a id="war-length-with"></a> war\_length\_with | `tag = <scope> / <variable>` Target country.  `months = <int>` Amounth of months. | `war_length_with = { tag = GER months > 3 }` | Checks how long a country has been at war with specific country, in months. |  | 1.14 |
| <a id="has-truce-with"></a> has\_truce\_with | `<scope> / <variable>` The country to check for. | `has_truce_with = GER` | Checks if the country has truce with the specified country. |  | 1.16 |
| <a id="has-naval-control"></a> has\_naval\_control | `<id> / <variable>` The region to check in. | `has_naval_control = 16` | Checks if friendly nations and country scope together has enough naval dominance to assert control in strategic region. |  | 1.17 |
| <a id="has-enemy-naval-control"></a> has\_enemy\_naval\_control | `<id> / <variable>` The region to check in. | `has_enemy_naval_control = 16` | Checks if any enemy has enough naval dominance to assert control in certain strategic region. |  | 1.17 |

### <a id="state"></a>State

These are state-related triggers in the country scope, not [state-scoped triggers](#state-scope).

State-related country-scoped triggers:
| Name | Parameters | Examples | Description | Notes | Version Added |
| --- | --- | --- | --- | --- | --- |
| <a id="controls-state"></a> controls\_state | `<scope> / <variable>` The state to check for. | `controls_state = 39`  `controls_state = var:state` | Checks if the current scope has control of the specified state. |  | 1.0 |
| <a id="owns-state"></a> owns\_state | `<scope> / <variable>` The state to check for. | `owns_state = 39` | Checks if the current scope owns the specified state. |  | 1.0 |
| <a id="num-of-controlled-states"></a> num\_of\_controlled\_states | `<int>` The amount to check for. | `num_of_controlled_states > 5` | Checks if the current scope has the specified amount of controlled states. | Must use either > or < operators. | 1.0 |
| <a id="num-occupied-states"></a> num\_occupied\_states | `<int>` The amount to check for. | `num_occupied_states > 5` | Checks if the current scope has the specified amount of occupied states. | Must use either > or < operators. | 1.0 |
| <a id="has-full-control-of-state"></a> has\_full\_control\_of\_state | `<scope> / <variable>` The state to check for. | `has_full_control_of_state = 39` | Checks if the current scope has total control (100% occupation) of the specified state. |  | 1.3 |
| <a id="has-resources-rights"></a> has\_resources\_rights | `state = <scope> / <variable>` The state to check in. Mandatory if used in country scope. `resources = { <resource> <...> <resource> }` Resources to check for. Optional, defaults to any if unset. | `has_resources_rights = { state = 123 resources = { oil steel } }` | Checks if there are any resource rights with the specified parameters. | Can be used in either state or country scope. Always returns false if the state has no resources. [Can also be used in state scope.](#s-has-resources-rights) | 1.12 |
| <a id="core-compliance"></a> core\_compliance | `occupied_country_tag = <TAG>` The country for which to check compliance.  `value = <int>` The value to check for. | `core_compliance = { occupied_country_tag = ITA value > 10 }` | Compares the average compliance of core states of the specified country within controlled states of the current scope. | Must use either > or < operators for value. | 1.9 |
| <a id="core-resistance"></a> core\_resistance | `occupied_country_tag = <TAG>` The country for which to check resistance.  `value = <int>` The value to check for. | `core_resistance = { occupied_country_tag = ITA value > 10 }` | Compares the average resistance of core states of the specified country within controlled states of the current scope. | Must use either > or < operators for value. | 1.9 |
| <a id="garrison-manpower-need"></a> garrison\_manpower\_need | `<int>` Amount to check. | `garrison_manpower_need > 10000` | Checks how much garrison manpower we need for resistance in controlled states. | Must use either > or < operators. | 1.9 |
| <a id="has-core-occupation-modifier"></a> has\_core\_occupation\_modifier | `occupied_country_tag = <scope> / <variable>` The country to check.  `modifier = <token>`The modifier to check. | `has_core_occupation_modifier = { occupied_country_tag = ITA modifier = token }` | Checks if the current scope has an occupation modifier for resistance/compliance that applies to our occupied states of a specified country. |  | 1.9 |
| <a id="occupation-law"></a> occupation\_law | `<law ID>` The law to check. | `POL = { POL = { occupation_law = foreign_civilian_oversight } }`  # Checks POL's default occupation law  `HOL = { BEL = { occupation_law = foreign_civilian_oversight } }`  # Checks HOL's occupation law over BEL | Checks the occupation law that's either the default or applied over a specific country. | Checks [PREV's](<Scopes - Hearts of Iron 4 Wiki.md#prev-usage>) occupation law over the current country. If they're the same scope, checks the default occupation law. [Can also be used in state scope.](#s-occupation-law) | 1.12 |
| <a id="has-contested-owner"></a> has\_contested\_owner | `<state> / <variable>` State to check. | `has_contested_owner = 42` | Checks if a state has the specified country as a contested owner. The trigger can be used either from a country or a state scope and accepts the other as parameter. | [Can also be used in state scope.](#s-has-contested-owner) | 1.15 |
| <a id="owns-any-state-of"></a> owns\_any\_state\_of | `<states>` States to check. | `owns_any_state_of = { 123 246 }` | Check if the country owns any of the states in the list. | The same as:  `OR = { owns_state = 123 owns_state = 246 }` | 1.16 |
| <a id="is-on-same-continent-as"></a> is\_on\_same\_continent\_as | `<scope> / <variable>` The state to check for. | `is_on_same_continent_as = 111` | Checks if the scope country is on the same continent as the given state. The capital state is used for given country tag. | [Can also be used in state scope.](#s-is-on-same-continent-as) | 1.17 |

### <a id="military"></a>Military

Military-related country-scoped triggers:
| Name | Parameters | Examples | Description | Notes | Version Added |
| --- | --- | --- | --- | --- | --- |
| <a id="has-army-experience"></a> has\_army\_experience | `<float> / <variable>` The amount to check for. | `has_army_experience > 10`  `has_army_experience > var:number` | Checks if the current scope has the specified amount of Army experience. | **Must** use either > or < operators as = operator checks for the **exact** value | 1.3 |
| <a id="has-air-experience"></a> has\_air\_experience | `<float> / <variable>` The amount to check for. | `has_air_experience > 10` | Checks if the current scope has the specified amount of Air experience. | **Must** use either > or < operators as = operator checks for the **exact** value | 1.3 |
| <a id="has-navy-experience"></a> has\_navy\_experience | `<float> / <variable>` The amount to check for. | `has_navy_experience < 10` | Checks if the current scope has the specified amount of Navy experience. | **Must** use either > or < operators as = operator checks for the **exact** value | 1.3 |
| <a id="has-manpower"></a> has\_manpower | `<float> / <variable>` The amount to check for. | `has_manpower > 1000` | Checks if the current scope has the specified amount of manpower. | **Must** use either > or < operators as = operator checks for the **exact** value | 1.0 |
| <a id="has-army-manpower"></a> has\_army\_manpower | `size = <int>` The amount to check for. | `has_army_manpower = { size > 1000 }` | Checks if the current scope has an army using the specified amount of manpower. | Must use either > or < operators. | 1.0 |
| <a id="manpower-per-military-factory"></a> manpower\_per\_military\_factory | `<float>` The amount to check for. | `manpower_per_military_factory > 1000` | Checks if the current scope has the specified manpower times their number of military factories. | Must use either > or < operators. | 1.0 |
| <a id="conscription-ratio"></a> conscription\_ratio | `<float> / <variable>` The ratio to compare with. | `conscription_ratio < 0.2` | Checks if the current scope has the specified conscription ratio currently, not to be mixed up with the target conscription ratio. | **Must** use either > or < operators as = operator checks for the **exact** value | 1.9 |
| <a id="current-conscription-amount"></a> current\_conscription\_amount | `<float> / <variable>` The amount to compare with. | `current_conscription_amount > 2000` | Checks if the current scope has already conscripted that much manpower. | **Must** use either > or < operators as = operator checks for the **exact** value | 1.9 |
| <a id="target-conscription-amount"></a> target\_conscription\_amount | `<float> / <variable>` The amount to compare with. | `target_conscription_amount > 2000` | Checks if the current scope is targeting to conscript that much manpower. | **Must** use either > or < operators as = operator checks for the **exact** value | 1.9 |
| <a id="num-divisions"></a> num\_divisions | `<int>` The amount to check for. | `num_divisions > 5` | Checks if the current scope has the specified amount of divisions. | Must use either > or < operators. | 1.3 |
| <a id="num-of-nukes"></a> num\_of\_nukes | `<int>` The amount to check for. | `num_of_nukes > 5` | Checks if the current scope has the specified amount of nukes. | Must use either > or < operators. | 1.0 |
| <a id="casualties"></a> casualties | `<int>` The amount to check for. | `casualties > 10000` | Checks if the current scope has suffered the specified amount of casualties. | Must use either > or < operators. | 1.0 |
| <a id="casualties-k"></a> casualties\_k | `<int>` The amount to check for. | `casualties_k > 10` | Checks if the current scope has suffered the specified amount of casualties in thousands. | Must use either > or < operators. | 1.0 |
| <a id="casualties-inflicted-by"></a> casualties\_inflicted\_by | `opponent = <tag>` The tag that inflicted the casualties.  `thousands <> <int>`  The amount of casualties in thousands. | `casualties_inflicted_by = { opponent = POL thousands > 10 }` | Checks if the current scope has suffered the specified amount of casualties in thousands from a specific country. | Must use either > or < operators for thousands. | 1.6 |
| <a id="amount-manpower-in-deployment-queue"></a> amount\_manpower\_in\_deployment\_queue | `<float>` The amount to check for. | `amount_manpower_in_deployment_queue > 1000` | Checks if the current scope has the specified amount of manpower in their deployment queue. | Must use either > or < operators. | 1.5 |
| <a id="has-attache-from"></a> has\_attache\_from | `<scope> / <variable>` The country to check for. | `has_attache_from = GER` | Checks if the current scope has an attache from the specified scope. |  | 1.5 |
| <a id="has-attache"></a> has\_attache | `<bool>` Boolean. | `has_attache = yes` | Checks if the current scope has an attache. |  | 1.5 |
| <a id="is-lend-leasing"></a> is\_lend\_leasing | `<scope> / <variable>` The country to check for. | `is_lend_leasing = GER` | Checks if the current scope is lend leasing to the specified scope. |  | 1.0 |
| <a id="has-template"></a> has\_template | `<string>` The name of the template. | `has_template = "Infantry Division"` | Checks if the current scope has a division template of the specified name. |  | 1.0 |
| <a id="has-template-majority-unit"></a> has\_template\_majority\_unit | `<string>` The unit to check for. | `has_template_majority_unit = infantry` | Checks if the current scope has a division template composed mostly of the specified unit. |  | 1.0 |
| <a id="has-template-containing-unit"></a> has\_template\_containing\_unit | `<string>` The name of the unit. | `has_template_containing_unit = light_armor` | Checks if the current scope has a division template contained any of the specified unit. |  | 1.0 |
| <a id="strength-ratio"></a> strength\_ratio | `tag = <scope>` The country to check for. `ratio <> <float>` The ratio to check for. | `strength_ratio = { tag = GER ratio > 1 }` | Checks if the current scope has the specified strength ratio against the specified country. The ratio is the number of fielded divisions of the current scope divided by those of `tag` (or 1 if `tag` has no divisions). The ratio gets increased by 10% if the current scope has a stronger air forces.<a id="cite-ref-2"></a>[[2]](#cite-note-2) | Must use > or < in the ratio. | 1.0 |
| <a id="fighting-army-strength-ratio"></a> fighting\_army\_strength\_ratio | `tag = <scope>` The country to check for. `ratio <>= <float> / <variable>` The ratio to check for. | `fighting_army_strength_ratio = { tag = GER ratio > 0.7 }` | Compares the total army fighting strength between the scope country and the one set with 'tag'. | Ratio can be '<','>' or '='. | 1.15 |
| <a id="naval-strength-ratio"></a> naval\_strength\_ratio | `tag = <scope>` The country to check for. `ratio <> <float>` The ratio to check for. | `naval_strength_ratio = { tag = GER ratio <> 1 }` | Checks if the current scope has the specified naval strength ratio against the specified country. | Must use > or < in the ratio. | 1.0 |
| <a id="naval-strength-comparison"></a> naval\_strength\_comparison | `other = <scope>` The country to check for.  `tooltip = <string>` The ratio to check for. Optional.  `ratio <> <float>` The ratio to check for.  `sub_unit_def_weights = { ... }` The weight to assign to each unit. Optional. | `naval_strength_comparison = { other = POL tooltip = my_loc_key_tt ratio > 1 sub_unit_def_weights = { carrier = 1 submarine = 2 } }` | Checks if the current scope has the specified naval strength ratio against the specified country. | Must use > or < in the ratio. If sub\_unit\_def\_weights is unset, each unit is assumed to have 1 weight. If sub\_unit\_def\_weights is set, only specified units will be counted towards strength. Units are defined in /Hearts of Iron IV/common/units/\*.txt. | 1.6 |
| <a id="alliance-strength-ratio"></a> alliance\_strength\_ratio | `<float> / <variable>` The ratio to check for. | `alliance_strength_ratio > 0.5` | Checks if the current scope and allies has an army strength higher than the specified ratio against estimated enemy strength. | Must use either > or < operators. | 1.0 |
| <a id="alliance-naval-strength-ratio"></a> alliance\_naval\_strength\_ratio | `<float> / <variable>` The ratio to check for. | `alliance_naval_strength_ratio > 0.5` | Checks if the current scope and allies has an naval strength ratio higher than the specified ratio against estimated enemy strength. | Must use either > or < operators. | 1.0 |
| <a id="enemies-strength-ratio"></a> enemies\_strength\_ratio | `<float> / <variable>` The ratio to check for. | `enemies_strength_ratio > 0.5` | Checks if the estimated enemy army strength ratio is higher than the specified ratio. | Must use either > or < operators. | 1.0 |
| <a id="enemies-naval-strength-ratio"></a> enemies\_naval\_strength\_ratio | `<float> / <variable>` The ratio to check for. | `enemies_naval_strength_ratio > 0.5` | Checks if the estimated enemy naval strength ratio is higher than the specified ratio. | Must use either > or < operators. | 1.0 |
| <a id="has-army-size"></a> has\_army\_size | `size = <float>` The amount to check for.  `type = <string>` The battalion type to check for. Divisions that are majority made up of battalions in that type count. Optional, counts all divisions by default. | `has_army_size = { size > 10 type = armor }` | Checks if the current scope has the specified number of divisions, or of a specified type of division. | Battalion types are defined within /Hearts of Iron IV/common/units/\*.txt files. Must use either > or < operators for size. | 1.0 |
| <a id="has-navy-size"></a> has\_navy\_size | `size = <float> / <variable>` The amount to check for.  `type = <string>` The type to check for. Optional.  `archetype = <string>` The ship archetype to check for. Optional. | `has_navy_size = { size > 10 type = capital_ship archetype = ship_hull_heavy }` | Checks if the current scope has the specified number of ships, or of a specified type of ship. | Ship types are defined within /Hearts of Iron IV/common/units/\*.txt files. Must use either > or < operators for size. Ship archetypes are found in /Hearts of Iron IV/common/units/equipment/\*.txt files. | 1.0 |
| <a id="has-deployed-air-force-size"></a> has\_deployed\_air\_force\_size | `size = <float>` The amount to check for.  `type = <string>` The type to check for. Optional. | `has_deployed_air_force_size = { size > 10 type = cas }` | Checks if the current scope has the specified number of aircraft, or of a specified type of aircraft. | Airwing types are defined within /Hearts of Iron IV/common/units/\*.txt files. Must use either > or < operators for size. | 1.0 |
| <a id="divisions-in-state"></a> divisions\_in\_state | `size = <float>` The amount to check for.  `type = <string>` The battalion type to check for. Divisions that are majority made up of battalions in that type count. Optional, counts all divisions by default.  `unit = <string>` The exact battalion to check for. Divisions that are majority made up of that battalions count. Optional, counts all divisions by default.  `state = <scope> / <variable>` The state to check in. | `divisions_in_state = { type = armor size > 10 state = 49 }` | Checks if the specified state contains the specified amount of divisions. | Battalions and their types are defined within /Hearts of Iron IV/common/units/\*.txt files. Must use either > or < operators for size. | 1.0 |
| <a id="army-manpower-in-state"></a> army\_manpower\_in\_state | `amount <> <float>` The amount to check for.  `type = <string>` The type to check for. Optional.  `state = <scope> / <variable>` The state to check in. | `army_manpower_in_state = { type = support amount > 10000 state = 49 }` | Checks if the specified state contains the specified amount of army manpower within the state. | Battalion types are defined within /Hearts of Iron IV/common/units/\*.txt files. Must use either > or < operators for size. | 1.6 |
| <a id="divisions-in-border-state"></a> divisions\_in\_border\_state | `size = <float>` The amount to check for.  `type = <string>` The battalion type to check for. Divisions that are majority made up of battalions in that type count. Optional, counts all divisions by default.  `state = <scope> / <variable>` The state to check in.  `border_state = <scope> / <variable>` The border state to check in. | `divisions_in_border_state = { type = infantry size > 10 state = 49 border_state = var:state }` | Checks if the border provinces between the specified state and border state contain the specified amount of divisions. | Battalion types are defined within /Hearts of Iron IV/common/units/\*.txt files. Must use either > or < operators for size. | 1.5 |
| <a id="num-divisions-in-states"></a> num\_divisions\_in\_states | `count = <int>` The amount to check for.  `states = { <int> <...> <int> }` The states to check in.  `types = { <string> <...> <string> }` The battalion types to check for. Divisions that are majority made up of battalions in that type count. Optional, counts all divisions by default.  `exclude = { <string> <...> <string> }` The sub-units to exclude from the search. Divisions that are majority made up of specified battalions are excluded. Optional, excludes no divisions by default. | `num_divisions_in_states = { count > 24 states = { 550 559 271 } exclude = { irregular_infantry } }` | Checks if the specified states contain enough divisions of the specified types. | Divisions and their types are defined within /Hearts of Iron IV/common/units/\*.txt files. Can use either =, >, or < operators for count. The tooltip does not specify the states the check runs for nor the filtered types. | 1.12 |
| <a id="num-battalions-in-states"></a> num\_battalions\_in\_states | `count = <int>` The amount to check for.  `states = { <int> <...> <int> }` The states to check in.  `types = { <string> <...> <string> }` The battalion types to check for.  `exclude = { <string> <...> <string> }` The sub-units to exclude from the search. | `num_battalions_in_states = { count > 24 states = { 550 559 271 } exclude = { irregular_infantry } }` | Checks if the specified states contain enough battalions (or sub-units) of the specified types. | Battalions and their types are defined within /Hearts of Iron IV/common/units/\*.txt files. Can use either =, >, or < operators for count. The tooltip does not specify the states the check runs for nor the filtered types. | 1.12 |
| <a id="ships-in-state-ports"></a> ships\_in\_state\_ports | `size = <float>` The amount to check for.  `type = <string>` The type to check for. Optional.  `state = <scope> / <variable>` The state to check in. | `ships_in_state_ports = { type = capital_ship size > 10 state = 49 }` | Checks if the specified state contains the specified amount of ships, or of ships of the specified type. | Ship types are defined within /Hearts of Iron IV/common/units/\*.txt files. Must use either > or < operators for size. | 1.0 |
| <a id="num-planes-stationed-in-regions"></a> num\_planes\_stationed\_in\_regions | `value = <float>` The amount to check for.  `regions = { <id> <...> <id> }` The regions to check in. | `num_planes_stationed_in_regions = { value > 10 regions = { 123 321 } }` | Checks if the current scope has the specified number of aircraft stationed within strategic regions. | Must use either =, >, or < operators for value. | 1.12 |
| <a id="has-volunteers-amount-from"></a> has\_volunteers\_amount\_from | `tag = <scope>` The country to check for.  `count = <int>` The amount to check for. | `has_volunteers_amount_from = { tag = GER count > 10 }` | Checks if the current scope has recieved volunteers from the specified country of the specified amounts. | Must use either > or < operators for count. | 1.0 |
| <a id="convoy-threat"></a> convoy\_threat | `<float>` The threat to compate with. | `convoy_threat > 0.5` | Checks how much the convoys are threatened. | Must use either > or < operators for count. Threat is always between 0 and 1. | 1.6 |
| <a id="has-mined"></a> has\_mined | `target = <tag>` The country the coast of which is mined.  `value <> <int>` The amount of mines to compare with. | `has_mined = { target = POL value > 1000 }` | Checks if the current scope has X mines on the coast of the specified country. | Must use either > or < operators for value. | 1.6 |
| <a id="has-mines"></a> has\_mines | `region = <ID>` The strategic region that contains the mines.  `amount = <int>` The amount of mines to compare with. | `has_mined = { target = POL amount = 1000 }` | Checks if the current scope has at least X mines within the specified strategic region. |  | 1.6 |
| <a id="mine-threat"></a> mine\_threat | `<float>` The threat to compate with. | `mine_threat < 0.6` | Checks how dangerous enemy mines are. | Must use either > or < operators for count. Threat is always between 0 and 1. | 1.6 |
| <a id="has-military-industrial-organization"></a> has\_military\_industrial\_organization | `<token>` The id to check for. | `has_military_industrial_organization = infantry_mio_token` | Checks if the current scope has a MIO with the specified name. | Accepts variables. | 1.13 |
| <a id="has-tactic"></a> has\_tactic | `<tactic>` The tactic to check for. | `has_tactic = tactic_masterful_blitz` | Check if the given tactic is unlocked (or active by default) for the country. |  | 1.17 |

### <a id="doctrine"></a>Doctrine

Doctrine-related country-scoped triggers:
| Name | Parameters | Examples | Description | Notes | Version Added |
| --- | --- | --- | --- | --- | --- |
| <a id="has-any-grand-doctrine"></a> has\_any\_grand\_doctrine | `<string>` Doctrine folder. | `has_any_grand_doctrine = land` | Checks if any grand doctrine in folder is currently active for the country. | Folders are land, naval and air. | 1.17.2 |
| <a id="has-doctrine"></a> has\_doctrine | `<grand doctrine> / <subdoctrine>` The doctrine to check for. | `has_doctrine = mobile_warfare # Grand doctrine`  `has_doctrine = mobile_infantry # Subdoctrine` | Checks if the given grand doctrine or subdoctrine is currently active for the country. |  | 1.17 |
| <a id="has-subdoctrine-in-track"></a> has\_subdoctrine\_in\_track | `<track>` The track to check for. | `has_subdoctrine_in_track = infantry` | Checks if any subdoctrine is currently assigned to (any instance of) the given track. |  | 1.17 |
| <a id="has-completed-subdoctrine"></a> has\_completed\_subdoctrine | `<subdoctrine>` The subdoctrine to check for. | `has_completed_subdoctrine = mobile_infantry` | Checks if the current country has ever completed the specified subdoctrine (even if it was later switched out). |  | 1.17 |
| <a id="has-completed-track"></a> has\_completed\_track | `<track>` The track to check for. | `has_completed_track = infantry` | Checks if the given subdoctrine track has been completed |  | 1.17 |
| <a id="has-mastery"></a> has\_mastery | `amount = <int>` The amout to check for. `track = <track>` The track to check for. | `has_mastery = { amount = 200 track = infantry }` | Checks if any track of the given type has at least X mastery. |  | 1.17 |
| <a id="has-mastery-level"></a> has\_mastery\_level | `amount = <int>` The amount to check for. `subdoctrine = <subdoctrine>` The subdoctrine to check for. | `has_mastery_level = { amount = 2 subdoctrine = mobile_infantry }` | Checks if the country has reached the specified number of mastery levels (rewards) for the given subdoctrine. |  | 1.17 |

### <a id="equipment"></a>Equipment

Equipment-related country-scoped triggers:
| Name | Parameters | Examples | Description | Notes | Version Added |
| --- | --- | --- | --- | --- | --- |
| <a id="stockpile-ratio"></a> stockpile\_ratio | `archetype = <string>` The equipment archetype to check for.  `ratio = <float>` The ratio of equipment to check for. | `stockpile_ratio = { archetype = infantry_equipment ratio > 0.5 }` | Checks if the current scope has stockpiled the specified equipment to the specified ratio against fielded equipment of the same type. | Must use either > or < operators for ratio.   For the convoy equipment which is not fielded as other equipments, ratio shall be not a percentage but a direct amount (for instance 256 convoys) | 1.5 |
| <a id="has-equipment"></a> has\_equipment | `<equipment> = <int> / <variable>` The equipment to check for, and the amount to check for. | `has_equipment = { infantry_equipment_1 > 10 }` | Checks if the current scope has the specified equipment to the specified amount. | Must use either > or < operators. | 1.0 |
| <a id="has-any-license"></a> has\_any\_license | `<bool>` Boolean. | `has_any_license = yes` | Checks if the current scope has any licenses from other countries. |  | 1.0 |
| <a id="is-licensing-any-to"></a> is\_licensing\_any\_to | `<scope> / <variable>` The country to check for. | `is_licensing_any_to = GER` | Checks if the current scope is licensing to the specified scope. |  | 1.0 |
| <a id="is-licensing-to"></a> is\_licensing\_to | `target = <scope>` The country to check for. `archetype = <string>` The equipment archetype to check for. Optional.  **Equipment scope**  `type = <string>` The equipment to check for. Optional.  `version = <int>` The variant id of the equipment. Optional. | `is_licensing_to = { target = GER archetype = infantry_equipment }`  `is_licensing_to = { target = GER equipment = { type = light_tank_equipment version = 1 } }` | Checks if the current scope is licensing the specified equipment to the specified country. |  | 1.0 |
| <a id="has-license"></a> has\_license | `from = <scope>` The country to check for. `archetype = <string>` The equipment archetype to check for. Optional.  **Equipment scope**  `type = <string>` The equipment to check for. Optional.  `version = <int>` The variant id of the equipment. Optional. | `has_license = { from = GER archetype = infantry_equipment }`  `has_license = { from = GER equipment = { type = light_tank_equipment version = 1 } }` | Checks if the current scope has a license for the specified equipment from the specified country. |  | 1.0 |
| <a id="fuel-ratio"></a> fuel\_ratio | `<float> / <variable>` The ratio to check with. | `fuel_ratio > 0.4` | Checks the fuel ratio of the country. | Must use either < or > operators. | 1.6 |
| <a id="has-fuel"></a> has\_fuel | `<int> / <variable>` The amount to compare with. | `has_fuel > 400` | Checks the fuel amount of the country. | Must use either < or > operators. | 1.6 |
| <a id="has-design-based-on"></a> has\_design\_based\_on | `<archetype>` The equipment archetype. | `has_design_based_on = light_tank_chassis` | Checks if the country has a builtable non-obsolete design based on the specified equipment archetype. | Equipment archetypes can be seen in /Hearts of Iron IV/common/units/equipment/\*. | 1.11 |

### <a id="intelligence"></a>Intelligence

Intelligence-related country-scoped triggers:
| Name | Parameters | Examples | Description | Notes | Version Added |
| --- | --- | --- | --- | --- | --- |
| <a id="estimated-intel-max-piercing"></a> estimated\_intel\_max\_piercing | `tag = <scope>` The country to check for.  `value = <int>` The amount to check for. | `estimated_intel_max_piercing = { tag = GER value > 2 }` | Checks if the specified scope has the specified amount of piercing based on the current scope's intel. | Must use either > or < operators for value. | 1.0 |
| <a id="estimated-intel-max-armor"></a> estimated\_intel\_max\_armor | `tag = <scope>` The country to check for.  `value = <int>` The amount to check for. | `estimated_intel_max_armor = { tag = GER value > 2 }` | Checks if the specified scope has the specified amount of armor based on the current scope's intel. | Must use either > or < operators for value. | 1.0 |
| <a id="compare-intel-with"></a> compare\_intel\_with | `target = <tag> / <variable>` The target to compare with.  `civilian_intel <>= <float> / <variable>` Comparison of civilian intel.  `army_intel <>= <float> / <variable>` Comparison of army intel.  `navy_intel <>= <float> / <variable>` Comparison of navy intel.  `airforce_intel <>= <float> / <variable>` Comparison of airforce intel. | `compare_intel_with = { target = POL civilian_intel > 0.5 army_intel = 0 navy_intel < 0 }` | Compares intel between 2 countries. | Can use < (in which case the current country has x less intel), >, and = (in which case it must be equal). | 1.9 |
| <a id="intel-level-over"></a> intel\_level\_over | `target = <tag> / <variable>` The target to compare with.  `civilian_intel <>= <float> / <variable>` Comparison of civilian intel.  `army_intel <>= <float> / <variable>` Comparison of army intel.  `navy_intel <>= <float> / <variable>` Comparison of navy intel.  `airforce_intel <>= <float> / <variable>` Comparison of airforce intel. | `intel_level_over = { target = POL civilian_intel > 0.5 army_intel = 0 navy_intel < 0 }` | Checks the intel level from the current country over a specified country. | Can use < (in which case the current country has x less intel), >, and = (in which case it must be equal). | 1.9 |
| <a id="has-intelligence-agency"></a> has\_intelligence\_agency | `<boolean>` The intelligence agency to check. | `has_intelligence_agency = yes` | Checks if the current scope has an intelligence agency. |  | 1.9 |
| <a id="network-national-coverage"></a> network\_national\_coverage | `target = <tag> / <variable>` The country which is checked.  `value <> <float> / <variable>` The value of network. | `network_national_coverage = { target = POL value < 70 }` | Checks network national coverage over a specific country. | Must use < or > for value. |  |
| <a id="network-strength"></a> network\_strength | `target = <tag>` The country which is checked.  `state = <id> / <variable>` The state which is checked.  `value <> <float> / <variable>` The strength of network. | `network_strength = { target = POL value < 70 }` | Checks network national coverage over a specific country. | Must use < or > for value. Can use either or both of target and state. | 1.9 |
| <a id="has-done-agency-upgrade"></a> has\_done\_agency\_upgrade | `<string>` The agency upgrade to check. | `has_done_agency_upgrade = upgrade_army_department` | Checks if the current scope has the specified agency upgrade (to its highest level). |  | 1.9 |
| <a id="agency-upgrade-number"></a> agency\_upgrade\_number | `<int> / <variable>` The amount of agency upgrades to check for. | `agency_upgrade_number > 4` | Checks the number of upgrades done in the current scope's intelligence agency. | Must use either > or < operators. | 1.9 |
| <a id="decryption-progress"></a> decryption\_progress | `target = <tag>` The country to compare with.  `value <> <float>` The value to compare. | `decryption_progress = { target = POL value < 0.5 }` | Checks the decryption progress towards a country. | Must use either > or < operators for value. | 1.9 |
| <a id="has-captured-operative"></a> has\_captured\_operative | `<tag>/<bool>` Country whose operative was captured/Whether an operative was captured. | `has_captured_operative = POL`  `has_captured_operative = yes` | Checks if the current scope has captured an operative. |  | 1.9 |
| <a id="has-finished-collecting-for-operation"></a> has\_finished\_collecting\_for\_operation | `target = <tag>` Country towards whom the operation is targeted.  `operation = <token>` The operation which current scope is planning against the target. | `has_finished_collecting_for_operation = { target = POL operation = operation_infiltrate_armed_forces_navy }` | Checks if the current scope has finished collecting resources for an operation. |  | 1.9 |
| <a id="is-preparing-operation"></a> is\_preparing\_operation | `target = <tag>` Country towards whom the operation is targeted.  `operation = <token>` The operation which current scope is planning against the target. Optional. | `is_preparing_operation = { target = POL operation = operation_infiltrate_armed_forces_navy }` | Checks if the current scope is preparing an operation against the specified country. |  | 1.9 |
| <a id="is-running-operation"></a> is\_running\_operation | `target = <tag>` Country towards whom the operation is targeted.  `operation = <token>` The operation which current scope is planning against the target. Optional. | `is_running_operation = { target = POL operation = operation_infiltrate_armed_forces_navy }` | Checks if the current scope is running an operation against the specified country. |  | 1.9 |
| <a id="num-finished-operations"></a> num\_finished\_operations | `target = <tag>` Country towards whom the operation is targeted.  `operation = <token>` The operation which current scope is planning against the target. Optional. | `num_finished_operations = { target = POL operation = operation_infiltrate_armed_forces_navy }` | Checks how many finished operations the current scope had against the specified country. |  | 1.9 |
| <a id="has-operation-token"></a> has\_operation\_token | `tag = <tag>` Country towards whom the operation is targeted.  `token = <token>` The operation token. | `has_operation_token = { tag = POL token = token_name }` | Checks if the current scope has an operation token against an another country. |  | 1.9 |
| <a id="is-active-decryption-bonuses-enabled"></a> is\_active\_decryption\_bonuses\_enabled | `<tag>` The country towards which the bonus is enabled. | `is_active_decryption_bonuses_enabled = POL` | Checks if the current scope has any decryption bonuses towards the specified country. |  | 1.9 |
| <a id="is-cryptology-department-active"></a> is\_cryptology\_department\_active | `<bool>` Boolean. | `is_cryptology_department_active = yes` | Checks if the current scope has a cryptology department active. |  | 1.9 |
| <a id="is-decrypting"></a> is\_decrypting | `<tag>` The country which is decrypted. | `is_decrypting = POL` | Checks if the current scope is decrypting a certain country. |  | 1.9 |
| <a id="is-fully-decrypted"></a> is\_fully\_decrypted | `<tag>` The country which is decrypted. | `is_fully_decrypted = POL` | Checks if the current scope has fully decrypted a certain country. |  | 1.9 |
| <a id="num-fake-intel-divisions"></a> num\_fake\_intel\_divisions | `<int>` Amount of divisions. | `num_fake_intel_divisions > 10` | Checks the amount of fake intel divisions. | Must use either < or >. | 1.9 |
| <a id="num-free-operative-slots"></a> num\_free\_operative\_slots | `<int>` Amount of slots. | `num_free_operative_slots > 2` | Checks the amount of free operative slots. | Must use either < or >. | 1.9 |
| <a id="num-operative-slots"></a> num\_operative\_slots | `<int>` Amount of slots. | `num_operative_slots > 2` | Checks the amount of operative slots. | Must use either < or >. | 1.9 |
| <a id="num-of-operatives"></a> num\_of\_operatives | `<int>` Amount of operatives. | `num_of_operatives > 2` | Checks the amount of operatives. | Must use either < or >. | 1.9 |

### <a id="ai"></a>AI

AI-related country-scoped triggers:
| Name | Parameters | Examples | Description | Notes | Version Added |
| --- | --- | --- | --- | --- | --- |
| <a id="ai-irrationality"></a> ai\_irrationality | `<int>` The amount to check for. | `ai_irrationality > 10` | Checks if the current scope AI has the specified irrationality. | Must use either > or < operators. | 1.0 |
| <a id="ai-liberate-desire"></a> ai\_liberate\_desire | `target = <scope>` The country to check for. `count = <float>` The amount to check for. | `ai_liberate_desire = { target = GER count > 1 }` | Checks if the current scope AI has the specified liberation desire towards the specified country. | Must use either > or < operators for count. | 1.0 |
| <a id="ai-has-role-division"></a> ai\_has\_role\_division | `<string>` The role to check for. | `ai_has_role_division = infantry` | Checks if the current scope AI has a division with the specified role. | Roles are defined in /Hearts of Iron IV/common/ai\_templates/\*.txt | 1.0 |
| <a id="ai-has-role-template"></a> ai\_has\_role\_template | `<string>` The role to check for. | `ai_has_role_template = armor` | Checks if the current scope AI has a division template with the specified role. | Roles are defined in /Hearts of Iron IV/common/ai\_templates/\*.txt | 1.0 |
| <a id="ai-wants-divisions"></a> ai\_wants\_divisions | `<int>` The amount to check for. | `ai_wants_divisions > 10` | Checks if the current scope AI desires the specified amount of divisions. | Must use either > or < operators. | 1.0 |
| <a id="has-template-ai-majority-unit"></a> has\_template\_ai\_majority\_unit | `<string>` The unit to check for. | `has_template_ai_majority_unit = infantry` | Checks if the current scope AI has a division template mostly made up of the specified unit. |  | 1.0 |

### <a id="characters"></a>Characters

These are character-related triggers in the country scope, not [character-scoped triggers](#character-scope).

Character-related country-scoped triggers:
| Name | Parameters | Examples | Description | Notes | Version Added |
| --- | --- | --- | --- | --- | --- |
| <a id="can-be-country-leader"></a> can\_be\_country\_leader | `<character>` The character to check. | `can_be_country_leader = POL_character_test` | Checks if the specified character has a country leader role, active or not, and can utilise it in this country. |  | 1.11 |
| <a id="has-character"></a> has\_character | `<string>` The character to check. | `has_character = my_character` | Checks if the current scope has the specified character recruited. The character does NOT need to be in power. |  | 1.11 |
| <a id="has-country-leader"></a> has\_country\_leader | `ruling_only = <bool>`(default = yes) Limit check to ruling only.   `character = <character_token>` (recommended criteria) The character to check for. Optional.  `name = <string>` The name to check for. Optional.  `id = <int>` The id to check for. Optional. | `has_country_leader = { id = 10 }`  `has_country_leader = { character = SPR_niceto_alcala_zamora ruling_only = yes }`  `has_country_leader = { name = "John Smith" ruling_only = yes }` | Checks if the current scope has the specified country leader. |  | 1.3 |
| <a id="has-country-leader-ideology"></a> has\_country\_leader\_ideology | <ideology> Checks the ideology of the active country leader | `has_country_leader_ideology = nazism` | Checks if the current scope's active country leader has the specified ideology. |  | 1.11 |
| <a id="has-country-leader-with-trait"></a> has\_country\_leader\_with\_trait | `<string>` The trait to check. | `has_country_leader_with_trait = champion_of_peace_1` | Checks if the leader of the country has a specific trait. |  | 1.6 |
| <a id="is-female"></a> is\_female | `<bool>` Boolean. | `is_female = yes` | Checks if the current country leader is female. |  | 1.9 |
| <a id="has-unit-leader"></a> has\_unit\_leader | `<int>` The id to check for. | `has_unit_leader = 1` | Checks if the current scope has a unit leader with the specified id. | Only the legacy ID can be used, the character ID doesn't work. | 1.0 |
| <a id="has-scientist-specialization"></a> has\_scientist\_specialization | `specialization = <specialization_token>` Specialization. | `has_scientist_specialization = specialization_nuclear` | Checks if the country in scope has a scientist with a skill level of at least 1 in specialization. |  | 1.15 |

### <a id="peace-conferences"></a>Peace conferences

These are not exactly peace conference-related triggers, but **those that can only be used within peace conferences**.

Peace conference-only country-scoped triggers:
| Name | Parameters | Examples | Description | Notes | Version Added |
| --- | --- | --- | --- | --- | --- |
| <a id="pc-is-winner"></a> pc\_is\_winner | `<bool>` Boolean. | `pc_is_winner = yes` | Checks if the current scope is a winner within the peace conference. |  | 1.12 |
| <a id="pc-is-on-winning-side"></a> pc\_is\_on\_winning\_side | `<bool>` Boolean. | `pc_is_on_winning_side = yes` | Checks if the current scope is on the winning side within the peace conference. |  | 1.12 |
| <a id="pc-is-loser"></a> pc\_is\_loser | `<bool>` Boolean. | `pc_is_loser = yes` | Checks if the current scope is a loser within the peace conference. |  | 1.12 |
| <a id="pc-is-untouched-loser"></a> pc\_is\_untouched\_loser | `<bool>` Boolean. | `pc_is_untouched_loser = yes` | Checks if the current scope is an untouched loser within the peace conference. |  | 1.12 |
| <a id="pc-is-on-same-side-as"></a> pc\_is\_on\_same\_side\_as | `<scope>` Country to check for. | `pc_is_on_same_side_as = BHR` | Checks if the current scope is on the same side of the peace conference as the specified country. |  | 1.12 |
| <a id="pc-is-liberated"></a> pc\_is\_liberated | `<bool>` Boolean. | `pc_is_liberated = yes` | Checks if the current scope has been liberated within the peace conference. |  | 1.12 |
| <a id="pc-is-liberated-by"></a> pc\_is\_liberated\_by | `<scope>` Country to check for. | `pc_is_liberated_by = BHR` | Checks if the current scope has been liberated within the peace conference by the specified country. |  | 1.12 |
| <a id="pc-is-puppeted"></a> pc\_is\_puppeted | `<bool>` Boolean. | `pc_is_puppeted = yes` | Checks if the current scope has been puppeted within the peace conference. |  | 1.12 |
| <a id="pc-is-puppeted-by"></a> pc\_is\_puppeted\_by | `<scope>` Country to check for. | `pc_is_puppeted_by = BHR` | Checks if the current scope has been puppeted within the peace conference by the specified country. |  | 1.12 |
| <a id="pc-is-forced-government"></a> pc\_is\_forced\_government | `<bool>` Boolean. | `pc_is_forced_government = yes` | Checks if the current scope has had an enforced government change within the peace conference. |  | 1.12 |
| <a id="pc-is-forced-government-by"></a> pc\_is\_forced\_government\_by | `<scope>` Country to check for. | `pc_is_forced_government_by = BHR` | Checks if the current scope has had an enforced government change within the peace conference demanded by the specified country. |  | 1.12 |
| <a id="pc-is-forced-government-to"></a> pc\_is\_forced\_government\_to | `<ideology group>` Ideology group to check for. | `pc_is_forced_government_to = democratic` | Checks if the current scope has had an enforced government change to the specified ideology group. |  | 1.12 |
| <a id="pc-total-score"></a> pc\_total\_score | `<decimal>` Scope to check for. | `pc_total_score > 2400` | Checks if the current scope has the specified amount in total score within the peace conference. | Can only be used for the winning countries. | 1.12 |
| <a id="pc-current-score"></a> pc\_current\_score | `<decimal>` Scope to check for. | `pc_current_score > 100` | Checks if the current scope has the specified amount in current score within the peace conference. | Can only be used for the winning countries. | 1.12 |

## <a id="faction-scope"></a>Faction scope

Can be used in **faction** scope.

There are currently no faction-specific triggers.

## <a id="every-state"></a><a id="state-scope"></a>State scope

Can be used in **state** scope.

### <a id="general_3"></a>General

General state-scoped triggers:
| Name | Parameters | Examples | Description | Notes | Version Added |
| --- | --- | --- | --- | --- | --- |
| <a id="state"></a> state | `<scope> / <variable>` The state to check for. | `state = 10`  `state = var:state` | Checks if the current scope is the specified state. |  | 1.0 |
| <a id="region"></a> region | `<int>` The strategic region id to check for. | `region = 10` | Checks if the current scope is a state in the specified strategic region. |  | 1.0 |
| <a id="s-building-count-trigger"></a> <building> (building\_count\_trigger) | `<int>` The amount of the specified building to check for. | `arms_factory > 10` | Checks if the current scope has the specified amount of the specified building. | Must use either > or < operators. [Can also be used in building scope.](#building-count-trigger) | 1.0 |
| <a id="free-building-slots"></a> free\_building\_slots | `building = <string>` The building to check for.  `size = <int>` The amount to check for.  `include_locked = <bool>` Whether to include locked slots. | `free_building_slots = { building = arms_factory size > 10 include_locked = yes }` | Checks if the current scope has available slots for the specified amount of buildings. | Must use either > or < operators for size. | 1.0 |
| <a id="non-damaged-building-level"></a> non\_damaged\_building\_level | `building = <string>` The building to check for.  `level = <int>` The amount to check for. | `non_damaged_building_level = { building = arms_factory level > 4 }` | Checks if the current scope has the specified amount of the specified buildings that are undamaged. | Must use either > or < operators for level. | 1.9 |
| <a id="any-province-building-level"></a> any\_province\_building\_level | `building = <string>` The building to check for.  `limit = <int>` The amount to check for.  **Province scope**  `id = <int>` The province to check for.  `limit_to_border = <bool>` Whether to limit check to border provinces. | `any_province_building_level = { province = { id = 445 id = 494 limit_to_border = yes } building = bunker level < 5 }` | Checks if the current scope has the specified provincal building at the specified amount in the specified provinces. | Must use either > or < operators for level. | 1.0 |
| <a id="has-state-flag"></a> has\_state\_flag | `<string>` The flag to check for. | `has_state_flag = my_flag` | Checks if the current scope has the specified flag. |  | 1.0 |
| <a id="has-state-flag"></a> has\_state\_flag | `flag = <string>` The flag to check.  `value = <int>` The flag value to check for. Optional.  `date = <date>` The flag creation date to check for. Optional.  `days = <int>` The duration the flag existed for. Optional. | `has_state_flag = { flag = my_flag days > 30 date > 1936.6.1 value > 0 }` | Compares the specified flag's last set date, days since last set, and/or value. | If not set, the value comparison is `>0`. `value` is limited between -32768 and 32767. | 1.0 |
| <a id="state-population"></a> state\_population | `<float>` The amount to check for. | `state_population > 10000` | Checks if the current scope has the specified state population. | Must use either > or < operators. | 1.0 |
| <a id="state-population-k"></a> state\_population\_k | `<float>` The amount to check for. | `state_population_k > 10` | Checks if the current scope has the specified state population in thousands. | Must use either > or < operators. | 1.0 |
| <a id="is-capital"></a> is\_capital | `<bool>` Boolean. | `is_capital = yes` | Checks if the current scope is a capital. |  | 1.5 |
| <a id="is-controlled-by"></a> is\_controlled\_by | `<scope> / <variable>` The country to check for. | `is_controlled_by = GER` | Checks if the current scope is controlled by the specified country. |  | 1.0 |
| <a id="is-fully-controlled-by"></a> is\_fully\_controlled\_by | `<scope> / <variable>` The country to check for. | `is_fully_controlled_by = GER` | Checks if the current scope is fully controlled by the specified country. |  | 1.5 |
| <a id="is-owned-by"></a> is\_owned\_by | `<scope> / <variable>` The country to check for. | `is_owned_by = GER` | Checks if the current scope is owned by the specified country. |  | 1.0 |
| <a id="is-claimed-by"></a> is\_claimed\_by | `<scope> / <variable>` The country to check for. | `is_claimed_by = GER` | Checks if the current scope is claimed by the specified country. |  | 1.0 |
| <a id="is-core-of"></a> is\_core\_of | `<scope> / <variable>` The country to check for. | `is_core_of = GER` | Checks if the current scope is a core of the specified country. |  | 1.0 |
| <a id="is-owned-and-controlled-by"></a> is\_owned\_and\_controlled\_by | `<scope> / <variable>` The country to check for. | `is_owned_and_controlled_by = GER` | Checks if the current scope is owned and controlled by the specified country. |  | 1.0 |
| <a id="is-demilitarized-zone"></a> is\_demilitarized\_zone | `<bool>` Boolean. | `is_demilitarized_zone = yes` | Checks if the current scope is a demilitarized zone. |  | 1.0 |
| <a id="is-border-conflict"></a> is\_border\_conflict | `<bool>` Boolean. | `is_border_conflict = yes` | Checks if the current scope is part of a border war. |  | 1.0 |
| <a id="is-in-home-area"></a> is\_in\_home\_area | `<bool>` Boolean. | `is_in_home_area = yes` | Checks if the current scope is connected to the capital state over land. The scope needs to be owned as well for the statement for it to be true. |  | 1.0 |
| <a id="is-coastal"></a> is\_coastal | `<bool>` Boolean. | `is_coastal = yes` | Checks if the current scope is a coastal state. |  | 1.0 |
| <a id="is-one-state-island"></a> is\_one\_state\_island | `<bool>` Boolean. | `is_one_state_island = yes` | Checks if the current scope is a coastal state with no adjacent land states. | An adjacent land state may be connected via a naval crossing. | 1.13 |
| <a id="is-island-state"></a> is\_island\_state | `<bool>` Boolean. | `is_island_state = yes` | Checks if the current scope is a state where every province has no land neighbour. | An adjacent land division may be connected via a naval crossing. | 1.0 |
| <a id="is-on-continent"></a> is\_on\_continent | `<string>` The continent to check for. | `is_on_continent = europe` | Checks if the current scope is on the specified continent. | Continents are found in /Hearts of Iron IV/map/continent.txt. | 1.0 |
| <a id="s-is-on-same-continent-as"></a> is\_on\_same\_continent\_as | `<scope> / <variable>` The country to check for. | `is_on_same_continent_as = FRA` | Checks if the scope state is on the same continent as the given state. The capital state is used for given country tag. | [Can also be used in country scope.](#is-on-same-continent-as) | 1.17 |
| <a id="impassable"></a> impassable | `<bool>` Boolean. | `impassable = yes` | Checks if the current scope is impassable. |  | 1.9.1 |
| <a id="has-state-category"></a> has\_state\_category | `<string>` The category to check for. | `has_state_category = rural` | Checks if the current scope has the specified category. | State categories are found in /Hearts of Iron IV/common/state\_category/\*.txt. | 1.0 |
| <a id="state-strategic-value"></a> state\_strategic\_value | `<int>` The amount to check for. | `state_strategic_value > 10` | Checks if the current scope has the specified strategic value. | Must use either > or < operators. | 1.5 |
| <a id="state-and-terrain-strategic-value"></a> state\_and\_terrain\_strategic\_value | `<int>` The amount to check for. | `state_and_terrain_strategic_value > 10` | Checks if the current scope has the specified state and terrain strategic value. | Must use either > or < operators. | 1.5 |
| <a id="num-owned-neighbour-states"></a> num\_owned\_neighbour\_states | `owner = <scope>` The country to check for. `count = <int>` The amount to check for. | `num_owned_neighbour_states = { owner = GER count > 2 }` | Checks if the current scope has the specified amount of neighbor states belonging to the specified country. | Must use either > or < operators for count. | 1.0 |
| <a id="distance-to"></a> distance\_to | `value = <float>` The distance to check for. `target = <scope>` The state to compare against. | `distance_to = { value > 1000 target = 49 }` | Checks if the current scope is at the specified distance from the specified state. | Must use either > or < operators for distance. | 1.0 |
| <a id="ships-in-area"></a> ships\_in\_area | `area = <int>` The strategic region to check for. `size = <int>` The amount to check for. | `ships_in_area = { area = 104 size > 14 }` | Checks if the current scope has the specified amount of ships in the specified strategic region. | Must use either > or < operators for count. | 1.0 |
| <a id="s-resource-count-trigger"></a> <resource> (resource\_count\_trigger) | `<int>` The amount to check for. | `tungsten > 10` | Checks if the current scope has the specified amount of the specified resource. | Must use either > or < operators for amount. [Can also be used in country scope.](#resource-count-trigger) | ??? |
| <a id="has-resources-amount"></a> has\_resources\_amount | `resource = <string>` The resource to check for.  `amount = <int>` The amount to check for.  `delivered = <bool>` If specified, checks the amount after the modifiers are applied rather than the base resource value. | `has_resources_amount = { resource = oil amount > 10 delivered = yes }` | Checks if the current scope has the specified amount of the specified resource. | Must use either > or < operators for amount. | 1.3 |
| <a id="s-has-resources-rights"></a> has\_resources\_rights | `receiver = <scope>` The receiver of the resource rights. Mandatory if used in state scope. `resources = { <resource> <...> <resource> }` Resources to check for. Optional, defaults to any if unset. | `has_resources_rights = { receiver = POL resources = { oil steel } }` | Checks if there are any resource rights with the specified parameters. | Can be used in either state or country scope. Always returns false if the state has no resources. [Can also be used in country scope.](#has-resources-rights) | 1.12 |
| <a id="days-since-last-strategic-bombing"></a> days\_since\_last\_strategic\_bombing | `<int>` The amount to compare with. | `days_since_last_strategic_bombing < 10` | Checks how many days have passed since the last strategic bombing of the state. | Must use either > or < operators. | 1.6 |
| <a id="has-railway-connection"></a> has\_railway\_connection | `<scope> / <variable>` The states to check. `<id>`  The provinces to check. Optional. | `has_railway_connection = { start_state = 10 target_state = 90 }`  `has_railway_connection = { start_province = 402 target_province = 9400 }` | Returns true if the states are connected by a railway. Can also check provinces. |  | 1.11 |
| <a id="can-build-railway"></a> can\_build\_railway | `<scope> / <variable>` The states to check. `<id>`  The provinces to check. Optional. | `can_build_railway = { start_state = 10 target_state = 90 }`  `can_build_railway = { start_province = 402 target_province = 9400 }` | Returns true if a railway can be built between states. Can also check for provinces. |  | 1.11 |
| <a id="has-railway-level"></a> has\_railway\_level | `<scope> / <variable>` The states to check. `<int>`  Railway level. | `has_railway_level = { state = 114 level = 5 }` | Checks if a state contains a railway at or above the specified level. | Works with level 1, 2, 3, 4 or 5. Level 0 does not work. | 1.11 |
| <a id="pc-does-state-stack-demilitarized"></a> pc\_does\_state\_stack\_demilitarized | `<bool>` Boolean. | `pc_does_state_stack_demilitarized = yes` | Checks if the current scope was demilitarised during a current or previously-ended peace conference. |  | 1.12 |
| <a id="pc-does-state-stack-dismantled"></a> pc\_does\_state\_stack\_dismantled | `<bool>` Boolean. | `pc_does_state_stack_dismantled = yes` | Checks if the current scope was dismantled during a current or previously-ended peace conference. |  | 1.12 |
| <a id="pc-is-state-claimed"></a> pc\_is\_state\_claimed | `<scope>` Country to check for. | `pc_is_state_claimed = yes` | Checks if the current scope was claimed by any country during the peace conference. | **Can only be used within peace conferences.** | 1.12.8 |
| <a id="pc-is-state-claimed-by"></a> pc\_is\_state\_claimed\_by | `<scope>` Country to check for. | `pc_is_state_claimed_by = BHR` | Checks if the current scope was claimed by the specified country during the peace conference. Note, that "claim" in this context, while includes, is NOT limited to outright taking: forcing government, puppeting and liberating will render that trigger true as well. If one looks specifically for states taken by victors for themselves, [pc\_is\_state\_claimed\_and\_taken\_by](#pc-is-state-claimed-and-taken-by) should be used. | **Can only be used within peace conferences.** | 1.12 |
| <a id="pc-is-state-claimed-and-taken-by"></a> pc\_is\_state\_claimed\_and\_taken\_by | `<scope>` Country to check for. | `pc_is_state_claimed_and_taken_by = SOV` | Checks if the current scope was claimed with "Take State" action (i.e. annexed) by the specified country during the peace conference. | **Can only be used within peace conferences.** |  |
| <a id="pc-is-state-outside-influence-for-winner"></a> pc\_is\_state\_outside\_influence\_for\_winner | `<scope>` Country to check for. | `pc_is_state_outside_influence_for_winner = ROOT` | Checks if the current state is outside of the influence of the specified winner country. | **Can only be used within peace conferences.** Was called pc\_is\_state\_outside\_influence\_for prior to 1.12.8. | 1.12.8 |
| <a id="pc-turn"></a> pc\_turn | `<int>` The amount of turns to check for. | `pc_turn > 20` | Compares the amount of turns that have passed during the peace conference with a number. | **Can only be used within peace conferences.** | 1.12.8 |
| can\_construct\_building | `<build type>`The type of building. | `can_construct_building = bunker` | Checks if the country (as ROOT) and state in scope can build a building in the state. |  | 1.15 |
| <a id="s-has-contested-owner"></a> has\_contested\_owner | `<country> / <variable>` Country to check. | `has_contested_owner = GER` | Checks if a state has the specified country as a contested owner. The trigger can be used either from a country or a state scope and accepts the other as parameter. | [Can also be used in country scope.](#has-contested-owner) | 1.15 |

### <a id="resistance-and-compliance"></a>Resistance and Compliance

Resistance-related state-scoped triggers:
| Name | Parameters | Examples | Description | Notes | Version Added |
| --- | --- | --- | --- | --- | --- |
| <a id="compliance"></a> compliance | `<int>` The amount to compare with. | `compliance > 50` | Compares the compliance value of the current scope with the given value. | Must use either > or < operators. | 1.9 |
| <a id="compliance-speed"></a> compliance\_speed | `<int>` The amount to compare with. | `compliance_speed > 50` | Compares the compliance speed of the current scope with the given value. | Must use either > or < operators. | 1.9 |
| <a id="has-active-resistance"></a> has\_active\_resistance | `<bool>` Boolean. | `has_active_resistance = yes` | Checks if the current scope has non-zero resistance. |  | 1.9 |
| <a id="has-resistance"></a> has\_resistance | `<bool>` Boolean. | `has_resistance = yes` | Checks if the current scope has resistance. |  | 1.9 |
| <a id="resistance"></a> resistance | `<int>` The amount to compare with. | `resistance > 50` | Compares the resistance value of the current scope with the given value. | Must use either > or < operators. | 1.9 |
| <a id="resistance-speed"></a> resistance\_speed | `<int>` The amount to compare with. | `resistance_speed > 50` | Compares the resistance speed of the current scope with the given value. | Must use either > or < operators. | 1.9 |
| <a id="resistance-target"></a> resistance\_target | `<int>` The amount to compare with. | `resistance_target > 50` | Compares the target resistance value of the current scope with the given value. | Must use either > or < operators. | 1.9 |
| <a id="has-occupation-modifier"></a> has\_occupation\_modifier | `<token>` The occupation modifier to check. | `has_occupation_modifier = modifier_name` | Checks if the current scope has an occupation modifier, changing resistance/compliance. |  | 1.9 |
| <a id="s-occupation-law"></a> occupation\_law | `<token>` The occupation law to check. | `occupation_law = law_name` | Checks if the current scope has an occupation law. | [Can also be used in country scope.](#occupation-law) | 1.9 |
| <a id="occupied-country-tag"></a> occupied\_country\_tag | `<tag>` The occupation tag to check. | `occupied_country_tag = POL` | Checks which country creates resistance. |  | 1.9 |

## <a id="character-scope"></a>Character scope

Can be used in **Character** scope.

### <a id="general_4"></a>General

General character-scoped triggers:
| Name | Parameters | Examples | Description | Notes | Version Added |
| --- | --- | --- | --- | --- | --- |
| <a id="is-character"></a> is\_character | `<scope>` Character ID. | `is_character = POL_test_character` | Checks if the current character's token matches up with the specified one. |  | 1.11 |
| <a id="can-be-country-leader"></a> can\_be\_country\_leader | `<bool>` Boolean. | `can_be_country_leader = yes` | Checks if the character in the current scope has a country leader role, active or non-active. |  | 1.11 |
| <a id="is-country-leader"></a> is\_country\_leader | `<bool>` Boolean. | `is_country_leader = yes` | Checks if the character in the current scope is the active country leader. |  | 1.11 |
| <a id="is-unit-leader"></a> is\_unit\_leader | `<bool>` Boolean. | `is_unit_leader = yes` | Checks if the character in the current scope has an active unit leader (Army/Navy leader) role. |  | 1.11 |
| <a id="is-advisor"></a> is\_advisor | `<bool>` Boolean. | `is_advisor = yes` | Checks if the character in the current scope has an advisor role (includes advisors/theorists/high command). |  | 1.11 |
| <a id="is-air-chief"></a> is\_air\_chief | `<bool>` Boolean. | `is_air_chief = yes` | Checks if the character in the current scope is selected as an air chief. | Prior to 1.12, checked if the character had a role within the slot, regardless of being selected. | 1.11 |
| <a id="is-army-chief"></a> is\_army\_chief | `<bool>` Boolean. | `is_army_chief = yes` | Checks if the character in the current scope is selected as an army chief. | Prior to 1.12, checked if the character had a role within the slot, regardless of being selected. | 1.11 |
| <a id="is-army-leader"></a> is\_army\_leader | `<bool>` Boolean. | `is_army_leader = yes` | Checks if the character in the current scope has an army leader (General/Field Marshal) role. |  | 1.11 |
| <a id="is-navy-chief"></a> is\_navy\_chief | `<bool>` Boolean. | `is_navy_chief = yes` | Checks if the character in the current scope is selected as a navy chief. | Prior to 1.12, checked if the character had a role within the slot, regardless of being selected. | 1.11 |
| <a id="is-navy-leader"></a> is\_navy\_leader | `<bool>` Boolean. | `is_navy_leader = yes` | Checks if the character in the current scope has an navy leader (Admiral) role. |  | 1.11 |
| <a id="is-high-command"></a> is\_high\_command | `<bool>` Boolean. | `is_high_command = yes` | Checks if the character in the current scope is selected as high command. | Prior to 1.12, checked if the character had a role within the slot, regardless of being selected. | 1.11 |
| <a id="is-corps-commander"></a> is\_corps\_commander | `<bool>` Boolean. | `is_corps_commander = yes` | Checks if the character in the current scope is a corps commander. |  | 1.11 |
| <a id="is-operative"></a> is\_operative | `<bool>` Boolean. | `is_operative = yes` | Checks if the character in the current scope is an operative. |  | 1.11 |
| <a id="is-political-advisor"></a> is\_political\_advisor | `<bool>` Boolean. | `is_political_advisor = yes` | Checks if the character in the current scope is selected as a political advisor. | Prior to 1.12, checked if the character had a role within the slot, regardless of being selected. | 1.11 |
| <a id="is-theorist"></a> is\_theorist | `<bool>` Boolean. | `is_theorist = yes` | Checks if the character in the current scope is selected as a theorist. | Prior to 1.12, checked if the character had a role within the slot, regardless of being selected. | 1.11 |
| <a id="is-character-slot"></a> is\_character\_slot | `<string>` The advisor slot to check. | `is_character_slot = political_advisor` | Checks if the character in the current scope has a role within the specified character slot | Character slots are defined within /Hearts of Iron IV/common/idea\_tags/\*.txt. | 1.11 |
| <a id="has-air-ledger"></a> has\_air\_ledger | `<bool>` Boolean. | `has_air_ledger = yes` | Checks if the character in the current scope has an air ledger. |  | 1.11 |
| <a id="has-army-ledger"></a> has\_army\_ledger | `<bool>` Boolean. | `has_army_ledger = yes` | Checks if the character in the current scope has an army ledger. |  | 1.11 |
| <a id="has-navy-ledger"></a> has\_navy\_ledger | `<bool>` Boolean. | `has_navy_ledger = yes` | Checks if the character in the current scope has an navy ledger. |  | 1.11 |
| <a id="has-character-flag"></a> has\_character\_flag | `<string>` The flag to check for. | `has_character_flag = my_flag` | Checks if the current scope has the specified flag. |  | 1.11 |
| <a id="has-character-flag"></a> has\_character\_flag | `flag = <string>` The flag to check.  `value = <int>` The flag value to check for. Optional.  `date = <date>` The flag creation date to check for. Optional.  `days = <int>` The duration the flag existed for. Optional. | `has_character_flag = { flag = my_flag days > 30 date > 1936.6.1 value > 0 }` | Compares the specified flag's last set date, days since last set, and/or value. | If not set, the value comparison is `>0`. `value` is limited between -32768 and 32767. | 1.11 |
| <a id="has-trait"></a> has\_trait | `<trait>` The trait to check for. | `has_trait = really_good_boss` | Checks if the current scope has the specified trait. |  | 1.5 |
| <a id="has-id"></a> has\_id | `<int>` The id to check for. | `has_id = 1` | Checks if the current character has the specificed ID. |  | 1.5 |

### <a id="advisors"></a>Advisors

These triggers are to be used specifically for advisors.

Advisor-scoped triggers:
| Name | Parameters | Examples | Description | Notes | Version Added |
| --- | --- | --- | --- | --- | --- |
| <a id="is-hired-as-advisor"></a> is\_hired\_as\_advisor | `<bool>` Boolean. | `is_hired_as_advisor = yes` | Checks if the current character is activated as an advisor in any slot. |  | 1.12.10 |
| <a id="not-already-hired-except-as"></a> not\_already\_hired\_except\_as | `<slot>` The slot to check in. | `not_already_hired_except_as = political_advisor` | Checks if the current character is not hired, with the exception of the specified slot. |  | 1.11 |
| <a id="advisor-can-be-fired"></a> advisor\_can\_be\_fired | `<bool>` Boolean.  **OR**  `slot = <slot>` The slot to check in. | `advisor_can_be_fired = no`  `advisor_can_be_fired = { slot = political_advisor }` | Checks if the current character's `can_be_fired` attribute is set or not within a certain slot. | If an advisor is available in multiple slots, the long version is mandatory to use. | 1.12.8 |
| <a id="has-advisor-role"></a> has\_advisor\_role | `<slot>` The slot to check in. | `has_advisor_role = political_advisor` | Checks if the character in scope has an advisor role for the given slot. | Possible advisor role slots. | ??? |

### <a id="country-leaders"></a>Country leaders

These triggers are to be used specifically for country leaders.

Country leader-scoped triggers:
| Name | Parameters | Examples | Description | Notes | Version Added |
| --- | --- | --- | --- | --- | --- |
| <a id="has-ideology"></a> has\_ideology | `<ideology>` The sub-ideology to check for. | `has_ideology = liberalism` | Checks if the current character has the specificed sub-ideology assigned. |  | 1.11 |
| <a id="has-ideology-group"></a> has\_ideology\_group | `<ideology>` The ideology to check for. | `has_ideology_group = democratic` | Checks if the current character has the specificed ideology assigned. |  | 1.11 |

### <a id="unit-leaders"></a>Unit leaders

These triggers are to be used specifically for unit leaders, i.e. generals and admirals.

Unit leader-scoped triggers:
| Name | Parameters | Examples | Description | Notes | Version Added |
| --- | --- | --- | --- | --- | --- |
| <a id="has-unit-leader-flag"></a> has\_unit\_leader\_flag | `<string>` The flag to check for. | `has_unit_leader_flag = my_flag` | Checks if the current scope has the specified flag. | Deprecated. Use has\_character\_flag instead. | 1.5 |
| <a id="has-unit-leader-flag"></a> has\_unit\_leader\_flag | `flag = <string>` The flag to check.  `value = <int>` The flag value to check for. Optional.  `date = <date>` The flag creation date to check for. Optional.  `days = <int>` The duration the flag existed for. Optional. | `has_unit_leader_flag = { flag = my_flag days > 30 date > 1936.6.1 value > 0 }` | Compares the specified flag's last set date, days since last set, and/or value. | Deprecated. Use has\_character\_flag instead. If not set, the value comparison is `>0`. `value` is limited between -32768 and 32767. | 1.5 |
| <a id="is-leading-army"></a> is\_leading\_army | `<bool>` Boolean. | `is_leading_army = yes` | Checks if the current scope is leading a single army. |  | 1.5 |
| <a id="is-leading-army-group"></a> is\_leading\_army\_group | `<bool>` Boolean. | `is_leading_army_group = yes` | Checks if the current scope is leading an army group. |  | 1.5 |
| <a id="is-leading-volunteer-group"></a> is\_leading\_volunteer\_group | `<tag>` Country tag. | `is_leading_volunteer_group = POL` | Checks if the current scope is leading a volunteer army within the specified country. | If the target country is in a civil war, this will only be valid for one side. | 1.11 |
| <a id="is-leading-volunteer-group-with-original-country"></a> is\_leading\_volunteer\_group\_with\_original\_country | `<tag>` Country tag. | `is_leading_volunteer_group_with_original_country = POL` | Checks if the current scope is leading a volunteer army within a country of the specified original tag. | If the target country is in a civil war, this will only be valid for each side. | 1.11 |
| <a id="is-field-marshal"></a> is\_field\_marshal | `<bool>` Boolean. | `is_field_marshal = yes` | Checks if the current scope is a Field Marshal. |  | 1.5 |
| <a id="is-assigned"></a> is\_assigned | `<bool>` Boolean. | `is_assigned = yes` | Checks if the current scope is an assigned unit leader. |  | 1.5 |
| <a id="can-select-trait"></a> can\_select\_trait | `<string>` The trait to check for. | `can_select_trait = offensive_doctrine` | Checks if the current scope can select the specified trait. |  | 1.5 |
| <a id="has-ability"></a> has\_ability | `<string>` The ability to check for. | `has_ability = glider_planes` | Checks if the current scope has the specified unit leader ability. |  | 1.5 |
| <a id="skill"></a> skill | `<int>` The amount to check for. | `skill > 1` | Checks if the current scope has a Skill above the specified amount. | Must use either > or < operators. | 1.5 |
| <a id="skill-advantage"></a> skill\_advantage | `<int>` The amount to check for. | `skill_advantage > 1` | Checks if the current scope has a Skill advantage above the specified amount in against an enemy unit leader whilst in combat. | Must use either > or < operators. | 1.5 |
| <a id="planning-skill-level"></a> planning\_skill\_level | `<int>` The amount to check for. | `planning_skill_level > 1` | Checks if the current scope has a Planning skill above the specified amount. | Must use either > or < operators. | 1.5 |
| <a id="logistics-skill-level"></a> logistics\_skill\_level | `<int>` The amount to check for. | `logistics_skill_level > 1` | Checks if the current scope has a Logistics skill above the specified amount. | Must use either > or < operators. | 1.5 |
| <a id="defense-skill-level"></a> defense\_skill\_level | `<int>` The amount to check for. | `defense_skill_level > 1` | Checks if the current scope has a Defense skill above the specified amount. | Must use either > or < operators. | 1.5 |
| <a id="attack-skill-level"></a> attack\_skill\_level | `<int>` The amount to check for. | `attack_skill_level > 1` | Checks if the current scope has a Attack skill above the specified amount. | Must use either > or < operators. | 1.5 |
| <a id="average-stats"></a> average\_stats | `<int>` The amount to check for. | `average_stats > 5` | Checks if the current scope has an average skill above the specified amount. | Must use either > or < operators. | 1.5 |
| <a id="is-border-war"></a> is\_border\_war | `<bool>` Boolean. | `is_border_war = yes` | Checks if the current socpe is in a border war. |  | 1.5 |
| <a id="num-units"></a> num\_units | `<int>` The amount to check for. | `num_units > 5` | Checks if the current scope is commanding the specified amount of divisions. | Must use either > or < operators. | 1.5 |
| <a id="is-exiled-leader"></a> is\_exiled\_leader | `<bool>` Boolean. | `is_exiled_leader = yes` | Checks if the current scope is a general from an exiled country. |  | 1.6 |
| <a id="is-exiled-leader-from"></a> is\_exiled\_leader\_from | `<tag>` Country. | `is_exiled_leader_from = POL` | Checks if the current scope is a general from the specified exiled country. |  | 1.6 |
| <a id="is-female"></a> is\_female | `<bool>` Boolean. | `is_female = yes` | Checks if the current scope is female. | Works for aces. | 1.9 |
| <a id="is-leading-army-in-province"></a> is\_leading\_army\_in\_province | `<province id>` | `is_leading_army_in_province = 1234` | Checks if the current unit leader is leading an army that has any division in a specific province |  | 1.17 |

### <a id="operatives"></a>Operatives

These triggers only work for operatives.

Operative-scoped triggers:
| Name | Parameters | Examples | Description | Notes | Version Added |
| --- | --- | --- | --- | --- | --- |
| <a id="has-nationality"></a> has\_nationality | `<tag>` The nationality to check. | `has_nationality = POL` | Checks if the current operative has the nationality. |  | 1.9 |
| <a id="is-operative-captured"></a> is\_operative\_captured | `<bool>` Boolean. | `is_operative_captured = yes` | Checks if the current scope is captured. |  | 1.9 |
| <a id="operative-leader-mission"></a> operative\_leader\_mission | `<token>` Mission. | `operative_leader_mission = mission_name` | Checks if the current scope is on the given mission. |  | 1.9 |
| <a id="operative-leader-operation"></a> operative\_leader\_operation | `<token>` Operation. | `operative_leader_operation = operation_name` | Checks if the current scope is on the given operation. |  | 1.9 |

### <a id="scientists"></a>Scientists

These triggers only work for scientists.

Scientist-scoped triggers:
| Name | Parameters | Examples | Description | Notes | Version Added |
| --- | --- | --- | --- | --- | --- |
| <a id="has-scientist-level"></a> has\_scientist\_level | `level = <int>` Level to check. `specialization = <specialization_token>` Specialization. | `has_scientist_level = { level > 2 specialization = specialization_nuclear }` | Checks if the scientist of the character in scope matches the skill level condition for a specialization. Supports < > = operators. |  | 1.15 |
| <a id="is-active-scientist"></a> is\_active\_scientist | `<bool>` | `is_scientist_active = yes` | Checks if the scientist of the character in scope is assigned to a project. |  | 1.15 |
| <a id="is-scientist-injured"></a> is\_scientist\_injured | `<bool>` | `is_scientist_injured = yes` | Checks if the scientist of the character in scope is injured. |  | 1.15 |

## <a id="combat"></a>Combat

These triggers are used within the combatant scope. Some trigger blocks in abilities, combat tactics, and unit leader traits check this, and it's impossible to access elsewhere.

Combatant-scoped triggers:
| Name | Parameters | Examples | Description | Notes | Version Added |
| --- | --- | --- | --- | --- | --- |
| <a id="hardness"></a> hardness | `<float>` The amount to check for. | `hardness > 0.5` | Checks if the current scope has the specified amount of hardness. | Must use either > or < operators. | 1.0 |
| <a id="armor"></a> armor | `<float>` The amount to check for. | `armor > 0.5` | Checks if the current scope has the specified amount of armor units. | Must use either > or < operators. | 1.0 |
| <a id="dig-in"></a> dig\_in | `<float>` The amount to check for. | `dig_in > 0.5` | Checks if the current scope has the specified amount of Dig In bonus. | Must use either > or < operators. | 1.0 |
| <a id="min-planning"></a> min\_planning | `<float>` The amount to check for. | `min_planning > 0.5` | Checks if the current scope has the specified amount of planning. | Must use either > or < operators. | 1.0 |
| <a id="fastest-unit"></a> fastest\_unit | `<float>` The speed in km/h to check for. | `fastest_unit > 12` | Checks if the current scope has a unit with the specified speed. | Must use either > or < operators. | 1.0 |
| <a id="temperature"></a> temperature | `<float>` The temperature in celsius to check for. | `temperature > 20` | Checks if the current scope is in a province with a temperature above the specified amount. | Must use either > or < operators. | 1.0 |
| <a id="reserves"></a> reserves | `<float>` The amount to check for. | `reserves > 10` | Checks if the current scope has the specified amount of reserves waiting. | Must use either > or < operators. | 1.0 |
| <a id="has-combat-modifier"></a> has\_combat\_modifier | `<string>` The modifier to check for. | `has_combat_modifier = river_crossing` | Checks if the current scope has the specified combat modifier. |  | 1.0 |
| <a id="is-fighting-in-terrain"></a> is\_fighting\_in\_terrain | `<string>` The terrain to check for. | `is_fighting_in_terrain = desert` | Checks if the current scope is fighting in the specified terrain. |  | 1.0 |
| <a id="is-fighting-in-weather"></a> is\_fighting\_in\_weather | `<string>` The weather to check for.  **OR**  `{ <string> <...> <string> }` The weather to check for in an OR statement. | `is_fighting_in_weather = sandstorm`  `is_fighting_in_weather = { rain_light rain_heavy }` | Checks if the current scope is fighting in the specified weather. |  | 1.0 |
| <a id="phase"></a> phase | `<bool>` Boolean. | `phase = yes` | Checks if the current scope is in phase. |  | 1.0 |
| <a id="recon-advantage"></a> recon\_advantage | `<bool>` Boolean. | `recon_advantage > 0` | Checks if the current scope has x recon advantage. |  | 1.0 |
| <a id="night"></a> night | `<bool>` Boolean. | `night = yes` | Checks if the current scope is fighting at night. |  | 1.0 |
| <a id="frontage-full"></a> frontage\_full | `<bool>` Boolean. | `frontage_full = yes` | Checks if the current scope has a full combat width. |  | 1.0 |
| <a id="has-flanked-opponent"></a> has\_flanked\_opponent | `<bool>` Boolean. | `has_flanked_opponent = yes` | Checks if the current scope has flanked their opponent. |  | 1.0 |
| <a id="has-max-planning"></a> has\_max\_planning | `<bool>` Boolean. | `has_max_planning = yes` | Checks if the current scope has the maximum planning bonus. |  | 1.0 |
| <a id="has-reserves"></a> has\_reserves | `<bool>` Boolean. | `has_reserves = yes` | Checks if the current scope has any reserves waiting. |  | 1.0 |
| <a id="is-amphibious-invasion"></a> is\_amphibious\_invasion | `<bool>` Boolean. | `is_amphibious_invasion = yes` | Checks if the current scope is performing an amphibious invasion. |  | 1.0 |
| <a id="is-attacker"></a> is\_attacker | `<bool>` Boolean. | `is_attacker = yes` | Checks if the current scope is attacking. |  | 1.0 |
| <a id="is-defender"></a> is\_defender | `<bool>` Boolean. | `is_defender = yes` | Checks if the current scope is defending. |  | 1.0 |
| <a id="is-winning"></a> is\_winning | `<bool>` Boolean. | `is_winning = yes` | Checks if the current scope is winning their battle. |  | 1.0 |
| <a id="is-fighting-air-units"></a> is\_fighting\_air\_units | `<bool>` Boolean. | `is_fighting_air_units = yes` | Checks if the current scope is fighting air units. |  | 1.0 |
| <a id="less-combat-width-than-opponent"></a> less\_combat\_width\_than\_opponent | `<bool>` Boolean. | `less_combat_width_than_opponent = yes` | Checks if the current scope is fighting with less combat width than their opponent. |  | 1.0 |
| <a id="has-carrier-airwings-on-mission"></a> has\_carrier\_airwings\_on\_mission | `<bool>` Boolean. | `has_carrier_airwings_on_mission = yes` | Checks if the current scope has carrier airwings on a mission. |  | 1.0 |
| <a id="has-carrier-airwings-in-own-combat"></a> has\_carrier\_airwings\_in\_own\_combat | `<bool>` Boolean. | `has_carrier_airwings_in_own_combat = yes` | Checks if the current scope has carrier airwings in their own combat. |  | 1.0 |
| <a id="has-artillery-ratio"></a> has\_artillery\_ratio | `<float>` | `has_artillery_ratio > 0.1` | Check that ratio of atrillery battalions in the composition of a side of combating troops are over a certain level. |  | ??? |
| <a id="has-unit-type"></a> has\_unit\_type | `<unit_type>` | `has_unit_type = amphibious_mechanized` | Check if the combatant has at least one of the provided unit types. |  | ??? |

## <a id="division-scope"></a>Division scope

Can be used in **Division** scope.

Division-scoped triggers:
| Name | Parameters | Examples | Description | Notes | Version Added |
| --- | --- | --- | --- | --- | --- |
| <a id="division-has-majority-template"></a> division\_has\_majority\_template | `<battalion>` Battalion to check for. | `division_has_majority_template = light_armor` | Checks if the current scope is majority made up of the specified battalion. | Battalions are defined within /Hearts of Iron IV/common/units/\*.txt files. | 1.12 |
| <a id="division-has-battalion-in-template"></a> division\_has\_battalion\_in\_template | `<battalion>` Battalion to check for. | `division_has_battalion_in_template = light_armor` | Checks if the current scope has any battalions of the type in the template. | Battalions are defined within /Hearts of Iron IV/common/units/\*.txt files. | 1.12 |
| <a id="unit-strength"></a> unit\_strength | `<float>` The amount to check for. | `unit_strength < 0.3` | Checks the current strength of the unit on the scale from 0 to 1. | Must use either the < or > operator. | 1.12 |
| <a id="unit-organization"></a> unit\_organization | `<float>` The amount to check for. | `unit_organization < 0.3` | Checks the current organisation of the unit on the scale from 0 to 1. | Must use either the < or > operator. | 1.12 |
| <a id="is-unit-template-reserves"></a> is\_unit\_template\_reserves | `<bool>` Boolean. | `is_unit_template_reserves = yes` | Checks if the current division has the supply priority set to 'Reserves', i.e. the lowest priority. | Must use either the < or > operator. | 1.12 |
| <a id="has-officer-name"></a> has\_officer\_name | `<string>` The localization key to check. | `has_officer_name = FIN_nikke_parmi` | Checks if the current division has an officer with the provided name key. |  |  |

## <a id="mio-scope"></a>MIO scope

Can be used in **Military-industrial organisation** scope.

MIO-scoped triggers:
| Name | Parameters | Examples | Description | Notes | Version Added |
| --- | --- | --- | --- | --- | --- |
| <a id="is-military-industrial-organization"></a> is\_military\_industrial\_organization | `<token>` MIO to check. | `is_military_industrial_organization = my_mio_token` | Checks if the currently-scoped MIO matches the input token. |  | 1.13 |
| <a id="is-mio-visible"></a> is\_mio\_visible | `<bool>` Boolean. | `is_mio_visible = yes` | Checks if the currently-scoped MIO is visible. |  | 1.13 |
| <a id="is-mio-available"></a> is\_mio\_available | `<bool>` Boolean. | `is_mio_available = yes` | Checks if the currently-scoped MIO is visible. |  | 1.13 |
| <a id="is-mio-assigned-to-task"></a> is\_mio\_assigned\_to\_task | `<bool>` Boolean. | `is_mio_assigned_to_task = yes` | Checks if the currently-scoped MIO is assigned to a task. |  | 1.13 |
| <a id="has-mio-size"></a> has\_mio\_size | `<int>` Integer. | `has_mio_size > 3` | Checks the size of the MIO. | Accepts variables. May use < or >. | 1.13 |
| <a id="has-mio-trait"></a> has\_mio\_trait | `<token>` Trait to check.  **OR**  `trait = <token>` Trait to check. | `has_mio_trait = my_trait_token`  `has_mio_trait = { token = my_trait_token }` | Checks whether the MIO has the target trait in its list. |  | 1.13 |
| <a id="is-mio-trait-available"></a> is\_mio\_trait\_available | `<token>` Trait to check.  **OR**  `trait = <token>` Trait to check.  `check_mio_parent_completed = <bool>` Whether to check if the parent traits are complete. True by default. `check_mio_mutually_exclusive = <bool>` Whether to check if any mutually exclusive traits are complete. True by default. | `is_mio_trait_available = my_trait_token`  `is_mio_trait_available = { token = my_trait_token check_mio_parent_completed = no }` | Checks whether the MIO has the target trait in its list and whether it's available. |  | 1.13 |
| <a id="is-mio-trait-completed"></a> is\_mio\_trait\_completed | `<token>` Trait to check.  **OR**  `trait = <token>` Trait to check. | `is_mio_trait_completed = my_trait_token`  `is_mio_trait_completed = { token = my_trait_token }` | Checks whether the MIO has the target trait in its list and whether it's completed. |  | 1.13 |
| <a id="has-mio-number-of-completed-traits"></a> has\_mio\_number\_of\_completed\_traits | `<int>` Integer. | `has_mio_number_of_completed_traits < 2` | Checks the amount of unlocked MIO traits. | Accepts variables. May use < or >. | 1.13 |
| <a id="has-mio-flag"></a> has\_mio\_flag | `<string>` The flag to check. | `has_mio_flag = my_flag` | Checks if the current scope has the specified flag. |  | 1.13 |
| <a id="has-mio-flag"></a> has\_mio\_flag | `flag = <string>` The flag to check.  `value = <int>` The flag value to check for. Optional.  `date = <date>` The flag creation date to check for. Optional.  `days = <int>` The duration the flag existed for. Optional. | `has_mio_flag = { flag = my_flag days > 30 date > 1936.6.1 value > 0 }` | Compares the specified flag's last set date, days since last set, and/or value. | If not set, the value comparison is `>0`. `value` is limited between -32768 and 32767. | 1.13 |
| <a id="has-mio-policy"></a> has\_mio\_policy | `<token>` Policy to check. | `has_mio_policy = my_policy_token` | Checks if the currently-scoped MIO has the target policy allowed. |  | 1.13 |
| <a id="has-mio-policy-active"></a> has\_mio\_policy\_active | `<token>` Policy to check. | `has_mio_policy_active = my_policy_token` | Checks if the currently-scoped MIO has the target policy active. |  | 1.13 |
| <a id="has-mio-research-category"></a> has\_mio\_research\_category | `<token>` Category to check. | `has_mio_research_category = my_research_category_token` | Checks if the currently-scoped MIO has the target research category. |  | 1.13 |
| <a id="has-mio-equipment-type"></a> has\_mio\_equipment\_type | `<token>` Type to check. | `has_mio_equipment_type = my_equipment_type_token` | Checks if the currently-scoped MIO has the target equipment types. | The possible equipment types are defined in `script_enum_equipment_bonus_type` (in /Hearts of Iron IV/common/script\_enums.txt) and in /Hearts of Iron IV/common/equipment\_groups.txt files. | 1.13 |

## <a id="contract-scope"></a>Contract scope

Can be used in **purchase contract** scope.

Contract-scoped triggers:
| Name | Parameters | Examples | Description | Notes | Version Added |
| --- | --- | --- | --- | --- | --- |
| <a id="contract-contains-equipment"></a> contract\_contains\_equipment | `<token>` Type to check. | `contract_contains_equipment = infantry_equipment` | Checks if the currently-scoped purchase contract contains an equipment type. | May use equipment types, equipment archetypes, or types of equipment archetypes. | 1.13 |
| <a id="deal-completion"></a> deal\_completion | `<decimal>` Progress to compare with. | `deal_completition > 0.6` | Checks the deal completion with the target value. | May use < or >. On the scale from 0 to 1. | 1.13 |
| <a id="seller"></a> seller | `<country>` Country to check. | `seller = BHR` | Checks the seller in the current purchase contract. |  | 1.13 |
| <a id="buyer"></a> buyer | `<country>` Country to check. | `buyer = OMA` | Checks the buyer in the current purchase contract. |  | 1.13 |

## <a id="special-projects"></a>Special projects

Special project-scoped triggers:
| Name | Parameters | Examples | Description | Notes | Version Added |
| --- | --- | --- | --- | --- | --- |
| <a id="has-project-flag"></a> has\_project\_flag | `<string>` The flag to check for. **OR**  `flag = <string>` The flag to check.  `value = <int>` The flag value to check for. Optional.  `date = <date>` The flag creation date to check for. Optional.  `days = <int>` The duration the flag existed for. Optional. | `has_project_flag = my_flag`  `has_project_flag = { flag = my_flag value < 12 date > 1936.3.25 days > 365 }` | Check if flag has been set within the special project in scope. May checks on the value or date/days since last modified date. | If not set, the value comparison is >0. value is limited between -32768 and 32767. | 1.15 |

## <a id="meta-triggers"></a>Meta triggers

Meta triggers are a system added with 1.6 with ![Man the Guns](media/triggers-hearts-of-iron-4-wiki_58368ba2e5__img31.png) Man the Guns<a id="cite-ref-3"></a>[[3]](#cite-note-3) used in the exact same manner as [meta effects](<Effects - Hearts of Iron 4 Wiki.md#meta-effects>): in order to tie a trigger block to a dynamic localisation entry. This is usually used in conjunction with [scripted localisation](<Localisation - Hearts of Iron 4 Wiki.md#scripted-localisation>) for non-numerical checks. This also can serve in order to place a variable check where one is not possible.  
Meta triggers work in any scope that supports triggers, including combat scope.

The following arguments go inside of a scripted trigger:

- `text = { ... }` is a trigger block used by the meta trigger. In here, any string that must be made dynamic is marked with the square brackets on each side as `[EXAMPLE]`.
- `EXAMPLE = "..."` is a string that will serve as the dynamic replacement for `[EXAMPLE]` within `text = { ... }`. This accepts [dynamic localisation](<Localisation - Hearts of Iron 4 Wiki.md#namespaces>) to a limited degree, such as getting a variable's value with `[?var_name]` or some namespaces like `[ROOT.GetTag]`.
- `debug = yes`, if added, will add the final output in the [user directory](<Modding - Hearts of Iron 4 Wiki.md>)'s /Hearts of Iron IV/logs/game.log file for debugging purposes.

For example, the following can be used with [has\_equipment](#has-equipment) to make it depend on a variable's value:

```text
meta_trigger = {
    text = {
        has_equipment = { [EQUIPMENT_ARCHETYPE] > 100 }
    }
    EQUIPMENT_ARCHETYPE = "[GetEquipmentArchetype]"
}
```

In this case, `GetEquipmentArchetype` is [scripted localisation](<Localisation - Hearts of Iron 4 Wiki.md#scripted-localisation>). An example definition of scripted localisation in this case is as such:

```text
defined_text = {
    name = GetEquipmentArchetype
    text = {
        trigger = {
            check_variable = { v = 0 }
        }
        localization_key = artillery_equipment
    }
    text = {
        localization_key = infantry_equipment
    }
}
```

## <a id="scripted-triggers"></a>Scripted triggers

Scripted triggers serve a similar purpose to [functions](https://en.wikipedia.org/wiki/Subroutine) in that they can be defined in /Hearts of Iron IV/common/scripted\_triggers/\*.txt and then used elsewhere as a shortened version. Alongside that, the game has certain base game scripted triggers that are checked directly in the game's code determining triggers for functions that cannot be changed.

A scripted trigger is defined simply as

```text
scripted_trigger_name = {
	<triggers>
}
```

This example can be used as a trigger in regular code as `scripted_trigger_name = yes` or `scripted_trigger_name = no`.

For example, this would be the definition in any scripted trigger file:

```text
state_is_in_area = {
    OR = {
        state = 120
        state = 121
        state = 123
        state = 124
        state = 125
    }
}
`This can then be used in any other trigger block, such as a national focus' available section:`
focus = {
    id = TAG_focus_id   # Optional attributes, other than available, have been omitted
    available = {
        capital_scope = {
            state_is_in_area = yes
        }
    }
}
```

If there are several definitions of scripted triggers with the exact same name, the game will make the scripted trigger be the one that was [evaluated later, as decided by file names and order in files](<Modding - Hearts of Iron 4 Wiki.md#loading-files>).

### <a id="diplomacy-scripted-triggers"></a>Diplomacy scripted triggers

Diplomacy scripted triggers fall into two mutually exclusive groups: deciding availability and deciding visibility. By default, these are defined in /Hearts of Iron IV/common/scripted\_triggers/diplomacy\_scripted\_triggers.txt and /Hearts of Iron IV/common/scripted\_triggers/00\_diplo\_action\_valid\_triggers.txt respectively. While it is possible to also use them as regular scripted triggers, they will also modify the prerequisites of being able to do a diplomatic action between 2 countries.

A diplomacy scripted trigger is identified by the naming pattern of `DIPLOMACY_<action>_ENABLE_TRIGGER` for availability, such as `DIPLOMACY_GUARANTEE_ENABLE_TRIGGER`, and `is_diplomatic_action_valid_<action>` for visibility, such as `is_diplomatic_action_valid_stage_coup`. In the base game, diplomacy scripted triggers are used to implement the game rules and add some country-specific exceptions, such as the ![Flag of United Kingdom](media/triggers-hearts-of-iron-4-wiki_58368ba2e5__img33.png) United Kingdom being unable to release its colonies with the ![Man the Guns](media/triggers-hearts-of-iron-4-wiki_58368ba2e5__img34.png) Man the Guns DLC. Checking the base game's contents beforehand or copying it to the mod would ensure that the mod won't accidentally break any existing game rules.

Generally, the pattern in localisation keys used for the button usually matches up with the internal ID of a diplomatic action. If the diplomatic action doesn't already have a scripted trigger in the base game, [entirety of localisation can be searched](<Modding - Hearts of Iron 4 Wiki.md#searching-multiple-files>) for the name of the button to find the name of the action. For example, a the English localisation entry of  `DIPLOMACY_CALL_ALLY_TITLE:0 "Call to arms"` would suggest that the diplomatic action of calling ally to war is `CALL_ALLY`.

List of known triggers:

```text
DIPLOMACY_JOIN_ALLY_ENABLE_TRIGGER
DIPLOMACY_CALL_ALLY_ENABLE_TRIGGER
DIPLOMACY_WAR_ENABLE_TRIGGER
DIPLOMACY_JOIN_FACTION_ENABLE_TRIGGER
DIPLOMACY_CREATE_FACTION_ENABLE_TRIGGER	
DIPLOMACY_PEACE_PROPOSAL_ENABLE_TRIGGER
DIPLOMACY_IMPROVERELATION_ENABLE_TRIGGER
DIPLOMACY_NONAGGRESSIONPACT_ENABLE_TRIGGER
DIPLOMACY_REVOKE_NONAGGRESSIONPACT_ENABLE_TRIGGER
DIPLOMACY_OFFER_JOIN_FACTION_ENABLE_TRIGGER
DIPLOMACY_REQUEST_FOREIGN_MANPOWER_ENABLE_TRIGGER
DIPLOMACY_CANCEL_FOREIGN_MANPOWER_ENABLE_TRIGGER
DIPLOMACY_CANCEL_LICENSED_PRODUCTION_ENABLE_TRIGGER
DIPLOMACY_REQUEST_ACCESS_TO_LICENCE_PRODUCTION_ENABLE_TRIGGER
DIPLOMACY_SEND_ATTACHE_ENABLE_TRIGGER
DIPLOMACY_EMBARGO_ENABLE_TRIGGER
DIPLOMACY_SEND_EXP_FORCE_ENABLE_TRIGGER
DIPLOMACY_REQUEST_EXP_FORCE_ENABLE_TRIGGER
DIPLOMACY_RETURN_EXP_FORCE_ENABLE_TRIGGER
DIPLOMACY_ASKSTATECONTROL_ENABLE_TRIGGER
DIPLOMACY_GIVESTATECONTROL_ENABLE_TRIGGER
DIPLOMACY_GUARANTEE_ENABLE_TRIGGER
DIPLOMACY_REVOKE_GUARANTEE_ENABLE_TRIGGER
DIPLOMACY_RELEASE_NATION_ENABLE_TRIGGER
DIPLOMACY_MILACC_ENABLE_TRIGGER
DIPLOMACY_OFFER_MILACC_ENABLE_TRIGGER
DIPLOMACY_REVOKE_OFFER_MILACC_ENABLE_TRIGGER
DIPLOMACY_DOCKING_RIGHTS_ENABLE_TRIGGER
DIPLOMACY_OFFER_DOCKING_RIGHTS_ENABLE_TRIGGER
DIPLOMACY_AIR_BASE_ACCESS_ENABLE_TRIGGER
DIPLOMACY_OFFER_AIR_BASE_ACCESS_ENABLE_TRIGGER
DIPLOMACY_REVOKE_OFFER_DOCKING_RIGHTS_ENABLE_TRIGGER
DIPLOMACY_REVOKE_OFFER_AIR_BASE_ACCESS_ENABLE_TRIGGER
DIPLOMACY_LEND_LEASE_ENABLE_TRIGGER
DIPLOMACY_INCOMING_LEND_LEASE_ENABLE_TRIGGER
DIPLOMACY_REQUEST_LICENSED_PRODUCTION_ENABLE_TRIGGER
DIPLOMACY_GENERATE_WARGOAL_ENABLE_TRIGGER
DIPLOMACY_BOOST_PARTY_POPULARITY_ENABLE_TRIGGER
DIPLOMACY_STAGE_COUP_ENABLE_TRIGGER
DIPLOMACY_LEAVE_FACTION_ENABLE_TRIGGER
DIPLOMACY_ASSUME_FACTION_LEADERSHIP_ENABLE_TRIGGER
DIPLOMACY_KICK_FROM_FACTION_ENABLE_TRIGGER
DIPLOMACY_SEND_VOLUNTEERS_ENABLE_TRIGGER
```

Know tokens for `is_diplomatic_action_valid_<action>` are:

- **declare\_war**, for the Declare War button
- **generate\_wargoal**, only affects the war goal menu by greying out the send button
- **guarantee**, for the Guarantee Independence button
- **docking\_rights**, for the request docking rights button
- **offer\_docking\_right**, for the offer docking rights button
- **create\_faction**, for the create faction button
- **assume\_faction\_leadership**, for the assume leadership of faction button
- **kick\_from\_faction**, for the kick from faction button
- **join\_faction**, for the ask to join faction button
- **request\_access\_to\_licence\_production**, for the negotiate license button
- **embargo**, for the embargo button
- **send\_volunteers**, only affects the sent volunteers menu by greying out the send button
- **stage\_coup**, for the stage coup button
- **boost\_party\_popularity**, for the boost party popularity button

Within a diplomacy scripted trigger, the default scope is the country that does the trigger, while [FROM](<Scopes - Hearts of Iron 4 Wiki.md#from>) is the target of the action. For availability, the trigger's tooltip is shown to the player when hovering over the diplomatic action; in case of country-specific restrictions, using [conditional statements](#if) can ensure that the tooltip would only be generated when needed rather than between any pair of nations.

For example, this trigger will prevent BHR from revoking a guarantee on QAT, while still ensuring the game rule works otherwise:

```text
DIPLOMACY_REVOKE_GUARANTEE_ENABLE_TRIGGER = {
    if = {
        limit = {
            has_game_rule = {
                rule = allow_revoke_guarantees
                option = BLOCKED
            }
        }
        custom_trigger_tooltip = {
            tooltip = RULE_ALLOW_REVOKE_GUARANTEES_BLOCKED_TOOLTIP
            always = no
        }
    }
    if = {
        limit = {
            tag = BHR
            FROM = { tag = QAT }
        }
        custom_trigger_tooltip = {
            tooltip = NO_REVOKING_ON_QAT_TT
            always = no
        }
    }
}
```

### <a id="resistance-initiation-triggers"></a>Resistance initiation triggers

The behaviour of resistance being automatically initiated is decided by the `should_initiate_resistance` scripted trigger, by default defined in /Hearts of Iron IV/common/scripted\_triggers/00\_resistance\_initiate\_triggers.txt. If it is unfulfilled, the resistance will never initiate unless forced via the [the force\_enable\_resistance effect](<Effects - Hearts of Iron 4 Wiki.md#force-enable-resistance>). Likewise, the resistance will always occur if it's true unless forcefully disabled.

The scripted trigger's behaviour can be overwritten with state-specific scripted triggers, which should be named `should_initiate_resistance` with the list of state IDs suffixed at the end, separated by underscores. For example, this ensures that when a state 321 or 123 is controlled by the ![Flag of United Kingdom](media/triggers-hearts-of-iron-4-wiki_58368ba2e5__img35.png) United Kingdom, resistance would get initiated if and only if they're national territory of ![Flag of France](media/cosmetic-tag-modding-hearts-of-iron-4-wiki_8daa0f4184__img3.png) France; otherwise, the normal behaviour is used:

```text
should_initiate_resistance_123_321 = {
	if = {
		limit = {
			tag = ENG
		}
		is_core_of = FRA
	}
	else = {
		should_initiate_resistance = yes # If this is not done, resistance would always activate due to overwriting that scripted trigger.
	}
}
```

### <a id="useful-scripted-triggers"></a>Useful scripted triggers

These scripted triggers are defined in base game and might be useful to keep in the mod to cut down on the amount of code. As scripted triggers, all of these use a boolean value as argument.

Scripted triggers:
| Name | Scope | Example | Description | Notes |
| --- | --- | --- | --- | --- |
| <a id="can-root-get-wargoal-on-this"></a> can\_ROOT\_get\_wargoal\_on\_THIS | Country | `can_ROOT_get_wargoal_on_THIS = yes` | Checks if ROOT can obtain a wargoal on the current scope. | To evaluate as true, the current scope must exist, not share a faction with ROOT, and not be a subject of ROOT. |
| <a id="is-free-or-subject-of-root"></a> is\_free\_or\_subject\_of\_root | Country | `is_free_or_subject_of_root = yes` | Checks if the current scope is either independent or a subject of ROOT. |  |
| <a id="has-same-ideology"></a> has\_same\_ideology | Country | `has_same_ideology = yes` | Checks if the current scope has the same ideology as ROOT. | Needs modifying if there are custom ideologies. Equivalent to `has_government = ROOT` for base game ideologies. |
| <a id="is-enemy-ideology"></a> is\_enemy\_ideology | Country | `is_enemy_ideology = yes` | Checks if the current scope has an ideology that is considered enemy to ROOT's. | ![{{{1}}}](media/triggers-hearts-of-iron-4-wiki_58368ba2e5__img37.png) Communism, ![{{{1}}}](media/triggers-hearts-of-iron-4-wiki_58368ba2e5__img38.png) Democracy, and ![{{{1}}}](media/triggers-hearts-of-iron-4-wiki_58368ba2e5__img39.png) Fascism are considered enemy to each other. |
| <a id="has-root-at-least-1-div-in-current-state-scope"></a> has\_ROOT\_at\_least\_1\_div\_in\_current\_state\_scope | State | `has_ROOT_at_least_1_div_in_current_state_scope = yes` | Checks if ROOT has at least one division in the current scope. |  |
| <a id="controls-or-subject-of"></a> controls\_or\_subject\_of | State | `controls_or_subject_of = yes` | Checks if the current state is controlled by ROOT or a subject of ROOT. |  |
| <a id="is-controlled-by-root-or-ally"></a> is\_controlled\_by\_ROOT\_or\_ally | State | `is_controlled_by_ROOT_or_ally = yes` | Checks if the current state is controlled by ROOT, a subject of ROOT, or a country in the same faction as ROOT. |  |
| <a id="owns-or-subject-of"></a> owns\_or\_subject\_of | State | `owns_or_subject_of = yes` | Checks if the current scope is owned by ROOT or a subject of ROOT. |  |

## <a id="references-and-notes"></a>References and notes

<a id="cnote-a"></a>**[^](#ref-a)** **a:** Triggers are able to set and modify temporary variables. This temporary variable itself may be then used separately to change the game's state, such as in a MTTH block or if the trigger block is used in some [effect](<Effects - Hearts of Iron 4 Wiki.md>)'s `limit = { ... }` (most commonly [if statements](<Effects - Hearts of Iron 4 Wiki.md#if>) or [effect scope limits](<Scopes - Hearts of Iron 4 Wiki.md#scope-limits>)), though the usage of the variable to change the game's state is not a trigger by itself.

<a id="cite-note-1"></a>1. [↑](#cite-ref-1) [[Modding] Achievement for mods](https://forum.paradoxplaza.com/forum/index.php?threads/1544899)  
   [Tutorial to write achievements files in your mod](https://forum.paradoxplaza.com/forum/index.php?threads/1544901)
<a id="cite-note-2"></a>2. [↑](#cite-ref-2) [forum:1356228/#post-26361808](https://forum.paradoxplaza.com/forum/index.php?threads/1356228/#post-26361808)
<a id="cite-note-3"></a>3. [↑](#cite-ref-3) [HOI4 Dev Diary - Modding and Traits](https://forum.paradoxplaza.com/forum/index.php?threads/1117516)

**[Modding](<Modding - Hearts of Iron 4 Wiki.md>)**
