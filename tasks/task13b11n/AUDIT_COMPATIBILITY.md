# Audit Compatibility

Schema v3 remains unchanged and no event was emitted. Existing passive audit vocabulary can later
carry a raw model proposal and a digest/redacted model-draft reference, but it does not settle the
adapter's raw envelope, retention boundary, or reasoning-field removal point.

The eventual adapter contract must preserve enough untrusted representation for deterministic
validation and future passive audit samples without retaining private reasoning or entire prompt
history. No audit writer or provenance ledger was accessed.
