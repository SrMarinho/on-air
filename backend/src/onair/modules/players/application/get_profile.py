from uuid import UUID

from onair.core.errors import NotFoundError
from onair.modules.players.domain.player import Player
from onair.modules.players.domain.repository import PlayerRepository


class GetProfile:
    def __init__(self, players: PlayerRepository) -> None:
        self._players = players

    async def execute(self, player_id: UUID) -> Player:
        player = await self._players.get(player_id)
        if player is None:
            raise NotFoundError("Player not found")
        return player
