"""Check responses recorded by Supervisor's tests can be parsed by this client.

Supervisor CI runs this from a checkout of this repo at the client version under
test, with that version installed:

    python tests/compat/check_responses.py <records-dir> [--coverage SCOPE]
        [--format FORMAT]

Records are read from every ``*.jsonl`` file in ``<records-dir>``, one JSON object
per line, as written by Supervisor's API test recorder:

    {"method": "GET", "template": "/mounts/{mount}/reload", "params": ["test"],
     "status": 200, "body": {...}, "test": "tests/api/test_mounts.py::test_x"}

``template`` is the request path with each route parameter replaced by ``{name}``,
``params`` holds the actual values in template order and ``test`` is the id of the
Supervisor test that produced the response.

Each unique response is checked as follows:

- Envelope: every body must parse as a ``Response``. Error responses with an
  ``error_key`` unknown to this client are reported as warnings.
- Model: successful v1 responses to an endpoint in ``endpoints.ENDPOINTS`` are
  served to the client method that calls it, which must not raise.
- Coverage, off by default: with ``--coverage client`` recorded GET endpoints the
  client lacks, other than ``endpoints.OMITTED``, are reported as warnings, with
  ``--coverage supervisor`` client endpoints no recording covers are,
  ``--coverage all`` reports both.

Exits non-zero on any failure. Issues are written as GitHub annotations when run
in GitHub Actions and as plain text otherwise, ``--format`` forces either.
"""

from __future__ import annotations

import argparse
import asyncio
from dataclasses import dataclass, field
from enum import StrEnum
from fnmatch import fnmatchcase
import json
import os
from pathlib import Path
import re
import sys
from typing import TYPE_CHECKING, Any

from aiohttp import ClientSession, web
from aiohttp.test_utils import TestServer

from aiohasupervisor import SupervisorClient
from aiohasupervisor.exceptions import ERROR_KEYS
from aiohasupervisor.models.base import Response, ResultType

if __package__:
    from .endpoints import ENDPOINTS, OMITTED, Endpoint
else:  # Run as a script, its directory is on sys.path
    from endpoints import ENDPOINTS, OMITTED, Endpoint

if TYPE_CHECKING:
    from collections.abc import Iterable

CALL_TIMEOUT = 10

_PARAM_RE = re.compile(r"\{[^}]*\}")
_TEST_PHASE_RE = re.compile(r" \((setup|call|teardown)\)$")


def normalize(template: str) -> str:
    """Normalize a path template so client and Supervisor templates compare."""
    return _PARAM_RE.sub("*", template.lstrip("/"))


def is_v2(template: str) -> bool:
    """Return true if template is for the v2 API."""
    return normalize(template).startswith("v2/")


def is_omitted(template: str) -> bool:
    """Return true if the client intentionally omits the endpoint."""
    return any(fnmatchcase(normalize(template), pattern) for pattern in OMITTED)


class Coverage(StrEnum):
    """Which coverage gaps to report."""

    NONE = "none"
    # Supervisor endpoints the client lacks
    CLIENT = "client"
    # Client endpoints Supervisor's tests do not cover
    SUPERVISOR = "supervisor"
    ALL = "all"


class OutputFormat(StrEnum):
    """How to write issues."""

    # GitHub annotations in GitHub Actions, text otherwise
    AUTO = "auto"
    GITHUB = "github"
    TEXT = "text"


@dataclass(frozen=True)
class Record:
    """Response recorded by a Supervisor test."""

    method: str
    template: str
    params: list[str]
    status: int
    body: Any
    test: str

    @property
    def key(self) -> tuple[str, str]:
        """Key to match against endpoints."""
        return (self.method.upper(), normalize(self.template))

    @property
    def test_file(self) -> str:
        """File of the test that produced the response."""
        return self.test.split("::", 1)[0]

    @property
    def is_success(self) -> bool:
        """Return true if response status is successful."""
        return 200 <= self.status < 300

    def describe(self) -> str:
        """Describe the request for messages."""
        return f"{self.method.upper()} /{self.template.lstrip('/')}"


