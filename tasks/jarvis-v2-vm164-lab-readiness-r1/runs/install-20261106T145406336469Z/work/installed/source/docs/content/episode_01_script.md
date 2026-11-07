# Episode 1 Script

## Title
**Building a Real JARVIS from Scratch - Part 1: The Brain**

## Hook (0:00-0:30)

[B-ROLL: Dark desktop setup. Terminal, editor, and JARVIS UI on screen. Quick cuts between waveform, terminal output, and JARVIS reply.]

[ON-SCREEN: "No cloud. No API bill. 100% local."]

**Host:** "JARVIS, give me a status check."

[ON-SCREEN: Terminal request and response.]

**JARVIS:** "All primary systems are operational, sir."

[B-ROLL: Fast punch-ins on `FastAPI`, `Ollama`, `Qwen3`, `Gemma`, and the repo tree.]

**Host:** "That voice, that response style, that routing logic, all of it is running on my own PC. No OpenAI bill. No monthly agent tax. Just a real local AI assistant stack built from scratch."

[ON-SCREEN: "Building JARVIS Series - Episode 1: The Brain"]

## Intro (0:30-1:30)

[B-ROLL: Face cam with desktop capture. GitHub repo open beside IDE.]

**Host:** "If you're new here, I'm building a real JARVIS-style assistant inspired by Tony Stark, but grounded in tools you can actually run at home. The goal is not a chatbot tab. The goal is a local-first AI system that can talk, route tasks, use tools, see the screen, and eventually control the whole machine."

[ON-SCREEN: "Local-first AI assistant"]

**Host:** "The reason I'm starting local is simple. Privacy matters, latency matters, and I do not want every experiment tied to somebody else's API pricing page. If I want to test this thing fifty times in one night, I want to do it for free on hardware I already own."

[B-ROLL: Ollama dashboard, config file, GPU footage, repo phases in README.]

**Host:** "In this first episode, we're building the brain. The FastAPI backend, the local model stack, the intent router, the JARVIS personality prompt, and the audit log that records what the system is doing."

[ON-SCREEN: "Today: Brain stack, routing, personality, audit log"]

## Section 1 - Tech Stack Overview (1:30-4:30)

[B-ROLL: Architecture diagram animating in.]

**Host:** "The stack for this phase is intentionally simple and modular."

**Host:** "At the center is `FastAPI`. That gives me a clean backend with REST and WebSocket endpoints, which means this same brain can serve a terminal demo now and a full voice interface later."

[ON-SCREEN: "`app/server.py` -> `/health`, `/chat`, `/ws`"]

**Host:** "For local inference, I'm using `Ollama`. That is the runtime layer that lets me pull models, host them on my machine, and swap configurations without rewriting the app."

[B-ROLL: Terminal showing `ollama pull qwen3:14b` and `ollama pull gemma3:4b`.]

**Host:** "The main language model for responses is `Qwen3`. That's the model doing the actual JARVIS talking, reasoning, and answering."

**Host:** "Then I split routing out to a smaller model, `Gemma`, because not every request needs the big brain. Sometimes you just need a fast classifier to decide: answer directly, use a tool, retrieve memory, use vision, or ask for confirmation."

[ON-SCREEN: "Main model: Qwen3 | Router model: Gemma"]

**Host:** "That separation matters because it keeps the system faster and cheaper to run locally. The router does triage. The main model does the performance."

**Host:** "The project config also leaves room for bigger upgrades later. Right now the README is already structured around the local stack: Qwen for the brain, Gemma for routing, and a future vision path with `qwen3-vl` once we step into screen awareness."

[B-ROLL: `README.md` feature matrix and architecture section.]

**Host:** "So the Phase 0 architecture is basically this: FastAPI handles requests, the router decides intent, tools can execute if needed, the main model crafts the JARVIS-style response, and every important event gets logged."

[ON-SCREEN: "Request -> Router -> Tool or Reply -> Audit Log"]

## Section 2 - Phase 0 Walkthrough (4:30-8:30)

[B-ROLL: Open `app/server.py` in editor. Slow zoom on imports and endpoints.]

**Host:** "Let's walk through the core files."

