"""Non-blocking sound effects for voice pipeline state changes."""
from __future__ import annotations

import os
import threading
import warnings
from pathlib import Path
from typing import Final

from app.config import settings
from app.logs.audit import audit

SOUND_FILES: Final[dict[str, str]] = {
    "boot_intro": "boot_intro.wav",
    "listening": "listening.wav",
    "working": "working.wav",
    "done": "done.wav",
    "error": "error.wav",
}


class SoundsManager:
    def __init__(self) -> None:
        self._mixer_initialized = False
        self._lock = threading.Lock()

    def play(self, sound_name: str) -> bool:
        """Play a named sound without blocking the caller."""
        path = self.sound_path(sound_name)
        if path is None:
            return False

        thread = threading.Thread(
            target=self._play_file_thread,
            args=(path, False),
            name=f"jarvis-sfx-{sound_name}",
            daemon=True,
        )
        thread.start()
        return True

    def play_file(self, path: str | Path, *, blocking: bool = False) -> bool:
        """Play an arbitrary WAV file, optionally waiting until it finishes."""
        audio_path = Path(path)
        if blocking:
            return self._play_file_thread(audio_path, True)

        thread = threading.Thread(
            target=self._play_file_thread,
            args=(audio_path, False),
            name="jarvis-audio-file",
            daemon=True,
        )
        thread.start()
        return True

    def sound_path(self, sound_name: str) -> Path | None:
        filename = SOUND_FILES.get(sound_name)
        if filename is None:
            audit.log("sound_missing", {"sound": sound_name, "reason": "unknown_sound"})
            return None

        path = Path(settings.paths.assets_dir) / "audio" / filename
        if not path.is_file():
            audit.log("sound_missing", {"sound": sound_name, "path": str(path)})
            return None
        return path

    def _play_file_thread(self, path: Path, blocking: bool) -> bool:
        try:
            pygame = self._load_pygame()
            if pygame is None:
                return False

            with self._lock:
                sound = pygame.mixer.Sound(str(path))
                sound.set_volume(settings.boot.music_volume)
                channel = sound.play()

            if blocking and channel is not None:
                while channel.get_busy():
                    pygame.time.wait(20)

            audit.log("sound_played", {"path": str(path), "blocking": blocking})
            return True
        except Exception as exc:
            audit.log("sound_error", {"path": str(path), "error": str(exc)})
            return False

    def _load_pygame(self):  # noqa: ANN202
        try:
            os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", message="pkg_resources is deprecated.*", category=UserWarning)
                import pygame
        except ImportError as exc:
            audit.log("sound_unavailable", {"reason": str(exc)})
            return None

        with self._lock:
            if not self._mixer_initialized:
                pygame.mixer.init()
                self._mixer_initialized = True
        return pygame

    def release(self) -> None:
        try:
            os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", message="pkg_resources is deprecated.*", category=UserWarning)
                import pygame

            with self._lock:
                if pygame.mixer.get_init():
                    pygame.mixer.stop()
                    pygame.mixer.quit()
                self._mixer_initialized = False
            audit.log("sound_released", {})
        except Exception as exc:  # noqa: BLE001
            audit.log("sound_release_error", {"error": str(exc)})


sounds = SoundsManager()