@dataclass(frozen=True)
class Issue:
    """Failure or warning found by the check."""

    message: str
    file: str | None = None


@dataclass
class Report:
    """Result of checking recorded responses."""

    checked: int = 0
    replayed: int = 0
    failures: list[Issue] = field(default_factory=list)
    warnings: list[Issue] = field(default_factory=list)


def load_records(records_dir: Path) -> list[Record]:
    """Load records from all JSONL files in directory, without duplicates."""
    records: dict[tuple[str, str, int, str], Record] = {}
    for path in sorted(records_dir.glob("*.jsonl")):
        with path.open(encoding="utf-8") as file:
            for line_no, line in enumerate(file, start=1):
                if not line.strip():
                    continue
                try:
                    raw = json.loads(line)
                    record = Record(
                        method=raw["method"],
                        template=raw["template"],
                        params=[str(param) for param in raw.get("params", [])],
                        status=int(raw["status"]),
                        body=raw["body"],
                        test=_TEST_PHASE_RE.sub("", raw.get("test", "")),
                    )
                except (ValueError, KeyError, TypeError) as err:
                    msg = f"{path}:{line_no}: invalid record: {err}"
                    raise ValueError(msg) from err
                key = (
                    record.method.upper(),
                    record.template,
                    record.status,
                    json.dumps(record.body, sort_keys=True),
                )
                records.setdefault(key, record)
    return list(records.values())


class ReplayServer:
    """Serves the recorded response for the record being checked."""

    def __init__(self) -> None:
        """Initialize server."""
        self.record: Record | None = None
        self.app = web.Application()
        self.app.router.add_route("*", "/{tail:.*}", self._handle)

    async def _handle(self, _request: web.Request) -> web.Response:
        """Return recorded response."""
        if self.record is None:
            return web.Response(status=500)
        return web.Response(
            status=self.record.status,
            text=json.dumps(self.record.body),
            content_type="application/json",
        )


def _check_envelope(
    record: Record, report: Report, unknown_keys: set[str]
) -> Issue | None:
    """Check record body parses as a response envelope, warn on unknown errors."""
    try:
        response = Response.from_dict(record.body)
    except Exception as err:  # noqa: BLE001
        return Issue(
            f"{record.describe()}: response envelope does not parse: "
            f"{type(err).__name__}: {err} (from {record.test})",
            record.test_file,
        )

    if (
        response.result == ResultType.ERROR
        and response.error_key
        and response.error_key not in ERROR_KEYS
        and response.error_key not in unknown_keys
    ):
        unknown_keys.add(response.error_key)
        report.warnings.append(
            Issue(
                f"{record.describe()}: error_key {response.error_key} is unknown to "
                f"the client (from {record.test})",
                record.test_file,
            )
        )
    return None


async def _check_model(
    record: Record, endpoint: Endpoint, client: SupervisorClient
) -> Issue | None:
    """Replay record through the client method for its endpoint."""
    try:
        async with asyncio.timeout(CALL_TIMEOUT):
            await endpoint.call(client, record.params)
    except Exception as err:  # noqa: BLE001
        return Issue(
            f"{record.describe()}: client cannot parse response: "
            f"{type(err).__name__}: {err} (from {record.test})",
            record.test_file,
        )
    return None


def _check_coverage(
    records: Iterable[Record], report: Report, coverage: Coverage
) -> None:
    """Warn about endpoints only one side knows about."""
    recorded: dict[tuple[str, str], Record] = {}
    for record in records:
        if record.is_success and not is_v2(record.template):
            recorded.setdefault(record.key, record)

    if coverage in (Coverage.CLIENT, Coverage.ALL):
        endpoints = {(ep.method, normalize(ep.template)) for ep in ENDPOINTS}
        report.warnings.extend(
            Issue(
                f"{record.describe()}: Supervisor endpoint has no client method "
                f"(from {record.test})",
                record.test_file,
            )
            for key, record in sorted(recorded.items())
            if key[0] == "GET"
            and key not in endpoints
            and not is_omitted(record.template)
        )

    if coverage in (Coverage.SUPERVISOR, Coverage.ALL):
        report.warnings.extend(
            Issue(
                f"{ep.method} /{ep.template}: client endpoint has no successful "
                "response recorded by Supervisor's tests"
            )
            for ep in ENDPOINTS
            if (ep.method, normalize(ep.template)) not in recorded
        )


