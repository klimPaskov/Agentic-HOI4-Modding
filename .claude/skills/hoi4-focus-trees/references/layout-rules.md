# Focus tree layout rules

This reference belongs to the `hoi4-focus-trees` skill and holds complete sections moved out of `SKILL.md` to keep it within the single-read ceiling. Every rule here is as binding as the rules in `SKILL.md`.

## 12. Layout rules

The tree must be readable in game. Layout quality is a completion requirement.

The layout must be compact, symmetrical, and honest about the route structure. Comparable sibling branches should mirror each other around their parent or use evenly balanced spacing. Route families should remain centered around the opening group or main trunk. Symmetry means balanced geometry and matching visual rhythm. It does not require identical focus counts, decorative filler, or empty nodes.

A focus tree must not fake non-linearity. A mechanically linear sequence should use a clean direct sequence. Do not offset focuses horizontally and reconnect them with long or awkward lines to make one chain appear branched. Visual splits, merges, and side lanes must represent real choices, route locks, convergence points, or mechanical interactions.

Every prerequisite connection must use the shortest clean practical path. Position the parent and child close enough that the connector remains direct and easy to follow. Before accepting a long line, a detour, a crossing, or a line through unrelated branch space, move the focuses or simplify the visible prerequisite structure. A distant connector is acceptable only when it represents a real convergence that cannot be placed closer without damaging the rest of the tree.

Do not build unnecessary ladders, staircase shapes, repeated zigzags, or decorative offsets. A complex-looking layout does not create depth. Route depth must come from real choices, mechanics, consequences, and branch interaction.

Focus boxes must never overlap. Connector lines must not overlap each other, intersect each other, pass through a focus box, or cross an unrelated branch. Hidden focuses and continuous focuses must also be included in the overlap review.

Use the MCP focus tools to find layout deformities before rewriting. `hoi4.focus_inspect` and `hoi4.focus_render` report overlapping focus boxes, excessive gaps, cramped spacing, connector crossings, path lines that run through focuses or stretch too far, dangling connectors, bad prerequisite presentation, unbalanced branches, off-center layouts, and related diagnostics. Review the artifacts, then call `hoi4.focus_rewrite` with `layoutMode: "compact"` for cleanup or a complete route plan for creation. Review the rewritten artifacts and source diff. MCP supplies shared parsing, layout, rendering, and writes. This skill owns design, prerequisites, localisation, AI, icons, balance, and completion.

Reward-only changes that deliberately preserve layout use inspect, render, and comparison evidence; they do not need an automatic layout rewrite. An invalid or empty identity-preserving rewrite request is a precise schema failure, not authority to invoke compact or automatic layout outside the requested scope. Inspect the actual schema and correct the request only within accepted scope. If the required identity-preserving operation is unavailable, report that blocker and stop writes. Capture an immutable before snapshot, preserve accepted non-layout edits, and roll back only proven tool-generated drift through normal `apply_patch`, recording rejected and restored evidence. Compare focus IDs, count, coordinates, and prerequisites, and distinguish `HEAD` from the dirty index before accepting the result.

Repeat inspect, render, rewrite, and render until the first-glance branch review passes. One clean render is not completion evidence.

Required layout checks:

- every supported major branch family is recognizable at normal zoom, with a visible root, meaningful fork, and payoff or convergence
- every focus has accurate search-filter tags and every spatially separate major branch family has a correct Focus Navigation shortcut
- any focus inlay window has a reserved footprint, correct visibility, readable state, and no obstruction of tree controls
- prerequisite parents are above children
- no duplicate coordinates
- no focus boxes overlap, including hidden and continuous focuses
- no connector lines overlap or intersect
- no connector runs through a focus box or an unrelated branch
- every prerequisite uses the shortest clean practical connector path
- no long connector remains when repositioning the parent, child, or branch can shorten it
- no unnecessary crossing lines
- no unnecessary ladder, staircase, zigzag, or decorative detour pattern
- no mechanically linear chain is offset to fake a non-linear branch
- comparable sibling branches use mirrored or evenly balanced horizontal spacing
- branch rows use a consistent vertical rhythm
- horizontal and vertical gaps are balanced and readable
- visible connectors agree with the scripted prerequisite structure
- route families remain balanced, symmetrical, and centered
- mutually exclusive branches are spaced comfortably and presented as a clear split
- branches are visually distinct without relying on awkward geometry
- continuous focuses are placed somewhere convenient without distorting the main tree
- hidden branches do not clutter ordinary routes
- large branches are not stacked in one vertical column
- the tree does not look like one long checklist
- branch endings are visually and mechanically clear
- side branches feed back into the main route, a mechanic, a decision family, or a real capstone
- the layout does not create random dangling focus chains with weak terminal rewards

If an `available = { has_completed_focus = ... }` condition gates a focus, decide whether it should also be a visible prerequisite. Do not add a visible prerequisite if it creates a crossing line, long detour, or asymmetric distortion. Move the branch, shorten the connection, or redesign the gate.
