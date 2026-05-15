# JARVIS Task Queue

- [x] Phase 0 — Core brain complete (FastAPI + router + tools + kill switch)
- [x] Phase 1 scaffold — voice + boot modules built and unit-tested
- [x] Install Piper model files and run manual hardware smoke tests
- [x] Validate unattended voice pipeline order with wake/PTT, STT, response, streaming TTS, and stop path mocked
- [ ] Run attended spoken live voice loop test with real wake word/PTT, STT, response, TTS playback, and kill-switch
- [x] Push Phase 0 + Phase 1 checkpoint to GitHub
- [x] Document voice clone as intentionally skipped until a real private 10-second WAV exists
- [x] Prepare 5090 migration runbook and 4070 Ti to 5090 config notes

## Phase 4+ early track (started 2026-05-14)

- [ ] Dictation mode in app/voice/push_to_talk.py — separate hotkey routes STT to clipboard/type-out instead of brain pipeline
- [ ] Obsidian vault + obsidian-mcp tool — new app/tools/obsidian.py, whitelist update in mcp_client.py, jarvis-vault/ folder
- [ ] Embedding-based tool selection second pass in app/brain/router.py — feature-flagged, default OFF
- [ ] Graphiti + Neo4j temporal knowledge graph — docker-compose service + app/memory/graphiti_client.py, feature-flagged default OFF
