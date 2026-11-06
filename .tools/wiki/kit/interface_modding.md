# Interface modding

<!-- kit:begin id="review" build="1.19.4.1" checked="2026-11-01" revision="100547" sources="interface/ gfx/fonts/ common/scripted_guis/_documentation.md hoi4.exe" -->
**Kit review (HOI4 1.19.3.0, 2026-10-31).** Checked against a census of the 130 vanilla `interface/*.gui` files (element types, attributes, value forms, size forms), the `bitmapfont` registrations in `interface/*.gfx`, `gfx/fonts/`, and the scrollbar and container usage in the vanilla windows. Focus inlay windows are covered by [National focus modding](<national_focus_modding.md>); scripted GUI attachment by [Scripted GUI modding](<scripted_gui_modding.md>).
- Kit blocks added: an element census, the container attributes with vanilla counts, per-element attribute checks (icon, text, button, checkbox, edit box, list boxes, overlapping box, scrollbars), the `size` forms, orientation values, the fonts that are registered, and the element types the page does not describe (`gridBoxType`, `dropDownBoxType`, `positionType`, `windowType`, `browserType`).
- Errors found in the wiki text: `tooltip` on buttons is not "never used" (29 uses); `background` on `listboxType` is not "never used" (21 of 30); text alignment also accepts `centre` (250 uses); the `editBoxType` list copies text box attributes that no vanilla edit box writes and omits `size`, which all 84 write; `shieldtype` and `eu3dialogtype` have no use in vanilla `.gui` files; 15 of the 33 listed fonts have no `bitmapfont` entry in `interface/*.gfx`.
- Gaps left: no documentation file exists for `.gui` files, so the meaning of attributes the wiki does not describe (for example `rotation`, `scale`, `click_to_front`) is read from usage only. Nothing was run in the game.
**1.19.4.1 re-check (2026-11-01).** 26 tagged statements depended on files the update changed (`interface/*.gui` and `interface/*.gfx`), and all of them were re-measured with a new census of the 132 top-level `.gui` files and the font registrations. Most counts moved (for example 2,024 containers, 2,054 buttons, 3,054 icons, 82 buttons with a size), the `orientation = left` count went from four to eight blocks, the `min` count on container sizes is 13 (one in `frontendmainview.gui` was missed before), the claim that `.gui` files write a font name in a different case than its registration no longer holds, and `keybind` on buttons, `tooltip` on one checkbox and one edit box are new. Every other statement cites files that are byte-identical in 1.19.4.1 (Steam depot manifest diff).
<!-- kit:end id="review" -->

<!-- kit:begin id="if-census" at="section:overview" -->
What vanilla `interface/*.gui` contains in 1.19.4.1, as a base for the checks below. All numbers: [vanilla-confirmed 1.19.4.1] a count over the 132 `.gui` files in `interface/`.

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

All rows: [vanilla-confirmed 1.19.4.1] `interface/*.gui`. A `buttonType` that sets a size, from `interface/airselectionview.gui`: `size = {x = 220 y = @equipment_entry_heigth}`.
<!-- kit:end id="if-census" -->

<!-- kit:begin id="if-constants-note" at="section:constants" -->
Vanilla `.gui` files define their own constants: 238 `@name = value` definitions in 31 of the 132 files, used for positions and sizes, for example `size = {width = 220 height = @equipment_entry_heigth}` in `interface/airselectionview.gui`. [vanilla-confirmed 1.19.4.1] `interface/*.gui`.
<!-- kit:end id="if-constants-note" -->

<!-- kit:begin id="if-container-attrs" at="section:arguments" -->
The container attributes of this page against the 2,024 vanilla `containerWindowType` blocks. All rows: [vanilla-confirmed 1.19.4.1] `interface/*.gui`.

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

Attributes that vanilla containers use and the page does not mention: `click_to_front = yes` (120), `vertical_scroll_step` (15), `background_margin` (11, for example `{ bottom = 15 }`), `scale` (8) and, once each in a sliding window, `closed_position`, `open_position`, `peek_position`, `peek_check_top_left` and `peek_check_size`. [vanilla-confirmed 1.19.4.1] `interface/*.gui`. Their effects are read from the names only and are untested. [unverified]
<!-- kit:end id="if-container-attrs" -->

