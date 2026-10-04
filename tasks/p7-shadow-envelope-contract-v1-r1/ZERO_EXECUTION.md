# Zero-execution boundary

The envelope and pure composer carry passive text and existing settled values only. No call to pipeline, adapter, registry.call, dispatcher, executor, model/provider/Ollama, tools, HTTP/WS send, confirmation store, provenance writer or audit writer is part of composition. The future transport branch must not make any such object reachable through the envelope.

This session adds documentation only. Existing canonical regression tests use their isolated fixtures; they do not demonstrate live shadow execution. No evaluator or server consumer is implemented. A data-shape contract is not itself measured runtime zero-execution proof.
