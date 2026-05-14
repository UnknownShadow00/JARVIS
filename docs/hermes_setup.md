# Hermes Agent — Install Guide

Hermes runs in WSL2 and points at the existing Windows Ollama instance.
Install order: Hermes core → labyrinth (observability) → mission-control (UI) → wondelai skills.

---

## 1 — Install Hermes Core (WSL2)

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

After install, configure the Ollama endpoint:

```bash
hermes model
# Select: Custom endpoint
# URL: http://host.docker.internal:11434/v1   (or http://localhost:11434/v1 if native WSL2)
# Model: qwen3-nothink
# Context: 8192
```

Verify connection:

```bash
hermes status
```

---

## 2 — Init Kanban

```bash
hermes kanban init
```

> **Note:** When Hermes Kanban is active it replaces `app/agent/task_queue.py`.
> The FastAPI `/confirm/{id}` endpoint maps to Kanban unblock — do not remove it.
>
> Hermes v0.13.0+ has durable Kanban with zombie detection, retry budgets, and `/goal` persistence.

---

## 3 — Create Specialist Profiles

```bash
# Researcher — web search, memory, RAG, files
hermes profile create jarvis-researcher \
  --model qwen3:14b \
  --tools search,web,memory,rag,files

# Coder — terminal, files, git, shell
hermes profile create jarvis-coder \
  --model qwen2.5-coder:14b \
  --tools terminal,files,git,shell

# Reviewer — files, web, memory
hermes profile create jarvis-reviewer \
  --model qwen3:14b \
  --tools files,web,memory
```

---

## 4 — Install Observability Plugin (hermes-labyrinth)

Always install this — it provides trace logs, cost tracking, and per-task timing.

```bash
git clone https://github.com/NousResearch/hermes-labyrinth ~/.hermes/plugins/hermes-labyrinth
hermes plugins reload
```

---

## 5 — Install UI (mission-control)

mission-control replaces hermes-workspace. It provides 26 real-time panels over WebSocket with a SQLite backend.

```bash
git clone https://github.com/builderz-labs/mission-control ~/mission-control
cd ~/mission-control
pnpm install
pnpm dev
# Open http://localhost:3000 in browser
```

---

## 6 — Install Community Skills (wondelai)

```bash
git clone https://github.com/wondelai/skills ~/.hermes/skills/wondelai
hermes skills reload
```

Verify skills loaded:

```bash
hermes skills list | head -20
```

---

## 7 — Self-Evolution (Phase 4+, after 500 interactions)

After 500 real interactions, enable Hermes self-evolution instead of OpenJarvis:

```bash
# Reference: NousResearch/hermes-agent-self-evolution (ICLR 2026 oral)
# Uses DSPy + GEPA to evolve skills autonomously
# Install DSPy first:
pip install dspy-ai
# Then follow the hermes-agent-self-evolution README for GEPA integration
```

> `audit.jsonl` is already in the correct format — traces are ready for self-evolution.

---

## 8 — Verify Full Stack

```bash
hermes status        # Hermes core + Ollama connection
hermes kanban list   # Kanban tasks (empty is fine on first run)
hermes skills list   # Wondelai + any built-in skills
hermes plugins list  # Should show hermes-labyrinth
```

---

## Notes

- **4070 Ti constraint:** qwen3:14b is the max single-load model for Hermes profiles. After 5090 arrives, switch to qwen3:32b for all profiles — run `scripts/switch_models.py --profile 5090`.
- **WSL2 networking:** Use `http://host.docker.internal:11434/v1` if Ollama is on Windows and Hermes is inside WSL2 Docker. Use `http://localhost:11434/v1` if Hermes runs natively in WSL2 (no Docker).
- **Kanban and task_queue.py:** Both can run simultaneously during transition. Kanban takes over permanently once Hermes is stable.
- **MCP via Hermes:** Hermes has native MCP support — connect it to the same whitelisted servers defined in `app/tools/mcp_client.py`.
