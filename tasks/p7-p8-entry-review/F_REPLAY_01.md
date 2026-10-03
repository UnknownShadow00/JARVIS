# F-REPLAY-01

Source: `task13b11o-r1/FOLLOWUPS.md` row F-REPLAY-01 and `task13b11p-r1/S08_S09_CONTRACT.md` lines 128–130. This is transport/cancellation loss after a live executor may have been entered but before a result is received. Absence of a result cannot establish `executed=False`; retry needs explicit idempotency/evidence.

Frozen P7 mode C consumes an existing linked result and resumes after dispatch (`task13b11p-r1/RESULT_REPLAY.md`); passive P8 checks of that behavior do not need a live lost-result path. F-P7R1-02 is different: an already available refusal result for a non-dispatchable action is excluded by v1 guard C-00a because obligation priority was unsigned. Neither scope is widened here.
