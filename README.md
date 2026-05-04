# Agentic HOI4 Modding

A practical starter kit for using coding agents on Hearts of Iron IV mods.

This repo gives you a reusable `AGENTS.md` template, offline wiki references, and example skills that can be adapted into your own mod repo.

## Who should use this

This is for HOI4 modders who already understand the basics of modding and want AI to handle more of the repetitive work.

This is not a magic replacement for modding knowledge. You still need to review the diff, understand the design, and test the result in game.

## Recommended setup

### 1. Put the mod in git

Use a normal git repository for the mod. Git is important because agents can make broad edits quickly, and you need a clean way to review, revert, and commit changes.

### 2. Make vanilla HOI4 readable

The agent should be able to inspect vanilla files. Vanilla implementations are usually the best examples for syntax, file structure, and edge cases.

### 3. Keep the offline wiki snapshot available

Put the offline wiki folder somewhere predictable, then set `[OFFLINE_WIKI_PATH]` in `AGENTS.md`.

For example:

```text
paradox_wiki/
```

### 4. Copy the template into your mod

Copy `AGENTS.md` into the root of your mod repo.

Then replace the placeholders. The file should describe your real project. Generic instructions help less than specific ones.

### 5. Start the agent from the repo root

Run your coding agent inside the repository root so it can see `AGENTS.md`, the mod files, docs, skills, and local references.

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

The important part is that your development environment stays in WSL while HOI4 still sees the mod in its normal place. You can achieve that using a SymLink.

## MCP servers

MCP servers are optional tools that can expand what the agent can access.

Do not add MCP servers just because they exist. More tools can also mean more noise, more tokens, and more confusion. Add tools when they solve a real workflow problem.

## Skills

Skills are best used for repeated tasks.

The point is to stop the agent from rediscovering the same process every time. If a workflow repeats, turn it into a skill or improve an existing one.

## Customizing this repo for your mod

Do not treat the template as finished once copied.

Your `AGENTS.md` should grow with your project. Add rules when the agent repeats a mistake. Add skills when a workflow becomes common.

Good project instructions are specific. A small mod might only need a simple setup. A large mod should document its event format, naming rules, integration points, docs policy, asset rules, and git expectations.

## License

Use this template in any way you please for your own HOI4 modding workflow. 
