# Offline provenance packet

Read `FINAL-REPORT.md` and its final evidence reference. Earlier evidence is
preserved to show inspector corrections and concurrent workspace observations.

Reproduce the bounded byte inspection from the project root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 tasks/jarvis-offline-provenance-r1/inspect_provenance.py
PYTHONDONTWRITEBYTECODE=1 python3 tasks/jarvis-offline-provenance-r1/test_inspector.py
```

The inspector creates a new exclusive timestamped evidence file. Reproduction
changes this packet's inventory and therefore requires a new successor seal; do
not overwrite or reinterpret the existing SHA256SUMS as covering future files.
These commands do not import or execute inspected application/package payloads.

`SHA256SUMS` covers all current packet files except itself. It is a byte-integrity
record and provides no operator authorization.
