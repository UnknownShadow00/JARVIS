# JARVIS Task Queue

- [x] Phase 0 - Core brain complete (FastAPI + router + tools + kill switch)
- [x] Phase 1 scaffold - voice + boot modules built and unit-tested
- [x] Install Piper model files and run manual hardware smoke tests
- [x] Validate unattended voice pipeline order with wake/PTT, STT, response, streaming TTS, and stop path mocked
- [ ] Run attended spoken live voice loop test with real wake word/PTT, STT, response, TTS playback, and kill-switch
- [x] Push Phase 0 + Phase 1 checkpoint to GitHub
- [x] Document voice clone as intentionally skipped until a real private 10-second WAV exists
- [x] Prepare 5090 migration runbook and 4070 Ti to 5090 config notes

## Phase 4+ early track

- [x] Dictation mode in `app/voice/push_to_talk.py` - separate hotkey routes STT to clipboard/type-out instead of the brain pipeline
- [x] Obsidian vault + optional obsidian-mcp handoff - constrained note CRUD/search in `jarvis-vault/`
- [x] Embedding-based tool selection second pass in `app/brain/router.py` - feature-flagged, default OFF
- [x] Graphiti + Neo4j temporal knowledge graph - docker-compose service + `app/memory/graphiti_client.py`, feature-flagged default OFF

## Pre-Proxmox local finish queue

- [ ] Run attended live voice loop test with microphone, speakers, PTT/wake, response, TTS playback, and kill-switch.
- [ ] Run live web search smoke test with network available.
- [ ] Run Ollama vision smoke test with the configured `models.vision` model pulled.
- [ ] Decide whether to keep browser-use as plan-only or enable live browser-agent automation behind confirmation gates.
- [ ] Validate Graphiti against a live Neo4j container after Docker is available locally or on the server host.
