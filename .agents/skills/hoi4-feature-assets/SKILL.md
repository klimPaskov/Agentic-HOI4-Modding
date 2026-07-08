---
name: hoi4-feature-assets
description: Use when creating, sourcing, processing, converting, organizing, wiring, or documenting visual assets for a Hearts of Iron IV mod.
---

# HOI4 Feature Assets

Use this skill when a HOI4 modding task requires final visual assets.

This includes event pictures, UI assets, focus tree assets, country assets, achievement assets, generated icons, sourced feature art, generated icon art, animated sprites, animated portraits, sprite sheets, GIF previews, and any asset package that must be wired into the mod.

## 1. Core purpose

The goal is to turn asset needs from a feature spec into real HOI4-ready files.

The asset workflow must produce:

- source artwork
- processed PNG previews
- final DDS files
- correct file placement
- sprite handoff notes for the main agent
- documentation of what was created

Do not leave assets as loose generated or downloaded images.

If an asset is used by the feature, it must be processed, placed, documented, and handed off so the main agent can wire it cleanly.

## 2. When to use this skill

Use this skill for:

- event pictures
- report event pictures
- news event pictures
- custom feature images
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
- animated sprites
- animated UI pieces
- animated leader portraits
- sprite sheets and GIF previews for review
- any other static or animated visual asset required by a feature or mechanic

Use this skill when the user asks the agent to create, source, process, or wire final visual assets.

Use this skill when the implementation task includes generated, sourced, or user-provided PNG files that must be turned into HOI4-ready assets.

Use `hoi4-frame-animation` together with this skill when an asset needs animation. Animated final assets must come from planned source frames, not from moving, scaling, rotating, warping, blurring, recoloring, or filtering one still image.


## 2.1 Custom subagent split

When actual files must be created, route the work through narrow project subagents instead of one broad asset worker.

The main agent decides which subagent to spawn, gives it a bounded asset prompt, reviews the output, and performs final wiring.

Use:

- `hoi4_asset_source_researcher` for real or archival image sourcing, real leader portraits, historical flags, historically attested symbols, user-provided source photos, and report, news, or custom feature images that must depict a real photographed person, place, object, or historical document
- `hoi4_generated_feature_art` for generated non-icon feature art, including fictional or alternate-history report images, news images, custom feature images, fictional portraits, fictional flags, faction emblems, UI panels, dossier art, and progression-state base art
- `hoi4_icon_artist` for focus icons, idea icons, national spirit icons, officer corps spirit icons, decision icons, decision category icons, achievement icons, and tech icons

For animated work, route by asset type first. Then require the chosen asset subagent to follow `hoi4-frame-animation` for frame plans, per-frame source art, normalization, contact sheets, preview GIFs, frame sheets, static fallbacks, and animation handoffs.

Asset subagents may create:

- source files
- processed PNG previews
- final DDS files
- contact sheets
- manifests
- `docs/assets/<feature_slug>/gfx_handoff.md`

Asset subagents must not edit `.gfx`, localisation, GUI, event, focus, idea, decision, scripted effect, scripted trigger, on_action, history, country, external tabular data files, or workbooks unless the parent explicitly grants that scope.

The main agent owns final `.gfx` sprite definitions, gameplay references, docs alignment, and validation.

A good parent prompt to an asset subagent includes the feature slug, asset list, asset type, target size, source mode, final DDS folder, sprite name if already registered, reference folder, visual direction, source constraints, and anything the subagent must mark blocked instead of substituting.


## 2.2 Final asset placement and naming

Feature-owned final assets should be grouped under a feature-scoped folder whenever the engine surface uses explicit sprite or texture paths.

Use this folder form:

```text
<feature_slug>
```

Place the feature folder directly under the asset category folder, for example `gfx/event_pictures/<feature_slug>/` or `gfx/interface/ideas/<feature_slug>/`. Do not insert a project namespace layer such as `gfx/event_pictures/<mod_namespace>/<feature_slug>/`; the mod root already provides the project namespace.

Do not leave new feature assets loose in category roots such as `gfx/event_pictures/`, `gfx/presentations/`, `gfx/interface/ideas/`, `gfx/interface/goals/`, `gfx/interface/decisions/`, or `gfx/leaders/` unless that root placement is an engine-facing lookup requirement.

Root-only and engine-convention exceptions:

