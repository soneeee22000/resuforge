"""Unit tests for the LaTeX parser — TDD style."""

from __future__ import annotations

from pathlib import Path

import pytest

from resuforge.resume.ir_schema import ResumeIR
from resuforge.resume.latex_parser import parse_latex

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures" / "resumes"


# ---------------------------------------------------------------------------
# Basic parsing
# ---------------------------------------------------------------------------


class TestParseLatexBasic:
    """Tests for basic parsing functionality."""

    def test_parse_from_file_path(self) -> None:
        """Parser accepts a Path and returns ResumeIR."""
        ir = parse_latex(FIXTURES_DIR / "simple_article.tex")
        assert isinstance(ir, ResumeIR)

    def test_parse_from_string(self) -> None:
        """Parser accepts a LaTeX string directly."""
        tex = (FIXTURES_DIR / "simple_article.tex").read_text(encoding="utf-8")
        ir = parse_latex(tex)
        assert isinstance(ir, ResumeIR)

    def test_parse_nonexistent_file_raises(self) -> None:
        """Parser raises FileNotFoundError for missing files."""
        with pytest.raises(FileNotFoundError):
            parse_latex(Path("/nonexistent/resume.tex"))

    def test_parse_empty_string_raises(self) -> None:
        """Parser raises ValueError for empty input."""
        with pytest.raises(ValueError, match="empty"):
            parse_latex("")


# ---------------------------------------------------------------------------
# Preamble extraction
# ---------------------------------------------------------------------------


class TestPreambleExtraction:
    """Tests for preamble and custom command extraction."""

    def test_preamble_extracted(self) -> None:
        """Preamble is everything before \\begin{document}."""
        ir = parse_latex(FIXTURES_DIR / "simple_article.tex")
        assert r"\documentclass" in ir.preamble
        assert r"\usepackage" in ir.preamble
        assert r"\begin{document}" not in ir.preamble

    def test_custom_commands_detected(self) -> None:
        """Custom \\newcommand definitions are captured."""
        ir = parse_latex(FIXTURES_DIR / "custom_commands.tex")
        assert len(ir.custom_commands) >= 2
        assert any("resumeHeading" in cmd for cmd in ir.custom_commands)

    def test_simple_has_no_custom_commands(self) -> None:
        """Simple article template has no custom commands."""
        ir = parse_latex(FIXTURES_DIR / "simple_article.tex")
        assert len(ir.custom_commands) == 0


# ---------------------------------------------------------------------------
# Header parsing
# ---------------------------------------------------------------------------


class TestHeaderParsing:
    """Tests for header section extraction."""

    def test_name_extracted(self) -> None:
        """Parser extracts the resume holder's name."""
        ir = parse_latex(FIXTURES_DIR / "simple_article.tex")
        assert ir.header.name == "Jane Doe"

    def test_email_extracted(self) -> None:
        """Parser extracts email address."""
        ir = parse_latex(FIXTURES_DIR / "simple_article.tex")
        assert ir.header.email == "jane@example.com"

    def test_phone_extracted(self) -> None:
        """Parser extracts phone number."""
        ir = parse_latex(FIXTURES_DIR / "simple_article.tex")
        assert ir.header.phone == "+1-555-0100"

    def test_location_extracted(self) -> None:
        """Parser extracts location."""
        ir = parse_latex(FIXTURES_DIR / "simple_article.tex")
        assert ir.header.location == "San Francisco, CA"

    def test_links_extracted(self) -> None:
        """Parser extracts hyperlinked URLs."""
        ir = parse_latex(FIXTURES_DIR / "simple_article.tex")
        assert len(ir.header.links) == 2
        labels = {link.label for link in ir.header.links}
        assert "GitHub" in labels
        assert "LinkedIn" in labels

    def test_custom_header_parsed(self) -> None:
        """Parser handles different header formats."""
        ir = parse_latex(FIXTURES_DIR / "custom_commands.tex")
        assert ir.header.name == "Alex Chen"
        assert ir.header.email == "alex.chen@email.com"


# ---------------------------------------------------------------------------
# Experience parsing
# ---------------------------------------------------------------------------


