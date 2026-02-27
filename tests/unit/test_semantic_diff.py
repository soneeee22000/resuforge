"""Unit tests for the semantic diff module — all mocked."""

from __future__ import annotations

from resuforge.resume.ir_schema import GapAnalysis, JDObject, ResumeIR
from resuforge.tailoring.semantic_diff import compute_gap_analysis
from tests.conftest import MockLLMProvider


class TestComputeGapAnalysis:
    """Tests for gap analysis computation."""

    def test_returns_gap_analysis(
        self,
        sample_resume_ir: ResumeIR,
        sample_jd: JDObject,
        mock_llm: MockLLMProvider,
    ) -> None:
        """Returns a GapAnalysis object."""
        result = compute_gap_analysis(sample_resume_ir, sample_jd, llm=mock_llm)
        assert isinstance(result, GapAnalysis)

    def test_has_strengths(
        self,
        sample_resume_ir: ResumeIR,
        sample_jd: JDObject,
        mock_llm: MockLLMProvider,
    ) -> None:
        """Result contains strengths."""
        result = compute_gap_analysis(sample_resume_ir, sample_jd, llm=mock_llm)
        assert len(result.strengths) > 0

    def test_has_gaps(
        self,
        sample_resume_ir: ResumeIR,
        sample_jd: JDObject,
        mock_llm: MockLLMProvider,
    ) -> None:
        """Result contains gaps."""
        result = compute_gap_analysis(sample_resume_ir, sample_jd, llm=mock_llm)
        assert len(result.gaps) > 0

    def test_has_opportunities(
        self,
        sample_resume_ir: ResumeIR,
        sample_jd: JDObject,
        mock_llm: MockLLMProvider,
    ) -> None:
        """Result contains opportunities."""
        result = compute_gap_analysis(sample_resume_ir, sample_jd, llm=mock_llm)
        assert len(result.opportunities) > 0

    def test_llm_called_once(
        self,
        sample_resume_ir: ResumeIR,
        sample_jd: JDObject,
        mock_llm: MockLLMProvider,
    ) -> None:
        """Makes exactly one LLM call."""
        compute_gap_analysis(sample_resume_ir, sample_jd, llm=mock_llm)
        assert len(mock_llm.calls) == 1

    def test_llm_gets_system_prompt(
        self,
        sample_resume_ir: ResumeIR,
        sample_jd: JDObject,
        mock_llm: MockLLMProvider,
    ) -> None:
        """LLM receives the tailoring system prompt."""
        compute_gap_analysis(sample_resume_ir, sample_jd, llm=mock_llm)
        system = mock_llm.calls[0]["system"]
        assert isinstance(system, str)
        assert "ONLY reference" in system

    def test_custom_gap_analysis(
        self,
        sample_resume_ir: ResumeIR,
        sample_jd: JDObject,
    ) -> None:
        """Custom mock response is returned."""
        custom = GapAnalysis(
            strengths=["custom strength"],
            gaps=["custom gap"],
            opportunities=[],
        )
        mock = MockLLMProvider(responses={GapAnalysis: custom})
        result = compute_gap_analysis(sample_resume_ir, sample_jd, llm=mock)
        assert result.strengths == ["custom strength"]
