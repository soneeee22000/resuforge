"""File utilities — reading, writing, and path management."""

from __future__ import annotations

from pathlib import Path


def read_file(path: str | Path) -> str:
    """Read a file and return its contents as a string.

    Args:
        path: Path to the file.

    Returns:
        File contents as a string.

    Raises:
        FileNotFoundError: If the file doesn't exist.
    """
    return Path(path).read_text(encoding="utf-8")


def write_file(path: str | Path, content: str) -> Path:
    """Write content to a file, creating parent directories if needed.

    Args:
        path: Output file path.
        content: Content to write.

    Returns:
        The resolved Path to the written file.
    """
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
    return output_path.resolve()
