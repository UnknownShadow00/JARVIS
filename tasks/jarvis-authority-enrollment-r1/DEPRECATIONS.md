# Retained dependency warning investigation

The final full-app run retains two upstream TestClient warnings: Starlette1.6.0
prefers absent httpx2 and warns when falling back to retained httpx0.28.1; its
BlockingPortal annotation also uses the alias deprecated by AnyIO4.15.1. Current
retained package source hashes were rechecked as data against the prior packet;
[DEPRECATIONS.json](DEPRECATIONS.json) records them. Neither source is application
code. The exact28 dependency target is unchanged/read-only. No installation,
network lookup, package patch or warning filter was used. A newly verified offline
compatibility closure is still the appropriate dependency follow-up.

The27 stderr startup lines are nine sets of absent Piper binary/model and isolated
loopback Ollama unreachable checks. No real provider/model request occurred. IPv4/
IPv6 unreachable canaries are asserted before imports; synthetic configurations
and every original stdout/stderr are retained. These warnings are inspected and
reported, not suppressed or described as a production readiness pass.
