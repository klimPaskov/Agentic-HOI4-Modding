---
name: hoi4-comfyui-runpod
description: Use only when the selected HOI4 portrait provider is an existing RunPod ComfyUI workspace.
---

# RunPod ComfyUI portrait route

Read `hoi4-portrait-production` first. This is the only provider-specific
portrait route that may be used for this project. Do not use another provider
skill or claim that a workspace is ready from a URL alone.

Prefer an existing pod. Persist only the non-secret workspace and endpoint in
`.codex/portrait_pipeline.toml`. Keep tokens in a provider vault or scoped
process environment and never write them to the project, lock, logs, prompts,
screenshots, or runtime output.

The canonical setup uses the pinned repository and installer:

```bash
export HF_TOKEN="hf_..."
P=/workspace/comfyui-hoi4-portraits
COMFY_ROOT=/workspace/runpod-slim/ComfyUI
test -f "$COMFY_ROOT/main.py" || { echo "ComfyUI not found at $COMFY_ROOT; set COMFY_ROOT to the folder containing main.py."; exit 1; }
test -d "$P/.git" || git clone --depth 1 https://github.com/klimPaskov/comfyui-hoi4-portraits "$P"
"$P/scripts/install_runpod.sh" "$COMFY_ROOT"
```

The current installer places the adaptive crop node, workflows, backgrounds,
sample input, and eight pinned model files into the standard ComfyUI folders.
The model files use about 19.42 GB decimal; keep a 30 GB pod volume for the
repository, ComfyUI files, caches, and outputs. Start the pod UI with:

```bash
"$P/scripts/start_runpod.sh" "$COMFY_ROOT"
```

Record the resolved upstream commit, workspace, endpoint, model state, and
workflow installation. An endpoint is not ready until the selected workflow
is visible and the required models are available.

Use the pinned API graph when the endpoint is reachable. Upload the approved
source, submit one dry-run/no-spend validation, retain the exact `prompt_id`,
wait for terminal success, review the three source candidates, select one
`832x1120`/`156x210` pair, and verify its dimensions and hashes. Use browser or
computer control only when the parent explicitly requests visible operation;
otherwise provide the manual/API steps and do not claim generation.

Missing workspace access, models, workflow installation, or endpoint health
keeps the portrait pending and preserves the source-based fallback.
