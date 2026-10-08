from abc import ABC, abstractmethod
from uuid import UUID

from onair.modules.rooms.domain.room import Room


class RoomRepository(ABC):
    @abstractmethod
    def add(self, room: Room) -> None: ...

    @abstractmethod
    def get(self, room_id: UUID) -> Room | None: ...

    @abstractmethod
    def remove(self, room_id: UUID) -> None: ...

    @abstractmethod
    def all(self) -> list[Room]: ...
