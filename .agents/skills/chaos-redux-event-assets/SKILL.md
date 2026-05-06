---
name: chaos-redux-event-assets
description: Use when creating, sourcing, processing, converting, organizing, wiring, or documenting visual assets for Chaos Redux.
---

# Chaos Redux Event Assets

Use this skill when a Chaos Redux task requires final visual assets.

This includes event assets, UI assets, focus tree assets, country assets, achievement assets, generated icons, sourced event art, generated icon art, and any asset package that must be wired into the mod.

## 1. Core purpose

The goal is to turn asset needs from an event spec into real HOI4-ready files.

The asset workflow must produce:

- source artwork
- processed PNG previews
- final DDS files
- correct file placement
- `.gfx` sprite definitions
- documentation of what was created

Do not leave assets as loose generated or downloaded images.

If an asset is used by the event, it must be processed, placed, wired, and documented.

## 2. When to use this skill

Use this skill for:

- event pictures
- report event pictures
- news event pictures
- super-event images
- decision icons
- decision category icons
- idea icons
- national spirit icons
- focus icons
- achievement icons
- flags
- leader portraits
- faction emblems
- UI panels
- progression-state variants
- any other static visual asset required by a Chaos Redux event or mechanic

Use this skill when the user asks the agent to create, source, process, or wire final visual assets.

Use this skill when the implementation task includes generated, sourced, or user-provided PNG files that must be turned into HOI4-ready assets.

## 3. Asset source rules

Choose the source mode based on asset type.

### Use `image_gen` for generated symbolic or fictional assets

Use Codex's official built-in `image_gen` tool by default for:

- idea icons
- focus icons
- decision icons
- decision category icons
- achievement icons
- fictional flags
- faction emblems
- fictional leader portraits
- UI panels
- progression-state base art
- other symbolic or fictional static assets

Do not use an image generation MCP, API script, or CLI fallback by default.

If built-in `image_gen` is unavailable, report that clearly and ask before using a fallback route.

### Use internet source images for event photo assets

Do not generate these asset types with `image_gen` by default:

- news event images
- report event images
- super-event images

For these asset types, find suitable images from the internet, then process them into the correct HOI4 format.

Follow the repository web research rules from `AGENTS.md` when searching for source images.

Record the image source, source link, author or archive if available, license or public domain status if available, and any uncertainty in the manifest.

Report event images and super-event images must be marked for user review before they are treated as final.

### Real leader portraits

Do not generate a leader portrait for a real person.

For real people, use a real source image from the internet or a user-provided image, then crop, resize, process, convert, and document it.

Record the source link, author or archive if available, and license or public domain status if available.

### User-provided assets

If the user provides an image, treat it as a source asset.

Record that the image was user-provided in the manifest.

Still crop, resize, convert, place, wire, and document it like any other source asset.

## 4. Reference asset folder

This skill folder contains an `assets/` folder with reference images for how different asset types should look.

Before creating or processing an asset, inspect the relevant reference examples when they exist.

Reference examples may include:

- achievement icons
- focus icons
- idea icons
- decision icons
- leader portraits
- flags
- event images
- news images
- report images
- super-event images
- UI elements

Use these references to match style, framing, contrast, readability, and HOI4 presentation.

Do not copy reference assets directly unless the user explicitly allows it. Use them as style and formatting guidance.

## 5. No core artwork with scripts

Do not create core artwork with:

- Python drawing
- simple geometric shapes
- flat placeholder symbols
- contact-sheet mockups
- layout-only mockups
- basic generated charts
- empty UI boxes with no real art

Python or scripts may only be used after the source image exists for:

- cropping
- resizing
- organizing files
- creating manifests
- creating contact sheets
- creating achievement state variants
- creating progression-state variants
- converting final assets to DDS

## 6. Required asset workflow

For every asset package:

1. Read the event spec, asset prompt, or implementation task.
2. Identify every required visual asset.
3. Group assets by usage type.
4. Assign each asset a stable filename.
5. Assign each asset a sprite name if it needs one.
6. Identify the target size.
7. Identify the intended in-game use.
8. Inspect relevant examples in the skill `assets/` folder when they exist.
9. Decide the source mode for each asset:
   - `image_gen`
   - internet source image
   - user-provided source image