- `gfx/achievements/` must keep achievement DDS files directly in the root. Do not create `gfx/achievements/<feature_slug>/` subfolders unless a new engine behavior has been verified locally. Achievement filenames must match the full achievement ids from `common/achievements/`, so feature-owned achievement ids and triplet filenames should use `<feature_slug>_<achievement_name>{,_grey,_not_eligible}.dds` or the exact established id if it includes an ordinal.
- `gfx/flags/`, `gfx/flags/medium/`, and `gfx/flags/small/` must keep HOI4 tag/ideology filenames. Do not put flags into feature folders; use cosmetic tags or route-specific tag filenames when a feature needs transformed flags.

Shared systems may use a clear shared or system folder. Do not force shared assets into a feature folder just to avoid a root directory.

When moving or adding an asset, update every `.gfx`, `.gui`, event, idea, decision, focus, localisation, and documentation reference that names the old path or sprite. Keep sprite names stable unless the engine-facing identifier itself has to change, as with achievement ids.

Researched presentation audio belongs to `hoi4-text-audio-research`. Use feature-scoped music and sound paths only when the repository already uses that convention or the parent prompt asks for it. Preserve source downloads under a documented source-audio path instead of burying them among final game files.

## 3. Asset source rules

Choose the source mode based on asset type.

### Scene-first and mood-first selection rule

Do not default feature art to maps, cartographic overlays, arrows, staff tables, conference rooms, or generic war-room compositions unless that is the strongest visual for the specific asset.

For a feature, many visuals should focus on the actor, force, symbol, ritual, creature, crowd, machine, government, army, leader, or strange condition behind the event. The image should usually make the event feel active and dangerous, not merely show that territory changed.

Prefer visuals that show:

- a country, movement, army, cult, council, machine, plague, or supernatural force as the subject
- people, banners, ruins, storms, fires, shadows, masks, relics, halls, crowds, weapons, monuments, or rituals
- obsession, wrath, zeal, panic, corruption, transformation, prophecy, dread, awe, or other feature-specific mood
- fantasy, surreal, mythic, occult, symbolic, or unexplained elements when the event concept supports them
- a clear subject and strong atmosphere over neutral geography

Avoid making the main visual read like:

- a map has changed
- borders have shifted
- officers are discussing an expansion route
- the art is mainly a strategic diagram with decoration
- the scene is a generic command table without a strong feature identity

Maps may still appear as secondary props when useful, but they should rarely be the main visual idea for fictional, alternate-history, extreme-route, supernatural, symbolic, or strange event assets.

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

For generated animated assets, use `$imagegen` through `hoi4-frame-animation`. Each animation frame must be generated or edited as its own source frame according to a frame plan. Do not use local filters, transforms, glow pulses, or offsets as the source of final motion.

### Choose source mode for event photo assets

Report images, news images, and custom feature images may be either internet-sourced or generated.

Use internet-sourced imagery when the asset must show a real photographed person, specific real battle, real place, real object, real newspaper, real poster, real map, real archive item, or other verifiable historical material.

Use `$imagegen` when the event is fictional, alternate-history, symbolic, supernatural, extreme-route, or when a unique scene is more important than matching an existing archive image. Generated event-photo assets should be prompted as period-authentic documentary material, not modern cinematic concept art.

For generated Second World War-era report, news, or custom feature images:

- prompt for 1936-1945 photographic technology, period composition, period clothing, period vehicles, period architecture, and documentary realism
- avoid modern streets, uniforms, props, weapons, vehicles, signage, UI overlays, cinematic color grading, and readable generated text
- keep the source PNG, processed preview, final DDS, prompt, and manifest entry
- record the source mode as generated and explain why generation fit better than sourcing
- never use generated images for real leader portraits or to fabricate a real person's likeness

Follow the repository web research rules from `AGENTS.md` when searching for source images.

For internet-sourced event photo assets that are meant to represent the Second World War era, search for period-matching source imagery from roughly 1936 to 1945 unless the feature spec gives a narrower date range. Prefer contemporary photographs, war correspondents' photographs, press agency images, propaganda posters, maps, newspapers, official records, government or military archive images, museum scans, library scans, and period illustrations. Do not use modern photographs, reenactment images, film stills, AI-looking reconstructions, postwar uniforms, streets, weapons, vehicles, buildings, colorized tourist photos, reenactments, or modern props when they do not fit the era. If no suitable period source can be found, either generate a period-authentic fictional/documentary image when the asset does not require a real source, or mark the asset as blocked or `needs_user_review`.

