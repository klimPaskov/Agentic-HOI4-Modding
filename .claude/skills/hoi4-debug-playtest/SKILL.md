---
name: hoi4-debug-playtest
description: Explicit-invocation-only HOI4 debug playtest that fixes a mod from fresh logs and tests it; never use unless the user names this skill or explicitly asks for autonomous desktop playtesting.
---

# HOI4 Autonomous Debug Playtest

Use this skill only when the user explicitly invokes it or explicitly authorizes autonomous desktop control for a Hearts of Iron IV mod test run.

Do not trigger this skill as a normal coding, review, validation, audit, or completion step. Do not add it to default agent routing. Do not infer permission from a request to implement a feature.

Launch the game in debug mode, read fresh logs, repair the one selected mod until no new attributable error remains, then run bounded gameplay and UI tests, capture screenshots, fix confirmed defects and verify the fixes in game. The skill grants no capability itself: the Capability gate, the Hard scope boundary and the Hard stops below decide what may be done.

Always apply these rules (full detail in the references):

- Edit only the one selected mod. Never touch vanilla files, Steam or launcher files, Windows settings, other mods or repositories, the user's normal saves, or unrelated Git changes. Never delete the user's logs to look clean (`references/startup-and-log-attribution.md`).
- Fix by root cause, not by suppressing a warning, and fix only lines attributable to the selected mod. An empty `error.log` is not success: the goal is no new target-mod error attributable to the run (`references/startup-and-log-attribution.md`).
- When the game must be stopped, close it gracefully; terminate only the exact launched PID, never a process by broad name (`references/startup-and-log-attribution.md`).
- Prefer normal UI over console commands. Use the console only for a deterministic prerequisite, record every command, and never use it to bypass the trigger, cost, AI choice or state transition under test. Stay as the primary country unless the brief allows switching (`references/live-gameplay-protocol.md`).
- Use dedicated saves, never overwrite an ordinary save, and checkpoint before each destructive or branching test (`references/live-gameplay-protocol.md`).
- Any human keyboard or mouse input is an immediate pause. Stop on a hard stop and write a blocked report (below).
- Fix a defect only after reproducing it once, mark each as `fixed`, `blocked`, `not_reproduced` or `needs_user_review`, and never redesign a feature to resolve unclear intent (`references/defects-evidence-and-report.md`).

Work in this order: `startup-and-log-attribution` until the startup is clean, `live-gameplay-protocol` with the `test-matrix` for the surfaces in scope, `defects-evidence-and-report` for each defect, the evidence folder and the final report.

## Reference map

- [Startup, logs and repair loop](references/startup-and-log-attribution.md): Read before launching the game, resolving the log directory, attributing log lines to the mod or repairing startup errors. Covers: Debug-mode and shortcut verification; Log-directory resolution; Fresh-log attribution rule; Startup repair loop.
- [Live gameplay test protocol](references/live-gameplay-protocol.md): Read before driving the running game: navigation, console use, checkpoints and efficiency rules. Covers: Live gameplay test protocol.
- [Generic HOI4 test matrix](references/test-matrix.md): Read when choosing which surfaces to test and what to check on each. Covers: Generic HOI4 test matrix.
- [Defects, evidence package and final report](references/defects-evidence-and-report.md): Read when a live defect is found, before keeping the evidence folder, and before writing the final report. Covers: Visual defect triage; Fix and retest loop; Evidence package; Final report format.

## 1. Capability gate

This skill defines a workflow. It does not install or grant computer-control capabilities.

<!-- HOI4_MOD_SETUP:LIVE_TESTING_PROVIDER:START -->
Live-testing provider: manual until HOI4 Mod Setup writes the selected route.
<!-- HOI4_MOD_SETUP:LIVE_TESTING_PROVIDER:END -->

Follow `hoi4-live-playtest` before any operation. Inspect the selected server tool list, use qualified tool names, and map each step below to an advertised capability. These recipes describe test goals; Windows desktop mechanics apply only to a provider that supports them. Clausewitz supports direct native Linux HOI4 1.19.2 state reads without OCR or saves, and does not promise the Live Tools launch, console, UI, or save operations. Report unsupported steps and request manual observations. Do not automatically fall back to desktop control. Manual desktop testing requires explicit user authorization and available controls.

