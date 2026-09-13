# Reusable HOI4 3D model pipeline

This package provides the bounded source-to-handoff route for custom HOI4
models. It is dormant until a 3D task is accepted and the bootstrap is run.
Runtime caches, provider outputs, reports, job registries, and vendored
dependencies are generated on demand and are not starter files.

## Security and bootstrap gate

Provider-dependent work requires a non-blank `MESHY_API_KEY` before provider
preparation, balance checks, or provider calls. An explicitly requested
existing non-firearm Blender-only repair may inspect its approved job, source,
dependency lock, adapter schema, bridge, and export stack without this key and
must not invoke Meshy. If provider work requires a missing key, stop and set it
with:

```powershell
[Environment]::SetEnvironmentVariable(
    "MESHY_API_KEY",
    "msy_your_actual_key_here",
    "User"
)
```

Restart the shell or Codex, then let HOI4 Mod Setup invoke:

```powershell
python .tools/3d_pipeline/bootstrap_3d_workflow.py `
  --project-root <repository-root> `
  --trusted-launcher <installed-hoi4-mod-setup-executable>
```

The bootstrap verifies the pinned Meshy MCP 0.4.0 package and complete runtime
tree, resolves Blender Lab MCP to an exact commit, discovers Blender, installs
and verifies io_pdx_mesh 0.91, enables the matching Blender MCP add-on, probes
the loopback bridge, materializes the bounded Blender adapter config, and
writes observed evidence to `config/dependencies.lock.json`.

Meshy credentials may flow only through the external app-owned launcher with
the single argument `--run-verified-meshy-mcp`. Project Python, project
wrappers, PATH Python, direct REST calls, and mutable `npx` routes are not
credential routes. `meshy_client.py` enforces this reviewed route.

## Meshy 7 contract and recovery

Meshy 7 is the only accepted generation model. Before paid work, require a
live `tools/list` response whose `meshy_image_to_3d` schema accepts
`ai_model = "meshy-7"`; compare it with both
`config/meshy_tool_contract.json` and `config/meshy_tool_schema.lock.json`.
Never alias `latest`, relabel an older result, or silently downgrade.

The checked-in package pins the official Meshy runtime bytes. Compatibility
patching, private runtime copying, certificate verification, immediate
pre-spawn rehashing, environment clearing, process-tree ownership, and stale
process cleanup belong to the installed HOI4 Mod Setup launcher. After any
recovery, run two consecutive schema probes plus a concurrent probe pair, then
one live balance probe through the same app-owned route. A schema mismatch or
surviving exact-route process blocks paid work.

The verified tool family is `meshy_check_balance`, `meshy_image_to_3d`,
`meshy_get_task_status`, `meshy_download_model`, `meshy_remesh`, `meshy_rig`,
`meshy_convert`, and `meshy_animate`. Use only live-listed tools and arguments.
Planned generation, remesh/retexture, conversion, one supported rig attempt,
one supported animation attempt per missing role, and bounded geometry recovery
are pre-authorized while live balance and verified provider capability permit
them. Do not submit paid rig or animation retries: preserve passing results and
switch failed, unusable, or unsupported stages to Blender. Download each
successful GLB immediately and retain FBX when a rig or action route requires
it.

## Route selection

- Firearm-bearing units use a fresh weapon-free Meshy 7 body and a separate
  Meshy 7 geometry task for each required firearm. Blender owns body rigging,
  weights, substantive actions, weapon fitting/attachment, rigid controls,
  locators, contacts, and other props. This route skips Meshy rig/animation.
- Existing non-firearm repairs proceed directly in Blender.
- Other new animated models receive one supported Meshy rig attempt and one
  action attempt per missing role, then Blender recovery without paid retries.

Complete every required anatomy element, equipment piece, held object, rig
element, and action through the verified adapter. Static, transform-only,
whole-rig-only, or semantically aliased motion is not acceptable completion.

