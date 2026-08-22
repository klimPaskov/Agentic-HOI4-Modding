# 3D tooling synchronization handoff

Status: complete for reusable starter tooling; live provider/Blender execution remains intentionally unrun.

## Scope and source

- Source of truth inspected: the current dirty working tree under
  `../chaos_redux/.tools/3d_pipeline/`.
- Target ownership honored: only `.tools/3d_pipeline/**` and this handoff were
  edited.
- The target had no root `AGENTS.md`; no replacement project instructions were
  invented.
- The existing target bootstrap and app-owned credential route were retained
  as the architectural baseline. Chaos's project Meshy wrapper was not copied.

## Exact target files

Updated existing files:

- `.tools/3d_pipeline/bootstrap_3d_workflow.py`
- `.tools/3d_pipeline/adapter/hoi4_blender_mcp.py`
- `.tools/3d_pipeline/adapter/blender_worker.py`
- `.tools/3d_pipeline/adapter/pyproject.toml`
- `.tools/3d_pipeline/config/asset_profiles.json`
- `.tools/3d_pipeline/config/dependencies.lock.json`
- `.tools/3d_pipeline/config/meshy_tool_contract.json`

Added reusable source, contracts, documentation, and tests:

- `.tools/3d_pipeline/README.md`
- `.tools/3d_pipeline/blender_client.py`
- `.tools/3d_pipeline/init_pilot_jobs.py`
- `.tools/3d_pipeline/meshy_client.py`
- `.tools/3d_pipeline/pack_pdx_material.py`
- `.tools/3d_pipeline/run_pilot.py`
- `.tools/3d_pipeline/verify_environment.py`
- `.tools/3d_pipeline/lib/__init__.py`
- `.tools/3d_pipeline/lib/mcp_stdio.py`
- `.tools/3d_pipeline/lib/paths.py`
- `.tools/3d_pipeline/config/meshy_tool_schema.lock.json`
- `.tools/3d_pipeline/tests/test_rigid_weapon_attachment_tool.py`
- `.tools/3d_pipeline/tests/blender_rigid_weapon_attachment_integration.py`

`adapter/uv.lock` was refreshed locally from `adapter/pyproject.toml` to verify
the dependency graph, but the target deliberately ignores that generated lock
and the bootstrap rematerializes it on demand before `uv sync --locked`.

## Behavior synchronized

- Meshy 7 is mandatory in the checked-in contract, locked schema, client, job
  runner, bootstrap-generated policy, environment verifier, and docs. The
  image call rejects any value other than explicit `ai_model="meshy-7"`.
- Meshy calls resolve only the reviewed external HOI4 Mod Setup executable from
  `.codex/config.toml` and invoke it with only
  `--run-verified-meshy-mcp`. No project Meshy wrapper or direct REST fallback
  was introduced.
- The full evidence-recording Meshy client and MCP stdio cleanup/error handling
  were ported, including task recovery, balance gates, immediate downloads,
  request/response/credit lineage, and redaction.
- The Blender adapter is now version `1.4.0` and consistently exposes 25
  `hoi4_blender_*` tools. The bootstrap derives its worker-operation allowlist
  directly from these function identifiers.
- The expanded worker includes bounded static transform baking, static stream
  partitioning, action import/retiming/grounding, humanoid and creature routes,
  component review/isolation, runtime sanitization, and rigid checkpoint weapon
  attachment with retention evidence.
- All copied `chaosx`, `CHAOS_REDUX`, Chaos path, package, environment,
  Blender-property, MCP tool, and worker identifiers were generalized to
  `hoi4`/`HOI4` names.
- Job paths derive from the target repository as
  `docs/assets/<owner_id>/models_3d/<asset_slug>`. Job registries must be passed
  explicitly with `--jobs-config`; no Chaos pilot registry is embedded.
- The winged-biped profile was added. The generic creature profile retained a
  job-supplied runtime scale rather than Chaos's rat-specific scale.
- The README records the Meshy 7 recovery gate, app-owned credential boundary,
  deterministic job layout, animation/weapon rules, HOI4 material/scale/export
  gates, and parent-owned runtime boundary.

## Deliberate exclusions

Not copied or created:

- Chaos `config/pilot_jobs.json`, job overrides, asset slugs, runtime staging,
  provider requests/responses/tasks/downloads, or pilot evidence.
- Generated `config/runtime.json`, generated adapter config, environment
  reports, clone logs, or live dependency resolution records.
- Chaos project Meshy `.cmd`/`.ps1` wrappers.
- `vendor/blender_mcp`, the io_pdx archive, `node_modules`, `.venv`, `.tmp`,
  `__pycache__`, compiled bytecode, or any other vendored/cache tree.
- Gameplay, GFX, entity, sound-definition, localisation, `.agents`, `.codex`,
  root, or Chaos repository edits.

Ignored bootstrap/runtime folders already present in the shared target
workspace were not added or treated as source changes.

## Validation

Passed on Python 3.13 with bytecode writes disabled:

- In-memory compilation of 14 non-vendored Python sources.
- `python -m unittest discover -s .tools/3d_pipeline/tests -p "test_*.py"`:
  4 tests passed.
- `python .tools/3d_pipeline/verify_environment.py`: passed with no findings;
  confirmed Meshy 7 contracts and all 25 generic adapter identifiers.
- PowerShell JSON parsing for `asset_profiles.json`,
  `meshy_tool_contract.json`, `meshy_tool_schema.lock.json`, and
  `dependencies.lock.json`.
- `uv lock --check --directory .tools/3d_pipeline/adapter`: passed with 41
  resolved packages and the generic `hoi4-blender-adapter 1.4.0` package.
- Repository search found no remaining Chaos namespace, Chaos absolute path,
  Meshy 6, or project Meshy-wrapper reference in reusable checked-in sources.

## Remaining risks and next live gates

- No paid Meshy call, live balance call, or live `tools/list` probe was made.
  Before provider work, bootstrap through installed HOI4 Mod Setup and run
  `verify_environment.py --probe-meshy`; require the live image schema to expose
  `meshy-7` and verify process-tree cleanup.
- The Blender integration test was not run because it requires the
  lock-selected Blender executable and installed io_pdx_mesh. Run
  `tests/blender_rigid_weapon_attachment_integration.py` through that exact
  Blender after bootstrap.
- `run_pilot.py` retains broad recovery capabilities from Chaos. Feature jobs
  still need an accepted job registry, exact vanilla references, explicit
  action-source policy, credit limits, counter/audio handoffs, and review
  before any provider work.
- `dependencies.lock.json` is starter policy until bootstrap replaces it with
  observed versions, checksums, bridge evidence, generated adapter config, and
  operation hashes.
- Final `.mesh`/`.anim` correctness, runtime copies, consumers, and in-game
  evidence remain parent-owned and cannot be inferred from these source tests.
