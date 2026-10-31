---
name: hoi4-3d-model-pipeline
description: Create, rig, animate, convert, export, or repair custom Hearts of Iron IV 3D models and prepare their sourced sound and bespoke counter handoffs.
---

# HOI4 3D Model Pipeline

This skill owns bounded model-source production through Blender/PDX export and
evidence handoff. It does not own final gameplay, GFX/entity/sound wiring or the
overall in-game completion claim. Route portraits and other 2D art through their
dedicated skills; frame sheets use `hoi4-frame-animation`, not skeletal `.anim`.

## Required mode reading

Read [the production guide](references/production-guide.md) before job intake,
provider production, Blender processing/repair, custom-unit companion work,
export, or handoff. It is the full rule set: route selection, hard start gates,
credits and attempts, the job schema/layout, calibrated vanilla scale/material
rules, source rights, fail-closed checks, checkpoint and runtime-copy
discipline, audio/counter requirements, the registration audit and in-game
check, and completion boundaries. This file only points to it.

Read [source-reference policy](references/source-reference-policy.md) before
searching or approving a model input. Read [motion and repair QA](references/motion-and-repair-qa.md)
before standalone motion, retargeting, skeletal repair, material rebinding,
assembly yaw, or export acceptance. Read only the other system/asset references
needed for the actual consumer; do not start provider/runtime operations for a
workflow-documentation task.

## Gates in one glance

Each gate is defined once in the guide:

- **Route**: choose it before any provider call ([Route selection](references/production-guide.md#route-selection-and-component-completion)).
- **Key and dependencies**: provider work needs a nonblank `MESHY_API_KEY`
  first, then the reviewed dependency lock, live schemas, Blender bridge and
  pinned io_pdx_mesh export support ([Hard start gates](references/production-guide.md#hard-start-gates)).
- **Credits**: one `credit_budget` per job, approved by the user once at job
  start; no paid retries ([Credits and attempts](references/production-guide.md#credits-and-attempts)).
- **Reference image**: one approved image per geometry task, visually reviewed
  by the parent before any paid call ([Exactly one reference image](references/production-guide.md#exactly-one-reference-image-per-meshy-geometry-task)).
- **Checks**: gates fail closed and every role needs anatomical multi-phase
  motion with exported-byte reimport proof ([Geometry, materials, rigging, and actions](references/production-guide.md#geometry-materials-rigging-and-actions)).
- **Custom units**: defensibly sourced audio (including selection) and bespoke
  vanilla-green counters, or the package stays blocked ([counters](references/production-guide.md#custom-unit-counter-companion), [sound](references/production-guide.md#custom-unit-sound-design-companion)).

## Handoff

The worker hands off source/checkpoint/export lineage, task/credit records
(including the `--credits-report` output), meaningful QA, audio/counter status,
exact proposed runtime identifiers, and remaining work. The parent owns runtime
integration, a clean `GFX-3D-*` run of `.tools/audits/audit_asset_wiring_static.py`,
reviewed live-consumer evidence, and final completion
([Registration audit and in-game check](references/production-guide.md#registration-audit-and-in-game-check)).
Never launch HOI4 from the 3D worker.
