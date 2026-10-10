# Asset planning and asset, text, and audio handoffs

This reference belongs to the `hoi4-feature-planning` skill and holds complete sections moved out of `SKILL.md` to keep it within the single-read ceiling. Every rule here is as binding as the rules in `SKILL.md`.

## 13. Asset planning

The feature specification should identify all important visual assets. For major features, assume every visible system needs asset planning unless the spec explicitly explains why it does not.

Consider whether the feature needs:

- idea icons
- national spirit icons
- focus icons for every focus or focus-family in each mapped tree
- decision category icons
- decision icons
- achievement icons
- news event pictures
- report event pictures
- custom feature images for custom feature UI when the repository has such a surface
- leader portraits
- council, committee, regency, cult, junta, or symbolic leadership portraits
- faction emblems
- flags for every new country, modified country identity, ideology variant, focus-route variant, puppet identity, and major cosmetic transformation
- UI
- animated decision category seals, mechanic-window elements, warning pulses, route emblems, hover loops, selected states, glow loops, float loops, particle loops, and animated leader portraits when motion clarifies the mechanic
- progression-state variants
- static fallbacks for every animated UI piece, route emblem, icon, or portrait
- country-selection, feature-log, or custom-window graphics when relevant

Asset generation, sourcing, cropping, resizing, DDS conversion, file placement, sprite handoff notes, and manifests belong to `hoi4-feature-assets`. Animated frame planning and frame-sheet handoff requirements belong to `hoi4-frame-animation`. Final `.gfx` wiring belongs to the main implementation agent unless a parent prompt explicitly grants that scope.

This skill defines required assets, their meaning, source mode, and any visible states that benefit from animation. Do not infer an optional family solely from a gameplay consumer. Record the accepted requirement before requesting its production.

Historical or real-world assets need special care. Historical flags and symbols should be sourced from reliable references. `hoi4_portrait_creator` owns sourced real portraits and image-generator fictional portraits, including processing and wiring. Generated non-portrait art is appropriate for fictional flags, invented extreme-route identities, idea icons, focus icons, decision icons, achievements, faction emblems, UI art, and fictional or alternate-history report, news, or custom feature images unless the user says otherwise.

### Reference examples for asset planning

When a spec or asset prompt asks for generated or sourced assets, tell the asset agent to inspect the matching reference examples before creating anything.

Use repo-relative project paths:

```text
.claude/skills/hoi4-feature-assets/assets/vanilla_reference/README.md
.claude/skills/hoi4-feature-assets/assets/vanilla_reference/CATALOG.md
.claude/skills/hoi4-feature-assets/assets/vanilla_reference/icons
.claude/skills/hoi4-feature-assets/assets/vanilla_reference/event_art
.claude/skills/hoi4-feature-assets/assets/vanilla_reference/flags
.claude/skills/hoi4-feature-assets/assets/vanilla_reference/portraits
.claude/skills/hoi4-feature-assets/assets/vanilla_reference/units
```

Reference mapping:

- idea and national spirit icons: `.claude/skills/hoi4-feature-assets/assets/vanilla_reference/icons/ideas/`
- news event images: `.claude/skills/hoi4-feature-assets/assets/vanilla_reference/event_art/news/`
- report event images: `.claude/skills/hoi4-feature-assets/assets/vanilla_reference/event_art/report/`
- large presentation art: use the report, news, or custom feature reference set that matches the owning UI surface
- technology and special-project icons: `.claude/skills/hoi4-feature-assets/assets/vanilla_reference/icons/technologies/` and `.claude/skills/hoi4-feature-assets/assets/vanilla_reference/icons/special_projects/`
- achievement icons: `.claude/skills/hoi4-feature-assets/assets/vanilla_reference/icons/achievements/`; the reusable not-eligible overlay is `.claude/skills/hoi4-feature-assets/assets/vanilla_reference/icons/achievements/template/overlay.png`
- decisions, missions, and decision-category icons: their separate folders under `.claude/skills/hoi4-feature-assets/assets/vanilla_reference/icons/`
- flags: complete normal, medium, and small sets under `.claude/skills/hoi4-feature-assets/assets/vanilla_reference/flags/`
- focus icons: `.claude/skills/hoi4-feature-assets/assets/vanilla_reference/icons/national_focus/`
- officer-corps, balance-of-power, faction, and other system icons: their matching folders under `.claude/skills/hoi4-feature-assets/assets/vanilla_reference/icons/`
- country-leader, commander, operative, advisor, and high-command portraits: their matching folders under `.claude/skills/hoi4-feature-assets/assets/vanilla_reference/portraits/`
- unit visual references: the separate equipment, land, air, naval, and 3D-model families under `.claude/skills/hoi4-feature-assets/assets/vanilla_reference/units/`

