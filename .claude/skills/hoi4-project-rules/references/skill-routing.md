# Project rules: Skill routing

Part of the [hoi4-project-rules](../SKILL.md) skill. `CLAUDE.md` summarizes section 0 (Repo Skills). Read when deciding which repo skill governs a task.

### Repo Skills

Use repo skills as required implementation guidance, not as optional notes.

- Use `hoi4-events` for ordinary HOI4 event implementation, event chains, news events, report events, localisation, on_actions, documentation, and validation.
- Use `hoi4-feature-planning` when designing or expanding feature ideas, feature mechanics, country packages, focus-tree route plans, decision plans, achievements, AI behavior, asset needs, text and audio research gates, and implementation-ready specifications before coding.
- Use `hoi4-feature-assets` when a task needs visual assets, icons, flags, portraits, native advisor or high-command cards, UI art, report images, news images, achievement icons, final DDS files, asset manifests, or sprite handoff notes; route 3D geometry, materials, skeletal actions, `.mesh`/`.anim` exports, and reimport evidence to `hoi4-3d-model-pipeline`.
- Use `hoi4-imagegen` to make or import any 2D asset of the 40 families (free plan, generation, process, validate, review, install); `hoi4-feature-assets` keeps the sources, naming and handoff rules.
- Use `hoi4-feature-planning` to plan 3D unit and building profiles, exact-one-image Meshy inputs, vanilla scale calibration, action roles, entity consumers, map placement, and runtime acceptance evidence whenever a feature needs a model.
- Use `hoi4-3d-model-pipeline` for every custom HOI4 3D model: sourced and refined inputs, generation with the profile's model (currently Meshy 7), Blender component, rig, weight, and action work, PDX textures, sourced custom-unit sound, bespoke vanilla-green counters, `.mesh`/`.anim` export, reimport proof, and runtime handoffs. The skill defines the routes and the per-job credit budget that the user approves once.
- Use `hoi4-frame-animation` when a task needs animated sprites, frame sequences, sprite sheets, GIF previews, animated UI pieces, animated portraits, hover loops, pulse loops, route emblems, or frame-by-frame visual packages. This skill forbids final animation made only by moving, scaling, rotating, warping, blurring, recoloring, or filtering one still image.
- Use `hoi4-text-audio-research` when a task needs sourced quotes, cultural references, title-like references, slogans, or music and audio research.
- Use `hoi4-super-events` when designing, researching, wiring, auditing, or documenting a super-event, including its sourced quote, image, sound-only audio package, runtime playback, and durable provenance.
- Use `hoi4-focus-trees` before editing national focus trees.
- Use `hoi4-decisions-missions` before editing decisions/missions.
- Use `hoi4-scripted-gui` for scripted GUI composition, reference-image mapping, content and interaction budgets, layout, iterative MCP live previews, click-region review, state and resolution coverage, and visual acceptance. `hoi4-decisions-missions` retains gameplay-changing control integrity, costs, effects, AI, cleanup, and balance.
- Use `hoi4-native-raids` for native raid scopes, outcome dispatch, native costs, and final target validation when editing `common/raids/`.
- Use `hoi4-mtth` when MTTH logic or weighted timing would reduce clutter or make AI and release logic clearer.
- Use `hoi4-investigate` for any bug, regression, or described crash before writing a fix, and to check a "done" report.
- Use the HOI4 system skills for engine systems: `hoi4-equipment` (equipment, modules, designers, production), `hoi4-technology-doctrines` (technologies, folders, doctrines), `hoi4-units-divisions` (sub-units, templates, orders of battle), `hoi4-characters-leaders` (characters, leaders, advisors, traits), `hoi4-ideas-modifiers` (ideas, spirits, laws, dynamic modifiers), `hoi4-map-states` (map and state data, buildings, supply), `hoi4-diplomacy-war` (diplomacy, factions, subjects, wars, peace), and `hoi4-ai-strategies` (AI strategies and weights).
- Use `hoi4-localisation` for localisation files, keys, loc commands, `§` and `£` codes and scripted localisation, `hoi4-on-actions` for `common/on_actions` hooks, `hoi4-ideologies` for `common/ideologies`, parties and popularities, and `hoi4-scripted-triggers-effects` for reusable scripted effects and triggers.
- Use `hoi4-subagents` when coordinating project subagents, routing bounded work, or defining parent/subagent ownership boundaries.
- Use `hoi4-improvement-loop` when an implemented or planned mechanic needs recursive depth expansion, spec addenda, improvement handoffs, or checks for shallow, duplicated, generic, disconnected, or low-impact content.
- Use `hoi4-save-inspection` whenever the user supplies a save, and when runtime state would settle a question that source reading cannot: why a decision or focus is unavailable, what an action changed, whether state survives save and reload, what the AI did, whether script state leaks, or how an engine rule behaves.
- Use `xlsx` for repository-maintained spreadsheet or delimited-table work. Establish the editable source of truth first, preserve existing workbook structure and formulas, regenerate declared exports rather than editing them, and require successful recalculation with no formula errors when formulas change.

`hoi4-debug-playtest` is never part of normal coding, validation, audit, or completion routing. Use it only when the user explicitly names the skill or explicitly authorizes autonomous desktop playtesting for the current task; otherwise live game and launcher testing remain user-owned.
