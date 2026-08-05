---
name: hoi4-comfyui-local
description: Use only when the selected HOI4 portrait provider is a configured loopback ComfyUI installation.
---

# Loopback ComfyUI portrait route

Read `hoi4-portrait-production` first. This is the only provider-specific
portrait route that may be used for this project. Do not use another provider
skill or scan the computer for an unapproved installation.

Use only an explicitly configured or verified common installation root and a
loopback server at `127.0.0.1`, `localhost`, or `::1`. Report the root, server
URL, exact workflow commit, model presence, hardware result, and provider
status.

Use only a user-managed installation that already satisfies the locked hardware, model, authorization, and workflow requirements. The current source and processing graphs require the
`adaptive_portrait_crop` custom node and the MediaPipe/YuNet detector files.

Use the canonical model manifest and require Hugging Face authorization where the manifest requires it. Give the user the loopback REST/WebSocket steps; the user submits, polls the exact job/history record, and supplies both output sizes. The agent validates the supplied outputs and keeps server or filesystem paths out of runtime portrait references. It must not silently start or queue generation.

Missing hardware, authorization, models, workflow installation, or a running
server is an honest incomplete state. It is not successful portrait
production.
