# HOI4 Decisions and Missions: Cost localisation and payment

Part of the [hoi4-decisions-missions](../SKILL.md) skill. Read before writing cost text, custom_cost_text keys, affordability gates, debits or refunds for a paid decision.

## 6. Cost localisation

An action may spend at most four distinct resource types. Non-consumed conditions such as holding a state or route remain requirements. Do not conceal a fifth payment in a tooltip, effect, confirmation, or secondary panel. Redesign the action instead.

Inline cost/status text shows at most three values, each paired with its correct texticon, and at most four ordinary words when text is necessary. Do not repeat a payment already drawn by the native row or expand resource names beside icons. Separate texticon names from following formatting codes with whitespace, or use closed syntax verified in installed vanilla. Amount-first and icon-first entries are both allowed when the native render proves fit and icon separation.

Keep every payment and reserved resource explicit in the full tooltip. Verify the longest available and blocked strings beside the actual decision title using the matching native MCP render. Record the exact unavailable route or scenario blocker if this evidence cannot be obtained, and do not substitute source-only review.

Do not prefix every blocked cost line with words like `Requires` or `Needed`. In most cases, show only the value and the matching text icon.

Good examples:

- `2,000 <infantry_equipment_texticon>`
- `20 <army_xp_texticon> 20 <command_power_texticon>`
- `200 <support_equipment_texticon>`
- `Depot control`

Do not add filler words between costs.

Use:

`20 <army_xp_texticon> 20 <command_power_texticon>`

Do not use:

`20 <army_xp_texticon> and 20 <command_power_texticon>`

If the country does not meet a requirement, show the missing or unmet cost in red. If the country meets the requirement, show it normally.

For numerous non-cost requirements, use a short scripted localisation summary:

- met: `Requirements met`
- not met: `§RRequirements not met§!`

Then put the full requirement list in a tooltip. Missing requirements should be red, while satisfied requirements display normally. This summary never conceals extra spendable costs. A custom spendable resource needs a wired texticon before appearing in cost text.

### Custom-cost affordability and payment

Every native `custom_cost_text = <base>` needs localisation for `<base>`, `<base>_blocked`, and `<base>_tooltip`; the engine selects the row key through `custom_cost_trigger` and shows the tooltip key on hover (offline Decision modding, custom cost section).
Per-resource scripted colour selectors do not replace these parent native keys.
When the base already renders each resource's ready or blocked colour independently, exact `$base$` aliases for the suffixed keys can reuse that quote without duplicating amounts or adding fees.
Trace actual decision consumers, scripted getters, and texticon definitions; missing source-key coverage establishes a contract gap, not proof that a native row displayed a raw key.

Custom-cost display is not sufficient evidence that a decision is selectable. Define one shared, inclusive affordability predicate and invoke it from both `available` and `custom_cost_trigger`; manually debit the custom payment once in `complete_effect`, and set the fixed `ai_hint_pp_cost` amount when political power is included. If the cost row already fully explains payment, the duplicate `available` check may use `hidden_trigger` to keep raw requirements out of the visible block. Keep display, affordability gate, and debit aligned, and document engine uncertainty instead of inferring behavior.
Each resource's cost colour or display selector must call the same authoritative inclusive affordability component used by that shared gate, with the same payer, quote, units, and equipment token.
Do not copy strict, deprecated, or inexact reserve or equipment predicates into display logic.
Check agreement just below, exactly at, and just above the quoted cost.

For fractional dynamic costs, show enough decimal places in every cost row and tooltip to communicate the actual debit. Keep display caches separate from fresh affordability and payment calculations so a rounded or stale quote cannot govern selection or payment.

When accepted design requires an emergency resolution to remain available while every other recovery is unaffordable, do not gate it on full nominal reserves. Bound each actual fee by its nominal fee and the nonnegative current reserve, show the actual quote with matching texticons, recompute all fees together before any debit, then charge that coherent quote once. Avoid hidden partial payments and threshold fee-waiver cliffs.
For variable-fee emergency actions, use an `ai_hint_pp_cost` matching the actual quote only if that input form is verified as supported; otherwise omit the fixed nominal hint so a zero quote remains available to AI at zero political power. Never assume `ai_hint_pp_cost` accepts dynamic values.
Verify exact numeric reader tokens in the installed dynamic-variable documentation rather than assuming a display or stat name: `has_political_power`, `has_stability`, and `has_war_support` are documented readers, while raw `war_support` is not a documented built-in reader. This does not forbid a custom normal variable with that name.
Make final resolution and cleanup idempotent with a closed-state guard, and require queued work and late timed callbacks to match the active context before invoking cleanup. Preserve earned finite aftermath until its intended expiry and retain achievement receipts when removing active-crisis state.

### Refundable purchases and separate credit receipts

When a refundable decision both charges a currency and grants separate credit, such as progress toward an achievement or a sale-period counter, keep the two receipts apart.
Store the exact paid quote in an owner normal variable for the currency refund; never infer credit from the price, an active sale, or another display value.

- Clear the previous owner receipt before crediting, preinitialize every helper output temp in the caller chain, and invoke the shared credit helper exactly once after payment.
- Persist a positive credited result as an owner country flag and its credit sequence or period identifier as an owner normal variable. Use separate pairs for decisions whose timers can overlap.
- On cancellation, load the saved flag and sequence into the helper inputs and withdraw credit only when the receipt sequence matches both the current credit period and the payer's retained credit record.
- Refund the recorded paid quote once and clear the persistent receipt pair and paid marker, so repeated cancellation cannot refund currency twice or withdraw another purchase's credit.
- Successful completion clears the receipt and paid marker without withdrawing earned credit.
- Do not invent a historical credit ledger, reverse an older purchase through a newer index, or revoke an awarded achievement.

Verify same-period refunds, purchases made outside a credit period, older-period refunds after a newer purchase, excluded credit eligibility, repeated cancellation, and successful completion through the actual helper chain.

