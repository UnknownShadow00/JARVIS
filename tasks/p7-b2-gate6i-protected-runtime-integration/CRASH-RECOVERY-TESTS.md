# Crash and concurrency qualification

New runtime tests inject failures before/after protected CLAIM, ACCEPT, BIND, SEND, SETTLE and CHECKPOINT commits. Fresh child processes terminate with os._exit at CONSUME/BIND/SEND/SETTLE before/after commit; reopened reads prove zero or one durable event, never manufactured success. Gate6H subprocess successor/permit/send/settle tests remain in the full suite.

Controller faults cover local possible-send commit, provider terminal commit, receipt append before join and receipt join. Coordinated publication faults cover before/after directory publication. These failures retain accepted ordinals and block a next permit. Lost SEND acknowledgment leaves pending intent before any provider call. Missing terminal witness refuses settlement. Stop during a blocked provider preserves both protected pending intent and D06 remote unknown.

Concurrency covers operator permit races, service consumption races, concurrent reads, bounded worker admission and inherited successor races. The listener shutdown race found during testing was fixed without weakening its assertion. Actual partial-read/nonreading shutdown, broken pipes, process identity drift and journal reopen/replay are covered.

Reopen is not authority to reopen an epoch. New service/helper/operator process identities need explicit provisioning; terminal state is monotonic, COMPLETE may downgrade to INCOMPLETE, never the reverse. No process crash or timeout refunds an attempt. Whole-host power-cut tests and genuine UID separation were not run.

Initial test-authoring and later engineering/environment failures are retained in evidence/runs with their source identities. No failing assertion was removed or marked skipped. TEST-RESULTS.md distinguishes intermediate revisions and the final suite.
