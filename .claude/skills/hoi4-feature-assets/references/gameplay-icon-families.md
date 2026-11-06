# HOI4 Feature Assets: Gameplay icon families

Part of the [hoi4-feature-assets](../SKILL.md) skill. Read before making any focus, idea, spirit, decision, category, achievement or other gameplay icon, and before reusing art across icon types.

## 5.2 Icon type separation rules

Focus, idea, national-spirit, officer-corps, decision, mission, decision-category, achievement, technology, special-project, balance-of-power, intelligence-agency, intelligence-operation, commander-trait, medal, military-raid, state-modifier, MIO, faction, building, and modifier icons are separate asset types.

Never treat focus, idea, and decision icons as interchangeable, and never satisfy one by resizing, cropping, shrinking, recoloring, padding, or lightly editing another. Each is its own `hoi4-imagegen` family, and the tool refuses another family's size or pixels (`GFX-FAMILY-MISMATCH`, `GFX-FAMILY-REUSE`). Each icon type needs its own brief, reference inspection, source artwork, target size, filename prefix, manifest entry, and final DDS.

Shared visual themes are allowed only when every icon is still designed for its own in-game use:

- focus icons should read as full HOI4 focus art at the `focus` profile canvas (vanilla 100x88) with focus-tree style detail and composition
- idea and national spirit icons should read as compact symbolic spirit art at the `idea_spirit` canvas (vanilla 60x68) without borrowing the full focus icon frame
- decision icons should read clearly at the `decision` canvas (vanilla 33x32) with simpler shapes, stronger silhouettes, and less interior detail
- decision category icons should be designed for the category button or scripted GUI surface, not derived from a focus icon
- officer corps spirit icons should follow the vanilla officer corps spirit look and 45x45 transparent style
- achievement icons should follow the achievement rules and variants
- intelligence-agency and intelligence-operation icons must follow their own agency or operation UI precedent rather than a generic decision treatment
- commander traits, medals, military raids, state modifiers, MIOs, factions, buildings, and modifier icons must follow the matching canonical folder and owning vanilla definition; do not force these families onto a blanket 32x32 or 64x64 canvas
- frame strips, indexed building sprites, and multi-state modifier art must retain their frame order and frame count rather than being treated as a single standalone icon; `python -B .tools/gfx/gfx.py sprites --paths <the .gfx file>` warns when a strip's width does not divide by its `noOfFrames`

If a mechanic needs matching focus, idea, and decision visuals, build them as a coordinated icon family. A coordinated family can share subject matter, symbols, colors, and lore cues, but each member still needs separate source art or a separate generated output designed for its target size and UI role.

The manifest must record the exact asset type for every icon and should note when icons are part of a coordinated family. Do not mark an icon complete if it only exists as a resized version of another icon type.

## 16. Idea and national spirit icons

Idea and national spirit icons should look like compact HOI4-style icon art.

They should have:

- strong central symbol
- clear silhouette
- aged texture
- strong contrast
- readable meaning at the small canvas
- no generated text

Canvas: the `idea_spirit` profile (vanilla 60x68). Industrial concerns and manufacturers are `idea_concern` (64x64) and advisor cards are `advisor_card` (65x67). Use `idea_` filename prefix.

Use `hoi4.image_icon` (`idea_spirit`, `idea_concern` or `officer_corps_spirit`) for the base artwork unless the user provides or requests a specific source image.

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

Canvas: the `focus` profile (vanilla 100x88). Use `focus_` filename prefix (`goal_` is accepted); the tool also writes the `_shine` companion sprite.

Every focus icon should support the focus tree's story, ideology, or gameplay purpose.

Use `hoi4.image_icon` with `family: focus` for the base artwork unless the user provides or requests a specific source image.

Inspect `icons/national_focus/` and the matching row in `CATALOG.md` before generating or processing focus icons. Do not force every focus source onto an older nominal canvas when the owning sprite and current vanilla precedent use a different native canvas.

## 18. Decision icons

Decision icons must remain readable at very small size.

Use:

- simple symbolic composition
- strong contrast
- clear central shape
- limited small detail
- no generated text

Canvas: the `decision` profile (vanilla 33x32). Use `decision_` filename prefix.

Decision category icons may use:

```text
decision_category_
```

Use `hoi4.image_icon` (`decision` or `decision_category_icon`) for the base artwork unless the user provides or requests a specific source image.

Inspect `icons/decisions/` or `icons/decision_categories/` as appropriate before generating or processing decision-system icons. Missions use the `decision` family (there is no mission folder) but still need mission-specific semantic readability.

## 18.1 Decision category pictures

Read [`references/icon-and-ui-families.md`](icon-and-ui-families.md) whenever a task creates decision category pictures or advisor and high-command portrait icons. It contains the complete standard for this section and its subsections.

## Additional gameplay icon families

Route additional icon work by the exact UI surface:

- intelligence identity and action: `icons/intelligence_agency/` and `icons/intelligence_operations/`
- commander progression and honours: `icons/commander_traits/` and `icons/medals/`
- operations and world state: `icons/military_raids/` and `icons/state_modifiers/`
- organizations and map/economy identity: `icons/military_industrial_organizations/`, `icons/factions/`, and `icons/buildings/`
- generic or text-linked modifier presentation: `icons/modifiers/`

Each is its own `hoi4-imagegen` family (`hoi4.image_families` lists them). Read the matching canonical catalog entries and inspect the owning `.gfx`, `.gui`, or database definition before choosing canvas, frame layout, transparency, or filename. These families are not reskinned decision or idea icons. When a source is a strip or contains several UI states, preserve its frame semantics and document them in the manifest and handoff.

## 19. Achievement icons

Read [`references/achievement-icons.md`](achievement-icons.md) whenever a task creates or changes achievement icons. It contains the complete standard for this section and its subsections.

