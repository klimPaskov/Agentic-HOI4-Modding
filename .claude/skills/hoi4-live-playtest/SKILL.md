---
name: hoi4-live-playtest
description: Use when a task needs live Hearts of Iron IV evidence through the HOI4 Live Tools MCP server (hoi4-live), such as launching or reusing the running game, loading a save, firing an event or effect, running time with popup handling, reading popups, tooltips and the screen, saving and diffing saves, checking the error-log delta, or playing a campaign, and the user asked for live testing or named this skill or hoi4-debug-playtest.
---

# HOI4 live playtest through HOI4 Live Tools

HOI4 Live Tools is an MCP server, registered as `hoi4-live`, that drives a running Hearts of Iron IV on Windows through the game's own interface and console. Its tools appear as `hoi4_status`, `hoi4_load`, `hoi4_fire_event` and so on (Claude Code lists them as `mcp__hoi4-live__*`). It is how an agent turns a source change into observed game behavior: set up a state, trigger the content, run time, capture every popup, and read the log delta and the save.

Use it instead of scripting the desktop. A feature check that needs the game goes through these tools; screenshots, clicks and keys sent by ad-hoc scripts are not a substitute and can hit the wrong window.

Live testing is requested by the user. Use this skill when the user asks for live testing, names this skill or `hoi4-debug-playtest`, or the task explicitly includes a live check. Never start the game or play on your own initiative during implementation, audit, or completion work.

## Before the first call

1. Confirm the server is connected: the `hoi4_*` tools are listed. If not, the user installs it with HOI4 Mod Setup or `python install.py` from the release (see `references/setup.md`); tell them and stop the live part. Do not script the desktop yourself.
2. Call `hoi4_status` once. It reports the process, window, playset, session mode (`test` or `campaign`), lock holder, recent saves, screen, date and open popups. Everything that follows starts from it.
3. Check the playset: the mod under test must be enabled. The game reads mods only at launch, so a changed playset needs a restart.
4. Take the desktop lock for a multi-step run: `hoi4_lock action=acquire purpose=<short text>`; release it when you finish or fail. If another holder has it, wait or report; never break a live holder's lock.

## Efficiency rules

Loading a save costs one to three minutes, saving about one, and starting the game several. Spend them only when the question needs them.

- **Reuse the running game and the loaded position.** `hoi4_status` first; launch only when no game runs (`hoi4_launch`), load a save only to start or to change the position, never to repeat a check.
- **Repeat only the step that failed.** When one step of a longer sequence fails, fix the cause and call that step again on the running game. Run the whole sequence again only when the step is about persistence, meaning what a save shows.
- **No needless save or reload.** Read state without a file: `hoi4_screen`, `hoi4_ocr`, `hoi4_hover`, the output of `hoi4_eval_effect` and `hoi4_console`. Save (`hoi4_save`) only when a file answers the question: a `hoi4_save_query`, a diff, a briefing's deep sections, or a persistence check. One save per question; one save, load and diff per feature for persistence.
- **One checkpoint save, used sparingly.** Save a clean checkpoint once after setup and go back to it only when a case contaminated the state (mutually exclusive branches, world-end paths, country creation). Independent checks share the loaded position.
- **Mark the logs, then read the delta once.** `hoi4_logs set_mark=<name>` before the action, `hoi4_logs log=error since=<name>` after it.
- **Short, bounded time.** `hoi4_time action=step days=N` with `popups=stop` (or `choices`) and a small N; never leave open-ended speed running.
- **Script what is repeatable.** `hoi4_scenario` runs a list of tool calls in one request and writes a Markdown and JSON report; keep its report path in the handoff.
- **Text before pictures.** Use screenshots only when the result is visual (a GUI state, a map mode, layout); read values through the text tools.
- **Delete your own saves at the end.** Test saves are named `hoi4live_<name>`; with a large mod each is about 100 MB and every save pushes older ones further down the load list.
- **A slow call is not a failed call.** On a busy machine the tools wait and re-read. Repeat a failed call once before changing the plan.

## Feature test recipe (test mode)

