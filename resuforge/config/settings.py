"""Configuration management for ResuForge.

Config is stored at ~/.resuforge/config.yaml and loaded at startup.
API keys can also come from environment variables.

Priority: env vars > config file > defaults.
"""

from __future__ import annotations

import os
from pathlib import Path

import yaml
from pydantic import BaseModel, Field

CONFIG_DIR = Path.home() / ".resuforge"
CONFIG_FILE = CONFIG_DIR / "config.yaml"

DEFAULT_MODEL = "claude-3-5-sonnet-20241022"
DEFAULT_PROVIDER = "anthropic"


class ResuForgeConfig(BaseModel):
    """Application configuration."""

    default_model: str = DEFAULT_MODEL
    provider: str = DEFAULT_PROVIDER
    default_resume: str | None = None
    output_format: str = "tex"
    cover_letter_tone: str = "professional"
    anthropic_api_key: str | None = Field(default=None, exclude=True)
    openai_api_key: str | None = Field(default=None, exclude=True)


def load_config() -> ResuForgeConfig:
    """Load configuration from file and environment variables.

    Priority: env vars > config file > defaults.

    Returns:
        A validated ResuForgeConfig instance.
    """
    # Start with defaults
    data: dict[str, object] = {}

    # Layer 2: Override with config file if exists
    if CONFIG_FILE.exists():
        raw = CONFIG_FILE.read_text(encoding="utf-8")
        file_data = yaml.safe_load(raw)
        if isinstance(file_data, dict):
            data.update(file_data)

    # Layer 3: Override with env vars
    env_model = os.environ.get("RESUFORGE_MODEL")
    if env_model:
        data["default_model"] = env_model

    env_provider = os.environ.get("RESUFORGE_PROVIDER")
    if env_provider:
        data["provider"] = env_provider

    env_anthropic = os.environ.get("ANTHROPIC_API_KEY")
    if env_anthropic:
        data["anthropic_api_key"] = env_anthropic

    env_openai = os.environ.get("OPENAI_API_KEY")
    if env_openai:
        data["openai_api_key"] = env_openai

    return ResuForgeConfig(**data)


def save_config(config: ResuForgeConfig) -> None:
    """Save configuration to ~/.resuforge/config.yaml.

    API keys are excluded from the saved file for security.

    Args:
        config: The configuration to persist.
    """
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    # model_dump excludes fields with exclude=True (API keys)
    data = config.model_dump()

    # Remove None values for cleaner YAML
    clean_data = {k: v for k, v in data.items() if v is not None}

    CONFIG_FILE.write_text(
        yaml.dump(clean_data, default_flow_style=False),
        encoding="utf-8",
    )
