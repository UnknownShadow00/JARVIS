# Target schemas

| V1 row | Field | Type / required | Canonical form | Validation owner and source | Raw user target allowed? | Model may populate? |
|---|---|---|---|---|---|---|
| OPEN_APP→`apps` | `app` | exact `str`, required, nonempty | P3 `canonicalize("apps", ...)` field `app`; current declared VS Code alias only | P3 resolved `RouteResult.target`; V1 binder checks canonical value is an exact `_APP_MAP` key from passive metadata snapshot | yes, only through deterministic P3 route | **no** |
| OPEN_URL→`browser` | `url` | exact `str`, required, nonempty | unchanged by P3 V1 canonicalizer | P3 `OPEN_URL` whole-operand target; V1 binder enforces absolute lowercase HTTP(S), host, no whitespace/control or userinfo per P4 row 12 | yes, only through deterministic P3 route | **no** |

The target carried in `PermissionRequest.target` remains the exact route target, including pre-canonical app alias. `PermissionRequest.canonical_target` is the canonical target argument. Neither is taken from a `ToolProposal`. App key membership is a conservative, current-source restriction; the handler's additional `.lower().strip()` is not duplicated as a second normalizer. Browser validation performs parsing only, no fetch/DNS/redirect check; any later live execution needs its separate network/egress policy review. Ambiguous or unresolved target produces no expected executable binding.