<!-- kit:begin id="if-scrollbar-notes" at="section:scrollbartype" -->
All 14 attributes in the list above (`name`, `slider`, `track`, `leftbutton`, `rightbutton`, `position`, `size`, `priority`, `borderSize`, `maxValue`, `minValue`, `stepSize`, `startValue`, `horizontal`) appear in every one of the 31 vanilla `scrollbarType` blocks, plus one `scroll_speed`. `horizontal` is the number 1 in 28 blocks and 0 in 3. [vanilla-confirmed 1.19.4.1] `interface/*.gui`. `scrollbarType` is what list boxes and text boxes name in their `scrollbarType = ...` attribute: `standardlistbox_slider` (43 uses) and `standardtext_slider` (27). [vanilla-confirmed 1.19.4.1] `interface/*.gui`.

The scrollbar of a container is a different element, `extendedScrollbarType`, which the "Scrolling" section mentions without listing its attributes. The 22 vanilla blocks use `name`, `position`, `size` (`{ width = .. height = .. }`), `startValue` (22), `slider` (22), `track` (21), `decreaseButton` and `increaseButton` (18 each), `background` (14), `tileSize`, `maxValue`, `minValue`, `stepSize`, `horizontal` (10 each, written `yes`), `orientation` and `origo` (8 each), `clickOnly` (6), `smooth_scrolling` (4, with values such as 0.25 and 1.25) and `setTrackFrameOnChange` (2). All 313 `verticalScrollbar` and `horizontalScrollbar` references in vanilla point at an `extendedScrollbarType`. [vanilla-confirmed 1.19.4.1] `interface/*.gui`.
<!-- kit:end id="if-scrollbar-notes" -->

<!-- kit:begin id="if-element-types" at="section:elements" -->
Checks of the lists above.

- `shieldtype` and `eu3dialogtype` are not used by any of the 132 vanilla `.gui` files. Country flags in vanilla come from `maskedShieldType` sprites in `.gfx` files (`interface/core.gfx`, `interface/general_stuff.gfx`, `interface/countryconstructionsview.gfx`), not from a `.gui` element. [vanilla-confirmed 1.19.4.1] `interface/*.gui`, `interface/*.gfx`.
- The "legacy" types are still used widely: `guiButtonType` 340 blocks, `windowType` 83 and `textBoxType` 23. `guiButtonType` has the attributes of `buttonType` plus `parent` (28 blocks); `windowType` groups children and writes `moveable` as 0 or 1, `fullScreen`, `horizontalBorder` and `verticalBorder`, `dontRender` and `background`. [vanilla-confirmed 1.19.4.1] `interface/*.gui`. For new windows prefer `containerWindowType` and `buttonType`, the types the page names as current. That is advice, and no defined test shows it. [unverified]
- Element types in vanilla that the page does not describe are covered in the section "Element types the page does not describe" at the bottom of the page.
<!-- kit:end id="if-element-types" -->

<!-- kit:begin id="if-icon-notes" at="section:icontype" -->
The attribute list against the 3,054 vanilla `iconType` blocks. All numbers: [vanilla-confirmed 1.19.4.1] `interface/*.gui`.

- Used: `name` (3,054), `position` (2,979), `spriteType` (2,525), `alwaystransparent` (1,175), `orientation` (547), `quadTextureSprite` (498), `frame` (392), `centerposition` (321, always `yes`), `pdx_tooltip` (117), `pdx_tooltip_delayed` (2), `hint_tag` (1).
- Used but missing from the page: `scale` (395, values such as 0.6, 0.7, 0.8, 0.9), `hide` (57, `hide = yes`), `rotation` (52, mostly 1.5708, which looks like a quarter turn in radians), `context_aware_tooltip` (40, a scripted localisation call such as `[GetNavalFactionDesc]`), `tooltip` (10, a localisation key) and `buttonMesh` (1). All counts: [vanilla-confirmed 1.19.4.1] `interface/*.gui`, 3,054 `iconType` blocks. The meanings of `scale`, `rotation` and `hide` are inferred from the values. [unverified]
- No `iconType` writes `size`. [vanilla-confirmed 1.19.4.1] 0 of 3,054 `interface/*.gui`. The icon is drawn at the size of its sprite, scaled by `scale`. [unverified]
- `spriteType` is the common choice (2,525) over `quadTextureSprite` (498).
<!-- kit:end id="if-icon-notes" -->

<!-- kit:begin id="if-text-notes" at="section:instanttextboxtype" -->
The attribute list against the 2,798 vanilla `instantTextBoxType` blocks. All numbers: [vanilla-confirmed 1.19.4.1] `interface/*.gui`.

