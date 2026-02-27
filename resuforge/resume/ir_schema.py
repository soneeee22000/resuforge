"""Pydantic models for the Resume Intermediate Representation (IR).

All resume data flows through these models. Never use ad-hoc dicts.
The IR is the single source of truth between parsing and rendering.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class Link(BaseModel):
    """A labeled hyperlink (GitHub, LinkedIn, portfolio, etc.)."""

    label: str
    url: str


class HeaderSection(BaseModel):
    """Contact information and personal links."""

    name: str
    email: str | None = None
    phone: str | None = None
    location: str | None = None
    links: list[Link] = Field(default_factory=list)


class BulletPoint(BaseModel):
    """A single bullet point with a stable ID for change tracking.

    IDs follow the pattern: {section}_{entry_idx}_{bullet_idx}
    e.g., 'exp_0_2' = experience entry 0, bullet 2.
    """

    id: str
    text: str


class ExperienceEntry(BaseModel):
    """A single work experience entry."""

    company: str
    title: str
    dates: str
    location: str | None = None
    bullets: list[BulletPoint] = Field(default_factory=list)


class EducationEntry(BaseModel):
    """A single education entry."""

    school: str
    degree: str
    dates: str
    location: str | None = None
    details: list[str] = Field(default_factory=list)


class SkillCategory(BaseModel):
    """A skill category with its list of skill strings."""

    category: str
    items: list[str]


class ProjectEntry(BaseModel):
    """A single project entry."""

    name: str
    description: str | None = None
    dates: str | None = None
    url: str | None = None
    bullets: list[BulletPoint] = Field(default_factory=list)


class ResumeIR(BaseModel):
    """Top-level resume intermediate representation.

    This is the central data structure. The parser produces it,
    the tailoring engine modifies it, and the renderer consumes it.
    """

    preamble: str = ""
    header: HeaderSection = Field(default_factory=HeaderSection)
    summary: str | None = None
    experience: list[ExperienceEntry] = Field(default_factory=list)
    education: list[EducationEntry] = Field(default_factory=list)
    skills: list[SkillCategory] = Field(default_factory=list)
    projects: list[ProjectEntry] = Field(default_factory=list)
    raw_sections: dict[str, str] = Field(default_factory=dict)
    custom_commands: list[str] = Field(default_factory=list)
    section_order: list[str] = Field(default_factory=list)


class JDObject(BaseModel):
    """Structured representation of a parsed job description."""

    raw_text: str
    job_title: str | None = None
    company: str | None = None
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    responsibilities: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    experience_years: int | None = None
    education_requirement: str | None = None


class GapAnalysis(BaseModel):
    """Semantic comparison between JD requirements and resume content."""

    strengths: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
    opportunities: list[str] = Field(default_factory=list)


class Change(BaseModel):
    """A single tracked modification made by the tailoring engine.

    Every edit must be logged with its reason and the JD keyword that triggered it.
    """

    section: str
    original: str
    modified: str
    reason: str
    jd_keyword: str = ""


class TailoringResult(BaseModel):
    """Output of the tailoring engine — modified resume + change log."""

    resume: ResumeIR
    changes: list[Change] = Field(default_factory=list)
    gap_analysis: GapAnalysis | None = None
