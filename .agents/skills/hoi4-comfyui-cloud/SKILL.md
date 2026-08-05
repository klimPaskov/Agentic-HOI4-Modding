---
name: hoi4-comfyui-cloud
description: Use when the generic HOI4 portrait pipeline selects Comfy Cloud.
---

# Comfy Cloud portrait route

Read `hoi4-portrait-production` and `.codex/portrait_pipeline.toml` first. Use this route only when `provider = "cloud"`.

Use the configured Comfy Cloud MCP endpoint and keep credentials outside the repository. The user runs the selected workflow and supplies the final portrait outputs; the agent validates and installs them through `hoi4_portrait_creator`.

If authorization, the required subscription, models, custom nodes, or provider access are unavailable, leave the portrait pending and report the exact blocker. Never silently switch providers.
