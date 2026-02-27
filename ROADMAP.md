# Roadmap — ResuForge

## Vision

Build the best open-source resume tailoring tool for technical professionals — starting as a CLI, evolving into a platform.

---

## v0.1.0 — CLI MVP _(in progress — scaffold complete)_

**Goal:** Core pipeline working end-to-end. Useful for personal use and initial open-source release.

### Deliverables

- [x] Project scaffold (pyproject.toml, CI, directory structure)
- [x] IR schema — all Pydantic models (ResumeIR, JDObject, Change, etc.)
- [x] CLI entrypoint with tailor/config/profile subcommands (stubs)
- [x] LLM provider abstraction + prompt templates
- [x] Test framework with smoke tests passing
- [x] README, PRD, Architecture, Contributing docs
- [ ] LaTeX resume parser (.tex to JSON IR)
- [ ] LaTeX renderer (JSON IR to .tex)
- [ ] JD ingestion from `.txt` and `.pdf`
- [ ] Tailoring engine: summary rewrite, skills reorder, bullet rephrase
- [ ] Cover letter generator
- [ ] Wire up full CLI pipeline
- [ ] 3 example resume fixtures and 5 JD fixtures for testing

**Success criteria:** Can tailor a real resume to a real JD in < 30 seconds, output compiles cleanly.

---

## v0.2.0 — Polish & Power Users

**Goal:** Make it production-worthy for daily use.

### Deliverables

- [ ] `--diff` flag with colored terminal output showing changes + reasons
- [ ] `--dry-run` mode
- [ ] URL JD input (scrape + extract)
- [ ] `resuforge profile` subcommand — manage multiple base resumes
- [ ] Batch mode: `--jd-dir` processes a folder of JDs
- [ ] Organized output: `applications/company_name/` folder structure
- [ ] Improved LaTeX parser: support for more template styles
- [ ] Streaming output for long operations
- [ ] Config file at `~/.resuforge/config.yaml`

---

## v0.3.0 — Web UI

**Goal:** Make ResuForge accessible to non-CLI users.

### Deliverables

- [ ] FastAPI backend exposing core pipeline as REST API
- [ ] React frontend: upload resume, paste JD, get tailored output
- [ ] PDF preview in browser
- [ ] Download as `.tex` or compiled `.pdf`
- [ ] Docker compose for self-hosting
- [ ] Optional hosted version (Bring Your Own API Key)

---

## v0.4.0 — Intelligence Layer

**Goal:** Make the tool smarter and more useful over time.

### Deliverables

- [ ] ATS score estimation (keyword match scoring pre/post tailoring)
- [ ] Application tracker: log which JDs you applied to, what version of resume
- [ ] Feedback loop: mark applications as "got interview" / "rejected" to improve tailoring
- [ ] Multi-language resume support (JDs in French, German, etc.)
- [ ] Plugin system: custom section handlers for non-standard resume formats

---

## Future / Community Ideas

- VS Code extension: tailor resume from within editor
- LinkedIn JD input (scrape from job URL)
- Resume scoring rubric based on industry-specific criteria
- Collaborative templates gallery

---

## What We Will NOT Build

- Anything that creates or implies false credentials
- A resume "spinning" tool that makes resumes unreadable to humans
- A SaaS with resume data stored on our servers (privacy-first, always)