Record the image source, source link, author or archive if available, license or public domain status if available, estimated date or date range, why the image fits the Second World War era, and any uncertainty in the manifest.

### Real leader portraits

Do not generate a leader portrait for a real person.

For real people, use a real source image from the internet or a user-provided image, then crop, resize, process, convert, and document it. Use the repository web research tools when a source image is needed, and prefer public domain, archival, official, or clearly licensed images. If the person belongs to the Second World War setting, prefer contemporary portraits, wartime photographs, news photographs, official portraits, military archive images, passport or identity photos, or archival illustrations. Do not use modern actors, reenactors, statues, cosplay, later fictional depictions, postwar images, or modern images that do not fit the era unless the user explicitly approves them as placeholders.

Real leader portraits should be processed toward the HOI4 portrait style rather than left as raw photos: bust or upper-torso crop, face readable, subdued contrast, mild painterly or period texture, HOI4-like color grading, no modern UI artifacts, no hard white cutout halo, and no over-smoothed face. Do not change the person's identity or generate missing facial features.

Record the source link, author or archive if available, license or public domain status if available, source image path, processed PNG path, final DDS path, and sprite name

For generated or sourced one-person leader portraits, the asset handoff must identify the portrait's gender presentation and any matching leader-name pool requirement. Female-presenting portraits must not be paired with male names and should require `female = yes` where a country leader is created directly. Male-presenting portraits must not be paired with female names or `female = yes`. Council, board, office, crowd, and symbolic-institution portraits should keep institutional leader names instead of personal random-name pools.


### Fictional leader portraits

Fictional leaders, invented councils, collective bodies, supernatural leaders, and symbolic regime portraits must use `$imagegen`.

Generated leader portraits should follow HOI4 leader portrait conventions: 156x210 final DDS unless an existing sprite uses another size, bust or upper-torso framing, strong face or governing-body focal point, subdued painterly finish, period-appropriate uniform or civilian clothing, transparent or HOI4-compatible portrait background as required by the existing asset pattern, and no text, labels, watermarks, modern UI, or meme-like exaggeration.

For generated one-person leader portraits, record the portrait's apparent gender presentation in the manifest and handoff. Female-presenting portraits require female leader-name pools and female leader metadata where the implementation surface supports it. Male-presenting portraits require male leader-name pools and must not be paired with female metadata. Never hand off a portrait in a way that lets implementation randomly assign names from the opposite gender pool. Council, committee, junta, crowd, office, or symbolic-body portraits should be marked as institutional leaders and use institutional names instead of personal random-name pools.

For council or collective leaders, use one clear symbolic council portrait rather than a cluttered crowd. Keep the subject readable at leader portrait size and document that the leader is fictional or collective.

### User-provided assets

If the user provides an image, treat it as a source asset.

Record that the image was user-provided in the manifest.

Still crop, resize, convert, place, wire, and document it like any other source asset.

## 4. Reference asset examples

This skill includes reference images that show how different mod asset types should look.

Before generating, sourcing, processing, or wiring an asset, inspect the relevant reference folder for that asset type. Use the examples to match style, framing, contrast, readability, scale, texture, and HOI4 presentation.

```text
.agents/skills/hoi4-feature-assets/assets/ideas
.agents/skills/hoi4-feature-assets/assets/news_event_images
.agents/skills/hoi4-feature-assets/assets/report_event_images
.agents/skills/hoi4-feature-assets/assets/tech_icons
.agents/skills/hoi4-feature-assets/assets/achievements
.agents/skills/hoi4-feature-assets/assets/decisions
.agents/skills/hoi4-feature-assets/assets/flags
.agents/skills/hoi4-feature-assets/assets/focuses
.agents/skills/hoi4-feature-assets/assets/special_projects
```

Reference mapping:

- idea and national spirit icons: `assets/ideas`
- officer corps spirit icons: inspect vanilla `gfx/interface/officer_corp/spirits/`. Final assets should be 45x45 DDS files with transparent backgrounds, no frames, no painted backdrop, no full-canvas opaque pixels, a readable dark or black outline, and a slight drop shadow. Wire them as `GFX_idea_<spirit_id>` sprites from a `.gfx` file.
- news event images: `assets/news_event_images`
- report event images: `assets/report_event_images`
- tech icons: `assets/tech_icons`
- achievement icons: `assets/achievements`
- decision and decision category icons: `assets/decisions`
- flags: `assets/flags`
- focus icons: `assets/focuses`

