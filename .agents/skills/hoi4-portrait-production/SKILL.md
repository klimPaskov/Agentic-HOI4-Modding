---
name: hoi4-portrait-production
description: Use for the provider-neutral HOI4 portrait source, prompt, archive, validation, and runtime handoff contract.
---

# HOI4 portrait production contract

This skill contains only the provider-neutral portrait contract. Read the
provider skill named by `provider_skill` in `.codex/portrait_pipeline.toml`
after reading this file. Do not search for or use another provider skill.

## Ownership boundary

`hoi4_asset_source_researcher` owns real-person source discovery, attribution,
license evidence, crop bounds, and the durable source record. The selected
provider skill and `hoi4_portrait_creator` own production-specific work,
output retrieval, validation, archive placement, DDS conversion, and the
runtime handoff. The provider never edits gameplay, character, GFX,
localisation, or country files.

Portrait generation is user-owned by default. The agent prepares and validates the locked job, source placeholder, prompt, and exact manual or API handoff; the user runs the selected provider workflow and supplies the final outputs. The agent must not queue or generate a portrait unless the user explicitly changes that boundary for the current task. Browser or computer control is opt-in for the current user-run job and must never silently queue generation.

Never invent a real person. A grounded subject uses the approved source and
the pinned source or processing workflow. A fictional, impossible, or
otherwise non-sourced subject uses native ImageGen under the parent brief and
never enters this portrait workflow.

## Source and prompt gate

Before production, require an attributed source, immutable source hash, exact
crop evidence, durable source storage, runtime basename, and a person-only
prompt. The prompt begins with `hoi4_portrait,` and describes only the visible
person: age, gender presentation, face shape, hair, facial hair, expression,
gaze, head direction, visible clothing or uniform, medals, accessories, and
framing. Omit the subject's name, background, lighting, rendering/style,
restoration, game instructions, and unsupported biography. Do not add a
second sentence.

## Durable archive and output

For every candidate use:

`docs/assets/portraits/<event_id>_<event_slug>/`

The source PNG and prompt TXT use the exact runtime basename. Keep the source
immutable and retain provenance beside it. A final package contains the
provider master, game-size PNG, DDS, hashes, review evidence, and handoff.
Runtime files never reference the archive, a queue, a provider URL, or a
temporary source path.

The expected dimensions are `832x1120` for the master and `156x210` for the
game output. Validate PNG decoding, dimensions, identity/framing review, DDS
conversion, sprite name, and final runtime path before the parent wires the
portrait.

If production is unavailable for a grounded source, preserve the source and
prompt, create only the deterministic source-based `156x210` fallback, mark
the replacement pending, and report that styled completion is incomplete.
Never repaint, filter, or substitute a generated face for the source. Native
ImageGen subjects have their own parent-owned review and do not receive this
fallback.

## Configuration and handoff

Use the exact repository revision and workflow hashes in the enabled
provider's `.codex/portrait_pipeline.toml`. The project configuration stores
only non-secret provider state and the selected `provider_skill`; credentials
remain outside the project, lock, logs, prompts, screenshots, and runtime
files.

The portrait worker must report the selected provider skill, workflow commit,
source and prompt paths/hashes, user-supplied provider job evidence, output paths/hashes,
DDS path/hash, review result, final or pending state, skipped checks, and
remaining blockers. The parent owns character/GFX/gameplay/localisation
wiring and the final completion claim.
