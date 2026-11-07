"""Optional parent-run harness. Never run outside the parent-approved cage.

Run sequentially against snapshot-final mounted at /input, with all target/tooling
read-only, no network, an empty allowlisted environment and bounded /work scratch.
Suggested output: final-registry-controls.txt, maximum 262144 bytes, promoted only
by the trusted parent after the cage and its children terminate. This file is a
proposal, not execution evidence.
"""
import sys

sys.path[:0] = ['/input', '/input/tests', '/deps']

import pytest

tests = [
    'test_restore_proposal_decision_receipt_restart',
    'test_forged_receipts[wrong_key]',
    'test_checkpoint_key_cannot_forge_operator_authorization_on_restart',
    'test_witness_expiring_during_expensive_derive_never_publishes',
    'test_proposal_context_expiring_during_derive_never_publishes',
    'test_predecessor_expiring_during_derive_never_publishes',
]

raise SystemExit(pytest.main([
    '-q', '-p', 'no:cacheprovider', '--basetemp=/work/final-registry-tmp',
    *['/input/tests/test_recovery_decisions.py::' + name for name in tests],
]))
