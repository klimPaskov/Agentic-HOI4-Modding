# Reusable HOI4 3D model pipeline

This package provides the bounded source-to-handoff route for custom HOI4
models. It is dormant until a 3D task is accepted and the bootstrap is run.
Runtime caches, provider outputs, reports, job registries, and vendored
dependencies are generated on demand and are not starter files.

## Security and bootstrap gate

`MESHY_API_KEY` must be non-blank before repository or job discovery. If it is
missing, stop and set it with:

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
Planned paid operations are pre-authorized; failure-driven extra paid recovery
still requires explicit approval. Download each successful GLB immediately and
retain FBX when a rig or action route requires it.

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

Meshy receives exactly one approved image at
`refs/original/meshy_input.png`. Multi-view boards, turnaround sheets,
collages, and separate front/rear inputs are forbidden. Provider source files
remain immutable evidence, and all adapter payload paths are job-relative.

## Blender adapter contract

`adapter/hoi4_blender_mcp.py` exposes only `hoi4_blender_*` operations. The
bootstrap derives the generated operation allowlist directly from those
functions, so the module, client, config, and dependency evidence cannot drift
through separate hand-written lists. No tool accepts arbitrary Python, shell,
URL, or unrestricted absolute write paths.

The reusable operations cover candidate preparation, scene inspection,
texture processing, static transform baking and stream partitioning, mesh and
animation export, action import and retiming, bounded humanoid/creature rig
work, source-action cleanup, component review, weapon isolation, rigid weapon
checkpoint attachment, grounding, runtime sanitization, reimport proof, and
checkpointing.

Rigid weapon attachment copies one explicitly named weapon object from one
checkpoint into another, validates collision policy, optionally creates one
weapon bone, preserves existing bones/actions, parents the object rigidly, and
records transform and edge-length retention evidence. It does not author or
replace animation.

For required final actions, substantive motion must come from `meshy_animate`
or another explicitly approved professional source. Blender may import,
retarget, clean, correct contact/root placement, normalize scale, bake,
validate, and export it. Static aliases, shared-root transforms, and manually
keyed replacement motion are not accepted final actions.

## HOI4 validation rules

- Calibrate humanoids and buildings against the exact installed vanilla mesh
  and entity consumer. Apply entity scale exactly once.
- Repair or reject holes, loose components, non-manifold edges, degenerates,
  missing semantic components, invalid weights, and ungrounded actions.
- Preserve provider textures and derive PDX diffuse, packed specular, and
  normal maps deterministically. Raw roughness is not a PDX specular map.
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
