from __future__ import annotations

import argparse
import os
from pathlib import Path

import yaml


CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.yaml"

PROFILE_UPDATES = {
    "4070ti": {
        "main": "qwen3:14b",
        "coder": "qwen2.5-coder:14b",
    },
    "5090": {
        "main": "qwen3:32b",
        "coder": "qwen2.5-coder:32b",
        "vision": "qwen3-vl",
    },
}


def switch_models(profile: str, config_path: Path = CONFIG_PATH) -> None:
    with config_path.open("r", encoding="utf-8") as config_file:
        config = yaml.safe_load(config_file) or {}

    models = config.setdefault("models", {})
    models.update(PROFILE_UPDATES[profile])

    tmp_path = config_path.with_name(f"{config_path.name}.tmp")
    with tmp_path.open("w", encoding="utf-8", newline="\n") as tmp_file:
        yaml.safe_dump(config, tmp_file, sort_keys=False, allow_unicode=False)

    os.replace(tmp_path, config_path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Switch JARVIS model profiles.")
    parser.add_argument("--profile", required=True, choices=("4070ti", "5090"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    switch_models(args.profile)
    print(f"Switched to {args.profile} profile. Restart Ollama and JARVIS server to apply.")


if __name__ == "__main__":
    main()
