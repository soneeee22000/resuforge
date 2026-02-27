"""JD ingestion — parse job descriptions from text, PDF, or URL.

Normalizes JD input regardless of source format into a structured JDObject.
v0.1: regex-based extraction (no LLM). Easily swappable to LLM later.
"""

from __future__ import annotations

import re
from pathlib import Path

from resuforge.resume.ir_schema import JDObject

# Patterns for section headers in JDs
RE_REQUIRED = re.compile(
    r"(?:required\s+(?:skills|qualifications)|requirements|must\s+have|minimum\s+qualifications)"
    r"\s*:?\s*\r?\n",
    re.IGNORECASE,
)
RE_PREFERRED = re.compile(
    r"(?:preferred\s+(?:skills|qualifications)|nice\s+to\s+have|bonus|desired)" r"\s*:?\s*\r?\n",
    re.IGNORECASE,
)
RE_RESPONSIBILITIES = re.compile(
    r"(?:^|\n)\s*(?:responsibilities|what\s+you'?ll\s+do|key\s+duties)" r"\s*:?\s*\r?\n",
    re.IGNORECASE,
)
RE_EDUCATION = re.compile(
    r"(?:education|academic|degree)\s*:?\s*\r?\n?",
    re.IGNORECASE,
)
RE_EXPERIENCE_YEARS = re.compile(r"(\d+)\+?\s*years?\b", re.IGNORECASE)
RE_COMPANY = re.compile(r"(?:company|employer|organization)\s*:\s*(.+)", re.IGNORECASE)
RE_BULLET = re.compile(r"^\s*[-•*]\s*(.+)", re.MULTILINE)


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
    raw_text = _read_source(source)
    if not raw_text.strip():
        raise ValueError("JD content is empty")

    job_title = _extract_title(raw_text)
    company = _extract_company(raw_text)
    required_skills = _extract_bullet_section(raw_text, RE_REQUIRED)
    preferred_skills = _extract_bullet_section(raw_text, RE_PREFERRED)
    responsibilities = _extract_bullet_section(raw_text, RE_RESPONSIBILITIES)
    experience_years = _extract_experience_years(raw_text)
    education_requirement = _extract_education(raw_text)
    keywords = _extract_keywords(raw_text)

    return JDObject(
        raw_text=raw_text,
        job_title=job_title,
        company=company,
        required_skills=required_skills,
        preferred_skills=preferred_skills,
        responsibilities=responsibilities,
        keywords=keywords,
        experience_years=experience_years,
        education_requirement=education_requirement,
    )


def _read_source(source: str | Path) -> str:
    """Read JD content from various source types.

    Args:
        source: File path, URL, or raw text.

    Returns:
        Raw text content.
    """
    if isinstance(source, Path):
        if not source.exists():
            raise FileNotFoundError(f"JD file not found: {source}")
        return _read_file(source)

    # Check if it's a file path string
    if "\n" not in source and len(source) < 500:
        path = Path(source)
        if path.suffix in {".txt", ".pdf", ".md"} and path.exists():
            return _read_file(path)
        if path.suffix in {".txt", ".pdf", ".md"} and not path.exists():
            raise FileNotFoundError(f"JD file not found: {source}")

    return source


def _read_file(path: Path) -> str:
    """Read content from a file, handling PDF and text formats.

    Args:
        path: File path.

    Returns:
        Extracted text content.
    """
    if path.suffix.lower() == ".pdf":
        return _read_pdf(path)
    return path.read_text(encoding="utf-8")


def _read_pdf(path: Path) -> str:
    """Extract text from a PDF file.

    Args:
        path: Path to PDF file.

    Returns:
        Extracted text content.
    """
    from pypdf import PdfReader

    reader = PdfReader(str(path))
    pages: list[str] = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages.append(text)
    return "\n".join(pages)


def _extract_title(text: str) -> str | None:
    """Extract job title from the JD text.

    Looks for the title in the first few lines of the document.

    Args:
        text: Raw JD text.

    Returns:
        Job title string or None.
    """
    lines = text.strip().split("\n")
    for line in lines[:5]:
        line = line.strip()
        if not line:
            continue
        # Skip lines that look like metadata (Company:, Location:, etc.)
        if re.match(r"^(company|location|experience|salary|about|type)\s*:", line, re.IGNORECASE):
            continue
        # First non-metadata line is likely the title
        if len(line) < 100 and not line.startswith("-"):
            return line
    return None


