"""Unit tests for the LaTeX renderer — TDD style."""

from __future__ import annotations

from pathlib import Path

from resuforge.resume.ir_schema import (
    BulletPoint,
    ExperienceEntry,
    HeaderSection,
    ProjectEntry,
    ResumeIR,
    SkillCategory,
)
from resuforge.resume.latex_parser import parse_latex
from resuforge.resume.latex_renderer import render_latex

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures" / "resumes"


# ---------------------------------------------------------------------------
# Basic rendering
# ---------------------------------------------------------------------------


class TestRenderBasic:
    """Tests for basic rendering functionality."""

    def test_render_returns_string(self, sample_resume_ir: ResumeIR) -> None:
        """Renderer returns a string."""
        result = render_latex(sample_resume_ir)
        assert isinstance(result, str)

    def test_render_contains_documentclass(self, sample_resume_ir: ResumeIR) -> None:
        """Output contains documentclass from preamble."""
        result = render_latex(sample_resume_ir)
        assert r"\documentclass" in result

    def test_render_contains_begin_end_document(self, sample_resume_ir: ResumeIR) -> None:
        """Output has begin/end document tags."""
        result = render_latex(sample_resume_ir)
        assert r"\begin{document}" in result
        assert r"\end{document}" in result

    def test_render_empty_ir(self) -> None:
        """Renderer handles minimal IR gracefully."""
        ir = ResumeIR(header=HeaderSection(name="Test"))
        result = render_latex(ir)
        assert "Test" in result
        assert r"\begin{document}" in result


# ---------------------------------------------------------------------------
# Header rendering
# ---------------------------------------------------------------------------


class TestRenderHeader:
    """Tests for header rendering."""

    def test_name_rendered(self, sample_resume_ir: ResumeIR) -> None:
        """Name appears in output."""
        result = render_latex(sample_resume_ir)
        assert "Jane Doe" in result

    def test_email_rendered(self, sample_resume_ir: ResumeIR) -> None:
        """Email appears in output."""
        result = render_latex(sample_resume_ir)
        assert "jane@example.com" in result

    def test_links_rendered(self, sample_resume_ir: ResumeIR) -> None:
        """Links are rendered as \\href commands."""
        result = render_latex(sample_resume_ir)
        assert r"\href{https://github.com/janedoe}{GitHub}" in result


# ---------------------------------------------------------------------------
# Section rendering
# ---------------------------------------------------------------------------


class TestRenderSections:
    """Tests for individual section rendering."""

    def test_summary_rendered(self, sample_resume_ir: ResumeIR) -> None:
        """Summary section appears in output."""
        result = render_latex(sample_resume_ir)
        assert r"\section*{Summary}" in result
        assert "ML engineer" in result

    def test_experience_rendered(self, sample_resume_ir: ResumeIR) -> None:
        """Experience entries appear in output."""
        result = render_latex(sample_resume_ir)
        assert "Senior ML Engineer" in result
        assert "Acme Corp" in result

    def test_experience_bullets_rendered(self, sample_resume_ir: ResumeIR) -> None:
        """Experience bullet points are rendered as \\item."""
        result = render_latex(sample_resume_ir)
        assert r"\item" in result
        assert "recommendation system" in result

    def test_skills_rendered(self, sample_resume_ir: ResumeIR) -> None:
        """Skills section renders categories and items."""
        result = render_latex(sample_resume_ir)
        assert r"\section*{Skills}" in result
        assert "Python" in result
        assert "Languages" in result

    def test_education_rendered(self, sample_resume_ir: ResumeIR) -> None:
        """Education entries appear in output."""
        result = render_latex(sample_resume_ir)
        assert "Stanford University" in result
        assert "M.S. Computer Science" in result

    def test_section_order_respected(self) -> None:
        """Sections render in the order specified by section_order."""
        ir = ResumeIR(
            header=HeaderSection(name="Test"),
            summary="A summary",
            skills=[SkillCategory(category="Lang", items=["Python"])],
            experience=[
                ExperienceEntry(
                    company="Co",
                    title="Eng",
                    dates="2020",
                    bullets=[],
                ),
            ],
            section_order=["skills", "summary", "experience"],
        )
        result = render_latex(ir)
        skills_pos = result.index("Skills")
        summary_pos = result.index("Summary")
        exp_pos = result.index("Experience")
        assert skills_pos < summary_pos < exp_pos


