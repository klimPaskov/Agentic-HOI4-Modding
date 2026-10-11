# Repository tools

This directory contains maintained tooling that supports multiple HOI4 implementation surfaces, protects a shared contract, or provides a required runtime adapter, bootstrap, or synchronizer.
It is not storage for generated output, temporary experiments, editor state, Python bytecode, logs, provider artifacts, or copied dependencies that can be resolved from a verified lock.

## Retention rules

Keep a tool here when it validates or generates shared source-of-truth artifacts, enforces a repository-wide contract, or is a maintained runtime entry point used by the reusable workflow.
Move or remove one-time migrations, superseded generators, feature-local evidence, temporary reports, caches, and unreferenced presets.
Before retiring a tool, search its filename, module name, generated headers, and output signatures across project instructions, skills, agent definitions, docs, configuration, runtime source, and Git history. Preserve uncertain or recently active tooling until its owner and replacement are clear.

## Supported tools

### ChatGPT source packaging

`package_chatgpt_project_sources.py` builds a curated flat source folder with
`all-project-sources.zip` and, when agents exist, `subagents.zip`. The installed
project root is discovered from the script location, independently of the
working directory. Python 3.10 or newer is required; no extra packages or
credentials are used. Windows users can double-click
`package_chatgpt_project_sources.bat`, which opens the completed folder.

```sh
python .tools/package_chatgpt_project_sources.py --dry-run
python .tools/package_chatgpt_project_sources.py
python .tools/package_chatgpt_project_sources.py --output /path/outside/mod/new-bundle
python .tools/package_chatgpt_project_sources.py --include 'AGENTS.md' --include 'events/**/*.txt' --exclude 'events/private/**'
```

Defaults include instructions, README, descriptors, canonical skills/subagents,
Markdown/CSV documentation, and HOI4 common, events, history, localisation,
interface, and map text. Missing optional directories are allowed. Nested paths
are encoded into flat filenames (`/` becomes `%2F`, `%` becomes `%25`), avoiding
ambiguous basename collisions. `--include` replaces the include defaults;
`--exclude` adds exclusions. `--config` accepts a JSON object with `include` and
`exclude` arrays of project-relative slash-separated globs. `*` matches one
path segment; `**` matches zero or more. Matching is case-insensitive.

Default exclusions always apply to secret-shaped filenames, .env files, Git,
virtual environments, dependency folders, logs, backups, and old flattened
exports. Links and junction directories are not followed; selected linked
files, binary/non-UTF-8 sources, files over 8 MiB, bundles over 128 MiB or
10,000 files, and destination collisions are rejected. Review the dry run and
file contents before sharing: filename filtering cannot identify every secret.

Output defaults to Downloads/<project-folder>-chatgpt-project-sources, must be
outside the project, and must not exist. Choose a new `--output` for another
export. The verified archives and loose files are staged together before the
folder is published; failure removes staging and leaves project files intact.
The tool performs no upload and does not launch a conversation. It is installed
by the all-platform `runtime.agent_sync` shared-tools manifest component,
included by both core profiles and every coding-environment dependency closure. Modified installed
tools retain normal manifest conflict review.

### HOI4 Agent Tools bootstrap

`mcp/bootstrap_hoi4_agent_tools.py` installs and verifies the manifest-pinned HOI4 Agent Tools package and advertised MCP routes.
Its package version, integrity, runtime-entry evidence, manifest declaration, and documentation must move together.

### Runtime synchronization

Claude Code files are canonical. The tools under `sync/` regenerate `AGENTS.md` from `CLAUDE.md`, the Codex, Cursor, Qoder, and OpenCode agents from `.claude/agents/`, and the `.agents/skills/` and `.qoder/skills/` copies from `.claude/skills/`. `check_guidance_size.py` keeps instruction files, skills, and agent prompts within the single-read ceiling. Run them after a canonical change and again with `--check`:

```powershell
python -B .tools/sync/sync_instructions.py
python -B .tools/sync/sync_agents.py
python -B .tools/sync/sync_skills.py
python -B .tools/sync/check_guidance_size.py
```

Generated files are tracked so a checkout works immediately. Never hand-edit them or copy project-specific MCP paths between runtimes. `sync/README.md` documents each tool and its configuration file, and `docs/runtimes.md` documents what every runtime reads, including DeepSeek Harness, which has no agent registry.

### HOI4 Live Tools

HOI4 Live Tools is a separate, optional MCP server that drives a running game. `mcp/bootstrap_hoi4_live_tools.py` installs the release pinned in it (version, URL, SHA-256, size) for the current user and registers it in the user-level configuration of the coding clients found; it is the `mcp.hoi4_live.bootstrap` manifest component and `scripts/test_live_bootstrap_contract.py` keeps it equal to the manifest. `.claude/skills/hoi4-live-playtest/references/setup.md` documents setup and troubleshooting, and the optional `hoi4-live-playtest` skill explains how agents use it.

### 3D model pipeline

`3d_pipeline/` contains the reusable Meshy, Blender, `io_pdx_mesh`, material, verification, and adapter infrastructure.
Follow `3d_pipeline/README.md` and `hoi4-3d-model-pipeline` for dependency gates, job containment, provider evidence, test commands, and runtime ownership boundaries.
Do not commit secrets, provider outputs, job artifacts, virtual environments, vendor caches, generated environment reports, or transient process state.

### Offline Paradox wiki snapshot

`wiki/sync_wiki_snapshot.py` regenerates `paradox_wiki/` from the live Hearts of Iron IV wiki, and `wiki/verify_wiki_snapshot.py` is the read-only acceptance check for the result.
The snapshot ships as the `wiki.snapshot` manifest component and is named by the project instructions as the required modding reference, so both commands run as a pair whenever the wiki moves:

```powershell
python -B .tools/wiki/sync_wiki_snapshot.py
python -B .tools/wiki/verify_wiki_snapshot.py
```

After a refresh, regenerate `hoi4-mod-setup.manifest.json` with `scripts/generate_manifest_evidence.py --revision <new commit>` so `wiki.snapshot` pins the refreshed hashes.
Contract, options, and the page set are in `wiki/README.md`.

## Generated and local-only data

Run Python tools with `python -B` when practical.
Track a generated report only when a maintained consumer or durable handoff requires it and its provenance remains current.
Feature-local receipts and implementation handoffs belong under the matching `docs/plans/<feature_slug>/` hierarchy, not in `.tools`.

## Adding or removing a tool

When adding a tool, confirm that an existing tool or skill-local utility does not already cover the need, give it a narrow command-line contract and safe defaults, add a read-only check or dry-run when practical, document inputs and outputs, and keep caches out of Git.
When removing a tool, verify direct references, imports, generated headers, docs, skills, agents, configuration, and historical handoffs, then update the authoritative replacement in the same change.
