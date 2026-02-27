"""Diff display utilities — colored terminal output showing changes."""

from __future__ import annotations

from resuforge.resume.ir_schema import Change


def display_changes(changes: list[Change]) -> None:
    """Display a list of changes in a readable, colored format.

    Args:
        changes: List of Change objects from the tailoring engine.
    """
    # TODO: Implement using rich
    # Show section, original -> modified, reason
    raise NotImplementedError("Diff display not yet implemented")
