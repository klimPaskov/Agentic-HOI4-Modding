---
name: hoi4-feature-assets
description: Use when creating, sourcing, processing, converting, organizing, wiring, or documenting visual assets for a Hearts of Iron IV mod.
---

# HOI4 Feature Assets

Use this skill when a HOI4 modding task requires final visual assets.

Asset coverage follows accepted spec rows, manifest requirements, or explicit user instructions. Do not infer optional advisor, high-command, officer-corps, dossier-card, portrait, emblem, or animation families merely because a character or gameplay consumer exists. Record the required family before production.

This includes event pictures, UI assets, focus tree assets, country assets, achievement assets, generated icons, sourced feature art, generated icon art, animated sprites, animated portraits, sprite sheets, GIF previews, and any asset package that must be wired into the mod.

## Canonical reference root

All active HOI4 asset skills and agents use this one reference folder:

`.claude/skills/hoi4-feature-assets/assets/vanilla_reference/`

All category paths in this skill are relative to that exact folder. Do not use
a project-local copy, another skill-local copy, a compatibility pack, or a
different parent asset folder.

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
- static and animated decision category pictures
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

- `hoi4_asset_source_researcher` for non-portrait real or archival image sourcing, historical flag-design research, historically attested symbols, user-provided source photos, archival decision category pictures, and report, news, or custom feature images that must depict real photographed material
- `hoi4_portrait_creator` for every character portrait: grounded source research, durable archival storage, explicit source placeholders, fictional image-generator production, user-supplied styled-result validation, processing, DDS conversion, portrait-specific wiring, manifests, and handoffs
- `hoi4_generated_feature_art` for generated non-icon feature art, including fictional or alternate-history report images, news images, large presentation images, generated decision category pictures, flat fictional flag designs, faction emblems, UI panels, and progression-state base art; it does not own final character portraits
- `hoi4_icon_artist` for focus icons, idea icons, national spirit icons, officer corps spirit icons, decision icons, decision category icons, achievement icons, tech icons, custom-unit counters, and exact state-piece graphics derived from verified map geometry

For animated work, route by asset type first. Then require the chosen asset subagent to follow `hoi4-frame-animation` for frame plans, per-frame source art, normalization, contact sheets, preview GIFs, frame sheets, static fallbacks, and animation handoffs.

Asset subagents may create:

- source files
- processed PNG previews
- final DDS files
- contact sheets
- manifests
- <!-- HOI4_MOD_SETUP_PORTRAITS_START --> durable sourced portraits under `docs/assets/portraits/` <!-- HOI4_MOD_SETUP_PORTRAITS_END -->
- `docs/assets/<feature_slug>/gfx_handoff.md`

Asset subagents must not edit `.gfx`, localisation, GUI, event, focus, idea, decision, scripted effect, scripted trigger, on_action, history, country, external tabular data files, or workbooks unless the parent explicitly grants that scope. The portrait worker has a standing narrow exception for portrait-specific `.gfx` entries and existing character portrait references.

The main agent owns final non-portrait `.gfx` sprite definitions, gameplay references, docs alignment, and validation. The portrait worker owns portrait-specific `.gfx` and existing character portrait references.

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

## 2.3 Temporary feature-workspace lifecycle

Treat project-root `docs/assets/<feature_slug>/` as temporary evidence and working material, except for explicitly durable archives such as the portrait source archive described below. Keep source files, previews, contact sheets, manifests, provenance, research notes, and handoffs while work is active, blocked, awaiting review, or undergoing acceptance scenarios.

Before declaring the feature fully complete:

1. Promote durable provenance, licensing, attribution, requirement-to-runtime crosswalks, review results, accepted handoff facts, and blocker or exception notes into permanent feature, plan, spec, super-event, or system documentation.
2. Move final runtime assets into engine-facing folders and verify every `.gfx`, `.gui`, audio, or gameplay reference.
3. Verify that no runtime reference points into `docs/assets/`.
4. Delete the complete feature-scoped temporary workspace, including empty subfolders, and verify that it is absent. Never delete a separately designated durable archive as part of this cleanup.

An absent temporary workspace is expected after a fully complete goal. If the feature is incomplete or blocked, retain it and report the blocker. Never delete skill-local reference libraries or another feature's workspace.

## 2.4 Asset repository preflight and Git LFS hydration

Before processing a large asset set, classify paths by role: `.gfx` files are text registries, while `.png`, `.dds`, `.wav`, and other artwork or audio paths are binary candidates, and modified files outside the requested scope must remain untouched.

