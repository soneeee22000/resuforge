# Product Requirements Document — ResuForge

**Version:** 0.1  
**Status:** Draft  
**Author:** ResuForge Core  
**Last Updated:** 2025

---

## 1. Problem Statement

Job seekers — especially engineers, researchers, and technical professionals — maintain LaTeX resumes and spend significant time manually adapting them for each role they apply to. This involves:

- Reordering and rephrasing bullet points to match JD keywords
- Updating the summary/objective section per role
- Adjusting skills sections to surface the most relevant technologies
- Writing fresh cover letters each time

This process is repetitive, error-prone, and time-consuming. Existing tools either operate on Word/PDF formats (not LaTeX), rewrite entire resumes (losing personal voice), or fabricate experience (a liability). There is no open-source, LaTeX-native, developer-friendly tool that does this intelligently.

---

## 2. Goals

### Primary Goals (v0.1 — CLI MVP)
- Ingest a JD from a text file, PDF, or URL
- Parse a LaTeX resume into editable structured representation
- Make targeted, minimal edits to the resume to better match the JD
- Generate a cover letter grounded strictly in resume content
- Output clean, compilable `.tex` files

### Secondary Goals (v0.2+)
- Diff view showing exactly what changed and why
- Multi-profile management (multiple base resumes)
- ATS score estimation before and after tailoring
- Web UI for non-CLI users

### Non-Goals
- We do NOT fabricate experience, skills, or credentials
- We do NOT support Word/DOCX natively (LaTeX first)
- We do NOT store user resumes on any server (local-first)
- We do NOT replace human judgment — changes are always reviewable

---

## 3. Target Users

### Primary
- Software engineers and ML/AI practitioners with LaTeX resumes
- PhD students and researchers applying to industry roles
- Technical professionals applying to multiple roles simultaneously

### Secondary
- Any professional with a LaTeX resume (finance, consulting, etc.)
- Open-source contributors who want to extend the tool for their field

---

## 4. User Stories

### Must Have (v0.1)

**US-01 — Tailor resume to JD**
> As a job seeker, I want to point ResuForge at my `.tex` resume and a JD, and get back a modified `.tex` that highlights relevant skills and experience, so I don't have to do it manually.

**US-02 — Grounded cover letter**
> As a job seeker, I want a cover letter generated from my actual resume content and the JD, with no invented facts, so I can trust it and submit it quickly.

**US-03 — Preserve LaTeX formatting**
> As a LaTeX user, I want my output `.tex` file to compile cleanly and retain all my custom formatting, fonts, and structure — only the content should change.

**US-04 — Dry run mode**
> As a cautious user, I want to see what changes would be made before they're written to disk, so I can decide whether to proceed.

**US-05 — API key configuration**
> As a developer, I want to set my preferred LLM provider and API key once and have it persist across sessions.

### Should Have (v0.2)

**US-06 — Diff view**
> As a user, I want to see a clear, readable diff of original vs. tailored resume, annotated with the reasoning behind each change.

**US-07 — Profile management**
> As a power user, I want to store multiple base resumes (e.g., one ML-focused, one backend-focused) and choose which to tailor per application.

**US-08 — Batch mode**
> As someone applying to many roles, I want to process multiple JDs against my resume in one command and get organized output folders.

### Nice to Have (v0.3+)

**US-09 — ATS score**
> As a user, I want to see an estimated ATS match score before and after tailoring to quantify improvement.

**US-10 — Web UI**
> As a non-CLI user, I want a simple web interface where I can upload my resume and paste a JD and get results without using the terminal.

---

## 5. Functional Requirements

### 5.1 JD Ingestion Module

| ID | Requirement |
|---|---|
| F-JD-01 | Accept JD as plain text file (`.txt`, `.md`) |
| F-JD-02 | Accept JD as PDF file |
| F-JD-03 | Accept JD as a URL (scrape and clean the text) |
| F-JD-04 | Extract: job title, company name, required skills, preferred skills, responsibilities, years of experience |
| F-JD-05 | Normalize extracted skills to canonical forms (e.g., "ML" → "machine learning") |
| F-JD-06 | Output a structured JD object (JSON) for downstream use |

### 5.2 LaTeX Resume Parser

