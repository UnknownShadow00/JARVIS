# P8 entry

P8 is **inert end-to-end conformance** (`task13b11a/IMPLEMENTATION_PHASES.md` line 24): test-only inert dispatcher fixtures, full CT-001…CT-018 against the real control plane; its input dependency is formal P7 exit. It is passive as to side effects, but requires the integrated P7 control-plane path as system under test. Recorded outputs may be test inputs (`TEST_STRATEGY.md` §4), yet recorded-only execution of the existing `run_recorded_turn` API cannot satisfy full P8 or its entry criterion. No production module or live dispatch is a P8 deliverable.

Binary entry check: P7 passive unit **PASS**; formal P7 exit **BLOCKED**; integrated server/API/UI shadow path **BLOCKED**; measured P7 shadow and CT-001/013 **BLOCKED**; current Core production/evidence verification **PASS**. Therefore **P8 entry blocked**. No independent item is uniquely a P8-entry blocker apart from the P7 exit gate; CT-001…CT-018 are P8 exit criteria.
