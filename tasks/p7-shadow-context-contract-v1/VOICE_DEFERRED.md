# Voice is inventoried, deferred

`app/voice/audio_stream.py:68-113` handles transcription and calls _process_stream, then _process on fallback. Dictation follows another branch. It does not traverse REST/WS capture ownership. No voice turn, session, snapshot, trace or shadow coverage is claimed. A later voice contract should reuse the same JARVIS identity model; no voice wiring occurs here.
