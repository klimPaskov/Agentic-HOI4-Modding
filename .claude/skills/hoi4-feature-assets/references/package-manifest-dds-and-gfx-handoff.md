# HOI4 Feature Assets: Package, manifest, DDS and gfx handoff

Part of the [hoi4-feature-assets](../SKILL.md) skill. Read before building an asset package, writing its manifest, converting to DDS, writing gfx_handoff.md, wiring a finished sprite or marking an asset blocked.

## 7. Asset package structure

Use a stable working folder for a new asset package, structured like this:

```text
docs/assets/<feature_slug>/
 manifest.md
 prompts/
 source_png/
 processed_png/
 contact_sheets/
 notes/
```

Move final DDS files into the correct gameplay asset folders; never keep final assets under `docs/assets/`.

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
- source mode: `hoi4-imagegen`, internet source image, or user-provided source image
- brief, family, plan id and ledger entry if generated with `hoi4-imagegen`
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

## 24. DDS conversion

Assets made or imported through `hoi4-imagegen` get their DDS (TGA for flags) from `hoi4.image_install`; do not convert them by hand. Final PNG art outside the 40 families must be converted to DDS using the repository's standard DDS conversion workflow.

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

When an asset needs a sprite definition, the asset package must include a handoff note for the main agent. `hoi4.image_install` (default `mode: handoff`) writes it to `docs/assets/<feature_slug>/gfx_handoff.md` with the sprite snippet; add the consumer ids it cannot know.

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

The main agent then finds the correct existing `.gfx` file, follows its naming and formatting pattern, adds the sprite definition pointing at the final DDS path, keeps sprite names stable, updates the localisation, GUI, event, focus, idea, or decision references that use the sprite, and updates docs and any explicitly scoped external records.

When wiring feature-owned sprite-backed art, the texture path should point to the feature-scoped folder for that asset category. If an asset must stay root-only, document the engine reason in the handoff or manifest.

Do not create a new `.gfx` file if an existing one is clearly the right place. If a new `.gfx` file is needed, the main agent must name it consistently and document why.

## 26. Documentation updates

When generated or sourced assets are part of a feature or mechanic, update the relevant docs.

The docs should mention what assets exist, where the DDS files live, which `.gfx` file the main agent should use or has used, which sprite names are used or proposed, which assets are placeholders, and what still needs final art. Do not leave the docs describing old or missing assets.

## 27. Contact sheets

When an asset package contains many generated or sourced images, create a contact sheet for review.

Contact sheets are for review only and never final game assets. They should make the asset name, type, selected final version, and any rejected alternatives easy to see.

## 28. Handling blocked assets

If an asset cannot be created or processed cleanly, mark it as blocked.

Record the asset name, reason blocked, what was attempted, what is needed from the user, and whether implementation can continue without it.

Do not invent a substitute asset unless the user explicitly approves it. A "substitute and report" answer to the fallback question of the upfront consultation is that approval.

