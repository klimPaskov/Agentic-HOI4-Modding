# Project rules: Deterministic tools and checks

Part of the [hoi4-project-rules](../SKILL.md) skill. `CLAUDE.md` summarizes section 4a. Read before running a check, adding a tool or script, or interpreting a check result.

## 4a. Deterministic Tools and Checks

Mechanical questions get mechanical answers. Before reasoning through a question that a file can answer (does this key, sprite, texture or flag exist, is this size or frame count right, is this output stale), run the existing check.

1. Look first. `.tools/README.md` indexes every maintained tool and the question it answers, and skills name the checks for their workflows. Run `python -B .tools/check.py quick` on the files you changed before review, and `python -B .tools/check.py full` at the end of a large task. Read a check's documented limits before relying on its result.
2. Add or improve a tool only for a recurring task with an explicit rule, known inputs and an independently checkable result. Extend the owning tool before creating a new one, and give each new rule one valid and one invalid fixture.
3. Document every maintained tool in `.tools/README.md` or its package README: purpose, command, inputs, outputs, dependencies, callers, the rule or reference it enforces, and its limits. Checks are read-only by default; fixers are separate and explicit.
4. Place shared tools under `.tools/` with one canonical implementation in `.tools/lib/`, and helpers used by one skill in that skill's `tools/` or `scripts/` folder. Never copy a tool between `.tools/`, `.claude/`, `.agents/` or another runtime folder.
5. When a reusable workflow gains or changes a tool, update the skill that owns the workflow in the same change.
6. Keep one-off repairs, migrations, job-specific scripts, temporary checks and their outputs in ignored `.tmp/<task>/`. Retain maintained regression tests that protect a current contract; a filename or date does not make a test disposable. Promote a helper only for demonstrated recurring use or a required shared entry point; command-line arguments alone do not make a one-off tool reusable.
7. Before adding a skill, document, report, wrapper or helper, check its existing owner and extend that source. Keep one current task report, avoid duplicate instruction copies outside the established synchronizers, review new files for unnecessary scaffolding before completion, and control bloat by removing duplication and keeping temporary work out of maintained paths, not by deleting specific requirements or shortening them into generic advice.
8. Tools never replace design, gameplay reasoning, writing, art direction or review. Do not generate focus trees, events, decisions, ideas, localisation prose or lore with scripts, do not spend a goal on scripts, report generators or bulk-generation helpers while the content stays shallow or incomplete, and do not count generated volume as progress.
9. A passing check proves only the properties it checks. A size or alpha check does not establish visual quality, and a reference check does not establish gameplay behaviour; report it that way.
10. Never weaken a check, add a suppression, lower a threshold, edit a baseline or change a requirement to make validation pass. Fix the finding, or report it with its reason and get the rule owner's decision.