- Used as the page says: `name`, `position` (2,795), `font` (2,772), `maxWidth` (2,751), `maxHeight` (2,546), `format` (2,457), `text` (2,259), `borderSize` (879, written `{ x = .. y = .. }`), `fixedsize` (865), `alwaystransparent` (590), `orientation` (488), `pdx_tooltip` (157), `scrollbarType` (29, always a scrollbar such as `standardtext_slider`).
- `format` takes `left` (1,037), `center` (988), `centre` (252) and `right` (181). The page lists three values; `centre` is a fourth spelling in common use.
- `pdx_tooltip_delayed` is listed on the page but no `instantTextBoxType` writes it.
- `textureFile` is written in 607 blocks, almost always as an empty string (`textureFile = ""` in 630 of 657 uses across all types), which fits "never used for anything".
- Used but missing from the page: `vertical_alignment` (117: `center` for nearly all, `top` for 4), `multiline` (72), `context_aware_text` (39, a localisation key or a scripted localisation call), `truncate` (33, `yes` in 32), `context_aware_tooltip` (2), `text_color_code` (29, a one-letter colour code such as `b`, `g` or `L`), `tooltip` (14) and `hide` (4). Their meanings are read from the names and are untested. [unverified]
<!-- kit:end id="if-text-notes" -->

<!-- kit:begin id="if-button-notes" at="section:buttontype" -->
The attribute list against the 2,054 vanilla `buttonType` blocks. All numbers: [vanilla-confirmed 1.19.4.1] `interface/*.gui`.

- Used as the page says: `name`, `position` (2,003), `quadTextureSprite` (1,457), `clicksound` (1,414), `spriteType` (598), `buttonFont` (586), `orientation` (554), `pdx_tooltip` (434), `buttonText` (415), `shortcut` (368), `oversound` (300), `frame` (270), `scale` (136), `web_link` (76), `alwaystransparent` (43), `pdx_tooltip_delayed` (36). `quadTextureSprite` is the common sprite key for buttons, more than twice as common as `spriteType`.
- `tooltip` is **not** "never used": 29 buttons write it, with a localisation key (`tooltip = "LEDGER_CIV_GRAPH_SHOW_INDUSTRY"`). `tooltipText` and `delayedTooltipText` have no use. `hint_tag` is listed on the page but no `buttonType` writes it.
- Used but missing from the page: `size` (82, always `{ x = .. y = .. }`), `font` (313) and `text` (180) next to `buttonFont` and `buttonText`, `pdx_tooltip_anchor` (55), `centerposition` (52), `no_clicksound` (21, always `yes`), `format` (17), `enabled` (8, always `no`), `borderSize` (6), `multiline` (3), `pdx_disabled_tooltip` and `pdx_disabled_tooltip_delayed` (1 each), `rotation` (1), `hide` (2) and `keybind` (12, a name such as `air_wings_split`, written mostly in files the 1.19.4.1 update changed).
- The vanilla files contain two typos you should not copy: `format = left;` with a semicolon, in two buttons.
- The heading of this section describes `guiButtonType`, a typo in the wiki text. `buttonType` is the current spelling; `guiButtonType` (340 blocks) also still works. [vanilla-confirmed 1.19.4.1] `interface/*.gui`.
<!-- kit:end id="if-button-notes" -->

<!-- kit:begin id="if-smoothlist-notes" at="section:smoothlistboxtype" -->
Of the 14 vanilla `smoothListboxType` blocks, all write `name`, `position` and `size`; 13 write `scrollbarType`, and the rest of the page's list is rarely used (`orientation` 6, `bordersize` 6, `spacing` 3). `horizontal` and `alwaystransparent` appear in none, while `priority` (3) and `clipping` (2) do. `background` has no use, as the page says. [vanilla-confirmed 1.19.4.1] `interface/*.gui`.
<!-- kit:end id="if-smoothlist-notes" -->

<!-- kit:begin id="if-list-notes" at="section:listboxtype" -->
`background` is not "never used" on `listboxType`: 21 of the 30 vanilla `listboxType` blocks write it. The other attributes: `name`, `position`, `size` (all 30, `{ x = .. y = .. }`), `scrollbarType` (28), `orientation` (25), `spacing` (24), `bordersize` (19), `horizontal` (9, always 0), `alwaystransparent` (3), `priority` (2) and `offset` (2). [vanilla-confirmed 1.19.4.1] `interface/*.gui`.
<!-- kit:end id="if-list-notes" -->

