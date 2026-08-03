---
name: hoi4-comfyui-runpod
description: Use for the optional RunPod ComfyUI portrait provider route.
---

# RunPod ComfyUI portrait provider

Prefer an existing pod and retain the non-secret URL/workspace in project
configuration. The canonical setup uses the current portrait repository and
its installer:

```bash
export HF_TOKEN="hf_..."
P=/workspace/comfyui-hoi4-portraits
test -d "$P/.git" || git clone --depth 1 https://github.com/klimPaskov/comfyui-hoi4-portraits "$P"
"$P/scripts/install_runpod.sh" /workspace/ComfyUI
```

Pass credentials only through a scoped process environment or provider vault;
never persist them. Record the resolved upstream commit, pod URL, workspace,
models, workflow installation, and exact provider status.

When interactive setup is required, use browser/computer control only against
the visible titled RunPod/ComfyUI window. Navigate by labels, inspect the
current screen before clicking, and stop for authorization, payment, model
import, or destructive actions. A pod URL alone is not a ready portrait
provider. Use the exact pinned API graph and retrieve both 832x1120 and 156x210
outputs before marking a portrait final.
