---
name: hoi4-shared-git-commit
description: Use when committing one finished HOI4 mod change from a shared working tree whose index or files also contain other agents' staged or unstaged work.
---

# Shared Working Tree Commit

Use this workflow only for a finished, reviewed change that must be committed while unrelated work remains in the same checkout. Follow `AGENTS.md` for commit scope and completion. Detect concurrent changes to `HEAD` or relevant index entries, and rebuild or coordinate only when the checks show an actual conflict.

1. Record the exact `HEAD` object ID and symbolic branch ref, and inspect the real index and working-tree diffs for every affected path. Record the real index entries and unrelated staged hunks that must survive. Stop on unresolved index entries or ambiguous ownership. Use literal Windows paths and PowerShell argument arrays where quoting matters; `JSON.stringify()` is not shell escaping.
2. Create a unique temporary `GIT_INDEX_FILE` outside the real index. In PowerShell, save any existing `$env:GIT_INDEX_FILE`, set it to the temporary path for the isolated Git commands, and restore the previous value in `finally`. Initialize it with `git read-tree <recorded-HEAD>`. Add only paths owned in full with `git add -- <exact-paths>`. For a file with mixed ownership, apply a manually reviewed patch containing only owned hunks with `git apply --cached <owned-patch>`; never add the whole file. When omitting earlier hunks from a full diff, recalculate the retained hunks' new-side line positions so they do not retain offsets from omitted changes, and verify the isolated patch applies before constructing the commit. If hunks cannot be separated reliably, stop and coordinate the edit.
   Preserve hunk whitespace exactly: a blank context line contains its leading context space; never use `trimEnd()` on hunk content.
   Keep stderr separate from patch stdout, or strip only confirmed stderr warning lines outside the patch without altering context lines.
3. Check the temporary index with `git diff --cached --name-status <recorded-HEAD>` and `git diff --cached <recorded-HEAD>`. Every changed path and hunk must belong to this commit. Run `git write-tree` against that index. Before moving `HEAD`, prepare the real-index reconciliation for mixed files in a second temporary index: `git read-tree <proposed-tree>`, apply only the other work that was staged in the original real index, and review the resulting blobs and staged diff. Preserve file mode and binary content. Stop if the other staged changes cannot be carried forward exactly.
4. Run `git commit-tree <proposed-tree> -p <recorded-HEAD> -F <message-file>`. Restore the real `GIT_INDEX_FILE` setting. Recheck the symbolic branch, `HEAD`, and captured real-index entries for affected paths, then publish with `git update-ref HEAD <new-commit> <recorded-HEAD>`. The old object ID is the compare-and-swap guard. If it fails, leave the real index alone and rebuild from the new `HEAD`; never retry the old tree or force the ref.
5. After the ref moves, reconcile only paths in this commit's ownership. Set fully owned real-index paths to the new `HEAD` entries with `git restore --staged --source=HEAD -- <exact-paths>`. Set each mixed file's real-index entry to its previously reviewed reconciliation blob with `git update-index --cacheinfo <mode>,<blob-id>,<exact-path>`, so unrelated staged hunks remain staged. Verify the relevant real-index entries have not changed since capture before updating them; if they have, stop for coordination. Do not touch the working-tree copies or reset the whole index. Review `git show --stat --oneline HEAD`, `git show HEAD`, and the remaining staged and unstaged diffs, and confirm unrelated work retains its prior staged or unstaged state.

   For fully owned new paths, `git restore --staged --source=<new-commit> -- <exact-paths>` also creates missing index entries; for mixed paths absent from the real index, use `git update-index --add --cacheinfo <mode>,<blob-id>,<exact-path>` with the reviewed reconciliation blob.

For example, when one Markdown file contains your edited paragraph and another agent's staged paragraph, the isolated commit index receives only your paragraph's patch. The reconciliation blob starts from your new committed file and reapplies the other paragraph's staged patch, so that paragraph is still staged after the commit.

Never use `git add -A`, a broad pathspec, a normal `git commit` against the shared index, or `git reset --hard` for this workflow. If the ref update succeeded but index reconciliation cannot be completed safely, report the new commit and the exact remaining index state; do not rewrite or reset the commit automatically.

## Index lock failures

When the checkout lives in a cloud-synchronized folder, or another tool watches `.git`, the reconciliation step can fail with `Unable to create .git/index.lock: File exists` right after `update-ref`. Never hide that step's errors (no `|| true` or `2>/dev/null`): a silent failure leaves the committed paths staged as deletions or reversions against the new `HEAD`.
Always confirm no `git` process is running, then wait and retry reconciliation before considering lock removal.
Recheck the lock's identity and age across the wait and retry, and remove only a provably stale lock; the absence of an observed `git` process alone is insufficient proof, and an active actor's lock must never be removed.
Rerun the same reconciliation and check that `git status --short -- <exact-paths>` shows only their pre-commit unstaged state.
