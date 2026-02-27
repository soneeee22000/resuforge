# Architecture — ResuForge

## Overview

ResuForge is designed around a clean pipeline architecture. Data flows in one direction: ingest → parse → diff → edit → render. Every stage is independently testable and swappable.

The key architectural decision is the **JSON Intermediate Representation (IR)** — we never manipulate LaTeX strings directly. We parse to structured data, operate on structured data, and render back to LaTeX. This is what makes the tool reliable and extensible.

---

## Pipeline Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLI Layer                               │
│              resuforge tailor --resume --jd                     │
└────────────────────────────┬────────────────────────────────────┘
                             │
              ┌──────────────┴──────────────┐
              ▼                             ▼
   ┌─────────────────┐           ┌─────────────────────┐
   │   JD Ingestion  │           │   Resume Parser     │
   │  ─────────────  │           │  ─────────────────  │
   │  text/PDF/URL   │           │  .tex → JSON IR     │
   │       ↓         │           │                     │
   │  Structured JD  │           │  Structured Resume  │
   └────────┬────────┘           └──────────┬──────────┘
            │                               │
            └──────────────┬────────────────┘
                           ▼
               ┌───────────────────────┐
               │   Tailoring Engine    │
               │  ───────────────────  │
               │  Semantic Diff        │
               │  Section Editor       │
               │  Change Logger        │
               └───────────┬───────────┘
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
   ┌─────────────────┐       ┌─────────────────────┐
   │ LaTeX Renderer  │       │ Cover Letter Gen    │
   │  ─────────────  │       │  ─────────────────  │
   │  JSON IR → .tex │       │  Grounded from IR   │
   └─────────────────┘       └─────────────────────┘
```

---

## Module Breakdown

### `ingestion/jd_parser.py`
Responsible for normalizing JD input regardless of source format.

**Inputs:** `.txt` file path, `.pdf` file path, or URL string  
**Output:** `JDObject` (Pydantic model)

```python
class JDObject(BaseModel):
    raw_text: str
    job_title: Optional[str]
    company: Optional[str]
    required_skills: List[str]
    preferred_skills: List[str]
    responsibilities: List[str]
    keywords: List[str]
    experience_years: Optional[int]
    education_requirement: Optional[str]
```

PDF extraction via `pypdf`. URL scraping via `httpx` + `trafilatura` (handles boilerplate removal cleanly). Skill/keyword extraction is done via a single LLM call with structured output.

---

### `resume/latex_parser.py`
The most critical and complex module. Parses a `.tex` file into a `ResumeIR`.

**Strategy:** Regex + heuristic section detection, NOT a full LaTeX grammar parser (too brittle). We identify known section patterns (`\section{Experience}`, `\begin{itemize}`, etc.) and extract content between them.

**Fallback:** For unknown sections, store as raw LaTeX string in `raw_sections` — they pass through unchanged to renderer.

**Key concern:** Custom macros. We detect `\newcommand` definitions in preamble and treat those tokens as atomic — never split or modify them.

```python
class ResumeIR(BaseModel):
    preamble: str                      # Everything before \begin{document}
    header: HeaderSection
    summary: Optional[str]
    experience: List[ExperienceEntry]
    education: List[EducationEntry]
    skills: List[SkillCategory]
    projects: List[ProjectEntry]
    raw_sections: Dict[str, str]       # Unknown sections, preserved verbatim
    custom_commands: List[str]         # Detected \newcommand defs
```

---

### `resume/latex_renderer.py`
Inverse of the parser. Takes a `ResumeIR` and produces a valid `.tex` string.

**Key constraint:** The renderer must be a pure function — same IR in, same LaTeX out. No state, no side effects.

**Approach:** Template-based rendering. We maintain a set of Jinja2 templates for common resume layouts. The parser detects which template was used (by document class and structure fingerprint) and the renderer uses the matching template.

For resumes using unsupported templates, we do a targeted string-replacement approach — we only replace the specific text content we modified, leaving the surrounding LaTeX structure completely untouched.

---

### `tailoring/engine.py`
Orchestrates the tailoring process. Calls `semantic_diff.py`, then iterates over editable sections.

**Editable sections (v0.1):**
1. `summary` — rewritten to open with role-relevant framing
2. `skills` — reordered (not changed) to surface JD-relevant skills first
3. `experience[*].bullets` — individual bullets can be rephrased

**Non-editable (protected):**
- Job titles, company names, dates
- Education entries
- Header/contact info
- Anything in `raw_sections`

**Change log:** Every modification is recorded as a `Change` object:
```python
class Change(BaseModel):
    section: str        # e.g., "experience[0].bullets[2]"
    original: str
    modified: str
    reason: str         # LLM-provided explanation
    jd_keyword: str     # Which JD requirement triggered this change
