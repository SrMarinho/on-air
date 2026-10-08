from uuid import UUID

from onair.modules.rooms.domain.repository import RoomRepository
from onair.modules.rooms.domain.room import Room


class InMemoryRoomRepository(RoomRepository):
    """Rooms are ephemeral and bound to this process' live match loops."""

    def __init__(self) -> None:
        self._rooms: dict[UUID, Room] = {}

    def add(self, room: Room) -> None:
        self._rooms[room.id] = room

    def get(self, room_id: UUID) -> Room | None:
        return self._rooms.get(room_id)

    def remove(self, room_id: UUID) -> None:
        self._rooms.pop(room_id, None)

    def all(self) -> list[Room]:
        return list(self._rooms.values())
