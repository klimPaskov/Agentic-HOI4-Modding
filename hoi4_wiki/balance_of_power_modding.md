# Balance of power modding

*Offline snapshot of the Hearts of Iron IV Wiki page "Balance of power modding", revision 67049, captured 2026-10-31. Wiki text by the wiki's contributors under CC BY-SA 3.0 (see LICENSE.txt); kit blocks are local additions under the same license.*

<!-- kit:begin id="review" at="top" build="1.19.4.1" checked="2026-11-01" revision="67049" sources="common/bop/ documentation/loc_objects_documentation.md common/modifiers/ common/decisions/ localisation/english/Juno_bop_l_english.yml localisation/english/bba_bop_l_english.yml documentation/effects_documentation.md documentation/triggers_documentation.md documentation/modifiers_documentation.md documentation/dynamic_variables_documentation.md" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Checked against: all 10 vanilla files in `common/bop/` (including `_test.txt`), every BoP effect, trigger, modifier and dynamic variable in the documentation, and vanilla use of each.
- Kit blocks added: `bop-initial-value-typo`, `bop-vanilla-format`, `bop-example-rule-fix`, `bop-variables-and-modifiers`, `bop-scopes-and-operators`, `bop-triggers-1193` (bottom).
- Errors found: `intial_value` (typo) and `can_create_faction` (the rule is `can_create_factions`) in wiki examples; no vanilla range uses `rule`; the "tracked globally" claim held in a game run on 2026-11-02 (see the kit section at the bottom).
- Gaps left: the clamping of `add_power_balance_value` beyond -1 and 1 and the exact end-point rule for `max` are not documented; the wiki's version column (1.12) was not re-checked.
**1.19.4.1 re-check (2026-11-01).** Seven statements depended on files the update changed (the vanilla decision, focus, scripted effect and static modifier files), and all seven were re-measured. Two facts changed: `tooltip_side = ITA_communism_side` now appears 6 times in the Italian scripted effects (was 3), and the two `SWI_DEBUG_*` BoP modifiers have no loc key. Every other statement cites files that are byte-identical in 1.19.4.1 (Steam depot manifest diff).
<!-- kit:end id="review" -->

## Table of contents

