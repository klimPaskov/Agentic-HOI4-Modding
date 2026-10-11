# Report and news images and flags

This reference belongs to the `hoi4-feature-assets` skill and holds complete sections moved out of `SKILL.md` to keep it within the single-read ceiling. Every rule here is as binding as the rules in `SKILL.md`.

## 13. Report event images

Report event images may use internet-sourced imagery or generated period-documentary imagery. Prefer generated report images when the event needs a unique fictional or alternate-history scene, staged document, invented location, or more specific visual than archive search can reliably provide. Use real sources when the image must depict a real person, real historical scene, or real archival document.

Report event images should look like documentary-style photographs, field documentation, or period documentary material.

For Second World War-era subjects, prefer contemporary photographs, war correspondents' photographs, press agency images, propaganda posters, newspapers, maps, official records, military archive images, museum or library scans, or period illustrations. Do not use modern reenactment photos or modern documentary photos that visually belong to a later era.

Use:

- realistic or period-authentic source imagery
- black-and-white treatment with sepia applied
- Second World War-era visual fit when the feature belongs to that era
- period-appropriate framing where possible
- strong subject clarity
- natural composition
- no modern UI overlays
- no modern clothing, streets, weapons, vehicles, buildings, or props unless they are intentionally part of the event
- no generated text

Target size:

```text
210x176
```

Report event images must be black and white with sepia applied. Do not leave report event images in full colour unless the user explicitly requests a colour exception, and record that exception in the manifest.

### Report-event card treatment

Report-event images use a finished `210x176` RGBA canvas. The source photograph is processed as a slightly tilted documentary card with transparent edge space and a soft drop shadow. The transparent corners are part of the style.

Do not ask the image generator to create the tilted card. Generate or source the documentary photograph first, then apply the card treatment locally. This keeps the tilt, shadow, and margins consistent.

```bash
python -B .claude/skills/hoi4-feature-assets/tools/process_report_event_image.py source.png processed_report_event.png
python -B .claude/skills/hoi4-feature-assets/tools/process_report_event_image.py source_folder processed_folder
```

The script performs cover crop, black-and-white conversion, sepia application, grain, paper border, deterministic tilt, transparent canvas margin, and soft shadow. It writes RGBA PNG output. Convert the processed PNG to DDS through the normal repo workflow.

Validation:

- processed PNG is exactly `210x176`
- final DDS is exactly `210x176`
- corner pixels are transparent
- no hard photo pixels are clipped
- tilt is visible but subtle
- shadow is soft and not a thick border
- edge space is transparent, not black padding
- source remains readable after crop, tilt, shadow, and DDS conversion

Generated report images must still receive this local report-card treatment.

## 20. Flags

Flags should use clean symbolic designs that look like intentional flag art, not simple-shape placeholders, palette swaps, ugly filters, or flipped/recolored variants.

They must remain readable at HOI4 sizes.

Required flag sizes:

- small: 10x7
- medium: 41x26
- normal: 82x52

HOI4 flag TGAs must use the same origin/header convention as vanilla flags. Validate with `file`; completed flag TGAs should read as Targa image data at the correct size and must not end with `- top`. If a flag displays upside down in-game while the artwork looks correct in an image viewer, fix the TGA encoding/origin on the flag files themselves. Do not add custom UI sprites, scripted-localisation routing, DDS display copies, or other workarounds for flag orientation.

Avoid overly detailed symbols.

Avoid generated text unless the design absolutely requires it and the final output is manually checked.

Always use the image generator for fictional flags and user-provided or internet source images for historical or real-world flags.

For existing countries that already have game-provided or repository-approved base flags, do not replace the no-suffix base flag as part of an ideology pass. Keep the base flag unchanged, or restore it from the approved prior asset if an asset pass damaged it, unless the user explicitly asks for that base flag to be redone or the country receives a deliberate focus/event/cosmetic-tag transformation. Ideology variants should be separate assets for `_communism`, `_democratic`, `_fascism`, and `_neutrality`, not mutations of the base flag with one small shape, a palette swap, a color filter, a vertical flip, or a copied emblem.

For focus-tree or event route flag changes, use explicit cosmetic tags or route-specific flag files and document the trigger/focus that changes the flag. Do not create default flag overrides or new base flags for vanilla-supported or already-existing countries just because they participate in an event.

Historical or historically grounded flags must use sourced motifs, documented heraldry, period symbols, or clearly explained alternate-history synthesis. If no directly attested flag exists, state that in the manifest and produce a historically grounded design from relevant motifs instead of inventing unrelated symbols.

Generated fictional or alternate-history flag variants must come from generated/source artwork and then be processed into final flag sizes. Do not hand-draw final flags from basic rectangles, circles, stars, arrows, or random emblems unless those shapes are part of a researched or generated source design.

Before marking any flag complete, verify normal, medium, and small TGA files:

- normal: 82x52
- medium: 41x26
- small: 10x7
- correct visual orientation in a contact sheet
- TGA origin/header convention consistent with vanilla HOI4 flags; `file` output must not show `- top`
- no byte-identical ideology variants unless the design is intentionally shared and documented
- no upside-down copies
- no accidental no-suffix base-flag replacement for countries that were only meant to receive ideology variants
