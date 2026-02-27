"""Main CLI entrypoint for ResuForge.

Uses Click for command-line interface. All user-facing output
goes through rich.console — never use print().
"""

from __future__ import annotations

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
    # TODO: Wire up the full pipeline
    # 1. Parse resume -> ResumeIR
    # 2. Parse JD -> JDObject
    # 3. Tailor resume -> TailoringResult
    # 4. If --cover-letter, generate cover letter
    # 5. If --diff, display changes
    # 6. If --dry-run, print and exit
    # 7. Render and write output files
    console.print("[bold red]Not yet implemented.[/bold red] Pipeline coming soon.")


@app.command()
@click.option("--set-key", type=str, help="Set API key")
@click.option("--set-model", type=str, help="Set default model")
def config(set_key: str | None, set_model: str | None) -> None:
    """Manage ResuForge configuration."""
    console.print("[bold red]Not yet implemented.[/bold red]")


@app.command()
@click.option("--add", type=click.Path(exists=True), help="Add a resume profile")
@click.option("--list", "list_profiles", is_flag=True, help="List saved profiles")
@click.option("--use", type=str, help="Set default profile")
def profile(add: str | None, list_profiles: bool, use: str | None) -> None:
    """Manage resume profiles."""
    console.print("[bold red]Not yet implemented.[/bold red]")


if __name__ == "__main__":
    app()
