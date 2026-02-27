"""LaTeX resume parser — converts .tex files to ResumeIR.

Strategy: Regex + heuristic section detection. We identify known section
patterns and extract content between them. Unknown sections are stored
in raw_sections for verbatim passthrough.

This is the most critical module. Round-trip tests (parse -> render -> parse)
must pass for all supported templates.
"""

from __future__ import annotations

import re
from pathlib import Path

from resuforge.resume.ir_schema import (
    BulletPoint,
    EducationEntry,
    ExperienceEntry,
    HeaderSection,
    Link,
    ProjectEntry,
    ResumeIR,
    SkillCategory,
)

# Section name aliases → normalized names
SECTION_ALIASES: dict[str, str] = {
    "summary": "summary",
    "professional summary": "summary",
    "objective": "summary",
    "experience": "experience",
    "work experience": "experience",
    "professional experience": "experience",
    "employment": "experience",
    "education": "education",
    "skills": "skills",
    "technical skills": "skills",
    "core competencies": "skills",
    "projects": "projects",
    "personal projects": "projects",
    "selected projects": "projects",
}

# Regex patterns
RE_DOCUMENTCLASS = re.compile(r"\\documentclass.*?\{.*?\}")
RE_BEGIN_DOC = re.compile(r"\\begin\{document\}")
RE_END_DOC = re.compile(r"\\end\{document\}")
RE_SECTION = re.compile(r"\\section\*?\{(.+?)\}")
RE_NEWCOMMAND = re.compile(r"\\(?:newcommand|renewcommand|def).*?(?:\n(?=\\)|$)", re.DOTALL)
RE_HREF = re.compile(r"\\href\{([^}]+)\}\{([^}]+)\}")
RE_TEXTBF = re.compile(r"\\textbf\{([^}]+)\}")
RE_TEXTIT = re.compile(r"\\textit\{([^}]+)\}")
RE_HFILL = re.compile(r"\\hfill\s*")
RE_ITEM = re.compile(r"\\item\s+(.*?)(?=\\item|\Z)", re.DOTALL)
RE_ITEMIZE_BLOCK = re.compile(r"\\begin\{itemize\}.*?\n(.*?)\\end\{itemize\}", re.DOTALL)
RE_EMAIL = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
RE_PHONE = re.compile(r"\+?[\d][\d\s\-().]{6,}")
RE_LARGE_NAME = re.compile(r"\{\\(?:LARGE|Huge|huge|HUGE|Large)\s+\\textbf\{([^}]+)\}\}")
RE_RESUME_HEADING = re.compile(r"\\resumeHeading\{([^}]*)\}\{([^}]*)\}\{([^}]*)\}\{([^}]*)\}")
RE_RESUME_SUBHEADING = re.compile(r"\\resumeSubheading\{([^}]*)\}\{([^}]*)\}")


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
    content = _read_source(source)
    if not content.strip():
        raise ValueError("LaTeX content is empty")

    preamble, body = _split_preamble(content)
    custom_commands = _extract_custom_commands(preamble)
    sections = _split_into_sections(body)

    header = _parse_header(body, sections)
    section_order: list[str] = []
    summary: str | None = None
    experience: list[ExperienceEntry] = []
    education: list[EducationEntry] = []
    skills: list[SkillCategory] = []
    projects: list[ProjectEntry] = []
    raw_sections: dict[str, str] = {}

    for section_name, section_content in sections:
        normalized = _normalize_section_name(section_name)
        section_order.append(normalized)

        if normalized == "summary":
            summary = _parse_summary(section_content)
        elif normalized == "experience":
            experience = _parse_experience(section_content)
        elif normalized == "education":
            education = _parse_education(section_content)
        elif normalized == "skills":
            skills = _parse_skills(section_content)
        elif normalized == "projects":
            projects = _parse_projects(section_content)
        else:
            raw_sections[normalized] = section_content.strip()

    return ResumeIR(
        preamble=preamble.strip(),
        header=header,
        summary=summary,
        experience=experience,
        education=education,
        skills=skills,
        projects=projects,
        raw_sections=raw_sections,
        custom_commands=custom_commands,
        section_order=section_order,
    )


def _read_source(source: str | Path) -> str:
    """Read LaTeX content from a file path or return string directly.

    Args:
        source: File path or LaTeX string.

    Returns:
        Raw LaTeX content as string.
    """
    if isinstance(source, Path):
        if not source.exists():
            raise FileNotFoundError(f"Resume file not found: {source}")
        return source.read_text(encoding="utf-8")

    # Check if string looks like a file path
    if not source.strip().startswith("\\") and Path(source).suffix == ".tex":
        path = Path(source)
        if path.exists():
            return path.read_text(encoding="utf-8")
        raise FileNotFoundError(f"Resume file not found: {source}")

    return source


