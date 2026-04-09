# Table of contents

- [Code structure](#code-structure)
  - [Side](#side)
  - [Range](#range)
  - [Example](#example)
- [Implementation](#implementation)
- [Balance of power modifiers](#balance-of-power-modifiers)
- [Effects](#effects)
- [Triggers](#triggers)


---

A **balance of power** (also internally referred to as bop or power balance) is typically used to represent a conflict between two sides, using a progress bar divided into distinct sections and decisions to push it towards some side for benefits. These are defined in /Hearts of Iron IV/common/bop/\*.txt files.

Each balance of power consists of 2 or more sides. While a balance of power can contain more than 2 sides, at any time the player may only see 2 which are chosen in the effect to initialise the balance of power.  
To track the current balance, a single value is used, which can range from -1 to 1 with up to 3 decimal points. The 

[
−
1
;
0
)
{\displaystyle [-1;0)}
![{\displaystyle [-1;0)}](media/balance-of-power-modding-hearts-of-iron-4-wiki_2c86d53bfd__img1.svg) range is used for the left side, 

[
0
;
1
]
{\displaystyle [0;1]}
![{\displaystyle [0;1]}](media/balance-of-power-modding-hearts-of-iron-4-wiki_2c86d53bfd__img2.svg) is used for the right side. A side having power only has a cosmetic impact, changing the icon and the text used in scripted localisation. A side isn't inherently set as being left or right, instead it is assigned which side is on which half when the power balance is initialised.

Depending on the value, the country is placed in some range representing the exact degree of power on a certain side. This is usually used to grant certain [modifiers](<Modifiers - Hearts of Iron 4 Wiki.md>) or to execute an [effect](<Effect - Hearts of Iron 4 Wiki.md>) upon entering it. Most ranges are placed inside of sides, making it only possible to enter when that side is active. A range may also not be assigned to any side and be always visible, usually used for a single "balanced" range in the middle.  
A range being assigned to a side only means that it'll be visible when the range is active, and a side may have ranges on both halves of the balance at the same time. Entering a range defined on a certain side does not necessitate that the balance is tipped in favour of that side. For example, if a side is set as a left side and yet it includes a range of 

[
0.1
,
0.3
)
{\displaystyle [0.1,0.3)}
![{\displaystyle [0.1,0.3)}](media/balance-of-power-modding-hearts-of-iron-4-wiki_2c86d53bfd__img3.svg), then if the value is at 0.2, then the balance will be tipped towards the right side visually, but it will still be inside of that range.

**A balance of power is tracked globally.** If 2 countries are assigned the same BoP, then the value of the balance will always be exactly the same between both countries. If both of these countries have modifiers pushing the BoP to some side daily or weekly, the effects of these modifiers will stack.

## Code structure

Balances of power are created in any /Hearts of Iron IV/common/bop/\*.txt file. A BoP is defined as a root-level block, where the name of the block determines the unique ID of the BoP. In case of duplicates, the error.log entry `Template ID duplicate: bop_name` is generated and the game will prioritise the one that was [created later](<Modding - Hearts of Iron 4 Wiki.md#code-structure>), determined using the filename and order in files.  
There are no strictly mandatory arguments, however it is preferred to have at least 2 sides as the UI is built on the assumption that there is always a left and a right side active. In particular, these arguments exist:

- `intial_value = -0.1` is the default value of the BoP. If unset, defaults to 0.
- `left_side = side_id` is the default left side of the BoP.
- `right_side = side_id` is the default right side of the BoP.

The default values are used when the BoP is first initialised with [set\_power\_balance](#set-power-balance) (unless overwritten by its arguments) or when that same effect includes `set_default = yes` to reset it.

- `decision_category = TAG_example_category` will move that decision category to the balance of power view. In particular, this ensures that it's impossible to access the decision category in any way other than by the balance of power. Any trigger blocks in the decision category, such as `allowed = { ... }`, are still checked for the country with the BoP, however.

In addition, `side = { ... }` and `range = { ... }` are possible with more detail.

### Side

Each side is defined using a `side = { ... }` block in the balance of power. In particular, these arguments exist:

- `id = side_id` is the identifier used for the side. There should not be overlap in the same BoP, however overlap may exist between different BoPs. In case of overlap in the same BoP, only the first-created side will be used with a `Side ID duplicate: side_id` entry in error.log.
- `icon = GFX_idea_unknown` is the spriteType used as the image to represent the side. If undefined or if the spriteType doesn't exist, the icon will not be created with no default to replace it.

- **For loading GFX, the game uses the sprite system. Sprites are code definitions that attach a name to an image file, as well as optionally adding additional information, such as animation, the amount of frames, the way that the image will be loaded, and so on. This means**
  - Example:
    ```text
    spriteTypes = {
        spriteType = {
            name = GFX_first_sprite                         # In some cases, beginning with GFX_ is mandatory for it to work.
            texturefile = gfx/interface/folder/filename.dds # The folder and filename don't matter, as long as they are correct
        }                                                   # Only the forward slash '/' (can be doubled as '//') can be used to separate folders.
        spriteType = {                                      # The image doesn't have to be .dds, as .tga and .png are acceptable.
            name = GFX_second_sprite
            texturefile = gfx/interface/folder2/filename2.dds
            noOfFrames = 2 # Splits the image into 2 halves, which may be switched between dynamically in GUI
        }
    }
    ```

- `range = { ... }` is a range set to exist if and only if that side is active.

### Range

A range is defined as a `range = { ... }` block which may exist either directly in the BoP or inside of a `side = { ... }`. This is used to determine when the range will be visible to the player: a range directly in a BoP is always visible, while a range in a side will only be visible if that side is visible. There are 3 mandatory attributes:

- `id = range_id` is used to assign an ID to the specified range. There shouldn't be duplicates across the entire BoP (even in different sides), but there may be between different BoPs. A duplicate will be marked with a `Range ID duplicate: range_id` entry in error.log. In this case, the game will still display each range with the same ID that is not in a disabled side. However, this can cause issues with strict non-equal comparison when using [is\_power\_balance\_in\_range](#is-power-balance-in-range): in particular, the game will only recognise the range that's placed furthest to the left. For example, if there are duplicate `range_id` on intervals of 

  [
  −
  0.3
  ,
  −
  0.1
  )
  {\displaystyle [-0.3,-0.1)}
  ![{\displaystyle [-0.3,-0.1)}](media/balance-of-power-modding-hearts-of-iron-4-wiki_2c86d53bfd__img4.svg) and 

  [
  0.1
  ,
  0.3
  )
  {\displaystyle [0.1,0.3)}
  ![{\displaystyle [0.1,0.3)}](media/balance-of-power-modding-hearts-of-iron-4-wiki_2c86d53bfd__img5.svg), then a strict equilibrium will be recognised as being to the right of `range_id`, but not to the left of it.
- `min = -0.1` is the minimum value in the range's interval. If the value is exactly at this point, this range will be applied.
- `max = 0.1` is the maximum value in the range's interval. If the value is exactly at this point, this range will be applied if and only if max is set to 1. Otherwise, the exact point is excluded from the interval.

There are also blocks that decide which impact exactly a range has on the country when the value is inside that. In particular:

- `modifier = { ... }` decides on the [modifiers](<Modifiers - Hearts of Iron 4 Wiki.md>) applying to the country when the value is in that range.
- `rule = { ... }` decides on the [game rules](<Effect - Hearts of Iron 4 Wiki.md#set-rule>) applying to the country when the value is in that range.
- `on_activate = { ... }` executes effects the instant that the value enters this range.
- `on_deactivate = { ... }` executes effects the instant that the value exits this range.

### Example

```text
TAG_example_balance = {
    initial_value = 0.25
    left_side = default_left_side
    right_side = default_right_side
    decision_category = TAG_example_category
    range = {
        id = mid_range
        min = -0.1
        max = 0.1
        modifier = {
            war_support_weekly = 0.5
        }
        rule = {
            can_create_faction = yes
        }
    }

    side = {
        id = default_left_side
        icon = GFX_idea_generic_agrarian_society
        range = {
            id = left_side_range
            min = -1
            max = -0.1
            modifier = {
                war_support_weekly = 0.1
            }
            on_activate = {
                random_owned_controlled_state = {
                    limit = {
                        NOT = { is_core_of = PREV }
                    }
                    add_core_of = PREV
                    set_state_flag = cored_by_bop
                }
            }
            on_deactivate = {
                random_owned_controlled_state = {
                    limit = {
                        has_state_flag = cored_by_bop
                    }
                    remove_core_of = PREV
                    clr_state_flag = cored_by_bop
                }
            }
        }
    }
    side = {
        id = default_right_side
        icon = GFX_idea_generic_degauss_ship_hulls
        range = {
            id = right_side_range
            min = 0.1
            max = 1
            modifier = {
                war_support_weekly = 0.9
            }
        }
    }
}
```

## Implementation

As a balance of power isn't inherently assigned to any country, it must be manually initialised. This is done using the `set_power_balance` [effect](<Effect - Hearts of Iron 4 Wiki.md>). For example, this is the most bare-bones way to initialise the BoP, which will set it to the default:

```text
set_power_balance = {
    id = TAG_example_balance
}
```

The effect can also be used to change details about the currently-active balance of power, such as changing the sides or the value:

```text
set_power_balance = {
    id = TAG_example_balance
    left_side = default_left_side
    right_side = default_right_side
    set_value = 0.1
}
```

If necessary to reset it completely to the default, `set_default = yes` will do so.

```text
set_power_balance = {
    id = TAG_example_balance
    set_default = yes
}
```

As an effect, it can be used in any effect block. If it should be initialised at the game's start, this is usually done in [country history](<Country creation - Hearts of Iron 4 Wiki.md#country-history>), alternatively it can be initialised when needed, such as in a focus reward or an event option.

## Balance of power modifiers

*See also: [Modifiers § Static modifiers](<Modifiers - Hearts of Iron 4 Wiki.md#static-modifiers>)*

Balance of power modifiers are static modifiers that are applied directly to a balance of power, from which they are cloned to each country that has the BoP assigned. As static modifiers, they're defined in any /Hearts of Iron IV/common/modifiers/\*.txt file. They typically include within of themselves only the [power\_balance\_daily](<Modifiers - Hearts of Iron 4 Wiki.md#power-balance-daily>) and/or [power\_balance\_weekly](<Modifiers - Hearts of Iron 4 Wiki.md#power-balance-weekly>) modifiers in order to gradually tip the balance towards one side. These modifiers will be shown in the tooltip when hovering over the current value.

An example of a BoP modifier is as such:

```text
my_bop_modifier = {
    power_balance_weekly = -0.01 # Changes by 1% each week to the left
}
```

Balance of power modifiers are added via [the add\_power\_balance\_modifier effect](#add-power-balance-modifier) as such:

```text
add_power_balance_modifier = {
    id = my_bop    # The ID of the balance of power
    modifier = my_bop_modifier # The modifier to add
}
```

[The remove\_power\_balance\_modifier effect](#remove-power-balance-modifier), with the same syntax, or [remove\_all\_power\_balance\_modifiers](#remove-all-power-balance-modifiers) can be used to remove these from the country.

Since these are duplicated to each country that has the BoP, the weekly or daily effect for each modifier will increase for each country that is assigned the BoP. For example, if the BoP is assigned to 3 countries, `power_balance_daily = 0.01` in a BoP modifier will, in practice, make the balance get pushed by 3% to the right in total daily.

## Effects

*Parts of this section are transcluded from [Effect § Balance of power](<Effect - Hearts of Iron 4 Wiki.md#balance-of-power>).*

Other than `set_power_balance`, these effects exist which can be used to modify a balance of power:

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

## Triggers

*Parts of this section are transcluded from [Triggers § Balance of power](<Triggers - Hearts of Iron 4 Wiki.md#balance-of-power>).*

These triggers exist for checking the state of a balance of power. Some of these can only be used in country scope.

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

**[Modding](<Modding - Hearts of Iron 4 Wiki.md>)**
