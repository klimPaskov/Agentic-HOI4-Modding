# Technology tree interface authoring

Read this file when a technology folder, branch, tile, or tab must be added or changed.
`GAME` is the installed Hearts of Iron IV folder named in `CLAUDE.md` and `WIKI` is the repository folder `paradox_wiki`.
Source: `WIKI/Technology modding - Hearts of Iron 4 Wiki.md` (Brief user interface, Position, Folders, Graphical user interface), checked against `GAME/interface/countrytechtreeview.gui` and `.gfx`.
Also read `WIKI/Interface modding - Hearts of Iron 4 Wiki.md` for the control types.

## What must exist for a visible folder

1. The folder in `technology_folders` (`common/technology_tags/*.txt`) with `ledger`.
2. Technologies with `folder = { name = <folder> position = { x y } }`.
3. A folder tab button named `<folder>_tab` inside the `folder_tabs` container window of `countrytechtreeview` (vanilla line ~3768 of `countrytechtreeview.gui`), using a sprite with two frames: the first frame is the open tab and the second the closed tab.
4. A folder container window named exactly like the folder, inside the `countrytechtreeview` window, with the background and any extra pictures or text, and one `gridboxtype` per branch.
5. Item container windows named `techtree_<folder>_item` and, optionally, `techtree_<folder>_small_item`, defined independently (not inside another container).
6. Localisation `<folder>` and `<folder>_desc`.

If any piece is missing, the player cannot research there.
The AI still can, and `set_technology` still works.
Folder windows go in `countrytechtreeview.gui`, not `countrytechnologyview.gui` (the wiki stresses this).

## Branches and gridboxes

- A branch is a series of technologies connected by `path`; it needs one `gridboxtype` named `<first_tech>_tree`, where the first tech is the one in the branch that has no `path` parent.
- Every technology without a `path` parent in a folder must have its own gridbox in that folder, otherwise it does not render.
- Gridbox fields: `position` (top-left pixel position in the folder window), `slotsize` (pixels per x and y unit), `format` (`"LEFT"` for horizontal trees where x runs top to bottom and y runs left to right; `"UP"` for vertical trees where x runs left to right and y runs top to bottom), and optionally `size`.
- Lines draw as: with `LEFT`, one unit right, vertical as needed, then right; with `UP`, one unit down, horizontal as needed, then down.
- A tech with several `path` parents in one folder uses the gridbox of the earliest-defined parent.
- `ignore_for_layout = yes` on a secondary `path` block prevents the "Found multiple potential grid boxes for tech" error.
- Vanilla examples: the `infantry_folder` window and its `support_weapons_tree`, `night_vision_tree`, and `infantry_weapons_tree` gridboxes in `countrytechtreeview.gui`.

Slot size is not free. `techtree_line_item` is one global 70x70 template and the line sprites `techtree_line_horisontal.dds` (144x16, 4 frames) and `techtree_line_vertical.dds` (64x36, 4 frames) are 36-pixel segments drawn from the slot centre, so a slot wider or taller than 70 leaves a visible gap in every connector.
Keep `slotsize = { width = 70 height = 70 }` and space cards by using more slots: a step of 2 is one 140-pixel column, which is the pitch of the vanilla year headers.
For a row pitch other than a multiple of 70, give each branch its own gridbox at its own pixel `position` and keep every card in that branch at the same `x`, the way the vanilla infantry folder stacks its branches at 100 to 115 pixel intervals.
A year header reads correctly when it sits ten pixels left of its column at `y = 50`, and a branch label in the left gutter needs the gridbox origin pushed right far enough for the label plus a small gap, because a 72-pixel card starts exactly at the gridbox origin.

A project technology does not have to be hidden. With `is_special_project_tech = yes`, a folder position and `allow = { ROOT = { is_special_project_completed = sp:<project> } }` it shows as a locked card that explains itself and uses the `GFX_technology_<folder>_special_project_*` backgrounds, as vanilla `jet_fighter1` does; keep its research weight at zero when a project effect already grants it.

