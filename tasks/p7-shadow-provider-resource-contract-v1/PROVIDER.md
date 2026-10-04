# Approved provider selection

The operator selects local Ollama only, on 192.168.0.27, for a future separately authorized measured shadow run. No external provider, alternate local model or automatic fallback is permitted. Selection is contract intent and does not authorize a request now.

Current systemd unit points to /usr/local/bin/ollama serve; override sets OLLAMA_HOST=192.168.0.27:11434. OS socket inventory confirms that exact listener. No Ollama executable, /api/tags, /api/show, /api/ps, generation endpoint or model SDK was called. Installed-file inspection suffices for identity, not operational readiness.
