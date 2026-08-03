---
name: hoi4-comfyui-cloud
description: Use for the optional Comfy Cloud provider route for HOI4 portraits.
---

# Comfy Cloud portrait provider

Use `https://cloud.comfy.org/mcp` for the Comfy Cloud MCP route. Keep
authorization in the provider/client session; never write an API key or OAuth
token to the mod, installation lock, logs, prompts, or output.

The official API-key bootstrap commands from the canonical repository are:

```bash
curl -fsSL https://raw.githubusercontent.com/Comfy-Org/comfy-cloud-mcp/main/install.sh | bash
```

```powershell
irm https://raw.githubusercontent.com/Comfy-Org/comfy-cloud-mcp/main/install.ps1 | iex
```

Use a Comfy Cloud Builder subscription for custom model import. Import the
exact current LoRA filename:
`hoi4_portraits_flux2_klein_9b_lora_000002500.safetensors`.

Use the matching pinned `.api.json` graph from the upstream lock. Upload the
source through the Cloud upload flow; a local filesystem path is not a valid
Cloud `LoadImage.image` value. Dry-run the graph, submit it, retain the exact
`prompt_id`, wait for that job, and retrieve both 832x1120 and 156x210 outputs.
Queue emptiness is not proof of success. If authorization, subscription,
model import, or MCP access is missing, report the exact deferred status and
keep the source-based fallback pending.
