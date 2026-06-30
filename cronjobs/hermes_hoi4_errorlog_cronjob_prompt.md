Set up an automatic Hearts of Iron IV `error.log` watchdog for the user's current mod project.

Start by discovering the local setup:

```text
Mod repo path: <absolute path>
Profile scripts directory: <profile scripts path>
Repo-local temp log directory: <repo path>/tmp/hoi4-error-logs or another suitable repo-local path
HOI4 executable or launch command: <path or command>
Paradox error.log path: <path>
Coding-agent handoff target: <Codex, local file, webhook, chat, etc.>
Schedule: <default every 120m unless the user chooses otherwise>
Game runtime per check: <default 120 seconds unless the user chooses otherwise>
```

Use system inspection where possible: current repo, profile/config, HOI4/Steam install locations, Paradox user-data locations, and available coding-agent tools. Ask the user for any value that cannot be discovered confidently.

Create two profile-local scripts after the target profile/scripts directory is known:

```text
<scripts dir>/hoi4_errorlog_kickoff.<platform-appropriate extension>
<scripts dir>/hoi4_errorlog_worker.py
```

The launcher should be cron-safe and minimal:

- create the repo-local temp log directory
- skip if a mod-specific watchdog lock is already active
- start the Python worker detached/backgrounded so the scheduler is not blocked by the HOI4 run
- append worker output to `<temp log dir>/watchdog.log`

Use a launcher appropriate for the detected OS/shell. A POSIX shell script is fine on Linux/macOS/WSL. On Windows, use PowerShell, Python, or another reliable launcher.

Implement the Python worker so it:

- uses a mod-specific lock file or lock mechanism
- exits quietly if another worker is active
- checks whether HOI4 is already running
- exits without action if HOI4 was already running, so it does not kill the user's manual game session
- launches HOI4 using the discovered executable path or launch command
- waits exactly the configured runtime, default `120` seconds
- kills only the HOI4 process/process tree it launched
- reads the discovered Paradox `error.log`
- detects actionable current-mod errors conservatively:
  - direct mentions of the mod repo name, descriptor name, mod folder name, or known mod path, or
  - line mentions a repo-relative file path that exists under the current repo, especially common HOI4 mod directories like `common/`, `events/`, `history/`, `localisation/`, `gfx/`, `interface/`, `decisions/`, `missions/`, `map/`, `units/`, `music/`, `sound/`, `characters/`, `focus/`, `technologies/`, etc.
- ignores obvious vanilla/launcher/engine noise that does not point to the current mod
- if no matching lines exist, logs this and exits `0`:

```text
error.log has no obvious current-mod related errors; not copying or sending a handoff
```

If matching lines exist, copy the full log to:

```text
<temp log dir>/hoi4-error-YYYYMMDDTHHMMSSZ.log
```

Then send a concise handoff to the configured coding-agent target. Prefer structured/API handoff over GUI paste automation. If no coding-agent target is available, write the prompt to a local handoff file and tell the user where it is.

Generic handoff prompt:

```text
Fix the HOI4 errors reported in this latest automated game run.

Repo: <repo path>
error.log path: <copied temp log path>

Identify actionable errors for this mod only; ignore unrelated vanilla errors, launcher noise, or engine noise. Preserve the existing project style and do not broaden scope beyond the reported errors. After fixing and validating the actionable errors, delete the temporary copied log file at <copied temp log path>.
```

Also mirror the handoff prompt to a local recovery/debug file, for example:

```text
<temp log dir>/latest_coding_agent_prompt.txt
```

If the user uses Codex and an app-server/state-DB handoff is available, discover the latest matching thread for the current repo path and use that. Prefer this over GUI automation. If Codex paths/env vars differ by OS or install method, discover them from the system or ask the user.

Add `--dry-run` support to the worker. Dry-run must not launch HOI4. It should print:

- repo exists
- HOI4 launch command/executable exists or is resolvable
- `error.log` exists
- temp log dir exists or can be created
- count of current-mod error matches in the current `error.log`
- first few matching lines, if any
- coding-agent target status, if configured
- current HOI4 process status
- whether another watchdog worker is locked/running

Create the cronjob after scripts are in place:

```yaml
name: HOI4 error.log watchdog for coding-agent handoff
schedule: every 120m
repeat: forever
deliver: local
script: <launcher script path or profile-relative script name>
no_agent: true
```

Cron prompt/description:

```text
On schedule, kick off the HOI4 error.log watchdog for the current mod repo. The profile-local launcher starts a detached worker that launches HOI4 for a fixed short run when HOI4 is not already running, checks Paradox error.log for errors related to the current mod, copies matching logs to the repo-local temp log directory, and sends a coding-agent handoff prompt to the configured target. If no current-mod errors are found, stay quiet.
```

Expected no-error log shape:

```text
handoff target ready or local handoff fallback ready; launching HOI4
leaving HOI4 running for <runtime> seconds
stopping HOI4 process launched by watchdog
error.log has no obvious current-mod related errors; not copying or sending a handoff
```

Expected handoff log shape:

```text
found <n> current-mod related error line(s); copying and sending log
copied error.log to <temp log dir>/hoi4-error-YYYYMMDDTHHMMSSZ.log
sent handoff to <target>; prompt mirror=<temp log dir>/latest_coding_agent_prompt.txt
coding agent was instructed to delete temp log after fixing/validating actionable errors
```

Important rules:

- discover/verify the local setup before writing scripts or scheduling
- ask the user only for values that cannot be safely discovered
- prefer structured/API/file handoff over GUI paste automation
- store copied logs in the repo-local temp folder
- leave copied logs for the coding agent to delete after fixing unless the user requests different cleanup
- leave any pre-existing HOI4 session alone
- filter out vanilla/launcher noise before sending a handoff
- keep cron `no_agent=true`
- detach the worker from the cron launcher so the game run is not limited by cron runtime

Final response should report:

```text
Created/updated files:
- ...

Cron job:
- id/name/schedule/profile

Verified:
- syntax check: ...
- dry-run: ...
- cron status/list: ...
- manual run/log tail: ...

Notes:
- HOI4 is not launched during dry-run.
- Handoff only happens if current-mod related errors are found.
```