def _split_preamble(content: str) -> tuple[str, str]:
    """Split LaTeX content into preamble and document body.

    Args:
        content: Full LaTeX file content.

    Returns:
        Tuple of (preamble, body) where body excludes begin/end document tags.
    """
    match = RE_BEGIN_DOC.search(content)
    if match is None:
        return "", content

    preamble = content[: match.start()].strip()
    rest = content[match.end() :]

    end_match = RE_END_DOC.search(rest)
    body = rest[: end_match.start()] if end_match is not None else rest

    return preamble, body


def _extract_custom_commands(preamble: str) -> list[str]:
    """Extract custom command definitions from the preamble.

    Args:
        preamble: LaTeX preamble text.

    Returns:
        List of custom command definition strings.
    """
    commands: list[str] = []
    # Match \newcommand and \renewcommand with their full definitions
    pattern = re.compile(
        r"(\\(?:newcommand|renewcommand)\{[^}]+\}(?:\[\d+\])?\{[^}]*(?:\{[^}]*\}[^}]*)*\})",
        re.DOTALL,
    )
    for match in pattern.finditer(preamble):
        commands.append(match.group(1).strip())

    # Also match \def commands
    def_pattern = re.compile(r"(\\def\\[a-zA-Z]+.*?\{.*?\})", re.DOTALL)
    for match in def_pattern.finditer(preamble):
        commands.append(match.group(1).strip())

    return commands


def _split_into_sections(body: str) -> list[tuple[str, str]]:
    """Split the document body into named sections.

    Args:
        body: Document body (between begin/end document).

    Returns:
        List of (section_name, section_content) tuples.
    """
    sections: list[tuple[str, str]] = []
    matches = list(RE_SECTION.finditer(body))

    for i, match in enumerate(matches):
        section_name = match.group(1).strip()
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        section_content = body[start:end]
        sections.append((section_name, section_content))

    return sections


def _normalize_section_name(name: str) -> str:
    """Normalize a section name to a canonical form.

    Args:
        name: Raw section name from LaTeX.

    Returns:
        Normalized section identifier.
    """
    lower = name.strip().lower()
    return SECTION_ALIASES.get(lower, lower)


def _parse_header(body: str, sections: list[tuple[str, str]]) -> HeaderSection:
    """Extract header information from the document body.

    Header is typically in a center environment before the first section.

    Args:
        body: Full document body.
        sections: Parsed sections list.

    Returns:
        Populated HeaderSection.
    """
    # Get text before first section
    first_section_match = RE_SECTION.search(body)
    header_text = body[: first_section_match.start()] if first_section_match else body

    name = _extract_name(header_text)
    email = _extract_email(header_text)
    phone = _extract_phone(header_text)
    location = _extract_location(header_text)
    links = _extract_links(header_text)

    return HeaderSection(
        name=name,
        email=email,
        phone=phone,
        location=location,
        links=links,
    )


def _extract_name(header_text: str) -> str:
    """Extract name from header block.

    Args:
        header_text: Text before first section.

    Returns:
        Extracted name string.
    """
    # Try {\LARGE \textbf{Name}} or {\huge \textbf{Name}} pattern
    match = RE_LARGE_NAME.search(header_text)
    if match:
        return match.group(1).strip()

    # Fallback: first \textbf in header
    match = RE_TEXTBF.search(header_text)
    if match:
        return match.group(1).strip()

    return "Unknown"


def _extract_email(header_text: str) -> str | None:
    """Extract email address from header text.

    Args:
        header_text: Text before first section.

    Returns:
        Email string or None.
    """
    match = RE_EMAIL.search(header_text)
    return match.group(0) if match else None


def _extract_phone(header_text: str) -> str | None:
    """Extract phone number from header text.

    Args:
        header_text: Text before first section.

    Returns:
        Phone string or None.
    """
    match = RE_PHONE.search(header_text)
    if match:
        phone = match.group(0).strip()
        # Clean up trailing non-digit chars
        phone = re.sub(r"[^\d+\-() ]$", "", phone).strip()
        return phone
    return None


