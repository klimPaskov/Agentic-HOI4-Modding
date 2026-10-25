# Shared sprite QA and alpha repair

Run from the mod root with Python 3.9 or later.
Install dependencies with `python -m pip install -r .tools/gfx/requirements.txt`.
The repair and conversion tools operate only on explicitly selected paths; there is no implicit repository-wide mutation. The conformance checks below read the repository and write nothing.
All repair and conversion outputs go to a separate directory for review before the asset owner installs them.

`gfx.py` is a byte-identical copy of the upstream tool (`scripts/shared_tools.json` in the source package). Repository values live beside it: `settings.json` names the asset-tool folder (`asset_tools`, the folder of `convert_to_dds.py` and `process_report_event_image.py`) and an optional registry prefix for contact-sheet grouping, and `profiles.json` holds the canvas profiles.

## Commands

```powershell
# Audit alpha, including every frame of a horizontal sheet.
python -B .tools/gfx/gfx.py alpha gfx/interface/goals/example.dds --json alpha.json
python -B .tools/gfx/gfx.py alpha gfx/texticons/example.dds --frames 2 --json alpha.json

# Batch input: JSON array of literal paths, or objects with a texture/path field.
python -B .tools/gfx/gfx.py alpha --list owned_paths.json --json alpha.json

# Erode one pixel of alpha, and bleed uncontaminated interior colour into edge pixels.
# The output mirrors input paths relative to --root; DDS inputs become lossless PNG previews.
python -B .tools/gfx/gfx.py defringe --list owned_paths.json --root . --out .tmp/gfx_review/review --json defringe.json

# Check exact canvas, transparent margins and undersized subjects.
python -B .tools/gfx/gfx.py size gfx/event_pictures/example.dds --profile report --json size.json
python -B .tools/gfx/gfx.py size gfx/interface/decisions/example.dds --profile category

# Compare the exact counter surface to an inspected installed-vanilla reference.
python -B .tools/gfx/gfx.py counter gfx/interface/counters/divisions_large/example.dds --surface large --reference "<HOI4_GAME_DIR>/gfx/interface/counters/divisions_large/unit_infantry_icon.dds"

# Mechanical 2D DDS conversion: call the existing asset-skill writer and verify the bytes.
python -B .tools/gfx/gfx.py dds .tmp/gfx_review/review/gfx/interface/goals/example.png --root .tmp/gfx_review/review --out .tmp/gfx_review/dds --json dds.json

# Contact sheets of every registered sprite in selected registry groups.
python -B .tools/gfx/gfx.py sheet --groups my_feature_icons --out .tmp/gfx_review/sheets --label before
```

Read-only repository conformance checks follow the `.tools/lib/report.py` contract (`--paths`, `--paths-from`, `--json`, `--fail-on`), so `.tools/check.py` can run them:

```powershell
python -B .tools/gfx/gfx.py audit                       # every check below
python -B .tools/gfx/gfx.py sprites --paths interface/countrystateview.gfx
python -B .tools/gfx/gfx.py flags
python -B .tools/gfx/gfx.py achievements
python -B .tools/gfx/gfx.py binaries --paths gfx/interface/goals
python -B .tools/gfx/gfx.py families --paths gfx/interface/goals/x.dds
python -B .tools/gfx/gfx.py families --calibrate-vanilla   # per-rule rates on the installed game
python -B .tools/gfx/gfx.py reports
```

