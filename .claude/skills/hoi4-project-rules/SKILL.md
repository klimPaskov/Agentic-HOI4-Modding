---
name: hoi4-project-rules
description: Use when a HOI4 mod task needs the full project rules summarized in CLAUDE.md, such as coding style, localisation, completion proof, skill routing, MCP use, subagents, specs, checks or git.
---

# HOI4 Project Rules

`CLAUDE.md` keeps the rules that apply to every task in a few lines per section.
This skill holds the full text of those sections, unchanged, so a session loads it only for the work that needs it.
Read the reference named for your task before you start, and again before you report completion.
A summary in `CLAUDE.md` never replaces the full rule here.

## Reference map

| Read | When | Section of `CLAUDE.md` |
| --- | --- | --- |
| [reading-and-references.md](references/reading-and-references.md) | Before editing engine-facing source, and before relying on the wiki, vanilla documentation or a reference mod. | 0: HOI4 Wiki, Vanilla References, Mod References |
| [skill-routing.md](references/skill-routing.md) | When deciding which repo skill governs a task. | 0: Repo Skills |
| [mcp-usage.md](references/mcp-usage.md) | Before using the HOI4 Agent Tools routes, when a route fails, and before reporting MCP evidence. | 0: HOI4 MCP |
| [agent-runtimes.md](references/agent-runtimes.md) | Before editing a canonical instruction, skill or agent file, or when working in a client other than Claude Code. | 0: Agent runtimes |
| [subagents.md](references/subagents.md) | Before delegating to a project subagent, choosing a model tier or reviewing a handoff. | 0: Subagents |
| [specs-plans-consultation.md](references/specs-plans-consultation.md) | Before writing a spec or plan, or asking the user about a new feature. | 0: Specs and Plans, Upfront consultation |
| [coding-style.md](references/coding-style.md) | Before writing or reviewing any Clausewitz script. | 1 |
| [localisation-ui-naming.md](references/localisation-ui-naming.md) | Before adding anything that appears on screen, and before naming scripted effects, triggers or variables. | 2 and 3 |
| [mechanic-checklist.md](references/mechanic-checklist.md) | Before implementing a new mechanic, and before answering a user's problem report. | 4 |
| [checks-and-tools.md](references/checks-and-tools.md) | Before running a check, adding a tool or script, or reading a check result. | 4a |
| [completion-proof.md](references/completion-proof.md) | Before claiming a goal complete and before writing the final report. | 5 |
| [content-integration.md](references/content-integration.md) | Before wiring an event, a focus tree or a visual asset into the mod. | 6, 7 and 8 |
| [skill-maintenance.md](references/skill-maintenance.md) | Before creating, changing or sizing a skill, agent prompt or instruction file. | 9 |
| [git.md](references/git.md) | Before committing. | 10 |

## Rules that never wait for a reference

- Read the wiki and the installed game documentation through `hoi4.reference_*` before editing engine-facing source.
- Never use `<=` or `>=`, never hard-code tunable numbers, and indent script with tabs.
- Write localisation as UTF-8 with BOM, in the same change as the content it names.
- Never launch Hearts of Iron IV. Live testing belongs to the user unless they invoke `hoi4-debug-playtest` or `hoi4-live-playtest`.
- A goal is complete only with evidence. Report every simplification, omission and blocker.
- Edit canonical files only, then regenerate the projections with `python .tools/sync/generators.py`.
