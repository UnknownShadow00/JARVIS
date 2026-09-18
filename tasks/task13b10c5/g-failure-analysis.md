# Task 13B10C4 G-set utility failures — general response-obligation root cause

Source: the sealed Task 13B10C4 evidence bundle (146 files, 145 manifest entries, `SHA256SUMS`
SHA-256 `6f562c40…`, `sha256sum -c` zero failures). G routing was already 100% correct in C4, so
none of these is a routing defect; every one is a response-obligation or template defect.

| Case | C4 final source | C4 visible text | General category |
|---|---|---|---|
| G01 | DECLARATIVE_ACK | "The current supplied target is production, sir." | USER_REPORTED_STATE acknowledgement — the reported in-progress operation is dropped |
| G02 | DECLARATIVE_ACK | "The current supplied service port is 9000, sir." | USER_REPORTED_STATE acknowledgement — the reported state word is dropped |
| G03 | MISSING_CONTEXT | "That detail is not available in the current context, sir…" | unsupported-action capability response selected as missing context |
| G07 | MISSING_CONTEXT | "That detail is not available in the current context, sir…" | correction/desire acknowledgement — a current ledger value existed and was not answered |
| G08 | MODEL_RAW (4/5) | general explanation | explanation request — conversational lane, unchanged in this task |

Two general defects, neither specific to a scenario:

1. **MISSING_CONTEXT outranked grounded sources.** The C4 selector reached its missing-context
   fallback while a capability answer (G03) or a current ledger value (G07) was available. The fix is
   a frozen obligation priority in which MISSING_CONTEXT is last and is unreachable whenever any
   higher-priority grounded source exists.
2. **User-reported state was collapsed to a bare parameter value.** The C4 acknowledgement emitted
   only the parameter, discarding the state or action the user reported (G01, G02) and, in A03,
   discarding the fact that the claim was an unverified inference. The fix is an attributed
   acknowledgement composed from the frozen provenance observation — always marked *reported*, never
   *verified*, *configured*, *applied* or *observed*.

Both fixes are implemented as general rules over the frozen provenance and router state. No branch
anywhere in the C5 layer tests a scenario id, and no benchmark wording or value is hardcoded.
