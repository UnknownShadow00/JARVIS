# Task 13B11D — Correction and Supersession Semantics

Contract §10, invariants INV-007 and INV-019, conformance test CT-006.

## 1. The rule

Recording a value for a key marks the previous **current record of the same key and the same trust
class** as `SUPERSEDED`, names the record that replaced it in `superseded_by`, and appends the new
record as `CURRENT`. Nothing is deleted and no stored value is edited; the ledger is append-only,
and the superseded record stays queryable through `history()`.

## 2. Why supersession is scoped by trust class

The integration plan is explicit: a user correction supersedes the previous user statement, but it
does **not** supersede a tool observation — "a user statement cannot overwrite an observation … it
creates a newer SUPPLIED record alongside it, and the response layer is responsible for saying which
is which".

So a key may legitimately have two current records: what the user said, and what a tool saw. Both
keep their own attribution. The symmetric case holds too: a newer observation supersedes the older
observation and leaves the user's supplied value standing.

## 3. A correction is not a change to the world

§10.2. Given "port 8000", then "make it 8080", the current *supplied* value is 8080. The ledger
records exactly that and nothing more: no record claims a service restarted, a listener moved, a
configuration was applied or health was verified. Those would require a `TOOL_SUCCESS` record, and
the only way to create one is a real `TrustedToolResult` from the dispatcher.

The evidence bundle shows this concretely: after the correction,
`current('service_port', trust_class=VERIFIED)` is `None`.

## 4. Ambiguity is refused, not resolved

`current(fact_key)` returns the single current record when there is one. When a supplied value and a
verified observation both stand it raises `AmbiguousProvenance`, naming the competing trust classes,
instead of picking one. Preferring an observation over a user statement — or the reverse — is the
response layer's decision under §16, and the ledger will not make it silently.

Callers that know what they want ask for it: `current(key, trust_class=SUPPLIED)` or
`current(key, trust_class=VERIFIED)`, or take the whole set with `current_records(key)`.

There is deliberately **no** value-only accessor. Returning a bare value would drop the source and
trust class, which is exactly the attribution §16 forbids losing.

## 5. Same value recorded again

Supersession is keyed, not value-compared: recording the same value again creates a new record and
supersedes the previous one. This follows the integration plan's rule as written ("supersedes an
earlier CURRENT record with the same `fact_key`") and keeps "when did the user last say this"
auditable. Both records remain in `history()` with identical values and different ids.

## 6. What history guarantees

* `history(key)` — every record ever written for that key, newest first, including superseded ones.
* `current_records(key)` — the current ones only, newest first.
* `all_records()` — the whole session, oldest first.
* `snapshot()` — an immutable view of the current facts that does not follow later writes.

Every return is a tuple; a caller cannot mutate ledger history by editing what it was handed.
