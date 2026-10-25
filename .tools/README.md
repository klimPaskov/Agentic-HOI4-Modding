# Repository tools

This directory contains maintained tooling that supports multiple HOI4 implementation surfaces, protects a shared contract, or provides a required runtime adapter, bootstrap, or synchronizer.
It is not storage for generated output, temporary experiments, editor state, Python bytecode, logs, provider artifacts, or copied dependencies that can be resolved from a verified lock.

## Retention rules

Keep a tool here when it validates or generates shared source-of-truth artifacts, enforces a repository-wide contract, or is a maintained runtime entry point used by the reusable workflow.
Move or remove one-time migrations, superseded generators, feature-local evidence, temporary reports, caches, and unreferenced presets.
Before retiring a tool, search its filename, module name, generated headers, and output signatures across project instructions, skills, agent definitions, docs, configuration, runtime source, and Git history. Preserve uncertain or recently active tooling until its owner and replacement are clear.

## Supported tools

### Repository checks

`check.py` is the single read-only entry point for mechanical questions about a mod: run `python -B .tools/check.py quick` on the files you changed before review and `python -B .tools/check.py full` at the end of a large task. `quick` takes the changed paths from Git (or `--paths`), runs only the checks those paths can affect and reports only findings in them; `full` runs every check over the whole repository. Both print errors as `path:line: level RULE message` and one summary line per check, and `--json <file>` writes every finding, including review candidates. Exit status: 0 no errors, 1 errors, 2 a check could not run.

First run on a machine:

```powershell
python -m pip install -r .tools/requirements.txt          # Pillow, numpy, scipy, openpyxl
python -B .tools/check.py doctor                          # what is still missing, and the fix for each item
python -B .tools/check.py doctor --save-game-dir "<game folder>"   # only if the game was not found
python -B .tools/quality.py --adopt                       # once, if the mod already had its own Python tools
```

HOI4 Mod Setup performs these steps when it installs the package. `doctor` exits 0 when everything a `full` run needs is present. Optional items (`uv` for the `quality` check, the HOI4 Agent Tools server for `script-validate`, the `.gitignore` entries) only cause their own check to be skipped with a notice. The game folder comes from `HOI4_GAME_DIR`, the machine-local `.tools/local_settings.json` (never committed), or the Steam libraries on the machine, in that order. `--adopt` records the findings of Python files that have no quality-baseline entries yet, so a mod's pre-existing tools start from a passing run. Files already in the baseline stay ratcheted, and new code must meet the limits instead of being adopted.

Every check follows `lib/report.py`: an `error` is an exact rule and fails the run, a `warning` is a heuristic that is printed but never fails, and a `review` item is a candidate list for a person. Each tool also runs alone with `--paths`, `--paths-from`, `--fail-on` and `--json`.

| Check | Tool | Question it answers | Needs the game |
| --- | --- | --- | --- |
| `localisation` | `audits/audit_localisation_static.py` | Are localisation files encoded, parsed and unique, and does every key the engine or script reads exist here or in vanilla? `--calibrate` measures each implicit-key rule on vanilla. | yes |
| `asset-wiring` | `audits/audit_asset_wiring_static.py` | Does every `GFX_` name, texture, mesh and implicit engine lookup (idea, decision, focus shine, flag, achievement art) resolve? Unreferenced sprites are review items. | yes |
| `script-rules` | `audits/audit_script_rules.py` | Does script use `<=` or `>=`, unary minus on a variable token, or `§`/`£` written into scripted localisation? Lexical only; fixtures in `tests/fixtures/script_rules/`. | no |
| `gfx` | `gfx/gfx.py audit` | Frame-strip widths, the flag size ladder and TGA origin, achievement art size, LFS pointers and truncated runtime binaries, profiled icon families and report-image provenance (`gfx/README.md`). | for vanilla textures |
| `guidance` | `sync/check_guidance_size.py` | Are instructions, skills and agent prompts within the single-read ceiling? | no |
| `generators` | `sync/sync_*.py --check` | Do `AGENTS.md`, the generated agents and the skill copies match their canonical sources? | no |
| `tests` | `unittest` over `tests/`, `gfx/` and skill `tools/tests/` folders | Do the maintained tests pass? | no |
| `quality` | `quality.py` | Ruff defect rules, the complexity ratchet in `quality_baseline.json` and `mypy --strict` for the strict tooling files; skipped with a notice without `uv`. | no |
| `script-validate` | `audits/validate_scripts_mcp.py` | Does `hoi4.script_validate` accept each changed script file? Quick only; skipped with a notice when the HOI4 Agent Tools server cannot start. Unresolved commands are warnings and unchecked argument blocks review items, never passes. | no |

Tools that read vanilla files take the game folder from `HOI4_GAME_DIR` and fall back to the default Steam path (`lib/game.py`); without the game they exit 2 and name the variable. `lib/` holds the one shared implementation of the finding contract, the script and localisation readers, the game-folder lookup, the `doctor` report and the MCP client; tools import it instead of copying it.

A passing check proves only the properties it checks: a size or alpha check does not establish visual quality, and a reference check does not establish gameplay behaviour. Never weaken a check, add a suppression, lower a threshold or edit a baseline to make validation pass. `quality.py --write-baseline` records the first baseline or improvements only and refuses while errors remain.

`lib/`, `audits/audit_script_rules.py`, `audits/validate_scripts_mcp.py`, `gfx/gfx.py` with its tests, the asset tools in `hoi4-feature-assets/tools/` and `save_inspect.py` are byte-identical copies of upstream tools, listed in the source package's `scripts/shared_tools.json`; repository values live in their settings files (`gfx/settings.json`, `gfx/profiles.json`, the asset tools' `project_settings.json`), which are not shared. `check.py`, `quality.py` and the localisation and asset-wiring audits are this package's own editions.

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
