from __future__ import annotations

import argparse
import csv
from datetime import datetime
from pathlib import Path
from statistics import mean
from typing import Any

from app.config import settings


SAMPLE_RATE = 16_000
FRAME_DURATION_MS = 80
FRAME_SAMPLES = int(SAMPLE_RATE * (FRAME_DURATION_MS / 1000))
CSV_COLUMNS = ["timestamp_ms", "score", "detected"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Diagnostic tool for tuning OpenWakeWord hey_jarvis sensitivity."
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=30,
        help="Capture duration in seconds.",
    )
    parser.add_argument(
        "--sensitivity",
        type=float,
        default=settings.voice.wake_word_sensitivity,
        help="Wake-word detection threshold.",
    )
    parser.add_argument(
        "--device",
        type=int,
        default=-1,
        help="Input device index. Use -1 for the default input device.",
    )
    return parser.parse_args()


def load_model():  # noqa: ANN202
    from openwakeword.model import Model

    return Model(
        wakeword_models=[settings.voice.wake_word_model],
        inference_framework="onnx",
    )


def extract_score(prediction: Any) -> float:
    if isinstance(prediction, dict):
        return float(
            prediction.get(
                settings.voice.wake_word_model,
                max(prediction.values(), default=0.0),
            )
        )
    return 0.0


def summarize(frames: list[dict]) -> dict[str, float | int]:
    scores = [float(frame["score"]) for frame in frames]
    max_score = max(scores, default=0.0)
    return {
        "max_score": max_score,
        "mean_score": mean(scores) if scores else 0.0,
        "detection_count": sum(1 for frame in frames if frame["detected"]),
        "suggested_sensitivity": round(max_score * 0.9, 2),
    }


def csv_path_for_now() -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return Path(__file__).resolve().parent / f"wake_diag_{timestamp}.csv"


def save_frames_csv(frames: list[dict], output_path: Path) -> None:
    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(frames)


def print_frame(timestamp_ms: int, score: float, detected: bool, frame_index: int) -> None:
    if detected or frame_index % 5 == 0:
        suffix = " | [DETECTED]" if detected else ""
        print(f"T+{timestamp_ms:6d}ms | score={score:.4f}{suffix}")


def run_capture(duration: int, sensitivity: float, device: int) -> tuple[list[dict], Path]:
    import pyaudio
    import numpy as np

    model = load_model()
    frames: list[dict] = []
    output_path = csv_path_for_now()
    total_frames = max(1, int((duration * 1000) / FRAME_DURATION_MS))

    audio = pyaudio.PyAudio()
    stream_kwargs = {
        "format": pyaudio.paInt16,
        "channels": 1,
        "rate": SAMPLE_RATE,
        "input": True,
        "frames_per_buffer": FRAME_SAMPLES,
    }
    if device >= 0:
        stream_kwargs["input_device_index"] = device

    stream = audio.open(**stream_kwargs)
    try:
        for frame_index in range(1, total_frames + 1):
            raw_frame = stream.read(FRAME_SAMPLES, exception_on_overflow=False)
            prediction = model.predict(np.frombuffer(raw_frame, dtype=np.int16))
            score = extract_score(prediction)
            timestamp_ms = (frame_index - 1) * FRAME_DURATION_MS
            detected = score >= sensitivity
            frame_info = {
                "timestamp_ms": timestamp_ms,
                "score": score,
                "detected": detected,
            }
            frames.append(frame_info)
            print_frame(timestamp_ms, score, detected, frame_index)
    except KeyboardInterrupt:
        print("\nCapture interrupted. Saving partial results.")
    finally:
        stream.stop_stream()
        stream.close()
        audio.terminate()
        save_frames_csv(frames, output_path)

    return frames, output_path


def print_summary(summary: dict[str, float | int], output_path: Path) -> None:
    print(f"Saved CSV: {output_path}")
    print(f"max_score={summary['max_score']:.4f}")
    print(f"mean_score={summary['mean_score']:.4f}")
    print(f"detection_count={summary['detection_count']}")
    print(f"suggested_sensitivity={summary['suggested_sensitivity']:.2f}")


def main() -> None:
    args = parse_args()
    frames, output_path = run_capture(
        duration=args.duration,
        sensitivity=args.sensitivity,
        device=args.device,
    )
    print_summary(summarize(frames), output_path)


if __name__ == "__main__":
    main()
