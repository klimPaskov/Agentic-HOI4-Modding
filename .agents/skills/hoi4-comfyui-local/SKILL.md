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

Before offering a new installation, inspect hardware and refuse an infeasible
route unless the user explicitly overrides the gate. Use the exact upstream
scripts after review:

```powershell
.\scripts\install_windows.ps1 -ComfyUIRoot "<COMFYUI_ROOT>"
python scripts/install_workflows.py --comfyui-root "<COMFYUI_ROOT>"
python scripts/download_models.py --comfyui-root "<COMFYUI_ROOT>"
```

The current manifest installs eight pinned model files totaling about 19.42 GB
decimal. A 24 GB GPU is the practical target; 18 GB may work with aggressive
offloading, and 16 GB is limited to slower reduced-resolution tests. Accept
the gated FLUX.2 Klein agreement before downloading the base model. The
current source and processing graphs also require the
`adaptive_portrait_crop` custom node and the MediaPipe/YuNet detector files.

Use the canonical model manifest and require Hugging Face authorization where
the manifest requires it. Submit through the loopback REST/WebSocket
interface, poll the exact job/history record, retrieve both output sizes, and
keep server or filesystem paths out of runtime portrait references.

Missing hardware, authorization, models, workflow installation, or a running
server is an honest incomplete state. It is not successful portrait
production.