def _extract_location(header_text: str) -> str | None:
    """Extract location from header text.

    Looks for patterns like 'City, ST' after separators.

    Args:
        header_text: Text before first section.

    Returns:
        Location string or None.
    """
    # Look for City, State/Country pattern
    # Common: after last pipe/enspace separator on contact line
    lines = header_text.split("\n")
    for line in lines:
        # Skip name line and link lines
        if (RE_LARGE_NAME.search(line) or "\\href" in line) and (
            "\\href" not in line or "|" not in line
        ):
            continue
        # Look for city, state pattern
        loc_match = re.search(
            r"(?:\\enspace\s*\|\s*\\enspace\s*|\\quad\s*|\|\s*)"
            r"([A-Z][a-zA-Z\s]+,\s*[A-Z]{2,}(?:\s|\\\\|$))",
            line,
        )
        if loc_match:
            return loc_match.group(1).strip().rstrip("\\").strip()

    return None


def _extract_links(header_text: str) -> list[Link]:
    """Extract hyperlinks from header text.

    Args:
        header_text: Text before first section.

    Returns:
        List of Link objects.
    """
    links: list[Link] = []
    for match in RE_HREF.finditer(header_text):
        url = match.group(1)
        label = match.group(2)
        links.append(Link(label=label, url=url))
    return links


def _parse_summary(content: str) -> str:
    """Extract summary text from section content.

    Args:
        content: Raw content of the summary section.

    Returns:
        Cleaned summary text.
    """
    text = _strip_latex_commands(content).strip()
    # Remove leading/trailing whitespace and normalize
    return " ".join(text.split())


def _parse_experience(content: str) -> list[ExperienceEntry]:
    """Parse experience section into entries.

    Handles two formats:
    1. Standard: \\textbf{Title} \\hfill Dates \\\\ \\textit{Company} \\hfill Location
    2. Custom: \\resumeHeading{Title}{Dates}{Company}{Location}

    Args:
        content: Raw content of the experience section.

    Returns:
        List of ExperienceEntry objects.
    """
    # Try custom \resumeHeading format first
    custom_matches = list(RE_RESUME_HEADING.finditer(content))
    if custom_matches:
        return _parse_experience_custom(content, custom_matches)

    # Standard format: split by \textbf entries
    return _parse_experience_standard(content)


def _parse_experience_custom(
    content: str,
    matches: list[re.Match[str]],
) -> list[ExperienceEntry]:
    """Parse experience entries using \\resumeHeading format.

    Args:
        content: Section content.
        matches: Regex matches for resumeHeading.

    Returns:
        List of ExperienceEntry objects.
    """
    entries: list[ExperienceEntry] = []
    for i, match in enumerate(matches):
        title = match.group(1).strip()
        dates = match.group(2).strip()
        company = match.group(3).strip()
        location = match.group(4).strip()

        # Get bullets between this heading and the next
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        block = content[start:end]
        bullets = _extract_bullets(block, "exp", len(entries))

        entries.append(
            ExperienceEntry(
                company=company,
                title=title,
                dates=dates,
                location=location or None,
                bullets=bullets,
            )
        )
    return entries


def _parse_experience_standard(content: str) -> list[ExperienceEntry]:
    """Parse experience entries using standard \\textbf/\\textit format.

    Args:
        content: Section content.

    Returns:
        List of ExperienceEntry objects.
    """
    entries: list[ExperienceEntry] = []

    # Split on \textbf which marks entry starts
    textbf_matches = list(RE_TEXTBF.finditer(content))
    # Filter to only those that look like job titles (followed by \hfill)
    entry_starts: list[int] = []
    entry_titles: list[str] = []
    for m in textbf_matches:
        after = content[m.end() : m.end() + 20]
        if "\\hfill" in after or "hfill" in after:
            entry_starts.append(m.start())
            entry_titles.append(m.group(1))

    for i, (start, title) in enumerate(zip(entry_starts, entry_titles, strict=True)):
        end = entry_starts[i + 1] if i + 1 < len(entry_starts) else len(content)
        block = content[start:end]

        dates = _extract_dates_from_line(block)
        company = _extract_company(block)
        location = _extract_entry_location(block)
        bullets = _extract_bullets(block, "exp", len(entries))

        entries.append(
            ExperienceEntry(
                company=company,
                title=title,
                dates=dates,
                location=location,
                bullets=bullets,
            )
        )

    return entries


