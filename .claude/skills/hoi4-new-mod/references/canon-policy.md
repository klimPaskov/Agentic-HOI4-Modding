# Canon policy

Part of the [hoi4-new-mod](../SKILL.md) skill. Read before writing `docs/mod/canon.md`, and before writing any lore, history or player-facing text for the mod.

A mod built over many sessions drifts when one session's invention becomes the next session's fact. The canon policy keeps what is settled apart from what is only proposed, so later work builds only on settled ground.

## Two kinds of material

| Kind | What it is | Where it lives |
| --- | --- | --- |
| Established | The user's own words and choices, accepted decisions in `decisions.md`, the agreed brief, real history and geography from sources, and vanilla game facts | `canon.md` under Established, each with its source |
| Proposed | Anything an agent invents: a leader's name, a party, a city, a backstory, a war's outcome | `canon.md` under Proposed, with the feature that needs it |

## Rules

1. Write player-facing text only from established material, or from a proposal the brief lets the agent settle (see Promotion).
2. Never contradict an established fact. When a feature needs to, ask the user, and record the answer.
3. Every proposal names the feature that uses it, so a rejected proposal shows what it touches.
4. Real people, places and events follow sources. A real person never says or does something invented that would read as historical fact; alternate-history changes are framed as the mod's divergence, which the brief names.
5. Names, dates and numbers that appear in several features (a capital, a leader, a founding date) are recorded once in `canon.md` and copied from there.

## Promotion

A proposal becomes established when:

- the user approves it, by name or by approving the feature spec or picture round that contains it; or
- the brief's autonomy says "ask once, then build" and the proposal fills a gap the user left to the agent: record it as established with origin `agent default`, so the user can still overrule it.

A promoted proposal moves to Established with its origin and date. A rejected one is removed, and every feature that used it is reopened in the ledger (`passes: false`).

## Template

```markdown
# <Mod name>: canon

## Established
| Item | Fact | Source or origin | Date |
| --- | --- | --- | --- |
| Capital of Atlantis | Poseidonis | user | 2026-01-01 |

## Proposed
| Item | Proposal | Needed by feature | Status |
| --- | --- | --- | --- |
| First head of state | Admiral Kleito Varos | country-atl | proposed |
```
