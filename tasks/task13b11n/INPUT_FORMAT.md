# Input Format — Unresolved

13B11A names only **prompt inputs** and **tool schemas** as adapter inputs. Contract v1 says JARVIS
owns the system prompt, history and schemas. It does not define a production request type, fields,
schema serialization, mutability rule, or recorded provider-response envelope.

C5 historical evidence contains harness-level normalized records: separate draft strings and
`structured_calls` with `id`, `name`, and JSON-string `arguments`. The target map explicitly says
test-harness code is not copied, and no canonical plan designates that normalized record as the P7
production input schema.

Therefore no input dataclass, mapping convention or parser signature was invented.
