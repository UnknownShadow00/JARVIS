"""Web search tool - DuckDuckGo search and page fetching."""
from __future__ import annotations

from typing import Any

import httpx
from bs4 import BeautifulSoup

SAFETY_LEVEL = 0
DESCRIPTION = "Search the web via DuckDuckGo or fetch readable text from a URL."


def execute(params: dict[str, Any]) -> list[dict[str, str]] | str:
    """Search the web, or fetch a page when action='fetch'."""
    if params.get("action") == "fetch":
        return fetch_page(str(params.get("url", "")))

    try:
        from ddgs import DDGS
    except ImportError:
        from duckduckgo_search import DDGS

    query: str = params.get("query", "")
    max_results: int = int(params.get("max_results", 5))

    if not query:
        return []

    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=max_results))

    return [
        {
            "title": r.get("title", ""),
            "url": r.get("href", ""),
            "snippet": r.get("body", ""),
        }
        for r in results
    ]


def fetch_page(url: str) -> str:
    """Fetch a URL and return clean visible page text."""
    if not url.startswith(("http://", "https://")):
        return "Only http:// and https:// URLs can be fetched."

    with httpx.Client(timeout=httpx.Timeout(15.0), follow_redirects=True) as client:
        response = client.get(url, headers={"User-Agent": "JARVIS/0.1"})
        response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    text = " ".join(soup.get_text(" ").split())
    return text[:20_000]
