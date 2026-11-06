# Project rules: Skill maintenance

Part of the [hoi4-project-rules](../SKILL.md) skill. `CLAUDE.md` summarizes section 9. Read before creating, changing or sizing a skill, agent prompt or instruction file.

## 9. Skill Maintenance

Use skills actively. Skills are not only for cleanup at the end of a task. They are the agent's memory for repeated workflows, project-specific patterns, hard-won fixes, and instructions that should not be rediscovered every time.

When a task reveals a repeated workflow, repeated mistake, reusable process, repo-specific convention, asset workflow, prompt pattern, or useful implementation rule, use `hoi4_skill_maintainer` or the `skill-creator` skill when it is available to capture it cleanly.

Create or update skills more often during long tasks, especially when working through many events, mechanics, assets, localisation passes, or UI patterns. If the same reasoning would likely be needed again later in the run, spawn `hoi4_skill_maintainer` or update the relevant skill before moving on.

Never put feature-specific, country-specific, or one-off implementation context inside general skills. This is very important!

Rules:

1. Check whether an existing skill already covers the workflow before creating a new one.
2. Use `hoi4_skill_maintainer` for non-trivial skill creation, skill cleanup, routing updates, or multi-skill consistency work.
3. Prefer updating an existing skill when the workflow belongs there.
4. Create a new skill when the workflow is reusable, distinct, and not covered by an existing skill.
5. Add concise, specific rules based on actual task experience, not speculation. Tag each engine fact `[game-tested <version>]`, `[vanilla-confirmed <version>]`, `[docs]` or `[unverified]`.
6. Record repo paths, commands, examples, gotchas, source folders, validation steps, and handoff rules when they prevent rediscovery.
7. Keep each skill focused on one reusable workflow.
8. Do not bloat skills with one-off details that will not help future tasks.
   Keep every skill, agent prompt, and instruction file within the single-read ceiling in `.tools/sync/read_limits.json` (20,000 tokens); `python .tools/sync/check_guidance_size.py` reports any file above it.
   The ceiling is a limit, not a target: leave files that already fit at their current size and do not pad or shorten them.
   The kit's source package also enforces a context budget from the same file: the instruction template holds at most 4,000 tokens, each `SKILL.md` at most 5,000 tokens with its details in `references/`, and each skill `description` is one sentence of at most 200 characters.
   A description is a YAML value, so avoid a colon followed by a space in it or quote it. The Validate workflow fails above these limits.
   When a file exceeds it, bring it just below the ceiling by moving complete topics into linked `references/` files or by removing genuine duplication, preserving every requirement and updating references.
   Never treat truncated tool output as a complete read; reread the rest before acting on the file.
9. During large multi-feature runs, review skill gaps after each completed feature or shared system. Update or create skills before starting the next feature if something reusable was learned.
10. Report which skills were used, created, or updated at the end of each task.

Skill files must keep valid frontmatter, because a skill with missing or invalid `name` or `description` frontmatter is skipped by the runtime instead of being reported as broken. Keep `name` kebab-case and matching the containing directory or file name, and keep `description` a complete sentence that names when the skill applies.