If a relevant reference folder exists, do not generate, source, crop, process, or wire new artwork until you have inspected it.

Never copy reference assets directly. Use them as style and formatting guidance.

If the needed asset type has no matching reference folder, inspect the closest relevant folder and existing repository or vanilla assets before choosing a style.

## 5. Generated artwork rules

Do not create core artwork from simple shapes, placeholders, contact sheets, layout-only mockups, empty UI boxes, or generated charts. Final art must be real generated, sourced, or user-provided artwork, not circles, rectangles, lines, gradients, geometric diagrams, or other primitive-shape stand-ins.

For custom feature images, this rule is strict: final art must be a real scene, archival image, painted illustration, or generated documentary-style image. Do not use symbolic diagrams, flat icons, abstract geometry, title cards, or UI-like compositions as the final custom feature image unless the user explicitly requests that exact visual approach and the exception is documented.

Use `$imagegen` for generated artwork and follow the `$imagegen` skill workflow for the source image.

Generated artwork must be real source art that can be processed into the final game asset. Final assets must be clean: must not have sticking artifacts, an icon is centered in the image, etc. Do not use contact sheets, review boards, or layout drafts as final source art.

## 5.1 Icon creation rules

Small gameplay icons must be readable at their final in-game size.

- Use transparent backgrounds for asset types that are transparent in vanilla, especially idea and decision icons and small symbolic interface icons.
- Keep unused pixels fully transparent. Do not leave a square opaque fill behind icons unless the asset type explicitly uses a painted frame or backdrop.
- Give the icon silhouette a dark or black outline and a subtle drop shadow when the icon is displayed over variable UI backgrounds. Do not leave some chroma green outline on the icon.
- Avoid tiny interior detail that disappears at 45x45 or 64x64. Favor one clear subject, strong value contrast, and a centered silhouette.
- Avoid fake checkerboard pixels, white halos, white outlines, oversized medallion fills, and square opaque backdrops.

For every generated icon, follow the `$imagegen` skill's transparent image workflow. Preserve the original generated image, create a processed PNG preview, convert to DDS, and validate the final appearance over a checker background before treating the icon as complete.

The final icon should have transparent unused canvas, no fake checker or matte pixels, no transparent holes inside the painted subject, a slight black outline, a subtle drop shadow, and a centered subject that remains readable at final size.

Generated icon packages must keep visible `$imagegen` source evidence: save the source atlas or source PNGs, record the prompt and source mode in the manifest, process to real transparent backgrounds, and include a contact sheet that shows final alignment, dimensions, transparency, and absence of white matte or opaque square backgrounds. Do not mark a generated icon complete if the final art is a primitive local drawing, a resized unrelated icon, or a locally assembled shape substitute instead of imagegen or sourced artwork.

## 5.2 Icon type separation rules

Focus icons, idea icons, national spirit icons, officer corps spirit icons, decision icons, decision category icons, achievement icons, and tech icons are separate asset types.

Never treat focus, idea, and decision icons as interchangeable.

Do not create focus icons first and then satisfy idea icons or decision icons by resizing, cropping, shrinking, recoloring, padding, or lightly editing the focus icon. This is not a valid asset workflow.

Each icon type must have its own asset-type-specific brief, reference inspection, source artwork, prompt or source choice, crop, target size, filename prefix, manifest entry, and final DDS output.

Shared visual themes are allowed only when every icon is still designed for its own in-game use:

- focus icons should read as full HOI4 focus art at 94x86 with focus-tree style detail and composition
- idea and national spirit icons should read as compact 64x64 symbolic spirit art without borrowing the full focus icon frame
- decision icons should read clearly at 32x32 with simpler shapes, stronger silhouettes, and less interior detail
- decision category icons should be designed for the category button or scripted GUI surface, not derived from a focus icon
- officer corps spirit icons should follow the vanilla officer corps spirit look and 45x45 transparent style
- achievement icons should follow achievement presentation rules and variant rules

If a mechanic needs matching focus, idea, and decision visuals, build them as a coordinated icon family. A coordinated family can share subject matter, symbols, colors, and lore cues, but each member still needs separate source art or a separate generated output designed for its target size and UI role.

The manifest must record the exact asset type for every icon and should note when icons are part of a coordinated family. Do not mark an icon complete if it only exists as a resized version of another icon type.

