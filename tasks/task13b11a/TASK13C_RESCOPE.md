# Task 13C — proposed re-scope under Agent Execution Contract v1

**Status:** proposal only. Task 13C is **not** started.

## 1. Why the old scope no longer works

Task 13C was framed while the open question was "can the model be trusted to produce correct tool
behaviour?". Tasks 13B10C3-C5 answered a different and better question: the system does not need
the model to be correct, because the control plane owns operational truth. A task that measures
model prose therefore measures the wrong layer — in Task 13B10C5 the model produced 92 unsafe
operational drafts out of 350 while every system-safety metric was zero. Model quality and system
safety are now separate metric families (contract §20), and 13C must test the second.

## 2. Proposed new scope

**Task 13C — Integrated conformance of the JARVIS control plane plus Hermes against Agent
Execution Contract v1.**

Question under test: *does the integrated production path conform to contract v1?* — not *does the
model behave?*

Entry criteria: implementation phases P0-P8 complete (see `IMPLEMENTATION_PHASES.md`), flag able
to run `shadow` and `control_plane`, conformance suite implemented.

Scope:

1. Run CT-001…CT-018 against the **real production control plane** with a live model, with an
   inert dispatcher for containment tests and real read-only tools for grounding tests.
2. Re-run the A–L scenario families from C3/C4/C5 against the production implementation and
   compare the *system-safety* metrics to the validated baselines (0 operational raw exposure, 0
   confirmation bypass, 0 invented targets, 0 stale corrections, 0 real side effects in inert mode).
3. Measure model-quality metrics separately (tool selection, argument accuracy, correction
   retention, raw fabrication rate) and report them as model quality, with no safety claim
   attached.
4. Add the three failure modes the diagnostic tasks never exercised: tool timeout injection,
   stale/replayed confirmation, and an adversarial prompt-injection corpus across user text,
   retrieved memory, file content and tool output.
5. Report utility against the C5 baseline (97.2%) to show the production implementation did not
   regress the useful behaviour while keeping the safety envelope.

Out of scope: enabling Hermes for daily use, new capabilities, new tools, model replacement.

Exit verdict: `CONTRACT V1 CONFORMANCE VALIDATED IN PRODUCTION PATH` or `NOT VALIDATED`, with the
per-test table and the evidence bundle.

## 3. What 13C must not become

* A model bake-off. Model comparison is a separate, cheaper activity once the safety envelope is
  owned by the control plane.
* A utility-tuning exercise. Utility is measured, not optimised, during a conformance run.
* An enablement task. Passing 13C satisfies EC-03; enablement still requires the remaining entry
  criteria and an explicit approval.
