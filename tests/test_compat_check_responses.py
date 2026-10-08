"""Test the compat checker for recorded Supervisor responses."""

import json
from pathlib import Path
from typing import Any

import pytest

from . import load_fixture
from .compat import check_responses
from .compat.check_responses import (
    Coverage,
    Issue,
    Record,
    check,
    load_records,
    main,
)
from .compat.endpoints import ENDPOINTS

TEST_ID = "tests/api/test_mounts.py::test_api_mounts_info"
BAD_MOUNTS = {"result": "ok", "data": {"mounts": "invalid"}}


def make_record(
    template: str = "/mounts",
    body: Any = None,
    *,
    method: str = "GET",
    params: list[str] | None = None,
    status: int = 200,
    test: str = TEST_ID,
) -> dict[str, Any]:
    """Make a raw record as Supervisor's recorder writes it."""
    return {
        "method": method,
        "template": template,
        "params": params or [],
        "status": status,
        "body": json.loads(load_fixture("mounts_info.json")) if body is None else body,
        "test": test,
    }


def to_record(raw: dict[str, Any]) -> Record:
    """Convert a raw record to a Record."""
    return Record(**raw)


def write_records(path: Path, *records: dict[str, Any]) -> Path:
    """Write records to a JSONL file in path."""
    path.mkdir(exist_ok=True)
    with (path / "gw0.jsonl").open("a", encoding="utf-8") as file:
        file.writelines(json.dumps(record) + "\n" for record in records)
    return path


def messages(issues: list[Issue]) -> list[str]:
    """Return issue messages."""
    return [issue.message for issue in issues]


async def test_valid_response() -> None:
    """Test a response the client parses passes."""
    report = await check([to_record(make_record())])

    assert report.checked == 1
    assert report.replayed == 1
    assert report.failures == []


async def test_valid_response_with_params() -> None:
    """Test params from the record are passed to the client method."""
    record = make_record(
        "/addons/{addon}/info",
        json.loads(load_fixture("addons_info.json")),
        params=["core_ssh"],
    )
    report = await check([to_record(record)])

    assert report.replayed == 1
    assert report.failures == []


async def test_model_failure() -> None:
    """Test a response the client cannot parse fails naming the test."""
    report = await check([to_record(make_record(body=BAD_MOUNTS))])

    assert report.replayed == 1
    assert len(report.failures) == 1
    failure = report.failures[0]
    assert failure.message.startswith("GET /mounts: client cannot parse response")
    assert failure.message.endswith(f"(from {TEST_ID})")
    assert failure.file == "tests/api/test_mounts.py"


async def test_envelope_failure() -> None:
    """Test any response not matching the response envelope fails."""
    record = make_record(
        "/unknown", {"data": {}}, method="POST", status=400, test="tests/a.py::test"
    )
    report = await check([to_record(record)])

    assert report.replayed == 0
    assert messages(report.failures) == [
        (
            "POST /unknown: response envelope does not parse: MissingField: Field "
            '"result" of type ResultType is missing in Response instance '
            "(from tests/a.py::test)"
        )
    ]


async def test_error_responses_not_replayed() -> None:
    """Test error responses are only checked for the envelope."""
    body = {"result": "error", "message": "Boom", "error_key": "unknown_error"}
    report = await check([to_record(make_record(body=body, status=400))])

    assert report.replayed == 0
    assert report.failures == []


async def test_unknown_error_key() -> None:
    """Test an error key unknown to the client is a warning, once."""
    body = {"result": "error", "message": "Boom", "error_key": "brand_new_error"}
    records = [
        to_record(make_record(body=body, status=400)),
        to_record(make_record("/info", body=body, status=400)),
    ]
    report = await check(records)

    assert report.failures == []
    assert [m for m in messages(report.warnings) if "error_key" in m] == [
        (
            "GET /mounts: error_key brand_new_error is unknown to the client "
            f"(from {TEST_ID})"
        )
    ]


async def test_v2_not_replayed() -> None:
    """Test v2 responses are only checked for the envelope."""
    report = await check([to_record(make_record("/v2/mounts", BAD_MOUNTS))])

    assert report.replayed == 0
    assert report.failures == []
    assert not [m for m in messages(report.warnings) if "v2" in m]


async def test_no_coverage_warnings_by_default() -> None:
    """Test endpoints only known to one side are not reported by default."""
    records = [to_record(make_record("/new/{thing}/info", params=["a"]))]
    report = await check(records)

    assert report.failures == []
    assert report.warnings == []


CLIENT_GAP = "Supervisor endpoint has no client method"
SUPERVISOR_GAP = "client endpoint has no successful response recorded"


