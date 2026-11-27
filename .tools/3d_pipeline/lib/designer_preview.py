"""The size of the game's designer preview, where a player looks at a unit's model and its animations (D-140).

The division designer (`interface/divisiondesignerview.gui`) shows the template's model in a square frame, the button
`toggle_model_selector_button` (249 by 249 pixels at the interface's own scale). Clicking it opens the model picker,
`div_template_select_model`, whose `3d_view` sits in `border_container` (510 by 316). Both frames hold the `GFX_3d_view_placeholder`
sprite, which the engine replaces with the rendered model. The frame shows the sub-unit's own entity: a mod's custom tank appeared there,
not vanilla's model of its equipment.

No interface or define file sets the camera inside the frame, so it was fitted to the game (`GAME_FILL`). On HOI4 1.20.0.0 at 1920 by
1080 the designer showed a custom light tank (an M2A4 the kit made, at entity scale 0.7) 149 by 136 pixels in the 249 pixel frame,
0.60 of its width and 0.55 of its height, front three-quarter and from above. `tripo/designer_calibrate.py` rendered that mesh over a
grid of views and fitted each silhouette to the screenshot's: `VIEW` is the best view (30 degrees round, 27 up, overlap 0.68; a view
at 38 and 39 scores the same, so the elevation is known only to about ten degrees), and `FRAME_WORLD` is the frame's width in game units
that gives the tank its width in the game. Every unit is drawn with that one camera at its entity scale, so its size in the frame is
its size in the game, never a fit to its own outline.

Open, for a later in-game look to settle (`tripo/designer_calibrate.py` refits from a screenshot): whether the camera is the same for
every model (an infantry template), and whether the designer plays the idle. The tank showed its rest facing, while its idle clip
turns a tank's hull 90 degrees, as vanilla tanks' idles do. `VIEW` is taken against a unit's rest facing.

`measure(text)` reads the two frames from the file's text. `PREVIEW_PX` and `PICKER_PX` are the numbers read from the installed game
on 2026-11-23, which the tests hold `measure` to on a copy of the blocks.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, Optional, Tuple

import numpy as np

GUI_FILE = "interface/divisiondesignerview.gui"
PREVIEW_PX = 249  # the designer's model frame, toggle_model_selector_button, square
PICKER_PX = (510, 316)  # the model picker's view, border_container in div_template_select_model (width, height)

# The in-game measurement (the Windows check of 2026-11-24, screenshot d07): the frame spans x 1297 to 1546 and y 545 to 794 of the
# 1920 by 1080 screen. The calibration render drew the same mesh at the calibration camera `calibration_ortho` mesh units wide; at
# `VIEW` it spans `render_pixels` of the 249 pixel tile, so the game's frame is FRAME_WORLD = render width / 249 * ortho * scale / fill.
GAME_FILL = {
    "build": "1.20.0.0",
    "date": "2026-11-24",
    "unit": "tank_m2a4_sm (a kit Smart Mesh light tank in a test mod)",
    "entity_scale": 0.7,
    "pixels": (149, 136),
    "width": 149 / 249,
    "height": 136 / 249,
    "calibration_ortho": 9.6979,
    "render_pixels": (156, 135),
}
VIEW = (30.0, 27.0)  # (azimuth, elevation) in degrees against the unit's rest facing: azimuth 0 faces the unit, as the renderer's views
FRAME_WORLD = 7.1074  # the frame's width in game units (mesh units times the entity's scale)
# The class reference a vehicle's preview sheet shows when no job names one: vanilla's light tank, `USA_light_armor_entity`.
VEHICLE_REFERENCE = {"mesh": "gfx/models/units/tanks/USA_tank_light.mesh", "entity_scale": 0.85}


def view_axes(view: Tuple[float, float] = VIEW) -> Tuple[np.ndarray, np.ndarray]:
    """The screen's right and up directions in a `.mesh` file's own frame (Y up, the unit facing +Z) for a camera at `view`."""

    azimuth, elevation = (np.radians(value) for value in view)
    towards = np.array([np.sin(azimuth) * np.cos(elevation), np.sin(elevation), np.cos(azimuth) * np.cos(elevation)])
    right = np.cross(-towards, [0.0, 1.0, 0.0])
    right /= np.linalg.norm(right)
    return right, np.cross(right, -towards)


def projected_extent(points: np.ndarray, view: Tuple[float, float] = VIEW) -> Tuple[float, float]:
    """(width, height) of the points on the screen of an orthographic camera at `view`, in the points' own units."""

    right, up = view_axes(view)
    points = np.asarray(points, float)
    return float(np.ptp(points @ right)), float(np.ptp(points @ up))


def frame_fill(points: np.ndarray, entity_scale: float, view: Tuple[float, float] = VIEW, frame_world: float = FRAME_WORLD) -> Tuple[float, float]:
    """The share of the designer frame's (width, height) that a model's points fill at its entity scale."""

    width, height = projected_extent(points, view)
    return width * entity_scale / frame_world, height * entity_scale / frame_world


def ortho_for(entity_scale: float) -> float:
    """The review camera's ortho scale in a mesh's own units, for a mesh drawn at `entity_scale`: the designer frame's width."""

    if entity_scale <= 0:
        raise ValueError(f"entity scale {entity_scale} must be above 0")
    return FRAME_WORLD / float(entity_scale)


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
