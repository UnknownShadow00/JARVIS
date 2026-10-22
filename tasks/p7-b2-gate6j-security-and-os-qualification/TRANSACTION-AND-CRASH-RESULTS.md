# Durable transitions and interruptions

Sequence: signed singleton succession → signed OPEN/permit approvals → durable administrative CLAIM → protected CONSUME → local D09 acceptance → BIND exact attempt ID → local possible-send → protected SEND → new one-use DISPATCH → provider → correlated native terminal → protected SETTLE with independent witness → D04 append → D09 receipt association → coordinated CHECKPOINT. TERMINATE never grants succession or reopening.

SQLite BEGIN IMMEDIATE/FULL transactions commit before acknowledgment. Nonces and attempts remain spent after failure. The new DISPATCH event is consumed against the existing pending SEND under the journal lock; it is never refunded. A claim without observed transmission remains uncertain, not proof of inference.

New tests exercise exception before/after DISPATCH commit, real child os._exit before/after commit, simultaneous dispatch claims, stop before dispatch and mismatched attempts/substeps/digests. Exactly one durable disposition remains and no crash manufactures provider work. Existing regressions cover successor/claim/permit acceptance/BIND/SEND/SETTLE crash windows, local possible-send and provider-terminal writes, D04 append-before-join, receipt join, checkpoint publication and bounded stop/drain. Supplemental socket test disconnects without reading OPEN acknowledgment, observes durable approval, rejects replay and proves admissions did not automatically open.

The false COMPLETE repair independently compares helper terminal status after TERMINATE. Inability to verify also downgrades completion. A later clean local database cannot refund an unbound accepted ordinal.

Not tested: VM power loss, hardware cache failure, hypervisor rollback, true multi-UID crash workflow or real remote-completion witness. Provider/model activity was fake throughout.
