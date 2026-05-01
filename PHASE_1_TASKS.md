# JARVIS — Phase 1 Build Tasks for Claude Code

> Only start Phase 1 after ALL Phase 0 acceptance criteria pass.
> Read CLAUDE.md before starting. Update "Current Status" when done.

---

## Before You Start

1. Confirm Phase 0 is 100% complete (all tests passing)
2. Verify CUDA is working: `python -c "import torch; print(torch.cuda.is_available())"`
3. Verify faster-whisper GPU works: `python -c "from faster_whisper import WhisperModel; m=WhisperModel('tiny', device='cuda'); print('GPU STT OK')"`
4. Download Piper binary for Windows from: `github.com/rhasspy/piper/releases`
5. Download jgkawell/jarvis ONNX model from: `huggingface.co/jgkawell/jarvis`
   - Download `jarvis.onnx` and `jarvis.onnx.json` to `./models/`

---

## Task 1.1 — Build the TTS engine

**File:** `voice/tts.py`

Build a streaming TTS engine that:
- Supports Piper and Kokoro (switch via `settings.voice.tts_engine`)
- **CRITICAL: Streams audio — starts playing before full text is generated**
  - Split response into sentences
  - Synthesize and play sentence 1 while sentence 2 is being synthesized
  - Never wait for full response before playing
- Exposes: `speak(text)` — async, starts audio immediately
- Exposes: `stop()` — stops mid-speech
- Sets `is_speaking = True` during output, `False` when done
- `is_speaking` must be importable by the wake word module
- Calls the audio SFX "done.wav" chime after speech completes

**Test:** `python -c "from voice.tts import tts; import asyncio; asyncio.run(tts.speak('Good morning sir. All systems are operational.'))"` — should play audio immediately, not after a delay.

---

## Task 1.2 — Build the sound effects manager

**File:** `voice/sounds.py`

Build a simple non-blocking SFX player:
- `play(sound_name)` — plays a sound from `settings.paths.assets_dir/audio/`
- Sounds: `boot_intro`, `listening`, `working`, `done`, `error`
- Non-blocking — never delays the pipeline
- Volume controlled by `settings.boot.music_volume`

Create placeholder audio files in `assets/audio/` with a note explaining what each should sound like. They can be silent WAV files until real sounds are added.

**Test:** `python -c "from voice.sounds import sounds; sounds.play('done')"` — should play without error (even if file is silent placeholder).

---

## Task 1.3 — Build the VAD module

**File:** `voice/vad.py`

Voice activity detection using webrtcvad:
- Records audio continuously from microphone
- Returns audio chunks only when speech is detected
- Stops recording automatically when silence is detected
- Uses `settings.voice.vad_aggressiveness` (3 for noisy workshop)
- Minimum speech length: 0.5 seconds (filters out brief noises)
- Maximum recording length: 30 seconds (prevents runaway recording)

Exposes: `record_until_silence()` → returns `bytes` (WAV audio data)

**Test:** Run the module standalone. Speak a sentence. Verify it captures only the speech and stops cleanly.

---

## Task 1.4 — Build the STT module

**File:** `voice/stt.py`

Speech-to-text using faster-whisper with CUDA:
- Model: `settings.voice.stt_model` (medium.en)
- Device: CUDA
- Compute type: float16
- Transcribes audio bytes → returns string
- Strips leading/trailing whitespace and filler words
- Log every transcription to audit log with duration

Exposes: `transcribe(audio_bytes)` → `str`

**Test:** `python tests/stt_test.py` — record yourself saying "Hey JARVIS open VS Code" and verify accurate transcription, sub 0.5s on GPU.

---

## Task 1.5 — Build the wake word detector

**File:** `voice/wake_word.py`

Wake word detection using OpenWakeWord:
- Listens continuously from microphone
- Detects "hey_jarvis" trigger
- On detection:
  1. Check `is_speaking` from tts.py — if True, IGNORE (prevent self-trigger)
  2. Play `listening.wav` chime immediately
  3. Start VAD recording
  4. Return audio when silence detected
- Also supports push-to-talk:
  - `settings.voice.push_to_talk_key` held down → record
  - Key released → stop recording and return audio
- Uses `settings.voice.wake_word_sensitivity`

Exposes: `listen()` → `bytes` (audio ready for STT)

**Test:** Say "Hey JARVIS" while the detector is running. Verify the listening chime plays and recording starts. Test self-suppression: play TTS while detector is running, say the wake phrase — verify it is IGNORED.

