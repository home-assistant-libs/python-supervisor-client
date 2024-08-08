"""Simple connectivity test."""

import asyncio
import json
import os
from typing import final

from aiosupervisor import SupervisorClient
from aiosupervisor.models import RootInfo

SUPERVISOR_API_HOST: final = os.environ.get("SUPERVISOR_API_HOST")
SUPERVISOR_TOKEN: final = os.environ.get("SUPERVISOR_TOKEN")

if not SUPERVISOR_API_HOST:
    raise RuntimeError("SUPERVISOR_API_HOST env must be set")
if not SUPERVISOR_TOKEN:
    raise RuntimeError("SUPERVISOR_TOKEN env must be set")

client = SupervisorClient(SUPERVISOR_API_HOST, SUPERVISOR_TOKEN)

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)


async def get_info() -> RootInfo:
    """Get root info."""
    async with client:
        return await client.info()


info = loop.run_until_complete(get_info())
print(json.dumps(info.to_dict(), indent=4))  # noqa: T201
