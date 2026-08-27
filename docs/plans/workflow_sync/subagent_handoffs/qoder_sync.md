# Qoder synchronization handoff

> Historical handoff, superseded on 2026-08-27 by the shared Qoder, Cursor, and OpenCode synchronizer under `.tools/sync/`. Canonical `.codex/agents/*.toml` files remain authoritative, generated alternate-runtime folders are now ignored and machine-local, and the current commands and validation contract live in `.tools/sync/README.md`. The deleted root `.tools/sync_qoder_agents.py`, tracked generated Qoder files, and optional manifest components described below are not current implementation requirements.

## Scope and result

Added a reusable, one-way Codex-to-Qoder agent workflow to the general HOI4
starter. `.codex/agents/*.toml` remains the canonical source. The generator
derives Qoder-compatible hyphenated names, descriptions, prompt bodies, tool
authority, and a mapping README without modifying `.codex`.

The authority table explicitly covers all 23 canonical target agents,
including the general audio and quote researchers and the three selected-only
Super Event research roles. An unclassified new or removed canonical agent is
an error, preventing silent generation without an authority contract.

## Files changed

- `.tools/sync_qoder_agents.py`
- `.qoder/mcp.json`
- `.qoder/agents/README.md`
- `.qoder/agents/hoi4-3d-model-pipeline.md`
- `.qoder/agents/hoi4-ai-probability-auditor.md`
- `.qoder/agents/hoi4-asset-source-researcher.md`
- `.qoder/agents/hoi4-audio-researcher.md`
- `.qoder/agents/hoi4-country-package-auditor.md`
- `.qoder/agents/hoi4-decision-mission-auditor.md`
- `.qoder/agents/hoi4-documentation-curator.md`
- `.qoder/agents/hoi4-event-ui-worker.md`
- `.qoder/agents/hoi4-feature-completion-auditor.md`
- `.qoder/agents/hoi4-focus-tree-auditor.md`
- `.qoder/agents/hoi4-generated-feature-art.md`
- `.qoder/agents/hoi4-icon-artist.md`
- `.qoder/agents/hoi4-improvement-loop-planner.md`
- `.qoder/agents/hoi4-localisation-auditor.md`
- `.qoder/agents/hoi4-portrait-creator.md`
- `.qoder/agents/hoi4-quote-remark-researcher.md`
- `.qoder/agents/hoi4-repo-explorer.md`
- `.qoder/agents/hoi4-scripted-system-architect.md`
- `.qoder/agents/hoi4-skill-maintainer.md`
- `.qoder/agents/hoi4-spreadsheet-doc-worker.md`
- `.qoder/agents/hoi4-super-event-art-researcher.md`
- `.qoder/agents/hoi4-super-event-audio-researcher.md`
- `.qoder/agents/hoi4-super-event-quote-researcher.md`
- this handoff

## Behavior and portability decisions

- `python .tools/sync_qoder_agents.py` creates or updates generated Markdown
  idempotently. It warns about stale Markdown but does not delete it.
- `python .tools/sync_qoder_agents.py --check` performs a read-only drift check
  and exits nonzero for missing, outdated, or stale generated Markdown.
- Canonical snake-case `hoi4_*` names become Qoder hyphen-case names.
- Codex-only TOML fields are intentionally omitted because Qoder has no direct
  equivalents. Qoder tools are derived from the `hoi4-subagents` authority
  model; the generated body remains the authoritative scope contract.
- Mechanical prompt substitutions translate inherited-context wording,
  Agent-Nudger wording, and the Codex-specific ImageGen phrase into
  runtime-neutral language.
- `.qoder/mcp.json` contains only the portable PATH-resolved
  `hoi4-agent-tools.cmd` server. Meshy and Blender routes were excluded because
  the starter deliberately defers concrete 3D bootstrap and job-root setup;
  copying Chaos Redux paths or environment variable names would be unsafe.

## Explicit exclusions

- Did not modify the source repository.
- Did not copy `.qoder/repowiki`; it is generated, Chaos-specific content.
- Did not modify canonical `.codex` definitions, `.agents`, root documentation,
  templates, manifests, gameplay, or other `.tools` files.
- Did not copy Chaos-specific MCP wrapper paths, asset job roots, or environment
  variables.
- Preserved unrelated concurrent changes under `.tools/3d_pipeline/`.

## Validation

- `python .tools/sync_qoder_agents.py` — final idempotence run reported 0
  created, 0 updated, and 24 unchanged generated files (23 agents plus README).
- `python .tools/sync_qoder_agents.py --check` — passed for the final target
  state.
- Imported the generator and asserted 23 authority entries, 24 rendered files,
  a generated file for every canonical mapping, and a tools field on every
  agent output.
- Parsed `.qoder/mcp.json` with PowerShell `ConvertFrom-Json` and confirmed the
  HOI4 Agent Tools command is present.
- Searched generated output for `chaosx`, `chaos-redux`, `chaos_redux`, raw
  `fork_context=false`, untranslated `Agent Nudger writes`, and the
  Codex-specific ImageGen phrase; none remained.

## Remaining integration note

The main integrator should rerun `python .tools/sync_qoder_agents.py` after any
concurrent `.codex/agents/*.toml` edit and commit the regenerated Qoder output.
When a project activates the deferred 3D workflow, its repository bootstrap
must add concrete Qoder Meshy/Blender MCP entries separately; this generic MCP
file intentionally does not guess those paths.
