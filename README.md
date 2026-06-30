# Agentic HOI4 Modding

A starter kit for using coding agents on Hearts of Iron IV mods.

This repo gives you a reusable `AGENTS.md` example, offline wiki references, repo skills, and optional Codex subagent configs that can be adapted into your own mod repo.

Watch the video tutorials: https://www.youtube.com/playlist?list=PLh6JmuEabQioc4V8IYGEsMtqiw-xemeX3

## What this repo provides

- `AGENTS_chaos_redux.md`, a real, full project instruction for a large HOI4 mod, Chaos Redux.
- `AGENTS_template.md`, a template `AGENTS.md` file that can be adapted to your own mod. Just replace the placeholders.
- Offline Paradox wiki references for syntax and engine behavior.
- Example repo skills for repeated HOI4 workflows.
- Optional custom Codex subagent patterns for bounded research, asset work, audits, and documentation.
- A model for separating main-agent implementation from helper-agent production and audits.

## Recommended setup

### 1. Put the mod in git

Use a normal git repository for the mod. Git is important because agents can make broad edits quickly, and you need a clean way to review, revert, and commit changes.

### 2. Make vanilla HOI4 readable

The agent should be able to inspect vanilla files. Vanilla implementations are usually the best examples for syntax, file structure, and edge cases.

The usual Windows path is:

```text
C:\Program Files (x86)\Steam\steamapps\common\Hearts of Iron IV\
```

### 3. Keep the offline wiki snapshot available

Put the offline wiki folder somewhere predictable, then point your `AGENTS.md` rules at that path.

For example:

```text
paradox_wiki/
```

The agent should consult the offline wiki before editing systems that depend on HOI4 syntax or engine behavior.

### 4. Copy the project instructions

Copy `AGENTS_template.md` into the root of your mod repo as `AGENTS.md`.

Then adapt it to your real project. Replace project-specific names, paths, skills, subagents, docs policy, asset folders, validation rules, and any workflow rules that only apply to the example project. Codex can do the first adaptation pass by inspecting the repo and local setup.

Example Codex prompt:

```text
I am adapting an AGENTS.md template for a Hearts of Iron IV mod repo.

Work from the current repo root. Use AGENTS_template.md as the base and create or update AGENTS.md for this specific mod.

First discover the project setup yourself. Inspect the repo files, descriptor.mod, folder names, existing docs, .agents/skills, .codex/agents, git root, common script prefixes, namespaces, localisation prefixes, event namespaces, and any existing project instructions. Also inspect likely local Windows paths for Hearts of Iron IV and the Paradox user mod folder where needed.

Discover these values where possible:
- Mod name
- Mod prefix or namespace
- Mod repo path
- Vanilla HOI4 path
- Offline Paradox wiki path
- Docs folder
- Main systems in this mod
- Existing repo skills
- Existing Codex subagents
- Approved reference mods and paths
- Project-specific rules, including naming rules, event formats, file placement, completion rules, asset rules, and validation rules

If a value cannot be discovered confidently after inspection, stop and ask me for that specific value before editing AGENTS.md. Do not invent missing paths, skills, agents, reference mods, or rules.

Instructions:
1. Replace all template placeholders with discovered project values.
2. Remove optional sections for tools, skills, subagents, reference mods, or workflows this project does not use.
3. Keep core general instructions as is.
4. Preserve the structure and style of the template.
5. Report what you changed and list any values that still need confirmation.
6. Do not create a commit unless I explicitly ask for one.
```

### 5. Copy or create repo skills

Skills are best used for repeated tasks.

Put skills under:

```text
.agents/skills/
```

Use skills for workflows that repeat, such as events, assets, super-events, focus trees, decisions, country packages, scripted systems, localisation, and documentation.

The point is to stop the agent from rediscovering the same process every time. If a workflow repeats, turn it into a skill or improve an existing one.

### 6. Add optional Codex subagents

Custom Codex subagents are useful when a task can be split into bounded helper work.

Put subagent TOML files under:

```text
.codex/agents/
```

Use subagents for work such as:

- repo exploration before edits
- archival image sourcing
- generated event art
- icon production
- quote, remark, and audio research (for super events for example)
- focus tree audits
- decision and mission audits
- country package audits
- localisation audits
- scripted system architecture
- event completion audits
- documentation updates

The main agent should still own final implementation, final wiring, final review, final validation, and the completion report.

### 7. Keep asset ownership clear

Asset subagents should produce source files, processed PNG previews, DDS files, manifests, contact sheets when useful, and `gfx_handoff.md`.

