from __future__ import annotations

import asyncio
from typing import Optional, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from .socket import CanSocket

CAN_READER_LIMIT = 1024 * 1024


class CanNode:
    def __init__(self, node_id: int, cansocket: CanSocket) -> None:
        self.node_id = node_id
        self._reader = asyncio.StreamReader(CAN_READER_LIMIT)
        self._cansocket = cansocket

    async def read(
        self, n: int = -1, timeout: Optional[float] = 2
    ) -> bytes:
        return await asyncio.wait_for(self._reader.read(n), timeout)

    async def readexactly(
        self, n: int, timeout: Optional[float] = 2
    ) -> bytes:
        return await asyncio.wait_for(self._reader.readexactly(n), timeout)

    async def readuntil(
        self, sep: bytes = b"\x03", timeout: Optional[float] = 2
    ) -> bytes:
        return await asyncio.wait_for(self._reader.readuntil(sep), timeout)

    def write(self, payload: Union[bytes, bytearray]) -> None:
        if isinstance(payload, bytearray):
            payload = bytes(payload)
        self._cansocket.send(self.node_id, payload)

    async def write_with_response(
        self,
        payload: Union[bytearray, bytes],
        resp_length: int,
        timeout: Optional[float] = 2.
    ) -> bytes:
        self.write(payload)
        return await self.readexactly(resp_length, timeout)

    def feed_data(self, data: bytes) -> None:
        self._reader.feed_data(data)

    def close(self) -> None:
        self._reader.feed_eof()
