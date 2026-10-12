# Runtime synchronizers

Claude Code is the canonical runtime. These one-way tools regenerate what the other runtimes read from the canonical Claude files:

| Tool | Canonical source | Writes | Configuration |
| --- | --- | --- | --- |
| `sync_instructions.py` | `CLAUDE.md` (and `CLAUDE_template.md` in the source package) | `AGENTS.md` (`AGENTS_template.md`) | `instruction_projection.json` |
| `sync_agents.py` | `.claude/agents/*.md` | `.codex/agents/*.toml` and the `[agents.*]` rows of `.codex/config.toml`, `.cursor/agents/`, `.qoder/agents/`, `.opencode/agent/`, and each runtime's `agent-map.md` | `agent_profiles.json` |
| `sync_skills.py` | `.claude/skills/` | `.agents/skills/` (Codex, DSH) and `.qoder/skills/` (Qoder) copies | none |
| `check_guidance_size.py` | instruction files, skills, and agent prompts | nothing; reports files above the single-read ceiling | `read_limits.json` |

```powershell
python .tools/sync/sync_instructions.py
python .tools/sync/sync_agents.py
python .tools/sync/sync_skills.py
python .tools/sync/check_guidance_size.py
```

Run the three synchronizers after editing a canonical file, and run them with `--check` during validation; `--check` writes nothing and exits with status 1 when a projection is out of date.
Run `python .tools/sync/sync_agents.py --verify` to check the role tier and effort policies in `agent_profiles.json` and read back every generated definition without writing. A valid frontmatter tier alone does not establish that it is the intended tier for that role.
The tools use only the Python standard library and run on Python 3.9 or newer.

## Rules

The image-generation provider markers remain the same in canonical instructions and generated runtime files. HOI4 Mod Setup fills each marker from the provider table in the manifest revision selected for that project.

- Edit only canonical files. A generated file carries a header naming its source; hand edits are overwritten on the next run.
- `sync_agents.py` maintains a runtime only when its folder exists in the project, so a mod set up for Claude Code and Codex never receives Cursor files. Pass `--runtime <name>` to create one explicitly.
- It deletes only projection files it generated earlier whose canonical agent is gone, and it rewrites only the `.codex/config.toml` agent rows that point at generated TOML files. Other Codex settings are left untouched.
- Agents are discovered from `.claude/agents/`; adding an agent never requires editing a script. Each canonical agent needs `name` (its hyphen-case file name), `description`, `model` (`opus`, `sonnet`, or `haiku`), and a valid `effort` field. `disallowedTools: Write, Edit, NotebookEdit` marks a read-only role.
- `agent_profiles.json` translates the Claude tier for other runtimes: the Codex reasoning effort (and an optional fixed `model`), the Codex sandbox per authority, the Cursor and OpenCode model setting, and the Qoder tool list.
- `instruction_projection.json` lists the exact phrases that differ between `CLAUDE.md` and `AGENTS.md`. Keep the list short; write the canonical file so that every other sentence is correct for both.
- `sync_skills.py` copies by default because HOI4 Mod Setup tracks installed files. `--mode link` replaces a copy with a directory junction (Windows) or symbolic link for projects that do not use the app. A skill that exists only in a copy is reported and kept.
- `read_limits.json` sets the 20,000-token single-read ceiling (measured at about 3 bytes per token, so 60,000 bytes for instruction files and agent prompts and 58,000 bytes for a root `SKILL.md`). It is a ceiling, not a target. Bring an oversized file just below it by moving complete topics into linked `references/` files; never shorten requirements to fit.

DSH has no project agent registry, so it has no agent projection; it reads `AGENTS.md`, `CLAUDE.md`, and the `.agents/skills/` copy. See `docs/runtimes.md`.
