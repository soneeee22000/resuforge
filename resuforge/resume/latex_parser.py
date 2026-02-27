"""LaTeX resume parser — converts .tex files to ResumeIR.

Strategy: Regex + heuristic section detection. We identify known section
patterns and extract content between them. Unknown sections are stored
in raw_sections for verbatim passthrough.

This is the most critical module. Round-trip tests (parse -> render -> parse)
must pass for all supported templates.
"""

from __future__ import annotations

from pathlib import Path

from resuforge.resume.ir_schema import ResumeIR


def parse_latex(source: str | Path) -> ResumeIR:
    """Parse a LaTeX resume file or string into a ResumeIR.

    Args:
        source: Either a file path to a .tex file or a LaTeX string.

    Returns:
        A ResumeIR representing the structured resume content.

    Raises:
        FileNotFoundError: If source is a path that doesn't exist.
        ValueError: If the LaTeX content cannot be parsed.
    """
    _ = source  # Will be used when parser is implemented

    # TODO: Implement LaTeX parsing logic
    # 1. Split preamble from document body
    # 2. Detect custom commands (\newcommand, \def)
    # 3. Identify sections by \section{} or custom section commands
    # 4. Extract header info (name, email, links)
    # 5. Parse experience entries with bullets
    # 6. Parse education entries
    # 7. Parse skills categories
    # 8. Parse projects
    # 9. Store unknown sections in raw_sections
    raise NotImplementedError("LaTeX parser not yet implemented")