The feature spec does not need to analyze those images itself. It should make the handoff explicit so the asset agent knows which example set to inspect before generation, sourcing, cropping, or wiring.

## 14. Asset prompt handoff

After the full feature specification is complete, create a separate asset prompt file for `hoi4-feature-assets`.

The asset prompt should include:

- required assets
- visual style
- symbols and motifs
- target sizes
- intended in-game use
- country package asset coverage, including base flags, ideology flags, focus-route flags, cosmetic flags, leaders, portraits, and faction emblems
- suggested filenames
- suggested sprite names
- suggested static fallback sprite names and animated sprite names when animation is planned
- whether each asset is for a feature, report event, news event, custom feature image, decision, idea, focus, achievement, flag, leader portrait, faction emblem, or UI element
- animation brief needs for every animated asset, including state logic, frame count target, target frame size, expected sheet size, frames per second, loop behavior, `play_on_show` expectation, static fallback, source mode, and target `.gfx` or `.gui` surface when known
- achievement icon list with completed icon directions for every achievement
- manifest requirements
- source mode, including whether a flag, symbol, or portrait must be sourced historically instead of generated
- reference example folder that must be inspected before asset work

The asset prompt must state the correct source mode where relevant.

It must also state the relevant reference folder from the list above when a matching folder exists.

Use `hoi4-feature-assets` rules for source selection. Symbolic icons usually use the image generator. News event images, report event images, and custom feature images may be sourced or generated. prefer generated assets for fictional, alternate-history, symbolic, extreme-route, or unique scenes, and sourced assets for real historical people, real photographed events, and real archival artifacts. Historical flags and historically attested symbols should be sourced and documented, then converted to HOI4 flag sizes. Fictional, supernatural, invented, or alternate-history flags can use the image generator through `hoi4-feature-assets` when appropriate.

Do not make the asset prompt vague. If a country has multiple cosmetic identities, ideology names, focus-route transformations, or leader changes, list the required assets for each visible identity state. Include animation and a static fallback only when the presentation-choice pass supports motion. Apply the category-picture eligibility gate to every requested picture.

## 15. HOI4 asset size reference

Use these sizes when planning assets:

- report event images: 210x176
- news event images: 397x153, black and white
- leader portraits: 156x210
- commander portraits: 156x210
- operative portraits: 156x210
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

## 16. Asset style reference

When planning visuals, use these style expectations.

Report and news event images should look like documentary photographs, whether sourced or generated. News event images should be black and white.

Large feature presentation images should have a strong central composition, clear dramatic theme, readable subject, and enough contrast for HOI4 UI.

Focus icons should look like HOI4 focus icons, with a central symbol, readable silhouette, aged texture, painterly detail, and strong contrast.

Idea and national spirit icons should look like compact HOI4 icon art. They need strong symbolic shapes and clear readability at 64x64. They are similar to focus icons, but they are missing the main frame.

Achievement icons should be readable at 64x64 and have a clear completion theme. The completed version is generated first. Grey and not-eligible variants can be produced later.

Flags should use clean symbols that remain readable at HOI4 flag sizes.

Progression-state variants may include selected, dim, active, locked, completed, rejected, damaged, corrupted, urgent, meter-fill, and bar-fill states.

## 17. Text and audio research handoff

If the feature has one or more sourced text or audio needs, create a separate prompt file for `hoi4-text-audio-research`.

For each research package, include:

- feature role
- trigger moment or surface where the material appears
- tone
- quote direction, not quote text unless researched and sourced
- cultural remark, slogan, or allusion direction, not final wording unless researched and sourced
- audio mood, not a final track unless researched and licensed
- whether the material supports a reveal, escalation, defeat moment, aftermath moment, route payoff, achievement theme, menu cue, custom UI surface, or other feature role
- any special constraints from the feature spec

The `hoi4-text-audio-research` prompt should ask the researcher to:

- find a real quote using the repository research workflow from `AGENTS.md`
- verify quote wording and attribution
- find a meaningful cultural remark, reference, allusion, slogan, or short line where appropriate
- follow copyright limits for songs, films, books, games, poems, and other protected works
- find suitable public domain or clearly licensed audio when audio is required
- document all sources, license notes, rights notes, and uncertainties
- mark unclear attribution or licensing as blocked instead of treating it as usable

Do not claim a quote, cultural reference, or audio track is usable without checking.

If a license or attribution is unclear, mark it as uncertain or unsuitable.

The prompt must explicitly state that unresearched button text, quotes, cultural remarks, slogans, lyric fragments, allusions, and audio choices are blockers. The implementation agent must not convert research directions, working labels, achievement names, asset names, or draft-like wording into final localisation.