- Detect Git LFS pointer stubs from the exact pointer signature, not byte size: the first line is exactly `version https://git-lfs.github.com/spec/v1`, followed by `oid sha256:<hex>` and `size <integer>` lines.
- File size alone is not validity evidence; legitimate tiny images such as 10x7 flags may be under 1 KB.
- If the required objects are present in `.git/lfs/objects`, run a scoped `git lfs checkout <paths>` first, limited to the requested binary paths; `git lfs checkout` preserves modified files.
- Use `git lfs fetch` or `git pull` only when objects are missing and the task explicitly authorizes network or repository updates; never broaden the scope or discard local edits.
- For every expected LFS path, compare the working file's SHA-256 to its index OID from `git lfs ls-files -l`, then confirm zero remaining pointer stubs.
- If checkout reports an index-refresh warning after writing real content, retain the content/OID verification as authoritative and record the warning in the handoff.
- After hydration, validate image and audio containers with format-aware decoders or parsers, such as DDS header and pixel checks or WAV metadata checks, rather than size heuristics.

<!-- HOI4_MOD_SETUP_PORTRAITS_START -->
## 2.5 Sourced portrait handoff

`hoi4_portrait_creator` researches each grounded source, archives it under `docs/assets/portraits/<feature_slug>/`, wires an explicit pending source placeholder at the final runtime path, and keeps the basename stable. The user runs the selected Cloud, Local, or RunPod styled-replacement workflow and supplies the final result; the portrait worker validates and installs it. Agents never open, configure, queue, monitor, or otherwise operate RunPod. For fictional or impossible subjects the portrait worker invokes the image generator and completes processing and wiring itself.

Resolve the stable runtime basename first:

```text
portrait_<tag>_<character_key>
```

Use that exact basename for the runtime DDS and archived source:

```text
<runtime_portrait_path>/portrait_<tag>_<character_key>.dds
docs/assets/portraits/<feature_slug>/portrait_<tag>_<character_key>.png
```

`<tag>` is the owning country or cosmetic tag. `<character_key>` is the stable scripted character or institutional subject key. Save the highest-resolution source and record provenance plus `source_placeholder`, `replacement_pending`, or `styled_final`.

The durable archive is not runtime storage. No `.gfx`, character, GUI, event, focus, idea, or decision reference may point into `docs/assets/portraits/`. Never delete it during temporary feature-workspace cleanup unless the user explicitly asks.
<!-- HOI4_MOD_SETUP_PORTRAITS_END -->

## 3. Asset source rules

Read [`references/asset-source-rules.md`](references/asset-source-rules.md) before choosing whether an asset is sourced, generated, or user-provided. It contains the complete standard for this section and its subsections.

## 4. Reference asset examples

Read [`references/reference-asset-examples.md`](references/reference-asset-examples.md) before producing any asset family, to find its matching reference examples. It contains the complete standard for this section and its subsections.

## 5. Generated artwork rules

Do not create core artwork from simple shapes, placeholders, contact sheets, layout-only mockups, empty UI boxes, or generated charts. Final art must be real generated, sourced, or user-provided artwork, not circles, rectangles, lines, gradients, geometric diagrams, or other primitive-shape stand-ins.

For custom feature images, this rule is strict: final art must be a real scene, archival image, painted illustration, or generated documentary-style image. Do not use symbolic diagrams, flat icons, abstract geometry, title cards, or UI-like compositions as the final custom feature image unless the user explicitly requests that exact visual approach and the exception is documented.

Use the selected image-generation route for generated artwork. HOI4 Mod Setup fills in the provider details from the manifest section below.

Generated artwork must be real source art that can be processed into the final game asset. Final assets must be clean: must not have sticking artifacts, an icon is centered in the image, etc. Do not use contact sheets, review boards, or layout drafts as final source art.

## 5.1 Icon creation rules

Small gameplay icons must be readable at their final in-game size.

- Use transparent backgrounds for asset types that are transparent in vanilla, especially idea and decision icons and small symbolic interface icons.
- Keep unused pixels fully transparent. Do not leave a square opaque fill behind icons unless the asset type explicitly uses a painted frame or backdrop.
- Give the icon silhouette a dark or black outline and a subtle drop shadow when the icon is displayed over variable UI backgrounds. Do not leave some chroma green outline on the icon.
- Avoid tiny interior detail that disappears at 45x45 or 64x64. Favor one clear subject, strong value contrast, and a centered silhouette.
- Avoid fake checkerboard pixels, white halos, white outlines, oversized medallion fills, and square opaque backdrops.

