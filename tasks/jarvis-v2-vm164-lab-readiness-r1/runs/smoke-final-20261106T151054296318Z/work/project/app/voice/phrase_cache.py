from __future__ import annotations

from dataclasses import dataclass


CACHED_PHRASES: dict[str, str] = {
    "right_away": "Right away, sir.",
    "on_it": "On it, sir.",
    "done": "Done, sir.",
    "working": "Working on it, sir.",
    "looking": "Looking into that now, sir.",
    "searching": "Searching now, sir.",
    "understood": "Understood, sir.",
    "complete": "Task complete, sir.",
    "listening": "Listening.",
    "no_connection": "Afraid the connection is unavailable, sir.",
    "cannot": "Afraid I cannot do that, sir.",
    "error": "Encountered an error, sir. Checking systems.",
    "confirm_delete": "That will permanently delete the file, sir. Shall I proceed?",
    "confirm_send": "Shall I send that, sir?",
    "good_morning": "Good morning, sir. All systems operational.",
}


@dataclass
class PhraseCache:
    """In-memory phrase catalog; audio pre-generation can fill this later."""

    phrases: dict[str, str]

    def get(self, key: str, default: str = "On it, sir.") -> str:
        return self.phrases.get(key, default)


phrase_cache = PhraseCache(CACHED_PHRASES)
