# Project rules: Event, focus tree and visual asset integration

Part of the [hoi4-project-rules](../SKILL.md) skill. `CLAUDE.md` summarizes sections 6, 7 and 8. Read before wiring an event, a focus tree or a visual asset into the mod.

## 6. Event Integration

For event implementation, use `hoi4-events`.

1. Wire the event script, namespace or category registration, trigger or firing route, localisation and name mappings, and any maintained event-log or event-detail surfaces together in the same change.
2. If the event has evolutions, terminal branches, or a super-event outcome, wire the related log entries, super-event integration, assets, audio, and localisation in the same change.
3. Keep gameplay files, specs, implementation docs, maintained spreadsheets or presentations, asset manifests, and player-facing detail text aligned.
4. Treat any project-specific event id, entry-root format, catalog exporter, or maintained log framework as a repository source-of-truth rule and preserve it explicitly in this file.

## 7. Focus Trees and Large Content

For national focus work, use `hoi4-focus-trees` before editing. That skill is the detailed source of truth for focus-tree depth, reward variety, route logic, AI, localisation, icons, ideas, country identity changes, focus-decision integration, route coverage proof, and completion standards.

Before claiming focus-tree completion, use the appropriate audit route from `hoi4-subagents` if this repo uses audit subagents. If a tree works but feels shallow, duplicated, generic, or disconnected from gameplay, use `hoi4-improvement-loop` and consider a plan-mode pass from `hoi4_improvement_loop_planner` if this repo uses one.

## 8. Agent-generated Visual Assets

For final visual assets, use `hoi4-feature-assets`. That skill is the detailed source of truth for image generation rules, 2D asset classification, and the handoff boundary for 3D model packages.

Use `hoi4-imagegen` (MCP tools `hoi4.image_*`) for generated artwork. HOI4 Mod Setup may replace the default below with the selected provider’s details. Make one image per call. The tool proves transparency from the saved pixels. If no provider is configured, ask the maintainer for a route.

(The default image-generation route and the provider markers are in `CLAUDE.md` section 8.)

For animated visual assets, use `hoi4-frame-animation` in addition to `hoi4-feature-assets` for frame-sheet animation. Use `hoi4-3d-model-pipeline` for skeletal unit or entity actions. Final animation assets must be built from real planned frames or real exported skeletal actions and must not be transform-only mockups.

Use `hoi4-subagents` for detailed asset routing. Native advisor and high-command cards use the `65x67` contract in `hoi4-feature-assets`.
