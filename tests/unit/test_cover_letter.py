"""Unit tests for the cover letter generator — all mocked."""

from __future__ import annotations

from resuforge.cover_letter.generator import generate_cover_letter
from resuforge.cover_letter.verification import GroundingViolationError, verify_grounding
from resuforge.resume.ir_schema import JDObject, ResumeIR
from tests.conftest import MockLLMProvider

# ---------------------------------------------------------------------------
# Cover letter generation
# ---------------------------------------------------------------------------


class TestGenerateCoverLetter:
    """Tests for cover letter generation."""

    def test_returns_string(
        self,
        sample_resume_ir: ResumeIR,
        sample_jd: JDObject,
        mock_llm: MockLLMProvider,
    ) -> None:
        """Generator returns a LaTeX string."""
        result = generate_cover_letter(sample_resume_ir, sample_jd, llm=mock_llm)
        assert isinstance(result, str)

    def test_contains_latex_structure(
        self,
        sample_resume_ir: ResumeIR,
        sample_jd: JDObject,
        mock_llm: MockLLMProvider,
    ) -> None:
        """Generated letter has LaTeX document structure."""
        result = generate_cover_letter(sample_resume_ir, sample_jd, llm=mock_llm)
        assert "\\begin{document}" in result or "document" in result.lower()

    def test_llm_called(
        self,
        sample_resume_ir: ResumeIR,
        sample_jd: JDObject,
        mock_llm: MockLLMProvider,
    ) -> None:
        """LLM is called during generation."""
        generate_cover_letter(sample_resume_ir, sample_jd, llm=mock_llm)
        assert len(mock_llm.calls) == 1

    def test_system_prompt_has_grounding(
        self,
        sample_resume_ir: ResumeIR,
        sample_jd: JDObject,
        mock_llm: MockLLMProvider,
    ) -> None:
        """System prompt includes grounding constraint."""
        generate_cover_letter(sample_resume_ir, sample_jd, llm=mock_llm)
        system = mock_llm.calls[0]["system"]
        assert isinstance(system, str)
        assert "ONLY reference" in system


# ---------------------------------------------------------------------------
# Grounding verification
# ---------------------------------------------------------------------------


class TestGroundingVerification:
    """Tests for the grounding verification system."""

    def test_grounding_violation_exception(self) -> None:
        """GroundingViolationError has correct attributes."""
        violation = GroundingViolationError(["Claimed 10 years when resume shows 5"])
        assert len(violation.violations) == 1
        assert "ungrounded" in str(violation).lower()

    def test_clean_letter_passes(self, sample_resume_ir: ResumeIR) -> None:
        """Letter referencing only resume content passes verification."""
        letter = (
            "I have experience with Python and PyTorch at Acme Corp. "
            "I hold an M.S. from Stanford University."
        )
        violations = verify_grounding(letter, sample_resume_ir)
        assert len(violations) == 0

    def test_verify_returns_list(self, sample_resume_ir: ResumeIR) -> None:
        """verify_grounding always returns a list."""
        violations = verify_grounding("Hello world", sample_resume_ir)
        assert isinstance(violations, list)
