# Formable category attachment audit

Use this companion record for every manifest-driven state-puzzle consumer. The consumer manifest is the source of truth for the finite state set, projection, helper policy, and generated runtime names. This audit proves that every decision category in the formable family actually embeds the generated state-puzzle GUI.

## Attachment policy

Set `attachment_scope = all_formable_categories` when the owning event or system requires every shared and phase-specific category that exposes formation or integration decisions to show the puzzle. Categories outside the family may be marked `out_of_scope` only with a concrete reason. Never omit an uncertain category silently.

## Manifest-to-category crosswalk

Keep this table beside the completed manifest or owner handoff. Copy the generated GUI identifier and window name from the generated runtime files; do not guess a naming formula.

| Category ID | Category source | Formable decision IDs | Manifest path | Generated scripted GUI ID | Generated window | GUI context | Attachment status | Evidence or blocker |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `<category_id>` | `<category source>` | `<decision ids>` | `<manifest path>` | `<generated_gui_id>` | `<window>` | `decision_category` | `attached` / `missing` / `blocked` / `out_of_scope` | `<artifact or reason>` |

## Audit procedure

1. Enumerate category metadata and decision containers for the entire formable family, including shared and phase-specific categories.
2. Confirm each in-scope row names a complete manifest with the exact map revision, helper policy, and generated runtime outputs.
3. Inspect the generated scripted-GUI block. It must use `context_type = decision_category` and expose the manifest's state pieces.
4. Inspect each category metadata block and verify `scripted_gui = <generated_gui_id>` points to that generated block. A picture-only, text-only, or unrelated status window does not satisfy a strict attachment policy.
5. Use the installed read-only GUI inspect/render routes for the linked category window and retain artifact references for the row. If the route is unavailable, record the exact blocker; source inspection is not equivalent evidence.
6. Compare the category's formation decision and AI path with the manifest's shared territory helper. The GUI is informational and must not be the only formation gate.

Fail the audit on a missing or duplicate category row, manifest/category mismatch, missing `scripted_gui`, wrong context, unresolved generated reference, stale manifest status, missing DDS evidence, or a displayed state set that differs from the formation helper.

## Completion rule

The formable package is not ready for parent review until every in-scope category is `attached`, every generated state piece and hover resolves, and named scenarios show agreement between piece status, summary status, decision availability, and AI validity. A missing MCP route blocks the affected evidence; it does not authorize a source-only completion claim.
