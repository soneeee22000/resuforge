"""Semantic diff — computes the gap between JD requirements and resume content.

Not a vector DB / RAG setup. For a single resume + JD, we pass both
to the LLM in a single context window and get a structured gap analysis.
"""

from __future__ import annotations

from resuforge.llm.base import LLMProvider
from resuforge.resume.ir_schema import GapAnalysis, JDObject, ResumeIR
from resuforge.tailoring.prompts import PROMPT_GAP_ANALYSIS, SYSTEM_TAILORING


def compute_gap_analysis(
    resume: ResumeIR,
    jd: JDObject,
    *,
    llm: LLMProvider,
) -> GapAnalysis:
    """Compute the semantic gap between a resume and a job description.

    Args:
        resume: The parsed resume IR.
        jd: The parsed job description.
        llm: LLM provider for analysis.

    Returns:
        A GapAnalysis with strengths, gaps, and opportunities.
    """
    resume_json = resume.model_dump_json(indent=2)
    jd_json = jd.model_dump_json(indent=2)

    user_prompt = PROMPT_GAP_ANALYSIS.format(
        resume_json=resume_json,
        jd_json=jd_json,
    )

    return llm.complete(
        system=SYSTEM_TAILORING,
        user=user_prompt,
        response_model=GapAnalysis,
    )
