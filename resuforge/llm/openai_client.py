"""OpenAI GPT LLM provider implementation."""

from __future__ import annotations

from resuforge.llm.base import LLMProvider


class OpenAIClient(LLMProvider):
    """LLM provider using OpenAI's GPT API via instructor.

    Fallback provider when Anthropic is not configured.
    Uses instructor for structured output validation.
    """

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        """Initialize the OpenAI client.

        Args:
            api_key: OpenAI API key. Falls back to OPENAI_API_KEY env var.
            model: Model identifier. Defaults to gpt-4o.
        """
        # TODO: Initialize openai client with instructor
        raise NotImplementedError("OpenAI client not yet implemented")

    def complete(self, **kwargs: object) -> object:  # type: ignore[override]
        """Send a completion request to GPT."""
        raise NotImplementedError("OpenAI client not yet implemented")
