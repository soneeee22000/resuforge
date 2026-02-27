"""Cover letter generator — produces LaTeX cover letters grounded in resume IR.

Grounding enforcement: the system prompt receives only the ResumeIR JSON,
not the raw .tex. A post-generation verification pass checks that every
named claim appears in the IR.
"""

from __future__ import annotations

from pydantic import BaseModel

from resuforge.cover_letter.prompts import PROMPT_COVER_LETTER, SYSTEM_COVER_LETTER
from resuforge.cover_letter.verification import GroundingViolationError, verify_grounding
from resuforge.llm.base import LLMProvider
from resuforge.resume.ir_schema import JDObject, ResumeIR


class CoverLetterResponse(BaseModel):
    """LLM response for cover letter generation."""

    content: str


def generate_cover_letter(
    resume: ResumeIR,
    jd: JDObject,
    *,
    llm: LLMProvider,
) -> str:
    """Generate a grounded cover letter in LaTeX format.

    Args:
        resume: The resume IR (source of truth for all claims).
        jd: The parsed job description.
        llm: LLM provider for generation.

    Returns:
        A compilable LaTeX string for the cover letter.

    Raises:
        GroundingViolationError: If the generated letter references facts
            not present in the resume IR.
    """
    resume_json = resume.model_dump_json(indent=2)
    jd_json = jd.model_dump_json(indent=2)

    company = jd.company or "the company"
    job_title = jd.job_title or "the position"

    user_prompt = PROMPT_COVER_LETTER.format(
        resume_json=resume_json,
        jd_json=jd_json,
        company=company,
        job_title=job_title,
    )

    response = llm.complete(
        system=SYSTEM_COVER_LETTER,
        user=user_prompt,
        response_model=CoverLetterResponse,
    )

    letter_text = response.content

    # Post-generation grounding check
    violations = verify_grounding(letter_text, resume)
    if violations:
        raise GroundingViolationError(violations)

    return letter_text
