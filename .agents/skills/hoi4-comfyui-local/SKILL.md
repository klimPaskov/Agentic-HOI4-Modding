---
name: hoi4-comfyui-local
description: Use for the optional local ComfyUI portrait provider route.
---

# Local ComfyUI portrait provider

Only use a configured or common local ComfyUI root and a loopback server
(127.0.0.1, localhost, or ::1). Do not scan the whole computer. Report the
root, server URL, workflow commit, model presence, and provider status.

Before offering a new install, inspect hardware. Refuse an infeasible local
route unless the user explicitly overrides the hardware gate. Use the exact
current upstream scripts after review:

```powershell
.\scripts\install_windows.ps1 -ComfyUIRoot "<COMFYUI_ROOT>"
python scripts/install_workflows.py --comfyui-root "<COMFYUI_ROOT>"
python scripts/download_models.py --comfyui-root "<COMFYUI_ROOT>"
```

Use the canonical model manifest and require Hugging Face authorization where
the manifest says it is required. Submit through the local REST/WebSocket
interface, poll the exact job/history record, retrieve both output sizes, and
keep browser-visible or server paths out of runtime portrait references.

Missing hardware, Hugging Face access, models, workflow installation, or a
running server is an honest incomplete provider status, not a successful
installation.
