"""Utilities for interacting with aiohttp."""

import asyncio
import contextlib
from typing import Self

from aiohttp import ClientResponse


class ResponseChunkIterator:
    """Async iterator over the chunks of a response body.

    Yields bytes like aiohttp.streams.ChunkTupleAsyncStreamIterator, but owns the
    response and closes it when done.

    A partially read response holds its connection until it is closed, and is
    kept alive by the connector, so it is never garbage collected. The response
    is closed when the body is fully read, when reading raises, when close() or
    aclose() is called, or when the iterator is garbage collected, whether or
    not iteration has started. Garbage collection may happen in any thread, the
    response is then closed on the event loop. close() and aclose() must be
    called from the event loop thread, and may be called while a read is in
    flight in another task, the pending read then raises ClientConnectionError.

    Once the body is fully read or close() is called, the iterator is exhausted
    and further iteration stops immediately. If reading raised, further reads
    raise as well, so a truncated body is not mistaken for a complete one. A
    fully read response has already released its connection, so closing it is
    a no-op.
    """

    __slots__ = ("_closed", "_exhausted", "_loop", "_response")

    def __init__(self, response: ClientResponse) -> None:
        """Initialize."""
        self._response = response
        self._loop = asyncio.get_running_loop()
        self._closed = False
        self._exhausted = False

    def __aiter__(self) -> Self:
        """Iterate."""
        return self

    async def __anext__(self) -> bytes:
        """Yield next chunk."""
        # A closed response's reader raises, so don't read from it again
        if self._exhausted:
            raise StopAsyncIteration
        try:
            rv = await self._response.content.readchunk()
        except BaseException:
            self._close_response()
            raise
        if rv == (b"", False):
            self.close()
            raise StopAsyncIteration
        return rv[0]

    def _close_response(self) -> None:
        """Close the response, which makes further reads raise."""
        self._closed = True
        self._response.close()

    def close(self) -> None:
        """Close the response and release its connection."""
        self._exhausted = True
        self._close_response()

    async def aclose(self) -> None:
        """Close the response and release its connection."""
        self.close()

    def __del__(self) -> None:
        """Close the response when the iterator is garbage collected."""
        if self._closed:
            return
        self._closed = True
        loop = self._loop
        if loop.is_closed():
            return
        try:
            running_loop = asyncio.get_running_loop()
        except RuntimeError:
            running_loop = None
        if running_loop is loop:
            self._response.close()
            return
        # The response may only be closed from the event loop thread. If the loop
        # was closed concurrently, skip closing like aiohttp does.
        with contextlib.suppress(RuntimeError):
            loop.call_soon_threadsafe(self._response.close)