## 6. Required asset workflow

For every asset package:

1. Read the feature spec, asset prompt, or implementation task.
2. Identify every required visual asset.
3. Group assets by usage type.
4. Split focus icons, idea icons, national spirit icons, officer corps spirit icons, decision icons, decision category icons, achievement icons, and tech icons into separate asset-type work items. Never satisfy one icon type by resizing or lightly editing another icon type.
5. Assign each asset a stable filename.
6. Assign each asset a sprite name if it needs one.
7. Identify the target size.
8. Identify the intended in-game use.
9. Inspect the matching reference folder from section 4 before generating, sourcing, processing, or wiring the asset.
10. Decide the source mode for each asset:
  - `$imagegen`
  - internet source image
  - user-provided source image
11. If the asset is animated, follow `hoi4-frame-animation` before ordinary static processing. Write the animation brief and frame plan, create or approve the static fallback, generate or source every frame, then normalize the frame sequence.
12. For `$imagegen` assets, write a specific image generation prompt and create the base artwork by following the official `$imagegen` skill.
13. For internet-sourced assets, find a suitable source image and record its source link, author or archive if available, and license or public domain status if available.
14. For user-provided assets, record that the image was provided by the user.
15. Save the original generated, sourced, or provided image as a source PNG.
16. Crop and resize the image to the target size.
17. Save a processed PNG preview.
18. Convert the processed PNG to DDS 32 bit unsigned BGRB 8.8.8.8.
19. Move the DDS into the correct mod folder.
20. Create or update the asset manifest.
21. Create or update `gfx_handoff.md` for any asset that needs a sprite definition.
22. Update feature docs or asset docs when the parent prompt grants that documentation scope.
23. Report all created files, proposed sprite names, final paths, blocked assets, and any handoff uncertainty.

Do not mark assets complete until the DDS files exist, the manifest is written, and the main agent has enough handoff information to wire every sprite without guessing.

## Asset depth from improvement addenda

When an improvement addendum asks for richer presentation, the asset handoff should name the visual states instead of asking for generic polish. A good asset request says what the player sees before activation, while active, when locked, when dangerous, when complete, and when the route has failed.

For scripted GUI, plan asset families. A panel usually needs a background, header, button states, value icons, warning indicators, progress frames, locked overlays, selected overlays, hover states, and any animated glow, particle, float, or pulse layers. The main agent owns `.gui` and `.gfx` wiring, but the asset package must provide clear sprite names, sizes, frame counts, static fallbacks, and contact sheets.

## 7. Asset package structure

When creating a new asset package, use a stable working folder.

Recommended working structure:

```text
docs/assets/<feature_slug>/
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
docs/assets/<feature_slug>/manifest.md
```

The manifest must list every asset.

Each asset entry should include:

- asset name
- related feature slug
- related event id only when the asset is tied to a real HOI4 event
- asset type
- intended in-game use
- source mode: `$imagegen`, internet source image, or user-provided source image
- image generation prompt if generated with `$imagegen`
- source link if internet-sourced
- source author, archive, or collection if available
- source date or estimated date range if internet-sourced
- license or public domain status if available
- era-fit note for Second World War-era assets
- source PNG path
- processed PNG path
- final DDS path
- target size
- sprite name
- `.gfx` file
- localisation key if relevant
- related focus, idea, event, decision, UI element, or text and audio research package if relevant
- notes
- asset status
- frame count, frame timing, loop behavior, and anchor point for animated assets
- static fallback path and animated sheet or frame-sequence path for animated assets
- source mode and source note for every animation frame when animated

Use `not_needed`, `planned`, `sourced`, `generated`, `processed`, `converted`, `handed_off`, `wired`, `complete`, `needs_user_review`, or `blocked` as asset statuses.

## 9. Standard HOI4 asset sizes

Use these sizes unless the feature spec or an existing repo pattern gives a better project-specific requirement.

- report event images: 210x176
- news event images: 397x153, black and white
- leader portraits: 156x210
- flags small: 10x7
- flags medium: 41x26
- flags normal: 82x52
- tech icons small: 64x64
- tech icons medium: 132x52
- achievements: 64x64
- custom feature images: match the target GUI surface or documented repository pattern
- decision icons: 32x32
- idea and national spirit icons: 64x64
- focus icons: 94x86

Use other sizes when the feature UI or asset type requires it.

