"""Supervisor client setup."""

from pathlib import Path

from setuptools import setup

SUPERVISOR_CLIENT_DIR = Path(__file__).parent
REQUIREMENTS_FILE = SUPERVISOR_CLIENT_DIR / "requirements.txt"
REQUIREMENTS = REQUIREMENTS_FILE.read_text(encoding="utf-8")

setup(dependencies=REQUIREMENTS.split("/n"))