<!-- kit:begin id="if-checkbox-notes" at="section:checkboxtype" -->
All 164 vanilla `checkboxType` blocks use `quadTextureSprite` and none uses `spriteType`. Attributes in use: `name`, `position`, `quadTextureSprite` (164 each), `clicksound` (104), `orientation` (60), `buttonFont` (51), `buttonText` (44), `pdx_tooltip` (9), `frame` (5), `tooltip` (1, in `countryintelligenceagencyview.gui`) and `pdx_tooltip_delayed` (1). `shortcut`, `scale`, `hint_tag` and `alwaystransparent` are listed on the page and written by no vanilla checkbox. `tooltipText` and `delayedTooltipText` are unused, as the page says, but `tooltip`, which the page calls never used, now appears in one checkbox. [vanilla-confirmed 1.19.4.1] `interface/*.gui`.
<!-- kit:end id="if-checkbox-notes" -->

<!-- kit:begin id="if-editbox-notes" at="section:editboxtype" -->
The list above copies the text box attributes, and the vanilla edit boxes do not use most of them. All 85 vanilla `editBoxType` blocks write `size` (always `{ x = .. y = .. }`), `name`, `position` and `font`, and the page does not list `size`. They also use `text` (69), `bordersize` (52), `orientation` (45), `textureFile` (27), `ignore_enter` (6), `cursor` (5), `only_numbers` (3, `yes`), `is_multiline` (2), `pdx_tooltip` (1) and `tooltip` (1). None writes `maxWidth`, `maxHeight`, `format`, `fixedsize` or `alwaystransparent`, and no `.gui` file writes `ignore_tab_navigation`, although the string exists once in `hoi4.exe`. [vanilla-confirmed 1.19.4.1] `interface/*.gui`, 0 uses of that key. The executable string says nothing about whether the key works. [unverified] `hoi4.exe`
<!-- kit:end id="if-editbox-notes" -->

<!-- kit:begin id="if-overlap-notes" at="section:overlappingelementsboxtype" -->
The 46 vanilla `OverlappingElementsBoxType` blocks write `name`, `position` and `size` (all 46), `spacing` (45), `format` (42: `left` 22, `right` 11, `center` 9), `orientation` (13) and `first_on_top` (10, `yes` in 9). `format` and `first_on_top` are missing from the page's list, which also names `horizontal`, `bordersize` and `alwaystransparent`, written by none of them. The "Valid format values" list at the end of this section is right for `format` here. [vanilla-confirmed 1.19.4.1] `interface/*.gui`.
<!-- kit:end id="if-overlap-notes" -->

<!-- kit:begin id="if-orientation-notes" at="section:position-and-orientation" -->
Orientation and position as vanilla writes them. All bullets: [vanilla-confirmed 1.19.4.1] `interface/*.gui`.

- The values in use are `upper_left`, `upper_right`, `lower_left`, `lower_right`, `center`, `center_up`, `center_down`, `center_left`, `center_right` and `center_lower` (7 uses). `center_upper` is never written. `center_up` has 75 uses and `center_down` 37. [vanilla-confirmed 1.19.4.1] `interface/*.gui`. That `center_lower` is an alias for `center_down` is a guess. [unverified]
- Values are written quoted (`orientation = "upper_left"`) or bare (`orientation = upper_left`), in any case, and vanilla also writes `orientation = left` in eight blocks (two edit boxes, two buttons, a checkbox, an overlapping box and two text boxes), a value the page does not list. [vanilla-confirmed 1.19.4.1] `interface/*.gui`: 2,435 `orientation` lines are quoted or bare, in upper, lower or mixed case.
- `position` is always `{ x = .. y = .. }` and the values can be negative (`position = { x=0 y=-22 }` in `interface/AST_cabinet_trust_scripted_gui.gui`). 547 of the 2,024 containers write an `orientation`.
<!-- kit:end id="if-orientation-notes" -->

