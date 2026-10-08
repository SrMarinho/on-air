from typing import Protocol
from uuid import UUID

from onair.modules.rooms.domain.room import Room


class MatchPort(Protocol):
    """What the rooms module needs from the match module (implemented there)."""

    async def start_match(self, room: Room) -> None: ...

    async def remove_player(self, room_id: UUID, player_id: UUID) -> None: ...
