"""Shared test fixtures for ResuForge test suite."""

from __future__ import annotations

from pathlib import Path
from typing import TypeVar

import pytest
from pydantic import BaseModel

from resuforge.llm.base import LLMProvider
from resuforge.resume.ir_schema import (
    BulletPoint,
    Change,
    EducationEntry,
    ExperienceEntry,
    GapAnalysis,
    HeaderSection,
    JDObject,
    Link,
    ResumeIR,
    SkillCategory,
)

T = TypeVar("T", bound=BaseModel)

FIXTURES_DIR = Path(__file__).parent / "fixtures"
RESUME_FIXTURES_DIR = FIXTURES_DIR / "resumes"
JD_FIXTURES_DIR = FIXTURES_DIR / "jds"
EXPECTED_DIR = FIXTURES_DIR / "expected"


class MockLLMProvider(LLMProvider):
    """Mock LLM provider for unit tests.

    Returns pre-built responses based on the requested response_model type.
    Records calls for assertion.
    """

    def __init__(self, responses: dict[type[BaseModel], BaseModel] | None = None) -> None:
        """Initialize with optional response overrides.

        Args:
            responses: Map of model type -> response instance.
        """
        self.responses: dict[type[BaseModel], BaseModel] = responses or {}
        self.calls: list[dict[str, object]] = []

    def complete(
        self,
        *,
        system: str,
        user: str,
        response_model: type[T],
        temperature: float = 0.3,
        max_tokens: int = 4000,
    ) -> T:
        """Return pre-configured response for the requested model type.

        Args:
            system: System prompt.
            user: User prompt.
            response_model: Expected response model type.
            temperature: Sampling temperature.
            max_tokens: Max tokens.

        Returns:
            Pre-configured response instance.
        """
        self.calls.append(
            {
                "system": system,
                "user": user,
                "response_model": response_model,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
        )

        if response_model in self.responses:
            return self.responses[response_model]  # type: ignore[return-value]

        # Default responses for known types
        return _default_response(response_model)


def _default_response(model: type[T]) -> T:
    """Generate a default response for a known model type.

    Args:
        model: Pydantic model class.

    Returns:
        Default instance of the model.
    """
    name = model.__name__ if hasattr(model, "__name__") else ""

    if model is GapAnalysis or name == "GapAnalysis":
        return GapAnalysis(  # type: ignore[return-value]
            strengths=["Strong Python experience", "ML deployment knowledge"],
            gaps=["No Kubernetes experience mentioned"],
            opportunities=["Could reframe data pipeline work for relevance"],
        )

    # Summary rewrite response
    if name == "SummaryResponse":
        return model(  # type: ignore[call-arg]
            summary="Production ML engineer with 5 years deploying scalable systems.",
            reason="Aligned with JD focus on deployment",
            jd_keyword="deployment",
        )

    # Bullet rephrase response
    if name == "BulletResponse":
        return model(  # type: ignore[call-arg]
            text="Led development and deployment of production recommendation system",
            reason="Added deployment emphasis",
            jd_keyword="deployment",
        )

    # Skills reorder response
    if name == "SkillsReorderResponse":
        return model(categories=[])  # type: ignore[call-arg]

    # Cover letter response
    if name == "CoverLetterResponse":
        return model(  # type: ignore[call-arg]
            content=(
                "\\documentclass{letter}\n\\begin{document}\n"
                "Dear Hiring Manager,\n\n"
                "I am writing to apply for the position.\n\n"
                "Sincerely,\nJane Doe\n"
                "\\end{document}"
            ),
        )

    raise ValueError(f"No default mock response configured for {name}")


@pytest.fixture()
def fixtures_dir() -> Path:
    """Return the path to the test fixtures directory."""
    return FIXTURES_DIR


@pytest.fixture()
def sample_resume_ir() -> ResumeIR:
    """Return a minimal but complete ResumeIR for testing."""
    return ResumeIR(
        preamble=r"\documentclass[11pt]{article}",
        header=HeaderSection(
            name="Jane Doe",
            email="jane@example.com",
            phone="+1-555-0100",
            location="San Francisco, CA",
            links=[
                Link(label="GitHub", url="https://github.com/janedoe"),
                Link(label="LinkedIn", url="https://linkedin.com/in/janedoe"),
            ],
        ),
        summary="ML engineer with 5 years of experience building production models.",
        experience=[
            ExperienceEntry(
                company="Acme Corp",
                title="Senior ML Engineer",
                dates="2022 - Present",
                location="San Francisco, CA",
                bullets=[
                    BulletPoint(id="exp_0_0", text="Led development of recommendation system"),
                    BulletPoint(id="exp_0_1", text="Reduced model inference latency by 40%"),
                ],
            ),
        ],
        education=[
            EducationEntry(
                school="Stanford University",
                degree="M.S. Computer Science",
                dates="2018 - 2020",
            ),
        ],
        skills=[
            SkillCategory(category="Languages", items=["Python", "C++", "Rust"]),
            SkillCategory(category="ML/AI", items=["PyTorch", "TensorFlow", "MLOps"]),
        ],
        section_order=["header", "summary", "experience", "skills", "education"],
    )


@pytest.fixture()
def sample_jd() -> JDObject:
    """Return a sample JDObject for testing."""
    return JDObject(
        raw_text="We are looking for an ML Engineer...",
        job_title="Machine Learning Engineer",
        company="AI Dynamics",
        required_skills=["Python", "PyTorch", "TensorFlow", "MLOps"],
        preferred_skills=["Kubernetes", "Real-time inference"],
        responsibilities=[
            "Design and deploy production ML models",
            "Build ML pipelines for data processing",
        ],
        keywords=["ML", "Python", "PyTorch", "production", "deployment"],
        experience_years=3,
        education_requirement="Master's degree in Computer Science",
    )


@pytest.fixture()
def mock_llm() -> MockLLMProvider:
    """Return a MockLLMProvider with default responses."""
    return MockLLMProvider()


@pytest.fixture()
def sample_gap_analysis() -> GapAnalysis:
    """Return a sample GapAnalysis for testing."""
    return GapAnalysis(
        strengths=["Strong Python experience", "ML deployment knowledge"],
        gaps=["No Kubernetes experience mentioned"],
        opportunities=["Could reframe data pipeline work for relevance"],
    )


@pytest.fixture()
def sample_changes() -> list[Change]:
    """Return sample Change objects for testing."""
    return [
        Change(
            section="summary",
            original="ML engineer with 5 years of experience building production models.",
            modified="ML engineer with 5 years of experience deploying production ML systems.",
            reason="Aligned language with JD emphasis on deployment",
            jd_keyword="deployment",
        ),
        Change(
            section="experience",
            original="Led development of recommendation system",
            modified="Led development and deployment of recommendation system serving 10M users",
            reason="Emphasized deployment aspect matching JD requirements",
            jd_keyword="production",
        ),
    ]
