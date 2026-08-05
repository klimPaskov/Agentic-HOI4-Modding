---
name: hoi4-comfyui-cloud
description: Use only when the selected HOI4 portrait provider is the Comfy Cloud MCP route.
---

# Comfy Cloud portrait route

Read `hoi4-portrait-production` first. This is the only provider-specific
portrait route that may be used for this project. Do not use another provider
skill or invent a fallback route.

Use the official Comfy Cloud MCP endpoint:

`https://cloud.comfy.org/mcp`

Keep authorization in the provider/client session. Never write an API key,
OAuth token, account data, or cookie to the mod, installation lock, logs,
prompts, screenshots, or output.

The canonical bootstrap commands are:

```bash
curl -fsSL https://raw.githubusercontent.com/Comfy-Org/comfy-cloud-mcp/main/install.sh | bash
```

```powershell
irm https://raw.githubusercontent.com/Comfy-Org/comfy-cloud-mcp/main/install.ps1 | iex
```

Use the provider subscription required for custom model import. Import the
exact current LoRA filename from the pinned upstream model manifest:
`hoi4_portraits_flux2_klein_9b_lora_000002500.safetensors`.

The source and processing graphs also use the upstream
`adaptive_portrait_crop` custom node. Confirm that the current Builder
environment has that node before opening the graph. The processing graph does
not use the LoRA; a source run still emits three candidate master/game pairs
for review.

Use the matching pinned `.api.json` graph. Upload the approved source through
the provider upload flow; a project filesystem path is not a valid
`LoadImage.image` value. Dry-run the graph, submit it, retain the exact
`prompt_id`, wait for that job, and retrieve both `832x1120` and `156x210`
outputs. A source run emits three candidate master/game pairs; review and
select one before handing the pair to the project. Queue emptiness is not
proof of success.

If authorization, subscription, model import, or MCP access is missing, keep
the exact deferred status and the source-based fallback pending. Do not claim
styled completion from a queued job or a provider preview.