class TestExperienceParsing:
    """Tests for experience section extraction."""

    def test_experience_entries_found(self) -> None:
        """Parser finds all experience entries."""
        ir = parse_latex(FIXTURES_DIR / "simple_article.tex")
        assert len(ir.experience) == 2

    def test_experience_company_and_title(self) -> None:
        """Parser extracts company and title correctly."""
        ir = parse_latex(FIXTURES_DIR / "simple_article.tex")
        first = ir.experience[0]
        assert first.title == "Senior ML Engineer"
        assert first.company == "Acme Corp"

    def test_experience_dates(self) -> None:
        """Parser extracts date ranges."""
        ir = parse_latex(FIXTURES_DIR / "simple_article.tex")
        assert "2022" in ir.experience[0].dates
        assert "Present" in ir.experience[0].dates

    def test_experience_bullets(self) -> None:
        """Parser extracts bullet points with stable IDs."""
        ir = parse_latex(FIXTURES_DIR / "simple_article.tex")
        first = ir.experience[0]
        assert len(first.bullets) == 3
        assert first.bullets[0].id == "exp_0_0"
        assert "recommendation" in first.bullets[0].text.lower()

    def test_experience_location(self) -> None:
        """Parser extracts location from experience entries."""
        ir = parse_latex(FIXTURES_DIR / "simple_article.tex")
        assert ir.experience[0].location == "San Francisco, CA"

    def test_custom_command_experience(self) -> None:
        """Parser handles \\resumeHeading style entries."""
        ir = parse_latex(FIXTURES_DIR / "custom_commands.tex")
        assert len(ir.experience) == 2
        assert ir.experience[0].title == "Staff Software Engineer"
        assert ir.experience[0].company == "MegaTech Ltd"


# ---------------------------------------------------------------------------
# Education parsing
# ---------------------------------------------------------------------------


class TestEducationParsing:
    """Tests for education section extraction."""

    def test_education_entries_found(self) -> None:
        """Parser finds all education entries."""
        ir = parse_latex(FIXTURES_DIR / "simple_article.tex")
        assert len(ir.education) == 2

    def test_education_degree_and_school(self) -> None:
        """Parser extracts degree and school."""
        ir = parse_latex(FIXTURES_DIR / "simple_article.tex")
        first = ir.education[0]
        assert "M.S." in first.degree
        assert "Stanford" in first.school

    def test_education_details(self) -> None:
        """Parser captures extra detail lines."""
        ir = parse_latex(FIXTURES_DIR / "simple_article.tex")
        first = ir.education[0]
        assert any("GPA" in d for d in first.details)


# ---------------------------------------------------------------------------
# Skills parsing
# ---------------------------------------------------------------------------


class TestSkillsParsing:
    """Tests for skills section extraction."""

    def test_skill_categories_found(self) -> None:
        """Parser finds all skill categories."""
        ir = parse_latex(FIXTURES_DIR / "simple_article.tex")
        assert len(ir.skills) >= 3

    def test_skill_category_name(self) -> None:
        """Parser extracts category name."""
        ir = parse_latex(FIXTURES_DIR / "simple_article.tex")
        categories = {s.category for s in ir.skills}
        assert "Languages" in categories

    def test_skill_items(self) -> None:
        """Parser extracts individual skills within categories."""
        ir = parse_latex(FIXTURES_DIR / "simple_article.tex")
        lang = next(s for s in ir.skills if s.category == "Languages")
        assert "Python" in lang.items
        assert "C++" in lang.items


# ---------------------------------------------------------------------------
# Projects parsing
# ---------------------------------------------------------------------------


class TestProjectsParsing:
    """Tests for projects section extraction."""

    def test_project_entries_found(self) -> None:
        """Parser finds all project entries."""
        ir = parse_latex(FIXTURES_DIR / "simple_article.tex")
        assert len(ir.projects) == 2

    def test_project_name(self) -> None:
        """Parser extracts project names."""
        ir = parse_latex(FIXTURES_DIR / "simple_article.tex")
        assert ir.projects[0].name == "ResuForge"

    def test_project_bullets(self) -> None:
        """Parser extracts project bullet points."""
        ir = parse_latex(FIXTURES_DIR / "simple_article.tex")
        first = ir.projects[0]
        assert len(first.bullets) == 2
        assert first.bullets[0].id == "proj_0_0"

    def test_project_url(self) -> None:
        """Parser extracts project URLs."""
        ir = parse_latex(FIXTURES_DIR / "simple_article.tex")
        first = ir.projects[0]
        assert first.url is not None
        assert "github" in first.url.lower()


# ---------------------------------------------------------------------------
# Section ordering and raw sections
# ---------------------------------------------------------------------------


class TestSectionOrdering:
    """Tests for section_order and raw_sections handling."""

    def test_section_order_captured(self) -> None:
        """Parser records the order of sections as they appear."""
        ir = parse_latex(FIXTURES_DIR / "simple_article.tex")
        assert len(ir.section_order) > 0
        assert "experience" in ir.section_order

    def test_summary_in_section_order(self) -> None:
        """Summary section appears in ordering."""
        ir = parse_latex(FIXTURES_DIR / "simple_article.tex")
        assert "summary" in ir.section_order

    def test_unknown_sections_go_to_raw(self) -> None:
        """Sections not recognized are stored in raw_sections."""
        ir = parse_latex(FIXTURES_DIR / "custom_commands.tex")
        # "Certifications" is not a standard recognized section
        assert "certifications" in ir.raw_sections

    def test_summary_extracted(self) -> None:
        """Parser extracts the summary text."""
        ir = parse_latex(FIXTURES_DIR / "simple_article.tex")
        assert ir.summary is not None
        assert "ML engineer" in ir.summary