## 2. Required invocation contract

Resolve these values from the user prompt, a supplied test brief, or the current repository. Do not search unrelated drives or folders.

- `mod_root`: absolute path to the one mod that may be edited
- `launch_target`: provider-supported debug launch target, only when launching is supported and requested
- `launch_arguments`: optional arguments when the target is an executable
- `log_root`: the active Hearts of Iron IV `logs` directory, or a bounded list of candidates
- `test_scope`: changed feature, named feature list, event list, issue list, or explicit full-mod pass
- `primary_country`: country to play when a gameplay test needs a country
- `max_repair_cycles`: default `6`, unless the user sets another limit
- `max_launch_failures`: default `2`
- `artifact_root`: default `<mod_root>\docs\testing\live_qa\<run_id>` when that path belongs in the repository, otherwise a user-approved test-output folder

When a value can be safely inferred from a provided path or repository file, infer it and record the inference. When a required value cannot be safely determined, produce a blocked preflight report rather than guessing.

## 3. Hard scope and privacy boundary

During an autonomous run:

- interact only with HOI4, its launcher when necessary, the target mod, the target mod's logs, the editor or terminal used for the target mod, and the dedicated test artifact folder
- do not inspect unrelated applications, browser tabs, messages, documents, account data, clipboard contents, or personal folders
- do not edit vanilla HOI4 files, Steam files, launcher installation files, Windows settings, the registry, unrelated mods, or unrelated repositories
- do not join multiplayer sessions or interact with online players
- do not alter achievements, cloud saves, or account settings
- do not overwrite or delete the user's normal saves
- do not reset, clean, stash, discard, or overwrite unrelated Git changes
- do not use destructive shell commands outside the explicit test artifact folder
- do not keep moving the mouse or sending keys after the user takes control

Any human keyboard or mouse intervention is an immediate pause signal. Re-read the visible state before resuming. Never fight the user's input.

## 4. Test-run isolation

Create a unique `run_id`, for example `20260713_hoi4_<scope_slug>`.

Record:

- launch target and resolved target arguments
- mod root
- active branch and commit
- pre-existing uncommitted files
- log directory selected
- game version visible in the main menu
- loaded mod or playset evidence
- screen resolution and UI scale when visible
- primary country
- test scope
- repair-cycle limits

Use a fresh non-Ironman test game or a dedicated test save named with the run ID. Never overwrite an ordinary save. Keep the game paused while configuring a test.

If a test must reuse a save, copy it to a dedicated test name first and record the source. Do not claim that a defect is reproducible from a save unless the copied test save reproduces it.

## 9. Hard stops

Stop the autonomous loop and write a blocked report when any of these occurs:

- the desktop-control capability fails or loses reliable input or screenshot feedback
- the launch target, mod root, or active log directory cannot be verified
- the wrong mod or wrong playset is loaded and correcting it would alter unrelated launcher configuration
- the same root error survives the maximum repair cycles
- the game crashes twice at the same checkpoint without enough evidence to make a bounded fix
- a fix requires changing vanilla files, another mod, Windows configuration, or account data
- a requested behavior conflicts with the mod's accepted specification
- the correct fix requires a design choice with materially different gameplay outcomes
- a source asset, licence, quote, audio track, or other required input is missing and a placeholder would be a fallback
- the repository has overlapping uncommitted changes in the exact file and the agent cannot preserve them safely
- a visual defect cannot be reproduced reliably

A hard stop is not a silent failure. Save the last screenshot, log delta, reproduction steps, suspected files, attempted fixes, and the exact decision needed.

## 15. Completion standard

The scoped run is complete only when:

- the correct debug launch path was used
- the correct mod was visibly loaded
- a clean startup checkpoint produced no new attributable blocking error
- every scoped test has a recorded result
- every confirmed defect is fixed, blocked with evidence, or explicitly marked for user review
- every fixed defect was reproduced after relaunch
- the final run produced no new attributable blocking error
- screenshots exist for important failures and fixes
- the report separates passed, failed, blocked, not covered, and not applicable cases
- no unrelated files or user saves were changed

An empty `error.log` alone is not completion. A game that launches but has broken gameplay or UI is not completion.

