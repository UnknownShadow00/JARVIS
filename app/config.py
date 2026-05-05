from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict


CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.yaml"


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ModelsConfig(StrictModel):
    main: str
    coder: str
    router: str
    vision: str
    ollama_base_url: str
    main_context: int
    coder_context: int
    router_context: int
    vision_context: int


class SafetyConfig(StrictModel):
    approval_mode: str
    dry_run: bool
    confidence_threshold: float
    max_tool_chain: int


class VoiceConfig(StrictModel):
    wake_word_model: str
    wake_word_sensitivity: float
    vad_aggressiveness: int
    stt_model: str
    stt_device: str
    stt_compute_type: str
    tts_engine: str
    voice_clone_path: str
    piper_model_path: str
    piper_config_path: str
    kokoro_voice: str
    kokoro_speed: float
    push_to_talk_key: str
    input_device_index: int
    output_device_index: int


class BootConfig(StrictModel):
    enabled: bool
    music_file: str
    music_volume: float
    animation_delay_ms: int
    status_report: bool
    report_items: list[str]


class ServerConfig(StrictModel):
    host: str
    port: int
    websocket_path: str
    ue5_enabled: bool
    cors_origins: list[str]
    tailscale_hostname: str


class MemoryConfig(StrictModel):
    mem0_enabled: bool
    mem0_base_url: str
    chromadb_enabled: bool
    chromadb_path: str
    chromadb_collection: str
    index_paths: list[str]


class AgentConfig(StrictModel):
    hermes_enabled: bool
    hermes_cli_path: str
    hermes_workspace: str
    max_concurrent_tasks: int
    task_timeout_seconds: int
    checkpoint_interval_seconds: int


class CommsConfig(StrictModel):
    discord_enabled: bool
    discord_token: str
    discord_channel_id: str
    telegram_enabled: bool
    telegram_token: str
    telegram_chat_id: str
    require_approval_for_remote: bool


class ComputerConfig(StrictModel):
    use_open_computer_use: bool
    use_open_interpreter: bool
    open_interpreter_api_base: str
    open_interpreter_model: str
    screenshot_format: str
    screenshot_quality: int
    gesture_enabled: bool
    gesture_camera_index: int


class PathsConfig(StrictModel):
    projects_dir: str
    downloads_dir: str
    datasheets_dir: str
    logs_dir: str
    models_dir: str
    assets_dir: str


class LoggingConfig(StrictModel):
    audit_log: str
    level: str
    log_to_file: bool
    log_file: str
    max_log_size_mb: int


class OpenJarvisConfig(StrictModel):
    trace_logging_enabled: bool
    optimization_enabled: bool
    traces_dir: str


class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="forbid")

    models: ModelsConfig
    safety: SafetyConfig
    voice: VoiceConfig
    boot: BootConfig
    server: ServerConfig
    memory: MemoryConfig
    agent: AgentConfig
    comms: CommsConfig
    computer: ComputerConfig
    paths: PathsConfig
    logging: LoggingConfig
    openjarvis: OpenJarvisConfig


def load_settings(config_path: Path = CONFIG_PATH) -> Settings:
    resolved_path = config_path.resolve()

    if not resolved_path.is_file():
        raise FileNotFoundError(f"Config file not found: {resolved_path}")

    try:
        with resolved_path.open("r", encoding="utf-8") as config_file:
            raw_config: Any = yaml.safe_load(config_file)
    except yaml.YAMLError as exc:
        raise ValueError(f"Invalid YAML in config file {resolved_path}: {exc}") from exc
    except OSError as exc:
        raise OSError(f"Unable to read config file {resolved_path}: {exc}") from exc

    if not isinstance(raw_config, dict):
        raise ValueError(
            f"Invalid config structure in {resolved_path}: expected a YAML mapping at the top level."
        )

    try:
        return Settings.model_validate(raw_config)
    except ValidationError as exc:
        raise ValueError(f"Invalid config file {resolved_path}: {exc}") from exc


settings = load_settings()
