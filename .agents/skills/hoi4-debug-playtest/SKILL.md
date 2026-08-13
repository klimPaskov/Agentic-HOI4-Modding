---
name: hoi4-debug-playtest
description: Explicit-invocation-only workflow for controlling a Windows desktop to launch Hearts of Iron IV in debug mode, inspect fresh logs, repair one selected mod, relaunch until attributable errors are gone, run bounded gameplay and UI tests, capture screenshots, fix confirmed defects, and verify the fixes in game. Never use unless the user names this skill or explicitly asks for autonomous desktop playtesting.
---

# HOI4 Autonomous Debug Playtest

Use this skill only when the user explicitly invokes it or explicitly authorizes autonomous desktop control for a Hearts of Iron IV mod test run.

Do not trigger this skill as a normal coding, review, validation, audit, or completion step. Do not add it to default agent routing. Do not infer permission from a request to implement a feature.

## 1. Capability gate

This skill defines a workflow. It does not install or grant computer-control capabilities.

Before starting, confirm that the current Codex environment exposes all of the following:

- a desktop-control tool that can identify windows, capture screenshots, click, type, send keys, and inspect the visible result
- filesystem access to the selected mod repository and the HOI4 log directory
- process-launch capability for a Windows executable or shortcut
- process inspection and bounded process termination
- an editing environment for the selected mod

If desktop control is unavailable, stop and report that the skill cannot operate the computer in the current environment. Do not pretend that shell access alone is equivalent to playing the game.

If screenshots cannot be captured or retained, stop before visual testing. Log-only validation is not a substitute for the requested live test.

## 2. Required invocation contract

Resolve these values from the user prompt, a supplied test brief, or the current repository. Do not search unrelated drives or folders.

- `mod_root`: absolute Windows path to the one mod that may be edited
- `launch_target`: absolute path to a debug-enabled `.lnk` or executable
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

## 5. Debug-mode and shortcut verification

A `.lnk` may contain important arguments. Launch the shortcut itself so its configured arguments are preserved.

When verification is needed, use a bounded PowerShell inspection such as:

```powershell
$wsh = New-Object -ComObject WScript.Shell
$link = $wsh.CreateShortcut($launch_target)
$link.TargetPath
$link.Arguments
$link.WorkingDirectory
```

Treat either of these as acceptable evidence of debug mode:

- the shortcut or executable arguments explicitly include the intended debug flag
- the user explicitly states that the supplied shortcut is debug-enabled and fresh debug logs are produced after launch

Do not rewrite the user's shortcut unless the user explicitly requests it.

For a shortcut, launch with a native Windows action such as:

```powershell
Start-Process -FilePath $launch_target
```

For an executable, pass the separately recorded argument list. Do not concatenate untrusted text into one shell command.

## 6. Log-directory resolution

Prefer a path supplied by the user. Otherwise inspect only these bounded candidates and select the directory whose logs become fresh after launch:

```text
%USERPROFILE%\Documents\Paradox Interactive\Hearts of Iron IV\logs
%OneDrive%\Documents\Paradox Interactive\Hearts of Iron IV\logs
%OneDriveConsumer%\Documents\Paradox Interactive\Hearts of Iron IV\logs
```

Do not choose a log directory only because it exists. Confirm freshness by comparing file modification times before and after the current launch.

Primary files:

- `error.log` for script, content, GUI, asset, and localisation errors
- `exceptions.log` and crash folders when the game crashes
- `game.log` for intentional debug output and runtime breadcrumbs
- `setup.log` when startup or content loading fails
- `text.log` for duplicate loc keys

Copy the pre-launch versions into the run artifact folder. Record file sizes, timestamps, and hashes. Do not delete the user's logs merely to make them look clean.

## 7. Fresh-log attribution rule

The objective is not an empty `error.log`. The objective is no new target-mod error attributable to the tested run.

For each launch:

1. Record pre-launch log size, timestamp, and hash.
2. Launch HOI4.
3. Wait for a stable visible checkpoint, such as the main menu, country selection, or the exact tested feature.
4. Copy the current logs.
5. Compute the current-run delta by timestamp, byte offset, or a before-and-after comparison.
6. Normalize repeated messages and count occurrences without hiding the first full example.
7. Classify every new line as:
   - target-mod blocking error
   - target-mod warning that affects the tested behavior
   - target-mod warning with no demonstrated effect
   - engine, vanilla, launcher, or another-mod message
   - uncertain attribution
