"""Test jobs supervisor client."""

from datetime import datetime
from uuid import UUID

from aioresponses import aioresponses
from yarl import URL

from aiohasupervisor import SupervisorClient
from aiohasupervisor.models import JobCondition, JobsOptions

from . import load_fixture
from .const import SUPERVISOR_URL


async def test_jobs_info(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test jobs info API."""
    responses.get(
        f"{SUPERVISOR_URL}/jobs/info", status=200, body=load_fixture("jobs_info.json")
    )
    info = await supervisor_client.jobs.info()
    assert info.ignore_conditions == [JobCondition.FREE_SPACE]

    assert info.jobs[0].name == "backup_manager_partial_backup"
    assert info.jobs[0].reference == "89cafa67"
    assert info.jobs[0].uuid.hex == "2febe59311f94d6ba36f6f9f73357ca8"
    assert info.jobs[0].progress == 0
    assert info.jobs[0].stage == "finishing_file"
    assert info.jobs[0].done is True
    assert info.jobs[0].errors == []
    assert info.jobs[0].created == datetime.fromisoformat(
        "2025-01-30T20:55:12.859349+00:00"
    )
    assert info.jobs[0].child_jobs[0].name == "backup_store_folders"
    assert info.jobs[0].child_jobs[0].child_jobs[0].name == "backup_folder_save"
    assert info.jobs[0].child_jobs[0].child_jobs[0].reference == "ssl"
    assert info.jobs[0].child_jobs[0].child_jobs[0].child_jobs == []

    assert info.jobs[1].name == "backup_manager_partial_restore"
    assert info.jobs[1].reference == "cfddca18"
    assert info.jobs[1].errors[0].type == "BackupInvalidError"
    assert info.jobs[1].errors[0].message == "Invalid password for backup cfddca18"


async def test_jobs_set_options(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test jobs set options API."""
    responses.post(f"{SUPERVISOR_URL}/jobs/options", status=200)
    assert (
        await supervisor_client.jobs.set_options(
            JobsOptions(ignore_conditions=[JobCondition.FREE_SPACE])
        )
        is None
    )
    assert responses.requests.keys() == {
        ("POST", URL(f"{SUPERVISOR_URL}/jobs/options"))
    }


async def test_jobs_reset(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test jobs reset API."""
    responses.post(f"{SUPERVISOR_URL}/jobs/reset", status=200)
    assert await supervisor_client.jobs.reset() is None
    assert responses.requests.keys() == {("POST", URL(f"{SUPERVISOR_URL}/jobs/reset"))}


async def test_jobs_get_job(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test jobs get job API."""
    responses.get(
        f"{SUPERVISOR_URL}/jobs/2febe59311f94d6ba36f6f9f73357ca8",
        status=200,
        body=load_fixture("jobs_get_job.json"),
    )
    info = await supervisor_client.jobs.get_job(
        UUID("2febe59311f94d6ba36f6f9f73357ca8")
    )

    assert info.name == "backup_manager_partial_backup"
    assert info.reference == "89cafa67"
    assert info.uuid.hex == "2febe59311f94d6ba36f6f9f73357ca8"
    assert info.progress == 0
    assert info.stage == "finishing_file"
    assert info.done is True
    assert info.errors == []
    assert info.created == datetime.fromisoformat("2025-01-30T20:55:12.859349+00:00")
    assert info.child_jobs[0].name == "backup_store_folders"
    assert info.child_jobs[0].child_jobs[0].name == "backup_folder_save"
    assert info.child_jobs[0].child_jobs[0].reference == "ssl"
    assert info.child_jobs[0].child_jobs[0].child_jobs == []


async def test_jobs_delete_job(
    responses: aioresponses, supervisor_client: SupervisorClient
) -> None:
    """Test jobs delete job API."""
    responses.delete(
        f"{SUPERVISOR_URL}/jobs/2febe59311f94d6ba36f6f9f73357ca8", status=200
    )
    assert (
        await supervisor_client.jobs.delete_job(
            UUID("2febe59311f94d6ba36f6f9f73357ca8")
        )
        is None
    )
    assert responses.requests.keys() == {
        ("DELETE", URL(f"{SUPERVISOR_URL}/jobs/2febe59311f94d6ba36f6f9f73357ca8"))
    }
