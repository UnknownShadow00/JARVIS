# Broker/worker source reconciliation

Use the reviewed13-file successor, not the older12-file Phase3 candidate. It retains the lifetime serial-budget reset, lock-through-receipt, fresh beacon/challenge synchronization and precredential canary/evidence corrections. All13 source pins match Unified RC1’s standalone-broker proposal exactly. The fresh71-method/305-subtest namespace run is in BROKER-TEST-RESULTS.json; no installed guest or cross-UID result is inferred.

| File | Original vs reviewed |
|---|---|
| `entry.py` | changed/added; reviewed successor packaged |
| `g6k_serial/__init__.py` | byte-identical |
| `g6k_serial/broker.py` | changed/added; reviewed successor packaged |
| `g6k_serial/hardening.py` | byte-identical |
| `g6k_serial/journal.py` | changed/added; reviewed successor packaged |
| `g6k_serial/policy.py` | byte-identical |
| `g6k_serial/preissuance.py` | changed/added; reviewed successor packaged |
| `g6k_serial/protocol.py` | changed/added; reviewed successor packaged |
| `g6k_serial/provision.py` | changed/added; reviewed successor packaged |
| `g6k_serial/runtime.py` | changed/added; reviewed successor packaged |
| `g6k_serial/securefs.py` | changed/added; reviewed successor packaged |
| `g6k_serial/transport.py` | changed/added; reviewed successor packaged |
| `g6k_serial/worker.py` | changed/added; reviewed successor packaged |

RC1 has no live broker adapter; JARVIS36-character task UUIDs and32-hex broker IDs have no implicit bridge. The installed serial-candidate tree is dormant source/examples/tests only. Existing worker/broker setup, credentials, roles, units and activation remain separately authorized.
