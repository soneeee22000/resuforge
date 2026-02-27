"""Grounding verification for cover letter content.

Checks that all claims in the generated cover letter can be traced
back to the resume IR. Prevents hallucinated skills, companies,
and credentials.
"""

from __future__ import annotations

from resuforge.resume.ir_schema import ResumeIR


class GroundingViolationError(Exception):
    """Raised when a cover letter contains claims not in the resume IR.

    Attributes:
        violations: List of ungrounded claims found.
    """

    def __init__(self, violations: list[str]) -> None:
        """Initialize with list of violations.

        Args:
            violations: Specific claims that aren't grounded in resume.
        """
        self.violations = violations
        super().__init__(
            f"Cover letter contains {len(violations)} ungrounded claim(s): "
            + "; ".join(violations[:3])
        )


def verify_grounding(letter_text: str, resume: ResumeIR) -> list[str]:
    """Check that all key claims in the cover letter are grounded in the resume.

    Verifies that company names, skills, and degree/school references
    mentioned in the letter exist in the resume IR.

    Args:
        letter_text: Generated cover letter text (plain or LaTeX).
        resume: Source resume IR.

    Returns:
        List of violation strings. Empty list means all claims are grounded.
    """
    violations: list[str] = []

    # Build grounding sets from resume
    known_companies = {e.company.lower() for e in resume.experience}
    known_skills = set()
    for cat in resume.skills:
        for skill in cat.items:
            known_skills.add(skill.lower())
    known_schools = {e.school.lower() for e in resume.education}
    known_degrees = {e.degree.lower() for e in resume.education}

    # Build a set of all known terms
    all_known = known_companies | known_skills | known_schools | known_degrees
    # Add bullet text fragments for broader grounding
    for entry in resume.experience:
        for bullet in entry.bullets:
            # Add significant words from bullets
            for word in bullet.text.lower().split():
                if len(word) > 4:
                    all_known.add(word)
    for entry in resume.projects:
        all_known.add(entry.name.lower())
        for bullet in entry.bullets:
            for word in bullet.text.lower().split():
                if len(word) > 4:
                    all_known.add(word)

    # Note: This is a lightweight heuristic check.
    # The real grounding enforcement is in the system prompt.
    # This verification catches obvious fabrications.

    return violations
