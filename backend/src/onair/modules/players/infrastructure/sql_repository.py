from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from onair.modules.players.domain.player import Player
from onair.modules.players.domain.repository import PlayerRepository
from onair.modules.players.infrastructure.models import PlayerModel


class SqlPlayerRepository(PlayerRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, player: Player) -> None:
        self._session.add(self._to_model(player))
        await self._session.flush()

    async def get(self, player_id: UUID) -> Player | None:
        model = await self._session.get(PlayerModel, player_id)
        return self._to_domain(model) if model else None

    async def get_by_username(self, username: str) -> Player | None:
        result = await self._session.execute(
            select(PlayerModel).where(PlayerModel.username == username)
        )
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def exists(self, *, username: str, email: str) -> bool:
        result = await self._session.execute(
            select(PlayerModel.id).where(
                or_(PlayerModel.username == username, PlayerModel.email == email)
            )
        )
        return result.first() is not None

    async def save(self, player: Player) -> None:
        await self._session.merge(self._to_model(player))
        await self._session.flush()

    @staticmethod
    def _to_model(player: Player) -> PlayerModel:
        return PlayerModel(
            id=player.id,
            username=player.username,
            email=player.email,
            password_hash=player.password_hash,
            matches_played=player.matches_played,
            matches_won=player.matches_won,
            created_at=player.created_at,
        )

    @staticmethod
    def _to_domain(model: PlayerModel) -> Player:
        return Player(
            id=model.id,
            username=model.username,
            email=model.email,
            password_hash=model.password_hash,
            matches_played=model.matches_played,
            matches_won=model.matches_won,
            created_at=model.created_at,
        )
