# Policy table — the frozen data

The machine-readable form of `SIGNED_OFF_PERMISSION_MATRIX.md`, frozen before
`app/execution/permissions.py` was written.

* file: `policy-table.json`
* rows: **40**, keys unique
* table digest (canonical JSON, sorted keys, no whitespace):
  `8feca50e7a2c5b560e16250fb5a63093a603e3b1899c98d16302bebb43f19772`
* `policy_version`: `"1"`

Composition:

| | count |
|---|---|
| `ALLOW` | 18 |
| `REQUIRE_CONFIRMATION` | 12 |
| `DENY` | 10 |
| `READ_ONLY` | 16 |
| `REVERSIBLE_ACTION` | 8 |
| `PRIVILEGED_ACTION` | 8 |
| `DESTRUCTIVE_ACTION` | 3 |
| `EXTERNAL_COMMUNICATION` | 2 |
| `SYSTEM_POWER` | 1 |
| `FINANCIAL_PURCHASE` | 1 |
| no class (row 40) | 1 |
| registered capabilities | 31 of 40 |

Nine rows are unregistered — `files.delete`, `messaging.send`, `messaging.system_egress`,
`system.power`, `resource.control`, `finance.purchase`, `deploy.execute`, `database.status`,
`health_check` — and every one of them is `DENY`. There is no unregistered row with a permissive
outcome, which is the D-08 property stated as data rather than as code.

## Where the table lives

As a frozen module-level tuple in `app/execution/permissions.py`, not as a YAML file.

`PERMISSION_MATRIX_PLAN.md` §3.5 proposes `config/permissions.yaml`, and the task authorizes that
file "only if the signed-off plan requires a separate passive policy data file". It is **not**
created here, for one reason: a YAML table is read at import time, which is filesystem I/O inside a
component whose entire safety argument is that it is pure. The same choice was made for the router's
lexicon in 13B11H and recorded there as a deferral. The table is still data — a frozen tuple of
frozen rows, versioned by `PERMISSION_POLICY_VERSION`, hashed above, and asserted against
`policy-table.json` by test — so nothing about the "policy is data, not code" property is lost.

**Deferred, recorded here so it is not forgotten:** externalizing the table to
`config/permissions.yaml` when P5 needs operators to edit policy without a code change. That task
must keep the loader immutable, fail closed on a parse error, and keep the digest check.

## Test binding

`tests/execution/permissions_test.py` loads `policy-table.json` from the workspace copy committed
into the evidence bundle, recomputes the digest, and asserts row-for-row equality with the module's
table: same keys, same order, same class, same outcome, same registration flag, same constraints.
A row changed in the module without changing the frozen file fails the suite.
