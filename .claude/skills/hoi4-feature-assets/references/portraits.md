# HOI4 Feature Assets: Portraits

Part of the [hoi4-feature-assets](../SKILL.md) skill. Read before producing, sourcing or wiring any leader, commander, operative, advisor or officeholder portrait, together with the sourced-portrait handoff in workspace-lfs-and-portrait-archive.md.

## 21. Country-leader, commander, operative, and officeholder portraits

Choose the canonical reference family before production:

- country leader: `portraits/leaders/`
- army or navy commander: `portraits/commanders/`
- operative: `portraits/operatives/`
- advisor, theorist, high command, officer corps, or army-small:
  `portraits/advisors/`

Grounded real, historical, restored, separatist, regional, indigenous, dynastic,
or otherwise plausibly historical identities use an attributed real-person
source. One-person generated portraits are reserved for wholly fictional,
impossible, or supernatural identities. Missing or contradictory identity
classification fails closed.

For a real person, `hoi4_portrait_creator` preserves the unchanged archival master and imports it through `hoi4.image_process` with the portrait family, which runs the crop of `tools/extract_portrait_source_crop.py` (never run it by hand for that asset). Automatic mode uses the bundled YuNet detector and fails closed unless exactly one subject is detected; it writes the unchanged source copy, lossless crop, deterministic `156x210` PNG, exact-pixel JSON evidence, and a co-located provenance contract. Use the explicit `--crop` recovery path only for an independently reviewed boundary or detector miss. The detector is a framing aid, never identity approval. Retain the source placeholder and require independent likeness, style, identity, and provenance review before DDS conversion or wiring. The user alone supplies the HOI4-style final; when supplied, `hoi4_portrait_creator` validates, installs, and updates portrait-specific wiring.

Record source URL, author or archive, rights status when available, source and
candidate hashes, crop coordinates, review evidence, processed PNG, final DDS,
runtime sprite, and the durable source archive from section 2.4.

For fictional people and impossible or supernatural entities, `hoi4_portrait_creator` uses `hoi4.image_portrait` (`leader_portrait`, `commander_portrait`, `operative_portrait` or `scientist_portrait`) after the identity gate permits it.
Reject generic, modern, meme, gore, stereotyped, text-bearing, or
interchangeable output. If `hoi4-imagegen` has no provider, mark the portrait blocked.

Full country-leader, commander, and operative textures are `156x210`. Never
manufacture a smaller commander source merely because one UI view displays it
at a smaller apparent size.

## 21.1 Advisor and high-command portrait icons

Read [`references/icon-and-ui-families.md`](icon-and-ui-families.md) whenever a task creates decision category pictures or advisor and high-command portrait icons. It contains the complete standard for this section and its subsections.

## Animated leader portraits

Leader portraits can be animated for special routes, extreme-route leaders, supernatural leaders, rare formables, major transformations, or dramatic council reveals. They should not be required for every normal country leader.

Animated leader portrait packages must include:

- static fallback portrait
- animated sheet or frame source
- final DDS files
- final sprite names
- character or leader key that will use the portrait
- source mode and source documentation
- whether the leader is real, fictional, symbolic, collective, supernatural, or alternate-history
- note on motion type, such as glow, smoke, flicker, eye-light, flag shadow, slow breathing, office light, map projection, or particle drift

