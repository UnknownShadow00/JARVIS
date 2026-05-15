from __future__ import annotations

import ipaddress
import os
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, ValidationError, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.yaml"
OLLAMA_BASE_URL_ENV = "JARVIS_OLLAMA_BASE_URL"


def _is_loopback_host(host: str) -> bool:
    normalized = host.strip().lower()
    if normalized == "localhost":
        return True
    try:
        return ipaddress.ip_address(normalized).is_loopback
    except ValueError:
        return False


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
    dictation_enabled: bool
    dictation_hotkey: str
    dictation_type_out: bool
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
    remote_access_enabled: bool = False
    enable_voice_on_startup: bool = False
    enable_hotkey_listener: bool = False

    @model_validator(mode="after")
    def validate_localhost_default(self) -> "ServerConfig":
        if not self.remote_access_enabled and not _is_loopback_host(self.host):
            raise ValueError(
                "server.host must be localhost/loopback unless server.remote_access_enabled is true"
            )
        return self


class ResourceModeConfig(StrictModel):
    enabled: bool = True
    idle_timeout_minutes: int = 10
    deep_sleep_timeout_minutes: int = 60
    keep_wake_listener_in_light_sleep: bool = True
    keep_wake_listener_in_deep_sleep: bool = False
    auto_light_sleep: bool = True
    auto_deep_sleep: bool = True
    stop_server_on_auto_deep_sleep: bool = True
    preload_primary_model_on_wake: bool = False
    preload_keep_alive: str = "5m"


class MemoryConfig(StrictModel):
    mem0_enabled: bool
    mem0_base_url: str
    chromadb_enabled: bool
    chromadb_path: str
    chromadb_collection: str
    index_paths: list[str]
    graphiti_enabled: bool
    neo4j_uri: str
    neo4j_user: str
    neo4j_password_env: str


class ToolsConfig(StrictModel):
    obsidian_enabled: bool
    obsidian_vault_path: str


class RoutingConfig(StrictModel):
    embedding_enabled: bool
    embedding_model: str
    embedding_top_k: int


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
    resource_mode: ResourceModeConfig
    memory: MemoryConfig
    tools: ToolsConfig
    routing: RoutingConfig
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

    if os.environ.get(OLLAMA_BASE_URL_ENV) and isinstance(raw_config.get("models"), dict):
        raw_config["models"]["ollama_base_url"] = os.environ[OLLAMA_BASE_URL_ENV]

    try:
        return Settings.model_validate(raw_config)
    except ValidationError as exc:
        raise ValueError(f"Invalid config file {resolved_path}: {exc}") from exc


settings = load_settings()
