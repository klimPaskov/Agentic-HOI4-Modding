# Agentic HOI4 Modding

A practical starter kit for using coding agents on Hearts of Iron IV mods.

This repo gives you a reusable `AGENTS.md` example, offline wiki references, repo skills, and optional Codex subagent configs that can be adapted into your own mod repo.

Watch the video tutorials: https://www.youtube.com/playlist?list=PLh6JmuEabQioc4V8IYGEsMtqiw-xemeX3

## Who should use this

This is for HOI4 modders who already understand the basics of modding and want AI to handle more of the repetitive work.

This is not a magic replacement for modding knowledge. You still need to review the diff, understand the design, and test the result in game.

## What this repo provides

- `AGENTS_example.md`, a real, full project instruction for a large HOI4 mod, Chaos Redux.
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

A practical WSL path is:

```text
~/projects/Hearts of Iron IV/
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

Then adapt it to your real project. Replace project-specific names, paths, skills, subagents, docs policy, asset folders, and validation rules.

Generic instructions help less than specific ones. A large mod should document event formats, naming rules, integration points, docs policy, asset rules, subagent routing, completion proof, and git expectations.

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
- spreadsheet and documentation updates

The main agent should still own final implementation, final wiring, final review, final validation, and the completion report.

### 7. Keep asset ownership clear

Asset subagents should produce source files, processed PNG previews, DDS files, manifests, contact sheets when useful, and `gfx_handoff.md`.

The main agent should own `.gfx` edits, event references, focus icon assignments, idea icon assignments, decision icon assignments, localisation references, GUI references, documentation alignment, and validation.

This split avoids having an asset worker silently change gameplay or UI wiring.

### 8. Start the agent from the repo root

Run your coding agent inside the repository root so it can see `AGENTS.md`, the mod files, docs, skills, local references, and optional `.codex/agents/` configs.

## Windows and WSL

For Windows users, WSL is usually the cleanest setup.

A practical layout is:

```text
/home/<you>/projects/<your_mod>
```

Then link the project into the normal HOI4 mod folder on Windows so the game can load it.

Example Windows mod folder:

```text
C:\Users\<you>\Documents\Paradox Interactive\Hearts of Iron IV\mod\<your_mod>
```

The important part is that your development environment stays in WSL while HOI4 still sees the mod in its normal place. You can achieve that using a Windows directory symbolic link.

## MCP servers and apps

MCP servers and apps are optional tools that can expand what the agent can access.

Do not add tools just because they exist. More tools can also mean more noise, more tokens, and more confusion. Add tools when they solve a real workflow problem.

Good use cases include web research, image sourcing, document conversion, spreadsheets, asset processing, or project-specific integrations.

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