| ID | Requirement |
|---|---|
| F-LP-01 | Parse `.tex` file into a structured JSON Intermediate Representation (IR) |
| F-LP-02 | Identify and preserve: preamble, document class, packages, custom commands |
| F-LP-03 | Segment resume into sections: header, summary, experience, education, skills, projects, publications (if present) |
| F-LP-04 | For experience entries: extract company, title, dates, and individual bullet points |
| F-LP-05 | For skills section: extract skill categories and items |
| F-LP-06 | Flag LaTeX commands that must not be modified (e.g., `\begin`, `\end`, custom macros) |
| F-LP-07 | Round-trip test: parse → serialize back to LaTeX → compile successfully |

### 5.3 Tailoring Engine

| ID | Requirement |
|---|---|
| F-TE-01 | Perform semantic comparison between JD requirements and resume content |
| F-TE-02 | Identify gaps (required JD skills not present or underemphasized in resume) |
| F-TE-03 | Identify strengths (resume content that directly matches JD) |
| F-TE-04 | Edit the summary/objective section to open with role-relevant framing |
| F-TE-05 | Reorder skills within skills section to surface JD-relevant ones first |
| F-TE-06 | Rephrase existing bullet points in experience to use JD language where accurate |
| F-TE-07 | Never add skills, tools, or experience the user does not have |
| F-TE-08 | Never remove substantive content — only reframe and reorder |
| F-TE-09 | All edits must be explainable — each change must have a logged reason |
| F-TE-10 | Preserve the user's voice and writing style |

### 5.4 Cover Letter Generator

| ID | Requirement |
|---|---|
| F-CL-01 | Generate a professional cover letter in LaTeX format |
| F-CL-02 | Grounding constraint: only reference facts present in the resume IR |
| F-CL-03 | Structure: opening hook, 2-3 body paragraphs (experience alignment, skills, motivation), closing |
| F-CL-04 | Incorporate company name and role title from JD |
| F-CL-05 | Configurable tone: professional (default) or conversational |
| F-CL-06 | Output as `.tex` file, compilable independently |

### 5.5 LaTeX Renderer

| ID | Requirement |
|---|---|
| F-LR-01 | Serialize modified JSON IR back to syntactically valid LaTeX |
| F-LR-02 | Preserve all original formatting, spacing, and custom macros |
| F-LR-03 | Output must compile with `pdflatex` or `xelatex` without errors |
| F-LR-04 | Optionally auto-compile to PDF if `latexmk` is available on system |

### 5.6 CLI Interface

| ID | Requirement |
|---|---|
| F-CLI-01 | Primary command: `resuforge tailor` with required `--resume` and `--jd` flags |
| F-CLI-02 | `--dry-run` flag: print changes to stdout, no file writes |
| F-CLI-03 | `--diff` flag: show colored diff of original vs. tailored |
| F-CLI-04 | `--cover-letter` flag: also generate cover letter |
| F-CLI-05 | `--output` / `--output-dir` flags for controlling output location |
| F-CLI-06 | `resuforge config` subcommand for managing API keys and defaults |
| F-CLI-07 | `resuforge profile` subcommand for managing resume profiles |
| F-CLI-08 | Verbose mode with `--verbose` for debugging |
| F-CLI-09 | Clean, human-readable progress output with status indicators |

---

## 6. Non-Functional Requirements

| ID | Requirement |
|---|---|
| NF-01 | End-to-end tailoring (resume + cover letter) completes in under 30 seconds |
| NF-02 | All user data (resume, JD, outputs) remains on local machine — nothing sent to servers beyond LLM API calls |
| NF-03 | LLM provider is configurable — not locked to a single vendor |
| NF-04 | Tool works offline for parsing/diffing (LLM calls only for generation) |
| NF-05 | Comprehensive test suite with round-trip LaTeX parse/render tests |
| NF-06 | Python 3.10+ compatibility |
| NF-07 | Installable via `pip install resuforge` |
| NF-08 | MIT licensed |

---

## 7. System Architecture Overview

