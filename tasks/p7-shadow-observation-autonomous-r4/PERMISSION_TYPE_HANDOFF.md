# Existing decision only

Consume exact PermissionDecision, copy its existing PermissionOutcome and reject disagreement with an available stopped-state outcome. No PermissionRequest is treated as a decision. No permission engine, row_for, policy evaluation, escalation, browser D-01 resolution or confirmation mutation. Absent permission remains None rather than fabricated DENY/ALLOW.
