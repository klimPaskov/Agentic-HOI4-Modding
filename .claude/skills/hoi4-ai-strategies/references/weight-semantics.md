# HOI4 AI Strategies: Weight semantics

Part of the [hoi4-ai-strategies](../SKILL.md) skill. Read before writing or tuning any ai_will_do, ai_chance or strategy value, and before comparing two weights.

## Weight semantics

### The shared MTTH-style block

Most `ai_will_do` and `ai_chance` blocks use the same arithmetic (WIKI AI modding, "MTTH blocks"; Decision, Focus, Technology, Event wiki pages).

- The value starts at 1.
- `base = N` replaces the running value, `add = N` adds, `factor = N` multiplies.
- `modifier = { <triggers> add/factor/base }` applies its change only when the triggers are true.
- Top-level operations and `modifier` blocks apply in the order written, so a `factor` written before an `add` does not scale that add.
- Scope is the evaluated country (ROOT). Some surfaces add FROM scopes (targeted decisions, peace desires, faction goals and rules).
- A temporary variable set inside a `modifier` must be defined before the `add`/`factor` that uses it.
- Variables may be used in `add`, `factor`, and `base`. For repeated or shared weights use `hoi4-mtth` instead of copying modifier ladders.
- `factor = 0` inside a matching modifier forces the whole result to zero and is the standard hard block.

A worked check, taken from the wiki example: `base = 10.5`, `modifier add 1 (major)`, `modifier factor 3 add 2.5 (FRA)`, `factor = 2` gives 21 for a minor, 23 for another major, and 74 for FRA when FRA is a major.
Within the FRA modifier the wiki computes `factor` before `add` (`(10.5 + 1) * 3 + 2.5`, then times 2).

### Score is not probability

- Focus selection: for each available focus the game draws a random decimal between 0 and the focus value, multiplies the draw by 1.5 if the focus follows one just completed, multiplies by the strategy plan `focus_factors` entry, and picks the highest draw (National focus modding wiki, "AI will do"). A focus with value 4 beside a focus with value 8 wins far less than one third of the time. The wiki gives closed-form chances; small values lose disproportionately. Never read the ratio of two values as the ratio of chances.
- If no focus has a value above 0, the AI takes none and falls to continuous focuses or idles.
- Technology selection: every 7 days (`NAI.RESEARCH_DAYS_BETWEEN_WEIGHT_UPDATE`) a random draw between 0 and the weight is made per tech, with cost, bonus, and ahead-of-time modifiers on top. `NAI.RESEARCH_WEIGHT_TRUNCATION_THRESHOLD` picks randomly among scores within a fraction of the top score.
- Event options: weight divided by the sum of weights, rolled as a d100, so a weight share below 1 percent behaves like 0 and the share is rounded to whole percents. If every weight is 0 the first option is chosen. The result is deterministic for a given seed, time, and country across reloads (Event modding wiki).
- Decisions: the AI only considers decisions with an `ai_will_do`, compares them with a priority system, and may pick a lower-priority decision early within `NAI.DECISION_PRIORITY_RANDOMIZER` (0.1). Idea scores are scaled into `MIN/MAX_SCALED_IDEA_WEIGHT_TO_COMPARE_WITH_DECISIONS` (100 to 200). `CRITICAL_DECISION_PRIORITY` (200) lets a high-priority decision fire early. A decision that leads to war should declare it with `war_with_on_remove`, `war_with_on_complete`, or `war_with_on_timeout` so the AI prepares (see `hoi4-diplomacy-war`).
- Strategy `value`: not a probability. Each type defines its own meaning (additive weight, percent factor, absolute count, binary, threshold). Always read the token entry before choosing a number. Typical vanilla magnitudes: diplomacy weights 100 to 800, hard blocks at -800 to -1000, production percent factors 10 to 100, `role_ratio` small integers.
- A strategy with the wrong magnitude can be invisible or dominant, because several active strategies of the same type and target add together.

### Common ai_will_do traps

- Putting a hard prerequisite only in `ai_will_do` when the player can also do the action. The AI weight is not a gate; use `available` or `allow`.
- Giving every option `ai_chance` 0 (first option wins) or a lone positive value on a branch that the AI cannot legally pick.
- Using `ai_irrationality` (a trigger, vanilla focuses use it with `factor`) as if it were a random number; it is a country property read with comparisons.
- Forgetting that `base = 0` plus conditional `add` modifiers is the idiom for "never unless". Starting at the implicit 1 means the object is always eligible.
- Sharing one large `modifier` ladder across dozens of objects instead of computing one variable once.