For every generated icon, follow the selected route's transparent-background instructions. Preserve the original generated image, create a processed PNG preview, convert to DDS, and validate the final appearance over a checker background before treating the icon as complete.

<!-- HOI4_MOD_SETUP:IMAGE_GENERATION_PROVIDER:START -->
[The selected image-generation provider details are added by HOI4 Mod Setup.]
<!-- HOI4_MOD_SETUP:IMAGE_GENERATION_PROVIDER:END -->

The final icon should have transparent unused canvas, no fake checker or matte pixels, no transparent holes inside the painted subject, a slight black outline, a subtle drop shadow, and a centered subject that remains readable at final size.

Generated icon packages must keep visible image-generation source evidence: save the source atlas or source PNGs, record the prompt and source mode in the manifest, process to real transparent backgrounds, and include a contact sheet that shows final alignment, dimensions, transparency, and absence of white matte or opaque square backgrounds. Do not mark a generated icon complete if the final art is a primitive local drawing, a resized unrelated icon, or a locally assembled shape substitute instead of generated or sourced artwork.

## 5.2 Icon type separation rules

Focus, idea, national-spirit, officer-corps, decision, mission, decision-category, achievement, technology, special-project, balance-of-power, intelligence-agency, intelligence-operation, commander-trait, medal, military-raid, state-modifier, MIO, faction, building, and modifier icons are separate asset types.

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
- intelligence-agency and intelligence-operation icons must follow their own agency or operation UI precedent rather than a generic decision treatment
- commander traits, medals, military raids, state modifiers, MIOs, factions, buildings, and modifier icons must follow the matching canonical folder and owning vanilla definition; do not force these families onto a blanket 32x32 or 64x64 canvas
- frame strips, indexed building sprites, and multi-state modifier art must retain their frame order and frame count rather than being treated as a single standalone icon

If a mechanic needs matching focus, idea, and decision visuals, build them as a coordinated icon family. A coordinated family can share subject matter, symbols, colors, and lore cues, but each member still needs separate source art or a separate generated output designed for its target size and UI role.

The manifest must record the exact asset type for every icon and should note when icons are part of a coordinated family. Do not mark an icon complete if it only exists as a resized version of another icon type.

## 6. Required asset workflow

For every asset package:

1. Read the feature spec, asset prompt, or implementation task.
2. Identify every required visual asset.
3. Group assets by usage type.
4. Split every icon family named in section 5.2 into its own asset-type work item. Never satisfy one UI surface by resizing, relabeling, or lightly editing art created for another surface.
5. Assign each asset a stable filename.
6. Assign each asset a sprite name if it needs one.
7. Identify the target size.
8. Identify the intended in-game use.
9. Inspect the matching reference folder from section 4 before generating, sourcing, processing, or wiring the asset.
10. Decide the source mode for each asset:
  - the image generator
  - internet source image
  - user-provided source image
11. If the asset is animated, follow `hoi4-frame-animation` before ordinary static processing. Write the animation brief and frame plan, create or approve the static fallback, generate or source every frame, then normalize the frame sequence.
12. For image-generator assets, write a specific image generation prompt and create the base artwork by following the image generator's workflow.
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

Use [hoi4-scripted-gui](../hoi4-scripted-gui/SKILL.md) for the accepted reference-to-native mapping, background-region contract, iterative MCP live previews, click-region inspection, state and resolution coverage, and final visual acceptance. Asset production alone does not prove a GUI layout complete.

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
- source mode: image generator, internet source image, or user-provided source image
- image generation prompt if generated with the image generator
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

## 8.1 Requirement-to-runtime coverage audit

Before any asset completion claim, create or refresh a row-level coverage crosswalk from every accepted asset requirement in the current specs, manifest plans, and animation plans. Do not start from the assets that happen to be live. Each accepted row must identify:

- its requirement id and accepted design source
- its intended in-game purpose
- the exact source package and manifest entry
- the exact runtime registration: final asset path plus the `.gfx` sprite or texture, engine lookup id, or other owning definition as applicable
- the live consumer file and id
- the state or visibility binding when the asset is conditional or state-driven
- the current audit record path, evidence, and row status

