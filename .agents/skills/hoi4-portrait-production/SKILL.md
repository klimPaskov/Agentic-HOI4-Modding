---
name: hoi4-portrait-production
description: Use for sourced or grounded HOI4 portraits that are archived and wired as source placeholders, then replaced with user-supplied HOI4-style finals.
---

# HOI4 sourced portraits

1. Find and verify an attributed source portrait. Never generate or substitute a real person's identity.
2. Save the source under `docs/assets/portraits/<feature_slug>/` using the runtime portrait basename. Record its provenance.
3. Crop and convert the source to the runtime portrait DDS size, wire it at the final path, and mark it as a pending source placeholder.
4. Read `.codex/portrait_pipeline.toml` and the selected provider skill: `hoi4-comfyui-cloud`, `hoi4-comfyui-local`, or `hoi4-comfyui-runpod`. The user runs that workflow and supplies the final outputs.
5. When the user supplies the HOI4-style final, verify identity, framing, dimensions, and provenance; convert it to DDS and replace the placeholder without changing the runtime basename or wiring.

Keep the durable source archive after replacement. Runtime files must never reference `docs/assets/portraits/`.

`hoi4_asset_source_researcher` owns source research and provenance. `hoi4_portrait_creator` validates and converts the user-supplied final. The parent owns character, `.gfx`, localisation, gameplay, and runtime wiring.

Provider choice is project configuration. Never silently replace the selected Cloud, Local, or RunPod route with another provider.

Non-sourced fictional or impossible portraits use parent-owned native ImageGen and do not use this workflow.