The main agent should own `.gfx` edits, event references, focus icon assignments, idea icon assignments, decision icon assignments, localisation references, GUI references, documentation alignment, and validation.

This split avoids having an asset worker silently change gameplay or UI wiring.

### 8. Start the agent from the repo root

Run your coding agent inside the repository root so it can see `AGENTS.md`, the mod files, docs, skills, local references, and optional `.codex/agents/` configs.

## Windows native Codex setup

For Windows users, the simplest setup is to keep the mod repo in a normal Windows folder and open that folder directly in Codex.

The easiest layout is to clone the mod straight into the normal HOI4 mod folder:

```text
C:\Users\<you>\Documents\Paradox Interactive\Hearts of Iron IV\mod\<your_mod>
```

Some Windows installs use OneDrive for Documents:

```text
C:\Users\<you>\OneDrive\Documents\Paradox Interactive\Hearts of Iron IV\mod\<your_mod>
```

A practical setup is:

```text
HOI4 mod folder
        ↓
native Windows git repo
        ↓
Codex opened from the repo root
        ↓
HOI4 launcher loads the same folder
```

After cloning, check the mod descriptor. Its `path="..."` value should point to the real Windows folder that contains the mod. If the repo folder name changes, update the descriptor path to match it.

Start Codex from the repository root so it can see `AGENTS.md`, `.agents/skills/`, `.codex/agents/`, `paradox_wiki/`, docs, and all mod files from one native Windows path.

## MCP servers and apps

MCP servers and apps are optional tools that can expand what the agent can access.

Do not add tools just because they exist. More tools can also mean more noise, more tokens, and more confusion. Add tools when they solve a real workflow problem.

Good use cases include web research, image sourcing, document conversion, spreadsheets, asset processing, or project-specific integrations.

## Codex scheduled tasks or Hermes

Codex scheduled tasks (or Hermes cornjobs) can handle recurring modding work.

Good scheduled task use cases for HOI4 modding include:

- scheduled `error.log` checks after launching HOI4
- collecting actionable game errors from the current mod
- turning repeated Discord or GitHub reports into clean implementation prompts
- producing daily or weekly summaries of unresolved bugs, balance complaints, and content requests
- checking whether docs, spreadsheets, plans, and implementation files are drifting apart

A practical setup is:

```text
Codex scheduled task
        ↓
repo-local script or focused recurring prompt
        ↓
collect reports, logs, notes, and screenshots
        ↓
filter for actionable current-mod issues
        ↓
Codex fixes the issue or writes a local handoff file
```

For example, a Codex scheduled task can periodically run a HOI4 error-log watchdog for a fixed test window. The watchdog can launch HOI4, inspect the Paradox `error.log`, copy the log into a repo-local temporary folder, and create a focused Codex prompt such as:

```text
Fix the HOI4 errors reported in this latest automated game run.

error.log path: tmp/hoi4-error-logs/hoi4-error-YYYYMMDDTHHMMSSZ.log

Identify actionable mod errors only. Ignore unrelated vanilla or launcher noise.
After fixing and validating the errors, delete the temporary copied log.
```

Keep scheduled tasks narrow. They should gather evidence, preserve source context, and create precise work items. The main Codex implementation pass should still own code changes, final review, validation, docs alignment, and completion proof.

## Subagent design rules

Subagents should be narrow.

A good subagent has:

- a clear task type
- clear allowed files
- clear forbidden files
- a clear handoff output
- no hidden ownership of final implementation

Use subagents before completion claims, not after claiming the work is done. A subagent report is evidence, not final proof. The main agent must inspect it and fix the issues.

## Completion proof

A goal should not be marked complete unless the implementation is actually complete.

For large events, mechanics, focus trees, country packages, UI work, balance passes, and asset goals, require a concrete completion report. It should list files changed, systems touched, checks run, assets created or reused, docs updated, audits performed, and blockers.

Every simplification should be reported. If no simplifications were made, the agent should say so and provide evidence.

## Customizing this repo for your mod

Do not treat the template as finished once copied.

Your `AGENTS.md` should grow with your project. Add rules when the agent repeats a mistake. Add skills when a workflow becomes common. Add subagents only when the helper role is clear enough to stay bounded.

Good project instructions are specific. A small mod might only need a simple setup. A large mod should document its event format, naming rules, integration points, docs policy, asset rules, subagent routing, completion proof, and git expectations.

## License

Use this template in any way you please for your own HOI4 modding workflow.
