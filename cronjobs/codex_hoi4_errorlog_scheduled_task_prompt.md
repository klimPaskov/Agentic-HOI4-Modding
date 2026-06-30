# Codex scheduled task prompt

Set up an automatic Hearts of Iron IV `error.log` watchdog for the user's current mod project using Codex scheduled tasks.

Do not set up Hermes, system cron, Windows Task Scheduler, launchd, or any other external scheduler unless the user explicitly asks for it. The scheduler for this workflow should be the Codex app scheduled task feature.

Start by discovering the local setup:

```text
Mod repo path: <absolute path>
Profile scripts directory: <profile scripts path>
Repo-local temp log directory: <repo path>/tmp/hoi4-error-logs or another suitable repo-local path
HOI4 executable or launch command: <path or command>
Paradox error.log path: <path>
Codex handoff target: <Codex current repo thread, Codex task handoff, local file fallback, etc.>
Codex scheduled task name: <default HOI4 error.log watchdog for Codex handoff>
Schedule: <default every 120m unless the user chooses otherwise>
Game runtime per check: <default 120 seconds unless the user chooses otherwise>
```

Use system inspection where possible: current repo, profile or config folders, HOI4 or Steam install locations, Paradox user-data locations, and available Codex tools or state files. Ask the user only for values that cannot be discovered confidently.

Create two profile-local scripts after the target profile or scripts directory is known:

```text
<scripts dir>/hoi4_errorlog_kickoff.<platform-appropriate extension>
<scripts dir>/hoi4_errorlog_worker.py
```

The launcher should be safe for a Codex scheduled task and minimal:

- create the repo-local temp log directory
- skip if a mod-specific watchdog lock is already active
- start the Python worker detached or backgrounded so the Codex scheduled task is not blocked by the HOI4 run
- append worker output to `<temp log dir>/watchdog.log`

Use a launcher appropriate for the detected OS or shell. On Windows, prefer PowerShell or Python. On Linux, macOS, or WSL, a POSIX shell script is fine.

Implement the Python worker so it:

- uses a mod-specific lock file or lock mechanism
- exits quietly if another worker is active
- checks whether HOI4 is already running
- exits without action if HOI4 was already running, so it does not kill the user's manual game session
- launches HOI4 using the discovered executable path or launch command
- waits exactly the configured runtime, default `120` seconds
- kills only the HOI4 process or process tree it launched
- reads the discovered Paradox `error.log`
- detects actionable current-mod errors conservatively:
  - direct mentions of the mod repo name, descriptor name, mod folder name, or known mod path
  - line mentions a repo-relative file path that exists under the current repo, especially common HOI4 mod directories like `common/`, `events/`, `history/`, `localisation/`, `gfx/`, `interface/`, `decisions/`, `missions/`, `map/`, `units/`, `music/`, `sound/`, `characters/`, `focus/`, `technologies/`, etc.
- ignores obvious vanilla, launcher, or engine noise that does not point to the current mod
- if no matching lines exist, logs this and exits `0`:

```text
error.log has no obvious current-mod related errors; not copying or sending a handoff
```

If matching lines exist, copy the full log to:

```text
<temp log dir>/hoi4-error-YYYYMMDDTHHMMSSZ.log
```

Then send a concise handoff to Codex. Prefer a structured Codex handoff over GUI paste automation. If Codex app-server, state database, CLI task APIs, or a repo-thread mapping is available, discover the latest matching Codex thread for the current repo path and use that. If no verified Codex handoff target is available, write the prompt to a local handoff file and tell the user where it is.

Generic Codex handoff prompt:

```text
Fix the HOI4 errors reported in this latest automated game run.

Repo: <repo path>
error.log path: <copied temp log path>

Identify actionable errors for this mod only. Ignore unrelated vanilla errors, launcher noise, or engine noise. Preserve the existing project style and do not broaden scope beyond the reported errors. After fixing and validating the actionable errors, delete the temporary copied log file at <copied temp log path>.
```

Also mirror the handoff prompt to a local recovery/debug file, for example:

```text
<temp log dir>/latest_codex_handoff_prompt.txt
```

Add `--dry-run` support to the worker. Dry-run must not launch HOI4. It should print:

- repo exists
- HOI4 launch command or executable exists or is resolvable
- `error.log` exists
- temp log dir exists or can be created
- count of current-mod error matches in the current `error.log`
- first few matching lines, if any
- Codex handoff target status, if configured
- current HOI4 process status
- whether another watchdog worker is locked or running

Create the Codex scheduled task after scripts are in place. Use the Codex app scheduled task feature, not Hermes cron.

```yaml
name: HOI4 error.log watchdog for Codex handoff
schedule: every 120m
repeat: forever
delivery: local command
script: <launcher script path or profile-relative script name>
```

Codex scheduled task prompt or description:

```text
On schedule, kick off the HOI4 error.log watchdog for the current mod repo. The profile-local launcher starts a detached worker that launches HOI4 for a fixed short run when HOI4 is not already running, checks Paradox error.log for errors related to the current mod, copies matching logs to the repo-local temp log directory, and sends a Codex handoff prompt to the configured Codex target. If no current-mod errors are found, stay quiet.
```

Expected no-error log shape:

```text
Codex handoff target ready or local handoff fallback ready; launching HOI4
leaving HOI4 running for <runtime> seconds
stopping HOI4 process launched by watchdog
error.log has no obvious current-mod related errors; not copying or sending a handoff
```

Expected handoff log shape:

```text
found <n> current-mod related error line(s); copying and sending log
copied error.log to <temp log dir>/hoi4-error-YYYYMMDDTHHMMSSZ.log
sent handoff to <Codex target>; prompt mirror=<temp log dir>/latest_codex_handoff_prompt.txt
Codex was instructed to delete temp log after fixing and validating actionable errors
```

Important rules:

- discover and verify the local setup before writing scripts or scheduling
- ask the user only for values that cannot be safely discovered
- use Codex scheduled tasks rather than Hermes cron or an OS scheduler
- prefer structured Codex handoff or file handoff over GUI paste automation
- store copied logs in the repo-local temp folder
- leave copied logs for Codex to delete after fixing unless the user requests different cleanup
- leave any pre-existing HOI4 session alone
- filter out vanilla, launcher, and engine noise before sending a handoff
- detach the worker from the scheduled task launcher so the game run is not limited by scheduled task runtime
- do not use Hermes-only fields such as `no_agent=true` unless the user explicitly switches back to Hermes

Final response should report:

```text
Created/updated files:
- ...

Codex scheduled task:
- id/name/schedule/profile or workspace
- launcher path

Verified:
- syntax check: ...
- dry-run: ...
- Codex scheduled task status/list: ...
- manual run/log tail: ...

Notes:
- HOI4 is not launched during dry-run.
- Handoff only happens if current-mod related errors are found.
- The workflow uses Codex scheduled tasks, not Hermes cron.
```
