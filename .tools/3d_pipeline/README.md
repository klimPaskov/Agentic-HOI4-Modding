# Reusable HOI4 3D model pipeline

This package provides the bounded source-to-handoff route for custom HOI4
models. It is dormant until a 3D task is accepted and the bootstrap is run.
Runtime caches, provider outputs, reports, job registries, and vendored
dependencies are generated on demand and are not starter files.

## Security and bootstrap gate

Provider-dependent work requires a non-blank `MESHY_API_KEY` before provider
preparation, balance checks, or provider calls; the exact command that sets it
is in the [3D agent's hard start gate](../../.claude/agents/hoi4-3d-model-pipeline.md).
The account must be on a paid Meshy plan: on the free plan every task create
returns HTTP 402 and charges nothing, so the free monthly credits shown by the
balance cannot be spent through the API.
An explicitly requested existing non-firearm Blender-only repair may inspect its
approved job, source, dependency lock, adapter schema, bridge, and export stack
without this key and must not invoke Meshy. Restart the shell or the agent
runtime after setting the key, then let HOI4 Mod Setup invoke:

```powershell
python .tools/3d_pipeline/bootstrap_3d_workflow.py `
  --project-root <repository-root> `
  --trusted-launcher <installed-hoi4-mod-setup-executable>
```

The bootstrap verifies the pinned Meshy MCP 0.6.7 package (npm integrity
`sha512-kmOyjdcW+FZuc+TZHK4aUjfOID+LbjmQAM7W9YLtLhApW7b7lo+aZLnLl6xnNfM2KvktODXCF61kgDhjwP7dUg==`,
upstream head `0f4c10a3c37f74a2625a922aeaff03b2f878887f`) and its complete
3,954-file runtime tree (SHA-256 `dbd2ebfce197a18875c3d367ad4b5325a345b92ce54c2a33440f5490efe7f6b3`),
installs Blender Lab MCP at source commit `dbbf836ad4b1025f14a2b3b504c43903f39e0b04`, discovers Blender, installs
and verifies io_pdx_mesh 0.91, enables the matching Blender MCP add-on, probes
the loopback bridge, materializes the bounded Blender adapter config, and
writes observed evidence to `config/dependencies.lock.json`. The rewrite keeps
the lock's pinned `sources` and `compatibility` evidence, so the bootstrap can
be rerun on its own output. The adapter requires the `mcp` 1.x SDK; its
`FastMCP` server API does not exist in `mcp` 2.x.

Blender is pinned to the minors in the lock's `compatibility.blender.supported_minors`
(5.1 and 5.2). The bootstrap selects the highest supported minor and refuses any
other, including a `BLENDER_EXE` that names an unsupported build. Every supported
minor installs the same deterministic io_pdx_mesh compatibility archive, derived
from the checksum-locked upstream 0.91 bytes. The derived archive fixes the
removed Python `imp` imports, guards the removed `Material.shadow_method`, and
uses `bpy.context.temp_override` for object joining. The bootstrap verifies the
derived archive digest and each installed patched file on every minor; it
preserves the upstream archive unchanged. A Blender 5.1 `io_pdx_mesh` whose
patched files do not match the lock is replaced.

Credential routes, the one REST exception (the bootstrap's own bounded balance
request that verifies the key) and the rest of the start gates are in the
[production guide](../../.claude/skills/hoi4-3d-model-pipeline/references/production-guide.md#hard-start-gates).
`meshy_client.py` enforces the reviewed route.

## Generation model, credits and recovery

The generation model is the profile's `generation.ai_model` in
`config/asset_profiles.json` (currently Meshy 7 for every profile); a job may
restate it but never change it. Before paid work, require a live `tools/list`
response whose `meshy_image_to_3d` schema accepts that identifier and compare
it with both `config/meshy_tool_contract.json` and
`config/meshy_tool_schema.lock.json`. The pinned schema was captured from the
published runtime's `tools/list` without authenticated provider calls. Upstream
marks `meshy-7` deprecated in favor of `meshy-7.1`; the profile keeps its model
until a maintainer changes it. Retired models (`meshy-t1`, `meshy-5`, `meshy-4`,
`meshy-3`), the `lowpoly` model type and the alias `latest` are refused before
any paid call.

Paid work is gated by the job's `credit_budget`, not by a standing
pre-authorization. Prices come from `config/meshy_pricing.json`. Each paid
create checks the remaining budget and the live balance, counts attempts from
`provider/credits/ledger.jsonl` against the contract limits, and reuses an
earlier result before paying (`lib/credits.py`, `lib/reuse.py`). Print the
totals with:

```powershell
python .tools/3d_pipeline/run_pilot.py --credits-report [<job-folder-or-root>]
```

The rules for budgets, attempts, reuse and the ledger are in the
[production guide](../../.claude/skills/hoi4-3d-model-pipeline/references/production-guide.md#credits-and-attempts).

The checked-in package pins the official Meshy runtime bytes. Compatibility
patching, private runtime copying, certificate verification, immediate
pre-spawn rehashing, environment clearing, process-tree ownership, and stale
process cleanup belong to the installed HOI4 Mod Setup launcher. After any
recovery, run two consecutive schema probes plus a concurrent probe pair, then
one live balance probe through the same app-owned route. A schema mismatch or
surviving exact-route process blocks paid work.

The verified tool family is in `config/meshy_tool_contract.json` (required
tools and the optional Text-to-Motion tools). Use only live-listed tools and
arguments. `meshy_image_to_3d` never gets `multi_view_thumbnails`, and
`meshy_rig` never gets `texture_image_url`. Download each successful GLB
immediately and retain FBX when a rig or action route requires it. The route
each kind of asset takes (firearm units, existing repairs, bipeds, non-bipedal
anatomy) is defined once, in the guide's
[Route selection](../../.claude/skills/hoi4-3d-model-pipeline/references/production-guide.md#route-selection-and-component-completion).

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
python .tools/3d_pipeline/init_pilot_jobs.py --jobs-config docs/plans/<feature>/3d_jobs.json --record-visual-review <asset_slug> --reviewer <name> --review-file <answers.json>
```

The registry contains a non-empty `jobs` mapping, and each paid job needs a
whole-number `credit_budget`. `run_pilot.py` refuses a paid job without one, and
refuses a job whose reference image has not passed the recorded visual review
(see the guide's
[Exactly one reference image](../../.claude/skills/hoi4-3d-model-pipeline/references/production-guide.md#exactly-one-reference-image-per-meshy-geometry-task)).
Each job resolves to:

```text
docs/assets/<owner_id>/models_3d/<asset_slug>/
  job.yaml
  manifest.md
  history.jsonl
  refs/{original,derived,briefs}/
  provider/{requests,responses,tasks,submissions,credits,downloads,rejected}/
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

The client supports Text-to-Motion (`meshy_text_to_motion`, with the generic
`meshy_get_task_status`, `meshy_list_tasks` and `meshy_download_model`),
animation-library discovery (`meshy_list_animations`), and exclusive
preset/generated-motion retarget inputs. These require actual live schema
exposure through the app-owned launcher; the attempt limit is the contract's
`max_text_to_motion_attempts`. No project wrapper/runtime patch or direct REST
fallback was introduced. See the skill's `references/motion-and-repair-qa.md` for source,
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
  missing semantic components, invalid weights, and ungrounded actions. The
  gates fail closed: `candidate_gate` blocks on a missing measurement, the
  texture cap is read from the PNG header, and an uncaptured io_pdx_mesh
  export report is refused. Limits and per-profile `exceptions` are in
  `config/asset_profiles.json` (see the guide's Fail-closed gates). The
  topology checks count position-welded geometry, so UV seams are not holes or
  loose parts, and each profile's `validation_calibration` records the
  measurements behind its limits.
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

Once the bootstrap has materialized `config/blender_hoi4_adapter.json`, the
verifier starts the adapter through `wrappers/run_blender_hoi4_adapter.cmd`,
completes MCP `initialize` and `tools/list`, and blocks unless the served tools
match the adapter source. Without that config it reports the adapter as
`not_materialized`; add `--probe-adapter` to make that a failure. The probe
makes no provider calls. Add `--probe-meshy` only after bootstrap when a live
authenticated schema and balance probe is intended. Run the Blender integration script through the
lock-selected Blender executable; it creates only temporary `.blend` files.

The model worker owns sources, checkpoints, textures, exports, validation,
provenance, sound-source research, and handoff evidence. The parent owns
`.asset`, entity, `.gfx`, sound definitions, gameplay wiring, active runtime
copies, live consumers, and in-game proof.