@pytest.mark.parametrize(
    ("coverage", "client_gaps", "supervisor_gaps"),
    [
        (Coverage.NONE, 0, 0),
        (Coverage.CLIENT, 1, 0),
        (Coverage.SUPERVISOR, 0, len(ENDPOINTS) - 1),
        (Coverage.ALL, 1, len(ENDPOINTS) - 1),
    ],
)
async def test_coverage_warnings(
    coverage: Coverage, client_gaps: int, supervisor_gaps: int
) -> None:
    """Test endpoints only known to one side are warnings for the chosen scope."""
    records = [
        to_record(make_record()),
        to_record(make_record("/new/{thing}/info", params=["a"])),
        to_record(make_record("/new/thing", method="POST")),
        to_record(make_record("/missing/route", status=404)),
        to_record(make_record("/host/logs/identifiers")),
        to_record(make_record("/store/addons/{app}/icon", params=["a"])),
        to_record(make_record("/ingress/{token}/{path}", params=["a", "b"])),
    ]
    report = await check(records, coverage=coverage)

    warnings = messages(report.warnings)
    assert [w for w in warnings if CLIENT_GAP in w] == [
        f"GET /new/{{thing}}/info: {CLIENT_GAP} (from {TEST_ID})"
    ] * client_gaps
    unrecorded = [w for w in warnings if SUPERVISOR_GAP in w]
    assert len(unrecorded) == supervisor_gaps
    assert not [w for w in unrecorded if w.startswith("GET /mounts:")]
    assert len(warnings) == client_gaps + supervisor_gaps


def test_load_records_dedupes(tmp_path: Path) -> None:
    """Test identical responses from different tests are checked once."""
    write_records(
        tmp_path,
        make_record(test=f"{TEST_ID} (call)"),
        make_record(test="tests/api/test_mounts.py::test_other (call)"),
        make_record(status=201),
    )
    (tmp_path / "gw1.jsonl").write_text(
        json.dumps(make_record(body=BAD_MOUNTS)) + "\n\n", encoding="utf-8"
    )
    (tmp_path / "ignored.json").write_text("not records", encoding="utf-8")

    records = load_records(tmp_path)

    assert [(r.status, r.test) for r in records] == [
        (200, TEST_ID),
        (201, TEST_ID),
        (200, TEST_ID),
    ]


def test_main_pass(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Test main exits zero when all responses parse."""
    write_records(tmp_path, make_record())

    assert main([str(tmp_path)]) == 0
    out = capsys.readouterr().out
    assert "ERROR" not in out
    assert out.splitlines()[-1].startswith(
        "Checked 1 responses, 1 replayed through the client"
    )


def test_main_fail(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test main exits non-zero with GitHub annotations on failure."""
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    write_records(tmp_path, make_record(body=BAD_MOUNTS))

    assert main([str(tmp_path)]) == 1
    lines = capsys.readouterr().out.splitlines()
    assert lines[0].startswith(
        "::error file=tests/api/test_mounts.py::GET /mounts: client cannot parse"
    )
    assert lines[-1].endswith("the client: 1 failures, 0 warnings")


MAIN_CLIENT_GAP = f"WARNING: GET /new/thing: {CLIENT_GAP} (from {TEST_ID})"
MAIN_SUPERVISOR_GAP = f"WARNING: GET /info: {SUPERVISOR_GAP} by Supervisor's tests"


@pytest.mark.parametrize(
    ("coverage", "expected"),
    [
        ("none", []),
        ("client", [MAIN_CLIENT_GAP]),
        ("supervisor", [MAIN_SUPERVISOR_GAP]),
        ("all", [MAIN_CLIENT_GAP, MAIN_SUPERVISOR_GAP]),
    ],
)
def test_main_coverage(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    coverage: str,
    expected: list[str],
) -> None:
    """Test main reports coverage warnings for the chosen scope, without failing."""
    monkeypatch.setattr(
        check_responses,
        "ENDPOINTS",
        [ep for ep in ENDPOINTS if ep.template in ("mounts", "info")],
    )
    write_records(tmp_path, make_record(), make_record("/new/thing"))

    assert main([str(tmp_path), "--coverage", coverage]) == 0
    lines = capsys.readouterr().out.splitlines()
    assert lines[:-1] == expected
    assert lines[-1].endswith(f"0 failures, {len(expected)} warnings")


def test_main_invalid_coverage(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Test main rejects an unknown coverage scope."""
    with pytest.raises(SystemExit) as exc_info:
        main([str(tmp_path), "--coverage", "everything"])
    assert exc_info.value.code == 2
    assert "argument --coverage" in capsys.readouterr().err


@pytest.mark.parametrize("records", ["not json\n", '{"method": "GET"}\n'])
def test_main_invalid_records(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], records: str
) -> None:
    """Test main exits with usage error on invalid records."""
    (tmp_path / "gw0.jsonl").write_text(records, encoding="utf-8")

    assert main([str(tmp_path)]) == 2
    assert capsys.readouterr().err