1. `hoi4_load save=<known save>` (or `hoi4_new_game`); the tool checks the date. Skip when the right position is already loaded.
2. `hoi4_logs set_mark=<case>`.
3. Set up the state with `hoi4_eval_effect effect=... [scope=TAG]` or `hoi4_console`; record every command, since a setup shortcut must never be used to prove the condition it bypasses.
4. Trigger the content with `hoi4_fire_event event=<id> [tag=TAG]`, a decision through `hoi4_decisions action=take`, or the mod's own control.
5. Read and answer the popups with `hoi4_popups` (`read`, then `answer` by index or option text), or let `hoi4_time action=step days=N popups=first|choices|stop` answer them while time runs.
6. Check the outcome:
   - `hoi4_save` then `hoi4_save_query query=get|variables|flags|find` for variables, flags and arrays, and `query=diff` against the checkpoint for what the change did; the diff is the authoritative list.
   - `hoi4_logs log=error since=<case>` for new error-log lines. A new error that points at your files is a defect.
   - `hoi4_screen`, `hoi4_hover`, `hoi4_ocr` or `hoi4_screenshot` when the result is visual.
7. When the feature persists, `hoi4_save`, `hoi4_load` and diff the two saves once.
8. Release the lock; leave the game paused on the map with no window open.

For a deep read of runtime state, use `hoi4-save-inspection` on the saves this loop writes: `footprint` shows script state that grows without cleanup, `flatten` tallies AI outcomes across countries, and `diff` compares two points in time. `hoi4_save_query` is the quick in-session version of the same questions. Both need plain-text saves (`save_as_binary=no` in `settings.txt`); when saves are binary, say so and ask the user to change it, because the server never edits that file.

## Restarts and reloading

The game loads script content (events, decisions, effects, scripted triggers, localisation, ideas, focus trees) only at launch. After editing those, restart with `hoi4_launch restart=true`, then `hoi4_load`. A few things reload in place through `hoi4_console` in test mode, per the installed `documentation/console_commands_documentation.md`: `reloadinterface` (interface), `reload_textures` (textures), `reloadtechnologies` (technologies), `reloadoob` (orders of battle). Use them for a GUI or texture iteration instead of a restart; confirm the fix on screen afterwards.

A changed playset (including `hoi4_telemetry enable`) edits `dlc_load.json`, backed up first, and needs a restart that the user has agreed to.

## Reading the situation

- `hoi4_briefing` is a one-page report of the player's country: what needs a decision, government, wars and fronts, economy, military, focus and research, and the changes since the last briefing.
- `hoi4_state` is the structured country model with the source and age of every field (telemetry, newest save, top bar). The optional telemetry companion mod (`hoi4_telemetry`) makes both current to the last in-game day; enabling it edits the playset, so ask first.

## Campaign actions

Campaign mode refuses console cheats, so everything the agent does is something a player could do: `hoi4_focus`, `hoi4_research`, `hoi4_production`, `hoi4_construction`, `hoi4_politics`, `hoi4_decisions`, `hoi4_diplomacy`, `hoi4_army`, `hoi4_orders`, `hoi4_navy_air`, each verified on screen after acting. Use them when a test must show that a player can reach the content without the console, for example taking a decision whose `allow` block depends on the mod's state. Switch with `hoi4_lock action=set_mode mode=campaign` only when the case needs it.

For a longer campaign (advance, brief, act, journal), `hoi4_advance` and `hoi4_journal` run the loop, and the playbook is installed with the server at `%LOCALAPPDATA%\hoi4-live-tools\app\skills\hoi4-live-campaign\SKILL.md`.

## Safety

- Input goes to the game window only. Never send keys or clicks to other windows or steal focus.
- The server writes only `hoi4live_*` saves, never deletes anything and never edits `settings.txt`. It changes the playset only through `hoi4_telemetry enable|disable|restore`.
- Do not quit the game unless the task calls for it (`hoi4_shutdown confirm=true`).
- `test` mode allows console commands, events and effects; `campaign` mode refuses them.

## Failures

Apply the project's bounded retry rule: one corrected retry for a failed call, then stop that line of testing and report what was attempted, the tool error or screen state, the save and log mark, and what would justify another attempt. A tool failure is not a mod defect; a new error-log line or a wrong save value after your change is. Fix confirmed defects in source, restart only when the changed content needs it, and rerun only the affected case.

## Reporting

State which cases ran live, the saves and marks used, the observed popups, values and error-log lines, and which claims rest on source review instead of live evidence. Live evidence from this skill is agent-observed; it does not replace the user's own play session unless the user says so.

## Reference map

- `references/setup.md`: install, register, upgrade and troubleshoot the server (the HOI4 Mod Setup app does this for you).
