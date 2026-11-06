# Project rules: Localisation, UI and naming

Part of the [hoi4-project-rules](../SKILL.md) skill. `CLAUDE.md` summarizes sections 2 and 3. Read before adding anything that appears on screen, and before naming scripted effects, triggers or variables.

In this file `GAME` is the vanilla Hearts of Iron IV folder, `WORKSHOP` the Workshop content folder and `PREFIX` the mod's script prefix. `CLAUDE.md` names all three.

## 2. Localisation and UI

Localisation and UI must always be kept in sync with gameplay changes.

1. Localisation files must be encoded as **UTF 8 with BOM**. Wrong encoding breaks strings in game.
2. When you add or rename anything that appears on screen, update localisation in the same change.
3. In scripted localisation, do not write format characters like `§` or `£` directly.
4. Player-facing game text must describe the current world state and player choices, not implementation history or tuning mechanics. Do not say a value was capped, hardcoded, newly added, reworked, or changed because of an update request, keep those notes in docs or comments instead.
5. Localisation keys:
   - Do not use `:0`. Write keys as `key_name: "Text"` without `0` and without a leading space before the key.
   - Keep key names consistent and readable. No unnecessary prefixes.
6. Icons and UI assets:
   - Define icons in `interface/...` and keep naming stable.
   - When something needs icons, define them in a correct `.gfx` file. If final sprites are not part of the task, tell the user what folder to put them in and what names to use.
   - Use placeholder sprites only when the user has approved a pending placeholder or an owning skill explicitly requires a sourced placeholder. Keep the final filename stable and report the asset as pending until its approved replacement is installed.
   - Register new UI assets before requesting art so filenames do not need to change later.
   - Static or animated decision-category pictures are allowed only for simple categories (a description, ordinary decisions, basic value tables) and an animated one needs a static fallback; follow the complete eligibility contract in `hoi4-decisions-missions`.
7. A flag trigger such as `has_country_flag` inside a player-visible requirement block (`available`, `allow`, `bypass`, and similar) uses the flag name as its tooltip localisation key, so an unlocalised flag shows its raw identifier to the player. Give a player-meaningful flag a localisation key, or wrap implementation-only checks in `hidden_trigger` and state the real requirement with `custom_trigger_tooltip`.

## 3. Naming and Prefix Rules

Use prefixes only where they are needed.

Add prefixes if a folder is dedicated to this mod's files that all share the prefix. Do not add the mod prefix (`PREFIX`) to variable names, scripted effects, or scripted triggers unless the surrounding context uses it consistently.
Prefer short, descriptive names that reflect function and scope.

Unnecessary prefixes make code harder to read and maintain. Keep names clean.
