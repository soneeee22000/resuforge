# Contributing to ResuForge

Thank you for considering contributing! ResuForge is open-source and built collaboratively.

---

## Ways to Contribute

- **Add LaTeX template support** — The parser currently handles 3 templates. Adding more is the highest-value contribution right now.
- **Add JD fixtures** — More real-world JDs make the test suite stronger.
- **Improve prompts** — Better tailoring results through prompt engineering.
- **Bug reports** — Especially LaTeX parse failures on real resumes.
- **Documentation** — Tutorials, usage examples, video walkthroughs.

---

## Getting Started

```bash
git clone https://github.com/soneeee22000/resuforge
cd resuforge
pip install -e ".[dev]"
cp .env.example .env  # Add your API key
pytest tests/unit/    # Run fast tests
```

---

## Development Guidelines

### Code Style

- Black for formatting (`black .`)
- Ruff for linting (`ruff check .`)
- Type hints everywhere — Pydantic models for all data structures
- No inline prompts — all prompts go in `prompts.py` files

### Commit Convention

```
feat: add URL JD ingestion
fix: handle custom LaTeX commands in parser
test: add round-trip test for moderncv template
docs: update architecture for v0.2
```

### PR Guidelines

- One feature or fix per PR
- Include tests for new functionality
- Update relevant docs if changing behavior
- Add a sample JD/resume fixture if adding template support

---

## Adding a New LaTeX Template

1. Add a sample `.tex` file to `tests/fixtures/resumes/`
2. Add a template detector in `resume/latex_parser.py` (look for identifying document class or commands)
3. Add a Jinja2 render template in `resume/templates/`
4. Add a round-trip test in `tests/unit/test_latex_parser.py`
5. Document the template in `docs/supported_templates.md`

---

## Code of Conduct

Be kind, be constructive. No harassment, no gatekeeping. Everyone is learning.
