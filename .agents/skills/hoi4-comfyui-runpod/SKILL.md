---
name: hoi4-comfyui-runpod
description: Use only when the selected HOI4 portrait provider is an existing RunPod ComfyUI workspace.
---

# RunPod ComfyUI portrait route

Read `hoi4-portrait-production` first. This is the only provider-specific
portrait route that may be used for this project. Do not use another provider
skill or claim that a workspace is ready from a URL alone.

Use an existing user-managed pod. Persist only the non-secret workspace and endpoint in
`.codex/portrait_pipeline.toml`. Keep tokens in a provider vault or scoped
process environment and never write them to the project, lock, logs, prompts,
screenshots, or runtime output.

Record the resolved upstream commit, workspace, endpoint, model state, and
workflow installation. An endpoint is not ready until the selected workflow
is visible and the required models are available.

Give the user the pinned API graph and exact API steps. The user uploads the approved source, performs one dry-run/no-spend validation, retains the exact `prompt_id`, waits for terminal success, reviews the three source candidates, selects one `832x1120`/`156x210` pair, and supplies it for dimension, identity, framing, and hash validation. Use browser or computer control only when the parent explicitly requests help with the current user-run job. Never silently queue or generate, and do not claim completion from queue state.

Missing workspace access, models, workflow installation, or endpoint health
keeps the portrait pending and preserves the source-based fallback.
