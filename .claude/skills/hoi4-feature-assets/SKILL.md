---
name: hoi4-feature-assets
description: Use when a Hearts of Iron IV mod needs final visual assets such as icons, event images, flags, portraits, UI art or animations, including sourcing, DDS conversion, placement and wiring.
---

# HOI4 Feature Assets

Use this skill when a HOI4 modding task requires final visual assets.

Asset coverage follows accepted spec rows, manifest requirements, or explicit user instructions. Do not infer optional advisor, high-command, officer-corps, dossier-card, portrait, emblem, or animation families merely because a character or gameplay consumer exists. Record the required family before production.

This includes event pictures, UI assets, focus tree assets, country assets, achievement assets, generated icons, sourced feature art, generated icon art, animated sprites, animated portraits, sprite sheets, GIF previews, and any asset package that must be wired into the mod.

This file is a router. It keeps the rules that apply to every asset, and every other rule sits, moved verbatim, in exactly one reference below. Open the reference that matches your phase before you act.

Always apply:

- Route file production to the narrow asset subagents with a bounded prompt: `hoi4_icon_artist` (icons, tech icons, counters), `hoi4_generated_feature_art` (generated non-icon art), `hoi4_asset_source_researcher` (real or archival non-portrait images), `hoi4_portrait_creator` (every character portrait). They do not edit `.gfx`, localisation, GUI or gameplay scripts unless the parent grants it (the portrait worker may edit portrait `.gfx` entries). The main agent wires and validates.
- Focus, idea, spirit, decision, category, achievement, tech and the other icon families are separate asset types. Never satisfy one by resizing, cropping or recolouring another.
- Animated finals come from planned source frames through `hoi4-frame-animation`, never from transforming one still.
- Final DDS files go into the engine folders, feature-scoped except for achievements and flags, and nothing at runtime may point into `docs/assets/`.
- Never substitute an asset that cannot be made cleanly: mark it blocked.

Generated source art: read [generation-and-review.md](references/generation-and-review.md) and the `hoi4-imagegen` skill before any generation or editing.

Before reporting an asset package or goal complete, read `completion-checklist.md`, which holds the coverage audit and the final checklist, and the "Super Events images" rules. Before declaring the whole feature complete, also run the workspace cleanup in `workspace-lfs-and-portrait-archive.md`.

## Reference map

- [Scope and subagent routing](references/scope-and-subagent-routing.md): Read before starting asset work, to confirm the scope and choose the subagent and its brief. Covers: When to use this skill; Custom subagent split.
- [Workspace, Git LFS and portrait archive](references/workspace-lfs-and-portrait-archive.md): Read before creating or cleaning up a feature asset workspace, hydrating Git LFS asset files or archiving a sourced portrait. Covers: Temporary feature-workspace lifecycle; Asset repository preflight and Git LFS hydration; Sourced portrait handoff.
- [Prompts, sourcing and feature images](references/prompts-sourcing-and-feature-images.md): Read before writing an image-generation prompt, sourcing an internet image, making report, news or large presentation images or flags, or sourcing music for a presentation. Covers: Image generation prompt rules; Internet source image rules; Report event images; News event images; Large feature presentation images; Flags.
- [Gameplay icon families](references/gameplay-icon-families.md): Read before making any focus, idea, spirit, decision, category, achievement or other gameplay icon, and before reusing art across icon types. Covers: Icon type separation rules; Idea and national spirit icons; Focus icons; Decision icons; Decision category pictures; Additional gameplay icon families; Achievement icons.
- [Portraits](references/portraits.md): Read before producing, sourcing or wiring any leader, commander, operative, advisor or officeholder portrait, together with the sourced-portrait handoff in workspace-lfs-and-portrait-archive.md. Covers: Country-leader, commander, operative, and officeholder portraits; Advisor and high-command portrait icons; Animated leader portraits.
- [Interface, formable and animation assets](references/interface-formable-and-animation-assets.md): Read before planning or making UI panels, scripted GUI art, progression-state variants, formable nation assets or animated sprites. Covers: Asset depth from improvement addenda; UI panels and custom windows; Decision category and scripted GUI visual packs; Progression-state variants; Formable state-puzzle visual assets; Formable nation asset coverage; Animated sprites, scripted GUI assets, and animated portraits.
- [Placement, naming and sizes](references/placement-naming-and-sizes.md): Read before choosing the folder, file name or canvas size of a final asset. Covers: Final asset placement and naming; Standard HOI4 asset sizes; Naming rules.
- [Package, manifest, DDS and gfx handoff](references/package-manifest-dds-and-gfx-handoff.md): Read before building an asset package, writing its manifest, converting to DDS, writing gfx_handoff.md, wiring a finished sprite or marking an asset blocked. Covers: Asset package structure; Manifest requirements; DDS conversion; `.gfx` handoff and main-agent wiring; Documentation updates; Contact sheets; Handling blocked assets.
- [Coverage audit and completion checklist](references/completion-checklist.md): Read before reporting any asset package or goal complete. Covers: Requirement-to-runtime coverage audit; Final checklist; Super Events images.

## Canonical reference root

All active HOI4 asset skills and agents use this one reference folder:

`.claude/skills/hoi4-feature-assets/assets/vanilla_reference/`

All category paths in this skill are relative to that exact folder. Do not use
a project-local copy, another skill-local copy, a compatibility pack, or a
different parent asset folder.

## 1. Core purpose

The goal is to turn asset needs from a feature spec into real HOI4-ready files: source artwork, processed PNG previews, final DDS files in the correct places, sprite handoff notes for the main agent, and documentation of what was created.
Never leave an asset used by the feature as a loose generated or downloaded image; process, place, document, and hand it off so the main agent can wire it cleanly.

