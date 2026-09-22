# Task 13B11M — Implementation

## Scope

Production phase P6 unit 2 adds the passive deterministic operational-response builder at
`app/execution/response.py`. It is not imported by a live production module and does not alter
`execution.mode: legacy`, either Hermes flag, the legacy response path, a registry, a tool, or an
audit writer.

Production commit:

```text
4885c4f7ca35f2395fab3497e6ce009d36b742be
parent 8a70d179c527f2912522920918f70a68ee213386
feat: add deterministic operational response builder
```

## Shape

`ResponseBuildInput` carries only settled structured state:

- the existing `ObligationDecision` and `ObligationState`;
- exact current `ToolInvocation` / `TrustedToolResult` linkage when a response depends on a
  current result;
- exact historical invocation/result/provenance linkage for a tool-observed ledger value;
- exact `ProvenanceRecord` values, expected fact key, session and correlation metadata;
- a caller-supplied aware timestamp.

`build()` validates that the supplied decision is the highest-priority satisfied decision from
the frozen obligation rules. It never calls `derive()` or `require()` and never substitutes a
different obligation. It then selects one frozen template and returns the existing P0
`ApprovedOperationalResponse` unchanged.

## Files

Production changed eight files: one new module, six new focused test/fixture files, and one
narrow update to the P6-unit-1 non-activation test so its sole permitted passive consumer is
`app/execution/response.py`. No frozen ancestor production module was edited.

## Results

- focused P6 response/obligation slice: 169 passed;
- full suite: 5,245 passed, 11 deselected, 0 failed;
- golden: 12/20, same eight known failures;
- legacy probe: `fc68a0b041c8d0d41f446e9638cae5f888e4f4f6caf84d438ca0e11a30d98291`;
- static security review: 19/19;
- 24/24 critical files byte-identical to the entry commit;
- zero live importers.
