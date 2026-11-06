# HOI4 Decisions and Missions: Mission design

Part of the [hoi4-decisions-missions](../SKILL.md) skill. Read before designing a mission's objective, duration, native timer, outcomes or active-mission cap.

## 8. Mission quality

Do not create passive checklist missions that the player already satisfies.

Bad missions:

- have 20,000 manpower
- have 500 rifles
- have stability above 35 percent
- have war support above 35 percent
- own a small generic stockpile
- wait until a passive condition is true
- pay political power to reduce a meter

Good missions:

- hold named capitals for a deadline
- place supplied divisions in named states
- secure named rail hubs
- guard named depots
- keep a capital connected to supply
- send equipment through an aid decision
- open or close a named corridor
- build influence over a target country
- protect a border line with actual units
- complete a local support chain before a deadline
- prevent a rival influence threshold
- rebuild a named railway or supply line
- keep a port open while a convoy mission runs

Even easy missions should require real action. Easy should mean lower risk or shorter scope, not passive.

## 9. Mission duration

Timed missions need enough time for the player and AI to act.

Use varied durations based on mission difficulty.

Recommended bands:

- easy missions: at least 90 days, often 90, 95, 100, 105, or 110 days
- medium missions: usually 120 to 180 days
- hard missions: half a year or a full year when the objective is large

Emergency missions can be shorter only when the event story clearly justifies immediate danger.

Do not give every mission the same timer.

For every decision-level `modifier = { ... }`, define `days_remove` even when `days_mission_timeout` is present; the modifier applies during the active post-selection removal timer, not the mission timeout.
A `modifier` nested inside `ai_will_do` adjusts AI weight and is not a decision effect.
Audit the entire owned decision and mission family by block scope, preserving completion, removal, timeout, cancellation, and cleanup behavior.
Derive `days_remove` from the intended active duration and existing tuning; do not invent deadlines or change mission deadlines only to satisfy this requirement.

### Synchronizing native mission timers

`activate_mission` initializes the native `days_mission_timeout` from the static mission definition; changing a separately stored deadline does not update it.
Immediately after activation and after every accepted deadline extension, synchronize in the mission owner's country scope, guarded by the active contract, an existing deadline, and `has_active_mission`.
Compute remaining days as `deadline - global.num_days`, then pass the signed difference `remaining_days - days_mission_timeout@mission_id` to `add_days_mission_timeout = { mission = mission_id days = var:timeout_delta }`; this can shorten or extend the native timer and is idempotent.
Partial payments must leave the running mission and deadline intact rather than removing and reactivating the mission.
If the deadline has already expired, use the guarded timeout resolver; the native timeout callback and any owner recovery pass must share an active-contract guard and clear it on resolution so failure cannot resolve twice.

## 10. Success, failure, and partial success

Success and failure must use distinct effect logic.

A successful stabilising mission should lower or stabilise the relevant pressure. It should not raise the main threat by accident.

Failure should create consequences, such as:

- higher threat
- lower authority
- higher enemy confidence
- higher foreign penetration
- depot vulnerability
- local unrest
- new report event
- harder follow-up mission
- AI strategy change

Partial success is useful when a mission has mixed outcomes.

Example:

- rail hub secured, but local support lost
- capital held, but foreign recognition spread
- depot guarded, but old movement pressure rose
- border reinforced, but another front weakened

A heavy-handed success may lower one pressure while raising another. The tooltip must explain the tradeoff.

## 11. Objective capacity

Do not overload a decision category with too many active missions.

When a system has many possible missions, use:

- hidden queued missions
- active mission cap
- priority scoring
- regional mission families
- phased unlocks
- mission pools

Only show the most relevant active missions. A player should not see a wall of similar objectives.

If the spec defines a cap, respect it.

