# Motion sources and bounded repair QA

Read for standalone motion, retargeting, skeletal repair, material rebinding,
assembly yaw, or export QA. Apply the production guide's job, permissions,
source, dependency, credit, and parent-ownership gates first.

## Motion capability and attempts

Text-to-Motion can supply a suitable role within an accepted provider plan;
ordinary existing-model repair stays in Blender unless the user explicitly
requests provider motion. Existing accepted geometry, rig, and actions remain
protected. Firearm body rigs/actions stay on the declared Blender route;
separate firearm geometry tasks do not authorize provider-rig regeneration.

Verify actual live creation, status, task inventory, download, and animation
library tools through the external app-owned launcher. `meshy_client.py`
checks the optional names and argument exposure before use. Its client support
and `meshy_tool_contract.json` capability intent are not live-schema evidence.
The pinned launcher/runtime may not expose this capability: carry the exact
missing tool/schema and use authorized Blender recovery where applicable.
Never patch that runtime, create a project credential wrapper, or call REST
to bypass the launcher. Do not fabricate or copy a Chaos live-schema lock.

The [official motion contract](https://docs.meshy.ai/en/api/text-to-motion)
checked on 2026-09-13 permits nonblank prompts up to 400 characters, duration
2–10 seconds in 0.5-second steps, `prime` FBX or `swift` BVH. Current estimates
are 10/3 credits respectively; recheck pricing and live balance before each
paid tranche and record actual consumption. Download immediately within the
documented three-day retention window. A standalone clip needs no character
model or provider rig. Preserve task ID, prompt/mode/duration, format, original
bytes, SHA, and the upfront submission journal. An uncertain response requires
task-inventory/receipt recovery, not another paid submission.

The [animation contract](https://docs.meshy.ai/en/api/animation) requires
`rig_task_id` and exactly one preset `action_id` or generated `motion_task_id`.
An existing Blender rig supplies no provider task ID: prefer local retargeting
and do not create another provider rig merely to consume a clip. Inspect actual
returned formats; FBX-dependent post-processing cannot be assumed for a
generated-motion result. Use live-exposed [library discovery](https://docs.meshy.ai/en/api/animation-library)
for IDs/previews; a preset is not bespoke motion.

One selected motion-generation or preset-action attempt per missing role shares
the existing action allowance. Switching endpoints or regenerating an accepted
rig does not reset it. Failed/unusable motion or transfer goes to substantive
Blender authoring without paid retries. Polling/downloading the same recorded
task is continuation. Other providers/sources remain separately approval-gated.

## Transfer and phase proof

- Inspect hash-bound standalone FBX through `hoi4_blender_inspect_animation_source`
  for exact armature/action identity, hierarchy, FPS, and units. Use the bounded
  BVH route for BVH; source format and source receipt must agree.
- Use a sibling checkpoint, measured anatomical joint-head spans in world
  space, and source/target object/rest bases. Do not infer scale from short
  bone tails. Retain per-frame world-root translation and rotation proofs,
  preserve accepted actions, and reject unmapped constrained controls.
- Inspect complete semantics and ending, not only successful transfer. Death
  must collapse, impact, rebound/settle as intended, then retain its terminal
  support pose; attack must show applicable aim/discharge/recoil/recovery.
- Normalize equivalent quaternion signs and review half-frame interpolation
  for branch flips, snaps, floor excursions, and settled bodies rising again.
  Integer-frame poses and global minimum-Z alone do not prove support.
- Use explicit evaluated-frame inventories, focused previews, and anatomy/
  grip/stock/muzzle/support contact groups. Loops require first/quarter/middle/
  three-quarter/last proof and endpoint return. Sampling bounds is not visual
  proof of role completeness.

## Geometry, normals, materials, and publication

Diagnose neutral topology versus posed foldover and decoded exported corners
in a common coordinate space before changing normals. Keep the native default
0.25-degree guard. A reviewed job-specific tolerance up to 0.5 degrees requires
exact source/selection hashes, per-corner before/after and reopened-checkpoint
evidence, and final visual review. No broad normal reset or tolerance relaxation.

Batch skin/winding/corner-normal repairs remain explicit and bounded; vertex
remapping requires exact fan/corner correspondence and retained geometry, UV,
weights, and material proofs. Identity-leaf collapse is permitted only for the
declared constant identity channels and equivalent parent skin matrices, with
retained actions/geometry and all-frame/half-frame proof. It is not general rig
simplification. Assembly yaw rotates only the declared unprotected assembly
and proves skeletal deformation equivalence without baking accepted anatomy.

Packed specular alpha is engine glossiness, not opacity or raw roughness.
Resize each RGBA scalar independently; validate inversion/ranges/constants
after DDS round-trip. Preserve inspected existing-body atlases up to 2048 when
explicitly bounded; new components keep the calibrated default budget. A
corrected Blender importer preview is separate from runtime packed bytes.

After yaw, inspect actual reimported `.mesh`/`.anim` facing, initial root pose,
rest-bounds and contacts. `animation_root_export.py` aligns initial root t/q
with the samples' POSE-to-WORLD conversion, retaining child/sample fields and
serialized readback. Do not bake a rig or spend provider credits to hide this
export mismatch. When rebinding a newer adjacent texture set, explicitly use
`stage_default_textures=False` at reimport rather than overwriting it from old
source maps; inspect every retained DDS header and final material result.

Material/image reconciliation accepts only exactly owned partition clones or
proven discardable orphan consumers, never unexplained additions or missing
pixels. Keep source/checkpoint/runtime synchronization hashes where they prove
provenance or integrity; ordinary Markdown edits need no repetitive hash ledger.

Adapter publication must include the complete local import closure, unique
registered tools, operation-array agreement, matching release source hashes,
and Git-clean/raw-byte consistency for hash-locked text. Rebootstrap a target
installation after changing adapter sources; do not leave generated old locks
claiming the new implementation. Inspection/rendering stays read-only. Mutation
transport drains its matching response before stdin closes and never auto-replays
an uncertain call; inspect its saved request/checkpoint/report receipts first.
