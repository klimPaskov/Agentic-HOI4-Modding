# HOI4 Events: Scopes and helper outputs

Part of the [hoi4-events](../SKILL.md) skill. Read before writing effects that change scope or call scripted helpers that return values.

### 5. Use scopes deliberately

Event bugs often come from scope drift.

Before writing an effect, identify the expected scope:

- `ROOT` for the event owner
- `FROM` for the caller or target from the firing context
- `FROM.FROM` only when the chain is clear and documented
- `THIS` for the current iterator scope
- state scopes when selecting states or using state modifiers
- country scopes when saving targets or applying country effects
- global scope only for intentionally shared values

If an effect chain needs a scope later, save it as an event target. Use regular event targets for short chains and global event targets only when persistence is required. Clean global event targets when the system ends.

For country activation, deferred setup, player transfer, or coalesced refreshes, read [country-activation.md](country-activation.md) before implementing the receiver chain. For variables, arrays, loops and script math, read [variables-and-math.md](variables-and-math.md).

When inlining a multi-condition scripted trigger inside `NOT`, retain an explicit `AND` around its conditions because sibling conditions in `NOT` use NOR semantics. Preserve rejection when either a shared precondition or native legality check fails. State-scoped diagnostics must check country flags through the intended country scope.

Stored state pointers refer to persistent map objects, so do not use COUNTRY-only `exists = yes` inside a STATE scope.
Validate the intended state with an appropriate documented native STATE predicate or a registered state marker such as `has_state_flag`, together with its expected state ID using the documented identity semantics.
`scope_exists` is always true for variable scopes and does not validate the stored pointer.
Retain `exists = yes` checks in actual COUNTRY scopes, including a state's owner, controller, or stored country pointer.

Native callbacks keep their own ROOT and FROM contracts, and participant iterators, targeted decisions, and nested transactions do not rebind ROOT. The callback scope table, participant capture pattern, frozen transaction inputs, receipt nonces, and state-owned cadence rules live in [country-activation.md](country-activation.md); read them before changing a callback-to-helper scope chain or a receipt read.

### Helper output lifetime

Temporary variables first created inside a scripted effect or trigger may disappear after return, while caller-preinitialized storage retains the helper's modifications (offline `hoi4_wiki/data_structures.md`, Variable types section).

- Before each helper call, ensure every temporary scalar and temporary-array output consumed afterwards has caller-owned storage, including calls inside `if.limit` and scripted-localisation `text.trigger`. Initialize new output storage to zero or its documented invalid sentinel without resetting existing input or cursor values.
- Apply this at every nested call boundary: each caller initializes the outputs it consumes, and outer callers also initialize forwarded outputs needed after return.
- Helpers reset public outputs at entry and clear one-shot input envelopes separately on success and rejection, without erasing published results before the caller consumes them.
- Public helper API docs must list caller-owned output storage and its required initial values.
- Actual-source tests must model conservative call-frame cleanup by discarding temporary scalars and arrays first created in the returning helper, retaining modifications to caller-preinitialized storage, and keeping scoped regular saved state separate from temporary storage instead of using one flat global temporary dictionary.

When a source audit or fixture cannot model this call-frame lifetime, report it as unmodelled and separately check caller preinitialization before consuming helper outputs.
For shared dispatchers, locate the matching authorization gate and recursively inspect its body and invoked helpers for actual dispatch and accounting, including package-specific nested branches.
A flat block-shape assertion or literal marker match does not establish that execution coverage.

