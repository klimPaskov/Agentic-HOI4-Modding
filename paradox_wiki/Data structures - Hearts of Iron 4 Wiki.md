# Table of contents

- [Constants](#constants)
  - [Defines](#defines)
- [Flags](#flags)
  - [Example](#example)
  - [Non-boolean usage](#non-boolean-usage)
  - [Debugging](#debugging)
- [Event targets](#event-targets)
  - [Global event targets](#global-event-targets)
  - [Regular event targets](#regular-event-targets)
- [Country tag aliases](#country-tag-aliases)
- [Variables](#variables)
  - [Variable types](#variable-types)
  - [Scoping](#scoping)
  - [Trigger usage](#trigger-usage)
  - [Localisation](#localisation)
  - [Additional usage](#additional-usage)
  - [Operators](#operators)
  - [Usage examples](#usage-examples)
  - [MTTH variables](#mtth-variables)
  - [Debugging variables](#debugging-variables)
  - [Token-valued variables](#token-valued-variables)
  - [Advanced use of tokens](#advanced-use-of-tokens)
- [Modifier tokens](#modifier-tokens)
  - [Examples](#examples)
  - [Using in variables](#using-in-variables)
- [Arrays](#arrays)
  - [Arguments](#arguments)
  - [Scorers](#scorers)
    - [Example](#example)
- [Game variables](#game-variables)
  - [Game arrays](#game-arrays)
- [References](#references)


---

Within Hearts of Iron IV, there are several types of data structures, used to store data to be used for later. This can be used in-game as a way to check if some effect block was executed or not, as a counter of sorts, or something else.

## Constants

Constants serve as a way to use the same value with a reference. The constants are marked with the `@` symbol when defining or using them. An example definition is the following:

```text
@CONSTANT_1 = 10
@CONSTANT_2 = "TAG_my_idea"
```

This can later be used in the file as, for example, `cost = @CONSTANT_1`. These definitions can be in any point of the file.

Constants are available in the vast majority of game files, including most, if not all, \*.txt and \*.gui files. Constants can be used as a way to link several values to be the same if they can easily be changed at any point in the development. However, constants that store a string for its value can only be used in triggers and the attributes of elements and windows, trying to use them in an effect will result in an "invalid database object for effect/trigger" error.  
For example, if there is a large decision system where every decision is intended to have the same cost, then these constants may be used if the political power cost gets changed mid-development for better balance.  
Another example would be a scripted GUI container: if a large multitude of elements are to be at the same X or Y position, it might be worth it to link them to be a constant in case their position could be changed for better appearance or to fit in another GUI element.

Example [decision file](<Decision modding - Hearts of Iron 4 Wiki.md>) that utilises constants:

```text
@CONSTANT_1 = 10
@CONSTANT_2 = "TAG_my_idea"
TAG_decision_category = {
    TAG_decision = {
        icon = test_icon
        cost = @CONSTANT_1
        complete_effect = {
            if = {
                limit = {
                    has_ideas = @CONSTANT_2
                }
                add_stability = 0.1
            }
        }
    }
}
```

### Defines

*Main article: [Defines](<Defines - Hearts of Iron 4 Wiki.md>)*

Defines are a particular type of constant that are used within internal calculations only, defined within /Hearts of Iron IV/common/defines/\*.lua files. These cannot be referenced in any other files and are only used within the internal, unchangeable code.

Some of the things included in the defines are that events by default stay for 13 days before auto-selecting the first option or that the ai\_will\_do value is 50% higher for focuses which were unlocked by the just-completed focus. Most defines are numerical in nature, but some can be strings or blocks, such as the end date at which the game over screen appears or the list of experience need for a division to progress to the next level.  
The list of defines is vast and touches on every mechanic in the game, so if something can't be changed within the mechanic's respective files, it may be worth to check defines. Defines don't include the [Modifiers#Static modifiers](<Modifiers - Hearts of Iron 4 Wiki.md#static-modifiers>), which can serve a similar purpose but with modifier blocks.

As defines are Lua code rather than a PDXscript-interpreted file, any Lua code can go in there, however modules allowing to go out of this directory are not available. As a consequence of this, **there is no need to copy the entire file to edit it**. Defines, including graphical defines, are merely a Lua-contained array, and it is possible to modify a single member of the array in Lua using, for example, `NDefines.NGame.START_DATE = "1936.1.2.12"`. Each of these lines is contained on a separate line and there are no commas separating them, such as the following:

```text
NDefines
.
NGame
.
START_DATE
 
=
 
"1936.1.2.12"

NDefines
.
NGraphics
.
COUNTRY_FLAG_TEX_MAX_SIZE
 
=
 
2048
```

This goes into a separate file set to be evaluated after the base game defines, which is done by making the filename be later in the alphabetical order (decided by Unicode character IDs). As most Unicode characters (including every uppercase or lowercase letter) have larger IDs than the code used for the number 0, the filename is almost irrelevant.  
In the base game files, the graphical defines are set to be merged into NDefines in the last line of the base game file. However, since Lua does not create copies of tables by default, the base game's NDefines contains pointers to the actual elements, which are contained within NDefines\_Graphics regardless. For this reason, modifying either NDefines or NDefines\_Graphics works for changing graphical defines.  
A mod should **never** contain the 00\_defines.lua and 00\_graphics.lua files within of itself: these files are commonly changed even in minor game updates, and having a define missing from a file results in the mod being unstable, potentially having a crash on startup.

## Flags

In this case, flags are used in the sense of a computer variable that is used to set data to and later read it from, commonly but not necessarily of a boolean value (i.e. either 0 or 1). For editing the flags used for representing countries in-game, see [Country creation](<Country creation - Hearts of Iron 4 Wiki.md>) for the starting flags and [cosmetic tags](<Cosmetic tag modding - Hearts of Iron 4 Wiki.md>) for changing them in the middle of the game.

Flags within PDXScript are a 32-bit signed integer, ranging from -2147483648 to 2147483647. A flag can only be set to a specific value (Potentially for a certain amount of days), modified in an additive way by a certain value and read, no other operations can be done. [Variables](#variables) serve as a more operational alternative, with far more capacity for changing (Such as multiplication or non-integer values, reading game values, being able to set to other database entries rather than numbers, etc). Flags are still recommended to use as a boolean value, as these are more optimised than the variables, and so using variables will lead to an unnecessary increase in memory usage and will lead to the game running slower compared to flags.

Flags are divided into 5 scopes:

- Global. These can be read from anywhere in the game, without the need for scoping.
- Country. These are assigned to individual countries, being impossible to assign or read elsewhere. A country flag can have different values depending on which country it's checked in.
- State. These are assigned to individual states, being impossible to assign or read elsewhere. A state flag can have different values depending on which state it's checked in.
- Character. These are assigned to individual characters, being impossible to assign or read elsewhere. A character flag can have different values depending on which character it's checked in.
- Military industrial organisation. The `mio` shortnening is used in code for them, such as `set_mio_flag`.

In general, the same principles apply to them with little changes. While unit leader flags exist, these are marked as deprecated and are likely to be removed within the next updates.

A flag can be set in *any* [effect](<Effect - Hearts of Iron 4 Wiki.md>) block. There is no file where flags need to be defined, they will exist if set and stop existing when cleared.  
The simplest formatting for setting a flag is `set_country_flag = my_flag_name`. This will create the country flag (If it did not exist otherwise) and set it to be a value of 1. *This has no tooltip* and so it will be invisible to the player. [custom\_effect\_tooltip](<Effect - Hearts of Iron 4 Wiki.md#custom-effect-tooltip>) may be used to tell the player that something will be done, if wanting to keep them in the know.  
Afterwards, that flag can be checked with `has_country_flag = my_flag_name` as a trigger. This is set to be true if the flag was set, regardless of which value it has. This will create a tooltip using the flag's name as the [localisation key](<Localisation - Hearts of Iron 4 Wiki.md>). As such, `my_flag_name: "Has my flag"` will make that appear when the country flag is checked.  
If a flag is no longer useful, it can be cleared by using `clr_country_flag = my_flag_name`, which'll mark it as no longer being set. This also has no tooltip and the player will not be aware unless specifically told with the custom effect tooltip that the flag was cleared.

The exact same principles apply with global, state, and character flags. The only differences are in the used effects/triggers (In which case the word `country` is swapped with the type's name like `set_global_flag`, `has_state_flag`, or `clr_character_flag`) scopes in which they can be set and where they can be checked. For global flags, it can be done in any scope rather than the 'global' scope: it can be set in either country, state, character, or rare other scopes.

Flags can also be targeted towards a certain country. This is usually done by appending the `@TAG` to the name of the flag, though it can be placed anywhere within the tag name except for the first character. For example, `set_country_flag = my_targeted_flag_@PREV` will set it to be targeted towards the country represented by PREV, which we'll take as TAG. *This just appends the PREV's tag to the flag's name*. After this, `has_country_flag = my_targeted_flag_TAG` will come up as true for the same country it was set in. This can be used to create dynamic flags without relying on [meta effects](<Effect - Hearts of Iron 4 Wiki.md#meta-effects>). You cannot have more than one target specifier in a single tag, You can only use @ROOT, @PREV, @FROM, and @THIS, even @PREV.PREV does not work. Both of these restrictions do not apply to targeted variables, so those may be a more flexible alternative if you need.

### Example

The most common use of flags is to simply to mark a certain event (in the generic sense of a word, not necessarily the in-game event mechanic) as having occurred, such as an election, an invasion, a diplomatic deal, et cetera. For example, here's an event that starts off an election campaign in the country:

```text
country_event = {
    id = algeria_election.0         # Namespace is assumed to exist.
    title = algeria_election.0.t
    desc = algeria_election.0.desc
    
    is_triggered_only = yes
    
    immediate = {
        set_country_flag = ALG_1936_elect_campaign  # Since set_country_flag has no tooltip, no need to hide it.
    }
    
    option = {
        < ... >                     # Irrelevant what's in the option
    }
}
```

Flags provide a way to mark that this event has been received, in this case set within the immediate effect block of the event.

In order to utilise this, the `has_country_flag` trigger will have to be used similarly to this example decision:

```text
ALG_1936_campaign_category = {         # Decision category is assumed to exist and contain 'allowed = { tag = ALG }'
    ALG_1936_select_candidate_A = {
        available = {
            has_country_flag = ALG_1936_elect_campaign
        }
        
        icon = ALG_elect
        cost = 50
        fire_only_once = yes
        
        complete_effect = {
            country_event = algeria_election.1
        }
    }
}
```

This will work fine, however, as is, the player will see either a ![Yes](media/data-structures-hearts-of-iron-4-wiki_6e1fd6f20a__img1.png) check mark or a ![No](media/data-structures-hearts-of-iron-4-wiki_6e1fd6f20a__img2.png) cross next to 'ALG\_1936\_elect\_campaign', with no indication what that truly means. In order to correct that, a localisation entry can be added to any working localisation file (i.e. is an \*.yml file within the /Hearts of Iron IV/localisation/ folder or any of its subfolders, has the internal name of the language in the end of filename before the extension, and is encoded in UTF-8 with the byte order mark present):

```text
 ALG_1936_elect_campaign: "The 1936 election campaign is currently ongoing"
```

In order to clear the flag when needed, the `clr_country_flag` effect would be used as such:

```text
country_event = {
    id = algeria_election.100         # Namespace is assumed to exist.
    title = algeria_election.100.t
    desc = algeria_election.100.desc
    
    is_triggered_only = yes
    option = {
        name = algeria_election.100.a
        trigger = {
            has_country_flag = ALG_candidate_A_won
        }
        clr_country_flag = ALG_1936_elect_campaign
        < ... >                     # Irrelevant what else is in the option
    }
    option = {
        name = algeria_election.100.b
        trigger = {
            has_country_flag = ALG_candidate_B_won
        }
        clr_country_flag = ALG_1936_elect_campaign
        < ... >                     # Irrelevant what else is in the option
    }
    < ... >                         # Other potential options
}
```

Note that neither of the effects that modify country flags have tooltips, so [a custom effect tooltip can be used to notify the player](<Effect - Hearts of Iron 4 Wiki.md#effect-tooltips>) in some cases.  
Everything is the exact same for flags of other scope types.

### Non-boolean usage

This will cover the non-boolean usage of flags. [Variables](#variables) usually do this job better, but this still has some usages.

The `set_<type>_flag` effect can also be expanded with the optional `days` and `value` arguments. This will appear like the following:

```text
set_state_flag = {
    flag = my_state_flag
    days = 50
    value = 3
}
```

This in particular will set the flag my\_state\_flag to the state to be equal to 3 for 50 days. After these 50 days end, the flag will be cleared completely, reset to 0. If days are left out, the flag will be set to that value forever. If the value is left out, the flag will not be changed.

And the trigger if a flag is set can also be expanded as such:

```text
has_global_flag = {
    flag = my_global_flag
    value > 2
    days > 30
    date < "1938.1.1"
}
```

While the flag and the value arguments are self-explanatory, `days` checks how many days it was *since the flag was set* (Not how many are remaining), while the `date` checks the date at which the flag is set. Every argument aside from the `flag` one is optional, just assumed to be always true if not set. This trigger will still always fail if the flag was never set or if it was cleared.

Additionally, it is possible to *modify* a flag as such:

```text
modify_character_flag = {
    flag = my_character_flag
    value = 4
}
```

This *adds* the amount to the flag, with negatives being possible. However, there's one catch: **this does nothing if the flag is not set**, having a value of 0.

Each of the preceding examples can be used for any flag type.

### Debugging

The following console commands exist for debugging variables. In console commands, the 'current scope' is what is currently selected: the country opened in diplomacy, the state selected, the unit leader that's selected. If left out, assumes to be the player country.

- **set_country_flag**
  - Parameters:
    ```text
    <flag>
    The name of the flag to set.
    ```
  - Example:
    ```text
    set_country_flag my_flag
    ```
  - Description: Sets the country flag for the country controlled by the player.

- **set_global_flag**
  - Parameters:
    ```text
    <flag>
    The name of the flag to set.
    ```
  - Example:
    ```text
    set_global_flag my_flag
    ```
  - Description: Sets the global flag.

- **list_flags**
  - Parameters:
    ```text
    <scope>
    Optional. Changes the scope from the currently-selected scope to what's specified.
    ```
  - Example:
    ```text
    list_vars
    ```
  - Description: Lists currently active flags in the console window, with their value. Context senstive if nothing (global_flag), country (country_flag) or state (state_flag) is selected when entering this command.

## Event targets

Event targets serve as a primitive way to set a pointer to a scope (country, state, character) to be referred to later. Any single event target can only point towards a single scope at a time, however a scope may have several event targets at the same time. Similarly to flags, there is no set folder for event targets, they can be assigned in any event block.  
There are two types of event targets: regular and global. The difference between them is purely when they get cleared.

A scope can be checked if it has an event target assigned using `has_event_target = name_of_event_target`.

### Global event targets

Global event targets can be declared using `save_global_event_target_as = my_event_target` as an effect. This will create the global event target with the name of `my_event_target` and it will last forever. Afterwards, it can be referred to as `event_target:my_event_target`, both as a scope and as a target.

If `save_global_event_target_as = my_event_target` is used when the event target is already set, the event target will change scopes to the one where the effect is used.  
Additionally, `clear_global_event_target = my_event_target` (to be used in any scope, not necessarily the event target) will clear the specified global event target entirely, while `clear_global_event_targets = ROOT` will clear every global event target from the specified scope.

For example, by using [start\_civil\_war](<Effect - Hearts of Iron 4 Wiki.md#start-civil-war>) as an effect block, the following will assign the TAG\_democratic\_side event target to the revolter:

```text
start_civil_war = {
    size = 0.5
    ideology = democratic
    save_global_event_target_as = TAG_democratic_side
}
```

After this, TAG\_democratic\_side event target will refer to the democratic side. For example, this code later in another effect block can be used to transfer a state and a part of the armies to the event target:

```text
event_target:TAG_democratic_side = {
    transfer_state = 123
}
transfer_units_fraction = {
    target = event_target:TAG_democratic_side
    size = 0.2
}
```

It would make sense to clear the event target after it no longer exist, such as by using the [on\_civil\_war\_end on action](<On actions - Hearts of Iron 4 Wiki.md#on-civil-war-end>).

When using the event target as a scope for a namespace in localisation, the `event_target:` prefix is not needed, instead it'll look like `[TAG_democratic_side.GetName]`.

### Regular event targets

Regular event targets can be declared using `save_event_target_as = my_event_target` as an effect. The difference between regular and global event targets is in when they get cleared. While global event targets are used forever and can only be cleared manually, regular event targets only last as long as the effect block does (carrying over into events fired within as well), clearing automatically afterwards, and there is no way to clear them manually.

For example, this in an effect block will save a random owned and controlled state as the event target `target_state` and then fire the event mod\_event.0 in 10 days:

```text
random_owned_controlled_state = {
    save_event_target_as = target_state
}
country_event = { id = mod_event.0 days = 10 }
```

Assuming no other events, this event target will only exist within this effect block and the event mod\_event.0 (Where it can be used in its corresponding trigger or effect blocks). If the event mod\_event.0 fires another event within a corresponding effect block, this event target will exist in that event as well, meaning that this carries over to the entire mod\_event.0-starting event chain. For example, the generic event [generic.23 ([From.GetNameDefCap] Demands Control of [demanded\_prov\_target.GetName])](https://hoi4.paradoxwikis.com/Generic_events#generic.23) uses this with demanded\_prov\_target as the event target. In order to make ROOT demand the state 123 from TAG using this, this effect block will be used:

```text
123 = {
    save_event_target_as = demanded_prov_target
}
TAG = {
    country_event = generic.23
}
```

Event targets can be used in *most* effect blocks, they are called event targets only because they carry over to events. However, there are a few effect blocks, such as scripted diplomatic actions, where event targets are impossible to set.

## Country tag aliases

Country tag aliases are somewhat similar to event targets: they are used as pointers towards a specific scope, a single alias can point towards a single scope, and a single scope can have several aliases. However, there are differences. Primarily, country tag aliases can only point towards countries (as per the name) and they are set and cleared entirely automatically without any manual involvement. A country tag alias can point towards a non-existing country.

Country tag aliases are stored within /Hearts of Iron IV/common/country\_tag\_aliases/\*.txt files. Each country tag alias is stored as a separate block within the file, with the name of the block being the name of the alias. Additionally, the country tag aliases serve as a trigger block, so any trigger can be used within. These are the arguments that can be used within:

- `variable = global.var_name` - This will make sure that the country tag alias is equivalent to the country that the specified [variable](#variables) points to, in this case `var_name` assigned to the global scope.
- `event_target = my_event_target` - This will make sure that the country tag alias is equivalent to the country that the specified **regular** event target points to, in this case `my_event_target`.
- `global_event_target = my_event_target` - This will make sure that the country tag alias is equivalent to the country that the specified **global** event target points to, in this case `my_event_target`.
- `original_tag = TAG` - This puts every country that originates from TAG (created with [start\_civil\_war](<Effect - Hearts of Iron 4 Wiki.md#start-civil-war>) or [create\_dynamic\_country](<Effect - Hearts of Iron 4 Wiki.md#create-dynamic-country>)) as a possible target for the alias. In this case, further specification is needed with triggers. This is equivalent to the original\_tag trigger, but this is treated as an argument here as it does make certain errors go away.
- `targets = { ABC DEF GHI }` - This is a whitespace-separated list of country tags that the country tag alias can select. In this case, further specification is needed with triggers.
- `target_array = global.my_array` - This puts every country that's within the specified array (`my_array` in the global scope in this case) as a possible target for the country tag alias. In this case, further specification is needed with triggers.
- `country_score = { ... }` - This is a [MTTH block](<AI modding - Hearts of Iron 4 Wiki.md#mtth-blocks>) evaluated for each country. The country which has the highest total score will be picked for the country tag alias, provided the conditions imposed by every other argument are met.
- `fallback = TAG` - This is what the country tag alias will point to if no country fulfills the conditions specified within triggers or other arguments.

Here are some examples of country tag aliases:

```text
MOD = {
    targets = { ABC DEF GHI }
    has_country_flag = my_flag
    country_score = {
        base = 1
        modifier = {
            add = 2
            tag = ABC
        }
        modifier = {
            add = 1
            tag = DEF
        }
    }
    fallback = ABC  # This will point to ABC, DEF, or GHI if they have the specified country flags. ABC is prioritised over DEF, which is prioritised over GHI. If neither have the country flag, defaults to ABC.
}
ARB = {
    target_array = global.arab_countries
    has_cosmetic_tag = ARABIA_UNITED    # This will point to any country in the global.arab_countries array if they have the ARABIA_UNITED cosmetic tag, provided they exist.
    exists = yes
}
```

This is most commonly used with [start\_civil\_war](<Effect - Hearts of Iron 4 Wiki.md#start-civil-war>) or [create\_dynamic\_country](<Effect - Hearts of Iron 4 Wiki.md#create-dynamic-country>). For example:

```text
SDA = {
    original_tag = SDI
    has_country_flag = SDI_side_A
}
```

In order for this country tag alias to get used for side A of the civil war, it must have the country flag set. This is usually done directly in the effect that spawns it:

```text
start_civil_war = {
    ideology = neutrality
    size = 0.5
    set_country_flag = SDI_side_A
}
```

After doing this, it's possible to use `SDA` as if it's a regular country tag, e.g. `SDA = { add_political_power = 100 }` or `transfer_state_to = SDA`.

separate from the method above another easier method to give custom tag to a dynamic d## country eg d04 (this method does not require a flag to be set)

in common\country\_tag\_aliases\tag\_aliases.txt add

```text
INA = {                                  #new tag
	original_tag = INS
	has_government = monarchism     #change monarchism to democratic etc to define which faction you want
}
```

The INA tag above will be functional without any other changes e.g. `INA = { add_political_power = 100 }`

using a limit

```text
        if = {                                          ## Put this inside completion reward in a focus to create a custom cosmetic tag for a dynamic country, 
	limit = { 					##checks both conditions below match
		any_country = { original_tag = INS } 	##INS is original country Tag
		NOT = { has_government = democratic } 	## democratic/neutrality etc is government type change it to usually the government type of the original country or  , custom ideologies can be used here too.
		}					##  if the civil war has  MORE than 2 factions of differing government types  copy the NOT line and enter the third factions government type. 
	set_cosmetic_tag = INA				## set any country matching the above conditions to cosmetic tag INA that can be used.
	}
```

To Change a Dynamic country Name the name file you need is \localisation\countries\_cosmetic\_l\_english.yml

add the below lines (rename inside " " to suit your needs)

```text
 INA:0 "Indonesia Royalist uprising"                         #INA is new cosmetic tag created above
 INA_AST_autonomy_puppet_DEF:0 "Royal $OVERLORDADJ$ Indies"  # will change name to overlords adjective
```

## Variables

A variable within Hearts of Iron IV is a signed 32-bit fixed point number with scaling of 

1
1000
{\displaystyle {\frac {1}{1000}}}
![{\displaystyle {\frac {1}{1000}}}](media/data-structures-hearts-of-iron-4-wiki_6e1fd6f20a__img3.svg). As such, it ranges from -2 147 483.648 to 2 147 483.647. Adding further amounts above or below the variable will result in an [overflow](http://en.wikipedia.org/wiki/Integer_overflow), causing the value go from the maximum to the minimum or vice-versa.

Variables are not stored within any particular file and can be created dynamically with any [effect](<Effect - Hearts of Iron 4 Wiki.md>) or (temporary variables-only) trigger. Each database object (such as countries, states, ideas, or even equipment types) has a unique internal numeric ID, which can be assigned to a variable. For example, setting a variable's value to a country tag will make it take on the ID of the tag, and then the variable will be taken as a country when used as a target or as a scope. For [tokenizable database types](#token-valued-variables), a `token:` prefix is necessary when assigning a literal, for example: `var_name = token:some_idea_name`.

When using a variable as a scope, the `var:` prefix is needed, however in some cases the prefix is optional: most notably when using it as the target of an effect or trigger. For example, in `transfer_state = var:my_state_variable`, the `var:` can be omitted with no difference (For some cases, there will be logged errors, yet it will work in-game), but in `var:my_country_variable = { transfer_state = 123 }` the `var:` is *mandatory*. Despite functioning similarly to a scope, the `var:` prefix is optional when a variable is used as a weight inside of [random\_list](<Effect - Hearts of Iron 4 Wiki.md#random-effects>). Same as with event targets, using variables in localisation for namespaces does not require the `var:` prefix, such as `[?var_name.GetName]`. A good rule of thumb is that when passing a variable in a place where a raw token (rather than, say, a quoted string, a number, or a numeric state ID) is acceptable, it must usually be prefixed with `var:` so that the parser can distinguish whether the token being passed is meant to reference a database object or a variable. If `var:` is absent in a location where it should be present, the code may work, but the game will often complain in the error log. In general, it is best to err on the side of caution in this regard, as what may result in a merely-complaining error in one context, might result in an effect-nullifying, or worse, trigger-falsifying, error in another context. However, `var:` is always optional in variable and array manipulation operators (including `check_variable`), and so it can be elided in those operators for readability's sake.

Within their names, variables can have any word character, i.e. the 26 English letters (Either lowercase or uppercase), underscores, and the decimal digits from 0 to 9. However, a variable name cannot *begin* with a decimal digit, so a name like `123_my_variable` is invalid. This requirement common in many programming languages, and is implemented here for the same reason that the `var:` prefix exists: so that the parser can determine what syntactic type a token will be from the first (few) characters, and therefore doesn't have to worry about backtracking as much. In addition, it is recommended to avoid any names by variables that are already used for something else. For example, naming a variable `capital` can prevent any subsequent usage of the [game variable with the same name](#game-variables) within the internal code. A common naming convention to avoid overlap is to add a prefix signifying where it's used, such as the country's tag (`POL_capital`) or the name of the mechanic (Usually shortened like `PC_capital`).

### Variable types

There are two types of variables: regular and temporary. There are the following differences between the two:

- Different effects are used to set and modify regular and temporary variables. Typically, the difference is just in changing `variable` to `temp_variable`.
- Temporary variables only exist within the effect or trigger block where they're defined, similarly to regular event targets (although without carrying over to events). This does not mean they don't survive outside of the scope where they're defined, but the '*entire* effect block, such as a focus reward or an event option. Meanwhile, regular variables exist forever. Note that this, however, does not always function properly in regards to scripted effects or triggers: temporary variables defined within of them may not still exist outside of them within the same effect/trigger block. However, a temporary variable defined before the scripted effect or trigger's usage will always carry on into it and get modified properly within.
- Due to the previous point, **temporary variables can be defined and modified in trigger blocks** as well as in effect blocks. This enables them to be computed as-needed in scripted triggers called from the `trigger` block of scripted localizations. Meanwhile, regular variables are restricted to only being defined in effect blocks.
- Temporary variables are unscoped: they will remain the same regardless of in which scope they're defined and where they're checked. Meanwhile, regular variables are restricted to scopes, so that the variable has different values depending on which scope it's checked in, such as how different countries may have different stability values.

### Scoping

**Scoping only exists for regular variables.** They can and must be assigned to countries, states, characters, and to the global scope.  
If nothing else is specified, the current scope, or [THIS](<Scopes - Hearts of Iron 4 Wiki.md#this>), is used as the scope of the variable. For example, `ABC = { set_variable = { my_var = 1 } }` will set the variable with the name of my\_var within the scope of ABC. `CBA = { check_variable = { my_var = 1 } }` would then come up as false, since it checks for the variable only within CBA, while the variable is set in ABC.

The scope where the variable is read can be changed by prepending any [dual scope](<Scopes - Hearts of Iron 4 Wiki.md#dual-scopes>) that can be used as a target and can be used in any scope (For example, character scopes can not be prepended before variable because character scopes are not any-scoping scopes, which means they can not be used in other character scopes.) before the variable's name, separated with a dot, such as `PREV.PREV.var_name` being the value of `var_name` as checked for `PREV.PREV` or `event_target:my_event_target.var_name`. This also includes `global` in order to assign it globally, **which is necessary to scope into global**. Other variables, if pointing to a scope, can also be used, but the `var:` is unneeded. Variables must be chained using the `:` separator (rather than the usual dot), such as `ABC.capital:var_name` being the variable `var_name` as it's assigned to the capital state of the country ABC, where `capital` is a built-in variable pointing to the capital state of the country. Note that the scope specifier preceding `capital` is separated from it by a `.` since it is a static (that is, non-variable) scope. The way to intuit this syntax is that the whole `ABC.capital` clause forms a variable scope specifier, in which `var_name` is accessed.

Here are some examples of scoped variable references:

```text
var_name                                    # Scopes to THIS
GER.var_name                                # Scopes to GER
123.var_name                                # Scopes to state 123
global.var_name                             # Scopes to global
province_controllers^1234:capital:var_name  # Scopes to the capital state of the country that controls the province 1234.
```

In practice, scoping to distinguish variables may look like this:

```text
every_country = {
    set_variable = { weighted_manpower = 0 } # Reset the counter to default in case it already exists
    every_owned_state = {
        set_variable = { weighted_manpower = state_population_k } # Completely unrelated to the above variable due to being in a different scope
        if = {
            limit = {
                NOT = { is_core_of = PREV } # Is core of the owner
            }
            divide_variable = { weighted_manpower  = 10 } # Divides the state's equivalent
        }
        add_to_variable = { PREV.weighted_manpower = weighted_manpower } # Adds to the owner's counter
    }
}
```

In this case, each state has a `weighted_manpower` variable which is equal to the population in thousands if it's a core of the owner at the time of being set and it's divided by 10 otherwise. Each country will also have a `weighted_manpower` variable, which sums up the weighted manpower of each state. Despite having the same name, these variables are completely unrelated to each other due to one being country-level and the other being state-level.

### Trigger usage

**Only temporary variables can be modified within a trigger block.** Regular variables can only be used in effects, while temporary can be used in both triggers and effects.

However, there's one aspect of triggers that's important to know: *when* each scope stops evaluating. If a scope stops evaluating, then the variable will not be modified anymore. In general, [trigger scopes](<Scopes - Hearts of Iron 4 Wiki.md#trigger-scopes>) that can select multiple targets are divided into two groups: `all_<scope type>` and `any_<scope type>`. The first group, requiring all targets to meet triggers, evaluates each target in order and stops when it encounters one where the triggers aren't met. The second group, requiring any target to meet triggers, evaluates each target and stops when it encounters a true one.  
Empty trigger blocks are considered true by default, so one would instantly stop the validation of the second group (`any_` triggers). For this reason, [since scope limits are not supported in trigger scopes](<Scopes - Hearts of Iron 4 Wiki.md#scope-limits>), then the proper usage for modifying temp variables would be an if statement that modifies the variable if the limit is met with no other triggers that can come up as true or false coming up.

### Localisation

*Parts of this section are transcluded from [Localisation § Formatting variables](<Localisation - Hearts of Iron 4 Wiki.md#formatting-variables>)*

In order to display the value of a variable in localisation, `[?var_name]` is used, with the question mark signifying that it's a variable. **The question mark is mandatory** in order to distinguish the variable from the event targets. For example, such a localisation value will work:  `var_value_tt: "There are [?num_of_dogs] dog(s) in the country"`  
By default, the scope where this is used gets assumed. Scoping works the same way as it does with variables regularly:  `GER_var_value_tt: "There are [?GER.num_of_dogs] dog(s) in [GER.GetNameWithFlag]"`  
When the variable is a scope by itself, the question mark is still mandatory to use to distinguish from event targets:  `target_tt: "The target country is [?target_country.GetName]"`. **Variables can only be displayed in UI that supports dynamic localisation**, otherwise it will appear exactly as in the localisation file. List of such UI elements and necessary conditions for them to support dynamic localisation can be found in [Localisation § Namespaces](<Localisation - Hearts of Iron 4 Wiki.md#namespaces>).

If the variable points to a certain address with more localised text, such as a country, namespaces can be used in the same manner as with a regular tag or event target:  `most_dogs_tt: "[?most_dogs.GetNameDefCap] has the most dogs out of any country."` Question marks are still mandatory to include in this case.

Variables have a unique way for applying colouring, also allowing extra formatting characters. These are applied after a pipe placed at the end of the variable's name, such as `[?my_variable|R]` that will turn the colour of the variable `my_variable` red. If no colouring is applied, it will use the same colour as regular text: the §-colour block, textbox's `text_color_mode`, or the font's default colour in that order.

The list of formatting characters that are restricted to variables only are the following:

- *****
  - Effect: Converts the variable to SI units—appends "K" or "M" and divides the variable appropriately, such as 65 536 becoming 65.53K and 1 500 000 becoming 1.50M. Displays 2 decimals after the dot by default.

- **^**
  - Effect: Same as *.

- **=**
  - Effect:
    ```text
    Prefixes the variable with
    +
    if the value is positive or
    -
    if it is negative.
    ```

- **0..9**
  - Effect: Controls the number of decimals to display. Due to the nature of the game's variables, there are no more than 3 decimals that can be shown. Using any digit greater than 3 will instead have the same result as 3.

- **%**
  - Effect: Converts the variable to percentage, multiplying by 100 and appending a %. By default, will show 2 digits after the decimal point, though the second digit will always be 0.

- **%%**
  - Effect: Appends a percentage to the end of the variable without multiplying by 100.

- **+**
  - Effect: Colours the variable green if positive, yellow if zero, red if negative.

- **-**
  - Effect: Colours the variable red if positive, yellow if zero, green if negative.

Any unrecognised symbols will neither change how the variable is localised nor get recognised as an error in-game. For example, it's common practice in the base game to prepend a dot before the digit used to control the amount of displayed digits as `[?var|.1]`. In case of overlap between mutually-exclusive rules, the last-used one will be prioritised. However, static colouring has a lower priority than dynamic colouring (e.g. `[?var|+Y]` will be treated as `[?var|+]`), and using `%%` will also override `%`.

Some examples of formatting characters in usage:

```text
l_english
loc_key
"Democratic
 
party
 
popularity:
 
[?party_popularity@democracy|%G0]"
 

 
loc_key_2
"Modifier
 
token's
 
value:
 
[?modifier@my_modifier|.1%%+]"

 
pol_power_trigger_tt
"Has
 
more
 
than
 
[?var_name|Y]
 
political
 
power"
```

Within these examples, the first string depicts the current scope's democratic popularity as a percentage multiplied by 100 (%), in green (G), rounded to a whole number with 0 decimals (0). The second string displays the `my_modifier` [modifier token](<Modifiers - Hearts of Iron 4 Wiki.md#modifier-tokens>)'s value as a 'good' number (+ making it green if positive, red if negative), with a percentage sign appended in the end (%%) and rounded to a number with one decimal (.1). The third string displays the variable in yellow colouring (as is common in the base game's tooltips), leaving it unchanged otherwise.

By default, variable-related arguments such as `set_variable` or `check_variable` do not have a tooltip. For *some* of these arguments, such as `add_to_temp_variable`, it is possible to set a tooltip with an optional `tooltip = localisation_key` argument within. Others, such as `check_variable`, do not support this and a custom tooltip must be used instead, whether it's for [effects](<Effect - Hearts of Iron 4 Wiki.md#tooltip-manipulation>) or for [triggers](<Triggers - Hearts of Iron 4 Wiki.md#custom-trigger-tooltip>).

This tooltip argument is notable since the value of that localisation key allows using two [strictly-internal variables](<Localisation - Hearts of Iron 4 Wiki.md#nested-strings>) marked with dollar signs: `$LEFT$` and `$RIGHT$`.  
`$LEFT$` represents the variable's value before the operation, while `$RIGHT$` represents the variable's value after the operation. This can be used to let the player know the current and/or the potential value of the variable in the same localisation key without taking up more space with `custom_effect_tooltip`.

Here's an example of it being done:

```text
add_to_variable = {
    var = num_dogs
    value = ENG.num_cats
    tooltip = add_cats_to_dogs_tt
}
```

This is the effect itself. Within localisation, this would be done:

```text
 add_cat_to_dogs_tt: "Adds [ENG.GetAdjective] cats to our $LEFT$ dog(s) to get $RIGHT$ in total."
```

### Additional usage

By default, an unset variable is equal to zero when checked. However, the game also provides a [null coalescing operator](http://en.wikipedia.org/wiki/null_coalescing_operator) for variables, used with a question mark. For example, `cost = var_name?100` within a decision will result in the cost of the decision being the same as var\_name for the country. However, if that variable was never set or was cleared beforehand, then the decision will cost 100 ![Political Power](media/data-structures-hearts-of-iron-4-wiki_6e1fd6f20a__img4.png)Political Power instead of 0.

Similarly to flags, a variable can be set as targeted by appending the target with `@TAG`. However, there are differences: in variables this does not append the target's ID to the name but stores it as a separate variable, as well as it being possible to target far more than countries, but also, for example, states or ideology groups. A variable reference `var_name_@GER` would resolve to a variable named `var_name_GER`. If called in a scope where PREV`= { tag = ENG }`, a variable reference `var_name_@PREV` would resolve to a variable named `var_name_ENG`. This can even be applied to temporary variables. You can also target variables using the syntax `var_name_@var:target_var_name`, regardless of the type of their value: be it country, state, token, even a raw integer. Variables targeting tokenizable types such as ideology groups and ideas provides a powerful alternative to scoped variables for associating a set of variable fields together, enabling one to get around the fact that ideas, ideologies, etc. do not have their own scopes. Generally, when you target a token, it is pasted in as its underlying integer ID (a number in the ten-thousands, usually), but this generally works fine, because it's consistent; the only problem is it's not human-readable. In general, variable targeting is substantially more optimized than meta-effect/trigger token pasting, not to mention more readable and understandable, so should be preferred wherever feasible.

It is technically possible, under some circumstances, to use multiple target specifiers in one variable name, usually strung together back-to-back at the end of the name, like `var_name_@THIS_@PREV`. However, this is extremely inconsistent, and the exact rules that govern how it behaves are currently an open question.

### Operators

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

- **check_variable**
  - Parameters:
    ```text
    var = <variable>
    Variable to compare.
    value = <decimal>/<variable>
    The value to compare the variable to.
    compare = <compare type>/<variable>
    The comparison type. Variants are
    equals
    ,
    not_equals
    ,
    less_than
    ,
    less_than_or_equals
    ,
    greater_than
    , and
    greater_than_or_equals
    . Defaults to
    greater_than_or_equals
    .
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
    check_variable = { var_name > 10 }
    ```
  - Description: Compares the value of a variable. Used as a trigger.
  - Notes:
    ```text
    Temporary and regular formatting use the exact same formatting. Shortened variant exists as
    check_variable = { <variable> < <value> }
    , where the operator in the middle is an equality sign (=), greater than sign (>), or a lesser than sign (<). The comparison type is always strict in this case:
    check_variable = { var_name > 10 }
    will come up as false if
    var_name
    is exactly 10.
    ```

- **has_variable**
  - Parameters:
    ```text
    <variable>
    Variable to check.
    ```
  - Example:
    ```text
    has_variable = my_variable
    ```
  - Description: Checks if the value was set, regardless of its amount. Used as a trigger.
  - Notes: A variable is considered set even if its value is 0, as long as it wasn't cleared.

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

### Usage examples

A common usage for variables is to grant a more 'complex' effect or a trigger. This is best done with temporary variables, as they can be set in either triggers or effects and they're not bound to scopes making operations on them more simple.  
For example, the following can take 0.1% of every controlled state's population and add it directly to the manpower pool if the country has more democratic party support than fascist and communist party support combined:

```text
if = {
    limit = {
        set_temp_variable = { fascom_pop = party_popularity@fascism }
        add_to_temp_variable = { fascom_pop = party_popularity@communism }
        check_variable = { party_popularity@democratic > fascom_pop }   # Completely hidden from the player.
        
    }                                                                   # 'limit = {}' is always hidden so it doesn't matter here, but use custom_trigger_tooltip when wanting the player to be aware.
    hidden_effect = {   # Every controlled state can look weird to the player otherwise.
        set_temp_variable = { temp_manpower = 0 }   # Optional, can be omitted as variables are assumed to be 0 if unset.
        every_controlled_state = {
            add_to_temp_variable = { temp_manpower = state_population_k } # Executed in the state's scope, so state_population_k is of the state. 
        }                                                                 # Temp variables are unscoped so it doesn't matter where they're edited.
    }                                                                     # For regular varibles, "add_to_variable" would need to scope into the correct country such as with "PREV.temp_manpower".
    add_manpower = var:temp_manpower # 'add_manpower = temp_manpower' also works
}
```

Since temporary variables can be set in triggers, they can be used as an alternative version of [count\_triggers](<Triggers - Hearts of Iron 4 Wiki.md#count-triggers>), to count the amount of scopes where the trigger is fulfilled instead of counting the amount of fulfilled triggers:

```text
if = {
    limit = {
        all_country = { # all_-typed scopes iterate over each entity until encountering a false, making them preferred over any_-typed ones that will exit out at a true.
            if = {                              # Direct limiting is only supported in effect scopes.
                limit = {
                    has_country_flag = example_flag
                }
                add_to_temp_variable = { flag_counter = 1 } # Assumed to be zero if unset
            }
        }
        check_variable = { flag_counter > 9 }
    }
    country_event = example.0 # The event fires if at least 10 countries have the example_flag flag.
}
```

Additionally, it is common for a variable to be a counter of something within a mechanic. For example, let CAN\_beavers be a counter of beavers within the country.  
When using variables in this sense, **it is better to use [scripted effects](<Effect - Hearts of Iron 4 Wiki.md#scripted-effects>) to modify them**, in order to make changes to the variable easier. For example, a small gain in beavers could be the following:

```text
CAN_beavers_small_add = {
    custom_effect_tooltip = CAN_beavers_small_add_tt    # Tooltip for the player to be aware.
    add_to_variable = { CAN_beavers = 100 } # Adds 100 beavers.
}
```

However, if 100 seems like too little, the scripted effect can be changed and it'll immediately apply the changes every single time that scripted effect was used without needing to find them manually. These effects may also share a single 'recalculating' scripted effect in common. This can be used to clamp the variable between a minimum and a maximum, to have an instant effect as soon as some variable value is reached, or to have another variable 'tied' to the value to be kept at an exact or a dynamic ratio. For example, these scripted effects can be used with the same CAN\_beavers example:

```text
CAN_beavers_calibrate = {
    clamp_variable = {  # The variable will be kept between these levels by calling this each time the variable is changed.
        var = CAN_beavers
        min = 0
        max = 2000
    }
    
    set_variable = { CAN_beavers_modifier = CAN_beavers }
    divide_variable = { CAN_beavers_modifier = 1000 }   # Another variable tied to the base value, as long as the scripted effect is called upon each change of CAN_beavers.
    
    if = {
        limit = {
            check_variable = { CAN_beavers = 0 }
        }
        country_event = CAN_beavers_extinction.0    # The event gets fired as soon as CAN_beavers hits 0.
    }
}

CAN_beavers_small_add = {   # Same as before, but with calling the previous effect
    custom_effect_tooltip = CAN_beavers_small_add_tt
    add_to_variable = { CAN_beavers = 100 }
    CAN_beavers_calibrate = yes
}

CAN_beavers_small_remove = { # Another example of a variable-modifying effect
    custom_effect_tooltip = CAN_beavers_small_remove_tt
    add_to_variable = { CAN_beavers = -100 }    # 'subtract_from_variable = { CAN_beavers = 100 }' also works.
    CAN_beavers_calibrate = yes
}
```

After creating these scripted effects, these can be used within any effect block to modify the variable at will. [Showing its value in localisation to the player](#additional-usage) would also be helpful, such as within a [decision category](<Decision modding - Hearts of Iron 4 Wiki.md>) or in [scripted GUI](<Scripted GUI modding - Hearts of Iron 4 Wiki.md>). **Variables cannot be used within idea modifiers directly, [dynamic modifiers can be used instead.](<Modifiers - Hearts of Iron 4 Wiki.md#dynamic-modifiers>)**

Remember that variables are not necessarily used as numbers only. For example, the simplest way to make the current ideology group to change to the one that's the most popular (aside from the ruling party) would be a `set_politics = { ruling_party = highest_party_ideology@exclude_ruling_party }`. Similarly, some event target-type variables can be used to cut down on code, such as `transfer_state = GER.capital` immediately transferring the capital of GER to the current scope.

### MTTH variables

MTTH variables allow to dynamically create a [MTTH block](<AI modding - Hearts of Iron 4 Wiki.md#mtth-blocks>) to be used as a variable. These are stored within /Hearts of Iron IV/common/mtth/\*.txt files, where each MTTH variable is a separate block, the name of which gets taken as the MTTH variable.  
As per the name, the MTTH variables serve as a MTTH block, so everything that applies to MTTH blocks applies here: The starting base is defined with `factor` or `base` and then each `modifier = { ... }` begin a trigger block needed to be fulfilled for the `add` (for adding) or/and `factor` (for multiplying) within to be applied.
For example, the following is an example of a /Hearts of Iron IV/common/mtth/\*.txt file:

```text
my_mtth_variable_1 = {
    base = 10
    modifier = {
        factor = 10
        is_major = yes
    }
    modifier = {
        add = -10
        tag = FRA
    }
}
my_mtth_variable_2 = {
    base = other_variable
    factor = 0.5
    add = 10
}
```

This can be called the same way as a game variable, but somewhat differently: `set_variable = { my_var = mtth:my_mtth_variable_1 }`. This will check the MTTH block for the scope where it's checked and return the total result as a variable.

### Debugging variables

There are the following arguments that can be used in trigger or effect blocks:

- **log**
  - Parameters:
    ```text
    <string>
    What to write in the log.
    ```
  - Example:
    ```text
    log = "Current value of myVar in [THIS.GetName]: [?myVar]"
    ```
  - Description:
    ```text
    Creates an entry in the
    /Hearts of Iron IV/logs/game.log
    file in the
    user directory
    and, if console is open and debug mode is turned on, in console as well.
    ```
  - Notes: While it nominally has nothing to do with variables, its most common use is for variables.

- **print_variables**
  - Parameters:
    ```text
    file = <string>
    The name of the file, not counting the file extension. Defaults to "variable_dump".
    text = <string>
    What will be printed in the beginning of the file. Defaults to "No Header".
    append = yes
    If set, will append the current variables (and the text) to the end of the file instead of overwriting.
    print_global = yes
    If true, will print the variables from the global scope as well.
    var_list = { ... }
    A whitespace-separated list of variables the values of which should be printed. Optional: every variable in the scope (and global if set) if left out.
    ```
  - Example:
    ```text
    print_variables = {
        file = my_file
        text = "These variables are printed at [GetDateText]"
        append = yes
        print_global = yes
    }
    ```
  - Example:
    ```text
    print_variables = {
        file = my_file_2
        var_list = { temp1 temp2 temp3 }
    }
    ```
  - Description: Dumps the specified variables from the current scope and optionally the global scope into a log file with the specified name.
  - Notes:
    ```text
    The log will be within
    /Hearts of Iron IV/logs/variable_dumps/
    in the
    user directory
    .
    ```

Additionally, the following console commands exist for variables. In console commands, the 'current scope' is what is currently selected: the country opened in diplomacy, the state selected, the unit leader that's selected. If left out, assumes to be the player country.

- **set_var**
  - Parameters:
    ```text
    <variable>
    The variable to get the value of.
    <value>
    What to set the variable to.
    ```
  - Example:
    ```text
    set_var my_variable 10
    ```
  - Description: Changes the value of the variable within the specified scope.

- **get_var**
  - Parameters:
    ```text
    <variable>
    The variable to get the value of.
    ```
  - Example:
    ```text
    get_var my_variable
    ```
  - Description: Prints the value of the variable in console.

- **list_vars**
  - Parameters:
    ```text
    <scope>
    Optional. Changes the scope from the currently-selected scope to what's specified.
    ```
  - Example:
    ```text
    list_vars
    ```
  - Description: Lists the variables and their values as within the currently-selected scope.

### Token-valued variables

When one uses a literal of the form `token:some_tokenizable_value`, what is actually returned is an integer variable (commonly with a large value), with an internal flag set so that it is interpreted as an index into a central table of token strings that exists within the game's memory. This can be placed into a variable and passed around freely, it can be compared for equality to other token variables, and it can even be treated as a numeric in arithmetic even if usages for such cases are rare if nonexistent. Variables that have the token flag set can be distinguished in the output of the `list_vars` console command by dint of being automatically translated into their underlying raw-token strings. For example, `some_var_name = token:some_tokenizable_value (27012)`.

When the variable contains a token value, it is possible to use the `GetTokenKey` [localisation function](<Localisation - Hearts of Iron 4 Wiki.md#functions>) (such as `[?some_var_with_token_value.GetTokenKey]`) to get the token string value of the variable, `token:` prefix not included. This is useful for pasting in [meta-effects](<Effect - Hearts of Iron 4 Wiki.md#meta-effects>) and meta-triggers, however note that the `token:` prefix is still required if using it within the `set_(temp_)variable` operator. With some token-valued variables (specifically, those backed by named database objects of a tokenizable datatype), it is possible to use `GetTokenLocalizedKey` to retrieve the value of the localisation key with the same name as the token itself. This can be used to produce and/or define human-readable names, but it can also be taken advantage of to pass around arbitrary localisation values.

At present (1.12), known tokenizable datatypes include (but are probably not limited to):

- Ideas: These are generally the most flexible tokenizable datatype to use for a token that represents some arbitrary value by using a dummy idea. They can also carry an effectual payload in their `on_add` clauses, which can be used to pass around effects, or better yet, to return a set of variables encoding information relevant to the token value.
- Everything listed in /Hearts of Iron IV/common/script\_enums.txt
- Ideologies/Ideology groups
- Technologies
- Equipment types - Sometimes this is a bit inconsistent with regards to the archetype/non-archetype distinction, so be wary.
- Operations
- Characters/Unit leaders: These are finicky in the game's core. When a character is promoted to a unit leader position, all tokenizations of that character's token will begin to return a different value, representing the token for the unit leader with the same identifier, which is linked to, but not the same as, the original character. The unit leader version of the token returns the same `GetTokenKey` and `GetTokenLocalizedKey`, but it is *not numerically equal to the character version of the token.* This can come into play if code compares the equality of two character-pointing variables.
- Decisions
- Buildings

### Advanced use of tokens

Using tokenizable values in variables is the key to a number of advanced techniques that enable relatively seamless abstraction and metaprogramming, with a minimum of scripted-localisation boilerplate code. These techniques are, however, difficult to learn how to apply and can be unintuitive for those not already experienced. Therefore, caution is advised.

It is often useful to define related dummy tokenizable database entries, especially ideas, to represent arbitrary (possibly enumerable) custom datatypes. In most cases, ideas are preferable, however there can be uses for other token types, such as technologies if the code is to implement something that can't be done with a regular idea. The reason for idea preference is little to no downstream effects simply from existing, ease to define in bulk with minimal syntactic overhead, and ease to separate different custom datatypes by using custom idea categories and by placing the definitions for different custom datatypes in different files within /Hearts of Iron IV/common/ideas/. Decisions or technologies are common alternatives for custom datatypes with different usages, but generally datatypes other than these have too much downstream baggage (i.e. their very existence has consequences elsewhere, such as custom building types appearing automatically in certain UIs) to be worth using for dummy values.

Using a systematic naming scheme, custom tokenizable datatypes can also convey multiple related localisation keys, similarly to the approach that the base game does for country naming with separate `TAG`, `TAG_DEF`, and `TAG_ADJ` keys. An example of that would be creating an idea `foo_bar` to act as the key identifier of the custom data value, whose localisation value carries the human-readable name of the data value, and another idea `foo_bar_description` (**NOT `foo_bar_desc`, this collides with the localisation key generated for `foo_bar`**) to carry the localisation value for the description that would be associated with the data value identified by `foo_bar`. This description localisation can be accessed with a meta-effect or meta-trigger (including in scripted localisation), such as `set_temp_variable = { description_var = token:[IDEA_TOKEN]_description }` (where `IDEA_TOKEN = "[?idea_var_name.GetTokenKey]"`). This allows accessing `[?description_var.GetTokenLocalizedKey]` in localisation where `description_var` is visible, such as the `localization_key` following the scripted localisation `trigger` block where the pasting meta-trigger is called.

As far more advanced usage, it is possible to rig up the dummy tokenizable values with arbitrary localisation payloads that carry fragments of Clausewitz code which can then be pasted together in meta-effects (or triggers) to approximate true token string manipulation or at least concatenation, as there's presently no way to split strings, token or otherwise. This is probably most useful for encoding a set of suffixes that can be applied to an idea token to dynamically navigate within the custom datatype's naming scheme. For example, if the mod has a custom datatype representing positions within a government such as the Secretary of State and the Attorney General, such that it might have a base idea `position_attorney_general`, a corresponding description idea (suffixed with `_description`), a singular name idea (suffixed with `_singular`, carrying the name of the data value in singular form, like "Attorney General"), and a plural name idea (suffixed with `_plural`, carrying the name in plural form, like "Attorneys General"), it is possible to select which name to use by having a dummy idea called `enum_position_name_singular` with the localisation value `"_singular"`, and another called `enum_position_name_plural` with the localisation value `"_plural"`. After that, the mod may pass one of the `enum_position` ideas in a variable and then paste its `GetTokenLocalizedKey` after the `GetTokenKey` of the base idea in a meta-effect/trigger to produce either `token:position_attorney_general_singular` or `token:position_attorney_general_plural`. This is a contrived example, and is also possible to be done using a scripted localisation system with hard-coded entries to access the singular vs. plural ideas, but this approach has far more use in more complex systems where creating a scripted localisation file can prove to be far too bulky.

From 1.12 onwards, anything defined in /Hearts of Iron IV/common/script\_enums.txt can be freely tokenized, even if defined in a totally custom enumeration block, seperate from the ones hard-coded into the game. It is therefore theoretically possible to define arbitrary tokens of a custom enum type in this file. However, for compatibility reasons, using `script_enums` for custom enumeration types should be avoided, as this will ensure that the mod will not be compatible with any other mod that overwrites that file, no matter which mod gets priority on the file. As before, it's preferable to have a custom idea category with a set of dummy ideas in their own file that will not be overridden by other mods representing the values the custom enum can take on. This pattern is a useful replacement for passing around arbitrary integers that have some enumerable meaning when interpreted by code, especially if those integers are interpreted to yield names in scripted localisation, in which case this pattern can substantially remove the need for scripted localisation boilerplate by allowing defining the localised name for each enum member directly in a localisation file, as similarly to defining the localised name for an idea.

Technically, any raw token used in the language can actually be tokenized: for instance, `token:set_stability` (that is, a token literal of the name of the [set\_stability effect](<Effect - Hearts of Iron 4 Wiki.md#mana>)) is perfectly valid, and yields a token for which `GetTokenKey` and `GetTokenLocalizedKey` both return `set_stability`. However, this is rarely useful (especially since it does not apply to scripted effect and trigger names), and arguably counts as a bug; it mostly just provides an interesting peek into the internals of the tokenization system, indicating that it most likely delegates to a pre-existing string de-duplication system built into the Clausewitz engine.

## Modifier tokens

*This section is transposed from [Modifiers § Modifier definitions](<Modifiers - Hearts of Iron 4 Wiki.md#modifier-tokens>)*

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

## Arrays

Arrays are similar to variables, but they instead store a collection of variables.  
An array in the game is structured with indexes starting from 0. `arrayname^0` as a variable refers to the first item of `arrayname`, `arrayname^1` refers to the second item in the array, and so on. In order to obtain the total amount of items within the given array, `arrayname^num` is used. An array is assumed to have no elements by default, if not already created, with [add\_to\_array or add\_to\_temp\_array](#add-to-array) usually being used to create an array.

Temporary and regular arrays exist, with the same distinction between them as in variables: temp arrays can be set and modified in triggers and effects, are unscoped, and cleared after the effect/trigger block ends; regular arrays can only be set or modified in effects, are linked to a specific scope, and persist forever until cleared manually.

A single element of an array is considered a variable in every regard: `set_variable = { arrayname^0 = 10 }` will set the first element to be equal to 10 (with `set_temp_variable` used for temporary arrays), `check_variable = { arrayname^0 > 10 }` is also valid syntax, and `[?arrayname^0]` will print the value of the element in localisation. However, the element must already exist for it to be edited. **There is no simple way to print an entire array in localisation**, however a recursive scripted localisation can be used, which modifies the value of a temporary variable by one until hitting the array's size each time that it's used.

### Arguments

The following arguments exist for arrays. Similarly to variables, temporary versions exist by replacing `array` with `temp_array`.

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

Meanwhile, the following triggers exist that are array-related. As with variables, these are the exact same for temporary and regular variables.

- **is_in_array**
  - Parameters:
    ```text
    array = <array>
    The array to check.
    value = <decimal>/<variable>
    The value to check for.
    ```
  - Example:
    ```text
    is_in_array = {
        array = global.my_countries
        value = THIS.id
    }
    ```
  - Example:
    ```text
    is_in_array = { temp_states = THIS }
    ```
  - Description: Checks if any value within the array is the same as the specified value.
  - Notes:
    ```text
    Shortened version exists with
    is_in_array = { <array> = <value> }
    .
    ```

- **any_of**
  - Parameters:
    ```text
    array = <array>
    The array to check.
    value = <variable>
    The name of the temporary variable where the value of the currently-selected element is stored.
    index = <variable>
    The name of the temporary variable where the index of the currently-selected element is stored.
    <triggers>
    An AND trigger block.
    ```
  - Example:
    ```text
    any_of = {
        array = temp_numbers
        value = v
        index = i
        multiply_temp_variable = { v = i }
        check_variable = { v > political_power }     # Checks if the value multiplied by the index is larger than the political power of the country this is checked in.
    }
    ```
  - Description: Checks if any value within the array fulfills the triggers, halting and returning true if that's the case.
  - Notes:
    ```text
    The scope does not change from the one this is checked in by default, requiring one of
    scopes
    .
    ```

- **any_of_scopes**
  - Parameters:
    ```text
    array = <array>
    The array to check.
    tooltip = <localisation key>
    The localisation key used for the trigger.
    <triggers>
    An AND trigger block.
    ```
  - Example:
    ```text
    any_of_scopes = {
        array = global.majors
        tooltip = has_more_states_than_any_other_major_tt
        NOT = { tag = PREV }
        check_variable = { num_owned_controlled_states > PREV.num_owned_controlled_states }
    }
    ```
  - Description: Checks if any value within the array fulfills the triggers, halting and returning true if that's the case, scoping into each element in the array.
  - Notes:
    ```text
    Appending
    _NOT
    to the tooltip's key (such as has_more_states_than_any_other_major_tt_NOT in the example) results in the localisation key used if this any_of_scopes is put inside of
    NOT = { ... }
    . Since this changes scopes,
    PREV
    would, unless there's deeper scoping, refer to the scope this trigger is checked in.
    ```

- **all_of**
  - Parameters:
    ```text
    array = <array>
    The array to check.
    value = <variable>
    The name of the temporary variable where the value of the currently-selected element is stored.
    index = <variable>
    The name of the temporary variable where the index of the currently-selected element is stored.
    <triggers>
    An AND trigger block.
    ```
  - Example:
    ```text
    all_of = {
        array = temp_numbers
        value = v
        index = i
        multiply_temp_variable = { v = i }
        check_variable = { v > political_power }     # Checks if the value multiplied by the index is larger than the political power of the country this is checked in.
    }
    ```
  - Description: Checks if every value within the array fulfills the triggers, halting and returning false if any one doesn't.
  - Notes:
    ```text
    The scope does not change from the one this is checked in by default, requiring one of
    scopes
    .
    ```

- **all_of_scopes**
  - Parameters:
    ```text
    array = <array>
    The array to check.
    tooltip = <localisation key>
    The localisation key used for the trigger.
    <triggers>
    An AND trigger block.
    ```
  - Example:
    ```text
    all_of_scopes = {
        array = global.majors
        tooltip = has_more_states_than_every_other_major_tt
        OR = { 
            tag = PREV
            check_variable = { num_owned_controlled_states < PREV.num_owned_controlled_states }
        }
    }
    ```
  - Description: Checks if every value within the array fulfills the triggers, halting and returning false if any one doesn't, scoping into each element in the array.
  - Notes:
    ```text
    Appending
    _NOT
    to the tooltip's key (such as has_more_states_than_every_other_major_tt_NOT in the example) results in the localisation key used if this any_of_scopes is put inside of
    NOT = { ... }
    . Since this changes scopes,
    PREV
    would, unless there's deeper scoping, refer to the scope this trigger is checked in.
    ```

The following effects also exist in addition used, with arrays. While some are nominally unrelated to arrays, they are often used in conjunction.

- **for_each_loop**
  - Parameters:
    ```text
    array = <array>
    The array to check.
    value = <variable>
    The name of the temporary variable where the value of the currently-selected element is stored.
    index = <variable>
    The name of the temporary variable where the index of the currently-selected element is stored.
    break = <variable>
    The temporary variable that can be set to be not 0 to instantly break the loop.
    <effects>
    An effect block.
    ```
  - Example:
    ```text
    for_each_loop = {
        array = temp_numbers
        value = v
        break = break
        random_list = {
            10 = { add_political_power = v }
            10 = {
                divide_temp_variable = { v = 100 }
                add_stability = v
            }
            10 = {
                divide_temp_variable = { v = 100 }
                add_war_support = v
            }
        }
    }
    ```
  - Description: Runs an effect once for every element in the array.
  - Notes:
    ```text
    The scope does not change from the one this is checked in by default, requiring one of
    scopes
    . You cannot remove any elements in the array with the effects block whilst the loop is running.
    ```

- **for_each_scope_loop**
  - Parameters:
    ```text
    array = <array>
    The array to check.
    break = <variable>
    The temporary variable that can be set to be not 0 to instantly break the loop.
    <effects>
    An effect block.
    ```
  - Example:
    ```text
    for_each_scope_loop = {
        array = global.majors
        if = {
            limit = {
                NOT = { tag = PREV } # Not the country where the for_each_scope_loop is executed
            }
            random_owned_controlled_state = {
                transfer_state_to = PREV.PREV
            }
        }
    }
    ```
  - Description: Runs the effects for every scope within the array.
  - Notes:
    ```text
    Equivalent to a
    every_<...>
    effect scope type, with additional
    break
    . Since this changes scopes,
    PREV
    would, unless there's deeper scoping, refer to the scope the effect is executed in.
    ```

- **random_scope_in_array**
  - Parameters:
    ```text
    array = <array>
    The array to check.
    break = <variable>
    The temporary variable that can be set to be not 0 to instantly break the loop.
    limit = { <triggers> }
    An AND trigger block deciding which scopes can be picked.
    <effects>
    An effect block.
    ```
  - Example:
    ```text
    random_scope_in_array = {
        array = global.countries
        break = break
        limit = {
            is_dynamic_country = no
            exists = no
            any_state = {
                is_core_of = PREV   # Is core of the currently-checked country
            }
        }
        random_core_state = {
            transfer_state_to = PREV    # Transfers to the currently-selected country.
        }
    }
    ```
  - Description: Runs the effects for a random scope within the array.
  - Notes:
    ```text
    Equivalent to a
    random_<...>
    effect scope type, with additional
    break
    . Since this changes scopes,
    PREV
    would, unless there's deeper scoping, refer to the scope this effect is executed in.
    ```

- **while_loop_effect**
  - Parameters:
    ```text
    limit = { <triggers> }
    An AND trigger block deciding when the effect would repeat.
    break = <variable>
    The temporary variable that can be set to be not 0 to instantly break the loop.
    <effects>
    An effect block.
    ```
  - Example:
    ```text
    while_loop_effect = {
        limit = {
            any_country = {
                num_owned_controlled_states > 10
            }
        }
        random_country = {
            limit = {
                num_owned_controlled_states > 10
            }
            random_other_country = {
                limit = {
                    num_owned_controlled_states < 10
                }
                PREV = {
                    random_owned_controlled_state = {
                        transfer_state_to = PREV.PREV
                    }
                }
            }
        }
    }
    ```
  - Description: Runs the effects as long as the limit is fulfilled.
  - Notes:
    ```text
    The limit is only checked at the beginning and once the effect block is executed. Can't run for more than 1000 times by default
    .
    ```

- **for_loop_effect**
  - Parameters:
    ```text
    start = <decimal>/<variable>
    The value at which the evaluation starts. Default to 0.
    end = <decimal>/<variable>
    The value at which the evaluation ends. Default to 0.
    compare = <compare type>
    How the currently-evaluated value must compare with the
    end
    for the for loop to continue. Defaults to
    less_than
    , leading to the end value never being picked.
    add = <variable>
    How much is being added to the
    start
    value for every iteration. Defaults to 1.
    break = <variable>
    The temporary variable that can be set to be not 0 to instantly break the loop.
    value = <variable>
    The name of the temporary variable where the current value of evaluation is stored.
    <effects>
    An effect block.
    ```
  - Example:
    ```text
    for_loop_effect = {
        end = 4
        value = temp
        if = {
            limit = {
                NOT = {
                    count_triggers = {
                        amount = 2
                        check_variable = { temparr^temp < temparr^0 }
                        check_variable = { temparr^temp < temparr^1 }
                        check_variable = { temparr^temp < temparr^2 }
                        check_variable = { temparr^temp < temparr^3 }
                    }
                }
            }
            add_to_array = { potential_max = temp }
        }
    }
    ```
  - Description: Runs the effects as long as the limit is fulfilled.
  - Notes:
    ```text
    The limit is only checked at the beginning and once the effect block is executed. Can't run for more than 1000 times by default
    . Comparison types are the same as used in
    check_variable
    .
    ```

### Scorers

Scorers are defined within /Hearts of Iron IV/common/scorers/country/\*.txt files, serving as a sorted list of targeted countries, based on how well they did in the specified [MTTH block](<AI modding - Hearts of Iron 4 Wiki.md#mtth-block>). The scorer has the primary country which the scorer is used for and targeted countries.

Each scorer is a separate block within the file, with the name of the block being the name of the scorer. The scorer then has the `targets = { ... }` block that encompasses everything else about the scorer.

Scorers target countries similarly to [targeted decisions](<Decision modding - Hearts of Iron 4 Wiki.md#targeted-decisions>) but with differences, with the following arguments being used within of `targets = { ... }`:

As with targetted decisions, [FROM](<Scopes - Hearts of Iron 4 Wiki.md>) is the scope of the country being targeted by the scorer, while ROOT is the scope of the country invoking the scorer.

Scorers do not seem to hotreload very reliably. But, assuming you're changing an existing file rather than making a brand new one, edits to a scorer are reflected if you quit to main menu and then re-enter the game.

- `targets = { TAG, TAG }` - A list of country tags, including other [dual scopes](<Scopes - Hearts of Iron 4 Wiki.md#dual-scopes>) such as [overlord](<Scopes - Hearts of Iron 4 Wiki.md#overlord>), that can be targeted by this scorer. Unlike targeted decisions, this seems to be comma-separated.
- `target_array = global.majors` - The array to target. The default scope is the primary country.
- `target_root_trigger = { ... }` - The trigger block which the primary country must fulfill for the target to work. In here, ROOT (default scope) is the country running the scorer.
  - It's not clear if there's any difference between `target_root_trigger` and `target_trigger` except that `target_root_trigger` is presumably only run once when invoking a scorer, and FROM cannot be used within it.
- `target_trigger = { ... }` - The trigger block that target country must fulfill for the target to work. In here, ROOT (default scope) is the country running the scorer and FROM is the potential target of the scorer.
- `targets_dynamic = yes` - If set, makes the dynamic countries possible targets. Defaults to no.
- `target_non_existing = yes` - If set, makes non-existing countries possible targets. Defaults to no.
- `score = { ... }` - This is the MTTH block itself that ranks the countries in the list. By default, THIS (the default scope) is the target, FROM is the primary country initialising the check.

For example, the following is a scorer that sorts every major country depending on the amount of states they own:

```text
asian_countries_owned_states_scorer = {
	majors_owned_states = {
		targets = {
			target_array = global.countries
			target_trigger = {
				FROM = {
					capital_scope = {
						is_on_continent = asia
					}
				}
			}
			score = {
				modifier = {
					add = num_owned_states
				}
			}
		}
	}
}
```

After defining a scorer, there is the way to use it: an argument, similar to arrays and variables. Similarly to them, regular and temporary versions exist, which decides whether the variable/array it's writing to is regular or temporary. Both can only be used inside of country scope. Regular versions can only be used in effects, and temporary versions can be used in effects and triggers.

- **get_highest_scored_country**
  - Parameters:
    ```text
    scorer = <scorer>
    The scorer to use.
    var = <variable>
    The variable where the result will be stored.
    ```
  - Example:
    ```text
    get_highest_scored_country = {
        scorer = asian_countries_owned_states_scorer
        var = largest_asian_country
    }
    ```
  - Example:
    ```text
    get_highest_scored_country_temp = {
        scorer = asian_countries_owned_states_scorer
        var = largest_asian_country
    }
    ```
  - Description: Sets the specified variable to be the highest-scoring country within the scorer, as checked for the country where this is used.

- **get_sorted_scored_countries**
  - Parameters:
    ```text
    scorer = <scorer>
    The scorer to use.
    array = <variable>
    The array where the countries will be stored.
    scores = <variable>
    The array where the scores will be stored. Optional.
    ```
  - Example:
    ```text
    get_sorted_scored_countries = {
        scorer = asian_countries_owned_states_scorer
        array = asian_countries_by_size
        scores = asian_country_size_scores
    }
    ```
  - Example:
    ```text
    get_sorted_scored_countries_temp = {
        scorer = asian_countries_owned_states_scorer
        array = asian_countries_by_size
        scores = asian_country_size_scores
    }
    ```
  - Description: Creates two arrays of countries and their corresponding values, sorted in the ascending order.
  - Notes:
    ```text
    Values with the same index are connected: in the example,
    asian_countries_by_size^0
    is the country that got
    asian_countries_scores^0
    points in the
    majors_owned_states
    scorer.
    ```

#### Example

Scorers can be helpful to create a sorted list of scopes by a certain element, such as political power. For example, the following can be used to find the countries with the most infantry equipment.

Within the scorer file:

```text
infantry_equipment_scorer = {
	targets = {
		target_array = global.countries
		targets_dynamic = yes
		score = {
		    modifier = {
		    	add = num_equipment@infantry_equipment
		    }
		}
	}
}
```

Within an effect block:

```text
ROOT = {
	get_sorted_scored_countries_temp = {
		scorer = infantry_equipment_scorer
		array = scored_array
		scores = scored_values
	}

	for_loop_effect = {
		end = scored_array^num
		value = s
		log = "[?scored_array^s.GetName] had inf equipment [?scored_values^s]"
	}
}
```

## Game variables

Game variables are read-only variables that are used to read certain aspects of the game, such as the current political power that the player has. These cannot be modified using any variable-modifying argument, but they can serve as the value within them (such as `add_to_temp_variable = { temp = GER.army_experience }` adding the amount of army experience that GER has to the `temp` temporary variable). Some are targeted, requiring one more argument in the target's place. For example, `modifier` has a modifier token as the target, so it would be used as `set_temp_variable = { temp = modifier@consumer_goods_factor }`, where `consumer_goods_factor` is the name of the modifier used as the argument.

Remember that to get global-scoped game variables, it is necessary to scope into global as `global.year` rather than leaving out the scope. A list of game variables can be found within /Hearts of Iron IV/documentation/dynamic\_variables\_documentation. A large portion of purely numeric [Triggers](<Triggers - Hearts of Iron 4 Wiki.md>) also have corresponding game variables that are not mentioned in the documentation. The following game variables exist in the game (Some duplicates are omitted):

- **year**
  - Target: None.
  - Description/Notes: The current year, such as 1936.

- **date**
  - Target: None.
  - Description/Notes:
    ```text
    The ID of the current date. This can be localised in
    a multitude of different ways
    , using the localisation functions beginning with
    GetDateString
    . This variable functions by having one game hour be 0.00001, with 0 of the variable corresponding to the date 1st January -5000, 1:00.
    ```

- **num_days**
  - Target: None.
  - Description/Notes: The amount of days passed since the start of year 0. The value on the 1st of January 1936 is 706640.

- **difficulty**
  - Target: None.
  - Description/Notes: The current difficulty value on the scale from 0 (For Civilian) to 4 (For Elite).

- **threat**
  - Target: None.
  - Description/Notes: The current world tension value on the scale from 0 to 1.

- **pc_turn**
  - Target: None.
  - Description/Notes: The turn in the currently-ongoing peace conference.

- **power_balance_value**
  - Target:
    ```text
    BoP, such as
    @ITA_power_balance
    ```
  - Description/Notes: The current value of the balance of power on the scale from -1 to 1.

- **power_balance_daily_change**
  - Target:
    ```text
    BoP, such as
    @ITA_power_balance
    ```
  - Description/Notes: The current daily change in the value of the balance of power.

- **power_balance_weekly_change**
  - Target:
    ```text
    BoP, such as
    @ITA_power_balance
    ```
  - Description/Notes: The current weekly change in the value of the balance of power.

- **num_of_career_profile_points**
  - Description/Notes: Check amount of gained career points.

- **modifier**
  - Target:
    ```text
    Modifier's name, such as
    @political_power_gain
    .
    ```
  - Description/Notes:
    ```text
    The total value of the current
    modifier
    as the country has in total. Targeted modifiers have separate definitions.
    ```

- **id**
  - Target: None.
  - Description/Notes:
    ```text
    The internal ID of the country. Equivalent to not specifying anything, like
    set_temp_variable = { temp = TAG }
    .
    ```

- **max_manpower**
  - Target: None.
  - Description/Notes:
    ```text
    Total population of the country. Deprecated, recommended to use
    max_manpower_k
    instead as to push the necessary number for an overflow to ~2 billion from the very possible ~2 million.
    ```

- **max_manpower_k**
  - Target: None.
  - Description/Notes: Total population of the country in thousands.

- **party_popularity**
  - Target:
    ```text
    Ideology group or
    ruling_party
    , such as
    @ruling_party
    .
    ```
  - Description/Notes: The popularity of the specified political party in the range from 0 to 1.

- **party_popularity_100**
  - Target:
    ```text
    Ideology group or
    ruling_party
    , such as
    @neutrality
    .
    ```
  - Description/Notes: The popularity of the specified political party in the range from 0 to 100.

- **highest_party_ideology**
  - Target:
    ```text
    exclude_ruling_party
    or nothing.
    ```
  - Description/Notes: The ideology group that has the highest party popularity within the country, optionally excluding the ruling party.

- **highest_party_popularity**
  - Target:
    ```text
    exclude_ruling_party
    or nothing.
    ```
  - Description/Notes: The popularity of the ideology group that has the highest party popularity within the country, optionally excluding the ruling party. The popularity is on the scale from 0 to 1.

- **current_party_ideology_group**
  - Target: None.
  - Description/Notes: Ideology group that the country currently has.

- **original_tag**
  - Target: None.
  - Description/Notes: The tag from which the current country originates. Same as the regular tag for non-dynamic countries.

- **opinion**
  - Target: Country.
  - Description/Notes: The opinion of the current country towards the specified one.

- **days_decision_timeout**
  - Target:
    ```text
    Decision, such as
    @my_decision
    .
    ```
  - Description/Notes: The remaining amount of days for a completed decision before it gets removed.

- **days_mission_timeout**
  - Target: Mission.
  - Description/Notes: The remaining amount of days for an ongoing mission before it times out.

- **political_power**
  - Target: None.
  - Description/Notes:
    ```text
    Total current political power of the country.
    has_political_power
    can be used in the same way.
    ```

- **political_power_daily**
  - Target: None.
  - Description/Notes:
    ```text
    Current amount of daily gain of political power, equivalent to
    political_power_growth
    .
    ```

- **stability**
  - Target: None.
  - Description/Notes:
    ```text
    Current stability of the country on the scale from 0 to 1.
    has_stability
    can be used in the same way.
    ```

- **has_war_support**
  - Target: None.
  - Description/Notes: Current war support of the country on the scale from 0 to 1.

- **has_casualties_war_support**
  - Target: None.
  - Description/Notes: The malus from casualties towards war support on the scale from 0 to 1.

- **has_convoys_war_support**
  - Target: None.
  - Description/Notes: The malus from sunk convoys towards war support on the scale from 0 to 1.

- **has_bombing_war_support**
  - Target: None.
  - Description/Notes: The malus from bombing towards war support on the scale from 0 to 1.

- **power_balance_value**
  - Target: None.
  - Description/Notes: The current power balance value.

- **power_balance_daily**
  - Target: None.
  - Description/Notes: The current daily change in power balance.

- **power_balance_weekly**
  - Target: None.
  - Description/Notes: The current weekly change in power balance.

- **capital**
  - Target: None.
  - Description/Notes: The capital state of the country.

- **autonomy_ratio**
  - Target: None.
  - Description/Notes:
    ```text
    How close the country is to taking the next autonomy level. 0 if can be downgraded, 1 if can be upgraded, -1 if independent.
    compare_autonomy_progress_ratio
    can be used in a similar way.
    ```

- **overlord**
  - Target: None.
  - Description/Notes: The country that the current country is a subject of.

- **num_subjects**
  - Target: None.
  - Description/Notes: The number of subjects that the country has as an overlord.

- **core_compliance**
  - Target: Country.
  - Description/Notes: Average compliance within cores of the target country occupied by the current country.

- **core_resistance**
  - Target: Country.
  - Description/Notes: Average resistance within cores of the target country occupied by the current country.

- **has_collaboration**
  - Target: Country.
  - Description/Notes: The collaboration of the target country with the current country within target's cores currently occupied by the current country.

- **faction_leader**
  - Target: None.
  - Description/Notes: The leader of the faction the current country is in. Returns nothing if not in a faction.

- **country_leader**
  - Target: None.
  - Description/Notes: The leader of the current country.

- **num_faction_members**
  - Target: None.
  - Description/Notes: The number of members in the faction with the current country.

- **fuel_k**
  - Target: None.
  - Description/Notes: Current fuel of country in thousands.

- **max_fuel_k**
  - Target: None.
  - Description/Notes: Maximum fuel of country in thousands.

- **fuel_ratio**
  - Target: None.
  - Description/Notes: Ratio of the current fuel compared to the maximum amount, from 0 to 1.

- **host**
  - Target: None.
  - Description/Notes: The host of the current country. Returns nothing if not exiled.

- **legitimacy**
  - Target: None.
  - Description/Notes: The legitimacy of the currently-exiled country. Returns -1 if not exiled.

- **num_controlled_states**
  - Target: None.
  - Description/Notes: The amount of states that are controlled but not necessarily owned by the current country.

- **num_core_states**
  - Target: None.
  - Description/Notes: The amount of states that are national territory of the current country.

- **num_owned_controlled_states**
  - Target: None.
  - Description/Notes: The amount of states that are owned and controlled by the current country.

- **num_owned_states**
  - Target: None.
  - Description/Notes: The amount of states that are owned but not necessarily controlled by the current country.

- **num_occupied_states**
  - Target: None.
  - Description/Notes: The number of states occupied by the country.

- **resource**
  - Target:
    ```text
    Resource, such as
    @steel
    .
    ```
  - Description/Notes: The amount of surplus resource of the specified type, which isn't exported or used in production.

- **resource_consumed**
  - Target:
    ```text
    Resource, such as
    @aluminium
    .
    ```
  - Description/Notes: The amount of resource of the specified type currently used for equipment production.

- **resource_exported**
  - Target:
    ```text
    Resource, such as
    @oil
    .
    ```
  - Description/Notes:
    ```text
    The amount of resource of the specified type currently set to be exported with the
    min_export modifier
    .
    ```

- **resource_imported**
  - Target:
    ```text
    Resource, such as
    @tungsten
    .
    ```
  - Description/Notes: The amount of resource of the specified type currently set to be imported from trade with other countries.

- **resource_produced**
  - Target:
    ```text
    Resource, such as
    @rubber
    .
    ```
  - Description/Notes: The amount of resource of the specified type produced from the country's controlled states, buildings on them, and resource rights.

- **alliance_strength_ratio**
  - Target: Country.
  - Description/Notes: The ratio of land strength between the current country's faction and the target's faction.

- **alliance_naval_strength_ratio**
  - Target: Country.
  - Description/Notes: The ratio of naval strength between the current country's faction and the target's faction.

- **enemies_naval_strength_ratio**
  - Target: None.
  - Description/Notes: The estimated navy strength between the current country and all its enemies.

- **enemies_strength_ratio**
  - Target: None.
  - Description/Notes: The estimated army strength between the current country and all its enemies.

- **amount_research_slots**
  - Target: None.
  - Description/Notes: The current amount of research slots the country has.

- **original_research_slots**
  - Target: None.
  - Description/Notes:
    ```text
    The amount of research slots that the country had in the beginning of the game, as set in the
    history file
    .
    ```

- **any_war_score**
  - Target: None.
  - Description/Notes: The highest war score that the country has among wars it's in, on the scale from 0 to 100.

- **casualties**
  - Target: None.
  - Description/Notes: The amount of casualties a country has suffered in all of its wars.

- **casualties_k**
  - Target: None.
  - Description/Notes: The amount of casualties a country has suffered in all of its wars in thousands.

- **days_since_capitulated**
  - Target: None.
  - Description/Notes: The amount of days since the country has capitulated. If the country has never capitulated, returns 2147483.

- **convoy_threat**
  - Target: None.
  - Description/Notes: Returns, in the range from 0 to 1, the current danger that enemy convoys pose to the current country. Uses NDefines.NNavy.NAVAL_CONVOY_DANGER_RATIOS as the baseline.

- **mine_threat**
  - Target: None.
  - Description/Notes: Returns, in the range from 0 to 1, the current danger that enemy mines pose to the current country. Uses NDefines.NNavy.NAVAL_MINE_DANGER_RATIOS as the baseline.

- **foreign_manpower**
  - Target: None.
  - Description/Notes: The amount of foreign garrison manpower that the country has.

- **garrison_manpower_need**
  - Target: None.
  - Description/Notes: The amount of manpower needed by garrisons.

- **has_added_tension_amount**
  - Target: None.
  - Description/Notes: The amount of world tension currently added by the country.

- **manpower_per_military_factory**
  - Target: None.
  - Description/Notes: The amount of manpower that the country has for each military factory.

- **num_of_available_civilian_factories**
  - Target: None.
  - Description/Notes: Amount of available civilian factories.

- **num_of_available_military_factories**
  - Target: None.
  - Description/Notes: Amount of available military factories.

- **num_of_available_naval_factories**
  - Target: None.
  - Description/Notes: Amount of available naval factories.

- **num_of_civilian_factories**
  - Target: None.
  - Description/Notes: Amount of civilian factories.

- **num_of_civilian_factories_available_for_projects**
  - Target: None.
  - Description/Notes: Amount of civilian factories available for a new project to use.

- **total_constructed_<building>**
  - Target: None.
  - Description/Notes:
    ```text
    Amount of buildings of a certain type that have been constructed after the game's start by the country. The following options exist:
    Name
    Notes
    total_constructed_civilian_factory
    total_constructed_infrastructure
    total_constructed_military_factory
    total_constructed_dockyard
    total_constructed_port
    total_constructed_air_base
    total_constructed_rocket_site
    total_constructed_radar
    total_constructed_anti_air
    total_constructed_refinery
    total_constructed_fuel_silo
    total_constructed_supply_node
    total_constructed_nuclear_reactor
    total_constructed_land_fort
    total_constructed_naval_fort
    total_constructed_other
    ```
  - Column 4: Name
  - Column 5: Notes
  - Column 6: total_constructed_civilian_factory
  - Column 8: total_constructed_infrastructure
  - Column 10: total_constructed_military_factory
  - Column 12: total_constructed_dockyard
  - Column 14: total_constructed_port
  - Column 16: total_constructed_air_base
  - Column 18: total_constructed_rocket_site
  - Column 20: total_constructed_radar
  - Column 22: total_constructed_anti_air
  - Column 24: total_constructed_refinery
  - Column 26: total_constructed_fuel_silo
  - Column 28: total_constructed_supply_node
  - Column 30: total_constructed_nuclear_reactor
  - Column 32: total_constructed_land_fort
  - Column 34: total_constructed_naval_fort
  - Column 36: total_constructed_other

- **Name**
  - Target: Notes

- **total_constructed_civilian_factory**

- **total_constructed_infrastructure**

- **total_constructed_military_factory**

- **total_constructed_dockyard**

- **total_constructed_port**

- **total_constructed_air_base**

- **total_constructed_rocket_site**

- **total_constructed_radar**

- **total_constructed_anti_air**

- **total_constructed_refinery**

- **total_constructed_fuel_silo**

- **total_constructed_supply_node**

- **total_constructed_nuclear_reactor**

- **total_constructed_land_fort**

- **total_constructed_naval_fort**

- **total_constructed_other**

- **num_of_factories**
  - Target: None.
  - Description/Notes: Amount of total factories.

- **num_of_military_factories**
  - Target: None.
  - Description/Notes: Amount of military factories.

- **num_of_naval_factories**
  - Target: None.
  - Description/Notes: Amount of naval factories.

- **num_of_controlled_factories**
  - Target: None.
  - Description/Notes: Amount of factories within controlled states.

- **num_of_owned_factories**
  - Target: None.
  - Description/Notes: Amount of factories within owned states.

- **num_of_supply_nodes**
  - Target: None.
  - Description/Notes: Amount of supply nodes.

- **num_of_nukes**
  - Target: None.
  - Description/Notes: Amount of nukes.

- **num_researched_technologies**
  - Target: None.
  - Description/Notes: Number of technologies a tag has researched.

- **num_tech_sharing_groups**
  - Target: None.
  - Description/Notes: How many tech sharing groups a nation is a member of.

- **surrender_progress**
  - Target: None.
  - Description/Notes: How close the country is to surrendering on the scale from 0 to 1.

- **has_legitimacy**
  - Target: None.
  - Description/Notes: Legitimacy of the government in exile on the scale from 0 to 100. Defaults to 0 if none.

- **pc_total_score**
  - Target: None.
  - Description/Notes: Total score of the country on the currently-ongoing peace conference where it is a winner.

- **pc_current_score**
  - Target: None.
  - Description/Notes: Current score of the country on the currently-ongoing peace conference where it is a winner.

- **days_left**
  - Target:
    ```text
    Country flag such as
    :my_flag
    ```
  - Description/Notes:
    ```text
    The current number of remaining days for a country flag. Must be targeted with a
    :
    rather than a
    @
    with the position of the target and the variable being swapped unlike in most other game variables, e.g.
    my_flag:days_left
    . The value of the variable cannot be directly passed into another variable; instead, a
    meta effect
    must be used.
    ```

- **army_intel**
  - Target: Country.
  - Description/Notes: Army intel against the target country.

- **navy_intel**
  - Target: Country.
  - Description/Notes: Navy intel against the target country.

- **airforce_intel**
  - Target: Country.
  - Description/Notes: Air intel against the target country.(If you need to use this variable as a trigger for checking, please write a localization yourself.)

- **civilian_intel**
  - Target: Country.
  - Description/Notes: Civilian intel against the target country.

- **encryption_strength**
  - Target: None.
  - Description/Notes:
    ```text
    Total encryption strength of the country. Only without the
    La Résistance
    DLC.
    ```

- **decryption_speed**
  - Target: None.
  - Description/Notes:
    ```text
    Total decryption speed of the country. Only without the
    La Résistance
    DLC.
    ```

- **cryptology_defense_level**
  - Target: None.
  - Description/Notes: cryptology defense level of the country.

- **agency_upgrade_number**
  - Target: None.
  - Description/Notes: The number of upgrade done in the intelligence agency.

- **decryption_progress**
  - Target: Country.
  - Description/Notes: Decryption progress against the target country.

- **network_national_coverage**
  - Target: Country.
  - Description/Notes: Network national coverage the current country has over the target country.

- **num_fake_intel_divisions**
  - Target: None.
  - Description/Notes: The amount of fake intel division that the country has.

- **num_operative_slots**
  - Target: None.
  - Description/Notes: The number of available operative slots a country has. If this differs from the number of operative, this does not mean the country can recruit an operative, but that it will eventually be able to.

- **num_free_operative_slots**
  - Target: None.
  - Description/Notes: The amount of operative slots that are currently empty and an operative can be recruited in.

- **num_of_operatives**
  - Target: None.
  - Description/Notes: The number of operatives the country controls.

- **manpower**
  - Target: None.
  - Description/Notes:
    ```text
    Manpower that the country has, both in the army and reserved. Deprecated, recommended to use
    manpower_k
    instead as to push the necessary number for an overflow to ~2 billion from the very possible ~2 million.
    has_manpower
    can be used in the same way.
    ```

- **manpower_k**
  - Target: None.
  - Description/Notes: Manpower that the country has, both in the army and reserved, in thousands.

- **deployed_army_manpower_k**
  - Target: None.
  - Description/Notes: Manpower in the army in the field in thousands. Do not count manpower in training.

- **deployed_navy_manpower_k**
  - Target: None.
  - Description/Notes: Manpower in the navy in thousands.

- **deployed_airforce_manpower_k**
  - Target: None.
  - Description/Notes: Manpower in the airforce in thousands.

- **max_available_manpower**
  - Target: None.
  - Description/Notes:
    ```text
    Manpower that the country has, both in the army and reserved, taking into account those that are in the process of being drafted as the result of a recent conscription amount change. Deprecated, recommended to use
    max_available_manpower_k
    instead as to push the necessary number for an overflow to ~2 billion from the very possible ~2 million.
    ```

- **max_available_manpower_k**
  - Target: None.
  - Description/Notes: Manpower that the country has, both in the army and reserved, taking into account those that are in the process of being drafted as the result of a recent conscription amount change, in thousands.

- **target_conscription_amount**
  - Target: None.
  - Description/Notes: The target conscription amount of the country.

- **amount_manpower_in_deployment_queue**
  - Target: None.
  - Description/Notes: Amount of manpower currently in the deployment view.

- **conscription_ratio**
  - Target: None.
  - Description/Notes: Conscription ratio of the country compared to target conscription ratio.

- **current_conscription_amount**
  - Target: None.
  - Description/Notes: The current conscription amount of the country.

- **command_power**
  - Target: None.
  - Description/Notes: The current command power of country.

- **command_power_daily**
  - Target: None.
  - Description/Notes: The current daily gain of command power by country.

- **army_experience**
  - Target: None.
  - Description/Notes: Army experience that the country has.

- **navy_experience**
  - Target: None.
  - Description/Notes: Naval experience that the country has.

- **air_experience**
  - Target: None.
  - Description/Notes: Air experience that the country has.

- **num_armies**
  - Target: None.
  - Description/Notes: Amount of land divisions.

- **num_armies_in_state**
  - Target:
    ```text
    State such as
    @123
    .
    ```
  - Description/Notes: Amount of land divisions within the target state.

- **num_armies_with_type**
  - Target:
    ```text
    Subunit type such as
    @light_armor
    .
    ```
  - Description/Notes: Amount of land divisions that are majority of the same subunit type.

- **num_battalions**
  - Target: None.
  - Description/Notes: Amount of battalions within land divisions the country has.

- **num_battalions_with_type**
  - Target:
    ```text
    Subunit type such as
    @cavalry
    .
    ```
  - Description/Notes: Amount of battalions within land divisions the country has that have the specified subunit type.

- **num_deployed_planes**
  - Target: None.
  - Description/Notes: Amount of deployed planes.

- **num_deployed_planes_with_type**
  - Target:
    ```text
    Subunit type such as
    @fighter
    .
    ```
  - Description/Notes: Amount of deployed planes with equipment type.

- **num_divisions**
  - Target: None.
  - Description/Notes: Amount of land and naval divisions.

- **num_equipment**
  - Target:
    ```text
    Equipment type or archetype such as
    @infantry_equipment
    .
    ```
  - Description/Notes: Amount of equipment within the country's stockpile.

- **num_equipment_in_armies**
  - Target:
    ```text
    Equipment type or archetype such as
    @artillery_equipment
    .
    ```
  - Description/Notes:
    ```text
    Amount of equipment in country that are used in armies. If there's a large amount of equipment possible, use
    num_equipment_in_armies_k
    .
    ```

- **num_equipment_in_armies_k**
  - Target:
    ```text
    Equipment type or archetype such as
    @support_equipment
    .
    ```
  - Description/Notes: Amount of equipment in country that are used in armies, in thousands.

- **num_target_equipment_in_armies**
  - Target:
    ```text
    Equipment type or archetype such as
    @motorized_equipment_1
    .
    ```
  - Description/Notes:
    ```text
    Amount of equipment in country that are wanted in armies. If there's a large amount of equipment possible, use
    num_target_equipment_in_armies_k
    .
    ```

- **num_target_equipment_in_armies_k**
  - Target:
    ```text
    Equipment type or archetype such as
    @anti_air_equipment_1
    .
    ```
  - Description/Notes: Amount of equipment in country that are wanted in armies, in thousands.

- **total_equipment_produced_<type>**
  - Target: None.
  - Description/Notes:
    ```text
    The total amount of produced equipment with the specified type of equipment archetypes. The following options exist:
    Name
    Base game notes
    total_equipment_produced_infantry
    Includes infantry equipment, support equipment, artillery (non-rocket), anti-air, and anti-tank.
    total_equipment_produced_artillery
    Also includes anti-air, anti-tank, and rocket artillery.
    total_equipment_produced_anti_air
    total_equipment_produced_anti_tank
    total_equipment_produced_rocket
    total_equipment_produced_support
    total_equipment_produced_motorized
    Also includes armoured cars, rocket artillery, and support equipment.
    total_equipment_produced_mechanized
    total_equipment_produced_capital_ship
    total_equipment_produced_submarine
    total_equipment_produced_carrier
    total_equipment_produced_screen_ship
    total_equipment_produced_fighter
    total_equipment_produced_heavy_fighter
    total_equipment_produced_cas
    total_equipment_produced_interceptor
    total_equipment_produced_strategic_bomber
    total_equipment_produced_tactical_bomber
    total_equipment_produced_naval_bomber
    total_equipment_produced_maritime_patrol_plane
    total_equipment_produced_scout_plane
    total_equipment_produced_air_transport
    total_equipment_produced_suicide
    Suicide bombers.
    total_equipment_produced_missile
    total_equipment_produced_convoy
    total_equipment_produced_armor
    total_equipment_produced_amphibious
    Only includes amphibious tanks and not amphibious mechanised equipment.
    total_equipment_produced_flame
    total_equipment_produced_train
    total_equipment_produced_railway_gun
    total_equipment_produced_floating_harbor
    ```
  - Column 4: Name
  - Column 5: Base game notes
  - Column 6: total_equipment_produced_infantry
  - Column 7: Includes infantry equipment, support equipment, artillery (non-rocket), anti-air, and anti-tank.
  - Column 8: total_equipment_produced_artillery
  - Column 9: Also includes anti-air, anti-tank, and rocket artillery.
  - Column 10: total_equipment_produced_anti_air
  - Column 12: total_equipment_produced_anti_tank
  - Column 14: total_equipment_produced_rocket
  - Column 16: total_equipment_produced_support
  - Column 18: total_equipment_produced_motorized
  - Column 19: Also includes armoured cars, rocket artillery, and support equipment.
  - Column 20: total_equipment_produced_mechanized
  - Column 22: total_equipment_produced_capital_ship
  - Column 24: total_equipment_produced_submarine
  - Column 26: total_equipment_produced_carrier
  - Column 28: total_equipment_produced_screen_ship
  - Column 30: total_equipment_produced_fighter
  - Column 32: total_equipment_produced_heavy_fighter
  - Column 34: total_equipment_produced_cas
  - Column 36: total_equipment_produced_interceptor
  - Column 38: total_equipment_produced_strategic_bomber
  - Column 40: total_equipment_produced_tactical_bomber
  - Column 42: total_equipment_produced_naval_bomber
  - Column 44: total_equipment_produced_maritime_patrol_plane
  - Column 46: total_equipment_produced_scout_plane
  - Column 48: total_equipment_produced_air_transport
  - Column 50: total_equipment_produced_suicide
  - Column 51: Suicide bombers.
  - Column 52: total_equipment_produced_missile
  - Column 54: total_equipment_produced_convoy
  - Column 56: total_equipment_produced_armor
  - Column 58: total_equipment_produced_amphibious
  - Column 59: Only includes amphibious tanks and not amphibious mechanised equipment.
  - Column 60: total_equipment_produced_flame
  - Column 62: total_equipment_produced_train
  - Column 64: total_equipment_produced_railway_gun
  - Column 66: total_equipment_produced_floating_harbor

- **Name**
  - Target: Base game notes

- **total_equipment_produced_infantry**
  - Target: Includes infantry equipment, support equipment, artillery (non-rocket), anti-air, and anti-tank.

- **total_equipment_produced_artillery**
  - Target: Also includes anti-air, anti-tank, and rocket artillery.

- **total_equipment_produced_anti_air**

- **total_equipment_produced_anti_tank**

- **total_equipment_produced_rocket**

- **total_equipment_produced_support**

- **total_equipment_produced_motorized**
  - Target: Also includes armoured cars, rocket artillery, and support equipment.

- **total_equipment_produced_mechanized**

- **total_equipment_produced_capital_ship**

- **total_equipment_produced_submarine**

- **total_equipment_produced_carrier**

- **total_equipment_produced_screen_ship**

- **total_equipment_produced_fighter**

- **total_equipment_produced_heavy_fighter**

- **total_equipment_produced_cas**

- **total_equipment_produced_interceptor**

- **total_equipment_produced_strategic_bomber**

- **total_equipment_produced_tactical_bomber**

- **total_equipment_produced_naval_bomber**

- **total_equipment_produced_maritime_patrol_plane**

- **total_equipment_produced_scout_plane**

- **total_equipment_produced_air_transport**

- **total_equipment_produced_suicide**
  - Target: Suicide bombers.

- **total_equipment_produced_missile**

- **total_equipment_produced_convoy**

- **total_equipment_produced_armor**

- **total_equipment_produced_amphibious**
  - Target: Only includes amphibious tanks and not amphibious mechanised equipment.

- **total_equipment_produced_flame**

- **total_equipment_produced_train**

- **total_equipment_produced_railway_gun**

- **total_equipment_produced_floating_harbor**

- **num_ships**
  - Target: None.
  - Description/Notes: Amount of ships.

- **num_ships_with_type**
  - Target:
    ```text
    Subunit type such as
    @carrier
    .
    ```
  - Description/Notes: Amount of ships with the specified subunit type.

- **land_doctrine_level**
  - Target: None.
  - Description/Notes: The currently-researched land doctrine level.

A large portion of the AI-related game variables can have values seen in-game by using the `aiview` console command.

- **ai_attitude_allied_weight**
  - Target: Country.
  - Description/Notes:
    ```text
    The total amount of the
    attitude_allied
    AI attribute.
    ```

- **ai_attitude_friendly_weight**
  - Target: Country.
  - Description/Notes:
    ```text
    The total amount of the
    attitude_friendly
    AI attribute.
    ```

- **ai_attitude_hostile_weight**
  - Target: Country.
  - Description/Notes:
    ```text
    The total amount of the
    attitude_hostile
    AI attribute.
    ```

- **ai_attitude_is_threatened**
  - Target: None.
  - Description/Notes: Returns 1 if the AI is threatened, 0 otherwise.

- **ai_attitude_neutral_weight**
  - Target: Country.
  - Description/Notes:
    ```text
    The total amount of the
    attitude_neutral
    AI attribute.
    ```

- **ai_attitude_outraged_weight**
  - Target: Country.
  - Description/Notes:
    ```text
    The total amount of the
    attitude_outraged
    AI attribute.
    ```

- **ai_attitude_protective_weight**
  - Target: Country.
  - Description/Notes:
    ```text
    The total amount of the
    attitude_protective
    AI attribute.
    ```

- **ai_attitude_threatened_weight**
  - Target: Country.
  - Description/Notes:
    ```text
    The total amount of the
    attitude_threatened
    AI attribute.
    ```

- **ai_attitude_wants_ally**
  - Target: None.
  - Description/Notes: Returns 1 if the AI wants to ally any country, 0 otherwise.

- **ai_attitude_wants_antagonize**
  - Target: None.
  - Description/Notes: Returns 1 if the AI wants to antagonize any country, 0 otherwise.

- **ai_attitude_wants_ignore**
  - Target: None.
  - Description/Notes: Returns 1 if the AI wants to ignore any country, 0 otherwise.

- **ai_attitude_wants_protect**
  - Target: None.
  - Description/Notes: Returns 1 if the AI wants to protect any country, 0 otherwise.

- **ai_attitude_wants_weaken**
  - Target: None.
  - Description/Notes: Returns 1 if the AI wants to weaken any country, 0 otherwise.

- **ai_strategy_activate_crypto**
  - Target: Country.
  - Description/Notes:
    ```text
    Total sum of the
    AI strategy
    values of the type
    activate_crypto
    towards the target country.
    ```

- **ai_strategy_alliance**
  - Target: Country.
  - Description/Notes:
    ```text
    Total sum of the
    AI strategy
    values of the type
    alliance
    towards the target country.
    ```

- **ai_strategy_antagonize**
  - Target: Country.
  - Description/Notes:
    ```text
    Total sum of the
    AI strategy
    values of the type
    antagonize
    towards the target country.
    ```

- **ai_strategy_befriend**
  - Target: Country.
  - Description/Notes:
    ```text
    Total sum of the
    AI strategy
    values of the type
    befriend
    towards the target country.
    ```

- **ai_strategy_conquer**
  - Target: Country.
  - Description/Notes:
    ```text
    Total sum of the
    AI strategy
    values of the type
    conquer
    towards the target country.
    ```

- **ai_strategy_consider_weak**
  - Target: Country.
  - Description/Notes:
    ```text
    Total sum of the
    AI strategy
    values of the type
    consider_weak
    towards the target country.
    ```

- **ai_strategy_contain**
  - Target: Country.
  - Description/Notes:
    ```text
    Total sum of the
    AI strategy
    values of the type
    contain
    towards the target country.
    ```

- **ai_strategy_declare_war**
  - Target: Country.
  - Description/Notes:
    ```text
    Total sum of the
    AI strategy
    values of the type
    declare_war
    towards the target country.
    ```

- **ai_strategy_decrypt_target**
  - Target: Country.
  - Description/Notes:
    ```text
    Total sum of the
    AI strategy
    values of the type
    decrypt_target
    towards the target country.
    ```

- **ai_strategy_dont_defend_ally_borders**
  - Target: Country.
  - Description/Notes:
    ```text
    Total sum of the
    AI strategy
    values of the type
    dont_defend_ally_borders
    towards the target country.
    ```

- **ai_strategy_force_defend_ally_borders**
  - Target: Country.
  - Description/Notes:
    ```text
    Total sum of the
    AI strategy
    values of the type
    force_defend_ally_borders
    towards the target country.
    ```

- **ai_strategy_ignore**
  - Target: Country.
  - Description/Notes:
    ```text
    Total sum of the
    AI strategy
    values of the type
    ignore
    towards the target country.
    ```

- **ai_strategy_ignore_claim**
  - Target: Country.
  - Description/Notes:
    ```text
    Total sum of the
    AI strategy
    values of the type
    ignore_claim
    towards the target country.
    ```

- **ai_strategy_influence**
  - Target: Country.
  - Description/Notes:
    ```text
    Total sum of the
    AI strategy
    values of the type
    influence
    towards the target country.
    ```

- **ai_strategy_invade**
  - Target: Country.
  - Description/Notes:
    ```text
    Total sum of the
    AI strategy
    values of the type
    invade
    towards the target country.
    ```

- **ai_strategy_occupation_policy**
  - Target: Country.
  - Description/Notes:
    ```text
    Total sum of the
    AI strategy
    values of the type
    occupation_policy
    towards the target country.
    ```

- **ai_strategy_prepare_for_war**
  - Target: Country.
  - Description/Notes:
    ```text
    Total sum of the
    AI strategy
    values of the type
    prepare_for_war
    towards the target country.
    ```

- **ai_strategy_protect**
  - Target: Country.
  - Description/Notes:
    ```text
    Total sum of the
    AI strategy
    values of the type
    protect
    towards the target country.
    ```

- **ai_strategy_send_volunteers_desire**
  - Target: Country.
  - Description/Notes:
    ```text
    Total sum of the
    AI strategy
    values of the type
    send_volunteers_desire
    towards the target country.
    ```

- **ai_strategy_support**
  - Target: Country.
  - Description/Notes:
    ```text
    Total sum of the
    AI strategy
    values of the type
    support
    towards the target country.
    ```

- **ai_irrationality**
  - Target: None.
  - Description/Notes: The AI's irrationality value.

- **ai_wants_divisions**
  - Target: None.
  - Description/Notes: The total amount of divisions that the AI aims for.

- **id**
  - Target: None.
  - Description/Notes:
    ```text
    The internal ID of the state. While regular
    set_variable = { my_state_pointer = 123 }
    would still work as a pointer to the state, this can remove ambiguity within the code whether the number is used as a state ID or the number that refers to the state with the state ID of 123.
    Not the same value as the state ID
    defined with
    id=123
    in the file, typically returns some negative number instead. For fetching the state ID, a
    meta effect
    using
    the GetID namespace
    can be used.
    ```

- **building_level**
  - Target:
    ```text
    Building such as
    @nuclear_reactor
    .
    ```
  - Description/Notes: The level of a building with the target type.

- **arms_factory_level**
  - Target: None.
  - Description/Notes: Military factory level in the state

- **industrial_complex_level**
  - Target: None.
  - Description/Notes: civilian factory level in the state

- **infrastructure_level**
  - Target: None.
  - Description/Notes: infrastructure level in the state

- **damaged_building_level**
  - Target:
    ```text
    Building such as
    @industrial_complex
    .
    ```
  - Description/Notes: Damaged building level of a building with target type.

- **non_damaged_building_level**
  - Target:
    ```text
    Building such as
    @arms_factory
    .
    ```
  - Description/Notes: Non-damaged building level of a building with target type.

- **modifier**
  - Target:
    ```text
    Modifier's name, such as
    @political_power_gain
    .
    ```
  - Description/Notes:
    ```text
    The total value of the current
    modifier
    as the country has in total. Targeted modifiers have separate definitions.
    ```

- **controller**
  - Target: None.
  - Description/Notes: Controller of the state.

- **owner**
  - Target: None.
  - Description/Notes: Owner of the state.

- **distance_to**
  - Target: State.
  - Description/Notes: Distance between the current state and the target state.

- **resource**
  - Target:
    ```text
    Resource type such as
    @chromium
    ```
  - Description/Notes: Amount of the resource produced within state.

- **compliance**
  - Target: None.
  - Description/Notes: Current compliance level of the state.

- **compliance_speed**
  - Target: None.
  - Description/Notes: Current compliance speed of the state.

- **days_since_last_strategic_bombing**
  - Target: None.
  - Description/Notes: Amount of days since the state was last strategic bombed.

- **resistance**
  - Target: None.
  - Description/Notes: Current resistance level of the state. On the scale from 0 to 100.

- **resistance_speed**
  - Target: None.
  - Description/Notes: Current resistance speed of the state.

- **resistance_target**
  - Target: None.
  - Description/Notes: Current resistance target of the state. On the scale from 0 to 100.

- **state_population**
  - Target: None.
  - Description/Notes:
    ```text
    Current population of the state. Recommended to use
    state_population_k
    when possible to push the necessary number for an overflow to ~2 billion from the very possible ~2 million.
    ```

- **state_population_k**
  - Target: None.
  - Description/Notes: Current population of the state in thousands.

- **state_and_terrain_strategic_value**
  - Target: None.
  - Description/Notes: Current state and terrain strategic value, decided by buildings and terrain of provinces.

- **state_strategic_value**
  - Target: None.
  - Description/Notes: Current state strategic value, decided by buildings.

- **days_left**
  - Target:
    ```text
    State flag such as
    :my_flag
    ```
  - Description/Notes:
    ```text
    The current number of remaining days for a state flag. Must be targeted with a
    :
    rather than a
    @
    with the position of the target and the variable being swapped unlike in most other game variables, e.g.
    my_flag:days_left
    . The value of the variable cannot be directly passed into another variable; instead, a
    meta effect
    must be used.
    ```

- **leader_modifier**
  - Target:
    ```text
    Modifier's name, such as
    @navy_max_range
    .
    ```
  - Description/Notes:
    ```text
    The total value of the specified
    modifier
    as the unit leader has in total, applied towards the leader. This is represented with
    non_shared_modifier = { ... }
    in
    unit leader traits
    .
    ```

- **unit_modifier**
  - Target:
    ```text
    Modifier type, such as
    @army_attack_factor
    ```
  - Description/Notes:
    ```text
    The total value of the specified
    modifier
    as the unit leader has in total, applied towards the units. This is represented with
    modifier = { ... }
    in
    unit leader traits
    .
    ```

- **sum_unit_terrain_modifier**
  - Target:
    ```text
    Modifier type, such as
    @sickness_chance
    ```
  - Description/Notes: The total sum of the modifier value applied by each province that this unit leader has divisions on.

- **army_attack_level**
  - Target: None.
  - Description/Notes: The attack level of the leader.

- **army_defense_level**
  - Target: None.
  - Description/Notes: The defense level of the leader.

- **attack_level**
  - Target: None.
  - Description/Notes:
    ```text
    The attack level of the leader.
    attack_skill_level
    exists as a synonym.
    ```

- **coordination_level**
  - Target: None.
  - Description/Notes: The coordination level of the leader.

- **defense_level**
  - Target: None.
  - Description/Notes:
    ```text
    The defense level of the leader.
    defense_skill_level
    exists as a synonym.
    ```

- **logistics_level**
  - Target: None.
  - Description/Notes:
    ```text
    The logistics level of the leader.
    logistics_skill_level
    exists as a synonym.
    ```

- **maneuvering_level**
  - Target: None.
  - Description/Notes: The maneuvering level of the leader.

- **planning_level**
  - Target: None.
  - Description/Notes:
    ```text
    The planning level of the leader.
    planning_skill_level
    exists as a synonym.
    ```

- **skill_level**
  - Target: None.
  - Description/Notes:
    ```text
    The general skill level of the leader.
    skill
    exists as a synonym.
    ```

- **average_stats**
  - Target: None.
  - Description/Notes: The average stats of the unit leader.

- **avg_combat_status**
  - Target: None.
  - Description/Notes: The average status of each engagement that units led by the leader are participating in.

- **avg_defensive_combat_status**
  - Target: None.
  - Description/Notes: The average status of each defensive engagement that units led by the leader are participating in.

- **avg_offensive_combat_status**
  - Target: None.
  - Description/Notes: The average status of each offensive engagement that units led by the leader are participating in.

- **avg_unit_planning_ratio**
  - Target: None.
  - Description/Notes: The average ratio of planning bonus that each unit has.

- **avg_units_acclimation**
  - Target:
    ```text
    Acclimatization type, such as
    @hot_climate
    ```
  - Description/Notes:
    ```text
    Average unit acclimatization for the specified climate, which is defined in
    /Hearts of Iron IV/common/acclimatation.txt
    ```

- **has_orders_group**
  - Target: None.
  - Description/Notes: Returns 1 if the general has any order groups assigned to them, 0 otherwise.

- **num_traits**
  - Target: None.
  - Description/Notes: Amount of traits that the unit leader has.

- **num_assigned_traits**
  - Target: None.
  - Description/Notes: Amount of assigned traits the leader has.

- **num_basic_traits**
  - Target: None.
  - Description/Notes: Amount of basic traits that the unit leader has.

- **num_personality_traits**
  - Target: None.
  - Description/Notes: Amount of personality traits that the unit leader has.

- **num_status_traits**
  - Target: None.
  - Description/Notes: Amount of status traits that the unit leader has.

- **num_max_traits**
  - Target: None.
  - Description/Notes: Amount of maximum assignable traits the leader can have.

- **num_terrain_traits**
  - Target: None.
  - Description/Notes: Amount of terrain traits that the unit leader has.

- **num_battalions**
  - Target: None.
  - Description/Notes: Amount of battalions that the army leader has within units under their control.

- **num_battalions_with_type**
  - Target:
    ```text
    Subunit type such as
    @artillery_brigade
    ```
  - Description/Notes: Amount of battalions with sub unit type, sub unit type is defined in target, example: num_battalions_with_type@light_armor

- **num_battle_plans**
  - Target: None.
  - Description/Notes: Amount of battle plans that the unit leader is assigned to.

- **num_orders_groups**
  - Target: None.
  - Description/Notes: Number of order groups assigned to the unit leader.

- **num_equipment**
  - Target:
    ```text
    Equipment type or archetype such as
    @light_tank_chassis
    .
    ```
  - Description/Notes: Amount of equipment fulfilled within units led by the unit leader.

- **num_target_equipment**
  - Target:
    ```text
    Equipment type or archetype such as
    @anti_tank_equipment
    ```
  - Description/Notes: Amount of equipment required within units led by the unit leader.

- **num_units_with_type**
  - Target:
    ```text
    Subunit type such as
    @modern_armor
    ```
  - Description/Notes: The amount of units controlled by the unit leader that are predominantly filled with subunits that are assigned the specified type.

- **num_armored**
  - Target: None.
  - Description/Notes:
    ```text
    The amount of units controlled by the unit leader that are predominantly filled with subunits that are assigned the
    armored
    type.
    ```

- **num_artillery**
  - Target: None.
  - Description/Notes:
    ```text
    The amount of units controlled by the unit leader that are predominantly filled with subunits that are assigned the
    artillery
    type.
    ```

- **num_cavalry**
  - Target: None.
  - Description/Notes:
    ```text
    The amount of units controlled by the unit leader that are predominantly filled with subunits that are assigned the
    cavalry
    type.
    ```

- **num_infantry**
  - Target: None.
  - Description/Notes:
    ```text
    The amount of units controlled by the unit leader that are predominantly filled with subunits that are assigned the
    infantry
    type.
    ```

- **num_mechanized**
  - Target: None.
  - Description/Notes:
    ```text
    The amount of units controlled by the unit leader that are predominantly filled with subunits that are assigned the
    mechanized
    type.
    ```

- **num_motorized**
  - Target: None.
  - Description/Notes:
    ```text
    The amount of units controlled by the unit leader that are predominantly filled with subunits that are assigned the
    motorized
    type.
    ```

- **num_rocket**
  - Target: None.
  - Description/Notes:
    ```text
    The amount of units controlled by the unit leader that are predominantly filled with subunits that are assigned the
    rocket
    type.
    ```

- **num_special**
  - Target: None.
  - Description/Notes:
    ```text
    The amount of units controlled by the unit leader that are predominantly filled with subunits that are assigned the
    special
    type.
    ```

- **num_ships**
  - Target: None.
  - Description/Notes: Amount of ships controlled by the unit leader

- **num_ships_with_type**
  - Target:
    ```text
    Subunit type such as
    @destroyer
    .
    ```
  - Description/Notes: Amount of ships controlled by the unit leader, ship type is defined in target, example: num_ships_with_type@carrier

- **num_units**
  - Target: None.
  - Description/Notes: Amount of units controlled by the unit leader.

- **num_units_crossing_river**
  - Target: None.
  - Description/Notes: Amount of units currently passing through a river.

- **num_units_in_combat**
  - Target: None.
  - Description/Notes: Amount of units currently fighting under control of this unit leader.

- **num_units_defensive_combats**
  - Target: None.
  - Description/Notes: Amount of units in defensive combat under control of this unit leader.

- **num_units_defensive_combats_on**
  - Target:
    ```text
    Provincial terrain, such as
    @marsh
    ```
  - Description/Notes: Amount of units that are currently defensively fighting on the specified terrain under control of this unit leader.

- **num_units_offensive_combats**
  - Target: None.
  - Description/Notes: Amount of units in offensive combat under control of this unit leader.

- **num_units_offensive_combats_against**
  - Target:
    ```text
    Provincial terrain type such as
    @urban
    ```
  - Description/Notes: Amount of units that are currently offensively fighting on the specified terrain under control of this unit leader.

- **num_units_in_state**
  - Target: State.
  - Description/Notes: Amount of units controlled by the unit leader within the target state.

- **num_units_on_climate**
  - Target:
    ```text
    Acclimatization type, such as
    @cold_climate
    ```
  - Description/Notes: Amount of units under control of the unit leader that are on provinces with a climate that requires the specified acclimatization type.

- **unit_ratio_ready_for_plan**
  - Target: None.
  - Description/Notes: The percentage of units, on the scale from 0 to 1, under control of this unit leader that have the full planning bonus.

- **intel_yield_factor_on_capture**
  - Target: None.
  - Description/Notes: The rate at which intel is extracted from this operative by an enemy country.

- **operation_country**
  - Target: None.
  - Description/Notes: The country that the operative is assigned to work in. 0 if not assigned to a country.

- **operation_state**
  - Target: None.
  - Description/Notes: The state that the operative is assigned to work in. 0 if not assigned to a country.

- **operation_type**
  - Target: None.
  - Description/Notes: The operation that the operative to work on.

- **operative_captor**
  - Target: None.
  - Description/Notes: The country that the operative is captured by.

- **own_capture_chance_factor**
  - Target: None.
  - Description/Notes: The chance that the operative has to be captured.

- **own_forced_into_hiding_time_factor**
  - Target: None.
  - Description/Notes: The chance that the operative has to be forced into hiding.

- **own_harmed_time_factor**
  - Target: None.
  - Description/Notes: The chance that the operative has to be harmed.

- **modifier**
  - Target:
    ```text
    Modifier name, such as
    @military_industrial_organization_research_bonus
    ```
  - Description/Notes: The total value of the modifier applied to the MIO.

- **research_bonus**
  - Target: None.
  - Description/Notes: Research bonus of the MIO when assigned to a research slot.

- **size**
  - Target: None.
  - Description/Notes: Size of the MIO.

- **funds**
  - Target: None.
  - Description/Notes: Total MIO funds.

- **number_of_currently_assigned_tasks**
  - Target: None.
  - Description/Notes: Amount of tasks that the MIO is assigned to.

- **max_task_capacity**
  - Target: None.
  - Description/Notes: Maximum task capacity of the MIO.

- **number_of_unlocked_traits**
  - Target: None.
  - Description/Notes: Unlocked traits in the MIO.

- **number_of_unused_trait_points**
  - Target: None.
  - Description/Notes: Unused trait points in the MIO.

### Game arrays

- **countries**
  - Description/Notes:
    ```text
    Every single country, regardless if they exist or not, including the
    50 dynamic countries
    even if they do not have an original tag defined.
    ```

- **majors**
  - Description/Notes: Every country that is currently major.

- **states**
  - Description/Notes: Every state that exists in the game.

- **ideology_groups**
  - Description/Notes: Every ideology group that exists in the game.

- **operations**
  - Description/Notes: Every operation that exists in the game.

- **province_controllers**
  - Description/Notes: An array of controller countries for each province. In this case, the province ID serves as the index: the controller of province 1234 is province_controllers^1234.

- **technology**
  - Description/Notes: Every technology in the game.

- **allies**
  - Description/Notes: Countries that are considered an ally, including fellow faction members, subjects, and the overlord.

- **army_leaders**
  - Description/Notes: Army leaders recruited by the country.

- **enemies**
  - Description/Notes: Countries that the current country is at war with.

- **enemies_of_allies**
  - Description/Notes: Countries that are considered an ally of any country that is at war with the current country.

- **faction_members**
  - Description/Notes: Countries that are in the same faction as this one.

- **occupied_countries**
  - Description/Notes: Countries that are currently occupied by this one.

- **subjects**
  - Description/Notes: Countries that are subject to this one.

- **owned_controlled_states**
  - Description/Notes: States that are owned and controlled by the current country.

- **owned_states**
  - Description/Notes: States that are owned, but not necessarily controlled, by the current country.

- **potential_and_current_enemies**
  - Description/Notes: Countries that are considered enemies and that 'may' become enemies (due to being an ally of an enemy or by having a wargoal)

- **controlled_states**
  - Description/Notes: States that are controlled, but not necessarily owned, by the current country.

- **core_states**
  - Description/Notes: States that are considered national territory of the current country.

- **neighbors**
  - Description/Notes: Countries that are considered neighbours to the current country, having at least one border within controlled provinces.

- **neighbors_owned**
  - Description/Notes: Countries that are considered neighbours to the current country, having at least one owned state that borders any state that the current country owns.

- **researched_techs**
  - Description/Notes: Technologies that were researched by the current country.

- **navy_leaders**
  - Description/Notes: Navy leaders recruited by the country.

- **operatives**
  - Description/Notes: Operatives recruited by the country.

- **exiles**
  - Description/Notes: The exiled governments that the current country is hosting.

- **core_countries**
  - Description/Notes: Countries that consider this state to be national territory.

## References

1. [↑](#cite-ref-1) `NDefines.NGame.EVENT_TIMEOUT_DEFAULT = 13` in [Defines](<Defines - Hearts of Iron 4 Wiki.md>)
2. [↑](#cite-ref-2) `NDefines.NAI.FOCUS_TREE_CONTINUE_FACTOR = 1.5` in [Defines](<Defines - Hearts of Iron 4 Wiki.md>)
3. [↑](#cite-ref-3) `NDefines.NGame.END_DATE = "1949.1.1.1"` in [Defines](<Defines - Hearts of Iron 4 Wiki.md>)
4. [↑](#cite-ref-4) `NDefines.NMilitary.UNIT_EXP_LEVELS = { 0.1, 0.3, 0.75, 0.9 }` in [Defines](<Defines - Hearts of Iron 4 Wiki.md>)
5. ↑ [Jump up to: 5.0](#cite-ref-loop-5-0) [5.1](#cite-ref-loop-5-1) `NDefines.NGame.MAX_EFFECT_ITERATION = 1000` in [Defines](<Defines - Hearts of Iron 4 Wiki.md>)

**[Modding](<Modding - Hearts of Iron 4 Wiki.md>)**
