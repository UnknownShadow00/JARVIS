from __future__ import annotations

import re
from dataclasses import dataclass

from app.config import settings


@dataclass(frozen=True)
class ComplexityDecision:
    tier: str
    model: str
    think: bool
    num_predict: int
    reason: str


class ComplexityRouter:
    """Choose the cheapest model path that can answer the request well."""

    _DEEP_RE = re.compile(
        r"\b(debug|design|architect|analy[sz]e|think through|root cause|trade[- ]?off|review this|"
        r"explain why|plan a system|investigate)\b",
        re.IGNORECASE,
    )
    _TRIVIAL_RE = re.compile(
        r"\b(time|date|uptime|hello|hi|thanks|thank you|joke|status)\b",
        re.IGNORECASE,
    )

    def decide(self, message: str, intent: str = "respond") -> ComplexityDecision:
        text = message.strip()
        if intent == "deep_reasoning" or self._DEEP_RE.search(text):
            return ComplexityDecision(
                tier="deep",
                model=self._deep_model(),
                think=True,
                num_predict=700,
                reason="Request asks for analysis, design, or debugging.",
            )

        if intent == "respond" and len(text.split()) <= 8 and self._TRIVIAL_RE.search(text):
            return ComplexityDecision(
                tier="trivial",
                model=settings.models.router,
                think=False,
                num_predict=80,
                reason="Short direct request can use the router model.",
            )

        return ComplexityDecision(
            tier="normal",
            model=settings.models.main,
            think=False,
            num_predict=150,
            reason="Default fast no-think response path.",
        )

    def _deep_model(self) -> str:
        main = settings.models.main
        if main == "qwen3-nothink":
            return "qwen3:14b"
        return main


complexity_router = ComplexityRouter()
