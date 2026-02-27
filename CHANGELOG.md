# Changelog

All notable changes to ResuForge will be documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

### Added

- Complete project scaffold with 8 subpackages (cli, ingestion, resume, tailoring, cover_letter, llm, config, utils)
- Pydantic v2 IR schema with all data models: `ResumeIR`, `JDObject`, `GapAnalysis`, `Change`, `TailoringResult`
- Click CLI entrypoint with `tailor`, `config`, and `profile` subcommands (stubs)
- LLM provider abstraction (`LLMProvider` base class) with Anthropic and OpenAI client stubs
- All tailoring and cover letter prompt templates
- Config management module with `ResuForgeConfig` model
- Utility modules for file operations and diff display
- pytest framework with 4 passing smoke tests and shared fixtures
- GitHub Actions CI pipeline (lint + test + type-check across Python 3.10-3.12)
- `pyproject.toml` (PEP 621 standard format with setuptools)
- PRD, Architecture, Roadmap, and Contributing documentation

---

## [0.1.0] — In Development

### Planned

- JD ingestion from `.txt` and `.pdf` files
- LaTeX resume parser supporting moderncv, altacv, and article-based templates
- LaTeX renderer: IR to valid `.tex`
- Tailoring engine: summary rewrite, skills reorder, bullet rephrasing
- Grounded cover letter generator
- CLI: fully wired `resuforge tailor` pipeline
- Example resume fixtures and JD fixtures for testing
