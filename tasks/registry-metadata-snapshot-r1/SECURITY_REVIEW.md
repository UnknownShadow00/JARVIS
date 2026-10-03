# Security review

| Boundary | Finding |
|---|---|
| Callable, bound method, handler, registry, mutable reference | None in returned recursive value graph |
| `registry.call`, handler execution, dispatch, network, subprocess | No import/call edge; runtime sentinel zero |
| Model/client metadata injection | Public factory has no parameters; injected arguments raise `TypeError` |
| Fake manually constructed snapshot | Type identity alone insufficient; future binder must verify digest/reviewed rows |
| Duplicate/ambiguous declarations | Explicit failure in isolated fixtures |
| Unknown valid entry | Does not become a V1 admitted row; source drift blocks runtime use |
| Nondeterministic order or mutation | Sorted tuples and repeatability/immutability tests pass |
| Hidden consumer | Production source scan zero; only tests import |

Authority bypasses observed: **0**. No audit or permission schema changed. `pip-audit`/Bandit were unavailable in the Core environment; no packages were installed and no network audit was attempted.
