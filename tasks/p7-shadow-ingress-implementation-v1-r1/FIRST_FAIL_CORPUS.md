# Pre-code focused corpus

No prior ingress corpus existed in the sealed blocked attempt. A new executable corpus and expected PASS outcomes were frozen before production code/test edits, along with the exact authorization. 64 parameterized cases, including 52 security cases.

Frozen source SHA256: `fd2cb95fe3fade3b967df55dd1768e12323d47b49ed51bdab88a2c2088aa2ed5`. Core path: `first-fail-corpus/shadow_ingress_test.py`. The production test remains byte-identical to that frozen source. `pre-code-freeze.sha256` covers executable source and expectations; final verification passes.

First scored frozen run: 64 failures due to absent shadow_ingress, before implementation. First implementation run: 64 new cases plus the authorized structural gate = 65 passed. Neither expectations nor implementation nor frozen tests were changed after that run. Supplemental proof/security variants are separate, not retrospectively frozen cases.

Before freeze, collection caught pytest's reserved `request` parameter name; it was renamed to `raw_text` before outcomes/hash were frozen. Original harness and error are retained. The initial verification helper also used system Python without pydantic; it was corrected to the existing venv before coding. No package installation, production change or altered acceptance expectation followed either setup correction.
