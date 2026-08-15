# Agentic HOI4 Modding

[![Discord](https://img.shields.io/badge/Discord-Join%20Community-7289da?logo=discord&logoColor=white)](https://discord.gg/rAXesGcT2t)

A reusable source package for preparing Hearts of Iron IV mod repositories for
agentic development. Its project instructions, references, skills, tools,
optional workflows, and helper-agent profiles can be adapted to a new or
existing mod.

Watch the video tutorials: https://www.youtube.com/playlist?list=PLh6JmuEabQioc4V8IYGEsMtqiw-xemeX3

## What this repo provides

- Adaptable project instructions, together with a full real-project example.
- An offline Paradox wiki snapshot and supporting technical documentation.
- Reusable skills, tools, examples, and optional workflow packages for common
  and specialized HOI4 modding work.
- A growing collection of bounded helper-agent profiles for research,
  production, implementation support, review, validation, and documentation.
  The authoritative set is the `.codex/agents/` directory rather than a list in
  this README.
- A source manifest used by the setup application to select, verify, and adapt
  these components for a specific mod.

## Complete package download

[Download the complete Agentic HOI4 Modding package](https://github.com/klimPaskov/Agentic-HOI4-Modding/releases/latest/download/Agentic-HOI4-Modding.zip).
The ZIP is a clean snapshot of the version-controlled source package without
Git history or machine-local files.

## Recommended setup

The recommended way to use this repository is
[HOI4 Mod Setup](https://github.com/klimPaskov/HOI4-Mod-Setup). The desktop
wizard can create a new mod or prepare an existing one, discover and adapt the
project identity, install the selected instructions, skills, helper agents,
tools, and offline references, configure optional workflows, preview every
change before applying it, and later update or repair the managed setup. This
keeps project-specific names and paths consistent and avoids manually copying
an evolving set of files.

[Download the latest HOI4 Mod Setup release](https://github.com/klimPaskov/HOI4-Mod-Setup/releases/latest),
then choose whether to create a new mod or import an existing one. The manual
steps below remain useful when you deliberately do not want to use the setup
application.

## Manual setup

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
2. Remove only genuinely optional sections for skills, subagents, reference mods, or workflows this project does not use. Keep the HOI4 MCP setup and mandatory in-scope routing rules.
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

Custom Codex subagents are useful when a task can be split into bounded helper
work. This repository includes profiles across several broad kinds of work,
including discovery, research, planning, implementation support, visual and
audio production, audits, validation, and documentation. The collection evolves
with the workflows, so inspect `.codex/agents/` for the current set instead of
relying on a static list here.

Put subagent TOML files under:

```text
.codex/agents/
```

The main agent should still own final implementation, final wiring, final review, final validation, and the completion report. Spawn every project custom subagent without inherited conversation context and pass every required path, constraint, correction, accepted decision, ownership boundary, and handoff destination explicitly in its prompt.

## Optional Super Events workflow

HOI4 Mod Setup leaves Super Events out by default. Selecting the workflow
installs the `hoi4-super-events` skill plus the reusable runtime under
`interface/`, `common/`, `events/`, `localisation/`, `gfx/`, and
`docs/super_events/`.

The installer adapts all scripted identifiers and runtime filenames to the
confirmed mod prefix. The upstream `hoi4ms_*` names are source-package names;
installed files use the project's actual `<mod_prefix>_*` names.
The package includes one hidden console-test event, a default image and
background, the response button texture, and both full-composition and
`457x328` image Photoshop templates. New registrations add one stable integer
ID and matching image, title, description, quote, response, caller, unique rights-verified Internet-sourced audio, and documentation. Audio is never synthesized, generated, recorded, or manually authored by an agent.

## Portrait workflow

The portrait workflow separates grounded-source research, fictional generation,
provider-assisted styling, asset processing, wiring, provenance, and validation.
It supports selectable Comfy Cloud, Local ComfyUI, and RunPod routes while
keeping provider operation and approval boundaries explicit.

### 7. Keep asset ownership clear

Asset helpers should produce source files, processed PNG previews, DDS files,
manifests, contact sheets when useful, and a clear handoff. Portrait work follows
the dedicated portrait workflow and its ownership rules.

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

## MCP in agent workflows

HOI4 Agent Tools is an MCP server for coding agents. It helps agents inspect, lint, render, create, and rewrite focus trees; inspect and rewrite scripted GUIs; inspect and edit connected map data; trace, compare, render, and lint event chains; analyze AI weights, MTTH, random outcomes, and declared weighted systems under explicit scenarios; and inspect, render, and compare technology and doctrine trees through `hoi4.tech_inspect`, `hoi4.tech_render`, and `hoi4.tech_compare`. It is one tool in the existing skills and source workflow.

`AGENTS_template.md` includes instructions for the coding agent to install and register the required server, so users do not need to install it manually. For reference, the published package command is:

```powershell
npm install --global hoi4-agent-tools@latest
```

A Codex server entry looks like this:

```toml
[mcp_servers.hoi4_agent_tools]
command = "hoi4-agent-tools.cmd"
cwd = "C:\\Users\\<you>\\OneDrive\\Documents\\Paradox Interactive\\Hearts of Iron IV\\mod\\<your_mod>"
```

Agents must use MCP for every in-scope focus tree, event chain, technology or doctrine tree, weighted-logic system, scripted GUI, and map surface that HOI4 Agent Tools supports. Source review remains required but is not a substitute for the corresponding MCP inspection, render, lint, evaluation, comparison, or post-change validation. If a required route is unavailable, the agent records the exact blocker instead of silently downgrading to source-only review. The owning skills still define design, research, source review, assets, tests, audits, and handoffs. Large MCP artifacts are returned as linked resources instead of placed in the prompt.

See `docs/systems/hoi4_agent_tools_mcp_integration.md` for the capability matrix, artifact and source-authority rules, probability scenario contract, rewrite and recovery lifecycle, and local or HTTP troubleshooting guidance.

## Autonomous 3D model workflow

The reusable 3D workflow lives in .agents/skills/hoi4-3d-model-pipeline/SKILL.md and .codex/agents/hoi4_3d_model_pipeline.toml.

This workflow is optional at the project level. Mods that do not add new 3D models, entities, unit actions, or skeletal animations do not install or enable the 3D routes. Once a feature requires the workflow, its declared Meshy and Blender MCP routes and evidence gates are mandatory.

The workflow stops before any path discovery, brief read, reference generation, balance check, or provider call unless the process environment already exposes a nonblank MESHY_API_KEY.

If the key is missing, the agent must show this PowerShell command and then require a shell or Codex restart:

    [Environment]::SetEnvironmentVariable(
        "MESHY_API_KEY",
        "msy_your_actual_key_here",
        "User"
    )

When a feature needs 3D work, the agent runs `.tools/3d_pipeline/bootstrap_3d_workflow.py` after the key gate. The bootstrap resolves and records the latest supported Meshy, Blender Lab, Blender build, repository-owned allowlisted HOI4 adapter, and io_pdx_mesh dependencies, verifies the Blender bridge separately from the process, writes the concrete production and development MCP entries into `.codex/config.toml`, and records versions and checksums in the generated lock.

Unattended production uses the narrow repository-owned HOI4 Blender adapter. The unrestricted Blender Lab route remains disabled and development-only. The production adapter confines file access to the declared job and reference roots and exposes only the bounded health, candidate preparation, inspection, texture processing, mesh and animation export, locomotion authoring, reimport, and checkpoint operations required by the workflow.

When a brief has no ready reference, the workflow generates exactly one final Meshy-ready image for the asset and never sends side-profile sheets, turnaround boards, collages, or multi-view boards to Meshy.

Meshy 6 is the default image-to-3D generation model. The worker records the exact live model identifier and does not silently downgrade to an older model when Meshy 6 is unavailable.

Normal planned model generation, remesh/retexture, rigging, conversion, and required animation credit use is pre-authorized. The worker checks and records the live balance and consumed credits without asking for confirmation. It asks only before additional paid recovery caused by a failed or rejected operation; otherwise it must not ask for credit-spend confirmation.

Humanoid units are calibrated against a named installed vanilla source mesh and entity scale with source geometry height and effective runtime height recorded separately and the scale applied exactly once.

For custom units, the 3D worker also researches sound files on the Internet, preserves original downloads and source URLs, records licensing and usage terms, access dates, and checksums, and maps sound roles and synchronization points to animation actions or frames. Selection audio and its exact engine consumer are mandatory. Country or original-tag infantry voice templates must be audited across every consumer under that identity, and per-subunit selection is reported blocked when the engine surface cannot bind it independently. The worker may make only license-permitted mechanical edits and must never generate, synthesize, record, manually author, fabricate placeholder or test-tone audio, or use an unlicensed file.

Every custom unit also requires original counters for every runtime counter surface it uses. The counter artist must inspect the exact installed-vanilla definition and DDS plus the matching reference family, sample and match the vanilla green palette and frame behavior, and produce the final large and map-counter variants required by the consumer. Reused counters, arbitrary green, placeholders, and unreferenced imitations are incomplete.

The package retains provider lineage, immutable source downloads, Blender checkpoints, topology repair evidence, locally verified PDX material packing, processed textures, real mesh and skeletal animation exports, sourced-audio evidence for custom units, reimport proof, source-to-runtime hashes, and a parent-owned runtime handoff.

The parent agent owns entity, asset, GFX, gameplay, placement, live-consumer wiring, and in-game proof, so an export alone never counts as a completed feature.

Users provide only MESHY_API_KEY. The agent must not ask the user to copy, edit, or replace MCP configuration; if required setup for an in-scope 3D feature cannot finish, it must report the blocker and leave the 3D routes disabled.

## Optional super-event workflow

The reusable super-event workflow lives in `.agents/skills/hoi4-super-events/SKILL.md`.

It is optional because many mods do not use a custom super-event presentation system. When enabled, the skill first detects the current mod's event, scripted GUI, scripted localisation, sprite, sound, volume-setting, documentation, and naming patterns. It does not assume Chaos Redux slots, prefixes, helpers, paths, audio formats, subagents, spreadsheets, or catalogues.

Use it for major campaign moments that need aligned trigger wiring, title and body text, reaction text, a sourced quote, final image and audio assets, settings-aware playback, provenance, cleanup, and validation. General event logic remains owned by `hoi4-events`; visual production remains owned by `hoi4-feature-assets`; quote and audio source research remains owned by `hoi4-text-audio-research`.

## Subagent design rules

Subagents should be narrow.

A good subagent has:

- a clear task type
- clear allowed files
- clear forbidden files
- a clear handoff output
- no hidden ownership of final implementation

Use subagents before completion claims, not after claiming the work is done. A subagent report is evidence, not final proof. The main agent must inspect it and fix the issues.

Specialized helper profiles may impose additional evidence and ownership gates.
Follow the selected profile and owning skill rather than treating the generic
rules here as a replacement for them.

## Completion proof

A goal should not be marked complete unless the implementation is actually complete.

For large events, mechanics, focus trees, country packages, UI work, balance
passes, and asset goals, require a concrete completion report. It should list
files changed, systems touched, meaningful scenarios or comparisons, assets
created or reused, docs updated, audits performed, and blockers.

Every simplification should be reported. If no simplifications were made, the agent should say so and provide evidence.

## Customizing this repo for your mod

Do not treat the template as finished once copied.

Your `AGENTS.md` should grow with your project. Add rules when the agent repeats a mistake. Add skills when a workflow becomes common. Add subagents only when the helper role is clear enough to stay bounded.

Good project instructions are specific. A small mod might only need a simple setup. A large mod should document its event format, naming rules, integration points, docs policy, asset rules, subagent routing, completion proof, and git expectations.

## License

Use this template in any way you please for your own HOI4 modding workflow.
