# Achievement icons

This reference belongs to the `hoi4-feature-assets` skill and holds complete sections moved out of `SKILL.md` to keep it within the single-read ceiling. Every rule here is as binding as the rules in `SKILL.md`.

## 19. Achievement icons

Achievement icons should be compact and readable at 64x64.

Inspect `assets/vanilla_reference/icons/achievements/contact_sheet.png` and matching individual references before creating an achievement icon. The contact sheet and references are review material. The separate `template/` folder is excluded from the reference count.

### New achievement creation

Use the image generator to design one original subject on a genuinely transparent background, guided by the inspected achievement references for framing, density, contrast, and readability. Request no achievement frame, square background, red cross, text, or fake checkerboard. Process the result into one centered 64x64 color subject layer. Retain the native generated source PNG, prompt, processed PNG, and candidate lineage. Do not independently generate three state artworks or borrow another icon type.

Use these exact supplied workflow inputs and do not rename, move, resize, crop, trim, recolor, redraw, filter, or replace them:

```text
assets/vanilla_reference/icons/achievements/template/achievement_template.png
assets/vanilla_reference/icons/achievements/template/achievement_template_grey.png
assets/vanilla_reference/icons/achievements/template/overlay.png
```

Their verified SHA-256 values are respectively `248DB006611EB3942550C43DF83802AA6FB24761035FC928B5D34586C0C4C5BA`, `70E073694C1A7D9FE40C63B1EB2E987A8A45B3FFD15CCF789EEAA5B843B90022`, and `89BC80C6AC975BF6F1FF000FF3070B20C337BFB8B8AE966AE35A5540C004D6DD`.

Build one complete transparent source triplet deterministically from the color subject, preserving the 64x64 canvas, exact position, and alpha alignment:

1. Completed source: the processed transparent color subject unchanged.
2. Grey source: a deterministic grayscale conversion of the same subject.
3. Not-eligible source: the grey source with the unchanged `template/overlay.png` composited on top at exact alignment.

Then use `tools/process_achievement_icons.py` to place the supplied completed background beneath the completed source and the supplied grey background beneath the grey and not-eligible sources. Normal alpha compositing is the only pixel interaction. Do not derive not-eligible state from a completed or runtime grey output, recolor or resize the red cross, or feed a processed output back as a source layer.

### Existing-triplet migration

For an existing achievement, provide the complete `<achievement_id>.{png,dds}`, `<achievement_id>_grey.{png,dds}`, and `<achievement_id>_not_eligible.{png,dds}` source triplet. Migration preserves each supplied state at its native 64x64 canvas and exact position without resizing, cropping, alpha trimming, grayscale conversion, recoloring, redrawing, filtering, or other preprocessing. It never derives a missing state.

Every decoded source state must be exactly 64x64. The processor fails closed when a state is missing or a source exposes an already-applied template border. Keep source triplets separate from processed outputs and use `--in-place --force` only for intentional replacement.

Target size:

```text
64x64
```

Use an `achievement_` prefix for source or intermediate art when it helps distinguish the asset type.

For final files, achievements are a root-only exception. Put completed, grey, and not-eligible DDS files directly under `gfx/achievements/`, and name them after the exact achievement id registered in `common/achievements/`:

```text
gfx/achievements/<achievement_id>.dds
gfx/achievements/<achievement_id>_grey.dds
gfx/achievements/<achievement_id>_not_eligible.dds
```

When renaming or adding achievement ids, update `common/achievements/`, `localisation/english/<mod_namespace>_achievements_l_english.yml`, `interface/<mod_namespace>_achievements.gfx`, the three DDS variants in `gfx/achievements/`, and any docs or manifests that list the final DDS paths. If the achievement registry owns a single `unique_id`, keep it as one root-level registry file and group feature-owned achievements by feature section inside the file instead of splitting it into per-feature achievement files.

Validation and handoff must retain the source color subject, deterministic grey source, not-eligible source with unchanged overlay, all three composited review PNGs, a native-size contact sheet, three template hashes, strict DDS decode and pixel-equality evidence, and final root-only DDS paths. Identify the exact achievement id, runtime triplet, registered sprite aliases, source and processed paths, and any remaining review or blocked state. The parent reviews the contact sheet before wiring or completion.