def _extract_dates_from_line(block: str) -> str:
    """Extract date range from an entry block.

    Args:
        block: Text block for a single entry.

    Returns:
        Date string (e.g., '2022 -- Present').
    """
    # Look for date patterns after \hfill
    date_match = re.search(
        r"\\hfill\s*((?:\d{4}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
        r"(?:\w*)?\.?\s+\d{4})\s*(?:--?|–|—|to)\s*(?:\d{4}|Present"
        r"|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)(?:\w*)?\.?\s+\d{4}))",
        block,
    )
    if date_match:
        return date_match.group(1).strip()

    # Try simpler year pattern
    simple_match = re.search(r"(\d{4}\s*(?:--?|–|—)\s*(?:\d{4}|Present))", block)
    if simple_match:
        return simple_match.group(1).strip()

    return ""


def _extract_company(block: str) -> str:
    """Extract company name from an entry block.

    Args:
        block: Text block for a single entry.

    Returns:
        Company name string.
    """
    match = RE_TEXTIT.search(block)
    if match:
        return match.group(1).strip()
    return ""


def _extract_entry_location(block: str) -> str | None:
    """Extract location from an entry block.

    Args:
        block: Text block for a single entry.

    Returns:
        Location string or None.
    """
    # Location typically on the \textit line after \hfill
    lines = block.split("\n")
    for line in lines:
        if "\\textit" in line and "\\hfill" in line:
            loc_match = re.search(r"\\hfill\s*(.+?)(?:\\\\|\s*$)", line)
            if loc_match:
                loc = loc_match.group(1).strip()
                if loc and not loc.startswith("\\"):
                    return loc
    return None


def _extract_bullets(block: str, prefix: str, entry_idx: int) -> list[BulletPoint]:
    """Extract bullet points from an itemize block.

    Args:
        block: Text containing an itemize environment.
        prefix: ID prefix (e.g., 'exp', 'proj').
        entry_idx: Entry index for ID generation.

    Returns:
        List of BulletPoint objects with stable IDs.
    """
    bullets: list[BulletPoint] = []
    itemize_match = RE_ITEMIZE_BLOCK.search(block)
    if not itemize_match:
        return bullets

    items_text = itemize_match.group(1)
    for item_match in RE_ITEM.finditer(items_text):
        text = item_match.group(1).strip()
        text = _strip_latex_commands(text)
        text = " ".join(text.split())  # Normalize whitespace
        if text:
            bullet_id = f"{prefix}_{entry_idx}_{len(bullets)}"
            bullets.append(BulletPoint(id=bullet_id, text=text))

    return bullets


def _parse_education(content: str) -> list[EducationEntry]:
    """Parse education section into entries.

    Args:
        content: Raw content of the education section.

    Returns:
        List of EducationEntry objects.
    """
    # Try custom \resumeHeading format
    custom_matches = list(RE_RESUME_HEADING.finditer(content))
    if custom_matches:
        return _parse_education_custom(custom_matches)

    # Standard format
    return _parse_education_standard(content)


def _parse_education_custom(
    matches: list[re.Match[str]],
) -> list[EducationEntry]:
    """Parse education entries using \\resumeHeading format.

    Args:
        matches: Regex matches for resumeHeading.

    Returns:
        List of EducationEntry objects.
    """
    entries: list[EducationEntry] = []
    for match in matches:
        degree = match.group(1).strip()
        dates = match.group(2).strip()
        school = match.group(3).strip()
        location = match.group(4).strip()

        entries.append(
            EducationEntry(
                school=school,
                degree=degree,
                dates=dates,
                location=location or None,
            )
        )
    return entries


def _parse_education_standard(content: str) -> list[EducationEntry]:
    """Parse education entries using standard format.

    Args:
        content: Section content.

    Returns:
        List of EducationEntry objects.
    """
    entries: list[EducationEntry] = []

    textbf_matches = list(RE_TEXTBF.finditer(content))
    entry_starts: list[int] = []
    entry_degrees: list[str] = []

    for m in textbf_matches:
        after = content[m.end() : m.end() + 20]
        if "\\hfill" in after:
            entry_starts.append(m.start())
            entry_degrees.append(m.group(1))

    for i, (start, degree) in enumerate(zip(entry_starts, entry_degrees, strict=True)):
        end = entry_starts[i + 1] if i + 1 < len(entry_starts) else len(content)
        block = content[start:end]

        dates = _extract_dates_from_line(block)
        school = _extract_company(block)  # Same \textit pattern
        location = _extract_entry_location(block)

        # Extract detail lines (non-empty lines after the header that aren't items)
        details = _extract_education_details(block)

        entries.append(
            EducationEntry(
                school=school,
                degree=degree,
                dates=dates,
                location=location,
                details=details,
            )
        )

    return entries


