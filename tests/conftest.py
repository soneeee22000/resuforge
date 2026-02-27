"""Shared test fixtures for ResuForge test suite."""

from __future__ import annotations

from pathlib import Path

import pytest

from resuforge.resume.ir_schema import (
    BulletPoint,
    EducationEntry,
    ExperienceEntry,
    HeaderSection,
    Link,
    ResumeIR,
    SkillCategory,
)

FIXTURES_DIR = Path(__file__).parent / "fixtures"
RESUME_FIXTURES_DIR = FIXTURES_DIR / "resumes"
JD_FIXTURES_DIR = FIXTURES_DIR / "jds"
EXPECTED_DIR = FIXTURES_DIR / "expected"


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