**Host:** "First is `app/server.py`. This is the brain's entry point. The server exposes `/health`, `/chat`, and a WebSocket endpoint so the system can support both normal request-response flows and real-time streaming later."

[ON-SCREEN: "`/health` | `/chat` | WebSocket"]

**Host:** "The important part is that the server does not try to be clever by itself. It orchestrates. It receives the message, passes it into the processing pipeline, and returns a structured reply with the intent, confidence score, dry-run state, and active state."

[B-ROLL: Highlight `ChatResponse` model and `chat()` handler.]

**Host:** "Next is the router in `app/brain/router.py`. This file is one of the most important design choices in the whole project. Instead of dumping every message straight into the main model, I run a fast intent classifier first."

**Host:** "The router can classify messages into direct response, tool use, memory retrieval, vision, or confirmation for risky actions. It also has deterministic safety rules, so if you say something like delete, wipe, commit, deploy, or install, the system can force a confirmation path before anything dangerous happens."

[ON-SCREEN: "Intents: respond | use_tool | retrieve_memory | vision | confirm_action"]

[B-ROLL: Highlight regex rules and router result dataclass.]

**Host:** "That means the local assistant is not just talking. It's deciding what kind of task it is dealing with before the big model spends time on it."

**Host:** "Then we have the JARVIS personality prompt in `app/brain/prompts.py`. This is where the character becomes consistent. The prompt tells the model to stay precise, fast, composed, and operationally useful. It always calls the user 'sir', keeps responses concise, stays in character, and asks for confirmation on risky actions."

[ON-SCREEN: "Personality rules: precise, concise, in-character, calls user 'sir'"]

**Host:** "A detail I really like here is that the prompt also bans a lot of generic AI filler. No 'great question', no 'I'd be happy to', no soft chatbot fluff. The whole point is to make the assistant sound like JARVIS, not a customer support widget."

[B-ROLL: Prompt text scrolling on screen.]

**Host:** "And finally, the audit log in `app/logs/audit.py`. This file quietly does a lot of heavy lifting. Every important event gets turned into a JSON line entry with a timestamp, event type, session ID, and structured data."

[ON-SCREEN: "JSONL audit trail"]

**Host:** "It even writes asynchronously through a queue and background thread, which means I get a clean trail of what the assistant classified, what it tried to do, and what happened, without blocking the main request path."

[B-ROLL: Example log lines appearing on screen.]

**Host:** "That logging is critical because once this grows into voice, desktop control, and autonomous workflows, debugging without an audit trail becomes a nightmare."

## Demo (8:30-10:30)

[B-ROLL: Terminal and local app in full screen. Face cam minimized.]

**Host:** "Let's run it."

[ON-SCREEN: "`python -m app.main`"]

**Host:** "The backend is up. Health check is clean. Now I'll send it a simple question."

[B-ROLL: Type into terminal or chat UI: "What is the goal of this project?"]

**Host:** "Watch the response style."

**JARVIS:** "The objective is a local-first AI assistant that can think, speak, and operate your machine without cloud dependency, sir."

[ON-SCREEN: "Concise. In-character. Local."]

**Host:** "That answer is exactly what I want from Phase 0. Short, composed, and in personality."

[B-ROLL: Send a second prompt: "Open VS Code" or "Delete the old project folder".]

**Host:** "Now if I push it toward an action, the router can classify the task and the system can either trigger the right path or ask for confirmation if the request is risky."

[ON-SCREEN: "Router confidence + intent + safety gate"]

**Host:** "So even at this early stage, the brain already has structure. It is not just text generation. It is a local assistant pipeline with routing, safety, personality, and traceability."

## Outro (10:30-11:00)

[B-ROLL: Montage of repo files, terminal, and future voice waveform teaser.]

**Host:** "That is Part 1 of building a real JARVIS from scratch. In the next episode, we're going deeper into Phase 1 and giving this thing a voice with wake word detection, speech-to-text, and spoken replies."

[ON-SCREEN: "Next: Episode 2 - Voice"]

**Host:** "The GitHub link is in the description if you want to build along. Subscribe if you want to see this become a full local AI system, because this is just the brain, sir."

[ON-SCREEN: "GitHub: github.com/UnknownShadow00/JARVIS | Subscribe for Part 2"]