<!-- kit:begin id="if-fonts-notes" at="section:fonts" -->
Fonts are registered with `bitmapfont = { name = ".." ... }` blocks in `interface/*.gfx`, mostly `interface/core.gfx`, with 44 names across `interface/*.gfx` in 1.19.4.1, `interface/core.gfx` among them. In 1.19.4.1 every `font` and `buttonFont` value in `interface/*.gui` is written in the same case as its registration (for example `Main_14_black`), so vanilla shows no case mismatch. [vanilla-confirmed 1.19.4.1] `interface/core.gfx`, `interface/*.gui`. Whether the game matches font names without regard to case is not shown and is untested. [unverified] See [Font modding](font_modding.md).

- 15 of the 33 names in the list above have no `bitmapfont` entry in any `interface/*.gfx` file: `Arial12_bold`, `cg_18b`, `garamond_14_bold`, `garamond_16`, `garamond_16_bold`, `garamond_24`, `hoi_16tooltip3`, `hoi_26mbs`, `hoi_mapfont4`, `newsfeed_body`, `newsfeed_title`, `standard`, `standard_18`, `standard_22` and `tahoma_20_bold`. Some have font files in `gfx/fonts/`, but whether a font can be used by name without a registration is not shown. [vanilla-confirmed 1.19.4.1] `interface/*.gfx`, `gfx/fonts/`, and no `.gui` file uses any of the 15. Whether a font works without a registration is untested. [unverified]
- Registered fonts that the list omits include `Main_14`, `Main_14_black`, `Main_14_bold`, `Main_14_eu`, `Main_14_grey`, `Main_16`, `ToolTip_Font`, `hoi_22chat`, `hoi_30`, `vic_22`, `vic_36`, `standard_font`, `chat_input_font`, `hoi4_typewriter16_inverted` and `hoi4_typewriter22_inverted`. [vanilla-confirmed 1.19.4.1] `interface/core.gfx` and related `.gfx` files.
- The workhorses of the vanilla windows, counting `font` and `buttonFont` uses in `.gui` files: `hoi_18mbs` (1,470), `hoi_16mbs` (1,072), `vic_18` (231), `hoi_36header` (190), `hoi_24header` (160), `hoi_20b` (152), `hoi_20bs` (93), `hoi4_typewriter16` (92), `hoi_18b` (77). [vanilla-confirmed 1.19.4.1] `interface/*.gui`.
<!-- kit:end id="if-fonts-notes" -->

<!-- kit:begin id="if-other-types" at="bottom" -->
## Element types the page does not describe

Types that appear in vanilla `.gui` files but have no section above. Counts are blocks in the 132 files and attributes are the keys they write. All rows: [vanilla-confirmed 1.19.4.1] `interface/*.gui`. The meanings are read from names and usage and are untested. [unverified]

| Type | Blocks | Attributes and notes |
| --- | --- | --- |
| `gridBoxType` | 596 | `name`, `slotsize` (571, `{ width = .. height = .. }`), `position` (556), `size` (546), `format` (528, values such as `"UPPER_LEFT"`, `"LEFT"`, `"UP"`, `"UPPER_RIGHT"`), `max_slots_horizontal` (398), `max_slots_vertical` (111), `orientation` (34), `max_slots` (27), `add_horizontal` (26), `background` (6), `padding` (5). This is the element a scripted GUI dynamic list fills. |
| `dropDownBoxType` | 38 | `name`, `position`, an `expandedWindow` child (38, 37 of them with `show_animation_type = decelerated` and `hide_animation_type = accelerated`), `expandButton` (35), `size` (27), `clipping` (9), `switch_frame_on_expand` (3), `expandedOnTop` (2) |
| `positionType` | 160 | only `name` and `position`; a named position |
| `windowType` | 83 | older dialog type: `name`, `position`, `size` (80), `moveable` (77, 0 or 1), `background` (72), `fullScreen` (67), `horizontalBorder` and `verticalBorder` (56), `dontRender` (53), `orientation` (52), with `guiButtonType` and `textBoxType` children |
| `textBoxType` | 23 | `name`, `position`, `textureFile`, `bordersize`, `font`, `maxWidth`, `maxHeight` (all 23), `text` (21); the older form of `instantTextBoxType` |
| `browserType` | 1 | `name`, `spriteType`, `position`, `size`; the name suggests an embedded web view |
| `extendedScrollbarType` | 22 | the container scrollbar, see the notes under "scrollbarType" |

Scripted GUIs fill a `gridBoxType` from an array through `dynamic_lists`, which is why the page [Scripted GUI modding](scripted_gui_modding.md) pairs them. [docs] `common/scripted_guis/_documentation.md`.
<!-- kit:end id="if-other-types" -->
