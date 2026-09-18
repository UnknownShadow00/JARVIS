"""Offline preview of every scored turn: no model, no tool calls.

Turns whose expectation depends on a trusted tool result (TOOL_SUCCESS / TOOL_ERROR / CONFIRMATION /
AMBIGUITY from a proposed call) cannot be reproduced without the model, so they are listed as MODEL-DEPENDENT.
Every other turn is fully deterministic here and must already match its frozen expectation.
"""
import json, sys
from pathlib import Path
E = Path(__file__).resolve().parent
sys.path.insert(0, str(E))
from selftest import run_turn
from task13b10c_provenance import Ledger

scen = json.loads((E / "scenarios.json").read_text())
util = json.loads((E / "utility-expectation.json").read_text())["expectations"]
MODEL_DEPENDENT = {"TOOL_SUCCESS", "TOOL_ERROR", "CONFIRMATION", "AMBIGUITY", "MODEL_RAW"}

sessions = []
for case in scen["orig_cases"]:
    sessions.append(("orig", case["id"], case["turns"]))
for case in scen["g_cases"]:
    sessions.append(("g", case["id"], case["turns"]))
for key, suite in (("h_sessions", "h"), ("i_sessions", "i"), ("j_sessions", "j"), ("k_sessions", "k"), ("l_sessions", "l")):
    for case in scen[key]:
        sessions.append((suite, case["id"], case["turns"]))

deterministic_ok = deterministic_total = 0
for suite, sid, turns in sessions:
    led = Ledger()
    for i, prompt in enumerate(turns, 1):
        base = f"{suite}:{sid}-t{i}"
        exp = util[base]
        _, _, chosen, _, _ = run_turn(prompt, ledger=led, turn=i)
        src, text = chosen["final_user_visible_source"], chosen["visible_text"]
        model_dep = bool(set(exp["accept"]) & MODEL_DEPENDENT)
        ok = src in exp["accept"] and exp.get("require_substring", "") in text
        if model_dep:
            tag = "MODEL-DEP"
        else:
            deterministic_total += 1
            deterministic_ok += ok
            tag = "OK " if ok else "FAIL"
        print(f"{tag:9s} {base:18s} {src:24s} accept={','.join(exp['accept'])} need={exp.get('require_substring','-')}")
        print(f"          user: {prompt}")
        print(f"          resp: {text}")
print(f"\ndeterministic_turns={deterministic_total} matching_expectation={deterministic_ok}")
