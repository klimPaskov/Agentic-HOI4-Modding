# Reusable 3D pipeline sync handoff

> Historical August snapshot. See the [September 13 integrated sync](latest_workflow_sync_2026_09_13.md) and current 3D skill/tool contracts for active model, recovery, firearm, transport and export policies. Derived runtime checks remain job-scoped.

Date: 2026-08-27

## Scope and result

Statically audited the current Chaos Redux 3D pipeline against the generic starter pipeline and ported only high-confidence reusable code. No provider, balance, bootstrap, Blender, asset, audio, counter, or game operation ran. `MESHY_API_KEY` was confirmed non-blank before repository intake but was never read or exposed. Credits estimated/consumed: 0/0.

The target retains its app-owned verified Meshy launcher and generic adapter names. No Chaos job, asset ID, path, environment variable, generated lock, environment report, provider artifact, vendor tree, gameplay file, state-ledger material, or `.qoder` content was copied.

## Source mapping

- `248da4a58` (`lib/mcp_stdio.py`, lifecycle test): exact owned-process cleanup and observable lifecycle receipts.
- `a3e0a1497`, `1be22d5ae`, `8de5d5923` (`adapter/blender_worker.py`, `adapter/normalization_convergence.py`, preparation tests): pre-normalization scale-key sanitation and save/reopen normalization verification with bounded convergence guards.
- `5d3a17e0d`, `ed42391cc` (`adapter/blender_worker.py`, adapter wrapper, client, animation tests): pose-basis location scaling from source/target armature world scale, exact source-action selection, and verified external animation-source provenance.
- `cdd4103eb` (Chaos project Meshy wrappers): reviewed but deliberately not copied. Artifact repair/persistence belongs to the target's app-owned launcher. The target runner already performs atomic `.partial` replacement and checksum recording for accepted downloads.
- `ccc287e33`: used only as a consolidation reference; project-specific adapter/config/version identity was not copied.

## Files changed

- `.tools/3d_pipeline/lib/mcp_stdio.py`
- `.tools/3d_pipeline/adapter/normalization_convergence.py`
- `.tools/3d_pipeline/adapter/blender_worker.py`
- `.tools/3d_pipeline/adapter/hoi4_blender_mcp.py`
- `.tools/3d_pipeline/adapter/pyproject.toml` (generic version `1.5.0`)
- `.tools/3d_pipeline/blender_client.py`
- `.tools/3d_pipeline/run_pilot.py`
- `.tools/3d_pipeline/tests/test_workflow_sync_contracts.py`
- `.tools/3d_pipeline/README.md`
- this handoff

The shared humanoid continuation now requires explicit verified receipts for idle, move, attack, and death and no longer authors replacement locomotion. Animation import validates the immutable source checksum and JSON receipt, selects the exact source action and rigs, and records its coordinate formula. Preparation reopens the saved checkpoint and fails closed on scale persistence errors. Stdio calls can emit exact process ownership and survivor evidence.

## Validation

- `python -m unittest discover -s .tools/3d_pipeline/tests -p "test_*.py"` passed: 12 tests.
- `python -m py_compile` passed for every changed Python module and the new test module.
- `git diff --check -- .tools/3d_pipeline` passed; output contained only LF to CRLF conversion warnings.
- No Blender integration tests ran because this task explicitly prohibited adapter/bootstrap execution. No runtime or in-game completion is claimed.

## Follow-up status (2026-08-28)

The four reusable deltas identified as deferred in this handoff's 2026-08-27 audit are now ported. This status update preserves the original audit history and does not claim provider, Blender, live, runtime, or game execution. The follow-up provider-free test run reports 19 passing tests.

- Native BVH import and source-armature compatibility, previously deferred from `ed42391cc`/`8de5d5923`, are now ported in `.tools/3d_pipeline/adapter/blender_worker.py`, `.tools/3d_pipeline/adapter/hoi4_blender_mcp.py`, `.tools/3d_pipeline/blender_client.py`, and `.tools/3d_pipeline/tests/test_reusable_adapter_advances.py`.
- The guarded export-coordinate checkpoint, previously deferred from `ff985f3d2`, is now ported in `.tools/3d_pipeline/adapter/blender_worker.py`, `.tools/3d_pipeline/adapter/hoi4_blender_mcp.py`, `.tools/3d_pipeline/blender_client.py`, and `.tools/3d_pipeline/tests/test_reusable_adapter_advances.py`.
- Excluded-contact grounding plus configurable/nearest-face weight handling, previously deferred from `9f9bb2e58`, are now ported in `.tools/3d_pipeline/adapter/blender_worker.py`, `.tools/3d_pipeline/adapter/hoi4_blender_mcp.py`, `.tools/3d_pipeline/blender_client.py`, and `.tools/3d_pipeline/tests/test_reusable_adapter_advances.py`.
- Dual-source geometry selection/reset, previously deferred beyond saved normalization convergence from `a3e0a1497`, is now ported in `.tools/3d_pipeline/adapter/blender_worker.py`, `.tools/3d_pipeline/adapter/hoi4_blender_mcp.py`, `.tools/3d_pipeline/blender_client.py`, and `.tools/3d_pipeline/tests/test_reusable_adapter_advances.py`.

The current `.tools/3d_pipeline/README.md` and `.agents/skills/hoi4-3d-model-pipeline/SKILL.md` document these capabilities. The follow-up implementation files are the four paths named above; this reconciliation edits only this handoff and does not alter either documentation surface.

The original handoff's note that the skill was not edited for concurrent skill-maintenance work is retained as history. The current skill now documents the verified-action receipt fields, save/reopen normalization evidence, and lifecycle receipt language; no additional skill work is requested here.

## Remaining deferred reusable deltas

- Chaos wrapper artifact-persistence patches and tests from `cdd4103eb` remain intentionally blocked as non-portable until app-launcher ownership/version evidence is available. They must not be transplanted as project wrappers.
- Generated adapter config, dependency locks, and environment reports remain deferred and were not regenerated. Bootstrap remains the owner of those derived files.
- Legacy local action-authoring adapter operations still exist for bounded tooling, although the shared final-action continuation no longer invokes them. A later policy audit should decide whether to remove or reclassify those exposed operations.

## Parent work

Regenerate and verify the adapter operation allowlist and dependency evidence through the normal repository bootstrap only when a real authorized 3D job needs runtime execution. At that time, run the Blender real-file integrations and confirm the installed app launcher independently provides the reviewed artifact-persistence behavior. Final consumer wiring and live game validation remain parent-owned.
