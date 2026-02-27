"""Unit tests for config management."""

from __future__ import annotations

from pathlib import Path

import pytest

from resuforge.config.settings import (
    DEFAULT_MODEL,
    DEFAULT_PROVIDER,
    ResuForgeConfig,
    load_config,
    save_config,
)

# ---------------------------------------------------------------------------
# Config model
# ---------------------------------------------------------------------------


class TestResuForgeConfig:
    """Tests for the config model."""

    def test_default_values(self) -> None:
        """Config has sensible defaults."""
        cfg = ResuForgeConfig()
        assert cfg.default_model == DEFAULT_MODEL
        assert cfg.provider == DEFAULT_PROVIDER
        assert cfg.output_format == "tex"

    def test_keys_excluded_from_dump(self) -> None:
        """Sensitive fields are excluded from model_dump."""
        fake = "FAKE_FOR_TEST"
        cfg = ResuForgeConfig(**{"anthropic_api_key": fake})
        dumped = cfg.model_dump()
        assert "anthropic_api_key" not in dumped


# ---------------------------------------------------------------------------
# load_config
# ---------------------------------------------------------------------------


class TestLoadConfig:
    """Tests for config loading."""

    def test_returns_config(self) -> None:
        """load_config returns a ResuForgeConfig."""
        cfg = load_config()
        assert isinstance(cfg, ResuForgeConfig)

    def test_env_overrides_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Environment variables override config values."""
        fake = "sk-ant-FAKE-ENV"
        monkeypatch.setenv("ANTHROPIC_API_KEY", fake)
        cfg = load_config()
        assert cfg.anthropic_api_key == fake

    def test_env_overrides_model(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """RESUFORGE_MODEL env var overrides default model."""
        monkeypatch.setenv("RESUFORGE_MODEL", "gpt-4o")
        cfg = load_config()
        assert cfg.default_model == "gpt-4o"

    def test_loads_from_yaml(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Loads config from YAML file if it exists."""
        import resuforge.config.settings as settings_mod

        config_dir = tmp_path / ".resuforge"
        config_dir.mkdir()
        config_file = config_dir / "config.yaml"
        config_file.write_text(
            "default_model: custom-model\nprovider: openai\ncover_letter_tone: casual\n",
            encoding="utf-8",
        )
        monkeypatch.setattr(settings_mod, "CONFIG_DIR", config_dir)
        monkeypatch.setattr(settings_mod, "CONFIG_FILE", config_file)

        cfg = load_config()
        assert cfg.default_model == "custom-model"
        assert cfg.provider == "openai"
        assert cfg.cover_letter_tone == "casual"


# ---------------------------------------------------------------------------
# save_config
# ---------------------------------------------------------------------------


class TestSaveConfig:
    """Tests for config saving."""

    def test_save_creates_file(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """save_config creates the config file."""
        import resuforge.config.settings as settings_mod

        config_dir = tmp_path / ".resuforge"
        config_file = config_dir / "config.yaml"
        monkeypatch.setattr(settings_mod, "CONFIG_DIR", config_dir)
        monkeypatch.setattr(settings_mod, "CONFIG_FILE", config_file)

        cfg = ResuForgeConfig(default_model="test-model")
        save_config(cfg)
        assert config_file.exists()

    def test_save_excludes_api_keys(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Saved config does not contain API keys."""
        import resuforge.config.settings as settings_mod

        config_dir = tmp_path / ".resuforge"
        config_file = config_dir / "config.yaml"
        monkeypatch.setattr(settings_mod, "CONFIG_DIR", config_dir)
        monkeypatch.setattr(settings_mod, "CONFIG_FILE", config_file)

        fake = "FAKE_FOR_TEST"
        cfg = ResuForgeConfig(**{"anthropic_api_key": fake})
        save_config(cfg)
        content = config_file.read_text(encoding="utf-8")
        assert fake not in content

    def test_save_roundtrip(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Config can be saved and loaded back."""
        import resuforge.config.settings as settings_mod

        config_dir = tmp_path / ".resuforge"
        config_file = config_dir / "config.yaml"
        monkeypatch.setattr(settings_mod, "CONFIG_DIR", config_dir)
        monkeypatch.setattr(settings_mod, "CONFIG_FILE", config_file)

        original = ResuForgeConfig(
            default_model="test-model",
            provider="openai",
            cover_letter_tone="casual",
        )
        save_config(original)
        loaded = load_config()
        assert loaded.default_model == "test-model"
        assert loaded.provider == "openai"
        assert loaded.cover_letter_tone == "casual"
