"""Cover letter generator — produces LaTeX cover letters grounded in resume IR.

Grounding enforcement: the system prompt receives only the ResumeIR JSON,
not the raw .tex. A post-generation verification pass checks that every
named claim appears in the IR.
"""

from __future__ import annotations

from resuforge.resume.ir_schema import JDObject, ResumeIR


def generate_cover_letter(resume: ResumeIR, jd: JDObject) -> str:
    """Generate a grounded cover letter in LaTeX format.

    Args:
        resume: The resume IR (source of truth for all claims).
        jd: The parsed job description.

    Returns:
        A compilable LaTeX string for the cover letter.

    Raises:
        GroundingViolation: If the generated letter references facts
            not present in the resume IR.
    """
    # TODO: Implement cover letter generation
    # 1. Serialize resume IR to JSON for LLM context
    # 2. Generate via LLM with grounding constraints
    # 3. Post-generation verification pass
    # 4. Return LaTeX string
    raise NotImplementedError("Cover letter generator not yet implemented")
