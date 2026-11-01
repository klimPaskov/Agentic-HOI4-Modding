# National focus modding

*Offline snapshot of the Hearts of Iron IV Wiki page "National focus modding", revision 105626, captured 2026-10-31. Wiki text by the wiki's contributors under CC BY-SA 3.0 (see LICENSE.txt); kit blocks are local additions under the same license.*

<!-- kit:begin id="review" at="top" build="1.19.4.1" checked="2026-11-01" revision="105626" sources="common/national_focus/ common/continuous_focus/ common/focus_inlay_windows/ common/ai_strategy_plans/ common/technology_tags/ common/defines/00_defines.lua documentation/effects_documentation.md documentation/triggers_documentation.md documentation/console_commands_documentation.md documentation/modifiers_documentation.md interface/nationalfocusview.gfx localisation/english/core_l_english.yml localisation/english/focus_filter_tag_l_english.yml hoi4.exe" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Checked against: all 81 files in `common/national_focus/` (67 trees, 10,333 focuses, 335 shared and 280 joint focuses), `common/continuous_focus/`, the 7 inlay windows and their `documentation.md`, `common/ai_strategy_plans/`, the focus effects and triggers in `documentation/`, the focus defines, and error strings in `hoi4.exe`.
- Kit blocks added: tree and shortcut keys, a corrected inlay window format and declaration, prerequisite, exclusivity and relative position rules, cost units, icon extras, search filters missing from the table, trigger and bypass keys, focus effects (`load_focus_tree`, `add_tech_bonus`), shared and joint focus facts, continuous focus palettes, AI strategy plan keys.
- Errors found in the wiki text: the inlay window example is missing a closing brace and the average tree example has `tag = 25` where `add = 25` is meant; the search filter table lacks three real filters; the wiki's `advisor_portrait`, `gfx_name_fallback`, `inlay_window_id`, `BHR_*` names are placeholders.
- Gaps left: the `on_uncomplete` focus key (mentioned by the `uncomplete_national_focus` entry, used by no focus), the `allowed_is_joint` key and `copy_completed_from` are named by the game but not used in a way that shows their effect; the wiki sentence under `joint_trigger` is cut off in the captured text.
**1.19.4.1 re-check (2026-11-01).** About 55 statements depended on files the update changed (the 59 changed focus files, the AI strategy plans, the technology categories, two English loc files and the vanilla-wide effect counts), and all were re-measured. Numbers that moved: tree focuses 10,333 to 10,341, `prerequisite` blocks 10,901 to 10,912, `mutually_exclusive` entries 2,612 to 2,614, the cost, search filter and availability key counts, `complete_national_focus` 3,152 to 3,150 and `add_tech_bonus` 1,948 to 1,946 (the `technology` count is now 78). Every other statement cites files that are byte-identical in 1.19.4.1 (Steam depot manifest diff).
<!-- kit:end id="review" -->

## Table of contents

