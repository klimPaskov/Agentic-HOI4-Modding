---
name: hoi4-live-testing
description: Use when a task needs live Hearts of Iron IV evidence through the optional HOI4 Live Tools MCP server (hoi4-live), such as loading a save, firing an event or effect in test mode, running time with popup handling, reading popups and tooltips, checking the error-log delta, or querying the plain-text save, and the user has asked for live testing or the task explicitly includes it.
---

# HOI4 live testing through HOI4 Live Tools

HOI4 Live Tools is an optional MCP server, registered as `hoi4-live`, that drives a running Hearts of Iron IV on Windows through the game's own interface and console.
Use it to turn a source change into observed game behavior: set up a state, trigger the content, run time, capture every popup, and read the log delta and the save.

Live testing is user-owned by default.
Use this skill only when the user asked for live testing, named this skill, or the task explicitly includes a live check.
Never launch, restart, or quit the game on your own initiative; `hoi4_launch` and `hoi4_shutdown` need a task that calls for them.

## Before the first call

1. Confirm the server is connected: its tools appear as `hoi4_status`, `hoi4_load`, `hoi4_fire_event`, and similar (Claude Code shows them under `/mcp` as `mcp__hoi4-live__*`).
   If it is not connected, tell the user how to register it (see `references/setup.md` in this skill) and stop the live part of the task; do not script the desktop yourself.
2. Call `hoi4_status`. It reports the process, window, playset, session mode (`test` or `campaign`), lock holder, recent saves, screen, date, and open popups. Read it before acting.
3. Check the playset: the mod under test must be enabled. The game reads mods only at launch, so a changed playset needs a restart that the user has agreed to.
4. Long calls take minutes. If the client times out, ask the user to raise the tool timeout (for example `MCP_TOOL_TIMEOUT=1800000` for Claude Code, `tool_timeout_sec = 1800` for Codex) instead of retrying blindly.

## Safety rules

- **One desktop lock.** Every acting tool holds the shared lock while it acts. For a multi-step run, take it with `hoi4_lock action=acquire` and a short `purpose`, and release it with `action=release` when you finish or fail. If another holder has it, wait or report; never break a live holder's lock.
- **Only inside the game.** Input goes to the game window only. Never send keys or clicks to other windows, and never steal focus for anything else.
- **Saves.** The server writes only `hoi4live_*` saves. Any save can be loaded or queried; nothing is deleted.
- **Settings.** `settings.txt` is never edited. Save queries need plain-text saves (`save_as_binary=no`); when saves are binary, report it and ask the user rather than changing the setting.
- **Modes.** `test` mode allows console commands, events, and effects. `campaign` mode refuses them so an agent plays with player-equivalent actions. Switch with `hoi4_lock action=set_mode` only when the task needs the other mode.
- **Leave it tidy.** Finish paused on the map with no window open and the lock released.

## Feature test workflow (test mode)

1. Acquire the lock.
2. Load a known save with `hoi4_load` (or start with `hoi4_new_game`); the tool verifies the date.
3. Mark the logs: `hoi4_logs set_mark=<name>`.
4. Set up the state with `hoi4_eval_effect` (optionally scoped) or `hoi4_console`, then trigger the content with `hoi4_fire_event` (`event`, optional `tag`).
5. Read and answer the popups with `hoi4_popups` (`read`, `answer` by index or option text), or let `hoi4_time action=step days=N popups=first|all` answer them while time runs.
6. Save with `hoi4_save name=<case>`.
7. Check the outcome:
   - `hoi4_save_query` for variables, flags, and arrays (`get`, `find`, `variables`, `flags`), and `query=diff` against the starting save for what changed.
   - `hoi4_logs log=error since=<mark>` for new error-log lines; treat a new error that points at your files as a defect.
   - `hoi4_screen`, `hoi4_hover`, `hoi4_ocr`, or `hoi4_screenshot` when the result is visual (tooltip text, a GUI state, a map mode).
8. Release the lock.

`hoi4_scenario` runs the same list of tool calls in one request and writes a Markdown and JSON report; use it for a repeatable case and keep its report path in the handoff.

## Reading the situation

- `hoi4_briefing` gives a one-page report of the player's country: what needs a decision, government, wars and fronts, economy, military, focus and research, and changes since the last briefing.
- `hoi4_state` gives the structured country model with the source and age of every field (telemetry, newest save, top bar).
- The optional telemetry companion mod (`hoi4_telemetry`) makes both current to the last in-game day. Enabling it edits the playset (backed up first) and needs a restart, so ask before enabling it.

## Campaign actions

Campaign tools act through the real interface and verify each action on screen: `hoi4_focus`, `hoi4_research`, `hoi4_production`, `hoi4_construction`, `hoi4_politics`, `hoi4_decisions`, and `hoi4_diplomacy`.
Use them when a test must show that a player can reach the content without the console, for example taking a decision whose `allow` block depends on the mod's state.
They read structure from the game's and the enabled mods' files, so they work for any country and mod that keeps the vanilla interface.

## Failures

Apply the project's bounded retry rule: one corrected retry for a failed call, then stop that line of testing.
Report what was attempted, the tool error or screen state, the save and log mark, and what would justify another attempt.
A tool failure is not a mod defect; a new error-log line or a wrong save value after your change is.
Fix confirmed defects in source, then rerun only the affected case.

## Reporting

State which cases ran live, the saves and marks used, the observed popups, values, and error-log lines, and which claims rest on source review instead of live evidence.
Live evidence from this skill is agent-observed; it does not replace the user's own play session unless the user says so.
