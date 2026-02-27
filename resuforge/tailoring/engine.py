"""Core tailoring engine — orchestrates the resume tailoring pipeline.

Takes a ResumeIR and JDObject, performs semantic diff, and produces
a TailoringResult with tracked changes.
"""

from __future__ import annotations

import copy

from pydantic import BaseModel, Field

from resuforge.llm.base import LLMProvider
from resuforge.resume.ir_schema import (
    BulletPoint,
    Change,
    JDObject,
    ResumeIR,
    SkillCategory,
    TailoringResult,
)
from resuforge.tailoring.prompts import (
    PROMPT_BULLET_REPHRASE,
    PROMPT_SKILLS_REORDER,
    PROMPT_SUMMARY_REWRITE,
    SYSTEM_TAILORING,
)
from resuforge.tailoring.semantic_diff import compute_gap_analysis


class SummaryResponse(BaseModel):
    """LLM response for summary rewrite."""

    summary: str
    reason: str = ""
    jd_keyword: str = ""


class BulletResponse(BaseModel):
    """LLM response for bullet rephrase."""

    text: str
    reason: str = ""
    jd_keyword: str = ""


class SkillsReorderResponse(BaseModel):
    """LLM response for skills reordering."""

    categories: list[SkillCategoryResponse] = Field(default_factory=list)


class SkillCategoryResponse(BaseModel):
    """Single skill category in reorder response."""

    category: str
    items: list[str]


def tailor_resume(
    resume: ResumeIR,
    jd: JDObject,
    *,
    llm: LLMProvider,
) -> TailoringResult:
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
        llm: LLM provider for generation.

    Returns:
        A TailoringResult containing the modified resume and change log.
    """
    modified = copy.deepcopy(resume)
    changes: list[Change] = []

    # Step 1: Gap analysis
    gap_analysis = compute_gap_analysis(resume, jd, llm=llm)

    # Step 2: Rewrite summary (if present)
    if modified.summary:
        summary_change = _rewrite_summary(modified, jd, llm)
        if summary_change:
            changes.append(summary_change)

    # Step 3: Reorder skills
    skill_changes = _reorder_skills(modified, jd, llm)
    changes.extend(skill_changes)

    # Step 4: Rephrase experience bullets
    bullet_changes = _rephrase_bullets(modified, jd, llm)
    changes.extend(bullet_changes)

    return TailoringResult(
        resume=modified,
        changes=changes,
        gap_analysis=gap_analysis,
    )


def _rewrite_summary(
    ir: ResumeIR,
    jd: JDObject,
    llm: LLMProvider,
) -> Change | None:
    """Rewrite the summary section for JD alignment.

    Args:
        ir: Resume IR (modified in-place).
        jd: Job description.
        llm: LLM provider.

    Returns:
        Change object if summary was modified, None otherwise.
    """
    if not ir.summary:
        return None

    original = ir.summary
    jd_json = jd.model_dump_json(indent=2)
    resume_json = ir.model_dump_json(indent=2)

    user_prompt = PROMPT_SUMMARY_REWRITE.format(
        jd_json=jd_json,
        summary=original,
        resume_json=resume_json,
    )

    response = llm.complete(
        system=SYSTEM_TAILORING,
        user=user_prompt,
        response_model=SummaryResponse,
    )

    if response.summary and response.summary != original:
        ir.summary = response.summary
        return Change(
            section="summary",
            original=original,
            modified=response.summary,
            reason=response.reason or "Aligned summary with JD",
            jd_keyword=response.jd_keyword,
        )

    return None


def _reorder_skills(
    ir: ResumeIR,
    jd: JDObject,
    llm: LLMProvider,
) -> list[Change]:
    """Reorder skills within each category to prioritize JD-relevant ones.

    Args:
        ir: Resume IR (modified in-place).
        jd: Job description.
        llm: LLM provider.

    Returns:
        List of changes for reordered categories.
    """
    if not ir.skills:
        return []

    changes: list[Change] = []
    jd_json = jd.model_dump_json(indent=2)
    skills_json = _skills_to_json(ir.skills)

    user_prompt = PROMPT_SKILLS_REORDER.format(
        jd_json=jd_json,
        skills_json=skills_json,
    )

    response = llm.complete(
        system=SYSTEM_TAILORING,
        user=user_prompt,
        response_model=SkillsReorderResponse,
    )

    if response.categories:
        for i, cat_response in enumerate(response.categories):
            if i >= len(ir.skills):
                break
            original_cat = ir.skills[i]
            new_items = cat_response.items

            # Verify no skills added or removed
            if set(new_items) == set(original_cat.items) and new_items != original_cat.items:
                original_str = ", ".join(original_cat.items)
                modified_str = ", ".join(new_items)
                ir.skills[i] = SkillCategory(
                    category=original_cat.category,
                    items=new_items,
                )
                changes.append(
                    Change(
                        section="skills",
                        original=f"{original_cat.category}: {original_str}",
                        modified=f"{original_cat.category}: {modified_str}",
                        reason="Reordered to prioritize JD-relevant skills",
                    )
                )

    return changes


def _rephrase_bullets(
    ir: ResumeIR,
    jd: JDObject,
    llm: LLMProvider,
) -> list[Change]:
    """Rephrase experience bullets to better match JD language.

    Args:
        ir: Resume IR (modified in-place).
        jd: Job description.
        llm: LLM provider.

    Returns:
        List of changes for rephrased bullets.
    """
    changes: list[Change] = []
    jd_json = jd.model_dump_json(indent=2)

    for entry in ir.experience:
        for j, bullet in enumerate(entry.bullets):
            user_prompt = PROMPT_BULLET_REPHRASE.format(
                jd_json=jd_json,
                bullet_text=bullet.text,
                company=entry.company,
                title=entry.title,
            )

            response = llm.complete(
                system=SYSTEM_TAILORING,
                user=user_prompt,
                response_model=BulletResponse,
            )

            if response.text and response.text != bullet.text:
                original_text = bullet.text
                entry.bullets[j] = BulletPoint(
                    id=bullet.id,
                    text=response.text,
                )
                changes.append(
                    Change(
                        section="experience",
                        original=original_text,
                        modified=response.text,
                        reason=response.reason or "Rephrased for JD alignment",
                        jd_keyword=response.jd_keyword,
                    )
                )

    return changes


def _skills_to_json(skills: list[SkillCategory]) -> str:
    """Serialize skills to a JSON string for prompts.

    Args:
        skills: List of skill categories.

    Returns:
        JSON string representation.
    """
    import json

    data = [{"category": s.category, "items": s.items} for s in skills]
    return json.dumps(data, indent=2)