```
resuforge/
├── cli/                    # Click-based CLI entrypoints
│   ├── tailor.py
│   ├── profile.py
│   └── config.py
├── ingestion/              # JD ingestion
│   ├── jd_parser.py        # Text/PDF/URL → structured JD object
│   └── extractors.py       # Skill/requirement extraction via LLM
├── resume/                 # LaTeX resume handling
│   ├── latex_parser.py     # .tex → JSON IR
│   ├── latex_renderer.py   # JSON IR → .tex
│   └── ir_schema.py        # Pydantic models for IR
├── tailoring/              # Core tailoring logic
│   ├── engine.py           # Orchestration
│   ├── semantic_diff.py    # JD ↔ resume semantic comparison
│   └── prompts.py          # All LLM prompt templates
├── cover_letter/           # Cover letter generation
│   ├── generator.py
│   └── prompts.py
├── llm/                    # LLM provider abstraction
│   ├── base.py
│   ├── anthropic_client.py
│   └── openai_client.py
├── config/                 # Config management
│   └── settings.py
└── utils/
    ├── diff.py
    └── file_utils.py
```

---

## 8. Data Models

### JD Object (JSON)
```json
{
  "raw_text": "...",
  "job_title": "Senior ML Engineer",
  "company": "Acme Corp",
  "required_skills": ["Python", "PyTorch", "MLOps"],
  "preferred_skills": ["Kubernetes", "Ray"],
  "responsibilities": ["Train and deploy models", "..."],
  "experience_years": 5,
  "education_requirement": "BS/MS in CS or related",
  "keywords": ["distributed training", "production ML", "..."]
}
```

### Resume IR (JSON)
```json
{
  "preamble": "\\documentclass[11pt]{article}...",
  "header": {
    "name": "Jane Doe",
    "email": "jane@example.com",
    "links": [{"label": "GitHub", "url": "..."}]
  },
  "summary": "ML engineer with 5 years experience...",
  "experience": [
    {
      "company": "OpenAI",
      "title": "Research Engineer",
      "dates": "2022 - Present",
      "bullets": [
        {"id": "exp_0_0", "text": "Trained 70B parameter models on 512 H100s"}
      ]
    }
  ],
  "skills": [
    {"category": "Languages", "items": ["Python", "C++", "Rust"]}
  ],
  "education": [...],
  "projects": [...],
  "raw_sections": {}
}
```

---

## 9. LLM Strategy

### Provider Abstraction
All LLM calls go through a provider-agnostic interface. Default: Anthropic Claude (Sonnet tier for speed/cost balance). Fallback: OpenAI GPT-4o.

### Prompt Design Principles
- All prompts use structured output (JSON mode where available)
- Grounding constraint is enforced via explicit system-level instruction: *"You may only reference skills, experience, and facts present in the provided resume JSON. Do not invent or imply anything not present."*
- Each edit includes a `reason` field explaining the change — enables diff view and user trust
- Temperature: 0.3 (low — we want consistent, precise edits, not creative rewrites)

### Token Budget
- JD extraction: ~500 tokens
- Resume tailoring: ~2000-3000 tokens depending on resume length
- Cover letter: ~1000 tokens
- Total per application: ~4000 tokens (~$0.02 at Sonnet pricing)

---

## 10. Testing Strategy

| Layer | Approach |
|---|---|
| LaTeX Parser | Round-trip tests on 5+ real-world resume templates |
| JD Extractor | Unit tests against 10+ sample JDs across industries |
| Tailoring Engine | Snapshot tests — given input IR + JD, output must match expected delta |
| Cover Letter | Grounding assertion tests — verify no fact in output is absent from IR |
| CLI | Integration tests using `click.testing.CliRunner` |
| End-to-end | Full pipeline test on 3 persona × 3 JD combinations |

---

## 11. Open Source Strategy

- License: MIT
- Host: GitHub
- Initial release: CLI MVP with 3 example resume templates and 5 sample JDs
- README includes: quickstart, how it works, contribution guide
- First community features: support for additional LaTeX resume templates
- Potential future: plugin system for custom section handlers

---

## 12. Versioning Plan

| Version | Scope |
|---|---|
| v0.1.0 | CLI MVP — tailor + cover letter, text/PDF JD input |
| v0.2.0 | Diff view, batch mode, profile management, URL JD input |
| v0.3.0 | Web UI (FastAPI + React), PDF output |
| v0.4.0 | ATS score estimation, multi-language support |
