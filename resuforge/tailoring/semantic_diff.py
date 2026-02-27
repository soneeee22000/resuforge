"""Semantic diff — computes the gap between JD requirements and resume content.

Not a vector DB / RAG setup. For a single resume + JD, we pass both
to the LLM in a single context window and get a structured gap analysis.
"""

from __future__ import annotations

from resuforge.resume.ir_schema import GapAnalysis, JDObject, ResumeIR


def compute_gap_analysis(resume: ResumeIR, jd: JDObject) -> GapAnalysis:
    """Compute the semantic gap between a resume and a job description.

    Args:
        resume: The parsed resume IR.
        jd: The parsed job description.

    Returns:
        A GapAnalysis with strengths, gaps, and opportunities.
    """
    # TODO: Implement via LLM call
    # 1. Serialize resume and JD to JSON
    # 2. Send to LLM with PROMPT_GAP_ANALYSIS
    # 3. Return validated GapAnalysis
    raise NotImplementedError("Semantic diff not yet implemented")
