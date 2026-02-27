"""Unit tests for the CLI — uses CliRunner with mocked LLM."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

from resuforge.cli.main import app
from resuforge.resume.ir_schema import Change
from resuforge.utils.diff import display_changes, format_changes_text

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"
RESUME_PATH = str(FIXTURES_DIR / "resumes" / "simple_article.tex")
JD_PATH = str(FIXTURES_DIR / "jds" / "software_engineer.txt")


# ---------------------------------------------------------------------------
# CLI basic tests
# ---------------------------------------------------------------------------


class TestCLIBasic:
    """Tests for basic CLI functionality."""

    def test_version_flag(self) -> None:
        """--version prints version and exits."""
        runner = CliRunner()
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output

    def test_help_flag(self) -> None:
        """--help prints usage and exits."""
        runner = CliRunner()
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "ResuForge" in result.output

    def test_tailor_help(self) -> None:
        """tailor --help shows command options."""
        runner = CliRunner()
        result = runner.invoke(app, ["tailor", "--help"])
        assert result.exit_code == 0
        assert "--resume" in result.output
        assert "--jd" in result.output
        assert "--dry-run" in result.output

    def test_tailor_missing_resume(self) -> None:
        """tailor without --resume exits with error."""
        runner = CliRunner()
        result = runner.invoke(app, ["tailor", "--jd", JD_PATH])
        assert result.exit_code != 0

    def test_tailor_missing_jd(self) -> None:
        """tailor without --jd exits with error."""
        runner = CliRunner()
        result = runner.invoke(app, ["tailor", "--resume", RESUME_PATH])
        assert result.exit_code != 0


# ---------------------------------------------------------------------------
# Tailor command with mocked LLM
# ---------------------------------------------------------------------------


class TestTailorCommand:
    """Tests for the tailor command with mocked pipeline."""

    @patch("resuforge.cli.main._run_tailor_pipeline")
    def test_tailor_calls_pipeline(self, mock_pipeline: object) -> None:
        """tailor command invokes the pipeline."""
        runner = CliRunner()
        runner.invoke(
            app,
            [
                "tailor",
                "--resume",
                RESUME_PATH,
                "--jd",
                JD_PATH,
                "--dry-run",
            ],
        )
        # The pipeline is called (may fail due to no API key, but call happens)
        assert mock_pipeline.called  # type: ignore[union-attr]


# ---------------------------------------------------------------------------
# Config command
# ---------------------------------------------------------------------------


class TestConfigCommand:
    """Tests for the config command."""

    def test_config_shows_defaults(self) -> None:
        """config with no flags shows current config."""
        runner = CliRunner()
        result = runner.invoke(app, ["config"])
        assert result.exit_code == 0
        assert "Provider" in result.output or "provider" in result.output.lower()

    def test_config_set_key_warning(self) -> None:
        """config --set-key warns about env vars."""
        runner = CliRunner()
        result = runner.invoke(app, ["config", "--set-key", "test-key"])
        assert result.exit_code == 0
        assert "environment" in result.output.lower()


# ---------------------------------------------------------------------------
# Diff display
# ---------------------------------------------------------------------------


class TestDiffDisplay:
    """Tests for the diff display utility."""

    def test_display_empty_changes(self) -> None:
        """display_changes handles empty list."""
        # Should not raise
        display_changes([])

    def test_display_with_changes(self, sample_changes: list[Change]) -> None:
        """display_changes handles a list of changes."""
        # Should not raise
        display_changes(sample_changes)

    def test_format_text_empty(self) -> None:
        """format_changes_text handles empty list."""
        result = format_changes_text([])
        assert "No changes" in result

    def test_format_text_with_changes(self, sample_changes: list[Change]) -> None:
        """format_changes_text produces readable output."""
        result = format_changes_text(sample_changes)
        assert "2 change(s)" in result
        assert "summary" in result
