---
name: chaos-redux-event-assets
description: Use when creating, sourcing, processing, converting, organizing, wiring, or documenting visual assets for Chaos Redux.
---

# Chaos Redux Event Assets

Use this skill when a Chaos Redux task requires final visual assets.

This includes event assets, UI assets, focus tree assets, country assets, achievement assets, generated icons, sourced event art, generated icon art, and any asset package that must be prepared for final wiring by the main agent.

## 1. Core purpose

The goal is to turn asset needs from an event spec into real HOI4-ready files.

The asset workflow must produce:

- source artwork
- processed PNG previews
- final DDS files
- correct file placement
- sprite handoff notes for the main agent
- documentation of what was created

Do not leave assets as loose generated or downloaded images.

If an asset is used by the event, it must be processed, placed, documented, and handed off so the main agent can wire it cleanly.

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
- officer corps spirit icons
- focus icons
- achievement icons
- flags
- leader portraits
- faction emblems
- UI panels
- progression-state variants
- any other static visual asset required by a Chaos Redux event or mechanic

Use this skill when the user asks the agent to create, source, process, convert, or prepare final visual assets for wiring.

Use this skill when the implementation task includes generated, sourced, or user-provided PNG files that must be turned into HOI4-ready assets.

## 2.1 Custom subagent split

When actual files must be created, source the work through the narrow project subagents instead of using one broad asset worker.

The main agent decides which subagent to spawn, gives it a bounded asset prompt, reviews the output, and then performs final wiring.

| Asset need | Spawn |
| --- | --- |
| Report event images, news event images, documentary or archival super-event images, real leader portraits, historical flags, historically attested symbols, and user-provided source photos | `chaosx_asset_source_researcher` |
| Fictional, symbolic, supernatural, or fully invented super-event images, fictional portraits, fictional flags, faction emblems, UI panels, dossier art, and progression-state base art | `chaosx_generated_event_art` |
| Focus icons, idea icons, national spirit icons, officer corps spirit icons, decision icons, decision category icons, achievement icons, and tech icons | `chaosx_icon_artist` |

Do not send all asset types to one generic asset worker when the package naturally separates into source-image research, generated event art, and icon work.

Each visual asset subagent may produce:

- source files
- processed PNG previews
- final DDS files
- contact sheets
- manifests
- `docs/assets/<event_id>_<event_slug>/gfx_handoff.md`

The visual asset subagents must not edit:

- `.gfx` files
- localisation files
- GUI files
- event files
- focus tree files
- idea files
- decision files
- scripted effects or scripted triggers
- on_actions
- history files
- country files
- spreadsheets

The main agent owns final `.gfx` sprite definitions, references from gameplay files, docs alignment, spreadsheet alignment, and validation.

A good parent prompt to an asset subagent includes:

- event id and slug
- exact asset list
- asset type for each item
- target size
- source mode
- intended final DDS folder
- proposed sprite name
- reference folder to inspect
- visual direction
- licensing, era-fit, or historical-source constraints
- existing assets to reuse or avoid
- what the subagent must mark as blocked instead of substituting


## 3. Asset source rules

Choose the source mode based on asset type.

### Use `$imagegen` for generated symbolic or fictional assets

Use Codex's official `$imagegen` skill by default for:

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

When creating generated assets, follow the `$imagegen` skill workflow. Do not define a separate image generation route in this skill.

For transparent icons, ask `$imagegen` for the required transparent output and follow the `$imagegen` skill's transparent image workflow. The final PNG must have real transparency, no fake checkerboard, no white halo, no white outline, and no opaque square background unless the asset type explicitly uses a painted backdrop.

If `$imagegen` is unavailable, report that clearly and stop before using an alternate route.

### Use internet source images for event photo assets

Do not generate these asset types with `$imagegen` by default:

- news event images
- report event images
- super-event images

For these asset types, find suitable images from the internet, then process them into the correct HOI4 format.

Follow the repository web research rules from `AGENTS.md` when searching for source images.

