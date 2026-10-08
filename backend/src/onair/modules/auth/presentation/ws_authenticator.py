from onair.core.database import Database
from onair.core.errors import UnauthorizedError
from onair.core.security import TokenService
from onair.gateway.connection import Identity
from onair.gateway.ports import Authenticator
from onair.modules.players.infrastructure.sql_repository import SqlPlayerRepository


class JwtWsAuthenticator(Authenticator):
    def __init__(self, tokens: TokenService, database: Database) -> None:
        self._tokens = tokens
        self._database = database

    async def authenticate(self, token: str) -> Identity:
        player_id = self._tokens.verify(token, "access")
        async for session in self._database.session():
            player = await SqlPlayerRepository(session).get(player_id)
            if player is None:
                raise UnauthorizedError("Player no longer exists")
            return Identity(player_id=player.id, username=player.username)
        raise UnauthorizedError("Database unavailable")