- [Code structure](#Code_structure)
  - [Side](#Side)
  - [Range](#Range)
  - [Example](#Example)
- [Implementation](#Implementation)
- [Balance of power modifiers](#Balance_of_power_modifiers)
- [Effects](#Effects)
- [Triggers](#Triggers)
- [Kit: Balance of power triggers, scopes and the global claim](#kit-bop-triggers)

---

A **balance of power** (also internally referred to as bop or power balance) is typically used to represent a conflict between two sides, using a progress bar divided into distinct sections and decisions to push it towards some side for benefits. These are defined in `/Hearts of Iron IV/common/bop/*.txt` files.

Each balance of power consists of 2 or more sides. While a balance of power can contain more than 2 sides, at any time the player may only see 2 which are chosen in the effect to initialise the balance of power.
To track the current balance, a single value is used, which can range from -1 to 1 with up to 3 decimal points. The `[-1;0)` range is used for the left side, `[0;1]` is used for the right side. A side having power only has a cosmetic impact, changing the icon and the text used in scripted localisation. A side isn't inherently set as being left or right, instead it is assigned which side is on which half when the power balance is initialised.

Depending on the value, the country is placed in some range representing the exact degree of power on a certain side. This is usually used to grant certain [modifiers](<modifiers.md>) or to execute an [effect](<effects.md>) upon entering it. Most ranges are placed inside of sides, making it only possible to enter when that side is active. A range may also not be assigned to any side and be always visible, usually used for a single "balanced" range in the middle.
A range being assigned to a side only means that it'll be visible when the range is active, and a side may have ranges on both halves of the balance at the same time. Entering a range defined on a certain side does not necessitate that the balance is tipped in favour of that side. For example, if a side is set as a left side and yet it includes a range of `[0.1,0.3)`, then if the value is at 0.2, then the balance will be tipped towards the right side visually, but it will still be inside of that range.

**A balance of power is tracked globally.** If 2 countries are assigned the same BoP, then the value of the balance will always be exactly the same between both countries. If both of these countries have modifiers pushing the BoP to some side daily or weekly, the effects of these modifiers will stack.

## Code structure <a id="Code_structure"></a>

Balances of power are created in any `/Hearts of Iron IV/common/bop/*.txt` file. A BoP is defined as a root-level block, where the name of the block determines the unique ID of the BoP. In case of duplicates, the error.log entry `Template ID duplicate: bop_name` is generated and the game will prioritise the one that was [created later](<modding.md#Code_structure>), determined using the filename and order in files.
There are no strictly mandatory arguments, however it is preferred to have at least 2 sides as the UI is built on the assumption that there is always a left and a right side active. In particular, these arguments exist:

- `intial_value = -0.1` is the default value of the BoP. If unset, defaults to 0.
- `left_side = side_id` is the default left side of the BoP.
- `right_side = side_id` is the default right side of the BoP.

The default values are used when the BoP is first initialised with set_power_balance (unless overwritten by its arguments) or when that same effect includes `set_default = yes` to reset it.

- `decision_category = TAG_example_category` will move that decision category to the balance of power view. In particular, this ensures that it's impossible to access the decision category in any way other than by the balance of power. Any trigger blocks in the decision category, such as `allowed = { ... }`, are still checked for the country with the BoP, however.

In addition, `side = { ... }` and `range = { ... }` are possible with more detail.

<!-- kit:begin id="bop-initial-value-typo" at="section:Code_structure" -->
**Kit correction** The first bullet above misspells the key. It is `initial_value` (11 BoP blocks in vanilla use it, including the wiki's own example and `_test.txt`); A misspelled `intial_value` is most likely ignored, leaving the start value at 0 [unverified]. [vanilla-confirmed 1.19.3] `common/bop/*.txt`.
<!-- kit:end id="bop-initial-value-typo" -->

<!-- kit:begin id="bop-vanilla-format" at="section:Code_structure" -->
**Kit note** What the 10 vanilla BoP files use in 1.19.4.1. All lines: [vanilla-confirmed 1.19.4.1] `common/bop/*.txt` (parsed by script) and `localisation/english/Juno_bop_l_english.yml`, `bba_bop_l_english.yml`.

- Root block keys: `initial_value`, `left_side`, `right_side`, `decision_category`, `side`, `range`. Side keys: `id`, `icon`, `range`. Range keys: `id`, `min`, `max`, `modifier`, `on_activate`, `on_deactivate`. No vanilla range sets `rule`. [vanilla-confirmed 1.19.4.1] `common/bop/*.txt` (10 files). The loc object `GetActiveRangeRuleDesc` implies that a range can carry a rule. [docs] `documentation/loc_objects_documentation.md`. That a `rule = { ... }` block inside a range takes effect is [unverified].
- Vanilla has 10 BoPs (`BRA`, `CZE`, `DEN` twice, `ETH`, `FIN`, `ITA`, `PRC`, `SWE`, `SWI`), plus `_test_balance` in `_test.txt`, which is the wiki's example without `decision_category` and `rule`. Sides per BoP: 2 for most (both `DEN` BoPs included), 3 for `PRC`, 4 for `ETH`, 9 for `ITA`. So a BoP really can hold more sides than the two shown.
- Neighbouring ranges share their boundary value (for example -1 to -0.7, -0.7 to -0.4, -0.4 to -0.1), and the middle range sits directly in the BoP, outside any side.
- `on_activate` and `on_deactivate` are effect blocks; 135 of the 218 vanilla ones are empty. The 83 filled ones swap ideas (`swap_ideas` with `add_idea` and `remove_idea`, 23 blocks), set variables (22), call `promote_character` (10) and `log` (4), and in 38 blocks call `set_power_balance_gfx` to change a side's icon. `promote_character` is documented for country and character scope. [docs] `documentation/effects_documentation.md`. That the block runs in the owner country's scope is [unverified].
- Every id needs a loc entry of the same name: the BoP id, each side id, each range id and the decision category id (`BRA_political_military_balance`, `BRA_bop_left_side`, `BRA_unstable_government`, `BRA_balance_of_power_category` in `Juno_bop_l_english.yml`).
- `BRA_political_military_balance` is referenced only by its own file and its loc, and its `decision_category` `BRA_balance_of_power_category` is defined in no decision file: a vanilla leftover, not a pattern to copy.
<!-- kit:end id="bop-vanilla-format" -->

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
In order to add animation, a [frameAnimatedSpriteType](<graphical_asset_modding.md#frameAnimatedSpriteType>) is used.

**It's never mandatory to copy a base game file to change a sprite**. If there are duplicate definitions of a sprite with the same name in different files, the game will prioritise the one that would be [evaluated later, based on the filename](<modding.md#Loading_files>), and the older sprite will be ignored in entirety. This can be ensured by beginning the replacement file's name with a symbol late in the ASCII character table. Typically the lowercase letter 'z' is used for this purpose. For example, to change the amount of frames in `GFX_idea_traits_strip` to 10, it is possible to define a sprite with that name with 10 frames in the mod's `modname/interface/zz_replace.gfx` file instead of copying over the base game file.
Since most .gfx files define integral parts of the user interface, copying them over can lead to the mod's loaded files missing sprites upon a major game update, which would appear in-game as the default image, which is the error dog by default. As to ease the burden of needing to check the interface files, it's best to never copy over .gfx files, unless more additions would be actively harmful to the mod, such as with `interface/subuniticons.gfx`

- `range = { ... }` is a range set to exist if and only if that side is active.

### Range <a id="Range"></a>

A range is defined as a `range = { ... }` block which may exist either directly in the BoP or inside of a `side = { ... }`. This is used to determine when the range will be visible to the player: a range directly in a BoP is always visible, while a range in a side will only be visible if that side is visible. There are 3 mandatory attributes:

- `id = range_id` is used to assign an ID to the specified range. There shouldn't be duplicates across the entire BoP (even in different sides), but there may be between different BoPs. A duplicate will be marked with a `Range ID duplicate: range_id` entry in error.log. In this case, the game will still display each range with the same ID that is not in a disabled side. However, this can cause issues with strict non-equal comparison when using is_power_balance_in_range: in particular, the game will only recognise the range that's placed furthest to the left. For example, if there are duplicate `range_id` on intervals of `[-0.3,-0.1)` and `[0.1,0.3)`, then a strict equilibrium will be recognised as being to the right of `range_id`, but not to the left of it.
- `min = -0.1` is the minimum value in the range's interval. If the value is exactly at this point, this range will be applied.
- `max = 0.1` is the maximum value in the range's interval. If the value is exactly at this point, this range will be applied if and only if max is set to 1. Otherwise, the exact point is excluded from the interval.

There are also blocks that decide which impact exactly a range has on the country when the value is inside that. In particular:

- `modifier = { ... }` decides on the [modifiers](<modifiers.md>) applying to the country when the value is in that range.
- `rule = { ... }` decides on the [game rules](<effects.md>) applying to the country when the value is in that range.
- `on_activate = { ... }` executes [effects](<effects.md>) the instant that the value enters this range.
- `on_deactivate = { ... }` executes [effects](<effects.md>) the instant that the value exits this range.

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

<!-- kit:begin id="bop-example-rule-fix" at="section:Example" -->
**Kit correction** The example's `can_create_faction = yes` is not a rule. The game rule is `can_create_factions` (plural), used in vanilla and listed in the rule table of [Autonomy state modding](<autonomy_state_modding.md>). [vanilla-confirmed 1.19.4.1] `common/`, searched by script. A misspelled rule name is most likely ignored without an error [unverified].
<!-- kit:end id="bop-example-rule-fix" -->

## Implementation <a id="Implementation"></a>

As a balance of power isn't inherently assigned to any country, it must be manually initialised. This is done using the `set_power_balance` [effect](<effects.md>). For example, this is the most bare-bones way to initialise the BoP, which will set it to the default:

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

As an effect, it can be used in any effect block. If it should be initialised at the game's start, this is usually done in [country history](<country_creation.md>), alternatively it can be initialised when needed, such as in a focus reward or an event option.

## Balance of power modifiers <a id="Balance_of_power_modifiers"></a>

*See also: [Modifiers § Static modifiers](<modifiers.md#Static_modifiers>)*

Balance of power modifiers are [static modifiers](<modifiers.md>) that are applied directly to a balance of power, from which they are cloned to each country that has the BoP assigned. As static modifiers, they're defined in any `/Hearts of Iron IV/common/modifiers/*.txt` file. They typically include within of themselves only the [power_balance_daily](<modifiers.md>) and/or [power_balance_weekly](<modifiers.md>) modifiers in order to gradually tip the balance towards one side. These modifiers will be shown in the tooltip when hovering over the current value.

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

<!-- kit:begin id="bop-variables-and-modifiers" at="section:Balance_of_power_modifiers" -->
**Kit addition** Facts about the modifier side of a BoP in 1.19.4.1.

- `power_balance_daily` and `power_balance_weekly` are country modifiers with two decimals. [docs] `documentation/modifiers_documentation.md`.
- Vanilla keeps BoP modifiers in `common/modifiers/` (`AAT_power_balance_modifiers.txt`, `BBA_power_balance_modifiers.txt`, `MUN_power_balance_modifiers.txt`) and gives each a loc key of the same name, which the tooltip shows (`FIN_bop_modifier_eradicate_socialism` in `aat_bop_l_english.yml`). The two `SWI_DEBUG_*` entries in the BBA file have no loc key. `00_static_modifiers.txt` holds a test one, `_test_power_balance_mod = { power_balance_daily = 0.02 }`. [vanilla-confirmed 1.19.4.1] files named.
- `power_balance_weekly` can also be driven by a variable inside a dynamic modifier: `power_balance_weekly = DEN_resistance_power_balance_weekly` in `common/dynamic_modifiers/aat_dynamic_modifiers.txt`. This pushes the balance without a static BoP modifier. [vanilla-confirmed 1.19.3] `common/dynamic_modifiers/aat_dynamic_modifiers.txt`.
- Three dynamic variables read the country's active BoP: `power_balance_value` (current value), `power_balance_daily` and `power_balance_weekly` (current total change). Vanilla reads the value with `set_temp_variable = { fascism_to_add = power_balance_value }` after `has_power_balance`. [docs] `documentation/dynamic_variables_documentation.md`; [vanilla-confirmed 1.19.4.1] `common/national_focus/czechoslovakia_mu.txt`.
<!-- kit:end id="bop-variables-and-modifiers" -->

## Effects <a id="Effects"></a>

*Parts of this section are transcluded from [Effect § Balance of power](<effects.md#Balance_of_power>).*

Other than `set_power_balance`, these effects exist which can be used to modify a balance of power:

Balance of power-related country-scoped effects:

| Name | Parameters | Examples | Description | Notes | Version Added |
| --- | --- | --- | --- | --- | --- |
| remove_power_balance | `id = <BoP ID>`<br>Balance of power to modify. | *(example below)* | Removes the balance of power in entirety. |  | 1.12 |
| add_power_balance_value | `id = <BoP ID>`<br>Balance of power to modify.<br> `value = <decimal>`<br>The value to add.<br> `tooltip_side = <BoP side ID>`<br>The side to show in the tooltip. Optional.<br> | *(example below)* | Pushes the balance of power towards one side. |  | 1.12 |
| add_power_balance_modifier | `id = <BoP ID>`<br>Balance of power to modify.<br> `modifier = <static modifier>`<br>The [static modifier](<modifiers.md>) to apply. | *(example below)* | Applies a balance of power modifier. |  | 1.12 |
| remove_power_balance_modifier | `id = <BoP ID>`<br>Balance of power to modify.<br> `modifier = <static modifier>`<br>The [static modifier](<modifiers.md>) to apply. | *(example below)* | Cancels a balance of power modifier. |  | 1.12 |
| remove_all_power_balance_modifiers | `id = <BoP ID>`<br>Balance of power to modify. | *(example below)* | Cancels all balance of power modifiers. |  | 1.12 |
| set_power_balance_gfx | `id = <BoP ID>`<br>Balance of power to modify.<br> `side = <BoP side ID>`<br>The side whose GFX to change.<br> `gfx = <sprite>`<br>The sprite to change the GFX to. | *(example below)* | Changes the appearance of one of the sides within the balance of power. | Sprites are defined within `/Hearts of Iron IV/interface/*.gfx` files. | 1.12 |

**Example: remove_power_balance**

```text
remove_power_balance = {
    id = my_bop
}
```

**Example: add_power_balance_value**

```text
add_power_balance_value = {
    id = my_bop
    value = -0.1
    tooltip_side = my_bop_side
}
```

**Example: add_power_balance_modifier**

```text
add_power_balance_modifier = {
    id = my_bop
    modifier = my_static_modifier
}
```

**Example: remove_power_balance_modifier**

```text
remove_power_balance_modifier = {
    id = my_bop
    modifier = my_static_modifier
}
```

**Example: remove_all_power_balance_modifiers**

```text
remove_all_power_balance_modifiers = {
    id = my_bop
}
```

**Example: set_power_balance_gfx**

```text
set_power_balance_gfx = {
    id = my_bop
    side = my_bop_side
    gfx = GFX_my_bop_side_new
}
```

<!-- kit:begin id="bop-scopes-and-operators" at="section:Effects" -->
**Kit addition** Scopes and the parameters of `set_power_balance` in 1.19.3. All lines: [docs] `documentation/effects_documentation.md`.

| Effect | Scope | Parameters |
| --- | --- | --- |
| `set_power_balance` | country only | `id`, `left_side`, `right_side`, `set_default` (default no; yes resets to `initial_value`), `set_value` (sets the value when present) |
| `remove_power_balance` | country only | `id` |
| `add_power_balance_value` | any | `id`, `value` (added to the current value), `tooltip_side` (optional, names a side in the tooltip) |
| `add_power_balance_modifier`, `remove_power_balance_modifier` | any | `id`, `modifier` (a static modifier) |
| `remove_all_power_balance_modifiers` | any | `id` |
| `set_power_balance_gfx` | any | `id`, `side`, `gfx` |

Vanilla starts a BoP in a country's history with `set_power_balance = { id = FIN_power_balance left_side = FIN_bad_side right_side = FIN_good_side set_value = -0.45 }`, and resets one with `set_default = yes` (`SWI_centralization_bop` in `common/national_focus/switzerland.txt`). `tooltip_side = ITA_communism_side` appears 6 times in `common/scripted_effects/ITA_scripted_effects.txt`. [vanilla-confirmed 1.19.4.1] `history/countries/FIN - Finland.txt`, `common/national_focus/switzerland.txt`, `common/scripted_effects/ITA_scripted_effects.txt`.
<!-- kit:end id="bop-scopes-and-operators" -->

## Triggers <a id="Triggers"></a>

*Parts of this section are transcluded from [Triggers § Balance of power](<triggers.md#Balance_of_power>).*

These triggers exist for checking the state of a balance of power. Some of these can only be used in country scope.

Balance of power-related country-scoped triggers:

| Name | Parameters | Examples | Description | Notes | Version Added |
| --- | --- | --- | --- | --- | --- |
| has_power_balance | `id = <bop ID>`<br>The balance to check for. | *(example below)* | Checks if the current scope has the specified balance of power active. |  | 1.12 |
| has_any_power_balance | `<bool>`<br>Boolean. | `has_any_power_balance = yes` | Checks if the current scope has any balance of power active. |  | 1.12 |
| power_balance_value | `id = <bop ID>`<br>The balance to check in.<br> `value = <float>`<br>The value to check for. | *(example below)* | Checks if the current scope has the specified value within the balance of power. | Either =, >, or < operators are allowed. | 1.12 |
| power_balance_daily_change | `id = <bop ID>`<br>The balance to check in.<br> `value = <float>`<br>The value to check for. | *(example below)* | Checks if the current scope's balance of power changes each day by the specified value. | Either =, >, or < operators are allowed. | 1.12 |
| power_balance_weekly_change | `id = <bop ID>`<br>The balance to check in.<br> `value = <float>`<br>The value to check for. | *(example below)* | Checks if the current scope's balance of power changes each week by the specified value. | Either =, >, or < operators are allowed. | 1.12 |
| is_power_balance_in_range | `id = <bop ID>`<br>The balance to check in.<br> `range = <range ID>`<br>The range to check for. | *(example below)* | Checks if the current scope's balance of power value lies within the specified range. | Ranges are defined within the balance of power. Can use either =, >, and < operators. In case of > or <, the comparison is 'strict', i.e. excluding the range itself. | 1.12 |
| is_power_balance_side_active | `id = <bop ID>`<br>The balance to check in.<br> `side = <side ID>`<br>The side to check. | *(example below)* | Checks if the specified balance of power has a side active. | Sides are defined within the balance of power. "Active" means that the side is among those that are currently visible instead of relying on the current value. | 1.12 |
| has_power_balance_modifier | `id = <bop ID>`<br>The balance to check in.<br> `modifier = <modifier ID>`<br>The [static modifier](<modifiers.md>). | *(example below)* | Checks if the current scope's balance of power value activates a modifier. | BoP modifiers are defined within `/Hearts of Iron IV/common/modifiers/*.txt` files, while they're activated in the balance of power definition. | 1.12 |

**Example: has_power_balance**

```text
has_power_balance = {
    id = TAG_my_bop
}
```

**Example: power_balance_value**

```text
power_balance_value = {
    id = TAG_my_bop
    value > 0.7
}
```

**Example: power_balance_daily_change**

```text
power_balance_daily_change = {
    id = TAG_my_bop
    value < -0.01
}
```

**Example: power_balance_weekly_change**

```text
power_balance_weekly_change = {
    id = TAG_my_bop
    value < -0.01
}
```

**Example: is_power_balance_in_range**

```text
is_power_balance_in_range = {
    id = TAG_my_bop
    range > TAG_my_bop_right_range
}
```

**Example: is_power_balance_side_active**

```text
is_power_balance_side_active = {
    id = TAG_my_bop
    side = TAG_my_bop_right_range
}
```

**Example: has_power_balance_modifier**

```text
has_power_balance_modifier = {
    id = TAG_my_bop
    modifier = TAG_my_bop_modifier
}
```

<!-- kit:begin id="bop-triggers-1193" at="bottom" -->
## Kit: Balance of power triggers, scopes and the global claim <a id="kit-bop-triggers"></a>

Scopes of the BoP triggers, from the documentation: `has_power_balance` and `has_any_power_balance` are country-scope only; `power_balance_value`, `power_balance_daily_change`, `power_balance_weekly_change`, `is_power_balance_in_range`, `is_power_balance_side_active` and `has_power_balance_modifier` are documented for any scope, but read the BoP of the country in scope. The three value triggers accept `>`, `<` and `=` on `value`. [docs] `documentation/triggers_documentation.md`.

- Vanilla also writes `range < SWI_centralization_bop_balanced` and `range > ...` in `is_power_balance_in_range`, so the strict comparison form on `range` is real. A plain `range = <id>` is the documented form. [vanilla-confirmed 1.19.4.1] `common/decisions/SWI.txt`, `common/national_focus/switzerland.txt`.
- The `side` argument of `is_power_balance_side_active` is a side id, for example `side = FIN_good_side`. The wiki example passes a name ending in `_right_range`, which reads like a range id; a range id is not a side. [vanilla-confirmed 1.19.3] `common/on_actions/09_aat_on_actions.txt`, `common/bop/FIN.txt`.
- Vanilla guards reads with `has_power_balance = { id = X }` when the BoP may not be active yet, for example before reading `power_balance_value` in `common/national_focus/czechoslovakia_mu.txt`. [vanilla-confirmed 1.19.4.1]
- The introduction says a BoP is "tracked globally" and identical in all countries that have it. The documentation words it per country: `set_power_balance` sets the "active power balance for country", `remove_power_balance` removes it "from country", `has_power_balance` is country scope, and the dynamic variables `power_balance_value`, `power_balance_daily` and `power_balance_weekly` are country scope. Vanilla starts each BoP in one country's history. [docs] `documentation/effects_documentation.md`, `documentation/triggers_documentation.md`, `documentation/dynamic_variables_documentation.md`. The global claim holds in the game: DEN starts with `DEN_balance_of_power` (welfare low range) and GER has none. As GER, `bop_set DEN_balance_of_power` activated it at 0 and `bop_add DEN_balance_of_power 0.3` moved it to 0.3, and DEN then read 0.3 as well (warfare medium range). `has_power_balance` and `power_balance_value > 0.2` were true for both DEN and GER, so one value per id is shared. [game-tested 1.19.4.1] HOI4 Live Tools run, 2026-11-02, console commands and trigger checks with Arms Against Tyranny active. In a run without any DLC, DEN had no balance at all.
<!-- kit:end id="bop-triggers-1193" -->

---

## Navigation

**[Modding](<modding.md>)**

- **Documentation**: [Effects](<effects.md>) • [Triggers](<triggers.md>) • [Defines](<defines.md>) • [Modifiers](<modifiers.md>) • [List of modifiers](<list_of_modifiers.md>) • [Scopes](<scopes.md>) • [Localisation](<localisation.md>) • [On actions](<on_actions.md>) • [Data structures](<data_structures.md>) • [Flags](<data_structures.md#Flags>) • [Event targets](<data_structures.md#Event_targets>) • [Country tag aliases](<data_structures.md#Country_tag_aliases>) • [Variables](<data_structures.md#Variables>) • [Arrays](<data_structures.md#Arrays>)
- **Scripting**: [Achievements](<achievement_modding.md>) • [AI](<ai_modding.md>) • [AI focuses](<ai_focuses.md>) • [Autonomous states](<autonomy_state_modding.md>) • [Bookmarks/Scenarios](<bookmark_modding.md>) • [Game rules](<bookmark_modding.md#Game_rules>) • [Buildings](<building_modding.md>) • [Characters and traits](<character_modding.md>) • [Cosmetic tags](<cosmetic_tag_modding.md>) • [Countries](<country_creation.md>) • [Divisions](<division_modding.md>) • [Decisions](<decision_modding.md>) • [Doctrines](<doctrine_modding.md>) • [Equipment](<equipment_modding.md>) • [Events](<event_modding.md>) • [Factions](<faction_modding.md>) • [Ideas](<idea_modding.md>) • [Ideologies](<ideology_modding.md>) • [Military industrial organizations](<military_industrial_organization_modding.md>) • [National focuses](<national_focus_modding.md>) • [Resources](<resources_modding.md>) • [Scripted GUI](<scripted_gui_modding.md>) • [Technologies and doctrines](<technology_modding.md>) • [Units](<unit_modding.md>)
- **Map**: [Map](<map_modding.md>) • [States](<state_modding.md>) • [Supply areas](<supply_areas_modding.md>) • [Strategic regions](<strategic_region_modding.md>)
- **Graphical**: [Interface](<interface_modding.md>) • [Graphical assets](<graphical_asset_modding.md>) • [Entities](<entity_modding.md>) • [Posteffects](<posteffect_modding.md>) • [Particles](<particle_modding.md>) • [Fonts](<font_modding.md>)
- **Cosmetic**: [Portraits](<portrait_modding.md>) • [Namelists](<namelist_modding.md>) • [Music](<music_modding.md>) • [Sound](<sound_modding.md>)
- **Other**: [Console commands](<console_commands.md>) • [Troubleshooting](<troubleshooting.md>) • [Mod structure](<mod_structure.md>) • [Mods](<mods.md>) • [Nudger](<nudger.md>)
- **Kit pages (not on the wiki)**: [Collection modding](<collection_modding.md>) • [Defines additions](<defines_additions.md>) • [Game rule modding](<game_rule_modding.md>) • [Intelligence operation modding](<intelligence_operation_modding.md>) • [Map mode modding](<map_mode_modding.md>) • [Occupation and resistance modding](<occupation_and_resistance_modding.md>) • [Peace conference modding](<peace_conference_modding.md>) • [Raid modding](<raid_modding.md>) • [Script constant modding](<script_constant_modding.md>) • [Special project modding](<special_project_modding.md>)
