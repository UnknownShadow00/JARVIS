# Closed model selection

Only the selected alias may be used by a future approved shadow call. Failure does not permit OpenAI, Claude, Gemini, another Ollama model or the configured legacy model. app/brain/llm_client.py contains retry and model-substitution behavior; it is not automatically an authorized shadow transport. Its existing 600-second timeout is not selected as a shadow timeout. No synthetic empty recording may bypass unavailability.
