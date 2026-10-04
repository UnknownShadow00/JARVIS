# Structural zero-execution contract

Producer call boundary has zero registry.call, handler, dispatcher, executor, real tool, Hermes/model/provider/Ollama call, confirmation mutation, provenance write, audit emission, clock call and external I/O. It returns data only; no file/database/network/queue writes or scheduled callback. This is a future implementation invariant, not a runtime-call counter serialized in the record.

The future dependency budget may use only standard immutable/serialization/hash helpers and the existing passive source types/identifier validation needed by INPUTS.md. No app.tools, live registry, app.server, transport framework, service locator, provider client, confirmation machine, dispatch module, audit writer or P2 store dependency. Importing a type-owner module must not invoke that owner's API. Do not call snapshot_registry_metadata, which reads source files, even though it is passive elsewhere.

Future focused sentinels must guard the producer call after allowed fixture setup/imports, rejecting clock, filesystem, socket/process/thread and owner-evaluator/write entry points. Existing canonical regression uses isolated test fixtures; it is not new observation-runtime proof. No production module exists in this task and no observation is emitted.
