---
name: hoi4-comfyui-runpod
description: Use when the generic HOI4 portrait pipeline selects a RunPod ComfyUI workspace.
---

# RunPod ComfyUI portrait route

Read `hoi4-portrait-production` and `.codex/portrait_pipeline.toml` first. Use this route only for a grounded subject's styled replacement when `provider = "runpod"`; fictional or impossible portraits use native ImageGen through the portrait owner.

Respect the configured user-managed pod and keep credentials outside the repository. The user alone runs the selected workflow and supplies the final portrait outputs; the agent only validates and installs supplied results through `hoi4_portrait_creator`. Agents must never open, configure, start, queue, monitor, or otherwise operate RunPod or its workspace.

If the workspace, endpoint, workflow, models, or access are unavailable, leave the portrait pending and report the exact blocker. Never silently switch providers.