8. Fix only lines attributable to the selected mod, unless the user explicitly expands scope.

A path, namespace, localisation key, sprite name, event ID, focus ID, decision ID, or script identifier from the target mod is strong attribution evidence. A generic engine line without target-mod evidence is not enough to justify editing random files.

Do not dismiss a new error introduced after the agent's own patch as pre-existing. Treat it as part of the current change set until disproven with evidence.

## 8. Startup repair loop

Before gameplay testing, reach a stable clean startup checkpoint.

For each repair cycle:

1. Capture the current screen and current log delta.
2. Save the exact error messages, counts, paths, and any line numbers.
3. Close HOI4 gracefully through the game UI when possible.
4. Wait for the launched HOI4 process to exit.
5. If the game is unresponsive, capture evidence, identify the exact launched PID, and terminate only that process. Never kill processes by a broad name when the PID is known.
6. Read the target repository's instructions and the system-specific modding references required for the files being changed.
7. Reproduce the error statically where possible with targeted search.
8. Make the smallest coherent fix that addresses the root cause.
9. Run task-specific static checks that can catch the same failure before relaunch.
10. Relaunch through the same debug target.
11. Verify the original error is absent from the fresh delta and that no new attributable error replaced it.
12. Update the repair ledger.

Continue until the clean-startup criterion is met or a hard stop is reached.

Do not fix warnings by suppressing, deleting, or renaming content without understanding the gameplay consequence. Do not replace missing content with placeholders or fallbacks unless the user approved that exact fallback.

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

## 10. Live gameplay test protocol

After startup is clean, test the requested feature as a player would.

### 10.1 Navigation discipline

- Use screenshot and visual understanding as the primary UI feedback.
- Re-anchor on visible labels, windows, icons, and stable geometry after every major screen transition.
- Do not reuse blind absolute coordinates after resolution changes, window movement, popups, or UI scaling changes.
- Keep the game paused while opening menus or setting up a deterministic state.
- Use conservative game speeds and monitor the screen. Do not leave maximum speed unattended.
- Dismiss unexpected popups only after capturing them and identifying whether they belong to the test.
- Capture a screenshot before and after every action that exposes a defect.

### 10.2 Primary-country rule

Stay as the configured primary country unless the test brief explicitly permits tag switching or a separate test case requires another country.

If a feature cannot be reached from the primary country, record it as not covered in single-country mode. Do not silently tag-switch and then claim single-country coverage.

### 10.3 Console and debug-command policy

Prefer normal UI, decisions, focuses, and mod-provided debug or scenario controls.

Use console or debug commands only to create a deterministic prerequisite state, shorten dead time, or reproduce a reported issue. Record every command and its purpose.

Never use a console command to bypass the exact trigger, cost, AI choice, or state transition that the test is supposed to validate.

### 10.4 Checkpoint policy

Create a dedicated checkpoint before each destructive or branching test. Return to a clean checkpoint when one test would contaminate the next.

Use separate saves when testing:

- mutually exclusive routes
- event branches with persistent global flags
- country creation or civil wars
- world-end or terminal paths
- focus-tree route choices
- decisions that consume unique resources
- scripted GUI state that cannot be reset safely

## 11. Generic HOI4 test matrix

Select only the surfaces in scope, but do not ignore an adjacent surface that the feature visibly depends on.

### Startup and content loading

- game reaches the main menu
- correct mod is visibly loaded
- new game reaches country selection
- selected country loads into the map
- no new attributable startup error appears
- a dedicated test save can be created and loaded

### Events and news

- event triggers under intended conditions
- event does not trigger under a named invalid condition when eligibility is in scope
- title, description, options, images, sounds, and tooltips appear
- no raw localisation keys appear
- each option produces the visible result it describes
- follow-up events occur once and in the intended order
- hidden effects do not duplicate visible option effects
- event targets and actors remain correct across follow-ups

### Decisions, missions, and categories

- category visibility and lifecycle are correct
- costs and blocked requirements are readable
- buttons enable and disable at the correct state
- timers advance and resolve
- success, failure, cancellation, and cleanup work
- obsolete decisions disappear
- repeated use does not create free rewards or stale targets
- AI has a valid path when the system is AI-usable

### Focus trees