| Rule | Level | What it checks and why |
|---|---|---|
| `GFX-FRAME-WIDTH` | warning | A multi-frame sprite's texture width divides by `noOfFrames`. Vanilla ships 79 of 1,798 uneven strips, so the engine tolerates it; the message gives the per-frame width for review. |
| `GFX-FLAG-SIZE` | error | Normal, medium and small flag TGAs are 82x52, 41x26 and 10x7 (`hoi4-feature-assets` flag rules; 2,202 of 2,203 vanilla files per folder). |
| `GFX-FLAG-LADDER` | warning | A flag exists in all three sizes. The skill requires it for completion, but vanilla ships incomplete ladders. |
| `GFX-FLAG-ORIGIN` | warning | A flag TGA is stored bottom-origin, as the flag rules require; vanilla ships 5 of 2,203 top-origin flags, so the engine loads them. |
| `GFX-ACHIEVEMENT-SIZE` | error | Achievement art is 64x64 (882 of 882 vanilla files). Triplet presence for defined achievements is checked by `audit_asset_wiring_static.py`. |
| `GFX-LFS-POINTER`, `GFX-TRUNCATED` | error | Runtime binaries under `gfx/`, `sound/` and `music/` hold real data: no LFS pointer, a complete header, and at least the payload their DDS or TGA header declares. DX10, compressed and mipmapped DDS are accepted. |
| `GFX-FOCUS-SIZE`, `GFX-DECISION-SIZE`, `GFX-IDEA-SIZE` | from the profile row | A focus, decision or idea frame is one of the sizes its `profiles.json` row accepts. These rows are project decisions, so the source package ships none; the check is silent for a family without a row. |
| `GFX-FOCUS-ALTERNATIVE` | warning for `--paths`, review otherwise | A focus icon uses an accepted size other than the row's canvas for new art. |
| `GFX-OPAQUE-CANVAS` | error | All four corners of a profiled focus, decision or idea frame are fully opaque, so the unused canvas has a background. No vanilla texture of those families matches. |
| `GFX-EMPTY-SUBJECT` | error | A profiled focus, decision or idea frame has no visible pixel. |
| `GFX-GHOSTED` | warning | A focus icon's visible pixels average below alpha 200; decision and idea icons are exempt because vanilla's are normally that faint. |
| `GFX-CHROMA-FRINGE` | warning | Edge pixels of a profiled family texture carry the magenta or green key colour that `defringe` repairs; legitimate green or purple art also triggers it. |
| `GFX-REPORT-PROVENANCE-MISMATCH`, `GFX-REPORT-RECIPE-MISMATCH` | error | A 210x176 report picture with a record in the provenance registry (`report_provenance` in the asset tools' `project_settings.json`) has the recorded pixels, and rerunning the recorded recipe on the recorded source (when it still exists) reproduces them. |
| `GFX-REPORT-NO-PROVENANCE`, `GFX-REPORT-OPAQUE-CORNERS`, `GFX-REPORT-STALE-PROVENANCE` | warning | A report picture has no record (then only its size and transparent corners can be checked), a corner is opaque (the report-card tilt is missing), or a record names a missing file. |

Family checks take their consumers from the asset audit's implicit-lookup extractors (focus `icon =`, decision `icon =`, idea `picture` or default), resolve each sprite through the `.gfx` registry, and measure only textures stored in the mod.
`families --calibrate-vanilla` runs the same rules on the installed game and prints each rule's rate for every profiled family; on the vanilla game installed in October 2026, `GFX-OPAQUE-CANVAS` and `GFX-EMPTY-SUBJECT` matched 0 of 4,440 focus, decision and idea textures, `GFX-GHOSTED` 5.5% of focus icons, and `GFX-CHROMA-FRINGE` 4–7%.
The report recipe is recorded by `process_report_event_image.py --runtime gfx/event_pictures/<file>.dds` (see `hoi4-feature-assets`); `pixels_sha256` is preserved by the uncompressed BGRA DDS conversion, so the runtime file stays verifiable after its temporary workspace is deleted.
These checks establish geometry, transparency and file integrity only, never visual quality or style.

Use the actual vanilla texture path from its `.gfx` definition; the counter command requires this explicit reference and does not guess it from a unit name.
Exit status is `0` when every requested operation/check succeeds, and `1` for findings or input errors.
JSON reports include each source hash, dimensions, per-frame alpha, visible bounds and detected chroma edge pixels.
Redirect console output to a file for large batches; `--json` writes the full structured report independently.
Existing output files are refused unless `--force` is supplied.
Non-force PNG/DDS installs use an exclusive same-directory hard link so a concurrent writer cannot silently replace another worker's output; filesystems without hard-link support fail closed.
Even `--force` cannot overwrite an input.
Input LFS pointers, unsupported images, incomplete frame widths and truncated DDS data fail rather than silently exporting a substitute.

## Alpha processing

`alpha` flags a mean below `200` across subject pixels with nonzero alpha.
Empty subjects also fail.
The check is per frame: a solid NATO frame cannot hide an almost invisible first frame.
Thin antialiased symbols and intentional disabled states can trigger this diagnostic and need consumer review; it is not permission to make every pixel opaque.

`defringe` is for existing transparent cut-outs with inherited key-colour contamination, not the normal production route for new art.
New icons use real transparency from the selected image-generation route, as `hoi4-feature-assets` requires.
It shrinks the alpha boundary by one pixel using a zero-padded minimum filter, then extends the nearest uncontaminated opaque interior RGB into semitransparent/transparent pixels and contaminated edge pixels.
Magenta means both red and blue exceed green by more than 40; green means green exceeds red and blue by more than 40.
Interior seed pixels must have alpha at least 240 and survive a one-pixel erosion, so a key-coloured rim cannot become a source colour.
RGB bleeding does not alter alpha or subject colour inside that core.
Opaque chroma recolouring is restricted to the original two-pixel boundary band, preserving vivid green or purple paint inside the subject.
For a visually confirmed key-colour blob inside opaque artwork, `--spill-mask reviewed_mask.png` explicitly selects pixels for interior-colour bleeding; the grayscale mask must match the exact sheet dimensions, with nonzero values only at reviewed spill coordinates.
This opt-in mask does not infer a background or change alpha; retain the mask, source hash and reviewed pixel coordinates as repair evidence.
Each frame is processed separately to prevent colours bleeding across frame boundaries.
`--erosion 0` performs RGB bleeding without shrinking the silhouette when an owner has verified that erosion would damage a very small symbol.
The tool refuses empty subjects, images without transparent unused canvas, interiors too faint to supply reliable colours, and erosion that would erase the subject.
It does not remove opaque mattes, key entire images, unpremultiply colour, restore missing details or boost opacity.
Stray opaque blobs, broad glows, legitimate green objects near the edge, tiny thin lines and badly ghosted subjects need direct visual/source review.

Review the source and processed PNG on dark, light and checker backgrounds at native size and enlarged size before installing any output.
Retain source hashes and the selected processed version; do not run erosion twice on a repaired runtime export.
Recheck subject bounds, alpha and fringes after DDS decoding.
The contact sheet shows the first frame plus the declared frame count; inspect every frame separately for counter or animation acceptance.

## Profiles and counter conventions

Profiles live in `profiles.json`, one row per family with its canvas for new art, its accepted sizes, its minimum margin, its frame count and the vanilla evidence for each number:

| Profile | Canvas for new art | Minimum margin |
|---|---|---|
| category (small icon) | 52x40 | 3 px |
| report | 210x176 | none |
| news | 397x153 | none |
| counter-large | 76x42 per frame, 2 frames | 1 px |
| counter-small | 30x12 per frame, 2 frames | none (vanilla fills the top/bottom) |

Margins are review defaults, not vanilla measurements.
When a mod settles its focus, decision or idea canvases, add a row with `canvas`, `accepted`, `margin`, `frames`, `off_size_level` (`error` or `warning`), `alternative_level` and a `source` naming the decision; `gfx.py families` then checks that family.
`size --profile` accepts any listed size unless `--canvas` overrides it.
`category` means the small category icon, not the separate 114x101 category illustration.
Always inspect the actual consumer; use `--canvas W H` and `--margin N` for a verified exception.
Horizontal strips require `--frames N`; canvas width is checked against the per-frame width multiplied by N.
Margins use alpha at least 16 to disregard negligible shadow tails.
Icon span below 80% of its canvas raises an undersized-art finding.
There is no automatic rescaling or cropping, because that cannot recover a clipped subject.

`counter` is a conservative automated triage check, not proof that the symbol depicts the right unit.
Its default frame count is two, so the returned alpha diagnostics describe both frames separately.
Large frame 1 must follow the muted flat vanilla-green silhouette palette sampled from the supplied reference.
Small frame 1 must predominantly be light grey/white at full opacity.
Frame 2 needs an opaque pale/white NATO field with a black line glyph, distinct from frame 1.
The check catches empty/ghosted subjects, wrong canvases, broad palette mismatches, identical frames and missing white/black structure.
It also compares the largest connected pale/black field's density, footprint and rectangular aspect to vanilla, flagging scattered white/black noise and unboxed glyphs.
Counter opacity and colour-spread comparisons use the supplied reference, since actual vanilla antialiased infantry silhouettes themselves average below 200 alpha.
The separate `alpha` command still reports the requested literal 200 threshold without that adjustment.
It cannot establish a recognizable silhouette, a complete box border, the correct NATO glyph, line weight or a readable support marker; those require native-size visual comparison to the exact vanilla family.
Do not apply this counter rule to unrelated 18x18 inline texticons or division-template emblems.

## DDS contract and shared-tree installation

The 2D writer imports `convert_to_dds.py` from the `asset_tools` folder in `settings.json` and calls its canonical `write_bgra_dds` function.
It writes a legacy 128-byte DDS header, one uncompressed straight-alpha BGRA level, pixel-format block at byte 76 with `RGB | ALPHAPIXELS`, correct BGRA masks and `DDSCAPS_TEXTURE`.
It then validates every header field, exact `128 + width * height * 4` file length, and pixel equality through both strict parsing and Pillow decoding before atomically replacing the reviewed output file.
This writer is for mechanical 2D alpha processing, under the asset skill's explicit exception; general source-art conversion still uses the canonical converter's CLI.
It is not the compressed full-mip BC1/BC3 model-texture pipeline.
It does not resize, change frame counts, generate missing art or alter `.gfx` registrations.

Before installing an output, verify the runtime path still has the recorded source hash and that the owner has not edited it since selection.
Copy only the selected reviewed files; leave unrelated assets and shared registries alone.
Keep sprite names, canvas and frame count stable; edit `.gfx` only when those must change.
Use `hoi4-shared-git-commit` to commit only owned paths and hunks when other work shares the checkout.
Live consumer checks belong to the orchestrator.
