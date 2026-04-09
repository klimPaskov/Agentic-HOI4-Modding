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
  - [General](#general)
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
  - [General](#general)
  - [Resistance and Compliance](#resistance-and-compliance)
- [Character scope](#character-scope)
  - [General](#general)
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

**Conditions** (also known as **Triggers**) are used to check whether certain conditions are fulfilled in the game's current state or not, without being able to change anything in the game's state. These return a [boolean](http://en.wikipedia.org/wiki/Boolean_data_type) (true or false), which may be interpreted by the block where it's used. Usually blocks that allow using triggers are an [AND](#and) unless stated otherwise, which would instantly stop execution upon receiving a single false statement and return false.

The list of triggers may be outdated. A complete, but unsorted, list of triggers can be found in /Hearts of Iron IV/documentation/triggers\_documentation.html or /Hearts of Iron IV/documentation/triggers\_documentation.md. As of 1.17.1.1, this file was last updated in the version 1.17.0.

## Operators

Every trigger uses one of the three operators: The equality sign `=` or the comparison signs `>` and `<`.

The equality sign can either mean strict equality (Unlike previous games in the series where it checked for being equal or greater than) or can serve as a way to introduce a block of additional triggers, as in `has_opinion = { target = GRE value < -10 }`. The comparison signs serves as strict comparison: `has_political_power > 100` will not be true if the country has exactly 100 political power, for instance.

Not all triggers support the equality sign or comparison signs. See the details for each trigger in the notes for it. If not stated otherwise, the trigger only supports the equality sign.

## Context scopes

There are three general scopes all triggers operate in:

- country
- state
- character

They give context to a trigger by stating what the trigger is checking against.

Each country acts as a sub-scope of the general country scope, i.e. `GER = { }` will check only against Germany, whereas `any_country` will check against all countries. Likewise for states and characters.

Triggers won't work in scopes they are not assigned to. Country triggers will not work for states or vice-versa.

## Scopes

*Main article: [Scopes](<Scopes - Hearts of Iron 4 Wiki.md>)*

These don't serve as triggers, but rather as scopes that change for whom the triggers are being checked. Each one also serves as an [AND statement](#and).

### Trigger scopes

These can only be used as triggers; trying to use them as effects will result in nothing happening.

- **all_country**
  - Usage: Always usable
  - Target type: Country
  - Example: all_country = { … }
  - Description: Checks if all countries meet the triggers.
  - Version Added: 1.0

- **any_country**
  - Usage: Always usable
  - Target type: Country
  - Example: any_country = { … }
  - Description: Checks if any country meets the triggers.
  - Version Added: 1.0

- **all_other_country**
  - Usage: Within country scope only
  - Target type: Country
  - Example: all_other_country = { … }
  - Description: Checks if all countries other than the one where this scope is located meet the triggers.
  - Version Added: 1.0

- **any_other_country**
  - Usage: Within country scope only
  - Target type: Country
  - Example: any_other_country = { … }
  - Description: Checks if any country other than the one where this scope is located meets the triggers.
  - Version Added: 1.0

- **all_country_with_original_tag**
  - Usage: Always usable
  - Target type: Country
  - Example:
    ```text
    all_country_with_original_tag = {
        original_tag_to_check = TAG  #required
        …                  #triggers to check
    }
    ```
  - Description:
    ```text
    Checks if all countries originating from the specified country, including the dynamic countries created for civil wars and other purposes, meet the triggers.
    original_tag_to_check = TAG
    is used to specify the original tag.
    ```
  - Version Added: 1.9

- **any_country_with_original_tag**
  - Usage: Always usable
  - Target type: Country
  - Example:
    ```text
    any_country_with_original_tag = {
        original_tag_to_check = TAG  #required
        …                  #triggers to check
    }
    ```
  - Description:
    ```text
    Checks if any country originating from the specified country, including the dynamic countries created for civil wars and other purposes, meets the triggers.
    original_tag_to_check = TAG
    is used to specify the original tag.
    ```
  - Version Added: 1.9

- **all_neighbor_country**
  - Usage: Within country scope only
  - Target type: Country
  - Example: all_neighbor_country = { … }
  - Description: Checks if all countries that border the one where this scope is located meet the triggers.
  - Version Added: 1.0

- **any_neighbor_country**
  - Usage: Within country scope only
  - Target type: Country
  - Example: any_neighbor_country = { … }
  - Description: Checks if any country that borders the one where this scope is located meets the triggers.
  - Version Added: 1.0

- **any_home_area_neighbor_country**
  - Usage: Within country scope only
  - Target type: Country
  - Example: any_home_area_neighbor_country = { … }
  - Description: Checks if any country that borders the one where this scope is located, as well as being in its home area - meaning a direct land connection between the capitals of countries - meets the triggers.
  - Version Added: 1.0

- **all_guaranteed_country**
  - Usage: Within country scope only
  - Target type: Country
  - Example: all_guaranteed_country = { … }
  - Description: Checks if all countries that are guaranteed by the one where this scope is located meet the triggers.
  - Version Added: 1.9

- **any_guaranteed_country**
  - Usage: Within country scope only
  - Target type: Country
  - Example: any_guaranteed_country = { … }
  - Description: Checks if any country that is guaranteed by the one where this scope is located meets the triggers.
  - Version Added: 1.9

- **all_allied_country**
  - Usage: Within country scope only
  - Target type: Country
  - Example: all_allied_country = { … }
  - Description: Checks if all countries that are allied with the one where this scope is located - meaning that they are either a subject of the country, its overlord, or that they share a faction - meet the triggers. Does not include the country itself.
  - Version Added: 1.9

- **any_allied_country**
  - Usage: Within country scope only
  - Target type: Country
  - Example: any_allied_country = { … }
  - Description: Checks if any country that is allied with the one where this scope is located - meaning that they are either a subject of the country, its overlord, or that they share a faction - meets the triggers. Does not include the country itself.
  - Version Added: 1.9

- **all_occupied_country**
  - Usage: Within country scope only
  - Target type: Country
  - Example: all_occupied_country = { … }
  - Description: Checks if all countries that are occupied by the one where this scope is located - meaning that the occupied country has core states controlled by the occupier country - meet the triggers.
  - Version Added: 1.9

- **any_occupied_country**
  - Usage: Within country scope only
  - Target type: Country
  - Example: any_occupied_country = { … }
  - Description: Checks if any country that is occupied by the one where this scope is located - meaning that the occupied country has core states controlled by the occupier country - meets the triggers.
  - Version Added: 1.9

- **all_enemy_country**
  - Usage: Within country scope only
  - Target type: Country
  - Example: all_enemy_country = { … }
  - Description: Checks if all countries that are at war with the one where this scope is located meet the triggers.
  - Version Added: 1.9

- **any_enemy_country**
  - Usage: Within country scope only
  - Target type: Country
  - Example: any_enemy_country = { … }
  - Description: Checks if any country that are at war with the one where this scope is located meets the triggers.
  - Version Added: 1.9

- **all_subject_countries**
  - Usage: Within country scope only
  - Target type: Country
  - Example: all_subject_countries = { … }
  - Description: Checks if all countries that are a subject of the one where this scope is located meet the triggers. Notice the plural spelling in the scope.
  - Version Added: 1.11

- **any_subject_country**
  - Usage: Within country scope only
  - Target type: Country
  - Example: any_subject_country = { … }
  - Description: Checks if any country that is a subject of the one where this scope is located meets the triggers.
  - Version Added: 1.11

- **any_country_with_core**
  - Usage: Within state scope only
  - Target type: Country
  - Example: any_country_with_core = { … }
  - Description:
    ```text
    Checks if any country that has the current scope as a core state meets the triggers.
    Does not have an equivalent for other effect/trigger scope types.
    ```
  - Version Added: 1.12

- **all_state**
  - Usage: Always usable
  - Target type: State
  - Example: all_state = { … }
  - Description: Check if all states meet the triggers.
  - Version Added: 1.0

- **any_state**
  - Usage: Always usable
  - Target type: State
  - Example: any_state = { … }
  - Description: Check if any state meets the triggers.
  - Version Added: 1.0

- **any_state_in**
  - Usage: Always usable
  - Target type: State
  - Example: Requires on of the following fields
  - Example:
    ```text
    any_state_in = {
      array = array_of_states  #required 
        …                  #triggers to check
    }
    ```
  - Example:
    ```text
    array = <array_of_states>
    continent = <continent_name>
    ai_area = <ai_area_name>
    strategic_region = <strategic_region_number>
    ```
  - Description: Check if any state in the given category meets the trigger.
  - Version Added: 1.15

- **all_neighbor_state**
  - Usage: Within state scope only
  - Target type: State
  - Example: all_neighbor_state = { … }
  - Description: Check if all states that are neighbour to the one where this scope is located meet the triggers.
  - Version Added: 1.0

- **any_neighbor_state**
  - Usage: Within state scope only
  - Target type: State
  - Example: any_neighbor_state = { … }
  - Description: Check if any state that is neighbour to the one where this scope is located meets the triggers.
  - Version Added: 1.0

- **all_owned_state**
  - Usage: Within country scope only
  - Target type: State
  - Example: all_owned_state = { … }
  - Description: Check if all states that are owned by the country where this scope is located meet the triggers.
  - Version Added: 1.0

- **any_owned_state**
  - Usage: Within country scope only
  - Target type: State
  - Example: any_owned_state = { … }
  - Description: Check if any state that is owned by the country where this scope is located meets the triggers.
  - Version Added: 1.0

- **all_core_state**
  - Usage: Within country scope only
  - Target type: State
  - Example: all_core_state = { … }
  - Description: Check if any state that is cored by the country where this scope is located meets the triggers.
  - Version Added: 1.11

- **any_core_state**
  - Usage: Within country scope only
  - Target type: State
  - Example: any_core_state = { … }
  - Description: Check if all states that are cored by the country where this scope is located meet the triggers.
  - Version Added: 1.11

- **all_controlled_state**
  - Usage: Within country scope only
  - Target type: State
  - Example: all_controlled_state = { … }
  - Description: Check if all states that are controlled by the country where this scope is located meet the triggers.
  - Version Added: 1.9

- **any_controlled_state**
  - Usage: Within country scope only
  - Target type: State
  - Example: any_controlled_state = { … }
  - Description: Check if any state that is controlled by the country where this scope is located meets the triggers.
  - Version Added: 1.9

- **all_unit_leader**
  - Usage: Within country scope only
  - Target type: Unit Leader
  - Example: all_unit_leader = { … }
  - Description: Checks if all unit leaders (corps commanders, field marshals, admirals) that are employed by the country where this scope is located meet the triggers.
  - Version Added: 1.5

- **any_unit_leader**
  - Usage: Within country scope only
  - Target type: Unit Leader
  - Example: any_unit_leader = { … }
  - Description: Checks if any unit leader (corps commander, field marshal, admiral) that is employed by the country where this scope is located meets the triggers.
  - Version Added: 1.5

- **all_army_leader**
  - Usage: Within country scope only
  - Target type: Unit Leader
  - Example: all_army_leader = { … }
  - Description: Checks if all army leaders that are employed by the country where this scope is located meet the triggers.
  - Version Added: 1.5

- **any_army_leader**
  - Usage: Within country scope only
  - Target type: Unit Leader
  - Example: any_army_leader = { … }
  - Description: Checks if any army leader that is employed by the country where this scope is located meets the triggers.
  - Version Added: 1.5

- **all_navy_leader**
  - Usage: Within country scope only
  - Target type: Unit Leader
  - Example: all_navy_leader = { … }
  - Description: Checks if all navy leaders that are employed by the country where this scope is located meet the triggers.
  - Version Added: 1.5

- **any_navy_leader**
  - Usage: Within country scope only
  - Target type: Unit Leader
  - Example: any_navy_leader = { … }
  - Description: Checks if any navy leader that is employed by the country where this scope is located meets the triggers.
  - Version Added: 1.5

- **all_operative_leader**
  - Usage: Within country scope or operations only
  - Target type: Operative
  - Example: all_operative_leader = { … }
  - Description: Checks if all operatives that are employed by the country where this scope is located meet the triggers.
  - Version Added: 1.9

- **any_operative_leader**
  - Usage: Within country scope or operations only
  - Target type: Operative
  - Example: any_operative_leader = { … }
  - Description: Checks if any operative that is employed by the country where this scope is located meets the triggers.
  - Version Added: 1.9

- **all_character**
  - Usage: Within country scope only
  - Target type: Character
  - Example: all_character = { … }
  - Description: Checks if all characters that are recruited by the country where this scope is located meet the triggers.
  - Version Added: 1.11

- **any_character**
  - Usage: Within country scope only
  - Target type: Character
  - Example: any_character = { … }
  - Description: Checks if any character that is recruited by the country where this scope is located meets the triggers.
  - Version Added: 1.11

- **any_country_division**
  - Usage: Within country scope only
  - Target type: Division
  - Example: any_country_division = { … }
  - Description: Checks if any division owned by the current country meets the triggers.
  - Version Added: 1.12

- **any_state_division**
  - Usage: Within state scope only
  - Target type: Division
  - Example: any_state_division = { … }
  - Description: Checks if any division within the current state meets the triggers.
  - Version Added: 1.12

- **all_military_industrial_organization**
  - Usage: Within country scope only
  - Target type: MIO
  - Example: all_military_industrial_organization = { … }
  - Description: Checks if all MIOs within the current country meet the conditions.
  - Version Added: 1.13

- **any_military_industrial_organization**
  - Usage: Within country scope only
  - Target type: MIO
  - Example: any_military_industrial_organization = { … }
  - Description: Checks if any MIO within the current country meets the conditions.
  - Version Added: 1.13

- **all_purchase_contract**
  - Usage: Within country scope only
  - Target type: Purchase contract
  - Example: all_purchase_contract = { … }
  - Description: Checks if all purchase contracts within the current country meet the conditions.
  - Version Added: 1.13

- **any_purchase_contract**
  - Usage: Within country scope only
  - Target type: Purchase contract
  - Example: any_purchase_contract = { … }
  - Description: Checks if any purchase contract within the current country meets the conditions.
  - Version Added: 1.13

- **all_scientists**
  - Usage: Within country scope only
  - Target type: Character
  - Example: all_scientistst = { … }
  - Description: Checks if all scientists of the Country in scope matches the triggers.
  - Version Added: 1.15

- **any_scientist**
  - Usage: Within country scope only
  - Target type: Character
  - Example: any_scientist = { … }
  - Description: Checks if at least one active scientist of the Country in scope matches the triggers.
  - Version Added: 1.15

- **all_active_scientist**
  - Usage: Within country scope only
  - Target type: Character
  - Example: all_active_scientist = { … }
  - Description: Checks if all active scientists of the Country in scope matches the triggers.
  - Version Added: 1.15

- **any_active_scientist**
  - Usage: Within country scope only
  - Target type: Character
  - Example: any_active_scientist = { … }
  - Description: Checks if at least one active scientist of the Country in scope matches the triggers.
  - Version Added: 1.15

### Dual scopes

The following scopes can be used either as effect or trigger scopes; some can also be used as the right side of some effects and triggers as a target. If usage as a target is possible, it's marked within the table.

Several dual scopes may have a scope that varies depending on where it's used, such as variables, which can be set to anything.

- **TAG**
  - Usage: Always usable
  - Target type: Country scope
  - Example: SOV = { country_event = my_event.1 }
  - Description:
    ```text
    The country defined by the tag or tag alias. Tag aliases are defined in
    /Hearts of Iron IV/common/country_tag_aliases
    , as a way to refer to a specific country (such as a side in a civil war) in addition to its actual tag. If the country with the exact tag doesn't exist, but a dynamic country originating from the specified tag does, the scope will refer to the dynamic country.
    ```
  - Usable as target: ✓
  - Version Added: 1.0

- **<state_id>**
  - Usage: Always usable
  - Target type: State scope
  - Example: 123 = { transfer_state_to = SCO }
  - Description: The state defined by this id.
  - Usable as target: ✓
  - Version Added: 1.0

- **<character>**
  - Usage: not within Character scope
  - Target type: Character scope
  - Example: ENG_theodore_makhno = { set_nationality = UKR }
  - Description: On game versions prior to 1.12.8, the character must be already recruited by the country this is scoped from.
  - Usable as target: ✓
  - Version Added: 1.11

- **mio:<MIO>**
  - Usage: Within country scope only
  - Target type: MIO scope
  - Example: mio:AST_cockatoo_doe_organization = { … }
  - Description:
    ```text
    The MIO identified by that ID as defined within the
    /Hearts of Iron IV/common/military_industrial_organization/organizations/*.txt
    file.
    ```
  - Usable as target: ✓
  - Version Added: 1.13

- **sp:<special_project>**
  - Usage: Within country scope only
  - Target type: Special project scope
  - Example: sp:sp_land_flamethrower_tank = { … }
  - Description:
    ```text
    The special project identified by that ID as defined within the
    /Hearts of Iron IV/common/special_projects/projects/*.txt
    file.
    ```
  - Usable as target: ✓
  - Version Added: 1.15

- **ROOT**
  - Usage: Always usable
  - Target type: Depends on usage
  - Example:
    ```text
    ENG = {
        FRA = {
            GER = {
                declare_war_on = {
                    target = ROOT
                    type = annex_everything
                }
            }
        }
    } #GER declares war on ENG (if there is no scope before ENG)
    ```
  - Description:
    ```text
    Targets the root node of the block, an inherent property of each block. Most commonly, this is the default scope: for example, ROOT
    within a national focus
    will always refer to the country doing the focus and ROOT
    within a event
    will always refer to the country getting the event. However, some blocks do distinguish between the default scope and ROOT, such as
    certain scripted GUI contexts
    or
    certain on actions
    . If a block doesn't have ROOT defined (such as
    on_startup in on actions
    ), then it is impossible to use it.
    ```
  - Usable as target: ✓
  - Version Added: 1.0

- **THIS**
  - Usage: Always usable
  - Target type: Depends on usage
  - Example:
    ```text
    set_temp_variable = { target_country = THIS }
    ```
  - Description:
    ```text
    Targets the current scope where it's used. For example, when used in
    every_state
    , it will refer to the state that's currently being evaluated. Primarily useful for
    variables
    (as in the example, where omitting it wouldn't work) or for
    built-in localisation commands
    , where some scope must be specified. More rarely, this may help with scope manipulation when using
    PREV
    . Since omitting it makes no difference in how the code gets interpreted, there is little to no usage outside of these cases.
    ```
  - Usable as target: ✓
  - Version Added: 1.0

- **PREV**
  - Usage: Always usable
  - Target type: Depends on usage
  - Example:
    ```text
    FRA = {
        random_country = {
            GER = {
                declare_war_on = {
                    target = PREV
                    type = annex_everything
                }
            }
        }
    } #Germany declares war on random_country
    ```
  - Description:
    ```text
    Targets the scope that the current scope is contained in. Can have additional applications where the assumed default scope differs from the ROOT, such as in state events or some on_actions. Can be chained indefinitely as PREV.PREV.
    Commonly results in broken-looking tooltips
    : what's shown to the player doesn't always correlate with reality.
    See also:
    PREV usage
    .
    ```
  - Usable as target: ✓
  - Version Added: 1.0

- **FROM**
  - Usage: Always usable
  - Target type: Depends on usage
  - Example:
    ```text
    declare_war_on = {
        target = FROM
        type = annex_everything
    }
    
    FROM = {
        load_oob = defend_ourselves
    }
    ```
  - Description:
    ```text
    Can be chained indefinitely as FROM.FROM. Used to target various hardcoded scopes inherent to the block, often a secondary scope in addition to ROOT. For example:
    In
    events
    , this refers to the country that sent the event (i.e. if the event was fired
    using an effect
    , then it's the ROOT scope where it was fired).
    In
    targeted decisions
    or
    diplomacy scripted triggers
    , this refers to the scope that is targeted.
    ```
  - Usable as target: ✓
  - Version Added: 1.0

- **overlord**
  - Usage: Within country scope only
  - Target type: Country scope
  - Example: overlord = { … }
  - Description:
    ```text
    The overlord of the country if it is a subject.
    Subject to the 'invalid event target' error.
    ```
  - Usable as target: X
  - Version Added: 1.3

- **faction_leader**
  - Usage: Within country scope only
  - Target type: Country scope
  - Example: faction_leader = { add_to_faction = FROM }
  - Description:
    ```text
    Faction leader of the faction the country is a part of.
    Subject to the 'invalid event target' error.
    ```
  - Usable as target: X
  - Version Added: 1.10.1

- **owner**
  - Usage: Within state, character, or combatant scope only
  - Target type: Country scope
  - Example: owner = { add_ideas = owns_this_state }
  - Description:
    ```text
    In state scope, the country that owns the state. In
    combatant scope
    , the country that owns the divisions. In character scope, the country that has recruited the character.
    Subject to the 'invalid event target' error
    when used for a state.
    ```
  - Usable as target: X
  - Version Added: 1.0

- **controller**
  - Usage: Within state scope only
  - Target type: Country scope
  - Example:
    ```text
    controller = { 
        ROOT = {
            create_wargoal = {
                target = PREV
                type = take_state_focus
                generator = { 123 }
            }
        }
    }
    ```
  - Description:
    ```text
    The controller of the current state.
    Subject to the 'invalid event target' error.
    ```
  - Usable as target: X
  - Version Added: 1.0

- **capital_scope**
  - Usage: Within country scope only
  - Target type: State scope
  - Example: capital_scope = { … }
  - Description:
    ```text
    The state where the capital of the current country is located in.
    Subject to the 'invalid event target' error
    in rare cases.
    ```
  - Usable as target: X
  - Version Added: 1.0

- **event_target:<event_target_key>**
  - Usage: Always usable
  - Target type: Depends on usage
  - Example: event_target:my_event_target = { … }
  - Description:
    ```text
    Saved
    event target or global event target
    , with no space after the colon.
    Subject to the 'invalid event target' error.
    ```
  - Usable as target: ✓
  - Version Added: 1.0

- **var:<variable>**
  - Usage: Always usable
  - Target type: Depends on usage
  - Example:
    ```text
    var:my_variable = { … }
    add_to_faction = my_variable
    or
    add_to_faction = var:my_variable
    ```
  - Description:
    ```text
    Variable
    set to a scope.
    When used as a target rather than a scope, the
    var:
    can be omitted in most cases.
    ```
  - Usable as target: ✓
  - Version Added: 1.5

## Flow control tools

*Main article: [Scopes#Flow control tools](<Scopes - Hearts of Iron 4 Wiki.md#flow-control-tools>)*

These are triggers that serve as more of a way to establish a connection in how triggers are evaluated. Each one serves as a trigger scope with additional arguments and can be used regardless of scope.

- **AND**
  - Additional parameters: None
  - Example:
    ```text
    AND = {
        original_tag = GER
        has_stability > 0.5
    }
    ```
  - Description: Returns false if any sub-trigger returns false, true otherwise. Evaluation stops at the first false sub-trigger.
  - Notes:
    ```text
    Only necessary within
    OR statements
    and
    NOT statements
    , as everything else is implicitly AND.
    ```
  - Version Added: 1.0

- **OR**
  - Additional parameters: None
  - Example:
    ```text
    OR = {
        original_tag = ENG
        original_tag = USA
    }
    ```
  - Description: Returns true if any sub-trigger returns true, false otherwise. Evaluation stops at the first true sub-trigger.
  - Version Added: 1.0

- **NOT**
  - Additional parameters: None
  - Example:
    ```text
    NOT = {
        has_stability > 0.5
        has_war_support > 0.5
    }
    ```
  - Description: Returns false if any sub-trigger returns true, true otherwise. Evaluation stops at the first true sub-trigger.
  - Notes: Equivalent to a NOR rather than a NAND.
  - Version Added: 1.0

- **count_triggers**
  - Additional parameters:
    ```text
    amount = <int>
    The amount of triggers that need to be fulfilled.
    ```
  - Example:
    ```text
    count_triggers = {
        amount = 2
        10 = { state_population = 100000 }
        11 = { state_population = 100000 }
        12 = { state_population = 100000 }
    }
    ```
  - Description:
    ```text
    Sums the results of all sub-triggers (false=0, true=1) and returns true if the sum is at least
    amount
    .
    ```
  - Version Added: 1.5

- **if**
  - Additional parameters:
    ```text
    limit = <trigger block>
    else_if = <if-trigger>
    Alternative condition. Optional.
    else = <AND-trigger>
    Final alternative condition. Optional.
    ```
  - Example:
    ```text
    if = {
        limit = {
            has_dlc = "Poland: United and Ready"
        }
        has_political_power > 100
    }
    else_if = {
        limit = {
            has_dlc = "Waking the Tiger"
        }
        has_war_support > 0.5
    }
    else = {
        always = no
    }
    ```
  - Description:
    ```text
    If
    limit
    is true, the sub-triggers are evaluated like an AND-trigger. If
    limit
    is false,
    else_if
    blocks are tried in sequence and finally
    else
    (if present).
    Otherwise true is returned
    .
    ```
  - Notes:
    ```text
    Both nested (As in inside of
    if = { ... }
    ) and unnested (As in the example)
    else
    and
    else_if
    exist. In case of overlap, unnested is preferred.
    Can be useful for tooltip management: same as in effects, if the limit is unmet, nothing appears. If it is met, then the limit is hidden while the condition outside of the limit appears in the tooltip.
    if = { limit = { trigger_1 = yes } trigger_2 = yes }
    is equivalent to
    OR = { NOT = { trigger_1 = yes } trigger_2 = yes }
    , but generates a different tooltip.
    ```
  - Version Added: 1.0

- **hidden_trigger**
  - Additional parameters: None
  - Example:
    ```text
    hidden_trigger = {
        country_exists = GER
    }
    ```
  - Description: Hides the triggers from the tooltip shown to the player.
  - Notes:
    ```text
    Also serves as an
    AND statement
    .
    ```
  - Version Added: 1.0

- **custom_trigger_tooltip**
  - Additional parameters:
    ```text
    tooltip = <string>
    The localisation key to use.
    ```
  - Example:
    ```text
    custom_trigger_tooltip = {
        tooltip = sunrise_invasion_tt		
        any_state = {
            is_owned_by = JAP
            is_on_continent = europe
            is_coastal = yes
        }
    }
    ```
  - Description: Hides the triggers from the tooltip shown to the player and instead uses the specified localisation key.
  - Notes:
    ```text
    Alias for
    #custom_override_tooltip
    trigger (see that trigger for more info). Kept for backward compatibility. Prefer
    #custom_override_tooltip
    instead.
    Also supports
    Localisation#Bindable_localisation
    .
    ```
  - Version Added: 1.0

- **custom_override_tooltip**
  - Additional parameters:
    ```text
    tooltip = <string>
    The localisation key to use.
    not_tooltip = <string>
    The localisation key to use for NOT block. Optional.
    ```
  - Example:
    ```text
    custom_override_tooltip = {
        tooltip = {
          localization_key = GER_inner_circle_focus_in_progress_tt
    	  CHARACTER = GER_rudolf_hess
    	  FLAG_DAYS = [?GER_rally_the_industrialists_in_progress_flag:days]
        }
        not_tooltip = MY_TOOLTIP_NOT
        <triggers>
    }
    ```
  - Description:
    ```text
    An
    AND
    trigger that has an overriden custom tooltip.
    ```
  - Notes:
    ```text
    A positive tooltip can be set with
    tooltip
    and the tooltip to be used inside a
    NOT
    can be set with
    not_tooltip
    . If no positive tooltip is provided and the root key is a localization key (not a formatter, see formatted localization), then a negative tooltip will be generated by appending
    _NOT
    to the root localization for the positive tooltip. Both
    tooltip
    and
    not_tooltip
    are bindable localizations.
    Can also be used as effect.
    Also supports
    Localisation#Bindable_localisation
    .
    ```
  - Version Added: 1.15

## Any scope

These triggers do not require any particular scope.

### General

- **always**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    always = yes
    ```
  - Description: Always returns true or false. Useful for debugging.
  - Version Added: 1.0

- **has_global_flag**
  - Parameters:
    ```text
    <string>
    The flag to check.
    ```
  - Example:
    ```text
    has_global_flag = my_flag
    ```
  - Description: Checks if the specified flag has been set.
  - Version Added: 1.0

- **has_global_flag**
  - Parameters:
    ```text
    flag = <string>
    The flag to check.
    value = <int>
    The flag value to check for. Optional.
    date = <date>
    The flag creation date to check for. Optional.
    days = <int>
    The duration the flag existed for. Optional.
    ```
  - Example:
    ```text
    has_global_flag = {
        flag = my_flag
        days > 30
        date > 1936.6.1
        value > 0
    }
    ```
  - Description: Compares the specified flag's last set date, days since last set, and/or value.
  - Notes:
    ```text
    If not set, the value comparison is
    >0
    .
    value
    is limited between -32768 and 32767.
    ```
  - Version Added: 1.0

- **has_dlc**
  - Parameters:
    ```text
    <string>
    The DLC name to check for.
    ```
  - Example:
    ```text
    has_dlc = "Waking the Tiger"
    ```
  - Description: Checks if the specified DLC is enabled.
  - Version Added: 1.0

- **has_start_date**
  - Parameters:
    ```text
    <date>
    The date to check for.
    ```
  - Example:
    ```text
    has_start_date > 1950.01.01
    ```
  - Description: Checks if the specified date was the start date used for the current game.
  - Notes:
    ```text
    Year.Month.Day
    Must use either > or < operators.
    ```
  - Version Added: 1.0

- **date**
  - Parameters:
    ```text
    <date>
    The date to check for.
    ```
  - Example:
    ```text
    date < 1950.01.01
    ```
  - Description: Checks if the specified date against the current date.
  - Notes:
    ```text
    Year.Month.Day
    Must use either > or < operators.
    ```
  - Version Added: 1.0

- **difficulty**
  - Parameters:
    ```text
    <int>
    The difficulty value.
    ```
  - Example:
    ```text
    difficulty > 0
    ```
  - Description: checks if the specified difficulty against the current difficulty.
  - Notes: Must use either > or < operators.
  - Version Added: 1.0

- **has_any_custom_difficulty_setting**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    has_any_custom_difficulty_setting = yes
    ```
  - Description: Checks if any custom difficulty setting is changed from their default value.
  - Notes:
    ```text
    Custom difficulty in this case refers to
    /Hearts of Iron IV/common/difficulty_settings/*.txt
    , used in base game to strengthen a specific country.
    ```
  - Version Added: 1.0

- **has_custom_difficulty_setting**
  - Parameters:
    ```text
    <string>
    The setting to check.
    ```
  - Example:
    ```text
    has_custom_difficulty_setting = custom_diff_strong_sov
    ```
  - Description: Checks if the specified custom difficulty setting is changed from the default value.
  - Notes:
    ```text
    Custom difficulty in this case refers to
    /Hearts of Iron IV/common/difficulty_settings/*.txt
    , used in base game to strengthen a specific country.
    ```
  - Version Added: 1.0

- **game_rules_allow_achievements**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    game_rules_allow_achievements = yes
    ```
  - Description: Checks if all of the active game rule options allow achievements.
  - Version Added: 1.9

- **country_exists**
  - Parameters:
    ```text
    <scope> / <variable>
    The country to check.
    ```
  - Example:
    ```text
    country_exists = GER
    ```
  - Description: Checks if the specified country currently exists in game.
  - Version Added: 1.0

- **is_ironman**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    is_ironman = yes
    ```
  - Description: Checks if the current game is running in Ironman mode.
  - Version Added: 1.0

- **is_historical_focus_on**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    is_historical_focus_on = yes
    ```
  - Description: Checks if the current game is running with Historical Focuses on.
  - Version Added: 1.0

- **is_tutorial**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    is_tutorial = yes
    ```
  - Description: Checks if the current game is running in Tutorial mode.
  - Version Added: 1.0

- **is_debug**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    is_debug = yes
    ```
  - Description: Checks if game is in debug mode (launched with -debug argument).
  - Version Added: 1.9

- **threat**
  - Parameters:
    ```text
    <float>
    The amount to check for.
    ```
  - Example:
    ```text
    threat > 0.5
    ```
  - Description: Checks if World Tension is above the specified amount.
  - Notes: Must use either > or < operators.
  - Version Added: 1.0

- **has_game_rule**
  - Parameters:
    ```text
    <string>
    The game rule to check for.
    <string> / <bool>
    The option to check.
    ```
  - Example:
    ```text
    has_game_rule = { rule = GER_can_remilitarize_rhineland option = yes }
    ```
  - Description: Checks if a game rule is set to a particular option.
  - Version Added: 1.5

- **has_completed_custom_achievement**
  - Parameters:
    ```text
    mod = <mod ID>
    The mod where the achievement is from.
    achievement = <achievement ID>
    The name of the achievement.
    ```
  - Example:
    ```text
    has_completed_custom_achievement = {
        mod = my_mod_unique_id
        achievement = my_achievement_token
    }
    ```
  - Description: Checks if the player controlling the current scope has completed the specified custom achievement.
  - Notes:
    ```text
    The achievement (including the ID of the mod it's from) is defined within
    /Hearts of Iron IV/common/achievements/*.txt
    files
    . The achievement could be completed during a previous session, not necessarily the current one.
    If the mod defining the achievement is not loaded, the trigger evaluates as false.
    ```
  - Version Added: 1.12.5

### Career profile

- **career_profile_check_medal**
  - Parameters:
    ```text
    medal = <medal>
    Medal to check.
    ???
    ```
  - Example:
    ```text
    career_profile_check_medal = {
      medal = raining_debris_medal
      ???
    }
    ```
  - Description: Checks if the required medal is achieved and collected.
  - Notes: Provide no tooltip.
  - Version Added: ???

- **career_profile_check_ribbon**
  - Parameters:
    ```text
    ribbon = <ribbon>
    Ribbon to check.
    tooltip = <loc_key>
    Optional.
    ```
  - Example:
    ```text
    career_profile_check_ribbon = {
      ribbon = orchestra_of_boom
      tooltip = my_loc_key
    }
    ```
  - Description: Checks if the required ribbon is achieved and collected.
  - Notes: By default provide no tooltip.
  - Version Added: ???

- **career_profile_check_playthrough_ratio**
  - Parameters:
    ```text
    frits = <variable>
    second = <variable>
    ratio = <int>
    Ratio.
    compare = <type>
    The type of comparison.
    ```
  - Example:
    ```text
    career_profile_check_playthrough_ratio = {
      first = enemy_casualties
      second = total_own_casualties
      ratio = 4
      compare = greater_than_or_equals
    }
    ```
  - Description: Compares the ratio (first/second) of two playthrough values to a number.
  - Notes:
    ```text
    Provide no tooltip.
    Possible compare types:
    less_than
    less_than_or_equals
    greater_than
    greater_than_or_equals
    equals
    not_equals
    ```
  - Version Added: ???

- **career_profile_check_playthrough_value**
  - Parameters:
    ```text
    { ... }
    OR
    var = <variable>
    Value to compare.
    value = <int>
    Value to compare to.
    compare = <type>
    The type of comparison. Optional.
    tooltip = <loc_key>
    Optional.
    tooltip_value = <int>
    Optional.
    ```
  - Example:
    ```text
    career_profile_check_playthrough_value = {
      plan_landlocked_battleship > 1
      plan_landlocked_carrier > 0
    }
    ```
  - Example:
    ```text
    career_profile_check_playthrough_value = {
      var = deployed_airplanes_with_air_defense_gold
      value = 100
      compare = greater_than_or_equals
      tooltip = CAREER_PROFILE_TRIGGER_DEPLOYED_AIRPLANES_WITH_AIR_DEFENSE
      tooltip_value = 100
    ```
  - Description: Compares a playthrough value to a number.
  - Notes:
    ```text
    By default provide no tooltip.
    Possible compare types:
    less_than
    less_than_or_equals
    greater_than
    greater_than_or_equals
    equals
    not_equals
    ```
  - Version Added: ???

- **career_profile_check_points**
  - Parameters:
    ```text
    value = <int>
    Value to compare.
    compare = <type>
    The type of comparison.
    tooltip = <loc_key>
    Optional.
    ```
  - Example:
    ```text
    career_profile_check_points = {
      value = 5000
      compare = greater_than_or_equals
      tooltip = CAREER_PROFILE_TRIGGER_MINED_SEA_REGIONS
    }
    ```
  - Description: Compares a career points value to a number.
  - Notes:
    ```text
    By default provide no tooltip.
    Possible compare types:
    less_than
    less_than_or_equals
    greater_than
    greater_than_or_equals
    equals
    not_equals
    ```
  - Version Added: ???

- **career_profile_check_ratio**
  - Parameters:
    ```text
    Possible the same as
    #career_profile_check_playthrough_ratio
    .
    ```
  - Examples:
    ```text
    Possible the same as
    #career_profile_check_playthrough_ratio
    .
    ```
  - Description: Compares the ratio (first/second) of two career profile values to a number.
  - Notes:
    ```text
    Possible the same as
    #career_profile_check_playthrough_ratio
    .
    ```
  - Version Added: ???

- **career_profile_check_value**
  - Parameters:
    ```text
    Possible the same as
    #career_profile_check_playthrough_value
    .
    ```
  - Examples:
    ```text
    Possible the same as
    #career_profile_check_playthrough_value
    .
    ```
  - Description: Compares a career profile value to a number.
  - Notes:
    ```text
    Possible the same as
    #career_profile_check_playthrough_value
    .
    ```
  - Version Added: ???

- **career_profile_has_player_flag**
  - Parameters:
    ```text
    <string>
    The flag to check.
    ```
  - Example:
    ```text
    career_profile_has_player_flag = career_profile_overrun_infantry_flag
    ```
  - Description: Checks if the flag is set for the local player.
  - Version Added: ???

### Variables

- **has_variable**
  - Parameters:
    ```text
    <variable>
    The variable to check.
    ```
  - Example:
    ```text
    has_variable = my_var
    ```
  - Description: Checks if the specified variable exists for the current scope.
  - Version Added: 1.5

- **check_variable**
  - Parameters:
    ```text
    var = <variable>
    The variable to check.
    value = <float> / <variable>
    The value to check for.
    compare = <type>
    The type of comparison. Optional, can use < or > instead.
    ```
  - Example:
    ```text
    check_variable = {
        var = my_var
        value = 10
        compare = greater_than_or_equals
    }
    ```
  - Example:
    ```text
    check_variable = {
        my_var > 10
    }
    ```
  - Description: Check the specified variable for the current scope.
  - Notes:
    ```text
    Possible compare types:
    less_than
    less_than_or_equals
    greater_than
    greater_than_or_equals
    equals
    not_equals
    ```
  - Version Added: 1.5

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

### Debugging

These are usable as both effects and triggers and are used for debugging, with the player never seeing them.

- **log**
  - Parameters:
    ```text
    <string>
    What to log. Supports dynamic localisation.
    ```
  - Example:
    ```text
    log = "Added [?temp_add] to [THIS.GetTag]'s variable [?THIS.varvalue]"
    ```
  - Description: Appends an entry into the game.log and, if open, the console when evaluating the trigger.
  - Notes:
    ```text
    game.log is stored within
    /Hearts of Iron IV/logs/
    in the
    user directory
    ```
  - Version Added: 1.5

- **print_variables**
  - Parameters:
    ```text
    print_global = <bool>
    Print global variables. Defaults to
    no
    .
    var_list = <list>
    The variables to print. Defaults to all variables.
    file = <string>
    The file path to log to. Defaults to "variable_dump". Does not include the
    .log
    extension.
    text = <string>
    Text to prepend. Defaults to "No Header".
    append = <bool>
    Whether to append to the file instead of overwrite. Defaults to
    yes
    ```
  - Example:
    ```text
    print_variables = {
        var_list = { myvar1 myvar2 }
        file = "my_dump_file"
        text = "my header"
    }
    ```
  - Description: Dumps the specified variables from the current scope and optionally the global scope into a log file with the specified name.
  - Notes:
    ```text
    The log will be within
    /Hearts of Iron IV/logs/variable_dumps/
    in the
    user directory
    . See also
    debugging variables
    .
    ```
  - Version Added: 1.5

## Country scope

Can be used in **country** scope.

### General

- **exists**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    exists = yes
    ```
  - Description: Checks if the current scope exists in game.
  - Version Added: 1.0

- **tag**
  - Parameters:
    ```text
    <scope> / <variable>
    The country to check.
    ```
  - Example:
    ```text
    tag = GER
    ```
  - Example:
    ```text
    tag = var:my_country
    ```
  - Description: Checks if the current scope is the specified country.
  - Notes:
    ```text
    Only checks the actual tag while excluding dynamic countries, see
    original_tag
    if they should be included.
    ```
  - Version Added: 1.0

- **original_tag**
  - Parameters:
    ```text
    <scope> / <variable>
    The country to check.
    ```
  - Example:
    ```text
    original_tag = GER
    ```
  - Example:
    ```text
    original_tag = var:my_country
    ```
  - Description: Checks if the current scope originates from the specified country.
  - Notes:
    ```text
    This also includes dynamic countries: civil war breakaways and countries created via
    create_dynamic_country
    . True for the original country.
    ```
  - Version Added: 1.0

- **is_ai**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    is_ai = yes
    ```
  - Description: Checks if the current scope is AI.
  - Version Added: 1.0

- **has_collaboration**
  - Parameters:
    ```text
    target = <country>
    The country to check.
    value <> <decimal>
    The value of the collaboration on the 0-1 scale.
    ```
  - Example:
    ```text
    has_collaboration = {
        target = GER
        value > 0.5
    }
    ```
  - Description: Checks if the current scope has a collaboration level in the target scope.
  - Notes: The target is occupied by the current scope. Must use < or > in the value argument.
  - Version Added: 1.9

- **has_country_flag**
  - Parameters:
    ```text
    <string>
    The flag to check.
    ```
  - Example:
    ```text
    has_country_flag = my_flag
    ```
  - Description: Checks if the current scope has the specified flag.
  - Version Added: 1.0

- **has_country_flag**
  - Parameters:
    ```text
    flag = <string>
    The flag to check.
    value = <int>
    The flag value to check for. Optional.
    date = <date>
    The flag creation date to check for. Optional.
    days = <int>
    The duration the flag existed for. Optional.
    ```
  - Example:
    ```text
    has_country_flag = {
        flag = my_flag
        days > 30
        date > 1936.6.1
        value > 0
    }
    ```
  - Description: Compares the specified flag's last set date, days since last set, and/or value.
  - Notes:
    ```text
    If not set, the value comparison is
    >0
    .
    value
    is limited between -32768 and 32767.
    ```
  - Version Added: 1.0

- **has_cosmetic_tag**
  - Parameters:
    ```text
    <string>
    The cosmetic tag to check.
    ```
  - Example:
    ```text
    has_cosmetic_tag = SOV_custom
    ```
  - Description: Checks if the current scope has the specified cosmetic tag active.
  - Version Added: 1.5

- **has_event_target**
  - Parameters:
    ```text
    <event target>
    The event target to check.
    ```
  - Example:
    ```text
    has_event_target = my_var
    ```
  - Description: Checks if current scope or global scope has the specified event target saved.
  - Version Added: 1.0

- **has_decision**
  - Parameters:
    ```text
    <string>
    The decision to check.
    ```
  - Example:
    ```text
    has_decision = my_decision
    ```
  - Description: Checks if the current scope has the specified decision activated.
  - Version Added: 1.5

- **has_dynamic_modifier**
  - Parameters:
    ```text
    modifier = <string>
    The dynamic_modifier to check.
    scope = <scope>
    The country to check. Optional, if the original modifier has been targeted.
    ```
  - Example:
    ```text
    has_dynamic_modifier = {
        modifier = my_dynamic_modifier
        scope = GER
    }
    ```
  - Description: Checks if the current scope has the specified dynamic modifier activated.
  - Version Added: 1.6

- **has_active_mission**
  - Parameters:
    ```text
    <string>
    The mission to check.
    ```
  - Example:
    ```text
    has_active_mission = my_mission
    ```
  - Description: Checks if the current scope has the specified mission active.
  - Version Added: 1.5

- **has_country_custom_difficulty_setting**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    has_country_custom_difficulty_setting = yes
    ```
  - Description: Checks if the any custom difficulty setting targeting the current scope is changed from the default value.
  - Notes:
    ```text
    Custom difficulty in this case refers to
    /Hearts of Iron IV/common/difficulty_settings/*.txt
    , used in base game to strengthen a specific country.
    ```
  - Version Added: 1.0

- **has_terrain**
  - Parameters:
    ```text
    <terrain>
    Terrain.
    ```
  - Example:
    ```text
    has_terrain = urban
    ```
  - Description: Checks if the current scope has any provinces of the specified terrain.
  - Notes: Only can be used in country scope.
  - Version Added: 1.11

- **is_dynamic_country**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    is_dynamic_country = yes
    ```
  - Description: Checks if the current scope is a dynamic country.
  - Notes: Dynamic countries include those generated in civil wars as well as those generated with the create_dynamic_country effect, such as collaboration governments.
  - Version Added: 1.11

- **num_of_supply_nodes**
  - Parameters:
    ```text
    <int>
    The amount to check for.
    ```
  - Example:
    ```text
    num_of_supply_nodes > 10
    ```
  - Description: Checks if the current scope has the specified amount of supply nodes under control.
  - Notes: Can only use < or > operators.
  - Version Added: 1.11

- **<resource> (resource_count_trigger)**
  - Parameters:
    ```text
    <int>
    The amount to check for.
    ```
  - Example:
    ```text
    tungsten > 10
    ```
  - Description: Checks if the current scope has the specified amount of the specified resource.
  - Notes:
    ```text
    Must use either > or < operators for amount.
    Can also be used in state scope.
    ```
  - Version Added: ???

- **has_resources_in_country**
  - Parameters:
    ```text
    resource = <resource>
    The resource to check for.
    amount = <int>
    The amount to check for.
    extracted = <bool>
    Limits the checked resources only to those gained from the state's base value and multiplicative modifiers on top of it if true. Optional, defaults to false.
    buildings = <bool>
    Limits the checked resources only to those gained from the state's modifiers applied by buildings. Optional, defaults to false.
    ```
  - Example:
    ```text
    has_resources_in_country = {
        resource = oil
        amount > 10
        extracted = yes
    }
    ```
  - Description: Checks if the current scope has the specified amount of the specified resource in reserve.
  - Notes: Must use either > or < operators for amount. 'In reserve' means that it's not spent on equipment production or exports.
  - Version Added: 1.12

### National focuses

- **has_focus_tree**
  - Parameters:
    ```text
    <string>
    The focus tree to check.
    ```
  - Example:
    ```text
    has_focus_tree = soviet_tree
    ```
  - Description: Checks if the current scope has the specified focus tree.
  - Version Added: 1.3

- **has_completed_focus**
  - Parameters:
    ```text
    <string>
    The focus to check.
    ```
  - Example:
    ```text
    has_completed_focus = my_focus
    ```
  - Description: Checks if the current scope has the specified focus completed.
  - Version Added: 1.0

- **focus_progress**
  - Parameters:
    ```text
    focus = <string>
    The focus to check.
    progress = <string>
    The progress to check for.
    ```
  - Example:
    ```text
    focus_progress = {
      focus = my_focus
      progress > 0.5
    }
    ```
  - Description: Checks if the specified focus has been completed the specified percent for the current scope.
  - Notes: Must use either > or < operators for progress.
  - Version Added: 1.0

- **has_shine_effect_on_focus**
  - Parameters:
    ```text
    <string>
    The focus to check.
    ```
  - Example:
    ```text
    has_shine_effect_on_focus = GER_wunderwaffe
    ```
  - Description: Check if country has shine effect on focus (either manually achieved or by being worked on).
  - Notes:
    ```text
    Note that tooltips are only shown in debug mode.
    Shine can be added manually by selecting focus, or via
    activate_shine_on_focus
    effect.
    ```
  - Version Added: 1.15

### Politics

- **<ideology> (ideology_support_trigger)**
  - Parameters:
    ```text
    <ideology> = <float> / <variable>
    The amount of the ideology to check for.
    ```
  - Example:
    ```text
    fascism > 0.5
    ```
  - Example:
    ```text
    democratic > party_popularity@communism
    ```
  - Description: Checks if the current scope has popularity of the specified ideology above the specified amount.
  - Version Added: 1.0

- **has_political_power**
  - Parameters:
    ```text
    <float>
    The amount to check for.
    ```
  - Example:
    ```text
    has_political_power > 100
    ```
  - Description: Checks if the current scope has the specified amount of political power.
  - Notes: Must use either > or < operators.
  - Version Added: 1.0

- **political_power_daily**
  - Parameters:
    ```text
    <float> / <variable>
    The amount to check for.
    ```
  - Example:
    ```text
    political_power_daily > 1
    ```
  - Description: Checks if the current scope has the specified amount of daily political power gain.
  - Notes: Must use either > or < operators.
  - Version Added: 1.5

- **political_power_growth**
  - Parameters:
    ```text
    <float> / <variable>
    The amount to check for.
    ```
  - Example:
    ```text
    political_power_growth > 1
    ```
  - Description: Checks if the current scope has the specified amount of daily political power gain.
  - Notes: Must use either > or < operators.
  - Version Added: 1.5

- **command_power**
  - Parameters:
    ```text
    <float> / <variable>
    The amount to check for.
    ```
  - Example:
    ```text
    command_power > 1
    ```
  - Description: Checks if the current scope has the specified amount of command power.
  - Notes: Must use either > or < operators.
  - Version Added: 1.5

- **command_power_daily**
  - Parameters:
    ```text
    <float> / <variable>
    The amount to check for.
    ```
  - Example:
    ```text
    command_power_daily > 1
    ```
  - Description: Checks if the current scope has the specified amount of daily command power gain.
  - Notes: Must use either > or < operators.
  - Version Added: 1.5

- **has_war_support**
  - Parameters:
    ```text
    <float> / <variable>
    The amount to check for.
    ```
  - Example:
    ```text
    has_war_support > 0.5
    ```
  - Description: Checks if the current scope has the specified percentage of War Support.
  - Notes: Must use either > or < operators.
  - Version Added: 1.5

- **has_stability**
  - Parameters:
    ```text
    <float> / <variable>
    The amount to check for.
    ```
  - Example:
    ```text
    has_stability > 0.5
    ```
  - Description: Checks if the current scope has the specified percentage of Stability.
  - Notes: Must use either > or < operators.
  - Version Added: 1.5

- **has_government**
  - Parameters:
    ```text
    <ideology>
    The ideology group to check for.
    OR
    <country>
    The country to compare with.
    ```
  - Example:
    ```text
    has_government = fascism
    ```
  - Example:
    ```text
    has_government = ROOT
    ```
  - Description: Checks if the ruling party of the current scope meets the requirements of being either the specified ideology group or having the same ideology group as the specified country.
  - Version Added: 1.0

- **has_elections**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    has_elections = yes
    ```
  - Description: Checks if the current scope holds elections.
  - Version Added: 1.0

- **is_staging_coup**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    is_staging_coup = yes
    ```
  - Description: Checks if the current scope is staging a coup.
  - Version Added: 1.3

- **is_target_of_coup**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    is_target_of_coup = yes
    ```
  - Description: Checks if the current scope is the target of a coup.
  - Version Added: 1.0

- **has_civil_war**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    has_civil_war = yes
    ```
  - Description: Checks if the current scope has a civil war active.
  - Version Added: 1.0

- **civilwar_target**
  - Parameters:
    ```text
    <scope>
    The target country.
    ```
  - Example:
    ```text
    civilwar_target = GER
    ```
  - Description: Checks if the specified country is a target of a civil war.
  - Version Added: 1.0

- **has_manpower_for_recruit_change_to**
  - Parameters:
    ```text
    value = <float>
    The amount to check for.
    group = <group>
    The group to check for.
    ```
  - Example:
    ```text
    has_manpower_for_recruit_change_to = {
        value > 0.05
        group = mobilization_laws
    }
    ```
  - Description: Checks if the current scope has the specified amount of manpower for changing the specified idea group.
  - Notes:
    ```text
    Must
    use either > or < operators as = operator checks for the
    exact
    value
    ```
  - Version Added: 1.0

- **has_rule**
  - Parameters:
    ```text
    <string>
    The rule to check for.
    ```
  - Example:
    ```text
    has_rule = can_create_factions
    ```
  - Description: Checks if the current scope has the specified country rule.
  - Version Added: 1.6

- **has_casualties_war_support**
  - Parameters:
    ```text
    <float> / <variable>
    The amount to check for.
    ```
  - Example:
    ```text
    has_casualties_war_support < 0
    ```
  - Description: Checks if the current scope has the specified percentage of war support from own combat casualties.
  - Notes: Must use either > or < operators.
  - Version Added: 1.12

- **has_convoys_war_support**
  - Parameters:
    ```text
    <float> / <variable>
    The amount to check for.
    ```
  - Example:
    ```text
    has_convoys_war_support < 0
    ```
  - Description: Checks if the current scope has the specified percentage of war support from own convoys sunk.
  - Notes: Must use either > or < operators.
  - Version Added: 1.12

- **has_bombing_war_support**
  - Parameters:
    ```text
    <float> / <variable>
    The amount to check for.
    ```
  - Example:
    ```text
    has_bombing_war_support < 0
    ```
  - Description: Checks if the current scope has the specified percentage of war support from own states bombed by the enemy.
  - Notes: Must use either > or < operators.
  - Version Added: 1.12

### Balance of power

Balances of power are stored within /Hearts of Iron IV/common/bop/\*.txt files.

- **has_power_balance**
  - Parameters:
    ```text
    id = <bop ID>
    The balance to check for.
    ```
  - Example:
    ```text
    has_power_balance = {
        id = TAG_my_bop
    }
    ```
  - Description: Checks if the current scope has the specified balance of power active.
  - Version Added: 1.12

- **has_any_power_balance**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    has_any_power_balance = yes
    ```
  - Description: Checks if the current scope has any balance of power active.
  - Version Added: 1.12

- **power_balance_value**
  - Parameters:
    ```text
    id = <bop ID>
    The balance to check in.
    value = <float>
    The value to check for.
    ```
  - Example:
    ```text
    power_balance_value = {
        id = TAG_my_bop
        value > 0.7
    }
    ```
  - Description: Checks if the current scope has the specified value within the balance of power.
  - Notes: Either =, >, or < operators are allowed.
  - Version Added: 1.12

- **power_balance_daily_change**
  - Parameters:
    ```text
    id = <bop ID>
    The balance to check in.
    value = <float>
    The value to check for.
    ```
  - Example:
    ```text
    power_balance_daily_change = {
        id = TAG_my_bop
        value < -0.01
    }
    ```
  - Description: Checks if the current scope's balance of power changes each day by the specified value.
  - Notes: Either =, >, or < operators are allowed.
  - Version Added: 1.12

- **power_balance_weekly_change**
  - Parameters:
    ```text
    id = <bop ID>
    The balance to check in.
    value = <float>
    The value to check for.
    ```
  - Example:
    ```text
    power_balance_weekly_change = {
        id = TAG_my_bop
        value < -0.01
    }
    ```
  - Description: Checks if the current scope's balance of power changes each week by the specified value.
  - Notes: Either =, >, or < operators are allowed.
  - Version Added: 1.12

- **is_power_balance_in_range**
  - Parameters:
    ```text
    id = <bop ID>
    The balance to check in.
    range = <range ID>
    The range to check for.
    ```
  - Example:
    ```text
    is_power_balance_in_range = {
        id = TAG_my_bop
        range > TAG_my_bop_right_range
    }
    ```
  - Description: Checks if the current scope's balance of power value lies within the specified range.
  - Notes:
    ```text
    Ranges are defined within the balance of power. Can use either =, >, and < operators. In case of > or <, the comparison is 'strict', i.e. excluding the range itself.
    ```
  - Version Added: 1.12

- **is_power_balance_side_active**
  - Parameters:
    ```text
    id = <bop ID>
    The balance to check in.
    side = <side ID>
    The side to check.
    ```
  - Example:
    ```text
    is_power_balance_side_active = {
        id = TAG_my_bop
        side = TAG_my_bop_right_range
    }
    ```
  - Description: Checks if the specified balance of power has a side active.
  - Notes: Sides are defined within the balance of power. "Active" means that the side is among those that are currently visible instead of relying on the current value.
  - Version Added: 1.12

- **has_power_balance_modifier**
  - Parameters:
    ```text
    id = <bop ID>
    The balance to check in.
    modifier = <modifier ID>
    The
    static modifier
    .
    ```
  - Example:
    ```text
    has_power_balance_modifier = {
        id = TAG_my_bop
        modifier = TAG_my_bop_modifier
    }
    ```
  - Description: Checks if the current scope's balance of power value activates a modifier.
  - Notes:
    ```text
    BoP modifiers are defined within
    /Hearts of Iron IV/common/modifiers/*.txt
    files, while they're activated in the balance of power definition.
    ```
  - Version Added: 1.12

### Buildings

- **<building> (building_count_trigger)**
  - Parameters:
    ```text
    <int>
    The amount of the specified building to to check for.
    ```
  - Example:
    ```text
    arms_factory > 10
    ```
  - Description: Checks if the current scope has the specified amount of the specified building.
  - Notes:
    ```text
    Must use either > or < operators. Works in the state scope as well, unlike the other triggers.
    Can also be used in state scope.
    ```
  - Version Added: 1.0

- **num_of_military_factories**
  - Parameters:
    ```text
    <int>
    The amount to check for.
    ```
  - Example:
    ```text
    num_of_military_factories > 10
    ```
  - Description: Checks if the current scope has the specified amount of military factories.
  - Notes: Must use either > or < operators.
  - Version Added: 1.0

- **num_of_civilian_factories**
  - Parameters:
    ```text
    <int>
    The amount to check for.
    ```
  - Example:
    ```text
    num_of_civilian_factories > 10
    ```
  - Description: Checks if the current scope has the specified amount of civilian factories.
  - Notes: Must use either > or < operators.
  - Version Added: 1.0

- **num_of_naval_factories**
  - Parameters:
    ```text
    <int>
    The amount to check for.
    ```
  - Example:
    ```text
    num_of_naval_factories > 10
    ```
  - Description: Checks if the current scope has the specified amount of dockyards.
  - Notes: Must use either > or < operators.
  - Version Added: 1.0

- **num_of_available_military_factories**
  - Parameters:
    ```text
    <int>
    The amount to check for.
    ```
  - Example:
    ```text
    num_of_available_military_factories > 10
    ```
  - Description: Checks if the current scope has the specified amount of available military factories.
  - Notes: Must use either > or < operators.
  - Version Added: 1.0

- **num_of_available_civilian_factories**
  - Parameters:
    ```text
    <int>
    The amount to check for.
    ```
  - Example:
    ```text
    num_of_available_civilian_factories > 10
    ```
  - Description: Checks if the current scope has the specified amount of available civilian factories.
  - Notes: Must use either > or < operators.
  - Version Added: 1.0

- **num_of_available_naval_factories**
  - Parameters:
    ```text
    <int>
    The amount to check for.
    ```
  - Example:
    ```text
    num_of_available_naval_factories > 10
    ```
  - Description: Checks if the current scope has the specified amount of available dockyards.
  - Notes: Must use either > or < operators.
  - Version Added: 1.0

- **num_of_factories**
  - Parameters:
    ```text
    <int>
    The amount to check for.
    ```
  - Example:
    ```text
    num_of_factories > 10
    ```
  - Description: Checks if the current scope has the specified amount of military, civilian or dockyard factories.
  - Notes: Must use either > or < operators.
  - Version Added: 1.0

- **num_of_controlled_factories**
  - Parameters:
    ```text
    <int>
    The amount to check for.
    ```
  - Example:
    ```text
    num_of_controlled_factories > 10
    ```
  - Description: Checks if the current scope has the specified amount of military, civilian or dockyard factories under control.
  - Notes: Must use either > or < operators.
  - Version Added: 1.11

- **num_of_owned_factories**
  - Parameters:
    ```text
    <int>
    The amount to check for.
    ```
  - Example:
    ```text
    num_of_owned_factories > 10
    ```
  - Description: Checks if the current scope has the specified amount of military, civilian or dockyard factories under owned states.
  - Notes: Must use either > or < operators.
  - Version Added: 1.11

- **num_of_civilian_factories_available_for_projects**
  - Parameters:
    ```text
    <int>
    The amount to check for.
    ```
  - Example:
    ```text
    num_of_civilian_factories_available_for_projects > 10
    ```
  - Description: Checks if the current scope has the specified amount of civilian factories usable for projects.
  - Notes: Must use either > or < operators.
  - Version Added: 1.5

- **ic_ratio**
  - Parameters:
    ```text
    tag = <scope>
    The country to check.
    ratio = <float>
    The ratio to check for.
    ```
  - Example:
    ```text
    ic_ratio = {
        tag = GER
        ratio > 0.5
    }
    ```
  - Description: Checks if the current scope has the specified ratio of factories with the target country.
  - Notes: Must use either > or < operators for ratio.
  - Version Added: 1.0

- **has_damaged_buildings**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    has_damaged_buildings = yes
    ```
  - Description: Checks if the current scope has any damanged buildings in their states.
  - Version Added: 1.0

- **has_built**
  - Parameters:
    ```text
    type = <building>
    The building to check for.
    value = <int>
    The amount to check for.
    ```
  - Example:
    ```text
    has_built = {
        type = arms_factory
        value > 10
    }
    ```
  - Description: Checks if the current scope has built the specified building the specified number of times.
  - Notes: Must use either > or < operators for value.
  - Version Added: 1.0

### Technology

- **has_tech**
  - Parameters:
    ```text
    <string>
    The technology to check for.
    ```
  - Example:
    ```text
    has_tech = my_technology
    ```
  - Description: Checks if the current scope has the specified technology.
  - Version Added: 1.0

- **is_researching_technology**
  - Parameters:
    ```text
    <string>
    The technology to check for.
    ```
  - Example:
    ```text
    is_researching_technology = my_tech
    ```
  - Description: Checks if the current scope is currently researching the specified technology.
  - Version Added: 1.0

- **can_research**
  - Parameters:
    ```text
    <string>
    The technology to check for.
    ```
  - Example:
    ```text
    can_research = my_tech
    ```
  - Description: Checks if the current scope can start researching the specified technology.
  - Version Added: 1.0

- **original_research_slots**
  - Parameters:
    ```text
    <int>
    The amount to check for.
    ```
  - Example:
    ```text
    original_research_slots > 3
    ```
  - Description: Checks if the current scope had the specified amount of slots at game start.
  - Notes: Must use either > or < operators.
  - Version Added: 1.0

- **amount_research_slots**
  - Parameters:
    ```text
    <int>
    The amount to check for.
    ```
  - Example:
    ```text
    amount_research_slots > 3
    ```
  - Description: Checks if the current scope has the specified amount of research slots.
  - Notes: Must use either > or < operators.
  - Version Added: 1.3

- **is_in_tech_sharing_group**
  - Parameters:
    ```text
    <string>
    The group to check for.
    ```
  - Example:
    ```text
    is_in_tech_sharing_group = us_research
    ```
  - Description: Checks if the current scope is in the specified technology sharing group.
  - Version Added: 1.3

- **num_tech_sharing_groups**
  - Parameters:
    ```text
    <int>
    The amount to check for.
    ```
  - Example:
    ```text
    num_tech_sharing_groups > 3
    ```
  - Description: Checks if the current scope is in the specified amount of technology sharing groups.
  - Notes: Must use either > or < operators.
  - Version Added: 1.3

- **has_tech_bonus**
  - Parameters:
    ```text
    technology = <string>
    The technology to check for. Optional.
    category = <string>
    The category to check for. Optional.
    ```
  - Example:
    ```text
    has_tech_bonus = {
        technology = my_tech
    }
    ```
  - Example:
    ```text
    has_tech_bonus = {
        category = my_category
    }
    ```
  - Description: Checks if the current scope has a technology bonus in the specified category, or for the specific technology.
  - Version Added: 1.3

- **land_doctrine_level**
  - Parameters:
    ```text
    <int>
    The amount to check for.
    ```
  - Example:
    ```text
    land_doctrine_level > 2
    ```
  - Description: Checks if the current scope has the specified amount of land doctrine technologies.
  - Notes: Must use either > or < operators.
  - Version Added: 1.0

- **num_researched_technologies**
  - Parameters:
    ```text
    <int>
    The amount to check for.
    ```
  - Example:
    ```text
    num_researched_technologies > 10
    ```
  - Description: Checks how many technologies the target has researched.
  - Notes: Must use either > or < operators.
  - Version Added: 1.3

- **is_special_project_being_researched**
  - Parameters:
    ```text
    sp:<string>
    A special project to check for.
    ```
  - Example:
    ```text
    is_special_project_being_researched = sp:sp_air_radar
    ```
  - Description: Checks if the country in scope is currently researching the special project in input.
  - Version Added: 1.15

- **is_special_project_completed**
  - Parameters:
    ```text
    sp:<string>
    A special project to check for.
    ```
  - Example:
    ```text
    is_special_project_completed = sp:sp_land_flamethrower_tank
    ```
  - Description: Checks if the current scope has the specified special project completed.
  - Version Added: 1.15

### Ideas

- **has_idea**
  - Parameters:
    ```text
    <string>
    The idea to check for.
    ```
  - Example:
    ```text
    has_idea = my_idea
    ```
  - Description: Checks if the current scope has the specified idea.

- **has_idea_with_trait**
  - Parameters:
    ```text
    <string>
    The trait to check for.
    ```
  - Example:
    ```text
    has_idea_with_trait = my_trait
    ```
  - Description: Checks if the current scope has any ideas with the specified trait.
  - Version Added: 1.0

- **has_allowed_idea_with_traits**
  - Parameters:
    ```text
    idea = <string>
    The trait to check for.
    limit = <int>
    The amount to check for.
    characters = <bool>
    If set, will only run this on characters.
    ignore = { <ideas> }
    If set, ignores the ideas inside. Optional.
    ```
  - Example:
    ```text
    has_available_idea_with_traits = {
        idea = my_trait
        limit = 1
        ignore = { generic_head_of_intelligence }
    }
    ```
  - Description: Checks if the current scope has the specified amount of ideas with the specified trait.
  - Notes: ignore = idea_name works for 1 idea.
  - Version Added: 1.9.1

- **has_available_idea_with_traits**
  - Parameters:
    ```text
    idea = <string>
    The trait to check for.
    limit = <int>
    The amount to check for.
    characters = <bool>
    If set, will only run this on characters.
    ignore = { <ideas> }
    If set, ignores the ideas inside. Optional.
    ```
  - Example:
    ```text
    has_available_idea_with_traits = {
        idea = my_trait
        limit = 1
        ignore = { generic_head_of_intelligence }
    }
    ```
  - Description: Checks if the current scope has the specified amount of ideas with the specified trait.
  - Notes: ignore = idea_name works for 1 idea.
  - Version Added: 1.0

- **amount_taken_ideas**
  - Parameters:
    ```text
    amount = <int>
    The amount to check for.
    slots = { <string> }
    The slot type.
    ```
  - Example:
    ```text
    amount_taken_ideas = {
        amount > 3
        slots = {
            political_advisor
        }
    }
    ```
  - Description: Checks if the current scope has the specified amount of ideas of the specified slot type. Excludes spirits, hidden ideas, and laws.
  - Notes:
    ```text
    Slots types are found in
    /Hearts of Iron IV/common/idea_tags/*.txt
    .
    ```
  - Version Added: 1.4

### Diplomacy

- **is_major**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    is_major = yes
    ```
  - Description: Checks if the current scope is considered a Major.
  - Version Added: 1.0

- **is_ally_with**
  - Parameters:
    ```text
    <scope> / <variable>
    The country to check for.
    ```
  - Example:
    ```text
    is_ally_with = GER
    ```
  - Example:
    ```text
    is_ally_with = var:country
    ```
  - Description: Checks if the current scope is an ally (Faction members or subject-master relation).
  - Version Added: 1.0

- **is_spymaster**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    is_spymaster = yes
    ```
  - Description: Checks if the current scope is the spymaster of a faction.
  - Version Added: 1.9

- **has_non_aggression_pact_with**
  - Parameters:
    ```text
    <scope> / <variable>
    The country to check for.
    ```
  - Example:
    ```text
    has_non_aggression_pact_with = GER
    ```
  - Description: Checks if the current scope has a non-aggression pact with the specified country.
  - Version Added: 1.0

- **is_guaranteed_by**
  - Parameters:
    ```text
    <scope> / <variable>
    The country to check for.
    ```
  - Example:
    ```text
    is_guaranteed_by = GER
    ```
  - Description: Checks if the current scope has been guaranteed by the specified country.
  - Version Added: 1.0

- **has_guaranteed**
  - Parameters:
    ```text
    <scope> / <variable>
    The country to check for.
    ```
  - Example:
    ```text
    has_guaranteed = GER
    ```
  - Description: Checks if the current scope has guaranteed the specified country.
  - Version Added: 1.0

- **has_military_access_to**
  - Parameters:
    ```text
    <scope> / <variable>
    The country to check for.
    ```
  - Example:
    ```text
    has_military_access_to = GER
    ```
  - Description: Checks if the current scope has military access to the specified country.
  - Version Added: 1.0

- **gives_military_access_to**
  - Parameters:
    ```text
    <scope> / <variable>
    The country to check for.
    ```
  - Example:
    ```text
    gives_military_access_to = GER
    ```
  - Description: Checks if the current scope gives military to the specified country.
  - Version Added: 1.0

- **is_neighbor_of**
  - Parameters:
    ```text
    <scope> / <variable>
    The country to check for.
    ```
  - Example:
    ```text
    is_neighbor_of = GER
    ```
  - Description: Checks if the current scope is a neighbor of the specified country.
  - Version Added: 1.0

- **is_owner_neighbor_of**
  - Parameters:
    ```text
    <scope> / <variable>
    The country to check for.
    ```
  - Example:
    ```text
    is_owner_neighbor_of = GER
    ```
  - Description: Checks if the current scope is a neighbor of the specified country with their core territory only.
  - Version Added: 1.0

- **is_puppet_of**
  - Parameters:
    ```text
    <scope> / <variable>
    The country to check for.
    ```
  - Example:
    ```text
    is_puppet_of = GER
    ```
  - Description: Checks if the current scope is a puppet of the specified country.
  - Notes:
    ```text
    A "puppet" is an autonomous state that has
    is_puppet = yes
    in its definition within
    /Hearts of Iron IV/common/autonomous_states/
    . For any subject type, see
    is_subject_of
    .
    ```
  - Version Added: 1.0

- **is_subject_of**
  - Parameters:
    ```text
    <scope> / <variable>
    The country to check for.
    ```
  - Example:
    ```text
    is_subject_of = GER
    ```
  - Description: Checks if the current scope is a subject of the specified scope.
  - Version Added: 1.0

- **is_puppet**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    is_puppet = yes
    ```
  - Description: Returns true if the current country is a puppet.
  - Notes:
    ```text
    A "puppet" is an autonomous state that has
    is_puppet = yes
    in its definition within
    /Hearts of Iron IV/common/autonomous_states/
    . For any subject type, see
    is_subject
    .
    ```
  - Version Added: 1.0

- **is_subject**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    is_subject = yes
    ```
  - Description: Checks if the current scope is a subject.
  - Version Added: 1.0

- **has_subject**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    has_subject = GRE
    ```
  - Description: Checks if the country has for subject the given country.
  - Version Added: 1.0

- **num_subjects**
  - Parameters:
    ```text
    <int>
    The amount to check for.
    ```
  - Example:
    ```text
    num_subjects > 3
    ```
  - Description: Checks if the current scope has the specified amount of subjects.
  - Notes: Must use either > or < operators.
  - Version Added: 1.3

- **has_autonomy_state**
  - Parameters:
    ```text
    <string>
    The autonomy state to check for.
    ```
  - Example:
    ```text
    has_autonomy_state = autonomy_dominion
    ```
  - Description: Checks if the current scope is in the specified autonomous state.
  - Version Added: 1.0

- **compare_autonomy_state**
  - Parameters:
    ```text
    <string>
    The autonomy state to check for.
    ```
  - Example:
    ```text
    compare_autonomy_state > autonomy_dominion
    ```
  - Description:
    ```text
    Checks if the current scope's autonomy state
    min_freedom_level
    is less or greater than that of the specified autonomy state. The special value "autonomy_free" compares as greater than any autonomy state. If the current scope is not a subject, it is treated as greater than any autonomy state (including "autonomy_free"). With
    =
    , checks if the current scope is in the specified autonomous state.
    ```
  - Version Added: 1.0

- **compare_autonomy_progress_ratio**
  - Parameters:
    ```text
    <float>
    The amount to check for.
    ```
  - Example:
    ```text
    compare_autonomy_progress_ratio > 0.5
    ```
  - Description: Checks if the current scope autonomy progress is at the specified ratio. If the current scope is not a subject, the ratio is 1.
  - Version Added: 1.3

- **has_opinion_modifier**
  - Parameters:
    ```text
    <string>
    The opinion modifier to check for.
    ```
  - Example:
    ```text
    has_opinion_modifier = my_modifier
    ```
  - Description: Checks if the current scope has the specified opinion modifier.
  - Version Added: 1.0

- **has_opinion**
  - Parameters:
    ```text
    target = <scope>
    The country to check for.
    value = <float>
    The amount to check for.
    ```
  - Example:
    ```text
    has_opinion = {
        target = GER
        value > 50
    }
    ```
  - Description: Checks if the current scope has the specified opinion of the target country.
  - Notes: Must use either > or < operators.
  - Version Added: 1.0

- **has_relation_modifier**
  - Parameters:
    ```text
    target = <scope>
    The country to check for.
    modifier = <modifier>
    The modifier to check for.
    ```
  - Example:
    ```text
    has_relation_modifier = {
        target = GER
        modifier = my_modifier
    }
    ```
  - Description: Checks if the current scope has the specified relation modifier with the specified country.
  - Version Added: 1.0

- **has_legitimacy**
  - Parameters:
    ```text
    <int>
    Amount to check.
    ```
  - Example:
    ```text
    has_legitimacy > 50
    ```
  - Description: Checks how much legitimacy the current government in exile has.
  - Notes: Must use either > or < operators. Legitimacy ranges from 0 to 100.
  - Version Added: 1.6

- **is_exile_host**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    is_exile_host = yes
    ```
  - Description: Checks if the current country is hosting an exile.
  - Version Added: 1.6

- **is_hosting_exile**
  - Parameters:
    ```text
    <tag>
    Country.
    ```
  - Example:
    ```text
    is_hosting_exile = POL
    ```
  - Description: Checks if the current country is hosting a specific exile.
  - Version Added: 1.6

- **is_government_in_exile**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    is_government_in_exile = yes
    ```
  - Description: Checks if the current country is exiled in a different country.
  - Version Added: 1.6

- **is_exiled_in**
  - Parameters:
    ```text
    <tag>
    Country to be exiled in.
    ```
  - Example:
    ```text
    is_exiled_in = POL
    ```
  - Description: Checks if the current country is exiled in a specific country.
  - Version Added: 1.6

- **received_expeditionary_forces**
  - Parameters:
    ```text
    sender = <tag>
    Country which sent forces.
    value <> <int>
    Amount of forces.
    ```
  - Example:
    ```text
    received_expeditionary_forces = {
        sender = POL
        value > 10
    }
    ```
  - Description: Checks if the current country received X units in expeditions from the specified country.
  - Version Added: 1.6

- **can_declare_war_on**
  - Parameters:
    ```text
    <tag>
    Country to check.
    ```
  - Example:
    ```text
    can_declare_war_on = POL
    ```
  - Description: Checks if the current scope is able to declare war on the specified country.
  - Version Added: 1.9

- **foreign_manpower**
  - Parameters:
    ```text
    <int>
    Amount to check.
    ```
  - Example:
    ```text
    foreign_manpower > 10000
    ```
  - Description: Checks how much foreign manpower we have received for garrisoning.
  - Notes: Must use either > or < operators.
  - Version Added: 1.9

- **is_embargoed_by**
  - Parameters:
    ```text
    <scope>
    Amount to check.
    ```
  - Example:
    ```text
    is_embargoed_by = USA
    ```
  - Description: Checks if the current scope is embargoed by the specified country.
  - Version Added: 1.12

- **is_embargoing**
  - Parameters:
    ```text
    <scope>
    Amount to check.
    ```
  - Example:
    ```text
    is_embargoing = CUB
    ```
  - Description: Checks if the current scope is embargoing the specified country.
  - Version Added: 1.12

### Faction

- **is_in_faction**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    is_in_faction = yes
    ```
  - Description: Checks if the current scope is in a faction.
  - Version Added: 1.0

- **is_in_faction_with**
  - Parameters:
    ```text
    <scope> / <variable>
    The country to check for.
    ```
  - Example:
    ```text
    is_in_faction_with = GER
    ```
  - Example:
    ```text
    is_in_faction_with = var:country
    ```
  - Description: Checks if the current scope is in a faction with the specified country.
  - Version Added: 1.0

- **is_faction_leader**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    is_faction_leader = yes
    ```
  - Description: Checks if the current scope is the leader of a faction.
  - Version Added: 1.0

- **num_faction_members**
  - Parameters:
    ```text
    <int> / <variable>
    The amount to check for.
    ```
  - Example:
    ```text
    num_faction_members > 1
    ```
  - Description: Checks if the faction of the current scope has the specified amount of members.
  - Notes: Must use either > or < operators.
  - Version Added: 1.0

- **has_manpower_to_become_leader**
  - Parameters:
    ```text
    <bool>
    Boolean
    ```
  - Example:
    ```text
    has_manpower_to_become_leader = yes
    ```
  - Description: Checks if the current country exceeds the current faction leader and its subjects in deployed manpower.
  - Version Added: 1.17

- **has_industry_to_become_leader**
  - Parameters:
    ```text
    <bool>
    Boolean
    ```
  - Example:
    ```text
    has_industry_to_become_leader = yes
    ```
  - Description: Checks if the current country exceeds the faction leader in number of factories.
  - Version Added: 1.17

- **has_enough_influence_for_leadership**
  - Parameters:
    ```text
    <bool>
    Boolean
    ```
  - Example:
    ```text
    has_enough_influence_for_leadership = yes
    ```
  - Description: Checks if the current country has enough political influence to become faction leader.
  - Version Added: 1.17

- **has_faction_template**
  - Parameters:
    ```text
    <template_id>
    Faction template id.
    ```
  - Example:
    ```text
    has_faction_template = faction_template_chinese_united_front
    ```
  - Description: Checks if the current country is in a faction with a template.
  - Version Added: 1.17

- **has_active_rule**
  - Parameters:
    ```text
    <rule_id>
    Faction rule id.
    ```
  - Example:
    ```text
    has_active_rule = government_in_exile_allowed
    ```
  - Description: Checks if the country's faction has a specific active rule.
  - Version Added: 1.17

- **has_faction_goal**
  - Parameters:
    ```text
    <goal_id>
    Faction goal id.
    ```
  - Example:
    ```text
    has_faction_goal = faction_goal_resource_control
    ```
  - Description: Checks if the country's faction has an active or completed goal.
  - Version Added: 1.17

- **has_completed_faction_goal**
  - Parameters:
    ```text
    <goal_id>
    Faction goal id.
    ```
  - Example:
    ```text
    has_completed_faction_goal = faction_goal_resource_control
    ```
  - Description: Checks if the country's faction has successfully completed a goal.
  - Version Added: 1.17

- **faction_goal_fulfillment**
  - Parameters:
    ```text
    goal = <goal_id>
    Faction goal id.
    value = <float> / <variable>
    The amount to check for.
    ```
  - Example:
    ```text
    faction_goal_fulfillment = {
        goal = faction_goal_resource_control
        value > 0.85
    }
    ```
  - Example:
    ```text
    faction_goal_fulfillment = {
        goal = faction_goal_resource_control
        value > 0.5
        value < 0.85
    }
    ```
  - Description: Checks fulfillment of a faction goal for the current country's faction.
  - Notes: Value supports > and <, can accept variables, can be repeated multiple times.
  - Version Added: 1.17

- **faction_manifest_fulfillment**
  - Parameters:
    ```text
    <float> / <variable>
    The amount to check for.
    ```
  - Example:
    ```text
    faction_manifest_fulfillment > 0.95
    ```
  - Description: Checks manifest fulfillment value of current country's faction manifest.
  - Version Added: 1.17

- **faction_upgrade_level**
  - Parameters:
    ```text
    <upgrade_token>
    Faction upgrade token.
    ```
  - Example:
    ```text
    faction_upgrade_level > upgrade_token
    ```
  - Description: Checks the active faction member upgrade against the specified upgrade.
  - Notes: Works with >, <, =
  - Version Added: 1.17

- **faction_power_projection**
  - Parameters:
    ```text
    <int> / <variable>
    The amount to check for.
    ```
  - Example:
    ```text
    faction_power_projection > 100
    ```
  - Description: Checks power value of current country's faction projection.
  - Version Added: 1.17

- **faction_influence_rank**
  - Parameters:
    ```text
    <int> / <variable>
    The amount to check for.
    ```
  - Example:
    ```text
    faction_influence_rank < 5
    ```
  - Description: Checks influence rank in the faction of the current country.
  - Version Added: 1.17

- **faction_influence_ratio**
  - Parameters:
    ```text
    <float> / <variable>
    The amount to check for.
    ```
  - Example:
    ```text
    faction_influence_ratio > 0.1
    ```
  - Description: Checks influence ratio of current country in the faction.
  - Version Added: 1.17

- **faction_influence_score**
  - Parameters:
    ```text
    <int> / <variable>
    The amount to check for.
    ```
  - Example:
    ```text
    faction_influence_score > 100
    ```
  - Description: Checks influence value of current country in the faction.
  - Version Added: 1.17

- **can_assign_supportive_scientist_to_faction**
  - Parameters:
    ```text
    <specialization>
    Specialization.
    ```
  - Example:
    ```text
    can_assign_supportive_scientist_to_faction = specialization_land
    ```
  - Description: Checks if the faction from the country in scope has a free slot for a supportive scientist for the country with the specialization type.
  - Version Added: 1.17

- **has_faction_research_unlocked**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    has_faction_research_unlocked = yes
    ```
  - Description: Whether the faction has unlocked the research.
  - Version Added: 1.17

- **has_faction_military_unlocked**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    has_faction_military_unlocked = yes
    ```
  - Description: Whether the faction has unlocked the military operations.
  - Version Added: 1.17

- **compare_ideology_with_faction**
  - Parameters:
    ```text
    value = <float> / <variable>
    The amount to check for.
    leader = <tag>
    Country to check.
    ```
  - Example:
    ```text
    compare_ideology_with_faction = {
        value > 0.5
        leader = FROM
    }
    ```
  - Description: Compares the ideology support of the country's ruling party for the ideology of the faction it wants to join.
  - Notes: Tooltip is visible only if 'leader' is in faction.
  - Version Added: 1.17

### War

- **has_war**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    has_war = yes
    ```
  - Description: Checks if the current scope is at war.
  - Version Added: 1.0

- **has_war_with**
  - Parameters:
    ```text
    <scope> / <variable>
    The country to check for.
    ```
  - Example:
    ```text
    has_war_with = GER
    ```
  - Example:
    ```text
    has_war_with = var:country
    ```
  - Description: Checks if the current scope is at war with the specified country.
  - Version Added: 1.0

- **has_offensive_war_with**
  - Parameters:
    ```text
    <scope> / <variable>
    The country to check for.
    ```
  - Example:
    ```text
    has_offensive_war_with = GER
    ```
  - Description: Checks if the current scope is in an offensive war against the specified country.
  - Version Added: 1.0

- **has_offensive_war_without_friend**
  - Parameters:
    ```text
    <scope> / <variable>
    The country to check for.
    ```
  - Example:
    ```text
    has_offensive_war_without_friend = GER
    ```
  - Description: Is country at offensive war without specific ally present.
  - Version Added: 1.17

- **has_defensive_war_with**
  - Parameters:
    ```text
    <scope> / <variable>
    The country to check for.
    ```
  - Example:
    ```text
    has_defensive_war_with = GER
    ```
  - Description: Checks if the current scope is in an defensive war against the specified country.
  - Version Added: 1.0

- **has_offensive_war**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    has_offensive_war = yes
    ```
  - Description: Checks if the current scope is in an offensive war.
  - Version Added: 1.0

- **has_defensive_war**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    has_defensive_war = yes
    ```
  - Description: Checks if the current scope is in a defensive war.
  - Version Added: 1.0

- **has_war_together_with**
  - Parameters:
    ```text
    <scope> / <variable>
    The country to check for.
    ```
  - Example:
    ```text
    has_war_together_with = GER
    ```
  - Description: Checks if the current scope is in a war alongside the specified country.
  - Version Added: 1.0

- **has_war_with_major**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    has_war_with_major = yes
    ```
  - Description: Checks if the current scope is at war with any other country that is considered major.
  - Version Added: 1.12

- **has_war_with_wargoal_against**
  - Parameters:
    ```text
    target = <scope> / <variable>
    The country to check for.
    type = <wargoal>
    The wargoal to check for. Optional.
    ```
  - Example:
    ```text
    has_war_with_wargoal_against = {
        target = ENG
        type = independence_wargoal
    }
    ```
  - Description: Checks if the current scope is at war with the specified country with the specified wargoal being active.
  - Notes:
    ```text
    Wargoals are stored within
    /Hearts of Iron IV/common/wargoals/*.txt
    files. If no wargoal is specified, checks for
    any
    wargoal. Joining an ally in their war does not count as a wargoal.
    ```
  - Version Added: 1.12

- **surrender_progress**
  - Parameters:
    ```text
    <float> / <variable>
    The amount to check for.
    ```
  - Example:
    ```text
    surrender_progress > 0.1
    ```
  - Description: Checks if the current scope has the specified amount of surrender progress.
  - Notes: Must use either > or < operators.
  - Version Added: 1.0

- **any_war_score**
  - Parameters:
    ```text
    <float>
    The amount to check for.
    ```
  - Example:
    ```text
    any_war_score > 10
    ```
  - Description:
    ```text
    Checks if the current scope has the specified amount of
    war progress
    (not war participation)
    in any war.
    ```
  - Notes: Must use either > or < operators.
  - Version Added: 1.0

- **has_capitulated**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    has_capitulated = yes
    ```
  - Description: Checks if the current scope has capitulated.
  - Version Added: 1.0

- **days_since_capitulated**
  - Parameters:
    ```text
    <int>
    Amount of days.
    ```
  - Example:
    ```text
    days_since_capitulated > 10
    ```
  - Description: Checks the amount of days since the target last capitulated.
  - Notes: If the target never capitulated, the amount of days is extremely large.  Recommended to combine with has_capitulated.
  - Version Added: 1.9

- **has_border_war_with**
  - Parameters:
    ```text
    <scope> / <variable>
    The country to check for.
    ```
  - Example:
    ```text
    has_border_war_with = GER
    ```
  - Description: Checks if the current scope has a border war with the specified country.
  - Version Added: 1.5

- **has_border_war_between**
  - Parameters:
    ```text
    attacker = <scope> / <variable>
    The state to check for.
    defender = <scope> / <variable>
    The state to check for.
    ```
  - Example:
    ```text
    has_border_war_between = {
        attacker = 1
        defender = 2
    }
    ```
  - Description: Checks if there is a border war between the two specified states.
  - Version Added: 1.5

- **has_border_war**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    has_border_war = yes
    ```
  - Description: Checks if the current scope has a border war active.
  - Version Added: 1.5

- **has_added_tension_amount**
  - Parameters:
    ```text
    <float> / <variable>
    The amount to check for.
    ```
  - Example:
    ```text
    has_added_tension_amount > 10
    ```
  - Description: Checks if the current scope has caused the specified amount of World Tension.
  - Notes: Must use either > or < operators.
  - Version Added: 1.0

- **has_wargoal_against**
  - Parameters:
    ```text
    <scope> / <variable>
    The country to check for.
    ```
  - Example:
    ```text
    has_wargoal_against = GER
    ```
  - Description: Checks if the current scope has any wargoal against the specified country.
  - Version Added: 1.0

- **has_wargoal_against**
  - Parameters:
    ```text
    target = <scope> / <variable>
    The country to check for.
    type = <string>
    The type of wargoal to check for.
    ```
  - Example:
    ```text
    has_wargoal_against = {
        target = FROM
        type = take_state
    }
    ```
  - Description: Checks if the current scope has a specific wargoal type against the specified country.
  - Version Added: 1.8

- **is_justifying_wargoal_against**
  - Parameters:
    ```text
    <scope> / <variable>
    The country to check for.
    ```
  - Example:
    ```text
    is_justifying_wargoal_against = GER
    ```
  - Description: Checks if the current scope is justifying a wargoal against the specified country.
  - Version Added: 1.0

- **has_annex_war_goal**
  - Parameters:
    ```text
    <scope> / <variable>
    The country to check for.
    ```
  - Example:
    ```text
    has_annex_war_goal = GER
    ```
  - Description: Checks if the current scope has the Annex wargoal against the specified country.
  - Version Added: 1.0

- **any_claim**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    any_claim = yes
    ```
  - Description: Checks if the current scope has any claims on another country.
  - Version Added: 1.0

- **is_in_peace_conference**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    is_in_peace_conference = yes
    ```
  - Description: Checks if the current scope is in a peace conference.
  - Notes: Please test this in-game for 1.12.
  - Version Added: 1.0

- **controls_province**
  - Parameters:
    ```text
    <id>
    The province to check for.
    ```
  - Example:
    ```text
    controls_province = 1239
    ```
  - Description: Checks if the current scope has control of the specified province.
  - Version Added: 1.9

- **longest_war_length**
  - Parameters:
    ```text
    <int>
    Amount of months.
    ```
  - Example:
    ```text
    longest_war_length > 3
    ```
  - Description: Checks how long a country has been at war, in months.
  - Version Added: 1.14

- **war_length_with**
  - Parameters:
    ```text
    tag = <scope> / <variable>
    Target country.
    months = <int>
    Amounth of months.
    ```
  - Example:
    ```text
    war_length_with = {
        tag = GER
        months > 3
    }
    ```
  - Description: Checks how long a country has been at war with specific country, in months.
  - Version Added: 1.14

- **has_truce_with**
  - Parameters:
    ```text
    <scope> / <variable>
    The country to check for.
    ```
  - Example:
    ```text
    has_truce_with = GER
    ```
  - Description: Checks if the country has truce with the specified country.
  - Version Added: 1.16

- **has_naval_control**
  - Parameters:
    ```text
    <id> / <variable>
    The region to check in.
    ```
  - Example:
    ```text
    has_naval_control = 16
    ```
  - Description: Checks if friendly nations and country scope together has enough naval dominance to assert control in strategic region.
  - Version Added: 1.17

- **has_enemy_naval_control**
  - Parameters:
    ```text
    <id> / <variable>
    The region to check in.
    ```
  - Example:
    ```text
    has_enemy_naval_control = 16
    ```
  - Description: Checks if any enemy has enough naval dominance to assert control in certain strategic region.
  - Version Added: 1.17

### State

These are state-related triggers in the country scope, not [state-scoped triggers](#state-scope).

- **controls_state**
  - Parameters:
    ```text
    <scope> / <variable>
    The state to check for.
    ```
  - Example:
    ```text
    controls_state = 39
    ```
  - Example:
    ```text
    controls_state = var:state
    ```
  - Description: Checks if the current scope has control of the specified state.
  - Version Added: 1.0

- **owns_state**
  - Parameters:
    ```text
    <scope> / <variable>
    The state to check for.
    ```
  - Example:
    ```text
    owns_state = 39
    ```
  - Description: Checks if the current scope owns the specified state.
  - Version Added: 1.0

- **num_of_controlled_states**
  - Parameters:
    ```text
    <int>
    The amount to check for.
    ```
  - Example:
    ```text
    num_of_controlled_states > 5
    ```
  - Description: Checks if the current scope has the specified amount of controlled states.
  - Notes: Must use either > or < operators.
  - Version Added: 1.0

- **num_occupied_states**
  - Parameters:
    ```text
    <int>
    The amount to check for.
    ```
  - Example:
    ```text
    num_occupied_states > 5
    ```
  - Description: Checks if the current scope has the specified amount of occupied states.
  - Notes: Must use either > or < operators.
  - Version Added: 1.0

- **has_full_control_of_state**
  - Parameters:
    ```text
    <scope> / <variable>
    The state to check for.
    ```
  - Example:
    ```text
    has_full_control_of_state = 39
    ```
  - Description: Checks if the current scope has total control (100% occupation) of the specified state.
  - Version Added: 1.3

- **has_resources_rights**
  - Parameters:
    ```text
    state = <scope> / <variable>
    The state to check in. Mandatory if used in country scope.
    resources = { <resource> <...> <resource> }
    Resources to check for. Optional, defaults to any if unset.
    ```
  - Example:
    ```text
    has_resources_rights = {
      state = 123
      resources = { oil steel }
    }
    ```
  - Description: Checks if there are any resource rights with the specified parameters.
  - Notes:
    ```text
    Can be used in either state or country scope. Always returns false if the state has no resources.
    Can also be used in state scope.
    ```
  - Version Added: 1.12

- **core_compliance**
  - Parameters:
    ```text
    occupied_country_tag = <TAG>
    The country for which to check compliance.
    value = <int>
    The value to check for.
    ```
  - Example:
    ```text
    core_compliance = {
        occupied_country_tag = ITA
        value > 10
    }
    ```
  - Description: Compares the average compliance of core states of the specified country within controlled states of the current scope.
  - Notes: Must use either > or < operators for value.
  - Version Added: 1.9

- **core_resistance**
  - Parameters:
    ```text
    occupied_country_tag = <TAG>
    The country for which to check resistance.
    value = <int>
    The value to check for.
    ```
  - Example:
    ```text
    core_resistance = {
        occupied_country_tag = ITA
        value > 10
    }
    ```
  - Description: Compares the average resistance of core states of the specified country within controlled states of the current scope.
  - Notes: Must use either > or < operators for value.
  - Version Added: 1.9

- **garrison_manpower_need**
  - Parameters:
    ```text
    <int>
    Amount to check.
    ```
  - Example:
    ```text
    garrison_manpower_need > 10000
    ```
  - Description: Checks how much garrison manpower we need for resistance in controlled states.
  - Notes: Must use either > or < operators.
  - Version Added: 1.9

- **has_core_occupation_modifier**
  - Parameters:
    ```text
    occupied_country_tag = <scope> / <variable>
    The country to check.
    modifier = <token>
    The modifier to check.
    ```
  - Example:
    ```text
    has_core_occupation_modifier = {
      occupied_country_tag = ITA
      modifier = token
    }
    ```
  - Description: Checks if the current scope has an occupation modifier for resistance/compliance that applies to our occupied states of a specified country.
  - Version Added: 1.9

- **occupation_law**
  - Parameters:
    ```text
    <law ID>
    The law to check.
    ```
  - Examples:
    ```text
    # Checks POL's default occupation law
    # Checks HOL's occupation law over BEL
    ```
  - Example:
    ```text
    POL = {
      POL = {
        occupation_law = foreign_civilian_oversight
      }
    }
    ```
  - Example:
    ```text
    HOL = {
      BEL = {
        occupation_law = foreign_civilian_oversight
      }
    }
    ```
  - Description: Checks the occupation law that's either the default or applied over a specific country.
  - Notes:
    ```text
    Checks
    PREV's
    occupation law over the current country. If they're the same scope, checks the default occupation law.
    Can also be used in state scope.
    ```
  - Version Added: 1.12

- **has_contested_owner**
  - Parameters:
    ```text
    <state> / <variable>
    State to check.
    ```
  - Example:
    ```text
    has_contested_owner = 42
    ```
  - Description: Checks if a state has the specified country as a contested owner. The trigger can be used either from a country or a state scope and accepts the other as parameter.
  - Notes: Can also be used in state scope.
  - Version Added: 1.15

- **owns_any_state_of**
  - Parameters:
    ```text
    <states>
    States to check.
    ```
  - Example:
    ```text
    owns_any_state_of = {
      123
      246
    }
    ```
  - Description: Check if the country owns any of the states in the list.
  - Notes: The same as:
  - Example:
    ```text
    OR = {
      owns_state = 123
      owns_state = 246
    }
    ```
  - Version Added: 1.16

- **is_on_same_continent_as**
  - Parameters:
    ```text
    <scope> / <variable>
    The state to check for.
    ```
  - Example:
    ```text
    is_on_same_continent_as = 111
    ```
  - Description: Checks if the scope country is on the same continent as the given state. The capital state is used for given country tag.
  - Notes: Can also be used in state scope.
  - Version Added: 1.17

### Military

- **has_army_experience**
  - Parameters:
    ```text
    <float> / <variable>
    The amount to check for.
    ```
  - Example:
    ```text
    has_army_experience > 10
    ```
  - Example:
    ```text
    has_army_experience > var:number
    ```
  - Description: Checks if the current scope has the specified amount of Army experience.
  - Notes:
    ```text
    Must
    use either > or < operators as = operator checks for the
    exact
    value
    ```
  - Version Added: 1.3

- **has_air_experience**
  - Parameters:
    ```text
    <float> / <variable>
    The amount to check for.
    ```
  - Example:
    ```text
    has_air_experience > 10
    ```
  - Description: Checks if the current scope has the specified amount of Air experience.
  - Notes:
    ```text
    Must
    use either > or < operators as = operator checks for the
    exact
    value
    ```
  - Version Added: 1.3

- **has_navy_experience**
  - Parameters:
    ```text
    <float> / <variable>
    The amount to check for.
    ```
  - Example:
    ```text
    has_navy_experience < 10
    ```
  - Description: Checks if the current scope has the specified amount of Navy experience.
  - Notes:
    ```text
    Must
    use either > or < operators as = operator checks for the
    exact
    value
    ```
  - Version Added: 1.3

- **has_manpower**
  - Parameters:
    ```text
    <float> / <variable>
    The amount to check for.
    ```
  - Example:
    ```text
    has_manpower > 1000
    ```
  - Description: Checks if the current scope has the specified amount of manpower.
  - Notes:
    ```text
    Must
    use either > or < operators as = operator checks for the
    exact
    value
    ```
  - Version Added: 1.0

- **has_army_manpower**
  - Parameters:
    ```text
    size = <int>
    The amount to check for.
    ```
  - Example:
    ```text
    has_army_manpower = {
        size > 1000
    }
    ```
  - Description: Checks if the current scope has an army using the specified amount of manpower.
  - Notes: Must use either > or < operators.
  - Version Added: 1.0

- **manpower_per_military_factory**
  - Parameters:
    ```text
    <float>
    The amount to check for.
    ```
  - Example:
    ```text
    manpower_per_military_factory > 1000
    ```
  - Description: Checks if the current scope has the specified manpower times their number of military factories.
  - Notes: Must use either > or < operators.
  - Version Added: 1.0

- **conscription_ratio**
  - Parameters:
    ```text
    <float> / <variable>
    The ratio to compare with.
    ```
  - Example:
    ```text
    conscription_ratio < 0.2
    ```
  - Description: Checks if the current scope has the specified conscription ratio currently, not to be mixed up with the target conscription ratio.
  - Notes:
    ```text
    Must
    use either > or < operators as = operator checks for the
    exact
    value
    ```
  - Version Added: 1.9

- **current_conscription_amount**
  - Parameters:
    ```text
    <float> / <variable>
    The amount to compare with.
    ```
  - Example:
    ```text
    current_conscription_amount > 2000
    ```
  - Description: Checks if the current scope has already conscripted that much manpower.
  - Notes:
    ```text
    Must
    use either > or < operators as = operator checks for the
    exact
    value
    ```
  - Version Added: 1.9

- **target_conscription_amount**
  - Parameters:
    ```text
    <float> / <variable>
    The amount to compare with.
    ```
  - Example:
    ```text
    target_conscription_amount > 2000
    ```
  - Description: Checks if the current scope is targeting to conscript that much manpower.
  - Notes:
    ```text
    Must
    use either > or < operators as = operator checks for the
    exact
    value
    ```
  - Version Added: 1.9

- **num_divisions**
  - Parameters:
    ```text
    <int>
    The amount to check for.
    ```
  - Example:
    ```text
    num_divisions > 5
    ```
  - Description: Checks if the current scope has the specified amount of divisions.
  - Notes: Must use either > or < operators.
  - Version Added: 1.3

- **num_of_nukes**
  - Parameters:
    ```text
    <int>
    The amount to check for.
    ```
  - Example:
    ```text
    num_of_nukes > 5
    ```
  - Description: Checks if the current scope has the specified amount of nukes.
  - Notes: Must use either > or < operators.
  - Version Added: 1.0

- **casualties**
  - Parameters:
    ```text
    <int>
    The amount to check for.
    ```
  - Example:
    ```text
    casualties > 10000
    ```
  - Description: Checks if the current scope has suffered the specified amount of casualties.
  - Notes: Must use either > or < operators.
  - Version Added: 1.0

- **casualties_k**
  - Parameters:
    ```text
    <int>
    The amount to check for.
    ```
  - Example:
    ```text
    casualties_k > 10
    ```
  - Description: Checks if the current scope has suffered the specified amount of casualties in thousands.
  - Notes: Must use either > or < operators.
  - Version Added: 1.0

- **casualties_inflicted_by**
  - Parameters:
    ```text
    opponent = <tag>
    The tag that inflicted the casualties.
    thousands <> <int>
    The amount of casualties in thousands.
    ```
  - Example:
    ```text
    casualties_inflicted_by = {
        opponent = POL
        thousands > 10
    }
    ```
  - Description: Checks if the current scope has suffered the specified amount of casualties in thousands from a specific country.
  - Notes: Must use either > or < operators for thousands.
  - Version Added: 1.6

- **amount_manpower_in_deployment_queue**
  - Parameters:
    ```text
    <float>
    The amount to check for.
    ```
  - Example:
    ```text
    amount_manpower_in_deployment_queue > 1000
    ```
  - Description: Checks if the current scope has the specified amount of manpower in their deployment queue.
  - Notes: Must use either > or < operators.
  - Version Added: 1.5

- **has_attache_from**
  - Parameters:
    ```text
    <scope> / <variable>
    The country to check for.
    ```
  - Example:
    ```text
    has_attache_from = GER
    ```
  - Description: Checks if the current scope has an attache from the specified scope.
  - Version Added: 1.5

- **has_attache**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    has_attache = yes
    ```
  - Description: Checks if the current scope has an attache.
  - Version Added: 1.5

- **is_lend_leasing**
  - Parameters:
    ```text
    <scope> / <variable>
    The country to check for.
    ```
  - Example:
    ```text
    is_lend_leasing = GER
    ```
  - Description: Checks if the current scope is lend leasing to the specified scope.
  - Version Added: 1.0

- **has_template**
  - Parameters:
    ```text
    <string>
    The name of the template.
    ```
  - Example:
    ```text
    has_template = "Infantry Division"
    ```
  - Description: Checks if the current scope has a division template of the specified name.
  - Version Added: 1.0

- **has_template_majority_unit**
  - Parameters:
    ```text
    <string>
    The unit to check for.
    ```
  - Example:
    ```text
    has_template_majority_unit = infantry
    ```
  - Description: Checks if the current scope has a division template composed mostly of the specified unit.
  - Version Added: 1.0

- **has_template_containing_unit**
  - Parameters:
    ```text
    <string>
    The name of the unit.
    ```
  - Example:
    ```text
    has_template_containing_unit = light_armor
    ```
  - Description: Checks if the current scope has a division template contained any of the specified unit.
  - Version Added: 1.0

- **strength_ratio**
  - Parameters:
    ```text
    tag = <scope>
    The country to check for.
    ratio <> <float>
    The ratio to check for.
    ```
  - Example:
    ```text
    strength_ratio = {
        tag = GER
        ratio > 1
    }
    ```
  - Description:
    ```text
    Checks if the current scope has the specified strength ratio against the specified country. The ratio is the number of fielded divisions of the current scope divided by those of
    tag
    (or 1 if
    tag
    has no divisions). The ratio gets increased by 10% if the current scope has a stronger air forces.
    ```
  - Notes: Must use > or < in the ratio.
  - Version Added: 1.0

- **fighting_army_strength_ratio**
  - Parameters:
    ```text
    tag = <scope>
    The country to check for.
    ratio <>= <float> / <variable>
    The ratio to check for.
    ```
  - Example:
    ```text
    fighting_army_strength_ratio = {
        tag = GER
        ratio > 0.7
    }
    ```
  - Description: Compares the total army fighting strength between the scope country and the one set with 'tag'.
  - Notes: Ratio can be '<','>' or '='.
  - Version Added: 1.15

- **naval_strength_ratio**
  - Parameters:
    ```text
    tag = <scope>
    The country to check for.
    ratio <> <float>
    The ratio to check for.
    ```
  - Example:
    ```text
    naval_strength_ratio = {
        tag = GER
        ratio <> 1
    }
    ```
  - Description: Checks if the current scope has the specified naval strength ratio against the specified country.
  - Notes: Must use > or < in the ratio.
  - Version Added: 1.0

- **naval_strength_comparison**
  - Parameters:
    ```text
    other = <scope>
    The country to check for.
    tooltip = <string>
    The ratio to check for. Optional.
    ratio <> <float>
    The ratio to check for.
    sub_unit_def_weights = { ... }
    The weight to assign to each unit. Optional.
    ```
  - Example:
    ```text
    naval_strength_comparison = {
        other = POL
        tooltip = my_loc_key_tt
        ratio > 1
        sub_unit_def_weights = {
            carrier = 1
            submarine = 2
        }
    }
    ```
  - Description: Checks if the current scope has the specified naval strength ratio against the specified country.
  - Notes:
    ```text
    Must use > or < in the ratio. If sub_unit_def_weights is unset, each unit is assumed to have 1 weight. If sub_unit_def_weights is set, only specified units will be counted towards strength. Units are defined in
    /Hearts of Iron IV/common/units/*.txt
    .
    ```
  - Version Added: 1.6

- **alliance_strength_ratio**
  - Parameters:
    ```text
    <float> / <variable>
    The ratio to check for.
    ```
  - Example:
    ```text
    alliance_strength_ratio > 0.5
    ```
  - Description: Checks if the current scope and allies has an army strength higher than the specified ratio against estimated enemy strength.
  - Notes: Must use either > or < operators.
  - Version Added: 1.0

- **alliance_naval_strength_ratio**
  - Parameters:
    ```text
    <float> / <variable>
    The ratio to check for.
    ```
  - Example:
    ```text
    alliance_naval_strength_ratio > 0.5
    ```
  - Description: Checks if the current scope and allies has an naval strength ratio higher than the specified ratio against estimated enemy strength.
  - Notes: Must use either > or < operators.
  - Version Added: 1.0

- **enemies_strength_ratio**
  - Parameters:
    ```text
    <float> / <variable>
    The ratio to check for.
    ```
  - Example:
    ```text
    enemies_strength_ratio > 0.5
    ```
  - Description: Checks if the estimated enemy army strength ratio is higher than the specified ratio.
  - Notes: Must use either > or < operators.
  - Version Added: 1.0

- **enemies_naval_strength_ratio**
  - Parameters:
    ```text
    <float> / <variable>
    The ratio to check for.
    ```
  - Example:
    ```text
    enemies_naval_strength_ratio > 0.5
    ```
  - Description: Checks if the estimated enemy naval strength ratio is higher than the specified ratio.
  - Notes: Must use either > or < operators.
  - Version Added: 1.0

- **has_army_size**
  - Parameters:
    ```text
    size = <float>
    The amount to check for.
    type = <string>
    The battalion type to check for. Divisions that are majority made up of battalions in that type count. Optional, counts all divisions by default.
    ```
  - Example:
    ```text
    has_army_size = {
        size > 10
        type = armor
    }
    ```
  - Description: Checks if the current scope has the specified number of divisions, or of a specified type of division.
  - Notes:
    ```text
    Battalion types are defined within
    /Hearts of Iron IV/common/units/*.txt
    files. Must use either > or < operators for size.
    ```
  - Version Added: 1.0

- **has_navy_size**
  - Parameters:
    ```text
    size = <float> / <variable>
    The amount to check for.
    type = <string>
    The type to check for. Optional.
    archetype = <string>
    The ship archetype to check for. Optional.
    ```
  - Example:
    ```text
    has_navy_size = {
        size > 10
        type = capital_ship
        archetype = ship_hull_heavy
    }
    ```
  - Description: Checks if the current scope has the specified number of ships, or of a specified type of ship.
  - Notes:
    ```text
    Ship types are defined within
    /Hearts of Iron IV/common/units/*.txt
    files. Must use either > or < operators for size. Ship archetypes are found in
    /Hearts of Iron IV/common/units/equipment/*.txt
    files.
    ```
  - Version Added: 1.0

- **has_deployed_air_force_size**
  - Parameters:
    ```text
    size = <float>
    The amount to check for.
    type = <string>
    The type to check for. Optional.
    ```
  - Example:
    ```text
    has_deployed_air_force_size = {
        size > 10
        type = cas
    }
    ```
  - Description: Checks if the current scope has the specified number of aircraft, or of a specified type of aircraft.
  - Notes:
    ```text
    Airwing types are defined within
    /Hearts of Iron IV/common/units/*.txt
    files. Must use either > or < operators for size.
    ```
  - Version Added: 1.0

- **divisions_in_state**
  - Parameters:
    ```text
    size = <float>
    The amount to check for.
    type = <string>
    The battalion type to check for. Divisions that are majority made up of battalions in that type count. Optional, counts all divisions by default.
    unit = <string>
    The exact battalion to check for. Divisions that are majority made up of that battalions count. Optional, counts all divisions by default.
    state = <scope> / <variable>
    The state to check in.
    ```
  - Example:
    ```text
    divisions_in_state = {
        type = armor
        size > 10
        state = 49
    }
    ```
  - Description: Checks if the specified state contains the specified amount of divisions.
  - Notes:
    ```text
    Battalions and their types are defined within
    /Hearts of Iron IV/common/units/*.txt
    files. Must use either > or < operators for size.
    ```
  - Version Added: 1.0

- **army_manpower_in_state**
  - Parameters:
    ```text
    amount <> <float>
    The amount to check for.
    type = <string>
    The type to check for. Optional.
    state = <scope> / <variable>
    The state to check in.
    ```
  - Example:
    ```text
    army_manpower_in_state = {
        type = support
        amount > 10000
        state = 49
    }
    ```
  - Description: Checks if the specified state contains the specified amount of army manpower within the state.
  - Notes:
    ```text
    Battalion types are defined within
    /Hearts of Iron IV/common/units/*.txt
    files. Must use either > or < operators for size.
    ```
  - Version Added: 1.6

- **divisions_in_border_state**
  - Parameters:
    ```text
    size = <float>
    The amount to check for.
    type = <string>
    The battalion type to check for. Divisions that are majority made up of battalions in that type count. Optional, counts all divisions by default.
    state = <scope> / <variable>
    The state to check in.
    border_state = <scope> / <variable>
    The border state to check in.
    ```
  - Example:
    ```text
    divisions_in_border_state = {
        type = infantry
        size > 10
        state = 49
        border_state = var:state
    }
    ```
  - Description: Checks if the border provinces between the specified state and border state contain the specified amount of divisions.
  - Notes:
    ```text
    Battalion types are defined within
    /Hearts of Iron IV/common/units/*.txt
    files. Must use either > or < operators for size.
    ```
  - Version Added: 1.5

- **num_divisions_in_states**
  - Parameters:
    ```text
    count = <int>
    The amount to check for.
    states = { <int> <...> <int> }
    The states to check in.
    types = { <string> <...> <string> }
    The battalion types to check for. Divisions that are majority made up of battalions in that type count. Optional, counts all divisions by default.
    exclude = { <string> <...> <string> }
    The sub-units to exclude from the search. Divisions that are majority made up of specified battalions are excluded. Optional, excludes no divisions by default.
    ```
  - Example:
    ```text
    num_divisions_in_states = {
        count > 24
        states = { 550 559 271 }
        exclude = { irregular_infantry }
    }
    ```
  - Description: Checks if the specified states contain enough divisions of the specified types.
  - Notes:
    ```text
    Divisions and their types are defined within
    /Hearts of Iron IV/common/units/*.txt
    files. Can use either =, >, or < operators for count. The tooltip does not specify the states the check runs for nor the filtered types.
    ```
  - Version Added: 1.12

- **num_battalions_in_states**
  - Parameters:
    ```text
    count = <int>
    The amount to check for.
    states = { <int> <...> <int> }
    The states to check in.
    types = { <string> <...> <string> }
    The battalion types to check for.
    exclude = { <string> <...> <string> }
    The sub-units to exclude from the search.
    ```
  - Example:
    ```text
    num_battalions_in_states = {
        count > 24
        states = { 550 559 271 }
        exclude = { irregular_infantry }
    }
    ```
  - Description: Checks if the specified states contain enough battalions (or sub-units) of the specified types.
  - Notes:
    ```text
    Battalions and their types are defined within
    /Hearts of Iron IV/common/units/*.txt
    files. Can use either =, >, or < operators for count. The tooltip does not specify the states the check runs for nor the filtered types.
    ```
  - Version Added: 1.12

- **ships_in_state_ports**
  - Parameters:
    ```text
    size = <float>
    The amount to check for.
    type = <string>
    The type to check for. Optional.
    state = <scope> / <variable>
    The state to check in.
    ```
  - Example:
    ```text
    ships_in_state_ports = {
        type = capital_ship
        size > 10
        state = 49
    }
    ```
  - Description: Checks if the specified state contains the specified amount of ships, or of ships of the specified type.
  - Notes:
    ```text
    Ship types are defined within
    /Hearts of Iron IV/common/units/*.txt
    files. Must use either > or < operators for size.
    ```
  - Version Added: 1.0

- **num_planes_stationed_in_regions**
  - Parameters:
    ```text
    value = <float>
    The amount to check for.
    regions = { <id> <...> <id> }
    The regions to check in.
    ```
  - Example:
    ```text
    num_planes_stationed_in_regions = {
        value > 10
        regions = { 123 321 }
    }
    ```
  - Description: Checks if the current scope has the specified number of aircraft stationed within strategic regions.
  - Notes: Must use either =, >, or < operators for value.
  - Version Added: 1.12

- **has_volunteers_amount_from**
  - Parameters:
    ```text
    tag = <scope>
    The country to check for.
    count = <int>
    The amount to check for.
    ```
  - Example:
    ```text
    has_volunteers_amount_from = {
        tag = GER
        count > 10
    }
    ```
  - Description: Checks if the current scope has recieved volunteers from the specified country of the specified amounts.
  - Notes: Must use either > or < operators for count.
  - Version Added: 1.0

- **convoy_threat**
  - Parameters:
    ```text
    <float>
    The threat to compate with.
    ```
  - Example:
    ```text
    convoy_threat > 0.5
    ```
  - Description: Checks how much the convoys are threatened.
  - Notes: Must use either > or < operators for count. Threat is always between 0 and 1.
  - Version Added: 1.6

- **has_mined**
  - Parameters:
    ```text
    target = <tag>
    The country the coast of which is mined.
    value <> <int>
    The amount of mines to compare with.
    ```
  - Example:
    ```text
    has_mined = {
        target = POL
        value > 1000
    }
    ```
  - Description: Checks if the current scope has X mines on the coast of the specified country.
  - Notes: Must use either > or < operators for value.
  - Version Added: 1.6

- **has_mines**
  - Parameters:
    ```text
    region = <ID>
    The strategic region that contains the mines.
    amount = <int>
    The amount of mines to compare with.
    ```
  - Example:
    ```text
    has_mined = {
        target = POL
        amount = 1000
    }
    ```
  - Description: Checks if the current scope has at least X mines within the specified strategic region.
  - Version Added: 1.6

- **mine_threat**
  - Parameters:
    ```text
    <float>
    The threat to compate with.
    ```
  - Example:
    ```text
    mine_threat < 0.6
    ```
  - Description: Checks how dangerous enemy mines are.
  - Notes: Must use either > or < operators for count. Threat is always between 0 and 1.
  - Version Added: 1.6

- **has_military_industrial_organization**
  - Parameters:
    ```text
    <token>
    The id to check for.
    ```
  - Example:
    ```text
    has_military_industrial_organization = infantry_mio_token
    ```
  - Description: Checks if the current scope has a MIO with the specified name.
  - Notes: Accepts variables.
  - Version Added: 1.13

- **has_tactic**
  - Parameters:
    ```text
    <tactic>
    The tactic to check for.
    ```
  - Example:
    ```text
    has_tactic = tactic_masterful_blitz
    ```
  - Description: Check if the given tactic is unlocked (or active by default) for the country.
  - Version Added: 1.17

### Doctrine

- **has_any_grand_doctrine**
  - Parameters:
    ```text
    <string>
    Doctrine folder.
    ```
  - Example:
    ```text
    has_any_grand_doctrine = land
    ```
  - Description: Checks if any grand doctrine in folder is currently active for the country.
  - Notes: Folders are land, naval and air.
  - Version Added: 1.17.2

- **has_doctrine**
  - Parameters:
    ```text
    <grand doctrine> / <subdoctrine>
    The doctrine to check for.
    ```
  - Example:
    ```text
    has_doctrine = mobile_warfare # Grand doctrine
    ```
  - Example:
    ```text
    has_doctrine = mobile_infantry # Subdoctrine
    ```
  - Description: Checks if the given grand doctrine or subdoctrine is currently active for the country.
  - Version Added: 1.17

- **has_subdoctrine_in_track**
  - Parameters:
    ```text
    <track>
    The track to check for.
    ```
  - Example:
    ```text
    has_subdoctrine_in_track = infantry
    ```
  - Description: Checks if any subdoctrine is currently assigned to (any instance of) the given track.
  - Version Added: 1.17

- **has_completed_subdoctrine**
  - Parameters:
    ```text
    <subdoctrine>
    The subdoctrine to check for.
    ```
  - Example:
    ```text
    has_completed_subdoctrine = mobile_infantry
    ```
  - Description: Checks if the current country has ever completed the specified subdoctrine (even if it was later switched out).
  - Version Added: 1.17

- **has_completed_track**
  - Parameters:
    ```text
    <track>
    The track to check for.
    ```
  - Example:
    ```text
    has_completed_track = infantry
    ```
  - Description: Checks if the given subdoctrine track has been completed
  - Version Added: 1.17

- **has_mastery**
  - Parameters:
    ```text
    amount = <int>
    The amout to check for.
    track = <track>
    The track to check for.
    ```
  - Example:
    ```text
    has_mastery = {
        amount = 200
        track = infantry
    }
    ```
  - Description: Checks if any track of the given type has at least X mastery.
  - Version Added: 1.17

- **has_mastery_level**
  - Parameters:
    ```text
    amount = <int>
    The amount to check for.
    subdoctrine = <subdoctrine>
    The subdoctrine to check for.
    ```
  - Example:
    ```text
    has_mastery_level = {
        amount = 2
        subdoctrine = mobile_infantry
    }
    ```
  - Description: Checks if the country has reached the specified number of mastery levels (rewards) for the given subdoctrine.
  - Version Added: 1.17

### Equipment

- **stockpile_ratio**
  - Parameters:
    ```text
    archetype = <string>
    The equipment archetype to check for.
    ratio = <float>
    The ratio of equipment to check for.
    ```
  - Example:
    ```text
    stockpile_ratio = {
        archetype = infantry_equipment
        ratio > 0.5
    }
    ```
  - Description: Checks if the current scope has stockpiled the specified equipment to the specified ratio against fielded equipment of the same type.
  - Notes:
    ```text
    Must use either > or < operators for ratio.
    For the convoy equipment which is not fielded as other equipments, ratio shall be not a percentage but a direct amount (for instance 256 convoys)
    ```
  - Version Added: 1.5

- **has_equipment**
  - Parameters:
    ```text
    <equipment> = <int> / <variable>
    The equipment to check for, and the amount to check for.
    ```
  - Example:
    ```text
    has_equipment = {
        infantry_equipment_1 > 10
    }
    ```
  - Description: Checks if the current scope has the specified equipment to the specified amount.
  - Notes: Must use either > or < operators.
  - Version Added: 1.0

- **has_any_license**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    has_any_license = yes
    ```
  - Description: Checks if the current scope has any licenses from other countries.
  - Version Added: 1.0

- **is_licensing_any_to**
  - Parameters:
    ```text
    <scope> / <variable>
    The country to check for.
    ```
  - Example:
    ```text
    is_licensing_any_to = GER
    ```
  - Description: Checks if the current scope is licensing to the specified scope.
  - Version Added: 1.0

- **is_licensing_to**
  - Parameters:
    ```text
    target = <scope>
    The country to check for.
    archetype = <string>
    The equipment archetype to check for. Optional.
    Equipment scope
    type = <string>
    The equipment to check for. Optional.
    version = <int>
    The variant id of the equipment. Optional.
    ```
  - Example:
    ```text
    is_licensing_to = {
        target = GER
        archetype = infantry_equipment
    }
    ```
  - Example:
    ```text
    is_licensing_to = {
        target = GER
        equipment = {
            type = light_tank_equipment
            version = 1
        }
    }
    ```
  - Description: Checks if the current scope is licensing the specified equipment to the specified country.
  - Version Added: 1.0

- **has_license**
  - Parameters:
    ```text
    from = <scope>
    The country to check for.
    archetype = <string>
    The equipment archetype to check for. Optional.
    Equipment scope
    type = <string>
    The equipment to check for. Optional.
    version = <int>
    The variant id of the equipment. Optional.
    ```
  - Example:
    ```text
    has_license = {
        from = GER
        archetype = infantry_equipment
    }
    ```
  - Example:
    ```text
    has_license = {
        from = GER
        equipment = {
            type = light_tank_equipment
            version = 1
        }
    }
    ```
  - Description: Checks if the current scope has a license for the specified equipment from the specified country.
  - Version Added: 1.0

- **fuel_ratio**
  - Parameters:
    ```text
    <float> / <variable>
    The ratio to check with.
    ```
  - Example:
    ```text
    fuel_ratio > 0.4
    ```
  - Description: Checks the fuel ratio of the country.
  - Notes: Must use either < or > operators.
  - Version Added: 1.6

- **has_fuel**
  - Parameters:
    ```text
    <int> / <variable>
    The amount to compare with.
    ```
  - Example:
    ```text
    has_fuel > 400
    ```
  - Description: Checks the fuel amount of the country.
  - Notes: Must use either < or > operators.
  - Version Added: 1.6

- **has_design_based_on**
  - Parameters:
    ```text
    <archetype>
    The equipment archetype.
    ```
  - Example:
    ```text
    has_design_based_on = light_tank_chassis
    ```
  - Description: Checks if the country has a builtable non-obsolete design based on the specified equipment archetype.
  - Notes:
    ```text
    Equipment archetypes can be seen in
    /Hearts of Iron IV/common/units/equipment/*
    .
    ```
  - Version Added: 1.11

### Intelligence

- **estimated_intel_max_piercing**
  - Parameters:
    ```text
    tag = <scope>
    The country to check for.
    value = <int>
    The amount to check for.
    ```
  - Example:
    ```text
    estimated_intel_max_piercing = {
        tag = GER
        value > 2
    }
    ```
  - Description: Checks if the specified scope has the specified amount of piercing based on the current scope's intel.
  - Notes: Must use either > or < operators for value.
  - Version Added: 1.0

- **estimated_intel_max_armor**
  - Parameters:
    ```text
    tag = <scope>
    The country to check for.
    value = <int>
    The amount to check for.
    ```
  - Example:
    ```text
    estimated_intel_max_armor = {
        tag = GER
        value > 2
    }
    ```
  - Description: Checks if the specified scope has the specified amount of armor based on the current scope's intel.
  - Notes: Must use either > or < operators for value.
  - Version Added: 1.0

- **compare_intel_with**
  - Parameters:
    ```text
    target = <tag> / <variable>
    The target to compare with.
    civilian_intel <>= <float> / <variable>
    Comparison of civilian intel.
    army_intel <>= <float> / <variable>
    Comparison of army intel.
    navy_intel <>= <float> / <variable>
    Comparison of navy intel.
    airforce_intel <>= <float> / <variable>
    Comparison of airforce intel.
    ```
  - Example:
    ```text
    compare_intel_with = { 
        target = POL 
        civilian_intel > 0.5
        army_intel = 0
        navy_intel < 0
    }
    ```
  - Description: Compares intel between 2 countries.
  - Notes: Can use < (in which case the current country has x less intel), >, and = (in which case it must be equal).
  - Version Added: 1.9

- **intel_level_over**
  - Parameters:
    ```text
    target = <tag> / <variable>
    The target to compare with.
    civilian_intel <>= <float> / <variable>
    Comparison of civilian intel.
    army_intel <>= <float> / <variable>
    Comparison of army intel.
    navy_intel <>= <float> / <variable>
    Comparison of navy intel.
    airforce_intel <>= <float> / <variable>
    Comparison of airforce intel.
    ```
  - Example:
    ```text
    intel_level_over = { 
        target = POL 
        civilian_intel > 0.5
        army_intel = 0
        navy_intel < 0
    }
    ```
  - Description: Checks the intel level from the current country over a specified country.
  - Notes: Can use < (in which case the current country has x less intel), >, and = (in which case it must be equal).
  - Version Added: 1.9

- **has_intelligence_agency**
  - Parameters:
    ```text
    <boolean>
    The intelligence agency to check.
    ```
  - Example:
    ```text
    has_intelligence_agency = yes
    ```
  - Description: Checks if the current scope has an intelligence agency.
  - Version Added: 1.9

- **network_national_coverage**
  - Parameters:
    ```text
    target = <tag> / <variable>
    The country which is checked.
    value <> <float> / <variable>
    The value of network.
    ```
  - Example:
    ```text
    network_national_coverage = {
        target = POL
        value < 70
    }
    ```
  - Description: Checks network national coverage over a specific country.
  - Notes: Must use < or > for value.

- **network_strength**
  - Parameters:
    ```text
    target = <tag>
    The country which is checked.
    state = <id> / <variable>
    The state which is checked.
    value <> <float> / <variable>
    The strength of network.
    ```
  - Example:
    ```text
    network_strength = {
        target = POL
        value < 70
    }
    ```
  - Description: Checks network national coverage over a specific country.
  - Notes: Must use < or > for value. Can use either or both of target and state.
  - Version Added: 1.9

- **has_done_agency_upgrade**
  - Parameters:
    ```text
    <string>
    The agency upgrade to check.
    ```
  - Example:
    ```text
    has_done_agency_upgrade = upgrade_army_department
    ```
  - Description: Checks if the current scope has the specified agency upgrade (to its highest level).
  - Version Added: 1.9

- **agency_upgrade_number**
  - Parameters:
    ```text
    <int> / <variable>
    The amount of agency upgrades to check for.
    ```
  - Example:
    ```text
    agency_upgrade_number > 4
    ```
  - Description: Checks the number of upgrades done in the current scope's intelligence agency.
  - Notes: Must use either > or < operators.
  - Version Added: 1.9

- **decryption_progress**
  - Parameters:
    ```text
    target = <tag>
    The country to compare with.
    value <> <float>
    The value to compare.
    ```
  - Example:
    ```text
    decryption_progress = {
        target = POL
        value < 0.5
    }
    ```
  - Description: Checks the decryption progress towards a country.
  - Notes: Must use either > or < operators for value.
  - Version Added: 1.9

- **has_captured_operative**
  - Parameters:
    ```text
    <tag>/<bool>
    Country whose operative was captured/Whether an operative was captured.
    ```
  - Example:
    ```text
    has_captured_operative = POL
    ```
  - Example:
    ```text
    has_captured_operative = yes
    ```
  - Description: Checks if the current scope has captured an operative.
  - Version Added: 1.9

- **has_finished_collecting_for_operation**
  - Parameters:
    ```text
    target = <tag>
    Country towards whom the operation is targeted.
    operation = <token>
    The operation which current scope is planning against the target.
    ```
  - Example:
    ```text
    has_finished_collecting_for_operation = {
        target = POL
        operation = operation_infiltrate_armed_forces_navy
    }
    ```
  - Description: Checks if the current scope has finished collecting resources for an operation.
  - Version Added: 1.9

- **is_preparing_operation**
  - Parameters:
    ```text
    target = <tag>
    Country towards whom the operation is targeted.
    operation = <token>
    The operation which current scope is planning against the target. Optional.
    ```
  - Example:
    ```text
    is_preparing_operation = {
        target = POL
        operation = operation_infiltrate_armed_forces_navy
    }
    ```
  - Description: Checks if the current scope is preparing an operation against the specified country.
  - Version Added: 1.9

- **is_running_operation**
  - Parameters:
    ```text
    target = <tag>
    Country towards whom the operation is targeted.
    operation = <token>
    The operation which current scope is planning against the target. Optional.
    ```
  - Example:
    ```text
    is_running_operation = {
        target = POL
        operation = operation_infiltrate_armed_forces_navy
    }
    ```
  - Description: Checks if the current scope is running an operation against the specified country.
  - Version Added: 1.9

- **num_finished_operations**
  - Parameters:
    ```text
    target = <tag>
    Country towards whom the operation is targeted.
    operation = <token>
    The operation which current scope is planning against the target. Optional.
    ```
  - Example:
    ```text
    num_finished_operations = {
        target = POL
        operation = operation_infiltrate_armed_forces_navy
    }
    ```
  - Description: Checks how many finished operations the current scope had against the specified country.
  - Version Added: 1.9

- **has_operation_token**
  - Parameters:
    ```text
    tag = <tag>
    Country towards whom the operation is targeted.
    token = <token>
    The operation token.
    ```
  - Example:
    ```text
    has_operation_token = {
        tag = POL
        token = token_name
    }
    ```
  - Description: Checks if the current scope has an operation token against an another country.
  - Version Added: 1.9

- **is_active_decryption_bonuses_enabled**
  - Parameters:
    ```text
    <tag>
    The country towards which the bonus is enabled.
    ```
  - Example:
    ```text
    is_active_decryption_bonuses_enabled = POL
    ```
  - Description: Checks if the current scope has any decryption bonuses towards the specified country.
  - Version Added: 1.9

- **is_cryptology_department_active**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    is_cryptology_department_active = yes
    ```
  - Description: Checks if the current scope has a cryptology department active.
  - Version Added: 1.9

- **is_decrypting**
  - Parameters:
    ```text
    <tag>
    The country which is decrypted.
    ```
  - Example:
    ```text
    is_decrypting = POL
    ```
  - Description: Checks if the current scope is decrypting a certain country.
  - Version Added: 1.9

- **is_fully_decrypted**
  - Parameters:
    ```text
    <tag>
    The country which is decrypted.
    ```
  - Example:
    ```text
    is_fully_decrypted = POL
    ```
  - Description: Checks if the current scope has fully decrypted a certain country.
  - Version Added: 1.9

- **num_fake_intel_divisions**
  - Parameters:
    ```text
    <int>
    Amount of divisions.
    ```
  - Example:
    ```text
    num_fake_intel_divisions > 10
    ```
  - Description: Checks the amount of fake intel divisions.
  - Notes: Must use either < or >.
  - Version Added: 1.9

- **num_free_operative_slots**
  - Parameters:
    ```text
    <int>
    Amount of slots.
    ```
  - Example:
    ```text
    num_free_operative_slots > 2
    ```
  - Description: Checks the amount of free operative slots.
  - Notes: Must use either < or >.
  - Version Added: 1.9

- **num_operative_slots**
  - Parameters:
    ```text
    <int>
    Amount of slots.
    ```
  - Example:
    ```text
    num_operative_slots > 2
    ```
  - Description: Checks the amount of operative slots.
  - Notes: Must use either < or >.
  - Version Added: 1.9

- **num_of_operatives**
  - Parameters:
    ```text
    <int>
    Amount of operatives.
    ```
  - Example:
    ```text
    num_of_operatives > 2
    ```
  - Description: Checks the amount of operatives.
  - Notes: Must use either < or >.
  - Version Added: 1.9

### AI

- **ai_irrationality**
  - Parameters:
    ```text
    <int>
    The amount to check for.
    ```
  - Example:
    ```text
    ai_irrationality > 10
    ```
  - Description: Checks if the current scope AI has the specified irrationality.
  - Notes: Must use either > or < operators.
  - Version Added: 1.0

- **ai_liberate_desire**
  - Parameters:
    ```text
    target = <scope>
    The country to check for.
    count = <float>
    The amount to check for.
    ```
  - Example:
    ```text
    ai_liberate_desire = {
        target = GER
        count > 1
    }
    ```
  - Description: Checks if the current scope AI has the specified liberation desire towards the specified country.
  - Notes: Must use either > or < operators for count.
  - Version Added: 1.0

- **ai_has_role_division**
  - Parameters:
    ```text
    <string>
    The role to check for.
    ```
  - Example:
    ```text
    ai_has_role_division = infantry
    ```
  - Description: Checks if the current scope AI has a division with the specified role.
  - Notes:
    ```text
    Roles are defined in
    /Hearts of Iron IV/common/ai_templates/*.txt
    ```
  - Version Added: 1.0

- **ai_has_role_template**
  - Parameters:
    ```text
    <string>
    The role to check for.
    ```
  - Example:
    ```text
    ai_has_role_template = armor
    ```
  - Description: Checks if the current scope AI has a division template with the specified role.
  - Notes:
    ```text
    Roles are defined in
    /Hearts of Iron IV/common/ai_templates/*.txt
    ```
  - Version Added: 1.0

- **ai_wants_divisions**
  - Parameters:
    ```text
    <int>
    The amount to check for.
    ```
  - Example:
    ```text
    ai_wants_divisions > 10
    ```
  - Description: Checks if the current scope AI desires the specified amount of divisions.
  - Notes: Must use either > or < operators.
  - Version Added: 1.0

- **has_template_ai_majority_unit**
  - Parameters:
    ```text
    <string>
    The unit to check for.
    ```
  - Example:
    ```text
    has_template_ai_majority_unit = infantry
    ```
  - Description: Checks if the current scope AI has a division template mostly made up of the specified unit.
  - Version Added: 1.0

### Characters

These are character-related triggers in the country scope, not [character-scoped triggers](#character-scope).

- **can_be_country_leader**
  - Parameters:
    ```text
    <character>
    The character to check.
    ```
  - Example:
    ```text
    can_be_country_leader = POL_character_test
    ```
  - Description: Checks if the specified character has a country leader role, active or not, and can utilise it in this country.
  - Version Added: 1.11

- **has_character**
  - Parameters:
    ```text
    <string>
    The character to check.
    ```
  - Example:
    ```text
    has_character = my_character
    ```
  - Description: Checks if the current scope has the specified character recruited. The character does NOT need to be in power.
  - Version Added: 1.11

- **has_country_leader**
  - Parameters:
    ```text
    ruling_only = <bool>
    (default = yes) Limit check to ruling only.
    character = <character_token>
    (recommended criteria) The character to check for. Optional.
    name = <string>
    The name to check for. Optional.
    id = <int>
    The id to check for. Optional.
    ```
  - Example:
    ```text
    has_country_leader = {
        id = 10
    }
    ```
  - Example:
    ```text
    has_country_leader = {
    	character = SPR_niceto_alcala_zamora
    	ruling_only = yes
    }
    ```
  - Example:
    ```text
    has_country_leader = {
        name = "John Smith"
        ruling_only = yes
    }
    ```
  - Description: Checks if the current scope has the specified country leader.
  - Version Added: 1.3

- **has_country_leader_ideology**
  - Parameters:
    ```text
    <ideology>
    Checks the ideology of the active country leader
    ```
  - Example:
    ```text
    has_country_leader_ideology = nazism
    ```
  - Description: Checks if the current scope's active country leader has the specified ideology.
  - Version Added: 1.11

- **has_country_leader_with_trait**
  - Parameters:
    ```text
    <string>
    The trait to check.
    ```
  - Example:
    ```text
    has_country_leader_with_trait = champion_of_peace_1
    ```
  - Description: Checks if the leader of the country has a specific trait.
  - Version Added: 1.6

- **is_female**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    is_female = yes
    ```
  - Description: Checks if the current country leader is female.
  - Version Added: 1.9

- **has_unit_leader**
  - Parameters:
    ```text
    <int>
    The id to check for.
    ```
  - Example:
    ```text
    has_unit_leader = 1
    ```
  - Description: Checks if the current scope has a unit leader with the specified id.
  - Notes: Only the legacy ID can be used, the character ID doesn't work.
  - Version Added: 1.0

- **has_scientist_specialization**
  - Parameters:
    ```text
    specialization = <specialization_token>
    Specialization.
    ```
  - Example:
    ```text
    has_scientist_specialization = specialization_nuclear
    ```
  - Description: Checks if the country in scope has a scientist with a skill level of at least 1 in specialization.
  - Version Added: 1.15

### Peace conferences

These are not exactly peace conference-related triggers, but **those that can only be used within peace conferences**.

- **pc_is_winner**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    pc_is_winner = yes
    ```
  - Description: Checks if the current scope is a winner within the peace conference.
  - Version Added: 1.12

- **pc_is_on_winning_side**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    pc_is_on_winning_side = yes
    ```
  - Description: Checks if the current scope is on the winning side within the peace conference.
  - Version Added: 1.12

- **pc_is_loser**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    pc_is_loser = yes
    ```
  - Description: Checks if the current scope is a loser within the peace conference.
  - Version Added: 1.12

- **pc_is_untouched_loser**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    pc_is_untouched_loser = yes
    ```
  - Description: Checks if the current scope is an untouched loser within the peace conference.
  - Version Added: 1.12

- **pc_is_on_same_side_as**
  - Parameters:
    ```text
    <scope>
    Country to check for.
    ```
  - Example:
    ```text
    pc_is_on_same_side_as = BHR
    ```
  - Description: Checks if the current scope is on the same side of the peace conference as the specified country.
  - Version Added: 1.12

- **pc_is_liberated**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    pc_is_liberated = yes
    ```
  - Description: Checks if the current scope has been liberated within the peace conference.
  - Version Added: 1.12

- **pc_is_liberated_by**
  - Parameters:
    ```text
    <scope>
    Country to check for.
    ```
  - Example:
    ```text
    pc_is_liberated_by = BHR
    ```
  - Description: Checks if the current scope has been liberated within the peace conference by the specified country.
  - Version Added: 1.12

- **pc_is_puppeted**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    pc_is_puppeted = yes
    ```
  - Description: Checks if the current scope has been puppeted within the peace conference.
  - Version Added: 1.12

- **pc_is_puppeted_by**
  - Parameters:
    ```text
    <scope>
    Country to check for.
    ```
  - Example:
    ```text
    pc_is_puppeted_by = BHR
    ```
  - Description: Checks if the current scope has been puppeted within the peace conference by the specified country.
  - Version Added: 1.12

- **pc_is_forced_government**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    pc_is_forced_government = yes
    ```
  - Description: Checks if the current scope has had an enforced government change within the peace conference.
  - Version Added: 1.12

- **pc_is_forced_government_by**
  - Parameters:
    ```text
    <scope>
    Country to check for.
    ```
  - Example:
    ```text
    pc_is_forced_government_by = BHR
    ```
  - Description: Checks if the current scope has had an enforced government change within the peace conference demanded by the specified country.
  - Version Added: 1.12

- **pc_is_forced_government_to**
  - Parameters:
    ```text
    <ideology group>
    Ideology group to check for.
    ```
  - Example:
    ```text
    pc_is_forced_government_to = democratic
    ```
  - Description: Checks if the current scope has had an enforced government change to the specified ideology group.
  - Version Added: 1.12

- **pc_total_score**
  - Parameters:
    ```text
    <decimal>
    Scope to check for.
    ```
  - Example:
    ```text
    pc_total_score > 2400
    ```
  - Description: Checks if the current scope has the specified amount in total score within the peace conference.
  - Notes: Can only be used for the winning countries.
  - Version Added: 1.12

- **pc_current_score**
  - Parameters:
    ```text
    <decimal>
    Scope to check for.
    ```
  - Example:
    ```text
    pc_current_score > 100
    ```
  - Description: Checks if the current scope has the specified amount in current score within the peace conference.
  - Notes: Can only be used for the winning countries.
  - Version Added: 1.12

## Faction scope

Can be used in **faction** scope.

There are currently no faction-specific triggers.

## State scope

Can be used in **state** scope.

### General

- **state**
  - Parameters:
    ```text
    <scope> / <variable>
    The state to check for.
    ```
  - Example:
    ```text
    state = 10
    ```
  - Example:
    ```text
    state = var:state
    ```
  - Description: Checks if the current scope is the specified state.
  - Version Added: 1.0

- **region**
  - Parameters:
    ```text
    <int>
    The strategic region id to check for.
    ```
  - Example:
    ```text
    region = 10
    ```
  - Description: Checks if the current scope is a state in the specified strategic region.
  - Version Added: 1.0

- **<building> (building_count_trigger)**
  - Parameters:
    ```text
    <int>
    The amount of the specified building to check for.
    ```
  - Example:
    ```text
    arms_factory > 10
    ```
  - Description: Checks if the current scope has the specified amount of the specified building.
  - Notes:
    ```text
    Must use either > or < operators.
    Can also be used in building scope.
    ```
  - Version Added: 1.0

- **free_building_slots**
  - Parameters:
    ```text
    building = <string>
    The building to check for.
    size = <int>
    The amount to check for.
    include_locked = <bool>
    Whether to include locked slots.
    ```
  - Example:
    ```text
    free_building_slots = {
        building = arms_factory
        size > 10
        include_locked = yes
    }
    ```
  - Description: Checks if the current scope has available slots for the specified amount of buildings.
  - Notes: Must use either > or < operators for size.
  - Version Added: 1.0

- **non_damaged_building_level**
  - Parameters:
    ```text
    building = <string>
    The building to check for.
    level = <int>
    The amount to check for.
    ```
  - Example:
    ```text
    non_damaged_building_level = {
        building = arms_factory
        level > 4
    }
    ```
  - Description: Checks if the current scope has the specified amount of the specified buildings that are undamaged.
  - Notes: Must use either > or < operators for level.
  - Version Added: 1.9

- **any_province_building_level**
  - Parameters:
    ```text
    building = <string>
    The building to check for.
    limit = <int>
    The amount to check for.
    Province scope
    id = <int>
    The province to check for.
    limit_to_border = <bool>
    Whether to limit check to border provinces.
    ```
  - Example:
    ```text
    any_province_building_level = {
        province = {
            id = 445
            id = 494
            limit_to_border = yes
        }
        building = bunker
        level < 5
    }
    ```
  - Description: Checks if the current scope has the specified provincal building at the specified amount in the specified provinces.
  - Notes: Must use either > or < operators for level.
  - Version Added: 1.0

- **has_state_flag**
  - Parameters:
    ```text
    <string>
    The flag to check for.
    ```
  - Example:
    ```text
    has_state_flag = my_flag
    ```
  - Description: Checks if the current scope has the specified flag.
  - Version Added: 1.0

- **has_state_flag**
  - Parameters:
    ```text
    flag = <string>
    The flag to check.
    value = <int>
    The flag value to check for. Optional.
    date = <date>
    The flag creation date to check for. Optional.
    days = <int>
    The duration the flag existed for. Optional.
    ```
  - Example:
    ```text
    has_state_flag = {
        flag = my_flag
        days > 30
        date > 1936.6.1
        value > 0
    }
    ```
  - Description: Compares the specified flag's last set date, days since last set, and/or value.
  - Notes:
    ```text
    If not set, the value comparison is
    >0
    .
    value
    is limited between -32768 and 32767.
    ```
  - Version Added: 1.0

- **state_population**
  - Parameters:
    ```text
    <float>
    The amount to check for.
    ```
  - Example:
    ```text
    state_population > 10000
    ```
  - Description: Checks if the current scope has the specified state population.
  - Notes: Must use either > or < operators.
  - Version Added: 1.0

- **state_population_k**
  - Parameters:
    ```text
    <float>
    The amount to check for.
    ```
  - Example:
    ```text
    state_population_k > 10
    ```
  - Description: Checks if the current scope has the specified state population in thousands.
  - Notes: Must use either > or < operators.
  - Version Added: 1.0

- **is_capital**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    is_capital = yes
    ```
  - Description: Checks if the current scope is a capital.
  - Version Added: 1.5

- **is_controlled_by**
  - Parameters:
    ```text
    <scope> / <variable>
    The country to check for.
    ```
  - Example:
    ```text
    is_controlled_by = GER
    ```
  - Description: Checks if the current scope is controlled by the specified country.
  - Version Added: 1.0

- **is_fully_controlled_by**
  - Parameters:
    ```text
    <scope> / <variable>
    The country to check for.
    ```
  - Example:
    ```text
    is_fully_controlled_by = GER
    ```
  - Description: Checks if the current scope is fully controlled by the specified country.
  - Version Added: 1.5

- **is_owned_by**
  - Parameters:
    ```text
    <scope> / <variable>
    The country to check for.
    ```
  - Example:
    ```text
    is_owned_by = GER
    ```
  - Description: Checks if the current scope is owned by the specified country.
  - Version Added: 1.0

- **is_claimed_by**
  - Parameters:
    ```text
    <scope> / <variable>
    The country to check for.
    ```
  - Example:
    ```text
    is_claimed_by = GER
    ```
  - Description: Checks if the current scope is claimed by the specified country.
  - Version Added: 1.0

- **is_core_of**
  - Parameters:
    ```text
    <scope> / <variable>
    The country to check for.
    ```
  - Example:
    ```text
    is_core_of = GER
    ```
  - Description: Checks if the current scope is a core of the specified country.
  - Version Added: 1.0

- **is_owned_and_controlled_by**
  - Parameters:
    ```text
    <scope> / <variable>
    The country to check for.
    ```
  - Example:
    ```text
    is_owned_and_controlled_by = GER
    ```
  - Description: Checks if the current scope is owned and controlled by the specified country.
  - Version Added: 1.0

- **is_demilitarized_zone**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    is_demilitarized_zone = yes
    ```
  - Description: Checks if the current scope is a demilitarized zone.
  - Version Added: 1.0

- **is_border_conflict**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    is_border_conflict = yes
    ```
  - Description: Checks if the current scope is part of a border war.
  - Version Added: 1.0

- **is_in_home_area**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    is_in_home_area = yes
    ```
  - Description: Checks if the current scope is connected to the capital state over land. The scope needs to be owned as well for the statement for it to be true.
  - Version Added: 1.0

- **is_coastal**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    is_coastal = yes
    ```
  - Description: Checks if the current scope is a coastal state.
  - Version Added: 1.0

- **is_one_state_island**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    is_one_state_island = yes
    ```
  - Description: Checks if the current scope is a coastal state with no adjacent land states.
  - Notes: An adjacent land state may be connected via a naval crossing.
  - Version Added: 1.13

- **is_island_state**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    is_island_state = yes
    ```
  - Description: Checks if the current scope is a state where every province has no land neighbour.
  - Notes: An adjacent land division may be connected via a naval crossing.
  - Version Added: 1.0

- **is_on_continent**
  - Parameters:
    ```text
    <string>
    The continent to check for.
    ```
  - Example:
    ```text
    is_on_continent = europe
    ```
  - Description: Checks if the current scope is on the specified continent.
  - Notes:
    ```text
    Continents are found in
    /Hearts of Iron IV/map/continent.txt
    .
    ```
  - Version Added: 1.0

- **is_on_same_continent_as**
  - Parameters:
    ```text
    <scope> / <variable>
    The country to check for.
    ```
  - Example:
    ```text
    is_on_same_continent_as = FRA
    ```
  - Description: Checks if the scope state is on the same continent as the given state. The capital state is used for given country tag.
  - Notes: Can also be used in country scope.
  - Version Added: 1.17

- **impassable**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    impassable = yes
    ```
  - Description: Checks if the current scope is impassable.
  - Version Added: 1.9.1

- **has_state_category**
  - Parameters:
    ```text
    <string>
    The category to check for.
    ```
  - Example:
    ```text
    has_state_category = rural
    ```
  - Description: Checks if the current scope has the specified category.
  - Notes:
    ```text
    State categories are found in
    /Hearts of Iron IV/common/state_category/*.txt
    .
    ```
  - Version Added: 1.0

- **state_strategic_value**
  - Parameters:
    ```text
    <int>
    The amount to check for.
    ```
  - Example:
    ```text
    state_strategic_value > 10
    ```
  - Description: Checks if the current scope has the specified strategic value.
  - Notes: Must use either > or < operators.
  - Version Added: 1.5

- **state_and_terrain_strategic_value**
  - Parameters:
    ```text
    <int>
    The amount to check for.
    ```
  - Example:
    ```text
    state_and_terrain_strategic_value > 10
    ```
  - Description: Checks if the current scope has the specified state and terrain strategic value.
  - Notes: Must use either > or < operators.
  - Version Added: 1.5

- **num_owned_neighbour_states**
  - Parameters:
    ```text
    owner = <scope>
    The country to check for.
    count = <int>
    The amount to check for.
    ```
  - Example:
    ```text
    num_owned_neighbour_states = {
        owner = GER
        count > 2
    }
    ```
  - Description: Checks if the current scope has the specified amount of neighbor states belonging to the specified country.
  - Notes: Must use either > or < operators for count.
  - Version Added: 1.0

- **distance_to**
  - Parameters:
    ```text
    value = <float>
    The distance to check for.
    target = <scope>
    The state to compare against.
    ```
  - Example:
    ```text
    distance_to = {
        value > 1000
        target = 49
    }
    ```
  - Description: Checks if the current scope is at the specified distance from the specified state.
  - Notes: Must use either > or < operators for distance.
  - Version Added: 1.0

- **ships_in_area**
  - Parameters:
    ```text
    area = <int>
    The strategic region to check for.
    size = <int>
    The amount to check for.
    ```
  - Example:
    ```text
    ships_in_area = { area = 104 size > 14 }
    ```
  - Description: Checks if the current scope has the specified amount of ships in the specified strategic region.
  - Notes: Must use either > or < operators for count.
  - Version Added: 1.0

- **<resource> (resource_count_trigger)**
  - Parameters:
    ```text
    <int>
    The amount to check for.
    ```
  - Example:
    ```text
    tungsten > 10
    ```
  - Description: Checks if the current scope has the specified amount of the specified resource.
  - Notes:
    ```text
    Must use either > or < operators for amount.
    Can also be used in country scope.
    ```
  - Version Added: ???

- **has_resources_amount**
  - Parameters:
    ```text
    resource = <string>
    The resource to check for.
    amount = <int>
    The amount to check for.
    delivered = <bool>
    If specified, checks the amount after the modifiers are applied rather than the base resource value.
    ```
  - Example:
    ```text
    has_resources_amount = {
        resource = oil
        amount > 10
        delivered = yes
    }
    ```
  - Description: Checks if the current scope has the specified amount of the specified resource.
  - Notes: Must use either > or < operators for amount.
  - Version Added: 1.3

- **has_resources_rights**
  - Parameters:
    ```text
    receiver = <scope>
    The receiver of the resource rights. Mandatory if used in state scope.
    resources = { <resource> <...> <resource> }
    Resources to check for. Optional, defaults to any if unset.
    ```
  - Example:
    ```text
    has_resources_rights = {
      receiver = POL
      resources = { oil steel }
    }
    ```
  - Description: Checks if there are any resource rights with the specified parameters.
  - Notes:
    ```text
    Can be used in either state or country scope. Always returns false if the state has no resources.
    Can also be used in country scope.
    ```
  - Version Added: 1.12

- **days_since_last_strategic_bombing**
  - Parameters:
    ```text
    <int>
    The amount to compare with.
    ```
  - Example:
    ```text
    days_since_last_strategic_bombing < 10
    ```
  - Description: Checks how many days have passed since the last strategic bombing of the state.
  - Notes: Must use either > or < operators.
  - Version Added: 1.6

- **has_railway_connection**
  - Parameters:
    ```text
    <scope> / <variable>
    The states to check.
    <id>
    The provinces to check. Optional.
    ```
  - Example:
    ```text
    has_railway_connection = {
    	start_state = 10
    	target_state = 90
    }
    ```
  - Example:
    ```text
    has_railway_connection = {
    	start_province = 402
    	target_province = 9400
    }
    ```
  - Description: Returns true if the states are connected by a railway. Can also check provinces.
  - Version Added: 1.11

- **can_build_railway**
  - Parameters:
    ```text
    <scope> / <variable>
    The states to check.
    <id>
    The provinces to check. Optional.
    ```
  - Example:
    ```text
    can_build_railway = {
    	start_state = 10
    	target_state = 90
    }
    ```
  - Example:
    ```text
    can_build_railway = {
    	start_province = 402
    	target_province = 9400
    }
    ```
  - Description: Returns true if a railway can be built between states. Can also check for provinces.
  - Version Added: 1.11

- **has_railway_level**
  - Parameters:
    ```text
    <scope> / <variable>
    The states to check.
    <int>
    Railway level.
    ```
  - Example:
    ```text
    has_railway_level = {
        	state = 114
        	level = 5
    }
    ```
  - Description: Checks if a state contains a railway at or above the specified level.
  - Notes: Works with level 1, 2, 3, 4 or 5. Level 0 does not work.
  - Version Added: 1.11

- **pc_does_state_stack_demilitarized**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    pc_does_state_stack_demilitarized = yes
    ```
  - Description: Checks if the current scope was demilitarised during a current or previously-ended peace conference.
  - Version Added: 1.12

- **pc_does_state_stack_dismantled**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    pc_does_state_stack_dismantled = yes
    ```
  - Description: Checks if the current scope was dismantled during a current or previously-ended peace conference.
  - Version Added: 1.12

- **pc_is_state_claimed**
  - Parameters:
    ```text
    <scope>
    Country to check for.
    ```
  - Example:
    ```text
    pc_is_state_claimed = yes
    ```
  - Description: Checks if the current scope was claimed by any country during the peace conference.
  - Notes: Can only be used within peace conferences.
  - Version Added: 1.12.8

- **pc_is_state_claimed_by**
  - Parameters:
    ```text
    <scope>
    Country to check for.
    ```
  - Example:
    ```text
    pc_is_state_claimed_by = BHR
    ```
  - Description:
    ```text
    Checks if the current scope was claimed by the specified country during the peace conference.  Note, that "claim" in this context, while includes, is NOT limited to outright taking: forcing government, puppeting and liberating will render that trigger true as well. If one looks specifically for states taken by victors for themselves,
    pc_is_state_claimed_and_taken_by
    should be used.
    ```
  - Notes: Can only be used within peace conferences.
  - Version Added: 1.12

- **pc_is_state_claimed_and_taken_by**
  - Parameters:
    ```text
    <scope>
    Country to check for.
    ```
  - Example:
    ```text
    pc_is_state_claimed_and_taken_by = SOV
    ```
  - Description: Checks if the current scope was claimed with "Take State" action (i.e. annexed) by the specified country during the peace conference.
  - Notes: Can only be used within peace conferences.

- **pc_is_state_outside_influence_for_winner**
  - Parameters:
    ```text
    <scope>
    Country to check for.
    ```
  - Example:
    ```text
    pc_is_state_outside_influence_for_winner = ROOT
    ```
  - Description: Checks if the current state is outside of the influence of the specified winner country.
  - Notes:
    ```text
    Can only be used within peace conferences.
    Was called pc_is_state_outside_influence_for prior to 1.12.8.
    ```
  - Version Added: 1.12.8

- **pc_turn**
  - Parameters:
    ```text
    <int>
    The amount of turns to check for.
    ```
  - Example:
    ```text
    pc_turn > 20
    ```
  - Description: Compares the amount of turns that have passed during the peace conference with a number.
  - Notes: Can only be used within peace conferences.
  - Version Added: 1.12.8

- **can_construct_building**
  - Parameters:
    ```text
    <build type>
    The type of building.
    ```
  - Examples: can_construct_building = bunker
  - Description: Checks if the country (as ROOT) and state in scope can build a building in the state.
  - Version Added: 1.15

- **has_contested_owner**
  - Parameters:
    ```text
    <country> / <variable>
    Country to check.
    ```
  - Example:
    ```text
    has_contested_owner = GER
    ```
  - Description: Checks if a state has the specified country as a contested owner. The trigger can be used either from a country or a state scope and accepts the other as parameter.
  - Notes: Can also be used in country scope.
  - Version Added: 1.15

### Resistance and Compliance

- **compliance**
  - Parameters:
    ```text
    <int>
    The amount to compare with.
    ```
  - Example:
    ```text
    compliance > 50
    ```
  - Description: Compares the compliance value of the current scope with the given value.
  - Notes: Must use either > or < operators.
  - Version Added: 1.9

- **compliance_speed**
  - Parameters:
    ```text
    <int>
    The amount to compare with.
    ```
  - Example:
    ```text
    compliance_speed > 50
    ```
  - Description: Compares the compliance speed of the current scope with the given value.
  - Notes: Must use either > or < operators.
  - Version Added: 1.9

- **has_active_resistance**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    has_active_resistance = yes
    ```
  - Description: Checks if the current scope has non-zero resistance.
  - Version Added: 1.9

- **has_resistance**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    has_resistance = yes
    ```
  - Description: Checks if the current scope has resistance.
  - Version Added: 1.9

- **resistance**
  - Parameters:
    ```text
    <int>
    The amount to compare with.
    ```
  - Example:
    ```text
    resistance > 50
    ```
  - Description: Compares the resistance value of the current scope with the given value.
  - Notes: Must use either > or < operators.
  - Version Added: 1.9

- **resistance_speed**
  - Parameters:
    ```text
    <int>
    The amount to compare with.
    ```
  - Example:
    ```text
    resistance_speed > 50
    ```
  - Description: Compares the resistance speed of the current scope with the given value.
  - Notes: Must use either > or < operators.
  - Version Added: 1.9

- **resistance_target**
  - Parameters:
    ```text
    <int>
    The amount to compare with.
    ```
  - Example:
    ```text
    resistance_target > 50
    ```
  - Description: Compares the target resistance value of the current scope with the given value.
  - Notes: Must use either > or < operators.
  - Version Added: 1.9

- **has_occupation_modifier**
  - Parameters:
    ```text
    <token>
    The occupation modifier to check.
    ```
  - Example:
    ```text
    has_occupation_modifier = modifier_name
    ```
  - Description: Checks if the current scope has an occupation modifier, changing resistance/compliance.
  - Version Added: 1.9

- **occupation_law**
  - Parameters:
    ```text
    <token>
    The occupation law to check.
    ```
  - Example:
    ```text
    occupation_law = law_name
    ```
  - Description: Checks if the current scope has an occupation law.
  - Notes: Can also be used in country scope.
  - Version Added: 1.9

- **occupied_country_tag**
  - Parameters:
    ```text
    <tag>
    The occupation tag to check.
    ```
  - Example:
    ```text
    occupied_country_tag = POL
    ```
  - Description: Checks which country creates resistance.
  - Version Added: 1.9

## Character scope

Can be used in **Character** scope.

### General

- **is_character**
  - Parameters:
    ```text
    <scope>
    Character ID.
    ```
  - Example:
    ```text
    is_character = POL_test_character
    ```
  - Description: Checks if the current character's token matches up with the specified one.
  - Version Added: 1.11

- **can_be_country_leader**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    can_be_country_leader = yes
    ```
  - Description: Checks if the character in the current scope has a country leader role, active or non-active.
  - Version Added: 1.11

- **is_country_leader**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    is_country_leader = yes
    ```
  - Description: Checks if the character in the current scope is the active country leader.
  - Version Added: 1.11

- **is_unit_leader**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    is_unit_leader = yes
    ```
  - Description: Checks if the character in the current scope has an active unit leader (Army/Navy leader) role.
  - Version Added: 1.11

- **is_advisor**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    is_advisor = yes
    ```
  - Description: Checks if the character in the current scope has an advisor role (includes advisors/theorists/high command).
  - Version Added: 1.11

- **is_air_chief**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    is_air_chief = yes
    ```
  - Description: Checks if the character in the current scope is selected as an air chief.
  - Notes: Prior to 1.12, checked if the character had a role within the slot, regardless of being selected.
  - Version Added: 1.11

- **is_army_chief**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    is_army_chief = yes
    ```
  - Description: Checks if the character in the current scope is selected as an army chief.
  - Notes: Prior to 1.12, checked if the character had a role within the slot, regardless of being selected.
  - Version Added: 1.11

- **is_army_leader**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    is_army_leader = yes
    ```
  - Description: Checks if the character in the current scope has an army leader (General/Field Marshal) role.
  - Version Added: 1.11

- **is_navy_chief**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    is_navy_chief = yes
    ```
  - Description: Checks if the character in the current scope is selected as a navy chief.
  - Notes: Prior to 1.12, checked if the character had a role within the slot, regardless of being selected.
  - Version Added: 1.11

- **is_navy_leader**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    is_navy_leader = yes
    ```
  - Description: Checks if the character in the current scope has an navy leader (Admiral) role.
  - Version Added: 1.11

- **is_high_command**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    is_high_command = yes
    ```
  - Description: Checks if the character in the current scope is selected as high command.
  - Notes: Prior to 1.12, checked if the character had a role within the slot, regardless of being selected.
  - Version Added: 1.11

- **is_corps_commander**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    is_corps_commander = yes
    ```
  - Description: Checks if the character in the current scope is a corps commander.
  - Version Added: 1.11

- **is_operative**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    is_operative = yes
    ```
  - Description: Checks if the character in the current scope is an operative.
  - Version Added: 1.11

- **is_political_advisor**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    is_political_advisor = yes
    ```
  - Description: Checks if the character in the current scope is selected as a political advisor.
  - Notes: Prior to 1.12, checked if the character had a role within the slot, regardless of being selected.
  - Version Added: 1.11

- **is_theorist**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    is_theorist = yes
    ```
  - Description: Checks if the character in the current scope is selected as a theorist.
  - Notes: Prior to 1.12, checked if the character had a role within the slot, regardless of being selected.
  - Version Added: 1.11

- **is_character_slot**
  - Parameters:
    ```text
    <string>
    The advisor slot to check.
    ```
  - Example:
    ```text
    is_character_slot = political_advisor
    ```
  - Description: Checks if the character in the current scope has a role within the specified character slot
  - Notes:
    ```text
    Character slots are defined within
    /Hearts of Iron IV/common/idea_tags/*.txt
    .
    ```
  - Version Added: 1.11

- **has_air_ledger**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    has_air_ledger = yes
    ```
  - Description: Checks if the character in the current scope has an air ledger.
  - Version Added: 1.11

- **has_army_ledger**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    has_army_ledger = yes
    ```
  - Description: Checks if the character in the current scope has an army ledger.
  - Version Added: 1.11

- **has_navy_ledger**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    has_navy_ledger = yes
    ```
  - Description: Checks if the character in the current scope has an navy ledger.
  - Version Added: 1.11

- **has_character_flag**
  - Parameters:
    ```text
    <string>
    The flag to check for.
    ```
  - Example:
    ```text
    has_character_flag = my_flag
    ```
  - Description: Checks if the current scope has the specified flag.
  - Version Added: 1.11

- **has_character_flag**
  - Parameters:
    ```text
    flag = <string>
    The flag to check.
    value = <int>
    The flag value to check for. Optional.
    date = <date>
    The flag creation date to check for. Optional.
    days = <int>
    The duration the flag existed for. Optional.
    ```
  - Example:
    ```text
    has_character_flag = {
        flag = my_flag
        days > 30
        date > 1936.6.1
        value > 0
    }
    ```
  - Description: Compares the specified flag's last set date, days since last set, and/or value.
  - Notes:
    ```text
    If not set, the value comparison is
    >0
    .
    value
    is limited between -32768 and 32767.
    ```
  - Version Added: 1.11

- **has_trait**
  - Parameters:
    ```text
    <trait>
    The trait to check for.
    ```
  - Example:
    ```text
    has_trait = really_good_boss
    ```
  - Description: Checks if the current scope has the specified trait.
  - Version Added: 1.5

- **has_id**
  - Parameters:
    ```text
    <int>
    The id to check for.
    ```
  - Example:
    ```text
    has_id = 1
    ```
  - Description: Checks if the current character has the specificed ID.
  - Version Added: 1.5

### Advisors

These triggers are to be used specifically for advisors.

- **is_hired_as_advisor**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    is_hired_as_advisor = yes
    ```
  - Description: Checks if the current character is activated as an advisor in any slot.
  - Version Added: 1.12.10

- **not_already_hired_except_as**
  - Parameters:
    ```text
    <slot>
    The slot to check in.
    ```
  - Example:
    ```text
    not_already_hired_except_as = political_advisor
    ```
  - Description: Checks if the current character is not hired, with the exception of the specified slot.
  - Version Added: 1.11

- **advisor_can_be_fired**
  - Parameters:
    ```text
    <bool>
    Boolean.
    OR
    slot = <slot>
    The slot to check in.
    ```
  - Example:
    ```text
    advisor_can_be_fired = no
    ```
  - Example:
    ```text
    advisor_can_be_fired = {
        slot = political_advisor
    }
    ```
  - Description:
    ```text
    Checks if the current character's
    can_be_fired
    attribute is set or not within a certain slot.
    ```
  - Notes: If an advisor is available in multiple slots, the long version is mandatory to use.
  - Version Added: 1.12.8

- **has_advisor_role**
  - Parameters:
    ```text
    <slot>
    The slot to check in.
    ```
  - Example:
    ```text
    has_advisor_role = political_advisor
    ```
  - Description: Checks if the character in scope has an advisor role for the given slot.
  - Notes:
    ```text
    Possible
    advisor
    role slots.
    ```
  - Version Added: ???

### Country leaders

These triggers are to be used specifically for country leaders.

- **has_ideology**
  - Parameters:
    ```text
    <ideology>
    The sub-ideology to check for.
    ```
  - Example:
    ```text
    has_ideology = liberalism
    ```
  - Description: Checks if the current character has the specificed sub-ideology assigned.
  - Version Added: 1.11

- **has_ideology_group**
  - Parameters:
    ```text
    <ideology>
    The ideology to check for.
    ```
  - Example:
    ```text
    has_ideology_group = democratic
    ```
  - Description: Checks if the current character has the specificed ideology assigned.
  - Version Added: 1.11

### Unit leaders

These triggers are to be used specifically for unit leaders, i.e. generals and admirals.

- **has_unit_leader_flag**
  - Parameters:
    ```text
    <string>
    The flag to check for.
    ```
  - Example:
    ```text
    has_unit_leader_flag = my_flag
    ```
  - Description: Checks if the current scope has the specified flag.
  - Notes: Deprecated. Use has_character_flag instead.
  - Version Added: 1.5

- **has_unit_leader_flag**
  - Parameters:
    ```text
    flag = <string>
    The flag to check.
    value = <int>
    The flag value to check for. Optional.
    date = <date>
    The flag creation date to check for. Optional.
    days = <int>
    The duration the flag existed for. Optional.
    ```
  - Example:
    ```text
    has_unit_leader_flag = {
        flag = my_flag
        days > 30
        date > 1936.6.1
        value > 0
    }
    ```
  - Description: Compares the specified flag's last set date, days since last set, and/or value.
  - Notes:
    ```text
    Deprecated. Use has_character_flag instead. If not set, the value comparison is
    >0
    .
    value
    is limited between -32768 and 32767.
    ```
  - Version Added: 1.5

- **is_leading_army**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    is_leading_army = yes
    ```
  - Description: Checks if the current scope is leading a single army.
  - Version Added: 1.5

- **is_leading_army_group**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    is_leading_army_group = yes
    ```
  - Description: Checks if the current scope is leading an army group.
  - Version Added: 1.5

- **is_leading_volunteer_group**
  - Parameters:
    ```text
    <tag>
    Country tag.
    ```
  - Example:
    ```text
    is_leading_volunteer_group = POL
    ```
  - Description: Checks if the current scope is leading a volunteer army within the specified country.
  - Notes: If the target country is in a civil war, this will only be valid for one side.
  - Version Added: 1.11

- **is_leading_volunteer_group_with_original_country**
  - Parameters:
    ```text
    <tag>
    Country tag.
    ```
  - Example:
    ```text
    is_leading_volunteer_group_with_original_country = POL
    ```
  - Description: Checks if the current scope is leading a volunteer army within a country of the specified original tag.
  - Notes: If the target country is in a civil war, this will only be valid for each side.
  - Version Added: 1.11

- **is_field_marshal**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    is_field_marshal = yes
    ```
  - Description: Checks if the current scope is a Field Marshal.
  - Version Added: 1.5

- **is_assigned**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    is_assigned = yes
    ```
  - Description: Checks if the current scope is an assigned unit leader.
  - Version Added: 1.5

- **can_select_trait**
  - Parameters:
    ```text
    <string>
    The trait to check for.
    ```
  - Example:
    ```text
    can_select_trait = offensive_doctrine
    ```
  - Description: Checks if the current scope can select the specified trait.
  - Version Added: 1.5

- **has_ability**
  - Parameters:
    ```text
    <string>
    The ability to check for.
    ```
  - Example:
    ```text
    has_ability = glider_planes
    ```
  - Description: Checks if the current scope has the specified unit leader ability.
  - Version Added: 1.5

- **skill**
  - Parameters:
    ```text
    <int>
    The amount to check for.
    ```
  - Example:
    ```text
    skill > 1
    ```
  - Description: Checks if the current scope has a Skill above the specified amount.
  - Notes: Must use either > or < operators.
  - Version Added: 1.5

- **skill_advantage**
  - Parameters:
    ```text
    <int>
    The amount to check for.
    ```
  - Example:
    ```text
    skill_advantage > 1
    ```
  - Description: Checks if the current scope has a Skill advantage above the specified amount in against an enemy unit leader whilst in combat.
  - Notes: Must use either > or < operators.
  - Version Added: 1.5

- **planning_skill_level**
  - Parameters:
    ```text
    <int>
    The amount to check for.
    ```
  - Example:
    ```text
    planning_skill_level > 1
    ```
  - Description: Checks if the current scope has a Planning skill above the specified amount.
  - Notes: Must use either > or < operators.
  - Version Added: 1.5

- **logistics_skill_level**
  - Parameters:
    ```text
    <int>
    The amount to check for.
    ```
  - Example:
    ```text
    logistics_skill_level > 1
    ```
  - Description: Checks if the current scope has a Logistics skill above the specified amount.
  - Notes: Must use either > or < operators.
  - Version Added: 1.5

- **defense_skill_level**
  - Parameters:
    ```text
    <int>
    The amount to check for.
    ```
  - Example:
    ```text
    defense_skill_level > 1
    ```
  - Description: Checks if the current scope has a Defense skill above the specified amount.
  - Notes: Must use either > or < operators.
  - Version Added: 1.5

- **attack_skill_level**
  - Parameters:
    ```text
    <int>
    The amount to check for.
    ```
  - Example:
    ```text
    attack_skill_level > 1
    ```
  - Description: Checks if the current scope has a Attack skill above the specified amount.
  - Notes: Must use either > or < operators.
  - Version Added: 1.5

- **average_stats**
  - Parameters:
    ```text
    <int>
    The amount to check for.
    ```
  - Example:
    ```text
    average_stats > 5
    ```
  - Description: Checks if the current scope has an average skill above the specified amount.
  - Notes: Must use either > or < operators.
  - Version Added: 1.5

- **is_border_war**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    is_border_war = yes
    ```
  - Description: Checks if the current socpe is in a border war.
  - Version Added: 1.5

- **num_units**
  - Parameters:
    ```text
    <int>
    The amount to check for.
    ```
  - Example:
    ```text
    num_units > 5
    ```
  - Description: Checks if the current scope is commanding the specified amount of divisions.
  - Notes: Must use either > or < operators.
  - Version Added: 1.5

- **is_exiled_leader**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    is_exiled_leader = yes
    ```
  - Description: Checks if the current scope is a general from an exiled country.
  - Version Added: 1.6

- **is_exiled_leader_from**
  - Parameters:
    ```text
    <tag>
    Country.
    ```
  - Example:
    ```text
    is_exiled_leader_from = POL
    ```
  - Description: Checks if the current scope is a general from the specified exiled country.
  - Version Added: 1.6

- **is_female**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    is_female = yes
    ```
  - Description: Checks if the current scope is female.
  - Notes: Works for aces.
  - Version Added: 1.9

- **is_leading_army_in_province**
  - Parameters: <province id>
  - Example:
    ```text
    is_leading_army_in_province = 1234
    ```
  - Description: Checks if the current unit leader is leading an army that has any division in a specific province
  - Version Added: 1.17

### Operatives

These triggers only work for operatives.

- **has_nationality**
  - Parameters:
    ```text
    <tag>
    The nationality to check.
    ```
  - Example:
    ```text
    has_nationality = POL
    ```
  - Description: Checks if the current operative has the nationality.
  - Version Added: 1.9

- **is_operative_captured**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    is_operative_captured = yes
    ```
  - Description: Checks if the current scope is captured.
  - Version Added: 1.9

- **operative_leader_mission**
  - Parameters:
    ```text
    <token>
    Mission.
    ```
  - Example:
    ```text
    operative_leader_mission = mission_name
    ```
  - Description: Checks if the current scope is on the given mission.
  - Version Added: 1.9

- **operative_leader_operation**
  - Parameters:
    ```text
    <token>
    Operation.
    ```
  - Example:
    ```text
    operative_leader_operation = operation_name
    ```
  - Description: Checks if the current scope is on the given operation.
  - Version Added: 1.9

### Scientists

These triggers only work for scientists.

- **has_scientist_level**
  - Parameters:
    ```text
    level = <int>
    Level to check.
    specialization = <specialization_token>
    Specialization.
    ```
  - Example:
    ```text
    has_scientist_level = {
      level > 2
      specialization = specialization_nuclear
    }
    ```
  - Description: Checks if the scientist of the character in scope matches the skill level condition for a specialization. Supports < > = operators.
  - Version Added: 1.15

- **is_active_scientist**
  - Parameters: <bool>
  - Example:
    ```text
    is_scientist_active = yes
    ```
  - Description: Checks if the scientist of the character in scope is assigned to a project.
  - Version Added: 1.15

- **is_scientist_injured**
  - Parameters: <bool>
  - Example:
    ```text
    is_scientist_injured = yes
    ```
  - Description: Checks if the scientist of the character in scope is injured.
  - Version Added: 1.15

## Combat

These triggers are used within the combatant scope. Some trigger blocks in abilities, combat tactics, and unit leader traits check this, and it's impossible to access elsewhere.

- **hardness**
  - Parameters:
    ```text
    <float>
    The amount to check for.
    ```
  - Example:
    ```text
    hardness > 0.5
    ```
  - Description: Checks if the current scope has the specified amount of hardness.
  - Notes: Must use either > or < operators.
  - Version Added: 1.0

- **armor**
  - Parameters:
    ```text
    <float>
    The amount to check for.
    ```
  - Example:
    ```text
    armor > 0.5
    ```
  - Description: Checks if the current scope has the specified amount of armor units.
  - Notes: Must use either > or < operators.
  - Version Added: 1.0

- **dig_in**
  - Parameters:
    ```text
    <float>
    The amount to check for.
    ```
  - Example:
    ```text
    dig_in > 0.5
    ```
  - Description: Checks if the current scope has the specified amount of Dig In bonus.
  - Notes: Must use either > or < operators.
  - Version Added: 1.0

- **min_planning**
  - Parameters:
    ```text
    <float>
    The amount to check for.
    ```
  - Example:
    ```text
    min_planning > 0.5
    ```
  - Description: Checks if the current scope has the specified amount of planning.
  - Notes: Must use either > or < operators.
  - Version Added: 1.0

- **fastest_unit**
  - Parameters:
    ```text
    <float>
    The speed in km/h to check for.
    ```
  - Example:
    ```text
    fastest_unit > 12
    ```
  - Description: Checks if the current scope has a unit with the specified speed.
  - Notes: Must use either > or < operators.
  - Version Added: 1.0

- **temperature**
  - Parameters:
    ```text
    <float>
    The temperature in celsius to check for.
    ```
  - Example:
    ```text
    temperature > 20
    ```
  - Description: Checks if the current scope is in a province with a temperature above the specified amount.
  - Notes: Must use either > or < operators.
  - Version Added: 1.0

- **reserves**
  - Parameters:
    ```text
    <float>
    The amount to check for.
    ```
  - Example:
    ```text
    reserves > 10
    ```
  - Description: Checks if the current scope has the specified amount of reserves waiting.
  - Notes: Must use either > or < operators.
  - Version Added: 1.0

- **has_combat_modifier**
  - Parameters:
    ```text
    <string>
    The modifier to check for.
    ```
  - Example:
    ```text
    has_combat_modifier = river_crossing
    ```
  - Description: Checks if the current scope has the specified combat modifier.
  - Version Added: 1.0

- **is_fighting_in_terrain**
  - Parameters:
    ```text
    <string>
    The terrain to check for.
    ```
  - Example:
    ```text
    is_fighting_in_terrain = desert
    ```
  - Description: Checks if the current scope is fighting in the specified terrain.
  - Version Added: 1.0

- **is_fighting_in_weather**
  - Parameters:
    ```text
    <string>
    The weather to check for.
    OR
    { <string> <...> <string> }
    The weather to check for in an OR statement.
    ```
  - Example:
    ```text
    is_fighting_in_weather = sandstorm
    ```
  - Example:
    ```text
    is_fighting_in_weather = { rain_light rain_heavy }
    ```
  - Description: Checks if the current scope is fighting in the specified weather.
  - Version Added: 1.0

- **phase**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    phase = yes
    ```
  - Description: Checks if the current scope is in phase.
  - Version Added: 1.0

- **recon_advantage**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    recon_advantage > 0
    ```
  - Description: Checks if the current scope has x recon advantage.
  - Version Added: 1.0

- **night**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    night = yes
    ```
  - Description: Checks if the current scope is fighting at night.
  - Version Added: 1.0

- **frontage_full**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    frontage_full = yes
    ```
  - Description: Checks if the current scope has a full combat width.
  - Version Added: 1.0

- **has_flanked_opponent**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    has_flanked_opponent = yes
    ```
  - Description: Checks if the current scope has flanked their opponent.
  - Version Added: 1.0

- **has_max_planning**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    has_max_planning = yes
    ```
  - Description: Checks if the current scope has the maximum planning bonus.
  - Version Added: 1.0

- **has_reserves**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    has_reserves = yes
    ```
  - Description: Checks if the current scope has any reserves waiting.
  - Version Added: 1.0

- **is_amphibious_invasion**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    is_amphibious_invasion = yes
    ```
  - Description: Checks if the current scope is performing an amphibious invasion.
  - Version Added: 1.0

- **is_attacker**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    is_attacker = yes
    ```
  - Description: Checks if the current scope is attacking.
  - Version Added: 1.0

- **is_defender**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    is_defender = yes
    ```
  - Description: Checks if the current scope is defending.
  - Version Added: 1.0

- **is_winning**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    is_winning = yes
    ```
  - Description: Checks if the current scope is winning their battle.
  - Version Added: 1.0

- **is_fighting_air_units**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    is_fighting_air_units = yes
    ```
  - Description: Checks if the current scope is fighting air units.
  - Version Added: 1.0

- **less_combat_width_than_opponent**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    less_combat_width_than_opponent = yes
    ```
  - Description: Checks if the current scope is fighting with less combat width than their opponent.
  - Version Added: 1.0

- **has_carrier_airwings_on_mission**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    has_carrier_airwings_on_mission = yes
    ```
  - Description: Checks if the current scope has carrier airwings on a mission.
  - Version Added: 1.0

- **has_carrier_airwings_in_own_combat**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    has_carrier_airwings_in_own_combat = yes
    ```
  - Description: Checks if the current scope has carrier airwings in their own combat.
  - Version Added: 1.0

- **has_artillery_ratio**
  - Parameters: <float>
  - Example:
    ```text
    has_artillery_ratio > 0.1
    ```
  - Description: Check that ratio of atrillery battalions in the composition of a side of combating troops are over a certain level.
  - Version Added: ???

- **has_unit_type**
  - Parameters: <unit_type>
  - Example:
    ```text
    has_unit_type = amphibious_mechanized
    ```
  - Description: Check if the combatant has at least one of the provided unit types.
  - Version Added: ???

## Division scope

Can be used in **Division** scope.

- **division_has_majority_template**
  - Parameters:
    ```text
    <battalion>
    Battalion to check for.
    ```
  - Example:
    ```text
    division_has_majority_template = light_armor
    ```
  - Description: Checks if the current scope is majority made up of the specified battalion.
  - Notes:
    ```text
    Battalions are defined within
    /Hearts of Iron IV/common/units/*.txt
    files.
    ```
  - Version Added: 1.12

- **division_has_battalion_in_template**
  - Parameters:
    ```text
    <battalion>
    Battalion to check for.
    ```
  - Example:
    ```text
    division_has_battalion_in_template = light_armor
    ```
  - Description: Checks if the current scope has any battalions of the type in the template.
  - Notes:
    ```text
    Battalions are defined within
    /Hearts of Iron IV/common/units/*.txt
    files.
    ```
  - Version Added: 1.12

- **unit_strength**
  - Parameters:
    ```text
    <float>
    The amount to check for.
    ```
  - Example:
    ```text
    unit_strength < 0.3
    ```
  - Description: Checks the current strength of the unit on the scale from 0 to 1.
  - Notes: Must use either the < or > operator.
  - Version Added: 1.12

- **unit_organization**
  - Parameters:
    ```text
    <float>
    The amount to check for.
    ```
  - Example:
    ```text
    unit_organization < 0.3
    ```
  - Description: Checks the current organisation of the unit on the scale from 0 to 1.
  - Notes: Must use either the < or > operator.
  - Version Added: 1.12

- **is_unit_template_reserves**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    is_unit_template_reserves = yes
    ```
  - Description: Checks if the current division has the supply priority set to 'Reserves', i.e. the lowest priority.
  - Notes: Must use either the < or > operator.
  - Version Added: 1.12

- **has_officer_name**
  - Parameters:
    ```text
    <string>
    The localization key to check.
    ```
  - Example:
    ```text
    has_officer_name = FIN_nikke_parmi
    ```
  - Description: Checks if the current division has an officer with the provided name key.

## MIO scope

Can be used in **Military-industrial organisation** scope.

- **is_military_industrial_organization**
  - Parameters:
    ```text
    <token>
    MIO to check.
    ```
  - Example:
    ```text
    is_military_industrial_organization = my_mio_token
    ```
  - Description: Checks if the currently-scoped MIO matches the input token.
  - Version Added: 1.13

- **is_mio_visible**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    is_mio_visible = yes
    ```
  - Description: Checks if the currently-scoped MIO is visible.
  - Version Added: 1.13

- **is_mio_available**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    is_mio_available = yes
    ```
  - Description: Checks if the currently-scoped MIO is visible.
  - Version Added: 1.13

- **is_mio_assigned_to_task**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    is_mio_assigned_to_task = yes
    ```
  - Description: Checks if the currently-scoped MIO is assigned to a task.
  - Version Added: 1.13

- **has_mio_size**
  - Parameters:
    ```text
    <int>
    Integer.
    ```
  - Example:
    ```text
    has_mio_size > 3
    ```
  - Description: Checks the size of the MIO.
  - Notes:
    ```text
    Accepts
    variables
    . May use < or >.
    ```
  - Version Added: 1.13

- **has_mio_trait**
  - Parameters:
    ```text
    <token>
    Trait to check.
    OR
    trait = <token>
    Trait to check.
    ```
  - Example:
    ```text
    has_mio_trait = my_trait_token
    ```
  - Example:
    ```text
    has_mio_trait = {
        token = my_trait_token
    }
    ```
  - Description: Checks whether the MIO has the target trait in its list.
  - Version Added: 1.13

- **is_mio_trait_available**
  - Parameters:
    ```text
    <token>
    Trait to check.
    OR
    trait = <token>
    Trait to check.
    check_mio_parent_completed = <bool>
    Whether to check if the parent traits are complete. True by default.
    check_mio_mutually_exclusive = <bool>
    Whether to check if any mutually exclusive traits are complete. True by default.
    ```
  - Example:
    ```text
    is_mio_trait_available = my_trait_token
    ```
  - Example:
    ```text
    is_mio_trait_available = {
        token = my_trait_token
        check_mio_parent_completed = no
    }
    ```
  - Description: Checks whether the MIO has the target trait in its list and whether it's available.
  - Version Added: 1.13

- **is_mio_trait_completed**
  - Parameters:
    ```text
    <token>
    Trait to check.
    OR
    trait = <token>
    Trait to check.
    ```
  - Example:
    ```text
    is_mio_trait_completed = my_trait_token
    ```
  - Example:
    ```text
    is_mio_trait_completed = {
        token = my_trait_token
    }
    ```
  - Description: Checks whether the MIO has the target trait in its list and whether it's completed.
  - Version Added: 1.13

- **has_mio_number_of_completed_traits**
  - Parameters:
    ```text
    <int>
    Integer.
    ```
  - Example:
    ```text
    has_mio_number_of_completed_traits < 2
    ```
  - Description: Checks the amount of unlocked MIO traits.
  - Notes:
    ```text
    Accepts
    variables
    . May use < or >.
    ```
  - Version Added: 1.13

- **has_mio_flag**
  - Parameters:
    ```text
    <string>
    The flag to check.
    ```
  - Example:
    ```text
    has_mio_flag = my_flag
    ```
  - Description: Checks if the current scope has the specified flag.
  - Version Added: 1.13

- **has_mio_flag**
  - Parameters:
    ```text
    flag = <string>
    The flag to check.
    value = <int>
    The flag value to check for. Optional.
    date = <date>
    The flag creation date to check for. Optional.
    days = <int>
    The duration the flag existed for. Optional.
    ```
  - Example:
    ```text
    has_mio_flag = {
        flag = my_flag
        days > 30
        date > 1936.6.1
        value > 0
    }
    ```
  - Description: Compares the specified flag's last set date, days since last set, and/or value.
  - Notes:
    ```text
    If not set, the value comparison is
    >0
    .
    value
    is limited between -32768 and 32767.
    ```
  - Version Added: 1.13

- **has_mio_policy**
  - Parameters:
    ```text
    <token>
    Policy to check.
    ```
  - Example:
    ```text
    has_mio_policy = my_policy_token
    ```
  - Description: Checks if the currently-scoped MIO has the target policy allowed.
  - Version Added: 1.13

- **has_mio_policy_active**
  - Parameters:
    ```text
    <token>
    Policy to check.
    ```
  - Example:
    ```text
    has_mio_policy_active = my_policy_token
    ```
  - Description: Checks if the currently-scoped MIO has the target policy active.
  - Version Added: 1.13

- **has_mio_research_category**
  - Parameters:
    ```text
    <token>
    Category to check.
    ```
  - Example:
    ```text
    has_mio_research_category = my_research_category_token
    ```
  - Description: Checks if the currently-scoped MIO has the target research category.
  - Version Added: 1.13

- **has_mio_equipment_type**
  - Parameters:
    ```text
    <token>
    Type to check.
    ```
  - Example:
    ```text
    has_mio_equipment_type = my_equipment_type_token
    ```
  - Description: Checks if the currently-scoped MIO has the target equipment types.
  - Notes:
    ```text
    The possible equipment types are defined in
    script_enum_equipment_bonus_type
    (in
    /Hearts of Iron IV/common/script_enums.txt
    ) and in
    /Hearts of Iron IV/common/equipment_groups.txt
    files.
    ```
  - Version Added: 1.13

## Contract scope

Can be used in **purchase contract** scope.

- **contract_contains_equipment**
  - Parameters:
    ```text
    <token>
    Type to check.
    ```
  - Example:
    ```text
    contract_contains_equipment = infantry_equipment
    ```
  - Description: Checks if the currently-scoped purchase contract contains an equipment type.
  - Notes: May use equipment types, equipment archetypes, or types of equipment archetypes.
  - Version Added: 1.13

- **deal_completion**
  - Parameters:
    ```text
    <decimal>
    Progress to compare with.
    ```
  - Example:
    ```text
    deal_completition > 0.6
    ```
  - Description: Checks the deal completion with the target value.
  - Notes: May use < or >. On the scale from 0 to 1.
  - Version Added: 1.13

- **seller**
  - Parameters:
    ```text
    <country>
    Country to check.
    ```
  - Example:
    ```text
    seller = BHR
    ```
  - Description: Checks the seller in the current purchase contract.
  - Version Added: 1.13

- **buyer**
  - Parameters:
    ```text
    <country>
    Country to check.
    ```
  - Example:
    ```text
    buyer = OMA
    ```
  - Description: Checks the buyer in the current purchase contract.
  - Version Added: 1.13

## Special projects

- **has_project_flag**
  - Parameters:
    ```text
    <string>
    The flag to check for.
    OR
    flag = <string>
    The flag to check.
    value = <int>
    The flag value to check for. Optional.
    date = <date>
    The flag creation date to check for. Optional.
    days = <int>
    The duration the flag existed for. Optional.
    ```
  - Example:
    ```text
    has_project_flag = my_flag
    ```
  - Example:
    ```text
    has_project_flag = {
      flag = my_flag
      value < 12
      date > 1936.3.25
      days > 365
    }
    ```
  - Description: Check if flag has been set within the special project in scope. May checks on the value or date/days since last modified date.
  - Notes: If not set, the value comparison is >0. value is limited between -32768 and 32767.
  - Version Added: 1.15

## Meta triggers

Meta triggers are a system added with 1.6 with ![Man the Guns](media/triggers-hearts-of-iron-4-wiki_58368ba2e5__img31.png)Man the Guns used in the exact same manner as [meta effects](<Effect - Hearts of Iron 4 Wiki.md#meta-effects>): in order to tie a trigger block to a dynamic localisation entry. This is usually used in conjunction with [scripted localisation](<Localisation - Hearts of Iron 4 Wiki.md#scripted-localisation>) for non-numerical checks. This also can serve in order to place a variable check where one is not possible.  
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

## Scripted triggers

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
```

This can then be used in any other trigger block, such as a national focus' available section:

```text
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

### Diplomacy scripted triggers

Diplomacy scripted triggers fall into two mutually exclusive groups: deciding availability and deciding visibility. By default, these are defined in /Hearts of Iron IV/common/scripted\_triggers/diplomacy\_scripted\_triggers.txt and /Hearts of Iron IV/common/scripted\_triggers/00\_diplo\_action\_valid\_triggers.txt respectively. While it is possible to also use them as regular scripted triggers, they will also modify the prerequisites of being able to do a diplomatic action between 2 countries.

A diplomacy scripted trigger is identified by the naming pattern of `DIPLOMACY_<action>_ENABLE_TRIGGER` for availability, such as `DIPLOMACY_GUARANTEE_ENABLE_TRIGGER`, and `is_diplomatic_action_valid_<action>` for visibility, such as `is_diplomatic_action_valid_stage_coup`. In the base game, diplomacy scripted triggers are used to implement the game rules and add some country-specific exceptions, such as the ![Flag of United Kingdom](media/triggers-hearts-of-iron-4-wiki_58368ba2e5__img33.png) United Kingdom being unable to release its colonies with the ![Man the Guns](media/triggers-hearts-of-iron-4-wiki_58368ba2e5__img34.png)Man the Guns DLC. Checking the base game's contents beforehand or copying it to the mod would ensure that the mod won't accidentally break any existing game rules.

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

### Resistance initiation triggers

The behaviour of resistance being automatically initiated is decided by the `should_initiate_resistance` scripted trigger, by default defined in /Hearts of Iron IV/common/scripted\_triggers/00\_resistance\_initiate\_triggers.txt. If it is unfulfilled, the resistance will never initiate unless forced via the [the force\_enable\_resistance effect](<Effect - Hearts of Iron 4 Wiki.md#force-enable-resistance>). Likewise, the resistance will always occur if it's true unless forcefully disabled.

The scripted trigger's behaviour can be overwritten with state-specific scripted triggers, which should be named `should_initiate_resistance` with the list of state IDs suffixed at the end, separated by underscores. For example, this ensures that when a state 321 or 123 is controlled by the ![Flag of United Kingdom](media/triggers-hearts-of-iron-4-wiki_58368ba2e5__img35.png) United Kingdom, resistance would get initiated if and only if they're national territory of ![Flag of France](media/triggers-hearts-of-iron-4-wiki_58368ba2e5__img36.png) France; otherwise, the normal behaviour is used:

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

### Useful scripted triggers

These scripted triggers are defined in base game and might be useful to keep in the mod to cut down on the amount of code. As scripted triggers, all of these use a boolean value as argument.

- **can_ROOT_get_wargoal_on_THIS**
  - Scope: Country
  - Example:
    ```text
    can_ROOT_get_wargoal_on_THIS = yes
    ```
  - Description: Checks if ROOT can obtain a wargoal on the current scope.
  - Notes: To evaluate as true, the current scope must exist, not share a faction with ROOT, and not be a subject of ROOT.

- **is_free_or_subject_of_root**
  - Scope: Country
  - Example:
    ```text
    is_free_or_subject_of_root = yes
    ```
  - Description: Checks if the current scope is either independent or a subject of ROOT.

- **has_same_ideology**
  - Scope: Country
  - Example:
    ```text
    has_same_ideology = yes
    ```
  - Description: Checks if the current scope has the same ideology as ROOT.
  - Notes:
    ```text
    Needs modifying if there are custom ideologies. Equivalent to
    has_government = ROOT
    for base game ideologies.
    ```

- **is_enemy_ideology**
  - Scope: Country
  - Example:
    ```text
    is_enemy_ideology = yes
    ```
  - Description: Checks if the current scope has an ideology that is considered enemy to ROOT's.
  - Notes:
    ```text
    Communism
    ,
    Democracy
    , and
    Fascism
    are considered enemy to each other.
    ```

- **has_ROOT_at_least_1_div_in_current_state_scope**
  - Scope: State
  - Example:
    ```text
    has_ROOT_at_least_1_div_in_current_state_scope = yes
    ```
  - Description: Checks if ROOT has at least one division in the current scope.

- **controls_or_subject_of**
  - Scope: State
  - Example:
    ```text
    controls_or_subject_of = yes
    ```
  - Description: Checks if the current state is controlled by ROOT or a subject of ROOT.

- **is_controlled_by_ROOT_or_ally**
  - Scope: State
  - Example:
    ```text
    is_controlled_by_ROOT_or_ally = yes
    ```
  - Description: Checks if the current state is controlled by ROOT, a subject of ROOT, or a country in the same faction as ROOT.

- **owns_or_subject_of**
  - Scope: State
  - Example:
    ```text
    owns_or_subject_of = yes
    ```
  - Description: Checks if the current scope is owned by ROOT or a subject of ROOT.

## References and notes

**[^](#ref-a)** **a:** Triggers are able to set and modify temporary variables. This temporary variable itself may be then used separately to change the game's state, such as in a MTTH block or if the trigger block is used in some [effect](<Effect - Hearts of Iron 4 Wiki.md>)'s `limit = { ... }` (most commonly [if statements](<Effect - Hearts of Iron 4 Wiki.md#if>) or [effect scope limits](<Scopes - Hearts of Iron 4 Wiki.md#scope-limits>)), though the usage of the variable to change the game's state is not a trigger by itself.

1. [↑](#cite-ref-1) [[Modding] Achievement for mods](https://forum.paradoxplaza.com/forum/index.php?threads/1544899)  
   [Tutorial to write achievements files in your mod](https://forum.paradoxplaza.com/forum/index.php?threads/1544901)
2. [↑](#cite-ref-2) [How does any\_war\_score work?](https://forum.paradoxplaza.com/forum/index.php?threads/1124460)
3. [↑](#cite-ref-3) [forum:1356228/#post-26361808](https://forum.paradoxplaza.com/forum/index.php?threads/1356228/#post-26361808)
4. [↑](#cite-ref-4) [HOI4 Dev Diary - Modding and Traits](https://forum.paradoxplaza.com/forum/index.php?threads/1117516)

**[Modding](<Modding - Hearts of Iron 4 Wiki.md>)**
