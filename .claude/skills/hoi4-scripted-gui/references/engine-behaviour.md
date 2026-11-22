# Engine behaviour a render does not show

The MCP renderer reads the `.gui` and `.gfx` source; the game lays some windows out by code at run time. Each rule below was seen in a game capture, not in a render. Follow it when you build or restyle a window, run its check, and confirm the rest in a capture of the exact state.

Run the static check on every changed `.gui` file: `python -B .tools/check.py quick --paths interface/<file>.gui` (or `python -B .tools/audits/audit_gui_rules.py --paths interface/<file>.gui`). Errors must be fixed; a review finding must be read and either fixed or explained in the handoff.

## 1. Negative sizes count from the element's own place

- A negative `height` (or `width`) is the fill from the element's own `y` (or `x`) to its parent's far edge, less that many pixels. It is not "the parent's size less that much".
- So a list that should end 96 px above its parent's foot writes `height = -96`, whatever its `y`. Writing the parent's height less its place and the gap (for example `-473` at `y = 377`) collapses it to nothing in the game.
- A root window under a bar at `y = B` with `height = -B` ends B px over the screen's foot: the window is the screen less 2B tall. Budget its rows on that height.
- The renderer and some lints read a negative size the other way, so the render looks right while the game collapses the element. Work the height out by hand at the smallest supported screen (720 px tall) before trusting a picture.
- Check: `GUI-NEGATIVE-SIZE` (review) flags a negative size larger than the element's offset. Confirm each one: is the number the gap alone?

## 2. A text box takes only a plain scrollbar

- A text box's `scrollbartype` must name a plain `scrollbarType` block (the base game's `standardtext_slider` or `standardlistbox_slider`). An `extendedScrollbarType` is for a list's `verticalScrollbar` only.
- On a text box it crashed the game at load, with no log line naming the cause.
- Check: `GUI-TEXT-EXTENDED-SCROLLBAR` (error).

## 3. Quoted words are read as written

- `format = "left"` logs "Unknown format token", and a quoted lower-case `orientation` on a top-level window logs "Not a valid orientation".
- Write the bare word (`format = left`, `orientation = upper_left`) or the quoted word in upper case (`"LEFT"`).
- Check: `GUI-QUOTED-WORD` (error).

## 4. The event window is laid out by its text

- The engine looks for `Description` directly in the container `midsection` and nowhere else. Anywhere else it shows the placeholder text from the file.
- It binds the event picture only inside `bottom_Window` in the plain event window. The news window keeps its picture in its header.
- It places `bottom_Window`, with the picture and the options, right under the description by the text's real height, line by line. Neither `maxHeight` nor `fixedsize` keeps it still. A text one line longer moves the picture and the options one line down, and a long text pushes them out of the frame.
- So:
  - declare `bottom_Window` where the engine will put it: measure, in a capture, where a text of n lines puts it, then add one line height for every line over n;
  - give the picture a negative `y` inside `bottom_Window` that lands it in its seat;
  - pad every description to one line count, so all texts put `bottom_Window` in the same place;
  - keep every description within that count. Measure each text's wrapped line count in its real font and width; a font-aware measure catches what a character count misses.
- Check: `GUI-EVENT-PLACEMENT` (error) for the two places. The line count needs a measuring step in the build, not a lint.

## 5. Grounds the engine sets by name, and the disabled grey

- Some grounds are set by the engine by sprite name, over whatever the layout names. Template rows and unavailable entries are examples. If a capture still shows the old ground after a layout swap, the engine draws that sprite by name. Restyle it by writing the base texture at its base size, frame count and mip levels, not by swapping the name in the layout.
- A sprite's `effectFile` decides what a disabled element looks like:
  - `buttonstate.lua`, `buttonstate_nodowneffect.lua` and `buttonstate_onlydisable.lua` grey the whole texture by its luminance when the engine disables the element. A row the player cannot act on becomes a grey slab, whatever colour the texture has.
  - If the ground must keep its colour, redefine the sprite with `gfx/FX/buttonstate_nodownordisableeffect.lua`. Use a whole-file override of the base `.gfx` that changes only that `effectFile` line, or a sprite of your own.
  - For a button that must show its own disabled state, draw a four-frame strip whose fourth frame is your disabled frame.
- Check: no static lint can know which elements the engine disables. Before restyling a ground, read its sprite's `effectFile` in the base `.gfx`, and capture the disabled state (an entry the player cannot use).

## 6. What a restyle rule must not replace

A rule that restyles many textures at once (a whole-interface reskin, a kit applied by rule) breaks three kinds of texture silently:
- **A ground laid over something the engine draws beneath it** (a 3D model view, a portrait, the map) must leave its middle clear: a rim with a transparent centre. An opaque ground hides the engine's picture.
- **A texture shared by several sprites carries one meaning per sprite.** Two progress bars that use each other's textures as fill and ground ended in one colour, so the bar never showed where one side ends. Give each side its own look.
- **A texture that already has reviewed bespoke art** (a pictogram, a painted picture) is not overwritten by the generic ground.
- Check: before a rule restyles a texture, list every sprite that draws it and every state it is drawn in (fill, ground, overlay, disabled), and test that reviewed art survives the restyle. A per-project test is the right tool here; a generic lint cannot know which art was reviewed.
