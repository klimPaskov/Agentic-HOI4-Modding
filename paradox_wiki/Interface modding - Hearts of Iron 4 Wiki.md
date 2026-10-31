# Interface modding

*Offline snapshot of the Hearts of Iron IV Wiki page "Interface modding", revision 100547, captured 2026-10-31. Wiki text by the wiki's contributors under CC BY-SA 3.0 (see LICENSE.txt); kit blocks are local additions under the same license.*

<!-- kit:begin id="review" at="top" build="1.19.3.0" checked="2026-10-31" revision="100547" sources="interface/ gfx/fonts/ common/scripted_guis/_documentation.md hoi4.exe" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Checked against a census of the 130 vanilla `interface/*.gui` files (element types, attributes, value forms, size forms), the `bitmapfont` registrations in `interface/*.gfx`, `gfx/fonts/`, and the scrollbar and container usage in the vanilla windows. Focus inlay windows are covered by [National focus modding](<National focus modding - Hearts of Iron 4 Wiki.md>); scripted GUI attachment by [Scripted GUI modding](<Scripted GUI modding - Hearts of Iron 4 Wiki.md>).
- Kit blocks added: an element census, the container attributes with vanilla counts, per-element attribute checks (icon, text, button, checkbox, edit box, list boxes, overlapping box, scrollbars), the `size` forms, orientation values, the fonts that are registered, and the element types the page does not describe (`gridBoxType`, `dropDownBoxType`, `positionType`, `windowType`, `browserType`).
- Errors found in the wiki text: `tooltip` on buttons is not "never used" (29 uses); `background` on `listboxType` is not "never used" (21 of 30); text alignment also accepts `centre` (250 uses); the `editBoxType` list copies text box attributes that no vanilla edit box writes and omits `size`, which all 84 write; `shieldtype` and `eu3dialogtype` have no use in vanilla `.gui` files; 15 of the 33 listed fonts have no `bitmapfont` entry in `interface/*.gfx`.
- Gaps left: no documentation file exists for `.gui` files, so the meaning of attributes the wiki does not describe (for example `rotation`, `scale`, `click_to_front`) is read from usage only. Nothing was run in the game.
<!-- kit:end id="review" -->

## Table of contents

