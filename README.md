# ResuForge 🔨

> Surgically tailor your LaTeX resume to any job description — in seconds.

ResuForge is an open-source CLI tool that ingests a job description and your LaTeX resume, makes **targeted, intelligent edits** to fit the role, and generates a **grounded cover letter** — all without hallucinating fake experience.

Built for engineers, researchers, and anyone who uses LaTeX and is tired of manually tweaking their resume for every application.

---

## Why ResuForge?

- **LaTeX-native** — works directly with your `.tex` files, preserves formatting
- **Surgical edits** — rewrites only what's relevant, doesn't touch your whole resume
- **Grounded cover letters** — only uses facts from your actual resume, no fabrication
- **CLI-first** — fast, scriptable, no SaaS lock-in
- **Open source** — own your data, extend the tool, contribute back

---

## Quickstart

> **Note:** ResuForge is in active development. The pipeline modules are being implemented. The quickstart below reflects the target v0.1 CLI.

```bash
# Install from source
pip install -e ".[dev]"

# Tailor your resume to a JD
resuforge tailor --resume my_resume.tex --jd job_description.txt --output tailored_resume.tex

# Also generate a cover letter
resuforge tailor --resume my_resume.tex --jd job_description.txt --cover-letter --output-dir ./applications/company_name/
```

---

## Features

| Feature                               | Status             |
| ------------------------------------- | ------------------ |
| Project scaffold + IR schema          | Done               |
| JD ingestion (text / PDF)             | In Progress (v0.1) |
| LaTeX resume parsing                  | In Progress (v0.1) |
| Keyword & skill extraction from JD    | In Progress (v0.1) |
| Targeted resume section editing       | In Progress (v0.1) |
| Grounded cover letter generation      | In Progress (v0.1) |
| Diff view (original vs tailored)      | Planned (v0.2)     |
| Profile management (multiple resumes) | Planned (v0.2)     |
| Web UI                                | Planned (v0.3)     |
| ATS score estimation                  | Planned (v0.4)     |

---

## Installation

### Requirements

- Python 3.10+
- An Anthropic or OpenAI API key (configurable)

```bash
# Install from source
git clone https://github.com/soneeee22000/resuforge
cd resuforge
pip install -e ".[dev]"

# Set your API key
export ANTHROPIC_API_KEY=your_key_here
# or
export OPENAI_API_KEY=your_key_here
```

---

## How It Works

```
JD Input ──────────────────────────────────────────────┐
                                                        ▼
Resume (.tex) ──► LaTeX Parser ──► JSON IR ──► LLM Pipeline ──► Modified JSON IR ──► LaTeX Renderer ──► Output (.tex)
                                                        │
                                                        └──► Cover Letter Generator ──► cover_letter.tex
```

1. **Parse** your `.tex` resume into a structured JSON intermediate representation (IR)
2. **Extract** skills, keywords, and requirements from the JD
3. **Diff** the JD requirements against your resume's content semantically
4. **Edit** only the relevant sections (summary, skills, bullet points) to highlight alignment
5. **Render** back to clean, compilable LaTeX
6. **Generate** a cover letter using only verified facts from your resume

---

## CLI Reference

```bash
resuforge tailor [OPTIONS]
  --resume      PATH    Path to your .tex resume file (required)
  --jd          PATH    Path to JD file (.txt, .pdf) or URL (required)
  --output      PATH    Output path for tailored resume
  --output-dir  PATH    Output directory (for resume + cover letter)
  --cover-letter        Generate a cover letter alongside the resume
  --diff                Show a diff of changes made
  --dry-run             Show what would change without writing files
  --model       STR     LLM to use (default: claude-3-5-sonnet)
  --verbose             Verbose logging

resuforge profile [OPTIONS]
  --add         PATH    Add a resume to your profile store
  --list                List saved profiles
  --use         NAME    Set a default resume profile

resuforge config
  --set-key     STR     Set API key
  --set-model   STR     Set default model
```

---

## Configuration

ResuForge stores config in `~/.resuforge/config.yaml`:

```yaml
default_model: claude-3-5-sonnet-20241022
provider: anthropic
default_resume: ~/.resuforge/profiles/main.tex
output_format: tex # tex | pdf (pdf requires latexmk)
cover_letter_tone: professional # professional | conversational
```

---

## Contributing

We welcome contributions! See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

---

## Roadmap

See [ROADMAP.md](./ROADMAP.md) for the full roadmap.

---

## License

MIT — use it, fork it, build on it.

---

## Acknowledgements

Built with Claude (Anthropic). Inspired by every engineer who has spent 2 hours tweaking bullet points for a job they didn't get.