def _extract_company(text: str) -> str | None:
    """Extract company name from JD text.

    Args:
        text: Raw JD text.

    Returns:
        Company name or None.
    """
    match = RE_COMPANY.search(text)
    if match:
        return match.group(1).strip()
    return None


def _extract_bullet_section(text: str, header_pattern: re.Pattern[str]) -> list[str]:
    """Extract bullet items from a section identified by a header pattern.

    Args:
        text: Raw JD text.
        header_pattern: Compiled regex for the section header.

    Returns:
        List of extracted bullet strings.
    """
    match = header_pattern.search(text)
    if not match:
        return []

    # Get text from after the header to the next section header or end
    start = match.end()
    remaining = text[start:]

    # Find next section boundary (any line that looks like a header)
    section_end = _find_next_section_boundary(remaining)
    section_text = remaining[:section_end] if section_end else remaining

    # Extract bullets
    bullets: list[str] = []
    for bullet_match in RE_BULLET.finditer(section_text):
        item = bullet_match.group(1).strip()
        if item and len(item) > 5:
            bullets.append(item)

    return bullets


def _find_next_section_boundary(text: str) -> int | None:
    """Find the position of the next section header.

    Args:
        text: Text to search.

    Returns:
        Position of next section header, or None if not found.
    """
    # Look for lines that are section headers (short lines followed by bullets or colon)
    patterns = [
        RE_REQUIRED,
        RE_PREFERRED,
        RE_RESPONSIBILITIES,
        RE_EDUCATION,
        re.compile(
            r"(?:about\s+(?:us|the|our)|benefits|perks|compensation|how\s+to\s+apply)"
            r"\s*:?\s*\n",
            re.IGNORECASE,
        ),
    ]
    earliest: int | None = None
    for pattern in patterns:
        match = pattern.search(text)
        if match and (earliest is None or match.start() < earliest):
            earliest = match.start()

    # Also check for standalone header-like lines
    header_pattern = re.compile(r"^\n[A-Z][A-Za-z\s]+:\s*$", re.MULTILINE)
    match = header_pattern.search(text)
    if match and (earliest is None or match.start() < earliest):
        earliest = match.start()

    return earliest


def _extract_experience_years(text: str) -> int | None:
    """Extract years of experience requirement.

    Args:
        text: Raw JD text.

    Returns:
        Integer years or None.
    """
    match = RE_EXPERIENCE_YEARS.search(text)
    if match:
        return int(match.group(1))
    return None


def _extract_education(text: str) -> str | None:
    """Extract education requirement.

    Args:
        text: Raw JD text.

    Returns:
        Education requirement string or None.
    """
    # Look for "Education:" section
    match = RE_EDUCATION.search(text)
    if match:
        start = match.end()
        remaining = text[start:]
        # Get next non-empty line
        for line in remaining.split("\n"):
            line = line.strip()
            if line and not line.startswith("#"):
                return line
    return None


def _extract_keywords(text: str) -> list[str]:
    """Extract key technical terms and keywords from the JD.

    Simple frequency-based extraction of capitalized technical terms.

    Args:
        text: Raw JD text.

    Returns:
        List of keyword strings.
    """
    # Look for technical terms (capitalized words, acronyms, tools)
    tech_pattern = re.compile(r"\b(?:[A-Z][a-z]+(?:\.[a-z]+)*|[A-Z]{2,})\b")
    words = tech_pattern.findall(text)

    # Count occurrences, filter noise
    noise = {
        "The",
        "We",
        "You",
        "Our",
        "Your",
        "This",
        "That",
        "Are",
        "About",
        "What",
        "How",
        "Join",
        "Will",
        "Must",
        "With",
        "Have",
        "Has",
        "Not",
        "Can",
        "May",
        "Should",
        "For",
        "From",
        "Into",
        "Over",
        "Each",
        "Any",
        "All",
        "Both",
    }
    counts: dict[str, int] = {}
    for word in words:
        if word not in noise and len(word) > 1:
            counts[word] = counts.get(word, 0) + 1

    # Return words that appear more than once, sorted by frequency
    keywords = sorted(
        (w for w, c in counts.items() if c >= 1),
        key=lambda w: counts[w],
        reverse=True,
    )
    return keywords[:20]