- correct tree loads for the correct country and origin
- branches are visible, readable, and connected
- prerequisites and mutual exclusions behave as intended
- focus icons and localisation are present
- completion rewards and unlocked content occur once
- route-specific decisions, events, leaders, flags, and ideas appear
- AI does not choose invalid or impossible routes

### Countries and map state

- tag, name, adjective, flag, portrait, leader, parties, capital, cores, claims, ownership, and controller state are coherent
- released or transformed countries receive their intended tree, ideas, units, equipment, and AI
- no country is accidentally deleted or left landless unless that is the intended result
- annexation, release, civil war, transfer, peace, and cleanup produce valid map state

### Localisation and dynamic text

- no raw keys, broken format codes, missing icons, or wrong scope names appear
- dynamic values update after the underlying state changes
- integer values do not show unwanted decimal noise
- hidden content is not spoiled early
- tooltips describe visible requirements and consequences

### GUI and graphics

- windows open, close, move, and return to the correct state
- tabs, lists, scroll areas, sliders, buttons, hover states, and selected states work
- text does not overlap, clip, escape its container, or sit behind another layer
- decorative layers do not intercept clicks
- no pink textures, checkerboards, missing sprites, stretched assets, wrong flags, or wrong portraits appear
- animated sprites loop correctly and have a usable static fallback
- UI remains usable at the current resolution and scale

### Runtime, AI, and pacing

- the feature continues working after time advances
- repeated ticks do not spam events or logs
- AI uses actions only when valid
- cleanup occurs after war, annexation, route change, target death, or feature completion
- no obvious performance stall, runaway loop, or uncontrolled decision spam appears

### Save and reload

- the dedicated test save loads
- important variables, flags, event targets, missions, GUI state, and country identity persist correctly
- temporary state that should be cleared does not return after reload

## 12. Visual defect triage

For each visual or gameplay defect:

1. Capture a screenshot with the full relevant window and enough context to locate it.
2. Record the exact UI path and action sequence.
3. Record the expected behavior from the accepted spec, existing documentation, or clear vanilla pattern.
4. Record the actual visible behavior.
5. Check the fresh log delta at the same moment.
6. Identify the likely owning file or surface.
7. Reproduce once from a clean checkpoint.
8. Fix only after reproduction.

Do not turn taste preferences into bugs. A visual issue is confirmed when it violates accepted design, hides information, blocks input, shows the wrong state, uses missing content, or breaks a stable project pattern.

When the intended design is unclear, mark `needs_user_review` instead of redesigning the feature autonomously.

## 13. Fix and retest loop

When a live defect is confirmed:

1. Save the dedicated test state and evidence.
2. Close HOI4 safely.
3. Read the repository instructions and the skill or documentation for the affected system.
4. Patch the smallest complete surface, including directly dependent localisation, GUI, GFX, or cleanup when required.
5. Run targeted static checks.
6. Relaunch through the same debug target.
7. Return to the same test setup or a clean equivalent setup.
8. Reproduce the original sequence.
9. Capture the corrected state.
10. Check the fresh log delta.
11. Run one nearby regression test that could have been affected.
12. Mark the issue `fixed`, `blocked`, `not_reproduced`, or `needs_user_review`.

Do not continue to unrelated tests while a new blocking startup or runtime error from the current patch remains.

## 14. Evidence package

Keep the run auditable. Recommended structure:

```text
<artifact_root>\
  run_manifest.md
  test_report.md
  coverage.csv
  console_commands.md
  logs\
    preflight_error.log
    launch_01_error.log
    launch_01_delta.log
    final_error.log
    final_delta.log
  screenshots\
    001_main_menu.png
    002_test_setup.png
    003_issue_before.png
    004_issue_after.png
```

Do not copy large ordinary save files into the repository unless the user requests them. Record dedicated test-save names and locations instead.

Each screenshot filename should include a sequence, test ID, and state such as `before`, `after`, or `pass`.

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

## 16. Final report format

Use these sections:

```markdown
# HOI4 Autonomous Debug Playtest Report

## Run configuration
## Launch and log evidence
## Repair cycles
## Test coverage
## Confirmed defects and fixes
## Screenshots
## Files changed
## Remaining blockers and needs-user-review items
## Simplifications or fallbacks
## Final status
```

State explicitly whether any fallback or simplification was used. Do not call the run complete when a scoped defect remains unresolved.
