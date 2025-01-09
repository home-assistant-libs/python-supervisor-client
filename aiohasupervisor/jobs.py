"""Jobs client for supervisor."""

from uuid import UUID

from .client import _SupervisorComponentClient
from .models.jobs import Job, JobsInfo, JobsOptions


class JobsClient(_SupervisorComponentClient):
    """Handles Jobs access in Supervisor."""

    async def info(self) -> JobsInfo:
        """Get Jobs info."""
        result = await self._client.get("jobs/info")
        return JobsInfo.from_dict(result.data)

    async def set_options(self, options: JobsOptions) -> None:
        """Set Jobs options."""
        await self._client.post("jobs/options", json=options.to_dict())

    async def reset(self) -> None:
        """Reset Jobs options (primarily clears previously ignored job conditions)."""
        await self._client.post("jobs/reset")

    async def get_job(self, job: UUID) -> Job:
        """Get details of a job."""
        result = await self._client.get(f"jobs/{job.hex}")
        return Job.from_dict(result.data)

    async def delete_job(self, job: UUID) -> None:
        """Remove a done job from Supervisor's cache."""
        await self._client.delete(f"jobs/{job.hex}")
