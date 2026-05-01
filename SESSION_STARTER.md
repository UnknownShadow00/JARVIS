# JARVIS — Session Starter
> Read this at the beginning of every Claude Code session before touching any file.

---

## Step 1 — Read CLAUDE.md

Read the full `CLAUDE.md` file. Pay special attention to:
- Current Status section (bottom of file) — what phase are we on, what was last built
- Tech stack — never use a library not listed there without asking
- Coding conventions — enforce all of them
- Action format — `[ACTION:TYPE:PARAMS]` everywhere

---

## Step 2 — Check current state

```bash
# What phase are we on?
cat CLAUDE.md | grep "Phase:" 

# What files exist?
find app/ voice/ tools/ -name "*.py" | sort

# Are tests passing?
python tests/ollama_test.py
```

---

## Step 3 — Read the current phase task file

- Phase 0 → read `PHASE_0_TASKS.md`
- Phase 1 → read `PHASE_1_TASKS.md`
- Phase 2+ → task files will be added as phases complete

Find the first unchecked `- [ ]` task and start there.

---

## Step 4 — Never do these things

- Never hardcode model names — always `settings.models.main`
- Never hardcode ports or paths — always `settings.server.port` etc.
- Never skip the audit log — every tool call needs a log entry
- Never execute a tool without checking `settings.safety.dry_run`
- Never start building Phase N+1 while Phase N has failing tests
- Never use a library not in requirements.txt without updating it first
- Never create a TTS response with more than 2 sentences
- Never break character — JARVIS always says "sir"

---

## Step 5 — End of session

Before ending the session:
1. Run all tests in `tests/` — report which pass and which fail
2. Update the `Current Status` section at the bottom of `CLAUDE.md`:
   ```
   Phase:        [current phase]
   Last built:   [file name and what it does]
   Last tested:  [test name and result]
   Notes:        [any blockers, decisions made, next steps]
   ```
3. Summarize what was built in 3 bullet points

---

## Quick Reference

| What I need | Where it is |
|-------------|-------------|
| Model names | `settings.models.*` |
| Port numbers | `settings.server.*` |
| File paths | `settings.paths.*` |
| Safety mode | `settings.safety.approval_mode` |
| Dry run flag | `settings.safety.dry_run` |
| JARVIS personality | `brain/prompts.py` |
| All tool names | `tools/registry.py` → `registry.list_tools()` |
| Audit logging | `from logs.audit import audit; audit.log(type, data)` |
| Kill switch flag | `from brain.kill_switch import JARVIS_ACTIVE` |
| TTS speaking flag | `from voice.tts import tts; tts.is_speaking` |
