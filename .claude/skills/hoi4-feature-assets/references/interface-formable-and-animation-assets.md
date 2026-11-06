# HOI4 Feature Assets: Interface, formable and animation assets

Part of the [hoi4-feature-assets](../SKILL.md) skill. Read before planning or making UI panels, scripted GUI art, progression-state variants, formable nation assets or animated sprites.

## Asset depth from improvement addenda

When an improvement addendum asks for richer presentation, the asset handoff should name the visual states instead of asking for generic polish. A good asset request says what the player sees before activation, while active, when locked, when dangerous, when complete, and when the route has failed.

For scripted GUI, plan asset families. A panel usually needs a background, header, button states, value icons, warning indicators, progress frames, locked overlays, selected overlays, hover states, and any animated glow, particle, float, or pulse layers. The main agent owns `.gui` and `.gfx` wiring, but the asset package must provide clear sprite names, sizes, frame counts, static fallbacks, and contact sheets.

Use [hoi4-scripted-gui](../../hoi4-scripted-gui/SKILL.md) for the accepted reference-to-native mapping, background-region contract, iterative MCP live previews, click-region inspection, state and resolution coverage, and final visual acceptance. Asset production alone does not prove a GUI layout complete.

## 22. UI panels and custom windows

For UI panels, investigation windows, ledgers, and similar assets, separate artwork from functional UI.

Use `hoi4.image_interface` (family `gui_texture` or `super_event`, with the canvas the mod defines) for illustrated background panels, thematic decorations, symbolic seals, propaganda visuals and report board elements.
Use normal UI editing for exact layout slicing, cropping, button states, state variants, meter fills and final export preparation.
Do not let generated art decide exact interactive layout; the implementation still follows HOI4 UI rules and existing repo patterns.
Before a multi-window interface pass, use the assembled-screen mockup that `hoi4-scripted-gui` requires as the shared target for every window's art.

## Decision category and scripted GUI visual packs

For a decision category with a scripted GUI or mechanic window, the asset handoff should cover the full interface state set.

When the asset package belongs to a focus-tree or scripted-GUI change, the corresponding MCP inspect and render evidence is mandatory before and after placement. For technology or doctrine icons, mandatory evidence uses `hoi4.tech_inspect` in `explain` or `lint` mode to verify sprite and texture references, then the `assets` or affected folder view in `hoi4.tech_render`, followed by `hoi4.tech_inspect` with `mode: "compare"` after source edits. If a required route is unavailable, record the exact blocker and leave the linked asset surface unresolved; source-only review is not equivalent. This skill still owns source art, processing, DDS conversion, placement, manifests, and `.gfx`/`.gui` handoff.

Useful assets include the category icon and header plate, background panel, tab buttons, normal, hover, selected, locked, disabled and warning button states, progress bars and fill variants, meter frames, target cards, status seals, warning overlays, animated glow, particle and float overlays (each with a static fallback), the tooltip icon set, close and open buttons, and a mechanic-specific leader, council or envoy portrait.

The asset prompt should state which sprites are decorative and which represent mechanic state. State-driven sprites need clear names that match the mechanic value or route state.

## 23. Progression-state variants

Progression-state variants may include:

- selected
- dim
- active
- inactive
- locked
- completed
- rejected
- damaged
- corrupted
- urgent
- meter-fill
- bar-fill

Progression-state variants should use the same target size as the base asset.

## Formable state-puzzle visual assets

When a formable uses the reusable state-puzzle presentation from `hoi4-decisions-missions`, preserve exact state geometry and one shared geographic projection.

Each package must include a manifest with formable id, state ids and names, alternate requirement groups, counting rules, source map data, projection bounds, anchors, and proposed sprite names; one exact mask or sprite region per required state; grey unmet and green qualifying states with a second non-colour cue; a composed geographic preview; hover-region notes; and final runtime, `.gfx`, and GUI ownership.

Derive shapes from the installed map's state and province geometry. Do not trace screenshots by hand, generate borders with the image generator, simplify the pieces into generic tiles, or substitute a modern political map. Keep one projection, scale, origin, edge treatment, and border width so neighbouring states meet cleanly.

Copy and adapt `.claude/skills/hoi4-decisions-missions/templates/formable_state_puzzle/`. The asset handoff must match its manifest and naming rules. Skill-local templates are reference scaffolding and must never become runtime consumers. The static category-picture alternative also requires the simple-category eligibility gate and cannot accompany the interactive puzzle.

## Formable nation asset coverage

Every formable nation needs visible identity assets.

Asset planning should cover:

- formable flag in normal, medium, and small sizes
- ideology variants where relevant
- cosmetic-tag flags where relevant
- leader portrait or council portrait
- animated leader portrait when the formable is a rare dramatic route
- focus icons for the formation route
- decision icon for the formation decision
- decision category or scripted GUI assets if formation progress is managed visually
- news, report, or custom feature image if the formation is globally important
- faction emblem if the formable creates a league, empire, federation, bloc, mandate, compact, or coalition
- achievement icon if the formable has achievement hooks

Historical or culturally attested formable symbols need source review. Fictional, alternate-history, supernatural, and extreme-route variants may use generated art with clear manifest notes.


## Animated sprites, scripted GUI assets, and animated portraits

Use `hoi4-frame-animation` for every final animated visual asset. Some mod mechanics should have animated visual layers when motion improves readability, atmosphere, or feedback. Examples include floating seals, glowing route emblems, particle drift, meter pulses, warning frames, active-button glows, occult pressure effects, sponsor influence networks, and final formable proclamations.

Animated leader portraits should be handled as major identity assets by
`hoi4_portrait_creator` plus `hoi4-frame-animation`. The portrait worker owns sourced real base images and image-generator fictional or impossible base portraits. The asset handoff must say whether the animation is subtle,
such as breathing light or smoke, or symbolic, such as eye glow, map shadow,
glitch, or spectral overlay. The portrait should still read clearly at in-game
size.

Final animated assets must be built from planned source frames. Do not create final animation by taking one still image and shifting, scaling, rotating, warping, blurring, recoloring, brightening, or pulsing it with a script. Local scripts may normalize, align, crop, resize, assemble sheets, create previews, and convert frames after the real frames exist.

