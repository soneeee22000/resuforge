"""Unit tests for the tailoring engine — all mocked."""

from __future__ import annotations

from pydantic import BaseModel

from resuforge.resume.ir_schema import (
    BulletPoint,
    ExperienceEntry,
    GapAnalysis,
    HeaderSection,
    JDObject,
    ResumeIR,
    SkillCategory,
    TailoringResult,
)
from resuforge.tailoring.engine import tailor_resume
from tests.conftest import MockLLMProvider


class _MockSummaryResponse(BaseModel):
    """Mock response for summary rewrite."""

    summary: str


class _MockBulletResponse(BaseModel):
    """Mock response for bullet rephrase."""

    text: str
    reason: str
    jd_keyword: str


class _MockSkillsResponse(BaseModel):
    """Mock response for skills reorder."""

    categories: list[dict[str, list[str]]]


def _make_tailoring_mock(sample_resume_ir: ResumeIR) -> MockLLMProvider:
    """Create a MockLLMProvider configured for tailoring tests.

    Args:
        sample_resume_ir: The resume IR to base mock responses on.

    Returns:
        Configured MockLLMProvider.
    """
    return MockLLMProvider(
        responses={
            GapAnalysis: GapAnalysis(
                strengths=["Strong Python experience"],
                gaps=["No Kubernetes mentioned"],
                opportunities=["Could reframe ML work for production emphasis"],
            ),
            _MockSummaryResponse: _MockSummaryResponse(
                summary="Production ML engineer with 5 years deploying scalable systems.",
            ),
            _MockBulletResponse: _MockBulletResponse(
                text="Led development and deployment of recommendation system",
                reason="Added deployment emphasis",
                jd_keyword="deployment",
            ),
        }
    )


# ---------------------------------------------------------------------------
# Core tailoring pipeline
# ---------------------------------------------------------------------------


class TestTailorResume:
    """Tests for the tailor_resume function."""

    def test_returns_tailoring_result(
        self,
        sample_resume_ir: ResumeIR,
        sample_jd: JDObject,
        mock_llm: MockLLMProvider,
    ) -> None:
        """Returns a TailoringResult."""
        result = tailor_resume(sample_resume_ir, sample_jd, llm=mock_llm)
        assert isinstance(result, TailoringResult)

    def test_result_has_resume(
        self,
        sample_resume_ir: ResumeIR,
        sample_jd: JDObject,
        mock_llm: MockLLMProvider,
    ) -> None:
        """Result contains a modified ResumeIR."""
        result = tailor_resume(sample_resume_ir, sample_jd, llm=mock_llm)
        assert isinstance(result.resume, ResumeIR)

    def test_result_has_gap_analysis(
        self,
        sample_resume_ir: ResumeIR,
        sample_jd: JDObject,
        mock_llm: MockLLMProvider,
    ) -> None:
        """Result includes gap analysis."""
        result = tailor_resume(sample_resume_ir, sample_jd, llm=mock_llm)
        assert result.gap_analysis is not None

    def test_header_never_modified(
        self,
        sample_resume_ir: ResumeIR,
        sample_jd: JDObject,
        mock_llm: MockLLMProvider,
    ) -> None:
        """Header is never changed by tailoring."""
        result = tailor_resume(sample_resume_ir, sample_jd, llm=mock_llm)
        assert result.resume.header.name == sample_resume_ir.header.name
        assert result.resume.header.email == sample_resume_ir.header.email
        assert result.resume.header.phone == sample_resume_ir.header.phone

    def test_education_never_modified(
        self,
        sample_resume_ir: ResumeIR,
        sample_jd: JDObject,
        mock_llm: MockLLMProvider,
    ) -> None:
        """Education entries are never changed."""
        result = tailor_resume(sample_resume_ir, sample_jd, llm=mock_llm)
        assert len(result.resume.education) == len(sample_resume_ir.education)
        for orig, mod in zip(sample_resume_ir.education, result.resume.education, strict=True):
            assert orig.school == mod.school
            assert orig.degree == mod.degree
            assert orig.dates == mod.dates

    def test_experience_titles_preserved(
        self,
        sample_resume_ir: ResumeIR,
        sample_jd: JDObject,
        mock_llm: MockLLMProvider,
    ) -> None:
        """Job titles are never changed."""
        result = tailor_resume(sample_resume_ir, sample_jd, llm=mock_llm)
        for orig, mod in zip(sample_resume_ir.experience, result.resume.experience, strict=True):
            assert orig.title == mod.title
            assert orig.company == mod.company
            assert orig.dates == mod.dates

    def test_skills_not_added_or_removed(
        self,
        sample_resume_ir: ResumeIR,
        sample_jd: JDObject,
        mock_llm: MockLLMProvider,
    ) -> None:
        """Skills are reordered but not added/removed."""
        result = tailor_resume(sample_resume_ir, sample_jd, llm=mock_llm)
        for orig_cat, mod_cat in zip(sample_resume_ir.skills, result.resume.skills, strict=True):
            assert set(orig_cat.items) == set(mod_cat.items)

    def test_section_order_preserved(
        self,
        sample_resume_ir: ResumeIR,
        sample_jd: JDObject,
        mock_llm: MockLLMProvider,
    ) -> None:
        """Section ordering is preserved."""
        result = tailor_resume(sample_resume_ir, sample_jd, llm=mock_llm)
        assert result.resume.section_order == sample_resume_ir.section_order

    def test_no_summary_skips_summary_rewrite(
        self,
        sample_jd: JDObject,
        mock_llm: MockLLMProvider,
    ) -> None:
        """Resume without summary skips summary rewrite step."""
        ir = ResumeIR(
            header=HeaderSection(name="Test User"),
            experience=[
                ExperienceEntry(
                    company="Co",
                    title="Eng",
                    dates="2020",
                    bullets=[BulletPoint(id="exp_0_0", text="Did stuff")],
                ),
            ],
            skills=[SkillCategory(category="Lang", items=["Python"])],
        )
        result = tailor_resume(ir, sample_jd, llm=mock_llm)
        assert result.resume.summary is None
