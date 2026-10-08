import asyncio
import contextlib
import logging
from dataclasses import dataclass
from uuid import UUID

from fastapi import WebSocket

from onair.protocol.base import Message

logger = logging.getLogger(__name__)

OUTBOX_SIZE = 256
REPLACED_BY_NEW_SESSION = 4000


@dataclass(frozen=True, slots=True)
class Identity:
    player_id: UUID
    username: str


class ClientConnection:
    """One authenticated socket. Outbound messages go through a bounded queue drained by a
    writer task, so a slow client never stalls the match loop."""

    def __init__(self, websocket: WebSocket, identity: Identity) -> None:
        self._websocket = websocket
        self.identity = identity
        self._outbox: asyncio.Queue[str] = asyncio.Queue(maxsize=OUTBOX_SIZE)
        self._writer: asyncio.Task[None] | None = None

    @property
    def player_id(self) -> UUID:
        return self.identity.player_id

    def start(self) -> None:
        self._writer = asyncio.create_task(self._drain())

    async def close(self, *, close_socket: bool = False) -> None:
        if self._writer is not None:
            self._writer.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._writer
        if close_socket:
            with contextlib.suppress(Exception):
                await self._websocket.close(code=REPLACED_BY_NEW_SESSION)

    def send(self, message: Message) -> None:
        try:
            self._outbox.put_nowait(message.model_dump_json())
        except asyncio.QueueFull:
            logger.warning("Dropping message for slow client %s", self.player_id)

    async def _drain(self) -> None:
        while True:
            payload = await self._outbox.get()
            try:
                await self._websocket.send_text(payload)
            except Exception:  # socket gone; receive loop will clean up
                return
