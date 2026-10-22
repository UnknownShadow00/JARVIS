# Authority bypass experiments

Two failing tests on unchanged Gate6I runtime code reached the fake provider through direct OwnedProvider and NativeTransport invocation after a local possible-send row, without a protected SEND. Evidence: runs/redteam-before (2 failures). Both are repaired by a durable native-seam DISPATCH claim referencing the existing pending SEND, resource, accepted attempt and exact local substep. Reusing the claim, conflicting IDs/digest, stop approval and lost acknowledgment refuse; no new provider call is made.

A passed connection was also accepted from a different actual PID under the connector's SO_PEERCRED. runs/delegated-before preserves the failure. Per-message SCM_CREDENTIALS now checks each writer. Numeric client UID/PID fields remain rejected. Actual cross-UID execution is NOT RUN.

runs/terminal-before demonstrates protected INCOMPLETE while local/runtime claimed COMPLETE after protected consumption but before D09 join. Readback now propagates the conservative protected outcome. None of these tests used a real model or a production controller.

The protected journal now also rejects a classifier SEND on ordinal2 and more than11 total SENDs. This enforces the already proposed four original inputs/conditional-operation budget at the protected boundary; it does not approve X11. The real runtime's rules-first second turn already omitted classification.