Before changing asset or portrait wiring or completion counts, audit the full current required logical slot -> registered alias -> actual runtime path matrix, including conditional or regional variants and aliases sharing a path. Preserve the audited requirement, registry, and consumer source revisions or hashes, runtime file hashes, and declared coverage bounds in the audit record before making the change. A partial receipt or historical count must never stand in for the current consumer inventory.

Report file inventory, registered aliases and actual consumption, source provenance and archive packages, and accepted final coverage separately. Count unique consumed runtime paths, unique whole-file hashes, and unique decoded-pixel hashes as separate measures. File presence or alias consumption does not prove source provenance or final acceptance.

For every animation family, also record the purpose and the direction or state semantics that distinguish the family, together with its frame, timing, and loop evidence. Frame totals, live animation-family totals, and registered sprite totals are not coverage proof.

Audit exact rows, not counts. An extra asset or animation cannot satisfy an absent accepted row unless an explicit accepted design amendment identifies that row and names the replacement; link that amendment in the crosswalk. Any missing source package, runtime registration, live consumer, required state or visibility binding, or current audit record leaves the row incomplete.

After a late user correction or accepted spec, manifest-plan, or animation-plan change, rebuild the crosswalk against the current repository and attach a fresh coverage diff listing added, removed or replaced, changed, and still-uncovered rows. Do not reuse the prior audit or its totals for the completion claim.

## 9. Standard HOI4 asset sizes

Use these sizes unless the feature spec or an existing repo pattern gives a better project-specific requirement.

- report event images: 210x176
- news event images: 397x153, black and white
- country-leader portraits: 156x210
- commander portraits: 156x210 full portrait textures
- operative portraits: 156x210 full portrait textures
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

## 9.1 Unit visual references

Read [`references/unit-visuals-and-3d-handoff.md`](references/unit-visuals-and-3d-handoff.md) whenever a task touches unit visuals, unit counters, or a 3D model package. It contains the complete standard for this section and its subsections.

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

Every image-generation prompt should be specific enough to produce usable game art.

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

Read [`references/event-images-and-flags.md`](references/event-images-and-flags.md) whenever a task creates report or news event images or flags. It contains the complete standard for this section and its subsections.

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

Use the image generator for the base artwork unless the user provides or requests a specific source image.

Follow the selected provider section for transparent icons: use native alpha when supported or its listed removal fallback, then verify the saved alpha.

Inspect `icons/ideas/` and the matching row in `CATALOG.md` before generating or processing idea icons.

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

Use the image generator for the base artwork unless the user provides or requests a specific source image.

Follow the selected provider section for transparent icons: use native alpha when supported or its listed removal fallback, then verify the saved alpha.

Inspect `icons/national_focus/` and the matching row in `CATALOG.md` before generating or processing focus icons. Do not force every focus source onto an older nominal canvas when the owning sprite and current vanilla precedent use a different native canvas.

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

Use the image generator for the base artwork unless the user provides or requests a specific source image.

Follow the selected provider section for transparent icons: use native alpha when supported or its listed removal fallback, then verify the saved alpha.

Inspect `icons/decisions/`, `icons/missions/`, or `icons/decision_categories/` as appropriate before generating or processing decision-system icons. Missions use the decision icon pipeline but still need mission-specific semantic readability.

## 18.1 Decision category pictures

Read [`references/icon-and-ui-families.md`](references/icon-and-ui-families.md) whenever a task creates decision category pictures or advisor and high-command portrait icons. It contains the complete standard for this section and its subsections.

## Additional gameplay icon families

Route additional icon work by the exact UI surface:

- intelligence identity and action: `icons/intelligence_agency/` and `icons/intelligence_operations/`
- commander progression and honours: `icons/commander_traits/` and `icons/medals/`
- operations and world state: `icons/military_raids/` and `icons/state_modifiers/`
- organizations and map/economy identity: `icons/military_industrial_organizations/`, `icons/factions/`, and `icons/buildings/`
- generic or text-linked modifier presentation: `icons/modifiers/`

Read the matching canonical catalog entries and inspect the owning `.gfx`, `.gui`, or database definition before choosing canvas, frame layout, transparency, or filename. These families are not reskinned decision or idea icons. When a source is a strip or contains several UI states, preserve its frame semantics and document them in the manifest and handoff.

## 19. Achievement icons

Read [`references/achievement-icons.md`](references/achievement-icons.md) whenever a task creates or changes achievement icons. It contains the complete standard for this section and its subsections.

## 20. Flags

Read [`references/event-images-and-flags.md`](references/event-images-and-flags.md) whenever a task creates report or news event images or flags. It contains the complete standard for this section and its subsections.

