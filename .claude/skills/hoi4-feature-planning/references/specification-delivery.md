# Specification depth, splitting, and improvement-loop specs

This reference belongs to the `hoi4-feature-planning` skill and holds complete sections moved out of `SKILL.md` to keep it within the single-read ceiling. Every rule here is as binding as the rules in `SKILL.md`.

## 12. Depth, file splitting, and internal resume notes

Do not compress the spec so much that important ideas become shallow.

The goal is depth, not speed.

Think through the feature as far as the idea can reasonably go. If the feature has multiple branches, escalation variants, rare variants, custom countries, focus trees, UI elements, text and audio packages, or major system connections, treat each of those as deserving real design space.

Large feature specifications should be written across multiple repo files instead of being rushed into one oversized file. Split at clean design boundaries, such as the core loop, variants, focus trees, decisions, country packages, assets, AI, or acceptance criteria.

Each file should be complete enough to be useful on its own. Stop at a clean section boundary or a clean subsection boundary when possible. If a design surface is too large for one file, stop after a complete paragraph, table, route, country package, or list item instead of cutting a thought in half.

Do not summarize later sections just because the current working context is getting large. Continue in another repo file under the same spec folder. Use the available context for real specification content and do not hold back important design material for a shorter handoff.

When a large feature specification cannot fit in the current response, end the response with a temporary continuation prompt for the next iteration. This prompt is a working handoff, not part of the saved specification, final package, or feature documentation. When the agent can continue by writing the next repo file without yielding, prefer that; use the prompt when response boundaries or a handoff make it necessary.

The continuation prompt should include:

- the feature slug, feature name, and current part number when known
- the exact section and subsection where work stopped
- the last completed heading, table, route, country package, or design surface
- the next heading, table, route, country package, decision family, asset group, or research brief to write
- constraints that must continue to apply, including localisation direction, country naming rules, asset source rules, and the user's core feature idea
- a reminder to continue with full-depth design and not summarize missing sections
- a reminder to avoid repeating completed sections except for short context needed to continue cleanly

Use a clear temporary heading such as `Temporary continuation prompt, not part of the spec`. Keep it outside the saved spec content. In the final compiled package, remove all temporary continuation prompts and retain only the complete specification and requested final handoff files.

If several iterations are needed, each response should write a new continuation prompt that reflects the current stopping point. Do not reuse an older prompt after the design has moved forward. When the final part is complete, omit the continuation prompt and provide the finished package or completion summary.

Internal continuation notes are allowed only when the agent is about to hit context limits, output a very large amount of design material, hand off to another agent, or prepare for auto compaction. Put those notes outside the source spec, preferably in `docs/plans/<feature_slug>/resume_packet.md` or another clearly marked plan handoff. Internal notes should not be part of feature docs, localisation, spreadsheets, or asset manifests.

An internal resume note should include:

- feature slug, feature name, and current source spec folder
- files already written or updated
- the exact section, subsection, route, table, country package, or design surface where work stopped
- the next file, heading, route, decision family, country package, asset group, or research brief to write
- constraints that must continue to apply, including localisation direction, country naming rules, asset source rules, and the user's core feature idea
- unresolved research needs, blockers, and accepted assumptions
- a reminder to continue with full-depth design and not summarize missing sections
- a reminder to avoid repeating completed sections except for short context needed to continue cleanly

When the source spec is complete, remove temporary resume wording from source spec files. If a resume packet remains useful for implementation, keep it as a working handoff under `docs/plans/` rather than source design.

For major features, the final combined specification may be extremely long. That is acceptable. A 10,000 line, 50,000 line, or 100,000+ line specification is valid if the feature truly needs that much design detail. Do not compress focus trees, rare variants, or decision webs into summaries just to keep the file short.

Avoid filler. Every section should add useful design, player-facing detail, implementation clarity, asset direction, or system connection.

Before saving the final spec, run a cleanup pass. Remove generic safeguards, obvious implementation boilerplate, empty labels, repeated wording, and admin audit sections.

## Improvement-loop expansion specs

When `hoi4-improvement-loop` produces an expansion addendum, treat it as feature-planning input. The addendum should be folded into the main spec pack with the same seriousness as the original user idea. Do not treat it as a loose suggestion if the parent accepted it.

An improvement-derived spec can be shaped freely. It does not need to copy the section order of this skill. It should still make the design concrete. A useful addendum explains the playable promise, the route or mechanic that feels shallow, the deeper player loop, the choices that change outcomes, the AI behavior, the visual and localisation needs, and the surfaces that must align.

### Mandatory near-completion improvement loop pass

Before any feature-planning goal is treated as near complete, the coding agent must spawn `hoi4_improvement_loop_planner` for a final depth and anti-bloat pass when the repository has that subagent. This is mandatory for feature specs, large addenda, country packages, focus-tree plans, decision systems, quote, remark, and audio research planning, asset-heavy plans, formable plans, custom UI plans, and any goal that creates or changes meaningful mod design.

Run this pass after the main design is mostly assembled and before the final completion report. The loop planner should inspect the current spec, accepted plans, unresolved handoffs, asset needs, AI plans, mechanic surfaces, and implementation handoff needs. Its job is to find remaining shallow systems, disconnected mechanics, missing route depth, missing AI behavior, missing asset states, missing aftermath, or scope bloat.

Spawn the loop planner without inherited conversation context. The parent prompt must explicitly pass the feature slug, current goal, user constraints, current spec paths, relevant plan paths, known unresolved decisions, and the exact question to answer. Do not rely on inherited conversation context.

The loop planner may return either an expansion addendum or a closure handoff. If it returns an expansion addendum, the parent must resolve it before completion by folding accepted content into `docs/specs/<feature_slug>/`, implementing or queuing it with a clear reason, or rejecting it with a clear reason. If it returns a closure handoff, record that closure and proceed with final checks.

A goal is not complete while an accepted loop addendum is unresolved, while a loop-recommended closure handoff has not been recorded, or while the mandatory loop pass was skipped without a tooling blocker. If the loop agent cannot be spawned because the tool is unavailable, the completion report must state that as a blocker and must not hide it as finished work.

Tiny known-file text edits, narrow typo fixes, and direct one-line skill updates can skip the loop pass only when they do not create or change feature design, mechanics, focus trees, decisions, country packages, assets, sourced text or audio packages, or implementation handoff rules.
