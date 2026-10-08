from typing import Protocol
from uuid import UUID

from onair.protocol.base import Message


class Broadcaster(Protocol):
    """Outbound transport port. Implemented by the WebSocket gateway."""

    async def send_to_player(self, player_id: UUID, message: Message) -> None: ...

    async def send_to_room(self, room_id: UUID, message: Message) -> None: ...

    def bind_room(self, player_id: UUID, room_id: UUID | None) -> None: ...
