"""Integration tests for the full tailoring pipeline.

These tests use MockLLMProvider to test the end-to-end pipeline
without real API calls. Real API integration tests are marked with
@pytest.mark.integration and require ANTHROPIC_API_KEY.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from resuforge.cover_letter.generator import generate_cover_letter
from resuforge.ingestion.jd_parser import parse_jd
from resuforge.resume.ir_schema import ResumeIR, TailoringResult
from resuforge.resume.latex_parser import parse_latex
from resuforge.resume.latex_renderer import render_latex
from resuforge.tailoring.engine import tailor_resume
from tests.conftest import MockLLMProvider

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"
RESUME_PATH = FIXTURES_DIR / "resumes" / "simple_article.tex"
JD_PATH = FIXTURES_DIR / "jds" / "software_engineer.txt"
ML_JD_PATH = FIXTURES_DIR / "jds" / "ml_engineer.txt"


class TestMockedPipeline:
    """End-to-end pipeline tests with mocked LLM."""

    def test_full_pipeline_simple(self) -> None:
        """Full pipeline: parse -> tailor -> render with simple fixture."""
        resume_ir = parse_latex(RESUME_PATH)
        jd = parse_jd(JD_PATH)
        mock = MockLLMProvider()

        result = tailor_resume(resume_ir, jd, llm=mock)
        assert isinstance(result, TailoringResult)
        assert isinstance(result.resume, ResumeIR)

        rendered = render_latex(result.resume)
        assert r"\begin{document}" in rendered
        assert result.resume.header.name == "Jane Doe"

    def test_full_pipeline_ml_jd(self) -> None:
        """Full pipeline with ML engineer JD."""
        resume_ir = parse_latex(RESUME_PATH)
        jd = parse_jd(ML_JD_PATH)
        mock = MockLLMProvider()

        result = tailor_resume(resume_ir, jd, llm=mock)
        rendered = render_latex(result.resume)

        assert "Jane Doe" in rendered
        assert result.gap_analysis is not None

    def test_pipeline_with_cover_letter(self) -> None:
        """Full pipeline including cover letter generation."""
        resume_ir = parse_latex(RESUME_PATH)
        jd = parse_jd(ML_JD_PATH)
        mock = MockLLMProvider()

        result = tailor_resume(resume_ir, jd, llm=mock)
        cover_letter = generate_cover_letter(result.resume, jd, llm=mock)

        assert isinstance(cover_letter, str)
        assert len(cover_letter) > 0

    def test_round_trip_after_tailoring(self) -> None:
        """Tailored resume can be rendered and re-parsed."""
        resume_ir = parse_latex(RESUME_PATH)
        jd = parse_jd(JD_PATH)
        mock = MockLLMProvider()

        result = tailor_resume(resume_ir, jd, llm=mock)
        rendered = render_latex(result.resume)
        reparsed = parse_latex(rendered)

        assert reparsed.header.name == result.resume.header.name
        assert len(reparsed.experience) == len(result.resume.experience)

    def test_custom_commands_fixture(self) -> None:
        """Pipeline works with custom commands fixture."""
        custom_path = FIXTURES_DIR / "resumes" / "custom_commands.tex"
        resume_ir = parse_latex(custom_path)
        jd = parse_jd(JD_PATH)
        mock = MockLLMProvider()

        result = tailor_resume(resume_ir, jd, llm=mock)
        rendered = render_latex(result.resume)

        assert "Alex Chen" in rendered
        assert result.resume.header.name == "Alex Chen"


@pytest.mark.integration
class TestRealLLMPipeline:
    """Integration tests that require a real API key.

    Run with: pytest -m integration (requires ANTHROPIC_API_KEY)
    """

    def test_real_tailoring(self) -> None:
        """Full tailoring with real LLM calls."""
        import os

        from resuforge.llm.anthropic_client import AnthropicClient

        if not os.environ.get("ANTHROPIC_API_KEY"):
            pytest.skip("ANTHROPIC_API_KEY not set")

        resume_ir = parse_latex(RESUME_PATH)
        jd = parse_jd(ML_JD_PATH)
        llm = AnthropicClient()

        result = tailor_resume(resume_ir, jd, llm=llm)

        assert isinstance(result, TailoringResult)
        assert result.gap_analysis is not None
        assert result.resume.header.name == "Jane Doe"
        # Verify immutable fields
        assert result.resume.education[0].school == resume_ir.education[0].school
