"""Tests for aiosupervisor."""

from pathlib import Path


def load_fixture(filename: str) -> str:
    """Load a fixture."""
    fixture = Path(__package__) / "fixtures" / filename
    return fixture.read_text(encoding="utf-8")
