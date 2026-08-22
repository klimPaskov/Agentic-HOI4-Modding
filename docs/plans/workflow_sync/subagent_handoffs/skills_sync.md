# Skills synchronization handoff

Date: 2026-08-22

## Scope completed

This bounded sync ports reusable, general HOI4 workflow practice from Chaos Redux into the starter skill tree. Only target `.agents/skills/**` and this handoff were touched. The Chaos Redux source repository was read for comparison but not modified; no large reference-image, model, audio, or other binary libraries were copied or hashed.

### Created

- `.agents/skills/hoi4-state-ledgers/SKILL.md` — generic exact-transfer contract, sparse aligned cohort registry, reception/outcome accounting, transaction-time map projections, no-double-counting proof, MCP map evidence, and handoff/validation rules. Chaos-specific IDs, historical profiles, balance choices, and implementation history were excluded.
- `.agents/skills/hoi4-3d-model-pipeline/references/source-reference-policy.md` — reusable designed-source, rights, `NoAI`, faithful-edit, native-alpha, one-input, and checksum/lineage policy.

### Updated

- `.agents/skills/hoi4-3d-model-pipeline/SKILL.md` — current `meshy-7` default, designed-source gate, native-alpha guidance, exact Technology Tree MCP route (`hoi4.tech_inspect`, `hoi4.tech_render`, `hoi4.tech_compare`) with unavailable-route/source-only blocker, verified provider/professional action-source gate, parent-variant lineage, and expanded provenance manifest fields.
- `.agents/skills/hoi4-subagents/SKILL.md` — current Meshy 7/source requirements and Technology Tree MCP evidence/blocker language.
- `.agents/skills/hoi4-feature-planning/SKILL.md` — current Meshy 7 plus designed-source/rights and native-alpha requirements.
- `.agents/skills/hoi4-improvement-loop/SKILL.md` — current Meshy 7 plus designed-source/rights and native-alpha requirements.

## Validation

The available quick validator passed for every changed/new skill folder:

```text
python C:\Users\klimp\.codex\skills\.system\skill-creator\scripts\quick_validate.py .agents/skills/hoi4-3d-model-pipeline  -> Skill is valid!
python C:\Users\klimp\.codex\skills\.system\skill-creator\scripts\quick_validate.py .agents/skills/hoi4-feature-planning       -> Skill is valid!
python C:\Users\klimp\.codex\skills\.system\skill-creator\scripts\quick_validate.py .agents/skills/hoi4-improvement-loop       -> Skill is valid!
python C:\Users\klimp\.codex\skills\.system\skill-creator\scripts\quick_validate.py .agents/skills/hoi4-subagents               -> Skill is valid!
python C:\Users\klimp\.codex\skills\.system\skill-creator\scripts\quick_validate.py .agents/skills/hoi4-state-ledgers           -> Skill is valid!
```

An additional scan found no `Meshy 6`/`Meshy6` references or stale Technology Tree Viewer absence claims under `.agents/skills`.

## Exclusions and parent follow-up

- No gameplay, runtime, `.tools`, `.codex`, root AGENTS/README/templates/manifests, or source-repository files were changed.
- Chaos-specific feature skills, identifiers, CXT/event names, private paths, one-off balance, and binary/reference libraries were excluded. Existing generic target skills without a bounded reusable delta were left unchanged.
- `AGENTS_template.md` remains outside this delegated scope and still contains the previously identified root-level Meshy 6 and obsolete Technology Tree Viewer claims. The parent should update those root instructions if desired; this handoff deliberately does not edit them.
- The target workspace has no root `AGENTS.md`; the existing target `AGENTS_template.md` and delegated skill instructions were used as the available infrastructure contract.
- No HOI4 launch or live gameplay validation was performed; parent-owned runtime wiring and live MCP evidence remain the completion boundary.

## Parent integration correction

The final independent completion audit found that the first bounded pass had not included the source repository's newest designed-art sourcing rules. The parent integration pass then updated `hoi4-3d-model-pipeline`, its source-reference policy, `hoi4-subagents`, `hoi4-feature-planning`, the 3D agent definition, `AGENTS_template.md`, and `README.md` to require eligible modern designed-art Internet search, excluded historical and documentary source families, immutable `refs/source/untouched.<ext>` and `source_search.md` evidence, faithful ImageGen cleanup, source-to-derivative visual-fidelity comparison, and explicit direction before any from-scratch fallback. The affected skills and regenerated Qoder agent output passed validation after this correction.
