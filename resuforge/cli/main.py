"""Main CLI entrypoint for ResuForge.

Uses Click for command-line interface. All user-facing output
goes through rich.console — never use print().
"""

from __future__ import annotations

from pathlib import Path

import click
from rich.console import Console

from resuforge import __version__

console = Console()


@click.group()
@click.version_option(version=__version__, prog_name="resuforge")
def app() -> None:
    """ResuForge — Surgically tailor your LaTeX resume to any job description."""


@app.command()
@click.option("--resume", required=True, type=click.Path(exists=True), help="Path to .tex resume")
@click.option("--jd", required=True, type=click.Path(exists=True), help="Path to JD file")
@click.option("--output", type=click.Path(), help="Output path for tailored resume")
@click.option("--output-dir", type=click.Path(), help="Output directory for all generated files")
@click.option("--cover-letter", is_flag=True, help="Also generate a cover letter")
@click.option("--diff", is_flag=True, help="Show diff of changes made")
@click.option("--dry-run", is_flag=True, help="Show changes without writing files")
@click.option("--model", type=str, help="LLM model to use")
@click.option("--verbose", is_flag=True, help="Verbose logging")
def tailor(
    resume: str,
    jd: str,
    output: str | None,
    output_dir: str | None,
    cover_letter: bool,
    diff: bool,
    dry_run: bool,
    model: str | None,
    verbose: bool,
) -> None:
    """Tailor a resume to match a job description."""

    _run_tailor_pipeline(
        resume_path=resume,
        jd_path=jd,
        output_path=output,
        output_dir=output_dir,
        cover_letter=cover_letter,
        diff=diff,
        dry_run=dry_run,
        model=model,
        verbose=verbose,
    )


def _run_tailor_pipeline(
    *,
    resume_path: str,
    jd_path: str,
    output_path: str | None,
    output_dir: str | None,
    cover_letter: bool,
    diff: bool,
    dry_run: bool,
    model: str | None,
    verbose: bool,
    llm_override: object | None = None,
) -> None:
    """Execute the full tailoring pipeline.

    Separated from CLI handler for testability.

    Args:
        resume_path: Path to .tex resume file.
        jd_path: Path to JD file.
        output_path: Explicit output file path.
        output_dir: Output directory for generated files.
        cover_letter: Whether to generate a cover letter.
        diff: Whether to display changes.
        dry_run: Whether to skip writing files.
        model: LLM model override.
        verbose: Whether to show verbose output.
        llm_override: Optional LLM provider override (for testing).
    """
    from resuforge.config.settings import load_config
    from resuforge.cover_letter.generator import generate_cover_letter
    from resuforge.ingestion.jd_parser import parse_jd
    from resuforge.llm.base import LLMProvider
    from resuforge.resume.latex_parser import parse_latex
    from resuforge.resume.latex_renderer import render_latex
    from resuforge.tailoring.engine import tailor_resume
    from resuforge.utils.diff import display_changes
    from resuforge.utils.file_utils import write_file

    # Step 1: Parse resume
    with console.status("[bold cyan]Parsing resume..."):
        resume_ir = parse_latex(Path(resume_path))

    if verbose:
        console.print(f"[dim]Parsed {len(resume_ir.experience)} experience entries[/dim]")

    # Step 2: Parse JD
    with console.status("[bold cyan]Parsing job description..."):
        jd_obj = parse_jd(Path(jd_path))

    if verbose:
        console.print(f"[dim]JD: {jd_obj.job_title} at {jd_obj.company}[/dim]")

    # Step 3: Initialize LLM
    if llm_override and isinstance(llm_override, LLMProvider):
        llm = llm_override
    else:
        from resuforge.llm.anthropic_client import AnthropicClient
        from resuforge.llm.exceptions import LLMError

        config = load_config()
        llm_model = model or config.default_model
        try:
            llm = AnthropicClient(model=llm_model)
        except LLMError as exc:
            console.print(f"[bold red]Error:[/bold red] {exc}")
            raise SystemExit(1) from exc

    # Step 4: Tailor resume
    with console.status("[bold cyan]Tailoring resume..."):
        result = tailor_resume(resume_ir, jd_obj, llm=llm)

    console.print(f"[bold green]Done![/bold green] {len(result.changes)} change(s) made.")

    # Step 5: Show diff if requested
    if diff or dry_run:
        display_changes(result.changes)

    # Step 6: If dry-run, stop here
    if dry_run:
        console.print("[dim]Dry run — no files written.[/dim]")
        return

    # Step 7: Render and write output
    rendered = render_latex(result.resume)
    out_path = _resolve_output_path(resume_path, output_path, output_dir, "_tailored.tex")
    write_file(out_path, rendered)
    console.print(f"[bold]Tailored resume written to:[/bold] {out_path}")

    # Step 8: Generate cover letter if requested
    if cover_letter:
        with console.status("[bold cyan]Generating cover letter..."):
            cl_text = generate_cover_letter(result.resume, jd_obj, llm=llm)

        cl_path = _resolve_output_path(resume_path, None, output_dir, "_cover_letter.tex")
        write_file(cl_path, cl_text)
        console.print(f"[bold]Cover letter written to:[/bold] {cl_path}")


def _resolve_output_path(
    input_path: str,
    explicit_output: str | None,
    output_dir: str | None,
    suffix: str,
) -> Path:
    """Determine the output file path.

    Args:
        input_path: Original input file path.
        explicit_output: Explicitly specified output path.
        output_dir: Output directory.
        suffix: Suffix to append (e.g., '_tailored.tex').

    Returns:
        Resolved output Path.
    """
    if explicit_output:
        return Path(explicit_output)

    input_p = Path(input_path)
    stem = input_p.stem
    filename = f"{stem}{suffix}"

    if output_dir:
        return Path(output_dir) / filename

    return input_p.parent / filename


@app.command()
@click.option("--set-key", type=str, help="Set API key")
@click.option("--set-model", type=str, help="Set default model")
def config(set_key: str | None, set_model: str | None) -> None:
    """Manage ResuForge configuration."""
    from resuforge.config.settings import load_config, save_config

    cfg = load_config()

    if set_key:
        console.print(
            "[bold yellow]Note:[/bold yellow] API keys should be set via environment "
            "variables (ANTHROPIC_API_KEY) for security. Not saving to config file."
        )
    elif set_model:
        cfg.default_model = set_model
        save_config(cfg)
        console.print(f"[bold green]Default model set to:[/bold green] {set_model}")
    else:
        console.print("[bold]Current configuration:[/bold]")
        console.print(f"  Provider: {cfg.provider}")
        console.print(f"  Model: {cfg.default_model}")
        console.print(f"  Output format: {cfg.output_format}")
        console.print(f"  Cover letter tone: {cfg.cover_letter_tone}")


@app.command()
@click.option("--add", type=click.Path(exists=True), help="Add a resume profile")
@click.option("--list", "list_profiles", is_flag=True, help="List saved profiles")
@click.option("--use", type=str, help="Set default profile")
def profile(add: str | None, list_profiles: bool, use: str | None) -> None:
    """Manage resume profiles."""
    console.print("[bold red]Not yet implemented.[/bold red] Profile management coming in v0.2.")


if __name__ == "__main__":
    app()
