# Changelog

All notable changes to ResuForge will be documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

### Added
- Initial project scaffold
- PRD, Architecture, and Roadmap documentation
- `pyproject.toml` with full dependency spec
- `CLAUDE.md` for Claude Code instructions

---

## [0.1.0] — TBD

### Added
- JD ingestion from `.txt` and `.pdf` files
- LaTeX resume parser supporting moderncv, altacv, and article-based templates
- JSON Intermediate Representation (IR) for resumes
- Tailoring engine: summary rewrite, skills reorder, bullet rephrasing
- LaTeX renderer: IR → valid `.tex`
- Grounded cover letter generator
- CLI: `resuforge tailor` command
- CLI: `resuforge config` command
- Example resume fixtures and JD fixtures for testing