- [Focus tree](#Focus_tree)
  - [Examples](#Examples)
  - [Shortcuts](#Shortcuts)
  - [Inlay window](#Inlay_window)
    - [Definition](#Definition)
    - [Declaration](#Declaration)
- [National focuses](#National_focuses)
  - [Name and description](#Name_and_description)
  - [Position](#Position)
  - [Interaction with other focuses](#Interaction_with_other_focuses)
  - [Cost](#Cost)
  - [Icon](#Icon)
  - [Dynamic appearance](#Dynamic_appearance)
  - [Triggers](#Triggers)
  - [Effects](#Effects)
  - [Search filters](#Search_filters)
  - [Titlebar styles](#Titlebar_styles)
  - [AI will do](#AI_will_do)
    - [Formulas for chance calculation](#Formulas_for_chance_calculation)
  - [Other](#Other)
  - [Examples](#Examples_2)
- [Shared focuses](#Shared_focuses)
  - [Joint focuses](#Joint_focuses)
  - [Example](#Example)
- [Continuous focuses](#Continuous_focuses)
  - [Focus palettes](#Focus_palettes)
  - [Focuses](#Focuses)
- [AI strategy plans](#AI_strategy_plans)
  - [Example](#Example_2)
- [Notes](#Notes)
- [References](#References)

---

National focus trees are defined within `/Hearts of Iron IV/common/national_focus/*.txt` files. Like most other files, the filename is irrelevant and isn't used for anything other than organisation. One file can store more than one focus tree or none at all.

## Focus tree <a id="Focus_tree"></a>

A focus tree is defined by using a `focus_tree = { ... }` block. The following arguments are used:

`id = my_focus_tree` decides the ID that the focus tree uses. It is mandatory to define, and an overlap will result in an error. The ID is primarily used for the [has_focus_tree trigger](<triggers.md>) and the [load_focus_tree effect](<effects.md>), whose tooltips use it as a localization key.

`country = { ... }` is a [MTTH block](<ai_modding.md>) that assigns a score for the focus tree, deciding which one is used in-game. This is evaluated *before the game's start* and the check is essentially **never refreshed**`[a]`. The focus tree with the highest score will be the one that gets loaded for the country. By default, the score starts with 1. A typical usage looks like this:

```text
country = {
    factor = 0
    modifier = {
        add = 20
        original_tag = TRA
    }
}
```

In this case, countries originating from ![Flag of Transylvania](media/national_focus_modding_b6347a9782__img2.png) Transylvania (i.e. the country itself and any civil war or collaboration government breakaways, as ensured by [the original_tag trigger](<triggers.md>)) will have the score of 20, while every other country will have the score of 0. Assuming that there is no other focus tree where ![Flag of Transylvania](media/national_focus_modding_b6347a9782__img2.png) Transylvania has a higher country score, this will ensure that this focus tree gets loaded for it.

`default = yes` sets the focus tree to be marked as default. In total, *there should be one total default focus tree*, no more, no less. A focus tree being marked as default means that if every other focus tree has a country score of 0, this tree will be chosen instead. Additionally, a country starting with a focus tree will fail to appear in the "minor countries" section within the "interesting countries" menu before the game's start. If this is left out from a focus tree, it gets assumed to be non-default.

`reset_on_civilwar = no` is not determined on its effect. Instead, this is how focus trees are handled in civil wars, regardless of if `reset_on_civilwar` is set or how it's set:
When a civil war starts, the original country will always continue using the focus tree. The focus it's doing will not be paused or cancelled by the civil war itself. The revolter will have the focus tree it's using evaluated when the civil war starts, assigning one depending on each tree's `country = { ... }` value. If the same focus tree gets used for the revolting country as the one that the original country used when the civil war started, every focus that the original country has completed will get completed for the revolting country, including setting the same focus progress for the one that's being completed by the original country at the moment. Otherwise, the focus progress will get lost.

`shared_focus = TAG_focusname` will set the focus tree to include the specified [shared focus](#Shared_focuses) and every focus that is connected to it via prerequisites. **Setting this to a non-existing focus causes a game crash when loading into the main menu.**

`continuous_focus_position = { x = 1200 y = 100 }` is the position of the top left corner of the continuous focus menu *in pixels*. For comparison, by default`[b]`, the continuous focus palette has the position of 50 on the X axis and 1000 on the Y axis. If both x and y are set to 0 or the position is undefined for the tree, it resets to the default position.

`initial_show_position = { ... }` decides the initial position of the camera when the focus tree is first opened. There are 2 ways to arrange it:

- `focus = TAG_focusname` will make the camera centre on the specified focus in particular. It'll be in the top centre of the screen exactly, taking offsets into consideration.
- `x = 12 y = 0` decides the exact position of the top-centre of the camera. This uses the same coordinate system as regular focuses do, by default a unit of x being equal to 96 pixels and a unit of y being equal to 130 pixels`[c]`

This also accepts `offset = { ... }`, adding the specified values to respective positions if the conditions within the `trigger = { ... }` trigger block are met for the country. For example, this will apply the modifier and result in a position of x = 13, y = 1 if the country is BHR:

```text
initial_show_position = {
    x = 17
    y = 0
    offset = {
        x = -4
        y = 1
        trigger = {
            tag = BHR
        }
    }
}
```

`focus = { ... }` are the focuses themselves. Each focus that's put within the focus tree will. The focuses **have** to be within a `focus_tree = { ... }` in order to let the game know which focus tree exactly to assign them to. If a `focus = { ... }` blocks ends up outside of a `focus_tree = { ... }` or within another `focus = { ... }`, this gets marked within the [error log](<modding.md>) as "focus" being an unexpected token, fixed by adjusting brackets as needed.

<!-- kit:begin id="focus-tree-vanilla" at="section:Focus_tree" -->
**Kit addition** Focus tree files in vanilla 1.19.4.1 (81 files in `common/national_focus/`). All counts: [vanilla-confirmed 1.19.4.1] `common/national_focus/`.

| Top-level block | Count |
| --- | --- |
| `focus_tree` | 67, holding 10,341 focuses |
| `shared_focus` | 335 |
| `joint_focus` | 280 |
| `style` | 22 |
| `search_filter_prios` | 1 |

- Tree keys: `id`, `country` and `default` appear in all 67 trees; `continuous_focus_position` in 57; `initial_show_position` in 29; `shared_focus` lines (71 of them) in 37; `shortcut` blocks (52) in 7 trees; `inlay_window` in 5 trees (6 declarations); `reset_on_civilwar` in 1; `alternate_icon_set` in 1 (`germany.txt`).
- `country` blocks: 64 trees use `factor` with `modifier` blocks, 2 use only `factor` and 1 uses `base` with `modifier`.
- `default`: 66 trees write `default = no` and one writes `default = yes`, the generic tree `generic_focus` in `generic.txt`. `hoi4.exe` has the message "Only one national focus tree should be default, switching from %s to %s". [vanilla-confirmed 1.19.4.1] for the values, [unverified] for the message.
- `initial_show_position` forms: `x` with `y` (22 trees, one with an `offset`), `focus` (6 trees, one with an `offset`) and one tree with only `x`. `hoi4.exe` reports "Both focus and the pair x, y cannot be specified at the same time" and "initial_show_position references invalid focus". [vanilla-confirmed 1.19.4.1] for the forms, [unverified] for the messages.
- `shortcut` always has `name` and `target`; `scroll_wheel_factor` is set in 28 of the 52 shortcut blocks and `trigger` in 31. [vanilla-confirmed 1.19.4.1]
- `hoi4.exe` also has "Duplicate focus name will cause database problems" and "Focus %s has a hash collision in tree %s, this must be fixed for correct behaviour", which fits the wiki's warning about duplicate focus ids. [unverified]
<!-- kit:end id="focus-tree-vanilla" -->

### Examples <a id="Examples"></a>

Pure minimum, with 2 focuses:

**The text in this section has been collapsed by default.**

```text
focus_tree = {
    id = BHR_focus_tree
    country = {
        base = 0
        modifier = {
            add = 10
            tag = BHR
        }
    }
    focus = {
        ...
    }
    focus = {
        ...
    }
}
```

Average tree, with 2 focuses:

**The text in this section has been collapsed by default.**

```text
focus_tree = {
    id = OMA_focus_tree
    country = {
        base = 0
        modifier = {
            tag = 25
            original_tag = OMA
        }
    }
    continuous_focus_position = { x = 450 y = 800 }
    initial_show_position = { focus = OMA_focus_name }
    focus = {
        id = OMA_focus_name
        ...
    }
    focus = {
        ...
    }
}
```

<!-- kit:begin id="focus-example-corrections" at="section:Examples" -->
**Kit correction** The "Average tree" example above has `tag = 25` inside the `country` modifier. The `tag` trigger takes a country tag, so this is a typo for `add = 25`; vanilla writes `modifier = { add = 10 tag = GER }` in `common/national_focus/germany.txt`. [vanilla-confirmed 1.19.4.1]
<!-- kit:end id="focus-example-corrections" -->

### Shortcuts <a id="Shortcuts"></a>

Shortcuts are used to add navigation buttons in the lower left corner that, when clicked, will move the camera to a specific focus.

Parameters:

- `name = lockey`, the localized name that will be displayed on the button.
- `target = focus_id`, focus where the camera should be moved.
- `scroll_wheel_factor = <float>`, zoom, the higher the value the greater the zoom. (between 0 and 1)
- `trigger = { ... }`, a trigger block specifying whether the shortcut button should be visible, optional. (If true, it will not supersede allow conditions of target focus.)

An example shortcut definition is as such:

```text
shortcut = {
  name = GER_oppose_hitler_shortcut
  target = GER_oppose_hitler_ww
  scroll_wheel_factor = 0.485
  trigger = {
    has_dlc = "Gotterdammerung"
  }
}
```

### Inlay window <a id="Inlay_window"></a>

Focus inlay windows are generic inlay components that can be added to the focus tree, similar to the continuous focus window, a [scripted GUI](<scripted_gui_modding.md>) object.

#### Definition <a id="Definition"></a>

<!-- kit:begin id="focus-inlay-warning" at="heading:Definition" -->
**Kit correction** The example below is not valid script. `scripted_buttons` is never closed, so `scripted_images` ends up inside it and the definition has one `}` too few. The names in it are placeholders: `inlay_window_id` is the name of your own definition (vanilla: `ger_inner_circle_inlay_window`), `advisor_portrait` stands for the name of a subcomponent of the GUI window, and `gfx_name` and `gfx_name_fallback` stand for sprite names starting with `GFX_`. A corrected format follows after this section's text. [vanilla-confirmed 1.19.3] `common/focus_inlay_windows/`.
<!-- kit:end id="focus-inlay-warning" -->

Definitions for inlay windows are located in `/Hearts of Iron IV/common/focus_inlay_windows/*.txt`.

For a guide written by the game developers, see Dev dairy modding

Parameters:

- `window_name = gui_component_name` the name of the scripting GUI to use.
- `internal = <bool>` if true, then the inlay window is only visible to the country itself. (defaults no)
- `visible = { ... }` whether the inlay window should be visible, when not visible, no evaluations will be done.
- `scripted_buttons = { ... }` list of images that should have dynamic sprites.
  - `<button_name> = { ... }` name of the button.
    - `available={ ... }` List of triggers when the button is allowed to be pressed.
    - `click_effect={ ... }` List of effects the button will have upon being pressed.
- `scripted_images = { ... }` list of images that should have dynamic sprites.
  - `<icon_name> = { ... }` name of the icon (must be a subcomponent of "gui_component_name"). List of possible gfx:es for the icon, first that evaluates to true is selected.
    - `<gfx_name> = { ... }/yes` If a trigger is provided, then it will be evaluated with the country scope of the focus tree. If "yes" is set, then it will always be used. Note: "yes" is commonly the last entry in the list that acts as a default case.

An example for inlay window definition:

```text
inlay_window_id = {
  window_name = gui_component_name
  internal = yes
  visible = {
    visibility_triggers
  }
  scripted_buttons = {
    my_button = {
      available = {
        triggers
      }
      click_effect = {
        add_political_power=5
      }
    }
  scripted_images = {
    advisor_portrait = {
      gfx_name = {
        has_completed_focus = TAG_focus_name_example
      }
      gfx_name_fallback = yes
    }
  }
}
```

<!-- kit:begin id="focus-inlay-format" at="section:Definition" -->
**Kit addition** Inlay window definition, from `common/focus_inlay_windows/documentation.md`:

- `window_name` is the name of the GUI component to show. In vanilla it is the `name` of a window in `interface/*.gui`, for example `sia_khana_ratsadon_ui_window` in `interface/SIA_khana_ratsadon_scripted_gui.gui`. [docs] for the key, [vanilla-confirmed 1.19.3] for the `.gui` link.
- `internal = yes` shows the window only to the country itself; the default is `no`. All 7 vanilla windows set `internal = yes`. [docs] and [vanilla-confirmed 1.19.3] `common/focus_inlay_windows/`.
- `visible` is a trigger; while it is false nothing in the window is evaluated. [docs]
- `scripted_images`: per icon name (a subcomponent of the window or a button) a list of `GFX_...` sprite names, each with a trigger or `yes`. The first entry whose trigger is true is used, on every update, and triggers run in the country scope of the focus tree. `yes` is normally the last entry, as the default. [docs]
- `scripted_buttons`: per button name an `available` trigger and a `click_effect` in country scope. A button name may also appear in `scripted_images` to choose its sprite; otherwise the sprite from the `.gui` file is used. [docs]
- `scripted_progressbars`: per progress bar name a `progress = <variable name>` line. The bar must be a subcomponent that uses a `progressbartype` sprite. The wiki does not mention this block. [docs]
- Vanilla windows: `scripted_images` in 5 of the 7 files, `scripted_buttons` in 3 and `scripted_progressbars` in 1. A button may have only a `click_effect` (the 5 buttons in `cze_industry_focus_inlay_window.txt`). [vanilla-confirmed 1.19.3] `common/focus_inlay_windows/`.

```text
my_inlay_window = {
    window_name = my_ui_window
    internal = yes
    visible = { has_completed_focus = TAG_focus_name }
    scripted_images = {
        my_status_icon = {
            GFX_my_status_good = { has_idea = TAG_good_idea }
            GFX_my_status_default = yes
        }
    }
    scripted_buttons = {
        my_button = { available = { has_political_power > 0 } click_effect = { add_political_power = -5 } }
    }
    scripted_progressbars = { my_bar = { progress = my_progress_variable } }
}
```

All names in the example are placeholders; the structure is the one the documentation and the vanilla files use. [docs]
<!-- kit:end id="focus-inlay-format" -->

#### Declaration <a id="Declaration"></a>

Inlay window must be declared in focus tree. Any number of inlay windows can be defined for focus tree.

Parameters:

- `id = inlay_window_id` inlay window identifier.
- `position = { x = <int> y = <int> }` position on the tree, same syntax and scale as continuous focus position.

An example declaration of inlay window is as such:

```text
inlay_window = {
  id = ger_inner_circle_inlay_window
  position = { x = 4500 y = 1150 }
}
```

<!-- kit:begin id="focus-inlay-declaration" at="section:Declaration" -->
**Kit addition** Declarations in vanilla 1.19.4.1. All items: [vanilla-confirmed 1.19.4.1] `common/national_focus/`.

- 6 `inlay_window` declarations in 5 trees (`australia_taog_focus` declares two windows at the same position, an empty one and the real one; `mu_czech_focus`, `german_focus`, `japan_wtt_focus`, `siam_focus`). Positions are in pixels, for example `x = 4500 y = 1150` for the German window.
- The Czech and Japanese trees add `override_position = { x = ... y = ... trigger = { ... } }` blocks (10 and 9) that move the window when branches are hidden. `override_position` is not mentioned in the documentation or on this page. A vanilla position block is also written with a capital `X` once, so key names look case-insensitive; keep them lowercase.
- `hoi4.exe` has the messages "Inlay window %s already exist" and "Couldn't find inlay window %s", so every `id` must be unique and must name an existing definition. [unverified]
<!-- kit:end id="focus-inlay-declaration" -->

## National focuses <a id="National_focuses"></a>

The ID for the focus is defined using `id = TAG_focusname`. While it's optional to preface the focus' ID with the country's tag, doing so is preferred to avoid overlapping focus IDs from different focus trees. Having the same focus ID in different focus trees leads to errors, such as broken prerequisite lines and effects or triggers such as [complete_national_focus](<effects.md>) or [has_completed_focus](<triggers.md>) not working correctly. Instead, it could be possible to use [shared focuses](#Shared_focuses) to put the same focus in different focus trees.

### Name and description <a id="Name_and_description"></a>

The name of the focus depending on the language that's turned on is defined within `/Hearts of Iron IV/localisation/`, using the ID of the focus as the localisation key. For English in particular, this is defined within any `/Hearts of Iron IV/localisation/english/*_l_english.yml` file with the UTF-8-BOM encoding. It is preferable to use new localisation files when possible rather than overwriting base game localisation in order to not have to change that for compatibility with recent versions, and to do so, the file should have a new name that doesn't exist in base game, but it must still end with `_l_english.yml` to be loaded properly. The focus' ID is used as the localisation key used to establish the name in the enabled language, while a description uses the focus' ID with `_desc` appended:

```yaml
l_english:
 TAG_focus_name: "Example focus"
 TAG_focus_name_desc: "Example focus description"
```

### Position <a id="Position"></a>

The position of the focus is decided via `x = 5` and `y = 1` attributes. By default, a unit of x is equal to 96 pixels and a unit of y is equal to 130 pixels`[c]`. In other words, a focus directly below another focus would have a unit difference of 1, while a focus directly to the right of another one would have a unit difference of 2. By default, this is relative to the top left corner of the tree: a larger x value moves the focus right, a larger y value moves the focus *down*.

It is also possible **and preferred** (on focuses with prerequisites) to make the focus' position be relative to another focus with doing `relative_position_id = TAG_other_focus`. This will position the focus relative to that focus, adding the `x` and `y` values to the other focus' position (after calculating that one's relative_position_id too). Doing so allows for more flexibility in the focus tree design by allowing to easily modify the position of the entire branch at the same time, due to updates to the children focuses' positioning. This also allows to only use the later `offset = { ... }` only in the top focus of each branch that requires to be moved.
For example, if focus A has `x = 1 y = 2`, focus B is positioned relative to focus A and has `x = 3 y = 4`, then the focus B will be positioned, in total, 4 steps to the right and 6 steps down of the top-left corner. A focus C positioned relative to focus B at `x = -1 y = 1` would then be located 3 steps to the right and 7 steps down of the top-left corner.
The game can behave unstably with an incorrect relative position ID. A recursion (such as a focus being positioned relative to itself or focus A and focus B being positioned relative to each other) may cause a game crash since it is impossible to determine the exact position of the focus, and the focus must also be located in the same focus tree for the argument to work properly.

Changing a focus' position based on a condition being met is done with `offset = { ... }`. The `x = 10` and `y = -3` values will be added to the focus' position if the conditions within `trigger = { ... }` are met for the country *when the focus tree is loaded*. This looks like the following:

```text
offset = {
    x = -5
    trigger = {
        has_dlc = "Poland: United and Ready"
    }
}
```

This in particular will move the focus 5 units to the left if the "Poland: United and Ready" DLC is turned on. This check also can be refreshed mid-session with the [mark_focus_tree_layout_dirty effect](<effects.md>)`[d]`, applying the offset if true.

### Interaction with other focuses <a id="Interaction_with_other_focuses"></a>

`prerequisite = { focus = TAG_other_focus }` decides the focuses necessary to complete for this focus to be available. At least one focus within a prerequisite has to be completed to mark the prerequisite as true, and each prerequisite much be completed to take the focus. If neither of the prerequisites is located in the same focus tree, then the focus will not appear. In other words, an OR statement is done by putting 2 focuses inside a prerequisite as `prerequisite = { focus = TAG_other_focus_1 focus = TAG_other_focus_2 }`, while an AND statement is done by putting two different prerequisites like the following:

```text
prerequisite = { focus = TAG_other_focus_1 }
prerequisite = { focus = TAG_other_focus_2 }
```

This system cannot represent every boolean logical arrangement, such as `A\lor (B\land C)` (Where `A`, `B`, and `C` represent whether a focus is complete) or with anything using negation. In this case, it can be possible to, instead, put an OR statement for either of the focuses necessary to complete this one and use the [has_completed_focus](<triggers.md>) trigger within the `available = { ... }` block with necessary flow control tools. [A custom trigger tooltip can be used to make it easier for the player to understand.](<triggers.md>)

`mutually_exclusive = { focus = TAG_other_focus }` makes this focus impossible to select if the specified focus has been completed. If both focuses are mutually exclusive toward each other, then the mutually exclusive arrows will be shown in the focus tree view. Mutual exclusivity to multiple focuses is usually done by putting several of `focus = TAG_focusname` in the same mutually_exclusive, but defining several of mutually_exclusive is also possible.

Neither prerequisites nor mutual exclusivity require the other focus to be in the same focus tree. This means that it can be used with [shared focuses](#Shared_focuses) to declare a regular, non-shared focus as mutually exclusive or a prerequisite without any errors, even when used in a focus tree not containing that focus.

The difference between prerequisites and using [has_completed_focus](<triggers.md>) within the `available = { ... }` block is that the prerequisites show up as lines within the national focus tree view and show up separately from other triggers in the tooltip of a focus.

There is an issue that leads to prerequisite lines not working properly: duplicate focus IDs within different focus trees. In this case, the game can take the position of the focuses as the ones within the different focus tree that contains the same focuses, leading to them appearing to link towards empty spaces or start inside of them. This can also break the path-generating algorithm and make it use the wrong turn sprites, which will show up broken even in trees that don't have any duplicates.
In order to avoid this, duplicate focus IDs must be avoided. A simple way to decrease the chance drastically is to preface the focus IDs with the country tag (such as `TAG_focus_name`) or something else that's unique for the focus tree (Such as `REGION_focus_name` for a shared regional tree). If the same focus tree should be used for several countries, this can be done by only having one focus tree where the `country = { ... }` of the tree is set up so that the desire to use it is the highest for several countries instead of just one; if the same focus tree branch should be used within several different focus trees, then [shared focuses](#Shared_focuses) can achieve exactly that.

Additionally, the game intends for a focus' prerequisite to be placed above the focus that requires it and it is unable to correctly generate the path to the focus otherwise, which will show up as having a path that uses the wrong sprites in the 90° turns.

<!-- kit:begin id="focus-prerequisites-vanilla" at="section:Interaction_with_other_focuses" -->
**Kit addition** Prerequisites, exclusivity and relative positions, checked against vanilla 1.19.4.1 (focuses inside the 67 `focus_tree` blocks).

- Prerequisite logic matches the wiki: one `prerequisite` block with several `focus` lines means one of them, several blocks mean all blocks, and mixing both means every block must be met, each by one of its focuses. The vanilla tooltips say so: "Requires one of the following" (`FOCUS_SINGLE_OR_PREREQ_HEADER`) and "Requires all of the following" (`FOCUS_AND_PREREQ_HEADER`, `FOCUS_MIX_PREREQ_HEADER`) in `localisation/english/core_l_english.yml`. [vanilla-confirmed 1.19.4.1]
- Vanilla uses 10,912 `prerequisite` blocks: 1,786 list more than one focus, 828 focuses have more than one block and 61 focuses mix both forms. [vanilla-confirmed 1.19.4.1] `common/national_focus/`.
- `mutually_exclusive` is written on both focuses: all 2,614 vanilla entries in tree focuses have the reverse entry on the target focus, and none is one-way. `hoi4.exe` contains the log text "Has mutual exclusivity with ... but the other focus does not." [vanilla-confirmed 1.19.4.1] for the counts, [unverified] for the message.
- `relative_position_id` is used by 10,145 focuses and always points at a focus defined earlier in the same tree (none later, none in another tree). `hoi4.exe` contains "Error in focus: ... does not exist. Relative focus must be scripted before this." and "Circular reference detected for relative position.", so define the anchor focus first and never close a loop. [vanilla-confirmed 1.19.4.1] for the counts, [unverified] for the messages.
<!-- kit:end id="focus-prerequisites-vanilla" -->

### Cost <a id="Cost"></a>

Another important aspect of the focus is `cost = 8`. This sets how long the focus takes to complete. By default, a cost of 1 is taken to be 7 "points",[1] of which by default 1 is completed daily, although it's possible to set different speeds depending if the country is at war or at peace.[2] In other words, a cost of 1 represents a week by default. This behaviour can be changed via the [Defines](<defines.md>) file. Decimals within cost are supported, and it will get rounded down to a whole day in the game.

Focus cost can be changed on a per focus basis via the `reduce_focus_completion_cost` effect. Examples are provided [here](<effects.md>).

<!-- kit:begin id="focus-cost-units" at="section:Cost" -->
**Kit addition** Cost units. `cost` counts in units of `FOCUS_POINT_DAYS` days: `NDefines.NFocus.FOCUS_POINT_DAYS = 7` ("Each point takes a week"), with `FOCUS_PROGRESS_PEACE = 1`, `FOCUS_PROGRESS_WAR = 1` and `MAX_SAVED_FOCUS_PROGRESS = 10`. At the default progress of 1 per day, `cost = 10` is 70 days. [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua`.

- Vanilla costs: 10 in 6,735 of 10,341 entries (70 days), 5 in 3,494 (35 days); the rest are 0, 1, 2, 3, 4, 12, 15, 20, 30 or 35, or a file-scoped constant: `germany.txt` defines `@inner_circle_time_tier_1 = 20` and uses `cost = @inner_circle_time_tier_1`. No vanilla cost has decimals. [vanilla-confirmed 1.19.4.1] `common/national_focus/`.
- `reduce_focus_completion_cost = { focus = <id> cost = N }` accepts script constants, and `focus` can be a single token or a list. Vanilla uses it 152 times. [docs] `documentation/effects_documentation.md` and [vanilla-confirmed 1.19.4.1].
<!-- kit:end id="focus-cost-units" -->

### Icon <a id="Icon"></a>

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

Within a focus, an icon is assigned with the line of `icon = GFX_focus_icon`. This assigns two sprites to the focus, in particular:

- Regular sprite, with the name of `GFX_focus_icon`. This is used in the focus description view and in the focus tree view when the focus is unavailable, is being completed, or has been completed.
- Sprite for the shine animation, with the name of `GFX_focus_icon_shine` (With _shine at the end). This is used in the focus tree view for focuses that are currently available and in the country politics and diplomacy views for the focus currently being complete. Since the game [doesn't use filenames in evaluation](<modding.md#Loading_files>), putting the spriteType definition into a file with `shine` in the filename isn't either necessary or sufficient. Only the name of the sprite is used, which must be the same as the regular sprite with _shine appended to the end. **The most common mistake when the shine doesn't work is not following this naming rule**.

If one of these is undefined or is defined incorrectly, the ![Goal unknown.png](media/national_focus_modding_b6347a9782__img9.png)missing focus icon will be used instead of the appropriate sprite, however the working sprite will continue to be used.
If the texturefile links to a non-existing file, whether it's the folder path that's incorrect`[e]` or the filename, including the extension, the focus icon will appear as fully transparent.
By default, the base game stores images for focus icons in the `/Hearts of Iron IV/gfx/interface/goals/` folder and sprites in the `interface/goals.gfx` and `interface/goals_shine.gfx` files. Since there's no reason to copy the files to the mod and doing so will lead to needing to update the file after a major update to use new sprites, it's best to create a new file in the folder for sprite definitions.
The following is an example of an interface file that defines both of the sprites:

**Example interface file**

```text
spriteTypes = {
    spriteType = {
        name = GFX_focus_icon
        texturefile = gfx/interface/goals/filename.dds
    }
    spriteType = {
        name = GFX_focus_icon_shine # Change the name, note to keep _shine in the end
        texturefile = gfx/interface/goals/filename.dds # Change to the focus icon
        effectFile = gfx/FX/buttonstate.lua
        animation = {
            animationmaskfile = gfx/interface/goals/filename.dds # Change to the focus icon
            animationtexturefile = gfx/interface/goals/shine_overlay.dds
            animationrotation = -90.0
            animationlooping = no
            animationtime = 0.75
            animationdelay = 0
            animationblendmode = "add"
            animationtype = "scrolling"
            animationrotationoffset = { x = 0.0 y = 0.0 }
            animationtexturescale = { x = 1.0 y = 1.0 }
        }
        animation = {
            animationmaskfile = gfx/interface/goals/filename.dds # Change to the focus icon
            animationtexturefile = gfx/interface/goals/shine_overlay.dds
            animationrotation = 90.0
            animationlooping = no
            animationtime = 0.75
            animationdelay = 0
            animationblendmode = "add"
            animationtype = "scrolling"
            animationrotationoffset = { x = 0.0 y = 0.0 }
            animationtexturescale = { x = 1.0 y = 1.0 }
        }
        legacy_lazy_load = no
    }
}
```

When copying from the template, note to change the `animationmaskfile` in each animation within the sprite with the shine alongside the `texturefile` and `name`.

<!-- kit:begin id="focus-icon-extras" at="section:Icon" -->
**Kit addition** Icon keys and messages in vanilla 1.19.4.1.

- `hoi4.exe` has "Missing icon for focus: " and "Missing icon shine for focus: ", which fits the wiki's rule that both `GFX_name` and `GFX_name_shine` must exist. [unverified]
- `overlay = GFX_...` is set in 94 focuses (`czechoslovakia_mu.txt` 44, `australia_taog.txt` 21, `philippines.txt` 17, `indonesia_joint.txt` 4, `japan.txt` 4, `china_communist_sea.txt` 3, `indonesia.txt` 1). The wiki does not mention it; the name suggests an image drawn over the icon. [vanilla-confirmed 1.19.4.1] `common/national_focus/` for the usage, [unverified] for the effect.
- `alternate_icon = GFX_...` is set in 22 focuses, all in `germany.txt`, and the tree sets `alternate_icon_set = FOCUS_ICON_SET_HISTORICAL_KEY_FOCUS` (sprite `GFX_FOCUS_ICON_SET_HISTORICAL_KEY_FOCUS` in `interface/nationalfocusview.gfx`, name in `localisation/english/wuw_focus_l_english.yml`). A commented line in `germany.txt` shows the other set name `FOCUS_ALTERNATE_ICONS`, whose toggle button needs a localisation key and a `GFX_` sprite of the same name. [vanilla-confirmed 1.19.4.1]
- `hoi4.exe` also has "Missing alternate icon for focus: " and "Missing alternate icon shine for focus: ", so an alternate icon needs its own `_shine` sprite as well. [unverified]
<!-- kit:end id="focus-icon-extras" -->

### Dynamic appearance <a id="Dynamic_appearance"></a>

`dynamic = yes` allows the title and icon of the focus to be dynamic. In particular, it allows using [scripted localisation](<localisation.md>) in focus titles and a dynamic icon. If false or unset, it will still allow using them, but instead it will pick one at the game's start and never change it.

Dynamic icons are treated similarly to events' titles or descriptions: instead of a single `icon = GFX_focus_example` a focus can contain multiple assets in the one `icon = { ... }` parentheses at the same time, each with a unique trigger. The first possible icon will get used in the focus. An `icon = { ... }` consists of a GFX_asset_name `= { ... }` with a trigger inside, which must be fulfilled by the country for the icon to be selectable. To set a default icon you need to put `GFX_focus_example = yes` in `icon = { ... }` parentheses.

An example dynamic focus definition, with all other optional arguments omitted:

```text
focus = {
    id = TAG_political_focus # In localisation, TAG_political_focus: "[THIS.GetRulingIdeology] political focus"
    icon = {
        GFX_focus_example_democratic = {
             has_government = democratic
        }
        GFX_focus_example_fallback = yes
    }
    dynamic = yes
}
```

<!-- kit:begin id="focus-dynamic-vanilla" at="section:Dynamic_appearance" -->
**Kit addition** Dynamic icons in vanilla 1.19.4.1. All counts: [vanilla-confirmed 1.19.4.1] `common/national_focus/`.

- 254 focuses set `dynamic = yes` (127 in trees, 26 shared, 101 joint). 60 focuses write `icon` as a block; 24 of them set `dynamic = yes` and 36 do not, which is the case the wiki describes where the icon is chosen once at game start.
- Every one of the 60 icon blocks contains a default entry written `GFX_name = yes`. [vanilla-confirmed 1.19.4.1] `common/national_focus/`. `hoi4.exe` has "Focus %s (%s) does not have a default icon case." and "Focus %s (%s) has alternate icons but does not have a default case.", so always add the default. [unverified] (strings in `hoi4.exe`).
<!-- kit:end id="focus-dynamic-vanilla" -->

### Triggers <a id="Triggers"></a>

*See also: [Triggers](<triggers.md>)*

In order to take the focus, aside from the focus prerequisites, the conditions within the `available = { ... }` block must be met. This functions as an [AND block](<scopes.md>), so each of the triggers must be true to fulfilled. [Scopes](<scopes.md>) can be used to check for conditions for other countries or within states. By default, the scope is of the country doing the focus. For example, this example requires the country to have more than 10% ![Stability](media/country_creation_1d4220f262__img10.png)Stability and for the state 294 to be owned by the ![Flag of Republic of Qatar](media/national_focus_modding_b6347a9782__img11.png) Republic of Qatar:

```text
available = {
    stability > 0.1
    294 = { is_owned_by = QAT }
}
```

`bypass = { ... }` is similar, but for bypassing the focus. Bypassing a focus marks the focus as complete, but does not grant its effects within the completion reward, instead focus can have `bypass_effect = { ... }`, focus can have `enable_automatic_bypass = no` to prevent bypassing focus automaticly. The exact same applies as to `available`: it's an AND block that assumes the country doing the focus by default. `bypass_if_unavailable = yes` can be used to make the focus automatically bypass as soon as the `available = { ... }` block is not met without needing to port over the triggers.

`allow_branch = { ... }` is used to tell when the focus should be visible. **This is only checked when the focus tree is first loaded**. However, this check also can be refreshed mid-session with the [mark_focus_tree_layout_dirty effect](<effects.md>)`[d]`, making the focus visible or invisible depending on if it's true or not. By default, a focus will also be disallowed if either of the parent focuses (as set by prerequisites) is disallowed. However, a focus containing `allow_branch` within its definition will only check its own allowed status, still showing up if it has disallowed parents. This means that if a branch is set to be disallowed under certain conditions, the first focus in any sub-branch that has its own conditions for being allowed must also contain the parent branch's condition within of itself, while other focuses may not have any `allow_branch` defined at all due to it being inherited from parents.

`available_if_capitulated = yes` sets the focus to be possible to complete while being capitulated. By default, this is set to false.

`cancel_if_invalid = no` and `continue_if_invalid = yes` decide how to treat the focus if the `available = { ... }` block becomes false while doing it. By default, these are true and false respectively. If both are set to false, the focus would pause when the `available = { ... }` block is false. This will not remove the gain_focus [static modifier](<modifiers.md>), which by default results in costing 1 ![Political Power](media/building_modding_811161eae8__img1.png)Political Power per day when doing the focus.

`cancel = { ... }` decides additional conditions which would cancel the focus if met. This is usually paired with `cancel_if_invalid = no`.

`historical_ai = { ... }` decides when the AI is able to pick this focus with the historical focus turned on. This does not ensure it picks this focus, rather prevents it from picking it when false. This takes priority over the order of focuses granted within [AI strategy plans](#AI_strategy_plans): if the AI were to do this focus next by the plan, yet `historical_ai = { ... }` is false and historical focus is turned on, then it won't be able to.

<!-- kit:begin id="focus-trigger-keys-vanilla" at="section:Triggers" -->
**Kit addition** Availability keys in vanilla 1.19.4.1. Counts are focuses inside `focus_tree` blocks (10,341) unless stated. All rows: [vanilla-confirmed 1.19.4.1] `common/national_focus/`.

| Key | Focuses | Notes |
| --- | --- | --- |
| `available` | 9,728 | |
| `bypass` | 5,889 | |
| `available_if_capitulated` | 5,514 | across tree, shared and joint focuses: 4,143 `no`, 1,690 `yes` |
| `cancel_if_invalid` | 3,807 | across all kinds: 3,478 `yes`, 563 `no` |
| `continue_if_invalid` | 3,780 | across all kinds: 3,555 `no`, 458 `yes` |
| `allow_branch` | 523 | plus 20 shared and 11 joint |
| `will_lead_to_war_with` | 777 | |
| `complete_tooltip` | 370 | |
| `select_effect` | 75 | |
| `enable_automatic_bypass = no` | 23 | |
| `cancel` | 20 | |
| `bypass_effect` | 18 | |
| `historical_ai` | 10 | |
| `bypass_if_unavailable = yes` | 8 | |
| `cancelable = no` | 2 | |

- Vanilla writes the defaults explicitly (`cancel_if_invalid = yes`, `continue_if_invalid = no`), so a missing line is not a mistake.
- The vanilla tooltips for the four outcomes when `available` turns false are `FOCUS_WILL_PAUSE`, `FOCUS_WILL_CANCEL`, `FOCUS_WILL_BYPASS_IF_UNAVAILABLE` and `FOCUS_WILL_CONTINUE` in `localisation/english/core_l_english.yml`, matching the key names above. [vanilla-confirmed 1.19.4.1]
<!-- kit:end id="focus-trigger-keys-vanilla" -->

### Effects <a id="Effects"></a>

*See also: [Effects](<effects.md>)*

The primary reward of the focus is done with `completion_reward = { ... }`. This executes each [effect](<effects.md>) within the specified [scopes](<scopes.md>) in order that they are put in the file. The assumed scope is the country doing the focus. For example, this would add 100 ![Political Power](media/building_modding_811161eae8__img1.png)Political Power to the country doing the focus and fire the `my_event.0` country event to ![Flag of Oman](media/national_focus_modding_b6347a9782__img14.png) Oman:

```text
completion_reward = {
    add_political_power = 100
    OMA = { country_event = my_event.0 }
}
```

The tooltip of the focus can be changed with `complete_tooltip = { ... }`, *which is also an effect block*. This would be equivalent to putting the contents of the reward inside of [hidden_effect](<scopes.md>) and using [effect_tooltip](<scopes.md>) in the same reward. This can be useful if the tooltip of the reward appears cluttered. For instance, using [random_owned_controlled_state](<scopes.md>) thrice with the same effect in each one can result in a cluttered tooltip, as each state and its effects would appear individually. But if, instead, the code [sets a state flag](<effects.md>) for each state in the reward and, in the tooltip, uses [every_state](<scopes.md>) limited to the ones that have the state flag, it'll show the same effect being executed for 3 states at the same time, cutting it into a third of what it was.

Additionally, `select_effect = { ... }` is used to execute an effect when the focus is *selected*. This has no tooltip shown to the player. This also automatically makes the focus impossible to cancel manually. It may still be cancelled automatically if set to do so, so in most cases it'd be preferable to set it to not cancel if invalid in order to prevent the effects within from firing more than once, as there is no way to execute an effect when the focus gets cancelled.

Additionally, `bypass_effect = { ... }` is used to execute an effect when focus is [*bypassed*](#Triggers).

**The focus is not yet marked as complete when the effects are being executed.** What this means is that any [has_completed_focus check](<triggers.md>) ran within will return as false. This can be a hinderance in some cases, most commonly when using allow_branch (as the effect to refresh the check will not work properly when put within a focus). Some alternatives can be considered:

- [Country flags to track that a focus has been completed](<data_structures.md#Flags>). Since country flags are set immediately, as long as the setting precedes the requirement, this will work.
- Delaying the effects that would require the focus to be complete. This is usually done by firing a hidden event. If done with no delay, the event will be fired *right after* the focus is complete, resulting in no noticeable delay for the player, but still executing the effects in order.
- Forcefully marking the focus to be complete. This, for example, can be done by using [load_focus_tree](<effects.md>) for the same focus tree with the completed focuses being kept. Doing so will not interrupt the completion reward's execution.

<!-- kit:begin id="focus-effects-vanilla" at="section:Effects" -->
**Kit addition** Focus effects and triggers that this page does not name. Documentation: `documentation/effects_documentation.md` and `documentation/triggers_documentation.md` ([docs]). Uses are counted over `events/`, `common/` and `history/` ([vanilla-confirmed 1.19.4.1]).

| Name | What the documentation says | Uses |
| --- | --- | --- |
| `complete_national_focus = <id>` | completes a focus for the country | 3,150 short; 36 in block form `{ focus = <id> use_side_message = yes originator_name = ... }`, which the documentation does not describe |
| `unlock_national_focus = <id>` | unlocks a focus for the country | 354 |
| `uncomplete_national_focus = { focus = <id> uncomplete_children = yes refund_political_power = yes }` | uncompletes a focus; both flags default to `no`; runs an `on_uncomplete` effect on each uncompleted focus if one is specified | 101 |
| `activate_shine_on_focus = <id>`, `deactivate_shine_on_focus = <id>` | switch the shine on a focus; a completed focus cannot be given a shine and the current focus cannot lose it; tooltips show only in debug mode | 24 and 32 |
| `focus_progress = { focus = <id> progress > 0.5 }` | trigger on the progress of a focus | 194 |
| `has_shine_effect_on_focus = <id>` | trigger: the focus has a shine, by hand or by being worked on | 71 |

- The `uncomplete_national_focus` entry says an `on_uncomplete` effect runs on each uncompleted focus. [docs] `documentation/effects_documentation.md`. No vanilla focus uses it. [vanilla-confirmed 1.19.4.1] `common/national_focus/`. Where exactly it sits in the focus block is [unverified].
- Console commands: `Focus.IgnorePrerequisites`, `Focus.NoChecks`, `Focus.AutoComplete`, `freefocuses`, `show_focuses`, `list_hidden_focuses`, `loc_check_focuses` and `focus_count`. [docs] `documentation/console_commands_documentation.md`.

**`load_focus_tree`.** The documentation names `tree`, `keep_completed` (default `no`: keep the completed focuses of the old tree that also exist in the new one) and `copy_completed_from = <country>` (mark everything that country has completed as completed in the new tree); the effect retains finished shared focuses. [docs] `documentation/effects_documentation.md`.

- Vanilla has 80 uses: 25 short (`load_focus_tree = <tree id>`) and 55 block form, every block with `tree` and `keep_completed`; none uses `copy_completed_from`. [vanilla-confirmed 1.19.4.1]
- `hoi4.exe` logs "Unable to find focus tree with ID: %s" for a wrong tree id. [unverified]

**`add_tech_bonus`.** The documentation only says "adds a limited use tech bonus". [docs] `documentation/effects_documentation.md`.

- Vanilla has 1,946 uses. Keys: `name` (1,893), `bonus` (1,899) or `ahead_reduction` (177, and 130 of those also write `bonus`), `uses` (1,918), and either one or more `category` lines (1,868 uses, 211 of them with two or more) or one `technology` line (78 uses). [vanilla-confirmed 1.19.4.1] `common/national_focus/generic.txt` and others.
- `category` takes a technology category from `common/technology_tags/00_technology.txt`, which lists 134 names, such as `industry` (117 uses), `construction_tech` (25 uses), `electronics` and `infantry_weapons`. There is no category called `construction`. [vanilla-confirmed 1.19.4.1]

```text
add_tech_bonus = {
    name = infantry_artillery_bonus
    bonus = 1.0
    uses = 1
    category = infantry_weapons
    category = artillery
}
```

**`research_bonus`** is not an effect. It is a key of ideas (1,086 uses in `common/ideas/`), characters (15) and military industrial organizations (2), and `documentation/effects_documentation.md` has no effect of that name. In a focus reward use `add_tech_bonus`, or add an idea that carries `research_bonus`. [vanilla-confirmed 1.19.4.1] and [docs]
<!-- kit:end id="focus-effects-vanilla" -->

### Search filters <a id="Search_filters"></a>

Search filters for each focus are set with `search_filters = { ... }`. Within that block, each search filter that the focus has is put inside, separated by whitespace characters. For instance, the following will assign FOCUS_FILTER_MANPOWER and FOCUS_FILTER_POLITICAL to the focus: `search_filters = { FOCUS_FILTER_MANPOWER FOCUS_FILTER_POLITICAL }`. These filters get used in the search menu in the top right of the national focus tree view.

A focus filter is not defined in any file, but instead they are created dynamically for each focus tree. Each one uses the sprite the same as its name but with `GFX_` inserted in the beginning. For instance, this defininition within any `/Hearts of Iron IV/interface/*.gfx` file would be used for FOCUS_FILTER_MY_MOD:

```text
spriteType = {
    name = GFX_FOCUS_FILTER_MY_MOD
    texturefile = gfx/interface/focusview/filter/my_mod_icon.dds
}
```

As before with regular focus icon, the exact folder where filter icons are stored is irrelevant, as long as the texturefile specified within the sprite is correct.

The localisation key used for the focus filter is the same as its name. For example, with the prior example of FOCUS_FILTER_MY_MOD, this would get defined for the English language in any `/Hearts of Iron IV/localisation/english/*_l_english.yml` file as  `FOCUS_FILTER_MY_MOD: "My mod"`

A list of every base game focus filter:

| Icon | Internal name | Localised name | Notes |
| --- | --- | --- | --- |
| ![Pol power icon.png](media/national_focus_modding_b6347a9782__img15.png) | FOCUS_FILTER_POLITICAL | Political | Typically used when gaining political power, when changing the internal political situation, or when improving diplomatic relations. |
| ![Research icon.png](media/national_focus_modding_b6347a9782__img16.png) | FOCUS_FILTER_RESEARCH | Research | Used for tech bonuses, scientists, research sharing groups, etc. |
| ![Industry icon.png](media/national_focus_modding_b6347a9782__img17.png) | FOCUS_FILTER_INDUSTRY | Industry | Used for economic modifiers and gaining factories |
| ![Stability icon.png](media/national_focus_modding_b6347a9782__img18.png) | FOCUS_FILTER_STABILITY | Stability |  |
| ![War support icon.png](media/national_focus_modding_b6347a9782__img19.png) | FOCUS_FILTER_WAR_SUPPORT | War support |  |
| ![Manpower icon.png](media/national_focus_modding_b6347a9782__img20.png) | FOCUS_FILTER_MANPOWER | Manpower | Usually used when gaining more manpower (directly or via conscription), equipment, generals, or when creating units. |
| ![Territory icon.png](media/national_focus_modding_b6347a9782__img21.png) | FOCUS_FILTER_ANNEXATION | Territorial Expansion | Usually used in demands for territory and avoided in outright declarations of war. |
| ![Historical focus filter icon.png](media/national_focus_modding_b6347a9782__img22.png) | FOCUS_FILTER_HISTORICAL | Historical | Usually used for focuses taken on the historical focus on. |
| ![International trade icon.png](media/national_focus_modding_b6347a9782__img23.png) | FOCUS_FILTER_INTERNATIONAL_TRADE | International Trade | Usually used for focuses related to the international market. |
| ![Army xp icon.png](media/national_focus_modding_b6347a9782__img24.png) | FOCUS_FILTER_ARMY_XP | Army Experience | Used when gaining Army Experience or modifiers related to it. |
| ![Navy xp icon.png](media/national_focus_modding_b6347a9782__img25.png) | FOCUS_FILTER_NAVY_XP | Navy Experience | Used when gaining Navy Experience or modifiers related to it. |
| ![Air xp icon.png](media/national_focus_modding_b6347a9782__img26.png) | FOCUS_FILTER_AIR_XP | Air Experience | Used when gaining Air Experience or modifiers related to it. |
| ![Autonomy icon.png](media/national_focus_modding_b6347a9782__img27.png) | FOCUS_FILTER_TFV_AUTONOMY | Autonomy | Used when adding or subtracting autonomy or modifiers related to it. |
| ![Political character icon.png](media/national_focus_modding_b6347a9782__img28.png) | FOCUS_FILTER_POLITICAL_CHARACTER | Political Character | Used for focuses about a nation’s politics |
| ![Military character icon.png](media/national_focus_modding_b6347a9782__img29.png) | FOCUS_FILTER_MILITARY_CHARACTER | Military Character | Used for focuses about a nation’s military |
| ![Internal affairs icon.png](media/national_focus_modding_b6347a9782__img30.png) | FOCUS_FILTER_INTERNAL_AFFAIRS | Internal Affairs | Used in the ![Flag of Bulgaria](media/national_focus_modding_b6347a9782__img32.png) Bulgarian and ![Flag of Greece](media/national_focus_modding_b6347a9782__img33.png) Greek national focus trees for focuses dealing with the internal factions. |
| ![Pol violence.png](media/national_focus_modding_b6347a9782__img34.png) | FOCUS_FILTER_FRA_POLITICAL_VIOLENCE | Political Violence | Used in the ![Flag of France](media/cosmetic_tag_modding_8daa0f4184__img3.png) French national focus tree for the focuses that remove the *political violence* spirit. |
| ![SOV propaganda icon.png](media/national_focus_modding_b6347a9782__img36.png) | FOCUS_FILTER_PROPAGANDA | Propaganda | Used in the ![Flag of Soviet Union](media/national_focus_modding_b6347a9782__img37.png) Soviet national focus tree for the focuses dealing with the propaganda system. |
| ![Occupation cost icon.png](media/national_focus_modding_b6347a9782__img38.png) | FOCUS_FILTER_FRA_OCCUPATION_COST | Occupation Costs | Used in the ![Flag of Vichy France](media/national_focus_modding_b6347a9782__img39.png) Vichy French national focus tree for the focuses dealing with the ![Flag of Germany](media/effect_ec2e2a02fa__img1.png) German occupation. |
| ![Inflation icon.png](media/national_focus_modding_b6347a9782__img41.png) | FOCUS_FILTER_CHI_INFLATION | Inflation |  |
| ![Balance of power icon.png](media/national_focus_modding_b6347a9782__img42.png) | FOCUS_FILTER_BALANCE_OF_POWER | Balance of Power | Used when implementing, modifying, or removing a balance of power |
| ![SWI military readiness filter icon.png](media/national_focus_modding_b6347a9782__img43.png) | FOCUS_FILTER_SWI_MILITARY_READINESS | Military Readiness | Used in the ![Flag of Switzerland](media/scopes_eff9c6f993__img16.png) Swiss focus tree for focuses dealing with Switzerland’s ‘‘Military Readiness’’ system. |
| ![Congress icon.png](media/national_focus_modding_b6347a9782__img44.png) | FOCUS_FILTER_USA_CONGRESS | Congress | Used in the ![Flag of USA](media/national_focus_modding_b6347a9782__img45.png) United States focus tree for focuses requiring or changing support in Congress. |
| ![Church authority.png](media/national_focus_modding_b6347a9782__img46.png) | FOCUS_FILTER_MEX_CHURCH_AUTHORITY | Church Authority | Used in the ![Flag of Mexico](media/national_focus_modding_b6347a9782__img153.png) Mexican national focus tree for focuses dealing with the church. |
| ![Caudillo rebellion.png](media/national_focus_modding_b6347a9782__img47.png) | FOCUS_FILTER_MEX_CAUDILLO_REBELLION | Caudillo Rebellion |  |
| ![Spa civil war.png](media/national_focus_modding_b6347a9782__img48.png) | FOCUS_FILTER_SPA_CIVIL_WAR | Spanish Civil War |  |
| ![Spa carlist uprising.png](media/national_focus_modding_b6347a9782__img49.png) | FOCUS_FILTER_SPA_CARLIST_UPRISING | Carlist Uprising |  |
| ![Kurdistan icon.png](media/national_focus_modding_b6347a9782__img50.png) | FOCUS_FILTER_TUR_KURDISTAN | Kurdistan | Used in the ![Flag of Turkey](media/country_creation_1d4220f262__img19.png) Turkish focus tree for focuses dealing with Kurdistan and Kurdish resistance |
| ![Kemalism icon.png](media/national_focus_modding_b6347a9782__img52.png) | FOCUS_FILTER_TUR_KEMALISM | Kemalism |  |
| ![Traditionalism icon.png](media/national_focus_modding_b6347a9782__img53.png) | FOCUS_FILTER_TUR_TRADITIONALISM | Traditionalism |  |
| ![Debt to the ifc icon.png](media/national_focus_modding_b6347a9782__img54.png) | FOCUS_FILTER_GRE_DEBT_TO_IFC | Debt to the I.F.C. |  |
| ![SOV paranoia icon.png](media/national_focus_modding_b6347a9782__img55.png) | FOCUS_FILTER_SOV_POLITICAL_PARANOIA | Political Paranoia |  |
| ![ITA missiolini icon.png](media/national_focus_modding_b6347a9782__img56.png) | FOCUS_FILTER_ITA_MISSIOLINI | Mussolini's Missions | Spelt exactly as used in-game. |
| ![SWE folkhemmet icon.png](media/national_focus_modding_b6347a9782__img57.png) | FOCUS_FILTER_FOLKHEMMET | Folkhemmet |  |

In addition, it is possible to set the priority of focus filters. This is done with the `search_filter_prios = { ... }` block *outside of the `focus_tree = { ... }`*. This priority is impossible to set to be focus tree-specific and instead is global. An entry within that block is done in the format of `FOCUS_FILTER_MY_MOD = 1200`, where the first part decides the filter and the second part decides the priority. Focus filters with the higher priority appear earlier in the top view. By default, the game does it in the file containing the generic focus tree: `/Hearts of Iron IV/common/national_focus/generic.txt`.

<!-- kit:begin id="focus-search-filters-vanilla" at="section:Search_filters" -->
**Kit addition** Search filters in vanilla 1.19.4.1. The focuses in `common/national_focus/` use 38 distinct `FOCUS_FILTER_*` names, and 8,980 of the 10,341 tree focuses write `search_filters` (9,052 lines, 944 of them empty blocks). The most used are `FOCUS_FILTER_INDUSTRY` (2,657 uses), `FOCUS_FILTER_POLITICAL` (2,551) and `FOCUS_FILTER_RESEARCH` (1,717). [vanilla-confirmed 1.19.4.1] `common/national_focus/`.

Real filters that the table above lacks. All rows: [vanilla-confirmed 1.19.4.1] `common/national_focus/`, `interface/nationalfocusview.gfx`, `localisation/english/focus_filter_tag_l_english.yml`.

| Internal name | Uses | Localised name |
| --- | --- | --- |
| `FOCUS_FILTER_IMPERIAL_INFLUENCE` | 51 | Imperial Influence |
| `FOCUS_FILTER_INNER_CIRCLE` | 30 | Inner Circle |
| `FOCUS_FILTER_COMPLETED_BY_EVENT` | 13 | Completed Through Events |

- `FOCUS_FILTER_INDUSTRIAL` (one use, in `paraguay_uruguay_shared_branch.txt`) has no sprite and no localisation key anywhere in the game files: it is a typo for `FOCUS_FILTER_INDUSTRY`. [vanilla-confirmed 1.19.4.1]
- `search_filter_prios` in `generic.txt` holds 10 entries. Its entry `FOCUS_FILTER_MISSIOLINI = 110` does not match the name focuses use (`FOCUS_FILTER_ITA_MISSIOLINI`), so it probably never applies. `hoi4.exe` has "Prio is already set for focus tree filter" for a repeated entry. [vanilla-confirmed 1.19.4.1] for the entries, [unverified] for the effect and the message.
<!-- kit:end id="focus-search-filters-vanilla" -->

### Titlebar styles <a id="Titlebar_styles"></a>

Styles are used for determining the picture used for the titlebar, the background on which the focus name is shown.
A titlebar is set by using `text_icon = mod_focus_style` in the focus.

A style that can be used in focuses is created by using a root-level `style = { ... }` block in a `/Hearts of Iron IV/common/national_focus/*.txt` file, by default `00_titlebar_styles.txt`. There are these possible attributes that can be used inside of a style:

- `name = example_style` is the name of the style. The argument determines what needs to be written in a focus' `text_icon` to reference this style.
- `default = yes`, if written, will make any focus without a defined `text_icon` use this style. Only one style total may use this.
- `unavailable = GFX_focus_unavailable_example` is the sprite that gets used when the focus is unavailable.
- `completed = GFX_focus_unavailable_example` is the sprite that gets used when the focus has been completed.
- `available = GFX_focus_unavailable_example` is the sprite that gets used when the focus is available for completion, but not yet selected.
- `current = GFX_focus_unavailable_example` is the sprite that gets used when the focus is currently in progress of being completed.

An example style definition is as such:

```text
style = {
	name = example_style
	unavailable = GFX_focus_unavailable_example
	completed = GFX_focus_completed_example
	available = GFX_focus_can_start_example
	current = GFX_focus_current_example
}
```

**Example sprite definitions**

```text
spriteTypes = {
    spriteType = {
        name = GFX_focus_unavailable_example
        textureFile = gfx/interface/focusview/titlebar/focus_unavailable_example_bg.dds
    }
    spriteType = {
        name = GFX_focus_can_start_example
        textureFile = gfx/interface/focusview/titlebar/focus_can_start_example_bg.dds
    }

    SpriteType = {
        name = "GFX_focus_current_example
        texturefile = gfx/interface/focusview/titlebar/focus_can_start_example_bg.dds # Usually the same as the available sprite
        effectFile = gfx/FX/buttonstate_onlydisable.lua
        animation = {
            animationmaskfile = gfx/interface/focusview/titlebar/focus_ongoing_mask2.dds
            animationtexturefile = gfx/interface/focusview/titlebar/focus_ongoing_texture.dds     # <- the animated file
            animationrotation = -90.0        # -90 clockwise 90 counterclockwise(by default)
            animationlooping = yes            # yes or no ;)
            animationtime = 20.0                # in seconds
            animationdelay = 0.2            # in seconds
            animationblendmode = add       #add, multiply, overlay
            animationtype = rotating      #scrolling, rotating, pulsing
            animationrotationoffset = { x = 0.0 y = 0.0 }
            animationtexturescale = { x = 1.0 y = 1.0 }
        }
        animation = {
            animationmaskfile = gfx/interface/focusview/titlebar/focus_ongoing_mask4.dds
            animationtexturefile = gfx/interface/focusview/titlebar/focus_ongoing_texture.dds
            animationrotation = 90.0        # -90 clockwise 90 counterclockwise(by default)
            animationlooping = yes            # yes or no ;)
            animationtime = 15.0                # in seconds
            animationdelay = 0.2            # in seconds
            animationblendmode = add       #add, multiply, overlay
            animationtype = rotating_ccw      #scrolling, rotating, pulsing
            animationrotationoffset = { x = 0.0 y = 0.0 }
            animationtexturescale = { x = 1.0 y = 1.0 }
        }
        legacy_lazy_load = no
    }

    SpriteType = {
        name = GFX_focus_completed_example
        texturefile = gfx/interface/focusview/titlebar/focus_completed_example_bg.dds
        effectFile = gfx/FX/buttonstate_onlydisable.lua
        animation = {
            animationmaskfile = gfx/interface/focusview/titlebar/focus_completed_mask.dds
            animationtexturefile = gfx/interface/focusview/titlebar/focus_completed_texture.dds     # <- the animated file
            animationrotation = 0.0        # -90 clockwise 90 counterclockwise(by default)
            animationlooping = yes            # yes or no ;)
            animationtime = 26.0                # in seconds
            animationdelay = 0.0            # in seconds
            animationblendmode = add       #add, multiply, overlay
            animationtype = scrolling      #scrolling, rotating, pulsing
            animationrotationoffset = { x = 0.0 y = 0.0 }
            animationtexturescale = { x = 1.0 y = 1.0 }
        }
        legacy_lazy_load = no
    }
}
```

<!-- kit:begin id="focus-titlebar-vanilla" at="section:Titlebar_styles" -->
**Kit addition** Titlebar styles in vanilla 1.19.4.1. All 22 `style` blocks are in `common/national_focus/00_titlebar_styles.txt`, each with exactly `name`, `unavailable`, `completed`, `available` and `current`; one (`default_style`) also sets `default = yes`. `text_icon` is set in 316 focuses (20 in trees, 16 shared, all 280 joint). [vanilla-confirmed 1.19.4.1] `common/national_focus/`.
<!-- kit:end id="focus-titlebar-vanilla" -->

### AI will do <a id="AI_will_do"></a>

`ai_will_do = { ... }` is a [MTTH block](<ai_modding.md>) that decides the likelihood for the AI to do this focus if [an AI strategy plan](#AI_strategy_plans) is not set.
By default, each focus has a score of 1. The arguments of `base` (changing the value), `add`, and `factor` (multiplying it) can be used to modify it.
Within the `ai_will_do = { ... }` block, `modifier = { ... }` functions as a trigger block where the prior three value-modifying arguments are also supported. The value will be modified if the triggers are true. For example, the following will result in the value of 15 for POL and a value of 5 for every other country:

```text
ai_will_do = {
    base = 5
    modifier = {
        factor = 3
        tag = POL
    }
}
```

An arbitrarily large amount of modifiers is possible to add to an ai_will_do, and they will apply in the order they're put in the code. It is also possible to use [variables](<data_structures.md>) within a modifier of the ai_will_do value.

The way that the value is evaluated for AI picking the focus is that, when picking a focus to do, it generates a random decimal value between 0 and the ai_will_do value for each of the focuses. If the evaluated focus has a prerequisite focus that the AI has just completed, the generated ai_will_do value gets multiplied by 1.5 before the game picks a focus.[3] If the [AI strategy plan](#AI_strategy_plans) that the country is currently following has `focus_factors = { ... }` defined for this focus, the value gets multiplied by the specified value. Afterwards, the game picks the focus that has the highest generated value. If neither of the focuses has a value above 0, the AI will not pick any of them, instead going into continuous focuses if possible or not doing any otherwise.
**Due to that algorithm, low values are less likely to be picked than intuition suggests.**

To reiterate, **this is only evaluated if the [AI strategy plan](#AI_strategy_plans) for the country doesn't have the order of the focuses set** or if none of the focuses in that order can be followed.Comparing the chances between focuses is the following:

#### Formulas for chance calculation <a id="Formulas_for_chance_calculation"></a>

As the general formula can be complex to calculate without a special tool, simpler calculations for special cases can provide quite useful: whether for approximating a chance by substituting similar numbers or for calculating the exact chance if the numbers align. Each case will be provided with three paragraphs — The formula in the first paragraph, an example in the second paragraph, and a general explanation of why it applies (though not necessarily a rigorous proof) in the third paragraph. The total chance will be given on the scale of 0—1; focuses are assumed each to have a positive value, as negatives are unintended and a focus with a chance of zero will never get picked by the game's AI meaning they can be excluded from the calculation entirely; and the modifiers applying to the focus' AI will do value (e.g. from AI strategy plans or the bonus for continuing the same branch) have already been applied, as multiplying the result of the rolled dice by a number would be the same as multiplying the ends of a range by that number.
In shortened form, the ai_will_do value of a focus will be referred simply as the "focus' value".

**One focus with a large value and other focuses with the same smaller value**

Let there be `n` focuses: a focus with the chance of `a` and `n-1` focuses with the chance of `b`, where `a\geq b`. In this case, the chance for the focus with the value of `a` has a chance of `{\frac {a-b}{a}}+{\frac {b}{n*a}}`, while the focuses with the value of `b` each have the chance of `{\frac {b}{n*a}}`.

For example, if there are 3 focuses with values of `2`, `1`, and `1`, the chance for the first focus will be `{\frac {2-1}{2}}+{\frac {1}{3*2}}={\frac {2}{3}}`, while the chance for a focus with a smaller chance to be picked is `{\frac {1}{6}}` (Since there are 2 such focuses, this adds up to 1 in total).

Intuitively, the chance for the largest-valued focus to get picked consists of 2 mutually exclusive possibilities: the picked value between `0` and `a` is larger than `b` and the opposite: it is smaller. While it's theoretically possible that the same value will get picked for both, this almost never happens, so it can be disregarded. The chance of the former is the first element of the sum: `1-{\frac {b}{a}}={\frac {a-b}{a}}`. If that possibility is fulfilled, the element with the chance of `a` will get picked every time since other focuses can't get a higher value. If the latter possibility is met, which has the chance of `{\frac {b}{a}}`, each focus has an equal chance to be picked. Since there are `n` focuses in total, the chance gets divided by that number. That is the entire chance for the smaller-valued focuses, while it gets added to the larger-valued focus alongside the chance for the initial possibility.

**Focuses split across two different values**

Let there be two sequences of focuses: `(a_{i})_{i=1}^{n}` and `(b_{i})_{i=1}^{k}` where each focus in a given sequence has the same value — respectively `a` and `b`. Focuses are arranged so that `a\geq b`. The first sequence will have `n` focuses, while the second sequence will have `k` focuses. In this case, a focus with the value of `a` will have the chance of `{\frac {1}{n}}-{\frac {kb^{n}}{n(n+k)a^{n}}}`, while a focus with the value of `b` will have the chance of `{\frac {b^{n}}{(n+k)a^{n}}}`

For example, if there are 3 focuses with a value of 4, and 2 focuses with a value of 3, then the former focuses will each have a chance of `{\frac {1}{3}}-{\frac {2*3^{3}}{3*5*4^{3}}}={\frac {1}{3}}-{\frac {54}{960}}={\frac {160}{480}}-{\frac {27}{480}}={\frac {133}{480}}\approx 27.71\%`. The latter focuses will each have a chance of `{\frac {3^{3}}{5*4^{3}}}={\frac {27}{320}}\approx 8.44\%`

For an understanding of this, it's once again useful to split this into two possibilities: Each focus with the value of `a` rolled a number between `0` and `b` and the reverse: at least one focus has rolled a number above `b`.
In regards to the first possibility, this has the chance of `\left({\frac {b}{a}}\right)^{n}={\frac {b^{n}}{a^{n}}}`, since this is `n` independent events, each with a chance of `{\frac {b}{a}}`. If this is fulfilled, each individual focus has a chance of `{\frac {1}{n+k}}` of being picked, and this is the only way focuses in the sequence `b` can get picked. As such, this sets the chance for these focuses to be `{\frac {b^{n}}{(n+k)a^{n}}}`.
While the chance for the first sequence of focuses can be found by subtracting this – multiplied by `k` – from `1` and then dividing the result by `n`, a different approach will lead to the same result while being more rigorous. For this, we'll take apart the second possibility. If this possibility is indeed the case, then we can safely ignore the focuses with the chance of `b`. In this case, the chance for a single one of the focuses to be picked is `{\frac {1}{n}}`. However, that's taking into account the whole `I(0;a)` interval, while we need to subtract the `I(0;b)` interval. The chance for a focus to have the highest value within that interval is `{\frac {b^{n}}{n*a^{n}}}`, as there are `n` focuses. As such, the chance that a focus' rolled value falls into the `I(b;a)` interval and is the highest among focuses is `{\frac {1}{n}}-{\frac {b^{n}}{n*a^{n}}}`. Adding the initial value calculated for the first possibility, the resulting formula is `{\frac {1}{n}}+{\frac {b^{n}}{(n+k)a^{n}}}-{\frac {b^{n}}{n*a^{n}}}={\frac {1}{n}}-{\frac {b^{n}}{a^{n}}}\left({\frac {1}{n}}-{\frac {1}{n+k}}\right)={\frac {1}{n}}-{\frac {kb^{n}}{n(n+k)a^{n}}}`

**General formula**

Let `(a_{i})_{i=1}^{n}` be a sequence of focus values. As such, a focus numbered with `i` will have the value of `a_{i}`. Then the chance for the focus `i` to be picked is `{\frac {1}{a_{i}}}\int _{0}^{a_{i}}\left({\frac {a_{i}}{x}}*\prod _{t=1}^{n}min({\frac {x}{a_{t}}},1)\right)dx`.

For example, with 3 focuses that have values of 1, 2, and 3 respectively, this formula will result in the chances of `\int _{0}^{1}\left({\frac {x}{2}}*{\frac {x}{3}}\right)dx=\int _{0}^{1}\left({\frac {x^{2}}{6}}\right)dx=\left(\Delta ({\frac {x^{3}}{18}})\right)_{0}^{1}={\frac {1}{18}}` for the first focus, `{\frac {1}{2}}\int _{0}^{2}\left(min(x,1)*{\frac {x}{3}}\right)dx={\frac {1}{2}}\left(\int _{0}^{1}\left({\frac {x^{2}}{3}}\right)dx+\int _{1}^{2}\left({\frac {x}{3}}\right)\right)={\frac {1}{2}}\left(\left(\Delta ({\frac {x^{3}}{9}})\right)_{0}^{1}+\left(\Delta ({\frac {x^{2}}{6}})\right)_{1}^{2}\right)={\frac {1}{2}}\left({\frac {1}{9}}+{\frac {4}{6}}-{\frac {1}{6}}\right)={\frac {11}{36}}` for the second focus, and `{\frac {1}{3}}\int _{0}^{3}\left(min(x,1)*min({\frac {x}{2}},1)\right)dx={\frac {1}{3}}\left(\int _{0}^{1}\left({\frac {x^{2}}{2}}\right)dx+\int _{1}^{2}\left({\frac {x}{2}}\right)dx+\int _{2}^{3}dx\right)={\frac {1}{3}}\left(\left(\Delta ({\frac {x^{3}}{6}})\right)_{0}^{1}+\left(\Delta ({\frac {x^{2}}{4}})\right)_{1}^{2}+\left(\Delta (x)\right)_{2}^{3}\right)={\frac {1}{3}}\left({\frac {1}{6}}+1-{\frac {1}{4}}+3-2\right)={\frac {23}{36}}` for the third focus.

In order to calculate this, let's assume that the rolled value for `a_{i}` landed on `x`. If this is the case, the chance for a given different focus with the value of `a_{t}` to have a rolled value lower than x is `{\frac {x}{a_{t}}}`. However, since this value can exceed `1`, the chance should be capped at that amount with `min({\frac {x}{a_{t}}},1)`.
Since each other focus' generation is an independent event, the chance for all `n` of them to have a value lower than `x`, making the focus `i` picked, is all of these chances multiplied, marked with `\prod _{t=1}^{n}min({\frac {x}{a_{t}}},1)`. However, this exact formula includes `{\frac {x}{a_{i}}}` itself, which shouldn't be a factor since this is the focus that is being calculated. In order to cancel this out from the equation, it can be multiplied by `{\frac {a_{i}}{x}}` to produce `{\frac {a_{i}}{x}}\prod _{t=1}^{n}min({\frac {x}{a_{t}}},1)`
However, this is for a static value of `x`. In practice, `x` can take up any value from `0` to `a_{i}`. As such, to get the exact chance, one needs to calculate an infinite sum of infinitely-small values. This is exactly what integrating it does: `\int _{0}^{a_{i}}\left({\frac {a_{i}}{x}}*\prod _{t=1}^{n}min({\frac {x}{a_{t}}},1)\right)dx`. Though, the scale of this result is unknown instead of being 0–1. The total chance of any focus being picked is `1` at any given point. Therefore, the total upper bound of the scale will be `\int _{0}^{a_{i}}1dx=a_{i}`. In order to find the chance on the scale of 0–1, it'll need to be divided by this result as `{\frac {1}{a_{i}}}\int _{0}^{a_{i}}\left({\frac {a_{i}}{x}}*\prod _{t=1}^{n}min({\frac {x}{a_{t}}},1)\right)dx`, which is the final formula.

### Other <a id="Other"></a>

`will_lead_to_war_with = TAG` is used to mark the focus as leading to a war towards the specified country. This will show up for the specified country and its allies (subjects, overlord, and/or fellow faction members) as the country doing the focus justifying a wargoal on them in the alerts topbar. This also makes the AI prepare for a potential war, both for the country doing the focus and for the country on whom the focus is set to declare war on.

`cancelable = no` will set the focus to be impossible to cancel manually without defining a `select_effect`. This does not prevent the focus from cancelling automatically. However, `cancelable = yes` *does not* make the focus possible to manually cancel if the focus also contains `select_effect = { ... }`.

### Examples <a id="Examples_2"></a>

Pure minimum (at the top of the branch):

**The text in this section has been collapsed by default.**

```text
focus = {
    id = TAG_focus_name
    x = 5
    y = 0
    icon = GFX_focus_icon_name

    cost = 8
    search_filters = { FOCUS_FILTER_MANPOWER }  # Not necessary but recommended, like the icon.

    completion_reward = {
        add_manpower = 1000
    }
}
```

Average focuses:

**The text in this section has been collapsed by default.**

```text
focus = {
    id = TAG_focus_name_2
    x = -1
    y = 1
    relative_position_id = TAG_focus_name # A total position of x = 4 y = 1, with the earlier example
    icon = GFX_other_focus_icon_name
    prerequisite = { focus = TAG_focus_name }
    mutually_exclusive = { focus = TAG_focus_name_3 }

    cost = 8
    will_lead_to_war_with = QAT

    available = {
        country_exists = QAT
        NOT = {
            has_subject = QAT
        }
    }

    ai_will_do = {
        base = 5
        modifier = {
            factor = 0
            has_war = yes
        }
    }

    completion_reward = {
        declare_war_on = {
            target = QAT
            type = annex_everything
        }
    }
}
```

**The text in this section has been collapsed by default.**

```text
focus = {
    id = TAG_focus_name_3
    x = 1
    y = 1
    relative_position_id = TAG_focus_name # A total position of x = 6 y = 1, with the earlier example
    icon = GFX_other_focus_icon_name
    prerequisite = { focus = TAG_focus_name }
    mutually_exclusive = { focus = TAG_focus_name_2 }

    cost = 8
    search_filters = { FOCUS_FILTER_POLITICAL }

    available = {
        country_exists = QAT
        NOT = {
            has_war_with = QAT
        }
    }
    cancel = {
        has_war_with = QAT
    }
    cancel_if_invalid = no
    continue_if_invalid = yes

    text_icon = example_style

    ai_will_do = {
        base = 3
    }

    select_effect = {
        QAT = {
            country_event = my_event.0
        }
    }
    completion_reward = {
        QAT = {
            country_event = my_event.1
        }
    }
}
```

An allow_branch focus:

**The text in this section has been collapsed by default.**

```text
focus = {
    id = TAG_democratic_branch
    x = 10
    y = 0
    offset = {
        x = -8
        trigger = {
            has_completed_focus = TAG_democratic_branch
        }
    }
    icon = GFX_other_focus_icon_name
    mutually_exclusive = { focus = TAG_radical_branch }

    cost = 8
    search_filters = { FOCUS_FILTER_POLITICAL }

    allow_branch = {
        NOT = {
            has_completed_focus = TAG_radical_branch
        }
    }

    completion_reward = {
        add_popularity = {
            ideology = democratic
            popularity = 0.1
        }
        hidden_effect = {
            load_focus_tree = {
                tree = TAG_focus_tree   # Reloads the same focus tree, marking it as completed.
                keep_completed = yes    # Instead of doing load_focus_tree, the mark_focus_tree_layout_dirty can be moved to be within immediate effects of a hidden event that's fired by this focus with no delay.
            }
            mark_focus_tree_layout_dirty = yes  # Updates the offset and allow_branch.
        }
    }
}
```

## Shared focuses <a id="Shared_focuses"></a>

Shared focuses are those that can be used in multiple national focus trees. Examples of these include the "Invite foreign investors" branch present in focus trees for ![Flag of China](media/national_focus_modding_b6347a9782__img144.png) China, ![Flag of Communist China](media/national_focus_modding_b6347a9782__img145.png) Communist China, and ![Flag of Manchukuo](media/national_focus_modding_b6347a9782__img146.png) Manchukuo or the "Rejoin the railways" and "Restore the worker's republic" national focus tree branches for ![Flag of Estonia](media/national_focus_modding_b6347a9782__img147.png) Estonia, ![Flag of Latvia](media/national_focus_modding_b6347a9782__img148.png) Latvia, and ![Flag of Lithuania](media/national_focus_modding_b6347a9782__img149.png) Lithuania.

A shared focus is defined with a `shared_focus = { ... }` block, **not** inside of any `focus_tree = { ... }` block. Within that block, the focus is defined in *exactly* the same way as a regular focus within a focus tree: each of the arguments that can be used in a regular `focus = { ... }` can be used with a `shared_focus = { ... }` without any changes.

A shared focus is added to a focus tree by adding the `shared_focus = my_shared_focus` argument within that focus tree. This will add the specified shared focus **and every shared focus that's connected to it via prerequisites**, assuming that allow_branch is true. Even if the shared focus has a different focus as a prerequisite that's not loaded in this focus tree, it will appear as visible. **Setting this to a non-existing focus causes a game crash when loading into the main menu.** In addition, having no non-shared focuses in your tree while your shared focus is added will result in a crash.

In addition, the [load_focus_tree effect](<effects.md>) can be used with kept completed focuses as such in order to have shared focuses be kept as complete when switching to a different tree:

```text
load_focus_tree = {
    tree = my_focus_tree
    keep_completed = yes
}
```

This can serve as an alternative to using `allow_branch = { ... }` in order to swap out focus tree branches for the same country from being visible or not.

Shared focuses can be defined in any `/Hearts of Iron IV/common/national_focus/*.txt` file. Usually they're kept in different files from the focus trees using them, but that's not necessary.

### Joint focuses <a id="Joint_focuses"></a>

Joint focuses are a subset of shared focuses which also share the completion of focuses between different countries. The effects may apply to the completer, only other countries, or all of them.[4]

A joint focus is defined as a root-level `joint_focus = { ... }` block. Each attribute possible to use in regular national focuses is also possible to use here, with extra additions and changes:

- `joint_trigger = { ... }` is a trigger block that determines which countries are considered joint for this particular focus. This is checked for every country. Completion will be shared between all coun
- `completion_reward = { ... }` functions similarly to regular national focuses, but executes the effects on every country which is joint.
- `completion_reward_joint_originator = { ... }` is a completion reward executed only for the country that has directly completed the focus.
- `completion_reward_joint_member = { ... }` is a completion reward executed to every country where the focus is completed other than the one that has directly completed it.

Other than these, joint focuses are identical to shared focuses.

However, editing the generic tree to have joint focuses will cause the error log to be filled with missing scope error, although if the game was launched in debug mode saving any focus tree will cause the problem to stop for the duration of that session. A shared focus tree that doesn't have joint focuses do not have that problem.

<!-- kit:begin id="focus-joint-shared-vanilla" at="section:Joint_focuses" -->
**Kit addition** Shared and joint focuses in vanilla 1.19.4.1. All counts: [vanilla-confirmed 1.19.4.1] `common/national_focus/`.

- 335 shared focuses sit in 7 files (largest: `toa_shared_military_branch.txt` 76, `china_shared_TSR.txt` 69, `china_shared.txt` 65, `baltic_shared.txt` 60, `paraguay_uruguay_shared_branch.txt` 49).
- 280 joint focuses sit in 8 files: `indonesia_joint.txt` 96, `congo_shared.txt` 57, `nordic_shared.txt` 51, `habsburg_joint.txt` 35, `goe_shared_saadabad_branch.txt` 18, `abdacom_shared_branch.txt` 11, `TSR_lingguang_incident_joint_branch.txt` 7 and `ncns_ma_clique_joint_branch.txt` 5.
- Joint focus keys: `completion_reward_joint_originator` in 263, `completion_reward_joint_member` in 221, `completion_reward` in 168, `joint_trigger` in 135, and `allowed_is_joint = yes` in 12 (7 in `TSR_lingguang_incident_joint_branch.txt`, 5 in `ncns_ma_clique_joint_branch.txt`). [vanilla-confirmed 1.19.4.1] The wiki and `documentation/` do not mention `allowed_is_joint`, and what it does is [unverified].
- All 280 joint focuses set `text_icon`, and 273 set `search_filters`.
<!-- kit:end id="focus-joint-shared-vanilla" -->

### Example <a id="Example"></a>

**The text in this section has been collapsed by default.**

```text
shared_focus = {
    id = LATIN_focus_name
    x = 0
    y = 0
    icon = GFX_LATIN_focus_icon

    search_filters = { FOCUS_FILTER_POLITICAL }

    completion_reward = {
        add_political_power = 100
    }
}
joint_focus = {
    id = LATIN_focus_name_2
    x = 0
    y = 1
    relative_position_id = LATIN_focus_name
    prerequisite = { focus = LATIN_focus_name }
    icon = GFX_LATIN_focus_icon
    text_icon = example_style
    joint_trigger = { is_latin_american_country = yes }

    search_filters = { FOCUS_FILTER_POLITICAL }

    completion_reward = {
        add_political_power = 100
    }
    completion_reward_joint_originator = {
        country_event = latin_america.0
    }
    completion_reward_joint_member = {
        country_event = latin_america.1
    }
}
focus_tree = {
    id = ECU_focus_tree
    country = {
        base = 0
        modifier = {
            add = 10
            original_tag = ECU
        }
    }
    shared_focus = LATIN_focus_name # The second focus will appear automatically
    focus = {
        ...
    }
    focus = {
        ...
    }
}
focus_tree = {
    id = PRU_focus_tree
    country = {
        base = 0
        modifier = {
            add = 10
            original_tag = PRU
        }
    }
    shared_focus = LATIN_focus_name
    focus = {
        ...
    }
    focus = {
        ...
    }
}
```

## Continuous focuses <a id="Continuous_focuses"></a>

Continuous focuses are defined in `/Hearts of Iron IV/common/continuous_focus/*.txt` files. These are the focuses that can be selected after having completed 10 national focuses[5] and which last eternally without being able to complete them entirely.

<!-- kit:begin id="focus-continuous-vanilla" at="section:Continuous_focuses" -->
**Kit addition** Continuous focuses in vanilla 1.19.4.1. All counts: [vanilla-confirmed 1.19.4.1] `common/continuous_focus/generic.txt` and `common/national_focus/`.

- All of vanilla is one file with one palette: `generic.txt` defines `continuous_focus_palette = { id = generic_focus ... }` with `country = { factor = 1 }`, `default = yes`, `reset_on_civilwar = no`, `position = { x = 50 y = 1000 }` and 14 focuses.
- Keys used by the 14 focuses: `id`, `icon`, `available`, `ai_will_do`, `supports_ai_strategy`, `daily_cost` and `available_if_capitulated` in all 14; `modifier` in 11; `enable` in 7; `select_effect` and `cancel_effect` in 4; `idea` in 2.
- Focus trees only place the palette with `continuous_focus_position = { x = ... y = ... }` (57 of the 67 trees). No focus in `common/national_focus/` or `common/continuous_focus/` sets `continuous = yes`; a continuous focus is defined in a palette, not flagged in a tree.
- `NDefines.NCountry.MIN_FOCUSES_FOR_CONTINUOUS = 10` is commented "Focuses needed to unlock continuous focuses". [vanilla-confirmed 1.19.3] `common/defines/00_defines.lua`.
<!-- kit:end id="focus-continuous-vanilla" -->

### Focus palettes <a id="Focus_palettes"></a>

A continuous focus palette is incredibly similar to a definition to a national focus tree, but with less arguments.

`id = my_focus_palette` decides the ID of the focus palette. Mandatory.

`country = { ... }` is a [MTTH block](<ai_modding.md>) that assigns scores to each country for picking a continuous focus palette, in the exact same manner as it's done with national focus trees.

`default = yes` assigns a focus palette as default. As with national focus trees, only one palette should be default total: no more, no less. Defaults to false.

`reset_on_civilwar = no` similarly as with national focuses, has an unknown effect.

`position = { x = 100 y = 1230 }` assigns the default position of the continuous focus palette, measuring in the pixel position of the top left corner. This will get used if the national focus tree of the country doesn't specify a different position that is not `x = 0 y = 0`

`focus = { ... }` are the continuous focuses themselves.

Example:

**The text in this section has been collapsed by default.**

```text
continuous_focus_palette = {
    id = BHR_focus_palette
    country = {
        factor = 0
        modifier = {
            tag = BHR
            add = 10
        }
    }
    position = { x = 50 y = 1000 }
    focus = {
        ...
    }
    focus = {
        ...
    }
}
```

### Focuses <a id="Focuses"></a>

Continuous focuses are also fairly similar to national focuses in definition, but there are substantial differences.

`id = TAG_focus_name` is the continuous focus' ID. There must be no overlap across different palettes. This also gets used as the localisation key for the focus' name and appending `_desc` is used to get the focus' description.

`icon = GFX_focus_icon_name` is the sprite of the icon used by the continuous focus. Similarly to national focus, there must be both a regular icon and a shine for it to always work properly.

`available = { ... }` is a trigger block required to be met for the focus to be *visible*, unlike national focuses where this makes it possible to pick. Instead, the trigger block used for making the focus be possible to pick is `enable = { ... }`. `available_if_capitulated = yes` will also make the focus possible to select while capitulated. If false, the focus will still be visible, but can't be picked.

`modifier = { ... }` is a modifier block that details the list of [modifiers](<modifiers.md>) and their values that are added by having the focus selected. However, there are other ways to apply continuous bonuses aside from modifiers, such as research bonuses for specific categories and equipment bonuses. For these, `idea = idea_name` can be used, which'll add the idea to the country when the focus is selected and remove it when the focus is cancelled. This is recommended to do with hidden ideas, as it shows the effects of the idea when hovering over the focus.

`select_effect = { ... }` and `cancel_effect = { ... }` are effects executed when selecting and unselecting this focus respectively. Since it's possible to select and unselect the focus at any time with no cost, it's recommended to make these be completely the opposite of each other so that doing so will not grant the player any benefit.

`daily_cost = 0.4` is the cost in daily political power gain to take this focus compared to not having any focus selected, can be decimal.

`ai_will_do = { ... }` is a [MTTH block](<ai_modding.md>), working in the exact same way as [ai_will_do in national focuses](#AI_will_do). Additionally, `supports_ai_strategy = AI_focus` makes the focus be possible to pick by AI if [it is following the specified focus](<ai_focuses.md>). Without that, AI would never pick this continuous focus.

Examples:

**The text in this section has been collapsed by default.**

```text
focus = {
    id = BHR_focus_name_1
    icon = GFX_focus_icon_name_1
    daily_cost = 1

    available = {
        has_war = no
    }

    supports_ai_strategy = ai_focus_peaceful

    modifier = {
        stability_weekly = 0.005
        war_support_weekly = -0.001
    }
}
```

**The text in this section has been collapsed by default.**

```text
focus = {
    id = BHR_focus_name_2
    icon = GFX_focus_icon_name_2
    daily_cost = 1.2

    available = {
        has_war = yes
    }
    enable = {
        surrender_progress > 0.5
    }

    ai_will_do = {
        base = 4
        modifier = {
            factor = 2
            surrender_progress > 0.7
        }
        modifier = {
            factor = 2
            surrender_progress > 0.8
        }
    }
    supports_ai_strategy = ai_focus_defense

    modifier = {
        army_defence_factor = 0.2
    }
}
```

## AI strategy plans <a id="AI_strategy_plans"></a>

*Main article: [AI modding § AI Strategy Plans](<ai_modding.md>)*

AI strategy plans to tell AI what to prioritise depending on circumstances: which advisors to pick, which technologies to research, which AI strategies to apply, and, most importantly here, which focuses to pick. This is a short overview of AI strategy plans purely for national focus prioritising, full detail being in the [AI modding](<ai_modding.md>) article. Several AI strategy plans can be enabled at the same time.

AI strategy plans are defined within `/Hearts of Iron IV/common/ai_strategy_plans/*.txt` files. Within these files, a new strategy plan is done as a new block, the name of which must be the same as the internal ID of the plan.

Within that plan, `name = "AI plan's name"` and `desc = "AI plan's description"` decide the name and the description of the strategy plan. *This is never intended to be shown to the player*, so localising it into different languages is never needed. Instead, this is used within the `aiview` console command, which tells info to the developer about what AI wants to prioritise.

`allowed = { ... }` is, similarly to decisions or ideas, is a trigger block **checked only at the game's start**. This is primarily used to tell which country and DLCs to restrict the strategy plan to.

`enable = { ... }` is checked each day if the allowed is met. If `enable = { ... }` is met, then the AI strategy plan will be assigned to the AI regardless of whether `enable = { ... }` turns false later or not. Commonly, [the has_game_rule trigger](<triggers.md>) is used to make it work with custom game rules deciding what path the AI will pick. [is_historical_focus_on](<triggers.md>) is commonly used with the default AI game rule, and country flags can be used for randomisation, by setting up an [on_startup](<on_actions.md>) to set a random one using [random_list](<scopes.md>)

`abort = { ... }` is checked every day in order to make the AI *stop* using this AI strategy plan if `enable = { ... }` is met. Additionally, it must be false in order for the AI strategy plan to be possible to be picked.

`ai_national_focuses = { TAG_focus_name_1 TAG_focus_name_2 }` is a list of national focuses, separated by whitespaces, in the order that the AI should take them. In this example, the AI will try to take TAG_focus_name_1 first if possible. If it's already taken or TAG_focus_name_1 is impossible to take, then AI will try to take TAG_focus_name_2. If both of the focuses are impossible to take due to being completed or unavailable, then it will move on to other focuses, taking `ai_will_do = { ... }` into consideration. While following a focus order, it ignores `ai_will_do = { ... }` values.

`focus_factors = { ... }` assigns a multiplier to ai_will_do values of the specified focus. An entry in this block looks like `TAG_focus_name = 3`. In this case, this will make the ai_will_do value of the focus be multiplied by 3, assuming AI strategy plan's weight of 1. If the focus has an ai_will_do value of 4 after applying modifiers, it'll become 12 if AI is following this strategy plan, and get treated as such. And, of course, a factor of 0 will make the focus be never picked without specification in ai_national_focuses. This can serve as a faster-to-write or a more randomised way to make AI follow a political path by making focuses it should never pick have a value of 0.

`weight = { ... }` is a [MTTH block](<ai_modding.md>) assigning an overall weight to the plan. Defined in the same way as [a national focus' ai_will_do](#AI_will_do), this multiplies each factor within the AI strategy plan by the weight before applying them. A weight of 1.25 will turn a focus factor of 4 into 5 before applying it, for instance. This can be used to make the AI follow the strategy plan more strictly in some cases and less strictly in others.

<!-- kit:begin id="focus-ai-plans-vanilla" at="section:AI_strategy_plans" -->
**Kit addition** AI strategy plans in vanilla 1.19.4.1: 376 plans in 128 files of `common/ai_strategy_plans/`. Keys per plan: `enable` 376, `abort` 368, `name` 366, `allowed` 366, `ideas` 365, `desc` 364, `weight` 362, `ai_national_focuses` 352, `research` 351, `focus_factors` 252, `traits` 125 and `ai_strategy` 61. The keys `ideas`, `research`, `traits` and `ai_strategy` are not covered on this page; see [AI modding](<ai_modding.md>). [vanilla-confirmed 1.19.4.1] `common/ai_strategy_plans/`.

The nine modifiers `ai_focus_aggressive_factor`, `ai_focus_aviation_factor`, `ai_focus_defense_factor`, `ai_focus_military_advancements_factor`, `ai_focus_military_equipment_factor`, `ai_focus_naval_air_factor`, `ai_focus_naval_factor`, `ai_focus_peaceful_factor` and `ai_focus_war_production_factor` are listed in `documentation/modifiers_documentation.md`. [docs]
<!-- kit:end id="focus-ai-plans-vanilla" -->

### Example <a id="Example_2"></a>

**The text in this section has been collapsed by default.**

```text
BHR_historical = {
    name = "Historical plan for BHR"
    desc = "4 focuses in a specific order"
    allowed = {
        tag = BHR
    }
    enable = {
        OR = {
            AND = {
                is_historical_focus_on = yes
                has_game_rule = {
                    rule = BHR_ai_behavior
                    option = DEFAULT
                }
            }
            has_country_flag = BHR_AI_RANDOM_HISTORICAL # Randomly set in on_actions if BHR_ai_behavior is set to RANDOM. Make sure to set that up!
            has_game_rule = {
                rule = BHR_ai_behavior
                option = HISTORICAL
            }
        }
    }
    abort = {
        OMA = {
            OR = {
                has_government = fascism
                has_government = communism
            }
        }
    }
    ai_national_focuses = {
        BHR_focus_name_1
        BHR_focus_name_2
        BHR_focus_name_3
        BHR_focus_name_4
    }
}
BHR_alternate = {
    name = "Alternative plan for BHR"
    desc = "AI is just set to never do BHR_focus_name_2 and be more likely to do BHR_focus_name_5, especially if after 1937"
    enable = {
        OR = {
            has_country_flag = BHR_AI_RANDOM_ALTERNATE # Randomly set in on_actions if BHR_ai_behavior is set to RANDOM. Make sure to set that up!
            has_game_rule = {
                rule = BHR_ai_behavior
                option = ALTERNATE
            }
        }
    }
    focus_factors = {
        BHR_focus_name_2 = 0
        BHR_focus_name_5 = 2
    }
    weight = {
        modifier = {
            factor = 2
            date > 1937.1.1
        }
    }
}
```

## Notes <a id="Notes"></a>

**^** **a:** Dynamic countries, when created, will go through the check assigning a focus tree again. As well as that, reloading focuses by saving over a focus tree file while the debug mode is turned on via launch settings will also refresh this check.
**^** **b:** The default position is defined within the pallete's definition in a `/Hearts of Iron IV/common/continuous_focus/*.txt` file
**^** **c:** The exact size of a single x and y coordinate unit uses the focus_spacing positionType within `/Hearts of Iron IV/interface/nationalfocusview.gui`
**^** **d:** If [mark_focus_tree_layout_dirty](<effects.md>) is put within a focus reward, it wouldn't be marked as complete for the [has_completed_focus](<triggers.md>) trigger at the time it's executed. This can be avoided by using a hidden event, fired immediately, which has the effect to refresh the check within its immediate. Alternatively, the [load_focus_tree](<effects.md>) effect, set to have the focuses kept complete, can be used to mark the focus as complete before doing the refreshing.
**^** **e:** Within folder paths, a backslash (\\) can result in the game not being able to read the folder, since it's expected to be used as an escape character. Instead, it's preferable to use forward slashes, as in `texturefile = gfx/interface/goals/my_file.dds`.

## References <a id="References"></a>

1. ↑ `NDefines.NFocus.FOCUS_POINT_DAYS = 7` in [Defines](<defines.md>).
2. ↑ `NDefines.NFocus.FOCUS_PROGRESS_PEACE = 1` and `NDefines.NFocus.FOCUS_PROGRESS_WAR = 1` in [Defines](<defines.md>)
3. ↑ `NDefines.NAI.FOCUS_TREE_CONTINUE_FACTOR = 1.5` in [Defines](<defines.md>).
4. ↑ Developer Diary | Modding!, Paradox developer diary for 1.13.
5. ↑ `NDefines.NCountry.MIN_FOCUSES_FOR_CONTINUOUS = 10` in [Defines](<defines.md>).

Note that while modifying defines to use a define override file rather than copying over the entire file, as even otherwise 'minor' updates can add new defines causing potential crashes.

---

## Navigation

**[Modding](<modding.md>)**

- **Documentation**: [Effects](<effects.md>) • [Triggers](<triggers.md>) • [Defines](<defines.md>) • [Modifiers](<modifiers.md>) • [List of modifiers](<list_of_modifiers.md>) • [Scopes](<scopes.md>) • [Localisation](<localisation.md>) • [On actions](<on_actions.md>) • [Data structures](<data_structures.md>) • [Flags](<data_structures.md#Flags>) • [Event targets](<data_structures.md#Event_targets>) • [Country tag aliases](<data_structures.md#Country_tag_aliases>) • [Variables](<data_structures.md#Variables>) • [Arrays](<data_structures.md#Arrays>)
- **Scripting**: [Achievements](<achievement_modding.md>) • [AI](<ai_modding.md>) • [AI focuses](<ai_focuses.md>) • [Autonomous states](<autonomy_state_modding.md>) • [Balances of power](<balance_of_power_modding.md>) • [Bookmarks/Scenarios](<bookmark_modding.md>) • [Game rules](<bookmark_modding.md#Game_rules>) • [Buildings](<building_modding.md>) • [Characters and traits](<character_modding.md>) • [Cosmetic tags](<cosmetic_tag_modding.md>) • [Countries](<country_creation.md>) • [Divisions](<division_modding.md>) • [Decisions](<decision_modding.md>) • [Doctrines](<doctrine_modding.md>) • [Equipment](<equipment_modding.md>) • [Events](<event_modding.md>) • [Factions](<faction_modding.md>) • [Ideas](<idea_modding.md>) • [Ideologies](<ideology_modding.md>) • [Military industrial organizations](<military_industrial_organization_modding.md>) • [Resources](<resources_modding.md>) • [Scripted GUI](<scripted_gui_modding.md>) • [Technologies and doctrines](<technology_modding.md>) • [Units](<unit_modding.md>)
- **Map**: [Map](<map_modding.md>) • [States](<state_modding.md>) • [Supply areas](<supply_areas_modding.md>) • [Strategic regions](<strategic_region_modding.md>)
- **Graphical**: [Interface](<interface_modding.md>) • [Graphical assets](<graphical_asset_modding.md>) • [Entities](<entity_modding.md>) • [Posteffects](<posteffect_modding.md>) • [Particles](<particle_modding.md>) • [Fonts](<font_modding.md>)
- **Cosmetic**: [Portraits](<portrait_modding.md>) • [Namelists](<namelist_modding.md>) • [Music](<music_modding.md>) • [Sound](<sound_modding.md>)
- **Other**: [Console commands](<console_commands.md>) • [Troubleshooting](<troubleshooting.md>) • [Mod structure](<mod_structure.md>) • [Mods](<mods.md>) • [Nudger](<nudger.md>)
- **Kit pages (not on the wiki)**: [Collection modding](<collection_modding.md>) • [Defines additions](<defines_additions.md>) • [Game rule modding](<game_rule_modding.md>) • [Intelligence operation modding](<intelligence_operation_modding.md>) • [Map mode modding](<map_mode_modding.md>) • [Occupation and resistance modding](<occupation_and_resistance_modding.md>) • [Peace conference modding](<peace_conference_modding.md>) • [Raid modding](<raid_modding.md>) • [Script constant modding](<script_constant_modding.md>) • [Special project modding](<special_project_modding.md>)
