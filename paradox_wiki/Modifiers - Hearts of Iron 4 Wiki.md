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
  - [Examples](#examples)
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
Each modifier has the exact same layout: `modifier_name = 0.1`. This adds the specified value to the modifier's total value for the scope where it is applied. For example, assuming that there are no other modifiers changing that to the country, having `political_power_gain = 0.2` and `political_power_gain = -0.05` applied to the country (potentially in different modifier blocks) will result in a total of **+0.15** political power gain above the base gain. Due to how modifiers work, **a modifier with the value of 0 will always do nothing.** This also means that negative modifiers will always work and have the opposite effect of positive modifiers.  
A modifier's current total value can be received as a variable by reading `modifier@modifier_name`, such as `set_variable = { my_var = modifier@political_power_gain }`. This works for countries and states, but for unit leaders, `unit_modifier@modifier_name` and `leader_modifier@modifier_name` is used instead.

The following are *not* modifiers, even if they are similar:

- Research bonuses allowing to grant a boost to a specific technology category. This is, instead, [an argument within ideas](<Idea modding - Hearts of Iron 4 Wiki.md#modifiers>), which can be applied in the same way for advisors, but not elsewhere.
- Equipment bonuses, such as decreasing the cost to build an equipment archetype. Similarly, this is [an argument within ideas](<Idea modding - Hearts of Iron 4 Wiki.md#modifiers>), which can be applied in the same way for advisors and country leader traits, but not elsewhere.
- Opinion modifiers, which can be applied to change the opinion (including trade influence) within countries, defined in /Hearts of Iron IV/common/opinion\_modifiers/\*.txt files.

## Applying a modifier

There are a large variety of ways to apply modifiers, but these are the primary ones:

- [Ideas](<Idea modding - Hearts of Iron 4 Wiki.md>) - This primarily includes but is not limited to national spirits and hidden ideas. **These are the simplest way to add a modifier to a country** by using an [effect block](<Effect - Hearts of Iron 4 Wiki.md>), such as a national focus reward, by using [add\_ideas](<Effect - Hearts of Iron 4 Wiki.md#add-ideas>) or [add\_timed\_idea](<Effect - Hearts of Iron 4 Wiki.md#add-timed-idea>). These only work for countries.
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

### Tooltip modification

Modifier blocks support, within them, the `hidden_modifier = { ... }` block, which can be used to provent the modifiers within from showing up in the tooltip. Additionally, `custom_modifier_tooltip = localisation_key_tt` can be used to add a custom localisation string to appear within the localisation as one of the modifiers. In combination, this will look like the following:

```text
modifier = {
    hidden_modifier = {
        political_power_gain = 0.1
    }
    custom_modifier_tooltip = political_power_gain_tt
}
```

Custom modifier tooltips *do not* support dynamic commands, which includes anything that uses square brackets.

## Dynamic modifiers

*If you want to apply a consistent modifier to a country, [it's easier to use ideas instead.](<Idea modding - Hearts of Iron 4 Wiki.md>)*

Dynamic modifiers, defined in /Hearts of Iron IV/common/dynamic\_modifiers/\*.txt files, are a type to apply modifiers that accept variables. The modifiers are updated daily, unless the [force\_update\_dynamic\_modifier effect](<Effect - Hearts of Iron 4 Wiki.md#force-update-dynamic-modifier>) is used to forcefully refresh the impact of modifiers. They can be applied to both countries and states, in case of the latter, the variable must be defined for the state, not for the country-owner or controller. They can also be applied to unit leaders.

Unlike ideas, **there is no way to reload definitions of dynamic modifiers** via debug mode or console, any changes to their definitions require a game restart to apply in-game. Additionally, due to the daily refresh of the variable check, these are more poorly optimised than ideas are. Due to this, when it's feasible to not use variables for a country-scoped dynamic modifier, it's both easier and more optimised [to use national spirits instead.](<Idea modding - Hearts of Iron 4 Wiki.md>)

The dynamic modifiers are evaluated daily for each scope. The process consists of the following:

- At the beginning of each day, each variable modifier value for each dynamic modifier is temporarily reset to 0, even if the null-coalescing operator is used to assume a different number as the default. Constant values do not get reset.
- Dynamic modifiers are then evaluated in the order that they were given to the scope with `add_dynamic_modifier`.
- The variable values inside of a dynamic modifier are assumed to be 0 until every variable inside is calculated. This includes those that rely on other modifiers, which includes the `modifier@modifier_name` game variable or MTTH variables that utilise that game variable.
- After the variables are calculated for a single dynamic modifier, the modifiers apply to the scope with the dynamic modifier and the game moves onto the next dynamic modifier added to the current scope until each one is calculated.

### Arguments

- **icon** decides what is the icon used for the dynamic modifier. The icon uses a sprite defined in any /Hearts of Iron IV/interface/\*.gfx file. If the icon is not specified, it will be hidden.
- **enable** decides when exactly the dynamic modifier's modifiers apply. If the dynamic modifier is set, but the country or state it's set to does not fulfill the requirements, its effects will not apply. Optional.
- **remove\_trigger** will automatically remove the dynamic modifier upon the triggers being met. Optional.
- **attacker\_modifier** will, if set to true within a state-scoped dynamic modifier, additionally makes the modifier apply to divisions that, while not being present in the state with the dynamic modifier, are attacking an enemy located on that state. Optional, defaults to false.

Modifiers are put directly inside the dynamic modifier as a list. Non-modifier idea attributes such as `equipment_bonus` or `research_bonus` are impossible to use inside of dynamic modifiers.

### Example

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

### Adding a dynamic modifier

Dynamic modifiers are added via the [add\_dynamic\_modifier effect](<Effect - Hearts of Iron 4 Wiki.md#add-dynamic-modifier>). A typical addition of a dynamic modifier looks like the following:

```text
add_dynamic_modifier = { modifier = dynamic_modifier_name }
```

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

A dynamic modifier is removed via [remove\_dynamic\_modifier](<Effect - Hearts of Iron 4 Wiki.md#remove-dynamic-modifier>), phrased similarly to add\_dynamic\_modifier: `remove_dynamic_modifier = { modifier = dynamic_modifier_name }`. If, when added, the dynamic modifier had a scope assigned to it, the scope will have to be specified when removing it as well.

**Modifiers that use variables will not show up in the tooltip of add\_dynamic\_modifier**, while those that are set to a static value will. While this may make the dynamic modifier appear broken when only reading the tooltip, this will not be actually the case once it gets added. In this case, [the tooltip of the effect can be changed](<Effect - Hearts of Iron 4 Wiki.md#custom-effect-tooltip>), with [the effect adding the dynamic modifier hidden](<Scopes - Hearts of Iron 4 Wiki.md#hidden-effect>).

## Static modifiers

Static modifiers are stored in /Hearts of Iron IV/common/modifiers/\*.txt files, where each code block within is a modifier block with the name being the ID of the static modifier. There are 5 main categories of static modifiers:

### Global modifiers

Global modifiers are applied by the hard-coded game features. Their names mustn't be changed, as the code uses them internally, but their effects can be edited. Examples of global modifiers are the penalty for non-core states or the effects of stability and war support.

### Difficulty modifiers

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

### Relation modifiers

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
```

They can be added by the add\_relation\_modifier effect, used as such:

```text
add_relation_modifier = {
	target = TAG
	modifier = test_relation_modifier
}
```

remove\_relation\_modifier, which works similarly, can remove them.

### Province modifiers

Province modifiers apply a modifier to a specific province rather than a state. They can be applied via the add\_province\_modifier effect, and removed with remove\_province\_modifier. More info on how to use these can be seen in the effects page.  
An example definition looks like

```text
mod_modifier = { 
	army_speed_factor = -0.5
	army_defence_factor = 0.5
	dig_in_speed_factor = 0.5
}
```

Many state-scope modifiers will work in province scope as well. In order to make the GFX in GUI, you first need to edit /Hearts of Iron IV/interface/countrystateview.gui. The icon must be defined inside custom\_icon\_container, similarly to other examples. An example definition looks like

```text
iconType = {
	name = "<modifier name>_icon"
	spriteType = "GFX_modifiers_<modifier name>_icon"
	position = { x = 0 y = 0 }
	Orientation = "UPPER_LEFT"			
}
```

The spriteType you have defined needs to be defined in /Hearts of Iron IV/interface/\*.gfx similarly to this example:

```text
spriteType = {
	name = "GFX_modifiers_<modifier name>_icon"
	textureFile = "gfx/interface/modifiers_<modifier name>_icon.dds"
}
```

### Balance of power modifiers

Balance of power modifiers typically include within of themselves the [power\_balance\_daily](#power-balance-daily) and/or [power\_balance\_weekly](#power-balance-weekly) modifiers in order to gradually tip the balance towards one side. For example,

```text
my_bop_modifier = {
    power_balance_weekly = -0.01 # Changes by 1% each week to the left, in the range of -1 to 1.
}
```

Balance of power modifiers are added via [the add\_power\_balance\_modifier effect](<Effect - Hearts of Iron 4 Wiki.md#add-power-balance-modifier>) as such:

```text
add_power_balance_modifier = {
    id = my_bop    # The ID of the balance of power
    modifier = my_bop_modifier # The modifier to add
}
```

[The remove\_power\_balance\_modifier effect](<Effect - Hearts of Iron 4 Wiki.md#remove-power-balance-modifier>), with the same syntax, or [remove\_all\_power\_balance\_modifiers](<Effect - Hearts of Iron 4 Wiki.md#remove-all-power-balance-modifiers>) can be used to remove these from the country.

## Modifier definitions

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

### Examples

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

### Using in variables

The function of modifier definitions is to modify the value of a game variable, which can be read by other variables. You can set a variable to be equal to the sum of all values of the same modifier token in the current scope by doing `set_variable = { var_name = modifier@modifier_token_name }`. This example will set var\_name to be equal to the total value of modifier\_token\_name.

Note that, unlike countries and states, unit leaders use leader\_modifier@modifier\_definition\_name or unit\_modifier@modifier\_definition\_name in their scopes.

Example usage of making a modifier token create civilian factories in random core states monthly, in any on action file:

## Opinion modifiers

Despite their name, opinion modifiers are not related to modifiers in any way, instead they are used to modify the diplomatic or economic relations between a pair of countries.

The opinion modifiers are made in any /Hearts of Iron IV/common/opinion\_modifiers/\*.txt file as an entry in the `opinion_modifiers = { ... }` block, with the name of the entry being the ID of the opinion modifier. In case of there being several entries with the same ID, the one that was [evaluated later based on the filename and order in files](<Modding - Hearts of Iron 4 Wiki.md#loading-files>) will take priority, meaning that copying a base game file is never necessary in a mod.

There are the following attributes that are used in opinion modifiers:

- `trade = yes` is used to decide whether the opinion modifier changes the diplomatic relations or the trade opinion from one country to another. If unset, defaults to being false making it diplomatic.
- `value = -10` is the value of the modifier that decides by how much the diplomatic or trade opinion should change once the opinion modifier is added.
- `decay = 1` details the speed at which the opinion modifier trends towards zero monthly. Optional, defaults to the modifier not changing if unset.
- `days = 10` | `months = 2` | `years = 1` decides the time for how much the opinion modifier should last before it will get automatically removed. A month is interpreted as exactly 30 days, while a year is 365. Optional, the modifier will be permanent if neither is set.
- `min_trust = 10` | `max_trust = -10` detail the minimum and maximum value that the opinion modifier can change to. As the only non-hardcoded way to change the value of an existing opinion modifier is through decay, this can be used to limit how far it can apply.

The [localisation](<Localisation - Hearts of Iron 4 Wiki.md>) is created in any /Hearts of Iron IV/localisation/english/\*\_l\_english.yml file encoded in UTF-8 using the byte order mark (aka UTF-8-BOM), with the localisation key being the name of the modifier.

### Examples

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
```

Inside of a new /Hearts of Iron IV/localisation/english/\*\_l\_english.yml file:

```text
l_english:
 test_trade_modifier: "Testing trade modifier"
 test_diplomatic_modifier: "Testing diplomatic modifier"
```

### Implementation

New opinion modifiers can only be added using the [add\_opinion\_modifier effect](<Effect - Hearts of Iron 4 Wiki.md#add-opinion-modifier>) (or the similar [reverse\_add\_opinion\_modifier](<Effect - Hearts of Iron 4 Wiki.md#reverse-add-opinion-modifier>)) in any effect block, such as a [focus reward](<National focus modding - Hearts of Iron 4 Wiki.md#effects>), a [country history file](<Country creation - Hearts of Iron 4 Wiki.md#country-history>), or an idea's [on\_add and on\_remove](<Idea modding - Hearts of Iron 4 Wiki.md#effects>). Similarly, already applied new opinion modifiers can only be removed with [remove\_opinion\_modifier](<Effect - Hearts of Iron 4 Wiki.md#remove-opinion-modifier>). When `add_opinion_modifier` is used to apply an opinion modifier, only the country where the effect is executed will change its opinion towards the target.

There is no way to use a modifier block to directly apply an opinion modifier, but it can be simulated by adding or removing an opinion modifier at the same time the modifier block's effects are. For example, this national spirit would simulate applying an opinion modifier towards every other country that has the idea:

## List of modifiers

The list of modifiers may be outdated. A complete, but unsorted, list of modifiers can be found in /Hearts of Iron IV/documentation/modifiers\_documentation.html or /Hearts of Iron IV/documentation/modifiers\_documentation.md.

### Country scope

#### General

- **monthly_population**
  - Effects: Changes the monthly population gain in states owned by the country.
  - Example:
    ```text
    monthly_population = 0.5
    ```
  - Modifier type: Percentual.
  - Notes: Does not work with states.
  - Version added: 1.0

- **nuclear_production**
  - Effects: Enables the production of nukes.
  - Example:
    ```text
    nuclear_production = 1
    ```
  - Modifier type: Boolean (only 1).
  - Version added: 1.0

- **nuclear_production_factor**
  - Effects: Changes speed at which nukes are produced.
  - Example:
    ```text
    nuclear_production_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Notes: Works in state scope, in which case it'll apply to the owner.
  - Version added: 1.0

- **research_sharing_per_country_bonus**
  - Effects: Changes the bonus in research speed per country when technology sharing.
  - Example:
    ```text
    research_sharing_per_country_bonus = 0.5
    ```
  - Modifier type: Flat.
  - Version added: 1.3

- **research_sharing_per_country_bonus_factor**
  - Effects: Changes the bonus in research speed per country when technology sharing by a percentage.
  - Example:
    ```text
    research_sharing_per_country_bonus_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.3

- **research_speed_factor**
  - Effects: Changes the research speed.
  - Example:
    ```text
    research_speed_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **local_resources_factor**
  - Effects: Resource extraction efficiency. Modifies the amount of available resources.
  - Example:
    ```text
    local_resources_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **surrender_limit**
  - Effects: Changes the percentage of victory points the country needs to lose control of to capitulate.
  - Example:
    ```text
    surrender_limit = 0.1
    ```
  - Modifier type: Percentual.
  - Notes: The larger, the more victory points are needed to capitulate a country.
  - Version added: 1.0

- **max_surrender_limit_offset**
  - Effects: Controls the maximum surrender progress of a nation.
  - Example:
    ```text
    max_surrender_limit_offset = 0.3
    ```
  - Modifier type: Flat.
  - Notes: For example, 0.4 means that the country cannot require more than 60% victory points to capitulate, no matter the surrender_limit.
  - Version added: 1.9

- **forced_surrender_limit**
  - Effects: Changes the percentage of victory points the country needs to lose control of to capitulate, bypassing the minimum or maximum.
  - Example:
    ```text
    forced_surrender_limit = 0.1
    ```
  - Modifier type: Percentual.
  - Notes:
    ```text
    The larger, the more victory points are needed to capitulate a country. Applied after the minimum and maximum are applied, leading to making it possible to have it below
    20%
    or above the maximum defined with max_surrender_limit_offset.
    ```
  - Version added: 1.0

- **country_resource_<resource>**
  - Effects: Directly modifies the country's resource stockpile.
  - Example:
    ```text
    country_resource_oil = 10
    ```
  - Modifier type: Flat.
  - Notes: Can also go into country scope.
  - Version added: 1.0

- **country_resource_cost_<resource>**
  - Effects: Directly modifies the country's resource stockpile.
  - Example:
    ```text
    country_resource_cost_aluminium = 10
    ```
  - Modifier type: Flat.
  - Notes: Can also go into country scope.
  - Version added: 1.0

- **factory_energy_consumption**
  - Effects: Directly modifies the country's energy usage per factory
  - Example:
    ```text
    factory_energy_consumption = 0.1
    ```
  - Modifier type: Percentual
  - Version added: 1.17

#### Politics

- **min_export**
  - Effects: Changes the amount of resources to market.
  - Example:
    ```text
    min_export = 0.5
    ```
  - Modifier type: Flat.
  - Version added: 1.0

- **trade_opinion_factor**
  - Effects: Makes AI more likely to purchase resources from this country.
  - Example:
    ```text
    trade_opinion_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **defensive_war_stability_factor**
  - Effects: Changes the penalty to the stability invoked by participating in a defensive war.
  - Example:
    ```text
    defensive_war_stability_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **disabled_ideas**
  - Effects: Disables manually changing ideas (including ministers and laws).
  - Example:
    ```text
    disabled_ideas = 1
    ```
  - Modifier type: Boolean (only 1).
  - Version added: 1.9

- **<idea|character slot>_cost_factor**
  - Effects: Changes the cost in political power to add an idea or character within the specified slot.
  - Example:
    ```text
    political_advisor_cost_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Notes:
    ```text
    Idea slots can be found in common/idea_tags.
    Requires an idea or a character of that category to be present in an earlier-evaluated file.
    ```
  - Version added: 1.4

- **<idea category type>_category_type_cost_factor**
  - Effects: Changes the cost in political power to add an idea within any of the categories with the specified type.
  - Example:
    ```text
    air_spirit_category_type_cost_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Notes:
    ```text
    Idea category definitions can be found in
    /Hearts of Iron IV/common/idea_tags/*.txt
    files, a type is assigned with
    type = army_spirit
    .
    ```
  - Version added: 1.10

- **<ledger>_advisor_cost_factor**
  - Effects: Changes the cost in political power to add an advisor assigned the specified military ledger.
  - Example:
    ```text
    air_advisor_cost_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Notes: Ledgers are assigned to categories and characters in common/idea_tags and common/ideas. Modifier works with air, army, and navy.
  - Version added: 1.11

- **unit_leader_as_advisor_cp_cost_factor**
  - Effects: Changes the cost in command power to turn a unit leader into an advisor.
  - Example:
    ```text
    unit_leader_as_advisor_cp_cost_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.11

- **improve_relations_maintain_cost_factor**
  - Effects: Changes the cost in political power to maintain improvement of relations.
  - Example:
    ```text
    improve_relations_maintain_cost_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.4

- **female_random_country_leader_chance**
  - Effects: Changes the chance for a randomly-generated country leader to be female.
  - Example:
    ```text
    female_random_country_leader_chance = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **offensive_war_stability_factor**
  - Effects: Modifies the stability penalty received from participating in an offensive war.
  - Example:
    ```text
    offensive_war_stability_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **party_popularity_stability_factor**
  - Effects: Modifies the stability gained by the popularity of the ruling party.
  - Example:
    ```text
    party_popularity_stability_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **political_power_cost**
  - Effects: Daily cost in political power.
  - Example:
    ```text
    political_power_cost = 0.3
    ```
  - Modifier type: Flat.
  - Version added: 1.0

- **political_power_gain**
  - Effects: Modifies daily gain in political power.
  - Example:
    ```text
    political_power_gain = 0.3
    ```
  - Modifier type: Flat.
  - Version added: 1.0

- **political_power_factor**
  - Effects: Modifies daily gain in political power by a percentage.
  - Example:
    ```text
    political_power_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **stability_factor**
  - Effects: Modifies stability of the country.
  - Example:
    ```text
    stability_factor = 0.3
    ```
  - Modifier type: Flat.
  - Version added: 1.0

- **stability_weekly**
  - Effects: Modifies weekly stability gain of the country.
  - Example:
    ```text
    stability_weekly = 0.01
    ```
  - Modifier type: Flat.
  - Version added: 1.0

- **stability_weekly_factor**
  - Effects: Modifies weekly stability gain of the country by a percentage.
  - Example:
    ```text
    stability_weekly_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **war_stability_factor**
  - Effects: Modifies the stability loss caused by being at war.
  - Example:
    ```text
    war_stability_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **war_support_factor**
  - Effects: Modifies war support of the country.
  - Example:
    ```text
    war_support_factor = 0.3
    ```
  - Modifier type: Flat.
  - Version added: 1.0

- **war_support_weekly**
  - Effects: Modifies weekly war support gain of the country.
  - Example:
    ```text
    war_support_weekly = 0.01
    ```
  - Modifier type: Flat.
  - Version added: 1.0

- **war_support_weekly_factor**
  - Effects: Modifies weekly war support gain of the country by a percentage.
  - Example:
    ```text
    war_support_weekly_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **weekly_casualties_war_support**
  - Effects: Modifies weekly war support gain of the country depending on the casualties suffered by it.
  - Example:
    ```text
    weekly_casualties_war_support = 0.006
    ```
  - Modifier type: Percentual.
  - Version added: 1.12

- **weekly_convoys_war_support**
  - Effects: Modifies weekly war support gain of the country depending on the amount of its convoys that have been sunk.
  - Example:
    ```text
    weekly_convoys_war_support = 0.006
    ```
  - Modifier type: Percentual.
  - Version added: 1.12

- **weekly_bombing_war_support**
  - Effects: Modifies weekly war support gain of the country depending on the enemy bombing of its states.
  - Example:
    ```text
    weekly_bombing_war_support = 0.006
    ```
  - Modifier type: Percentual.
  - Version added: 1.12

- **drift_defence_factor**
  - Effects: Ideology drift defense.
  - Example:
    ```text
    drift_defence_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **power_balance_daily**
  - Effects: Pushes the power balance by a specified amount on each day.
  - Example:
    ```text
    power_balance_daily = 0.01
    ```
  - Modifier type: Flat.
  - Notes: Positive values result in it being pushed right, while negatives result in it being pushed left.
  - Version added: 1.12

- **power_balance_weekly**
  - Effects: Pushes the power balance by a specified amount on each week.
  - Example:
    ```text
    power_balance_weekly = 0.01
    ```
  - Modifier type: Flat.
  - Notes: Positive values result in it being pushed right, while negatives result in it being pushed left.
  - Version added: 1.12

- **<ideology>_drift**
  - Effects: Daily gain of the specified ideology.
  - Example:
    ```text
    communism_drift = 0.03
    ```
  - Modifier type: Flat.
  - Version added: 1.0

- **<ideology>_acceptance**
  - Effects: Likelihood of AI to accept offers from countries of the specified ideology.
  - Example:
    ```text
    fascism_acceptance = 50
    ```
  - Modifier type: Flat.
  - Version added: 1.0

#### Diplomacy

- **civil_war_involvement_tension**
  - Effects: Changes the world tension amount necessary to intervene in an ally's civil war.
  - Example:
    ```text
    civil_war_involvement_tension = 0.5
    ```
  - Modifier type: Flat.
  - Version added: 1.0

- **enemy_declare_war_tension**
  - Effects: Changes the world tension required for an enemy to justify a wargoal on us.
  - Example:
    ```text
    enemy_declare_war_tension = 0.5
    ```
  - Modifier type: Flat.
  - Version added: 1.0

- **enemy_justify_war_goal_time**
  - Effects: Changes the time required for an enemy to justify a wargoal on us.
  - Example:
    ```text
    enemy_justify_war_goal_time = 0.5
    ```
  - Modifier type: Percentual.
  - Notes: This also modifies the cost in political power.
  - Version added: 1.0

- **faction_trade_opinion_factor**
  - Effects: Changes the opinion gain gained by trade between faction members.
  - Example:
    ```text
    faction_trade_opinion_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **generate_wargoal_tension**
  - Effects: Changes the necessary tension for us to generate a wargoal.
  - Example:
    ```text
    generate_wargoal_tension = 0.3
    ```
  - Modifier type: Flat.
  - Version added: 1.0

- **guarantee_cost**
  - Effects: Cost in political power for the country to guarantee an another country.
  - Example:
    ```text
    guarantee_cost = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.4

- **guarantee_tension**
  - Effects: Necessary world tension for the country to guarantee an another country.
  - Example:
    ```text
    guarantee_tension = 0.3
    ```
  - Modifier type: Flat.
  - Version added: 1.0

- **join_faction_tension**
  - Effects: Necessary world tension for the country to join a faction.
  - Example:
    ```text
    join_faction_tension = 0.3
    ```
  - Modifier type: Flat.
  - Version added: 1.0

- **justify_war_goal_time**
  - Effects: The amount of time necessary to justify a wargoal.
  - Example:
    ```text
    justify_war_goal_time = 0.3
    ```
  - Modifier type: Percentual.
  - Notes: This also modifies the cost in political power.
  - Version added: 1.0

- **justify_war_goal_when_in_major_war_time**
  - Effects: The amount of time necessary to justify a wargoal when in a war with a major country.
  - Example:
    ```text
    justify_war_goal_when_in_major_war_time = 0.3
    ```
  - Modifier type: Percentual.
  - Notes: This also modifies the cost in political power.
  - Version added: 1.0

- **lend_lease_tension**
  - Effects: Necessary world tension for the country to lend-lease.
  - Example:
    ```text
    lend_lease_tension = 0.3
    ```
  - Modifier type: Flat.
  - Version added: 1.0

- **lend_lease_tension_with_overlord**
  - Effects: Necessary world tension for the country to lend-lease to its overlord.
  - Example:
    ```text
    lend_lease_tension_with_overlord = 0.3
    ```
  - Modifier type: Flat.
  - Version added: 1.13

- **opinion_gain_monthly**
  - Effects: Changes opinion gain from the 'Improve relations' diplomatic action.
  - Example:
    ```text
    opinion_gain_monthly = 5
    ```
  - Modifier type: Flat.
  - Version added: 1.0

- **opinion_gain_monthly_factor**
  - Effects: Changes opinion gain from the 'Improve relations' diplomatic action by a percentage.
  - Example:
    ```text
    opinion_gain_monthly_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **opinion_gain_monthly_same_ideology**
  - Effects: Changes opinion gain from the 'Improve relations' diplomatic action for countries of the same ideology.
  - Example:
    ```text
    opinion_gain_monthly_same_ideology = 5
    ```
  - Modifier type: Flat.
  - Version added: 1.0

- **opinion_gain_monthly_same_ideology_factor**
  - Effects: Changes opinion gain from the 'Improve relations' diplomatic action for countries of the same ideology by a percentage.
  - Example:
    ```text
    opinion_gain_monthly_same_ideology_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **request_lease_tension**
  - Effects: Necessary world tension for the country to request lend-lease.
  - Example:
    ```text
    request_lease_tension = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.9

- **annex_cost_factor**
  - Effects: Modifies the cost in victory points to annex states in peace deals.
  - Example:
    ```text
    annex_cost_factor = 0.1
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **puppet_cost_factor**
  - Effects: Modifies the cost in victory points per state to puppet countries in peace deals.
  - Example:
    ```text
    puppet_cost_factor = 0.1
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **send_volunteer_divisions_required**
  - Effects: Changes the number of divisions needed to send volunteers.
  - Example:
    ```text
    send_volunteer_divisions_required = -0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **send_volunteer_factor**
  - Effects: Changes the number of divisions the country can send as volunteers by a percentage.
  - Example:
    ```text
    send_volunteer_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **send_volunteer_size**
  - Effects: Changes the number of divisions the country can send as volunteers.
  - Example:
    ```text
    send_volunteer_size = 5
    ```
  - Modifier type: Flat.
  - Version added: 1.0

- **send_volunteers_tension**
  - Effects: Changes the world tension necessary for the country to send volunteers.
  - Example:
    ```text
    send_volunteers_tension = -0.1
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **air_volunteer_cap**
  - Effects: Changes the amount of airforce you can send as volunteers.
  - Example:
    ```text
    air_volunteer_cap = 100
    ```
  - Modifier type: Flat.
  - Version added: 1.5

- **embargo_threshold_factor**
  - Effects: Changes the necessary world tension level in order to be able to embargo a country.
  - Example:
    ```text
    embargo_threshold_factor = 0.2
    ```
  - Modifier type: Percentual.
  - Version added: 1.12

- **embargo_cost_factor**
  - Effects: Changes the cost in political power to send an embargo.
  - Example:
    ```text
    embargo_cost_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.12

#### Autonomy

- **autonomy_gain**
  - Effects: Daily gain of autonomy.
  - Example:
    ```text
    autonomy_gain = 0.5
    ```
  - Modifier type: Flat.
  - Notes: A positive number increase total autonomy, meaning the SUBJECT can be free faster. A negative number decrease total autonomy, meaning the OVERLORD can annex the manpower-slaves faster.
  - Version added: 1.3

- **autonomy_gain_global_factor**
  - Effects: Modifies all gain of autonomy by a subject.
  - Example:
    ```text
    autonomy_gain_global_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.4

- **subjects_autonomy_gain**
  - Effects: Daily gain of autonomy in our subjects.
  - Example:
    ```text
    subjects_autonomy_gain = 0.5
    ```
  - Modifier type: Flat.
  - Version added: 1.3

- **autonomy_gain_ll_to_overlord**
  - Effects: Modifies gain of autonomy from lend-leasing to the overlord.
  - Example:
    ```text
    autonomy_gain_ll_to_overlord = 0.5
    ```
  - Modifier type: Flat.
  - Version added: 1.3

- **autonomy_gain_ll_to_overlord_factor**
  - Effects: Modifies gain of autonomy from lend-leasing to the overlord by a percentage.
  - Example:
    ```text
    autonomy_gain_ll_to_overlord_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.3

- **autonomy_gain_ll_to_subject**
  - Effects: Modifies loss of autonomy from lend-leasing to the subject.
  - Example:
    ```text
    autonomy_gain_ll_to_subject = 0.5
    ```
  - Modifier type: Flat.
  - Version added: 1.3

- **autonomy_gain_ll_to_subject_factor**
  - Effects: Modifies loss of autonomy from lend-leasing to the subject by a percentage.
  - Example:
    ```text
    autonomy_gain_ll_to_subject_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.3

- **autonomy_gain_trade**
  - Effects: Modifies gain of autonomy from the overlord trading with the subject.
  - Example:
    ```text
    autonomy_gain_trade = 0.5
    ```
  - Modifier type: Flat.
  - Version added: 1.3

- **autonomy_gain_trade_factor**
  - Effects: Modifies gain of autonomy from the overlord trading with the subject by a percentage.
  - Example:
    ```text
    autonomy_gain_trade_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.3

- **autonomy_gain_warscore**
  - Effects: Modifies gain of autonomy from the subject gaining warscore.
  - Example:
    ```text
    autonomy_gain_warscore = 0.5
    ```
  - Modifier type: Flat.
  - Version added: 1.3

- **autonomy_gain_warscore_factor**
  - Effects: Modifies gain of autonomy from the subject gaining warscore by a percentage.
  - Example:
    ```text
    autonomy_gain_warscore_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.3

- **autonomy_manpower_share**
  - Effects: Modifies the amount of manpower the overlord can use from the subject.
  - Example:
    ```text
    autonomy_manpower_share = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.3

- **can_master_build_for_us**
  - Effects: Makes the overlord be able to build in the subject.
  - Example:
    ```text
    can_master_build_for_us = 1
    ```
  - Modifier type: Boolean (only 1).
  - Version added: 1.3

- **cic_to_overlord_factor**
  - Effects: Modifies the amount of the subject's civilian industry that goes to the overlord.
  - Example:
    ```text
    cic_to_overlord_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.3

- **mic_to_overlord_factor**
  - Effects: Modifies the amount of the subject's military industry that goes to the overlord.
  - Example:
    ```text
    mic_to_overlord_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.3

- **extra_trade_to_overlord_factor**
  - Effects: Modifies the amount of the subject's resources that the overlord can receive via trade.
  - Example:
    ```text
    extra_trade_to_overlord_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.3

- **license_subject_master_purchase_cost**
  - Effects: Modifies the cost of licensed production from the overlord.
  - Example:
    ```text
    license_subject_master_purchase_cost = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.4

- **master_build_autonomy_factor**
  - Effects: Modifies loss of autonomy from the overlord building in subject's states by a percentage.
  - Example:
    ```text
    master_build_autonomy_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.3

- **master_ideology_drift**
  - Effects: Changes daily gain of the overlord's ideology in the country.
  - Example:
    ```text
    master_ideology_drift = 0.03
    ```
  - Modifier type: Flat.
  - Version added: 1.6

- **overlord_trade_cost_factor**
  - Effects: Modifies the cost of trade between the overlord and the subject in civilian factories.
  - Example:
    ```text
    overlord_trade_cost_factor = -0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.3

#### Governments in exile

- **dockyard_donations**
  - Effects: Amount of dockyards donated.
  - Example:
    ```text
    dockyard_donations = 2
    ```
  - Modifier type: Flat.
  - Version added: 1.6

- **industrial_factory_donations**
  - Effects: Amount of civilian factories donated.
  - Example:
    ```text
    industrial_factory_donations = 2
    ```
  - Modifier type: Flat.
  - Version added: 1.6

- **military_factory_donations**
  - Effects: Amount of military factories donated.
  - Example:
    ```text
    military_factory_donations = 2
    ```
  - Modifier type: Flat.
  - Version added: 1.6

- **exile_manpower_factor**
  - Effects: Amount of manpower given to the host country.
  - Example:
    ```text
    exile_manpower_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.6

- **exiled_government_weekly_manpower**
  - Effects: Amount of weekly manpower given to the host country.
  - Example:
    ```text
    exiled_government_weekly_manpower = 100
    ```
  - Modifier type: Percentual.
  - Version added: 1.11

- **legitimacy_daily**
  - Effects: Changes the amount of legitimacy gained daily.
  - Example:
    ```text
    legitimacy_daily = 1
    ```
  - Modifier type: Flat.
  - Version added: 1.6

- **legitimacy_gain_factor**
  - Effects: Changes the amount of legitimacy gained daily by a percentage.
  - Example:
    ```text
    legitimacy_gain_factor = 1
    ```
  - Modifier type: Percentual.
  - Version added: 1.9

#### Equipment

- **equipment_capture**
  - Effects: Changes the combat equipment capture ratio.
  - Example:
    ```text
    equipment_capture = 0.2
    ```
  - Modifier type: Flat.
  - Version added: 1.0

- **equipment_capture_factor**
  - Effects: Modifies the combat equipment capture ratio.
  - Example:
    ```text
    equipment_capture_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **equipment_conversion_speed**
  - Effects: Changes the speed at which equipment is converted.
  - Example:
    ```text
    equipment_conversion_speed = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **equipment_upgrade_xp_cost**
  - Effects: Changes the experience cost to upgrade military equipment.
  - Example:
    ```text
    equipment_upgrade_xp_cost = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **license_purchase_cost**
  - Effects: Changes the cost of licensed equipment by a percentage.
  - Example:
    ```text
    license_purchase_cost = 0.5
    ```
  - Modifier type: Percentual.
  - Notes: Can be used as a targeted modifier.
  - Version added: 1.4

- **license_purchase_cost_factor**
  - Effects: Changes the cost of licensed equipment by a percentage.
  - Example:
    ```text
    license_purchase_cost_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Notes: Allowed equipment types are anti_tank_eq, artillery_eq, infantry_eq, and light_tank_eq. Can be used as a targeted modifier.
  - Version added: 1.4

- **license_purchase_cost_factor**
  - Effects: Changes the cost of licensed equipment by a percentage.
  - Example:
    ```text
    license_purchase_cost_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Notes: Allowed categories are air, armor, infantry, and naval. Can be used as a targeted modifier.
  - Version added: 1.4

- **license_tech_difference_speed**
  - Effects: Changes the production penalty of licensed equipment by tech difference by a percentage.
  - Example:
    ```text
    license_tech_difference_speed = 0.5
    ```
  - Modifier type: Percentual.
  - Notes: Also allows specifying category as license_<category>_tech_difference_speed_factor. Allowed categories are anti_tank_eq, artillery_eq, infantry_eq, and light_tank_eq. That's added in 1.6. Can be used as a targeted modifier.
  - Version added: 1.4

- **license_production_speed**
  - Effects: Changes the production speed of licensed equipment by a percentage.
  - Example:
    ```text
    license_production_speed = 0.5
    ```
  - Modifier type: Percentual.
  - Notes: Can be used as a targeted modifier.
  - Version added: 1.4

- **license_<category>_production_speed_factor**
  - Effects: Changes the production speed of licensed equipment by a percentage.
  - Example:
    ```text
    license_infantry_eq_production_speed_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Notes: Allowed categories are anti_tank_eq, artillery_eq, infantry_eq, and light_tank_eq. Can be used as a targeted modifier.
  - Version added: 1.6

- **production_cost_max_<ship type>**
  - Effects: Modifies the maximum cost of the ship type.
  - Example:
    ```text
    production_cost_max_ship_hull_light = 0.3
    ```
  - Modifier type: Percentual.
  - Notes: Allowed ship types in base game: convoy, ship_hull_carrier, ship_hull_cruiser, ship_hull_heavy, ship_hull_light, ship_hull_submarine
  - Version added: 1.6

- **production_factory_efficiency_gain_factor**
  - Effects: Production efficiency growth.
  - Example:
    ```text
    production_factory_efficiency_gain_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **production_factory_max_efficiency_factor**
  - Effects: Production efficiency cap.
  - Example:
    ```text
    production_factory_max_efficiency_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **production_factory_start_efficiency_factor**
  - Effects: Production efficiency base.
  - Example:
    ```text
    production_factory_start_efficiency_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **line_change_production_efficiency_factor**
  - Effects: Production efficiency retention.
  - Example:
    ```text
    line_change_production_efficiency_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **production_lack_of_resource_penalty_factor**
  - Effects: Lack of resources penalty.
  - Example:
    ```text
    production_lack_of_resource_penalty_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **floating_harbor_duration**
  - Effects: Modifies the duration of floating harbours.
  - Example:
    ```text
    floating_harbor_duration = 2
    ```
  - Modifier type: Flat.
  - Version added: 1.11

- **floating_harbor_range**
  - Effects: Modifies the range of floating harbours.
  - Example:
    ```text
    floating_harbor_range = 2
    ```
  - Modifier type: Flat.
  - Version added: 1.11

- **floating_harbor_supply**
  - Effects: Modifies the supply of floating harbours.
  - Example:
    ```text
    floating_harbor_supply = 2
    ```
  - Modifier type: Flat.
  - Version added: 1.11

- **railway_gun_bombardment_factor**
  - Effects: Modifies the bombardment of railway guns.
  - Example:
    ```text
    railway_gun_bombardment_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.11

#### Fuel and supply

- **base_fuel_gain**
  - Effects: Changes base daily gain of fuel.
  - Example:
    ```text
    base_fuel_gain = 100
    ```
  - Modifier type: Flat.
  - Version added: 1.6

- **base_fuel_gain_factor**
  - Effects: Changes base daily gain of fuel by a percentage.
  - Example:
    ```text
    base_fuel_gain_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.6

- **fuel_cost**
  - Effects: Changes daily cost of fuel.
  - Example:
    ```text
    fuel_cost = 100
    ```
  - Modifier type: Flat.
  - Version added: 1.6

- **fuel_gain**
  - Effects: Changes daily gain of fuel from our controlled oil.
  - Example:
    ```text
    fuel_gain = 100
    ```
  - Modifier type: Flat.
  - Version added: 1.6

- **fuel_gain_factor**
  - Effects: Changes daily gain of fuel from our controlled oil by a percentage.
  - Example:
    ```text
    fuel_gain_factor = 100
    ```
  - Modifier type: Percentual.
  - Version added: 1.6

- **fuel_gain_from_states**
  - Effects: Changes daily gain of fuel.
  - Example:
    ```text
    fuel_gain_from_states = 100
    ```
  - Modifier type: Flat.
  - Notes: Refineries use this modifier.
  - Version added: 1.6

- **fuel_gain_factor_from_states**
  - Effects: Changes daily gain of fuel by a percentage.
  - Example:
    ```text
    fuel_gain_factor_from_states = 0.5
    ```
  - Modifier type: Percentual.
  - Notes: Modifies fuel gain from refineries.
  - Version added: 1.6

- **max_fuel**
  - Effects: Changes maximum amount of fuel you can have.
  - Example:
    ```text
    max_fuel = 100
    ```
  - Modifier type: Flat.
  - Version added: 1.6

- **max_fuel_factor**
  - Effects: Changes maximum amount of fuel you can have by a percentage.
  - Example:
    ```text
    max_fuel_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.6

- **army_fuel_capacity_factor**
  - Effects: Modifies how much fuel a single unit can store before running out.
  - Example:
    ```text
    army_fuel_capacity_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.6

- **army_fuel_consumption_factor**
  - Effects: Modifies the rate at which the army consumes fuel.
  - Example:
    ```text
    army_fuel_consumption_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.6

- **air_fuel_consumption_factor**
  - Effects: Modifies the rate at which the airforce consumes fuel.
  - Example:
    ```text
    air_fuel_consumption_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.6

- **navy_fuel_consumption_factor**
  - Effects: Modifies the rate at which the navy consumes fuel.
  - Example:
    ```text
    navy_fuel_consumption_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.6

- **supply_factor**
  - Effects: Modifies the total amount of supply the military has.
  - Example:
    ```text
    supply_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.11

- **supply_combat_penalties_on_core_factor**
  - Effects: Modifies the penalty given by low supply when the army is on a core state.
  - Example:
    ```text
    supply_combat_penalties_on_core_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.11

- **supply_consumption_factor**
  - Effects: Modifies the rate at which army consumes supply.
  - Example:
    ```text
    supply_consumption_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **no_supply_grace**
  - Effects: Modifies the grace period for units without supply.
  - Example:
    ```text
    no_supply_grace = 120
    ```
  - Modifier type: Flat.
  - Version added: 1.0

- **out_of_supply_factor**
  - Effects: Reduces the penalty that units take when they run out of supplies.
  - Example:
    ```text
    out_of_supply_factor = 0.2
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **attrition**
  - Effects: Modifies the army's attrition.
  - Example:
    ```text
    attrition = 0.3
    ```
  - Modifier type: Percentual.
  - Notes: Can also be used in states or provinces.
  - Version added: 1.0

- **unit_upkeep_attrition_factor**
  - Effects: Modifies the unit upkeep.
  - Example:
    ```text
    unit_upkeep_attrition_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **naval_attrition**
  - Effects: Modifies attrition suffered by naval units.
  - Example:
    ```text
    naval_attrition = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.6

- **heat_attrition**
  - Effects: Changes the attrition due to heat.
  - Example:
    ```text
    heat_attrition = 0.5
    ```
  - Modifier type: Flat.
  - Version added: 1.3

- **heat_attrition_factor**
  - Effects: Changes the attrition due to heat by a percentage.
  - Example:
    ```text
    heat_attrition_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.3

- **winter_attrition**
  - Effects: Changes the attrition due to winter.
  - Example:
    ```text
    winter_attrition = 0.5
    ```
  - Modifier type: Flat.
  - Version added: 1.3

- **winter_attrition_factor**
  - Effects: Changes the attrition due to winter by a percentage.
  - Example:
    ```text
    winter_attrition_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.3

- **extra_marine_supply_grace**
  - Effects: Changes the supply grace given to marines.
  - Example:
    ```text
    extra_marine_supply_grace = 96
    ```
  - Modifier type: Flat.
  - Version added: 1.0

- **extra_paratrooper_supply_grace**
  - Effects: Changes the supply grace given to paratroopers.
  - Example:
    ```text
    extra_paratrooper_supply_grace = 96
    ```
  - Modifier type: Flat.
  - Version added: 1.0

- **special_forces_no_supply_grace**
  - Effects: Changes the supply grace period for special forces.
  - Example:
    ```text
    special_forces_no_supply_grace = 120
    ```
  - Modifier type: Flat.
  - Version added: 1.0

- **special_forces_out_of_supply_factor**
  - Effects: Changes the penalty for special forces out of supply.
  - Example:
    ```text
    special_forces_out_of_supply_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **truck_attrition**
  - Effects: Changes the attrition supply trucks suffer from.
  - Example:
    ```text
    truck_attrition = 3
    ```
  - Modifier type: Flat.
  - Version added: 1.11

- **truck_attrition_factor**
  - Effects: Modifies the attrition supply trucks suffer from.
  - Example:
    ```text
    truck_attrition_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.11

#### Buildings

- **production_speed_buildings_factor**
  - Effects: Changes the construction speed of all buildings.
  - Example:
    ```text
    production_speed_buildings_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **production_speed_<building>_factor**
  - Effects: Changes the construction speed of a specific building.
  - Example:
    ```text
    production_speed_industrial_complex_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **production_cost_<building>_factor**
  - Effects: Changes the base cost of a specific building.
  - Example:
    ```text
    production_cost_industrial_complex_factor = -0.1
    ```
  - Modifier type: Percentual.
  - Notes: Localization is missing and must be added yourself.
  - Version added: Unknown

- **civilian_factory_use**
  - Effects: Uses the specified amount of civilian factory as a special project.
  - Example:
    ```text
    civilian_factory_use = 3
    ```
  - Modifier type: Flat.
  - Version added: 1.5

- **consumer_goods_factor**
  - Effects: Modifies the percentage of factories used for consumer goods.
  - Example:
    ```text
    consumer_goods_factor = 0.1
    ```
  - Modifier type: Multiplicative.
  - Notes:
    ```text
    The modifier adds multiplicatively. For example,
    consumer_goods_factor = 0.5
    and
    consumer_goods_factor = -0.5
    will, in total, multiply the consumer goods value by
    (
    1
    −
    0.5
    )
    (
    1
    +
    0.5
    )
    =
    0.5
    ⋅
    1.5
    =
    0.75
    {\displaystyle (1-0.5)(1+0.5)=0.5\cdot 1.5=0.75}
    .
    ```
  - Version added: 1.0

- **consumer_goods_expected_value**
  - Effects: Sets the baseline percentage of expected consumer goods.
  - Example:
    ```text
    consumer_goods_expected_value = 0.1
    ```
  - Modifier type: Flat.
  - Notes: Used to be only updated when the economic law was changed. Now gets updated normaly.
  - Version added: 1.13

- **conversion_cost_civ_to_mil_factor**
  - Effects: Changes the cost to convert civilian factories to military factories.
  - Example:
    ```text
    conversion_cost_civ_to_mil_factor = 0.4
    ```
  - Modifier type: Percentual.
  - Version added: 1.5

- **conversion_cost_mil_to_civ_factor**
  - Effects: Changes the cost to convert military factories to civilian factories.
  - Example:
    ```text
    conversion_cost_mil_to_civ_factor = 0.4
    ```
  - Modifier type: Percentual.
  - Version added: 1.5

- **global_building_slots**
  - Effects: Changes amount of building slots in our every state.
  - Example:
    ```text
    global_building_slots = 1
    ```
  - Modifier type: Flat.
  - Version added: 1.0

- **global_building_slots_factor**
  - Effects: Changes amount of building slots in our every state by a percentage.
  - Example:
    ```text
    global_building_slots_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **industrial_capacity_dockyard**
  - Effects: Dockyard output.
  - Example:
    ```text
    industrial_capacity_dockyard = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.3.3

- **industrial_capacity_factory**
  - Effects: Military factory output.
  - Example:
    ```text
    industrial_capacity_factory = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **industry_air_damage_factor**
  - Effects: Amount of damage our factories receive from air bombings.
  - Example:
    ```text
    industry_air_damage_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **industry_free_repair_factor**
  - Effects: Changes the speed at which buildings repair themselves without factories assigned.
  - Example:
    ```text
    industry_free_repair_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **industry_repair_factor**
  - Effects: Changes the speed at which buildings are repaired.
  - Example:
    ```text
    industry_repair_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **production_oil_factor**
  - Effects: Synthetic oil gain.
  - Example:
    ```text
    production_oil_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **repair_speed_<building>_factor**
  - Effects: Changes the repair speed of a specific building.
  - Example:
    ```text
    repair_speed_arms_factory_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **supply_node_range**
  - Effects: Increases the effective range of supply nodes.
  - Example:
    ```text
    supply_node_range = 0.1
    ```
  - Modifier type: Percentual.
  - Version added: 1.11

- **static_anti_air_damage_factor**
  - Effects: Modifies the damage done to planes by the anti-air buildings.
  - Example:
    ```text
    static_anti_air_damage_factor = 0.1
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **static_anti_air_hit_chance_factor**
  - Effects: Modifies the chance for the anti-air buildings to hit enemy planes.
  - Example:
    ```text
    static_anti_air_hit_chance_factor = 0.1
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **tech_air_damage_factor**
  - Effects: Modifies the damage done to the country's planes by enemy anti-air buildings.
  - Example:
    ```text
    tech_air_damage_factor = 0.1
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **tech_air_damage_factor**
  - Effects: Modifies the damage done to the country's planes by enemy anti-air buildings.
  - Example:
    ```text
    tech_air_damage_factor = 0.1
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **cic_construction_boost**
  - Effects: Modifies the base construction speed from civilian factories.
  - Example:
    ```text
    cic_construction_boost = 0.1
    ```
  - Modifier type: Flat.
  - Version added: 1.13

- **cic_construction_boost_factor**
  - Effects: Modifies the modifier to the base construction speed from civilian factories.
  - Example:
    ```text
    cic_construction_boost_factor = 0.1
    ```
  - Modifier type: Percentual.
  - Version added: 1.13

- **land_bunker_effectiveness_factor**
  - Effects: Modifies the effectiveness of land forts in defence.
  - Example:
    ```text
    land_bunker_effectiveness_factor = 0.1
    ```
  - Modifier type: Percentual.
  - Version added: 1.13

- **coastal_bunker_effectiveness_factor**
  - Effects: Modifies the effectiveness of coastal forts in defence.
  - Example:
    ```text
    coastal_bunker_effectiveness_factor = 0.1
    ```
  - Modifier type: Percentual.
  - Version added: 1.13

#### Resistance and compliance

- **compliance_growth_on_our_occupied_states**
  - Effects: Changes the compliance growth speed on the country's controlled states.
  - Example:
    ```text
    compliance_growth_on_our_occupied_states = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.9

- **no_compliance_gain**
  - Effects: Disables the compliance gain on our controlled states.
  - Example:
    ```text
    no_compliance_gain = 1
    ```
  - Modifier type: Boolean (only 1).
  - Notes: Can also be used in state scope.
  - Version added: 1.9

- **required_garrison_factor**
  - Effects: Changes the required garrison in our occupied states.
  - Example:
    ```text
    required_garrison_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Notes: Can also be used in state scope.
  - Version added: 1.9

- **resistance_activity**
  - Effects: Changes the chance for resistance activity to occur on our occupied states.
  - Example:
    ```text
    resistance_activity = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.9

- **resistance_damage_to_garrison_on_our_occupied_states**
  - Effects: Changes the resistance damage to the garrison in our occupied states.
  - Example:
    ```text
    resistance_damage_to_garrison_on_our_occupied_states = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.9

- **resistance_decay_on_our_occupied_states**
  - Effects: Changes the resistance decay in our occupied states.
  - Example:
    ```text
    resistance_decay_on_our_occupied_states = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.9

- **resistance_growth_on_our_occupied_states**
  - Effects: Changes the resistance growth speed in our occupied states.
  - Example:
    ```text
    resistance_growth_on_our_occupied_states = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.9

- **resistance_target_on_our_occupied_states**
  - Effects: Changes the resistance target in our occupied states.
  - Example:
    ```text
    resistance_target_on_our_occupied_states = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.9

- **resistance_target**
  - Effects: Changes the resistance target in foreign states occupied by us
  - Example:
    ```text
    resistance_target = 0.5
    ```
  - Modifier type: Percentual
  - Version added: 1.9

#### Intelligence

- **agency_upgrade_time**
  - Effects: Changes the time it takes to upgrade the agency
  - Example:
    ```text
    agency_upgrade_time = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.9

- **decryption**
  - Effects: Changes the decription capability of the country.
  - Example:
    ```text
    decryption = 1
    ```
  - Modifier type: Flat.
  - Notes:
    ```text
    Only works with the
    La Résistance
    DLC disabled.
    ```
  - Version added: 1.0

- **decryption_factor**
  - Effects: Changes the decription capability of the country by a percentage.
  - Example:
    ```text
    decryption_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Notes:
    ```text
    Only works with the
    La Résistance
    DLC disabled.
    ```
  - Version added: 1.0

- **encryption**
  - Effects: Changes the encryption capability of the country.
  - Example:
    ```text
    encryption = 1
    ```
  - Modifier type: Flat.
  - Notes:
    ```text
    Only works with the
    La Résistance
    DLC disabled.
    ```
  - Version added: 1.0

- **encryption_factor**
  - Effects: Changes the encryption capability of the country by a percentage.
  - Example:
    ```text
    encryption_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Notes:
    ```text
    Only works with the
    La Résistance
    DLC disabled.
    ```
  - Version added: 1.0

- **<type>_intel_decryption_bonus**
  - Effects: Adds a cipher bonus to the specified intel.
  - Example:
    ```text
    civilian_intel_decryption_bonus = 0.5
    ```
  - Modifier type: Percentual.
  - Notes: Types are: airforce, army, civilian, navy.
  - Version added: 1.9

- **<type>_intel_factor**
  - Effects: Modifies the intelligence you receive of the specified type.
  - Example:
    ```text
    navy_intel_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Notes: Types are: airforce, army, civilian, navy.
  - Version added: 1.9

- **<type>_intel_to_others**
  - Effects: Changes the amount of intel other countries will receive of the specified type.
  - Example:
    ```text
    civilian_intel_to_others = 0.5
    ```
  - Modifier type: Percentual.
  - Notes: Types are: airforce, army, civilian, navy.
  - Version added: 1.9

- **female_random_operative_chance**
  - Effects: Changes the chance for a randomly-generated operative to be female.
  - Example:
    ```text
    female_random_operative_chance = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.9.1

- **foreign_subversive_activites**
  - Effects: Changes efficiency of foreign subversive activities.
  - Example:
    ```text
    foreign_subversive_activites = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.9

- **intel_network_gain**
  - Effects: Changes gain of intel network strength.
  - Example:
    ```text
    intel_network_gain = 1
    ```
  - Modifier type: Flat.
  - Notes: Can also be used in state scope.
  - Version added: 1.9

- **intel_network_gain_factor**
  - Effects: Changes gain of intel network strength by a percentage.
  - Example:
    ```text
    intel_network_gain_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Notes: Can also be used in state scope.
  - Version added: 1.9

- **subversive_activites_upkeep**
  - Effects: Changes the cost of subversive activities.
  - Example:
    ```text
    subversive_activites_upkeep = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **operation_cost**
  - Effects: Changes the cost of operations.
  - Example:
    ```text
    operation_cost = 0.5
    ```
  - Modifier type: Percentual.
  - Notes:
    ```text
    Dynamically created by operations with the
    cost_modifiers = { ... }
    block. This one is used by each base game operation to modify the operation cost.
    ```
  - Version added: 1.9

- **operation_outcome**
  - Effects: Changes the efficiency of operations.
  - Example:
    ```text
    operation_outcome = 0.5
    ```
  - Modifier type: Percentual.
  - Notes:
    ```text
    Dynamically created by operations with the
    outcome_modifiers = { ... }
    block. This one is used by
    each base game operation
    to modify the operation's outcome chance.
    ```
  - Version added: 1.9

- **operation_risk**
  - Effects: Changes the risk of operations.
  - Example:
    ```text
    operation_risk = 0.5
    ```
  - Modifier type: Percentual.
  - Notes:
    ```text
    Dynamically created by operations with the
    risk_modifiers = { ... }
    block. This one is used by
    each base game operation
    to modify the operation risk.
    ```
  - Version added: 1.9

- **<operation>_cost**
  - Effects: Changes the cost of the specified operation.
  - Example:
    ```text
    operation_infiltrate_cost = 0.5
    ```
  - Modifier type: Percentual.
  - Notes:
    ```text
    Operations are defined in
    /Hearts of Iron IV/common/operations/*.txt
    . Dynamically created by operations with the
    cost_modifiers = { ... }
    block.
    ```
  - Version added: 1.9

- **<operation>_outcome**
  - Effects: Changes the efficiency of the specified operation.
  - Example:
    ```text
    operation_coup_government_outcome = 0.5
    ```
  - Modifier type: Percentual.
  - Notes:
    ```text
    Operations are defined in
    /Hearts of Iron IV/common/operations/*.txt
    . Dynamically created by operations with the
    outcome_modifiers = { ... }
    block. Note that target_sabotage uses target_sabotage_factor rather than target_sabotage_outcome.
    ```
  - Version added: 1.9

- **<operation>_risk**
  - Effects: Changes the risk of the specified operation.
  - Example:
    ```text
    operation_make_resistance_contacts_risk = 0.5
    ```
  - Modifier type: Percentual.
  - Notes:
    ```text
    Operations are defined in
    /Hearts of Iron IV/common/operations/*.txt
    . Dynamically created by operations with the
    risk_modifiers = { ... }
    block.
    ```
  - Version added: 1.9

- **<mission>_factor**
  - Effects: Modifies the effect of the specified mission.
  - Example:
    ```text
    boost_ideology_mission_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Notes: Types are: boost_ideology_mission, boost_resistance, control_trade_mission, diplomatic_pressure_mission, propaganda_mission, root_out_resistance_effectiveness.
  - Version added: 1.9

- **commando_trait_chance_factor**
  - Effects: Modifies the chance for an operative to get the commando trait when hired.
  - Example:
    ```text
    commando_trait_chance_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.9

- **crypto_department_enabled**
  - Effects: Enables the crypto department.
  - Example:
    ```text
    crypto_department_enabled = 1
    ```
  - Modifier type: Boolean (only 1).
  - Version added: 1.9

- **crypto_strength**
  - Effects: Modifies the cryptology level.
  - Example:
    ```text
    crypto_strength = 1
    ```
  - Modifier type: Flat.
  - Notes:
    ```text
    La Résistance
    DLC enabled.
    ```
  - Version added: 1.9

- **decryption_power**
  - Effects: Modifies the decryption power.
  - Example:
    ```text
    decryption_power = 1
    ```
  - Modifier type: Flat.
  - Notes:
    ```text
    La Résistance
    DLC enabled.
    ```
  - Version added: 1.9

- **decryption_power_factor**
  - Effects: Modifies the decryption power by a percentage.
  - Example:
    ```text
    decryption_power_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Notes:
    ```text
    La Résistance
    DLC enabled.
    ```
  - Version added: 1.9

- **defense_impact_on_blueprint_stealing**
  - Effects: Modifies the impact of enemy defense on the blueprint stealing operation.
  - Example:
    ```text
    defense_impact_on_blueprint_stealing = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.9

- **intel_from_combat_factor**
  - Effects: Modifies the intelligence gained from combat.
  - Example:
    ```text
    intel_from_combat_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.9

- **intel_from_operatives_factor**
  - Effects: Modifies the intelligence gained from operatives and infiltrated assets.
  - Example:
    ```text
    intel_from_operatives_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.9

- **intel_network_gain**
  - Effects: Modifies the intelligence network gain.
  - Example:
    ```text
    intel_network_gain = 0.3
    ```
  - Modifier type: Flat.
  - Version added: 1.9

- **intel_network_gain_factor**
  - Effects: Modifies the intelligence network gain by a percentage.
  - Example:
    ```text
    intel_network_gain_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.9

- **intelligence_agency_defense**
  - Effects: Modifies the counter intelligence.
  - Example:
    ```text
    intelligence_agency_defense = 0.3
    ```
  - Modifier type: Flat.
  - Version added: 1.9

- **root_out_resistance_effectiveness_factor**
  - Effects: Modifies the effectiveness of rooting out resistance.
  - Example:
    ```text
    root_out_resistance_effectiveness_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.9

#### Operatives

These can be used in both the country scope and operative scope, such as traits, unless specified otherwise.

- **own_operative_capture_chance_factor**
  - Effects: Changes the chance for our operatives to be captured.
  - Example:
    ```text
    own_operative_capture_chance_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.9

- **own_operative_detection_chance**
  - Effects: Changes the chance for our operatives to be detected.
  - Example:
    ```text
    own_operative_detection_chance = 10
    ```
  - Modifier type: Flat.
  - Version added: 1.9

- **own_operative_detection_chance_factor**
  - Effects: Changes the chance for our operatives to be detected by a percentage.
  - Example:
    ```text
    own_operative_detection_chance_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.9

- **own_operative_forced_into_hiding_time_factor**
  - Effects: Changes the chance for our operatives to be forced into hiding by a percentage.
  - Example:
    ```text
    own_operative_forced_into_hiding_time_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.9

- **own_operative_harmed_time_factor**
  - Effects: Changes the chance for our operatives to be harmed by a percentage.
  - Example:
    ```text
    own_operative_harmed_time_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.9

- **own_operative_intel_extraction_rate**
  - Effects: Changes the rate at which our operatives extract enemy intel.
  - Example:
    ```text
    own_operative_intel_extraction_rate = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.9

- **enemy_operative_capture_chance_factor**
  - Effects: Changes the chance for an enemy operative to be captured.
  - Example:
    ```text
    enemy_operative_capture_chance_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.9

- **enemy_operative_detection_chance**
  - Effects: Changes the chance for an enemy operative to be detected.
  - Example:
    ```text
    enemy_operative_detection_chance = 10
    ```
  - Modifier type: Flat.
  - Version added: 1.9

- **enemy_operative_detection_chance_factor**
  - Effects: Changes the chance for an enemy operative to be detected by a percentage.
  - Example:
    ```text
    enemy_operative_detection_chance_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.9

- **enemy_operative_forced_into_hiding_time_factor**
  - Effects: Changes the chance for an enemy operative to be forced into hiding by a percentage.
  - Example:
    ```text
    enemy_operative_forced_into_hiding_time_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.9

- **enemy_operative_harmed_time_factor**
  - Effects: Changes the chance for an enemy operative to be harmed by a percentage.
  - Example:
    ```text
    enemy_operative_harmed_time_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.9

- **enemy_operative_intel_extraction_rate**
  - Effects: Changes the rate at which the enemy operatives extract our intel.
  - Example:
    ```text
    enemy_operative_intel_extraction_rate = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.9

- **enemy_spy_negative_status_factor**
  - Effects: Changes the chance an enemy spy can receive a negative status.
  - Example:
    ```text
    enemy_spy_negative_status_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.9

- **enemy_operative_recruitment_chance**
  - Effects: Modifies the chance to recruit an enemy operative.
  - Example:
    ```text
    enemy_operative_recruitment_chance = 0.3
    ```
  - Modifier type: Percentual.
  - Notes: Cannot be used in operative scope.
  - Version added: 1.9

- **new_operative_slot_bonus**
  - Effects: Modifies the operative recruitment choices.
  - Example:
    ```text
    new_operative_slot_bonus = 1
    ```
  - Modifier type: Flat.
  - Notes: Cannot be used in operative scope.
  - Version added: 1.9

- **occupied_operative_recruitment_chance**
  - Effects: Modifies the chance to get an operative from occupied territory.
  - Example:
    ```text
    occupied_operative_recruitment_chance = 0.3
    ```
  - Modifier type: Percentual.
  - Notes: Cannot be used in operative scope.
  - Version added: 1.9

- **operative_death_on_capture_chance**
  - Effects: Modifies the chance for the country's operative to die on being captured.
  - Example:
    ```text
    operative_death_on_capture_chance = 0.3
    ```
  - Modifier type: Percentual.
  - Notes: Cannot be used in operative scope.
  - Version added: 1.9

- **operative_slot**
  - Effects: Modifies the amount of operative slots.
  - Example:
    ```text
    operative_slot = 1
    ```
  - Modifier type: Flat.
  - Notes: Cannot be used in operative scope.
  - Version added: 1.9

#### AI

- **ai_badass_factor**
  - Effects: AI's threat perception.
  - Example:
    ```text
    ai_badass_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **ai_call_ally_desire_factor**
  - Effects: Chance for AI to call allies.
  - Example:
    ```text
    ai_call_ally_desire_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **ai_desired_divisions_factor**
  - Effects: The amount of divisions AI seeks to produce.
  - Example:
    ```text
    ai_desired_divisions_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **ai_focus_aggressive_factor**
  - Effects: AI's focus on offense.
  - Example:
    ```text
    ai_focus_aggressive_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **ai_focus_defense_factor**
  - Effects: AI's focus on defense.
  - Example:
    ```text
    ai_focus_defense_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **ai_focus_aviation_factor**
  - Effects: AI's focus on aviation.
  - Example:
    ```text
    ai_focus_aviation_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **ai_focus_military_advancements_factor**
  - Effects: AI's focus on advanced military technologies.
  - Example:
    ```text
    ai_focus_military_advancements_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **ai_focus_military_equipment_factor**
  - Effects: AI's focus on advanced military equipment.
  - Example:
    ```text
    ai_focus_military_equipment_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **ai_focus_naval_air_factor**
  - Effects: AI's focus on building naval airforce.
  - Example:
    ```text
    ai_focus_naval_air_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **ai_focus_naval_factor**
  - Effects: AI's focus on building a navy.
  - Example:
    ```text
    ai_focus_naval_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **ai_focus_peaceful_factor**
  - Effects: AI's focus on peaceful research and policies.
  - Example:
    ```text
    ai_focus_peaceful_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **ai_focus_war_production_factor**
  - Effects: AI's focus on wartime production.
  - Example:
    ```text
    ai_focus_war_production_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **ai_get_ally_desire_factor**
  - Effects: AI's desire to be in or expand a faction.
  - Example:
    ```text
    ai_get_ally_desire_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **ai_join_ally_desire_factor**
  - Effects: AI's desire to join the wars led by allies.
  - Example:
    ```text
    ai_join_ally_desire_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **ai_license_acceptance**
  - Effects: AI's chance to agree licensing equipment.
  - Example:
    ```text
    ai_license_acceptance = 0.5
    ```
  - Modifier type: Percentual.
  - Notes: Can be used as a targeted modifier.
  - Version added: 1.4

#### Military outside of combat

- **command_power_gain**
  - Effects: Changes the daily gain of command power.
  - Example:
    ```text
    command_power_gain = 0.5
    ```
  - Modifier type: Flat.
  - Version added: 1.5

- **command_power_gain_mult**
  - Effects: Changes the daily gain of command power by a percentage.
  - Example:
    ```text
    command_power_gain_mult = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.5

- **conscription**
  - Effects: Changes the recruitable percentage of the total population.
  - Example:
    ```text
    conscription = 0.02
    ```
  - Modifier type: Flat.
  - Version added: 1.0

- **conscription_factor**
  - Effects: Changes the recruitable percentage of the total population by a percent.
  - Example:
    ```text
    conscription_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **experience_gain_army**
  - Effects: Modifies the daily gain of army experience.
  - Example:
    ```text
    experience_gain_army = 0.5
    ```
  - Modifier type: Flat.
  - Version added: 1.0

- **experience_gain_army_factor**
  - Effects: Modifies the gain of army experience by a percentage.
  - Example:
    ```text
    experience_gain_army_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **experience_gain_navy**
  - Effects: Modifies the daily gain of naval experience.
  - Example:
    ```text
    experience_gain_navy = 0.02
    ```
  - Modifier type: Flat.
  - Version added: 1.0

- **experience_gain_navy_factor**
  - Effects: Modifies the gain of naval experience by a percentage.
  - Example:
    ```text
    experience_gain_navy_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **experience_gain_air**
  - Effects: Modifies the daily gain of air experience.
  - Example:
    ```text
    experience_gain_air = 0.05
    ```
  - Modifier type: Flat.
  - Version added: 1.0

- **experience_gain_air_factor**
  - Effects: Modifies the daily gain of air experience by a percentage.
  - Example:
    ```text
    experience_gain_air_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **land_equipment_upgrade_xp_cost**
  - Effects: Changes the experience cost to upgrade land army equipment.
  - Example:
    ```text
    land_equipment_upgrade_xp_cost = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **land_reinforce_rate**
  - Effects: Changes the rate at which reinforcements to divisions arrive.
  - Example:
    ```text
    land_reinforce_rate = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **max_command_power**
  - Effects: Changes maximum command power.
  - Example:
    ```text
    max_command_power = 20
    ```
  - Modifier type: Flat.
  - Version added: 1.5

- **max_command_power_mult**
  - Effects: Changes maximum command power by a percentage.
  - Example:
    ```text
    max_command_power_mult = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.5

- **weekly_manpower**
  - Effects: Amount of manpower gained each week.
  - Example:
    ```text
    weekly_manpower = 1000
    ```
  - Modifier type: Flat.
  - Version added: 1.6

- **naval_equipment_upgrade_xp_cost**
  - Effects: Changes the naval experience cost to upgrade equipment.
  - Example:
    ```text
    naval_equipment_upgrade_xp_cost = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **refit_ic_cost**
  - Effects: The IC cost to refit naval equipment.
  - Example:
    ```text
    refit_ic_cost = 20
    ```
  - Modifier type: Flat.
  - Version added: 1.6

- **refit_speed**
  - Effects: The speed at which naval equipment is refitted.
  - Example:
    ```text
    refit_speed = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.6

- **air_equipment_upgrade_xp_cost**
  - Effects: Changes the air experience cost to upgrade equipment.
  - Example:
    ```text
    air_equipment_upgrade_xp_cost = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **training_time_factor**
  - Effects: Modifies the training time for both army and navy.
  - Example:
    ```text
    training_time_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **minimum_training_level**
  - Effects: Changes training level necessary for the unit to deploy.
  - Example:
    ```text
    minimum_training_level = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **max_training**
  - Effects: Modifies the required experience to achieve full training.
  - Example:
    ```text
    max_training = -0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **training_time_army_factor**
  - Effects: Modifies the training time for the army.
  - Example:
    ```text
    training_time_army_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **special_forces_training_time_factor**
  - Effects: Changes the time it takes to train special forces.
  - Example:
    ```text
    special_forces_training_time_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **<land/air/naval>_doctrine_cost_factor**
  - Effects: Changes the cost of buying a new doctrine of the specified type.
  - Example:
    ```text
    land_doctrine_cost_factor = -0.05
    ```
  - Modifier type: Percentual.
  - Version added: 1.11

- **<doctrine category>_cost_factor**
  - Effects: Modifies the cost of buying a new doctrine of the specified category.
  - Example:
    ```text
    cat_mobile_warfare_cost_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Notes:
    ```text
    Doctrines are defined in
    /Hearts of Iron IV/common/technologies/*.txt
    .
    ```
  - Version added: 1.11

- **<land/air/naval>_mastery_gain_factor**
  - Effects: Modifies the speed at which mastery in a given doctrine folder is gained.
  - Examples: land_mastery_gain_factor = 0.15
  - Modifier type: Percentual.
  - Notes:
    ```text
    Doctrine tracks are defined in
    /Hearts of Iron IV/common/doctrines/folders
    .
    ```

- **<doctrine track>_track_mastery_gain_factor**
  - Effects: Modifies the speed at which mastery of a given track is gained.
  - Examples: operations_track_mastery_gain_factor = 0.1
  - Modifier type: Percentual.
  - Notes:
    ```text
    Doctrine tracks are defined in
    /Hearts of Iron IV/common/doctrines/tracks
    .
    currently existing tracks are
    Army:
    infantry
    ,
    combat_support
    ,
    armor
    and
    operations
    Air:
    fighter_aircraft
    ,
    strike_aircraft
    ,
    medium_aircraft
    and
    heavy_aircraft
    Navy:
    capital_ships
    ,
    carriers
    ,
    screens
    and
    submarines
    ```
  - Version added: 1.17

- **choose_preferred_tactics_cost**
  - Effects: Changes the cost to choose a preferred tactic.
  - Example:
    ```text
    choose_preferred_tactics_cost = 5
    ```
  - Modifier type: Flat.
  - Version added: 1.11

- **command_abilities_cost_factor**
  - Effects: Changes the cost to choose a command ability.
  - Example:
    ```text
    command_abilities_cost_factor = -0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.11

- **transport_capacity**
  - Effects: Modifies how many convoys units require to be transported over sea.
  - Example:
    ```text
    transport_capacity = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **paratroopers_special_forces_contribution_factor**
  - Effects: Modifies how much paratroopers contribute to the limit of special forces on a template.
  - Example:
    ```text
    paratroopers_special_forces_contribution_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.13

- **marines_special_forces_contribution_factor**
  - Effects: Modifies how much marines contribute to the limit of special forces on a template.
  - Example:
    ```text
    marines_special_forces_contribution_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.13

- **mountaineers_special_forces_contribution_factor**
  - Effects: Modifies how much mountaineers contribute to the limit of special forces on a template.
  - Example:
    ```text
    mountaineers_special_forces_contribution_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.13

- **special_forces_cap_flat**
  - Effects: Modifies how many special forces sub-units can be put into a single template.
  - Example:
    ```text
    special_forces_cap_flat = 10
    ```
  - Modifier type: Percentual.
  - Version added: 1.13

- **additional_brigade_column_size**
  - Effects: Changes the amount of maximum unlocked slots on each brigade column in division templates.
  - Example:
    ```text
    additional_brigade_column_size = 1
    ```
  - Modifier type: Flat.
  - Version added: 1.13

- **unit_<unit type>_design_cost_factor**
  - Effects: Modifies how much experience it costs to add a brigade of the specified type to a template.
  - Example:
    ```text
    unit_artillery_brigade_design_cost_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Notes:
    ```text
    Brigades are defined in
    /Hearts of Iron IV/common/units/*.txt
    ```
  - Version added: 1.11

- **<equipment archetype>_design_cost_factor**
  - Effects: Modifies how much experience it costs to add upgrades or modules to a specified equipment archetype.
  - Example:
    ```text
    strat_bomber_equipment_design_cost_factor = 0.3
    ```
  - Example:
    ```text
    ship_hull_heavy_design_cost_factor = -0.2
    ```
  - Modifier type: Percentual.
  - Notes:
    ```text
    Equipment archetypes are defined in
    /Hearts of Iron IV/common/units/equipment/*.txt
    ```
  - Version added: 1.11

- **module_<module type>_design_cost_factor**
  - Effects: Modifies how much experience it costs to add a module of the specified type to equipment.
  - Example:
    ```text
    module_tank_torsion_bar_suspension_design_cost_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Notes:
    ```text
    Modules are defined in
    /Hearts of Iron IV/common/units/equipment/modules/*.txt
    ```
  - Version added: 1.11

#### MIOs

These are modifiers related to military industrial organisations.

- **military_industrial_organization_research_bonus**
  - Effects: Modifies the research bonus granted by MIOs.
  - Example:
    ```text
    military_industrial_organization_research_bonus = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.13

- **military_industrial_organization_design_team_assign_cost**
  - Effects: Modifies the political power cost to assign a design team.
  - Example:
    ```text
    military_industrial_organization_design_team_assign_cost = 30
    ```
  - Modifier type: Flat.
  - Version added: 1.13

- **military_industrial_organization_design_team_change_cost**
  - Effects: Modifies the political power cost to change a design team.
  - Example:
    ```text
    military_industrial_organization_design_team_change_cost = 20
    ```
  - Modifier type: Flat.
  - Version added: 1.13

- **military_industrial_organization_industrial_manufacturer_assign_cost**
  - Effects: Modifies the political power cost to assign an industrial manufacturer.
  - Example:
    ```text
    military_industrial_organization_industrial_manufacturer_assign_cost = 10
    ```
  - Modifier type: Flat.
  - Version added: 1.13

- **military_industrial_organization_task_capacity**
  - Effects: Modifies the amount of tasks possible to assign to the MIO.
  - Example:
    ```text
    military_industrial_organization_task_capacity = 2
    ```
  - Modifier type: Flat.
  - Version added: 1.13

- **military_industrial_organization_size_up_requirement**
  - Effects: Modifies the requirement to size up a MIO.
  - Example:
    ```text
    military_industrial_organization_size_up_requirement = 2
    ```
  - Modifier type: Flat.
  - Version added: 1.13

- **military_industrial_organization_funds_gain**
  - Effects: Modifies the amount of funds gained by the MIO.
  - Example:
    ```text
    military_industrial_organization_funds_gain = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.13

- **military_industrial_organization_policy_cost**
  - Effects: Modifies the political power cost to assign a MIO policy.
  - Example:
    ```text
    military_industrial_organization_policy_cost = 20
    ```
  - Modifier type: Flat.
  - Version added: 1.13

- **military_industrial_organization_policy_cooldown**
  - Effects: Modifies the cooldown between how often it's possible to change policies.
  - Example:
    ```text
    military_industrial_organization_policy_cooldown = 5
    ```
  - Modifier type: Flat.
  - Version added: 1.13

#### Unit leaders

These are modifiers related to unit leaders in the country scope, rather than being in the unit leader scope.

- **female_random_army_leader_chance**
  - Effects: Changes the chance for a randomly-generated army leader to be female.
  - Example:
    ```text
    female_random_army_leader_chance = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.9.1

- **assign_army_leader_cp_cost**
  - Effects: Modifies the cost to assign an army leader to an army.
  - Example:
    ```text
    assign_army_leader_cp_cost = -5
    ```
  - Modifier type: Flat.
  - Version added: 1.11

- **army_leader_cost_factor**
  - Effects: The cost in political power to recruit an unit leader for the land army.
  - Example:
    ```text
    army_leader_cost_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.3

- **army_leader_start_level**
  - Effects: Bonus to the starting level of generic unit leaders.
  - Example:
    ```text
    army_leader_start_level = 1
    ```
  - Modifier type: Flat.
  - Version added: 1.5

- **army_leader_start_attack_level**
  - Effects: Bonus to the starting level of attack in generic unit leaders.
  - Example:
    ```text
    army_leader_start_attack_level = 1
    ```
  - Modifier type: Flat.
  - Version added: 1.5

- **army_leader_start_defense_level**
  - Effects: Bonus to the starting level of defense in generic unit leaders.
  - Example:
    ```text
    army_leader_start_defense_level = 1
    ```
  - Modifier type: Flat.
  - Version added: 1.5

- **army_leader_start_logistics_level**
  - Effects: Bonus to the starting level of logistics in generic unit leaders.
  - Example:
    ```text
    army_leader_start_logistics_level = 1
    ```
  - Modifier type: Flat.
  - Version added: 1.5

- **army_leader_start_planning_level**
  - Effects: Bonus to the starting level of planning in generic unit leaders.
  - Example:
    ```text
    army_leader_start_planning_level = 1
    ```
  - Modifier type: Flat.
  - Version added: 1.5

- **military_leader_cost_factor**
  - Effects: The cost in political power to recruit an unit leader.
  - Example:
    ```text
    military_leader_cost_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.3

- **female_random_admiral_chance**
  - Effects: Changes the chance for a randomly-generated admiral to be female.
  - Example:
    ```text
    female_random_admiral_chance = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.9.1

- **assign_navy_leader_cp_cost**
  - Effects: Modifies the cost to assign a navy leader to a navy.
  - Example:
    ```text
    assign_navy_leader_cp_cost = -5
    ```
  - Modifier type: Flat.
  - Version added: 1.11

- **navy_leader_cost_factor**
  - Effects: The cost in political power to recruit an unit leader for the land navy.
  - Example:
    ```text
    navy_leader_cost_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.3

- **navy_leader_start_level**
  - Effects: Bonus to the starting level of generic unit leaders.
  - Example:
    ```text
    navy_leader_start_level = 1
    ```
  - Modifier type: Flat.
  - Version added: 1.9

- **navy_leader_start_attack_level**
  - Effects: Bonus to the starting level of attack in generic unit leaders.
  - Example:
    ```text
    navy_leader_start_attack_level = 1
    ```
  - Modifier type: Flat.
  - Version added: 1.9

- **navy_leader_start_coordination_level**
  - Effects: Bonus to the starting level of coordination in generic unit leaders.
  - Example:
    ```text
    navy_leader_start_coordination_level = 1
    ```
  - Modifier type: Flat.
  - Version added: 1.9

- **navy_leader_start_defense_level**
  - Effects: Bonus to the starting level of defense in generic unit leaders.
  - Example:
    ```text
    navy_leader_start_defense_level = 1
    ```
  - Modifier type: Flat.
  - Version added: 1.9

- **navy_leader_start_maneuvering_level**
  - Effects: Bonus to the starting level of maneuvering in generic unit leaders.
  - Example:
    ```text
    navy_leader_start_maneuvering_level = 1
    ```
  - Modifier type: Flat.
  - Version added: 1.9

- **grant_medal_cost_factor**
  - Effects: Changes the cost in command power to grant a medal to a division commander.
  - Example:
    ```text
    grant_medal_cost_factor = 0.2
    ```
  - Modifier type: Percentual.
  - Version added: 1.12

- **field_officer_promotion_penalty**
  - Effects: Changes the experience penalty applied to the divisions when a commander is promoted to a field marshal.
  - Example:
    ```text
    field_officer_promotion_penalty = 0.2
    ```
  - Modifier type: Percentual.
  - Version added: 1.12

- **female_divisional_commander_chance**
  - Effects: Changes the chance to get a female divisional commander.
  - Example:
    ```text
    female_divisional_commander_chance = 0.2
    ```
  - Modifier type: Flat.
  - Notes:
    ```text
    If no generic female portraits are defined within
    /Hearts of Iron IV/portraits/*.txt
    files, there will be a silhouette.
    ```
  - Version added: 1.12

#### General combat

Note that most of these modifiers are not only in country scope but also in unit leader and navy leader scopes.

- **offence**
  - Effects: Modifies the attack value of our military, navy, and airforce.
  - Example:
    ```text
    offence = 0.5
    ```
  - Modifier type: Percentual.
  - Notes: Does not work in country scope, use army_attack_factor instead.
  - Version added: 1.0

- **defence**
  - Effects: Modifies the defence value of our military, navy, and airforce.
  - Example:
    ```text
    defence = 0.5
    ```
  - Modifier type: Percentual.
  - Notes: Does not work in country scope, use army_defence_factor instead.
  - Version added: 1.0

- **<Tactic>_preferred_weight_factor**
  - Effects: Modifies the chance for a commander to choose the specified tactic.
  - Example:
    ```text
    tactic_ambush_preferred_weight_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Notes:
    ```text
    Combat tactics are defined in
    /Hearts of Iron IV/common/combat_tactics.txt
    .
    ```
  - Version added: 1.6

#### Land combat

Note that most of these modifiers are not only in country scope but also in unit leader scope.

- **acclimatization_cold_climate_gain_factor**
  - Effects: Cold acclimatization gain factor.
  - Example:
    ```text
    acclimatization_cold_climate_gain_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **acclimatization_hot_climate_gain_factor**
  - Effects: Hot acclimatization gain factor.
  - Example:
    ```text
    acclimatization_hot_climate_gain_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **air_superiority_bonus_in_combat**
  - Effects: The bonus in combat given from having air superiority.
  - Example:
    ```text
    air_superiority_bonus_in_combat = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **army_attack_factor**
  - Effects: The bonus to land army's attack.
  - Example:
    ```text
    army_attack_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **army_core_attack_factor**
  - Effects: The bonus to land army's attack on core territory.
  - Example:
    ```text
    army_core_attack_factor = 0.1
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **army_attack_against_major_factor**
  - Effects: The bonus to land army's attack against a major country.
  - Example:
    ```text
    army_attack_against_major_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.11

- **army_attack_against_minor_factor**
  - Effects: The bonus to land army's attack against a non-major country.
  - Example:
    ```text
    army_attack_against_minor_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.11

- **army_attack_speed_factor**
  - Effects: The bonus to speed at which the land army attacks.
  - Example:
    ```text
    army_attack_speed_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **army_breakthrough_against_major_factor**
  - Effects: The bonus to land army's breakthrough against a major country.
  - Example:
    ```text
    army_breakthrough_against_major_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.11

- **army_breakthrough_against_minor_factor**
  - Effects: The bonus to land army's breakthrough against a non-major country.
  - Example:
    ```text
    army_breakthrough_against_minor_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.11

- **army_defence_factor**
  - Effects: The bonus to land army's defence.
  - Example:
    ```text
    army_defence_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **army_defence_against_major_factor**
  - Effects: The bonus to land army's defence against a major country.
  - Example:
    ```text
    army_defence_against_major_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.11

- **army_defence_against_minor_factor**
  - Effects: The bonus to land army's defence against a non-major country.
  - Example:
    ```text
    army_defence_against_minor_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.11

- **army_core_defence_factor**
  - Effects: The bonus to land army's defence on core territory.
  - Example:
    ```text
    army_core_defence_factor = 0.1
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **army_speed_factor**
  - Effects: The bonus to land army's speed.
  - Example:
    ```text
    army_speed_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **army_strength_factor**
  - Effects: The bonus to land army's strength.
  - Example:
    ```text
    army_strength_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.11

- **<unit type>_attack_factor**
  - Effects: The bonus to specified unit type's attack.
  - Example:
    ```text
    cavalry_attack_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Notes: Allowed unit types are army_armor, army_artillery, army_infantry, cavalry, mechanized, motorized, special_forces
  - Version added: 1.0

- **<unit type>_defence_factor**
  - Effects: The bonus to the specified unit type's defence.
  - Example:
    ```text
    army_artillery_defence_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Notes: Allowed unit types are army_armor, army_artillery, army_infantry, cavalry, mechanized, motorized, special_forces
  - Version added: 1.0

- **<unit type>_speed_factor**
  - Effects: The bonus to specified unit type's speed.
  - Example:
    ```text
    army_armor_speed_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Notes: Allowed unit types are army_armor and cavalry. Cavalry_speed_factor is currently broken and not recognized by the game.
  - Version added: 1.0

- **army_morale**
  - Effects: Modifies the division recovery rate.
  - Example:
    ```text
    army_morale = 10
    ```
  - Modifier type: Flat.
  - Version added: 1.0

- **army_morale_factor**
  - Effects: Modifies the division recovery rate by a percentage.
  - Example:
    ```text
    army_morale_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **army_org**
  - Effects: Modifies the army's organisation.
  - Example:
    ```text
    army_org = 10
    ```
  - Modifier type: Flat.
  - Version added: 1.0

- **army_org_factor**
  - Effects: Modifies the army's organisation by a percentage.
  - Example:
    ```text
    army_org_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **army_org_regain**
  - Effects: Modifies the army's organisation regain speed by a percentage.
  - Example:
    ```text
    army_org_regain = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.5.1

- **breakthrough_factor**
  - Effects: Modifies the army's breakthrough.
  - Example:
    ```text
    breakthrough_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **cas_damage_reduction**
  - Effects: Reduces the damage dealt by close air support.
  - Example:
    ```text
    cas_damage_reduction = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **combat_width_factor**
  - Effects: Changes our own combat width.
  - Example:
    ```text
    combat_width_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **coordination_bonus**
  - Effects: Changes the bonus to coordination, that is how much damage is done to the primary target instead of being spread out.
  - Example:
    ```text
    coordination_bonus = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.11

- **dig_in_speed**
  - Effects: Changes entrenchment speed.
  - Example:
    ```text
    dig_in_speed = 2
    ```
  - Modifier type: Flat.
  - Version added: 1.0

- **dig_in_speed_factor**
  - Effects: Changes entrenchment speed by a percentage.
  - Example:
    ```text
    dig_in_speed_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **experience_gain_army_unit**
  - Effects: Changes experience gain by the army divisions.
  - Example:
    ```text
    experience_gain_army_unit = 0.5
    ```
  - Modifier type: Flat.
  - Version added: 1.0

- **experience_gain_army_unit_factor**
  - Effects: Changes experience gain by the army divisions by a percentage.
  - Example:
    ```text
    experience_gain_army_unit_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **experience_loss_factor**
  - Effects: Changes the loss in divisions' experience in combat.
  - Example:
    ```text
    experience_loss_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **initiative_factor**
  - Effects: Modifies the initiative.
  - Example:
    ```text
    initiative_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.11

- **land_night_attack**
  - Effects: Changes the penalty due to attacking at night.
  - Example:
    ```text
    land_night_attack = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **max_dig_in**
  - Effects: Changes the maximum entrenchment.
  - Example:
    ```text
    max_dig_in = 20
    ```
  - Modifier type: Flat.
  - Notes: Can also apply in state scope.
  - Version added: 1.0

- **max_dig_in_factor**
  - Effects: Changes the maximum entrenchment by a percentage.
  - Example:
    ```text
    max_dig_in_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Notes: Can also apply in state scope.
  - Version added: 1.0

- **max_planning**
  - Effects: Changes the maximum planning.
  - Example:
    ```text
    max_planning = 20
    ```
  - Modifier type: Flat.
  - Version added: 1.0

- **max_planning_factor**
  - Effects: Changes the maximum planning by a percentage.
  - Example:
    ```text
    max_planning_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.9

- **pocket_penalty**
  - Effects: Reduces the penalty that troops take when they are encircled.
  - Example:
    ```text
    pocket_penalty = 0.2
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **recon_factor**
  - Effects: Changes reconnaisance.
  - Example:
    ```text
    recon_factor = 0.2
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **recon_factor_while_entrenched**
  - Effects: Changes reconnaisance for entrenched divisions.
  - Example:
    ```text
    recon_factor_while_entrenched = 0.2
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **special_forces_cap**
  - Effects: Changes the maximum amount of special forces by a percentage.
  - Example:
    ```text
    special_forces_cap = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **special_forces_min**
  - Effects: Changes the minimum amount of special forces.
  - Example:
    ```text
    special_forces_min = 250
    ```
  - Modifier type: Flat.
  - Version added: 1.0

- **terrain_penalty_reduction**
  - Effects: Decreases the penalties given by terrain.
  - Example:
    ```text
    terrain_penalty_reduction = 0.3
    ```
  - Modifier type: Percentual.
  - Notes: Only works in the unit_leader scope despite the modifier being present in vanilla national spirits at the time of writing.
  - Version added: 1.0

- **org_loss_at_low_org_factor**
  - Effects: Modifies the organisation loss for units when they have low organisation.
  - Example:
    ```text
    org_loss_at_low_org_factor = 0.2
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **org_loss_when_moving**
  - Effects: Modifies the organisation loss for units when they are moving.
  - Example:
    ```text
    org_loss_when_moving = 0.2
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **planning_speed**
  - Effects: Modifies the planning speed.
  - Example:
    ```text
    planning_speed = 0.2
    ```
  - Modifier type: Percentual.
  - Notes: Works in state scope.
  - Version added: 1.0

- **experience_gain_<unit type>_combat_factor**
  - Effects: Modifies the experience gain in combat for the unit type.
  - Example:
    ```text
    experience_gain_artillery_combat_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Notes:
    ```text
    Units are defined in
    /Hearts of Iron IV/common/units/*.txt
    files.
    ```
  - Version added: 1.11

- **experience_gain_<unit type>_training_factor**
  - Effects: Modifies the experience gain in training for the unit type.
  - Example:
    ```text
    experience_gain_destroyer_training_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Notes:
    ```text
    Units are defined in
    /Hearts of Iron IV/common/units/*.txt
    files.
    ```
  - Version added: 1.11

#### Naval invasions

- **naval_invasion_prep_speed**
  - Effects: Modifies the speed at which a naval invasion is prepared.
  - Example:
    ```text
    naval_invasion_prep_speed = 10
    ```
  - Modifier type: Flat.
  - Notes: Can be a targeted modifier or in unit leader scope.
  - Version added: 1.0

- **naval_invasion_capacity**
  - Effects: Modifies the amount of divisions that can have a naval invasion plan going on at the same time.
  - Example:
    ```text
    naval_invasion_capacity = 10
    ```
  - Modifier type: Flat.
  - Version added: 1.0

- **naval_invasion_penalty**
  - Effects: Modifies the penalty for naval invasions.
  - Example:
    ```text
    naval_invasion_penalty = 0.3
    ```
  - Modifier type: Percentual.
  - Notes: Is the opposite of amphibious_invasion_defence. Can also apply in state scope.
  - Version added: 1.0

- **naval_invasion_planning_bonus_speed**
  - Effects: Modifies the speed at which the planning bonus is accumulated during a naval invasion preparation.
  - Example:
    ```text
    naval_invasion_planning_bonus_speed = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.11

- **amphibious_invasion**
  - Effects: Modifies the speed of units during naval invasions.
  - Example:
    ```text
    amphibious_invasion = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.6

- **amphibious_invasion_defence**
  - Effects: Modifies the penalty given by naval invasions.
  - Example:
    ```text
    amphibious_invasion_defence = 0.5
    ```
  - Modifier type: Percentual.
  - Notes: Is the opposite of naval_invasion_penalty. Can also apply in state scope.
  - Version added: 1.6

- **invasion_preparation**
  - Effects: Modifies the required preparation needed to execute a naval invasion.
  - Example:
    ```text
    invasion_preparation = 0.3
    ```
  - Modifier type: Percentual.
  - Notes: Is the opposite of naval_invasion_prep_speed. Can be used in unit leader scope.
  - Version added: 1.6

#### Naval combat

Note that most of these modifiers are not only in country scope but also in navy leader scope as well as within equipment modules.

- **convoy_escort_efficiency**
  - Effects: Modifies the efficiency of the convoy escort mission.
  - Example:
    ```text
    convoy_escort_efficiency = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.6

- **convoy_raiding_efficiency_factor**
  - Effects: Modifies the efficiency of the convoy raiding mission.
  - Example:
    ```text
    convoy_raiding_efficiency_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.6

- **convoy_retreat_speed**
  - Effects: Modifies the speed of convoys retreating.
  - Example:
    ```text
    convoy_retreat_speed = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.6

- **critical_receive_chance**
  - Effects: Changes the chance for the enemy to get a critical hit on us in naval combat.
  - Example:
    ```text
    critical_receive_chance = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.6

- **experience_gain_navy_unit**
  - Effects: Modifies the daily gain of experience by the ships.
  - Example:
    ```text
    experience_gain_navy_unit = 0.02
    ```
  - Modifier type: Flat.
  - Version added: 1.6

- **experience_gain_navy_unit_factor**
  - Effects: Modifies the gain of experience by the ships by a percentage.
  - Example:
    ```text
    experience_gain_navy_unit_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.6

- **mines_planting_by_fleets_factor**
  - Effects: Modifies the efficiency of the mine planting mission.
  - Example:
    ```text
    mines_planting_by_fleets_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.6

- **mines_sweeping_by_fleets_factor**
  - Effects: Modifies the efficiency of the mine sweeping mission.
  - Example:
    ```text
    mines_sweeping_by_fleets_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.6

- **naval_accidents_chance**
  - Effects: Modifies the chance for a ship to be accidentally sunk or damaged.
  - Example:
    ```text
    naval_accidents_chance = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.6

- **navy_anti_air_attack**
  - Effects: Modifies the attack against enemy airplanes for the country's ships.
  - Example:
    ```text
    navy_anti_air_attack = 5
    ```
  - Modifier type: Flat.
  - Version added: 1.6

- **navy_anti_air_attack_factor**
  - Effects: Modifies the attack against enemy airplanes for the country's ships by a percentage.
  - Example:
    ```text
    navy_anti_air_attack_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.6

- **naval_coordination**
  - Effects: Modifies how quickly the fleet can gather or disperse when a target is found or when switching missions.
  - Example:
    ```text
    naval_coordination = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.6

- **naval_critical_effect_factor**
  - Effects: Modifies the effects of sustained critical hits on our ships.
  - Example:
    ```text
    naval_critical_effect_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.6

- **naval_critical_score_chance_factor**
  - Effects: Modifies the chance for us to get a critical hit on the enemy in naval combat.
  - Example:
    ```text
    naval_critical_score_chance_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.6

- **naval_damage_factor**
  - Effects: Modifies the damage dealt by our ships.
  - Example:
    ```text
    naval_damage_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.6

- **naval_defense_factor**
  - Effects: Modifies the damage received by our ships.
  - Example:
    ```text
    naval_defense_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.6

- **naval_detection**
  - Effects: Modifies the chance for our ships to detect submarines.
  - Example:
    ```text
    naval_detection = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.6

- **naval_enemy_fleet_size_ratio_penalty_factor**
  - Effects: Modifies the penalty the enemy receives for having a larger amount of ships than us.
  - Example:
    ```text
    naval_enemy_fleet_size_ratio_penalty_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.6

- **naval_enemy_positioning_in_initial_attack**
  - Effects: Modifies the positioning of the enemy during the initial naval attack.
  - Example:
    ```text
    naval_enemy_positioning_in_initial_attack = 3
    ```
  - Modifier type: Flat.
  - Version added: 1.11

- **naval_enemy_retreat_chance**
  - Effects: Modifies the chance for the enemy to retreat.
  - Example:
    ```text
    naval_enemy_retreat_chance = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.6

- **naval_has_potf_in_combat_attack**
  - Effects: Modifies the attack of the navy when fighting together with the pride of the fleet.
  - Example:
    ```text
    naval_has_potf_in_combat_attack = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.6

- **naval_has_potf_in_combat_defense**
  - Effects: Modifies the defense of the navy when fighting together with the pride of the fleet.
  - Example:
    ```text
    naval_has_potf_in_combat_defense = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.6

- **naval_hit_chance**
  - Effects: Modifies the chance for the naval attacks to land.
  - Example:
    ```text
    naval_hit_chance = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.6

- **naval_mine_hit_chance**
  - Effects: Modifies the chance for a naval mine to hit.
  - Example:
    ```text
    naval_mine_hit_chance = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.6

- **naval_mines_damage_factor**
  - Effects: Modifies the damage naval mines deal to enemy ships.
  - Example:
    ```text
    naval_mines_damage_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.6

- **naval_mines_effect_reduction**
  - Effects: Modifies the damage enemy naval mines deal.
  - Example:
    ```text
    naval_mines_effect_reduction = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.6

- **naval_morale**
  - Effects: Modifies the navy recovery rate.
  - Example:
    ```text
    naval_morale = 15
    ```
  - Modifier type: Flat.
  - Version added: 1.6

- **naval_morale_factor**
  - Effects: Modifies the navy recovery rate by a percentage.
  - Example:
    ```text
    naval_morale_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.6

- **naval_night_attack**
  - Effects: Modifies the damage dealt by the country's ships at night.
  - Example:
    ```text
    naval_night_attack = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.11

- **naval_retreat_chance**
  - Effects: Modifies the chance for the country's ships to retreat.
  - Example:
    ```text
    naval_retreat_chance = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.6

- **naval_retreat_chance_after_initial_combat**
  - Effects: Modifies the chance for the country's ships to retreat after initial combat.
  - Example:
    ```text
    naval_retreat_chance_after_initial_combat = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.11

- **naval_retreat_speed**
  - Effects: Modifies the speed at which the country's ships retreat.
  - Example:
    ```text
    naval_retreat_speed = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.6

- **naval_retreat_speed_after_initial_combat**
  - Effects: Modifies the speed at which the country's ships to retreat after initial combat.
  - Example:
    ```text
    naval_retreat_speed_after_initial_combat = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.11

- **naval_speed_factor**
  - Effects: Modifies the speed of the country's ships.
  - Example:
    ```text
    naval_speed_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.6

- **navy_org**
  - Effects: Modifies the navy's organisation.
  - Example:
    ```text
    navy_org = 10
    ```
  - Modifier type: Flat.
  - Version added: 1.0

- **navy_org_factor**
  - Effects: Modifies the navy's organisation by a percentage.
  - Example:
    ```text
    navy_org_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **navy_max_range**
  - Effects: Modifies the navy's maximum range.
  - Example:
    ```text
    navy_max_range = 10
    ```
  - Modifier type: Flat.
  - Version added: 1.0

- **navy_max_range_factor**
  - Effects: Modifies the navy's maximum range by a percentage.
  - Example:
    ```text
    navy_max_range_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **naval_torpedo_cooldown_factor**
  - Effects: Modifies the rate at which the country's ships can fire torpedos.
  - Example:
    ```text
    naval_torpedo_cooldown_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.6

- **naval_torpedo_hit_chance_factor**
  - Effects: Modifies the likelihood for country's torpedos to hit enemy ships.
  - Example:
    ```text
    naval_torpedo_hit_chance_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.6

- **naval_torpedo_reveal_chance_factor**
  - Effects: Modifies the chance that the country's submarines reveal themselves when firing torpedos.
  - Example:
    ```text
    naval_torpedo_reveal_chance_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.6

- **naval_torpedo_screen_penetration_factor**
  - Effects: Modifies the rate at which the country's torpedos penalise enemy screening.
  - Example:
    ```text
    naval_torpedo_screen_penetration_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.6

- **naval_torpedo_damage_reduction_factor**
  - Effects: Modifies the damage at which enemy torpedos damage the country's ships.
  - Example:
    ```text
    naval_torpedo_damage_reduction_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.12

- **naval_torpedo_enemy_critical_chance_factor**
  - Effects: Modifies the chance for an enemy torpedo to get a cricical hit against the country's ships.
  - Example:
    ```text
    naval_torpedo_enemy_critical_chance_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.12

- **naval_light_gun_hit_chance_factor**
  - Effects: Modifies the chance for the country's naval light guns to hit enemy ships.
  - Example:
    ```text
    naval_light_gun_hit_chance_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.12

- **naval_heavy_gun_hit_chance_factor**
  - Effects: Modifies the chance for the country's naval heavy guns to hit enemy ships.
  - Example:
    ```text
    naval_heavy_gun_hit_chance_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.12

- **navy_capital_ship_attack_factor**
  - Effects: Modifies the attack of the country's capital ships.
  - Example:
    ```text
    navy_capital_ship_attack_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.6

- **navy_capital_ship_defence_factor**
  - Effects: Modifies the defence of the country's capital ships.
  - Example:
    ```text
    navy_capital_ship_defence_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.6

- **navy_screen_attack_factor**
  - Effects: Modifies the attack of the country's screening ships.
  - Example:
    ```text
    navy_screen_attack_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.6

- **navy_screen_defence_factor**
  - Effects: Modifies the defence of the country's screening ships.
  - Example:
    ```text
    navy_screen_defence_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.6

- **navy_submarine_attack_factor**
  - Effects: Modifies the attack of the country's submarines.
  - Example:
    ```text
    navy_submarine_attack_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.6

- **navy_submarine_defence_factor**
  - Effects: Modifies the defence of the country's submarines.
  - Example:
    ```text
    navy_submarine_defence_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.6

- **navy_submarine_detection_factor**
  - Effects: Modifies the country's detection of enemy submarines.
  - Example:
    ```text
    navy_submarine_detection_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.6

- **navy_visibility**
  - Effects: Modifies the visibility of the country's navy.
  - Example:
    ```text
    navy_visibility = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.6

- **navy_weather_penalty**
  - Effects: Modifies the penalty the country's navy gets during poor weather.
  - Example:
    ```text
    navy_weather_penalty = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.11

- **night_spotting_chance**
  - Effects: Modifies the chance for the country's navy to spot the enemy at night.
  - Example:
    ```text
    night_spotting_chance = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.11

- **positioning**
  - Effects: Modifies the positioning of the country's navy.
  - Example:
    ```text
    positioning = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.6

- **repair_speed_factor**
  - Effects: Modifies the speed at which the dockyards repair the navy.
  - Example:
    ```text
    repair_speed_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.6

- **screening_efficiency**
  - Effects: Modifies the efficiency screen ships operate.
  - Example:
    ```text
    screening_efficiency = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.6

- **screening_without_screens**
  - Effects: Modifies the base screening without any screen ships assigned.
  - Example:
    ```text
    screening_without_screens = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.11

- **ships_at_battle_start**
  - Effects: Modifies the number of ships at first contact.
  - Example:
    ```text
    ships_at_battle_start = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.6

- **spotting_chance**
  - Effects: Modifies the chance to spot enemy ships.
  - Example:
    ```text
    spotting_chance = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.6

- **strike_force_movement_org_loss**
  - Effects: Modifies the organisation loss from movement during the strike force mission.
  - Example:
    ```text
    strike_force_movement_org_loss = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.6

- **sub_retreat_speed**
  - Effects: Modifies the retreat speed of submarines.
  - Example:
    ```text
    sub_retreat_speed = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.6

- **submarine_attack**
  - Effects: Modifies the attack of submarines.
  - Example:
    ```text
    submarine_attack = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.6

#### Carriers and their planes

- **navy_carrier_air_agility_factor**
  - Effects: Modifies the agility of airplanes executing tasks from carriers.
  - Example:
    ```text
    navy_carrier_air_agility_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.6

- **navy_carrier_air_attack_factor**
  - Effects: Modifies the attack of airplanes executing tasks from carriers.
  - Example:
    ```text
    navy_carrier_air_attack_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.6

- **navy_carrier_air_targetting_factor**
  - Effects: Modifies the targeting of airplanes executing tasks from carriers.
  - Example:
    ```text
    navy_carrier_air_targetting_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.6

- **air_carrier_night_penalty_reduction_factor**
  - Effects: Modifies the reduction of the night penalty for air carriers.
  - Example:
    ```text
    air_carrier_night_penalty_reduction_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **carrier_capacity_penalty_reduction**
  - Effects: Modifies the penalty given by overcrowding a carrier with planes.
  - Example:
    ```text
    carrier_capacity_penalty_reduction = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.6

- **carrier_traffic**
  - Effects: Modifies the traffic of carriers.
  - Example:
    ```text
    carrier_traffic = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.6

- **sortie_efficiency**
  - Effects: Modifies the speed when refueling and rearming planes on the carrier during the battle.
  - Example:
    ```text
    sortie_efficiency = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.6

- **carrier_sortie_hours_delay**
  - Effects: Modifies the delay in hours for refueling and rearming planes on the carrier.
  - Example:
    ```text
    carrier_sortie_hours_delay = 2
    ```
  - Modifier type: Flat.
  - Version added: 1.12

- **carrier_night_traffic**
  - Effects: Modifies the traffic of carriers at night.
  - Example:
    ```text
    carrier_night_traffic = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.11

- **fighter_sortie_efficiency**
  - Effects: Modifies the speed when refueling and rearming fighter planes on the carrier during the battle.
  - Example:
    ```text
    fighter_sortie_efficiency = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.6

#### Air combat

Note that most of these modifiers are not only in country scope but also in ace scope.

- **air_accidents_factor**
  - Effects: Modifies the chance for air accidents to happen.
  - Example:
    ```text
    air_accidents_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **air_ace_bonuses_factor**
  - Effects: Modifies the bonuses the aces grant.
  - Example:
    ```text
    air_ace_bonuses_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.11

- **air_ace_generation_chance_factor**
  - Effects: Modifies the chance for aces to appear.
  - Example:
    ```text
    air_ace_generation_chance_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.11

- **ace_effectiveness_factor**
  - Effects: Modifies the effectiveness of aces
  - Example:
    ```text
    ace_effectiveness_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **air_agility_factor**
  - Effects: Modifies the agility of the country's airplanes.
  - Example:
    ```text
    air_agility_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **air_attack_factor**
  - Effects: Modifies the attack of the country's airplanes.
  - Example:
    ```text
    air_attack_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **air_defence_factor**
  - Effects: Modifies the defence of the country's airplanes.
  - Example:
    ```text
    air_defence_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **air_interception_detect_factor**
  - Effects: Modifies the chance of detecting an enemy plane while on interception mission.
  - Example:
    ```text
    air_interception_detect_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **naval_strike_targetting_factor**
  - Effects: Modifies the ability of planes to target their objectives when executing naval strikes.
  - Example:
    ```text
    naval_strike_targetting_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **port_strike**
  - Effects: Modifies the damage done by planes on the port strike mission.
  - Example:
    ```text
    port_strike = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **air_close_air_support_org_damage_factor**
  - Effects: Modifies the damage to division organisation by planes on the close air support mission.
  - Example:
    ```text
    air_close_air_support_org_damage_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.11

- **air_bombing_targetting**
  - Effects: Modifies targetting for ground bombing.
  - Example:
    ```text
    air_bombing_targetting = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **air_cas_efficiency**
  - Effects: Modifies efficiency of close-air-support.
  - Example:
    ```text
    air_cas_efficiency = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **air_cas_present_factor**
  - Effects: Modifies impact of close-air-support in land combat.
  - Example:
    ```text
    air_cas_present_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **air_escort_efficiency**
  - Effects: Modifies ability of planes in dogfights.
  - Example:
    ```text
    air_escort_efficiency = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **air_home_defence_factor**
  - Effects: Modifies the defence of airplanes when defending states in the home region (Connected to the country's capital by land)
  - Example:
    ```text
    air_home_defence_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.11

- **air_intercept_efficiency**
  - Effects: Modifies the efficiency of air interception.
  - Example:
    ```text
    air_intercept_efficiency = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **air_manpower_requirement_factor**
  - Effects: Modifies the manpower required to deploy an airplane.
  - Example:
    ```text
    air_manpower_requirement_factor = -0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.11

- **air_maximum_speed_factor**
  - Effects: Modifies the maximum speed of the airforce.
  - Example:
    ```text
    air_maximum_speed_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **air_mission_efficiency**
  - Effects: Modifies the efficiency of airplanes in missions.
  - Example:
    ```text
    air_mission_efficiency = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **air_mission_xp_gain_factor**
  - Effects: Modifies the experience gain for airplanes for doing missions.
  - Example:
    ```text
    air_mission_xp_gain_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **air_nav_efficiency**
  - Effects: Modifies the efficiency of airplanes doing port strike and naval bombing missions.
  - Example:
    ```text
    air_nav_efficiency = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **air_night_penalty**
  - Effects: Modifies the penalty the airforce receives while at night.
  - Example:
    ```text
    air_night_penalty = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **air_power_projection_factor**
  - Effects: Modifies the power projection given out by the airplanes.
  - Example:
    ```text
    air_power_projection_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **air_range_factor**
  - Effects: Modifies the range of the airplanes.
  - Example:
    ```text
    air_range_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **air_strategic_bomber_bombing_factor**
  - Effects: Modifies the efficiency of the strategic bombing mission.
  - Example:
    ```text
    air_strategic_bomber_bombing_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **air_strategic_bomber_night_penalty**
  - Effects: Modifies the penalty for the strategic bombing mission while at night.
  - Example:
    ```text
    air_strategic_bomber_night_penalty = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **air_superiority_detect_factor**
  - Effects: Modifies the chance to detect enemy planes while on the air superiority mission. Displays as Fighter Detection.
  - Example:
    ```text
    air_superiority_detect_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **air_superiority_efficiency**
  - Effects: Modifies the efficiency of the air superiority mission.
  - Example:
    ```text
    air_superiority_efficiency = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **air_training_xp_gain_factor**
  - Effects: Modifies the air experience gain from training.
  - Example:
    ```text
    air_training_xp_gain_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.6

- **air_untrained_pilots_penalty_factor**
  - Effects: Modifies the penalty given to airplanes which don't have enough experience.
  - Example:
    ```text
    air_untrained_pilots_penalty_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.6

- **air_weather_penalty**
  - Effects: Modifies the penalty the airplanes receive because of weather.
  - Example:
    ```text
    air_weather_penalty = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **air_wing_xp_loss_when_killed_factor**
  - Effects: Modifies the experience loss of airplanes due to airplanes being shot down.
  - Example:
    ```text
    air_wing_xp_loss_when_killed_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **army_bonus_air_superiority_factor**
  - Effects: Modifies the bonus to land combat from air superiority.
  - Example:
    ```text
    army_bonus_air_superiority_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **enemy_army_bonus_air_superiority_factor**
  - Effects: Modifies the effect to land combat from enemy air superiority.
  - Example:
    ```text
    enemy_army_bonus_air_superiority_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **ground_attack_factor**
  - Effects: Modifies the bonus to airplane attack on enemy divisions by a percentage.
  - Example:
    ```text
    ground_attack_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **mines_planting_by_air_factor**
  - Effects: Modifies efficiency of airplanes planting mines.
  - Example:
    ```text
    mines_planting_by_air_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **mines_sweeping_by_air_factor**
  - Effects: Modifies efficiency of airplanes sweeping mines.
  - Example:
    ```text
    mines_sweeping_by_air_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **strategic_bomb_visibility**
  - Effects: Modifies the chance for the enemy to detect our strategic bombers.
  - Example:
    ```text
    strategic_bomb_visibility = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **rocket_attack_factor**
  - Effects: Modifies the attack given to rockets.
  - Example:
    ```text
    rocket_attack_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

#### Targeted modifiers

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

- **extra_trade_to_target_factor**
  - Effects: Adds extra produced resources available for trade to target country.
  - Example:
    ```text
    extra_trade_to_target_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.5

- **generate_wargoal_tension_against**
  - Effects: Changes world tension necessary for us to justify against the target country.
  - Example:
    ```text
    generate_wargoal_tension_against = 0.5
    ```
  - Modifier type: Flat.
  - Version added: 1.5

- **cic_to_target_factor**
  - Effects: Gives a portion of the country's civilian industry to the specified target.
  - Example:
    ```text
    cic_to_target_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.5

- **mic_to_target_factor**
  - Effects: Gives a portion of the country's military industry to the specified target.
  - Example:
    ```text
    mic_to_target_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.5

- **trade_cost_for_target_factor**
  - Effects: The cost for the targeted country to purchase this country's resources.
  - Example:
    ```text
    trade_cost_for_target_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.5

- **targeted_legitimacy_daily**
  - Effects: Changes daily gain of legitimacy of the target country.
  - Example:
    ```text
    targeted_legitimacy_daily = 0.5
    ```
  - Modifier type: Flat.
  - Version added: 1.6

- **attack_bonus_against**
  - Effects: Gives an attack bonus against the armies of the specified country.
  - Example:
    ```text
    attack_bonus_against = 0.5
    ```
  - Modifier type: Percentual.
  - Notes: Due to a bug, this will not apply to units that are defending.
  - Version added: 1.5

- **attack_bonus_against_cores**
  - Effects: Gives an attack bonus against the armies of the specified country on its core territory.
  - Example:
    ```text
    attack_bonus_against_cores = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.5

- **breakthrough_bonus_against**
  - Effects: Gives a breakthrough bonus against the armies of the specified country.
  - Example:
    ```text
    breakthrough_bonus_against = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.5

- **defense_bonus_against**
  - Effects: Gives a defense bonus against the armies of the specified country.
  - Example:
    ```text
    defense_bonus_against = 0.5
    ```
  - Modifier type: Percentual.
  - Notes: Due to a bug, this will not apply to units that are attacking.
  - Version added: 1.5

### State scope

Several country-scoped modifiers (such as a portion of those in the [land combat section](#land-combat)) unlisted here can go into state scope. A large portion of state-scoped modifiers can go into province scope.

- **army_speed_factor_for_controller**
  - Effects: Changes the division speed for the controller of the state.
  - Example:
    ```text
    army_speed_factor_for_controller = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **attrition_for_controller**
  - Effects: Changes the attrition for the controller of the state.
  - Example:
    ```text
    attrition_for_controller = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.0

- **equipment_capture_for_controller**
  - Effects: Changes the equipment capture ratio by the state's controller.
  - Example:
    ```text
    equipment_capture_for_controller = 0.3
    ```
  - Modifier type: Flat.
  - Version added: 1.13

- **equipment_capture_factor_for_controller**
  - Effects: Modifies the equipment capture ratio by the state's controller.
  - Example:
    ```text
    equipment_capture_factor_for_controller = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.13

- **enemy_army_speed_factor**
  - Effects: Modifies the speed of divisions at war with the state's owner.
  - Example:
    ```text
    enemy_army_speed_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.13

- **enemy_local_supplies**
  - Effects: Modifies the supply of divisions at war with the state's owner.
  - Example:
    ```text
    enemy_local_supplies = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.13

- **enemy_attrition**
  - Effects: Modifies the attrition of divisions at war with the state's owner.
  - Example:
    ```text
    enemy_attrition = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.13

- **enemy_truck_attrition_factor**
  - Effects: Modifies the truck attrition of divisions at war with the state's owner.
  - Example:
    ```text
    enemy_truck_attrition_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.13

- **compliance_gain**
  - Effects: Changes the compliance gain in the current state.
  - Example:
    ```text
    compliance_gain = 0.01
    ```
  - Modifier type: Flat.
  - Notes: Can also go into country scope. Can also be used as a targeted modifier.
  - Version added: 1.9

- **compliance_growth**
  - Effects: Changes the compliance growth speed in the current state.
  - Example:
    ```text
    compliance_growth = 0.5
    ```
  - Modifier type: Percentual.
  - Notes: Can also go into country scope.
  - Version added: 1.9

- **disable_strategic_redeployment**
  - Effects: Disables strategic redeployment in the state.
  - Example:
    ```text
    disable_strategic_redeployment = 1
    ```
  - Modifier type: Boolean (only 1).
  - Version added: 1.9

- **disable_strategic_redeployment_for_controller**
  - Effects: Disables strategic redeployment in the state for the controller.
  - Example:
    ```text
    disable_strategic_redeployment_for_controller = 1
    ```
  - Modifier type: Boolean (only 1).
  - Version added: 1.9

- **enemy_intel_network_gain_factor_over_occupied_tag**
  - Effects: Modifies enemy intel network strength gain.
  - Example:
    ```text
    enemy_intel_network_gain_factor_over_occupied_tag = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.9

- **local_building_slots**
  - Effects: Modifies amount of building slots.
  - Example:
    ```text
    local_building_slots = 2
    ```
  - Modifier type: Flat.
  - Version added: 1.9

- **local_building_slots_factor**
  - Effects: Modifies amount of building slots by a percentage.
  - Example:
    ```text
    local_building_slots_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.9

- **local_factories**
  - Effects: Modifies amount of available factories in the state.
  - Example:
    ```text
    local_factories = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.9

- **local_factory_energy_consumption**
  - Effects: Modifiers amount of energy consumed by factories in the state.
  - Example:
    ```text
    local_factory_energy_consumption = 0.2
    ```
  - Modifier type: Percentual
  - Notes: The game file documentation incorrectly labels this as a number with zero decimals, yet the code itself uses a decimal,
  - Version added: 1.17

- **local_factory_sabotage**
  - Effects: Modifies chance for factory sabotage.
  - Example:
    ```text
    local_factory_sabotage = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.9

- **local_intel_to_enemies**
  - Effects: Modifies amount of intel to enemies.
  - Example:
    ```text
    local_intel_to_enemies = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.9

- **local_manpower**
  - Effects: Modifies amount of available manpower.
  - Example:
    ```text
    local_manpower = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.4

- **local_non_core_manpower**
  - Effects: Modifies amount of available non-core manpower.
  - Example:
    ```text
    local_non_core_manpower = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.3.3

- **local_org_regain**
  - Effects: Modifies how much organisation is regained after combat.
  - Example:
    ```text
    local_org_regain = -0.3
    ```
  - Modifier type: Percentual.
  - Notes: Can be used in provinces and strategic regions.
  - Version added: 1.0

- **local_resources**
  - Effects: Modifies amount of available resources.
  - Example:
    ```text
    local_resources = 0.3
    ```
  - Modifier type: Flat.
  - Version added: 1.9

- **local_supplies**
  - Effects: Modifies amount of available supplies.
  - Example:
    ```text
    local_supplies = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.9

- **local_supplies_for_controller**
  - Effects: Modifies amount of available supplies for the controller.
  - Example:
    ```text
    local_supplies_for_controller = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.9

- **local_supply_impact_factor**
  - Effects: Modifies the impact that the state's local supplies have.
  - Example:
    ```text
    local_supply_impact_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.12

- **local_non_core_supply_impact_factor**
  - Effects: Modifies the impact that the state's local supplies have if the state is not cored by the controller of provinces within.
  - Example:
    ```text
    local_non_core_supply_impact_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.12

- **mobilization_speed**
  - Effects: Modifies the mobilisation speed.
  - Example:
    ```text
    mobilization_speed = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.9

- **non_core_manpower**
  - Effects: Modifies the amount of recruited non-core manpower.
  - Example:
    ```text
    non_core_manpower = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.9

- **max_fuel_building**
  - Effects: Modifies the amount of fuel capacity, in thousands, given to the state controller from the building.
  - Example:
    ```text
    max_fuel_building = 1500
    ```
  - Modifier type: Percentual.
  - Notes: Does not have to be in a building.
  - Version added: 1.0

- **recruitable_population**
  - Effects: Modifies the amount of recruited manpower.
  - Example:
    ```text
    recruitable_population = 0.03
    ```
  - Modifier type: Flat.
  - Version added: 1.9

- **recruitable_population_factor**
  - Effects: Modifies the amount of recruited manpower by a percentage.
  - Example:
    ```text
    recruitable_population_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.9

- **resistance_damage_to_garrison**
  - Effects: Modifies the amount of resistance damage to the garrison.
  - Example:
    ```text
    resistance_damage_to_garrison = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.9

- **resistance_decay**
  - Effects: Modifies the speed of resistance decay.
  - Example:
    ```text
    resistance_decay = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.9

- **resistance_garrison_penetration_chance**
  - Effects: Modifies the chance for the garrison to be penetrated.
  - Example:
    ```text
    resistance_garrison_penetration_chance = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.9

- **resistance_growth**
  - Effects: Modifies the speed of the resistance growth.
  - Example:
    ```text
    resistance_growth = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.9

- **resistance_target**
  - Effects: Modifies the target of the resistance growth.
  - Example:
    ```text
    resistance_target = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.9

- **starting_compliance**
  - Effects: Modifies the base compliance value.
  - Example:
    ```text
    starting_compliance = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.9

- **state_bunker_max_level_terrain_limit**
  - Effects:
    ```text
    Modifies the amount of available bunker building slots
    in the state.
    ```
  - Example:
    ```text
    state_bunker_max_level_terrain_limit = 6
    ```
  - Modifier type: Flat.

- **state_coastal_bunker_max_level_terrain_limit**
  - Effects:
    ```text
    Modifies the amount of available coastal bunker building slots
    in the state.
    ```
  - Example:
    ```text
    state_coastal_bunker_max_level_terrain_limit = 6
    ```
  - Modifier type: Flat.

- **state_production_speed_<building>_factor**
  - Effects: Modifies the building speed of the specified building in the state.
  - Example:
    ```text
    state_production_speed_industrial_complex_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Notes: Use state_production_speed_buildings_factor for it to apply to all buildings. (added in 1.9)
  - Version added: 1.9.1

- **state_repair_speed_<building>_factor**
  - Effects: Modifies the repair speed of the specified building in the state.
  - Example:
    ```text
    state_repair_speed_industrial_complex_factor = 0.3
    ```
  - Modifier type: Percentual.
  - Version added: 1.9.1

- **state_resource_<resource>**
  - Effects: Modifies the amount of the specified resource in the state.
  - Example:
    ```text
    state_resource_oil = 5
    ```
  - Modifier type: Flat.
  - Version added: 1.0

- **state_resources_factor**
  - Effects: Modifies the amount of resources in a state.
  - Example:
    ```text
    state_resources_factor = 0.2
    ```
  - Modifier type: Percentual.
  - Version added: 1.9

- **state_resource_cost_<resource>**
  - Effects: Modifies the amount of the specified resource in the state.
  - Example:
    ```text
    state_resource_cost_rubber = 5
    ```
  - Modifier type: Flat.
  - Version added: 1.9

- **temporary_state_resource_<resource>**
  - Effects: Modifies the amount of the specified resource in the state as an added modifier after the base one.
  - Example:
    ```text
    temporary_state_resource_tungsten = 5
    ```
  - Modifier type: Flat.
  - Version added: 1.0

- **enemy_operative_detection_chance_over_occupied_tag**
  - Effects: Offsets the chance for an enemy operative to be detected for the tag that occupies this state.
  - Example:
    ```text
    enemy_operative_detection_chance_over_occupied_tag = 5
    ```
  - Modifier type: Flat.
  - Version added: 1.9

- **enemy_operative_detection_chance_factor_over_occupied_tag**
  - Effects: Modifies the chance for an enemy operative to be detected for the tag that occupies this state.
  - Example:
    ```text
    enemy_operative_detection_chance_factor_over_occupied_tag = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.9

### Unit leader scope

Note that most modifiers in land and naval combat sections also apply.

- **cannot_use_abilities**
  - Effects: Disables using abilities.
  - Example:
    ```text
    cannot_use_abilities = 1
    ```
  - Modifier type: Boolean (only 1).
  - Version added: 1.5

- **dont_lose_dig_in_on_attack**
  - Effects: Disables losing the entrechment bonus during attack.
  - Example:
    ```text
    dont_lose_dig_in_on_attack = 1
    ```
  - Modifier type: Boolean (only 1).
  - Version added: 1.5

- **exiled_divisions_attack_factor**
  - Effects: Modifies the attack of divisions led by this unit leader if they're exiled.
  - Example:
    ```text
    exiled_divisions_attack_factor = 0.4
    ```
  - Modifier type: Percentual.
  - Version added: 1.6

- **exiled_divisions_defense_factor**
  - Effects: Modifies the defence of divisions led by this unit leader if they're exiled.
  - Example:
    ```text
    exiled_divisions_defense_factor = 0.4
    ```
  - Modifier type: Percentual.
  - Version added: 1.6

- **own_exiled_divisions_attack_factor**
  - Effects: Modifies the attack of divisions led by this unit leader if they're exiled and belong to the same country.
  - Example:
    ```text
    own_exiled_divisions_attack_factor = 0.4
    ```
  - Modifier type: Percentual.
  - Version added: 1.6

- **own_exiled_divisions_defense_factor**
  - Effects: Modifies the defence of divisions led by this unit leader if they're exiled and belong to the same country.
  - Example:
    ```text
    own_exiled_divisions_defense_factor = 0.4
    ```
  - Modifier type: Percentual.
  - Version added: 1.6

- **experience_gain_factor**
  - Effects: Modifies the experience gained by the unit leader.
  - Example:
    ```text
    experience_gain_factor = 0.1
    ```
  - Modifier type: Percentual.
  - Version added: 1.5

- **fortification_collateral_chance**
  - Effects: Chance for combat to damage enemy forts.
  - Example:
    ```text
    fortification_collateral_chance = 0.4
    ```
  - Modifier type: Percentual.
  - Version added: 1.5

- **fortification_damage**
  - Effects: Damage enemy forts receive from combat.
  - Example:
    ```text
    fortification_damage = 0.4
    ```
  - Modifier type: Percentual.
  - Version added: 1.5

- **max_commander_army_size**
  - Effects: Modifies amount of divisions that can be led by the army leader without penalty.
  - Example:
    ```text
    max_commander_army_size = 12
    ```
  - Modifier type: Flat.
  - Version added: 1.5

- **max_army_group_size**
  - Effects: Modifies amount of army groups that can be led by the field marshal without penalty.
  - Example:
    ```text
    max_army_group_size = 1
    ```
  - Modifier type: Flat.
  - Version added: 1.5

- **paradrop_organization_factor**
  - Effects: The amount of organisation paratroopers will have after paradropping.
  - Example:
    ```text
    paradrop_organization_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.5

- **paratrooper_aa_defense**
  - Effects: The strength of anti-air against paratroopers.
  - Example:
    ```text
    paratrooper_aa_defense = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.5

- **paratrooper_weight_factor**
  - Effects: Paratrooper transport space factor.
  - Example:
    ```text
    paratrooper_weight_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Notes: Can also be used in country scope.
  - Version added: 1.13

- **promote_cost_factor**
  - Effects: The cost to promote the unit leader.
  - Example:
    ```text
    promote_cost_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.5

- **reassignment_duration_factor**
  - Effects: The length of the reassignment penalty.
  - Example:
    ```text
    reassignment_duration_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.5

- **river_crossing_factor**
  - Effects: The effects of the river crossing penalty.
  - Example:
    ```text
    river_crossing_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.5

- **sickness_chance**
  - Effects: The chance for the unit leader to get sick.
  - Example:
    ```text
    sickness_chance = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.5

- **skill_bonus_factor**
  - Effects: The bonus the unit leader receives from their skillset.
  - Example:
    ```text
    skill_bonus_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.5

- **trait_<trait>_xp_gain_factor**
  - Effects: Modifies the experience gain towards the specified trait.
  - Example:
    ```text
    trait_infantry_leader_xp_gain_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.11

- **terrain_trait_xp_gain_factor**
  - Effects: Modifies the experience gain towards all terrain traits (With the type of either basic_terrain_trait or assignable_terrain_trait).
  - Example:
    ```text
    terrain_trait_xp_gain_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.5

- **wounded_chance_factor**
  - Effects: The chance for the unit leader to get wounded.
  - Example:
    ```text
    wounded_chance_factor = 0.5
    ```
  - Modifier type: Percentual.
  - Version added: 1.5

- **shore_bombardment_bonus**
  - Effects: Modifies the penalty given by the shore bombardment on divisions.
  - Example:
    ```text
    shore_bombardment_bonus = 0.5
    ```
  - Modifier type: Percentual.
  - Notes: Can apply to both army and navy leaders.
  - Version added: 1.5

### Scientists scope

- **female_random_scientist_chance**
  - Effects: The chance of spawn female scientist
  - Example:
    ```text
    female_random_scientist_chance = 0.05
    ```
  - Modifier type: Percentual.
  - Version added: 1.15

- **scientist_breakthrough_bonus_factor**
  - Effects: Modifiers scientist breakthrough bonus for special projects
  - Example:
    ```text
    scientist_breakthrough_bonus_factor = -0.25
    ```
  - Modifier type: Percentual.
  - Version added: 1.15

- **scientist_research_bonus_factor**
  - Effects: Modifiers scientist research bonus for special projects
  - Example:
    ```text
    scientist_research_bonus_factor = 0.15
    ```
  - Modifier type: Percentual.
  - Version added: 1.15

- **scientist_xp_gain_factor**
  - Effects: Modifiers scientist gain xp
  - Example:
    ```text
    scientist_xp_gain_factor = 0.02
    ```
  - Modifier type: Percentual.
  - Version added: 1.15

### Strategic region scope

This is limited to [static modifiers](#static-modifiers) defined for weather.

- **air_accidents**
  - Effects: Base chance for an air accident to happen.
  - Example:
    ```text
    air_accidents = 0.3
    ```
  - Modifier type: Flat.
  - Version added: 1.0

- **air_detection**
  - Effects: Base chance for air detection.
  - Example:
    ```text
    air_detection = -0.1
    ```
  - Modifier type: Flat.
  - Version added: 1.0

- **naval_strike**
  - Effects: Base efficiency for naval strikes.
  - Example:
    ```text
    naval_strike = -0.1
    ```
  - Modifier type: Flat.
  - Version added: 1.0

- **navy_casualty_on_sink**
  - Effects: Modifies the casualties when ships are sunk in this region.
  - Example:
    ```text
    navy_casualty_on_sink = -0.1
    ```
  - Modifier type: Percentual.
  - Version added: 1.6

- **navy_casualty_on_hit**
  - Effects: Modifies the casualties when ships are damaged in this region.
  - Example:
    ```text
    navy_casualty_on_hit = -0.1
    ```
  - Modifier type: Percentual.
  - Version added: 1.6

## Notes and references

**[^](#ref-a)** **a:** A few modifiers, such as [consumer\_goods\_factor](#consumer-goods-factor), instead get added in a multiplicative fashion. What this means is that, for example, `consumer_goods_factor = 0.1` and `consumer_goods_factor = 0.2` as separate ideas don't sum up to a 0.3 bonus, but instead multiply the consumer goods by 

(
1
+
0.1
)
(
1
+
0.2
)
=
1.1
⋅
1.2
=
1.32
{\displaystyle (1+0.1)(1+0.2)=1.1\cdot 1.2=1.32}
![{\displaystyle (1+0.1)(1+0.2)=1.1\cdot 1.2=1.32}](media/modifiers-hearts-of-iron-4-wiki_5dfb90c7fa__img29.svg), resulting in a 32% increase instead of 30%.

1. [↑](#cite-ref-1) [Developer Diary | Small Features #1](https://forum.paradoxplaza.com/forum/index.php?threads/1593911), 1.13 developer diary.

**[Modding](<Modding - Hearts of Iron 4 Wiki.md>)**