When unsure, inspect the existing repository pattern and vanilla HOI4 assets before choosing.

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
- custom feature images: `presentation_`
- achievement icons: `achievement_`
- leader portraits: `leader_`

For feature-specific assets, include the feature slug where useful. For example, all idea assets related to a feature should go into one folder for that feature.

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

For transparent icon prompts, explicitly request a transparent canvas, no fake checkerboard, no white rim, no white/colored outline, no glow, no sticker border, no opaque square background, and a clean silhouette suitable for HOI4 UI.

## 12. Internet source image rules

When using internet source images:

1. Search for images that fit the event tone, target use, and intended era.
2. For Second World War-era event assets, search for source images from roughly 1936 to 1945 unless the feature spec gives a narrower date range.
3. Prefer contemporary or near-contemporary public domain, archival, official, museum, library, newspaper, map, press photograph, propaganda poster, government record, military record, period illustration, or clearly licensed sources.
4. Reject modern photographs, reenactments, film stills, postwar streets, uniforms, props, weapons, vehicles, buildings, AI-looking reconstructions, and later stylized images when they do not fit the era.
5. Record source links, source date or estimated date range, and license or public domain status when available.
6. If licensing, date, or era fit is unclear, mark it as uncertain in the manifest.
7. Process the image into the correct HOI4 size and style.
8. Preserve the source image path and processed preview path.

For public-facing or uncertain assets, keep the manifest honest about the source status, date uncertainty, and Second World War-era fit uncertainty.

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

Do not ask `$imagegen` to create the tilted card. Generate or source the documentary photograph first, then apply the card treatment locally. This keeps the tilt, shadow, and margins consistent.

