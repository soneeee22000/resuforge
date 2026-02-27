"""Smoke tests — verify the project is properly set up and importable."""

from __future__ import annotations


def test_package_imports() -> None:
    """Verify all package modules are importable."""
    import resuforge
    import resuforge.cli
    import resuforge.config
    import resuforge.cover_letter
    import resuforge.ingestion
    import resuforge.llm
    import resuforge.resume
    import resuforge.tailoring
    import resuforge.utils

    assert resuforge.__version__ == "0.1.0"


def test_ir_schema_models() -> None:
    """Verify IR schema models can be instantiated."""
    from resuforge.resume.ir_schema import (
        BulletPoint,
        Change,
        HeaderSection,
        JDObject,
        ResumeIR,
        TailoringResult,
    )

    header = HeaderSection(name="Test User")
    assert header.name == "Test User"
    assert header.email is None

    bullet = BulletPoint(id="exp_0_0", text="Did something impactful")
    assert bullet.id == "exp_0_0"

    ir = ResumeIR(header=header)
    assert ir.header.name == "Test User"
    assert ir.experience == []
    assert ir.raw_sections == {}

    jd = JDObject(raw_text="We are looking for an engineer")
    assert jd.job_title is None
    assert jd.required_skills == []

    change = Change(
        section="summary",
        original="Old summary",
        modified="New summary",
        reason="Better alignment with JD",
    )
    assert change.section == "summary"

    result = TailoringResult(resume=ir, changes=[change])
    assert len(result.changes) == 1


def test_sample_resume_fixture(sample_resume_ir: object) -> None:
    """Verify the sample resume fixture is valid."""
    from resuforge.resume.ir_schema import ResumeIR

    assert isinstance(sample_resume_ir, ResumeIR)
    assert sample_resume_ir.header.name == "Jane Doe"
    assert len(sample_resume_ir.experience) == 1
    assert len(sample_resume_ir.skills) == 2
    assert len(sample_resume_ir.experience[0].bullets) == 2


def test_cli_entrypoint_exists() -> None:
    """Verify CLI app can be imported."""
    from resuforge.cli.main import app

    assert app is not None
    assert callable(app)
