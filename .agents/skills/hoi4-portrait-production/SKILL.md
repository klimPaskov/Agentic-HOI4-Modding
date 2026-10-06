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

## Parallel portrait receipts and final selection

Parallel portrait workers report only their bounded tranche's files and independent acceptance evidence and status.
Global completion counts belong to the parent; cite them only from a current authoritative parent inventory with its revision and observation time, and never copy an earlier parent count.
A missing or parse-failed receipt leaves another owner's status unknown, not unproduced or pending.
Preserve timestamped pre and post snapshots, observed changed paths, and known concurrent changes in disjoint regions without resetting shared work or attributing another owner's changes to yourself.
A later global count must not rewrite historical pre and post facts.

Record whether current runtime DDS bytes match the selected candidate separately from art acceptance; a matching hash alone never proves final approval.
Source versions and canonical PNG packages may retain unselected alternates, so final global review must follow the explicit selected source or version and the processed PNG -> candidate DDS -> runtime path mapping, never the first glob match or an unsuffixed filename.
When moving receipts to canonical paths, update pointers in every referring manifest, handoff, and referenced metadata record while preserving immutable original source and candidate lineage and the receipt's original path and revision.
