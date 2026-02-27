"""JD ingestion — parse job descriptions from text, PDF, or URL.

Normalizes JD input regardless of source format into a structured JDObject.
Skill/keyword extraction is done via a single LLM call with structured output.
"""

from __future__ import annotations

from pathlib import Path

from resuforge.resume.ir_schema import JDObject


def parse_jd(source: str | Path) -> JDObject:
    """Parse a job description from a file path, URL, or raw text.

    Args:
        source: A file path (.txt, .pdf), URL, or raw JD text.

    Returns:
        A structured JDObject with extracted fields.

    Raises:
        FileNotFoundError: If source is a file path that doesn't exist.
        ValueError: If the JD content cannot be parsed.
    """
    # TODO: Implement JD parsing logic
    # 1. Detect source type (file path, URL, or raw text)
    # 2. Extract raw text (from PDF via pypdf, URL via httpx+trafilatura)
    # 3. Send to LLM for structured extraction (job title, skills, etc.)
    # 4. Return validated JDObject
    raise NotImplementedError("JD parser not yet implemented")
