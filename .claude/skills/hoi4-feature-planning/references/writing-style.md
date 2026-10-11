# Writing style for specifications and player-facing text

This reference belongs to the `hoi4-feature-planning` skill and holds complete sections moved out of `SKILL.md` to keep it within the single-read ceiling. Every rule here is as binding as the rules in `SKILL.md`.

## 10. Writing style

For player-facing text, define the same style as direction only. Feature description direction can stay grounded while option direction can use irony, sarcasm, cultural remarks, and humour that fit the actor and stakes.

Avoid:

- generic disaster wording
- empty dramatic language
- making every feature apocalyptic
- random escalation without purpose
- implementation code
- excessive technical detail
- filler text that repeats obvious system behavior
- displaying feature effects in feature-details
- long sentences without actually saying anything
- short staccato sentences that are dramatic and just make comprehension more confusing
- option direction that would lead to bland placeholder buttons
- absence notes for systems that are not present, such as saying that a feature lacks a surface that was never in scope

Mention implementation only where it matters for the design, such as custom presentation treatment, custom UI, AI behavior, documentation, assets, dynamic factors, focus tree structure, custom tags, or important system connections.

This planning skill defines direction for player-facing text. It must not write final player-facing localisation. This includes feature titles, feature option text, feature descriptions, news and report prose, decision names, decision descriptions, focus names, focus descriptions, achievement titles, achievement descriptions, GUI labels, feature-detail text, external record wording, presentation titles, presentation button text, main quotes, cultural remarks, source-like allusions, and final audio selections.

The planning spec may define tone, actor viewpoint, structure, visible information, route variation, dynamic placeholders that final text should use, and research needs. If a working label is needed for a row, filename, prompt, branch, route, asset, diagram, or internal handoff, mark it clearly as `working label, not final localisation`.

Important text and audio research boundary: this planning skill may define feature role, trigger, tone, image direction, quote direction, cultural-remark direction, and audio mood. Any source-dependent wording belongs to `hoi4-text-audio-research` and must stay blocked until researched and documented.

### General text writing style

1. Never use the em dash or semicolons in sentences.
2. Absolutely avoid dialectical hedging. Do not frame sentences as thesis, antithesis, synthesis.
 - Dialectical hedging examples:
  - `The invasion is not merely a border crisis, but a crisis of identity.`
  - `The regime is not only losing the war, it is losing itself.`
  - `This is not just a strike. This is a warning.`
  - `The cult is not fighting for land, but for meaning.`
  - `The disaster is both a local tragedy and a global sign.`
  - `The government is neither dead nor alive, but something worse.`
  - `The army did not collapse. It transformed.`
  - `This is less a rebellion than a confession.`
  - `The question is not whether order can return, but what kind of order will survive.`
  - `What looks like defeat is actually a new form of power.`
 - Thesis, antithesis, synthesis examples:
  - `The army claims the province is secure. Refugees say it is already lost. The truth lies between them.`
  - `Some call the new state liberation. Others call it occupation. In reality, it is both.`
  - `The priests call it a miracle. The generals call it a weapon. History will call it both.`
  - `The committee promises order. The opposition sees tyranny. The new system contains both impulses.`
  - `The papers call it a victory. The hospitals call it a defeat. The country has become both at once.`
  - `The rebels ask for justice. The regime asks for peace. The settlement gives neither and both.`
3. Avoid AI-style explanatory templates. Do not write lines that sound prebuilt or reusable across any feature.
4. Absolutely avoid staccato sentences. Do not split one simple thought into a chain of tiny lines for artificial weight or dramatic effect. Use complete, readable sentences with enough context to be clear.
 - Staccato examples:
  - `The radios died. The roads emptied. The city listened.`
  - `No orders. No mercy. No dawn.`
  - `The border fell. Then the capital. Then the government.`
  - `They marched. They burned. They vanished.`
  - `A knock at the door. A list on the table. A train in the dark.`
  - `The guns stopped. The screaming did not.`
  - `First hunger. Then anger. Then flags.`
  - `No king. No cabinet. No law.`
  - `Ash in the streets. Smoke over the port. Silence at noon.`
  - `One order. One shot. One missing officer.`
  - `The gate opened. The crowd moved. The guards ran.`
5. Avoid staged contrast formulas. Do not write sentences or paired clauses built as `claim X while officials Y`, `reports say X while authorities Y`, `people do X before governments Y`, `X happens before Y admits it`, or similar. Do not manufacture tension by contrasting unofficial fear with official denial, silence, delay, admission, or reaction. Write the observed fear, behaviour, rumours, anomalies, and consequences directly.
6. Absolutely avoid empty dramatic filler. Do not lean on vague intensity words when concrete detail would do the work.
7. Do not paste instruction text, task labels, prompt fragments, or process notes into in-game text, specs, docs, localisation, external documentation fields, or reports.
 - For example, when I say: `Do not reveal the hidden mechanics here.`, don't write `This path purposely doesn't reveal the hidden mechanics`
