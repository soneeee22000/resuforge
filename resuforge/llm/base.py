"""Abstract base class for LLM providers.

All LLM calls go through this interface. Implementations must return
validated Pydantic models via the instructor library.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class LLMProvider(ABC):
    """Abstract LLM provider interface.

    All providers must implement the complete() method, which takes
    system/user prompts and a Pydantic response model, and returns
    a validated instance of that model.
    """

    @abstractmethod
    def complete(
        self,
        *,
        system: str,
        user: str,
        response_model: type[T],
        temperature: float = 0.3,
        max_tokens: int = 4000,
    ) -> T:
        """Send a completion request to the LLM.

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
        ...
