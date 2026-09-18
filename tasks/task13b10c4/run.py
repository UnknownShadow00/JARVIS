"""Execute the frozen C2 collector with only C4 evidence/lane/suite wiring changed.

The large Hermes integration collector is retained byte-for-byte as
task13b10c2-run-base.py.  Exact guarded substitutions make the collection
path auditable while avoiding a fork of unrelated runtime logic.
"""
from __future__ import annotations

from pathlib import Path


base = Path(__file__).with_name("task13b10c2-run-base.py").read_text()
replacements = {
    'assert SUITE in ("orig", "g", "h", "i") and 1 <= REP <= 5 and ATTEMPT >= 1':
        'assert SUITE in ("orig", "g", "h", "i", "j", "k") and 1 <= REP <= 5 and ATTEMPT >= 1',
    'EVIDENCE = Path("/home/jarvis/.hermes-poc/evidence/task13b10c2-response-selector")':
        'EVIDENCE = Path("/home/jarvis/.hermes-poc/evidence/task13b10c4-action-routing")',
    'HOME = Path("/home/jarvis/.hermes-poc/task13b10c2-home-granite")':
        'HOME = Path("/home/jarvis/.hermes-poc/task13b10c4-home-granite")',
    'PHASE_FILE = Path("/tmp/task13b10c2-current-phase")':
        'PHASE_FILE = Path("/tmp/task13b10c4-current-phase")',
    '"i": "i_sessions"}[SUITE]':
        '"i": "i_sessions", "j": "j_sessions", "k": "k_sessions"}[SUITE]',
    '"i": (7, 10)}[SUITE]':
        '"i": (7, 10), "j": (10, 10), "k": (12, 12)}[SUITE]',
    '"task": "13B10C2"':
        '"task": "13B10C4"',
    '"response_need_class": g["response_need_class"],':
        '"response_need_class": g["response_need_class"], "response_lane": g["response_lane"],',
    '"response_candidates": g["response_candidates"], "selected_candidate": g["selected_candidate"],':
        '"response_candidates": g["response_candidates"], "selected_candidate": g["selected_candidate"], "final_user_visible_source": g["final_user_visible_source"], "shadow_detector_reviews": g["shadow_detector_reviews"],',
}
for old, new in replacements.items():
    count = base.count(old)
    if count != 1:
        raise RuntimeError(f"base collector drift for substitution {old!r}: count={count}")
    base = base.replace(old, new)
exec(compile(base, str(Path(__file__).with_name("task13b10c2-run-base.py")), "exec"))