```

---

### `tailoring/semantic_diff.py`
Computes the semantic gap between JD requirements and resume content.

**Not a vector DB / RAG setup** — for a single resume + JD, this is overkill. We pass both to the LLM in a single context window and ask it to return a structured gap analysis.

Output: `GapAnalysis` object with `strengths`, `gaps`, and `opportunities` (things in resume that could be reframed to match JD better).

---

### `tailoring/prompts.py`
All LLM prompts live here as constants. Never inline prompts in logic code.

Key prompts:
- `SYSTEM_TAILORING` — global constraint: no fabrication, preserve voice
- `PROMPT_SUMMARY_REWRITE`
- `PROMPT_BULLET_REPHRASE`
- `PROMPT_SKILLS_REORDER`
- `PROMPT_GAP_ANALYSIS`

Prompts use XML-style tags to clearly delimit resume content from instructions (Anthropic best practice).

---

### `llm/base.py`
Abstract base class for LLM providers.

```python
class LLMProvider(ABC):
    @abstractmethod
    def complete(self, system: str, user: str, response_model: Type[BaseModel]) -> BaseModel:
        ...
```

Both `AnthropicClient` and `OpenAIClient` implement this. Structured output enforced via Pydantic models + instructor library.

---

### `cover_letter/generator.py`
Generates a LaTeX cover letter grounded in resume IR.

**Grounding enforcement:** The system prompt is given only the `ResumeIR` JSON — not the raw `.tex`. This prevents the model from referencing anything beyond what was parsed. A post-generation verification pass checks that every named claim (company, role, skill, project) appears in the IR.

**Output:** A standalone `.tex` file using a simple letter template.

---

## Key Design Decisions

### Why JSON IR instead of direct LaTeX manipulation?
Direct string manipulation of LaTeX is fragile — a misplaced `%` or `\` breaks compilation. The IR approach gives us a clean, typed representation to reason about and test independently of LaTeX syntax.

### Why heuristic parsing instead of a full LaTeX grammar?
Full LaTeX parsing (e.g., via `pylatexenc`) is complex and still brittle for arbitrary user-generated resumes. A heuristic approach that handles the 95% case and safely passes through the rest is more robust in practice.

### Why instructor for structured output?
Tool calling / function calling is the most reliable way to get structured JSON from LLMs. `instructor` wraps both Anthropic and OpenAI APIs cleanly and handles retries on validation failure.

### Why low temperature (0.3)?
We want precise, conservative edits — not creative rewrites. Lower temperature means more deterministic outputs that are easier to test and trust.

---

## Dependency Stack

```
click                   # CLI framework
pydantic v2             # Data models and validation
instructor              # Structured LLM output
anthropic               # Anthropic API client
openai                  # OpenAI API client
pypdf                   # PDF text extraction
httpx                   # HTTP client for URL JD input
trafilatura             # Web content extraction / boilerplate removal
jinja2                  # LaTeX template rendering
rich                    # Terminal output formatting
typer                   # (Considered — sticking with click for now)
pytest                  # Testing
```

---

## Error Handling Strategy

| Error Type | Handling |
|---|---|
| LaTeX parse failure | Warn user, fall back to raw-section passthrough |
| LLM API error | Retry 3× with exponential backoff, then fail gracefully |
| Compilation failure | Detect via `latexmk` exit code, surface diff to user |
| Grounding violation | Post-generation check fails → regenerate with stricter constraint |
| Invalid JD format | Attempt extraction anyway, warn about low-confidence fields |

---

## Testing Architecture

```
tests/
├── fixtures/
│   ├── resumes/          # 5 real-world LaTeX resume templates
│   ├── jds/              # 10 sample JDs across industries
│   └── expected/         # Expected output snapshots
├── unit/
│   ├── test_latex_parser.py
│   ├── test_latex_renderer.py
│   ├── test_jd_parser.py
│   └── test_tailoring_engine.py
├── integration/
│   ├── test_pipeline.py
│   └── test_cli.py
└── e2e/
    └── test_full_run.py   # Marked slow, skipped in CI by default
```

Round-trip test (critical):
```python
def test_round_trip(resume_fixture):
    ir = parse_latex(resume_fixture)
    output = render_latex(ir)
    ir2 = parse_latex(output)
    assert ir == ir2  # Structural equivalence
```