For event photo assets that are meant to represent the World War II era, search for period-matching source imagery from roughly 1936 to 1945 unless the event spec gives a narrower date range. Prefer contemporary photographs, war correspondents' photographs, press agency images, propaganda posters, maps, newspapers, official records, government or military archive images, museum scans, library scans, and period illustrations. Do not use modern photographs, reenactment images, film stills, AI-looking reconstructions, postwar uniforms, streets, weapons, vehicles, buildings, colorized tourist photos, reenactments, or modern props when they do not fit the era. If no suitable period source can be found, mark the asset as blocked or `needs_user_review` instead of substituting a modern image.

Record the image source, source link, author or archive if available, license or public domain status if available, estimated date or date range, why the image fits the World War II era, and any uncertainty in the manifest.

### Real leader portraits

Do not generate a leader portrait for a real person.

For real people, use a real source image from the internet or a user-provided image, then crop, resize, process, convert, and document it. Use the repository web research tools when a source image is needed, and prefer public domain, archival, official, or clearly licensed images. If the person belongs to the World War II setting, prefer contemporary portraits, wartime photographs, news photographs, official portraits, military archive images, passport or identity photos, or archival illustrations. Do not use modern actors, reenactors, statues, cosplay, later fictional depictions, postwar images, or modern images that do not fit the era unless the user explicitly approves them as placeholders.

Real leader portraits should be processed toward the HOI4 portrait style rather than left as raw photos: bust or upper-torso crop, face readable, subdued contrast, mild painterly or period texture, HOI4-like color grading, no modern UI artifacts, no hard white cutout halo, and no over-smoothed face. Do not change the person's identity or generate missing facial features.

Record the source link, author or archive if available, license or public domain status if available, source image path, processed PNG path, final DDS path, and sprite name

### Fictional leader portraits

Fictional leaders, invented councils, collective bodies, supernatural leaders, and symbolic regime portraits may use `$imagegen`.

Generated leader portraits should follow HOI4 leader portrait conventions: 156x210 final DDS unless an existing sprite uses another size, bust or upper-torso framing, strong face or governing-body focal point, subdued painterly finish, period-appropriate uniform or civilian clothing, transparent or HOI4-compatible portrait background as required by the existing asset pattern, and no text, labels, watermarks, modern UI, or meme-like exaggeration.

For council or collective leaders, use one clear symbolic council portrait rather than a cluttered crowd. Keep the subject readable at leader portrait size and document that the leader is fictional or collective.

### User-provided assets

If the user provides an image, treat it as a source asset.

Record that the image was user-provided in the manifest.

Still crop, resize, convert, place, wire, and document it like any other source asset.

## 4. Reference asset examples

This skill includes reference images that show how different Chaos Redux asset types should look.

Before generating, sourcing, processing, or wiring an asset, inspect the relevant reference folder for that asset type. Use the examples to match style, framing, contrast, readability, scale, texture, and HOI4 presentation.

Use Linux project paths, not Windows UNC paths:

```text
~/projects/chaos_redux/.agents/skills/chaos-redux-event-assets/assets/ideas
~/projects/chaos_redux/.agents/skills/chaos-redux-event-assets/assets/news_event_images
~/projects/chaos_redux/.agents/skills/chaos-redux-event-assets/assets/report_event_images
~/projects/chaos_redux/.agents/skills/chaos-redux-event-assets/assets/super_event_images
~/projects/chaos_redux/.agents/skills/chaos-redux-event-assets/assets/tech_icons
~/projects/chaos_redux/.agents/skills/chaos-redux-event-assets/assets/achievements
~/projects/chaos_redux/.agents/skills/chaos-redux-event-assets/assets/decisions
~/projects/chaos_redux/.agents/skills/chaos-redux-event-assets/assets/flags
~/projects/chaos_redux/.agents/skills/chaos-redux-event-assets/assets/focuses
```

Reference mapping:

