# Future evidence sink owner

app/execution/shadow_observation_sink.py owns only record validation/explicit serialization, local durable evidence acceptance, UTC chronology sampling and a truthful sink-level receipt. Its production import must not initialize workers, create files, read a clock or touch services; side effects occur only on an explicitly authorized future persistence call.

The observation producer owns pure settled-fact projection. The future evaluator owns same-attempt facts and isolation; the scheduler owns admission/retries/overload. A future measurement controller owns window boundaries, reconciliation and acceptance decisions. The sink owns neither of these. Sink success confers no permission, confirmation, trust, provenance, execution or CT pass.

The existing source tree has no equivalent canonical sink or receipt with this responsibility. AuditLogger and JsonlTraceWriter have other owners, schemas, deletion/failure semantics and no durable success receipt; neither is reused as the sink.