def _extract_education_details(block: str) -> list[str]:
    """Extract extra detail lines from an education entry.

    Args:
        block: Text block for a single education entry.

    Returns:
        List of detail strings.
    """
    details: list[str] = []
    lines = block.strip().split("\n")
    # Skip the first two lines (degree+dates and school+location)
    header_count = 0
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if header_count < 2 and ("\\textbf" in stripped or "\\textit" in stripped):
            header_count += 1
            continue
        # Remaining non-empty, non-command lines are details
        cleaned = _strip_latex_commands(stripped)
        cleaned = cleaned.strip().rstrip("\\").strip()
        if cleaned and not cleaned.startswith("\\"):
            details.append(cleaned)

    return details


def _parse_skills(content: str) -> list[SkillCategory]:
    """Parse skills section into categories.

    Expected format: \\textbf{Category:} Skill1, Skill2, Skill3

    Args:
        content: Raw content of the skills section.

    Returns:
        List of SkillCategory objects.
    """
    categories: list[SkillCategory] = []

    # Pattern: \textbf{Category:} items
    skill_pattern = re.compile(r"\\textbf\{([^}]+?):\}\s*(.+?)(?=\\textbf|$)", re.DOTALL)
    for match in skill_pattern.finditer(content):
        category = match.group(1).strip()
        items_text = match.group(2).strip()
        # Clean up LaTeX artifacts
        items_text = items_text.replace("\\\\", "").strip()
        items = [item.strip() for item in items_text.split(",") if item.strip()]
        if items:
            categories.append(SkillCategory(category=category, items=items))

    return categories


def _parse_projects(content: str) -> list[ProjectEntry]:
    """Parse projects section into entries.

    Args:
        content: Raw content of the projects section.

    Returns:
        List of ProjectEntry objects.
    """
    entries: list[ProjectEntry] = []

    # Find project headers: \textbf{Name} \hfill ...
    textbf_matches = list(RE_TEXTBF.finditer(content))
    entry_starts: list[int] = []
    entry_names: list[str] = []

    for m in textbf_matches:
        # Projects have \hfill after name (for URL or date)
        after = content[m.end() : m.end() + 30]
        if "\\hfill" in after:
            entry_starts.append(m.start())
            entry_names.append(m.group(1))

    for i, (start, name) in enumerate(zip(entry_starts, entry_names, strict=True)):
        end = entry_starts[i + 1] if i + 1 < len(entry_starts) else len(content)
        block = content[start:end]

        url = _extract_project_url(block)
        dates = _extract_project_dates(block)
        bullets = _extract_bullets(block, "proj", len(entries))

        entries.append(
            ProjectEntry(
                name=name,
                url=url,
                dates=dates,
                bullets=bullets,
            )
        )

    return entries


def _extract_project_url(block: str) -> str | None:
    """Extract URL from a project entry.

    Args:
        block: Text block for a single project.

    Returns:
        URL string or None.
    """
    match = RE_HREF.search(block)
    if match:
        return match.group(1)
    return None


def _extract_project_dates(block: str) -> str | None:
    """Extract dates from a project entry.

    Args:
        block: Text block for a single project.

    Returns:
        Date string or None.
    """
    # Check for a year after \hfill (but not a URL)
    first_line = block.split("\n")[0]
    date_match = re.search(r"\\hfill\s+(\d{4}(?:\s*--?\s*\d{4})?)\s*$", first_line)
    if date_match:
        return date_match.group(1).strip()
    return None


def _strip_latex_commands(text: str) -> str:
    """Remove common LaTeX formatting commands from text.

    Args:
        text: LaTeX-formatted text.

    Returns:
        Plain text with formatting stripped.
    """
    # Remove \textbf{...}, \textit{...}, etc. but keep content
    text = re.sub(r"\\text(?:bf|it|rm|sf|tt|sc)\{([^}]*)\}", r"\1", text)
    # Remove \emph{...}
    text = re.sub(r"\\emph\{([^}]*)\}", r"\1", text)
    # Remove \href{url}{label} -> label
    text = re.sub(r"\\href\{[^}]*\}\{([^}]*)\}", r"\1", text)
    # Remove standalone LaTeX commands like \hfill, \enspace, \\
    text = re.sub(r"\\(?:hfill|enspace|quad|qquad|noindent|vspace\{[^}]*\})", " ", text)
    text = text.replace("\\\\", " ")
    # Remove \% -> %
    text = text.replace("\\%", "%")
    # Clean up multiple spaces
    text = re.sub(r"\s+", " ", text)
    return text.strip()
