# CLAUDE.md — Instructions for Claude Code

This file tells Claude Code how to work on the ResuForge codebase. Read this before making any changes.

---

## Project Overview

ResuForge is a CLI tool that tailors LaTeX resumes to job descriptions using LLMs. The core pipeline is:

```
JD Input → JD Parser → Structured JD Object
Resume (.tex) → LaTeX Parser → JSON IR (Intermediate Representation)
[JD Object + JSON IR] → Tailoring Engine → Modified JSON IR + Change Log
Modified JSON IR → LaTeX Renderer → Output (.tex)
Modified JSON IR → Cover Letter Generator → cover_letter.tex
```

---

## Architecture Principles

1. **Never manipulate LaTeX strings directly** — always go through the JSON IR. The parser converts `.tex` → IR, the renderer converts IR → `.tex`. Logic operates on IR only.

2. **All LLM prompts live in `prompts.py` files** — never inline prompt strings in logic code.

3. **Structured output always** — every LLM call must return a validated Pydantic model. Use `instructor` for this. No raw string parsing of LLM output.

4. **Grounding is sacred** — the cover letter and tailoring engine must NEVER add skills, experience, or credentials that don't exist in the resume IR. This is a hard constraint enforced both in system prompts and via post-generation verification.

5. **Changes are logged** — every modification the tailoring engine makes must be recorded as a `Change` object with `original`, `modified`, and `reason` fields.

---

## File Structure

```
resuforge/
├── cli/                    # Click CLI entrypoints
├── ingestion/              # JD parsing (text, PDF, URL)
├── resume/                 # LaTeX parser, renderer, IR schema
├── tailoring/              # Core tailoring logic and prompts
├── cover_letter/           # Cover letter generation
├── llm/                    # LLM provider abstraction (Anthropic/OpenAI)
├── config/                 # Config management (~/.resuforge/config.yaml)
└── utils/                  # Diff display, file utilities
tests/
├── fixtures/
│   ├── resumes/            # Sample .tex files for testing
│   ├── jds/                # Sample JD text files
│   └── expected/           # Snapshot outputs
├── unit/
├── integration/
└── e2e/
```

---

## Key Data Models (in `resume/ir_schema.py`)

Always use these models — don't create ad-hoc dicts:

```python
ResumeIR          # Top-level resume structure
HeaderSection     # Name, email, links
ExperienceEntry   # Company, title, dates, bullets
BulletPoint       # id, text (bullets have stable IDs for change tracking)
SkillCategory     # Category name + list of skill strings
EducationEntry    # School, degree, dates
ProjectEntry      # Name, description, bullets, links
JDObject          # Parsed job description
GapAnalysis       # Strengths, gaps, opportunities from semantic diff
Change            # Single tracked change: section, original, modified, reason
TailoringResult   # Modified ResumeIR + list of Changes
```

---

## LLM Usage Rules

- Default model: `claude-3-5-sonnet-20241022` (configurable)
- Temperature: `0.3` for all tailoring tasks
- Always pass structured output schema to LLM (via `instructor`)
- Retry logic: 3 retries with exponential backoff on API errors
- Never exceed 4000 tokens per call — split large resumes if needed

### Tailoring system prompt must always include:
```
You may ONLY reference skills, experience, projects, and facts 
that are present in the provided resume JSON. Do not invent, 
imply, or suggest anything that is not explicitly in the resume.
```

---

## Testing Conventions

- **Unit tests**: fast, no LLM calls, use fixtures
- **Integration tests**: may make real LLM calls, marked with `@pytest.mark.integration`
- **Round-trip test**: critical — parse `.tex` → render back → parse again → assert structural equality
- Run fast tests: `pytest tests/unit/`
- Run all tests: `pytest` (requires API key)

---

## CLI Commands Being Built

```bash
resuforge tailor --resume <path> --jd <path> [--cover-letter] [--diff] [--dry-run] [--output-dir <path>]
resuforge profile --add <path> --list --use <name>
resuforge config --set-key <key> --set-model <model>
```

---

## Current Build Order (v0.1.0)

Build in this order — each stage depends on the previous:

1. `resume/ir_schema.py` — Define all Pydantic models first
2. `resume/latex_parser.py` — Parser (write round-trip tests immediately)
3. `resume/latex_renderer.py` — Renderer (test with parser fixtures)
4. `ingestion/jd_parser.py` — JD extraction
5. `llm/base.py` + `llm/anthropic_client.py` — LLM provider
6. `tailoring/prompts.py` + `tailoring/engine.py` — Core tailoring
7. `cover_letter/generator.py` — Cover letter
8. `cli/tailor.py` — Wire up the CLI
9. `config/settings.py` — Config management

---

## Do Not

- Do not add dependencies without updating `pyproject.toml`
- Do not hardcode API keys anywhere — always read from env or config
- Do not modify anything in `raw_sections` — these pass through untouched
- Do not change job titles, company names, dates, or education entries
- Do not use `print()` for user-facing output — use `rich.console`
- Do not catch bare `Exception` — catch specific exceptions
