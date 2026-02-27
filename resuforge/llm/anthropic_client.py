"""Anthropic Claude LLM provider implementation.

Uses the anthropic SDK with instructor for structured output.
Retry logic: 3 retries with exponential backoff on transient errors.
"""

from __future__ import annotations

import os
import time
from typing import TypeVar

import anthropic
import instructor
from pydantic import BaseModel

from resuforge.llm.base import LLMProvider
from resuforge.llm.exceptions import LLMError

T = TypeVar("T", bound=BaseModel)

DEFAULT_MODEL = "claude-3-5-sonnet-20241022"
MAX_RETRIES = 3
INITIAL_BACKOFF_SECONDS = 1.0


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

        Raises:
            LLMError: If no API key is found.
        """
        resolved_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not resolved_key:
            raise LLMError(
                "No Anthropic API key found. Set ANTHROPIC_API_KEY env var or pass api_key.",
                provider="anthropic",
            )

        self._model = model or DEFAULT_MODEL
        raw_client = anthropic.Anthropic(api_key=resolved_key)
        self._client = instructor.from_anthropic(raw_client)

    def complete(
        self,
        *,
        system: str,
        user: str,
        response_model: type[T],
        temperature: float = 0.3,
        max_tokens: int = 4000,
    ) -> T:
        """Send a completion request to Claude with structured output.

        Args:
            system: System prompt with instructions and constraints.
            user: User prompt with the actual task content.
            response_model: Pydantic model class for structured output.
            temperature: Sampling temperature (default 0.3 for precision).
            max_tokens: Maximum tokens in response.

        Returns:
            A validated instance of response_model.

        Raises:
            LLMError: If the API call fails after retries.
        """
        last_error: Exception | None = None

        for attempt in range(MAX_RETRIES):
            try:
                result: T = self._client.messages.create(
                    model=self._model,
                    max_tokens=max_tokens,
                    system=system,
                    messages=[{"role": "user", "content": user}],
                    response_model=response_model,
                    temperature=temperature,
                )
                return result
            except anthropic.RateLimitError as exc:
                last_error = exc
                _backoff(attempt)
            except anthropic.APIStatusError as exc:
                if exc.status_code >= 500:
                    last_error = exc
                    _backoff(attempt)
                else:
                    raise LLMError(
                        f"Anthropic API error: {exc.message}",
                        provider="anthropic",
                        status_code=exc.status_code,
                    ) from exc
            except anthropic.APIConnectionError as exc:
                last_error = exc
                _backoff(attempt)

        raise LLMError(
            f"Anthropic API failed after {MAX_RETRIES} retries: {last_error}",
            provider="anthropic",
        )


def _backoff(attempt: int) -> None:
    """Sleep with exponential backoff.

    Args:
        attempt: Current attempt number (0-indexed).
    """
    delay = INITIAL_BACKOFF_SECONDS * (2**attempt)
    time.sleep(delay)
