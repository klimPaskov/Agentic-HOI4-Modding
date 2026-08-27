# Skills and subagents workflow sync

Date: 2026-08-27
Owner: skills/subagents maintenance subagent

## Scope and result

Compared the general repository skill and subagent workflow with the current
Chaos Redux `.agents` skills and reusable agent-definition patterns. Applied
only high-confidence generic workflow rules to the five target skills below.
The general repository now records the alternate-runtime canonical-definition boundary, conditional shared unit-family provider integration, mandatory matching MCP evidence with exact unavailable-route blockers, and the current bounded 3D source/intake requirements. Stronger faithful-source and provenance rules in the general skills were retained where dirty Chaos wording was broader or contradictory.

## Sources reviewed

- General skill sources: `.agents/skills/hoi4-subagents/SKILL.md`,
  `hoi4-events/SKILL.md`, `hoi4-feature-planning/SKILL.md`,
  `hoi4-improvement-loop/SKILL.md`, and
  `hoi4-3d-model-pipeline/SKILL.md`.
- General reusable definitions: `.codex/agents/` entries, especially
  `hoi4_ai_probability_auditor.toml` and the 3D worker definition, plus the
  current `.codex/config.toml` policy. Definitions/config were inspected but
  were not edited in this bounded pass.
- Chaos Redux reusable sources: the corresponding
  `chaos_redux/.agents/skills/chaos-redux-*` skills and
  `chaos_redux/.codex/agents/chaosx_3d_model_pipeline.toml`.
- Relevant Chaos revisions reviewed included `4d52c94ec` (pose-preparation
  evidence), `89d8ad4f6` (style, period, color, and firearm preflight),
  `10ff72287` (Meshy rig/`meshy_animate` route), `00506d56e` (failure-driven
  provider recovery), and `0f05375a5` (generic event/subagent workflow).
- HOI4 Agent Tools routes were checked against the available tool surface. Reusable skills retain portable route names such as `hoi4.event_inspect`, `hoi4.gui_render`, `hoi4.probability_compare`, and `hoi4.tech_compare`; runtime-specific adapters may map those names to their native callable identifiers.

## Files changed

- `.agents/skills/hoi4-subagents/SKILL.md`
  - Documents canonical `.codex/agents/*.toml` ownership and generated
    Qoder/Cursor/OpenCode projections, including hyphen-case Cursor invocation
    and the no-hand-edit rule.
  - Updates event/UI, probability, and technology evidence to actual MCP names
    and keeps weighted changes on the
    `hoi4_ai_probability_auditor` audit-patch-compare route.
  - Aligns the generic 3D handoff with failure-driven recovery while live
    balance/capability permit and substantive `meshy_animate` or approved
    professional skeletal motion; Blender remains processing/validation only.
- `.agents/skills/hoi4-events/SKILL.md`
  - Adds conditional shared unit-family provider integration when the destination already exposes an extensible API, including idempotent registration, concrete equipment and presentation-token coverage, and a bounded provider-family audit.
  - Keeps event, GUI, and probability evidence on portable MCP route names and adds the conditional provider-family audit to the completion checklist.
- `.agents/skills/hoi4-feature-planning/SKILL.md`
  - Normalizes technology, GUI, and weighted-logic MCP references; requires
    exact route blockers and source-only non-equivalence.
  - Carries the current 3D skeletal-motion and failure-driven recovery policy
    into planning handoffs.
- `.agents/skills/hoi4-improvement-loop/SKILL.md`
  - Normalizes probability and technology MCP references and aligns the 3D
    recovery policy with live balance/capability stop conditions.
- `.agents/skills/hoi4-3d-model-pipeline/SKILL.md`
  - Extends job intake with style/period/color preflight, firearm-use and
    contact declarations, and explicit `pose_preparation_mode` evidence.
  - Makes failure-driven recovery stop conditions explicit while retaining the
    existing faithful source, immutable provenance, and one-approved-input
    safeguards.

No `.codex` TOML/config file was changed by this subtask. Runtime projections
and synchronizer files were not hand-edited; any concurrent runtime-sync work
belongs to the parent/other owner.

## Explicit exclusions

- Excluded every state-ledger/state ledger artifact, instruction, helper, role,
  generated entry, and related documentation from both repositories.
- Did not copy Chaos-specific gameplay, event-framework, CXT, meter, catalog,
  path, asset, or role material.
- Did not copy dirty Chaos wording that weakens faithful source identity,
  derivative provenance, explicit rights, or source-only non-equivalence. In
  particular, Chaos-specific source-first removal and source-informed
  redesign language were not generalized.
- Did not edit Chaos Redux, gameplay, schemas, manifests, README files,
  `AGENTS` templates, `.tools`, or any documentation other than this required
  handoff.
- Did not create a central MCP skill, router, or tool wrapper. Viewer routes
  remain read-only and bounded rewrite routes remain conditional on the
  discovered route existing.
- Did not launch HOI4 or claim live game/provider validation.

## Validation

- `quick_validate.py` passed for all five changed skill directories:
  `hoi4-3d-model-pipeline`, `hoi4-events`, `hoi4-feature-planning`,
  `hoi4-improvement-loop`, and `hoi4-subagents`.
- `git diff --check` passed for the five changed skill files. Git emitted only
  the existing LF-to-CRLF working-copy warnings.
- This bounded skill pass changed no canonical agent definition or config file. The parent subsequently aligned the canonical 3D worker policy and regenerated all runtime projections as part of the repository-wide sync.

## Unresolved items for parent review

- The general repository has no root `AGENTS.md`; only
  `AGENTS_template.md` and `AGENTS_chaos_redux.md` are present. Existing skills
  still require reading `AGENTS.md`; this was recorded rather than changing
  the forbidden templates.
- `.agents/skills/hoi4-map-modding/` has no `SKILL.md`; no new map skill was
  invented in this pass.
- Other owner skills and agent TOMLs outside this bounded set still contain
  shorthand MCP references and may need a separate normalization pass for
  focus, decisions, map, scripted-GUI, technology, or weighted surfaces.
- MCP route availability and live provider balance were not exercised here;
  affected workflows now require the exact missing tool/selector blocker and
  must leave source-only conclusions unresolved.
