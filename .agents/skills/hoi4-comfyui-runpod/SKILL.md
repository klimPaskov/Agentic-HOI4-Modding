---
name: hoi4-comfyui-runpod
description: Use when the generic HOI4 portrait pipeline selects a RunPod ComfyUI workspace.
---

# RunPod ComfyUI portrait route

Read `hoi4-portrait-production` and `.codex/portrait_pipeline.toml` first. Use this route only when `provider = "runpod"`.

Use the configured user-managed pod and keep credentials outside the repository. The user runs the selected workflow and supplies the final portrait outputs; the agent validates and installs them through `hoi4_portrait_creator`.

If the workspace, endpoint, workflow, models, or access are unavailable, leave the portrait pending and report the exact blocker. Never silently switch providers.