```bash
python tools/process_report_event_image.py source.png processed_report_event.png
python tools/process_report_event_image.py source_folder processed_folder
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

## 14. News event images

News event images may use internet-sourced imagery or generated period-news imagery. Prefer generated news images when the event needs a unique fictional or alternate-history scene, invented crisis, or scene that is unlikely to exist in archives. Use real sources when the image must depict a real person, real historical scene, or real archival item.

News images should look like black-and-white documentary photographs or period news illustrations.

For Second World War-era subjects, prefer contemporary newspapers, news photographs, war correspondents' photographs, press agency images, propaganda posters, maps, official visual records, military archive images, museum or library scans, or period illustrations. Do not use modern reenactment photos, modern news photos, film stills, or later images that do not fit the era.

Use:

- old news photograph or period press illustration style
- Second World War-era visual fit when the feature belongs to that era
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

Generated news images must be converted to black and white during processing, with period press contrast/grain and no modern color remnants. Record the source link and license or public domain status for internet-sourced images, or the generation prompt and source-mode rationale for generated images.

## 15. Large feature presentation images

Large feature presentation images may use internet-sourced imagery or generated art. Prefer generated custom feature images for fictional, alternate-history, symbolic, supernatural, extreme-route, or emotionally specific moments where a unique composed image better fits the feature role. Use internet sources when the image must depict a real historical person, real photographed event, or real archival artifact.

Large feature presentation images should have:

- strong central composition
- clear dramatic theme
- readable subject
- enough contrast for HOI4 UI
- Second World War-era visual fit when the feature belongs to that era
- no generated text
- no modern clothing, streets, weapons, vehicles, buildings, props, film stills, or reenactment imagery when they do not fit the era
- no cluttered small details that disappear at final size

Target size:

Use the exact target size required by the repository UI surface, image slot, or parent prompt. Do not assume a fixed custom-presentation size when the repository has no matching surface.

If sourced quote, remark, or audio research needs music, use `hoi4-text-audio-research` and research suitable public domain or clearly licensed music. Use feature-scoped paths such as `music/<feature_slug>/` and `sound/<feature_slug>/` only when the repository uses that convention or the parent requests it. Never create final music or audio from generated test tones, primitive waveforms, beeps, noise beds, or local oscillator output; that includes sine, square, triangle, and sawtooth waveforms.

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

Do not derive idea or national spirit icons from focus icons. They must be designed as 64x64 spirit-style icons from their own prompt or source art, even when they share a theme with a focus.

Use `$imagegen` for the base artwork unless the user provides or requests a specific source image.

Follow the `$imagegen` skill's transparent image workflow when the icon should have a transparent background.

Inspect `.agents/skills/hoi4-feature-assets/assets/ideas` before generating or processing idea icons.

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

Do not create a focus icon as the master artwork for idea icons, decision icons, or other smaller icon types. A focus icon can share a theme with those icons, but it must remain a separate focus-specific asset.

Every focus icon should support the focus tree's story, ideology, or gameplay purpose.

Use `$imagegen` for the base artwork unless the user provides or requests a specific source image.

Follow the `$imagegen` skill's transparent image workflow when the icon should have a transparent background.

Inspect `.agents/skills/hoi4-feature-assets/assets/focuses` before generating or processing focus icons.

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

Do not derive decision icons from focus icons or idea icons. They must be composed for 32x32 readability from their own prompt or source art.

Decision category icons may use:

```text
decision_category_
```

Use `$imagegen` for the base artwork unless the user provides or requests a specific source image.

Follow the `$imagegen` skill's transparent image workflow when the icon should have a transparent background.

Inspect `.agents/skills/hoi4-feature-assets/assets/decisions` before generating or processing decision icons.

## 19. Achievement icons

Achievement icons should be compact and readable at 64x64.

Generate the completed achievement icon first with `$imagegen`.

Then create:

- grey variant (simply black and white)
- not-eligible variant by copying the grey variant and compositing `.agents/skills/hoi4-feature-assets/assets/achievements/overlay.png` on top

The variants may be created after the completed icon exists.

Do not create not-eligible achievement icons by red-tinting, filtering, darkening, recoloring, or manually redrawing the grey icon. If the overlay file is missing or cannot be applied cleanly, stop and report the asset as blocked instead of substituting another treatment.

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

Inspect `.agents/skills/hoi4-feature-assets/assets/achievements` before generating or processing achievement icons.

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

Always use `$imagegen` for fictional flags and user-provided or internet source images for historical or real-world flags.

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

Leader portraits should match the intended the repository visual direction for the character or country.

Target size:

```text
156x210
```

Inspect the closest relevant reference folder and existing repository portraits before generating or processing fictional leader portraits.

## Animated leader portraits

Leader portraits can be animated for special routes, extreme-route leaders, supernatural leaders, rare formables, major transformations, or dramatic council reveals. They should not be required for ordinary advisors or every normal country leader.

Animated leader portrait packages must include:

- static fallback portrait
- animated sheet or frame source
- final DDS files
- final sprite names
- character or leader key that will use the portrait
- source mode and source documentation
- whether the leader is real, fictional, symbolic, collective, supernatural, or alternate-history
- note on motion type, such as glow, smoke, flicker, eye-light, flag shadow, slow breathing, office light, map projection, or particle drift

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

## Decision category and scripted GUI visual packs

For a decision category with a scripted GUI or mechanic window, the asset handoff should cover the full interface state set.

Useful assets include:

- category icon
- category header plate
- background panel
- tab buttons
- normal, hover, selected, locked, disabled, and warning button states
- progress bars and fill variants
- meter frames
- target cards
- status seals
- warning overlays
- animated glow overlays
- animated particle overlays
- animated float emblems
- static fallback for every animated element
- tooltip icon set
- close and open buttons
- mechanic-specific leader, council, or envoy portrait

The asset prompt should state which sprites are decorative and which represent mechanic state. State-driven sprites need clear names that match the mechanic value or route state.

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

## Formable nation asset coverage

Every formable nation needs visible identity assets.

Asset planning should cover:

- formable flag in normal, medium, and small sizes
- ideology variants where relevant
- cosmetic-tag flags where relevant
- leader portrait or council portrait
- animated leader portrait when the formable is a rare dramatic route
- focus icons for the formation route
- decision icon for the formation decision
- decision category or scripted GUI assets if formation progress is managed visually
- news, report, or custom feature image if the formation is globally important
- faction emblem if the formable creates a league, empire, federation, bloc, mandate, compact, or coalition
- achievement icon if the formable has achievement hooks

Historical or culturally attested formable symbols need source review. Fictional, alternate-history, supernatural, and extreme-route variants may use generated art with clear manifest notes.


## Animated sprites, scripted GUI assets, and animated portraits

Use `hoi4-frame-animation` for every final animated visual asset. Some mod mechanics should have animated visual layers when motion improves readability, atmosphere, or feedback. Examples include floating seals, glowing route emblems, particle drift, meter pulses, warning frames, active-button glows, occult pressure effects, sponsor influence networks, and final formable proclamations.

Animated leader portraits should be handled as major identity assets. Real people require sourced base images. Fictional or impossible leaders can be generated. The asset handoff must say whether the animation is subtle, such as breathing light or smoke, or symbolic, such as eye glow, map shadow, glitch, or spectral overlay. The portrait should still read clearly at in-game size.

Final animated assets must be built from planned source frames. Do not create final animation by taking one still image and shifting, scaling, rotating, warping, blurring, recoloring, brightening, or pulsing it with a script. Local scripts may normalize, align, crop, resize, assemble sheets, create previews, and convert frames after the real frames exist.

## 24. DDS conversion

Final PNG assets must be converted to DDS using the repository's standard DDS conversion workflow.

The output must be compatible with the mod's expected 32-bit BGRA or B8G8R8A8-style DDS workflow.

If conversion fails, stop and report the error. Do not invent another conversion route unless the user approves it.

After conversion, confirm that:

- the DDS exists
- the dimensions are correct
- the background is transparent for icons
- the filename is stable
- the file is in the correct mod folder, including the feature-scoped folder or documented root-only exception
- the `.gfx` path points to the DDS
- the manifest records the final path

Do not leave only PNG files when the game expects DDS.

## 25. `.gfx` handoff and main-agent wiring

Asset subagents do not edit `.gfx` files by default.

When an asset needs a sprite definition, the asset package must include a handoff note for the main agent.

Recommended path:

```text
docs/assets/<feature_slug>/gfx_handoff.md
```

The handoff must include:

1. Final DDS path.
2. Proposed sprite name or the exact sprite name already provided by the parent.
3. Suggested target `.gfx` file.
4. Ready-to-copy sprite definition snippet when useful.
5. Related localisation key, GUI element, event id, focus id, idea id, decision id, achievement id, or presentation cue or package id when known.
6. Any uncertainty about sprite naming or target file placement.
7. Any blocked or needs-review asset.

If the main agent already registered `.gfx` sprites or texture paths before requesting art, the asset subagent must follow those filenames, sprite names, DDS paths, and target sizes exactly. It should only propose names or paths when they were not provided.

The main agent then:

1. Finds the correct existing `.gfx` file if one exists.
2. Follows the existing naming and formatting pattern.
3. Adds the sprite definition.
4. Points the texture file to the final DDS path.
5. Keeps sprite names stable.
6. Updates localisation, GUI, event, focus, idea, or decision references that use the sprite.
7. Updates docs and any explicitly scoped external records when relevant.

When wiring feature-owned sprite-backed art, the texture path should point to the feature-scoped folder for that asset category. If an asset must stay root-only, document the engine reason in the handoff or manifest.

Do not create a new `.gfx` file if an existing one is clearly the right place. If a new `.gfx` file is needed, the main agent must name it consistently and document why.

## 26. Documentation updates

When generated or sourced assets are part of a feature or mechanic, update the relevant docs.

The docs should mention:

- what assets exist
- where the DDS files live
- which `.gfx` file the main agent should use or has used
- which sprite names are used or proposed
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

1. Every required asset from the feature spec is accounted for.
2. Every asset uses the correct source mode: `$imagegen` for generated symbolic, fictional, alternate-history, or unique report, news, or large feature presentation assets. internet or user-provided source images for real historical materials. and real source images for real leader portraits.
3. The matching reference folder from section 4 was inspected before generation, sourcing, processing, or wiring.
4. Every generated, sourced, or provided asset has a source PNG.
5. Every final asset has a processed PNG preview.
6. Every final asset has a DDS output.
7. DDS files use 32 bit unsigned BGRB 8.8.8.8.
8. DDS files are moved into the correct mod folders.
9. A `gfx_handoff.md` exists for every asset that needs a sprite definition, and the main agent has enough information to wire it.
10. The asset manifest exists.
11. Internet-sourced assets record source links, source date or estimated date range, license or public domain status if available, and era-fit notes for Second World War-era assets.
12. Fictional or non-human portraits generated with `$imagegen` are clearly marked as fictional or generated in the manifest.
13. Docs are updated where relevant.
14. The feature implementation or parent handoff knows which sprite names to use.
15. No final asset remains only in a temporary folder.
16. Focus, idea, national spirit, officer corps spirit, decision, decision category, achievement, and tech icons were treated as separate asset types. No idea or decision icon is only a resized, cropped, recolored, padded, or lightly edited focus icon.
17. Every animated asset used `hoi4-frame-animation`, has real source frames, has a static fallback, and has no transform-only final motion.
