# Dependency-ordered next decision

Re-read the original OPERATOR-DECISIONS.md after freeze: D03 is resolved only for this observational producer contract. The next smallest downstream decision is **D04 — separate evidence sink, clock/timing and failure/loss accounting contract**, including pre-terminal/no-turn failures and delivery accounting. It is needed before this record can support complete scored measurement. No sink path, timing field or loss semantics is selected here.

D05 authentic current-turn adapter input is an independent branch before any real-traffic evaluation; D06 provider/resource and D07 evaluator/scheduler remain prerequisites to its runtime use. D01/D02 session/retry semantics and D10 exact implementation/test budget remain prerequisites to wiring. D08/D09 remain final-acceptance blockers. Stop after this freeze; do not start any of these units or implement runtime without a separate instruction.
