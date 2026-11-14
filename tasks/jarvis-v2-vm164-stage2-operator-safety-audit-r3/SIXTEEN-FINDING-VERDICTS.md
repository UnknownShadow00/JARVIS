# Sixteen original finding verdicts

All sixteen original unsafe R2 outcomes were independently reproduced from the untouched preceding Astra source. The corrected R3 predicates reject the fifteen corresponding unsafe inputs; required `/` inspection succeeds. **PASS below is deliberately limited to the named original reproduction. It is not a verdict that the broader causal/evidence requirements are complete**; six new finding groups still require REJECT.

| ID | Original defect | R2 reproduction | R3 original-reproducer verdict |
|---|---|---|---|
| ASTRA-16-01 | Stale collision proof | FAIL reproduced | **PASS** |
| ASTRA-16-02 | Failed service accepted as cancellation | FAIL reproduced | **PASS** |
| ASTRA-16-03 | Changed privilege review without resealing | FAIL reproduced | **PASS** |
| ASTRA-16-04 | Timed-out collision evidence | FAIL reproduced | **PASS** |
| ASTRA-16-05 | Creation receipt after deadline | FAIL reproduced | **PASS** |
| ASTRA-16-06 | Duplicate after callback firing | FAIL reproduced | **PASS** |
| ASTRA-16-07 | Contradictory ExecStart exit | FAIL reproduced | **PASS** |
| ASTRA-16-08 | Invocation after failed timer | FAIL reproduced | **PASS** |
| ASTRA-16-09 | Journal before session | FAIL reproduced | **PASS** |
| ASTRA-16-10 | Callback after authorization expiry | FAIL reproduced | **PASS** |
| ASTRA-16-11 | Legitimate root-directory inspection | FAIL reproduced | **PASS** |
| ASTRA-16-12 | Missing raw cgroup capture | FAIL reproduced | **PASS** |
| ASTRA-16-13 | Stale cancellation journal | FAIL reproduced | **PASS** |
| ASTRA-16-14 | Failed service reported successful | FAIL reproduced | **PASS** |
| ASTRA-16-15 | Stale cleanup readback | FAIL reproduced | **PASS** |
| ASTRA-16-16 | Stop receipt after cancellation deadline | FAIL reproduced | **PASS** |

The original 51 methods are in tests/ORIGINAL-ASTRA-PROBES.py. R2 was run first through its untouched independent runner: 35 pass/16 fail. The independent R3 replay imports those original methods and substitutes a valid new-schema positive fixture plus an independently implemented envelope/sealer. Only two input adapters are necessary: the old null/0 ExecStart trailer mutation now targets exited/0, and the missing-raw test explicitly removes the raw fields now present in the R3 seed. Assertions remain unchanged; exact adapter diff is retained. Literal old-format bytes are not misrepresented as a valid R3 control.

The independently ported original 51 methods pass, with a passing full twelve-case positive control and recorded validator calls/reasons. Time mutations with internally consistent receipt finishes were additionally tested independently (late creation, stale raw capture, late cancellation acknowledgment and post-expiry callback); all reject. Correctly bound canceled callback evidence also rejects. The R21 original probe runs only the lexical prefix; the replayed descriptor tests separately check ownership, permissions and symlink restrictions against fake objects, never the host.

Original before failures are matched by method identity in evidence/ORIGINAL-R2-NEGATIVE-RESULTS.json. Per-method after outcomes and calls are in evidence/ORIGINAL-METHODS-R3.json and SIXTEEN-FINDING-VERDICTS.json. Original fixes are real, but waiting/completion/invocation and finer timestamp bypasses show that broader root-cause coverage is still partial.
