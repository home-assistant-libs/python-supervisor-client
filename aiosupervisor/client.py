"""Internal client for making requests and managing session with Supervisor."""

from collections.abc import Awaitable
from dataclasses import dataclass, field
from importlib import metadata
from typing import Any

from aiohttp import (
    ClientError,
    ClientResponse,
    ClientResponseError,
    ClientSession,
    ClientTimeout,
)
from aiohttp.hdrs import METH_DELETE, METH_GET, METH_POST, METH_PUT
from yarl import URL

from .const import ResponseType
from .exceptions import (
    SupervisorAuthenticationError,
    SupervisorBadRequestError,
    SupervisorConnectionError,
    SupervisorError,
    SupervisorForbiddenError,
    SupervisorNotFoundError,
    SupervisorResponseError,
    SupervisorServiceUnavailableError,
    SupervisorTimeoutError,
)
from .models.base import Response, ResultType

VERSION = metadata.version(__package__)


def is_json(response: ClientResponse, raise_on_fail: bool = False) -> bool:
    """Check if response is json according to Content-Type."""
    content_type = response.headers.get("Content-Type", "")
    if "application/json" not in content_type:
        if raise_on_fail:
            raise SupervisorError(
                f"Unexpected response received from supervisor when expecting JSON. Status: {response.status}, content type: {content_type}"
            )
        return False
    return True


@dataclass(slots=True)
class _SupervisorClient:
    """Main class for handling connections with Supervisor."""

    api_host: str
    token: str
    request_timeout: int
    session: ClientSession | None = None
    _close_session: bool = field(default=False, init=False)

    @property
    def timeout(self) -> ClientTimeout:
        """Timeout for requests."""
        return ClientTimeout(total=self.request_timeout)

    async def _request(
        self,
        method: str,
        uri: str,
        *,
        params: dict[str, str] | None,
        response_type: ResponseType,
        json: dict[str, Any] | None = None,
        data: Any = None,
    ) -> Response:
        """Handle a request to Supervisor."""
        url = URL(self.api_host).joinpath(uri)

        match response_type:
            case ResponseType.TEXT:
                accept = "text/plain, */*"
            case _:
                accept = "application/json, text/plain, */*"

        headers = {
            "User-Agent": f"AioSupervisor/{VERSION}",
            "Accept": accept,
            "Authorization": f"Bearer {self.token}",
        }

        if self.session is None:
            self.session = ClientSession()
            self._close_session = True

        try:
            async with self.session.request(
                method,
                url,
                timeout=self.timeout,
                headers=headers,
                params=params,
                json=json,
                data=data,
            ) as response:
                if response.status >= 400:
                    exc_type: type[SupervisorError] = SupervisorError
                    match response.status:
                        case 400:
                            exc_type = SupervisorBadRequestError
                        case 401:
                            exc_type = SupervisorAuthenticationError
                        case 403:
                            exc_type = SupervisorForbiddenError
                        case 404:
                            exc_type = SupervisorNotFoundError
                        case 503:
                            exc_type = SupervisorServiceUnavailableError

                    if is_json(response):
                        result = Response.from_json(await response.text())
                        raise exc_type(result.message, result.job_id)
                    raise exc_type()

                match response_type:
                    case ResponseType.JSON:
                        is_json(response, raise_on_fail=True)
                        return Response.from_json(await response.text())
                    case ResponseType.TEXT:
                        return Response(ResultType.OK, await response.text())
                    case _:
                        return Response(ResultType.OK)

        except (UnicodeDecodeError, ClientResponseError) as err:
            raise SupervisorResponseError(
                "Unusable response received from Supervisor, check logs"
            ) from err
        except TimeoutError as err:
            raise SupervisorTimeoutError("Timeout connecting to Supervisor") from err
        except ClientError as err:
            raise SupervisorConnectionError(
                "Error occurred connecting to supervisor"
            ) from err

    def get(
        self,
        uri: str,
        *,
        params: dict[str, str] | None = None,
        response_type: ResponseType = ResponseType.JSON,
    ) -> Awaitable[Response]:
        """Handle a GET request to Supervisor."""
        return self._request(METH_GET, uri, params=params, response_type=response_type)

    def post(
        self,
        uri: str,
        *,
        params: dict[str, str] | None = None,
        response_type: ResponseType = ResponseType.NONE,
        json: dict[str, Any] | None = None,
        data: Any = None,
    ) -> Awaitable[Response]:
        """Handle a POST request to Supervisor."""
        return self._request(
            METH_POST,
            uri,
            params=params,
            response_type=response_type,
            json=json,
            data=data,
        )

    def put(
        self,
        uri: str,
        *,
        params: dict[str, str] | None = None,
        json: dict[str, Any] | None = None,
    ) -> Awaitable[Response]:
        """Handle a PUT request to Supervisor."""
        return self._request(
            METH_PUT, uri, params=params, response_type=ResponseType.NONE, json=json
        )

    def delete(
        self,
        uri: str,
        *,
        params: dict[str, str] | None = None,
    ) -> Awaitable[Response]:
        """Handle a DELETE request to Supervisor."""
        return self._request(
            METH_DELETE, uri, params=params, response_type=ResponseType.NONE
        )

    async def close(self) -> None:
        """Close open client session."""
        if self.session and self._close_session:
            await self.session.close()


class _SupervisorComponentClient:
    """Common ancestor for all component clients of supervisor."""

    def __init__(self, client: _SupervisorClient) -> None:
        """Initialize sub module with client for API calls."""
        self._client = client
