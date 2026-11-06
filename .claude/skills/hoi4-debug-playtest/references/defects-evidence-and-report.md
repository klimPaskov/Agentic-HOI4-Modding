# HOI4 Autonomous Debug Playtest: Defects, evidence package and final report

Part of the [hoi4-debug-playtest](../SKILL.md) skill. Read when a live defect is found, before keeping the evidence folder, and before writing the final report.

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
2. Keep the game running unless the fix needs a restart (content read at launch).
3. Read the repository instructions and the skill or documentation for the affected system.
4. Patch the smallest complete surface, including directly dependent localisation, GUI, GFX, or cleanup when required.
5. Run targeted static checks.
6. Restart through the same debug target when the fix requires it.
7. Return to the same test setup or a clean equivalent setup (on a running game, the loaded checkpoint).
8. Reproduce the original sequence, and confirm persistent state with a before-and-after save diff when the fix changed it.
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
