"""Unit tests for the LLM provider — all mocked, no API calls."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from pydantic import BaseModel

from resuforge.llm.base import LLMProvider
from resuforge.llm.exceptions import LLMError
from resuforge.resume.ir_schema import GapAnalysis
from tests.conftest import MockLLMProvider

# ---------------------------------------------------------------------------
# MockLLMProvider tests
# ---------------------------------------------------------------------------


class TestMockLLMProvider:
    """Tests for the mock LLM provider used in downstream tests."""

    def test_mock_is_llm_provider(self) -> None:
        """Mock implements the LLMProvider interface."""
        mock = MockLLMProvider()
        assert isinstance(mock, LLMProvider)

    def test_mock_returns_gap_analysis(self) -> None:
        """Mock returns a default GapAnalysis."""
        mock = MockLLMProvider()
        result = mock.complete(
            system="test",
            user="test",
            response_model=GapAnalysis,
        )
        assert isinstance(result, GapAnalysis)
        assert len(result.strengths) > 0

    def test_mock_records_calls(self) -> None:
        """Mock records each call for assertion."""
        mock = MockLLMProvider()
        mock.complete(system="sys", user="usr", response_model=GapAnalysis)
        assert len(mock.calls) == 1
        assert mock.calls[0]["system"] == "sys"
        assert mock.calls[0]["user"] == "usr"

    def test_mock_custom_responses(self) -> None:
        """Mock uses custom response overrides."""
        custom_gap = GapAnalysis(strengths=["custom"], gaps=[], opportunities=[])
        mock = MockLLMProvider(responses={GapAnalysis: custom_gap})
        result = mock.complete(
            system="test",
            user="test",
            response_model=GapAnalysis,
        )
        assert result.strengths == ["custom"]

    def test_mock_raises_for_unknown_type(self) -> None:
        """Mock raises ValueError for unconfigured types."""

        class UnknownModel(BaseModel):
            """A model the mock doesn't know about."""

            value: str

        mock = MockLLMProvider()
        with pytest.raises(ValueError, match="No default mock response"):
            mock.complete(system="test", user="test", response_model=UnknownModel)


# ---------------------------------------------------------------------------
# LLMError tests
# ---------------------------------------------------------------------------


class TestLLMError:
    """Tests for the LLMError exception."""

    def test_error_message(self) -> None:
        """LLMError has correct message."""
        error = LLMError("API failed", provider="anthropic", status_code=429)
        assert str(error) == "API failed"
        assert error.provider == "anthropic"
        assert error.status_code == 429

    def test_error_defaults(self) -> None:
        """LLMError has sensible defaults."""
        error = LLMError("oops")
        assert error.provider == "unknown"
        assert error.status_code is None


# ---------------------------------------------------------------------------
# AnthropicClient tests (mocked)
# ---------------------------------------------------------------------------


FAKE_KEY = "sk-ant-FAKE-FOR-TEST"


class TestAnthropicClient:
    """Tests for the Anthropic client with mocked API calls."""

    def test_init_with_explicit_key(self) -> None:
        """Client initializes with explicit key."""
        from resuforge.llm.anthropic_client import AnthropicClient

        client = AnthropicClient(FAKE_KEY)
        assert isinstance(client, LLMProvider)

    def test_init_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Client reads key from environment."""
        monkeypatch.setenv("ANTHROPIC_API_KEY", FAKE_KEY)
        from resuforge.llm.anthropic_client import AnthropicClient

        client = AnthropicClient()
        assert isinstance(client, LLMProvider)

    def test_init_no_key_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Client raises LLMError without key."""
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        from resuforge.llm.anthropic_client import AnthropicClient

        with pytest.raises(LLMError, match="API key"):
            AnthropicClient()

    @patch("resuforge.llm.anthropic_client.instructor")
    @patch("resuforge.llm.anthropic_client.anthropic")
    def test_complete_calls_instructor(
        self, mock_anthropic: MagicMock, mock_instructor: MagicMock
    ) -> None:
        """Complete method calls instructor for structured output."""
        from resuforge.llm.anthropic_client import AnthropicClient

        mock_client = MagicMock()
        mock_anthropic.Anthropic.return_value = mock_client
        mock_instructor_client = MagicMock()
        mock_instructor.from_anthropic.return_value = mock_instructor_client
        mock_instructor_client.messages.create.return_value = GapAnalysis(
            strengths=["test"],
            gaps=[],
            opportunities=[],
        )

        client = AnthropicClient(FAKE_KEY)
        result = client.complete(
            system="system prompt",
            user="user prompt",
            response_model=GapAnalysis,
        )

        assert isinstance(result, GapAnalysis)
        assert result.strengths == ["test"]
        mock_instructor_client.messages.create.assert_called_once()
