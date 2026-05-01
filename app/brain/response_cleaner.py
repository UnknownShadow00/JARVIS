"""Response cleaner - strips markdown, enforces JARVIS voice rules, handles dry-run narration."""
from __future__ import annotations

import re

from app.config import settings

_MARKDOWN_PATTERNS = [
    re.compile(r"```[\s\S]*?```"),
    re.compile(r"`([^`]+)`"),
    re.compile(r"#{1,6}\s+"),
    re.compile(r"\*{1,2}([^*]+)\*{1,2}"),
    re.compile(r"_{1,2}([^_]+)_{1,2}"),
    re.compile(r"!\[.*?\]\(.*?\)"),
    re.compile(r"\[([^\]]+)\]\(.*?\)"),
    re.compile(r"^\s*[-*+]\s+", re.MULTILINE),
    re.compile(r"^\s*\d+\.\s+", re.MULTILINE),
]

_BANNED_OPENERS = [
    "absolutely",
    "great question",
    "i'd be happy to",
    "of course",
    "how can i help",
    "is there anything else",
    "i apologize",
    "certainly",
    "sure thing",
    "no problem",
]


def clean(text: str) -> str:
    """Strip markdown and enforce voice output rules."""
    for pattern in _MARKDOWN_PATTERNS:
        text = pattern.sub(r"\1" if pattern.groups else " ", text)

    text = re.sub(r"\s+", " ", text).strip()

    lower = text.lower()
    for phrase in _BANNED_OPENERS:
        if lower.startswith(phrase):
            text = text[len(phrase):].lstrip(" ,.")
            break

    sentences = re.split(r"(?<=[.!?])\s+", text)
    if len(sentences) > 2:
        text = " ".join(sentences[:2])

    return text.strip()


def dry_run_narration(tool_name: str, params: dict) -> str:
    """Generate a verbal narration of what would happen if dry_run were off."""
    if not settings.safety.dry_run:
        return ""
    return f"I would call {tool_name} with {params}, sir. Dry run mode is active - no action taken."