10. For `image_gen` assets, write a specific image generation prompt and generate the base artwork with Codex's official built-in `image_gen` tool.
11. For internet-sourced assets, find a suitable source image and record its source link, author or archive if available, and license or public domain status if available.
12. For user-provided assets, record that the image was provided by the user.
13. Save the original generated, sourced, or provided image as a source PNG.
14. Crop and resize the image to the target size.
15. Save a processed PNG preview.
16. Convert the processed PNG to DDS 32 bit unsigned BGRB 8.8.8.8.
17. Move the DDS into the correct mod folder.
18. Add or update the matching sprite definition in the correct `.gfx` file.
19. Create or update the asset manifest.
20. Update event docs when they list asset expectations.
21. Report all created files and any blocked assets.

Do not mark assets complete until the DDS files exist, the sprite definitions are wired, and the manifest is written.

Report event images and super-event images are not final until the user has reviewed them.

## 7. Asset package structure

When creating a new asset package, use a stable working folder.

Recommended working structure:

```text
docs/assets/<event_id>_<event_slug>/
  manifest.md
  prompts/
  source_png/
  processed_png/
  contact_sheets/
  notes/
```

Final DDS files must be moved into the correct gameplay asset folders.

Do not keep final assets under `docs/assets/`.

## 8. Manifest requirements

Every asset package must include a markdown manifest.

Recommended path:

```text
docs/assets/<event_id>_<event_slug>/manifest.md
```

The manifest must list every asset.

Each asset entry should include:

- asset name
- related event id
- related event slug
- asset type
- intended in-game use
- source mode: `image_gen`, internet source image, or user-provided source image
- image generation prompt if generated with `image_gen`
- source link if internet-sourced
- source author, archive, or collection if available
- license or public domain status if available
- source PNG path
- processed PNG path
- final DDS path
- target size
- sprite name
- `.gfx` file
- localisation key if relevant
- related focus, idea, event, decision, UI element, or super-event if relevant
- review status: `not_needed`, `needs_user_review`, `approved`, or `rejected`
- notes
- asset status

Use `not_needed`, `planned`, `sourced`, `generated`, `processed`, `converted`, `wired`, `complete`, or `blocked` as asset statuses.

## 9. Standard HOI4 asset sizes

Use these sizes unless the event spec or an existing repo pattern gives a better project-specific requirement.

- report event images: 210x176
- news event images: 397x153, black and white
- leader portraits: 156x210
- flags small: 10x7
- flags medium: 42x26
- flags normal: 82x52
- tech icons small: 64x64
- tech icons medium: 132x52
- achievements: 64x64
- super-event images: 457x328
- decision icons: 32x32
- idea and national spirit icons: 64x64
- focus icons: 94x86

Use other sizes when the event’s UI or asset type requires it.

When unsure, inspect the existing Chaos Redux pattern and vanilla HOI4 assets before choosing.

## 10. Naming rules

Use lowercase snake_case.

Keep names stable once they are wired into `.gfx`.

Recommended filename prefixes:

- idea icons: `idea_`
- focus icons: `goal_`
- decision icons: `decision_`
- decision category icons: `decision_category_`
- report event images: `report_event_`
- news event images: `news_event_`
- super-event images: `super_event_`
- achievement icons: `achievement_`
- leader portraits: `leader_`

For event-specific assets, include the event id or slug where useful.

## 11. Image generation prompt rules

Every `image_gen` prompt should be specific enough to produce usable game art.

A good prompt should include:

- asset type
- target in-game use
- subject
- visual style
- readability requirements
- what must be avoided
- whether the result must be readable at small size

Do not ask for vague “cool icon” style outputs.

Do not rely on text inside generated images. Generated text is unreliable.

Prefer strong symbols, clear silhouettes, and readable composition.

## 12. Internet source image rules

When using internet source images:

1. Search for images that fit the event tone and target use.
2. Prefer public domain, archival, official, or clearly licensed sources.
3. Record source links and license or public domain status when available.
4. If licensing is unclear, mark it as uncertain in the manifest.
5. Process the image into the correct HOI4 size and style.
6. Preserve the source image path and processed preview path.

For public-facing or uncertain assets, keep the manifest honest about the source status.

## 13. Report event images

Report event images should use internet source images by default.

Do not generate report event images with `image_gen` unless the user explicitly asks for a fictional or symbolic report image.

Report event images should look like documentary-style photographs or field documentation.

Use:

