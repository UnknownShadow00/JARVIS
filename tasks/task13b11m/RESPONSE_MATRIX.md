# Response Construction Matrix

The machine-readable matrix was frozen before `app/execution/response.py` existed:

```text
tests/execution/response_matrix.json
SHA-256 f073cd7fca0f3e76d5b332a1398f06e21df5ad2febae3dc9d82d172555b47e0a
response_module=ABSENT at freeze
```

It contains one row for every actual `ObligationReason` member and records required evidence,
prohibited evidence, attribution, template family and forbidden claims. Coverage is 21 reasons,
11 obligations, and all 10 operational sources.

The preceding P6 report says 22 reasons; the implemented `ObligationReason` enum and rule table
contain 21. This discrepancy is recorded in the fixture rather than hidden or “fixed” by adding
an unauthorized reason. It does not alter the 11-member obligation contract.

The builder additionally validates exact P0 `ToolInvocation` linkage for every result-dependent
response. This strengthens the matrix's typed-result requirement and does not change any frozen
template or obligation.
