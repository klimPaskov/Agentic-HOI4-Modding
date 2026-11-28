---
name: hoi4-live-playtest
description: Use for in-game Hearts of Iron IV tests through the selected live-testing provider when the recorded in-game testing answer or the user asks for them, or for the manual test recipe.
---

# HOI4 live playtest

In-game testing is a normal step of the workflow, run as the user decided. The upfront consultation asks once whether to run in-game tests, how and when (`hoi4-feature-planning/references/consultation-questions.md`), and the answer is recorded in the feature's or the mod's `decisions.md` and, for a whole-mod build, in the ledger's `live_testing` (`hoi4-new-mod`). Launch the game only as that answer allows, or when the user asks for a live check. Without a recorded answer, ask the question at the next consultation; never launch on a guess.

<!-- HOI4_MOD_SETUP:LIVE_TESTING_PROVIDER:START -->
Live-testing provider: manual until HOI4 Mod Setup writes the selected route.
<!-- HOI4_MOD_SETUP:LIVE_TESTING_PROVIDER:END -->

## Capability gate

Read the selected provider guidance above and inspect that server's advertised tool list. Use qualified tool names belonging to that server. Do not infer tool names from another provider or assume identical capabilities. If the selected server is unavailable, the platform is not supported, or the answer is "manual", use the manual recipe below and record the in-game part as not run by the agent. Do not automatically fall back to desktop control or another provider.

Clausewitz MCP reads state directly from the native Linux HOI4 1.19.2 process. These reads need neither OCR nor a save. Linux hosts connect directly; Windows hosts use WSL; macOS hosts use SSH to Linux. Complete manual Linux/game/server setup and confirm the Linux game and server are ready in HOI4 Mod Setup before registration. See references/clausewitz-mcp.md.

HOI4 Live Tools is experimental, slower and not thoroughly tested. It runs on Windows and macOS. See references/hoi4-live-tools.md only for this provider's interface, console, save, log and campaign operations.

## When to run

The recorded answer names one of these, and the agent follows it without asking again:

| Answer | What the agent does |
| --- | --- |
| After each feature | A feature test (below) before the feature's `passes` is set, plus the smoke test at the end |
| After each phase | The smoke test when a phase of the build plan is finished, before the next phase builds on it, and at the end. This is the suggested answer when the selected provider supports this platform |
| At the end | The smoke test once every other feature has passed |
| Manual | The short manual recipe at the same points; the user's observations are the evidence. This is the suggested answer when no provider is installed or the platform is not supported |
| No | No in-game step; the completion report says the mod was not checked in game |

The answer may also limit how: for example only while the user is away from the computer, only one game instance, or never on this machine. Follow it as written.

## Smoke test

The smoke test is the in-game check of a whole build. With a provider that supports it:

1. Confirm the mod is enabled in the launcher's playset. The tools never change the playset on their own; if it is not enabled, tell the user the one step to take and record a `blocker` (`needs: user`).
2. Launch to the main menu (or reuse the running game), and fail on a crash or a fatal dialog.
3. Start a new game as each playable nation the brief names, on the mod's start date.
4. Mark the logs, run 30 in-game days with popups answered, then read the new `error.log` lines. Every new error that points at the mod's files is a defect to fix.
5. Fire each of the mod's event namespaces where the provider has a smoke tool (Live Tools `hoi4_smoke_namespace`), and sweep the visible screens for raw localisation keys (Live Tools `hoi4_sweep_loc`).
6. Write the result to `docs/mod/evidence/smoke-<date>.md`: provider, game version, nations started, days run, new errors with their files, raw keys found, and what the provider could not check.
7. Fix every defect, rerun only the affected step, and record the final run. In the ledger set `live_testing.smoke` to `{"passes": true, "evidence": [<the report>], "covers": [<every feature id that has passed>]}`.

The completion gate requires this record whenever the answer is not "no", and again after a later feature passes, because `covers` must name every passed feature. While the user runs a manual recipe, record the wait with `python -B .tools/check.py gate --wait "<what they are checking>"`.

## Feature test recipe

1. Define the feature, starting conditions and observable expected result.
2. Inspect the selected server's status and state capabilities. Reuse the running session when possible. Confirm the mod and game version before acting.
3. Map each required operation to an advertised tool. Report unsupported operations as a coverage limitation; never invent an equivalent.
4. Obtain a baseline through direct state reads or supported logs. Use screenshots for visual claims only. Save or reload only for persistence claims or when required by the selected provider.
5. Trigger the case using a supported action, record every setup shortcut, and advance bounded time if supported. Do not treat a condition bypassed during setup as proven.
6. Compare observed state and fresh errors against expectations. Fix confirmed source defects and rerun only the affected case. Restart only when changed content requires it and the route supports it.
7. Release any provider lock acquired and leave the session paused when supported. Do not close the game without authorization.

## Manual recipe

When no provider can run the test, give the user one short, bounded recipe at the agreed point and record what they report:

1. Enable the mod in the launcher's playset, and start the game with the `-debug` launch option if they agree.
2. Start a new game as <nation> on <date>, unpause and let 30 days pass.
3. Look for: <the two to five visible results of the features under test, such as the focus tree opening, an event firing on a date, a decision appearing>.
4. Open `Documents/Paradox Interactive/Hearts of Iron IV/logs/error.log` and paste the lines that mention the mod's files, or say there are none.

Record their observations as the evidence file and set the ledger as in step 7 of the smoke test, with `"provider": "manual"`. If the user does not answer, the in-game part stays open and the completion report says so.

## Failures and reporting

Use one corrected retry for a failed call, then stop that test path. Distinguish tool failures from mod defects. Report provider, game version, cases, qualified tools, state/log/screenshot evidence, source-only conclusions and unsupported checks. Agent observations do not replace the user's play session unless the user says so.

## References

- references/setup.md: provider choice, setup and update/repair.
- references/clausewitz-mcp.md: Linux native version restriction and MIT acknowledgement.
- references/hoi4-live-tools.md: provider-specific operations, installed with that runtime.
