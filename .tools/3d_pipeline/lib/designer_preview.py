"""The size of the game's designer preview, where a player looks at a unit's model and its animations (D-140).

The division designer (`interface/divisiondesignerview.gui`) shows the template's model in a square frame, the button
`toggle_model_selector_button` (249 by 249 pixels at the interface's own scale). Clicking it opens the model picker,
`div_template_select_model`, whose `3d_view` sits in `border_container` (510 by 316). Both frames hold the `GFX_3d_view_placeholder`
sprite, which the engine replaces with the rendered model. The camera that frames the model inside them is the engine's own: no
interface or define file sets it, so the review sheets fit the unit to the frame with the close-up margin (`FILL`), and the first
in-game look at a designer preview confirms or corrects that share.

`measure(text)` reads the two frames from the file's text. `PREVIEW_PX` and `PICKER_PX` are the numbers read from the installed game
on 2026-11-23, which the tests hold `measure` to on a copy of the blocks.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, Optional, Tuple

GUI_FILE = "interface/divisiondesignerview.gui"
PREVIEW_PX = 249  # the designer's model frame, toggle_model_selector_button, square
PICKER_PX = (510, 316)  # the model picker's view, border_container in div_template_select_model (width, height)
FILL = 1.15  # the frame's height over the unit's, as the close-up sheets frame a unit (an assumption until checked in the game)


def _block(text: str, name: str) -> Optional[str]:
    """The braces block of the element named `name`: from its `name = "..."` line to the brace that closes its element."""

    match = re.search(r'name\s*=\s*"?' + re.escape(name) + r'"?', text)
    if not match:
        return None
    start = text.rfind("{", 0, match.start())
    depth = 0
    for index in range(start, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return text[start:index + 1]
    return None


def _size(block: Optional[str]) -> Optional[Tuple[int, int]]:
    """The element's own `size`, `{ x = .. y = .. }` or `{ width = .. height = .. }`, before any child element opens."""

    if block is None:
        return None
    own = block[1:]
    child = re.search(r"\w+Type\s*=\s*\{|background\s*=\s*\{", own)
    own = own[: child.start()] if child else own
    match = re.search(r"size\s*=\s*\{\s*(?:x|width)\s*=\s*(\d+)\s*(?:y|height)\s*=\s*(\d+)", own)
    return (int(match.group(1)), int(match.group(2))) if match else None


def measure(text: str) -> Dict[str, Optional[Tuple[int, int]]]:
    """The designer's model frame and the model picker's view, (width, height) in interface pixels, from divisiondesignerview.gui."""

    picker = _block(text, "div_template_select_model")
    return {
        "preview": _size(_block(text, "toggle_model_selector_button")),
        "picker": _size(_block(picker, "border_container")) if picker else None,
    }


def measure_game(game_dir: Path) -> Dict[str, object]:
    """`measure` on the installed game's file, with the file it read."""

    path = Path(game_dir) / GUI_FILE
    return {"file": GUI_FILE, **measure(path.read_text(encoding="utf-8", errors="replace"))}
