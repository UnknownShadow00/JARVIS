# Fixture scope and laundering defense

Hand-built ModelDraft/ToolProposal or hand-created canonical response JSON is synthetic test data. It may exercise canonical parsing, strict fields, cardinality, matching/mismatch or pipeline tests, but is never authentic live or provider-origin replay evidence. Seal/hash/parser success cannot upgrade its origin.

Do not accept direct server/client/UI/provider-wrapper/evaluator constructors of ModelDraft or ToolProposal as live adapter output. Current P7 has no such input field; it creates outputs only through its imported canonical parser. A fabricated recording can nevertheless pass syntax and pipeline comparison, so live input must additionally have the controlled origin chain. Never hardcode proposals from BindingProjection.expected/query, invent empty text/proposals or fake adapter status to get a pass.

Future mocks/doubles may test the live-flow association algorithm without calling a real provider; their test results stay synthetic/test evidence, not a measured-live score. No hidden fixture fallback or category relabeling after a failed provider call.