- idea and national spirit icons: `assets/ideas`
- officer corps spirit icons: inspect vanilla `gfx/interface/officer_corp/spirits/`. Final assets should be 45x45 DDS files with transparent backgrounds, no frames, no painted backdrop, no full-canvas opaque pixels, a readable dark or black outline, and a slight drop shadow. Wire them as `GFX_idea_<spirit_id>` sprites from a `.gfx` file.
- news event images: `assets/news_event_images`
- report event images: `assets/report_event_images`
- super-event images: `assets/super_event_images`
- tech icons: `assets/tech_icons`
- achievement icons: `assets/achievements`
- decision and decision category icons: `assets/decisions`
- flags: `assets/flags`
- focus icons: `assets/focuses`

If a relevant reference folder exists, do not generate, source, crop, process, or wire new artwork until you have inspected it.

Do not copy reference assets directly unless the user explicitly allows it. Use them as style and formatting guidance.

If the needed asset type has no matching reference folder, inspect the closest relevant folder and existing Chaos Redux or vanilla assets before choosing a style.

## 5. Generated artwork rules

Do not create core artwork from simple shapes, placeholders, contact sheets, layout-only mockups, empty UI boxes, or generated charts.

Use `$imagegen` for generated artwork and follow the `$imagegen` skill workflow for the source image.

Generated artwork must be real source art that can be processed into the final game asset. Do not use contact sheets, review boards, or layout drafts as final source art.

## 5.1 Icon creation rules

Small gameplay icons must be readable at their final in-game size.

- Use transparent backgrounds for asset types that are transparent in vanilla, especially officer corps spirit icons and small symbolic interface icons.
- Keep unused pixels fully transparent. Do not leave a square opaque fill behind icons unless the asset type explicitly uses a painted frame or backdrop.
- Give the icon silhouette a dark or black outline and a subtle drop shadow when the icon is displayed over variable UI backgrounds.
- Avoid tiny interior detail that disappears at 45x45 or 64x64. Favor one clear subject, strong value contrast, and a centered silhouette.
- Officer corps spirit icons specifically must be 45x45, transparent, unframed, and visually similar to vanilla officer corps spirit icons rather than national spirit cards.
- Avoid fake checkerboard pixels, white halos, white outlines, oversized medallion fills, and square opaque backdrops.

For every generated icon, follow the `$imagegen` skill's transparent image workflow. This skill must not provide its own transparency cleanup method. Preserve the original generated image, create a processed PNG preview, convert to DDS, and validate the final appearance over a checker background before treating the icon as complete.

The final icon should have transparent unused canvas, no fake checker or matte pixels, no transparent holes inside the painted subject, a slight black outline, a subtle drop shadow, and a centered subject that remains readable at final size.

## 6. Required asset workflow

For every asset package:

1. Read the event spec, asset prompt, or implementation task.
2. Identify every required visual asset.
3. Group assets by usage type.
4. Assign each asset a stable filename.
5. Assign each asset a sprite name if it needs one.
6. Identify the target size.
7. Identify the intended in-game use.
8. Inspect the matching reference folder from section 4 before generating, sourcing, processing, or wiring the asset.
9. Decide the source mode for each asset:
   - `$imagegen`
   - internet source image
   - user-provided source image
10. For `$imagegen` assets, write a specific image generation prompt and create the base artwork by following the official `$imagegen` skill.
11. For internet-sourced assets, find a suitable source image and record its source link, author or archive if available, and license or public domain status if available.
12. For user-provided assets, record that the image was provided by the user.
13. Save the original generated, sourced, or provided image as a source PNG.
14. Crop and resize the image to the target size. For report event images, normalize the source to `210x176` before placing it into the Photoshop report-event template.
15. Save a processed PNG preview. For report event images, this preview is the Photoshop-exported `210x176` PNG with the fixed report box and sepia treatment.
16. Convert the processed PNG to DDS 32 bit unsigned BGRB 8.8.8.8.
17. Move the DDS into the correct mod folder.
18. Create or update the asset manifest.
19. Create or update `gfx_handoff.md` for the main agent.
20. Update event docs when they list asset expectations.
21. Report all created files and any blocked assets.