```
containerWindowType = {
	name = "my_folder"
	position = { x=0 y=47 }
	size = { width = 100%% height = 100%% }
	margin = { top = 13 left = 13 bottom = 24 right = 25 }
	drag_scroll = { left middle }
	verticalScrollbar = "right_vertical_slider"
	horizontalScrollbar = "bottom_horizontal_slider"
	scroll_wheel_factor = 40
	background = { name = "Background" quadTextureSprite = "GFX_tiled_window_2b_border" }
	iconType = { name = "my_techtree_bg" spriteType = "GFX_my_techtree_bg" position = { x=0 y=0 } }
	gridboxtype = {
		name = "my_first_tech_tree"
		position = { x = 150 y = 60 }
		size = { width = 100 height = 140 }
		slotsize = { width = 70 height = 70 }
		format = "LEFT"
	}
}
```

Start years or branch captions are plain `instantTextBoxType` entries in the folder window, as in the `infantry_subtitle_weapons` entry at the top of the vanilla folder.
A scripted GUI can attach with `parent_window_name`.

## Item containers

- Tile layout comes from the container named for the folder.
  A tile that unlocks equipment uses the regular item; one that does not uses the small item, if the folder defines one.
  If no small item exists, every tile uses the regular item.
  `force_use_small_tech_layout = yes` on the technology overrides the choice.
- The tile contains, by element name:
  `Background` (a `quadTextureSprite`), `Icon` (an `iconType` with `spriteType = "GFX_technology_medium"`, replaced per tech by `GFX_<tech>_medium`), `Name` (optional `instantTextBoxType` on regular tiles), `bonus_icon` (`GFX_tech_bonus`), `bonus` (the bonus percentage text), and up to three `sub_technology_slot_0`, `_1`, `_2` containers with a `picture` icon.
- Sub-technology pictures depend on the sub-technology index, not on the technology.
- Default backgrounds are five sprites in `GAME/interface/countrytechtreeview.gfx`: `GFX_technology_available_item_bg`, `_branch_`, `_unavailable_`, `_researched_`, and the animated `GFX_technology_currently_researching_item_bg`.
- A folder-specific override inserts the folder name after `technology`: `GFX_technology_<folder>_available_item_bg`; for small tiles add `small` as in `GFX_technology_<folder>_small_available_item_bg`; for sub-technologies use `GFX_subtechnology_<folder>_..._item_bg`.
  Vanilla: `GFX_technology_naval_doctrine_folder_unavailable_item_bg`.
- Animated "researching" background example uses `frameAnimatedSpriteType` with `noOfFrames = 9`, `animation_rate_fps = 15`, `looping = yes`, `play_on_show = yes`.
- Tile sizes are set by the container `size`; the background sprite sets the visible size.

## Folder tab sprite

```
spriteType = {
	name = "GFX_my_folder_tab"
	textureFile = "gfx//interface//techtree//techtree_my_tab.dds"
	noOfFrames = 2
}
```

Button entry in `folder_tabs`:

```
buttonType = {
	name = "my_folder_tab"
	position = { x = 22 y = 0 }
	quadTextureSprite = "GFX_my_folder_tab"
	frame = 1
	clicksound = click_default
}
```

Vanilla also adds a hidden (`hide = yes`) `iconType` named `highlight_<folder>` using `GFX_tutorial_research_folder_icon_glow`; it is not needed for a folder to work, and whether the tutorial relies on it for new folders was not checked.

## Technology sprites and localisation

- `GFX_<tech>_medium` in an `interface/*.gfx` file, texture usually under `gfx/interface/technologies/`; vanilla `GAME/interface/Technologies.gfx` and DLC `*_technologies.gfx` files.
- Country override: `GFX_<TAG>_<tech>_medium`.
- Name `<tech>`, description `<tech>_desc`; omitted keys borrow from the unlocked equipment.
- Register tiles the mod adds in its own `.gfx` file under `interface/` rather than editing a vanilla file.

## Doctrine interface for legacy technology doctrines

Doctrine items follow the same `techtree_<folder>_item` pattern and use `countrydoctrinetreeview.gui` (container `countrydoctrineview`, tab container `folder_tabs`), but the current doctrine system does not use technology folders; see `references/doctrine-authoring.md`.

## Checks

- Every technology with a `folder` block has a gridbox reachable by `path` or by its own `<tech>_tree` gridbox.
- Every folder has a tab, a container, and an item container.
- Every sprite name resolves in a `.gfx` file and every texture path exists.
- Tooltips and layout are only checkable in the game; `hoi4.tech_render` with `view = folder` and `view = assets` shows source-linked placement and asset gaps without the game.
- State the unchecked layout in the handoff.
