# HOI4 Autonomous Debug Playtest: Live gameplay test protocol

Part of the [hoi4-debug-playtest](../SKILL.md) skill. Read before driving the running game: navigation, console use, checkpoints and efficiency rules.

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

Command names to get right: `acclimatization` (not `acclimization`), `reload_textures`, `update_loc <tag>`, and `addfunds`, which defaults to 700. [docs]

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

Before the run, confirm with the user that the game writes plain-text saves (`save_as_binary=no` in the HOI4 `settings.txt`); do not edit that file yourself. Plain-text checkpoint saves let `hoi4-save-inspection` and `hoi4_save_query` read the real runtime state. Name them after the test step, such as `qa_<run_id>_020_event_pre` and `..._post` (the server prefixes `hoi4live_`), and record which query or inspector command produced each piece of evidence.

### 10.5 Efficiency

- Keep one running game and one loaded dedicated save for the whole scope. Independent test cases run in sequence on the same loaded position; go back to a checkpoint only when a case contaminated the state.
- After a fix, retest the failed case on the running game (restart only for content the game reads at launch), plus the one nearby regression check. Do not rerun passed cases or restart the coverage ledger.
- Save only when a file answers the question: a diff around an option, a persistence check, a briefing's deep sections. Read everything else from the screen and tool output.
- Repeat only the step that failed; repeat the whole sequence only when the step concerns persistence.
- Delete your own `hoi4live_` saves when the run is done.

