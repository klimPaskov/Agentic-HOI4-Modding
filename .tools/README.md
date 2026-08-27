# Repository tools

This directory contains maintained tooling that supports multiple HOI4 implementation surfaces, protects a shared contract, or provides a required runtime adapter, bootstrap, or synchronizer.
It is not storage for generated output, temporary experiments, editor state, Python bytecode, logs, provider artifacts, or copied dependencies that can be resolved from a verified lock.

## Retention rules

Keep a tool here when it validates or generates shared source-of-truth artifacts, enforces a repository-wide contract, or is a maintained runtime entry point used by the reusable workflow.
Move or remove one-time migrations, superseded generators, feature-local evidence, temporary reports, caches, and unreferenced presets.
Before retiring a tool, search its filename, module name, generated headers, and output signatures across project instructions, skills, agent definitions, docs, configuration, runtime source, and Git history.

## Supported tools

### HOI4 Agent Tools bootstrap

`mcp/bootstrap_hoi4_agent_tools.py` installs and verifies the manifest-pinned HOI4 Agent Tools package and advertised MCP routes.
Its package version, integrity, runtime-entry evidence, manifest declaration, and documentation must move together.

### Agent synchronization

The scripts under `sync/` generate Qoder, Cursor, OpenCode, and Claude Code subagents from canonical `.codex/agents/*.toml` definitions.
Run all four after a canonical definition changes, then rerun them with `--check`:

```powershell
python -B .tools/sync/sync_qoder_agents.py
python -B .tools/sync/sync_cursor_agents.py
python -B .tools/sync/sync_opencode_agents.py
python -B .tools/sync/sync_claude_agents.py
python -B .tools/sync/sync_qoder_agents.py --check
python -B .tools/sync/sync_cursor_agents.py --check
python -B .tools/sync/sync_opencode_agents.py --check
python -B .tools/sync/sync_claude_agents.py --check
```

Qoder, Cursor, and OpenCode generated directories are ignored and machine-local. Claude Code project agents are generated but tracked for immediate project discovery.
Never hand-edit generated agent files or copy project-specific MCP paths between runtimes.

### 3D model pipeline

`3d_pipeline/` contains the reusable Meshy, Blender, `io_pdx_mesh`, material, verification, and adapter infrastructure.
Follow `3d_pipeline/README.md` and `hoi4-3d-model-pipeline` for dependency gates, job containment, provider evidence, test commands, and runtime ownership boundaries.
Do not commit secrets, provider outputs, job artifacts, virtual environments, vendor caches, generated environment reports, or transient process state.

## Generated and local-only data

Run Python tools with `python -B` when practical.
Track a generated report only when a maintained consumer or durable handoff requires it and its provenance remains current.
Feature-local receipts and implementation handoffs belong under the matching `docs/plans/<feature_slug>/` hierarchy, not in `.tools`.

## Adding or removing a tool

When adding a tool, confirm that an existing tool or skill-local utility does not already cover the need, give it a narrow command-line contract and safe defaults, add a read-only check or dry-run when practical, document inputs and outputs, and keep caches out of Git.
When removing a tool, verify direct references, imports, generated headers, docs, skills, agents, configuration, and historical handoffs, then update the authoritative replacement in the same change.
