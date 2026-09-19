# Triggers

*Offline snapshot of the Hearts of Iron IV Wiki page "Triggers", captured 2026-09-19.*

## Table of contents

- [Operators](#Operators)
- [Context scopes](#Context_scopes)
- [Scopes](#Scopes)
  - [Trigger scopes](#Trigger_scopes)
  - [Dual scopes](#Dual_scopes)
- [Flow control tools](#Flow_control_tools)
- [Any scope](#Any_scope)
  - [General](#General)
  - [Career profile](#Career_profile)
  - [Variables](#Variables)
  - [Debugging](#Debugging)
- [Country scope](#Country_scope)
  - [General](#General_2)
  - [National focuses](#National_focuses)
  - [Politics](#Politics)
  - [Balance of power](#Balance_of_power)
  - [Buildings](#Buildings)
  - [Technology](#Technology)
  - [Ideas](#Ideas)
  - [Diplomacy](#Diplomacy)
  - [Faction](#Faction)
  - [War](#War)
  - [State](#State)
  - [Military](#Military)
  - [Doctrine](#Doctrine)
  - [Equipment](#Equipment)
  - [Intelligence](#Intelligence)
  - [AI](#AI)
  - [Characters](#Characters)
  - [Peace conferences](#Peace_conferences)
- [Faction scope](#Faction_scope)
- [State scope](#State_scope)
  - [General](#General_3)
  - [Resistance and Compliance](#Resistance_and_Compliance)
- [Character scope](#Character_scope)
  - [General](#General_4)
  - [Advisors](#Advisors)
  - [Country leaders](#Country_leaders)
  - [Unit leaders](#Unit_leaders)
  - [Operatives](#Operatives)
  - [Scientists](#Scientists)
- [Combat](#Combat)
- [Division scope](#Division_scope)
- [MIO scope](#MIO_scope)
- [Contract scope](#Contract_scope)
- [Special projects](#Special_projects)
- [Meta triggers](#Meta_triggers)
- [Scripted triggers](#Scripted_triggers)
  - [Diplomacy scripted triggers](#Diplomacy_scripted_triggers)
  - [Resistance initiation triggers](#Resistance_initiation_triggers)
  - [Useful scripted triggers](#Useful_scripted_triggers)
- [References and notes](#References_and_notes)

---

**Conditions** (also known as **Triggers**) are used to check whether certain conditions are fulfilled in the game's current state or not, without being able to change anything in the game's state.`[a]` These return a boolean (true or false), which may be interpreted by the block where it's used. Usually blocks that allow using triggers are an AND unless stated otherwise, which would instantly stop execution upon receiving a single false statement and return false. Please note that the `yes` and `no` inputs are case-sensitive and must not contain any uppercase letters.

The list of triggers may be outdated. A complete, but unsorted, list of triggers can be found in `/Hearts of Iron IV/documentation/triggers_documentation.html` or `/Hearts of Iron IV/documentation/triggers_documentation.md`. As of 1.17.1.1, this file was last updated in the version 1.17.0.

## Operators <a id="Operators"></a>

Every trigger uses one of the three operators: The equality sign `=` or the comparison signs `>` and `<`.

The equality sign can either mean strict equality (Unlike previous games in the series where it checked for being equal or greater than) or can serve as a way to introduce a block of additional triggers, as in `has_opinion = { target = GRE value < -10 }`. The comparison signs serves as strict comparison: `has_political_power > 100` will not be true if the country has exactly 100 political power, for instance.

Not all triggers support the equality sign or comparison signs. See the details for each trigger in the notes for it. If not stated otherwise, the trigger only supports the equality sign.

## Context scopes <a id="Context_scopes"></a>

There are three general scopes all triggers operate in:

- country
- state
- character

They give context to a trigger by stating what the trigger is checking against.

Each country acts as a sub-scope of the general country scope, i.e. `GER = { }` will check only against Germany, whereas `any_country` will check against all countries. Likewise for states and characters.

Triggers won't work in scopes they are not assigned to. Country triggers will not work for states or vice-versa.

## Scopes <a id="Scopes"></a>

:   *Main article: [Scopes](<Scopes - Hearts of Iron 4 Wiki.md>)*

These don't serve as triggers, but rather as scopes that change for whom the triggers are being checked. Each one also serves as an AND statement.

### Trigger scopes <a id="Trigger_scopes"></a>

These can only be used as triggers; trying to use them as [effects](<Effects - Hearts of Iron 4 Wiki.md>) will result in nothing happening.

Trigger scopes:

| Name | Usage | Target type | Example | Description | Version Added |
| --- | --- | --- | --- | --- | --- |
| all_country | Always usable | Country | `all_country = { … }` | Checks if all countries meet the triggers. | 1.0 |
| any_country | Always usable | Country | `any_country = { … }` | Checks if any country meets the triggers. | 1.0 |
| all_other_country | Within country scope only | Country | `all_other_country = { … }` | Checks if all countries other than the one where this scope is located meet the triggers. | 1.0 |
| any_other_country | Within country scope only | Country | `any_other_country = { … }` | Checks if any country other than the one where this scope is located meets the triggers. | 1.0 |
| all_country_with_original_tag | Always usable | Country | `all_country_with_original_tag = {`<br>`    original_tag_to_check = TAG  #required`<br>`    …                  #triggers to check`<br>`}` | Checks if all countries originating from the specified country, including the dynamic countries created for civil wars and other purposes, meet the triggers. `original_tag_to_check = TAG` is used to specify the original tag. | 1.9 |
| any_country_with_original_tag | Always usable | Country | `any_country_with_original_tag = {`<br>`    original_tag_to_check = TAG  #required`<br>`    …                  #triggers to check`<br>`}` | Checks if any country originating from the specified country, including the dynamic countries created for civil wars and other purposes, meets the triggers. `original_tag_to_check = TAG` is used to specify the original tag. | 1.9 |
| all_neighbor_country | Within country scope only | Country | `all_neighbor_country = { … }` | Checks if all countries that border the one where this scope is located meet the triggers. | 1.0 |
| any_neighbor_country | Within country scope only | Country | `any_neighbor_country = { … }` | Checks if any country that borders the one where this scope is located meets the triggers. | 1.0 |
| any_home_area_neighbor_country | Within country scope only | Country | `any_home_area_neighbor_country = { … }` | Checks if any country that borders the one where this scope is located, as well as being in its home area - meaning a direct land connection between the capitals of countries - meets the triggers. | 1.0 |
| all_guaranteed_country | Within country scope only | Country | `all_guaranteed_country = { … }` | Checks if all countries that are guaranteed by the one where this scope is located meet the triggers. | 1.9 |
| any_guaranteed_country | Within country scope only | Country | `any_guaranteed_country = { … }` | Checks if any country that is guaranteed by the one where this scope is located meets the triggers. | 1.9 |
| all_allied_country | Within country scope only | Country | `all_allied_country = { … }` | Checks if all countries that are allied with the one where this scope is located - meaning that they are either a subject of the country, its overlord, or that they share a faction - meet the triggers. Does not include the country itself. | 1.9 |
| any_allied_country | Within country scope only | Country | `any_allied_country = { … }` | Checks if any country that is allied with the one where this scope is located - meaning that they are either a subject of the country, its overlord, or that they share a faction - meets the triggers. Does not include the country itself. | 1.9 |
| all_occupied_country | Within country scope only | Country | `all_occupied_country = { … }` | Checks if all countries that are occupied by the one where this scope is located - meaning that the occupied country has core states controlled by the occupier country - meet the triggers. | 1.9 |
| any_occupied_country | Within country scope only | Country | `any_occupied_country = { … }` | Checks if any country that is occupied by the one where this scope is located - meaning that the occupied country has core states controlled by the occupier country - meets the triggers. | 1.9 |
| all_enemy_country | Within country scope only | Country | `all_enemy_country = { … }` | Checks if all countries that are at war with the one where this scope is located meet the triggers. | 1.9 |
| any_enemy_country | Within country scope only | Country | `any_enemy_country = { … }` | Checks if any country that are at war with the one where this scope is located meets the triggers. | 1.9 |
| all_subject_countries | Within country scope only | Country | `all_subject_countries = { … }` | Checks if all countries that are a subject of the one where this scope is located meet the triggers. Notice the plural spelling in the scope. | 1.11 |
| any_subject_country | Within country scope only | Country | `any_subject_country = { … }` | Checks if any country that is a subject of the one where this scope is located meets the triggers. | 1.11 |
| any_country_with_core | Within state scope only | Country | `any_country_with_core = { … }` | Checks if any country that has the current scope as a core state meets the triggers. **Does not have an equivalent for other effect/trigger scope types.** | 1.12 |
| all_country_of | Alway usable | Country | `all_country_of = {`<br>`	tooltip = my_loc # Optional bindable localization`<br>`	target = { SWE NOR FIN DEN ICE }`<br>`	has_defensive_war = yes`<br>`}`<br><br>`all_country_of = {`<br>`    tooltip = my_loc # Optional bindable localization`<br>`	target = constant:country_groups:nordics`<br>`	has_defensive_war = yes`<br>`}` | Checks if all of the provided countries fulfill the specified triggers. The \`target\` supports script constants and \`tooltip\` supports bindable localization. | 1.17 |
| any_country_of | Alway usable | Country | `any_country_of = {`<br>`	tooltip = my_loc # Optional bindable localization`<br>`	target = { SWE NOR FIN DEN ICE }`<br>`	has_defensive_war = yes`<br>`}`<br><br>`any_country_of = {`<br>`    tooltip = my_loc # Optional bindable localization`<br>`	target = constant:country_groups:nordics`<br>`	has_defensive_war = yes`<br>`}` | Checks if any of the provided countries fulfills the specified triggers. The \`target\` supports script constants and \`tooltip\` supports bindable localization. | 1.17 |
| all_state | Always usable | State | `all_state = { … }` | Check if all states meet the triggers. | 1.0 |
| any_state | Always usable | State | `any_state = { … }` | Check if any state meets the triggers. | 1.0 |
| any_state_in | Always usable | State | `any_state_in = {`<br>`  array = array_of_states  #required`<br>`    …                  #triggers to check`<br>`}`Requires on of the following fields`array = <array_of_states>`<br>`continent = <continent_name>`<br>`ai_area = <ai_area_name>`<br>`strategic_region = <strategic_region_number>` | Check if any state in the given category meets the trigger. | 1.15 |
| any_state_of | Alway usable | State | `any_state_of = {`<br>`	tooltip = my_loc # Optional bindable localization`<br>`	target = { 1 42 1992 }`<br>`	controller = {`<br>`		has_defensive_war = yes`<br>`	}`<br>`}`<br><br>`any_state_of = {`<br>`    tooltip = my_loc # Optional bindable localization`<br>`	target = constant:country_groups:nordics`<br>`	controller = {`<br>`		has_defensive_war = yes`<br>`	}`<br>`}` | Checks if any of the provided states fulfills the specified triggers. The \`target\` supports script constants and \`tooltip\` supports bindable localization. | 1.17 |
| all_neighbor_state | Within state scope only | State | `all_neighbor_state = { … }` | Check if all states that are neighbour to the one where this scope is located meet the triggers. | 1.0 |
| any_neighbor_state | Within state scope only | State | `any_neighbor_state = { … }` | Check if any state that is neighbour to the one where this scope is located meets the triggers. | 1.0 |
| all_owned_state | Within country scope only | State | `all_owned_state = { … }` | Check if all states that are owned by the country where this scope is located meet the triggers. | 1.0 |
| any_owned_state | Within country scope only | State | `any_owned_state = { … }` | Check if any state that is owned by the country where this scope is located meets the triggers. | 1.0 |
| all_core_state | Within country scope only | State | `all_core_state = { … }` | Check if any state that is cored by the country where this scope is located meets the triggers. | 1.11 |
| any_core_state | Within country scope only | State | `any_core_state = { … }` | Check if all states that are cored by the country where this scope is located meet the triggers. | 1.11 |
| all_controlled_state | Within country scope only | State | `all_controlled_state = { … }` | Check if all states that are controlled by the country where this scope is located meet the triggers. | 1.9 |
| any_controlled_state | Within country scope only | State | `any_controlled_state = { … }` | Check if any state that is controlled by the country where this scope is located meets the triggers. | 1.9 |
| all_unit_leader | Within country scope only | Unit Leader | `all_unit_leader = { … }` | Checks if all unit leaders (corps commanders, field marshals, admirals) that are employed by the country where this scope is located meet the triggers. | 1.5 |
| any_unit_leader | Within country scope only | Unit Leader | `any_unit_leader = { … }` | Checks if any unit leader (corps commander, field marshal, admiral) that is employed by the country where this scope is located meets the triggers. | 1.5 |
| all_army_leader | Within country scope only | Unit Leader | `all_army_leader = { … }` | Checks if all army leaders that are employed by the country where this scope is located meet the triggers. | 1.5 |
| any_army_leader | Within country scope only | Unit Leader | `any_army_leader = { … }` | Checks if any army leader that is employed by the country where this scope is located meets the triggers. | 1.5 |
| all_navy_leader | Within country scope only | Unit Leader | `all_navy_leader = { … }` | Checks if all navy leaders that are employed by the country where this scope is located meet the triggers. | 1.5 |
| any_navy_leader | Within country scope only | Unit Leader | `any_navy_leader = { … }` | Checks if any navy leader that is employed by the country where this scope is located meets the triggers. | 1.5 |
| all_operative_leader | Within country scope or operations only | Operative | `all_operative_leader = { … }` | Checks if all operatives that are employed by the country where this scope is located meet the triggers. | 1.9 |
| any_operative_leader | Within country scope or operations only | Operative | `any_operative_leader = { … }` | Checks if any operative that is employed by the country where this scope is located meets the triggers. | 1.9 |
| all_character | Within country scope only | Character | `all_character = { … }` | Checks if all characters that are recruited by the country where this scope is located meet the triggers. | 1.11 |
| any_character | Within country scope only | Character | `any_character = { … }` | Checks if any character that is recruited by the country where this scope is located meets the triggers. | 1.11 |
| any_country_division | Within country scope only | Division | `any_country_division = { … }` | Checks if any division owned by the current country meets the triggers. | 1.12 |
| any_state_division | Within state scope only | Division | `any_state_division = { … }` | Checks if any division within the current state meets the triggers. | 1.12 |
| all_military_industrial_organization | Within country scope only | MIO | `all_military_industrial_organization = { … }` | Checks if all MIOs within the current country meet the conditions. | 1.13 |
| any_military_industrial_organization | Within country scope only | MIO | `any_military_industrial_organization = { … }` | Checks if any MIO within the current country meets the conditions. | 1.13 |
| all_purchase_contract | Within country scope only | Purchase contract | `all_purchase_contract = { … }` | Checks if all purchase contracts within the current country meet the conditions. | 1.13 |
| any_purchase_contract | Within country scope only | Purchase contract | `any_purchase_contract = { … }` | Checks if any purchase contract within the current country meets the conditions. | 1.13 |
| all_scientists | Within country scope only | Character | `all_scientistst = { … }` | Checks if all scientists of the Country in scope matches the triggers. | 1.15 |
| any_scientist | Within country scope only | Character | `any_scientist = { … }` | Checks if at least one active scientist of the Country in scope matches the triggers. | 1.15 |
| all_active_scientist | Within country scope only | Character | `all_active_scientist = { … }` | Checks if all active scientists of the Country in scope matches the triggers. | 1.15 |
| any_active_scientist | Within country scope only | Character | `any_active_scientist = { … }` | Checks if at least one active scientist of the Country in scope matches the triggers. | 1.15 |

### Dual scopes <a id="Dual_scopes"></a>

The following scopes can be used either as effect or trigger scopes; some can also be used as the right side of some effects and triggers as a target. If usage as a target is possible, it's marked within the table.

Several dual scopes may have a scope that varies depending on where it's used, such as variables, which can be set to anything.

Dual scopes:

| Name | Usage | Target type | Example | Description | Usable as target | Version Added |
| --- | --- | --- | --- | --- | --- | --- |
| TAG | Always usable | Country scope | `SOV = { country_event = my_event.1 }` | The country defined by the tag or tag alias. Tag aliases are defined in `/Hearts of Iron IV/common/country_tag_aliases`, as a way to refer to a specific country (such as a side in a civil war) in addition to its actual tag. If the country with the exact tag doesn't exist, but a dynamic country originating from the specified tag does, the scope will refer to the dynamic country. | ✓ | 1.0 |
| <state_id> | Always usable | State scope | `123 = { transfer_state_to = SCO }` | The state defined by this id. | ✓ | 1.0 |
| <character> | not within Character scope | Character scope | `ENG_theodore_makhno = { set_nationality = UKR }` | On game versions prior to 1.12.8, the character must be already recruited by the country this is scoped from. | ✓ | 1.11 |
| mio:<MIO> | Within country scope only | MIO scope | `mio:AST_cockatoo_doe_organization = { … }` | The MIO identified by that ID as defined within the `/Hearts of Iron IV/common/military_industrial_organization/organizations/*.txt` file. | ✓ | 1.13 |
| sp:<special_project> | Within country scope only | Special project scope | `sp:sp_land_flamethrower_tank = { … }` | The special project identified by that ID as defined within the `/Hearts of Iron IV/common/special_projects/projects/*.txt` file. | ✓ | 1.15 |
| ROOT | Always usable | Depends on usage | `ENG = {`<br>`    FRA = {`<br>`        GER = {`<br>`            declare_war_on = {`<br>`                target = ROOT`<br>`                type = annex_everything`<br>`            }`<br>`        }`<br>`    }`<br>`} #GER declares war on ENG (if there is no scope before ENG)` | Targets the root node of the block, an inherent property of each block. Most commonly, this is the default scope: for example, ROOT [within a national focus](<National focus modding - Hearts of Iron 4 Wiki.md>) will always refer to the country doing the focus and ROOT [within a event](<Event modding - Hearts of Iron 4 Wiki.md>) will always refer to the country getting the event. However, some blocks do distinguish between the default scope and ROOT, such as [certain scripted GUI contexts](<Scripted GUI modding - Hearts of Iron 4 Wiki.md>) or [certain on actions](<On actions - Hearts of Iron 4 Wiki.md#La_R.C3.A9sistance>). If a block doesn't have ROOT defined (such as [on_startup in on actions](<On actions - Hearts of Iron 4 Wiki.md>)), then it is impossible to use it. | ✓ | 1.0 |
| THIS | Always usable | Depends on usage | `set_temp_variable = { target_country = THIS }` | Targets the current scope where it's used. For example, when used in every_state, it will refer to the state that's currently being evaluated. Primarily useful for [variables](<Data structures - Hearts of Iron 4 Wiki.md>) (as in the example, where omitting it wouldn't work) or for [built-in localisation commands](<Localisation - Hearts of Iron 4 Wiki.md#Namespaces>), where some scope must be specified. More rarely, this may help with scope manipulation when using PREV. Since omitting it makes no difference in how the code gets interpreted, there is little to no usage outside of these cases. | ✓ | 1.0 |
| PREV | Always usable | Depends on usage | `FRA = {`<br>`    random_country = {`<br>`        GER = {`<br>`            declare_war_on = {`<br>`                target = PREV`<br>`                type = annex_everything`<br>`            }`<br>`        }`<br>`    }`<br>`} #Germany declares war on random_country` | Targets the scope that the current scope is contained in. Can have additional applications where the assumed default scope differs from the ROOT, such as in state events or some on_actions. Can be chained indefinitely as PREV.PREV. **Commonly results in broken-looking tooltips**: what's shown to the player doesn't always correlate with reality.<br> See also: [PREV usage](<Scopes - Hearts of Iron 4 Wiki.md#PREV_usage>). | ✓ | 1.0 |
| FROM | Always usable | Depends on usage | `declare_war_on = {`<br>`    target = FROM`<br>`    type = annex_everything`<br>`}`<br><br>`FROM = {`<br>`    load_oob = defend_ourselves`<br>`}` | Can be chained indefinitely as FROM.FROM. Used to target various hardcoded scopes inherent to the block, often a secondary scope in addition to ROOT. For example:<br> In [events](<Event modding - Hearts of Iron 4 Wiki.md>), this refers to the country that sent the event (i.e. if the event was fired [using an effect](<Event modding - Hearts of Iron 4 Wiki.md#Effect>), then it's the ROOT scope where it was fired).<br> In [targeted decisions](<Decision modding - Hearts of Iron 4 Wiki.md>) or [diplomacy scripted triggers](<Triggers - Hearts of Iron 4 Wiki.md#Scripted_triggers>), this refers to the scope that is targeted.<br> | ✓ | 1.0 |
| overlord | Within country scope only | Country scope | `overlord = { … }` | The overlord of the country if it is a subject. [Subject to the 'invalid event target' error.](<Scopes - Hearts of Iron 4 Wiki.md#Invalid_event_target>) | X | 1.3 |
| faction_leader | Within country scope only | Country scope | `faction_leader = { add_to_faction = FROM }` | Faction leader of the faction the country is a part of. [Subject to the 'invalid event target' error.](<Scopes - Hearts of Iron 4 Wiki.md#Invalid_event_target>) | X | 1.10.1 |
| owner | Within state, character, or combatant scope only | Country scope | `owner = { add_ideas = owns_this_state }` | In state scope, the country that owns the state. In combatant scope, the country that owns the divisions. In character scope, the country that has recruited the character. [Subject to the 'invalid event target' error](<Scopes - Hearts of Iron 4 Wiki.md#Invalid_event_target>) when used for a state. | X | 1.0 |
| controller | Within state scope only | Country scope | `controller = {`<br>`    ROOT = {`<br>`        create_wargoal = {`<br>`            target = PREV`<br>`            type = take_state_focus`<br>`            generator = { 123 }`<br>`        }`<br>`    }`<br>`}` | The controller of the current state. [Subject to the 'invalid event target' error.](<Scopes - Hearts of Iron 4 Wiki.md#Invalid_event_target>) | X | 1.0 |
| capital_scope | Within country scope only | State scope | `capital_scope = { … }` | The state where the capital of the current country is located in. [Subject to the 'invalid event target' error](<Scopes - Hearts of Iron 4 Wiki.md#Invalid_event_target>) in rare cases. | X | 1.0 |
| event_target:<event_target_key> | Always usable | Depends on usage | `event_target:my_event_target = { … }` | Saved [event target or global event target](<Data structures - Hearts of Iron 4 Wiki.md#Event_targets>), with no space after the colon. [Subject to the 'invalid event target' error.](<Scopes - Hearts of Iron 4 Wiki.md#Invalid_event_target>) | ✓ | 1.0 |
| var:<variable> | Always usable | Depends on usage | `var:my_variable = { … }`<br>`add_to_faction = my_variable` or <br>`add_to_faction = var:my_variable` | [Variable](<Data structures - Hearts of Iron 4 Wiki.md>) set to a scope.<br> When used as a target rather than a scope, the `var:` can be omitted in most cases. | ✓ | 1.5 |

## Flow control tools <a id="Flow_control_tools"></a>

:   *Main article: [Scopes#Flow control tools](<Scopes - Hearts of Iron 4 Wiki.md#Flow_control_tools>)*

These are triggers that serve as more of a way to establish a connection in how triggers are evaluated. Each one serves as a trigger scope with additional arguments and can be used regardless of scope.

Flow control tools:

| Name | Additional parameters | Examples | Description | Notes | Version Added |
| --- | --- | --- | --- | --- | --- |
| AND | None | `AND = {`<br>`    original_tag = GER`<br>`    has_stability > 0.5`<br>`}` | Returns false if any sub-trigger returns false, true otherwise. Evaluation stops at the first false sub-trigger. | Only necessary within OR statements and NOT statements, as everything else is implicitly AND. | 1.0 |
| OR | None | `OR = {`<br>`    original_tag = ENG`<br>`    original_tag = USA`<br>`}` | Returns true if any sub-trigger returns true, false otherwise. Evaluation stops at the first true sub-trigger. |  | 1.0 |
| NOT | None | `NOT = {`<br>`    has_stability > 0.5`<br>`    has_war_support > 0.5`<br>`}` | Returns false if any sub-trigger returns true, true otherwise. Evaluation stops at the first true sub-trigger. | Equivalent to a NOR rather than a NAND. | 1.0 |
| count_triggers | `amount = <int>`<br> The amount of triggers that need to be fulfilled. | `count_triggers = {`<br>`    amount = 2`<br>`    10 = { state_population = 100000 }`<br>`    11 = { state_population = 100000 }`<br>`    12 = { state_population = 100000 }`<br>`}` | Sums the results of all sub-triggers (false=0, true=1) and returns true if the sum is at least `amount`. |  | 1.5 |
| if | `limit = <trigger block>`<br> `else_if = <if-trigger>`<br> Alternative condition. Optional.<br> `else = <AND-trigger>`<br> Final alternative condition. Optional. | `if = {`<br>`    limit = {`<br>`        has_dlc = "Poland: United and Ready"`<br>`    }`<br>`    has_political_power > 100`<br>`}`<br>`else_if = {`<br>`    limit = {`<br>`        has_dlc = "Waking the Tiger"`<br>`    }`<br>`    has_war_support > 0.5`<br>`}`<br>`else = {`<br>`    always = no`<br>`}` | If `limit` is true, the sub-triggers are evaluated like an AND-trigger. If `limit` is false, `else_if` blocks are tried in sequence and finally `else` (if present). *Otherwise true is returned*. | Both nested (As in inside of `if = { ... }`) and unnested (As in the example) `else` and `else_if` exist. In case of overlap, unnested is preferred. Can be useful for tooltip management: same as in effects, if the limit is unmet, nothing appears. If it is met, then the limit is hidden while the condition outside of the limit appears in the tooltip.  `if = { limit = { trigger_1 = yes } trigger_2 = yes }` is equivalent to `OR = { NOT = { trigger_1 = yes } trigger_2 = yes }`, but generates a different tooltip. | 1.0 |
| hidden_trigger | None | `hidden_trigger = {`<br>`    country_exists = GER`<br>`}` | Hides the triggers from the tooltip shown to the player. | Also serves as an AND statement. | 1.0 |
| custom_trigger_tooltip | `tooltip = <string>`<br>The localisation key to use. | `custom_trigger_tooltip = {`<br>`    tooltip = sunrise_invasion_tt`<br>`    any_state = {`<br>`        is_owned_by = JAP`<br>`        is_on_continent = europe`<br>`        is_coastal = yes`<br>`    }`<br>`}` | Hides the triggers from the tooltip shown to the player and instead uses the specified localisation key. | Alias for #custom_override_tooltip trigger (see that trigger for more info). Kept for backward compatibility. Prefer #custom_override_tooltip instead. Also supports [Localisation#Bindable_localisation](<Localisation - Hearts of Iron 4 Wiki.md#Bindable_localisation>). | 1.0 |
| custom_override_tooltip | `tooltip = <string>`<br>The localisation key to use. `not_tooltip = <string>`<br>The localisation key to use for NOT block. Optional. | `custom_override_tooltip = {`<br>`    tooltip = {`<br>`      localization_key = GER_inner_circle_focus_in_progress_tt`<br>`	  CHARACTER = GER_rudolf_hess`<br>`	  FLAG_DAYS = [?GER_rally_the_industrialists_in_progress_flag:days]`<br>`    }`<br>`    not_tooltip = MY_TOOLTIP_NOT`<br>`    <triggers>`<br>`}` | An AND trigger that has an overriden custom tooltip. | A positive tooltip can be set with `tooltip` and the tooltip to be used inside a NOT can be set with `not_tooltip`. If no positive tooltip is provided and the root key is a localization key (not a formatter, see formatted localization), then a negative tooltip will be generated by appending `_NOT` to the root localization for the positive tooltip. Both `tooltip` and `not_tooltip` are bindable localizations. [Can also be used as effect.](<Effects - Hearts of Iron 4 Wiki.md>)<br> Also supports [Localisation#Bindable_localisation](<Localisation - Hearts of Iron 4 Wiki.md#Bindable_localisation>). | 1.15 |

## Any scope <a id="Any_scope"></a>

These triggers do not require any particular scope.

### General <a id="General"></a>

General any-scoped triggers:

| Name | Parameters | Examples | Description | Notes | Version Added |
| --- | --- | --- | --- | --- | --- |
| always | `<bool>`<br>Boolean. | `always = yes` | Always returns true or false. Useful for debugging. |  | 1.0 |
| has_global_flag | `<string>`<br>The flag to check. | `has_global_flag = my_flag` | Checks if the specified flag has been set. |  | 1.0 |
| has_global_flag | `flag = <string>`<br>The flag to check.<br> `value = <int>`<br>The flag value to check for. Optional.<br> `date = <date>`<br>The flag creation date to check for. Optional.<br> `days = <int>`<br>The duration the flag existed for. Optional. | `has_global_flag = {`<br>`    flag = my_flag`<br>`    days > 30`<br>`    date > 1936.6.1`<br>`    value > 0`<br>`}` | Compares the specified flag's last set date, days since last set, and/or value. | If not set, the value comparison is `>0`. `value` is limited between -32768 and 32767. | 1.0 |
| has_dlc | `<string>`<br>The DLC name to check for. | `has_dlc = "Waking the Tiger"` | Checks if the specified DLC is enabled. |  | 1.0 |
| has_start_date | `<date>`<br>The date to check for. | `has_start_date > 1950.01.01` | Checks if the specified date was the start date used for the current game. | Year.Month.Day Must use either > or < operators. | 1.0 |
| date | `<date>`<br>The date to check for. | `date < 1950.01.01` | Checks if the specified date against the current date. | Year.Month.Day Must use either > or < operators. | 1.0 |
| difficulty | `<int>`<br>The difficulty value. | `difficulty > 0` | checks if the specified difficulty against the current difficulty. | Must use either > or < operators. | 1.0 |
| has_any_custom_difficulty_setting | `<bool>`<br>Boolean. | `has_any_custom_difficulty_setting = yes` | Checks if any custom difficulty setting is changed from their default value. | Custom difficulty in this case refers to `/Hearts of Iron IV/common/difficulty_settings/*.txt`, used in base game to strengthen a specific country. | 1.0 |
| has_custom_difficulty_setting | `<string>`<br>The setting to check. | `has_custom_difficulty_setting = custom_diff_strong_sov` | Checks if the specified custom difficulty setting is changed from the default value. | Custom difficulty in this case refers to `/Hearts of Iron IV/common/difficulty_settings/*.txt`, used in base game to strengthen a specific country. | 1.0 |
| game_rules_allow_achievements | `<bool>`<br>Boolean. | `game_rules_allow_achievements = yes` | Checks if all of the active game rule options allow achievements. |  | 1.9 |
| country_exists | `<scope> / <variable>`<br>The country to check. | `country_exists = GER` | Checks if the specified country currently exists in game. |  | 1.0 |
| is_ironman | `<bool>`<br>Boolean. | `is_ironman = yes` | Checks if the current game is running in Ironman mode. |  | 1.0 |
| is_historical_focus_on | `<bool>`<br>Boolean. | `is_historical_focus_on = yes` | Checks if the current game is running with Historical Focuses on. |  | 1.0 |
| is_tutorial | `<bool>`<br>Boolean. | `is_tutorial = yes` | Checks if the current game is running in Tutorial mode. |  | 1.0 |
| is_debug | `<bool>`<br>Boolean. | `is_debug = yes` | Checks if game is in debug mode (launched with -debug argument). |  | 1.9 |
| threat | `<float>`<br>The amount to check for. | `threat > 0.5` | Checks if World Tension is above the specified amount. | Must use either > or < operators. | 1.0 |
| has_game_rule | `<string>`<br>The game rule to check for.<br> `<string> / <bool>`<br>The option to check.<br> | `has_game_rule = { rule = GER_can_remilitarize_rhineland option = yes }` | Checks if a game rule is set to a particular option. |  | 1.5 |
| has_completed_custom_achievement | `mod = <mod ID>`<br>The mod where the achievement is from.<br> `achievement = <achievement ID>`<br>The name of the achievement. | `has_completed_custom_achievement = {`<br>`    mod = my_mod_unique_id`<br>`    achievement = my_achievement_token`<br>`}` | Checks if the player controlling the current scope has completed the specified custom achievement. | The achievement (including the ID of the mod it's from) is defined within `/Hearts of Iron IV/common/achievements/*.txt` files[1]. The achievement could be completed during a previous session, not necessarily the current one.<br> If the mod defining the achievement is not loaded, the trigger evaluates as false. | 1.12.5 |

### Career profile <a id="Career_profile"></a>

Career profile-releated any-scoped triggers:

| Name | Parameters | Examples | Description | Notes | Version Added |
| --- | --- | --- | --- | --- | --- |
| career_profile_check_medal | `medal = <medal>`<br>Medal to check. `???`<br> | `career_profile_check_medal = {`<br>`  medal = raining_debris_medal`<br>`  ???`<br>`}` | Checks if the required medal is achieved and collected. | Provide no tooltip. | ??? |
| career_profile_check_ribbon | `ribbon = <ribbon>`<br>Ribbon to check. `tooltip = <loc_key>`<br>Optional. | `career_profile_check_ribbon = {`<br>`  ribbon = orchestra_of_boom`<br>`  tooltip = my_loc_key`<br>`}` | Checks if the required ribbon is achieved and collected. | By default provide no tooltip. | ??? |
| career_profile_check_playthrough_ratio | `frits = <variable>`<br> `second = <variable>`<br><br> `ratio = <int>`<br>Ratio.<br> `compare = <type>`<br>The type of comparison.<br> | `career_profile_check_playthrough_ratio = {`<br>`  first = enemy_casualties`<br>`  second = total_own_casualties`<br>`  ratio = 4`<br>`  compare = greater_than_or_equals`<br>`}` | Compares the ratio (first/second) of two playthrough values to a number. | Provide no tooltip. Possible compare types:   - less_than - less_than_or_equals - greater_than - greater_than_or_equals - equals - not_equals | ??? |
| career_profile_check_playthrough_value | `{ ... }`<br> **OR**<br> `var = <variable>`<br>Value to compare.<br> `value = <int>`<br>Value to compare to.<br> `compare = <type>`<br>The type of comparison. Optional.<br> `tooltip = <loc_key>`<br>Optional.<br> `tooltip_value = <int>`<br>Optional. | `career_profile_check_playthrough_value = {`<br>`  plan_landlocked_battleship > 1`<br>`  plan_landlocked_carrier > 0`<br>`}``career_profile_check_playthrough_value = {`<br>`  var = deployed_airplanes_with_air_defense_gold`<br>`  value = 100`<br>`  compare = greater_than_or_equals`<br>`  tooltip = CAREER_PROFILE_TRIGGER_DEPLOYED_AIRPLANES_WITH_AIR_DEFENSE`<br>`  tooltip_value = 100` | Compares a playthrough value to a number. | By default provide no tooltip. Possible compare types:   - less_than - less_than_or_equals - greater_than - greater_than_or_equals - equals - not_equals | ??? |
| career_profile_check_points | `value = <int>`<br>Value to compare. `compare = <type>`<br>The type of comparison.<br> `tooltip = <loc_key>`<br>Optional.<br> | `career_profile_check_points = {`<br>`  value = 5000`<br>`  compare = greater_than_or_equals`<br>`  tooltip = CAREER_PROFILE_TRIGGER_MINED_SEA_REGIONS`<br>`}` | Compares a career points value to a number. | By default provide no tooltip. Possible compare types:   - less_than - less_than_or_equals - greater_than - greater_than_or_equals - equals - not_equals | ??? |
| career_profile_check_ratio | Possible the same as #career_profile_check_playthrough_ratio. | Possible the same as #career_profile_check_playthrough_ratio. | Compares the ratio (first/second) of two career profile values to a number. | Possible the same as #career_profile_check_playthrough_ratio. | ??? |
| career_profile_check_value | Possible the same as #career_profile_check_playthrough_value. | Possible the same as #career_profile_check_playthrough_value. | Compares a career profile value to a number. | Possible the same as #career_profile_check_playthrough_value. | ??? |
| career_profile_has_player_flag | `<string>`<br>The flag to check. | `career_profile_has_player_flag = career_profile_overrun_infantry_flag` | Checks if the flag is set for the local player. |  | ??? |

### Variables <a id="Variables"></a>

Variable-related triggers:

| Name | Parameters | Examples | Description | Notes | Version Added |
| --- | --- | --- | --- | --- | --- |
| has_variable | `<variable>`<br>The variable to check. | `has_variable = my_var` | Checks if the specified variable exists for the current scope. |  | 1.5 |
| check_variable | `var = <variable>`<br>The variable to check.<br> `value = <float> / <variable>`<br>The value to check for.<br> `compare = <type>`<br>The type of comparison. Optional, can use < or > instead. | `check_variable = {`<br>`    var = my_var`<br>`    value = 10`<br>`    compare = greater_than_or_equals`<br>`}``check_variable = {`<br>`    my_var > 10`<br>`}` | Check the specified variable for the current scope. | Possible compare types:  - less_than - less_than_or_equals - greater_than - greater_than_or_equals - equals - not_equals | 1.5 |

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

See [Variables](<Data structures - Hearts of Iron 4 Wiki.md>) for more information.

### Debugging <a id="Debugging"></a>

These are usable as both effects and triggers and are used for debugging, with the player never seeing them.

Debugging-helpful triggers:

| Name | Parameters | Examples | Description | Notes | Version Added |
| --- | --- | --- | --- | --- | --- |
| log | `<string>`<br>What to log. Supports dynamic localisation.<br> | `log = "Added [?temp_add] to [THIS.GetTag]'s variable [?THIS.varvalue]"` | Appends an entry into the game.log and, if open, the console when evaluating the trigger. | game.log is stored within `/Hearts of Iron IV/logs/` in the [user directory](<Modding - Hearts of Iron 4 Wiki.md>) | 1.5 |
| print_variables | `print_global = <bool>`<br>Print global variables. Defaults to `no`.<br> `var_list = <list>`<br>The variables to print. Defaults to all variables.<br> `file = <string>`The file path to log to. Defaults to "variable_dump". Does not include the `.log` extension.<br> `text = <string>`Text to prepend. Defaults to "No Header".<br> `append = <bool>`Whether to append to the file instead of overwrite. Defaults to `yes` | `print_variables = {`<br>`    var_list = { myvar1 myvar2 }`<br>`    file = "my_dump_file"`<br>`    text = "my header"`<br>`}` | Dumps the specified variables from the current scope and optionally the global scope into a log file with the specified name. | The log will be within `/Hearts of Iron IV/logs/variable_dumps/` in the [user directory](<Modding - Hearts of Iron 4 Wiki.md>). See also [debugging variables](<Data structures - Hearts of Iron 4 Wiki.md#Debugging>). | 1.5 |

## Country scope <a id="Country_scope"></a>

Can be used in **country** scope.

### General <a id="General_2"></a>

General country-scoped triggers:

| Name | Parameters | Examples | Description | Notes | Version Added |
| --- | --- | --- | --- | --- | --- |
| exists | `<bool>`<br>Boolean. | `exists = yes` | Checks if the current scope exists in game. |  | 1.0 |
| tag | `<scope> / <variable>`<br>The country to check. | `tag = GER``tag = var:my_country` | Checks if the current scope is the specified country. | Only checks the actual tag while excluding dynamic countries, see original_tag if they should be included. | 1.0 |
| original_tag | `<scope> / <variable>`<br>The country to check. | `original_tag = GER``original_tag = var:my_country` | Checks if the current scope originates from the specified country. | This also includes dynamic countries: civil war breakaways and countries created via [create_dynamic_country](<Effects - Hearts of Iron 4 Wiki.md>). True for the original country. | 1.0 |
| is_ai | `<bool>`<br>Boolean. | `is_ai = yes` | Checks if the current scope is AI. |  | 1.0 |
| has_collaboration | `target = <country>`<br>The country to check.<br> `value <> <decimal>`<br>The value of the collaboration on the 0-1 scale. | `has_collaboration = {`<br>`    target = GER`<br>`    value > 0.5`<br>`}` | Checks if the current scope has a collaboration level in the target scope. | The target is occupied by the current scope. Must use < or > in the value argument. | 1.9 |
| has_country_flag | `<string>`<br>The flag to check. | `has_country_flag = my_flag` | Checks if the current scope has the specified flag. |  | 1.0 |
| has_country_flag | `flag = <string>`<br>The flag to check.<br> `value = <int>`<br>The flag value to check for. Optional.<br> `date = <date>`<br>The flag creation date to check for. Optional.<br> `days = <int>`<br>The duration the flag existed for. Optional. | `has_country_flag = {`<br>`    flag = my_flag`<br>`    days > 30`<br>`    date > 1936.6.1`<br>`    value > 0`<br>`}` | Compares the specified flag's last set date, days since last set, and/or value. | If not set, the value comparison is `>0`. `value` is limited between -32768 and 32767. | 1.0 |
| has_cosmetic_tag | `<string>`<br>The cosmetic tag to check. | `has_cosmetic_tag = SOV_custom` | Checks if the current scope has the specified cosmetic tag active. |  | 1.5 |
| has_event_target | `<event target>`<br>The event target to check. | `has_event_target = my_var` | Checks if current scope or global scope has the specified event target saved. |  | 1.0 |
| has_decision | `<string>`<br>The decision to check. | `has_decision = my_decision` | Checks if the current scope has the specified decision activated. |  | 1.5 |
| has_dynamic_modifier | `modifier = <string>`<br>The dynamic_modifier to check. <br> `scope = <scope>`<br> The country to check. Optional, if the original modifier has been targeted. | `has_dynamic_modifier = {`<br>`    modifier = my_dynamic_modifier`<br>`    scope = GER`<br>`}` | Checks if the current scope has the specified dynamic modifier activated. |  | 1.6 |
| has_active_mission | `<string>`<br>The mission to check. | `has_active_mission = my_mission` | Checks if the current scope has the specified mission active. |  | 1.5 |
| has_country_custom_difficulty_setting | `<bool>`<br>Boolean. | `has_country_custom_difficulty_setting = yes` | Checks if the any custom difficulty setting targeting the current scope is changed from the default value. | Custom difficulty in this case refers to `/Hearts of Iron IV/common/difficulty_settings/*.txt`, used in base game to strengthen a specific country. | 1.0 |
| has_terrain | `<terrain>`<br>Terrain. | `has_terrain = urban` | Checks if the current scope has any provinces of the specified terrain. | Only can be used in country scope. | 1.11 |
| is_dynamic_country | `<bool>`<br>Boolean. | `is_dynamic_country = yes` | Checks if the current scope is a dynamic country. | Dynamic countries include those generated in civil wars as well as those generated with the create_dynamic_country effect, such as collaboration governments. | 1.11 |
| num_of_supply_nodes | `<int>`<br>The amount to check for. | `num_of_supply_nodes > 10` | Checks if the current scope has the specified amount of supply nodes under control. | Can only use < or > operators. | 1.11 |
| <resource> (resource_count_trigger) | `<int>`<br>The amount to check for. | `tungsten > 10` | Checks if the current scope has the specified amount of the specified resource. | Must use either > or < operators for amount. Can also be used in state scope. | ??? |
| has_resources_in_country | `resource = <resource>`<br>The resource to check for.<br> `amount = <int>`<br>The amount to check for.<br> `extracted = <bool>`<br>Limits the checked resources only to those gained from the state's base value and multiplicative modifiers on top of it if true. Optional, defaults to false.<br> `buildings = <bool>`<br>Limits the checked resources only to those gained from the state's modifiers applied by buildings. Optional, defaults to false. | `has_resources_in_country = {`<br>`    resource = oil`<br>`    amount > 10`<br>`    extracted = yes`<br>`}` | Checks if the current scope has the specified amount of the specified resource in reserve. | Must use either > or < operators for amount. 'In reserve' means that it's not spent on equipment production or exports. | 1.12 |

### National focuses <a id="National_focuses"></a>

National focus-related country-scoped triggers:

| Name | Parameters | Examples | Description | Notes | Version Added |
| --- | --- | --- | --- | --- | --- |
| has_focus_tree | `<string>`<br>The focus tree to check. | `has_focus_tree = soviet_tree` | Checks if the current scope has the specified focus tree. |  | 1.3 |
| has_completed_focus | `<string>`<br>The focus to check. | `has_completed_focus = my_focus` | Checks if the current scope has the specified focus completed. |  | 1.0 |
| focus_progress | `focus = <string>`<br>The focus to check.<br> `progress = <string>`<br>The progress to check for. | `focus_progress = {`<br>`  focus = my_focus`<br>`  progress > 0.5`<br>`}` | Checks if the specified focus has been completed the specified percent for the current scope. | Must use either > or < operators for progress. | 1.0 |
| has_shine_effect_on_focus | `<string>`<br>The focus to check. | `has_shine_effect_on_focus = GER_wunderwaffe` | Check if country has shine effect on focus (either manually achieved or by being worked on). | Note that tooltips are only shown in debug mode. Shine can be added manually by selecting focus, or via [activate_shine_on_focus](<Effects - Hearts of Iron 4 Wiki.md>) effect. | 1.15 |

### Politics <a id="Politics"></a>

Political country-scoped triggers:

| Name | Parameters | Examples | Description | Notes | Version Added |
| --- | --- | --- | --- | --- | --- |
| <ideology> (ideology_support_trigger) | `<ideology> = <float> / <variable>`<br>The amount of the ideology to check for. | `fascism > 0.5``democratic > party_popularity@communism` | Checks if the current scope has popularity of the specified ideology above the specified amount. |  | 1.0 |
| has_political_power | `<float> / <variable>`<br>The amount to check for. | `has_political_power > 100` | Checks if the current scope has the specified amount of political power. | Must use either > or < operators. | 1.0 |
| political_power_daily | `<float> / <variable>`<br>The amount to check for. | `political_power_daily > 1` | Checks if the current scope has the specified amount of daily political power gain. | Must use either > or < operators. | 1.5 |
| political_power_growth | `<float> / <variable>`<br>The amount to check for. | `political_power_growth > 1` | Checks if the current scope has the specified amount of daily political power gain. | Must use either > or < operators. | 1.5 |
| command_power | `<float> / <variable>`<br>The amount to check for. | `command_power > 1` | Checks if the current scope has the specified amount of command power. | Must use either > or < operators. | 1.5 |
| command_power_daily | `<float> / <variable>`<br>The amount to check for. | `command_power_daily > 1` | Checks if the current scope has the specified amount of daily command power gain. | Must use either > or < operators. | 1.5 |
| has_war_support | `<float> / <variable>`<br>The amount to check for. | `has_war_support > 0.5` | Checks if the current scope has the specified percentage of War Support. | Must use either > or < operators. | 1.5 |
| has_stability | `<float> / <variable>`<br>The amount to check for. | `has_stability > 0.5` | Checks if the current scope has the specified percentage of Stability. | Must use either > or < operators. | 1.5 |
| has_government | `<ideology>`<br>The ideology group to check for.<br> **OR**<br> `<country>`<br>The country to compare with. | `has_government = fascism``has_government = ROOT` | Checks if the ruling party of the current scope meets the requirements of being either the specified ideology group or having the same ideology group as the specified country. |  | 1.0 |
| has_elections | `<bool>`<br>Boolean. | `has_elections = yes` | Checks if the current scope holds elections. |  | 1.0 |
| is_staging_coup | `<bool>`<br>Boolean. | `is_staging_coup = yes` | Checks if the current scope is staging a coup. |  | 1.3 |
| is_target_of_coup | `<bool>`<br>Boolean. | `is_target_of_coup = yes` | Checks if the current scope is the target of a coup. |  | 1.0 |
| has_civil_war | `<bool>`<br>Boolean. | `has_civil_war = yes` | Checks if the current scope has a civil war active. |  | 1.0 |
| civilwar_target | `<scope>`<br>The target country. | `civilwar_target = GER` | Checks if the specified country is a target of a civil war. |  | 1.0 |
| has_manpower_for_recruit_change_to | `value = <float>`<br>The amount to check for. `group = <group>`<br>The group to check for. | `has_manpower_for_recruit_change_to = {`<br>`    value > 0.05`<br>`    group = mobilization_laws`<br>`}` | Checks if the current scope has the specified amount of manpower for changing the specified idea group. | **Must** use either > or < operators as = operator checks for the **exact** value | 1.0 |
| has_rule | `<string>`<br>The rule to check for. | `has_rule = can_create_factions` | Checks if the current scope has the specified country rule. |  | 1.6 |
| has_casualties_war_support | `<float> / <variable>`<br>The amount to check for. | `has_casualties_war_support < 0` | Checks if the current scope has the specified percentage of war support from own combat casualties. | Must use either > or < operators. | 1.12 |
| has_convoys_war_support | `<float> / <variable>`<br>The amount to check for. | `has_convoys_war_support < 0` | Checks if the current scope has the specified percentage of war support from own convoys sunk. | Must use either > or < operators. | 1.12 |
| has_bombing_war_support | `<float> / <variable>`<br>The amount to check for. | `has_bombing_war_support < 0` | Checks if the current scope has the specified percentage of war support from own states bombed by the enemy. | Must use either > or < operators. | 1.12 |

### Balance of power <a id="Balance_of_power"></a>

Balances of power are stored within `/Hearts of Iron IV/common/bop/*.txt` files.

Balance of power-related country-scoped triggers:

| Name | Parameters | Examples | Description | Notes | Version Added |
| --- | --- | --- | --- | --- | --- |
| has_power_balance | `id = <bop ID>`<br>The balance to check for. | `has_power_balance = {`<br>`    id = TAG_my_bop`<br>`}` | Checks if the current scope has the specified balance of power active. |  | 1.12 |
| has_any_power_balance | `<bool>`<br>Boolean. | `has_any_power_balance = yes` | Checks if the current scope has any balance of power active. |  | 1.12 |
| power_balance_value | `id = <bop ID>`<br>The balance to check in.<br> `value = <float>`<br>The value to check for. | `power_balance_value = {`<br>`    id = TAG_my_bop`<br>`    value > 0.7`<br>`}` | Checks if the current scope has the specified value within the balance of power. | Either =, >, or < operators are allowed. | 1.12 |
| power_balance_daily_change | `id = <bop ID>`<br>The balance to check in.<br> `value = <float>`<br>The value to check for. | `power_balance_daily_change = {`<br>`    id = TAG_my_bop`<br>`    value < -0.01`<br>`}` | Checks if the current scope's balance of power changes each day by the specified value. | Either =, >, or < operators are allowed. | 1.12 |
| power_balance_weekly_change | `id = <bop ID>`<br>The balance to check in.<br> `value = <float>`<br>The value to check for. | `power_balance_weekly_change = {`<br>`    id = TAG_my_bop`<br>`    value < -0.01`<br>`}` | Checks if the current scope's balance of power changes each week by the specified value. | Either =, >, or < operators are allowed. | 1.12 |
| is_power_balance_in_range | `id = <bop ID>`<br>The balance to check in.<br> `range = <range ID>`<br>The range to check for. | `is_power_balance_in_range = {`<br>`    id = TAG_my_bop`<br>`    range > TAG_my_bop_right_range`<br>`}` | Checks if the current scope's balance of power value lies within the specified range. | Ranges are defined within the balance of power. Can use either =, >, and < operators. In case of > or <, the comparison is 'strict', i.e. excluding the range itself. | 1.12 |
| is_power_balance_side_active | `id = <bop ID>`<br>The balance to check in.<br> `side = <side ID>`<br>The side to check. | `is_power_balance_side_active = {`<br>`    id = TAG_my_bop`<br>`    side = TAG_my_bop_right_range`<br>`}` | Checks if the specified balance of power has a side active. | Sides are defined within the balance of power. "Active" means that the side is among those that are currently visible instead of relying on the current value. | 1.12 |
| has_power_balance_modifier | `id = <bop ID>`<br>The balance to check in.<br> `modifier = <modifier ID>`<br>The [static modifier](<Modifiers - Hearts of Iron 4 Wiki.md>). | `has_power_balance_modifier = {`<br>`    id = TAG_my_bop`<br>`    modifier = TAG_my_bop_modifier`<br>`}` | Checks if the current scope's balance of power value activates a modifier. | BoP modifiers are defined within `/Hearts of Iron IV/common/modifiers/*.txt` files, while they're activated in the balance of power definition. | 1.12 |

### Buildings <a id="Buildings"></a>

Building-related country-scoped triggers:

| Name | Parameters | Examples | Description | Notes | Version Added |
| --- | --- | --- | --- | --- | --- |
| <building> (building_count_trigger) | `<int>`<br>The amount of the specified building to to check for. | `arms_factory > 10` | Checks if the current scope has the specified amount of the specified building. | Must use either > or < operators. Works in the state scope as well, unlike the other triggers. Can also be used in state scope. | 1.0 |
| num_of_military_factories | `<int>`<br>The amount to check for. | `num_of_military_factories > 10` | Checks if the current scope has the specified amount of military factories. | Must use either > or < operators. | 1.0 |
| num_of_civilian_factories | `<int>`<br>The amount to check for. | `num_of_civilian_factories > 10` | Checks if the current scope has the specified amount of civilian factories. | Must use either > or < operators. | 1.0 |
| num_of_naval_factories | `<int>`<br>The amount to check for. | `num_of_naval_factories > 10` | Checks if the current scope has the specified amount of dockyards. | Must use either > or < operators. | 1.0 |
| num_of_available_military_factories | `<int>`<br>The amount to check for. | `num_of_available_military_factories > 10` | Checks if the current scope has the specified amount of available military factories. | Must use either > or < operators. | 1.0 |
| num_of_available_civilian_factories | `<int>`<br>The amount to check for. | `num_of_available_civilian_factories > 10` | Checks if the current scope has the specified amount of available civilian factories. | Must use either > or < operators. | 1.0 |
| num_of_available_naval_factories | `<int>`<br>The amount to check for. | `num_of_available_naval_factories > 10` | Checks if the current scope has the specified amount of available dockyards. | Must use either > or < operators. | 1.0 |
| num_of_factories | `<int>`<br>The amount to check for. | `num_of_factories > 10` | Checks if the current scope has the specified amount of military, civilian or dockyard factories. | Must use either > or < operators. | 1.0 |
| num_of_controlled_factories | `<int>`<br>The amount to check for. | `num_of_controlled_factories > 10` | Checks if the current scope has the specified amount of military, civilian or dockyard factories under control. | Must use either > or < operators. | 1.11 |
| num_of_owned_factories | `<int>`<br>The amount to check for. | `num_of_owned_factories > 10` | Checks if the current scope has the specified amount of military, civilian or dockyard factories under owned states. | Must use either > or < operators. | 1.11 |
| num_of_civilian_factories_available_for_projects | `<int>`<br>The amount to check for. | `num_of_civilian_factories_available_for_projects > 10` | Checks if the current scope has the specified amount of civilian factories usable for projects. | Must use either > or < operators. | 1.5 |
| ic_ratio | `tag = <scope>`<br>The country to check. `ratio = <float>`<br>The ratio to check for. | `ic_ratio = {`<br>`    tag = GER`<br>`    ratio > 0.5`<br>`}` | Checks if the current scope has the specified ratio of factories with the target country. | Must use either > or < operators for ratio. | 1.0 |
| has_damaged_buildings | `<bool>`<br>Boolean. | `has_damaged_buildings = yes` | Checks if the current scope has any damanged buildings in their states. |  | 1.0 |
| has_built | `type = <building>`<br>The building to check for. `value = <int>`<br>The amount to check for. | `has_built = {`<br>`    type = arms_factory`<br>`    value > 10`<br>`}` | Checks if the current scope has built the specified building the specified number of times. | Must use either > or < operators for value. | 1.0 |

### Technology <a id="Technology"></a>

Technology-related country-scoped triggers:

| Name | Parameters | Examples | Description | Notes | Version Added |
| --- | --- | --- | --- | --- | --- |
| has_tech | `<string>`<br>The technology to check for. | `has_tech = my_technology` | Checks if the current scope has the specified technology. |  | 1.0 |
| is_researching_technology | `<string>`<br>The technology to check for. | `is_researching_technology = my_tech` | Checks if the current scope is currently researching the specified technology. |  | 1.0 |
| can_research | `<string>`<br>The technology to check for. | `can_research = my_tech` | Checks if the current scope can start researching the specified technology. |  | 1.0 |
| original_research_slots | `<int>`<br>The amount to check for. | `original_research_slots > 3` | Checks if the current scope had the specified amount of slots at game start. | Must use either > or < operators. | 1.0 |
| amount_research_slots | `<int>`<br>The amount to check for. | `amount_research_slots > 3` | Checks if the current scope has the specified amount of research slots. | Must use either > or < operators. | 1.3 |
| is_in_tech_sharing_group | `<string>`<br>The group to check for. | `is_in_tech_sharing_group = us_research` | Checks if the current scope is in the specified technology sharing group. |  | 1.3 |
| num_tech_sharing_groups | `<int>`<br>The amount to check for. | `num_tech_sharing_groups > 3` | Checks if the current scope is in the specified amount of technology sharing groups. | Must use either > or < operators. | 1.3 |
| has_tech_bonus | `technology = <string>`<br>The technology to check for. Optional.<br> `category = <string>`<br>The category to check for. Optional.<br> | `has_tech_bonus = {`<br>`    technology = my_tech`<br>`}``has_tech_bonus = {`<br>`    category = my_category`<br>`}` | Checks if the current scope has a technology bonus in the specified category, or for the specific technology. |  | 1.3 |
| land_doctrine_level | `<int>`<br>The amount to check for. | `land_doctrine_level > 2` | Checks if the current scope has the specified amount of land doctrine technologies. | Must use either > or < operators. | 1.0 |
| num_researched_technologies | `<int>`<br>The amount to check for. | `num_researched_technologies > 10` | Checks how many technologies the target has researched. | Must use either > or < operators. | 1.3 |
| is_special_project_being_researched | `sp:<string>`<br>A special project to check for. | `is_special_project_being_researched = sp:sp_air_radar` | Checks if the country in scope is currently researching the special project in input. |  | 1.15 |
| is_special_project_completed | `sp:<string>`<br>A special project to check for. | `is_special_project_completed = sp:sp_land_flamethrower_tank` | Checks if the current scope has the specified special project completed. |  | 1.15 |

### Ideas <a id="Ideas"></a>

Idea-related country-scoped triggers:

| Name | Parameters | Examples | Description | Notes | Version Added |
| --- | --- | --- | --- | --- | --- |
| has_idea | `<string>`<br>The idea to check for. | `has_idea = my_idea` | Checks if the current scope has the specified idea. |  |  |
| has_idea_with_trait | `<string>`<br>The trait to check for. | `has_idea_with_trait = my_trait` | Checks if the current scope has any ideas with the specified trait. |  | 1.0 |
| has_allowed_idea_with_traits | `idea = <string>`<br>The trait to check for.<br> `limit = <int>`<br>The amount to check for.<br> `characters = <bool>`<br>If set, will only run this on characters.<br> `ignore = { <ideas> }`<br>If set, ignores the ideas inside. Optional.<br> | `has_available_idea_with_traits = {`<br>`    idea = my_trait`<br>`    limit = 1`<br>`    ignore = { generic_head_of_intelligence }`<br>`}` | Checks if the current scope has the specified amount of ideas with the specified trait. | ignore = idea_name works for 1 idea. | 1.9.1 |
| has_available_idea_with_traits | `idea = <string>`<br>The trait to check for.<br> `limit = <int>`<br>The amount to check for.<br> `characters = <bool>`<br>If set, will only run this on characters.<br> `ignore = { <ideas> }`<br>If set, ignores the ideas inside. Optional.<br> | `has_available_idea_with_traits = {`<br>`    idea = my_trait`<br>`    limit = 1`<br>`    ignore = { generic_head_of_intelligence }`<br>`}` | Checks if the current scope has the specified amount of ideas with the specified trait. | ignore = idea_name works for 1 idea. | 1.0 |
| amount_taken_ideas | `amount = <int>`<br>The amount to check for. `slots = { <string> }`<br>The slot type. | `amount_taken_ideas = {`<br>`    amount > 3`<br>`    slots = {`<br>`        political_advisor`<br>`    }`<br>`}` | Checks if the current scope has the specified amount of ideas of the specified slot type. Excludes spirits, hidden ideas, and laws. | Slots types are found in `/Hearts of Iron IV/common/idea_tags/*.txt`. | 1.4 |

### Diplomacy <a id="Diplomacy"></a>

Diplomatic country-scoped triggers:

| Name | Parameters | Examples | Description | Notes | Version Added |
| --- | --- | --- | --- | --- | --- |
| is_major | `<bool>`<br>Boolean. | `is_major = yes` | Checks if the current scope is considered a Major. |  | 1.0 |
| is_ally_with | `<scope> / <variable>`<br>The country to check for. | `is_ally_with = GER``is_ally_with = var:country` | Checks if the current scope is an ally (Faction members or subject-master relation). |  | 1.0 |
| is_spymaster | `<bool>`<br>Boolean. | `is_spymaster = yes` | Checks if the current scope is the spymaster of a faction. |  | 1.9 |
| has_non_aggression_pact_with | `<scope> / <variable>`<br>The country to check for. | `has_non_aggression_pact_with = GER` | Checks if the current scope has a non-aggression pact with the specified country. |  | 1.0 |
| is_guaranteed_by | `<scope> / <variable>`<br>The country to check for. | `is_guaranteed_by = GER` | Checks if the current scope has been guaranteed by the specified country. |  | 1.0 |
| has_guaranteed | `<scope> / <variable>`<br>The country to check for. | `has_guaranteed = GER` | Checks if the current scope has guaranteed the specified country. |  | 1.0 |
| has_military_access_to | `<scope> / <variable>`<br>The country to check for. | `has_military_access_to = GER` | Checks if the current scope has military access to the specified country. |  | 1.0 |
| gives_military_access_to | `<scope> / <variable>`<br>The country to check for. | `gives_military_access_to = GER` | Checks if the current scope gives military to the specified country. |  | 1.0 |
| is_neighbor_of | `<scope> / <variable>`<br>The country to check for. | `is_neighbor_of = GER` | Checks if the current scope is a neighbor of the specified country. |  | 1.0 |
| is_owner_neighbor_of | `<scope> / <variable>`<br>The country to check for. | `is_owner_neighbor_of = GER` | Checks if the current scope is a neighbor of the specified country with their core territory only. |  | 1.0 |
| is_puppet_of | `<scope> / <variable>`<br>The country to check for. | `is_puppet_of = GER` | Checks if the current scope is a puppet of the specified country. | A "puppet" is an autonomous state that has `is_puppet = yes` in its definition within `/Hearts of Iron IV/common/autonomous_states/`. For any subject type, see is_subject_of. | 1.0 |
| is_subject_of | `<scope> / <variable>`<br>The country to check for. | `is_subject_of = GER` | Checks if the current scope is a subject of the specified scope. |  | 1.0 |
| is_puppet | `<bool>`<br>Boolean. | `is_puppet = yes` | Returns true if the current country is a puppet. | A "puppet" is an autonomous state that has `is_puppet = yes` in its definition within `/Hearts of Iron IV/common/autonomous_states/`. For any subject type, see is_subject. | 1.0 |
| is_subject | `<bool>`<br>Boolean. | `is_subject = yes` | Checks if the current scope is a subject. |  | 1.0 |
| has_subject | `<bool>`<br>Boolean. | `has_subject = GRE` | Checks if the country has for subject the given country. |  | 1.0 |
| num_subjects | `<int>`<br>The amount to check for. | `num_subjects > 3` | Checks if the current scope has the specified amount of subjects. | Must use either > or < operators. | 1.3 |
| has_autonomy_state | `<string>`<br>The autonomy state to check for. | `has_autonomy_state = autonomy_dominion` | Checks if the current scope is in the specified autonomous state. |  | 1.0 |
| compare_autonomy_state | `<string>`<br>The autonomy state to check for. | `compare_autonomy_state > autonomy_dominion` | Checks if the current scope's autonomy state `min_freedom_level` is less or greater than that of the specified autonomy state. The special value "autonomy_free" compares as greater than any autonomy state. If the current scope is not a subject, it is treated as greater than any autonomy state (including "autonomy_free"). With `=`, checks if the current scope is in the specified autonomous state. |  | 1.0 |
| compare_autonomy_progress_ratio | `<float>`<br>The amount to check for. | `compare_autonomy_progress_ratio > 0.5` | Checks if the current scope autonomy progress is at the specified ratio. If the current scope is not a subject, the ratio is 1. |  | 1.3 |
| has_opinion_modifier | `<string>`<br>The opinion modifier to check for. | `has_opinion_modifier = my_modifier` | Checks if the current scope has the specified opinion modifier. |  | 1.0 |
| has_opinion | `target = <scope>`<br>The country to check for. `value = <float>`<br>The amount to check for. | `has_opinion = {`<br>`    target = GER`<br>`    value > 50`<br>`}` | Checks if the current scope has the specified opinion of the target country. | Must use either > or < operators. | 1.0 |
| has_relation_modifier | `target = <scope>`<br>The country to check for. `modifier = <modifier>`<br>The modifier to check for. | `has_relation_modifier = {`<br>`    target = GER`<br>`    modifier = my_modifier`<br>`}` | Checks if the current scope has the specified relation modifier with the specified country. |  | 1.0 |
| has_legitimacy | `<int>`<br>Amount to check. | `has_legitimacy > 50` | Checks how much legitimacy the current government in exile has. | Must use either > or < operators. Legitimacy ranges from 0 to 100. | 1.6 |
| is_exile_host | `<bool>`<br>Boolean. | `is_exile_host = yes` | Checks if the current country is hosting an exile. |  | 1.6 |
| is_hosting_exile | `<tag>`<br>Country. | `is_hosting_exile = POL` | Checks if the current country is hosting a specific exile. |  | 1.6 |
| is_government_in_exile | `<bool>`<br>Boolean. | `is_government_in_exile = yes` | Checks if the current country is exiled in a different country. |  | 1.6 |
| is_exiled_in | `<tag>`<br>Country to be exiled in. | `is_exiled_in = POL` | Checks if the current country is exiled in a specific country. |  | 1.6 |
| received_expeditionary_forces | `sender = <tag>`<br>Country which sent forces. `value <> <int>`<br>Amount of forces. | `received_expeditionary_forces = {`<br>`    sender = POL`<br>`    value > 10`<br>`}` | Checks if the current country received X units in expeditions from the specified country. |  | 1.6 |
| can_declare_war_on | `<tag>`<br>Country to check. | `can_declare_war_on = POL` | Checks if the current scope is able to declare war on the specified country. |  | 1.9 |
| foreign_manpower | `<int>`<br>Amount to check. | `foreign_manpower > 10000` | Checks how much foreign manpower we have received for garrisoning. | Must use either > or < operators. | 1.9 |
| is_embargoed_by | `<tag>`<br>Country to check. | `is_embargoed_by = USA` | Checks if the current scope is embargoed by the specified country. |  | 1.12 |
| is_embargoing | `<tag>`<br>Country to check. | `is_embargoing = CUB` | Checks if the current scope is embargoing the specified country. |  | 1.12 |
| has_market_access_with | `<tag>`<br>Country to check. | `has_market_access_with = CUB` | Checks if the current scope has market access with the specified country. |  |  |

### Faction <a id="Faction"></a>

Faction-related country-scoped triggers:

| Name | Parameters | Examples | Description | Notes | Version Added |
| --- | --- | --- | --- | --- | --- |
| is_in_faction | `<bool>`<br>Boolean. | `is_in_faction = yes` | Checks if the current scope is in a faction. |  | 1.0 |
| is_in_faction_with | `<scope> / <variable>`<br>The country to check for. | `is_in_faction_with = GER``is_in_faction_with = var:country` | Checks if the current scope is in a faction with the specified country. |  | 1.0 |
| is_faction_leader | `<bool>`<br>Boolean. | `is_faction_leader = yes` | Checks if the current scope is the leader of a faction. |  | 1.0 |
| num_faction_members | `<int> / <variable>`<br>The amount to check for. | `num_faction_members > 1` | Checks if the faction of the current scope has the specified amount of members. | Must use either > or < operators. | 1.0 |
| has_manpower_to_become_leader | `<bool>`<br>Boolean | `has_manpower_to_become_leader = yes` | Checks if the current country exceeds the current faction leader and its subjects in deployed manpower. |  | 1.17 |
| has_industry_to_become_leader | `<bool>`<br>Boolean | `has_industry_to_become_leader = yes` | Checks if the current country exceeds the faction leader in number of factories. |  | 1.17 |
| has_enough_influence_for_leadership | `<bool>`<br>Boolean | `has_enough_influence_for_leadership = yes` | Checks if the current country has enough political influence to become faction leader. |  | 1.17 |
| has_faction_template | `<template_id>`<br>Faction template id. | `has_faction_template = faction_template_chinese_united_front` | Checks if the current country is in a faction with a template. |  | 1.17 |
| has_active_rule | `<rule_id>`<br>Faction rule id. | `has_active_rule = government_in_exile_allowed` | Checks if the country's faction has a specific active rule. |  | 1.17 |
| has_faction_goal | `<goal_id>`<br>Faction goal id. | `has_faction_goal = faction_goal_resource_control` | Checks if the country's faction has an active or completed goal. |  | 1.17 |
| has_completed_faction_goal | `<goal_id>`<br>Faction goal id. | `has_completed_faction_goal = faction_goal_resource_control` | Checks if the country's faction has successfully completed a goal. |  | 1.17 |
| faction_goal_fulfillment | `goal = <goal_id>`<br>Faction goal id. `value = <float> / <variable>`<br>The amount to check for. | `faction_goal_fulfillment = {`<br>`    goal = faction_goal_resource_control`<br>`    value > 0.85`<br>`}``faction_goal_fulfillment = {`<br>`    goal = faction_goal_resource_control`<br>`    value > 0.5`<br>`    value < 0.85`<br>`}` | Checks fulfillment of a faction goal for the current country's faction. | Value supports > and <, can accept variables, can be repeated multiple times. | 1.17 |
| faction_manifest_fulfillment | `<float> / <variable>`<br>The amount to check for. | `faction_manifest_fulfillment > 0.95` | Checks manifest fulfillment value of current country's faction manifest. |  | 1.17 |
| faction_upgrade_level | `<upgrade_token>`<br>Faction upgrade token. | `faction_upgrade_level > upgrade_token` | Checks the active faction member upgrade against the specified upgrade. | Works with >, <, = | 1.17 |
| faction_power_projection | `<int> / <variable>`<br>The amount to check for. | `faction_power_projection > 100` | Checks power value of current country's faction projection. |  | 1.17 |
| faction_influence_rank | `<int> / <variable>`<br>The amount to check for. | `faction_influence_rank < 5` | Checks influence rank in the faction of the current country. |  | 1.17 |
| faction_influence_ratio | `<float> / <variable>`<br>The amount to check for. | `faction_influence_ratio > 0.1` | Checks influence ratio of current country in the faction. |  | 1.17 |
| faction_influence_score | `<int> / <variable>`<br>The amount to check for. | `faction_influence_score > 100` | Checks influence value of current country in the faction. |  | 1.17 |
| can_assign_supportive_scientist_to_faction | `<specialization>`<br>Specialization. | `can_assign_supportive_scientist_to_faction = specialization_land` | Checks if the faction from the country in scope has a free slot for a supportive scientist for the country with the specialization type. |  | 1.17 |
| has_faction_research_unlocked | `<bool>`<br>Boolean. | `has_faction_research_unlocked = yes` | Whether the faction has unlocked the research. |  | 1.17 |
| has_faction_military_unlocked | `<bool>`<br>Boolean. | `has_faction_military_unlocked = yes` | Whether the faction has unlocked the military operations. |  | 1.17 |
| compare_ideology_with_faction | `value = <float> / <variable>`<br>The amount to check for. `leader = <tag>`<br>Country to check. | `compare_ideology_with_faction = {`<br>`    value > 0.5`<br>`    leader = FROM`<br>`}` | Compares the ideology support of the country's ruling party for the ideology of the faction it wants to join. | Tooltip is visible only if 'leader' is in faction. | 1.17 |

### War <a id="War"></a>

War-related country-scoped triggers:

| Name | Parameters | Examples | Description | Notes | Version Added |
| --- | --- | --- | --- | --- | --- |
| has_war | `<bool>`<br>Boolean. | `has_war = yes` | Checks if the current scope is at war. |  | 1.0 |
| has_war_with | `<scope> / <variable>`<br>The country to check for. | `has_war_with = GER``has_war_with = var:country` | Checks if the current scope is at war with the specified country. |  | 1.0 |
| has_offensive_war_with | `<scope> / <variable>`<br>The country to check for. | `has_offensive_war_with = GER` | Checks if the current scope is in an offensive war against the specified country. |  | 1.0 |
| has_offensive_war_without_friend | `<scope> / <variable>`<br>The country to check for. | `has_offensive_war_without_friend = GER` | Is country at offensive war without specific ally present. |  | 1.17 |
| has_defensive_war_with | `<scope> / <variable>`<br>The country to check for. | `has_defensive_war_with = GER` | Checks if the current scope is in an defensive war against the specified country. |  | 1.0 |
| has_offensive_war | `<bool>`<br>Boolean. | `has_offensive_war = yes` | Checks if the current scope is in an offensive war. |  | 1.0 |
| has_defensive_war | `<bool>`<br>Boolean. | `has_defensive_war = yes` | Checks if the current scope is in a defensive war. |  | 1.0 |
| has_war_together_with | `<scope> / <variable>`<br>The country to check for. | `has_war_together_with = GER` | Checks if the current scope is in a war alongside the specified country. |  | 1.0 |
| has_war_with_major | `<bool>`<br>Boolean. | `has_war_with_major = yes` | Checks if the current scope is at war with any other country that is considered major. |  | 1.12 |
| has_war_with_wargoal_against | `target = <scope> / <variable>`<br>The country to check for.<br> `type = <wargoal>`<br>The wargoal to check for. Optional. | `has_war_with_wargoal_against = {`<br>`    target = ENG`<br>`    type = independence_wargoal`<br>`}` | Checks if the current scope is at war with the specified country with the specified wargoal being active. | Wargoals are stored within `/Hearts of Iron IV/common/wargoals/*.txt` files. If no wargoal is specified, checks for *any* wargoal. Joining an ally in their war does not count as a wargoal. | 1.12 |
| surrender_progress | `<float> / <variable>`<br>The amount to check for. | `surrender_progress > 0.1` | Checks if the current scope has the specified amount of surrender progress. | Must use either > or < operators. | 1.0 |
| any_war_score | `<float>`<br>The amount to check for. | `any_war_score > 10` | Highest warscore value can be approximated by interating a variable by 1 for as long as any_war_score is greater than the variable. Checking with less than appears broken as a warscore of 0 is sometimes erroneously reported. | Must use either > or < operators. | 1.0 |
| has_capitulated | `<bool>`<br>Boolean. | `has_capitulated = yes` | Checks if the current scope has capitulated. |  | 1.0 |
| days_since_capitulated | `<int>`<br>Amount of days. | `days_since_capitulated > 10` | Checks the amount of days since the target last capitulated. | If the target never capitulated, the amount of days is extremely large. Recommended to combine with has_capitulated. | 1.9 |
| has_border_war_with | `<scope> / <variable>`<br>The country to check for. | `has_border_war_with = GER` | Checks if the current scope has a border war with the specified country. |  | 1.5 |
| has_border_war_between | `attacker = <scope> / <variable>`<br>The state to check for. `defender = <scope> / <variable>`<br>The state to check for. | `has_border_war_between = {`<br>`    attacker = 1`<br>`    defender = 2`<br>`}` | Checks if there is a border war between the two specified states. |  | 1.5 |
| has_border_war | `<bool>`<br>Boolean. | `has_border_war = yes` | Checks if the current scope has a border war active. |  | 1.5 |
| has_added_tension_amount | `<float> / <variable>`<br>The amount to check for. | `has_added_tension_amount > 10` | Checks if the current scope has caused the specified amount of World Tension. | Must use either > or < operators. | 1.0 |
| has_wargoal_against | `<scope> / <variable>`<br>The country to check for. | `has_wargoal_against = GER` | Checks if the current scope has any wargoal against the specified country. |  | 1.0 |
| has_wargoal_against | `target = <scope> / <variable>`<br>The country to check for.<br> `type = <string>`<br>The type of wargoal to check for. | `has_wargoal_against = {`<br>`    target = FROM`<br>`    type = take_state`<br>`}` | Checks if the current scope has a specific wargoal type against the specified country. |  | 1.8 |
| is_justifying_wargoal_against | `<scope> / <variable>`<br>The country to check for. | `is_justifying_wargoal_against = GER` | Checks if the current scope is justifying a wargoal against the specified country. |  | 1.0 |
| has_annex_war_goal | `<scope> / <variable>`<br>The country to check for. | `has_annex_war_goal = GER` | Checks if the current scope has the Annex wargoal against the specified country. |  | 1.0 |
| any_claim | `<bool>`<br>Boolean. | `any_claim = yes` | Will return true if  1. Is (manually) justifying on another country 2. Is being (manually) justified on 3. Has wargoal on another country 4. Another country has wargoal on the current country | Misleading name. In-game the localization says "Active or generating war goals related to `[TAG.GetNameDefCap]`" | 1.0 |
| is_in_peace_conference | `<bool>`<br>Boolean. | `is_in_peace_conference = yes` | Checks if the current scope is in a peace conference. | Please test this in-game for 1.12. | 1.0 |
| controls_province | `<id>`<br>The province to check for. | `controls_province = 1239` | Checks if the current scope has control of the specified province. |  | 1.9 |
| longest_war_length | `<int>`<br>Amount of months. | `longest_war_length > 3` | Checks how long a country has been at war, in months. |  | 1.14 |
| war_length_with | `tag = <scope> / <variable>`<br>Target country.<br> `months = <int>`<br>Amounth of months. | `war_length_with = {`<br>`    tag = GER`<br>`    months > 3`<br>`}` | Checks how long a country has been at war with specific country, in months. |  | 1.14 |
| has_truce_with | `<scope> / <variable>`<br>The country to check for. | `has_truce_with = GER` | Checks if the country has truce with the specified country. |  | 1.16 |
| has_naval_control | `<id> / <variable>`<br>The region to check in. | `has_naval_control = 16` | Checks if friendly nations and country scope together has enough naval dominance to assert control in strategic region. |  | 1.17 |
| has_enemy_naval_control | `<id> / <variable>`<br>The region to check in. | `has_enemy_naval_control = 16` | Checks if any enemy has enough naval dominance to assert control in certain strategic region. |  | 1.17 |

### State <a id="State"></a>

These are state-related triggers in the country scope, not [state-scoped triggers](#State_scope).

State-related country-scoped triggers:

| Name | Parameters | Examples | Description | Notes | Version Added |
| --- | --- | --- | --- | --- | --- |
| controls_state | `<scope> / <variable>`<br>The state to check for. | `controls_state = 39``controls_state = var:state` | Checks if the current scope has control of the specified state. |  | 1.0 |
| owns_state | `<scope> / <variable>`<br>The state to check for. | `owns_state = 39` | Checks if the current scope owns the specified state. |  | 1.0 |
| num_of_controlled_states | `<int>`<br>The amount to check for. | `num_of_controlled_states > 5` | Checks if the current scope has the specified amount of controlled states. | Must use either > or < operators. | 1.0 |
| num_occupied_states | `<int>`<br>The amount to check for. | `num_occupied_states > 5` | Checks if the current scope has the specified amount of occupied states. | Must use either > or < operators. | 1.0 |
| has_full_control_of_state | `<scope> / <variable>`<br>The state to check for. | `has_full_control_of_state = 39` | Checks if the current scope has total control (100% occupation) of the specified state. |  | 1.3 |
| has_resources_rights | `state = <scope> / <variable>`<br>The state to check in. Mandatory if used in country scope. `resources = { <resource> <...> <resource> }`<br>Resources to check for. Optional, defaults to any if unset. | `has_resources_rights = {`<br>`  state = 123`<br>`  resources = { oil steel }`<br>`}` | Checks if there are any resource rights with the specified parameters. | Can be used in either state or country scope. Always returns false if the state has no resources. Can also be used in state scope. | 1.12 |
| core_compliance | `occupied_country_tag = <TAG>`<br>The country for which to check compliance.<br> `value = <int>`<br>The value to check for.<br> | `core_compliance = {`<br>`    occupied_country_tag = ITA`<br>`    value > 10`<br>`}` | Compares the average compliance of core states of the specified country within controlled states of the current scope. | Must use either > or < operators for value. | 1.9 |
| core_resistance | `occupied_country_tag = <TAG>`<br>The country for which to check resistance.<br> `value = <int>`<br>The value to check for.<br> | `core_resistance = {`<br>`    occupied_country_tag = ITA`<br>`    value > 10`<br>`}` | Compares the average resistance of core states of the specified country within controlled states of the current scope. | Must use either > or < operators for value. | 1.9 |
| garrison_manpower_need | `<int>`<br>Amount to check. | `garrison_manpower_need > 10000` | Checks how much garrison manpower we need for resistance in controlled states. | Must use either > or < operators. | 1.9 |
| has_core_occupation_modifier | `occupied_country_tag = <scope> / <variable>`<br>The country to check.<br> `modifier = <token>`The modifier to check. | `has_core_occupation_modifier = {`<br>`  occupied_country_tag = ITA`<br>`  modifier = token`<br>`}` | Checks if the current scope has an occupation modifier for resistance/compliance that applies to our occupied states of a specified country. |  | 1.9 |
| occupation_law | `<law ID>`<br>The law to check. | `POL = {`<br>`  POL = {`<br>`    occupation_law = foreign_civilian_oversight`<br>`  }`<br>`}`# Checks POL's default occupation law`HOL = {`<br>`  BEL = {`<br>`    occupation_law = foreign_civilian_oversight`<br>`  }`<br>`}`# Checks HOL's occupation law over BEL | Checks the occupation law that's either the default or applied over a specific country. | Checks [PREV's](<Scopes - Hearts of Iron 4 Wiki.md#PREV_usage>) occupation law over the current country. If they're the same scope, checks the default occupation law. Can also be used in state scope. | 1.12 |
| has_contested_owner | `<state> / <variable>`<br>State to check. | `has_contested_owner = 42` | Checks if a state has the specified country as a contested owner. The trigger can be used either from a country or a state scope and accepts the other as parameter. | Can also be used in state scope. | 1.15 |
| owns_any_state_of | `<states>`<br>States to check. | `owns_any_state_of = {`<br>`  123`<br>`  246`<br>`}` | Check if the country owns any of the states in the list. | The same as:`OR = {`<br>`  owns_state = 123`<br>`  owns_state = 246`<br>`}` | 1.16 |
| is_on_same_continent_as | `<scope> / <variable>`<br>The state to check for. | `is_on_same_continent_as = 111` | Checks if the scope country is on the same continent as the given state. The capital state is used for given country tag. | Can also be used in state scope. | 1.17 |

### Military <a id="Military"></a>

Military-related country-scoped triggers:

| Name | Parameters | Examples | Description | Notes | Version Added |
| --- | --- | --- | --- | --- | --- |
| has_army_experience | `<float> / <variable>`<br>The amount to check for. | `has_army_experience > 10``has_army_experience > var:number` | Checks if the current scope has the specified amount of Army experience. | **Must** use either > or < operators as = operator checks for the **exact** value | 1.3 |
| has_air_experience | `<float> / <variable>`<br>The amount to check for. | `has_air_experience > 10` | Checks if the current scope has the specified amount of Air experience. | **Must** use either > or < operators as = operator checks for the **exact** value | 1.3 |
| has_navy_experience | `<float> / <variable>`<br>The amount to check for. | `has_navy_experience < 10` | Checks if the current scope has the specified amount of Navy experience. | **Must** use either > or < operators as = operator checks for the **exact** value | 1.3 |
| has_manpower | `<float> / <variable>`<br>The amount to check for. | `has_manpower > 1000` | Checks if the current scope has the specified amount of manpower. | **Must** use either > or < operators as = operator checks for the **exact** value | 1.0 |
| has_army_manpower | `size = <int>`<br>The amount to check for. | `has_army_manpower = {`<br>`    size > 1000`<br>`}` | Checks if the current scope has an army using the specified amount of manpower. | Must use either > or < operators. | 1.0 |
| manpower_per_military_factory | `<float>`<br>The amount to check for. | `manpower_per_military_factory > 1000` | Checks if the current scope has the specified manpower times their number of military factories. | Must use either > or < operators. | 1.0 |
| conscription_ratio | `<float> / <variable>`<br>The ratio to compare with. | `conscription_ratio < 0.2` | Checks if the current scope has the specified conscription ratio currently, not to be mixed up with the target conscription ratio. | **Must** use either > or < operators as = operator checks for the **exact** value | 1.9 |
| current_conscription_amount | `<float> / <variable>`<br>The amount to compare with. | `current_conscription_amount > 2000` | Checks if the current scope has already conscripted that much manpower. | **Must** use either > or < operators as = operator checks for the **exact** value | 1.9 |
| target_conscription_amount | `<float> / <variable>`<br>The amount to compare with. | `target_conscription_amount > 2000` | Checks if the current scope is targeting to conscript that much manpower. | **Must** use either > or < operators as = operator checks for the **exact** value | 1.9 |
| num_divisions | `<int>`<br>The amount to check for. | `num_divisions > 5` | Checks if the current scope has the specified amount of divisions. | Must use either > or < operators. | 1.3 |
| num_of_nukes | `<int>`<br>The amount to check for. | `num_of_nukes > 5` | Checks if the current scope has the specified amount of nukes. | Must use either > or < operators. | 1.0 |
| casualties | `<int>`<br>The amount to check for. | `casualties > 10000` | Checks if the current scope has suffered the specified amount of casualties. | Must use either > or < operators. | 1.0 |
| casualties_k | `<int>`<br>The amount to check for. | `casualties_k > 10` | Checks if the current scope has suffered the specified amount of casualties in thousands. | Must use either > or < operators. | 1.0 |
| casualties_inflicted_by | `opponent = <tag>`<br>The tag that inflicted the casualties.<br> `thousands <> <int>`<br> The amount of casualties in thousands. | `casualties_inflicted_by = {`<br>`    opponent = POL`<br>`    thousands > 10`<br>`}` | Checks if the current scope has suffered the specified amount of casualties in thousands from a specific country. | Must use either > or < operators for thousands. | 1.6 |
| amount_manpower_in_deployment_queue | `<float>`<br>The amount to check for. | `amount_manpower_in_deployment_queue > 1000` | Checks if the current scope has the specified amount of manpower in their deployment queue. | Must use either > or < operators. | 1.5 |
| has_attache_from | `<scope> / <variable>`<br>The country to check for. | `has_attache_from = GER` | Checks if the current scope has an attache from the specified scope. |  | 1.5 |
| has_attache | `<bool>`<br>Boolean. | `has_attache = yes` | Checks if the current scope has an attache. |  | 1.5 |
| is_lend_leasing | `<scope> / <variable>`<br>The country to check for. | `is_lend_leasing = GER` | Checks if the current scope is lend leasing to the specified scope. |  | 1.0 |
| has_template | `<string>`<br>The name of the template. | `has_template = "Infantry Division"` | Checks if the current scope has a division template of the specified name. |  | 1.0 |
| has_template_majority_unit | `<string>`<br>The unit to check for. | `has_template_majority_unit = infantry` | Checks if the current scope has a division template composed mostly of the specified unit. |  | 1.0 |
| has_template_containing_unit | `<string>`<br>The name of the unit. | `has_template_containing_unit = light_armor` | Checks if the current scope has a division template contained any of the specified unit. |  | 1.0 |
| strength_ratio | `tag = <scope>`<br>The country to check for. `ratio <> <float>`<br>The ratio to check for. | `strength_ratio = {`<br>`    tag = GER`<br>`    ratio > 1`<br>`}` | Checks if the current scope has the specified strength ratio against the specified country. The ratio is the number of fielded divisions of the current scope divided by those of `tag` (or 1 if `tag` has no divisions). The ratio gets increased by 10% if the current scope has a stronger air forces.[2] | Must use > or < in the ratio. | 1.0 |
| fighting_army_strength_ratio | `tag = <scope>`<br>The country to check for. `ratio <>= <float> / <variable>`<br>The ratio to check for. | `fighting_army_strength_ratio = {`<br>`    tag = GER`<br>`    ratio > 0.7`<br>`}` | Compares the total army fighting strength between the scope country and the one set with 'tag'. | Ratio can be '<','>' or '='. | 1.15 |
| naval_strength_ratio | `tag = <scope>`<br>The country to check for. `ratio <> <float>`<br>The ratio to check for. | `naval_strength_ratio = {`<br>`    tag = GER`<br>`    ratio > 1`<br>`}` | Checks if the current scope has the specified naval strength ratio against the specified country. | Must use > or < in the ratio. | 1.0 |
| naval_strength_comparison | `other = <scope>`<br>The country to check for.<br> `tooltip = <string>`<br>The ratio to check for. Optional.<br> `ratio <> <float>`<br>The ratio to check for.<br> `sub_unit_def_weights = { ... }` The weight to assign to each unit. Optional. | `naval_strength_comparison = {`<br>`    other = POL`<br>`    tooltip = my_loc_key_tt`<br>`    ratio > 1`<br>`    sub_unit_def_weights = {`<br>`        carrier = 1`<br>`        submarine = 2`<br>`    }`<br>`}` | Checks if the current scope has the specified naval strength ratio against the specified country. | Must use > or < in the ratio. If sub_unit_def_weights is unset, each unit is assumed to have 1 weight. If sub_unit_def_weights is set, only specified units will be counted towards strength. Units are defined in `/Hearts of Iron IV/common/units/*.txt`. | 1.6 |
| alliance_strength_ratio | `<float> / <variable>`<br>The ratio to check for. | `alliance_strength_ratio > 0.5` | Checks if the current scope and allies has an army strength higher than the specified ratio against estimated enemy strength. | Must use either > or < operators. | 1.0 |
| alliance_naval_strength_ratio | `<float> / <variable>`<br>The ratio to check for. | `alliance_naval_strength_ratio > 0.5` | Checks if the current scope and allies has an naval strength ratio higher than the specified ratio against estimated enemy strength. | Must use either > or < operators. | 1.0 |
| enemies_strength_ratio | `<float> / <variable>`<br>The ratio to check for. | `enemies_strength_ratio > 0.5` | Checks if the estimated enemy army strength ratio is higher than the specified ratio. | Must use either > or < operators. | 1.0 |
| enemies_naval_strength_ratio | `<float> / <variable>`<br>The ratio to check for. | `enemies_naval_strength_ratio > 0.5` | Checks if the estimated enemy naval strength ratio is higher than the specified ratio. | Must use either > or < operators. | 1.0 |
| has_army_size | `size = <float>`<br>The amount to check for.<br> `type = <string>`<br>The battalion type to check for. Divisions that are majority made up of battalions in that type count. Optional, counts all divisions by default.<br> | `has_army_size = {`<br>`    size > 10`<br>`    type = armor`<br>`}` | Checks if the current scope has the specified number of divisions, or of a specified type of division. | Battalion types are defined within `/Hearts of Iron IV/common/units/*.txt` files. Must use either > or < operators for size. | 1.0 |
| has_navy_size | `size = <float> / <variable>`<br>The amount to check for.<br> `type = <string>`<br>The type to check for. Optional.<br> `archetype = <string>`<br>The ship archetype to check for. Optional.<br> | `has_navy_size = {`<br>`    size > 10`<br>`    type = capital_ship`<br>`    archetype = ship_hull_heavy`<br>`}` | Checks if the current scope has the specified number of ships, or of a specified type of ship. | Ship types are defined within `/Hearts of Iron IV/common/units/*.txt` files. Must use either > or < operators for size. Ship archetypes are found in `/Hearts of Iron IV/common/units/equipment/*.txt` files. | 1.0 |
| has_deployed_air_force_size | `size = <float>`<br>The amount to check for.<br> `type = <string>`<br>The type to check for. Optional.<br> | `has_deployed_air_force_size = {`<br>`    size > 10`<br>`    type = cas`<br>`}` | Checks if the current scope has the specified number of aircraft, or of a specified type of aircraft. | Airwing types are defined within `/Hearts of Iron IV/common/units/*.txt` files. Must use either > or < operators for size. | 1.0 |
| divisions_in_state | `size = <float>`<br>The amount to check for.<br> `type = <string>`<br>The battalion type to check for. Divisions that are majority made up of battalions in that type count. Optional, counts all divisions by default.<br> `unit = <string>`<br>The exact battalion to check for. Divisions that are majority made up of that battalions count. Optional, counts all divisions by default.<br> `state = <scope> / <variable>`<br>The state to check in. | `divisions_in_state = {`<br>`    type = armor`<br>`    size > 10`<br>`    state = 49`<br>`}` | Checks if the specified state contains the specified amount of divisions. | Battalions and their types are defined within `/Hearts of Iron IV/common/units/*.txt` files. Must use either > or < operators for size. | 1.0 |
| army_manpower_in_state | `amount <> <float>`<br>The amount to check for.<br> `type = <string>`<br>The type to check for. Optional.<br> `state = <scope> / <variable>`<br>The state to check in. | `army_manpower_in_state = {`<br>`    type = support`<br>`    amount > 10000`<br>`    state = 49`<br>`}` | Checks if the specified state contains the specified amount of army manpower within the state. | Battalion types are defined within `/Hearts of Iron IV/common/units/*.txt` files. Must use either > or < operators for size. | 1.6 |
| divisions_in_border_state | `size = <float>`<br>The amount to check for.<br> `type = <string>`<br>The battalion type to check for. Divisions that are majority made up of battalions in that type count. Optional, counts all divisions by default.<br> `state = <scope> / <variable>`<br>The state to check in.<br> `border_state = <scope> / <variable>`<br>The border state to check in. | `divisions_in_border_state = {`<br>`    type = infantry`<br>`    size > 10`<br>`    state = 49`<br>`    border_state = var:state`<br>`}` | Checks if the border provinces between the specified state and border state contain the specified amount of divisions. | Battalion types are defined within `/Hearts of Iron IV/common/units/*.txt` files. Must use either > or < operators for size. | 1.5 |
| num_divisions_in_states | `count = <int>`<br>The amount to check for.<br> `states = { <int> <...> <int> }`<br>The states to check in.<br> `types = { <string> <...> <string> }`<br>The battalion types to check for. Divisions that are majority made up of battalions in that type count. Optional, counts all divisions by default.<br> `exclude = { <string> <...> <string> }`<br>The sub-units to exclude from the search. Divisions that are majority made up of specified battalions are excluded. Optional, excludes no divisions by default. | `num_divisions_in_states = {`<br>`    count > 24`<br>`    states = { 550 559 271 }`<br>`    exclude = { irregular_infantry }`<br>`}` | Checks if the specified states contain enough divisions of the specified types. | Divisions and their types are defined within `/Hearts of Iron IV/common/units/*.txt` files. Can use either =, >, or < operators for count. The tooltip does not specify the states the check runs for nor the filtered types. | 1.12 |
| num_battalions_in_states | `count = <int>`<br>The amount to check for.<br> `states = { <int> <...> <int> }`<br>The states to check in.<br> `types = { <string> <...> <string> }`<br>The battalion types to check for.<br> `exclude = { <string> <...> <string> }`<br>The sub-units to exclude from the search. | `num_battalions_in_states = {`<br>`    count > 24`<br>`    states = { 550 559 271 }`<br>`    exclude = { irregular_infantry }`<br>`}` | Checks if the specified states contain enough battalions (or sub-units) of the specified types. | Battalions and their types are defined within `/Hearts of Iron IV/common/units/*.txt` files. Can use either =, >, or < operators for count. The tooltip does not specify the states the check runs for nor the filtered types. | 1.12 |
| ships_in_state_ports | `size = <float>`<br>The amount to check for.<br> `type = <string>`<br>The type to check for. Optional.<br> `state = <scope> / <variable>`<br>The state to check in.<br> | `ships_in_state_ports = {`<br>`    type = capital_ship`<br>`    size > 10`<br>`    state = 49`<br>`}` | Checks if the specified state contains the specified amount of ships, or of ships of the specified type. | Ship types are defined within `/Hearts of Iron IV/common/units/*.txt` files. Must use either > or < operators for size. | 1.0 |
| num_planes_stationed_in_regions | `value = <float>`<br>The amount to check for.<br> `regions = { <id> <...> <id> }`<br>The regions to check in.<br> | `num_planes_stationed_in_regions = {`<br>`    value > 10`<br>`    regions = { 123 321 }`<br>`}` | Checks if the current scope has the specified number of aircraft stationed within strategic regions. | Must use either =, >, or < operators for value. | 1.12 |
| has_volunteers_amount_from | `tag = <scope>`<br>The country to check for.<br> `count = <int>`<br>The amount to check for. | `has_volunteers_amount_from = {`<br>`    tag = GER`<br>`    count > 10`<br>`}` | Checks if the current scope has recieved volunteers from the specified country of the specified amounts. | Must use either > or < operators for count. | 1.0 |
| convoy_threat | `<float>`<br>The threat to compate with. | `convoy_threat > 0.5` | Checks how much the convoys are threatened. | Must use either > or < operators for count. Threat is always between 0 and 1. | 1.6 |
| has_mined | `target = <tag>`<br>The country the coast of which is mined.<br> `value <> <int>`<br>The amount of mines to compare with. | `has_mined = {`<br>`    target = POL`<br>`    value > 1000`<br>`}` | Checks if the current scope has X mines on the coast of the specified country. | Must use either > or < operators for value. | 1.6 |
| has_mines | `region = <ID>`<br>The strategic region that contains the mines.<br> `amount = <int>`<br>The amount of mines to compare with. | `has_mined = {`<br>`    target = POL`<br>`    amount = 1000`<br>`}` | Checks if the current scope has at least X mines within the specified strategic region. |  | 1.6 |
| mine_threat | `<float>`<br>The threat to compate with. | `mine_threat < 0.6` | Checks how dangerous enemy mines are. | Must use either > or < operators for count. Threat is always between 0 and 1. | 1.6 |
| has_military_industrial_organization | `<token>`<br>The id to check for. | `has_military_industrial_organization = infantry_mio_token` | Checks if the current scope has a MIO with the specified name. | Accepts variables. | 1.13 |
| has_tactic | `<tactic>`<br>The tactic to check for. | `has_tactic = tactic_masterful_blitz` | Check if the given tactic is unlocked (or active by default) for the country. |  | 1.17 |

### Doctrine <a id="Doctrine"></a>

Doctrine-related country-scoped triggers:

| Name | Parameters | Examples | Description | Notes | Version Added |
| --- | --- | --- | --- | --- | --- |
| has_any_grand_doctrine | `<string>`<br>Doctrine folder. | `has_any_grand_doctrine = land` | Checks if any grand doctrine in folder is currently active for the country. | Folders are land, naval and air. | 1.17.2 |
| has_doctrine | `<grand doctrine> / <subdoctrine>`<br>The doctrine to check for. | `has_doctrine = mobile_warfare # Grand doctrine``has_doctrine = mobile_infantry # Subdoctrine` | Checks if the given grand doctrine or subdoctrine is currently active for the country. |  | 1.17 |
| has_subdoctrine_in_track | `<track>`<br>The track to check for. | `has_subdoctrine_in_track = infantry` | Checks if any subdoctrine is currently assigned to (any instance of) the given track. |  | 1.17 |
| has_completed_subdoctrine | `<subdoctrine>`<br>The subdoctrine to check for. | `has_completed_subdoctrine = mobile_infantry` | Checks if the current country has ever completed the specified subdoctrine (even if it was later switched out). |  | 1.17 |
| has_completed_track | `<track>`<br>The track to check for. | `has_completed_track = infantry` | Checks if the given subdoctrine track has been completed |  | 1.17 |
| has_mastery | `amount = <int>`<br>The amout to check for. `track = <track>`<br>The track to check for. | `has_mastery = {`<br>`    amount = 200`<br>`    track = infantry`<br>`}` | Checks if any track of the given type has at least X mastery. |  | 1.17 |
| has_mastery_level | `amount = <int>`<br>The amount to check for. `sub_doctrine = <subdoctrine>`<br>The subdoctrine to check for. | `has_mastery_level = {`<br>`    amount = 2`<br>`    sub_doctrine = mobile_infantry`<br>`}` | Checks if the country has reached the specified number of mastery levels (rewards) for the given subdoctrine. |  | 1.17 |

### Equipment <a id="Equipment"></a>

Equipment-related country-scoped triggers:

| Name | Parameters | Examples | Description | Notes | Version Added |
| --- | --- | --- | --- | --- | --- |
| stockpile_ratio | `archetype = <string>`<br>The equipment archetype to check for.<br> `ratio = <float>`<br>The ratio of equipment to check for. | `stockpile_ratio = {`<br>`    archetype = infantry_equipment`<br>`    ratio > 0.5`<br>`}` | Checks if the current scope has stockpiled the specified equipment to the specified ratio against fielded equipment of the same type. | Must use either > or < operators for ratio. <br> For the convoy equipment which is not fielded as other equipments, ratio shall be not a percentage but a direct amount (for instance 256 convoys) | 1.5 |
| has_equipment | `<equipment> = <int> / <variable>`<br>The equipment to check for, and the amount to check for. | `has_equipment = {`<br>`    infantry_equipment_1 > 10`<br>`}` | Checks if the current scope has the specified equipment to the specified amount. | Must use either > or < operators. | 1.0 |
| has_any_license | `<bool>`<br>Boolean. | `has_any_license = yes` | Checks if the current scope has any licenses from other countries. |  | 1.0 |
| is_licensing_any_to | `<scope> / <variable>`<br>The country to check for. | `is_licensing_any_to = GER` | Checks if the current scope is licensing to the specified scope. |  | 1.0 |
| is_licensing_to | `target = <scope>`<br>The country to check for. `archetype = <string>`<br>The equipment archetype to check for. Optional.<br> **Equipment scope**<br> `type = <string>`<br>The equipment to check for. Optional.<br> `version = <int>`<br>The variant id of the equipment. Optional. | `is_licensing_to = {`<br>`    target = GER`<br>`    archetype = infantry_equipment`<br>`}``is_licensing_to = {`<br>`    target = GER`<br>`    equipment = {`<br>`        type = light_tank_equipment`<br>`        version = 1`<br>`    }`<br>`}` | Checks if the current scope is licensing the specified equipment to the specified country. |  | 1.0 |
| has_license | `from = <scope>`<br>The country to check for. `archetype = <string>`<br>The equipment archetype to check for. Optional.<br> **Equipment scope**<br> `type = <string>`<br>The equipment to check for. Optional.<br> `version = <int>`<br>The variant id of the equipment. Optional. | `has_license = {`<br>`    from = GER`<br>`    archetype = infantry_equipment`<br>`}``has_license = {`<br>`    from = GER`<br>`    equipment = {`<br>`        type = light_tank_equipment`<br>`        version = 1`<br>`    }`<br>`}` | Checks if the current scope has a license for the specified equipment from the specified country. |  | 1.0 |
| fuel_ratio | `<float> / <variable>`<br>The ratio to check with. | `fuel_ratio > 0.4` | Checks the fuel ratio of the country. | Must use either < or > operators. | 1.6 |
| has_fuel | `<int> / <variable>`<br>The amount to compare with. | `has_fuel > 400` | Checks the fuel amount of the country. | Must use either < or > operators. | 1.6 |
| has_design_based_on | `<archetype>`<br>The equipment archetype. | `has_design_based_on = light_tank_chassis` | Checks if the country has a builtable non-obsolete design based on the specified equipment archetype. | Equipment archetypes can be seen in `/Hearts of Iron IV/common/units/equipment/*`. | 1.11 |

### Intelligence <a id="Intelligence"></a>

Intelligence-related country-scoped triggers:

| Name | Parameters | Examples | Description | Notes | Version Added |
| --- | --- | --- | --- | --- | --- |
| estimated_intel_max_piercing | `tag = <scope>`<br>The country to check for.<br> `value = <int>`<br>The amount to check for. | `estimated_intel_max_piercing = {`<br>`    tag = GER`<br>`    value > 2`<br>`}` | Checks if the specified scope has the specified amount of piercing based on the current scope's intel. | Must use either > or < operators for value. | 1.0 |
| estimated_intel_max_armor | `tag = <scope>`<br>The country to check for.<br> `value = <int>`<br>The amount to check for. | `estimated_intel_max_armor = {`<br>`    tag = GER`<br>`    value > 2`<br>`}` | Checks if the specified scope has the specified amount of armor based on the current scope's intel. | Must use either > or < operators for value. | 1.0 |
| compare_intel_with | `target = <tag> / <variable>`<br>The target to compare with.<br> `civilian_intel <>= <float> / <variable>`<br>Comparison of civilian intel.<br> `army_intel <>= <float> / <variable>`<br>Comparison of army intel.<br> `navy_intel <>= <float> / <variable>`<br>Comparison of navy intel.<br> `airforce_intel <>= <float> / <variable>`<br>Comparison of airforce intel.<br> | `compare_intel_with = {`<br>`    target = POL`<br>`    civilian_intel > 0.5`<br>`    army_intel = 0`<br>`    navy_intel < 0`<br>`}` | Compares intel between 2 countries. | Can use < (in which case the current country has x less intel), >, and = (in which case it must be equal). | 1.9 |
| intel_level_over | `target = <tag> / <variable>`<br>The target to compare with.<br> `civilian_intel <>= <float> / <variable>`<br>Comparison of civilian intel.<br> `army_intel <>= <float> / <variable>`<br>Comparison of army intel.<br> `navy_intel <>= <float> / <variable>`<br>Comparison of navy intel.<br> `airforce_intel <>= <float> / <variable>`<br>Comparison of airforce intel.<br> | `intel_level_over = {`<br>`    target = POL`<br>`    civilian_intel > 0.5`<br>`    army_intel = 0`<br>`    navy_intel < 0`<br>`}` | Checks the intel level from the current country over a specified country. | Can use < (in which case the current country has x less intel), >, and = (in which case it must be equal). | 1.9 |
| has_intelligence_agency | `<boolean>`<br>The intelligence agency to check.<br> | `has_intelligence_agency = yes` | Checks if the current scope has an intelligence agency. |  | 1.9 |
| network_national_coverage | `target = <tag> / <variable>`<br>The country which is checked.<br> `value <> <float> / <variable>`<br>The value of network. | `network_national_coverage = {`<br>`    target = POL`<br>`    value < 70`<br>`}` | Checks network national coverage over a specific country. | Must use < or > for value. |  |
| network_strength | `target = <tag>`<br>The country which is checked.<br> `state = <id> / <variable>`<br>The state which is checked.<br> `value <> <float> / <variable>`<br>The strength of network. | `network_strength = {`<br>`    target = POL`<br>`    value < 70`<br>`}` | Checks network national coverage over a specific country. | Must use < or > for value. Can use either or both of target and state. | 1.9 |
| has_done_agency_upgrade | `<string>`<br>The agency upgrade to check. | `has_done_agency_upgrade = upgrade_army_department` | Checks if the current scope has the specified agency upgrade (to its highest level). |  | 1.9 |
| agency_upgrade_number | `<int> / <variable>`<br>The amount of agency upgrades to check for. | `agency_upgrade_number > 4` | Checks the number of upgrades done in the current scope's intelligence agency. | Must use either > or < operators. | 1.9 |
| decryption_progress | `target = <tag>`<br>The country to compare with.<br> `value <> <float>`<br>The value to compare. | `decryption_progress = {`<br>`    target = POL`<br>`    value < 0.5`<br>`}` | Checks the decryption progress towards a country. | Must use either > or < operators for value. | 1.9 |
| has_captured_operative | `<tag>/<bool>`<br>Country whose operative was captured/Whether an operative was captured. | `has_captured_operative = POL``has_captured_operative = yes` | Checks if the current scope has captured an operative. |  | 1.9 |
| has_finished_collecting_for_operation | `target = <tag>`<br>Country towards whom the operation is targeted.<br> `operation = <token>`<br>The operation which current scope is planning against the target. | `has_finished_collecting_for_operation = {`<br>`    target = POL`<br>`    operation = operation_infiltrate_armed_forces_navy`<br>`}` | Checks if the current scope has finished collecting resources for an operation. |  | 1.9 |
| is_preparing_operation | `target = <tag>`<br>Country towards whom the operation is targeted.<br> `operation = <token>`<br>The operation which current scope is planning against the target. Optional. | `is_preparing_operation = {`<br>`    target = POL`<br>`    operation = operation_infiltrate_armed_forces_navy`<br>`}` | Checks if the current scope is preparing an operation against the specified country. |  | 1.9 |
| is_running_operation | `target = <tag>`<br>Country towards whom the operation is targeted.<br> `operation = <token>`<br>The operation which current scope is planning against the target. Optional. | `is_running_operation = {`<br>`    target = POL`<br>`    operation = operation_infiltrate_armed_forces_navy`<br>`}` | Checks if the current scope is running an operation against the specified country. |  | 1.9 |
| num_finished_operations | `target = <tag>`<br>Country towards whom the operation is targeted.<br> `operation = <token>`<br>The operation which current scope is planning against the target. Optional. | `num_finished_operations = {`<br>`    target = POL`<br>`    operation = operation_infiltrate_armed_forces_navy`<br>`}` | Checks how many finished operations the current scope had against the specified country. |  | 1.9 |
| has_operation_token | `tag = <tag>`<br>Country towards whom the operation is targeted.<br> `token = <token>`<br>The operation token. | `has_operation_token = {`<br>`    tag = POL`<br>`    token = token_name`<br>`}` | Checks if the current scope has an operation token against an another country. |  | 1.9 |
| is_active_decryption_bonuses_enabled | `<tag>`<br>The country towards which the bonus is enabled. | `is_active_decryption_bonuses_enabled = POL` | Checks if the current scope has any decryption bonuses towards the specified country. |  | 1.9 |
| is_cryptology_department_active | `<bool>`<br>Boolean. | `is_cryptology_department_active = yes` | Checks if the current scope has a cryptology department active. |  | 1.9 |
| is_decrypting | `<tag>`<br>The country which is decrypted. | `is_decrypting = POL` | Checks if the current scope is decrypting a certain country. |  | 1.9 |
| is_fully_decrypted | `<tag>`<br>The country which is decrypted. | `is_fully_decrypted = POL` | Checks if the current scope has fully decrypted a certain country. |  | 1.9 |
| num_fake_intel_divisions | `<int>`<br>Amount of divisions. | `num_fake_intel_divisions > 10` | Checks the amount of fake intel divisions. | Must use either < or >. | 1.9 |
| num_free_operative_slots | `<int>`<br>Amount of slots. | `num_free_operative_slots > 2` | Checks the amount of free operative slots. | Must use either < or >. | 1.9 |
| num_operative_slots | `<int>`<br>Amount of slots. | `num_operative_slots > 2` | Checks the amount of operative slots. | Must use either < or >. | 1.9 |
| num_of_operatives | `<int>`<br>Amount of operatives. | `num_of_operatives > 2` | Checks the amount of operatives. | Must use either < or >. | 1.9 |

### AI <a id="AI"></a>

AI-related country-scoped triggers:

| Name | Parameters | Examples | Description | Notes | Version Added |
| --- | --- | --- | --- | --- | --- |
| ai_irrationality | `<int>`<br>The amount to check for. | `ai_irrationality > 10` | Checks if the current scope AI has the specified irrationality. | Must use either > or < operators. | 1.0 |
| ai_liberate_desire | `target = <scope>`<br>The country to check for. `count = <float>`<br>The amount to check for. | `ai_liberate_desire = {`<br>`    target = GER`<br>`    count > 1`<br>`}` | Checks if the current scope AI has the specified liberation desire towards the specified country. | Must use either > or < operators for count. | 1.0 |
| ai_has_role_division | `<string>`<br>The role to check for. | `ai_has_role_division = infantry` | Checks if the current scope AI has a division with the specified role. | Roles are defined in `/Hearts of Iron IV/common/ai_templates/*.txt` | 1.0 |
| ai_has_role_template | `<string>`<br>The role to check for. | `ai_has_role_template = armor` | Checks if the current scope AI has a division template with the specified role. | Roles are defined in `/Hearts of Iron IV/common/ai_templates/*.txt` | 1.0 |
| ai_wants_divisions | `<int>`<br>The amount to check for. | `ai_wants_divisions > 10` | Checks if the current scope AI desires the specified amount of divisions. | Must use either > or < operators. | 1.0 |
| has_template_ai_majority_unit | `<string>`<br>The unit to check for. | `has_template_ai_majority_unit = infantry` | Checks if the current scope AI has a division template mostly made up of the specified unit. |  | 1.0 |

### Characters <a id="Characters"></a>

These are character-related triggers in the country scope, not [character-scoped triggers](#Character_scope).

Character-related country-scoped triggers:

| Name | Parameters | Examples | Description | Notes | Version Added |
| --- | --- | --- | --- | --- | --- |
| can_be_country_leader | `<character>`<br>The character to check. | `can_be_country_leader = POL_character_test` | Checks if the specified character has a country leader role, active or not, and can utilise it in this country. |  | 1.11 |
| has_character | `<string>`<br>The character to check. | `has_character = my_character` | Checks if the current scope has the specified character recruited. The character does NOT need to be in power. |  | 1.11 |
| has_country_leader | `ruling_only = <bool>`(default = yes) Limit check to ruling only. <br> `character = <character_token>` (recommended criteria) The character to check for. Optional. <br>`name = <string>`<br>The name to check for. Optional. <br>`id = <int>`<br>The id to check for. Optional. <br> | `has_country_leader = {`<br>`    id = 10`<br>`}``has_country_leader = {`<br>`	character = SPR_niceto_alcala_zamora`<br>`	ruling_only = yes`<br>`}``has_country_leader = {`<br>`    name = "John Smith"`<br>`    ruling_only = yes`<br>`}` | Checks if the current scope has the specified country leader. |  | 1.3 |
| has_country_leader_ideology | <ideology> Checks the ideology of the active country leader | `has_country_leader_ideology = nazism` | Checks if the current scope's active country leader has the specified ideology. |  | 1.11 |
| has_country_leader_with_trait | `<string>`<br>The trait to check. | `has_country_leader_with_trait = champion_of_peace_1` | Checks if the leader of the country has a specific trait. |  | 1.6 |
| is_female | `<bool>`<br>Boolean. | `is_female = yes` | Checks if the current country leader is female. |  | 1.9 |
| has_unit_leader | `<int>`<br>The id to check for. | `has_unit_leader = 1` | Checks if the current scope has a unit leader with the specified id. | Only the legacy ID can be used, the character ID doesn't work. | 1.0 |
| has_scientist_specialization | `specialization = <specialization_token>`<br>Specialization. | `has_scientist_specialization = specialization_nuclear` | Checks if the country in scope has a scientist with a skill level of at least 1 in specialization. |  | 1.15 |

### Peace conferences <a id="Peace_conferences"></a>

These are not exactly peace conference-related triggers, but **those that can only be used within peace conferences**.

Peace conference-only country-scoped triggers:

| Name | Parameters | Examples | Description | Notes | Version Added |
| --- | --- | --- | --- | --- | --- |
| pc_is_winner | `<bool>`<br>Boolean. | `pc_is_winner = yes` | Checks if the current scope is a winner within the peace conference. |  | 1.12 |
| pc_is_on_winning_side | `<bool>`<br>Boolean. | `pc_is_on_winning_side = yes` | Checks if the current scope is on the winning side within the peace conference. |  | 1.12 |
| pc_is_loser | `<bool>`<br>Boolean. | `pc_is_loser = yes` | Checks if the current scope is a loser within the peace conference. |  | 1.12 |
| pc_is_untouched_loser | `<bool>`<br>Boolean. | `pc_is_untouched_loser = yes` | Checks if the current scope is an untouched loser within the peace conference. |  | 1.12 |
| pc_is_on_same_side_as | `<scope>`<br>Country to check for. | `pc_is_on_same_side_as = BHR` | Checks if the current scope is on the same side of the peace conference as the specified country. |  | 1.12 |
| pc_is_liberated | `<bool>`<br>Boolean. | `pc_is_liberated = yes` | Checks if the current scope has been liberated within the peace conference. |  | 1.12 |
| pc_is_liberated_by | `<scope>`<br>Country to check for. | `pc_is_liberated_by = BHR` | Checks if the current scope has been liberated within the peace conference by the specified country. |  | 1.12 |
| pc_is_puppeted | `<bool>`<br>Boolean. | `pc_is_puppeted = yes` | Checks if the current scope has been puppeted within the peace conference. |  | 1.12 |
| pc_is_puppeted_by | `<scope>`<br>Country to check for. | `pc_is_puppeted_by = BHR` | Checks if the current scope has been puppeted within the peace conference by the specified country. |  | 1.12 |
| pc_is_forced_government | `<bool>`<br>Boolean. | `pc_is_forced_government = yes` | Checks if the current scope has had an enforced government change within the peace conference. |  | 1.12 |
| pc_is_forced_government_by | `<scope>`<br>Country to check for. | `pc_is_forced_government_by = BHR` | Checks if the current scope has had an enforced government change within the peace conference demanded by the specified country. |  | 1.12 |
| pc_is_forced_government_to | `<ideology group>`<br>Ideology group to check for. | `pc_is_forced_government_to = democratic` | Checks if the current scope has had an enforced government change to the specified ideology group. |  | 1.12 |
| pc_total_score | `<decimal>`<br>Scope to check for. | `pc_total_score > 2400` | Checks if the current scope has the specified amount in total score within the peace conference. | Can only be used for the winning countries. | 1.12 |
| pc_current_score | `<decimal>`<br>Scope to check for. | `pc_current_score > 100` | Checks if the current scope has the specified amount in current score within the peace conference. | Can only be used for the winning countries. | 1.12 |

## Faction scope <a id="Faction_scope"></a>

Can be used in **faction** scope.

There are currently no faction-specific triggers.

## State scope <a id="State_scope"></a>

Can be used in **state** scope.

### General <a id="General_3"></a>

General state-scoped triggers:

| Name | Parameters | Examples | Description | Notes | Version Added |
| --- | --- | --- | --- | --- | --- |
| state | `<scope> / <variable>`<br>The state to check for. | `state = 10``state = var:state` | Checks if the current scope is the specified state. |  | 1.0 |
| region | `<int>`<br>The strategic region id to check for. | `region = 10` | Checks if the current scope is a state in the specified strategic region. |  | 1.0 |
| <building> (building_count_trigger) | `<int>`<br>The amount of the specified building to check for. | `arms_factory > 10` | Checks if the current scope has the specified amount of the specified building. | Must use either > or < operators. Can also be used in building scope. | 1.0 |
| free_building_slots | `building = <string>`<br>The building to check for.<br> `size = <int>`<br>The amount to check for.<br> `include_locked = <bool>`<br>Whether to include locked slots. | `free_building_slots = {`<br>`    building = arms_factory`<br>`    size > 10`<br>`    include_locked = yes`<br>`}` | Checks if the current scope has available slots for the specified amount of buildings. | Must use either > or < operators for size. | 1.0 |
| non_damaged_building_level | `building = <string>`<br>The building to check for.<br> `level = <int>`<br>The amount to check for.<br> | `non_damaged_building_level = {`<br>`    building = arms_factory`<br>`    level > 4`<br>`}` | Checks if the current scope has the specified amount of the specified buildings that are undamaged. | Must use either > or < operators for level. | 1.9 |
| any_province_building_level | `building = <string>`<br>The building to check for.<br> `limit = <int>`<br>The amount to check for.<br> **Province scope**<br> `id = <int>`<br>The province to check for.<br> `limit_to_border = <bool>`<br>Whether to limit check to border provinces. | `any_province_building_level = {`<br>`    province = {`<br>`        id = 445`<br>`        id = 494`<br>`        limit_to_border = yes`<br>`    }`<br>`    building = bunker`<br>`    level < 5`<br>`}` | Checks if the current scope has the specified provincal building at the specified amount in the specified provinces. | Must use either > or < operators for level. | 1.0 |
| has_state_flag | `<string>`<br>The flag to check for. | `has_state_flag = my_flag` | Checks if the current scope has the specified flag. |  | 1.0 |
| has_state_flag | `flag = <string>`<br>The flag to check.<br> `value = <int>`<br>The flag value to check for. Optional.<br> `date = <date>`<br>The flag creation date to check for. Optional.<br> `days = <int>`<br>The duration the flag existed for. Optional. | `has_state_flag = {`<br>`    flag = my_flag`<br>`    days > 30`<br>`    date > 1936.6.1`<br>`    value > 0`<br>`}` | Compares the specified flag's last set date, days since last set, and/or value. | If not set, the value comparison is `>0`. `value` is limited between -32768 and 32767. | 1.0 |
| state_population | `<float>`<br>The amount to check for. | `state_population > 10000` | Checks if the current scope has the specified state population. | Must use either > or < operators. | 1.0 |
| state_population_k | `<float>`<br>The amount to check for. | `state_population_k > 10` | Checks if the current scope has the specified state population in thousands. | Must use either > or < operators. | 1.0 |
| is_capital | `<bool>`<br>Boolean. | `is_capital = yes` | Checks if the current scope is a capital. |  | 1.5 |
| is_controlled_by | `<scope> / <variable>`<br>The country to check for. | `is_controlled_by = GER` | Checks if the current scope is controlled by the specified country. |  | 1.0 |
| is_fully_controlled_by | `<scope> / <variable>`<br>The country to check for. | `is_fully_controlled_by = GER` | Checks if the current scope is fully controlled by the specified country. |  | 1.5 |
| is_owned_by | `<scope> / <variable>`<br>The country to check for. | `is_owned_by = GER` | Checks if the current scope is owned by the specified country. |  | 1.0 |
| is_claimed_by | `<scope> / <variable>`<br>The country to check for. | `is_claimed_by = GER` | Checks if the current scope is claimed by the specified country. |  | 1.0 |
| is_core_of | `<scope> / <variable>`<br>The country to check for. | `is_core_of = GER` | Checks if the current scope is a core of the specified country. |  | 1.0 |
| is_owned_and_controlled_by | `<scope> / <variable>`<br>The country to check for. | `is_owned_and_controlled_by = GER` | Checks if the current scope is owned and controlled by the specified country. |  | 1.0 |
| is_demilitarized_zone | `<bool>`<br>Boolean. | `is_demilitarized_zone = yes` | Checks if the current scope is a demilitarized zone. |  | 1.0 |
| is_border_conflict | `<bool>`<br>Boolean. | `is_border_conflict = yes` | Checks if the current scope is part of a border war. |  | 1.0 |
| is_in_home_area | `<bool>`<br>Boolean. | `is_in_home_area = yes` | Checks if the current scope is connected to the capital state over land. The scope needs to be owned as well for the statement for it to be true. |  | 1.0 |
| is_coastal | `<bool>`<br>Boolean. | `is_coastal = yes` | Checks if the current scope is a coastal state. |  | 1.0 |
| is_one_state_island | `<bool>`<br>Boolean. | `is_one_state_island = yes` | Checks if the current scope is a coastal state with no adjacent land states. | An adjacent land state may be connected via a naval crossing. | 1.13 |
| is_island_state | `<bool>`<br>Boolean. | `is_island_state = yes` | Checks if the current scope is a state where every province has no land neighbour. | An adjacent land division may be connected via a naval crossing. | 1.0 |
| is_on_continent | `<string>`<br>The continent to check for. | `is_on_continent = europe` | Checks if the current scope is on the specified continent. | Continents are found in `/Hearts of Iron IV/map/continent.txt`. | 1.0 |
| is_on_same_continent_as | `<scope> / <variable>`<br>The country to check for. | `is_on_same_continent_as = FRA` | Checks if the scope state is on the same continent as the given state. The capital state is used for given country tag. | Can also be used in country scope. | 1.17 |
| impassable | `<bool>`<br>Boolean. | `impassable = yes` | Checks if the current scope is impassable. |  | 1.9.1 |
| has_state_category | `<string>`<br>The category to check for. | `has_state_category = rural` | Checks if the current scope has the specified category. | State categories are found in `/Hearts of Iron IV/common/state_category/*.txt`. | 1.0 |
| state_strategic_value | `<int>`<br>The amount to check for. | `state_strategic_value > 10` | Checks if the current scope has the specified strategic value. | Must use either > or < operators. | 1.5 |
| state_and_terrain_strategic_value | `<int>`<br>The amount to check for. | `state_and_terrain_strategic_value > 10` | Checks if the current scope has the specified state and terrain strategic value. | Must use either > or < operators. | 1.5 |
| num_owned_neighbour_states | `owner = <scope>`<br>The country to check for. `count = <int>`<br>The amount to check for. | `num_owned_neighbour_states = {`<br>`    owner = GER`<br>`    count > 2`<br>`}` | Checks if the current scope has the specified amount of neighbor states belonging to the specified country. | Must use either > or < operators for count. | 1.0 |
| distance_to | `value = <float>`<br>The distance to check for. `target = <scope>`<br>The state to compare against. | `distance_to = {`<br>`    value > 1000`<br>`    target = 49`<br>`}` | Checks if the current scope is at the specified distance from the specified state. | Must use either > or < operators for distance. | 1.0 |
| ships_in_area | `area = <int>`<br>The strategic region to check for. `size = <int>`<br>The amount to check for. | `ships_in_area = { area = 104 size > 14 }` | Checks if the current scope has the specified amount of ships in the specified strategic region. | Must use either > or < operators for count. | 1.0 |
| <resource> (resource_count_trigger) | `<int>`<br>The amount to check for. | `tungsten > 10` | Checks if the current scope has the specified amount of the specified resource. | Must use either > or < operators for amount. Can also be used in country scope. | ??? |
| has_resources_amount | `resource = <string>`<br>The resource to check for.<br> `amount = <int>`<br>The amount to check for.<br> `delivered = <bool>`<br>If specified, checks the amount after the modifiers are applied rather than the base resource value. | `has_resources_amount = {`<br>`    resource = oil`<br>`    amount > 10`<br>`    delivered = yes`<br>`}` | Checks if the current scope has the specified amount of the specified resource. | Must use either > or < operators for amount. | 1.3 |
| has_resources_rights | `receiver = <scope>`<br>The receiver of the resource rights. Mandatory if used in state scope. `resources = { <resource> <...> <resource> }`<br>Resources to check for. Optional, defaults to any if unset. | `has_resources_rights = {`<br>`  receiver = POL`<br>`  resources = { oil steel }`<br>`}` | Checks if there are any resource rights with the specified parameters. | Can be used in either state or country scope. Always returns false if the state has no resources. Can also be used in country scope. | 1.12 |
| days_since_last_strategic_bombing | `<int>`<br>The amount to compare with. | `days_since_last_strategic_bombing < 10` | Checks how many days have passed since the last strategic bombing of the state. | Must use either > or < operators. | 1.6 |
| has_railway_connection | `<scope> / <variable>`<br>The states to check. `<id>`  The provinces to check. Optional. | `has_railway_connection = {`<br>`	start_state = 10`<br>`	target_state = 90`<br>`}``has_railway_connection = {`<br>`	start_province = 402`<br>`	target_province = 9400`<br>`}` | Returns true if the states are connected by a railway. Can also check provinces. |  | 1.11 |
| can_build_railway | `<scope> / <variable>`<br>The states to check. `<id>`  The provinces to check. Optional. | `can_build_railway = {`<br>`	start_state = 10`<br>`	target_state = 90`<br>`}``can_build_railway = {`<br>`	start_province = 402`<br>`	target_province = 9400`<br>`}` | Returns true if a railway can be built between states. Can also check for provinces. |  | 1.11 |
| has_railway_level | `<scope> / <variable>`<br>The states to check. `<int>`  Railway level. | `has_railway_level = {`<br>`    	state = 114`<br>`    	level = 5`<br>`}` | Checks if a state contains a railway at or above the specified level. | Works with level 1, 2, 3, 4 or 5. Level 0 does not work. | 1.11 |
| pc_does_state_stack_demilitarized | `<bool>`<br>Boolean. | `pc_does_state_stack_demilitarized = yes` | Checks if the current scope was demilitarised during a current or previously-ended peace conference. |  | 1.12 |
| pc_does_state_stack_dismantled | `<bool>`<br>Boolean. | `pc_does_state_stack_dismantled = yes` | Checks if the current scope was dismantled during a current or previously-ended peace conference. |  | 1.12 |
| pc_is_state_claimed | `<scope>`<br>Country to check for. | `pc_is_state_claimed = yes` | Checks if the current scope was claimed by any country during the peace conference. | **Can only be used within peace conferences.** | 1.12.8 |
| pc_is_state_claimed_by | `<scope>`<br>Country to check for. | `pc_is_state_claimed_by = BHR` | Checks if the current scope was claimed by the specified country during the peace conference. Note, that "claim" in this context, while includes, is NOT limited to outright taking: forcing government, puppeting and liberating will render that trigger true as well. If one looks specifically for states taken by victors for themselves, pc_is_state_claimed_and_taken_by should be used. | **Can only be used within peace conferences.** | 1.12 |
| pc_is_state_claimed_and_taken_by | `<scope>`<br>Country to check for. | `pc_is_state_claimed_and_taken_by = SOV` | Checks if the current scope was claimed with "Take State" action (i.e. annexed) by the specified country during the peace conference. | **Can only be used within peace conferences.** |  |
| pc_is_state_outside_influence_for_winner | `<scope>`<br>Country to check for. | `pc_is_state_outside_influence_for_winner = ROOT` | Checks if the current state is outside of the influence of the specified winner country. | **Can only be used within peace conferences.** Was called pc_is_state_outside_influence_for prior to 1.12.8. | 1.12.8 |
| pc_turn | `<int>`<br>The amount of turns to check for. | `pc_turn > 20` | Compares the amount of turns that have passed during the peace conference with a number. | **Can only be used within peace conferences.** | 1.12.8 |
| can_construct_building | `<build type>`The type of building. | `can_construct_building = bunker` | Checks if the country (as ROOT) and state in scope can build a building in the state. |  | 1.15 |
| has_contested_owner | `<country> / <variable>`<br>Country to check. | `has_contested_owner = GER` | Checks if a state has the specified country as a contested owner. The trigger can be used either from a country or a state scope and accepts the other as parameter. | Can also be used in country scope. | 1.15 |

### Resistance and Compliance <a id="Resistance_and_Compliance"></a>

Resistance-related state-scoped triggers:

| Name | Parameters | Examples | Description | Notes | Version Added |
| --- | --- | --- | --- | --- | --- |
| compliance | `<int>`<br>The amount to compare with. | `compliance > 50` | Compares the compliance value of the current scope with the given value. | Must use either > or < operators. | 1.9 |
| compliance_speed | `<int>`<br>The amount to compare with. | `compliance_speed > 50` | Compares the compliance speed of the current scope with the given value. | Must use either > or < operators. | 1.9 |
| has_active_resistance | `<bool>`<br>Boolean. | `has_active_resistance = yes` | Checks if the current scope has non-zero resistance. |  | 1.9 |
| has_resistance | `<bool>`<br>Boolean. | `has_resistance = yes` | Checks if the current scope has resistance. |  | 1.9 |
| resistance | `<int>`<br>The amount to compare with. | `resistance > 50` | Compares the resistance value of the current scope with the given value. | Must use either > or < operators. | 1.9 |
| resistance_speed | `<int>`<br>The amount to compare with. | `resistance_speed > 50` | Compares the resistance speed of the current scope with the given value. | Must use either > or < operators. | 1.9 |
| resistance_target | `<int>`<br>The amount to compare with. | `resistance_target > 50` | Compares the target resistance value of the current scope with the given value. | Must use either > or < operators. | 1.9 |
| has_occupation_modifier | `<token>`<br>The occupation modifier to check. | `has_occupation_modifier = modifier_name` | Checks if the current scope has an occupation modifier, changing resistance/compliance. |  | 1.9 |
| occupation_law | `<token>`<br>The occupation law to check. | `occupation_law = law_name` | Checks if the current scope has an occupation law. | Can also be used in country scope. | 1.9 |
| occupied_country_tag | `<tag>`<br>The occupation tag to check. | `occupied_country_tag = POL` | Checks which country creates resistance. |  | 1.9 |

## Character scope <a id="Character_scope"></a>

Can be used in **Character** scope.

### General <a id="General_4"></a>

General character-scoped triggers:

| Name | Parameters | Examples | Description | Notes | Version Added |
| --- | --- | --- | --- | --- | --- |
| is_character | `<scope>`<br>Character ID. | `is_character = POL_test_character` | Checks if the current character's token matches up with the specified one. |  | 1.11 |
| can_be_country_leader | `<bool>`<br>Boolean. | `can_be_country_leader = yes` | Checks if the character in the current scope has a country leader role, active or non-active. |  | 1.11 |
| is_country_leader | `<bool>`<br>Boolean. | `is_country_leader = yes` | Checks if the character in the current scope is the active country leader. |  | 1.11 |
| is_unit_leader | `<bool>`<br>Boolean. | `is_unit_leader = yes` | Checks if the character in the current scope has an active unit leader (Army/Navy leader) role. |  | 1.11 |
| is_advisor | `<bool>`<br>Boolean. | `is_advisor = yes` | Checks if the character in the current scope has an advisor role (includes advisors/theorists/high command). |  | 1.11 |
| is_air_chief | `<bool>`<br>Boolean. | `is_air_chief = yes` | Checks if the character in the current scope is selected as an air chief. | Prior to 1.12, checked if the character had a role within the slot, regardless of being selected. | 1.11 |
| is_army_chief | `<bool>`<br>Boolean. | `is_army_chief = yes` | Checks if the character in the current scope is selected as an army chief. | Prior to 1.12, checked if the character had a role within the slot, regardless of being selected. | 1.11 |
| is_army_leader | `<bool>`<br>Boolean. | `is_army_leader = yes` | Checks if the character in the current scope has an army leader (General/Field Marshal) role. |  | 1.11 |
| is_navy_chief | `<bool>`<br>Boolean. | `is_navy_chief = yes` | Checks if the character in the current scope is selected as a navy chief. | Prior to 1.12, checked if the character had a role within the slot, regardless of being selected. | 1.11 |
| is_navy_leader | `<bool>`<br>Boolean. | `is_navy_leader = yes` | Checks if the character in the current scope has an navy leader (Admiral) role. |  | 1.11 |
| is_high_command | `<bool>`<br>Boolean. | `is_high_command = yes` | Checks if the character in the current scope is selected as high command. | Prior to 1.12, checked if the character had a role within the slot, regardless of being selected. | 1.11 |
| is_corps_commander | `<bool>`<br>Boolean. | `is_corps_commander = yes` | Checks if the character in the current scope is a corps commander. |  | 1.11 |
| is_operative | `<bool>`<br>Boolean. | `is_operative = yes` | Checks if the character in the current scope is an operative. |  | 1.11 |
| is_political_advisor | `<bool>`<br>Boolean. | `is_political_advisor = yes` | Checks if the character in the current scope is selected as a political advisor. | Prior to 1.12, checked if the character had a role within the slot, regardless of being selected. | 1.11 |
| is_theorist | `<bool>`<br>Boolean. | `is_theorist = yes` | Checks if the character in the current scope is selected as a theorist. | Prior to 1.12, checked if the character had a role within the slot, regardless of being selected. | 1.11 |
| is_character_slot | `<string>`<br>The advisor slot to check. | `is_character_slot = political_advisor` | Checks if the character in the current scope has a role within the specified character slot | Character slots are defined within `/Hearts of Iron IV/common/idea_tags/*.txt`. | 1.11 |
| has_air_ledger | `<bool>`<br>Boolean. | `has_air_ledger = yes` | Checks if the character in the current scope has an air ledger. |  | 1.11 |
| has_army_ledger | `<bool>`<br>Boolean. | `has_army_ledger = yes` | Checks if the character in the current scope has an army ledger. |  | 1.11 |
| has_navy_ledger | `<bool>`<br>Boolean. | `has_navy_ledger = yes` | Checks if the character in the current scope has an navy ledger. |  | 1.11 |
| has_character_flag | `<string>`<br>The flag to check for. | `has_character_flag = my_flag` | Checks if the current scope has the specified flag. |  | 1.11 |
| has_character_flag | `flag = <string>`<br>The flag to check.<br> `value = <int>`<br>The flag value to check for. Optional.<br> `date = <date>`<br>The flag creation date to check for. Optional.<br> `days = <int>`<br>The duration the flag existed for. Optional. | `has_character_flag = {`<br>`    flag = my_flag`<br>`    days > 30`<br>`    date > 1936.6.1`<br>`    value > 0`<br>`}` | Compares the specified flag's last set date, days since last set, and/or value. | If not set, the value comparison is `>0`. `value` is limited between -32768 and 32767. | 1.11 |
| has_trait | `<trait>`<br>The trait to check for. | `has_trait = really_good_boss` | Checks if the current scope has the specified trait. |  | 1.5 |
| has_id | `<int>`<br>The id to check for. | `has_id = 1` | Checks if the current character has the specificed ID. |  | 1.5 |

### Advisors <a id="Advisors"></a>

These triggers are to be used specifically for advisors.

Advisor-scoped triggers:

| Name | Parameters | Examples | Description | Notes | Version Added |
| --- | --- | --- | --- | --- | --- |
| is_hired_as_advisor | `<bool>`<br>Boolean.<br> | `is_hired_as_advisor = yes` | Checks if the current character is activated as an advisor in any slot. |  | 1.12.10 |
| not_already_hired_except_as | `<slot>`<br>The slot to check in. | `not_already_hired_except_as = political_advisor` | Checks if the current character is not hired, with the exception of the specified slot. |  | 1.11 |
| advisor_can_be_fired | `<bool>`<br>Boolean.<br> **OR**<br> `slot = <slot>`<br>The slot to check in. | `advisor_can_be_fired = no``advisor_can_be_fired = {`<br>`    slot = political_advisor`<br>`}` | Checks if the current character's `can_be_fired` attribute is set or not within a certain slot. | If an advisor is available in multiple slots, the long version is mandatory to use. | 1.12.8 |
| has_advisor_role | `<slot>`<br>The slot to check in. | `has_advisor_role = political_advisor` | Checks if the character in scope has an advisor role for the given slot. | Possible [advisor](<Character modding - Hearts of Iron 4 Wiki.md#Advisors>) role slots. | ??? |

### Country leaders <a id="Country_leaders"></a>

These triggers are to be used specifically for country leaders.

Country leader-scoped triggers:

| Name | Parameters | Examples | Description | Notes | Version Added |
| --- | --- | --- | --- | --- | --- |
| has_ideology | `<ideology>`<br>The sub-ideology to check for. | `has_ideology = liberalism` | Checks if the current character has the specificed sub-ideology assigned. |  | 1.11 |
| has_ideology_group | `<ideology>`<br>The ideology to check for. | `has_ideology_group = democratic` | Checks if the current character has the specificed ideology assigned. |  | 1.11 |

### Unit leaders <a id="Unit_leaders"></a>

These triggers are to be used specifically for unit leaders, i.e. generals and admirals.

Unit leader-scoped triggers:

| Name | Parameters | Examples | Description | Notes | Version Added |
| --- | --- | --- | --- | --- | --- |
| has_unit_leader_flag | `<string>`<br>The flag to check for. | `has_unit_leader_flag = my_flag` | Checks if the current scope has the specified flag. | Deprecated. Use has_character_flag instead. | 1.5 |
| has_unit_leader_flag | `flag = <string>`<br>The flag to check.<br> `value = <int>`<br>The flag value to check for. Optional.<br> `date = <date>`<br>The flag creation date to check for. Optional.<br> `days = <int>`<br>The duration the flag existed for. Optional. | `has_unit_leader_flag = {`<br>`    flag = my_flag`<br>`    days > 30`<br>`    date > 1936.6.1`<br>`    value > 0`<br>`}` | Compares the specified flag's last set date, days since last set, and/or value. | Deprecated. Use has_character_flag instead. If not set, the value comparison is `>0`. `value` is limited between -32768 and 32767. | 1.5 |
| is_leading_army | `<bool>`<br>Boolean. | `is_leading_army = yes` | Checks if the current scope is leading a single army. |  | 1.5 |
| is_leading_army_group | `<bool>`<br>Boolean. | `is_leading_army_group = yes` | Checks if the current scope is leading an army group. |  | 1.5 |
| is_leading_volunteer_group | `<tag>`<br>Country tag. | `is_leading_volunteer_group = POL` | Checks if the current scope is leading a volunteer army within the specified country. | If the target country is in a civil war, this will only be valid for one side. | 1.11 |
| is_leading_volunteer_group_with_original_country | `<tag>`<br>Country tag. | `is_leading_volunteer_group_with_original_country = POL` | Checks if the current scope is leading a volunteer army within a country of the specified original tag. | If the target country is in a civil war, this will only be valid for each side. | 1.11 |
| is_field_marshal | `<bool>`<br>Boolean. | `is_field_marshal = yes` | Checks if the current scope is a Field Marshal. |  | 1.5 |
| is_assigned | `<bool>`<br>Boolean. | `is_assigned = yes` | Checks if the current scope is an assigned unit leader. |  | 1.5 |
| can_select_trait | `<string>`<br>The trait to check for. | `can_select_trait = offensive_doctrine` | Checks if the current scope can select the specified trait. |  | 1.5 |
| has_ability | `<string>`<br>The ability to check for. | `has_ability = glider_planes` | Checks if the current scope has the specified unit leader ability. |  | 1.5 |
| skill | `<int>`<br>The amount to check for. | `skill > 1` | Checks if the current scope has a Skill above the specified amount. | Must use either > or < operators. | 1.5 |
| skill_advantage | `<int>`<br>The amount to check for. | `skill_advantage > 1` | Checks if the current scope has a Skill advantage above the specified amount in against an enemy unit leader whilst in combat. | Must use either > or < operators. | 1.5 |
| planning_skill_level | `<int>`<br>The amount to check for. | `planning_skill_level > 1` | Checks if the current scope has a Planning skill above the specified amount. | Must use either > or < operators. | 1.5 |
| logistics_skill_level | `<int>`<br>The amount to check for. | `logistics_skill_level > 1` | Checks if the current scope has a Logistics skill above the specified amount. | Must use either > or < operators. | 1.5 |
| defense_skill_level | `<int>`<br>The amount to check for. | `defense_skill_level > 1` | Checks if the current scope has a Defense skill above the specified amount. | Must use either > or < operators. | 1.5 |
| attack_skill_level | `<int>`<br>The amount to check for. | `attack_skill_level > 1` | Checks if the current scope has a Attack skill above the specified amount. | Must use either > or < operators. | 1.5 |
| average_stats | `<int>`<br>The amount to check for. | `average_stats > 5` | Checks if the current scope has an average skill above the specified amount. | Must use either > or < operators. | 1.5 |
| is_border_war | `<bool>`<br>Boolean. | `is_border_war = yes` | Checks if the current socpe is in a border war. |  | 1.5 |
| num_units | `<int>`<br>The amount to check for. | `num_units > 5` | Checks if the current scope is commanding the specified amount of divisions. | Must use either > or < operators. | 1.5 |
| is_exiled_leader | `<bool>`<br>Boolean. | `is_exiled_leader = yes` | Checks if the current scope is a general from an exiled country. |  | 1.6 |
| is_exiled_leader_from | `<tag>`<br>Country. | `is_exiled_leader_from = POL` | Checks if the current scope is a general from the specified exiled country. |  | 1.6 |
| is_female | `<bool>`<br>Boolean. | `is_female = yes` | Checks if the current scope is female. | Works for aces. | 1.9 |
| is_leading_army_in_province | `<province id>` | `is_leading_army_in_province = 1234` | Checks if the current unit leader is leading an army that has any division in a specific province |  | 1.17 |

### Operatives <a id="Operatives"></a>

These triggers only work for operatives.

Operative-scoped triggers:

| Name | Parameters | Examples | Description | Notes | Version Added |
| --- | --- | --- | --- | --- | --- |
| has_nationality | `<tag>`<br>The nationality to check. | `has_nationality = POL` | Checks if the current operative has the nationality. |  | 1.9 |
| is_operative_captured | `<bool>`<br>Boolean. | `is_operative_captured = yes` | Checks if the current scope is captured. |  | 1.9 |
| operative_leader_mission | `<token>`<br>Mission. | `operative_leader_mission = mission_name` | Checks if the current scope is on the given mission. |  | 1.9 |
| operative_leader_operation | `<token>`<br>Operation. | `operative_leader_operation = operation_name` | Checks if the current scope is on the given operation. |  | 1.9 |

### Scientists <a id="Scientists"></a>

These triggers only work for scientists.

Scientist-scoped triggers:

| Name | Parameters | Examples | Description | Notes | Version Added |
| --- | --- | --- | --- | --- | --- |
| has_scientist_level | `level = <int>`<br>Level to check. `specialization = <specialization_token>`<br>Specialization. | `has_scientist_level = {`<br>`  level > 2`<br>`  specialization = specialization_nuclear`<br>`}` | Checks if the scientist of the character in scope matches the skill level condition for a specialization. Supports < > = operators. |  | 1.15 |
| is_active_scientist | `<bool>`<br> | `is_scientist_active = yes` | Checks if the scientist of the character in scope is assigned to a project. |  | 1.15 |
| is_scientist_injured | `<bool>`<br> | `is_scientist_injured = yes` | Checks if the scientist of the character in scope is injured. |  | 1.15 |

## Combat <a id="Combat"></a>

These triggers are used within the combatant scope. Some trigger blocks in abilities, combat tactics, and unit leader traits check this, and it's impossible to access elsewhere.

Combatant-scoped triggers:

| Name | Parameters | Examples | Description | Notes | Version Added |
| --- | --- | --- | --- | --- | --- |
| hardness | `<float>`<br>The amount to check for. | `hardness > 0.5` | Checks if the current scope has the specified amount of hardness. | Must use either > or < operators. | 1.0 |
| armor | `<float>`<br>The amount to check for. | `armor > 0.5` | Checks if the current scope has the specified amount of armor units. | Must use either > or < operators. | 1.0 |
| dig_in | `<float>`<br>The amount to check for. | `dig_in > 0.5` | Checks if the current scope has the specified amount of Dig In bonus. | Must use either > or < operators. | 1.0 |
| min_planning | `<float>`<br>The amount to check for. | `min_planning > 0.5` | Checks if the current scope has the specified amount of planning. | Must use either > or < operators. | 1.0 |
| fastest_unit | `<float>`<br>The speed in km/h to check for. | `fastest_unit > 12` | Checks if the current scope has a unit with the specified speed. | Must use either > or < operators. | 1.0 |
| temperature | `<float>`<br>The temperature in celsius to check for. | `temperature > 20` | Checks if the current scope is in a province with a temperature above the specified amount. | Must use either > or < operators. | 1.0 |
| reserves | `<float>`<br>The amount to check for. | `reserves > 10` | Checks if the current scope has the specified amount of reserves waiting. | Must use either > or < operators. | 1.0 |
| has_combat_modifier | `<string>`<br>The modifier to check for. | `has_combat_modifier = river_crossing` | Checks if the current scope has the specified combat modifier. |  | 1.0 |
| is_fighting_in_terrain | `<string>`<br>The terrain to check for. | `is_fighting_in_terrain = desert` | Checks if the current scope is fighting in the specified terrain. |  | 1.0 |
| is_fighting_in_weather | `<string>`<br>The weather to check for.<br> **OR**<br> `{ <string> <...> <string> }`<br>The weather to check for in an OR statement. | `is_fighting_in_weather = sandstorm``is_fighting_in_weather = { rain_light rain_heavy }` | Checks if the current scope is fighting in the specified weather. |  | 1.0 |
| phase | `<bool>`<br>Boolean. | `phase = yes` | Checks if the current scope is in phase. |  | 1.0 |
| recon_advantage | `<bool>`<br>Boolean. | `recon_advantage > 0` | Checks if the current scope has x recon advantage. |  | 1.0 |
| night | `<bool>`<br>Boolean. | `night = yes` | Checks if the current scope is fighting at night. |  | 1.0 |
| frontage_full | `<bool>`<br>Boolean. | `frontage_full = yes` | Checks if the current scope has a full combat width. |  | 1.0 |
| has_flanked_opponent | `<bool>`<br>Boolean. | `has_flanked_opponent = yes` | Checks if the current scope has flanked their opponent. |  | 1.0 |
| has_max_planning | `<bool>`<br>Boolean. | `has_max_planning = yes` | Checks if the current scope has the maximum planning bonus. |  | 1.0 |
| has_reserves | `<bool>`<br>Boolean. | `has_reserves = yes` | Checks if the current scope has any reserves waiting. |  | 1.0 |
| is_amphibious_invasion | `<bool>`<br>Boolean. | `is_amphibious_invasion = yes` | Checks if the current scope is performing an amphibious invasion. |  | 1.0 |
| is_attacker | `<bool>`<br>Boolean. | `is_attacker = yes` | Checks if the current scope is attacking. |  | 1.0 |
| is_defender | `<bool>`<br>Boolean. | `is_defender = yes` | Checks if the current scope is defending. |  | 1.0 |
| is_winning | `<bool>`<br>Boolean. | `is_winning = yes` | Checks if the current scope is winning their battle. |  | 1.0 |
| is_fighting_air_units | `<bool>`<br>Boolean. | `is_fighting_air_units = yes` | Checks if the current scope is fighting air units. |  | 1.0 |
| less_combat_width_than_opponent | `<bool>`<br>Boolean. | `less_combat_width_than_opponent = yes` | Checks if the current scope is fighting with less combat width than their opponent. |  | 1.0 |
| has_carrier_airwings_on_mission | `<bool>`<br>Boolean. | `has_carrier_airwings_on_mission = yes` | Checks if the current scope has carrier airwings on a mission. |  | 1.0 |
| has_carrier_airwings_in_own_combat | `<bool>`<br>Boolean. | `has_carrier_airwings_in_own_combat = yes` | Checks if the current scope has carrier airwings in their own combat. |  | 1.0 |
| has_artillery_ratio | `<float>`<br> | `has_artillery_ratio > 0.1` | Check that ratio of atrillery battalions in the composition of a side of combating troops are over a certain level. |  | ??? |
| has_unit_type | `<unit_type>`<br> | `has_unit_type = amphibious_mechanized` | Check if the combatant has at least one of the provided unit types. |  | ??? |

## Division scope <a id="Division_scope"></a>

Can be used in **Division** scope.

Division-scoped triggers:

| Name | Parameters | Examples | Description | Notes | Version Added |
| --- | --- | --- | --- | --- | --- |
| division_has_majority_template | `<battalion>`<br>Battalion to check for. | `division_has_majority_template = light_armor` | Checks if the current scope is majority made up of the specified battalion. | Battalions are defined within `/Hearts of Iron IV/common/units/*.txt` files. | 1.12 |
| division_has_battalion_in_template | `<battalion>`<br>Battalion to check for. | `division_has_battalion_in_template = light_armor` | Checks if the current scope has any battalions of the type in the template. | Battalions are defined within `/Hearts of Iron IV/common/units/*.txt` files. | 1.12 |
| unit_strength | `<float>`<br>The amount to check for. | `unit_strength < 0.3` | Checks the current strength of the unit on the scale from 0 to 1. | Must use either the < or > operator. | 1.12 |
| unit_organization | `<float>`<br>The amount to check for. | `unit_organization < 0.3` | Checks the current organisation of the unit on the scale from 0 to 1. | Must use either the < or > operator. | 1.12 |
| is_unit_template_reserves | `<bool>`<br>Boolean. | `is_unit_template_reserves = yes` | Checks if the current division has the supply priority set to 'Reserves', i.e. the lowest priority. | Must use either the < or > operator. | 1.12 |
| has_officer_name | `<string>`<br>The localization key to check. | `has_officer_name = FIN_nikke_parmi` | Checks if the current division has an officer with the provided name key. |  |  |

## MIO scope <a id="MIO_scope"></a>

Can be used in **Military-industrial organisation** scope.

MIO-scoped triggers:

| Name | Parameters | Examples | Description | Notes | Version Added |
| --- | --- | --- | --- | --- | --- |
| is_military_industrial_organization | `<token>`<br>MIO to check. | `is_military_industrial_organization = my_mio_token` | Checks if the currently-scoped MIO matches the input token. |  | 1.13 |
| is_mio_visible | `<bool>`<br>Boolean. | `is_mio_visible = yes` | Checks if the currently-scoped MIO is visible. |  | 1.13 |
| is_mio_available | `<bool>`<br>Boolean. | `is_mio_available = yes` | Checks if the currently-scoped MIO is visible. |  | 1.13 |
| is_mio_assigned_to_task | `<bool>`<br>Boolean. | `is_mio_assigned_to_task = yes` | Checks if the currently-scoped MIO is assigned to a task. |  | 1.13 |
| has_mio_size | `<int>`<br>Integer. | `has_mio_size > 3` | Checks the size of the MIO. | Accepts [variables](<Data structures - Hearts of Iron 4 Wiki.md>). May use < or >. | 1.13 |
| has_mio_trait | `<token>`<br>Trait to check.<br> **OR**<br> `trait = <token>`<br>Trait to check. | `has_mio_trait = my_trait_token``has_mio_trait = {`<br>`    token = my_trait_token`<br>`}` | Checks whether the MIO has the target trait in its list. |  | 1.13 |
| is_mio_trait_available | `<token>`<br>Trait to check.<br> **OR**<br> `trait = <token>`<br>Trait to check.<br> `check_mio_parent_completed = <bool>`<br>Whether to check if the parent traits are complete. True by default. `check_mio_mutually_exclusive = <bool>`<br>Whether to check if any mutually exclusive traits are complete. True by default. | `is_mio_trait_available = my_trait_token``is_mio_trait_available = {`<br>`    token = my_trait_token`<br>`    check_mio_parent_completed = no`<br>`}` | Checks whether the MIO has the target trait in its list and whether it's available. |  | 1.13 |
| is_mio_trait_completed | `<token>`<br>Trait to check.<br> **OR**<br> `trait = <token>`<br>Trait to check. | `is_mio_trait_completed = my_trait_token``is_mio_trait_completed = {`<br>`    token = my_trait_token`<br>`}` | Checks whether the MIO has the target trait in its list and whether it's completed. |  | 1.13 |
| has_mio_number_of_completed_traits | `<int>`<br>Integer. | `has_mio_number_of_completed_traits < 2` | Checks the amount of unlocked MIO traits. | Accepts [variables](<Data structures - Hearts of Iron 4 Wiki.md>). May use < or >. | 1.13 |
| has_mio_flag | `<string>`<br>The flag to check. | `has_mio_flag = my_flag` | Checks if the current scope has the specified flag. |  | 1.13 |
| has_mio_flag | `flag = <string>`<br>The flag to check.<br> `value = <int>`<br>The flag value to check for. Optional.<br> `date = <date>`<br>The flag creation date to check for. Optional.<br> `days = <int>`<br>The duration the flag existed for. Optional. | `has_mio_flag = {`<br>`    flag = my_flag`<br>`    days > 30`<br>`    date > 1936.6.1`<br>`    value > 0`<br>`}` | Compares the specified flag's last set date, days since last set, and/or value. | If not set, the value comparison is `>0`. `value` is limited between -32768 and 32767. | 1.13 |
| has_mio_policy | `<token>`<br>Policy to check. | `has_mio_policy = my_policy_token` | Checks if the currently-scoped MIO has the target policy allowed. |  | 1.13 |
| has_mio_policy_active | `<token>`<br>Policy to check. | `has_mio_policy_active = my_policy_token` | Checks if the currently-scoped MIO has the target policy active. |  | 1.13 |
| has_mio_research_category | `<token>`<br>Category to check. | `has_mio_research_category = my_research_category_token` | Checks if the currently-scoped MIO has the target research category. |  | 1.13 |
| has_mio_equipment_type | `<token>`<br>Type to check. | `has_mio_equipment_type = my_equipment_type_token` | Checks if the currently-scoped MIO has the target equipment types. | The possible equipment types are defined in `script_enum_equipment_bonus_type` (in `/Hearts of Iron IV/common/script_enums.txt`) and in `/Hearts of Iron IV/common/equipment_groups.txt` files. | 1.13 |

## Contract scope <a id="Contract_scope"></a>

Can be used in **purchase contract** scope.

Contract-scoped triggers:

| Name | Parameters | Examples | Description | Notes | Version Added |
| --- | --- | --- | --- | --- | --- |
| contract_contains_equipment | `<token>`<br>Type to check. | `contract_contains_equipment = infantry_equipment` | Checks if the currently-scoped purchase contract contains an equipment type. | May use equipment types, equipment archetypes, or types of equipment archetypes. | 1.13 |
| deal_completion | `<decimal>`<br>Progress to compare with. | `deal_completition > 0.6` | Checks the deal completion with the target value. | May use < or >. On the scale from 0 to 1. | 1.13 |
| seller | `<country>`<br>Country to check. | `seller = BHR` | Checks the seller in the current purchase contract. |  | 1.13 |
| buyer | `<country>`<br>Country to check. | `buyer = OMA` | Checks the buyer in the current purchase contract. |  | 1.13 |

## Special projects <a id="Special_projects"></a>

Special project-scoped triggers:

| Name | Parameters | Examples | Description | Notes | Version Added |
| --- | --- | --- | --- | --- | --- |
| has_project_flag | `<string>`<br>The flag to check for. **OR**<br> `flag = <string>`<br>The flag to check.<br> `value = <int>`<br>The flag value to check for. Optional.<br> `date = <date>`<br>The flag creation date to check for. Optional.<br> `days = <int>`<br>The duration the flag existed for. Optional. | `has_project_flag = my_flag``has_project_flag = {`<br>`  flag = my_flag`<br>`  value < 12`<br>`  date > 1936.3.25`<br>`  days > 365`<br>`}` | Check if flag has been set within the special project in scope. May checks on the value or date/days since last modified date. | If not set, the value comparison is >0. value is limited between -32768 and 32767. | 1.15 |

## Meta triggers <a id="Meta_triggers"></a>

Meta triggers are a system added with 1.6 with ![Man the Guns](media/country-creation-hearts-of-iron-4-wiki_1d4220f262__img8.png)Man the Guns[3] used in the exact same manner as [meta effects](<Effects - Hearts of Iron 4 Wiki.md#Meta_effects>): in order to tie a trigger block to a dynamic localisation entry. This is usually used in conjunction with [scripted localisation](<Localisation - Hearts of Iron 4 Wiki.md#Scripted_localisation>) for non-numerical checks. This also can serve in order to place a variable check where one is not possible.
Meta triggers work in any scope that supports triggers, including combat scope.

The following arguments go inside of a scripted trigger:

- `text = { ... }` is a trigger block used by the meta trigger. In here, any string that must be made dynamic is marked with the square brackets on each side as `[EXAMPLE]`.
- `EXAMPLE = "..."` is a string that will serve as the dynamic replacement for `[EXAMPLE]` within `text = { ... }`. This accepts [dynamic localisation](<Localisation - Hearts of Iron 4 Wiki.md#Namespaces>) to a limited degree, such as getting a variable's value with `[?var_name]` or some namespaces like `[ROOT.GetTag]`.
- `debug = yes`, if added, will add the final output in the [user directory](<Modding - Hearts of Iron 4 Wiki.md>)'s `/Hearts of Iron IV/logs/game.log` file for debugging purposes.

For example, the following can be used with has_equipment to make it depend on a variable's value:

```text
meta_trigger = {
    text = {
        has_equipment = { [EQUIPMENT_ARCHETYPE] > 100 }
    }
    EQUIPMENT_ARCHETYPE = "[GetEquipmentArchetype]"
}
```

In this case, `GetEquipmentArchetype` is [scripted localisation](<Localisation - Hearts of Iron 4 Wiki.md#Scripted_localisation>). An example definition of scripted localisation in this case is as such:

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

## Scripted triggers <a id="Scripted_triggers"></a>

Scripted triggers serve a similar purpose to functions in that they can be defined in `/Hearts of Iron IV/common/scripted_triggers/*.txt` and then used elsewhere as a shortened version. Alongside that, the game has certain base game scripted triggers that are checked directly in the game's code determining triggers for functions that cannot be changed.

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

If there are several definitions of scripted triggers with the exact same name, the game will make the scripted trigger be the one that was [evaluated later, as decided by file names and order in files](<Modding - Hearts of Iron 4 Wiki.md#Loading_files>).

### Diplomacy scripted triggers <a id="Diplomacy_scripted_triggers"></a>

Diplomacy scripted triggers fall into two mutually exclusive groups: deciding availability and deciding visibility. By default, these are defined in `/Hearts of Iron IV/common/scripted_triggers/diplomacy_scripted_triggers.txt` and `/Hearts of Iron IV/common/scripted_triggers/00_diplo_action_valid_triggers.txt` respectively. While it is possible to also use them as regular scripted triggers, they will also modify the prerequisites of being able to do a diplomatic action between 2 countries.

A diplomacy scripted trigger is identified by the naming pattern of `DIPLOMACY_<action>_ENABLE_TRIGGER` for availability, such as `DIPLOMACY_GUARANTEE_ENABLE_TRIGGER`, and `is_diplomatic_action_valid_<action>` for visibility, such as `is_diplomatic_action_valid_stage_coup`. In the base game, diplomacy scripted triggers are used to implement the game rules and add some country-specific exceptions, such as the ![Flag of United Kingdom](media/localisation-hearts-of-iron-4-wiki_0824ba8845__img2.png) United Kingdom being unable to release its colonies with the ![Man the Guns](media/country-creation-hearts-of-iron-4-wiki_1d4220f262__img8.png)Man the Guns DLC. Checking the base game's contents beforehand or copying it to the mod would ensure that the mod won't accidentally break any existing game rules.

Generally, the pattern in localisation keys used for the button usually matches up with the internal ID of a diplomatic action. If the diplomatic action doesn't already have a scripted trigger in the base game, [entirety of localisation can be searched](<Modding - Hearts of Iron 4 Wiki.md#Searching_multiple_files>) for the name of the button to find the name of the action. For example, a the English localisation entry of  `DIPLOMACY_CALL_ALLY_TITLE:0 "Call to arms"` would suggest that the diplomatic action of calling ally to war is `CALL_ALLY`.

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

- **declare_war**, for the Declare War button
- **generate_wargoal**, only affects the war goal menu by greying out the send button
- **guarantee**, for the Guarantee Independence button
- **docking_rights**, for the request docking rights button
- **offer_docking_right**, for the offer docking rights button
- **create_faction**, for the create faction button
- **assume_faction_leadership**, for the assume leadership of faction button
- **kick_from_faction**, for the kick from faction button
- **join_faction**, for the ask to join faction button
- **request_access_to_licence_production**, for the negotiate license button
- **embargo**, for the embargo button
- **send_volunteers**, only affects the sent volunteers menu by greying out the send button
- **stage_coup**, for the stage coup button
- **boost_party_popularity**, for the boost party popularity button

Within a diplomacy scripted trigger, the default scope is the country that does the trigger, while [FROM](<Scopes - Hearts of Iron 4 Wiki.md>) is the target of the action. For availability, the trigger's tooltip is shown to the player when hovering over the diplomatic action; in case of country-specific restrictions, using conditional statements can ensure that the tooltip would only be generated when needed rather than between any pair of nations.

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

### Resistance initiation triggers <a id="Resistance_initiation_triggers"></a>

The behaviour of resistance being automatically initiated is decided by the `should_initiate_resistance` scripted trigger, by default defined in `/Hearts of Iron IV/common/scripted_triggers/00_resistance_initiate_triggers.txt`. If it is unfulfilled, the resistance will never initiate unless forced via the [the force_enable_resistance effect](<Effects - Hearts of Iron 4 Wiki.md>). Likewise, the resistance will always occur if it's true unless forcefully disabled.

The scripted trigger's behaviour can be overwritten with state-specific scripted triggers, which should be named `should_initiate_resistance` with the list of state IDs suffixed at the end, separated by underscores. For example, this ensures that when a state 321 or 123 is controlled by the ![Flag of United Kingdom](media/localisation-hearts-of-iron-4-wiki_0824ba8845__img2.png) United Kingdom, resistance would get initiated if and only if they're national territory of ![Flag of France](media/cosmetic-tag-modding-hearts-of-iron-4-wiki_8daa0f4184__img3.png) France; otherwise, the normal behaviour is used:

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

### Useful scripted triggers <a id="Useful_scripted_triggers"></a>

These scripted triggers are defined in base game and might be useful to keep in the mod to cut down on the amount of code. As scripted triggers, all of these use a boolean value as argument.

Scripted triggers:

| Name | Scope | Example | Description | Notes |
| --- | --- | --- | --- | --- |
| can_ROOT_get_wargoal_on_THIS | Country | `can_ROOT_get_wargoal_on_THIS = yes` | Checks if ROOT can obtain a wargoal on the current scope. | To evaluate as true, the current scope must exist, not share a faction with ROOT, and not be a subject of ROOT. |
| is_free_or_subject_of_root | Country | `is_free_or_subject_of_root = yes` | Checks if the current scope is either independent or a subject of ROOT. |  |
| has_same_ideology | Country | `has_same_ideology = yes` | Checks if the current scope has the same ideology as ROOT. | Needs modifying if there are custom ideologies. Equivalent to `has_government = ROOT` for base game ideologies. |
| is_enemy_ideology | Country | `is_enemy_ideology = yes` | Checks if the current scope has an ideology that is considered enemy to ROOT's. | ![Communism](media/character-modding-hearts-of-iron-4-wiki_41494a4f46__img8.png)Communism, ![Democracy](media/character-modding-hearts-of-iron-4-wiki_cee5ae9645__img1.png)Democracy, and ![Fascism](media/character-modding-hearts-of-iron-4-wiki_58ea48332f__img14.png)Fascism are considered enemy to each other. |
| has_ROOT_at_least_1_div_in_current_state_scope | State | `has_ROOT_at_least_1_div_in_current_state_scope = yes` | Checks if ROOT has at least one division in the current scope. |  |
| controls_or_subject_of | State | `controls_or_subject_of = yes` | Checks if the current state is controlled by ROOT or a subject of ROOT. |  |
| is_controlled_by_ROOT_or_ally | State | `is_controlled_by_ROOT_or_ally = yes` | Checks if the current state is controlled by ROOT, a subject of ROOT, or a country in the same faction as ROOT. |  |
| owns_or_subject_of | State | `owns_or_subject_of = yes` | Checks if the current scope is owned by ROOT or a subject of ROOT. |  |

## References and notes <a id="References_and_notes"></a>

**^** **a:** Triggers are able to set and modify [temporary variables](<Data structures - Hearts of Iron 4 Wiki.md>). This temporary variable itself may be then used separately to change the game's state, such as in a MTTH block or if the trigger block is used in some [effect](<Effects - Hearts of Iron 4 Wiki.md>)'s `limit = { ... }` (most commonly [if statements](<Effects - Hearts of Iron 4 Wiki.md>) or [effect scope limits](<Scopes - Hearts of Iron 4 Wiki.md>)), though the usage of the variable to change the game's state is not a trigger by itself.

1. ↑ `[Modding]` Achievement for mods
   Tutorial to write achievements files in your mod
2. ↑ forum:1356228/#post-26361808
3. ↑ HOI4 Dev Diary - Modding and Traits

---

## Navigation

**[Modding](<Modding - Hearts of Iron 4 Wiki.md>)**

- **Documentation**: [Effects](<Effects - Hearts of Iron 4 Wiki.md>) • [Triggers](<Triggers - Hearts of Iron 4 Wiki.md>) • [Defines](<Defines - Hearts of Iron 4 Wiki.md>) • [Modifiers](<Modifiers - Hearts of Iron 4 Wiki.md>) • [List of modifiers](<List of modifiers - Hearts of Iron 4 Wiki.md>) • [Scopes](<Scopes - Hearts of Iron 4 Wiki.md>) • [Localisation](<Localisation - Hearts of Iron 4 Wiki.md>) • [On actions](<On actions - Hearts of Iron 4 Wiki.md>) • [Data structures](<Data structures - Hearts of Iron 4 Wiki.md>) • [Flags](<Data structures - Hearts of Iron 4 Wiki.md#Flags>) • [Event targets](<Data structures - Hearts of Iron 4 Wiki.md#Event_targets>) • [Country tag aliases](<Data structures - Hearts of Iron 4 Wiki.md#Country_tag_aliases>) • [Variables](<Data structures - Hearts of Iron 4 Wiki.md#Variables>) • [Arrays](<Data structures - Hearts of Iron 4 Wiki.md#Arrays>)
- **Scripting**: [Achievements](<Achievement modding - Hearts of Iron 4 Wiki.md>) • [AI](<AI modding - Hearts of Iron 4 Wiki.md>) • [AI focuses](<AI focuses - Hearts of Iron 4 Wiki.md>) • [Autonomous states](<Autonomy state modding - Hearts of Iron 4 Wiki.md>) • [Balances of power](<Balance of power modding - Hearts of Iron 4 Wiki.md>) • [Bookmarks/Scenarios](<Bookmark modding - Hearts of Iron 4 Wiki.md>) • [Game rules](<Bookmark modding - Hearts of Iron 4 Wiki.md#Game_rules>) • [Buildings](<Building modding - Hearts of Iron 4 Wiki.md>) • [Characters and traits](<Character modding - Hearts of Iron 4 Wiki.md>) • [Cosmetic tags](<Cosmetic tag modding - Hearts of Iron 4 Wiki.md>) • [Countries](<Country creation - Hearts of Iron 4 Wiki.md>) • [Divisions](<Division modding - Hearts of Iron 4 Wiki.md>) • [Decisions](<Decision modding - Hearts of Iron 4 Wiki.md>) • [Doctrines](<Doctrine modding - Hearts of Iron 4 Wiki.md>) • [Equipment](<Equipment modding - Hearts of Iron 4 Wiki.md>) • [Events](<Event modding - Hearts of Iron 4 Wiki.md>) • [Factions](<Faction modding - Hearts of Iron 4 Wiki.md>) • [Ideas](<Idea modding - Hearts of Iron 4 Wiki.md>) • [Ideologies](<Ideology modding - Hearts of Iron 4 Wiki.md>) • [Military industrial organizations](<Military industrial organization modding - Hearts of Iron 4 Wiki.md>) • [National focuses](<National focus modding - Hearts of Iron 4 Wiki.md>) • [Resources](<Resources modding - Hearts of Iron 4 Wiki.md>) • [Scripted GUI](<Scripted GUI modding - Hearts of Iron 4 Wiki.md>) • [Technologies and doctrines](<Technology modding - Hearts of Iron 4 Wiki.md>) • [Units](<Unit modding - Hearts of Iron 4 Wiki.md>)
- **Map**: [Map](<Map modding - Hearts of Iron 4 Wiki.md>) • [States](<State modding - Hearts of Iron 4 Wiki.md>) • [Supply areas](<Supply areas modding - Hearts of Iron 4 Wiki.md>) • [Strategic regions](<Strategic region modding - Hearts of Iron 4 Wiki.md>)
- **Graphical**: [Interface](<Interface modding - Hearts of Iron 4 Wiki.md>) • [Graphical assets](<Graphical asset modding - Hearts of Iron 4 Wiki.md>) • [Entities](<Entity modding - Hearts of Iron 4 Wiki.md>) • [Posteffects](<Posteffect modding - Hearts of Iron 4 Wiki.md>) • [Particles](<Particle modding - Hearts of Iron 4 Wiki.md>) • [Fonts](<Font modding - Hearts of Iron 4 Wiki.md>)
- **Cosmetic**: [Portraits](<Portrait modding - Hearts of Iron 4 Wiki.md>) • [Namelists](<Namelist modding - Hearts of Iron 4 Wiki.md>) • [Music](<Music modding - Hearts of Iron 4 Wiki.md>) • [Sound](<Sound modding - Hearts of Iron 4 Wiki.md>)
- **Other**: [Console commands](<Console commands - Hearts of Iron 4 Wiki.md>) • [Troubleshooting](<Troubleshooting - Hearts of Iron 4 Wiki.md>) • [Mod structure](<Mod structure - Hearts of Iron 4 Wiki.md>) • [Mods](<Mods - Hearts of Iron 4 Wiki.md>) • [Nudger](<Nudger - Hearts of Iron 4 Wiki.md>)
