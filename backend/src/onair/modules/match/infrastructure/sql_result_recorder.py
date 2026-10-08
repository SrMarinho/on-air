from uuid import UUID

from onair.core.database import Database
from onair.modules.match.application.ports import MatchResultRecorder
from onair.modules.players.infrastructure.sql_repository import SqlPlayerRepository


class SqlMatchResultRecorder(MatchResultRecorder):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def record(self, participants: list[UUID], winner_id: UUID | None) -> None:
        async for session in self._database.session():
            players = SqlPlayerRepository(session)
            for player_id in participants:
                player = await players.get(player_id)
                if player is not None:
                    player.record_match(won=player_id == winner_id)
                    await players.save(player)
