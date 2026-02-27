"""LaTeX renderer — converts ResumeIR back to valid .tex output.

The renderer is a pure function: same IR in, same LaTeX out.
No state, no side effects. Renders into standard article-class format.
"""

from __future__ import annotations

from resuforge.resume.ir_schema import (
    EducationEntry,
    ExperienceEntry,
    HeaderSection,
    ProjectEntry,
    ResumeIR,
    SkillCategory,
)

DEFAULT_PREAMBLE = r"""\documentclass[11pt]{article}
\usepackage[margin=0.75in]{geometry}
\usepackage{hyperref}
\usepackage{enumitem}"""

# Maps normalized section names to display names
SECTION_DISPLAY_NAMES: dict[str, str] = {
    "summary": "Summary",
    "experience": "Experience",
    "education": "Education",
    "skills": "Skills",
    "projects": "Projects",
}


def render_latex(ir: ResumeIR) -> str:
    """Render a ResumeIR back to a valid LaTeX string.

    Args:
        ir: The structured resume intermediate representation.

    Returns:
        A compilable LaTeX string.
    """
    parts: list[str] = []

    # Preamble
    preamble = ir.preamble.strip() if ir.preamble else DEFAULT_PREAMBLE
    parts.append(preamble)
    parts.append("")
    parts.append(r"\begin{document}")
    parts.append("")

    # Header
    parts.append(_render_header(ir.header))
    parts.append("")

    # Sections in order
    rendered_sections = _get_section_order(ir)
    for section_name in rendered_sections:
        section_output = _render_section(ir, section_name)
        if section_output:
            parts.append(section_output)
            parts.append("")

    parts.append(r"\end{document}")
    parts.append("")

    return "\n".join(parts)


def _get_section_order(ir: ResumeIR) -> list[str]:
    """Determine the rendering order for sections.

    Uses section_order if available, otherwise builds a default order.

    Args:
        ir: The resume IR.

    Returns:
        Ordered list of section name strings.
    """
    if ir.section_order:
        return ir.section_order

    # Default order based on what's populated
    order: list[str] = []
    if ir.summary:
        order.append("summary")
    if ir.experience:
        order.append("experience")
    if ir.skills:
        order.append("skills")
    if ir.education:
        order.append("education")
    if ir.projects:
        order.append("projects")
    for key in ir.raw_sections:
        order.append(key)
    return order


def _render_section(ir: ResumeIR, section_name: str) -> str | None:
    """Render a single section by name.

    Args:
        ir: The resume IR.
        section_name: Normalized section name.

    Returns:
        Rendered LaTeX string for the section, or None if empty.
    """
    if section_name == "summary" and ir.summary:
        return _render_summary(ir.summary)
    elif section_name == "experience" and ir.experience:
        return _render_experience(ir.experience)
    elif section_name == "education" and ir.education:
        return _render_education(ir.education)
    elif section_name == "skills" and ir.skills:
        return _render_skills(ir.skills)
    elif section_name == "projects" and ir.projects:
        return _render_projects(ir.projects)
    elif section_name in ir.raw_sections:
        return _render_raw_section(section_name, ir.raw_sections[section_name])
    return None


def _render_header(header: HeaderSection) -> str:
    """Render the header/contact section.

    Args:
        header: Header data.

    Returns:
        LaTeX string for the header.
    """
    lines: list[str] = []
    lines.append(r"\begin{center}")
    lines.append(rf"{{\LARGE \textbf{{{header.name}}}}} \\[4pt]")

    # Contact line
    contact_parts: list[str] = []
    if header.email:
        contact_parts.append(header.email)
    if header.phone:
        contact_parts.append(header.phone)
    if header.location:
        contact_parts.append(header.location)
    if contact_parts:
        lines.append(r" \enspace | \enspace ".join(contact_parts) + r" \\")

    # Links line
    if header.links:
        link_parts = [rf"\href{{{link.url}}}{{{link.label}}}" for link in header.links]
        lines.append(r" \enspace | \enspace ".join(link_parts))

    lines.append(r"\end{center}")
    return "\n".join(lines)


def _render_summary(summary: str) -> str:
    """Render the summary section.

    Args:
        summary: Summary text.

    Returns:
        LaTeX string for the summary section.
    """
    return f"\\section*{{Summary}}\n{summary}"


def _render_experience(entries: list[ExperienceEntry]) -> str:
    """Render the experience section.

    Args:
        entries: List of experience entries.

    Returns:
        LaTeX string for the experience section.
    """
    lines: list[str] = [r"\section*{Experience}", ""]
    for i, entry in enumerate(entries):
        if i > 0:
            lines.append("")
        lines.append(rf"\textbf{{{entry.title}}} \hfill {entry.dates} \\")
        location = f" \\hfill {entry.location}" if entry.location else ""
        lines.append(rf"\textit{{{entry.company}}}{location}")
        if entry.bullets:
            lines.append(r"\begin{itemize}[leftmargin=*]")
            for bullet in entry.bullets:
                lines.append(rf"    \item {bullet.text}")
            lines.append(r"\end{itemize}")
    return "\n".join(lines)


def _render_education(entries: list[EducationEntry]) -> str:
    """Render the education section.

    Args:
        entries: List of education entries.

    Returns:
        LaTeX string for the education section.
    """
    lines: list[str] = [r"\section*{Education}", ""]
    for i, entry in enumerate(entries):
        if i > 0:
            lines.append("")
        lines.append(rf"\textbf{{{entry.degree}}} \hfill {entry.dates} \\")
        location = f" \\hfill {entry.location}" if entry.location else ""
        lines.append(rf"\textit{{{entry.school}}}{location}")
        for detail in entry.details:
            lines.append(rf"{detail}")
    return "\n".join(lines)


def _render_skills(categories: list[SkillCategory]) -> str:
    """Render the skills section.

    Args:
        categories: List of skill categories.

    Returns:
        LaTeX string for the skills section.
    """
    lines: list[str] = [r"\section*{Skills}"]
    skill_lines: list[str] = []
    for cat in categories:
        items = ", ".join(cat.items)
        skill_lines.append(rf"\textbf{{{cat.category}:}} {items}")
    lines.append(" \\\\\n".join(skill_lines))
    return "\n".join(lines)


def _render_projects(entries: list[ProjectEntry]) -> str:
    """Render the projects section.

    Args:
        entries: List of project entries.

    Returns:
        LaTeX string for the projects section.
    """
    lines: list[str] = [r"\section*{Projects}", ""]
    for i, entry in enumerate(entries):
        if i > 0:
            lines.append("")
        # Name with optional URL or dates
        right_side = ""
        if entry.url:
            right_side = rf"\href{{{entry.url}}}{{GitHub}}"
        elif entry.dates:
            right_side = entry.dates
        lines.append(rf"\textbf{{{entry.name}}} \hfill {right_side}")
        if entry.bullets:
            lines.append(r"\begin{itemize}[leftmargin=*]")
            for bullet in entry.bullets:
                lines.append(rf"    \item {bullet.text}")
            lines.append(r"\end{itemize}")
    return "\n".join(lines)


def _render_raw_section(name: str, content: str) -> str:
    """Render a raw (unknown) section verbatim.

    Args:
        name: Normalized section name.
        content: Raw section content.

    Returns:
        LaTeX string with section header and verbatim content.
    """
    display_name = name.replace("_", " ").title()
    return f"\\section*{{{display_name}}}\n{content}"
