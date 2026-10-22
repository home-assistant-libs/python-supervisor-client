"""Utilities for interacting with aiohttp."""

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
    not iteration has started. close() may be called while a read is in flight
    in another task, the pending read then raises ClientConnectionError. Once
    closed, the iterator is exhausted and further iteration stops immediately.
    A fully read response has already released its connection, so closing it is
    a no-op.
    """

    __slots__ = ("_closed", "_response")

    def __init__(self, response: ClientResponse) -> None:
        """Initialize."""
        self._response = response
        self._closed = False

    def __aiter__(self) -> Self:
        """Iterate."""
        return self

    async def __anext__(self) -> bytes:
        """Yield next chunk."""
        # A closed response's reader raises, so don't read from it again
        if self._closed:
            raise StopAsyncIteration
        try:
            rv = await self._response.content.readchunk()
        except BaseException:
            self.close()
            raise
        if rv == (b"", False):
            self.close()
            raise StopAsyncIteration
        return rv[0]

    def close(self) -> None:
        """Close the response and release its connection."""
        self._closed = True
        self._response.close()

    async def aclose(self) -> None:
        """Close the response and release its connection."""
        self.close()

    def __del__(self) -> None:
        """Close the response when the iterator is garbage collected."""
        self.close()
