---
name: hoi4-comfyui-portraits
description: Use when an optional HOI4 mod portrait pipeline is enabled and portraits must be sourced, produced, validated, archived, and wired without coupling source research to image production.
---

# HOI4 ComfyUI Portraits

This is an optional provider-aware portrait workflow for generic HOI4 mod
projects. The project owner chooses exactly one provider: `cloud`, `local`,
`runpod`, or `disabled`. `disabled` is a valid complete configuration; it
must remove this skill, provider skills, portrait subagent, provider config,
and ComfyUI-specific generated guidance from the target project.

## Ownership boundary

`hoi4_asset_source_researcher` owns real-person source discovery, attribution,
license evidence, crop bounds, and the durable source record. This skill and
`hoi4_portrait_creator` own provider execution, workflow selection, output
retrieval, validation, archive placement, DDS conversion, and the runtime
handoff. `hoi4_generated_feature_art` may provide a fictional source, but it
does not silently repaint or replace a grounded real subject.

Never let a provider invent a real person. A grounded subject uses the pinned
source or processing workflow. A fictional or source-free subject uses the
pinned text-to-image workflow. The provider never edits gameplay, character,
GFX, localisation, or country files.

## Persisted configuration

Store only non-secret configuration in `.codex/portrait_pipeline.toml` and the
installation lock:

- `enabled`: boolean
- `provider`: `cloud`, `local`, `runpod`, or `disabled`
- `provider_status`: `ready`, `needs_authorization`, `needs_subscription`,
  `needs_huggingface_access`, `needs_models`, `needs_workflow_install`,
  `unreachable`, or `temporarily_unavailable`
- `workflow_repository`, `workflow_branch`, and the exact 40-character
  `workflow_commit`
- `preferred_workflow`: `source`, `processing_only`, or `text_to_image`
- local loopback server/root or RunPod URL/workspace when relevant

API keys, OAuth tokens, and provider account data stay in the OS credential
store or provider-owned session. They never enter the project, lock, logs,
prompts, screenshots, or runtime output.

The current upstream lock is `docs/portrait_pipeline/upstream-lock.json`.
Resolve the branch to an exact commit before reading its manifest; use one
revision for the manifest and every selected graph. Never clone the complete
repository into a mod project.

## Current workflow contract

The canonical current graph ids are:

- `hoi4_portrait_flux2_klein_9b_source`: grounded identity-preserving source
  portrait; crop and RealESRGAN precede optional FLUX restoration and LoRA
  styling.
- `hoi4_portrait_processing_only`: grounded source preparation without LoRA
  styling.
- `hoi4_portrait_flux2_klein_9b_text_to_image`: fictional/source-free portrait.

Migrated job aliases `full_power` -> `source` and `esrgan_only` ->
`processing_only` may be accepted only at the boundary and must be normalized
before execution. Use the `.api.json` graph for Cloud/MCP/API submission and
the matching UI JSON for local/browser operation. Keep the project LoRA at
`0.7`, Euler, 8 steps, CFG 5, 832x1120 master, and 156x210 game output.

Prompts are one line, begin with `hoi4_portrait,`, describe only the person,
and omit names, titles, roles, background, scenery, style, camera, lighting,
pose, expression, gaze, and facing direction. Do not add a period-separated
second sentence. The exact final prompt is archived beside the source.

Background replacement is optional and happens only after the decoded final
LoRA image. Do not apply a generic repaint to a grounded source. If the
provider is unavailable, preserve the source and prompt, create the exact
head-and-shoulders crop and 156x210 fallback, convert it normally to DDS, mark
the portrait `pending`/`replacement_pending`, and report that art completion
is incomplete.

## Durable archive and runtime handoff

For every portrait candidate use:

`docs/assets/portraits/<event_id>_<event_slug>/`

The source PNG, provider master, game PNG, and prompt TXT use the exact runtime
basename. The prompt TXT contains only the final person-only prompt. The
runtime output must not reference an archive, temporary queue, provider URL,
or local source path. Record source provenance and provider state in a
manifest/handoff. Validate PNG dimensions, PNG decode, DDS conversion, sprite
name, and the final runtime path before the parent wires the portrait.

## Provider routing

Use the provider skill selected in the persisted config:

- Cloud: `hoi4-comfyui-cloud`, Comfy Cloud MCP at
  `https://cloud.comfy.org/mcp`, with provider-owned authorization and the
  exact upstream API graph.
- Local: `hoi4-comfyui-local`; discover configured/common roots and a running
  loopback server, inspect hardware before offering installation, then use the
  upstream installer/model/workflow scripts.
- RunPod: `hoi4-comfyui-runpod`; use the upstream repository and install script,
  preserve the current pod/workspace, and provide browser/computer-control
  guidance when interactive model import or workflow setup is required.
- Disabled: use source-based DDS fallback only; no ComfyUI wording or files
  may remain in generated project instructions, skills, subagents, reports,
  prompts, or readiness output.

Provider status is evidence, not a claim of completion. Authorization,
subscription, model, workflow, hardware, network, and temporary-unavailable
states remain visible and non-blocking for generic core setup.

## Completion gate

Before handoff check source/provenance separation, current upstream commit and
hashes, provider status, exact workflow mapping, prompt policy, source upload,
background order, both output dimensions, exact runtime basename, normal DDS,
fallback state, archive paths, no runtime references, no secret persistence,
and Disabled output cleanliness. A provider job or generated image alone is
not completion.