# ---------------------------------------------------------------------------
# Raw sections and projects
# ---------------------------------------------------------------------------


class TestRenderRawAndProjects:
    """Tests for raw section passthrough and project rendering."""

    def test_raw_sections_passed_through(self) -> None:
        """Raw sections appear verbatim in output."""
        ir = ResumeIR(
            header=HeaderSection(name="Test"),
            raw_sections={"certifications": "\\begin{itemize}\n\\item AWS Pro\n\\end{itemize}"},
            section_order=["certifications"],
        )
        result = render_latex(ir)
        assert "Certifications" in result
        assert "AWS Pro" in result

    def test_projects_rendered(self) -> None:
        """Project entries render with bullets."""
        ir = ResumeIR(
            header=HeaderSection(name="Test"),
            projects=[
                ProjectEntry(
                    name="MyProject",
                    url="https://github.com/test",
                    bullets=[BulletPoint(id="proj_0_0", text="Built something cool")],
                ),
            ],
            section_order=["projects"],
        )
        result = render_latex(ir)
        assert "MyProject" in result
        assert "Built something cool" in result


# ---------------------------------------------------------------------------
# Round-trip tests (critical)
# ---------------------------------------------------------------------------


class TestRoundTrip:
    """Round-trip tests: parse -> render -> parse -> assert structural equivalence."""

    def test_round_trip_simple_article(self) -> None:
        """Parse simple_article.tex, render, parse again, compare."""
        ir1 = parse_latex(FIXTURES_DIR / "simple_article.tex")
        rendered = render_latex(ir1)
        ir2 = parse_latex(rendered)
        _assert_ir_equivalent(ir1, ir2)

    def test_round_trip_custom_commands(self) -> None:
        """Parse custom_commands.tex, render, parse again, compare."""
        ir1 = parse_latex(FIXTURES_DIR / "custom_commands.tex")
        rendered = render_latex(ir1)
        ir2 = parse_latex(rendered)
        _assert_ir_equivalent(ir1, ir2)


def _assert_ir_equivalent(ir1: ResumeIR, ir2: ResumeIR) -> None:
    """Assert two ResumeIRs are structurally equivalent.

    Compares header, experience, education, skills, projects, summary,
    and section_order. Raw sections and preamble may differ in formatting.

    Args:
        ir1: First IR (from original parse).
        ir2: Second IR (from round-trip parse).
    """
    # Header
    assert ir1.header.name == ir2.header.name
    assert ir1.header.email == ir2.header.email

    # Summary
    if ir1.summary:
        assert ir2.summary is not None
        assert ir1.summary.strip() == ir2.summary.strip()

    # Experience
    assert len(ir1.experience) == len(ir2.experience)
    for e1, e2 in zip(ir1.experience, ir2.experience, strict=True):
        assert e1.title == e2.title
        assert e1.company == e2.company
        assert len(e1.bullets) == len(e2.bullets)
        for b1, b2 in zip(e1.bullets, e2.bullets, strict=True):
            assert b1.text == b2.text

    # Education
    assert len(ir1.education) == len(ir2.education)
    for ed1, ed2 in zip(ir1.education, ir2.education, strict=True):
        assert ed1.school == ed2.school
        assert ed1.degree == ed2.degree

    # Skills
    assert len(ir1.skills) == len(ir2.skills)
    for s1, s2 in zip(ir1.skills, ir2.skills, strict=True):
        assert s1.category == s2.category
        assert s1.items == s2.items

    # Projects
    assert len(ir1.projects) == len(ir2.projects)
    for p1, p2 in zip(ir1.projects, ir2.projects, strict=True):
        assert p1.name == p2.name
        assert len(p1.bullets) == len(p2.bullets)