## 3. Asset source rules

Read [`references/asset-source-rules.md`](references/asset-source-rules.md) before choosing whether an asset is sourced, generated, or user-provided. It contains the complete standard for this section and its subsections.

## 4. Reference asset examples

Read [`references/reference-asset-examples.md`](references/reference-asset-examples.md) before producing any asset family, to find its matching reference examples. It contains the complete standard for this section and its subsections.

## 5. Generated artwork rules

Do not create core artwork from simple shapes, placeholders, contact sheets, layout-only mockups, empty UI boxes, or generated charts. Final art must be real generated, sourced, or user-provided artwork, not circles, rectangles, lines, gradients, geometric diagrams, or other primitive-shape stand-ins. Every icon socket gets its own meaning-specific art: a shared placeholder or fallback plate is a defect, and the exact-duplicate check (such as the `hoi4.image_audit` reuse report) is never re-baselined or aliased, except for one control shown in two places with the reason recorded.

For custom feature images, this rule is strict: final art must be a real scene, archival image, painted illustration, or generated documentary-style image. Do not use symbolic diagrams, flat icons, abstract geometry, title cards, or UI-like compositions as the final custom feature image unless the user explicitly requests that exact visual approach and the exception is documented.

Use `hoi4-imagegen` for generated artwork (canvas, alpha, margins, naming, DDS or TGA export, sprite handoff); read its skill first.

Final assets must be clean: no stray artifacts, and an icon centred in its image.
## 5.1 Icon creation rules

Small gameplay icons must be readable at their final in-game size.

- Use transparent backgrounds for asset types that are transparent in vanilla, especially idea and decision icons and small symbolic interface icons.
- Keep unused pixels fully transparent. Do not leave a square opaque fill behind icons unless the asset type explicitly uses a painted frame or backdrop.
- Give the icon silhouette a dark or black outline and a subtle drop shadow when the icon is displayed over variable UI backgrounds. Do not leave some chroma green outline on the icon.
- Avoid tiny interior detail that disappears at 45x45 or 64x64. Favor one clear subject, strong value contrast, and a centered silhouette.
- Avoid fake checkerboard pixels, white halos, white outlines, oversized medallion fills, and square opaque backdrops.

`hoi4.image_process` proves transparency from the saved pixels and refuses an opaque result instead of keying a guessed background; `hoi4.image_preview` shows the final art at native size over a checker background before review.

<!-- HOI4_MOD_SETUP:IMAGE_GENERATION_PROVIDER:START -->
Default route: `hoi4-imagegen` (MCP server `hoi4_imagegen`, tools `hoi4.image_*`). Read the `hoi4-imagegen` skill, then `hoi4.image_families { family }`, then the group tool with a required `family` (`hoi4.image_icon`, `_picture`, `_portrait`, `_flag`, `_unit` or `_interface`): without `approve` it returns a free plan with the cost, with `approve: true` and an `idempotency_key` it generates one asset. Then `hoi4.image_process`, `_validate`, `_preview`, `_review` and `_install`; `hoi4.image_audit` checks the mod for cross-family reuse. Provider: the ChatGPT login (`hoi4-imagegen login`) or a key in the environment. If none is configured, stop and report the blocker.
<!-- HOI4_MOD_SETUP:IMAGE_GENERATION_PROVIDER:END -->

The final icon should have transparent unused canvas, no fake checker or matte pixels, no transparent holes inside the painted subject, a slight black outline, a subtle drop shadow, and a centered subject that remains readable at final size.

Generated icon packages must keep visible image-generation source evidence: save the source atlas or source PNGs, record the prompt and source mode in the manifest, process to real transparent backgrounds, and include a contact sheet that shows final alignment, dimensions, transparency, and absence of white matte or opaque square backgrounds. Do not mark a generated icon complete if the final art is a primitive local drawing, a resized unrelated icon, or a locally assembled shape substitute instead of generated or sourced artwork.

## 6. Required asset workflow

For every asset package:

1. Read the feature spec, asset prompt, or implementation task.
2. Identify every required visual asset.
3. Group assets by usage type.
4. Split every icon family named in section 5.2 into its own asset-type work item. Never satisfy one UI surface by resizing, relabeling, or lightly editing art created for another surface.
5. Assign each asset a stable filename.
6. Assign each asset a sprite name if it needs one.
7. Identify the target size from the family's profile (`hoi4.image_families`: the mod's `.tools/gfx/profiles.json` row, vanilla by default).
8. Identify the intended in-game use.
9. Inspect the matching reference folder from section 4 before generating, sourcing, processing, or wiring the asset.
10. Decide the source mode for each asset:
  - `hoi4-imagegen`
  - internet source image
  - user-provided source image
11. If the asset is animated, follow `hoi4-frame-animation` before ordinary static processing. Write the animation brief and frame plan, create or approve the static fallback, generate or source every frame, then normalize the frame sequence.
12. For generated assets, follow the `hoi4-imagegen` loop (families, references, free plan, approved generation, process, validate, preview, review, install) with a specific brief.
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

For a generated asset, `hoi4.image_process` and `hoi4.image_install` do steps 15 to 19 and the handoff of step 21. Sourced and user-provided art of one of the 40 families is imported through `hoi4.image_process` with its `family`. Run `hoi4.image_audit` before the handoff.

Do not mark assets complete until the DDS files exist, the manifest is written, and the main agent has enough handoff information to wire every sprite without guessing.

## 9.1 Unit visual references

Read [`references/unit-visuals-and-3d-handoff.md`](references/unit-visuals-and-3d-handoff.md) whenever a task touches unit visuals, unit counters, or a 3D model package. It contains the complete standard for this section and its subsections.

