# Idempotence

Same immutable RecordedTurn and admitted timestamps yield equal outcomes with zero new executor calls, dispatch entries, claims, invocations, trusted results, writes or audit emissions. Current result identity is retained after successful S09 association; no store or clock participates. V1 IDEMPOTENCE.md remains normative. Cross-turn deduplication and reporting history are not added.