- realistic source imagery
- period-appropriate framing where possible
- strong subject clarity
- natural composition
- no modern UI overlays
- no generated text

Target size:

```text
210x176
```

Use colour unless the event spec asks otherwise.

Report event images must be marked `needs_user_review` in the manifest before being treated as final.

## 14. News event images

News event images should use internet source images by default.

Do not generate news event images with `image_gen` unless the user explicitly asks for a fictional or symbolic news image.

News images should look like black-and-white documentary photographs.

Use:

- old news photograph style
- clear central subject
- strong contrast
- period-appropriate composition
- no modern UI overlays
- no generated text

Target size:

```text
397x153
```

News images must be black and white.

Record the source link and license or public domain status if available.

## 15. Super-event images

Super-event images should use internet source images by default.

Do not generate super-event images with `image_gen` unless the user explicitly asks for fictional, symbolic, supernatural, or fully invented super-event art.

Super-event images should have:

- strong central composition
- clear dramatic theme
- readable subject
- enough contrast for HOI4 UI
- no generated text
- no cluttered small details that disappear at final size

Target size:

```text
457x328
```

Super-event images must be marked `needs_user_review` in the manifest before being treated as final.

If a super-event needs music, research suitable public domain or clearly licensed music.

For each track, document:

- title
- composer
- performer or recording source if relevant
- public domain status or license status
- source link
- why it fits
- suggested in-game use
- editing notes

Do not claim public domain status without checking.

If the license is unclear, mark it as uncertain or unsuitable.

## 16. Idea and national spirit icons

Idea and national spirit icons should look like compact HOI4-style icon art.

They should have:

- strong central symbol
- clear silhouette
- aged texture
- strong contrast
- readable meaning at 64x64
- no generated text

Target size:

```text
64x64
```

Use `idea_` filename prefix.

These icons usually do not need the full focus icon frame.

Use `image_gen` for the base artwork unless the user provides or requests a specific source image.

Inspect the skill reference assets for idea icons when available.

## 17. Focus icons

Focus icons should look like normal HOI4 focus icons.

They should have:

- strong central symbol
- clear silhouette
- aged texture
- painterly detail
- readable contrast
- meaningful relation to the focus
- no generated text

Target size:

```text
94x86
```

Use `goal_` filename prefix.

Do not make focus icons look like generic AI art thumbnails.

Every focus icon should support the focus tree’s story, ideology, or gameplay purpose.

Use `image_gen` for the base artwork unless the user provides or requests a specific source image.

Inspect the skill reference assets for focus icons when available.

## 18. Decision icons

Decision icons must remain readable at very small size.

Use:

- simple symbolic composition
- strong contrast
- clear central shape
- limited small detail
- no generated text

Target size:

```text
32x32
```

Use `decision_` filename prefix.

Decision category icons may use:

```text
decision_category_
```

Use `image_gen` for the base artwork unless the user provides or requests a specific source image.

Inspect the skill reference assets for decision icons when available.

## 19. Achievement icons

Achievement icons should be compact and readable at 64x64.

Generate the completed achievement icon first with `image_gen`.

Then create:

- grey variant
- not-eligible variant

The variants may be created with scripting or image editing after the completed icon exists.

Target size:

```text
64x64
```

Use `achievement_` filename prefix.

Inspect the skill reference assets for achievement icons when available.

## 20. Flags

Flags should use clean symbolic designs.

They must remain readable at HOI4 sizes.

Required flag sizes:

- small: 10x7
- medium: 42x26
- normal: 82x52

Avoid overly detailed symbols.

Avoid generated text unless the design absolutely requires it and the final output is manually checked.

Use `image_gen` for fictional flags and user-provided or internet source images for historical or real-world flags when appropriate.

## 21. Leader portraits

For real people, do not generate leader portraits with `image_gen`.

Use a real source image from the internet or a user-provided image, then crop, resize, process, convert, and document it.

Record:

- source link if internet-sourced
- author or archive if available
- license or public domain status if available
- original image path
- processed PNG path
- final DDS path

For fictional people, non-human beings, supernatural entities, aliens, zombies, monsters, symbolic leaders, or other invented characters, `image_gen` may be used to create the base portrait.

Leader portraits should match the intended Chaos Redux visual direction for the character or country.

Target size:

```text
156x210
```

Inspect the skill reference assets for leader portraits when available.

## 22. UI panels and custom windows

