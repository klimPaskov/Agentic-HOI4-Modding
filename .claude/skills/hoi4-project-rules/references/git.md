# Project rules: Git

Part of the [hoi4-project-rules](../SKILL.md) skill. `CLAUDE.md` summarizes section 10. Read before committing.

## 10. Git

After completing each meaningful plan, create a Git commit.

The commit must only include changes related to that plan. Before committing, review the diff, verify that the implementation is complete.

Use a clear commit message that describes what was implemented.

Do not commit broken, unrelated, or half-finished work. If the goal cannot be completed cleanly, report the blocker instead of creating a misleading commit.

When the working tree or index also contains other agents' staged or unstaged work, commit only the owned paths and hunks through `hoi4-shared-git-commit`. Never use `git add -A`, a broad pathspec, a normal commit against the shared index, or `git reset --hard` in a shared checkout.
