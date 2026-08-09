---
name: hoi4-comfyui-local
description: Use when the generic HOI4 portrait pipeline selects a local ComfyUI installation.
---

# Local ComfyUI portrait route

Read `hoi4-portrait-production` and `.codex/portrait_pipeline.toml` first. Use this route only for a grounded subject's styled replacement when `provider = "local"`; fictional or impossible portraits use native ImageGen through the portrait owner.

Respect only the explicitly configured local installation and loopback endpoint. The user runs the selected workflow and supplies the final portrait outputs; the agent does not operate the provider and only validates and installs supplied results through `hoi4_portrait_creator`.

If the installation, server, models, custom nodes, or hardware requirements are unavailable, leave the portrait pending and report the exact blocker. Never scan for, start, or substitute an unconfigured installation.
