# HOI4 Feature-Asset Tools

These are the active reusable tools for the `hoi4-feature-assets` skill. Call
them from the mod root. Canonical engine-surface reference lookups use:

`.agents/skills/hoi4-feature-assets/assets/vanilla_reference/`

Select the role-specific leader, commander, operative, or advisor family before
production. Advisor dossier cards use the separate canonical references under
`.agents/skills/hoi4-feature-assets/assets/vanilla_reference/portraits/advisors/`.

There is no bundled full-size portrait processor. After the immutable crop, create
the deterministic `156x210` country-leader, commander, operative, or named-officeholder
candidate with a reproducible task-specific/manual image workflow. Inspect the
canonical role family (`leaders/`, `commanders/`, or `operatives/`). Retain the processed source or
ImageGen result, candidate PNG, exact dimensions, crop metadata, hashes, role-specific
comparison sheet, and independent likeness/style/provenance review. Do not hand off
a raw, filtered, or merely resized photograph as runtime art.

Use the canonical role-specific references as style-family controls only. An
independent auditor must compare the archival master, explicit archival crop, raw
ImageGen result, processed candidate, and role-specific references separately.

## `extract_portrait_source_crop.py`

This is the only accepted immutable crop stage for a real-person archival photograph. It decodes the photographic master and crops it with Pillow, preserves the decoded source mode in a lossless PNG, reopens that PNG, and proves exact decoded-pixel equality against the same master rectangle in RGBA form before committing the PNG and JSON evidence together. It never resizes, enhances, recolours, retouches, or replaces an existing artifact without `--force`. Illustrations and generated reconstructions cannot be used as real-person identity masters.

Run it before ImageGen with the measured boundary in decoded master pixels:

```powershell
python -B .agents/skills/hoi4-feature-assets/tools/extract_portrait_source_crop.py `
	<archival_master.jpg> <archival_crop.png> `
	--crop <left> <top> <right> <bottom> `
	--metadata <archival_crop.json>
```

Keep the PNG and JSON together. The JSON records the Pillow/tool versions and hash, master/output hashes and dimensions, decode modes, crop rectangle, equality hashes/result, and a normalized command. `ffmpeg` or ImageMagick crops are not immutable source crops unless an independent check proves exact equality of their decoded output pixels against the same decoded master rectangle and retains equivalent evidence; when that proof is unavailable, reject the crop and return to this utility.

## `convert_to_dds.py`

Converts an approved PNG to the legacy one-level uncompressed BGRA DDS layout
used by the relevant vanilla HOI4 UI assets.

```powershell
python -B .agents/skills/hoi4-feature-assets/tools/convert_to_dds.py `
	--input <approved.png> --output <runtime.dds> `
	--width <pixels> --height <pixels>
```

The command above is the supported converter; `.tools/convert_to_dds.py` is
obsolete and must not be restored or used by active workflows. Follow the matching vanilla
catalog entry for dimensions and compression.

## Advisor and high-command dossier portraits

Advisor, theorist, military-high-command, officer-corps, and army-small portraits are a separate, explicitly authorized asset family.

Inspect the canonical native `65x67` references under `.agents/skills/hoi4-feature-assets/assets/vanilla_reference/portraits/advisors/`.

Use `create_advisor_icon.py` when the accepted design calls for the shared `advisor_template.png` dossier surface.

The tool loads the complete source portrait without cropping, resizes the complete source to a `65x67` intermediate, applies the requested transformed size, rotation, and opening-center offset, and composites the untouched template once as the top layer.

Run it from the mod root:

```powershell
python -B .agents/skills/hoi4-feature-assets/tools/create_advisor_icon.py `
	--source <approved_portrait.dds> `
	--portrait-size <width> <height> `
	--rotation <degrees> `
	--portrait-offset <right> <down> `
	--preview <review.png> `
	--output <runtime.dds>
```

Negative `--portrait-offset` values move left or up.

Use a coarse placement grid followed by a fine grid against the actual template opening when the first supplied transform does not fit.

Keep the complete head and shoulders readable, prevent portrait pixels from appearing outside the frame, keep the face clear of the paper, and retain the exact template as the final top layer.

Record the source hash, template hash, complete-source resize, selected dimensions, center, offset, rotation, sepia strength, candidate grids, independent review, processed PNG hash, and runtime DDS hash.

For grounded real people, complete the shared sourced identity gate through an independently approved `156x210` candidate first; fictional high-chaos or impossible or supernatural subjects may use an approved generated master.

Review the candidate at native size and at `4x` nearest-neighbour size against the canonical advisor and high-command family.

The producer may not approve the candidate.

## `process_report_event_image.py`

Processes report-event source art according to the report-event workflow
documented in the skill. It is not a portrait, flag, icon, or generic-image
fallback.

```powershell
python -B .agents/skills/hoi4-feature-assets/tools/process_report_event_image.py `
	<input.png> <processed_report_event.png>
```
