# Interface modding

The graphical user interface elements are defined within `/Hearts of Iron IV/interface/*.gui` files, as typical code formatting. The files only decide on the positions of how elements are arranged, [scripted GUI](scripted_gui_modding.md) is used to assign effects to newly-created interface elements.

## Overview

The interface consists of [container windows (or containers)](#containers) and elements within them. Each element, other than containers, must reside in a container. Containers can be nested in other elements to organise their positions. Gridboxes are used to clone the same container several times, with different details specified for each one. Newly-added elements can have their effects defined in [scripted GUI](scripted_gui_modding.md), while the effects of base game's GUI are hard-coded, that is, it's impossible to modify what it does directly.

The elements are shown in the order that they are defined in the file: what's placed later will be shown on top of what's placed earlier. The files are contained within a `guiTypes = { ... }` block overarching the entire file.

What vanilla `interface/*.gui` contains in 1.19.4.1, as a base for the checks below.

- Every file is wrapped in one `guiTypes = { ... }` block (132 of 132). Element type names and attribute names are case-insensitive: vanilla writes both `instantTextboxType` (1,735) and `instantTextBoxType` (1,063), `gridBoxType` and `gridboxtype`, `buttonType` and `ButtonType`, `orientation` and `Orientation`.
- Block counts: `iconType` 3,054; `instantTextBoxType` 2,798; `buttonType` 2,054; `containerWindowType` 2,024; `gridBoxType` 596; `guiButtonType` 340; `positionType` 160; `checkboxType` 164; `editBoxType` 85; `windowType` 83; `OverlappingElementsBoxType` 46; `dropDownBoxType` 38 (each with an `expandedWindow`); `scrollbarType` 31; `listboxType` 30; `textBoxType` 23; `extendedScrollbarType` 22; `smoothListboxType` 14; `browserType` 1.
- Sprites for the elements are defined in `.gfx` files next to the `.gui` files; see [Graphical asset modding](graphical_asset_modding.md).
- Percent sizes are written both as `100%%` (706 uses) and as `100%` (348 uses), counting any number before the sign. Both occur in vanilla, so the page's two spellings are both fine.

**Size forms.** The same `size` key takes two shapes depending on the element:

| Element | Blocks that set `size` | Form |
| --- | --- | --- |
| `containerWindowType` | 1,809 of 2,024 | `{ width = .. height = .. }`; 13 add `min = { width = .. height = .. }` (12 in the tech tree, one in `frontendmainview.gui`, which also writes `max` and `preserve_aspect_ratio`) |
| `gridBoxType` | 546 of 596 | `{ width = .. height = .. }` |
| `extendedScrollbarType`, `dropDownBoxType`, `expandedWindow` | 22, 27, 38 | `{ width = .. height = .. }` |
| `buttonType` | 82 of 2,054 | `{ x = .. y = .. }` in all 82 |
| `guiButtonType`, `editBoxType`, `windowType`, `scrollbarType`, `listboxType`, `smoothListboxType`, `OverlappingElementsBoxType`, `browserType` | 7, 85, 80, 31, 30, 14, 46, 1 | `{ x = .. y = .. }` |
| `iconType`, `instantTextBoxType`, `checkboxType` | 0 | none; icons and checkboxes take their size from the sprite and text boxes use `maxWidth` and `maxHeight` |

A `buttonType` that sets a size, from `interface/airselectionview.gui`: `size = {x = 220 y = @equipment_entry_heigth}`.

## Constants

*This section is transcluded from [Data structures § Constants](data_structures.md#constants)*

Constants serve as a way to use the same value with a reference. The constants are marked with the `@` symbol when defining or using them. An example definition is the following:

```text
@CONSTANT_1 = 10
@CONSTANT_2 = "TAG_my_idea"
```

This can later be used in the file as, for example, `cost = @CONSTANT_1`. These definitions can be in any point of the file.

Constants are available in the vast majority of game files, including most, if not all, \*.txt and \*.gui files. Constants can be used as a way to link several values to be the same if they can easily be changed at any point in the development. However, constants that store a string for its value can only be used in triggers and the attributes of elements and windows, trying to use them in an effect will result in an "invalid database object for effect/trigger" error.
For example, if there is a large decision system where every decision is intended to have the same cost, then these constants may be used if the political power cost gets changed mid-development for better balance.
Another example would be a scripted GUI container: if a large multitude of elements are to be at the same X or Y position, it might be worth it to link them to be a constant in case their position could be changed for better appearance or to fit in another GUI element.

Example [decision file](decision_modding.md) that utilises constants:

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

Vanilla `.gui` files define their own constants: 238 `@name = value` definitions in 31 of the 132 files, used for positions and sizes, for example `size = {width = 220 height = @equipment_entry_heigth}` in `interface/airselectionview.gui`.

## Containers

Containers are used to group together elements and associate them with an internal function, written as a `containerWindowType = { ... }` block.

New containers that are independent (not inside of any other container) will not show up in-game by default. For one to show up, it is required for it to be tied to a function, such as [scripted GUI](scripted_gui_modding.md), which decides where it should show and when. In some cases, new containers can be created for the internally-defined functions, such as [new technology folders](technology_modding.md#graphical-user-interface) or [getting a music station to show up](music_modding.md#radio-stations). In most cases, however, a scripted GUI would be required to make a new container show up.

If a container is defined within another container, it will appear at the same time as the window containing it unless more information is defined within the function. A scripted GUI cannot be assigned to such a container, however. In some cases, it's not necessary for a container to be visible to be useful, for example, an empty container can be used as an anchor, that is, used as the [parent window name](scripted_gui_modding.md) for Scripted GUI to place another container on the same place as the anchor is defined. This can allow placing containers with higher precision than normally possible with `parent_window_name`, allowing the parent window to have elements drawn on top of the scripted GUI.

### Arguments

The following attributes are commonly used:

- `name = "my_container"` – The name of the container, used to tie a function to the container. Independent containers must have unique names. While nested containers may have name overlap when defined in different independent containers, it's still preferable to avoid overlap, such as to ensure unambiguity when using `parent_window_name` in scripted GUI.
- `size = { height = 300 width = 100%% }` – The bounding box for the container. If this container is placed inside of another one, either directly or through a gridbox, then only this size is used to create the scrollbar, without taking into account elements inside. This boundary also sets the size that the scrollbar must use. Either in pixels or in percentages relative to the size of the parent container (the entire screen if independent).
- `background = { ... }` – The background of the container. This is required for a scrollbar to work, as otherwise the boundaries will get ignored. There are the following arguments inside:
  - `name = "Background"` – The name for handling the background in other functions. Commonly just set to "Background".
  - `spriteType = "GFX_tiled_window"` or `quadTextureSprite = "GFX_tiled_window_transparent"` – Refers to a [corneredTileSpriteType](graphical_asset_modding.md#corneredtilespritetype) definition that would automatically get resized to fit the container's set size.
- `clipping = yes` – If true (and if a background exists), the elements inside of the container will not be able to go outside of the boundary box, and what doesn't fit will get cropped. Defaults to true. This being true is mandatory for a scrollbar to work.
- `position = { x = 100 y = 100 }` – The position of the container in pixels relative to the set orientation and set origo.
- `orientation = center` – Sets the origin that the position is measured relative to, such as `upper_left`, `center_down`, or `lower_right` for the screen.
- `origo = center` – Sets the origin that the position is measured relative to, such as `upper_left`, `center_down`, or `lower_right` for the element.
- `moveable = yes` – If set, the container can be moved by the player with their cursor.
- `fullScreen = yes` – If set, the container will be considered to cover the entire screen.

Animation can be assigned to containers with these attributes:

- `show_position = { x = 300 y = 100 }` – The screen position where the container will show up to the player after the 'show' animation finishes.
- `hide_position = { x = 100 y = 100 }` – The screen position the container aims for during the 'hide' animation.
- `show_animation_type = linear` – The animation type used to show the container (`decelerated` or `linear`).
- `hide_animation_type = accelerated` – The animation type used to hide the container (`accelerated` or `linear`).
- `animation_type = decelerated` – The animation if both show and hide animations are supposed to be the same (`accelerated`, `decelerated`, or `linear`).
- `animation_time = 1000` – The animation time in milliseconds.
- `show_sound = menu_open_window` – The [sound](sound_modding.md) to play during the 'show' animation.
- `hide_sound = menu_close_window` – The [sound](sound_modding.md) to play during the 'hide' animation.
- `fade_time = 300` – The time it takes for the container to fade in, in milliseconds.
- `fade_type = linear` – The type of fade in: either `accelerated` or `linear`.

The container attributes of this page against the 2,024 vanilla `containerWindowType` blocks.

| Attribute | Vanilla use |
| --- | --- |
| `size` | 1,809 blocks; `min = { width = .. height = .. }` is accepted inside it (13 blocks: 12 in `countrytechtreeview.gui` and one in `frontendmainview.gui`) |
| `background` | 1,006 blocks |
| `clipping` | 705 blocks: `no` 640, `yes` 65. Writing `no` is the common case, so the default really is on, as the page says |
| `position`, `orientation` | 1,812 and 547. Orientation values seen: `upper_left` 265, `center` 129, `center_right` 42, `lower_left` 31, `center_up` 30, `upper_right` 26, `lower_right` 13, `center_down` 8, `center_left` 3 |
| `origo` | 67: `center` 45, `center_up` 9, `lower_right` 4, `upper_right` 3, `lower_left` 3, `center_down` 2, `upper_left` 1 |
| `moveable` | 199: `yes` 176, `no` 23 |
| `fullScreen` | 0 on `containerWindowType`; it appears in 67 `windowType` blocks (`no` 62, `yes` 5) |
| `show_position`, `hide_position` | 87 and 5 |
| `show_animation_type`, `hide_animation_type`, `animation_type` | 63, 63 and 9. Values: `decelerated` for show (63) and for `animation_type` (9); `accelerated` for hide (61), plus one `linear` and one `decelerated` |
| `animation_time`, `fade_time`, `fade_type` | 72, 109 and 108; `fade_type` is always `linear` |
| `show_sound`, `hide_sound` | 65 and 26; common values `menu_open_window`, `pop_up`, `diplomatic_notification` for show and `menu_close_window` for hide |
| `verticalScrollbar`, `horizontalScrollbar` | 254 and 24. All 313 references (containers and other blocks) resolve to an `extendedScrollbarType` definition |
| `drag_scroll` | 23, always `{ left middle }` |
| `margin` | 170, written as `{ top = .. bottom = .. left = .. right = .. }` with any subset of the four |
| `scroll_wheel_factor`, `smooth_scrolling` | 138 and 128; `smooth_scrolling = yes` in all 128 and a factor of 40 in 73 of the 138 |
| `autohide_scrollbars` | 1 (`no`) |

Attributes that vanilla containers use and the page does not mention: `click_to_front = yes` (120), `vertical_scroll_step` (15), `background_margin` (11, for example `{ bottom = 15 }`), `scale` (8) and, once each in a sliding window, `closed_position`, `open_position`, `peek_position`, `peek_check_top_left` and `peek_check_size`. Their effects are read from the names only and are untested. (unverified)

### Scrolling

Scrolling can be done via scrollbars. If scrollbars are enabled, it's also possible to enabled it with dragging the screen. Since the game has to know what should be inside of the container, there are some attributes which must be used in the container. `size = { ... }` has to be defined using pixels instead of percentage values (for directions where scrolling is enabled) to ensure that it doesn't stretch to fit all elements. `clipping = yes` should be true (or unset, making it default to true). A `background = { ... }` also has to be defined for the container, since it establishes the boundaries.

Scrollbars use extendedScrollbarType definitions. If this definition is inside of a container, in which case it will be automatically assigned to the container without needing to assign it manually, however it can't be used for any other container. If the definition is entirely independent, it will not be assigned to any by default, but can be re-used in multiple containers.

In particular, these arguments enable scrolling, assuming the conditions are fulfilled:

- `verticalScrollbar = scrollbar_name` assigns an external ExtendedScrollbarType to act as the vertical scrollbar. The scrollbar can't have `horizontal = yes` in its definition.
- `horizontalScrollbar = scrollbar_name` assigns an external ExtendedScrollbarType to act as the horizontal scrollbar. The scrollbar must have `horizontal = yes` in its definition.
- `drag_scroll = { left middle right }` enables drag scrolling. The drag scrolling will only work if there exists a scrollbar for the same axis. The direction represent the mouse button that the scrolling can be done with, however only `left` seems to work in-game. If there's only one button, it can be shortened as `drag_scroll = left`.

In addition, there are optional attributes that can be used to refine the scrollbar:

- `margin = { top = 10 bottom = 10 left = 20 right = 20 }` is used to determine the margins of the container. These areas will be taken as the border of the window, unaffected by the scrollbar; only what's inside of the margin's border will be modified by the scrollbar.
- `autohide_scrollbars = no` – By default, a scrollbar will not appear if it isn't necessary due to all elements being inside of the container's `size`. If this is set to false, then it will always appear.
- `scroll_wheel_factor = 40` determines how much a single mouse scroll will affect the scrollbar.
- `smooth_scrolling = yes` enables a smoother scrolling animation.

## scrollbarType

The **scrollbarType** is used to define which elements a scrollbar is composed of.

The following attributes are used:

- **name** - The scrollbar name.
- **slider** - The button element to use as the scrollbar slider.
- **track** - The button element to use as the scrollbar tracker.
- **leftbutton** - The button element to use as the scrollbar left increment button.
- **rightbutton** - The button element to use as the scrollbar right increment button.
- **position** - The screen position of the scrollbar.
- **size** - The bounding box for the scrollbar.
- **priority** - The priority the scrollbar has over other elements.
- **borderSize** - The bounding box for border of the scrollbar.
- **maxValue** - The maximum value the scrollbar moves to (used to control the increments).
- **minValue** - The minimum value the scrollbar moves to (used to control the increments).
- **stepSize** - The size of increments using the increment button.
- **startValue** - The initial size the slider for the scrollbar starts at.
- **horizontal** - Sets whether the scrollbar is horizontal (1) or vertical (0).

All 14 attributes in the list above (`name`, `slider`, `track`, `leftbutton`, `rightbutton`, `position`, `size`, `priority`, `borderSize`, `maxValue`, `minValue`, `stepSize`, `startValue`, `horizontal`) appear in every one of the 31 vanilla `scrollbarType` blocks, plus one `scroll_speed`. `horizontal` is the number 1 in 28 blocks and 0 in 3. `scrollbarType` is what list boxes and text boxes name in their `scrollbarType = ...` attribute: `standardlistbox_slider` (43 uses) and `standardtext_slider` (27).

The scrollbar of a container is a different element, `extendedScrollbarType`, which the "Scrolling" section mentions without listing its attributes. The 22 vanilla blocks use `name`, `position`, `size` (`{ width = .. height = .. }`), `startValue` (22), `slider` (22), `track` (21), `decreaseButton` and `increaseButton` (18 each), `background` (14), `tileSize`, `maxValue`, `minValue`, `stepSize`, `horizontal` (10 each, written `yes`), `orientation` and `origo` (8 each), `clickOnly` (6), `smooth_scrolling` (4, with values such as 0.25 and 1.25) and `setTrackFrameOnChange` (2). All 313 `verticalScrollbar` and `horizontalScrollbar` references in vanilla point at an `extendedScrollbarType`.

## Elements

There are multiple element types used within containers. All elements must be used within containers, they will not work outside of one.

Elements will inherit the orientation of the containers they are located in unless the orientation is specified for the element itself.

The following elements can be freely added and are usable with scripted GUIs.

- **iconType** - Used for static images.
- **instantTextBoxType** - Used for text.
- **buttonType** - Used for buttons

The following elements do rely on internal code. You can add new elements, they will not be populated with data.

- **smoothListboxType** - Used for smooth scrollable lists.
- **listboxType** - Used for scrollable lists.
- **checkboxType** - Used for checkboxes.
- **OverlappingElementsBoxType** - Used for overlapping many elements.
- **editBoxType** - Used for editable textboxes.
- **shieldtype** - Used for to display country flags.

The following elements are legacy:

- **guiButtonType** - Same as *buttonType*.
- **textBoxType** - Same as *instantTextBoxType*.
- **eu3dialogtype** - Same as *windowType*.
- **shieldtype** - Only used within *eu3dialogtype*. Different elements are used for flags in more recent files.

Checks of the lists above.

- `shieldtype` and `eu3dialogtype` are not used by any of the 132 vanilla `.gui` files. Country flags in vanilla come from `maskedShieldType` sprites in `.gfx` files (`interface/core.gfx`, `interface/general_stuff.gfx`, `interface/countryconstructionsview.gfx`), not from a `.gui` element.
- The "legacy" types are still used widely: `guiButtonType` 340 blocks, `windowType` 83 and `textBoxType` 23. `guiButtonType` has the attributes of `buttonType` plus `parent` (28 blocks); `windowType` groups children and writes `moveable` as 0 or 1, `fullScreen`, `horizontalBorder` and `verticalBorder`, `dontRender` and `background`. For new windows prefer `containerWindowType` and `buttonType`, the types the page names as current. That is advice, and no defined test shows it. (unverified)
- Element types in vanilla that the page does not describe are covered in the section "Element types the page does not describe" at the bottom of the page.

## iconType

The *iconType* element is used to add images to the interface. It's usage overlaps with *buttonType*, which is similar but operates as a button.

The following attributes are used:

- **name** - The icon name.
- **position** - The screen position of the icon.
- **orientation** - Sets the orientation origin for the *position* attribute.
- **spriteType** - The image to use for the icon. Refers to a *spriteType* definition.
- **quadTextureSprite** - The image to use for the icon. Refers to a dynamic *spriteType* definitions (i.e. flags) or multi-frame *spriteType* definitions.
- **frame** - Which frame to use for the icon when using a multi-frame image.
- **alwaystransparent** - Forces the icon to allow click through, i.e. clicking on an element behind another element.
- **hint_tag** - Set the hint key the icon uses to display a hint tooltip with when hovered over.
- **pdx_tooltip** - The tooltip that is shown when hovering over the button.
- **pdx_tooltip_delayed** - Sets the delayed tooltip to display to the player. Takes a localization key.
- **centerposition** - Sets whether the position is from the center of the icon.

The attribute list against the 3,054 vanilla `iconType` blocks.

- Used: `name` (3,054), `position` (2,979), `spriteType` (2,525), `alwaystransparent` (1,175), `orientation` (547), `quadTextureSprite` (498), `frame` (392), `centerposition` (321, always `yes`), `pdx_tooltip` (117), `pdx_tooltip_delayed` (2), `hint_tag` (1).
- Used but missing from the page: `scale` (395, values such as 0.6, 0.7, 0.8, 0.9), `hide` (57, `hide = yes`), `rotation` (52, mostly 1.5708, which looks like a quarter turn in radians), `context_aware_tooltip` (40, a scripted localisation call such as `[GetNavalFactionDesc]`), `tooltip` (10, a localisation key) and `buttonMesh` (1). The meanings of `scale`, `rotation` and `hide` are inferred from the values. (unverified)
- No `iconType` writes `size`. The icon is drawn at the size of its sprite, scaled by `scale`. (unverified)
- `spriteType` is the common choice (2,525) over `quadTextureSprite` (498).

## instantTextBoxType

The *instantTextBoxType* element is used to add text to the interface. In some instances, the text for the element is generated internally (i.e. *regiment_count*). In these instances you cannot edit the text unless it is exposed in an localized string.

The following attributes are used:

- **name** - The textbox name.
- **position** - The screen position of the textbox.
- **orientation** - Sets the orientation origin for the *position* attribute.
- **text** - The text displayed by the textbox.
- **font** - The font to use for the text.
- **maxWidth** - The total width in pixels at which text is displayed.
- **maxHeight** - The total height in pixels at which text is displayed.
- **format** - How the text is aligned.
- **fixedsize** - Whether the textbox should truncate text that exceeds its limits.
- **borderSize** - The bounding box for the border of the textbox.
- **alwaystransparent** - Forces the text to allow click through, i.e. clicking on an element behind another element.
- **scrollbarType** - which kind of scrollbar to use (for example standardtext_slider)
- **pdx_tooltip** - Sets the tooltip to display to the player. Takes a localization key.
- **pdx_tooltip_delayed** - Sets the delayed tooltip to display to the player. Takes a localization key.

The following attributes are rarely or never used:

- **textureFile** - Never used for anything.

Valid *format* values:

- left
- center
- right

The attribute list against the 2,798 vanilla `instantTextBoxType` blocks.

- Used as the page says: `name`, `position` (2,795), `font` (2,772), `maxWidth` (2,751), `maxHeight` (2,546), `format` (2,457), `text` (2,259), `borderSize` (879, written `{ x = .. y = .. }`), `fixedsize` (865), `alwaystransparent` (590), `orientation` (488), `pdx_tooltip` (157), `scrollbarType` (29, always a scrollbar such as `standardtext_slider`).
- `format` takes `left` (1,037), `center` (988), `centre` (252) and `right` (181). The page lists three values; `centre` is a fourth spelling in common use.
- `pdx_tooltip_delayed` is listed on the page but no `instantTextBoxType` writes it.
- `textureFile` is written in 607 blocks, almost always as an empty string (`textureFile = ""` in 630 of 657 uses across all types), which fits "never used for anything".
- Used but missing from the page: `vertical_alignment` (117: `center` for nearly all, `top` for 4), `multiline` (72), `context_aware_text` (39, a localisation key or a scripted localisation call), `truncate` (33, `yes` in 32), `context_aware_tooltip` (2), `text_color_code` (29, a one-letter colour code such as `b`, `g` or `L`), `tooltip` (14) and `hide` (4). Their meanings are read from the names and are untested. (unverified)

## buttonType

The *guiButtonType'* element is used to add buttons to the interface. Buttons are composed of an image and text, so they operate in a similar manner to *iconType* and *instantTextBoxType*.

The following attributes are used:

- **name** - The button name.
- **position** - The screen position of the button.
- **orientation** - Sets the orientation origin for the *position* attribute.
- **spriteType** - The image to use for the button. Refers to a *spriteType* definition.
- **quadTextureSprite** - The image to use for the button. Refers to a dynamic *spriteType* definitions (i.e. flags) or multi-frame *spriteType* definitions.
- **frame** - Which frame to use for the button when using a multi-frame image.
- **alwaystransparent** - Forces the button to allow click through, i.e. clicking on an element behind another element.
- **buttonText** - The text displayed by the button.
- **buttonFont** - The font to display the button text in.
- **shortcut** - The shortcut to add for this button.
- **clicksound** - The sound to use when clicked.
- **oversound** - The sound to play when hovered over.
- **hint_tag** - Set the hint key the icon uses to display a hint tooltip with when hovered over.
- **pdx_tooltip** - The tooltip that is shown when hovering over the button.
- **pdx_tooltip_delayed** - Sets the delayed tooltip to display to the player. Takes a localization key.
- **scale** - Scales the button size.
- **web_link** - URL to open in browser

The following attributes are rarely or never used:

- **tooltip** - Never used.
- **tooltipText** - Never used.
- **delayedTooltipText** - Never used.

The attribute list against the 2,054 vanilla `buttonType` blocks.

- Used as the page says: `name`, `position` (2,003), `quadTextureSprite` (1,457), `clicksound` (1,414), `spriteType` (598), `buttonFont` (586), `orientation` (554), `pdx_tooltip` (434), `buttonText` (415), `shortcut` (368), `oversound` (300), `frame` (270), `scale` (136), `web_link` (76), `alwaystransparent` (43), `pdx_tooltip_delayed` (36). `quadTextureSprite` is the common sprite key for buttons, more than twice as common as `spriteType`.
- `tooltip` is **not** "never used": 29 buttons write it, with a localisation key (`tooltip = "LEDGER_CIV_GRAPH_SHOW_INDUSTRY"`). `tooltipText` and `delayedTooltipText` have no use. `hint_tag` is listed on the page but no `buttonType` writes it.
- Used but missing from the page: `size` (82, always `{ x = .. y = .. }`), `font` (313) and `text` (180) next to `buttonFont` and `buttonText`, `pdx_tooltip_anchor` (55), `centerposition` (52), `no_clicksound` (21, always `yes`), `format` (17), `enabled` (8, always `no`), `borderSize` (6), `multiline` (3), `pdx_disabled_tooltip` and `pdx_disabled_tooltip_delayed` (1 each), `rotation` (1), `hide` (2) and `keybind` (12, a name such as `air_wings_split`, written mostly in files the 1.19.4.1 update changed).
- The vanilla files contain two typos you should not copy: `format = left;` with a semicolon, in two buttons.
- The heading of this section describes `guiButtonType`, a typo in the wiki text. `buttonType` is the current spelling; `guiButtonType` (340 blocks) also still works.

## smoothListboxType

The *smoothListboxType* element is used to define a listbox, which is a scrollable list that is populated with entries. Typically these elements are internally linked with another container, which composes the actual entry used in the list box.

The following attributes are used:

- **name** - The listbox name.
- **position** - The screen position of the listbox.
- **orientation** - Sets the orientation origin for the *position* attribute.
- **size** - The bounding box for the listbox.
- **spacing** - The spacing to use between listbox entries.
- **horizontal** - Whether the listbox is horizontal (1) or vertical (0).
- **scrollbartype** - The scrollbar to use for the listbox.
- **bordersize** - The bounding box for the border for the listbox.
- **alwaystransparent** - Forces the listbox to allow click through, i.e. clicking on an element behind another element.

The following attributes are rarely or never used:

- **background** - Never used.

Of the 14 vanilla `smoothListboxType` blocks, all write `name`, `position` and `size`; 13 write `scrollbarType`, and the rest of the page's list is rarely used (`orientation` 6, `bordersize` 6, `spacing` 3). `horizontal` and `alwaystransparent` appear in none, while `priority` (3) and `clipping` (2) do. `background` has no use, as the page says.

## listboxType

The *listboxType*  element is used to define a listbox, which is a scrollable list that is populated with entries. Typically these elements are internally linked with another container, which composes the actual entry used in the list box.

The following attributes are used:

- **name** - The listbox name.
- **position** - The screen position of the listbox.
- **orientation** - Sets the orientation origin for the *position* attribute.
- **size** - The bounding box for the listbox.
- **spacing** - The spacing to use between listbox entries.
- **horizontal** - Whether the listbox is horizontal (1) or vertical (0).
- **scrollbartype** - The scrollbar to use for the listbox.
- **bordersize** - The bounding box for the border for the listbox.
- **alwaystransparent** - Forces the listbox to allow click through, i.e. clicking on an element behind another element.

The following attributes are rarely or never used:

- **background** - Never used.

`background` is not "never used" on `listboxType`: 21 of the 30 vanilla `listboxType` blocks write it. The other attributes: `name`, `position`, `size` (all 30, `{ x = .. y = .. }`), `scrollbarType` (28), `orientation` (25), `spacing` (24), `bordersize` (19), `horizontal` (9, always 0), `alwaystransparent` (3), `priority` (2) and `offset` (2).

## checkboxType

The *checkboxType*  element is used to add checkboxes to the interface. The actual effect of the checkbox is defined internally.

The following attributes are used:

- **name** - The checkbox name.
- **position** - The screen position of the checkbox.
- **orientation** - Sets the orientation origin for the *position* attribute.
- **spriteType** - The image to use for the checkbox. Refers to a *spriteType* definition.
- **quadTextureSprite** - The image to use for the checkbox. Refers to a dynamic *spriteType* definitions (i.e. flags) or multi-frame *spriteType* definitions.
- **frame** - Which frame to use for the checkbox when using a multi-frame image.
- **alwaystransparent** - Forces the checkbox to allow click through, i.e. clicking on an element behind another element.
- **buttonText** - The text displayed by the checkbox.
- **buttonFont** - The font to display the checkbox text in.
- **shortcut** - The shortcut to add for this checkbox.
- **clicksound** - The sound to use when clicked.
- **hint_tag** - Set the hint key the checkbox uses to display a hint tooltip with when hovered over.
- **pdx_tooltip** - Set the short tooltip this checkbox uses.
- **pdx_tooltip_delayed** - Set the full tooltip this checkbox uses.
- **scale** - Scales the checkbox size.

The following attributes are rarely or never used:

- **tooltip** - Never used.
- **tooltipText** - Never used.
- **delayedTooltipText** - Never used.

All 164 vanilla `checkboxType` blocks use `quadTextureSprite` and none uses `spriteType`. Attributes in use: `name`, `position`, `quadTextureSprite` (164 each), `clicksound` (104), `orientation` (60), `buttonFont` (51), `buttonText` (44), `pdx_tooltip` (9), `frame` (5), `tooltip` (1, in `countryintelligenceagencyview.gui`) and `pdx_tooltip_delayed` (1). `shortcut`, `scale`, `hint_tag` and `alwaystransparent` are listed on the page and written by no vanilla checkbox. `tooltipText` and `delayedTooltipText` are unused, as the page says, but `tooltip`, which the page calls never used, now appears in one checkbox.

## editBoxType

The *editBoxType* element is used to add editable textboxes to the interface.

The following attributes are used:

- **name** - The textbox name.
- **position** - The screen position of the textbox.
- **orientation** - Sets the orientation origin for the *position* attribute.
- **text** - The text displayed by the textbox.
- **font** - The font to use for the text.
- **maxWidth** - The total width in pixels at which text is displayed.
- **maxHeight** - The total height in pixels at which text is displayed.
- **format** - How the text is aligned.
- **fixedsize** - Whether the textbox should truncate text that exceeds its limits.
- **borderSize** - The bounding box for the border of the textbox.
- **alwaystransparent** - Forces the text to allow click through, i.e. clicking on an element behind another element.
- **ignore_tab_navigation** - Makes the element ignore tab navigation.

The list above copies the text box attributes, and the vanilla edit boxes do not use most of them. All 85 vanilla `editBoxType` blocks write `size` (always `{ x = .. y = .. }`), `name`, `position` and `font`, and the page does not list `size`. They also use `text` (69), `bordersize` (52), `orientation` (45), `textureFile` (27), `ignore_enter` (6), `cursor` (5), `only_numbers` (3, `yes`), `is_multiline` (2), `pdx_tooltip` (1) and `tooltip` (1). None writes `maxWidth`, `maxHeight`, `format`, `fixedsize` or `alwaystransparent`, and no `.gui` file writes `ignore_tab_navigation`, although the string exists once in `hoi4.exe`. The executable string says nothing about whether the key works. (unverified) `hoi4.exe`

## OverlappingElementsBoxType

The *OverlappingElementsBoxType* element is used to define a special kind of listbox that dynamically overlaps sub-elements within itself.

The following attributes are used:

- **name** - The listbox name.
- **position** - The screen position of the listbox.
- **orientation** - Sets the orientation origin for the *position* attribute.
- **size** - The bounding box for the listbox.
- **spacing** - The spacing to use between listbox entries.
- **horizontal** - Whether the listbox is horizontal (1) or vertical (0).
- **bordersize** - The bounding box for the border for the listbox.
- **alwaystransparent** - Forces the listbox to allow click through, i.e. clicking on an element behind another element.

The following attributes are rarely or never used:

- **textureFile** - Never used for anything.

Valid *format* values:

- left
- center
- right

The 46 vanilla `OverlappingElementsBoxType` blocks write `name`, `position` and `size` (all 46), `spacing` (45), `format` (42: `left` 22, `right` 11, `center` 9), `orientation` (13) and `first_on_top` (10, `yes` in 9). `format` and `first_on_top` are missing from the page's list, which also names `horizontal`, `bordersize` and `alwaystransparent`, written by none of them. The "Valid format values" list at the end of this section is right for `format` here.

## Position and orientation

The `orientation` attribute sets the anchor point of an element. As example, `orientation = UPPER_LEFT` sets `position = { x = 0 y = 0 }` to be in the top left corner of the screen or container, and `orientation = LOWER_RIGHT` sets it to be the bottom right instead.

The `position` attribute sets the position of an element relatively to its orientation. For example, `position = { x = 120 y = 100 }` with `orientation = UPPER_LEFT` will result in the element being 120 pixels to the right and 100 pixels to the bottom relatively to the upper left corner of its container, while `orientation = LOWER_RIGHT` will result in it being 120 pixels to the left and 100 pixels to the top from the lower right corner.

Valid `orientation` values (case-insensitive):

- `CENTER`
- `CENTER_UP` (possibly interchangeable with `CENTER_UPPER`)
- `CENTER_DOWN` (possibly interchangeable with `CENTER_LOWER`)
- `CENTER_LEFT`
- `CENTER_RIGHT`
- `UPPER_LEFT`
- `LOWER_LEFT`
- `UPPER_RIGHT`
- `LOWER_RIGHT`

Orientation and position as vanilla writes them.

- The values in use are `upper_left`, `upper_right`, `lower_left`, `lower_right`, `center`, `center_up`, `center_down`, `center_left`, `center_right` and `center_lower` (7 uses). `center_upper` is never written. `center_up` has 75 uses and `center_down` 37. That `center_lower` is an alias for `center_down` is a guess. (unverified)
- Values are written quoted (`orientation = "upper_left"`) or bare (`orientation = upper_left`), in any case, and vanilla also writes `orientation = left` in eight blocks (two edit boxes, two buttons, a checkbox, an overlapping box and two text boxes), a value the page does not list.
- `position` is always `{ x = .. y = .. }` and the values can be negative (`position = { x=0 y=-22 }` in `interface/AST_cabinet_trust_scripted_gui.gui`). 547 of the 2,024 containers write an `orientation`.

## Fonts

*See also: [Font modding](font_modding.md)*

The following fonts are usable in Hearts of Iron IV (note that some do not support every language the game includes translations for):

- Arial12
- Arial12_bold
- cg_16b
- cg_18b
- garamond_12
- garamond_14
- garamond_14_bold
- garamond_16
- garamond_16_bold
- garamond_24
- hoi_16mbs
- hoi_16tooltip3
- hoi_18
- hoi_18b
- hoi_18mbs
- hoi_20b
- hoi_20bs
- hoi_22tech
- hoi_24header
- hoi_26mbs
- hoi_30header
- hoi_33
- hoi_36header
- hoi4_typewriter16
- hoi4_typewriter22
- hoi_mapfont4
- hoi_arrow_font
- newsfeed_body
- newsfeed_title
- standard
- standard_18
- standard_22
- tahoma_20_bold
- vic_18
- vic_18_grey
- vic_18s
- vic_22
- vic_22_bl
- vic_22s
- vic_36
- vic_36s

Fonts are registered with `bitmapfont = { name = ".." ... }` blocks in `interface/*.gfx`, mostly `interface/core.gfx`, with 44 names across `interface/*.gfx` in 1.19.4.1, `interface/core.gfx` among them. In 1.19.4.1 every `font` and `buttonFont` value in `interface/*.gui` is written in the same case as its registration (for example `Main_14_black`), so vanilla shows no case mismatch. Whether the game matches font names without regard to case is not shown and is untested. (unverified) See [Font modding](font_modding.md).

- 15 of the 33 names in the list above have no `bitmapfont` entry in any `interface/*.gfx` file: `Arial12_bold`, `cg_18b`, `garamond_14_bold`, `garamond_16`, `garamond_16_bold`, `garamond_24`, `hoi_16tooltip3`, `hoi_26mbs`, `hoi_mapfont4`, `newsfeed_body`, `newsfeed_title`, `standard`, `standard_18`, `standard_22` and `tahoma_20_bold`. Some have font files in `gfx/fonts/`, but whether a font can be used by name without a registration is not shown. Whether a font works without a registration is untested. (unverified)
- Registered fonts that the list omits include `Main_14`, `Main_14_black`, `Main_14_bold`, `Main_14_eu`, `Main_14_grey`, `Main_16`, `ToolTip_Font`, `hoi_22chat`, `hoi_30`, `vic_22`, `vic_36`, `standard_font`, `chat_input_font`, `hoi4_typewriter16_inverted` and `hoi4_typewriter22_inverted`.
- The workhorses of the vanilla windows, counting `font` and `buttonFont` uses in `.gui` files: `hoi_18mbs` (1,470), `hoi_16mbs` (1,072), `vic_18` (231), `hoi_36header` (190), `hoi_24header` (160), `hoi_20b` (152), `hoi_20bs` (93), `hoi4_typewriter16` (92), `hoi_18b` (77).

## Element types the page does not describe

Types that appear in vanilla `.gui` files but have no section above. Counts are blocks in the 132 files and attributes are the keys they write. The meanings are read from names and usage and are untested. (unverified)

| Type | Blocks | Attributes and notes |
| --- | --- | --- |
| `gridBoxType` | 596 | `name`, `slotsize` (571, `{ width = .. height = .. }`), `position` (556), `size` (546), `format` (528, values such as `"UPPER_LEFT"`, `"LEFT"`, `"UP"`, `"UPPER_RIGHT"`), `max_slots_horizontal` (398), `max_slots_vertical` (111), `orientation` (34), `max_slots` (27), `add_horizontal` (26), `background` (6), `padding` (5). This is the element a scripted GUI dynamic list fills. |
| `dropDownBoxType` | 38 | `name`, `position`, an `expandedWindow` child (38, 37 of them with `show_animation_type = decelerated` and `hide_animation_type = accelerated`), `expandButton` (35), `size` (27), `clipping` (9), `switch_frame_on_expand` (3), `expandedOnTop` (2) |
| `positionType` | 160 | only `name` and `position`; a named position |
| `windowType` | 83 | older dialog type: `name`, `position`, `size` (80), `moveable` (77, 0 or 1), `background` (72), `fullScreen` (67), `horizontalBorder` and `verticalBorder` (56), `dontRender` (53), `orientation` (52), with `guiButtonType` and `textBoxType` children |
| `textBoxType` | 23 | `name`, `position`, `textureFile`, `bordersize`, `font`, `maxWidth`, `maxHeight` (all 23), `text` (21); the older form of `instantTextBoxType` |
| `browserType` | 1 | `name`, `spriteType`, `position`, `size`; the name suggests an embedded web view |
| `extendedScrollbarType` | 22 | the container scrollbar, see the notes under "scrollbarType" |

Scripted GUIs fill a `gridBoxType` from an array through `dynamic_lists`, which is why the page [Scripted GUI modding](scripted_gui_modding.md) pairs them.
