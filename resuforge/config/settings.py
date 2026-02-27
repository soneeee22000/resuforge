"""Configuration management for ResuForge.

Config is stored at ~/.resuforge/config.yaml and loaded at startup.
API keys can also come from environment variables.
"""

from __future__ import annotations

from pathlib import Path

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
    # TODO: Implement config loading
    # 1. Load defaults
    # 2. Override with config file if exists
    # 3. Override with env vars (ANTHROPIC_API_KEY, OPENAI_API_KEY, etc.)
    return ResuForgeConfig()


def save_config(config: ResuForgeConfig) -> None:
    """Save configuration to ~/.resuforge/config.yaml.

    Args:
        config: The configuration to persist.
    """
    # TODO: Implement config saving
    # 1. Ensure CONFIG_DIR exists
    # 2. Write config to YAML (exclude sensitive fields)
    raise NotImplementedError("Config saving not yet implemented")
