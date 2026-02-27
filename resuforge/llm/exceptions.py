"""LLM-specific exceptions."""

from __future__ import annotations


class LLMError(Exception):
    """Raised when an LLM API call fails after retries.

    Attributes:
        message: Human-readable error description.
        provider: The LLM provider that failed (e.g., 'anthropic', 'openai').
        status_code: HTTP status code if available.
    """

    def __init__(
        self,
        message: str,
        provider: str = "unknown",
        status_code: int | None = None,
    ) -> None:
        """Initialize LLMError.

        Args:
            message: Error description.
            provider: Provider name.
            status_code: HTTP status code.
        """
        self.provider = provider
        self.status_code = status_code
        super().__init__(message)