## 21. Country-leader, commander, operative, and officeholder portraits

Choose the canonical reference family before production:

- country leader: `portraits/leaders/`
- army or navy commander: `portraits/commanders/`
- operative: `portraits/operatives/`
- advisor, theorist, high command, officer corps, or army-small:
  `portraits/advisors/`

Grounded real, historical, restored, separatist, regional, indigenous, dynastic,
or otherwise plausibly historical identities use an attributed real-person
source. One-person generated portraits are reserved for wholly fictional,
impossible, or supernatural identities. Missing or contradictory identity
classification fails closed.

For a real person, `hoi4_portrait_creator` preserves the unchanged archival master and runs `.claude/skills/hoi4-feature-assets/tools/extract_portrait_source_crop.py`. Automatic mode uses the bundled YuNet detector and fails closed unless exactly one subject is detected; it writes the unchanged source copy, lossless crop, deterministic `156x210` PNG, exact-pixel JSON evidence, and a co-located provenance contract. Use the explicit `--crop` recovery path only for an independently reviewed boundary or detector miss. The detector is a framing aid, never identity approval. Retain the source placeholder and require independent likeness, style, identity, and provenance review before DDS conversion or wiring. The user alone supplies the HOI4-style final; when supplied, `hoi4_portrait_creator` validates, installs, and updates portrait-specific wiring.

Record source URL, author or archive, rights status when available, source and
candidate hashes, crop coordinates, review evidence, processed PNG, final DDS,
runtime sprite, and the durable source archive from section 2.4.

For fictional people and impossible or supernatural entities, `hoi4_portrait_creator` uses native
the image generator after the identity gate permits it.
Reject generic, modern, meme, gore, stereotyped, text-bearing, or
interchangeable output. If the image generator is unavailable, mark the portrait blocked.

Full country-leader, commander, and operative textures are `156x210`. Never
manufacture a smaller commander source merely because one UI view displays it
at a smaller apparent size.

## 21.1 Advisor and high-command portrait icons

Read [`references/icon-and-ui-families.md`](references/icon-and-ui-families.md) whenever a task creates decision category pictures or advisor and high-command portrait icons. It contains the complete standard for this section and its subsections.

## Animated leader portraits

Leader portraits can be animated for special routes, extreme-route leaders, supernatural leaders, rare formables, major transformations, or dramatic council reveals. They should not be required for every normal country leader.

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

For UI panels, investigation windows, ledgers, and similar assets, separate artwork from functional UI.

Use the image generator for:

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

When the asset package belongs to a focus-tree or scripted-GUI change, the corresponding MCP inspect and render evidence is mandatory before and after placement. For technology or doctrine icons, mandatory evidence uses `hoi4.tech_inspect` in `explain` or `lint` mode to verify sprite and texture references, then the `assets` or affected folder view in `hoi4.tech_render`, followed by `hoi4.tech_inspect` with `mode: "compare"` after source edits. If a required route is unavailable, record the exact blocker and leave the linked asset surface unresolved; source-only review is not equivalent. This skill still owns source art, processing, DDS conversion, placement, manifests, and `.gfx`/`.gui` handoff.

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

## Formable state-puzzle visual assets

When a formable uses the reusable state-puzzle presentation from `hoi4-decisions-missions`, preserve exact state geometry and one shared geographic projection.

Each package must include a manifest with formable id, state ids and names, alternate requirement groups, counting rules, source map data, projection bounds, anchors, and proposed sprite names; one exact mask or sprite region per required state; grey unmet and green qualifying states with a second non-colour cue; a composed geographic preview; hover-region notes; and final runtime, `.gfx`, and GUI ownership.

Derive shapes from the installed map's state and province geometry. Do not trace screenshots by hand, generate borders with the image generator, simplify the pieces into generic tiles, or substitute a modern political map. Keep one projection, scale, origin, edge treatment, and border width so neighbouring states meet cleanly.

Copy and adapt `.claude/skills/hoi4-decisions-missions/templates/formable_state_puzzle/`. The asset handoff must match its manifest and naming rules. Skill-local templates are reference scaffolding and must never become runtime consumers. The static category-picture alternative also requires the simple-category eligibility gate and cannot accompany the interactive puzzle.

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

