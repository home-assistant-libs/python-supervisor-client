"""Store client for supervisor."""

import re
from typing import Any

from .client import _SupervisorComponentClient
from .const import ResponseType
from .exceptions import (
    AddonNotSupportedArchitectureError,
    AddonNotSupportedError,
    AddonNotSupportedHomeAssistantVersionError,
    AddonNotSupportedMachineTypeError,
    SupervisorBadRequestError,
)
from .models.addons import (
    Repository,
    StoreAddon,
    StoreAddonComplete,
    StoreAddonInstall,
    StoreAddonsList,
    StoreAddonUpdate,
    StoreAddRepository,
    StoreInfo,
)

RE_ADDON_UNAVAILABLE_ARCHITECTURE = re.compile(
    r"^Add\-on (?P<addon>\w+) not supported on this platform, "
    r"supported architectures: (?P<architectures>.*)$"
)
RE_ADDON_UNAVAILABLE_MACHINE_TYPE = re.compile(
    r"^Add\-on (?P<addon>\w+) not supported on this machine, "
    r"supported machine types: (?P<machine_types>.*)$"
)
RE_ADDON_UNAVAILABLE_HOME_ASSISTANT = re.compile(
    r"^Add\-on (?P<addon>\w+) not supported on this system, "
    r"requires Home Assistant version (?P<version>\S+) or greater$"
)


class StoreClient(_SupervisorComponentClient):
    """Handles store access in Supervisor."""

    async def info(self) -> StoreInfo:
        """Get store info."""
        result = await self._client.get("store")
        return StoreInfo.from_dict(result.data)

    async def addons_list(self) -> list[StoreAddon]:
        """Get list of store addons."""
        result = await self._client.get("store/addons")
        return StoreAddonsList.from_dict(result.data).addons

    async def addon_info(self, addon: str) -> StoreAddonComplete:
        """Get store addon info."""
        result = await self._client.get(f"store/addons/{addon}")
        return StoreAddonComplete.from_dict(result.data)

    async def addon_changelog(self, addon: str) -> str:
        """Get addon changelog."""
        result = await self._client.get(
            f"store/addons/{addon}/changelog", response_type=ResponseType.TEXT
        )
        return result.data

    async def addon_documentation(self, addon: str) -> str:
        """Get addon documentation."""
        result = await self._client.get(
            f"store/addons/{addon}/documentation", response_type=ResponseType.TEXT
        )
        return result.data

    async def addon_availability(self, addon: str) -> None:
        """Determine if latest version of addon can be installed on this system.

        No return means it can be. If not, raises one of the following errors:
        - AddonUnavailableHomeAssistantVersionError
        - AddonUnavailableArchitectureError
        - AddonUnavailableMachineTypeError

        If Supervisor adds a new reason an add-on can be restricted from being
        installed on some systems in the future, older versions of this client
        will raise the generic AddonNotSupportedError for that reason.
        """
        try:
            await self._client.get(
                f"store/addons/{addon}/availability", response_type=ResponseType.NONE
            )
        except SupervisorBadRequestError as err:
            if match := RE_ADDON_UNAVAILABLE_ARCHITECTURE.match(str(err)):
                raise AddonNotSupportedArchitectureError(
                    match.group("addon"), match.group("architectures"), err.job_id
                ) from None
            if match := RE_ADDON_UNAVAILABLE_HOME_ASSISTANT.match(str(err)):
                raise AddonNotSupportedHomeAssistantVersionError(
                    match.group("addon"), match.group("version"), err.job_id
                ) from None
            if match := RE_ADDON_UNAVAILABLE_MACHINE_TYPE.match(str(err)):
                raise AddonNotSupportedMachineTypeError(
                    match.group("addon"), match.group("machine_types"), err.job_id
                ) from None
            raise AddonNotSupportedError(str(err), err.job_id) from None

    async def install_addon(
        self, addon: str, options: StoreAddonInstall | None = None
    ) -> None:
        """Install an addon."""
        # Must disable timeout if API call waits for install to complete
        kwargs: dict[str, Any] = {}
        if not options or not options.background:
            kwargs["timeout"] = None

        await self._client.post(
            f"store/addons/{addon}/install",
            json=options.to_dict() if options else None,
            **kwargs,
        )

    async def update_addon(
        self, addon: str, options: StoreAddonUpdate | None = None
    ) -> None:
        """Update an addon to latest version."""
        # Must disable timeout if API call waits for update to complete
        kwargs: dict[str, Any] = {}
        if not options or not options.background:
            kwargs["timeout"] = None

        await self._client.post(
            f"store/addons/{addon}/update",
            json=options.to_dict() if options else None,
            **kwargs,
        )

    async def reload(self) -> None:
        """Reload the store."""
        await self._client.post("store/reload")

    async def repositories_list(self) -> list[Repository]:
        """Get list of repositories."""
        result = await self._client.get("store/repositories")
        # This API is inconsistent with Supervisor's API model, data should be
        # a dictionary with a "repositories" field. It would break the CLI like
        # this but the CLI doesn't use it so it went unnoticed.
        return [Repository.from_dict(repo) for repo in result.data]

    async def repository_info(self, repository: str) -> Repository:
        """Get repository info."""
        result = await self._client.get(f"store/repositories/{repository}")
        return Repository.from_dict(result.data)

    async def add_repository(self, options: StoreAddRepository) -> None:
        """Add a repository to the store."""
        await self._client.post("store/repositories", json=options.to_dict())

    async def remove_repository(self, repository: str) -> None:
        """Remove a repository from the store."""
        await self._client.delete(f"store/repositories/{repository}")

    # Omitted for now - Icon/Logo endpoints