Every project-side stdio call records an exact process-ownership receipt. The
receipt includes the launcher PID, Windows Job Object process IDs, and any
surviving owned PIDs after cleanup; a survivor is a hard failure. Provider
artifact repair and persistence remain app-launcher responsibilities. The
project runner only accepts completed downloads after atomic `.partial`
replacement and checksum recording.

## Job intake and layout

Job registries are feature-owned inputs and are never checked into this starter
directory. Pass an explicit repository-owned registry when initializing or
running jobs:

```powershell
python .tools/3d_pipeline/init_pilot_jobs.py --jobs-config docs/plans/<feature>/3d_jobs.json --all
python .tools/3d_pipeline/run_pilot.py --jobs-config docs/plans/<feature>/3d_jobs.json <asset_slug>
python .tools/3d_pipeline/run_pilot.py --jobs-config docs/plans/<feature>/3d_jobs.json --shared-humanoid-batch <batch_id>
```

The registry contains a non-empty `jobs` mapping. Each job resolves to:

```text
docs/assets/<owner_id>/models_3d/<asset_slug>/
  job.yaml
  manifest.md
  history.jsonl
  refs/{original,derived,briefs}/
  provider/{requests,responses,tasks,credits,downloads,rejected}/
  blender/{source,reference,working,checkpoints,previews,reports}/
  textures/{source,processed,dds}/
  export/{mesh,anim}/
  validation/
  evidence/
  logs/
  runtime/{handoff.md,crosswalk.md}
```

Each Meshy geometry task receives exactly one approved image: the body at
`refs/original/meshy_input.png`, each firearm at
`refs/firearms/<firearm_id>/meshy_input.png`. Multi-view boards, turnaround sheets,
collages, and separate front/rear inputs are forbidden. Provider source files
remain immutable evidence, and all adapter payload paths are job-relative.

## Optional motion and latest repair tools

The client supports Text-to-Motion creation/status/inventory/download,
animation-library discovery, and exclusive preset/generated-motion retarget
inputs. These require actual live schema exposure through the app-owned
launcher. The checked-in pinned runtime and inherited schema lock do not prove
that exposure. No project wrapper/runtime patch or direct REST fallback was
introduced. See the skill's `references/motion-and-repair-qa.md` for source,
attempt, credit, format, measured-root, phase, and interpolation gates.

The adapter adds hash-bound standalone FBX inspection, explicit batch
skin/winding/corner-normal repair, exact vertex remap, rigid assembly yaw,
identity-leaf equivalence repair, and initial animation-root export correction.
Existing-body atlas rebinding can preserve an inspected budget up to 2048;
new components retain their calibrated default. All operations stay job-bounded
and source guarded. Rebootstrap generated target installation locks after
updating adapter sources; old deployment locks must not advertise new code.

Blender transport initializes and drains the matching response before closing
stdin. Mutation calls are not automatically replayed after uncertain transport;
inspect saved request/checkpoint/report receipts before continuing. Read-only
inspection retries remain separate.

## Blender adapter contract

`adapter/hoi4_blender_mcp.py` exposes only `hoi4_blender_*` operations. The
bootstrap derives the generated operation allowlist directly from those
functions, so the module, client, config, and dependency evidence cannot drift
through separate hand-written lists. No tool accepts arbitrary Python, shell,
URL, or unrestricted absolute write paths.

The reusable operations cover dual-source candidate preparation; action-channel,
mesh-region, component, landmark, winding, and material-visibility inspection;
texture processing; explicit skin, vertex, material, mesh-patch, and winding
repair; fitted humanoid and measured-creature rigs/actions; rigid components
and locators; action-phase patching and grounding; static and skeletal material
stream partitioning; accepted-reimport promotion; mesh/animation export;
verified FBX and native BVH import; retiming; guarded export-coordinate
checkpointing; configurable weight transfer/sanitation; runtime sanitization;
reimport proof; and checkpointing.

