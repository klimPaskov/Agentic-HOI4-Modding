# Project rules: Modding rules summary

Part of the [hoi4-project-rules](../SKILL.md) skill. `CLAUDE.md` summarizes section 4. Read before implementing any new mechanic, and before replying to a user's problem report.

In this file `GAME` is the vanilla Hearts of Iron IV folder, `WORKSHOP` the Workshop content folder and `PREFIX` the mod's script prefix. `CLAUDE.md` names all three.

## 4. HOI4 Modding Rules Summary

When implementing any new mechanic, follow this checklist:

1. Consult pertinent offline wiki and installed-game documentation sections through the reference tools in section 0 of `CLAUDE.md`, or read those local sections directly when a route is unavailable. Keep exact citations for the syntax and engine behavior used by the change.
2. In addition to the HOI4 wiki, inspect vanilla files in `GAME` and read all the necessary documentation, particularly in `GAME/documentation`.
3. Create a new markdown file in `docs/` for the mechanic you've added. Describe what it does, how it works step by step and how it interacts with existing systems. Add a section for future plans and your own suggestions on how the mechanic could be extended or made deeper.
4. In that docs file, list all icons needed for the new features. Write where the sprites should live, which `gfx` file should reference them and what icon names are used in code and localisation, so the wiring rules from this file are also clear inside the docs file.
5. Plan variables and flags so that values are dynamic and centralised.
6. Avoid unsupported operators and constructs.
7. Use loops, meta effects/triggers if needed to make things dynamic, and scripted effects or scripted triggers to remove duplication.
8. Reuse existing dynamic scripted effects before writing new bespoke logic. If new dynamic effects/triggers are added, document them in `docs/PREFIX_dynamic_effects.md` in the same change.
9. Keep localisation, icons and UI definitions aligned with changes in the same edit.
10. When adding any new equipment type/archetype/category, also update `common/script_enums.txt` (`script_enum_equipment_bonus_type`) in the same change.
11. Document each new script file with an overview at the top.
12. Confirm that all decisions and event options or other effects have proper trigger tooltips and effect descriptions.
13. Respect the repository style and naming rules so new content blends with this mod's existing code.
14. For systems that touch or are related to an existing project-wide mechanic, review related docs and verify integration across events, on_actions, decisions, scripted logic, UI, logs, and localisation.
15. Never launch Hearts of Iron IV during normal implementation, audit, or completion work. Live game and launcher testing is owned by the user unless they explicitly invoke `hoi4-debug-playtest`, ask for live testing through `hoi4-live-playtest`, or explicitly authorize that bounded workflow for the current task.
16. When the user reports an issue after new changes were made, assume the game has already been reloaded. Do not default to restart/reload advice. Do not ask for, request, or search for logs. If the user did not paste any error lines, treat it as having no error lines to use. Do not tell the user to run in-game validation. Assume they will always verify changes in a live session and in a new save. Do not mention old saves. When the user supplies a save, read it with `hoi4-save-inspection` before forming a hypothesis.
17. Design fallbacks and reductions of requested functionality require user approval unless already authorized. Direct source and reference review and local checks are preauthorized verification alternatives and do not require another permission question. A wired sourced portrait remains an explicitly pending source placeholder until the user supplies its HOI4-style replacement.
18. When the user reports that something is wrong and you can't figure out what exactly, then add temporary debug code (for example: `log = "my debug log"`) that exposes the relevant runtime values needed to understand the issue, and remove every debug line you added once the issue is resolved.
19. When an error is reported or discovered after your changes, treat it as caused by your current change set. Do not speculate that the project was already broken before your work.
20. When updating content (for example reworking an event), write as if the feature has always existed. Do not use meta wording like “now it is,” “now it has been reworked,” “newly added,” or similar update-history phrasing.
21. Respect the writing style.
22. Markdown prose must not be hard-wrapped in the middle of a sentence or clause. Keep each prose sentence on one physical line and preserve deliberate Markdown structure such as paragraphs, lists, tables, block quotes, and code blocks.

Follow these rules and your changes will be easier to review, safer to merge and more consistent with the rest of the project.
If an indispensable input is still missing, finish independent work and ask once as Upfront consultation allows. An unavailable check alone calls for source review and useful local checks, not another design request.
