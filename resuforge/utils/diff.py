"""Diff display utilities — colored terminal output showing changes."""

from __future__ import annotations

from rich.console import Console
from rich.table import Table

from resuforge.resume.ir_schema import Change

console = Console()


def display_changes(changes: list[Change]) -> None:
    """Display a list of changes in a readable, colored table format.

    Args:
        changes: List of Change objects from the tailoring engine.
    """
    if not changes:
        console.print("[dim]No changes were made.[/dim]")
        return

    table = Table(title="Tailoring Changes", show_lines=True)
    table.add_column("Section", style="cyan", width=12)
    table.add_column("Original", style="red")
    table.add_column("Modified", style="green")
    table.add_column("Reason", style="yellow", width=30)

    for change in changes:
        table.add_row(
            change.section,
            change.original,
            change.modified,
            change.reason,
        )

    console.print(table)
    console.print(f"\n[bold]{len(changes)} change(s) made.[/bold]")


def format_changes_text(changes: list[Change]) -> str:
    """Format changes as plain text (for non-terminal output).

    Args:
        changes: List of Change objects.

    Returns:
        Formatted text representation.
    """
    if not changes:
        return "No changes were made."

    lines: list[str] = [f"{len(changes)} change(s):"]
    for i, change in enumerate(changes, 1):
        lines.append(f"\n{i}. [{change.section}]")
        lines.append(f"   - {change.original}")
        lines.append(f"   + {change.modified}")
        lines.append(f"   Reason: {change.reason}")

    return "\n".join(lines)
