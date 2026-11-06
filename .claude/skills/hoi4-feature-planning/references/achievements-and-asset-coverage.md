# HOI4 Feature Planning: Achievements and asset coverage

Part of the [hoi4-feature-planning](../SKILL.md) skill. Read before planning the achievements or the asset coverage of a spec.

## 3.7 Achievement design standard

Achievements are mandatory for feature specifications unless the user explicitly says not to include them or the feature is so small that achievements would be dishonest. Major features, custom countries, deep focus trees, rare variants, international-order routes, or text and audio packages always need achievements.

Achievements should be creative and difficult. Do not design achievements that unlock just because the feature appeared, because the player clicked the obvious option, or because a country survived a few days. Achievements should reward mastery, unusual campaign states, risky choices, hidden routes, hard containment, difficult victories, or rare escalated outcomes.

A good achievement should usually require several conditions at once, such as:

- playing a specific country or route
- completing a difficult focus tree branch
- surviving a dangerous crisis state
- defeating or containing a major enemy
- avoiding an easy exploit, puppet shortcut, or foreign bailout
- triggering or suppressing a specific escalation variant track
- forming a special faction under strict conditions
- completing a rare extreme-route route
- winning while keeping a fragile coalition together
- using a special mechanic successfully without taking the safest path

Do not make achievements conservative. If the feature has dark paths, extreme-route tags, strange mechanics, foreign influence systems, coalition politics, or international-order ambitions, design achievements for them. Difficult achievements can require long campaigns, high escalation, multiple wars, internal crises, and careful decision play.

For each achievement, define:

- achievement id or working key
- title direction or working label, not final title
- player-facing description direction
- eligible starting country or countries
- exact story route or campaign situation required
- unlock conditions
- failure or disqualifying conditions
- whether it is visible, hidden, rare, or secret
- difficulty tier
- why it is interesting and not trivial
- icon direction and visual motif
- related focus paths, decisions, escalation variants, tags, factions, text and audio packages, or assets
- implementation notes for tracking if the unlock cannot be checked from a single final state

Achievement design must include asset planning. Each achievement needs a 64x64 completed icon direction, and the asset prompt must hand those icons to `hoi4-feature-assets`. Grey, locked, and not-eligible variants can be produced later if the achievement system requires them.

The achievement list should include a spread of routes. Do not put all achievements on the safest or most obvious path. Cover containment, failure recovery, republic victories, foreign influence, special factions, strange countries, extreme-route routes, and secret or hard branches when those exist.

If a feature creates many playable tags, design achievements for the most important ones and for the feature-wide systems. A large feature can justify dozens of achievements. The achievement prompt should still explain which ones are highest priority if implementation must be staged.

## 3.14 Mandatory asset coverage and source-mode standard

Everything visible or meaningful needs an asset plan. A major spec should not only define a few feature images. It should identify assets for countries, focus trees, decisions, ideas, national spirits, achievements, flags, portraits, faction emblems, text and audio packages, feature images, UI, unit systems, and route-specific identity changes.

Every focus in a mapped focus tree needs an icon direction. Large trees may use reusable icon packs, but the spec must still state which focuses use which motif or icon category. Do not leave hundreds of focuses with no asset guidance.

Every decision, decision category, idea, national spirit, achievement, faction emblem, UI panel, news image, report image, custom feature image, leader or council portrait, and important special-unit identity that appears in the feature needs an asset entry or a clear asset-family entry.

Every country package must include flags. Required flag coverage includes normal, medium, and small sizes for each implemented flag state. If the country has ideology-specific names, focus-tree transformations, puppet identities, restored historical forms, radical routes, or extreme-route mutations, the spec must identify whether those states need separate flags.

Historical and real-world flags should not be invented with the image generator by default. If a country, movement, party, military authority, or restoration path has a real historical flag or a well-attested symbolic design, the asset prompt should instruct the asset agent to source that flag or symbol from a reliable source, document it, and convert it into HOI4 flag sizes. Use the image generator only for fictional, alternate, supernatural, or deliberately invented flag identities when generated art is appropriate.

Historical or real leaders should not be generated. The spec should route every portrait to `hoi4_portrait_creator`, which sources and archives real images, records provenance and rights status, creates crops and placeholders, and processes user-supplied styled finals. For fictional leaders, council portraits, cult leaders, alternate invented officers, and symbolic committee portraits, the portrait worker invokes the image generator and completes production.

When an asset source is historically sensitive, disputed, or politically loaded, the asset prompt must require source notes, and a clear distinction between sourced historical use and fictional alternate-history invention.


## 13. Asset planning

Read [`references/asset-and-research-handoffs.md`](asset-and-research-handoffs.md) whenever the specification plans assets, writes asset prompts, or hands off text and audio research. It contains the complete standard for this section and its subsections. It also holds `14. Asset prompt handoff`, `15. HOI4 asset size reference`, `16. Asset style reference`, `17. Text and audio research handoff`.