Do not mark assets complete until the DDS files exist, the manifest is written, and `gfx_handoff.md` gives the main agent enough information to wire the sprite without guessing.

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
- source mode: `$imagegen`, internet source image, or user-provided source image
- image generation prompt if generated with `$imagegen`
- source link if internet-sourced
- source author, archive, or collection if available
- source date or estimated date range if internet-sourced
- license or public domain status if available
- era-fit note for World War II-era assets
- source PNG path
- processed PNG path
- final DDS path
- target size
- sprite name
- `.gfx` file
- localisation key if relevant
- related focus, idea, event, decision, UI element, or super-event if relevant
- notes
- asset status

Use `not_needed`, `planned`, `sourced`, `generated`, `processed`, `converted`, `wired`, `complete`, or `blocked` as asset statuses.

For large focus trees that deliberately reuse branch-level icon sprites instead of unique art for every focus, create a separate reuse ledger under the asset package. The ledger must be based on the actual focus file, state the real focus count, map each branch sprite to its final DDS and reuse rationale, and either list every focus or provide branch counts that can be verified from the tree. Do not treat branch-level reuse as complete unless the `.gfx` sprites are wired and the manifest links to that ledger.

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

Use other sizes when the event's UI or asset type requires it.

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

Every `$imagegen` prompt should be specific enough to produce usable game art.

A good prompt should include:

- asset type
- target in-game use
- subject
- visual style
- readability requirements
- what must be avoided
- whether the result must be readable at small size

Do not ask for vague "cool icon" style outputs.

Do not rely on text inside generated images. Generated text is unreliable.

Prefer strong symbols, clear silhouettes, and readable composition.

For transparent icon prompts, explicitly request a transparent canvas, no fake checkerboard, no white rim, no white outline, no glow, no sticker border, no opaque square background, and a clean silhouette suitable for HOI4 UI.

## 12. Internet source image rules

When using internet source images:

1. Search for images that fit the event tone, target use, and intended era.
2. For World War II-era event assets, search for source images from roughly 1936 to 1945 unless the event spec gives a narrower date range.
3. Prefer contemporary or near-contemporary public domain, archival, official, museum, library, newspaper, map, press photograph, propaganda poster, government record, military record, period illustration, or clearly licensed sources.
4. Reject modern photographs, reenactments, film stills, postwar streets, uniforms, props, weapons, vehicles, buildings, AI-looking reconstructions, and later stylized images when they do not fit the era.
5. Record source links, source date or estimated date range, and license or public domain status when available.
6. If licensing, date, or era fit is unclear, mark it as uncertain in the manifest.
7. Process the image into the correct HOI4 size and style.
8. Preserve the source image path and processed preview path.

For public-facing or uncertain assets, keep the manifest honest about the source status, date uncertainty, and World War II-era fit uncertainty.

## 13. Report event images

Report event images should use internet source images by default.

Do not generate report event images with `$imagegen` unless the user explicitly asks for a fictional or symbolic report image.

Report event images should look like documentary-style photographs, field documentation, or period documentary material.

For World War II-era subjects, prefer contemporary photographs, war correspondents' photographs, press agency images, propaganda posters, newspapers, maps, official records, military archive images, museum or library scans, or period illustrations. Do not use modern reenactment photos or modern documentary photos that visually belong to a later era.

Use:

- realistic or period-authentic source imagery
- World War II-era visual fit when the event belongs to that era
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

### Report event Photoshop template

