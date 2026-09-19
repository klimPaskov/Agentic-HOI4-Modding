# Balance of power modding

*Offline snapshot of the Hearts of Iron IV Wiki page "Balance of power modding", captured 2026-09-19.*

## Table of contents

- [Code structure](#Code_structure)
  - [Side](#Side)
  - [Range](#Range)
  - [Example](#Example)
- [Implementation](#Implementation)
- [Balance of power modifiers](#Balance_of_power_modifiers)
- [Effects](#Effects)
- [Triggers](#Triggers)

---

A **balance of power** (also internally referred to as bop or power balance) is typically used to represent a conflict between two sides, using a progress bar divided into distinct sections and decisions to push it towards some side for benefits. These are defined in `/Hearts of Iron IV/common/bop/*.txt` files.

Each balance of power consists of 2 or more sides. While a balance of power can contain more than 2 sides, at any time the player may only see 2 which are chosen in the effect to initialise the balance of power.
To track the current balance, a single value is used, which can range from -1 to 1 with up to 3 decimal points. The `[-1;0)` range is used for the left side, `[0;1]` is used for the right side. A side having power only has a cosmetic impact, changing the icon and the text used in scripted localisation. A side isn't inherently set as being left or right, instead it is assigned which side is on which half when the power balance is initialised.

Depending on the value, the country is placed in some range representing the exact degree of power on a certain side. This is usually used to grant certain [modifiers](<Modifiers - Hearts of Iron 4 Wiki.md>) or to execute an [effect](<Effects - Hearts of Iron 4 Wiki.md>) upon entering it. Most ranges are placed inside of sides, making it only possible to enter when that side is active. A range may also not be assigned to any side and be always visible, usually used for a single "balanced" range in the middle.
A range being assigned to a side only means that it'll be visible when the range is active, and a side may have ranges on both halves of the balance at the same time. Entering a range defined on a certain side does not necessitate that the balance is tipped in favour of that side. For example, if a side is set as a left side and yet it includes a range of `[0.1,0.3)`, then if the value is at 0.2, then the balance will be tipped towards the right side visually, but it will still be inside of that range.

**A balance of power is tracked globally.** If 2 countries are assigned the same BoP, then the value of the balance will always be exactly the same between both countries. If both of these countries have modifiers pushing the BoP to some side daily or weekly, the effects of these modifiers will stack.

## Code structure <a id="Code_structure"></a>

Balances of power are created in any `/Hearts of Iron IV/common/bop/*.txt` file. A BoP is defined as a root-level block, where the name of the block determines the unique ID of the BoP. In case of duplicates, the error.log entry `Template ID duplicate: bop_name` is generated and the game will prioritise the one that was [created later](<Modding - Hearts of Iron 4 Wiki.md#Code_structure>), determined using the filename and order in files.
There are no strictly mandatory arguments, however it is preferred to have at least 2 sides as the UI is built on the assumption that there is always a left and a right side active. In particular, these arguments exist:

- `intial_value = -0.1` is the default value of the BoP. If unset, defaults to 0.
- `left_side = side_id` is the default left side of the BoP.
- `right_side = side_id` is the default right side of the BoP.

The default values are used when the BoP is first initialised with set_power_balance (unless overwritten by its arguments) or when that same effect includes `set_default = yes` to reset it.

- `decision_category = TAG_example_category` will move that decision category to the balance of power view. In particular, this ensures that it's impossible to access the decision category in any way other than by the balance of power. Any trigger blocks in the decision category, such as `allowed = { ... }`, are still checked for the country with the BoP, however.

In addition, `side = { ... }` and `range = { ... }` are possible with more detail.

### Side <a id="Side"></a>

Each side is defined using a `side = { ... }` block in the balance of power. In particular, these arguments exist:

- `id = side_id` is the identifier used for the side. There should not be overlap in the same BoP, however overlap may exist between different BoPs. In case of overlap in the same BoP, only the first-created side will be used with a `Side ID duplicate: side_id` entry in error.log.
- `icon = GFX_idea_unknown` is the spriteType used as the image to represent the side. If undefined or if the spriteType doesn't exist, the icon will not be created with no default to replace it.

**General sprite overview**

For loading GFX, the game uses the sprite system. Sprites are code definitions that attach a name to an image file, as well as optionally adding additional information, such as animation, the amount of frames, the way that the image will be loaded, and so on. This means **placing an image into the gfx folder isn't enough for it to work**, a sprite has to use that image file as well.

Sprites are defined in any `/Hearts of Iron IV/interface/*.gfx` file (this is separate from `gfx/interface/`), opened with a text editor. To create a new .gfx file, a text file can be created and renamed to change the extension (on Windows, the Windows Explorer needs to show the extensions, which it doesn't by default). In particular, sprites are defined within a `spriteTypes = { ... }` block, as to separate from fonts and map arrows also defined in that folder, while the simplest sprite with the least mandatory properties is a `spriteType = { ... }`. The simplest sprite definition looks like the following:

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

In this case, this creates a sprite with the name of `GFX_first_sprite` and attaches the `/Hearts of Iron IV/gfx/interface/folder/filename.dds` image to it, and a second sprite similarly. The second sprite will be split into 2 frames: this is decided by having the left half of the image as the first frame and the right half as the second frame (more frames would further split the image horizontally). This doesn't make the sprite animated, just turns on the option to switch between the two halves as needed. `GFX_second_sprite:1` serves as a reference to the first frame, and GUI can be set up to change the shown frame depending on context, such as with radio stations.
In order to add animation, a [frameAnimatedSpriteType](<Graphical asset modding - Hearts of Iron 4 Wiki.md#frameAnimatedSpriteType>) is used.

**It's never mandatory to copy a base game file to change a sprite**. If there are duplicate definitions of a sprite with the same name in different files, the game will prioritise the one that would be [evaluated later, based on the filename](<Modding - Hearts of Iron 4 Wiki.md#Loading_files>), and the older sprite will be ignored in entirety. This can be ensured by beginning the replacement file's name with a symbol late in the ASCII character table. Typically the lowercase letter 'z' is used for this purpose. For example, to change the amount of frames in `GFX_idea_traits_strip` to 10, it is possible to define a sprite with that name with 10 frames in the mod's `modname/interface/zz_replace.gfx` file instead of copying over the base game file.
Since most .gfx files define integral parts of the user interface, copying them over can lead to the mod's loaded files missing sprites upon a major game update, which would appear in-game as the default image, which is the error dog by default. As to ease the burden of needing to check the interface files, it's best to never copy over .gfx files, unless more additions would be actively harmful to the mod, such as with `interface/subuniticons.gfx`

- `range = { ... }` is a range set to exist if and only if that side is active.

### Range <a id="Range"></a>

A range is defined as a `range = { ... }` block which may exist either directly in the BoP or inside of a `side = { ... }`. This is used to determine when the range will be visible to the player: a range directly in a BoP is always visible, while a range in a side will only be visible if that side is visible. There are 3 mandatory attributes:

- `id = range_id` is used to assign an ID to the specified range. There shouldn't be duplicates across the entire BoP (even in different sides), but there may be between different BoPs. A duplicate will be marked with a `Range ID duplicate: range_id` entry in error.log. In this case, the game will still display each range with the same ID that is not in a disabled side. However, this can cause issues with strict non-equal comparison when using is_power_balance_in_range: in particular, the game will only recognise the range that's placed furthest to the left. For example, if there are duplicate `range_id` on intervals of `[-0.3,-0.1)` and `[0.1,0.3)`, then a strict equilibrium will be recognised as being to the right of `range_id`, but not to the left of it.
- `min = -0.1` is the minimum value in the range's interval. If the value is exactly at this point, this range will be applied.
- `max = 0.1` is the maximum value in the range's interval. If the value is exactly at this point, this range will be applied if and only if max is set to 1. Otherwise, the exact point is excluded from the interval.

There are also blocks that decide which impact exactly a range has on the country when the value is inside that. In particular:

- `modifier = { ... }` decides on the [modifiers](<Modifiers - Hearts of Iron 4 Wiki.md>) applying to the country when the value is in that range.
- `rule = { ... }` decides on the [game rules](<Effects - Hearts of Iron 4 Wiki.md>) applying to the country when the value is in that range.
- `on_activate = { ... }` executes [effects](<Effects - Hearts of Iron 4 Wiki.md>) the instant that the value enters this range.
- `on_deactivate = { ... }` executes [effects](<Effects - Hearts of Iron 4 Wiki.md>) the instant that the value exits this range.

### Example <a id="Example"></a>

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

## Implementation <a id="Implementation"></a>

As a balance of power isn't inherently assigned to any country, it must be manually initialised. This is done using the `set_power_balance` [effect](<Effects - Hearts of Iron 4 Wiki.md>). For example, this is the most bare-bones way to initialise the BoP, which will set it to the default:

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

As an effect, it can be used in any effect block. If it should be initialised at the game's start, this is usually done in [country history](<Country creation - Hearts of Iron 4 Wiki.md>), alternatively it can be initialised when needed, such as in a focus reward or an event option.

## Balance of power modifiers <a id="Balance_of_power_modifiers"></a>

*See also: [Modifiers § Static modifiers](<Modifiers - Hearts of Iron 4 Wiki.md#Static_modifiers>)*

Balance of power modifiers are [static modifiers](<Modifiers - Hearts of Iron 4 Wiki.md>) that are applied directly to a balance of power, from which they are cloned to each country that has the BoP assigned. As static modifiers, they're defined in any `/Hearts of Iron IV/common/modifiers/*.txt` file. They typically include within of themselves only the [power_balance_daily](<Modifiers - Hearts of Iron 4 Wiki.md>) and/or [power_balance_weekly](<Modifiers - Hearts of Iron 4 Wiki.md>) modifiers in order to gradually tip the balance towards one side. These modifiers will be shown in the tooltip when hovering over the current value.

An example of a BoP modifier is as such:

```text
my_bop_modifier = {
    power_balance_weekly = -0.01 # Changes by 1% each week to the left
}
```

Balance of power modifiers are added via the add_power_balance_modifier effect as such:

```text
add_power_balance_modifier = {
    id = my_bop    # The ID of the balance of power
    modifier = my_bop_modifier # The modifier to add
}
```

The remove_power_balance_modifier effect, with the same syntax, or remove_all_power_balance_modifiers can be used to remove these from the country.

Since these are duplicated to each country that has the BoP, the weekly or daily effect for each modifier will increase for each country that is assigned the BoP. For example, if the BoP is assigned to 3 countries, `power_balance_daily = 0.01` in a BoP modifier will, in practice, make the balance get pushed by 3% to the right in total daily.

## Effects <a id="Effects"></a>

*Parts of this section are transcluded from [Effect § Balance of power](<Effects - Hearts of Iron 4 Wiki.md#Balance_of_power>).*

Other than `set_power_balance`, these effects exist which can be used to modify a balance of power:

Balance of power-related country-scoped effects:

| Name | Parameters | Examples | Description | Notes | Version Added |
| --- | --- | --- | --- | --- | --- |
| remove_power_balance | `id = <BoP ID>`<br>Balance of power to modify. | `remove_power_balance = {`<br>`    id = my_bop`<br>`}` | Removes the balance of power in entirety. |  | 1.12 |
| add_power_balance_value | `id = <BoP ID>`<br>Balance of power to modify.<br> `value = <decimal>`<br>The value to add.<br> `tooltip_side = <BoP side ID>`<br>The side to show in the tooltip. Optional.<br> | `add_power_balance_value = {`<br>`    id = my_bop`<br>`    value = -0.1`<br>`    tooltip_side = my_bop_side`<br>`}` | Pushes the balance of power towards one side. |  | 1.12 |
| add_power_balance_modifier | `id = <BoP ID>`<br>Balance of power to modify.<br> `modifier = <static modifier>`<br>The [static modifier](<Modifiers - Hearts of Iron 4 Wiki.md>) to apply. | `add_power_balance_modifier = {`<br>`    id = my_bop`<br>`    modifier = my_static_modifier`<br>`}` | Applies a balance of power modifier. |  | 1.12 |
| remove_power_balance_modifier | `id = <BoP ID>`<br>Balance of power to modify.<br> `modifier = <static modifier>`<br>The [static modifier](<Modifiers - Hearts of Iron 4 Wiki.md>) to apply. | `remove_power_balance_modifier = {`<br>`    id = my_bop`<br>`    modifier = my_static_modifier`<br>`}` | Cancels a balance of power modifier. |  | 1.12 |
| remove_all_power_balance_modifiers | `id = <BoP ID>`<br>Balance of power to modify. | `remove_all_power_balance_modifiers = {`<br>`    id = my_bop`<br>`}` | Cancels all balance of power modifiers. |  | 1.12 |
| set_power_balance_gfx | `id = <BoP ID>`<br>Balance of power to modify.<br> `side = <BoP side ID>`<br>The side whose GFX to change.<br> `gfx = <sprite>`<br>The sprite to change the GFX to. | `set_power_balance_gfx = {`<br>`    id = my_bop`<br>`    side = my_bop_side`<br>`    gfx = GFX_my_bop_side_new`<br>`}` | Changes the appearance of one of the sides within the balance of power. | Sprites are defined within `/Hearts of Iron IV/interface/*.gfx` files. | 1.12 |

## Triggers <a id="Triggers"></a>

*Parts of this section are transcluded from [Triggers § Balance of power](<Triggers - Hearts of Iron 4 Wiki.md#Balance_of_power>).*

These triggers exist for checking the state of a balance of power. Some of these can only be used in country scope.

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

---

## Navigation

**[Modding](<Modding - Hearts of Iron 4 Wiki.md>)**

- **Documentation**: [Effects](<Effects - Hearts of Iron 4 Wiki.md>) • [Triggers](<Triggers - Hearts of Iron 4 Wiki.md>) • [Defines](<Defines - Hearts of Iron 4 Wiki.md>) • [Modifiers](<Modifiers - Hearts of Iron 4 Wiki.md>) • [List of modifiers](<List of modifiers - Hearts of Iron 4 Wiki.md>) • [Scopes](<Scopes - Hearts of Iron 4 Wiki.md>) • [Localisation](<Localisation - Hearts of Iron 4 Wiki.md>) • [On actions](<On actions - Hearts of Iron 4 Wiki.md>) • [Data structures](<Data structures - Hearts of Iron 4 Wiki.md>) • [Flags](<Data structures - Hearts of Iron 4 Wiki.md#Flags>) • [Event targets](<Data structures - Hearts of Iron 4 Wiki.md#Event_targets>) • [Country tag aliases](<Data structures - Hearts of Iron 4 Wiki.md#Country_tag_aliases>) • [Variables](<Data structures - Hearts of Iron 4 Wiki.md#Variables>) • [Arrays](<Data structures - Hearts of Iron 4 Wiki.md#Arrays>)
- **Scripting**: [Achievements](<Achievement modding - Hearts of Iron 4 Wiki.md>) • [AI](<AI modding - Hearts of Iron 4 Wiki.md>) • [AI focuses](<AI focuses - Hearts of Iron 4 Wiki.md>) • [Autonomous states](<Autonomy state modding - Hearts of Iron 4 Wiki.md>) • [Bookmarks/Scenarios](<Bookmark modding - Hearts of Iron 4 Wiki.md>) • [Game rules](<Bookmark modding - Hearts of Iron 4 Wiki.md#Game_rules>) • [Buildings](<Building modding - Hearts of Iron 4 Wiki.md>) • [Characters and traits](<Character modding - Hearts of Iron 4 Wiki.md>) • [Cosmetic tags](<Cosmetic tag modding - Hearts of Iron 4 Wiki.md>) • [Countries](<Country creation - Hearts of Iron 4 Wiki.md>) • [Divisions](<Division modding - Hearts of Iron 4 Wiki.md>) • [Decisions](<Decision modding - Hearts of Iron 4 Wiki.md>) • [Doctrines](<Doctrine modding - Hearts of Iron 4 Wiki.md>) • [Equipment](<Equipment modding - Hearts of Iron 4 Wiki.md>) • [Events](<Event modding - Hearts of Iron 4 Wiki.md>) • [Factions](<Faction modding - Hearts of Iron 4 Wiki.md>) • [Ideas](<Idea modding - Hearts of Iron 4 Wiki.md>) • [Ideologies](<Ideology modding - Hearts of Iron 4 Wiki.md>) • [Military industrial organizations](<Military industrial organization modding - Hearts of Iron 4 Wiki.md>) • [National focuses](<National focus modding - Hearts of Iron 4 Wiki.md>) • [Resources](<Resources modding - Hearts of Iron 4 Wiki.md>) • [Scripted GUI](<Scripted GUI modding - Hearts of Iron 4 Wiki.md>) • [Technologies and doctrines](<Technology modding - Hearts of Iron 4 Wiki.md>) • [Units](<Unit modding - Hearts of Iron 4 Wiki.md>)
- **Map**: [Map](<Map modding - Hearts of Iron 4 Wiki.md>) • [States](<State modding - Hearts of Iron 4 Wiki.md>) • [Supply areas](<Supply areas modding - Hearts of Iron 4 Wiki.md>) • [Strategic regions](<Strategic region modding - Hearts of Iron 4 Wiki.md>)
- **Graphical**: [Interface](<Interface modding - Hearts of Iron 4 Wiki.md>) • [Graphical assets](<Graphical asset modding - Hearts of Iron 4 Wiki.md>) • [Entities](<Entity modding - Hearts of Iron 4 Wiki.md>) • [Posteffects](<Posteffect modding - Hearts of Iron 4 Wiki.md>) • [Particles](<Particle modding - Hearts of Iron 4 Wiki.md>) • [Fonts](<Font modding - Hearts of Iron 4 Wiki.md>)
- **Cosmetic**: [Portraits](<Portrait modding - Hearts of Iron 4 Wiki.md>) • [Namelists](<Namelist modding - Hearts of Iron 4 Wiki.md>) • [Music](<Music modding - Hearts of Iron 4 Wiki.md>) • [Sound](<Sound modding - Hearts of Iron 4 Wiki.md>)
- **Other**: [Console commands](<Console commands - Hearts of Iron 4 Wiki.md>) • [Troubleshooting](<Troubleshooting - Hearts of Iron 4 Wiki.md>) • [Mod structure](<Mod structure - Hearts of Iron 4 Wiki.md>) • [Mods](<Mods - Hearts of Iron 4 Wiki.md>) • [Nudger](<Nudger - Hearts of Iron 4 Wiki.md>)
