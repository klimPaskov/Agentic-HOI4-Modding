---
name: hoi4-portrait-production
description: "Use for complete HOI4 character portrait production: real-source research and placeholders, selectable Cloud/Local/RunPod styled replacements, fictional ImageGen portraits, processing, DDS conversion, portrait wiring, manifests, and handoffs."
---

# HOI4 portrait production

`hoi4_portrait_creator` owns every character portrait from brief to installed runtime asset.

1. Inspect matching installed-vanilla portrait references and lock the role, dimensions, basename, and consumers.
2. Classify the subject. Real or grounded subjects require attributed Internet source research; fictional or impossible subjects use native ImageGen.
3. For a grounded portrait, find and verify the source, record provenance and rights status, archive it under `docs/assets/portraits/<feature_slug>/`, create the explicit crop, and install an explicitly pending source placeholder at the stable final runtime path. Read `.codex/portrait_pipeline.toml` and the selected Cloud, Local, or RunPod provider skill; the user runs that styled-replacement workflow and supplies the final output.
4. For a fictional or impossible portrait, invoke native ImageGen, review the full-resolution result against the brief and vanilla references, and retain prompt/source evidence.
5. Process the approved portrait, create required PNG/DDS variants, preserve stable identifiers, update portrait-specific `.gfx` and existing character portrait references, and write the manifest and handoff.

Never generate or substitute the identity of a real person. If no defensible grounded source exists, mark the portrait blocked. `hoi4_portrait_creator` is the sole portrait owner: other asset roles must hand portrait work to it. Never silently switch configured providers. Agents never open, configure, queue, monitor, or otherwise operate RunPod. Do not edit unrelated gameplay, localisation, or UI.
