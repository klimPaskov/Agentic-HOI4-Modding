# HOI4 feature-asset tools

These deterministic tools belong to the `hoi4-feature-assets` skill. Run them from the current mod root and keep outputs in the owner-approved asset workspace. They prepare evidence and processed assets; they do not approve identity, rights, likeness, role fit, or runtime completion.

## `extract_portrait_source_crop.py`

The grounded-portrait source stage preserves the unchanged archival master and writes a lossless crop, exact-pixel JSON evidence, a deterministic RGB `156x210` candidate, and a co-located provenance contract. Automatic mode uses the bundled YuNet model at `tools/models/face_detection_yunet_2026may.onnx` and fails closed unless exactly one usable face is detected. A detector is a framing aid, never identity approval. Zero/multiple detections, missing OpenCV support, missing model, unsafe geometry, or a write collision blocks the automatic route.

Run automatic mode with an output crop path in the durable owner package:

```powershell
python -B .agents/skills/hoi4-feature-assets/tools/extract_portrait_source_crop.py `
	<archival_master.jpg> <subject_source_crop.png>
```

The command writes co-located source copy, JSON, processed `156x210` PNG, and provenance files. For an independently reviewed detector miss or known boundary, use the explicit recovery rectangle:

```powershell
python -B .agents/skills/hoi4-feature-assets/tools/extract_portrait_source_crop.py `
	<archival_master.jpg> <archival_crop.png> `
	--crop <left> <top> <right> <bottom> `
	--metadata <archival_crop.json>
```

Manual mode records `manual_crop_override` and does not claim a face detection. Keep the original, lossless crop, JSON, processed PNG, and provenance contract together. The user supplies any grounded HOI4-style final; agents do not operate RunPod or another external provider on the user's behalf.

The vendored YuNet model is from the MIT-licensed OpenCV Zoo `face_detection_yunet` project. Retain `tools/models/LICENSE` and the recorded SHA-256; do not replace the model with an unverified detector.

## `create_advisor_icon.py`

Advisor, theorist, high-command, officer-corps, and army-small dossier portraits are a native `65x67` family. Inspect the matching vanilla reference and the exact `advisor_template.png` before processing.

The compositor loads the complete source canvas without a pre-crop or warp, measures the opening on every run, and applies one uniform aspect-preserving cover scale. It expands the opening with the centralized under-frame bleed and portrait-edge guard, masks the portrait to that safe region, and composites the untouched template as the final top layer. Exact-opening clipping is forbidden because translucent antialiased frame edges require portrait coverage beneath them. Anisotropic stretch, matte strips, exterior leakage, and frame redraw are rejected.

Run it with all review artifacts:

```powershell
python -B .agents/skills/hoi4-feature-assets/tools/create_advisor_icon.py `
	--source <approved_portrait> `
	--portrait-size <width> <height> `
	--rotation <degrees> `
	--portrait-offset <right> <down> `
	--study-candidate <width> <height> <right> <down> <rotation> `
	--placement-study <placement_study.png> `
	--alignment-preview <alignment_8x.png> `
	--preview <review.png> `
	--review-preview <review_4x.png> `
	--metadata <placement_metadata.json> `
	--output <runtime.dds>
```

The native preview, nearest-neighbour `4x` review, placement study, alignment overlay, metadata, and staged DDS are required outputs. Record opening geometry, source/template hashes, cover geometry, bleed/guard constants, selected placement, alpha coverage (`opening_alpha_gap_pixels=0`, `inner_edge_alpha_gap_pixels=0`, `exterior_alpha_leak_pixels=0`), and output hashes. Review native and `4x` renders against solid and checker backgrounds and the matching vanilla reference family. Automated checks are evidence, not visual approval.

## `convert_to_dds.py`

Convert only an approved processed PNG to the repository's verified one-level uncompressed 32-bit BGRA DDS contract:

```powershell
python -B .agents/skills/hoi4-feature-assets/tools/convert_to_dds.py `
	--input <processed.png> --output <runtime.dds> `
	--width <pixels> --height <pixels>
```

Retain native dimensions, header checks, alpha checks, source and DDS hashes, and decoded round-trip evidence. Runtime wiring remains parent-owned.

## `process_report_event_image.py`

Use only for report-event image processing, as described in the skill. It is not a portrait, icon, flag, or generic fallback.

```powershell
python -B .agents/skills/hoi4-feature-assets/tools/process_report_event_image.py `
	<input.png> <processed_report_event.png>
```
