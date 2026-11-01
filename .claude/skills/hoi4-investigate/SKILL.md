---
name: hoi4-investigate
description: Use for any HOI4 mod bug, regression, crash the user describes, or "it worked before", before any fix, and when checking a "done" or "checks pass" report. Static root-cause protocol from source, vanilla and documentation, with log reading only when a log is already supplied.
---

# HOI4 Investigate

Find the real cause of a defect from source before changing anything. This skill is static: it reads the mod, vanilla, the game's documentation and the reference tools, and it never launches the game. Live testing stays with `hoi4-live-playtest` and `hoi4-debug-playtest`, which run only when the user names them.

Evidence tags: `[game-tested 1.19.3]` (observed in the running game), `[vanilla-confirmed 1.19.3]` (the installed vanilla script shows it), `[docs]` (the game's own documentation states it) and `[unverified]` (plausible, not confirmed).

## 1. Root cause before any edit

- Make no edit until you can name the exact file, line, identifier and mechanism that fails. If you notice that you are proposing a change before that, go back to the cause.
- Fix only what is proven. When only part of the cause is proven, fix that part and report the rest as open.
- Never edit only to silence a validator, a warning or an error line. Do not fix warnings by suppressing, deleting, or renaming content without understanding the gameplay consequence.
- Do not dismiss a new error introduced after the agent's own patch as pre-existing. Treat it as part of the current change set until disproven with evidence.
- Do not blame vanilla or another mod before you have checked vanilla source for the same pattern and found the defect there.

## 2. Premise tripwires

Facts from memory, plans, handoffs, earlier audits, status reports and your own earlier messages describe a past state. These phrases mean you are about to rely on one, whether you read them or write them:

- "the plan says", "the handoff says", "a previous pass found", "as before", "it was already fixed"
- "should work", "probably", "presumably", "it must be"
- "the checks pass", "the validator is green", "the tool accepted it"

When one appears, re-read the current files before you scope or report anything.

## 3. Evidence ladder

Each rung proves more than the one below it. Report the highest rung you reached, and never describe a lower rung as a higher one.

1. A tool or agent accepted the change.
2. A static check or validator passes.
3. You re-read the changed source and traced the identifier through every file that reads it.
4. Vanilla precedent, the game's documentation or the reference tools confirm the mechanism.
5. A game log the user supplied is clean for the mod's own identifiers.
6. The user observed the behaviour in game.

Static work normally ends at rung 4. Never ask for rungs 5 and 6: the project instructions forbid asking for logs or in-game testing. Use them when the user supplies them.

## 4. Red flags in a fix

- A fix that works through a path you did not expect is an alarm, not cleverness. Retrace it. Typical cases: a key added to a file the game never loads, a check relaxed or skipped, an identifier moved to a new file while the old definition still exists.
- Measure before fixing a "many" or a "drop": count the real occurrences in the source or the log first. The real number is sometimes small, or zero.

## 5. Parser cascades

- One malformed block (an unbalanced brace, a stray quote, a missing `=`) can produce many later errors in the same file, or hide errors that come after it. Fix the first error in a file first, then check again. [unverified]
- A parsed-object key recovered from a crash dump is an investigative lead, not proof that the named entry alone caused the crash. Shortening or removing it does not establish a cause without a successful controlled retest.
- Resolving an early parse crash can expose a large downstream error batch that earlier launches never reached, so distinguish newly observable errors from demonstrated patch regressions.

## 6. When a log is already supplied

Never ask for logs and never search the user's folders for them. When the user supplies a log or a crash folder, read it in this order, and use `hoi4.error_log` for the error log:

1. The last lines of `logs/game.log`: the in-game date and subsystem the game reached. Its start-date line shows which start actually ran, which can differ from the one the mod intends. [unverified] (observed in game output)
2. For a crash to desktop, `exception.txt` in the crash folder under `crashes/`. An access violation (`C0000005`) is an engine fault that `error.log` does not show, so look at what the engine was loading at that date before reading event text. The crash folder, `crashes/hoi4_<date>_<time>/`, also holds `meta.yml` and `minidump.dmp`; there is no `exceptions.log`. [unverified] (observed in game output)
3. The active mod list in `dlc_load.json`. The launcher reads the outer `mod/<name>.mod` file it lists, so compare that file's `path` and `replace_path` lines with the mod's own descriptor. A stale outer file can bring back vanilla folders the mod replaces. [unverified] (layout observed, which file wins is not tested)
4. `error.log` filtered by the mod's own identifiers: tag, event namespaces, focus, decision and idea ids, scripted effect and trigger names. Lines from other mods or vanilla are not yours to fix.
5. `text.log` for duplicate localisation keys. A pair can be an intended `localisation/replace/` override. [unverified]

To learn what condition an engine error message checks, search the game executable for its exact text and read the strings around it; the condition is often narrower than the message suggests.

## 7. Report

State the root cause with file and line evidence, the rung reached, what remains unproven, the fix (applied or proposed), and the regression check that covers it. If an indispensable input is missing, finish the independent work and list the question for the next batch (Upfront consultation in `CLAUDE.md`).
