# Table of contents

- [Scopes](#scopes)
  - [Effect scopes](#effect-scopes)
  - [Effects with scopes](#effects-with-scopes)
  - [Dual scopes](#dual-scopes)
- [Any scope](#any-scope)
  - [General](#general)
  - [Border wars](#border-wars)
  - [Variables](#variables)
  - [Arrays](#arrays)
- [Country scope](#country-scope)
  - [General](#general)
  - [States](#states)
  - [Mana](#mana)
  - [Politics](#politics)
  - [Balance of power](#balance-of-power)
  - [Diplomacy](#diplomacy)
  - [Faction](#faction)
  - [Autonomy](#autonomy)
  - [Governments in exile](#governments-in-exile)
  - [War](#war)
  - [Resources](#resources)
  - [Buildings](#buildings)
  - [National focuses](#national-focuses)
  - [Decisions](#decisions)
  - [Missions](#missions)
  - [Technologies](#technologies)
  - [Ideas](#ideas)
  - [Units](#units)
  - [Equipment](#equipment)
  - [Military](#military)
  - [Doctrine](#doctrine)
  - [Intelligence](#intelligence)
  - [Characters](#characters)
    - [Unit leaders](#unit-leaders)
    - [Country leaders](#country-leaders)
    - [Advisors](#advisors)
    - [Scientists](#scientists)
  - [MIOs](#mios)
  - [Special Projects](#special-projects)
  - [Career profile](#career-profile)
  - [History](#history)
  - [Variable](#variable)
- [State scope](#state-scope)
  - [General](#general)
  - [Buildings](#buildings)
  - [Resistance and compliance](#resistance-and-compliance)
  - [Raids](#raids)
- [Character scope](#character-scope)
  - [General](#general)
  - [Unit leaders](#unit-leaders)
  - [Country leaders](#country-leaders)
  - [Combat](#combat)
  - [Operatives](#operatives)
- [Division scope](#division-scope)
- [MIO scope](#mio-scope)
- [Contract scope](#contract-scope)
- [Raid scope](#raid-scope)
- [Special Project scope](#special-project-scope)
- [Other scopes](#other-scopes)
- [Flow control](#flow-control)
  - [If statements](#if-statements)
  - [Random effects](#random-effects)
  - [Tooltip manipulation](#tooltip-manipulation)
- [Meta effects](#meta-effects)
- [Scripted effects](#scripted-effects)
  - [Useful scripted effects](#useful-scripted-effects)


---

Effects (also known as Commands) are used in order to affect the game dynamically from within a specific scope. They are a one-time change to the current condition of the game, **without the ability to have a lasting effect**. Instead, [modifiers](<Modifiers - Hearts of Iron 4 Wiki.md>) are used to have a continuous, everlasting effect on the game's condition that can be represented with a number. Effect blocks cannot be used to apply modifiers directly, however they can add something that can apply modifiers, most commonly with [add\_ideas](#add-ideas).

Effects are used throughout the game in numerous scopes, most commonly edited effect blocks are [national focus rewards](<National focus modding - Hearts of Iron 4 Wiki.md>), [event options](<Event modding - Hearts of Iron 4 Wiki.md>) and [decision effects](<Decision modding - Hearts of Iron 4 Wiki.md>).

Note that certain effects may take a value from a variable, i.e. `add_manpower = var:my_var` This is noted by **<variable>** in an effect's parameters. See Variables for information on the variable effects.

The list of effects may be outdated. A complete, but unsorted, list of effects can be found in /Hearts of Iron IV/documentation/effects\_documentation.html or /Hearts of Iron IV/documentation/effects\_documentation.md.

## Scopes

*Main article: [Scopes](<Scopes - Hearts of Iron 4 Wiki.md>)*

Scopes serve as special effect types that modify the entity that serves as the context for the effects being executed, such as `GER = { add_political_power = 150 }` adding 150 political power to ![Flag of Germany](media/effect-hearts-of-iron-4-wiki_ec2e2a02fa__img1.png) Germany.

### Effect scopes

These can only be used as effects; trying to use them as [triggers](<Triggers - Hearts of Iron 4 Wiki.md>) will result in nothing happening.

- **every_possible_country**
  - Usage: Always usable
  - Target type: Country
  - Example: every_possible_country = { ... }
  - Description: Executes children effects on every country that meets the limit, including those that do not exist.
  - Version Added: 1.11

- **every_country**
  - Usage: Always usable
  - Target type: Country
  - Example: every_country = { … }
  - Description: Executes contained effects on every country that meets the limit.
  - Version Added: 1.0

- **random_country**
  - Usage: Always usable
  - Target type: Country
  - Example: random_country = { … }
  - Description: Executes contained effects on a random country that meets the limit.
  - Version Added: 1.0

- **every_other_country**
  - Usage: Within country scope only
  - Target type: Country
  - Example: every_other_country = { … }
  - Description: Executes contained effects on every country that meets the limit and is not the same country as the one this is contained in.
  - Version Added: 1.0

- **random_other_country**
  - Usage: Within country scope only
  - Target type: Country
  - Example: random_other_country = { … }
  - Description: Executes contained effects on a random country that meets the limit and is not the same country as the one this is contained in.
  - Version Added: 1.0

- **every_country_with_original_tag**
  - Usage: Always usable
  - Target type: Country
  - Example:
    ```text
    every_country_with_original_tag = {
        original_tag_to_check = TAG  #required
        …                  #effects to run
    }
    ```
  - Description: Executes contained effects on every country that meets the limit and has the specified original tag.
  - Version Added: 1.9

- **random_country_with_original_tag**
  - Usage: Always usable
  - Target type: Country
  - Example:
    ```text
    random_country_with_original_tag = {
        original_tag_to_check = TAG  #required
        …                  #effects to run
    }
    ```
  - Description: Executes contained effects on a random country that meets the limit and has the specified original tag.

- **every_neighbor_country**
  - Usage: Within country scope only
  - Target type: Country
  - Example: every_neighbor_country = { … }
  - Description: Executes contained effects on every country that meets the limit and borders the country this is contained in.
  - Version Added: 1.0

- **random_neighbor_country**
  - Usage: Within country scope only
  - Target type: Country
  - Example: random_neighbor_country = { … }
  - Description: Executes contained effects on a random country that meets the limit and borders the country this is contained in.
  - Version Added: 1.0

- **every_occupied_country**
  - Usage: Within country scope only
  - Target type: Country
  - Example: every_occupied_country = { … }
  - Description: Executes contained effects on every country that meets the limit and has any core states controlled by the country this is contained in.
  - Version Added: 1.9

- **random_occupied_country**
  - Usage: Within country scope only
  - Target type: Country
  - Example: random_occupied_country = { … }
  - Description: Executes contained effects on a random country that meets the limit and has any core states controlled by the country this is contained in.
  - Version Added: 1.9

- **every_allied_country**
  - Usage: Within country scope only
  - Target type: Country
  - Example: every_allied_country = { … }
  - Description: Executes children effects on every Allied Country different from the one in scope (or `random_select_amount` of random country if specified) that fulfills the `limit` trigger.
  - Version Added: 1.15

- **random_allied_country**
  - Usage: Within country scope only
  - Target type: Country
  - Example: random_allied_country = { … }
  - Description: Executes children effects on a random Allied Country different from the one in scope that fulfills the `limit` trigger.
  - Version Added: 1.15

- **every_enemy_country**
  - Usage: Within country scope only
  - Target type: Country
  - Example: every_enemy_country = { … }
  - Description: Executes contained effects on every country that meets the limit and is at war with the country this is contained in.
  - Version Added: 1.0

- **random_enemy_country**
  - Usage: Within country scope only
  - Target type: Country
  - Example: random_enemy_country = { … }
  - Description: Executes contained effects on a random country that meets the limit and is at war with the country this is contained in.
  - Version Added: 1.0

- **every_subject_country**
  - Usage: Within country scope only
  - Target type: Country
  - Example: every_subject_country = { … }
  - Description: Executes contained effects on every country that meets the limit and is a subject of the country this is contained in.
  - Version Added: 1.11

- **random_subject_country**
  - Usage: Within country scope only
  - Target type: Country
  - Example: random_subject_country = { … }
  - Description: Executes contained effects on a random country that meets the limit and is a subject of the country this is contained in.
  - Version Added: 1.11

- **every_faction_member**
  - Usage: Within country scope only
  - Target type: Country
  - Example: every_faction_member = { … }
  - Description: Executes children effects on every faction member of the country's faction in scope, if country does not have a faction it will only work on itself.
  - Version Added: 1.17

- **every_state**
  - Usage: Always usable
  - Target type: State
  - Example: every_state = { … }
  - Description: Executes contained effects on every state that meets the limit.
  - Version Added: 1.0

- **random_state**
  - Usage: Always usable
  - Target type: State
  - Example:
    ```text
    random_state = {
        prioritize = { 123 321 } #optional
        …    #effects to run
    }
    ```
  - Description: Executes contained effects on a random state that meets the limit.
  - Version Added: 1.0

- **every_neighbor_state**
  - Usage: Within state scope only
  - Target type: State
  - Example: every_neighbor_state = { … }
  - Description: Executes contained effects on every state that meets the limit and neighbours the state this is contained in.
  - Version Added: 1.0

- **random_neighbor_state**
  - Usage: Within state scope only
  - Target type: State
  - Example: random_neighbor_state = { … }
  - Description:
    ```text
    Executes contained effects on a random state that meets the limit and neighbours the state this is contained in. Does not support
    prioritizing
    .
    ```
  - Version Added: 1.0

- **every_owned_state**
  - Usage: Within country scope only
  - Target type: State
  - Example: every_owned_state = { … }
  - Description: Executes contained effects on every state that meets the limit and is owned by the country this is contained in.
  - Version Added: 1.0

- **random_owned_state**
  - Usage: Within country scope only
  - Target type: State
  - Example:
    ```text
    random_owned_state = {
        prioritize = { 123 321 } #optional
        …    #effects to run
    }
    ```
  - Description: Executes contained effects on a random state that meets the limit and is owned by the country this is contained in.
  - Version Added: 1.0

- **every_core_state**
  - Usage: Within country scope only
  - Target type: State
  - Example: every_core_state = { … }
  - Description: Executes contained effects on every state that meets the limit and is a core of the country this is contained in.
  - Version Added: 1.11

- **random_core_state**
  - Usage: Within country scope only
  - Target type: State
  - Example:
    ```text
    random_core_state = {
        prioritize = { 123 321 } #optional
        …    #effects to run
    }
    ```
  - Description: Executes contained effects on a random state that meets the limit and is a core of the country this is contained in.
  - Version Added: 1.11

- **every_controlled_state**
  - Usage: Within country scope only
  - Target type: State
  - Example: every_controlled_state = { … }
  - Description: Executes contained effects on every state that meets the limit and is controlled by the country this is contained in.
  - Version Added: 1.9

- **random_controlled_state**
  - Usage: Within country scope only
  - Target type: State
  - Example:
    ```text
    random_controlled_state = {
        prioritize = { 123 321 } #optional
        …    #effects to run
    }
    ```
  - Description: Executes contained effects on a random state that meets the limit and is controlled by the country this is contained in.
  - Version Added: 1.9

- **random_owned_controlled_state**
  - Usage: Within country scope only
  - Target type: State
  - Example:
    ```text
    random_owned_controlled_state = {
        prioritize = { 123 321 } #optional
        …    #effects to run
    }
    ```
  - Description: Executes contained effects on a random state that meets the limit and is owned and controlled by the country this is contained in.
  - Version Added: 1.3

- **every_unit_leader**
  - Usage: Within country scope only
  - Target type: Unit Leader
  - Example: every_unit_leader = { … }
  - Description: Executes contained effects on every unit leader (corps commanders, field marshals, admirals) that meets the limit and is recruited by the country this is contained in.
  - Version Added: 1.5

- **random_unit_leader**
  - Usage: Within country scope only
  - Target type: Unit Leader
  - Example: random_unit_leader = { … }
  - Description: Executes contained effects on a random unit leader (corps commanders, field marshals, admirals) that meets the limit and is recruited by the country this is contained in.
  - Version Added: 1.5

- **every_army_leader**
  - Usage: Within country scope only
  - Target type: Unit Leader
  - Example: every_unit_leader = { … }
  - Description: Executes contained effects on every army leader that meets the limit and is recruited by the country this is contained in.
  - Version Added: 1.5

- **random_army_leader**
  - Usage: Within country scope only
  - Target type: Unit Leader
  - Example: random_army_leader = { … }
  - Description: Executes contained effects on a random army leader that meets the limit and is recruited by the country this is contained in.
  - Version Added: 1.5

- **global_every_army_leader**
  - Usage: Always usable
  - Target type: Unit Leader
  - Example: global_every_army_leader = { … }
  - Description: Executes contained effects on every army leader that meets the limit. Preferable to use every_army_leader unless necessary to use global_every_army_leader.
  - Version Added: 1.5

- **every_navy_leader**
  - Usage: Within country scope only
  - Target type: Unit Leader
  - Example: every_navy_leader = { … }
  - Description: Executes contained effects on every navy leader that meets the limit and is recruited by the country this is contained in.
  - Version Added: 1.5

- **random_navy_leader**
  - Usage: Within country scope only
  - Target type: Unit Leader
  - Example: random_navy_leader = { … }
  - Description: Executes contained effects on a random navy leader that meets the limit and is recruited by the country this is contained in.
  - Version Added: 1.5

- **every_operative**
  - Usage: Within country scope or operations only
  - Target type: Operative
  - Example: every_operative = { … }
  - Description: Executes contained effects on every operative that meets the limit and is recruited by the country this is contained in.
  - Version Added: 1.9

- **random_operative**
  - Usage: Within country scope or operations only
  - Target type: Operative
  - Example: random_operative = { … }
  - Description: Executes contained effects on a random operative that meets the limit and is recruited by the country this is contained in.
  - Version Added: 1.9

- **every_character**
  - Usage: Within country scope only
  - Target type: Character
  - Example: every_character = { … }
  - Description: Executes contained effects on every character that meets the limit and is recruited by the country this is contained in.
  - Version Added: 1.11

- **random_character**
  - Usage: Within country scope only
  - Target type: Character
  - Example: random_character = { … }
  - Description: Executes contained effects on a random character that meets the limit and is recruited by the country this is contained in.
  - Version Added: 1.11

- **every_country_division**
  - Usage: Within country scope only
  - Target type: Division
  - Example: every_country_division = { … }
  - Description: Executes contained effects on every division that meets the limit and is owned by the current country.
  - Version Added: 1.12

- **random_country_division**
  - Usage: Within country scope only
  - Target type: Division
  - Example: random_country_division = { … }
  - Description: Executes contained effects on a random division that meets the limit and is owned by the current country.
  - Version Added: 1.12

- **every_state_division**
  - Usage: Within state scope only
  - Target type: Division
  - Example: every_state_division = { … }
  - Description: Executes contained effects on every division that meets the limit and is located within the current state.
  - Version Added: 1.12

- **random_state_division**
  - Usage: Within state scope only
  - Target type: Division
  - Example: random_state_division = { … }
  - Description: Executes contained effects on a random division that meets the limit and is located within the current state.
  - Version Added: 1.12

- **every_military_industrial_organization**
  - Usage: Within country scope only
  - Target type: MIO
  - Example: every_military_industrial_organization = { … }
  - Description: Executes contained effects on every MIO within the current country that meets the limit.
  - Version Added: 1.13

- **random_military_industrial_organization**
  - Usage: Within country scope only
  - Target type: MIO
  - Example: random_military_industrial_organization = { … }
  - Description: Executes contained effects on a random MIO within the current country that meets the limit.
  - Version Added: 1.13

- **every_purchase_contract**
  - Usage: Within country scope only
  - Target type: Purchase contract
  - Example: every_purchase_contract = { … }
  - Description: Executes contained effects on every purchase contract within the current country that meets the limit.
  - Version Added: 1.13

- **random_purchase_contract**
  - Usage: Within country scope only
  - Target type: Purchase contract
  - Example: random_purchase_contract = { … }
  - Description: Executes contained effects on a random purchase contract within the current country that meets the limit.
  - Version Added: 1.13

- **every_scientist**
  - Usage: Within country scope only
  - Target type: Character
  - Example: every_scientist = { … }
  - Description: Executes children effects on every scientist (or "random_select_amount" of random character if specified) of the country in scope, that fulfills the "limit" trigger.
  - Version Added: 1.15

- **random_scientist**
  - Usage: Within country scope only
  - Target type: Character
  - Example: random_scientist = { … }
  - Description: Executes children effects on random scientists that fulfills the "limit" trigger.
  - Version Added: 1.15

- **every_active_scientist**
  - Usage: Within country scope only
  - Target type: Character
  - Example: every_active_scientist = { … }
  - Description: Executes children effects on every active scientist (or "random_select_amount" of random character if specified) of the country in scope, that fulfills the "limit" trigger.title.
  - Version Added: 1.15

- **random_active_scientist**
  - Usage: Within country scope only
  - Target type: Character
  - Example: random_active_scientist = { … }
  - Description: Executes children effects on random scientists that fulfills the "limit" trigger.
  - Version Added: 1.15

- **party_leader**
  - Usage: Within country scope only
  - Target type: Character
  - Example:
    ```text
    party_leader = {
        limit = {
            has_ideology = liberalism
        }
        set_nationality = BHR
    }
    ```
  - Description:
    ```text
    Executes the effects on the party leader with the specified ideology type. Must contain a
    has_ideology
    in the limit that refers to a specific ideology type (e.g. Despotic), not a group that contain the type (e.g. Non-Aligned). The selected character must be the leader of a party corresponding to the ideology group.
    ```
  - Version Added: 1.11

- **every_collection_element**
  - Usage: Always usable
  - Target type: Collection/Any
  - Example:
    ```text
    every_collection_element = {
        input = {
            input = collection_id # This can be a collection name or an inline definition of a collection
            limit = {
                # Trigger - limit effect execution to a subset of elements
            }
        }
        # Effects to be executed
    }
    ```
  - Description:
    ```text
    Applies arbitrary effects to all elements of a collection. To learn more about collections, see the documentation in
    /Hearts of Iron IV/common/collections
    .
    ```
  - Version Added: 1.17

**NOTE:** Some of these scopes may have no countries/states that match the criteria.

### Effects with scopes

Effects that change the scope include the following:

- [start\_civil\_war](#start-civil-war), which changes it to the rebelling dynamic country.
- [create\_dynamic\_country](#create-dynamic-country), which changes it to the newly-created dynamic country.

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

## Any scope

Can be used in **country**, **state** or **character** scopes.

### General

- **add_dynamic_modifier**
  - Parameters:
    ```text
    modifier = <modifier_string>
    The name of the Modifier.
    scope = <country>
    If you specify it, your dynamic modifier will be scoped to this scope. Optional.
    days = x
    The modifiers will be removed after x days have passed. Optional.
    ```
  - Example:
    ```text
    add_dynamic_modifier = {
        modifier = example_dynamic_modifier
        scope = GER
        days = 14
    }
    ```
  - Description:
    ```text
    Adds a dynamic modifier to the specified scope (the default scope is ROOT).
    It will be updated daily, unless forced to update early by force_update_dynamic_modifier effect.
    ```
  - Notes:
    ```text
    Examples can be found in
    /Hearts of Iron IV/common/dynamic_modifiers/*.txt
    . Any modifiers that use variables within of the dynamic modifier will not show up in the tooltip of this effect, while those that are set to a static value will. Supports the state, country, character, and special project scopes.
    ```
  - Version Added: 1.6

- **remove_dynamic_modifier**
  - Parameters:
    ```text
    modifier = <modifier_string>
    The name of the Modifier.
    ```
  - Example:
    ```text
    remove_dynamic_modifier = { modifier = sabotaged_ressources }
    ```
  - Description: Removes a dynamic modifier from the current scope
  - Notes:
    ```text
    Examples can be found in
    /Hearts of Iron IV/common/dynamic_modifiers/*.txt
    ```
  - Version Added: 1.6

- **force_update_dynamic_modifier**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    force_update_dynamic_modifier = yes
    ```
  - Description: Forces an update to the effects given by variables within dynamic modifiers.
  - Notes: An update is done daily by default; this can be used if the applied values need to be changed urgently, such as if modifiers are checked or used later in the effect block.
  - Version Added: 1.6

- **set_global_flag**
  - Parameters:
    ```text
    <flag>
    An unique string to identify the global flag with.
    OR
    flag = <flag>
    The flag to set.
    days = <int>
    Sets the flag to last for the specified amount of days. Optional.
    value = <int>
    The new value of the flag on the scale from -2 147 483 648 to 2 147 483 647.
    ```
  - Example:
    ```text
    set_global_flag = my_flag
    ```
  - Example:
    ```text
    set_global_flag = {
        flag = my_flag
        days = 123
        value = 1
    }
    ```
  - Description: Defines a global flag.
  - Notes:
    ```text
    No tooltip is shown.
    The flag in this effect is used in the meaning of 'boolean flag', used to store information.
    ```
  - Version Added: 1.0

- **play_song**
  - Parameters:
    ```text
    <song title from .asset>
    A music file located in the music folder and .asset
    ```
  - Example:
    ```text
    play_song = "general_peace_1"
    ```
  - Description: Plays an audio track
  - Notes:
    ```text
    The song must be defined in a music station in order to work. More information can be found in the
    Music modding
    page. If you wish to simply play a sound, the
    sound_effect
    effect should be used instead.
    The song will start playing for every country if the effect is executed. See
    scoped_play_song
    if only one country should have the song.
    ```
  - Version Added: 1.9.3

- **clr_global_flag**
  - Parameters:
    ```text
    <flag>
    The unique string of a global flag to clear.
    ```
  - Example:
    ```text
    clr_global_flag = my_flag
    ```
  - Description: Clears a defined global flag.
  - Notes: No tooltip is shown
  - Version Added: 1.0

- **modify_global_flag**
  - Parameters:
    ```text
    flag = <flag>
    The flag to modify.
    value = <value>
    The value to add to the flag. Defaults to 0.
    days = <int>
    The amount of days that the flag should last for before being cleared. Optional, defaults to permanent.
    ```
  - Example:
    ```text
    modify_global_flag = {
        flag = my_flag
        value = 3
    }
    ```
  - Description: Adds an integer value to a flag.
  - Notes: The flag must be already set.
  - Version Added: 1.3

- **custom_effect_tooltip**
  - Parameters:
    ```text
    <string>
    A localized string to display in the tooltip.
    ```
  - Example:
    ```text
    custom_effect_tooltip = my_tooltip_tt
    ```
  - Example:
    ```text
    custom_effect_tooltip = {
        localization_key = my_loc
        NESTEDLOC = myotherloc/string
    }
    ```
  - Description: Displays a localized key in the effect tooltip.
  - Notes:
    ```text
    Also supports
    Localisation#Bindable_localisation
    .
    ```
  - Version Added: 1.0

- **custom_override_tooltip**
  - Parameters:
    ```text
    tooltip = <string>
    A localized string to display in the tooltip.
    not_tooltip = <string>
    A localized string to display in the tooltip for NOT block. Optional.
    ```
  - Example:
    ```text
    custom_override_tooltip= {
        tooltip = my_tt
        not_tooltip = my_tt_NOT
        <effects>
    }
    ```
  - Description: Executes the provided effects but with a custom tooltip surpressing all tooltips from all other effects inside this block.
  - Notes:
    ```text
    Can also be used as trigger.
    Also supports
    Localisation#Bindable_localisation
    .
    ```
  - Version Added: 1.15

- **effect_tooltip**
  - Parameters: <string>
  - Example:
    ```text
    effect_tooltip = {
        declare_war_on = {
            target = FRA
        }
    }
    ```
  - Description: Displays the effects in the tooltip without executing them.

- **log**
  - Parameters:
    ```text
    <string>
    An string to in the game.log
    ```
  - Example:
    ```text
    log = "myVariable: [?myVariable]"
    ```
  - Description:
    ```text
    Displays a string in the
    user directory's
    /Hearts of Iron IV/logs/game.log
    file when executed, as well as showing up in the console if it is open when the logging effect was executed.
    ```
  - Notes:
    ```text
    Accepts all localisation commands (e.g.
    [Root.GetName]
    ,
    [GetDateText]
    , etc)
    ```
  - Version Added: 1.5

- **save_event_target_as**
  - Parameters:
    ```text
    <string>
    An unique string to identify the event target with.
    ```
  - Example:
    ```text
    capital_scope = {
        save_event_target_as = my_state
    }
    ```
  - Description: Saves the current scope as a key. Is cleared once execution ends (i.e. end of event).
  - Notes:
    ```text
    Use event_target:<key> to access the scope.
    Do not use in Scripted GUIs.
    ```
  - Version Added: 1.0

- **save_global_event_target_as**
  - Parameters:
    ```text
    <string>
    An unique string to identify the global event target with.
    ```
  - Example:
    ```text
    random_other_country = {
        save_global_event_target_as = my_country
    }
    ```
  - Description: Saves the current scope as a key. Persists after execution until cleared via effect.
  - Notes:
    ```text
    Use event_target:<key> to access the scope.
    Do not use in Scripted GUIs.
    ```
  - Version Added: 1.0

- **clear_global_event_target**
  - Parameters:
    ```text
    <string>
    The unique string of the global event target to clear.
    ```
  - Example:
    ```text
    clear_global_event_target = my_country
    ```
  - Description: Clears a specific global event target.
  - Version Added: 1.0

- **clear_global_event_targets**
  - Parameters:
    ```text
    yes
    Boolean.
    ```
  - Example:
    ```text
    clear_global_event_targets = yes
    ```
  - Description: Clears all global event targets.
  - Version Added: 1.0

- **sound_effect**
  - Parameters:
    ```text
    <string>
    A sound reference from an .asset file.
    ```
  - Example:
    ```text
    sound_effect = "boom"
    ```
  - Description: Plays the specified sound once.
  - Notes:
    ```text
    The sound effect must be properly defined in
    /Hearts of Iron IV/sound/
    See also:
    Sound modding
    .
    The sound will play for every country if the effect is executed. See
    scoped_sound_effect
    if only one country should hear it.
    ```
  - Version Added: 1.0

- **randomize_weather**
  - Parameters:
    ```text
    <int>
    A seed integer.
    ```
  - Example:
    ```text
    randomize_weather = 12345
    ```
  - Description: Randomizes the weather with the specified seed.
  - Version Added: 1.0

- **set_province_name**
  - Parameters:
    ```text
    id = <id>
    The id of the province to be changed.
    name = <string>
    The name to change the province to.
    ```
  - Example:
    ```text
    set_province_name = {
        id = 325
        name = LOC_KEY
    }
    ```
  - Example:
    ```text
    set_province_name = { id = 325 name = "New Name" }
    ```
  - Description: Changes the specified province/victory point's name to the specified name.
  - Notes:
    ```text
    Localisation keys are to be defined in
    /Hearts of Iron IV/localisation/*_l_<language>.yml
    ```
  - Version Added: 1.3

- **reset_province_name**
  - Parameters:
    ```text
    <id>
    The id of the province to reset.
    ```
  - Example:
    ```text
    reset_province_name = 325
    ```
  - Description: Resets the specified province's name.
  - Version Added: 1.3

- **damage_units**
  - Parameters:
    ```text
    province = <id>
    Province where to damage units.
    state = <id>
    State where to damage units.
    region = <id>
    Strategic region where to damage units.
    limit = { <triggers> }
    Will only delete units if the triggers within are met for the country that owns the units.
    damage = <fraction>
    The percentage of damage done to units.
    org_damage = <fraction>
    The percentage of damage done to units to organisation in particular.
    str_damage = <fraction>
    The percentage of damage done to units to strength in particular.
    ratio = <yes>
    Will damage a ratio damage to total organisation/strength of unit if set.
    template = <string>
    If specified, requires the template name to match.
    army = <bool>
    Will damage the army units.
    navy = <bool>
    Will damage the navy units.
    ```
  - Example:
    ```text
    damage_units = {
        province = 42
        state = 5
        region = 5
        limit = { has_country_flag = TAG_test }
        damage = 0.5
        org_damage = 0.5
        str_damage = 0.5
        ratio = yes
        template = "template_name"
        army = no
        navy = yes
    }
    ```
  - Description: Damages units in the specified area.
  - Version Added: 1.11

- **create_entity**
  - Parameters:
    ```text
    entity = <gfx_entry>
    The entity to spawn, defined within
    /Hearts of Iron IV/gfx/entities/*.asset
    files.
    id = int
    A number ID which can be referred to by other effects. Optional.
    var = <variable>
    If provided, the id of the entity will be stored using this variable. Optional.
    x = <int>
    The X position of the entity.
    y = <int>
    The Y position of the entity.
    z = <int>
    The Z position of the entity.
    province = <int>
    The province the middle of which to use as the entity's position.
    state = <int>
    The state the middle of which to use as the entity's position.
    rotation = <decimal>
    The rotation of the entity in radians.
    scale = <decimal>
    The size of the entity.
    min_zoom = <decimal>
    Minimum zoom level needed to be able to see the entity.
    visible = <scripted_trigger>
    The scripted trigger that must be met for a country for it to see the entity.
    ```
  - Example:
    ```text
    create_entity = {
        entity = entity_name
        id = 123
        var = var_name
        x = 42
        y = 21
        z = 3
        province = 123
        state = 42
        rotation = 1.2
        scale = 10.0
        min_zoom = 100.0
        visible = scripted_trigger_name
    }
    ```
  - Description: Creates an entity.
  - Notes:
    ```text
    Uses the
    the same coordinate system that the map uses.
    A positive change in rotation results in counter-clockwise rotation, a full 360 degrees rotation is approximately 6.28 radians. For comparison, default minimum zoom level (closest to the map) is 50 units, while default maximum zoom level is 3000 units.
    ```
  - Version Added: 1.11

- **destroy_entity**
  - Parameters:
    ```text
    <id>
    The ID of the entity to destroy.
    ```
  - Example:
    ```text
    destroy_entity = 123
    ```
  - Description: Deletes an entity
  - Notes:
    ```text
    IDs are set by the
    create_entity effect
    .
    ```
  - Version Added: 1.11

- **set_entity_movement**
  - Parameters:
    ```text
    id = <ID>
    The ID of the entity to modify.
    ratio = <int>
    Distance between starting position and target position where the entity is to be placed.
    rotation = <int>
    The rotation to apply
    after
    the positioning.
    start
    and
    target
    arguments:
    x = <int>
    The X position of the point.
    y = <int>
    The Y position of the point.
    z = <int>
    The Z position of the point.
    province = <int>
    The province the middle of which to use as the point.
    state = <int>
    The state the middle of which to use as the point.
    ```
  - Example:
    ```text
    set_entity_movement = {
        id = 123
        start = {
            x = 42
            y = 21
            z = 3
        }
        target = {
            province = 124
        }
        ratio = 0.5
        rotation = 1.2
    }
    ```
  - Description: Sets the position and rotation of an entity using two coordinates.
  - Notes:
    ```text
    IDs are set by the
    create_entity effect
    . Uses the
    the same coordinate system that the map uses.
    A positive change in rotation results in counter-clockwise rotation, a full 360 degrees rotation is approximately 6.28 radians.
    ```
  - Version Added: 1.11

- **set_entity_position**
  - Parameters:
    ```text
    id = <id>
    x = <int>
    y = <int>
    z = <int>
    province = <int>
    state = <int>
    ```
  - Example:
    ```text
    set_entity_position = {
      id = 123
      x = 42
      y = 21
      z = 3
      province = 123
      state = 42
    }
    ```
  - Description: Sets the position of an existing entity
  - Notes:
    ```text
    IDs are set by the
    create_entity effect
    . Uses the
    the same coordinate system that the map uses.
    ```
  - Version Added: 1.11

- **set_entity_rotation**
  - Parameters:
    ```text
    id = <ID>
    The ID of the entity to modify.
    rotation = <decimal>
    The new angle in radians.
    ```
  - Example:
    ```text
    set_entity_rotation = {
        id = 123
        rotation = 0.23
    }
    ```
  - Description: Sets the currently-facing angle of an existing entity.
  - Notes:
    ```text
    IDs are set by the
    create_entity effect
    . A positive change results in counter-clockwise rotation, a full 360 degrees rotation is approximately 6.28 radians.
    ```
  - Version Added: 1.11

- **set_entity_scale**
  - Parameters:
    ```text
    id = <ID>
    The ID of the entity to modify.
    scale = <decimal>
    The scale to change the entity to.
    ```
  - Example:
    ```text
    set_entity_scale = {
      id = 123
      scale = 5.0
    }
    ```
  - Description: Sets the size of an existing entity.
  - Notes:
    ```text
    IDs are set by the
    create_entity effect
    .
    ```
  - Version Added: 1.11

- **set_entity_animation**
  - Parameters:
    ```text
    id = <int>
    The ID of the entity to modify.
    animation = <animation_type>
    The animation entry to apply.
    ```
  - Example:
    ```text
    set_entity_animation = {
        id = 123
        animation = "shoot_lasers"
    }
    ```
  - Description: Sets the animation of a specified entity.
  - Notes:
    ```text
    IDs are set by the
    create_entity effect
    . Animations are defined within the
    /Hearts of Iron IV/gfx/models/**/*.asset
    files.
    ```
  - Version Added: 1.11

- **build_railway**
  - Parameters:
    ```text
    level = <int>
    Defaults to 1
    build_only_on_allied = <bool>
    No by default, if yes and in a country scope, it will only build on allied territories for the country scoped.
    fallback = <bool>
    Defaults to no, if yes each option will try to fallback to the next available one.
    path = { <list of provinces> }
    start_province = <int>
    target_province = <int>
    start_state = <int>
    target_state = <int>
    If using start state/target state, the game will pick the provinces with the best supply available. If using state province/target province, the game will link those two provinces.
    ```
  - Example:
    ```text
    build_railway = {
        level = 1
        build_only_on_allied = yes
        controller_priority = {
            base = 1
            modifier = {
                tag = MAN
                add = 2
            }
        }
        fallback = yes
        path = { 42 10 20 30 40 84 }
        start_province = 42
        target_province = 84
    }
    ```
  - Example:
    ```text
    build_railway = {
        level = 1
        build_only_on_allied = yes
        controller_priority = {
            base = 1
            modifier = {
                tag = MAN
                add = 2
            }
        }
        fallback = yes
        path = { 50 10 20 30 40 100 }
        start_state = 50
        target_state = 100
    }
    ```
  - Description: Adds a railway level between two provinces or along a predefined path.
  - Version Added: 1.11

- **event_option_tooltip**
  - Parameters:
    ```text
    <option>
    The name of the option.
    ```
  - Example:
    ```text
    event_option_tooltip = mtg_usa_civil_war_fascists.1.a
    ```
  - Description: Shows the tooltip usually received for hovering over an event option with the specified name.
  - Notes: ROOT and FROM scopes are swapped.
  - Version Added: 1.13

- **create_purchase_contract**
  - Parameters:
    ```text
    seller = <country>
    The seller in the contract.
    buyer = <country>
    The buyer in the contract.
    civilian_factories = <int>
    The amount of civilian factories required by the contract.
    equipment = { ... }
    The equipment that the contract is for. In particular, contains these attributes:
    type = <archetype>
    The archetype of the equipment.
    amount = <int>
    The amount of the specified equipment.
    ```
  - Example:
    ```text
    create_purchase_contract = {
        seller = ROOT
        buyer = FROM
        civilian_factories = 2
        equipment = {
            type = artillery_equipment
            amount = 300
        }
    }
    ```
  - Description: Creates a purchase contract with the specified parameters.
  - Notes:
    ```text
    Allows using
    equipment = { ... }
    several times.
    ```
  - Version Added: 1.13

### Border wars

These effects refer to the border wars that simulate combat on a border between two countries, with provinces where it takes place being highlighted in white. For the state-based border wars represented with orange stripes on states, see [set\_border\_war](#set-border-war) in the state scope.

- **start_border_war**
  - Parameters:
    ```text
    change_state_after_war = <bool>
    Whether the state changes hands after the war.
    Attacker or Defender scope
    state = <id> / <variable>
    The state the side is fighting on.
    num_provinces = <id>
    The number of provinces used in the state.
    on_win = <id>
    The event to fire for the side on a win.
    on_lose = <id>
    The event to fire for the side on a loss.
    on_cancel = <id>
    The event to fire for the side on a draw.
    modifier = <decimal>
    The modifier on combat. Defaults to 0.
    dig_in_factor = <decimal>
    The modifier applied to dig-in bonuses. Defaults to 1.
    terrain_factor = <decimal>
    The modifier applied to terrain bonuses. Defaults to 1.
    ```
  - Example:
    ```text
    start_border_war = {
        change_state_after_war = no
        attacker = {
            state = 527
            num_provinces = 4
            on_win = japan_border_conflict.2
            on_lose = japan_border_conflict.3
            on_cancel = japan_border_conflict.4
            modifier = 0.1
            dig_in_factor = 0
            terrain_factor = 0
        }	
        defender = {
            state = 408
            num_provinces = 4
            on_win = japan_border_conflict.3
            on_lose = japan_border_conflict.2
            on_cancel = japan_border_conflict.4
        }
    }
    ```
  - Description: Starts a border war for the specified attacker and defender. The participating countries are the owners of the specified states.
  - Version Added: 1.5

- **set_border_war_data**
  - Parameters:
    ```text
    attacker = <id> / <variable>
    The attacker state.
    defender = <id> / <variable>
    The defender state.
    attacker_modifier = <id> / <variable>
    The modifier applied to attacker strength.
    defender_modifier = <id> / <variable>
    The modifier applied to attacker strength.
    combat_width = <id> / <variable>
    The combat width used in the border war battle.
    ```
  - Example:
    ```text
    set_border_war_data = {
        attacker = 527
        defender = 408
        defender_modifier = 0.15
        combat_width = 100
    }
    ```
  - Description:
    ```text
    Sets the bonuses or penalties for the attacker and defender in an on-going border war. Used after
    start_border_war
    .
    ```
  - Version Added: 1.5

- **cancel_border_war**
  - Parameters:
    ```text
    attacker = <id> / <variable>
    The attacker state.
    defender = <id> / <variable>
    The defender state.
    dont_fire_events = <bool>
    Stops the events from
    start_border_war
    from firing.
    ```
  - Example:
    ```text
    cancel_border_war = {
        dont_fire_events = yes
        defender = 408
        attacker = 527
    }
    ```
  - Description: Cancels an on-going border war without a winner.
  - Version Added: 1.5

- **finalize_border_war**
  - Parameters:
    ```text
    attacker = <id> / <variable>
    The attacker state.
    defender = <id> / <variable>
    The defender state.
    attacker_win = <bool>
    Makes the attacker the winner.
    defender_win = <bool>
    Makes the defender the winner.
    ```
  - Example:
    ```text
    finalize_border_war = {
        attacker_win = yes
        attacker = 527
        defender = 408
    }
    ```
  - Description: Ends an on-going border war.
  - Version Added: 1.5

### Variables

*This section is transcluded from [Data structures § Operators](<Data structures - Hearts of Iron 4 Wiki.md#operators>)*

The following is a list of variable-related effects and triggers. Variable-modifying effects have an equivalent for temporary variables, with `temp_variable` being used instead of `variable`, and these temporary variable operators are also valid triggers, as described above. Every operator can be used with variables that do not exist, assuming a value of 0 unless a null-coalescing operator is used.

- **set_variable**
  - Parameters:
    ```text
    var = <variable>
    The variable to modify or create.
    value = <decimal>/<variable>
    The value to set the variable to.
    tooltip = localisation_key
    Localisation used by the operation. Optional.
    ```
  - Example:
    ```text
    set_variable = {
        var = my_variable
        value = 100
        tooltip = set_var_to_100_tt
    }
    ```
  - Example:
    ```text
    set_temp_variable = { temp_var = ROOT.overlord }
    ```
  - Description: Sets a variable's value to the specified amount, creating it if not defined.
  - Notes:
    ```text
    Shortened version exists with
    set_variable = { <variable> = <value> }
    .
    ```

- **set_variable_to_random**
  - Parameters:
    ```text
    var = <variable>
    The variable to modify or create.
    min = <decimal>
    The minimum possible value, defaults to 0.
    max = <decimal>
    The maximum possible value, defaults to 1.
    integer = <bool>
    Sets if the variable
    must
    be an integer or if it can be decimal. Defaults to false.
    ```
  - Example:
    ```text
    set_variable_to_random = {
        var = random_num
        max = 11
        integer = yes
    }
    ```
  - Example:
    ```text
    set_temp_variable_to_random = my_var
    ```
  - Description: Sets a variable's value to the specified amount, creating it if not defined. The result will be greater than or equal than the minimum and strictly less than the maximum.
  - Notes:
    ```text
    Shortened version exists with
    set_variable_to_random = <variable>
    , setting it to a decimal between 0 and 1. Can be used in triggers.
    ```

- **clear_variable**
  - Parameters:
    ```text
    <variable>
    Variable to clear.
    ```
  - Example:
    ```text
    clear_variable = my_variable
    ```
  - Description: Clears the value from the memory entirely.
  - Notes: Can only be used on regular variables.

- **add_to_variable**
  - Parameters:
    ```text
    var = <variable>
    The variable to add to.
    value = <decimal>/<variable>
    The value to add to the variable.
    tooltip = localisation_key
    Localisation used by the operation. Optional.
    ```
  - Example:
    ```text
    add_to_variable = {
        var = my_variable
        value = 100
        tooltip = add_100_to_var_tt
    }
    ```
  - Example:
    ```text
    add_to_temp_variable = { temp_var = num_owned_states }
    ```
  - Description: Increases a variable's value by the specified amount, creating it if not defined.
  - Notes:
    ```text
    Shortened version exists with
    add_to_variable = { <variable> = <value> }
    .
    ```

- **subtract_from_variable**
  - Parameters:
    ```text
    var = <variable>
    The variable to subtract from.
    value = <decimal>/<variable>
    The value to subtract from the variable.
    tooltip = localisation_key
    Localisation used by the operation. Optional.
    ```
  - Example:
    ```text
    subtract_from_variable = {
        var = my_variable
        value = 100
        tooltip = sub_100_from_var_tt
    }
    ```
  - Example:
    ```text
    subtract_from_temp_variable = { temp_var = num_owned_states }
    ```
  - Description: Decreases a variable's value by the specified amount, creating it if not defined.
  - Notes:
    ```text
    Shortened version exists with
    subtract_from_variable = { <variable> = <value> }
    . Equivalent to adding a negative amount.
    ```

- **multiply_variable**
  - Parameters:
    ```text
    var = <variable>
    The variable to multiply.
    value = <decimal>/<variable>
    The value to multiply the variable by.
    tooltip = localisation_key
    Localisation used by the operation. Optional.
    ```
  - Example:
    ```text
    multiply_variable = {
        var = my_variable
        value = 100
        tooltip = multiply_var_by_100_tt
    }
    ```
  - Example:
    ```text
    multiply_temp_variable = { temp_var = num_owned_states }
    ```
  - Description: Multiplies a variable's value by the specified amount.
  - Notes:
    ```text
    Shortened version exists with
    multiply_variable = { <variable> = <value> }
    .
    ```

- **divide_variable**
  - Parameters:
    ```text
    var = <variable>
    The variable to divide.
    value = <decimal>/<variable>
    The value to divide the variable by.
    tooltip = localisation_key
    Localisation used by the operation. Optional.
    ```
  - Example:
    ```text
    divide_variable = {
        var = my_variable
        value = 100
        tooltip = divide_var_by_100_tt
    }
    ```
  - Example:
    ```text
    divide_temp_variable = { temp_var = num_owned_states }
    ```
  - Description: Divides a variable's value by the specified amount.
  - Notes:
    ```text
    Shortened version exists with
    divide_variable = { <variable> = <value> }
    .
    ```

- **modulo_variable**
  - Parameters:
    ```text
    var = <variable>
    The variable to modulo.
    value = <decimal>/<variable>
    The value to modulo the variable by.
    tooltip = localisation_key
    Localisation used by the operation. Optional.
    ```
  - Example:
    ```text
    modulo_variable = {
        var = my_variable
        value = 50
        tooltip = get_modulo_of_var_by_50_tt
    }
    ```
  - Example:
    ```text
    modulo_temp_variable = { temp_var = num_controlled_states }
    ```
  - Description:
    ```text
    Makes the variable become the remainder of
    Euclidean division
    of the variable by the specified value.
    ```
  - Notes:
    ```text
    Shortened version exists with
    modulo_variable = { <variable> = <value> }
    .
    ```

- **round_variable**
  - Parameters:
    ```text
    <variable>
    The variable to round.
    ```
  - Example:
    ```text
    round_variable = my_variable
    ```
  - Example:
    ```text
    round_temp_variable = temp
    ```
  - Description: Rounds the variable towards the closest integer value.
  - Notes: If exactly between two integers (Such as 1.5), the option with lager absolute val gets chosen ( if -1.5,will be -2 ).

- **clamp_variable**
  - Parameters:
    ```text
    var = <variable>
    The variable to clamp.
    min = <decimal>/<variable>
    The minimum value of the variable after the clamp.
    max = <decimal>/<variable>
    The maximum value of the variable after the clamp.
    ```
  - Example:
    ```text
    clamp_variable = {
        var = my_var
        min = 0
    }
    ```
  - Example:
    ```text
    clamp_temp_variable = {
        var = my_var
        min = 0
    }
    ```
  - Description: Clamps the variable to ensure its value is between the two specified numbers, raising to the minimum if smaller or lowering to the maximum if larger.
  - Notes:
    ```text
    Either min or max can be omitted, in which case it'll not be checked. Does nothing if the variable is already in the range between min and max.
    This only changes the current value of the variable
    , it can still go beyond the minimum or the maximum after the clamp.
    ```

- **career_profile_set_temp_playthrough_variable**
  - Parameters:
    ```text
    var = <variable>
    The variable to modify or create.
    value = <decimal>/<variable>
    The value to set the variable to.
    ```
  - Example:
    ```text
    career_profile_set_temp_playthrough_variable = {
      sum = rocket_sites_built_1936
    }
    ```
  - Description: Sets a temporary variable to a value or another variable.
  - Column 6: ???

- **career_profile_set_temp_variable**
  - Parameters:
    ```text
    var = <variable>
    The variable to modify or create.
    value = <decimal>/<variable>
    The value to set the variable to.
    ```
  - Example:
    ```text
    career_profile_set_temp_variable = {
      var = num_dogs
      value = num_dogs_in_career_profile
    }
    ```
  - Description: Sets a temporary variable to a value or another variable.
  - Column 6: ???

### Arrays

*See also: Arrays*

- **add_to_array**
  - Parameters:
    ```text
    array = <array>
    The array to modify.
    value = <decimal>/<variable>
    The variable to add.
    index = <integer>
    The index to place the variable on in the array. Optional, defaults to the end of the array.
    ```
  - Example:
    ```text
    add_to_array = {
        array = global.my_countries
        value = THIS.id
    }
    ```
  - Example:
    ```text
    add_to_temp_array = { temp_states = THIS }
    ```
  - Description: Adds an element to the array either at the specified index, defaulting to the end otherwise.
  - Notes:
    ```text
    Shortened version exists with
    add_to_array = { <array> = <value> }
    .
    ```

- **remove_from_array**
  - Parameters:
    ```text
    array = <array>
    The array to modify.
    value = <decimal>/<variable>
    The variable to remove. Optional.
    index = <integer>
    The index to remove the variable from in the array. Optional.
    ```
  - Example:
    ```text
    remove_from_array = {
        array = global.my_countries
        index = 0
    }
    ```
  - Example:
    ```text
    remove_from_temp_array = { temp_states = THIS }
    ```
  - Description: Removes an element from the array with the specified value or index.
  - Notes:
    ```text
    Shortened version exists with
    remove_from_array = { <array> = <value> }
    . If neither value nor index are specified, then the last element is deleted.
    ```

- **clear_array**
  - Parameters:
    ```text
    <array>
    The array to clear.
    ```
  - Example:
    ```text
    clear_array = global.my_countries
    ```
  - Example:
    ```text
    clear_temp_array = temp_states
    ```
  - Description: Clears the array, removing every element inside.

- **resize_array**
  - Parameters:
    ```text
    array = <array>
    The array to modify.
    value = <decimal>/<variable>
    The variable to add to the array if the size is larger than the array's current size. Optional, defaults to 0.
    size = <integer>
    The amount of elements inside of the array after the resizing.
    ```
  - Example:
    ```text
    resize_array = {
        array = global.countries_by_states
        value = 10
        size = global.countries^num
    }
    ```
  - Example:
    ```text
    resize_temp_array = { temp_states = 20 }
    ```
  - Description: Resizes the array, removing or adding elements in the end if necessary.
  - Notes:
    ```text
    Shortened version exists with
    resize_array = { <array> = <size> }
    .
    ```

- **find_highest_in_array**
  - Parameters:
    ```text
    array = <array>
    The array to modify.
    value = <variable>
    The temporary variable where the largest value will get stored.
    index = <variable>
    The temporary variable where the index of the largest value will get stored.
    ```
  - Example:
    ```text
    find_highest_in_array = {
        array = global.countries_by_states
        value = temp_largest_country
        index = temp_country_index
    }
    ```
  - Description: Finds the largest value in the array and assigns its value and index to a temporary variable.
  - Notes: Either value or index are optional to specify.

- **find_lowest_in_array**
  - Parameters:
    ```text
    array = <array>
    The array to modify.
    value = <variable>
    The temporary variable where the smallest value will get stored.
    index = <variable>
    The temporary variable where the index of the smallest value will get stored.
    ```
  - Example:
    ```text
    find_lowest_in_array = {
        array = global.countries_by_states
        value = temp_largest_country
        index = temp_country_index
    }
    ```
  - Description: Finds the smallest value in the array and assigns its value and index to a temporary variable.
  - Notes: Either value or index are optional to specify.

## Country scope

The effects here must be used within a **country** scope.

### General

- **set_country_flag**
  - Parameters:
    ```text
    <flag>
    An unique string to identify the country flag with.
    OR
    flag = <flag>
    The flag to set.
    days = <int>
    Sets the flag to last for the specified amount of days. Optional.
    value = <int>
    The new value of the flag on the scale from -2 147 483 648 to 2 147 483 647.
    ```
  - Example:
    ```text
    set_country_flag = my_flag
    ```
  - Example:
    ```text
    set_country_flag = {
        flag = my_flag
        days = 123
        value = 1
    }
    ```
  - Description: Defines a country flag.
  - Notes:
    ```text
    No tooltip is shown.
    The flag in this effect is used in the meaning of 'boolean flag', used to store information.
    In order to change the flag that represents the country, see
    cosmetic tags.
    ```
  - Version Added: 1.0

- **clr_country_flag**
  - Parameters:
    ```text
    <flag>
    The unique string of a country flag to clear.
    ```
  - Example:
    ```text
    clr_country_flag = my_flag
    ```
  - Description: Clears a defined country flag.
  - Version Added: 1.0

- **modify_country_flag**
  - Parameters:
    ```text
    flag = <flag>
    The flag to modify.
    value = <value>
    The value to add to the flag. Defaults to 0.
    days = <int>
    The amount of days that the flag should last for before being cleared. Optional, defaults to permanent.
    ```
  - Example:
    ```text
    modify_country_flag = {
        flag = my_flag
        value = 3
    }
    ```
  - Description: Adds an integer value to a flag.
  - Notes: The flag must be already set.
  - Version Added: 1.3

- **country_event**
  - Parameters:
    ```text
    id = <event>
    The event to fire.
    days = <int> / <variable>
    Fires the event in the specified number of days. Optional.
    hours = <int> / <variable>
    Fires the event in the specified number of hours. Optional.
    random_hours = <int> / <variable>
    Adds a random number (between
    0
    and
    random_hours
    , inclusive) of
    hours
    to the scheduled fire time. Optional.
    random_days = <int> / <variable>
    Adds a random number (between
    0
    and
    random_days
    , inclusive) of days to the scheduled fire time. Optional.
    ```
  - Example:
    ```text
    country_event = {
        id = my_event.1
        days = 10
        random_hours = 12
        random_days = 10
    }
    ```
  - Example:
    ```text
    country_event = my_event.1
    ```
  - Description: Fires the specified event for the current country.
  - Notes:
    ```text
    Where triggers do not need to be repeatedly checked
    random
    can be a performance light alternative to
    mean_time_to_happen
    for scheduling events. Shortened variant exists if the event's ID is used instead of arguments.
    ```
  - Version Added: 1.0

- **news_event**
  - Parameters:
    ```text
    id = <event>
    The event to fire.
    days = <int> / <variable>
    Fires the event in the specified number of days. Optional.
    hours = <int> / <variable>
    Fires the event in the specified number of hours. Optional.
    random_hours = <int> / <variable>
    Adds a random number (between
    0
    and
    random_hours
    , inclusive) of
    hours
    to the scheduled fire time. Optional.
    random_days = <int> / <variable>
    Adds a random number (between
    0
    and
    random_days
    , inclusive) of days to the scheduled fire time. Optional.
    ```
  - Example:
    ```text
    news_event = {
        id = my_event.1
        days = 10
        random_hours = 12
        random_days = 10
    }
    ```
  - Example:
    ```text
    news_event = my_event.1
    ```
  - Description: Fires the specified news event for the current country.
  - Notes:
    ```text
    The news event uses a different interface to the country event.
    Where triggers do not need to be repeatedly checked
    random
    can be a performance light alternative to
    mean_time_to_happen
    for scheduling events. Shortened variant exists if the event's ID is used instead of arguments.
    ```
  - Version Added: 1.0

- **set_cosmetic_tag**
  - Parameters:
    ```text
    <string>
    The cosmetic tag to switch to.
    ```
  - Example:
    ```text
    set_cosmetic_tag = SAF_SOV_communism
    ```
  - Description: Makes the current scope use the specified cosmetic tag, changing name and flag.
  - Version Added: 1.3

- **drop_cosmetic_tag**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    drop_cosmetic_tag = yes
    ```
  - Description: Makes the current scope drop the current cosmetic tag they are using.
  - Version Added: 1.3

- **set_rule**
  - Parameters:
    ```text
    <rule>
    Boolean.
    desc = <localisation key>
    The localisation used as the description for why the rule is set.
    ```
  - Example:
    ```text
    set_rule = {
        desc = TAG_my_rule_description
        can_create_factions = yes
    }
    ```
  - Description: Toggles the special game rules for the current scope. Note: each rule can only be toggled a few times before a reload is required.
  - Notes:
    ```text
    Game rule list
    The following game rules exist as possible options:
    Internal name
    Localised name
    Notes
    can_access_market
    Can access International Market (
    Puppets
    and
    Overlords
    can always access each other's market)
    can_be_spymaster
    Can be Spy Master
    can_boost_other_ideologies
    Can boost popularity of other ideologies
    can_boost_own_ideology
    Can boost own party popularity in other countries
    can_create_collaboration_government
    Can create collaboration governments
    can_create_factions
    Can Create Factions
    can_declare_war_on_same_ideology
    Can declare war on country with the same ideology group without a war goal
    can_declare_war_without_wargoal_when_in_war
    Can declare war on a neighbor without a wargoal when at war with a major
    can_decline_call_to_war
    Can decline call to war
    can_force_government
    Can force government of another country to adopt the same ideology
    can_generate_female_aces
    Women in your country are allowed to become military pilots
    can_generate_female_country_leaders
    Can generate female country leaders
    can_generate_female_unit_leaders
    Can generate female unit leaders
    can_guarantee_other_ideologies
    Can guarantee other ideologies
    can_join_factions
    Can join factions
    can_join_factions_not_allowed_diplomacy
    Country's name
    is not allowed to join factions
    can_join_opposite_factions
    Can Join Factions led by another Ideology
    can_lower_tension
    Lowers World Tension with Guarantees
    can_not_build_buildings
    CAN_NOT_BUILD_BUILDINGS
    Doesn't seem to work.
    can_not_declare_war
    Can not declare wars
    Prevents generating wargoals, but not using existing ones.
    can_occupy_non_war
    Can hold territory owned by a country they are not at war with
    can_only_justify_war_on_threat_country
    Can justify war goals against a country that have not generated world tension
    can_puppet
    Can puppet a country
    can_send_volunteers
    Can send volunteer forces
    can_use_kamikaze_pilots
    Can use kamikaze pilots
    contributes_operatives
    Contributes Operatives to Spy Master: Yes
    Only has an effect for subjects.
    units_deployed_to_overlord
    Control over deployed units go to overlord
    Only has an effect for subjects.
    ```
  - Version Added: Game rule list
  - Column 7:
    ```text
    The following game rules exist as possible options:
    Internal name
    Localised name
    Notes
    can_access_market
    Can access International Market (
    Puppets
    and
    Overlords
    can always access each other's market)
    can_be_spymaster
    Can be Spy Master
    can_boost_other_ideologies
    Can boost popularity of other ideologies
    can_boost_own_ideology
    Can boost own party popularity in other countries
    can_create_collaboration_government
    Can create collaboration governments
    can_create_factions
    Can Create Factions
    can_declare_war_on_same_ideology
    Can declare war on country with the same ideology group without a war goal
    can_declare_war_without_wargoal_when_in_war
    Can declare war on a neighbor without a wargoal when at war with a major
    can_decline_call_to_war
    Can decline call to war
    can_force_government
    Can force government of another country to adopt the same ideology
    can_generate_female_aces
    Women in your country are allowed to become military pilots
    can_generate_female_country_leaders
    Can generate female country leaders
    can_generate_female_unit_leaders
    Can generate female unit leaders
    can_guarantee_other_ideologies
    Can guarantee other ideologies
    can_join_factions
    Can join factions
    can_join_factions_not_allowed_diplomacy
    Country's name
    is not allowed to join factions
    can_join_opposite_factions
    Can Join Factions led by another Ideology
    can_lower_tension
    Lowers World Tension with Guarantees
    can_not_build_buildings
    CAN_NOT_BUILD_BUILDINGS
    Doesn't seem to work.
    can_not_declare_war
    Can not declare wars
    Prevents generating wargoals, but not using existing ones.
    can_occupy_non_war
    Can hold territory owned by a country they are not at war with
    can_only_justify_war_on_threat_country
    Can justify war goals against a country that have not generated world tension
    can_puppet
    Can puppet a country
    can_send_volunteers
    Can send volunteer forces
    can_use_kamikaze_pilots
    Can use kamikaze pilots
    contributes_operatives
    Contributes Operatives to Spy Master: Yes
    Only has an effect for subjects.
    units_deployed_to_overlord
    Control over deployed units go to overlord
    Only has an effect for subjects.
    ```
  - Column 8: Internal name
  - Column 9: Localised name
  - Column 10: Notes
  - Column 11: can_access_market
  - Column 12:
    ```text
    Can access International Market (
    Puppets
    and
    Overlords
    can always access each other's market)
    ```
  - Column 14: can_be_spymaster
  - Column 15: Can be Spy Master
  - Column 17: can_boost_other_ideologies
  - Column 18: Can boost popularity of other ideologies
  - Column 20: can_boost_own_ideology
  - Column 21: Can boost own party popularity in other countries
  - Column 23: can_create_collaboration_government
  - Column 24: Can create collaboration governments
  - Column 26: can_create_factions
  - Column 27: Can Create Factions
  - Column 29: can_declare_war_on_same_ideology
  - Column 30: Can declare war on country with the same ideology group without a war goal
  - Column 32: can_declare_war_without_wargoal_when_in_war
  - Column 33: Can declare war on a neighbor without a wargoal when at war with a major
  - Column 35: can_decline_call_to_war
  - Column 36: Can decline call to war
  - Column 38: can_force_government
  - Column 39: Can force government of another country to adopt the same ideology
  - Column 41: can_generate_female_aces
  - Column 42: Women in your country are allowed to become military pilots
  - Column 44: can_generate_female_country_leaders
  - Column 45: Can generate female country leaders
  - Column 47: can_generate_female_unit_leaders
  - Column 48: Can generate female unit leaders
  - Column 50: can_guarantee_other_ideologies
  - Column 51: Can guarantee other ideologies
  - Column 53: can_join_factions
  - Column 54: Can join factions
  - Column 56: can_join_factions_not_allowed_diplomacy
  - Column 57:
    ```text
    Country's name
    is not allowed to join factions
    ```
  - Column 59: can_join_opposite_factions
  - Column 60: Can Join Factions led by another Ideology
  - Column 62: can_lower_tension
  - Column 63: Lowers World Tension with Guarantees
  - Column 65: can_not_build_buildings
  - Column 66: CAN_NOT_BUILD_BUILDINGS
  - Column 67: Doesn't seem to work.
  - Column 68: can_not_declare_war
  - Column 69: Can not declare wars
  - Column 70: Prevents generating wargoals, but not using existing ones.
  - Column 71: can_occupy_non_war
  - Column 72: Can hold territory owned by a country they are not at war with
  - Column 74: can_only_justify_war_on_threat_country
  - Column 75: Can justify war goals against a country that have not generated world tension
  - Column 77: can_puppet
  - Column 78: Can puppet a country
  - Column 80: can_send_volunteers
  - Column 81: Can send volunteer forces
  - Column 83: can_use_kamikaze_pilots
  - Column 84: Can use kamikaze pilots
  - Column 86: contributes_operatives
  - Column 87: Contributes Operatives to Spy Master: Yes
  - Column 88: Only has an effect for subjects.
  - Column 89: units_deployed_to_overlord
  - Column 90: Control over deployed units go to overlord
  - Column 91: Only has an effect for subjects.
  - Column 92: 1.0

- **Game rule list**

- **The following game rules exist as possible options:**
  - Parameters: Internal name
  - Examples: Localised name
  - Description: Notes
  - Notes: can_access_market
  - Version Added:
    ```text
    Can access International Market (
    Puppets
    and
    Overlords
    can always access each other's market)
    ```
  - Column 8: can_be_spymaster
  - Column 9: Can be Spy Master
  - Column 11: can_boost_other_ideologies
  - Column 12: Can boost popularity of other ideologies
  - Column 14: can_boost_own_ideology
  - Column 15: Can boost own party popularity in other countries
  - Column 17: can_create_collaboration_government
  - Column 18: Can create collaboration governments
  - Column 20: can_create_factions
  - Column 21: Can Create Factions
  - Column 23: can_declare_war_on_same_ideology
  - Column 24: Can declare war on country with the same ideology group without a war goal
  - Column 26: can_declare_war_without_wargoal_when_in_war
  - Column 27: Can declare war on a neighbor without a wargoal when at war with a major
  - Column 29: can_decline_call_to_war
  - Column 30: Can decline call to war
  - Column 32: can_force_government
  - Column 33: Can force government of another country to adopt the same ideology
  - Column 35: can_generate_female_aces
  - Column 36: Women in your country are allowed to become military pilots
  - Column 38: can_generate_female_country_leaders
  - Column 39: Can generate female country leaders
  - Column 41: can_generate_female_unit_leaders
  - Column 42: Can generate female unit leaders
  - Column 44: can_guarantee_other_ideologies
  - Column 45: Can guarantee other ideologies
  - Column 47: can_join_factions
  - Column 48: Can join factions
  - Column 50: can_join_factions_not_allowed_diplomacy
  - Column 51:
    ```text
    Country's name
    is not allowed to join factions
    ```
  - Column 53: can_join_opposite_factions
  - Column 54: Can Join Factions led by another Ideology
  - Column 56: can_lower_tension
  - Column 57: Lowers World Tension with Guarantees
  - Column 59: can_not_build_buildings
  - Column 60: CAN_NOT_BUILD_BUILDINGS
  - Column 61: Doesn't seem to work.
  - Column 62: can_not_declare_war
  - Column 63: Can not declare wars
  - Column 64: Prevents generating wargoals, but not using existing ones.
  - Column 65: can_occupy_non_war
  - Column 66: Can hold territory owned by a country they are not at war with
  - Column 68: can_only_justify_war_on_threat_country
  - Column 69: Can justify war goals against a country that have not generated world tension
  - Column 71: can_puppet
  - Column 72: Can puppet a country
  - Column 74: can_send_volunteers
  - Column 75: Can send volunteer forces
  - Column 77: can_use_kamikaze_pilots
  - Column 78: Can use kamikaze pilots
  - Column 80: contributes_operatives
  - Column 81: Contributes Operatives to Spy Master: Yes
  - Column 82: Only has an effect for subjects.
  - Column 83: units_deployed_to_overlord
  - Column 84: Control over deployed units go to overlord
  - Column 85: Only has an effect for subjects.

- **Internal name**
  - Parameters: Localised name
  - Examples: Notes

- **can_access_market**
  - Parameters:
    ```text
    Can access International Market (
    Puppets
    and
    Overlords
    can always access each other's market)
    ```

- **can_be_spymaster**
  - Parameters: Can be Spy Master

- **can_boost_other_ideologies**
  - Parameters: Can boost popularity of other ideologies

- **can_boost_own_ideology**
  - Parameters: Can boost own party popularity in other countries

- **can_create_collaboration_government**
  - Parameters: Can create collaboration governments

- **can_create_factions**
  - Parameters: Can Create Factions

- **can_declare_war_on_same_ideology**
  - Parameters: Can declare war on country with the same ideology group without a war goal

- **can_declare_war_without_wargoal_when_in_war**
  - Parameters: Can declare war on a neighbor without a wargoal when at war with a major

- **can_decline_call_to_war**
  - Parameters: Can decline call to war

- **can_force_government**
  - Parameters: Can force government of another country to adopt the same ideology

- **can_generate_female_aces**
  - Parameters: Women in your country are allowed to become military pilots

- **can_generate_female_country_leaders**
  - Parameters: Can generate female country leaders

- **can_generate_female_unit_leaders**
  - Parameters: Can generate female unit leaders

- **can_guarantee_other_ideologies**
  - Parameters: Can guarantee other ideologies

- **can_join_factions**
  - Parameters: Can join factions

- **can_join_factions_not_allowed_diplomacy**
  - Parameters:
    ```text
    Country's name
    is not allowed to join factions
    ```

- **can_join_opposite_factions**
  - Parameters: Can Join Factions led by another Ideology

- **can_lower_tension**
  - Parameters: Lowers World Tension with Guarantees

- **can_not_build_buildings**
  - Parameters: CAN_NOT_BUILD_BUILDINGS
  - Examples: Doesn't seem to work.

- **can_not_declare_war**
  - Parameters: Can not declare wars
  - Examples: Prevents generating wargoals, but not using existing ones.

- **can_occupy_non_war**
  - Parameters: Can hold territory owned by a country they are not at war with

- **can_only_justify_war_on_threat_country**
  - Parameters: Can justify war goals against a country that have not generated world tension

- **can_puppet**
  - Parameters: Can puppet a country

- **can_send_volunteers**
  - Parameters: Can send volunteer forces

- **can_use_kamikaze_pilots**
  - Parameters: Can use kamikaze pilots

- **contributes_operatives**
  - Parameters: Contributes Operatives to Spy Master: Yes
  - Examples: Only has an effect for subjects.

- **units_deployed_to_overlord**
  - Parameters: Control over deployed units go to overlord
  - Examples: Only has an effect for subjects.

- **set_party_rule**
  - Parameters:
    ```text
    ideology = <ideology group>
    Ideology group of the party.
    desc = <localisation key>
    A description used for the rule. Optional, defaults to being the same as default.
    <rule> = <bool>
    Rule's new value.
    ```
  - Example:
    ```text
    set_party_rule = {
        ideology = democratic
        desc = TAG_my_rule_description
        can_create_factions = yes
    }
    ```
  - Description: Toggles the special game rules for the current scope's political party.
  - Version Added: 1.12

- **add_relation_rule_override**
  - Parameters:
    ```text
    target = <country>
    Target of the rule.
    usage_desc = <localisation key>
    A description used as the reason for the rule applying. Optional.
    trigger = <scripted trigger>
    A
    scripted trigger
    deciding when the override should be active. Optional, defaults to always true.
    <rule> = <bool>
    Rule's new value.
    ```
  - Example:
    ```text
    add_relation_rule_override = {
        target = SOV
        usage_desc = TAG_my_rule_description
        trigger = my_scripted_trigger
        can_access_market = yes
    }
    ```
  - Description: Toggles the special game rules for the current scope in diplomacy towards the specified country only, if the trigger is met.
  - Notes:
    ```text
    Currently
    can_access_market
    and
    can_send_volunteers
    are supported. In case of overlap, restricting actions is preferred (e.g.
    can_send_volunteers = no
    or
    can_not_declare_war = yes
    are preferred over the alternatives). In the scripted trigger,
    ROOT
    is the country with the override and
    FROM
    is the target.
    ```
  - Version Added: 1.13

- **remove_relation_rule_override**
  - Parameters:
    ```text
    target = <country>
    Target of the rule.
    usage_desc = <localisation key>
    A description used as the reason for the rule applying. Optional.
    trigger = <scripted trigger>
    A
    scripted trigger
    for identifying the relation rule.
    <rule> = <bool>
    Rule's new value.
    ```
  - Example:
    ```text
    remove_relation_rule_override = {
        target = SOV
        usage_desc = TAG_my_rule_description
        can_access_market = yes
    }
    ```
  - Description:
    ```text
    Removes the toggle added with
    add_relation_rule_override
    .
    ```
  - Version Added: 1.13

- **scoped_sound_effect**
  - Parameters:
    ```text
    <string>
    A sound reference from an .asset file.
    ```
  - Example:
    ```text
    scoped_sound_effect = "boom"
    ```
  - Description: Plays the specified sound once only for the current country.
  - Notes:
    ```text
    The sound effect must be properly defined in
    /Hearts of Iron IV/sound/
    More info can be found in the
    Sound modding
    article.
    ```
  - Version Added: 1.6

- **scoped_play_song**
  - Parameters:
    ```text
    <song title from .asset>
    A music file located in the music folder and .asset
    ```
  - Example:
    ```text
    scoped_play_song = "general_peace_1"
    ```
  - Description: Plays an audio track for the specified country only.
  - Notes:
    ```text
    The song must be defined in a music station in order to work. More information can be found in the
    Music modding
    page. If you wish to simply play a sound, the scoped_sound_effect effect should be used instead.
    ```
  - Version Added: 1.9.3

- **goto_province**
  - Parameters:
    ```text
    <id>
    The id of the province go to.
    ```
  - Example:
    ```text
    goto_province = 325
    ```
  - Description: Moves the camera position over the specified province.
  - Version Added: 1.0

- **goto_state**
  - Parameters:
    ```text
    <state> / <variable>
    The id of the state go to.
    ```
  - Example:
    ```text
    goto_state = 1
    ```
  - Example:
    ```text
    goto_state = var:some_state
    ```
  - Description: Moves the camera position over the specified state.
  - Version Added: 1.0

- **change_tag_from**
  - Parameters:
    ```text
    <country> / <variable>
    The country to change from.
    ```
  - Example:
    ```text
    change_tag_from = ROOT
    ```
  - Example:
    ```text
    change_tag_from = var:from.country
    ```
  - Description: Switches the player to the current scope from the target scope. Nothing happens if the target scope is controlled by AI.
  - Notes:
    ```text
    The country the player becomes needs to be the scope in which the command is used.
    For example,
    ABC = { change_tag_from = XYZ }
    will make the player controlling XYZ play as ABC instead.
    ```
  - Version Added: 1.0

- **reserve_dynamic_country**
  - Parameters: <bool>
  - Example:
    ```text
    reserve_dynamic_country = yes
    ```
  - Description: Reserves the dynamic country, making sure that it does not get recycled for civil war even if it does not exist.
  - Notes:
    ```text
    Usually used in combination with
    create_dynamic_country
    .
    ```
  - Version Added: 1.9

- **force_update_map_mode**
  - Parameters:
    ```text
    limit = { ... }
    Triggers required for the map mode to refresh. Optional.
    mapmode = <id>
    The ID of the custom map mode.
    ```
  - Example:
    ```text
    force_update_map_mode = {
        limit = {
            is_ai = no
        }
        mapmode = my_map_mode
    }
    ```
  - Description: Forcefully refreshes the specified mapmode for the player, rather than waiting for a daily update.
  - Notes:
    ```text
    Map modes are defined in
    /Hearts of Iron IV/common/map_modes/*.txt
    ```
  - Version Added: 1.11

- **add_ai_strategy**
  - Parameters:
    ```text
    type = <type>
    The type of strategy.
    id = <country>
    What country the strategy is against.
    value = <int>
    The weighting added by the strategy.
    ```
  - Example:
    ```text
    add_ai_strategy = {
        type = alliance
        id = GER
        value = 200
    }
    ```
  - Description: Sets an AI strategy for the current scope.
  - Notes:
    ```text
    See
    AI Modding
    for more details.
    ```
  - Version Added: 1.0

- **create_dynamic_country**
  - Parameters:
    ```text
    original_tag = <tag>
    The original tag to be used by the country.
    copy_tag = <tag>
    If specified, copies stuff from this tag rather than the original tag.
    <effects>
    Effects that will be executed on the new dynamic country.
    ```
  - Example:
    ```text
    create_dynamic_country = {
        original_tag = POL
        copy_tag = SOV
        add_political_power = 100
        transfer_state = 123
    }
    ```
  - Description: Creates a new dynamic country, akin to ones used in civil wars.
  - Notes:
    ```text
    The
    reserve_dynamic_country
    effect can be used if the dynamic country does not yet exist in order to ensure that it does not get overwritten by other creations of dynamic countries. If this is not done, the dynamic country will immediately stop existing if no states are transferred in the same scope.
    Every state of the original country immediately gets set as a dynamic country's core: if that's unneeded, the cores would need to be removed after creation.
    ```
  - Version Added: 1.9

### States

These effects in particular are country-scoped effects that are related to states rather than effects within the state scope.

- **add_state_core**
  - Parameters:
    ```text
    <state> / <variable>
    The state to add core to.
    ```
  - Example:
    ```text
    add_state_core = 345
    ```
  - Description: Adds a core for the current scope to the specified state.
  - Version Added: 1.0

- **remove_state_core**
  - Parameters:
    ```text
    <state> / <variable>
    The state to remove core from.
    ```
  - Example:
    ```text
    remove_state_core = 345
    ```
  - Description: Removes the core of the current scope from the specified state.
  - Version Added: 1.0

- **set_capital**
  - Parameters:
    ```text
    state = <state> / <variable>
    The state to make capital.
    remember_old_capital = no
    Whether the old capital gets "remembered", making the country change to it in case the current capital is lost.
    ```
  - Example:
    ```text
    set_capital = {state = 345}
    ```
  - Example:
    ```text
    set_capital = {
      state = 345
      remember_old_capital = no
    }
    ```
  - Description: Makes the specified state the current scope's capital state.
  - Notes:
    ```text
    Syntax has been changed in 1.11.
    It was "set_capital = 345"
    Old capital is remembered, if not specified otherwise.
    ```
  - Version Added: 1.0

- **add_state_claim**
  - Parameters:
    ```text
    <state> / <variable>
    The state to add a claim to.
    ```
  - Example:
    ```text
    add_state_claim = 345
    ```
  - Description: Adds a claim for the current scope on the specified state.
  - Version Added: 1.0

- **remove_state_claim**
  - Parameters:
    ```text
    <state> / <variable>
    The state to remove the claim from.
    ```
  - Example:
    ```text
    remove_state_claim = 345
    ```
  - Description: Removes a claim of the current scope from the specified state.
  - Version Added: 1.0

- **set_state_owner**
  - Parameters:
    ```text
    <state> / <variable>
    The state to change ownership of.
    ```
  - Example:
    ```text
    set_state_owner = 345
    ```
  - Description: Makes the current scope the owner of the specified state.
  - Notes:
    ```text
    This can fail to carry over the control, so it's recommended to instead use
    transfer_state
    unless transferring the ownership without transferring over the control.
    ```
  - Version Added: 1.0

- **set_state_controller**
  - Parameters:
    ```text
    <state> / <variable>
    The state to change controller of.
    ```
  - Example:
    ```text
    set_state_controller = 345
    ```
  - Description: Makes the current scope the controller of the specified state.
  - Version Added: 1.0

- **add_contested_owner**
  - Parameters:
    ```text
    <state> / <variable>
    State to contest.
    ```
  - Example:
    ```text
    add_contested_owner = 42
    ```
  - Description: Adds a contested owner to a state. The effect can be used either from a country or a state scope and accepts the other as parameter.
  - Notes: Can also be used in state scope.
  - Version Added: 1.15

- **remove_contested_owner**
  - Parameters:
    ```text
    <state> / <variable>
    State to stop contest.
    ```
  - Example:
    ```text
    remove_contested_owner = 42
    ```
  - Description: Removes a contested owner to a state. The effect can be used either from a country or a state scope and accepts the other as parameter.
  - Notes: Can also be used in state scope.
  - Version Added: 1.15

- **transfer_state**
  - Parameters:
    ```text
    <state> / <variable>
    The state to change owner and controller of.
    ```
  - Example:
    ```text
    transfer_state = 345
    ```
  - Description: Makes the current scope the owner and controller of the specified state.
  - Notes:
    ```text
    transfer_state_to
    exists as a state-scoped variant.
    ```
  - Version Added: 1.0

- **set_province_controller**
  - Parameters:
    ```text
    <id>
    The province to change controller of.
    ```
  - Example:
    ```text
    set_province_controller = 2999
    ```
  - Description: Changes the controller of the specified province to the current scope.
  - Notes: A peace conference or the controller being at peace will reset the control of the province to the owner unless the controller is at war with the owner.
  - Version Added: 1.0

### Mana

Mana in this usage means political power, stability, war support, and other values in the topbar. Fuel is, instead, in the [resources section](#resources), while convoys can be added/removed with [add\_equipment\_to\_stockpile](#add-equipment-to-stockpile).

- **add_political_power**
  - Parameters:
    ```text
    <int> / <variable>
    The amount to add.
    ```
  - Example:
    ```text
    add_political_power = 100
    ```
  - Example:
    ```text
    add_political_power = var:my_var
    ```
  - Description: Adds the specified amount of political power to the current scope.
  - Version Added: 1.0

- **set_political_power**
  - Parameters:
    ```text
    <int> / <variable>
    The amount to add.
    ```
  - Example:
    ```text
    set_political_power = 100
    ```
  - Description: Sets the specified amount of political power for the current scope.
  - Version Added: 1.0

- **add_stability**
  - Parameters:
    ```text
    <int> / <variable>
    The amount to add.
    ```
  - Example:
    ```text
    add_stability = 0.1
    ```
  - Description: Adds to the current stability value for the current scope.
  - Notes: Stability values are between 0 and 1.
  - Version Added: 1.5

- **set_stability**
  - Parameters:
    ```text
    <int> / <variable>
    The amount to add.
    ```
  - Example:
    ```text
    set_stability = 0.5
    ```
  - Description: Sets the current stability value for the current scope.
  - Notes: Stability values are between 0 and 1.
  - Version Added: 1.5

- **add_war_support**
  - Parameters:
    ```text
    <int> / <variable>
    The amount to add.
    ```
  - Example:
    ```text
    add_war_support = 0.1
    ```
  - Description: Adds to the current war support value for the current scope.
  - Notes: War Support values are between 0 and 1.
  - Version Added: 1.5

- **set_war_support**
  - Parameters:
    ```text
    <int> / <variable>
    The amount to set.
    ```
  - Example:
    ```text
    set_war_support = 0.5
    ```
  - Description: Sets the current war support value for the current scope.
  - Notes: War Support values are between 0 and 1.
  - Version Added: 1.5

- **add_command_power**
  - Parameters:
    ```text
    <int> / <variable>
    The amount to add.
    ```
  - Example:
    ```text
    add_command_power = 100
    ```
  - Description: Adds the specified amount of command power to the current scope.
  - Version Added: 1.5

- **add_manpower**
  - Parameters:
    ```text
    <int> / <variable>
    The amount to add.
    ```
  - Example:
    ```text
    add_manpower = 100000
    ```
  - Example:
    ```text
    add_manpower = var:my_var
    ```
  - Description: Adds the specified amount of manpower to the current scope.
  - Version Added: 1.0

- **army_experience**
  - Parameters:
    ```text
    <float> / <variable>
    The amount to add.
    ```
  - Example:
    ```text
    army_experience = 10
    ```
  - Description: Adds the specified amount of army experience to the current scope.
  - Version Added: 1.0

- **navy_experience**
  - Parameters:
    ```text
    <float> / <variable>
    The amount to add.
    ```
  - Example:
    ```text
    navy_experience = 10
    ```
  - Description: Adds the specified amount of navy experience to the current scope.
  - Version Added: 1.0

- **air_experience**
  - Parameters:
    ```text
    <float> / <variable>
    The amount to add.
    ```
  - Example:
    ```text
    air_experience = 10
    ```
  - Description: Adds the specified amount of air experience to the current scope.
  - Version Added: 1.0

### Politics

- **set_politics**
  - Parameters:
    ```text
    ruling_party = <ideology>
    The party to set.
    elections_allowed = <bool>
    Whether elections are allowed. Optional.
    last_election = <date>
    When the last election was. Optional.
    election_frequency = <int>
    How often in months an election occurs. Optional.
    long_name = <string>
    The long name of the country's new ruling party, appearing when hovering over it. Optional.
    name = <string>
    The name of the country's new ruling party. Optional.
    ```
  - Example:
    ```text
    set_politics = {
        ruling_party = democratic
        elections_allowed = no
        last_election = "1935.12.17"
        election_frequency = 48
        long_name = TAG_party_long
        name = TAG_party
    }
    ```
  - Description: Sets the political status of the country, including the ruling party and elections.
  - Notes:
    ```text
    Before 1.7, included
    parties = { ... }
    for assigning party popularities, which has been moved to
    set_popularities
    ```
  - Version Added: 1.0 (updated 1.7)

- **set_popularities**
  - Parameters:
    ```text
    <ideology> = <int>/<variable>
    The popularity to set.
    ```
  - Example:
    ```text
    set_popularities = {
    	democratic = 50
    	neutrality = 15
    	fascism = 30
    	communism = 5
    }
    ```
  - Description: Sets the political party popularities for the current scope.
  - Notes: The popularities must add up to 100, otherwise the command will have no effect.
  - Version Added: 1.7

- **add_popularity**
  - Parameters:
    ```text
    ideology = <ideology/tag>
    The party to change. If using a tag, uses that tag's ruling party.
    popularity = <int> / <variable>
    The amount of popularity to change.
    ```
  - Example:
    ```text
    add_popularity = {
        ideology = fascism
        popularity = -0.5
    }
    ```
  - Description: Adjusts the popularity for the specified party in the current scope.
  - Notes:
    ```text
    Values used are 0 to 1.
    You can use ideology = ROOT to increase the popularity of the currently ruling party.
    ```
  - Version Added: 1.0

- **set_political_party**
  - Parameters:
    ```text
    ideology = <ideology>
    The party to change.
    popularity = <int>
    The amount of popularity to set.
    ```
  - Example:
    ```text
    set_political_party = {
        ideology = fascism
        popularity = 50
    }
    ```
  - Description: Sets the popularity for the specified political party in the current scope.
  - Version Added: 1.0

- **set_party_name**
  - Parameters:
    ```text
    ideology = <ideology>
    The party to change.
    long_name = <string>
    The new full name for the party.
    name = <string>
    The new short name for the party.
    ```
  - Example:
    ```text
    set_party_name = {
        ideology = neutrality
        long_name = GER_neutrality_party_kaiserreich_long
        name = GER_neutrality_party_kaiserreich
    }
    ```
  - Description: Changes the name of the specified political party for the current scope.
  - Notes: The name appears in the country politics/diplomacy view, the long name appears in the tooltip when hovering over the party.
  - Version Added: 1.0

- **hold_election**
  - Parameters:
    ```text
    <country>
    The country to hold an election for.
    ```
  - Example:
    ```text
    hold_election = ROOT
    ```
  - Description:
    ```text
    Executes the events in the
    on_new_term_election
    on action for the current scope.
    ```
  - Version Added: 1.0

### Balance of power

Balance of power is defined in /Hearts of Iron IV/common/bop/\*.txt files.

- **set_power_balance**
  - Parameters:
    ```text
    id = <BoP ID>
    Balance of power to set/modify.
    left_side = <BoP side ID>
    The left side of the BoP.
    right_side = <BoP side ID>
    The right side of the BoP.
    set_default = <bool>
    Resets the BoP to the initial state defined in the file. Optional, defaults to false.
    set_value = <decimal>
    The new value of the BoP. Optional, defaults to not changing the value.
    ```
  - Example:
    ```text
    set_power_balance = {
        id = my_bop
        left_side = my_bop_left_side
        right_side = my_bop_right_side
    }
    ```
  - Description: Sets a new balance of power or edits the existing one.
  - Notes:
    ```text
    Necessary for a balance of power to appear. For the default state,
    initial_value
    ,
    left_side
    , and
    right_side
    directly inside of the BoP are read.
    ```
  - Version Added: 1.12

- **remove_power_balance**
  - Parameters:
    ```text
    id = <BoP ID>
    Balance of power to modify.
    ```
  - Example:
    ```text
    remove_power_balance = {
        id = my_bop
    }
    ```
  - Description: Removes the balance of power in entirety.
  - Version Added: 1.12

- **add_power_balance_value**
  - Parameters:
    ```text
    id = <BoP ID>
    Balance of power to modify.
    value = <decimal>
    The value to add.
    tooltip_side = <BoP side ID>
    The side to show in the tooltip. Optional.
    ```
  - Example:
    ```text
    add_power_balance_value = {
        id = my_bop
        value = -0.1
        tooltip_side = my_bop_side
    }
    ```
  - Description: Pushes the balance of power towards one side.
  - Version Added: 1.12

- **add_power_balance_modifier**
  - Parameters:
    ```text
    id = <BoP ID>
    Balance of power to modify.
    modifier = <static modifier>
    The
    static modifier
    to apply.
    ```
  - Example:
    ```text
    add_power_balance_modifier = {
        id = my_bop
        modifier = my_static_modifier
    }
    ```
  - Description: Applies a balance of power modifier.
  - Version Added: 1.12

- **remove_power_balance_modifier**
  - Parameters:
    ```text
    id = <BoP ID>
    Balance of power to modify.
    modifier = <static modifier>
    The
    static modifier
    to apply.
    ```
  - Example:
    ```text
    remove_power_balance_modifier = {
        id = my_bop
        modifier = my_static_modifier
    }
    ```
  - Description: Cancels a balance of power modifier.
  - Version Added: 1.12

- **remove_all_power_balance_modifiers**
  - Parameters:
    ```text
    id = <BoP ID>
    Balance of power to modify.
    ```
  - Example:
    ```text
    remove_all_power_balance_modifiers = {
        id = my_bop
    }
    ```
  - Description: Cancels all balance of power modifiers.
  - Version Added: 1.12

- **set_power_balance_gfx**
  - Parameters:
    ```text
    id = <BoP ID>
    Balance of power to modify.
    side = <BoP side ID>
    The side whose GFX to change.
    gfx = <sprite>
    The sprite to change the GFX to.
    ```
  - Example:
    ```text
    set_power_balance_gfx = {
        id = my_bop
        side = my_bop_side
        gfx = GFX_my_bop_side_new
    }
    ```
  - Description: Changes the appearance of one of the sides within the balance of power.
  - Notes:
    ```text
    Sprites are defined within
    /Hearts of Iron IV/interface/*.gfx
    files.
    ```
  - Version Added: 1.12

### Diplomacy

- **set_major**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    set_major = yes
    ```
  - Description: Makes the current scope a major country.
  - Version Added: 1.0

- **release**
  - Parameters:
    ```text
    <country>
    The target country.
    ```
  - Example:
    ```text
    release = GER
    ```
  - Description: Releases the specified non-existent country as a free nation within the current country's owned states.
  - Notes: The effect does nothing if the country exists. All states that are cored by the specified country will be given to it. If the current country has a core on a state transferred to the released country, the core will be lost. If looking to make a subject into an independent nation, use set_autonomy. States that are owned but not controlled will be transferred to the released country, but won't be controlled by it.
  - Version Added: 1.0

- **release_on_controlled**
  - Parameters:
    ```text
    <country>
    The target country.
    ```
  - Example:
    ```text
    release_on_controlled = GER
    ```
  - Description: Releases the specified non-existent country as a free nation within the current country's controlled states.
  - Notes: The effect does nothing if the country exists. All states that are cored by the specified country will be given to it. If the current country has a core on a state transferred to the released country, the core will be lost.
  - Version Added: 1.9.1

- **release_puppet**
  - Parameters:
    ```text
    <country>
    The target country.
    ```
  - Example:
    ```text
    release_puppet = GER
    ```
  - Description: Releases the specified non-existent country as a puppet of the current scope within the current country's owned states.
  - Notes: The effect does nothing if the country exists. All states that are cored by the specified country will be given to it. If the current country has a core on a state transferred to the released country, the core will be lost. States that are owned but not controlled will be transferred to the released country, but won't be controlled by it.
  - Version Added: 1.0

- **release_puppet_on_controlled**
  - Parameters:
    ```text
    <country>
    The target country.
    ```
  - Example:
    ```text
    release_puppet_on_controlled = GER
    ```
  - Description: Releases the specified non-existent country as a puppet of the current scope within the current country's controlled states.
  - Notes: The effect does nothing if the country exists. All states that are cored by the specified country will be given to it. If the current country has a core on a state transferred to the released country, the core will be lost.
  - Version Added: 1.9.1

- **release_autonomy**
  - Parameters:
    ```text
    target = <country> / <variable>
    The subject country.
    autonomy_state = <type>
    The type of autonomy state to set.
    freedom_level = <float>
    The new freedom level value. Optional.
    ```
  - Example:
    ```text
    release_autonomy = {
        target = VIN
        autonomy_state = autonomy_puppet
        freedom_level = 0.5
    }
    ```
  - Description: Releases the specified non-existent country as a subject of the specified autonomy of the current scope within the current country's owned states.
  - Notes:
    ```text
    The effect does nothing if the country exists. All states that are cored by the specified country will be given to it. If the current country has a core on a state transferred to the released country, the core will be lost. States that are owned but not controlled will be transferred to the released country, but won't be controlled by it. The autonomy states are found in
    /Hearts of Iron IV/common/autonomous_states/*.txt
    .
    ```
  - Version Added: 1.3

- **give_guarantee**
  - Parameters:
    ```text
    <country>
    The target country.
    ```
  - Example:
    ```text
    give_guarantee = GER
    ```
  - Description: The current scope guarantees the target country.
  - Notes:
    ```text
    diplomatic_relation
    effect can be used to remove it.
    ```
  - Version Added: 1.0

- **give_military_access**
  - Parameters:
    ```text
    <country>
    The target country.
    ```
  - Example:
    ```text
    give_military_access = GER
    ```
  - Description: The current scope grants military access to the target country.
  - Notes:
    ```text
    diplomatic_relation
    effect can be used to remove it.
    ```
  - Version Added: 1.0

- **recall_attache**
  - Parameters:
    ```text
    <country>
    The target country with an attache.
    ```
  - Example:
    ```text
    recall_attache = GER
    ```
  - Description: Recalls the current scope's attaché from the specified country.
  - Version Added: 1.5

- **diplomatic_relation**
  - Parameters:
    ```text
    country = <country>
    The target country to alter the relationship with ROOT.
    relation = <type>
    The relation to change.
    active = <bool>
    Whether the relation is started or broken.
    ```
  - Example:
    ```text
    diplomatic_relation = {
        country = SOV
        relation = guarantee
        active = no
    }
    ```
  - Description: Used to define a diplomatic relation between the current scope and target scope country.
  - Notes:
    ```text
    Possible relations:
    non_aggression_pact
    guarantee
    puppet
    military_access
    docking_rights
    embargo
    OFFER_AIR_BASE_ACCESS
    ```
  - Version Added: 1.0

- **add_opinion_modifier**
  - Parameters:
    ```text
    target = <country>
    The target country.
    modifier = <modifier>
    The opinion modifier to add.
    ```
  - Example:
    ```text
    add_opinion_modifier = {
        target = GER
        modifier = faction_traitor
    }
    ```
  - Description:
    ```text
    The current scope gains the specified opinion modifier
    towards the target scope
    . Can also be used to modify trade relations by adding 'trade = yes' in the opinion <modifier> in
    /Hearts of Iron IV/common/opinion_modifiers/*.txt
    . If used with a trade opinion_modifier the behaviour is reversed, meaning that the target gains the trade opinion towards the
    current scope
    .
    ```
  - Notes:
    ```text
    Opinion modifiers are found in
    /Hearts of Iron IV/common/opinion_modifiers/*.txt
    .
    ```
  - Version Added: 1.0

- **remove_opinion_modifier**
  - Parameters:
    ```text
    target = <country>
    The target country.
    modifier = <modifier>
    The opinion modifier to remove.
    ```
  - Example:
    ```text
    remove_opinion_modifier = {
        target = GER
        modifier = faction_traitor
    }
    ```
  - Description:
    ```text
    The current scope loses the specified opinion modifier
    towards the target scope
    .
    ```
  - Notes:
    ```text
    Opinion modifiers are found in
    /Hearts of Iron IV/common/opinion_modifiers/*.txt
    .
    ```
  - Version Added: 1.0

- **reverse_add_opinion_modifier**
  - Parameters:
    ```text
    target = <country>
    The target country.
    modifier = <modifier>
    The opinion modifier to add.
    ```
  - Example:
    ```text
    reverse_add_opinion_modifier = {
        target = GER
        modifier = faction_traitor
    }
    ```
  - Description:
    ```text
    The target scope gains the specified opinion modifier
    towards the current scope
    .
    ```
  - Notes:
    ```text
    Opinion modifiers are found in
    /Hearts of Iron IV/common/opinion_modifiers/*.txt
    .
    Useful for when you don't know what the current scope will be.
    ```
  - Version Added: 1.0

- **add_relation_modifier**
  - Parameters:
    ```text
    target = <country>
    The target country.
    modifier = <modifier>
    The relation modifier to add.
    ```
  - Example:
    ```text
    add_relation_modifier = {
        target = SWE
        modifier = HUN_dynastic_ties_license
    }
    ```
  - Description:
    ```text
    The current scope gains the specified relation modifier
    towards the target scope
    .
    ```
  - Notes:
    ```text
    Relation modifiers are found in
    /Hearts of Iron IV/common/modifiers/*.txt
    files, used to apply a
    targeted modifier
    with a non-static target. To change the diplomatic opinion of a country, see
    add_opinion_modifier
    .
    ```
  - Version Added: 1.4

- **remove_relation_modifier**
  - Parameters:
    ```text
    target = <country>
    The target country.
    modifier = <modifier>
    The relation modifier to remove.
    ```
  - Example:
    ```text
    remove_relation_modifier = {
        target = SWE
        modifier = HUN_dynastic_ties_license
    }
    ```
  - Description:
    ```text
    The current scope loses the specified relation modifier for
    towards the target scope
    .
    ```
  - Notes:
    ```text
    Relation modifiers are found in
    /Hearts of Iron IV/common/modifiers/*.txt
    , used to apply a
    targeted modifier
    with a non-static target. To change the diplomatic opinion of a country, see
    remove_opinion_modifier
    .
    ```
  - Version Added: 1.4

- **add_collaboration**
  - Parameters:
    ```text
    target = <country>
    The target country.
    value = <0-1>
    How much collaboration to add.
    ```
  - Example:
    ```text
    add_collaboration = {
        target = TAG
        value = 0.3
    }
    ```
  - Description: Adds collaboration in TAG with the scoped country.
  - Version Added: 1.9

- **set_collaboration**
  - Parameters:
    ```text
    target = <country>
    The target country.
    value = <0-1>
    How much collaboration will be set.
    ```
  - Example:
    ```text
    set_collaboration = {
        target = TAG
        value = 0.3
    }
    ```
  - Description: Sets the collaboration in TAG with the scoped country.
  - Version Added: 1.9

- **recall_volunteers_from**
  - Parameters:
    ```text
    <tag>
    The target country.
    ```
  - Example:
    ```text
    recall_volunteers_from = SPR
    ```
  - Description: Recalls volunteers sent to the specified country back to the current country.
  - Version Added: 1.9

- **set_occupation_law**
  - Parameters:
    ```text
    <law ID>
    The new occupation law enacted by the previous scope or
    default_law
    .
    ```
  - Examples:
    ```text
    # Changes USA's occupation law for GER.
    # Changes the USA's default occupation law to the default.
    ```
  - Example:
    ```text
    USA = {
      GER = {
        set_occupation_law = foreign_civilian_oversight
      }
    }
    ```
  - Example:
    ```text
    USA = {
      USA = {
        set_occupation_law = default_law
      }
    }
    ```
  - Description: Sets the occupation law of the country.
  - Notes:
    ```text
    PREV
    will be the country for whom the occupation law will be changed. If PREV is not a country, nothing changes. If PREV is the same country, changes the default occupation law. If PREV is different, default_law resets the country-specific law to the global default, otherwise it resets the default law to the occupation law with
    starting_law = yes
    in definition.
    Can also be used in state scope.
    ```
  - Version Added: 1.12

- **set_occupation_law_where_available**
  - Parameters:
    ```text
    <law ID>
    The new occupation law enacted by the previous scope or
    default_law
    .
    ```
  - Examples:
    ```text
    # Changes USA's occupation law for GER where possible.
    # Changes the USA's default occupation law to the default where possible.
    ```
  - Example:
    ```text
    USA = {
      GER = {
        set_occupation_law_where_available = foreign_civilian_oversight
      }
    }
    ```
  - Example:
    ```text
    USA = {
      USA = {
        set_occupation_law_where_available = default_law
      }
    }
    ```
  - Description: Sets the occupation law of the country.
  - Notes:
    ```text
    Identical to
    set_occupation_law
    , except if the law is impossible to set, tries again at every smaller sub-set: if default is impossible, tries every single individual occupied country; if the country's law is impossible to change, tries every single state within the country.
    ```
  - Version Added: 1.12

- **send_embargo**
  - Parameters:
    ```text
    <tag>
    The target country.
    ```
  - Example:
    ```text
    send_embargo = ITA
    ```
  - Description: Embargos the target country.
  - Version Added: 1.12

- **break_embargo**
  - Parameters:
    ```text
    <tag>
    The target country.
    ```
  - Example:
    ```text
    break_embargo = ITA
    ```
  - Description: Stops embargoing the target country.
  - Notes:
    ```text
    As of 1.14.7, this effect ignores country scoping and always applies to the ROOT, instead the
    diplomatic_relation
    effect can be used to break the embargoes of other countries.
    ```
  - Version Added: 1.12

- **give_market_access**
  - Parameters:
    ```text
    <tag>
    The target country.
    ```
  - Example:
    ```text
    give_market_access = ITA
    ```
  - Description: Opens market access between the two countries.
  - Version Added: 1.13

### Faction

- **create_faction**
  - Parameters:
    ```text
    <loc_key>
    The name of the faction.
    ```
  - Example:
    ```text
    create_faction = MY_FACTION_NAME
    ```
  - Description: Creates a faction with the specified name for the current scope. The current scope and any subjects automatically join the faction.
  - Notes:
    ```text
    OBSOLETE, use
    create_faction_from_template
    .
    ```
  - Version Added: 1.0

- **create_faction_from_template**
  - Parameters:
    ```text
    <string>
    Faction template id.
    OR
    template = <string>
    The tamplate of the faction.
    name = <loc_key>
    The name of the faction.
    icon = <sprite>
    The icon of the faction.
    color = <int>
    The color of the faction in RGB format.
    ```
  - Example:
    ```text
    create_faction_from_template = faction_template_GER_mitteleuropa_alliance
    ```
  - Example:
    ```text
    create_faction_from_template = {
       template = faction_template_defensive_democratic
       name = AUS_alpine_federation
       icon = GFX_faction_logo_generic_2
       color = { 100 100 150 }
    }
    ```
  - Description: Create a faction from a template allows for optional customization of name, icon and color.
  - Version Added: 1.17

- **add_to_faction**
  - Parameters:
    ```text
    <TAG>
    The TAG of the nation to add to the faction of the current scope.
    ```
  - Example:
    ```text
    add_to_faction = GER
    ```
  - Description: Adds the country to the faction of the current scope.
  - Version Added: 1.0

- **dismantle_faction**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    dismantle_faction = yes
    ```
  - Description: Dismantles the faction of the current scope.
  - Version Added: 1.0

- **leave_faction**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    leave_faction = yes
    ```
  - Description: Removes the current scope from the faction they are part of.
  - Version Added: 1.5

- **remove_from_faction**
  - Parameters:
    ```text
    <scope>
    The target country.
    ```
  - Example:
    ```text
    remove_from_faction = GER
    ```
  - Description: Removes the specified scope from the faction led by the current scope.
  - Version Added: 1.0

- **set_faction_name**
  - Parameters: Sets a faction name as the loc name.
  - Example:
    ```text
    set_faction_name = SOME_LOC_KEY
    ```
  - Description: Changes faction names.
  - Version Added: 1.6

- **set_faction_leader**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    set_faction_leader = yes
    ```
  - Description: Sets the current country as the faction leader.
  - Version Added: 1.0

- **set_faction_spymaster**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    set_faction_spymaster = yes
    ```
  - Description: Sets the current country as the faction spymaster.
  - Version Added: 1.9

- **set_faction_rule**
  - Parameters:
    ```text
    <string>
    Faction rule id.
    ```
  - Example:
    ```text
    set_faction_rule = rule_id
    ```
  - Description: Set a rule on the country's faction.
  - Version Added: 1.17

- **set_faction_manifest**
  - Parameters:
    ```text
    <string>
    Faction manifest id.
    ```
  - Example:
    ```text
    set_faction_manifest = faction_manifest_id
    ```
  - Description: Changes current country's faction manifest, the previous manifest is removed.
  - Version Added: 1.17

- **add_faction_goal**
  - Parameters:
    ```text
    <string>
    The goal of the faction.
    ```
  - Example:
    ```text
    add_faction_goal = faction_goal_an_armored_fist
    ```
  - Description: Adds a goal to the current’s country faction.
  - Version Added: 1.17

- **remove_faction_goal**
  - Parameters:
    ```text
    <string>
    The goal of the faction.
    ```
  - Example:
    ```text
    remove_faction_goal = faction_goal_secure_the_oil_supply
    ```
  - Description: Remove a goal from the current’s country faction.
  - Version Added: 1.17

- **add_faction_goal_slot**
  - Parameters:
    ```text
    category = <string>
    The category of the faction goal.
    value = <int> / <variable>
    A value of the faction goal slot.
    ```
  - Example:
    ```text
    add_faction_goal_slot = {
        category  = short_term
        value = 1 
    }
    ```
  - Description: Adds extra goal slots to the faction for a specific category.
  - Version Added: 1.17

- **add_faction_influence_ratio**
  - Parameters:
    ```text
    <float> / <variable>
    The amount to add.
    ```
  - Example:
    ```text
    add_faction_influence_ratio = 0.075
    ```
  - Description: Adds influence to the country based on the given ratio of the faction’s total influence.
  - Version Added: 1.17

- **add_faction_influence_score**
  - Parameters:
    ```text
    <int> / <variable>
    The amount to add.
    ```
  - Example:
    ```text
    add_faction_influence_score = 5
    ```
  - Description: Adds influence to the country in the faction.
  - Version Added: 1.17

- **add_faction_initiative**
  - Parameters:
    ```text
    <int> / <variable>
    The amount to add.
    ```
  - Example:
    ```text
    add_faction_initiative = 1
    ```
  - Description: Adds Faction Initiative points to the current country’s faction.
  - Version Added: 1.17

- **add_faction_power_projection**
  - Parameters:
    ```text
    <int> / <variable>
    The amount to add.
    ```
  - Example:
    ```text
    add_faction_power_projection = 100
    ```
  - Description: Adds power projection to the faction.
  - Version Added: 1.17

- **set_faction_upgrade**
  - Parameters:
    ```text
    <string>
    Faction upgrade id.
    ```
  - Example:
    ```text
    set_faction_upgrade = token
    ```
  - Description: Set either a member upgrade for the specified tag.
  - Version Added: 1.17

- **set_faction_member_upgrade_min**
  - Parameters:
    ```text
    upgrade = <string>
    Faction upgrade id.
    ```
  - Example:
    ```text
    set_faction_member_upgrade_min = {
        upgrade = TOKEN_TO_FACTION_MEMBER_UPGRADE
    }
    ```
  - Description: Set a faction's minimal requirements for an faction member upgrade group.
  - Version Added: 1.17

- **set_faction_military_unlocked**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    set_faction_military_unlocked = yes
    ```
  - Description: Sets wheter the current countries faction can make changes to the faction research section.
  - Version Added: 1.17

- **set_faction_research_unlocked**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    set_faction_research_unlocked = yes
    ```
  - Description: Sets wheter the current countries faction can make changes to the faction research section.
  - Version Added: 1.17

### Autonomy

- **puppet**
  - Parameters:
    ```text
    <country>
    The target country.
    OR
    target = <country>
    The target country.
    end_wars = <bool>
    Whether the target country will peace out in all of its non-civil wars it's participating in. Defaults to true.
    end_civil_wars = <bool>
    Whether the target country will peace out in all of its civil wars it's participating in. Defaults to true.
    ```
  - Example:
    ```text
    puppet = GER
    ```
  - Example:
    ```text
    puppet = {
        target = ITA
        end_wars = no
    }
    ```
  - Description: Makes the specified country a subject of the current scope.
  - Notes:
    ```text
    The autonomous state picked is one which contains
    default = yes
    and where
    allowed = { ... }
    is fulfilled within the
    /Hearts of Iron IV/commmon/autonomous_states/
    definition, rather than necessarily being autonomy_puppet.
    Results in a crash-to-desktop if the game is unable to find any such autonomous states.
    ```
  - Version Added: 1.0

- **end_puppet**
  - Parameters:
    ```text
    <country>
    The target country.
    ```
  - Example:
    ```text
    end_puppet = GER
    ```
  - Description: Removes the subject status between the target and the current scope.
  - Notes: Must be used within the overlord's scope.
  - Version Added: 1.0

- **add_autonomy_ratio**
  - Parameters:
    ```text
    value = <float>
    The freedom score to add.
    localization = <string>
    The localization key for the modifier.
    ```
  - Example:
    ```text
    add_autonomy_ratio = {
        value = 0.1
        localization = AST_adopt_westminster
    }
    ```
  - Description: Adds a freedom score ratio modifier to the current scope.
  - Notes: Used in the subject's scope.
  - Version Added: 1.3

- **add_autonomy_score**
  - Parameters:
    ```text
    value = <float>
    The freedom score to add.
    localization = <string>
    The localization key for the modifier.
    ```
  - Example:
    ```text
    add_autonomy_score = {
        value = 10
        localization = EXAMPLE
    }
    ```
  - Description: Adds an exact freedom score modifier to the current scope.
  - Notes: Used in the subject's scope.
  - Version Added: 1.3

- **set_autonomy**
  - Parameters:
    ```text
    target = <country> / <variable>
    The subject country.
    autonomous_state = <type>
    The type of autonomy state to set.
    freedom_level = <float>
    The new freedom level value. Optional.
    end_wars = <yes/no>
    Will end any wars the subject is involved in.
    end_civil_wars = <yes/no>
    Will end any civil wars the subject is subject to
    ```
  - Example:
    ```text
    set_autonomy = {
        target = AST
        autonomous_state = autonomy_free
        end_wars = no
        end_civil_wars = no
    }
    ```
  - Description:
    ```text
    Sets the autonomy level for the specified country,
    including independence
    .
    ```
  - Notes:
    ```text
    The autonomy_free state will free the subject,
    however this effect has to be executed within the scope of the target country's current overlord
    for this to have effect. The autonomy states are found in
    /Hearts of Iron IV/common/autonomous_states/*.txt
    files. Although end_wars is an optional argument defaulting to no, omitting it results in the country's occupied states returning to its control, stranding enemy units.
    ```
  - Version Added: 1.3

### Governments in exile

- **add_legitimacy**
  - Parameters: Adds legitimacy to a government in exile.
  - Example:
    ```text
    add_legitimacy = 10
    ```
  - Description: Adds legitimacy.
  - Version Added: 1.6

- **set_legitimacy**
  - Parameters: Sets the legitimacy of governments in exile.
  - Example:
    ```text
    set_legitimacy = 10
    ```
  - Description: Sets legitimacy.
  - Version Added: 1.6

- **become_exiled_in**
  - Parameters: Makes a country a government in exile in a set country, with a set starting legitimacy.
  - Example:
    ```text
    become_exiled_in = { target = <Host tag> legitimacy = <0-100> (starting legitimacy, optional) }
    ```
  - Description: Creates a government in exile.
  - Notes: Must be fired from ROOT, the country that should be exiled, or a TAG specification must be used.
  - Version Added: 1.6

- **end_exile**
  - Parameters: Ends a government in exile.
  - Example:
    ```text
    end_exile = yes
    ```
  - Description: Ends a government in exile.
  - Version Added: 1.6

### War

- **add_threat**
  - Parameters:
    ```text
    <int>
    The amount to change by.
    ```
  - Example:
    ```text
    add_threat = 10
    ```
  - Description: Adjusts the level of World Tension.
  - Version Added: 1.0

- **add_named_threat**
  - Parameters:
    ```text
    threat = <int>
    The amount to change by.
    name = <string>
    The localization string.
    ```
  - Example:
    ```text
    add_named_threat = {
        threat = 5
        name = GER_rhineland
    }
    ```
  - Description: Adjusts the level of World Tension and adds an entry in the World Tension tooltip.
  - Version Added: 1.0

- **annex_country**
  - Parameters:
    ```text
    target = <country>
    Which country to annex.
    transfer_troops = yes
    Whether to transfer the troops of the annexed country.
    ```
  - Example:
    ```text
    annex_country = {
        target = GER
        transfer_troops = yes
    }
    ```
  - Description: Annex the specified country for the current scope.
  - Notes: Without transfering troops, the annexed country's divisions' equipment is lost.
  - Version Added: 1.0

- **add_to_war**
  - Parameters:
    ```text
    targeted_alliance = <country>
    The country to assist.
    enemy = <country>
    The country attacking the ally.
    hostility_reason = <string>
    Localization for the reason for joining. Optional.
    ```
  - Example:
    ```text
    add_to_war = {
        targeted_alliance = PREV
        enemy = HUN
        hostility_reason = asked_to_join
    }
    ```
  - Description: Forces the current scope to join the war of the specified ally against the specified enemy.
  - Version Added: 1.0

- **declare_war_on**
  - Parameters:
    ```text
    target = <country> / <variable>
    The country to attack.
    type = <wargoal>
    The wargoal to declare with.
    generator = { <state id> }
    The states to supply the wargoal (i.e. take_state_focus).
    ```
  - Example:
    ```text
    declare_war_on = {
        target = GER
        type = annex_everything
    }
    ```
  - Description: Makes the current scope declare war on the specified country with the specified wargoal.
  - Notes:
    ```text
    Wargoals are found in
    /Hearts of Iron IV/common/wargoals/*.txt
    . See also
    add_civil_war_target
    in order to assign a war between different countries to be a civil war.
    ```
  - Version Added: 1.0

- **white_peace**
  - Parameters:
    ```text
    <country> / <variable>
    The scope to white peace.
    OR
    tag = <country> / <variable>
    The scope to white peace.
    message = <localisation key>
    The reason for peace showing up in the pop-up.
    ```
  - Example:
    ```text
    white_peace = GER
    ```
  - Example:
    ```text
    white_peace = {
        tag = GER
        message = my_peace_tt
    }
    ```
  - Description: Makes the current scope white peace the specified scope.
  - Version Added: 1.0

- **start_peace_conference**
  - Parameters:
    ```text
    tag = <country> / <variable>
    The scope to peace with.
    score_factor = <decimal> / <variable>
    The fraction of the total score awarded to the winners compared to regular victory.
    message = <localisation key>
    The reason for peace showing up in the pop-up. Optional.
    winner_scope = <scope type>
    Which countries should be present in the conference on the winner side alongside the current scope. Optional, defaults to LIMITED_FACTION.
    loser_scope = <scope type>
    Which countries should be present in the conference on the loser side alongside the target country. Optional, defaults to LIMITED_FACTION.
    ```
  - Example:
    ```text
    start_peace_conference = {
        tag = GER
        score_factor = 0.4
        message = my_peace_tt
    }
    ```
  - Description: Makes the current scope start a peace conference with the specified scope on the other side.
  - Notes:
    ```text
    Current scope is the winner, target and its subjects are the losers. Can only be used if at war with the target. A score_factor of 0.0 is equivalent to a whitepeace.
    winner_scope
    and
    loser_scope
    have the following possible values:
    ALL
    : all countries at war with the other side.
    FACTION
    : all countries in the same faction as the current scope or under its overlordship.
    LIMITED_FACTION
    : includes faction members if and only if the country is a faction leader, and includes subjects of the country.
    LIMITED
    : includes only subjects of the country.
    ```
  - Version Added: 1.12

- **set_truce**
  - Parameters:
    ```text
    target = <country>
    The scope to truce with.
    days = <int>
    The duration of the truce.
    ```
  - Example:
    ```text
    set_truce = {
        target = GER
        days = 90
    }
    ```
  - Description: Makes the current scope truce with the specified scope.
  - Version Added: 1.0

- **create_wargoal**
  - Parameters:
    ```text
    target = <country> / <variable>
    The country to target.
    type = <wargoal>
    The wargoal to generate.
    generator = { <state id> }
    The states to supply the wargoal (i.e. take_state_focus).
    expire = 365
    The amount of days that the wargoal will last before expiring. If unset or set to 0, will never expire.
    ```
  - Example:
    ```text
    create_wargoal = {
        type = puppet_wargoal_focus
        target = ROOT
    }
    ```
  - Example:
    ```text
    create_wargoal = {
        type = take_state_focus
        target = PREV
        generator = { 123 321 }
        expire = 90
    }
    ```
  - Description: Grants the current scope a wargoal against the specified country.
  - Notes:
    ```text
    Wargoal type can be found in
    /Hearts of Iron IV/common/wargoals/*.txt
    ```
  - Version Added: 1.0

- **remove_wargoal**
  - Parameters:
    ```text
    target = <country> / <variable>
    The country to target.
    type = <wargoal>
    The wargoal to remove. "all" will remove all wargoals.
    ```
  - Example:
    ```text
    remove_wargoal = {
        type = all
        target = ROOT
    }
    ```
  - Description: Removes wargoals from the current scope to the specified country.
  - Notes:
    ```text
    Wargoal type can be found in
    /Hearts of Iron IV/common/wargoals/*.txt
    ```
  - Version Added: 1.10.2

- **start_civil_war**
  - Parameters:
    ```text
    ideology = <ideology>
    The ideology of the breakaway country.
    ruling_party = <ideology>
    Changes the ideology of the
    original, player-led
    country, if set. Optional.
    size = <float>
    The size of the breakaway country and the fraction of the original stockpile and military units it will receive by default. Optional, defaults to 0.5.
    army_ratio = <float>
    The size of the land army that the breakaway country gets. Optional, defaults to being the same as size.
    navy_ratio = <float>
    The size of the naval forces that the breakaway country gets. Optional, defaults to being the same as size.
    air_ratio = <float>
    The size of the airforce that the breakaway country gets. Optional, defaults to being the same as size.
    capital = <state>
    The capital state of the breakaway country. Optional.
    states = { <state> }
    The states included in the breakway country. Optional, defaults to random states based off size.
    all
    will result in all states that meet the filter going to the breakaway.
    states_filter = { <triggers> }
    A trigger block checked for the state that must be met to be transferred to the breakaway. Optional.
    keep_unit_leaders = { <unit leader id> }
    List of unit leaders to be kept by their legacy_id. Optional.
    keep_unit_leaders_trigger = { <triggers> }
    Trigger block checked for every unit leader that forces them to be kept if they meet the triggers. The default scope is the unit leader, ROOT is the country receiving the unit leader, while FROM is the original owner of the unit leader. Optional.
    keep_scientists_trigger = { <triggers> }
    Trigger for scientist to remain with the original country.
    keep_political_leader = <bool>
    Controls if the promoted party leader (i.e. the one that'd take power if the country were to be switched to that ideology group) of the revolting ideology group will be kept by the country or join the revolt, yes resulting in the former. Optional, defaults to false.
    keep_political_party_members = <bool>
    Controls if non-promoted party leaders of the revolting ideology group will be kept by the country or join the revolt, yes resulting in the former. Optional, defaults to false.
    keep_all_characters = yes
    If true, the revolter will have no characters from the original country transferred to them. Optional, defaults to false.
    <effects>
    An effect block executed for the breakaway country.
    ```
  - Examples:
    ```text
    (
    See country tag aliases
    )
    (
    See usage for PREV and PREV.PREV
    )
    ```
  - Example:
    ```text
    start_civil_war = {
        ruling_party = communism
        # Original country's ideology changes to communism
        ideology = ROOT
        # Breakaway gets old ideology of ROOT
        size = 0.8
        capital = 282
        states = {
            282 533 536 555 529 530 528
        }
        keep_unit_leaders = {
            750 751 752
        }
        keep_political_leader = yes
        keep_political_party_members = yes
    }
    ```
  - Example:
    ```text
    start_civil_war = {
        ideology = democratic
        size = 0.1
        states = all
        states_filter = {
            is_on_continent = europe
            is_capital = no
        }
        set_country_flag = TAG_my_country_tag_alias_trigger
        # Sets a country flag that gets used in a country tag alias.
    }
    ```
  - Example:
    ```text
    start_civil_war = {
        ideology = neutrality
        size = 0.1
        army_ratio = 0.5
        navy_ratio = 0
        air_ratio = 1
        keep_unit_leaders_trigger = {
            has_trait = my_trait_name
        }
        keep_all_characters = yes
        PREV = {  # Original country
            TAG_airforce_leader = { # Character
                set_nationality = PREV.PREV
                # Transfers to breakaway
            }
        }
        promote_character = TAG_airforce_leader
    }
    ```
  - Description: Starts a civil war for the current scope with the specified parameters.
  - Notes:
    ```text
    states = all
    would include every single state controlled by the country.
    If the country's current capital state is set as one of the states that the revolt can gain, it won't fire
    .
    set_capital
    can be used to change the capital beforehand, with
    on_civil_war_end
    being used to set it back to the default after the civil war ends.
    Elections will always be disallowed for the breakaway. If the
    ruling_party
    attribute is used, the original country will have its elections disallowed. In the base game files, an
    on action
    is set up to ensure that elections get allowed if the democratic side wins the civil war.
    A civil war started via this effect cannot have more than two sides and the effect cannot be used in
    history
    or
    bookmark's effect = { ... }
    . For adding more sides or starting one before the game's start, this can be simulated by setting an existing war (typically originating from a dynamic country created via
    create_dynamic_country
    ) as a civil war via
    add_civil_war_target
    .
    ```
  - Version Added: 1.0

- **add_civil_war_target**
  - Parameters:
    ```text
    <country>
    - The country to set as the target.
    ```
  - Example:
    ```text
    add_civil_war_target = TAG
    ```
  - Description: Sets that the war between ROOT and TAG is a civil war, resulting in the victory being the annexation of the other side and setting world tension limits on intervention.
  - Notes: ROOT and TAG must already be at war with each other for the effect to take place.
  - Version Added: 1.9

- **remove_civil_war_target**
  - Parameters:
    ```text
    <country>
    - The country to set as the target.
    ```
  - Example:
    ```text
    remove_civil_war_target = TAG
    ```
  - Description: Removes the status of the war as a civil war between the pair of countries.
  - Notes:
    ```text
    The ongoing war must already be marked as a civil war, whether it was initiated by
    start_civil_war
    or
    add_civil_war_target
    was used to mark it as one.
    ```
  - Version Added: 1.12.13

- **transfer_units_fraction**
  - Parameters:
    ```text
    target = <country>
    The country which should receive the units from the current scope.
    size = <float>
    The size of the breakaway country and the fraction of the original stockpile and military units it will receive by default. Optional, defaults to 0.5.
    army_ratio = <float>
    The size of the land army that the breakaway country gets. Optional, defaults to being the same as size.
    navy_ratio = <float>
    The size of the naval forces that the breakaway country gets. Optional, defaults to being the same as size.
    air_ratio = <float>
    The size of the airforce that the breakaway country gets. Optional, defaults to being the same as size.
    keep_unit_leaders = { <unit leader id> }
    List of unit leaders to be kept by their legacy_id. Optional.
    keep_unit_leaders_trigger = { <triggers> }
    Trigger block checked for every unit leader that forces them to be kept if they meet the triggers. The default scope is the unit leader, ROOT is the country receiving the unit leader, while FROM is the original owner of the unit leader. Optional.
    ```
  - Example:
    ```text
    transfer_units_fraction= {
    	target = SPD
    	size = 0.5
    	stockpile_ratio = 0.8
    	army_ratio = 0.8
    	navy_ratio = 0.5
    	air_ratio = 0.5
    	keep_unit_leaders_trigger = {
    		has_trait = trait_SPA_nationalist_sympathies
    	}
    }
    ```
  - Description: Transfers a fraction of the military to a target, including units (either type: land, navy, or air), equipment, and unit leaders.
  - Version Added: 1.9

- **add_nuclear_bombs**
  - Parameters: Adds nuclear bomb to TAG's stockpile.
  - Example:
    ```text
    add_nuclear_bombs = 100
    ```
  - Description: Adds specified number of nukes to the country's stockpile
  - Notes: Needs the Nuke tech to use.
  - Version Added: 1.6

- **launch_nuke**
  - Parameters:
    ```text
    province = <ID>
    The specific province to nuke.
    state = <ID>
    The state to nuke.
    controller = <TAG>
    Prioritises provinces controlled by this country.
    use_nuke = <boolean>
    Whether a nuke should be deducted from the country's stockpile. Defaults to false.
    nuke_type = <nuke_type>
    type of nuke to use (e.g. nuclear_bomb, thermonuclear_bomb etc.)
    ```
  - Example:
    ```text
    launch_nuke = {
        province = 1234
    }
    ```
  - Example:
    ```text
    launch_nuke = {
        state = 42
        controller = GER
        use_nuke = yes
        nuke_type = nuclear_bomb 
    }
    ```
  - Description:
    ```text
    Nukes the specified province or a province in the needed state. If a state is set rather than the specific province, first prioritises the country set in
    controller
    , then prioritises the countries at war with the current scope, and then countries that are neutral.
    ```
  - Notes: If set to use a nuke, then requires at least one nuclear bomb in the stockpile.
  - Version Added: 1.6

### Resources

- **add_resource**
  - Parameters:
    ```text
    type = <resource>
    The resource to add.
    amount = <int>
    The amount of resource to add.
    state = <id>
    Which state to add the resource to. Variables can be used.
    show_state_in_tooltip = <bool>
    Whether the state should be shown in the tooltip. Defaults to true.
    ```
  - Example:
    ```text
    add_resource = {
        type = oil
        amount = 50
        state = 88
    }
    ```
  - Description: Adds the specified resource in the specified amount to the specified state.
  - Notes: Can also be used in state scope.
  - Version Added: 1.0

- **create_import**
  - Parameters:
    ```text
    resource = <resource>
    The resource to import.
    amount = <int>
    The amount of resource to import.
    exporter = <id>
    Which country exports the resource.
    ```
  - Example:
    ```text
    create_import = {
        resource = steel
        amount = 100
        exporter = GER
    }
    ```
  - Description: Creates an import for the current scope with the specified resource and from the specified exporter.
  - Version Added: 1.0

- **give_resource_rights**
  - Parameters:
    ```text
    receiver = <tag>
    The country that would get the resource rights.
    state = <state>
    The state where the resource rights are located.
    resources = { <resource> <...> <resource> }
    The resources to which give resource rights to. Optional, defaults to all.
    ```
  - Example:
    ```text
    give_resource_rights = { receiver = ENG state = 291 }
    ```
  - Example:
    ```text
    give_resource_rights = {
        receiver = POL
        state = 321
        resources = { oil }
    }
    ```
  - Description: Gives all the resources of a state to the target country
  - Notes: The resource rights will only be provided as long as the current country controls the state with resource rights.
  - Version Added: 1.6

- **remove_resource_rights**
  - Parameters:
    ```text
    <state>
    The state to remove current country's resource rights from.
    ```
  - Example:
    ```text
    ENG = { remove_resource_rights = 477 }
    ```
  - Description: Removes given resource rights
  - Version Added: 1.6

- **add_fuel**
  - Parameters:
    ```text
    <int>
    The fuel amount
    ```
  - Example:
    ```text
    add_fuel = 400
    ```
  - Description: Adds fuel to the current country.
  - Version Added: 1.6

- **set_fuel**
  - Parameters:
    ```text
    <int>
    Fuel amount.
    ```
  - Example:
    ```text
    set_fuel = 400
    ```
  - Description: Sets country's current fuel amount.
  - Version Added: 1.6

- **set_fuel_ratio**
  - Parameters:
    ```text
    <decimal>
    The needed ratio of fuel.
    ```
  - Example:
    ```text
    set_fuel_ratio = 0.5
    ```
  - Description: Set country's current fuel ratio relative to its capacity.
  - Version Added: 1.6

### Buildings

- **add_offsite_building**
  - Parameters:
    ```text
    type = <building>
    The building to add.
    level = <level> / <variable>
    The maximum level to add.
    ```
  - Example:
    ```text
    add_offsite_building = { type = arms_factory level = 1 }
    ```
  - Description: Adds an off-map (offmap) building for the current scope that produces its effects without being present in a state.
  - Version Added: 1.5

- **modify_building_resources**
  - Parameters:
    ```text
    building = <building>
    The building to modify.
    resource = <resource>
    The resource to add.
    amount = <amount>
    The amount of resource to add.
    ```
  - Example:
    ```text
    modify_building_resources = {
        building = synthetic_refinery
        resource = oil
        amount = 1
    }
    ```
  - Description: Modifies the resource output of the specified building for the current scope.
  - Version Added: 1.5

- **damage_building**
  - Parameters:
    ```text
    type = <building>
    The building to damage.
    state = <id> / <variable>
    The state to target.
    tags = <building_tag>
    The buildings with this tag to damage.
    tags = { <building_tag> }
    The buildings with these tags to damage.
    repair_speed_modifier = <float>
    Repair will be x% slower until building is fully repaired
    damage = <float>
    The amount of damage to inflict.
    province = <id> / <variable>
    The province to target for provincal buildings.
    ```
  - Example:
    ```text
    damage_building = {
      type = infrastructure
      state = 123
      damage = 1
    }
    ```
  - Example:
    ```text
    damage_building = {
      tags = dam_building
      damage = 1
      repair_speed_modifier = -0.8
      province = 3488
    }
    ```
  - Description: Damages a building in a targeted state or province.
  - Notes:
    ```text
    The health of buildings is determined by the
    value
    attribute in a building's definition. This is multiplied by their level to get their total health.
    Can also be used in state scope.
    ```
  - Version Added: 1.3

### National focuses

- **load_focus_tree**
  - Parameters:
    ```text
    <focus tree>
    The national focus tree to load.
    OR
    tree = <focus tree ID>
    The national focus tree to load.
    keep_completed = <bool>
    Whether focuses shared between the old and new trees should stay completed. Defaults to false.
    copy_completed_from = <tag>
    Copy completed focus from an existing country.
    ```
  - Example:
    ```text
    load_focus_tree = china_communist_focus
    ```
  - Example:
    ```text
    load_focus_tree = {
      tree = british_focus
      keep_completed = yes
      copy_completed_from = ENG
    }
    ```
  - Description: Loads a new focus tree for the current scope, retaining any shared focuses if set.
  - Notes:
    ```text
    Focuses that aren't present in the newly-loaded tree will not be kept as completed for
    has_completed_focus
    checks or when loading the old tree back.
    ```
  - Version Added: 1.5

- **unlock_national_focus**
  - Parameters:
    ```text
    <focus>
    The focus to unlock.
    ```
  - Example:
    ```text
    unlock_national_focus = my_focus
    ```
  - Description:
    ```text
    Bypasses the specified focus for the current scope (marks as complete without firing
    complete_effect
    of the focus).
    ```
  - Version Added: 1.0

- **complete_national_focus**
  - Parameters:
    ```text
    <focus>
    The focus to complete.
    OR
    focus = <focus>
    The focus to complete.
    use_side_message = <bool>
    Create popup notification in the bottom right that includes
    originator_name
    instead of normal focus popup.
    originator_name = <string>
    Used for tooltip only.
    ```
  - Example:
    ```text
    complete_national_focus = my_focus
    ```
  - Example:
    ```text
    complete_national_focus = {
      focus = GER_autonomous_organization_todt
      use_side_message = yes
      originator_name = GER_fritz_todt
    }
    ```
  - Description: Completes the specified focus for the current scope.
  - Notes: In 1.15 block version was added, 'originator_name' can be TAG, character, state, or any other localization key.
  - Version Added: 1.0

- **uncomplete_national_focus**
  - Parameters:
    ```text
    focus = <focus>
    uncomplete_children = <bool>
    Defaults "no". Optional.
    refund_political_power = <bool>
    Defaults "no". Optional.
    ```
  - Example:
    ```text
    uncomplete_national_focus = {
      focus = GER_oppose_hitler
      uncomplete_children = yes
      refund_political_power = no
    }
    ```
  - Description:
    ```text
    Removes a focus from list of completed focus, and potentially all focuses requiring it as a prerequisite.
    If the focus has one, the 'on_uncomplete' effect will be executed on each uncompleted focus.
    ```
  - Version Added: 1.11

- **mark_focus_tree_layout_dirty**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    mark_focus_tree_layout_dirty = yes
    ```
  - Description:
    ```text
    Refreshes the focus tree for the specified country, restarting the checks in
    allow_branch
    and position offsets for focuses.
    ```
  - Notes:
    ```text
    If put within a focus' completion reward, the focus will not be marked as complete at the time the effect is executed, leading to
    has_completed_focus
    checks specifying that focus in particular to be marked as false.
    This can be bypassed by putting an effect within a hidden event fired immediately within the focus or by reloading the same focus tree with
    load_focus_tree
    set to keep completed focuses, marking the focus as complete, before using the effect.
    ```
  - Version Added: 1.9

- **activate_shine_on_focus**
  - Parameters:
    ```text
    <focus>
    The focus to activate a shine effect on.
    ```
  - Examples: activate_shine_on_focus = my_focus
  - Description: Activates the shine effect on the focus with the given id. Focuses that are completed cannot have an activated shine effect.
  - Notes:
    ```text
    Tooltips are only shown in debug mode.
    Can be used to simulate work on more than one focus at a time.
    ```
  - Version Added: 1.15

- **deactivate_shine_on_focus**
  - Parameters:
    ```text
    <focus>
    The focus to deactivate a shine effect on.
    ```
  - Examples: deactivate_shine_on_focus = my_focus
  - Description: Deactivate the shine effect on the focus with the given id. The current focus cannot have it's shine effect removed.
  - Notes: Tooltips are only shown in debug mode.
  - Version Added: 1.15

- **reduce_focus_completion_cost**
  - Parameters:
    ```text
    focus = <focus>
    The focus to reduce cost time.
    cost = <int> / <variable>
    Time to reduce (in days).
    ```
  - Example:
    ```text
    reduce_focus_completion_cost = {
      focus = focus_id
      cost = 35
    }
    ```
  - Example:
    ```text
    reduce_focus_completion_cost = {
      focus = {focus_id_1 focus_id_2}
      cost = 35
    }
    ```
  - Description: Reduce the cost needed to complete a specific focus. The cost accepts script constants. The focus can be a uniform list or a single token.
  - Version Added: 1.17

### Decisions

- **activate_decision**
  - Parameters:
    ```text
    <decision>
    The decision to activate.
    ```
  - Example:
    ```text
    activate_decision = my_decision
    ```
  - Description: Activates the specified decision for the current scope, ignoring triggers for the decision.
  - Notes:
    ```text
    Decisions are found in
    /Hearts of Iron IV/common/decisions/*.txt
    ```
  - Version Added: 1.0

- **activate_targeted_decision**
  - Parameters:
    ```text
    target = <country>
    The country to target.
    decision = <decision>
    The decision to activate.
    ```
  - Example:
    ```text
    activate_targeted_decision = {
        target = GER
        decision = my_decision
    }
    ```
  - Description: Activates the specified targeted decision for the specified target for the current scope.
  - Notes:
    ```text
    Decisions are found in
    /Hearts of Iron IV/common/decisions/*.txt
    Only works on missions; regular decisions targeted this way become visible but do not activate.
    ```
  - Version Added: 1.5

- **remove_targeted_decision**
  - Parameters:
    ```text
    <decision>
    The decision to remove.
    ```
  - Example:
    ```text
    remove_targeted_decision = {
        target = FROM
        decision = my_decision
    }
    ```
  - Description: Removes the specified targeted decision for the current scope.
  - Notes:
    ```text
    Decisions are found in
    /Hearts of Iron IV/common/decisions/*.txt
    ```
  - Version Added: 1.5

- **unlock_decision_tooltip**
  - Parameters:
    ```text
    <decision>
    The decision to display.
    <show_effect_tooltip>
    Show decision effects (default is no)
    <show_modifiers>
    Show decision modifiers. (default is no)
    ```
  - Example:
    ```text
    unlock_decision_tooltip = my_decision
    ```
  - Example:
    ```text
    unlock_decision_tooltip = {
        decision = my_decision
        show_effect_tooltip = yes
        show_modifiers = yes
    }
    ```
  - Description: Displays a special tooltip for the specified decision in the effect tooltip.
  - Notes:
    ```text
    Decisions are found in
    /Hearts of Iron IV/common/decisions/*.txt
    ```
  - Version Added: 1.5

- **unlock_decision_category_tooltip**
  - Parameters:
    ```text
    <category>
    The decision category to display.
    ```
  - Example:
    ```text
    unlock_decision_category_tooltip = my_category
    ```
  - Description: Displays a special tooltip for the specified decision category in the effect tooltip.
  - Notes:
    ```text
    Decision categories are found in
    /Hearts of Iron IV/common/decisions/catergories/*.txt
    ```
  - Version Added: 1.5

- **add_days_remove**
  - Parameters:
    ```text
    decision = <decision>
    The decision to add days to.
    days = <int> / <variable>
    The number of days to add to the decision.
    ```
  - Example:
    ```text
    add_days_remove  = {
        decision = decision_here
        days = 30
    }
    ```
  - Description: Adds the number of days to the timer created by a decision's days_remove.
  - Notes:
    ```text
    Decisions are found in
    /Hearts of Iron IV/common/decisions/*.txt
    ```
  - Version Added: 1.9

- **remove_decision**
  - Parameters: Allows to remove specified decision without running remove_effect.
  - Example:
    ```text
    remove_decision = GER_MEPO
    ```
  - Description: Removes a decision.
  - Version Added: 1.6

- **remove_decision_on_cooldown**
  - Parameters:
    ```text
    <decision>
    The decision that is to be removed.
    ```
  - Example:
    ```text
    remove_decision_on_cooldown = TAG_my_decision
    ```
  - Description: If the decision is on cooldown, it gets removed, in order to reactivate or remove completely.
  - Version Added: 1.11

### Missions

- **activate_mission**
  - Parameters:
    ```text
    <mission>
    The mission to activate.
    ```
  - Example:
    ```text
    activate_mission = my_mission
    ```
  - Description: Activates the specified mission for the current scope, ignoring any triggers for the decision.
  - Notes:
    ```text
    Missions are found in
    /Hearts of Iron IV/common/decisions/*.txt
    ```
  - Version Added: 1.5

- **activate_mission_tooltip**
  - Parameters:
    ```text
    <mission>
    The mission to display.
    ```
  - Example:
    ```text
    activate_mission_tooltip = my_mission
    ```
  - Description: Displays a special tooltip for the specified mission in the effect tooltip.
  - Notes:
    ```text
    Missions are found in
    /Hearts of Iron IV/common/decisions/*.txt
    ```
  - Version Added: 1.5

- **remove_mission**
  - Parameters:
    ```text
    <mission>
    The mission to remove.
    ```
  - Example:
    ```text
    remove_mission = my_mission
    ```
  - Description: Removes the specified mission for the current scope.
  - Notes:
    ```text
    Missions are found in
    /Hearts of Iron IV/common/decisions/*.txt
    ```
  - Version Added: 1.5

- **add_days_mission_timeout**
  - Parameters:
    ```text
    mission = <mission>
    The mission to add days to.
    days = <int> / <variable>
    The number of days to add to the mission.
    ```
  - Example:
    ```text
    add_days_mission_timeout = {
        mission = my_mission
        days = 20
    }
    ```
  - Description: Adds the number of days to the specified mission.
  - Notes:
    ```text
    Missions are found in
    /Hearts of Iron IV/common/decisions/*.txt
    ```
  - Version Added: 1.9

### Technologies

- **add_research_slot**
  - Parameters:
    ```text
    <int>
    The number of slots to add or remove.
    ```
  - Example:
    ```text
    add_research_slot = 1
    ```
  - Description: Adjusts the number of research slots the current scope has. Can remove slots with negatives.
  - Version Added: 1.0

- **set_research_slots**
  - Parameters:
    ```text
    <int>
    The number of slots to set.
    ```
  - Example:
    ```text
    set_research_slots = 4
    ```
  - Description: Sets the number of research slots the current scope has.
  - Version Added: 1.0

- **add_tech_bonus**
  - Parameters:
    ```text
    bonus = <float>
    The bonus to technology given, default 0.
    uses = <int>
    The amount of times the bonus can be used, default 1.
    ahead_reduction = <float>
    The cost reduction if ahead of time, default 0.
    category = <string>
    Which technology category the bonus applies to. Multiple can be defined.
    technology = <string>
    Which technology the bonus applies to. Multiple can be defined.
    name = <string>
    Tooltip shown in research tabs, optional.
    ```
  - Example:
    ```text
    add_tech_bonus = {
        bonus = 0.5
        uses = 1
        category = radar_tech
    }
    ```
  - Description: Grants a research bonus to the current scope with the specified parameters.
  - Notes:
    ```text
    Research bonus categories are defined in
    /Hearts of Iron IV/common/technology_tags/*.txt
    files, while technologies are defined in
    /Hearts of Iron IV/common/technologies/*.txt
    files.
    ```
  - Version Added: 1.0

- **set_technology**
  - Parameters:
    ```text
    <technology> = <int>
    The technology to add.
    popup = no
    To not show the popup after adding technology
    ```
  - Example:
    ```text
    set_technology = {
        suicide_craft = 1
    }
    ```
  - Description: Grants the specified technology to the current scope.
  - Notes:
    ```text
    A value of 1 sets the technology. A value of 0 removes the technology, but if it is a researchable technology, the duration it takes to research isn't reset, meaning it can be researched in 1 day. Technologies that are mutually exclusive with other technologies can not be removed by this effect. Technologies are defined in
    /Hearts of Iron IV/common/technologies/*.txt
    files.
    ```
  - Version Added: 1.0

- **add_to_tech_sharing_group**
  - Parameters:
    ```text
    <string>
    The group to add the current scope to.
    ```
  - Example:
    ```text
    add_to_tech_sharing_group = us_research
    ```
  - Description: Adds the current scope to the specified technology sharing group.
  - Notes:
    ```text
    Technology sharing groups are found in
    Hearts of Iron IV\common\technology_sharing\*.txt
    ```
  - Version Added: 1.3

- **remove_from_tech_sharing_group**
  - Parameters:
    ```text
    <string>
    The group to remove the current scope from.
    ```
  - Example:
    ```text
    remove_from_tech_sharing_group = us_research
    ```
  - Description: Removes the current scope from the specified technology sharing group.
  - Notes:
    ```text
    Technology sharing groups are found in
    Hearts of Iron IV\common\technology_sharing\*.txt
    ```
  - Version Added: 1.3

- **modify_tech_sharing_bonus**
  - Parameters:
    ```text
    id = <string>
    The group to modify.
    bonus = <float>
    The new bonus.
    ```
  - Example:
    ```text
    modify_tech_sharing_bonus = {
        id = us_research
        bonus = 0.5
    }
    ```
  - Description: Modifies the specified technology sharing group.
  - Notes:
    ```text
    Technology sharing groups are found in
    Hearts of Iron IV\common\technology_sharing\*.txt
    ```
  - Version Added: 1.3

- **inherit_technology**
  - Parameters:
    ```text
    <tag>
    The country to inherit technology from.
    ```
  - Example:
    ```text
    inherit_technology = CAN
    ```
  - Description: Makes the current country's researched technologies be copied from the specified country.
  - Notes: Useful when making a country independent.
  - Version Added: 1.6

- **mark_technology_tree_layout_dirty**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    mark_technology_tree_layout_dirty = yes
    ```
  - Description: Forces the refresh of the hidden technologies for the scoped country.
  - Version Added: 1.15

### Ideas

This includes national spirits, laws, designers, and advisors. (using the idea\_token)

- **add_ideas**
  - Parameters:
    ```text
    <idea>
    The idea to add.
    ```
  - Example:
    ```text
    add_ideas = my_idea
    ```
  - Example:
    ```text
    add_ideas = {
        my_idea_1
        my_idea_2
    }
    ```
  - Description: Adds the specified ideas to the current scope.
  - Notes: Can be used as a scope to add multiple at once.
  - Version Added: 1.0

- **add_timed_idea**
  - Parameters:
    ```text
    idea = <idea>
    The idea to add.
    days = <int> / <variable>
    The number of days to add the idea for.
    months = <int> / <variable>
    The number of months to add the idea for. A month is equal to 30 days.
    years = <int> / <variable>
    The number of years to add the idea for. A year is equal to 365 days.
    ```
  - Example:
    ```text
    add_timed_idea = {
        idea = my_idea
        days = 180
    }
    ```
  - Description: Adds the specified ideas to the current scope for the specified number of days.
  - Notes:
    ```text
    Either one of
    days
    ,
    months
    , or
    years
    is mandatory. The tooltip will use the exact same phrasing in years/months/days as used in the attributes.
    ```
  - Version Added: 1.0

- **modify_timed_idea**
  - Parameters:
    ```text
    idea = <idea>
    The idea to modify.
    days = <int> / <variable>
    The number of days to modify the idea by.
    months = <int> / <variable>
    The number of months to modify the idea by. A month is equal to 30 days.
    years = <int> / <variable>
    The number of years to modify the idea by. A year is equal to 365 days.
    ```
  - Example:
    ```text
    modify_timed_idea = {
        idea = my_idea
        days = 60
    }
    ```
  - Description: Extends or shortens the duration of the timed idea by the specified amount.
  - Notes:
    ```text
    Positives add to the time, negatives shorten it. Either one of
    days
    ,
    months
    , or
    years
    is mandatory. The tooltip will use the exact same phrasing in years/months/days as used in the attributes.
    ```
  - Version Added: 1.0

- **swap_ideas**
  - Parameters:
    ```text
    add_idea = <idea>
    The idea to add.
    remove_idea = <idea>
    The idea to remove.
    ```
  - Example:
    ```text
    swap_ideas = {
        remove_idea = my_idea_1
        add_idea = my_idea_2
    }
    ```
  - Description: Switches two ideas with a tooltip displaying any modifier differences between them.
  - Notes:
    ```text
    If the ideas have the same name in the localisation, it will show up as modifying the idea rather than swapping them.
    The add will occur before the removal of the old idea.
    ```
  - Version Added: 1.3

- **remove_ideas**
  - Parameters:
    ```text
    <idea>
    The idea to remove.
    ```
  - Example:
    ```text
    remove_ideas = my_idea
    ```
  - Example:
    ```text
    remove_ideas = {
        my_idea_1
        my_idea_2
    }
    ```
  - Description: Removes the specified idea from the current scope.
  - Notes: Can be used as a scope to remove multiple at once.
  - Version Added: 1.0

- **remove_ideas_with_trait**
  - Parameters:
    ```text
    <trait>
    The trait to target.
    ```
  - Example:
    ```text
    remove_ideas_with_trait = motorized_equipment_manufacturer
    ```
  - Description: Removes all ideas for the current scope that use the specified trait.
  - Version Added: 1.0

- **show_ideas_tooltip**
  - Parameters:
    ```text
    <idea>
    The idea to display.
    ```
  - Example:
    ```text
    show_ideas_tooltip = my_idea
    ```
  - Description: Displays the specified idea in the tooltip for the current effect scope. Does not add the idea.
  - Version Added: 1.0

### Units

- **load_oob**
  - Parameters:
    ```text
    <oob>
    The filename of the order of battle to load, without the .txt extension.
    ```
  - Example:
    ```text
    load_oob = "GER_default"
    ```
  - Description:
    ```text
    Loads the specified order of battle for the current scope, applying the effects within. The filename with the
    .txt
    extension omitted is used as the effect's target.
    ```
  - Notes:
    ```text
    Orders of battle are stored within
    /Hearts of Iron IV/history/units/*.txt
    . Primarily used to spawn divisions at specified locations.
    ```
  - Version Added: 1.0

- **division_template**
  - Parameters:
    ```text
    name
    The name of the division.
    The composition of the division. Sub-units are defined in
    /Hearts of Iron IV/common/units/*.txt
    files.
    division_names_group = <group>
    The division names group that the template will use, deciding on the automatically-generated names of any new divisions built using that template. Optional, assigns one automatically if omitted. These are defined within
    /Hearts of Iron IV/common/units/names_divisions/*.txt
    files.
    is_locked = <bool>
    Whether the division is locked to modification and deletion. Optional.
    force_allow_recruiting = <bool>
    Whether the locked template can have units deployed using it without allowing editing. Optional, only has an effect in locked templates.
    division_cap = <int>
    The maximum amount of divisions that this template may have; requires the template to be locked. Optional.
    priority = <int>
    The priority the template receives in receiving supplies. Goes from 0 to 2. Optional, 1 by default.
    template_counter = <int>
    The icon used by the division as an integer. Optional, defaults to the icon of the most common sub-unit within. The icons are defined as sprites within any
    /Hearts of Iron IV/interface/*.gfx
    file (By default
    subuniticons.gfx
    ) with the pattern of
    GFX_div_templ_<int>_large
    and
    GFX_div_templ_<int>_small
    .
    override_model = <entity>
    Enforces the entity used by the units using this template to be the specified one
    . Optional.
    ```
  - Example:
    ```text
    regiments = {
        <unit> = { x = 0 y = 0 }
    }
    support = {
        <unit> = { x = 0 y = 0 }
    }
    ```
  - Example:
    ```text
    division_template = {
        name = "Test"
        is_locked = yes
        division_cap = 3 
        division_names_group = USA_INF_01
        priority = 0
        template_counter = 0
        regiments = {
            infantry = { x = 0 y = 0 }
            infantry = { x = 0 y = 1 }
            infantry = { x = 0 y = 2 }
            infantry = { x = 0 y = 3 }
        }
        support = {
            military_police = { x = 0 y = 0 }
        }
    }
    ```
  - Description: Creates and adds the specified division template to the current scope.
  - Notes:
    ```text
    The
    x
    and
    y
    attributes represent the rows and columns in the division designer and start from 0. No tooltip is shown.
    ```
  - Version Added: 1.0

- **create_colonial_division_template**
  - Parameters:
    ```text
    subject = <country>
    Country tag for an overlords subject.
    division_template = { ... }
    The regular effect to create a
    division template
    .
    ```
  - Example:
    ```text
    create_colonial_division_template = {
      subject = RAJ
      division_template = {
        name = "Infantry Division"
        division_names_group = RAJ_INF_01
        ...
        regiments = {
          infantry = { x = 0 y = 0 }
          infantry = { x = 0 y = 1 }
         }
      }
    }
    ```
  - Description: Create a colonial division template for overlord/owner.
  - Notes: In country scope of overlord, E.g. ROOT = ENG.
  - Version Added: 1.15

- **add_units_to_division_template**
  - Parameters:
    ```text
    template_name = <string>
    The template to change. Optional if used in division scope.
    The units to add to the template. Sub-units are defined in
    /Hearts of Iron IV/common/units/*.txt
    files.
    ```
  - Example:
    ```text
    regiments = {
        <unit> = <column>
    }
    support = {
        <unit> = <column>
    }
    ```
  - Example:
    ```text
    add_units_to_division_template = {
        template_name = "Test"
        regiments = {
            infantry = 2
            infantry = 2
        }
        support = {
            military_police = 0
        }
    }
    ```
  - Description: Adds the specified brigades to first available slots of specified columns to the template (if possible).
  - Notes: Columns go left-to-right starting with 0. Can also be used in division scope.
  - Version Added: 1.0

- **set_division_template_lock**
  - Parameters:
    ```text
    division_template = <string>
    The name of the division template.
    is_locked = <bool>
    Whether the division is locked or not.
    ```
  - Example:
    ```text
    set_division_template_lock = {
        division_template = "Infantry Division"
        is_locked = yes
    }
    ```
  - Description: Toggles the locked status on a division template for the current scope, which prevents editing or deletion.
  - Version Added: 1.5

- **country_lock_all_division_template**
  - Parameters:
    ```text
    <bool>
    Boolean.
    OR
    is_locked = <bool>
    Boolean.
    desc = <loc_key>
    Tooltip.
    ```
  - Example:
    ```text
    country_lock_all_division_template = yes
    ```
  - Example:
    ```text
    country_lock_all_division_template = {
      is_locked = yes
      desc = loc_key
    }
    ```
  - Description: Locks all division templates for the current scope.
  - Notes: Used to prevent training, disbanding, and editing units.
  - Version Added: 1.9

- **set_division_force_allow_recruiting**
  - Parameters:
    ```text
    division_template = <string>
    Template to modify.
    force_allow_recruiting = <bool>
    Whether to allow or disallow recruiting. Defaults to true if unset.
    ```
  - Example:
    ```text
    set_division_force_allow_recruiting = {
        division_template = "My locked template"
    }
    ```
  - Description: Changes whether it's possible to recruit divisions of a locked template without unlocking the template.
  - Version Added: 1.12

- **set_division_template_cap**
  - Parameters:
    ```text
    division_template = <string>
    The name of the division template.
    division_cap = <int>
    The division cap.
    ```
  - Example:
    ```text
    set_division_template_cap = { 
    	division_template = "Swiss Citizen Militia" 
    	division_cap = SWI_militia_division_cap
    }
    ```
  - Description: Sets the cap of a division template. The template has to be locked first.
  - Version Added: 1.12

- **clear_division_template_cap**
  - Parameters:
    ```text
    division_template = <string>
    The name of the division template.
    ```
  - Example:
    ```text
    clear_division_template_cap = { 
    	division_template = "Swiss Citizen Militia"
    }
    ```
  - Description: Clears the cap on the template, allowing it to have an unlimited amount of divisions.
  - Version Added: 1.12

- **delete_unit_template_and_units**
  - Parameters:
    ```text
    division_template = <string>
    The name of the division template.
    ```
  - Example:
    ```text
    delete_unit_template_and_units = {
        division_template = "Infantry Division"
        disband = yes #will refund equipment and manpower
    }
    ```
  - Description: Deletes the specified division template and all units using it for the current scope.
  - Version Added: 1.5

- **delete_unit**
  - Parameters:
    ```text
    state = <number id>
    The id number of the state the unit must be in.
    division_template = <string>
    The template the units must use to be deleted.
    id = <int>
    The id given to the unit if created via the
    create_unit
    effect.
    disband = <bool>
    If true, will refund equipment and manpower.
    ```
  - Example:
    ```text
    delete_unit = {
        state = 787
        disband = yes #will refund equipment and manpower
    }
    ```
  - Example:
    ```text
    delete_unit = {
        division_template = "Infantry Division"
    }
    ```
  - Example:
    ```text
    delete_unit = {} # Will delete all units
    ```
  - Description: Deletes all units that meet the filters.
  - Notes: No tooltip is generated. delete_units can be used if deleting all units of a specific template.
  - Version Added: 1.5

- **delete_units**
  - Parameters:
    ```text
    division_template = <string>
    The template the units must use to be deleted.
    disband = <bool>
    If true, will refund equipment and manpower.
    ```
  - Example:
    ```text
    delete_units = {
        division_template = "Infantry Division"
        disband = yes
    }
    ```
  - Description: Deletes all units with a certain template.
  - Notes: Generates a tooltip, unlike delete_unit. Mandatory to specify a division_template.
  - Version Added: 1.9

- **create_railway_gun**
  - Parameters:
    ```text
    equipment = <type>
    Equipment type used by the railway gun.
    name = <string>
    The name used by the railway gun. Optional.
    location = <province>
    Location where the railway gun is created. Assumes the capital by default.
    ```
  - Example:
    ```text
    create_railway_gun = {
        equipment = railway_gun_equipment_1
    	name = TAG_new_railway_gun
    	location = 12406
    }
    ```
  - Description: Creates a railway gun.
  - Version Added: 1.11

- **teleport_railway_guns_to_deploy_province**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    teleport_railway_guns_to_deploy_province = yes
    ```
  - Description: Teleports all railway guns to the province where they get deployed.
  - Version Added: 1.11

- **add_unit_bonus**
  - Parameters: <subunit> = { ... }
  - Example:
    ```text
    add_unit_bonus = {
      category_light_infantry = {
        soft_attack = 0.05
      }
    
      cavalry = {
        soft_attack = 0.05
        hard_attack = 0.05
      }
    }
    ```
  - Description: Adds permanent subunit and subunit category bonuses for country.
  - Version Added: ???

### Equipment

- **set_equipment_fraction**
  - Parameters:
    ```text
    <float> / <variable>
    The fraction of equipment to remove.
    ```
  - Example:
    ```text
    set_equipment_fraction = 0.5
    ```
  - Description: Reduces the overall equipment stockpile by the specified fraction.
  - Notes:
    ```text
    This should
    not
    be used in civil wars to simulate stockpile splitting.
    start_civil_war
    automatically divides stockpiles according to the respective size.
    ```
  - Version Added: 1.0

- **add_equipment_to_stockpile**
  - Parameters:
    ```text
    type = <equipment>
    The equipment to add. Either types and archetypes are accepted.
    amount = <int> / <variable>
    The amount to add.
    producer = <country> / <variable>
    Defines who produced the equipment. Optional, defaults to the current scope.
    variant_name = <string>
    The equipment variant to add. Mandatory if a variant needs to be created to produce the equipment, optional otherwise.
    ```
  - Example:
    ```text
    add_equipment_to_stockpile = {
        type = infantry_equipment
        amount = -100
        producer = GER
    }
    ```
  - Example:
    ```text
    add_equipment_to_stockpile = {
        type = medium_tank_chassis_1
        amount = 100
        variant_name = "Panzer III"
    }
    ```
  - Description: Edits the equipment stockpile of the current scope, adds or removes equipment of a specified type or archetype.
  - Notes: With negative numbers, optionally specifying a producer will ensure only equipment with that producer gets removed. The equipment must be unlocked by the producer for the effect to succeed.
  - Version Added: 1.0

- **send_equipment**
  - Parameters:
    ```text
    type = <equipment>
    The equipment to add. Can be archetype.
    amount = <int> / <variable>
    The amount to add.
    target = <country> / <variable>
    Which country receives the equipment.
    ```
  - Example:
    ```text
    send_equipment = {
        equipment = infantry_equipment
        amount = 100
        target = GER
    }
    ```
  - Description: Sends the specified amount of equipment to the specified target, removing said equipment from the current scope.
  - Notes: Cannot remove equipment into negatives, in which case equipment will not be received by the target in entirety.
  - Version Added: 1.0

- **send_equipment_fraction**
  - Parameters:
    ```text
    value = <0-1>
    How much equipment to send.
    target = <country> / <variable>
    Which country receives the equipment.
    ```
  - Example:
    ```text
    send_equipment_fraction = {
        value = 0.3
        target = GER
    }
    ```
  - Description: Sends the specified fraction of equipment to the specified target, removing said equipment from the current scope.
  - Version Added: 1.9

- **create_production_license**
  - Parameters:
    ```text
    target = <country>
    Which country receives the license.
    cost_factor = <float>
    Modifies the production cost.
    Equipment scope
    type = <equipment>
    The equipment the country is licensed to produce. Must be an non-archetype equipment.
    version = <int>
    The version indicates which variant should be licensed. The default is 0, meaning the base variant.
    new_prioritised = <boolean>
    Whether new equipment is prioritised or not. Yes by default.
    ```
  - Example:
    ```text
    create_production_license = {
        target = HUN
        equipment = {
            type = fighter_equipment_1
            version = 0
            new_prioritised = no
        }
        cost_factor = 0
    }
    ```
  - Description: Grants the specified country a license to produce the specified equipment from the current scope.
  - Version Added: 1.4

- **add_equipment_subsidy**
  - Parameters:
    ```text
    cic = <int>
    The amount of economic capacity required by the subsidy.
    equipment_type = <archetype>
    The equipment archetype that the subsidy is for.
    seller_tags = { <countries }
    Countries that can have the subsidy.
    seller_trigger = <scripted trigger>
    The trigger deciding which countries can have the subsidy.
    ```
  - Example:
    ```text
    add_equipment_subsidy = {
        cic = 300
        equipment_type = support_equipment
        seller_tags = { BHR }
    }
    ```
  - Example:
    ```text
    add_equipment_subsidy = {
        cic = 1000
        equipment_type = infantry_equipment
        seller_trigger = my_scripted_trigger
    }
    ```
  - Description:
    ```text
    Creates an equipment subsidy on the
    international market
    .
    ```
  - Notes:
    ```text
    seller_tags
    and
    seller_trigger
    are mutually exclusive. In the scripted trigger,
    ROOT
    is the country with the subsidy and
    FROM
    is the seller.
    ```
  - Version Added: 1.13

- **add_cic**
  - Parameters:
    ```text
    <int>
    The amount of economic capacity to add.
    ```
  - Example:
    ```text
    add_cic = 300
    ```
  - Description:
    ```text
    Modifies the economic capacity bank on the
    international market
    .
    ```
  - Notes: The economic capacity will be capped to 0 if the total after the effect is negative.
  - Version Added: 1.13

- **create_equipment_variant**
  - Parameters:
    ```text
    name = <string>
    The name of the variant.
    type = <equipment>
    The equipment type the variant is of.
    parent_version = <int>
    Ordering for multiple variants of the same equipment. 0 is the oldest, 1 is the second-oldest, etc. Optional, 0 by default.
    show_position = <bool>
    Dynamic equipment version numbering. If disabled removes the suffix from the equipment name. Numbering linked to
    parent_version
    . Optional, yes by default.
    obsolete = <bool>
    Whether the equipment variant is flagged as obsolete within the GUI and for AI. Optional, no by default.
    mark_older_equipment_obsolete = <bool>
    Marks all older (non-chassis) equipment variants as obsolete as long as the following matches: Archetype, niche, mission set (for planes). Optional, defaults to false.
    name_group = <name group>
    The name group used for equipment. Stored in
    /Hearts of Iron IV/common/units/names_ships
    . Optional, can only be defined for ships.
    role_icon_index = <int>/auto
    Index of the role icon that will be used, as an integer. If set to "auto", will pick automatically. If set to 0, will be unset. Optional, only can be defined for ships.
    model = <model name>
    Model that will be used by the equipment on the world map. Optional.
    icon = <sprite>
    The icon that will be used by equipment. Stored as a spriteType within
    /Hearts of Iron IV/interface/*.gfx
    . Optional.
    design_team = mio:<MIO>
    The
    military industrial organisation
    that should be set as the designer of the equipment. Optional.
    allow_without_tech = <bool>
    If set, bypasses the requirement that the equipment that the variant is for must be unlocked through research. Optional, defaults to false.
    Upgrade scope
    <upgrade> = <amount>
    The upgrades configuration for the variant.
    Module scope
    <slot> = <module>
    The modules configuration for the variant.
    ```
  - Example:
    ```text
    create_equipment_variant = {
        name = "Vetehinen Class"								
        type = ship_hull_submarine_1
        name_group = FIN_SS_HISTORICAL
        role_icon_index = 1
        modules = {
            fixed_ship_torpedo_slot = ship_torpedo_sub_1
            fixed_ship_engine_slot = sub_ship_engine_1
            rear_1_custom_slot = ship_mine_layer_sub
        }
    }
    ```
  - Example:
    ```text
    create_equipment_variant = {
        name = "He 112"
        type = fighter_equipment_0
        obsolete = yes
        upgrades = {
            plane_gun_upgrade = 1
            plane_range_upgrade = 1
        }
    }
    ```
  - Example:
    ```text
    create_equipment_variant = {
        name = "Light Tank Mk. IV"
        type = light_tank_chassis_1
        parent_version = 1
        modules = {
            main_armament_slot = tank_heavy_machine_gun
        }
        upgrades = {
            tank_nsb_engine_upgrade = 2
        }
        icon = "GFX_ENG_basic_light_tank_medium"
        model = ENG_MKIV_light_tank_entity
        design_team = mio:ENG_vauxhall_organization
    }
    ```
  - Description: Creates the specified equipment variant for the current scope.
  - Notes:
    ```text
    Role icons for ships are defined in
    /Hearts of Iron IV/gfx/army_icons/army_icons.txt
    .
    Upgrades are defined within
    /Hearts of Iron IV/common/units/equipment/upgrades/*.txt
    .
    Equipment types, including module slots for them, are defined within
    /Hearts of Iron IV/common/units/equipment/*.txt
    .
    Equipment modules are defined within
    /Hearts of Iron IV/common/units/equipment/modules/*.txt
    .
    ```
  - Version Added: 1.0

- **add_equipment_production**
  - Parameters:
    ```text
    amount = <int>
    The amount to produce before automatically stopping. Optional.
    requested_factories = <int>
    The number of factories to assigned initially. Optional.
    progress = <float>
    The initial production progress. Optional.
    efficiency = <float>
    The initial production efficiency. Optional.
    name = <string>
    The name that'll be used for the equipment, such as with ships. Optional.
    industrial_manufacturer = mio:<MIO>
    The
    military industrial organisation
    that's set as the equipment's designer.
    Equipment scope
    type = <equipment>
    The name of the equipment to produce.
    creator = <country>
    The country which is producing the equipment. Used if root scope isn't producer. Optional.
    version_name = <string>
    The name of the variant to produce. Optional.
    ```
  - Example:
    ```text
    add_equipment_production = {
        equipment = {
            type = light_cruiser_2
        }
        requested_factories = 1
        progress = 0.95
        amount = 1
    }
    ```
  - Description: Starts a production line for the specified equipment for the current scope.
  - Version Added: 1.0

- **add_design_template_bonus**
  - Parameters:
    ```text
    name = <loc_key>
    Name.
    uses = <int>
    The amount of times the discount can be used.
    cost_factor = <float>
    Discount.
    equipment = <equipment>
    Can be equipment type and archetype.
    ```
  - Example:
    ```text
    add_design_template_bonus = {
      name = air_equipment
      uses = 1
      cost_factor = 0.75
      equipment = small_plane_airframe
      equipment = medium_plane_airframe
      equipment = large_plane_airframe
    }
    ```
  - Description: Add free bonus design discount to given types with a set of uses.
  - Notes:
    ```text
    The value for
    uses
    and
    cost_factor
    can either be an absolute value or a script constant. Can use several equipment types, where 1 is mandatory.
    ```
  - Version Added: 1.15

- **add_equipment_bonus**
  - Parameters:
    ```text
    project = <>
    Optional, special project scope for using special project name. If not set, the name will be used.
    name = <loc_key>
    Name.
    bonus = { ... }
    Bonus.
    ```
  - Example:
    ```text
    add_equipment_bonus = {
      project = FROM
      bonus = {
        armor = { # Type of equipment
          armor_value = 3
          soft_attack = 3
          instant = yes
        }
        small_plane_naval_bomber_airframe = {
          air_range = 0.1
          naval_strike_attack = 0.1
        }
      }
    }
    ```
  - Description: Adds the specified equipment bonuses to the country. As description the given loc key or the name of given special project will be used. Same usage as in Ideas/National spirits.
  - Version Added: 1.15

- **set_equipment_version_number**
  - Parameters:
    ```text
    type = <equipment>
    Equipment type.
    version = <int>
    Version to set.
    ```
  - Example:
    ```text
    set_equipment_version_number = {
      type = small_plane_airframe_1
      version = 4
    }
    ```
  - Description: Changes current version number for a given equipment type to N. The next equipment variant created from that type will have version number N+1.
  - Notes:
    ```text
    Set "Variant max version" to specified version.
    Provides no tooltip.
    ```
  - Version Added: 1.16

### Military

- **destroy_ships**
  - Parameters:
    ```text
    type = <ship>
    The type of ship to destroy.
    count = <int> or all
    The amount to destroy.
    ```
  - Example:
    ```text
    destroy_ships = {
        type = destroyer
        count = all
    }
    ```
  - Description: Destroys the specified type and amount of ships controlled by the current scope.
  - Version Added: 1.5

- **transfer_navy**
  - Parameters:
    ```text
    target = <country>
    The target country.
    ```
  - Example:
    ```text
    transfer_navy = {
        target = GER
    }
    ```
  - Description: Transfers the current scope navy to the specified country.
  - Version Added: 1.5

- **transfer_ship**
  - Parameters:
    ```text
    type = <ship>
    The type of ship to transfer.
    target = <country>
    The target country.
    prefer_name = <string>
    Name of ship in origin navy that will preferably be transferred to target navy. Optional.
    exclude_refitting = <bool>
    Determines whether ships that are being refitted will be transferred. Optional.
    ```
  - Example:
    ```text
    transfer_ship = {
        prefer_name = "HMS Achilles"
        type = light_cruiser
        target = NZL
        exclude_refitting = no
    }
    ```
  - Description: Transfers the specified type of ship from the current scope to the specified country.
  - Version Added: 1.4

- **create_ship**
  - Parameters:
    ```text
    type = <ship>
    The type of ship to create.
    equipment_variant = <string>
    The equipment variant to use.
    creator = <country>
    The country that created this ship. Optional.
    name = <string>
    Name of the ship. Optional.
    amount = <int>
    The amount of ships to create. Optional, defaults to 1.
    ```
  - Example:
    ```text
    FRA = {
        create_ship = {
            type = ship_hull_submarine_1
            equipment_variant = "S Class"
            creator = ENG
            name = "My ship name"
        }
    }
    ```
  - Description: Create a ship from another country and assign it to the reserve fleet. If not set, it will be the scoped country.
  - Version Added: 1.9

- **add_mines**
  - Parameters: Add mines to a strategic region for the current country.
  - Example:
    ```text
    add_mines = { region = 42 amount = 100 }
    ```
  - Description: Add mines to a strategic region.
  - Version Added: 1.6

- **add_ace**
  - Parameters:
    ```text
    name = <string>
    The name of the ace.
    surname = <string>
    The surname of the ace.
    callsign = <string>
    The callsign of the ace.
    type = <type>
    The ace type.
    is_female = <bool>
    The gender of the ace.
    ```
  - Example:
    ```text
    add_ace = {
        name = "Amelia"
        surname = "Earhart"
        callsign = "Revenant"
        type = fighter_genius
        is_female = yes
    }
    ```
  - Description: Adds an ace for the current scope.
  - Notes:
    ```text
    Ace types found in
    /Hearts of Iron IV/common/aces/*.txt
    .
    ```
  - Version Added: 1.0

- **unlock_tactic**
  - Parameters:
    ```text
    <string>
    Tactic to unlock.
    ```
  - Example:
    ```text
    unlock_tactic = tactic_masterful_blitz
    ```
  - Description: Unlocks the specified combat tactic for the country.
  - Version Added: 1.17

### Doctrine

- **add_doctrine_cost_reduction**
  - Parameters:
    ```text
    name = <loc_key>
    Optional tooltip showing why the doctrine has reduced cost in the doctrine menu.
    cost_reduction = <float>
    Percentage of cost reduced.
    uses = <int>
    Number of times the cost reduction can be used.
    category = <doctrine category>
    Which doctrine category the cost reduction will apply to. (Ex:
    land_doctrine
    ,
    air_doctrine
    .)
    ```
  - Example:
    ```text
    add_doctrine_cost_reduction = {
    	cost_reduction = 0.5
    	uses = 2
    	category = land_doctrine
    }
    ```
  - Description: Adds a limited use cost reduction for doctrines.
  - Notes:
    ```text
    For a general doctrine cost reduction, see "<land/air/naval>_doctrine_cost_factor" in
    Modifiers
    .
    ```
  - Version Added: 1.11

- **add_mastery**
  - Parameters:
    ```text
    amount = <int>
    Amount of mastery to add.
    folder = <string>
    Optional - will filter by tracks in the specified folder.
    grand_doctrine = <string>
    Optional - will filter by tracks in folders with the specified grand doctrine.
    sub_doctrine = <string>
    Optional - will filter by tracks with the specified subdoctrine.
    track = <string>
    Optional - will filter by tracks of the specified type.
    index = <int>
    Optional - will filter by the track index within the folder (0-indexed).
    ```
  - Example:
    ```text
    add_mastery = {
        amount = 100
        # FILTERS:
        folder = land
        grand_doctrine = mobile_warfare
        sub_doctrine = mobile_infantry
        track = infantry
        index = 1
    }
    ```
  - Description: Adds doctrine mastery.
  - Notes: You can use flexible filters to have this effect apply to all tracks that match the specified folder, grand doctrine, subdoctrine or specific track. If a certain filter is not present, it will be counted as a pass. For example, you can add mastery to all active tracks in all folders by not specifying any filters at all.
  - Version Added: 1.17

- **add_daily_mastery**
  - Parameters:
    ```text
    amount = <float>
    Amount of mastery to add per day.
    days = <int>
    Number of days to apply the daily mastery gain for.
    name = <loc_key>
    Loc key - will be used in descriptions to show the source of the mastery gain.
    folder = <string>
    Optional - will filter by tracks in the specified folder.
    grand_doctrine = <string>
    Optional - will filter by tracks in folders with the specified grand doctrine.
    sub_doctrine = <string>
    Optional - will filter by tracks with the specified subdoctrine.
    track = <string>
    Optional - will filter by tracks of the specified type.
    index = <int>
    Optional - will filter by the track index within the folder (0-indexed).
    ```
  - Example:
    ```text
    add_daily_mastery = {
        amount = 0.5
        days = 90
        name = CHI_military_affairs_commission_sea
        # FILTERS:
        folder = land
        grand_doctrine = mobile_warfare
        sub_doctrine = mobile_infantry
        track = infantry
        index = 1
    }
    ```
  - Description: Adds doctrine mastery daily for a certain duration.
  - Notes: You can use flexible filters to have this effect apply to all tracks that match the specified folder, grand doctrine, subdoctrine or specific track. If a certain filter is not present, it will be counted as a pass.	For example, you can add mastery to all active tracks in all folders by not specifying any filters at all.
  - Version Added: 1.17

- **add_mastery_bonus**
  - Parameters:
    ```text
    bonus = <float>
    Bonus factor, e.g. 0.1 = +10%
    days = <int>
    Number of days to apply the bonus mastery gain for.
    name = <loc_key>
    Loc key - will be used in descriptions to show the source of the mastery gain.
    folder = <string>
    Optional - will filter by tracks in the specified folder.
    grand_doctrine = <string>
    Optional - will filter by tracks in folders with the specified grand doctrine.
    sub_doctrine = <string>
    Optional - will filter by tracks with the specified subdoctrine.
    track = <string>
    Optional - will filter by tracks of the specified type.
    index = <int>
    Optional - will filter by the track index within the folder (0-indexed).
    ```
  - Example:
    ```text
    add_mastery_bonus = {
        bonus = 0.5
        days = 90
        name = CHI_military_affairs_commission_sea
        # FILTERS:
        folder = land
        grand_doctrine = mobile_warfare
        sub_doctrine = mobile_infantry
        track = infantry
        index = 1
    }
    ```
  - Description: Get a bonus to doctrine mastery gain for a certain duration.
  - Notes: You can use flexible filters to have this effect apply to all tracks that match the specified folder, grand doctrine, subdoctrine or specific track. If a certain filter is not present, it will be counted as a pass. For example, you can add mastery to all active tracks in all folders by not specifying any filters at all.
  - Version Added: 1.17

- **set_grand_doctrine**
  - Parameters:
    ```text
    <string>
    Grand doctrine id.
    ```
  - Example:
    ```text
    set_grand_doctrine = mobile_warfare
    ```
  - Description: Activate (unlock and assign) the specified grand doctrine.
  - Version Added: 1.17

- **set_sub_doctrine**
  - Parameters:
    ```text
    <string>
    Subdoctrine id.
    OR
    sub_doctrine = <string>
    Subdoctrine id.
    folder = <string>
    Optional, in case you need to specify the folder.
    track = <int>
    Optional, in case you need to specify the track index within the folder. Note that this is the track index (starting with 0) among ALL the tracks in the folder, not just the ones that match the subdoctrine. So in a case where a grand doctrine has the tracks: 'infantry - armor - armor - operations', you would use track = 1 to refer to the first armor track, and track = 2 to refer to the second armor track.
    ```
  - Example:
    ```text
    set_sub_doctrine = mobile_infantry
    ```
  - Example:
    ```text
    set_sub_doctrine = {
        sub_doctrine = mobile_infantry
        folder = land
        track = 1
    }
    ```
  - Description: Activate (unlock and assign) the specified subdoctrine.
  - Notes: By default, the subdoctrine is assigned to the first matching track that the system can find. However, you can also specify a specific folder and track index to assign the subdoctrine to, in case the same track appears in multiple folders, or multiple times in the same folder.
  - Version Added: 1.17

### Intelligence

- **create_intelligence_agency**
  - Parameters:
    ```text
    name = <string>
    The name of the intelligence agency. (Optional)
    icon = <sprite>
    The icon of the intelligence agency. (Optional)
    ```
  - Example:
    ```text
    create_intelligence_agency = {
        name = "A.G.E.N.C.Y"
        icon = GFX_intelligence_agency_logo_agency
    }
    ```
  - Example:
    ```text
    create_intelligence_agency = yes
    ```
  - Description: Creates an Intelligence Agency.
  - Notes:
    ```text
    Both parameters are not required, thus you can call the effect with just
    create_intelligence_agency = yes
    . This will check if any specific intelligence agency cosmetics should be used for the nation, and if not it uses the default.
    ```
  - Version Added: 1.9

- **upgrade_intelligence_agency**
  - Parameters: Allows to unlock automatically an intelligence agency upgrade
  - Example:
    ```text
    upgrade_intelligence_agency = upgrade_form_department
    ```
  - Example:
    ```text
    upgrade_intelligence_agency = <upgrade>
    ```
  - Description: Unlocks an Intelligence Agency Upgrade.
  - Notes: Upgrades can be found in common/intelligence_agency_upgrades
  - Version Added: 1.9

- **add_decryption**
  - Parameters:
    ```text
    target = <tag>
    Towards which country to add decryption.
    amount = <int>
    How much decryption to add in flat numbers.
    ratio = <0-1>
    How much decryption ratio to add.
    ```
  - Example:
    ```text
    add_decryption = {
        target = GER
        amount = 300
    }
    ```
  - Example:
    ```text
    add_decryption = {
        target = GER
        ratio = 0.5
    }
    ```
  - Description: Adds decryption towards the target country
  - Notes:
    ```text
    target
    and
    ratio
    arguments are mutually exclusive.
    ```
  - Version Added: 1.9

- **add_intel**
  - Parameters:
    ```text
    target = <tag>
    Towards which country to add intelligence.
    civilian_intel = <int>
    How much civilian intel to add.
    army_intel = <int>
    How much army intel to add.
    navy_intel = <int>
    How much navy intel to add.
    airforce_intel = <int>
    How much airforce intel to add.
    ```
  - Example:
    ```text
    add_intel = {
        target = GER
        civilian_intel = 3
        army_intel = 2
        navy_intel = 1
        airforce_intel = 2
    }
    ```
  - Description: Adds the specified amount of intel towards the specified country.
  - Notes: If an intel argument is left out, 0 is assumed.
  - Version Added: 1.9

- **add_operation_token**
  - Parameters:
    ```text
    tag = <tag>
    Towards which country to add a token on.
    token = <id>
    Which token to add.
    ```
  - Example:
    ```text
    add_operation_token = {
        tag = GER
        token = token_test
    }
    ```
  - Description: Adds an operation token towards the country, allowing access to more intel or applying a targeted modifier.
  - Notes:
    ```text
    Operation tokens are defined in
    /Hearts of Iron IV/common/operation_tokens/*
    .
    ```
  - Version Added: 1.9

- **remove_operation_token**
  - Parameters:
    ```text
    tag = <tag>
    Towards which country to remove a token from.
    token = <id>
    Which token to remove.
    ```
  - Example:
    ```text
    remove_operation_token = {
        tag = GER
        token = token_test
    }
    ```
  - Description: Removes an operation token from the country.
  - Notes:
    ```text
    Operation tokens are defined in
    /Hearts of Iron IV/common/operation_tokens/*
    .
    ```
  - Version Added: 1.9

- **capture_operative**
  - Parameters:
    ```text
    operative = <tag>
    Which operative to capture.
    ignore_death_chance = <bool>
    Whether to ignore the death chance on capture (no by default).
    ```
  - Example:
    ```text
    capture_operative = {
        operative = PREV
        ignore_death_chance = yes
    }
    ```
  - Example:
    ```text
    capture_operative = PREV
    ```
  - Description: Captures the specified operative.
  - Notes:
    ```text
    Operatives can be referred to by using
    tags that refer to scopes
    ```
  - Version Added: 1.9

- **create_operative_leader**
  - Parameters:
    ```text
    bypass_recruitment = <bool>
    Whether the operative is directly added to the list of available operatives or needs to be recruited.
    available_to_spy_master = <bool>
    Whether the operative can be recruited by the spy master. bypass_recruitment should be set to no.
    portrait_tag_override = <bool>
    If selecting a random portrait, create one that is from the specified country rather than the current country.
    name = <string>
    The name of the operative.
    GFX = <string>
    The graphical reference of the picture of the leader, defined as a sprite within any
    /Hearts of Iron IV/interface/*.gfx
    file.
    nationalities = { <tag> }
    The nationalities of the operative.
    traits = { <trait> }
    The traits the leader spawns with.
    gender = <male|female>
    The gender of the operative. Defaults to random.
    ```
  - Example:
    ```text
    create_operative_leader = {
    	name = "Jacques Duclos"
    	GFX = GFX_portrait_jacques_duclos
    	traits = { operative_infiltrator operative_natural_orator }
    	bypass_recruitment = no
    	available_to_spy_master = yes
    	nationalities = { FRA POL }
    }
    ```
  - Description: Creates an operative for the current scope with the specified attributes.
  - Notes:
    ```text
    Traits are found in
    /Hearts of Iron IV/common/unit_leader/*.txt
    . All arguments aside from bypass_recruitment are optional.
    Must use a spriteType for the portrait
    , a direct link as in "gfx/leaders/TAG/filename.dds" will not work.
    ```
  - Version Added: 1.9

- **free_operative**
  - Parameters:
    ```text
    <tag>
    The operative to be freed.
    ```
  - Example:
    ```text
    free_operative = PREV
    ```
  - Description: Frees the specifies operative.
  - Notes:
    ```text
    Operatives can be referred to by using
    tags that refer to scopes
    ```
  - Version Added: 1.9

- **free_random_operative**
  - Parameters:
    ```text
    captured_by = <tag>
    The country that captured the operative.
    all = <bool>
    Whether to free all operatives or not (Defaults to no).
    ```
  - Example:
    ```text
    free_random_operative = {
    	captured_by = POL
    	all = yes
    }
    ```
  - Description: Frees one random captured operative or all of them.
  - Version Added: 1.9

- **kill_operative**
  - Parameters:
    ```text
    operative = <tag>
    The operative that is killed.
    ```
  - Example:
    ```text
    kill_operative = {
        operative = PREV
    }
    ```
  - Example:
    ```text
    kill_operative = PREV
    ```
  - Description: Kills the targeted operative.
  - Notes:
    ```text
    Operatives can be referred to by using
    tags that refer to scopes
    ```
  - Version Added: 1.9

- **turn_operative**
  - Parameters:
    ```text
    operative = <tag>
    The operative that is turned.
    ```
  - Example:
    ```text
    turn_operative = {
        operative = PREV
    }
    ```
  - Example:
    ```text
    turn_operative = PREV
    ```
  - Description: Turns the targeted operative against their own country, transferring them to the current country.
  - Notes:
    ```text
    Operatives can be referred to by using
    tags that refer to scopes
    . This counts as the operative dying and will trigger the corresponding
    On action
    . Logs an error if used against your own operative.
    ```
  - Version Added: 1.9

- **steal_random_tech_bonus**
  - Parameters:
    ```text
    category = <category name>
    The category to steal from. See
    /Hearts of Iron IV/common/technology_tags/*
    for list.
    folder = naval_folder
    The folder to steal from. See
    /Hearts of Iron IV/common/technology_tags/*
    for list.
    ahead_reduction = <float>
    The reduction to the ahead of time penalty.
    bonus = <float>
    The bonus to research speed.
    base_bonus = <float>
    The backup bonus if no tech is available.
    instant = <bool>
    Whether to instantly give a tech instead of a bonus or not. No by default.
    dynamic = <bool>
    Changes between instant and non-instant based on type. No by default.
    name = <localisation key>
    The name of the bonus.
    target = <tag>
    The country to steal from.
    uses = <int>
    How many times the bonus can be used.
    ```
  - Example:
    ```text
    steal_random_tech_bonus = {
        category = air_equipment
        folder = naval_folder
        ahead_reduction = 0.8
        bonus = 1.2
        base_bonus = 1.1
        dynamic = yes
        name = LOC_KEY
        target = POL
        uses = 2
    }
    ```
  - Description: Steals a random tech bonus from the specified country.
  - Notes: If a country does not have a tech to be stolen, a random bonus will be applied by using base_bonus as a base.
  - Version Added: 1.9

### Characters

These are the character-related effects in the country scope. For effects in character scope, see [§ Character scope](#character-scope).

- **set_nationality**
  - Parameters:
    ```text
    target_country = <country> / <variable>
    The target country.
    character = <character>
    The character to transfer.
    ```
  - Example:
    ```text
    set_nationality = {
        target_country = TZN
        character = OMA_sultan
    }
    ```
  - Description: Switches the specified character to the specified country.
  - Notes:
    ```text
    If you wish to change the nationality of a specific character, and the country getting the effect doesn't have the character recruited already, use the
    command to call them up. Only necessary in 1.11 and beyond.
    ```
  - Example:
    ```text
    every_possible_country = {
        limit = { has_character = ID }
        random_character = {
            limit = { is_character = ID }
            set_nationality = TAG
        }
    }
    ```
  - Version Added: 1.11

- **retire_character**
  - Parameters: <character>
  - Example:
    ```text
    retire_character = GER_Character_Token
    ```
  - Description: Retires the character, removing every role they hold and making them disappear from the game.
  - Notes: Country scope only. The character cannot be re-recruited after retiring.
  - Version Added: 1.11

- **set_character_name**
  - Parameters:
    ```text
    character = <character>
    The character to modify.
    name = <localisation key>
    The new name of the character.
    ```
  - Example:
    ```text
    set_character_name = {
    	character = my_character
    	name = my_name
    }
    ```
  - Description: Sets the new name for the target character.
  - Notes: Can also be used in character scope.
  - Version Added: 1.11

- **character_list_tooltip**
  - Parameters:
    ```text
    limit = { <triggers> }
    Triggers that must be fulfilled to show up in the list.
    random_select_amount = <int>
    Upper bound on the characters that may be shown.
    ```
  - Example:
    ```text
    character_list_tooltip = {
    	limit = {
            has_character_flag = SOV_targeted_for_purge_flag
        }
        random_select_amount = 4
    }
    ```
  - Description: Displays a list of every character meeting the specified limitation and recruited by the current country.
  - Version Added: 1.11

- **add_trait**
  - Parameters:
    ```text
    character = <character>
    The character to modify.
    slot = <slot>
    Slot of the character. Necessary for advisors.
    ideology = <sub-ideology>
    Ideology type of the character. Necessary for country leaders.
    trait = <trait>
    The trait to add.
    ```
  - Example:
    ```text
    add_trait = {
         character = TAG_jane_smith
         slot = political_advisor
         trait = really_good_boss
    }
    ```
  - Example:
    ```text
    add_trait = {
         character = TAG_my_leader
         ideology = liberalism
         trait = field_of_gar
    }
    ```
  - Description: Adds the specified country leader trait to the character.
  - Notes:
    ```text
    Can also be used in character scope
    . Ideology type refers to a sub-type of an ideology group assigned to characters, commonly referred to as sub-ideologies in community jargon. The character slot can be the character's name or id. Using name is recommended because 1.11 made id obsolete.
    ```
  - Version Added: 1.11

- **remove_trait**
  - Parameters:
    ```text
    character = <character>
    The character to modify.
    slot = <slot>
    Slot of the character. Necessary for advisors.
    ideology = <sub-ideology>
    Ideology type of the character. Necessary for country leaders.
    trait = <trait>
    The trait to remove.
    ```
  - Example:
    ```text
    remove_trait = {
        character = TAG_jane_smith
        slot = political_advisor
        trait = really_good_boss
    }
    ```
  - Example:
    ```text
    remove_trait = {
         character = TAG_my_leader
         ideology = liberalism
         trait = field_of_gar
    }
    ```
  - Description: Removes the specified trait from the character.
  - Notes:
    ```text
    Can also be used in character scope
    . Ideology type refers to a sub-type of an ideology group assigned to characters, commonly referred to as sub-ideologies in community jargon. The character slot can be the character's name or id. Using name is recommended because 1.11 made id obsolete.
    ```
  - Version Added: 1.11

#### Unit leaders

- **create_corps_commander**
  - Parameters:
    ```text
    name = <string>
    The name of the leader.
    picture = <string>
    OR
    portrait_path = <string>
    OR
    gfx
    = <string>
    The graphical reference of the picture of the leader.
    skill = <int>
    The skill of the leader.
    attack_skill = <int>
    The attack skill of the leader.
    defense_skill = <int>
    The defense skill of the leader.
    planning_skill = <int>
    The planning skill of the leader.
    logistics_skill = <int>
    The logistics skill of the leader.
    traits = { <trait> }
    The traits the leader spawns with.
    female = <bool>
    The gender of the leader.
    legacy_id = <int>
    The legacy ID used for the unit leader. Optional.
    ```
  - Example:
    ```text
    create_corps_commander = {
    	name = "Jean de Lattre de Tassigny"
    	picture = "Portrait_France_Jean_de_Lattre_de_Tassigny.dds"
    	traits = { trickster brilliant_strategist }
    	skill = 4
    	attack_skill = 4
    	defense_skill = 2
    	planning_skill = 4
    	logistics_skill = 3
    }
    ```
  - Description: Creates a commander for the current scope with the specified attributes.
  - Notes:
    ```text
    Traits are found in
    /Hearts of Iron IV/common/unit_leader/*.txt
    .
    Deprecated
    , recommended to use
    add_corps_commander_role
    instead when possible.
    The created corps commander will not be able to have a portrait if assigned to be a minister via officer corps, causing errors.
    ```
  - Version Added: 1.0

- **create_field_marshal**
  - Parameters:
    ```text
    name = <string>
    The name of the leader.
    picture = <string>
    OR
    portrait_path = <string>
    OR
    gfx
    = <string>
    The graphical reference of the picture of the leader.
    skill = <int>
    The skill of the leader.
    attack_skill = <int>
    The attack skill of the leader.
    defense_skill = <int>
    The defense skill of the leader.
    planning_skill = <int>
    The planning skill of the leader.
    logistics_skill = <int>
    The logistics skill of the leader.
    traits = { <trait> }
    The traits the leader spawns with.
    female = <bool>
    The gender of the leader.
    legacy_id = <int>
    The legacy ID used for the unit leader. Optional.
    ```
  - Example:
    ```text
    create_field_marshal = {
    	name = "Maurice Gamelin"
    	portrait_path = "GFX_portrait_FRA_maurice_gamelin"
    	traits = { defensive_doctrine }
    	skill = 2
    	attack_skill = 1
    	defense_skill = 3
    	planning_skill = 2
    	logistics_skill = 1
    }
    ```
  - Description: Creates a field marshal for the current scope with the specified attributes.
  - Notes:
    ```text
    Traits are found in
    /Hearts of Iron IV/common/unit_leader/*.txt
    . Deprecated, recommended to use
    add_field_marshal_role
    instead when possible.
    The created field marshal will not be able to have a portrait if assigned to be a minister via officer corps, causing errors.
    ```
  - Version Added: 1.0

- **create_navy_leader**
  - Parameters:
    ```text
    name = <string>
    The name of the leader.
    picture = <string>
    OR
    portrait_path = <string>
    OR
    gfx
    = <string>
    The graphical reference of the picture of the leader.
    skill = <int>
    The skill of the leader.
    attack_skill = <int>
    The attack skill of the leader.
    defense_skill = <int>
    The defense skill of the leader.
    maneuvering_skill = <int>
    The maneuvering skill of the leader.
    coordination_skill = <int>
    The coordination skill of the leader.
    traits = { <trait> }
    The traits the leader spawns with.
    female = <bool>
    The gender of the leader.
    legacy_id = <int>
    The legacy ID used for the unit leader. Optional.
    ```
  - Example:
    ```text
    create_navy_leader = {
    	name = "François Darlan"
    	gfx = "GFX_portrait_FRA_francois_darlan"
    	traits = { superior_tactician }
    	skill = 3
    	attack_skill = 2
    	defense_skill = 4
    	maneuvering_skill = 3
    	coordination_skill = 2
    }
    ```
  - Description: Creates a naval leader for the current scope with the specified attributes.
  - Notes:
    ```text
    Traits are found in
    /Hearts of Iron IV/common/unit_leader/*.txt
    . Deprecated, recommended to use
    add_naval_commander_role
    instead when possible.
    The created admiral will not be able to have a portrait if assigned to be a minister via officer corps, causing errors.
    ```
  - Version Added: 1.0

- **remove_unit_leader**
  - Parameters:
    ```text
    <id>
    The id of the unit leader.
    ```
  - Example:
    ```text
    remove_unit_leader = 70
    ```
  - Description: Removes the specified unit leader by their legacy ID.
  - Notes:
    ```text
    Does not work with the character ID. Instead,
    remove_unit_leader_role
    within the scope of the character is recommended when possible.
    ```
  - Version Added: 1.0

- **add_corps_commander_role**
  - Parameters:
    ```text
    character = <character>
    The character to modify.
    <...>
    Army leader role definition
    ```
  - Example:
    ```text
    add_corps_commander_role = {
        Character = GER_Character_token
        skill = 4
        attack_skill = 2
        defense_skill = 3
        planning_skill = 3
        logistics_skill = 5
    }
    ```
  - Description: Sets the specified character to also act as a corps commander.
  - Notes: Can also be used in character scope.
  - Version Added: 1.11

- **add_field_marshal_role**
  - Parameters:
    ```text
    character = <character>
    The character to modify.
    <...>
    Army leader role definition
    ```
  - Example:
    ```text
    add_field_marshal_role = {
      character = GER_Character_token
      skill = 4
      attack_skill = 2
      defense_skill = 3
      planning_skill = 3
      logistics_skill = 5
    }
    ```
  - Description: Sets the specified character to also act as a field marshal.
  - Notes: Can also be used in character scope.
  - Version Added: 1.11

- **add_naval_commander_role**
  - Parameters:
    ```text
    character = <character>
    The character to modify.
    <...>
    Navy leader role definition
    ```
  - Example:
    ```text
    add_naval_commander_role = {
      Character = GER_Character_token
      skill = 4
      attack_skill = 2
      defense_skill = 3
      planning_skill = 3
      logistics_skill = 5
    }
    ```
  - Description: Sets the specified character to also act as an admiral.
  - Notes: Can also be used in character scope.
  - Version Added: 1.11

- **show_unit_leaders_tooltip**
  - Parameters:
    ```text
    <character>
    The character whose name is to be shown.
    ```
  - Example:
    ```text
    show_unit_leaders_tooltip = TAG_my_leader
    ```
  - Description: Shows the name of the specified character as a tooltip.
  - Version Added: 1.11

#### Country leaders

- **create_country_leader**
  - Parameters:
    ```text
    name = <string>
    The name of the leader.
    desc = <string>
    The description of the leader.
    picture = <spriteType>
    The graphical reference to the leader portrait.
    expire = <string>
    When the leader dies in history.
    ideology = <string>
    The sub-ideology of the country leader. Does not accept regular ideologies.
    female = <bool>
    The gender of the leader.
    Traits scope
    <trait>
    The trait to add. Can add multiple.
    ```
  - Example:
    ```text
    create_country_leader = {
    	name = AFG_mohammed_zahir_shah
    	desc = "POLITICS_MOHAMMED_ZAHIR_SHAH_DESC"
    	picture = GFX_AFG_mohammed_zahir_shah
    	expire = "1965.1.1"
    	ideology = despotism
    	traits = {
    	}
    }
    ```
  - Notes:
    ```text
    The portrait uses a spriteType, defined within
    /Hearts of Iron IV/interface/*.gfx
    .
    Sub-ideologies are defined in
    /Hearts of Iron IV/common/ideologies
    .
    Deprecated. Recommended to use
    add_country_leader_role
    instead when possible.
    ```
  - Version Added: 1.0

- **add_country_leader_role**
  - Parameters:
    ```text
    character = <character>
    The character to modify.
    country_leader = { ... }
    Country leader role definition
    promote_leader = <bool>
    Will promote the leader to be the leader of the assigned party. Optional, defaults to false.
    ```
  - Example:
    ```text
    add_country_leader_role = {
        character = GER_character_token
        promote_leader = yes
        country_leader = {
            ideology = fascism_ideology
            expire = "1965.1.1.1"
            traits = { war_industrialist }
        }
    }
    ```
  - Description: Sets the specified character to also act as a country leader, promoting to the party leader if specified.
  - Notes:
    ```text
    Can also be used in character scope.
    Does absolutely nothing if the character already has a country leader role in the ideology group.
    ```
  - Version Added: 1.11

- **promote_character**
  - Parameters:
    ```text
    <character>
    The character to promote.
    OR
    character = <character>
    The character to promote.
    ideology = <ideology type>
    The ideology type used by the country leader role.
    ```
  - Example:
    ```text
    promote_character = GER_erwin_rommel
    ```
  - Example:
    ```text
    promote_character = {
        character = GER_erwin_rommel
        ideology = nazism
    }
    ```
  - Description: Promotes a character to the leader of their political party.
  - Notes:
    ```text
    Can also be used in character scope.
    If the character has multiple country leader roles, specifying the ideology type is mandatory. Ideology type refers to a sub-type of an ideology group assigned to characters, commonly referred to as sub-ideologies in community jargon.
    ```
  - Version Added: 1.11

- **remove_country_leader_role**
  - Parameters:
    ```text
    character = <character>
    The character to modify.
    ideology = <string>
    The ideology type of the character.
    ```
  - Example:
    ```text
    remove_country_leader_role = {
        character = GER_Character_Token
        ideology = socialism
    }
    ```
  - Description: Removes a country leader role from a character.
  - Notes:
    ```text
    Can also be used in character scope.
    Ideology type refers to a sub-type of an ideology group assigned to characters, commonly referred to as sub-ideologies in community jargon.
    ```
  - Version Added: 1.11

- **kill_ideology_leader**
  - Parameters:
    ```text
    <ideology>
    Ideology.
    ```
  - Example:
    ```text
    kill_ideology_leader = communism
    ```
  - Description: Kills the country leader of the designated ideology for the current scope.
  - Version Added: 1.9

- **retire_ideology_leader**
  - Parameters:
    ```text
    <ideology>
    Ideology.
    ```
  - Example:
    ```text
    retire_ideology_leader = fascism
    ```
  - Description: Retires and removes the country leader of the ideology party for the current scope.
  - Version Added: 1.9

- **kill_country_leader**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    kill_country_leader = yes
    ```
  - Description: Kills the country leader for the current scope.
  - Version Added: 1.0

- **retire_country_leader**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    retire_country_leader = yes
    ```
  - Description: Retires and removes the country leader as head of their party for the current scope.
  - Version Added: 1.0

- **set_country_leader_ideology**
  - Parameters:
    ```text
    <government>
    The government to set.
    ```
  - Example:
    ```text
    set_country_leader_ideology = socialism
    ```
  - Description: Changes the country leader's government type for the current scope.
  - Notes: Creates no tooltip.
  - Version Added: 1.0

- **set_country_leader_description**
  - Parameters:
    ```text
    ideology = <ideology>
    The ideology of the country leader, optional.
    desc = <localisation key>
    The new description.
    ```
  - Example:
    ```text
    set_country_leader_description = {
    	ideology = neutrality
    	desc = LOC_KEY
    }
    ```
  - Description: Changes the country leader's description.
  - Notes:
    ```text
    Must use a localisation key from any
    /Hearts of Iron IV/localisation/*.yml
    file, putting the description in quotes will not work.
    Localisation
    for more info
    ```
  - Version Added: 1.9.1

- **set_country_leader_name**
  - Parameters:
    ```text
    ideology = <ideology>
    The ideology of the country leader, optional.
    name = <localisation key>
    The new name.
    ```
  - Example:
    ```text
    set_country_leader_name = {
    	ideology = neutrality
    	name = LOC_KEY
    }
    ```
  - Description: Changes the country leader's name.
  - Version Added: 1.9.1

- **set_country_leader_portrait**
  - Parameters:
    ```text
    ideology = <ideology>
    The ideology of the country leader, optional.
    portrait = <sprite name>
    The new portrait.
    ```
  - Example:
    ```text
    set_country_leader_portrait = {
    	ideology = neutrality
    	portrait = GFX_IMAGE_NAME
    }
    ```
  - Description: Changes the country leader's portrait.
  - Notes:
    ```text
    The portrait must be defined in
    /Hearts of Iron IV/interface/*.gfx
    ```
  - Version Added: 1.9.1

- **add_country_leader_trait**
  - Parameters:
    ```text
    <trait>
    The trait to add.
    ```
  - Example:
    ```text
    add_country_leader_trait = nationalist_symbol
    ```
  - Description: Adds the specified trait to the current country's country leader.
  - Notes:
    ```text
    Traits are found in
    /Hearts of Iron IV/common/country_leader/*.txt
    files.
    ```
  - Version Added: 1.0

- **remove_country_leader_trait**
  - Parameters:
    ```text
    <trait>
    The trait to remove.
    ```
  - Example:
    ```text
    remove_country_leader_trait = nationalist_symbol
    ```
  - Description: Removes the specified trait from the current scope's country leader.
  - Notes:
    ```text
    Traits are found in
    /Hearts of Iron IV/common/country_leader/*.txt
    files.
    ```
  - Version Added: 1.0

- **swap_ruler_traits**
  - Parameters: Similar to swap_ideas. Removes one trait and adds another.
  - Example:
    ```text
    swap_ruler_traits = { remove = <trait> add = <trait> }
    ```
  - Description: Swaps traits.
  - Notes:
    ```text
    Use
    swap_country_leader_traits
    in character scope.
    ```
  - Version Added: 1.6

#### Advisors

- **activate_advisor**
  - Parameters:
    ```text
    <character>
    The character to activate.
    ```
  - Example:
    ```text
    activate_advisor = GER_character_token_air_chief
    ```
  - Description: Hires an advisor, placing them into their respective slot.
  - Version Added: 1.11

- **deactivate_advisor**
  - Parameters:
    ```text
    <character>
    The character to deactivate.
    ```
  - Example:
    ```text
    deactivate_advisor = GER_character_token_air_chief
    ```
  - Description: Dismisses an advisor from their respective slot, leaving it empty.
  - Version Added: 1.11

- **add_advisor_role**
  - Parameters:
    ```text
    character = <character>
    The character to modify.
    advisor = { ... }
    Advisor role definition
    activate = <bool>
    Will activate the advisor (add them directly when the command is run to the countries government). Optional, defaults to false.
    ```
  - Example:
    ```text
    add_advisor_role = {
        character = GER_Character_token
        activate = yes
        advisor = {
            slot = air_chief
            cost = 50
            idea_token = GER_character_token_air_chief
            traits = {
                air_chief_ground_support_2
            }
        }
    }
    ```
  - Description: Sets the specified character to also act as an advisor, activating if specified.
  - Notes:
    ```text
    Can also be used in character scope.
    Trigger and effect blocks (such as
    allowed
    and
    on_add
    ) cannot be added within advisor definitions created this way.
    ```
  - Version Added: 1.11

- **remove_advisor_role**
  - Parameters:
    ```text
    character = <character>
    Specifies the character if the effect is executed in country scope.
    slot = <int>
    The slot where to remove the advisor slot from.
    ```
  - Example:
    ```text
    remove_advisor_role = {
      character = "SOV_genrikh_yagoda"
      slot = political_advisor
    }
    ```
  - Description: Removes the specified advisor role from the character.
  - Notes: Can also be used in character scope.
  - Version Added: 1.11

- **set_can_be_fired_in_advisor_role**
  - Parameters:
    ```text
    character = <character>
    The character to modify.
    slot = <slot>
    The slot of the character to modify.
    value = <bool>
    The value to set.
    ```
  - Example:
    ```text
    set_can_be_fired_in_advisor_role = {
        character = BHR_important_advisor
        value = no
    }
    ```
  - Description:
    ```text
    Changes the
    can_be_fired
    attribute of the advisor, preventing the player from dismissing the advisor.
    ```
  - Notes: Can also be used in character scope.
  - Version Added: 1.12.8

#### Scientists

- **add_scientist_role**
  - Parameters:
    ```text
    character = <character> / <variable>
    The character to modify.
    <...>
    Scientist role definition
    ```
  - Example:
    ```text
    add_scientist_role = {
      character = my_character / var:my_char_var / PREV
      scientist = {
        desc = desc_loc_key
        traits = { scientist_trait_token ... }
        skills = { specialization_token = 2 ... }
      }
    }
    ```
  - Description: Adds the scientist role to a character.
  - Notes:
    ```text
    The scientist role format is the same as in the character DB. Except the visible trigger, a scientist role created via effect cannot have triggers.
    Can also be used in character scope.
    ```
  - Version Added: 1.15

- **remove_scientist_role**
  - Parameters: character = <character> / <variable>
  - Example:
    ```text
    remove_scientist_role = {
      character = my_character / var:my_char_var / PREV
    }
    ```
  - Description: Remove the scientist role from a character.
  - Notes: Can also be used in character scope.
  - Version Added: 1.15

- **generate_scientist_character**
  - Parameters:
    ```text
    portrait = <GFX>
    Optional, random portrait by default.
    portrait_tag_override = <country> / <variable>
    Optional, accepts variable and keyword, only relevant if using random portrait, by default use country in scope.
    gender = <gender>
    Optional, by default random gender.
    skills = { ??? }
    Optional array, same format as in scientist role in character DB, by default all skills are at 1.
    traits = { <trait> }
    Optional array.
    ```
  - Example:
    ```text
    generate_scientist_character = {
      portrait = GFX_portrait
      portrait_tag_override = CHI
      gender = male
      skills = {
        specialization_token = 2
      }
      traits = { trait_token }
    }
    ```
  - Description: Generate a new character with a scientist role and recruit it in the country in scope.
  - Version Added: 1.15

### MIOs

These are the MIO-related effects in the country scope. For effects in military industrial organisation scope, see [§ MIO scope](#mio-scope).

- **show_mio_tooltip**
  - Parameters:
    ```text
    <MIO>
    MIO to display.
    ```
  - Example:
    ```text
    show_mio_tooltip = my_mio
    ```
  - Description: Displays a tooltip that shows the name of the MIO and its initial trait (if present).
  - Notes: Doesn't change the availability of the MIO directly.
  - Version Added: 1.13

- **unlock_military_industrial_organization_tooltip**
  - Parameters:
    ```text
    <mio> / <variable>
    MIO to unlock.
    ```
  - Example:
    ```text
    unlock_military_industrial_organization_tooltip = mio:my_mio_token
    ```
  - Example:
    ```text
    unlock_military_industrial_organization_tooltip = var:my_mio_var
    ```
  - Description: Display a tooltip saying the MIO is made available (aka unlocked).
  - Version Added: 1.13

- **unlock_mio_policy_tooltip**
  - Parameters:
    ```text
    <policy>
    Policy to display.
    OR
    policy = <policy>
    Policy to display.
    show_modifiers = <bool>
    Whether the trait's modifiers should be shown in the tooltip. Defaults to true.
    ```
  - Example:
    ```text
    unlock_mio_policy_tooltip = my_policy_1
    ```
  - Example:
    ```text
    unlock_mio_policy_tooltip = {
        policy = my_policy_2
        show_modifiers = no
    }
    ```
  - Description: Displays a tooltip that says that the policy is made available.
  - Notes: Doesn't change the availability of the policy directly.
  - Version Added: 1.13

- **add_mio_policy_cost**
  - Parameters:
    ```text
    policy = <policy>
    Policy to modify.
    value = <int>
    Amount in political power to add.
    ```
  - Example:
    ```text
    add_mio_policy_cost = {
        policy = my_policy
        value = 10
    }
    ```
  - Description: Modifies the base cost of a MIO policy.
  - Notes: The base amount is capped at 0 from below.
  - Version Added: 1.13

- **set_mio_policy_cost**
  - Parameters:
    ```text
    policy = <policy>
    Policy to modify.
    value = <int>
    Amount in political power to set.
    ```
  - Example:
    ```text
    set_mio_policy_cost = {
        policy = my_policy
        value = 100
    }
    ```
  - Description: Modifies the base cost of a MIO policy.
  - Notes: Cannot be negative.
  - Version Added: 1.13

- **add_mio_policy_cooldown**
  - Parameters:
    ```text
    policy = <policy>
    Policy to modify.
    value = <int>
    Amount in days to add.
    ```
  - Example:
    ```text
    add_mio_policy_cooldown = {
        policy = my_policy
        value = 10
    }
    ```
  - Description: Modifies the base length of a MIO policy cooldown.
  - Notes: The base amount is capped at 0 from below.
  - Version Added: 1.13

- **set_mio_policy_cooldown**
  - Parameters:
    ```text
    policy = <policy>
    Policy to modify.
    value = <int>
    Amount in days to set.
    ```
  - Example:
    ```text
    set_mio_policy_cooldown  = {
        policy = my_policy
        value = 100
    }
    ```
  - Description: Modifies the base length of a MIO policy cooldown.
  - Notes: Cannot be negative.
  - Version Added: 1.13

### Special Projects

These are special project related effects in the country scope.

- **complete_special_project**
  - Parameters:
    ```text
    sp:<project>
    Project to complete.
    OR
    project = sp:<project>
    Project to complete.
    scientist = <character>
    Optional, default to current scientists on the project.
    state = <string>
    Optional, default to current state of the project.
    iteration_output = { <list> }
    Optional, can be a single reward or reward = option.
    show_modifiers = <bool>
    Optional, default = yes.
    ```
  - Example:
    ```text
    complete_special_project = sp:sp_naval_midget_submarine
    ```
  - Example:
    ```text
    complete_special_project = {
      project = sp:sp_naval_midget_submarine
      scientist = ITA_curio_bernardis
      state = my_state
      iteration_output = {
        my_reward
        my_other_reward
        my_third_reward = my_option_1
      }
      show_modifiers = no
    }
    ```
  - Description: Complete a special project for the country in scope. This effect will not take into account the current state of the project tree and will allow you to unlock a project even if the one before is not unlocked. Since the project is not completed within a facility, the facility state and scientist effects are NOT applied.
  - Notes: project, scientist, state accepts variables and keywords.
  - Version Added: 1.15

- **add_breakthrough_points**
  - Parameters:
    ```text
    specialization = <dp_specialization_id>
    The specialization e.g. specialization_land.
    value = <int>
    The amount of specialization breakthrough points to add.
    ```
  - Example:
    ```text
    add_breakthrough_points = {
      specialization = specialization_land
      value = 3
    }
    ```
  - Example:
    ```text
    add_breakthrough_points = {
      specialization = all
      value = 1
    }
    ```
  - Description: Add breakthrough points to one specialization or all for a country scope.
  - Version Added: 1.15

- **add_breakthrough_progress**
  - Parameters:
    ```text
    specialization = <dp_specialization_id>
    The specialization e.g. specialization_land.
    value = <int>
    The amount of specialization breakthrough progress to be added.
    ```
  - Example:
    ```text
    add_breakthrough_progress = {
      specialization = specialization_land
      value = 3
    }
    ```
  - Example:
    ```text
    add_breakthrough_progress = {
      specialization = all
      value = sp_breakthrough_progress.medium
    }
    ```
  - Description: Add breakthrough progress to one specialization or all for a country scope.
  - Notes: The value can either be an absolute value or a script constant.
  - Version Added: 1.15

### Career profile

These are career profile related effects in the country scope.

- **career_profile_step_missiolini**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    career_profile_step_missiolini = yes
    ```
  - Description: Step completed Mussolini missions by one for the career profile.
  - Version Added: ???

### History

These effects can **only be used within history files**, failing when used outside. However, they're considered effects anyway rather than history arguments, as they can be used in if statements.

- **recruit_character**
  - Parameters: <character>
  - Example:
    ```text
    recruit_character = GER_Character_token
    ```
  - Description: Initially assigns the specified character to the current country.
  - Version Added: 1.11

- **generate_character**
  - Parameters:
    ```text
    token_base = <string>
    Mandatory, acts as the character token.
    name = <localisation key>
    The name used for the character. Generates a random name if not set.
    ```
  - Example:
    ```text
    generate_character = {
        token_base = army_chief_defensive_1
        name = funny_name
        advisor = {
            slot = air_chief
            cost = 50
            idea_token = GER_character_token_air_chief
            traits = {
                air_chief_ground_support_2
            }
            allowed = {
                always = yes
            }
        }
    }
    ```
  - Description: Generates a character for current country.
  - Notes:
    ```text
    If used to create an advisor, the idea token of the advisor role will be the
    token_base
    and
    idea_token
    (defaulting to the slot if the idea token is not set) concatenated, with an underscore as a separator. In the provided example, the idea token will be
    army_chief_defensive_1_GER_character_token_air_chief
    ; if
    idea_token
    wasn't present, it'd be
    army_chief_defensive_1_air_chief
    .
    ```
  - Version Added: 1.11

- **set_oob**
  - Parameters:
    ```text
    <order of battle>
    The name of the file used for the order of battle without the
    .txt
    extension.
    ```
  - Example:
    ```text
    set_oob = BHR_1936
    ```
  - Description: Sets the order of battle to be used for the current country's divisions, overriding every other non-naval and non-air order of battle.
  - Notes:
    ```text
    Orders of battle are defined in
    /Hearts of Iron IV/history/units/*.txt
    files.
    ```
  - Version Added: 1.0

- **set_naval_oob**
  - Parameters:
    ```text
    <order of battle>
    The name of the file used for the order of battle without the
    .txt
    extension.
    ```
  - Example:
    ```text
    set_naval_oob = BHR_1936_naval_legacy
    ```
  - Description: Sets the order of battle to be used for the current country's divisions, overriding every other naval order of battle.
  - Notes:
    ```text
    Orders of battle are defined in
    /Hearts of Iron IV/history/units/*.txt
    files.
    ```
  - Version Added: 1.0

- **set_air_oob**
  - Parameters:
    ```text
    <order of battle>
    The name of the file used for the order of battle without the
    .txt
    extension.
    ```
  - Example:
    ```text
    set_air_oob = ITA_1936_air_bba
    ```
  - Description: Sets the order of battle to be used for the current country's divisions, overriding every other air order of battle.
  - Notes:
    ```text
    Orders of battle are defined in
    /Hearts of Iron IV/history/units/*.txt
    files.
    ```
  - Version Added: 1.12

- **set_keyed_oob**
  - Parameters:
    ```text
    key = <string>
    The key used for the file.
    name = <order of battle>
    The name of the file used for the order of battle without the
    .txt
    extension.
    ```
  - Example:
    ```text
    set_keyed_oob = {
        key = naval
        name = BHR_1936_mtg
    }
    ```
  - Description: Sets the order of battle to be used for the current country's divisions, overriding every other keyed order of battle that uses the same key.
  - Notes:
    ```text
    Orders of battle are defined in
    /Hearts of Iron IV/history/units/*.txt
    files.
    ```
  - Version Added: 1.0

### Variable

These are variable related effects in the country scope.

- **get_highest_scored_country_temp**
  - Parameters:
    ```text
    scorer = <???>
    Id that is used in country scorer.
    var
    Variable name that the result will be stored. (default is highest_scored_country)
    ```
  - Example:
    ```text
    get_highest_scored_country_temp = {
      scorer = scorer_id
      var = var_name
    }
    ```
  - Description: Calculates the highest scored country that is defined in a country scorer and sets it to a variable.
  - Version Added: ???

- **get_sorted_scored_countries_temp**
  - Parameters:
    ```text
    scorer = <???>
    Id that is used in country scorer.
    array = <string>
    A name to store sorted countries as a temp array (default to sorted_country_list)
    scores = <string>
    Corresponding score temp array for countries stored in array (default to country_list_scores)
    ```
  - Example:
    ```text
    get_sorted_scored_countries_temp = {
      scorer = scorer_id
      array = array_name
      scores = array_name
    }
    ```
  - Description: Calculates & sorts all countries in a country scorer and stores them and their scores in temp arrays.
  - Version Added: ???

- **get_supply_vehicles**
  - Parameters:
    ```text
    var = <string>
    Variable name to set.
    type = <type>
    Can be truck or train.
    need = <bool>
    Default no. If yes, gets the number of needed vehicles.
    ```
  - Example:
    ```text
    get_supply_vehicles = {
      var = trucks_needed
      type = truck
      need = yes
    }
    ```
  - Description: Sets a variable to the number of supply vehicles in stockpile or that are needed.
  - Version Added: ???

- **get_supply_vehicles_temp**
  - Parameters:
    ```text
    var = <string>
    Variable name to set.
    type = <type>
    Can be truck or train.
    need = <bool>
    Default no. If yes, gets the number of needed vehicles.
    ```
  - Example:
    ```text
    get_supply_vehicles_temp = {
      var = trucks_needed
      type = truck
      need = yes
    }
    ```
  - Description: Sets a temp variable to the number of supply vehicles in stockpile or that are needed.
  - Version Added: ???

## State scope

The effects here must be used within a **state** scope.

### General

- **state_event**
  - Parameters:
    ```text
    id = <event>
    The event to fire.
    days = <int> / <variable>
    Fires the event in the specified number of days. Optional.
    hours = <int> / <variable>
    Fires the event in the specified number of hours. Optional.
    random = <int> / <variable>
    Adds a random number (between
    0
    and
    random
    , inclusive) of
    hours
    to the scheduled fire time. Optional.
    random_days = <int> / <variable>
    Adds a random number (between
    0
    and
    random_days
    , inclusive) of days to the scheduled fire time. Optional.
    ```
  - Example:
    ```text
    state_event = {
        id = my_event.1
        days = 10
        random = 50
        random_days = 10
        trigger_for = controller
    }
    ```
  - Description: Fires the specified event for the current state.
  - Notes:
    ```text
    Where triggers do not need to be repeatedly checked
    random
    can be a performance light alternative to
    mean_time_to_happen
    for scheduling events.
    Using days = <event> / <variable> or hours may still be bugged and will not fire the event.
    ```
  - Version Added: 1.0

- **set_state_flag**
  - Parameters:
    ```text
    <flag>
    An unique string to identify the state flag with.
    OR
    flag = <flag>
    The flag to set.
    days = <int>
    Sets the flag to last for the specified amount of days. Optional.
    value = <int>
    The new value of the flag on the scale from -2 147 483 648 to 2 147 483 647.
    ```
  - Example:
    ```text
    set_state_flag = my_flag
    ```
  - Example:
    ```text
    set_state_flag = {
        flag = my_flag
        days = 123
        value = 1
    }
    ```
  - Description: Defines a state flag.
  - Notes:
    ```text
    No tooltip is shown.
    The flag in this effect is used in the meaning of 'boolean flag', used to store information.
    ```
  - Version Added: 1.0

- **clr_state_flag**
  - Parameters:
    ```text
    <flag>
    The unique string of a state flag to clear.
    ```
  - Example:
    ```text
    clr_state_flag = my_flag
    ```
  - Description: Clears a defined state flag.
  - Notes: No tooltip is shown.
  - Version Added: 1.0

- **modify_state_flag**
  - Parameters:
    ```text
    flag = <flag>
    The flag to modify.
    value = <value>
    The value to add to the flag. Defaults to 0.
    days = <int>
    The amount of days that the flag should last for before being cleared. Optional, defaults to permanent.
    ```
  - Example:
    ```text
    modify_state_flag = {
        flag = my_flag
        value = 3
    }
    ```
  - Description: Adds an integer value to a flag.
  - Notes: The flag must be already set.
  - Version Added: 1.3

- **set_state_name**
  - Parameters:
    ```text
    <string>
    Defines the new name.
    ```
  - Example:
    ```text
    set_state_name = "Funland"
    ```
  - Description: Changes the current state's name to the specified name.
  - Version Added: 1.3

- **reset_state_name**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    reset_state_name = yes
    ```
  - Description: Resets any changes to the current state's name.
  - Version Added: 1.3

- **add_claim_by**
  - Parameters:
    ```text
    <country> / <variable>
    The country to add the claim for.
    ```
  - Example:
    ```text
    add_claim_by = SOV
    ```
  - Description: Adds a claim for the specified country on the current scope.
  - Version Added: 1.0

- **remove_claim_by**
  - Parameters:
    ```text
    <country> / <variable>
    The country to remove the claim for.
    ```
  - Example:
    ```text
    remove_claim_by = SOV
    ```
  - Description: Removes a claim by the specified country on the current scope.
  - Version Added: 1.0

- **add_core_of**
  - Parameters:
    ```text
    <country> / <variable>
    The country to add the core for.
    ```
  - Example:
    ```text
    add_core_of = SOV
    ```
  - Description: Adds a core for the specified country on the current scope.
  - Version Added: 1.0

- **remove_core_of**
  - Parameters:
    ```text
    <country> / <variable>
    The country to remove the core for.
    ```
  - Example:
    ```text
    remove_core_of = SOV
    ```
  - Description: Removes a core for the specified country on the current scope.
  - Version Added: 1.0

- **set_demilitarized_zone**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    set_demilitarized_zone = yes
    ```
  - Description: Makes the current scope a demilitarized zone.
  - Version Added: 1.0

- **set_state_category**
  - Parameters:
    ```text
    <category>
    The category to change to.
    ```
  - Example:
    ```text
    set_state_category = rural
    ```
  - Description: Changes the current state category to the specified category.
  - Notes:
    ```text
    Categories are found in
    /Hearts of Iron IV/common/state_category/*.txt
    ```
  - Version Added: 1.3

- **add_state_modifier**
  - Parameters:
    ```text
    Modifier scope
    <modifier> = <float>
    Adds a modifier to the state.
    ```
  - Example:
    ```text
    add_state_modifier = {
        modifier = {
            local_resources = 2.0
        }
    }
    ```
  - Description:
    ```text
    Adds a
    modifier
    to the current state.
    ```
  - Version Added: 1.3

- **add_manpower**
  - Parameters:
    ```text
    <int> / <variable>
    The amount to add.
    ```
  - Example:
    ```text
    add_manpower = 10000
    ```
  - Description: Adds the specified amount of total population to the current state.
  - Notes: Note that when using negative manpower it will, besides reducing the population, also add directly to the recruitable manpower of the state. Which will increase your manpower
  - Version Added: 1.0

- **add_resource**
  - Parameters:
    ```text
    type = <resource>
    The resource to add.
    amount = <int> / <variable>
    The amount to add.
    ```
  - Example:
    ```text
    add_resource = {
        type = oil
        amount = 100
    }
    ```
  - Description: Adds the specified resource in the specified amount to the current state.
  - Notes: Can also be used in country scope.
  - Version Added: 1.0

- **set_border_war**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    set_border_war = yes
    ```
  - Description: Enables Border War status for the current state.
  - Notes:
    ```text
    Used for the state-based border wars, represented with orange stripes, see
    § Border wars
    for the border wars that simulate combat on a border between two countries. On the end of the border war,
    the on_border_war_lost on action
    is fired for the state that where the border war was lost.
    ```
  - Version Added: 1.0

- **create_unit**
  - Parameters:
    ```text
    division = <division string>
    The division string.
    owner = <country>
    The owner of the division.
    prioritize_location = <province>
    If possible, this province within the state gets used. Optional.
    allow_spawning_on_enemy_provs = yes
    Allows the units to be created on provinces owned by the division owner's enemy. Defaults to false.
    count = <int>
    The amount of units to create. Defaults to 1.
    id = <int>
    The ID to identify the unit. Only used in
    delete_unit
    .
    country_score = { ... }
    A
    MTTH
    block deciding the province in the state where the division should spawn, evaluates in the scope of the controller. Defaults to prioritising owner's controlled provinces first and then owner's allies.
    divisional_commander_xp = <int>
    give the division commander experience on unit creation
    The following arguments go within
    division = ""
    :
    name = \"<string>\"
    The name of the division.
    division_template = \"<string>\"
    The template to be used by the division.
    start_experience_factor = <double>
    Experience of the division, with 0 being none and 1 being full training. Defaults to 1.
    start_equipment_factor = <double>
    Equipment stockpile of the division. Defaults to 1.
    start_manpower_factor = <double>
    Manpower stockpile of the division. Defaults to 1.
    force_equipment_variants = { <equipment type> = { owner = \"<country>\" amount = <int> version_name = \"<string>\" } }
    Forces a certain type of equipment to be used. Multiple equipment types can be added by adding multiple <equipment type> = {} lines.
    ```
  - Example:
    ```text
    create_unit = {
        division = "name = \"Infantry Division\" division_template = \"Infantry Division\" start_experience_factor = 0.5"
        owner = GER
    }
    ```
  - Example:
    ```text
    create_unit = {
        division = "name = \"Artie\" division_template = \"Artillery Division\" start_manpower_factor = 0.3"
        owner = BHR
        count = 3
        allow_spawning_on_enemy_provs = yes
        country_score = {
            base = 3
            modifier = {
                factor = 2
                tag = OMA
            }
        }
        id = 123
    }
    ```
  - Example:
    ```text
    create_unit = { 
      division = "name = \"Tank division\" division_template = \"Tank Division\" start_manpower_factor = 1 force_equipment_variants = { medium_tank_chassis_2 = { owner = \"USA\" amount = 100 version_name = \"M4 Sherman\" }}" 
      owner = USA 
      count = 1
    }
    ```
  - Description: Adds the specified division to the current state.
  - Notes:
    ```text
    The division string
    must be on one line
    . A linebreak in the middle of
    division = "..."
    will break the effect and result in no units being spawned.
    Can only be used within a state scope
    , such as
    capital_scope
    . The effect will do nothing when put into a country's scope.
    Equipment factor cannot be set to zero.
    If set to zero, it will be treated as a 1. Created equipment will be the latest available to the country.
    ```
  - Version Added: 1.3

- **teleport_armies**
  - Parameters:
    ```text
    limit = { <triggers> }
    The condition that must be true for the owner of the armies for them to teleport.
    to_state_array = <array>
    The state array the armies will get teleported to.
    to_province = <ID>
    The province the armies will get teleported to.
    to_state = <ID>
    The state the armies will get teleported to.
    ```
  - Example:
    ```text
    teleport_armies = {
        limit = {
            has_war_together_with = ROOT
        }
        to_state_array = owned_controlled_states
    }
    ```
  - Description: Teleports all armies in the specified state if the owner of the armies meets the condition.
  - Notes: Only define one of to_state_array, to_state, or to_province. If none is specified, it defaults to the capital.
  - Version Added: 1.9

- **add_province_modifier**
  - Parameters:
    ```text
    static_modifiers = { <modifiers> }
    The list of modifiers.
    province = <id>
    The province to apply the modifiers to.
    provinces = {}
    Scope for selecting multiple provinces. The following arguments have to go inside it:
    id = <id>
    The ID of the province. Multiple can be specified.
    all_provinces = yes
    Selects all provinces to which the limitations apply. The following arguments require it:
    limit_to_coastal = yes
    Limits the selection of provinces to only coastal ones.
    limit_to_border = yes
    Limits the selection of provinces to only ones bordering a different country.
    limit_to_naval_base = yes
    Limits the selection of provinces to only ones that have a naval base.
    limit_to_victory_point = yes
    Limits the selection of provinces to only ones that have a victory point, or a city, in them.
    days = <int>
    Will be temporary if specified, can be variable
    ```
  - Example:
    ```text
    add_province_modifier = {
    	static_modifiers = { mod_modifier_1 mod_modifier_2 }
    	province = 1234
    }
    ```
  - Example:
    ```text
    add_province_modifier = {
    
    	static_modifiers = { mod_modifier_1 mod_modifier_2 }
    	province = {
    		id = 1234
    		id = 4321
    
    
    
           days = 7
    
    
    
    	}
    
    
    }
    ```
  - Example:
    ```text
    add_province_modifier = {
    
    	static_modifiers = { mod_modifier_1 mod_modifier_2 }
    	province = {
    		all_provinces = yes
    		limit_to_coastal = yes
    		limit_to_border = yes
    		limit_to_naval_base = yes
    		limit_to_victory_point = yes
    	}
    
    
    }
    ```
  - Description: Adds a province modifier to the specified provinces in this state.
  - Notes:
    ```text
    Province modifiers are defined in
    /Hearts of Iron IV/common/modifiers/*.txt
    ```
  - Version Added: 1.6

- **remove_province_modifier**
  - Parameters:
    ```text
    static_modifiers = { <modifiers> }
    The list of modifiers.
    province = <id>
    The province to apply the modifiers to.
    provinces = {}
    Scope for selecting multiple provinces. The following arguments have to go inside it:
    id = <id>
    The ID of the province. Multiple can be specified.
    all_provinces = yes
    Selects all provinces to which the limitations apply. The following arguments require it:
    limit_to_coastal = yes
    Limits the selection of provinces to only coastal ones.
    limit_to_border = yes
    Limits the selection of provinces to only ones bordering a different country.
    limit_to_naval_base = yes
    Limits the selection of provinces to only ones that have a naval base.
    limit_to_victory_point = yes
    Limits the selection of provinces to only ones that have a victory point, or a city, in them.
    ```
  - Example:
    ```text
    remove_province_modifier = {
    	static_modifiers = { mod_modifier_1 mod_modifier_2 }
    	province = 1234
    }
    ```
  - Example:
    ```text
    remove_province_modifier = {
    
    	static_modifiers = { mod_modifier_1 mod_modifier_2 }
    	province = {
    		id = 1234
    		id = 4321
    	}
    
    
    }
    ```
  - Example:
    ```text
    remove_province_modifier = {
    
    	static_modifiers = { mod_modifier_1 mod_modifier_2 }
    	province = {
    		all_provinces = yes
    		limit_to_coastal = yes
    		limit_to_border = yes
    		limit_to_naval_base = yes
    		limit_to_victory_point = yes
    	}
    
    
    }
    ```
  - Description: Removes a province modifier to the specified provinces in this state.
  - Notes:
    ```text
    Province modifiers are defined in
    /Hearts of Iron IV/common/modifiers/*.txt
    ```
  - Version Added: 1.6

- **add_victory_points**
  - Parameters: Add victory points to a province
  - Example:
    ```text
    add_victory_points = {
    	province = 1234
    	value = 10
    }
    ```
  - Description: Adds victory points to a province.
  - Notes: Accepts negative values
  - Version Added: 1.10

- **set_victory_points**
  - Parameters: Set the victory points of a province
  - Example:
    ```text
    set_victory_points = {
    	province = 1234
    	value = 10
    }
    ```
  - Description: Sets the number of victory point in a province.
  - Notes: Accepts negative values
  - Version Added: 1.10

- **set_state_province_controller**
  - Parameters:
    ```text
    controller = <tag>
    The new controller of the province.
    limit = { <triggers> }
    The triggers that must be fulfilled by the province's current controller to be transferred to the new controller.
    ```
  - Example:
    ```text
    set_state_province_controller = {
        controller = POL
        limit = {
            OR = {
                tag = GER
                is_in_faction_with = GER
            }
        }
    }
    ```
  - Description: Changes the controller of all provinces within that state controlled by countries that meet triggers to the specified country.
  - Version Added: 1.9

- **transfer_state_to**
  - Parameters:
    ```text
    <country>
    Country to transfer the state to.
    ```
  - Example:
    ```text
    transfer_state_to = JAM
    ```
  - Description: Sets owner and controller of the state to the given country
  - Version Added: 1.11

- **set_state_owner_to**
  - Parameters:
    ```text
    <country>
    Country to set the owner
    (but not the controller)
    of the state to.
    ```
  - Example:
    ```text
    set_state_owner_to = JAM
    ```
  - Description: Sets the owner of the state to the given country
  - Notes:
    ```text
    Use
    transfer_state_to
    unless the control specifically shouldn't be given.
    ```
  - Version Added: 1.11

- **set_state_controller_to**
  - Parameters:
    ```text
    <country>
    Country to set the controller
    (but not the owner)
    of the state to.
    ```
  - Example:
    ```text
    set_state_controller_to = ITA
    ```
  - Description: Sets the controller of the state to the given country
  - Version Added: 1.11

- **add_contested_owner**
  - Parameters:
    ```text
    <country> / <variable>
    Country to add contest to state.
    ```
  - Example:
    ```text
    add_contested_owner = GER
    ```
  - Description: Adds a contested owner to a state. The effect can be used either from a country or a state scope and accepts the other as parameter.
  - Notes: Can also be used in country scope.
  - Version Added: 1.15

- **remove_contested_owner**
  - Parameters:
    ```text
    <country> / <variable>
    Country to remove contest to state.
    ```
  - Example:
    ```text
    remove_contested_owner = GER
    ```
  - Description: Removes a contested owner to a state. The effect can be used either from a country or a state scope and accepts the other as parameter.
  - Notes: Can also be used in country scope.
  - Version Added: 1.15

- **strategic_province_location**
  - Parameters: <string> = <int>
  - Example:
    ```text
    strategic_province_location = {
        defensible_coastline = 10124
    }
    ```
  - Description: Add a strategic location to a province using state scope. The available strategic locations are defined in strategic_locations and are specified with a province id.
  - Notes: Can contain multiple strategic locations.
  - Version Added: 1.17

- **strategic_state_location**
  - Parameters: <string> = <int>
  - Example:
    ```text
    strategic_state_location = {
        favorable_approach = 11932
    }
    ```
  - Description: Add strategic locations to a state in scope. The available strategic locations are defined in strategic_locations.
  - Notes: Can contain multiple strategic locations.
  - Version Added: 1.17

### Buildings

- **add_extra_state_shared_building_slots**
  - Parameters:
    ```text
    <int> / <variable>
    The amount of slots to add or remove.
    ```
  - Example:
    ```text
    add_extra_state_shared_building_slots = 2
    ```
  - Description: Changes the number of shared building slots for the current state.
  - Notes:
    ```text
    Shared buildings slots being the ones used for multiple building types, such as military or civilian factories. This is in contrast to non-shared slots, such as those used by radio stations or air bases, which only can be changed globally with technologies.
    Note:
    When using a variable and a
    saved event target
    , must be used as "saved_event.var_name" because "event_target:saved_event.var_name" will not work.
    ```
  - Version Added: 1.0

- **add_building_construction**
  - Parameters:
    ```text
    type = <string>
    The building to add.
    level = <int> / <variable>
    The level to set the building to.
    instant_build = <bool>
    Defines whether the buildings are instantly built.
    province = <id>
    Defines the exact province to add provincal buildings in. Can be used as a scope.
    Province scope
    all_provinces = <bool>
    Affect all provinces within the state that meet each limit. Used in the province scope.
    id = <id>
    Affect the specified province ID. Used in the province scope, will apply for each province if inserted multiple times.
    limit_to_coastal = <bool>
    Affect only coastal provinces within the selection. Used in the province scope.
    limit_to_naval_base = <bool>
    Affect only provinces that have naval bases built. Used in the province scope.
    limit_to_border = <bool>
    Affect only provinces that lie on a border between countries. Used in the province scope.
    limit_to_border_country = <country>
    Affect only provinces that border a specific other country. Used in the province scope.
    limit_to_victory_point = <int>/<bool>
    Affect only provinces that meet the victory point amount prerequisite. If
    yes
    is used in place of a number, any amount of victory points works. Used in the province scope.
    limit_to_supply_node = <bool>
    Affect only provinces that have a supply node. Used in the province scope.
    level = <int>
    Affect only provinces with buildings level below, at or above the specified level. Used in the province scope.
    ```
  - Example:
    ```text
    add_building_construction = {
        type = arms_factory
        level = 5
        instant_build = yes
    }
    ```
  - Example:
    ```text
    add_building_construction = {
        type = bunker
        level = 10
        instant_build = yes
        province = {
            all_provinces = yes
            limit_to_border = yes
            limit_to_victory_point > 1
        }
    }
    ```
  - Example:
    ```text
    add_building_construction = {
        type = bunker
        level = 1
        instant_build = yes
        province = 2999
    }
    ```
  - Description: Starts construction in the current state for the specified building.
  - Notes:
    ```text
    For provincial buildings,
    must be done within the scope of the state that contains the province
    even if done on a specific province.
    If the controller country doesn't have an
    order of battle assigned within the history file
    , the buildings will not show up within the production menu
    until a recalculation of buildings, such as by changing consumer goods or reloading a savefile.
    Can only be used within a state scope
    , such as
    random_owned_controlled_state
    . The effect will do nothing when put into a country's scope.
    For the list of building IDs present in the base game, see
    Building modding#Types
    .
    ```
  - Version Added: 1.0

- **set_building_level**
  - Parameters:
    ```text
    type = <string>
    The building to add.
    level = <int> / <variable>
    The level to set the building to.
    instant_build = <bool>
    Defines whether the buildings are instantly built.
    province = <id>
    Defines the exact province to add provincal buildings in. Can be used as a scope.
    Province scope
    all_provinces = <bool>
    Affect all provinces within the state that meet each limit. Used in the province scope.
    id = <id>
    Affect the specified province ID. Used in the province scope, will apply for each province if inserted multiple times.
    limit_to_coastal = <bool>
    Affect only coastal provinces within the selection. Used in the province scope.
    limit_to_naval_base = <bool>
    Affect only provinces that have naval bases built. Used in the province scope.
    limit_to_border = <bool>
    Affect only provinces that lie on a border between countries. Used in the province scope.
    limit_to_border_country = <country>
    Affect only provinces that border a specific other country. Used in the province scope.
    limit_to_victory_point = <int>/<bool>
    Affect only provinces that meet the victory point amount prerequisite. If
    yes
    is used in place of a number, any amount of victory points works. Used in the province scope.
    limit_to_supply_node = <bool>
    Affect only provinces that have a supply node. Used in the province scope.
    level = <int>
    Affect only provinces with buildings level below, at or above the specified level. Used in the province scope.
    ```
  - Example:
    ```text
    set_building_level = {
        type = infrastructure
        level = 10
        instant_build = yes
    }
    ```
  - Example:
    ```text
    set_building_level = {
        type = bunker
        level = 3
        province = {
            all_provinces = yes
            limit_to_border = yes
            level < 3
        }
    }
    ```
  - Description: Sets the specified building to the current state (or provinces within the state).
  - Notes:
    ```text
    The province scope is used for provincal level buildings.  You can limit the construction to victory points using :
    limit_to_victory_point > 5
    (only build province buildings on province with VP over 5 )
    limit_to_victory_point = yes
    (only build province buildings on province with VP) For provincial buildings,
    must be done within the scope of the state that contains the province
    even if done on a specific province.
    ```
  - Version Added: 1.4

- **damage_building**
  - Parameters:
    ```text
    type = <building>
    The building to damage.
    tags = <building_tag>
    The buildings with this tag to damage.
    tags = { <building_tag> }
    The buildings with these tags to damage.
    repair_speed_modifier = <float>
    Repair will be x% slower until building is fully repaired
    damage = <float>
    The amount of damage to inflict.
    province = <id> / <variable>
    The province to target for provincal buildings.
    ```
  - Example:
    ```text
    damage_building = {
      type = infrastructure
      damage = 1
    }
    ```
  - Example:
    ```text
    damage_building = {
      tags = dam_building
      damage = 1
      repair_speed_modifier = -0.8
      province = 3488
    }
    ```
  - Description: Damages a building in a targeted state or province.
  - Notes:
    ```text
    The health of buildings is determined by the
    value
    attribute in a building's definition. This is multiplied by their level to get their total health.
    Can also be used in country scope.
    ```
  - Version Added: 1.3

- **remove_building**
  - Parameters:
    ```text
    type = <building>
    The building to remove.
    tag = <building_tag>
    The buildings with this tag to remove.
    tag = { <building_tag> }
    The buildings with these tags to remove.
    level = <int> / <variable>
    The levels to remove.
    ```
  - Example:
    ```text
    remove_building = {
        type = arms_factory
        level = 5
    }
    ```
  - Example:
    ```text
    remove_building = {
        tag = facility
        level = 1
    }
    ```
  - Description: Removes the specified building in the current state. For shared buildings level determines the amount, whereas for the others it is the actual level.
  - Version Added: 1.0

- **construct_building_in_random_province**
  - Parameters:
    ```text
    <building> = <int>
    Building to build.
    ```
  - Example:
    ```text
    65 = {
        construct_building_in_random_province = {
            land_facility = 1
        }
    }
    ```
  - Description: Set building level in a random province of state scope.
  - Version Added: 1.15

### Resistance and compliance

- **add_compliance**
  - Parameters:
    ```text
    <int> / <variable>
    The amount to add.
    ```
  - Example:
    ```text
    add_compliance = 30
    ```
  - Description: Adds compliance to the specified state.
  - Version Added: 1.9

- **add_resistance**
  - Parameters:
    ```text
    <int> / <variable>
    The amount to add.
    ```
  - Example:
    ```text
    add_resistance = 30
    ```
  - Description: Adds resistance to the specified state.
  - Version Added: 1.9

- **add_resistance_target**
  - Parameters:
    ```text
    <int> / <variable>
    The amount to add.
    ```
  - Example:
    ```text
    add_resistance_target = 30
    ```
  - Description: Increases resistance target in the specified state.
  - Version Added: 1.9

- **add_resistance_target**
  - Parameters:
    ```text
    id = <int>
    The ID of the target increase.
    amount = <int>/<variable>
    The amount to increase the resistance target by.
    occupied = <country>
    Will only apply the increase if the the occupied country is the specified scope.
    occupier = <country>
    Will only apply the increase if the the occupier is the specified scope.
    days = <int>/<variable>
    If set, the resistance target will only be increased for the specified amount of days.
    tooltip = <string>
    The tooltip to show in the resistance target tooltip.
    ```
  - Example:
    ```text
    add_resistance_target = {
        id = 123
        amount = 30
        occupied = ENG
        occupier = GER
        days = 365
        tooltip = my_localisation_key
    }
    ```
  - Description: Increases resistance target in the specified state.
  - Version Added: 1.9

- **cancel_resistance**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    cancel_resistance = yes
    ```
  - Description: Cancels resistance activity for the current state.
  - Version Added: 1.9

- **force_disable_resistance**
  - Parameters:
    ```text
    <country>
    The target country.
    ```
  - Example:
    ```text
    force_disable_resistance = GER
    ```
  - Description: Disables resistance for the scoped state when the occupier is the specified country.
  - Version Added: 1.9

- **force_disable_resistance**
  - Parameters:
    ```text
    clear = <bool>
    If set to yes, will clear resistance.
    occupier = <country>
    Resistance will be disabled if the occupier is the specified scope.
    occupied = <country>
    Resistance will be disabled if the occupied country is the specified scope.
    ```
  - Example:
    ```text
    force_disable_resistance = {
        clear = yes
        occupier = GER
        occupied = ENG
    }
    ```
  - Description: Disables resistance for the scoped state when the occupier is the specified country.
  - Version Added: 1.9

- **force_enable_resistance**
  - Parameters:
    ```text
    <country>
    The target country.
    ```
  - Example:
    ```text
    force_enable_resistance = GER
    ```
  - Description: Enables resistance for the scoped state when the occupier is the specified country.
  - Notes:
    ```text
    Does not start resistance by itself, only removes the checks forcefully disabling it. Use with
    start_resistance
    in order to immediately start resistance.
    ```
  - Version Added: 1.9

- **force_enable_resistance**
  - Parameters:
    ```text
    clear = <bool>
    If set to yes, will clear resistance.
    occupier = <country>
    Resistance will be enabled if the occupier is the specified scope.
    occupied = <country>
    Resistance will be enabled if the occupied country is the specified scope.
    ```
  - Example:
    ```text
    force_enable_resistance = {
        clear = yes
        occupier = GER
        occupied = ENG
    }
    ```
  - Description: Enables resistance for the scoped state when the occupier is the specified country.
  - Notes:
    ```text
    Does not start resistance by itself, only removes the checks forcefully disabling it. Use with
    start_resistance
    in order to immediately start resistance.
    ```
  - Version Added: 1.9

- **remove_resistance_target**
  - Parameters:
    ```text
    <int> / <variable>
    The id of the resistance target to remove. (Must be set with add_resistance_target)
    ```
  - Example:
    ```text
    remove_resistance_target = 30
    ```
  - Description: Removes a set resistance target increase in the specified state.
  - Notes: Has no tooltip.
  - Version Added: 1.9

- **set_compliance**
  - Parameters:
    ```text
    <int> / <variable>
    The amount to set the compliance to.
    ```
  - Example:
    ```text
    set_compliance = 30
    ```
  - Description: Sets compliance in the specified state.
  - Version Added: 1.9

- **set_resistance**
  - Parameters:
    ```text
    <int> / <variable>
    The amount to set the resistance to.
    ```
  - Example:
    ```text
    set_resistance = 30
    ```
  - Description: Sets resistance in the specified state.
  - Notes:
    ```text
    The resistance should be enabled in the state, either via
    start_resistance
    or through the in-game process. Occassionally it may take a tick for resistance to start after the controllership change, so it's preferable to do so on states that are given to the country immediately before this gets executed, such as if this is executed in country history.
    ```
  - Version Added: 1.9

- **start_resistance**
  - Parameters:
    ```text
    <bool>/<country>
    Whether to start resistance or not. If using a country as the parameter, the state will only start resistance if occupied by the target country.
    ```
  - Example:
    ```text
    start_resistance = POL
    ```
  - Example:
    ```text
    start_resistance = yes
    ```
  - Description: Starts resistance in the specified state.
  - Notes:
    ```text
    If used on a state that normally can't start resistance, use alongside with
    force_enable_resistance
    .
    ```
  - Version Added: 1.9

- **set_garrison_strength**
  - Parameters:
    ```text
    <0-1>
    The new garrison strength.
    ```
  - Example:
    ```text
    set_garrison_strength = 0.5
    ```
  - Description: Sets the strength of the garrison in the specified state.
  - Version Added: 1.9

- **set_occupation_law**
  - Parameters:
    ```text
    <law ID>
    The new occupation law enacted by the previous scope or
    default_law
    .
    ```
  - Examples: # Changes GER's occupation law for every controlled state.
  - Example:
    ```text
    GER = {
      every_controlled_state = {
        set_occupation_law = military_governor_occupation
      }
    }
    ```
  - Description: Sets the occupation law of the state.
  - Notes:
    ```text
    PREV
    will be the country for whom the occupation law will be changed. If PREV is not a country, nothing changes. If PREV doesn't occupy the state, nothing happens until it does. If using
    default_law
    , resets to the law set by the country's occupation.
    Can also be used in country scope.
    ```
  - Version Added: 1.12

### Raids

- **raid_reduce_project_progress_ratio**
  - Parameters:
    ```text
    <float>
    Value to reduce.
    ```
  - Example:
    ```text
    raid_reduce_project_progress_ratio = 0.1
    ```
  - Description: Reduce progress to the special project in state. Root scope is raid instance scope. The input value is a ratio of the total needed progress to complete the special project, i.e. a decimal number between 0 and 1.
  - Version Added: 1.15

## Character scope

The effects here must be used within a **character** scope.

### General

- **set_character_flag**
  - Parameters:
    ```text
    <flag>
    An unique string to identify the character flag with.
    OR
    flag = <flag>
    The flag to set.
    days = <int>
    Sets the flag to last for the specified amount of days. Optional.
    value = <int>
    The new value of the flag on the scale from -2 147 483 648 to 2 147 483 647.
    ```
  - Example:
    ```text
    set_character_flag = my_flag
    ```
  - Example:
    ```text
    set_character_flag = {
        flag = my_flag
        days = 123
        value = 1
    }
    ```
  - Description: Defines a character flag.
  - Notes:
    ```text
    No tooltip is shown.
    The flag in this effect is used in the meaning of 'boolean flag', used to store information.
    ```
  - Version Added: 1.11

- **set_character_name**
  - Parameters:
    ```text
    <localisation key>
    The name to use.
    ```
  - Example:
    ```text
    set_character_name = GER_my_cool_flag
    ```
  - Description: Changes the character's name to the specified localisation key's value.
  - Version Added: 1.11

- **modify_character_flag**
  - Parameters:
    ```text
    flag = <flag>
    The flag to modify.
    value = <value>
    The value to add to the flag. Defaults to 0.
    days = <int>
    The amount of days that the flag should last for before being cleared. Optional, defaults to permanent.
    ```
  - Example:
    ```text
    modify_character_flag = {
        flag = my_flag
        value = 3
    }
    ```
  - Description: Adds an integer value to a flag.
  - Notes: The flag must be already set.
  - Version Added: 1.11

- **clr_character_flag**
  - Example:
    ```text
    clr_character_flag = <bool>
    ```
  - Description: Clears a character flag
  - Version Added: 1.11

- **retire**
  - Parameters:
    ```text
    <bool>
    Boolean>
    ```
  - Example:
    ```text
    retire = yes
    ```
  - Description: Retires the current character (removing them).
  - Version Added: 1.5

- **set_nationality**
  - Parameters:
    ```text
    <country> / <variable>
    The target country.
    ```
  - Example:
    ```text
    set_nationality = GER
    ```
  - Description: Switches the current character to the specified country, giving them the character.
  - Notes:
    ```text
    If you wish to change the nationality of a specific character, and the country getting the effect doesn't have the character recruited already, use the
    command to call them up. Only necessary in 1.11 and beyond.
    ```
  - Example:
    ```text
    every_possible_country = {
        limit = { has_character = ID }
        random_character = {
            limit = { is_character = ID }
            set_nationality = TAG
        }
    }
    ```
  - Version Added: 1.5

- **set_portraits**
  - Parameters:
    ```text
    character = <character>
    The character name. Optional if in character scope.
    Army scope
    :
    small = <sprite>
    The sprite used as an advisor.
    large = <sprite>
    The sprite used as a general.
    Character scope
    :
    large = <sprite>
    The sprite used as a country leader.
    ```
  - Example:
    ```text
    set_portraits = {
        character = my_character
        army = { small ="MySmallCharacterGFX" }
        civilian = { large ="MyLargeCharacterGFX" }
    }
    ```
  - Description: Changes the specified portraits of a character.
  - Notes:
    ```text
    Sprites are defined within
    /Hearts of Iron IV/interface/*.gfx
    files.
    ```
  - Version Added: 1.11

- **add_trait**
  - Parameters:
    ```text
    slot = <slot>
    Slot of the character. Necessary for advisors.
    ideology = <sub-ideology>
    Ideology type of the character. Necessary for country leaders.
    trait = <trait>
    The trait to add.
    ```
  - Example:
    ```text
    add_trait = {
        slot = political_advisor
        trait = really_good_boss
    }
    ```
  - Example:
    ```text
    add_trait = {
        ideology = liberalism
        trait = field_of_gar
    }
    ```
  - Description: Adds the specified country leader trait to the character.
  - Notes: Ideology type refers to a sub-type of an ideology group assigned to characters, commonly referred to as sub-ideologies in community jargon. The character slot can be the character's name or id. Using name is recommended because 1.11 made id obsolete.
  - Version Added: 1.11

- **remove_trait**
  - Parameters:
    ```text
    slot = <slot>
    Slot of the character. Necessary for advisors.
    ideology = <sub-ideology>
    Ideology type of the character. Necessary for country leaders.
    trait = <trait>
    The trait to remove.
    ```
  - Example:
    ```text
    remove_trait = {
        slot = political_advisor
        trait = really_good_boss
    }
    ```
  - Example:
    ```text
    remove_trait = {
        ideology = liberalism
        trait = field_of_gar
    }
    ```
  - Description: Removes the specified trait from the character.
  - Notes: Ideology type refers to a sub-type of an ideology group assigned to characters, commonly referred to as sub-ideologies in community jargon. The character slot can be the character's name or id. Using name is recommended because 1.11 made id obsolete.
  - Version Added: 1.11

- **add_corps_commander_role**
  - Parameters:
    ```text
    <...>
    Army leader role definition
    ```
  - Example:
    ```text
    add_corps_commander_role = {
        skill = 4
        attack_skill = 2
        defense_skill = 3
        planning_skill = 3
        logistics_skill = 5
    }
    ```
  - Description: Sets the specified character to also act as a corps commander.
  - Version Added: 1.11

- **add_field_marshal_role**
  - Parameters:
    ```text
    <...>
    Army leader role definition
    ```
  - Example:
    ```text
    add_field_marshal_role = {
      skill = 4
      attack_skill = 2
      defense_skill = 3
      planning_skill = 3
      logistics_skill = 5
    }
    ```
  - Description: Sets the specified character to also act as a field marshal.
  - Version Added: 1.11

- **add_naval_commander_role**
  - Parameters:
    ```text
    <...>
    Navy leader role definition
    ```
  - Example:
    ```text
    add_naval_commander_role = {
      skill = 4
      attack_skill = 2
      defense_skill = 3
      planning_skill = 3
      logistics_skill = 5
    }
    ```
  - Description: Sets the specified character to also act as an admiral.
  - Version Added: 1.11

- **add_country_leader_role**
  - Parameters:
    ```text
    character = <character>
    The character to modify.
    country_leader = { ... }
    Country leader role definition
    promote_leader = <bool>
    Will promote the leader to be the leader of the assigned party. Optional, defaults to false.
    ```
  - Example:
    ```text
    add_country_leader_role = {
        character = GER_character_token
        promote_leader = yes
        country_leader = {
            ideology = fascism_type
            expire = "1965.1.1.1"
            traits = { war_industrialist }
        }
    }
    ```
  - Description: Sets the specified character to also act as a country leader, promoting to the party leader if specified.
  - Notes: Does nothing if the character already has a country leader role in the ideology group.
  - Version Added: 1.11

- **promote_character**
  - Parameters:
    ```text
    <bool>
    Boolean.
    OR
    <ideology type>
    The ideology type used by the country leader role.
    ```
  - Example:
    ```text
    promote_character = yes
    ```
  - Example:
    ```text
    promote_character = liberalism
    ```
  - Description: Promotes a character to the leader of their political party.
  - Notes: If the character has multiple country leader roles, specifying the ideology type is mandatory. Ideology type refers to a sub-type of an ideology group assigned to characters, commonly referred to as sub-ideologies in community jargon.
  - Version Added: 1.11

- **remove_country_leader_role**
  - Parameters:
    ```text
    ideology = <string>
    The ideology type of the character.
    ```
  - Example:
    ```text
    remove_country_leader_role = {
        ideology = socialism
    }
    ```
  - Description: Removes a country leader role from a character.
  - Notes: Ideology type refers to a sub-type of an ideology group assigned to characters, commonly referred to as sub-ideologies in community jargon.
  - Version Added: 1.11

- **add_advisor_role**
  - Parameters:
    ```text
    advisor = { ... }
    Advisor role definition
    activate = <bool>
    Will activate the advisor (add them directly when the command is run to the countries government). Optional, defaults to false.
    ```
  - Example:
    ```text
    add_advisor_role = {
        activate = yes
        advisor = {
            slot = air_chief
            cost = 50
            idea_token = GER_character_token_air_chief
            traits = {
                air_chief_ground_support_2
            }
        }
    }
    ```
  - Description: Sets the specified character to also act as an advisor, activating if specified.
  - Notes:
    ```text
    Trigger and effect blocks (such as
    allowed
    and
    on_add
    ) cannot be added within advisor definitions created this way.
    ```
  - Version Added: 1.11

- **remove_advisor_role**
  - Parameters:
    ```text
    slot = <int>
    The slot where to remove the advisor slot from.
    ```
  - Example:
    ```text
    remove_advisor_role = {
      slot = political_advisor
    }
    ```
  - Description: Removes the specified advisor role from the character.
  - Version Added: 1.11

- **add_scientist_role**
  - Parameters:
    ```text
    <...>
    Scientist role definition
    ```
  - Example:
    ```text
    add_scientist_role = {
      scientist = {
        desc = desc_loc_key
        traits = { scientist_trait_token ... }
        skills = { specialization_token = 2 ... }
      }
    }
    ```
  - Description: Adds the scientist role to a character.
  - Notes:
    ```text
    The scientist role format is the same as in the character DB. Except the visible trigger, a scientist role created via effect cannot have triggers.
    Can also be used in country scope.
    ```
  - Version Added: 1.15

- **remove_scientist_role**
  - Parameters: <bool>
  - Example:
    ```text
    remove_scientist_role = yes
    ```
  - Description: Remove the scientist role from a character.
  - Notes: Can also be used in country scope.
  - Version Added: 1.15

- **add_scientist_level**
  - Parameters:
    ```text
    level = <int> / <variable>
    Level to add.
    specialization = <specialization>
    Specialization to add.
    ```
  - Example:
    ```text
    add_scientist_level = {
      level = 2
      specialization = specialization_nuclear
    }
    ```
  - Description: Add levels to a special project specialization for a scientist character in scope.
  - Version Added: 1.15

- **injure_scientist_for_days**
  - Parameters:
    ```text
    <int> / <variable>
    Amount of days to apply injure.
    ```
  - Example:
    ```text
    injure_scientist_for_days = 12
    ```
  - Description: Injure a scientist for x amount of days to a scientist character in scope.
  - Version Added: 1.15

- **add_scientist_trait**
  - Parameters:
    ```text
    <trait>
    Trait to add.
    ```
  - Example:
    ```text
    add_scientist_trait = my_trait_token
    ```
  - Description: Add a trait to a scientist character in scope.
  - Version Added: 1.15

- **add_scientist_xp**
  - Parameters:
    ```text
    experience = <int> / <variable>
    Expierience to add.
    specialization = <specialization>
    Specialization to add.
    ```
  - Example:
    ```text
    add_scientist_xp = {
      experience = 2
      specialization = specialization_nuclear
    }
    ```
  - Description: Add experience to a special project specialization for a scientist character in scope.
  - Version Added: 1.15

- **set_can_be_fired_in_advisor_role**
  - Parameters:
    ```text
    slot = <slot>
    The slot of the character to modify.
    value = <bool>
    The value to set.
    ```
  - Example:
    ```text
    set_can_be_fired_in_advisor_role = {
        slot = political_advisor
        value = no
    }
    ```
  - Description:
    ```text
    Changes the
    can_be_fired
    attribute of the advisor, preventing the player from dismissing the advisor.
    ```
  - Version Added: 1.12.8

### Unit leaders

These can only be used with characters of the unit leader type.

- **unit_leader_event**
  - Parameters:
    ```text
    id = <event>
    The event to fire.
    days = <int> / <variable>
    Fires the event in the specified number of days. Optional.
    hours = <int> / <variable>
    Fires the event in the specified number of hours. Optional.
    random = <int> / <variable>
    Adds a random number (between
    0
    and
    random
    , inclusive) of
    hours
    to the scheduled fire time. Optional.
    random_days = <int> / <variable>
    Adds a random number (between
    0
    and
    random_days
    , inclusive) of days to the scheduled fire time. Optional.
    ```
  - Example:
    ```text
    unit_leader_event = {
        id = my_event.1
        days = 10
        random = 50
        random_days = 10
    }
    ```
  - Description: Fires the specified event for the owner of the current unit leader.
  - Notes:
    ```text
    Uses a special interface displaying the current unit leader portrait.
    Where triggers do not need to be repeatedly checked
    random
    can be a performance light alternative to
    mean_time_to_happen
    for scheduling events.
    ```
  - Version Added: 1.5

- **set_unit_leader_flag**
  - Parameters:
    ```text
    <flag>
    An unique string to identify the unit leader flag with.
    ```
  - Example:
    ```text
    set_unit_leader_flag = my_flag
    ```
  - Description: Defines a unit leader flag.
  - Notes:
    ```text
    Deprecated. Use
    set_character_flag
    instead. No tooltip is shown.
    ```
  - Version Added: 1.5

- **clr_unit_leader_flag**
  - Parameters:
    ```text
    <flag>
    The unique string of a unit leader flag to clear.
    ```
  - Example:
    ```text
    clr_unit_leader_flag = my_flag
    ```
  - Description: Clears a defined unit leader flag.
  - Notes:
    ```text
    Deprecated. Use
    clr_character_flag
    instead. No tooltip is shown.
    ```
  - Version Added: 1.5

- **modify_unit_leader_flag**
  - Parameters:
    ```text
    flag = <flag>
    The flag to modify.
    value = <value>
    The value to add to the flag. Defaults to 0.
    days = <int>
    The amount of days that the flag should last for before being cleared. Optional, defaults to permanent.
    ```
  - Example:
    ```text
    modify_unit_leader_flag = {
        flag = my_flag
        value = 3
    }
    ```
  - Description: Adds an integer value to a flag.
  - Notes:
    ```text
    The flag must be already set. Deprecated. Use
    modify_character_flag
    instead.
    ```
  - Version Added: 1.5

- **promote_leader**
  - Parameters:
    ```text
    <bool>
    Boolean
    ```
  - Example:
    ```text
    promote_leader = yes
    ```
  - Description: Promotes the current unit leader to Field Marshal (if Commander).
  - Version Added: 1.5

- **demote_leader**
  - Parameters:
    ```text
    <bool>
    Boolean
    ```
  - Example:
    ```text
    demote_leader = yes
    ```
  - Description: Demotes the current unit leader to Commander (if Field Marshal).
  - Version Added: 1.5

- **add_unit_leader_trait**
  - Parameters:
    ```text
    <trait>
    The trait to add.
    ```
  - Example:
    ```text
    add_unit_leader_trait = old_guard
    ```
  - Description: Adds the specified trait to the current unit leader.
  - Notes:
    ```text
    Traits are found in
    /Hearts of Iron IV/common/unit_leader/*.txt
    files.
    ```
  - Version Added: 1.0

- **remove_unit_leader_trait**
  - Parameters:
    ```text
    <trait>
    The trait to remove.
    ```
  - Example:
    ```text
    remove_unit_leader_trait = old_guard
    ```
  - Description: Removes the specified trait from the current unit leader.
  - Notes:
    ```text
    Traits are found in
    /Hearts of Iron IV/common/unit_leader/*.txt
    files.
    ```
  - Version Added: 1.0

- **add_random_trait**
  - Parameters:
    ```text
    <trait>
    The trait to add.
    ```
  - Example:
    ```text
    add_random_trait = { old_guard brilliant_strategist inflexible_strategist }
    ```
  - Description: Adds a random trait from the list to the character.
  - Notes:
    ```text
    Traits are found in
    /Hearts of Iron IV/common/unit_leader/*.txt
    files.
    ```
  - Version Added: 1.5

- **add_timed_unit_leader_trait**
  - Parameters:
    ```text
    <trait>
    The trait to add.
    days = <int>
    The duration of the trait.
    ```
  - Example:
    ```text
    add_timed_unit_leader_trait = {
        trait = wounded
        days = 90
    }
    ```
  - Description: Adds the specified trait to the current unit leader for the specified duration.
  - Notes:
    ```text
    Traits are found in
    /Hearts of Iron IV/common/unit_leader/*.txt
    files.
    ```
  - Version Added: 1.5

- **replace_unit_leader_trait**
  - Parameters:
    ```text
    trait = <trait>
    The trait to replace.
    replace = <trait>
    The new trait to add.
    ```
  - Example:
    ```text
    replace_unit_leader_trait = {
        trait = old_guard
        replace = brilliant_strategist
    }
    ```
  - Description: Replaces the specified trait with the new trait.
  - Notes:
    ```text
    Traits are found in
    /Hearts of Iron IV/common/unit_leader/*.txt
    files.
    Warning:
    This effect is extremely buggy. It does not properly replace traits and is crash prone. Use
    remove_unit_leader_trait
    and
    add_unit_leader_trait
    instead.
    ```
  - Version Added: 1.5

- **remove_exile_tag**
  - Parameters: Remove the exile tag on an army leader, making them no longer be considered exile leaders.
  - Example:
    ```text
    remove_exile_tag = yes
    ```
  - Description: Removes a leaders exile tag.
  - Version Added: 1.6

- **gain_xp**
  - Parameters: <int>
  - Example:
    ```text
    gain_xp = 5
    ```
  - Description: Adds experience to the current unit leader, promoting to the next skill level if applicable.
  - Notes: Cannot be used with negatives.
  - Version Added: 1.9

- **remove_unit_leader**
  - Parameters: <bool>
  - Example:
    ```text
    remove_unit_leader = yes
    ```
  - Description: Removes the current unit leader.
  - Version Added: 1.0

- **remove_unit_leader_role**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    remove_unit_leader_role = yes
    ```
  - Description: Removes every unit leader role from the character
  - Version Added: 1.11

### Country leaders

These can only be used with characters of the country leader type.

- **add_country_leader_trait**
  - Parameters:
    ```text
    <trait>
    The trait to add.
    OR
    :
    ideology = <sub-ideology>
    The sub-ideology of the country leader role to which the trait is added.
    trait = <trait>
    The trait to add.
    ```
  - Example:
    ```text
    add_country_leader_trait = nationalist_symbol
    ```
  - Example:
    ```text
    add_country_leader_trait = {
        ideology = marxism
        trait = anti_communist
    }
    ```
  - Description: Adds the specified trait to the current character.
  - Notes:
    ```text
    Traits are found in
    /Hearts of Iron IV/common/country_leader/*.txt
    files.
    The former only if the character has one country leader role.
    ```
  - Version Added: 1.11

- **remove_country_leader_trait**
  - Parameters:
    ```text
    <trait>
    The trait to remove.
    OR
    :
    ideology = <sub-ideology>
    The sub-ideology of the country leader role to which the trait is added.
    trait = <trait>
    The trait to remove.
    ```
  - Example:
    ```text
    remove_country_leader_trait = nationalist_symbol
    ```
  - Example:
    ```text
    remove_country_leader_trait = {
        ideology = marxism
        trait = anti_communist
    }
    ```
  - Description: Removes the specified trait from the current character.
  - Notes:
    ```text
    Traits are found in
    /Hearts of Iron IV/common/country_leader/*.txt
    files.
    The former only if the character has one country leader role.
    ```
  - Version Added: 1.11

- **swap_country_leader_traits**
  - Parameters:
    ```text
    remove = <trait>
    Trait to remove
    add = <trait>
    Trait to add
    ideology = <sub-ideology>
    Sub-ideology of the leader where to swap traits.
    ```
  - Example:
    ```text
    swap_country_leader_traits = {
        remove = nationalist_symbol
        add = anti_communist
        ideology = marxism
    }
    ```
  - Description: Swaps traits of the current character.
  - Notes:
    ```text
    Use
    swap_ruler_traits
    in country scope.
    ```
  - Version Added: 1.11

### Combat

- **supply_units**
  - Parameters:
    ```text
    <int> / <variable>
    The amount of hours of supply.
    ```
  - Example:
    ```text
    supply_units = 24
    ```
  - Description: Adds the specified amount of hours of supply to troops led by the current unit leader.
  - Version Added: 1.5

- **add_max_trait**
  - Parameters:
    ```text
    <int>
    The amount to add.
    ```
  - Example:
    ```text
    add_max_trait = 1
    ```
  - Description: Adds the specified amount of assignable trait slots to the current unit leader.
  - Version Added: 1.5

- **add_skill_level**
  - Parameters:
    ```text
    <int>
    The skill to add.
    ```
  - Example:
    ```text
    add_skill_level = 1
    ```
  - Description: Adds skill to the current unit leader.
  - Version Added: 1.5

- **add_logistics**
  - Parameters:
    ```text
    <int>
    How many skill levels to add.
    ```
  - Example:
    ```text
    add_logistics = 1
    ```
  - Description: Adds logistics skill to the current unit leader.
  - Version Added: 1.5

- **add_planning**
  - Parameters:
    ```text
    <int>
    How many skill levels to add.
    ```
  - Example:
    ```text
    add_planning = 1
    ```
  - Description: Adds planning skill to the current unit leader.
  - Version Added: 1.5

- **add_defense**
  - Parameters:
    ```text
    <int>
    How many skill levels to add.
    ```
  - Example:
    ```text
    add_defense = 1
    ```
  - Description: Adds defense skill to the current unit leader.
  - Version Added: 1.5

- **add_attack**
  - Parameters:
    ```text
    <int>
    How many skill levels to add.
    ```
  - Example:
    ```text
    add_attack = 1
    ```
  - Description: Adds attack skill to the current unit leader.
  - Version Added: 1.5

- **add_coordination**
  - Parameters:
    ```text
    <int>
    How many skill levels to add.
    ```
  - Example:
    ```text
    add_coordination = 1
    ```
  - Description: Adds coordination skill to the current navy leader.
  - Version Added: 1.5

- **add_maneuver**
  - Parameters:
    ```text
    <int>
    How many skill levels to add.
    ```
  - Example:
    ```text
    add_maneuver = 1
    ```
  - Description: Adds maneuver skill to the current navy leader.
  - Version Added: 1.5

- **add_temporary_buff_to_units**
  - Parameters:
    ```text
    combat_offense = <float>
    The bonus to grant. Optional.
    combat_breakthrough = <float>
    The bonus to grant. Optional.
    combat_defense = <float>
    The bonus to grant. Optional.
    combat_entrenchment = <float>
    The bonus to grant. Optional.
    org_damage_multiplier = <float>
    The bonus to grant. Optional.
    str_damage_multiplier = <float>
    The bonus to grant. Optional.
    war_support_reduction_on_damage = <float>
    The bonus to grant. Optional.
    cannot_retreat_while_attacking = <float>
    The bonus to grant. Optional.
    cannot_retreat_while_defending = <float>
    The bonus to grant. Optional.
    days = <int>
    The duration of the buff. Optional.
    tooltip = <string>
    The tooltip to display for the buff.
    ```
  - Example:
    ```text
    add_temporary_buff_to_units = {
        combat_offense = 0.25
        combat_breakthrough = 0.25
        org_damage_multiplier = -1.0
        str_damage_multiplier = 0.25
        war_support_reduction_on_damage = 0.2
        cannot_retreat_while_attacking = 1.0
    				
        days = 7
        tooltip = ABILITY_FORCE_ATTACK_TOOLTIP
    }
    ```
  - Description: Adds the specified combat buff to the current unit leader.
  - Version Added: 1.5

### Operatives

- **add_nationality**
  - Parameters:
    ```text
    <tag>
    The country to set the nationality to.
    ```
  - Example:
    ```text
    add_nationality = GER
    ```
  - Description: Adds the nationality to the current operative.
  - Version Added: 1.9

- **capture_operative**
  - Parameters:
    ```text
    captured_by = <tag>
    By which country to get captured.
    ignore_death_chance = <bool>
    Whether to ignore the death chance on capture (no by default).
    ```
  - Example:
    ```text
    capture_operative = {
        captured_by = POL
        ignore_death_chance = yes
    }
    ```
  - Description: Makes the current operative be captured by a specific country.
  - Version Added: 1.9

- **force_operative_leader_into_hiding**
  - Parameters: <bool>
  - Example:
    ```text
    force_operative_leader_into_hiding = yes
    ```
  - Description: Forces the current operative into hiding.
  - Version Added: 1.9

- **free_operative**
  - Parameters:
    ```text
    captured_by = <tag>
    The country that captured the operative.
    ```
  - Example:
    ```text
    free_operative = { captured_by = POL }
    ```
  - Description: Frees the current operative.
  - Version Added: 1.9

- **harm_operative_leader**
  - Parameters:
    ```text
    <int>
    How much to harm the operative.
    ```
  - Example:
    ```text
    harm_operative_leader = 12
    ```
  - Description: Harms the current operative.
  - Notes: The value is subject to modifiers.
  - Version Added: 1.9

- **kill_operative**
  - Parameters:
    ```text
    killed_by = <tag>
    The country that'll kill the operative.
    ```
  - Example:
    ```text
    kill_operative = { killed_by = POL }
    ```
  - Description: Kills the current operative.
  - Version Added: 1.9

- **turn_operative**
  - Parameters:
    ```text
    turned_by = <tag>
    The country to which the operative defects.
    ```
  - Example:
    ```text
    turn_operative = {
        turned_by = PREV
    }
    ```
  - Description: Turns the current operative against their own country, transferring them to the specified country.
  - Notes:
    ```text
    This counts as the operative dying and will trigger the corresponding
    On action
    . Logs an error if used against your own operative.
    ```
  - Version Added: 1.9

- **operative_leader_event**
  - Parameters:
    ```text
    id = <event>
    The event to fire.
    days = <int> / <variable>
    Fires the event in the specified number of days. Optional.
    hours = <int> / <variable>
    Fires the event in the specified number of hours. Optional.
    random = <int> / <variable>
    Adds a random number (between
    0
    and
    random
    , inclusive) of
    hours
    to the scheduled fire time. Optional.
    random_days = <int> / <variable>
    Adds a random number (between
    0
    and
    random_days
    , inclusive) of days to the scheduled fire time. Optional.
    originator = <tag>
    The originator of the event. Optional, defaults to owner of operative.
    recipient = <tag>
    The recipient of the event. Optional, defaults to owner of operative.
    set_from = <tag>
    Sets the scope of FROM in scripted localization. Optional.
    set_from_from = <tag>
    Sets the scope of FROM.FROM in scripted localization. Optional.
    set_root = <tag>
    Sets the scope of ROOT in scripted localization. Optional.
    ```
  - Example:
    ```text
    operative_leader_event = {
        id = my_event.1
    	originator = POL
    	recipient = GER
        days = 10
        random = 50
        random_days = 10
    	set_from = ENG
    	set_root = SOV
    	set_from_from = FRA
    }
    ```
  - Description: Fires the specified event for the operative.
  - Notes:
    ```text
    Uses a special interface displaying the current operative portrait.
    Where triggers do not need to be repeatedly checked
    random
    can be a performance light alternative to
    mean_time_to_happen
    for scheduling events.
    ```
  - Version Added: 1.9

## Division scope

The effects here must be used within a **division** scope.

- **destroy_unit**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    destroy_unit = yes
    ```
  - Description: Destroys the currently-scoped division.
  - Version Added: 1.12

- **add_history_entry**
  - Parameters:
    ```text
    key = <localisation key>
    The name of the entry.
    subject = "<string>"
    Logged entry. Never shown to the player.
    allow = <bool>
    Whether a medal can be awarded to the division over the history entry.
    ```
  - Example:
    ```text
    add_history_entry = {
        key = my_history_entry
        subject = "Test entry"
        allow = no
    }
    ```
  - Description: Creates an entry within the command history of a division.
  - Version Added: 1.12

- **change_division_template**
  - Parameters:
    ```text
    <string>
    The name of the division.
    ```
  - Example:
    ```text
    change_division_template = {
        division_template = "New template"
    }
    ```
  - Description: Changes the template of the division to the specified one.
  - Version Added: 1.12

- **add_random_valid_trait_from_unit**
  - Parameters:
    ```text
    <character>
    Character to grant the trait to.
    ```
  - Example:
    ```text
    add_random_valid_trait_from_unit = FROM
    ```
  - Description: Adds a random valid unit trait to a unit leader.
  - Notes: Only possible to use if the division scope is the same as the ROOT scope.
  - Version Added: 1.12

- **add_unit_medal_to_latest_entry**
  - Parameters:
    ```text
    unit_medals = <medal ID>
    The medal to add.
    ```
  - Example:
    ```text
    add_unit_medal_to_latest_entry = {
        unit_medals = my_medal
    }
    ```
  - Description: Adds the specified medal to the latest entry within the unit's history.
  - Version Added: 1.12

- **add_divisional_commander_xp**
  - Parameters:
    ```text
    <decimal>
    Experience to add.
    ```
  - Example:
    ```text
    add_divisional_commander_xp = 10
    ```
  - Description: Adds the specified amount of experience to the divisional commander.
  - Version Added: 1.12

- **reseed_division_commander**
  - Parameters:
    ```text
    <int>
    The seed to use.
    ```
  - Example:
    ```text
    reseed_division_commander = 760
    ```
  - Description: Re-randomises the division commander using the given seed.
  - Notes: Does not have a tooltip.
  - Version Added: 1.12

- **promote_officer_to_general**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    promote_officer_to_general = yes
    ```
  - Description: Promote the officer of the division to a general.

- **set_unit_organization**
  - Parameters:
    ```text
    <decimal>
    The level to set to.
    ```
  - Example:
    ```text
    set_unit_organization = 0.3
    ```
  - Description: Changes the organisation of the unit.
  - Notes: On the scale from 0 to 1.
  - Version Added: 1.13

## MIO scope

The effects here must be used within a **military industrial organisation** scope.

- **add_mio_funds**
  - Parameters:
    ```text
    <int>
    Funds to add.
    ```
  - Example:
    ```text
    add_mio_funds = 1000
    ```
  - Description: Adds funds to the MIO.
  - Notes: If the amount goes above the "Size Up" limit, the MIO will automatically gains sizes. The amount of funds is capped at 0 from below.
  - Version Added: 1.13

- **set_mio_funds**
  - Parameters:
    ```text
    <int>
    Amount to set.
    ```
  - Example:
    ```text
    set_mio_funds = 1000
    ```
  - Description: Sets the funds of a MIO to the certain level.
  - Notes: If the amount goes above the "Size Up" limit, the MIO will automatically gains sizes. Cannot be negative.
  - Version Added: 1.13

- **add_mio_funds_gain_factor**
  - Parameters:
    ```text
    <decimal>
    Amount to add.
    ```
  - Example:
    ```text
    add_mio_funds_gain_factor = 0.1
    ```
  - Description: Changes the base multiplier to MIO's funds.
  - Notes: The multiplier is capped at 0 from below.
  - Version Added: 1.13

- **set_mio_funds_gain_factor**
  - Parameters:
    ```text
    <decimal>
    Amount to set.
    ```
  - Example:
    ```text
    set_mio_funds = 0.1
    ```
  - Description: Changes the base multiplier to MIO's funds.
  - Notes: Cannot be negative.
  - Version Added: 1.13

- **add_mio_size**
  - Parameters:
    ```text
    <int>
    Amount to add.
    ```
  - Example:
    ```text
    add_mio_size = 2
    ```
  - Description: Adds sizes to the MIO.
  - Notes: Funds will not be changed by the effect. Cannot be negative.
  - Version Added: 1.13

- **add_mio_size_up_requirement_factor**
  - Parameters:
    ```text
    <decimal>
    Amount to add.
    ```
  - Example:
    ```text
    add_mio_size_up_requirement_factor = 0.1
    ```
  - Description: Changes the base multiplier to the requirement to size up a MIO.
  - Notes: The multiplier is capped at 0 from below.
  - Version Added: 1.13

- **set_mio_size_up_requirement_factor**
  - Parameters:
    ```text
    <decimal>
    Amount to set.
    ```
  - Example:
    ```text
    set_mio_size_up_requirement_factor = 0.1
    ```
  - Description: Changes the base multiplier to the requirement to size up a MIO.
  - Notes: Cannot be negative.
  - Version Added: 1.13

- **add_mio_task_capacity**
  - Parameters:
    ```text
    <int>
    Amount to add.
    ```
  - Example:
    ```text
    add_mio_task_capacity = 2
    ```
  - Description: Changes the base maximum task capacity of the MIO.
  - Notes: If the capacity is reduced to below the amount of assigned tasks, they'll be turned allowed. The base amount is capped at 0 from below. Doesn't instantly apply.
  - Version Added: 1.13

- **set_mio_task_capacity**
  - Parameters:
    ```text
    <int>
    Amount to set.
    ```
  - Example:
    ```text
    set_mio_task_capacity = 2
    ```
  - Description: Changes the base maximum task capacity of the MIO.
  - Notes: If the capacity is reduced to below the amount of assigned tasks, they'll be turned allowed. Cannot be negative. Doesn't instantly apply.
  - Version Added: 1.13

- **add_mio_research_bonus**
  - Parameters:
    ```text
    <decimal>
    Amount to add.
    ```
  - Example:
    ```text
    add_mio_research_bonus = 0.3
    ```
  - Description: Changes the base research bonus of the MIO.
  - Notes: The base amount is capped at 0 from below.
  - Version Added: 1.13

- **set_mio_research_bonus**
  - Parameters:
    ```text
    <decimal>
    Amount to set.
    ```
  - Example:
    ```text
    set_mio_research_bonus = 0.3
    ```
  - Description: Changes the base research bonus of the MIO.
  - Notes: Cannot be negative.
  - Version Added: 1.13

- **set_mio_name_key**
  - Parameters:
    ```text
    <localisation key>
    The new name.
    ```
  - Example:
    ```text
    set_mio_name_key = mio_new_name
    ```
  - Description: Changes the name of the MIO.
  - Notes:
    ```text
    May also refer to a
    scripted localisation
    definition, which'll be evaluated in MIO's scope.
    ```
  - Version Added: 1.13

- **set_mio_icon**
  - Parameters:
    ```text
    <sprite>
    The new
    sprite
    .
    ```
  - Example:
    ```text
    set_mio_icon = GFX_new_mio_icon
    ```
  - Description: Changes the MIO's icon.
  - Version Added: 1.13

- **add_mio_design_team_assign_cost**
  - Parameters:
    ```text
    <decimal>
    Amount to add.
    ```
  - Example:
    ```text
    add_mio_design_team_assign_cost = 0.3
    ```
  - Description: Changes the base political power cost of the MIO to assign research.
  - Notes: The base amount is capped at 0 from below.
  - Version Added: 1.13

- **set_mio_design_team_assign_cost**
  - Parameters:
    ```text
    <decimal>
    Amount to set.
    ```
  - Example:
    ```text
    set_mio_design_team_assign_cost = 0.3
    ```
  - Description: Changes the base political power cost of the MIO to assign research.
  - Notes: Cannot be negative.
  - Version Added: 1.13

- **add_mio_industrial_manufacturer_assign_cost**
  - Parameters:
    ```text
    <decimal>
    Amount to add.
    ```
  - Example:
    ```text
    add_mio_industrial_manufacturer_assign_cost = 0.3
    ```
  - Description: Changes the base political power cost of the MIO to assign production lines.
  - Notes: The base amount is capped at 0 from below.
  - Version Added: 1.13

- **set_mio_industrial_manufacturer_assign_cost**
  - Parameters:
    ```text
    <decimal>
    Amount to set.
    ```
  - Example:
    ```text
    set_mio_industrial_manufacturer_assign_cost = 0.3
    ```
  - Description: Changes the base political power cost of the MIO to assign production lines.
  - Notes: Cannot be negative.
  - Version Added: 1.13

- **add_mio_design_team_change_cost**
  - Parameters:
    ```text
    <decimal>
    Amount to add.
    ```
  - Example:
    ```text
    add_mio_design_team_change_cost = 0.3
    ```
  - Description: Changes the base experience cost of the MIO to assign to equipment by a percentage.
  - Notes:
    ```text
    The base amount is capped at 0 from below. Rounded down, e.g.
    0.3
    with a cost of
    5
    should result in
    6.5
    , but becomes
    6
    instead.
    ```
  - Version Added: 1.13

- **set_mio_design_team_change_cost**
  - Parameters:
    ```text
    <decimal>
    Amount to set.
    ```
  - Example:
    ```text
    set_mio_design_team_change_cost = 0.3
    ```
  - Description: Changes the base experience cost of the MIO to assign to equipment by a percentage.
  - Notes:
    ```text
    Cannot be negative. Rounded down, e.g.
    0.3
    with a cost of
    5
    should result in
    6.5
    , but becomes
    6
    instead.
    ```
  - Version Added: 1.13

- **unlock_mio_trait_tooltip**
  - Parameters:
    ```text
    <trait>
    Trait to display.
    OR
    trait = <trait>
    Trait to display.
    show_modifiers = <bool>
    Whether the trait's modifiers should be shown in the tooltip. Defaults to true.
    ```
  - Example:
    ```text
    unlock_mio_trait_tooltip = my_trait_1
    ```
  - Example:
    ```text
    unlock_mio_trait_tooltip = {
        trait = my_trait_2
        show_modifiers = no
    }
    ```
  - Description: Displays a tooltip that says that the trait is made available.
  - Notes: Doesn't change the availability of the trait directly.
  - Version Added: 1.13

- **complete_mio_trait**
  - Parameters:
    ```text
    <trait>
    Trait to complete.
    OR
    trait = <trait>
    Trait to complete.
    show_modifiers = <bool>
    Whether the trait's modifiers should be shown in the tooltip. Defaults to true.
    ```
  - Example:
    ```text
    complete_mio_trait = my_trait_1
    ```
  - Example:
    ```text
    complete_mio_trait = {
        trait = my_trait_2
        show_modifiers = no
    }
    ```
  - Description: Completes the specified MIO trait.
  - Notes: Automatically adds 1 size to the MIO. No checks are placed on the trait.
  - Version Added: 1.13

- **set_mio_flag**
  - Parameters:
    ```text
    <flag>
    An unique string to identify the MIO flag with.
    OR
    flag = <flag>
    The flag to set.
    days = <int>
    Sets the flag to last for the specified amount of days. Optional.
    value = <int>
    The new value of the flag on the scale from -2 147 483 648 to 2 147 483 647.
    ```
  - Example:
    ```text
    set_mio_flag = my_flag
    ```
  - Example:
    ```text
    set_mio_flag = {
        flag = my_flag
        days = 123
        value = 1
    }
    ```
  - Description: Defines a MIO flag.
  - Notes: No tooltip is shown.
  - Version Added: 1.13

- **clr_mio_flag**
  - Parameters:
    ```text
    <flag>
    The unique string of a country flag to clear.
    ```
  - Example:
    ```text
    clr_mio_flag = my_flag
    ```
  - Description: Clears a defined MIO flag.
  - Version Added: 1.13

- **modify_mio_flag**
  - Parameters:
    ```text
    flag = <flag>
    The flag to modify.
    value = <value>
    The value to add to the flag. Defaults to 0.
    days = <int>
    The amount of days that the flag should last for before being cleared. Optional, defaults to permanent.
    ```
  - Example:
    ```text
    modify_mio_flag = {
        flag = my_flag
        value = 3
    }
    ```
  - Description: Adds an integer value to a flag.
  - Notes: The flag must be already set.
  - Version Added: 1.13

## Contract scope

The effects here must be used within a **contract** scope.

- **cancel_purchase_contract**
  - Parameters:
    ```text
    <bool>
    Boolean.
    ```
  - Example:
    ```text
    cancel_purchase_contract = yes
    ```
  - Description: Cancels the current purchase contract.
  - Version Added: 1.13

## Raid scope

The effects here must be used within a **raid** scope.

- **add_raid_history_entry**
  - Parameters: <bool>
  - Example:
    ```text
    add_raid_history_entry = yes/no
    ```
  - Description: Add history entry to a raid.
  - Version Added: 1.15

- **raid_add_unit_experience**
  - Parameters:
    ```text
    <float>
    Can use either an explicit value or a variable
    ```
  - Example:
    ```text
    raid_add_unit_experience = 0.2
    ```
  - Description: Will give experience to any type of unit assigned to the raid, e.g. divisions or air wings.
  - Notes: The value defines the progress towards the max level, e.g. 0.2 = gain 20% of the experience needed to reach max level.
  - Version Added: 1.15

- **raid_damage_units**
  - Parameters:
    ```text
    <flag>
    An unique string to identify the project flag with.
    OR
    damage = <float/int>
    The amount of strength and organization damage taken.
    org_damage = <float/int>
    The amount of organization damage taken.
    str_damage = <float/int>
    The amount of strength damage taken
    plane_loss = <float/int>
    The amount of planes lost
    ratio = <bool>
    optional, default no
    ```
  - Example:
    ```text
    # Apply 50% damage to units
    raid_damage_units = {
    	damage = 0.5
    	ratio = yes
    }
    
    # Apply 10 strength loss and 20 organization loss to units
    raid_damage_units = {
    	org_damage = 20
    	str_damage = 10
    }
    
    # Lose 40% of all planes
    raid_damage_units = {
    	plane_loss = 0.4
    	ratio = yes
    }
    
    # Lose 5 planes
    raid_damage_units = {
    	plane_loss = 5
    }
    ```
  - Description: Damage is applied to ground units while damage to plane is defined as the amount of planes lost.
  - Notes:
    ```text
    If 'ratio = yes', then all damage / losses are applied as a fraction of the current amount.
    For units, damage can be defined through one value 'damage' or separately through 'org_damage' and 'str_damage'
    ```
  - Version Added: 1.15

## Special Project scope

The effects here must be used within a **special project** scope. Special projects must always be pre-pended with `sp:<special project>` when used a a scope or value.

- **add_project_progress_ratio**
  - Parameters:
    ```text
    <float>
    remove or add between -1 and 1 proect progress
    ```
  - Example:
    ```text
    sp:my_project = {
      add_project_progress_ratio = 0.1
      add_project_progress_ratio = var:my_var
    }
    ```
  - Description: Add progress to the project's prototype phase.
  - Notes: The input value is a ratio of the total needed progress to complete the special project.
  - Version Added: 1.15

- **complete_prototype_reward_option**
  - Parameters:
    ```text
    prototype_reward = <prototype_reward>
    The protypereward to compete
    prototyp_reward_option = my_option
    If multiple choice use the given one, use default one if not set. Optional.
    show_modifiers = <bool>
    Yes if the effects of the prototype reward should be shown (default no)
    ```
  - Example:
    ```text
    complete_prototype_reward_option = {
    	prototype_reward = my_reward
    	prototyp_reward_option = my_option
    	show_modifiers = yes
    }
    ```
  - Description: Complete a prototype reward option for the project in scope
  - Notes: The effect will respect the fire only once and allowed property of prototype rewards.
  - Version Added: 1.15

- **set_project_flag**
  - Parameters:
    ```text
    <flag>
    An unique string to identify the project flag with.
    OR
    flag = <flag>
    The flag to set.
    days = <int>
    Sets the flag to last for the specified amount of days. Optional.
    value = <int>
    The new value of the flag on the scale from -2 147 483 648 to 2 147 483 647.
    ```
  - Example:
    ```text
    set_project_flag = my_flag
    ```
  - Example:
    ```text
    set_project_flag = {
        flag = my_flag
        days = 123
        value = 1
    }
    ```
  - Description: Defines a project flag.
  - Notes: No tooltip is shown.
  - Version Added: 1.15

- **clr_project_flag**
  - Parameters:
    ```text
    <flag>
    The unique string of a country flag to clear.
    ```
  - Example:
    ```text
    clr_project_flag = my_flag
    ```
  - Description: Clears a defined project flag.
  - Version Added: 1.15

- **modify_project_flag**
  - Parameters:
    ```text
    flag = <flag>
    The flag to modify.
    value = <value>
    The value to add to the flag. Defaults to 0.
    days = <int>
    The amount of days that the flag should last for before being cleared. Optional, defaults to permanent.
    ```
  - Example:
    ```text
    modify_mproject_flag = {
        flag = my_flag
        value = 3
    }
    ```
  - Description: Adds an integer value to a flag.
  - Notes: The flag must be already set.
  - Version Added: 1.15

## Other scopes

The effects here must be used within a scope that's specified within the notes.

- **execute_operation_coordinated_strike**
  - Parameters:
    ```text
    amount = <int>
    How many times the operation will get executed within the days set in the operation.
    ```
  - Example:
    ```text
    execute_operation_coordinated_strike = {
        amount = 12
    }
    ```
  - Description: All prepared Port Strike and Strategic Bombing in the target region will execute multiple times without air defence being able to intercept them.
  - Notes: Can only be used within operations.
  - Version Added: 1.9

## Flow control

These scopes are used within effect scopes to control the execution of effects.

### If statements

An [if statement](<http://en.wikipedia.org/wiki/Conditional_(computer_programming>)#If%E2%80%93then(%E2%80%93else)) allows an execution of effects to only be done if certain [triggers](<Triggers - Hearts of Iron 4 Wiki.md>) are met. Conditional statements are represented with the `if = { ... }` effect. `limit = { ... }` inside of the if statement serves as a [trigger block](<Triggers - Hearts of Iron 4 Wiki.md>) that defines the conditions when it should be executed, and everything else directly inside of `if = { ... }` is interpreted as the effects that should be executed if the condition is true.

For example, the following will add 10% ![Stability](media/effect-hearts-of-iron-4-wiki_ec2e2a02fa__img2.png)Stability to the country this is executed on if it has positive ![Political Power](media/effect-hearts-of-iron-4-wiki_ec2e2a02fa__img3.png)Political Power and below 90% stability:

```text
if = {
    limit = {
        has_political_power > 0
        stability < 0.9
    }
    add_stability = 0.1
}
```

If the limit is not met, then none of the effects inside will be executed. If it is, then each one will be. If the limit is omitted, it defaults to being always true.

**The effects must be inside of the if statement to be tied to the limit**. For example, this will always give 100 ![Political Power](media/effect-hearts-of-iron-4-wiki_ec2e2a02fa__img4.png)Political Power, regardless of what country is played:

```text
if = {
    limit = { tag = BHR }
}                         # Closes if = { ... }. Since no effects are inside, this means that the if statement does absolutely nothing
add_political_power = 100 # Outside of if = { ... }, so it will always give 100 political power, even if not playing as BHR
```

Optionally, `else_if = { ... }` (with `limit = { ... }` serving in a similar fashion) and `else = { ... }` can be added. If the initial limit within `if = { ... }` is false, it moves on to the next `else_if = { ... }`, checking the limit there. If the limit there is false, then it moves on to the next one, until hitting an end or an `else = { ... }`.  
Two variants exist: nested and unnested. In the first case, the `else_if` or `else` is put directly inside of the preceding `if` or `else_if`, while in the second case it's put *right after*. In case of overlap, unnested if statements are preferred. Here is an example using unnested if statements:

```text
if = {
    limit = {
        stability < 0.3 # If stability is below 30%, add 30%.
    }
    add_stability = 0.3
}
else_if = {
    limit = {
        stability < 0.6 # Otherwise, if it's below 60% (i.e. 30-59%), add 20%
    }
    add_stability = 0.2
}
else = {
    add_stability = 0.1 # If there's 60-100% stability, add 10%
}
```

Within the tooltip, only effects that would be executed are shown. The effects within an unfulfilled if statement (or an `else`/`else_if` that's not read due to the if statement being met) will be hidden from the player, and so will the trigger. In order to avoid player confusion, [custom effect tooltips can be used to tell the player what this effect block would do](#effect-tooltips), such as being used within an `else`.

### Random effects

If you want an effect to have a random chance to be done or have nothing happen otherwise, the `random = { ... }` block is the simplest way to accomplish that:

```text
random = {
    chance = 80
    add_stability = 0.4
    add_war_support = 0.3
}
```

This in particular will have an 80% chance to add 40% stability and 30% war support and, accordingly, a 20% chance to do nothing. The chance here is on the scale from 0 to 100.

If you want the game to choose between effect blocks, random\_list can be used instead. For example, if you wanted an effect to randomly given the player one out of four bonuses, you'd do the following:

```text
random_list = {
    10 = {
        add_stability = 0.5
    }
    10 = {
        add_manpower = 10000
    }
    10 = {
        add_war_support = 0.5
    }
    10 = {
        army_experience = 100
    }
}
```

The number is not the chance, but the weight for each option, as they don't have to add up to 100 or any number. An option with the weight of 20 is twice as likely to be picked as the option with the chance of 10, for instance. In total, the probability for an option to be picked is equal to the weight of the option divided by the sum of all weights.

It is also possible to use modifiers (akin to MTTH blocks) to affect the weight of each possible random effect or to use variables as chances.

```text
random_list = {
    30 = {
        modifier = {
            factor = 1.3
            has_country_flag = inward_perfect_flag
        }
        add_stability = 0.5
    }
    25 = {
        add_manpower = 10000
    }
    20 = {
        add_war_support = 0.5
    }
    my_variable = { # Taking "my_variable" as the variable's name, both "var:my_variable" and "my_variable" are valid options, left up to the developer's preference.
        army_experience = 100
    }
}
```

If the country flag inward\_perfect\_flag is set, it'll multiply the above chance of 30 by 1.3 to get 39. Meanwhile, `my_variable` will take the value of the according temp variable or the current scope's variable as the weight of the option.

Note that if you want to create a repeatable decision including a random list, by default the same decision will pick the same random result every time it is triggered in a game. You can reverse this behaviour by including the following line in the decision block:

```text
fixed_random_seed = no
```

**This is only for decisions**. Elsewhere, random seed is unfixed by default, making this argument unnecessary to set to "no".

### Tooltip manipulation

*See also: [Localisation](<Localisation - Hearts of Iron 4 Wiki.md>)*

The "tooltip" in this case refers to the text shown to the player in-game that explains what the effect block changes within the game, such as "**+50** ![Political Power](media/effect-hearts-of-iron-4-wiki_ec2e2a02fa__img5.png)Political Power".

There are 3 ways to edit the tooltip within an effect block:

- `hidden_effect = { ... }` is used in order to hide the effects within from the tooltip, making their execution not get shown to the player.
- `effect_tooltip = { ... }` is, instead, used in order to put the effects into the tooltip without actually executing them.
- `custom_effect_tooltip = my_localisation_key` is used in order to put an arbitrary paragraph of text as an effect that will get executed.

For example, this sample [focus' completion reward](<National focus modding - Hearts of Iron 4 Wiki.md>) utilises all three:

```text
completion_reward = { 
    hidden_effect = {
        every_subject_country = { country_event = my_event.1 }
    }
    custom_effect_tooltip = send_event_to_subjects_tt
    effect_tooltip = {
        add_political_power = 100
    }
    custom_effect_tooltip = reject_war_tt
}
```

In this case, send\_event\_to\_subjects\_tt and reject\_war\_tt are localisation keys defined within any /Hearts of Iron IV/localisation/english/\*\_l\_english.yml file encoded with UTF-8-BOM, assuming the English language.

```text
 send_event_to_subjects_tt: "Sends a demand to our every subject.\nIf they agree, we get the following for each subject:"
 reject_war_tt: "If they reject the demand, we gain a wargoal against them."
```

In-game, this will appear as such:

Noticably, the effect that fires the country event gets hidden from the tooltip. After completing the focus, the only thing that happens is that every subject country receives an event with the ID of `my_event.1`, the country does not immediately gain 100 political power.

## Meta effects

Meta effects allow you to use non-dynamic effects (the ones that do not accept modifiers and can only use static tokens or constant values) as if they were accepting variables.

```text
add_equipment_to_stockpile = {
    type = infantry_equipment_2
    amount = eq_amount
}
```

In the effect shown above, amount of equipment added is dynamic and can be set using the variable "eq\_amount". However, this effect does not let you use a variable as equipment type. You can not store "infantry\_equipment\_2" in a variable and use it here.

However, meta effects will let you use variables and scripted localization within them to build effects as if they were texts and run them. Let's make previous effect accept equipment type and equipment level as variables stored in "eq\_type" and "eq\_level".

```text
set_variable = { eq_type = 1 } # Sets the equipment type to "1", which determines the equipment given using scripted localisation, included below
set_variable = { eq_amount = 10 } # Sets the amount of equipment given to 10
set_variable = { eq_level = 2 } # Sets the equipment level to 2, which is used directly in the meta effect, no scripted localisation required

meta_effect = { # The actual meta effect. This can go anywhere you need it: in a decision, in a scripted effect, in a scripted GUI click effect, etc...
    text = {
        add_equipment_to_stockpile = {
            type = [EQ_TYPE]_[EQ_LEVEL]
            amount = eq_amount
        }
    }
    EQ_LEVEL = "[?eq_level|.0]" # Gets the "eq_level" variable and saves it as "EQ_LEVEL" for the meta effect to use
    EQ_TYPE = "[This.GetEquipmentName]" # Gets the equipment type from scripted localisation, included below, based on the "eq_type" variable, and saves it as "EQ_TYPE" for the meta effect to use
}
```

```text
# The scripted localization for the "eq_type" variable, which goes in a scripted localisation file
defined_text = { # Since the "eq_type" variable in this example is equal to 1, the equipment given by the effect is "artillery_equipment"
    name = GetEquipmentName
    text = {
        trigger = {
            check_variable = { eq_type = 0 }
        }
        localization_key = "infantry_equipment"
    }
    text = {
        trigger = {
            check_variable = { eq_type = 1 }
        }
        localization_key = "artillery_equipment"
    }
}
```

As you can see, we have created a meta\_effect that takes two arguments. These arguments will be used replacing the parameters [EQ\_TYPE] and [EQ\_LEVEL] inside the meta effect. EQ\_LEVEL will be replaced by [?eq\_level|.0] which is the integer value of eq\_level (in this case 2.000 becomes 2). EQ\_TYPE is a bit more complicated, it is being replaced by a scripted localization. This scripted localization will check eq\_type variable and depending on its value it will return the key token for the equipment. If it is 0, it will return "infantry\_equipment". If it is 1, it will return "artillery\_equipment".

So the final result is [EQ\_TYPE] is being replaced by "artillery\_equipment" and [EQ\_LEVEL] is being replaced by "2" and in the end our effect will be built as:

```text
add_equipment_to_stockpile = {
    type = artillery_equipment_2
    amount = eq_amount
}
```

which will give you 10 artillery\_equipment\_2.

debug = yes can be added to meta effects. Which will print the final effect to game.log when the effect is executed and make debugging easier.

## Scripted effects

Scripted effects serve a similar purpose to [functions](https://en.wikipedia.org/wiki/Subroutine) in that they can be defined in /Hearts of Iron IV/common/scripted\_effects/\*.txt and then used elsewhere as a shortened version. **A scripted effect will never run by itself** and requires being used as an effect elsewhere to be executed. Alongside that, the game allows the creation of custom console commands, which are scripted effects.

A scripted effect is defined simply as

```text
scripted_effect_name = {
	<effects>
}
```

This example can be used as an effect in regular code as `scripted_effect_name = yes`.

Scripted effects can be accessed in console by typing `e scripted_effect_name` to run them.

To create a custom console command, the scripted effect's name should begin with `d_`. The console command itself does not include `d_`, so `d_test_command` would be run in console as `test_command`  
In custom console commands, the country running the command is FROM, while ROOT is the selected country, state, or character. Anything entered after the console command, separated by spaces like `test_command 123 321 GER` is added to the 'args' temp array. An example of a scripted effect which will transfer every state entered as an argument to the country that runs the console command is

```text
d_transfer_states = {
	for_each_scope_loop = {
		array = args
		FROM = {
			transfer_state = PREV
		}
	}
}
```

used like `transfer_states 123 321`

### Useful scripted effects

These scripted effects are defined in base game and might be useful to keep in the mod to cut down on the amount of code. As scripted effects, all of these use a boolean value as argument.

- **instantiate_collaboration_government**
  - Scope: Country
  - Example:
    ```text
    instantiate_collaboration_government = yes
    ```
  - Description: Creates a collaboration government, with the current scope as overlord.
  - Notes:
    ```text
    The target of the collaboration government is stored in the
    country_to_initiate
    temp variable
    .
    ```

- **upgrade_economy_law**
  - Scope: Country
  - Example:
    ```text
    upgrade_economy_law = yes
    ```
  - Description: Switches the economy law one level towards total mobilisation.
  - Notes:
    ```text
    If already on total mobilisation, adds 150
    Political Power
    . Must be adjusted manually for new laws.
    ```

- **gain_random_agency_upgrade**
  - Scope: Country
  - Example:
    ```text
    gain_random_agency_upgrade = yes
    ```
  - Description: Grants a random available intelligence agency upgrade.
  - Notes: Only results in an agency being created if one doesn't exist.

- **add_ruling_to_dem**
  - Scope: Country
  - Example:
    ```text
    add_ruling_to_dem = yes
    ```
  - Description:
    ```text
    All of the ruling party's popularity gets added to the
    Democratic
    ideology group.
    ```
  - Notes:
    ```text
    Requires manual adjustment if new ideologies are added. See also:
    add_ruling_to_fas
    ,
    add_ruling_to_com
    ,
    add_ruling_to_neu
    ```

- **remove_any_country_role_from_character**
  - Scope: Character
  - Example:
    ```text
    remove_any_country_role_from_character = yes
    ```
  - Description: Removes all advisor roles from the current scope.
  - Notes: Requires manual adjustment if new slots are added.

- **increase_state_category**
  - Scope: State
  - Example:
    ```text
    increase_state_category = yes
    ```
  - Description:
    ```text
    Changes the
    state category
    to the next one that contains more building slots.
    ```
  - Notes:
    ```text
    Has no effect on small islands, megalopolises, or
    large_city
    (Dense Urban Region).
    city
    (Urban Region) gets upgraded straight to Metropolis, skipping
    large_city
    .
    ```

- **lerp**
  - Scope: Any
  - Example:
    ```text
    lerp = yes
    ```
  - Description:
    ```text
    Creates the
    lerp_result
    regular variable with
    r
    e
    s
    u
    l
    t
    :=
    a
    +
    (
    b
    −
    a
    )
    ⋅
    x
    {\displaystyle result:=a+(b-a)\cdot x}
    ```
  - Notes:
    ```text
    a
    {\displaystyle a}
    ,
    b
    {\displaystyle b}
    , and
    x
    {\displaystyle x}
    are stored as
    lerp_a
    ,
    lerp_b
    ,
    lerp_x
    temp variables
    .
    x
    {\displaystyle x}
    is clamped between 0 and 1.
    ```

- **store_core_states_on_game_start**
  - Scope: Country
  - Example:
    ```text
    store_core_states_on_game_start = yes
    ```
  - Description:
    ```text
    Stores the current core states of the current scope in an
    array
    in ROOT's scope.
    ```
  - Notes:
    ```text
    The created array will be named
    core_states_at_game_start
    . Intended to be called in
    country history
    only once.
    ```

**[Modding](<Modding - Hearts of Iron 4 Wiki.md>)**
