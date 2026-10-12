---
name: hoi4-live-playtest
description: Use for explicitly requested live Hearts of Iron IV evidence through the selected live-testing provider, or manual checks when no server is selected.
---

# HOI4 live playtest

Use only when the user requests live testing or explicitly includes a live check. Never launch the game during ordinary implementation or audit work.

<!-- HOI4_MOD_SETUP:LIVE_TESTING_PROVIDER:START -->
Live-testing provider: manual until HOI4 Mod Setup writes the selected route.
<!-- HOI4_MOD_SETUP:LIVE_TESTING_PROVIDER:END -->

## Capability gate

Read the selected provider guidance above and inspect that server's advertised tool list. Use qualified tool names belonging to that server. Do not infer tool names from another provider or assume identical capabilities. If the selected server is unavailable, stop the live portion and report its setup requirement. Do not automatically fall back to desktop control or another provider.

Clausewitz MCP reads state directly from the native Linux HOI4 1.19.2 process. These reads need neither OCR nor a save. Windows hosts use WSL; macOS hosts use SSH to Linux. Complete manual Linux/game/server setup and confirm the Linux game and server are ready in HOI4 Mod Setup before registration. See references/clausewitz-mcp.md.

HOI4 Live Tools is experimental, slower and not thoroughly tested. Windows is verified; upstream macOS support is incomplete. See references/hoi4-live-tools.md only for this provider's interface, console, save, log and campaign operations.

With manual testing selected, give the user a bounded test recipe and record the observations they provide.

## Test recipe

1. Define the feature, starting conditions and observable expected result.
2. Inspect the selected server's status and state capabilities. Reuse the running session when possible. Confirm the mod and game version before acting.
3. Map each required operation to an advertised tool. Report unsupported operations as a coverage limitation; never invent an equivalent.
4. Obtain a baseline through direct state reads or supported logs. Use screenshots for visual claims only. Save or reload only for persistence claims or when required by the selected provider.
5. Trigger the case using a supported action, record every setup shortcut, and advance bounded time if supported. Do not treat a condition bypassed during setup as proven.
6. Compare observed state and fresh errors against expectations. Fix confirmed source defects and rerun only the affected case. Restart only when changed content requires it and the route supports it.
7. Release any provider lock acquired and leave the session paused when supported. Do not close the game without authorization.

## Failures and reporting

Use one corrected retry for a failed call, then stop that test path. Distinguish tool failures from mod defects. Report provider, game version, cases, qualified tools, state/log/screenshot evidence, source-only conclusions and unsupported checks. Agent observations do not replace the user's play session unless the user says so.

## References

- references/setup.md: provider choice, setup and update/repair.
- references/clausewitz-mcp.md: Linux native version restriction and MIT acknowledgement.
- references/hoi4-live-tools.md: provider-specific operations, installed with that Windows runtime.
