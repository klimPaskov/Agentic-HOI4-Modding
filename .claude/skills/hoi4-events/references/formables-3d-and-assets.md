# HOI4 Events: Formables, 3D models and generated assets

Part of the [hoi4-events](../SKILL.md) skill. Read before an event creates formable routes, a 3D unit or building, or generated visual assets.

## Formable nations as event surfaces

When an event can create or empower countries, consider whether it should create formable nation routes. A formable can be a major event payoff, a late-game ambition, a hidden branch, a rare escalation variant reward, a country package route, or a post-crisis consolidation goal.

Event implementation must keep formables aligned across:

- event flags and route flags
- decision category visibility
- focus unlocks
- scripted triggers for state control
- scripted effects for formation
- cosmetic tags and country names
- flags and portraits
- AI strategy
- achievements
- researched text or audio packages where the formation changes world order
- cleanup after tag switch, annexation, puppet transfer, civil war, or route failure

Use scripted helpers for formation effects. Do not duplicate formation logic in events, decisions, focuses, scripted GUI buttons, and achievements. The decision can pay the cost and validate requirements, while a shared helper performs the identity change and logs the result.

Hidden formables should still have implementation coverage. They need reveal events, hidden flags, visibility triggers, localisation, assets, AI rules, and cleanup.

When exact state control is the formation proof, use the manifest-driven state-puzzle workflow under `.claude/skills/hoi4-decisions-missions/templates/formable_state_puzzle/`. Keep generated state pieces, the shared territory helper, formation decision, AI path, and every in-scope decision category synchronized. Complete `category_attachment_audit.md`; under a strict family policy every category metadata block must attach the generated `context_type = decision_category` scripted GUI. A category picture or text-only description does not replace that attachment.


## 3D model and entity integration

When an event creates or changes a 3D unit or building, treat the model as a runtime contract across the event, unit or building definition, entity, `.asset`, `.gfx`, materials, textures, actions, and live map consumer.

The event implementation must use the `hoi4-3d-model-pipeline` handoff instead of trying to produce geometry or animations inside event work. The model handoff must include the exact runtime identifiers, processed texture paths, `.mesh`/`.anim` paths, action names, scale crosswalk, provider and Blender evidence, reimport proof, and final hashes.

For a spawned unit, validate that `create_unit` is executed in a country or other supported scope, that the unit template and sub-unit are registered, that every emitted `unit_<id>_icon_small` text icon exists when required, and that movement uses a real exported action rather than a static substitute.

For a building or map entity, validate that the building has an entity, the entity key resolves in the `.gfx`/`.asset` chain, the province belongs to the specified state, the building command has the correct argument count, and the test province is visible at the intended zoom without an existing building hiding it.

The main event agent owns the gameplay and runtime source wiring, final runtime copy synchronization, province/state placement, live consumer, and in-game evidence. The 3D worker owns the bounded model package and must not claim event or in-game completion.

## Generated asset handling

Use the `hoi4-feature-assets` skill whenever an event task requires generated or processed visual assets.

For every generated asset:

1. Create the base artwork by following the image generator's workflow through `hoi4-feature-assets`.
2. Save the original generated image as a source PNG.
3. Create a processed PNG preview at the correct HOI4 target size.
4. Convert the processed PNG to DDS 32 bit unsigned BGRB 8.8.8.8.
5. Move the DDS into the correct mod asset folder.
6. Add or update the matching sprite definition in the correct `.gfx` file.
7. Update localisation, docs, and any explicitly scoped external records that reference the asset.
8. Record the asset in a markdown manifest.

The asset manifest must include:

- asset name
- asset type
- source PNG path
- processed PNG path
- final DDS path
- target size
- sprite name
- intended in-game use
- related event id when the asset is tied to a real HOI4 event
- related feature slug
- notes

Do not leave generated assets only in a temporary folder. If the event uses them, wire them into the mod.


