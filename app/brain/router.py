from __future__ import annotations

import json
import re
from dataclasses import dataclass

import httpx

from app.config import settings
from app.logs.audit import audit

_SYSTEM_PROMPT = """You are an intent classifier. Classify the user message into exactly ONE intent.

Return ONLY valid JSON - no explanation, no markdown, no extra text:
{"intent": "...", "confidence": 0.0, "suggested_tool": "...", "reasoning": "..."}

Intent options:
- "respond"         - answer directly, no tools or actions needed
- "use_tool"        - requires a tool (set suggested_tool to: system_stats, web_search, apps, files, shell, calendar, screenshot, browser, browser_use)
- "retrieve_memory" - needs memory or history lookup
- "vision"          - needs screen capture or webcam
- "confirm_action"  - dangerous/irreversible action that needs user confirmation
- "deep_reasoning"  - needs slower analysis/design/debug reasoning

Rules:
- confidence is 0.0 to 1.0
- suggested_tool is the tool name if intent is use_tool, else empty string ""
- reasoning is one short sentence explaining why"""

_VALID_INTENTS = {"respond", "use_tool", "retrieve_memory", "vision", "confirm_action", "deep_reasoning"}


@dataclass
class RouterResult:
    intent: str
    confidence: float
    suggested_tool: str
    reasoning: str