Animated leader portraits should be handled as major identity assets by
`hoi4_portrait_creator` plus `hoi4-frame-animation`. The portrait worker owns sourced real base images and image-generator fictional or impossible base portraits. The asset handoff must say whether the animation is subtle,
such as breathing light or smoke, or symbolic, such as eye glow, map shadow,
glitch, or spectral overlay. The portrait should still read clearly at in-game
size.

Final animated assets must be built from planned source frames. Do not create final animation by taking one still image and shifting, scaling, rotating, warping, blurring, recoloring, brightening, or pulsing it with a script. Local scripts may normalize, align, crop, resize, assemble sheets, create previews, and convert frames after the real frames exist.

## 24. DDS conversion

Final PNG assets must be converted to DDS using the repository's standard DDS conversion workflow.

Use the bundled deterministic converter:

```powershell
python -B .claude/skills/hoi4-feature-assets/tools/convert_to_dds.py --input <processed.png> --output <final.dds> [--width <pixels> --height <pixels>]
```

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
2. Every asset uses the correct source mode: `hoi4_portrait_creator` owns attributed sources and user-supplied styled replacements for grounded portraits and the image generator for fictional or impossible portraits.
3. The matching reference folder from section 4 was inspected before generation, sourcing, processing, or wiring.
4. Every generated, sourced, or provided asset has a source PNG.
5. Every final asset has a processed PNG preview.
6. Every final asset has a DDS output.
7. DDS files use 32 bit unsigned BGRB 8.8.8.8.
8. DDS files are moved into the correct mod folders.
9. A `gfx_handoff.md` exists for every asset that needs a sprite definition, and the main agent has enough information to wire it.
10. The asset manifest exists.
11. Internet-sourced assets record source links, source date or estimated date range, license or public domain status if available, and era-fit notes for Second World War-era assets.
12. Fictional or non-human portraits produced through the image generator are clearly marked as fictional or generated in the manifest.
13. Decision category pictures are classified separately from small category icons, scripted GUI backgrounds, and full mechanic-window assets; their canonical reference folder and labeled contact sheet were inspected.
14. Simple categories were not expanded into full scripted GUI asset packs when a static or animated category picture was sufficient.
15. Every formable state-puzzle asset uses exact installed-map state geometry, one shared projection, grey and green qualification states with non-colour cues, clean neighbouring edges, and a manifest aligned with the reusable template.
16. Docs are updated where relevant.
17. The feature implementation or parent handoff knows which sprite names to use.
18. No final asset remains only in a temporary folder.
19. Focus, idea, national spirit, officer corps spirit, decision, decision category, achievement, and tech icons were treated as separate asset types. No idea or decision icon is only a resized, cropped, recolored, padded, or lightly edited focus icon.
20. Every animated asset used `hoi4-frame-animation`, has real source frames, has a static fallback, and has no transform-only final motion.
21. Every unit visual is classified by domain and surface as equipment/technology art, a large land counter, a land/air/naval map counter, a division-template emblem, or a land/air/naval 3D model package; one pipeline was not resized or relabeled to substitute for another. A 3D package also proves the one-image Meshy input rule, provider lineage, vanilla scale calibration, PDX material mapping, topology repair, required skeletal actions, `.mesh`/`.anim` reimport, hash-aware runtime synchronization, parent-owned wiring, and a live consumer.
22. Every advisor, theorist, high-command, officer-corps, or army-small card uses the native `65x67` advisor workflow, the exact accepted template, retained transforms and hashes, and independent native/4x review; it is not a shrunken leader texture.
23. Every sourced portrait has a durable source under `docs/assets/portraits/<feature_slug>/`, a stable runtime basename, an explicit pending source-placeholder or validated final state, and no runtime reference into the archive.

<!-- HOI4_MOD_SETUP_SUPER_EVENTS_START -->
## Super Events images

When the installed `hoi4-super-events` workflow is selected, read its runtime templates and use the declared `457x328` presentation image size. Define the exact role, subject, tone, focal hierarchy, symbolism, source mode, safe text area, prohibited content, final DDS path, and sprite purpose before production. Use sourced archival material for real people, events, places, documents, or objects; use approved generation for fictional, alternate-history, symbolic, or supernatural scenes that do not claim to be historical photographs.

Keep source material, processed previews, provenance, licenses, uncertainty, final DDS output, and GFX handoff together. Review the image at runtime size in the complete popup, then let the main agent wire the sprite, localisation branches, caller, and registration. The examples bundled with `hoi4-super-events` are composition references only and must not be registered as project art.
<!-- HOI4_MOD_SETUP_SUPER_EVENTS_END -->
