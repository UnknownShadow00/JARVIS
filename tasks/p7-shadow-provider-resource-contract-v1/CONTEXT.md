# Candidate context

The verified candidate parameter is num_ctx=64000. The operator's 64K label refers to this existing setting. It is a ceiling, not a requirement to fill every request. No context increase, history size, token budgeting rule or model reload is authorized. JARVIS owns current request/history/schema construction under D05. Exact prompt/history/schema provenance and faithful native wire normalization still need their own implementation contract; the existing recorded adapter is not an Ollama transport.
