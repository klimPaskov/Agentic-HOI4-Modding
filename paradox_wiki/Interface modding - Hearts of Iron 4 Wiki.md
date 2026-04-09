# Table of contents

- [Overview](#overview)
- [Constants](#constants)
- [Containers](#containers)
  - [Arguments](#arguments)
  - [Scrolling](#scrolling)
- [scrollbarType](#scrollbartype)
- [Elements](#elements)
- [iconType](#icontype)
- [instantTextBoxType](#instanttextboxtype)
- [buttonType](#buttontype)
- [smoothListboxType](#smoothlistboxtype)
- [listboxType](#listboxtype)
- [checkboxType](#checkboxtype)
- [editBoxType](#editboxtype)
- [OverlappingElementsBoxType](#overlappingelementsboxtype)
- [Position and orientation](#position-and-orientation)
- [Fonts](#fonts)


---

The graphical user interface elements are defined within /Hearts of Iron IV/interface/\*.gui files, as typical code formatting. The files only decide on the positions of how elements are arranged, [scripted GUI](<Scripted GUI modding - Hearts of Iron 4 Wiki.md>) is used to assign effects to newly-created interface elements.

## Overview

The interface consists of [container windows (or containers)](#containers) and elements within them. Each element, other than containers, must reside in a container. Containers can be nested in other elements to organise their positions. Gridboxes are used to clone the same container several times, with different details specified for each one. Newly-added elements can have their effects defined in [scripted GUI](<Scripted GUI modding - Hearts of Iron 4 Wiki.md>), while the effects of base game's GUI are hard-coded, that is, it's impossible to modify what it does directly.

The elements are shown in the order that they are defined in the file: what's placed later will be shown on top of what's placed earlier. The files are contained within a `guiTypes = { ... }` block overarching the entire file.

## Constants

*This section is transcluded from [Data structures § Constants](<Data structures - Hearts of Iron 4 Wiki.md#constants>)*

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

## Containers

Containers are used to group together elements and associate them with an internal function, written as a `containerWindowType = { ... }` block.

New containers that are independent (not inside of any other container) will not show up in-game by default. For one to show up, it is required for it to be tied to a function, such as [scripted GUI](<Scripted GUI modding - Hearts of Iron 4 Wiki.md>), which decides where it should show and when. In some cases, new containers can be created for the internally-defined functions, such as [new technology folders](<Technology modding - Hearts of Iron 4 Wiki.md#graphical-user-interface>) or [getting a music station to show up](<Music modding - Hearts of Iron 4 Wiki.md#radio-stations>). In most cases, however, a scripted GUI would be required to make a new container show up.

If a container is defined within another container, it will appear at the same time as the window containing it unless more information is defined within the function. A scripted GUI cannot be assigned to such a container, however. In some cases, it's not necessary for a container to be visible to be useful, for example, an empty container can be used as an anchor, that is, used as the [parent window name](<Scripted GUI modding - Hearts of Iron 4 Wiki.md#parent-window-token>) for Scripted GUI to place another container on the same place as the anchor is defined. This can allow placing containers with higher precision than normally possible with `parent_window_name`, allowing the parent window to have elements drawn on top of the scripted GUI.

### Arguments

The following attributes are commonly used:

- `name = "my_container"` – The name of the container, used to tie a function to the container. Independent containers must have unique names. While nested containers may have name overlap when defined in different independent containers, it's still preferable to avoid overlap, such as to ensure unambiguity when using `parent_window_name` in scripted GUI.
- `size = { height = 300 width = 100%% }` – The bounding box for the container. If this container is placed inside of another one, either directly or through a gridbox, then only this size is used to create the scrollbar, without taking into account elements inside. This boundary also sets the size that the scrollbar must use. Either in pixels or in percentages relative to the size of the parent container (the entire screen if independent).
- `background = { ... }` – The background of the container. This is required for a scrollbar to work, as otherwise the boundaries will get ignored. There are the following arguments inside:
  - `name = "Background"` – The name for handling the background in other functions. Commonly just set to "Background".
  - `spriteType = "GFX_tiled_window"` or `quadTextureSprite = "GFX_tiled_window_transparent"` – Refers to a [corneredTileSpriteType](<Graphical asset modding - Hearts of Iron 4 Wiki.md#corneredtilespritetype>) definition that would automatically get resized to fit the container's set size.
- `clipping = yes` – If true (and if a background exists), the elements inside of the container will not be able to go outside of the boundary box, and what doesn't fit will get cropped. Defaults to true. This being true is mandatory for a scrollbar to work.
- `position = { x = 100 y = 100 }` – The position of the container in pixels relative to the set orientation and set origo.
- `orientation = center` – Sets the origin that the position is measured relative to, such as `upper_left`, `center_down`, or `lower_right` for the screen.
- `origo = center` – Sets the origin that the position is measured relative to, such as `upper_left`, `center_down`, or `lower_right` for the element.
- `moveable = yes` – If set, the container can be moved by the player with their cursor.
- `fullScreen = yes` – If set, the container will be considered to cover the entire screen.

Animation can be assigned to containers with these attributes:

- `show_position = { x = 300 y = 100 }` – The screen position where the container will show up to the player after the 'show' animation finishes.
- `hide_position = { x = 100 y = 100 }` – The screen position the container aims for during the 'hide' animation.
- `show_animation_type = linear` – The animation type used to show the container (`decelerated` or `linear`).
- `hide_animation_type = accelerated` – The animation type used to hide the container (`accelerated` or `linear`).
- `animation_type = decelerated` – The animation if both show and hide animations are supposed to be the same (`accelerated`, `decelerated`, or `linear`).
- `animation_time = 1000` – The animation time in milliseconds.
- `show_sound = menu_open_window` – The [sound](<Sound modding - Hearts of Iron 4 Wiki.md>) to play during the 'show' animation.
- `hide_sound = menu_close_window` – The [sound](<Sound modding - Hearts of Iron 4 Wiki.md>) to play during the 'hide' animation.
- `fade_time = 300` – The time it takes for the container to fade in, in milliseconds.
- `fade_type = linear` – The type of fade in: either `accelerated` or `linear`.

### Scrolling

Scrolling can be done via scrollbars. If scrollbars are enabled, it's also possible to enabled it with dragging the screen. Since the game has to know what should be inside of the container, there are some attributes which must be used in the container. `size = { ... }` has to be defined using pixels instead of percentage values (for directions where scrolling is enabled) to ensure that it doesn't stretch to fit all elements. `clipping = yes` should be true (or unset, making it default to true). A `background = { ... }` also has to be defined for the container, since it establishes the boundaries.

Scrollbars use [extendedScrollbarType](#extendedscrollbartype) definitions. If this definition is inside of a container, in which case it will be automatically assigned to the container without needing to assign it manually, however it can't be used for any other container. If the definition is entirely independent, it will not be assigned to any by default, but can be re-used in multiple containers.

In particular, these arguments enable scrolling, assuming the conditions are fulfilled:

- `verticalScrollbar = scrollbar_name` assigns an external ExtendedScrollbarType to act as the vertical scrollbar. The scrollbar can't have `horizontal = yes` in its definition.
- `horizontalScrollbar = scrollbar_name` assigns an external ExtendedScrollbarType to act as the horizontal scrollbar. The scrollbar must have `horizontal = yes` in its definition.
- `drag_scroll = { left middle right }` enables drag scrolling. The drag scrolling will only work if there exists a scrollbar for the same axis. The direction represent the mouse button that the scrolling can be done with, however only `left` seems to work in-game. If there's only one button, it can be shortened as `drag_scroll = left`.

In addition, there are optional attributes that can be used to refine the scrollbar:

- `margin = { top = 10 bottom = 10 left = 20 right = 20 }` is used to determine the margins of the container. These areas will be taken as the border of the window, unaffected by the scrollbar; only what's inside of the margin's border will be modified by the scrollbar.
- `autohide_scrollbars = no` – By default, a scrollbar will not appear if it isn't necessary due to all elements being inside of the container's `size`. If this is set to false, then it will always appear.
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
- **hint\_tag** - Set the hint key the icon uses to display a hint tooltip with when hovered over.
- **pdx\_tooltip** - The tooltip that is shown when hovering over the button.
- **pdx\_tooltip\_delayed** - Sets the delayed tooltip to display to the player. Takes a localization key.
- **centerposition** - Sets whether the position is from the center of the icon.

## instantTextBoxType

The *instantTextBoxType* element is used to add text to the interface. In some instances, the text for the element is generated internally (i.e. *regiment\_count*). In these instances you cannot edit the text unless it is exposed in an localized string.

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
- **scrollbarType** - which kind of scrollbar to use (for example standardtext\_slider)
- **pdx\_tooltip** - Sets the tooltip to display to the player. Takes a localization key.
- **pdx\_tooltip\_delayed** - Sets the delayed tooltip to display to the player. Takes a localization key.

The following attributes are rarely or never used:

- **textureFile** - Never used for anything.

Valid *format* values:

- left
- center
- right

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
- **hint\_tag** - Set the hint key the icon uses to display a hint tooltip with when hovered over.
- **pdx\_tooltip** - The tooltip that is shown when hovering over the button.
- **pdx\_tooltip\_delayed** - Sets the delayed tooltip to display to the player. Takes a localization key.
- **scale** - Scales the button size.
- **web\_link** - URL to open in browser

The following attributes are rarely or never used:

- **tooltip** - Never used.
- **tooltipText** - Never used.
- **delayedTooltipText** - Never used.

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
- **hint\_tag** - Set the hint key the checkbox uses to display a hint tooltip with when hovered over.
- **pdx\_tooltip** - Set the short tooltip this checkbox uses.
- **pdx\_tooltip\_delayed** - Set the full tooltip this checkbox uses.
- **scale** - Scales the checkbox size.

The following attributes are rarely or never used:

- **tooltip** - Never used.
- **tooltipText** - Never used.
- **delayedTooltipText** - Never used.

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
- **ignore\_tab\_navigation** - Makes the element ignore tab navigation.

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

## Fonts

*See also: Font modding*

The following fonts are usable in Hearts of Iron IV:

- Arial12
- Arial12\_bold
- cg\_16b
- cg\_18b
- garamond\_12
- garamond\_14
- garamond\_14\_bold
- garamond\_16
- garamond\_16\_bold
- garamond\_24
- hoi\_16mbs
- hoi\_16tooltip3
- hoi\_16typewriter
- hoi\_18
- hoi\_18b
- hoi\_18mbs
- hoi\_20b
- hoi\_20bs
- hoi\_22tech
- hoi\_22typewriter
- hoi\_24header
- hoi\_26mbs
- hoi\_30header
- hoi\_33
- hoi\_36header
- hoi4\_typewriter16
- hoi4\_typewriter22
- hoi\_mapfont4
- hoi\_arrow\_font
- newsfeed\_body
- newsfeed\_title
- standard
- standard\_18
- standard\_22
- tahoma\_20\_bold
- vic\_18
- vic\_18\_grey
- vic\_18s
- vic\_22
- vic\_22\_bl
- vic\_22s
- vic\_36
- vic\_36s

**[Modding](<Modding - Hearts of Iron 4 Wiki.md>)**
