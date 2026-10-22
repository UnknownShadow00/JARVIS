# Protected transactions

Gate6K does not redesign or alter authority/runtime logic. Focused regressions re-exercise Gate6J's singleton signed succession; nonce persistence; signed OPEN/CLAIM; durable one-use CONSUME before D09; exact BIND; protected SEND and one-use DISPATCH before fake provider work; terminal witness association; D04/D09 joins and checkpoint; truthful incomplete stop. Accepted attempts are never refunded, including lost acknowledgment. Four global attempts and original REST/REST/WS/WS order remain.

The future distinct-UID runner prepares a synthetic predecessor, concurrent signed successor race, CLOSED attach, signed OPEN with dropped response, signed permit/replay, concurrent consume, protected possible-send/fake blocked provider, uncertain D06/terminal and rollback. Invalid/expired operator signatures must leave the protected journal unchanged. Synthetic signing keys remain in operator-owned0700/key0600 storage.

Actual multi-UID transaction execution: NOT RUN. The current fixture scenario consumes one attempt then deliberately enters uncertainty. The logical supplement tests four-attempt exhaustion and receipt/checkpoint boundaries; it is not a four-UID positive settlement attestation. Independent terminal-completion witness and actual production topology remain unavailable. No unsigned claim of remote completion is introduced to make that scenario pass.

A missing response is not failure proof. A possible-send record is not proof inference occurred. Local timeout/cancellation/disconnect does not terminate remote inference. No retry/fallback/next permit is automatic. No production predecessor, successor or permit is signed or mutated.
