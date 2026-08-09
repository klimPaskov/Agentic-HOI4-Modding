# Static category-picture alternative

This alternative is valid only when the formable's territorial proof is simple enough that a state-by-state display would add no useful information.

## Gate

Use this option only when every gate is true:

- The formable needs one installed state, or at most two adjacent states treated as one indivisible shape.
- There are no alternate groups, sponsor or member counting rules, or state-by-state actions.
- A per-state hover would add no information beyond the category description and decision tooltip.
- The picture can remain a static territorial overview and will never be presented as a clickable map.

If any gate is false, copy the full state-puzzle package instead.

## Owner record

Record the following in the owning plan or manifest before choosing the picture:

| Field | Required value |
| --- | --- |
| `formable_id` | `<FORMABLE_ID>` |
| `formation_decision_id` | `<FORMATION_DECISION_ID>` |
| `state_ids` | One state id, or the adjacent pair treated as one indivisible requirement |
| `installed_map_revision` | Revision and source hashes from the installed provinces map, definition file, and state history |
| `geometry_source` | Exact state mask assembled from installed province membership |
| `picture_sprite` | `GFX_<FORMABLE_ID>_category_picture` |
| `interaction` | Static picture only; no click region and no per-state hover |

The picture must still be derived from installed state geometry. Do not use generated art, a hand-drawn outline, a province blob, or a picture from another map revision.

## Category snippet

Copy this into the owner decision category after replacing the tokens and preserving the owner's route gates.

```text
<FORMABLE_ID>_formation_category = {
	priority = <CATEGORY_PRIORITY>
	icon = <CATEGORY_ICON>
	picture = GFX_<FORMABLE_ID>_category_picture
	visible_when_empty = no

	allowed = {
		<OWNER_TAG> = { always = yes }
	}

	visible = {
		<FORMABLE_ID>_route_revealed = yes
	}
}
```

The category description and formation decision must still explain the exact state requirement and call the owner's shared formation eligibility helper.

## Static sprite snippet

Register the one composite static picture in the owner `.gfx` file.

```text
spriteTypes = {
	spriteType = {
		name = "GFX_<FORMABLE_ID>_category_picture"
		texturefile = "<CATEGORY_PICTURE_PATH>"
	}
}
```

The picture should show the exact shape in the same projection used by the installed map. It is not a map control and must not contain an implied click target.

## Rejection conditions

Reject the static option if the owner later adds an alternate group, a live qualifying count, a subject or ally counting exception, a meaningful state hover, or any state-specific action. Re-evaluate the presentation choice when the requirement changes rather than stretching the picture into a pseudo-interface.
