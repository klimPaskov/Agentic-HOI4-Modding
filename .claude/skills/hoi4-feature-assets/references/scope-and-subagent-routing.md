# HOI4 Feature Assets: Scope and subagent routing

Part of the [hoi4-feature-assets](../SKILL.md) skill. Read before starting asset work, to confirm the scope and choose the subagent and its brief.

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


