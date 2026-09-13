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
export, or handoff. It preserves the full job schema/layout, calibrated vanilla
scale/material rules, source rights, credit/recovery limits, checkpoint and
runtime-copy discipline, audio/counter requirements, and completion boundaries.

Read [source-reference policy](references/source-reference-policy.md) before
searching or approving a model input. Read [motion and repair QA](references/motion-and-repair-qa.md)
before standalone motion, retargeting, skeletal repair, material rebinding,
assembly yaw, or export acceptance. Read only the other system/asset references
needed for the actual consumer; do not start provider/runtime operations for a
workflow-documentation task.

## Route and authority

- Firearm units, including firearm rebuilds, use a fresh weapon-free Meshy 7
  body plus a separate Meshy 7 geometry task for each required gun. Each task
  gets one approved body-only/firearm-only image and independent lineage.
  Blender owns rigs, weights, substantive actions, weapon fitting/attachment,
  rigid controls, locators, contacts, and missing-component completion.
- Existing non-firearm repairs use Blender directly. They need no Meshy key
  unless explicit provider work is added. A standalone motion request does not
  authorize replacing accepted geometry, rigs, or actions.
- Other new animated models receive one supported rig attempt and one selected
  provider motion/preset attempt per missing role, then substantive Blender
  recovery while preserving passing outputs. No paid rig/action retries or
  attempt-reset through endpoint/rig changes.

Required Blender completion and bounded planned provider/geometry work are
preauthorized within the accepted brief and limits. Other source/provider
substitution, omitted requirements, identity change, or source-free references
remain separately approval-gated. Record actual approval basis, not file dates
or old spec/status labels.

## Critical gates

For provider-dependent work, check a nonblank process `MESHY_API_KEY` first
and follow the guide's exact missing-key instruction. Never record credentials.
Require the reviewed dependency lock, live schemas, Blender bridge, and pinned
io_pdx_mesh export support. Meshy credentials flow only through the external
app-owned launcher with `--run-verified-meshy-mcp`; never through project
wrappers, mutable runtime patches, direct REST, or PATH Python.

Use only actual live-listed capabilities. Optional Text-to-Motion client and
contract support do not prove launcher exposure. Missing capability is an exact
blocker; use authorized Blender recovery where applicable. Rebootstrap stale
adapter deployments and verify the complete local source closure.

Every role needs anatomical multi-phase motion, contact/deformation proof,
correct units/root basis, interpolation review, and actual exported-byte
reimport/parse evidence. Static, whole-rig-only, transform-only or semantic
aliases cannot pass. Inspect source normals and engine material packing rather
than trusting a plausible viewport.

Custom units require defensibly sourced/licensed audio (including actual
selection-consumer scope) and bespoke counters based on inspected installed
vanilla definitions/DDS and sampled green palette. Missing source/capability
remains blocked; generated audio or reused placeholder counters cannot pass.

The worker hands off source/checkpoint/export lineage, task/credit records,
meaningful QA, audio/counter status, exact proposed runtime identifiers, and
remaining work. The parent owns runtime integration, reviewed live-consumer
evidence, and final completion. Never launch HOI4 from the 3D worker.
