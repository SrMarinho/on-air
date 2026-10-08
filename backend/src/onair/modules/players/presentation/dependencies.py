from typing import Annotated

from fastapi import Depends

from onair.core.dependencies import SessionDep
from onair.modules.players.domain.repository import PlayerRepository
from onair.modules.players.infrastructure.sql_repository import SqlPlayerRepository


def player_repository(session: SessionDep) -> PlayerRepository:
    return SqlPlayerRepository(session)


PlayerRepositoryDep = Annotated[PlayerRepository, Depends(player_repository)]
