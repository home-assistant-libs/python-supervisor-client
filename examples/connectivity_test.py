"""Simple connectivity test."""

import asyncio
import json
import os
from typing import final

from aiohasupervisor import SupervisorClient
from aiohasupervisor.models import RootInfo

SUPERVISOR_API_URL: final = os.environ.get("SUPERVISOR_API_URL")
SUPERVISOR_TOKEN: final = os.environ.get("SUPERVISOR_TOKEN")

if not SUPERVISOR_API_URL:
    raise RuntimeError("SUPERVISOR_API_URL env must be set")
if not SUPERVISOR_TOKEN:
    raise RuntimeError("SUPERVISOR_TOKEN env must be set")

client = SupervisorClient(SUPERVISOR_API_URL, SUPERVISOR_TOKEN)


async def get_info() -> RootInfo:
    """Get root info."""
    async with client:
        return await client.info()


info = asyncio.run(get_info())
print(json.dumps(info.to_dict(), indent=4))  # noqa: T201