Rigid weapon attachment copies one explicitly named weapon object from one
checkpoint into another, validates collision policy, optionally creates one
weapon bone, preserves existing bones/actions, parents the object rigidly, and
records transform and edge-length retention evidence. It does not author or
replace animation.

The route may preserve and process a passing `meshy_animate` or approved
professional-source action, or author the required substantive skeletal action
in Blender under the route-selection policy. Blender-authored work must retain
editable bones, weights, keys, phase intent, and deformation/contact evidence.
Static aliases, shared-root transforms, and semantic role reuse are invalid.

Animation import is fail-closed. Its repository-owned provenance receipt must
name a verified source kind, reference ID, source file checksum, exact source
action, exact source armature when supplied, and exact target armature. Action
names may include balanced parenthetical qualifiers and are matched exactly.
Retargeted location channels use `source_world_scale / target_world_scale`;
rest-data ratios are audit evidence, not the coordinate conversion.

Native BVH import additionally verifies the BVH header, filename/action
identity, explicit bone-chain map, axis and scale settings, frame-rate
conversion, root-motion policy, and the saved/reopened curve signature. Before
PDX animation export, the export-coordinate checkpoint fails closed on
protected source/reference changes, topology or material binding drift,
armature/bone drift, action drift, or missing approved provenance.

Preparation persists normalization through a saved-checkpoint reopen. It
verifies applied scale, axes, origin, grounding, and expected dimensions from
the saved file. When a geometry source is available, bounded convergence may
correct a persisted mismatch, but stalls, divergence, sign changes, invalid
measurements, and correction-cap exhaustion all fail closed. Shared humanoid
continuation requires verified receipts for idle, move, attack, and death.
Missing or failed roles follow the bounded Blender recovery policy and never
become static or semantically aliased locomotion.

Dual-source preparation resets the accepted target rig to an action-free base,
requires one explicitly selected geometry mesh, and records the exact source
mesh set. Weight transfer may use four-nearest, bone-distance, automatic, or
nearest-face barycentric modes; sanitation enforces an explicit one-to-four
influence cap. Grounding may exclude vertices dominated by named non-contact
bones so tails, weapons, and similar appendages do not define the floor.

## HOI4 validation rules

- Calibrate humanoids and buildings against the exact installed vanilla mesh
  and entity consumer. Apply entity scale exactly once.
- Repair or reject holes, loose components, non-manifold edges, degenerates,
  missing semantic components, invalid weights, and ungrounded actions.
- Preserve provider textures and derive PDX diffuse, packed specular, and
  normal maps deterministically. For `PdxMeshAdvanced`, packed specular alpha
  is glossiness (`255 - roughness`), not raw roughness.
- Use the selected installed shader. Static map-building precedent currently
  uses `PdxMeshAdvancedSnow` and a 4.0 m runtime X/Y ceiling.
- Export only through the locked io_pdx_mesh route, then reimport or parse the
  actual `.mesh` and every `.anim` and retain byte-level evidence.
- Sample loop actions at start, quarter, midpoint, three-quarter, and end.
- Select source exports before runtime synchronization and record source and
  destination hashes. Runtime wiring remains parent-owned.

## Focused validation

The source-only checks do not require provider spend:

```powershell
python -m compileall -q .tools/3d_pipeline
python -m unittest discover -s .tools/3d_pipeline/tests -p "test_*.py"
python .tools/3d_pipeline/verify_environment.py
```

Add `--probe-meshy` only after bootstrap when a live authenticated schema and
balance probe is intended. Run the Blender integration script through the
lock-selected Blender executable; it creates only temporary `.blend` files.

The model worker owns sources, checkpoints, textures, exports, validation,
provenance, sound-source research, and handoff evidence. The parent owns
`.asset`, entity, `.gfx`, sound definitions, gameplay wiring, active runtime
copies, live consumers, and in-game proof.
