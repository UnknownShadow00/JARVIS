"""Pure deterministic self-tests for Task 13B10C3."""
from __future__ import annotations

from lane import derive_lane
from provenance_lock import select_response
from task13b10c_provenance import Ledger


def choose(prompt: str, events=None, decision="ALLOW"):
    ledger = Ledger()
    facts = ledger.ingest_user(1, prompt)
    events = events or []
    ledger.ingest_tool_events(1, events)
    frozen = {"draft_gate_decision": decision, "decision": decision, "violations": [], "allowed_trace": [], "gate_state": {}}
    return select_response(prompt, ["fabricated raw operational claim"], events, ledger, facts, frozen)


def main() -> None:
    cases = [
        ("Is the database query failing?", "OPERATIONAL", "UNVERIFIED_STATUS"),
        ("The database query failed.", "OPERATIONAL", "DECLARATIVE_ACK"),
        ("Did the service fail?", "OPERATIONAL", "UNVERIFIED_STATUS"),
        ("Verify that the service is healthy.", "OPERATIONAL", "CAPABILITY_UNAVAILABLE"),
        ("What does blue-green deployment mean?", "CONVERSATIONAL", "MODEL_RAW"),
    ]
    for prompt, lane, source in cases:
        selected = choose(prompt)
        assert selected["response_lane"]["lane"] == lane, selected
        assert selected["final_user_visible_source"] == source, selected
    event = {"tool": "jarvis_test_get_database_status", "result": {"status": "success", "database_status": "reachable", "latency_ms": 12}, "dispatcher_called": True}
    selected = choose("Check the database status.", [event])
    assert selected["final_user_visible_source"] == "TOOL_SUCCESS"
    assert selected["visible_text"] == "The database is reachable at 12 ms, sir."
    event = {"tool": "jarvis_test_deploy", "result": {"status": "confirmation_required", "executed": False}, "dispatcher_called": False}
    selected = choose("Deploy to production.", [event])
    assert selected["final_user_visible_source"] == "CONFIRMATION"
    assert "nothing has been executed" in selected["visible_text"]
    print("SELFTEST PASS")


if __name__ == "__main__":
    main()
