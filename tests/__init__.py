"""Tests for aiohasupervisor."""

from pathlib import Path


def get_fixture_path(filename: str) -> Path:
    """Get fixture path."""
    return Path(__package__) / "fixtures" / filename


def load_fixture(filename: str) -> str:
    """Load a fixture."""
    fixture = get_fixture_path(filename)
    return fixture.read_text(encoding="utf-8")
