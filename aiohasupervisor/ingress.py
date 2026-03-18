"""Ingress client for supervisor."""

from .client import _SupervisorComponentClient
from .const import ResponseType
from .models.ingress import CreateSessionOptions, IngressPanel, IngressPanels, Session


class IngressClient(_SupervisorComponentClient):
    """Handles ingress access in Supervisor.

    This includes only the APIs with fixed paths and models from Supervisor's Ingress
    API. The wildcard proxy endpoints that allow the UI to talk to addons through Core
    and Supervisor are intentionally omitted as they can't be modeled.
    """

    async def panels(self) -> dict[str, IngressPanel]:
        """Get ingress panels, returns a map of addon slug to panel info."""
        result = await self._client.get("ingress/panels")
        return IngressPanels.from_dict(result.data).panels

    async def create_session(self, options: CreateSessionOptions | None = None) -> str:
        """Create a new ingress session."""
        result = await self._client.post(
            "ingress/session",
            json=options.to_dict() if options else None,
            response_type=ResponseType.JSON,
        )
        return Session.from_dict(result.data).session

    async def validate_session(self, session: str) -> None:
        """Validate an existing ingress session."""
        body = Session(session=session).to_dict()
        await self._client.post("ingress/validate_session", json=body)
