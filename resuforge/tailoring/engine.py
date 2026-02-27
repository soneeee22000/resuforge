"""Core tailoring engine — orchestrates the resume tailoring pipeline.

Takes a ResumeIR and JDObject, performs semantic diff, and produces
a TailoringResult with tracked changes.
"""

from __future__ import annotations

from resuforge.resume.ir_schema import JDObject, ResumeIR, TailoringResult


def tailor_resume(resume: ResumeIR, jd: JDObject) -> TailoringResult:
    """Tailor a resume to match a job description.

    Pipeline:
    1. Perform semantic gap analysis (JD vs resume)
    2. Rewrite summary section with role-relevant framing
    3. Reorder skills to surface JD-relevant ones first
    4. Rephrase experience bullets to use JD language
    5. Log all changes with reasons

    Args:
        resume: The parsed resume IR.
        jd: The parsed job description.

    Returns:
        A TailoringResult containing the modified resume and change log.
    """
    # TODO: Implement tailoring pipeline
    # 1. Run semantic_diff to get GapAnalysis
    # 2. Edit summary
    # 3. Reorder skills
    # 4. Rephrase relevant bullets
    # 5. Collect all Changes
    # 6. Return TailoringResult
    raise NotImplementedError("Tailoring engine not yet implemented")
