# Attribution Rules

Values are rendered only from one exact current, unambiguous `ProvenanceRecord` whose session,
fact key, status, source and trust class match the supplied projection.

| Provenance | Attribution |
|---|---|
| `USER_FACT` | “The value you supplied … not independently verified.” |
| `USER_REPORTED` | “You reported … not independently verified.” |
| `TOOL_SUCCESS` | “A trusted tool observed …” plus exact invocation/result/fact linkage |
| `CORRECTION_STATE` | current corrected supplied value, explicitly not external verification |
| `ROUTER_STATE` | deterministic route-state value |
| `CAPABILITY_STATE` | deterministic capability-state value |

Strings are JSON-quoted and escaped so attributed data cannot break out into another sentence or
line. Finite scalar JSON values are supported. Compound values and non-finite floats fail closed
because rendering them safely would require the deferred redaction/display policy.

Superseded records, duplicate/ambiguous records, wrong fact keys, wrong sessions, incorrect
source/trust pairings, unrelated invocations, or tool facts absent from the linked result cannot
support a claim.
