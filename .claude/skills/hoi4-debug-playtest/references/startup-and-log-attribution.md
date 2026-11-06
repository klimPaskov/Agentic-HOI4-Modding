# HOI4 Autonomous Debug Playtest: Startup, logs and repair loop

Part of the [hoi4-debug-playtest](../SKILL.md) skill. Read before launching the game, resolving the log directory, attributing log lines to the mod or repairing startup errors.

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

For a repeated pre-menu crash with an empty fresh `error.log`, check `common/script_constants/` category schemas early; the empty log does not prove successful startup. Read installed vanilla `common/script_constants/documentation.md` and the Script Constants section of `documentation/script_concept_documentation.md`: each category requires `schema` as its first entry, and scalar declarations use `data = int` or `data = fixed_point`, not `any_value`. Preserve valid array declarations using installed vanilla `common/script_constants/country_groups.txt` (`array = country`) and `state_groups.txt` (`array = state`) precedents; absence of scalar `data` alone is not an array-schema defect. Repair confirmed declaration defects without changing tuning values, constant names, or consumers.

Apply `hoi4-investigate` to every attributed line: root cause before an edit, the evidence ladder, parser cascades and crash-dump leads (section 5), and your own patch's new errors (section 1). Keep the clean-start gate pending until the required main-menu and country-map observations and fresh-log checks pass.

For startup parse errors involving `check_variable`, distinguish valid shorthand such as `{ some_value > threshold }` from malformed mixed form `{ var = some_value > threshold }`. Consult installed `documentation/triggers_documentation.md` and the offline Data structures comparison examples. In a confirmed mixed form, remove only the redundant `var =`, preserving the comparator, scoped variable token, and right-hand value, including a `constant:category.threshold` token. Keep valid shorthand and genuine long-form blocks such as `{ var = some_value value = threshold compare = greater_than }` intact; `>` is supported syntax.

For unsupported `clear_temp_variable`, do not mechanically rename it to `clear_variable` or delete all occurrences: the offline Data structures documentation restricts `clear_variable` to regular variables. Inventory each exact identifier's writes, reads, callers, nested helpers, and caller continuations before choosing a repair. Delete terminal cleanup only when every later invocation initializes before any read and no downstream consumer observes absence or retention. Cross-helper inputs or sentinel semantics require an explicit repair that preserves the consumer contract; setting zero or assuming deletion at a helper's closing brace does not prove equivalence to absence.

For deliberately inert ordinary country templates, a comment-only history file can still be reported missing by the loader. When the accepted package model supplies all country attributes at runtime, an empty dated history block such as `1936.1.1 = { }` can provide a recognized input with no child effects; confirm acceptance in fresh logs for the installed engine. Do not use this instead of required starting history or OOB content, or switch tags into a dynamic pool merely to remove the warning: inspect `create_dynamic_country` origin, copy-source, and reservation semantics first. Loader acceptance does not validate runtime country creation, reservation, transfer, or cleanup.

## 8. Startup repair loop

With HOI4 Live Tools, "close" is `hoi4_shutdown confirm=true` and "relaunch" is `hoi4_launch restart=true`. Restart only when the edit changed content the game reads at launch (script, localisation, ideas, focus trees); interface and texture edits reload in place with `reloadinterface` and `reload_textures` through `hoi4_console`.

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

Fix by root cause as `hoi4-investigate` section 1 requires, never by suppressing a warning. Do not replace missing content with placeholders or fallbacks unless the user approved that exact fallback.

