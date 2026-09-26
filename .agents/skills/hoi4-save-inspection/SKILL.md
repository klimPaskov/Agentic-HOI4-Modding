---
name: hoi4-save-inspection
description: Use when the user supplies, names, or offers a Hearts of Iron IV save, or when runtime state would settle a question that source reading cannot, such as which flags and variables are really set, why a decision is unavailable, what an action changed, whether state survives save and reload, what the AI did over time, whether script state leaks, or how an engine rule behaves. Reads plain-text saves with the bundled read-only inspector.
---

# HOI4 Save Inspection

A plain-text save is the game's full runtime state written as ordinary Clausewitz script. Reading it replaces guessing: flags, variables, arrays, state data, and global flags show exactly what the scripts produced in a real session. This skill turns saves the user provides into evidence.

The bundled inspector is `scripts/save_inspect.py` (Python 3, no dependencies, read-only). Run it from the repository root:

```powershell
python .agents/skills/hoi4-save-inspection/scripts/save_inspect.py <command> <save> [...]
```

## 1. Boundaries

- The inspector never modifies a save. Never copy saves into Git; they are large and personal.
- Never edit the user's HOI4 `settings.txt` or launch the game. Live play, saving, and console commands belong to the user, or to `hoi4-debug-playtest` when the user explicitly invokes it.
- When the project instructions forbid asking for logs, a save is still different: when runtime state would decide a question that source reading cannot, you may offer one concrete save request (which moment, which save name) instead of guessing. Never make a save a precondition for fixing a clear source defect.
- Save evidence proves the state of that save only. Record its file name, in-game date, game version, and the commands you ran. Do not generalise one save into coverage of other countries, dates, or branches.
- Save evidence complements, and never replaces, the HOI4 MCP evidence and audits that the project instructions require for the same surface.

## 2. Plain-text saves

Saves live in `<Documents>/Paradox Interactive/Hearts of Iron IV/save games/`, where `<Documents>` may be redirected to OneDrive (`autosave.hoi4` is the latest autosave).

The inspector reads only plain-text saves (header `HOI4txt`). The game writes binary saves (`HOI4bin`) while `settings.txt` contains `save_as_binary=yes`; binary saves need Paradox's token table, which is not distributed, and the inspector refuses them with instructions. If a supplied save is binary, ask the user once to set `save_as_binary=no` in `Documents/Paradox Interactive/Hearts of Iron IV/settings.txt` and save again. Text saves are larger, so the user may switch the setting back after the investigation.

## 3. Inspector commands

| Command | Use |
|---|---|
| `info SAVE` | header, size, player, date, version |
| `keys SAVE [PATH]` | child keys under a path, with counts; use it to explore |
| `get SAVE PATH [--depth N]` | print a subtree as script |
| `find SAVE REGEX [--in PATH]` | leaves whose path or value matches |
| `flatten SAVE [--in PATH] [--match R]` | one `path = value` line per leaf |
| `diff OLD NEW [--in PATH] [--match R]` | added, removed, and changed leaves |
| `footprint SAVE [--in PATH] [--containers A,B]` | script-state entry counts by name prefix |

Paths use `/` with glob segments: `countries/GER/variables`, `countries/*/flags`. A key repeated inside one block gets an occurrence suffix after its first use (`division`, `division[1]`), and an unnamed block is `-`.

Performance: a full-size text save is hundreds of megabytes. Always pass `--in` when you can; blocks outside it are skipped by a fast brace scan. For many questions against one save, write `flatten --in <area>` once to a file in your scratch directory and search that file.

Layout: Jomini's HOI4 save model confirms `countries = { TAG = { variables = { ... } } }`. Confirm the other container names (flags, arrays, states, global data) with `keys` on the first real save of a session, pass them to `footprint --containers`, and record confirmed names in this skill so later runs start from facts.

## 4. Recipes

### 4.1 Why is this unavailable or wrong?

When the user reports that a decision, focus, mission, or event did not behave as expected and supplies a save:

1. Read the relevant trigger in source (`visible`, `available`, `bypass`, `trigger`, scripted triggers) and list every flag, variable, array, and global it reads.
2. Look each one up in the save for the acting scope: `find SAVE "<name>" --in countries/<TAG>`, the state path for state scope, or global data.
3. Report which condition fails with its actual value. Fix the cause in source, not the symptom.

This is offline trigger evaluation. It works for any ROOT, FROM, or state as long as the save contains that scope.

### 4.2 What did this action change?

Ask for two saves around one action: `pre_<name>` just before, `post_<name>` just after. Then:

```powershell
python .../save_inspect.py diff pre.hoi4 post.hoi4 --in countries/<TAG>
python .../save_inspect.py diff pre.hoi4 post.hoi4 --in countries --match "<event or system prefix>"
```

Check that every intended effect appears once, that temporary scaffolding was cleaned up, and that nothing unrelated changed in other countries or in global data. This verifies costs, cleanup contracts, receipts, and ledgers far more precisely than a tooltip.

### 4.3 Does state survive save and reload?

The console command `savecheck` writes `Test_01`, reloads it, and writes `Test_02`. With both saved as text, `diff Test_01.hoi4 Test_02.hoi4` lists every value that did not survive the round trip. Anything owned by the mod in that list is a persistence defect, such as state held only in temporary variables, event targets, or GUI-only values.

### 4.4 What does the AI actually do?

Have the user run `observe` from a fresh start to a target date and save. Then tally outcomes across all countries: `find SAVE "<system>_" --in countries` or `flatten --in countries --match "<prefix>"`. Count which decisions, routes, events, and states the AI reached. Hand these counts to `hoi4_ai_probability_auditor` as live observations beside its HOI4 MCP scenarios, and compare them with the intended weights. One observer run is a sample, not a distribution; say how many runs back a conclusion.

### 4.5 Is script state leaking?

Run `footprint` on an early and a late save of the same campaign with the same `--in` and `--containers`. A prefix whose entries or array elements keep growing points to state that is never cleared (per-state variables left behind, arrays that only append, flags never removed). Map the prefix to its owning system and check its cleanup path against the lifecycle rules in the project instructions and the owning skill.

### 4.6 Settling an engine question

When a rule is uncertain (for example whether `for_each_scope_loop` stops at 1,000 iterations like `for_loop_effect`), design the smallest probe that records its result in a variable. Prefer an inline probe the user pastes into `eval_effect`, which needs no repository change. When the probe is too large for one console line, add a temporary scripted effect that the user runs with `effect <TAG> <probe_effect>`; it is temporary debug code, so remove it once the question is answered. After the probe, the user saves and you read the variable. Record every confirmed rule in the relevant skill or the project instructions. The console `run <file>` command executes a file of console commands, which suits multi-step probes; confirm where it looks for the file on first use.

### 4.7 Is this gate ever reached?

For flags that source analysis reports as checked but never set, search late observer saves: `find SAVE "<flag>"`. Absence across several long runs strengthens a dead-gate finding; presence means a setter exists that static search missed.

## 5. Reporting

State the save file, in-game date, game version, the commands run, and the exact values that support each conclusion. Keep bulky outputs in scratch and quote only the relevant lines. When a save changes what you believed from source, say so plainly and correct the earlier claim.
