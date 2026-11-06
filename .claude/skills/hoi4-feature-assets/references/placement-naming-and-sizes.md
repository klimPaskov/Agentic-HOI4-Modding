# HOI4 Feature Assets: Placement, naming and sizes

Part of the [hoi4-feature-assets](../SKILL.md) skill. Read before choosing the folder, file name or canvas size of a final asset.

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

`hoi4-imagegen` installs each family into its own leaf folder under the feature slug and applies these exceptions.

Shared systems may use a clear shared or system folder. Do not force shared assets into a feature folder just to avoid a root directory.

When moving or adding an asset, update every `.gfx`, `.gui`, event, idea, decision, focus, localisation, and documentation reference that names the old path or sprite. Keep sprite names stable unless the engine-facing identifier itself has to change, as with achievement ids.

Researched presentation audio belongs to `hoi4-text-audio-research`. Use feature-scoped music and sound paths only when the repository already uses that convention or the parent prompt asks for it. Preserve source downloads under a documented source-audio path instead of burying them among final game files.

## 9. Standard HOI4 asset sizes

The canvas of every generated family comes from the mod's profile: its `.tools/gfx/profiles.json` row, vanilla-measured (HOI4 1.19.4.1) by default. `hoi4.image_families` shows it next to the mod's override, `python -B .tools/gfx/gfx.py size --profile <name>` checks a file against a row, and `python -B .tools/check.py quick` runs the GFX conformance checks on changed art. Each row's `source` holds the vanilla evidence, and `assets/vanilla_reference/CATALOG.md` lists the canvas of every family. The ones used most: focus 100x88, idea_spirit 60x68, idea_concern 64x64, advisor_card 65x67, decision 33x32 (missions too), decision_category_icon 52x40, decision_category_picture 114x101, report_event 210x176, news_event 397x153 (black and white), achievement 64x64, leader, commander, operative and scientist portraits 156x210, flags 82x52, 41x26 and 10x7. Counters, building, faction_logo and agency_logo are two-frame strips. `gui_texture` and `super_event` have no vanilla canvas, so the mod defines them in its profile or per request. Custom feature images match the target GUI surface or documented repository pattern.

A mod that settled other canvases records them in its own `profiles.json` rows with the source, and the tool reports the difference from vanilla. Use other sizes when the feature UI requires it.

## 10. Naming rules

Use lowercase snake_case.

Keep names stable once they are wired into `.gfx`.

Recommended filename prefixes:

- idea icons: `idea_`
- focus icons: `focus_` (`goal_` is accepted)
- decision icons: `decision_`
- decision category icons: `decision_category_`
- report event images: `report_event_`
- news event images: `news_event_`
- custom feature images: `presentation_`
- achievement icons: `achievement_`
- leader portraits: `leader_`

`hoi4-imagegen` names assets from the family prefix, the feature slug and the asset name; keep what it installs.

For feature-specific assets, include the feature slug where useful. For example, all idea assets related to a feature should go into one folder for that feature.

