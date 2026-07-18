# Table of contents

- [Applying a modifier](#applying-a-modifier)
  - [Tooltip modification](#tooltip-modification)
- [Dynamic modifiers](#dynamic-modifiers)
  - [Arguments](#arguments)
  - [Example](#example)
  - [Adding a dynamic modifier](#adding-a-dynamic-modifier)
- [Static modifiers](#static-modifiers)
  - [Global modifiers](#global-modifiers)
  - [Difficulty modifiers](#difficulty-modifiers)
  - [Relation modifiers](#relation-modifiers)
  - [Province modifiers](#province-modifiers)
  - [Balance of power modifiers](#balance-of-power-modifiers)
- [Modifier definitions](#modifier-definitions)
  - [Examples](#examples)
  - [Using in variables](#using-in-variables)
- [Opinion modifiers](#opinion-modifiers)
  - [Examples](#examples_2)
  - [Implementation](#implementation)
- [List of modifiers](#list-of-modifiers)
  - [Country scope](#country-scope)
    - [General](#general)
    - [Politics](#politics)
    - [Diplomacy](#diplomacy)
    - [Autonomy](#autonomy)
    - [Governments in exile](#governments-in-exile)
    - [Equipment](#equipment)
    - [Fuel and supply](#fuel-and-supply)
    - [Buildings](#buildings)
    - [Resistance and compliance](#resistance-and-compliance)
    - [Intelligence](#intelligence)
    - [Operatives](#operatives)
    - [AI](#ai)
    - [Military outside of combat](#military-outside-of-combat)
    - [MIOs](#mios)
    - [Unit leaders](#unit-leaders)
    - [General combat](#general-combat)
    - [Land combat](#land-combat)
    - [Naval invasions](#naval-invasions)
    - [Naval combat](#naval-combat)
    - [Carriers and their planes](#carriers-and-their-planes)
    - [Air combat](#air-combat)
    - [Targeted modifiers](#targeted-modifiers)
  - [State scope](#state-scope)
  - [Unit leader scope](#unit-leader-scope)
  - [Scientists scope](#scientists-scope)
  - [Strategic region scope](#strategic-region-scope)
- [Notes and references](#notes-and-references)

---

A modifier is essentially a variable used in internal calculations. However, unlike [Defines](<Defines - Hearts of Iron 4 Wiki.md>), modifiers are dynamically changeable within any modifier block. In general, modifiers are typically used to create a consistent and long-lasting effect that can be easily reversed.  
Each modifier has the exact same layout: `modifier_name = 0.1`. This adds the specified value to the modifier's total value for the scope where it is applied.<a id="ref-a"></a>[[a]](#cnote-a) For example, assuming that there are no other modifiers changing that to the country, having `political_power_gain = 0.2` and `political_power_gain = -0.05` applied to the country (potentially in different modifier blocks) will result in a total of **+0.15** political power gain above the base gain. Due to how modifiers work, **a modifier with the value of 0 will always do nothing.** This also means that negative modifiers will always work and have the opposite effect of positive modifiers.  
A modifier's current total value can be received as a variable by reading `modifier@modifier_name`, such as `set_variable = { my_var = modifier@political_power_gain }`. This works for countries and states, but for unit leaders, `unit_modifier@modifier_name` and `leader_modifier@modifier_name` is used instead.

The following are *not* modifiers, even if they are similar:

- Research bonuses allowing to grant a boost to a specific technology category. This is, instead, [an argument within ideas](<Idea modding - Hearts of Iron 4 Wiki.md#modifiers>), which can be applied in the same way for advisors, but not elsewhere.
- Equipment bonuses, such as decreasing the cost to build an equipment archetype. Similarly, this is [an argument within ideas](<Idea modding - Hearts of Iron 4 Wiki.md#modifiers>), which can be applied in the same way for advisors and country leader traits, but not elsewhere.
- Opinion modifiers, which can be applied to change the opinion (including trade influence) within countries, defined in /Hearts of Iron IV/common/opinion\_modifiers/\*.txt files.

## <a id="modifier-tokens"></a><a id="applying-a-modifier"></a>Applying a modifier

There are a large variety of ways to apply modifiers, but these are the primary ones:

- [Ideas](<Idea modding - Hearts of Iron 4 Wiki.md>) - This primarily includes but is not limited to national spirits and hidden ideas. **These are the simplest way to add a modifier to a country** by using an [effect block](<Effects - Hearts of Iron 4 Wiki.md>), such as a national focus reward, by using [add\_ideas](<Effects - Hearts of Iron 4 Wiki.md#add-ideas>) or [add\_timed\_idea](<Effects - Hearts of Iron 4 Wiki.md#add-timed-idea>). These only work for countries.
- [Dynamic modifiers](#dynamic-modifiers) - This is similar to ideas (Showing up in the same screen for countries), but they accept variables and can also be applied on states and unit leaders. **These are the primary way to add modifiers to a state.**
- Traits:
  - Country leader traits - These can be added to ideas (including advisors which function similarly) and country leaders, which'll apply on the country.
  - Unit leader traits - These can be added to unit leaders and apply effects on the leaders themselves or their units. These are the primary way to add a modifier to a unit leader.
- [Static modifiers](#static-modifiers):
  - [Global modifiers](#global-modifiers) - These are entirely hard-coded on *when* they apply, such as those used for stability and war support bonuses. However, these can be changed in *what* they apply.
  - [Provincial modifiers](#province-modifiers) - These are the primary if not the only way to apply a modifier towards a specific province.
  - [Relation modifiers](#relation-modifiers) - These are the only way to apply a targeted modifier from one country towards the other without needing to specify a specific country tag within the targeted modifier block.

Each modifier follows the same structure of being assigned a number, such as the following formatting within many blocks **that support modifiers**, such as anything listed above:

```text
modifier = { # While this is present in, for example, ideas or decisions, it's equally likely to see is modifier = { ... } being omitted entirely in other entries, such as country leader traits.
    political_power_gain = 0.1
    disabled_ideas = 1
}
```

No modifiers can have a non-numeric value, including boolean ones that must be 1 to have any effect.
Note that **modifiers do not support if statements**. The closest replica possible of one are [dynamic modifiers](#dynamic-modifiers), which allow using variables.

### <a id="tooltip-modification"></a>Tooltip modification

Modifier blocks support, within them, the `hidden_modifier = { ... }` block, which can be used to provent the modifiers within from showing up in the tooltip. Additionally, `custom_modifier_tooltip = localisation_key_tt` can be used to add a custom localisation string to appear within the localisation as one of the modifiers. In combination, this will look like the following:

```text
modifier = {
    hidden_modifier = {
        political_power_gain = 0.1
    }
    custom_modifier_tooltip = political_power_gain_tt
}
```

Custom modifiers now support dynamic commands (anything within square brackets). They were previously only usable for non-dynamic localisation

## <a id="dynamic-modifiers"></a>Dynamic modifiers

*If you want to apply a consistent modifier to a country, [it's easier to use ideas instead.](<Idea modding - Hearts of Iron 4 Wiki.md>)*

Dynamic modifiers, defined in /Hearts of Iron IV/common/dynamic\_modifiers/\*.txt files, are a type to apply modifiers that accept variables. The modifiers are updated daily, unless the [force\_update\_dynamic\_modifier effect](<Effects - Hearts of Iron 4 Wiki.md#force-update-dynamic-modifier>) is used to forcefully refresh the impact of modifiers. They can be applied to both countries and states, in case of the latter, the variable must be defined for the state, not for the country-owner or controller. They can also be applied to unit leaders.

Unlike ideas, **there is no way to reload definitions of dynamic modifiers** via debug mode or console, any changes to their definitions require a game restart to apply in-game. Additionally, due to the daily refresh of the variable check, these are more poorly optimised than ideas are. Due to this, when it's feasible to not use variables for a country-scoped dynamic modifier, it's both easier and more optimised [to use national spirits instead.](<Idea modding - Hearts of Iron 4 Wiki.md>)

The dynamic modifiers are evaluated daily for each scope. The process consists of the following:

- At the beginning of each day, each variable modifier value for each dynamic modifier is temporarily reset to 0, even if the null-coalescing operator is used to assume a different number as the default. Constant values do not get reset.
- Dynamic modifiers are then evaluated in the order that they were given to the scope with `add_dynamic_modifier`.
- The variable values inside of a dynamic modifier are assumed to be 0 until every variable inside is calculated. This includes those that rely on other modifiers, which includes the `modifier@modifier_name` game variable or MTTH variables that utilise that game variable.
- After the variables are calculated for a single dynamic modifier, the modifiers apply to the scope with the dynamic modifier and the game moves onto the next dynamic modifier added to the current scope until each one is calculated.

### <a id="arguments"></a>Arguments

- **icon** decides what is the icon used for the dynamic modifier. The icon uses a sprite defined in any /Hearts of Iron IV/interface/\*.gfx file. If the icon is not specified, it will be hidden.
- **enable** decides when exactly the dynamic modifier's modifiers apply. If the dynamic modifier is set, but the country or state it's set to does not fulfill the requirements, its effects will not apply. Optional.
- **remove\_trigger** will automatically remove the dynamic modifier upon the triggers being met. Optional.
- **attacker\_modifier** will, if set to true within a state-scoped dynamic modifier, additionally makes the modifier apply to divisions that, while not being present in the state with the dynamic modifier, are attacking an enemy located on that state. Optional, defaults to false.

Modifiers are put directly inside the dynamic modifier as a list. Non-modifier idea attributes such as `equipment_bonus` or `research_bonus` are impossible to use inside of dynamic modifiers.

### <a id="example"></a>Example

```text
dynamic_modifier_name = {
    icon = GFX_idea_unknown
    enable = { always = yes }
    remove_trigger = {
        NOT = {
            has_variable = var_name
        }
    }
    political_power_gain = var_name # Variable value
    weekly_manpower = 1000 # Constant value
    stability_factor = GER.stability_var # Checks specifically GER's variable, regardless of where the modifier is applied
}
```

### <a id="adding-a-dynamic-modifier"></a>Adding a dynamic modifier

Dynamic modifiers are added via the [add\_dynamic\_modifier effect](<Effects - Hearts of Iron 4 Wiki.md#add-dynamic-modifier>). A typical addition of a dynamic modifier looks like the following:

`add_dynamic_modifier = { modifier = dynamic_modifier_name }`

Since dynamic modifiers do not have assigned scopes, the same modifier can be assigned to either a country, a state, a unit leader, or several at once – this is decided only by where the `add_dynamic_modifier` effect is executed.

Within GUI, a dynamic modifier will take up these places if visible:

- For a country, a dynamic modifier will show up in the list of national spirits, appearing after the regular spirits.
- For a state, a dynamic modifier will show up in the special section for them in the bottom of the selected state view, marked with `dynamic_modifiers_grid` in /Hearts of Iron IV/interface/countrystateview.gui.

When adding a dynamic modifier, it is also possible to make it be timed or make it use a different scope as the variable's base. For example, the following code will apply dynamic\_modifier\_name to GER for 30 days, but the variables will be read off POL:

```text
GER = {
    add_dynamic_modifier = {
        modifier = dynamic_modifier_name
        scope = POL  # The modifier itself will be applied to GER, but the variables will be read off POL.
        days = 30
    }
}
```

In particular, assuming that dynamic\_modifier\_name is the example dynamic modifier created previously, if you do `set_variable = { POL.var_name = 0.3 }`, then the dynamic modifier assigned to GER as the result of this effect will give 0.3 daily political power gain. However, if the dynamic modifier scopes into ROOT for the variable as `political_power_gain = ROOT.var_name`, then `set_variable = { GER.var_name = 0.3 }` would be done.

A dynamic modifier is removed via [remove\_dynamic\_modifier](<Effects - Hearts of Iron 4 Wiki.md#remove-dynamic-modifier>), phrased similarly to add\_dynamic\_modifier: `remove_dynamic_modifier = { modifier = dynamic_modifier_name }`. If, when added, the dynamic modifier had a scope assigned to it, the scope will have to be specified when removing it as well.

**Modifiers that use variables will not show up in the tooltip of add\_dynamic\_modifier**, while those that are set to a static value will. While this may make the dynamic modifier appear broken when only reading the tooltip, this will not be actually the case once it gets added. In this case, [the tooltip of the effect can be changed](<Effects - Hearts of Iron 4 Wiki.md#custom-effect-tooltip>), with [the effect adding the dynamic modifier hidden](<Scopes - Hearts of Iron 4 Wiki.md#hidden-effect>).

## <a id="static-modifiers"></a>Static modifiers

Static modifiers are stored in /Hearts of Iron IV/common/modifiers/\*.txt files, where each code block within is a modifier block with the name being the ID of the static modifier. There are 5 main categories of static modifiers:

### <a id="global-modifiers"></a>Global modifiers

Global modifiers are applied by the hard-coded game features. Their names mustn't be changed, as the code uses them internally, but their effects can be edited. Examples of global modifiers are the penalty for non-core states or the effects of stability and war support.

### <a id="difficulty-modifiers"></a>Difficulty modifiers

These are applied within /Hearts of Iron IV/common/difficulty\_settings/\*.txt files. This is used in the menu to strengthen specific countries at the game's start within game rules. If there are no difficulty settings defined, the menu will not be possible to open.  
Each difficulty setting is defined as a `difficulty_setting = { ... }` block, which must lie within an overarching `difficulty_settings = { ... }` block. The following arguments can go into difficulty settings:

- `key = localisation_key` is the [localisation](<Localisation - Hearts of Iron 4 Wiki.md>) key used as the name of the difficulty setting as it shows up in the game rules menu/
- `modifier = static_modifier` sets the static modifier to be used by this difficulty setting.
- `countries = { ... }` is a whitespace-separated list of country tags for which the difficulty setting applies.
- `multiplier = 2.0` is a value by which the static modifier gets multiplied at the max value. As there are 5 levels for each difficulty rule, including 0, this gets split into quarters for each level, with the second being a quarter, the third being a half, and the fourth being three quarters.

An example of a difficulty setting file is the following:

```text
difficulty_settings = {
    difficulty_setting = {
        key = difficulty_weaken_GER
        modifier = weaken_country
        countries = { GER }
        multiplier = 2.0
    }
    difficulty_setting = {
        key = difficulty_weaken_SOV
        modifier = weaken_country
        countries = { SOV UKR BLR }
        multiplier = 2.0
    }
}
```

### <a id="relation-modifiers"></a>Relation modifiers

Not to be confused with opinion modifiers. The relation modifiers apply a targeted modifier from one country towards an another one, automatically removed when the trigger is met. ROOT is the country that the modifier is applied to and FROM is the target. An example would be:

```text
test_relation_modifier = {
	valid_relation_trigger = {
		FROM = {
			has_government = ROOT		# same ruling party as ROOT
		}
	}
	compliance_gain = 0.2				# FROM's states have 20% more compliance gain when controlled by ROOT
}
`They can be added by the add\_relation\_modifier effect, used as such:`
add_relation_modifier = {
	target = TAG
	modifier = test_relation_modifier
}
```

remove\_relation\_modifier, which works similarly, can remove them.

### <a id="province-modifiers"></a>Province modifiers

Province modifiers apply a modifier to a specific province rather than a state. They can be applied via the add\_province\_modifier effect, and removed with remove\_province\_modifier. More info on how to use these can be seen in the [effects](<Effects - Hearts of Iron 4 Wiki.md>) page.  
An example definition looks like

```text
mod_modifier = { 
	army_speed_factor = -0.5
	army_defence_factor = 0.5
	dig_in_speed_factor = 0.5
}
`Many state-scope modifiers will work in province scope as well. In order to make the GFX in GUI, you first need to edit /Hearts of Iron IV/interface/countrystateview.gui. The icon must be defined inside custom\_icon\_container, similarly to other examples. An example definition looks like`
iconType = {
	name = "<modifier name>_icon"
	spriteType = "GFX_modifiers_<modifier name>_icon"
	position = { x = 0 y = 0 }
	Orientation = "UPPER_LEFT"			
}
`The spriteType you have defined needs to be defined in /Hearts of Iron IV/interface/\*.gfx similarly to this example:`
spriteType = {
	name = "GFX_modifiers_<modifier name>_icon"
	textureFile = "gfx/interface/modifiers_<modifier name>_icon.dds"
}
```

### <a id="balance-of-power-modifiers"></a>Balance of power modifiers

Balance of power modifiers typically include within of themselves the [power\_balance\_daily](#power-balance-daily) and/or [power\_balance\_weekly](#power-balance-weekly) modifiers in order to gradually tip the balance towards one side. For example,

```text
my_bop_modifier = {
    power_balance_weekly = -0.01 # Changes by 1% each week to the left, in the range of -1 to 1.
}
`Balance of power modifiers are added via [the add\_power\_balance\_modifier effect](<Effects - Hearts of Iron 4 Wiki.md#add-power-balance-modifier>) as such:`
add_power_balance_modifier = {
    id = my_bop    # The ID of the balance of power
    modifier = my_bop_modifier # The modifier to add
}
```

[The remove\_power\_balance\_modifier effect](<Effects - Hearts of Iron 4 Wiki.md#remove-power-balance-modifier>), with the same syntax, or [remove\_all\_power\_balance\_modifiers](<Effects - Hearts of Iron 4 Wiki.md#remove-all-power-balance-modifiers>) can be used to remove these from the country.

## <a id="modifier-definitions"></a>Modifier definitions

Modifier definitions allow the creation of a custom modifier, which can be accessed as a variable when you wish to use it. After being defined, they function entirely like a new variable, being possible to read as a variable with the same `modifier@modifier_name` procedure. They will not have any effect by default and function only as a way to change the variable's value in an additive way with modifier blocks.  
Each modifier token is defined within /Hearts of Iron IV/common/modifier\_definitions/\*.txt files as a separate code block, where the name of the code block serves as the ID of the modifier definition. There are the following arguments that can go inside of it:

- `color_type = good` decides the colour of the modifier's value itself. There are three values, `good`, `bad`, and `neutral`. `neutral` is permamently yellow, while `good` turns the positive values **green** and negative values **red**. `bad` is the reversal of `good`.
- `value_type = percentage` decides the way the number will show up in the tooltip. There are the following values this argument can be set to:
  - `number` will make the exact value of the modifier show up. 0.02 will show up like "Modifier definition: 0.02".
  - `percentage` will make the modifier show up as a percentage on the scale from 0 to 1. 0.2 will show up like "Modifier token: 20%".
  - `percentage_in_hundred` will make the modifier show up as a percentage on the scale from 0 to 100. 10 will show up like "Modifier token: 10%".
  - `yes_no` shows up as a boolean: anything larger than 1 will shows up as `yes`, while 0 will show up as `no`.
- `precision = 1` decides how many numbers will be shown after the period in the tooltip. For example, if it is set to 1, the tooltip will show 0.341 as if it was 0.3. Note that the game inherently does not support more than 3 decimal numbers, so it cannot be larger than 3.
- `postfix` decides what will be added after the value of the modifier in the tooltip. Allowed values are 'none' (Default), 'days', 'hours', and 'daily'.
- `category` decides on the category of the modifier. By default, the category is 'all', which makes it be in every single category. Certain tooltips will only show modifiers if they belong to a certain category. It is possible to set multiple categories for the same modifier definition by defining them one after another.

The allowed values are 'none', 'all', 'country', 'state', 'unit\_leader', 'army', 'naval', 'air', 'peace', 'politics', 'ai', 'defensive', 'aggressive', 'war\_production', 'military\_advancements', 'military\_equipment', 'autonomy', 'government\_in\_exile', and 'intelligence\_agency'.

The modifier definition's ID is also used as the [localisation](<Localisation - Hearts of Iron 4 Wiki.md>) key needed to change the name of the modifier depending on the currently turned on language.

### <a id="examples"></a>Examples

```text
modifier_definition_example = {
	color_type = good
	value_type = number
	precision = 1
	postfix = daily
	
	category = country
	category = state
}
modifier_definition_example_2 = {
    color_type = bad
    value_type = percentage
}
```

### <a id="using-in-variables"></a>Using in variables

The function of modifier definitions is to modify the value of a game variable, which can be read by other variables. You can set a variable to be equal to the sum of all values of the same modifier token in the current scope by doing `set_variable = { var_name = modifier@modifier_token_name }`. This example will set var\_name to be equal to the total value of modifier\_token\_name.

Note that, unlike countries and states, unit leaders use leader\_modifier@modifier\_definition\_name or unit\_modifier@modifier\_definition\_name in their scopes.

Example usage of making a modifier token create civilian factories in random core states monthly, in any on action file:
| Example |
| --- |
| `on_actions = { on_monthly = { effect = { if = { limit = { check_variable = { modifier@modifier_definition_example > 0 } } for_loop_effect = { start = 0 end = modifier@modifier_definition_example random_owned_controlled_state = { limit = { is_core_of = ROOT free_building_slots = { building = industrial_complex size > 0 include_locked = no } } add_building_construction = { type = industrial_complex level = 1 instant_build = yes } } } } } } }` |

## <a id="opinion-modifiers"></a>Opinion modifiers

Despite their name, opinion modifiers are not related to modifiers in any way, instead they are used to modify the diplomatic or economic relations between a pair of countries.

The opinion modifiers are made in any /Hearts of Iron IV/common/opinion\_modifiers/\*.txt file as an entry in the `opinion_modifiers = { ... }` block, with the name of the entry being the ID of the opinion modifier. In case of there being several entries with the same ID, the one that was [evaluated later based on the filename and order in files](<Modding - Hearts of Iron 4 Wiki.md#loading-files>) will take priority, meaning that copying a base game file is never necessary in a mod.

There are the following attributes that are used in opinion modifiers:

- `trade = yes` is used to decide whether the opinion modifier changes the diplomatic relations or the trade opinion from one country to another. If unset, defaults to being false making it diplomatic.
- `value = -10` is the value of the modifier that decides by how much the diplomatic or trade opinion should change once the opinion modifier is added.
- `decay = 1` details the speed at which the opinion modifier trends towards zero monthly. Optional, defaults to the modifier not changing if unset.
- `days = 10` | `months = 2` | `years = 1` decides the time for how much the opinion modifier should last before it will get automatically removed. A month is interpreted as exactly 30 days, while a year is 365. Optional, the modifier will be permanent if neither is set.
- `min_trust = 10` | `max_trust = -10` detail the minimum and maximum value that the opinion modifier can change to. As the only non-hardcoded way to change the value of an existing opinion modifier is through decay, this can be used to limit how far it can apply.

The [localisation](<Localisation - Hearts of Iron 4 Wiki.md>) is created in any /Hearts of Iron IV/localisation/english/\*\_l\_english.yml file encoded in UTF-8 using the byte order mark (aka UTF-8-BOM), with the localisation key being the name of the modifier.

### <a id="examples_2"></a>Examples

Inside of a new /Hearts of Iron IV/common/opinion\_modifiers/\*.txt file:

```text
opinion_modifiers = {
    test_trade_modifier = {
        trade = yes
        value = -100    # Provides -100 trade opinion for 2 months
        months = 2
    }
    test_diplomatic_modifier = {
        value = 20      # Provides +20 diplomatic opinion that decays by 0.5 per month
        decay = 0.5
    }
}
`Inside of a new /Hearts of Iron IV/localisation/english/\*\_l\_english.yml file:`
l_english:
 test_trade_modifier: "Testing trade modifier"
 test_diplomatic_modifier: "Testing diplomatic modifier"
```

### <a id="implementation"></a>Implementation

New opinion modifiers can only be added using the [add\_opinion\_modifier effect](<Effects - Hearts of Iron 4 Wiki.md#add-opinion-modifier>) (or the similar [reverse\_add\_opinion\_modifier](<Effects - Hearts of Iron 4 Wiki.md#reverse-add-opinion-modifier>)) in any effect block, such as a [focus reward](<National focus modding - Hearts of Iron 4 Wiki.md#effects>), a [country history file](<Country creation - Hearts of Iron 4 Wiki.md#country-history>), or an idea's [on\_add and on\_remove](<Idea modding - Hearts of Iron 4 Wiki.md#effects>). Similarly, already applied new opinion modifiers can only be removed with [remove\_opinion\_modifier](<Effects - Hearts of Iron 4 Wiki.md#remove-opinion-modifier>). When `add_opinion_modifier` is used to apply an opinion modifier, only the country where the effect is executed will change its opinion towards the target.

There is no way to use a modifier block to directly apply an opinion modifier, but it can be simulated by adding or removing an opinion modifier at the same time the modifier block's effects are. For example, this national spirit would simulate applying an opinion modifier towards every other country that has the idea:
| Example code of a national spirit that uses opinion modifiers |
| --- |
| `ideas = { country = { idea_opinion_modifier = { on_add = { # Note: Doesn't work if the idea is added within country history or a bookmark's effect. every_other_country = { # If it's added in country history, then replicate the effects there as well. limit = { has_idea = idea_opinion_modifier } add_opinion_modifier = { target = ROOT modifier = test_diplomatic_modifier } reverse_add_opinion_modifier = { target = ROOT modifier = test_diplomatic_modifier } } } on_remove = { every_other_country = { limit = { has_idea = idea_opinion_modifier } remove_opinion_modifier = { target = ROOT modifier = test_diplomatic_modifier } ROOT = { remove_opinion_modifier = { target = PREV modifier = test_diplomatic_modifier } } } } modifier = { custom_modifier_tooltip = add_opinion_modifier_tt # Since on_add/on_remove aren't shown to the player } } } }` |

## <a id="list-of-modifiers"></a>List of modifiers

The list of modifiers may be outdated. A complete, but unsorted, list of modifiers can be found in /Hearts of Iron IV/documentation/modifiers\_documentation.html or /Hearts of Iron IV/documentation/modifiers\_documentation.md.

### <a id="country-scope"></a>Country scope

#### <a id="general"></a>General

General country-scoped modifiers:
| Name | Effects | Examples | Modifier type | Notes | Version added |
| --- | --- | --- | --- | --- | --- |
| <a id="monthly-population"></a> monthly\_population | Changes the monthly population gain in states owned by the country. | `monthly_population = 0.5` | Percentual. | Does not work with states. | 1.0 |
| <a id="nuclear-production"></a> nuclear\_production | Enables the production of nukes. | `nuclear_production = 1` | Boolean (only 1). |  | 1.0 |
| <a id="nuclear-production-factor"></a> nuclear\_production\_factor | Changes speed at which nukes are produced. | `nuclear_production_factor = 0.5` | Percentual. | Works in state scope, in which case it'll apply to the owner. | 1.0 |
| <a id="research-sharing-per-country-bonus"></a> research\_sharing\_per\_country\_bonus | Changes the bonus in research speed per country when technology sharing. | `research_sharing_per_country_bonus = 0.5` | Flat. |  | 1.3 |
| <a id="research-sharing-per-country-bonus-factor"></a> research\_sharing\_per\_country\_bonus\_factor | Changes the bonus in research speed per country when technology sharing by a percentage. | `research_sharing_per_country_bonus_factor = 0.5` | Percentual. |  | 1.3 |
| <a id="research-speed-factor"></a> research\_speed\_factor | Changes the research speed. | `research_speed_factor = 0.5` | Percentual. |  | 1.0 |
| <a id="special-project-speed-factor"></a> special\_project\_speed\_factor | Changes the speed that special projects are completed. | `special_project_speed_factor = 0.05` | Percentual. |  | 1.16 |
| <a id="local-resources-factor"></a> local\_resources\_factor | Resource extraction efficiency. Modifies the amount of available resources. | `local_resources_factor = 0.3` | Percentual. |  | 1.0 |
| <a id="surrender-limit"></a> surrender\_limit | Changes the percentage of victory points the country needs to lose control of to capitulate. | `surrender_limit = 0.1` | Percentual. | The larger, the more victory points are needed to capitulate a country. | 1.0 |
| <a id="max-surrender-limit-offset"></a> max\_surrender\_limit\_offset | Controls the maximum surrender progress of a nation. | `max_surrender_limit_offset = 0.3` | Flat. | For example, 0.4 means that the country cannot require more than 60% victory points to capitulate, no matter the surrender\_limit. | 1.9 |
| <a id="forced-surrender-limit"></a> forced\_surrender\_limit | Changes the percentage of victory points the country needs to lose control of to capitulate, bypassing the minimum or maximum. | `forced_surrender_limit = 0.1` | Percentual. | The larger, the more victory points are needed to capitulate a country. Applied after the minimum and maximum are applied, leading to making it possible to have it below 20% or above the maximum defined with max\_surrender\_limit\_offset. | 1.0 |
| <a id="country-resource-resource"></a> country\_resource\_<resource> | Directly modifies the country's resource stockpile. | `country_resource_oil = 10` | Flat. |  | 1.0 |
| <a id="country-resource-cost-resource"></a> country\_resource\_cost\_<resource> | Directly modifies the country's resource stockpile. | `country_resource_cost_aluminium = 10` | Flat. |  | 1.0 |
| resource\_trade\_cost\_bonus\_per\_factory | Modifies the country's cost to buy resources from others. | `resource_trade_cost_bonus_per_factory = 1` | Flat. | A positive value will grant more resources for the same amount of factories traded while a negative amount will do the opposite. Does not affect other countries buying resources from the one modified. | 1.16 |
| factory\_energy\_consumption | Directly modifies the country's energy usage per factory | `factory_energy_consumption = 0.1` | Percentual. |  | 1.17 |

#### <a id="politics"></a>Politics

Political country-scoped modifiers:
| Name | Effects | Examples | Modifier type | Notes | Version added |
| --- | --- | --- | --- | --- | --- |
| <a id="min-export"></a> min\_export | Changes the amount of resources to market. | `min_export = 0.5` | Flat. |  | 1.0 |
| <a id="trade-opinion-factor"></a> trade\_opinion\_factor | Makes AI more likely to purchase resources from this country. | `trade_opinion_factor = 0.5` | Percentual. |  | 1.0 |
| <a id="defensive-war-stability-factor"></a> defensive\_war\_stability\_factor | Changes the penalty to the stability invoked by participating in a defensive war. | `defensive_war_stability_factor = 0.5` | Percentual. |  | 1.0 |
| <a id="disabled-ideas"></a> disabled\_ideas | Disables manually changing ideas (including ministers and laws). | `disabled_ideas = 1` | Boolean (only 1). |  | 1.9 |
| <a id="idea-cost-factor"></a> <idea\|character slot>\_cost\_factor | Changes the cost in political power to add an idea or character within the specified slot. | `political_advisor_cost_factor = 0.5` | Percentual. | Idea slots can be found in common/idea\_tags. [Requires an idea or a character of that category to be present in an earlier-evaluated file.](<Idea modding - Hearts of Iron 4 Wiki.md#modifying-cost-of-a-category>) | 1.4 |
| <a id="idea-type-cost-factor"></a> <idea category type>\_category\_type\_cost\_factor | Changes the cost in army experience to add an idea within any of the categories with the specified type. | `air_spirit_category_type_cost_factor = 0.5` | Percentual. | Idea category definitions can be found in /Hearts of Iron IV/common/idea\_tags/\*.txt files, a type is assigned with `type = army_spirit`. | 1.10 |
| <a id="ledger-advisor-cost-factor"></a> <ledger>\_advisor\_cost\_factor | Changes the cost in political power to add an advisor assigned the specified military ledger. | `air_advisor_cost_factor = 0.5` | Percentual. | Ledgers are assigned to categories and characters in common/idea\_tags and common/ideas. Modifier works with air, army, and navy. | 1.11 |
| <a id="unit-leader-as-advisor-cp-cost-factor"></a> unit\_leader\_as\_advisor\_cp\_cost\_factor | Changes the cost in command power to turn a unit leader into an advisor. | `unit_leader_as_advisor_cp_cost_factor = 0.5` | Percentual. |  | 1.11 |
| <a id="improve-relations-maintain-cost-factor"></a> improve\_relations\_maintain\_cost\_factor | Changes the cost in political power to maintain improvement of relations. | `improve_relations_maintain_cost_factor = 0.5` | Percentual. |  | 1.4 |
| <a id="female-random-country-leader-chance"></a> female\_random\_country\_leader\_chance | Changes the chance for a randomly-generated country leader to be female. | `female_random_country_leader_chance = 0.3` | Percentual. |  | 1.0 |
| <a id="offensive-war-stability-factor"></a> offensive\_war\_stability\_factor | Modifies the stability penalty received from participating in an offensive war. | `offensive_war_stability_factor = 0.3` | Percentual. |  | 1.0 |
| <a id="party-popularity-stability-factor"></a> party\_popularity\_stability\_factor | Modifies the stability gained by the popularity of the ruling party. | `party_popularity_stability_factor = 0.3` | Percentual. |  | 1.0 |
| <a id="political-power-cost"></a> political\_power\_cost | Daily cost in political power. | `political_power_cost = 0.3` | Flat. |  | 1.0 |
| <a id="political-power-gain"></a> political\_power\_gain | Modifies daily gain in political power. | `political_power_gain = 0.3` | Flat. |  | 1.0 |
| <a id="political-power-factor"></a> political\_power\_factor | Modifies daily gain in political power by a percentage. | `political_power_factor = 0.3` | Percentual. |  | 1.0 |
| <a id="stability-factor"></a> stability\_factor | Modifies stability of the country. | `stability_factor = 0.3` | Flat. |  | 1.0 |
| <a id="stability-weekly"></a> stability\_weekly | Modifies weekly stability gain of the country. | `stability_weekly = 0.01` | Flat. |  | 1.0 |
| <a id="stability-weekly-factor"></a> stability\_weekly\_factor | Modifies weekly stability gain of the country by a percentage. | `stability_weekly_factor = 0.3` | Percentual. |  | 1.0 |
| <a id="war-stability-factor"></a> war\_stability\_factor | Modifies the stability loss caused by being at war. | `war_stability_factor = 0.3` | Percentual. |  | 1.0 |
| <a id="war-support-factor"></a> war\_support\_factor | Modifies war support of the country. | `war_support_factor = 0.3` | Flat. |  | 1.0 |
| <a id="war-support-weekly"></a> war\_support\_weekly | Modifies weekly war support gain of the country. | `war_support_weekly = 0.01` | Flat. |  | 1.0 |
| <a id="war-support-weekly-factor"></a> war\_support\_weekly\_factor | Modifies weekly war support gain of the country by a percentage. | `war_support_weekly_factor = 0.3` | Percentual. |  | 1.0 |
| <a id="weekly-casualties-war-support"></a> weekly\_casualties\_war\_support | Modifies weekly war support gain of the country depending on the casualties suffered by it. | `weekly_casualties_war_support = 0.006` | Percentual. |  | 1.12 |
| <a id="weekly-convoys-war-support"></a> weekly\_convoys\_war\_support | Modifies weekly war support gain of the country depending on the amount of its convoys that have been sunk. | `weekly_convoys_war_support = 0.006` | Percentual. |  | 1.12 |
| <a id="weekly-bombing-war-support"></a> weekly\_bombing\_war\_support | Modifies weekly war support gain of the country depending on the enemy bombing of its states. | `weekly_bombing_war_support = 0.006` | Percentual. |  | 1.12 |
| <a id="drift-defence-factor"></a> drift\_defence\_factor | Ideology drift defense. | `drift_defence_factor = 0.3` | Percentual. |  | 1.0 |
| <a id="power-balance-daily"></a> power\_balance\_daily | Pushes the power balance by a specified amount on each day. | `power_balance_daily = 0.01` | Flat. | Positive values result in it being pushed right, while negatives result in it being pushed left. | 1.12 |
| <a id="power-balance-weekly"></a> power\_balance\_weekly | Pushes the power balance by a specified amount on each week. | `power_balance_weekly = 0.01` | Flat. | Positive values result in it being pushed right, while negatives result in it being pushed left. | 1.12 |
| <a id="ideology-drift"></a> <ideology>\_drift | Daily gain of the specified ideology. | `communism_drift = 0.03` | Flat. |  | 1.0 |
| <a id="ideology-acceptance"></a> <ideology>\_acceptance | Likelihood of AI to accept offers from countries of the specified ideology. | `fascism_acceptance = 50` | Flat. |  | 1.0 |

#### <a id="diplomacy"></a>Diplomacy

Diplomatic country-scoped modifiers:
| Name | Effects | Examples | Modifier type | Notes | Version added |
| --- | --- | --- | --- | --- | --- |
| <a id="civil-war-involvement-tension"></a> civil\_war\_involvement\_tension | Changes the world tension amount necessary to intervene in an ally's civil war. | `civil_war_involvement_tension = 0.5` | Flat. |  | 1.0 |
| <a id="enemy-declare-war-tension"></a> enemy\_declare\_war\_tension | Changes the world tension required for an enemy to justify a wargoal on us. | `enemy_declare_war_tension = 0.5` | Flat. |  | 1.0 |
| <a id="enemy-justify-war-goal-time"></a> enemy\_justify\_war\_goal\_time | Changes the time required for an enemy to justify a wargoal on us. | `enemy_justify_war_goal_time = 0.5` | Percentual. | This also modifies the cost in political power. | 1.0 |
| <a id="faction-trade-opinion-factor"></a> faction\_trade\_opinion\_factor | Changes the opinion gain gained by trade between faction members. | `faction_trade_opinion_factor = 0.5` | Percentual. |  | 1.0 |
| <a id="generate-wargoal-tension"></a> generate\_wargoal\_tension | Changes the necessary tension for us to generate a wargoal. | `generate_wargoal_tension = 0.3` | Flat. |  | 1.0 |
| <a id="guarantee-cost"></a> guarantee\_cost | Cost in political power for the country to guarantee an another country. | `guarantee_cost = 0.3` | Percentual. |  | 1.4 |
| <a id="guarantee-tension"></a> guarantee\_tension | Necessary world tension for the country to guarantee an another country. | `guarantee_tension = 0.3` | Flat. |  | 1.0 |
| <a id="join-faction-tension"></a> join\_faction\_tension | Necessary world tension for the country to join a faction. | `join_faction_tension = 0.3` | Flat. |  | 1.0 |
| <a id="justify-war-goal-time"></a> justify\_war\_goal\_time | The amount of time necessary to justify a wargoal. | `justify_war_goal_time = 0.3` | Percentual. | This also modifies the cost in political power. | 1.0 |
| <a id="justify-war-goal-when-in-major-war-time"></a> justify\_war\_goal\_when\_in\_major\_war\_time | The amount of time necessary to justify a wargoal when in a war with a major country. | `justify_war_goal_when_in_major_war_time = 0.3` | Percentual. | This also modifies the cost in political power. | 1.0 |
| <a id="lend-lease-tension"></a> lend\_lease\_tension | Necessary world tension for the country to lend-lease. | `lend_lease_tension = 0.3` | Flat. |  | 1.0 |
| <a id="lend-lease-tension-with-overlord"></a> lend\_lease\_tension\_with\_overlord | Necessary world tension for the country to lend-lease to its overlord. | `lend_lease_tension_with_overlord = 0.3` | Flat. |  | 1.13 |
| <a id="opinion-gain-monthly"></a> opinion\_gain\_monthly | Changes opinion gain from the 'Improve relations' diplomatic action. | `opinion_gain_monthly = 5` | Flat. |  | 1.0 |
| <a id="opinion-gain-monthly-factor"></a> opinion\_gain\_monthly\_factor | Changes opinion gain from the 'Improve relations' diplomatic action by a percentage. | `opinion_gain_monthly_factor = 0.3` | Percentual. |  | 1.0 |
| <a id="opinion-gain-monthly-same-ideology"></a> opinion\_gain\_monthly\_same\_ideology | Changes opinion gain from the 'Improve relations' diplomatic action for countries of the same ideology. | `opinion_gain_monthly_same_ideology = 5` | Flat. |  | 1.0 |
| <a id="opinion-gain-monthly-same-ideology-factor"></a> opinion\_gain\_monthly\_same\_ideology\_factor | Changes opinion gain from the 'Improve relations' diplomatic action for countries of the same ideology by a percentage. | `opinion_gain_monthly_same_ideology_factor = 0.3` | Percentual. |  | 1.0 |
| <a id="request-lease-tension"></a> request\_lease\_tension | Necessary world tension for the country to request lend-lease. | `request_lease_tension = 0.3` | Percentual. |  | 1.9 |
| <a id="annex-cost-factor"></a> annex\_cost\_factor | Modifies the cost in victory points to annex states in peace deals. | `annex_cost_factor = 0.1` | Percentual. | Partially deprecated, please instead use common/peace\_conference/cost\_modifiers | 1.0 |
| <a id="puppet-cost-factor"></a> puppet\_cost\_factor | Modifies the cost in victory points per state to puppet countries in peace deals. | `puppet_cost_factor = 0.1` | Percentual. | Partially deprecated, please instead use common/peace\_conference/cost\_modifiers | 1.0 |
| <a id="send-volunteer-divisions-required"></a> send\_volunteer\_divisions\_required | Changes the number of divisions needed to send volunteers. | `send_volunteer_divisions_required = -0.3` | Percentual. |  | 1.0 |
| <a id="send-volunteer-factor"></a> send\_volunteer\_factor | Changes the number of divisions the country can send as volunteers by a percentage. | `send_volunteer_factor = 0.3` | Percentual. |  | 1.0 |
| <a id="send-volunteer-size"></a> send\_volunteer\_size | Changes the number of divisions the country can send as volunteers. | `send_volunteer_size = 5` | Flat. |  | 1.0 |
| <a id="send-volunteers-tension"></a> send\_volunteers\_tension | Changes the world tension necessary for the country to send volunteers. | `send_volunteers_tension = -0.1` | Percentual. |  | 1.0 |
| <a id="air-volunteer-cap"></a> air\_volunteer\_cap | Changes the amount of airforce you can send as volunteers. | `air_volunteer_cap = 100` | Flat. |  | 1.5 |
| <a id="embargo-threshold-factor"></a> embargo\_threshold\_factor | Changes the necessary world tension level in order to be able to embargo a country. | `embargo_threshold_factor = 0.2` | Percentual. |  | 1.12 |
| <a id="embargo-cost-factor"></a> embargo\_cost\_factor | Changes the cost in political power to send an embargo. | `embargo_cost_factor = 0.3` | Percentual. |  | 1.12 |

#### <a id="autonomy"></a>Autonomy

Autonomy-related country-scoped modifiers:
| Name | Effects | Examples | Modifier type | Notes | Version added |
| --- | --- | --- | --- | --- | --- |
| <a id="autonomy-gain"></a> autonomy\_gain | Daily gain of autonomy. | `autonomy_gain = 0.5` | Flat. | A positive number increase total autonomy, meaning the SUBJECT can be free faster. A negative number decrease total autonomy, meaning the OVERLORD can annex the manpower-slaves faster. | 1.3 |
| <a id="autonomy-gain-global-factor"></a> autonomy\_gain\_global\_factor | Modifies all gain of autonomy by a subject. | `autonomy_gain_global_factor = 0.5` | Percentual. |  | 1.4 |
| <a id="subjects-autonomy-gain"></a> subjects\_autonomy\_gain | Daily gain of autonomy in our subjects. | `subjects_autonomy_gain = 0.5` | Flat. |  | 1.3 |
| <a id="autonomy-gain-ll-to-overlord"></a> autonomy\_gain\_ll\_to\_overlord | Modifies gain of autonomy from lend-leasing to the overlord. | `autonomy_gain_ll_to_overlord = 0.5` | Flat. |  | 1.3 |
| <a id="autonomy-gain-ll-to-overlord-factor"></a> autonomy\_gain\_ll\_to\_overlord\_factor | Modifies gain of autonomy from lend-leasing to the overlord by a percentage. | `autonomy_gain_ll_to_overlord_factor = 0.5` | Percentual. |  | 1.3 |
| <a id="autonomy-gain-ll-to-subject"></a> autonomy\_gain\_ll\_to\_subject | Modifies loss of autonomy from lend-leasing to the subject. | `autonomy_gain_ll_to_subject = 0.5` | Flat. |  | 1.3 |
| <a id="autonomy-gain-ll-to-subject-factor"></a> autonomy\_gain\_ll\_to\_subject\_factor | Modifies loss of autonomy from lend-leasing to the subject by a percentage. | `autonomy_gain_ll_to_subject_factor = 0.5` | Percentual. |  | 1.3 |
| <a id="autonomy-gain-trade"></a> autonomy\_gain\_trade | Modifies gain of autonomy from the overlord trading with the subject. | `autonomy_gain_trade = 0.5` | Flat. |  | 1.3 |
| <a id="autonomy-gain-trade-factor"></a> autonomy\_gain\_trade\_factor | Modifies gain of autonomy from the overlord trading with the subject by a percentage. | `autonomy_gain_trade_factor = 0.5` | Percentual. |  | 1.3 |
| <a id="autonomy-gain-warscore"></a> autonomy\_gain\_warscore | Modifies gain of autonomy from the subject gaining warscore. | `autonomy_gain_warscore = 0.5` | Flat. |  | 1.3 |
| <a id="autonomy-gain-warscore-factor"></a> autonomy\_gain\_warscore\_factor | Modifies gain of autonomy from the subject gaining warscore by a percentage. | `autonomy_gain_warscore_factor = 0.5` | Percentual. |  | 1.3 |
| <a id="autonomy-manpower-share"></a> autonomy\_manpower\_share | Modifies the amount of manpower the overlord can use from the subject. | `autonomy_manpower_share = 0.5` | Percentual. |  | 1.3 |
| <a id="can-master-build-for-us"></a> can\_master\_build\_for\_us | Makes the overlord be able to build in the subject. | `can_master_build_for_us = 1` | Boolean (only 1). |  | 1.3 |
| <a id="cic-to-overlord-factor"></a> cic\_to\_overlord\_factor | Modifies the amount of the subject's civilian industry that goes to the overlord. | `cic_to_overlord_factor = 0.3` | Percentual. |  | 1.3 |
| <a id="mic-to-overlord-factor"></a> mic\_to\_overlord\_factor | Modifies the amount of the subject's military industry that goes to the overlord. | `mic_to_overlord_factor = 0.3` | Percentual. |  | 1.3 |
| <a id="extra-trade-to-overlord-factor"></a> extra\_trade\_to\_overlord\_factor | Modifies the amount of the subject's resources that the overlord can receive via trade. | `extra_trade_to_overlord_factor = 0.3` | Percentual. |  | 1.3 |
| <a id="license-subject-master-purchase-cost"></a> license\_subject\_master\_purchase\_cost | Modifies the cost of licensed production from the overlord. | `license_subject_master_purchase_cost = 0.3` | Percentual. |  | 1.4 |
| <a id="master-build-autonomy-factor"></a> master\_build\_autonomy\_factor | Modifies loss of autonomy from the overlord building in subject's states by a percentage. | `master_build_autonomy_factor = 0.3` | Percentual. |  | 1.3 |
| <a id="master-ideology-drift"></a> master\_ideology\_drift | Changes daily gain of the overlord's ideology in the country. | `master_ideology_drift = 0.03` | Flat. |  | 1.6 |
| <a id="overlord-trade-cost-factor"></a> overlord\_trade\_cost\_factor | Modifies the cost of trade between the overlord and the subject in civilian factories. | `overlord_trade_cost_factor = -0.3` | Percentual. |  | 1.3 |

#### <a id="governments-in-exile"></a>Governments in exile

Government-in-exile-related country-scoped modifiers:
| Name | Effects | Examples | Modifier type | Notes | Version added |
| --- | --- | --- | --- | --- | --- |
| <a id="dockyard-donations"></a> dockyard\_donations | Amount of dockyards donated. | `dockyard_donations = 2` | Flat. |  | 1.6 |
| <a id="industrial-factory-donations"></a> industrial\_factory\_donations | Amount of civilian factories donated. | `industrial_factory_donations = 2` | Flat. |  | 1.6 |
| <a id="military-factory-donations"></a> military\_factory\_donations | Amount of military factories donated. | `military_factory_donations = 2` | Flat. |  | 1.6 |
| <a id="exile-manpower-factor"></a> exile\_manpower\_factor | Amount of manpower given to the host country. | `exile_manpower_factor = 0.5` | Percentual. |  | 1.6 |
| <a id="exiled-government-weekly-manpower"></a> exiled\_government\_weekly\_manpower | Amount of weekly manpower given to the host country. | `exiled_government_weekly_manpower = 100` | Percentual. |  | 1.11 |
| <a id="legitimacy-daily"></a> legitimacy\_daily | Changes the amount of legitimacy gained daily. | `legitimacy_daily = 1` | Flat. |  | 1.6 |
| <a id="legitimacy-gain-factor"></a> legitimacy\_gain\_factor | Changes the amount of legitimacy gained daily by a percentage. | `legitimacy_gain_factor = 1` | Percentual. |  | 1.9 |

#### <a id="equipment"></a>Equipment

Equipment-related country-scoped modifiers:
| Name | Effects | Examples | Modifier type | Notes | Version added |
| --- | --- | --- | --- | --- | --- |
| <a id="equipment-capture"></a> equipment\_capture | Changes the combat equipment capture ratio. | `equipment_capture = 0.2` | Flat. |  | 1.0 |
| <a id="equipment-capture-factor"></a> equipment\_capture\_factor | Modifies the combat equipment capture ratio. | `equipment_capture_factor = 0.5` | Percentual. |  | 1.0 |
| <a id="equipment-conversion-speed"></a> equipment\_conversion\_speed | Changes the speed at which equipment is converted. | `equipment_conversion_speed = 0.5` | Percentual. |  | 1.0 |
| <a id="equipment-upgrade-xp-cost"></a> equipment\_upgrade\_xp\_cost | Changes the experience cost to upgrade military equipment. | `equipment_upgrade_xp_cost = 0.5` | Percentual. |  | 1.0 |
| <a id="license-purchase-cost"></a> license\_purchase\_cost | Changes the cost of licensed equipment by a percentage. | `license_purchase_cost = 0.5` | Percentual. | Can be used as a targeted modifier. | 1.4 |
| <a id="license-equipment-type-cost-factor"></a> license\_purchase\_cost\_factor | Changes the cost of licensed equipment by a percentage. | `license_purchase_cost_factor = 0.5` | Percentual. | Allowed equipment types are anti\_tank\_eq, artillery\_eq, infantry\_eq, and light\_tank\_eq. Can be used as a targeted modifier. | 1.4 |
| <a id="license-category-purchase-cost"></a> license\_purchase\_cost\_factor | Changes the cost of licensed equipment by a percentage. | `license_purchase_cost_factor = 0.5` | Percentual. | Allowed categories are air, armor, infantry, and naval. Can be used as a targeted modifier. | 1.4 |
| <a id="license-tech-difference-speed"></a> license\_tech\_difference\_speed | Changes the production penalty of licensed equipment by tech difference by a percentage. | `license_tech_difference_speed = 0.5` | Percentual. | Also allows specifying category as license\_<category>\_tech\_difference\_speed\_factor. Allowed categories are anti\_tank\_eq, artillery\_eq, infantry\_eq, and light\_tank\_eq. That's added in 1.6. Can be used as a targeted modifier. | 1.4 |
| <a id="license-production-speed"></a> license\_production\_speed | Changes the production speed of licensed equipment by a percentage. | `license_production_speed = 0.5` | Percentual. | Can be used as a targeted modifier. | 1.4 |
| <a id="license-category-production-speed-factor"></a> license\_<category>\_production\_speed\_factor | Changes the production speed of licensed equipment by a percentage. | `license_infantry_eq_production_speed_factor = 0.5` | Percentual. | Allowed categories are anti\_tank\_eq, artillery\_eq, infantry\_eq, and light\_tank\_eq. Can be used as a targeted modifier. | 1.6 |
| <a id="production-cost-max-ship-type"></a> production\_cost\_max\_<ship type> | Modifies the maximum cost of the ship type. | `production_cost_max_ship_hull_light = 0.3` | Percentual. | Allowed ship types in base game: convoy, ship\_hull\_carrier, ship\_hull\_cruiser, ship\_hull\_heavy, ship\_hull\_light, ship\_hull\_submarine | 1.6 |
| <a id="production-factory-efficiency-gain-factor"></a> production\_factory\_efficiency\_gain\_factor | Production efficiency growth. | `production_factory_efficiency_gain_factor = 0.5` | Percentual. |  | 1.0 |
| <a id="production-factory-max-efficiency-factor"></a> production\_factory\_max\_efficiency\_factor | Production efficiency cap. | `production_factory_max_efficiency_factor = 0.5` | Percentual. |  | 1.0 |
| <a id="production-factory-start-efficiency-factor"></a> production\_factory\_start\_efficiency\_factor | Production efficiency base. | `production_factory_start_efficiency_factor = 0.5` | Percentual. | These modifiers get added to the base value. So rather than a percent to the base value, they are to be understood as relative to full efficiency. | 1.0 |
| <a id="line-change-production-efficiency-factor"></a> line\_change\_production\_efficiency\_factor | Production efficiency retention. | `line_change_production_efficiency_factor = 0.3` | Percentual. |  | 1.0 |
| <a id="production-lack-of-resource-penalty-factor"></a> production\_lack\_of\_resource\_penalty\_factor | Lack of resources penalty. | `production_lack_of_resource_penalty_factor = 0.5` | Flat. |  | 1.0 |
| <a id="floating-harbor-duration"></a> floating\_harbor\_duration | Modifies the duration of floating harbours. | `floating_harbor_duration = 2` | Flat. |  | 1.11 |
| <a id="floating-harbor-range"></a> floating\_harbor\_range | Modifies the range of floating harbours. | `floating_harbor_range = 2` | Flat. |  | 1.11 |
| <a id="floating-harbor-supply"></a> floating\_harbor\_supply | Modifies the supply of floating harbours. | `floating_harbor_supply = 2` | Flat. |  | 1.11 |
| <a id="railway-gun-bombardment-factor"></a> railway\_gun\_bombardment\_factor | Modifies the bombardment of railway guns. | `railway_gun_bombardment_factor = 0.3` | Percentual. |  | 1.11 |

#### <a id="fuel-and-supply"></a>Fuel and supply

Supply-related country-scoped modifiers:
| Name | Effects | Examples | Modifier type | Notes | Version added |
| --- | --- | --- | --- | --- | --- |
| <a id="base-fuel-gain"></a> base\_fuel\_gain | Changes base daily gain of fuel. | `base_fuel_gain = 100` | Flat. |  | 1.6 |
| <a id="base-fuel-gain-factor"></a> base\_fuel\_gain\_factor | Changes base daily gain of fuel by a percentage. | `base_fuel_gain_factor = 0.5` | Percentual. |  | 1.6 |
| <a id="fuel-cost"></a> fuel\_cost | Changes hourly cost of fuel. | `fuel_cost = 100` | Flat. |  | 1.6 |
| <a id="fuel-gain"></a> fuel\_gain | Changes daily gain of fuel from our controlled oil. | `fuel_gain = 100` | Flat. |  | 1.6 |
| <a id="fuel-gain-factor"></a> fuel\_gain\_factor | Changes daily gain of fuel from our controlled oil by a percentage. | `fuel_gain_factor = 100` | Percentual. |  | 1.6 |
| <a id="fuel-gain-from-states"></a> fuel\_gain\_from\_states | Changes daily gain of fuel. | `fuel_gain_from_states = 100` | Flat. | Refineries use this modifier. | 1.6 |
| <a id="fuel-gain-factor-from-states"></a> fuel\_gain\_factor\_from\_states | Changes daily gain of fuel by a percentage. | `fuel_gain_factor_from_states = 0.5` | Percentual. | Modifies fuel gain from refineries. | 1.6 |
| <a id="max-fuel"></a> max\_fuel | Changes maximum amount of fuel you can have. | `max_fuel = 100` | Flat. |  | 1.6 |
| <a id="max-fuel-factor"></a> max\_fuel\_factor | Changes maximum amount of fuel you can have by a percentage. | `max_fuel_factor = 0.3` | Percentual. |  | 1.6 |
| <a id="army-fuel-capacity-factor"></a> army\_fuel\_capacity\_factor | Modifies how much fuel a single unit can store before running out. | `army_fuel_capacity_factor = 0.3` | Percentual. |  | 1.6 |
| <a id="army-fuel-consumption-factor"></a> army\_fuel\_consumption\_factor | Modifies the rate at which the army consumes fuel. | `army_fuel_consumption_factor = 0.3` | Percentual. |  | 1.6 |
| <a id="air-fuel-consumption-factor"></a> air\_fuel\_consumption\_factor | Modifies the rate at which the airforce consumes fuel. | `air_fuel_consumption_factor = 0.5` | Percentual. |  | 1.6 |
| <a id="navy-fuel-consumption-factor"></a> navy\_fuel\_consumption\_factor | Modifies the rate at which the navy consumes fuel. | `navy_fuel_consumption_factor = 0.3` | Percentual. |  | 1.6 |
| <a id="supply-factor"></a> supply\_factor | Modifies the total amount of supply the military has. | `supply_factor = 0.3` | Percentual. |  | 1.11 |
| <a id="supply-combat-penalties-on-core-factor"></a> supply\_combat\_penalties\_on\_core\_factor | Modifies the penalty given by low supply when the army is on a core state. | `supply_combat_penalties_on_core_factor = 0.3` | Percentual. |  | 1.11 |
| <a id="supply-consumption-factor"></a> supply\_consumption\_factor | Modifies the rate at which army consumes supply. | `supply_consumption_factor = 0.3` | Percentual. |  | 1.0 |
| <a id="no-supply-grace"></a> no\_supply\_grace | Modifies the grace period for units without supply. | `no_supply_grace = 120` | Flat. |  | 1.0 |
| <a id="out-of-supply-factor"></a> out\_of\_supply\_factor | Reduces the penalty that units take when they run out of supplies. | `out_of_supply_factor = 0.2` | Percentual. |  | 1.0 |
| <a id="attrition"></a> attrition | Modifies the army's attrition. | `attrition = 0.3` | Percentual. | Can also be used in states or provinces. | 1.0 |
| <a id="unit-upkeep-attrition-factor"></a> unit\_upkeep\_attrition\_factor | Modifies the unit upkeep. | `unit_upkeep_attrition_factor = 0.3` | Percentual. |  | 1.0 |
| <a id="naval-attrition"></a> naval\_attrition | Modifies attrition suffered by naval units. | `naval_attrition = 0.3` | Percentual. |  | 1.6 |
| <a id="heat-attrition"></a> heat\_attrition | Changes the attrition due to heat. | `heat_attrition = 0.5` | Flat. |  | 1.3 |
| <a id="heat-attrition-factor"></a> heat\_attrition\_factor | Changes the attrition due to heat by a percentage. | `heat_attrition_factor = 0.5` | Percentual. |  | 1.3 |
| <a id="winter-attrition"></a> winter\_attrition | Changes the attrition due to winter. | `winter_attrition = 0.5` | Flat. |  | 1.3 |
| <a id="winter-attrition-factor"></a> winter\_attrition\_factor | Changes the attrition due to winter by a percentage. | `winter_attrition_factor = 0.5` | Percentual. |  | 1.3 |
| <a id="extra-marine-supply-grace"></a> extra\_marine\_supply\_grace | Changes the supply grace given to marines. | `extra_marine_supply_grace = 96` | Flat. |  | 1.0 |
| <a id="extra-paratrooper-supply-grace"></a> extra\_paratrooper\_supply\_grace | Changes the supply grace given to paratroopers. | `extra_paratrooper_supply_grace = 96` | Flat. |  | 1.0 |
| <a id="special-forces-no-supply-grace"></a> special\_forces\_no\_supply\_grace | Changes the supply grace period for special forces. | `special_forces_no_supply_grace = 120` | Flat. |  | 1.0 |
| <a id="special-forces-out-of-supply-factor"></a> special\_forces\_out\_of\_supply\_factor | Changes the penalty for special forces out of supply. | `special_forces_out_of_supply_factor = 0.3` | Percentual. |  | 1.0 |
| <a id="truck-attrition"></a> truck\_attrition | Changes the attrition supply trucks suffer from. | `truck_attrition = 3` | Flat. |  | 1.11 |
| <a id="truck-attrition-factor"></a> truck\_attrition\_factor | Modifies the attrition supply trucks suffer from. | `truck_attrition_factor = 0.3` | Percentual. |  | 1.11 |

#### <a id="buildings"></a>Buildings

Building-related country-scoped modifiers:
| Name | Effects | Examples | Modifier type | Notes | Version added |
| --- | --- | --- | --- | --- | --- |
| <a id="production-speed-buildings-factor"></a> production\_speed\_buildings\_factor | Changes the construction speed of all buildings. | `production_speed_buildings_factor = 0.5` | Percentual. |  | 1.0 |
| <a id="production-speed-building-factor"></a> production\_speed\_<building>\_factor | Changes the construction speed of a specific building. | `production_speed_industrial_complex_factor = 0.5` | Percentual. |  | 1.0 |
| <a id="production-cost-building-factor"></a> production\_cost\_<building>\_factor | Changes the base cost of a specific building. | `production_cost_industrial_complex_factor = -0.1` | Percentual. | Localization is missing and must be added yourself. | Unknown |
| <a id="civilian-factory-use"></a> civilian\_factory\_use | Uses the specified amount of civilian factory as a special project. | `civilian_factory_use = 3` | Flat. |  | 1.5 |
| <a id="consumer-goods-factor"></a> consumer\_goods\_factor | Modifies the percentage of factories used for consumer goods. | `consumer_goods_factor = 0.1` | Multiplicative. | The modifier adds multiplicatively. For example, `consumer_goods_factor = 0.5` and `consumer_goods_factor = -0.5` will, in total, multiply the consumer goods value by ![{\displaystyle (1-0.5)(1+0.5)=0.5\cdot 1.5=0.75}](media/modifiers-hearts-of-iron-4-wiki_5dfb90c7fa__img9.svg). | 1.0 |
| <a id="consumer-goods-expected-value"></a> consumer\_goods\_expected\_value | Sets the baseline percentage of expected consumer goods. | `consumer_goods_expected_value = 0.1` | Flat. | Used to be only updated when the economic law was changed. Now gets updated normaly. | 1.13 |
| <a id="conversion-cost-civ-to-mil-factor"></a> conversion\_cost\_civ\_to\_mil\_factor | Changes the cost to convert civilian factories to military factories. | `conversion_cost_civ_to_mil_factor = 0.4` | Percentual. |  | 1.5 |
| <a id="conversion-cost-mil-to-civ-factor"></a> conversion\_cost\_mil\_to\_civ\_factor | Changes the cost to convert military factories to civilian factories. | `conversion_cost_mil_to_civ_factor = 0.4` | Percentual. |  | 1.5 |
| <a id="global-building-slots"></a> global\_building\_slots | Changes amount of building slots in our every state. | `global_building_slots = 1` | Flat. |  | 1.0 |
| <a id="global-building-slots-factor"></a> global\_building\_slots\_factor | Changes amount of building slots in our every state by a percentage. | `global_building_slots_factor = 0.3` | Percentual. |  | 1.0 |
| <a id="industrial-capacity-dockyard"></a> industrial\_capacity\_dockyard | Dockyard output. | `industrial_capacity_dockyard = 0.3` | Percentual. |  | 1.3.3 |
| <a id="industrial-capacity-factory"></a> industrial\_capacity\_factory | Military factory output. | `industrial_capacity_factory = 0.3` | Percentual. |  | 1.0 |
| <a id="industry-air-damage-factor"></a> industry\_air\_damage\_factor | Amount of damage our factories receive from air bombings. | `industry_air_damage_factor = 0.3` | Percentual. |  | 1.0 |
| <a id="industry-free-repair-factor"></a> industry\_free\_repair\_factor | Changes the speed at which buildings repair themselves without factories assigned. | `industry_free_repair_factor = 0.3` | Percentual. |  | 1.0 |
| <a id="industry-repair-factor"></a> industry\_repair\_factor | Changes the speed at which buildings are repaired. | `industry_repair_factor = 0.3` | Percentual. |  | 1.0 |
| <a id="production-oil-factor"></a> production\_oil\_factor | Synthetic oil gain. | `production_oil_factor = 0.5` | Percentual. |  | 1.0 |
| <a id="repair-speed-buildingf-factor"></a> repair\_speed\_<building>\_factor | Changes the repair speed of a specific building. | `repair_speed_arms_factory_factor = 0.5` | Percentual. |  | 1.0 |
| <a id="supply-node-range"></a> supply\_node\_range | Increases the effective range of supply nodes. | `supply_node_range = 0.1` | Percentual. |  | 1.11 |
| <a id="static-anti-air-damage-factor"></a> static\_anti\_air\_damage\_factor | Modifies the damage done to planes by the anti-air buildings. | `static_anti_air_damage_factor = 0.1` | Percentual. |  | 1.0 |
| <a id="static-anti-air-hit-chance-factor"></a> static\_anti\_air\_hit\_chance\_factor | Modifies the chance for the anti-air buildings to hit enemy planes. | `static_anti_air_hit_chance_factor = 0.1` | Percentual. |  | 1.0 |
| <a id="tech-air-damage-factor"></a> tech\_air\_damage\_factor | Modifies the damage done to the country's planes by enemy anti-air buildings. | `tech_air_damage_factor = 0.1` | Percentual. |  | 1.0 |
| <a id="tech-air-damage-factor"></a> tech\_air\_damage\_factor | Modifies the damage done to the country's planes by enemy anti-air buildings. | `tech_air_damage_factor = 0.1` | Percentual. |  | 1.0 |
| <a id="cic-construction-boost"></a> cic\_construction\_boost | Modifies the base construction speed from civilian factories. | `cic_construction_boost = 0.1` | Flat. |  | 1.13 |
| <a id="cic-construction-boost-factor"></a> cic\_construction\_boost\_factor | Modifies the modifier to the base construction speed from civilian factories. | `cic_construction_boost_factor = 0.1` | Percentual. |  | 1.13 |
| <a id="land-bunker-effectiveness-factor"></a> land\_bunker\_effectiveness\_factor | Modifies the effectiveness of land forts in defence. | `land_bunker_effectiveness_factor = 0.1` | Percentual. |  | 1.13 |
| <a id="coastal-bunker-effectiveness-factor"></a> coastal\_bunker\_effectiveness\_factor | Modifies the effectiveness of coastal forts in defence. | `coastal_bunker_effectiveness_factor = 0.1` | Percentual. |  | 1.13 |

#### <a id="resistance-and-compliance"></a>Resistance and compliance

Resistance-related country-scoped modifiers:
| Name | Effects | Examples | Modifier type | Notes | Version added |
| --- | --- | --- | --- | --- | --- |
| <a id="compliance-growth-on-our-occupied-states"></a> compliance\_growth\_on\_our\_occupied\_states | Changes the compliance growth speed on the country's controlled states. | `compliance_growth_on_our_occupied_states = 0.5` | Percentual. |  | 1.9 |
| <a id="no-compliance-gain"></a> no\_compliance\_gain | Disables the compliance gain on our controlled states. | `no_compliance_gain = 1` | Boolean (only 1). | Can also be used in state scope. | 1.9 |
| <a id="required-garrison-factor"></a> required\_garrison\_factor | Changes the required garrison in our occupied states. | `required_garrison_factor = 0.5` | Percentual. | Can also be used in state scope. | 1.9 |
| <a id="resistance-activity"></a> resistance\_activity | Changes the chance for resistance activity to occur on our occupied states. | `resistance_activity = 0.5` | Percentual. |  | 1.9 |
| <a id="resistance-damage-to-garrison-on-our-occupied-states"></a> resistance\_damage\_to\_garrison\_on\_our\_occupied\_states | Changes the resistance damage to the garrison in our occupied states. | `resistance_damage_to_garrison_on_our_occupied_states = 0.5` | Percentual. |  | 1.9 |
| <a id="resistance-decay-on-our-occupied-states"></a> resistance\_decay\_on\_our\_occupied\_states | Changes the resistance decay in our occupied states. | `resistance_decay_on_our_occupied_states = 0.5` | Percentual. |  | 1.9 |
| <a id="resistance-growth-on-our-occupied-states"></a> resistance\_growth\_on\_our\_occupied\_states | Changes the resistance growth speed in our occupied states. | `resistance_growth_on_our_occupied_states = 0.5` | Percentual. |  | 1.9 |
| <a id="resistance-target-on-our-occupied-states"></a> resistance\_target\_on\_our\_occupied\_states | Changes the resistance target in our occupied states. | `resistance_target_on_our_occupied_states = 0.5` | Percentual. |  | 1.9 |
| resistance\_target | Changes the resistance target in foreign states occupied by us | `resistance_target = 0.5` | Percentual |  | 1.9 |

#### <a id="intelligence"></a>Intelligence

Intelligence-related country-scoped modifiers:
| Name | Effects | Examples | Modifier type | Notes | Version added |
| --- | --- | --- | --- | --- | --- |
| <a id="agency-upgrade-time"></a> agency\_upgrade\_time | Changes the time it takes to upgrade the agency | `agency_upgrade_time = 0.5` | Percentual. |  | 1.9 |
| <a id="decryption"></a> decryption | Changes the decription capability of the country. | `decryption = 1` | Flat. | Only works with the ![La Résistance](media/modifiers-hearts-of-iron-4-wiki_5dfb90c7fa__img12.png) La Résistance DLC disabled. | 1.0 |
| <a id="decryption-factor"></a> decryption\_factor | Changes the decription capability of the country by a percentage. | `decryption_factor = 0.5` | Percentual. | Only works with the ![La Résistance](media/modifiers-hearts-of-iron-4-wiki_5dfb90c7fa__img12.png) La Résistance DLC disabled. | 1.0 |
| <a id="encryption"></a> encryption | Changes the encryption capability of the country. | `encryption = 1` | Flat. | Only works with the ![La Résistance](media/modifiers-hearts-of-iron-4-wiki_5dfb90c7fa__img12.png) La Résistance DLC disabled. | 1.0 |
| <a id="encryption-factor"></a> encryption\_factor | Changes the encryption capability of the country by a percentage. | `encryption_factor = 0.5` | Percentual. | Only works with the ![La Résistance](media/modifiers-hearts-of-iron-4-wiki_5dfb90c7fa__img12.png) La Résistance DLC disabled. | 1.0 |
| <a id="type-intel-decryption-bonus"></a> <type>\_intel\_decryption\_bonus | Adds a cipher bonus to the specified intel. | `civilian_intel_decryption_bonus = 0.5` | Percentual. | Types are: airforce, army, civilian, navy. | 1.9 |
| <a id="type-intel-factor"></a> <type>\_intel\_factor | Modifies the intelligence you receive of the specified type. | `navy_intel_factor = 0.5` | Percentual. | Types are: airforce, army, civilian, navy. | 1.9 |
| <a id="type-intel-to-others"></a> <type>\_intel\_to\_others | Changes the amount of intel other countries will receive of the specified type. | `civilian_intel_to_others = 0.5` | Percentual. | Types are: airforce, army, civilian, navy. | 1.9 |
| <a id="female-random-operative-chance"></a> female\_random\_operative\_chance | Changes the chance for a randomly-generated operative to be female. | `female_random_operative_chance = 0.3` | Percentual. |  | 1.9.1 |
| <a id="foreign-subversive-activites"></a> foreign\_subversive\_activites | Changes efficiency of foreign subversive activities. | `foreign_subversive_activites = 0.3` | Percentual. |  | 1.9 |
| <a id="intel-network-gain"></a> intel\_network\_gain | Changes gain of intel network strength. | `intel_network_gain = 1` | Flat. | Can also be used in state scope. | 1.9 |
| <a id="intel-network-gain-factor"></a> intel\_network\_gain\_factor | Changes gain of intel network strength by a percentage. | `intel_network_gain_factor = 0.5` | Percentual. | Can also be used in state scope. | 1.9 |
| <a id="subversive-activites-upkeep"></a> subversive\_activites\_upkeep | Changes the cost of subversive activities. | `subversive_activites_upkeep = 0.5` | Percentual. |  | 1.0 |
| <a id="operation-cost"></a> operation\_cost | Changes the cost of operations. | `operation_cost = 0.5` | Percentual. | Dynamically created by operations with the `cost_modifiers = { ... }` block. This one is used by each base game operation to modify the operation cost. | 1.9 |
| <a id="operation-outcome"></a> operation\_outcome | Changes the efficiency of operations. | `operation_outcome = 0.5` | Percentual. | Dynamically created by operations with the `outcome_modifiers = { ... }` block. This one is used by each base game operation to modify the operation's outcome chance. | 1.9 |
| <a id="operation-risk"></a> operation\_risk | Changes the risk of operations. | `operation_risk = 0.5` | Percentual. | Dynamically created by operations with the `risk_modifiers = { ... }` block. This one is used by each base game operation to modify the operation risk. | 1.9 |
| <a id="operation-cost"></a> <operation>\_cost | Changes the cost of the specified operation. | `operation_infiltrate_cost = 0.5` | Percentual. | Operations are defined in /Hearts of Iron IV/common/operations/\*.txt. Dynamically created by operations with the `cost_modifiers = { ... }` block. | 1.9 |
| <a id="operation-outcome"></a> <operation>\_outcome | Changes the efficiency of the specified operation. | `operation_coup_government_outcome = 0.5` | Percentual. | Operations are defined in /Hearts of Iron IV/common/operations/\*.txt. Dynamically created by operations with the `outcome_modifiers = { ... }` block. Note that target\_sabotage uses target\_sabotage\_factor rather than target\_sabotage\_outcome. | 1.9 |
| <a id="operation-risk"></a> <operation>\_risk | Changes the risk of the specified operation. | `operation_make_resistance_contacts_risk = 0.5` | Percentual. | Operations are defined in /Hearts of Iron IV/common/operations/\*.txt. Dynamically created by operations with the `risk_modifiers = { ... }` block. | 1.9 |
| <a id="mission-factor"></a> <mission>\_factor | Modifies the effect of the specified mission. | `boost_ideology_mission_factor = 0.5` | Percentual. | Types are: boost\_ideology\_mission, boost\_resistance, control\_trade\_mission, diplomatic\_pressure\_mission, propaganda\_mission, root\_out\_resistance\_effectiveness. | 1.9 |
| <a id="commando-trait-chance-factor"></a> commando\_trait\_chance\_factor | Modifies the chance for an operative to get the commando trait when hired. | `commando_trait_chance_factor = 0.5` | Percentual. |  | 1.9 |
| <a id="crypto-department-enabled"></a> crypto\_department\_enabled | Enables the crypto department. | `crypto_department_enabled = 1` | Boolean (only 1). |  | 1.9 |
| <a id="crypto-strength"></a> crypto\_strength | Modifies the cryptology level. | `crypto_strength = 1` | Flat. | ![La Résistance](media/modifiers-hearts-of-iron-4-wiki_5dfb90c7fa__img12.png) La Résistance DLC enabled. | 1.9 |
| <a id="decryption-power"></a> decryption\_power | Modifies the decryption power. | `decryption_power = 1` | Flat. | ![La Résistance](media/modifiers-hearts-of-iron-4-wiki_5dfb90c7fa__img12.png) La Résistance DLC enabled. | 1.9 |
| <a id="decryption-power-factor"></a> decryption\_power\_factor | Modifies the decryption power by a percentage. | `decryption_power_factor = 0.3` | Percentual. | ![La Résistance](media/modifiers-hearts-of-iron-4-wiki_5dfb90c7fa__img12.png) La Résistance DLC enabled. | 1.9 |
| <a id="defense-impact-on-blueprint-stealing"></a> defense\_impact\_on\_blueprint\_stealing | Modifies the impact of enemy defense on the blueprint stealing operation. | `defense_impact_on_blueprint_stealing = 0.3` | Percentual. |  | 1.9 |
| <a id="intel-from-combat-factor"></a> intel\_from\_combat\_factor | Modifies the intelligence gained from combat. | `intel_from_combat_factor = 0.3` | Percentual. |  | 1.9 |
| <a id="intel-from-operatives-factor"></a> intel\_from\_operatives\_factor | Modifies the intelligence gained from operatives and infiltrated assets. | `intel_from_operatives_factor = 0.3` | Percentual. |  | 1.9 |
| <a id="intel-network-gain"></a> intel\_network\_gain | Modifies the intelligence network gain. | `intel_network_gain = 0.3` | Flat. |  | 1.9 |
| <a id="intel-network-gain-factor"></a> intel\_network\_gain\_factor | Modifies the intelligence network gain by a percentage. | `intel_network_gain_factor = 0.3` | Percentual. |  | 1.9 |
| <a id="intelligence-agency-defense"></a> intelligence\_agency\_defense | Modifies the counter intelligence. | `intelligence_agency_defense = 0.3` | Flat. |  | 1.9 |
| <a id="root-out-resistance-effectiveness-factor"></a> root\_out\_resistance\_effectiveness\_factor | Modifies the effectiveness of rooting out resistance. | `root_out_resistance_effectiveness_factor = 0.3` | Percentual. |  | 1.9 |

#### <a id="operatives"></a>Operatives

These can be used in both the country scope and operative scope, such as traits, unless specified otherwise.

Operative-related country-scoped modifiers:
| Name | Effects | Examples | Modifier type | Notes | Version added |
| --- | --- | --- | --- | --- | --- |
| <a id="own-operative-capture-chance-factor"></a> own\_operative\_capture\_chance\_factor | Changes the chance for our operatives to be captured. | `own_operative_capture_chance_factor = 0.5` | Percentual. |  | 1.9 |
| <a id="own-operative-detection-chance"></a> own\_operative\_detection\_chance | Changes the chance for our operatives to be detected. | `own_operative_detection_chance = 10` | Flat. |  | 1.9 |
| <a id="own-operative-detection-chance-factor"></a> own\_operative\_detection\_chance\_factor | Changes the chance for our operatives to be detected by a percentage. | `own_operative_detection_chance_factor = 0.5` | Percentual. |  | 1.9 |
| <a id="own-operative-forced-into-hiding-time-factor"></a> own\_operative\_forced\_into\_hiding\_time\_factor | Changes the chance for our operatives to be forced into hiding by a percentage. | `own_operative_forced_into_hiding_time_factor = 0.5` | Percentual. |  | 1.9 |
| <a id="own-operative-harmed-time-factor"></a> own\_operative\_harmed\_time\_factor | Changes the chance for our operatives to be harmed by a percentage. | `own_operative_harmed_time_factor = 0.5` | Percentual. |  | 1.9 |
| <a id="own-operative-intel-extraction-rate"></a> own\_operative\_intel\_extraction\_rate | Changes the rate at which our operatives extract enemy intel. | `own_operative_intel_extraction_rate = 0.5` | Percentual. |  | 1.9 |
| <a id="enemy-operative-capture-chance-factor"></a> enemy\_operative\_capture\_chance\_factor | Changes the chance for an enemy operative to be captured. | `enemy_operative_capture_chance_factor = 0.5` | Percentual. |  | 1.9 |
| <a id="enemy-operative-detection-chance"></a> enemy\_operative\_detection\_chance | Changes the chance for an enemy operative to be detected. | `enemy_operative_detection_chance = 10` | Flat. |  | 1.9 |
| <a id="enemy-operative-detection-chance-factor"></a> enemy\_operative\_detection\_chance\_factor | Changes the chance for an enemy operative to be detected by a percentage. | `enemy_operative_detection_chance_factor = 0.5` | Percentual. |  | 1.9 |
| <a id="enemy-operative-forced-into-hiding-time-factor"></a> enemy\_operative\_forced\_into\_hiding\_time\_factor | Changes the chance for an enemy operative to be forced into hiding by a percentage. | `enemy_operative_forced_into_hiding_time_factor = 0.5` | Percentual. |  | 1.9 |
| <a id="enemy-operative-harmed-time-factor"></a> enemy\_operative\_harmed\_time\_factor | Changes the chance for an enemy operative to be harmed by a percentage. | `enemy_operative_harmed_time_factor = 0.5` | Percentual. |  | 1.9 |
| <a id="enemy-operative-intel-extraction-rate"></a> enemy\_operative\_intel\_extraction\_rate | Changes the rate at which the enemy operatives extract our intel. | `enemy_operative_intel_extraction_rate = 0.5` | Percentual. |  | 1.9 |
| <a id="enemy-spy-negative-status-factor"></a> enemy\_spy\_negative\_status\_factor | Changes the chance an enemy spy can receive a negative status. | `enemy_spy_negative_status_factor = 0.5` | Percentual. |  | 1.9 |
| <a id="enemy-operative-recruitment-chance"></a> enemy\_operative\_recruitment\_chance | Modifies the chance to recruit an enemy operative. | `enemy_operative_recruitment_chance = 0.3` | Percentual. | Cannot be used in operative scope. | 1.9 |
| <a id="new-operative-slot-bonus"></a> new\_operative\_slot\_bonus | Modifies the operative recruitment choices. | `new_operative_slot_bonus = 1` | Flat. | Cannot be used in operative scope. | 1.9 |
| <a id="occupied-operative-recruitment-chance"></a> occupied\_operative\_recruitment\_chance | Modifies the chance to get an operative from occupied territory. | `occupied_operative_recruitment_chance = 0.3` | Percentual. | Cannot be used in operative scope. | 1.9 |
| <a id="operative-death-on-capture-chance"></a> operative\_death\_on\_capture\_chance | Modifies the chance for the country's operative to die on being captured. | `operative_death_on_capture_chance = 0.3` | Percentual. | Cannot be used in operative scope. | 1.9 |
| <a id="operative-slot"></a> operative\_slot | Modifies the amount of operative slots. | `operative_slot = 1` | Flat. | Cannot be used in operative scope. | 1.9 |

#### <a id="ai"></a>AI

AI-related country-scoped modifiers:
| Name | Effects | Examples | Modifier type | Notes | Version added |
| --- | --- | --- | --- | --- | --- |
| <a id="ai-badass-factor"></a> ai\_badass\_factor | AI's threat perception. | `ai_badass_factor = 0.5` | Percentual. |  | 1.0 |
| <a id="ai-call-ally-desire-factor"></a> ai\_call\_ally\_desire\_factor | Chance for AI to call allies. | `ai_call_ally_desire_factor = 0.5` | Percentual. |  | 1.0 |
| <a id="ai-desired-divisions-factor"></a> ai\_desired\_divisions\_factor | The amount of divisions AI seeks to produce. | `ai_desired_divisions_factor = 0.5` | Percentual. |  | 1.0 |
| <a id="ai-focus-aggressive-factor"></a> ai\_focus\_aggressive\_factor | AI's focus on offense. | `ai_focus_aggressive_factor = 0.5` | Percentual. |  | 1.0 |
| <a id="ai-focus-defense-factor"></a> ai\_focus\_defense\_factor | AI's focus on defense. | `ai_focus_defense_factor = 0.5` | Percentual. |  | 1.0 |
| <a id="ai-focus-aviation-factor"></a> ai\_focus\_aviation\_factor | AI's focus on aviation. | `ai_focus_aviation_factor = 0.5` | Percentual. |  | 1.0 |
| <a id="ai-focus-military-advancements-factor"></a> ai\_focus\_military\_advancements\_factor | AI's focus on advanced military technologies. | `ai_focus_military_advancements_factor = 0.5` | Percentual. |  | 1.0 |
| <a id="ai-focus-military-equipment-factor"></a> ai\_focus\_military\_equipment\_factor | AI's focus on advanced military equipment. | `ai_focus_military_equipment_factor = 0.5` | Percentual. |  | 1.0 |
| <a id="ai-focus-naval-air-factor"></a> ai\_focus\_naval\_air\_factor | AI's focus on building naval airforce. | `ai_focus_naval_air_factor = 0.5` | Percentual. |  | 1.0 |
| <a id="ai-focus-naval-factor"></a> ai\_focus\_naval\_factor | AI's focus on building a navy. | `ai_focus_naval_factor = 0.5` | Percentual. |  | 1.0 |
| <a id="ai-focus-peaceful-factor"></a> ai\_focus\_peaceful\_factor | AI's focus on peaceful research and policies. | `ai_focus_peaceful_factor = 0.5` | Percentual. |  | 1.0 |
| <a id="ai-focus-war-production-factor"></a> ai\_focus\_war\_production\_factor | AI's focus on wartime production. | `ai_focus_war_production_factor = 0.5` | Percentual. |  | 1.0 |
| <a id="ai-get-ally-desire-factor"></a> ai\_get\_ally\_desire\_factor | AI's desire to be in or expand a faction. | `ai_get_ally_desire_factor = 0.5` | Percentual. |  | 1.0 |
| <a id="ai-join-ally-desire-factor"></a> ai\_join\_ally\_desire\_factor | AI's desire to join the wars led by allies. | `ai_join_ally_desire_factor = 0.5` | Percentual. |  | 1.0 |
| <a id="ai-license-acceptance"></a> ai\_license\_acceptance | AI's chance to agree licensing equipment. | `ai_license_acceptance = 0.5` | Percentual. | Can be used as a targeted modifier. | 1.4 |

#### <a id="military-outside-of-combat"></a>Military outside of combat

Military-related country-scoped modifiers:
| Name | Effects | Examples | Modifier type | Notes | Version added |
| --- | --- | --- | --- | --- | --- |
| <a id="command-power-gain"></a> command\_power\_gain | Changes the daily gain of command power. | `command_power_gain = 0.5` | Flat. |  | 1.5 |
| <a id="command-power-gain-mult"></a> command\_power\_gain\_mult | Changes the daily gain of command power by a percentage. | `command_power_gain_mult = 0.5` | Percentual. |  | 1.5 |
| <a id="conscription"></a> conscription | Changes the recruitable percentage of the total population. | `conscription = 0.02` | Flat. |  | 1.0 |
| <a id="conscription-factor"></a> conscription\_factor | Changes the recruitable percentage of the total population by a percent. | `conscription_factor = 0.3` | Percentual. |  | 1.0 |
| <a id="experience-gain-army"></a> experience\_gain\_army | Modifies the daily gain of army experience. | `experience_gain_army = 0.5` | Flat. |  | 1.0 |
| <a id="experience-gain-army-factor"></a> experience\_gain\_army\_factor | Modifies the gain of army experience by a percentage. | `experience_gain_army_factor = 0.5` | Percentual. |  | 1.0 |
| <a id="experience-gain-navy"></a> experience\_gain\_navy | Modifies the daily gain of naval experience. | `experience_gain_navy = 0.02` | Flat. |  | 1.0 |
| <a id="experience-gain-navy-factor"></a> experience\_gain\_navy\_factor | Modifies the gain of naval experience by a percentage. | `experience_gain_navy_factor = 0.3` | Percentual. |  | 1.0 |
| <a id="experience-gain-air"></a> experience\_gain\_air | Modifies the daily gain of air experience. | `experience_gain_air = 0.05` | Flat. |  | 1.0 |
| <a id="experience-gain-air-factor"></a> experience\_gain\_air\_factor | Modifies the daily gain of air experience by a percentage. | `experience_gain_air_factor = 0.5` | Percentual. |  | 1.0 |
| <a id="land-equipment-upgrade-xp-cost"></a> land\_equipment\_upgrade\_xp\_cost | Changes the experience cost to upgrade land army equipment. | `land_equipment_upgrade_xp_cost = 0.3` | Percentual. |  | 1.0 |
| <a id="land-reinforce-rate"></a> land\_reinforce\_rate | Changes the rate at which reinforcements to divisions arrive. | `land_reinforce_rate = 0.3` | Percentual. |  | 1.0 |
| <a id="max-command-power"></a> max\_command\_power | Changes maximum command power. | `max_command_power = 20` | Flat. |  | 1.5 |
| <a id="max-command-power-mult"></a> max\_command\_power\_mult | Changes maximum command power by a percentage. | `max_command_power_mult = 0.3` | Percentual. |  | 1.5 |
| <a id="weekly-manpower"></a> weekly\_manpower | Amount of manpower gained each week. | `weekly_manpower = 1000` | Flat. |  | 1.6 |
| <a id="naval-equipment-upgrade-xp-cost"></a> naval\_equipment\_upgrade\_xp\_cost | Changes the naval experience cost to upgrade equipment. | `naval_equipment_upgrade_xp_cost = 0.3` | Percentual. |  | 1.0 |
| <a id="refit-ic-cost"></a> refit\_ic\_cost | The IC cost to refit naval equipment. | `refit_ic_cost = 20` | Flat. |  | 1.6 |
| <a id="refit-speed"></a> refit\_speed | The speed at which naval equipment is refitted. | `refit_speed = 0.5` | Percentual. |  | 1.6 |
| <a id="air-equipment-upgrade-xp-cost"></a> air\_equipment\_upgrade\_xp\_cost | Changes the air experience cost to upgrade equipment. | `air_equipment_upgrade_xp_cost = 0.5` | Percentual. |  | 1.0 |
| <a id="training-time-factor"></a> training\_time\_factor | Modifies the training time for both army and navy. | `training_time_factor = 0.3` | Percentual. |  | 1.0 |
| <a id="minimum-training-level"></a> minimum\_training\_level | Changes training level necessary for the unit to deploy. | `minimum_training_level = 0.3` | Percentual. |  | 1.0 |
| <a id="max-training"></a> max\_training | Modifies the required experience to achieve full training. | `max_training = -0.3` | Percentual. |  | 1.0 |
| <a id="training-time-army-factor"></a> training\_time\_army\_factor | Modifies the training time for the army. | `training_time_army_factor = 0.3` | Percentual. |  | 1.0 |
| <a id="special-forces-training-time-factor"></a> special\_forces\_training\_time\_factor | Changes the time it takes to train special forces. | `special_forces_training_time_factor = 0.3` | Percentual. |  | 1.0 |
| <a id="land-air-naval-doctrine-cost-factor"></a> <land/air/naval>\_doctrine\_cost\_factor | Changes the cost of buying a new doctrine of the specified type. | `land_doctrine_cost_factor = -0.05` | Percentual. |  | 1.11 |
| <a id="doctrine-cost-factor"></a> <doctrine category>\_cost\_factor | Modifies the cost of buying a new doctrine of the specified category. | `cat_mobile_warfare_cost_factor = 0.3` | Percentual. | Doctrines are defined in /Hearts of Iron IV/common/technologies/\*.txt. | 1.11 |
| <land/air/naval>\_mastery\_gain\_factor | Modifies the speed at which mastery in a given doctrine folder is gained. | `land_mastery_gain_factor = 0.15` | Percentual. | Doctrine tracks are defined in `/Hearts of Iron IV/common/doctrines/folders`. |  |
| <doctrine track>\_track\_mastery\_gain\_factor | Modifies the speed at which mastery of a given track is gained. | `operations_track_mastery_gain_factor = 0.1` | Percentual. | Doctrine tracks are defined in `/Hearts of Iron IV/common/doctrines/tracks`. currently existing tracks are Army: `infantry`,`combat_support`,`armor`and`operations`  Air: `fighter_aircraft`,`strike_aircraft`,`medium_aircraft`and`heavy_aircraft`  Navy: `capital_ships`,`carriers`,`screens`and`submarines` | 1.17 |
| <a id="choose-preferred-tactics-cost"></a> choose\_preferred\_tactics\_cost | Changes the cost to choose a preferred tactic. | `choose_preferred_tactics_cost = 5` | Flat. |  | 1.11 |
| <a id="command-abilities-cost-factor"></a> command\_abilities\_cost\_factor | Changes the cost to choose a command ability. | `command_abilities_cost_factor = -0.3` | Percentual. |  | 1.11 |
| <a id="transport-capacity"></a> transport\_capacity | Modifies how many convoys units require to be transported over sea. | `transport_capacity = 0.3` | Percentual. |  | 1.0 |
| <a id="paratroopers-special-forces-contribution-factor"></a> paratroopers\_special\_forces\_contribution\_factor | Modifies how much paratroopers contribute to the limit of special forces on a template. | `paratroopers_special_forces_contribution_factor = 0.3` | Percentual. |  | 1.13 |
| <a id="marines-special-forces-contribution-factor"></a> marines\_special\_forces\_contribution\_factor | Modifies how much marines contribute to the limit of special forces on a template. | `marines_special_forces_contribution_factor = 0.3` | Percentual. |  | 1.13 |
| <a id="mountaineers-special-forces-contribution-factor"></a> mountaineers\_special\_forces\_contribution\_factor | Modifies how much mountaineers contribute to the limit of special forces on a template. | `mountaineers_special_forces_contribution_factor = 0.3` | Percentual. |  | 1.13 |
| <a id="rangers-special-forces-contribution-factor"></a> rangers\_special\_forces\_contribution\_factor | Modifies how much rangers contribute to the limit of special forces on a template. | `rangers_special_forces_contribution_factor = 0.3` | Percentual. |  | 1.17 |
| <a id="special-forces-cap-flat"></a> special\_forces\_cap\_flat | Modifies how many special forces sub-units can be put into a single template. | `special_forces_cap_flat = 10` | Percentual. |  | 1.13 |
| <a id="additional-brigade-column-size"></a> additional\_brigade\_column\_size | Changes the amount of maximum unlocked slots on each brigade column in division templates. | `additional_brigade_column_size = 1` | Flat. |  | 1.13 |
| <a id="unit-design-cost-factor"></a> unit\_<unit type>\_design\_cost\_factor | Modifies how much experience it costs to add a brigade of the specified type to a template. | `unit_artillery_brigade_design_cost_factor = 0.3` | Percentual. | Brigades are defined in /Hearts of Iron IV/common/units/\*.txt | 1.11 |
| <a id="equipment-design-cost-factor"></a> <equipment archetype>\_design\_cost\_factor | Modifies how much experience it costs to add upgrades or modules to a specified equipment archetype. | `strat_bomber_equipment_design_cost_factor = 0.3`  `ship_hull_heavy_design_cost_factor = -0.2` | Percentual. | Equipment archetypes are defined in /Hearts of Iron IV/common/units/equipment/\*.txt | 1.11 |
| <a id="module-design-cost-factor"></a> module\_<module type>\_design\_cost\_factor | Modifies how much experience it costs to add a module of the specified type to equipment. | `module_tank_torsion_bar_suspension_design_cost_factor = 0.3` | Percentual. | Modules are defined in /Hearts of Iron IV/common/units/equipment/modules/\*.txt | 1.11 |

#### <a id="mios"></a>MIOs

These are modifiers related to military industrial organisations.

MIO-related country-scoped modifiers:
| Name | Effects | Examples | Modifier type | Notes | Version added |
| --- | --- | --- | --- | --- | --- |
| <a id="military-industrial-organization-research-bonus"></a> military\_industrial\_organization\_research\_bonus | Modifies the research bonus granted by MIOs. | `military_industrial_organization_research_bonus = 0.3` | Percentual. |  | 1.13 |
| <a id="military-industrial-organization-design-team-assign-cost"></a> military\_industrial\_organization\_design\_team\_assign\_cost | Modifies the political power cost to assign a design team. | `military_industrial_organization_design_team_assign_cost = 30` | Flat. |  | 1.13 |
| <a id="military-industrial-organization-design-team-change-cost"></a> military\_industrial\_organization\_design\_team\_change\_cost | Modifies the political power cost to change a design team. | `military_industrial_organization_design_team_change_cost = 20` | Flat. |  | 1.13 |
| <a id="military-industrial-organization-industrial-manufacturer-assign-cost"></a> military\_industrial\_organization\_industrial\_manufacturer\_assign\_cost | Modifies the political power cost to assign an industrial manufacturer. | `military_industrial_organization_industrial_manufacturer_assign_cost = 10` | Flat. |  | 1.13 |
| <a id="military-industrial-organization-task-capacity"></a> military\_industrial\_organization\_task\_capacity | Modifies the amount of tasks possible to assign to the MIO. | `military_industrial_organization_task_capacity = 2` | Flat. |  | 1.13 |
| <a id="military-industrial-organization-size-up-requirement"></a> military\_industrial\_organization\_size\_up\_requirement | Modifies the requirement to size up a MIO. | `military_industrial_organization_size_up_requirement = 2` | Flat. |  | 1.13 |
| <a id="military-industrial-organization-funds-gain"></a> military\_industrial\_organization\_funds\_gain | Modifies the amount of funds gained by the MIO. | `military_industrial_organization_funds_gain = 0.3` | Percentual. |  | 1.13 |
| <a id="military-industrial-organization-policy-cost"></a> military\_industrial\_organization\_policy\_cost | Modifies the political power cost to assign a MIO policy. | `military_industrial_organization_policy_cost = 20` | Flat. |  | 1.13 |
| <a id="military-industrial-organization-policy-cooldown"></a> military\_industrial\_organization\_policy\_cooldown | Modifies the cooldown between how often it's possible to change policies. | `military_industrial_organization_policy_cooldown = 5` | Flat. |  | 1.13 |

#### <a id="unit-leaders"></a>Unit leaders

These are modifiers related to unit leaders in the country scope, rather than being in the unit leader scope.

Unit leader-related country-scoped modifiers:
| Name | Effects | Examples | Modifier type | Notes | Version added |
| --- | --- | --- | --- | --- | --- |
| <a id="female-random-army-leader-chance"></a> female\_random\_army\_leader\_chance | Changes the chance for a randomly-generated army leader to be female. | `female_random_army_leader_chance = 0.3` | Percentual. |  | 1.9.1 |
| <a id="assign-army-leader-cp-cost"></a> assign\_army\_leader\_cp\_cost | Modifies the cost to assign an army leader to an army. | `assign_army_leader_cp_cost = -5` | Flat. |  | 1.11 |
| <a id="army-leader-cost-factor"></a> army\_leader\_cost\_factor | The cost in political power to recruit an unit leader for the land army. | `army_leader_cost_factor = 0.5` | Percentual. |  | 1.3 |
| <a id="army-leader-start-level"></a> army\_leader\_start\_level | Bonus to the starting level of generic unit leaders. | `army_leader_start_level = 1` | Flat. |  | 1.5 |
| <a id="army-leader-start-attack-level"></a> army\_leader\_start\_attack\_level | Bonus to the starting level of attack in generic unit leaders. | `army_leader_start_attack_level = 1` | Flat. |  | 1.5 |
| <a id="army-leader-start-defense-level"></a> army\_leader\_start\_defense\_level | Bonus to the starting level of defense in generic unit leaders. | `army_leader_start_defense_level = 1` | Flat. |  | 1.5 |
| <a id="army-leader-start-logistics-level"></a> army\_leader\_start\_logistics\_level | Bonus to the starting level of logistics in generic unit leaders. | `army_leader_start_logistics_level = 1` | Flat. |  | 1.5 |
| <a id="army-leader-start-planning-level"></a> army\_leader\_start\_planning\_level | Bonus to the starting level of planning in generic unit leaders. | `army_leader_start_planning_level = 1` | Flat. |  | 1.5 |
| <a id="military-leader-cost-factor"></a> military\_leader\_cost\_factor | The cost in political power to recruit an unit leader. | `military_leader_cost_factor = 0.5` | Percentual. |  | 1.3 |
| <a id="female-random-admiral-chance"></a> female\_random\_admiral\_chance | Changes the chance for a randomly-generated admiral to be female. | `female_random_admiral_chance = 0.3` | Percentual. |  | 1.9.1 |
| <a id="assign-navy-leader-cp-cost"></a> assign\_navy\_leader\_cp\_cost | Modifies the cost to assign a navy leader to a navy. | `assign_navy_leader_cp_cost = -5` | Flat. |  | 1.11 |
| <a id="navy-leader-cost-factor"></a> navy\_leader\_cost\_factor | The cost in political power to recruit an unit leader for the land navy. | `navy_leader_cost_factor = 0.5` | Percentual. |  | 1.3 |
| <a id="navy-leader-start-level"></a> navy\_leader\_start\_level | Bonus to the starting level of generic unit leaders. | `navy_leader_start_level = 1` | Flat. |  | 1.9 |
| <a id="navy-leader-start-attack-level"></a> navy\_leader\_start\_attack\_level | Bonus to the starting level of attack in generic unit leaders. | `navy_leader_start_attack_level = 1` | Flat. |  | 1.9 |
| <a id="navy-leader-start-coordination-level"></a> navy\_leader\_start\_coordination\_level | Bonus to the starting level of coordination in generic unit leaders. | `navy_leader_start_coordination_level = 1` | Flat. |  | 1.9 |
| <a id="navy-leader-start-defense-level"></a> navy\_leader\_start\_defense\_level | Bonus to the starting level of defense in generic unit leaders. | `navy_leader_start_defense_level = 1` | Flat. |  | 1.9 |
| <a id="navy-leader-start-maneuvering-level"></a> navy\_leader\_start\_maneuvering\_level | Bonus to the starting level of maneuvering in generic unit leaders. | `navy_leader_start_maneuvering_level = 1` | Flat. |  | 1.9 |
| <a id="grant-medal-cost-factor"></a> grant\_medal\_cost\_factor | Changes the cost in command power to grant a medal to a division commander. | `grant_medal_cost_factor = 0.2` | Percentual. |  | 1.12 |
| <a id="field-officer-promotion-penalty"></a> field\_officer\_promotion\_penalty | Changes the experience penalty applied to the divisions when a commander is promoted to a field marshal. | `field_officer_promotion_penalty = 0.2` | Percentual. |  | 1.12 |
| <a id="female-divisional-commander-chance"></a> female\_divisional\_commander\_chance | Changes the chance to get a female divisional commander. | `female_divisional_commander_chance = 0.2` | Flat. | If no generic female portraits are defined within /Hearts of Iron IV/portraits/\*.txt files, there will be a silhouette. | 1.12 |

#### <a id="general-combat"></a>General combat

Note that most of these modifiers are not only in country scope but also in unit leader and navy leader scopes.

Combat-related country-scoped modifiers:
| Name | Effects | Examples | Modifier type | Notes | Version added |
| --- | --- | --- | --- | --- | --- |
| <a id="offence"></a> offence | Modifies the attack value of our military, navy, and airforce. | `offence = 0.5` | Percentual. | Does not work in country scope, use army\_attack\_factor instead. | 1.0 |
| <a id="defence"></a> defence | Modifies the defence value of our military, navy, and airforce. | `defence = 0.5` | Percentual. | Does not work in country scope, use army\_defence\_factor instead. | 1.0 |
| <a id="tactic-preferred-weight-factor"></a> <Tactic>\_preferred\_weight\_factor | Modifies the chance for a commander to choose the specified tactic. | `tactic_ambush_preferred_weight_factor = 0.3` | Percentual. | Combat tactics are defined in /Hearts of Iron IV/common/combat\_tactics.txt. | 1.6 |

#### <a id="land-combat"></a>Land combat

Note that most of these modifiers are not only in country scope but also in unit leader scope.

Land combat-related country-scoped modifiers:
| Name | Effects | Examples | Modifier type | Notes | Version added |
| --- | --- | --- | --- | --- | --- |
| <a id="acclimatization-cold-climate-gain-factor"></a> acclimatization\_cold\_climate\_gain\_factor | Cold acclimatization gain factor. | `acclimatization_cold_climate_gain_factor = 0.5` | Percentual. |  | 1.0 |
| <a id="acclimatization-hot-climate-gain-factor"></a> acclimatization\_hot\_climate\_gain\_factor | Hot acclimatization gain factor. | `acclimatization_hot_climate_gain_factor = 0.5` | Percentual. |  | 1.0 |
| <a id="air-superiority-bonus-in-combat"></a> air\_superiority\_bonus\_in\_combat | The bonus in combat given from having air superiority. | `air_superiority_bonus_in_combat = 0.5` | Percentual. |  | 1.0 |
| <a id="army-attack-factor"></a> army\_attack\_factor | The bonus to land army's attack. | `army_attack_factor = 0.5` | Percentual. |  | 1.0 |
| <a id="army-core-attack-factor"></a> army\_core\_attack\_factor | The bonus to land army's attack on core territory. | `army_core_attack_factor = 0.1` | Percentual. |  | 1.0 |
| <a id="army-claim-attack-factor"></a> army\_claim\_attack\_factor | The bonus to land army's attack on claimed territory. | `army_claim_attack_factor = 0.1` | Percentual. |  | 1.17 |
| <a id="army-attack-against-major-factor"></a> army\_attack\_against\_major\_factor | The bonus to land army's attack against a major country. | `army_attack_against_major_factor = 0.5` | Percentual. |  | 1.11 |
| <a id="army-attack-against-minor-factor"></a> army\_attack\_against\_minor\_factor | The bonus to land army's attack against a non-major country. | `army_attack_against_minor_factor = 0.5` | Percentual. |  | 1.11 |
| <a id="army-attack-speed-factor"></a> army\_attack\_speed\_factor | The bonus to speed at which the land army attacks. | `army_attack_speed_factor = 0.5` | Percentual. |  | 1.0 |
| <a id="army-breakthrough-against-major-factor"></a> army\_breakthrough\_against\_major\_factor | The bonus to land army's breakthrough against a major country. | `army_breakthrough_against_major_factor = 0.5` | Percentual. |  | 1.11 |
| <a id="army-breakthrough-against-minor-factor"></a> army\_breakthrough\_against\_minor\_factor | The bonus to land army's breakthrough against a non-major country. | `army_breakthrough_against_minor_factor = 0.5` | Percentual. |  | 1.11 |
| <a id="army-defence-factor"></a> army\_defence\_factor | The bonus to land army's defence. | `army_defence_factor = 0.5` | Percentual. |  | 1.0 |
| <a id="army-defence-against-major-factor"></a> army\_defence\_against\_major\_factor | The bonus to land army's defence against a major country. | `army_defence_against_major_factor = 0.5` | Percentual. |  | 1.11 |
| <a id="army-defence-against-minor-factor"></a> army\_defence\_against\_minor\_factor | The bonus to land army's defence against a non-major country. | `army_defence_against_minor_factor = 0.5` | Percentual. |  | 1.11 |
| <a id="army-core-defence-factor"></a> army\_core\_defence\_factor | The bonus to land army's defence on core territory. | `army_core_defence_factor = 0.1` | Percentual. |  | 1.0 |
| <a id="army-claim-defence-factor"></a> army\_claim\_defence\_factor | The bonus to land army's defence on claimed territory. | `army_claim_defence_factor = 0.1` | Percentual. |  | 1.17 |
| <a id="army-speed-factor"></a> army\_speed\_factor | The bonus to land army's speed. | `army_speed_factor = 0.5` | Percentual. |  | 1.0 |
| <a id="army-strength-factor"></a> army\_strength\_factor | The bonus to land army's strength. | `army_strength_factor = 0.5` | Percentual. |  | 1.11 |
| <a id="unit-type-attack-factor"></a> <unit type>\_attack\_factor | The bonus to specified unit type's attack. | `cavalry_attack_factor = 0.5` | Percentual. | Allowed unit types are army\_armor, army\_artillery, army\_infantry, cavalry, mechanized, motorized, special\_forces | 1.0 |
| <a id="unit-type-defence-factor"></a> <unit type>\_defence\_factor | The bonus to the specified unit type's defence. | `army_artillery_defence_factor = 0.5` | Percentual. | Allowed unit types are army\_armor, army\_artillery, army\_infantry, cavalry, mechanized, motorized, special\_forces | 1.0 |
| <a id="unit-type-speed-factor"></a> <unit type>\_speed\_factor | The bonus to specified unit type's speed. | `army_armor_speed_factor = 0.5` | Percentual. | Allowed unit types are army\_armor and cavalry. Cavalry\_speed\_factor is currently broken and not recognized by the game. | 1.0 |
| <a id="modifier-army-sub-unit-unit-type-attack-factor"></a> modifier\_army\_sub\_unit\_<unit type>\_attack\_factor | The bonus to specified unit type's attack. | `modifier_army_sub_unit_armored_car_attack_factor = 0.1` | Percentual. | Allowed unit types are all defined batallions, including those added through mods. | ??? |
| <a id="modifier-army-sub-unit-unit-type-defence-factor"></a> modifier\_army\_sub\_unit\_<unit type>\_defence\_factor | The bonus to the specified unit type's defence. | `modifier_army_sub_unit_armored_car_defence_factor = 0.1` | Percentual. | Allowed unit types are all defined batallions, including those added through mods. | ??? |
| <a id="modifier-army-sub-unit-unit-type-speed-factor"></a> modifier\_army\_sub\_unit\_<unit type>\_speed\_factor | The bonus to specified unit type's speed. | `modifier_army_sub_unit_armored_car_speed_factor = 0.1` | Percentual. | Allowed unit types are all defined batallions, including those added through mods. | ??? |
| <a id="army-morale"></a> army\_morale | Modifies the division recovery rate. | `army_morale = 10` | Flat. |  | 1.0 |
| <a id="army-morale-factor"></a> army\_morale\_factor | Modifies the division recovery rate by a percentage. | `army_morale_factor = 0.3` | Percentual. |  | 1.0 |
| <a id="army-org"></a> army\_org | Modifies the army's organisation. | `army_org = 10` | Flat. |  | 1.0 |
| <a id="army-org-factor"></a> army\_org\_factor | Modifies the army's organisation by a percentage. | `army_org_factor = 0.3` | Percentual. |  | 1.0 |
| <a id="army-org-regain"></a> army\_org\_regain | Modifies the army's organisation regain speed by a percentage. | `army_org_regain = 0.3` | Percentual. |  | 1.5.1 |
| <a id="breakthrough-factor"></a> breakthrough\_factor | Modifies the army's breakthrough. | `breakthrough_factor = 0.3` | Percentual. |  | 1.0 |
| <a id="cas-damage-reduction"></a> cas\_damage\_reduction | Reduces the damage dealt by close air support. | `cas_damage_reduction = 0.3` | Percentual. |  | 1.0 |
| <a id="combat-width-factor"></a> combat\_width\_factor | Changes our own combat width. | `combat_width_factor = 0.3` | Percentual. |  | 1.0 |
| <a id="coordination-bonus"></a> coordination\_bonus | Changes the bonus to coordination, that is how much damage is done to the primary target instead of being spread out. | `coordination_bonus = 0.3` | Percentual. |  | 1.11 |
| <a id="dig-in-speed"></a> dig\_in\_speed | Changes entrenchment speed. | `dig_in_speed = 2` | Flat. |  | 1.0 |
| <a id="dig-in-speed-factor"></a> dig\_in\_speed\_factor | Changes entrenchment speed by a percentage. | `dig_in_speed_factor = 0.5` | Percentual. |  | 1.0 |
| <a id="experience-gain-army-unit"></a> experience\_gain\_army\_unit | Changes experience gain by the army divisions. | `experience_gain_army_unit = 0.5` | Flat. |  | 1.0 |
| <a id="experience-gain-army-unit-factor"></a> experience\_gain\_army\_unit\_factor | Changes experience gain by the army divisions by a percentage. | `experience_gain_army_unit_factor = 0.5` | Percentual. |  | 1.0 |
| <a id="experience-loss-factor"></a> experience\_loss\_factor | Changes the loss in divisions' experience in combat. | `experience_loss_factor = 0.3` | Percentual. |  | 1.0 |
| <a id="initiative-factor"></a> initiative\_factor | Modifies the initiative. | `initiative_factor = 0.3` | Percentual. |  | 1.11 |
| <a id="land-night-attack"></a> land\_night\_attack | Changes the penalty due to attacking at night. | `land_night_attack = 0.5` | Percentual. |  | 1.0 |
| <a id="max-dig-in"></a> max\_dig\_in | Changes the maximum entrenchment. | `max_dig_in = 20` | Flat. | Can also apply in state scope. | 1.0 |
| <a id="max-dig-in-factor"></a> max\_dig\_in\_factor | Changes the maximum entrenchment by a percentage. | `max_dig_in_factor = 0.5` | Percentual. | Can also apply in state scope. | 1.0 |
| <a id="max-planning"></a> max\_planning | Changes the maximum planning. | `max_planning = 20` | Flat. |  | 1.0 |
| <a id="max-planning-factor"></a> max\_planning\_factor | Changes the maximum planning by a percentage. | `max_planning_factor = 0.5` | Percentual. |  | 1.9 |
| <a id="pocket-penalty"></a> pocket\_penalty | Reduces the penalty that troops take when they are encircled. | `pocket_penalty = 0.2` | Percentual. |  | 1.0 |
| <a id="recon-factor"></a> recon\_factor | Changes reconnaisance. | `recon_factor = 0.2` | Percentual. |  | 1.0 |
| <a id="recon-factor-while-entrenched"></a> recon\_factor\_while\_entrenched | Changes reconnaisance for entrenched divisions. | `recon_factor_while_entrenched = 0.2` | Percentual. |  | 1.0 |
| <a id="special-forces-cap"></a> special\_forces\_cap | Changes the maximum amount of special forces by a percentage. | `special_forces_cap = 0.5` | Percentual. |  | 1.0 |
| <a id="special-forces-min"></a> special\_forces\_min | Changes the minimum amount of special forces. | `special_forces_min = 250` | Flat. |  | 1.0 |
| <a id="terrain-penalty-reduction"></a> terrain\_penalty\_reduction | Decreases the penalties given by terrain. | `terrain_penalty_reduction = 0.3` | Percentual. | Only works in the unit\_leader scope despite the modifier being present in vanilla national spirits at the time of writing. | 1.0 |
| <a id="org-loss-at-low-org-factor"></a> org\_loss\_at\_low\_org\_factor | Modifies the organisation loss for units when they have low organisation. | `org_loss_at_low_org_factor = 0.2` | Percentual. |  | 1.0 |
| <a id="org-loss-when-moving"></a> org\_loss\_when\_moving | Modifies the organisation loss for units when they are moving. | `org_loss_when_moving = 0.2` | Percentual. |  | 1.0 |
| <a id="planning-speed"></a> planning\_speed | Modifies the planning speed. | `planning_speed = 0.2` | Percentual. | Works in state scope. | 1.0 |
| <a id="experience-gain-unit-combat-factor"></a> experience\_gain\_<unit type>\_combat\_factor | Modifies the experience gain in combat for the unit type. | `experience_gain_artillery_combat_factor = 0.3` | Percentual. | Units are defined in /Hearts of Iron IV/common/units/\*.txt files. | 1.11 |
| <a id="experience-gain-unit-training-factor"></a> experience\_gain\_<unit type>\_training\_factor | Modifies the experience gain in training for the unit type. | `experience_gain_destroyer_training_factor = 0.3` | Percentual. | Units are defined in /Hearts of Iron IV/common/units/\*.txt files. | 1.11 |

#### <a id="naval-invasions"></a>Naval invasions

Invasion-related country-scoped modifiers:
| Name | Effects | Examples | Modifier type | Notes | Version added |
| --- | --- | --- | --- | --- | --- |
| <a id="naval-invasion-prep-speed"></a> naval\_invasion\_prep\_speed | Modifies the speed at which a naval invasion is prepared. | `naval_invasion_prep_speed = 10` | Flat. | Can be a targeted modifier or in unit leader scope. | 1.0 |
| <a id="naval-invasion-capacity"></a> naval\_invasion\_capacity | Modifies the amount of divisions that can have a naval invasion plan going on at the same time. | `naval_invasion_capacity = 10` | Flat. |  | 1.0 |
| <a id="naval-invasion-penalty"></a> naval\_invasion\_penalty | Modifies the penalty for naval invasions. | `naval_invasion_penalty = 0.3` | Percentual. | Is the opposite of amphibious\_invasion\_defence. Can also apply in state scope. | 1.0 |
| <a id="naval-invasion-planning-bonus-speed"></a> naval\_invasion\_planning\_bonus\_speed | Modifies the speed at which the planning bonus is accumulated during a naval invasion preparation. | `naval_invasion_planning_bonus_speed = 0.3` | Percentual. |  | 1.11 |
| <a id="amphibious-invasion"></a> amphibious\_invasion | Modifies the speed of units during naval invasions. | `amphibious_invasion = 0.5` | Percentual. |  | 1.6 |
| <a id="amphibious-invasion-defence"></a> amphibious\_invasion\_defence | Modifies the penalty given by naval invasions. | `amphibious_invasion_defence = 0.5` | Percentual. | Is the opposite of naval\_invasion\_penalty. Can also apply in state scope. | 1.6 |
| <a id="invasion-preparation"></a> invasion\_preparation | Modifies the required preparation needed to execute a naval invasion. | `invasion_preparation = 0.3` | Percentual. | Is the opposite of naval\_invasion\_prep\_speed. Can be used in unit leader scope. | 1.6 |

#### <a id="naval-combat"></a>Naval combat

Note that most of these modifiers are not only in country scope but also in navy leader scope as well as within equipment modules.

Naval combat-related country-scoped modifiers:
| Name | Effects | Examples | Modifier type | Notes | Version added |
| --- | --- | --- | --- | --- | --- |
| <a id="convoy-escort-efficiency"></a> convoy\_escort\_efficiency | Modifies the efficiency of the convoy escort mission. | `convoy_escort_efficiency = 0.5` | Percentual. |  | 1.6 |
| <a id="convoy-raiding-efficiency-factor"></a> convoy\_raiding\_efficiency\_factor | Modifies the efficiency of the convoy raiding mission. | `convoy_raiding_efficiency_factor = 0.5` | Percentual. |  | 1.6 |
| <a id="convoy-retreat-speed"></a> convoy\_retreat\_speed | Modifies the speed of convoys retreating. | `convoy_retreat_speed = 0.5` | Percentual. |  | 1.6 |
| <a id="critical-receive-chance"></a> critical\_receive\_chance | Changes the chance for the enemy to get a critical hit on us in naval combat. | `critical_receive_chance = 0.5` | Percentual. |  | 1.6 |
| <a id="experience-gain-navy-unit"></a> experience\_gain\_navy\_unit | Modifies the daily gain of experience by the ships. | `experience_gain_navy_unit = 0.02` | Flat. |  | 1.6 |
| <a id="experience-gain-navy-unit-factor"></a> experience\_gain\_navy\_unit\_factor | Modifies the gain of experience by the ships by a percentage. | `experience_gain_navy_unit_factor = 0.3` | Percentual. |  | 1.6 |
| <a id="mines-planting-by-fleets-factor"></a> mines\_planting\_by\_fleets\_factor | Modifies the efficiency of the mine planting mission. | `mines_planting_by_fleets_factor = 0.3` | Percentual. |  | 1.6 |
| <a id="mines-sweeping-by-fleets-factor"></a> mines\_sweeping\_by\_fleets\_factor | Modifies the efficiency of the mine sweeping mission. | `mines_sweeping_by_fleets_factor = 0.3` | Percentual. |  | 1.6 |
| <a id="naval-accidents-chance"></a> naval\_accidents\_chance | Modifies the chance for a ship to be accidentally sunk or damaged. | `naval_accidents_chance = 0.3` | Percentual. |  | 1.6 |
| <a id="navy-anti-air-attack"></a> navy\_anti\_air\_attack | Modifies the attack against enemy airplanes for the country's ships. | `navy_anti_air_attack = 5` | Flat. |  | 1.6 |
| <a id="navy-anti-air-attack-factor"></a> navy\_anti\_air\_attack\_factor | Modifies the attack against enemy airplanes for the country's ships by a percentage. | `navy_anti_air_attack_factor = 0.3` | Percentual. |  | 1.6 |
| <a id="naval-coordination"></a> naval\_coordination | Modifies how quickly the fleet can gather or disperse when a target is found or when switching missions. | `naval_coordination = 0.3` | Percentual. |  | 1.6 |
| <a id="naval-critical-effect-factor"></a> naval\_critical\_effect\_factor | Modifies the effects of sustained critical hits on our ships. | `naval_critical_effect_factor = 0.3` | Percentual. |  | 1.6 |
| <a id="naval-critical-score-chance-factor"></a> naval\_critical\_score\_chance\_factor | Modifies the chance for us to get a critical hit on the enemy in naval combat. | `naval_critical_score_chance_factor = 0.3` | Percentual. |  | 1.6 |
| <a id="naval-damage-factor"></a> naval\_damage\_factor | Modifies the damage dealt by our ships. | `naval_damage_factor = 0.3` | Percentual. |  | 1.6 |
| <a id="naval-defense-factor"></a> naval\_defense\_factor | Modifies the damage received by our ships. | `naval_defense_factor = 0.3` | Percentual. |  | 1.6 |
| <a id="naval-detection"></a> naval\_detection | Modifies the chance for our ships to detect submarines. | `naval_detection = 0.3` | Percentual. |  | 1.6 |
| <a id="naval-enemy-fleet-size-ratio-penalty-factor"></a> naval\_enemy\_fleet\_size\_ratio\_penalty\_factor | Modifies the penalty the enemy receives for having a larger amount of ships than us. | `naval_enemy_fleet_size_ratio_penalty_factor = 0.3` | Percentual. |  | 1.6 |
| <a id="naval-enemy-positioning-in-initial-attack"></a> naval\_enemy\_positioning\_in\_initial\_attack | Modifies the positioning of the enemy during the initial naval attack. | `naval_enemy_positioning_in_initial_attack = 3` | Flat. |  | 1.11 |
| <a id="naval-enemy-retreat-chance"></a> naval\_enemy\_retreat\_chance | Modifies the chance for the enemy to retreat. | `naval_enemy_retreat_chance = 0.3` | Percentual. |  | 1.6 |
| <a id="naval-has-potf-in-combat-attack"></a> naval\_has\_potf\_in\_combat\_attack | Modifies the attack of the navy when fighting together with the pride of the fleet. | `naval_has_potf_in_combat_attack = 0.3` | Percentual. |  | 1.6 |
| <a id="naval-has-potf-in-combat-defense"></a> naval\_has\_potf\_in\_combat\_defense | Modifies the defense of the navy when fighting together with the pride of the fleet. | `naval_has_potf_in_combat_defense = 0.3` | Percentual. |  | 1.6 |
| <a id="naval-hit-chance"></a> naval\_hit\_chance | Modifies the chance for the naval attacks to land. | `naval_hit_chance = 0.3` | Percentual. |  | 1.6 |
| <a id="naval-mine-hit-chance"></a> naval\_mine\_hit\_chance | Modifies the chance for a naval mine to hit. | `naval_mine_hit_chance = 0.3` | Percentual. |  | 1.6 |
| <a id="naval-mines-damage-factor"></a> naval\_mines\_damage\_factor | Modifies the damage naval mines deal to enemy ships. | `naval_mines_damage_factor = 0.3` | Percentual. |  | 1.6 |
| <a id="naval-mines-effect-reduction"></a> naval\_mines\_effect\_reduction | Modifies the damage enemy naval mines deal. | `naval_mines_effect_reduction = 0.3` | Percentual. |  | 1.6 |
| <a id="naval-morale"></a> naval\_morale | Modifies the navy recovery rate. | `naval_morale = 15` | Flat. |  | 1.6 |
| <a id="naval-morale-factor"></a> naval\_morale\_factor | Modifies the navy recovery rate by a percentage. | `naval_morale_factor = 0.3` | Percentual. |  | 1.6 |
| <a id="naval-night-attack"></a> naval\_night\_attack | Modifies the damage dealt by the country's ships at night. | `naval_night_attack = 0.3` | Percentual. |  | 1.11 |
| <a id="naval-retreat-chance"></a> naval\_retreat\_chance | Modifies the chance for the country's ships to retreat. | `naval_retreat_chance = 0.3` | Percentual. |  | 1.6 |
| <a id="naval-retreat-chance-after-initial-combat"></a> naval\_retreat\_chance\_after\_initial\_combat | Modifies the chance for the country's ships to retreat after initial combat. | `naval_retreat_chance_after_initial_combat = 0.3` | Percentual. |  | 1.11 |
| <a id="naval-retreat-speed"></a> naval\_retreat\_speed | Modifies the speed at which the country's ships retreat. | `naval_retreat_speed = 0.3` | Percentual. |  | 1.6 |
| <a id="naval-retreat-speed-after-initial-combat"></a> naval\_retreat\_speed\_after\_initial\_combat | Modifies the speed at which the country's ships to retreat after initial combat. | `naval_retreat_speed_after_initial_combat = 0.3` | Percentual. |  | 1.11 |
| <a id="naval-speed-factor"></a> naval\_speed\_factor | Modifies the speed of the country's ships. | `naval_speed_factor = 0.3` | Percentual. |  | 1.6 |
| <a id="navy-org"></a> navy\_org | Modifies the navy's organisation. | `navy_org = 10` | Flat. |  | 1.0 |
| <a id="navy-org-factor"></a> navy\_org\_factor | Modifies the navy's organisation by a percentage. | `navy_org_factor = 0.3` | Percentual. |  | 1.0 |
| <a id="navy-max-range"></a> navy\_max\_range | Modifies the navy's maximum range. | `navy_max_range = 10` | Flat. |  | 1.0 |
| <a id="navy-max-range-factor"></a> navy\_max\_range\_factor | Modifies the navy's maximum range by a percentage. | `navy_max_range_factor = 0.3` | Percentual. |  | 1.0 |
| <a id="naval-torpedo-cooldown-factor"></a> naval\_torpedo\_cooldown\_factor | Modifies the rate at which the country's ships can fire torpedos. | `naval_torpedo_cooldown_factor = 0.3` | Percentual. |  | 1.6 |
| <a id="naval-torpedo-hit-chance-factor"></a> naval\_torpedo\_hit\_chance\_factor | Modifies the likelihood for country's torpedos to hit enemy ships. | `naval_torpedo_hit_chance_factor = 0.3` | Percentual. |  | 1.6 |
| <a id="naval-torpedo-reveal-chance-factor"></a> naval\_torpedo\_reveal\_chance\_factor | Modifies the chance that the country's submarines reveal themselves when firing torpedos. | `naval_torpedo_reveal_chance_factor = 0.3` | Percentual. |  | 1.6 |
| <a id="naval-torpedo-screen-penetration-factor"></a> naval\_torpedo\_screen\_penetration\_factor | Modifies the rate at which the country's torpedos penalise enemy screening. | `naval_torpedo_screen_penetration_factor = 0.3` | Percentual. |  | 1.6 |
| <a id="naval-torpedo-damage-reduction-factor"></a> naval\_torpedo\_damage\_reduction\_factor | Modifies the damage at which enemy torpedos damage the country's ships. | `naval_torpedo_damage_reduction_factor = 0.3` | Percentual. |  | 1.12 |
| <a id="naval-torpedo-enemy-critical-chance-factor"></a> naval\_torpedo\_enemy\_critical\_chance\_factor | Modifies the chance for an enemy torpedo to get a cricical hit against the country's ships. | `naval_torpedo_enemy_critical_chance_factor = 0.3` | Percentual. |  | 1.12 |
| <a id="naval-light-gun-hit-chance-factor"></a> naval\_light\_gun\_hit\_chance\_factor | Modifies the chance for the country's naval light guns to hit enemy ships. | `naval_light_gun_hit_chance_factor = 0.3` | Percentual. |  | 1.12 |
| <a id="naval-heavy-gun-hit-chance-factor"></a> naval\_heavy\_gun\_hit\_chance\_factor | Modifies the chance for the country's naval heavy guns to hit enemy ships. | `naval_heavy_gun_hit_chance_factor = 0.3` | Percentual. |  | 1.12 |
| <a id="navy-capital-ship-attack-factor"></a> navy\_capital\_ship\_attack\_factor | Modifies the attack of the country's capital ships. | `navy_capital_ship_attack_factor = 0.3` | Percentual. |  | 1.6 |
| <a id="navy-capital-ship-defence-factor"></a> navy\_capital\_ship\_defence\_factor | Modifies the defence of the country's capital ships. | `navy_capital_ship_defence_factor = 0.3` | Percentual. |  | 1.6 |
| <a id="navy-screen-attack-factor"></a> navy\_screen\_attack\_factor | Modifies the attack of the country's screening ships. | `navy_screen_attack_factor = 0.3` | Percentual. |  | 1.6 |
| <a id="navy-screen-defence-factor"></a> navy\_screen\_defence\_factor | Modifies the defence of the country's screening ships. | `navy_screen_defence_factor = 0.3` | Percentual. |  | 1.6 |
| <a id="navy-submarine-attack-factor"></a> navy\_submarine\_attack\_factor | Modifies the attack of the country's submarines. | `navy_submarine_attack_factor = 0.3` | Percentual. |  | 1.6 |
| <a id="navy-submarine-defence-factor"></a> navy\_submarine\_defence\_factor | Modifies the defence of the country's submarines. | `navy_submarine_defence_factor = 0.3` | Percentual. |  | 1.6 |
| <a id="navy-submarine-detection-factor"></a> navy\_submarine\_detection\_factor | Modifies the country's detection of enemy submarines. | `navy_submarine_detection_factor = 0.3` | Percentual. |  | 1.6 |
| <a id="navy-visibility"></a> navy\_visibility | Modifies the visibility of the country's navy. | `navy_visibility = 0.3` | Percentual. |  | 1.6 |
| <a id="navy-weather-penalty"></a> navy\_weather\_penalty | Modifies the penalty the country's navy gets during poor weather. | `navy_weather_penalty = 0.3` | Percentual. |  | 1.11 |
| <a id="night-spotting-chance"></a> night\_spotting\_chance | Modifies the chance for the country's navy to spot the enemy at night. | `night_spotting_chance = 0.3` | Percentual. |  | 1.11 |
| <a id="positioning"></a> positioning | Modifies the positioning of the country's navy. | `positioning = 0.3` | Percentual. |  | 1.6 |
| <a id="repair-speed-factor"></a> repair\_speed\_factor | Modifies the speed at which the dockyards repair the navy. | `repair_speed_factor = 0.3` | Percentual. |  | 1.6 |
| <a id="screening-efficiency"></a> screening\_efficiency | Modifies the efficiency screen ships operate. | `screening_efficiency = 0.3` | Percentual. |  | 1.6 |
| <a id="screening-without-screens"></a> screening\_without\_screens | Modifies the base screening without any screen ships assigned. | `screening_without_screens = 0.3` | Percentual. |  | 1.11 |
| <a id="ships-at-battle-start"></a> ships\_at\_battle\_start | Modifies the number of ships at first contact. | `ships_at_battle_start = 0.3` | Percentual. |  | 1.6 |
| <a id="spotting-chance"></a> spotting\_chance | Modifies the chance to spot enemy ships. | `spotting_chance = 0.3` | Percentual. |  | 1.6 |
| <a id="strike-force-movement-org-loss"></a> strike\_force\_movement\_org\_loss | Modifies the organisation loss from movement during the strike force mission. | `strike_force_movement_org_loss = 0.3` | Percentual. |  | 1.6 |
| <a id="sub-retreat-speed"></a> sub\_retreat\_speed | Modifies the retreat speed of submarines. | `sub_retreat_speed = 0.3` | Percentual. |  | 1.6 |
| <a id="submarine-attack"></a> submarine\_attack | Modifies the attack of submarines. | `submarine_attack = 0.3` | Percentual. |  | 1.6 |

#### <a id="carriers-and-their-planes"></a>Carriers and their planes

Carrier-related country-scoped modifiers:
| Name | Effects | Examples | Modifier type | Notes | Version added |
| --- | --- | --- | --- | --- | --- |
| <a id="navy-carrier-air-agility-factor"></a> navy\_carrier\_air\_agility\_factor | Modifies the agility of airplanes executing tasks from carriers. | `navy_carrier_air_agility_factor = 0.3` | Percentual. |  | 1.6 |
| <a id="navy-carrier-air-attack-factor"></a> navy\_carrier\_air\_attack\_factor | Modifies the attack of airplanes executing tasks from carriers. | `navy_carrier_air_attack_factor = 0.3` | Percentual. |  | 1.6 |
| <a id="navy-carrier-air-targetting-factor"></a> navy\_carrier\_air\_targetting\_factor | Modifies the targeting of airplanes executing tasks from carriers. | `navy_carrier_air_targetting_factor = 0.3` | Percentual. |  | 1.6 |
| <a id="air-carrier-night-penalty-reduction-factor"></a> air\_carrier\_night\_penalty\_reduction\_factor | Modifies the reduction of the night penalty for air carriers. | `air_carrier_night_penalty_reduction_factor = 0.5` | Percentual. |  | 1.0 |
| <a id="carrier-capacity-penalty-reduction"></a> carrier\_capacity\_penalty\_reduction | Modifies the penalty given by overcrowding a carrier with planes. | `carrier_capacity_penalty_reduction = 0.5` | Percentual. |  | 1.6 |
| <a id="carrier-traffic"></a> carrier\_traffic | Modifies the traffic of carriers. | `carrier_traffic = 0.5` | Percentual. |  | 1.6 |
| <a id="sortie-efficiency"></a> sortie\_efficiency | Modifies the speed when refueling and rearming planes on the carrier during the battle. | `sortie_efficiency = 0.3` | Percentual. |  | 1.6 |
| <a id="carrier-sortie-hours-delay"></a> carrier\_sortie\_hours\_delay | Modifies the delay in hours for refueling and rearming planes on the carrier. | `carrier_sortie_hours_delay = 2` | Flat. |  | 1.12 |
| <a id="carrier-night-traffic"></a> carrier\_night\_traffic | Modifies the traffic of carriers at night. | `carrier_night_traffic = 0.5` | Percentual. |  | 1.11 |
| <a id="fighter-sortie-efficiency"></a> fighter\_sortie\_efficiency | Modifies the speed when refueling and rearming fighter planes on the carrier during the battle. | `fighter_sortie_efficiency = 0.3` | Percentual. |  | 1.6 |

#### <a id="air-combat"></a>Air combat

Note that most of these modifiers are not only in country scope but also in ace scope.

Air-related country-scoped modifiers:
| Name | Effects | Examples | Modifier type | Notes | Version added |
| --- | --- | --- | --- | --- | --- |
| <a id="air-accidents-factor"></a> air\_accidents\_factor | Modifies the chance for air accidents to happen. | `air_accidents_factor = 0.5` | Percentual. |  | 1.0 |
| <a id="air-ace-bonuses-factor"></a> air\_ace\_bonuses\_factor | Modifies the bonuses the aces grant. | `air_ace_bonuses_factor = 0.5` | Percentual. |  | 1.11 |
| <a id="air-ace-generation-chance-factor"></a> air\_ace\_generation\_chance\_factor | Modifies the chance for aces to appear. | `air_ace_generation_chance_factor = 0.5` | Percentual. |  | 1.11 |
| <a id="ace-effectiveness-factor"></a> ace\_effectiveness\_factor | Modifies the effectiveness of aces | `ace_effectiveness_factor = 0.5` | Percentual. |  | 1.0 |
| <a id="air-agility-factor"></a> air\_agility\_factor | Modifies the agility of the country's airplanes. | `air_agility_factor = 0.5` | Percentual. |  | 1.0 |
| <a id="air-attack-factor"></a> air\_attack\_factor | Modifies the attack of the country's airplanes. | `air_attack_factor = 0.5` | Percentual. |  | 1.0 |
| <a id="air-defence-factor"></a> air\_defence\_factor | Modifies the defence of the country's airplanes. | `air_defence_factor = 0.5` | Percentual. |  | 1.0 |
| <a id="air-interception-detect-factor"></a> air\_interception\_detect\_factor | Modifies the chance of detecting an enemy plane while on interception mission. | `air_interception_detect_factor = 0.5` | Percentual. |  | 1.0 |
| <a id="naval-strike-targetting-factor"></a> naval\_strike\_targetting\_factor | Modifies the ability of planes to target their objectives when executing naval strikes. | `naval_strike_targetting_factor = 0.5` | Percentual. |  | 1.0 |
| <a id="port-strike"></a> port\_strike | Modifies the damage done by planes on the port strike mission. | `port_strike = 0.5` | Percentual. |  | 1.0 |
| <a id="air-close-air-support-org-damage-factor"></a> air\_close\_air\_support\_org\_damage\_factor | Modifies the damage to division organisation by planes on the close air support mission. | `air_close_air_support_org_damage_factor = 0.5` | Percentual. |  | 1.11 |
| <a id="air-bombing-targetting"></a> air\_bombing\_targetting | Modifies targetting for ground bombing. | `air_bombing_targetting = 0.5` | Percentual. |  | 1.0 |
| <a id="air-cas-efficiency"></a> air\_cas\_efficiency | Modifies efficiency of close-air-support. | `air_cas_efficiency = 0.5` | Percentual. |  | 1.0 |
| <a id="air-cas-present-factor"></a> air\_cas\_present\_factor | Modifies impact of close-air-support in land combat. | `air_cas_present_factor = 0.5` | Percentual. |  | 1.0 |
| <a id="air-escort-efficiency"></a> air\_escort\_efficiency | Modifies ability of planes in dogfights. | `air_escort_efficiency = 0.5` | Percentual. |  | 1.0 |
| <a id="air-home-defence-factor"></a> air\_home\_defence\_factor | Modifies the defence of airplanes when defending states in the home region (Connected to the country's capital by land) | `air_home_defence_factor = 0.5` | Percentual. |  | 1.11 |
| <a id="air-intercept-efficiency"></a> air\_intercept\_efficiency | Modifies the efficiency of air interception. | `air_intercept_efficiency = 0.5` | Percentual. |  | 1.0 |
| <a id="air-manpower-requirement-factor"></a> air\_manpower\_requirement\_factor | Modifies the manpower required to deploy an airplane. | `air_manpower_requirement_factor = -0.5` | Percentual. |  | 1.11 |
| <a id="air-maximum-speed-factor"></a> air\_maximum\_speed\_factor | Modifies the maximum speed of the airforce. | `air_maximum_speed_factor = 0.5` | Percentual. |  | 1.0 |
| <a id="air-mission-efficiency"></a> air\_mission\_efficiency | Modifies the efficiency of airplanes in missions. | `air_mission_efficiency = 0.5` | Percentual. |  | 1.0 |
| <a id="air-mission-xp-gain-factor"></a> air\_mission\_xp\_gain\_factor | Modifies the experience gain for airplanes for doing missions. | `air_mission_xp_gain_factor = 0.5` | Percentual. |  | 1.0 |
| <a id="air-nav-efficiency"></a> air\_nav\_efficiency | Modifies the efficiency of airplanes doing port strike and naval bombing missions. | `air_nav_efficiency = 0.5` | Percentual. |  | 1.0 |
| <a id="air-night-penalty"></a> air\_night\_penalty | Modifies the penalty the airforce receives while at night. | `air_night_penalty = 0.5` | Percentual. |  | 1.0 |
| <a id="air-power-projection-factor"></a> air\_power\_projection\_factor | Modifies the power projection given out by the airplanes. | `air_power_projection_factor = 0.5` | Percentual. |  | 1.0 |
| <a id="air-range-factor"></a> air\_range\_factor | Modifies the range of the airplanes. | `air_range_factor = 0.5` | Percentual. |  | 1.0 |
| <a id="air-strategic-bomber-bombing-factor"></a> air\_strategic\_bomber\_bombing\_factor | Modifies the efficiency of the strategic bombing mission. | `air_strategic_bomber_bombing_factor = 0.5` | Percentual. |  | 1.0 |
| <a id="air-strategic-bomber-night-penalty"></a> air\_strategic\_bomber\_night\_penalty | Modifies the penalty for the strategic bombing mission while at night. | `air_strategic_bomber_night_penalty = 0.5` | Percentual. |  | 1.0 |
| <a id="air-superiority-detect-factor"></a> air\_superiority\_detect\_factor | Modifies the chance to detect enemy planes while on the air superiority mission. Displays as Fighter Detection. | `air_superiority_detect_factor = 0.5` | Percentual. |  | 1.0 |
| <a id="air-superiority-efficiency"></a> air\_superiority\_efficiency | Modifies the efficiency of the air superiority mission. | `air_superiority_efficiency = 0.5` | Percentual. |  | 1.0 |
| <a id="air-training-xp-gain-factor"></a> air\_training\_xp\_gain\_factor | Modifies the air experience gain from training. | `air_training_xp_gain_factor = 0.5` | Percentual. |  | 1.6 |
| <a id="air-untrained-pilots-penalty-factor"></a> air\_untrained\_pilots\_penalty\_factor | Modifies the penalty given to airplanes which don't have enough experience. | `air_untrained_pilots_penalty_factor = 0.5` | Percentual. |  | 1.6 |
| <a id="air-weather-penalty"></a> air\_weather\_penalty | Modifies the penalty the airplanes receive because of weather. | `air_weather_penalty = 0.5` | Percentual. |  | 1.0 |
| <a id="air-wing-xp-loss-when-killed-factor"></a> air\_wing\_xp\_loss\_when\_killed\_factor | Modifies the experience loss of airplanes due to airplanes being shot down. | `air_wing_xp_loss_when_killed_factor = 0.5` | Percentual. |  | 1.0 |
| <a id="army-bonus-air-superiority-factor"></a> army\_bonus\_air\_superiority\_factor | Modifies the bonus to land combat from air superiority. | `army_bonus_air_superiority_factor = 0.5` | Percentual. |  | 1.0 |
| <a id="enemy-army-bonus-air-superiority-factor"></a> enemy\_army\_bonus\_air\_superiority\_factor | Modifies the effect to land combat from enemy air superiority. | `enemy_army_bonus_air_superiority_factor = 0.5` | Percentual. |  | 1.0 |
| <a id="ground-attack-factor"></a> ground\_attack\_factor | Modifies the bonus to airplane attack on enemy divisions by a percentage. | `ground_attack_factor = 0.5` | Percentual. |  | 1.0 |
| <a id="mines-planting-by-air-factor"></a> mines\_planting\_by\_air\_factor | Modifies efficiency of airplanes planting mines. | `mines_planting_by_air_factor = 0.5` | Percentual. |  | 1.0 |
| <a id="mines-sweeping-by-air-factor"></a> mines\_sweeping\_by\_air\_factor | Modifies efficiency of airplanes sweeping mines. | `mines_sweeping_by_air_factor = 0.5` | Percentual. |  | 1.0 |
| <a id="strategic-bomb-visibility"></a> strategic\_bomb\_visibility | Modifies the chance for the enemy to detect our strategic bombers. | `strategic_bomb_visibility = 0.5` | Percentual. |  | 1.0 |
| <a id="rocket-attack-factor"></a> rocket\_attack\_factor | Modifies the attack given to rockets. | `rocket_attack_factor = 0.5` | Percentual. |  | 1.0 |

#### <a id="targeted-modifiers"></a>Targeted modifiers

These modifiers are targeted, meaning that they must be used in a block for targeted modifiers rather than regular modifiers. These include `targeted_modifier = { ... }` in ideas, traits, advisors, and decisions; [relation modifiers](#relation-modifiers).  
A `targeted_modifier` block is structured as such:

```text
targeted_modifier = {
    tag = FROM    # this can also take a variable that stores a scope
    attack_bonus_against = 0.1
    defense_bonus_against = 0.1
}
```

**This is a completely separate block from `modifier = { ... }`** in ideas, advisors, and decisions; as such it will not work when it's put inside of `modifier = { ... }`.

Targeted modifiers:
| Name | Effects | Examples | Modifier type | Notes | Version added |
| --- | --- | --- | --- | --- | --- |
| <a id="extra-trade-to-target-factor"></a> extra\_trade\_to\_target\_factor | Adds extra produced resources available for trade to target country. | `extra_trade_to_target_factor = 0.5` | Percentual. |  | 1.5 |
| <a id="generate-wargoal-tension-against"></a> generate\_wargoal\_tension\_against | Changes world tension necessary for us to justify against the target country. | `generate_wargoal_tension_against = 0.5` | Flat. |  | 1.5 |
| <a id="cic-to-target-factor"></a> cic\_to\_target\_factor | Gives a portion of the country's civilian industry to the specified target. | `cic_to_target_factor = 0.5` | Percentual. |  | 1.5 |
| <a id="mic-to-target-factor"></a> mic\_to\_target\_factor | Gives a portion of the country's military industry to the specified target. | `mic_to_target_factor = 0.5` | Percentual. |  | 1.5 |
| <a id="trade-cost-for-target-factor"></a> trade\_cost\_for\_target\_factor | The cost for the targeted country to purchase this country's resources. | `trade_cost_for_target_factor = 0.5` | Percentual. |  | 1.5 |
| <a id="targeted-legitimacy-daily"></a> targeted\_legitimacy\_daily | Changes daily gain of legitimacy of the target country. | `targeted_legitimacy_daily = 0.5` | Flat. |  | 1.6 |
| <a id="attack-bonus-against"></a> attack\_bonus\_against | Gives an attack bonus against the armies of the specified country. | `attack_bonus_against = 0.5` | Percentual. | Due to a bug, this will not apply to units that are defending. | 1.5 |
| <a id="attack-bonus-against-cores"></a> attack\_bonus\_against\_cores | Gives an attack bonus against the armies of the specified country on its core territory. | `attack_bonus_against_cores = 0.5` | Percentual. |  | 1.5 |
| <a id="breakthrough-bonus-against"></a> breakthrough\_bonus\_against | Gives a breakthrough bonus against the armies of the specified country. | `breakthrough_bonus_against = 0.5` | Percentual. |  | 1.5 |
| <a id="defense-bonus-against"></a> defense\_bonus\_against | Gives a defense bonus against the armies of the specified country. | `defense_bonus_against = 0.5` | Percentual. | Due to a bug, this will not apply to units that are attacking. | 1.5 |

### <a id="state-scope"></a>State scope

Several country-scoped modifiers (such as a portion of those in the [land combat section](#land-combat)) unlisted here can go into state scope. A large portion of state-scoped modifiers can go into province scope.

State-scoped modifiers:
| Name | Effects | Examples | Modifier type | Notes | Version added |
| --- | --- | --- | --- | --- | --- |
| <a id="army-speed-factor-for-controller"></a> army\_speed\_factor\_for\_controller | Changes the division speed for the controller of the state. | `army_speed_factor_for_controller = 0.5` | Percentual. |  | 1.0 |
| <a id="attrition-for-controller"></a> attrition\_for\_controller | Changes the attrition for the controller of the state. | `attrition_for_controller = 0.5` | Percentual. |  | 1.0 |
| <a id="equipment-capture-for-controller"></a> equipment\_capture\_for\_controller | Changes the equipment capture ratio by the state's controller. | `equipment_capture_for_controller = 0.3` | Flat. |  | 1.13 |
| <a id="equipment-capture-factor-for-controller"></a> equipment\_capture\_factor\_for\_controller | Modifies the equipment capture ratio by the state's controller. | `equipment_capture_factor_for_controller = 0.3` | Percentual. |  | 1.13 |
| <a id="enemy-army-speed-factor"></a> enemy\_army\_speed\_factor | Modifies the speed of divisions at war with the state's owner. | `enemy_army_speed_factor = 0.3` | Percentual. |  | 1.13 |
| <a id="enemy-local-supplies"></a> enemy\_local\_supplies | Modifies the supply of divisions at war with the state's owner. | `enemy_local_supplies = 0.3` | Percentual. |  | 1.13 |
| <a id="enemy-attrition"></a> enemy\_attrition | Modifies the attrition of divisions at war with the state's owner. | `enemy_attrition = 0.3` | Percentual. |  | 1.13 |
| <a id="enemy-truck-attrition-factor"></a> enemy\_truck\_attrition\_factor | Modifies the truck attrition of divisions at war with the state's owner. | `enemy_truck_attrition_factor = 0.3` | Percentual. |  | 1.13 |
| <a id="compliance-gain"></a> compliance\_gain | Changes the compliance gain in the current state. | `compliance_gain = 0.01` | Flat. | Can also go into country scope. Can also be used as a targeted modifier. | 1.9 |
| <a id="compliance-growth"></a> compliance\_growth | Changes the compliance growth speed in the current state. | `compliance_growth = 0.5` | Percentual. | Can also go into country scope. | 1.9 |
| <a id="disable-strategic-redeployment"></a> disable\_strategic\_redeployment | Disables strategic redeployment in the state. | `disable_strategic_redeployment = 1` | Boolean (only 1). |  | 1.9 |
| <a id="disable-strategic-redeployment-for-controller"></a> disable\_strategic\_redeployment\_for\_controller | Disables strategic redeployment in the state for the controller. | `disable_strategic_redeployment_for_controller = 1` | Boolean (only 1). |  | 1.9 |
| <a id="enemy-intel-network-gain-factor-over-occupied-tag"></a> enemy\_intel\_network\_gain\_factor\_over\_occupied\_tag | Modifies enemy intel network strength gain. | `enemy_intel_network_gain_factor_over_occupied_tag = 0.3` | Percentual. |  | 1.9 |
| <a id="local-building-slots"></a> local\_building\_slots | Modifies amount of building slots. | `local_building_slots = 2` | Flat. |  | 1.9 |
| <a id="local-building-slots-factor"></a> local\_building\_slots\_factor | Modifies amount of building slots by a percentage. | `local_building_slots_factor = 0.3` | Percentual. |  | 1.9 |
| <a id="local-factories"></a> local\_factories | Modifies amount of available factories in the state. | `local_factories = 0.3` | Percentual. |  | 1.9 |
| <a id="local-factory-energy-consumption"></a> local\_factory\_energy\_consumption | Modifies amount of energy consumed by factories in the state. | `local_factory_energy_consumption = 0.2` | Percentual | The game file documentation incorrectly labels this as a number with zero decimals, yet the code itself uses a decimal, | 1.17 |
| <a id="local-factory-energy-consumption-per-infrastructure"></a> local\_factory\_energy\_consumption\_per\_infrastructure | Modifies amount of energy consumed by factories depending on the infrastructure of the state. | `local_factory_energy_consumption_per_infrastructure = 0.2` | Percentual |  | 1.17.2 |
| <a id="local-factory-sabotage"></a> local\_factory\_sabotage | Modifies chance for factory sabotage. | `local_factory_sabotage = 0.3` | Percentual. |  | 1.9 |
| <a id="local-intel-to-enemies"></a> local\_intel\_to\_enemies | Modifies amount of intel to enemies. | `local_intel_to_enemies = 0.3` | Percentual. |  | 1.9 |
| <a id="local-manpower"></a> local\_manpower | Modifies amount of available manpower. | `local_manpower = 0.3` | Percentual. |  | 1.4 |
| <a id="local-non-core-manpower"></a> local\_non\_core\_manpower | Modifies amount of available non-core manpower. | `local_non_core_manpower = 0.3` | Percentual. |  | 1.3.3 |
| <a id="local-org-regain"></a> local\_org\_regain | Modifies how much organisation is regained after combat. | `local_org_regain = -0.3` | Percentual. | Can be used in provinces and strategic regions. | 1.0 |
| <a id="local-resource-gain-efficiency-per-infrastructure"></a> local\_resource\_gain\_efficiency\_per\_infrastructure | Modifies amount of available resources gained depending on the infrastructure of the state. | `local_resource_gain_efficiency_per_infrastructure = 0.3` | Percentual. |  | 1.17.2 |
| <a id="local-resources"></a> local\_resources | Modifies amount of available resources. | `local_resources = 0.3` | Flat. |  | 1.9 |
| <a id="local-supplies"></a> local\_supplies | Modifies amount of available supplies. | `local_supplies = 0.3` | Percentual. |  | 1.9 |
| <a id="local-supplies-for-controller"></a> local\_supplies\_for\_controller | Modifies amount of available supplies for the controller. | `local_supplies_for_controller = 0.3` | Percentual. |  | 1.9 |
| <a id="local-supply-impact-factor"></a> local\_supply\_impact\_factor | Modifies the impact that the state's local supplies have. | `local_supply_impact_factor = 0.3` | Percentual. |  | 1.12 |
| <a id="local-non-core-supply-impact-factor"></a> local\_non\_core\_supply\_impact\_factor | Modifies the impact that the state's local supplies have if the state is not cored by the controller of provinces within. | `local_non_core_supply_impact_factor = 0.3` | Percentual. |  | 1.12 |
| <a id="mobilization-speed"></a> mobilization\_speed | Modifies the mobilisation speed. | `mobilization_speed = 0.3` | Percentual. |  | 1.9 |
| <a id="non-core-manpower"></a> non\_core\_manpower | Modifies the amount of recruited non-core manpower. | `non_core_manpower = 0.3` | Percentual. |  | 1.9 |
| <a id="max-fuel-building"></a> max\_fuel\_building | Modifies the amount of fuel capacity, in thousands, given to the state controller from the building. | `max_fuel_building = 1500` | Percentual. | Does not have to be in a building. | 1.0 |
| <a id="recruitable-population"></a> recruitable\_population | Modifies the amount of recruited manpower. | `recruitable_population = 0.03` | Flat. |  | 1.9 |
| <a id="recruitable-population-factor"></a> recruitable\_population\_factor | Modifies the amount of recruited manpower by a percentage. | `recruitable_population_factor = 0.3` | Percentual. |  | 1.9 |
| <a id="resistance-damage-to-garrison"></a> resistance\_damage\_to\_garrison | Modifies the amount of resistance damage to the garrison. | `resistance_damage_to_garrison = 0.3` | Percentual. |  | 1.9 |
| <a id="resistance-decay"></a> resistance\_decay | Modifies the speed of resistance decay. | `resistance_decay = 0.3` | Percentual. |  | 1.9 |
| <a id="resistance-garrison-penetration-chance"></a> resistance\_garrison\_penetration\_chance | Modifies the chance for the garrison to be penetrated. | `resistance_garrison_penetration_chance = 0.3` | Percentual. |  | 1.9 |
| <a id="resistance-growth"></a> resistance\_growth | Modifies the speed of the resistance growth. | `resistance_growth = 0.3` | Percentual. |  | 1.9 |
| <a id="resistance-target"></a> resistance\_target | Modifies the target of the resistance growth. | `resistance_target = 0.3` | Percentual. |  | 1.9 |
| <a id="starting-compliance"></a> starting\_compliance | Modifies the base compliance value. | `starting_compliance = 0.3` | Percentual. |  | 1.9 |
| state\_bunker\_max\_level\_terrain\_limit | Modifies the amount of available bunker building slots in the state. | `state_bunker_max_level_terrain_limit = 6` | Flat. |  |  |
| state\_coastal\_bunker\_max\_level\_terrain\_limit | Modifies the amount of available coastal bunker building slots in the state. | `state_coastal_bunker_max_level_terrain_limit = 6` | Flat. |  |  |
| <a id="state-production-speed-building-factor"></a> state\_production\_speed\_<building>\_factor | Modifies the building speed of the specified building in the state. | `state_production_speed_industrial_complex_factor = 0.3` | Percentual. | Use state\_production\_speed\_buildings\_factor for it to apply to all buildings. (added in 1.9) | 1.9.1 |
| <a id="state-repair-speed-building-factor"></a> state\_repair\_speed\_<building>\_factor | Modifies the repair speed of the specified building in the state. | `state_repair_speed_industrial_complex_factor = 0.3` | Percentual. |  | 1.9.1 |
| <a id="state-resource-resource"></a> state\_resource\_<resource> | Modifies the amount of the specified resource in the state. | `state_resource_oil = 5` | Flat. |  | 1.0 |
| <a id="state-resources-factor"></a> state\_resources\_factor | Modifies the amount of resources in a state. | `state_resources_factor = 0.2` | Percentual. |  | 1.9 |
| <a id="state-resource-cost-resource"></a> state\_resource\_cost\_<resource> | Modifies the amount of the specified resource in the state. | `state_resource_cost_rubber = 5` | Flat. |  | 1.9 |
| <a id="temporary-state-resource-resource"></a> temporary\_state\_resource\_<resource> | Modifies the amount of the specified resource in the state as an added modifier after the base one. | `temporary_state_resource_tungsten = 5` | Flat. |  | 1.0 |
| <a id="enemy-operative-detection-chance-over-occupied-tag"></a> enemy\_operative\_detection\_chance\_over\_occupied\_tag | Offsets the chance for an enemy operative to be detected for the tag that occupies this state. | `enemy_operative_detection_chance_over_occupied_tag = 5` | Flat. |  | 1.9 |
| <a id="enemy-operative-detection-chance-factor-over-occupied-tag"></a> enemy\_operative\_detection\_chance\_factor\_over\_occupied\_tag | Modifies the chance for an enemy operative to be detected for the tag that occupies this state. | `enemy_operative_detection_chance_factor_over_occupied_tag = 0.5` | Percentual. |  | 1.9 |

### <a id="unit-leader-scope"></a>Unit leader scope

Note that most modifiers in land and naval combat sections also apply.

Unit leader-scoped modifiers:
| Name | Effects | Examples | Modifier type | Notes | Version added |
| --- | --- | --- | --- | --- | --- |
| <a id="cannot-use-abilities"></a> cannot\_use\_abilities | Disables using abilities. | `cannot_use_abilities = 1` | Boolean (only 1). |  | 1.5 |
| <a id="dont-lose-dig-in-on-attack"></a> dont\_lose\_dig\_in\_on\_attack | Disables losing the entrechment bonus during attack. | `dont_lose_dig_in_on_attack = 1` | Boolean (only 1). |  | 1.5 |
| <a id="exiled-divisions-attack-factor"></a> exiled\_divisions\_attack\_factor | Modifies the attack of divisions led by this unit leader if they're exiled. | `exiled_divisions_attack_factor = 0.4` | Percentual. |  | 1.6 |
| <a id="exiled-divisions-defense-factor"></a> exiled\_divisions\_defense\_factor | Modifies the defence of divisions led by this unit leader if they're exiled. | `exiled_divisions_defense_factor = 0.4` | Percentual. |  | 1.6 |
| <a id="own-exiled-divisions-attack-factor"></a> own\_exiled\_divisions\_attack\_factor | Modifies the attack of divisions led by this unit leader if they're exiled and belong to the same country. | `own_exiled_divisions_attack_factor = 0.4` | Percentual. |  | 1.6 |
| <a id="own-exiled-divisions-defense-factor"></a> own\_exiled\_divisions\_defense\_factor | Modifies the defence of divisions led by this unit leader if they're exiled and belong to the same country. | `own_exiled_divisions_defense_factor = 0.4` | Percentual. |  | 1.6 |
| <a id="experience-gain-factor"></a> experience\_gain\_factor | Modifies the experience gained by the unit leader. | `experience_gain_factor = 0.1` | Percentual. |  | 1.5 |
| <a id="fortification-collateral-chance"></a> fortification\_collateral\_chance | Chance for combat to damage enemy forts. | `fortification_collateral_chance = 0.4` | Percentual. |  | 1.5 |
| <a id="fortification-damage"></a> fortification\_damage | Damage enemy forts receive from combat. | `fortification_damage = 0.4` | Percentual. |  | 1.5 |
| <a id="max-commander-army-size"></a> max\_commander\_army\_size | Modifies amount of divisions that can be led by the army leader without penalty. | `max_commander_army_size = 12` | Flat. |  | 1.5 |
| <a id="max-army-group-size"></a> max\_army\_group\_size | Modifies amount of army groups that can be led by the field marshal without penalty. | `max_army_group_size = 1` | Flat. |  | 1.5 |
| <a id="paradrop-organization-factor"></a> paradrop\_organization\_factor | The amount of organisation paratroopers will have after paradropping. | `paradrop_organization_factor = 0.5` | Percentual. |  | 1.5 |
| <a id="paratrooper-aa-defense"></a> paratrooper\_aa\_defense | The strength of anti-air against paratroopers. | `paratrooper_aa_defense = 0.5` | Percentual. |  | 1.5 |
| <a id="paratrooper-weight-factor"></a> paratrooper\_weight\_factor | Paratrooper transport space factor. | `paratrooper_weight_factor = 0.5` | Percentual. | Can also be used in country scope. | 1.13 |
| <a id="promote-cost-factor"></a> promote\_cost\_factor | The cost to promote the unit leader. | `promote_cost_factor = 0.5` | Percentual. |  | 1.5 |
| <a id="reassignment-duration-factor"></a> reassignment\_duration\_factor | The length of the reassignment penalty. | `reassignment_duration_factor = 0.5` | Percentual. |  | 1.5 |
| <a id="river-crossing-factor"></a> river\_crossing\_factor | The effects of the river crossing penalty. | `river_crossing_factor = 0.5` | Percentual. |  | 1.5 |
| <a id="sickness-chance"></a> sickness\_chance | The chance for the unit leader to get sick. | `sickness_chance = 0.5` | Percentual. |  | 1.5 |
| <a id="skill-bonus-factor"></a> skill\_bonus\_factor | The bonus the unit leader receives from their skillset. | `skill_bonus_factor = 0.5` | Percentual. |  | 1.5 |
| <a id="trait-xp-gain-factor"></a> trait\_<trait>\_xp\_gain\_factor | Modifies the experience gain towards the specified trait. | `trait_infantry_leader_xp_gain_factor = 0.5` | Percentual. |  | 1.11 |
| <a id="terrain-trait-xp-gain-factor"></a> terrain\_trait\_xp\_gain\_factor | Modifies the experience gain towards all terrain traits (With the type of either basic\_terrain\_trait or assignable\_terrain\_trait). | `terrain_trait_xp_gain_factor = 0.5` | Percentual. |  | 1.5 |
| <a id="wounded-chance-factor"></a> wounded\_chance\_factor | The chance for the unit leader to get wounded. | `wounded_chance_factor = 0.5` | Percentual. |  | 1.5 |
| <a id="shore-bombardment-bonus"></a> shore\_bombardment\_bonus | Modifies the penalty given by the shore bombardment on divisions. | `shore_bombardment_bonus = 0.5` | Percentual. | Can apply to both army and navy leaders. | 1.5 |

### <a id="scientists-scope"></a>Scientists scope

Scientist-scoped modifiers:
| Name | Effects | Examples | Modifier type | Notes | Version added |
| --- | --- | --- | --- | --- | --- |
| female\_random\_scientist\_chance | The chance of spawn female scientist | `female_random_scientist_chance = 0.05` | Percentual. |  | 1.15 |
| scientist\_breakthrough\_bonus\_factor | Modifiers scientist breakthrough bonus for special projects | `scientist_breakthrough_bonus_factor = -0.25` | Percentual. |  | 1.15 |
| scientist\_research\_bonus\_factor | Modifiers scientist research bonus for special projects | `scientist_research_bonus_factor = 0.15` | Percentual. |  | 1.15 |
| scientist\_xp\_gain\_factor | Modifiers scientist gain xp | `scientist_xp_gain_factor = 0.02` | Percentual. |  | 1.15 |

### <a id="strategic-region-scope"></a>Strategic region scope

This is limited to [static modifiers](#static-modifiers) defined for weather.

Strategic region-scoped modifiers:
| Name | Effects | Examples | Modifier type | Notes | Version added |
| --- | --- | --- | --- | --- | --- |
| <a id="air-accidents"></a> air\_accidents | Base chance for an air accident to happen. | `air_accidents = 0.3` | Flat. |  | 1.0 |
| <a id="air-detection"></a> air\_detection | Base chance for air detection. | `air_detection = -0.1` | Flat. |  | 1.0 |
| <a id="naval-strike"></a> naval\_strike | Base efficiency for naval strikes. | `naval_strike = -0.1` | Flat. |  | 1.0 |
| <a id="navy-casualty-on-sink"></a> navy\_casualty\_on\_sink | Modifies the casualties when ships are sunk in this region. | `navy_casualty_on_sink = -0.1` | Percentual. |  | 1.6 |
| <a id="navy-casualty-on-hit"></a> navy\_casualty\_on\_hit | Modifies the casualties when ships are damaged in this region. | `navy_casualty_on_hit = -0.1` | Percentual. |  | 1.6 |

## <a id="notes-and-references"></a>Notes and references

<a id="cnote-a"></a>**[^](#ref-a)** **a:** A few modifiers, such as [consumer\_goods\_factor](#consumer-goods-factor), instead get added in a multiplicative fashion.<a id="cite-ref-1"></a>[[1]](#cite-note-1) What this means is that, for example, `consumer_goods_factor = 0.1` and `consumer_goods_factor = 0.2` as separate ideas don't sum up to a 0.3 bonus, but instead multiply the consumer goods by ![{\displaystyle (1+0.1)(1+0.2)=1.1\cdot 1.2=1.32}](media/modifiers-hearts-of-iron-4-wiki_5dfb90c7fa__img29.svg), resulting in a 32% increase instead of 30%.

<a id="cite-note-1"></a>1. [↑](#cite-ref-1) [Developer Diary | Small Features #1](https://forum.paradoxplaza.com/forum/index.php?threads/1593911), 1.13 developer diary.

**[Modding](<Modding - Hearts of Iron 4 Wiki.md>)**