---

## Task 1.6 — Wire the full voice pipeline

**File:** `voice/audio_stream.py`

Connect everything into one pipeline loop:
```
wake_word.listen() 
  → stt.transcribe() 
  → sounds.play("working")
  → router.classify()
  → llm_client.chat() OR tools.registry.execute()
  → tts.speak()
  → sounds.play("done")
  → loop back to wake_word.listen()
```

The loop runs in a background thread/task.
On any error: `sounds.play("error")` then `tts.speak("Afraid something went wrong, sir. Standing by.")`
Set `is_speaking=True/False` around tts.speak() so wake word is suppressed.
Log every step to audit.

**Test:** Full end-to-end. Say "Hey JARVIS, what is today's date?" — verify the full pipeline runs and JARVIS responds in character. Time the full round trip — target under 3 seconds.

---

## Task 1.7 — Build the boot sequence

**File:** `app/boot.py`

The boot sequence runs on Windows login and makes JARVIS feel cinematic.

```
Step 1: Start server (if not already running)
Step 2: Wait for Ollama to respond (retry up to 30s)
Step 3: Start Electron HUD (subprocess)
Step 4: Play boot music via sounds.play("boot_intro")
Step 5: Send WebSocket event to HUD: {"type": "boot_start"}
Step 6: Wait 5 seconds for animation
Step 7: Generate morning status report from Qwen3 32B
Step 8: Send WebSocket event to HUD: {"type": "boot_complete"}
Step 9: Speak morning status report via tts.speak()
Step 10: Set is_listening=True, wake word active
```

**Morning status report generation:**
Call `llm_client.chat()` with a system prompt that tells JARVIS to generate a concise status report using:
- Current time (from Python datetime)
- GPU temperature (from GPUtil)
- Last project name (from `memory/project_state.py` if exists, else "no active project")
- Pending task count (from task queue if exists, else 0)

The generated report should sound like:
"Good morning, sir. The time is 9:14 AM. All systems operational. GPU temperature 42 degrees. No pending tasks. No active project on record. Ready when you are."

**Test:** Run `python app/boot.py` manually. Verify all 10 steps complete. Verify TTS plays the status report. Time the full boot — should complete in under 10 seconds.

---

## Task 1.8 — Windows Task Scheduler setup script

**File:** `scripts/setup_autostart.py`

Write a Python script that creates a Windows Task Scheduler entry to run boot.py on user login.

Uses `subprocess` to call `schtasks.exe`:
```python
# Creates task: "JARVIS Boot" runs boot.py at login
subprocess.run([
    "schtasks", "/create", "/tn", "JARVIS Boot",
    "/tr", f"python {boot_py_path}",
    "/sc", "onlogon", "/rl", "highest"
])
```

**Test:** Run the setup script. Log out and back in. Verify JARVIS boots automatically.

---

## Task 1.9 — Write boot test

**File:** `tests/boot_test.py`

Test the boot sequence:
- Verifies Ollama responds before boot completes
- Verifies morning report contains: time, GPU temp, project name
- Verifies TTS starts within 6 seconds of boot
- Verifies `is_listening=True` after boot
- Times total boot duration (target: under 10 seconds)

---

## Phase 1 Complete When

- [ ] `python tests/stt_test.py` — PASS (sub 0.5s transcription)
- [ ] `python tests/tts_test.py` — PASS (streaming confirmed — first word within 0.5s)
- [ ] `python tests/wake_word_test.py` — PASS (fires in workshop with fan noise)
- [ ] `python tests/boot_test.py` — PASS (boot under 10 seconds)
- [ ] Push-to-talk works without wake word
- [ ] Self-suppression: say wake phrase during TTS output → NOT triggered (10/10 times)
- [ ] Full pipeline: "Hey JARVIS, what's today's date?" → correct answer in under 3 seconds
- [ ] Boot sequence: AC/DC plays → animation → morning report → listening
- [ ] Morning report contains: time + GPU temp + project/task info
- [ ] UI sound effects at every stage (listening, working, done, error)
- [ ] Verbal error: disconnect Ollama mid-session → JARVIS speaks the error
- [ ] Emergency stop works mid-response (voice "JARVIS stop" + Ctrl+Alt+J)
- [ ] No internet needed for any voice interaction

**After Phase 1 passes: update CLAUDE.md "Current Status" section.**
