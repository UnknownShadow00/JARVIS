# Deferred Items

Task 13B11M deliberately does not resolve:

- browser permission tension (`apps.open` confirms while `browser.open/search` allow);
- confirmation numeric TTLs;
- timeout confirmation lifecycle remaining `EXECUTING`;
- lane as an audit field;
- secret-key/redaction list and compound-value display policy;
- TIMEOUT provenance source;
- R1/R2 undocumented aggregate-digest formula;
- the real registry adapter;
- audit writer integration;
- conversational/model response boundary wiring;
- pipeline/shadow/live request composition;
- resource/model ownership changes.

Compound provenance values fail closed rather than solving the deferred redaction/display design.
No opaque confirmation ID is exposed.

## Smallest next independently reversible phase

The actual 13B11A dependency graph now advances from completed P6 to P7. Its §3 table says the
Hermes adapter can be built independently against recorded model outputs, while the pipeline is
the later integration point. Therefore the smallest next unit is a **passive P7 adapter boundary
against recorded outputs**, with no config change, no model invocation, no Hermes enablement, no
pipeline wiring and no user-visible behavior. This is identification only; it was not started.
