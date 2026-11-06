# HOI4 Events: Event text and localisation

Part of the [hoi4-events](../SKILL.md) skill. Read before writing or editing any player-facing event text, documentation prose or localisation.

## Event writing and player-facing text

Event implementation owns final player-facing wording for event popups, news events, report events, event details, decision text, focus text, tooltips, GUI labels, scripted localisation, documentation summaries, and any parent-provided external records that mirror in-game text. Convert direction into finished wording, but do not paste working labels, prompt fragments, route notes, placeholder text, or process notes into localisation.

These writing style rules apply to every mod prose surface, including event text, news text, researched text, decision text, focus descriptions, tooltips, docs, specs, plans, prompts, and all player-facing text.

1. Never use the em dash or semicolons in sentences.
2. Absolutely avoid dialectical hedging. Do not frame sentences as thesis, antithesis, synthesis.
  - Dialectical hedging examples:
   - `This is not just a strike. This is a warning.`
   - `The cult is not fighting for land, but for meaning.`
   - `The disaster is both a local tragedy and a global sign.`
   - `The army did not collapse. It transformed.`
   - `This is less a rebellion than a confession.`
   - `The question is not whether order can return, but what kind of order will survive.`
  - Thesis, antithesis, synthesis examples:
   - `The army claims the province is secure. Refugees say it is already lost. The truth lies between them.`
   - `Some call the new state liberation. Others call it occupation. In reality, it is both.`
   - `The priests call it a miracle. The generals call it a weapon. History will call it both.`
3. Avoid AI-style explanatory templates. Do not write lines that sound prebuilt or reusable across any event.
4. Absolutely avoid staccato sentences. Do not split one simple thought into a chain of tiny lines for artificial weight or dramatic effect. Use complete, readable sentences with enough context to be clear.
  - Staccato examples:
   - `No orders. No mercy. No dawn.`
   - `The guns stopped. The screaming did not.`
   - `First hunger. Then anger. Then flags.`
   - `The gate opened. The crowd moved. The guards ran.`
5. Absolutely avoid empty dramatic filler. Do not lean on vague intensity words when concrete detail would do the work.
6. Do not paste instruction text, task labels, prompt fragments, or process notes into in-game text, specs, docs, localisation, external documentation fields, or reports.
  - For example, when the user says `Do not reveal the hidden mechanics here.`, do not write `This path purposely doesn't reveal the hidden mechanics`.

Write in-world text. Describe what the country, army, population, strange force, disaster, cult, machine, disease, movement, or leader is doing. Do not make the emotional center a changed map, a staff-table scene, administrative paperwork, formal diplomatic phrasing, sealed reports or generic crisis communications. They should not become the default way to create mystery.

Player-facing escalation text must not label itself as a warning, a non-warning, a threat, a danger signal, or a campaign-endinging risk. Let the player infer trouble through fear, missing people, strange behaviour, rumours, unexplained anomalies, local panic, and consequences that repeat over time. Do not build tension with staged contrast formulas. Forbid patterns such as `claim X while officials Y`, `reports say X while authorities Y`, `X before Y`, `people do X before governments Y`, and any similar construction that pairs one observation against a denial, admission, delay, or official reaction. Write the observed fear and uncertainty directly instead of using those contrast frames.

Only write sections for event surfaces that actually exist. Omit absent systems entirely. This applies to campaign-ending branches, manual scenarios, text or audio research packages, achievement sets, focus trees, country packages, and custom UI.

Do not expose hidden routes, secret variables, future surprises, achievement paths, implementation history, tuning history, or rework history in player-facing text. event details and any explicitly scoped external records describe the situation and premise, not the mechanical effects. Options, decisions, focuses, and tooltips must still clearly describe visible consequences and requirements, but they should not read like reward lists or spoil content.

For sourced text or audio packages, do not invent quotes, cultural remarks, song fragments, title references, or final audio choices. Use `hoi4-text-audio-research` and the relevant research subagents when the event needs sourced wording or music.


## Localisation and scripted localisation

Every player-facing event needs complete localisation:

- event title
- event description
- every option
- option tooltips when effects are not self-evident
- custom trigger tooltips for complex requirements
- news or report title and body
- scripted localisation selectors when dynamic names, states, countries, values, or routes appear
- event picture or sprite localisation only when the UI needs it

Localisation must describe the in-world situation and visible consequences. It must not expose implementation history, prompt fragments, hidden variables, secret route names, future surprises, or achievement spoilers.

Dynamic values often display decimal places unless formatted. If a value is conceptually an integer, use an integer formatter such as `|0` or an equivalent scripted-localisation helper. Use fractional precision only when the fraction changes player decisions.

For numeric `defined_text` output, put the formatted variable in a real `.yml` localisation value, such as `numeric_value_display: "[?temp_value|0]"`, and use the key's literal name in the corresponding `text` block: `localization_key = numeric_value_display`.
An inline formatted variable string such as `localization_key = "[?temp_value|0]"` is tokenized as a dynamic key and may fail with dynamic-token errors.
Temporary variables assigned in the same `text.trigger` remain visible to the selected localisation key, so calculate the display value there.
Retain constant-backed temporary getters where the installed documentation supports the assignment, and do not introduce persistent globals solely for formatting.
A scripted localisation `random_list` needs `seed = <scoped variable>`, or it repeats the same result. [vanilla-confirmed 1.19.3]
The triggers of a scripted localisation entry must be valid for the scope the key is called in. [vanilla-confirmed 1.19.3]
`§[ScriptedLocName]` yields a computed colour letter. [vanilla-confirmed 1.19.4.1]
The checksum covers only `common`, `events`, `history` and `map`, so a localisation-only mod keeps the checksum. [vanilla-confirmed 1.19.3] `checksum_manifest.txt`

Report and event descriptions drawn on a light parchment or paper background must use plain text for names and values, without `§` colour formatting, including strings returned by scripted localisation.
Keep colours only in consumers with a supported dark background, such as options, tooltips, decisions, or GUI text; use separate plain and coloured localisation variants when a shared helper feeds both.
Audit the whole owned description family and its dynamic substitutions for contrast in the actual consumer, including at 1080p.

Native PowerShell stdin can replace non-ASCII program text before Python receives it, even when Python writes a UTF-8 BOM correctly.
For localisation writes through that route, use ASCII program text with Unicode escapes or `chr()` for the `U+00A3` texticon and `U+00A7` formatting glyphs, or read the intended text from an explicitly UTF-8 file.
Re-read the affected values as UTF-8 and verify their actual glyphs after writing.
When normalizing physical line endings, preserve authored `\n` escapes inside localisation values rather than rewriting them as literal `\r\n` escapes.

When text mirrors a docs field or a parent-provided external record, the in-game localisation is the source of truth. Do not paraphrase mirror fields unless the field is explicitly a summary field.


