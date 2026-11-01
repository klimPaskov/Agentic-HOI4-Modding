# Runtime synchronizers

Claude Code is the canonical runtime. These one-way tools regenerate what the other runtimes read from the canonical Claude files. `generators.json` lists every generator and generated-file check with its inputs and outputs, and `generators.py` runs them. `check.py`, `check.py setup` (which HOI4 Mod Setup runs after an install or update), the Claude Code hook, the optional Git hook, CI and the release checks all read that one list.

| Tool | Canonical source | Writes | Configuration |
| --- | --- | --- | --- |
| `generators.py` | `generators.json` | whatever the listed generators write | `generators.json` |
| `sync_instructions.py` | `CLAUDE.md` (and `CLAUDE_template.md` in the source package) | `AGENTS.md` (`AGENTS_template.md`) | `instruction_projection.json` |
| `sync_agents.py` | `.claude/agents/*.md` | `.codex/agents/*.toml` and the `[agents.*]` rows of `.codex/config.toml`, `.cursor/agents/`, `.qoder/agents/`, `.opencode/agent/`, and each runtime's `agent-map.md` | `agent_profiles.json` |
| `sync_skills.py` | `.claude/skills/` | `.agents/skills/` (Codex, DSH) and `.qoder/skills/` (Qoder) copies | none |
| `check_guidance_size.py` | instruction files, skills, and agent prompts | nothing; reports files above the single-read ceiling | `read_limits.json` |

```powershell
python .tools/sync/generators.py                     # run every generator, then the size check
python .tools/sync/generators.py --check             # report stale outputs, write nothing
python .tools/sync/generators.py --paths CLAUDE.md   # run only what these paths affect
python .tools/sync/sync_agents.py --verify           # also check the tier and effort policy
```

Each tool still runs on its own, for example `python .tools/sync/sync_skills.py --skill hoi4-mtth`. Every tool accepts `--root <folder>` to work on another project. The tools use only the Python standard library and run on Python 3.9 or newer.

## When they run

- **Claude Code:** the `PostToolUse` hook in `.claude/settings.json` runs `generators.py --hook` after every Edit or Write, also inside subagents and worktrees. An edit to a canonical file regenerates only the outputs it affects (one skill's copies for a skill edit) and names them so they are committed together with the source. An edit to a generated file is reported with the canonical file to edit instead, and the edit is kept until the next sync. Any other edit starts nothing. Permission deny rules in the same file stop the edit tools from writing generated files.
- **Other runtimes and people:** run `python .tools/sync/generators.py` after editing a canonical file. `python .tools/check.py setup --git-hook` adds an optional pre-commit check of the staged changes. It is off by default and is never installed through `core.hooksPath`.
- **Validation:** `check.py quick` and `full` run the `generators` check, CI runs `generators.py --check` on every pull request, and `scripts/check_release_package.py` also requires every tracked generated file to ship in the manifest.
- **Launcher:** the hooks start Python through `.tools/py.sh`, which finds a working Python 3.9 or newer (`python3`, `python` or `py -3`) and names the problem when there is none.

Exit codes are the same everywhere: 0 in sync, 1 an output is out of date (or was edited by hand), 2 a tool could not run. A crashing or missing generator, a broken `generators.json`, or a folder where no generator has its sources is a failure, never a pass.

## Rules

The image-generation provider markers remain the same in canonical instructions and generated runtime files. HOI4 Mod Setup fills each marker from the provider table in the manifest revision selected for that project.

- Edit only canonical files. A generated file carries a header naming its source where its format allows one; hand edits are overwritten on the next run.
- Add a new generator as an entry in `generators.json` (its script, `inputs`, `outputs`, and `sources`), never as a new hard-coded list. `{item}` in a pattern stands for one folder name, and `item_args` passes it to the tool so one edited item regenerates alone. An entry that lists another in `needs` runs after it and reruns whenever it runs. A generator written before this runner keeps its own command line through four optional fields: `interpreter` (for example `["node"]`), `check_args` (default `["--check"]`, passed in check mode to generators and checks alike, so a check that takes no flag lists `[]`), `root_args` (default `["--root", "{root}"]`, `[]` for a tool that finds the root itself) and `stale_markers` (the output prefixes that mean "out of date", default `DRIFT`, `STALE`, `OVER` and `UNUSED`). Every output of an installed mod must stay inside the paths HOI4 Mod Setup lets `check.py setup` rewrite.
- `sync_agents.py` maintains a runtime only when its folder exists in the project, so a mod set up for Claude Code and Codex never receives Cursor files. Pass `--runtime <name>` to create one explicitly.
- It deletes only projection files it generated earlier whose canonical agent is gone, and it rewrites only the `.codex/config.toml` agent rows that point at generated TOML files. Other Codex settings are left untouched.
- Agents are discovered from `.claude/agents/`; adding an agent never requires editing a script. Each canonical agent needs `name` (its hyphen-case file name), `description`, `model` (`opus`, `sonnet`, or `haiku`), and a valid `effort` field. `disallowedTools: Write, Edit, NotebookEdit` marks a read-only role.
- `agent_profiles.json` translates the Claude tier for other runtimes: the Codex reasoning effort (and an optional fixed `model`), the Codex sandbox per authority, the Cursor and OpenCode model setting, and the Qoder tool list. `codex.agent_models` pins a Codex model for named agents (see `docs/runtimes.md`); `--verify` fails when it names an agent that does not exist (an installed mod may hold only some agents, so writing and `--check` ignore entries for absent agents).
- `instruction_projection.json` lists the exact phrases that differ between `CLAUDE.md` and `AGENTS.md`. Keep the list short; write the canonical file so that every other sentence is correct for both. A phrase that occurs only in some sources names them as a third element, and a phrase that no longer occurs in a source it applies to is reported as `UNUSED`.
- `sync_skills.py` copies by default because HOI4 Mod Setup tracks installed files. An installed mod needs `.agents/skills` when it has `.codex/` and `.qoder/skills` when it has `.qoder/`, and `--check` reports a missing required copy. The source package tracks only the canonical library. `--mode link` replaces a copy with a directory junction (Windows) or symbolic link for projects that do not use the app. A skill that exists only in a copy is reported and kept.
- `read_limits.json` sets the 20,000-token single-read ceiling (measured at about 3 bytes per token, so 60,000 bytes for instruction files and agent prompts and 58,000 bytes for a root `SKILL.md`). It is a ceiling, not a target. Bring an oversized file just below it by moving complete topics into linked `references/` files; never shorten requirements to fit.

DSH has no project agent registry, so it has no agent projection; it reads `AGENTS.md`, `CLAUDE.md`, and the `.agents/skills/` copy. See `docs/runtimes.md`.
