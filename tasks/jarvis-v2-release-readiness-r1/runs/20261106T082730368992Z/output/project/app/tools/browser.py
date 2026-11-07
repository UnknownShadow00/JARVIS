"""Browser control tool for opening URLs or running searches."""
from __future__ import annotations

from typing import Any
from urllib.parse import quote_plus
import webbrowser

from app.config import settings
from app.logs.audit import audit

SAFETY_LEVEL = 1
DESCRIPTION = "Open a URL or control the default browser"

ACTION_KEY = "action"
URL_KEY = "url"
DEFAULT_ACTION = "open"
SEARCH_ACTION = "search"
OPEN_ACTION = "open"
ERROR_KEY = "error"
DRY_RUN_KEY = "dry_run"
NOTE_KEY = "note"
TOOL_NAME = "browser"
URL_REQUIRED_ERROR = "url required"
UNKNOWN_ACTION_ERROR = "unknown action: {action}"
SEARCH_PREFIX = "https://www.google.com/search?q="
DRY_RUN_NOTE = "Would open: {url}"
TOOL_CALL_EVENT = "tool_call"
TOOL_RESULT_EVENT = "tool_result"


def execute(params: dict[str, Any]) -> dict[str, Any]:
    """Open a URL or search the web in the default browser."""
    action = str(params.get(ACTION_KEY, DEFAULT_ACTION))
    raw_url = params.get(URL_KEY)
    url = str(raw_url) if raw_url is not None else ""

    if not url:
        return {ERROR_KEY: URL_REQUIRED_ERROR}

    if action == SEARCH_ACTION:
        target_url = f"{SEARCH_PREFIX}{quote_plus(url)}"
    elif action == OPEN_ACTION:
        target_url = url
    else:
        return {ERROR_KEY: UNKNOWN_ACTION_ERROR.format(action=action)}

    audit.log(
        TOOL_CALL_EVENT,
        {
            "tool": TOOL_NAME,
            ACTION_KEY: action,
            URL_KEY: target_url,
            DRY_RUN_KEY: settings.safety.dry_run,
        },
    )

    if settings.safety.dry_run:
        return {DRY_RUN_KEY: True, NOTE_KEY: DRY_RUN_NOTE.format(url=target_url)}

    webbrowser.open(target_url)
    audit.log(TOOL_RESULT_EVENT, {"tool": TOOL_NAME, URL_KEY: target_url})
    return {URL_KEY: target_url}
