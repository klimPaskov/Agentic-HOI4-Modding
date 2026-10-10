# Major-event defeat aftermath

This reference belongs to the `hoi4-events` skill and holds complete sections moved out of `SKILL.md` to keep it within the single-read ceiling. Every rule here is as binding as the rules in `SKILL.md`.

## Major-event defeat aftermath

Some major events should also have a structured aftermath when the threat is beaten.

Use a defeat aftermath package when all of these are true:

- the defeated threat was global or near-global in reach
- the campaign lasted long enough to feel like a world crisis
- the cost in casualties, destruction, or political disruption was high enough that the world should not simply snap back to normal

Typical aftermath content:

- a sourced defeat quote, cultural remark, or audio cue when the feature needs one
- postwar treaties, compacts, or new world orders
- recurring remembrance, reconstruction, or vigilance events
- lasting ideas, tech-sharing groups, or diplomatic rules that exist because the world learned from the crisis

Do not add a treaty/new world order after every contained or short-lived disaster. Those only make sense when the event genuinely reshaped the campaign.


### 7. Duration fields and constants

Use `script_constants` for shared tuning, but remember that some duration fields reject both `constant:` and variable tokens.

Before adding or extending `script_constants`, read the installed `common/script_constants/documentation.md` and `documentation/script_concept_documentation.md` (Script Constants), then inspect the existing group.
Every new group must begin with `schema` matching its key and data kinds (`int`, `fixed_point`, or a documented complex schema); new keys in an existing group inherit and must satisfy that schema.
A basic brace parse does not validate schema correctness.
Keep script constant category IDs unique across files so helpers with different schemas cannot redeclare the same category.

**Variable arithmetic evidence:** distinguish getter, modifier, normal variable, and script constant representations. Read the installed `documentation/script_concept_documentation.md` (Math Expressions) and the offline `paradox_wiki/Data structures - Hearts of Iron 4 Wiki.md` (Variables), and record precision conflicts rather than inferring a universal normal-variable maximum from math-expression fixed point, modifier-only three-decimal precision, or the deprecated raw-manpower getter overflow near 2.1 million.
Audit actual source operations with a conservative bounded fixed-point model, explicit rounding or truncation assumptions, and independent integer-floor boundary and count-type cases; a later division or clamp does not prove intermediate safety, and passing unbounded Python arithmetic does not prove engine behavior.
Never turn an unsupported numeric maximum into an eligibility gate or no-payment policy, or silently cap actual history.
For integer receipt validation, prefer modulo by one on scratch storage using the documented `modulo_temp_variable` effect and trigger forms without rounding the receipt or adding maximum or count caps; use ratio quotient and remainder or rational scaled coefficients only when proven equivalent under the stated arithmetic assumptions.

Known sensitive fields:

- `set_country_flag = { days = ... }`
- `set_global_flag = { days = ... }`
- any other timed field that throws `Malformed token` for either `constant:category.key` or a variable token

For those fields, use a file-scoped `@NAME = literal` constant in the same script file and pass `days = @NAME`. Keep the value mirrored with the matching `common/script_constants/` tuning entry, and update both in the same change.

Do not work around this by setting a temp variable and passing `days = temp_name`. those fields can reject variable tokens too. In which case, a `meta_effect` must be used if possible.
