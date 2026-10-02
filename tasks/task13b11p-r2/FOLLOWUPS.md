# FOLLOW-UPS

## BLOCKING NOW — P-B02: frozen `RecordedTurn` field 15 is unimplementable

**Question.** `RecordedTurn.confirmation` is frozen as `ConfirmationRecord | None` with
exact type identity, and guards B-01…B-07 additionally require `ConfirmationState.PENDING`,
`TERMINAL_STATES`, `is_fresh_at`, `execution_started` and `NON_CONFIRMABLE_ACTIONS`.
Implementing any of this makes `app/execution/pipeline.py` the first module under `app/` to
import `app/execution/confirmation.py`.

**Current behaviour.** Three frozen assertions forbid it:
`confirmation_non_activation_test.py::test_no_module_under_app_imports_the_confirmation_machine`
(`assert hits == []`, all of `app/`, no allowlist);
`test_no_public_symbol_is_referenced_anywhere_under_app` (19 symbols, substring match); and
`obligations_non_activation_test.py::test_the_confirmation_machine_keeps_its_zero_importers`,
whose docstring states the rule normatively — "whether an approval was claimed arrives as a
settled projection. The record's lifecycle stays P4-internal." P5 and P6 each paid to
preserve it; P6 re-froze a 442-row matrix to do so.

**Options.**
1. **Recommended.** Replace field 15 with a JARVIS-owned settled projection
   (`RecordedConfirmationObservation`) built from the record *outside* the pipeline, using
   only `types.py` enums and plain data. All seven guards survive, restated over projected
   fields; the confirmation machine keeps zero importers; S-14 becomes stronger because it
   rests on absence rather than an allowlist. Full field table in BLOCKER_ANALYSIS.md.
2. Drop mode B from v1, leaving two admission shapes. Smaller change, but a continuation
   turn after an approval request would have no representation and nine matrix rows would be
   deleted rather than restated.
3. Import the confirmation machine and extend its 20 assertions. Cheapest today; reverses a
   decision two prior phases implemented deliberately.

**Security consequence of choosing implicitly.** Option 3 silently moves the "no
confirmation mutation" property from *absence of the import* to *an allowlist entry*, and
puts the record's lifecycle inside a module whose whole purpose is composition. Option 1
keeps it where P5 and P6 put it. No option grants new authority, and no policy changes
either way.

**Artifacts a V2 must re-freeze under option 1:** `TURN_INPUT_SCHEMA.md` (field 15 type;
the exact-type-identity sentence narrows to fields 16–17), `ADMISSION_MODES.md` (the `c`
term), `CONFIRMATION_CONTINUATION.md` (B-01…B-07), `ASSOCIATION_RULES.md`,
`SECURITY_INVARIANTS.md` (S-02/S-03/S-14 mechanisms), `IMPLEMENTATION_ACCEPTANCE.md`, and
`ADMISSION_MATRIX.md` + `admission-matrix.json` rows `B01`–`B07`, `X01`, `X02` — new
matrix digest. Modes A and C and their 23 rows stand as frozen. Preserve the 13B11P-R1
documents as history; do not edit them in place.

## BLOCKING THE SAME IMPLEMENTATION — P-B03: scope of non-activation allowlist extensions

Any integration boundary needs roughly 41 assertion extensions across `router` (~12),
`permissions` (~15), `obligations` (~12) and `response` (~2), naming
`app/execution/pipeline.py` as a passive importer. This is authorized *in kind* by frozen
13B11O-R1 `IMPLEMENTATION_ACCEPTANCE.md` and precedented exactly by the obligation engine's
test naming `response.py`, and it weakens nothing in substance — no live wiring, no
request-path call site, `registry.call` stays at four sites in `app/server.py`. But no
frozen document has quantified it, and it touches four prior phases' suites. Requires an
explicit operator authorization of the scope rather than discovery inside a diff.
`dispatch_non_activation_test.py` and `confirmation_non_activation_test.py` need no change
(the latter only under option 1).

## Unchanged prerequisites

F-TYPE-01 remains implementation work, fully specified for `PipelineStop` and — after the
P-B02 repair — for `RecordedTurn`. F-MAP-01 remains unfrozen and BLOCKING for any branch
that derives a binding or dispatches from it, and BEFORE LIVE WIRING in every case; it does
not block comparison against admitted projections. F-FALLBACK-01 and F-AUDIT-01 remain
BEFORE LIVE WIRING and BEFORE LIVE AUDIT WIRING. F-REPLAY-01 remains BEFORE LIVE WIRING.
F-P7R1-01/02/03 remain open and were not closed or narrowed here.

FUTURE-AGENT-BRIDGE is preserved in DEFERRED.md and is not implemented or authorized.

## Next dependency

Resolve P-B02 (and authorize P-B03), land the admission contract V2 as explicit version
history with new digests and new evidence, then resume this same passive pipeline unit.
Freeze the fixture corpus against the repaired input type *before* writing any module code.
Live consumers, shadow mode, permission policy, confirmation policy, the real registry
adapter and Hermes activation each still require separate authorization. P8 and Task 13C
must not start. Stop here.