- [Overview](#Overview)
- [Constants](#Constants)
- [Containers](#Containers)
  - [Arguments](#Arguments)
  - [Scrolling](#Scrolling)
- [scrollbarType](#scrollbarType)
- [Elements](#Elements)
- [iconType](#iconType)
- [instantTextBoxType](#instantTextBoxType)
- [buttonType](#buttonType)
- [smoothListboxType](#smoothListboxType)
- [listboxType](#listboxType)
- [checkboxType](#checkboxType)
- [editBoxType](#editBoxType)
- [OverlappingElementsBoxType](#OverlappingElementsBoxType)
- [Position and orientation](#Position_and_orientation)
- [Fonts](#Fonts)
- [Kit: Element types the page does not describe](#kit-interface-other-types)

---

The graphical user interface elements are defined within `/Hearts of Iron IV/interface/*.gui` files, as typical code formatting. The files only decide on the positions of how elements are arranged, [scripted GUI](<Scripted GUI modding - Hearts of Iron 4 Wiki.md>) is used to assign effects to newly-created interface elements.

## Overview <a id="Overview"></a>

The interface consists of [container windows (or containers)](#Containers) and elements within them. Each element, other than containers, must reside in a container. Containers can be nested in other elements to organise their positions. Gridboxes are used to clone the same container several times, with different details specified for each one. Newly-added elements can have their effects defined in [scripted GUI](<Scripted GUI modding - Hearts of Iron 4 Wiki.md>), while the effects of base game's GUI are hard-coded, that is, it's impossible to modify what it does directly.

The elements are shown in the order that they are defined in the file: what's placed later will be shown on top of what's placed earlier. The files are contained within a `guiTypes = { ... }` block overarching the entire file.

<!-- kit:begin id="if-census" at="section:Overview" -->
**Kit note** What vanilla `interface/*.gui` contains in 1.19.3, as a base for the checks below. All numbers: [vanilla-confirmed 1.19.3] a count over the 130 `.gui` files in `interface/`.

- Every file is wrapped in one `guiTypes = { ... }` block (130 of 130). Element type names and attribute names are case-insensitive: vanilla writes both `instantTextboxType` (1,722) and `instantTextBoxType` (1,042), `gridBoxType` and `gridboxtype`, `buttonType` and `ButtonType`, `orientation` and `Orientation`.
- Block counts: `iconType` 3,023; `instantTextBoxType` 2,764; `buttonType` 2,024; `containerWindowType` 1,998; `gridBoxType` 591; `guiButtonType` 340; `positionType` 160; `checkboxType` 155; `editBoxType` 84; `windowType` 83; `OverlappingElementsBoxType` 46; `dropDownBoxType` 37 (each with an `expandedWindow`); `scrollbarType` 31; `listboxType` 30; `textBoxType` 23; `extendedScrollbarType` 21; `smoothListboxType` 14; `browserType` 1.
- Sprites for the elements are defined in `.gfx` files next to the `.gui` files; see [Graphical asset modding](<Graphical asset modding - Hearts of Iron 4 Wiki.md>).
- Percent sizes are written both as `100%%` (705 uses) and as `100%` (351 uses). Both occur in vanilla, so the page's two spellings are both fine.

**Size forms.** The same `size` key takes two shapes depending on the element:

| Element | Blocks that set `size` | Form |
| --- | --- | --- |
| `containerWindowType` | 1,789 of 1,998 | `{ width = .. height = .. }`; 12 add `min = { width = .. height = .. }` (the tech tree) |
| `gridBoxType` | 541 of 591 | `{ width = .. height = .. }` |
| `extendedScrollbarType`, `dropDownBoxType`, `expandedWindow` | 21, 26, 37 | `{ width = .. height = .. }` |
| `buttonType` | 77 of 2,024 | `{ x = .. y = .. }` in all 77 |
| `guiButtonType`, `editBoxType`, `windowType`, `scrollbarType`, `listboxType`, `smoothListboxType`, `OverlappingElementsBoxType`, `browserType` | 7, 84, 80, 31, 30, 14, 46, 1 | `{ x = .. y = .. }` |
| `iconType`, `instantTextBoxType`, `checkboxType` | 0 | none; icons and checkboxes take their size from the sprite and text boxes use `maxWidth` and `maxHeight` |

All rows: [vanilla-confirmed 1.19.3] `interface/*.gui`. A `buttonType` that sets a size, from `interface/airselectionview.gui`: `size = {x = 220 y = @equipment_entry_heigth}`.
<!-- kit:end id="if-census" -->

## Constants <a id="Constants"></a>

*This section is transcluded from [Data structures § Constants](<Data structures - Hearts of Iron 4 Wiki.md#Constants>)*

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

<!-- kit:begin id="if-constants-note" at="section:Constants" -->
**Kit note** Vanilla `.gui` files define their own constants: 238 `@name = value` definitions in 31 of the 130 files, used for positions and sizes, for example `size = {width = 220 height = @equipment_entry_heigth}` in `interface/airselectionview.gui`. [vanilla-confirmed 1.19.3] `interface/*.gui`.
<!-- kit:end id="if-constants-note" -->

## Containers <a id="Containers"></a>

Containers are used to group together elements and associate them with an internal function, written as a `containerWindowType = { ... }` block.

New containers that are independent (not inside of any other container) will not show up in-game by default. For one to show up, it is required for it to be tied to a function, such as [scripted GUI](<Scripted GUI modding - Hearts of Iron 4 Wiki.md>), which decides where it should show and when. In some cases, new containers can be created for the internally-defined functions, such as [new technology folders](<Technology modding - Hearts of Iron 4 Wiki.md#Graphical_user_interface>) or [getting a music station to show up](<Music modding - Hearts of Iron 4 Wiki.md#Radio_stations>). In most cases, however, a scripted GUI would be required to make a new container show up.

If a container is defined within another container, it will appear at the same time as the window containing it unless more information is defined within the function. A scripted GUI cannot be assigned to such a container, however. In some cases, it's not necessary for a container to be visible to be useful, for example, an empty container can be used as an anchor, that is, used as the [parent window name](<Scripted GUI modding - Hearts of Iron 4 Wiki.md>) for Scripted GUI to place another container on the same place as the anchor is defined. This can allow placing containers with higher precision than normally possible with `parent_window_name`, allowing the parent window to have elements drawn on top of the scripted GUI.

### Arguments <a id="Arguments"></a>

The following attributes are commonly used:

- `name = "my_container"` – The name of the container, used to tie a function to the container. Independent containers must have unique names. While nested containers may have name overlap when defined in different independent containers, it's still preferable to avoid overlap, such as to ensure unambiguity when using `parent_window_name` in scripted GUI.
- `size = { height = 300 width = 100%% }` – The bounding box for the container. If this container is placed inside of another one, either directly or through a gridbox, then only this size is used to create the scrollbar, without taking into account elements inside. This boundary also sets the size that the scrollbar must use. Either in pixels or in percentages relative to the size of the parent container (the entire screen if independent).
- `background = { ... }` – The background of the container. This is required for a scrollbar to work, as otherwise the boundaries will get ignored. There are the following arguments inside:
  - `name = "Background"` – The name for handling the background in other functions. Commonly just set to "Background".
  - `spriteType = "GFX_tiled_window"` or `quadTextureSprite = "GFX_tiled_window_transparent"` – Refers to a [corneredTileSpriteType](<Graphical asset modding - Hearts of Iron 4 Wiki.md#corneredTileSpriteType>) definition that would automatically get resized to fit the container's set size.
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
- `show_sound = menu_open_window` – The [sound](<Sound modding - Hearts of Iron 4 Wiki.md>) to play during the 'show' animation.
- `hide_sound = menu_close_window` – The [sound](<Sound modding - Hearts of Iron 4 Wiki.md>) to play during the 'hide' animation.
- `fade_time = 300` – The time it takes for the container to fade in, in milliseconds.
- `fade_type = linear` – The type of fade in: either `accelerated` or `linear`.

<!-- kit:begin id="if-container-attrs" at="section:Arguments" -->
**Kit note** The container attributes of this page against the 1,998 vanilla `containerWindowType` blocks. All rows: [vanilla-confirmed 1.19.3] `interface/*.gui`.

| Attribute | Vanilla use |
| --- | --- |
| `size` | 1,789 blocks; `min = { width = .. height = .. }` is accepted inside it (12 blocks, all in `countrytechtreeview.gui`) |
| `background` | 1,028 blocks |
| `clipping` | 697 blocks: `no` 633, `yes` 64. Writing `no` is the common case, so the default really is on, as the page says |
| `position`, `orientation` | 1,793 and 540. Orientation values seen: `upper_left` 262, `center` 127, `center_right` 42, `lower_left` 31, `center_up` 30, `upper_right` 25, `lower_right` 12, `center_down` 8, `center_left` 3 |
| `origo` | 65: `center` 44, `center_up` 9, `upper_right` 3, `lower_left` 3, `lower_right` 3, `center_down` 2, `upper_left` 1 |
| `moveable` | 195: `yes` 172, `no` 23 |
| `fullScreen` | 0 on `containerWindowType`; it appears in 67 `windowType` blocks (`no` 62, `yes` 5) |
| `show_position`, `hide_position` | 87 and 5 |
| `show_animation_type`, `hide_animation_type`, `animation_type` | 63, 63 and 9. Values: `decelerated` for show (63) and for `animation_type` (9); `accelerated` for hide (61), plus one `linear` and one `decelerated` |
| `animation_time`, `fade_time`, `fade_type` | 72, 109 and 108; `fade_type` is always `linear` |
| `show_sound`, `hide_sound` | 65 and 26; common values `menu_open_window`, `pop_up`, `diplomatic_notification` for show and `menu_close_window` for hide |
| `verticalScrollbar`, `horizontalScrollbar` | 252 and 24. All 310 references resolve to an `extendedScrollbarType` definition |
| `drag_scroll` | 23, always `{ left middle }` |
| `margin` | 167, written as `{ top = .. bottom = .. left = .. right = .. }` with any subset of the four |
| `scroll_wheel_factor`, `smooth_scrolling` | 136 and 126; `smooth_scrolling = yes` in all 126 and a factor of 40 in 73 of the 136 |
| `autohide_scrollbars` | 1 (`no`) |

Attributes that vanilla containers use and the page does not mention: `click_to_front = yes` (113), `vertical_scroll_step` (13), `background_margin` (11, for example `{ bottom = 15 }`), `scale` (8) and, once each in a sliding window, `closed_position`, `open_position`, `peek_position`, `peek_check_top_left` and `peek_check_size`. [vanilla-confirmed 1.19.3] `interface/*.gui`. Their effects are read from the names only. [unverified]
<!-- kit:end id="if-container-attrs" -->

### Scrolling <a id="Scrolling"></a>

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

## scrollbarType <a id="scrollbarType"></a>

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

<!-- kit:begin id="if-scrollbar-notes" at="section:scrollbarType" -->
**Kit note** All 14 attributes in the list above (`name`, `slider`, `track`, `leftbutton`, `rightbutton`, `position`, `size`, `priority`, `borderSize`, `maxValue`, `minValue`, `stepSize`, `startValue`, `horizontal`) appear in every one of the 31 vanilla `scrollbarType` blocks, plus one `scroll_speed`. `horizontal` is the number 1 in 28 blocks and 0 in 3. [vanilla-confirmed 1.19.3] `interface/*.gui`. `scrollbarType` is what list boxes and text boxes name in their `scrollbarType = ...` attribute: `standardlistbox_slider` (43 uses) and `standardtext_slider` (26). [vanilla-confirmed 1.19.3] `interface/*.gui`.

The scrollbar of a container is a different element, `extendedScrollbarType`, which the "Scrolling" section mentions without listing its attributes. The 21 vanilla blocks use `name`, `position`, `size` (`{ width = .. height = .. }`), `startValue` (21), `slider` (21), `track` (20), `decreaseButton` and `increaseButton` (18 each), `background` (14), `tileSize`, `maxValue`, `minValue`, `stepSize`, `horizontal` (9 each, written `yes`), `orientation` and `origo` (8 each), `clickOnly` (6), `smooth_scrolling` (4, with values such as 0.25 and 1.25) and `setTrackFrameOnChange` (2). All 310 `verticalScrollbar` and `horizontalScrollbar` references in vanilla point at an `extendedScrollbarType`. [vanilla-confirmed 1.19.3] `interface/*.gui`.
<!-- kit:end id="if-scrollbar-notes" -->

## Elements <a id="Elements"></a>

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

<!-- kit:begin id="if-element-types" at="section:Elements" -->
**Kit note** Checks of the lists above.

- `shieldtype` and `eu3dialogtype` are not used by any of the 130 vanilla `.gui` files. Country flags in vanilla come from `maskedShieldType` sprites in `.gfx` files (`interface/core.gfx`, `interface/general_stuff.gfx`, `interface/countryconstructionsview.gfx`), not from a `.gui` element. [vanilla-confirmed 1.19.3] `interface/*.gui`, `interface/*.gfx`.
- The "legacy" types are still used widely: `guiButtonType` 340 blocks, `windowType` 83 and `textBoxType` 23. `guiButtonType` has the attributes of `buttonType` plus `parent` (28 blocks); `windowType` groups children and writes `moveable` as 0 or 1, `fullScreen`, `horizontalBorder` and `verticalBorder`, `dontRender` and `background`. [vanilla-confirmed 1.19.3] `interface/*.gui`. For new windows prefer `containerWindowType` and `buttonType`, the types the page names as current. [unverified]
- Element types in vanilla that the page does not describe are covered in the section "Kit: Element types the page does not describe" at the bottom of the page.
<!-- kit:end id="if-element-types" -->

## iconType <a id="iconType"></a>

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

<!-- kit:begin id="if-icon-notes" at="section:iconType" -->
**Kit note** The attribute list against the 3,023 vanilla `iconType` blocks. All numbers: [vanilla-confirmed 1.19.3] `interface/*.gui`.

- Used: `name` (3,023), `position` (2,958), `spriteType` (2,501), `alwaystransparent` (1,158), `orientation` (540), `quadTextureSprite` (491), `frame` (383), `centerposition` (316, always `yes`), `pdx_tooltip` (109), `pdx_tooltip_delayed` (2), `hint_tag` (1).
- Used but missing from the page: `scale` (382, values such as 0.6, 0.7, 0.8, 0.9), `hide` (57, `hide = yes`), `rotation` (50, mostly 1.5708, which looks like a quarter turn in radians), `context_aware_tooltip` (40, a scripted localisation call such as `[GetNavalFactionDesc]`), `tooltip` (10, a localisation key) and `buttonMesh` (1). The meanings of `scale`, `rotation` and `hide` are inferred from the values. [unverified]
- No `iconType` writes `size`. The icon is drawn at the size of its sprite, scaled by `scale`. [vanilla-confirmed 1.19.3] 0 of 3,023. [unverified]
- `spriteType` is the common choice (2,501) over `quadTextureSprite` (491).
<!-- kit:end id="if-icon-notes" -->

## instantTextBoxType <a id="instantTextBoxType"></a>

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

<!-- kit:begin id="if-text-notes" at="section:instantTextBoxType" -->
**Kit note** The attribute list against the 2,764 vanilla `instantTextBoxType` blocks. All numbers: [vanilla-confirmed 1.19.3] `interface/*.gui`.

- Used as the page says: `name`, `position` (2,761), `font` (2,738), `maxWidth` (2,729), `maxHeight` (2,513), `format` (2,429), `text` (2,232), `borderSize` (872, written `{ x = .. y = .. }`), `fixedsize` (849), `alwaystransparent` (576), `orientation` (487), `pdx_tooltip` (146), `scrollbarType` (28, always a scrollbar such as `standardtext_slider`).
- `format` takes `left` (1,022), `center` (976), `centre` (250) and `right` (181). The page lists three values; `centre` is a fourth spelling in common use.
- `pdx_tooltip_delayed` is listed on the page but no `instantTextBoxType` writes it.
- `textureFile` is written in 604 blocks, almost always as an empty string (`textureFile = ""` in 627 of 658 uses across all types), which fits "never used for anything".
- Used but missing from the page: `vertical_alignment` (112: `center` for nearly all, `top` for 4), `multiline` (72), `context_aware_text` (39, a localisation key or a scripted localisation call), `truncate` (33, `yes`), `text_color_code` (29, a one-letter colour code such as `b`, `g` or `L`), `tooltip` (14) and `hide` (4). Their meanings are read from the names. [unverified]
<!-- kit:end id="if-text-notes" -->

## buttonType <a id="buttonType"></a>

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

<!-- kit:begin id="if-button-notes" at="section:buttonType" -->
**Kit note** The attribute list against the 2,024 vanilla `buttonType` blocks. All numbers: [vanilla-confirmed 1.19.3] `interface/*.gui`.

- Used as the page says: `name`, `position` (1,978), `quadTextureSprite` (1,432), `clicksound` (1,391), `spriteType` (593), `buttonFont` (573), `orientation` (540), `pdx_tooltip` (426), `buttonText` (405), `shortcut` (366), `oversound` (294), `frame` (270), `scale` (134), `web_link` (76), `alwaystransparent` (42), `pdx_tooltip_delayed` (35). `quadTextureSprite` is the common sprite key for buttons, more than twice as common as `spriteType`.
- `tooltip` is **not** "never used": 29 buttons write it, with a localisation key (`tooltip = "LEDGER_CIV_GRAPH_SHOW_INDUSTRY"`). `tooltipText` and `delayedTooltipText` have no use. `hint_tag` is listed on the page but no `buttonType` writes it.
- Used but missing from the page: `size` (77, always `{ x = .. y = .. }`), `font` (312) and `text` (180) next to `buttonFont` and `buttonText`, `pdx_tooltip_anchor` (55), `centerposition` (52), `no_clicksound` (21, always `yes`), `format` (17), `enabled` (8, always `no`), `borderSize` (6), `multiline` (3), `pdx_disabled_tooltip` and `pdx_disabled_tooltip_delayed` (1 each) and `rotation` (1).
- The vanilla files contain two typos you should not copy: `format = left;` with a semicolon, in two buttons.
- The heading of this section describes `guiButtonType`, a typo in the wiki text. `buttonType` is the current spelling; `guiButtonType` (340 blocks) also still works. [vanilla-confirmed 1.19.3] `interface/*.gui`.
<!-- kit:end id="if-button-notes" -->

## smoothListboxType <a id="smoothListboxType"></a>

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

<!-- kit:begin id="if-smoothlist-notes" at="section:smoothListboxType" -->
**Kit note** Of the 14 vanilla `smoothListboxType` blocks, all write `name`, `position` and `size`; 13 write `scrollbarType`, and the rest of the page's list is rarely used (`orientation` 6, `bordersize` 6, `spacing` 3). `horizontal` and `alwaystransparent` appear in none, while `priority` (3) and `clipping` (2) do. `background` has no use, as the page says. [vanilla-confirmed 1.19.3] `interface/*.gui`.
<!-- kit:end id="if-smoothlist-notes" -->

## listboxType <a id="listboxType"></a>

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

<!-- kit:begin id="if-list-notes" at="section:listboxType" -->
**Kit correction** `background` is not "never used" on `listboxType`: 21 of the 30 vanilla `listboxType` blocks write it. The other attributes: `name`, `position`, `size` (all 30, `{ x = .. y = .. }`), `scrollbarType` (28), `orientation` (25), `spacing` (24), `bordersize` (19), `horizontal` (9, always 0), `alwaystransparent` (3), `priority` (2) and `offset` (2). [vanilla-confirmed 1.19.3] `interface/*.gui`.
<!-- kit:end id="if-list-notes" -->

## checkboxType <a id="checkboxType"></a>

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

<!-- kit:begin id="if-checkbox-notes" at="section:checkboxType" -->
**Kit note** All 155 vanilla `checkboxType` blocks use `quadTextureSprite` and none uses `spriteType`. Attributes in use: `name`, `position`, `quadTextureSprite` (155 each), `clicksound` (95), `orientation` (53), `buttonFont` (51), `buttonText` (44), `pdx_tooltip` (7), `frame` (5) and `pdx_tooltip_delayed` (1). `shortcut`, `scale`, `hint_tag` and `alwaystransparent` are listed on the page and written by no vanilla checkbox. `tooltip`, `tooltipText` and `delayedTooltipText` are unused, as the page says. [vanilla-confirmed 1.19.3] `interface/*.gui`.
<!-- kit:end id="if-checkbox-notes" -->

## editBoxType <a id="editBoxType"></a>

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

<!-- kit:begin id="if-editbox-notes" at="section:editBoxType" -->
**Kit correction** The list above copies the text box attributes, and the vanilla edit boxes do not use most of them. All 84 vanilla `editBoxType` blocks write `size` (always `{ x = .. y = .. }`), `name`, `position` and `font`, and the page does not list `size`. They also use `text` (69), `bordersize` (52), `orientation` (45), `textureFile` (27), `ignore_enter` (6), `cursor` (5), `only_numbers` (3, `yes`) and `is_multiline` (2). None writes `maxWidth`, `maxHeight`, `format`, `fixedsize` or `alwaystransparent`, and no `.gui` file writes `ignore_tab_navigation`, although the string exists once in `hoi4.exe`. [vanilla-confirmed 1.19.3] `interface/*.gui`. [unverified]
<!-- kit:end id="if-editbox-notes" -->

## OverlappingElementsBoxType <a id="OverlappingElementsBoxType"></a>

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

<!-- kit:begin id="if-overlap-notes" at="section:OverlappingElementsBoxType" -->
**Kit note** The 46 vanilla `OverlappingElementsBoxType` blocks write `name`, `position` and `size` (all 46), `spacing` (45), `format` (42: `left` 22, `right` 11, `center` 9), `orientation` (13) and `first_on_top` (10, `yes` in 9). `format` and `first_on_top` are missing from the page's list, which also names `horizontal`, `bordersize` and `alwaystransparent`, written by none of them. The "Valid format values" list at the end of this section is right for `format` here. [vanilla-confirmed 1.19.3] `interface/*.gui`.
<!-- kit:end id="if-overlap-notes" -->

## Position and orientation <a id="Position_and_orientation"></a>

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

<!-- kit:begin id="if-orientation-notes" at="section:Position_and_orientation" -->
**Kit note** Orientation and position as vanilla writes them. All bullets: [vanilla-confirmed 1.19.3] `interface/*.gui`.

- The values in use are `upper_left`, `upper_right`, `lower_left`, `lower_right`, `center`, `center_up`, `center_down`, `center_left`, `center_right` and `center_lower` (7 uses). `center_upper` is never written. `center_up` has 78 uses and `center_down` 37, so the alias `center_lower` for `center_down` is plausible and rare. [unverified]
- Values are written quoted (`orientation = "upper_left"`) or bare (`orientation = upper_left`), in any case, and vanilla also writes `orientation = left` in four blocks (two edit boxes, a checkbox, an overlapping box), a value the page does not list. [unverified]
- `position` is always `{ x = .. y = .. }` and the values can be negative (`position = { x=0 y=-22 }` in `interface/AST_cabinet_trust_scripted_gui.gui`). 540 of the 1,998 containers write an `orientation`.
<!-- kit:end id="if-orientation-notes" -->

## Fonts <a id="Fonts"></a>

*See also: [Font modding](<Font modding - Hearts of Iron 4 Wiki.md>)*

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

<!-- kit:begin id="if-fonts-notes" at="section:Fonts" -->
**Kit note** Fonts are registered with `bitmapfont = { name = ".." ... }` blocks in `interface/*.gfx`, mostly `interface/core.gfx`, with 44 names across `interface/*.gfx` in 1.19.3, `interface/core.gfx` among them. Font names are matched without regard to case: `.gui` files write `"main_14_black"` for the font registered as `Main_14_black`. [vanilla-confirmed 1.19.3] `interface/core.gfx`, `interface/*.gui`. See [Font modding](<Font modding - Hearts of Iron 4 Wiki.md>).

- 15 of the 33 names in the list above have no `bitmapfont` entry in any `interface/*.gfx` file: `Arial12_bold`, `cg_18b`, `garamond_14_bold`, `garamond_16`, `garamond_16_bold`, `garamond_24`, `hoi_16tooltip3`, `hoi_26mbs`, `hoi_mapfont4`, `newsfeed_body`, `newsfeed_title`, `standard`, `standard_18`, `standard_22` and `tahoma_20_bold`. Some have font files in `gfx/fonts/`, but whether a font can be used by name without a registration is not shown. [vanilla-confirmed 1.19.3] `interface/*.gfx`, `gfx/fonts/`. [unverified]
- Registered fonts that the list omits include `Main_14`, `Main_14_black`, `Main_14_bold`, `Main_14_eu`, `Main_14_grey`, `Main_16`, `ToolTip_Font`, `hoi_22chat`, `hoi_30`, `vic_22`, `vic_36`, `standard_font`, `chat_input_font`, `hoi4_typewriter16_inverted` and `hoi4_typewriter22_inverted`. [vanilla-confirmed 1.19.3] `interface/core.gfx` and related `.gfx` files.
- The workhorses of the vanilla windows, counting `font` and `buttonFont` uses in `.gui` files: `hoi_18mbs` (1,471), `hoi_16mbs` (1,051), `vic_18` (235), `hoi_36header` (207), `hoi_24header` (159), `hoi_20b` (152), `hoi_20bs` (95), `hoi4_typewriter16` (93), `hoi_18b` (77). [vanilla-confirmed 1.19.3] `interface/*.gui`.
<!-- kit:end id="if-fonts-notes" -->

<!-- kit:begin id="if-other-types" at="bottom" -->
## Kit: Element types the page does not describe <a id="kit-interface-other-types"></a>

**Kit addition** Types that appear in vanilla `.gui` files but have no section above. Counts are blocks in the 130 files and attributes are the keys they write. All rows: [vanilla-confirmed 1.19.3] `interface/*.gui`. The meanings are read from names and usage. [unverified]

| Type | Blocks | Attributes and notes |
| --- | --- | --- |
| `gridBoxType` | 591 | `name`, `slotsize` (566, `{ width = .. height = .. }`), `position` (553), `size` (541), `format` (523, values such as `"UPPER_LEFT"`, `"LEFT"`, `"UP"`, `"UPPER_RIGHT"`), `max_slots_horizontal` (393), `max_slots_vertical` (111), `orientation` (34), `max_slots` (27), `add_horizontal` (24), `background` (6), `padding` (5). This is the element a scripted GUI dynamic list fills. |
| `dropDownBoxType` | 37 | `name`, `position`, an `expandedWindow` child (37) with `show_animation_type = decelerated` and `hide_animation_type = accelerated`, `expandButton` (34), `size` (26), `clipping` (9), `switch_frame_on_expand` (3), `expandedOnTop` (2) |
| `positionType` | 160 | only `name` and `position`; a named position |
| `windowType` | 83 | older dialog type: `name`, `position`, `size` (80), `moveable` (77, 0 or 1), `background` (72), `fullScreen` (67), `horizontalBorder` and `verticalBorder` (56), `dontRender` (53), `orientation` (52), with `guiButtonType` and `textBoxType` children |
| `textBoxType` | 23 | `name`, `position`, `textureFile`, `bordersize`, `font`, `maxWidth`, `maxHeight` (all 23), `text` (21); the older form of `instantTextBoxType` |
| `browserType` | 1 | `name`, `spriteType`, `position`, `size`; the name suggests an embedded web view |
| `extendedScrollbarType` | 21 | the container scrollbar, see the notes under "scrollbarType" |

Scripted GUIs fill a `gridBoxType` from an array through `dynamic_lists`, which is why the page [Scripted GUI modding](<Scripted GUI modding - Hearts of Iron 4 Wiki.md>) pairs them. [docs] `common/scripted_guis/_documentation.md`.
<!-- kit:end id="if-other-types" -->

---

## Navigation

**[Modding](<Modding - Hearts of Iron 4 Wiki.md>)**

- **Documentation**: [Effects](<Effects - Hearts of Iron 4 Wiki.md>) • [Triggers](<Triggers - Hearts of Iron 4 Wiki.md>) • [Defines](<Defines - Hearts of Iron 4 Wiki.md>) • [Modifiers](<Modifiers - Hearts of Iron 4 Wiki.md>) • [List of modifiers](<List of modifiers - Hearts of Iron 4 Wiki.md>) • [Scopes](<Scopes - Hearts of Iron 4 Wiki.md>) • [Localisation](<Localisation - Hearts of Iron 4 Wiki.md>) • [On actions](<On actions - Hearts of Iron 4 Wiki.md>) • [Data structures](<Data structures - Hearts of Iron 4 Wiki.md>) • [Flags](<Data structures - Hearts of Iron 4 Wiki.md#Flags>) • [Event targets](<Data structures - Hearts of Iron 4 Wiki.md#Event_targets>) • [Country tag aliases](<Data structures - Hearts of Iron 4 Wiki.md#Country_tag_aliases>) • [Variables](<Data structures - Hearts of Iron 4 Wiki.md#Variables>) • [Arrays](<Data structures - Hearts of Iron 4 Wiki.md#Arrays>)
- **Scripting**: [Achievements](<Achievement modding - Hearts of Iron 4 Wiki.md>) • [AI](<AI modding - Hearts of Iron 4 Wiki.md>) • [AI focuses](<AI focuses - Hearts of Iron 4 Wiki.md>) • [Autonomous states](<Autonomy state modding - Hearts of Iron 4 Wiki.md>) • [Balances of power](<Balance of power modding - Hearts of Iron 4 Wiki.md>) • [Bookmarks/Scenarios](<Bookmark modding - Hearts of Iron 4 Wiki.md>) • [Game rules](<Bookmark modding - Hearts of Iron 4 Wiki.md#Game_rules>) • [Buildings](<Building modding - Hearts of Iron 4 Wiki.md>) • [Characters and traits](<Character modding - Hearts of Iron 4 Wiki.md>) • [Cosmetic tags](<Cosmetic tag modding - Hearts of Iron 4 Wiki.md>) • [Countries](<Country creation - Hearts of Iron 4 Wiki.md>) • [Divisions](<Division modding - Hearts of Iron 4 Wiki.md>) • [Decisions](<Decision modding - Hearts of Iron 4 Wiki.md>) • [Doctrines](<Doctrine modding - Hearts of Iron 4 Wiki.md>) • [Equipment](<Equipment modding - Hearts of Iron 4 Wiki.md>) • [Events](<Event modding - Hearts of Iron 4 Wiki.md>) • [Factions](<Faction modding - Hearts of Iron 4 Wiki.md>) • [Ideas](<Idea modding - Hearts of Iron 4 Wiki.md>) • [Ideologies](<Ideology modding - Hearts of Iron 4 Wiki.md>) • [Military industrial organizations](<Military industrial organization modding - Hearts of Iron 4 Wiki.md>) • [National focuses](<National focus modding - Hearts of Iron 4 Wiki.md>) • [Resources](<Resources modding - Hearts of Iron 4 Wiki.md>) • [Scripted GUI](<Scripted GUI modding - Hearts of Iron 4 Wiki.md>) • [Technologies and doctrines](<Technology modding - Hearts of Iron 4 Wiki.md>) • [Units](<Unit modding - Hearts of Iron 4 Wiki.md>)
- **Map**: [Map](<Map modding - Hearts of Iron 4 Wiki.md>) • [States](<State modding - Hearts of Iron 4 Wiki.md>) • [Supply areas](<Supply areas modding - Hearts of Iron 4 Wiki.md>) • [Strategic regions](<Strategic region modding - Hearts of Iron 4 Wiki.md>)
- **Graphical**: [Graphical assets](<Graphical asset modding - Hearts of Iron 4 Wiki.md>) • [Entities](<Entity modding - Hearts of Iron 4 Wiki.md>) • [Posteffects](<Posteffect modding - Hearts of Iron 4 Wiki.md>) • [Particles](<Particle modding - Hearts of Iron 4 Wiki.md>) • [Fonts](<Font modding - Hearts of Iron 4 Wiki.md>)
- **Cosmetic**: [Portraits](<Portrait modding - Hearts of Iron 4 Wiki.md>) • [Namelists](<Namelist modding - Hearts of Iron 4 Wiki.md>) • [Music](<Music modding - Hearts of Iron 4 Wiki.md>) • [Sound](<Sound modding - Hearts of Iron 4 Wiki.md>)
- **Other**: [Console commands](<Console commands - Hearts of Iron 4 Wiki.md>) • [Troubleshooting](<Troubleshooting - Hearts of Iron 4 Wiki.md>) • [Mod structure](<Mod structure - Hearts of Iron 4 Wiki.md>) • [Mods](<Mods - Hearts of Iron 4 Wiki.md>) • [Nudger](<Nudger - Hearts of Iron 4 Wiki.md>)
- **Kit pages (not on the wiki)**: [Collection modding](<Collection modding - Hearts of Iron 4 Wiki.md>) • [Game rule modding](<Game rule modding - Hearts of Iron 4 Wiki.md>) • [Intelligence operation modding](<Intelligence operation modding - Hearts of Iron 4 Wiki.md>) • [Map mode modding](<Map mode modding - Hearts of Iron 4 Wiki.md>) • [Occupation and resistance modding](<Occupation and resistance modding - Hearts of Iron 4 Wiki.md>) • [Peace conference modding](<Peace conference modding - Hearts of Iron 4 Wiki.md>) • [Raid modding](<Raid modding - Hearts of Iron 4 Wiki.md>) • [Script constant modding](<Script constant modding - Hearts of Iron 4 Wiki.md>) • [Special project modding](<Special project modding - Hearts of Iron 4 Wiki.md>)
