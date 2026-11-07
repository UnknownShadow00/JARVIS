"""Pure helpers that map routed user text to concrete tool parameters."""
from __future__ import annotations

import datetime
import re
from typing import Any

from app.config import settings

_WAKE_PREFIX_RE = re.compile(r"^\s*(?:hey\s+jarvis|jarvis)[,\s]*", re.IGNORECASE)
_WAKE_SUFFIX_RE = re.compile(r"[,\s]*\bjarvis\b\s*[?.]?\s*$", re.IGNORECASE)
_CANCEL_COMMAND_RE = re.compile(r"\babort\b|\bstop\s*,?\s*jarvis\b", re.IGNORECASE)
_OBSIDIAN_ACTION_RE = re.compile(r"\[ACTION:OBSIDIAN:([^:\]]+)(?::([^\]]+))?\]", re.IGNORECASE)


def strip_wake_word(text: str) -> str:
    text = _WAKE_PREFIX_RE.sub("", text)
    text = _WAKE_SUFFIX_RE.sub("", text)
    return text.strip()


def is_cancel_command(text: str) -> bool:
    return bool(_CANCEL_COMMAND_RE.search(text))


def extract_app_name(message: str) -> str:
    """Extract a likely app name from launch/close phrasing."""
    text = message.lower().replace("visual studio code", "vscode")
    text = re.sub(r"\b(open|launch|start|close|quit|exit)\b", "", text, flags=re.IGNORECASE)
    return text.strip(" .")


def build_tool_params(tool_name: str, message: str) -> dict[str, Any]:
    """Map routed user text to concrete tool parameters."""
    clean_msg = strip_wake_word(message)
    if tool_name == "system_stats":
        return {}
    if tool_name == "web_search":
        query = re.sub(r"\b(search|web|google|duckduckgo|look up)\b", "", clean_msg, flags=re.IGNORECASE)
        return {"query": query.strip(" .") or clean_msg, "max_results": 5}
    if tool_name == "apps":
        action = "close" if re.search(r"\b(close|quit|exit)\b", clean_msg, re.IGNORECASE) else "open"
        return {"action": action, "app": extract_app_name(clean_msg), "query": clean_msg}
    if tool_name == "files":
        lower = clean_msg.lower()
        action = "read" if "read" in lower else "list"
        path = settings.paths.downloads_dir if "download" in lower else settings.paths.projects_dir
        return {"action": action, "path": path, "query": clean_msg}
    if tool_name == "shell":
        command = re.sub(
            r"^\s*(run|execute|shell|cmd|bash|terminal)\b[:\s-]*",
            "",
            clean_msg,
            flags=re.IGNORECASE,
        ).strip()
        return {"command": command or clean_msg, "timeout": 30}
    if tool_name == "calendar":
        lower = clean_msg.lower()
        today = datetime.date.today()
        if "tomorrow" in lower:
            date_value = (today + datetime.timedelta(days=1)).isoformat()
        else:
            date_value = today.isoformat()
            if "today" in lower or re.search(r"\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b", lower):
                date_value = clean_msg
            elif re.search(r"\d", clean_msg):
                date_value = clean_msg
        return {"date": date_value}
    if tool_name == "screenshot":
        monitor_match = re.search(r"\b(?:monitor|screen)\s+(\d+)\b", clean_msg, flags=re.IGNORECASE)
        return {"monitor": int(monitor_match.group(1)) if monitor_match else 0}
    if tool_name == "vision":
        source = "webcam" if re.search(r"\b(webcam|camera)\b", clean_msg, re.IGNORECASE) else "screen"
        return {"source": source, "prompt": clean_msg or "What do you see?"}
    if tool_name == "browser":
        target = re.sub(
            r"^\s*(open|go to|browse|navigate to|open website|open url|open tab)\b[:\s-]*",
            "",
            clean_msg,
            flags=re.IGNORECASE,
        ).strip(" .")
        action = "open"
        if re.search(r"\b(search|google|look up|duckduckgo)\b", clean_msg, re.IGNORECASE):
            action = "search"
            target = re.sub(r"\b(search|google|look up|duckduckgo)\b", "", clean_msg, flags=re.IGNORECASE).strip(" .")
        elif target and "://" not in target and "." in target and " " not in target:
            target = f"https://{target}"
        elif target and "." not in target:
            action = "search"
        return {"action": action, "url": target or clean_msg}
    if tool_name == "browser_use":
        return {"goal": clean_msg}
    if tool_name == "obsidian":
        tag_match = _OBSIDIAN_ACTION_RE.search(clean_msg)
        if tag_match:
            action = tag_match.group(1).strip().lower()
            note = (tag_match.group(2) or "").strip()
            content = _OBSIDIAN_ACTION_RE.sub("", clean_msg).strip()
            params: dict[str, Any] = {"action": action}
            if note:
                params["path"] = note
            if content:
                params["content"] = content
                params["query"] = content
            return params

        lower = clean_msg.lower()
        if re.search(r"\b(search|find)\b", lower):
            query = re.sub(r"\b(search|find|obsidian|vault|notes?)\b", "", clean_msg, flags=re.IGNORECASE)
            return {"action": "note_search", "query": query.strip(" .") or clean_msg}
        if re.search(r"\b(read|open)\b", lower):
            return {"action": "note_read", "path": _extract_note_target(clean_msg)}
        if re.search(r"\b(append|add)\b", lower):
            return {
                "action": "note_append",
                "path": _extract_note_target(clean_msg),
                "content": clean_msg,
            }
        if re.search(r"\b(create|new)\b", lower):
            return {
                "action": "note_create",
                "path": _extract_note_target(clean_msg),
                "content": clean_msg,
            }
        return {"action": "note_search", "query": clean_msg}
    if tool_name == "computer_use":
        return {"task": clean_msg}
    if tool_name == "mouse_keyboard":
        return {"task": clean_msg, "query": clean_msg}
    return {"query": clean_msg}


def _extract_note_target(message: str) -> str:
    bracketed = re.search(r"\[\[([^\]]+)\]\]", message)
    if bracketed:
        return bracketed.group(1).strip()

    quoted = re.search(r'"([^"]+)"|\'([^\']+)\'', message)
    if quoted:
        return (quoted.group(1) or quoted.group(2)).strip()

    cleaned = re.sub(
        r"\b(obsidian|vault|notes?|create|new|append|add|read|open|called|named|to)\b",
        "",
        message,
        flags=re.IGNORECASE,
    )
    return cleaned.strip(" .:") or "Inbox"