For UI panels, dossier windows, ledgers, investigation boards, and similar assets, separate artwork from functional UI.

Use `image_gen` for:

- illustrated background panels
- thematic decorations
- symbolic seals
- propaganda visuals
- report board visual elements

Use scripts or UI editing for:

- exact layout slicing
- cropping
- button states
- state variants
- meter fills
- final export preparation

Do not let generated art decide exact interactive layout.

The implementation must still follow HOI4 UI rules and existing repo patterns.

## 23. Progression-state variants

Progression-state variants may include:

- selected
- dim
- active
- inactive
- locked
- completed
- rejected
- damaged
- corrupted
- urgent
- meter-fill
- bar-fill

Progression-state variants should use the same target size as the base asset.

## 24. DDS conversion

Final PNG assets must be converted with the repo wrapper:

```text
.tools/convert_to_dds.py
```

Use:

```bash
python3 .tools/convert_to_dds.py \
  --input <processed_png_path> \
  --output <final_dds_path> \
  --width <target_width> \
  --height <target_height>
```

Do not call DDS converters directly from event or asset tasks. Always use the wrapper so the command stays the same across machines.

The wrapper is responsible for choosing the available backend on the current system.

Backend expectations:

- On WSL, the wrapper may use DirectXTex `texconv`, usually through a Windows `texconv.exe` path such as `TEXCONV_EXE` or `TEXCONV_PATH`.
- On macOS, the wrapper may use its built-in pure Python DDS writer, or another explicitly configured backend if available.

The output must be compatible with Chaos Redux’s expected 32-bit BGRA / B8G8R8A8-style DDS workflow.

If conversion fails, stop and report the error. Do not invent another conversion route unless the user approves it.

After conversion, confirm that:

- the DDS exists
- the dimensions are correct
- the background is transparent for icons
- the filename is stable
- the file is in the correct mod folder
- the `.gfx` path points to the DDS
- the manifest records the final path

Do not leave only PNG files when the game expects DDS.

## 25. `.gfx` wiring

When an asset needs a sprite definition:

1. Find the correct existing `.gfx` file if one exists.
2. Follow the existing naming and formatting pattern.
3. Add the sprite definition.
4. Point the texture file to the final DDS path.
5. Keep sprite names stable.
6. Update any localisation, GUI, event, focus, idea, or decision references that use the sprite.

Do not create a new `.gfx` file if an existing one is clearly the right place.

If a new `.gfx` file is needed, name it consistently and document why.

## 26. Documentation updates

When generated or sourced assets are part of an event or mechanic, update the relevant docs.

The docs should mention:

- what assets exist
- where the DDS files live
- which `.gfx` file defines them
- which sprite names are used
- which assets need user review, if any
- which assets are placeholders, if any
- what still needs final art, if anything

Do not leave the docs describing old or missing assets.

## 27. Contact sheets

When an asset package contains many generated or sourced images, create a contact sheet for review.

Contact sheets are for review only.

Do not use contact sheets as final game assets.

The contact sheet should make it easy to see:

- asset name
- asset type
- selected final version
- rejected alternatives if relevant
- review status if relevant

## 28. Handling blocked assets

If an asset cannot be created or processed cleanly, mark it as blocked.

Record:

- asset name
- reason blocked
- what was attempted
- what is needed from the user
- whether implementation can continue without it

Do not invent a fallback asset unless the user explicitly approves it.

## 29. Final checklist

Before finishing, confirm:

1. Every required asset from the event spec is accounted for.
2. Every asset uses the correct source mode: `image_gen` for generated symbolic or fictional assets, internet source images for news/report/super-event images, and real source images for real leader portraits.
3. Relevant examples in the skill `assets/` folder were inspected when available.
4. Every generated, sourced, or provided asset has a source PNG.
5. Every final asset has a processed PNG preview.
6. Every final asset has a DDS output.
7. DDS files use 32 bit unsigned BGRB 8.8.8.8.
8. DDS files are moved into the correct mod folders.
9. Sprite definitions are added or updated.
10. The asset manifest exists.
11. Internet-sourced assets record source links and license or public domain status if available.
12. Report event images and super-event images are marked for user review before final use.
14. Fictional or non-human portraits generated with `image_gen` are clearly marked as fictional or generated in the manifest.
15. Docs are updated where relevant.
16. The event implementation knows which sprite names to use.
17. No final asset remains only in a temporary folder.