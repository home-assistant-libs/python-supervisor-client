"""Utilities for interacting with aiohttp."""

from collections.abc import AsyncGenerator
from typing import Self

from aiohttp import ClientResponse, StreamReader


class ChunkAsyncStreamIterator:
    """Async iterator for chunked streams.

    Based on aiohttp.streams.ChunkTupleAsyncStreamIterator, but yields
    bytes instead of tuple[bytes, bool].
    Borrowed from home-assistant/core.
    """

    __slots__ = ("_stream",)

    def __init__(self, stream: StreamReader) -> None:
        """Initialize."""
        self._stream = stream

    def __aiter__(self) -> Self:
        """Iterate."""
        return self

    async def __anext__(self) -> bytes:
        """Yield next chunk."""
        rv = await self._stream.readchunk()
        if rv == (b"", False):
            raise StopAsyncIteration
        return rv[0]


async def iter_response_chunks(response: ClientResponse) -> AsyncGenerator[bytes]:
    """Yield chunks of the response body and close the response when done.

    A partially read response holds its connection until it is closed, and is
    kept alive by the connector, so it is never garbage collected. Closing in
    finally returns the connection when the caller stops iterating early, calls
    aclose() or drops the generator. A fully read response has already released
    its connection, so close() is a no-op then.
    """
    try:
        async for chunk in ChunkAsyncStreamIterator(response.content):
            yield chunk
    finally:
        response.close()