class IntentRouter:
    """Fast intent classifier with deterministic safety rules and Ollama fallback."""

    def classify(self, user_message: str) -> RouterResult:
        """Classify a user message into one Phase 0 intent."""
        deterministic = self._classify_by_rules(user_message)
        if deterministic is not None:
            return self._finalize(deterministic, user_message)

        try:
            raw = self._classify_with_ollama(user_message)
        except Exception as exc:
            audit.log(
                "intent_classified",
                {
                    "intent": "respond",
                    "confidence": 0.5,
                    "suggested_tool": "",
                    "query": user_message,
                    "error": str(exc),
                },
            )
            return RouterResult("respond", 0.5, "", f"ollama error: {exc}")

        return self._finalize(self._parse(raw, user_message), user_message)

    def _classify_with_ollama(self, user_message: str) -> str:
        payload = {
            "model": settings.models.router,
            "messages": [
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            "stream": False,
            "think": False,
            "options": {
                "temperature": 0.1,
                "num_predict": 64,
                "num_ctx": settings.models.router_context,
            },
        }
        url = f"{settings.models.ollama_base_url}/api/chat"
        with httpx.Client(timeout=httpx.Timeout(20.0)) as client:
            response = client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()

        message = data.get("message", {})
        if isinstance(message, dict):
            return str(message.get("content", "") or "").strip()
        return str(data.get("response", "") or "").strip()

    def _finalize(self, result: RouterResult, user_message: str) -> RouterResult:
        if result.confidence < settings.safety.confidence_threshold:
            result = RouterResult(
                "confirm_action",
                result.confidence,
                result.suggested_tool,
                result.reasoning,
            )

        audit.log(
            "intent_classified",
            {
                "intent": result.intent,
                "confidence": result.confidence,
                "suggested_tool": result.suggested_tool,
                "reasoning": result.reasoning,
                "query": user_message,
            },
        )
        return result

    def _classify_by_rules(self, user_message: str) -> RouterResult | None:
        text = user_message.lower().strip()

        if not text:
            return RouterResult("respond", 1.0, "", "Empty input can be answered directly.")

        if re.search(r"\b(run|execute|shell|cmd|terminal|bash|powershell|npm run|pip install|python -)\b", text):
            return RouterResult(
                "use_tool",
                0.93,
                "shell",
                "The request asks to run a shell command.",
            )

        if re.search(
            r"\b(delete|format|wipe|erase|destroy|remove all|commit|push|deploy|install|uninstall|send|message|email|purchase|buy)\b",
            text,
        ):
            return RouterResult(
                "confirm_action",
                0.96,
                "",
                "The request may change external state or cause damage.",
            )

        if re.search(r"\b(screenshot|capture screen|take a screenshot)\b", text):
            return RouterResult(
                "use_tool",
                0.94,
                "screenshot",
                "The request asks to capture a screenshot.",
            )

        if re.search(r"\b(webcam|camera|see on my screen|look at)\b", text):
            return RouterResult("vision", 0.95, "", "The request needs visual context.")

        if re.search(r"\b(can'?t hear|can'?t listen|no audio|audio.*not working|not hearing|speak louder|too quiet|muted|sound.*issue)\b", text):
            return RouterResult("respond", 0.92, "", "User is reporting an audio/hardware issue — answer directly.")

        if re.search(
            r"\b(debug|design|architect|analy[sz]e|think through|root cause|trade[- ]?off|review this|investigate)\b",
            text,
        ):
            return RouterResult(
                "deep_reasoning",
                0.94,
                "",
                "The request asks for deeper analysis or design reasoning.",
            )

        if re.search(
            r"\b(remember|last project|yesterday|pending tasks|tasks.*pending|todo|hardware setup|what did i tell you|history)\b",
            text,
        ):
            return RouterResult(
                "retrieve_memory",
                0.94,
                "",
                "The request depends on stored memory.",
            )

        if re.search(r"\b(cpu|ram|memory usage|disk usage|gpu|system stats|processes|uptime)\b", text):
            return RouterResult(
                "use_tool",
                0.96,
                "system_stats",
                "The request asks for live system information.",
            )

        if re.search(
            r"\b(go to|browse|navigate to|open.*website|open.*url|open.*http|open.*tab|open a browser)\b",
            text,
        ) or re.search(r"\b[a-z0-9-]+\.(?:com|net|org|io|dev|app|ai|gg|tv|me|local)\b", text):
            return RouterResult(
                "use_tool",
                0.92,
                "browser",
                "The request asks to open a browser or URL.",
            )

        if re.search(r"\b(search|web|google|duckduckgo|latest|benchmarks|weather|news|look up)\b", text):
            return RouterResult(
                "use_tool",
                0.93,
                "web_search",
                "The request needs current web information.",
            )

        if re.search(r"\b(browser agent|use browser-use|automate.*browser|research.*website|fill.*form)\b", text):
            return RouterResult(
                "use_tool",
                0.91,
                "browser_use",
                "The request asks for browser-agent automation.",
            )

        if re.search(r"\b(open|launch|start)\b", text):
            return RouterResult("use_tool", 0.92, "apps", "The request asks to launch an application.")

        if re.search(r"\b(files?|folders?|directory|downloads|list dir|show me the files|read file)\b", text):
            return RouterResult(
                "use_tool",
                0.91,
                "files",
                "The request asks for file system information.",
            )

        if re.search(r"\b(calendar|schedule|events today|my day|appointments|what.*have.*today|today.*schedule)\b", text):
            return RouterResult(
                "use_tool",
                0.91,
                "calendar",
                "The request asks for calendar events.",
            )

        if re.search(r"\b(time|joke|capital|how are you|what is|who is|explain|tell me)\b", text):
            return RouterResult("respond", 0.9, "", "The request can be answered directly.")

        return None

    def _parse(self, raw: str, query: str) -> RouterResult:
        """Parse model JSON into a validated RouterResult."""
        try:
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            data = json.loads(match.group() if match else raw)
            intent = data.get("intent", "respond")
            if intent not in _VALID_INTENTS:
                intent = "respond"
            confidence = max(0.0, min(1.0, float(data.get("confidence", 0.5))))
            return RouterResult(
                intent=intent,
                confidence=confidence,
                suggested_tool=str(data.get("suggested_tool", "")),
                reasoning=str(data.get("reasoning", "")),
            )
        except Exception:
            return RouterResult("respond", 0.5, "", "parse error")


router = IntentRouter()


def classify_intent(user_message: str) -> RouterResult:
    """Module-level convenience wrapper around the shared IntentRouter."""
    return router.classify(user_message)