async def check(records: list[Record], *, coverage: Coverage = Coverage.NONE) -> Report:
    """Check recorded responses against the client."""
    endpoints = {(ep.method, normalize(ep.template)): ep for ep in ENDPOINTS}
    report = Report(checked=len(records))
    unknown_keys: set[str] = set()

    server = ReplayServer()
    async with (
        TestServer(server.app) as test_server,
        ClientSession() as session,
    ):
        client = SupervisorClient(
            str(test_server.make_url("")).rstrip("/"), "compat", session
        )
        for record in records:
            if issue := _check_envelope(record, report, unknown_keys):
                report.failures.append(issue)
                continue
            if not record.is_success or is_v2(record.template):
                continue
            if not (endpoint := endpoints.get(record.key)):
                continue

            server.record = record
            report.replayed += 1
            if issue := await _check_model(record, endpoint, client):
                report.failures.append(issue)

    if coverage != Coverage.NONE:
        _check_coverage(records, report, coverage)
    return report


def _escape(value: str) -> str:
    """Escape a value for a GitHub workflow command."""
    return value.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")


def _resolve_format(output_format: OutputFormat) -> OutputFormat:
    """Resolve auto output format from the environment."""
    if output_format != OutputFormat.AUTO:
        return output_format
    if os.environ.get("GITHUB_ACTIONS") == "true":
        return OutputFormat.GITHUB
    return OutputFormat.TEXT


def _emit(level: str, issue: Issue, output_format: OutputFormat) -> None:
    """Write an issue in the output format."""
    if output_format == OutputFormat.GITHUB:
        props = ""
        if issue.file:
            file = _escape(issue.file).replace(":", "%3A").replace(",", "%2C")
            props = f" file={file}"
        sys.stdout.write(f"::{level}{props}::{_escape(issue.message)}\n")
    else:
        sys.stdout.write(f"{level.upper()}: {issue.message}\n")


def main(argv: list[str] | None = None) -> int:
    """Run the check."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "records_dir", type=Path, help="Directory of JSONL records from Supervisor"
    )
    parser.add_argument(
        "--coverage",
        type=Coverage,
        choices=list(Coverage),
        default=Coverage.NONE,
        help=(
            "Warn about coverage gaps: Supervisor endpoints the client lacks "
            "(client), client endpoints Supervisor's tests do not cover "
            "(supervisor) or both (all). Default: none"
        ),
    )
    parser.add_argument(
        "--format",
        type=OutputFormat,
        choices=list(OutputFormat),
        default=OutputFormat.AUTO,
        help=(
            "Write issues as GitHub annotations (github) or plain text (text). "
            "Default: auto, github when run in GitHub Actions"
        ),
    )
    args = parser.parse_args(argv)

    try:
        records = load_records(args.records_dir)
    except (OSError, ValueError) as err:
        sys.stderr.write(f"{err}\n")
        return 2

    output_format = _resolve_format(args.format)
    report = asyncio.run(check(records, coverage=args.coverage))
    for issue in report.failures:
        _emit("error", issue, output_format)
    for issue in report.warnings:
        _emit("warning", issue, output_format)
    sys.stdout.write(
        f"Checked {report.checked} responses, {report.replayed} replayed through "
        f"the client: {len(report.failures)} failures, "
        f"{len(report.warnings)} warnings\n"
    )
    return 1 if report.failures else 0


if __name__ == "__main__":
    sys.exit(main())
