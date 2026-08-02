---
name: hoi4-super-events-event-integration
description: Use when wiring a selected Super Event runtime registration to its owning HOI4 event or gameplay effect.
---

# HOI4 Super Events Event Integration

Use this selected-only add-on with the installed `hoi4-super-events` runtime and `hoi4-events`. It generalizes the proven rule that gameplay state, presentation registration, caller wiring, cleanup, documentation, and validation move together.

## Required sources

Read the installed `hoi4-super-events` skill, the relevant event contract in `hoi4-events`, the accepted plan, the current registry, the owning caller, the runtime GUI/GFX/scripted-localisation files, the project audio definitions when audio is in scope, and the permanent presentation documentation.

## Ownership

`hoi4-events` owns event namespace, triggers, options, effects, chains, AI, on-actions, and ordinary event validation. This add-on owns the boundary from the accepted gameplay transition into the installed presentation runtime. The main agent owns all final runtime and gameplay edits.

## Integration workflow

1. Confirm that the owning gameplay transition is complete before the presentation is shown.
2. Reserve one stable integer registration ID and verify that it is not already assigned to a different moment.
3. Add every image, title, description, quote, and response branch required by the installed runtime.
4. Add the project-scoped sprite, final image, and player-facing localisation using existing project naming patterns.
5. Invoke the installed show effect from one accepted caller, with explicit duplicate suppression when more than one route can reach it.
6. Wire audio only according to the accepted audio decision and the project’s verified sound conventions.
7. Clear visibility, current registration, and playback state through the installed close path.
8. Update permanent documentation and run the named acceptance scenario from the live caller.

Do not add a caller without complete registry branches, register an unreachable package, display the presentation before the announced state exists, bypass project volume behavior, or invent helpers and commands that are not present in the selected project.

## Terminal and aftermath roles

For a terminal role, establish the terminal state first, gate incompatible future systems, prevent ordinary retriggers, and ensure the complete package communicates finality. Use a defeat-aftermath role only when the defeated threat was sustained and consequential enough to reshape the campaign; the package should communicate what ended, what was lost, what remains unstable, and what follows.

## Audio boundary

The reusable runtime supports a complete visual package without audio. If the accepted project plan marks audio optional, a missing cue is an honest incomplete optional enhancement and must not break display or close cleanup.

If the accepted project plan marks audio required, the feature is incomplete until the final track, source and rights evidence, project-scoped sound ID, sound definition, playback behavior, and documentation agree. Required audio must never be replaced by a placeholder, generated test tone, undocumented file, or invented fallback.

## Validation

Validate identifier uniqueness, all runtime branches, sprite and texture resolution, localisation coverage, caller reachability, state ordering, duplicate suppression, close cleanup, optional or required audio behavior, documentation alignment, and the named in-game scenario. Report unsupported or unverified project routes honestly.

## Update triggers

Update this skill when caller ownership, registration branches, show or close behavior, duplicate suppression, audio wiring, terminal-state handling, documentation, or acceptance scenarios change.

## Completion standard

The gameplay transition and the selected presentation package behave as one coherent feature, and no caller, registry branch, asset, localisation key, required cue, cleanup path, documentation record, or acceptance result is missing or contradictory.
