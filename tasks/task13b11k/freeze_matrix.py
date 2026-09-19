"""Generate the frozen 13B11K dispatcher decision matrix.

Run before the module exists. The JSON it writes is hashed and sealed, and the
scored test drives every cell against the real dispatcher and the real
confirmation store and compares field by field.
"""
from __future__ import annotations

import json
import pathlib

PERMISSION = ("ALLOW", "REQUIRE_CONFIRMATION", "DENY")

# How the confirmation side of the attempt was set up.
CONFIRMATION = (
    "absent",            # the invocation carries no confirmation id
    "binding_absent",    # confirmation id present, no binding mapping supplied
    "authority_absent",  # binding supplied, no confirmation authority injected
    "valid_pending",     # fresh PENDING record, exact 12-field binding, right session
    "wrong_session",     # record exists, a different session asks
    "wrong_binding",     # one bound value differs
    "expired",           # freshness window already passed
    "denied",            # record is DENIED
    "cancelled",         # record is CANCELLED
    "already_claimed",   # record is EXECUTING — this authority was used already
)

EXECUTOR = ("success", "error", "timeout", "exception", "contract_violation")

# Frozen mapping from an executor outcome to the trusted result, used only when
# every authority gate passed and the executor was actually invoked.
EXECUTED = {
    "success":            ("SUCCESS", None,                          "SUCCEEDED"),
    "error":              ("ERROR",   "executor_error",              "FAILED"),
    "timeout":            ("TIMEOUT", None,                          "EXECUTING"),
    "exception":          ("ERROR",   "executor_exception",          "FAILED"),
    "contract_violation": ("ERROR",   "executor_contract_violation", "FAILED"),
}

# A refusal that happens before the executor. Kind -> (status, gate).
REFUSAL = {
    "invocation_inconsistent":           ("BLOCKED", 2),
    "permission_denied":                 ("BLOCKED", 4),
    "confirmation_absent":               ("CONFIRMATION_REQUIRED", 5),
    "confirmation_binding_absent":       ("CONFIRMATION_REQUIRED", 5),
    "confirmation_authority_unavailable": ("CONFIRMATION_REQUIRED", 5),
    "confirmation_not_found":            ("CONFIRMATION_REQUIRED", 6),
    "confirmation_not_pending":          ("CONFIRMATION_REQUIRED", 6),
    "confirmation_expired":              ("CONFIRMATION_REQUIRED", 6),
    "confirmation_binding_mismatch":     ("CONFIRMATION_REQUIRED", 6),
    "invocation_already_dispatched":     ("BLOCKED", 6),
}

# What the confirmation record looks like after a refusal, per setup. "n/a" means
# no record exists for this setup at all.
AFTER_REFUSAL = {
    "absent": "n/a",
    "binding_absent": "PENDING",
    "authority_absent": "PENDING",
    "valid_pending": "PENDING",
    "wrong_session": "PENDING",
    "wrong_binding": "PENDING",
    "expired": "EXPIRED",      # the store expires a stale record on access
    "denied": "DENIED",
    "cancelled": "CANCELLED",
    "already_claimed": "EXECUTING",
}

CONFIRMATION_REFUSAL_KIND = {
    "binding_absent": "confirmation_binding_absent",
    "authority_absent": "confirmation_authority_unavailable",
    "wrong_session": "confirmation_not_found",
    "wrong_binding": "confirmation_binding_mismatch",
    "expired": "confirmation_expired",
    "denied": "confirmation_not_pending",
    "cancelled": "confirmation_not_pending",
    "already_claimed": "confirmation_not_pending",
}


def cell(permission: str, confirmation: str, executor: str) -> dict:
    has_confirmation_id = confirmation != "absent"

    # Gate 2 — the invocation must carry a confirmation id exactly when the
    # settled permission outcome is REQUIRE_CONFIRMATION.
    if permission != "REQUIRE_CONFIRMATION" and has_confirmation_id:
        kind = "invocation_inconsistent"
    elif permission == "REQUIRE_CONFIRMATION" and not has_confirmation_id:
        kind = "confirmation_absent"
    elif permission == "DENY":
        kind = "permission_denied"
    elif permission == "ALLOW":
        kind = None
    elif confirmation == "valid_pending":
        kind = None
    else:
        kind = CONFIRMATION_REFUSAL_KIND[confirmation]

    if kind is None:
        status, error_kind, after = EXECUTED[executor]
        if permission == "ALLOW":
            after = "n/a"
        return {
            "permission_outcome": permission,
            "confirmation": confirmation,
            "executor": executor,
            "executor_called": True,
            "result_status": status,
            "error_kind": error_kind,
            "executed": True,
            "facts_source": "executor" if status == "SUCCESS" else "none",
            "confirmation_state_after": after,
            "gate_reached": 7,
        }

    status, gate = REFUSAL[kind]
    after = "n/a" if permission != "REQUIRE_CONFIRMATION" else AFTER_REFUSAL[confirmation]
    return {
        "permission_outcome": permission,
        "confirmation": confirmation,
        "executor": executor,
        "executor_called": False,
        "result_status": status,
        "error_kind": kind,
        "executed": False,
        "facts_source": "none",
        "confirmation_state_after": after,
        "gate_reached": gate,
    }


cells = [
    cell(p, c, e) for p in PERMISSION for c in CONFIRMATION for e in EXECUTOR
]

# Replay: a second dispatch of an invocation whose id was already claimed. The
# executor count never rises above one, whatever the first outcome was.
replay = [
    {
        "first_outcome": first,
        "second_attempt_executor_called": False,
        "second_attempt_result_status": "BLOCKED",
        "second_attempt_error_kind": "invocation_already_dispatched",
        "second_attempt_executed": False,
        "total_executor_calls": 1,
    }
    for first in ("success", "error", "timeout", "exception", "contract_violation")
]

document = {
    "task": "13B11K",
    "component": "app/execution/dispatch.py",
    "matrix_version": "1",
    "dimensions": {
        "permission_outcome": list(PERMISSION),
        "confirmation": list(CONFIRMATION),
        "executor": list(EXECUTOR),
    },
    "gate_order": [
        "1 input and type validity",
        "2 invocation structural validity (dispatchable action, ids, confirmation pairing)",
        "3 canonicalization metadata consistency",
        "4 settled permission outcome",
        "5 confirmation requirement (id, binding, authority present)",
        "6 confirmation binding, ownership, freshness and the atomic execution claim",
        "7 executor invocation",
    ],
    "refusal_representation": "TrustedToolResult with BLOCKED or CONFIRMATION_REQUIRED and executed=false",
    "cell_count": len(cells),
    "cells": cells,
    "replay": replay,
}

out = pathlib.Path(__file__).with_name("dispatch-matrix.json")
out.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n")
print(f"wrote {out} with {len(cells)} cells and {len(replay)} replay rows")