Report event images must use the fixed Photoshop report-event template. If for some reason you can't use the Photoshop app, report it clearly and leave the final report image status as `Requires user's intervention!`.

Template path:

```text
.tools/report_event_template.psd
```

Workflow:

1. Source or receive the report-event image.
2. Crop or resize the source to exactly `210x176` before opening or placing it in Photoshop.
3. Place or replace it into `REPORT_SOURCE_IMAGE_REPLACE_ME__210x176_AT_0_0`.
4. Keep placement at `x = 0`, `y = 0`. Do not move, scale, stretch, or offset the source inside Photoshop.
5. Keep the fixed slight sepia layer enabled.
6. Keep the fixed report-event box and frame layers unchanged.
7. Export the full canvas as a `210x176` PNG.
8. Convert the exported PNG to final DDS through the repository DDS conversion workflow.
9. Record the PSD template path, source PNG path, exported PNG path, final DDS path, and any Photoshop/template uncertainty in the manifest.

Do not rebuild the report-event frame from flattened layers. If the Photoshop app or PSD editor cannot preserve the template layers, mark the asset blocked instead of inventing a substitute template.

## 14. News event images

News event images should use internet source images by default.

Do not generate news event images with `$imagegen` unless the user explicitly asks for a fictional or symbolic news image.

News images should look like black-and-white documentary photographs or period news illustrations.

For World War II-era subjects, prefer contemporary newspapers, news photographs, war correspondents' photographs, press agency images, propaganda posters, maps, official visual records, military archive images, museum or library scans, or period illustrations. Do not use modern reenactment photos, modern news photos, film stills, or later images that do not fit the era.

Use:

- old news photograph or period press illustration style
- World War II-era visual fit when the event belongs to that era
- clear central subject
- strong contrast
- period-appropriate composition
- no modern UI overlays
- no modern clothing, streets, weapons, vehicles, buildings, or props unless they are intentionally part of the event
- no generated text

Target size:

```text
397x153
```

News images must be black and white.

Record the source link and license or public domain status if available.

## 15. Super-event images

Super-event images should use internet source images by default.

Do not generate super-event images with `$imagegen` unless the user explicitly asks for fictional, symbolic, supernatural, or fully invented super-event art.

Super-event images should have:

- strong central composition
- clear dramatic theme
- readable subject
- enough contrast for HOI4 UI
- World War II-era visual fit when the event belongs to that era
- no generated text
- no modern clothing, streets, weapons, vehicles, buildings, props, film stills, or reenactment imagery when they do not fit the era
- no cluttered small details that disappear at final size

Target size:

```text
457x328
```

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

Use `$imagegen` for the base artwork unless the user provides or requests a specific source image.

Follow the `$imagegen` skill's transparent image workflow when the icon should have a transparent background.

Inspect `~/projects/chaos_redux/.agents/skills/chaos-redux-event-assets/assets/ideas` before generating or processing idea icons.

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

Do not make focus icons look like generic generated thumbnails.

Every focus icon should support the focus tree's story, ideology, or gameplay purpose.

Use `$imagegen` for the base artwork unless the user provides or requests a specific source image.

Follow the `$imagegen` skill's transparent image workflow when the icon should have a transparent background.

Inspect `~/projects/chaos_redux/.agents/skills/chaos-redux-event-assets/assets/focuses` before generating or processing focus icons.

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

Use `$imagegen` for the base artwork unless the user provides or requests a specific source image.

Follow the `$imagegen` skill's transparent image workflow when the icon should have a transparent background.

Inspect `~/projects/chaos_redux/.agents/skills/chaos-redux-event-assets/assets/decisions` before generating or processing decision icons.

## 19. Achievement icons

Achievement icons should be compact and readable at 64x64.

Generate the completed achievement icon first with `$imagegen`.

Then create:

- grey variant
- not-eligible variant

The variants may be created after the completed icon exists.

Target size:

```text
64x64
```

Use `achievement_` filename prefix.

Inspect `~/projects/chaos_redux/.agents/skills/chaos-redux-event-assets/assets/achievements` before generating or processing achievement icons.

## 20. Flags

Flags should use clean symbolic designs.

They must remain readable at HOI4 sizes.

Required flag sizes:

- small: 10x7
- medium: 42x26
- normal: 82x52

Avoid overly detailed symbols.

Avoid generated text unless the design absolutely requires it and the final output is manually checked.

Use `$imagegen` for fictional flags and user-provided or internet source images for historical or real-world flags when appropriate.

## 21. Leader portraits

For real people, do not generate leader portraits with `$imagegen`.

Use a real source image from the internet or a user-provided image, then crop, resize, process, convert, and document it.

Record:

- source link if internet-sourced
- author or archive if available
- license or public domain status if available
- original image path
- processed PNG path
- final DDS path

For fictional people, non-human beings, supernatural entities, aliens, zombies, monsters, symbolic leaders, or other invented characters, `$imagegen` may be used to create the base portrait.

Leader portraits should match the intended Chaos Redux visual direction for the character or country.

Target size:

```text
156x210
```

Inspect the closest relevant reference folder and existing Chaos Redux portraits before generating or processing fictional leader portraits.

## 22. UI panels and custom windows

For UI panels, dossier windows, ledgers, investigation boards, and similar assets, separate artwork from functional UI.

Use `$imagegen` for:

- illustrated background panels
- thematic decorations
- symbolic seals
- propaganda visuals
- report board visual elements

Use normal UI editing for:

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

Final PNG assets must be converted to DDS using the repository's standard DDS conversion workflow.

The output must be compatible with Chaos Redux's expected 32-bit BGRA or B8G8R8A8-style DDS workflow.

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

## 25. `.gfx` handoff and main-agent wiring

Asset subagents do not edit `.gfx` files.

When an asset needs a sprite definition, the asset package must include a handoff note for the main agent.

Recommended path:

```text
docs/assets/<event_id>_<event_slug>/gfx_handoff.md
```

The handoff must include:

1. Final DDS path.
2. Proposed sprite name.
3. Suggested target `.gfx` file.
4. Ready-to-copy sprite definition snippet when useful.
5. Related localisation key, GUI element, event id, focus id, idea id, decision id, achievement id, or super-event slot when known.
6. Any uncertainty about sprite naming or target file placement.
7. Any blocked or needs-review asset.

The main agent must then:

1. Find the correct existing `.gfx` file if one exists.
2. Follow the existing naming and formatting pattern.
3. Add the sprite definition.
4. Point the texture file to the final DDS path.
5. Keep sprite names stable.
6. Update localisation, GUI, event, focus, idea, or decision references that use the sprite.
7. Update docs and spreadsheet rows when relevant.

Do not create a new `.gfx` file if an existing one is clearly the right place. If a new `.gfx` file is needed, the main agent must name it consistently and document why.
## 26. Documentation updates

When generated or sourced assets are part of an event or mechanic, update the relevant docs.

The docs should mention:

- what assets exist
- where the DDS files live
- which `.gfx` file the main agent should use or has used
- which sprite names are used
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

## 28. Handling blocked assets

If an asset cannot be created or processed cleanly, mark it as blocked.

Record:

- asset name
- reason blocked
- what was attempted
- what is needed from the user
- whether implementation can continue without it

Do not invent a substitute asset unless the user explicitly approves it.

## 29. Final checklist

Before finishing, confirm:

1. Every required asset from the event spec is accounted for.
2. Every asset uses the correct source mode: `$imagegen` for generated symbolic or fictional assets, internet source images for news/report/super-event images, and real source images for real leader portraits.
3. The matching reference folder from section 4 was inspected before generation, sourcing, processing, or wiring.
4. Every generated, sourced, or provided asset has a source PNG.
5. Every final asset has a processed PNG preview.
6. Every final asset has a DDS output.
7. DDS files use 32 bit unsigned BGRB 8.8.8.8.
8. DDS files are moved into the correct mod folders.
9. A `gfx_handoff.md` exists for every asset that needs a sprite definition, and the main agent has enough information to wire it.
10. The asset manifest exists.
11. Internet-sourced assets record source links, source date or estimated date range, license or public domain status if available, and era-fit notes for World War II-era assets.
12. Fictional or non-human portraits generated with `$imagegen` are clearly marked as fictional or generated in the manifest.
13. Docs are updated where relevant.
14. The event implementation or parent handoff knows which sprite names to use.
15. No final asset remains only in a temporary folder.
