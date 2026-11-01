# Upfront consultation

`CLAUDE.md` (Upfront consultation) holds the short rule. This file is its detail: when a consultation is held, how open points are sorted, the standard questions with suggested answers, where answers are recorded, and what may still be asked later.

The goal is one organized round of questions at the start, then uninterrupted work. A question asked mid-task that could have been asked at the start is a process failure, and so is a question about something the agent should decide itself.

## When it applies

Hold a consultation before a task that creates or reshapes a feature, system, country, route set or asset set, that spans three or more surfaces (for example focus tree, events and decisions), or that has no accepted spec.

Skip it for bug fixes, single-surface edits, and follow-up work inside an accepted spec whose `decisions.md` already answers the open points.

## Inspect first

Before asking anything, read the project instructions, the relevant specs and plans under `docs/specs/` and `docs/plans/`, the feature's `decisions.md` when it exists, and the mod files the task touches. Use the reference tools for engine questions.

Never ask what a file, a spec, vanilla or the engine documentation can answer.

## Sort every open point

| Group | What belongs here | What to do |
| --- | --- | --- |
| Established | Stated by the user, an accepted spec or `decisions.md` | Use it. Do not ask again |
| Yours to decide | Derivable from the instructions, precedent in the mod, vanilla or the engine rules, and every routine implementation choice | Decide, and list the decision so the user can overrule it |
| Genuine question | Changes player-visible design, scope, canon, cost, risk or an irreversible action, cannot be derived, and has no safe reversible default | Ask once, with a suggested answer |

## Ask once

Send one message, grouped by surface. Give every question a suggested answer and a one-line reason, so the user can reply "all suggestions" or change only some. Follow the questions with the short list of decisions you will take yourself.

For a large task, announce the later batches up front, for example "after the spec draft" or "after the first implementation tranche", and keep each batch to about seven questions.

When the user has said to work without questions, or nobody can answer, apply the suggested answers, record them as agent defaults, and list them in the final report.

## Standard questions

Ask only the ones that are genuine for the task. The suggested answers are starting points, not defaults to apply silently.

| Topic | Question | Usual suggestion |
| --- | --- | --- |
| Scope | Which surfaces are in (focus tree, events, decisions, ideas, characters, assets, localisation, AI)? | Every surface the idea names, plus the AI and localisation they need |
| Depth | How many routes, branches or variants, and roughly how large is each? | The depth standard of `hoi4-feature-planning` |
| Canon and tone | Which lore, real people or sensitive topics constrain the design? | The established canon in the specs |
| Fallback policy | When a requested part cannot be built as specified, stop and report, or substitute and report? | Stop and report. The answer is the standing approval that the fallback rule in `CLAUDE.md` asks for |
| Asset sources | Generated, vanilla reuse or sourced art for each asset group, and may vanilla art be sent to an image provider as a reference? | The project's configured image route. Vanilla references stay off unless the project turns them on |
| Spend | What budget may paid operations use (image generation, 3D models)? | Ask once for one budget. Never ask per call afterwards |
| Audio | May a track be reused, run longer than two minutes, or use a non-music cue? | Decide per super event at intake, following `hoi4-super-events` |
| Saves | Are saves in scope, and may the game write them as text (`save_as_binary=no`)? | Ask only when the task inspects saves, following `hoi4-save-inspection` |
| World iteration | The design needs an effect or trigger that iterates over every country. May it? | Ask whenever the spec implies it. Without permission, design a narrower scope |
| Animation | Is motion wanted, and may a narrow exploration pass run where no precedent exists? | Static unless the idea asks for motion |
| Improvement rounds | Improvement proposals come after the first tranche. Answer each with Adopt, Adapt, Defer or Reject | Announce the round. Do not hold it now |

Live testing and the autonomous debug playtest run only when the user names them, so never offer them as a question. The user may still raise them in an answer.

## Record the answers

Write every answer and every default to `docs/specs/<feature_slug>/decisions.md`, and update the spec part it affects.

| ID | Item | Decision | Origin | Date | Basis |
| --- | --- | --- | --- | --- | --- |
| D-01 | Fallback policy | Stop and report | user | 2026-01-01 | Consultation answer |
| D-02 | Route count | Three routes | agent default | 2026-01-01 | Depth standard; the user did not answer |

Origin is `user`, `established` or `agent default`. An agent default stays open to change and never counts as user approval, which follows the acceptance rules in `CLAUDE.md` (Specs and Plans). Improvement-round answers go to the same file with the proposal they answer, mapped onto the plan dispositions: Adopt is implemented or promoted to a named spec, Adapt is promoted with the change recorded, Defer is queued with a reason, and Reject is rejected with a reason.

## Later questions

After the consultation, work without asking again about anything recorded. A later question is allowed only when it could not be foreseen, or when it hits a hard gate:

- spend above the authorized budget;
- an action that `CLAUDE.md` gates on permission, such as world iteration;
- a change that widens the agreed scope.

Ask it once, batched with any other open item, with a suggested answer, and continue independent work meanwhile.

## Never ask

- about naming, file layout inside the established layout, localisation keys, code factoring, tool choice, the order of work, which checks to run, or retries;
- for logs, for in-game testing, or for the user to reload the game;
- for confirmation of a paid call that the agreed budget covers.

## Subagents

Subagents have no channel to the user. They decide what is theirs to decide and put every genuine open item in their handoff. The parent folds those items into its next batch.
