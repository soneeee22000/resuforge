"""Anthropic Claude LLM provider implementation."""

from __future__ import annotations

from resuforge.llm.base import LLMProvider


class AnthropicClient(LLMProvider):
    """LLM provider using Anthropic's Claude API via instructor.

    Default model: claude-3-5-sonnet-20241022 (configurable).
    Uses instructor for structured output validation.
    Retry logic: 3 retries with exponential backoff.
    """

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        """Initialize the Anthropic client.

        Args:
            api_key: Anthropic API key. Falls back to ANTHROPIC_API_KEY env var.
            model: Model identifier. Defaults to claude-3-5-sonnet-20241022.
        """
        # TODO: Initialize anthropic client with instructor
        raise NotImplementedError("Anthropic client not yet implemented")

    def complete(self, **kwargs: object) -> object:  # type: ignore[override]
        """Send a completion request to Claude."""
        raise NotImplementedError("Anthropic client not yet implemented")
