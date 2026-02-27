"""Unit tests for the JD parser — TDD style."""

from __future__ import annotations

from pathlib import Path

import pytest

from resuforge.ingestion.jd_parser import parse_jd
from resuforge.resume.ir_schema import JDObject

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures" / "jds"


# ---------------------------------------------------------------------------
# Basic parsing
# ---------------------------------------------------------------------------


class TestParseJDBasic:
    """Tests for basic JD parsing."""

    def test_parse_from_file(self) -> None:
        """Parser accepts a file path and returns JDObject."""
        jd = parse_jd(FIXTURES_DIR / "software_engineer.txt")
        assert isinstance(jd, JDObject)

    def test_parse_from_string(self) -> None:
        """Parser accepts raw text."""
        jd = parse_jd("We are looking for a Software Engineer with Python skills.")
        assert isinstance(jd, JDObject)
        assert jd.raw_text != ""

    def test_parse_nonexistent_file_raises(self) -> None:
        """Parser raises FileNotFoundError for missing files."""
        with pytest.raises(FileNotFoundError):
            parse_jd(Path("/nonexistent/jd.txt"))

    def test_parse_empty_string_raises(self) -> None:
        """Parser raises ValueError for empty input."""
        with pytest.raises(ValueError, match="empty"):
            parse_jd("")

    def test_raw_text_always_populated(self) -> None:
        """raw_text field always contains the original text."""
        jd = parse_jd(FIXTURES_DIR / "software_engineer.txt")
        assert len(jd.raw_text) > 100


# ---------------------------------------------------------------------------
# Job title extraction
# ---------------------------------------------------------------------------


class TestJDTitleExtraction:
    """Tests for job title extraction."""

    def test_title_from_swe_jd(self) -> None:
        """Extracts job title from software engineer JD."""
        jd = parse_jd(FIXTURES_DIR / "software_engineer.txt")
        assert jd.job_title is not None
        assert "software engineer" in jd.job_title.lower()

    def test_title_from_ml_jd(self) -> None:
        """Extracts job title from ML engineer JD."""
        jd = parse_jd(FIXTURES_DIR / "ml_engineer.txt")
        assert jd.job_title is not None
        assert "machine learning" in jd.job_title.lower()

    def test_title_from_ds_jd(self) -> None:
        """Extracts job title from data scientist JD."""
        jd = parse_jd(FIXTURES_DIR / "data_scientist.txt")
        assert jd.job_title is not None
        assert "data scientist" in jd.job_title.lower()


# ---------------------------------------------------------------------------
# Company extraction
# ---------------------------------------------------------------------------


class TestJDCompanyExtraction:
    """Tests for company name extraction."""

    def test_company_from_swe_jd(self) -> None:
        """Extracts company name."""
        jd = parse_jd(FIXTURES_DIR / "software_engineer.txt")
        assert jd.company is not None
        assert "TechCorp" in jd.company


# ---------------------------------------------------------------------------
# Skills extraction
# ---------------------------------------------------------------------------


class TestJDSkillsExtraction:
    """Tests for required/preferred skills extraction."""

    def test_required_skills_extracted(self) -> None:
        """Extracts required skills from JD."""
        jd = parse_jd(FIXTURES_DIR / "software_engineer.txt")
        assert len(jd.required_skills) > 0

    def test_preferred_skills_extracted(self) -> None:
        """Extracts preferred skills from JD."""
        jd = parse_jd(FIXTURES_DIR / "software_engineer.txt")
        assert len(jd.preferred_skills) > 0

    def test_skills_are_specific(self) -> None:
        """Skills are actual skill items, not full sentences."""
        jd = parse_jd(FIXTURES_DIR / "ml_engineer.txt")
        # Required skills should have items
        assert len(jd.required_skills) >= 3


# ---------------------------------------------------------------------------
# Responsibilities extraction
# ---------------------------------------------------------------------------


class TestJDResponsibilities:
    """Tests for responsibilities extraction."""

    def test_responsibilities_extracted(self) -> None:
        """Extracts responsibilities."""
        jd = parse_jd(FIXTURES_DIR / "software_engineer.txt")
        assert len(jd.responsibilities) > 0

    def test_responsibilities_are_sentences(self) -> None:
        """Responsibilities are meaningful text."""
        jd = parse_jd(FIXTURES_DIR / "software_engineer.txt")
        for resp in jd.responsibilities:
            assert len(resp) > 10


# ---------------------------------------------------------------------------
# Experience and education
# ---------------------------------------------------------------------------


class TestJDExperienceEducation:
    """Tests for experience years and education extraction."""

    def test_experience_years_extracted(self) -> None:
        """Extracts years of experience requirement."""
        jd = parse_jd(FIXTURES_DIR / "software_engineer.txt")
        assert jd.experience_years is not None
        assert jd.experience_years == 5

    def test_education_requirement_extracted(self) -> None:
        """Extracts education requirement."""
        jd = parse_jd(FIXTURES_DIR / "software_engineer.txt")
        assert jd.education_requirement is not None

    def test_ml_experience_years(self) -> None:
        """ML JD has different experience requirement."""
        jd = parse_jd(FIXTURES_DIR / "ml_engineer.txt")
        assert jd.experience_years is not None
        assert jd.experience_years == 3
