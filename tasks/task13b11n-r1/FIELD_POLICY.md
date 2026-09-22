# Field policy
| Field | Required | Null | Exact type / treatment |
|---|---|---|---|
| response.text | yes | no | string; empty allowed; never authority |
| response.proposals | yes | no | array; empty allowed; ordered |
| proposal.tool_name | yes | no | nonblank string; never normalized |
| proposal.raw_arguments | yes | no | object; empty allowed |
| raw argument child | as supplied | yes | recursive JSON data; no defaults or inference |
| caller schema JSON child | as supplied | yes | recursive JSON data, serialized only |
| caller model/turn/time/IDs | yes | no | see main contract; provider cannot supply them |
All structural unknown fields fail closed. Duplicate decoded keys fail at every depth. Nonfinite numbers and malformed JSON fail. No string/bool/number/container coercion.
Open raw data keys cannot become structural fields or authority. Reasoning-key denial applies recursively to recorded data.

