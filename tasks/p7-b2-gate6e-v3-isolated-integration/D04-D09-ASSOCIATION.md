# Delivery and D04/D09 associations

Nonproduction Gate 6E reference implementation. No production installation, experiment approval, model traffic, credential use or measurement. G6D-LP-1 remains a proposal.

The controller first durably consumes the permit and records acceptance; a separate global high-water reservation precedes it. Each router/responder/Granite transmission has its own durable POSSIBLE_SEND substep, never a second pilot attempt. Only Granite produces an observation submission.

On send completion the controller and EvidenceBridge record LOCAL_SEND_COMPLETED, and legacy-owned assistant text enters bounded in-memory history. Generated text alone proves no delivery. Granite failure does not erase a delivered reply. No raw reply/prompt is persisted in task evidence or association databases.

EvidenceBridge uses actual D04 observation schema1 decoding, entry validation, minimized projection and ShadowObservationSinkReceiptV1. Its explicit root replaces any singleton sink access. D09 association extension1 durably records COMMIT_UNCERTAIN before append, fsyncs the D04 line/directory, then joins sequence/digest/correlation to the exact accepted Granite step. Duplicate submissions refuse before append; unknown/orphan evidence remains and prevents a READY checkpoint. Fault injection after append preserves the unknown join.

The candidate controller retains its schema5 receipt association in addition to the operational-format bridge. CheckpointWriter coordinates both with ownership and high-water state. These are actual schema fixture adapters, not a migration of the live D09 controller or activation of its collector. Operational event forwarding and production migration require an approved versioned deployment design.

Qualified distinctions: accepted, possible-send, known terminal, delivered-at-ASGI, observation submission, receipt join, settled attempt, checkpoint ready. A successful HTTP/WS reply is not D04 completion and not next-permit authority.
