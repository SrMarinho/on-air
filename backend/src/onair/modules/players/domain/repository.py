from abc import ABC, abstractmethod
from uuid import UUID

from onair.modules.players.domain.player import Player


class PlayerRepository(ABC):
    @abstractmethod
    async def add(self, player: Player) -> None: ...

    @abstractmethod
    async def get(self, player_id: UUID) -> Player | None: ...

    @abstractmethod
    async def get_by_username(self, username: str) -> Player | None: ...

    @abstractmethod
    async def exists(self, *, username: str, email: str) -> bool: ...

    @abstractmethod
    async def save(self, player: Player) -> None: ...
