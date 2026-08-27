# Alternate-runtime workflow synchronization

## Result

The general workflow now treats `.codex/agents/*.toml` as the only subagent authoring source and can generate Qoder, Cursor, and OpenCode definitions from one shared authority map.
The runtime projections are generic, ignored, and machine-local; no Chaos Redux identifier, absolute path, environment variable, MCP registration, generated repo wiki, package cache, or provider sidecar was copied.

## Files

- `.tools/sync/agent_sync_common.py`
- `.tools/sync/sync_qoder_agents.py`
- `.tools/sync/sync_cursor_agents.py`
- `.tools/sync/sync_opencode_agents.py`
- `.tools/sync/README.md`
- `.tools/README.md`
- `.tools/.gitignore`
- `scripts/test_agent_sync_contract.py`
- `.gitignore`
- `AGENTS_template.md`
- `AGENTS_chaos_redux.md`
- `README.md`

## Contract

The shared renderer requires an authority entry for every canonical TOML and rejects orphaned authority entries.
It performs only mechanical runtime substitutions, converts canonical snake-case names to hyphen-case names, writes runtime-native frontmatter, reports stale files without deleting them, and supports a read-only `--check` mode.
The prompt body remains the authoritative ownership boundary when an alternate runtime cannot express an equivalent tool allowlist.

## Exclusions

State-ledger workflow material was excluded.
Chaos Redux `.qoder/repowiki`, generated runtime folders, absolute MCP configuration, `.opencode/node_modules`, ImageGen sidecars, event-specific validators, formable-state generators, catalog exporters, source-packaging scripts, and user-owned dirty assets were not copied.

## Validation

- Generated and checked 23 agents in each of Qoder, Cursor, and OpenCode.
- `scripts/test_agent_sync_contract.py` checks 23 canonical authority mappings, three runtime renderers, required frontmatter, and runtime-neutral prompt substitutions.
- Published manifest evidence remains pinned to its exact committed revision and was not falsified with uncommitted hashes.

## Publication follow-up

The synchronizers are repository-maintainer tools until a release commit intentionally adds them to the setup manifest.
If they become an installable optional component, add the component and profile only in the final release commit, regenerate evidence from that exact 40-character revision, and rerun `scripts/validate_published_manifests.py`.
