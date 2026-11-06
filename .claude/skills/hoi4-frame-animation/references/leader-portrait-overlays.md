# hoi4-frame-animation: Leader portrait overlay animations

Part of the [hoi4-frame-animation](../SKILL.md) skill. Read before animating over a country leader portrait with a scripted GUI overlay instead of replacing the portrait.

## 16. Leader portrait overlay animations

Use a scripted GUI overlay when an animation should appear over an existing country leader portrait without replacing the portrait itself. This is the safest pattern for state-driven effects such as burning, corruption, divine glow, warning frames, possession, transmission noise, or route-state overlays.

Do not treat this as a character portrait replacement unless the user explicitly asks to animate the portrait asset itself. The overlay should be a transparent `frameAnimatedSpriteType` with a static fallback, placed by `.gui` and shown by `common/scripted_guis/`.

Required workflow:

1. Inspect the actual vanilla GUI surface that displays the portrait. Common country-leader surfaces include:
  - `<HOI4_INSTALL_DIR>/interface/countrypoliticsview.gui` for the current country's politics leader portrait.
  - `<HOI4_INSTALL_DIR>/interface/countrydiplomacyview.gui` for a selected country's diplomacy leader portrait.
2. Record the exact vanilla element coordinates, scale, and parent containers used to reach that element.
3. Create a separate independent overlay container in a mod `.gui` file. Do not edit vanilla GUI files for the overlay unless the task explicitly requires a vanilla GUI override.
4. Wire that container through `common/scripted_guis/` with the right context:
	- `player_context` for the current/player/tagged country.
	- `diplomacy_target_context` for an overlay that should appear only in the diplomacy tab for the active diplomacy target.
	- `selected_country_context` for selected-country surfaces that are not tied to the diplomacy tab.
5. Parent the scripted GUI to a known token or independent window when possible, then position the overlay from the chosen parent surface.
6. Use `alwaystransparent = yes` on decorative overlay icons so the overlay does not block UI interaction.
7. Document both the parent window and the coordinate source in the asset handoff.

Reusable implementation pattern:

1. Inspect the vanilla portrait surface and record:
	- the independent window name or scripted GUI parent token to attach to
	- every nested parent between the attachment point and the portrait
	- the portrait element name, `position`, `scale`, frame element, and tab/container visibility
2. Define the animation sprites in a `.gfx` file:
	- `spriteType` for the static fallback
	- `frameAnimatedSpriteType` for the sheet, with `noOfFrames`, `animation_rate_fps`, `looping`, and `play_on_show`
3. Define one independent overlay container in a `.gui` file:
	- `containerWindowType` must be top-level under `guiTypes`, not nested inside another container
	- container `position` is the tunable overlay origin
	- container `size` should fit the overlay frame; use `clipping = no` for portrait effects that extend beyond the portrait
	- child `iconType` should usually use `position = { x = 0 y = 0 }`, the animated sprite, matching portrait `scale`, and `alwaystransparent = yes`
4. Wire one scripted GUI entry:
	- set `window_name` to the independent overlay container
	- use `diplomacy_target_context` plus `parent_window_token = selected_country_view_diplomacy` for diplomacy-tab-only target overlays
	- use `player_context` plus a politics parent for current-country overlays
	- set `ai_enabled = { always = no }` unless the GUI has actual AI actions
5. Gate both the scripted GUI and the icon by the same target-scoped trigger:
	- put the actor/state trigger in `visible = { ... }`
	- also add `<icon_name>_visible = { ... }` under `triggers`
	- if non-actor countries show the overlay, fix the context or trigger scope; do not solve it with coordinate changes or duplicated GUI files
6. Align coordinates in this order:
	- start from the vanilla portrait coordinate relative to the chosen parent token/window
	- if using a higher independent parent, add nested parent offsets manually
	- if the parent token already maps to a nested tab/body surface, do not add that surface's offset again
	- tune only the top-level overlay container `position` after live visual feedback; keep the child icon at `{ x = 0 y = 0 }` unless the source frame has a bad anchor
7. Record the final parent token/window, context type, trigger name, overlay origin, scale, vanilla reference file, portrait element, and any manual visual offset in `gfx_handoff.md`.

Parent-window rule:

- `parent_window_name = <independent_container>` is usually safer than anchoring to a nested child.
- A nested child may require `<child_name>_instance`, but this is not guaranteed to exist as a valid scripted GUI parent in the loaded UI.
- If the game logs `Parent window for <scripted_gui> is not found`, do not keep trying variants blindly. Re-parent to the nearest independent vanilla window and sum the nested offsets manually.
- Verify the parent by name against the exact vanilla `.gui` file, not a similarly named element from another window. For example, a `country_leader` element in an endgame dialog is not proof of a top-bar country leader surface.

Example pattern:

```txt
scripted_gui = {
	my_selected_country_leader_overlay_scripted_gui = {
		context_type = selected_country_context
		window_name = "my_selected_country_leader_overlay_container"
		parent_window_name = countrydiplomacyview

		visible = {
			my_actor_trigger = yes
		}

		ai_enabled = { always = no }
	}

	my_current_country_leader_overlay_scripted_gui = {
		context_type = player_context
		window_name = "my_current_country_leader_overlay_container"
		parent_window_name = countrypoliticsview

		visible = {
			my_actor_trigger = yes
		}

		ai_enabled = { always = no }
	}
}
```

The matching `.gui` containers should use the real vanilla portrait position for the chosen parent. If the target portrait is nested two containers deep, add those parent offsets to the portrait offset and record the calculation in `gfx_handoff.md`.

